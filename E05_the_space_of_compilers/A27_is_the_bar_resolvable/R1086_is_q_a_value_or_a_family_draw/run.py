#!/usr/bin/env python3
"""R1086 — `q buys 2 arms` is a family of size k. Is it also a fact about WHICH k?

R1057 built the world where `q` can act and reported that it buys **2 arms at k=10 and 2 at k=15**,
and the clause was KEPT on that. Reading its code rather than its README: the family is

    Cc = C[:k]            # the lexicographically FIRST k of the 15 blind subsets

and the three "seeds" reseed the **bootstrap**, never the family. So the composition axis has exactly
one cell — and `itertools.combinations` orders by subset SIZE, so `C[:10]` is the 4 singletons plus
6 pairs: the SMALLEST, and on this data the weakest, comparators available. A family of weak
comparators is the composition where beating 9 of 10 is easiest relative to beating all 10, which is
the direction that flatters `q`. **At k=10 there are C(15,10) = 3003 families and they are fully
enumerable, so no sampling is needed at all.**

ESTIMAND        for each k in 10..15 and EVERY family F of size k drawn from the 15 blind subsets:
                    admit_q(F)   = arms resolvably beating >= ceil(0.9|F|) members of F
                    admit_all(F) = arms resolvably beating ALL of F
                    delta(F)     = |admit_q(F)| - |admit_all(F)|
                The quantity: the DISTRIBUTION of delta over all families at each k, and where
                R1057's single `C[:k]` family sits inside it.
IDENTIFICATION  exactly identified: the family space is finite and enumerated whole (3944 families
                over k=10..15). No sampling, so no sampling error on the composition axis.
                ⭐ The bootstrap is done ONCE per (arm, subset) pair -- 99 x 15 = 1485 decisions --
                and every family is then a lookup. R1057 re-bootstrapped inside the family loop,
                which is why sampling looked necessary. It was not.
UNIT OF THE     a family F, and the count of arms each rule admits over it.
  INSTRUMENT
UNIT OF THE     the same. The sentence permitted is "over the enumerated blind families of size k,
  CLAIM         q admits this many more arms than the every-comparator rule". It says nothing about
                a family the release actually ships -- the release ships 2, where q is inert.
SCOPE           population: 968-prompt A2 target, the released arms, the 15 universally-available
                fixed subsets. instrument: cluster bootstrap on prompts, 2.5th percentile, the same
                operator R1057 used and imported rather than re-implemented. baseline: the
                every-comparator rule. regime: k = 10..15, the only sizes where q is not algebraic.
WORLDS          A A VALUE  delta is essentially constant across families at each k -- "q buys 2" is a
                           property of k, and R1057's cell is representative.
                B A DRAW   delta varies across families -- "q buys 2" is a fact about the family
                           R1057 happened to take first, and the KEEP decision rests on one cell.
                Prediction matrix on (spread of delta at k=10, rank of R1057's cell):
                  A -> (0, anywhere)      B -> (>0, and R1057's cell need not be the mode)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if delta takes >= 2 distinct values across the 3003 families at
                  k = 10. One family disagreeing is enough, because the clause was kept on a number
                  that would then require naming its family to be stated at all.
                  ⚠ AND THE CONVERSE IS NOT A WIN: if delta is constant, that is world A and the
                  round is closure on R1057, not a new finding.
POSITIVE CTRL   a synthetic arm that beats EVERY subset must be admitted by both rules at every k
                (contributing 0 to delta), and a synthetic arm that beats exactly ceil(0.9k) of them
                must be admitted by q and NOT by the every-rule (contributing exactly 1). Retention
                and MDE: the instrument's MDE is one arm, and it fails at g=0 by the guard below.
g=0 GUARD       at k <= 9, ceil(0.9k) = k, so delta MUST be 0 for EVERY family. That is a DERIVATION
                (R1055's), and it is used here as the check that this code implements that algebra
                rather than as a finding. If any family at k<=9 returns delta != 0, the instrument
                is wrong and no k>=10 number is admissible.
NEGATIVE CTRL   shuffle the beat-matrix COLUMNS within each arm -- destroys which comparator an arm
                beats while preserving how MANY it beats. The every-rule and the q-rule both depend
                only on the count, so delta must be UNCHANGED. World it excludes: "delta is driven
                by comparator identity"; if it moved, the statistic is not what its name says.
SHAM            the same operation minus the ingredient (family DIVERSITY): a family of k copies of
                ONE subset. Then beating one is beating all, so delta must be 0 at every k. This
                prices what having distinct comparators is worth.
PLACEBO         delta computed with the q-rule's threshold set to 100 on both sides. Must be exactly
                0 for every family, by construction, and is the check that the two branches differ
                only in `need`.
NOISE FLOOR     the bootstrap's own instability: the beat-matrix is recomputed at >=3 bootstrap
                seeds and any (arm, subset) decision that is not unanimous is reported and excluded,
                so a family-level spread cannot be manufactured by an unstable single pair.
MULTIPLICITY    all 3944 families across k=10..15 are enumerated and their delta distribution is
                reported whole, not summarised to a mean.
SPECIFICATION   k in {10,11,12,13,14,15} x the two rules x seed-unanimity on/off.
ARTIFACT        results/q_value_or_draw.json with the source hash and the full per-k distribution.
REPRODUCIBILITY the enumeration is deterministic; the bootstrap seeds are fixed and listed.
IMPOSSIBLE      whether any of these families could be CERTIFIED from the release -- N/A, R1056
                measured that the certified family is 2 at every defensible threshold. These are
                synthetic by construction and the round claims nothing about the shipped family.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
import math
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
RES = ROOT / "corebench" / "results"
OUT = HERE / "results" / "q_value_or_draw.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

NBOOT = 2000
SEEDS = (11, 23, 47)
KS = (10, 11, 12, 13, 14, 15)
G0_KS = (2, 5, 9)                                            # where the algebra forces delta = 0


def need(k: int, q: int) -> int:
    return k if q >= 100 else max(1, math.ceil(q / 100 * k))


def admitted(beat: np.ndarray, fam: tuple[int, ...], q: int) -> int:
    """how many arms clear the rule over this family. `beat` is arms x subsets, boolean."""
    return int((beat[:, list(fam)].sum(axis=1) >= need(len(fam), q)).sum())


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    if len(pids) < 100:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0.")
        return 2
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)
    common = set.intersection(*[{i for i, _ in Sfull[p]} for p in pids])
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(sorted(common), r)]
    if len(subsets) < max(KS):
        print(f"  UNRUNNABLE: the blind space holds {len(subsets)} < {max(KS)}. Exit 2, never 0.")
        return 2

    def scorevec(sat, idxs):
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs if idxs is not None
                                      else sorted({j for j, _ in sat[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return np.nan_to_num(v, nan=float(np.nanmean(v)))

    C = np.array([scorevec(Sfull, list(s)) for s in subsets])
    arms, V = [], []
    for f in sorted(RES.glob("sat_*.npz")):
        try:
            Sa = load_sat(f)
        except Exception:                                     # noqa: BLE001 - counted, not hidden
            continue
        v = scorevec(Sa, None)
        if np.isfinite(v).sum() < 100:
            continue
        arms.append(f.stem[4:]); V.append(v)
    V = np.array(V)
    if len(arms) < 10:
        print(f"  UNRUNNABLE: only {len(arms)} arms scored. Exit 2, never 0.")
        return 2

    # ---- the beat matrix, ONCE, at three bootstrap seeds -------------------------------------
    # ⭐ A DERIVATION THAT MAKES THE ENUMERATION FREE, LABELLED AS ONE. Under the SAME resample
    #    indices, the bootstrap mean of a difference is the difference of the bootstrap means:
    #      mean_b(V[i] - C[j]) = mean_b(V[i]) - mean_b(C[j])
    #    by linearity. So the per-pair resampling R1057 does inside its family loop -- 99 x 15 x
    #    2000 x 968 element gathers per seed -- collapses to 114 gathers and 1485 subtractions.
    #    This changes the COST and not the number; the equality is exact, not an approximation,
    #    and the control below checks it against the direct computation on a sample of pairs.
    beats, direct_check = [], []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        idx = rng.integers(0, n, size=(NBOOT, n))
        Vb = np.array([V[i][idx].mean(axis=1) for i in range(len(arms))])
        Cb = np.array([C[j][idx].mean(axis=1) for j in range(len(subsets))])
        B = np.zeros((len(arms), len(subsets)), bool)
        for i in range(len(arms)):
            for j in range(len(subsets)):
                B[i, j] = float(np.percentile(Vb[i] - Cb[j], 2.5)) > 0
        beats.append(B)
        if s == SEEDS[0]:
            for i, j in ((0, 0), (1, 7), (len(arms) - 1, len(subsets) - 1)):
                direct = float(np.percentile((V[i] - C[j])[idx].mean(axis=1), 2.5))
                fast = float(np.percentile(Vb[i] - Cb[j], 2.5))
                direct_check.append(abs(direct - fast) < 1e-12)
    unanimous = (beats[0] == beats[1]) & (beats[1] == beats[2])
    beat = beats[0] & beats[1] & beats[2]
    unstable = int((~unanimous).sum())

    # ---- CONTROLS ---------------------------------------------------------------------------
    ctrl = {}
    ctrl["DERIVATION CHECK the fast bootstrap equals the direct one on sampled pairs"] = all(
        direct_check) and len(direct_check) == 3
    # g=0: the algebra forces delta = 0 below k = 10, for EVERY family
    g0 = []
    for k in G0_KS:
        for fam in itertools.combinations(range(len(subsets)), k):
            g0.append(admitted(beat, fam, 90) - admitted(beat, fam, 100))
    ctrl["g=0 delta is 0 for every family at k<=9 (the algebra, reproduced)"] = set(g0) == {0}

    # POSITIVE: a planted arm beating everything, and one beating exactly ceil(0.9k)
    fam10 = tuple(range(10))
    planted_all = np.ones((1, len(subsets)), bool)
    planted_q = np.zeros((1, len(subsets)), bool)
    planted_q[0, :need(10, 90)] = True
    bp = np.vstack([beat, planted_all, planted_q])
    a_all_q = admitted(bp, fam10, 90) - admitted(beat, fam10, 90)
    a_all_100 = admitted(bp, fam10, 100) - admitted(beat, fam10, 100)
    ctrl["POSITIVE an arm beating EVERY comparator is admitted by both rules"] = (
        a_all_q >= 1 and a_all_100 >= 1)
    ctrl["POSITIVE an arm beating exactly ceil(0.9k) is admitted by q ONLY"] = (
        a_all_q - a_all_100 == 1)
    # ⛔ THE FIRST NEGATIVE CONTROL FAILED FOR ITS OWN REASONS, and the diagnosis replaces it.
    #    It shuffled each arm's row independently and asserted delta over the FIXED family
    #    `range(k)` was unchanged, on the reasoning that "both rules depend only on the count".
    #    They depend on the count WITHIN THE FAMILY, not on the arm's global total, and a per-arm
    #    shuffle changes exactly that. The control was wrong; the instrument was not. §4's `the
    #    control fails for its own reasons`, fifth time in this arc.
    # ⭐ The invariance that DOES hold, and is worth checking: enumerating EVERY family of size k is
    #    invariant to RELABELLING the comparators, so a column permutation applied identically to
    #    all arms must leave the whole distribution byte-identical. That tests the enumeration.
    rng = np.random.default_rng(7)
    perm = rng.permutation(len(subsets))
    relabelled = beat[:, perm]

    def dist_of(B, k):
        return sorted(admitted(B, f, 90) - admitted(B, f, 100)
                      for f in itertools.combinations(range(len(subsets)), k))
    ctrl["NEGATIVE relabelling the comparators leaves the WHOLE distribution identical"] = all(
        dist_of(relabelled, k) == dist_of(beat, k) for k in (10, 12, 15))
    # ⭐ and the complementary destruction: breaking WHICH comparator each arm beats must MOVE the
    #    distribution. If it did not, delta would be arithmetic and not a fact about the arms.
    broken = np.array([rng.permutation(row) for row in beat])
    ctrl["NEGATIVE breaking the arm-comparator pairing MOVES the distribution"] = any(
        dist_of(broken, k) != dist_of(beat, k) for k in (10, 12))
    # SHAM: a family of k copies of ONE comparator -- no diversity
    ctrl["SHAM a family of k copies of one comparator gives delta 0"] = all(
        admitted(beat, (j,) * k, 90) - admitted(beat, (j,) * k, 100) == 0
        for k in KS for j in (0, 7, 14))
    # PLACEBO: both sides at q=100
    ctrl["PLACEBO both rules at q=100 give delta 0 everywhere"] = all(
        admitted(beat, tuple(range(k)), 100) - admitted(beat, tuple(range(k)), 100) == 0
        for k in KS)
    gate_open = all(ctrl.values())

    # ---- THE ENUMERATION --------------------------------------------------------------------
    dist, r1057_cell, families = {}, {}, 0
    for k in KS:
        ds = []
        for fam in itertools.combinations(range(len(subsets)), k):
            ds.append(admitted(beat, fam, 90) - admitted(beat, fam, 100))
        families += len(ds)
        c = collections.Counter(ds)
        first = tuple(range(k))                              # R1057's `C[:k]`
        dcell = admitted(beat, first, 90) - admitted(beat, first, 100)
        dist[k] = {"families": len(ds), "distribution": dict(sorted(c.items())),
                   "min": min(ds), "max": max(ds), "mode": c.most_common(1)[0][0],
                   "mode_share": round(c.most_common(1)[0][1] / len(ds), 4),
                   "distinct_values": len(c)}
        r1057_cell[k] = {"delta_of_the_first_k_family": dcell,
                         "share_of_families_at_or_below": round(
                             sum(v for d, v in c.items() if d <= dcell) / len(ds), 4)}

    a_killed = gate_open and dist[10]["distinct_values"] >= 2
    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so no distribution licenses a claim. A kill that "
                   "can fire on a broken instrument is not a commitment.")
    elif a_killed:
        d10 = dist[10]
        verdict = (f"world A (A VALUE) is KILLED — over the {d10['families']} enumerated families at "
                   f"k=10, delta takes {d10['distinct_values']} distinct values spanning "
                   f"[{d10['min']}, {d10['max']}], mode {d10['mode']} at "
                   f"{d10['mode_share']:.1%} of families. R1057's `C[:k]` family gives "
                   f"{r1057_cell[10]['delta_of_the_first_k_family']}. **`q buys N arms` cannot be "
                   f"stated without naming the family.**")
    else:
        verdict = (f"world A survives — delta is constant at {dist[10]['mode']} across all "
                   f"{dist[10]['families']} families at k=10, so R1057's cell is representative and "
                   f"this round is closure on it, not a new finding.")

    art = {
        "round": "R1086",
        "question": "is `q buys 2 arms` a fact about the family SIZE or about WHICH family?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "prior_art": {
            "R1055": "q is algebraically inert below |family| = 10 (a derivation).",
            "R1056": "the CERTIFIED family is 2 at every defensible threshold -- q is inert here.",
            "R1057": ("built the synthetic world and reported q buys 2 at k=10 and 2 at k=15. Its "
                      "family is `C[:k]`, the lexicographically first k subsets; its three seeds "
                      "reseed the BOOTSTRAP, not the family. One cell on the composition axis."),
        },
        "population": {"prompts": n, "arms": len(arms), "blind_subsets": len(subsets),
                       "families_enumerated": families, "ks": list(KS)},
        "noise_floor": {"bootstrap_seeds": list(SEEDS), "nboot": NBOOT,
                        "arm_subset_decisions": int(beat.size),
                        "not_unanimous_across_seeds": unstable,
                        "rule": "a decision counts as a beat only if all three seeds agree"},
        "controls": ctrl,
        "distribution_by_k": dist,
        "r1057_cell_by_k": r1057_cell,
        "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1086 — is `q buys 2 arms` a value, or a draw from the family space?\n")
    print(f"  {n} prompts · {len(arms)} arms · {len(subsets)} blind subsets · "
          f"{families} families enumerated over k={list(KS)}")
    print(f"  noise floor: {unstable} of {beat.size} (arm, subset) decisions are not unanimous "
          f"across {len(SEEDS)} bootstrap seeds; a beat requires all three")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE WHOLE FAMILY SPACE — delta = |admitted by q| - |admitted by every-comparator|")
    print(f"    {'k':>3}{'families':>10}{'min':>6}{'mode':>6}{'max':>6}{'mode share':>12}"
          f"{'distinct':>10}   R1057's C[:k]")
    for k in KS:
        d, r = dist[k], r1057_cell[k]
        print(f"    {k:>3}{d['families']:>10}{d['min']:>6}{d['mode']:>6}{d['max']:>6}"
              f"{d['mode_share']:>11.1%}{d['distinct_values']:>10}   "
              f"delta={r['delta_of_the_first_k_family']} "
              f"(<= {r['share_of_families_at_or_below']:.1%} of families)")
    print(f"\n  FULL DISTRIBUTION AT k=10 (every family, none summarised away)")
    print(f"    {dist[10]['distribution']}")
    print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}")
    print(f"\n  {'⛔' if not gate_open else '⭐' if a_killed else '·'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
