#!/usr/bin/env python3
"""A retraction must declare its class, its claim round and its killer round — at write time.

⛔ WHY, MEASURED ACROSS THREE ROUNDS AND MADE ADMISSIBLE BY A FOURTH.
  R951: **8 of 1,149** entries declare `same error as <entry>` — 99.3% declare no class.
  R952: **107 of 1,149** match a §4 mode at two shared tokens — 90.7% match none, and at the
        loosest threshold the real taxonomy scores BELOW decoys drawn from the ledger's own words.
  R953: **19 of 1,149** carry a parseable claim→killer pair, so the retraction-latency question is
        unidentified rather than under-powered — and all three probes were then shown to recover
        ≥0.90 of a planted structure and ≤0.05 on a stripped twin, so **the absence is measured,
        not instrumental.**

`RETRACTIONS.md` is 1,822,204 bytes against a 663,091-byte deliverable and answers none of §0.2's
questions mechanically: not *are they the same error*, not *which classes*, not *did we catch them
faster*. **The relation is not recoverable from prose after the fact.** So it has to be written when
the retraction is.

⭐ **THE VOCABULARY HAS AN ESCAPE, AND THAT IS THE LOAD-BEARING DESIGN CHOICE.** §4 names 20 modes
and R952 measured they cover at most 9% of what this ledger recorded. **A closed vocabulary would
therefore force a wrong label on nine entries in ten** — a gate that cannot be satisfied honestly is
worse than no gate, because it converts a silence into a false attribution. `class: new/<name>` is
accepted and counted separately, so the escape is visible rather than a loophole.

⚠ PROXY LEDGER — sound in one direction only:
  PROPERTY   : a reader can tell what kind of error this was and what killed it
  PROXY      : a header line parses, with a class from the vocabulary or an explicit `new/`
  IMPLICATION: parses ⇒ the fields exist. **Parsing does NOT imply the class is CORRECT** — nothing
               mechanical can check that, and this gate never claims to.
  SAFE SIDE  : a missing or malformed header FAILS. The remedy is one line, written by the person
               who already knows the answer.

⚠ AND THIS CANNOT REPAIR THE 1,149 COMMITTED ENTRIES. It binds from a floor entry number onward.
R953's numbers stand unchanged; a gate that failed on all history is a gate nobody runs.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "RETRACTIONS.md"
SKILL = pathlib.Path("/home/ivan/.claude/skills/realstat/SKILL.md")
# ⛔ THE FLOOR IS AN IDENTIFIER, NOT A COUNT, AND THE FIRST VERSION CONFLATED THEM. It was set to
#    1150 because 1,149 entries exist -- but entry IDs run 236..1387 with three gaps, so 238
#    committed entries already sit at or above 1150 and the gate would have retroactively bound
#    them. A gate that fails on history is a gate nobody runs, which this file's own docstring says.
#    The attack's vector 8 caught it: the real ledger returned 1 where an empty population was
#    expected. Measured, then fixed to one past the maximum id.
#    ⚠ AND IT STAYS A FIXED CONSTANT. Deriving it from the ledger at run time would make it bind
#    nothing, forever -- a check that cannot fail.
FLOOR_ENTRY = 1388          # ids measured 236..1387 on 2026-08-07; history is out of scope
ENTRY = re.compile(r"^## (\d+) · (.+)$")
HEADER = re.compile(r"^\s*<!--\s*retraction:\s*class=([^;]+);\s*claim=R(\d+);\s*"
                    r"killed_by=R(\d+)\s*-->\s*$")
MODE_ROW = re.compile(r"^\| \*\*([^*]+)\*\*")


def vocabulary():
    """READ from the standard, never from memory — the same discipline R952 used to extract it."""
    if not SKILL.exists():
        return None
    sk = SKILL.read_text(errors="replace")
    s4 = sk[sk.find("## §4"): sk.find("## §5")]
    return {m.group(1).strip() for m in (MODE_ROW.match(l) for l in s4.splitlines()) if m}


def audit(path: pathlib.Path, floor: int, vocab):
    """-> (rows, n_in_scope). One row per in-scope entry: ok, why, and whether the class is NEW."""
    rows = []
    lines = path.read_text(errors="replace").splitlines()
    cur, body = None, []
    def close():
        if cur is None or cur < floor:
            return
        hdr = next((HEADER.match(l) for l in body if HEADER.match(l)), None)
        if hdr is None:
            rows.append({"entry": cur, "ok": False, "why": "no retraction header", "new": False})
            return
        cls = hdr.group(1).strip()
        if cls.startswith("new/"):
            rows.append({"entry": cur, "ok": bool(cls[4:].strip()), "new": True,
                         "why": "" if cls[4:].strip() else "new/ with no name"})
        elif cls in vocab:
            rows.append({"entry": cur, "ok": True, "why": "", "new": False})
        else:
            rows.append({"entry": cur, "ok": False, "new": False,
                         "why": f"class `{cls[:48]}` is neither a §4 mode nor an explicit new/"})
    for l in lines:
        m = ENTRY.match(l)
        if m:
            close()
            cur, body = int(m.group(1)), []
        elif cur is not None:
            body.append(l)
    close()
    return rows


def main(path=None, floor=None) -> int:
    vocab = vocabulary()
    if vocab is None or len(vocab) < 10:
        print(f"  UNRUNNABLE: the §4 vocabulary must be read from {SKILL}, never from memory, and "
              f"it is missing or too small. Exit 2, never 0.")
        return 2
    path = pathlib.Path(path) if path else LEDGER
    floor = FLOOR_ENTRY if floor is None else floor
    if not path.exists():
        print(f"  UNRUNNABLE: {path} missing. Exit 2, never 0.")
        return 2

    rows = audit(path, floor, vocab)
    print(f"a retraction declares its class — {path.name}, binds from entry {floor} onward, "
          f"{len(vocab)} §4 modes in vocabulary, {len(rows)} entr(y/ies) in scope")

    if not rows:
        print("  EMPTY POPULATION: no entry at or above the floor. A gate that examines nothing "
              "must not pass.\n  Exit 2, never 0.")
        return 2

    bad = [r for r in rows if not r["ok"]]
    new = [r for r in rows if r["ok"] and r["new"]]
    for r in rows:
        print(f"  {r['entry']:<6} {'ok' if r['ok'] else 'FAIL'}"
              f"{'  (new class)' if r['new'] and r['ok'] else ''}"
              f"{'  ' + r['why'] if r['why'] else ''}")

    if new:
        print(f"\n  {len(new)} entr(y/ies) declared a NEW class. That is expected and is why the "
              f"escape exists: R952 measured §4's 20 modes covering at most 9% of this ledger, so a "
              f"closed vocabulary would force a wrong label nine times in ten.")
    if bad:
        print(f"\n{len(bad)} of {len(rows)} in-scope entries lack a parseable retraction header.")
        print("  Add one line: <!-- retraction: class=<§4 mode|new/<name>>; claim=R<n>; "
              "killed_by=R<n> -->")
        print("  ⚠ Parsing does NOT mean the class is CORRECT. Nothing mechanical can check that, "
              "and this gate does not claim to.")
        return 1

    print(f"\nAll {len(rows)} in-scope entries declare a class, a claim round and a killer round.")
    print("  This says nothing about whether the class is RIGHT — only that a later reader, and a "
          "later count, can find it without reading 1,149 entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main(*(sys.argv[1:3] if len(sys.argv) > 1 else [])))
