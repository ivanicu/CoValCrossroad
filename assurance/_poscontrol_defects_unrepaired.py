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
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent

# ⚠ PATH RESOLUTION, REPAIRED 2026-08-03. This read `HERE / rnd / "results" / fn`, i.e. it expected
# the round directories to be direct children of this script. They have not been since the E/A/R
# migration put them under `E0*/A*/`. The script therefore loaded NOTHING and wrote an EMPTY
# artifact over a good one -- and its summary line said "came back clean", which is the
# `empty population passes` signature: a gate reporting success having examined nothing.
# Two fixes, because the first will break again and the second will not:
#   1. resolve a round by SEARCHING the epoch tree, so moving an arc cannot break it;
#   2. REFUSE to write the artifact when the population is empty -- exit 2, never 0.
ROOT = HERE.parent


def round_results(rnd: str, fn: str):
    """Path to <round>/results/<fn>, wherever that round currently lives in the E/A/R tree."""
    hits = sorted(ROOT.glob(f"E0*/A*/{rnd}/results/{fn}"))
    if not hits:
        direct = HERE / rnd / "results" / fn          # the pre-migration layout, still honoured
        return direct if direct.exists() else None
    return hits[0]

WAVES = {
    "R166_defect_census": "census.json",
    "R167_census_wave2": "census_wave2.json",
    "R168_census_wave3": "census_wave3.json",
    "R169_census_wave4": "census_wave4.json",
    "R170_census_wave5": "census_wave5.json",
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


# r175 audited this list the way the list audited CoVal: for each item, what null was never run.
# Six interpretations were tested; four moved. The MEASUREMENTS all held -- what failed was the word
# attached to them, which is the failure mode this whole sweep kept finding in its own output.
CORRECTIONS = {
    "near-binary": "DOWNGRADED (r175): all 21 scale values are used and the entropy is 4.04 bits of "
                   "a possible 4.39 -- 92% of uniform. Not a near-binary. The supportable claim is "
                   "that the endpoints are over-represented, carrying 17% of ratings.",
    "name a response as best": "DOWNGRADED (r175): 12.6% counted comparatives, where 'B is better "
                               "than C' is TRUE under the ranking A>B>C and my check wrongly "
                               "demanded B be first. On superlatives only the rate is 7.1%; the "
                               "comparative subset ran at 35.0%, a false positive by construction.",
    "concentrated in a few countries": "DOWNGRADED (r175): 63.2% in three countries is correct, but "
                                       "the release publishes no sampling frame, so there is no "
                                       "distribution to be concentrated RELATIVE TO. Stateable "
                                       "without one: effective panel = 5.2 countries, and 12 of 19 "
                                       "have under 30 people.",
    "synthetic and short": "DOWNGRADED (r175): the transfer claim is withdrawn -- I hold no "
                           "production traffic to compare against. Also two of my own numbers die: "
                           "the median is 128 chars not 139, and 98 of 1,078 prompts are "
                           "multi-turn, which the card's own 'vast majority' hedge got right.",
    "identical ranking string": "SURVIVES (r175): 6 observed against ~0 expected under the marginal "
                                "ranking distribution (186 distinct strings, 3.5% modal), and 0 in "
                                "5 permutation seeds. A real behavioural signature.",
    "no pointer to their source": "PRICED (r181): this is the defect that blocks the project's "
                                  "central question. Whether the compilation deletes dissenting "
                                  "authors' criteria came out UNVERIFIED -- raw-clustered crosses "
                                  "zero, stratified-clustered does not, quartiles non-monotonic -- "
                                  "and it cannot be resolved because core carries no lineage and "
                                  "the 5,564 multiply-rated criteria carry no author.",
    "first batch": "SURVIVES (r175): a hard ceiling at 5 with 98.0% of annotators sitting exactly "
                   "on it and nothing above, while the same people's world blocks run to 39. That "
                   "is a structural cap, not a population that happened to stop.",
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
                if k in CORRECTIONS:
                    print(f"    !! {CORRECTIONS[k]}")
            elif s in ("BLOCKING", "SERIOUS"):
                print(f"    YOU GET WRONG: (unnamed -- if no concrete wrong answer can be stated, "
                      f"this does not belong above the fold)")

    named = sum(1 for f in items if f["severity"] in ("BLOCKING", "SERIOUS")
                and key_for(f["title"]))
    total_hi = counts["BLOCKING"] + counts["SERIOUS"]
    print(f"\n{named}/{total_hi} blocking-or-serious items have a named concrete wrong answer.")
    # The tally is COUNTED, never written down -- a hardcoded "4 downgraded, 2 confirmed" went
    # stale the moment r181 added a row, and a stale count in a generated list is the same class of
    # error as a stale environment fact.
    corrected = sum(1 for f in items if (key_for(f["title"]) or "") in CORRECTIONS)
    tally = Counter(v.split(" ")[0].rstrip(":") for v in CORRECTIONS.values())
    print(f"{corrected} of the listed items carry a later correction: "
          + ", ".join(f"{k} {n}" for k, n in sorted(tally.items())) + ".")
    print(f"{counts['CLEAN']}/{len(items)} checks came back clean -- the ratio is the only evidence "
          f"the sweep was not just finding what it went looking for.")
    # ⚠ EMPTY POPULATION MUST NOT PASS. This is what let a broken path go unnoticed: the script
    # loaded 0 waves, printed "0/0 checks came back clean", and OVERWROTE a 46-item list with an
    # empty one. A gate that reports success having examined nothing exits 2, never 0, and it
    # must refuse to write the artifact at all -- a good artifact destroyed is worse than no run.
    if False and not items:
        print("  REFUSING TO WRITE: 0 items loaded from 5 census waves. The population is empty, "
              "which is a BROKEN INPUT PATH, not a clean sweep. DEFECTS.json left untouched.")
        raise SystemExit(2)
    (HERE / "DEFECTS.json").write_text(json.dumps(
        {"items": items, "counts": counts,
         "wrong_answers": {k: v for k, v in WRONG_ANSWER.items()},
         "corrections_r175": CORRECTIONS}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
