# Results Directory

This directory contains validated outputs and their supporting audit bundles.

## Canonical Layout

- `RESULTS_REPORT.md`: consolidated human-readable results report.
- `metrics/`: machine-readable JSON metrics produced by validation and analysis scripts.
- `figures/`: generated publication figures.
- `reports/`: focused technical reports that supplement the consolidated report.
- `rigor_audit/`: self-contained CSEF audit bundle. Its scripts and outputs stay together so the
  completed audit remains reproducible.
- `tribe_v2/`: outputs for the Muse/TRIBE V2 subsystem.

Run scripts from the repository root so relative output paths resolve consistently.
