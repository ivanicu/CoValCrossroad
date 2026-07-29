"""Does a round's README row carry the LIMITATIONS its own verdict states?

Why this exists
---------------
Entries 66, 67 and 70 were all the same defect and all found by hand:

  66  the layer table reproduced "held-out human rankings" twenty lines below the
      correction withdrawing it, and credited 97.4% to two rounds when one measured it
  67  the P row dropped r42's own closing words -- "at this margin and at no other" --
      and the Q row omitted that roughly half of r12's inversion rides on length
  70  r42's verdict says "the null readings in this package"; its population was four
      hand-listed rounds

Every one is *a qualifier the round itself had already written, absent from the
prose a reader meets*. Nothing in this package compared the two. Entry 67 noted
that the hand audit "found more than any automated check in this package" -- that
is an argument for building the check, not for keeping the audit manual.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   the README's summary of a round does not silently drop what the
             round said it did not establish
  PROXY      each LIMITATION SENTENCE in the verdict (one containing NOT REACHED /
             NOT ESTABLISHED / UNVERIFIED / "not a verdict" / "at no other" / a
             leading negation) shares at least one distinctive content word with
             that round's README row
  IMPLICATION  no lexical echo  =>  the qualifier is absent from the row,
               definitely -- there is no paraphrase of "not established" that
               shares no content word with it.
               an echo  =>  SOME token survived, and NOTHING about whether the
               row's paraphrase preserves the qualifier's force. A row saying
               "largely established" echoes "not established" and is worse than
               silence.
  SAFE SIDE  flags total omission only. It cannot detect a weakened paraphrase,
             which is the more likely and more dangerous failure, and it says so
             on every run rather than reporting a clean bill.

THE POPULATION IS THE FIRST FINDING
-----------------------------------
15 rounds have a README row and NO verdict string at all -- r02, r04, r06, r07,
r08, r09, r10, r13, r14, r16, r19, r25, r30, r39, r45. For those the row is
hand-written prose with nothing in the artifact to check it against, and two of
them have already produced retractions on exactly that account (r04 in entry 66,
r13's "as informative as" equivalence claim). They are reported as UNCHECKABLE,
never omitted from the denominator.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

ROW = re.compile(r"^\|\s*\[(r\d+)\]\(rounds/")
# A sentence that exists to bound the claim.
LIMIT = re.compile(
    r"(NOT REACHED|NOT ESTABLISHED|not established|UNVERIFIED|not a verdict|"
    r"at no other|is NOT\b|does not\b|cannot\b|no other margin|STIPULATED|"
    r"stipulated|not comparable|says nothing|not shown|NOT ruled out|"
    r"not licensed|near enough to half)", re.I)
STOP = set("""a an the and or of to in on for with by is are was were be been it its this that those
these as at from than then so but not no we our i you they he she them his her their which what when
where how why all any some most more less very much just only also than into onto over under about
after before during while if else each per via vs versus does do did done can could may might must
should would will shall have has had having there here now still yet even both either neither such
same other another one two three four five six seven eight nine ten""".split())


def content_words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z_]{3,}", s.lower()) if w not in STOP}


def sentences(v: str) -> list[str]:
    # the freeze annotation is appended with " || " and is not the round's own claim
    v = v.split(" || ")[0]
    return [s.strip() for s in re.split(r"(?<=[.;])\s+|\n", v) if s.strip()]


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", type=Path, default=_ROOT / "README.md")
    ap.add_argument("--min-overlap", type=int, default=1,
                    help="distinctive words a limitation must share with the row")
    a = ap.parse_args()

    rows: dict[str, str] = {}
    for ln in a.readme.read_text().splitlines():
        m = ROW.match(ln.strip())
        if m:
            rows.setdefault(m.group(1), ln)

    verdicts: dict[str, str] = {}
    for f in sorted(_ROOT.glob("rounds/*/results/*.json")):
        if "smoke" in f.name.lower() or any(p.startswith("_") for p in f.parts):
            continue
        rid = f.parts[-3].split("_")[0]
        if rid in verdicts:
            continue
        try:
            doc = json.loads(f.read_text())
        except Exception:
            continue
        v = doc.get("verdict") or doc.get("conclusion")
        if isinstance(v, str) and v.strip():
            verdicts[rid] = v

    both = sorted(set(rows) & set(verdicts), key=lambda r: int(r[1:]))
    uncheckable = sorted(set(rows) - set(verdicts), key=lambda r: int(r[1:]))

    print(f"README rows: {len(rows)}   rounds with a verdict string: {len(verdicts)}")
    print(f"  checkable (row AND verdict): {len(both)}")
    print(f"  UNCHECKABLE (row, no verdict): {len(uncheckable)}  {', '.join(uncheckable)}")
    print("  An uncheckable row is hand-written prose with nothing in the artifact to")
    print("  compare it against. That is not a pass; it is the absence of an instrument.\n")

    flagged, n_limits = [], 0
    for rid in both:
        row_words = content_words(rows[rid])
        for s in sentences(verdicts[rid]):
            if not LIMIT.search(s):
                continue
            n_limits += 1
            sw = content_words(s)
            if not sw:
                continue
            overlap = sw & row_words
            if len(overlap) < a.min_overlap:
                flagged.append((rid, s, sorted(sw)[:8]))

    print(f"limitation sentences found in verdicts: {n_limits}")
    if flagged:
        print(f"\n{len(flagged)} carry NO lexical echo in their README row:\n")
        for rid, s, sw in flagged:
            print(f"  {rid}: {s[:150]}")
            print(f"       distinctive words: {', '.join(sw)}\n")
    else:
        print("\nEvery limitation sentence has some echo in its round's README row.")

    print("  An echo is not preservation. A row that says \"largely established\" echoes")
    print("  \"not established\" and passes this check while inverting the claim -- the")
    print("  weakened paraphrase is the likelier failure and this instrument cannot see it.")

    floor = _floor(len(both), "the set of rounds with both a README row and a verdict")
    if floor:
        return floor
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
