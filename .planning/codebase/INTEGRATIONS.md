# External Integrations

**Analysis Date:** 2026-02-26

## APIs & External Services

**Data Access:**
- OpenNeuro (OpenNeuro ds005048) - Clinical EEG dataset source
  - Download: https://openneuro.org/datasets/ds005048/versions/1.0.1
  - Format: BIDS-compliant (EEG .set files + accompanying .fdt binary data + event TSV)
  - Integration: `mne-bids` library handles dataset discovery and loading
  - Access: Via direct HTTP download (manual pre-staging to `data/raw/ds005048/`)

**No active API integrations detected:**
- No REST API clients (requests, httpx, aiohttp not in requirements)
- No cloud service SDKs (boto3, azure, gcp not in requirements)
- No webhook handlers or incoming API endpoints
- System is research/offline-first (no live service integrations)

## Data Storage

**Databases:**
- None - This is a single-machine research pipeline
- No persistent database backend (PostgreSQL, MongoDB, etc.)

**File Storage:**
- Local filesystem only
  - Raw data: `data/raw/ds005048/` (OpenNeuro ds005048 BIDS structure)
  - Processed windows: `data/processed/` (train/val/test split `.npz` files)
    - Format: NumPy zipped archives (`.npz`) containing preprocessed EEG + PAC labels
    - Files: `train_data.npz`, `val_data.npz`, `test_data.npz`
  - Temporal dataset: `data/processed/multiscale_temporal_lb20_hz1_ts5_clean/` (multiscale causal sequences)
  - Checkpoint storage: `models/` directory
    - Format: PyTorch state dicts (`.pth` files)
    - Metadata: Training history in `.json` format

**Caching:**
- None - No distributed cache (Redis, Memcached)
- In-memory caching via NumPy/PyTorch during training/inference

## Authentication & Identity

**Auth Provider:**
- None - Fully offline system
- No user authentication or authorization
- OpenNeuro dataset accessed via public HTTP download (no credentials required)

## Monitoring & Observability

**Error Tracking:**
- None - No external error tracking service
- Local logging to `logs/experiment.log` via Python logging module
  - Configured in `config.yaml` (level: INFO)
  - Console output optional (enabled by default)

**Logs:**
- Local file-based only
  - Location: `logs/experiment.log`
  - Format: Standard Python logging format (timestamp, logger name, level, message)
  - Captured during training, validation, closed-loop simulation, and audits

**Metrics/Monitoring:**
- No external monitoring (no Prometheus, CloudWatch, DataDog)
- Results saved locally to JSON files:
  - `results/closed_loop_demo_results.json` - Demo simulation outputs
  - `results/fatigue_analysis.json` - Fatigue sensitivity analysis
  - `results/fatigue_sensitivity.json` - Fatigue parameter sweep results
- Results/figures: `results/figures/` (PNG format, 300 DPI per config)

## CI/CD & Deployment

**Hosting:**
- Single-machine research deployment
- No cloud hosting (AWS, Azure, GCP)
- Designed for local NVIDIA GPU execution (CUDA 11.8)

**CI Pipeline:**
- None detected
- No GitHub Actions, GitLab CI, CircleCI config
- No automated testing infrastructure

**Deployment:**
- Manual: Clone repo, create venv, `pip install -r requirements.txt`
- No containerization (no Docker/Kubernetes)
- No deployment orchestration

## Environment Configuration

**Required env vars:**
- None - System uses `config.yaml` for all runtime configuration
- All parameters (channels, filters, model hyperparameters, controller thresholds) centralized in `config.yaml`
- No external environment variables required for core pipeline
- GPU selection: Configured in `config.yaml` (`resources.device`, `resources.gpu_id`)

**Secrets location:**
- No secrets managed - Research dataset is public (OpenNeuro)
- No API keys, tokens, or credentials in codebase
- All data paths specified in `config.yaml`

## Webhooks & Callbacks

**Incoming:**
- None - No webhook endpoints
- Closed-loop system is self-contained; no external trigger hooks

**Outgoing:**
- None - No webhooks sent to external services
- System generates local result files only

## Data Exchange Formats

**Input:**
- BIDS-formatted EEG:
  - `.set` files (MATLAB v7.3 HDF5 containers) - Loaded via `h5py` and `mne`
  - `.fdt` files (companion binary data, float32, Fortran/column-major order)
  - `events.tsv` - BIDS event timings (stimulus ON/OFF markers)

**Output:**
- `.npz` (NumPy zipped arrays) - Processed window datasets with PAC labels
- `.pth` (PyTorch state dicts) - Model checkpoints
- `.json` (JSON) - Training metrics, simulation results, metadata
- `.png` (PNG) - Figure exports (300 DPI, `results/figures/`)
- `.log` (plain text) - Experiment logs

## Real-time & Streaming

**Real-time Inference:**
- Module: `temporal_multiscale/realtime_inference.py`
- Class: `RealtimePACForecaster`
- Pattern: Rolling window causal inference on 2-second EEG segments
- Update rate: 1 Hz (decisions at 1 per second)
- Window latency: 2 seconds (full window required before inference)

**Simulation Loop:**
- `src/simulator.py` - Runs synthetic brain dynamics at 1 Hz decision rate
- Tracks PAC state and stimulation history
- Supports fatigue model integration for habituation effects

---

*Integration audit: 2026-02-26*
