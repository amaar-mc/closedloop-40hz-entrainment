"""
NeuroCare 40Hz — Live Mission Control v3

Real-time closed-loop 40Hz gamma entrainment with Muse 2 EEG.
Uses adapter.get_window() for reliable EEG acquisition with proper
256→250 Hz resampling. Bandpass filters raw EEG before all analysis.

Launch:
    streamlit run neurocare_live.py

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import io
import sys
import time as _time
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import streamlit as st
from scipy.io import wavfile
from scipy import signal

_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
FS = 250.0
N_CH = 4
N_SAMP = 500
CH_NAMES = ["TP9", "AF7", "AF8", "TP10"]
BANDS = {"Delta": (1, 4), "Theta": (4, 8), "Alpha": (8, 13),
         "Beta": (13, 30), "Gamma": (38, 42)}
Z_ON = -0.5
Z_OFF = 0.5
HYSTERESIS = 6.0
LOOKBACK = 20

# Bandpass 0.5-45 Hz — removes DC drift and high-freq noise from Muse 2
_BP_SOS = signal.butter(4, [0.5, 45.0], btype="band", fs=FS, output="sos")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _bandpass(eeg: np.ndarray) -> np.ndarray:
    """Bandpass filter (0.5-45 Hz) each channel. Returns filtered copy."""
    return signal.sosfiltfilt(_BP_SOS, eeg, axis=1).astype(np.float32)


def _band_powers(eeg: np.ndarray) -> Dict[str, float]:
    """Mean band power across channels. Returns dict of scalars."""
    nperseg = min(256, eeg.shape[1])
    freqs, psd = signal.welch(eeg, fs=FS, nperseg=nperseg, axis=1)
    _trapz = getattr(np, "trapz", None) or np.trapezoid
    out = {}
    for name, (lo, hi) in BANDS.items():
        idx = (freqs >= lo) & (freqs <= hi)
        if idx.sum() > 0:
            out[name] = float(_trapz(psd[:, idx], freqs[idx], axis=1).mean())
        else:
            out[name] = 0.0
    return out


def _pac_display(pac: float, history: List[float]) -> float:
    """Adaptive 0-100 display from session percentiles."""
    if len(history) < 5:
        return 50.0
    arr = np.array(history)
    p5, p95 = float(np.percentile(arr, 5)), float(np.percentile(arr, 95))
    if p95 - p5 < 1e-12:
        return 50.0
    return round(max(0.0, min(100.0, (pac - p5) / (p95 - p5) * 100)), 1)


def _z_score(pac: float, history: List[float]) -> float:
    if len(history) < 10:
        return 0.0
    recent = np.array(history[-30:])
    s = float(recent.std())
    return (pac - float(recent.mean())) / s if s > 1e-12 else 0.0


def _pac_stim_features(pac_hist: List[float], stim: bool,
                        t_switch: float, n_stim: int, step: int) -> np.ndarray:
    n = len(pac_hist)
    p = pac_hist[-1] if n > 0 else 0.0
    ma = lambda w: float(np.mean(pac_hist[-w:])) if n >= w else (float(np.mean(pac_hist)) if n > 0 else 0.0)
    diff = lambda lag: (pac_hist[-1] - pac_hist[-1 - lag]) if n > lag else 0.0
    sf = n_stim / max(1, step) if step > 0 else 0.0
    phase = step * 2.0 / 70.0 * 2 * np.pi
    return np.array([p, ma(2), ma(4), ma(8), ma(16), diff(1), diff(4),
                      1.0 if stim else 0.0, t_switch, sf,
                      np.sin(phase), np.cos(phase)], dtype=np.float32)


@st.cache_data
def _make_wav(vol: float = 0.3) -> bytes:
    sr = 44100
    period = sr // 40
    click_n = int(0.001 * sr)
    buf = np.zeros(period, dtype=np.float32)
    t = np.arange(click_n, dtype=np.float32) / sr
    buf[:click_n] = vol * np.sin(2 * np.pi * 1000 * t)
    audio = np.tile(np.tile(buf, 40), 30).astype(np.float32)
    out = io.BytesIO()
    wavfile.write(out, sr, audio)
    return out.getvalue()


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
@st.cache_resource
def _load_models():
    import torch
    from pac_computation import PACComputer
    from experimental.run_experiments import ImprovedTCN

    pac_comp = PACComputer(theta_band=(4, 8), gamma_band=(38, 42), fs=250, n_bins=18)

    ckpt = torch.load(str(_ROOT / "models/muse_4ch/best_pac_stim_tcn_4ch.pth"),
                       map_location="cpu", weights_only=False)
    cfg = ckpt["config"]
    tcn = ImprovedTCN(n_features=cfg["n_features"], hidden=cfg["hidden"],
                       kernel_size=cfg["kernel_size"], dilations=cfg["dilations"],
                       dropout=cfg["dropout"], n_heads=cfg["n_heads"])
    tcn.load_state_dict(ckpt["model_state_dict"])
    tcn.eval()

    feat_sc = np.load(str(_ROOT / "models/muse_4ch/pac_stim_feature_scalers.npz"))
    return pac_comp, tcn, ckpt["scalers"], feat_sc["mean"], feat_sc["std"]


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------
def _init():
    from src.streaming.adapters import RealEEGAdapter
    pac_comp, tcn, tsc, fm, fs = _load_models()
    adapter = RealEEGAdapter()
    st.session_state.update({
        "running": True, "pac_comp": pac_comp, "tcn": tcn,
        "tsc": tsc, "fm": fm, "fs": fs, "adapter": adapter,
        "step": 0, "stim": False, "n_stim": 0, "n_rest": 0,
        "t_switch": 0.0, "pac_hist": [], "pac_disp": [],
        "future_disp": [], "z_hist": [],
        "bands": {b: [] for b in BANDS}, "stim_hist": [],
        "log": [], "buf": [], "eeg": np.zeros((N_CH, N_SAMP), dtype=np.float32),
    })


def _cleanup():
    a = st.session_state.get("adapter")
    if a:
        try: a.close()
        except: pass
    for k in list(st.session_state.keys()):
        if k != "page":
            st.session_state.pop(k, None)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="NeuroCare Live", page_icon="\U0001f9e0", layout="wide")

    # Sidebar
    with st.sidebar:
        st.markdown("**NeuroCare** v3.0")
        st.divider()
        if st.session_state.get("running"):
            st.success("Muse 2 Connected")
        else:
            st.info("Muse 2 (disconnected)")
        st.caption("4ch: TP9 · AF7 · AF8 · TP10")
        st.divider()
        vol = st.slider("Stimulus Volume", 0.0, 1.0, 0.3, 0.05)
        st.session_state["_vol"] = vol
        st.divider()
        st.caption("PAC: Direct MI (Tort 2010)")
        st.caption("TCN: PAC+Stim (6.3K params)")
        st.caption("Test R²: 0.40 | Horizon: 5s")
        st.caption(f"Stim: z<{Z_ON} ON, z>{Z_OFF} OFF")

    st.title("NeuroCare 40Hz — Live Mission Control")

    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        go = st.button("▶ Connect", type="primary",
                        disabled=st.session_state.get("running", False))
    with c2:
        stop = st.button("■ Stop",
                          disabled=not st.session_state.get("running", False))

    if go and not st.session_state.get("running"):
        with st.spinner("Connecting to Muse 2..."):
            try:
                _init()
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {e}")
                return

    if stop and st.session_state.get("running"):
        _cleanup()
        st.rerun()

    if not st.session_state.get("running"):
        st.info("Turn on Muse 2 (hold power → LEDs blink), then click **Connect**.")
        return

    # === LIVE LOOP ===
    import torch

    S = st.session_state
    adapter = S["adapter"]
    step = S["step"]

    # --- Acquire EEG (blocks ~2s for proper data) ---
    eeg_raw = adapter.get_window()  # (4, 500) resampled from 256→250 Hz
    eeg = _bandpass(eeg_raw)  # remove DC drift + high-freq noise
    S["eeg"] = eeg

    # --- Band powers ---
    bp = _band_powers(eeg)
    for b in BANDS:
        S["bands"][b].append(bp[b])

    # --- PAC ---
    pac = S["pac_comp"].compute_pac_average(eeg)
    S["pac_hist"].append(pac)
    disp = _pac_display(pac, S["pac_hist"])
    S["pac_disp"].append(disp)
    z = _z_score(pac, S["pac_hist"])
    S["z_hist"].append(z)

    # --- TCN prediction ---
    feat = _pac_stim_features(S["pac_hist"], S["stim"], S["t_switch"], S["n_stim"], step)
    S["buf"].append(feat)
    if len(S["buf"]) > LOOKBACK:
        S["buf"] = S["buf"][-LOOKBACK:]

    fut_disp = None
    has_pred = False
    if len(S["buf"]) >= LOOKBACK:
        seq = np.stack(S["buf"][-LOOKBACK:])
        seq_n = (seq - S["fm"]) / (S["fs"] + 1e-12)
        with torch.no_grad():
            pn = S["tcn"](torch.from_numpy(seq_n[None].astype(np.float32))).item()
        fut_pac = pn * float(S["tsc"]["y_future_std"]) + float(S["tsc"]["y_future_mean"])
        fut_disp = _pac_display(fut_pac, S["pac_hist"])
        has_pred = True
    S["future_disp"].append(fut_disp)

    # --- Stimulus decision ---
    prev = S["stim"]
    stim = prev
    reason = f"warmup ({step+1}/{LOOKBACK})"

    if step >= LOOKBACK and has_pred:
        can = S["t_switch"] >= HYSTERESIS
        if prev:
            if z > Z_OFF and can:
                stim = False
                reason = f"z={z:.2f}>{Z_OFF} → REST"
            else:
                reason = f"STIM hold (z={z:.2f})"
        else:
            if z < Z_ON and can:
                stim = True
                reason = f"z={z:.2f}<{Z_ON} → STIM"
            else:
                reason = f"REST hold (z={z:.2f})"

    S["stim_hist"].append(stim)
    S["log"].append(reason)
    S["step"] += 1
    if stim: S["n_stim"] += 1
    else: S["n_rest"] += 1
    if stim != prev: S["t_switch"] = 0.0
    else: S["t_switch"] += 2.0
    S["stim"] = stim

    # =====================================================================
    # RENDER
    # =====================================================================

    # Status
    if step < LOOKBACK:
        st.progress((step + 1) / LOOKBACK, text=f"Warming up... ({step+1}/{LOOKBACK})")
    else:
        st.success("Closed-loop active")

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Brain Sync", f"{disp:.0f}/100")
    m2.markdown(f"### {'🟢 STIM' if stim else '⚪ REST'}")
    m3.metric("Therapy %", f"{S['n_stim']/max(1,step+1)*100:.0f}%")
    m4.metric("Predicted", f"{fut_disp:.0f}/100" if fut_disp is not None else "—")
    m5.metric("Windows", step + 1)

    # Audio
    if stim:
        st.audio(_make_wav(st.session_state.get("_vol", 0.3)),
                 format="audio/wav", loop=True, autoplay=True)

    # --- Charts ---
    left, right = st.columns(2)

    with left:
        # PAC trend (fixed 0-100)
        st.markdown("**Brain Sync Level**")
        n = len(S["pac_disp"])
        chart_data = {"Brain Sync": S["pac_disp"][-60:]}
        fv = S["future_disp"][-60:]
        if any(v is not None for v in fv):
            chart_data["Predicted (5s)"] = [v if v is not None else None for v in fv]
        df = pd.DataFrame(chart_data)
        # Pad to force 0-100 axis
        df.loc[len(df)] = {"Brain Sync": 0.0}
        df.loc[len(df)] = {"Brain Sync": 100.0}
        st.line_chart(df.iloc[:-2], use_container_width=True, height=250)

        # Band powers
        st.markdown("**Band Powers**")
        bp_data = {b: S["bands"][b][-30:] for b in BANDS if len(S["bands"][b]) > 1}
        if bp_data:
            max_len = max(len(v) for v in bp_data.values())
            for k in bp_data:
                while len(bp_data[k]) < max_len:
                    bp_data[k].insert(0, bp_data[k][0] if bp_data[k] else 0)
            # Clip to remove artifact spikes
            bp_df = pd.DataFrame(bp_data)
            for col in bp_df.columns:
                p99 = bp_df[col].quantile(0.95)
                bp_df[col] = bp_df[col].clip(upper=p99 * 2)
            st.line_chart(bp_df, use_container_width=True, height=200)

    with right:
        # Raw EEG (bandpass filtered)
        st.markdown("**EEG (filtered 0.5-45 Hz)**")
        t = np.arange(N_SAMP) / FS
        eeg_df = pd.DataFrame({ch: eeg[i] for i, ch in enumerate(CH_NAMES)}, index=t)
        st.line_chart(eeg_df, use_container_width=True, height=250)

        # Stimulus timeline
        st.markdown("**Stimulus Timeline**")
        if len(S["stim_hist"]) > 1:
            st.area_chart(
                pd.DataFrame({"Stimulus": [float(s) for s in S["stim_hist"][-60:]]}),
                use_container_width=True, height=100, color="#10B981",
            )

        # Z-score
        st.markdown("**Session Z-Score**")
        if len(S["z_hist"]) > 1:
            z_df = pd.DataFrame({"Z": S["z_hist"][-60:]})
            z_df["Zero"] = 0.0
            st.line_chart(z_df, use_container_width=True, height=100)

    # Decision log
    with st.expander("Decision Log", expanded=False):
        for i, entry in enumerate(reversed(S["log"][-10:])):
            sn = step + 1 - i
            icon = "🟢" if S["stim_hist"][-(i+1)] else "⚪"
            st.text(f"{icon} #{sn}: {entry}")

    # Next step
    st.rerun()


if __name__ == "__main__":
    main()
