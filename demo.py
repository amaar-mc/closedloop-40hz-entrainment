"""
Real-Time Closed-Loop 40 Hz Entrainment Demo — Real EEG Data

Interactive Streamlit dashboard replaying real EEG recordings from the
OpenNeuro ds005048 dataset through all four controller strategies and the
trained causal TCN forecaster.  Instead of simulated dynamics, the demo steps
through a held-out test subject's actual PAC trace and spectral features,
running the TCN in real time on the same 73-dimensional feature vectors it
was trained on.

Launch:
    streamlit run demo.py

Author: Amaar Chughtai
Date: March 2026
"""

from __future__ import annotations

import sys
import time
import threading
from pathlib import Path
from collections import deque
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from simulator import StimAction

# ---------------------------------------------------------------------------
# Audio availability — graceful fallback when sounddevice is missing
# ---------------------------------------------------------------------------
try:
    import sounddevice as sd

    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print(
        "Warning: sounddevice not installed — audio disabled. "
        "Install with: pip install sounddevice"
    )

# ---------------------------------------------------------------------------
# TCN availability — graceful fallback when torch/checkpoint is missing
# ---------------------------------------------------------------------------
try:
    import torch
    from temporal_multiscale.realtime_inference import RealtimePACForecaster

    _CHECKPOINT = _ROOT / "models" / "best_multiscale_tcn_lb20_hz5_ts1.pth"
    _SCALERS = _ROOT / "data" / "processed" / "multiscale_temporal" / "scalers.npz"
    TCN_AVAILABLE = _CHECKPOINT.exists() and _SCALERS.exists()
except ImportError:
    TCN_AVAILABLE = False


# ---------------------------------------------------------------------------
# Data paths
# ---------------------------------------------------------------------------
_DATA_DIR = _ROOT / "data" / "processed"
_RAW_ROOT = _ROOT / "data" / "raw" / "ds005048"


# ---------------------------------------------------------------------------
# Controllers copied from scripts/pipeline/run_closed_loop_demo.py
# for import isolation (avoid heavy src/validation.py dependencies)
# ---------------------------------------------------------------------------


class FixedScheduleControl:
    """40s ON + 20s OFF (standard clinical protocol)."""

    name = "Fixed Schedule"

    def __init__(self, stim_dur: int = 40, rest_dur: int = 20):
        self.cycle = stim_dur + rest_dur
        self.stim_dur = stim_dur
        self.step_count = 0

    def reset(self):
        self.step_count = 0

    def step(self, pac: float) -> int:
        pos = self.step_count % self.cycle
        self.step_count += 1
        return StimAction.STIMULATE if pos < self.stim_dur else StimAction.REST


class ReactiveThresholdControl:
    """Z-score reactive controller — stimulates when PAC drops below threshold."""

    name = "Reactive Threshold"

    def __init__(self, window: int = 30, z_thresh: float = 0.5):
        self.window = window
        self.z_thresh = z_thresh
        self.buf: list = []

    def reset(self):
        self.buf = []

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 10:
            return StimAction.REST
        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        if z < -self.z_thresh:
            return StimAction.STIMULATE
        return StimAction.REST


class PredictiveLookAheadControl:
    """Trend-based look-ahead controller with hysteresis."""

    name = "Predictive Look-Ahead"

    def __init__(
        self,
        window: int = 30,
        z_thresh: float = 0.5,
        trend_k: int = 5,
        hold_time: int = 5,
    ):
        self.window = window
        self.z_thresh = z_thresh
        self.trend_k = trend_k
        self.hold_time = hold_time
        self.buf: list = []
        self.state = StimAction.REST
        self.t_in_state = 0

    def reset(self):
        self.buf = []
        self.state = StimAction.REST
        self.t_in_state = 0

    def _trend(self) -> float:
        if len(self.buf) < self.trend_k:
            return 0.0
        recent = self.buf[-self.trend_k :]
        x = np.arange(self.trend_k, dtype=np.float64)
        y = np.array(recent, dtype=np.float64)
        xm, ym = x.mean(), y.mean()
        denom = np.sum((x - xm) ** 2)
        if denom < 1e-12:
            return 0.0
        return float(np.sum((x - xm) * (y - ym)) / denom)

    def step(self, pac: float) -> int:
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)
        if len(self.buf) < 10:
            return StimAction.REST

        mu = np.mean(self.buf)
        sigma = np.std(self.buf) + 1e-8
        z = (pac - mu) / sigma
        trend = self._trend()

        desired = None
        if trend < -0.3 * sigma:
            desired = StimAction.STIMULATE
        elif trend > 0.3 * sigma:
            desired = StimAction.REST
        elif z < -self.z_thresh:
            desired = StimAction.STIMULATE
        elif z > self.z_thresh:
            desired = StimAction.REST

        if desired is None:
            desired = self.state

        if desired != self.state:
            if self.t_in_state >= self.hold_time:
                self.state = desired
                self.t_in_state = 0
        else:
            self.t_in_state += 1

        return self.state


class OracleControl:
    """Perfect knowledge — stimulate when below target."""

    name = "Oracle"

    def __init__(self, target: float = 0.2):
        self.target = target

    def reset(self):
        pass

    def step(self, pac: float) -> int:
        return StimAction.STIMULATE if pac < self.target else StimAction.REST


class TCNController:
    """TCN-based predictive controller using the trained causal forecaster.

    Uses the multiscale causal TCN to forecast PAC 5 steps ahead and
    stimulates when the predicted future PAC is below the running mean.
    This is the primary research contribution — a learned closed-loop
    controller that uses 73-dimensional EEG features for adaptive control.
    """

    name = "Causal TCN (Ours)"

    def __init__(self, forecaster: RealtimePACForecaster):
        self.forecaster = forecaster
        self.last_prediction: Optional[Dict[str, float]] = None
        self.buf: list = []
        self.window = 30

    def reset(self):
        self.forecaster.reset()
        self.last_prediction = None
        self.buf = []

    def step(
        self,
        pac: float,
        spectral_features: np.ndarray,
        stim_state: float,
        time_since_switch_sec: float,
        stim_frac_recent: float,
        cycle_phase_sin: float,
        cycle_phase_cos: float,
    ) -> int:
        """Make a control decision using TCN forecast."""
        result = self.forecaster.step(
            spectral_features=spectral_features,
            pac_current=pac,
            stim_state=stim_state,
            time_since_switch_sec=time_since_switch_sec,
            stim_frac_recent=stim_frac_recent,
            cycle_phase_sin=cycle_phase_sin,
            cycle_phase_cos=cycle_phase_cos,
        )
        self.last_prediction = result
        self.buf.append(pac)
        if len(self.buf) > self.window:
            self.buf.pop(0)

        if result is None:
            # Still warming up (need lookback steps)
            return StimAction.REST

        # Stimulate when TCN predicts PAC will drop below running mean
        if len(self.buf) >= 10:
            mu = np.mean(self.buf)
            if result["future_pac"] < mu:
                return StimAction.STIMULATE
        return StimAction.REST


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------


@st.cache_data
def load_test_subjects() -> Dict[str, Dict]:
    """Load test subject metadata for the subject selector."""
    test = np.load(_DATA_DIR / "test_data.npz")
    subjects = test["subjects"]
    info = {}
    for s in sorted(np.unique(subjects)):
        n = int(np.sum(subjects == s))
        info[s] = {"n_steps": n, "duration_str": f"{n // 60}m {n % 60}s"}
    return info


@st.cache_data
def load_subject_data(subject: str) -> Dict[str, np.ndarray]:
    """Load a test subject's PAC, spectral features, and stim events."""
    test = np.load(_DATA_DIR / "test_data.npz")
    spec = np.load(_DATA_DIR / "test_spectral_cache.npy")
    mask = test["subjects"] == subject
    pac = test["pac"][mask]
    spectral = spec[mask]

    # Load stim events from BIDS
    events_path = (
        _RAW_ROOT
        / subject
        / "eeg"
        / f"{subject}_task-40HzAuditoryEntrainment_events.tsv"
    )
    events = (
        pd.read_csv(events_path, sep="\t").sort_values("onset").reset_index(drop=True)
    )
    # value=2 is stim, value=1 is rest
    events["state"] = (events["value"].astype(int) == 2).astype(np.float64)

    # Pre-compute stim context features for each timestep
    n = len(pac)
    hop_sec = 1.0
    window_sec = 2.0
    stim_history_sec = 20
    t = np.arange(n, dtype=np.float64) * hop_sec + window_sec / 2.0

    stim_state = np.zeros(n, dtype=np.float64)
    for _, row in events.iterrows():
        onset = float(row["onset"])
        duration = float(row["duration"])
        st_val = float(row["state"])
        in_event = (t >= onset) & (t < onset + duration)
        stim_state[in_event] = st_val

    # Time since last switch
    switch_onsets = np.unique(
        np.concatenate([[0.0], events["onset"].to_numpy(dtype=np.float64)])
    )
    idx = np.searchsorted(switch_onsets, t, side="right") - 1
    idx = np.clip(idx, 0, len(switch_onsets) - 1)
    time_since_switch = np.maximum(0.0, t - switch_onsets[idx])

    # Stim fraction recent (causal moving average)
    history_n = max(1, int(round(stim_history_sec / hop_sec)))
    stim_frac = np.zeros(n, dtype=np.float64)
    csum = np.cumsum(stim_state)
    for i in range(n):
        lo = max(0, i - history_n + 1)
        total = csum[i] - (csum[lo - 1] if lo > 0 else 0.0)
        stim_frac[i] = total / (i - lo + 1)

    # Cycle phase
    cycle = 60.0
    phase = (t % cycle) / cycle
    phase_sin = np.sin(2.0 * np.pi * phase)
    phase_cos = np.cos(2.0 * np.pi * phase)

    return {
        "pac": pac,
        "spectral": spectral,
        "stim_state": stim_state,
        "time_since_switch": time_since_switch,
        "stim_frac": stim_frac,
        "phase_sin": phase_sin,
        "phase_cos": phase_cos,
        "events": events,
    }


# ---------------------------------------------------------------------------
# Audio engine — 40 Hz click trains via sounddevice
# ---------------------------------------------------------------------------


class AudioEngine:
    """Produces 40 Hz click-train audio during stimulation periods."""

    SAMPLE_RATE = 44100
    CLICK_FREQ = 40

    def __init__(self):
        self.stimulating = False
        self.muted = False
        self.phase = 0
        self.stream = None
        period_samples = self.SAMPLE_RATE // self.CLICK_FREQ
        self.click_period = np.zeros(period_samples, dtype=np.float32)
        click_n = int(0.001 * self.SAMPLE_RATE)
        t = np.arange(click_n, dtype=np.float32) / self.SAMPLE_RATE
        self.click_period[:click_n] = 0.3 * np.sin(2 * np.pi * 1000 * t).astype(
            np.float32
        )

    def callback(self, outdata, frames, time_info, status):
        if self.muted or not self.stimulating:
            outdata[:] = 0
            return
        for i in range(frames):
            idx = self.phase % len(self.click_period)
            outdata[i, 0] = self.click_period[idx]
            self.phase += 1

    def start(self):
        self.stream = sd.OutputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            callback=self.callback,
            dtype="float32",
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None


class _NoOpAudioEngine:
    """Stub when sounddevice is unavailable."""

    stimulating = False
    muted = False

    def start(self):
        pass

    def stop(self):
        pass


# ---------------------------------------------------------------------------
# Matplotlib helpers
# ---------------------------------------------------------------------------

_lock = threading.RLock()


def _build_figure(
    controller_names: List[str],
    pac_history: List[float],
    action_histories: Dict[str, List[int]],
    tcn_predictions: Optional[List[Tuple[int, float]]] = None,
    pac_range: Optional[Tuple[float, float]] = None,
) -> plt.Figure:
    """Create multi-panel figure: one shared PAC trace, per-controller decisions.

    All controllers see the same real PAC trace.  Each panel shows the
    controller's stim/rest decisions as coloured background bands overlaid
    on the real PAC signal.  An optional TCN prediction overlay shows
    forecast vs actual.
    """
    n_panels = len(controller_names)
    with _lock:
        fig, axes = plt.subplots(
            n_panels,
            1,
            figsize=(12, 2.5 * n_panels),
            sharex=True,
        )
        if n_panels == 1:
            axes = [axes]

        y_lo = pac_range[0] if pac_range else 0.0
        y_hi = (
            pac_range[1]
            if pac_range
            else max(pac_history) * 1.2
            if pac_history
            else 1e-4
        )

        for idx, name in enumerate(controller_names):
            ax = axes[idx]
            acts = action_histories.get(name, [])

            # Draw stim/rest background bands (consolidated runs)
            if len(acts) > 0:
                run_start = 0
                current = acts[0]
                for t in range(1, len(acts)):
                    if acts[t] != current:
                        color = "#c8e6c9" if current == 1 else "#ffcdd2"
                        ax.axvspan(run_start, t, alpha=0.35, color=color, linewidth=0)
                        run_start = t
                        current = acts[t]
                color = "#c8e6c9" if current == 1 else "#ffcdd2"
                ax.axvspan(run_start, len(acts), alpha=0.35, color=color, linewidth=0)

            # Plot the real PAC trace
            ax.plot(pac_history, color="black", linewidth=0.8, label="Real PAC")

            # TCN prediction overlay on TCN panel
            if name == "Causal TCN (Ours)" and tcn_predictions:
                pred_times = [p[0] for p in tcn_predictions]
                pred_vals = [p[1] for p in tcn_predictions]
                ax.plot(
                    pred_times,
                    pred_vals,
                    color="#1565C0",
                    linewidth=1.2,
                    alpha=0.8,
                    linestyle="--",
                    label="TCN Forecast (+5s)",
                )
                ax.legend(loc="upper right", fontsize=7, framealpha=0.7)

            ax.set_ylabel(name, fontsize=10, fontweight="bold")
            ax.set_ylim(y_lo, y_hi)
            ax.set_xlim(0, max(len(pac_history), 1))
            ax.tick_params(labelsize=8)

        axes[-1].set_xlabel("Time (seconds)", fontsize=10)
        fig.suptitle(
            "Closed-Loop 40 Hz Entrainment — Real EEG Replay",
            fontsize=13,
            fontweight="bold",
            y=0.98,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


# ---------------------------------------------------------------------------
# Streamlit app
# ---------------------------------------------------------------------------


def main():
    st.set_page_config(
        page_title="40 Hz Entrainment Demo",
        page_icon="🧠",
        layout="wide",
    )

    if "phase" not in st.session_state:
        st.session_state.phase = "configure"
    if "muted" not in st.session_state:
        st.session_state.muted = False

    # ================================================================
    #  CONFIGURE PHASE
    # ================================================================
    if st.session_state.phase == "configure":
        st.title("Closed-Loop 40 Hz Entrainment Demo")
        st.markdown(
            "Replay **real EEG recordings** from held-out test subjects through "
            "four controller strategies.  The **Causal TCN** (our trained model) "
            "runs inference on the original 73-dimensional feature vectors — "
            "the same data it was trained on."
        )

        subject_info = load_test_subjects()
        subject_labels = {
            s: f"{s} ({info['duration_str']})" for s, info in subject_info.items()
        }

        col1, col2 = st.columns(2)

        with col1:
            subject = st.selectbox(
                "Test Subject",
                options=list(subject_labels.keys()),
                format_func=lambda s: subject_labels[s],
                index=2,  # Default to sub-15 (longest)
            )
            speed = st.select_slider(
                "Replay Speed",
                options=["1x", "5x", "10x", "Max"],
                value="5x",
            )

        with col2:
            st.markdown("**Subject Details**")
            si = subject_info[subject]
            st.markdown(
                f"- **Duration:** {si['duration_str']} ({si['n_steps']} timesteps)\n"
                f"- **Features:** 73 dimensions (61 spectral + 7 PAC + 5 stim context)\n"
                f"- **TCN:** {'✓ Available' if TCN_AVAILABLE else '✗ Not available'}\n"
                f"- **Audio:** {'✓ Available' if AUDIO_AVAILABLE else '✗ Not available'}"
            )

        if not TCN_AVAILABLE:
            st.warning(
                "⚠️ TCN checkpoint or scalers not found — TCN controller will be disabled. "
                "Run `python temporal_multiscale/build_multiscale_dataset.py` first."
            )
        if not AUDIO_AVAILABLE:
            st.warning(
                "⚠️ sounddevice not installed — audio disabled. "
                "Install with: `pip install sounddevice`"
            )

        st.markdown("---")
        st.markdown(
            "**How it works:** Each controller sees the same real PAC trace and "
            "decides when to stimulate.  The Causal TCN uses the full 73-feature "
            "vector (spectral power, PAC history, stim context) to predict PAC "
            "5 seconds ahead and stimulates when the forecast drops below the "
            "running mean."
        )

        if st.button("▶ Start Replay", type="primary"):
            st.session_state.subject = subject
            st.session_state.speed = speed
            st.session_state.phase = "running"
            st.rerun()

    # ================================================================
    #  RUNNING PHASE
    # ================================================================
    elif st.session_state.phase == "running":
        st.title("Closed-Loop 40 Hz Entrainment Demo")

        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 3])
        with ctrl_col1:
            if st.button("⏹ Stop", type="secondary"):
                st.session_state.phase = "configure"
                st.rerun()
        with ctrl_col2:
            muted = st.toggle("🔇 Mute Audio", value=st.session_state.muted)
            st.session_state.muted = muted

        subject = st.session_state.subject
        speed = st.session_state.speed

        # Load real EEG data
        data = load_subject_data(subject)
        pac_full = data["pac"]
        spectral_full = data["spectral"]
        n_steps = len(pac_full)

        status_text = st.empty()
        status_text.info(
            f"Replaying {subject} | {n_steps} steps | Speed: {speed} | "
            f"TCN: {'ON' if TCN_AVAILABLE else 'OFF'}"
        )

        # Speed maps
        sleep_map = {"1x": 1.0, "5x": 0.2, "10x": 0.1, "Max": 0.0}
        batch_map = {"1x": 1, "5x": 1, "10x": 2, "Max": 10}
        sleep_interval = sleep_map[speed]
        batch_size = batch_map[speed]

        # Initialise controllers
        controller_names: List[str] = []
        controllers: Dict[str, object] = {}

        # TCN controller (our model)
        tcn_ctrl: Optional[TCNController] = None
        if TCN_AVAILABLE:
            forecaster = RealtimePACForecaster(
                checkpoint_path=str(_CHECKPOINT),
                scalers_path=str(_SCALERS),
                device="cpu",
            )
            tcn_ctrl = TCNController(forecaster)
            controller_names.append("Causal TCN (Ours)")
            controllers["Causal TCN (Ours)"] = tcn_ctrl

        # Heuristic controllers
        controller_names.extend(
            [
                "Fixed Schedule",
                "Reactive Threshold",
                "Predictive Look-Ahead",
                "Oracle",
            ]
        )
        controllers["Fixed Schedule"] = FixedScheduleControl()
        controllers["Reactive Threshold"] = ReactiveThresholdControl()
        controllers["Predictive Look-Ahead"] = PredictiveLookAheadControl()
        # Oracle target set to median of this subject's PAC
        oracle_target = float(np.median(pac_full))
        controllers["Oracle"] = OracleControl(target=oracle_target)

        # Histories
        pac_history: List[float] = []
        action_histories: Dict[str, List[int]] = {name: [] for name in controller_names}
        tcn_predictions: List[Tuple[int, float]] = []

        # PAC range for y-axis (computed from full trace)
        pac_lo = float(pac_full.min()) * 0.8
        pac_hi = float(pac_full.max()) * 1.2

        # Audio setup — driven by TCN controller decisions
        audio: AudioEngine | _NoOpAudioEngine
        if AUDIO_AVAILABLE:
            audio = AudioEngine()
        else:
            audio = _NoOpAudioEngine()

        audio_started = False
        try:
            audio.start()
            audio_started = True
        except Exception as exc:
            st.warning(f"⚠️ Audio could not start: {exc}")

        # Plot placeholder
        plot_placeholder = st.empty()
        progress_bar = st.progress(0.0)

        # Metrics row
        metric_cols = st.columns(len(controller_names))
        stim_counts: Dict[str, int] = {name: 0 for name in controller_names}

        # ---- Replay loop ----
        try:
            step = 0
            while step < n_steps:
                if st.session_state.phase != "running":
                    break

                for _ in range(batch_size):
                    if step >= n_steps:
                        break

                    pac_val = float(pac_full[step])
                    pac_history.append(pac_val)

                    for name in controller_names:
                        ctrl = controllers[name]

                        if name == "Causal TCN (Ours)" and isinstance(
                            ctrl, TCNController
                        ):
                            action = ctrl.step(
                                pac=pac_val,
                                spectral_features=spectral_full[step],
                                stim_state=float(data["stim_state"][step]),
                                time_since_switch_sec=float(
                                    data["time_since_switch"][step]
                                ),
                                stim_frac_recent=float(data["stim_frac"][step]),
                                cycle_phase_sin=float(data["phase_sin"][step]),
                                cycle_phase_cos=float(data["phase_cos"][step]),
                            )
                            # Record TCN prediction
                            if ctrl.last_prediction is not None:
                                tcn_predictions.append(
                                    (step, ctrl.last_prediction["future_pac"])
                                )
                            # Audio follows TCN — our research model
                            audio.stimulating = action == 1
                        else:
                            action = ctrl.step(pac_val)

                        action_histories[name].append(int(action))
                        if action == 1:
                            stim_counts[name] += 1

                    step += 1

                # Update audio mute
                audio.muted = st.session_state.get("muted", False)

                # Redraw plot
                fig = _build_figure(
                    controller_names,
                    pac_history,
                    action_histories,
                    tcn_predictions=tcn_predictions if TCN_AVAILABLE else None,
                    pac_range=(pac_lo, pac_hi),
                )
                plot_placeholder.pyplot(fig)
                plt.close(fig)

                # Update metrics
                for i, name in enumerate(controller_names):
                    pct = (stim_counts[name] / max(step, 1)) * 100
                    metric_cols[i].metric(
                        label=name,
                        value=f"{pct:.0f}% stim",
                        delta=f"{stim_counts[name]}/{step} steps",
                    )

                progress_bar.progress(min(step / n_steps, 1.0))

                if sleep_interval > 0:
                    time.sleep(sleep_interval)

        finally:
            if audio_started:
                audio.stop()

        # ---- Replay complete ----
        progress_bar.progress(1.0)
        status_text.success(f"Replay complete — {subject}, {n_steps} steps")

        # Final static plot
        fig = _build_figure(
            controller_names,
            pac_history,
            action_histories,
            tcn_predictions=tcn_predictions if TCN_AVAILABLE else None,
            pac_range=(pac_lo, pac_hi),
        )
        plot_placeholder.pyplot(fig)
        plt.close(fig)

        # Summary statistics
        st.markdown("### Controller Comparison")
        summary_data = []
        for name in controller_names:
            acts = action_histories[name]
            stim_pct = sum(acts) / len(acts) * 100 if acts else 0
            summary_data.append(
                {
                    "Controller": name,
                    "Stim %": f"{stim_pct:.1f}%",
                    "Stim Steps": sum(acts),
                    "Rest Steps": len(acts) - sum(acts),
                }
            )
        st.table(summary_data)

        if st.button("🔄 Run Again", type="primary"):
            st.session_state.phase = "configure"
            st.rerun()


if __name__ == "__main__":
    main()
