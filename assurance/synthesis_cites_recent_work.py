"""Report which synthesis sections cite nothing recent. A staleness INDICATOR, not a gate.

WHY THIS EXISTS
---------------
Three times this package published a finding that never reached the section supposed
to carry it: r58's own README row quoted a census two regenerations old (entry 193),
the leakage passage lacked the criterion-population clause its own ledger entry had
stated (entry 175), and the M(R,J,pi,Q,P) layer table -- the reframed object's central
deliverable -- cited nothing past r58 in four of five rows while r85-r97 landed
(entry 200). Three instances of one class.

WHAT THIS CANNOT BE
-------------------
It cannot check that a finding reached the RIGHT section. Deciding which layer a round
bears on is a reading, and entry 199 established what happens when a name-based rule is
pushed past what it can decide: it invents pairings and reports them as findings. So
this does not attempt it.

WHAT IT DOES INSTEAD
--------------------
For each synthesis section it reports the HIGHEST round number cited and the gap to the
newest round in the package. A section whose newest citation is far behind is not
necessarily wrong -- it may legitimately rest on early work -- so this REPORTS and
never gates. It is a prompt to look, not a verdict.

  PROPERTY   a synthesis section reflects current evidence.
  PROXY      it cites a recent round.
  IMPLICATION cites nothing recent => worth checking     WEAK, and only a prompt.
              cites something recent => it is current    FALSE. A row can cite r99 and
                                                         still omit what r99 found.
  SAFE SIDE  raises a question. It answers none.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
CITE = re.compile(r"(?:\d\d_[a-z0-9_]+/)?r(\d+)_")
# Synthesis sections: the layer table rows and the headline block. Named explicitly --
# a regex over "important-looking" prose would be exactly the guess this avoids.
SECTIONS = [
    ("layer R", lambda l: l.lstrip().startswith("| **R** rubric")),
    ("layer J", lambda l: l.lstrip().startswith("| **J** judge")),
    ("layer pi", lambda l: l.lstrip().startswith("| **π** protocol")),
    ("layer Q", lambda l: l.lstrip().startswith("| **Q** responses")),
    ("layer P", lambda l: l.lstrip().startswith("| **P** population")),
]
STALE_GAP = 20          # rounds behind the newest before it is worth a look


def main() -> int:
    newest = max((int(p.name.split("_")[0][1:]) for p in ROOT.glob("[0-9][0-9]_*/r*/")
                  if p.name.split("_")[0][1:].isdigit()), default=0)
    if not newest:
        print("no rounds found -- nothing to check")
        return 2
    lines = README.read_text().splitlines()

    rows, found = [], 0
    for name, pred in SECTIONS:
        hits = [l for l in lines if pred(l)]
        if not hits:
            rows.append((name, None, "SECTION NOT FOUND -- renamed or removed"))
            continue
        found += 1
        cited = [int(m) for m in CITE.findall(hits[0])]
        top = max(cited) if cited else 0
        rows.append((name, top, f"{len(cited)} citation(s), newest r{top}, "
                                f"{newest - top} behind r{newest}"))
    if not found:
        print(f"none of the {len(SECTIONS)} named sections was found -- the README was "
              f"restructured and this check is looking for something that no longer exists")
        return 2

    print(f"newest round in the package: r{newest}\n")
    stale, missing = [], []
    for name, top, note in rows:
        flag = ""
        if top is None:
            missing.append(name); flag = "  <- LOOK"
        elif newest - top > STALE_GAP:
            stale.append((name, top)); flag = "  <- LOOK"
        print(f"  {name:<10} {note}{flag}")

    if missing:
        print(f"\n{len(missing)} named section(s) not found. Either the README was restructured "
              f"or a synthesis section was deleted; this check cannot tell which.")
    if stale:
        print(f"\n{len(stale)} section(s) cite nothing within {STALE_GAP} rounds of the newest. "
              f"That is a PROMPT TO LOOK, not a finding -- a section may rest legitimately on "
              f"early work, and one citing r{newest} can still omit what r{newest} found.")
    else:
        print(f"\nevery named section cites work within {STALE_GAP} rounds of r{newest}.")
    return 0        # report contract: this never gates


if __name__ == "__main__":
    sys.exit(main())
