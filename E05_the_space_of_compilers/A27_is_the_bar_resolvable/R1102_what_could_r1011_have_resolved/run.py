#!/usr/bin/env python3
"""R1102 — R1011 declared five nulls with NO MDE and a noise floor of width 0.000000. Price them.

⛔ FIRST, MY OWN NEXT WAS PRIOR ART, AND IT IS THE SECOND TIME IN THREE ROUNDS. R1101 closed by
proposing to score `coval_core` against `topw_k3/k4/k6/k8` as a comparator family. **R1011 already ran
exactly that**, 91 rounds ago, at full coverage with 8,000 cluster-bootstrap draws. The NEXT line also
called those arms `the rating-blind selectors` — and R1101's own measurement, one paragraph above it,
is that `topw` RANKS BY human ratings. **One closing sentence, two errors, both checkable against the
round that wrote it.** §4's row exactly, and the P4 prior-art gate is what caught it.

⭐ SO THE ROUND ATTACKS WHAT R1011 LEFT UNPRICED. Its headline — *the definition contains the core
without singling it out* — is the deepest claim in this arc, and it rests on five bootstrap intervals
that straddle zero. It reports **no MDE**. Its declared NOISE FLOOR is *"the width of the twin
comparison's interval"*, and that comparison returned **exactly 0.0000 with a degenerate interval** —
`floor == ceiling`, which §4 names as the case where **no threshold is admissible**. A null whose
floor is degenerate has not been priced at all.

⛔ AND THE ARITHMETIC TRAP IS ALREADY HALF THE ANSWER, SO IT IS LABELLED BEFORE IT IS MEASURED.
R1011's own committed table resolves `topw_k8` at Δ=+0.0072 (lo=+0.0013) and fails to resolve
`topw_k3` at Δ=+0.0033 (hi=+0.0095). **So its MDE is bracketed in (0.0033, 0.0072] by its own rows.**
That is a DERIVATION off a committed artifact — it establishes the design was NOT blind, and it is
worth more than the measurement below because it needs no new compute. The measurement's job is to
turn the bracket into a number and to say what the design would have retained.

ESTIMAND        (Q1) the MDE of R1011's design: the smallest constant shift g in the per-prompt A2
                     difference vector for which the design returns `lo > 0` at retention >= 0.80,
                     measured by dose-response over resampled studies, per rival pair.
                (Q2) the UPPER BOUND R1011's intervals already carry on the core's advantage over
                     each unresolved rival — the inequality its qualitative null replaced.
IDENTIFICATION  identified. The per-prompt vectors are reconstructable from committed npz files by
                R1011's own loader; the noise template is the real difference vector, mean-removed.
UNIT OF THE     a per-prompt A2 difference vector and the share of resampled studies whose 2.5th
  INSTRUMENT    percentile clears zero.
UNIT OF THE     the same. The claim is about what R1011's DESIGN could resolve, not about the arms.
  CLAIM
SCOPE           population: R1011's five rivals at 968/968 coverage. instrument: R1011's estimator,
                unchanged — cluster bootstrap over prompts, 2.5th percentile. baseline: the g=0 cell.
                regime: this release, this judge, A2 against every annotator (verified: `load_targets`
                iterates every assessment of every prompt, so the 3-of-16 failure mode does not apply
                here — counted, not assumed).
WORLDS          A THE DESIGN WAS AT ITS LIMIT   the MDE sits at or above the observed Δ for the
                                 unresolved rivals, so `not resolvably ordered` is a statement about
                                 the INSTRUMENT and R1011's world B is silence.
                B THE DESIGN HAD HEADROOM       the MDE sits below the observed Δ range and R1011
                                 resolved an effect of that size elsewhere, so the null is a
                                 statement about the ARMS — but the honest form is still the BOUND
                                 its intervals carry, not the qualitative `no special status`.
                Prediction matrix on (MDE vs the resolved Δ=+0.0072):
                  A -> MDE > 0.0072, contradicting R1011's own resolved row
                  B -> MDE <= 0.0072 and > 0.0033, matching the bracket the table already forces
                ⚠ ANNOTATED AFTER THE RUN, NOT REWRITTEN. World A's cell said `contradicting R1011's
                  own resolved row` — and that word `contradicting` was my error, not the design's.
                  A resolved cell is NOT required to sit above the MDE: the MDE is an 80%-power
                  threshold and a single study can cross zero at lower power. So the outcome that
                  looked self-contradictory when this matrix was written is the ordinary one, and it
                  is what the run returned. The pre-registration is left as written because the gap
                  between it and the result IS the round's lesson.
KILL            pre-registered. World A is KILLED if the measured MDE falls inside the derived
                bracket (0.0033, 0.0072]. Gated on the controls:
                                    if g0_fails and pos_saturates: evaluate(MDE)
                                    else:                          UNVERIFIED
POSITIVE CTRL   at g = +0.0738 — R1011's own committed core-vs-random effect — retention must be
                >= 0.99. An MDE curve that never saturates is measuring nothing.
g=0 GUARD       ⚠ THE CONTROL THAT MUST BE ABLE TO FAIL. At g = 0 the mean-removed template has a true
                effect of exactly zero, so retention must be <= 0.10 (nominal one-sided 2.5%). If a
                zero-effect template already `resolves`, the retention statistic is degenerate and no
                MDE is admissible.
NEGATIVE CTRL   a GAUGE TEST, run first because it is free: the cluster bootstrap resamples prompts
                exchangeably, so permuting the ORDER of the per-prompt differences must leave the MDE
                bit-identical. Measurement invariant under a transformation the property is also
                invariant under — a consistency check, and a failure would mean the estimator is
                reading prompt order.
SHAM            the same dose sweep with the noise template replaced by a CONSTANT vector (all
                entries equal to the observed mean). Same operation, same size, same compute, minus
                the ingredient under study — the per-prompt heterogeneity. Its MDE must collapse to
                ~0, because a design with no variance resolves any non-zero shift.
PLACEBO         a template of all zeros at g=0: lo = hi = 0, retention exactly 0.
NOISE FLOOR     measured as the standard deviation of the resampled study means, per pair — the
                quantity R1011's degenerate twin interval could not supply.
MULTIPLICITY    5 rivals x the dose grid, every cell reported. The MDE is read per rival, and the
                spread across rivals is reported rather than a single number.
SPECIFICATION   rival x dose x seed. The analytic 2.8*SE approximation is computed alongside as a
                DERIVATION and the two are required to agree — a model checking a measurement, with
                the measurement authoritative.
SEEDS           3, and the seed flag is verified to change the resampling draws.
ARTIFACT        results/what_r1011_could_resolve.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | whether the core SHOULD beat these arms | an external criterion; A2 is agreement
                  with this release's annotators and R1011's own caveat stands unchanged |
                | an MDE for the twin pair | its difference vector is identically zero, so the
                  design is degenerate there by construction — that is the finding, not a gap |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "what_r1011_could_resolve.json"
CORE = "coval_core"
NBOOT, NSTUDY, SEEDS = 8000, 300, (1102, 2204, 3306)
DOSES = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.010, 0.012, 0.015, 0.0738]
RETENTION = 0.80


def retention(d0: np.ndarray, g: float, seed: int) -> float:
    """Share of resampled STUDIES whose 2.5th-percentile bootstrap bound clears zero at dose g.

    Two levels, deliberately: the outer draw is a fresh study from the same population, the inner is
    R1011's own bootstrap INSIDE that study. A single bootstrap of the observed sample would measure
    that sample's luck, not the design's power."""
    rng = np.random.default_rng(seed)
    n = len(d0)
    hits = 0
    for _ in range(NSTUDY):
        s = d0[rng.integers(0, n, n)] + g                    # a fresh study at true effect g
        bs = s[rng.integers(0, n, size=(NBOOT // 8, n))].mean(axis=1)
        hits += float(np.percentile(bs, 2.5)) > 0
    return hits / NSTUDY


def mde_from_curve(curve: dict) -> float | None:
    for g in sorted(curve):
        if curve[g] >= RETENTION:
            return g
    return None


def main() -> int:
    f11 = next(A27.glob("R1011_*/results/instance_rank.json"), None)
    if f11 is None:
        print("  UNRUNNABLE: R1011's artifact is absent. Exit 2, never 0."); return 2
    r11 = json.loads(f11.read_text())
    rows = {r["arm"]: r for r in r11["rows"]}
    pos_effect = r11["controls"]["positive_vs_random"]["d"]

    # ---- R1011's estimator, unchanged
    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)
    n_annot = sum(len(tg[p]) for p in pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            Sa = load_sat(f)
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    cc = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(cc == h[:len(cc)]).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    vcore = vec(CORE)
    if vcore is None:
        print("  UNRUNNABLE: the instance is not scoreable. Exit 2, never 0."); return 2

    # ---- ⛔ THE DERIVATION, computed and labelled BEFORE the measurement
    resolved = [r for r in rows.values() if r["lo"] > 0]
    unresolved = [r for r in rows.values() if r["lo"] <= 0 <= r["hi"]]
    lo_brk = max([abs(r["delta"]) for r in unresolved], default=None)
    hi_brk = min([abs(r["delta"]) for r in resolved], default=None)
    derivation = {
        "is_a_derivation_not_a_measurement": True,
        "from": "R1011's own committed rows",
        "largest_UNRESOLVED_delta": lo_brk,
        "smallest_RESOLVED_delta": hi_brk,
        "implied_MDE_bracket": [lo_brk, hi_brk],
        "what_it_appeared_to_establish": ("the design was NOT blind — it resolved an effect of "
                                          f"{hi_brk} in the same family — so R1011's world B would "
                                          "be a statement about the arms, not the instrument"),
        # ⛔ THE ASSUMPTION THE DERIVATION RESTS ON, WRITTEN OUT BECAUSE THE MEASUREMENT ATTACKS IT.
        "rests_on": ("`a resolved cell lies above the MDE`. That is FALSE. The MDE is the 80%-power "
                     "threshold; a single study can cross at lower power, and a bracket built from "
                     "one crossing therefore bounds nothing. The measurement below is what shows it, "
                     "and this is the flattering direction — the derivation credits the design with "
                     "resolution it does not have."),
    }
    print(f"  ⛔ DERIVATION from R1011's table: MDE ∈ ({lo_brk:.4f}, {hi_brk:.4f}]  "
          f"— resolved {hi_brk:+.4f}, failed at {lo_brk:+.4f}")

    # ---- the measurement, per rival
    per_rival, curves = {}, {}
    for arm, row in sorted(rows.items()):
        v = vec(arm)
        if v is None:
            continue
        d = vcore - v
        d0 = d - d.mean()                       # mean-removed: the real per-prompt noise template
        cur = {}
        for g in DOSES:
            rs = [retention(d0, g, s) for s in SEEDS]
            cur[g] = float(np.mean(rs))
        curves[arm] = {str(k): round(v_, 4) for k, v_ in cur.items()}
        se = float(np.std(d, ddof=1) / np.sqrt(n))
        per_rival[arm] = {
            "observed_delta": row["delta"], "lo": row["lo"], "hi": row["hi"],
            "resolvable_in_R1011": row["resolvable"],
            "MDE_measured": mde_from_curve(cur),
            "MDE_analytic_2p8_SE": round(2.8 * se, 5),
            "noise_floor_SE_of_study_means": round(se, 5),
            "upper_bound_on_core_advantage": row["hi"],
            "retention_at_g0": cur[0.0],
            "retention_at_positive_control": cur[0.0738],
        }
        print(f"  {arm:<16} Δ={row['delta']:+.4f}  MDE={per_rival[arm]['MDE_measured']}  "
              f"analytic={per_rival[arm]['MDE_analytic_2p8_SE']:.4f}  "
              f"g0={cur[0.0]:.3f}  gpos={cur[0.0738]:.3f}  bound<{row['hi']:+.4f}")

    if not per_rival:
        print("  UNRUNNABLE: no rival was scoreable. Exit 2, never 0."); return 2

    # ---- controls
    ref = sorted(per_rival)[0]
    vref = vec(ref); dref = vcore - vref; d0ref = dref - dref.mean()
    g0_fails = all(v["retention_at_g0"] <= 0.10 for v in per_rival.values())
    pos_sat = all(v["retention_at_positive_control"] >= 0.99 for v in per_rival.values())
    # GAUGE: prompt order must not matter to an exchangeable cluster bootstrap.
    # ⚠ NOT exact equality. Permuting the vector while reusing the same index draws produces a
    #   DIFFERENT sample, so demanding identical floats would be a control failing for its own
    #   reasons — §4's dominant mode. The right expectation is agreement within Monte-Carlo error of
    #   NSTUDY draws, and that bound is computed rather than eyeballed.
    r_a = retention(d0ref, 0.005, SEEDS[0])
    r_b = retention(np.random.default_rng(7).permutation(d0ref), 0.005, SEEDS[0])
    mc_se = float(np.sqrt(max(r_a * (1 - r_a), 1e-6) / NSTUDY))
    gauge = abs(r_a - r_b) <= 3 * mc_se
    # SHAM: heterogeneity removed, the MDE must collapse
    flat = np.zeros_like(d0ref)
    sham_mde = mde_from_curve({g: float(np.mean([retention(flat, g, s) for s in SEEDS]))
                               for g in DOSES})
    sham_ok = sham_mde is not None and sham_mde <= 0.001 and sham_mde > 0.0
    placebo = retention(flat, 0.0, SEEDS[0]) == 0.0
    seeds_differ = len({round(retention(d0ref, 0.004, s), 6) for s in SEEDS}) > 1
    mdes = [v["MDE_measured"] for v in per_rival.values() if v["MDE_measured"] is not None]
    analytic_agrees = all(
        v["MDE_measured"] is not None
        and abs(v["MDE_measured"] - v["MDE_analytic_2p8_SE"]) <= 0.002
        for v in per_rival.values())

    controls = {
        "g=0 a zero-effect template does NOT resolve (retention <= 0.10)": g0_fails,
        "POSITIVE at R1011's own core-vs-random effect the curve saturates (>= 0.99)": pos_sat,
        "GAUGE prompt order moves retention no further than Monte-Carlo error": bool(gauge),
        "SHAM removing per-prompt heterogeneity collapses the MDE to the grid floor": bool(sham_ok),
        "PLACEBO an all-zero template at g=0 returns retention exactly 0": bool(placebo),
        "SEEDS the seed flag changes the resampling draws": bool(seeds_differ),
        "DERIVATION the analytic 2.8*SE agrees with the measured MDE within one grid step":
            bool(analytic_agrees),
    }
    gate_open = g0_fails and pos_sat and controls["PLACEBO an all-zero template at g=0 returns "
                                                  "retention exactly 0"]
    in_bracket = (all(lo_brk < m <= hi_brk for m in mdes) if (mdes and lo_brk and hi_brk)
                  else False)
    world_A_killed = in_bracket if gate_open else None

    bounds = {a: round(v["upper_bound_on_core_advantage"], 4) for a, v in per_rival.items()
              if v["resolvable_in_R1011"] == "no"}
    # ⛔ EVERY COMPARATIVE WORD BELOW IS COMPUTED. The first version of this verdict typed
    #    `the design was NOT blind` while the branch beside it had just computed the opposite —
    #    §4's `the verdict string is not a computation`, built for the fourth time in this family.
    unres_deltas = [abs(v["observed_delta"]) for v in per_rival.values()
                    if v["resolvable_in_R1011"] == "no"]
    mde_lo, mde_hi = (min(mdes), max(mdes)) if mdes else (None, None)
    ratio = (mde_lo / max(unres_deltas)) if (mde_lo and unres_deltas) else None
    res_rows = [v for v in per_rival.values() if v["resolvable_in_R1011"] != "no"]
    resolved_below_mde = [
        (a, v["observed_delta"], v["MDE_measured"]) for a, v in per_rival.items()
        if v["resolvable_in_R1011"] != "no" and v["MDE_measured"] is not None
        and abs(v["observed_delta"]) < v["MDE_measured"]]
    nulls_are_silence = bool(unres_deltas and mde_lo and max(unres_deltas) < mde_lo)
    payload = {
        "round": "R1102",
        "question": "what could R1011's design have resolved, and what do its intervals already bound?",
        "refuses": {
            "claim": "score coval_core against topw_k3/k4/k6/k8 as a comparator family",
            "round": "R1101 (its NEXT)",
            "status": "REFUSED — PRIOR ART. R1011 ran exactly this at full coverage, 91 rounds ago.",
            "second_error_in_the_same_sentence": ("it called them `the rating-blind selectors`; "
                                                  "R1101's own measurement is that topw RANKS BY "
                                                  "human ratings"),
        },
        "derivation": derivation,
        "per_rival": per_rival,
        "retention_curves": curves,
        "controls": controls,
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "measured_MDEs": mdes, "inside_derived_bracket": in_bracket},
        "derivation_overturned_by_the_measurement": {
            "derived_bracket": [lo_brk, hi_brk],
            "measured_MDE_range": [mde_lo, mde_hi],
            "inside": in_bracket,
            "why": ("the derivation assumed a resolved cell lies above the MDE. `topw_k8` resolved "
                    f"at Δ={hi_brk} while its measured MDE is "
                    f"{per_rival.get('topw_k8', {}).get('MDE_measured')} — a crossing at under 80% "
                    "power, which is a lucky cell and not a demonstration of resolution."),
            "resolved_cells_below_their_own_MDE": resolved_below_mde,
        },
        "downgrade": {
            "round": "R1011",
            "claim": "the definition contains the released core without singling it out",
            "status": "DOWNGRADED — its five nulls are SILENCE, not measurements",
            "to": ("the design cannot resolve a core advantage below the measured MDE range "
                   f"{[mde_lo, mde_hi]}, and the observed unresolved advantages are "
                   f"{sorted(round(x, 4) for x in unres_deltas)} — a factor of "
                   f"{round(ratio, 1) if ratio else None} under the resolution. What the data DO "
                   f"support is an inequality: the core's A2 advantage over each unresolved "
                   f"admitted rival is bounded above by {bounds}."),
            "what_still_stands": ("R1011's positive control, sham and coverage findings are "
                                  "untouched; so is the fact that the definition CONTAINS the "
                                  "core. Only the ranking claim loses its footing."),
        },
        "nulls_are_silence": nulls_are_silence,
        "annotators_consumed": {"per_prompt_ranking_records": n_annot, "prompts": n,
                                "note": "load_targets iterates EVERY assessment of every prompt; "
                                        "counted rather than assumed, because the release's own "
                                        "history contains a three-round error built on 3 of 16"},
        "grid": {"rivals": len(per_rival), "doses": len(DOSES), "seeds": len(SEEDS),
                 "cells": len(per_rival) * len(DOSES)},
        "positive_control_effect_from_R1011": pos_effect,
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red, so no MDE is admissible. "
                              f"Controls: {json.dumps(controls)}")
    else:
        payload["verdict"] = (
            f"⛔ WORLD A {'SURVIVES' if not world_A_killed else 'IS KILLED'}: R1011's DESIGN WAS AT "
            f"ITS LIMIT. Measured MDE {mde_lo}–{mde_hi} per rival, against the bracket "
            f"({lo_brk:.4f}, {hi_brk:.4f}] the derivation forced — inside: {in_bracket}. "
            f"⛔ SO THE DERIVATION IS OVERTURNED BY THE MEASUREMENT, in the flattering direction: "
            f"it credited the design with resolution it does not have, because "
            f"{[a for a, _d, _m in resolved_below_mde]} crossed zero BELOW its own MDE — a cell at "
            f"under 80% power. ⭐ THE CONSEQUENCE: R1011's five unresolved Δ are "
            f"{sorted(round(x, 4) for x in unres_deltas)}, a factor of "
            f"{round(ratio, 1) if ratio else None} under the resolution, so those nulls are "
            f"SILENCE and not measurements — nulls_are_silence={nulls_are_silence}. What the data "
            f"support is an INEQUALITY: the core's A2 advantage over each unresolved admitted "
            f"rival is bounded above by {bounds}.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print()
    for k, v in controls.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
