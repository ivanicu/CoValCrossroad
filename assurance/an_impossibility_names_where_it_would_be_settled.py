#!/usr/bin/env python3
"""An IMPOSSIBLE block declares WHERE it would be settled, as an ENUM. Forward-only, and it says so.

⛔ WHY, WITH THE COUNT THAT EARNED IT. R1039 measured that this arc's own IMPOSSIBLE lines fell to its
   own later rounds at 4 of 16 against R802's committed 1 of 30, and R1040 made it 5. All five shared
   ONE shape: each said the answer needed something OUTSIDE the release, and each was answered by an
   object already INSIDE it — pool16's subsets (R1033), the comparator family as its own null (R1038),
   the annotator panel (R1040).

⛔ AND R1041 CLOSED THE RETROACTIVE ROUTE BEFORE THIS WAS BUILT. Across nine text features the best
   separator between fallen and standing blocks reaches p = 0.0769 against a Bonferroni threshold of
   0.0056 and a label permutation of 0.2637. They are indistinguishable in committed text. So this
   gate CANNOT triage the existing blocks and does not try: it is FORWARD-ONLY, and that is a
   limitation stated in the file rather than discovered later.

⭐ THE FIX IS HB8's, AND R1029's: *if it can be an enum, it may NOT be text*, and STORE the field
   rather than recover it. A block declares `SETTLES:` followed by one tag from a CLOSED SET. An enum
   cannot be gamed by wording — a wrong tag is a wrong tag, and an invented one fails by membership.

    SETTLES: IN-RELEASE <object>     an object inside this release would settle it. NAME IT.
                                     ⭐ Five lines that claimed the opposite were answered this way.
    SETTLES: OUT-OF-RELEASE <what>   it genuinely needs something the release does not contain.
                                     ⚠ This is the tag the five wrongly deserved, so it is the one to
                                       be most suspicious of when writing it.
    SETTLES: UNATTACKED              no claim about possibility is being made at all.
                                     ⭐ This is the honest default, and R1039's whole finding is that
                                       it was almost never used where it belonged.

⚠ WHAT THIS GATE CANNOT DO, STATED UP FRONT. It checks that a DECLARATION EXISTS and is well-formed.
  It cannot check the declaration is TRUE — tagging a genuinely-external limit `IN-RELEASE` passes.
  That is a different unit and would need a reader. **The enum removes the wording loophole, not the
  mislabelling one**, which is the same boundary `register_requirements.py` draws for its own field.

EXIT  0 GREEN (every in-scope block declares, well-formed) · 1 RED (a block does not) ·
      2 UNRUNNABLE (no in-scope rounds yet — an empty population is NOT a pass, and until a round
        newer than the cutoff exists there is no evidence this gate works on real blocks)
"""
from __future__ import annotations
import pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
CUTOFF = 1041                      # forward-only: R1041 measured that earlier blocks cannot be triaged
TAGS = ("IN-RELEASE", "OUT-OF-RELEASE", "UNATTACKED")
DECL = re.compile(r"SETTLES:\s*([A-Z-]+)")


def block(text):
    m = re.search(r"^IMPOSSIBLE\s+(.+?)(?=^[A-Z]{3,}\s|^\"\"\")", text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else None


def verdict(b):
    m = DECL.search(b or "")
    if not m:
        return "NO-DECLARATION"
    tag = m.group(1)
    if tag not in TAGS:
        return f"INVALID-TAG:{tag}"
    if tag != "UNATTACKED" and len(b[m.end():].strip()) < 12:
        return f"{tag}-NAMES-NOTHING"
    return tag


def selftest():
    cases = [
        ("no field", 'x\nIMPOSSIBLE  it needs a second release.\nSEEDS 3\n', "NO-DECLARATION"),
        ("invented tag", 'x\nIMPOSSIBLE  SETTLES: MAYBE something.\nSEEDS 3\n', "INVALID-TAG:MAYBE"),
        ("names nothing", 'x\nIMPOSSIBLE  SETTLES: IN-RELEASE .\nSEEDS 3\n', "IN-RELEASE-NAMES-NOTHING"),
        ("valid in-release", 'x\nIMPOSSIBLE  SETTLES: IN-RELEASE the annotator panel, split in half.\nSEEDS 3\n', "IN-RELEASE"),
        ("valid unattacked", 'x\nIMPOSSIBLE  SETTLES: UNATTACKED\nSEEDS 3\n', "UNATTACKED"),
    ]
    ok = True
    print("  SELF-TEST — five constructed blocks whose answers are known:")
    for name, txt, want in cases:
        got = verdict(block(txt))
        ok &= (got == want)
        print(f"     {name:<20}{got:<28}{'PASS' if got == want else '⛔ FAIL want ' + want}")
    print(f"     ⚠ these are CONSTRUCTED cases and validate the PARSER only. A parser that reads")
    print(f"       invented blocks is validated against my imagination — which is why an empty REAL")
    print(f"       population exits 2 below rather than 0.")
    return 0 if ok else 2


def main(argv) -> int:
    if "--selftest" in argv:
        return selftest()
    if selftest() != 0:
        print("  ⛔ the parser failed its own control. Exit 2, never 0.")
        return 2

    rows = []
    for p in sorted(E05.glob("A*/R*/run.py")):
        m = re.match(r"R(\d+)_", p.parent.name)
        if not m or int(m.group(1)) <= CUTOFF:
            continue
        rows.append((f"R{m.group(1)}", verdict(block(p.read_text()))))

    print(f"\n  scope: rounds newer than R{CUTOFF} — FORWARD-ONLY, because R1041 measured that fallen "
          f"and\n  standing blocks are indistinguishable in committed text (best p 0.0769 against a "
          f"Bonferroni\n  threshold of 0.0056). This gate cannot triage the earlier blocks and does "
          f"not try.")
    if not rows:
        print(f"\n  UNRUNNABLE: no round newer than R{CUTOFF} exists yet, so there is no evidence this "
              f"gate\n  works on real blocks. An empty population is NOT a pass. Exit 2, never 0.")
        return 2

    print(f"\n     {'round':<9}{'declaration':<30}")
    bad = []
    for rid, v in rows:
        print(f"     {rid:<9}{v:<30}")
        if v not in TAGS:
            bad.append((rid, v))
    if bad:
        print(f"\n  ⛔ RED — {len(bad)} block(s) do not declare where they would be settled: {bad}")
        print(f"     The tags are {TAGS}. `UNATTACKED` is the honest default and costs one word.")
        return 1
    print(f"\n  GREEN — {len(rows)} in-scope block(s), every one declaring a valid tag.")
    print(f"  ⚠ AND THIS CHECKS THE DECLARATION EXISTS, NEVER THAT IT IS TRUE. Tagging a genuinely")
    print(f"    external limit IN-RELEASE passes. The enum removes the WORDING loophole, not the")
    print(f"    MISLABELLING one — the same boundary `register_requirements.py` draws for its field.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
