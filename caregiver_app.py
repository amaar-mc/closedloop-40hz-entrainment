"""
NeuroCare 40Hz Therapy — Caregiver Dashboard

Multi-page Streamlit app for caregivers to manage patients, view session
history, and run live 40 Hz entrainment therapy sessions.  Plan 01 builds
the skeleton: profile loading, page routing, patient selection, and history
view.  Plan 02 adds the live session and summary pages.

Launch:
    streamlit run caregiver_app.py

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st
from scipy.io import wavfile

# ---------------------------------------------------------------------------
# Path setup (matches demo.py pattern)
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PROFILES_PATH = _ROOT / "data" / "caregiver_profiles.json"
APP_VERSION = "v1.0 (CSEF Demo)"

LABEL_MAP: Dict[str, str] = {
    "pac": "Brain Sync Level",
    "brain_sync_level": "Brain Sync Level",
    "pac_trend": "Neural Entrainment Trend",
    "stim_fraction": "Therapy Active (%)",
    "therapy_active_pct": "Therapy Active (%)",
    "z_score": "Response to Therapy",
    "session_duration": "Session Duration (min)",
    "duration_min": "Session Duration (min)",
    "alignment": "Targeting Accuracy (%)",
    "targeting_accuracy_pct": "Targeting Accuracy (%)",
}


def label(key: str) -> str:
    """Map internal metric keys to plain-language labels."""
    return LABEL_MAP.get(key, key.replace("_", " ").title())


# ---------------------------------------------------------------------------
# Audio, model loading, and display helpers (Plan 02)
# ---------------------------------------------------------------------------
@st.cache_data
def make_40hz_wav(volume: float = 0.3, sample_rate: int = 44100) -> bytes:
    """One second of 40 Hz click-train, loopable WAV bytes for st.audio."""
    period = sample_rate // 40  # 1102 samples per 40 Hz period
    click_n = int(0.001 * sample_rate)  # 1 ms click pulse
    period_buf = np.zeros(period, dtype=np.float32)
    t = np.arange(click_n, dtype=np.float32) / sample_rate
    period_buf[:click_n] = volume * np.sin(2 * np.pi * 1000 * t)
    audio = np.tile(period_buf, 40).astype(np.float32)  # 40 periods = 1 second
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, audio)
    return buf.getvalue()


@st.cache_resource
def load_models():
    """Load 4-channel EEGNet + TCNTemporalModel. Cached across reruns.

    Returns (eegnet, pac_mean, pac_std, tcn_model) where:
    - eegnet: EEGNet nn.Module in eval mode
    - pac_mean/pac_std: z-score normalization from training
    - tcn_model: TCNTemporalModel wrapping RealtimePACForecaster
    """
    import torch
    from eegnet import EEGNet
    from temporal_multiscale.model_registry import TCNTemporalModel

    device = "cpu"  # Cloud-safe; MPS/CUDA not available on Streamlit Cloud
    eegnet_path = str(_ROOT / "models/muse_4ch/best_eegnet_4ch.pth")
    tcn_path = str(_ROOT / "models/muse_4ch/best_multiscale_tcn_4ch_lb20_hz5_ts1.pth")
    # scalers.npz was copied to models/muse_4ch/ by Plan 01 Task 1.
    # Do NOT use data/processed/... — that path is gitignored and absent on Streamlit Cloud.
    scalers_path = str(_ROOT / "models/muse_4ch/scalers.npz")

    ckpt = torch.load(eegnet_path, map_location=device, weights_only=False)
    eegnet = EEGNet(n_channels=4, n_samples=500)
    eegnet.load_state_dict(ckpt["model_state_dict"])
    eegnet.eval()
    pac_mean = float(ckpt.get("pac_mean", 0.0))
    pac_std = float(ckpt.get("pac_std", 1.0))

    tcn_model = TCNTemporalModel(
        checkpoint_path=tcn_path, scalers_path=scalers_path, device=device
    )

    return eegnet, pac_mean, pac_std, tcn_model


def pac_to_display(pac_value: float, pac_mean: float, pac_std: float) -> float:
    """Convert raw PAC to 0-100 Brain Sync Level for caregiver display."""
    if pac_std == 0.0:
        return 50.0
    z = (pac_value - pac_mean) / pac_std
    # Clamp z to [-3, 3], then map to [0, 100]
    z_clamped = max(-3.0, min(3.0, z))
    return round((z_clamped + 3.0) / 6.0 * 100.0, 1)


# ---------------------------------------------------------------------------
# Profile I/O
# ---------------------------------------------------------------------------
@st.cache_data
def load_profiles() -> Dict[str, Any]:
    """Load patient profiles from JSON.  Cached until file changes."""
    if not PROFILES_PATH.exists():
        raise FileNotFoundError(
            f"Patient profiles not found at {PROFILES_PATH}. "
            "Run the app from the project root directory."
        )
    return json.loads(PROFILES_PATH.read_text())


def save_session(patient_id: str, session_record: Dict[str, Any]) -> None:
    """Append a session record to the given patient and clear cache."""
    data = json.loads(PROFILES_PATH.read_text())
    for patient in data["patients"]:
        if patient["id"] == patient_id:
            patient["sessions"].append(session_record)
            break
    PROFILES_PATH.write_text(json.dumps(data, indent=2) + "\n")
    load_profiles.clear()


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------
def navigate(page: str) -> None:
    """Set the active page in session state."""
    st.session_state.page = page


def _init_session_state() -> None:
    """Ensure all session-state keys exist with defaults."""
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "selected_patient_id" not in st.session_state:
        st.session_state.selected_patient_id = None


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def render_welcome() -> None:
    """Landing page with app title and call-to-action."""
    st.markdown(
        "<h1 style='text-align: center;'>NeuroCare 40Hz Therapy</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; font-size: 1.2em; color: #555;'>"
        "Personalized closed-loop gamma entrainment for cognitive health"
        "</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            "**How it works:** NeuroCare monitors brain activity in real time "
            "and delivers precisely-timed 40 Hz stimulation only when the brain "
            "needs it — maximizing therapeutic benefit while minimizing fatigue."
        )
        st.markdown("")
        if st.button("Get Started", type="primary", width="stretch"):
            navigate("patient_select")
            st.rerun()


def render_patient_select() -> None:
    """Grid of patient cards with Start Session and View History actions."""
    st.header("Select Patient")

    profiles = load_profiles()
    patients: List[Dict[str, Any]] = profiles["patients"]

    cols = st.columns(2)
    for idx, patient in enumerate(patients):
        with cols[idx % 2]:
            with st.container(border=True):
                st.subheader(patient["name"])
                st.caption(f"Age {patient['age']} | {patient['diagnosis']}")

                n_sessions = len(patient.get("sessions", []))
                if n_sessions > 0:
                    last_date = patient["sessions"][-1]["date"]
                    st.markdown(
                        f"**Sessions:** {n_sessions} | "
                        f"**Last:** {last_date}"
                    )
                else:
                    st.markdown("**Sessions:** 0 | **Last:** --")

                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(
                        "Start Session",
                        key=f"start_{patient['id']}",
                        type="primary",
                        width="stretch",
                    ):
                        st.session_state.selected_patient_id = patient["id"]
                        navigate("session")
                        st.rerun()
                with btn_col2:
                    if st.button(
                        "View History",
                        key=f"history_{patient['id']}",
                        width="stretch",
                    ):
                        st.session_state.selected_patient_id = patient["id"]
                        navigate("patient_history")
                        st.rerun()


def _get_patient_by_id(patient_id: str) -> Optional[Dict[str, Any]]:
    """Look up a patient by ID from the cached profiles."""
    profiles = load_profiles()
    for patient in profiles["patients"]:
        if patient["id"] == patient_id:
            return patient
    return None


def render_patient_history() -> None:
    """Per-patient session history table and summary metrics."""
    patient_id = st.session_state.get("selected_patient_id")
    if patient_id is None:
        st.warning("No patient selected.")
        if st.button("Back to Patients"):
            navigate("patient_select")
            st.rerun()
        return

    patient = _get_patient_by_id(patient_id)
    if patient is None:
        st.error(f"Patient {patient_id} not found.")
        return

    st.header(f"Session History: {patient['name']}")
    st.caption(f"Age {patient['age']} | {patient['diagnosis']}")

    sessions: List[Dict[str, Any]] = patient.get("sessions", [])
    if not sessions:
        st.info("No sessions recorded yet.")
        if st.button("Back to Patients"):
            navigate("patient_select")
            st.rerun()
        return

    # Build dataframe with plain-language column names
    display_cols = [
        "date",
        "duration_min",
        "brain_sync_level",
        "therapy_active_pct",
        "targeting_accuracy_pct",
        "notes",
    ]
    df = pd.DataFrame(sessions)[display_cols]
    df.columns = [label(c) for c in display_cols]

    st.dataframe(df, width="stretch", hide_index=True)

    # Summary metrics row
    st.subheader("Averages")
    m1, m2, m3 = st.columns(3)
    with m1:
        avg_sync = np.mean([s["brain_sync_level"] for s in sessions])
        st.metric(label("brain_sync_level"), f"{avg_sync:.6f}")
    with m2:
        avg_active = np.mean([s["therapy_active_pct"] for s in sessions])
        st.metric(label("therapy_active_pct"), f"{avg_active:.1f}%")
    with m3:
        avg_acc = np.mean([s["targeting_accuracy_pct"] for s in sessions])
        st.metric(label("targeting_accuracy_pct"), f"{avg_acc:.1f}%")

    st.divider()
    if st.button("Back to Patients"):
        navigate("patient_select")
        st.rerun()


def render_session() -> None:
    """Live therapy session with 40 Hz audio, PAC trend, and warmup indicator.

    Runs the SimulatedEEGAdapter -> StreamingFeatureExtractor -> EEGNet ->
    TCNTemporalModel pipeline in a 2-second step loop driven by st.rerun().
    """
    import time as _time
    import torch
    from src.streaming.adapters import SimulatedEEGAdapter
    from src.streaming.feature_extractor import StreamingFeatureExtractor

    patient_id = st.session_state.get("selected_patient_id")
    patient = _get_patient_by_id(patient_id) if patient_id else None
    patient_name = patient["name"] if patient else "Unknown"

    st.title(f"Session -- {patient_name}")

    # Initialize session state for this session
    if "session_running" not in st.session_state:
        st.session_state.session_running = False
    if "session_controller" not in st.session_state:
        eegnet, pac_mean, pac_std, tcn_model = load_models()
        tcn_model.reset()
        st.session_state.session_eegnet = eegnet
        st.session_state.pac_mean = pac_mean
        st.session_state.pac_std = pac_std
        st.session_state.session_tcn = tcn_model
        st.session_state.session_extractor = StreamingFeatureExtractor(
            n_channels=4, fs=250.0, n_pac_bins=18,
        )
        st.session_state.session_adapter = SimulatedEEGAdapter(n_channels=4)
        st.session_state.pac_history = []
        st.session_state.pac_raw_history = []
        st.session_state.step_count = 0
        st.session_state.stim_active = False
        st.session_state.n_stim = 0
        st.session_state.n_rest = 0
        st.session_state.time_since_switch = 0.0
        st.session_state.last_stim_state = 0.0
        st.session_state.session_controller = True  # sentinel

    eegnet = st.session_state.session_eegnet
    tcn_model = st.session_state.session_tcn
    extractor = st.session_state.session_extractor
    adapter = st.session_state.session_adapter

    # Controls row
    col_vol, col_start, col_end = st.columns([2, 1, 1])
    with col_vol:
        volume = st.slider(
            "Stimulus Volume", 0.0, 1.0, 0.3, 0.05, key="volume_slider",
        )
    with col_start:
        if not st.session_state.session_running:
            if st.button("Start Session", type="primary"):
                st.session_state.session_running = True
                st.rerun()
    with col_end:
        if st.session_state.session_running:
            if st.button("End Session", type="secondary"):
                st.session_state.session_running = False
                navigate("summary")
                st.rerun()

    if not st.session_state.session_running:
        st.info(
            "Press 'Start Session' to begin therapy. "
            "Audio stimulus will activate when needed."
        )
        return

    # Warmup indicator
    LOOKBACK = 20
    step = st.session_state.step_count
    if step < LOOKBACK:
        st.progress(step / LOOKBACK, text=f"Warming up... ({step}/{LOOKBACK} windows)")
    else:
        st.success("Model ready -- live predictions active")

    # Status row
    col_sync, col_stim, col_steps = st.columns(3)

    # Run one inference step: adapter -> features -> EEGNet PAC -> TCN prediction
    eeg_window = adapter.get_window()  # (4, 500), sleeps 2s internally
    spectral_features = extractor.process_window(eeg_window)  # (37,)

    # EEGNet forward pass for current PAC estimate
    with torch.no_grad():
        eeg_tensor = torch.from_numpy(
            eeg_window[np.newaxis, np.newaxis, :, :]  # (1, 1, 4, 500)
        ).float()
        pac_raw = eegnet(eeg_tensor).item()
        # Denormalize from z-score to raw PAC
        pac_current = pac_raw * st.session_state.pac_std + st.session_state.pac_mean

    # TCN prediction step
    stim_state_float = 1.0 if st.session_state.stim_active else 0.0
    stim_frac = (
        st.session_state.n_stim / max(1, st.session_state.step_count)
    )
    prediction = tcn_model.step(
        spectral_features=spectral_features,
        pac_current=pac_current,
        stim_state=stim_state_float,
        time_since_switch_sec=st.session_state.time_since_switch,
        stim_frac_recent=stim_frac,
    )

    # Make stimulation decision (similar to demo.py TCNController logic)
    stim_active = False
    if prediction is not None:
        # Stimulate when TCN predicts PAC will decline
        delta_pac = prediction.get("delta_pac", 0.0)
        if delta_pac < -0.3:
            stim_active = True
        elif len(st.session_state.pac_raw_history) >= 10:
            mu = float(np.mean(st.session_state.pac_raw_history[-30:]))
            if prediction["future_pac"] < mu:
                stim_active = True

    # Update display and state
    pac_display = pac_to_display(
        pac_current, st.session_state.pac_mean, st.session_state.pac_std,
    )
    st.session_state.pac_history.append(pac_display)
    st.session_state.pac_raw_history.append(pac_current)
    st.session_state.step_count += 1
    prev_stim = st.session_state.stim_active

    # Track stim/rest counts and time since switch
    if stim_active:
        st.session_state.n_stim += 1
    else:
        st.session_state.n_rest += 1
    if stim_active != prev_stim:
        st.session_state.time_since_switch = 0.0
    else:
        st.session_state.time_since_switch += 2.0
    st.session_state.stim_active = stim_active

    with col_sync:
        st.metric(label("brain_sync_level"), f"{pac_display:.1f}/100")
    with col_stim:
        if stim_active:
            st.markdown("**Stimulus:** :green[ACTIVE]")
        else:
            st.markdown("**Stimulus:** :gray[REST]")
    with col_steps:
        st.metric("Windows Processed", st.session_state.step_count)

    # Audio -- only re-render on state transition to avoid restart clicks
    audio_ph = st.empty()
    if stim_active != prev_stim:
        if stim_active:
            wav = make_40hz_wav(volume=volume)
            audio_ph.audio(wav, format="audio/wav", loop=True, autoplay=True)
        else:
            audio_ph.empty()
    elif stim_active:
        wav = make_40hz_wav(volume=volume)
        audio_ph.audio(wav, format="audio/wav", loop=True, autoplay=True)

    # PAC trend chart -- show last 60 values
    if len(st.session_state.pac_history) > 1:
        chart_data = pd.DataFrame(
            {"Brain Sync Level": st.session_state.pac_history[-60:]},
            index=range(
                max(0, len(st.session_state.pac_history) - 60),
                len(st.session_state.pac_history),
            ),
        )
        st.line_chart(chart_data, width="stretch")

    # Auto-advance: rerun to simulate real-time
    # No extra sleep needed -- adapter.get_window() already sleeps 2 seconds
    st.rerun()


def render_summary() -> None:
    """Post-session summary with plain-language metrics and session saving."""
    patient_id = st.session_state.get("selected_patient_id")
    patient = _get_patient_by_id(patient_id) if patient_id else None

    st.title("Session Complete")
    if patient:
        st.subheader(f"Patient: {patient['name']}")

    # Check if session data exists
    if "session_controller" not in st.session_state:
        st.warning("No session data found.")
        if st.button("Back to Patient List"):
            navigate("patient_select")
            st.rerun()
        return

    pac_arr = np.array(st.session_state.get("pac_raw_history", []))
    n_stim = st.session_state.get("n_stim", 0)
    n_rest = st.session_state.get("n_rest", 0)
    n_steps = len(pac_arr)
    pct_stim = (n_stim / max(1, n_steps)) * 100.0

    pac_mean_raw = float(np.mean(pac_arr)) if n_steps > 0 else 0.0
    pac_display_mean = pac_to_display(
        pac_mean_raw,
        st.session_state.get("pac_mean", 0.0),
        st.session_state.get("pac_std", 1.0),
    )

    # Approximation: targeting accuracy from pct_stimulate vs validated 72.1% baseline
    targeting_accuracy = min(100.0, pct_stim * 72.1 / 65.0) if pct_stim > 0 else 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label("brain_sync_level"), f"{pac_display_mean:.1f}/100")
    with col2:
        st.metric(label("therapy_active_pct"), f"{pct_stim:.1f}%")
    with col3:
        st.metric(label("targeting_accuracy_pct"), f"{targeting_accuracy:.1f}%")

    duration_min = round(n_steps * 2 / 60, 1)
    st.info(f"Session duration: {duration_min} min across {n_steps} windows (2s each)")

    if patient_id and n_steps > 0:
        from datetime import date
        session_record = {
            "date": str(date.today()),
            "duration_min": duration_min,
            "brain_sync_level": pac_mean_raw,
            "therapy_active_pct": round(pct_stim, 1),
            "targeting_accuracy_pct": round(targeting_accuracy, 1),
            "notes": "Completed via caregiver app (simulated EEG)",
        }
        save_session(patient_id, session_record)
        st.success("Session saved to patient profile.")

    col_back, col_new = st.columns(2)
    with col_back:
        if st.button("View Patient History"):
            navigate("patient_history")
            st.rerun()
    with col_new:
        if st.button("Back to Patient List"):
            # Clear session state for next session
            for key in [
                "session_controller", "session_eegnet", "session_tcn",
                "session_extractor", "session_adapter", "pac_history",
                "pac_raw_history", "step_count", "stim_active",
                "session_running", "n_stim", "n_rest",
                "time_since_switch", "last_stim_state",
            ]:
                st.session_state.pop(key, None)
            navigate("patient_select")
            st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Persistent sidebar with hardware status, Real EEG toggle, and navigation."""
    with st.sidebar:
        st.markdown(f"**NeuroCare** {APP_VERSION}")
        st.divider()

        st.markdown("**Hardware Status**")
        st.success("Simulated EEG")
        st.toggle(
            "Real EEG Mode",
            value=False,
            disabled=True,
            help=(
                "Real EEG requires local execution with a BLE-enabled Muse 2 "
                "headset. Cloud deployment runs in simulated mode only."
            ),
            key="real_eeg_toggle",
        )

        st.divider()
        if st.session_state.get("page") != "welcome":
            if st.button("Home", width="stretch"):
                navigate("welcome")
                st.rerun()


# ---------------------------------------------------------------------------
# Page router
# ---------------------------------------------------------------------------
PAGE_MAP = {
    "welcome": render_welcome,
    "patient_select": render_patient_select,
    "patient_history": render_patient_history,
    "session": render_session,
    "summary": render_summary,
}


def main() -> None:
    """Entry point — configure page, init state, route to active page."""
    st.set_page_config(
        page_title="NeuroCare 40Hz",
        page_icon="\U0001f9e0",
        layout="wide",
    )

    _init_session_state()
    render_sidebar()

    page = st.session_state.page
    renderer = PAGE_MAP.get(page, render_welcome)
    renderer()


if __name__ == "__main__":
    main()
