"""
Real-Time Closed-Loop 40 Hz Entrainment Demo

Interactive Streamlit dashboard demonstrating the closed-loop entrainment
system. Runs all four controller strategies simultaneously on simulated brain
dynamics, rendering live PAC visualizations with stim/rest background bands
and producing 40 Hz click-train audio during stimulation periods.

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

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup — same pattern as scripts/pipeline/run_closed_loop_demo.py
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from simulator import EntrainmentSimulator, FatigueAwareSimulator, StimAction

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


# ---------------------------------------------------------------------------
# Audio engine — 40 Hz click trains via sounddevice
# ---------------------------------------------------------------------------


class AudioEngine:
    """Produces 40 Hz click-train audio during stimulation periods.

    The click pattern matches the auditory entrainment stimulus used in the
    research protocol: brief 1 kHz tone bursts at 40 Hz repetition rate.
    """

    SAMPLE_RATE = 44100
    CLICK_FREQ = 40  # Hz — matches research protocol

    def __init__(self):
        self.stimulating = False  # Set by simulation loop
        self.muted = False  # Set by mute toggle
        self.phase = 0
        self.stream = None
        # Pre-generate one period of 40 Hz click train
        period_samples = self.SAMPLE_RATE // self.CLICK_FREQ  # ~1102
        self.click_period = np.zeros(period_samples, dtype=np.float32)
        # 1ms click burst of 1kHz sine at start of each period
        click_n = int(0.001 * self.SAMPLE_RATE)  # 44 samples
        t = np.arange(click_n, dtype=np.float32) / self.SAMPLE_RATE
        self.click_period[:click_n] = 0.3 * np.sin(2 * np.pi * 1000 * t).astype(
            np.float32
        )

    def callback(self, outdata, frames, time_info, status):
        """Sounddevice callback — runs in audio thread."""
        if self.muted or not self.stimulating:
            outdata[:] = 0
            return
        for i in range(frames):
            idx = self.phase % len(self.click_period)
            outdata[i, 0] = self.click_period[idx]
            self.phase += 1

    def start(self):
        """Open and start the audio output stream."""
        self.stream = sd.OutputStream(
            samplerate=self.SAMPLE_RATE,
            channels=1,
            callback=self.callback,
            dtype="float32",
        )
        self.stream.start()

    def stop(self):
        """Stop and close the audio stream."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None


class _NoOpAudioEngine:
    """Stub when sounddevice is unavailable — all methods are silent no-ops."""

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
    controller_names: list[str],
    pac_histories: dict[str, list[float]],
    action_histories: dict[str, list[int]],
) -> plt.Figure:
    """Create the four-panel PAC trace figure with stim/rest background bands.

    Consecutive same-action timesteps are consolidated into single ``axvspan``
    calls to avoid O(n²) rendering on long simulations.
    """
    with _lock:
        fig, axes = plt.subplots(
            4,
            1,
            figsize=(12, 10),
            sharex=True,
        )
        if len(controller_names) < 4:
            return fig  # safety guard

        for idx, name in enumerate(controller_names):
            ax = axes[idx]
            pac = pac_histories[name]
            acts = action_histories[name]

            # Plot PAC trace
            ax.plot(pac, color="black", linewidth=0.8)

            # Draw consolidated stim/rest background bands
            if len(acts) > 0:
                run_start = 0
                current = acts[0]
                for t in range(1, len(acts)):
                    if acts[t] != current:
                        color = "#c8e6c9" if current == 1 else "#ffcdd2"
                        ax.axvspan(run_start, t, alpha=0.35, color=color, linewidth=0)
                        run_start = t
                        current = acts[t]
                # Final run
                color = "#c8e6c9" if current == 1 else "#ffcdd2"
                ax.axvspan(run_start, len(acts), alpha=0.35, color=color, linewidth=0)

            ax.set_ylabel(name, fontsize=10, fontweight="bold")
            ax.set_ylim(-0.02, 0.40)
            ax.set_xlim(0, max(len(pac), 1))
            ax.tick_params(labelsize=8)

        axes[-1].set_xlabel("Time step (seconds)", fontsize=10)
        fig.suptitle(
            "Closed-Loop 40 Hz Entrainment — Live PAC Dynamics",
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

    # ---- Initialise session state ----
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
            "Compare four controller strategies on simulated brain dynamics "
            "with live PAC visualization and 40 Hz click-train audio."
        )

        col1, col2 = st.columns(2)

        with col1:
            fatigue_on = st.toggle("Enable Fatigue Model", value=True)
            speed = st.select_slider(
                "Simulation Speed",
                options=["1x", "5x", "10x", "Max"],
                value="5x",
            )

        with col2:
            duration = st.number_input(
                "Duration (seconds)",
                min_value=60,
                max_value=600,
                value=180,
                step=60,
            )

        if not AUDIO_AVAILABLE:
            st.warning(
                "⚠️ sounddevice not installed — audio disabled. "
                "Install with: `pip install sounddevice`"
            )

        if st.button("▶ Start Simulation", type="primary"):
            # Store config
            st.session_state.fatigue = fatigue_on
            st.session_state.speed = speed
            st.session_state.duration = int(duration)
            st.session_state.phase = "running"
            st.rerun()

    # ================================================================
    #  RUNNING PHASE
    # ================================================================
    elif st.session_state.phase == "running":
        st.title("Closed-Loop 40 Hz Entrainment Demo")

        # ---- Controls ----
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 1, 3])
        with ctrl_col1:
            if st.button("⏹ Stop Simulation", type="secondary"):
                st.session_state.phase = "configure"
                st.rerun()
        with ctrl_col2:
            muted = st.toggle("🔇 Mute Audio", value=st.session_state.muted)
            st.session_state.muted = muted

        fatigue_on = st.session_state.fatigue
        speed = st.session_state.speed
        duration = st.session_state.duration

        status_text = st.empty()
        status_text.info(
            f"{'Fatigue' if fatigue_on else 'No Fatigue'} | "
            f"Speed: {speed} | Duration: {duration}s"
        )

        # ---- Speed maps ----
        sleep_map = {"1x": 1.0, "5x": 0.2, "10x": 0.1, "Max": 0.0}
        batch_map = {"1x": 1, "5x": 1, "10x": 2, "Max": 10}
        sleep_interval = sleep_map[speed]
        batch_size = batch_map[speed]

        # ---- Initialise controllers & simulators ----
        controller_names = [
            "Fixed Schedule",
            "Reactive Threshold",
            "Predictive Look-Ahead",
            "Oracle",
        ]
        controllers = {
            "Fixed Schedule": FixedScheduleControl(),
            "Reactive Threshold": ReactiveThresholdControl(),
            "Predictive Look-Ahead": PredictiveLookAheadControl(),
            "Oracle": OracleControl(),
        }

        SimClass = FatigueAwareSimulator if fatigue_on else EntrainmentSimulator
        simulators = {name: SimClass() for name in controller_names}
        pac_histories: dict[str, list[float]] = {
            name: [sim.pac] for name, sim in simulators.items()
        }
        action_histories: dict[str, list[int]] = {name: [] for name in controller_names}

        # ---- Audio setup ----
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

        # ---- Plot placeholder ----
        plot_placeholder = st.empty()
        progress_bar = st.progress(0.0)

        # ---- Simulation loop ----
        try:
            step = 0
            while step < duration:
                # Check if user stopped
                if st.session_state.phase != "running":
                    break

                # Simulate a batch of steps
                for _ in range(batch_size):
                    if step >= duration:
                        break
                    for name in controller_names:
                        ctrl = controllers[name]
                        sim = simulators[name]
                        pac_val = sim.pac
                        action = ctrl.step(pac_val)
                        sim.step(action)
                        pac_histories[name].append(sim.pac)
                        action_histories[name].append(int(action))

                        # Audio follows Reactive controller —
                        # the primary adaptive strategy
                        if name == "Reactive Threshold":
                            audio.stimulating = action == 1

                    step += 1

                # Update audio mute from session state
                audio.muted = st.session_state.get("muted", False)

                # Redraw plot
                fig = _build_figure(
                    controller_names,
                    pac_histories,
                    action_histories,
                )
                plot_placeholder.pyplot(fig)
                plt.close(fig)

                # Progress
                progress_bar.progress(min(step / duration, 1.0))

                # Sleep for visual pacing
                if sleep_interval > 0:
                    time.sleep(sleep_interval)

        finally:
            if audio_started:
                audio.stop()

        # ---- Simulation finished ----
        progress_bar.progress(1.0)
        status_text.success(
            f"Simulation complete — {duration}s, "
            f"{'Fatigue' if fatigue_on else 'No Fatigue'} model"
        )

        # Final static plot
        fig = _build_figure(
            controller_names,
            pac_histories,
            action_histories,
        )
        plot_placeholder.pyplot(fig)
        plt.close(fig)

        if st.button("🔄 Run Again", type="primary"):
            st.session_state.phase = "configure"
            st.rerun()


if __name__ == "__main__":
    main()
