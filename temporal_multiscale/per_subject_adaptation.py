"""
Per-subject adaptation via calibration windows.

For each test subject:
  1. Use first N windows as calibration data.
  2. Fit a per-subject Ridge (optionally blended with the global Ridge).
  3. Fine-tune TCN heads on calibration data (backbone frozen).
  4. Evaluate on remaining (non-calibration) windows.

Usage:
    python temporal_multiscale/per_subject_adaptation.py \
        --checkpoint models/best_multiscale_tcn_lb20_hz1_ts5.pth \
        --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


# ---------------------------------------------------------------------------
# Per-subject data helpers
# ---------------------------------------------------------------------------

def load_test_by_subject(dataset_dir: Path) -> Dict[str, Dict[str, np.ndarray]]:
    """Load test split and group by subject."""
    d = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)
    subjects = d["subjects"]
    unique = np.unique(subjects)
    out: Dict[str, Dict[str, np.ndarray]] = {}
    for subj in unique:
        mask = subjects == subj
        out[subj] = {
            "x_seq": d["x_seq"][mask],
            "y_future": d["y_future"][mask],
            "y_delta": d["y_delta"][mask],
            "y_future_norm": d["y_future_norm"][mask],
            "y_delta_norm": d["y_delta_norm"][mask],
            "last_pac": d["last_pac"][mask],
        }
    return out


def split_calibration(
    subj_data: Dict[str, np.ndarray], n_calib: int
) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
    """Split subject data into calibration (first N) and eval (rest)."""
    calib, evl = {}, {}
    for key, arr in subj_data.items():
        calib[key] = arr[:n_calib]
        evl[key] = arr[n_calib:]
    return calib, evl


# ---------------------------------------------------------------------------
# Persistence baseline
# ---------------------------------------------------------------------------

def persistence_eval(evl: Dict[str, np.ndarray]) -> Dict[str, float]:
    y_true = evl["y_future"]
    y_pred = evl["last_pac"]
    return {"r2": _r2(y_true, y_pred), "rmse": _rmse(y_true, y_pred),
            "corr": _corr(y_true, y_pred)}


# ---------------------------------------------------------------------------
# Ridge adaptation
# ---------------------------------------------------------------------------

def _flatten(x_seq: np.ndarray) -> np.ndarray:
    return x_seq.reshape(x_seq.shape[0], -1)


def ridge_global(
    dataset_dir: Path, alpha: float = 1.0
) -> Tuple[Ridge, np.ndarray, np.ndarray]:
    """Train a global Ridge on the full training split. Returns model."""
    train = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    x = _flatten(train["x_seq"].astype(np.float64))
    y = train["y_future"].astype(np.float64)
    model = Ridge(alpha=alpha)
    model.fit(x, y)
    return model, x, y


def ridge_per_subject(
    calib: Dict[str, np.ndarray],
    evl: Dict[str, np.ndarray],
    global_ridge: Ridge,
    blend_alpha: float = 0.5,
) -> Dict[str, float]:
    """Per-subject Ridge: blend global with locally-fit Ridge."""
    x_calib = _flatten(calib["x_seq"].astype(np.float64))
    y_calib = calib["y_future"].astype(np.float64)
    x_eval = _flatten(evl["x_seq"].astype(np.float64))
    y_eval = evl["y_future"].astype(np.float64)

    local_ridge = Ridge(alpha=1.0)
    local_ridge.fit(x_calib, y_calib)

    y_global = global_ridge.predict(x_eval)
    y_local = local_ridge.predict(x_eval)
    y_blend = blend_alpha * y_global + (1.0 - blend_alpha) * y_local

    return {
        "global_r2": _r2(y_eval, y_global),
        "local_r2": _r2(y_eval, y_local),
        "blend_r2": _r2(y_eval, y_blend),
        "global_rmse": _rmse(y_eval, y_global),
        "local_rmse": _rmse(y_eval, y_local),
        "blend_rmse": _rmse(y_eval, y_blend),
    }


# ---------------------------------------------------------------------------
# TCN fine-tuning
# ---------------------------------------------------------------------------

def tcn_finetune(
    checkpoint_path: str,
    calib: Dict[str, np.ndarray],
    evl: Dict[str, np.ndarray],
    scalers: Dict[str, float],
    lr: float = 1e-4,
    epochs: int = 10,
    patience: int = 3,
    device_str: str = "cpu",
) -> Dict[str, float]:
    """Fine-tune TCN heads on calibration data, evaluate on eval."""
    device = torch.device(device_str)
    ckpt = torch.load(checkpoint_path, map_location=device)
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device)

    # Freeze backbone, only train heads
    model.freeze_backbone()

    yf_mean = scalers["yf_mean"]
    yf_std = scalers["yf_std"]

    # Calibration tensors
    x_cal = torch.from_numpy(calib["x_seq"]).float().to(device)
    y_cal = torch.from_numpy(calib["y_future_norm"]).float().to(device)

    optimizer = torch.optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()), lr=lr
    )
    huber = nn.HuberLoss(delta=1.0)

    best_loss = float("inf")
    best_state = copy.deepcopy(model.state_dict())
    no_improve = 0

    model.train()
    for ep in range(epochs):
        out = model(x_cal)
        loss = huber(out["future"], y_cal)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if loss.item() < best_loss:
            best_loss = loss.item()
            best_state = copy.deepcopy(model.state_dict())
            no_improve = 0
        else:
            no_improve += 1
            if no_improve >= patience:
                break

    model.load_state_dict(best_state)
    model.eval()

    # Evaluate on held-out eval windows
    x_ev = torch.from_numpy(evl["x_seq"]).float().to(device)
    y_ev = evl["y_future"].astype(np.float64)

    with torch.no_grad():
        pred_norm = model(x_ev)["future"].cpu().numpy()
    pred_raw = pred_norm * yf_std + yf_mean

    # Also compute non-adapted TCN baseline
    ckpt2 = torch.load(checkpoint_path, map_location=device)
    model_base = MultiscaleCausalTCN(cfg)
    model_base.load_state_dict(ckpt2["model_state_dict"])
    model_base.to(device)
    model_base.eval()
    with torch.no_grad():
        base_norm = model_base(x_ev)["future"].cpu().numpy()
    base_raw = base_norm * yf_std + yf_mean

    return {
        "tcn_base_r2": _r2(y_ev, base_raw),
        "tcn_adapted_r2": _r2(y_ev, pred_raw),
        "tcn_base_rmse": _rmse(y_ev, base_raw),
        "tcn_adapted_rmse": _rmse(y_ev, pred_raw),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Per-subject adaptation.")
    p.add_argument("--checkpoint", type=str, required=True)
    p.add_argument("--dataset-dir", type=str, required=True)
    p.add_argument("--output-json", type=str, default="")
    p.add_argument("--n-calib", default="30,60,120", type=str,
                   help="Comma-separated calibration sizes to test")
    p.add_argument("--blend-alpha", default=0.5, type=float)
    p.add_argument("--finetune-lr", default=1e-4, type=float)
    p.add_argument("--finetune-epochs", default=10, type=int)
    p.add_argument("--device", default="cpu", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)
    calib_sizes = [int(x) for x in args.n_calib.split(",")]

    # Load scalers
    scalers_npz = np.load(dataset_dir / "scalers.npz")
    scalers = {
        "yf_mean": float(scalers_npz["y_future_mean"]),
        "yf_std": float(scalers_npz["y_future_std"]),
    }

    # Global Ridge
    print("Fitting global Ridge on train split...")
    global_ridge, _, _ = ridge_global(dataset_dir)

    # Per-subject test data
    subject_data = load_test_by_subject(dataset_dir)
    print(f"Test subjects: {sorted(subject_data.keys())}")

    all_results: List[Dict] = []

    for n_cal in calib_sizes:
        print(f"\n{'='*60}")
        print(f"CALIBRATION SIZE: {n_cal} windows")
        print(f"{'='*60}")

        for subj, data in sorted(subject_data.items()):
            n_total = data["x_seq"].shape[0]
            if n_total <= n_cal + 10:
                print(f"  {subj}: skipped (only {n_total} windows)")
                continue

            calib, evl = split_calibration(data, n_cal)
            n_eval = evl["x_seq"].shape[0]

            # Persistence
            persist = persistence_eval(evl)

            # Ridge
            ridge_res = ridge_per_subject(
                calib, evl, global_ridge, blend_alpha=args.blend_alpha
            )

            # TCN fine-tune
            tcn_res = tcn_finetune(
                checkpoint_path=args.checkpoint,
                calib=calib,
                evl=evl,
                scalers=scalers,
                lr=args.finetune_lr,
                epochs=args.finetune_epochs,
                device_str=args.device,
            )

            row = {
                "subject": subj,
                "n_calib": n_cal,
                "n_eval": n_eval,
                "persistence_r2": persist["r2"],
                **ridge_res,
                **tcn_res,
            }
            all_results.append(row)

            best_method = max(
                [("persistence", persist["r2"]),
                 ("ridge_blend", ridge_res["blend_r2"]),
                 ("tcn_adapted", tcn_res["tcn_adapted_r2"])],
                key=lambda x: x[1],
            )
            print(
                f"  {subj}: n_eval={n_eval:4d} | "
                f"persist={persist['r2']:.3f} | "
                f"ridge_blend={ridge_res['blend_r2']:.3f} | "
                f"tcn_base={tcn_res['tcn_base_r2']:.3f} | "
                f"tcn_adapt={tcn_res['tcn_adapted_r2']:.3f} | "
                f"best={best_method[0]}"
            )

    # Aggregate summary
    print(f"\n{'='*60}")
    print("AGGREGATE SUMMARY")
    print(f"{'='*60}")

    for n_cal in calib_sizes:
        rows = [r for r in all_results if r["n_calib"] == n_cal]
        if not rows:
            continue
        persist_r2s = [r["persistence_r2"] for r in rows]
        blend_r2s = [r["blend_r2"] for r in rows]
        tcn_base_r2s = [r["tcn_base_r2"] for r in rows]
        tcn_adapt_r2s = [r["tcn_adapted_r2"] for r in rows]
        print(f"\n  n_calib={n_cal}:")
        print(f"    Persistence   mean R2 = {np.mean(persist_r2s):.4f} (std={np.std(persist_r2s):.4f})")
        print(f"    Ridge blend   mean R2 = {np.mean(blend_r2s):.4f} (std={np.std(blend_r2s):.4f})")
        print(f"    TCN base      mean R2 = {np.mean(tcn_base_r2s):.4f} (std={np.std(tcn_base_r2s):.4f})")
        print(f"    TCN adapted   mean R2 = {np.mean(tcn_adapt_r2s):.4f} (std={np.std(tcn_adapt_r2s):.4f})")

    # Save
    output_path = args.output_json or str(
        Path(args.checkpoint).parent / "per_subject_adaptation_results.json"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(all_results, indent=2))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
