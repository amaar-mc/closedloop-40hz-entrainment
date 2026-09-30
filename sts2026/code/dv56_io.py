# AI-assisted code (Claude Code, 2026-10); reviewed and run by the student. See sts2026/AI_DISCLOSURE_LOG.md
"""Reader for the Chan et al. 2022 GENUS human EEG (Harvard Dataverse doi:10.7910/DVN/56XZ3F, CC0).

* BioSemi BDF, 512 Hz, 32 scalp channels labelled A1..A32 (standard BioSemi 32-channel cap layout, mapped
  below), plus EXG and a Status channel.
* Block schedule comes from the per-recording *_Notes.txt ('- (a-b) 1 min periodic audio only ...').
  Block boundaries are taken from Status triggers (code changes), which mark the transitions between
  blocks; if the trigger count does not equal n_blocks-1, the notes' nominal times are used instead.
"""
import re
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "data" / "raw" / "dv56XZ3F"
FS = 512.0
# BioSemi standard 32-channel cap (A1..A32)
BIOSEMI32 = ["Fp1", "AF3", "F7", "F3", "FC1", "FC5", "T7", "C3", "CP1", "CP5", "P7", "P3", "Pz", "PO3", "O1",
             "Oz", "O2", "PO4", "P4", "P8", "CP6", "CP2", "C4", "T8", "FC6", "FC2", "F4", "F8", "AF4", "Fp2",
             "Fz", "Cz"]

BLOCK_RE = re.compile(r"^-\s*\((\d+)\s*-\s*(\d+)\)\s*(.*)$")


def classify(desc):
    d = desc.lower()
    if "baseline" in d:
        return "baseline"
    rnd = "random" in d
    per = "periodic" in d or ("constant" not in d and not rnd and ("audio only" in d or "visual only" in d or "visual+audio" in d or "v+a" in d))
    const = "constant" in d
    if "visual+audio" in d or "v+a" in d:
        mod = "AV"
    elif "audio only" in d:
        mod = "A"
    elif "visual only" in d:
        mod = "V"
    else:
        mod = "?"
    kind = "random" if rnd else "constant" if const else "periodic" if per else "other"
    # duty-cycle test blocks ("96% duty cycle ...") are periodic AV with altered light duty cycle
    if "duty cycle" in d and "periodic" in d and "%" in d.split("duty")[0]:
        kind = "periodic_dutytest"
    return f"{kind}_{mod}"


def parse_notes(path):
    """Return list of sections {title, blocks=[(t0, t1, label, desc)]}. A section starts at a numbered
    header ('2. stim_on: ...') or an unnumbered one ('stim_on: 25 min recording ...',
    'constant_light_test*: 3 min recording ...')."""
    cur = {"title": "(implicit)", "blocks": []}
    sections = [cur]
    for line in Path(path).read_text(errors="ignore").splitlines():
        s = line.strip()
        if re.match(r"^\d+\.\s", s) or re.match(r"^[A-Za-z_0-9]+\*?\s*:\s*\d+\s*min recording", s):
            cur = {"title": s, "blocks": []}
            sections.append(cur)
            continue
        m = BLOCK_RE.match(s)
        if m:
            t0, t1, desc = int(m.group(1)), int(m.group(2)), m.group(3)
            cur["blocks"].append((t0, t1, classify(desc), desc))
    return [s for s in sections if s["blocks"]]


def _section_for(sections, fname):
    f = fname.lower()
    if "constant_light" in f:
        key = lambda t: "constant_light" in t
    elif "baseline.bdf" in f or "3months" in f:
        key = lambda t: "ipad" in t
    elif "stim_on" in f and "hour" not in f and "duty" not in f:
        key = lambda t: "stim_on" in t and not any(k in t for k in ("ipad", "duty", "hour"))
    else:
        return None
    hits = [s for s in sections if key(s["title"].lower())]
    return hits[0] if hits else None


def _sublists(blocks):
    """Split a section's block list where the time restarts at 0 (a recording that was split in two)."""
    out = [[]]
    for b in blocks:
        if b[0] == 0 and out[-1]:
            out.append([])
        out[-1].append(b)
    return out


def status_transitions(raw):
    st = raw.copy().pick(["Status"]).load_data().get_data()[0].astype(np.int64) & 0xFFFF
    on = np.flatnonzero((st[1:] != 0) & (st[:-1] == 0)) + 1
    # merge onsets closer than 2 s
    keep = [on[0]] if len(on) else []
    for i in on[1:]:
        if i - keep[-1] > 2 * FS:
            keep.append(i)
    return np.array(keep, dtype=int)


def schedule(bdf_path, notes_path, raw=None):
    """Blocks for one recording: list of dicts(label, desc, start, stop [samples], source), title.
    Rules (pre-registered): section chosen by file name; a split recording (*_stim_on_N) uses the N-th
    sub-list; blocks beyond the file end are dropped (truncated recordings); boundaries from Status
    triggers if their count equals n_blocks-1 and each is within 10 s of the nominal time, else nominal."""
    import mne
    mne.set_log_level("ERROR")
    raw = raw or mne.io.read_raw_bdf(bdf_path, preload=False)
    dur = raw.n_times / FS
    sec = _section_for(parse_notes(notes_path), Path(bdf_path).name)
    if sec is None:
        return None, "no matching notes section"
    subs = _sublists(sec["blocks"])
    m = re.search(r"stim_on_(\d)\.bdf$", Path(bdf_path).name)
    blocks = subs[int(m.group(1)) - 1] if m else subs[0]
    blocks = [b for b in blocks if b[1] <= dur + 5]
    if not blocks:
        return None, "no blocks within file"
    tr = status_transitions(raw)
    nominal = np.array([b[0] for b in blocks[1:]]) * FS
    if len(tr) == len(blocks) - 1 and np.all(np.abs(tr - nominal) < 10 * FS):
        bounds = np.r_[0, tr, min(blocks[-1][1] * FS, raw.n_times)].astype(int)
        src = "triggers"
    else:
        bounds = np.r_[np.array([b[0] for b in blocks]) * FS, min(blocks[-1][1] * FS, raw.n_times)].astype(int)
        src = f"notes (triggers={len(tr)})"
    out = [dict(label=b[2], desc=b[3], start=int(bounds[i]), stop=int(bounds[i + 1]), source=src)
           for i, b in enumerate(blocks)]
    return out, sec["title"]


def load_eeg(bdf_path, hp=1.0):
    """Scalp EEG (32 ch, volts->uV), average reference, 1 Hz zero-phase high-pass. Returns (x, names, raw)."""
    import mne
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_bdf(bdf_path, preload=True)
    raw.pick([f"A{i}" for i in range(1, 33)])
    raw.rename_channels({f"A{i}": BIOSEMI32[i - 1] for i in range(1, 33)})
    raw.filter(hp, None, fir_design="firwin")
    raw.set_eeg_reference("average")
    return raw.get_data() * 1e6, raw.ch_names, raw
