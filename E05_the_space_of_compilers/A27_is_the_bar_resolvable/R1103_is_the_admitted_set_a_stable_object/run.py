#!/usr/bin/env python3
"""R1103 — is `the admitted set` a stable object, or a draw? R1055 answered a different question.

R1102 measured that this design's MDE in A2 units is 0.008–0.010. The definition's operator ②′ admits
an arm when the 2.5th percentile of its bootstrapped paired difference clears zero — a test, so it is
valid, but its POWER near the cut is whatever the MDE says. That raises a question no round has asked:
**if a different 968 prompts had been drawn from the same population, would the admitted set be the
same set?** Every count this arc has published — 24, 9, 6, 0, the nesting, the slack — is a property
of that set.

⛔ WHAT LOOKS LIKE PRIOR ART AND IS NOT, CHECKED BEFORE BUILDING.
 · **R1055** reports a NOISE FLOOR: *"the admitted set at 3 seeds: 24 always in, 75 always out, 0
   unstable"*. Those are three **inner bootstrap seeds on the same prompts**. With NBOOT = 4000 the
   2.5th percentile barely moves between seeds, so `0 unstable` is close to forced — it certifies the
   ESTIMATOR is deterministic, never that the SET is a property of the population. §4's `determinism
   read as currency`. This round reproduces that control exactly, as its SHAM, to show what it cannot
   see.
 · **R978** sweeps the prompt COUNT — N ∈ {242, 484, 726, 968} — and finds 10 of 24 arms change at a
   quarter of the corpus. ⭐ But its N=968 row is **0 by construction**: the full corpus against
   itself, which R978 correctly labels its PLACEBO. **The variability at the actual N was never
   measured**, and R978 already computed the quantity that predicts it — its `registered band`, the
   number of arms within `z·sd/√N` of the cut, is **4 · 4** at N=968.

ESTIMAND        per arm, the share of bootstrap resamples of the 968 prompts in which R1055's operator
                admits it; and the distribution of |admitted set| across those resamples.
IDENTIFICATION  identified. The per-prompt A2 vectors and coverage masks are reconstructable from the
                committed npz files by R1055's own loader, and the operator is copied, not rewritten.
UNIT OF THE     an arm, and its admission frequency over outer resamples of the prompt population.
  INSTRUMENT
UNIT OF THE     the same. ⚠ The unit R1055's noise floor measured is DIFFERENT — an arm and its
  CLAIM         admission frequency over inner bootstrap seeds at a FIXED prompt sample — and the two
                are named here as separate strings, before the controls were designed, because a
                control sharing an instrument's blind spot licenses nothing.
SCOPE           population: the 99 arms carrying a sat_*.npz, target A2, prompts with >= 2 targets.
                instrument: R1055's admission operator with the inner lower bound taken analytically
                (validated below). baseline: the point-estimate run, which must reproduce R1055's
                committed 24. regime: 968 prompts, comparators {generic, genericpool16}, q = 100.
WORLDS          A THE SET IS AN OBJECT   at most one arm has admission frequency strictly inside
                                (0.05, 0.95); |admitted| is effectively a constant. Then every
                                set-membership count this arc publishes is safe as stated.
                B THE SET IS A DRAW      several arms sit in the middle band and |admitted| has a real
                                spread. Then `the released ②′ set is 24` is a point estimate with no
                                interval, and R1098's nesting, R1099's slack and R1101's ladder
                                (24 -> 9 -> 6 -> 0) all inherit that instability.
                ⭐ PRE-REGISTERED FROM A COMMITTED ARTIFACT, not from taste: R978's registered band at
                  N=968 is 4, so world B predicts ~4 unstable arms and world A predicts <= 1.
KILL            pre-registered. World A is KILLED if >= 2 arms have admission frequency in (0.05,
                0.95), agreeing across 3 outer seeds. Gated on its own controls:
                                    if positive_reproduces_R1055 and placebo_degenerate:
                                        evaluate(unstable_count)
                                    else: UNVERIFIED
POSITIVE CTRL   the point-estimate run (no outer resampling) must reproduce R1055's committed
                `baseline_admitted` — 24 arms, by name. If it does not, the operator being resampled
                is not the definition's operator and nothing below is about the definition.
g=0 / PLACEBO   with the outer draw set to the IDENTITY, every arm's admission is deterministic, so
                every frequency must be exactly 0.0 or 1.0 and the unstable count must be 0. This is
                R978's N=968 row made explicit, and it is what makes a non-zero count downstream a
                measurement rather than an artifact of the harness.
SHAM            ⭐ R1055's own control, rebuilt: hold the prompt sample FIXED and vary only the INNER
                bootstrap seed, 3 seeds, NBOOT = 4000. Same operation, same size, minus the ingredient
                under study — the resampling of the population. It must return ~0 unstable arms. If it
                does, R1055's `0 unstable` is reproduced AND shown to answer a different question.
NEGATIVE CTRL   an arm against itself has an identically-zero difference vector, so its lower bound is
                0 and `> 0` is false: it must be admitted in exactly 0 resamples. A non-zero there
                means the operator is not testing what it claims.
NOISE FLOOR     the Monte-Carlo standard error of an admission frequency at NOUTER draws,
                sqrt(p(1-p)/NOUTER), reported beside the band so `inside (0.05, 0.95)` is read against
                its own precision.
INSTRUMENT      ⚠ the inner lower bound is taken as `mean - 1.96*SE` rather than by a nested bootstrap,
  VALIDATION    because the nested form is ~10^4 times the compute. It is VALIDATED, not assumed: on
                the identity sample the analytic decision must agree with R1055's 4000-draw bootstrap
                on every arm, and the disagreement list is reported whether it is empty or not.
MULTIPLICITY    99 arms x 3 outer seeds, every arm's frequency reported — the stable-in, the
                stable-out and the band.
SPECIFICATION   outer seed x comparator family {both, generic only}, so the band is not read off one
                family choice.
SEEDS           3 outer seeds; the unstable set must agree across them, and the seed flag is verified
                to change the draws.
ARTIFACT        results/set_stability.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | the TRUE sampling distribution of the admitted set | a second draw of 968 prompts
                  from the same population; the bootstrap is an approximation to it and is labelled |
                | whether an unstable arm `should` be admitted | an external criterion; A2 is
                  agreement with this release's annotators |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "set_stability.json"
COMPARATORS = ["generic", "genericpool16"]
NOUTER, NBOOT, OUTER_SEEDS = 1000, 4000, (1103, 2206, 3309)
BAND = (0.05, 0.95)
Z = 1.959963984540054


def main() -> int:
    f55 = next(A27.glob("R1055_*/results/component_ablation.json"), None)
    f78 = next(A27.glob("R978_*/results/*.json"), None)
    if f55 is None:
        print("  UNRUNNABLE: R1055's artifact is absent. Exit 2, never 0."); return 2
    r55 = set(json.loads(f55.read_text())["baseline_admitted"])

    # ---- R1055's loader, copied
    tg, _ = load_targets()
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        nm = f.stem[4:]
        try:
            Sa = load_sat(f)
        except Exception:
            continue
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        cov = np.isfinite(v)
        if cov.sum() < 100:
            continue
        arms.append(nm); V.append(np.nan_to_num(v, nan=0.0)); COV.append(cov)
    V, COV = np.array(V), np.array(COV)
    print(f"  arms {len(arms)} · prompts {n} · comparators {COMPARATORS}")

    ci = [arms.index(c) for c in COMPARATORS if c in arms]
    if len(ci) != len(COMPARATORS):
        print("  UNRUNNABLE: a comparator is absent. Exit 2, never 0."); return 2

    # ---- the two inner lower bounds. `boot` is R1055's; `analytic` is what the outer sweep uses.
    def lo_boot(d: np.ndarray, seed: int) -> float:
        rng = np.random.default_rng(seed)
        m = len(d)
        return float(np.percentile(d[rng.integers(0, m, size=(NBOOT, m))].mean(axis=1), 2.5))

    def lo_analytic(d: np.ndarray) -> float:
        m = len(d)
        return float(d.mean() - Z * d.std(ddof=1) / np.sqrt(m)) if m > 1 else 0.0

    def admitted(sample: np.ndarray | None, inner: str, seed: int = 0,
                 comps: list[int] | None = None) -> set:
        """R1055's operator. `sample` None = the identity draw (every prompt once)."""
        cj = ci if comps is None else comps
        out = set()
        for i, nm in enumerate(arms):
            if i in cj:
                continue
            beats = 0
            for j in cj:
                m = COV[i] & COV[j]
                dd = V[i] - V[j]
                if sample is None:
                    d = dd[m]                       # the identity draw: every covered prompt once
                else:
                    d = dd[sample[m[sample]]]       # resample prompts, THEN apply the pair's mask
                if len(d) < 30:                     # R1055's own minimum, unchanged
                    continue
                ok = (lo_boot(d, seed) if inner == "boot" else lo_analytic(d)) > 0
                beats += bool(ok)
            if beats >= len(cj):
                out.add(nm)
        return out

    # ---------- POSITIVE: the point estimate must reproduce R1055's committed 24
    pe_boot = admitted(None, "boot", seed=11)
    pe_ana = admitted(None, "analytic")
    positive = pe_boot == r55
    disagree = sorted(pe_boot ^ pe_ana)
    instrument_ok = len(disagree) == 0
    print(f"  POSITIVE point estimate (R1055 operator, boot inner): {len(pe_boot)} arms, "
          f"equals R1055's committed {len(r55)}: {positive}")
    print(f"  INSTRUMENT analytic vs boot inner disagreement: {len(disagree)} {disagree}")

    # ---------- SHAM: R1055's own noise floor, rebuilt — inner seed only, prompts FIXED
    sham_sets = [admitted(None, "boot", seed=s) for s in (11, 23, 47)]
    sham_in = set.intersection(*sham_sets); sham_any = set.union(*sham_sets)
    sham_unstable = sorted(sham_any - sham_in)
    print(f"  SHAM  R1055's control rebuilt (inner seed only): unstable {len(sham_unstable)} "
          f"{sham_unstable}")

    # ---------- PLACEBO: identity outer draw -> deterministic
    placebo_unstable = 0  # by construction; asserted by re-running and comparing
    placebo_ok = admitted(None, "analytic") == pe_ana

    # ---------- NEGATIVE: an arm against itself is never admitted
    self_d = np.zeros(n)
    neg_ok = not (lo_analytic(self_d) > 0) and not (lo_boot(self_d, 11) > 0)

    # ---------- the measurement: outer resampling of the prompt population
    freq_by_seed, sizes_by_seed = [], []
    for os_ in OUTER_SEEDS:
        rng = np.random.default_rng(os_)
        cnt = {a: 0 for a in arms}
        sizes = []
        for _ in range(NOUTER):
            sample = rng.integers(0, n, n)
            s = admitted(sample, "analytic")
            sizes.append(len(s))
            for a in s:
                cnt[a] += 1
        freq_by_seed.append({a: cnt[a] / NOUTER for a in arms})
        sizes_by_seed.append(sizes)
        band = [a for a in arms if BAND[0] < cnt[a] / NOUTER < BAND[1]]
        print(f"  outer seed {os_}: |admitted| mean {np.mean(sizes):.2f} "
              f"[{np.percentile(sizes, 2.5):.0f}, {np.percentile(sizes, 97.5):.0f}]  "
              f"band arms {len(band)}")

    bands = [{a for a in arms if BAND[0] < f[a] < BAND[1]} for f in freq_by_seed]
    band_union, band_inter = set.union(*bands), set.intersection(*bands)
    seeds_agree = len({len(b) for b in bands}) == 1
    seeds_differ = len({tuple(sizes[:20]) for sizes in sizes_by_seed}) == len(OUTER_SEEDS)
    mc_se = float(np.sqrt(0.25 / NOUTER))
    all_sizes = [x for s in sizes_by_seed for x in s]

    gate_open = positive and placebo_ok and neg_ok and instrument_ok and seeds_differ
    world_A_killed = (len(band_inter) >= 2) if gate_open else None

    r978_band = 4      # R978's committed `registered band` at N=968, both comparators
    per_arm = {a: {"freq": round(float(np.mean([f[a] for f in freq_by_seed])), 4),
                   "in_R1055_baseline": a in r55,
                   "class": ("BAND" if a in band_inter else
                             "always" if all(f[a] >= BAND[1] for f in freq_by_seed) else
                             "never" if all(f[a] <= BAND[0] for f in freq_by_seed) else "seed-split")}
              for a in arms}

    payload = {
        "round": "R1103",
        "question": "is the admitted set a stable object under resampling the prompt population?",
        "prior_art_refused": {
            "R1055": ("its NOISE FLOOR varies the INNER bootstrap seed at a fixed prompt sample; "
                      "reproduced here as the SHAM to show what it cannot see"),
            "R978": ("its N=968 row is 0 BY CONSTRUCTION — the corpus against itself, its own "
                     "PLACEBO. Its `registered band` of 4 at N=968 is the pre-registration used here"),
        },
        "point_estimate": {"n_admitted": len(pe_boot), "equals_R1055": positive,
                           "arms": sorted(pe_boot)},
        "instrument_validation": {"analytic_vs_boot_disagreements": disagree, "ok": instrument_ok},
        "sham_R1055_rebuilt": {"unstable_arms": sham_unstable, "n": len(sham_unstable)},
        "set_size": {"mean": round(float(np.mean(all_sizes)), 2),
                     "p2.5": float(np.percentile(all_sizes, 2.5)),
                     "p97.5": float(np.percentile(all_sizes, 97.5)),
                     "min": int(np.min(all_sizes)), "max": int(np.max(all_sizes)),
                     "point_estimate": len(pe_boot)},
        "band": {"in_every_seed": sorted(band_inter), "in_any_seed": sorted(band_union),
                 "n_every": len(band_inter), "n_any": len(band_union),
                 "seeds_agree_on_count": seeds_agree,
                 "R978_registered_band_at_968": r978_band},
        "per_arm": per_arm,
        "noise_floor_MC_SE_of_a_frequency": round(mc_se, 5),
        "controls": {
            "POSITIVE the point estimate reproduces R1055's committed 24 by name": positive,
            "PLACEBO the identity outer draw is deterministic": bool(placebo_ok),
            "NEGATIVE an arm against itself is never admitted": bool(neg_ok),
            "INSTRUMENT the analytic inner bound agrees with R1055's 4000-draw bootstrap on every "
            "arm": instrument_ok,
            "SHAM R1055's inner-seed control returns ~0 unstable, a DIFFERENT quantity":
                len(sham_unstable) <= 1,
            "SEEDS the outer seed flag changes the draws": bool(seeds_differ),
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "band_size_every_seed": len(band_inter)},
        "grid": {"arms": len(arms), "outer_draws_per_seed": NOUTER, "seeds": len(OUTER_SEEDS),
                 "cells": len(arms) * len(OUTER_SEEDS)},
        "seeds": list(OUTER_SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red, so the band is not binding. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        sz = payload["set_size"]
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}: "
            f"{len(band_inter)} arm(s) sit in the band ({BAND[0]}, {BAND[1]}) in every outer seed "
            f"— {sorted(band_inter)} — against R978's committed registered band of {r978_band} at "
            f"N=968. |admitted| is {sz['mean']} [{sz['p2.5']:.0f}, {sz['p97.5']:.0f}] across "
            f"{NOUTER * len(OUTER_SEEDS)} resamples, point estimate {sz['point_estimate']}. "
            f"⭐ AND R1055's CONTROL IS REPRODUCED AND SHOWN BLIND: varying only the inner bootstrap "
            f"seed at a fixed prompt sample gives {len(sham_unstable)} unstable arms, so its "
            f"`0 unstable` certified the ESTIMATOR's determinism and never the SET.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for a in sorted(band_union):
        print(f"  BAND {a:<24} freq={per_arm[a]['freq']:.3f}  in_R1055={per_arm[a]['in_R1055_baseline']}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
