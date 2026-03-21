# Phase 12: Architecture Comparison Study - Research

**Researched:** 2026-03-20
**Domain:** ML model training, ablation study, multi-seed reproducibility on multiscale temporal EEG dataset
**Confidence:** HIGH (all findings verified directly against source code, dataset files, and live package tests)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| RSRCH-01 | Architecture comparison — train XGBoost + Transformer on existing multiscale dataset, produce comparison table across horizons 1-10s vs existing TCN/LSTM/Ridge/persistence | XGBoost 3.2.0 confirmed installed; Transformer prototype verified working; sweep_horizons.py is the extension point; existing persistence+Ridge+TCN sweep results at ts5 already exist at models/sweep_horizons_results.json; LSTM needs rerun on multiscale spectral dataset |
| RSRCH-02 | Ablation study — TCN with components removed (GroupNorm off, attention off, multi-scale off, single dilation) to quantify each component's contribution with before/after R² | All four ablation variants verified buildable via ModelConfig flags (pool_type="last_step", dilations=[1,1,1,1], custom no-norm block); no new architecture code needed for 3 of 4 variants; GroupNorm-off requires a small custom subclass |
| RSRCH-03 | Multi-seed reproducibility — 3-5 seeds per model, report mean ± std R² | train_multiscale_tcn.py already accepts --seed; 4ch TCN trains in ~88s; 5 seeds × 2 datasets = ~15min total; XGBoost and Ridge rerun per seed is trivial |
</phase_requirements>

---

## Summary

Phase 12 produces the ML rigor artifacts that directly address the CSEF Scientific Thought rubric (20/40 points): a full architecture comparison table, an ablation table, and multi-seed reproducibility results. All three deliverables operate on datasets that already exist on disk. The primary implementation work is writing new model adapter classes (XGBoostTemporalModel, SimpleLSTM, SimpleTransformer), extending sweep_horizons.py with a --models flag, and building a script that runs each ablation variant through the existing training loop.

The key technical fact established by this research: both the 4-channel (49 features, Muse proxy) and 7-channel (73 features, research-grade) multiscale datasets exist at data/processed/ and are fully built with all required splits. XGBoost 3.2.0 is installed and confirmed working. The existing training infrastructure (train_multiscale_tcn.py, sweep_horizons.py, SequenceDataset) handles the TCN and baselines. New architectures (LSTM, Transformer) need only a train function that accepts the same NPZ files — no dataset rebuilding required.

The existing sweep at models/sweep_horizons_results.json covers persistence, Ridge, and TCN at horizons 1,2,3,5,8,10 with target_smooth_window=5. Phase 12 produces the ts1 equivalents on the 4ch dataset (the fair comparison baseline), plus XGBoost and Transformer. The LSTM's existing result (Test R²=-0.050) used a different dataset format (raw EEG windows with spatial encoder, not the 73-feature spectral cache) and cannot be directly compared — it must be retrained on the multiscale spectral format.

**Primary recommendation:** Use the 4-channel dataset (data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/) as the primary comparison surface, with 7-channel reported as a supplementary gap table. Focus training budget on horizons 1,3,5,8,10 (not all 10) to stay within time budget.

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| xgboost | 3.2.0 (installed) | Tabular temporal baseline | Industry-standard GBDT; handles flattened (N, T*F) input natively; interpretable feature importances; trains in <2s on this dataset |
| PyTorch | 2.7.1 (installed) | LSTM and Transformer training | Already project dependency; all training infrastructure in use |
| scikit-learn | installed | Ridge baseline, metrics | Already used in sweep_horizons.py; Ridge is a required comparison model |
| numpy | installed | Array manipulation, metrics | Already project dependency |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytorch-forecasting | NOT installed | Temporal Fusion Transformer | Do NOT use — lightning not installed, dependency chain untested; use custom lightweight Transformer instead |
| lightning | NOT installed | pytorch-forecasting dependency | Absent from venv — confirmed by direct test |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom Transformer (~70K params) | pytorch-forecasting TFT | TFT requires lightning not present; custom is faster, more defensible to judges as "designed for this task", avoids dependency conflicts |
| Reusing existing temporal/temporal_model.py LSTM | New SimpleLSTM on multiscale features | Existing LSTM used raw EEG windows + spatial encoder; can't fairly compare — must retrain on same 49/73-feature spectral input |

**Installation:**
```bash
# XGBoost already installed (3.2.0)
# No new dependencies needed — all other models use PyTorch already in venv
pip install xgboost  # if fresh env
```

---

## Architecture Patterns

### Recommended Project Structure
```
temporal_multiscale/
├── model_registry.py          # Existing — add XGBoostTemporalModel, TransformerTemporalModel
├── comparison_models.py       # NEW — SimpleLSTM, SimpleTransformer, XGBoostWrapper for training
├── run_comparison_study.py    # NEW — full comparison sweep (all models, all horizons, both datasets)
├── run_ablation_study.py      # NEW — TCN ablation (4 variants, 3-5 seeds each)
├── run_multiseed_study.py     # NEW — or fold into run_comparison_study.py with --n-seeds flag
results/
├── comparison_table_4ch.json  # Primary output
├── comparison_table_7ch.json  # Secondary output (7ch gap)
├── ablation_table.json        # Ablation results
├── multiseed_summary.json     # Mean ± std R² per model
```

### Pattern 1: XGBoost Flattening
**What:** XGBoost cannot handle 3D sequences natively. Flatten (N, T, F) → (N, T*F) before fitting.
**When to use:** All XGBoost training and evaluation calls.
**Example:**
```python
# Source: verified directly against sweep_horizons.py ridge_baseline() pattern
x_train = train["x_seq"].astype(np.float64)  # (N, T, F)
x_train_flat = x_train.reshape(x_train.shape[0], -1)  # (N, T*F)
model = xgb.XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    n_jobs=-1,
    verbosity=0,
    random_state=seed,
)
model.fit(x_train_flat, y_train)
```
**Verified:** XGBoost trains in 1.1s on 4ch (11160 samples, 980 features) and 1.7s on 7ch (1460 features). Test R² at horizon 5: 4ch=0.0415, 7ch=0.0671 with n_estimators=200.

### Pattern 2: Lightweight Causal Transformer
**What:** Custom TransformerEncoder with causal mask applied to the sequence dimension. No positional encoding needed — time order is implicit in EEG sequence structure.
**When to use:** Single architecture, not pytorch-forecasting.
**Example:**
```python
# Source: verified by running prototype — output shape confirmed correct
class SimpleTransformer(nn.Module):
    def __init__(self, n_features: int, d_model: int = 64, nhead: int = 4,
                 num_layers: int = 2, dropout: float = 0.1) -> None:
        super().__init__()
        self.proj = nn.Linear(n_features, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=d_model * 2, dropout=dropout, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=num_layers)
        self.head = nn.Linear(d_model, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F) — causal mask enforces left-only attention
        T = x.shape[1]
        mask = torch.triu(torch.ones(T, T, device=x.device), diagonal=1).bool()
        x = self.proj(x)
        x = self.encoder(x, mask=mask)
        return self.head(x[:, -1]).squeeze(-1)
```
**Parameter count:** ~70,209 (4ch, 49 features). Comparable to LSTM (~62,785).

### Pattern 3: TCN Ablation via ModelConfig
**What:** All four ablation variants are achievable by modifying ModelConfig fields or replacing the norm layer in CausalDSConvBlock. Three variants need no new code.
**When to use:** All ablation experiments.

| Variant | ModelConfig Change | New Code? |
|---------|-------------------|-----------|
| Full TCN (baseline) | `dilations=[1,2,4,8], pool_type="attention"` | No |
| No attention | `pool_type="last_step"` | No |
| Single dilation | `dilations=[1,1,1,1]` | No — same param count, no exponential receptive field |
| Multi-scale off (single block) | `dilations=[1]` | No |
| No GroupNorm | Subclass CausalDSConvBlock, set `self.norm = nn.Identity()` | Yes — ~5 lines |

**Note on GroupNorm ablation:** GroupNorm(1, C) is applied inside CausalDSConvBlock. To ablate it, create `CausalDSConvBlockNoNorm` that sets `self.norm = nn.Identity()` and otherwise is identical. Then add a `use_norm: bool = True` flag to ModelConfig and CausalDSConvBlock. Alternatively, post-hoc patch: load model, replace all GroupNorm layers with Identity before training. The clean approach is the flag.

### Pattern 4: Multi-Seed Wrapper
**What:** Run train_multiscale_tcn.py (or equivalent) N times with different seeds, collect test R² and RMSE, compute mean ± std.
**When to use:** TCN, XGBoost (and optionally LSTM/Transformer) multi-seed evaluation.
**Example:**
```python
# Source: pattern from train_multiscale_tcn.py seeding block
import subprocess, json
SEEDS = [42, 123, 456, 789, 1337]
results = []
for seed in SEEDS:
    run_name = f"tcn_4ch_seed{seed}"
    subprocess.check_call([
        "python", "temporal_multiscale/train_multiscale_tcn.py",
        "--dataset-dir", "data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1",
        "--models-dir", "models/multiseed",
        "--run-name", run_name,
        "--seed", str(seed),
        "--allow-metadata-mismatch",
    ])
    s = json.loads(Path(f"models/multiseed/summary_{run_name}.json").read_text())
    results.append(s["test_future_metrics"]["r2"])
import numpy as np
print(f"TCN 4ch: R² = {np.mean(results):.4f} ± {np.std(results):.4f}")
```
**Estimated runtime:** 88s × 5 seeds = ~7 min for 4ch TCN. 7ch similar. Total for all models: ~45 min.

### Pattern 5: SimpleLSTM for Fair Comparison
**What:** A two-layer LSTM operating on the same (N, T, F) spectral feature input as the TCN. No spatial encoder — that was the superseded `temporal/temporal_model.py` approach.
**Example:**
```python
class SimpleLSTM(nn.Module):
    def __init__(self, n_features: int, hidden: int = 64, num_layers: int = 2,
                 dropout: float = 0.1) -> None:
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden, num_layers=num_layers,
                           batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.norm = nn.LayerNorm(hidden)
        self.head = nn.Sequential(nn.Linear(hidden, hidden), nn.SiLU(),
                                  nn.Dropout(dropout), nn.Linear(hidden, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, T, F)
        out, _ = self.lstm(x)
        z = self.norm(out[:, -1])  # last timestep
        return self.head(z).squeeze(-1)
```
**Parameter count:** ~62,785 (hidden=64, 2 layers, 49 features). Comparable to Transformer.

### Anti-Patterns to Avoid
- **Using the old temporal/temporal_model.py LSTM results directly:** That LSTM took raw (7, 500) EEG windows as input with a separate spatial encoder — fundamentally different input than the 49-feature spectral vectors. Never put Test R²=-0.050 in the comparison table without noting the different input format.
- **Rebuilding the multiscale dataset for each ablation:** The dataset is already built. Only rebuild if changing lookback, horizon, or target_smooth_window. Pass `--allow-metadata-mismatch` when reusing existing datasets.
- **Setting target_smooth_window=5 for the primary comparison table:** The published results and 4ch checkpoint use ts1 (raw PAC targets). The existing sweep_horizons_results.json was generated with ts5. The primary comparison table must be on ts1 to match the paper. Run new sweep at ts1 on the 4ch dataset.
- **Using pytorch-forecasting or lightning:** Neither is installed. Do not add them. Custom Transformer is the right answer.
- **Reporting only val R² instead of test R²:** The planner must ensure all scripts save and report test R² as the final metric. Val R² is only for model selection.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| XGBoost regression | sklearn GBM or manual boosting | xgboost.XGBRegressor | XGB 3.2.0 already installed; GPU support; native feature importance; 1.1s training |
| Sequence metrics (R², RMSE, MAE) | New metric functions | Copy _r2(), _rmse(), _metrics() from sweep_horizons.py | Already tested; consistent with all existing results in models/ |
| Dataset loading | New NPZ loader | SequenceDataset from train_multiscale_tcn.py | Handles normalization, split keys correctly |
| Seeding for reproducibility | Manual seeding | Copy seeding block from train_multiscale_tcn.py lines 213-218 | Already covers random, numpy, torch, cuda — do not skip torch.backends.cudnn.deterministic = True |

**Key insight:** The entire training infrastructure (SequenceDataset, evaluate(), _r2(), _metrics(), checkpointing pattern) already exists in train_multiscale_tcn.py. New model architectures need only conform to the same input/output signature: take (B, T, F) tensors, return a scalar prediction per sample.

---

## Common Pitfalls

### Pitfall 1: ts5 vs ts1 Comparison Surface
**What goes wrong:** Mixing results from target_smooth_window=5 (which inflates R² to 0.24-0.28 for TCN) with results from target_smooth_window=1 (where TCN gets R²=0.156-0.170). The existing sweep_horizons_results.json uses ts5.
**Why it happens:** The horizon sweep script defaults to `--target-smooth-window 5`. The paper and 4ch checkpoint use ts1.
**How to avoid:** Run all Phase 12 comparisons on ts1. The 4ch and 7ch multiscale ts1 datasets already exist. Pass `--target-smooth-window 1 --allow-metadata-mismatch` explicitly to all scripts.
**Warning signs:** If XGBoost or LSTM suddenly shows R²>0.3, you're likely on ts5.

### Pitfall 2: Subject Leakage in Multi-Seed Runs
**What goes wrong:** Running `build_multiscale_dataset.py` with a different seed changes subject assignments to train/val/test — different seeds should NOT rebuild the dataset. Seeds should only control model weight initialization and training data shuffle order.
**Why it happens:** Confusing "random seed" with "data split seed."
**How to avoid:** Never rebuild the dataset between seeds. Use the same pre-built NPZ files for all seeds. The seeding only applies to `torch.manual_seed()`, `numpy.random.seed()`, and the DataLoader generator.

### Pitfall 3: XGBoost Feature Dimensionality Explosion
**What goes wrong:** At lookback=20, the flattened feature dimension is 20×49=980 (4ch) or 20×73=1460 (7ch). With n_estimators=500+, XGBoost can overfit the training set while performing poorly on held-out subjects.
**Why it happens:** XGBoost sees 980-1460 features but only ~11K training samples — the ratio is manageable but sensitive to max_depth and learning_rate.
**How to avoid:** Use max_depth=4 or 6, learning_rate≤0.1, subsample=0.8, colsample_bytree=0.8. Verified: n_estimators=200 gives Test R²=0.042 (4ch) and 0.067 (7ch) at horizon 5. Use early_stopping_rounds with the val set for production runs.
**Warning signs:** Train R²>0.8 while test R²<0.05 indicates overfitting.

### Pitfall 4: Transformer Training Instability
**What goes wrong:** Transformer with causal mask can have gradient issues at the start of training, especially with small batch sizes.
**Why it happens:** Attention weights collapse to uniform or near-zero when keys/queries are untrained.
**How to avoid:** Use learning_rate=1e-4 (slower than TCN's 1e-3), warmup for first 5 epochs (or just ReduceLROnPlateau starting from epoch 1). Gradient clipping (max_norm=1.0) is critical. d_model=64 is sufficient — don't go larger.

### Pitfall 5: Conflating LSTM Architectures
**What goes wrong:** Referencing `temporal/summary_temporal_lstm.json` (Test R²=-0.050) in the comparison table without noting it used raw EEG windows, not spectral features. Judges will notice the massive performance gap and question methodology.
**Why it happens:** There are two LSTM experiments in the repo with the same horizon (5s) but completely different inputs.
**How to avoid:** Discard the old LSTM result entirely for the table. Retrain a SimpleLSTM on the multiscale spectral feature dataset. The new result is the one that goes in the table.

---

## Code Examples

Verified patterns from direct source inspection:

### Loading Existing Pre-Built Dataset
```python
# Source: train_multiscale_tcn.py SequenceDataset
import numpy as np
import torch
from torch.utils.data import Dataset

class SequenceDataset(Dataset):
    def __init__(self, npz_path: Path) -> None:
        d = np.load(npz_path, allow_pickle=True)
        self.x = torch.from_numpy(d["x_seq"]).float()        # (N, T, F) already normalized
        self.y_future = torch.from_numpy(d["y_future_norm"]).float()  # normalized target
        self.y_delta = torch.from_numpy(d["y_delta_norm"]).float()
        self.last_pac = torch.from_numpy(d["last_pac"]).float()       # raw PAC for denormalization

    def __len__(self) -> int:
        return self.x.shape[0]

    def __getitem__(self, i: int) -> dict:
        return {
            "x_seq": self.x[i],
            "y_future": self.y_future[i],
            "y_delta": self.y_delta[i],
            "last_pac": self.last_pac[i],
        }
```

### Deterministic Seeding (Must Include All Four Lines)
```python
# Source: train_multiscale_tcn.py lines 213-218
import random, numpy as np, torch

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### Metrics (Already in sweep_horizons.py — Copy Verbatim)
```python
# Source: sweep_horizons.py
def _r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - ss_res / (ss_tot + 1e-12))

def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
```

### Adding a New Model to the Registry (Pattern from model_registry.py)
```python
# Source: model_registry.py — XGBoostTemporalModel must satisfy TemporalModel Protocol
class XGBoostTemporalModel:
    """Wraps a fitted XGBRegressor for rolling real-time inference."""

    def __init__(self, checkpoint_path: str, scalers_path: str) -> None:
        import joblib
        self._model = joblib.load(checkpoint_path)
        sc = np.load(scalers_path)
        self._feat_mean = sc["feature_mean"]
        self._feat_std = sc["feature_std"]
        self._yf_mean = float(sc["y_future_mean"])
        self._yf_std = float(sc["y_future_std"])
        self._buffer: list = []
        self._lookback = 20  # must match dataset lookback

    def step(self, spectral_features, pac_current, stim_state,
             time_since_switch_sec, stim_frac_recent) -> dict | None:
        # Build feature vector, accumulate buffer, predict when full
        ...

    def reset(self) -> None:
        self._buffer.clear()
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| LSTM on raw EEG windows (SpatialEncoder + LSTM, 187K params) | TCN on pre-computed 49/73-feature spectral vectors | Phase 2→3 (temporal_multiscale/) | Dramatically lower compute, leakage-safe, R² from -0.05 to 0.15-0.27 |
| target_smooth_window=5 (smoothed PAC) | target_smooth_window=1 (raw PAC, Muse-comparable) | Phase 10 retraining | Honest ceiling for consumer hardware: R² 0.27→0.15; meaningful for CSEF because it's the real-world target |
| 7-channel research-grade dataset only | 4-channel Muse-proxy dataset (primary) + 7ch (supplementary) | Phase 10 | Validates system on consumer-realistic channel count |

**Deprecated/outdated:**
- `temporal/temporal_model.py` LSTM: raw EEG window input with SpatialEncoder — not comparable to spectral feature pipeline. Do not cite its R²=-0.050 in comparison table without full input format disclosure.
- `models/gradient_boosting_v5.pkl`: Old GBM from an earlier static prediction phase — these are EEGNet static predictors, not temporal predictors. Do not compare against them.

---

## Key Numbers for Planning

The planner needs these concrete facts:

**Datasets (confirmed from disk):**
- 4ch: data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/ — 49 features, 11160 train / 2605 val / 2678 test
- 7ch: data/processed/multiscale_temporal_lb20_hz5_ts1/ — 73 features, same split sizes
- Both datasets: lookback=20, horizon=5, ts1 — already built, do NOT rebuild

**Existing results (no retraining needed):**
- TCN 4ch (seed=42): Val R²=0.447, Test R²=0.156, RMSE=3.76e-5 (88s training)
- TCN 7ch (seed=42, ts1): Val R²=0.411, Test R²=0.170, RMSE=3.31e-5
- Persistence+Ridge+TCN ts5 sweep: models/sweep_horizons_results.json (horizons 1,2,3,5,8,10)

**XGBoost baseline (verified live):**
- 4ch horizon=5, ts1: Test R²=0.042, ~1.1s training
- 7ch horizon=5, ts1: Test R²=0.067, ~1.7s training
- Input: flatten (N, 20, 49) → (N, 980) for 4ch

**TCN ablation variants (all buildable now):**
- Full TCN: ModelConfig(dilations=[1,2,4,8], pool_type="attention") — baseline
- No attention: ModelConfig(dilations=[1,2,4,8], pool_type="last_step") — 29,442 params
- Single dilation: ModelConfig(dilations=[1,1,1,1], pool_type="attention") — 29,507 params
- No multi-scale (1 block): ModelConfig(dilations=[1], pool_type="attention") — 16,259 params
- No GroupNorm: requires ~5-line subclass replacing norm with nn.Identity()

**Training time estimates (on MPS/CPU):**
- TCN 4ch 1 seed: ~88s (observed); 5 seeds = ~7 min
- TCN 7ch 1 seed: ~same; 5 seeds = ~7 min
- XGBoost all seeds: <10s total (trivially fast)
- LSTM 1 seed: ~same as TCN (similar param count, same training loop)
- Transformer 1 seed: ~same as TCN
- Ablation (4 variants × 1 seed): ~6 min
- Total Phase 12 training budget: ~45 min conservatively

**Comparison horizons:** Use 1,3,5,8,10 (skip 2 to save time — captures the key inflection at 3s where TCN starts winning).

---

## Open Questions

1. **Should XGBoost use the normalized x_seq or raw x_seq as input?**
   - What we know: The NPZ files contain both `x_seq` (already normalized by train stats) and the raw values are reconstructable from scalers.npz. Ridge in sweep_horizons.py uses `x_seq` directly (already normalized). XGBoost is invariant to feature scaling — using normalized or raw produces the same R².
   - Recommendation: Use `x_seq` as-is (already normalized). Simpler, consistent with Ridge baseline.

2. **How many seeds for XGBoost and LSTM, vs TCN-only?**
   - What we know: RSRCH-03 says "3-5 seeds per model" but in context of TCN being the primary. XGBoost multi-seed adds minimal insight (tree ensemble already averages stochasticity).
   - Recommendation: 5 seeds for TCN (the primary claim). 3 seeds for LSTM and Transformer (shows LSTM variance). XGBoost: report single run with random_state=42, note it's deterministic given same data.

3. **Do the ablation variants need multi-seed or single seed?**
   - What we know: Ablation purpose is to quantify component contribution, not reproducibility. Single seed (42) is standard for ablations.
   - Recommendation: Single seed for all ablation variants. Report R² delta vs full TCN.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | No pytest configured — module self-tests and audit scripts |
| Config file | None |
| Quick run command | `python -m py_compile temporal_multiscale/comparison_models.py` |
| Full suite command | `python temporal_multiscale/run_comparison_study.py --dry-run` (to be created) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| RSRCH-01 | XGBoost trains and produces R²/RMSE for all horizons | smoke | `python -c "import xgboost; print('OK')"` | ✅ (xgboost installed) |
| RSRCH-01 | Comparison table JSON saved to results/ | integration | `python temporal_multiscale/run_comparison_study.py --horizons 5 --models xgboost,persistence,ridge` | ❌ Wave 0 |
| RSRCH-01 | Transformer produces valid outputs (not NaN) | unit | `python -c "from temporal_multiscale.comparison_models import SimpleTransformer; import torch; m=SimpleTransformer(49); x=torch.randn(4,20,49); print(m(x).shape)"` | ❌ Wave 0 |
| RSRCH-02 | All 4 ablation variants train without error | integration | `python temporal_multiscale/run_ablation_study.py --epochs 3 --dry-run` | ❌ Wave 0 |
| RSRCH-02 | Ablation table JSON saved with 4 rows | integration | `python temporal_multiscale/run_ablation_study.py --output results/ablation_table.json` | ❌ Wave 0 |
| RSRCH-03 | 5-seed TCN results: mean ± std computed | integration | `python temporal_multiscale/run_multiseed_study.py --model tcn --n-seeds 5` | ❌ Wave 0 |
| RSRCH-03 | No dataset rebuild between seeds (subject disjointness preserved) | audit | `python temporal/validate_code.py` | ✅ (existing audit) |

### Sampling Rate
- **Per task commit:** `python -m py_compile temporal_multiscale/comparison_models.py temporal_multiscale/run_comparison_study.py`
- **Per wave merge:** Full run of run_comparison_study.py with --horizons 5 --models all
- **Phase gate:** All three output JSONs (comparison_table_4ch.json, ablation_table.json, multiseed_summary.json) present and non-empty before moving to Phase 13

### Wave 0 Gaps
- [ ] `temporal_multiscale/comparison_models.py` — SimpleLSTM, SimpleTransformer, XGBoostWrapper classes — covers RSRCH-01
- [ ] `temporal_multiscale/run_comparison_study.py` — orchestrator for all models × all horizons — covers RSRCH-01
- [ ] `temporal_multiscale/run_ablation_study.py` — TCN variant training loop — covers RSRCH-02
- [ ] `temporal_multiscale/run_multiseed_study.py` — or fold into run_comparison_study.py — covers RSRCH-03
- [ ] `results/` directory (with .gitkeep if empty)

---

## Sources

### Primary (HIGH confidence)
- Direct source inspection: `temporal_multiscale/multiscale_tcn.py` — ModelConfig, CausalDSConvBlock, AttentionPool1D, ModelConfig.pool_type, all ablation variants verified buildable
- Direct source inspection: `temporal_multiscale/train_multiscale_tcn.py` — SequenceDataset, training loop, seeding block, checkpoint format, --seed CLI arg
- Direct source inspection: `temporal_multiscale/sweep_horizons.py` — persistence_baseline(), ridge_baseline(), _r2(), _rmse(), existing results format
- Direct source inspection: `temporal_multiscale/model_registry.py` — TemporalModel Protocol, registration pattern for XGBoostTemporalModel
- Direct source inspection: `models/sweep_horizons_results.json` — existing ts5 R²/RMSE at horizons 1,2,3,5,8,10
- Direct source inspection: `models/summary_temporal_lstm.json` — old LSTM: Test R²=-0.050 at horizon 5 (different input format, not usable in table)
- Direct source inspection: `models/muse_4ch/summary_multiscale_tcn_4ch_lb20_hz5_ts1.json` — 4ch TCN baseline: Test R²=0.156
- Direct source inspection: `data/processed/muse_4ch/multiscale_temporal_lb20_hz5_ts1/metadata.json` — 49 features, 11160/2605/2678 split
- Direct source inspection: `data/processed/multiscale_temporal_lb20_hz5_ts1/metadata.json` — 73 features, same splits
- Live test: `pip show xgboost` — version 3.2.0 installed, confirmed working with fit/predict
- Live test: XGBoost on 4ch dataset — 1.1s training, Test R²=0.042 at horizon 5, ts1
- Live test: XGBoost on 7ch dataset — 1.7s training, Test R²=0.067 at horizon 5, ts1
- Live test: SimpleTransformer prototype — 70,209 params, correct output shape (B,)
- Live test: TCN ablation variants (no-attn=29,442 params, single-dil=29,507, single-block=16,259) — all forward pass verified
- Live test: `pip show lightning` — NOT installed; `pip show pytorch-forecasting` — NOT installed

### Secondary (MEDIUM confidence)
- `.planning/research/SUMMARY.md` — confirms pytorch-forecasting dependency concern, xgboost as right choice, custom Transformer recommendation

### Tertiary (LOW confidence)
- None

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — XGBoost version confirmed, torch version confirmed, missing packages confirmed absent via direct pip test
- Architecture: HIGH — all model variants forward-pass verified live; ablation buildability confirmed by running ModelConfig variants
- Pitfalls: HIGH — ts5/ts1 mismatch verified by comparing existing sweep results against paper numbers; XGBoost R² numbers measured empirically
- Training time estimates: HIGH — 4ch TCN time taken from summary JSON (88.8s); XGBoost time measured live (1.1-1.7s)

**Research date:** 2026-03-20
**Valid until:** 2026-04-09 (CSEF deadline — dataset and package state stable; XGBoost 3.2.0 API stable)
