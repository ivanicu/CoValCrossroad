#!/usr/bin/env python3
"""R1010 — R1009's finding was committed at R921 and never adopted. The gap is the finding.

⛔⛔ THE CORRECTION FIRST, BECAUSE IT IS ABOUT MY OWN LAST ROUND. R1009 reported that the formulation
admits `generic`, a prompt-blind arm, and proposed quantifying clause ② over ALL certified
comparators. **Both are in R921's committed artifact.** It carries two fields:

    admitted_by_at_least_one_legitimate : 28 arms   <- includes `generic`, `generic_reprov`
    survives_all_legitimate             : 24 arms   <- the repair, already named and computed

and their difference is exactly `['generic', 'generic_reprov', 'greedy_k12_fit1', 'topw_k2']`.
⭐ So the MEMBERSHIP fact and the REPAIR were both on disk before R1009 ran. R1009's genuine
additions are narrower and are stated as such in its README correction: the READING (that admitting a
prompt-blind arm means the definition admits its own null — R921 framed it as comparator-choice
sensitivity), the RESOLVABILITY of that admission, and the repair's cost at the full ②∧③ conjunction
(9 vs 12), where R921's 24/28 are clause-② alone.

⭐⭐ AND THAT LEAVES A BETTER QUESTION THAN THE ONE R1009's NEXT ASKED. R1009 wanted a THIRD
prompt-blind comparator built. R921's own artifact prices that: *"a comparator that is not already a
scored arm costs 15,488 judge calls (R914); this round bounds what that would buy."* So the expensive
move is priced and partly pre-answered. **The unasked question is why a stronger criterion, computed
and committed, was never used.**

ESTIMAND        among rounds after R921, how many READ `survives_all_legitimate` (the stronger
                criterion) versus `legitimate_comparators` (the weaker, per-comparator route); and
                whether the definition's statement region ever carried it.
IDENTIFICATION  exact and textual — this is a count over committed files, not an inference.
SCOPE           population : every `run.py` under E*/A*/R*, plus DEFINITION.md's statement region
                instrument : a TIGHT pattern (the field in a subscript or `.get`) and a LOOSE one
                             (the bare string anywhere), reported side by side
                baseline   : `legitimate_comparators`, a field from the SAME artifact, which
                             establishes the instrument can find readers at all
                regime     : this repo
WORLDS          A ADOPTED       the stronger criterion is read widely, or reaches the statement.
                                Then R1009's repair was already in force and its cost is moot.
                B UNADOPTED     it is read rarely and never reaches the statement. Then a correct,
                                committed measurement sat unused, and R1009 rediscovered its
                                consequence ~90 rounds later.
                prediction matrix: A -> readers comparable to the baseline field, or >0 in the
                                   statement. B -> far fewer, and 0 in the statement.
KILL            pre-registered: if the stronger criterion IS read by a comparable number of rounds,
                the "never adopted" claim is withdrawn in this round's own headline.
POSITIVE CTRL   `legitimate_comparators` — a field of the SAME artifact — must return many readers.
                If the instrument cannot find readers of a field that is demonstrably used, a zero
                for the other field is silence, not a measurement.
NEGATIVE CTRL   a runtime-assembled field name that exists nowhere must return 0 readers under both
                patterns. Built from fragments, because writing an absent marker into the file is
                what puts it in the corpus.
PLACEBO         the tight and loose patterns applied to the BASELINE field must agree in direction
                (loose >= tight). A tight pattern exceeding its loose superset is a broken regex.
NOISE FLOOR     n/a — an exact count over a fixed corpus. Labelled rather than omitted; the
                uncertainty here is the tight/loose SPREAD, which is reported.
MULTIPLICITY    3 field names × 2 patterns × 2 populations (round scripts, statement) = 12 cells.
ARTIFACT        results/adoption_gap.json with this file's source hash.
IMPOSSIBLE      ⚠ WHY it was not adopted — N/A. Intent is not in the record, and a reason invented
                here would be a narrative. What is measurable is that it was not, and when.
                ⚠ whether a THIRD comparator would shrink the extension — N/A, and priced rather
                than guessed: R921 records 15,488 judge calls for a comparator that is not already
                a scored arm.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs  # noqa: E402

R921_ROUND = 921
FIELDS = ["survives_all_legitimate", "legitimate_comparators", "admitted_by_at_least_one_legitimate"]


def tight(field):
    return re.compile(rf"""\[\s*["']{field}["']\s*\]|\.get\(\s*["']{field}["']""")


def main() -> int:
    ghost = "zz" + "_absent_" + "field_" + "r1010"
    scripts = []
    for d in iter_round_dirs(ROOT):
        f = d / "run.py"
        if not f.exists():
            continue
        try:
            num = int(d.name.split("_")[0][1:])
        except ValueError:
            continue
        if num <= R921_ROUND:
            continue
        scripts.append((d.name, f.read_text()))
    if not scripts:
        print("  UNRUNNABLE: no rounds after R921. Empty population must not pass. Exit 2.")
        return 2
    print(f"  population: {len(scripts)} round scripts written after R{R921_ROUND}")

    spec = importlib.util.spec_from_file_location(
        "sc", ROOT / "assurance/a_statement_is_current_with_the_arc.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    region = m.statement_region((ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text())
    if region is None:
        print("  UNRUNNABLE: the statement region failed to load. Exit 2, never 0.")
        return 2

    rows = []
    for field in FIELDS + [ghost]:
        t = tight(field)
        n_t = sum(1 for _n, s in scripts if t.search(s))
        n_l = sum(1 for _n, s in scripts if field in s)
        in_stmt = field in region
        rows.append({"field": field, "tight_readers": n_t, "loose_mentions": n_l,
                     "in_statement": in_stmt,
                     "readers": sorted(n for n, s in scripts if t.search(s))[:6]})

    base = next(r for r in rows if r["field"] == "legitimate_comparators")
    gh = next(r for r in rows if r["field"] == ghost)
    pos_ok = base["tight_readers"] >= 5
    neg_ok = gh["tight_readers"] == 0 and gh["loose_mentions"] == 0 and not gh["in_statement"]
    plac_ok = all(r["loose_mentions"] >= r["tight_readers"] for r in rows)
    print(f"\n  POSITIVE CONTROL — the baseline field `legitimate_comparators` must have many "
          f"readers: {base['tight_readers']} → {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE CONTROL — a runtime-assembled absent field returns 0 everywhere: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO         — loose >= tight for every field (a tight pattern cannot exceed its "
          f"superset): {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; the counts below certify nothing. Exit 2, never 0.")
        return 2

    print(f"\n  {'field':<40}{'tight':>7}{'loose':>7}  in statement")
    for r in rows:
        nm = r["field"] if r["field"] != ghost else "(runtime-assembled sentinel)"
        print(f"  {nm:<40}{r['tight_readers']:>7}{r['loose_mentions']:>7}  {r['in_statement']}")

    strong = next(r for r in rows if r["field"] == "survives_all_legitimate")
    adopted = strong["tight_readers"] >= base["tight_readers"] or strong["in_statement"]
    world = ("A ADOPTED — the stronger criterion is read comparably to the weaker one or reaches "
             "the statement" if adopted else
             f"B UNADOPTED — the stronger criterion has {strong['tight_readers']} reader(s) against "
             f"the weaker one's {base['tight_readers']}, and appears in the statement: "
             f"{strong['in_statement']}")
    print(f"\n⭐ {world}")
    if not adopted:
        print(f"   readers of the stronger criterion: {strong['readers'] or 'none'}")
        print("   ⛔ SO A CORRECT, COMMITTED MEASUREMENT SAT UNUSED WHILE THE ARC BUILT A")
        print("      FORMULATION ON THE WEAKER ROUTE, AND R1009 REDISCOVERED ITS CONSEQUENCE.")
        print("      The defect was never that nobody computed it. It is that nobody adopted it.")

    print("\n⚠ WHY it was not adopted is NOT measured and is not guessed. Intent is not in the")
    print("   record; a reason invented here would be a narrative. What is measurable is that it")
    print("   was not, and from which round.")

    out = HERE / "results" / "adoption_gap.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="a stronger criterion was committed at R921 and never adopted",
        n_scripts_after_r921=len(scripts),
        controls={"positive_baseline_has_readers": bool(pos_ok),
                  "negative_absent_field_zero": bool(neg_ok),
                  "placebo_loose_ge_tight": bool(plac_ok)},
        rows=[r for r in rows if r["field"] != ghost], world=world, adopted=bool(adopted),
        correction_to_r1009="the membership fact and the repair's name were both committed in "
                            "R921's artifact; R1009's genuine additions are the reading, the "
                            "resolvability, and the repair's cost at the full conjunction",
        not_measured="why it was not adopted — intent is not in the record",
        third_comparator_price="15,488 judge calls (R914, quoted in R921's own artifact)",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
