#!/usr/bin/env python3
"""Reconstruction of the 40-Hz frontal-posterior PLV analysis (URTC 2026 LT ID-1269).

Rebuilds, from the raw OpenNeuro ds005048 EEG, the per-participant values stored in
results/metrics/early_late_connectivity_analysis.json (whose generating script,
validation/analyze_early_late_connectivity.py, is no longer on disk) and verifies
them value by value. Read-only with respect to the repository.

Method (verified against the JSON, see method_reconstruction.md):
  * Data: EEGLAB .fdt (float32, channel-interleaved, column-major), 250 Hz, channel
    order from *_channels.tsv. Events from *_events.tsv ('sample' column is 1-based).
  * 25 bipolar sites  b_ij = frontal_i - posterior_j, frontal = Fp1,Fp2,F3,Fz,F4,
    posterior = P3,Pz,P4,O1,O2.
  * 200 site pairs = unordered pairs of bipolar sites sharing no electrode.
  * Cycle k = k-th 40-s Stimulus block + the following Rest block; complete iff the
    rest lasts the full 20 s. 6-block protocol (sub-01..08) -> 5 complete cycles,
    10-block protocol (sub-09..35) -> 9 complete cycles (final rest is 5 s).
  * Windows: each 40-s stimulation block -> two non-overlapping 20-s windows
    [onset, onset+20 s) and [onset+20 s, onset+40 s); each complete rest -> one 20-s
    window. Each window is processed on its own (no samples shared across windows).
  * Per window, per bipolar signal: 2nd-order Butterworth band-pass f +/- 0.5 Hz
    (scipy.signal.butter(2, [f-.5, f+.5], 'bandpass', fs=250) -> 4th-order
    band-pass), zero-phase forward-backward filtering (sosfiltfilt; filtfilt gives
    the same to ~1e-13), analytic signal via scipy.signal.hilbert.
  * PLV_pair = |mean_t exp(i(phi_a - phi_b))|; window PLV = mean over the 200 pairs.
    PLI_pair = |mean_t sign(Im(z_a conj(z_b)))|.
    wPLI_pair = |mean_t Im(z_a conj(z_b))| / mean_t |Im(z_a conj(z_b))|  (Vinck 2011).
  * Cycle contrast = mean(two stim-window values) - rest-window value.
    Early = mean contrast over complete cycles 1-2; later = mean over cycles 4-5.

Usage:  python reconstruct_plv.py [--out-dir DIR]
Runs with numpy/scipy/pandas (tested with the repo's .venv-reliability interpreter:
numpy 2.5.1, scipy 1.18.0, pandas 3.0.5, Python 3.12).
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal

REPO = Path(__file__).resolve().parents[5]  # lightning_talk/analysis/ -> repository root
RAW = REPO / "data/raw/ds005048"
METRICS = REPO / "results/metrics"
TASK = "40HzAuditoryEntrainment"
FS = 250.0
WIN = int(20 * FS)                      # 5000 samples
FRONTAL = ["Fp1", "Fp2", "F3", "Fz", "F4"]
POSTERIOR = ["P3", "Pz", "P4", "O1", "O2"]
FREQS = [35.0, 37.0, 39.0, 40.0, 41.0, 43.0, 45.0]
HALF_BW = 0.5
ORDER = 2

SITES = [(i, j) for i in range(5) for j in range(5)]          # (frontal idx, posterior idx)
PAIRS = [(a, b) for a, b in itertools.combinations(range(25), 2)
         if SITES[a][0] != SITES[b][0] and SITES[a][1] != SITES[b][1]]
assert len(PAIRS) == 200
PA = np.array([p[0] for p in PAIRS])
PB = np.array([p[1] for p in PAIRS])


def site_name(k):
    i, j = SITES[k]
    return f"{FRONTAL[i]}-{POSTERIOR[j]}"


# ----------------------------------------------------------------------------- IO
def load_subject(sub: str):
    d = RAW / sub / "eeg"
    ch = pd.read_csv(d / f"{sub}_task-{TASK}_channels.tsv", sep="\t")["name"].tolist()
    x = np.fromfile(d / f"{sub}_task-{TASK}_eeg.fdt", dtype=np.float32)
    x = x.reshape(len(ch), -1, order="F").astype(np.float64)
    ev = pd.read_csv(d / f"{sub}_task-{TASK}_events.tsv", sep="\t")
    return ch, x, ev


def bipolar(ch, x):
    fi = [ch.index(c) for c in FRONTAL]
    pi = [ch.index(c) for c in POSTERIOR]
    return np.stack([x[fi[i]] - x[pi[j]] for i, j in SITES])


def build_windows(ev: pd.DataFrame, n_samples: int):
    """Return list of window dicts (every stim block + every rest, with completeness)."""
    rows = ev.to_dict("records")
    wins, block = [], 0
    for k, r in enumerate(rows):
        s0 = int(r["sample"]) - 1                      # 1-based -> 0-based
        if r["trial_type"] == "Stimulus":
            block += 1
            nxt = rows[k + 1] if k + 1 < len(rows) else None
            rest_complete = (nxt is not None and nxt["trial_type"] == "Rest"
                             and float(nxt["duration"]) >= 20
                             and int(nxt["sample"]) - 1 + WIN <= n_samples)
            for h in range(2):
                a = s0 + h * WIN
                wins.append(dict(condition="stim", block=block, half=h + 1, start=a, end=a + WIN,
                                 block_complete=a + WIN <= n_samples,
                                 cycle_complete=rest_complete))
        elif r["trial_type"] == "Rest":
            complete = float(r["duration"]) >= 20 and s0 + WIN <= n_samples
            wins.append(dict(condition="silence", block=block, half=0, start=s0,
                             end=min(s0 + WIN, n_samples), block_complete=complete,
                             cycle_complete=complete))
    return wins


# ------------------------------------------------------------------- connectivity
def analytic(seg: np.ndarray, f: float, method: str = "sosfiltfilt"):
    lo, hi = f - HALF_BW, f + HALF_BW
    if method == "sosfiltfilt":
        sos = signal.butter(ORDER, [lo, hi], btype="bandpass", fs=FS, output="sos")
        y = signal.sosfiltfilt(sos, seg, axis=-1)
    elif method == "filtfilt":
        b, a = signal.butter(ORDER, [lo, hi], btype="bandpass", fs=FS)
        y = signal.filtfilt(b, a, seg, axis=-1)
    else:
        raise ValueError(method)
    return y, signal.hilbert(y, axis=-1)


def window_measures(seg, f, method="sosfiltfilt", all_measures=False):
    _, z = analytic(seg, f, method)
    ph = np.angle(z)
    plv_pairs = np.abs(np.exp(1j * (ph[PA] - ph[PB])).mean(-1))
    out = {"plv": float(plv_pairs.mean())}
    if all_measures:
        im = np.imag(z[PA] * np.conj(z[PB]))
        out["pli"] = float(np.abs(np.sign(im).mean(-1)).mean())
        out["wpli"] = float((np.abs(im.mean(-1)) / np.abs(im).mean(-1)).mean())
        # alternative sign convention for PLI (phase-difference based) for checking
        out["pli_phase"] = float(np.abs(np.sign(np.sin(ph[PA] - ph[PB])).mean(-1)).mean())
    return out, plv_pairs


# ------------------------------------------------------------------------ derived
def contrasts(tab: pd.DataFrame, measure: str):
    """Per complete cycle: mean(stim windows) - rest window."""
    comp = tab[tab.cycle_complete]
    st = comp[comp.condition == "stim"].groupby("block")[measure].mean()
    re = comp[comp.condition == "silence"].groupby("block")[measure].mean()
    return (st - re).sort_index()       # index = cycle number


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--method", default="sosfiltfilt", choices=["sosfiltfilt", "filtfilt"])
    ap.add_argument("--reuse-table", action="store_true",
                    help="reuse reconstructed_window_table.csv instead of recomputing")
    args = ap.parse_args()
    out_dir = Path(args.out_dir)

    J = json.load(open(METRICS / "early_late_connectivity_analysis.json"))
    subjects = J["provenance"]["subjects"]

    table_path = out_dir / "reconstructed_window_table.csv"
    if args.reuse_table and table_path.exists():
        tab = pd.read_csv(table_path)
    else:
        tab = compute_table(subjects, args.method)
        tab.to_csv(table_path, index=False)

    report = verify(J, tab, subjects)
    json.dump(report, open(out_dir / "verification_report.json", "w"), indent=1)
    print(json.dumps(report["summary"], indent=1))

    fig = make_figure_data(J, tab, subjects, args.method)
    json.dump(fig, open(out_dir / "figure_data.json", "w"), indent=1)
    print("wrote", out_dir / "figure_data.json")


def compute_table(subjects, method):
    rows = []
    for sub in subjects:
        ch, x, ev = load_subject(sub)
        b = bipolar(ch, x)
        for w in build_windows(ev, x.shape[1]):
            if w["end"] - w["start"] < WIN:
                continue                                  # truncated final rest: skipped
            seg = b[:, w["start"]:w["end"]]
            rec = dict(subject=sub, **w)
            for f in FREQS:
                m, _ = window_measures(seg, f, method, all_measures=(f == 40.0))
                for k, v in m.items():
                    rec[f"{k}_{int(f)}"] = v
            rows.append(rec)
        print(sub, "done", flush=True)
    return pd.DataFrame(rows)


def per_subject(tab, sub):
    return tab[tab.subject == sub]


def maxerr(a, b):
    return float(np.max(np.abs(np.asarray(a, float) - np.asarray(b, float))))


def verify(J, tab, subjects):
    rep = {"summary": {}}
    S = rep["summary"]

    def early_late(measure, early_cycles, late_sel):
        e, l = [], []
        for sub in subjects:
            c = contrasts(per_subject(tab, sub), measure)
            e.append(c.loc[early_cycles].mean())
            l.append(late_sel(c).mean())
        return np.array(e), np.array(l)

    common = lambda c: c.loc[[4, 5]]
    last2 = lambda c: c.iloc[-2:]

    # 1. primary endpoint (cycles 4-5)
    v = J["target_position_sensitivity_plv"]["cycles_4_to_5"]["values"]
    e, l = early_late("plv_40", [1, 2], common)
    S["primary_plv_cycles4_5_early_maxerr"] = maxerr(e, v["early"])
    S["primary_plv_cycles4_5_late_maxerr"] = maxerr(l, v["late"])
    S["primary_pearson_r_reconstructed"] = float(np.corrcoef(e, l)[0, 1])
    S["primary_pearson_r_json"] = J["target_position_sensitivity_plv"]["cycles_4_to_5"]["raw_association"]["pearson_r"]

    # 2. other target positions (cycles k..k+1)
    for key, blk in J["target_position_sensitivity_plv"].items():
        k0, k1 = [int(t) for t in key.replace("cycles_", "").split("_to_")]
        subs = blk["values"]["subject"]
        ee, ll = [], []
        for sub in subs:
            c = contrasts(per_subject(tab, sub), "plv_40")
            ee.append(c.loc[[1, 2]].mean()); ll.append(c.loc[[k0, k1]].mean())
        S[f"target_{key}_n"] = len(subs)
        S[f"target_{key}_early_maxerr"] = maxerr(ee, blk["values"]["early"])
        S[f"target_{key}_late_maxerr"] = maxerr(ll, blk["values"]["late"])

    # 3. measure convergence (cycles 4-5)
    for m, blk in J["common_position_measure_convergence"]["measures"].items():
        e, l = early_late(f"{m}_40", [1, 2], common)
        S[f"convergence_{m}_early_maxerr"] = maxerr(e, blk["values"]["early"])
        S[f"convergence_{m}_late_maxerr"] = maxerr(l, blk["values"]["late"])
        S[f"convergence_{m}_r_reconstructed"] = float(np.corrcoef(e, l)[0, 1])
        if m == "pli":
            e2, l2 = early_late("pli_phase_40", [1, 2], common)
            S["convergence_pli_phase_sign_variant_early_maxerr"] = maxerr(e2, blk["values"]["early"])

    # 4. frequency specificity (cycles 4-5)
    fs_blk = J["common_position_frequency_specificity_plv"]
    E = np.array(fs_blk["values"]["early_by_frequency"]); L = np.array(fs_blk["values"]["late_by_frequency"])
    for j, f in enumerate(fs_blk["values"]["frequencies_hz"]):
        e, l = early_late(f"plv_{int(f)}", [1, 2], common)
        S[f"freqspec_{int(f)}hz_early_maxerr"] = maxerr(e, E[:, j])
        S[f"freqspec_{int(f)}hz_late_maxerr"] = maxerr(l, L[:, j])
        S[f"freqspec_{int(f)}hz_r_reconstructed"] = float(np.corrcoef(e, l)[0, 1])

    # 5. stimulus_vs_rest: mean(all stim windows) - mean(complete rests); test variants
    variants = {
        "all_stim_windows_minus_complete_rests": lambda t, m: t[t.condition == "stim"][m].mean() - t[(t.condition == "silence") & t.cycle_complete][m].mean(),
        "complete_cycle_stim_minus_complete_rests": lambda t, m: t[(t.condition == "stim") & t.cycle_complete][m].mean() - t[(t.condition == "silence") & t.cycle_complete][m].mean(),
    }
    for m in ["plv", "pli", "wpli"]:
        tv = J["primary_frequency_measures"][m]["stimulus_vs_rest"]["values"]["difference"]
        for vn, fn in variants.items():
            d = [fn(per_subject(tab, s), f"{m}_40") for s in subjects]
            S[f"stim_vs_rest_{m}_{vn}_maxerr"] = maxerr(d, tv)
    for f in FREQS:
        tv = J["frequency_controls_plv"][f"{int(f)}_hz"]["stimulus_vs_rest"]["values"]["difference"]
        for vn, fn in variants.items():
            d = [fn(per_subject(tab, s), f"plv_{int(f)}") for s in subjects]
            S[f"stim_vs_rest_plv{int(f)}_{vn}_maxerr"] = maxerr(d, tv)

    # 6. response_gain_early_to_late (early cycles 1-2 vs LAST two complete cycles)
    for f in FREQS:
        blk = J["frequency_controls_plv"][f"{int(f)}_hz"]["response_gain_early_to_late"]["values"]
        e, l = early_late(f"plv_{int(f)}", [1, 2], last2)
        S[f"response_gain_early_to_late_{int(f)}hz_early_maxerr"] = maxerr(e, blk["early"])
        S[f"response_gain_early_to_late_{int(f)}hz_late_maxerr"] = maxerr(l, blk["late"])

    # 7. response_gain_learning_curve k: first k cycles vs last 2 complete cycles
    for m in ["plv", "pli", "wpli"]:
        for k, blk in J["primary_frequency_measures"][m]["response_gain_learning_curve"].items():
            k = int(k)
            e, l = early_late(f"{m}_40", list(range(1, k + 1)), last2)
            S[f"response_gain_lc_{m}_k{k}_early_maxerr"] = maxerr(e, blk["values"]["early"])
            S[f"response_gain_lc_{m}_k{k}_late_maxerr"] = maxerr(l, blk["values"]["late"])

    # 8. absolute stimulation PLV: first k stim blocks (mean of their 20-s windows) vs
    #    mean of the last 3 stimulation blocks. Test variants for which blocks count.
    def abs_vals(t, m, k, late_mode):
        st = t[t.condition == "stim"]
        blocks_all = sorted(st.block.unique())
        blocks_cc = sorted(st[st.cycle_complete].block.unique())
        pool = blocks_all if late_mode == "all_blocks" else blocks_cc
        early = st[st.block.isin(blocks_all[:k])][m].mean()
        late = st[st.block.isin(pool[-3:])][m].mean()
        return early, late

    for mode in ["all_blocks", "complete_cycle_blocks"]:
        for m in ["plv", "pli", "wpli"]:
            for k, blk in J["primary_frequency_measures"][m]["absolute_stimulation_connectivity_learning_curve"].items():
                k = int(k)
                ev_ = [abs_vals(per_subject(tab, s), f"{m}_40", k, mode) for s in subjects]
                S[f"abs_lc_{m}_k{k}_{mode}_early_maxerr"] = maxerr([a for a, _ in ev_], blk["values"]["early"])
                S[f"abs_lc_{m}_k{k}_{mode}_late_maxerr"] = maxerr([b for _, b in ev_], blk["values"]["late"])
        for f in FREQS:
            blk = J["frequency_controls_plv"][f"{int(f)}_hz"]["absolute_first_block_to_late_blocks"]["values"]
            ev_ = [abs_vals(per_subject(tab, s), f"plv_{int(f)}", 1, mode) for s in subjects]
            S[f"abs_first_block_{int(f)}hz_{mode}_early_maxerr"] = maxerr([a for a, _ in ev_], blk["early"])
            S[f"abs_first_block_{int(f)}hz_{mode}_late_maxerr"] = maxerr([b for _, b in ev_], blk["late"])

    # 9. absolute stimulation PLV at the common position (cycles 1-2 vs 4-5), per frequency
    #    -- NOT in the JSON; computed to test the interpretation question.
    extra = {}
    for f in FREQS:
        m = f"plv_{int(f)}"
        ae, al, re_, rl = [], [], [], []
        for s in subjects:
            t = per_subject(tab, s); t = t[t.cycle_complete]
            st = t[t.condition == "stim"].groupby("block")[m].mean()
            rs = t[t.condition == "silence"].groupby("block")[m].mean()
            ae.append(st.loc[[1, 2]].mean()); al.append(st.loc[[4, 5]].mean())
            re_.append(rs.loc[[1, 2]].mean()); rl.append(rs.loc[[4, 5]].mean())
        extra[f"{int(f)}_hz"] = {
            "abs_stim_plv_cycles1_2_vs_4_5_r": float(np.corrcoef(ae, al)[0, 1]),
            "abs_silence_plv_cycles1_2_vs_4_5_r": float(np.corrcoef(re_, rl)[0, 1]),
            "abs_stim_vs_silence_same_cycles1_2_r": float(np.corrcoef(ae, re_)[0, 1]),
            "mean_abs_stim_plv_cycles1_2": float(np.mean(ae)),
            "mean_abs_silence_plv_cycles1_2": float(np.mean(re_)),
        }
    rep["not_in_json_common_position_absolute_plv"] = extra

    # counts
    rep["complete_cycles_per_subject"] = {s: int(contrasts(per_subject(tab, s), "plv_40").size) for s in subjects}
    return rep


# ------------------------------------------------------------------ figure data
EXAMPLES = {"strong": "sub-01", "moderate": "sub-24", "near_zero_negative": "sub-09"}
EXTRA_EXAMPLES = {"strong_9_cycle_alternate": "sub-32"}
SNIPPET_SUB = "sub-01"
SNIPPET_SEC = 0.3
SNIPPET_OFFSET_SEC = 10.0      # snippet taken from the middle of each 20-s window


def make_figure_data(J, tab, subjects, method):
    v = J["target_position_sensitivity_plv"]["cycles_4_to_5"]["values"]
    idx = {s: i for i, s in enumerate(v["subject"])}
    out = {
        "provenance": {
            "generator": str(Path(__file__).resolve()),
            "source_data": str(RAW),
            "verified_against": str(METRICS / "early_late_connectivity_analysis.json"),
            "method": "20-s windows filtered independently; 2nd-order Butterworth band-pass f+/-0.5 Hz "
                      f"({method}); Hilbert phase; PLV averaged over 200 electrode-disjoint pairs of "
                      "25 frontal-minus-posterior bipolar sites",
            "units": {"plv": "unitless 0-1", "signal": "units as stored in the EEGLAB .fdt (channels.tsv lists units n/a; EEGLAB convention is microvolts; raw channel SD ~1.5-2.2 in these units for sub-01)", "time": "seconds"},
        }
    }

    # (a) per-window 40-Hz PLV for example participants
    a = {}
    for label, sub in {**EXAMPLES, **EXTRA_EXAMPLES}.items():
        t = tab[tab.subject == sub].sort_values("start")
        recs = []
        for wi, r in enumerate(t.itertuples(index=False)):
            recs.append(dict(subject=sub, window_index=wi, start_sec=r.start / FS, end_sec=r.end / FS,
                             condition=r.condition, cycle_index=int(r.block),
                             stim_half=int(r.half) if r.condition == "stim" else None,
                             cycle_complete=bool(r.cycle_complete), plv=float(r.plv_40)))
        c = contrasts(t, "plv_40")
        a[label] = dict(subject=sub, n_complete_cycles=int(c.size),
                        early_contrast_cycles1_2=float(c.loc[[1, 2]].mean()),
                        later_contrast_cycles4_5=float(c.loc[[4, 5]].mean()),
                        json_early=v["early"][idx[sub]], json_late=v["late"][idx[sub]],
                        per_cycle_contrast={int(k): float(x) for k, x in c.items()},
                        windows=recs)
    out["a_example_participants_window_plv_40hz"] = a
    out["a_notes"] = ("cycle_index = stimulation block number; the silence window with the same cycle_index "
                      "follows that block. The final stimulation block of every session is followed by a "
                      "5-s truncated rest, which is not analysed (cycle_complete=false for that block's "
                      "stim windows; they enter only stimulus_vs_rest and absolute-stimulation measures, "
                      "not the early/later contrasts). Label choice: strong/moderate/near-zero chosen by "
                      "early and later cycles-4-5 contrasts in the JSON.")

    # (b) 0.3-s snippet, one electrode-disjoint pair, strong responder, cycle 1
    ch, x, ev = load_subject(SNIPPET_SUB)
    b = bipolar(ch, x)
    t = tab[tab.subject == SNIPPET_SUB]
    w_st = t[(t.condition == "stim") & (t.block == 1) & (t.half == 1)].iloc[0]
    w_re = t[(t.condition == "silence") & (t.block == 1)].iloc[0]
    seg_st = b[:, int(w_st.start):int(w_st.end)]
    seg_re = b[:, int(w_re.start):int(w_re.end)]
    _, pp_st = window_measures(seg_st, 40.0, method)
    _, pp_re = window_measures(seg_re, 40.0, method)
    diff = pp_st - pp_re
    # representative pair: stim-minus-silence pair PLV difference closest to the median over pairs
    k = int(np.argmin(np.abs(diff - np.median(diff))))
    pa, pb = PAIRS[k]
    n0 = int(SNIPPET_OFFSET_SEC * FS); n1 = n0 + int(round(SNIPPET_SEC * FS))
    snip = {}
    for name, seg, w, pp in [("stimulation", seg_st, w_st, pp_st), ("silence", seg_re, w_re, pp_re)]:
        y, z = analytic(seg, 40.0, method)
        dphi = np.angle(np.exp(1j * (np.angle(z[pa]) - np.angle(z[pb]))))
        tt = (w.start + np.arange(n0, n1)) / FS
        snip[name] = dict(window_start_sec=w.start / FS, window_end_sec=w.end / FS, cycle_index=int(w.block),
                          time_sec_session=tt.tolist(), time_sec_from_window_start=(np.arange(n0, n1) / FS).tolist(),
                          signal_a=y[pa, n0:n1].tolist(), signal_b=y[pb, n0:n1].tolist(),
                          phase_difference_rad=dphi[n0:n1].tolist(),
                          pair_plv_full_window=float(pp[k]),
                          pair_plv_snippet_only=float(np.abs(np.exp(1j * dphi[n0:n1]).mean())),
                          subject_window_plv_mean_200_pairs=float(pp.mean()),
                          # whole-window phase difference (decimated to 50 Hz) and a 36-bin histogram:
                          # with a 1-Hz-wide filter the phase difference drifts slowly, so a 0.3-s
                          # snippet looks phase-locked in BOTH conditions; the full window shows the
                          # dispersion that PLV actually measures.
                          full_window_time_sec_from_window_start=(np.arange(0, WIN, 5) / FS).tolist(),
                          full_window_phase_difference_rad_decimated_50hz=dphi[::5].tolist(),
                          phase_difference_histogram_36bins=dict(
                              bin_edges_rad=np.linspace(-np.pi, np.pi, 37).tolist(),
                              counts=np.histogram(dphi, bins=np.linspace(-np.pi, np.pi, 37))[0].tolist()))
    out["b_snippet"] = dict(subject=SNIPPET_SUB, site_a=site_name(pa), site_b=site_name(pb),
                            pair_selection_rule="pair whose (stim window 1 - silence) PLV difference in cycle 1 is closest to the median across the 200 pairs",
                            pair_plv_difference_rank_median=float(np.median(diff)),
                            snippet_rule=f"{SNIPPET_SEC} s starting {SNIPPET_OFFSET_SEC} s into each 20-s window (filtered on the full window, then cut)",
                            **snip)

    # (c) grand average per cycle position 1..5, per condition, 35/40/45 Hz
    c_out = {}
    for f in [35, 40, 45]:
        m = f"plv_{f}"
        per = {"stim": [], "silence": [], "contrast": []}
        for sub in subjects:
            tt = tab[(tab.subject == sub) & tab.cycle_complete]
            st = tt[tt.condition == "stim"].groupby("block")[m].mean()
            rs = tt[tt.condition == "silence"].groupby("block")[m].mean()
            per["stim"].append(st.loc[1:5].values); per["silence"].append(rs.loc[1:5].values)
            per["contrast"].append((st - rs).loc[1:5].values)
        res = {}
        for cond, arr in per.items():
            arr = np.array(arr)            # 35 x 5
            res[cond] = [dict(cycle_index=i + 1, mean=float(arr[:, i].mean()),
                              sem=float(arr[:, i].std(ddof=1) / np.sqrt(arr.shape[0])), n=int(arr.shape[0]))
                         for i in range(5)]
        c_out[f"{f}_hz"] = res
    out["c_grand_average_by_cycle"] = c_out
    out["c_notes"] = ("stim = mean of the two 20-s stimulation windows of that cycle; silence = the following "
                      "20-s rest; contrast = stim - silence; SEM = SD(ddof=1)/sqrt(35) across participants.")
    return out


if __name__ == "__main__":
    main()
