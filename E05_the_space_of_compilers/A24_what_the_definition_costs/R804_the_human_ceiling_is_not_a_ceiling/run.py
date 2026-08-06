#!/usr/bin/env python3
"""R804 · the human ceiling is not a ceiling — the exact attainable maximum of A2.

CHECK #406 read the source of the number R803's NEXT called a ceiling. `whose_verdicts.py:65`
computes CEIL_H = a2(annotator_i, annotator_j) — noise on BOTH sides — while an arm is a
DETERMINISTIC predictor scored against each annotator. A noiseless predictor of the human central
tendency beats pair-agreement by construction, so "above the human ceiling" is a units error and not
a finding. The real ceiling is exactly computable: 4 responses admit 75 weak orders, so the supremum
of A2 over ALL scoring functions is a brute-force max per prompt.

ESTIMAND        E1 ⭐ CEIL_ATT exactly · E2 ⭐ the 27 arms on floor→CEIL_H→CEIL_ATT · E3 ⭐ annotator
                equivalents · E4 the tie decomposition
IDENTIFICATION  E1 exact and FORCED (arm ≤ CEIL_ATT is algebra, so it is a CODE CHECK not evidence)
DERIVED FIRST   D1 two noisy raters agree less than a noiseless one · D2 a strict predictor forfeits
                the tie mass outright · D3 CEIL_PLUR ≥ CEIL_ATT, gap = human intransitivity ·
                D4 the k-curve must be monotone
WORLDS          A units error · B the arms saturate · C the excess is ties — B checked FIRST
CONTROLS        OBJECT (CEIL_H reproduced by its own method + the forced inequality) · PLACEBO
                (constant → the tie rate, derived) · POSITIVE (one annotator as predictor → CEIL_H)
                · NEGATIVE (annotators shuffled across prompts) · NOISE FLOOR
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
R803 = ARC / "R803_the_judge_free_floor_on_release_one/results/judge_free_floor.json"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 2.801585
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def weak_orders():
    """Every distinct 6-sign pattern realisable by a real-valued score on 4 responses."""
    seen = {}
    for v in itertools.product(range(4), repeat=4):
        s = tuple(int(np.sign(v[i] - v[j])) for i, j in PR)
        seen.setdefault(s, v)
    return np.array(sorted(seen)), len(seen)


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "an ARM",
           "e1_unit": "a PROMPT"}
    W, NW = weak_orders()
    print(f"  WEAK ORDERS on 4 responses: {NW}   (ordered Bell number a(4) = 75)")
    if NW != 75:
        print("  UNRUNNABLE: the enumeration is wrong; the ceiling would be approximate. Exit 2.")
        return 2

    # ================= OBJECT =====================================================================
    print("\n  OBJECT CHECK")
    targets, _ = load_targets()
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in targets and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]

    # reproduce CEIL_H by R793's OWN method (run.py:174-183): EXHAUSTIVE over all annotator
    # pairs on this population — NOT the 3-draw sample `whose_verdicts.py` ships.
    # ⚠ `cls` returns a TUPLE: `np.mean(tuple == tuple)` is one scalar bool, not an elementwise
    # rate. The first version of this check did that, returned 0.083488, and exited 2.
    ceil_pairs = []
    for a in range(P):
        C = HC[a]
        n = len(C)
        m = np.array([[float((C[i] == C[j]).mean()) for j in range(n)] for i in range(n)])
        iu = np.triu_indices(n, 1)
        ceil_pairs.append(m[iu].mean())
    CEIL_H = float(np.mean(ceil_pairs))
    # and what the SHIPPED script computes instead: one random pair per prompt, 3 seeds
    samp = {}
    for lab, keys in (("sorted", pids), ("insertion", [q for q in targets if q in set(pids)])):
        ch = []
        for sd in (0, 1, 2):
            rng0 = np.random.default_rng(500 + sd)
            for q in keys:
                v = targets[q]
                i, j = rng0.choice(len(v), 2, replace=False)
                ci = np.array(cls(np.array(v[i][0], float)))
                cj = np.array(cls(np.array(v[j][0], float)))
                ch.append(float(np.mean(ci == cj)))
        samp[lab] = float(np.mean(ch))
    print(f"     ⚠ `whose_verdicts.py`'s SHIPPED sampled ceiling: {samp['sorted']:.6f} (sorted) / "
          f"{samp['insertion']:.6f} (insertion order) — it is dict-order dependent and neither "
          f"equals the committed {CEIL_H:.6f}")
    out["ceil_h_sampled"] = samp
    okh = abs(CEIL_H - 0.551880) < 1e-6
    print(f"     CEIL_H reproduced by its own method: {CEIL_H:.6f} vs R793's committed 0.551880"
          f"   {'PASS' if okh else 'FAIL'}")
    if not okh or P < 900:
        print("  UNRUNNABLE: the number under audit did not reproduce. Exit 2, never 0.")
        return 2

    # ================= E1 · the exact attainable ceiling ==========================================
    print("\n  E1 - THE EXACT ATTAINABLE CEILING  (max over all 75 weak orders, per prompt)")
    att = np.zeros(P)
    plur = np.zeros(P)
    tie_rate = np.zeros(P)
    for a in range(P):
        H = HC[a]                                   # (n_ann, 6)
        agree = (H[None, :, :] == W[:, None, :]).mean(axis=1)      # (75, 6)
        att[a] = agree.mean(axis=1).max()
        # unconstrained per-pair plurality: best sign per pair, ignoring transitivity
        plur[a] = np.mean([max((H[:, q] == s).mean() for s in (-1, 0, 1)) for q in range(6)])
        tie_rate[a] = (H == 0).mean()
    CEIL_ATT = float(att.mean())
    CEIL_PLUR = float(plur.mean())
    TIE = float(tie_rate.mean())
    print(f"     ⭐ CEIL_ATT  (any scoring function, exact)      {CEIL_ATT:.6f}")
    print(f"        CEIL_PLUR (per-pair plurality, ignores transitivity, an UPPER bound) "
          f"{CEIL_PLUR:.6f}")
    print(f"        D3 gap = human INTRANSITIVITY cost           {CEIL_PLUR - CEIL_ATT:+.6f}")
    print(f"        CEIL_H   (one annotator vs another)          {CEIL_H:.6f}")
    print(f"        human tie rate                               {TIE:.10f}")
    out["e1"] = {"ceil_att": CEIL_ATT, "ceil_plur": CEIL_PLUR, "ceil_h": CEIL_H,
                 "intransitivity": CEIL_PLUR - CEIL_ATT, "tie_rate": TIE, "prompts": P,
                 "weak_orders": NW, "att_per_prompt": att}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    # PLACEBO — a constant predictor is the all-tied weak order; must equal the tie rate exactly
    const = np.zeros(6, int)
    plac = float(np.mean([float((HC[a] == const).mean()) for a in range(P)]))
    plac_ok = abs(plac - TIE) < 1e-12
    print(f"     PLACEBO   constant predictor (all ties): {plac:.10f}   human tie rate {TIE:.10f}"
          f"   {'PASS - identical, DERIVED not fitted' if plac_ok else 'FAIL'}")
    # POSITIVE — one annotator used as a PREDICTOR must land at CEIL_H
    rng = np.random.default_rng(4242)
    ann_as_pred = []
    for a in range(P):
        H = HC[a]
        i = rng.integers(len(H))
        others = np.delete(np.arange(len(H)), i)
        ann_as_pred.append(float((H[others] == H[i]).mean()))
    APRED = float(np.mean(ann_as_pred))
    pos_ok = abs(APRED - CEIL_H) < 0.02 and plac < APRED < CEIL_ATT
    print(f"     POSITIVE  one annotator AS A PREDICTOR: {APRED:.6f}  vs CEIL_H {CEIL_H:.6f}"
          f"   band {plac:.4f} < t < {CEIL_ATT:.4f}   {'PASS' if pos_ok else 'FAIL'}")
    NF_GUESS = 0.002          # R803-scale annotator noise; the band only has to exclude noise
    # NEGATIVE — ⛔ THE FIRST VERSION OF THIS CONTROL COULD NOT FAIL. It permuted which PROMPT an
    # annotator-set attached to; CEIL_ATT is a per-prompt max, so that permutes the multiset of
    # per-prompt values and leaves the mean EXACTLY invariant (measured: 0.686265 -> 0.686265).
    # CEIL_ATT has no cross-prompt structure to destroy. What it measures is WITHIN-prompt
    # annotator concentration, so that is what the control must break: each annotator slot is
    # filled from a DIFFERENT prompt.
    rngn = np.random.default_rng(909)
    negv = np.zeros(P)
    for a in range(P):
        n = len(HC[a])
        H = np.array([HC[rngn.integers(P)][0] for _ in range(n)])
        agree = (H[None, :, :] == W[:, None, :]).mean(axis=1)
        negv[a] = agree.mean(axis=1).max()
    NEG = float(negv.mean())
    # the floor this control should approach: the best CONSTANT weak order over the whole corpus
    allH = np.concatenate([HC[a] for a in range(P)], axis=0)
    BESTC = float(((allH[None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max())
    neg_ok = NEG < CEIL_ATT - 10 * NF_GUESS
    print(f"     NEGATIVE  each annotator slot filled from a DIFFERENT prompt: CEIL_ATT "
          f"{CEIL_ATT:.6f} -> {NEG:.6f}   (best single constant weak order corpus-wide "
          f"{BESTC:.6f})   {'PASS' if neg_ok else 'FAIL'}")
    # NOISE FLOOR — annotator split-half on CEIL_ATT
    rngf = np.random.default_rng(77)
    draws = []
    for _ in range(20):
        v = np.zeros(P)
        for a in range(P):
            H = HC[a]
            idx = rngf.permutation(len(H))
            h = H[idx[:max(1, len(H) // 2)]]
            agree = (h[None, :, :] == W[:, None, :]).mean(axis=1)
            v[a] = agree.mean(axis=1).max()
        draws.append(v.mean())
    NF = float(np.std(draws))
    print(f"     NOISE FLOOR  annotator split-half on CEIL_ATT, 20 draws: sd {NF:.6f}")
    gate = okh and plac_ok and pos_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": plac, "placebo_ok": plac_ok, "positive": APRED,
                       "positive_ok": pos_ok, "negative": NEG, "negative_ok": neg_ok,
                       "noise_floor": NF, "gate": gate}

    # ================= E2 · where the arms sit ====================================================
    print("\n  E2 - WHERE THE 27 ARMS SIT")
    lad = json.loads(R789.read_text())["e2"]["a2"]
    fl = json.loads(R803.read_text())
    FLOOR = float(fl["e1"]["floor"]) if "floor" in fl.get("e1", {}) else 0.4557
    arms = {}
    for name in sorted(lad):
        f = RES / f"sat_{name}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not all(p in S for p in pids):
            continue
        cl = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids])
        arms[name] = np.array([(HC[a] == cl[a]).mean() for a in range(P)])
    print(f"     arms recomputed on this population: {len(arms)}")
    viol = [k for k, v in arms.items() if v.mean() > CEIL_ATT + 1e-12]
    print(f"     ⛔ FORCED CHECK (a DERIVATION, never evidence): every arm is a scoring function, so "
          f"arm ≤ CEIL_ATT is algebra.  violations: {len(viol)}   {'PASS' if not viol else viol}")
    if viol:
        print("  UNRUNNABLE: an arm exceeded an exact supremum. The code is wrong. Exit 2.")
        return 2
    order = sorted(arms, key=lambda k: -arms[k].mean())
    rngb = np.random.default_rng(1234)
    idx = rngb.integers(0, P, size=(NBOOT, P))
    rows, pv = [], []
    for k in order:
        d = att - arms[k]                       # headroom to the exact ceiling, paired
        bs = d[idx].mean(axis=1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        t = d.mean() / (bs.std(ddof=1) + 1e-18)
        pv.append(2 * (1 - 0.5 * (1 + math.erf(abs(t) / np.sqrt(2)))) if abs(t) < 40 else 0.0)
        rows.append({"arm": k, "a2": float(arms[k].mean()), "headroom": float(d.mean()),
                     "lo": float(lo), "hi": float(hi),
                     "share_of_range": float((arms[k].mean() - FLOOR) / (CEIL_ATT - FLOOR)),
                     "above_ceil_h": bool(arms[k].mean() > CEIL_H)})
    keep = bh(pv)
    for r, kp in zip(rows, keep):
        r["bh"] = bool(kp)
    top = rows[0]
    nab = sum(r["above_ceil_h"] for r in rows)
    print(f"     floor(R803) {FLOOR:.4f}  <  CEIL_H {CEIL_H:.4f}  <  best arm "
          f"{top['a2']:.4f}  <  CEIL_ATT {CEIL_ATT:.4f}")
    print(f"     ⭐ arms ABOVE CEIL_H: {nab} of {len(rows)}   arms above CEIL_ATT: 0 (forced)")
    for r in rows[:4] + rows[-2:]:
        print(f"        {r['arm']:<22} {r['a2']:.4f}   headroom to ceiling "
              f"{r['headroom']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]   "
              f"share of attainable range {100 * r['share_of_range']:.1f}%   "
              f"BH {'keep' if r['bh'] else 'drop'}")
    print(f"     BH q=0.05: {int(keep.sum())} of {len(rows)} survive; "
          f"{len(rows) - int(keep.sum())} do not (reported, not hidden)")
    out["e2"] = {"floor": FLOOR, "rows": rows, "above_ceil_h": nab,
                 "bh_survivors": int(keep.sum())}

    # ================= E3 · annotator equivalents =================================================
    print("\n  E3 - ANNOTATOR-EQUIVALENTS  (k-consensus as a predictor, scored on a HELD-OUT half)")
    print("     ⛔ THE FIRST ESTIMATOR WAS NON-MONOTONE AND D4 CAUGHT IT. `np.sign(sum of sign "
          "vectors)` TIES whenever k annotators split evenly, and a tie can never match a strict "
          "held-out sign — so even k is penalised and the curve saws: 0.5516 / 0.5040 / 0.5898 / "
          "0.5784 at k = 1/2/3/4. Both estimators are reported.")
    YV = [np.array([np.array(y, float) for y, _ in targets[p]]) for p in pids]
    KS = [1, 2, 3, 4, 6, 8, 12]
    curves = {"signsum": {}, "meanscore": {}}
    sds = {}
    for est in curves:
        rngk = np.random.default_rng(31337)
        for k in KS:
            vals = []
            for _ in range(16):
                v = []
                for a in range(P):
                    H, Y = HC[a], YV[a]
                    n = len(H)
                    pm = rngk.permutation(n)
                    half = max(1, n // 2)
                    heldout = H[pm[:half]]
                    pool = pm[half:]
                    if len(pool) < 1:
                        continue
                    take = pool[:min(k, len(pool))]
                    if est == "signsum":
                        cons = np.sign(H[take].sum(axis=0))
                    else:                       # a real scoring function, as every arm is
                        cons = np.array(cls(Y[take].mean(axis=0)))
                    v.append(float((heldout == cons).mean()))
                vals.append(np.mean(v))
            curves[est][k] = float(np.mean(vals))
            sds.setdefault(est, {})[k] = float(np.std(vals, ddof=1))
    for k in KS:
        print(f"     k = {k:>2}   sign-sum {curves['signsum'][k]:.6f}   "
              f"⭐ mean-score {curves['meanscore'][k]:.6f} ± {sds['meanscore'][k]:.6f}")
    curve = curves["meanscore"]
    mono = {e: all(curves[e][KS[i]] <= curves[e][KS[i + 1]] + 1e-9 for i in range(len(KS) - 1))
            for e in curves}
    print(f"     D4 monotone in k:  sign-sum {mono['signsum']}   mean-score {mono['meanscore']}"
          f"   {'PASS on the reported estimator' if mono['meanscore'] else '⚠ FAIL - do NOT read equivalents off it'}")
    if not mono["meanscore"]:
        print("     ⚠ E3 REPORTS THE CURVE ONLY. No annotator-equivalent is quoted.")

    # arms rescored against the SAME held-out halves, so the target is identical
    rnga = np.random.default_rng(31338)
    arm_ho = {}
    for k in order:
        S = load_sat(RES / f"sat_{k}.npz")
        cl = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids])
        vv = []
        for _ in range(8):
            v = []
            for a in range(P):
                H = HC[a]
                pm = rnga.permutation(len(H))
                heldout = H[pm[:max(1, len(H) // 2)]]
                v.append(float((heldout == cl[a]).mean()))
            vv.append(np.mean(v))
        arm_ho[k] = float(np.mean(vv))

    def equiv(x):
        if not mono["meanscore"]:
            return None
        ks = sorted(curve)
        if x <= curve[ks[0]]:
            return float(ks[0]) * x / max(curve[ks[0]], 1e-12)
        for i in range(len(ks) - 1):
            if curve[ks[i]] <= x <= curve[ks[i + 1]]:
                f = (x - curve[ks[i]]) / max(curve[ks[i + 1]] - curve[ks[i]], 1e-12)
                return ks[i] + f * (ks[i + 1] - ks[i])
        return float("inf")

    kcross = equiv(CEIL_H)
    # ⚠ the pre-registered ESTIMAND was "does a k<=3 consensus beat CEIL_H"; `equiv()` was a
    # METHOD for it that global non-monotonicity made unfit. The estimand is directly evaluable:
    k3_beats = curves["meanscore"][3] > CEIL_H
    print(f"     ⭐ the pre-registered estimand, evaluated DIRECTLY (no interpolation, no "
          f"monotonicity needed): a 3-annotator consensus scores "
          f"{curves['meanscore'][3]:.6f} vs CEIL_H {CEIL_H:.6f}  ->  beats it: {k3_beats}")
    print(f"        and k=1 lands at {curves['meanscore'][1]:.6f}, i.e. CEIL_H IS the k=1 point "
          f"(|Δ| {abs(curves['meanscore'][1] - CEIL_H):.6f})")
    for k in order[:3] + order[-1:]:
        e = equiv(arm_ho[k])
        es = "n/a (curve not monotone)" if e is None else (">12" if e == float("inf")
                                                           else f"{e:.2f}")
        print(f"        {k:<22} held-out A2 {arm_ho[k]:.4f}  ->  {es} annotator-equivalents")
    out["e3"] = {"curves": curves, "curve_sd": sds, "k3_beats_ceil_h": bool(k3_beats),
                 "monotone": mono, "arm_heldout": arm_ho,
                 "ceil_h_equivalents": kcross,
                 "arm_equivalents": {k: (None if equiv(arm_ho[k]) in (None, float("inf"))
                                         else equiv(arm_ho[k])) for k in order}}

    # ================= E5 · the GENERALISING ceiling ==============================================
    print("\n  E5 - THE ORACLE CEILING IS IN-SAMPLE; THE GENERALISING ONE IS LOWER")
    print("     CEIL_ATT picks each prompt's best weak order AFTER seeing that prompt's "
          "annotators. No predictor that must generalise can attain it, so it is an UPPER bound "
          "and never a target. The honest comparator fits on half the annotators and scores on "
          "the other half.")
    rngo = np.random.default_rng(2718)
    hov = []
    for _ in range(8):
        v = np.zeros(P)
        for a in range(P):
            H = HC[a]
            pm = rngo.permutation(len(H))
            half = max(1, len(H) // 2)
            fit, ev = H[pm[half:]], H[pm[:half]]
            if len(fit) == 0:
                fit = H
            best = ((fit[None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).argmax()
            v[a] = float((ev == W[best]).mean())
        hov.append(v.mean())
    CEIL_HO = float(np.mean(hov))
    print(f"     ⭐ CEIL_ATT (in-sample oracle) {CEIL_ATT:.6f}   CEIL_HO (held-out oracle) "
          f"{CEIL_HO:.6f}   optimism {CEIL_ATT - CEIL_HO:+.6f}")
    print(f"        best arm {top['a2']:.4f} is {100 * (top['a2'] - FLOOR) / (CEIL_HO - FLOOR):.1f}% "
          f"of the GENERALISING range, vs "
          f"{100 * (top['a2'] - FLOOR) / (CEIL_ATT - FLOOR):.1f}% of the in-sample one")
    out["e5"] = {"ceil_att": CEIL_ATT, "ceil_ho": CEIL_HO, "optimism": CEIL_ATT - CEIL_HO,
                 "top_share_generalising": (top["a2"] - FLOOR) / (CEIL_HO - FLOOR)}

    # ================= E4 · the tie decomposition =================================================
    print("\n  E4 - TIES: where each score comes from")
    tied = [HC[a] == 0 for a in range(P)]
    def split(cl_per_prompt):
        t, s = [], []
        for a in range(P):
            m = tied[a]
            hit = (HC[a] == cl_per_prompt[a])
            t.append(hit[m].mean() if m.any() else np.nan)
            s.append(hit[~m].mean() if (~m).any() else np.nan)
        return float(np.nanmean(t)), float(np.nanmean(s))
    # an arm (strict scores) vs an annotator (can tie)
    kbest = order[0]
    S = load_sat(RES / f"sat_{kbest}.npz")
    clb = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids])
    at, as_ = split(clb)
    # CEIL_H's own decomposition: one annotator as predictor
    rngt = np.random.default_rng(555)
    ht, hs = [], []
    for a in range(P):
        H = HC[a]
        i = rngt.integers(len(H))
        others = np.delete(np.arange(len(H)), i)
        m = H[others] == 0
        hit = (H[others] == H[i])
        ht.append(hit[m].mean() if m.any() else np.nan)
        hs.append(hit[~m].mean() if (~m).any() else np.nan)
    HT, HS = float(np.nanmean(ht)), float(np.nanmean(hs))
    print(f"     on human-TIED pairs      best arm ({kbest}) {at:.4f}   one annotator {HT:.4f}")
    print(f"     on human-STRICT pairs    best arm ({kbest}) {as_:.4f}   one annotator {HS:.4f}")
    print(f"     ⭐ the arm's advantage over CEIL_H on STRICT pairs alone: {as_ - HS:+.4f}")
    print(f"        D2 holds: a strict predictor scores {at:.4f} on tied pairs — it forfeits that "
          f"mass, and still wins overall")
    out["e4"] = {"arm": kbest, "arm_tied": at, "arm_strict": as_, "ann_tied": HT, "ann_strict": HS,
                 "strict_advantage": as_ - HS}

    # ================= THE KILL ===================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif top["a2"] >= 0.98 * CEIL_ATT:
        world = "B"
    elif as_ - HS <= 0:
        world = "C"
    elif CEIL_ATT - top["a2"] > 0.02 and k3_beats:
        world = "A"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   top arm {top['a2']:.4f} vs 0.98*CEIL_ATT "
          f"{0.98 * CEIL_ATT:.4f}   strict advantage {as_ - HS:+.4f}   k=3 beats CEIL_H "
          f"{k3_beats}"
          f"  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/ceiling.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
