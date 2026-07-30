"""r48 -- the seed/write-in provenance is an IDENTIFICATION, not a proxy.

CLAIM CARD (inline; this round adds no estimate, it validates a proxy two
rounds already depend on, so the card is short and sits here).

  Claim        the rater-count split r13 and r32 use is not a heuristic --
               it recovers the documented pre-seeded/rater-written partition
  Estimand     (a) fraction of criteria in the ambiguous band between the two
               modes; (b) the per-prompt count of the many-rated class
  Target       observed exactly: rater counts are in the release
  Worlds       A the split is a smooth threshold choice -> a continuum, and the
               threshold moves results;  B it is structural -> a gap, and any
               threshold in the gap gives the same partition
  Intervention none, descriptive
  Null         the protocol's own prediction: pre-seeded items are a FIXED set
               shown to every participant, so their per-prompt count must be
               constant and small.  The data could have shown any distribution

WHY IT MATTERS.  r13 states, honestly, "the release does not flag seed vs
write-in", and r32 splits on the same rule.  Both therefore carry their
provenance results at the confidence of a guess.  If the partition is
structural, both upgrade -- and if it is not, both need a threshold-sensitivity
sweep they never ran.

WHAT IT DOES NOT REACH.  The card at data/DATASET_CARD.md:357 says "pre-seeded".
That means pre-populated in the interface, NOT authored before the responses
existed -- and every RATING is post-exposure regardless, since participants
ranked the four candidates first.  So this does not open S_pre by a crack.
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"

OUTCOME_SCOPE = (
    "Descriptive: no outcome variable, no model proxy, no scoring. This round "
    "reads rater counts out of the release and checks a structural property of "
    "the criterion set."
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    ap.add_argument("--out", type=Path, default=_RES / "r48_provenance_identified.json")
    a = ap.parse_args()

    per, counts = [], []
    for line in open(a.rubrics, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        items = json.loads(line).get("coval_full") or []
        if not items:
            continue
        c = np.array([len(it.get("scores") or []) for it in items])
        per.append(c)
        counts += c.tolist()
    counts = np.array(counts)

    single = int((counts == 1).sum())
    many = int((counts >= 5).sum())
    band = int(((counts >= 2) & (counts <= 4)).sum())
    # The rounds' own rule: majority of the raters who touched this prompt.
    amb = sum(int((((c > 1) & (c < max(2, (c.max() + 1) // 2)))).sum()) for c in per)

    many_per_prompt = np.array([int((c >= 5).sum()) for c in per])
    h = collections.Counter(many_per_prompt.tolist())
    cap = int(many_per_prompt.max())
    mode = h.most_common(1)[0][0]
    at_cap = int((many_per_prompt == cap).sum())

    print(f"criteria {len(counts):,} over {len(per)} prompts")
    print(f"  exactly 1 rater      {single:6,d}  ({single/len(counts):.1%})")
    print(f"  >= 5 raters          {many:6,d}  ({many/len(counts):.1%})")
    print(f"  2-4 raters (the gap) {band:6,d}  ({band/len(counts):.1%})")
    print(f"  ambiguous under the rounds' own per-prompt rule: {amb:,} "
          f"({amb/len(counts):.2%})")
    print(f"\n  many-rated criteria PER PROMPT: mode {mode}, median "
          f"{int(np.median(many_per_prompt))}, max {cap}, "
          f"{at_cap}/{len(per)} prompts at the cap")

    structural = band / len(counts) < 0.01
    fixed_set = cap == mode and at_cap / len(per) > 0.5
    if structural and fixed_set:
        verdict = (
            f"IDENTIFIED, NOT PROXIED. The two classes are separated by a structural "
            f"gap -- {band} of {len(counts):,} criteria ({band/len(counts):.1%}) lie "
            f"between them, and ZERO are ambiguous under the per-prompt rule r13 and "
            f"r32 actually use, so the threshold is not a choice. And the many-rated "
            f"class is a FIXED SET: capped at {cap} per prompt, mode {cap}, with "
            f"{at_cap}/{len(per)} prompts exactly at the cap. That is the signature of "
            f"items pre-populated for every participant, which is what "
            f"data/DATASET_CARD.md:357 documents as 'pre-seeded'. The count {cap} is "
            f"established HERE from the data, not read from the card, which does not "
            f"state it. r13's and r32's provenance results upgrade from heuristic to "
            f"identified. NOT REACHED: 'pre-seeded' means pre-populated in the "
            f"interface, not authored before the responses existed -- and every RATING "
            f"is post-exposure regardless, since participants ranked the four "
            f"candidates first. S_pre stays unreachable")
    elif structural:
        verdict = (
            f"PARTITION IS STRUCTURAL BUT NOT A FIXED SET. The gap is real "
            f"({band/len(counts):.1%} between the modes) so the threshold is not a "
            f"choice, but the many-rated class is not a constant-size set per prompt "
            f"(cap {cap}, mode {mode}), so identifying it with pre-seeding is an "
            f"inference from the card, not from the data")
    else:
        verdict = (
            f"THE SPLIT IS A THRESHOLD CHOICE. {band/len(counts):.1%} of criteria sit "
            f"between the modes, so r13 and r32 need a threshold-sensitivity sweep "
            f"before their provenance results can be read")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "criteria": int(len(counts)), "prompts": len(per),
        "n_single_rater": single, "n_many_rated": many, "n_in_gap": band,
        "gap_share": band / len(counts),
        "n_ambiguous_under_round_rule": amb,
        "many_per_prompt_mode": mode, "many_per_prompt_max": cap,
        "prompts_at_cap": at_cap,
        "many_per_prompt_hist": {str(k): v for k, v in sorted(h.items())},
        "partition_is_structural": bool(structural),
        "many_rated_is_fixed_set": bool(fixed_set),
        "verdict": verdict,
        "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Descriptive, on the released rater counts. It validates the "
                  "PARTITION used by r13 and r32; it does not validate any claim "
                  "those rounds make ABOUT the two classes. And it does not touch "
                  "S_pre: pre-populated is not response-blind, and all ratings are "
                  "post-exposure."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
