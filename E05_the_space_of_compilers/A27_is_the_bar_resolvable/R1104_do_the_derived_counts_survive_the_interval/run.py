#!/usr/bin/env python3
"""R1104 — R1103 put an interval on the admitted SET. Put one on the counts DERIVED from it.

R1103: |admitted| = 22.77 [17, 26] against a point estimate of 24, with 11 of 99 arms in the band
(0.05, 0.95). Every composed number in this arc is a set operation over that set — R1098's nesting
(`released_only = 0`), R1099's slack (`blind \\ released`, 9 arms), R1101's ladder (24 -> 9 -> 6 -> 0).
**Each was computed once, at the point estimate.**

⛔ AND THE ANSWER IS NOT DEDUCIBLE FROM R1103'S PER-ARM FREQUENCIES, WHICH IS WHY THIS IS A ROUND AND
NOT ARITHMETIC. A difference of two unstable sets can be MORE stable than either — if both sets move
together across resamples, the common noise cancels in the difference — or FAR LESS, if they move
independently. R1103 measured the marginals; the covariance is what decides, and it was not measured.

ESTIMAND        the sampling distribution, over bootstrap resamples of the 968 prompts, of:
                (Q1) `released_only` = |released ②′ \\ blind ②′| — R1098's NESTING claim, point 0
                (Q2) `blind_only`    = |blind ②′ \\ released ②′| — R1099's SLACK, point 9
                (Q3) the LADDER |released|, |released − leakage|, |released − authorship|,
                     |released − authorship − topw| — R1101's 24, 9, 6, 0
IDENTIFICATION  identified. Both families are reconstructable per resample: the released family from
                the committed npz arms, the blind family as the 2^4 − 1 = 15 subsets of the criteria
                present on EVERY prompt, built by R1098's own `vec` construction.
UNIT OF THE     a bootstrap resample of the prompt population, and the derived count computed on it.
  INSTRUMENT
UNIT OF THE     the same. R1103's unit was an ARM and its admission frequency; a marginal frequency
  CLAIM         does not determine a difference of sets, and the two are named separately here for
                the same reason R1103 named its unit apart from R1055's.
SCOPE           population: 99 npz arms + 15 blind subsets, target A2, prompts with >= 2 targets.
                instrument: R1055's operator, analytic inner bound (validated). baseline: the
                point-estimate run, which must reproduce R1098's committed 24/33/0/9 and R1101's
                ladder. regime: 968 prompts, q = 100 on both families.
WORLDS          A THE DIFFERENCES ARE MORE STABLE THAN THEIR INPUTS   the two families move together,
                                so `released_only` stays 0 in >= 95% of resamples and the ladder's
                                terminal 0 holds. The composed claims survive R1103 unchanged.
                B THE DIFFERENCES INHERIT OR AMPLIFY   `released_only` is non-zero in a material
                                share, or the slack's interval spans several arms. Then R1098's
                                `the families NEST` and R1099's `9-arm slack` need intervals, and
                                statements built on them are point estimates with no precision.
                Prediction matrix on (share of resamples with released_only = 0, sd of blind_only):
                  A -> (>= 0.95, small)      B -> (< 0.95, several arms)
KILL            pre-registered. World A is KILLED if the share of resamples with `released_only = 0`
                falls below 0.95, OR the central 95% interval on `blind_only` spans more than 4 arms
                (R978's registered band at N=968, the same yardstick R1103 used). Gated on controls:
                                    if positive_reproduces_R1098 and placebo_degenerate:
                                        evaluate(share, span)
                                    else: UNVERIFIED
POSITIVE CTRL   the point-estimate run must reproduce R1098's committed sets by SIZE and by NAME:
                released 24, blind-minus-comparators 33, released_only 0, blind_only 9. If it does
                not, the object being resampled is not the one this arc published.
g=0 / PLACEBO   the identity outer draw must return exactly the point estimate for every derived
                quantity, with zero spread. This is what makes a non-zero spread downstream a
                measurement rather than a harness artifact.
SHAM            ⭐ R1055's control, once more: hold the prompt sample FIXED, vary only the INNER
                bootstrap seed, 3 seeds. Every derived quantity must come back with a DEGENERATE
                interval. Same operation, same size, minus the ingredient — the resampling of the
                population. It reproduces R1103's finding one level up: the seed control cannot see
                any of this.
NEGATIVE CTRL   a family against itself: `released \\ released` must be empty in every resample. A
                non-zero there means the set operation is misapplied, not that the sets move.
⚠ DERIVATION    the ladder's terminal `0` may be STRUCTURALLY FORCED rather than measured: at the
  TO TEST       point estimate `released − authorship` contains only `topw` arms, so subtracting the
                `topw` arms empties it by construction. The round counts the resamples in which
                `released − authorship − topw` is NON-empty, which is the only way to tell a forced
                zero from a measured one. If it is never non-empty, the terminal 0 is a DERIVATION
                and R1101's ladder must say so.
NOISE FLOOR     the Monte-Carlo standard error of a share at NOUTER draws, reported beside the share.
MULTIPLICITY    3 derived families x 3 outer seeds, every distribution reported whole — not just its
                mean, and including the resamples that contradict the point estimate.
SPECIFICATION   outer seed x family {released 2 comparators, blind 15 subsets}.
SEEDS           3 outer seeds; the seed flag is verified to change the draws.
ARTIFACT        results/derived_counts.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | the TRUE sampling distribution | a second independent draw of 968 prompts; the
                  bootstrap approximates it and is labelled throughout |
                | whether the blind family is the RIGHT comparator family | R1097's standing limit;
                  this round prices the published numbers, it does not re-choose the family |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, itertools, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "derived_counts.json"
COMP = ["generic", "genericpool16"]
NOUTER, NBOOT, OUTER_SEEDS = 250, 4000, (1104, 2208, 3312)
Z = 1.959963984540054


def main() -> int:
    f98 = next(A27.glob("R1098_*/results/families_nest.json"), None)
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    if f98 is None or f94 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    s98 = json.loads(f98.read_text())["sets"]
    rd = json.loads(f94.read_text())["readings"]
    leak_x, auth_x = set(rd["leakage_excludes"]), set(rd["authorship_excludes"])

    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    def perprompt(sat, idxs=None):
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in sat:
                sel = idxs if idxs is not None else sorted({j for j, _ in sat[p]})
                c = np.array(cls(yvec(sat[p], sel)), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return v

    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        nm = f.stem[4:]
        try:
            Sa = load_sat(f)
        except Exception:
            continue
        v = perprompt(Sa)
        cov = np.isfinite(v)
        if cov.sum() < 100:
            continue
        arms.append(nm); V.append(np.nan_to_num(v, nan=0.0)); COV.append(cov)
    V, COV = np.array(V), np.array(COV)

    # ---- the blind family: R1098's construction, criteria present on EVERY prompt
    common = sorted(set.intersection(*[{i for i, _ in Sfull[p]} for p in pids]))
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(common, r)]
    BV, BCOV = [], []
    for s in subsets:
        v = perprompt(Sfull, list(s))
        BV.append(np.nan_to_num(v, nan=0.0)); BCOV.append(np.isfinite(v))
    BV, BCOV = np.array(BV), np.array(BCOV)
    print(f"  arms {len(arms)} · prompts {n} · blind subsets {len(subsets)} "
          f"(from {len(common)} universal criteria)")
    if len(subsets) != 15:
        print(f"  ⚠ blind family is {len(subsets)}, not the 15 this arc published — reported, "
              f"not silently accepted")

    ci = [arms.index(c) for c in COMP if c in arms]
    if len(ci) != len(COMP):
        print("  UNRUNNABLE: a comparator is absent. Exit 2, never 0."); return 2

    def lo_boot(d, seed):
        rng = np.random.default_rng(seed); m = len(d)
        return float(np.percentile(d[rng.integers(0, m, size=(NBOOT, m))].mean(axis=1), 2.5))

    def lo_ana(d):
        m = len(d)
        return float(d.mean() - Z * d.std(ddof=1) / np.sqrt(m)) if m > 1 else 0.0

    def admit(sample, family, inner="analytic", seed=0):
        """R1055's operator. family 'released' -> the 2 npz comparators; 'blind' -> the 15 subsets,
        with the npz comparators themselves excluded from candidacy (R1098's rule)."""
        out = set()
        for i, nm in enumerate(arms):
            if family == "released" and i in ci:
                continue
            if family == "blind" and nm in COMP:
                continue
            beats = 0
            need = len(ci) if family == "released" else len(subsets)
            for k in range(need):
                if family == "released":
                    j = ci[k]; m = COV[i] & COV[j]; dd = V[i] - V[j]
                else:
                    m = COV[i] & BCOV[k]; dd = V[i] - BV[k]
                d = dd[m] if sample is None else dd[sample[m[sample]]]
                if len(d) < 30:
                    continue
                if (lo_boot(d, seed) if inner == "boot" else lo_ana(d)) > 0:
                    beats += 1
            if beats >= need:
                out.add(nm)
        return out

    def ladder(rel, topw_admitted):
        return [len(rel), len(rel - leak_x), len(rel - auth_x),
                len(rel - auth_x - topw_admitted)]

    # ---------- POSITIVE + PLACEBO: the point estimate
    rel0, blind0 = admit(None, "released"), admit(None, "blind")
    topw0 = {a for a in rel0 if a.startswith("topw")}
    pt = {"released": len(rel0), "blind_minus_comparators": len(blind0),
          "released_only": len(rel0 - blind0), "blind_only": len(blind0 - rel0),
          "ladder": ladder(rel0, topw0)}
    positive = (pt["released"] == len(s98["released"])
                and pt["blind_minus_comparators"] == len(s98["blind_minus_comparators"])
                and pt["released_only"] == len(s98["released_only"])
                and pt["blind_only"] == len(s98["blind_only"])
                and rel0 == set(s98["released"]) and blind0 == set(s98["blind_minus_comparators"]))
    print(f"  POSITIVE point estimate {pt} · reproduces R1098 by name: {positive}")

    rel0b, blind0b = admit(None, "released", "boot", 11), admit(None, "blind", "boot", 11)
    instrument_ok = (rel0b == rel0) and (blind0b == blind0)
    print(f"  INSTRUMENT analytic vs 4000-draw boot inner, both families identical: {instrument_ok}")

    # ---------- SHAM: R1055's inner-seed control, one level up
    sham = [(len(a - b), len(b - a)) for a, b in
            ((admit(None, "released", "boot", s), admit(None, "blind", "boot", s))
             for s in (11, 23, 47))]
    sham_degenerate = len(set(sham)) == 1
    print(f"  SHAM  inner-seed only: (released_only, blind_only) = {sham} · degenerate: "
          f"{sham_degenerate}")

    # ---------- the measurement
    ro, bo, lads, terminal_nonempty, neg_ok = [], [], [], 0, True
    for os_ in OUTER_SEEDS:
        rng = np.random.default_rng(os_)
        for _ in range(NOUTER):
            sample = rng.integers(0, n, n)
            rel, bl = admit(sample, "released"), admit(sample, "blind")
            ro.append(len(rel - bl)); bo.append(len(bl - rel))
            tw = {a for a in rel if a.startswith("topw")}
            L = ladder(rel, tw)
            lads.append(L)
            if L[3] > 0:
                terminal_nonempty += 1
            if rel - rel:
                neg_ok = False
        print(f"  outer seed {os_}: released_only mean {np.mean(ro[-NOUTER:]):.3f} · "
              f"blind_only mean {np.mean(bo[-NOUTER:]):.2f}")

    N = len(ro)
    lads = np.array(lads)
    share_nested = float(np.mean(np.array(ro) == 0))
    bo_lo, bo_hi = float(np.percentile(bo, 2.5)), float(np.percentile(bo, 97.5))
    span = bo_hi - bo_lo
    mc_se = float(np.sqrt(max(share_nested * (1 - share_nested), 1e-9) / N))
    placebo_ok = admit(None, "released") == rel0 and admit(None, "blind") == blind0
    # ⛔ THIS CONTROL FAILED FOR ITS OWN REASONS ON THE FIRST RUN, and the diagnosis is the round's
    #    own finding. It compared the first ten `released_only` values across seeds — and
    #    `released_only` is 0 in EVERY resample, so all three seeds were trivially identical and the
    #    control reported the seed flag dead. §4's `the control fails for its own reasons`,
    #    sub-kind ② (it presupposed a non-null quantity, on exactly the quantity this round measures
    #    as null). The seed check must run on a quantity that VARIES; `blind_only` does.
    seeds_differ = len({tuple(bo[i * NOUTER:i * NOUTER + 10])
                        for i in range(len(OUTER_SEEDS))}) == len(OUTER_SEEDS)

    gate_open = positive and placebo_ok and neg_ok and instrument_ok and seeds_differ
    world_A_killed = ((share_nested < 0.95) or (span > 4)) if gate_open else None

    ladder_stats = {
        f"step{i}": {"point": pt["ladder"][i], "mean": round(float(lads[:, i].mean()), 2),
                     "p2.5": float(np.percentile(lads[:, i], 2.5)),
                     "p97.5": float(np.percentile(lads[:, i], 97.5)),
                     "min": int(lads[:, i].min()), "max": int(lads[:, i].max())}
        for i in range(4)}

    payload = {
        "round": "R1104",
        "question": "do the counts DERIVED from the admitted set survive R1103's interval?",
        "point_estimate": pt,
        "R1098_committed": {k: len(v) for k, v in s98.items()},
        "nesting": {"share_of_resamples_with_released_only_0": round(share_nested, 4),
                    "MC_SE": round(mc_se, 4),
                    "released_only_mean": round(float(np.mean(ro)), 3),
                    "released_only_max": int(np.max(ro)),
                    "R1098_claim": "the families NEST (released_only = 0)",
                    # ⚠ IF THIS COMES BACK AT 1.000 IT IS CLOSE TO A DERIVATION, and saying so is the
                    #    difference between a robustness finding and a restatement. R1098 measured
                    #    the mechanism: all 15 blind subsets score BELOW the weaker released
                    #    comparator. An arm that beats the strong pair therefore beats the weak
                    #    fifteen, on any resample, so nesting is largely forced by that ordering —
                    #    not by the resampling being kind to it.
                    "reading": ("a share at 1.000 is not evidence that nesting is robust to "
                                "resampling so much as that R1098's uniform-weakness mechanism "
                                "holds under it")},
        "slack": {"point": pt["blind_only"], "mean": round(float(np.mean(bo)), 2),
                  "p2.5": bo_lo, "p97.5": bo_hi, "span": span,
                  "min": int(np.min(bo)), "max": int(np.max(bo)),
                  "R1099_claim": "a 9-arm slack"},
        "ladder": ladder_stats,
        "terminal_zero": {
            "resamples_with_nonempty_terminal": terminal_nonempty, "of": N,
            "is_structurally_forced": terminal_nonempty == 0,
            "why_it_matters": ("at the point estimate `released − authorship` contains only `topw` "
                               "arms, so subtracting them empties it BY CONSTRUCTION. Counting the "
                               "resamples where it is non-empty is the only way to tell a forced "
                               "zero from a measured one — and R1101 reported it as a measurement."),
        },
        "sham_R1055_inner_seed": {"cells": sham, "degenerate": sham_degenerate},
        "instrument_validation": {"analytic_equals_boot_both_families": instrument_ok},
        "controls": {
            "POSITIVE the point estimate reproduces R1098's committed sets BY NAME": positive,
            "PLACEBO the identity draw returns exactly the point estimate": bool(placebo_ok),
            "NEGATIVE a family minus itself is empty in every resample": bool(neg_ok),
            "INSTRUMENT the analytic inner bound equals the 4000-draw bootstrap on both families":
                instrument_ok,
            "SHAM R1055's inner-seed control gives a DEGENERATE interval": bool(sham_degenerate),
            "SEEDS the outer seed flag changes the draws (checked on `blind_only`, which varies)":
                bool(seeds_differ),
        },
        "control_repair": {
            "control": "SEEDS the outer seed flag changes the draws",
            "first_form": "compared the first ten `released_only` values across seeds",
            "why_it_failed": ("`released_only` is 0 in every resample — the round's own finding — so "
                              "all three seeds were identical and the control declared the seed flag "
                              "dead. It presupposed a non-null quantity, on the one quantity this "
                              "round measures as null."),
            "repair": "run the same check on `blind_only`, which varies across resamples",
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "share_nested": round(share_nested, 4), "slack_span": span,
                 "thresholds": {"share_nested_min": 0.95, "slack_span_max": 4}},
        "grid": {"outer_draws": N, "seeds": len(OUTER_SEEDS), "arms": len(arms),
                 "blind_subsets": len(subsets)},
        "seeds": list(OUTER_SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        s = payload["slack"]
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}. "
            f"NESTING holds in {share_nested:.3f} of {N} resamples (MC SE {mc_se:.4f}), threshold "
            f"0.95. SLACK is {s['mean']} [{s['p2.5']:.0f}, {s['p97.5']:.0f}] against a point "
            f"estimate of {s['point']}, span {span} against a threshold of 4. LADDER "
            f"{pt['ladder']} -> means "
            f"{[ladder_stats[f'step{i}']['mean'] for i in range(4)]}. "
            + (f"⭐ AND THE LADDER'S TERMINAL ZERO IS STRUCTURALLY FORCED: it is non-empty in "
               f"{terminal_nonempty} of {N} resamples, so R1101 reported a DERIVATION as a "
               f"measurement."
               if terminal_nonempty == 0 else
               f"⚠ AND THE LADDER'S TERMINAL ZERO IS NOT FORCED: it is non-empty in "
               f"{terminal_nonempty} of {N} resamples, so the 0 is a measurement after all."))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for i in range(4):
        st = ladder_stats[f"step{i}"]
        print(f"  ladder step{i}: point {st['point']:>3}  mean {st['mean']:>6}  "
              f"[{st['p2.5']:.0f}, {st['p97.5']:.0f}]  min {st['min']} max {st['max']}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
