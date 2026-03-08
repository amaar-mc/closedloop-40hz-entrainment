# AGENTS.md
Repository guidance for coding agents working in `closedloop-40hz-entrainment`.

## Authority
- This is the primary repository instruction file.
- No `.cursorrules`, `.cursor/rules/`, or `.github/copilot-instructions.md` files are present.
- Prefer this file over generic defaults when they conflict.

## Project Layout
- `src/`: static PAC pipeline: data loading, preprocessing, PAC computation, EEGNet, controller, simulator, validation.
- `temporal_multiscale/`: main causal TCN forecasting pipeline, realtime inference, audits.
- `temporal/`: older temporal experiments plus `validate_code.py`, which is still an important leakage gate.
- `rigor/`: extended robustness, multi-seed, and statistical validation.
- `scripts/pipeline/`: orchestration scripts; use carefully because some entry points have fragile import-path assumptions.
- `data/raw/`: raw OpenNeuro BIDS data; never commit it.
- `data/processed/`: generated splits and temporal datasets.
- `models/`, `results/`, `logs/`: generated artifacts.
- `docs/` and `archive/`: documentation and historical code; do not extend `archive/` unless explicitly asked.

## Environment
- Use Python 3.10+ in a virtual environment.
- Install PyTorch first if GPU-specific wheels matter, then repo requirements.

```bash
python -m venv venv
source venv/bin/activate
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt
```

- CUDA is optional; several scripts also fall back to MPS or CPU.
- Runtime defaults live in `config.yaml`, but many scripts override them via CLI args.

## Canonical Commands

### Data preparation
```bash
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed
python temporal_multiscale/build_multiscale_dataset.py --processed-dir data/processed --raw-root data/raw/ds005048 --output-dir data/processed/multiscale_temporal
```

### Model training
```bash
python src/training.py --data_dir data/processed --output_dir models --epochs 100 --batch_size 64 --device cuda
python temporal/train_temporal.py --data-dir data/processed --save-dir models
python temporal_multiscale/train_multiscale_tcn.py --dataset-dir data/processed/multiscale_temporal --models-dir models
```

### Validation and audits
```bash
python src/validation.py --output_dir results --duration 360 --n_trials 3
python temporal/validate_code.py
python temporal_multiscale/audit_multiscale_pipeline.py --dataset-dir data/processed/multiscale_temporal
python temporal_multiscale/comprehensive_submission_audit.py --dataset-dir data/processed/multiscale_temporal
python temporal_multiscale/checkpoint_deployment_audit.py --checkpoint models/best_multiscale_tcn_lb20_hz5_ts1.pth
python rigor/rigorous_validation.py --n-trials 50 --duration 600 --seed 42
```

## Testing Strategy
- There is no `pytest`, `tests/`, or configured CI test suite.
- Testing is a mix of module self-tests, audit scripts, reduced-epoch smoke runs, and full validation scripts.
- Treat `python temporal/validate_code.py` as the required gate before temporal training changes.
- When changing model logic, run the nearest downstream audit or validation script too.

## Running A Single Test
- Most `src/` modules expose a bottom-of-file self-test and can be run directly.

```bash
python src/eegnet.py
python src/controller.py
python src/preprocessing.py
python src/personalization.py
python src/simulator.py
python src/pac_computation.py
```

- Run one specific audit function from `temporal/validate_code.py` with `python -c`.

```bash
python -c "from temporal.validate_code import load_data, test_no_subject_leakage; splits = load_data('data/processed'); raise SystemExit(0 if test_no_subject_leakage(splits) else 1)"
python -c "from temporal.validate_code import load_data, test_temporal_sequence_logic; splits = load_data('data/processed'); raise SystemExit(0 if test_temporal_sequence_logic(splits, lookback=10, horizon=5) else 1)"
```

## Lightweight Lint And Syntax Checks
- No canonical formatter, linter, or type checker is configured.
- Default to syntax checks unless the user explicitly asks for a formatter/linter pass.

```bash
python -m py_compile src/training.py
python -m compileall src temporal temporal_multiscale rigor scripts
```

- If you use `ruff`, `black`, or `mypy`, keep scope narrow and avoid repo-wide churn.

## Validation Matrix
- Changed `src/eegnet.py`: run `python src/eegnet.py` and a reduced-epoch `src/training.py` smoke run.
- Changed `src/controller.py`: run `python src/controller.py` and, if relevant, a closed-loop validation script.
- Changed preprocessing or PAC logic: rebuild or at least spot-check processed data before retraining.
- Changed `temporal/` or `temporal_multiscale/`: run `python temporal/validate_code.py` and the relevant multiscale audit.
- Changed split logic: explicitly verify subject disjointness and temporal causality.

## Code Style
- Follow PEP 8 with 4-space indentation.
- Aim for readable line lengths; existing code is usually under 100 chars and occasionally near 120.
- Prefer simple, explicit NumPy/PyTorch code over abstraction-heavy frameworks.
- Keep functions focused and pipeline stages obvious.
- Match the surrounding file instead of forcing a repo-wide rewrite.

## Imports
- Order imports as: standard library, third-party, project-local.
- Use standard aliases: `numpy as np`, `pandas as pd`, `matplotlib.pyplot as plt`, `seaborn as sns`.
- Legacy `src/` modules often use `sys.path.insert(...)` when run as scripts; preserve that pattern if extending them.
- Newer `temporal_multiscale/`, `rigor/`, and some `scripts/` files prefer `Path(__file__).resolve()`-based root discovery.
- Use local imports only to avoid heavy optional dependencies or circular imports.

## Typing
- Add type hints to public functions, methods, and important helpers.
- In `src/`, matching existing `typing` imports like `Dict`, `List`, `Optional`, and `Tuple` is fine.
- In newer temporal and rigor modules, `from __future__ import annotations` plus built-in generics is the local preference.
- Use type hints to clarify array/tensor shapes and returns, not to add noise.

## Naming And Docstrings
- Use `snake_case` for modules, functions, variables, and CLI flags.
- Use `PascalCase` for classes and `UPPER_CASE` for constants.
- Preserve common repo abbreviations such as `pac`, `eeg`, `snr`, `fs`, and `r2`.
- Keep checkpoint and run names descriptive, e.g. `best_multiscale_tcn_lb20_hz5_ts1.pth`.
- Most modules begin with a multi-line module docstring; keep that style when modifying substantial files.
- Prefer good names and docstrings over inline comments; add comments only for non-obvious signal-processing or leakage-safety logic.

## Error Handling And Logging
- Use `assert` for internal invariants and shape checks in hot paths.
- Raise `ValueError` for invalid inputs or unsupported states.
- Raise `FileNotFoundError` for missing datasets, checkpoints, or artifacts.
- Audit scripts should return `bool` and raise `SystemExit(1)` from `main()` on failure.
- Use small epsilon guards for numerical stability instead of silent failures.
- In reusable modules, prefer `logging.getLogger(__name__)` or the existing `closed_loop_entrainment` logger.
- In one-shot audits and CLI scripts, `print()` output is normal.
- Preserve the repo's `[PASS]` / `[FAIL]` output style for audits.
- New CLI entry points should use `argparse` and keep defaults aligned with `config.yaml` or nearby scripts.

## ML Guardrails
- Never allow subject overlap across train, val, and test splits.
- Preserve causal indexing: future targets must occur strictly after the sequence end.
- Fit normalization statistics on train only, then reuse them for val, test, and inference.
- Keep checkpoints self-describing when possible by storing config, metadata, and scaler values.
- Use deterministic seeding for temporal experiments when touching training logic.
- Report persistence and Ridge baselines honestly; they are expected reference points in this repo.

## Data And Artifact Hygiene
- Never commit raw data, private data, credentials, or large generated artifacts.
- Write checkpoints to `models/`, reports to `results/`, and logs to `logs/`.
- Do not mix generated outputs into `src/`, `temporal/`, or `temporal_multiscale/`.
- If a change affects defaults or interfaces, update `README.md`, `config.yaml`, or the relevant docs.

## When Adding New Code
- Put active implementation in `src/`, `temporal_multiscale/`, `rigor/`, or `scripts/` as appropriate.
- Add a small self-test or audit hook when practical, especially for new `src/` modules.
- Reuse existing utilities and conventions before inventing new framework layers.
- Optimize for correctness, leakage safety, and reproducibility before novelty or speed.

## Commit And PR Expectations
- Follow Conventional Commit style: `feat:`, `fix:`, `docs:`, `chore:`.
- Keep commit subjects imperative and specific.
- When model behavior changes, include before/after metrics such as R^2, RMSE, alignment, or stimulation efficiency.
- Record the exact validation commands you ran.
