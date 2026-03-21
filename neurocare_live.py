"""
NeuroCare 40Hz — Live Mission Control

Real-time closed-loop 40Hz gamma entrainment with Muse 2 EEG.
Shows live band powers (delta, theta, alpha, beta, gamma), raw EEG traces,
PAC trend, TCN future prediction, stimulus decisions, and 40Hz audio output.

Launch:
    streamlit run neurocare_live.py

Requires: Muse 2 paired and powered on (hold button until LEDs blink).

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import io
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
from scipy.io import wavfile
from scipy import signal

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_VERSION = "v2.0 (Live EEG)"
FS = 250.0
N_CHANNELS = 4
N_SAMPLES = 500
CHANNEL_NAMES = ["TP9", "AF7", "AF8", "TP10"]
BAND_RANGES = {
    "Delta": (1.0, 4.0),
    "Theta": (4.0, 8.0),
    "Alpha": (8.0, 13.0),
    "Beta": (13.0, 30.0),
    "Gamma": (38.0, 42.0),
}
# Hysteresis thresholds for stimulus decisions (z-score relative to session)
Z_STIM_ON = -0.5    # stimulate when PAC drops below -0.5σ of session baseline
Z_STIM_OFF = 0.5    # rest when PAC rises above +0.5σ
HYSTERESIS_SEC = 6.0  # minimum seconds before switching state


# ---------------------------------------------------------------------------
# Audio — generate a long loopable WAV to minimize restart gaps
# ---------------------------------------------------------------------------
@st.cache_data
def make_40hz_wav_long(volume: float = 0.3, duration_sec: int = 30,
                       sample_rate: int = 44100) -> bytes:
    """30-second 40 Hz click-train WAV. Longer duration = fewer loop restarts."""
    period = sample_rate // 40
    click_n = int(0.001 * sample_rate)
    period_buf = np.zeros(period, dtype=np.float32)
    t = np.arange(click_n, dtype=np.float32) / sample_rate
    period_buf[:click_n] = volume * np.sin(2 * np.pi * 1000 * t)
    one_sec = np.tile(period_buf, 40)
    audio = np.tile(one_sec, duration_sec).astype(np.float32)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
@st.cache_resource
def load_models():
    """Load 4-channel EEGNet + PAC+stim TCN (experimental breakthrough model).

    The PAC+stim TCN uses only 12 features (7 PAC-derived + 5 stim context),
    dropping spectral features that cause subject-specific overfitting.
    Test R²=0.40 (4ch) vs 0.11 with all features.

    Returns (eegnet, pac_mean, pac_std, pac_stim_tcn, tcn_scalers).
    """
    import torch
    from eegnet import EEGNet
    from experimental.run_experiments import ImprovedTCN

    device = "cpu"

    # EEGNet for static PAC estimation
    eegnet_path = str(_ROOT / "models/muse_4ch/best_eegnet_4ch.pth")
    ckpt = torch.load(eegnet_path, map_location=device, weights_only=False)
    eegnet = EEGNet(n_channels=4, n_samples=500)
    eegnet.load_state_dict(ckpt["model_state_dict"])
    eegnet.eval()
    pac_mean = float(ckpt.get("pac_mean", 0.0))
    pac_std = float(ckpt.get("pac_std", 1.0))

    # PAC+stim TCN (12 features, experimental breakthrough)
    tcn_path = str(_ROOT / "models/muse_4ch/best_pac_stim_tcn_4ch.pth")
    tcn_ckpt = torch.load(tcn_path, map_location=device, weights_only=False)
    cfg = tcn_ckpt["config"]
    pac_stim_tcn = ImprovedTCN(
        n_features=cfg["n_features"], hidden=cfg["hidden"],
        kernel_size=cfg["kernel_size"], dilations=cfg["dilations"],
        dropout=cfg["dropout"], n_heads=cfg["n_heads"],
    )
    pac_stim_tcn.load_state_dict(tcn_ckpt["model_state_dict"])
    pac_stim_tcn.eval()
    tcn_scalers = tcn_ckpt["scalers"]

    return eegnet, pac_mean, pac_std, pac_stim_tcn, tcn_scalers


# ---------------------------------------------------------------------------
# Signal analysis
# ---------------------------------------------------------------------------
def compute_band_powers(eeg: np.ndarray, fs: float) -> Dict[str, np.ndarray]:
    """Compute power in each frequency band for each channel."""
    nperseg = min(256, eeg.shape[1])
    freqs, psd = signal.welch(eeg, fs=fs, nperseg=nperseg, axis=1)
    _trapz = getattr(np, "trapz", None) or np.trapezoid
    powers = {}
    for band_name, (lo, hi) in BAND_RANGES.items():
        idx = np.logical_and(freqs >= lo, freqs <= hi)
        if idx.sum() > 0:
            powers[band_name] = _trapz(psd[:, idx], freqs[idx], axis=1)
        else:
            powers[band_name] = np.zeros(eeg.shape[0])
    return powers


def pac_to_display_adaptive(pac_value: float, pac_history: List[float]) -> float:
    """Adaptive PAC display: normalize to session's own distribution.

    Uses running percentiles from the session itself so the 0-100 scale
    reflects THIS session's signal range, not the training set's.
    Falls back to 50.0 until enough data accumulates.
    """
    if len(pac_history) < 5:
        return 50.0
    arr = np.array(pac_history)
    p5 = float(np.percentile(arr, 5))
    p95 = float(np.percentile(arr, 95))
    if p95 - p5 < 1e-12:
        return 50.0
    normalized = (pac_value - p5) / (p95 - p5)
    return round(max(0.0, min(100.0, normalized * 100.0)), 1)


def session_z_score(pac_value: float, pac_history: List[float],
                    window: int = 30) -> float:
    """Z-score of current PAC relative to recent session baseline.

    This adapts to the Muse 2's actual signal distribution instead of
    comparing against training-set statistics.
    """
    if len(pac_history) < 10:
        return 0.0
    recent = np.array(pac_history[-window:])
    mu = float(recent.mean())
    sigma = float(recent.std())
    if sigma < 1e-12:
        return 0.0
    return (pac_value - mu) / sigma


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------
def _build_pac_stim_features(pac_history: List[float], stim_active: bool,
                              time_since_switch: float, n_stim: int,
                              step_count: int) -> np.ndarray:
    """Build the 12 PAC+stim features that the experimental TCN expects.

    Features (same order as multiscale dataset indices 37:49 for 4ch):
      0: pac_current (latest PAC value)
      1: pac_ma2 (moving average over 2 steps)
      2: pac_ma4 (moving average over 4 steps)
      3: pac_ma8 (moving average over 8 steps)
      4: pac_ma16 (moving average over 16 steps)
      5: pac_diff1 (1-step difference)
      6: pac_diff4 (4-step difference)
      7: stim_state (1.0 if stimulating, 0.0 if rest)
      8: time_since_switch (seconds since last state change)
      9: stim_frac (fraction of session spent stimulating)
     10: phase_sin (sine of session phase, period ~70s)
     11: phase_cos (cosine of session phase, period ~70s)
    """
    n = len(pac_history)
    pac = pac_history[-1] if n > 0 else 0.0

    def _ma(w: int) -> float:
        if n < w:
            return float(np.mean(pac_history)) if n > 0 else 0.0
        return float(np.mean(pac_history[-w:]))

    def _diff(lag: int) -> float:
        if n <= lag:
            return 0.0
        return pac_history[-1] - pac_history[-1 - lag]

    stim_frac = n_stim / max(1, step_count) if step_count > 0 else 0.0
    session_time = step_count * 2.0
    phase = session_time / 70.0 * 2 * np.pi

    return np.array([
        pac, _ma(2), _ma(4), _ma(8), _ma(16),
        _diff(1), _diff(4),
        1.0 if stim_active else 0.0,
        time_since_switch, stim_frac,
        np.sin(phase), np.cos(phase),
    ], dtype=np.float32)


def init_session():
    """Initialize all session state for a new live session."""
    from src.streaming.adapters import RealEEGAdapter

    eegnet, pac_mean, pac_std, pac_stim_tcn, tcn_scalers = load_models()
    adapter = RealEEGAdapter()

    st.session_state.update({
        "live_running": True,
        "eegnet": eegnet,
        "pac_mean": pac_mean,
        "pac_std": pac_std,
        "pac_stim_tcn": pac_stim_tcn,
        "tcn_scalers": tcn_scalers,
        "adapter": adapter,
        "step_count": 0,
        "stim_active": False,
        "n_stim": 0,
        "n_rest": 0,
        "time_since_switch": 0.0,
        "pac_raw_history": [],
        "pac_display_history": [],
        "future_pac_history": [],
        "z_score_history": [],
        "band_history": {band: [] for band in BAND_RANGES},
        "eeg_latest": np.zeros((N_CHANNELS, N_SAMPLES), dtype=np.float32),
        "stim_history": [],
        "decision_log": [],
        # Rolling window of PAC+stim feature vectors for TCN (lookback=20)
        "pac_stim_buffer": [],
    })


def cleanup_session():
    """Close adapter and clear session state."""
    adapter = st.session_state.get("adapter")
    if adapter is not None:
        try:
            adapter.close()
        except Exception:
            pass
    for key in list(st.session_state.keys()):
        if key not in ("page",):
            st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# Live update fragment — only this section re-renders, not the whole page
# ---------------------------------------------------------------------------
@st.fragment(run_every=timedelta(seconds=2))
def live_fragment():
    """Acquire one EEG window, run inference, update all displays."""
    import torch

    if not st.session_state.get("live_running", False):
        return

    eegnet = st.session_state.eegnet
    pac_stim_tcn = st.session_state.pac_stim_tcn
    tcn_scalers = st.session_state.tcn_scalers
    adapter = st.session_state.adapter
    step = st.session_state.step_count
    LOOKBACK = 20

    # --- Acquire EEG (no sleep — fragment timing handles the 2s interval) ---
    try:
        raw = adapter._board.get_current_board_data(N_SAMPLES)
        eeg_window = raw[adapter._eeg_indices, :].astype(np.float32)
        if eeg_window.shape[1] < N_SAMPLES:
            pad = np.zeros((N_CHANNELS, N_SAMPLES - eeg_window.shape[1]), dtype=np.float32)
            eeg_window = np.concatenate([pad, eeg_window], axis=1)
    except Exception:
        eeg_window = st.session_state.eeg_latest
    st.session_state.eeg_latest = eeg_window

    # --- Band powers ---
    band_powers = compute_band_powers(eeg_window, FS)
    for band_name, powers in band_powers.items():
        st.session_state.band_history[band_name].append(float(powers.mean()))

    # --- EEGNet PAC estimate ---
    with torch.no_grad():
        eeg_tensor = torch.from_numpy(
            eeg_window[np.newaxis, np.newaxis, :, :]
        ).float()
        pac_raw = eegnet(eeg_tensor).item()
        pac_current = pac_raw * st.session_state.pac_std + st.session_state.pac_mean
    st.session_state.pac_raw_history.append(pac_current)

    # --- Adaptive display value ---
    pac_display = pac_to_display_adaptive(pac_current, st.session_state.pac_raw_history)
    st.session_state.pac_display_history.append(pac_display)

    # --- Session z-score ---
    z = session_z_score(pac_current, st.session_state.pac_raw_history)
    st.session_state.z_score_history.append(z)

    # --- Build PAC+stim features and run TCN prediction ---
    pac_stim_feat = _build_pac_stim_features(
        pac_history=st.session_state.pac_raw_history,
        stim_active=st.session_state.stim_active,
        time_since_switch=st.session_state.time_since_switch,
        n_stim=st.session_state.n_stim,
        step_count=step,
    )
    st.session_state.pac_stim_buffer.append(pac_stim_feat)
    # Keep only last 20 steps (lookback)
    if len(st.session_state.pac_stim_buffer) > LOOKBACK:
        st.session_state.pac_stim_buffer = st.session_state.pac_stim_buffer[-LOOKBACK:]

    future_display = None
    has_prediction = False
    if len(st.session_state.pac_stim_buffer) >= LOOKBACK:
        # Stack into (1, 20, 12) tensor and normalize with training scalers
        seq = np.stack(st.session_state.pac_stim_buffer[-LOOKBACK:], axis=0)  # (20, 12)
        seq_tensor = torch.from_numpy(seq[np.newaxis, :, :]).float()  # (1, 20, 12)
        with torch.no_grad():
            pred_norm = pac_stim_tcn(seq_tensor).item()
        # Denormalize: prediction is in z-score space of training targets
        yf_mean = float(tcn_scalers["y_future_mean"])
        yf_std = float(tcn_scalers["y_future_std"])
        future_pac = pred_norm * yf_std + yf_mean
        future_display = pac_to_display_adaptive(future_pac, st.session_state.pac_raw_history)
        has_prediction = True
    st.session_state.future_pac_history.append(future_display)

    # --- Stimulus decision: z-score with hysteresis ---
    prev_stim = st.session_state.stim_active
    stim_active = prev_stim  # default: maintain current state
    decision_reason = "warmup"

    if step >= LOOKBACK and has_prediction:
        can_switch = st.session_state.time_since_switch >= HYSTERESIS_SEC
        if prev_stim:
            # Currently stimulating — stop if PAC has recovered
            if z > Z_STIM_OFF and can_switch:
                stim_active = False
                decision_reason = f"z={z:.2f} > {Z_STIM_OFF} → REST (PAC recovered)"
            else:
                stim_active = True
                reason_hold = "hysteresis" if not can_switch else f"z={z:.2f} ≤ {Z_STIM_OFF}"
                decision_reason = f"STIM (holding: {reason_hold})"
        else:
            # Currently resting — stimulate if PAC drops
            if z < Z_STIM_ON and can_switch:
                stim_active = True
                decision_reason = f"z={z:.2f} < {Z_STIM_ON} → STIM (PAC low)"
            else:
                stim_active = False
                reason_hold = "hysteresis" if not can_switch else f"z={z:.2f} ≥ {Z_STIM_ON}"
                decision_reason = f"REST (holding: {reason_hold})"
    elif step < LOOKBACK:
        decision_reason = f"warmup ({step + 1}/{LOOKBACK})"
        stim_active = False

    # Update counts
    st.session_state.stim_history.append(stim_active)
    st.session_state.decision_log.append(decision_reason)
    st.session_state.step_count += 1
    if stim_active:
        st.session_state.n_stim += 1
    else:
        st.session_state.n_rest += 1
    if stim_active != prev_stim:
        st.session_state.time_since_switch = 0.0
    else:
        st.session_state.time_since_switch += 2.0
    st.session_state.stim_active = stim_active

    # =====================================================================
    # RENDER — inside fragment, only this section refreshes
    # =====================================================================

    # --- Status bar ---
    if step < LOOKBACK:
        st.progress((step + 1) / LOOKBACK,
                     text=f"Warming up TCN... ({step + 1}/{LOOKBACK} windows)")
    else:
        st.success("Models active — closed-loop running")

    # --- Key metrics row ---
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Brain Sync Level", f"{pac_display:.1f}/100")
    with m2:
        if stim_active:
            st.markdown("### :green[⬤ STIMULATING]")
        else:
            st.markdown("### :gray[○ REST]")
    with m3:
        pct = (st.session_state.n_stim / max(1, step + 1)) * 100
        st.metric("Therapy Active", f"{pct:.0f}%")
    with m4:
        fd = st.session_state.future_pac_history[-1] if st.session_state.future_pac_history else None
        st.metric("Predicted (5s)", f"{fd:.1f}/100" if fd is not None else "—")
    with m5:
        st.metric("Windows", step + 1)

    # --- Audio (inside fragment — updates on state change) ---
    if stim_active:
        volume = st.session_state.get("_volume", 0.3)
        wav = make_40hz_wav_long(volume=volume, duration_sec=30)
        st.audio(wav, format="audio/wav", loop=True, autoplay=True)

    # --- Row 2: Band power charts + PAC trend ---
    col_bands, col_pac = st.columns([1, 2])

    with col_bands:
        st.markdown("#### Band Powers (last 30 windows)")
        band_df_data = {}
        for band_name in BAND_RANGES:
            vals = st.session_state.band_history[band_name][-30:]
            if len(vals) > 1:
                band_df_data[band_name] = list(vals)
        if band_df_data:
            max_len = max(len(v) for v in band_df_data.values())
            for k in band_df_data:
                while len(band_df_data[k]) < max_len:
                    band_df_data[k].insert(0, 0.0)
            band_df = pd.DataFrame(band_df_data)
            band_df.index.name = "window"
            band_long = band_df.reset_index().melt(
                id_vars="window", var_name="Band", value_name="Power"
            )
            st.vega_lite_chart(band_long, {
                "mark": "line",
                "encoding": {
                    "x": {"field": "window", "type": "quantitative", "title": "Window"},
                    "y": {"field": "Power", "type": "quantitative", "title": "Power (µV²)",
                           "scale": {"domain": [0, max(1e-6, band_long["Power"].quantile(0.99) * 1.2)]}},
                    "color": {"field": "Band", "type": "nominal"},
                },
                "width": "container", "height": 200,
            }, use_container_width=True)

        # Per-channel gamma
        st.markdown("#### Per-Channel Gamma (µV²)")
        gamma_powers = band_powers["Gamma"]
        gamma_df = pd.DataFrame({"Power": gamma_powers}, index=CHANNEL_NAMES)
        st.bar_chart(gamma_df, use_container_width=True, color="#EF4444")

    with col_pac:
        st.markdown("#### PAC Trend — Brain Sync Level")
        if len(st.session_state.pac_display_history) > 1:
            pac_df_data = {
                "Brain Sync Level": st.session_state.pac_display_history[-60:]
            }
            future_vals = st.session_state.future_pac_history[-60:]
            if any(v is not None for v in future_vals):
                pac_df_data["Predicted (5s)"] = [
                    v if v is not None else np.nan for v in future_vals
                ]
            pac_df = pd.DataFrame(pac_df_data)
            pac_df.index.name = "window"
            pac_long = pac_df.reset_index().melt(
                id_vars="window", var_name="Metric", value_name="Value"
            )
            st.vega_lite_chart(pac_long, {
                "mark": "line",
                "encoding": {
                    "x": {"field": "window", "type": "quantitative", "title": "Window"},
                    "y": {"field": "Value", "type": "quantitative", "title": "Brain Sync (0-100)",
                           "scale": {"domain": [0, 100]}},
                    "color": {"field": "Metric", "type": "nominal"},
                },
                "width": "container", "height": 250,
            }, use_container_width=True)

        # Z-score trend — fixed axis [-3, 3]
        if len(st.session_state.z_score_history) > 1:
            st.markdown("#### Session Z-Score")
            z_data = st.session_state.z_score_history[-60:]
            z_df = pd.DataFrame({"Z-Score": z_data})
            z_df.index.name = "window"
            z_df = z_df.reset_index()
            st.vega_lite_chart(z_df, {
                "mark": "line",
                "encoding": {
                    "x": {"field": "window", "type": "quantitative"},
                    "y": {"field": "Z-Score", "type": "quantitative",
                           "scale": {"domain": [-3, 3]}},
                },
                "width": "container", "height": 150,
            }, use_container_width=True)

    # --- Row 3: Raw EEG + Stimulus timeline ---
    col_eeg, col_stim = st.columns(2)

    with col_eeg:
        st.markdown("#### Raw EEG (latest 2s window)")
        t_axis = np.arange(N_SAMPLES) / FS
        eeg_df = pd.DataFrame(
            {ch: eeg_window[i, :] for i, ch in enumerate(CHANNEL_NAMES)},
            index=t_axis,
        )
        eeg_df.index.name = "time_s"
        eeg_long = eeg_df.reset_index().melt(
            id_vars="time_s", var_name="Channel", value_name="µV"
        )
        st.vega_lite_chart(eeg_long, {
            "mark": "line",
            "encoding": {
                "x": {"field": "time_s", "type": "quantitative", "title": "Time (s)"},
                "y": {"field": "µV", "type": "quantitative",
                       "scale": {"domain": [-500, 500]}},
                "color": {"field": "Channel", "type": "nominal"},
            },
            "width": "container", "height": 200,
        }, use_container_width=True)

    with col_stim:
        st.markdown("#### Stimulus Timeline")
        if len(st.session_state.stim_history) > 1:
            stim_vals = [1.0 if s else 0.0
                        for s in st.session_state.stim_history[-60:]]
            stim_df = pd.DataFrame({"window": range(len(stim_vals)), "Stimulus": stim_vals})
            st.vega_lite_chart(stim_df, {
                "mark": {"type": "area", "color": "#10B981"},
                "encoding": {
                    "x": {"field": "window", "type": "quantitative"},
                    "y": {"field": "Stimulus", "type": "quantitative",
                           "scale": {"domain": [0, 1]}},
                },
                "width": "container", "height": 200,
            }, use_container_width=True)

    # --- Decision log ---
    with st.expander("Decision Log (last 10)", expanded=False):
        log = st.session_state.decision_log[-10:]
        for i, entry in enumerate(reversed(log)):
            step_num = step + 1 - i
            is_stim = st.session_state.stim_history[-(i + 1)] if i < len(
                st.session_state.stim_history) else False
            icon = "🟢" if is_stim else "⚪"
            st.text(f"{icon} Step {step_num}: {entry}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="NeuroCare Live",
        page_icon="\U0001f9e0",
        layout="wide",
    )

    # --- Sidebar (persists across fragment reruns) ---
    with st.sidebar:
        st.markdown(f"**NeuroCare** {APP_VERSION}")
        st.divider()
        st.markdown("**Hardware**")
        if st.session_state.get("live_running", False):
            st.success("Muse 2 Connected")
        else:
            st.info("Muse 2 (disconnected)")
        st.caption("4ch: TP9 · AF7 · AF8 · TP10")
        st.divider()
        volume = st.slider("Stimulus Volume", 0.0, 1.0, 0.3, 0.05)
        st.session_state["_volume"] = volume
        st.divider()
        st.markdown("**Models**")
        st.caption("EEGNet 4ch (1.4K params)")
        st.caption("PAC+Stim TCN (6.3K params)")
        st.caption("12 features (no spectral)")
        st.caption("Horizon: 5s ahead")
        st.caption("Test R²: 0.40 (4ch)")
        st.divider()
        st.markdown("**Decision Logic**")
        st.caption(f"Stim ON: z < {Z_STIM_ON}")
        st.caption(f"Stim OFF: z > {Z_STIM_OFF}")
        st.caption(f"Hysteresis: {HYSTERESIS_SEC:.0f}s")

    # --- Title and controls (persist across fragment reruns) ---
    st.title("NeuroCare 40Hz — Live Mission Control")

    col_start, col_stop, col_spacer = st.columns([1, 1, 4])
    with col_start:
        start = st.button("▶ Connect & Start", type="primary",
                          disabled=st.session_state.get("live_running", False))
    with col_stop:
        stop = st.button("■ Stop Session",
                         disabled=not st.session_state.get("live_running", False))

    if start and not st.session_state.get("live_running", False):
        with st.spinner("Connecting to Muse 2 via BLE..."):
            try:
                init_session()
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {e}")
                st.info(
                    "Make sure Muse 2 is powered on (LEDs blinking) "
                    "and unpaired from your phone."
                )
                return

    if stop and st.session_state.get("live_running", False):
        cleanup_session()
        st.rerun()

    if not st.session_state.get("live_running", False):
        st.info(
            "**Ready.** Turn on Muse 2 (hold power → LEDs blink), "
            "then click **Connect & Start**."
        )
        return

    # --- Live fragment: only this section auto-refreshes every 2s ---
    live_fragment()


if __name__ == "__main__":
    main()
