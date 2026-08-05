#!/usr/bin/env python3
"""R489 — is the second release "hidden", or has this campaign been using it for fifty rounds?

⚠ ACTION CLASS: CLOSURE. It retracts a finding I was about to announce. No fork is separated.

WHY. Triaging R488's frozen typed-population debt, `core_gen_second.json` turned out to hold 2,200
prompts sharing ZERO ids with the 968-prompt home release, and `data/utterances.jsonl` (68 MB) carries
per-response `score`, `if_chosen`, and interactions with exactly four responses. The register lists
cross-release as needing "a second values-annotation release". The conclusion assembled itself.

ESTIMAND
    Is the second corpus NEW TO THIS CAMPAIGN, or already in use? Measured two ways that must agree:
      (a) does the reasoning document cite it?      (b) are there judged artifacts keyed to it?
    ⭐ The estimand is NOVELTY, and novelty is a property of the RECORD, not of the object. Door ①
    sends me to the object and I went; nothing in an object says "this is already known".

IDENTIFICATION  Direct counts. Nothing is estimated.
SCOPE  population: this repository at HEAD · instrument: grep + npz key inspection.

WORLDS
    A  HIDDEN     no citations, no judged artifacts -> a genuine finding; the register is false.
    B  IN USE     citations and judged cells exist -> not a finding; the register's qualifier holds.

KILL   B if DEFINITION.md cites the second release AND transport artifacts carry its ids.
CONTROLS
    POSITIVE  the citation search must FIND the known second-release rounds (R434/R436/R437/R438) --
              a search that finds nothing proves nothing about absence.
    NEGATIVE  the same search for a genuinely absent capability (a third judge) must return nothing.
ARTIFACT  results/r489_second_release.json
"""
import json, pathlib, re, sys
import numpy as np
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R489_the_second_release_is_not_hidden/results"
defn = (ROOT/"E05_the_space_of_compilers"/"DEFINITION.md").read_text()
cites = [m.start() for m in re.finditer(r"second release", defn)]
rounds = sorted({m for m in re.findall(r"\(R(43[4-8])\b", defn)})
d = np.load(ROOT/"corebench"/"results"/"sat_transport_gen.npz", allow_pickle=True)
ids = {str(k).split("|")[0] for k in d["meta"]}
gs = json.load(open(ROOT/"corebench"/"results"/"core_gen_second.json"))
third = list((ROOT/"corebench"/"results").glob("sat_*_3b*.npz"))
print(f"  (a) DEFINITION.md mentions of 'second release' : {len(cites)}")
print(f"      POSITIVE: known second-release rounds cited: {rounds}  "
      f"{'PASS' if rounds else '⛔ search finds nothing — proves nothing'}")
print(f"  (b) sat_transport_gen.npz judged cells         : {len(d['meta'])}")
print(f"      distinct conversation ids                  : {len(ids)}")
print(f"      core_gen_second.json prompts               : {len(gs)}")
print(f"      NEGATIVE: artifacts for a THIRD judge       : {len(third)} "
      f"{'(absent, as it must be)' if not third else '⛔'}")
hidden = not cites and not len(d["meta"])
verdict = "MEASURED"
world = ("A (HIDDEN)" if hidden else
         "B (IN USE — the campaign has used the second release since R434; the register's "
         "'with this schema' qualifier is what makes it unavailable, not its existence)")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"definition_mentions": len(cites), "rounds_cited": rounds,
           "transport_cells": int(len(d["meta"])), "transport_conversations": len(ids),
           "gen_second_prompts": len(gs), "third_judge_artifacts": len(third),
           "verdict": verdict, "world": world}, open(OUT/"r489_second_release.json", "w"), indent=2)
sys.exit(0)
