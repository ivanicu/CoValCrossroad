#!/usr/bin/env python3
"""Every load-bearing constant of the CLAUSE must be re-derived from the round that measured it.

⭐ WHY THIS EXISTS (R1068, after R1067). R1067 mutated all 121 numeric constants in the clause
   region one at a time; the anchoring gate noticed NONE, while a value it does assert reds. So the
   gate was perfectly coupled to values that are not the definition, and `anchoring GREEN` said
   nothing whatever about the clause.

⛔ THIS GATE CLOSES THAT GAP FOR THE CONSTANTS THAT CAN BE RE-DERIVED. It reads each from the
   committed artifact of the round that measured it and requires the statement to state it. It does
   NOT claim to cover the clause's prose, only its numbers — a gate that overstated its own reach
   would be the failure it was built to fix.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"

# each entry: (label, artifact glob, key path, how the statement must render it)
CONSTANTS = [
    ("certified family size", "A27_*/R1055_*/results/component_ablation.json",
     ["family_size"], lambda v: rf"family\s*(size\s*)?[=of]?\s*\*{{0,2}}{v}\b|\|family\|\s*=\s*{v}"),
    ("q first testable at", "A27_*/R1055_*/results/q_first_testable_at_family_size.json",
     ["q_first_testable_at_family_size"], None),
    ("q threshold family size", "A27_*/R1055_*/results/component_ablation.json",
     ["q_first_testable_at_family_size"], lambda v: rf"\|family\|\s*=\s*\*{{0,2}}{v}|k\s*=\s*{v}\b"),
    ("k needed for q", "A27_*/R1056_*/results/certification_curve.json",
     ["k_needed_for_q"], lambda v: rf"\bq@?{v}\b|q[^.\n]{{0,40}}\b{v}\b"),
    ("blind-comparator space cap", "A27_*/R1057_*/results/q_in_its_own_world.json",
     ["synthetic_family"], lambda v: rf"caps?\s+at\s+\*{{0,2}}{v}|2\S{{0,2}}\s*.\s*1\s*=\s*{v}"),
]


def load(glob):
    hits = sorted(E05.glob(glob))
    return json.loads(hits[-1].read_text()) if hits else None


def main() -> int:
    if not DEF.exists():
        print("  UNRUNNABLE: the statement is missing. Exit 2, never 0.")
        return 2
    doc = DEF.read_text()
    rows, missing_art = [], []
    for label, glob, keypath, pat in CONSTANTS:
        if pat is None:
            continue
        d = load(glob)
        if d is None:
            missing_art.append((label, glob))
            continue
        v = d
        for k in keypath:
            v = v.get(k) if isinstance(v, dict) else None
            if v is None:
                break
        if v is None:
            missing_art.append((label, f"{glob}:{'.'.join(keypath)}"))
            continue
        n = len(v) if isinstance(v, list) else v
        ok = re.search(pat(n), doc, re.I) is not None
        rows.append((label, n, ok))

    if not rows:
        print("  UNRUNNABLE: no clause constant could be re-derived; a gate over nothing must not "
              "pass. Exit 2, never 0.")
        return 2
    if missing_art:
        print("  FAIL: a declared clause constant has no artifact to re-derive it from:")
        for label, g in missing_art:
            print(f"    {label}  <-  {g}")
        return 1

    for label, n, ok in rows:
        print(f"  {'OK  ' if ok else 'FAIL'}  {label:<28} = {n}")
    bad = [r for r in rows if not r[2]]
    if bad:
        print(f"  FAIL: {len(bad)} of {len(rows)} clause constant(s) are not stated in the statement "
              f"as their artifact records them.")
        return 1
    print(f"  PASS: all {len(rows)} re-derivable clause constants are stated as measured.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
