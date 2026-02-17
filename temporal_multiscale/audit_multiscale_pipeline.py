"""
Audit script for multiscale temporal dataset and training artifacts.

Checks:
1) Subject-level split integrity (no overlap).
2) Temporal causality (target index strictly after sequence end).
3) Sequence shape and NaN/Inf checks.
4) Normalization sanity:
   - train features ~ N(0,1),
   - val/test not forced to exact 0 mean (train-only scaler behavior).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np


def _load_npz(path: Path) -> Dict[str, np.ndarray]:
    if not path.exists():
        raise FileNotFoundError(path)
    return dict(np.load(path, allow_pickle=True))


def _finite_check(name: str, arr: np.ndarray) -> Tuple[bool, str]:
    if not np.all(np.isfinite(arr)):
        n_bad = int(np.size(arr) - np.sum(np.isfinite(arr)))
        return False, f"{name}: {n_bad} non-finite values found"
    return True, f"{name}: finite check passed"


def run_audit(dataset_dir: Path) -> bool:
    train = _load_npz(dataset_dir / "train_multiscale.npz")
    val = _load_npz(dataset_dir / "val_multiscale.npz")
    test = _load_npz(dataset_dir / "test_multiscale.npz")
    meta = json.loads((dataset_dir / "metadata.json").read_text())

    print("=" * 80)
    print("MULTISCALE PIPELINE AUDIT")
    print("=" * 80)

    ok_all = True

    # 1) Split integrity
    tr_sub = set(train["subjects"].tolist())
    va_sub = set(val["subjects"].tolist())
    te_sub = set(test["subjects"].tolist())
    overlap_tv = tr_sub & va_sub
    overlap_tt = tr_sub & te_sub
    overlap_vt = va_sub & te_sub
    if overlap_tv or overlap_tt or overlap_vt:
        ok_all = False
        print("[FAIL] Subject leakage across splits detected:")
        if overlap_tv:
            print(f"  train∩val: {sorted(overlap_tv)}")
        if overlap_tt:
            print(f"  train∩test: {sorted(overlap_tt)}")
        if overlap_vt:
            print(f"  val∩test: {sorted(overlap_vt)}")
    else:
        print("[PASS] No subject overlap across train/val/test.")

    # 2) Temporal causality
    for split_name, split in [("train", train), ("val", val), ("test", test)]:
        if not np.all(split["target_idx"] > split["end_idx"]):
            ok_all = False
            print(f"[FAIL] {split_name}: found target_idx <= end_idx")
        elif not np.all(split["start_idx"] <= split["end_idx"]):
            ok_all = False
            print(f"[FAIL] {split_name}: found start_idx > end_idx")
        else:
            print(f"[PASS] {split_name}: temporal causality indices valid.")

    # 3) Shape and finite checks
    for split_name, split in [("train", train), ("val", val), ("test", test)]:
        x = split["x_seq"]
        yf = split["y_future"]
        yd = split["y_delta"]
        yfn = split["y_future_norm"]
        ydn = split["y_delta_norm"]
        n = x.shape[0]
        expected = (n == yf.shape[0] == yd.shape[0] == yfn.shape[0] == ydn.shape[0])
        if not expected:
            ok_all = False
            print(f"[FAIL] {split_name}: inconsistent sample counts")
        else:
            print(f"[PASS] {split_name}: sample counts consistent ({n}).")

        for name, arr in [
            (f"{split_name}.x_seq", x),
            (f"{split_name}.y_future_norm", yfn),
            (f"{split_name}.y_delta_norm", ydn),
        ]:
            ok, msg = _finite_check(name, arr)
            print(f"[{'PASS' if ok else 'FAIL'}] {msg}")
            ok_all = ok_all and ok

    # 4) Normalization sanity
    x_train = train["x_seq"].reshape(-1, train["x_seq"].shape[-1]).astype(np.float64)
    tr_mean = np.mean(x_train, axis=0)
    tr_std = np.std(x_train, axis=0)
    mean_abs = float(np.mean(np.abs(tr_mean)))
    std_dev = float(np.mean(np.abs(tr_std - 1.0)))
    if mean_abs > 0.02 or std_dev > 0.05:
        ok_all = False
        print(
            "[FAIL] Train normalization sanity failed: "
            f"mean_abs={mean_abs:.4f}, avg|std-1|={std_dev:.4f}"
        )
    else:
        print(
            "[PASS] Train normalization sanity OK: "
            f"mean_abs={mean_abs:.4f}, avg|std-1|={std_dev:.4f}"
        )

    x_val = val["x_seq"].reshape(-1, val["x_seq"].shape[-1]).astype(np.float64)
    x_test = test["x_seq"].reshape(-1, test["x_seq"].shape[-1]).astype(np.float64)
    val_mean_abs = float(np.mean(np.abs(np.mean(x_val, axis=0))))
    test_mean_abs = float(np.mean(np.abs(np.mean(x_test, axis=0))))
    print(
        "Info: val/test normalized feature mean abs = "
        f"{val_mean_abs:.4f} / {test_mean_abs:.4f} "
        "(not expected to be near zero if scaler is train-only)."
    )

    # 5) Metadata consistency
    expected_lookback = int(meta["lookback"])
    actual_lookback = int(train["x_seq"].shape[1])
    if expected_lookback != actual_lookback:
        ok_all = False
        print(
            f"[FAIL] Lookback mismatch: metadata={expected_lookback}, "
            f"data={actual_lookback}"
        )
    else:
        print(f"[PASS] Lookback matches metadata ({actual_lookback}).")

    print("\n" + "=" * 80)
    print("AUDIT RESULT")
    print("=" * 80)
    print("PASS" if ok_all else "FAIL")
    return ok_all


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit multiscale pipeline.")
    p.add_argument("--dataset-dir", default="data/processed/multiscale_temporal", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ok = run_audit(Path(args.dataset_dir))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

