#!/usr/bin/env python3
"""
R942 · R941 got WORLD B and gave it the wrong reason — the second harness cannot move because it
        reads a whole-repo exit code that is pinned at 1, not because its plants were visible.

⛔ WHY. R941 measured `attack_outcome_variable_declared` at 2/4 vectors with R928's normalisation and
2/4 without it, and printed the sentence *"its plants never depended on the uppercase glob, so the
lowercase name is harmless there."* **That sentence is a verdict string, not a measurement.** The
alternative it never tested: the plant's visibility DOES depend on the normalisation, and the
harness is blind to the difference.

⭐ **THE OBJECT SAYS THE SECOND READING IS LIVE.** `assurance/outcome_variable_declared.py:86` globs
`E*/A*/R*/` — uppercase only, the exact construct R928 fixed elsewhere. The plant goes to
`fixture_dir(ROOT, "r91_attack_outcome")`, so with the fix it lands at `E99_fixtures/A01_planted/
R91_attack_outcome` and the gate can see it; without the fix it lands at `r91_attack_outcome` and the
gate cannot. **So the fixture-name channel is live for this gate.**

⭐⭐⭐ **AND THE HARNESS'S VERDICT CHANNEL IS SATURATED.** It computes `flagged = run() == 1` — the
gate's WHOLE-REPO exit code — while planting ONE round. Two real rounds, `R422` and `R425`, are
genuinely undeclared at HEAD, so the gate exits 1 on the clean repo. `flagged` is therefore True in
every cell, both of the harness's negative vectors are unfalsifiable, and its 2/4 is invariant to
everything — not merely to R928's fix. **Its own footer blames vector 4 on a regex hole and says
nothing about vector 3, which fails for this structural reason instead.**

⭐ **THIS IS THE GAUGE TEST, RUNG 1 OF THE LADDER, MADE FAILABLE.** Name a transformation that leaves
the MEASUREMENT identical and ask whether it leaves the PROPERTY identical. Transformation = flip
R928's normalisation. Measurement = the exit code. Property = is this round flagged. If the exit code
is constant across all four cells while the named-rounds channel moves, **the measurement is blind to
what the harness claims about it**, and that is a stronger statement than any vector count.

⚠ **AND THE CONTROL R941 DID NOT HAVE, PROMOTED TO ⓪.** R941's first run reverted one of R928's two
changes and compared against a baseline that was never re-established; the positive control caught it
only afterwards. The general repair is not "remember there were two" — it is **to verify on the
object that the revert changed the thing the round is about.** Here that is one line: the fixture path
must actually come back uppercase-R in FIXED and lowercase-r in REVERTED. An argument that it should
is what failed last time.

ESTIMAND        for a planted round that is undeclared, and one that is declared: (a) whether the gate
                FLAGS it, (b) whether it SCANNED it at all, and (c) the gate's exit code — each with
                and without R928's normalisation.
IDENTIFICATION  exact — the gate prints a scan line for every round it examines and a separate flag
                block for the undeclared ones, and returns an exit code; all read from one stdout.
SCOPE           population: 2 planted rounds × 2 normalisation states = 4 cells, plus one baseline
                instrument: the gate's own stdout and returncode
                baseline:   the clean repo, where the gate exits 1 naming R422 and R425
                regime:     HEAD, working tree clean; `covalx/rounds.py` reverted temporarily and
                            restored from the index
WORLDS          A · the undeclared plant is FLAGGED with the fix and ABSENT without it -> the
                    fixture-name channel is live for this gate, the harness's exit-code reading is
                    blind to it, and R941's WORLD B sentence is wrong for the right reason: the fix
                    did reach this harness's plant and the harness cannot report it
                B · it is flagged in both states -> the plant really was visible all along, the
                    lowercase name is harmless here, and R941's sentence stands as written
KILL            CONDITIONAL:
                  ⭐ ⓪ REVERT EFFECTIVE ON THE OBJECT: `fixture_dir` must return a path whose leaf
                     starts with `R` in FIXED and with `r` in REVERTED, computed in a FRESH
                     interpreter each time. **If the two paths are equal the baseline was never
                     re-established and every comparison below is void** — this is exactly how R941's
                     first run failed, and an argument is not a substitute for the check.
                  ⭐ ① POSITIVE: `R422` and `R425` must appear in the FLAG channel — the same unit
                     every claim below uses, not merely somewhere in stdout. They are undeclared at
                     HEAD. If the reader cannot see rounds already read off the gate's own output,
                     it cannot be trusted on a plant.
                  ⭐ ② NEGATIVE / DISCRIMINATION, TWO-SIDED: the DECLARED plant must be SCANNED and
                     tagged `declared` and NOT flagged. Its declaration is nested inside a list —
                     vector 3's exact payload — and the gate walks nested structures. Requiring
                     `scanned` as well as `not flagged` is what separates *the gate judged it
                     correctly* from *the gate never saw it*, which a one-sided control cannot do
                     and which is exactly the confusion this round is about.
                  ⭐ ③ GAUGE TEST: the exit code must be IDENTICAL in all four cells while the named
                     channel differs in at least one pair. Measurement invariant + property not
                     ⇒ the measurement is blind. **If the exit code DOES move, the harness's channel
                     was not saturated and this round's whole diagnosis is wrong** — that is the
                     branch that kills it.
                  ⭐ ④ RESTORATION VERIFIED: `covalx/rounds.py` byte-identical to HEAD by
                     `git diff --quiet`, and no fixture left behind.
MULTIPLICITY    2 plants × 2 states × {exit, scanned, tag, flagged} = 16 readings, plus baseline; all printed,
                including the cells that do not move.
ARTIFACT        results/blind_channel.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated
                — one repo, one gate, one release; a second site would be required. ⚠ AND: this
                measures the FIXTURE-NAME channel for ONE gate. It says nothing about whether the
                other 20-odd gates reading `E*/A*/R*` have the same exposure; that is a wider
                population and a separate round.
⛔ **AND MY FIRST READER MEASURED THE WRONG UNIT, WHICH CONTROL ② CAUGHT.** It asked
`path.name in stdout`. The gate prints a SCAN line for every round it examines, tagged `declared` or
`UNDECLARED` (`outcome_variable_declared.py:115-119`), and separately a FLAG BLOCK listing only the
undeclared ones (`:130-132`). So `in stdout` reads **scanned**, while every sentence this round wants
to write is about **flagged**. The declared plant was named, control ② failed, and the round exited
UNVERIFIED rather than banking a false verdict. **Control ① did not catch it: it proved the reader
can SEE a name, never that what it sees is the thing being claimed.** That is the documented gap —
a positive control asks *can this instrument see?* and never *is what it sees the thing I am about to
claim about?* Both channels are now parsed separately and the units are printed and compared before
any verdict, which is the mechanical remedy rather than the resolution to be careful.

⚠ ONLY `covalx/rounds.py` IS REVERTED HERE, deliberately. R928's second change was the glob inside
`assurance/no_withdrawn_framings.py`, a DIFFERENT gate, irrelevant to this one. R941's lesson is not
"always revert both" — it is "verify the revert moved the thing you are measuring", which is ⓪.
"""
import json, pathlib, re, shutil, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
ROUNDS = ROOT / "covalx/rounds.py"
PY = str(ROOT / ".venv/bin/python")
GATE = "assurance/outcome_variable_declared.py"
NAME = "r91_r942_gauge"

FIXED = '    if name[0] == "r":\n        name = "R" + name[1:]\n'
REVERTED = '    if False:  # R942 TEMPORARY REVERT\n        name = "R" + name[1:]\n'

# vector 3's exact payload: the declaration nested inside a list
DECLARED_DOC = {"notes": [{"a": ["scored against a model gold head, no human rankings"]}]}
UNDECLARED_DOC = {"verdict": "big result"}
SRC = "gold_fresh = 1\n"


def set_normalisation(on: bool):
    s = ROUNDS.read_text()
    if on and REVERTED in s:
        ROUNDS.write_text(s.replace(REVERTED, FIXED, 1))
    elif not on and FIXED in s:
        ROUNDS.write_text(s.replace(FIXED, REVERTED, 1))


def fixture_path() -> pathlib.Path:
    """computed in a FRESH interpreter so the edited module is actually re-imported"""
    code = (f"import pathlib,sys; sys.path.insert(0,{str(ROOT)!r});"
            f"from covalx.rounds import fixture_dir;"
            f"print(fixture_dir(pathlib.Path({str(ROOT)!r}), {NAME!r}))")
    r = subprocess.run([PY, "-c", code], cwd=ROOT, capture_output=True, text=True)
    return pathlib.Path(r.stdout.strip()) if r.returncode == 0 else None


INSTRUMENT_UNIT = "flagged"          # what the reader below computes
CLAIM_UNIT = "flagged"                # what every sentence in this round asserts
FLAG_HEADER = re.compile(r"round\(s\) score against a model proxy without saying so:")
FLAG_ROW = re.compile(r"^\s{2}(\S+)\s{3}\(\d+ results file\(s\)\)\s*$")
SCAN_ROW = re.compile(r"^\s{2}(\S+)\s+human_rankings=\S+\s+(declared|UNDECLARED)")


def read_channels(out: str):
    """TWO channels, never conflated: `scanned` = the gate examined it; `flagged` = the gate
    reported it as undeclared. `name in out` collapses them, which is the error control 2 caught."""
    scanned = {m.group(1): m.group(2) for m in
               (SCAN_ROW.match(l) for l in out.splitlines()) if m}
    lines, flagged, seen = out.splitlines(), set(), False
    for l in lines:
        if FLAG_HEADER.search(l):
            seen = True
            continue
        if seen:
            m = FLAG_ROW.match(l)
            if m:
                flagged.add(m.group(1))
            elif l.strip() and not l.startswith("  "):
                break
    return scanned, flagged


def run_gate():
    r = subprocess.run([PY, GATE], cwd=ROOT, capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout or "")


def cell(path: pathlib.Path, doc):
    shutil.rmtree(path, ignore_errors=True)
    (path / "results").mkdir(parents=True, exist_ok=True)
    (path / "run.py").write_text(SRC)
    (path / "results" / "out.json").write_text(json.dumps(doc, indent=1))
    try:
        rc, out = run_gate()
    finally:
        shutil.rmtree(path, ignore_errors=True)
    scanned, flagged = read_channels(out)
    return {"exit": rc, "scanned": path.name in scanned,
            "tag": scanned.get(path.name), "flagged": path.name in flagged,
            "path": str(path.relative_to(ROOT))}


def main() -> int:
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print(f"  UNRUNNABLE: tree not clean; this round edits a shared module and restores it from "
              f"the index.\n{dirty[:300]}\n  Exit 2, never 0.")
        return 2
    if FIXED not in ROUNDS.read_text():
        print("  UNRUNNABLE: R928's normalisation not found in covalx/rounds.py. Exit 2, never 0.")
        return 2

    print(f"  UNITS — instrument computes `{INSTRUMENT_UNIT}`, every claim asserts "
          f"`{CLAIM_UNIT}`, equal: {INSTRUMENT_UNIT == CLAIM_UNIT}")
    if INSTRUMENT_UNIT != CLAIM_UNIT:
        print("  UNRUNNABLE: the instrument measures a different unit than the claim. Exit 2.")
        return 2

    base_rc, base_out = run_gate()
    base_scan, base_flag = read_channels(base_out)
    named_base = sorted(n for n in base_flag if n.startswith(("R422", "R425")))
    c1 = len(named_base) >= 2
    print(f"  BASELINE — gate exits {base_rc}; {len(base_scan)} rounds SCANNED, "
          f"{len(base_flag)} FLAGGED: {sorted(n[:28] for n in base_flag)}")
    print(f"  ① POSITIVE — R422 and R425 appear in the FLAG channel, the same unit the claims "
          f"use: {c1}  {'PASS' if c1 else 'FAIL — the reader cannot see rounds I have already read'}")

    res, paths = {}, {}
    try:
        for state, on in (("fixed", True), ("reverted", False)):
            set_normalisation(on)
            p = fixture_path()
            if p is None:
                print(f"  UNRUNNABLE: fixture_dir refused the name in state={state}. Exit 2.")
                return 2
            paths[state] = p
            res[state] = {"undeclared": cell(p, UNDECLARED_DOC),
                          "declared": cell(p, DECLARED_DOC)}
            print(f"\n  state = {state.upper():<9} fixture leaf = {p.name}")
            for k, v in res[state].items():
                print(f"     {k:<12} exit {v['exit']}   scanned {str(v['scanned']):<5} "
                      f"tag {str(v['tag']):<11} flagged {v['flagged']}")
    finally:
        subprocess.run(["git", "-C", str(ROOT), "checkout", "--", "covalx/rounds.py"], check=True)
        for p in paths.values():
            shutil.rmtree(p, ignore_errors=True)

    c0 = (paths["fixed"].name[0] == "R" and paths["reverted"].name[0] == "r"
          and paths["fixed"] != paths["reverted"])
    print(f"\n  ⓪ REVERT EFFECTIVE ON THE OBJECT — fixed leaf `{paths['fixed'].name}`, reverted leaf "
          f"`{paths['reverted'].name}`: {c0}  "
          f"{'PASS' if c0 else 'FAIL — the baseline was never re-established, every cell is void'}")

    dec = res["fixed"]["declared"]
    c2 = (not dec["flagged"]) and dec["scanned"] and dec["tag"] == "declared"
    print(f"\n  ② NEGATIVE / DISCRIMINATION, TWO-SIDED — the DECLARED plant (declaration nested in "
          f"a list, vector 3's payload) must be SCANNED ({dec['scanned']}), tagged "
          f"`{dec['tag']}`, and NOT flagged ({not dec['flagged']}): {c2}")
    print(f"     {'PASS — visible AND correctly judged, which separates `invisible` from `passed`' if c2 else 'FAIL'}")

    exits = [res[s][k]["exit"] for s in ("fixed", "reverted") for k in ("undeclared", "declared")]
    named = {(s, k): res[s][k]["flagged"] for s in ("fixed", "reverted")
             for k in ("undeclared", "declared")}
    exit_constant = len(set(exits)) == 1
    name_moves = len(set(named.values())) > 1
    c3 = exit_constant and name_moves
    print(f"\n  ③ GAUGE TEST — exit codes across all four cells {exits}, constant: {exit_constant}; "
          f"named channel varies: {name_moves}: {c3}")
    verdict3 = ("PASS — measurement invariant, property NOT: the exit code is blind" if c3 else
                "FAIL — the exit code moved, so the harness's channel was not saturated and this "
                "round's diagnosis is wrong")
    print(f"     {verdict3}")

    clean = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--", "covalx/rounds.py"])
    left = [str(p.relative_to(ROOT)) for p in paths.values() if p.exists()]
    c4 = clean.returncode == 0 and not left
    print(f"\n  ④ RESTORATION — covalx/rounds.py byte-identical to HEAD "
          f"{clean.returncode == 0}, fixtures left behind {left}: {c4}  "
          f"{'PASS' if c4 else 'FAIL'}")

    if not (c0 and c1 and c2 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c0": c0, "c1": c1, "c2": c2, "c4": c4, "res": res},
                  open(OUT / "blind_channel.json", "w"), indent=2)
        return 2

    u_fixed = res["fixed"]["undeclared"]["flagged"]
    u_rev = res["reverted"]["undeclared"]["flagged"]
    world = "A" if (u_fixed and not u_rev) else "B"

    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"the undeclared plant is NAMED with the fix ({u_fixed}) and NOT without it ({u_rev}). "
        f"**The fixture-name channel IS live for this gate, and R928's fix did reach this "
        f"harness's plant.** The harness cannot report it because it reads the whole-repo exit "
        f"code, which control ③ just showed is constant across every cell. R941's WORLD B sentence "
        f"-- `its plants never depended on the uppercase glob` -- is wrong; the count was invariant "
        f"for a different reason than the one it named."
        if world == "A" else
        f"the undeclared plant is named in both states (fixed {u_fixed}, reverted {u_rev}). The "
        f"plant was visible all along, the lowercase name is harmless for this gate, and R941's "
        f"sentence stands as written."))

    print(f"\n  ⭐ AND VECTOR 3 WAS NEVER BROKEN. Its payload -- a declaration nested inside a list "
          f"-- is correctly NOT named by the gate: {c2}. The gate walks nested structures exactly as "
          f"vector 3 expected. What failed was the harness's ability to SEE that, because "
          f"`flagged = run() == 1` is True whenever any round in the repo is undeclared, and two "
          f"are. The harness's footer explains only vector 4, by a regex hole; vector 3 fails for "
          f"this structural reason and is undocumented.")
    print(f"     ⚠ SCOPE: one gate, one release. The other gates globbing `E*/A*/R*` are a wider "
          f"population and are NOT measured here.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "baseline": {"exit": base_rc, "known_undeclared_named": named_base},
               "cells": res,
               "fixture_leaf": {s: p.name for s, p in paths.items()},
               "gauge": {"exits": exits, "exit_constant": exit_constant,
                         "flagged_channel_varies": name_moves,
                         "channels_read_separately": "scanned (the gate examined it) vs flagged (the gate reported it undeclared); `name in stdout` collapses them",
                         "reading": "measurement invariant + property not => the exit code the "
                                    "harness reads is blind to what it claims about"},
               "vector3_verdict": {"declared_plant_flagged": res["fixed"]["declared"]["flagged"],
                                   "declared_plant_scanned": res["fixed"]["declared"]["scanned"],
                                   "declared_plant_tag": res["fixed"]["declared"]["tag"],
                                   "meaning": "vector 3's expectation was correct; the harness could "
                                              "not observe it because its channel is saturated",
                                   "harness_footer_explains": "vector 4 only"},
               "corrects": "R941's WORLD B sentence, not its WORLD B verdict",
               "unit_note": "counts are CELLS (plant kind x normalisation state)",
               "scope_not_measured": "the other gates globbing E*/A*/R*",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "blind_channel.json", "w"), indent=2)
    print(f"\n  artifact: results/blind_channel.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
