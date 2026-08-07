#!/usr/bin/env python3
"""
R935 · which assurance checks PASS on silence — no plant in their source AND nothing found on the
        real corpus.

⛔ WHY. Three consecutive rounds found three instrument defects, all in `assurance/`, all making a
check report something other than what it measured, and **none found by running the suite**: R928's
case-mismatched glob (an attack that landed nowhere, reporting 0/5 for a lock it never tested),
R927's loose currency patterns (PASSes that matched unrelated prose), R934's guard applying a refusal
to one branch of two. The register's remedy is to name the instrument's unit and the claim's unit and
require them EQUAL. **That remedy is a judgement, and a judgement I could satisfy with a plausible
list and no measurement**, which is why this round is built around a mechanical version of it.

⭐⭐⭐ **THE MECHANICAL VERSION, AND IT IS WHAT MAKES THE UNITS EQUAL.** The register: *a zero from
an instrument never shown to return non-zero is silence, not an acquittal*. A check earns its zero
two ways — a PLANT in its source, or **having actually fired on the real corpus**, which demonstrates
non-zero output for free. So the defect class is exactly the INTERSECTION:

    no plant in source   AND   zero findings on the corpus   ->   its PASS is silence

The static half alone measures "source contains a plant token", which is NOT the claim's unit. The
dynamic half measures "has this instrument ever returned non-zero here", which IS. **Only the
intersection is admissible, and this round reports both halves so the gap is visible.**

⛔⛔ **AND THIS ROUND WAS DESTROYED ONCE AND REBUILT — the destruction is the more important
finding.** The first run completed, wrote its artifact, and printed it; minutes later the directory
did not exist. Cause, traced to the object: `assurance/attack_the_suite.py:91-98` **MOVES the live
`E0*` campaign directories to `/tmp`**, runs its test against the emptied tree, then
`shutil.rmtree(c)` the live path and moves the stash back. **Anything created at the live path while
the stash is away is destroyed by that rmtree.** This round was written and run inside that window,
so it landed in a freshly-created empty `E05` and was deleted by `restore()`.
⚠ **It is a KNOWN hazard that recurred**: the same gate prints *"12 orphaned `attack_rounds_*`
stashes in /tmp … NOT deleted — R428 found 21 untracked artifacts that existed only inside one."*
⚠ **And the signature is exact and worth carrying:** every COMMITTED round survived — they came back
with the stash — and only the UNCOMMITTED one died. **Commit before running the suite, or do not run
the suite while working.**

⚠ **AND THE POPULATION HAD TO BE SCOPED, because my first pass counted 74 files as gates.** Eight
are tooling or documents, not checks — `apply_*`, `generate_round_index`, `pueue_wait`, `manifest`,
`HEADLINES`, `DEFECTS`, `_poscontrol_defects_unrepaired`. They are excluded BY NAME and the list is
printed, because a population chosen silently is the defect this session has committed most.

⚠ **AND MY FIRST DETECTOR WAS WRONG IN A WAY A SAMPLE CAUGHT.** It looked for words like `plant` and
`positive control` and reported 14 gates as having "no control". Reading three of them showed all
three carry `_floor(...)` or `if not scanned: return 2` — **empty-population refusals under wording
the pattern missed.** Those are a DIFFERENT guarantee: `_floor` stops a check passing on nothing;
only a plant shows it can see something. The two are now measured separately and never conflated.

ESTIMAND        the number of assurance CHECKS whose PASS is silence: no plant in source and zero
                findings when run on the committed corpus.
IDENTIFICATION  exact for the static half; the dynamic half is exact for the gates it runs and is
                reported with its timeouts named rather than folded into the count.
SCOPE           population: `assurance/*.py` minus the 8 named tooling/document files
                instrument: two source regexes + the gate's own exit code
                baseline:   the four gates known to carry plants, used as the detector's control
                regime:     the committed corpus at HEAD
WORLDS          A · a substantial share of checks pass on silence -> the suite's green is partly
                    uninformative and the share is the number to act on
                B · almost none -> the three defects were unlucky rather than systemic
KILL            CONDITIONAL:
                  ⭐ ① DETECTOR POSITIVE CONTROL: the four gates known to carry plants must all be
                     flagged as HAVING one. A detector that misses a known plant cannot be trusted
                     to find a missing one.
                  ⭐ ② DETECTOR NEGATIVE CONTROL: a synthetic source with no plant token must not
                     be flagged and one with a token must be — built at run time so writing this
                     docstring cannot seed the corpus (that failed three times in this project).
                  ⭐ ③ THE UNIT IS DECLARED AND MADE EQUAL: both halves printed, only their
                     INTERSECTION reported as the defect.
                  ⭐ ④ TIMEOUTS NAMED, NOT COUNTED AS ZERO. A gate that does not finish has not
                     been shown to return zero — it is UNKNOWN.
MULTIPLICITY    every check × {plant, empty-refusal, findings}; all three columns printed.
ARTIFACT        results/pass_on_silence.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: "has a plant token" is not "has a WORKING plant" — R934's own
                placebo passed on two empty lists. This bounds the defect from one side only.
"""
import json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
ASSUR = ROOT / "assurance"
NOTGATE = re.compile(r"^(apply_|generate_|pueue_|HEADLINES$|DEFECTS$|manifest$|_poscontrol)")
EMPTY = re.compile(r"_floor\(|if not scanned|if not total|UNRUNNABLE|Exit 2, never 0|"
                   r"empty population", re.I)
PLANT = re.compile(r"\bplant\b|planted|synthetic_control|fixture_dir|sentinel|must be caught|"
                   r"must still be caught|_PLANT|synthetic world|positive control", re.I)
KNOWN_PLANTS = ("no_withdrawn_framings", "a_statement_is_current_with_the_arc",
                "artifacts_are_internally_coherent", "a_detector_marker_matches_something")


def main() -> int:
    files = sorted(ASSUR.glob("*.py"))
    excluded = [f.stem for f in files if NOTGATE.match(f.stem)]
    gates = [f for f in files if not NOTGATE.match(f.stem)]
    print(f"  files {len(files)} · CHECKS {len(gates)} · excluded as tooling/documents "
          f"{len(excluded)}: {excluded}")

    src = {f.stem: f.read_text() for f in gates}
    plant = {k: bool(PLANT.search(v)) for k, v in src.items()}
    empty = {k: bool(EMPTY.search(v)) for k, v in src.items()}

    c1 = all(plant.get(k) for k in KNOWN_PLANTS)
    print(f"\n  ① DETECTOR POSITIVE CONTROL — gates known to carry plants:")
    for k in KNOWN_PLANTS:
        print(f"     {k:<46}{plant.get(k)}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    tok = "syn" + "thetic_" + "control"
    neg_src = "def main():\n    return 0\n"
    pos_src = f"def main():\n    # {tok}\n    return 0\n"
    c2 = (not PLANT.search(neg_src)) and bool(PLANT.search(pos_src))
    print(f"\n  ② DETECTOR NEGATIVE CONTROL — synthetic sources built at run time:")
    print(f"     no-token source flagged: {bool(PLANT.search(neg_src))} (must be False)   "
          f"token source flagged: {bool(PLANT.search(pos_src))} (must be True)")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2},
                  open(OUT / "pass_on_silence.json", "w"), indent=2)
        return 2

    noplant = sorted(k for k in src if not plant[k])
    print(f"\n  ③ THE TWO UNITS, BOTH PRINTED:")
    print(f"     static  — 'source contains a plant token': {len(src)-len(noplant)}/{len(src)} "
          f"have one, {len(noplant)} do not")
    print(f"     static  — 'has an empty-population refusal': {sum(empty.values())}/{len(src)} "
          f"(a DIFFERENT guarantee: stops a pass on nothing, not a blind pass on something)")
    print(f"     dynamic — 'has been shown to return non-zero HERE': measured below for the "
          f"{len(noplant)} without a plant, the only subset where it decides anything")

    dyn, timedout = {}, []
    for k in noplant:
        try:
            r = subprocess.run([str(ROOT / ".venv/bin/python"), str(ASSUR / f"{k}.py")],
                               cwd=ROOT, capture_output=True, text=True, timeout=300)
            dyn[k] = {"exit": r.returncode, "fired": r.returncode != 0}
        except subprocess.TimeoutExpired:
            timedout.append(k)
            dyn[k] = {"exit": None, "fired": None}
        print(f"     {k:<44}exit {dyn[k]['exit']}  fired {dyn[k]['fired']}")

    silent = sorted(k for k in noplant if dyn[k]["fired"] is False)
    fired = sorted(k for k in noplant if dyn[k]["fired"] is True)
    c4 = True
    print(f"\n  ④ TIMEOUTS NAMED — {len(timedout)} gate(s) did not finish and are UNKNOWN, not "
          f"zero: {timedout}")

    print(f"\n  ⭐⭐⭐ PASS ON SILENCE — no plant AND nothing found on the corpus: "
          f"{len(silent)} of {len(gates)} checks ({len(silent)/len(gates):.0%})")
    for k in silent:
        print(f"     {k:<46}empty-refusal {empty[k]}")
    print(f"\n     and {len(fired)} of the {len(noplant)} plant-less checks HAVE fired here, which")
    print(f"     is the positive control obtained for free — their zeros would be earned:")
    for k in fired:
        print(f"     {k:<46}exit {dyn[k]['exit']}")

    world = "A" if len(silent) / len(gates) > 0.10 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"{len(silent)/len(gates):.0%} of the suite's checks pass on silence — a green run from "
        f"them is not evidence, and that share is the number to act on."
        if world == "A" else
        f"only {len(silent)/len(gates):.0%} pass on silence; most zeros in this suite are earned."))
    print(f"     ⚠ BOUNDED FROM ONE SIDE ONLY: 'has a plant token' is not 'has a WORKING plant' — "
          f"R934's own placebo compared two empty lists and passed, so this UNDERSTATES it.")
    print(f"     ⛔ AND THE ROUND'S OWN HAZARD: `attack_the_suite.py` MOVES the live E0* trees to")
    print(f"     /tmp and rmtree's the live path on restore, so anything created during its run is")
    print(f"     destroyed. This round was killed that way once. COMMITTED work survived; only the")
    print(f"     uncommitted round died. Commit before running the suite.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "n_files": len(files), "n_checks": len(gates), "excluded_as_tooling": excluded,
               "static_plant": plant, "static_empty_refusal": empty, "dynamic": dyn,
               "timed_out_unknown": timedout,
               "pass_on_silence": silent, "plantless_but_fired": fired,
               "share_pass_on_silence": len(silent) / len(gates),
               "units": {"static": "source contains a plant token",
                         "claim": "has been shown to return non-zero here",
                         "made_equal_by": "the intersection: no plant AND zero findings"},
               "destruction_hazard": {
                   "what": "assurance/attack_the_suite.py moves the live E0* trees to /tmp, then "
                           "rmtree's the live path before moving the stash back",
                   "effect": "anything created at the live path during its run is destroyed",
                   "evidence": "this round was written, run and its artifact printed, then the "
                               "directory did not exist; every COMMITTED round survived",
                   "known_before": "the gate itself prints that R428 found 21 untracked artifacts "
                                   "existing only inside an orphaned stash",
                   "remedy": "commit before running the suite, or do not run it while working"},
               "bounded_one_side": "'has a plant token' is not 'has a WORKING plant'",
               "unit_note": "counts are CHECKS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "pass_on_silence.json", "w"), indent=2)
    print(f"\n  artifact: results/pass_on_silence.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
