"""
Small sweep utility for lookback/horizon settings.

Example:
    python temporal_multiscale/sweep_multiscale_configs.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run_cmd(cmd: str) -> int:
    print(f"\n[RUN] {cmd}")
    return subprocess.call(cmd, shell=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Sweep multiscale temporal settings.")
    p.add_argument("--python", default=".\\venv\\Scripts\\python.exe", type=str)
    p.add_argument("--epochs", default=20, type=int)
    p.add_argument("--patience", default=6, type=int)
    p.add_argument("--batch-size", default=128, type=int)
    p.add_argument("--hidden", default=64, type=int)
    p.add_argument(
        "--configs",
        default="20:1,20:2,20:5,30:5",
        type=str,
        help="Comma-separated lookback:horizon pairs",
    )
    p.add_argument("--models-dir", default="models", type=str)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    models_dir = Path(args.models_dir)
    models_dir.mkdir(parents=True, exist_ok=True)

    pairs = []
    for token in args.configs.split(","):
        lb, hz = token.split(":")
        pairs.append((int(lb), int(hz)))

    for lb, hz in pairs:
        dataset_dir = f"data/processed/multiscale_temporal_lb{lb}_hz{hz}"
        run_name = f"multiscale_tcn_lb{lb}_hz{hz}"
        cmd = (
            f'{args.python} temporal_multiscale/train_multiscale_tcn.py '
            f'--rebuild-dataset '
            f'--dataset-dir "{dataset_dir}" '
            f'--models-dir "{args.models_dir}" '
            f'--run-name "{run_name}" '
            f'--lookback {lb} --horizon {hz} '
            f'--epochs {args.epochs} --patience {args.patience} '
            f'--batch-size {args.batch_size} --hidden {args.hidden}'
        )
        code = run_cmd(cmd)
        if code != 0:
            print(f"[WARN] Run failed for lb={lb}, hz={hz} (exit={code})")

    # Aggregate summaries
    rows = []
    for p in models_dir.glob("summary_multiscale_tcn_lb*_hz*.json"):
        s = json.loads(p.read_text())
        rows.append(
            {
                "run_name": s["run_name"],
                "best_val_future_r2": s["best_val_future_r2"],
                "test_future_r2": s["test_future_metrics"]["r2"],
                "test_future_corr": s["test_future_metrics"]["corr"],
                "test_delta_r2": s["test_delta_metrics"]["r2"],
            }
        )
    rows = sorted(rows, key=lambda x: x["test_future_r2"], reverse=True)

    out = models_dir / "sweep_multiscale_results.json"
    out.write_text(json.dumps(rows, indent=2))
    print(f"\nSaved sweep summary: {out}")
    for r in rows[:5]:
        print(
            f"- {r['run_name']}: "
            f"test_future_r2={r['test_future_r2']:.4f}, "
            f"test_future_corr={r['test_future_corr']:.4f}"
        )


if __name__ == "__main__":
    main()

