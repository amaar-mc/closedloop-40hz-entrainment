"""
NeuroCare 40Hz -- Live Mission Control v4

Real-time closed-loop 40Hz gamma entrainment with Muse 2 EEG.
Uses adapter.get_window() for reliable EEG acquisition with proper
256->250 Hz resampling. Bandpass filters raw EEG before all analysis.

Rendering: Plotly graph_objects with fixed axes and st.fragment for
flicker-free partial reruns. No st.rerun() on the full page.

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
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy import signal
from scipy.io import wavfile

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
BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta": (13, 30),
    "Gamma": (38, 42),
}
Z_ON = -0.5
Z_OFF = 0.5
HYSTERESIS = 6.0
LOOKBACK = 20

# Max windows shown in time-series charts (last 60 = 2 min at 2s/window).
MAX_DISPLAY = 60

# Bandpass 0.5-45 Hz -- removes DC drift and high-freq noise from Muse 2.
_BP_SOS = signal.butter(4, [0.5, 45.0], btype="band", fs=FS, output="sos")

# ---------------------------------------------------------------------------
# Color palette -- muted, research-grade
# ---------------------------------------------------------------------------
CLR_SYNC = "#3B82F6"       # blue
CLR_PREDICTED = "#F59E0B"  # amber
CLR_STIM = "#10B981"       # teal-green
CLR_ZERO = "#6B7280"       # gray-500
CLR_EEG = ["#6366F1", "#EC4899", "#14B8A6", "#F97316"]  # indigo, pink, teal, orange
CLR_BAND = {
    "Delta": "#8B5CF6",
    "Theta": "#3B82F6",
    "Alpha": "#10B981",
    "Beta": "#F59E0B",
    "Gamma": "#EF4444",
}
PLOTLY_BG = "#FAFAFA"
PLOTLY_GRID = "#E5E7EB"

# Shared Plotly layout defaults for a clean research look.
_LAYOUT_BASE = dict(
    paper_bgcolor=PLOTLY_BG,
    plot_bgcolor=PLOTLY_BG,
    margin=dict(l=50, r=20, t=30, b=30),
    font=dict(family="Inter, system-ui, sans-serif", size=11, color="#374151"),
    xaxis=dict(gridcolor=PLOTLY_GRID, zeroline=False),
    yaxis=dict(gridcolor=PLOTLY_GRID, zeroline=False),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def _base_layout(**overrides: object) -> dict:
    """Return a copy of the shared layout with overrides applied."""
    layout = dict(_LAYOUT_BASE)
    layout.update(overrides)
    return layout


# ---------------------------------------------------------------------------
# Signal-processing helpers (unchanged from v3)
# ---------------------------------------------------------------------------
def _bandpass(eeg: np.ndarray) -> np.ndarray:
    """Bandpass filter (0.5-45 Hz) each channel. Returns filtered copy."""
    return signal.sosfiltfilt(_BP_SOS, eeg, axis=1).astype(np.float32)


def _band_powers(eeg: np.ndarray) -> Dict[str, float]:
    """Mean band power across channels via Welch PSD."""
    nperseg = min(256, eeg.shape[1])
    freqs, psd = signal.welch(eeg, fs=FS, nperseg=nperseg, axis=1)
    _trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    out: Dict[str, float] = {}
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
    """Z-score of current PAC relative to rolling 30-window baseline."""
    if len(history) < 10:
        return 0.0
    recent = np.array(history[-30:])
    s = float(recent.std())
    return (pac - float(recent.mean())) / s if s > 1e-12 else 0.0


def _pac_stim_features(
    pac_hist: List[float],
    stim: bool,
    t_switch: float,
    n_stim: int,
    step: int,
) -> np.ndarray:
    """Build 12-element PAC+stim feature vector for TCN input."""
    n = len(pac_hist)
    p = pac_hist[-1] if n > 0 else 0.0
    ma = lambda w: float(np.mean(pac_hist[-w:])) if n >= w else (
        float(np.mean(pac_hist)) if n > 0 else 0.0
    )
    diff = lambda lag: (pac_hist[-1] - pac_hist[-1 - lag]) if n > lag else 0.0
    sf = n_stim / max(1, step) if step > 0 else 0.0
    phase = step * 2.0 / 70.0 * 2 * np.pi
    return np.array(
        [p, ma(2), ma(4), ma(8), ma(16), diff(1), diff(4),
         1.0 if stim else 0.0, t_switch, sf,
         np.sin(phase), np.cos(phase)],
        dtype=np.float32,
    )


def _predicted_pac_display(
    pred_raw: float,
    train_mean: float,
    train_std: float,
    session_pac_hist: List[float],
) -> float:
    """Map TCN prediction (in training distribution) to the session's 0-100 scale.

    The TCN outputs denormalized PAC in the training distribution (~4e-5).
    Live Muse PAC values may occupy a different range. We convert the
    prediction into a z-score relative to training stats, then project that
    z-score into the session's live distribution so the display is comparable
    to Brain Sync.
    """
    if len(session_pac_hist) < 5:
        return 50.0
    # z-score in training space
    pred_z = (pred_raw - train_mean) / train_std if train_std > 1e-12 else 0.0
    # map to session space
    sess = np.array(session_pac_hist)
    sess_mean = float(sess.mean())
    sess_std = float(sess.std())
    if sess_std < 1e-12:
        return 50.0
    mapped = sess_mean + pred_z * sess_std
    return _pac_display(mapped, session_pac_hist)


# ---------------------------------------------------------------------------
# Audio generation (cached)
# ---------------------------------------------------------------------------
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
# Model loading (cached once per session)
# ---------------------------------------------------------------------------
@st.cache_resource
def _load_models():
    import torch
    from pac_computation import PACComputer
    from experimental.run_experiments import ImprovedTCN

    pac_comp = PACComputer(
        theta_band=(4, 8), gamma_band=(38, 42), fs=250, n_bins=18,
    )

    ckpt = torch.load(
        str(_ROOT / "models/muse_4ch/best_pac_stim_tcn_4ch.pth"),
        map_location="cpu",
        weights_only=False,
    )
    cfg = ckpt["config"]
    tcn = ImprovedTCN(
        n_features=cfg["n_features"],
        hidden=cfg["hidden"],
        kernel_size=cfg["kernel_size"],
        dilations=cfg["dilations"],
        dropout=cfg["dropout"],
        n_heads=cfg["n_heads"],
    )
    tcn.load_state_dict(ckpt["model_state_dict"])
    tcn.eval()

    feat_sc = np.load(str(_ROOT / "models/muse_4ch/pac_stim_feature_scalers.npz"))

    return pac_comp, tcn, ckpt["scalers"], feat_sc["mean"], feat_sc["std"]


# ---------------------------------------------------------------------------
# Plotly figure builders
# ---------------------------------------------------------------------------
def _fig_brain_sync(
    pac_disp: List[float],
    future_disp: List[Optional[float]],
) -> go.Figure:
    """Brain Sync + Predicted PAC on 0-100 fixed y-axis."""
    n = len(pac_disp)
    x = list(range(max(0, n - MAX_DISPLAY), n))
    y_sync = pac_disp[-MAX_DISPLAY:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y_sync, mode="lines",
        name="Brain Sync",
        line=dict(color=CLR_SYNC, width=2),
    ))

    # Predicted: filter out None values for a clean line
    fv = future_disp[-MAX_DISPLAY:]
    pred_x = [x[i] for i in range(len(fv)) if fv[i] is not None]
    pred_y = [v for v in fv if v is not None]
    if pred_x:
        fig.add_trace(go.Scatter(
            x=pred_x, y=pred_y, mode="lines",
            name="Predicted (5s)",
            line=dict(color=CLR_PREDICTED, width=2, dash="dash"),
        ))

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                range=[0, 100], dtick=25,
                gridcolor=PLOTLY_GRID, zeroline=False,
                title="PAC (0-100)",
            ),
            xaxis=dict(
                title="Window",
                gridcolor=PLOTLY_GRID, zeroline=False,
            ),
            height=260,
        ),
    )
    return fig


def _fig_band_powers(bands: Dict[str, List[float]]) -> go.Figure:
    """Band powers on log y-axis (powers span orders of magnitude)."""
    fig = go.Figure()
    for name, vals in bands.items():
        if len(vals) < 2:
            continue
        tail = vals[-MAX_DISPLAY:]
        n = len(vals)
        x = list(range(max(0, n - MAX_DISPLAY), n))
        fig.add_trace(go.Scatter(
            x=x, y=tail, mode="lines",
            name=name,
            line=dict(color=CLR_BAND.get(name, "#6B7280"), width=1.5),
        ))

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                type="log",
                gridcolor=PLOTLY_GRID, zeroline=False,
                title="Power (log)",
            ),
            xaxis=dict(title="Window", gridcolor=PLOTLY_GRID, zeroline=False),
            height=220,
        ),
    )
    return fig


def _fig_eeg(eeg: np.ndarray) -> go.Figure:
    """EEG traces for current window, y clipped to +/-300 uV."""
    t = np.arange(N_SAMP) / FS
    fig = go.Figure()
    for i, ch in enumerate(CH_NAMES):
        fig.add_trace(go.Scatter(
            x=t, y=eeg[i], mode="lines",
            name=ch,
            line=dict(color=CLR_EEG[i], width=1),
        ))

    # Clip y-axis to the current window range but no wider than +/-300
    eeg_min = max(-300.0, float(np.min(eeg)))
    eeg_max = min(300.0, float(np.max(eeg)))
    pad = max(5.0, (eeg_max - eeg_min) * 0.1)

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                range=[eeg_min - pad, eeg_max + pad],
                gridcolor=PLOTLY_GRID, zeroline=False,
                title="uV",
            ),
            xaxis=dict(
                title="Time (s)", range=[0, 2.0],
                gridcolor=PLOTLY_GRID, zeroline=False,
            ),
            height=260,
        ),
    )
    return fig


def _fig_stimulus(stim_hist: List[bool]) -> go.Figure:
    """Binary stimulus timeline, y fixed 0-1."""
    n = len(stim_hist)
    tail = stim_hist[-MAX_DISPLAY:]
    x = list(range(max(0, n - MAX_DISPLAY), n))
    y = [1.0 if s else 0.0 for s in tail]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        fill="tozeroy",
        name="Stimulus",
        line=dict(color=CLR_STIM, width=1.5),
        fillcolor="rgba(16, 185, 129, 0.25)",
    ))
    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                range=[-0.05, 1.15], dtick=1,
                tickvals=[0, 1], ticktext=["OFF", "ON"],
                gridcolor=PLOTLY_GRID, zeroline=False,
            ),
            xaxis=dict(title="Window", gridcolor=PLOTLY_GRID, zeroline=False),
            height=140,
            showlegend=False,
        ),
    )
    return fig


def _fig_zscore(z_hist: List[float]) -> go.Figure:
    """Z-score timeline, y fixed -3 to 3 with threshold lines."""
    n = len(z_hist)
    tail = z_hist[-MAX_DISPLAY:]
    x = list(range(max(0, n - MAX_DISPLAY), n))

    fig = go.Figure()
    # Zero line
    fig.add_hline(y=0, line=dict(color=CLR_ZERO, width=1, dash="dot"))
    # Threshold lines
    fig.add_hline(y=Z_ON, line=dict(color=CLR_STIM, width=1, dash="dash"),
                  annotation_text="STIM ON", annotation_position="bottom left")
    fig.add_hline(y=Z_OFF, line=dict(color="#EF4444", width=1, dash="dash"),
                  annotation_text="STIM OFF", annotation_position="top left")

    fig.add_trace(go.Scatter(
        x=x, y=tail, mode="lines",
        name="Z-Score",
        line=dict(color="#6366F1", width=2),
    ))

    fig.update_layout(
        **_base_layout(
            yaxis=dict(
                range=[-3, 3], dtick=1,
                gridcolor=PLOTLY_GRID, zeroline=False,
                title="Z",
            ),
            xaxis=dict(title="Window", gridcolor=PLOTLY_GRID, zeroline=False),
            height=180,
            showlegend=False,
        ),
    )
    return fig


# ---------------------------------------------------------------------------
# Session state management
# ---------------------------------------------------------------------------
def _init() -> None:
    """Connect to Muse 2 (or simulated adapter) and initialize session state."""
    from src.streaming.adapters import RealEEGAdapter

    pac_comp, tcn, tsc, fm, fs = _load_models()
    adapter = RealEEGAdapter()
    st.session_state.update({
        "running": True,
        "pac_comp": pac_comp,
        "tcn": tcn,
        "tsc": tsc,
        "fm": fm,
        "fs": fs,
        "adapter": adapter,
        "step": 0,
        "stim": False,
        "n_stim": 0,
        "n_rest": 0,
        "t_switch": 0.0,
        "pac_hist": [],
        "pac_disp": [],
        "future_disp": [],
        "z_hist": [],
        "bands": {b: [] for b in BANDS},
        "stim_hist": [],
        "log": [],
        "buf": [],
        "eeg": np.zeros((N_CH, N_SAMP), dtype=np.float32),
    })


def _cleanup() -> None:
    """Disconnect adapter and clear session state."""
    a = st.session_state.get("adapter")
    if a:
        try:
            a.close()
        except Exception:
            pass
    for k in list(st.session_state.keys()):
        if k != "page":
            st.session_state.pop(k, None)


# ---------------------------------------------------------------------------
# Live acquisition + inference (runs as a fragment -- no full page rerun)
# ---------------------------------------------------------------------------
@st.fragment(run_every=2.0)
def _live_loop() -> None:
    """Acquire one EEG window, run inference, update charts in-place."""
    import torch

    S = st.session_state
    if not S.get("running"):
        return

    adapter = S["adapter"]
    step = S["step"]

    # --- Acquire EEG ---
    eeg_raw = adapter.get_window()  # (4, 500)
    eeg = _bandpass(eeg_raw)
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
    feat = _pac_stim_features(
        S["pac_hist"], S["stim"], S["t_switch"], S["n_stim"], step,
    )
    S["buf"].append(feat)
    if len(S["buf"]) > LOOKBACK:
        S["buf"] = S["buf"][-LOOKBACK:]

    fut_disp: Optional[float] = None
    has_pred = False
    if len(S["buf"]) >= LOOKBACK:
        seq = np.stack(S["buf"][-LOOKBACK:])
        seq_n = (seq - S["fm"]) / (S["fs"] + 1e-12)
        with torch.no_grad():
            pn = S["tcn"](
                torch.from_numpy(seq_n[None].astype(np.float32))
            ).item()
        # Denormalize from training z-space to raw PAC
        train_mean = float(S["tsc"]["y_future_mean"])
        train_std = float(S["tsc"]["y_future_std"])
        fut_pac_raw = pn * train_std + train_mean

        # Map to session's 0-100 scale via training-distribution z-score
        fut_disp = _predicted_pac_display(
            fut_pac_raw, train_mean, train_std, S["pac_hist"],
        )
        has_pred = True
    S["future_disp"].append(fut_disp)

    # --- Stimulus decision ---
    prev = S["stim"]
    stim = prev
    reason = f"warmup ({step + 1}/{LOOKBACK})"

    if step >= LOOKBACK and has_pred:
        can = S["t_switch"] >= HYSTERESIS
        if prev:
            if z > Z_OFF and can:
                stim = False
                reason = f"z={z:.2f}>{Z_OFF} -> REST"
            else:
                reason = f"STIM hold (z={z:.2f})"
        else:
            if z < Z_ON and can:
                stim = True
                reason = f"z={z:.2f}<{Z_ON} -> STIM"
            else:
                reason = f"REST hold (z={z:.2f})"

    S["stim_hist"].append(stim)
    S["log"].append(reason)
    S["step"] += 1
    if stim:
        S["n_stim"] += 1
    else:
        S["n_rest"] += 1
    if stim != prev:
        S["t_switch"] = 0.0
    else:
        S["t_switch"] += 2.0
    S["stim"] = stim

    # =================================================================
    # RENDER -- all Plotly with key= for in-place updates
    # =================================================================
    step_now = S["step"]

    # Status bar
    if step_now <= LOOKBACK:
        st.progress(
            step_now / LOOKBACK,
            text=f"Warming up... ({step_now}/{LOOKBACK})",
        )
    else:
        st.markdown(
            '<div style="padding:6px 12px;background:#D1FAE5;border-radius:4px;'
            'color:#065F46;font-weight:500;">Closed-loop active</div>',
            unsafe_allow_html=True,
        )

    # Metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Brain Sync", f"{disp:.0f}/100")
    stim_label = "STIM" if stim else "REST"
    stim_color = "#10B981" if stim else "#6B7280"
    m2.markdown(
        f'<div style="font-size:1.4rem;font-weight:700;color:{stim_color};">'
        f'{stim_label}</div>',
        unsafe_allow_html=True,
    )
    therapy_pct = S["n_stim"] / max(1, step_now) * 100
    m3.metric("Therapy %", f"{therapy_pct:.0f}%")
    m4.metric(
        "Predicted",
        f"{fut_disp:.0f}/100" if fut_disp is not None else "--",
    )
    m5.metric("Windows", step_now)

    # Audio
    if stim:
        st.audio(
            _make_wav(st.session_state.get("_vol", 0.3)),
            format="audio/wav",
            loop=True,
            autoplay=True,
        )

    # --- Charts ---
    left, right = st.columns(2)

    with left:
        st.markdown("**Brain Sync Level**")
        st.plotly_chart(
            _fig_brain_sync(S["pac_disp"], S["future_disp"]),
            use_container_width=True,
            key="chart_sync",
        )

        st.markdown("**Band Powers**")
        st.plotly_chart(
            _fig_band_powers(S["bands"]),
            use_container_width=True,
            key="chart_bands",
        )

    with right:
        st.markdown("**EEG (filtered 0.5-45 Hz)**")
        st.plotly_chart(
            _fig_eeg(S["eeg"]),
            use_container_width=True,
            key="chart_eeg",
        )

        st.markdown("**Stimulus Timeline**")
        if len(S["stim_hist"]) > 1:
            st.plotly_chart(
                _fig_stimulus(S["stim_hist"]),
                use_container_width=True,
                key="chart_stim",
            )

        st.markdown("**Session Z-Score**")
        if len(S["z_hist"]) > 1:
            st.plotly_chart(
                _fig_zscore(S["z_hist"]),
                use_container_width=True,
                key="chart_zscore",
            )

    # Decision log
    with st.expander("Decision Log", expanded=False):
        log_slice = S["log"][-10:]
        stim_slice = S["stim_hist"][-10:]
        for i, entry in enumerate(reversed(log_slice)):
            sn = step_now - i
            tag = "[STIM]" if stim_slice[-(i + 1)] else "[REST]"
            st.text(f"{tag} #{sn}: {entry}")


# ---------------------------------------------------------------------------
# Main page (renders once, fragment handles live updates)
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(
        page_title="NeuroCare Live",
        layout="wide",
    )

    # Sidebar
    with st.sidebar:
        st.markdown("**NeuroCare** v4.0")
        st.divider()
        if st.session_state.get("running"):
            st.success("Muse 2 Connected")
        else:
            st.info("Muse 2 (disconnected)")
        st.caption("4ch: TP9 / AF7 / AF8 / TP10")
        st.divider()
        vol = st.slider("Stimulus Volume", 0.0, 1.0, 0.3, 0.05)
        st.session_state["_vol"] = vol
        st.divider()
        st.caption("PAC: Direct MI (Tort 2010)")
        st.caption("TCN: PAC+Stim (6.3K params)")
        st.caption("Test R2: 0.40 | Horizon: 5s")
        st.caption(f"Stim: z<{Z_ON} ON, z>{Z_OFF} OFF")

    st.title("NeuroCare 40Hz -- Live Mission Control")

    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        go_btn = st.button(
            "Connect",
            type="primary",
            disabled=st.session_state.get("running", False),
        )
    with c2:
        stop_btn = st.button(
            "Stop",
            disabled=not st.session_state.get("running", False),
        )

    if go_btn and not st.session_state.get("running"):
        with st.spinner("Connecting to Muse 2..."):
            try:
                _init()
                st.rerun()
            except Exception as e:
                st.error(f"Connection failed: {e}")
                return

    if stop_btn and st.session_state.get("running"):
        _cleanup()
        st.rerun()

    if not st.session_state.get("running"):
        st.info(
            "Turn on Muse 2 (hold power until LEDs blink), then click Connect."
        )
        return

    # Hand off to the fragment -- this runs every 2s without full page rerun.
    _live_loop()


if __name__ == "__main__":
    main()
