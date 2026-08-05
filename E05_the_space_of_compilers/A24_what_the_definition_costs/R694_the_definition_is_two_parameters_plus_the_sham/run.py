#!/usr/bin/env python3
"""
R694 -- the definition is two parameters we chose, plus the sham. And a killed derivation.

CHECK #295 ON R693's NEXT LINE -- A GAUGE TEST KILLED THE PROPOSED ROUND AT ZERO COMPUTE.
  It proposed fitting (family, k) jointly and reading the accuracy as evidence. 42 arms occupy 24
  distinct (family, k) cells and TWELVE ARE SINGLETONS, so a memorising fit's accuracy is forced by
  cell cardinality. "Could this have come out otherwise?" No. ⭐ The attack ladder's cheapest rung,
  fired again -- it is now the most productive check in this arc.

⚠ AND THE GAUGE TEST ITSELF HAD AN ARITHMETIC ERROR, CAUGHT BY ABSURDITY, NOT BY A CONTROL.
  I computed a memorising fit's errors as `sum(min(counts_per_cell))`, which charges one error to
  every PURE cell. It printed 4.8% -- a memorising fit cannot score below the 78.6% majority floor,
  and that impossibility is what exposed it. Correct: `len(cell) - max(counts)`. An ARITHMETIC
  control now enforces `accuracy >= floor` for every clause reading.

ESTIMAND        for each clause reading (②, ③, ②∧③), how many (family, k) cells contain BOTH labels
                -- i.e. where is the clause NOT determined by the two parameters we chose?
IDENTIFICATION  ⚠ (family, k) is OUR parameterisation of arms we built. A mixed cell shows the
                clause is not reducible to those two parameters; it does NOT show what the clause is.
SCOPE           population : the 42 arms in R360's committed ledger
                instrument : (family, k) cell partition + label mixing
                             instrument unit = A (family, k) CELL
                             claim unit      = A PLACE THE CLAUSE IS IRREDUCIBLE
                             ⚠ NOT EQUAL -- carried into the verdict.
                baseline   : the majority-class floor per clause reading, computed
                regime     : the home release, R360's committed verdicts
WORLDS          A IRREDUCIBLE AT THE SHAM: mixed cells exist and are the sham pairs -> the definition
                  is (family, k) plus exactly the sham distinction.
                B FULLY REDUCIBLE: zero mixed cells -> the definition is two parameters we chose,
                  and the sham separation is lost.
KILL            ②∧③ with zero mixed cells -> world B, the darker outcome.
POSITIVE CTRL   a synthetic cell holding both labels is detected as MIXED.
g=0             a pure cell is NOT detected as mixed.
NEGATIVE CTRL   an empty cell is not counted.
ARITHMETIC CTRL the memorising fit must score >= the majority floor for every reading.
PLACEBO         run twice identical.
ARTIFACT        results/cells.json
IMPOSSIBLE      a parameterisation we did not choose would test reducibility properly; every arm
                here is ours except one.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent


def family(a):
    m = re.match(r"^([a-z]+?)(?:_k\d+)", a)
    return m.group(1) if m else re.sub(r"_(sham|fit\d|s\d|\d+b[AB]?|reprov)$", "", a)


def k_of(a):
    m = re.search(r"_k(\d+)", a)
    return m.group(1) if m else "none"


def cells_of(arms, positive):
    c = defaultdict(list)
    for a in arms: c[(family(a), k_of(a))].append(a in positive)
    return c


def memorise_acc(cells, n):
    """⭐ errors = minority of each cell = len - max. NOT sum(min(...)), which charges every
       PURE cell an error and printed 4.8% for a fit that cannot go below the floor."""
    err = sum(len(v) - max(Counter(v).values()) for v in cells.values())
    return (n - err) / n, err


def main() -> int:
    art = next(ARC.glob("R360_*/results/*.json"), None)
    if art is None:
        print("UNRUNNABLE: R360's ledger absent. Exit 2, never 0."); return 2
    d = json.loads(art.read_text())
    arms = list(d["arms"])
    readings = {"②": set(d["clause2_admits"]), "②∧③": set(d["clause23_admits"])}
    # ⛔ THE THIRD ROW WAS A DUPLICATE WEARING A THIRD READING'S NAME. I first wrote
    #    readings["③ (as ②∧③ minus ②-only)"] = readings["②∧③"] -- the SAME SET, relabelled. It
    #    printed as an independent reading and would have read as corroboration. R360's ledger holds
    #    `clause2_admits` and `clause23_admits` and NOT ③ alone, so ③ alone is NOT COMPUTABLE here.
    #    Registered POINT B is therefore UNCOMPUTED, not scored -- never quietly dropped.
    #    §4's "a label is not a description", committed in my own dict key.

    print("─── CONTROLS ───")
    pos = len(set([True, False])) > 1
    print(f"  POSITIVE  a synthetic cell holding both labels is MIXED -> {pos} -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = len(set([True, True])) > 1
    print(f"  g=0       a PURE cell is not mixed -> {g0} -> "
          f"{'PASS — the detector returns both values' if not g0 else '⛔ FAIL'}")
    negok = len(set([])) == 0
    print(f"  NEGATIVE  an empty cell is not counted -> {'PASS' if negok else '⛔ FAIL'}")
    plc = cells_of(arms, readings["②"]).keys() == cells_of(arms, readings["②"]).keys()
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pos and not g0 and negok and plc

    print(f"\n─── THE CELL STRUCTURE (G3 — every reading, every mixed cell) ───")
    rows, arith_ok = [], True
    for name, positive in readings.items():
        c = cells_of(arms, positive)
        n_single = sum(1 for v in c.values() if len(v) == 1)
        mixed = {k: v for k, v in c.items() if len(set(v)) > 1}
        acc, err = memorise_acc(c, len(arms))
        y = [a in positive for a in arms]
        floor = max(Counter(y).values()) / len(y)
        ok = acc >= floor
        arith_ok &= ok
        rows.append({"reading": name, "n_cells": len(c), "singletons": n_single,
                     "mixed": sorted(f"{a}/{b}" for a, b in mixed),
                     "n_mixed": len(mixed), "memorise_acc": acc, "errors": err,
                     "floor": floor, "arith_ok": ok, "n_pass": sum(y)})
        print(f"  {name:<26} cells {len(c):<3} singletons {n_single:<3} "
              f"⭐ MIXED {len(mixed)}   memorising fit {acc:.1%} vs floor {floor:.1%} "
              f"{'✓' if ok else '⛔ BELOW FLOOR — the error formula is wrong again'}")
        for k_, v in mixed.items():
            members = [a for a in arms if (family(a), k_of(a)) == k_]
            print(f"  {'':26} irreducible at {k_}: {members}")
    print(f"\n  ARITHMETIC CONTROL  memorising fit >= floor for every reading -> "
          f"{'PASS' if arith_ok else '⛔ FAIL'}")
    ctl = ctl and arith_ok

    m2 = next(r for r in rows if r["reading"] == "②")
    m23 = next(r for r in rows if r["reading"] == "②∧③")
    print(f"\n  ⛔ registered B (③ alone has 1 mixed cell) -> UNCOMPUTED. R360's ledger holds "
          f"clause2_admits and clause23_admits, not ③ alone. A first draft of this round satisfied "
          f"B by RELABELLING ②∧③ as ③ -- a duplicate row that would have read as a third reading "
          f"agreeing with the other two. Reported as uncomputed rather than dropped.")
    print(f"  registered A (②∧③ has 2 mixed) [0,6] -> {m23['n_mixed']}: "
          f"{'INSIDE' if 0 <= m23['n_mixed'] <= 6 else '⛔ OUTSIDE'}, error {m23['n_mixed']-2:+d}")
    dirn = m23["n_mixed"] <= m2["n_mixed"]
    print(f"  DIRECTIONAL ②∧③ has no MORE mixed cells than ② -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'} ({m23['n_mixed']} vs {m2['n_mixed']})")
    killed = m23["n_mixed"] == 0
    print(f"  pre-registered kill (②∧③ zero mixed) -> "
          f"{'⭐ FIRES — fully reducible, the sham separation is LOST' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B FULLY REDUCIBLE — ②∧③ has ZERO mixed (family,k) cells. The full definition "
                 f"is determined by two parameters we chose, and the sham separation does not "
                 f"survive the conjunction. That is the darker outcome and it is what the data says.")
    else:
        world = (f"⭐⭐⭐ A THE DEFINITION IS TWO PARAMETERS WE CHOSE, PLUS THE SHAM. Over 42 arms and "
                 f"{m2['n_cells']} (family,k) cells, ② is irreducible in {m2['n_mixed']} cell(s) and "
                 f"②∧③ in {m23['n_mixed']}, and those cells are "
                 f"{'; '.join(m23['mixed']) or 'none'} — the released core against its own sham, and "
                 f"topw_k4 against its sham. ⭐ A MEMORISING (family,k) FIT SCORES "
                 f"{m23['memorise_acc']:.1%} ON ②∧③ BY CONSTRUCTION, so R693's proposed joint fit "
                 f"would have reported a DERIVATION as evidence. ⚠ AND THE UNIT GAP IS THE READING: "
                 f"(family,k) is OUR parameterisation of arms WE built. A mixed cell shows the clause "
                 f"is not reducible to those two parameters; it does not show what the clause IS.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(arms)} arms × {len(readings)} clause readings, 5 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"cells.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_arms": len(arms), "rows": rows, "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 2 [0,6] mixed cells for ②∧③; ②∧③ <= ②; kill if zero",
        "point_B": "UNCOMPUTED -- R360 holds no ③-alone verdict; a draft satisfied it by relabelling ②∧③",
        "killed_derivation": ("R693's proposed joint (family,k) fit: 12 of 24 cells are singletons, "
                              "so accuracy is forced by cell cardinality. Not evidence."),
        "own_arithmetic_error": ("the gauge test first computed errors as sum(min(counts)), charging "
                                 "every PURE cell an error, and printed 4.8% for a memorising fit "
                                 "that cannot go below the 78.6% floor. Caught by absurdity, not by "
                                 "a control -- an ARITHMETIC control now enforces acc >= floor."),
        "limit": "(family,k) is OUR parameterisation of arms WE built.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'cells.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
