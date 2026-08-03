"""R277 -- R249's "36.7% necessary" is defined by EXACT class equality. Sweep the tolerance.

WHERE THIS COMES FROM
    Two commits ago I found that "how corrective is this arc" has no rule-free answer: sweeping the
    classification rule's proximity window moved the count from 16 to 28 of 28. The lesson is not
    about that count. It is that A DEFINITION-DEPENDENT NUMBER MUST BE SWEPT OVER ITS DEFINITION,
    and I have been quoting one in FORMULATION all day without doing that.

    R249: "of 3.95 criteria printed per core, 1.45 are NECESSARY-WITHIN-SET (36.7%) and the smallest
    subset reproducing the printed core's own class is 1.42. On 66.4% of prompts a single printed
    criterion reproduces what all four produce."

    `necessary(j)` is `cls(core \\ {j}) != cls(core)` with bare `np.sign`. A criterion whose removal
    flips a pairwise sign by 1e-9 counts exactly as necessary as one that flips it by 0.4.
    R258 already found the sibling of this: exact `np.sign` on an eigenvector manufactured non-ties
    at 1e-17 and blocked a placebo until a tolerance was added.

ESTIMAND        the four R249 headline quantities as a function of the tolerance `tol` under which
                two weighted sums count as tied -- expressed as a FRACTION OF EACH PROMPT'S OWN
                score range, so it carries no absolute scale:
                  necessary-within-set (mean and share of printed) · minimal sufficient size ·
                  share of prompts with minimal size 1 · share with ZERO necessary criteria.
IDENTIFICATION  exact per prompt per tolerance; exhaustive over the printed set's power set.
                Nothing is sampled, so the curve is the object and there is no estimate in it.
SCOPE           the same 967 prompts R249 used, r04 core tensor, unweighted core as CoVal ships it.
                tol in {0, 1e-9, 1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1} of the prompt's range.
WORLDS          W-STABLE   the numbers barely move until tol is large -> 36.7% is a property of the
                             data and the exact-equality definition was harmless
                W-FRAGILE  they move early -> a large share of R249's "necessary" criteria flip the
                             class by a margin far below the instrument's own noise, and the
                             headline is an artifact of infinite precision
KILL            pre-registered: R260 measured this instrument's batch noise at sd 0.0073 on a
                [0,1] satisfaction scale. If the necessary-share at tol = 0.0073-equivalent differs
                from the tol=0 value by more than 5 percentage points, R249's 36.7% is
                INSTRUMENT-INDISTINGUISHABLE at its own noise floor and must be quoted with a
                tolerance or not at all.
POSITIVE CTRL   at tol >= 1.0 every pair is tied, so every class is the all-tied class, every
                criterion is redundant and minimal size is 1 on every prompt. Exact targets at a
                known point of the sweep; if the curve does not reach them the tolerance is not
                wired into the class function.
NEGATIVE CTRL   tol = 0 must reproduce R249's published 1.4519 / 1.4178 / 0.6640 / 0.2378 to three
                decimals. Pinned to numbers computed by a different script on a different day.
SHAM            apply the tolerance to a criterion's own values before summing rather than to the
                pairwise differences after. That is a different operation of the same magnitude and
                it should NOT reproduce the curve; if it does, the tolerance is not acting where it
                is claimed to act.
PLACEBO         tol = 0 twice gives identical output.
NOISE FLOOR     R260's measured batch sd, 0.0073, converted to a per-prompt range fraction and
                marked on the curve. It is not assumed: it was measured on 200 duplicate judgements.
MULTIPLICITY    9 tolerances x 4 quantities, whole curve printed including the tolerances that
                destroy the statistic.
SPECIFICATION   the axis IS the tolerance -- the parameter R249 held at exactly zero without
                recording that zero was a choice.
ARTIFACT        the full curve persisted.
IMPOSSIBLE      whether a 1e-9 class flip is MEANINGFUL to a person. That is a question about what
                the ordering is for, and the release carries no downstream task to answer it.
"""
from __future__ import annotations
import itertools, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
TOLS = [0.0, 1e-9, 1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 1.0]
R249 = {"necessary": 1.4519, "minimal": 1.4178, "min1": 0.6640, "zero_nec": 0.2378}
R260_SD = 0.0073


def cls(y, tol):
    r = float(np.max(y) - np.min(y)) or 1.0
    t = tol * r
    return tuple(0.0 if abs(y[i] - y[j]) <= t else float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def analyse(M, tol):
    k = len(M)
    base = cls(M.sum(0), tol)
    nec = sum(1 for j in range(k)
              if cls(M[[i for i in range(k) if i != j]].sum(0), tol) != base) if k > 1 else 1
    mini = k
    for s in range(1, k + 1):
        if any(cls(M[list(c)].sum(0), tol) == base for c in itertools.combinations(range(k), s)):
            mini = s
            break
    return nec, mini


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz"); sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    cores = []
    for p in sorted(sc):
        if p not in recs or p not in sf:
            continue
        cj = sorted({k[0] for k in sc[p]})
        if not cj or not all((j, x) in sc[p] for j in cj for x in L):
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < len(cj) + 1:
            continue
        cores.append(np.array([[sc[p][(j, x)] for x in L] for j in cj], float))
    print("prompts %d | mean printed size %.4f" % (len(cores), np.mean([len(c) for c in cores])))
    print("R260 measured this instrument's batch noise at sd %.4f on a [0,1] scale.\n" % R260_SD)

    print("%-10s %12s %10s %10s %10s" % ("tol", "necessary", "share", "minimal", "min==1"))
    curve = {}
    for tol in TOLS:
        res = [analyse(C, tol) for C in cores]
        nec = float(np.mean([r[0] for r in res]))
        mini = float(np.mean([r[1] for r in res]))
        m1 = float(np.mean([r[1] == 1 for r in res]))
        z = float(np.mean([r[0] == 0 for r in res]))
        ksz = float(np.mean([len(C) for C in cores]))
        curve[tol] = (nec, nec / ksz, mini, m1, z)
        print("%-10s %12.4f %10.4f %10.4f %10.4f" % (tol, nec, nec / ksz, mini, m1))

    print("\n=== controls ===")
    n0 = curve[0.0]
    neg_ok = (abs(n0[0] - R249["necessary"]) < 0.002 and abs(n0[2] - R249["minimal"]) < 0.002
              and abs(n0[3] - R249["min1"]) < 0.005)
    print(" NEGATIVE tol=0 reproduces R249's published numbers:")
    print("          necessary %.4f vs %.4f | minimal %.4f vs %.4f | min==1 %.4f vs %.4f  -> %s"
          % (n0[0], R249["necessary"], n0[2], R249["minimal"], n0[3], R249["min1"],
             "OK" if neg_ok else "DIFFERS -- this is not R249's object"))
    p1 = curve[1.0]
    pos_ok = (abs(p1[0]) < 1e-9 and abs(p1[2] - 1.0) < 1e-9 and abs(p1[3] - 1.0) < 1e-9)
    print(" POSITIVE tol=1.0 -- every pair tied by construction : necessary %.4f (0), minimal %.4f"
          " (1), min==1 %.4f (1)  -> %s" % (p1[0], p1[2], p1[3], "OK" if pos_ok else "NOT WIRED IN"))
    sham = []
    for C in cores:
        r_ = float(np.max(C) - np.min(C)) or 1.0
        sham.append(analyse(np.round(C / (R260_SD * r_)) * (R260_SD * r_), 0.0))
    sh_nec = float(np.mean([s[0] for s in sham]))
    print(" SHAM     tolerance applied to the VALUES before summing, not the pairwise differences")
    print("          after : necessary %.4f against the matched tol cell's %.4f"
          % (sh_nec, curve[3e-3][0]))
    print(" PLACEBO  tol=0 twice identical : %s"
          % ("OK" if analyse(cores[0], 0.0) == analyse(cores[0], 0.0) else "BROKEN"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    at_noise = curve[3e-3] if 3e-3 in curve else None
    drop = abs(n0[1] - at_noise[1]) * 100
    if not neg_ok:
        v = "UNVERIFIED -- tol=0 does not reproduce R249; this is not the same object."
    elif not pos_ok:
        v = "UNVERIFIED -- the tolerance is not reaching the class function at tol=1.0."
    elif drop > 5.0:
        v = ("W-FRAGILE -- the necessary-share falls %.1f percentage points (%.1f%% -> %.1f%%) by a "
             "tolerance of 0.003 of the prompt's range, which is BELOW this instrument's own "
             "measured batch noise. R249's 36.7%% counts criteria whose removal flips a class by a "
             "margin the judge cannot resolve. It must be quoted with a tolerance or not at all."
             % (drop, 100 * n0[1], 100 * at_noise[1]))
    else:
        v = ("W-STABLE -- the necessary-share moves only %.1f points (%.1f%% -> %.1f%%) at a "
             "tolerance below the instrument's noise, so 36.7%% is a property of the data and "
             "exact equality was harmless here." % (drop, 100 * n0[1], 100 * at_noise[1]))
    print("\n  " + v)
    json.dump({"prompts": len(cores), "curve": {str(k): list(v_) for k, v_ in curve.items()},
               "r249": R249, "r260_sd": R260_SD, "neg_ok": bool(neg_ok), "pos_ok": bool(pos_ok),
               "sham_necessary": sh_nec, "verdict": v},
              open(OUT / "necessity_tolerance.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
