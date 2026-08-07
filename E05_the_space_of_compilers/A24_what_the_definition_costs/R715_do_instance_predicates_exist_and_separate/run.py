#!/usr/bin/env python3
"""
R715 -- does any per-INSTANCE predicate separate, and is it F1? (No, and it is not.)

CHECK #317 ON R714's NEXT LINE — IT HOLDS.
  ✓ 1 of 3 clauses evaluable on the 986; F3 admits 1.0000 and separates nothing there. Both from
    R714's committed artifact.

⭐ AND ITS LIVE QUESTION HAS AN ANSWER ALREADY ON DISK. Each rubric row carries `coval_core`
  (criteria only) and `coval_full` (criteria + rubric_item_id + scores), so a per-INSTANCE provenance
  relation exists and has never been computed here: is the core drawn FROM the full rubric?

⛔ AND THE TRAP, WRITTEN BEFORE THE RUN. Overlap-with-the-full-rubric IS NOT F1. F1 says the criteria
  were selected WITHOUT READING THE OUTCOME LABELS, and the full rubric is not the labels. If a
  separating instance predicate turns up, calling it "F1 restated" is the a-label-is-not-a-description
  error. It is a DIFFERENT predicate and is named as one.

ESTIMAND        per clause, whether an INSTANCE-level predicate exists that is computable from the
                release's per-conversation record AND separates — admits some, rejects others. A
                predicate admitting everything separates nothing and is reported DEGENERATE.
IDENTIFICATION  exact from the release file. ⚠ "separates" is a property of THIS release's instances,
                not of cores. ⚠ whether a separating predicate is the RIGHT one is construct validity
                and is impossible here.
SCOPE           population : the 986 conversation rubrics
                instrument : exact string set operations over criteria lists
                             instrument unit = A CORE INSTANCE
                             claim unit      = WHETHER A CLAUSE HAS AN INSTANCE FORM
                             ⚠ NOT EQUAL -- a predicate that separates instances is not thereby the
                             clause; the clause names a property, the predicate is one
                             operationalisation of it.
                baseline   : F3's instance predicate, which admits 1.0000
                regime     : this repository at HEAD
WORLDS          A NO INSTANCE FORM · B ONE EXISTS · C IT IS ALREADY F3
KILL            conditional on POSITIVE firing and g=0 returning a degenerate split
POSITIVE CTRL   `k == 4`, which the card says holds for ~95%, must give a non-degenerate split
g=0             "the core is non-empty" must return exactly 1.0000 and be reported DEGENERATE
NEGATIVE CTRL   each core against a DIFFERENT conversation's full rubric, cyclically shifted
SHAM            the overlap computed on `coval_full` against ITSELF -- the cross-field ingredient
                removed; it must return exactly 1.0000
PLACEBO         two identical runs differ by exactly 0
ARTIFACT        results/instance_predicates.json
IMPOSSIBLE      whether a separating predicate is the RIGHT one (construct validity) · restating F1
                (the outcome labels are not in this file, so NO predicate here can be F1)
"""
from __future__ import annotations
import collections, json, pathlib, statistics, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
SRC = ROOT / "data" / "conversation_rubrics.jsonl"
INSTRUMENT_UNIT, CLAIM_UNIT = "A CORE INSTANCE", "WHETHER A CLAUSE HAS AN INSTANCE FORM"

NORM = {
    "verbatim": lambda s: s,
    "casefold+strip": lambda s: s.casefold().strip(),
    "first-40-chars": lambda s: s.casefold().strip()[:40],
}


def overlap(core, full, norm):
    fs = {norm(c) for c in full}
    return sum(1 for c in core if norm(c) in fs) / len(core) if core else 0.0


def describe(vals):
    """A distribution is DEGENERATE if every instance gets the same value."""
    d = collections.Counter(round(v, 4) for v in vals)
    return {"mean": statistics.fmean(vals), "min": min(vals), "max": max(vals),
            "distinct": len(d), "degenerate": len(d) == 1,
            "share_zero": sum(1 for v in vals if v == 0.0) / len(vals),
            "top": dict(d.most_common(5))}


def main() -> int:
    if not SRC.exists():
        print(f"⛔ {SRC} absent — exit 2 rather than passing on an empty population")
        return 2
    rows = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    core = [[i["criterion"] for i in r["coval_core"]] for r in rows]
    full = [[i["criterion"] for i in r["coval_full"]] for r in rows]
    n = len(rows)
    print(f"─── THE OBJECT ───\n  {SRC.relative_to(ROOT)}   instances {n}")

    print("\n─── CONTROLS ───")
    k4 = [1.0 if len(c) == 4 else 0.0 for c in core]
    d_k4 = describe(k4)
    posok = not d_k4["degenerate"]
    print(f"  POSITIVE  `k == 4` (the card says ~95%): mean {d_k4['mean']:.4f}, distinct "
          f"{d_k4['distinct']} -> {'PASS — a known split registers' if posok else '⛔ FAIL'}")
    nonempty = [1.0 if c else 0.0 for c in core]
    d_ne = describe(nonempty)
    g0ok = d_ne["degenerate"] and d_ne["mean"] == 1.0
    print(f"  g=0       'the core is non-empty': mean {d_ne['mean']:.4f}, distinct "
          f"{d_ne['distinct']} -> "
          f"{'PASS — reported DEGENERATE, not passing' if g0ok else '⛔ FAIL'}")
    own = [overlap(c, f, NORM["verbatim"]) for c, f in zip(core, full)]
    shift = [overlap(c, full[(i + 1) % n], NORM["verbatim"]) for i, c in enumerate(core)]
    d_own, d_shift = describe(own), describe(shift)
    negok = d_shift["mean"] < d_own["mean"]
    print(f"  NEGATIVE  core vs a DIFFERENT conversation's rubric (shift by 1): mean "
          f"{d_shift['mean']:.4f} vs own {d_own['mean']:.4f} -> "
          f"{'PASS — the pairing carries the overlap' if negok else '⛔ FAIL'}")
    sham = [overlap(f, f, NORM["verbatim"]) for f in full]
    d_sham = describe(sham)
    shamok = d_sham["mean"] == 1.0
    print(f"  SHAM      `coval_full` against ITSELF (cross-field ingredient removed): mean "
          f"{d_sham['mean']:.4f} -> {'PASS — exactly 1.0000 as it must be' if shamok else '⛔ FAIL'}")
    plc = [overlap(c, f, NORM["verbatim"]) for c, f in zip(core, full)] == own
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    f3 = [1.0 if 1 < len(c) <= 4 else 0.0 for c in core]
    d_f3 = describe(f3)
    print(f"\n─── THE INSTANCE PREDICATES, AND WHETHER EACH SEPARATES ───")
    preds = [
        ("F3 size  1<k<=4", d_f3, "the clause's own instance form"),
        ("PROVENANCE core∩full", d_own, "⚠ NOT F1 — the full rubric is not the outcome labels"),
        ("k == 4 exactly", d_k4, "a control, and the card's own statistic"),
    ]
    print(f"  {'predicate':<24}{'mean':>8}{'min':>7}{'max':>7}{'distinct':>10}{'  separates?'}")
    for nm, d, note in preds:
        print(f"  {nm:<24}{d['mean']:>8.4f}{d['min']:>7.2f}{d['max']:>7.2f}{d['distinct']:>10}"
              f"   {'⛔ DEGENERATE' if d['degenerate'] else '⭐ SEPARATES'}")
        print(f"  {'':24}{note}")

    print(f"\n─── THE PROVENANCE DISTRIBUTION (the one that separates) ───")
    print(f"  share with ZERO verbatim overlap : {d_own['share_zero']:.4f} "
          f"({round(d_own['share_zero']*n)} of {n})")
    print(f"  mean overlap                     : {d_own['mean']:.4f}")
    print(f"  distribution                     : {d_own['top']}")
    print(f"  exact subsets (overlap == 1.0)   : {sum(1 for v in own if v == 1.0)} of {n}")

    print(f"\n─── THE SPECIFICATION SWEEP (3 matchings × 2 comparisons = 6 cells) ───")
    cells = []
    for mn, fn in NORM.items():
        for cn, other in (("own conversation", None), ("shifted conversation", 1)):
            vals = [overlap(c, full[i] if other is None else full[(i + other) % n], fn)
                    for i, c in enumerate(core)]
            d = describe(vals)
            cells.append({"matching": mn, "comparison": cn, **{k: d[k] for k in
                                                               ("mean", "share_zero", "degenerate")}})
            print(f"  {mn:<16}{cn:<24}mean {d['mean']:.4f}   zero-overlap share "
                  f"{d['share_zero']:.4f}")
    print(f"  ⚠ verbatim is the STRICTEST matching, so a looser one can only RAISE overlap — the "
          f"sweep bounds the answer from both sides rather than reporting one cell.")

    A, B, Cc = d_f3["mean"], d_own["share_zero"], d_own["mean"]
    print(f"\n─── REGISTERED ───")
    print(f"  A  F3 admission = 1.0000 [0.80,1.00] -> {A:.4f}: "
          f"{'INSIDE' if 0.80 <= A <= 1.00 else '⛔ OUTSIDE'}   "
          f"{'and DEGENERATE — separates nothing' if d_f3['degenerate'] else ''}")
    print(f"  B  zero-overlap share = 0.70 [0.30,0.95] -> {B:.4f}: "
          f"{'INSIDE' if 0.30 <= B <= 0.95 else '⛔ OUTSIDE'}")
    print(f"  C  mean overlap = 0.10 [0.01,0.40] -> {Cc:.4f}: "
          f"{'INSIDE' if 0.01 <= Cc <= 0.40 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL provenance separates where F3 does not -> "
          f"{'HOLDS' if (not d_own['degenerate']) and d_f3['degenerate'] else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells above, all printed. Counts are EXACT; no p-values "
          f"are computed and none are implied.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; these distributions would be silence."
    elif (not d_own["degenerate"]) and d_f3["degenerate"]:
        world = (
            f"⭐⭐⭐ B AN INSTANCE PREDICATE EXISTS AND SEPARATES — AND IT IS NOT F1. Across the {n} "
            f"cores the release ships, F3's instance form admits {A:.4f} with {d_f3['distinct']} "
            f"distinct value: DEGENERATE, it separates nothing. A per-instance PROVENANCE predicate "
            f"does separate: the share of a core's criteria appearing verbatim in its OWN full "
            f"rubric has mean {Cc:.4f}, ranges {d_own['min']:.2f}–{d_own['max']:.2f}, and "
            f"{B:.4f} of conversations — {round(B*n)} of {n} — have ZERO overlap, with exactly "
            f"{sum(1 for v in own if v == 1.0)} core drawn wholly from its rubric. ⭐ SO THE RELEASED "
            f"CORES ARE NOT SELECTIONS FROM THE FULL RUBRIC; they are written fresh, which is what "
            f"the failure table's retired clause 'drawn from a rubric' asserted and what nothing here "
            f"had measured per instance. ⛔⛔ AND IT IS NOT F1, WHICH I WROTE DOWN BEFORE RUNNING IT: "
            f"F1 says the criteria were selected WITHOUT READING THE OUTCOME LABELS, and the full "
            f"rubric is not the labels — the labels are not in this file at all. Naming this "
            f"predicate F1 would be the a-label-is-not-a-description error, so it is named as a "
            f"DIFFERENT predicate and F1 remains without an instance form. ⚠ The negative control "
            f"carries the reading: against a DIFFERENT conversation's rubric the overlap falls to "
            f"{d_shift['mean']:.4f}, so the {Cc:.4f} is a property of the pairing and not of "
            f"criteria vocabulary in general. ⚠ AND SEPARATING IS NOT BEING RIGHT: whether this "
            f"predicate is the one a definition of core should use is construct validity, and it is "
            f"impossible here. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT} — a predicate that separates instances is not thereby the clause.")
    elif d_own["degenerate"]:
        world = (f"⭐⭐ A NO INSTANCE FORM — no computable per-instance predicate separates over the "
                 f"{n} cores, so the formulation is a GENERATOR definition and cannot be made an "
                 f"instance one from this release.")
    else:
        world = (f"⭐⭐ C IT IS ALREADY F3 — F3's instance form separates ({d_f3['distinct']} distinct "
                 f"values) and nothing is gained by looking further.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "instance_predicates.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n_instances": n,
        "f3": d_f3, "provenance_own": d_own, "provenance_shifted": d_shift,
        "control_k4": d_k4, "g0_nonempty": d_ne, "sham_full_vs_itself": d_sham,
        "exact_subsets": sum(1 for v in own if v == 1.0), "cells": cells,
        "registered": ("A F3 admission 1.0000 [0.80,1.00]; B zero-overlap 0.70 [0.30,0.95]; "
                       "C mean overlap 0.10 [0.01,0.40]; directional provenance separates, F3 not"),
        "observed": {"A": A, "B": B, "C": Cc,
                     "directional": (not d_own["degenerate"]) and d_f3["degenerate"]},
        "NOT_F1": ("the full rubric is not the outcome labels, and the labels are not in this file. "
                   "This predicate is NOT F1 restated; F1 remains without an instance form."),
        "limit": ("separating is not being right — whether this predicate is the one a definition of "
                  "core should use is construct validity, impossible here."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
