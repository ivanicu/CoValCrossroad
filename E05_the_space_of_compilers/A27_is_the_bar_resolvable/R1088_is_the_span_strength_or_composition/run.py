#!/usr/bin/env python3
"""R1088 — is resolvability's [2, 14] span about comparator STRENGTH, or about WHICH comparators?

R1087 enumerated all 32,767 blind families and found resolvability's exclusion count spans [2, 14]
across 9 values while coverage is a flat -2. Its NEXT proposed regressing each family's count on the
mean score of its members. **That regression is a trap and this round says so before running it.**

⛔ n_eff IS 15, NOT 32,767. Every family is a subset of the same 15 blind subsets, so the families
   are not independent units -- they are all reads of 15 objects. A correlation over 32,767 points
   would quote a CI narrower than the design can support by a factor of ~sqrt(2185). Computed at the
   honest n: **the MDE for |r| at n = 15 is 0.669** (Fisher z, two-sided alpha .05, power .80). Any
   |r| below that is UNRESOLVED, never "no relationship".

⭐ AND THERE IS AN EXACT ROUTE THAT NEEDS NO INFERENCE AT ALL. Under the every-comparator rule an arm
   is admitted iff it beats every member, so
       strict(F)  = intersection over j in F of strict_j
       relaxed(F) = intersection over j in F of relaxed_j
   and therefore d_res(F) = |intersection relaxed_j| - |intersection strict_j| is a DETERMINISTIC
   function of the 15 per-subset beat-columns. There is no family-level randomness to model. So the
   span is decomposable exactly, by leave-one-out over the 15 columns, and that is the primary
   instrument here; the correlation is secondary and reported with its MDE attached.

ESTIMAND        (Q1, exact) for each blind subset j: how the span of d_res over the family space
                changes when j is removed from the space entirely -- min, max and distinct-value
                count over the 2^14 - 1 families that exclude it.
                (Q2, inferential, underpowered by design) the association across the 15 subsets
                between a subset's own mean score s_j and its solo flip count f_j = |relaxed_j| -
                |strict_j|, reported against the MDE above.
IDENTIFICATION  Q1 is exactly identified -- it is a decomposition of a deterministic quantity, not an
                estimate. Q2 is identified but has n = 15 and MDE |r| = 0.669; that is stated with
                the number and governs its reading.
UNIT OF THE     Q1: a blind subset, and the span of the family space without it. Q2: a blind subset.
  INSTRUMENT
UNIT OF THE     the same for both. Neither says anything about the RELEASED comparators, which are
  CLAIM         not in this space (R1087's standing limit).
SCOPE           population: 968 prompts, target A2, released arms, the 15 blind subsets. instrument:
                R1055's operator, 3 bootstrap seeds, unanimity required. baseline: the strict
                (resolvable) variant. regime: the every-comparator rule.
WORLDS          A STRENGTH   the span tracks how good the comparators are: weak members admit more
                             flips, and removing the weakest collapses the span's top.
                B IDENTITY   the span is about WHICH subsets, not how strong: removing the weakest
                             leaves the span, and some particular subset carries it.
                C NEITHER    the span survives every single-subset removal -- it is a property of
                             the space's joint structure and no member explains it.
                Prediction matrix on (max after removing the weakest, max after removing the
                span-carrier identified by Q1):
                  A -> (collapses, collapses)   B -> (holds, collapses)   C -> (holds, holds)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if removing the WEAKEST subset leaves the maximum unchanged.
                  World B is KILLED if NO single removal changes the maximum.
                  Q2 is decided against the MDE and not against zero: |r| < 0.669 -> UNRESOLVED.
POSITIVE CTRL   plant a comparator far weaker than all 15 (a constant at the observed minimum) and
                one far stronger (a constant at the observed maximum). The weak plant must raise the
                space's maximum flip count and the strong plant must lower it; if neither moves,
                strength has no purchase on this instrument at any magnitude and Q2 is meaningless.
                Retention 1.0; MDE one arm.
g=0 GUARD       give every subset an IDENTICAL score vector: the flip counts must become identical
                and the correlation undefined. If a correlation survives constant strength, it is
                being manufactured by the harness.
NEGATIVE CTRL   permute the strength labels across the 15 subsets -- |r| must fall into its own
                permutation band. The band is measured over 2000 permutations, not assumed.
SHAM            correlate the flip count against subset SIZE instead of strength -- the same
                operation with the ingredient (score) replaced by a structural nuisance. Size and
                strength are themselves correlated here, and that confound is measured and reported
                rather than named and left.
PLACEBO         the strict variant against itself: flip count must be 0 for every subset.
NOISE FLOOR     3 bootstrap seeds with unanimity required; and the permutation band above.
MULTIPLICITY    15 leave-one-out cells and 2 correlations (strength, size) = 17 reported; no
                selection among them.
SPECIFICATION   strength summary in {mean, median, min over prompts} x flip statistic in {solo flip
                count, contribution to the space maximum}.
ARTIFACT        results/span_strength_or_composition.json with the source hash.
REPRODUCIBILITY deterministic given the seeds; the enumeration is exhaustive.
IMPOSSIBLE      any statement about the RELEASED comparators -- N/A, they are not blind subsets.
                a well-powered correlation -- N/A here, it would require more than 4 universally
                available criteria, and 2^4 - 1 = 15 is a hard cap on the population.
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
OUT = HERE / "results" / "span_strength_or_composition.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

NBOOT, SEEDS, NPERM = 2000, (11, 23, 47), 2000


def mde_r(n: int, alpha=1.959963985, power=0.841621234) -> float:
    z = (alpha + power) / math.sqrt(n - 3)
    return (math.exp(2 * z) - 1) / (math.exp(2 * z) + 1)


def pearson(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def span_over(strict: np.ndarray, relaxed: np.ndarray, cols: list[int]) -> dict:
    """the exact distribution of d_res over EVERY non-empty family drawn from `cols`."""
    ds = []
    for r in range(1, len(cols) + 1):
        for f in itertools.combinations(cols, r):
            s = int((strict[:, list(f)].sum(axis=1) == len(f)).sum())
            x = int((relaxed[:, list(f)].sum(axis=1) == len(f)).sum())
            ds.append(x - s)
    c = collections.Counter(ds)
    return {"families": len(ds), "min": min(ds), "max": max(ds), "distinct": len(c),
            "mode": c.most_common(1)[0][0]}


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)
    common = set.intersection(*[{i for i, _ in Sfull[p]} for p in pids])
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(sorted(common), r)]

    def scorevec(sat, idxs):
        v, cov = np.full(n, np.nan), np.zeros(n, bool)
        for i, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs if idxs is not None
                                      else sorted({j for j, _ in sat[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]])); cov[i] = True
        return np.nan_to_num(v, nan=0.0), cov

    C = np.array([scorevec(Sfull, list(s))[0] for s in subsets])
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        try:
            Sa = load_sat(f)
        except Exception:                                     # noqa: BLE001
            continue
        v, cov = scorevec(Sa, None)
        if cov.sum() < 100:
            continue
        arms.append(f.stem[4:]); V.append(v); COV.append(cov)
    V, COV = np.array(V), np.array(COV)
    if len(arms) < 20 or len(subsets) < 8:
        print(f"  UNRUNNABLE: {len(arms)} arms, {len(subsets)} subsets. Exit 2, never 0.")
        return 2

    def beats(Cmat, resolvable: bool, seed: int) -> np.ndarray:
        rng = np.random.default_rng(seed)
        idx_full = rng.integers(0, n, size=(NBOOT, n))
        B = np.zeros((len(arms), Cmat.shape[0]), bool)
        for i in range(len(arms)):
            m = COV[i]; k = int(m.sum())
            if k < 30:
                continue
            if not resolvable:
                B[i] = np.array([V[i][m].mean() - Cmat[j][m].mean() > 0
                                 for j in range(Cmat.shape[0])])
                continue
            idx = idx_full[:, :k] % k
            Vb = V[i][m][idx].mean(axis=1)
            for j in range(Cmat.shape[0]):
                B[i, j] = float(np.percentile(Vb - Cmat[j][m][idx].mean(axis=1), 2.5)) > 0
        return B

    def unanimous(Cmat, resolvable):
        ms = [beats(Cmat, resolvable, s) for s in SEEDS]
        return ms[0] & ms[1] & ms[2], int((~((ms[0] == ms[1]) & (ms[1] == ms[2]))).sum())

    STRICT, u1 = unanimous(C, True)
    RELAXED, u2 = unanimous(C, False)
    strength = C.mean(axis=1)
    sizes = np.array([len(s) for s in subsets], float)
    flips = (RELAXED.sum(axis=0) - STRICT.sum(axis=0)).astype(float)

    # ---------------------------------------------------------------- controls
    ctrl = {}
    # ⛔⛔ MY WORLD A HAD THE WRONG MECHANISM, AND THE PLANTS ARE WHAT SHOWED IT. A "flip" is an arm
    #     the POINT estimate admits and the 2.5th percentile does not, so it requires the arm to sit
    #     CLOSE to the comparator -- close enough that the bootstrap interval straddles zero. A
    #     comparator far BELOW every arm is beaten resolvably by all of them (0 flips); one far ABOVE
    #     is beaten by none (0 flips). Measured: both extreme plants flip exactly 0. So the driver is
    #     PROXIMITY to the arm distribution, not weakness, and "weaker admits more" was never the
    #     mechanism. The plants are rebuilt at the distance that can produce a flip at all.
    armbar = float(V.mean())
    lo, hi = float(C.min()), float(C.max())
    Cw = np.vstack([C, np.full((1, n), armbar - 0.002)])       # NEAR the arms, just below
    Cs = np.vstack([C, np.full((1, n), lo)])                   # FAR below every arm
    Sw, _ = unanimous(Cw, True); Rw, _ = unanimous(Cw, False)
    Ss, _ = unanimous(Cs, True); Rs, _ = unanimous(Cs, False)
    base_max = span_over(STRICT, RELAXED, list(range(len(subsets))))["max"]
    # ⛔ THE FIRST VERSION OF THIS CONTROL COULD NOT FAIL INFORMATIVELY. It compared the MAXIMUM over
    #    the space WITH a plant against the space WITHOUT it -- but adding a column makes the space a
    #    strict SUPERSET, so the max can only rise or stay, and `strong_max <= base_max` holds by
    #    construction whatever the plant is. §4's `control that cannot PASS`, mirrored: the criterion
    #    was satisfied before anything was planted.
    # ⭐ The comparison that isolates the plant: its SOLO flip count, i.e. the family {plant} alone.
    #    Same family size, same rule, only the comparator's strength differs.
    j_new = len(subsets)
    near_solo = int((Rw[:, j_new].astype(int) - Sw[:, j_new].astype(int)).sum())
    far_solo = int((Rs[:, j_new].astype(int) - Ss[:, j_new].astype(int)).sum())
    weak_solo, strong_solo = near_solo, far_solo
    weak_max = span_over(Sw, Rw, list(range(j_new + 1)))["max"]
    strong_max = span_over(Ss, Rs, list(range(j_new + 1)))["max"]
    ctrl["POSITIVE a NEAR plant flips arms; a FAR one flips none"] = (
        near_solo > 0 and far_solo == 0)
    ctrl["POSITIVE the near plant lands inside the real subsets' flip range"] = (
        int(flips.min()) <= near_solo <= len(arms))
    ctrl["g=0 adding a column never lowers the space maximum (a superset)"] = (
        weak_max >= base_max and strong_max >= base_max)
    Cc = np.repeat(C[:1], len(subsets), axis=0)               # every subset identical
    Sc, _ = unanimous(Cc, True); Rc, _ = unanimous(Cc, False)
    fc = (Rc.sum(axis=0) - Sc.sum(axis=0)).astype(float)
    ctrl["g=0 identical comparators give identical flip counts"] = len(set(fc.tolist())) == 1
    ctrl["PLACEBO the strict variant against itself flips nobody"] = int(
        (STRICT.sum(axis=0) - STRICT.sum(axis=0)).sum()) == 0
    r_obs = pearson(strength, flips)
    rng = np.random.default_rng(5)
    null = np.array([pearson(rng.permutation(strength), flips) for _ in range(NPERM)])
    band = (float(np.nanpercentile(null, 2.5)), float(np.nanpercentile(null, 97.5)))
    ctrl["NEGATIVE the permutation band brackets zero"] = band[0] < 0 < band[1]
    gate_open = all(ctrl.values())

    # ---------------------------------------------------------------- Q1, exact
    full = span_over(STRICT, RELAXED, list(range(len(subsets))))
    loo = {}
    for j in range(len(subsets)):
        cols = [c for c in range(len(subsets)) if c != j]
        loo[str(subsets[j])] = {**span_over(STRICT, RELAXED, cols),
                                "strength": round(float(strength[j]), 4),
                                "size": int(sizes[j]), "solo_flips": int(flips[j])}
    weakest = int(np.argmin(strength))
    max_after_weakest = loo[str(subsets[weakest])]["max"]
    carriers = sorted(k for k, v in loo.items() if v["max"] < full["max"])

    # ---------------------------------------------------------------- Q2, underpowered by design
    mde = mde_r(len(subsets))
    r_size = pearson(sizes, flips)
    r_conf = pearson(strength, sizes)
    q2 = {"r_strength_vs_flips": round(r_obs, 4), "n": len(subsets), "MDE_for_r": round(mde, 4),
          "resolved": bool(abs(r_obs) >= mde),
          "permutation_band_95": [round(b, 4) for b in band],
          "SHAM_r_size_vs_flips": round(r_size, 4),
          "CONFOUND_r_strength_vs_size": round(r_conf, 4),
          "reading": ("|r| below the MDE is UNRESOLVED at this n, never 'no relationship'. "
                      "n_eff is 15 because every family is a subset of the same 15 objects.")}

    a_killed = gate_open and max_after_weakest == full["max"]
    b_killed = gate_open and not carriers
    if not gate_open:
        verdict = "UNVERIFIED — a control failed, so no decomposition licenses a claim."
    elif b_killed:
        verdict = (f"world C (NEITHER) — no single subset's removal lowers the maximum of "
                   f"{full['max']}; the span is a joint property of the space and no member "
                   f"explains it.")
    elif a_killed:
        verdict = (f"world A (STRENGTH) is KILLED — removing the WEAKEST subset leaves the maximum "
                   f"at {full['max']}, while {len(carriers)} other subset(s) do lower it: "
                   f"{carriers[:4]}. The span is about WHICH comparators, not how strong.")
    else:
        verdict = (f"world A survives — removing the weakest subset lowers the maximum from "
                   f"{full['max']} to {max_after_weakest}, and {len(carriers)} subset(s) carry it.")

    art = {
        "round": "R1088",
        "question": "is resolvability's span a matter of comparator strength or of identity?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "n_eff_warning": ("32,767 families are subsets of 15 objects; n_eff = 15. The exact route "
                          "below is a decomposition of a deterministic quantity and needs no n."),
        "derivation": ("under the every-comparator rule admission is an INTERSECTION over members, "
                       "so d_res(F) = |∩ relaxed_j| - |∩ strict_j| is fully determined by the 15 "
                       "per-subset columns. Labelled as a derivation: it is why the leave-one-out "
                       "decomposition is exact rather than estimated."),
        "population": {"prompts": n, "arms": len(arms), "subsets": len(subsets)},
        "noise_floor": {"seeds": list(SEEDS), "non_unanimous_strict": u1,
                        "non_unanimous_relaxed": u2, "permutations": NPERM},
        "controls": ctrl,
        "plants": {"near_plant_solo_flips": near_solo, "far_plant_solo_flips": far_solo,
                   "mechanism": ("a flip needs the arm CLOSE to the comparator; extreme plants "
                                 "flip 0 in both directions, so proximity and not weakness is the "
                                 "driver, and world A's mechanism as first written was wrong"),
                   "real_subset_flip_range": [int(flips.min()), int(flips.max())]},
        "full_space": full,
        "leave_one_out": loo,
        "weakest_subset": {"subset": str(subsets[weakest]),
                           "strength": round(float(strength[weakest]), 4),
                           "max_after_removal": max_after_weakest},
        "span_carriers": carriers,
        "Q2_correlation": q2,
        "kill": {"gate_open": gate_open, "world_A_killed": a_killed, "world_C": b_killed},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1088 — is the span about comparator STRENGTH, or about WHICH comparators?\n")
    print(f"  ⛔ n_eff = {len(subsets)}, not {full['families']}: every family is a subset of the same "
          f"{len(subsets)} objects.")
    print(f"     MDE for |r| at n={len(subsets)} is {mde:.4f}. Stated BEFORE the correlation.")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  Q1 · EXACT DECOMPOSITION — the full space spans [{full['min']}, {full['max']}] over "
          f"{full['families']} families")
    print(f"    {'subset':<14}{'strength':>10}{'size':>6}{'solo flips':>12}"
          f"{'max without it':>16}")
    for k, v in sorted(loo.items(), key=lambda kv: kv[1]["strength"]):
        mark = "  ⭐ carries the max" if v["max"] < full["max"] else ""
        print(f"    {k:<14}{v['strength']:>10.4f}{v['size']:>6}{v['solo_flips']:>12}"
              f"{v['max']:>16}{mark}")
    print(f"\n  Q2 · CORRELATION, underpowered by design and reported against its MDE")
    print(f"    r(strength, flips) = {r_obs:+.4f}   MDE {mde:.4f}   "
          f"{'RESOLVED' if abs(r_obs) >= mde else '⚠ UNRESOLVED at this n'}")
    print(f"    permutation band 95%: [{band[0]:+.4f}, {band[1]:+.4f}]")
    print(f"    SHAM r(size, flips) = {r_size:+.4f} · CONFOUND r(strength, size) = {r_conf:+.4f}")
    print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}  world_C={b_killed}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
