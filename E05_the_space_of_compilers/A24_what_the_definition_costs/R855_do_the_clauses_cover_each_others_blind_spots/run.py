#!/usr/bin/env python3
"""
R855 · do the clauses cover each other's blind spots? — and the population trap fires on my own NEXT.

⛔ WHY. R854 found that ~15 arms clear clause ② under a pair shuffle, that the survivor sets are
10.7x chance overlap (so arm-intrinsic, not per-seed noise), and that the NINE surviving all eight
seeds are every one an ORACLE or FITTED arm. It closed by OWING a check: are those nine the arms
clause ③ (*no prompt labels*) already excludes? If so the clauses are not independent filters but a
CHAIN in which one repairs another's blind spot.

⚠ AND THE FIRST RESULT IS THAT THE CHECK CANNOT BE RUN AS I STATED IT. R854's nine live in a
99-arm space; clause ③'s exclusion was measured by R360/R444 on **42 arms**. **Only 3 of the 9 are
in that population at all.** This is the population trap that R851 already recorded once today
("29 of 99 is not 33 of 42") — and my own NEXT walked into it.

ESTIMAND        of R854's nine permutation-survivors, (a) how many are in R360's 42-arm space at
                all, and (b) of those, how many are admitted by ② and removed by ③.
IDENTIFICATION  set membership over two COMMITTED artifacts. No new scoring, no model.
SCOPE           population: R360's 42-arm ledger, which is where ③ was measured
                instrument: exact set membership
                baseline:   the nine, from R854's committed artifact
                regime:     home release
WORLDS          A · the checkable survivors are ②-admitted and ③-excluded -> the clauses form a
                    CHAIN and ③ covers ②'s permutation blind spot
                B · they are not -> the clauses are independent and ②'s blind spot is uncovered
KILL            CONDITIONAL: both artifacts must load and the nine must be read from R854's own
                committed JSON, never retyped. If fewer than 2 of the nine are in the population,
                the intersection is not reportable and the round returns UNVERIFIED for (b).
⚠ NO CONTROL    this is set arithmetic over committed artifacts, not an estimate. There is nothing
                to be noisy. The honest analogue of a control is the POPULATION CHECK above, which
                CAN fail and DID constrain the answer to a third of the set.
ARTIFACT        results/clause_interlock.json.
IMPOSSIBLE      the other 6 of 9 — they would need ③ re-measured on the 99-arm space, which is a
                different experiment and is named here rather than approximated.
"""
import json, glob, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

nine = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R854_*/results/survivor_stability.json"))[0])
                 )["always_survivors"]
r360 = json.load(open(glob.glob(str(ROOT / "E05*/A24*/R360_*/results/r360_clause_ledger.json"))[0]))
pop, c2, c23 = set(r360["arms"]), set(r360["clause2_admits"]), set(r360["clause23_admits"])

inpop = sorted(set(nine) & pop)
out = sorted(set(nine) - pop)
print(f"  R854 survivors: {len(nine)}")
print(f"  R360 population (where ③ was measured): {len(pop)} arms")
print(f"  ⭐ POPULATION CHECK  in that space: {len(inpop)} of {len(nine)} -> {inpop}")
print(f"     NOT in it (uncheckable): {len(out)} -> {out}")

if len(inpop) < 2:
    print("\n  UNVERIFIED for the interlock: too few survivors in the population. Exit 2.")
    raise SystemExit(2)

adm2 = [a for a in inpop if a in c2]
adm23 = [a for a in inpop if a in c23]
print(f"\n  of the {len(inpop)} checkable: admitted by ②      : {len(adm2)} -> {adm2}")
print(f"                              admitted by ②∧③   : {len(adm23)} -> {adm23}")
interlock = (len(adm2) == len(inpop)) and (len(adm23) == 0)
print(f"\n  ⭐ WORLD {'A' if interlock else 'B'}: "
      + ("every checkable survivor passes ② and is removed by ③ — the clauses form a CHAIN, and ③"
         " covers ②'s permutation blind spot"
         if interlock else
         "the pattern does not hold — the clauses are independent here and ②'s blind spot is"
         " uncovered"))
print(f"     ⚠ established on {len(inpop)} of {len(nine)} survivors. The other {len(out)} were never")
print(f"     in the space where ③ was measured, and approximating them would be the population")
print(f"     error this project recorded earlier today.")

head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                      capture_output=True, text=True).stdout.strip()
json.dump({"commit": head, "world": "A" if interlock else "B", "survivors": nine,
           "population_size": len(pop), "checkable": inpop, "uncheckable": out,
           "admitted_by_2": adm2, "admitted_by_2and3": adm23, "interlock": bool(interlock)},
          open(OUT / "clause_interlock.json", "w"), indent=2)
print(f"\n  artifact: results/clause_interlock.json @ {head[:8]}")
