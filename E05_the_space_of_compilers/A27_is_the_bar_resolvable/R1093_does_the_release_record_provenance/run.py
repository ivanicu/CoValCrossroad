#!/usr/bin/env python3
"""R1093 — clause ③ says the core consumes no prompt-specific human labels. The card says it does.

R1092 established that the core's criterion text is in the release and that clause ③ was still not
settled, because `n_distinct` measures prompt-specificity and ③ names human-label consumption. Its
NEXT asked whether the release records PROVENANCE. Two answers, and they point opposite ways.

⛔⛔ AND THIS IS PRIOR ART IN THE OBJECT'S OWN DOCUMENTATION. `data/DATASET_CARD.md` states how
    CoVal-core is built. A result that restates the object's own card is a **VERIFICATION**, not a
    finding, and the paper template carries a `prior_art_in_card` column precisely so this cannot be
    reported as a discovery. It is flagged below and in the artifact.

⚠ WHY NOBODY IN THIS ARC CHECKED IT. The clause table retains ③ as *"provenance, no bar"* with
  comparator and criterion both `invariant` -- which reads as *nothing to measure*. A clause with no
  threshold is not a clause with no truth value, and that reading is what kept it unexamined.

ESTIMAND        (Q1, schema) does any release file carry a per-item provenance field on
                     `coval_core` -- anything linking a core criterion to a source item or an
                     author? Counted over ALL conversations, not a sample.
                (Q2, card) what does `DATASET_CARD.md` say CoVal-core is built FROM? Quoted, not
                     paraphrased, and labelled prior art.
IDENTIFICATION  Q1 is exact. Q2 is a documented fact about the release, not a measurement of it.
UNIT OF THE     Q1: a rubric item and its field names. Q2: a sentence in the card.
  INSTRUMENT
UNIT OF THE     the same. ⚠ Q2 licenses a claim about the CONSTRUCTION of the core, which is what
  CLAIM         clause ③ quantifies over; it licenses nothing about any other arm.
SCOPE           population: 986 conversations in `data/conversation_rubrics.jsonl`; the card.
                instrument: direct read. baseline: `coval_full`'s field set. regime: this release.
WORLDS          A ③ HOLDS      the core is built without consuming prompt-specific human labels.
                B ③ IS FALSE   the core is a distillation of human-authored, human-rated items.
                C UNRECORDED   the release neither states nor records it.
                Prediction matrix on (per-item provenance field, card text):
                  A -> (any, says generated from the conversation alone)
                  B -> (any, says synthesised from the annotators' rubric items)
                  C -> (none, silent)
KILL            pre-registered. World A is KILLED if the card states the core is built from the
                collected rubric items. World C is KILLED if the card states any construction at
                all. Both are decided by quoting the card, not by inferring from the data.
POSITIVE CTRL   the field scan must find `rubric_item_id` and `scores` on `coval_full`, which are
                known to exist. An instrument that cannot see a field that is there cannot be
                trusted when it reports one absent.
g=0 GUARD       a field name that exists nowhere must return 0 items, not a default.
NEGATIVE CTRL   the scan is run over ALL 986 conversations, not the first 200: an absence found in a
                sample is a sample's absence.
SHAM            the same scan against `data/annotators.jsonl`, which carries no rubric items --
                it must report no `coval_core` items rather than an error read as a zero.
PLACEBO         re-reading returns identical field counts.
NOISE FLOOR     none; both questions are deterministic reads and the round says so.
MULTIPLICITY    every distinct field name seen under either key is reported, not only the sought one.
SPECIFICATION   key in {coval_core, coval_full} x scope in {first 200, all 986}.
ARTIFACT        results/provenance.json with the source hash and the quoted card sentence.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      auditing whether the human review the card describes actually occurred -- N/A, it
                would require the review record, which the release does not ship.
"""
from __future__ import annotations

import collections, hashlib, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "provenance.json"
RUB = ROOT / "data" / "conversation_rubrics.jsonl"
CARD = ROOT / "data" / "DATASET_CARD.md"


def fields(path, key, limit=None):
    c, n, items = collections.Counter(), 0, 0
    if not path.exists():
        return c, 0, 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            n += 1
            for it in r.get(key, []) or []:
                if isinstance(it, dict):
                    c.update(it.keys()); items += 1
            if limit and n >= limit:
                break
    return c, n, items


def main() -> int:
    if not RUB.exists() or not CARD.exists():
        print("  UNRUNNABLE: the release files are absent. Exit 2, never 0."); return 2

    core_all, n_all, core_items = fields(RUB, "coval_core")
    full_all, _, full_items = fields(RUB, "coval_full")
    core_200, _, _ = fields(RUB, "coval_core", limit=200)
    ghost, _, ghost_items = fields(RUB, "coval_does_not_exist")
    sham, sham_n, sham_items = fields(ROOT / "data" / "annotators.jsonl", "coval_core")

    ctrl = {}
    ctrl["POSITIVE the scan sees rubric_item_id and scores on coval_full"] = (
        "rubric_item_id" in full_all and "scores" in full_all)
    ctrl["g=0 a key that exists nowhere returns 0 items, not a default"] = ghost_items == 0
    ctrl["NEGATIVE the scan covers ALL conversations, not a sample"] = (
        n_all >= 900 and set(core_200) == set(core_all))
    ctrl["SHAM annotators.jsonl yields no rubric items rather than an error"] = (
        sham_items == 0 and sham_n > 0)
    ctrl["PLACEBO a second read returns identical field counts"] = (
        fields(RUB, "coval_core")[0] == core_all)
    gate_open = all(ctrl.values())

    # ---- Q2: the card, quoted rather than paraphrased --------------------------------------
    txt = CARD.read_text(encoding="utf-8")
    quotes = {}
    for label, pat in (("core construction", r"\*\*Core rubrics\*\*:[^\n]*"),
                       ("rubric authoring", r"\*\*Rubric item authoring\*\*:[^\n]*"),
                       ("core caveat", r"\*\*CoVal-core rubrics are experimental\*\*:[^\n]*")):
        m = re.search(pat, txt)
        quotes[label] = m.group(0)[:600] if m else None
    consumes = bool(quotes["core construction"]
                    and re.search(r"human review|highest average ratings|distillation|CoVal-full",
                                  quotes["core construction"] + (quotes["core caveat"] or "")))

    provenance_field = sorted(set(core_all) - {"criterion"})
    a_killed = gate_open and consumes

    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = ("⛔ CLAUSE ③ IS FALSE OF THE RELEASED CORE, by the release's own card. CoVal-core "
                   "is built by 'language-model-assisted synthesis and human review' from the "
                   "annotator-authored, annotator-rated CoVal-full items, selecting those with the "
                   "'highest average ratings'. So it CONSUMES prompt-specific human labels. "
                   "⚠ VERIFICATION, not a finding: this is stated in the object's own documentation "
                   "and was never read into this arc's record, because the clause table retains ③ "
                   "as 'provenance, no bar' — which reads as nothing to measure.")
    else:
        verdict = ("world C — the card states no construction for the core and the data records no "
                   "provenance field, so ③ is unrecorded rather than false.")

    art = {"round": "R1093",
           "question": "does the release record criterion provenance, and what does it say?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "prior_art_in_card": True,
           "prior_art_note": ("the answer is in data/DATASET_CARD.md. A result restating the "
                              "object's own card is a VERIFICATION, never a discovery."),
           "population": {"conversations": n_all, "coval_core_items": core_items,
                          "coval_full_items": full_items},
           "Q1_schema": {"coval_core_fields": dict(core_all), "coval_full_fields": dict(full_all),
                         "per_item_provenance_field_on_core": provenance_field,
                         "reading": ("`coval_core` items carry ONLY `criterion`. `coval_full` "
                                     "carries `rubric_item_id` and `scores`. There is NO link from "
                                     "a core criterion back to the full items it was synthesised "
                                     "from, so the provenance is documented in prose and not "
                                     "recorded per item.")},
           "Q2_card_quotes": quotes,
           "controls": ctrl,
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1093 — does the release record provenance, and what does the card say?\n")
    print("  ⚠ PRIOR ART IN THE OBJECT'S OWN CARD — this is a VERIFICATION, not a discovery.\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  Q1 · SCHEMA over all {n_all} conversations")
    print(f"    coval_core item fields : {dict(core_all)}")
    print(f"    coval_full item fields : {dict(full_all)}")
    print(f"    per-item provenance field on the core: {provenance_field or 'NONE'}")
    print(f"\n  Q2 · THE CARD, QUOTED")
    for k, v in quotes.items():
        print(f"    [{k}] {(v or 'NOT FOUND')[:300]}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
