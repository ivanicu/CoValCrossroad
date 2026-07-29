"""Does every round that produced a result reach the document a reader opens?

The companion to `scope_reaches_the_reader.py`. That one checks the GENERATED
package, where a renderer stands between the record and the reader. This one
checks the HAND-WRITTEN surface, where the failure is simpler: a round runs,
writes a verdict, and nobody ever mentions it.

Found on its first run: `r29_gold_ood` had asked whether the gold preference head
is unstable off-distribution -- directly relevant to r47 and entry 50 -- produced
a verdict, and appeared nowhere in README.md. Its recorded caveat ("a bias common
to both heads is invisible here") was answered by r47 eighteen rounds later and
nobody connected them, because one end of the connection was undelivered.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   no completed round is invisible to a reader
  PROXY      the round's directory name occurs in README.md
  IMPLICATION  absent => undelivered, definitely.
               present => named, which is NOT the same as accurately summarised.
  SAFE SIDE  flags omission only. It cannot tell whether the sentence about a
             round says what the round found -- `readme_agrees_with_results.py`
             checks the numbers, and nothing checks the wording.

Smoke, partial and archived artifacts do not count as results: a round whose
only output is a smoke run has nothing to deliver.
"""
from __future__ import annotations

import sys
import re
from pathlib import Path

# A provisional run is not a result. Matching one WORD failed twice: once on
# case (a04_smoke.json, entry 71) and once on vocabulary (a06_dryrun.json,
# entry 75). Match the class, and prefer the results/_smoke/ directory rule,
# which does not depend on the name at all.
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip",
                         re.I)

_ROOT = Path(__file__).resolve().parents[1]


def _floor(n: int, what: str) -> int:
    """Refuse to report success on an empty observation (entry 63/64).

    "Nothing outstanding" and "nothing observed" are different states, and every
    check in this package returned 0 for both. A check whose population is empty
    has measured nothing; that is exit 2, distinct from pass (0) and fail (1).
    """
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0

def main() -> int:
    readme = (_ROOT / "README.md").read_text()
    rounds = sorted(d for d in (_ROOT / "rounds").iterdir()
                    if d.is_dir() and not d.name.startswith("_"))
    missing, with_results = [], 0
    for d in rounds:
        res = [f for f in d.glob("results/**/*.json")
               if not PROVISIONAL.search(f.name) and "_smoke" not in str(f)
               and "_partial" not in str(f)]
        if not res:
            continue
        with_results += 1
        if d.name not in readme:
            missing.append((d.name, len(res)))

    print(f"rounds with a non-smoke result: {with_results}")
    print(f"named in README.md: {with_results - len(missing)}")
    floor = _floor(with_results, "the set of rounds with a non-smoke result")
    if floor:
        return floor
    if not missing:
        print("\nEvery completed round reaches the README.")
        print("  Named is not the same as accurately summarised -- this flags omission "
              "only, and nothing in this package checks a round's WORDING against its "
              "own verdict.")
        return 0
    print(f"\n{len(missing)} completed round(s) appear nowhere in README.md:\n")
    for name, n in missing:
        print(f"  {name}   ({n} results file(s))")
    print("\nA round that ran and is never mentioned is a result nobody has.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
