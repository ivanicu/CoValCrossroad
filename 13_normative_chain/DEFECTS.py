"""The consolidated defect list, generated from the five census result files, never from memory.

Five waves produced 46 checks across 23 axes. This merges them and re-orders by a dimension none of
the waves carried: WHAT A USER GETS WRONG. My severity labels answer "how bad is this for the
release"; a user needs "what will I compute incorrectly if nobody tells me". Those are different
orderings, and the second is the useful one.

Each blocking or serious item is annotated with the concrete wrong answer it produces. Anything
without a concrete wrong answer is not blocking, whatever I labelled it -- that annotation is the
discipline, not decoration.

THE CLEAN ITEMS ARE PRINTED TOO, and they are a third of the total. A defect list that shows only
defects tells a reader nothing about how hard anyone looked, and the ratio is the only evidence that
the sweep was not simply finding what it went looking for.
"""
from __future__ import annotations

import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
WAVES = {
    "r166_defect_census": "census.json",
    "r167_census_wave2": "census_wave2.json",
    "r168_census_wave3": "census_wave3.json",
    "r169_census_wave4": "census_wave4.json",
    "r170_census_wave5": "census_wave5.json",
}

# The concrete wrong answer each item produces, keyed by a distinctive fragment of its title.
# Absence from this map is itself a signal: an item nobody can name a wrong answer for does not
# belong above the fold.
WRONG_ANSWER = {
    "empty list": "Any analysis defaulting `.get(k, [])` counts 13,672 never-asked questions as "
                  "answered-zero. Veto rates come out 82.9% instead of 36.4%; a concentration ratio "
                  "comes out 5.01x instead of 2.56x. I made both errors.",
    "first batch": "The veto and personal-ranking fields are capped at five per annotator, so any "
                   "rate computed over the full corpus is diluted roughly fourfold, and any "
                   "per-person statistic on them has n=5 at most.",
    "No authorship field": "Treating the criterion pool as human normative input attributes 5,564 "
                           "lab-written seeds to participants. Any claim about 'what people wrote' "
                           "is 36% not what people wrote.",
    "no pointer to their source": "Lineage from a compiled criterion back to its source can only be "
                                  "recovered by text matching, which succeeds for 7.8% verbatim and "
                                  "30.8% at 0.80 similarity. Any claim that a criterion 'survived' "
                                  "compilation is a text-similarity guess.",
    "where the four candidate responses came from": "Nothing supports a claim about what generated "
                                                    "the candidates, so any statement about model "
                                                    "behaviour rather than about these 4,312 "
                                                    "specific texts is unfounded.",
    "UNACCEPTABLE is ranked FIRST": "Treating the veto as a hard constraint and the ranking as "
                                    "consistent with it will silently contradict itself on 4.4% of "
                                    "vetoing assessments.",
    "essentially every annotator": "Any inter-annotator agreement statistic leans hardest on the "
                                   "one prompt everyone saw -- and that prompt's text is garbled, "
                                   "so the agreement estimate is anchored on a test artefact.",
    "no rubric at all": "Joining rubrics to prompts silently drops 110 of 1,078 prompts, and they "
                        "are not a random remainder: they average 25.4 assessments against 16.1.",
    "two files with different coverage": "Reading assessments from comparisons.jsonl gives 293 "
                                         "fewer than reading them from annotators.jsonl. The two "
                                         "files are not interchangeable.",
    "disjoint id namespaces": "There is no key to join rubrics to prompts. Any pipeline assuming "
                              "one will silently produce an empty result, which reads as 'no data' "
                              "rather than as 'wrong join'.",
    "Two different message schemas": "A loader written for one file returns empty text for the "
                                     "other. Mine did, for 1,095 of 1,095 prompts, and every "
                                     "downstream feature came out constant without an error.",
    "near-binary": "Treating the -10..+10 scale as interval-valued over-weights the endpoints, "
                   "which carry 17% of all ratings.",
    "concentrated in a few countries": "Any 'collective' or 'crowd' aggregate is an aggregate over "
                                       "a panel that is 63% three countries.",
    "attributable to a single annotator": "9,684 free-text criteria are linkable to one person each, "
                                          "alongside their age, gender, country and education.",
    "synthetic and short": "Median user turn is 139 characters and the card calls the prompts "
                           "synthetic, so nothing here transfers to production traffic.",
    "leaked into the prompt text": "Eight prompts carry generation scaffolding or pretext framing. "
                                   "An annotator answering one is doing a different task, and "
                                   "nothing marks which.",
    "name a response as best": "Rationale text and ranking disagree in 12.6% of cases where "
                               "someone states plainly which response is best, so the two cannot "
                               "both be used as ground truth.",
    "same answer given twice": "Personal and world rankings are byte-identical in 52.1% of "
                               "assessments carrying both, so treating them as two independent "
                               "judgements double-counts one.",
    "identical ranking string": "Six annotators with five or more prompts submit the same ranking "
                                "every time, and nothing flags them.",
    "SLOT predicts": "Statistically real and worth nothing: a slot-only predictor scores 0.4993 "
                     "against 0.5000 chance. Do not correct for it and do not cite it as a defect "
                     "with consequences.",
}


def key_for(title: str) -> str | None:
    for k in WRONG_ANSWER:
        if k.lower() in title.lower():
            return k
    return None


def main() -> int:
    items = []
    for rnd, fn in WAVES.items():
        p = HERE / rnd / "results" / fn
        if not p.exists():
            print(f"  [missing] {rnd}/{fn} -- run that wave first")
            continue
        for f in json.loads(p.read_text()):
            f["round"] = rnd.split("_")[0]
            items.append(f)

    sev = {"BLOCKING": 0, "SERIOUS": 1, "NOTED": 2, "CLEAN": 3}
    # within a severity, an item with a named wrong answer outranks one without
    items.sort(key=lambda f: (sev.get(f["severity"], 9), key_for(f["title"]) is None, f["axis"]))

    counts = {s: sum(1 for f in items if f["severity"] == s) for s in sev}
    print(f"CoVal DEFECT LIST -- {len(items)} checks across five waves")
    print(f"  {counts['BLOCKING']} blocking, {counts['SERIOUS']} serious, "
          f"{counts['NOTED']} noted, {counts['CLEAN']} checked-clean\n")

    for s in ("BLOCKING", "SERIOUS", "NOTED", "CLEAN"):
        group = [f for f in items if f["severity"] == s]
        if not group:
            continue
        print(f"\n{'=' * 78}\n{s}  ({len(group)})\n{'=' * 78}")
        for f in group:
            print(f"\n[{f['round']} · {f['axis']}] {f['title']}")
            print(f"    measured: {f['measurement'][:300]}")
            k = key_for(f["title"])
            if k:
                print(f"    YOU GET WRONG: {WRONG_ANSWER[k]}")
            elif s in ("BLOCKING", "SERIOUS"):
                print(f"    YOU GET WRONG: (unnamed -- if no concrete wrong answer can be stated, "
                      f"this does not belong above the fold)")

    named = sum(1 for f in items if f["severity"] in ("BLOCKING", "SERIOUS")
                and key_for(f["title"]))
    total_hi = counts["BLOCKING"] + counts["SERIOUS"]
    print(f"\n{named}/{total_hi} blocking-or-serious items have a named concrete wrong answer.")
    print(f"{counts['CLEAN']}/{len(items)} checks came back clean -- the ratio is the only evidence "
          f"the sweep was not just finding what it went looking for.")
    (HERE / "DEFECTS.json").write_text(json.dumps(
        {"items": items, "counts": counts,
         "wrong_answers": {k: v for k, v in WRONG_ANSWER.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
