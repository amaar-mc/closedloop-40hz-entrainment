# Scripts

Run scripts from the repository root with the project virtual environment active.

## Layout

- `pipeline/`: end-to-end validation, replay, and simulation entrypoints.
- `figures/`: publication figure generators.
- `audit/`: leakage and integrity checks.
- `tools/`: supporting generators and one-off utilities.
- `notebook/`: research-notebook generation utilities.
- `setup/`: setup helpers.

CSEF-specific generators remain in `tools/` for reproducibility, but their outputs now resolve to
the archived `submission/` package.
