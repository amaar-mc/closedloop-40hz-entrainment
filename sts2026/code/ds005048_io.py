"""Minimal, dependency-light reader for OpenNeuro ds005048 (EEGLAB .set/.fdt, BIDS).

Written for the STS 2026 re-analysis. Independent of the original src/ pipeline so the
audit does not inherit its assumptions.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "ds005048"
FS = 250.0
TASK = "40HzAuditoryEntrainment"


def subjects():
    return sorted(p.name for p in ROOT.glob("sub-*") if p.is_dir())


def load(sub):
    """Return (data[n_ch, n_samp] float64 in file units (uV), ch_names, events DataFrame)."""
    d = ROOT / sub / "eeg"
    ch = pd.read_csv(d / f"{sub}_task-{TASK}_channels.tsv", sep="\t")["name"].tolist()
    raw = np.fromfile(d / f"{sub}_task-{TASK}_eeg.fdt", dtype="<f4")
    n_ch = len(ch)
    x = raw.reshape((n_ch, -1), order="F").astype(np.float64)
    ev = pd.read_csv(d / f"{sub}_task-{TASK}_events.tsv", sep="\t")
    ev["start"] = ev["sample"].astype(int) - 1  # BIDS sample is 1-based here (verified in URTC reconstruction)
    ev["stop"] = ev["start"] + np.round(ev["duration"] * FS).astype(int)
    ev["is_stim"] = ev["value"].astype(int) == 2
    return x, ch, ev


def participants():
    return pd.read_csv(ROOT / "participants.tsv", sep="\t")
