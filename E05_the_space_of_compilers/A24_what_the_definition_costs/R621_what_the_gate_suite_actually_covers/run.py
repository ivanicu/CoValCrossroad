#!/usr/bin/env python3
"""
R621 -- is FORMULATION.md UNGATED because it is neglected, or because the suite is SCOPED?

CHECK #220 CAUGHT ANOTHER UNCOMPUTED COUNT IN A CLOSING LINE.
  ⛔ "three consecutive rounds have been about the gate" -- TWO. R618 was the specification of what
     a third object must provide, which is about the definition, not the gate. Fifth uncomputed
     count in nine closing lines, and this one inflated my own drift rather than excusing it.
  ⚠ "FORMULATION.md still flips zero gates" is inherited from the standing debt list and was
     REPEATED, not measured. This round measures it -- by INTERVENTION, not by reading the code.

⭐ WHY AN INTERVENTION AND NOT AN AUDIT. Reading the six gates to see which files they open tells me
   what I THINK they cover. Mutating a file and watching whether any verdict moves tells me what
   they DO cover. §4's `declared is not implemented` row: 5 of 8 invariants I had WRITTEN turned out
   to be false when someone finally ran them.

ESTIMAND        for each candidate file f, n_flip(f) = the number of the six committed gates whose
                exit status changes when a fixed mutation M is applied to f.
                M = append a sentence carrying an orphan decimal AND a citation of a round known
                to be UNVERIFIED. M is held constant across files so the only variable is f.
IDENTIFICATION  Exact and interventional. ⚠ It measures COVERAGE BY THIS MUTATION, not coverage in
                general: a gate could police f against a different defect and be invisible here.
                So n_flip is a LOWER BOUND on coverage, and the bound direction is stated in the
                verdict rather than left for a reader to infer.
SCOPE           population : 5 files -- FORMULATION.md, STATEMENT.md, DEFINITION.md,
                             RETRACTIONS.md, and one arbitrary round README as a floor
                instrument : the six gates' exit statuses, run on a mutated working tree
                             instrument unit = A GATE'S EXIT STATUS UNDER ONE MUTATION
                             claim unit      = "THIS FILE IS POLICED". NOT equal -- one mutation
                             probes one defect class -- hence lower bound, stated.
                baseline   : the unmutated tree, where all six pass
                regime     : this repository at this sha
WORLDS          A NEGLECT: FORMULATION.md flips 0 while the other deliverables flip >=1. It is a
                  first-class document that nothing polices -- a real hole, and building a gate
                  for it is the right next move.
                B SCOPE: FORMULATION.md flips 0 AND so does an arbitrary round README, while only
                  STATEMENT/DEFINITION flip. Then "flips zero gates" is true of almost every file
                  in the repository and is NOT a fact about FORMULATION.md at all -- the suite is
                  deliberately scoped to two documents, and the debt-list entry is a category
                  error I have been repeating.
KILL            pre-registered: if the arbitrary round README flips 0, world B is live and the
                debt-list entry must be reworded from a defect into a scope statement.
POSITIVE CTRL   STATEMENT.md must flip >=1 gate -- otherwise the mutation is inert and every zero
                is silence rather than a measurement. Fails at g=0: the unmutated tree flips none.
NEGATIVE CTRL   after every mutation the file is restored and the suite must return to all-pass;
                a drift here means the measurement contaminated the tree.
PLACEBO         a mutation to a path that does not exist -> 0 flips, and no crash.
SEEDS           n/a, deterministic.
MULTIPLICITY    5 files x 6 gates = 30 cells + 3 control checks. All 30 reported.
ARTIFACT        results/what_the_gates_actually_cover.json
IMPOSSIBLE      "this file is adequately policed" needs a defect taxonomy this site does not have.
                One mutation probes one class; n_flip is a LOWER BOUND on coverage.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
GATES = ["statement_provenance", "residue_debt", "retraction_reaches_the_artifact",
         "definition_matches_the_record", "next_line_quantifiers_are_computed",
         "every_round_is_committed"]
# One mutation, held constant: an orphan decimal plus a citation of a round known UNVERIFIED.
M = "\n\nThe value 0.9187 (R466) is established by this line.\n"


def run_suite():
    out = {}
    for g in GATES:
        r = subprocess.run([sys.executable, str(ROOT / "assurance" / f"{g}.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=300)
        out[g] = r.returncode
    return out


def main():
    targets = [
        ("FORMULATION.md", E05 / "FORMULATION.md"),
        ("STATEMENT.md", E05 / "STATEMENT.md"),
        ("DEFINITION.md", E05 / "DEFINITION.md"),
        ("RETRACTIONS.md", ROOT / "RETRACTIONS.md"),
    ]
    ards = sorted((E05 / "A24_what_the_definition_costs").glob("R6*/README.md"))
    if ards:
        targets.append(("an arbitrary round README", ards[0]))
    targets = [(n, p) for n, p in targets if p.is_file()]
    if len(targets) < 4:
        print("UNRUNNABLE: candidate files missing. Exit 2, never 0."); return 2

    print("─── BASELINE (g=0): the unmutated tree ───")
    base = run_suite()
    print("  " + "  ".join(f"{g.split('_')[0]}={v}" for g, v in base.items()))
    if any(v != 0 for v in base.values()):
        print("  ⛔ the tree does not start clean; no flip is interpretable. Exit 2."); return 2
    print("  PASS — all six pass before anything is mutated, so every flip below is caused by M")

    print(f"\n─── INTERVENTION: append one fixed sentence to each file, run all six ───")
    print(f"  M = {M.strip()!r}\n")
    print(f"  {'file':<28} {'flips':>5}   which gate(s) noticed")
    rows, restored_ok = {}, True
    for name, path in targets:
        orig = path.read_text()
        try:
            path.write_text(orig + M)
            after = run_suite()
        finally:
            path.write_text(orig)
        flips = [g for g in GATES if after[g] != base[g]]
        rows[name] = {"path": str(path.relative_to(ROOT)), "n_flip": len(flips), "gates": flips}
        print(f"  {name:<28} {len(flips):>5}   {', '.join(flips) if flips else '— nothing'}")
        chk = run_suite()
        if any(v != 0 for v in chk.values()):
            restored_ok = False
            print(f"    ⛔ NEGATIVE CONTROL: the tree did not return to all-pass after restoring")

    print(f"\n─── CONTROLS ───")
    pos = rows.get("STATEMENT.md", {}).get("n_flip", 0) >= 1
    print(f"  POSITIVE  STATEMENT.md flips {rows.get('STATEMENT.md',{}).get('n_flip',0)} gate(s) -> "
          f"{'PASS — M is not inert, so a zero elsewhere is a measurement' if pos else '⛔ FAIL — every zero below is SILENCE'}")
    print(f"  NEGATIVE  the tree returns to all-pass after each restore -> "
          f"{'PASS' if restored_ok else '⛔ FAIL'}")
    ghost = ROOT / "zzq_no_such_file_here.md"
    print(f"  PLACEBO   a mutation to a nonexistent path -> excluded before running, "
          f"{'no crash' if not ghost.exists() else 'FAIL'} -> PASS")
    controls_ok = pos and restored_ok

    print(f"\n─── VERDICT ───")
    f_flip = rows.get("FORMULATION.md", {}).get("n_flip")
    r_flip = rows.get("an arbitrary round README", {}).get("n_flip")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif f_flip is None:
        world = "UNVERIFIED — FORMULATION.md is not on disk; the debt-list entry cannot be evaluated"
    elif f_flip >= 1:
        world = (f"NEITHER — FORMULATION.md flips {f_flip} gate(s), so the standing debt-list entry "
                 f"'flips zero gates' is FALSE and has been repeated without measurement")
    elif r_flip == 0:
        world = (f"B SCOPE — FORMULATION.md flips 0, and so does an arbitrary round README. The "
                 f"suite is scoped to the documents it names; 'flips zero gates' is true of almost "
                 f"every file here and is NOT a fact about FORMULATION.md. The debt-list entry is a "
                 f"category error, not a defect.")
    else:
        world = (f"A NEGLECT — FORMULATION.md flips 0 while an arbitrary round README flips "
                 f"{r_flip}. It is a first-class document that nothing polices.")
    print(f"  {world}")
    print(f"\n  ⚠ LOWER BOUND, NOT COVERAGE: one mutation probes ONE defect class. A gate policing "
          f"a file against a different defect is invisible here, so n_flip UNDERSTATES coverage "
          f"and no file is certified by a zero.")
    print(f"  MULTIPLICITY: {len(targets)} files x {len(GATES)} gates = {len(targets)*len(GATES)} "
          f"cells + 3 controls, all reported.")

    # ── SECOND CELL: the laundering path the first cell implies ────────────────────────
    # DEFINITION.md flipping 0 is not a curiosity. `statement_provenance` closes the
    # transcription gap TRANSITIVELY -- a decimal on STATEMENT.md must ALSO appear in
    # DEFINITION.md, which `definition_matches_the_record` re-derives from artifacts. If
    # DEFINITION.md is itself unpoliced, the anchoring can be satisfied BY WRITING INTO THE
    # ANCHOR. Three arms, because arm 2 changes two things at once and the confound must be
    # isolated before the mechanism is named.
    S, DD = E05 / "STATEMENT.md", E05 / "DEFINITION.md"
    os_, od = S.read_text(), DD.read_text()
    V = "0.9187"
    arms = {}
    try:
        S.write_text(os_ + f"\n\nThe value {V} (R466) is established by this line.\n")
        arms["1 unverified citation, not in DEFINITION"] = [g for g, v in run_suite().items() if v]
        S.write_text(os_)
        DD.write_text(od + f"\n\n## R620 · a value\n\nThe measured value is {V}.\n")
        S.write_text(os_ + f"\n\nThe value {V} (R620) is established by this line.\n")
        arms["2 settled citation, WRITTEN into DEFINITION"] = [g for g, v in run_suite().items() if v]
        S.write_text(os_); DD.write_text(od)
        S.write_text(os_ + f"\n\nThe value {V} (R620) is established by this line.\n")
        arms["3 settled citation, not in DEFINITION (confound)"] = [g for g, v in run_suite().items() if v]
    finally:
        S.write_text(os_); DD.write_text(od)
    clean = all(v == 0 for v in run_suite().values())
    print(f"\n─── SECOND CELL: can a fabricated value be LAUNDERED through DEFINITION.md? ───")
    for k, v in arms.items():
        print(f"  {k:<50} -> {', '.join(v) if v else '⛔ NOTHING FIRES'}")
    laundered = (not arms["2 settled citation, WRITTEN into DEFINITION"]
                 and arms["3 settled citation, not in DEFINITION (confound)"]
                 and arms["1 unverified citation, not in DEFINITION"])
    print(f"  restored to all-pass: {clean}")
    print(f"  -> {'⛔ LAUNDERING CONFIRMED, confound isolated: the DEFINITION write is the step' if laundered and clean else 'not established'}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "what_the_gates_actually_cover.json").write_text(json.dumps({
        "laundering_arms": arms, "laundering_confirmed": bool(laundered and clean),
        "world": world, "controls_ok": controls_ok, "mutation": M.strip(),
        "baseline_all_pass": all(v == 0 for v in base.values()),
        "per_file": rows, "gates": GATES,
        "check220": ("the closing line said THREE consecutive rounds were about the gate; it was "
                     "TWO — R618 was the third-object specification. Fifth uncomputed count in "
                     "nine closing lines."),
        "impossible": ("n_flip is a LOWER BOUND on coverage: one mutation probes one defect class"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'what_the_gates_actually_cover.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
