"""
40 Hz Auditory Stimulus Generator for TRIBE V2 Integration

Generates auditory click trains and amplitude-modulated tones at 40 Hz
for driving the TRIBE V2 cortical response model. These stimuli match
the 40 Hz ASSR paradigm used in gamma entrainment research.

Stimulus types:
    - Click train: Brief pulses at 40 Hz (standard ASSR paradigm)
    - AM tone: Carrier tone amplitude-modulated at 40 Hz
    - Silence: Baseline/rest condition

References:
    Galambos et al. (1981). "A 40-Hz auditory potential recorded from
    the human scalp." PNAS.
    Picton et al. (2003). "Human auditory steady-state responses."
    International Journal of Audiology.

Author: Amaar Chughtai
Date: April 2026
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np


AUDIO_SR: int = 16000  # 16 kHz — Wav2Vec-BERT native sample rate


@dataclass
class StimulusConfig:
    """Configuration for 40 Hz auditory stimulus generation."""
    stimulus_type: Literal["click_train", "am_tone"] = "click_train"
    frequency_hz: float = 40.0
    duration_sec: float = 2.0
    sample_rate: int = AUDIO_SR
    carrier_freq_hz: float = 1000.0   # For AM tone carrier
    click_duration_ms: float = 1.0    # Click pulse width
    amplitude: float = 0.8            # Peak amplitude (0-1)
    ramp_ms: float = 5.0              # Onset/offset cosine ramp


def generate_click_train(
    cfg: StimulusConfig,
) -> np.ndarray:
    """
    Generate a 40 Hz click train stimulus.

    Click trains are the standard ASSR stimulus: brief rectangular pulses
    repeated at 40 Hz. Each click is a short burst that evokes a transient
    auditory response; at 40 Hz repetition, these responses superimpose
    into a steady-state oscillation.

    Args:
        cfg: Stimulus configuration.

    Returns:
        signal: Audio waveform, shape (n_samples,), float32.
    """
    n_samples = int(cfg.duration_sec * cfg.sample_rate)
    signal = np.zeros(n_samples, dtype=np.float32)

    click_samples = max(1, int(cfg.click_duration_ms * cfg.sample_rate / 1000))
    period_samples = int(cfg.sample_rate / cfg.frequency_hz)

    # Place clicks at regular intervals
    click_starts = np.arange(0, n_samples, period_samples)
    for start in click_starts:
        end = min(start + click_samples, n_samples)
        signal[start:end] = cfg.amplitude

    # Apply onset/offset ramp to avoid spectral splatter
    signal = _apply_ramp(signal, cfg.ramp_ms, cfg.sample_rate)

    return signal


def generate_am_tone(
    cfg: StimulusConfig,
) -> np.ndarray:
    """
    Generate a 40 Hz amplitude-modulated tone.

    An AM tone has a carrier frequency (e.g. 1 kHz) whose amplitude is
    modulated sinusoidally at 40 Hz. This produces a cleaner spectral
    signature than click trains and is commonly used in ASSR research.

    Args:
        cfg: Stimulus configuration.

    Returns:
        signal: Audio waveform, shape (n_samples,), float32.
    """
    n_samples = int(cfg.duration_sec * cfg.sample_rate)
    t = np.arange(n_samples, dtype=np.float64) / cfg.sample_rate

    # Carrier tone
    carrier = np.sin(2 * np.pi * cfg.carrier_freq_hz * t)

    # 40 Hz amplitude modulation (depth = 1.0 for full modulation)
    modulator = 0.5 * (1.0 + np.sin(2 * np.pi * cfg.frequency_hz * t))

    signal = (cfg.amplitude * carrier * modulator).astype(np.float32)

    # Apply onset/offset ramp
    signal = _apply_ramp(signal, cfg.ramp_ms, cfg.sample_rate)

    return signal


def generate_silence(
    duration_sec: float,
    sample_rate: int = AUDIO_SR,
) -> np.ndarray:
    """
    Generate a silence stimulus (rest condition).

    Args:
        duration_sec: Duration in seconds.
        sample_rate: Sample rate in Hz.

    Returns:
        signal: Zero-valued waveform, shape (n_samples,), float32.
    """
    n_samples = int(duration_sec * sample_rate)
    return np.zeros(n_samples, dtype=np.float32)


def generate_stimulus(
    cfg: StimulusConfig,
) -> np.ndarray:
    """
    Generate auditory stimulus based on configuration.

    Args:
        cfg: Stimulus configuration.

    Returns:
        signal: Audio waveform, shape (n_samples,), float32.
    """
    if cfg.stimulus_type == "click_train":
        return generate_click_train(cfg)
    elif cfg.stimulus_type == "am_tone":
        return generate_am_tone(cfg)
    else:
        raise ValueError(f"Unknown stimulus type: {cfg.stimulus_type}")


def save_stimulus_wav(
    signal: np.ndarray,
    path: Path,
    sample_rate: int = AUDIO_SR,
) -> None:
    """
    Save stimulus as WAV file for TRIBE V2 input.

    Args:
        signal: Audio waveform, float32.
        path: Output file path (.wav).
        sample_rate: Sample rate in Hz.
    """
    import soundfile as sf
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), signal, sample_rate, subtype="FLOAT")


def generate_stimulus_library(
    output_dir: Path,
    durations: list[float] = [2.0, 5.0, 10.0, 20.0, 40.0],
) -> dict[str, Path]:
    """
    Pre-generate a library of stimuli at various durations.

    Creates both click train and silence stimuli for each duration,
    ready for TRIBE V2 cortical prediction caching.

    Args:
        output_dir: Directory to save WAV files.
        durations: List of stimulus durations in seconds.

    Returns:
        paths: Mapping of stimulus key to file path.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    for dur in durations:
        # Stimulation condition
        cfg = StimulusConfig(
            stimulus_type="click_train",
            duration_sec=dur,
        )
        stim_signal = generate_stimulus(cfg)
        stim_path = output_dir / f"stim_40hz_{dur:.0f}s.wav"
        save_stimulus_wav(stim_signal, stim_path)
        paths[f"stim_{dur:.0f}s"] = stim_path

        # Rest condition (silence)
        rest_signal = generate_silence(dur)
        rest_path = output_dir / f"rest_silence_{dur:.0f}s.wav"
        save_stimulus_wav(rest_signal, rest_path)
        paths[f"rest_{dur:.0f}s"] = rest_path

    return paths


def _apply_ramp(
    signal: np.ndarray,
    ramp_ms: float,
    sample_rate: int,
) -> np.ndarray:
    """Apply cosine onset/offset ramp to prevent spectral artifacts."""
    ramp_samples = int(ramp_ms * sample_rate / 1000)
    if ramp_samples < 1 or len(signal) < 2 * ramp_samples:
        return signal

    ramp = 0.5 * (1 - np.cos(np.linspace(0, np.pi, ramp_samples)))
    signal = signal.copy()
    signal[:ramp_samples] *= ramp.astype(signal.dtype)
    signal[-ramp_samples:] *= ramp[::-1].astype(signal.dtype)
    return signal


if __name__ == "__main__":
    print("=" * 60)
    print("Stimulus Generator — Self-Test")
    print("=" * 60)

    cfg = StimulusConfig(stimulus_type="click_train", duration_sec=2.0)
    click = generate_click_train(cfg)
    print(f"Click train: shape={click.shape}, dtype={click.dtype}")
    print(f"  Max={click.max():.3f}, RMS={np.sqrt(np.mean(click**2)):.4f}")
    n_clicks = np.sum(np.diff((click > 0.1).astype(int)) == 1)
    expected_clicks = int(cfg.frequency_hz * cfg.duration_sec)
    print(f"  Clicks detected: {n_clicks} (expected ~{expected_clicks})")

    cfg_am = StimulusConfig(stimulus_type="am_tone", duration_sec=2.0)
    am = generate_am_tone(cfg_am)
    print(f"\nAM tone: shape={am.shape}, dtype={am.dtype}")
    print(f"  Max={am.max():.3f}, RMS={np.sqrt(np.mean(am**2)):.4f}")

    silence = generate_silence(2.0)
    print(f"\nSilence: shape={silence.shape}, max={silence.max():.4f}")

    print("\n[PASS] All stimulus types generated successfully")
