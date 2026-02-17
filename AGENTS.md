# Repository Guidelines

## Project Structure & Module Organization
Core training and inference code lives in `src/` (data loading, preprocessing, feature extraction, models, training, validation). Temporal forecasting experiments live in `temporal/` (LSTM/GRU and sklearn baselines). Keep raw data in `data/raw/`, generated windows in `data/processed/`, trained artifacts in `models/`, and outputs in `results/` and `logs/`. Reference material and writeups belong in `docs/`; legacy experiments are in `archive/`.

## Build, Test, and Development Commands
Use Python 3.10+ in a virtual environment.

```bash
pip install -r requirements.txt
python src/data_loader.py --bids_root data/raw/ds005048 --output data/processed
python src/training.py --data_dir data/processed --output_dir models --epochs 100 --batch_size 64 --device cuda
python src/validation.py --output_dir results --duration 360 --n_trials 3
python temporal/validate_code.py
python temporal/train_temporal.py --data-dir data/processed --save-dir models
```

`validate_code.py` is the main pre-training audit for temporal workflows (sequence integrity, leakage checks, baseline quality).

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation and readable type hints where practical. Use `snake_case` for functions/variables, `PascalCase` for classes, and lowercase module names (for example, `spectral_features.py`). Prefer small, testable functions and keep CLI entry points under `if __name__ == "__main__":`.

## Testing Guidelines
There is no dedicated `tests/` package yet. Treat `python temporal/validate_code.py` as a required gate before temporal model training. For `src/` changes, run at least one end-to-end smoke path: data loading -> training -> validation with a reduced epoch count. When adding model logic, include or update lightweight `test_*` helper functions near the module and document expected metrics deltas in PR notes.

## Commit & Pull Request Guidelines
Recent history follows Conventional Commit style: `feat:`, `fix:`, `docs:`, `chore:`. Keep subjects imperative and specific (for example, `fix: prevent subject leakage in temporal split builder`).

PRs should include:
- clear problem/solution summary,
- linked issue or experiment note,
- exact commands run for validation,
- before/after metrics (R², RMSE, stimulation efficiency) when behavior changes,
- updated docs/config (`README.md`, `config.yaml`) if interfaces change.

## Configuration & Data Hygiene
Primary runtime settings are in `config.yaml`. Do not commit private datasets or credentials. Keep large generated artifacts in designated output directories and avoid mixing them into source folders.
