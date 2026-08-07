#!/usr/bin/env python3
"""R1025 — clause ②′ says "beats EVERY comparator". The set has two members. Is `every` irreducible?

⛔ THE CHEAP VERSION OF THIS QUESTION IS ALREADY ANSWERED ON DISK AND IS NOT RE-RUN HERE. R921
   committed BOTH `survives_all_legitimate` (24 arms) and `admitted_by_at_least_one_legitimate` (28).
   They differ, so the two comparators DO disagree — about `generic`, `generic_reprov`,
   `greedy_k12_fit1`, `topw_k2`. Reading that off a committed artifact is a lookup, and a lookup
   cannot fail, so it is not a round. It is stated here as PRIOR ART, and this round starts after it.

⛔ AND R921's OWN COMMITTED DERIVATION DECIDES WHAT IS LEFT TO ASK. It records, in its own words:
   "mean margin(A,C) = mean A2(A) − mean A2(C); the second term is the same for every A". So the
   POINT-ESTIMATE ordering of arms is comparator-INVARIANT — that is algebra, not a measurement.
   `lo` is not the mean: it is a bootstrap 2.5th percentile, which depends on the VARIANCE of the
   paired difference, and that variance does depend on C. ⇒ **The entire content of "every
   comparator" is which comparator yields the TIGHTER interval.** Nothing else can differ.

   That reduces the wording question to a sign test, and the sign test is not forced:

ESTIMAND        sign(lo(A, generic) − lo(A, genericpool16)) across the arm population — is one
                comparator UNIFORMLY tighter, or does the tighter one change from arm to arm?
IDENTIFICATION  exact. Both bounds are computable for every scored arm from committed vectors.
SCOPE           population : R1000's 96 arms · instrument : R923's operator, NBOOT=8000
                baseline   : the two R921-certified comparators · regime : A2 (this arc's target),
                with A1·consensus swept as a second specification
WORLDS          A `every` IS A SHORTHAND FOR ONE COMPARATOR — the sign is constant across arms, so
                  min-over-comparators always selects the same one. Then the clause should NAME the
                  stricter comparator: simpler, equivalent, and it stops implying a generality the
                  two-member set does not have.
                B `every` IS IRREDUCIBLE — the sign FLIPS across arms, so no single comparator
                  reproduces the conjunction. Then the universal quantifier is load-bearing and the
                  wording stays, but the clause must say the set is a CHOICE (R921 certified 2 of a
                  larger pool), because the quantifier's strength is inherited from that choice.
                prediction matrix: A -> one sign dominates; flips (if any) sit inside seed noise.
                                   B -> both signs occur with |Δlo| ABOVE the seed spread.
                ⚠ ONTOLOGICAL, not parametric: A says the clause is redundant notation, B says it is
                  an irreducible conjunction. They imply different sentences in the definition.
KILL            pre-registered and CONDITIONAL:
                  if positive fires and the invariance derivation holds and placebo is exactly 0:
                      arms with a RESOLVED sign flip (|Δlo| > 3× seed spread) >= 1 -> World B
                      else                                                         -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ① my per-arm bounds must reproduce R921's committed sets EXACTLY: |survives all| = 24
                and |at least one| = 28, with the same membership. Any change to the operator, the
                population or the comparators breaks it.
                ② A SIGN-DETECTION control, because the kill turns on detecting UNIFORMITY: build a
                synthetic comparator = `generic` + iid noise, mean-matched. It is strictly noisier, so
                it must be UNIFORMLY less tight — if the instrument cannot return a constant sign
                where one is constructed, a constant sign measured on the real pair means nothing.
                ⚠ SCORED BY THE KILL'S OWN RULE (no RESOLVED minority sign), not by strict
                one-sidedness. The first version demanded 97/0 at every dose and failed at g=0.05 on
                a single noise-flip — a threshold above what the design returns at that dose, and a
                different statistic from the one being reported.
                ⚠ and it must fail at g=0: with noise scale 0 the synthetic IS `generic`, and every
                sign must then VANISH rather than be uniform.
NEGATIVE CTRL   the invariance derivation as a falsifier: mean-margin(A,gen) − mean-margin(A,p16)
                must be CONSTANT across A to machine precision. If it is not, the algebra above is
                wrong and every reduction in this round is void.
PLACEBO         lo(A, generic) − lo(A, generic) must be exactly 0.0 for every arm.
NOISE FLOOR     per-arm seed spread of Δlo over 3 bootstrap seeds, measured, printed, and used as the
                resolution threshold — no flip is called at or below it.
MULTIPLICITY    96 arms × 2 targets = 192 sign cells, all printed in summary; flips listed in full.
SEEDS           3, and the flip set must be identical under all three or it is reported as unstable.
IMPOSSIBLE      whether the CERTIFIED SET is the right set — R921 certified 2 from a larger pool, and
                testing the quantifier over comparators that were never scored costs 15,488 judge
                calls per comparator (R914). N/A here; what it would require is that scoring run.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEEDS = 8000, (1025, 2050, 3075)
TARGETS = ("A2", "A1·consensus")


def main() -> int:
    r921f = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1000f = next(A27.glob("R1000_*/results/*.json"), None)
    if not (r921f and r1000f):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    r921 = json.loads(r921f.read_text())
    legit = r921["legitimate_comparators"]
    pop = json.loads(r1000f.read_text())["population_arms"]
    want_all = set(r921["survives_all_legitimate"])
    want_one = set(r921["admitted_by_at_least_one_legitimate"])
    print(f"  PRIOR ART, read not re-derived — R921 committed both sets: |all| {len(want_all)} · "
          f"|at least one| {len(want_one)}\n     they disagree about "
          f"{sorted(want_one - want_all)} ⇒ the comparators are NOT interchangeable, and that fact\n"
          f"     needed no new run. This round starts after it.")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    Hc = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    CONS = {p: np.sign(np.array(Hc[p], float).sum(axis=0)) for p in pids}

    def raw(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            Sa = load_sat(f)
            a2, a1c = np.full(n, np.nan), np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                a2[k] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in Hc[p]]))
                m = min(len(c), len(CONS[p]))
                a1c[k] = float((c[:m] == CONS[p][:m]).all())
            if np.isfinite(a2).sum() < 200:
                return None
            return {"A2": np.nan_to_num(a2, nan=np.nanmean(a2)),
                    "A1·consensus": np.nan_to_num(a1c, nan=np.nanmean(a1c))}
        return None

    V, names = {}, []
    for a in sorted(set(pop) | set(legit)):
        r = raw(a)
        if r is not None:
            V[a], _ = r, names.append(a)
    print(f"  arms scored: {len(names)} · prompts {n}")

    IDX = {s: np.random.default_rng(s).integers(0, n, size=(NBOOT, n)) for s in SEEDS}

    def lo(vec_a, vec_c, s):
        return float(np.percentile((vec_a - vec_c)[IDX[s]].mean(axis=1), 2.5))

    # ---------- NEGATIVE / the derivation as a falsifier ----------
    diffs = [float((V[a]["A2"] - V[legit[0]]["A2"]).mean() - (V[a]["A2"] - V[legit[1]]["A2"]).mean())
             for a in names]
    inv_span = float(max(diffs) - min(diffs))
    inv_ok = inv_span < 1e-12
    print(f"\n  NEGATIVE (R921's derivation as a falsifier) — mean-margin(A,gen) − mean-margin(A,p16)"
          f"\n     must be CONSTANT across all {len(names)} arms or the reduction in this round is "
          f"void: span {inv_span:.3e} {'PASS' if inv_ok else '⛔ FAIL'}")
    print(f"     ⇒ the POINT ESTIMATE cannot distinguish the comparators. Only the INTERVAL can.")

    # ---------- POSITIVE ①: reproduce R921's two committed sets ----------
    LO = {(a, c, tn, s): lo(V[a][tn], V[c][tn], s)
          for a in names for c in legit for tn in TARGETS for s in SEEDS}
    got_all = {a for a in names if all(LO[(a, c, "A2", SEEDS[0])] > 0 for c in legit)}
    got_one = {a for a in names if any(LO[(a, c, "A2", SEEDS[0])] > 0 for c in legit)}
    okA, okB = got_all == want_all, got_one == want_one
    print(f"\n  POSITIVE ① — R921's committed sets must be reproduced by this code path")
    print(f"     survives ALL      mine {len(got_all):>3}  R921 {len(want_all):>3}  "
          f"{'PASS' if okA else '⛔ FAIL ' + str(sorted(got_all ^ want_all))}")
    print(f"     at least ONE      mine {len(got_one):>3}  R921 {len(want_one):>3}  "
          f"{'PASS' if okB else '⛔ FAIL ' + str(sorted(got_one ^ want_one))}")

    # ---------- POSITIVE ②: can this instrument SEE a uniform sign when one is constructed? ------
    print(f"\n  POSITIVE ② — the kill turns on detecting UNIFORMITY, so plant it. A synthetic")
    print(f"     comparator = `generic` + iid noise (mean-matched) is strictly NOISIER, so it must be")
    print(f"     uniformly LESS tight. And at noise 0 it IS `generic`, so the sign must vanish.")
    # ⚠ THIS CONTROL WAS SCORED BY THE WRONG RULE ON ITS FIRST RUN AND PRINTED FAIL WITH NOTHING
    #   WRONG. It demanded STRICT one-sidedness (97/0) at every planted dose, and at the SMALL dose
    #   g=0.05 got 96/1 — one arm flipped by bootstrap noise. That is the "control that cannot PASS"
    #   mode twice over: a threshold above what the design returns at that dose, AND a different
    #   statistic than the kill uses. The kill counts a minority sign only when |Δlo| exceeds 3× that
    #   arm's OWN seed spread; the control must be scored the same way or it is testing something else.
    sign_ctrl = {}
    for g in (0.0, 0.05, 0.20):
        rng = np.random.default_rng(4242)
        e = rng.normal(0, g, size=n)
        synth = V[legit[0]]["A2"] + (e - e.mean())
        per = {a: [lo(V[a]["A2"], V[legit[0]]["A2"], s) - lo(V[a]["A2"], synth, s) for s in SEEDS]
               for a in names}
        d0 = {a: per[a][0] for a in names}
        spr = {a: max(per[a]) - min(per[a]) for a in names}
        pos = [a for a in names if d0[a] > 1e-9]
        neg = [a for a in names if d0[a] < -1e-9]
        minority = pos if len(pos) <= len(neg) else neg
        res = [a for a in minority if abs(d0[a]) > 3 * max(spr[a], 1e-12)]
        sign_ctrl[g] = {"pos": len(pos), "neg": len(neg), "zero": len(names) - len(pos) - len(neg),
                        "resolved_minority": len(res)}
        note = ("   <- g=0: the synthetic IS `generic`, so every sign must VANISH" if g == 0 else
                f"   <- resolved minority must be 0 (raw minority {len(minority)} is noise)")
        print(f"     noise g={g:<5} +{len(pos):>4}  −{len(neg):>4}  0:{sign_ctrl[g]['zero']:>4}"
              f"  resolved-minority {sign_ctrl[g]['resolved_minority']:>3}{note}")
    g0_ok = sign_ctrl[0.0]["zero"] == len(names)
    uni_ok = all(sign_ctrl[g]["resolved_minority"] == 0 for g in (0.05, 0.20))
    print(f"     g=0 vanishes: {'PASS' if g0_ok else '⛔ FAIL'} · planted uniformity detected by the "
          f"KILL's own rule: {'PASS' if uni_ok else '⛔ FAIL'}")
    print( "     ⚠ scored by the kill's rule, not by strict one-sidedness — the first version demanded")
    print( "       97/0 at a small dose, which the design cannot return, and failed for its own reasons.")

    # ---------- PLACEBO ----------
    plac = max(abs(lo(V[a]["A2"], V[legit[0]]["A2"], SEEDS[0])
                   - lo(V[a]["A2"], V[legit[0]]["A2"], SEEDS[0])) for a in names)
    plac_ok = plac == 0.0
    print(f"  PLACEBO — lo(A,generic) − lo(A,generic) must be exactly 0 for all {len(names)} arms: "
          f"{plac:.1e} {'PASS' if plac_ok else '⛔ FAIL'}")

    if not (inv_ok and okA and okB and g0_ok and uni_ok and plac_ok):
        print("\n  a control did not fire. Exit 2, never 0.")
        return 2

    # ---------- THE SIGN TEST ----------
    print(f"\n  ⭐ THE SIGN TEST — Δlo = lo(A,generic) − lo(A,genericpool16), per arm.")
    print(f"     {'target':<14}{'+ (gen tighter)':>17}{'− (p16 tighter)':>17}"
          f"{'resolved flips':>16}{'median |Δlo|':>14}")
    # ⚠ THE COMPARATORS THEMSELVES ARE EXCLUDED FROM THE CANDIDATE SET, AND THE FIRST RUN DID NOT
    #   EXCLUDE THEM. `lo(generic, generic)` is identically 0 by construction, so `generic` appeared
    #   as a "resolved sign flip" that is nothing but the degenerate diagonal. A candidate compared
    #   against itself is not evidence about a quantifier ranging over candidates.
    # ⚠ AND THE EXCLUSION IS COMPUTED, NOT HAND-PICKED. The first run flagged `generic` (a
    #   comparator) and then `generic_reprov`, whose paired sd against `generic` is EXACTLY 0 on
    #   A1·consensus — it IS `generic` on that target under another name. Both are the degenerate
    #   diagonal, and both would have been reported as evidence that `every` is irreducible.
    #   RULE: an arm is not a candidate against comparator C on target T if its paired sd against C
    #   is exactly 0 there, because lo is then identically 0 by construction.
    rows, verdicts, excluded = [], {}, {}
    for tn in TARGETS:
        dup = sorted({a for a in names for c in legit
                      if float((V[a][tn] - V[c][tn]).std()) == 0.0})
        cand = [a for a in names if a not in legit and a not in dup]
        excluded[tn] = {"comparators": sorted(legit),
                        "exact_duplicates_of_a_comparator": [d for d in dup if d not in legit]}
        print(f"     {tn:<14}candidates {len(cand)}  (excluded: {len(legit)} comparators + "
              f"{len([d for d in dup if d not in legit])} exact duplicate(s) "
              f"{[d for d in dup if d not in legit]})")
        d0 = {a: LO[(a, legit[0], tn, SEEDS[0])] - LO[(a, legit[1], tn, SEEDS[0])] for a in cand}
        spread = {a: max(LO[(a, legit[0], tn, s)] - LO[(a, legit[1], tn, s)] for s in SEEDS)
                     - min(LO[(a, legit[0], tn, s)] - LO[(a, legit[1], tn, s)] for s in SEEDS)
                  for a in cand}
        pos = [a for a in cand if d0[a] > 0]
        neg = [a for a in cand if d0[a] < 0]
        minority = pos if len(pos) <= len(neg) else neg
        resolved = [a for a in minority if abs(d0[a]) > 3 * max(spread[a], 1e-12)]
        stable = all(
            (LO[(a, legit[0], tn, s)] - LO[(a, legit[1], tn, s)] > 0) == (d0[a] > 0)
            for a in resolved for s in SEEDS)
        verdicts[tn] = {"pos": len(pos), "neg": len(neg), "resolved_flips": sorted(resolved),
                        "seed_stable": bool(stable), "n_cand": len(cand),
                        "binding_comparator": legit[0] if len(neg) >= len(pos) else legit[1]}
        rows.append({"target": tn, "n_cand": len(cand),
                     "excluded": excluded[tn], "n_pos": len(pos), "n_neg": len(neg),
                     "binding_comparator": legit[0] if len(neg) >= len(pos) else legit[1],
                     "minority_size": len(minority), "resolved": sorted(resolved),
                     "median_abs_dlo": float(np.median([abs(v) for v in d0.values()])),
                     "median_seed_spread": float(np.median(list(spread.values()))),
                     "seed_stable": bool(stable)})
        print(f"     {tn:<14}{len(pos):>17}{len(neg):>17}{len(resolved):>16}"
              f"{np.median([abs(v) for v in d0.values()]):>14.5f}")
        if resolved:
            print(f"       resolved minority-sign arms: {sorted(resolved)[:8]}"
                  f"{' …' if len(resolved) > 8 else ''}  seed-stable: {stable}")
            # ⭐ MECHANISM — a tight interval against a comparator means a SMALL PAIRED SD against
            #   it, i.e. the arm is a near-duplicate of that comparator. Measure it, do not assume.
            print(f"       {'arm':<18}{'sd vs gen':>11}{'sd vs p16':>11}{'ratio':>8}"
                  f"{'median arm sd vs gen':>23}")
            med = float(np.median([float((V[a][tn] - V[legit[0]][tn]).std()) for a in cand]))
            for a in sorted(resolved):
                s0 = float((V[a][tn] - V[legit[0]][tn]).std())
                s1 = float((V[a][tn] - V[legit[1]][tn]).std())
                print(f"       {a:<18}{s0:>11.4f}{s1:>11.4f}{s0/max(s1,1e-12):>8.3f}{med:>23.4f}")
            print( "       (a flip is produced by an arm being a NEAR-DUPLICATE of one comparator:")
            print( "        its paired sd against that comparator collapses, so its bound tightens.)")
        print(f"       median per-arm seed spread of Δlo: "
              f"{np.median(list(spread.values())):.5f}  (the resolution floor)")

    nres = sum(len(v["resolved_flips"]) for v in verdicts.values())
    binding = {v["binding_comparator"] for v in verdicts.values()}
    print()
    if nres >= 1:
        world = (f"⭐ B `every` IS IRREDUCIBLE — {nres} arm(s) across the two targets have a RESOLVED "
                 f"minority sign (|Δlo| > 3× that arm's own seed spread), so neither comparator is "
                 f"uniformly tighter and no single one reproduces the conjunction. The universal "
                 f"quantifier stays.")
    else:
        world = (f"⭐ A `every` IS A SHORTHAND — no candidate arm has a resolved minority sign on "
                 f"either target, so one comparator is uniformly the BINDING one and "
                 f"min-over-comparators always selects it: {sorted(binding)}. On this release clause "
                 f"②′ reduces to `resolvably beats {sorted(binding)[0]}`, and the second member of "
                 f"the certified set never binds.")
    print(world)
    print("⛔ AND WHAT `every` CAN MEAN HERE IS BOUNDED BY ALGEBRA, NOT BY THIS MEASUREMENT: R921's")
    print("   committed derivation makes the point-estimate ordering comparator-invariant, so the")
    print("   quantifier's ENTIRE content is which comparator gives the tighter interval. Whatever")
    print("   the sign test returns, `every comparator` can never encode a difference in WHICH ARM")
    print("   IS BETTER — only in how confidently that is known.")
    print("⚠ AND THE SET IS A CHOICE, WHICH THE CLAUSE DOES NOT SAY. R921 certified 2 comparators")
    print("   from a larger pool; the quantifier inherits its strength from that certification, and")
    print("   testing it over comparators never scored costs 15,488 judge calls each (R914).")

    out = HERE / "results" / "quantifier_work.json"
    out.write_text(json.dumps({
        "round": "R1025", "seeds": list(SEEDS), "nboot": NBOOT, "n_arms": len(names),
        "prior_art": {"source": "R921 comparator_sweep.json",
                      "survives_all": len(want_all), "at_least_one": len(want_one),
                      "disagreement_arms": sorted(want_one - want_all),
                      "note": "read from a committed artifact, not re-derived; a lookup cannot fail"},
        "derivation_point_estimate_invariant": {"span": inv_span, "holds": bool(inv_ok)},
        "positive_reproduced_r921": {"all": bool(okA), "at_least_one": bool(okB)},
        "sign_detection_control": {str(k): v for k, v in sign_ctrl.items()},
        "placebo_max_abs": plac, "rows": rows,
        "binding_comparator": sorted(binding), "n_resolved_flips": nres, "world": world,
        "limitation": "whether the CERTIFIED SET is the right set is untested here; R921 certified "
                      "2 from a larger pool and a new comparator costs 15,488 judge calls",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
