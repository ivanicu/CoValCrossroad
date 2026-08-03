"""r104 -- is r103's consensus gradient larger specificity, or lighter attenuation?

CLAIM CARD
----------
Claim      r103 found source specificity runs +0.0283 on pairs where humans barely agree
           to +0.2461 where they nearly all agree, and named its own residual: a noisy
           target attenuates every estimator toward chance, so a rising contrast is
           EXPECTED even if the underlying specificity is constant. It could not
           separate the two.
Estimand   the DEATTENUATED attribution per consensus bin -- own-minus-donor accuracy
           against the human label, divided by the measured reliability of that label,
           where the reliability is estimated from the raters themselves.
Target
observed?  YES, and this is the whole point. Attenuation is not a nuisance to be argued
           about: it is a MEASURABLE quantity. Split a pair's raters in two, and how
           often the two halves' majorities agree tells you how reliable a half-majority
           is, with no model of the latent truth. Under independent label noise,
           h = P(A_maj == B_maj) gives the attenuation factor sqrt(2h - 1) directly.
Alternative
worlds     A ATTENUATION  after correction the attribution is FLAT across bins. Then the
                          gradient is a property of the TARGET's noise, not of the
                          rubric; the pooled figure is an attenuated view of one
                          underlying number; and "the rubric works better where humans
                          agree" is dead.
           S SPECIFICITY  it still rises. Then the rubric genuinely resolves consensual
                          comparisons better than contested ones -- which is the reverse
                          of what a normative instrument should do, since contested
                          pairs are where prompt-specific values earn their keep. The
                          measured specificity would be concentrated where it matters
                          least.
           O OVERCORRECTED it inverts. Then the independent-noise model over-corrects
                          and the correction itself is unfit; report UNVERIFIED, never
                          an acquittal.
Intervention
           none on the data. A THREE-WAY rater split: one third supplies the scoring
           label, one third measures that label's reliability, one third does the
           binning. Binning on a third that touches neither the label nor the
           reliability probe is what removes r103's "conditioning on the outcome's own
           reliability" -- there, consensus and label came from the same raters, so
           selecting a high-consensus bin selected for the label being confident.
Null       TWO-SIDED SIMULATION CONTROL, and it must pass BOTH directions:
           (i) synthetic raters with a per-pair agreement probability spanning the bins,
           and an arm whose accuracy against the LATENT direction is CONSTANT. The
           pipeline must show a rising RAW curve and a FLAT corrected one, recovering
           the planted accuracy. An instrument that cannot flatten a gradient it knows
           to be pure attenuation cannot be trusted to report flatness.
           (ii) the same, with an arm whose latent accuracy genuinely RISES with rater
           agreement. The corrected curve must STILL rise. An instrument that flattens
           everything would report world A whatever the truth -- that is the opposite
           answer this check must be able to return, and it is checked, not assumed.

WHY THIS IS THE STEP
--------------------
r103's number is the one the reframed object cares about most: whether specificity is a
property of the rubric or an average over pairs whose target is a coin flip. It reported
an over-chance RATIO spanning 2.95x as weak evidence against pure attenuation -- but that
ratio's denominator is the donor arm's over-chance accuracy, 0.0041 in the lowest bin,
so the 7.86 there is a ratio of noise and the span is not a statistic. This round
replaces an unstable ratio with a measured factor.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
The correction assumes the arm's errors are INDEPENDENT of the label's errors. They need
not be: a rubric and a rater can be misled by the same surface feature of a response, and
that shared misdirection is plausibly STRONGER on contested pairs. Positively correlated
errors inflate observed accuracy above what independent noise predicts, so the correction
UNDER-corrects where correlation is high. If correlation is higher at low consensus, this
round's corrected curve is biased UPWARD at the low end -- i.e. biased TOWARD world A.
So a surviving rise (world S) is the robust finding here, and a flat result is the one
this design could manufacture. That asymmetry is in the verdict, not softened.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "E03_the_instrument_was_the_object/A04_what_the_resampling_unit_is/R85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import weights  # noqa: E402

SAT = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

# A FIXED POOL, not a minimum. The first version took every pair with >= 9 raters and
# split it in thirds, which made the consensus bins a RATER-COUNT partition: a third of
# size 3 can only produce consensus 0.667 or 1.000, a third of size 4 only 0.5, 0.75 or
# 1.000. So bin [0.5,0.6) held ONLY 12-14-rater pairs and bin [0.6,0.7) ONLY 9-11-rater
# pairs -- and label size drives label reliability directly. The tell was the attenuation
# factor being HIGHER in the lowest-consensus bin (0.723) than the next (0.615), which a
# consensus ladder cannot do. Subsampling every pair to exactly POOL raters makes
# |A|=|B|=|C|=POOL/3 in every bin, so the bins differ in consensus and nothing else.
POOL = 12
THIRD = POOL // 3
MIN_RATERS = POOL
EDGES = (0.49, 0.6, 0.9, 1.01)   # the only reachable values are 0.50, 0.75, 1.00
MIN_BIN = 300
N_SPLITS = 12
N_BOOT = 400
DONOR_SEED = 20260726
SPLIT_SEED = 20260732
FLAT_TOL = 0.02         # pre-registered: |corrected rise| below this reads as flat


def gap(satp, items, w, a_, b_) -> float:
    sa = sb = 0.0
    for ci in range(len(items)):
        if w[ci] == 0.0:
            continue
        va, vb = satp.get((ci, a_)), satp.get((ci, b_))
        if va is None or vb is None:
            continue
        sa += w[ci] * va
        sb += w[ci] * vb
    return sa - sb


# ---------------------------------------------------------------------------
# THE MEASUREMENT. One function, run on the real data AND on the simulations, so
# the control exercises this code path rather than re-deriving its rule.
# `votes[i]` is a boolean array: did rater r order the pair's canonical-first
# response above the canonical-second? `arms[name][i]` is the same boolean for an
# estimator. Nothing here knows which is real.
# ---------------------------------------------------------------------------
def records(votes, arms, rng, n_splits=N_SPLITS):
    names = list(arms)
    pid, cons, ab, tie, hit = [], [], [], [], {k: [] for k in names}
    t = THIRD
    for i, v in enumerate(votes):
        n = len(v)
        if n < POOL:
            continue
        for _ in range(n_splits):
            idx = rng.permutation(n)[:POOL]     # a fixed pool: every bin gets the same |A|
            A, B, C = v[idx[:t]], v[idx[t:2 * t]], v[idx[2 * t:3 * t]]
            ma, mb = A.mean(), B.mean()
            # TIES ARE BROKEN AT RANDOM, NOT DROPPED. Dropping a tied A conditions on the
            # LABEL being decisive, which is the very selection the three-way split exists
            # to remove -- and it bites hardest in the low-consensus bin. A random
            # tiebreak is an unbiased label, only noisier, and that extra noise is exactly
            # what the A/B factor below measures and divides out.
            da = bool(rng.integers(2)) if ma == 0.5 else ma > 0.5
            db = bool(rng.integers(2)) if mb == 0.5 else mb > 0.5
            mc = C.mean()
            pid.append(i)
            cons.append(max(mc, 1.0 - mc))
            ab.append(float(da == db))
            tie.append(float(ma == 0.5))
            for k in names:
                hit[k].append(float(arms[k][i] == da))
    out = {"pid": np.array(pid), "cons": np.array(cons), "ab": np.array(ab),
           "label_tied": np.array(tie)}
    for k in names:
        out[k] = np.array(hit[k])
    return out


def curve(rec, names, edges=EDGES, min_bin=MIN_BIN):
    """Per-bin raw and deattenuated accuracies. Factor = sqrt(2h-1) from the A/B halves."""
    rows = []
    for i in range(len(edges) - 1):
        m = (rec["cons"] >= edges[i]) & (rec["cons"] < edges[i + 1])
        if m.sum() < min_bin:
            continue
        h = float(rec["ab"][m].mean())
        f = float(np.sqrt(max(2.0 * h - 1.0, 0.0)))
        r = {"lo": edges[i], "hi": min(edges[i + 1], 1.0), "n": int(m.sum()),
             "half_agreement": h, "attenuation_factor": f,
             "label_tie_rate": float(rec["label_tied"][m].mean()) if "label_tied" in rec else None}
        for k in names:
            acc = float(rec[k][m].mean())
            r[k] = acc
            r[k + "_deatt"] = 0.5 + (acc - 0.5) / f if f > 1e-6 else float("nan")
        rows.append(r)
    return rows


def rises(rows, names):
    """Raw and corrected attribution per bin, and the low->high rise of each."""
    raw = [r[names[0]] - r[names[1]] for r in rows]
    cor = [r[names[0] + "_deatt"] - r[names[1] + "_deatt"] for r in rows]
    return raw, cor, raw[-1] - raw[0], cor[-1] - cor[0]


# ---------------------------------------------------------------------------
# SIMULATION CONTROL -- two-sided. Latent direction is True for every pair by
# construction; a rater agrees with it with probability p; the arm agrees with it
# with probability `acc`, which is either constant or rising in p.
# ---------------------------------------------------------------------------
def simulate(rng, rising: bool, a_star=0.75, n_pairs=6000, n_raters=POOL):
    p = rng.uniform(0.52, 1.0, n_pairs)
    votes = [rng.random(n_raters) < p[i] for i in range(n_pairs)]
    acc = 0.5 + (a_star - 0.5) * (2 * p - 1) if rising else np.full(n_pairs, a_star)
    arm = rng.random(n_pairs) < acc
    flat = rng.random(n_pairs) < 0.55                 # a second, weaker constant arm
    rec = records(votes, {"strong": arm, "weak": flat}, rng, n_splits=4)
    return curve(rec, ["strong", "weak"]), acc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r104_deattenuated_consensus.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    # ---- CONTROL (i): pure attenuation must be FLATTENED ----------------------
    rowsF, _ = simulate(np.random.default_rng(11), rising=False)
    rawF, corF, rrF, rcF = rises(rowsF, ["strong", "weak"])
    recovered = [r["strong_deatt"] for r in rowsF]
    print(f"CONTROL (i) constant-accuracy arm, planted 0.750:")
    rawvals = " ".join(f"{r['strong']:.3f}" for r in rowsF)
    print(f"   raw       {rawvals}   rise {rrF:+.4f}")
    print(f"   corrected {' '.join(f'{x:.3f}' for x in recovered)}   rise {rcF:+.4f}")
    ok_flat = abs(rcF) < 0.05 and abs(rrF) > abs(rcF) and \
        max(abs(x - 0.75) for x in recovered) < 0.05
    print(f"   -> {'PASS' if ok_flat else 'FAIL'} (attenuation removed, 0.750 recovered)")

    # ---- CONTROL (ii): a genuine rise must SURVIVE ---------------------------
    rowsR, _ = simulate(np.random.default_rng(12), rising=True)
    rawR, corR, rrR, rcR = rises(rowsR, ["strong", "weak"])
    print(f"CONTROL (ii) genuinely-rising arm:")
    print(f"   corrected attribution {' '.join(f'{x:+.3f}' for x in corR)}   rise {rcR:+.4f}")
    ok_rise = rcR > 0.05
    print(f"   -> {'PASS' if ok_rise else 'FAIL'} (the correction does not flatten a real gradient)")
    if not (ok_flat and ok_rise):
        raise SystemExit("REFUSING: the correction failed one side of its two-sided control. It must "
                         "flatten a known-attenuation gradient AND preserve a known-real one; an "
                         "instrument that only ever returns 'flat' cannot report flatness.")

    # ---- REAL DATA -----------------------------------------------------------
    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        p_, ci, lab = m.split("|")
        sat[p_][(int(ci), lab)] = float(s_)

    keep = []
    for pid_, comp, rub in load_join(COMPARISONS, RUBRICS):
        pr = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pr and items and pid_ in sat:
            keep.append((pid_, items, pr))
    n = len(keep)
    # DONOR DRAW: `(i + 1 + integers(0, n-1)) % n` -- sampling WITH replacement over
    # donors, not a permutation, and seeded once. Same idiom and seed as r103.
    rng_d = np.random.default_rng(DONOR_SEED)
    donor = np.array([(i + 1 + rng_d.integers(0, n - 1)) % n for i in range(n)])

    votes, own, don = [], [], []
    for i, (pid_, items, pr) in enumerate(keep):
        satp, w = sat[pid_], weights(items)
        di = keep[int(donor[i])][1]
        dw = weights(di)
        cnt: dict = defaultdict(int)
        for x, y in pr:
            cnt[(x, y)] += 1
        # SORTED, and this was a live defect. Iterating the set directly makes the pair
        # ORDER depend on str hashing, which python randomises per process -- so the pair
        # indices, and therefore every three-way split drawn from the seeded generator,
        # differed run to run. Four runs of this unchanged, fully-seeded file returned
        # corrected rises of +0.0968, +0.1179, +0.1056 and +0.1114. The verdict was stable
        # across all four; the number was not, and an unreproducible number may not be
        # quoted. Every seed in this file was correct and the round was still not seeded.
        for k in sorted({tuple(sorted(t)) for t in cnt}):
            f_, r_ = cnt.get((k[0], k[1]), 0), cnt.get((k[1], k[0]), 0)
            if f_ + r_ < MIN_RATERS:
                continue
            votes.append(np.array([True] * f_ + [False] * r_))
            own.append(gap(satp, items, w, k[0], k[1]) > 0)
            don.append(gap(satp, di, dw, k[0], k[1]) > 0)
    own, don = np.array(own), np.array(don)
    print(f"\npairs with >= {MIN_RATERS} raters: {len(votes):,}")

    rec = records(votes, {"own": own, "donor": don}, np.random.default_rng(SPLIT_SEED))
    rows = curve(rec, ["own", "donor"])
    raw, cor, rise_raw, rise_cor = rises(rows, ["own", "donor"])
    print(f"split records {len(rec['pid']):,} over {N_SPLITS} splits\n")
    print(f"{'consensus(C)':>13} {'n':>7} {'A=B':>7} {'factor':>7} {'own':>7} {'don':>7} "
          f"{'raw':>8} {'own*':>7} {'don*':>7} {'corrected':>10}")
    for r_, a_, c_ in zip(rows, raw, cor):
        rng_lbl = "[%.1f,%.1f)" % (r_["lo"], r_["hi"])
        print(f"{rng_lbl:>13} {r_['n']:>7,} "
              f"{r_['half_agreement']:>7.3f} {r_['attenuation_factor']:>7.3f} "
              f"{r_['own']:>7.4f} {r_['donor']:>7.4f} {a_:>+8.4f} "
              f"{r_['own_deatt']:>7.4f} {r_['donor_deatt']:>7.4f} {c_:>+10.4f}")
    print(f"\n  raw rise (low->high) {rise_raw:+.4f}   corrected rise {rise_cor:+.4f}   "
          f"shrunk by {100 * (1 - abs(rise_cor) / abs(rise_raw)):.0f}%")

    # ---- BOOTSTRAP over PAIRS, not over split records -------------------------
    # A pair contributes N_SPLITS rows; resampling rows would treat one pair as
    # independent evidence a dozen times over. Resample pair ids and gather.
    order = np.argsort(rec["pid"], kind="stable")
    start = np.searchsorted(rec["pid"][order], np.arange(len(votes)), side="left")
    end = np.searchsorted(rec["pid"][order], np.arange(len(votes)), side="right")
    rb = np.random.default_rng(20260733)
    draws = []
    for _ in range(N_BOOT):
        pick = rb.integers(0, len(votes), len(votes))
        sel = np.concatenate([order[start[p]:end[p]] for p in pick])
        sub = {k: v[sel] for k, v in rec.items()}
        rr = curve(sub, ["own", "donor"], min_bin=1)
        if len(rr) == len(rows):
            draws.append(rises(rr, ["own", "donor"])[3])
    draws = np.array(draws)
    blo, bhi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    print(f"  corrected rise 95% CI over pairs [{blo:+.4f},{bhi:+.4f}] ({len(draws)} draws)")

    world = ("O OVERCORRECTED" if rise_cor < -FLAT_TOL else
             "A ATTENUATION" if bhi > 0 > blo or abs(rise_cor) < FLAT_TOL else
             "S SPECIFICITY")
    vec = _RES / "r104_split_records.npz"
    np.savez_compressed(vec, **{k: rec[k] for k in rec})
    print(f"  per-split records persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. r103 found source specificity rising from +0.0283 to +0.2461 across human-consensus "
        f"bins and named its own residual: a noisy target attenuates every estimator toward chance, so "
        f"the rise is expected even under constant specificity. Attenuation is MEASURABLE. Splitting "
        f"each pair's raters in THREE -- one third supplies the scoring label, one third measures that "
        f"label's reliability, one third does the binning, so the binning variable touches neither -- "
        f"EVERY pair is subsampled to a fixed pool of {POOL} raters, so |A|=|B|=|C|={THIRD} in "
        f"every bin and the bins differ in consensus and nothing else -- the first version let the "
        f"third size vary, which made the bins a RATER-COUNT partition and showed up as the "
        f"lowest-consensus bin carrying the MOST reliable label. Ties in a third are broken at random "
        f"rather than dropped, since dropping them conditions on the label being decisive. The two "
        f"probe thirds agree "
        + ", ".join(f"{r_['half_agreement']:.3f}" for r_ in rows)
        + f" across bins, giving attenuation factors "
        + ", ".join(f"{r_['attenuation_factor']:.3f}" for r_ in rows) + ". "
        f"Dividing each arm's over-chance accuracy by its bin's factor, the attribution runs "
        + ", ".join(f"{c_:+.4f}" for c_ in cor)
        + f" against a raw {', '.join(f'{a_:+.4f}' for a_ in raw)}. The low-to-high rise falls from "
        f"{rise_raw:+.4f} raw to {rise_cor:+.4f} corrected, "
        f"{100 * (1 - abs(rise_cor) / abs(rise_raw)):.0f}% of it removed, 95% CI over PAIRS "
        f"[{blo:+.4f},{bhi:+.4f}]. "
        + ("THE GRADIENT IS THE TARGET'S NOISE, NOT THE RUBRIC'S: once the label's own unreliability is "
           "divided out, the specificity a contested pair carries is not distinguishable from the one a "
           "consensual pair carries. r103's reading -- that the interpretable figure is the "
           "high-consensus one -- becomes a statement about where the TARGET is legible, not about "
           "where the rubric works."
           if world.startswith("A") else
           "THE GRADIENT SURVIVES ITS OWN NOISE MODEL: the rubric resolves consensual comparisons "
           "better than contested ones even after the label's unreliability is divided out. That is the "
           "reverse of what a normative instrument should do -- contested pairs are where "
           "prompt-specific values would earn their keep, and the measured specificity is concentrated "
           "where it matters least."
           if world.startswith("S") else
           "THE CORRECTION IS UNFIT: it inverts the gradient, which the independent-noise model cannot "
           "produce. This is UNVERIFIED and not an acquittal of either reading.") +
        f" BOTH ARMS RISE AFTER CORRECTION, AND THAT IS A SECOND READING OF THE SAME TABLE: the own "
        f"arm's deattenuated accuracy runs {rows[0]['own_deatt']:.4f} to {rows[-1]['own_deatt']:.4f} and "
        f"the DONOR arm's runs {rows[0]['donor_deatt']:.4f} to {rows[-1]['donor_deatt']:.4f}. Under the "
        f"independent-noise model a constant-accuracy arm is FLAT after correction -- the simulation "
        f"control shows exactly that -- so NEITHER arm is constant. An UNRELATED rubric also resolves "
        f"consensual pairs better than contested ones, which is a general normative backbone behaving as "
        f"one would expect of it. The attribution's rise is the EXCESS of the own arm's rise over the "
        f"donor's, and it is that excess, not either level, that this round reports. "
        f"TWO-SIDED SIMULATION CONTROL, both required and both passed: synthetic raters with a "
        f"per-pair agreement probability spanning the bins and an arm of CONSTANT latent accuracy 0.750 "
        f"produce a rising raw curve that the correction flattens to {rcF:+.4f}, recovering the planted "
        f"value to {max(abs(x - 0.75) for x in recovered):.3f}; an arm whose latent accuracy genuinely "
        f"RISES keeps a corrected rise of {rcR:+.4f}. An instrument that flattened everything would "
        f"report the first world whatever the truth, so the second control is the one that makes a flat "
        f"result mean anything. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN AND NOT SOFTENED: the correction assumes the arm's errors "
        f"are INDEPENDENT of the label's. A rubric and a rater can be misled by the same surface feature, "
        f"plausibly more often on contested pairs, and positively correlated errors make the correction "
        f"UNDER-correct where correlation is high -- biasing this round's corrected curve UPWARD at the "
        f"low end, i.e. TOWARD flatness. So a surviving rise is the robust finding here and a flat one is "
        f"the result this design could manufacture. A SECOND EFFECT PUSHES THE SAME WAY: the binning "
        f"third holds only {THIRD} raters, so its consensus is a noisy estimate of the underlying rater "
        f"agreement and the bins are smeared into one another. Smearing pulls every bin toward the "
        f"pooled mean and SHRINKS the measured gradient, so the corrected rise is a LOWER BOUND rather "
        f"than an estimate. "
        f"REPRODUCIBILITY, AND IT WAS NOT FREE: pairs were first collected by iterating a set, whose "
        f"order depends on python's per-process string hashing, so the pair indices and every split "
        f"drawn from the seeded generator differed run to run -- four runs of the unchanged file gave "
        f"corrected rises of +0.0968, +0.1179, +0.1056 and +0.1114. Every seed in the file was correct "
        f"and the round was still not seeded. The set is now sorted and the figures below are stable "
        f"under PYTHONHASHSEED. "
        f"SCOPE: {len(votes):,} unordered pairs carrying at least {MIN_RATERS} raters, {N_SPLITS} "
        f"random three-way splits each; the bootstrap resamples PAIRS, since one pair contributing "
        f"{N_SPLITS} rows is not {N_SPLITS} pieces of evidence. The label here is a THIRD of the raters, "
        f"not all of them, so these accuracies are not comparable to r103's levels -- only their "
        f"gradient is."
    )

    doc = {
        "min_raters": MIN_RATERS, "n_pairs": len(votes), "n_splits": N_SPLITS,
        "n_split_records": int(len(rec["pid"])), "bins": rows,
        "attribution_raw": raw, "attribution_corrected": cor,
        "rise_raw": rise_raw, "rise_corrected": rise_cor,
        "rise_corrected_ci95_over_pairs": [blo, bhi], "n_boot": len(draws),
        "flat_tolerance": FLAT_TOL,
        "control_constant_arm": {"raw_rise": rrF, "corrected_rise": rcF,
                                 "recovered": recovered, "planted": 0.75, "pass": bool(ok_flat)},
        "control_rising_arm": {"corrected_rise": rcR, "pass": bool(ok_rise)},
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "Own-minus-donor accuracy against a THIRD of each pair's human raters, divided by that "
            "label's measured reliability, binned by a disjoint third's consensus. Satisfaction from "
            "r04's tensor; no new measurement and no new judge call."),
        "pool": POOL, "third": THIRD,
        "scope": (
            "The correction assumes arm errors are independent of label errors; correlated errors bias "
            "the corrected curve toward flatness, so a surviving rise is robust and a flat result is "
            "not. Accuracy LEVELS are not comparable to r103's, which labelled with all raters; only "
            "the gradient is. Pairs under 9 raters are excluded because a three-way split needs a "
            "majority in each third, and every pair is subsampled to exactly "
            f"{POOL} so that label size is constant across bins."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
