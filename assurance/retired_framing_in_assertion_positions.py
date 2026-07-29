"""Retired framings must not appear where prose ASSERTS: titles, headers, table cells.

Entry 65. The framing this project withdrew was the README's subtitle for
fourteen turns. `no_withdrawn_framings.py` could not see it: that check scans
results JSONs and deliberately excludes prose, because README legitimately
*discusses* withdrawn framings in order to withdraw them, and a checker that
cannot tell assertion from mention would either flag those sentences forever or
be taught to ignore the ones it exists to police.

I then recorded "the prose surface is unwatchable by construction". That was a
boundary asserted without testing, which is the habit entries 57-65 are about.

**There is a sound narrower population: STRUCTURAL POSITION.** A title, a
subtitle, a section header and a table cell assert by where they sit. A sentence
in body prose can be a mention. Measured before this was written:

    README.md            headers/subtitle 0   table cells 0   body prose 3
    FROZEN.md            0 / 0 / 0
    PREREGISTRATION.md   0 / 0 / 0

The three body-prose hits are the withdrawal discussions. So the assertion
positions are already clean, and a check over them fires zero false positives
today while catching exactly the defect entry 65 records.

RETRACTIONS.md is EXCLUDED: quoting withdrawn claims is that file's function, and
5 of its table cells do so deliberately.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   no retired framing is asserted in a reader-facing document
  PROXY      no retired PHRASE occurs in a header, a bold line in the first four
             lines, or a table cell of the watched files
  IMPLICATION  present => asserted, worth reading.  absent => NOTHING about body
               prose, which remains unwatchable and is where a retired framing
               could still be asserted in a full sentence.
  SAFE SIDE  flags only. It narrows the unwatchable surface; it does not close it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
WATCHED = ("README.md", "FROZEN.md", "PREREGISTRATION.md")

RETIRED = [
    (r"\bmeasures?\s+values\b", "values%/non-values framing"),
    (r"\bvalue[-_ ]carrying share\b", "same; use 'source specificity'"),
    (r"\bnot\s+(?:same-sample\s+)?leakage\b", "-> NOT PRIMARILY SAME-RATER circularity"),
    (r"\bdoes not depend on forcing\b", "-> ROBUST TO POST-HOC ABSTENTION only"),
    (r"\bnor country-conditional\b|\bnot population-conditional\b",
     "-> no aggregate loss detected in the tested splits"),
    (r"\bnot\s+(?:an\s+)?OOD artifact\b", "-> not explained by monotone degradation"),
    (r"\blaunder(?:s|ed|ing)\b", "-> core INTERNALISES polarity into criterion semantics"),
    # r10's row read "23.7% of the gap is topic, not value" and cleared every
    # framing check for the life of the project: the list held "measures values"
    # and "value-carrying share", and the DECOMPOSITION form of the same retired
    # contrast was on neither (entry 76). Matched narrowly enough that the
    # legitimate "demographic proxies, not value constituencies" is untouched --
    # that sentence denies a constituency, it does not decompose an accuracy.
    (r"\b(?:topic|quality|generic|format|style|wording)\s*,?\s+not\s+values?\b",
     "values/non-values DECOMPOSITION -> own-rubric vs reference-rubric"),
    # A pattern for the literal phrase "values vs non-values" was written here and
    # REMOVED the same minute: its only firing was on r10's replacement text,
    # "never values vs non-values", i.e. on a DISAVOWAL of the framing. A rule
    # that fires only on correct prose teaches you to phrase disavowals
    # awkwardly, which is worse than not having it. The decomposition pattern
    # above is the one with a demonstrated catch.
]
PAT = [(re.compile(p, re.I), why) for p, why in RETIRED]


def assertion_positions(text: str):
    """Yield (line_no, kind, line) for positions that assert by structure."""
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if s.startswith("#"):
            yield i, "header", s
        elif i <= 4 and s.startswith("**") and s.endswith("**"):
            yield i, "subtitle", s
        elif s.startswith("|") and not set(s) <= set("|-: "):
            yield i, "table cell", s


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. Exit 2, not success (entry 64).")
        return 2
    return 0


def main() -> int:
    hits, scanned = [], 0
    for name in WATCHED:
        p = _ROOT / name
        if not p.exists():
            print(f"  ! {name} absent -- UNCHECKED, not clean")
            continue
        for lineno, kind, line in assertion_positions(p.read_text()):
            scanned += 1
            for rx, why in PAT:
                m = rx.search(line)
                if m:
                    hits.append((name, lineno, kind, m.group(0), line[:90], why))

    print(f"assertion positions scanned: {scanned} across {len(WATCHED)} documents")
    print("  (headers, a bold line in the first four, and table cells; body prose is")
    print("   NOT watched and remains the surface entry 65 fell through)")
    floor = _floor(scanned, "the set of assertion positions")
    if floor:
        return floor
    if not hits:
        print("\nNo retired framing sits in an assertion position.")
        print("  This says nothing about body prose, where a retired framing could still")
        print("  be asserted in a full sentence and no instrument would see it.")
        return 0
    print(f"\n{len(hits)} retired framing(s) in assertion positions:\n")
    for name, lineno, kind, phrase, line, why in hits:
        print(f"  {name}:{lineno}  ({kind})")
        print(f"    phrase  {phrase!r}")
        print(f"    line    {line}")
        print(f"    rescope {why}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
