#!/usr/bin/env python3
"""Attack assurance/a_retraction_declares_its_class.py. A lock never attacked is untested.

⭐ ISOLATED BY CONSTRUCTION, NOT AFTER THE FACT. R950's attack ran its gate over the whole repo, so
every expected exit code silently depended on nothing else being in scope; the moment a real round
landed, a vector flipped and the attack reported 6/7 for a lock that had not changed — the same
defect R942 had already measured elsewhere. This gate takes a PATH and a FLOOR, so every vector runs
against a temporary ledger containing exactly what the vector plants and nothing else.
"""
import importlib.util
import pathlib
import sys
import tempfile

ROOT = pathlib.Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
GATE = ROOT / "assurance/a_retraction_declares_its_class.py"

spec = importlib.util.spec_from_file_location("gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

OK_HDR = ("<!-- retraction: class=the verdict string is not a computation; "
          "claim=R240; killed_by=R247 -->")

#      name, ledger text, floor, expected exit
VECTORS = [
    ("1 VALID — §4 class, claim and killer all present",
     f"## 1150 · a claim\n{OK_HDR}\nbody\n", 1150, 0),

    ("2 NO HEADER — the 1,149 committed entries' shape",
     "## 1150 · a claim\nbody with prose only\n", 1150, 1),

    ("3 MISSING killed_by — a partial header must not pass",
     "## 1150 · a claim\n<!-- retraction: class=check that cannot fail; claim=R240 -->\nbody\n",
     1150, 1),

    ("4 FREE-PROSE CLASS — not a §4 mode and not an explicit new/",
     "## 1150 · a claim\n<!-- retraction: class=something went a bit wrong; claim=R240; "
     "killed_by=R247 -->\nbody\n", 1150, 1),

    ("5 NEW CLASS ESCAPE — must PASS, or the gate forces a wrong label 9 times in 10",
     "## 1150 · a claim\n<!-- retraction: class=new/the ledger is not machine readable; "
     "claim=R240; killed_by=R247 -->\nbody\n", 1150, 0),

    ("6 NEW WITH NO NAME — the escape must not be a loophole",
     "## 1150 · a claim\n<!-- retraction: class=new/; claim=R240; killed_by=R247 -->\nbody\n",
     1150, 1),

    ("7 BELOW THE FLOOR — history is out of scope and must be SKIPPED, leaving nothing examined",
     "## 1149 · an old claim\nbody with prose only\n", 1150, 2),
]


def run(text, floor):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
        f.write(text)
        p = f.name
    try:
        return gate.main(p, floor)
    finally:
        pathlib.Path(p).unlink(missing_ok=True)


def main():
    results = []
    for name, text, floor, want in VECTORS:
        got = run(text, floor)
        ok = got == want
        results.append((name, ok, got, want))
        print(f"  {'OK    ' if ok else 'BROKEN'} {name}\n           exit={got} expected={want}\n")

    # 8 — the real ledger. Its baseline is EMPTY POPULATION until an entry lands at or above the
    #     floor, and that is a green state that has examined nothing. It must exit 2, never 0.
    got = gate.main()
    ok = got == 2
    results.append(("8 REAL LEDGER — empty population above the floor must exit 2", ok, got, 2))
    print(f"  {'OK    ' if ok else 'BROKEN'} 8 REAL LEDGER — empty population must exit 2"
          f"\n           exit={got} expected=2\n")

    n = sum(1 for _, ok, _, _ in results if ok)
    print(f"{n}/{len(results)} vectors behave as specified")
    if n != len(results):
        print("  BROKEN vectors above are real holes in the lock, not notes.")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
