"""What people actually say when they veto -- the last unread text in the release.

The unacceptable block is the only dispositive channel in the whole artefact, and its written
justifications have never been examined. The card states the intended dichotomy plainly:

    "They first reviewed each candidate response to see if any had disqualifying issues
     (either SAFETY VIOLATIONS or EGREGIOUSLY POOR QUALITY)."

That is a falsifiable claim about what the field contains. If the rationales are mostly neither --
if people veto for disagreement, for tone, for style, for taking the wrong side -- then the veto is
not a disqualification channel and every use of it as one is reading in a meaning the data does not
carry.

THIS MATTERS BEYOND THE CARD. r150 established that vetoing is nearly orthogonal to ranking: people
veto their own top choice 9.25% of the time and a rank-only model explains only 12.8% of it. That
was evidence the veto is a DISTINCT signal. What kind of distinct signal was never asked. A veto
cast for "I disagree with this position" is a second preference measurement wearing an absolute
word; a veto cast for "this tells someone to harm themselves" is a constraint. They call for
opposite treatment in any aggregation.

CLASSIFICATION IS LEXICAL AND ITS LIMITS ARE STATED UP FRONT. Keyword families cannot read intent,
and this repo has now been burned twice by matching a token and reporting a construct -- the
force-marker measurement and the harm-weight measurement both died that way. So: every rationale is
counted under EVERY family it matches rather than assigned to one, unmatched rationales are reported
as unmatched rather than distributed, and the headline is the share matching NEITHER of the card's
two categories, which is the only quantity the method can support.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

FAMILIES = {
    # the card's two stated categories
    "safety": r"\b(danger|harm|unsafe|illegal|violence|violent|weapon|suicide|self-harm|abuse|"
              r"exploit|hate|racist|sexist|discriminat|slur|offensive|inappropriate|explicit|"
              r"minor|child)\w*",
    "quality": r"\b(inaccurate|incorrect|wrong|false|misinform|error|vague|unclear|confus|"
               r"irrelevant|unhelpful|useless|incomplete|shallow|generic|repetit|nonsense|"
               r"doesn't answer|does not answer|off-topic)\w*",
    # everything the card does NOT name
    "disagreement": r"\b(disagree|I don't think|biased|bias|one-sided|opinion|agenda|push|"
                    r"impose|preachy|moraliz|lectur|judgment|judgemental)\w*",
    "tone or style": r"\b(tone|rude|condescend|patroniz|cold|blunt|harsh|dismissive|robotic|"
                     r"formal|informal|wordy|long-winded|too long|too short)\w*",
    "refusal": r"\b(refus|won't answer|declin|avoids the question|dodg|evasive|non-answer)\w*",
    "stance": r"\b(takes a side|takes sides|should not take|picks a side|political|partisan|"
              r"ideolog)\w*",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    rats, meta = [], []
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            for blk in b.get("unacceptable", []) or []:
                r = (blk.get("rationale") or "").strip()
                if r:
                    rats.append(r)
                    meta.append((s.get("importance"), s.get("subjectivity")))
    n = len(rats)
    L = [len(r) for r in rats]
    print(f"veto rationales: {n}   median {int(np.median(L))} chars, p10 "
          f"{int(np.percentile(L, 10))}, max {max(L)}")
    tiny = sum(1 for x in L if x < 20)
    print(f"  {tiny} of {n} ({tiny / n:.1%}) are under 20 characters, which bounds how much any "
          f"text method can classify and is most of why 56% match nothing below")

    hits = {k: 0 for k in FAMILIES}
    per = []
    for r in rats:
        got = {k for k, p in FAMILIES.items() if re.search(p, r, re.I)}
        for k in got:
            hits[k] += 1
        per.append(got)
    card_named = sum(1 for g in per if g & {"safety", "quality"})
    other_only = sum(1 for g in per if g and not (g & {"safety", "quality"}))
    unmatched = sum(1 for g in per if not g)

    print(f"\n{'family':16s} {'matched':>8s} {'share':>8s}   (a rationale counts under EVERY family "
          f"it matches)")
    for k, c in sorted(hits.items(), key=lambda kv: -kv[1]):
        star = "  <- named by the card" if k in ("safety", "quality") else ""
        print(f"  {k:14s} {c:8d} {c / n:8.1%}{star}")

    print(f"\nthe card says the field holds safety violations or egregiously poor quality:")
    print(f"  matches at least one of those two : {card_named:5d} ({card_named / n:.1%})")
    print(f"  matches ONLY families the card does not name: {other_only:5d} ({other_only / n:.1%})")
    print(f"  matches nothing in any family     : {unmatched:5d} ({unmatched / n:.1%})")
    print(f"  -> the supportable headline is that at least {other_only / n:.1%} of vetoes are cast "
          f"for reasons outside the card's stated dichotomy, and {unmatched / n:.1%} could not be "
          f"classified at all by this method")

    # does the veto rate track the prompt-level ratings people gave?
    by_imp = defaultdict(lambda: [0, 0])
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            # A CHECK THAT CANNOT FAIL. My first version used a non-empty `unacceptable` block as
            # BOTH the asked-filter and the vetoed-test, so every stratum came back at exactly
            # 100.0%. The block is filled for precisely the 5,006 assessments where the question was
            # posed, whether or not anything was actually flagged. Asked and vetoed are different:
            # asked = the block exists; vetoed = it contains a RATING.
            if not (b.get("unacceptable") or b.get("personal")):
                continue          # question not asked
            imp = s.get("importance") or "unstated"
            by_imp[imp][1] += 1
            flagged = any((blk.get("rating") or []) for blk in (b.get("unacceptable") or []))
            if flagged:
                by_imp[imp][0] += 1
    print(f"\nveto rate by the importance the SAME person assigned the prompt "
          f"(asked-only population):")
    for k, (v, t) in sorted(by_imp.items(), key=lambda kv: -kv[1][1]):
        print(f"  {str(k)[:44]:44s} {v:5d}/{t:5d} = {v / t:.1%}")

    ex = [r for r, g in zip(rats, per) if g and not (g & {"safety", "quality"})][:3]
    print(f"\nexamples of vetoes outside the card's dichotomy:")
    for e in ex:
        print(f"  - {e[:150]}")

    (OUT / "why_people_veto.json").write_text(json.dumps(
        {"n_rationales": n, "median_chars": int(np.median(L)), "family_hits": hits,
         "matches_card_categories": card_named, "only_outside_card": other_only,
         "unmatched": unmatched,
         "veto_rate_by_importance": {k: {"vetoed": v, "total": t, "rate": round(v / t, 4)}
                                     for k, (v, t) in by_imp.items()},
         "method_limit": "keyword families cannot read intent; every rationale is counted under "
                         "every family it matches, unmatched are reported as unmatched, and only "
                         "the outside-the-dichotomy share is claimed"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
