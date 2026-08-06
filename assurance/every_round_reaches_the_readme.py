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

import sys as _s
_s.path.insert(0, str(_ROOT))
from covalx.rounds import (fixture_dir, iter_round_dirs,  # noqa: E402
                            round_dir)


def main() -> int:
    readme = (_ROOT / "README.md").read_text()
    # iterdir() over rounds/ now yields the twelve CAMPAIGN directories, not rounds -- and the
    # failure was silent in the worst way: the glob still matched, so this reported twelve rounds
    # with no results, a completeness verdict computed over the wrong population.
    rounds = [d for d in iter_round_dirs(_ROOT) if not d.name.startswith("_")]
    missing, with_results = [], 0
    for d in rounds:
        res = [f for f in d.glob("results/**/*.json")
               if not PROVISIONAL.search(f.name) and "_smoke" not in str(f)
               and "_partial" not in str(f)]
        if not res:
            continue
        with_results += 1
        # ⚠ PROXY LEDGER ENTRY, 2026-08-03 — this proxy went stale under the project's own layout.
        #   PROPERTY     a round that ran is REACHABLE by a reader from an index.
        #   PROXY (old)  its directory name occurs in the ROOT README.md.
        #   WHY IT BROKE the root README was a per-round table for 34 of its 40 revisions, and
        #                stopped being one at 3d14d1b (2026-08-02, "Restructured 217 rounds into
        #                epochs and arcs"). It is an EPOCH summary now, by design. P16 puts a
        #                round's home in its ARC's README: "campaign READMEs are tables of
        #                contents". So the proxy kept testing a layout the project had left.
        #   PROXY (new)  its directory name occurs in the root README **or in its OWN arc's
        #                README** — its own arc, not any arc, because a round mentioned under
        #                somebody else's decision is not reachable, it is misfiled.
        #   IMPLICATION  absent from both => genuinely unreachable. Present => reachable from an
        #                index, and NOTHING about whether that index line is accurate; that is
        #                `readme_agrees_with_results.py`.
        # ⚠ AND READ THE PASS HONESTLY: this check passes today because
        # `generate_round_index.py` wrote those arc tables in the same session. That is a
        # CONSTRUCTION, not a discovery, and it is weak evidence of the property. Its real and
        # ongoing power is forward-looking: a NEW round added without regenerating the index
        # still fails here, which is the only thing that keeps the index from rotting.
        arc_readme = d.parent / "README.md"
        arc_txt = arc_readme.read_text(errors="ignore") if arc_readme.exists() else ""
        if d.name not in readme and d.name not in arc_txt:
            missing.append((d.name, len(res)))

    # A round with NO CODE is invisible to every enumeration in this package,
    # because all of them start from results files. r56 published a preregistered
    # NOT REPLICATED whose run.py was never committed -- its numbers exist in a
    # commit message and nowhere else, and r66 could not recompute them
    # (entry 101). Reported here because this is the check that enumerates from
    # DIRECTORIES rather than from results, so it is the only one that can see it.
    codeless = [d.name for d in rounds if not list(d.glob("*.py"))]
    resultless = [d.name for d in rounds
                  if not [f for f in d.glob("results/**/*.json")
                          if not PROVISIONAL.search(f.name) and "_smoke" not in str(f)]]

    print(f"round directories: {len(rounds)}   with a non-smoke result: {with_results}")
    # ⚠ THIS LABEL SAID "named in README.md" AND THE TEST IS NOT THAT (entry 1318). The proxy
    # was widened to root-README-OR-OWN-ARC-README on 2026-08-03, and the print was not. A reader
    # (me, this round) took 630 as a count of root-README mentions, scanned the root, found 140,
    # and spent two hypotheses on a contradiction that was a stale caption. The instrument's unit
    # and the sentence's unit must be the same string -- §4's own remedy, applied to a print.
    print(f"reachable from an index (root README or own arc README): "
          f"{with_results - len(missing)}")
    if codeless:
        print(f"\n⚠ {len(codeless)} round(s) contain NO .py FILE: {', '.join(codeless)}")
        print("  A round with no code cannot be recomputed, and every other enumeration in")
        print("  this package starts from results files, so nothing else can see it.")
    if resultless:
        print(f"⚠ {len(resultless)} round(s) have no non-smoke result: {', '.join(resultless)}")
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
