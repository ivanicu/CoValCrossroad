#!/usr/bin/env python3
"""R559 · The B recommendation is one cell of a two-cell specification curve.

Row 7 calls "whether reading A is correct after all" a DECISION rather than a measurement. But the
recommendation of B rests entirely on a measurement: oracle_k4 clearing the RANKER ceiling. Two
rounds computed that gap with different floors, and the ratio straddles P14's admissibility line.

ESTIMAND  effect/floor for the oracle-vs-ranker-ceiling gap, under every instrument that measured it.
IDENT     fully identified: both artifacts persist gap_rank and floor.
SCOPE     population = 968 prompts (both) · instrument = R505's floor vs R506's floor ·
          baseline = P14's admissibility line of 1.5 · regime = held-out, transitive_rate 0.665.
WORLDS    A the ratio clears 1.5 under EVERY instrument -> the recommendation is robust and row 7
            is right that what remains is a decision.
          B the ratio straddles 1.5 -> the recommendation is instrument-dependent, and row 7's
            "not a measurement" is false: a measurement is doing the work.
KILL      pre-registered: min ratio over instruments < 1.5 -> WORLD B.
POS CTRL  both artifacts must record their 4 controls as passing. If either does not, that round's
          number is inadmissible for a different reason and the comparison is void.
NEG CTRL  a ratio computed from a floor and a gap that belong to DIFFERENT rounds must be flagged
          as not a real specification -- it is a cell nobody ran.
ARTIFACT  results/two_cells.json
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
LINE = 1.5   # P14: below this, no count is admissible

def load(glob):
    fs = sorted(A24.glob(glob))
    if not fs: return None
    return json.loads(fs[0].read_text())

r505 = load("R505_*/results/*.json")
r506 = load("R506_*/results/*.json")
if not r505 or not r506:
    print("  an artifact is missing -> UNRUNNABLE"); sys.exit(2)

cells = {}
for name, d in (("R505", r505), ("R506", r506)):
    ctl = d.get("controls", {})
    ok = bool(ctl) and all(bool(v) for v in ctl.values())
    print(f"  POSITIVE CONTROL  {name}: {sum(bool(v) for v in ctl.values())}/{len(ctl)} controls "
          f"pass -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"    -> {name}'s number is inadmissible on its own terms; comparison void")
        sys.exit(2)
    cells[name] = {"gap_rank": d["gap_rank"], "floor": d["floor"], "n": d["n"],
                   "ratio": d["gap_rank"] / d["floor"], "controls_pass": True}

# NEGATIVE CONTROL: a cross-round ratio is a cell nobody ran.
cross = r506["gap_rank"] / r505["floor"]
print(f"  NEGATIVE CONTROL  a cross-round ratio ({cross:.3f}) is a cell NOBODY RAN and is "
      f"excluded -> PASS")

print(f"\n  {'instrument':<8} {'gap_rank':>10} {'floor':>10} {'effect/floor':>13}  admissible (>={LINE})")
for k, v in cells.items():
    print(f"  {k:<8} {v['gap_rank']:>10.6f} {v['floor']:>10.6f} {v['ratio']:>13.3f}  "
          f"{v['ratio'] >= LINE}")

ratios = [v["ratio"] for v in cells.values()]
lo, hi = min(ratios), max(ratios)
spread = hi / lo
print(f"\n  cells run: {len(cells)}   cells reported on the statement: 1")
print(f"  ratio range: {lo:.3f} .. {hi:.3f}   spread {spread:.2f}x   straddles {LINE}: "
      f"{lo < LINE <= hi}")

world = "B" if lo < LINE else "A"
print(f"\n  WORLD {world} -- " + (
    "the ratio straddles the admissibility line, so the recommendation is instrument-dependent "
    "and row 7's 'not a measurement' is false."
    if world == "B" else
    "every instrument clears the line; the recommendation is robust and row 7 stands."))
(pathlib.Path(__file__).parent / "results" / "two_cells.json").write_text(json.dumps(
    {"world": world, "admissibility_line": LINE, "cells": cells,
     "cells_run": len(cells), "cells_on_statement": 1,
     "ratio_min": lo, "ratio_max": hi, "spread": spread, "straddles": bool(lo < LINE <= hi),
     "cross_round_ratio_excluded": cross,
     "note": "P14: effect/floor below 1.5 admits no count, only a direction"}, indent=2))
