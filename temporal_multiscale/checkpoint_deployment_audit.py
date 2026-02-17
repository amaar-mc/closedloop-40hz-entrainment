"""
Checkpoint deployment realism audit.

Evaluates a trained checkpoint under multiple inference scenarios:
1) baseline (as trained),
2) PAC features zeroed (simulates no PAC oracle),
3) PAC features corrupted with Gaussian noise.

This quantifies how much performance depends on PAC-history oracle quality.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temporal_multiscale.multiscale_tcn import ModelConfig, MultiscaleCausalTCN


class SeqDataset(Dataset):
    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = d["x_seq"].astype(np.float32)
        self.y_future_norm = d["y_future_norm"].astype(np.float32)
        self.y_delta_norm = d["y_delta_norm"].astype(np.float32)
        self.feature_names = [str(x) for x in d["feature_names"].tolist()]

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int):
        return {
            "x_seq": torch.from_numpy(self.x[i]),
            "y_future": torch.tensor(self.y_future_norm[i], dtype=torch.float32),
            "y_delta": torch.tensor(self.y_delta_norm[i], dtype=torch.float32),
        }


def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _eval(
    model: MultiscaleCausalTCN,
    x: np.ndarray,
    y_future_norm: np.ndarray,
    y_delta_norm: np.ndarray,
    yf_mean: float,
    yf_std: float,
    yd_mean: float,
    yd_std: float,
    device: torch.device,
) -> Dict[str, Dict[str, float]]:
    model.eval()
    with torch.no_grad():
        out = model(torch.from_numpy(x).float().to(device))
        pf = out["future"].cpu().numpy()
        pd = out["delta"].cpu().numpy()

    yfn = y_future_norm
    ydn = y_delta_norm

    pf_raw = pf * yf_std + yf_mean
    yfn_raw = yfn * yf_std + yf_mean
    pd_raw = pd * yd_std + yd_mean
    ydn_raw = ydn * yd_std + yd_mean

    future = {"r2": _r2(yfn_raw, pf_raw), "corr": _corr(yfn_raw, pf_raw)}
    delta = {"r2": _r2(ydn_raw, pd_raw), "corr": _corr(ydn_raw, pd_raw)}
    return {"future": future, "delta": delta}


def run_audit(
    checkpoint: Path,
    dataset_dir: Path,
    output_json: Path,
    noise_sigmas: List[float],
) -> Dict[str, object]:
    ckpt = torch.load(checkpoint, map_location="cpu")
    cfg = ModelConfig(**ckpt["cfg"])
    model = MultiscaleCausalTCN(cfg)
    model.load_state_dict(ckpt["model_state_dict"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    d = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)
    x = d["x_seq"].astype(np.float32)
    yfn = d["y_future_norm"].astype(np.float32)
    ydn = d["y_delta_norm"].astype(np.float32)
    feature_names = [str(v) for v in d["feature_names"].tolist()]

    pac_idxs = [i for i, n in enumerate(feature_names) if n.startswith("pac_")]
    if not pac_idxs:
        raise RuntimeError("No PAC feature columns found.")

    yf_mean = float(ckpt["scalers"]["y_future_mean"])
    yf_std = float(ckpt["scalers"]["y_future_std"])
    yd_mean = float(ckpt["scalers"]["y_delta_mean"])
    yd_std = float(ckpt["scalers"]["y_delta_std"])

    report: Dict[str, object] = {
        "checkpoint": str(checkpoint),
        "dataset_dir": str(dataset_dir),
        "target_smooth_window": ckpt["metadata"].get("target_smooth_window", 1),
        "pac_feature_count": len(pac_idxs),
        "results": {},
    }

    # Baseline
    report["results"]["baseline"] = _eval(
        model, x, yfn, ydn, yf_mean, yf_std, yd_mean, yd_std, device
    )

    # PAC-zeroed
    x_zero = x.copy()
    x_zero[:, :, pac_idxs] = 0.0
    report["results"]["pac_zeroed"] = _eval(
        model, x_zero, yfn, ydn, yf_mean, yf_std, yd_mean, yd_std, device
    )

    # PAC noisy
    rng = np.random.default_rng(42)
    noisy_results = {}
    for s in noise_sigmas:
        x_noisy = x.copy()
        noise = rng.normal(loc=0.0, scale=s, size=x_noisy[:, :, pac_idxs].shape).astype(np.float32)
        x_noisy[:, :, pac_idxs] = x_noisy[:, :, pac_idxs] + noise
        noisy_results[f"sigma_{s}"] = _eval(
            model, x_noisy, yfn, ydn, yf_mean, yf_std, yd_mean, yd_std, device
        )
    report["results"]["pac_noisy"] = noisy_results

    output_json.write_text(json.dumps(report, indent=2))
    return report


def print_summary(report: Dict[str, object]) -> None:
    print("=" * 90)
    print("CHECKPOINT DEPLOYMENT AUDIT")
    print("=" * 90)
    print(f"checkpoint: {report['checkpoint']}")
    print(f"dataset:    {report['dataset_dir']}")
    print(f"target_smooth_window: {report['target_smooth_window']}")
    print(f"pac_feature_count: {report['pac_feature_count']}")
    print()

    b = report["results"]["baseline"]["future"]
    z = report["results"]["pac_zeroed"]["future"]
    print(f"baseline future:  R2={b['r2']:.4f}, corr={b['corr']:.4f}")
    print(f"pac_zeroed future:R2={z['r2']:.4f}, corr={z['corr']:.4f}")

    print("pac_noisy future:")
    for k, v in report["results"]["pac_noisy"].items():
        print(f"- {k}: R2={v['future']['r2']:.4f}, corr={v['future']['corr']:.4f}")
    print("=" * 90)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit deployment realism of checkpoint.")
    p.add_argument(
        "--checkpoint",
        default="models/best_multiscale_tcn_lb20_hz1_ts5.pth",
        type=str,
    )
    p.add_argument(
        "--dataset-dir",
        default="data/processed/multiscale_temporal_lb20_hz1_ts5_clean",
        type=str,
    )
    p.add_argument(
        "--output-json",
        default="models/deployment_audit_multiscale_ts5.json",
        type=str,
    )
    p.add_argument(
        "--noise-sigmas",
        default="0.1,0.25,0.5,1.0",
        type=str,
        help="comma-separated std devs in normalized PAC-feature space",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    sigmas = [float(x.strip()) for x in args.noise_sigmas.split(",") if x.strip()]
    report = run_audit(
        checkpoint=Path(args.checkpoint),
        dataset_dir=Path(args.dataset_dir),
        output_json=Path(args.output_json),
        noise_sigmas=sigmas,
    )
    print_summary(report)


if __name__ == "__main__":
    main()
