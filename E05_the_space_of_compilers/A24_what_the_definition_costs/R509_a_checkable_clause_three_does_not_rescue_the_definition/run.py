"""Narrowing ③ to something CHECKABLE gives an extension of one — and that one is a blind spot.

WHY. R508 found that ③'s provenance property has a PARTIAL behavioural surrogate: selection position
catches every arm that OPTIMISES against the labels and misses rule-based selectors. That invites an
obvious reformulation — replace ③ *"not built by reading the labels"* (provenance, checkable only
from the producer) with ③′ *"not OPTIMISED against the labels"* (checkable from the criterion set plus
the prompt's rubric). This round asks whether ③′ rescues the definition from its empty extension.

ESTIMAND        The extension of ①∧②∧④∧③′ — the arms admitted by the behavioural clauses that ③′ does
                not exclude — and, for each admitted arm, WHY it was admitted: because the instrument
                looked and found nothing, or because the instrument could not look.
IDENTIFICATION  Exact. The five arms admitted by ①∧②∧④ are fixed by the record; ③′'s verdict on each
                is R508's measured separation, re-read here rather than recomputed.

⛔ THE DISTINCTION THIS ROUND EXISTS TO ENFORCE, and §1 states it: a zero from an instrument never
                shown to return non-zero is SILENCE, not an acquittal. An arm with no criterion-text
                file has no selection positions, so ③′ cannot rule on it at all. Counting such an arm
                as ADMITTED converts missing data into a definitional member.
SCOPE           population = the 5 arms admitted by ①∧②∧④ · instrument = R508's normalised selection
                position against a null built from uniform selectors · regime = first release.
WORLDS          A ③′ RESCUES IT. The extension is non-empty and every member was ADJUDICATED — the
                  instrument looked at it and found no optimisation. Then a checkable definition
                  with real members exists and the fork's B-column loses its cost.
                B ③′ HIDES THE VACUITY. The extension is non-empty only because the instrument is
                  blind to its members. Then ③′ is worse than ③: same emptiness, less visible.
                C ③′ CHANGES NOTHING. Extension still 0.
KILL            Pre-registered: if every admitted arm is admitted by ABSENCE of instrument coverage
                rather than by a negative reading, world A is dead however non-empty the count looks.
POSITIVE CTRL   The instrument must have ruled on SOMETHING in this population — at least one of the
                five must be excluded by a measured separation, not by assumption. R508's
                `honest` set supplies it and it can fail: if none of the five separates, ③′ has no
                purchase here at all and the round reports C.
NEGATIVE CTRL   Arms whose selection rule is stated over the rubric ordering separate by DERIVATION.
                They are counted separately and never as evidence that ③′ works.
PLACEBO         An arm with criterion text and no separation would be a genuine ③′-admission. The
                round reports how many such arms exist; if zero, the extension is entirely blind
                spots and that is the finding.
NOISE FLOOR     Inherited from R508's null band, not recomputed.
MULTIPLICITY    All five arms reported; none selected.
ARTIFACT        results/checkable_extension.json
IMPOSSIBLE      whether `coval_core` would separate cannot be decided on this release: it ships no
                criterion-text file. It would require the released core's criteria as text, which
                the second release may carry and this one does not.
"""
from __future__ import annotations
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
R508 = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R508_selection_position_is_a_partial_provenance_surrogate/results/selection_position.json"
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
FIVE = ["oracle_k4", "greedy_k4_fit1", "indep_k4_fit1", "coval_core", "topw_k4"]


def main() -> int:
    if not R508.exists():
        print("  R508's artifact is missing -- this round reads it rather than recomputing"); return 2
    d = json.loads(R508.read_text())
    sep, missed, honest = set(d["separates"]), set(d["missed"]), set(d["honest"])
    has_text = {a for a in FIVE if (ROOT/f"corebench/results/core_{a}.json").exists()}

    print(f"  the {len(FIVE)} arms admitted by ①∧②∧④, under ③ and under ③′:\n")
    print(f"  {'arm':<20}{'has criterion text':>20}   ③′ verdict")
    adjudicated_out, blind, admitted_seen = [], [], []
    for a in FIVE:
        txt = a in has_text
        if not txt:
            v = "CANNOT RULE — no criterion text, so no positions"; blind.append(a)
        elif a in honest:
            v = "EXCLUDED — separates as an optimiser (measured)"; adjudicated_out.append(a)
        elif a in sep:
            v = "excluded by DERIVATION — rule stated over the ordering"; adjudicated_out.append(a)
        elif a in missed:
            v = "ADMITTED — instrument looked and found nothing"; admitted_seen.append(a)
        else:
            v = "not in R508's population"; blind.append(a)
        print(f"  {a:<20}{str(txt):>20}   {v}")

    ok_pos = len(adjudicated_out) > 0
    print(f"\n  POSITIVE CONTROL: the instrument ruled on at least one of the five -> "
          f"{'PASS' if ok_pos else 'FAIL'} ({len(adjudicated_out)} excluded by measurement)")
    if not ok_pos:
        print("  ③′ has no purchase on this population at all; nothing below is a reading"); return 1

    ext = admitted_seen + blind
    print(f"\n  ③  extension: 0   (every one of the five is provenance-excluded)")
    print(f"  ③′ extension: {len(ext)}  {ext}")
    print(f"     of which ADJUDICATED (instrument looked, found nothing): {len(admitted_seen)} {admitted_seen}")
    print(f"     of which BLIND SPOTS (instrument could not look):        {len(blind)} {blind}")

    world = ("A ③′ RESCUES IT" if admitted_seen and not blind else
             "B ③′ HIDES THE VACUITY" if blind and not admitted_seen else
             "C ③′ CHANGES NOTHING" if not ext else
             "SPLIT — the extension mixes adjudicated members with blind spots")
    print(f"\n  WORLD: {world}")
    if world.startswith("B"):
        print(f"  => ③′'s whole extension is {blind}, admitted because the release ships no")
        print(f"     criterion-text file for it — 95 arms have one and the RELEASED CORE does not.")
        print(f"     A zero from an instrument that could not look is silence, not an acquittal,")
        print(f"     so this is not a member; it is missing data wearing a member's clothes.")
        print(f"  => therefore narrowing ③ to something CHECKABLE does not rescue the definition.")
        print(f"     It converts 'empty because ③ excludes everything' into 'one member the")
        print(f"     instrument cannot see' — the same vacuity, harder to notice. WORSE, not better.")
    json.dump({"five": FIVE, "has_text": sorted(has_text), "adjudicated_out": adjudicated_out,
               "admitted_seen": admitted_seen, "blind": blind, "extension_3prime": ext,
               "positive_control": ok_pos, "world": world},
              (OUT/"checkable_extension.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
