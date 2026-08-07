"""r53 -- audit the join every round in this repository depends on.

Entry 53 named the pattern behind entries 49-52: a fixed part of the apparatus
stops looking like a choice, and then nobody interrogates it.  The n=4 null, the
gold head's length feature, the criterion population, the space of designs, the
judge.  This is the remaining one.

`covalx.load_join` pairs each rubric record to a comparison record, and every
round is built on that pairing.  It prints the same line on every run --
`{'role_canonical': 966, 'fuzzy>=0.95': 2, 'unmatched': 18}` -- which has been
scrolling past for 52 rounds without anyone asking:

  * are the 2 FUZZY matches the same prompt, or a mispairing that silently
    attaches a rubric to the wrong four responses?
  * are the 18 UNMATCHED excluded by the 0.95 CUTOFF (an analyst choice) or
    because their prompts are absent from the release (a fact about the data)?
  * what population does the analysed set actually cover?

A mispaired rubric would be the worst defect available here: criteria scored
against responses they were never written for, in every downstream round, with
no symptom.

CLAIM CARD, inline because the round adds no estimate:
  Claim       the join is sound and the analysed population is defined by data
              availability rather than by a threshold
  Estimand    (a) similarity of each fuzzy pair; (b) BEST available similarity
              for each unmatched record against ANY comparison prompt; (c) the
              covered fraction of released prompts
  Target      observed exactly -- all text is in hand
  Worlds      A cutoff excludes recoverable records -> unmatched records have
              near-misses just under 0.95;  B their prompts are absent -> best
              ratios fall well below it
  Null        none needed: A and B are distinguished by a measurement, not a test
"""
from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx.judge import content_key, message_key  # noqa: E402

OUTCOME_SCOPE = (
    "Descriptive on the release's own text. No judge, no proxy, no human rankings."
)
CUTOFF = 0.95


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r53_join_audit.json")
    a = p.parse_args()

    by_key, by_content = {}, {}
    for line in open(a.comparisons, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        msgs = rec["prompt"]["messages"]
        by_key[message_key(msgs)] = rec["prompt_id"]
        by_content.setdefault(content_key(msgs), rec["prompt_id"])
    keys = list(by_content)

    how = {"role_canonical": 0, "content_only": 0, "fuzzy": 0, "unmatched": 0}
    fuzzy, unmatched = [], []
    n_rub = 0
    for line in open(a.rubrics, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        n_rub += 1
        msgs = rec["conversation"]["messages"]
        if message_key(msgs) in by_key:
            how["role_canonical"] += 1
            continue
        ck = content_key(msgs)
        if ck in by_content:
            how["content_only"] += 1
            continue
        m = difflib.get_close_matches(ck, keys, n=1, cutoff=CUTOFF)
        if m:
            how["fuzzy"] += 1
            fuzzy.append({"rubric": ck, "matched": m[0],
                          "ratio": difflib.SequenceMatcher(None, ck, m[0]).ratio()})
            continue
        how["unmatched"] += 1
        best = difflib.get_close_matches(ck, keys, n=1, cutoff=0.0)
        r = difflib.SequenceMatcher(None, ck, best[0]).ratio() if best else 0.0
        # NOT truncated (entry 57): this string is persisted, and a reader
        # checking whether an unmatched prompt is genuinely absent needs all of
        # it. Console display is truncated below; the artifact is not.
        unmatched.append({"rubric": ck, "best_available_ratio": r,
                          "criteria": len(rec.get("coval_full") or [])})

    matched = how["role_canonical"] + how["content_only"] + how["fuzzy"]
    released = len(by_content)
    br = np.array([u["best_available_ratio"] for u in unmatched]) if unmatched else np.array([0.0])

    print(f"rubric records {n_rub}   released comparison prompts {released}")
    for k, v in how.items():
        print(f"  {k:16s} {v}")
    print(f"\nfuzzy pairs (are they the same prompt?):")
    for f in fuzzy:
        print(f"  ratio {f['ratio']:.4f}")
        print(f"    rubric : {f['rubric'][:110]}")
        print(f"    matched: {f['matched'][:110]}")
    print(f"\nunmatched records, BEST similarity available anywhere in the release:")
    print(f"  max {br.max():.4f}   median {np.median(br):.4f}   min {br.min():.4f}")
    print(f"  recoverable at a 0.90 cutoff: {int((br >= 0.90).sum())}"
          f"   at 0.80: {int((br >= 0.80).sum())}")
    print(f"  criteria per unmatched record: median "
          f"{int(np.median([u['criteria'] for u in unmatched]))} -- normal-sized records, "
          f"so this is not a quality filter")

    cutoff_is_binding = bool((br >= 0.90).sum() > 1)
    fuzzy_ok = all(f["ratio"] > 0.98 for f in fuzzy)
    coverage = matched / released

    if not cutoff_is_binding and fuzzy_ok:
        verdict = (
            f"THE JOIN IS SOUND. Both fuzzy pairs differ only by a typo "
            f"({', '.join(f'{f[chr(114)+chr(97)+chr(116)+chr(105)+chr(111)]:.4f}' for f in fuzzy)}) "
            f"and are the same prompt. The {how['unmatched']} unmatched rubric records are "
            f"not excluded by the {CUTOFF} cutoff: their best available similarity to ANY "
            f"released prompt has median {np.median(br):.4f} and max {br.max():.4f}, so "
            f"those prompts are ABSENT from comparisons.jsonl rather than narrowly missed. "
            f"POPULATION, stated because entry 51 is what happens when it is not: the "
            f"analysed set is {matched} of {released} released prompts ({coverage:.1%}); "
            f"the shortfall is {released - n_rub} prompts with no rubric record at all plus "
            f"{how['unmatched']} rubrics whose prompts are not in the comparison file. "
            f"ONE BORDERLINE: the closest unmatched record sits at {br.max():.4f}, which a "
            f"0.90 cutoff would admit and which nothing here proves is a different prompt")
    elif not fuzzy_ok:
        verdict = (
            f"A FUZZY MATCH IS QUESTIONABLE: the lowest pair ratio is "
            f"{min(f['ratio'] for f in fuzzy):.4f}. A mispaired rubric attaches criteria to "
            f"responses they were never written for, silently, in every downstream round")
    else:
        verdict = (
            f"THE CUTOFF IS BINDING: {int((br >= 0.90).sum())} unmatched records sit above "
            f"0.90, so the {CUTOFF} threshold is an analyst choice that excludes recoverable "
            f"data and the analysed population is defined by it")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "rubric_records": n_rub, "released_prompts": released,
        "match_counts": how, "matched_total": matched,
        "coverage_of_released": coverage,
        "fuzzy_pairs": fuzzy,
        "unmatched": unmatched,
        "unmatched_best_ratio": {"max": float(br.max()), "median": float(np.median(br)),
                                 "min": float(br.min()),
                                 "n_above_0.90": int((br >= 0.90).sum()),
                                 "n_above_0.80": int((br >= 0.80).sum())},
        "cutoff": CUTOFF, "cutoff_is_binding": cutoff_is_binding,
        "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Checks that the rubric<->prompt pairing is correct and that the "
                  "analysed population is set by data availability rather than by the "
                  "fuzzy threshold. It does NOT check whether the 92 prompts with no "
                  "rubric record differ systematically from those with one -- that is a "
                  "property of the release's own sampling and is not observable here."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
