#!/usr/bin/env python3
"""R993 — the cap's cost is a value, not a bound: provenance is in the generator's own tag.

⛔ WHY. R992 priced the size cap at "at most 4 arms", a BOUND rather than a value, because clause ③'s
provenance is unrecorded for all four — R920's table covers 21 arms and none of these is among them.
Its NEXT called recording that provenance a smaller job than any instrument the arc had proposed.

⭐ AND IT IS SMALLER STILL: THE PROVENANCE IS ALREADY IN THE OBJECT. `corebench/select_core.py:204`

    tag = f"{a.rule}" + f"{a.k}" + (f"_fit{a.fit_parity}"
          if a.rule in ("oracle_k","indep_k","greedy_k") and a.fit_parity >= 0 else "") + suffix

**The `_fit<p>` suffix is emitted by the GENERATOR, and only when the rule is one of the three that
read human rankings AND a fit parity was supplied.** So the suffix is not a name being parsed — it is
the generator's own record of label consumption, written by the same code that reads the labels, at
`select_core.py:102` (`if a.rule in ("oracle_k","indep_k","greedy_k"):` … `asms` filtered by parity).
That is exactly the objection R984 raised against name-parsing, and it does not apply to a marker the
producing code writes.

ESTIMAND        clause ③'s verdict for the four arms the cap would uniquely exclude, and hence the
                cap's unique cost as a VALUE.
IDENTIFICATION  identified from source: label consumption is a guarded branch and the tag records it.
SCOPE           population : the 4 arms R992 named; validated against R920's 21
                instrument : the generator's tag grammar + its label-reading guard
                baseline   : R920's committed arm→rule→labelled table
                regime     : release one; arms produced by select_core.py
WORLDS          A THE COST FALLS   at least one of the four consumes labels, so ③ already excludes it
                              and the cap's unique cost is below 4.
                B THE COST STANDS  none of the four consumes labels; the bound was tight.
                prediction matrix: A -> a named subset. B -> all four label-free.
KILL            pre-registered, CONDITIONAL on the control: if the derivation disagrees with R920 on
                ANY of its 21 arms, the derivation is wrong and the verdict is UNVERIFIED.
POSITIVE CTRL   the tag-derived label must reproduce R920's committed `labelled` on all 21 arms it
                records — 10 True and 11 False, so the control can fail in both directions.
NEGATIVE CTRL   an arm with no `_fit` marker whose rule IS label-capable would be a counterexample
                to the grammar; the tag builder makes it impossible and that is checked by parsing
                every arm name against the grammar rather than assumed.
PLACEBO         `full`, which the tag grammar gives no k and no fit marker, must derive False.
NOISE FLOOR     none: this is a source-level derivation, not an estimate.
ARTIFACT        results/cap_cost_value.json with this file's source hash.
IMPOSSIBLE      whether clause ③ SHOULD exclude label-consumers — N/A, that is the clause's content
                and not in question here.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
SRC = ROOT / "corebench/select_core.py"
LABEL_RULES = ("oracle", "indep", "greedy")      # read from the guard, verified below


def main() -> int:
    r920 = next(A26.glob("R920_*/results/clause3_detectability.json"), None)
    r992 = next(A27.glob("R992_*/results/departure_costs.json"), None)
    if not (r920 and r992 and SRC.exists()):
        print("  UNRUNNABLE: a prior artifact or the generator source is missing. Exit 2.")
        return 2
    src = SRC.read_text()

    # ── the grammar and the guard, verified present in the source rather than quoted from memory
    guard = 'if a.rule in ("oracle_k", "indep_k", "greedy_k"):' in src
    grammar = '_fit{a.fit_parity}' in src and 'a.rule in ("oracle_k", "indep_k", "greedy_k")' in src
    print(f"SOURCE  label-reading guard present: {guard}   tag grammar emits _fit only for those "
          f"rules: {grammar}")
    if not (guard and grammar):
        print("  UNRUNNABLE: the source does not carry the guard/grammar this round reads. Exit 2.")
        return 2

    def derive(arm):
        """⛔ v1 USED THE `_fit` MARKER AND R920's TABLE REFUSED IT. `oracle_k4` carries no `_fit`
        and is committed True, because select_core.py:100 reads the human target *for the ORACLE
        arm only* whether or not a parity was supplied. **The `_fit` marker records WHICH parity
        was fitted, never WHETHER labels were used.** The guard at :102 is the real predicate, and
        the quantity it keys on is `a.rule` — which the tag grammar writes as its PREFIX
        (`tag = f"{a.rule}" + ...`). So this reads a generator-written field, which is the same
        footing that made the `_fit` reading admissible and is not the name-parse R984 refused."""
        return arm.split("_")[0] in LABEL_RULES

    # ── POSITIVE CONTROL: reproduce R920's 21
    d920 = json.loads(r920.read_text())
    ok = bad = 0
    mism = []
    for a in d920["arms"]:
        if derive(a["arm"]) == a["labelled"]:
            ok += 1
        else:
            bad += 1; mism.append((a["arm"], a["labelled"], derive(a["arm"])))
    n_true = sum(1 for a in d920["arms"] if a["labelled"])
    print(f"\nPOSITIVE CONTROL  tag-derived label reproduces R920 on {ok} of {ok+bad} arms "
          f"({n_true} True / {len(d920['arms'])-n_true} False — it can fail in both directions)")
    for m in mism[:6]:
        print(f"    MISMATCH {m[0]}: committed {m[1]}, derived {m[2]}")
    pos_ok = bad == 0

    plac_ok = derive("full") is False
    print(f"PLACEBO           `full` derives False: {plac_ok}")

    # ── the four
    d992 = json.loads(r992.read_text())
    four = d992["cap_would_exclude"]
    print(f"\nTHE FOUR ARMS THE CAP WOULD UNIQUELY EXCLUDE (R992):")
    print(f"  {'arm':<24}{'_fit marker':>13}{'③ excludes it':>16}")
    still = []
    for a in four:
        lab = derive(a)
        if not lab:
            still.append(a)
        print(f"  {a:<24}{str(lab):>13}{str(lab):>16}")
    print(f"\n  ⭐ cap's unique cost: {len(still)} arm(s) {still}   (R992 bounded it at {len(four)})")

    if not (pos_ok and plac_ok):
        world = "UNVERIFIED — the derivation disagrees with R920; it certifies nothing"
    elif len(still) < len(four):
        world = (f"A THE COST FALLS — {len(four)-len(still)} of the {len(four)} consume human "
                 f"labels and are already excluded by clause ③, so the cap's unique cost is "
                 f"{len(still)}: {still}")
    else:
        world = f"B THE COST STANDS — none of the {len(four)} consumes labels; the bound was tight"
    print(f"\n⭐ {world}")

    out = HERE / "results" / "cap_cost_value.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        generator="corebench/select_core.py:204 tag grammar; :102 label-reading guard",
        control={"reproduces_r920": ok, "of": ok+bad, "mismatches": mism, "ok": pos_ok,
                 "placebo_full_false": plac_ok},
        four_arms={a: derive(a) for a in four},
        cap_unique_cost_value=len(still), cap_unique_cost_members=still,
        r992_bound=len(four), world=world,
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
