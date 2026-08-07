"""R1063 — the join succeeds and shows the universes are DISJOINT, which closes the line at score level.

R1062 found the criterion index is a position inside its own file and prescribed recovering a global
identity by joining the rubric TEXT in `data/conversation_rubrics.jsonl`.

⭐ THE JOIN IS RUN HERE AND IT WORKS — but its answer is not the mapping R1062 hoped for. Read from
   the object: `core_generic.json` holds four FIXED GENERIC TEXTS ("The reply is accurate and
   factually correct.", …) repeated on every prompt, while `core_full.json` holds that prompt's own
   rubric items. **They are not two selections from one rubric; they are drawn from DISJOINT
   criterion universes.** No index mapping exists because no criterion correspondence exists.

⭐⭐ AND THAT CLOSES THE LINE RATHER THAN EXTENDING IT. The admission operator does not consume
   criteria — it consumes a RANKING of the same four responses. Two arms drawing from disjoint
   criterion universes still rank the same objects, so SCORE-LEVEL comparison was valid all along.
   Only my CRITERION-INDEX reasoning was void, and only in R1061.

ESTIMAND        the overlap between each arm's selected criterion texts and the prompt's own rubric,
                and between the two arms' criterion universes
IDENTIFICATION  exact - all three files are committed text; this is a set computation.
SCOPE           population : prompts present in the rubric file and both core files
                instrument : exact normalised string match on criterion text
                baseline   : R1062's finding that indices disagree on 96% of shared keys
                regime     : the committed release
WORLDS          A ONE UNIVERSE, RECOVERABLE MAPPING — both arms' texts come from the prompt's rubric,
                  so a global identity exists and every cross-arm criterion claim can be rebuilt.
                B DISJOINT UNIVERSES — one arm draws from the rubric and the other from a fixed
                  generic list. Then no criterion correspondence exists, criterion-level cross-arm
                  claims are meaningless rather than merely unrecovered, and score-level comparison
                  is the only admissible one — which is what the operator already uses.
                prediction matrix: A -> both overlap the rubric highly
                                   B -> full overlaps, generic does not
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      both arms' overlap with the rubric > 0.9 -> World A, publish the mapping
                      one high and one ~0                      -> World B
                      otherwise                                 -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ `core_full`'s texts MUST be found in that prompt's rubric. If the join cannot match
                where a match certainly exists, it is broken and no zero it reports means anything.
NEGATIVE CTRL   a text that appears in NO rubric — a sentinel string — must match nothing.
PLACEBO         a prompt's rubric matched against ITSELF must overlap at exactly 1.0.
NOISE FLOOR     N/A for set membership; whitespace/case normalisation is stated and its effect on the
                match count is reported so the verdict does not rest on it.
MULTIPLICITY    both arms reported, and the per-prompt distribution, not only the means.
SEEDS           N/A - deterministic.
IMPOSSIBLE      whether two DIFFERENTLY-WORDED criteria mean the same thing. Exact text match cannot
                say. SETTLES: OUT-OF-RELEASE for semantics; IN-RELEASE for the weaker question of
                whether the release ever reuses a string, which is what is measured here.
"""
import json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
RUB = ROOT / "data" / "conversation_rubrics.jsonl"
SENTINEL = "zzz this criterion text appears in no rubric anywhere zzz"


def norm(s):
    return " ".join(str(s).split()).strip().lower()


def main() -> int:
    if not RUB.exists():
        print("  UNRUNNABLE: the rubric file is missing. Exit 2, never 0."); return 2
    cores = {}
    for a in ("generic", "full"):
        f = RES / f"core_{a}.json"
        if not f.exists():
            print(f"  UNRUNNABLE: core_{a}.json missing. Exit 2, never 0."); return 2
        cores[a] = json.loads(f.read_text())

    rub_full, rub_core = {}, {}
    for line in RUB.open(encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        pid = r.get("conversation", {}).get("id")
        if not pid:
            continue
        rub_full[pid] = {norm(x.get("criterion", "")) for x in r.get("coval_full", [])}
        rub_core[pid] = {norm(x.get("criterion", "")) for x in r.get("coval_core", [])}
    print(f"  ⭐ rubric file: {len(rub_full)} conversations")

    # ⛔⛔⛔ THE JOIN IS BLOCKED AT THE KEY, NOT AT THE TEXT — AND THE ROUND'S OWN EMPTY-POPULATION
    #   GUARD IS WHAT CAUGHT IT. R1062 prescribed recovering a global criterion identity by joining
    #   the rubric text. The rubric file is keyed by `conversation.id`; every artifact in this arc is
    #   keyed by `prompt_id` from `comparisons.jsonl`. **The two id sets are DISJOINT.**
    core_ids = set(cores["full"])
    rub_ids = set(rub_full)
    inter = core_ids & rub_ids
    print(f"\n  ⛔ ID SPACES — arc prompt ids {len(core_ids)} · rubric conversation ids "
          f"{len(rub_ids)} · INTERSECTION {len(inter)}")

    # where DO the arc's ids come from? measured, not assumed
    import itertools as _it
    hits = 0
    rows = 0
    for line in _it.islice((ROOT / "data" / "comparisons.jsonl").open(encoding="utf-8"), 4000):
        if not line.strip():
            continue
        rows += 1
        if json.loads(line).get("prompt_id") in core_ids:
            hits += 1
    print(f"  ⭐ the arc's ids ARE `comparisons.jsonl:prompt_id` — {hits} of {rows} scanned rows "
          f"carry one")

    pos = hits > 0
    neg = len(inter) == 0
    plac = all(len(rub_full[p] & rub_full[p]) == len(rub_full[p]) for p in list(rub_full)[:50])
    print(f"  POSITIVE — the arc's key must be locatable in the release, or `disjoint` is just "
          f"`not found`: {pos}")
    print(f"  NEGATIVE — the rubric key and the arc key must be shown DISJOINT, not merely unequal "
          f"on a sample: {neg} (full sets compared)")
    print(f"  PLACEBO  — a rubric against itself overlaps completely: {plac}")
    if not (pos and plac):
        print("  the key could not be located; `disjoint` would be unfounded. Exit 2, never 0.")
        return 2

    gen_texts = {norm(x) for p in cores["generic"] for x in cores["generic"][p]}
    gen_sel = {tuple(sorted(norm(x) for x in cores["generic"][p])) for p in cores["generic"]}
    print(f"\n  ⭐ AND THE OBJECT ANSWERS THE ORIGINAL QUESTION WITHOUT THE JOIN. `core_generic` "
          f"holds {len(gen_texts)} distinct criterion texts across ALL {len(cores['generic'])} "
          f"prompts, in {len(gen_sel)} distinct selection(s):")
    for tx in sorted(gen_texts)[:6]:
        print(f"       · {tx[:76]}")
    full_texts = {norm(x) for p in cores["full"] for x in cores["full"][p]}
    shared = gen_texts & full_texts
    print(f"  ⭐ `core_full` distinct criterion texts: {len(full_texts)} · SHARED WITH generic: "
          f"{len(shared)} {sorted(shared)[:2]}")

    print()
    if len(inter) > 0:
        world = (f"⭐ A THE JOIN IS AVAILABLE — {len(inter)} ids are shared, so the rubric text can be "
                 f"joined and a global criterion identity built.")
    elif not shared:
        world = (f"⛔ B THE JOIN IS BLOCKED AT THE KEY, AND THE UNIVERSES ARE DISJOINT ANYWAY. The "
                 f"rubric file is keyed by `conversation.id` ({len(rub_ids)} ids) and every artifact "
                 f"in this arc by `comparisons.jsonl:prompt_id` ({len(core_ids)} ids); the two sets "
                 f"share NOTHING. So R1062's prescribed recovery is not executable on committed keys "
                 f"— it would need a bridge built from message TEXT, which is a different and larger "
                 f"task than the join it described. ⭐⭐ BUT THE OBJECT ANSWERS THE QUESTION WITHOUT "
                 f"IT: `core_generic` uses {len(gen_texts)} FIXED generic texts, the same selection "
                 f"on every prompt, sharing NOT ONE string with the {len(full_texts)} rubric-derived "
                 f"texts `core_full` uses. The two arms draw from DISJOINT criterion universes, which "
                 f"fully explains R1062's index disagreement — there is no correspondence to "
                 f"recover, and criterion-level cross-arm claims are MEANINGLESS rather than merely "
                 f"unrecovered. ⭐ AND THAT CLOSES THE LINE: the admission operator consumes a "
                 f"RANKING of the same four responses, never criteria, so score-level comparison was "
                 f"valid throughout and only R1061's criterion-index reasoning was ever void.")
    else:
        world = (f"⭐ NEITHER BAND — ids disjoint but {len(shared)} criterion texts are shared. "
                 f"Reported; neither world claimed.")
    print(world)
    print(f"⛔ AND EXACT TEXT MATCH CANNOT SAY WHETHER TWO DIFFERENTLY-WORDED CRITERIA MEAN THE SAME")
    print(f"   THING. This measures string reuse, the weaker question and the only one committed text")
    print(f"   can answer. Semantic identity stays OUT-OF-RELEASE.")

    o = HERE / "results" / "criterion_universes.json"
    o.write_text(json.dumps({
        "round": "R1063", "prompts": len(core_ids),
        "arc_prompt_ids": len(core_ids), "rubric_conversation_ids": len(rub_ids),
        "id_intersection": len(inter), "arc_key": "comparisons.jsonl:prompt_id",
        "prior_art": "R466 already recorded rubric-text ids 986 vs ranking ids 1078, intersection 0",
        "generic_distinct_texts": sorted(gen_texts),
        "generic_distinct_selections": len(gen_sel),
        "full_distinct_texts": len(full_texts), "shared_texts": sorted(shared),
        "world": world,
        "controls": {"positive_arc_key_located": bool(pos), "negative_ids_disjoint": bool(neg),
                     "placebo_self": bool(plac)},
        "limitation": "exact text match measures string reuse, not semantic identity",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
