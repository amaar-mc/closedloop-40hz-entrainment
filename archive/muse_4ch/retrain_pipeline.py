"""
4-Channel Muse 2 Model Retraining Pipeline

Retrains the full EEGNet + TCN pipeline on 4 channels (F7, F8, T7, T8)
that approximate the Muse 2 electrode positions (AF7, AF8, TP9, TP10).

This script does NOT modify any existing code or models. It:
1. Monkey-patches the channel selection in BIDSDataProcessor
2. Processes raw BIDS data → data/processed/muse_4ch/
3. Generates spectral feature caches (37 features per window)
4. Builds the multiscale temporal dataset (49 features per timestep)
5. Trains EEGNet (4-channel input)
6. Trains MultiscaleCausalTCN
7. Evaluates both models and generates a comparison report

Usage:
    python muse_4ch/retrain_pipeline.py [--skip-data] [--skip-eegnet] [--skip-tcn]

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

# ---------------------------------------------------------------------------
# Project root discovery and path setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "archive" / "experimental_models"))
sys.path.insert(0, str(PROJECT_ROOT / "temporal_multiscale"))
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MUSE_PROXY_CHANNELS = ["F7", "F8", "T7", "T8"]
N_CHANNELS = len(MUSE_PROXY_CHANNELS)
N_SAMPLES = 500  # 2s @ 250 Hz
SAMPLING_RATE = 250.0

BIDS_ROOT = PROJECT_ROOT / "data" / "raw" / "ds005048"
OUTPUT_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "muse_4ch"
OUTPUT_MODEL_DIR = PROJECT_ROOT / "models" / "muse_4ch"
MULTISCALE_DIR = OUTPUT_DATA_DIR / "multiscale_temporal_lb20_hz5_ts1"

# TCN hyperparams (match 7-channel pipeline)
LOOKBACK = 20
HORIZON = 5
TARGET_SMOOTH_WINDOW = 1

# Training hyperparams
EEGNET_EPOCHS = 100
EEGNET_BATCH_SIZE = 64
EEGNET_LR = 0.001
TCN_EPOCHS = 100
TCN_BATCH_SIZE = 64
TCN_LR = 0.001
SEED = 42

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("muse_4ch")


# ===================================================================
# STEP 1: Process raw BIDS data with 4 channels
# ===================================================================
def step1_process_data() -> None:
    """Load raw BIDS data, select F7/F8/T7/T8, preprocess, window, compute PAC."""
    from data_loader import BIDSDataProcessor

    logger.info("=" * 70)
    logger.info("STEP 1: Processing raw BIDS data with 4 channels")
    logger.info(f"  Channels: {MUSE_PROXY_CHANNELS}")
    logger.info(f"  Input:  {BIDS_ROOT}")
    logger.info(f"  Output: {OUTPUT_DATA_DIR}")
    logger.info("=" * 70)

    # Override the channel selection — this is the KEY change
    BIDSDataProcessor.FRONTAL_CHANNELS = MUSE_PROXY_CHANNELS

    processor = BIDSDataProcessor(
        bids_root=str(BIDS_ROOT),
        output_dir=str(OUTPUT_DATA_DIR),
        window_sec=2.0,
        hop_sec=1.0,
        fs=SAMPLING_RATE,
    )

    # Process dataset: load, preprocess, window, compute PAC
    windows, pac_labels, subject_ids, session_ids = processor.process_dataset()
    logger.info(f"  Processed: {windows.shape[0]} windows, "
                f"{len(np.unique(subject_ids))} subjects")

    # Create subject-level train/val/test splits and save
    splits = processor.create_splits(windows, pac_labels, subject_ids)
    processor.save_splits(splits)

    # Verify output shapes
    for split in ["train", "val", "test"]:
        npz = np.load(OUTPUT_DATA_DIR / f"{split}_data.npz")
        w = npz["windows"]
        p = npz["pac"]
        s = npz["subjects"]
        logger.info(f"  {split}: windows={w.shape}, pac={p.shape}, "
                     f"subjects={len(np.unique(s))}")
        assert w.shape[1] == 1, f"Expected 1 feature channel dim, got {w.shape[1]}"
        assert w.shape[2] == N_CHANNELS, (
            f"Expected {N_CHANNELS} channels, got {w.shape[2]}"
        )
        assert w.shape[3] == N_SAMPLES, (
            f"Expected {N_SAMPLES} samples, got {w.shape[3]}"
        )

    logger.info("STEP 1 COMPLETE: 4-channel data processed\n")


# ===================================================================
# STEP 2: Generate spectral feature caches
# ===================================================================
def step2_spectral_caches() -> int:
    """Compute spectral features (37-dim) for each window in each split."""
    from spectral_features import extract_spectral_features

    logger.info("=" * 70)
    logger.info("STEP 2: Generating spectral feature caches")
    logger.info(f"  Expected features per window: {8 * N_CHANNELS + 5}")
    logger.info("=" * 70)

    expected_n_features = 8 * N_CHANNELS + 5  # 37 for 4 channels
    n_features_actual = None

    for split in ["train", "val", "test"]:
        npz_path = OUTPUT_DATA_DIR / f"{split}_data.npz"
        cache_path = OUTPUT_DATA_DIR / f"{split}_spectral_cache.npy"

        data = np.load(npz_path)
        windows = data["windows"]  # (N, 1, 4, 500)
        n_windows = windows.shape[0]

        logger.info(f"  {split}: extracting features for {n_windows} windows...")
        t0 = time.time()

        features_list = []
        for i in range(n_windows):
            eeg = windows[i, 0, :, :]  # (4, 500)
            feat = extract_spectral_features(eeg, fs=SAMPLING_RATE)
            features_list.append(feat)

            if i == 0:
                n_features_actual = len(feat)
                logger.info(f"    First window: {n_features_actual} features "
                             f"(expected {expected_n_features})")
                assert n_features_actual == expected_n_features, (
                    f"Feature count mismatch: got {n_features_actual}, "
                    f"expected {expected_n_features}"
                )

        features = np.array(features_list, dtype=np.float64)
        np.save(cache_path, features)
        elapsed = time.time() - t0
        logger.info(f"    Saved {cache_path.name}: shape={features.shape}, "
                     f"time={elapsed:.1f}s")

    logger.info("STEP 2 COMPLETE: Spectral caches generated\n")
    return n_features_actual


# ===================================================================
# STEP 3: Build multiscale temporal dataset
# ===================================================================
def step3_build_multiscale_dataset() -> None:
    """Build causal temporal sequences for TCN training."""
    import subprocess

    logger.info("=" * 70)
    logger.info("STEP 3: Building multiscale temporal dataset")
    logger.info(f"  Lookback={LOOKBACK}, Horizon={HORIZON}, "
                 f"TargetSmooth={TARGET_SMOOTH_WINDOW}")
    logger.info("=" * 70)

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "temporal_multiscale" / "build_multiscale_dataset.py"),
        "--processed-dir", str(OUTPUT_DATA_DIR),
        "--raw-root", str(BIDS_ROOT),
        "--output-dir", str(MULTISCALE_DIR),
        "--lookback", str(LOOKBACK),
        "--horizon", str(HORIZON),
        "--target-smooth-window", str(TARGET_SMOOTH_WINDOW),
    ]
    logger.info(f"  Running: {' '.join(cmd[-8:])}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        logger.error(f"Build failed:\n{result.stderr}")
        raise RuntimeError("Multiscale dataset build failed")

    # Verify metadata
    meta_path = MULTISCALE_DIR / "metadata.json"
    with open(meta_path) as f:
        meta = json.load(f)
    logger.info(f"  Metadata: {json.dumps(meta, indent=2)}")

    expected_tcn_features = 8 * N_CHANNELS + 5 + 7 + 5  # spectral + PAC + context = 49
    assert meta["n_features"] == expected_tcn_features, (
        f"TCN feature count mismatch: got {meta['n_features']}, "
        f"expected {expected_tcn_features}"
    )

    logger.info("STEP 3 COMPLETE: Multiscale dataset built\n")


# ===================================================================
# STEP 4: Train EEGNet (4-channel)
# ===================================================================
def step4_train_eegnet() -> dict:
    """Train EEGNet on 4-channel windows for static PAC prediction."""
    import torch
    from torch.utils.data import DataLoader, TensorDataset
    from eegnet import EEGNet

    logger.info("=" * 70)
    logger.info("STEP 4: Training EEGNet (4-channel)")
    logger.info(f"  Input shape: (batch, 1, {N_CHANNELS}, {N_SAMPLES})")
    logger.info(f"  Epochs={EEGNET_EPOCHS}, Batch={EEGNET_BATCH_SIZE}, "
                 f"LR={EEGNET_LR}")
    logger.info("=" * 70)

    # Deterministic seeding
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
        torch.backends.cudnn.deterministic = True

    # Device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    logger.info(f"  Device: {device}")

    # Load data
    train_data = np.load(OUTPUT_DATA_DIR / "train_data.npz")
    val_data = np.load(OUTPUT_DATA_DIR / "val_data.npz")

    # Z-score normalize PAC targets (training set statistics only)
    pac_train_raw = train_data["pac"].astype(np.float64)
    pac_mean = float(pac_train_raw.mean())
    pac_std = float(pac_train_raw.std())
    logger.info(f"  PAC normalization: mean={pac_mean:.8f}, std={pac_std:.8f}")

    pac_train = (pac_train_raw - pac_mean) / pac_std
    pac_val = (val_data["pac"].astype(np.float64) - pac_mean) / pac_std

    # Tensors
    X_train = torch.tensor(train_data["windows"], dtype=torch.float32)
    y_train = torch.tensor(pac_train, dtype=torch.float32).unsqueeze(1)
    X_val = torch.tensor(val_data["windows"], dtype=torch.float32)
    y_val = torch.tensor(pac_val, dtype=torch.float32).unsqueeze(1)

    train_loader = DataLoader(
        TensorDataset(X_train, y_train),
        batch_size=EEGNET_BATCH_SIZE, shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(X_val, y_val),
        batch_size=EEGNET_BATCH_SIZE, shuffle=False,
    )

    # Model
    model = EEGNet(n_channels=N_CHANNELS, n_samples=N_SAMPLES).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    logger.info(f"  Parameters: {n_params:,}")

    # Optimizer, scheduler, loss
    optimizer = torch.optim.Adam(
        model.parameters(), lr=EEGNET_LR, weight_decay=1e-4
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5,
    )
    loss_fn = torch.nn.MSELoss()

    # Training loop
    best_val_loss = float("inf")
    patience_counter = 0
    patience_limit = 15
    history = {"train_loss": [], "val_loss": []}

    for epoch in range(1, EEGNET_EPOCHS + 1):
        # Train
        model.train()
        train_losses = []
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = loss_fn(pred, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            train_losses.append(loss.item())

        # Validate
        model.eval()
        val_losses = []
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                pred = model(X_batch)
                loss = loss_fn(pred, y_batch)
                val_losses.append(loss.item())

        train_loss = np.mean(train_losses)
        val_loss = np.mean(val_losses)
        history["train_loss"].append(float(train_loss))
        history["val_loss"].append(float(val_loss))
        scheduler.step(val_loss)

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            # Save best checkpoint
            checkpoint = {
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "epoch": epoch,
                "val_loss": best_val_loss,
                "pac_mean": pac_mean,
                "pac_std": pac_std,
                "n_channels": N_CHANNELS,
                "channels": MUSE_PROXY_CHANNELS,
                "n_params": n_params,
            }
            ckpt_path = OUTPUT_MODEL_DIR / "best_eegnet_4ch.pth"
            torch.save(checkpoint, ckpt_path)
        else:
            patience_counter += 1

        if epoch % 10 == 0 or epoch == 1 or patience_counter == 0:
            logger.info(
                f"  Epoch {epoch:3d}/{EEGNET_EPOCHS}: "
                f"train_loss={train_loss:.6f}, val_loss={val_loss:.6f}"
                f"{' *' if patience_counter == 0 else ''}"
            )

        if patience_counter >= patience_limit:
            logger.info(f"  Early stopping at epoch {epoch} "
                         f"(patience={patience_limit})")
            break

    # Evaluate on test set
    test_data = np.load(OUTPUT_DATA_DIR / "test_data.npz")
    pac_test = (test_data["pac"].astype(np.float64) - pac_mean) / pac_std
    X_test = torch.tensor(test_data["windows"], dtype=torch.float32)
    y_test_norm = torch.tensor(pac_test, dtype=torch.float32).unsqueeze(1)

    model.load_state_dict(
        torch.load(OUTPUT_MODEL_DIR / "best_eegnet_4ch.pth",
                    weights_only=False, map_location=device)["model_state_dict"]
    )
    model.eval()
    with torch.no_grad():
        X_test_dev = X_test.to(device)
        preds_norm = model(X_test_dev).cpu().numpy().flatten()

    y_test_np = pac_test
    preds_np = preds_norm

    # R² in normalized space
    ss_res = np.sum((y_test_np - preds_np) ** 2)
    ss_tot = np.sum((y_test_np - y_test_np.mean()) ** 2)
    r2_norm = 1.0 - ss_res / ss_tot

    # R² in raw PAC space
    y_test_raw = test_data["pac"].astype(np.float64)
    preds_raw = preds_np * pac_std + pac_mean
    ss_res_raw = np.sum((y_test_raw - preds_raw) ** 2)
    ss_tot_raw = np.sum((y_test_raw - y_test_raw.mean()) ** 2)
    r2_raw = 1.0 - ss_res_raw / ss_tot_raw

    rmse_raw = np.sqrt(np.mean((y_test_raw - preds_raw) ** 2))

    results = {
        "n_channels": N_CHANNELS,
        "channels": MUSE_PROXY_CHANNELS,
        "n_params": n_params,
        "best_epoch": int(checkpoint["epoch"]),
        "best_val_loss": float(best_val_loss),
        "test_r2_normalized": float(r2_norm),
        "test_r2_raw": float(r2_raw),
        "test_rmse_raw": float(rmse_raw),
        "pac_mean": pac_mean,
        "pac_std": pac_std,
        "test_n_windows": len(y_test_raw),
    }

    logger.info(f"\n  EEGNet 4-channel Results:")
    logger.info(f"    Best epoch: {results['best_epoch']}")
    logger.info(f"    Test R² (normalized): {r2_norm:.4f}")
    logger.info(f"    Test R² (raw PAC):    {r2_raw:.4f}")
    logger.info(f"    Test RMSE (raw PAC):  {rmse_raw:.8f}")
    logger.info(f"    Parameters: {n_params:,}")

    # Save results
    with open(OUTPUT_MODEL_DIR / "eegnet_4ch_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info("STEP 4 COMPLETE: EEGNet 4-channel trained\n")
    return results


# ===================================================================
# STEP 5: Train MultiscaleCausalTCN
# ===================================================================
def step5_train_tcn() -> dict:
    """Train TCN on 4-channel multiscale temporal dataset."""
    import subprocess

    logger.info("=" * 70)
    logger.info("STEP 5: Training MultiscaleCausalTCN (4-channel features)")
    logger.info(f"  Lookback={LOOKBACK}, Horizon={HORIZON}")
    logger.info("=" * 70)

    run_name = f"multiscale_tcn_4ch_lb{LOOKBACK}_hz{HORIZON}_ts{TARGET_SMOOTH_WINDOW}"

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "temporal_multiscale" / "train_multiscale_tcn.py"),
        "--dataset-dir", str(MULTISCALE_DIR),
        "--models-dir", str(OUTPUT_MODEL_DIR),
        "--run-name", run_name,
        "--lookback", str(LOOKBACK),
        "--horizon", str(HORIZON),
        "--target-smooth-window", str(TARGET_SMOOTH_WINDOW),
        "--epochs", str(TCN_EPOCHS),
        "--batch-size", str(TCN_BATCH_SIZE),
        "--lr", str(TCN_LR),
        "--seed", str(SEED),
    ]
    logger.info(f"  Running TCN training...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        logger.error(f"TCN training failed:\nSTDOUT: {result.stdout[-2000:]}")
        logger.error(f"STDERR: {result.stderr[-2000:]}")
        raise RuntimeError("TCN training failed")

    # Extract results from training output
    logger.info(result.stdout[-1500:])

    # Load the checkpoint to get metrics
    import torch
    ckpt_path = OUTPUT_MODEL_DIR / f"best_{run_name}.pth"
    if not ckpt_path.exists():
        # Try alternative name patterns
        candidates = list(OUTPUT_MODEL_DIR.glob("best_multiscale_tcn_4ch*.pth"))
        if candidates:
            ckpt_path = candidates[0]
        else:
            logger.warning("No TCN checkpoint found — training may have failed")
            return {}

    ckpt = torch.load(ckpt_path, weights_only=False, map_location="cpu")
    tcn_results = {
        "checkpoint": str(ckpt_path.name),
        "n_features": int(ckpt.get("cfg", {}).get("n_features", 0)
                          if isinstance(ckpt.get("cfg"), dict)
                          else getattr(ckpt.get("cfg"), "n_features", 0)),
        "val_future_r2": float(ckpt.get("val_future_r2", 0)),
        "epoch": int(ckpt.get("epoch", 0)),
    }

    with open(OUTPUT_MODEL_DIR / "tcn_4ch_results.json", "w") as f:
        json.dump(tcn_results, f, indent=2)

    logger.info(f"\n  TCN 4-channel Results:")
    logger.info(f"    Checkpoint: {tcn_results['checkpoint']}")
    logger.info(f"    Best epoch: {tcn_results['epoch']}")
    logger.info(f"    Val future R²: {tcn_results['val_future_r2']:.4f}")
    logger.info(f"    n_features: {tcn_results['n_features']}")

    logger.info("STEP 5 COMPLETE: TCN 4-channel trained\n")
    return tcn_results


# ===================================================================
# STEP 6: Generate comparison report
# ===================================================================
def step6_comparison_report(eegnet_results: dict, tcn_results: dict) -> None:
    """Generate a comparison report: 4-channel vs 7-channel models."""

    logger.info("=" * 70)
    logger.info("STEP 6: Generating comparison report")
    logger.info("=" * 70)

    # 7-channel baseline metrics (from existing results)
    baseline_7ch = {
        "eegnet": {
            "n_channels": 7,
            "channels": ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8"],
            "test_r2_raw": 0.287,  # From CLAUDE.md
            "n_params": 1457,
        },
        "tcn": {
            "n_features": 73,
            "val_future_r2": 0.411,  # From checkpoint metadata
            "test_future_r2_hz5": 0.170,  # From RESULTS_REPORT
            "n_params": 31043,
        },
    }

    report_lines = [
        "# 4-Channel Muse 2 Proxy: Retraining Results",
        "",
        f"**Date:** {time.strftime('%Y-%m-%d')}",
        f"**Channels:** {', '.join(MUSE_PROXY_CHANNELS)} "
        f"(proxy for Muse 2 AF7/AF8/TP9/TP10)",
        f"**Dataset:** OpenNeuro ds005048 (N=35, elderly subjects)",
        "",
        "## Channel Mapping",
        "",
        "| Muse 2 | ds005048 Proxy | Region |",
        "|--------|---------------|--------|",
        "| AF7 | F7 | Inferior frontal L |",
        "| AF8 | F8 | Inferior frontal R |",
        "| TP9 | T7 | Temporal L (auditory cortex) |",
        "| TP10 | T8 | Temporal R (auditory cortex) |",
        "",
        "## EEGNet (Static PAC Prediction)",
        "",
        "| Metric | 7-channel (baseline) | 4-channel (Muse proxy) | Delta |",
        "|--------|---------------------|----------------------|-------|",
    ]

    if eegnet_results:
        r2_7 = baseline_7ch["eegnet"]["test_r2_raw"]
        r2_4 = eegnet_results.get("test_r2_raw", 0)
        delta = r2_4 - r2_7
        n_params_7 = baseline_7ch["eegnet"]["n_params"]
        n_params_4 = eegnet_results.get("n_params", 0)
        best_ep = eegnet_results.get("best_epoch", "?")
        rmse_val = eegnet_results.get("test_rmse_raw", 0)
        report_lines.extend([
            f"| Test R2 (raw PAC) | {r2_7:.3f} | {r2_4:.3f} | {delta:+.3f} |",
            f"| Parameters | {n_params_7} | {n_params_4} | - |",
            f"| Channels | 7 frontal | 4 (F7/F8/T7/T8) | -3 |",
            f"| Best epoch | - | {best_ep} | - |",
            f"| RMSE (raw PAC) | - | {rmse_val:.8f} | - |",
        ])
    else:
        report_lines.append("| (EEGNet not trained in this run) | - | - | - |")

    report_lines.extend([
        "",
        "## MultiscaleCausalTCN (Temporal PAC Forecasting, horizon=5s)",
        "",
        "| Metric | 7-channel (baseline) | 4-channel (Muse proxy) | Delta |",
        "|--------|---------------------|----------------------|-------|",
    ])

    if tcn_results:
        val_r2_7 = baseline_7ch["tcn"]["val_future_r2"]
        val_r2_4 = tcn_results.get("val_future_r2", 0)
        delta_val = val_r2_4 - val_r2_7
        n_feat_7 = baseline_7ch["tcn"]["n_features"]
        n_feat_4 = tcn_results.get("n_features", 0)
        tcn_ep = tcn_results.get("epoch", "?")
        report_lines.extend([
            f"| Val future R2 | {val_r2_7:.3f} | {val_r2_4:.3f} | {delta_val:+.3f} |",
            f"| Input features | {n_feat_7} | {n_feat_4} | {n_feat_4 - n_feat_7} |",
            f"| Best epoch | - | {tcn_ep} | - |",
        ])
    else:
        report_lines.append("| (TCN not trained in this run) | - | - | - |")

    data_rel = str(OUTPUT_DATA_DIR.relative_to(PROJECT_ROOT))
    ms_rel = str(MULTISCALE_DIR.relative_to(PROJECT_ROOT))
    model_rel = str(OUTPUT_MODEL_DIR.relative_to(PROJECT_ROOT))
    gen_time = time.strftime("%Y-%m-%d %H:%M")
    report_lines.append("")
    report_lines.append("## Interpretation")
    report_lines.append("")
    report_lines.append(
        "The performance delta between 7-channel and 4-channel models quantifies "
        "the cost of adapting from research-grade frontal coverage to consumer "
        "hardware (Muse 2) electrode positions."
    )
    report_lines.append("")
    report_lines.append("**Important caveats:**")
    report_lines.append(
        "- R2 values are NOT directly comparable across channel configurations "
        "because the PAC labels differ (mean MI across different channel sets)."
    )
    report_lines.append(
        "- Each model should be evaluated against its own persistence/Ridge baselines."
    )
    report_lines.append(
        "- At deployment, the domain gap (dry vs gel electrodes, reference mismatch) "
        "will further degrade performance beyond what this proxy comparison shows."
    )
    report_lines.append("")
    report_lines.append("## Files Generated")
    report_lines.append("")
    report_lines.append(f"- `{data_rel}/` -- 4-channel processed data")
    report_lines.append(f"- `{ms_rel}/` -- Temporal dataset (49 features)")
    report_lines.append(f"- `{model_rel}/best_eegnet_4ch.pth` -- EEGNet checkpoint")
    report_lines.append(f"- `{model_rel}/best_*tcn_4ch*.pth` -- TCN checkpoint")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append(f"*Generated by muse_4ch/retrain_pipeline.py on {gen_time}*")

    report_path = OUTPUT_MODEL_DIR / "COMPARISON_REPORT.md"
    report_path.write_text("\n".join(report_lines))
    logger.info(f"  Report written to {report_path}")
    logger.info("STEP 6 COMPLETE\n")


# ===================================================================
# MAIN
# ===================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="4-Channel Muse 2 Model Retraining Pipeline"
    )
    parser.add_argument("--skip-data", action="store_true",
                        help="Skip data processing (use existing muse_4ch data)")
    parser.add_argument("--skip-eegnet", action="store_true",
                        help="Skip EEGNet training")
    parser.add_argument("--skip-tcn", action="store_true",
                        help="Skip TCN training")
    args = parser.parse_args()

    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MODEL_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("4-CHANNEL MUSE 2 PROXY RETRAINING PIPELINE")
    logger.info("=" * 70)
    logger.info(f"Channels:     {MUSE_PROXY_CHANNELS}")
    logger.info(f"Data output:  {OUTPUT_DATA_DIR}")
    logger.info(f"Model output: {OUTPUT_MODEL_DIR}")
    logger.info(f"Seed:         {SEED}")
    logger.info("")

    t_start = time.time()

    # Step 1: Process raw data
    if not args.skip_data:
        step1_process_data()
        step2_spectral_caches()
        step3_build_multiscale_dataset()
    else:
        logger.info("Skipping data processing (--skip-data)\n")

    # Step 4: Train EEGNet
    eegnet_results = {}
    if not args.skip_eegnet:
        eegnet_results = step4_train_eegnet()
    else:
        logger.info("Skipping EEGNet training (--skip-eegnet)\n")
        results_path = OUTPUT_MODEL_DIR / "eegnet_4ch_results.json"
        if results_path.exists():
            with open(results_path) as f:
                eegnet_results = json.load(f)

    # Step 5: Train TCN
    tcn_results = {}
    if not args.skip_tcn:
        tcn_results = step5_train_tcn()
    else:
        logger.info("Skipping TCN training (--skip-tcn)\n")
        results_path = OUTPUT_MODEL_DIR / "tcn_4ch_results.json"
        if results_path.exists():
            with open(results_path) as f:
                tcn_results = json.load(f)

    # Step 6: Comparison report
    step6_comparison_report(eegnet_results, tcn_results)

    elapsed = time.time() - t_start
    logger.info("=" * 70)
    logger.info(f"PIPELINE COMPLETE in {elapsed / 60:.1f} minutes")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
