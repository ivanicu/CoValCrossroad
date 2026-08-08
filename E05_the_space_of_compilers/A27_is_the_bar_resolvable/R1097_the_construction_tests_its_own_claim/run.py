#!/usr/bin/env python3
"""R1097 — ⛔ R1096's "one file away" is RETRACTED. `prompt-blind` has two referents and they differ.

R1096 concluded that a comparator both CERTIFIABLE and DISJOINT from the candidates is one committed
selection file away, on the strength of a SHAM: give a constructed subset the artifact the rule reads
and it certifies. Its NEXT was to build the real thing. **Building it is what killed the claim.**

⛔⛔ THE SHAM WAS VALIDATED AGAINST A STRING I INVENTED. It wrote `f"criterion {i}"` -- the SAME text
    on every prompt -- so of course the rule saw one distinct selection and certified it. The REAL
    selection of a blind subset is not constant: `core_full.json` shows each prompt carries its own
    rubric TEXT, so selecting fixed INDICES {0,1,2} yields a different criterion set on every prompt.
    §4's *a control validated only against cases you invented is validated against your imagination*,
    committed one round ago and caught by attempting the construction.

⭐ AND THE STRUCTURAL FACT UNDERNEATH IS THE THIRD OF ITS KIND IN THIS ARC. `prompt-blind` has two
   referents and the arc has been using both:
     INDEX-BLIND  the same POSITIONAL selection on every prompt. R1057's 15 subsets are blind here,
                  and it verified exactly that (`one selection per comparator, every prompt`).
     TEXT-BLIND   the same criterion STRINGS on every prompt. `generic` is blind here.
   R1056's certification rule types TEXT. **So the certified family (2) and the synthetic family (15)
   are blind in DIFFERENT SENSES, and every cross-family statement in this arc has been carrying that
   seam.** R1094 found the same shape in clause ③'s two readings; R1091/R1092 found it in a wall.

ESTIMAND        (Q1) for index-blind subsets, the number of distinct criterion-TEXT selections over
                     the 968 prompts -- the quantity R1056's rule actually types.
                (Q2) the same for `generic` (text-blind) and `full` (maximally specific), as the two
                     poles that calibrate Q1.
                (Q3) the sham, restored: does the rule certify a constructed subset when given its
                     REAL selection rather than an invented constant?
IDENTIFICATION  exact over committed files; no join to the rubric release is needed, and none is
                available -- `conversation_rubrics.jsonl` keys on a CONVERSATION id whose overlap
                with the 968 scored prompt_ids is 0, while `comparisons.jsonl` overlaps at 968.
UNIT OF THE     a comparator, and its distinct-TEXT-selection count.
  INSTRUMENT
UNIT OF THE     the same. ⚠ `prompt-blind` is the term whose unit is contested; the round reports
  CLAIM         both readings rather than choosing.
SCOPE           population: the 968 scored prompts and the committed `core_*.json` selections.
                instrument: R1056's own diversity statistic. baseline: `generic` at 1.
WORLDS          A BOOKKEEPING  the real selection certifies, so R1096 stands and a file is enough.
                B TWO SENSES   the real selection is text-diverse, so an index-blind comparator can
                               never certify under a text-typing rule, and R1096's claim falls.
                Prediction matrix on distinct-text-selections for an index-blind subset:
                  A -> 1        B -> ~968, i.e. indistinguishable from `full`
KILL            pre-registered. World A is KILLED if an index-blind subset's real selection has more
                than 1 distinct text selection. One is enough: the rule's strict cell is `<= 1`.
POSITIVE CTRL   `generic` must return exactly 1 -- it is R918's `fixed` set and the rule's own
                anchor. If it does not, the statistic is not the one R1056 computed.
g=0 GUARD       `full` must return 968 -- the maximally prompt-specific pole. Without both poles the
                middle is uncalibrated.
NEGATIVE CTRL   the result must hold for MORE THAN ONE index set, or it is a property of one subset
                rather than of index-blindness.
SHAM            R1096's invented constant string, re-run beside the real selection: the fake must
                certify and the real must not. That contrast IS the retraction, made computable.
PLACEBO         re-reading a selection file returns an identical count.
NOISE FLOOR     none; these are counts over committed files.
MULTIPLICITY    three index sets reported, plus both poles.
SPECIFICATION   index set in {(0,), (0,1,2), (0,1,2,3)} x selection in {real, invented}.
ARTIFACT        results/two_senses_of_blind.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      a comparator that is TEXT-blind and NOT an arm -- ⚠ this is the corrected register
                entry. Text-blindness over prompts with prompt-specific rubrics means a FIXED
                EXTERNAL criterion set, which is exactly what `generic` is -- and `generic` is an
                arm. What it would require: a fixed external rubric committed as a comparator and
                excluded from candidacy, which the release does not ship.
"""
from __future__ import annotations

import hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "two_senses_of_blind.json"
RES = ROOT / "corebench" / "results"
IDXS = [(0,), (0, 1, 2), (0, 1, 2, 3)]


def distinct(sel):
    return len({frozenset(v) for v in sel.values() if v})


def main() -> int:
    f_full, f_gen = RES / "core_full.json", RES / "core_generic.json"
    if not f_full.exists() or not f_gen.exists():
        print("  UNRUNNABLE: a pole file is absent. Exit 2, never 0."); return 2
    full = json.loads(f_full.read_text())
    gen = json.loads(f_gen.read_text())

    poles = {"generic (text-blind)": distinct(gen), "full (maximally specific)": distinct(full)}
    real = {}
    for idxs in IDXS:
        sel = {p: [v[i] for i in idxs] for p, v in full.items() if v and max(idxs) < len(v)}
        real[str(idxs)] = {"prompts": len(sel), "distinct_text_selections": distinct(sel)}
    invented = {}
    for idxs in IDXS:
        sel = {p: [f"criterion {i}" for i in idxs] for p in list(full)[:200]}
        invented[str(idxs)] = {"prompts": len(sel), "distinct_text_selections": distinct(sel)}

    ctrl = {}
    ctrl["POSITIVE `generic` returns exactly 1 — R918's `fixed` set, the rule's anchor"] = (
        poles["generic (text-blind)"] == 1)
    ctrl["g=0 `full` returns 968 — the maximally prompt-specific pole"] = (
        poles["full (maximally specific)"] == len(full))
    ctrl["NEGATIVE the result holds for MORE THAN ONE index set"] = (
        len({v["distinct_text_selections"] for v in real.values()}) == 1
        and all(v["distinct_text_selections"] > 1 for v in real.values()))
    ctrl["SHAM the invented constant certifies and the real selection does not"] = (
        all(v["distinct_text_selections"] == 1 for v in invented.values())
        and all(v["distinct_text_selections"] > 1 for v in real.values()))
    ctrl["PLACEBO re-reading a selection file returns an identical count"] = (
        distinct(json.loads(f_gen.read_text())) == poles["generic (text-blind)"])
    gate_open = all(ctrl.values())

    a_killed = gate_open and all(v["distinct_text_selections"] > 1 for v in real.values())

    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        n = next(iter(real.values()))["distinct_text_selections"]
        verdict = (f"⛔ R1096's 'one committed selection file away' is RETRACTED. An index-blind "
                   f"subset's REAL selection has {n} distinct criterion-text selections — "
                   f"indistinguishable from `full`, and {n}× the rule's strict cell of 1. Writing "
                   f"the file does not help: it would honestly record {n}, and the rule would "
                   f"refuse. R1096's sham certified only because I fed it a constant string I "
                   f"invented. ⭐ **`prompt-blind` has two referents — INDEX-blind and TEXT-blind — "
                   f"and the certified family (2) and the synthetic family (15) are blind in "
                   f"different senses.** That is the third term in this arc to carry two referents "
                   f"whose control cannot separate them.")
    else:
        verdict = "world A — the real selection certifies, so R1096 stands."

    art = {"round": "R1097",
           "question": "does the real selection of an index-blind comparator certify?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "retracts": {"round": "R1096",
                        "claim": "a certifiable-and-disjoint family is one committed file away",
                        "why": ("its sham used an INVENTED constant string as the selection. The "
                                "real selection of an index-blind subset is text-diverse, so the "
                                "file would record 968 and the rule would refuse."),
                        "status": "headline RETRACTED; R1096's derivation and its population "
                                  "measurement (0 of 15 in the rule's population) stand"},
           "two_senses": {"INDEX_BLIND": "the same positional selection on every prompt — R1057's 15",
                          "TEXT_BLIND": "the same criterion strings on every prompt — `generic`",
                          "consequence": ("R1056's rule types TEXT, so the certified family and the "
                                          "synthetic family are blind in different senses and every "
                                          "cross-family statement in this arc carries that seam")},
           "id_space_note": ("`conversation_rubrics.jsonl` keys on a CONVERSATION id whose overlap "
                             "with the 968 scored prompt_ids is 0; `comparisons.jsonl` overlaps at "
                             "968. No join was needed here, and none is available by id."),
           "poles": poles, "real_selection": real, "invented_selection": invented,
           "controls": ctrl,
           "impossibility_corrected": {
               "criterion": "a comparator that is TEXT-blind and NOT an arm",
               "status": "N/A in this release",
               "what_it_would_require": ("a fixed external rubric committed as a comparator and "
                                         "excluded from candidacy; text-blindness over "
                                         "prompt-specific rubrics means a fixed external criterion "
                                         "set, which is what `generic` is — and `generic` is an arm")},
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1097 — the construction tests its own claim, and the claim fails\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE TWO POLES")
    for k, v in poles.items():
        print(f"    {k:<32} distinct text selections {v}")
    print(f"\n  AN INDEX-BLIND SUBSET'S REAL SELECTION")
    for k, v in real.items():
        print(f"    indices {k:<12} {v['prompts']} prompts -> {v['distinct_text_selections']}")
    print(f"\n  R1096's INVENTED SELECTION, re-run beside it")
    for k, v in invented.items():
        print(f"    indices {k:<12} {v['prompts']} prompts -> {v['distinct_text_selections']}"
              f"   ⚠ the fake certifies")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
