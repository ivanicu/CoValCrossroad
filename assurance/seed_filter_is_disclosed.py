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
import ast, re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# Verified against the source tree on every run -- see COMPLETENESS above.
ROUNDS = {
    "R01_rater_structure", "R05_value_taxonomy", "R06_rule_tournament",
    "R13_seed_vs_writein", "R16_minority_regret", "R17_conditional_core",
    "R18_routing_difficulty", "R32_channel_decomposition", "R34_global_rater_crossfit",
    "R35_polarity_abstention", "R36_channel_shapley", "R37_leakage_topology",
    "R43_criterion_heterogeneity", "R49_provenance_crossfit", "R50_response_anchoring",
    "R62_matching_floor", "R92_writein_analysability",
    "R97_rule_tournament_tost",
}

def _code_only(src: str) -> str:
    """⛔ THE PATTERN MUST MATCH CODE, NOT TEXT ABOUT CODE.
    `R382_does_the_pattern_match_anything` was flagged as applying the seed filter. It does not: its
    only match is inside a `print()` that QUOTES the regex while discussing it. Registering it would
    have recorded a filter application that never happened and corrupted the registry -- paying a
    debt that does not exist. A search is an instrument (§4), and this one was matching prose.
    Repair: blank every string literal and comment via `ast`, then search what remains. Falls back to
    the raw source on a parse error, which is the SAFE direction -- a round is over-detected (and so
    surfaces for a human) rather than silently dropped."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    lines = src.splitlines(keepends=True)
    offs, tot = [], 0
    for ln in lines:
        offs.append(tot); tot += len(ln)
    def pos(r, c):
        return offs[r - 1] + c if 0 < r <= len(offs) else len(src)
    out = list(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
           and node.end_lineno is not None:
            a, b = pos(node.lineno, node.col_offset), pos(node.end_lineno, node.end_col_offset)
            for i in range(a, min(b, len(out))):
                if out[i] != "\n":
                    out[i] = " "
    return re.sub(r"#[^\n]*", "", "".join(out))


FILTER = re.compile(r"len\(raters\)\s*\+\s*1\)\s*//\s*2|>=\s*thr\b")
DISCLOSE = re.compile(
    r"majority of (the|a) prompt|pre-?seeded|63\.5%|seed(ed)? (set|class|criteria)|write-?in",
    re.I)


def main() -> int:
    found = {p.parent.name for p in ROOT.glob("E*/A*/R*/run.py")
             if FILTER.search(_code_only(p.read_text()))}
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
        for f in glob.glob(str(ROOT / f"E*/A*/{r}/results/*.json")):
            if Path(f).stat().st_size < 4_000_000:
                try:
                    txt += json.dumps(json.load(open(f)))
                except Exception:
                    pass
        rows = [l for l in readme.splitlines()
                if l.lstrip().startswith("|") and f"/{r})" in l.lstrip()[1:].split("|")[0]]
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
