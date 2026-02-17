"""
Comprehensive submission-grade audit for multiscale temporal PAC pipeline.

Audit dimensions:
1) Split integrity and temporal causality.
2) Oracle-feature dependency (uses true PAC history as input).
3) Label-shuffle sanity test (should destroy performance).
4) Feature ablations:
   - full features
   - no PAC-derived features
   - PAC-only features
5) Inference realism note:
   - The deployed model must obtain pac_current from a realtime estimator,
     not from hidden ground truth labels.

This script produces a JSON report and console summary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score


def _corr(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if np.std(y_true) < 1e-12 or np.std(y_pred) < 1e-12:
        return 0.0
    return float(np.corrcoef(y_true, y_pred)[0, 1])


def _load(dataset_dir: Path) -> Dict[str, dict]:
    out = {}
    for split in ["train", "val", "test"]:
        out[split] = dict(np.load(dataset_dir / f"{split}_multiscale.npz", allow_pickle=True))
    out["meta"] = json.loads((dataset_dir / "metadata.json").read_text())
    return out


def _basic_integrity(data: Dict[str, dict]) -> Dict[str, object]:
    tr_sub = set(data["train"]["subjects"].tolist())
    va_sub = set(data["val"]["subjects"].tolist())
    te_sub = set(data["test"]["subjects"].tolist())
    overlap = {
        "train_val": sorted(tr_sub & va_sub),
        "train_test": sorted(tr_sub & te_sub),
        "val_test": sorted(va_sub & te_sub),
    }
    no_overlap = not (overlap["train_val"] or overlap["train_test"] or overlap["val_test"])

    temporal_ok = True
    temporal_details = {}
    for split in ["train", "val", "test"]:
        d = data[split]
        ok = bool(np.all(d["target_idx"] > d["end_idx"]) and np.all(d["start_idx"] <= d["end_idx"]))
        temporal_ok = temporal_ok and ok
        temporal_details[split] = ok

    return {
        "subject_overlap": overlap,
        "no_subject_overlap": no_overlap,
        "temporal_causality_ok": temporal_ok,
        "temporal_causality_by_split": temporal_details,
    }


def _fit_ridge(
    x_tr: np.ndarray,
    y_tr: np.ndarray,
    x_te: np.ndarray,
    y_te: np.ndarray,
    alpha: float = 1.0,
) -> Dict[str, float]:
    m = Ridge(alpha=alpha)
    m.fit(x_tr, y_tr)
    p = m.predict(x_te)
    return {
        "r2": float(r2_score(y_te, p)),
        "corr": _corr(y_te, p),
    }


def _feature_group_indices(feature_names: List[str]) -> Dict[str, List[int]]:
    # Dataset builder order:
    # [spectral_00..spectral_60] + [pac_* 7 cols] + [context 5 cols]
    pac_prefix = "pac_"
    ctx_names = {
        "stim_state",
        "time_since_switch_60s",
        "cycle_phase_sin",
        "cycle_phase_cos",
    }
    idx_spectral = [i for i, n in enumerate(feature_names) if n.startswith("spectral_")]
    idx_pac = [i for i, n in enumerate(feature_names) if n.startswith(pac_prefix)]
    idx_ctx = [i for i, n in enumerate(feature_names) if n in ctx_names or n.startswith("stim_frac_")]
    return {
        "spectral": idx_spectral,
        "pac": idx_pac,
        "context": idx_ctx,
    }


def _ablation_tests(data: Dict[str, dict]) -> Dict[str, Dict[str, float]]:
    tr = data["train"]
    te = data["test"]
    fn = [str(x) for x in tr["feature_names"].tolist()]
    groups = _feature_group_indices(fn)

    # Flatten sequence features
    x_tr = tr["x_seq"].reshape(tr["x_seq"].shape[0], -1)
    x_te = te["x_seq"].reshape(te["x_seq"].shape[0], -1)
    y_tr = tr["y_future"]
    y_te = te["y_future"]

    t = tr["x_seq"].shape[1]
    f = tr["x_seq"].shape[2]
    assert f == len(fn)

    def build_mask(base_idxs: List[int]) -> np.ndarray:
        mask = np.zeros(t * f, dtype=bool)
        for step in range(t):
            offset = step * f
            for i in base_idxs:
                mask[offset + i] = True
        return mask

    full = _fit_ridge(x_tr, y_tr, x_te, y_te, alpha=1.0)

    no_pac_mask = build_mask(groups["spectral"] + groups["context"])
    no_pac = _fit_ridge(x_tr[:, no_pac_mask], y_tr, x_te[:, no_pac_mask], y_te, alpha=1.0)

    pac_only_mask = build_mask(groups["pac"])
    pac_only = _fit_ridge(x_tr[:, pac_only_mask], y_tr, x_te[:, pac_only_mask], y_te, alpha=1.0)

    spectral_only_mask = build_mask(groups["spectral"])
    spectral_only = _fit_ridge(
        x_tr[:, spectral_only_mask], y_tr, x_te[:, spectral_only_mask], y_te, alpha=1.0
    )

    return {
        "full_features": full,
        "no_pac_features": no_pac,
        "pac_only_features": pac_only,
        "spectral_only_features": spectral_only,
    }


def _shuffle_label_sanity(data: Dict[str, dict]) -> Dict[str, float]:
    tr = data["train"]
    te = data["test"]

    x_tr = tr["x_seq"].reshape(tr["x_seq"].shape[0], -1)
    x_te = te["x_seq"].reshape(te["x_seq"].shape[0], -1)
    y_tr = tr["y_future"].copy()
    y_te = te["y_future"]

    rng = np.random.default_rng(42)
    rng.shuffle(y_tr)

    res = _fit_ridge(x_tr, y_tr, x_te, y_te, alpha=1.0)
    return res


def _persistence_baseline(data: Dict[str, dict]) -> Dict[str, float]:
    te = data["test"]
    y = te["y_future"]
    p = te["last_pac"]
    return {"r2": float(r2_score(y, p)), "corr": _corr(y, p)}


def run_audit(dataset_dir: Path, output_json: Path) -> Dict[str, object]:
    data = _load(dataset_dir)

    report: Dict[str, object] = {}
    report["dataset_dir"] = str(dataset_dir)
    report["metadata"] = data["meta"]
    report["integrity"] = _basic_integrity(data)
    report["persistence_baseline"] = _persistence_baseline(data)
    report["ablation"] = _ablation_tests(data)
    report["shuffle_label_sanity"] = _shuffle_label_sanity(data)

    # High-level verdict:
    integrity_ok = (
        report["integrity"]["no_subject_overlap"]
        and report["integrity"]["temporal_causality_ok"]
    )
    shuffle_ok = report["shuffle_label_sanity"]["r2"] < 0.05
    report["verdict"] = {
        "integrity_ok": bool(integrity_ok),
        "shuffle_sanity_ok": bool(shuffle_ok),
        "passes_submission_gate": bool(integrity_ok and shuffle_ok),
        "notes": [
            "PAC-derived input features are causal but can behave like oracle features if realtime PAC estimator is ideal.",
            "For strict deployment realism, evaluate end-to-end with PAC estimated from EEG online.",
            "High R² with target smoothing reflects latent-state predictability, not raw instantaneous PAC predictability.",
        ],
    }

    output_json.write_text(json.dumps(report, indent=2))
    return report


def print_summary(report: Dict[str, object]) -> None:
    print("=" * 90)
    print("COMPREHENSIVE SUBMISSION AUDIT")
    print("=" * 90)
    meta = report["metadata"]
    print(
        f"Dataset: lookback={meta['lookback']}, horizon={meta['horizon']}, "
        f"target_smooth_window={meta.get('target_smooth_window', 1)}"
    )
    print(
        f"Samples: train={meta['n_train']}, val={meta['n_val']}, test={meta['n_test']}, "
        f"features={meta['n_features']}"
    )
    print()

    integ = report["integrity"]
    print(f"Integrity - no subject overlap: {integ['no_subject_overlap']}")
    print(f"Integrity - temporal causality: {integ['temporal_causality_ok']}")

    pb = report["persistence_baseline"]
    print(f"Baseline persistence (test): R2={pb['r2']:.4f}, corr={pb['corr']:.4f}")

    print("\nAblation (Ridge, test):")
    for k, v in report["ablation"].items():
        print(f"- {k}: R2={v['r2']:.4f}, corr={v['corr']:.4f}")

    sh = report["shuffle_label_sanity"]
    print(f"\nShuffle-label sanity: R2={sh['r2']:.4f}, corr={sh['corr']:.4f}")

    verdict = report["verdict"]
    print("\nVerdict:")
    print(f"- integrity_ok: {verdict['integrity_ok']}")
    print(f"- shuffle_sanity_ok: {verdict['shuffle_sanity_ok']}")
    print(f"- passes_submission_gate: {verdict['passes_submission_gate']}")
    print("=" * 90)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Comprehensive submission-grade audit.")
    p.add_argument(
        "--dataset-dir",
        default="data/processed/multiscale_temporal_lb20_hz1_ts5",
        type=str,
    )
    p.add_argument(
        "--output-json",
        default="models/comprehensive_audit_multiscale_ts5.json",
        type=str,
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    report = run_audit(Path(args.dataset_dir), Path(args.output_json))
    print_summary(report)
    if not report["verdict"]["passes_submission_gate"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

