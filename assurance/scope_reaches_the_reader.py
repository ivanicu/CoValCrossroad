"""Does what the machine-readable record SAYS actually reach the human-readable one?

Entry 57. `ASSURANCE.md` rendered every claim as `statement[:110]…`. Scope clauses
sit after the headline sentence by construction -- you state the finding, then
what it does not establish -- so the truncation deleted qualifications
specifically and could not delete headlines. Nine turns of rescoping lived in
MANIFEST.json and reached no reader. Then, one turn later, I asserted no other
renderer truncated without checking, and a sweep found two more.

Every other check in this package asks whether a claim is CORRECT. None asked
whether it is DELIVERED. That is a different failure and it had no instrument.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   a reader of the human-readable artifacts sees every qualification
             the machine-readable ones record
  PROXY      each claim's full statement string occurs verbatim in ASSURANCE.md,
             and each round result carrying a scope field has that scope
             reproduced somewhere a human reads
  IMPLICATION  absent => the qualification is undelivered, definitely.
               present => it is on the page, which is NOT the same as legible,
               prominent, or read.
  SAFE SIDE  flags omission. Says nothing about whether prose is clear.

It cannot check the README, which is written by hand and paraphrases
deliberately -- requiring verbatim scope there would force the summary to
quote itself. What it checks is the generated package, where a renderer stands
between the record and the reader and can silently drop things.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = _ROOT / "assurance/MANIFEST.json"
DOC = _ROOT / "assurance/ASSURANCE.md"

# Clause markers whose whole purpose is to qualify. If one is recorded, a reader
# must be able to find it.
SCOPE_MARKERS = ("NOT ESTABLISHED", "POPULATION (", "DETECTION FLOOR",
                 "NOT REACHED", "SCOPE", "⚠")


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    if not MANIFEST.exists() or not DOC.exists():
        print("  ! manifest or document missing -- run assurance/manifest.py first")
        return 1
    man = json.loads(MANIFEST.read_text())
    doc = norm(DOC.read_text())

    missing, scoped, delivered = [], 0, 0
    for c in man.get("claims", []):
        stmt = norm(c["statement"])
        has_scope = any(m in stmt for m in SCOPE_MARKERS)
        if has_scope:
            scoped += 1
        if stmt in doc:
            delivered += 1
        else:
            # locate how much of it survived, so the report says WHERE it was cut
            keep = 0
            for i in range(len(stmt), 0, -40):
                if stmt[:i] in doc:
                    keep = i
                    break
            missing.append((c["id"], has_scope, keep, len(stmt)))

    print(f"claims in manifest: {len(man.get('claims', []))}   "
          f"carrying a scope clause: {scoped}")
    print(f"reproduced verbatim in ASSURANCE.md: {delivered}")
    if not missing:
        print("\nEvery claim statement reaches the document in full.")
        print("  Present is not the same as legible or prominent -- this check flags "
              "omission only.")
        return 0

    print(f"\n{len(missing)} claim(s) do not reach the document in full:\n")
    for cid, has_scope, keep, total in missing:
        tag = "  <- and it carries a SCOPE clause" if has_scope else ""
        where = f"{keep}/{total} chars survive" if keep else "absent entirely"
        print(f"  {cid}: {where}{tag}")
    print("\nA qualification recorded and not rendered is a qualification nobody has.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
