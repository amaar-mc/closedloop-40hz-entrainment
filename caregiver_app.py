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

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st

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
        if st.button("Get Started", type="primary", use_container_width=True):
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
                        use_container_width=True,
                    ):
                        st.session_state.selected_patient_id = patient["id"]
                        navigate("session")
                        st.rerun()
                with btn_col2:
                    if st.button(
                        "View History",
                        key=f"history_{patient['id']}",
                        use_container_width=True,
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

    st.dataframe(df, use_container_width=True, hide_index=True)

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
    """Live therapy session — stub for Plan 02."""
    st.header("Live Session")
    st.info("Session interface coming in Plan 02.")
    if st.button("Back to Patients"):
        navigate("patient_select")
        st.rerun()


def render_summary() -> None:
    """Post-session summary — stub for Plan 02."""
    st.header("Session Summary")
    st.info("Summary interface coming in Plan 02.")
    if st.button("Back to Patients"):
        navigate("patient_select")
        st.rerun()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Persistent sidebar with hardware status and navigation."""
    with st.sidebar:
        st.markdown(f"**NeuroCare** {APP_VERSION}")
        st.divider()

        st.markdown("**Hardware Status**")
        st.success("Simulated EEG")

        st.divider()
        if st.session_state.get("page") != "welcome":
            if st.button("Home", use_container_width=True):
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
