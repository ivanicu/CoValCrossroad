"""A link to a path that does not exist transfers the package's credibility to nothing.

WHY THIS EXISTS
---------------
Entry 173 added a disclosure note to six README rows citing
`rounds/r48_selection_partition`. No such directory exists -- r48 is
`r48_provenance_identified`. The round's CONTENT was right and its PATH was invented:
a plausible name written from memory and never asked of the filesystem.

It was caught by a one-off command, which is not a guard. This makes it one.

The failure is quiet in the worst way: a broken relative link renders as ordinary text
in most viewers, so a reader sees a citation and cannot tell it points nowhere. The
package's whole convention is "pointer or D2" -- every claim cites the object. A
pointer that does not resolve is the same defect as no pointer, wearing a citation's
clothes.

WHAT IS CHECKED
---------------
Every relative link in the emittable documents -- `rounds/`, `data/`, `assurance/`,
`covalx/`, `scripts/` -- must resolve. Directory links resolve to a directory, deep
links (`rounds/<name>/results/x.json`) to the file.

THE PROXY LEDGER
----------------
PROPERTY    the link points at the round the sentence is about.
PROXY       the path exists on disk.
IMPLICATION path missing => link is wrong        SOUND, and this gates on it.
            path exists  => link is RIGHT        NOT SOUND. A link to the wrong
                                                 EXISTING round resolves cleanly and
                                                 this check cannot see it.
SAFE SIDE   reports unresolvable links; never certifies that a resolving link is the
            correct one. That is a reading, left to review.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ["README.md", "RETRACTIONS.md", "PREREGISTRATION.md", "FROZEN.md", "EAR.md",
        "NORTH_STAR.md", "ADVERSARY_FORECAST.md"]
# Extended beyond rounds/ (entry 176): the invented-path failure is not specific to
# round links -- any relative path this package emits can be written from memory. These
# are the directories the documents actually cite.
# ⚠ 2026-08-02: this alternation began `\d\d_[a-z0-9_]+`, and the EAR restructure renamed every
# such directory to `E\d\d_...`. The regex then matched ZERO round links and the check reported
# "every relative link resolves" over an empty set -- a clean bill of health issued by an
# instrument pointed at nothing, which is the exact failure this package exists to prevent, in
# the commit that restructured it. The count assertion at the end is what makes it survivable.
LINK = re.compile(r"\]\(((?:E\d\d_[A-Za-z0-9_]+|\d\d_[a-z0-9_]+|rounds|data|assurance|covalx|scripts)/[A-Za-z0-9_./-]+)\)")


def main() -> int:
    scanned = 0
    total = 0
    bad: list[tuple[str, int, str]] = []
    for d in DOCS:
        p = ROOT / d
        if not p.exists():
            continue
        scanned += 1
        for ln, line in enumerate(p.read_text().splitlines(), 1):
            for m in LINK.finditer(line):
                total += 1
                if not (ROOT / m.group(1)).exists():
                    bad.append((d, ln, m.group(1)))

    if not scanned:
        print("no emittable documents found -- nothing to check")
        return 2
    if not total:
        print(f"{scanned} document(s) scanned, ZERO relative links found -- nothing to check")
        return 2

    print(f"{scanned} document(s), {total} relative links")
    if bad:
        print(f"\nFINDING: {len(bad)} link(s) point at a path that does not exist. A broken "
              f"relative link renders as ordinary text, so a reader sees a citation and cannot "
              f"tell it resolves nowhere:")
        for d, ln, t in bad:
            print(f"    {d}:{ln}  ->  {t}")
        print(f"\n1 gate(s) failed.")
        return 1
    print("\nevery relative link resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
