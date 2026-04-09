"""
TRIBE V2 + TCN-TRIBE: Train a TCN on TRIBE simulator data, then evaluate.

Pipeline:
    1. Generate PAC sequences from TRIBE V2 simulator (realistic noise mode)
    2. Build causal feature sequences (PAC history + stim context)
    3. Train a lightweight TCN ("TCN-TRIBE") to predict future PAC
    4. Run alignment evaluation: Fixed / Reactive / TCN-TRIBE / Oracle
    5. Compare across disease severities

This addresses the domain mismatch issue: the original TCN was trained on
real EEG data and underperforms on TRIBE simulator dynamics. TCN-TRIBE is
trained on the simulator's OWN dynamics, giving it a fair shot.

Usage:
    PYTHONPATH=src python run_tribe_tcn_validation.py
"""

from __future__ import annotations

import json
import sys
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from tribe_v2.enhanced_simulator import create_simulator


# ─── 1. Data Generation ───────────────────────────────────────────────


def generate_pac_sequences(
    n_subjects: int,
    duration_sec: int,
    severity: str,
    base_seed: int,
) -> list[dict]:
    """Generate PAC time series from TRIBE V2 simulator with realistic noise.

    Uses random action patterns (not fixed schedule) to expose the model
    to diverse stimulation regimes during training.
    """
    sequences = []
    for subj in range(n_subjects):
        seed = base_seed + subj * 137
        sim = create_simulator(
            disease_severity=severity,
            use_tribe_v2=False,
            subject_seed=seed,
            realistic_noise=True,
        )
        rng = np.random.default_rng(seed + 999)

        pac_values = []
        actions = []

        # Random action pattern: blocks of 5-30 steps
        t = 0
        current_action = 0
        block_remaining = 0

        for step in range(duration_sec):
            if block_remaining <= 0:
                current_action = int(rng.random() > 0.4)  # ~60% stim
                block_remaining = rng.integers(5, 30)
            block_remaining -= 1

            pac = sim.step(current_action)
            pac_values.append(pac)
            actions.append(current_action)

        sequences.append({
            "pac": np.array(pac_values),
            "actions": np.array(actions),
            "seed": seed,
        })

    return sequences


# ─── 2. Feature Engineering ───────────────────────────────────────────


LOOKBACK = 20
HORIZON = 3
N_FEATURES = 12  # PAC-derived (7) + stim context (5)


def build_features_from_sequence(
    pac: np.ndarray,
    actions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Build causal feature sequences and future PAC targets.

    Features per step (12 total):
        - pac_current
        - pac_ma2, pac_ma4, pac_ma8 (causal moving averages)
        - pac_diff1, pac_diff2, pac_diff4 (finite differences)
        - stim_state (current)
        - time_since_switch (normalized)
        - stim_frac_20s (recent stim fraction)
        - cycle_phase_sin, cycle_phase_cos
    """
    n = len(pac)
    if n < LOOKBACK + HORIZON + 1:
        return np.empty((0, LOOKBACK, N_FEATURES)), np.empty((0,))

    features_all = np.zeros((n, N_FEATURES), dtype=np.float32)

    for t in range(n):
        # PAC features (causal)
        features_all[t, 0] = pac[t]
        features_all[t, 1] = np.mean(pac[max(0, t - 1):t + 1])
        features_all[t, 2] = np.mean(pac[max(0, t - 3):t + 1])
        features_all[t, 3] = np.mean(pac[max(0, t - 7):t + 1])
        features_all[t, 4] = pac[t] - pac[t - 1] if t > 0 else 0.0
        features_all[t, 5] = pac[t] - pac[t - 2] if t > 1 else 0.0
        features_all[t, 6] = pac[t] - pac[t - 4] if t > 3 else 0.0

        # Stim context
        features_all[t, 7] = float(actions[t])

        # Time since switch
        t_switch = 0
        for k in range(t, 0, -1):
            if actions[k] != actions[k - 1]:
                break
            t_switch += 1
        features_all[t, 8] = min(t_switch / 60.0, 1.0)

        # Recent stim fraction
        window_start = max(0, t - 19)
        features_all[t, 9] = np.mean(actions[window_start:t + 1])

        # Cycle phase
        phase = 2.0 * np.pi * (t % 60) / 60.0
        features_all[t, 10] = np.sin(phase)
        features_all[t, 11] = np.cos(phase)

    # Build sequences: X[t-LOOKBACK:t] → Y[t+HORIZON]
    X_list = []
    Y_list = []
    for t in range(LOOKBACK, n - HORIZON):
        X_list.append(features_all[t - LOOKBACK:t])
        Y_list.append(pac[t + HORIZON])

    return np.array(X_list, dtype=np.float32), np.array(Y_list, dtype=np.float32)


# ─── 3. TCN-TRIBE Model ──────────────────────────────────────────────


class CausalConv1dBlock(nn.Module):
    """Single causal dilated conv block with residual."""

    def __init__(self, channels: int, kernel_size: int, dilation: int):
        super().__init__()
        padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            channels, channels, kernel_size,
            dilation=dilation, padding=padding,
        )
        self.norm = nn.GroupNorm(4, channels)
        self.act = nn.SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Causal: trim future samples
        out = self.conv(x)
        out = out[:, :, :x.size(2)]
        return self.act(self.norm(out)) + x


class TCNTribe(nn.Module):
    """Lightweight causal TCN for TRIBE simulator PAC forecasting."""

    def __init__(
        self,
        n_features: int = N_FEATURES,
        hidden: int = 32,
        kernel_size: int = 3,
        dilations: tuple[int, ...] = (1, 2, 4, 8),
    ):
        super().__init__()
        self.in_proj = nn.Sequential(
            nn.Linear(n_features, hidden),
            nn.LayerNorm(hidden),
            nn.SiLU(),
        )
        self.blocks = nn.ModuleList([
            CausalConv1dBlock(hidden, kernel_size, d) for d in dilations
        ])
        self.head = nn.Sequential(
            nn.Linear(hidden, hidden),
            nn.SiLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F) → project to hidden
        h = self.in_proj(x)        # (B, T, H)
        h = h.transpose(1, 2)      # (B, H, T) for conv1d
        for block in self.blocks:
            h = block(h)
        # Take last timestep
        h = h[:, :, -1]            # (B, H)
        return self.head(h).squeeze(-1)  # (B,)


# ─── 4. Training ─────────────────────────────────────────────────────


def train_tcn_tribe(
    train_X: np.ndarray,
    train_Y: np.ndarray,
    val_X: np.ndarray,
    val_Y: np.ndarray,
    epochs: int = 80,
    batch_size: int = 128,
    lr: float = 1e-3,
    device: str = "cpu",
) -> TCNTribe:
    """Train TCN-TRIBE with early stopping."""

    # Normalize targets
    y_mean, y_std = float(np.mean(train_Y)), float(np.std(train_Y)) + 1e-8
    train_Y_z = (train_Y - y_mean) / y_std
    val_Y_z = (val_Y - y_mean) / y_std

    # Normalize features
    feat_mean = np.mean(train_X.reshape(-1, N_FEATURES), axis=0)
    feat_std = np.std(train_X.reshape(-1, N_FEATURES), axis=0) + 1e-8
    train_X_n = (train_X - feat_mean) / feat_std
    val_X_n = (val_X - feat_mean) / feat_std

    train_ds = TensorDataset(
        torch.tensor(train_X_n, dtype=torch.float32),
        torch.tensor(train_Y_z, dtype=torch.float32),
    )
    val_ds = TensorDataset(
        torch.tensor(val_X_n, dtype=torch.float32),
        torch.tensor(val_Y_z, dtype=torch.float32),
    )
    train_dl = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_dl = DataLoader(val_ds, batch_size=batch_size)

    model = TCNTribe().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        opt, patience=10, factor=0.5,
    )
    loss_fn = nn.HuberLoss()

    best_val_loss = float("inf")
    best_state = None
    patience_counter = 0
    patience_limit = 20

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        n_batches = 0
        for xb, yb in train_dl:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            opt.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            train_loss += loss.item()
            n_batches += 1
        train_loss /= max(n_batches, 1)

        model.eval()
        val_loss = 0.0
        n_val = 0
        with torch.no_grad():
            for xb, yb in val_dl:
                xb, yb = xb.to(device), yb.to(device)
                pred = model(xb)
                val_loss += loss_fn(pred, yb).item()
                n_val += 1
        val_loss /= max(n_val, 1)
        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1

        if epoch % 10 == 0 or epoch == epochs - 1:
            print(f"    Epoch {epoch:3d}: train={train_loss:.5f}  val={val_loss:.5f}  best={best_val_loss:.5f}")

        if patience_counter >= patience_limit:
            print(f"    Early stopping at epoch {epoch}")
            break

    model.load_state_dict(best_state)

    # Attach normalization stats for inference
    model._y_mean = y_mean
    model._y_std = y_std
    model._feat_mean = feat_mean
    model._feat_std = feat_std

    # Compute test R²
    model.eval()
    with torch.no_grad():
        val_pred = []
        val_true = []
        for xb, yb in val_dl:
            pred = model(xb.to(device)).cpu().numpy()
            val_pred.append(pred)
            val_true.append(yb.numpy())
        val_pred = np.concatenate(val_pred) * y_std + y_mean
        val_true = np.concatenate(val_true) * y_std + y_mean
        ss_res = np.sum((val_true - val_pred) ** 2)
        ss_tot = np.sum((val_true - np.mean(val_true)) ** 2)
        r2 = 1.0 - ss_res / (ss_tot + 1e-10)
        print(f"    Validation R² = {r2:.4f}")

    return model


# ─── 5. TCN-TRIBE Controller ─────────────────────────────────────────


class TCNTribeController:
    """Closed-loop controller using TCN-TRIBE for proactive decisions."""

    name = "TCN-TRIBE Predictive"

    def __init__(self, model: TCNTribe, z_thresh: float = 0.5, hold: int = 3):
        self.model = model.cpu()  # Always run inference on CPU
        self.z_thresh = z_thresh
        self.hold = hold
        self.buf: deque = deque(maxlen=30)
        self.action_buf: deque = deque(maxlen=30)
        self.seq_buf: deque = deque(maxlen=LOOKBACK)
        self.state = 0
        self.t_in_state = 0
        self.t = 0

    def reset(self):
        self.buf.clear()
        self.action_buf.clear()
        self.seq_buf.clear()
        self.state = 0
        self.t_in_state = 0
        self.t = 0

    def _build_features(self, pac: float) -> np.ndarray:
        """Build single-step feature vector (12 dims)."""
        feat = np.zeros(N_FEATURES, dtype=np.float32)
        pac_list = list(self.buf) + [pac]

        feat[0] = pac
        feat[1] = np.mean(pac_list[-2:])
        feat[2] = np.mean(pac_list[-4:])
        feat[3] = np.mean(pac_list[-8:])
        feat[4] = pac - pac_list[-2] if len(pac_list) > 1 else 0.0
        feat[5] = pac - pac_list[-3] if len(pac_list) > 2 else 0.0
        feat[6] = pac - pac_list[-5] if len(pac_list) > 4 else 0.0

        feat[7] = float(self.state)

        # Time since switch
        t_switch = 0
        acts = list(self.action_buf)
        for k in range(len(acts) - 1, 0, -1):
            if acts[k] != acts[k - 1]:
                break
            t_switch += 1
        feat[8] = min(t_switch / 60.0, 1.0)

        # Recent stim fraction
        recent = list(self.action_buf)[-20:]
        feat[9] = np.mean(recent) if recent else 0.5

        # Cycle phase
        phase = 2.0 * np.pi * (self.t % 60) / 60.0
        feat[10] = np.sin(phase)
        feat[11] = np.cos(phase)

        return feat

    def step(self, pac: float, **kw) -> int:
        feat = self._build_features(pac)
        self.seq_buf.append(feat)
        self.buf.append(pac)
        self.action_buf.append(self.state)
        self.t += 1

        # Need full lookback window
        if len(self.seq_buf) < LOOKBACK or len(self.buf) < 10:
            return 0

        # TCN prediction
        seq = np.array(list(self.seq_buf), dtype=np.float32)
        seq_n = (seq - self.model._feat_mean) / self.model._feat_std
        x = torch.tensor(seq_n, dtype=torch.float32).unsqueeze(0)

        self.model.eval()
        with torch.no_grad():
            pred_z = self.model(x).item()
        pred_pac = pred_z * self.model._y_std + self.model._y_mean

        # Z-score of current PAC
        mu = np.mean(list(self.buf))
        sig = np.std(list(self.buf)) + 1e-12
        z_current = (pac - mu) / sig

        # Decision: predicted PAC change drives proactive control
        delta_pac = pred_pac - pac

        desired = None
        if delta_pac < -0.015:       # PAC predicted to drop → stimulate now
            desired = 1
        elif delta_pac > 0.015:      # PAC predicted to rise → rest
            desired = 0
        elif z_current < -self.z_thresh:
            desired = 1
        elif z_current > self.z_thresh:
            desired = 0

        if desired is None:
            desired = self.state

        if desired != self.state and self.t_in_state >= self.hold:
            self.state = desired
            self.t_in_state = 0
        else:
            self.t_in_state += 1

        return self.state


# ─── 6. Evaluation ───────────────────────────────────────────────────


class FixedScheduleCtrl:
    name = "Fixed Schedule"
    def __init__(self): self.t = 0
    def reset(self): self.t = 0
    def step(self, pac, **kw):
        self.t += 1
        return 1 if (self.t % 60) < 40 else 0


class ReactiveCtrl:
    name = "Reactive Threshold"
    def __init__(self, w=30, z_thresh=0.5):
        self.w = w; self.z = z_thresh; self.buf = []
    def reset(self): self.buf = []
    def step(self, pac, **kw):
        self.buf.append(pac)
        if len(self.buf) > self.w: self.buf.pop(0)
        if len(self.buf) < 10: return 0
        mu, sig = np.mean(self.buf), np.std(self.buf) + 1e-12
        return 1 if (pac - mu) / sig < -self.z else 0


def evaluate_alignment(pac: np.ndarray, decisions: np.ndarray) -> dict:
    """Same alignment metrics as the real-data validation."""
    median_pac = np.median(pac)
    low_mask = pac < median_pac
    high_mask = pac >= median_pac
    stim_mask = decisions == 1
    rest_mask = decisions == 0

    low_stim = float(np.mean(stim_mask[low_mask])) if low_mask.sum() > 0 else 0.0
    high_rest = float(np.mean(rest_mask[high_mask])) if high_mask.sum() > 0 else 0.0
    alignment = (low_stim + high_rest) / 2

    mean_stim = float(np.mean(pac[stim_mask])) if stim_mask.sum() > 0 else 0
    mean_rest = float(np.mean(pac[rest_mask])) if rest_mask.sum() > 0 else 0
    pac_gap = mean_rest - mean_stim

    return {
        "alignment": round(alignment, 6),
        "low_pac_stim_rate": round(low_stim, 6),
        "high_pac_rest_rate": round(high_rest, 6),
        "stim_pct": round(100.0 * float(np.mean(stim_mask)), 2),
        "pac_gap": round(pac_gap, 6),
    }


def hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = len(a), len(b)
    pooled = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    if pooled < 1e-12:
        return 0.0
    d = (np.mean(a) - np.mean(b)) / pooled
    return float(d * (1 - 3 / (4 * (na + nb) - 9)))


def run_trial(ctrl, severity: str, duration_sec: int, seed: int) -> dict:
    """Run one trial with a controller on the realistic-noise simulator."""
    sim = create_simulator(
        disease_severity=severity, use_tribe_v2=False,
        subject_seed=seed, realistic_noise=True,
    )
    ctrl.reset()
    pac_values, decisions = [], []
    for _ in range(duration_sec):
        pac = sim.pac
        action = ctrl.step(pac)
        sim.step(action)
        pac_values.append(pac)
        decisions.append(action)
    return evaluate_alignment(np.array(pac_values), np.array(decisions))


def run_oracle_trial(severity: str, duration_sec: int, seed: int) -> dict:
    """Oracle: two-pass — collect PAC, then decide with perfect info."""
    sim = create_simulator(
        disease_severity=severity, use_tribe_v2=False,
        subject_seed=seed, realistic_noise=True,
    )
    pac_values = []
    for step in range(duration_sec):
        pac_values.append(sim.pac)
        sim.step(1 if (step % 60) < 40 else 0)
    pac_arr = np.array(pac_values)
    median_pac = np.median(pac_arr)
    dec_arr = np.array([1 if p < median_pac else 0 for p in pac_arr])
    return evaluate_alignment(pac_arr, dec_arr)


# ─── 7. Main ─────────────────────────────────────────────────────────


def main():
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Device: {device}")

    # ── Step 1: Generate training data ──
    print("\n" + "=" * 70)
    print("Step 1: Generating PAC sequences from TRIBE V2 simulator (realistic noise)")
    print("=" * 70)

    # Train on multiple severities for generalization
    train_seqs = []
    for sev in ["healthy", "mild", "moderate"]:
        train_seqs.extend(generate_pac_sequences(
            n_subjects=20, duration_sec=600, severity=sev, base_seed=1000,
        ))
    val_seqs = generate_pac_sequences(
        n_subjects=10, duration_sec=600, severity="mild", base_seed=5000,
    )
    print(f"  Generated {len(train_seqs)} training + {len(val_seqs)} validation sequences")

    # ── Step 2: Build features ──
    print("\nStep 2: Building causal feature sequences")

    train_X_list, train_Y_list = [], []
    for seq in train_seqs:
        X, Y = build_features_from_sequence(seq["pac"], seq["actions"])
        if len(X) > 0:
            train_X_list.append(X)
            train_Y_list.append(Y)
    train_X = np.concatenate(train_X_list)
    train_Y = np.concatenate(train_Y_list)

    val_X_list, val_Y_list = [], []
    for seq in val_seqs:
        X, Y = build_features_from_sequence(seq["pac"], seq["actions"])
        if len(X) > 0:
            val_X_list.append(X)
            val_Y_list.append(Y)
    val_X = np.concatenate(val_X_list)
    val_Y = np.concatenate(val_Y_list)

    print(f"  Train: {train_X.shape[0]:,} samples, Val: {val_X.shape[0]:,} samples")
    print(f"  Features: {train_X.shape[2]}, Lookback: {train_X.shape[1]}, Horizon: {HORIZON}s")

    # ── Step 3: Train TCN-TRIBE ──
    print("\n" + "=" * 70)
    print("Step 3: Training TCN-TRIBE")
    print("=" * 70)

    t0 = time.time()
    model = train_tcn_tribe(
        train_X, train_Y, val_X, val_Y,
        epochs=80, batch_size=128, lr=1e-3, device=device,
    )
    elapsed = time.time() - t0
    n_params = sum(p.numel() for p in model.parameters())
    print(f"\n  Trained in {elapsed:.1f}s, {n_params:,} parameters")

    # ── Step 4: Evaluate alignment across severities ──
    print("\n" + "=" * 70)
    print("Step 4: Alignment evaluation (realistic noise, N=35 per severity)")
    print("=" * 70)

    n_subjects = 35
    duration_sec = 600
    base_seed = 42
    severities = ["healthy", "mild", "moderate", "severe"]

    controllers = [
        FixedScheduleCtrl(),
        ReactiveCtrl(),
        TCNTribeController(model),
    ]

    results = {}

    for severity in severities:
        print(f"\n  {'─' * 60}")
        print(f"  Severity: {severity.upper()}")
        print(f"  {'─' * 60}")

        sev_results = {}
        for ctrl in controllers:
            trials = []
            for subj in range(n_subjects):
                seed = base_seed + subj * 137
                m = run_trial(ctrl, severity, duration_sec, seed)
                trials.append(m)

            alignments = np.array([t["alignment"] for t in trials])
            low_pac = np.array([t["low_pac_stim_rate"] for t in trials])
            pac_gaps = np.array([t["pac_gap"] for t in trials])

            sev_results[ctrl.name] = {
                "alignment_mean": round(float(np.mean(alignments)), 4),
                "alignment_std": round(float(np.std(alignments)), 4),
                "low_pac_stim_mean": round(float(np.mean(low_pac)), 4),
                "pac_gap_mean": round(float(np.mean(pac_gaps)), 6),
                "trials": trials,
                "alignments": alignments.tolist(),
            }

            print(
                f"    {ctrl.name:25s}: align={np.mean(alignments):.3f}±{np.std(alignments):.3f}"
                f"  low_pac={np.mean(low_pac):.3f}  gap={np.mean(pac_gaps):+.5f}"
            )

        # Oracle
        oracle_trials = []
        for subj in range(n_subjects):
            seed = base_seed + subj * 137
            m = run_oracle_trial(severity, duration_sec, seed)
            oracle_trials.append(m)
        o_align = np.array([t["alignment"] for t in oracle_trials])
        sev_results["Oracle"] = {
            "alignment_mean": round(float(np.mean(o_align)), 4),
            "alignment_std": round(float(np.std(o_align)), 4),
            "trials": oracle_trials,
        }
        print(f"    {'Oracle':25s}: align={np.mean(o_align):.3f}±{np.std(o_align):.3f}")

        # Effect sizes: TCN-TRIBE vs Reactive
        tcn_align = np.array(sev_results["TCN-TRIBE Predictive"]["alignments"])
        react_align = np.array(sev_results["Reactive Threshold"]["alignments"])
        g = hedges_g(tcn_align, react_align)
        from scipy.stats import wilcoxon
        _, p = wilcoxon(tcn_align, react_align)
        print(f"\n    TCN-TRIBE vs Reactive: g={g:.3f}, p={p:.4f}")

        # % of oracle
        oracle_mean = float(np.mean(o_align))
        tcn_mean = float(np.mean(tcn_align))
        pct_oracle = 100.0 * tcn_mean / oracle_mean if oracle_mean > 0 else 0
        print(f"    TCN-TRIBE = {pct_oracle:.1f}% of Oracle")

        sev_results["tcn_vs_reactive_g"] = round(g, 4)
        sev_results["tcn_vs_reactive_p"] = round(float(p), 6)
        sev_results["tcn_pct_oracle"] = round(pct_oracle, 1)

        results[severity] = sev_results

    # ── Save results ──
    out_dir = ROOT / "results" / "tribe_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "tcn_tribe_alignment_results.json"

    # Strip non-serializable fields
    save_data = {}
    for sev, sev_data in results.items():
        save_data[sev] = {}
        for k, v in sev_data.items():
            if isinstance(v, dict):
                save_data[sev][k] = {
                    kk: vv for kk, vv in v.items() if kk != "trials"
                }
            else:
                save_data[sev][k] = v

    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")

    # Save model checkpoint
    ckpt_path = ROOT / "models" / "tcn_tribe.pth"
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({
        "state_dict": model.state_dict(),
        "n_features": N_FEATURES,
        "lookback": LOOKBACK,
        "horizon": HORIZON,
        "n_params": n_params,
        "y_mean": model._y_mean,
        "y_std": model._y_std,
        "feat_mean": model._feat_mean.tolist(),
        "feat_std": model._feat_std.tolist(),
    }, ckpt_path)
    print(f"  Checkpoint saved to {ckpt_path}")

    print("\n" + "=" * 70)
    print("  DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
