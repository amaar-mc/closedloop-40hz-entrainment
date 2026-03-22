"""
NeuroCare 40Hz -- Live Mission Control v5

Uses st.empty() placeholders for flicker-free chart updates.
No st.rerun(), no st.fragment() -- a while loop with adapter.get_window()
providing natural 2s pacing. Charts update in-place via placeholder.plotly_chart().

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
BANDS = {"Delta": (1, 4), "Theta": (4, 8), "Alpha": (8, 13),
         "Beta": (13, 30), "Gamma": (38, 42)}
Z_ON, Z_OFF, HYSTERESIS, LOOKBACK = -0.5, 0.5, 6.0, 20
MAX_DISP = 60
_BP_SOS = signal.butter(4, [0.5, 45.0], btype="band", fs=FS, output="sos")

# Colors
C_SYNC, C_PRED, C_STIM = "#3B82F6", "#F59E0B", "#10B981"
C_EEG = ["#6366F1", "#EC4899", "#14B8A6", "#F97316"]
C_BAND = {"Delta": "#8B5CF6", "Theta": "#3B82F6", "Alpha": "#10B981",
           "Beta": "#F59E0B", "Gamma": "#EF4444"}
BG, GRID = "#FAFAFA", "#E5E7EB"

_LO = dict(paper_bgcolor=BG, plot_bgcolor=BG,
           margin=dict(l=50, r=10, t=10, b=35),
           font=dict(size=11, color="#374151"),
           legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"))


# ---------------------------------------------------------------------------
# Signal processing
# ---------------------------------------------------------------------------
def _bp(eeg):
    return signal.sosfiltfilt(_BP_SOS, eeg, axis=1).astype(np.float32)

def _bpow(eeg):
    nperseg = min(256, eeg.shape[1])
    f, p = signal.welch(eeg, fs=FS, nperseg=nperseg, axis=1)
    tr = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return {n: float(tr(p[:, (f >= lo) & (f <= hi)], f[(f >= lo) & (f <= hi)], axis=1).mean())
            for n, (lo, hi) in BANDS.items()}

def _pac_disp(pac, hist):
    if len(hist) < 5: return 50.0
    a = np.array(hist)
    p5, p95 = float(np.percentile(a, 5)), float(np.percentile(a, 95))
    if p95 - p5 < 1e-12: return 50.0
    return round(max(0, min(100, (pac - p5) / (p95 - p5) * 100)), 1)

def _pred_disp(pred_raw, tr_mean, tr_std, hist):
    if len(hist) < 5: return 50.0
    pz = (pred_raw - tr_mean) / tr_std if tr_std > 1e-12 else 0.0
    s = np.array(hist)
    sm, ss = float(s.mean()), float(s.std())
    if ss < 1e-12: return 50.0
    return _pac_disp(sm + pz * ss, hist)

def _zscore(pac, hist):
    if len(hist) < 10: return 0.0
    r = np.array(hist[-30:])
    s = float(r.std())
    return (pac - float(r.mean())) / s if s > 1e-12 else 0.0

def _feats(ph, stim, tsw, ns, step):
    n = len(ph)
    p = ph[-1] if n > 0 else 0.0
    ma = lambda w: float(np.mean(ph[-w:])) if n >= w else (float(np.mean(ph)) if n > 0 else 0.0)
    df = lambda l: (ph[-1] - ph[-1 - l]) if n > l else 0.0
    sf = ns / max(1, step) if step > 0 else 0.0
    ph2 = step * 2 / 70 * 2 * np.pi
    return np.array([p, ma(2), ma(4), ma(8), ma(16), df(1), df(4),
                      1.0 if stim else 0.0, tsw, sf,
                      np.sin(ph2), np.cos(ph2)], dtype=np.float32)


# ---------------------------------------------------------------------------
# Plotly figure builders
# ---------------------------------------------------------------------------
def _fig_sync(pd_list, fd_list):
    n = len(pd_list)
    x = list(range(max(0, n - MAX_DISP), n))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=pd_list[-MAX_DISP:], mode="lines",
                              name="Brain Sync", line=dict(color=C_SYNC, width=2)))
    fv = fd_list[-MAX_DISP:]
    px = [x[i] for i in range(len(fv)) if fv[i] is not None]
    py = [v for v in fv if v is not None]
    if px:
        fig.add_trace(go.Scatter(x=px, y=py, mode="lines", name="Predicted (5s)",
                                  line=dict(color=C_PRED, width=2, dash="dash")))
    fig.update_layout(**_LO, height=240,
                       yaxis=dict(range=[0, 100], dtick=25, gridcolor=GRID, title="PAC (0-100)"),
                       xaxis=dict(gridcolor=GRID, title="Window"))
    return fig

def _fig_bands(bands):
    fig = go.Figure()
    for name, vals in bands.items():
        if len(vals) < 2: continue
        n = len(vals)
        fig.add_trace(go.Scatter(
            x=list(range(max(0, n - MAX_DISP), n)), y=vals[-MAX_DISP:],
            mode="lines", name=name, line=dict(color=C_BAND.get(name, "#999"), width=1.5)))
    fig.update_layout(**_LO, height=200,
                       yaxis=dict(type="log", gridcolor=GRID, title="Power (log)"),
                       xaxis=dict(gridcolor=GRID, title="Window"))
    return fig

def _fig_eeg(eeg):
    t = np.arange(N_SAMP) / FS
    fig = go.Figure()
    for i, ch in enumerate(CH_NAMES):
        fig.add_trace(go.Scatter(x=t, y=eeg[i], mode="lines", name=ch,
                                  line=dict(color=C_EEG[i], width=1)))
    mn, mx = max(-300, float(eeg.min())), min(300, float(eeg.max()))
    pad = max(5, (mx - mn) * 0.1)
    fig.update_layout(**_LO, height=240,
                       yaxis=dict(range=[mn - pad, mx + pad], gridcolor=GRID, title="uV"),
                       xaxis=dict(range=[0, 2], gridcolor=GRID, title="Time (s)"))
    return fig

def _fig_stim(hist):
    n = len(hist)
    x = list(range(max(0, n - MAX_DISP), n))
    y = [1.0 if s else 0.0 for s in hist[-MAX_DISP:]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, fill="tozeroy", mode="lines",
                              line=dict(color=C_STIM, width=1.5),
                              fillcolor="rgba(16,185,129,0.2)"))
    fig.update_layout(**_LO, height=120, showlegend=False,
                       yaxis=dict(range=[-0.05, 1.15], tickvals=[0, 1],
                                   ticktext=["OFF", "ON"], gridcolor=GRID),
                       xaxis=dict(gridcolor=GRID, title="Window"))
    return fig

def _fig_z(hist):
    n = len(hist)
    x = list(range(max(0, n - MAX_DISP), n))
    fig = go.Figure()
    fig.add_hline(y=0, line=dict(color="#9CA3AF", width=1, dash="dot"))
    fig.add_hline(y=Z_ON, line=dict(color=C_STIM, width=1, dash="dash"))
    fig.add_hline(y=Z_OFF, line=dict(color="#EF4444", width=1, dash="dash"))
    fig.add_trace(go.Scatter(x=x, y=hist[-MAX_DISP:], mode="lines",
                              line=dict(color="#6366F1", width=2)))
    fig.update_layout(**_LO, height=160, showlegend=False,
                       yaxis=dict(range=[-3, 3], dtick=1, gridcolor=GRID, title="Z"),
                       xaxis=dict(gridcolor=GRID, title="Window"))
    return fig


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------
@st.cache_data
def _wav(vol=0.3):
    sr = 44100
    per = sr // 40
    cn = int(0.001 * sr)
    b = np.zeros(per, dtype=np.float32)
    b[:cn] = vol * np.sin(2 * np.pi * 1000 * np.arange(cn, dtype=np.float32) / sr)
    audio = np.tile(np.tile(b, 40), 30).astype(np.float32)
    o = io.BytesIO()
    wavfile.write(o, sr, audio)
    return o.getvalue()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
@st.cache_resource
def _load():
    import torch
    from pac_computation import PACComputer
    from experimental.run_experiments import ImprovedTCN
    pc = PACComputer(theta_band=(4, 8), gamma_band=(38, 42), fs=250, n_bins=18)
    ck = torch.load(str(_ROOT / "models/muse_4ch/best_pac_stim_tcn_4ch.pth"),
                     map_location="cpu", weights_only=False)
    c = ck["config"]
    tcn = ImprovedTCN(n_features=c["n_features"], hidden=c["hidden"],
                       kernel_size=c["kernel_size"], dilations=c["dilations"],
                       dropout=c["dropout"], n_heads=c["n_heads"])
    tcn.load_state_dict(ck["model_state_dict"])
    tcn.eval()
    fs = np.load(str(_ROOT / "models/muse_4ch/pac_stim_feature_scalers.npz"))
    return pc, tcn, ck["scalers"], fs["mean"], fs["std"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="NeuroCare Live", layout="wide")

    # Sidebar (renders once)
    with st.sidebar:
        st.markdown("**NeuroCare** v5.0")
        st.divider()
        st.caption("4ch: TP9 / AF7 / AF8 / TP10")
        st.divider()
        vol = st.slider("Stimulus Volume", 0.0, 1.0, 0.3, 0.05)
        st.divider()
        st.caption("PAC: Direct MI (Tort 2010)")
        st.caption("TCN: PAC+Stim (6.3K params)")
        st.caption("Test R2: 0.40 | Horizon: 5s")

    st.title("NeuroCare 40Hz -- Live Mission Control")

    # Connect button
    if not st.session_state.get("running"):
        if st.button("Connect to Muse 2", type="primary"):
            from src.streaming.adapters import RealEEGAdapter
            with st.spinner("Connecting..."):
                try:
                    pc, tcn, tsc, fm, fs = _load()
                    adapter = RealEEGAdapter()
                    st.session_state.update({
                        "running": True, "pc": pc, "tcn": tcn, "tsc": tsc,
                        "fm": fm, "fs": fs, "adapter": adapter,
                        "step": 0, "stim": False, "n_stim": 0, "n_rest": 0,
                        "tsw": 0.0, "ph": [], "pd": [], "fd": [], "zh": [],
                        "bands": {b: [] for b in BANDS}, "sh": [], "log": [], "buf": [],
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")
                    return
        st.info("Turn on Muse 2 (hold power until LEDs blink), then click Connect.")
        return

    # === CREATE LAYOUT ONCE ===
    status_ph = st.empty()
    m1, m2, m3, m4, m5 = st.columns(5)
    ph_sync_metric = m1.empty()
    ph_stim_label = m2.empty()
    ph_therapy = m3.empty()
    ph_pred = m4.empty()
    ph_windows = m5.empty()
    audio_ph = st.empty()

    left, right = st.columns(2)
    with left:
        st.markdown("**Brain Sync Level**")
        ph_sync_chart = st.empty()
        st.markdown("**Band Powers**")
        ph_band_chart = st.empty()
    with right:
        st.markdown("**EEG (filtered 0.5-45 Hz)**")
        ph_eeg_chart = st.empty()
        st.markdown("**Stimulus Timeline**")
        ph_stim_chart = st.empty()
        st.markdown("**Session Z-Score**")
        ph_z_chart = st.empty()

    ph_log = st.expander("Decision Log", expanded=False)

    # === LIVE LOOP ===
    import torch
    S = st.session_state

    while S.get("running", False):
        adapter = S["adapter"]
        step = S["step"]

        # Acquire (blocks 2s)
        eeg = _bp(adapter.get_window())

        # Band powers
        bp = _bpow(eeg)
        for b in BANDS:
            S["bands"][b].append(bp[b])

        # PAC
        pac = S["pc"].compute_pac_average(eeg)
        S["ph"].append(pac)
        disp = _pac_disp(pac, S["ph"])
        S["pd"].append(disp)
        z = _zscore(pac, S["ph"])
        S["zh"].append(z)

        # TCN
        feat = _feats(S["ph"], S["stim"], S["tsw"], S["n_stim"], step)
        S["buf"].append(feat)
        if len(S["buf"]) > LOOKBACK:
            S["buf"] = S["buf"][-LOOKBACK:]

        fd = None
        has_pred = False
        if len(S["buf"]) >= LOOKBACK:
            seq = np.stack(S["buf"][-LOOKBACK:])
            seq_n = (seq - S["fm"]) / (S["fs"] + 1e-12)
            with torch.no_grad():
                pn = S["tcn"](torch.from_numpy(seq_n[None].astype(np.float32))).item()
            tm = float(S["tsc"]["y_future_mean"])
            ts = float(S["tsc"]["y_future_std"])
            fd = _pred_disp(pn * ts + tm, tm, ts, S["ph"])
            has_pred = True
        S["fd"].append(fd)

        # Decision
        prev = S["stim"]
        stim = prev
        reason = f"warmup ({step+1}/{LOOKBACK})"
        if step >= LOOKBACK and has_pred:
            can = S["tsw"] >= HYSTERESIS
            if prev:
                if z > Z_OFF and can:
                    stim = False; reason = f"z={z:.2f}>{Z_OFF} REST"
                else:
                    reason = f"STIM hold (z={z:.2f})"
            else:
                if z < Z_ON and can:
                    stim = True; reason = f"z={z:.2f}<{Z_ON} STIM"
                else:
                    reason = f"REST hold (z={z:.2f})"

        S["sh"].append(stim)
        S["log"].append(reason)
        S["step"] += 1
        if stim: S["n_stim"] += 1
        else: S["n_rest"] += 1
        if stim != prev: S["tsw"] = 0.0
        else: S["tsw"] += 2.0
        S["stim"] = stim
        sn = S["step"]

        # === UPDATE PLACEHOLDERS IN-PLACE ===
        if sn <= LOOKBACK:
            status_ph.progress(sn / LOOKBACK, text=f"Warming up... ({sn}/{LOOKBACK})")
        else:
            status_ph.success("Closed-loop active")

        ph_sync_metric.metric("Brain Sync", f"{disp:.0f}/100")
        color = "#10B981" if stim else "#6B7280"
        label = "STIM" if stim else "REST"
        ph_stim_label.markdown(f'<p style="font-size:1.4rem;font-weight:700;color:{color}">{label}</p>',
                                unsafe_allow_html=True)
        ph_therapy.metric("Therapy %", f"{S['n_stim']/max(1,sn)*100:.0f}%")
        ph_pred.metric("Predicted", f"{fd:.0f}/100" if fd is not None else "--")
        ph_windows.metric("Windows", sn)

        # Audio: only update on state CHANGE to avoid duplicate ID and reduce render load
        if stim and not prev:
            audio_ph.audio(_wav(vol), format="audio/wav", loop=True, autoplay=True,
                           key=f"audio_{sn}")
        elif not stim and prev:
            audio_ph.empty()

        # Render charts — placeholders handle in-place updates, no key needed
        ph_sync_chart.plotly_chart(_fig_sync(S["pd"], S["fd"]),
                                    use_container_width=True)
        ph_eeg_chart.plotly_chart(_fig_eeg(eeg),
                                   use_container_width=True)
        # Update secondary charts less frequently (every 3 steps) to reduce render load
        if sn % 3 == 0 or sn <= LOOKBACK + 1:
            ph_band_chart.plotly_chart(_fig_bands(S["bands"]),
                                        use_container_width=True)
            ph_stim_chart.plotly_chart(_fig_stim(S["sh"]),
                                        use_container_width=True)
            ph_z_chart.plotly_chart(_fig_z(S["zh"]),
                                     use_container_width=True)

        with ph_log:
            for i, entry in enumerate(reversed(S["log"][-8:])):
                tag = "[STIM]" if S["sh"][-(i+1)] else "[REST]"
                st.text(f"{tag} #{sn-i}: {entry}")


if __name__ == "__main__":
    main()
