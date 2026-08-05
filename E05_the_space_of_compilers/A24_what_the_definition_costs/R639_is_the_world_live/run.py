#!/usr/bin/env python3
"""
R639 -- is the world that fires on nothing live in committed code, and how many harnesses carry it?

CHECK #240: TWO, AND ONE IS THE THIRD UNCOMPUTED COST CLAIM IN FOUR ROUNDS.
  ⛔ "ONLY ONE harness in the corpus runs rounds" -- never counted. A universal over my own corpus,
     the twenty-sixth.
  ⛔ "cheap to install" -- after "re-runs are expensive" (to avoid work) and "the fix is one line"
     (to justify it), this is the third uncomputed cost claim in four rounds. ⭐ Every one of them
     felt obviously true, and the two that were measured were wrong by 260x and by "there is no fix".

ESTIMAND        ① n_harness = rounds whose run.py subprocess-executes ANOTHER round's run.py;
                ② whether R636's `failed` count reaches a VERDICT branch rather than a print;
                ③ after repair, whether a non-zero-exit round still counts toward world C.
IDENTIFICATION  ① exact by source scan. ② exact by reading the branch. ③ INTERVENTIONAL: plant a
                synthetic exit-1 result and check the classifier's output before and after.
                ⚠ ② is a DERIVATION once read -- the branch either references the count or it does
                not, and it could not have come out otherwise. Labelled, not reported as evidence.
SCOPE           population : every round under A24 with a run.py, self excluded
                instrument : source scan for subprocess-execution of a run.py + branch read
                             instrument unit = A SOURCE LINE
                             claim unit      = A HARNESS. NOT equal: a round can shell out to a
                             GATE without running a ROUND, and only the latter counts.
                baseline   : my claim of exactly one
                regime     : this repository at this sha
WORLDS          A LOCAL AND INERT: one harness, and its `failed` count feeds only a printed line ->
                  the repair is a wording change.
                B LOCAL AND LOAD-BEARING: one harness, but the count feeds the world-C threshold ->
                  the fires-on-nothing derivation is LIVE in committed code and must be repaired.
                C WIDESPREAD: more than one harness -> the prohibition must be installed in each,
                  and my "only one" was wrong.
KILL            pre-registered: the count reaching a verdict branch -> world B at minimum;
                n_harness >= 2 -> world C, reported FIRST because it changes the repair's scope.
POSITIVE CTRL   the scan must find R636, which demonstrably runs rounds. Fails at g=0: a round that
                shells out only to a GATE must NOT be counted as a round-harness.
NEGATIVE CTRL   after the repair, a planted exit-1 round must NOT increment the world-C count,
                while a genuinely unrunnable round (nonexistent path) still must.
PLACEBO         a round that runs nothing -> not counted.
SEEDS           n/a, deterministic.
MULTIPLICITY    313 rounds x 1 scan + 3 intervention cells + 4 controls.
ARTIFACT        results/is_the_world_live.json
IMPOSSIBLE      whether a repaired harness is CORRECT for every future round is untestable here --
                18 meanings for `EXIT 1` (R638) means no classifier can be validated against the
                corpus's semantics, only against the weak prohibition.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SELF = pathlib.Path(__file__).resolve().parent.name
# ⛔ v1's PATTERN MATCHED PATH CONSTRUCTION, NOT EXECUTION -- `/ "run.py"` fires on any round that
#    merely BUILDS a path to a run.py, e.g. to read its source. That is the mention-vs-use error of
#    R631 and R633, a third time. Tightened to require an actual subprocess call whose arguments
#    reach a run.py, and BOTH counts are reported so the inflation is visible rather than corrected
#    in silence.
MENTIONS_ROUND = re.compile(r"[\"']run\.py[\"']")
# ⛔⛔ AND v2 UNDER-MATCHED: it required `run.py` OUTSIDE any parenthesised subexpression, while
#     every real call nests it -- `subprocess.run([str(PY), str(A24 / n / "run.py")], ...)`. The
#     POSITIVE CONTROL caught it by failing on R636, the one round I had watched execute 43 others.
#     v1 over-matched on path construction, v2 under-matched on nesting, and ONLY THE POSITIVE
#     CONTROL DISTINGUISHED THEM. v3: `subprocess.run` and `run.py` within one statement window,
#     validated against the known member before the count is read.
RUNS_ROUND = re.compile(r"subprocess\.run\([^\n]{0,200}?run\.py|subprocess\.run\((?:[^\n]*\n){0,3}?[^\n]*run\.py")
RUNS_GATE = re.compile(r"assurance[\"'/]\s*[^)]*\.py")


def main():
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.name != SELF]
    harness, gateonly, mentions = [], [], []
    for d in rounds:
        src = (d / "run.py").read_text(errors="ignore")
        if RUNS_ROUND.search(src):
            harness.append(d.name)
        elif MENTIONS_ROUND.search(src):
            mentions.append(d.name)
        elif RUNS_GATE.search(src) and "subprocess" in src:
            gateonly.append(d.name)
    print(f"  rounds scanned                       : {len(rounds)}")
    print(f"  harnesses that RUN ANOTHER ROUND     : {len(harness)}  {harness}")
    print(f"  MENTION a run.py path without executing : {len(mentions)}  (v1 counted these)")
    print(f"  shell out to a GATE only (not a round): {len(gateonly)}  {gateonly[:3]}")
    print(f"  my claim was 'only one'              -> "
          f"{'HELD' if len(harness) == 1 else f'REFUTED, there are {len(harness)}'}")

    # ② read the branch -- a DERIVATION, labelled
    r636 = next((d for d in rounds if d.name.startswith("R636")), None)
    src636 = (r636 / "run.py").read_text(errors="ignore") if r636 else ""
    branch = re.search(r"elif len\(failed\) >= len\(names\) / 3:", src636)
    print(f"\n─── ② DOES THE `failed` COUNT REACH A VERDICT BRANCH? (DERIVATION) ───")
    print(f"  `elif len(failed) >= len(names) / 3:` present in R636 -> {bool(branch)}")
    print(f"  => the world-C threshold is computed FROM THE FAILURE COUNT, and R638 established")
    print(f"     that a non-zero exit is a VERDICT in 95 of 313 rounds. So the world that fires on")
    print(f"     nothing is LIVE IN COMMITTED CODE, not a reporting nicety.")

    print(f"\n─── ③ THE REPAIR, AND ITS INTERVENTION ───")
    def classify(rc, path_exists=True):
        """The PROHIBITION: a non-zero exit is UNKNOWN, never failure. Only an unrunnable
        path -- import error, missing file, timeout -- counts as a failure."""
        if not path_exists:
            return "FAILED"
        return "RAN" if rc == 0 else "RAN (non-zero verdict, UNKNOWN)"
    cells = [("exit 0, path exists", 0, True), ("exit 1, path exists", 1, True),
             ("exit 2, path exists", 2, True), ("nonexistent path", 1, False)]
    for label, rc, ex in cells:
        print(f"  {label:<24} -> {classify(rc, ex)}")
    old_failed = sum(1 for _, rc, ex in cells if rc != 0)
    new_failed = sum(1 for _, rc, ex in cells if classify(rc, ex) == "FAILED")
    print(f"  world-C count under the OLD rule: {old_failed} of {len(cells)}   "
          f"under the PROHIBITION: {new_failed} of {len(cells)}")

    print(f"\n─── CONTROLS ───")
    pos = any(h.startswith("R636") for h in harness)
    print(f"  POSITIVE  R636, which demonstrably runs rounds, is found -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = not any(h in gateonly for h in harness)
    print(f"  g=0       gate-only rounds ({len(gateonly)}) are NOT counted as round-harnesses -> "
          f"{'PASS' if g0 else '⛔ FAIL'}")
    neg = classify(1, True) != "FAILED" and classify(1, False) == "FAILED"
    print(f"  NEGATIVE  a planted exit-1 round does NOT count as failed, while an unrunnable path "
          f"still does -> {'PASS' if neg else '⛔ FAIL'}")
    plc = sum(1 for d in rounds if d.name not in harness and d.name not in gateonly
              and "subprocess" not in (d / "run.py").read_text(errors="ignore"))
    print(f"  PLACEBO   {plc} round(s) run nothing and are not counted -> "
          f"{'PASS' if plc > 0 else '⛔ FAIL'}")
    controls_ok = pos and g0 and neg and plc > 0

    print(f"\n─── VERDICT (world C first: it changes the repair's scope) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif len(harness) >= 2:
        world = (f"C WIDESPREAD — {len(harness)} harnesses run rounds: {harness}. My 'only one' was "
                 f"wrong and the prohibition must be installed in each.")
    elif branch:
        world = (f"B LOCAL AND LOAD-BEARING — one harness, and its failure count feeds the "
                 f"world-C threshold directly. The world that fires on nothing is LIVE IN "
                 f"COMMITTED CODE; under the prohibition the same four cells give "
                 f"{new_failed} failures instead of {old_failed}.")
    else:
        world = "A LOCAL AND INERT — one harness and the count feeds only a print."
    print(f"  {world}")
    print(f"\n  ⚠ ② IS A DERIVATION: the branch either references the count or it does not, and it "
          f"could not have come out otherwise. Labelled rather than reported as evidence.")
    print(f"  ⚠ AND THE REPAIRED RULE CANNOT BE VALIDATED AGAINST THE CORPUS'S SEMANTICS: R638 "
          f"found 18 meanings for `EXIT 1`, so no classifier is checkable beyond the weak "
          f"prohibition itself.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "is_the_world_live.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_rounds": len(rounds),
        "harnesses": harness, "gate_only": gateonly, "mention_only": mentions,
        "failed_count_reaches_verdict_branch": bool(branch),
        "world_c_count_old": old_failed, "world_c_count_under_prohibition": new_failed,
        "check240": ("'only one harness' was an uncomputed universal; 'cheap to install' was the "
                     "third uncomputed cost claim in four rounds"),
        "impossible": "no classifier is checkable beyond the prohibition; 18 meanings for EXIT 1",
    }, indent=2))
    print(f"\n  wrote {OUT / 'is_the_world_live.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
