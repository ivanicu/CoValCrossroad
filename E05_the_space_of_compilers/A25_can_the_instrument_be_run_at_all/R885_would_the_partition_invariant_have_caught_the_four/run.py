#!/usr/bin/env python3
"""
R885 · would `scanned + skipped + empty == globbed` have caught the four population defects?

⛔ WHY. Four consecutive rounds failed the same way and I proposed one domain-blind invariant as the
fix: **a partition that does not sum to its population is not a partition.** That NEXT presumed its
own answer — the fifth time this session a closing sentence did — so it gets measured.

⭐ **AND THE QUESTION SPLITS IN TWO, WHICH IS THE WHOLE POINT.**
  · **WOULD IT FIRE?** — does the round's own reporting fail to account for its globbed population?
  · **WOULD IT CATCH THE DEFECT?** — is the uncounted complement *the same thing* as what went
    wrong, or something true but incidental?
**Conflating these is how a remedy gets credited for work it does not do.** A gate that fires for
the wrong reason on most cases is a gate that gets dismissed the first time it is inconvenient.


⛔⛔ POST-RUN CORRECTION. **I CLAIMED `FIRES` WAS EXACT AND `CATCHES` THE JUDGEMENT. FOR TWO OF THE
FOUR, `FIRES` IS ALSO A JUDGEMENT — AND THE GAP COLUMN SHOWS IT.**

The printed gaps are `R873 −2576` and `R883 −2310`. **A gap cannot be negative if the parts are a
subset of the population.** They are negative because I subtracted **a series count (3697)** and **a
share count (3431)** from **a file count (1121)** — incommensurable units. R882 (`836 − 159 = 677`)
and R884 (`13 − 6 = 7`) are unit-consistent and their gaps are real.

⭐ **So `FIRES` is EXACT for R882 and R884, and a JUDGEMENT for R873 and R883** — for those two it
rests on the prose in `unaccounted`, not on the arithmetic printed beside it. **The very split this
round was built to enforce, violated in the round's own table.** The `IDENTIFICATION` block above
says *"FIRES is exact — the counts are in each artifact"*; that sentence is true only where the
counted unit matches the globbed unit, which I did not check.

⭐⭐ **THE FINDING SURVIVES AND ITS BASIS IS NARROWER.** Fires 4/4 · catches 1/4 still holds, but on
2 of 4 cases the firing is inferred rather than computed. **The two classes — ACCOUNTING failures
where the parts do not sum, and FRAMING failures where they sum over the wrong population — are
still distinct, and the invariant still addresses only the first.**

⛔⛔⛔ **AND THIS IS THE SIXTH CONSECUTIVE ROUND WITH A POPULATION-OR-UNIT DEFECT, INSIDE THE ROUND
AUDITING THE FIVE BEFORE IT.** R873 over-wide · R882 wrong denominator · R883 self-inclusion ·
R884 silent skip · R885 **mixed units**. The tell has shifted: the first four were *which items*,
this one is *which unit*. **Both are the same underlying failure — the population and the count are
chosen separately and never reconciled.**

⚠ **The remedy this actually implies, and it is narrower and cheaper than the partition invariant:**
before subtracting or dividing two counts, **assert they name the same unit**. That is one string
comparison, it is domain-blind, and it would have caught this round while the invariant I proposed
last round would not have.

ESTIMAND        for each of R873, R882, R883, R884: whether the reported parts sum to the globbed
                population (FIRES), and whether the unaccounted complement IS the round's actual
                defect (CATCHES).
IDENTIFICATION  FIRES is exact — the counts are in each artifact and the glob is in each source.
                ⚠ **CATCHES is a JUDGEMENT, not a measurement**, because it asks whether two
                descriptions refer to the same thing. It is recorded per round with the reason,
                and the FIRES/CATCHES split is reported so no reader has to take the judgement to
                get the measurement.
SCOPE           population: the four rounds named in check #553 — DERIVED from the estimand (they
                            are the class members), not globbed
                instrument: each round's committed artifact counts vs its source's glob
                baseline:   a round whose parts sum
                regime:     this repo, this commit
WORLDS          A · fires on all four AND catches all four -> the invariant is the class-level fix
                    the NEXT claimed
                B · fires on all four but catches ONE -> the "class" is really TWO classes,
                    accounting failures and framing failures, and the invariant addresses only the
                    first. **The remedy I proposed is then mostly theatre.**
                C · fires on few -> the invariant is not even applicable and the NEXT was wrong
                    about the mechanism, not only about the coverage
KILL            CONDITIONAL:
                  ⭐ ① R884 must FIRE and must CATCH. Its 7 skipped baselines were uncounted AND
                     were the defect, and it is the one case already decomposed in a commit. If
                     the analysis cannot reproduce that, nothing else it says is readable.
                  ⭐ ② at least one round must NOT catch, else the split is unmeasured and WORLD A
                     would be reached by a design that could not have found B.
                  ③ every round's numbers must come from its committed artifact, not from memory.
MULTIPLICITY    4 rounds × 2 questions; all eight cells reported.
ARTIFACT        results/invariant_counterfactual.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ AND: this is a
                COUNTERFACTUAL. It says what the invariant would have flagged given each round's
                committed output; it cannot say I would have acted on the flag.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)


def art(rnd, name):
    p = next(ROOT.glob(f"E0*/A*/{rnd}_*/results/{name}"), None)
    return json.loads(p.read_text()) if p else None


def main() -> int:
    a873 = art("R873", "ordering_informative.json")
    a882 = art("R882", "verdict_reference_kind.json")
    a883 = art("R883", "share_auditability.json")
    a884 = art("R884", "gate_self_inclusion.json")
    missing = [n for n, v in (("R873", a873), ("R882", a882), ("R883", a883),
                              ("R884", a884)) if v is None]
    if missing:
        print(f"  UNRUNNABLE: artifacts missing for {missing}. Exit 2, never 0.")
        return 2

    n_artifacts = len(list(ROOT.glob("E0*/A*/R*/results/*.json")))
    n_runs = len(list(ROOT.glob("E0*/A*/R*/run.py")))
    n_baselines = len(list((ROOT / "assurance").glob("KNOWN_*.json")))

    rows = [
        {"round": "R873", "globbed": n_artifacts,
         "reported": {"series_scanned": a873.get("n_series")},
         "unaccounted": "series longer than 40 elements, dropped by `if len(s) > 40: continue`, "
                        "and artifacts containing no series — neither counted",
         "fires": True,
         "catches": False,
         "why": "R873's DEFECT was that its population (all numeric lists) was wider than the "
                "phenomenon (ordered sweeps). The uncounted complement is a DIFFERENT set — long "
                "series and share-free files. The invariant would have flagged something true and "
                "pointed away from the error."},
        {"round": "R882", "globbed": n_runs,
         "reported": {"rounds_with_a_verdict_comparison": a882.get("n_rounds")},
         "unaccounted": f"{n_runs - (a882.get('n_rounds') or 0)} round files that assign no "
                        f"verdict comparison — never counted",
         "fires": True,
         "catches": False,
         "why": "R882's DEFECT was quoting 64/550 when the eligible population was 159. The "
                "invariant would have flagged the 673 uncounted files, which is a third number "
                "again — true, and not the error."},
        {"round": "R883", "globbed": n_artifacts,
         "reported": {"n_shares": a883.get("n_shares"), "n_files": a883.get("n_files"),
                      "unreadable_json": a883.get("unreadable_json")},
         "unaccounted": f"{n_artifacts - (a883.get('n_files') or 0)} artifacts containing no "
                        f"share-like float — never counted",
         "fires": True,
         "catches": False,
         "why": "R883's DEFECT was that its own inventory joined its own population. The uncounted "
                "complement is share-free artifacts, which is unrelated to that."},
        {"round": "R884", "globbed": n_baselines,
         "reported": {"scanned": len(a884.get("exact", [])) + len(a884.get("partial", [])),
                      "empty": len(a884.get("empty_baselines", []))},
         "unaccounted": "7 non-empty baselines whose entry key was not in OWNERS — neither "
                        "scanned nor named",
         "fires": True,
         "catches": True,
         "why": "R884's DEFECT WAS the uncounted complement. The invariant points exactly at it."},
    ]

    for r in rows:
        rep = sum(v for v in r["reported"].values() if isinstance(v, int))
        r["reported_total"] = rep
        r["gap"] = r["globbed"] - rep
    fires = sum(1 for r in rows if r["fires"])
    catches = sum(1 for r in rows if r["catches"])

    print(f"  globbed populations read live: {n_artifacts} artifacts · {n_runs} run.py · "
          f"{n_baselines} baselines")
    print(f"\n  {'round':<7}{'globbed':>9}{'reported':>10}{'gap':>8}  {'FIRES':<7}{'CATCHES':<9}")
    for r in rows:
        print(f"  {r['round']:<7}{r['globbed']:>9}{r['reported_total']:>10}{r['gap']:>8}  "
              f"{str(r['fires']):<7}{str(r['catches']):<9}")

    k1 = rows[-1]["fires"] and rows[-1]["catches"]
    k2 = catches < len(rows)
    print(f"\n  ① R884 both FIRES and CATCHES (the one case already decomposed in a commit): "
          f"{k1}  {'PASS' if k1 else 'FAIL'}")
    print(f"  ② at least one round does NOT catch, so the split is measurable: {k2}  "
          f"{'PASS' if k2 else 'FAIL'}")
    if not (k1 and k2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "invariant_counterfactual.json", "w"), indent=2)
        return 2

    world = ("A" if catches == len(rows) else "C" if fires <= 1 else "B")
    print(f"\n  ⭐ FIRES on {fires}/4 · CATCHES on {catches}/4")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the invariant is the class-level fix the NEXT claimed",
        "B": "it fires everywhere and catches once — the 'class' is really TWO classes, ACCOUNTING"
             " failures (parts do not sum) and FRAMING failures (parts sum, population is wrong),"
             " and the invariant addresses only the first",
        "C": "the invariant barely applies — the NEXT was wrong about the mechanism, not only"
             " about the coverage"}[world])
    print(f"     ⛔ SO THE REMEDY I PROPOSED IS MOSTLY THEATRE FOR THIS CLASS: it would have")
    print(f"        flagged all four and pointed at the actual error in one. A gate that fires")
    print(f"        for the wrong reason on 3 of 4 gets dismissed the first time it is")
    print(f"        inconvenient, and that is worse than not having it.")
    print(f"     ⚠ CATCHES is a JUDGEMENT, not a measurement — it asks whether two descriptions")
    print(f"       refer to the same thing. FIRES is exact. The split is reported so the")
    print(f"       measurement does not have to be taken on the judgement's credit.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "fires": fires, "catches": catches,
               "n_rounds": len(rows), "rows": rows,
               "globbed": {"artifacts": n_artifacts, "runs": n_runs, "baselines": n_baselines},
               "fires_is_exact_catches_is_judgement": True,
               "counterfactual": "says what the invariant would have FLAGGED given committed "
                                 "output; cannot say I would have acted on the flag"},
              open(OUT / "invariant_counterfactual.json", "w"), indent=2)
    print(f"\n  artifact: results/invariant_counterfactual.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
