#!/usr/bin/env python3
"""
R713 -- is F1's exclusion set stipulated by construction, or discovered?

CHECK #315 ON R712's NEXT LINE -- TWO DEFECTS, ONE OF THEM WORK ALREADY DONE.
  ✓ p = 0.0003, ceiling 7, and the four unique exclusions are oracle/label-fitted arms. Confirmed.
  ⛔ "the ONE THING IN THE DELIVERABLE whose count beats its own null" -- an UNVERIFIED SUPERLATIVE,
    the FIFTH in this arc, true within R712's 9-cell grid and unchecked against every other claim on
    the statement. Withdrawn to: the only cell in that grid at its observed size.
  ⛔ "recomputed under the REPAIRED size clause rather than the one R360 committed" -- R712 ALREADY
    used the repaired clause. A closing sentence can be wrong by asking for what is already on disk.

⭐ THE GAUGE TEST, RUN FIRST PER §3's LADDER, AT ZERO COMPUTE.
  F1 excludes EXACTLY {greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1} and nothing else in
  the 42-arm ledger, and the name predicate /oracle|_fit1/ returns EXACTLY that set. ⛔ So F1's
  p = 0.0003 may be measuring that we built four label-reading arms AND a clause excluding
  label-reading arms.

ESTIMAND        (i) NAME-REPRODUCIBILITY per clause: does one name predicate reproduce its verdict
                set exactly, and if not by how many arms; (ii) whether R712's uniform-admission null
                is ADMISSIBLE for each clause.
IDENTIFICATION  (i) exactly computable. ⚠ (ii) is NOT a measurement -- it is a judgement about what a
                null MEANS, argued from (i). This round MEASURES reproducibility and REASONS about
                admissibility; it does not test admissibility, and says so.
SCOPE           population : the 42 arms of R360's ledger, three clauses
                instrument : exact set comparison, clause verdict vs name predicate
                             instrument unit = AN ARM
                             claim unit      = WHETHER A NULL IS ADMISSIBLE FOR A CLAUSE
                             ⚠ NOT EQUAL, and that gap is this round's main limit -- exact name
                             agreement is EVIDENCE about construction, never PROOF of it.
                baseline   : the same test on F2 and F3
                regime     : this repository at HEAD
WORLDS          A STIPULATED · B DISCOVERED · C ALL STIPULATED (see PREREGISTRATION.txt)
KILL            conditional on POSITIVE missing and g=0 failing to match
POSITIVE CTRL   a predicate KNOWN wrong for F1 -- /topw/ -- must MISS
g=0             a random 4-arm subset must not reproduce F1's exclusions; exact chance 1/C(42,4)
NEGATIVE CTRL   scramble NAMES against verdicts at fixed multisets -> the exact match must vanish
SHAM            the same test on F2 and F3 -- the operation minus the clause under study
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/stipulated.json
IMPOSSIBLE      proving construction (that the arms were BUILT to be excluded is a fact about our
                history, not about the ledger) · cross-release (41 of 42 arms are ours)
"""
from __future__ import annotations
import json, math, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEEDS, NDRAW = (0, 1, 2), 3000
INSTRUMENT_UNIT, CLAIM_UNIT = "AN ARM", "WHETHER A NULL IS ADMISSIBLE FOR A CLAUSE"

PREDS = {
    "generator-name /oracle|_fit1/": re.compile(r"oracle|_fit1", re.I),
    "generator-name /topw/": re.compile(r"topw", re.I),
    "generator-name /random|gen|promptecho|full|generic/": re.compile(
        r"random|gen|promptecho|full|generic", re.I),
    "k-value 1<k<=4": None,                       # handled specially: a k predicate, not a name one
    "sham-suffix /_sham$/": re.compile(r"_sham$"),
}


def match(pred, arms, K):
    if pred is None:
        return {a for a in arms if K.get(a) is not None and 1 < K[a] <= 4}
    return {a for a in arms if pred.search(a)}


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms = set(led["arms"]); K = led["k"]
    p2 = set(led["clause2_admits"]); p23 = set(led["clause23_admits"])
    CL = {"F1 provenance": p23 | (arms - p2),
          "F2 behaviour": p2,
          "F3 size (repaired)": {a for a in arms if K.get(a) is not None and 1 < K[a] <= 4}}
    n = len(arms)
    EXCL = {name: arms - adm for name, adm in CL.items()}

    print(f"─── THE OBJECT ───\n  arms {n}")
    for name, ex in EXCL.items():
        print(f"  {name:<20}excludes {len(ex):>3}   {sorted(ex)[:5]}"
              f"{' …' if len(ex) > 5 else ''}")

    print(f"\n─── CONTROLS ───")
    f1x = EXCL["F1 provenance"]
    hit = match(PREDS["generator-name /oracle|_fit1/"], arms, K)
    f1_miss = len(f1x ^ hit)
    wrong = match(PREDS["generator-name /topw/"], arms, K)
    posok = len(f1x ^ wrong) > 0
    print(f"  POSITIVE  a predicate KNOWN wrong for F1, /topw/, misses by {len(f1x ^ wrong)} arms -> "
          f"{'PASS — the matcher does not match everything' if posok else '⛔ FAIL'}")
    rng = random.Random(11)
    others = sorted(arms)
    g0_hits = 0
    for sd in SEEDS:
        r = random.Random(sd)
        for _ in range(NDRAW // len(SEEDS)):
            if set(r.sample(others, len(f1x))) == f1x:
                g0_hits += 1
    exact_chance = 1 / math.comb(n, len(f1x))
    g0ok = g0_hits == 0
    print(f"  g=0       {NDRAW} random {len(f1x)}-arm subsets reproduce F1's exclusions "
          f"{g0_hits} times; the EXACT chance is 1/{math.comb(n, len(f1x)):,} = {exact_chance:.2e} -> "
          f"{'PASS — the match is not free' if g0ok else '⛔ FAIL'}")
    # NEGATIVE: scramble NAMES against verdicts, preserving both multisets.
    neg_matches = 0
    for sd in SEEDS:
        r = random.Random(100 + sd)
        for _ in range(NDRAW // len(SEEDS)):
            # ⛔ `list(arms)` on a SET is NOT reproducible: the seed fixes the permutation but
            #   not the INPUT ORDER, which varies with PYTHONHASHSEED across processes. Two
            #   runs of this round returned 1 and 0 matches. `sorted` first, always.
            shuffled = sorted(arms); r.shuffle(shuffled)
            remap = dict(zip(sorted(arms), shuffled))
            scr_excl = {remap[a] for a in f1x}
            if scr_excl == hit:
                neg_matches += 1
    negok = neg_matches < NDRAW * 0.01
    print(f"  NEGATIVE  names scrambled against verdicts at fixed multisets: exact match in "
          f"{neg_matches} of {NDRAW} -> "
          f"{'PASS — any-predicate-fits-4-strings is excluded' if negok else '⛔ FAIL'}")
    plc = match(PREDS["generator-name /oracle|_fit1/"], arms, K) == hit
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc and unitok

    print(f"\n─── THE SWEEP: EVERY CLAUSE × EVERY PREDICATE, MISS COUNTS (G4) ───")
    print(f"  {'clause':<20}{'predicate':<44}{'miss':>6}{'  exact?'}")
    cells, best = [], {}
    for cname, ex in EXCL.items():
        for pname, pred in PREDS.items():
            h = match(pred, arms, K)
            # ⛔ POLARITY. A predicate matching the exact COMPLEMENT of a clause's exclusion set
            #   reproduces it perfectly and scored `miss = 42` in the first version -- F3's own
            #   k-predicate, which IS F3, looked like the worst fit on the board. The miss is the
            #   MINIMUM over both polarities, and the polarity is reported so the reader knows which.
            m_pos, m_neg = len(ex ^ h), len(ex ^ (arms - h))
            miss = min(m_pos, m_neg)
            cells.append({"clause": cname, "predicate": pname, "miss": miss,
                          "polarity": "matches exclusions" if m_pos <= m_neg else "matches ADMISSIONS",
                          "miss_as_exclusions": m_pos, "miss_as_admissions": m_neg,
                          "exact": miss == 0})
            if cname not in best or miss < best[cname]["miss"]:
                best[cname] = cells[-1]
            print(f"  {cname:<20}{pname:<44}{miss:>6}  {cells[-1]['polarity']:<20}"
                  f"{'⭐ EXACT' if miss == 0 else ''}")
    print(f"\n  best predicate per clause:")
    for c, b in best.items():
        print(f"    {c:<20}{b['predicate']:<44}miss {b['miss']}")

    A = best["F1 provenance"]["miss"]
    B = best["F2 behaviour"]["miss"]
    Cc = best["F3 size (repaired)"]["miss"]
    print(f"\n  ⚠ F3's exact match under a k-predicate is a DERIVATION: F3 IS the predicate "
          f"1 < k <= 4, so a k-predicate reproducing it is forced. Labelled, not counted.")

    print(f"\n─── REGISTERED ───")
    print(f"  A  F1 miss = 0 [0,2] -> {A}: {'INSIDE' if 0 <= A <= 2 else '⛔ OUTSIDE'}")
    print(f"  B  F2 best miss = 4 [0,20] -> {B}: {'INSIDE' if 0 <= B <= 20 else '⛔ OUTSIDE'}")
    print(f"  C  F3 best miss = 0 [0,5] -> {Cc}: {'INSIDE' if 0 <= Cc <= 5 else '⛔ OUTSIDE'} "
          f"[DERIVATION]")
    print(f"  DIRECTIONAL F1 miss < F2 miss -> {'HOLDS' if A < B else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells above, all printed. Miss counts are EXACT, so no "
          f"p-values are computed and none are implied.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the exact match would be silence."
    elif A == 0 and B > 0:
        world = (
            f"⭐⭐⭐ A STIPULATED — F1's EXCLUSIONS ARE ITS ARMS' NAMES, AND R712's NULL DOES NOT "
            f"PRICE THEM. The predicate /oracle|_fit1/ reproduces F1's exclusion set EXACTLY — miss "
            f"{A} of {n} arms — while F2's best predicate over the same families misses {B}. ⭐ SO "
            f"F1's p = 0.0003 measures that we built {len(f1x)} label-reading arms AND a clause that "
            f"excludes label-reading arms. A uniform random admission is a meaningful null for a "
            f"clause whose exclusions are DISCOVERED and an empty one for a clause whose exclusions "
            f"are STIPULATED, and the exact name match is what tells them apart here. ⛔ SO R712's "
            f"'the only clause above chance' MUST BE RE-READ: F1 is the most CONSTRUCTED of the "
            f"three, not the most informative, and its low p is a consequence of construction rather "
            f"than evidence against chance. ⚠ THIS IS NOT A DEFECT IN F1. A clause that says "
            f"'selected without reading outcome labels' SHOULD exclude exactly the arms built to "
            f"read labels; exact agreement is the clause WORKING. What is void is the p, not the "
            f"clause. ⚠ AND THE LIMIT IS THE CLAIM UNIT: exact name agreement is EVIDENCE about "
            f"construction, never PROOF of it — that the arms were BUILT to be excluded is a fact "
            f"about our history, not about the ledger, and this round measures reproducibility while "
            f"REASONING about admissibility. ⚠ F3's exact k-match is a DERIVATION, since F3 IS that "
            f"predicate. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    elif A == 0 and B == 0:
        world = (f"⭐⭐⭐ C ALL STIPULATED — every clause is exactly name-reproducible (F1 miss {A}, "
                 f"F2 {B}, F3 {Cc}), so the whole three-clause comparison is a comparison of naming "
                 f"conventions and no clause's null prices anything.")
    else:
        world = (f"⭐⭐ B DISCOVERED — the best name predicate misses F1's exclusion set by {A} arms, "
                 f"so F1's verdict carries content beyond the name and R712's reading stands.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "stipulated.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n_arms": n,
        "exclusions": {c: sorted(e) for c, e in EXCL.items()},
        "cells": cells, "best_per_clause": best,
        "f1_miss": A, "f2_best_miss": B, "f3_best_miss": Cc,
        "g0_random_subset_hits": g0_hits, "g0_exact_chance": exact_chance,
        "negative_scrambled_matches": neg_matches, "negative_draws": NDRAW,
        "registered": "A F1 miss 0 [0,2]; B F2 best miss 4 [0,20]; C F3 0 [0,5] DERIVED; F1 < F2",
        "observed": {"A": A, "B": B, "C": Cc, "directional": A < B},
        "re_reads": ("R712's 'the only clause above chance' — F1's low p follows from its exclusions "
                     "being stipulated, so it is the most CONSTRUCTED clause, not the most "
                     "informative. The p is void for F1; the clause is not."),
        "limit": ("exact name agreement is EVIDENCE about construction, never PROOF; that the arms "
                  "were built to be excluded is a fact about our history, not about the ledger. This "
                  "round measures reproducibility and REASONS about null admissibility."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
