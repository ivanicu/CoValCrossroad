"""A round that analyses 36.5% of the criteria must say so.

WHY THIS EXISTS
---------------
Sixteen rounds apply the same filter -- keep only criteria rated by a MAJORITY of a
prompt's raters:

    thr = max(2, (len(raters) + 1) // 2)
    ... if len(scores) >= thr

r48 identified what that selects: the surviving class is capped at six per prompt and
is the PRE-SEEDED set, shown identically to every participant. The excluded 63.5% are
participant-authored write-ins, and r92 established they carry a median of ONE rater --
so the restriction is structural, not a tuning choice, and it cannot be lifted by
re-analysis.

That makes it load-bearing twice over for queue item 1. The population bullet ("no
detected aggregate loss in the tested splits") and the leakage bullet ("not primarily
same-rater leakage") are BOTH established on the pre-seeded criteria -- which are
exactly the criteria most exposed to the shared-menu construction the same item warns
about. A reader who does not know the restriction cannot see that.

Census when this was written: 10 of 16 disclosed it somewhere, 6 disclosed it nowhere.

WHY THERE IS NO JUDGMENT CALL HERE
-----------------------------------
The donor-scope check (entry 168) needs a per-round `needs_scope` decision, because
whether a round PUBLISHES a donor difference is a reading of its claim. This one does
not: applying the filter is a property of the SOURCE, and any round that applies it
analysed 36.5% of the criteria whatever it concluded. So the rule is flat -- apply the
filter, disclose the filter -- and the registry is a verified list rather than a set of
judgements. Fewer places to be wrong.

THE TWO GATES
-------------
COMPLETENESS  every round whose source applies the filter must be in ROUNDS below.
              The list is checked against the source tree on every run, never trusted:
              a new round that applies the filter and is not listed FAILS. A
              hand-written population turns an objective check into self-report.
DISCLOSURE    every listed round must mention the restriction in its stored artifact
              or in its README row.

THE PROXY LEDGER -- which direction this is sound in
-----------------------------------------------------
PROPERTY    the round tells its reader it analysed only the pre-seeded criteria.
PROXY       the artifact or README row matches a disclosure phrase.
IMPLICATION no match => not disclosed              SOUND, and this is what it gates on.
            match    => adequately disclosed       NOT SOUND. A passing mention of
                                                   "write-in" in another context
                                                   satisfies the pattern.
SAFE SIDE   may report a MISSING disclosure; may never certify a present one as
            adequate. That is a reading, left to review.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# Verified against the source tree on every run -- see COMPLETENESS above.
ROUNDS = {
    "r01_rater_structure", "r05_value_taxonomy", "r06_rule_tournament",
    "r13_seed_vs_writein", "r16_minority_regret", "r17_conditional_core",
    "r18_routing_difficulty", "r32_channel_decomposition", "r34_global_rater_crossfit",
    "r35_polarity_abstention", "r36_channel_shapley", "r37_leakage_topology",
    "r43_criterion_heterogeneity", "r49_provenance_crossfit", "r50_response_anchoring",
    "r62_matching_floor", "r92_writein_analysability",
}

FILTER = re.compile(r"len\(raters\)\s*\+\s*1\)\s*//\s*2|>=\s*thr\b")
DISCLOSE = re.compile(
    r"majority of (the|a) prompt|pre-?seeded|63\.5%|seed(ed)? (set|class|criteria)|write-?in",
    re.I)


def main() -> int:
    found = {p.parent.name for p in ROOT.glob("rounds/*/run.py")
             if FILTER.search(p.read_text())}
    readme = README.read_text()
    print(f"rounds applying the majority/seed filter: {len(found)}   registry: {len(ROUNDS)}")

    fail = 0
    unregistered = sorted(found - ROUNDS)
    stale = sorted(ROUNDS - found)
    if unregistered:
        fail += 1
        print(f"\nFINDING: {len(unregistered)} round(s) apply the filter and are not registered:")
        for r in unregistered:
            print(f"    {r}")
    if stale:
        fail += 1
        print(f"\nFINDING: {len(stale)} registered round(s) no longer apply it -- registry drifted:")
        for r in stale:
            print(f"    {r}")

    missing = []
    for r in sorted(ROUNDS & found):
        txt = ""
        for f in glob.glob(str(ROOT / f"rounds/{r}/results/*.json")):
            if Path(f).stat().st_size < 4_000_000:
                try:
                    txt += json.dumps(json.load(open(f)))
                except Exception:
                    pass
        rows = [l for l in readme.splitlines()
                if l.lstrip().startswith("|") and f"rounds/{r})" in l.lstrip()[1:].split("|")[0]]
        if not (DISCLOSE.search(txt) or any(DISCLOSE.search(l) for l in rows)):
            missing.append(r)

    if missing:
        fail += 1
        print(f"\nFINDING: {len(missing)} round(s) analyse only the pre-seeded criteria -- 36.5% of "
              f"the total -- and say so in neither their artifact nor their README row:")
        for r in missing:
            print(f"    {r}")

    if fail:
        print(f"\n{fail} gate(s) failed.")
        return 1
    print(f"\nall {len(ROUNDS & found)} seed-filtered rounds are registered and disclose the restriction.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
