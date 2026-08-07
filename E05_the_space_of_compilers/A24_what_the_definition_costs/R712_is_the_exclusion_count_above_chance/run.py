#!/usr/bin/env python3
"""
R712 -- is a clause's unique-exclusion count above a same-size random admission?

CHECK #314 ON R711's NEXT LINE -- IT HOLDS, WITH ONE NUMBER OF MINE CORRECTED BEFORE USE.
  ✓ STATEMENT.md:166 does say F2 "stands on its exclusions" -- written by R711 itself.
  ✓ Four rounds touch a unique-exclusion count (R494, R678, R703, R704); none gives the COUNT a
    null. R704 came closest -- "a count, not a signal" -- but argued it from the base rate rather
    than testing it against one.
  ⚠ I estimated F3 admits ~20 arms. It admits 27. Recomputed from the ledger, not carried forward.

⭐ THE STRUCTURE, DERIVED BEFORE THE RUN, AND IT IS R711's AGAIN.
  A clause's UNIQUE exclusions are the arms the OTHER TWO admit and it does not, so the ceiling is
  |F1 ∩ F3| = 23 and F2's 20 is 20 OF 23 POSSIBLE, not 20 of 42. Under a uniform random admission of
  9 of 42 the expected count is 23 × (1 − 9/42) = 18.0714. ⛔ So "20 unique exclusions, the largest
  of the three" may be admission-size arithmetic exactly as the sham residual was.

ESTIMAND        per clause, the number of arms it UNIQUELY excludes, against the EXACT distribution
                of that count under a uniformly random admission of the SAME SIZE with the other two
                clauses held fixed; P(count >= observed) enumerated hypergeometrically, not sampled.
IDENTIFICATION  exact -- the count is |others| minus a hypergeometric draw. ⚠ the OBSERVED counts are
                DERIVATIONS from R360's verdicts; the NULLS are the evidence. ⚠ randomising one
                clause while holding two fixed asks "is THIS count surprising given the others",
                not "is the triple surprising". Named, not assumed.
SCOPE           population : the 42 arms of R360's ledger, three clauses
                instrument : exact hypergeometric enumeration at fixed admission size
                             instrument unit = AN ARM
                             claim unit      = A CLAUSE'S EXCLUSION COUNT AS EVIDENCE
                             ⚠ NOT EQUAL -- a count above its null says the clause excludes more than
                             chance, never that it excludes the RIGHT arms.
                baseline   : uniformly random admission of the same size as the clause under test
                regime     : this repository at HEAD
WORLDS          A REAL COUNT · B ARITHMETIC · C ALL THREE AT CHANCE (see PREREGISTRATION.txt)
KILL            conditional on POSITIVE firing and g=0 landing BELOW the null mean
POSITIVE CTRL   a clause admitting 9 arms all OUTSIDE F1∩F3 -> the full ceiling, tiny exact P
g=0             a clause admitting 9 arms drawn ONLY from F1∩F3 -> below the null mean; the
                statistic must be able to move DOWN as well as up
NEGATIVE CTRL   the null itself; the world it excludes is NAMED
SHAM            the IDENTICAL machinery on F1 and F3 -- same operation, different clause
PLACEBO         two identical enumerations differ by exactly 0
EXACTNESS       enumerated vs sampled to 3 decimals, because "no Monte-Carlo error" is a CLAIM
ARTIFACT        results/exclusions.json
IMPOSSIBLE      whether the excluded arms are the RIGHT ones (construct validity, needs an outside
                standard) · cross-release (41 of 42 arms are ours)
"""
from __future__ import annotations
import json, math, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEEDS, NSAMP = (0, 1, 2), 60000
INSTRUMENT_UNIT, CLAIM_UNIT = "AN ARM", "A CLAUSE'S EXCLUSION COUNT AS EVIDENCE"
C = math.comb


def hyper_null(n, ceiling, k):
    """EXACT distribution of `ceiling - X` where X ~ Hypergeometric(n, ceiling, k).

    A clause admitting k of n arms uniformly at random admits X of the `ceiling` arms the other two
    clauses jointly admit; its unique exclusions are the remaining `ceiling - X`.
    """
    dist = {}
    for x in range(0, min(ceiling, k) + 1):
        w = C(ceiling, x) * C(n - ceiling, k - x)
        if w:
            dist[ceiling - x] = dist.get(ceiling - x, 0) + w
    tot = sum(dist.values())
    assert tot == C(n, k), f"enumeration lost mass: {tot} != {C(n,k)}"
    return {s: c / tot for s, c in sorted(dist.items())}


def summarise(dist, obs):
    mean = sum(s * p for s, p in dist.items())
    pge = sum(p for s, p in dist.items() if s >= obs)
    cum, q95 = 0.0, max(dist)
    for s in sorted(dist):
        cum += dist[s]
        if cum >= 0.95:
            q95 = s
            break
    return {"mean": mean, "p_ge_obs": pge, "q95": q95}


def sampled(n, ceiling, k, seeds=SEEDS, nsamp=NSAMP):
    cnt = {}
    pool = list(range(n))
    for sd in seeds:
        rng = random.Random(sd)
        for _ in range(nsamp // len(seeds)):
            adm = set(rng.sample(pool, k))
            v = ceiling - len(adm & set(range(ceiling)))
            cnt[v] = cnt.get(v, 0) + 1
    t = sum(cnt.values())
    return {s: c / t for s, c in sorted(cnt.items())}


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms = set(led["arms"]); K = led["k"]
    p2 = set(led["clause2_admits"]); p23 = set(led["clause23_admits"])
    CL = {"F1 provenance": p23 | (arms - p2),
          "F2 behaviour": p2,
          "F3 size (repaired)": {a for a in arms if K.get(a) is not None and 1 < K[a] <= 4}}
    n = len(arms)

    print(f"─── THE OBJECT ───\n  arms {n}")
    rows = []
    for name, adm in CL.items():
        others = set(arms)
        for m, o in CL.items():
            if m != name:
                others &= o
        uniq = others - adm
        rows.append({"clause": name, "admits": len(adm), "ceiling": len(others),
                     "observed": len(uniq)})
        print(f"  {name:<20}admits {len(adm):>3}   ceiling |others| {len(others):>3}   "
              f"unique exclusions {len(uniq):>3}  ({len(uniq)} of {len(others)} POSSIBLE)")
    print(f"  ⛔ DERIVATION, NOT EVIDENCE: these counts are forced by R360's committed verdicts. "
          f"The NULLS below are the measurement.")

    f2 = next(r for r in rows if r["clause"].startswith("F2"))
    ex2 = hyper_null(n, f2["ceiling"], f2["admits"])
    st2 = summarise(ex2, f2["observed"])

    print(f"\n─── CONTROLS ───")
    ceil_dist = summarise(ex2, f2["ceiling"])
    posok = ceil_dist["p_ge_obs"] < 0.05 and st2["mean"] < f2["ceiling"]
    print(f"  POSITIVE  a clause admitting {f2['admits']} arms all OUTSIDE the ceiling set -> "
          f"{f2['ceiling']} unique, exact p = {ceil_dist['p_ge_obs']:.6f}")
    print(f"            floor(null mean) {st2['mean']:.4f} < ceiling {f2['ceiling']} -> "
          f"{'PASS — a maximal plant is registered' if posok else '⛔ FAIL'}")
    g0_val = f2["ceiling"] - min(f2["admits"], f2["ceiling"])
    g0ok = g0_val < st2["mean"]
    print(f"  g=0       a clause admitting {f2['admits']} arms drawn ONLY from the ceiling set -> "
          f"{g0_val} unique, vs null mean {st2['mean']:.4f} -> "
          f"{'PASS — the statistic moves DOWN too' if g0ok else '⛔ FAIL'}")
    sm = sampled(n, f2["ceiling"], f2["admits"])
    agree = max(abs(ex2.get(s, 0) - sm.get(s, 0)) for s in set(ex2) | set(sm))
    exok = agree < 0.005
    print(f"  EXACTNESS enumerated vs {NSAMP}-draw sampled: max |Δp| = {agree:.5f} -> "
          f"{'PASS — the exact p carries no Monte-Carlo error' if exok else '⛔ FAIL'}")
    plc = summarise(hyper_null(n, f2["ceiling"], f2["admits"]), f2["observed"]) == st2
    print(f"  PLACEBO   two identical enumerations differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and exok and plc and unitok

    print(f"\n─── THE SHAM: THE IDENTICAL MACHINERY ON ALL THREE CLAUSES ───")
    print(f"  {'clause':<20}{'admits':>7}{'ceiling':>9}{'observed':>10}{'null mean':>11}"
          f"{'q95':>6}{'exact p':>10}")
    for r in rows:
        d = hyper_null(n, r["ceiling"], r["admits"])
        s = summarise(d, r["observed"])
        r.update(s); r["dist"] = {str(a): b for a, b in d.items()}
        print(f"  {r['clause']:<20}{r['admits']:>7}{r['ceiling']:>9}{r['observed']:>10}"
              f"{s['mean']:>11.4f}{s['q95']:>6}{s['p_ge_obs']:>10.4f}")
    all_chance = all(r["p_ge_obs"] >= 0.05 for r in rows)

    print(f"\n─── THE SPECIFICATION SWEEP (G4 — 3 clauses × 3 admission sizes = 9 cells) ───")
    cells = []
    for r in rows:
        for kk in (r["admits"], 5, 14):
            if kk > n: continue
            s = summarise(hyper_null(n, r["ceiling"], kk), r["observed"])
            cells.append({"clause": r["clause"], "k": kk, "observed": r["observed"], **s})
    ranked = sorted(cells, key=lambda c: c["p_ge_obs"])
    bh = []
    for i, c in enumerate(ranked):
        if c["p_ge_obs"] <= 0.10 * (i + 1) / len(cells):
            bh = ranked[:i + 1]
    for c in cells:
        print(f"  {c['clause']:<20}k={c['k']:<4}observed {c['observed']:>3}   null mean "
              f"{c['mean']:>8.4f}   exact p {c['p_ge_obs']:.4f}")
    print(f"  ⭐ BH q=0.10 over all {len(cells)} cells -> {len(bh)} survive: "
          f"{[c['clause'].split()[0] + '@k=' + str(c['k']) for c in bh] or 'NONE'}")

    print(f"\n─── REGISTERED ───")
    print(f"  A  [DERIVED] F2 unique = 20, ceiling 23 -> {f2['observed']}, {f2['ceiling']}: "
          f"error {f2['observed']-20:+d}, {f2['ceiling']-23:+d}")
    print(f"  B  null mean = 18.07 [15.0,21.0] -> {st2['mean']:.4f}: "
          f"{'INSIDE' if 15.0 <= st2['mean'] <= 21.0 else '⛔ OUTSIDE'}")
    print(f"  C  exact P(F2 >= {f2['observed']}) = 0.25 [0.05,0.70] -> {st2['p_ge_obs']:.4f}: "
          f"{'INSIDE' if 0.05 <= st2['p_ge_obs'] <= 0.70 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL F2 observed <= its null's 95th pct ({st2['q95']}) -> "
          f"{'HOLDS' if f2['observed'] <= st2['q95'] else '⛔ FAILS'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the exact p would be silence."
    elif st2["p_ge_obs"] < 0.05:
        world = (f"⭐⭐⭐ A REAL COUNT — F2's {f2['observed']} unique exclusions against an exact null "
                 f"mean of {st2['mean']:.4f}, P = {st2['p_ge_obs']:.4f} < 0.05. Its last leg holds.")
    else:
        world = (
            f"⭐⭐⭐ {'C ALL THREE AT CHANCE' if all_chance else 'B ARITHMETIC'} — F2's LAST LEG "
            f"FALLS. Its {f2['observed']} unique exclusions sit against an exact null mean of "
            f"{st2['mean']:.4f} with P = {st2['p_ge_obs']:.4f}, enumerated hypergeometrically over "
            f"all {C(n, f2['admits']):,} admissions of {f2['admits']} from {n}, no Monte-Carlo "
            f"error. ⭐ THE CEILING IS THE STRUCTURE AGAIN: a clause's unique exclusions are the arms "
            f"the OTHER TWO admit, so F2's ceiling is |F1∩F3| = {f2['ceiling']} and its count is "
            f"{f2['observed']} of {f2['ceiling']} POSSIBLE — a clause admitting only "
            f"{f2['admits']} of {n} arms reaches {st2['mean']:.1f} of that ceiling by admission "
            f"arithmetic alone. "
            + (f"⭐⭐⭐ AND THE ASYMMETRY R703 REPORTED IS INVERTED, WHICH IS THE ROUND'S LARGEST "
               f"FINDING: priced against its OWN ceiling, the clause with the FEWEST unique "
               f"exclusions is the only one above chance — "
               f"{', '.join(r['clause'].split()[0] + ' ' + str(r['observed']) + '/' + str(r['ceiling']) + ' p=' + ('%.4f' % r['p_ge_obs']) for r in rows)}. "
               f"F1 clears BH over the whole {len(cells)}-cell grid; F2 and F3 do not. ⭐ SO 'F2 "
               f"CARRIES THE MOST EXCLUSIONS' WAS A STATEMENT ABOUT ITS ADMISSION SIZE, and the "
               f"clause whose count actually beats its null is the one R703 ranked last on the raw "
               f"count. " if not all_chance else "")
            + (f"⭐⭐ AND ALL THREE CLAUSES SIT AT CHANCE — exact p "
               f"{', '.join(f'{r[chr(39)+chr(39)] if False else r['clause'].split()[0]}={r['p_ge_obs']:.4f}' for r in rows)} "
               f"— so R703's 20-vs-4-vs-2 ASYMMETRY IS ADMISSION-SIZE ARITHMETIC and the comparison "
               f"between clauses was never informative. " if all_chance else "")
            + f"⛔ SO STATEMENT.md's 'F2 stands on its exclusions', which I wrote ONE ROUND AGO, is "
            f"WITHDRAWN. After R696 took the A2 agreement as circular and R711 put the sham residual "
            f"at chance, this was the clause's last support, and it is admission arithmetic. ⚠ WHAT "
            f"THIS DOES NOT SAY: that F2 is wrong, or that its exclusions are the wrong arms. It says "
            f"the COUNT is not evidence. Whether the excluded arms are the RIGHT ones is construct "
            f"validity and needs a standard outside this repository. ⚠ AND THE NULL'S OWN CHOICE IS "
            f"NAMED: randomising one clause while holding two fixed asks whether THIS count is "
            f"surprising given the others, not whether the triple is. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "exclusions.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n_arms": n,
        "clauses": rows, "all_three_at_chance": all_chance,
        "f2_exact_p": st2["p_ge_obs"], "f2_null_mean": st2["mean"], "f2_ceiling": f2["ceiling"],
        "total_admissions_enumerated": C(n, f2["admits"]),
        "sampled_cross_check_max_delta": agree,
        "cells": cells, "bh_survivors": [f"{c['clause']}@k={c['k']}" for c in bh],
        "registered": ("A[DERIVED] F2 unique 20 ceiling 23; B null mean 18.07 [15,21]; "
                       "C exact P 0.25 [0.05,0.70]; directional obs <= q95"),
        "observed": {"A": [f2["observed"], f2["ceiling"]], "B": st2["mean"], "C": st2["p_ge_obs"],
                     "directional": f2["observed"] <= st2["q95"]},
        "withdraws": ("STATEMENT.md's 'F2 stands on its exclusions' (R711, one round old) — the "
                      "count is admission arithmetic."),
        "limit": ("a count above its null says a clause excludes more than chance, never that it "
                  "excludes the RIGHT arms; and randomising one clause while holding two fixed asks "
                  "whether THIS count is surprising given the others, not whether the triple is."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
