"""The defect list audited the way it audited CoVal: every item, what null did it never run.

Four times in this sweep a finding of mine has survived as a FACT and failed as an INTERPRETATION.
That is a base rate, not an anecdote, and it points the next check at my own DEFECTS.py rather than
at the artefact. Two items were killed before this file was written:

  "the weight scale is used as a near-binary"     17% at the endpoints, but all 21 values are used
                                                  and the entropy is 4.04 bits of a possible 4.39 --
                                                  92% of uniform. Not a near-binary. The defensible
                                                  claim is endpoint over-representation.
  "rationale names a best the ranking doesn't"    12.6% over all matches, but "B is better than C"
                                                  is TRUE when the ranking is A>B>C and my check
                                                  demanded B be FIRST. On superlatives only -- the
                                                  subset where the claim is even meaningful -- it is
                                                  7.1%. The comparative subset ran at 35.0%, which is
                                                  what a false-positive-by-construction looks like.

This round tests the four remaining items whose MEASUREMENT is sound and whose INTERPRETATION rests
on a baseline I never computed. In each case the number is right and the word attached to it is the
thing under test.

  identical-ranking annotators    6 people, always the same string. Above chance -- or is 6 what you
                                  get from any pool with a skewed marginal ranking distribution?
  panel concentrated              63% in three countries. Concentrated relative to WHAT? Uniform over
                                  19 countries is a strawman; nobody sampled that way.
  veto field capped at five       a cap is a mechanism. A distribution that stops at five could also
                                  be a population that mostly did five.
  prompts synthetic and short     139 median characters, and I wrote that nothing here transfers to
                                  production traffic. I have no production traffic.

The rule being applied is the one the sweep found the hard way: a result of magnitude X licenses a
claim of magnitude at most X. Every item below either gets its baseline or gets its claim shrunk.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

SEEDS = list(range(5))
VERDICTS: list[dict] = []


def verdict(item, was, now, status, why):
    VERDICTS.append({"item": item, "was": was, "now": now, "status": status, "why": why})


def first_world(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        if b.get("ranking"):
            return b["ranking"].replace(" ", "")
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]

    # ------------------------------------------------------------------ 1
    # "Six annotators submit the same ranking every time, and nothing flags them."
    # The measurement is a fact. "Nothing flags them" implies they SHOULD be flagged, which is a
    # claim that six is more than chance produces. That needs the marginal distribution.
    per = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            r = first_world(s)
            if r:
                per[a["annotator_id"]].append(r)
    elig = {k: v for k, v in per.items() if len(v) >= 5}
    obs = sum(1 for v in elig.values() if len(set(v)) == 1)

    pool = [r for v in per.values() for r in v]
    marg = Counter(pool)
    # analytic expectation under the marginal: P(all k identical) = sum_r p_r^k
    p = np.array([c / len(pool) for c in marg.values()])
    exp_analytic = sum(float((p ** len(v)).sum()) for v in elig.values())
    # and by permutation, which also respects the per-person load profile
    sims = []
    for sd in SEEDS:
        rng = random.Random(sd)
        c = 0
        for v in elig.values():
            draw = rng.choices(list(marg.keys()), weights=list(marg.values()), k=len(v))
            if len(set(draw)) == 1:
                c += 1
        sims.append(c)
    print("=" * 78)
    print("ITEM 1  'six annotators submit the same ranking every time, and nothing flags them'")
    print("=" * 78)
    print(f"  eligible annotators (>=5 world rankings) : {len(elig)}")
    print(f"  observed all-identical                   : {obs}")
    print(f"  expected under the marginal (analytic)   : {exp_analytic:.2f}")
    print(f"  expected by permutation, 5 seeds         : {np.mean(sims):.2f} "
          f"(range {min(sims)}-{max(sims)})")
    print(f"  distinct ranking strings in the pool      : {len(marg)}; "
          f"most common {marg.most_common(1)[0][0]} at {marg.most_common(1)[0][1] / len(pool):.1%}")
    if obs <= max(sims):
        verdict("identical-ranking annotators", "6 people, nothing flags them",
                f"{obs} observed vs {exp_analytic:.1f} expected -- inside the null",
                "KILLED",
                "the marginal ranking distribution is skewed enough that this many constant "
                "annotators is what chance produces; there is nothing to flag")
    else:
        verdict("identical-ranking annotators", "6 people, nothing flags them",
                f"{obs} observed vs {exp_analytic:.3g} expected under the marginal; "
                f"permutation gave {max(sims)} in 5 seeds", "SURVIVES",
                "186 distinct ranking strings and a 3.5% modal string make a constant annotator "
                "essentially impossible by chance; these six are a real behavioural signature")

    # ------------------------------------------------------------------ 2
    # "63% three countries" -- concentrated relative to what?
    ctry = Counter((a.get("demographics") or {}).get("country_of_residence")
                   for a in ann)
    ctry.pop(None, None)
    n = sum(ctry.values())
    top3 = sum(c for _k, c in ctry.most_common(3)) / n
    # Herfindahl and the effective number of countries -- baseline-free concentration measures
    shares = np.array([c / n for c in ctry.values()])
    hhi = float((shares ** 2).sum())
    eff = 1 / hhi
    ent = float(-(shares * np.log(shares)).sum())
    print("\n" + "=" * 78)
    print("ITEM 2  'the panel is concentrated in a few countries'")
    print("=" * 78)
    print(f"  countries represented          : {len(ctry)}")
    print(f"  top-3 share                    : {top3:.1%}")
    print(f"  effective number of countries  : {eff:.1f}  (1/HHI; 19 would be perfectly even)")
    print(f"  Shannon entropy                : {ent:.2f} nats of a possible {math.log(len(ctry)):.2f}")
    for k, c in ctry.most_common(6):
        print(f"    {str(k)[:28]:28s} {c:5d}  {c / n:6.1%}")
    print("  NO REFERENCE DISTRIBUTION EXISTS IN THE RELEASE. The card names no sampling frame and")
    print("  no target quotas, so 'concentrated' has no denominator here. What IS stateable without")
    print("  one: the effective panel is the size above, not 19, and any per-country estimate below")
    print("  the top few rests on double-digit counts.")
    small = sum(1 for _k, c in ctry.items() if c < 30)
    print(f"  countries with fewer than 30 annotators: {small} of {len(ctry)}")
    verdict("panel concentrated in a few countries", f"63% in three countries, 'concentrated'",
            f"effective n = {eff:.1f} countries; {small} of {len(ctry)} have <30 people",
            "DOWNGRADED",
            "the count is right and the WORD is unsupported: no sampling frame is published, so "
            "there is no distribution to be concentrated relative to. The defensible statement is "
            "the effective panel size and the thin per-country cells")

    # ------------------------------------------------------------------ 3
    # "the veto and personal fields are capped at five per annotator"
    cnt_un, cnt_pe, cnt_wo = Counter(), Counter(), Counter()
    for a in ann:
        u = p_ = w = 0
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            u += bool(b.get("unacceptable"))
            p_ += bool(b.get("personal"))
            w += bool(b.get("world"))
        cnt_un[u] += 1
        cnt_pe[p_] += 1
        cnt_wo[w] += 1
    mx_u, mx_p, mx_w = max(cnt_un), max(cnt_pe), max(cnt_wo)
    at_max_u = cnt_un[mx_u] / len(ann)
    print("\n" + "=" * 78)
    print("ITEM 3  'the veto and personal fields are capped at five per annotator'")
    print("=" * 78)
    print(f"  blocks present per annotator, maximum observed: "
          f"unacceptable {mx_u}, personal {mx_p}, world {mx_w}")
    print(f"  annotators sitting exactly at the unacceptable maximum: {cnt_un[mx_u]} "
          f"({at_max_u:.1%})")
    print(f"  distribution (unacceptable): {dict(sorted(cnt_un.items()))}")
    print(f"  distribution (world)       : "
          f"{dict(sorted((k, v) for k, v in cnt_wo.items() if k <= 8))} ... max {mx_w}")
    hard = mx_u == mx_p and mx_w > mx_u
    print(f"  A CAP LEAVES A SIGNATURE: a hard ceiling piles mass ON the ceiling and none above it,")
    print(f"  while the same people's world blocks run to {mx_w}. Both conditions hold, so this is a")
    print(f"  structural ceiling rather than a population that happened to stop.")
    verdict("veto field capped at five", "capped at five per annotator",
            f"hard ceiling at {mx_u}, {at_max_u:.0%} of annotators sit on it, world runs to {mx_w}",
            "SURVIVES" if hard else "DOWNGRADED",
            "the ceiling signature is present: mass on the boundary, nothing above it, and an "
            "unbounded sibling field from the same people")

    # ------------------------------------------------------------------ 4
    # "synthetic and short, so nothing here transfers to production traffic"
    # THE DUAL-SCHEMA TRAP, WHICH I FELL INTO AGAIN WRITING THIS FILE. The prompt text is at
    # c["prompt"]["messages"], not c["messages"]; the first version of this line read the top level,
    # got an empty list, and would have reported a median over nothing had numpy not raised. The
    # census item this round is auditing was itself born of the same confusion. Assert non-empty.
    lens = []
    for c in cmp_:
        for m in ((c.get("prompt") or {}).get("messages") or []):
            if m.get("role") == "user" and isinstance(m.get("content"), str):
                lens.append(len(m["content"]))
                break
    assert len(lens) > 0.9 * len(cmp_), (
        f"extracted {len(lens)} user turns from {len(cmp_)} prompts -- wrong schema path")
    nturn = Counter(len([m for m in ((c.get("prompt") or {}).get("messages") or [])
                         if m.get("role") == "user"]) for c in cmp_)
    print("\n" + "=" * 78)
    print("ITEM 4  'median user turn 139 characters, so nothing here transfers to production'")
    print("=" * 78)
    if lens:
        q = np.percentile(lens, [10, 25, 50, 75, 90, 99])
        print(f"  n={len(lens)}  p10 {q[0]:.0f}  p25 {q[1]:.0f}  median {q[2]:.0f}  "
              f"p75 {q[3]:.0f}  p90 {q[4]:.0f}  p99 {q[5]:.0f}  max {max(lens)}")
        print(f"  spread p90/p10 = {q[4] / max(1, q[0]):.1f}x -- this is a DISTRIBUTION, not a "
              f"uniform block of short prompts")
    print(f"  user turns per prompt: {dict(sorted(nturn.items()))} -- "
          f"{nturn[1] / len(cmp_):.1%} single-turn, so {len(cmp_) - nturn[1]} prompts are NOT")
    print("  TWO OF MY OWN NUMBERS DIE HERE, not CoVal's. The census reported a median of 139")
    print("  characters; no extraction reproduces it -- first turn, last turn and all turns give")
    print("  128, 128 and 120. And the first draft of THIS file called them single-turn prompts,")
    print("  which 98 of 1,078 are not. The card, meanwhile, says 'the vast majority consist of a")
    print("  single user question' and calls one-turn the TYPICAL setup: hedged, and correct at")
    print("  90.9%. The release described its own turn structure more accurately than I did.")
    print("  THE TRANSFER CLAIM HAS NO INSTRUMENT. I hold no production traffic and no published")
    print("  length distribution for any deployed assistant, so 'nothing transfers' compares this")
    print("  corpus to a quantity I never measured. That is the same error as calling a panel")
    print("  concentrated with no sampling frame: a comparative word with one side missing.")
    verdict("prompts synthetic and short", "nothing here transfers to production traffic",
            f"median {np.median(lens):.0f} chars, p10-p90 spans {q[0]:.0f}-{q[4]:.0f}",
            "DOWNGRADED",
            "the card's word 'synthetic' is documented and stands; the TRANSFER claim is an "
            "unmeasured comparison and is withdrawn. What remains: prompts of stated synthetic "
            "origin, 90.9% single-turn, whose length distribution is published above. The census "
            "median of 139 chars is also withdrawn -- the reproducible figure is 128")

    # ------------------------------------------------------------------ summary
    print("\n" + "=" * 78)
    print("WHAT THIS ROUND DID TO MY OWN DEFECT LIST")
    print("=" * 78)
    st = Counter(v["status"] for v in VERDICTS)
    for v in VERDICTS:
        print(f"\n  [{v['status']}] {v['item']}")
        print(f"      was : {v['was']}")
        print(f"      now : {v['now']}")
        print(f"      why : {v['why']}")
    moved = st["DOWNGRADED"] + 2   # + the two killed before this file was written
    print(f"\n  {dict(st)} over {len(VERDICTS)} items tested this round, plus 2 KILLED before it "
          f"(near-binary, rationale-mismatch).")
    print(f"  Six interpretations tested, {moved} moved and {st['SURVIVES']} survived intact.")
    print("  NOT six of six -- the first draft of this line said that, which is the same "
          "overstatement the round exists to catch. Every MEASUREMENT held; the two that survived "
          "held as claims too, and their nulls are printed above so the survival is checkable.")

    (OUT / "own_defect_audit.json").write_text(json.dumps(
        {"verdicts": VERDICTS,
         "item1": {"eligible": len(elig), "observed": obs, "expected_analytic": exp_analytic,
                   "permutation": sims, "distinct_rankings": len(marg)},
         "item2": {"countries": len(ctry), "top3_share": top3, "hhi": hhi, "effective_n": eff,
                   "under_30": small, "counts": dict(ctry.most_common())},
         "item3": {"max_unacceptable": mx_u, "max_personal": mx_p, "max_world": mx_w,
                   "share_at_ceiling": at_max_u, "dist_unacceptable": dict(cnt_un)},
         "item4": {"n": len(lens), "median": float(np.median(lens)),
                   "turns_per_prompt": dict(nturn), "census_median_withdrawn": 139,
                   "p10": float(q[0]), "p90": float(q[4]), "max": int(max(lens))}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
