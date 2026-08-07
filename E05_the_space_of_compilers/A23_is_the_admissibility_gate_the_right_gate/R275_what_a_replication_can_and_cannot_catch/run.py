"""R275 -- R269 replicated R268 and shared two of its defects. A 2x2 says which one it could catch.

THE CLAIM THIS ROUND MAKES MEASURABLE
    R268 reported the site MDE at (0.10, 0.12]. R269 was run to attack it, changed the SHAMS -- the
    one control R268 had built as a no-op -- and confirmed the number unchanged. R274 then found
    the number is [0.1250, 0.1250], and that R268 carried TWO OPPOSITE biases: a coarse GRID that
    reads a bracket's upper bound as the value (inflates the MDE), and a thin CALIBRATION whose
    95th percentile from 200 draws lands too low (deflates it).

    R269 varied neither. Its confirmation could only ever have tested the shams -- and it did,
    correctly, and to no effect, because the number does not depend on them.

    ⚠ "A REPLICATION ONLY TESTS WHAT IT VARIES" is cheap to say. What is not cheap is saying how
    much each held-fixed choice was worth, and that is a 2x2.

ESTIMAND        the class-agreement MDE in each cell of {grid 0.02, grid 0.005} x {200-draw
                calibration, 3000-draw}, and the decomposition of the R268 -> R274 shift into a
                GRID main effect, a CALIBRATION main effect, and their interaction.
IDENTIFICATION  exact per cell. The decomposition is arithmetic on four measured MDEs -- a
                DERIVATION whose inputs are measurements, labelled as such.
SCOPE           250 prompts, r04 cache + R257's measured batch noise resampled with replacement.
                400 replicates per dose in EVERY cell, so replicate count is not a third factor.
                baseline: R268's (0.10, 0.12] and R274's [0.1250, 0.1250] must appear as corners.
WORLDS          W-CALIBRATION  the calibration term carries most of the shift -> no replication
                                 that reuses the calibration could have caught it, R269 included
                W-GRID         the grid term carries it
                W-CANCEL       both large and opposite -> R268's number was near-right FOR THE
                                 WRONG REASON, and every uncorrected cell in this arc is
                                 unpredictable rather than merely biased
KILL            pre-registered: the (0.02, 200) corner must reproduce R268's bracket and the
                (0.005, 3000) corner must reproduce R274's, or the 2x2 is not measuring the same
                object and no decomposition is readable. Then whichever main effect exceeds the
                other by more than one coarse grid step (0.02) is named the carrier; if neither
                does, W-CANCEL.
POSITIVE CTRL   in every cell, the largest dose beats the lowest by > 3 binomial se. Computed.
NEGATIVE CTRL   held-out alpha per cell on fresh replicates. The 200-draw cells are EXPECTED to
                miss 0.05 -- that is the defect under study, not a failure -- and are reported
                with their alpha rather than excluded.
SHAM            R269's SHAM-B (plant aimed at the TARGET) in the reference cell; the only failable
                sham established for this statistic.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     binomial se at 400 replicates near 0.8 = 0.0200, identical across cells by design.
MULTIPLICITY    4 cells x up to 41 doses x 400 replicates.
SPECIFICATION   the two axes ARE the specification; nothing else moves.
ARTIFACT        all four curves, taus and alphas persisted.
IMPOSSIBLE      what R269 would have found had it varied these. This measures what the choices are
                worth, not what a counterfactual reviewer would have done.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402
import json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
DUPS = round_results("R257", "instruments.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
REPS = 400
ALPHA = 0.05
CELLS = [(0.02, 200), (0.02, 3000), (0.005, 200), (0.005, 3000)]
R268 = (0.10, 0.12)
R274 = (0.1250, 0.1250)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def wil(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(DUPS, allow_pickle=True)
    sat, ntask = d["sat"], int(d["n_tasks"][0])
    delta = (sat[ntask:ntask + 200] - sat[:200]).astype(float)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    P = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 14):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        P.append((W, S))
        if len(P) >= 250:
            break
    print("prompts %d | 400 replicates per dose in EVERY cell, so replicates are not a factor\n"
          % len(P), flush=True)

    def arm(g, rng, mode="real"):
        hit = 0
        for W, S in P:
            Sn = np.clip(S + rng.choice(delta, size=S.shape), 0, 1)
            cf = cls((W[:, None] * Sn).sum(0))
            idx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
            cr = cls((W[idx, None] * Sn[idx]).sum(0))
            ok_ = (cr == cf)
            if mode == "real" and rng.random() < g:
                ok_ = True
            elif mode == "shamB" and rng.random() < g:
                jdx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
                ok_ = (cr == cls((W[jdx, None] * Sn[jdx]).sum(0)))
            hit += int(ok_)
        return hit / len(P)

    cells = {}
    for step, ncal in CELLS:
        doses = [round(step * i, 4) for i in range(int(0.2001 / step) + 1)]
        cal = np.array([arm(0.0, np.random.default_rng(13_000 + i)) for i in range(ncal)])
        tau = float(np.quantile(cal, 1 - ALPHA))
        hold = np.array([arm(0.0, np.random.default_rng(93_000 + i)) for i in range(600)])
        ah = float((hold > tau).mean())
        curve = {}
        for g in doses:
            v = np.array([arm(g, np.random.default_rng(35_000 + int(g * 10000) * 977 + i))
                          for i in range(REPS)])
            curve[g] = float((v > tau).mean())
        ci = {g: wil(round(curve[g] * REPS), REPS) for g in doses}
        up = [g for g in doses if ci[g][1] >= 0.8]
        dn = [g for g in doses if ci[g][0] >= 0.8]
        lo = min(up) if up else float("inf")
        hi = min(dn) if dn else float("inf")
        g0, top = curve[doses[0]], curve[doses[-1]]
        se0 = math.sqrt(max(g0, 1e-9) * (1 - g0) / REPS)
        cells[(step, ncal)] = {"tau": tau, "alpha": ah, "mde": [lo, hi], "curve": curve,
                               "pos_ok": bool((top - g0) > 3 * se0), "cal_sd": float(cal.std())}
        print(" grid %.3f  cal %4d : tau %.4f  alpha %.4f  MDE [%s, %s]  positive %s"
              % (step, ncal, tau, ah,
                 "%.4f" % lo if up else "none", "%.4f" % hi if dn else "none",
                 "OK" if cells[(step, ncal)]["pos_ok"] else "FAILED"), flush=True)

    print("\n=== the 2x2, MDE upper bound ===")
    print("%-12s %14s %14s" % ("", "cal 200", "cal 3000"))
    for step in (0.02, 0.005):
        print("%-12s %14.4f %14.4f"
              % ("grid %.3f" % step, cells[(step, 200)]["mde"][1], cells[(step, 3000)]["mde"][1]))

    print("\n=== controls ===")
    ref = cells[(0.005, 3000)]
    refd = [round(0.005 * i, 4) for i in range(41)]
    shb = float((np.array([arm(refd[-1], np.random.default_rng(82_000 + i), mode="shamB")
                           for i in range(REPS)]) > ref["tau"]).mean())
    sham_ok = shb < ref["curve"][refd[-1]] - 0.10
    print(" SHAM-B (reference cell) : %.4f vs real %.4f -> %s"
          % (shb, ref["curve"][refd[-1]], "OK" if sham_ok else "DID NOT FALL"))
    r1 = arm(0.0, np.random.default_rng(999)); r2 = arm(0.0, np.random.default_rng(999))
    print(" PLACEBO %.6f  %s" % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))
    print(" NEGATIVE the 200-draw cells' alpha : %.4f and %.4f -- EXPECTED to miss 0.05; that is"
          % (cells[(0.02, 200)]["alpha"], cells[(0.005, 200)]["alpha"]))
    print("          the defect under study, reported rather than excluded.")
    corner_ok = (R268[0] <= cells[(0.02, 200)]["mde"][1] <= R268[1] + 0.021
                 and abs(cells[(0.005, 3000)]["mde"][1] - R274[1]) < 0.011)
    print(" CORNERS  (0.02,200) reproduces R268's bracket and (0.005,3000) reproduces R274's : %s"
          % ("OK" if corner_ok else "THE 2x2 IS NOT MEASURING THE SAME OBJECT"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    m = {k: cells[k]["mde"][1] for k in cells}
    grid_eff = 0.5 * ((m[(0.005, 200)] - m[(0.02, 200)]) + (m[(0.005, 3000)] - m[(0.02, 3000)]))
    cal_eff = 0.5 * ((m[(0.02, 3000)] - m[(0.02, 200)]) + (m[(0.005, 3000)] - m[(0.005, 200)]))
    inter = (m[(0.005, 3000)] - m[(0.005, 200)]) - (m[(0.02, 3000)] - m[(0.02, 200)])
    print(" GRID main effect        %+.4f   (0.02 -> 0.005)" % grid_eff)
    print(" CALIBRATION main effect %+.4f   (200 -> 3000 draws)" % cal_eff)
    print(" interaction             %+.4f" % inter)
    if not all(cells[k]["pos_ok"] for k in cells) or not sham_ok or not corner_ok:
        v = ("UNVERIFIED -- a control did not behave (positives %s, sham %s, corners %s)."
             % ([cells[k]["pos_ok"] for k in cells], sham_ok, corner_ok))
    elif abs(cal_eff) - abs(grid_eff) > 0.02:
        v = ("W-CALIBRATION -- the calibration term carries the shift (%+.4f against the grid's "
             "%+.4f). NO REPLICATION THAT REUSES THE CALIBRATION COULD HAVE CAUGHT IT, and R269 "
             "reused it. Its confirmation of R268 tested the shams and nothing else -- which is "
             "exactly what it varied." % (cal_eff, grid_eff))
    elif abs(grid_eff) - abs(cal_eff) > 0.02:
        v = ("W-GRID -- the grid term carries the shift (%+.4f against the calibration's %+.4f)."
             % (grid_eff, cal_eff))
    else:
        v = ("W-CANCEL -- neither term dominates by more than one coarse step: grid %+.4f, "
             "calibration %+.4f, interaction %+.4f. R268's number was near-right FOR THE WRONG "
             "REASON -- two biases of comparable size and opposite sign -- which means an "
             "uncorrected cell in this arc is UNPREDICTABLE rather than merely biased, and that is "
             "worse than a known direction." % (grid_eff, cal_eff, inter))
    print("\n  " + v)
    json.dump({"prompts": len(P), "cells": {"g%.3f_c%d" % k: {kk: vv for kk, vv in c.items()
                                                              if kk != "curve"}
                                            for k, c in cells.items()},
               "grid_effect": grid_eff, "cal_effect": cal_eff, "interaction": inter,
               "shamB": shb, "corner_ok": bool(corner_ok), "verdict": v},
              open(OUT / "replication_2x2.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
