"""
PAC direction classifier: 3-class prediction of future PAC change.

Classes:
    WILL_INCREASE  — delta_pac >  threshold
    STABLE         — |delta_pac| <= threshold
    WILL_DECREASE  — delta_pac < -threshold

Threshold = 0.5 * std(delta_pac) from training set.

Models:
    - Ridge (via sklearn RidgeClassifier)
    - Optional: TCN with softmax head

Usage:
    python temporal_multiscale/direction_classifier.py \
        --dataset-dir data/processed/multiscale_temporal_lb20_hz1_ts5_clean
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.linear_model import RidgeClassifier
from sklearn.metrics import (
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# Label construction
# ---------------------------------------------------------------------------

CLASS_NAMES = ["WILL_DECREASE", "STABLE", "WILL_INCREASE"]
CLASS_MAP = {0: "WILL_DECREASE", 1: "STABLE", 2: "WILL_INCREASE"}


def make_direction_labels(
    y_delta: np.ndarray, threshold: float
) -> np.ndarray:
    """Convert continuous delta to 3-class labels."""
    labels = np.ones(len(y_delta), dtype=np.int64)  # STABLE
    labels[y_delta < -threshold] = 0  # WILL_DECREASE
    labels[y_delta > threshold] = 2   # WILL_INCREASE
    return labels


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def eval_classifier(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Dict:
    ba = balanced_accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    report = classification_report(
        y_true, y_pred, labels=[0, 1, 2],
        target_names=CLASS_NAMES, output_dict=True, zero_division=0,
    )
    return {
        "balanced_accuracy": float(ba),
        "confusion_matrix": cm.tolist(),
        "per_class": {
            name: {
                "precision": report[name]["precision"],
                "recall": report[name]["recall"],
                "f1": report[name]["f1-score"],
                "support": int(report[name]["support"]),
            }
            for name in CLASS_NAMES
        },
    }


# ---------------------------------------------------------------------------
# Baselines
# ---------------------------------------------------------------------------

def majority_baseline(y_train: np.ndarray, y_test: np.ndarray) -> Dict:
    """Predict most frequent class from training set."""
    majority = int(np.argmax(np.bincount(y_train, minlength=3)))
    y_pred = np.full(len(y_test), majority)
    return eval_classifier(y_test, y_pred)


def persistence_direction_baseline(
    last_pac: np.ndarray, y_future: np.ndarray, threshold: float
) -> Dict:
    """Predict direction = 0 (STABLE) always — PAC doesn't change."""
    y_true = make_direction_labels(y_future - last_pac, threshold)
    y_pred = np.ones(len(y_true), dtype=np.int64)  # all STABLE
    return eval_classifier(y_true, y_pred)


# ---------------------------------------------------------------------------
# Ridge classifier
# ---------------------------------------------------------------------------

def ridge_direction(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_test: np.ndarray,
    y_test: np.ndarray,
    alpha: float = 1.0,
) -> Tuple[Dict, RidgeClassifier]:
    clf = RidgeClassifier(alpha=alpha)
    clf.fit(x_train, y_train)
    y_pred = clf.predict(x_test)
    return eval_classifier(y_test, y_pred), clf


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PAC direction classifier.")
    p.add_argument("--dataset-dir", type=str, required=True)
    p.add_argument("--output-json", default="", type=str)
    p.add_argument("--alpha", default=1.0, type=float,
                   help="Ridge regularization strength")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    dataset_dir = Path(args.dataset_dir)

    print("=" * 60)
    print("PAC DIRECTION CLASSIFIER")
    print("=" * 60)

    # Load data
    train = np.load(dataset_dir / "train_multiscale.npz", allow_pickle=True)
    test = np.load(dataset_dir / "test_multiscale.npz", allow_pickle=True)

    y_delta_train = train["y_delta"].astype(np.float64)
    y_delta_test = test["y_delta"].astype(np.float64)

    # Threshold = 0.5 * std(delta_pac) from training set
    threshold = 0.5 * float(np.std(y_delta_train))
    print(f"Threshold: {threshold:.6f} (0.5 * train delta std={np.std(y_delta_train):.6f})")

    # Make labels
    labels_train = make_direction_labels(y_delta_train, threshold)
    labels_test = make_direction_labels(y_delta_test, threshold)

    for cls_id, cls_name in CLASS_MAP.items():
        n_train = int((labels_train == cls_id).sum())
        n_test = int((labels_test == cls_id).sum())
        print(f"  {cls_name}: train={n_train}, test={n_test}")

    # Flatten features
    x_train = train["x_seq"].reshape(train["x_seq"].shape[0], -1).astype(np.float64)
    x_test = test["x_seq"].reshape(test["x_seq"].shape[0], -1).astype(np.float64)

    results = {}

    # Majority baseline
    print("\n--- Majority Baseline ---")
    majority = majority_baseline(labels_train, labels_test)
    results["majority"] = majority
    print(f"Balanced accuracy: {majority['balanced_accuracy']:.4f}")

    # Persistence baseline
    print("\n--- Persistence (always STABLE) ---")
    persist = persistence_direction_baseline(
        test["last_pac"].astype(np.float64),
        test["y_future"].astype(np.float64),
        threshold,
    )
    results["persistence_stable"] = persist
    print(f"Balanced accuracy: {persist['balanced_accuracy']:.4f}")

    # Ridge classifier
    print("\n--- Ridge Classifier ---")
    ridge_res, ridge_clf = ridge_direction(
        x_train, labels_train, x_test, labels_test, alpha=args.alpha,
    )
    results["ridge"] = ridge_res
    print(f"Balanced accuracy: {ridge_res['balanced_accuracy']:.4f}")

    # Per-class details
    print(f"\n{'Class':<16s} {'Precision':>10s} {'Recall':>8s} {'F1':>8s} {'Support':>8s}")
    print("-" * 52)
    for cls_name in CLASS_NAMES:
        c = ridge_res["per_class"][cls_name]
        print(
            f"{cls_name:<16s} "
            f"{c['precision']:>10.3f} {c['recall']:>8.3f} "
            f"{c['f1']:>8.3f} {c['support']:>8d}"
        )

    # Confusion matrix
    print("\nConfusion matrix (rows=true, cols=pred):")
    cm = np.array(ridge_res["confusion_matrix"])
    header = "  ".join(f"{n[:5]:>7s}" for n in CLASS_NAMES)
    print(f"{'':>16s} {header}")
    for i, name in enumerate(CLASS_NAMES):
        row = "  ".join(f"{cm[i, j]:>7d}" for j in range(3))
        print(f"{name:<16s} {row}")

    results["threshold"] = threshold

    # Save
    output_path = args.output_json or str(
        dataset_dir / "direction_classifier_results.json"
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
