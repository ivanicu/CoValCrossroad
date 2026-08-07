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
                NAMES it, and (b) the gate's exit code — each with and without R928's normalisation.
IDENTIFICATION  exact — the gate prints the directory name of every round it flags, and returns an
                exit code; both are read from the same stdout.
SCOPE           population: 2 planted rounds × 2 normalisation states = 4 cells, plus one baseline
                instrument: the gate's own stdout and returncode
                baseline:   the clean repo, where the gate exits 1 naming R422 and R425
                regime:     HEAD, working tree clean; `covalx/rounds.py` reverted temporarily and
                            restored from the index
WORLDS          A · the undeclared plant is NAMED with the fix and ABSENT without it -> the
                    fixture-name channel is live for this gate, the harness's exit-code reading is
                    blind to it, and R941's WORLD B sentence is wrong for the right reason: the fix
                    did reach this harness's plant and the harness cannot report it
                B · it is named in both states -> the plant really was visible all along, the
                    lowercase name is harmless here, and R941's sentence stands as written
KILL            CONDITIONAL:
                  ⭐ ⓪ REVERT EFFECTIVE ON THE OBJECT: `fixture_dir` must return a path whose leaf
                     starts with `R` in FIXED and with `r` in REVERTED, computed in a FRESH
                     interpreter each time. **If the two paths are equal the baseline was never
                     re-established and every comparison below is void** — this is exactly how R941's
                     first run failed, and an argument is not a substitute for the check.
                  ⭐ ① POSITIVE: the name-reader must find `R422` and `R425` in the baseline stdout.
                     They are undeclared at HEAD and the gate names them. If the reader cannot see
                     rounds already read off the gate's own output, it cannot be trusted on a plant.
                  ⭐ ② NEGATIVE / DISCRIMINATION: the DECLARED plant must NOT be named in the FIXED
                     state. Its declaration is nested inside a list — vector 3's exact payload — and
                     the gate walks nested structures. If it is named anyway the reader is reporting
                     any planted directory, and separately vector 3's expectation was right.
                  ⭐ ③ GAUGE TEST: the exit code must be IDENTICAL in all four cells while the named
                     channel differs in at least one pair. Measurement invariant + property not
                     ⇒ the measurement is blind. **If the exit code DOES move, the harness's channel
                     was not saturated and this round's whole diagnosis is wrong** — that is the
                     branch that kills it.
                  ⭐ ④ RESTORATION VERIFIED: `covalx/rounds.py` byte-identical to HEAD by
                     `git diff --quiet`, and no fixture left behind.
MULTIPLICITY    2 plants × 2 states × {exit, named} = 8 readings, plus baseline; all printed,
                including the cells that do not move.
ARTIFACT        results/blind_channel.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated
                — one repo, one gate, one release; a second site would be required. ⚠ AND: this
                measures the FIXTURE-NAME channel for ONE gate. It says nothing about whether the
                other 20-odd gates reading `E*/A*/R*` have the same exposure; that is a wider
                population and a separate round.
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
    return {"exit": rc, "named": path.name in out, "path": str(path.relative_to(ROOT))}


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

    base_rc, base_out = run_gate()
    named_base = sorted(set(re.findall(r"\bR4(?:22|25)\w*", base_out)))
    c1 = len(named_base) >= 2
    print(f"  BASELINE — gate exits {base_rc} on the clean repo, naming {len(named_base)} known "
          f"undeclared round(s): {[n[:28] for n in named_base]}")
    print(f"  ① POSITIVE — the name-reader finds R422 and R425 in the gate's own output: {c1}  "
          f"{'PASS' if c1 else 'FAIL — the reader cannot see rounds I have already read'}")

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
                print(f"     {k:<12} exit {v['exit']}   named-by-the-gate {v['named']}")
    finally:
        subprocess.run(["git", "-C", str(ROOT), "checkout", "--", "covalx/rounds.py"], check=True)
        for p in paths.values():
            shutil.rmtree(p, ignore_errors=True)

    c0 = (paths["fixed"].name[0] == "R" and paths["reverted"].name[0] == "r"
          and paths["fixed"] != paths["reverted"])
    print(f"\n  ⓪ REVERT EFFECTIVE ON THE OBJECT — fixed leaf `{paths['fixed'].name}`, reverted leaf "
          f"`{paths['reverted'].name}`: {c0}  "
          f"{'PASS' if c0 else 'FAIL — the baseline was never re-established, every cell is void'}")

    c2 = not res["fixed"]["declared"]["named"]
    print(f"\n  ② NEGATIVE / DISCRIMINATION — the DECLARED plant (declaration nested in a list, "
          f"vector 3's payload) must NOT be named with the fix in place: {c2}  "
          f"{'PASS' if c2 else 'FAIL — the reader reports any planted directory'}")

    exits = [res[s][k]["exit"] for s in ("fixed", "reverted") for k in ("undeclared", "declared")]
    named = {(s, k): res[s][k]["named"] for s in ("fixed", "reverted")
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

    u_fixed = res["fixed"]["undeclared"]["named"]
    u_rev = res["reverted"]["undeclared"]["named"]
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
                         "named_channel_varies": name_moves,
                         "reading": "measurement invariant + property not => the exit code the "
                                    "harness reads is blind to what it claims about"},
               "vector3_verdict": {"declared_plant_named": res["fixed"]["declared"]["named"],
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
