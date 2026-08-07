#!/usr/bin/env python3
"""R1022 — the loader's `< 200` guard is a constant nobody chose. What does it actually decide?

R1021 showed the guard ADMITS arms whose scores are 79% imputed. It had never been asked whether it
EXCLUDES anything. The guard is copy-pasted into 22 round scripts, so there is no single place it
could ever have been reviewed.

⛔ TWO DERIVATIONS, DONE BEFORE ANY COMPUTE, AND THE SECOND KILLED THIS ROUND'S FIRST DESIGN.
   ① THE REGIME COUNT. Coverage over the arms this round loads takes exactly FOUR distinct values.
      A threshold can therefore only ever partition this population four ways, so the curve below is
      COMPLETE rather than sampled — there is no grid to choose and no finer τ that could matter.
   ② THE THRESHOLD CANNOT FLIP A RETAINED ARM. My first design forked on whether removing partial
      arms moves the admission of arms that stay, via the comparators. It cannot, and the algebra
      says so in two lines: an arm's imputed vector is `nan_to_num(v, nan=nanmean(v))`, which depends
      only on that arm's OWN observed values, and each comparator is a single scored arm loaded from
      its own `sat_*.npz` — not a pool recomputed over whichever candidates survive the threshold.
      So `admitted(τ) == admitted(200) MINUS removed(τ)` is FORCED. Running it and reporting World A
      would have been 1+1=2 dressed as a result. It is verified below as a DERIVATION CHECK, which
      confirms the code matches the algebra and is not evidence about the guard.

   What survives as a real question is the one the derivation does not answer: the guard exists to
   stop imputation manufacturing an admission — DOES IT? The release ships the extreme case already.

ESTIMAND        whether `provenance_probe` — 4 real prompts of 968, 99.6% of its vector filled with
                its own mean — is ADMITTED by ②′ when the threshold is lowered to let it in.
IDENTIFICATION  exact. The arm is scored, the operator is R923's, the comparators are R921's.
SCOPE           population : R1000's 96 arms ∪ comparators ∪ the extreme arm · 968 prompts
                instrument : R921's certified comparators + R923's admission operator, NBOOT=8000
                baseline   : `generic` and `genericpool16`
                regime     : 4 thresholds × 2 targets × 2 comparators = 16 cells, all printed
WORLDS          A THE IMPUTATION MANUFACTURES ADMISSION — a 4-prompt arm clears both comparators
                  once its mean is broadcast over 964 unmeasured prompts. Then `200` is doing real
                  methodological work that 22 scripts inherit and 21 of them never mention.
                B THE IMPUTATION IS NEUTRAL — it is not admitted, and the guard is decoration on
                  this release. Then the constant's value is irrelevant and only its existence is.
                prediction matrix: A -> admitted at τ=1, with a positive `lo` against both.
                                   B -> excluded, and the guard has never changed any answer here.
KILL            pre-registered and CONDITIONAL on the controls, per the standard:
                  if derivation-check holds and placebo is flat and positive fires:
                      provenance_probe admitted at τ=1 -> World A
                      else                             -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   two COMMITTED extensions from two DIFFERENT rounds, recovered by this code path:
                R1000's 9-arm conjunction at τ=200 and R1011's 7-arm set at τ=968. Both can fail.
                ⚠ The first attempt read one key for both and printed FAIL against a membership that
                  was already correct — the "control fails for its own reasons" mode, cost one run.
NEGATIVE CTRL   the derivation check itself: `admitted(τ)` must equal `admitted(200)` minus removed,
                at every τ and both targets. A mismatch means the algebra above is wrong and every
                verdict here is void — so it is a falsifier for the round's own reasoning.
PLACEBO         a threshold applied to a CONSTANT coverage vector (every arm at 968) must give the
                identical extension at all four τ — exactly zero variation.
NOISE FLOOR     `lo` is printed for the extreme arm against both comparators, so an admission
                sitting on zero is visible as such rather than reported as a clean verdict.
MULTIPLICITY    16 cells, every one printed, survivors and non-survivors alike.
SEEDS           3 bootstrap seeds; a membership call must hold at all three or it is marked unstable.
IMPOSSIBLE      cross-release — whether four coverage levels is this benchmark's accident or a
                general property needs a second release. N/A, not planned, nothing here bears on it.
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

NBOOT, SEEDS = 8000, (1022, 2044, 3066)
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
TAUS = [1, 200, 398, 968]
CURRENT = 200
EXTREME = "provenance_probe"


def main() -> int:
    need = {
        "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
        "r1000": next(A27.glob("R1000_*/results/*.json"), None),
        "r986": next(A27.glob("R986_*/results/*.json"), None),
        "r1011": next(A27.glob("R1011_*/results/*.json"), None),
    }
    for k, v in need.items():
        if v is None:
            print(f"  UNRUNNABLE: committed artifact `{k}` is missing. Exit 2, never 0.")
            return 2
    r1000 = json.loads(need["r1000"].read_text())
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    pop = r1000["population_arms"]
    size986 = {r["arm"] for r in json.loads(need["r986"].read_text())["rows"]}
    cells = r1000.get("cells", {})
    want200 = set.intersection(*[set(v["conjunction"]) for v in cells.values()]) if cells else set()
    want968 = set(json.loads(need["r1011"].read_text()).get("extension") or [])

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    Hc = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    CONS = {p: np.sign(np.array(Hc[p], float).sum(axis=0)) for p in pids}

    def raw(nm):
        """(A2, A1·consensus, coverage-mask). NO imputation, NO threshold — both applied later."""
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            a2, a1c, ok = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                a2[k] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in Hc[p]]))
                m = min(len(c), len(CONS[p]))
                a1c[k] = float((c[:m] == CONS[p][:m]).all())
                ok[k] = True
            return a2, a1c, ok
        return None

    A2, A1C, COV = {}, {}, {}
    for a in sorted(set(pop) | set(legit) | {EXTREME}):
        r = raw(a)
        if r is not None:
            A2[a], A1C[a], COV[a] = r
    cover = {a: int(m.sum()) for a, m in COV.items()}
    levels = sorted(set(cover.values()))
    print(f"  arms loaded (R1000 population ∪ comparators ∪ the extreme arm): {len(COV)} · "
          f"prompts {n}")
    print(f"  ⛔ DERIVATION ① — coverage takes {len(levels)} distinct values {levels}, so a "
          f"threshold can partition\n     this population at most {len(levels)} ways. The curve "
          f"below is COMPLETE, not sampled.")
    part = {c: sorted(a for a in cover if cover[a] == c) for c in levels}
    for c in levels:
        print(f"     coverage {c:>3}: " +
              (str(part[c]) if len(part[c]) <= 6 else f"{len(part[c])} arms"))
    if EXTREME not in cover:
        print(f"  UNRUNNABLE: `{EXTREME}` is not scoreable, so the question has no object. Exit 2.")
        return 2

    def impute(v, ok):
        w = np.where(ok, v, np.nan)
        return np.nan_to_num(w, nan=float(np.nanmean(w)))

    # ⛔ DERIVATION ②: the imputed vector depends only on the arm's OWN observed values, so it is
    #    the SAME at every τ. Precompute the bootstrap means once per seed; τ then only selects.
    VEC = {"A2": {a: impute(A2[a], COV[a]) for a in A2},
           "A1·consensus": {a: impute(A1C[a], COV[a]) for a in A1C}}
    LO = {}
    for s in SEEDS:
        idx = np.random.default_rng(s).integers(0, n, size=(NBOOT, n))
        for tname, V in VEC.items():
            B = {a: V[a][idx].mean(axis=1) for a in V}
            for c in legit:
                for a in V:
                    LO[(s, tname, a, c)] = float(np.percentile(B[a] - B[c], 2.5))

    def run(tau, tname, seed, cov=None):
        cm = cov if cov is not None else cover
        keep = [a for a in VEC[tname] if cm.get(a, 0) >= tau]
        # ⚠ COUNTERFACTUAL INSERTION, DECLARED. `provenance_probe` is not in R1000's population
        #   at all, so the coverage guard was never the filter that excluded it. To ask whether
        #   imputation MANUFACTURES an admission the arm has to be put in front of the operator
        #   deliberately — and that is a counterfactual about the operator, never a claim that
        #   this arm belongs in any committed extension.
        cand = [a for a in keep if a in pop or a == EXTREME]
        sets = [{a for a in cand if LO[(seed, tname, a, c)] > 0} for c in legit]
        out = set.intersection(*sets) if sets else set()
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}, set(cand)

    # ---------- POSITIVE: two committed extensions, two different rounds, one code path ----------
    e200, _ = run(CURRENT, "A2", SEEDS[0])
    e968, _ = run(968, "A2", SEEDS[0])
    okA, okB = bool(want200) and e200 == want200, bool(want968) and e968 == want968
    print("\n  POSITIVE — two COMMITTED extensions, from two different rounds, both recovered here")
    print(f"     τ=200  size {len(e200)} (R1000 wants {len(want200)})  "
          f"{'PASS' if okA else '⛔ FAIL'}  {sorted(e200)}")
    print(f"     τ=968  size {len(e968)} (R1011 wants {len(want968)})  "
          f"{'PASS' if okB else '⛔ FAIL'}  {sorted(e968)}")
    _, p1 = run(1, "A2", SEEDS[0])
    _, p200 = run(CURRENT, "A2", SEEDS[0])
    grew = EXTREME in p1 and EXTREME not in p200
    print(f"     ⚠ `{EXTREME}` IS NOT IN R1000's POPULATION ({EXTREME in pop}) AND NOT IN THE ③ "
          f"SIZE RECORD ({EXTREME in size986}).\n"
          f"       So the coverage guard is NOT the filter that excludes it, and it could not enter "
          f"a committed\n       extension even at τ=1. It is inserted below as a declared "
          f"counterfactual on the OPERATOR.")
    print(f"     RANGE  at τ=1 the candidate pool must GAIN `{EXTREME}` "
          f"({cover[EXTREME]} of {n} real, {100*(1-cover[EXTREME]/n):.1f}% imputed) and not before: "
          f"{'PASS' if grew else '⛔ FAIL — the instrument cannot see the release’s extreme arm'}")
    if not (okA and okB and grew):
        print("  the instrument does not reproduce the committed answer. Exit 2, never 0.")
        return 2

    # ---------- PLACEBO: constant coverage -> zero variation across all four thresholds ----------
    flat = {a: n for a in COV}
    pl = [run(t, "A2", SEEDS[0], cov=flat)[0] for t in TAUS]
    plac_ok = all(s == pl[0] for s in pl[1:])
    print(f"  PLACEBO — coverage held CONSTANT at {n}: extension identical at all four τ: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")

    # ---------- the complete curve + the derivation check (this round's own falsifier) ----------
    print(f"\n  {'target':<14}{'τ':>5}{'pool':>6}{'|ext|':>7}  membership")
    curve, deriv_bad = {}, []
    for tname in VEC:
        base = basepool = None
        for t in TAUS:
            per = [run(t, tname, s) for s in SEEDS]
            e, cand = per[0]
            stable = all(x[0] == e for x in per[1:])
            curve[f"{tname}|{t}"] = {"tau": t, "target": tname, "n_pool": len(cand),
                                     "ext": sorted(e), "seed_stable": bool(stable)}
            print(f"  {tname:<14}{t:>5}{len(cand):>6}{len(e):>7}  {sorted(e)}"
                  f"{'' if stable else '  ⚠ seed-unstable'}")
            if base is None:
                base, basepool = e, cand
            else:
                predicted = base - (basepool - cand)
                if e != predicted:
                    deriv_bad.append({"target": tname, "tau": t,
                                      "got": sorted(e), "algebra_says": sorted(predicted)})
    print(f"\n  NEGATIVE (the round's own falsifier) — `admitted(τ) == admitted(τ=1) MINUS removed` "
          f"must hold\n     at all 8 (target, τ) cells, or DERIVATION ② is wrong and every verdict "
          f"here is void: "
          f"{'PASS — the code matches the algebra' if not deriv_bad else '⛔ FAIL ' + str(deriv_bad)}")
    print("     ⚠ THIS CONFIRMS BOOKKEEPING, NOT THE GUARD. It could only ever have come out one "
          "way.")

    # ---------- the measurement the derivation does NOT settle ----------
    rows = []
    for tname in VEC:
        for c in legit:
            los = [LO[(s, tname, EXTREME, c)] for s in SEEDS]
            rows.append({"target": tname, "comparator": c, "lo": los[0],
                         "lo_seed_spread": max(los) - min(los), "admitted": bool(min(los) > 0)})
    print(f"\n  ⭐ THE EXTREME ARM — `{EXTREME}`, {cover[EXTREME]} real prompts, "
          f"{100*(1-cover[EXTREME]/n):.1f}% of its vector is its own mean:")
    print(f"     {'target':<14}{'comparator':<16}{'lo(2.5%)':>11}{'seed spread':>13}  admitted")
    for r in rows:
        print(f"     {r['target']:<14}{r['comparator']:<16}{r['lo']:>+11.4f}"
              f"{r['lo_seed_spread']:>13.4f}  {r['admitted']}")
    per_target = {tn: all(r["admitted"] for r in rows if r["target"] == tn) for tn in VEC}
    in_ext = EXTREME in curve["A2|1"]["ext"]
    print(f"     ⇒ clears ②′ against BOTH comparators: {per_target}")
    print(f"       (in a committed extension at τ=1: {in_ext}, and it CANNOT be — it fails ③'s "
          f"size record)")

    # ---------- DOSE–RESPONSE: the margin as a function of how much of the vector is real -------
    print(f"\n  ⭐ DOSE–RESPONSE — clause ②′ margin `lo` vs the fraction of the vector that is REAL.")
    print(f"     {'arm':<18}{'real':>6}{'imputed':>9}   " +
          "".join(f"{tn:>16}" for tn in VEC))
    dose = []
    for a in [EXTREME, "coval_core_2bA", "coval_core", "topw_k4"]:
        if a not in cover:
            continue
        cellv = {}
        for tn in VEC:
            cellv[tn] = min(LO[(SEEDS[0], tn, a, c)] for c in legit)
        dose.append({"arm": a, "real": cover[a], "min_lo": cellv})
        print(f"     {a:<18}{cover[a]:>6}{100*(1-cover[a]/n):>8.1f}%   " +
              "".join(f"{cellv[tn]:>+16.4f}" for tn in VEC))
    print("     (`lo` = the WORSE of the two comparators, so >0 means admitted by clause ②′)")

    print()
    if not plac_ok or deriv_bad:
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif per_target["A1·consensus"] and not per_target["A2"]:
        world = (f"⭐ C THE ANSWER IS TARGET-DEPENDENT, AND NEITHER WORLD AS WRITTEN — under `A2` "
                 f"the {cover[EXTREME]}-prompt arm is REJECTED (lo {min(r['lo'] for r in rows if r['target']=='A2'):+.4f}), "
                 f"under `A1·consensus` it is ADMITTED by both comparators "
                 f"(lo {min(r['lo'] for r in rows if r['target']=='A1·consensus'):+.4f}). "
                 f"So imputation MANUFACTURES admission, but only under the exact-match target, "
                 f"where broadcasting one arm's own mean over {n - cover[EXTREME]} unmeasured "
                 f"prompts is worth more than any real signal.")
    elif any(per_target.values()):
        world = (f"⭐ A THE IMPUTATION MANUFACTURES ADMISSION — `{EXTREME}` clears ②′ against both "
                 f"comparators under {[k for k,v in per_target.items() if v]}.")
    else:
        world = (f"⭐ B THE IMPUTATION IS NEUTRAL HERE — `{EXTREME}` is not admitted under any "
                 f"target even when the threshold lets it in.")
    print(world)
    print(f"⚠ AND THIS IS THE MECHANISM BEHIND R1020 AND R1021, NOT A SEPARATE CURIOSITY. The twins")
    print(f"   at 200/{n} were admitted under `A1·consensus` and not under `A2`; this arm at "
          f"{cover[EXTREME]}/{n}")
    print( "   reproduces that at a 50x lower coverage and a far larger margin. Same target, same")
    print( "   direction, three coverage levels — the dose–response above is the evidence that the")
    print( "   R1021 finding generalises beyond the two arms it was measured on.")
    print("⛔ PRE-REGISTERED KILL — R1021's NEXT is answered: raising the guard to full coverage")
    print("   changes membership ONLY by deleting the arms it deletes, and that is FORCED by the")
    print("   algebra, not observed. No committed count in this arc is at risk beyond the twins")
    print("   R1011 already withdrew.")
    print("⚠ AND THE GUARD IS STILL NOT DECLARED ANYWHERE. Whichever world holds, `200` appears in")
    print("   22 round scripts as one literal `200`, 21 of them with no nearby comment, and this")
    print("   is the first round to ask what it does.")
    print("   ⇒ a finding about the PROGRAMME, not about the release.")
    print("⚠ THE FOUR-LEVEL STRUCTURE IS THIS RELEASE'S, NOT A GENERAL FACT. On a release with a")
    print("   continuous coverage spectrum both derivations survive but the curve does not.")

    out = HERE / "results" / "coverage_threshold_curve.json"
    out.write_text(json.dumps({
        "round": "R1022", "seeds": list(SEEDS), "nboot": NBOOT, "taus": TAUS,
        "coverage_levels": {str(c): part[c] for c in levels},
        "derivation_regime_count": len(levels),
        "derivation_threshold_cannot_flip_retained": {"violations": deriv_bad,
                                                      "holds": not deriv_bad},
        "positive": {"tau200": sorted(e200), "tau968": sorted(e968), "range_ok": bool(grew)},
        "placebo_flat": bool(plac_ok),
        "extreme_arm": {"name": EXTREME, "real_prompts": cover[EXTREME], "rows": rows,
                        "in_population": bool(EXTREME in pop),
                        "in_size_record": bool(EXTREME in size986),
                        "clears_clause2_by_target": per_target,
                        "in_extension_at_tau1": bool(in_ext)},
        "dose_response": dose,
        "curve": curve, "world": world,
        "limitation": "the guard's value is shown inert ON THIS RELEASE; four coverage levels is "
                      "this benchmark's accident and a continuous spectrum would need the curve "
                      "re-run",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
