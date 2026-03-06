"""Generate a timeline figure showing TCN vs Reactive decisions for one subject.

This is the most compelling figure for judges: shows real PAC trajectory
with color-coded controller decisions, highlighting where TCN anticipates
transitions that reactive misses.
"""
import sys, json
from pathlib import Path
from collections import deque
import numpy as np
import torch
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "archive" / "experimental_models"))


def main():
    import pandas as pd
    from spectral_features import SpectralFeatureExtractor
    from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN

    processed_dir = Path("data/processed")
    raw_root = Path("data/raw/ds005048")

    # Load model
    ckpt_path = list(Path("models").glob("best_multiscale_tcn_*.pth"))[0]
    device = torch.device("cpu")
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    lookback = int(ckpt["metadata"]["lookback"])

    scalers = np.load(list(processed_dir.glob("multiscale_temporal_*/scalers.npz"))[0])
    feat_mean = scalers["feature_mean"].astype(np.float32)
    feat_std = scalers["feature_std"].astype(np.float32)
    yd_std = float(scalers["y_delta_std"])
    yd_mean = float(scalers["y_delta_mean"])

    # Load one test subject for illustration
    extractor = SpectralFeatureExtractor(fs=250.0)
    d = np.load(processed_dir / "test_data.npz", allow_pickle=True)
    pac_all = d["pac"].astype(np.float64)
    subjects = d["subjects"]
    windows = d["windows"]

    # Pick a subject with interesting transitions
    unique_subjs = np.unique(subjects)
    best_subj = None
    best_transitions = 0
    for subj in unique_subjs:
        mask = subjects == subj
        sp = pac_all[mask]
        n_trans = sum(1 for i in range(1, len(sp)) if abs(sp[i] - sp[i-1]) > 1e-10)
        if n_trans > best_transitions:
            best_transitions = n_trans
            best_subj = subj

    mask = subjects == best_subj
    pac = pac_all[mask]
    subj_win = windows[mask]
    if subj_win.ndim == 4 and subj_win.shape[1] == 1:
        subj_win = subj_win.squeeze(1)
    spectral = extractor.extract(subj_win)
    n = len(pac)
    t = np.arange(n, dtype=np.float64)

    print(f"Subject: {best_subj}, {n} windows, {best_transitions} transitions")

    # Run reactive controller
    react_decisions = np.zeros(n, dtype=np.int32)
    buf = []
    for ti in range(n):
        buf.append(pac[ti])
        if len(buf) > 30: buf.pop(0)
        if len(buf) >= 10:
            mu = np.mean(buf)
            sig = np.std(buf) + 1e-12
            z = (pac[ti] - mu) / sig
            react_decisions[ti] = 1 if z < -0.5 else 0

    # Run TCN controller
    tcn_decisions = np.zeros(n, dtype=np.int32)
    seq_buf = deque(maxlen=lookback)
    pac_buf = deque(maxlen=32)
    baseline_buf = []
    state = 0
    t_in_state = 0
    delta_z_vals = np.zeros(n)

    for ti in range(n):
        p = pac[ti]
        s = spectral[ti]

        hist = list(pac_buf) + [p]
        def ml(k):
            k = min(k, len(hist))
            return float(np.mean(hist[-k:])) if k > 0 else float(p)
        d1 = float(p - hist[-2]) if len(hist) >= 2 else 0.0
        d4 = float(p - hist[-5]) if len(hist) >= 5 else 0.0
        pac_feats = np.array([p, ml(2), ml(4), ml(8), ml(16), d1, d4], dtype=np.float32)
        ctx = np.zeros(5, dtype=np.float32)
        ctx[4] = 1.0
        x = np.concatenate([s.reshape(-1), pac_feats, ctx]).astype(np.float32)
        x = (x - feat_mean) / (feat_std + 1e-8)
        seq_buf.append(x)
        pac_buf.append(float(p))
        baseline_buf.append(p)
        if len(baseline_buf) > 30:
            baseline_buf.pop(0)

        desired = None
        if len(seq_buf) >= lookback:
            x_seq = np.stack(list(seq_buf), axis=0)[None, ...]
            x_t = torch.from_numpy(x_seq).float().to(device)
            with torch.no_grad():
                out = model(x_t)
            dz = float(out["delta"].item())
            delta_z_vals[ti] = dz
            if dz < -0.3:
                desired = 1
            elif dz > 0.3:
                desired = 0

        if desired is None:
            if len(baseline_buf) >= 10:
                mu = np.mean(baseline_buf)
                sig = np.std(baseline_buf) + 1e-12
                z = (p - mu) / sig
                if z < -0.5:
                    desired = 1
                elif z > 0.5:
                    desired = 0
            if desired is None:
                desired = state

        if desired != state:
            if t_in_state >= 3:
                state = desired
                t_in_state = 0
        else:
            t_in_state += 1
        tcn_decisions[ti] = state

    # Find transitions for annotation
    transitions = []
    for i in range(1, n):
        if abs(pac[i] - pac[i-1]) > 1e-10:
            transitions.append(i)

    # --- Create figure ---
    fig, axes = plt.subplots(3, 1, figsize=(14, 8), sharex=True,
                              gridspec_kw={'height_ratios': [3, 1.2, 1.2]})

    # Panel A: PAC trajectory with epoch transitions
    ax1 = axes[0]
    ax1.plot(t, pac * 1e6, color='#333333', linewidth=1.5, zorder=3)
    median_pac = np.median(pac) * 1e6
    ax1.axhline(median_pac, color='#999999', linestyle='--', linewidth=0.8,
                label=f'Median PAC = {median_pac:.1f} µV²', zorder=1)

    # Shade epochs by PAC level
    for i in range(len(transitions)):
        start = transitions[i-1] if i > 0 else 0
        end = transitions[i]
        epoch_pac = pac[start] * 1e6
        color = '#E3F2FD' if epoch_pac < median_pac else '#FFF3E0'
        ax1.axvspan(start, end, alpha=0.3, color=color, zorder=0)
    # Last epoch
    if transitions:
        last_start = transitions[-1]
        epoch_pac = pac[last_start] * 1e6
        color = '#E3F2FD' if epoch_pac < median_pac else '#FFF3E0'
        ax1.axvspan(last_start, n, alpha=0.3, color=color, zorder=0)

    # Mark transitions
    for tr in transitions:
        ax1.axvline(tr, color='#E57373', linewidth=0.8, alpha=0.5, linestyle=':')

    ax1.set_ylabel('PAC (×10⁻⁶)', fontsize=12)
    ax1.set_title(f'Real-Data Controller Timeline — {best_subj} (test set)', fontsize=14, fontweight='bold')
    low_patch = mpatches.Patch(color='#E3F2FD', alpha=0.5, label='Low-PAC epoch (need stim)')
    high_patch = mpatches.Patch(color='#FFF3E0', alpha=0.5, label='High-PAC epoch (can rest)')
    ax1.legend(handles=[low_patch, high_patch], loc='upper right', fontsize=9, framealpha=0.9)

    # Panel B: Reactive decisions
    ax2 = axes[1]
    for ti in range(n):
        color = '#4CAF50' if react_decisions[ti] == 1 else '#EEEEEE'
        ax2.axvspan(ti, ti+1, color=color, alpha=0.7)
    # Shade low-PAC epochs faintly
    for i in range(len(transitions)):
        start = transitions[i-1] if i > 0 else 0
        end = transitions[i]
        if pac[start] < np.median(pac):
            ax2.axvspan(start, end, alpha=0.15, color='#1565C0', zorder=0)
    if transitions:
        if pac[transitions[-1]] < np.median(pac):
            ax2.axvspan(transitions[-1], n, alpha=0.15, color='#1565C0', zorder=0)
    ax2.set_ylabel('Reactive', fontsize=11)
    ax2.set_yticks([])
    stim_patch = mpatches.Patch(color='#4CAF50', alpha=0.7, label='Stimulate')
    rest_patch = mpatches.Patch(color='#EEEEEE', alpha=0.7, label='Rest')
    need_patch = mpatches.Patch(color='#1565C0', alpha=0.15, label='Low-PAC (need stim)')
    ax2.legend(handles=[stim_patch, rest_patch, need_patch], loc='upper right',
               fontsize=8, ncol=3, framealpha=0.9)

    # Panel C: TCN decisions
    ax3 = axes[2]
    for ti in range(n):
        color = '#FF9800' if tcn_decisions[ti] == 1 else '#EEEEEE'
        ax3.axvspan(ti, ti+1, color=color, alpha=0.7)
    for i in range(len(transitions)):
        start = transitions[i-1] if i > 0 else 0
        end = transitions[i]
        if pac[start] < np.median(pac):
            ax3.axvspan(start, end, alpha=0.15, color='#1565C0', zorder=0)
    if transitions:
        if pac[transitions[-1]] < np.median(pac):
            ax3.axvspan(transitions[-1], n, alpha=0.15, color='#1565C0', zorder=0)
    ax3.set_ylabel('TCN', fontsize=11)
    ax3.set_yticks([])
    ax3.set_xlabel('Time (seconds)', fontsize=12)
    stim_patch2 = mpatches.Patch(color='#FF9800', alpha=0.7, label='Stimulate')
    ax3.legend(handles=[stim_patch2, rest_patch, need_patch], loc='upper right',
               fontsize=8, ncol=3, framealpha=0.9)

    plt.tight_layout()

    out_dir = Path("results/figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "timeline_example.png", dpi=300, bbox_inches='tight')
    fig.savefig(out_dir / "timeline_example.pdf", bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_dir}/timeline_example.png")

    # Also generate threshold sensitivity figure
    sweep_data = json.loads(Path("results/threshold_sweep.json").read_text())

    fig2, ax = plt.subplots(figsize=(8, 5))
    thresholds = [r["threshold"] for r in sweep_data["thresholds"]]
    alignments = [r["alignment"] for r in sweep_data["thresholds"]]
    stim_pcts = [r["stim_pct"] for r in sweep_data["thresholds"]]
    reactive_baseline = sweep_data["reactive_baseline_alignment"]

    color1 = '#1976D2'
    color2 = '#F57C00'

    ax.plot(thresholds, alignments, 'o-', color=color1, linewidth=2,
            markersize=8, label='TCN Alignment (%)', zorder=3)
    ax.axhline(reactive_baseline, color='#E53935', linestyle='--', linewidth=1.5,
               label=f'Reactive baseline ({reactive_baseline}%)', zorder=2)

    ax2_twin = ax.twinx()
    ax2_twin.plot(thresholds, stim_pcts, 's--', color=color2, linewidth=1.5,
                  markersize=6, label='Stimulation %', alpha=0.8)
    ax2_twin.set_ylabel('Stimulation Rate (%)', fontsize=12, color=color2)
    ax2_twin.tick_params(axis='y', labelcolor=color2)
    ax2_twin.set_ylim(30, 70)

    ax.set_xlabel('Delta-z Threshold', fontsize=12)
    ax.set_ylabel('Alignment Score (%)', fontsize=12, color=color1)
    ax.tick_params(axis='y', labelcolor=color1)
    ax.set_title('TCN Robustness: Threshold Sensitivity Analysis', fontsize=14, fontweight='bold')
    ax.set_ylim(55, 80)

    # Shade the "beats reactive" region
    ax.fill_between([0.05, 1.05], reactive_baseline, 80, alpha=0.08, color='#4CAF50')
    ax.text(0.55, reactive_baseline + 1, 'TCN advantage zone', fontsize=9,
            color='#388E3C', ha='center', style='italic')

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=10)

    for spine in ['top']:
        ax.spines[spine].set_visible(False)
        ax2_twin.spines[spine].set_visible(False)

    plt.tight_layout()
    fig2.savefig(out_dir / "threshold_sensitivity.png", dpi=300, bbox_inches='tight')
    fig2.savefig(out_dir / "threshold_sensitivity.pdf", bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_dir}/threshold_sensitivity.png")


if __name__ == "__main__":
    main()
