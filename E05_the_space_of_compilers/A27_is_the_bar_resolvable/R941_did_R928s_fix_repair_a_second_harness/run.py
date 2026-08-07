#!/usr/bin/env python3
"""
R941 · R928 fixed one harness and measured one. A second uses the same lowercase fixture name —
        did the one-line fix silently repair it too?

⛔ WHY. R928 found `attack_no_withdrawn_framings` planting at `fixture_dir(ROOT, "r90_attack_tmp")`
— lowercase `r90` — while every gate globbed `E*/A*/R*`, uppercase only. The plants were invisible,
the harness reported **0/5 vectors caught** for a lock it had never tested, and the arc cited that
0/5 seventeen times. The fix normalised the leading `r` to `R` inside `fixture_dir`, at the
invariant rather than at 27 call sites. **R928 then verified exactly one harness.**

⭐ **A SECOND HARNESS USES THE SAME CONSTRUCT:** `attack_outcome_variable_declared` plants at
`fixture_dir(ROOT, "r91_attack_outcome")` — lowercase `r91`. If visibility is what its vectors
depend on, it was reporting a false result too, and R928's fix repaired it **without anyone
measuring that it had.** A fix credited for one repair may have made two; a fix credited for two
when it made one is the same error mirrored. Both are worth knowing, and only a measurement tells
them apart.

⛔ **AND MY FIRST REVERT WAS INCOMPLETE, WHICH CONTROL ① CAUGHT BEFORE ANY CONCLUSION.** R928 made
TWO changes, not one: `fixture_dir`'s case normalisation in `covalx/rounds.py`, AND the glob in
`assurance/no_withdrawn_framings.py` from `E*/A*/R*` to `E*/A*/[Rr]*`. Reverting only the first left
the second in place, the gate still accepted lowercase, and the known harness stayed at 5/5 in both
states — **a revert that does not restore the baseline makes the comparison meaningless**, and the
positive control refused it rather than letting the second harness's number be read against a
baseline that was never established. Both changes are reverted now.

⚠ **NOT FORCED.** `attack_no_withdrawn_framings` plants JSON that a corpus-scanning gate must find,
so visibility is everything to it. `attack_outcome_variable_declared` plants a `run.py` — whether
the gate it attacks discovers round SOURCES by the same uppercase glob is a fact about that gate, not
about `fixture_dir`. It may have been unaffected all along.

ESTIMAND        the vector catch count of each `fixture_dir`-using harness, with and without R928's
                case normalisation.
IDENTIFICATION  exact — the harnesses print `N/M vectors` and the normalisation is one branch.
SCOPE           population: the 5 committed attack harnesses; 2 use `fixture_dir`, 3 plant into
                            live files and are the placebo
                instrument: each harness's own reported vector count
                baseline:   the committed tree, with the fix in place
                regime:     HEAD, working tree clean; the normalisation is reverted temporarily and
                            restored from the index
WORLDS          A · the second harness also changes -> R928 repaired two and reported one; the
                    fix's value was understated and the arc's 0/5 story has a sibling
                B · it does not change -> its plants never depended on that glob, R928's claim was
                    exactly the right size, and the lowercase name is harmless there
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / REPRODUCE THE KNOWN ONE: `attack_no_withdrawn_framings` must go
                     5/5 with the fix and 0/5 without it. **If R928's own result does not
                     reproduce, the method is not measuring what R928 measured** and the second
                     harness's number means nothing.
                  ⭐ ② PLACEBO: the three harnesses that plant into live files — `README.md`,
                     `ASSURANCE.md`, `MANIFEST.json` — must be UNAFFECTED by the normalisation,
                     because they never call `fixture_dir`. If one moves, the revert is doing
                     something other than what it claims.
                  ⭐ ③ RESTORATION VERIFIED: after the run, `covalx/rounds.py` must be byte-identical
                     to HEAD, checked with `git diff --quiet`, not assumed.
                  ⭐ ④ every harness's count is reported both ways, including the ones that do not
                     move.
MULTIPLICITY    5 harnesses × 2 states (fixed, reverted) × {exit, vectors}; all printed.
ARTIFACT        results/second_harness.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: `attack_the_suite` hides the live campaign trees, so it is
                reported from its committed behaviour and NOT re-run twice here — running it four
                extra times to measure a fixture-name effect it does not use would be cost with no
                information, and it is the one harness that can destroy work.
"""
import json, pathlib, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
ROUNDS = ROOT / "covalx/rounds.py"
NWF = ROOT / "assurance/no_withdrawn_framings.py"
PY = str(ROOT / ".venv/bin/python")
FIXTURE_USERS = ("attack_no_withdrawn_framings", "attack_outcome_variable_declared")
LIVE_PLANTERS = ("attack_every_check", "attack_scope_reaches_the_reader")
SKIP = ("attack_the_suite",)
VEC = re.compile(r"(\d+)\s*/\s*(\d+)\s+vectors")


def run_harness(name, timeout=600):
    r = subprocess.run([PY, f"assurance/{name}.py"], cwd=ROOT,
                       capture_output=True, text=True, timeout=timeout)
    m = VEC.search(r.stdout or "")
    return {"exit": r.returncode,
            "vectors": [int(m.group(1)), int(m.group(2))] if m else None}


def set_normalisation(on: bool):
    """R928 made TWO changes; reverting one leaves the other sufficient. Both, or neither."""
    s = ROUNDS.read_text()
    fixed = '    if name[0] == "r":\n        name = "R" + name[1:]\n'
    reverted = '    if False:  # R941 TEMPORARY REVERT\n        name = "R" + name[1:]\n'
    if on and reverted in s:
        ROUNDS.write_text(s.replace(reverted, fixed, 1))
    elif not on and fixed in s:
        ROUNDS.write_text(s.replace(fixed, reverted, 1))
    g = NWF.read_text()
    g_fixed = 'glob("E*/A*/[Rr]*/results/**/*.json")'
    g_rev = 'glob("E*/A*/R*/results/**/*.json")'
    if on and g_rev in g:
        NWF.write_text(g.replace(g_rev, g_fixed, 1))
    elif not on and g_fixed in g:
        NWF.write_text(g.replace(g_fixed, g_rev, 1))


def main() -> int:
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print(f"  UNRUNNABLE: tree not clean; this round edits a shared module and restores it "
              f"from the index.\n{dirty[:300]}\n  Exit 2, never 0.")
        return 2
    if '    if name[0] == "r":' not in ROUNDS.read_text():
        print("  UNRUNNABLE: R928's normalisation not found in covalx/rounds.py. Exit 2, never 0.")
        return 2

    names = FIXTURE_USERS + LIVE_PLANTERS
    res = {}
    print("  state = FIXED (R928's normalisation in place)")
    for n in names:
        res.setdefault(n, {})["fixed"] = run_harness(n)
        print(f"     {n:<38}{res[n]['fixed']}")

    set_normalisation(False)
    print("\n  state = REVERTED (lowercase fixture names again)")
    try:
        for n in names:
            res[n]["reverted"] = run_harness(n)
            print(f"     {n:<38}{res[n]['reverted']}")
    finally:
        subprocess.run(["git", "-C", str(ROOT), "checkout", "--", "covalx/rounds.py",
                        "assurance/no_withdrawn_framings.py"], check=True)

    clean = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "--",
                            "covalx/rounds.py", "assurance/no_withdrawn_framings.py"])
    c3 = clean.returncode == 0
    print(f"\n  ③ RESTORATION VERIFIED — both edited files byte-identical to HEAD: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")

    k = "attack_no_withdrawn_framings"
    fv, rv = res[k]["fixed"]["vectors"], res[k]["reverted"]["vectors"]
    c1 = fv == [5, 5] and rv == [0, 5]
    print(f"\n  ① POSITIVE — R928's own result reproduced for `{k}`: fixed {fv}, reverted {rv}: "
          f"{c1}  {'PASS' if c1 else 'FAIL — the method is not measuring what R928 measured'}")

    moved_live = [n for n in LIVE_PLANTERS
                  if res[n]["fixed"] != res[n]["reverted"]]
    c2 = not moved_live
    print(f"\n  ② PLACEBO — harnesses that plant into LIVE files must not move: "
          f"{'none moved' if c2 else moved_live}: {c2}  {'PASS' if c2 else 'FAIL'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "res": res},
                  open(OUT / "second_harness.json", "w"), indent=2)
        return 2

    k2 = "attack_outcome_variable_declared"
    f2, r2 = res[k2]["fixed"]["vectors"], res[k2]["reverted"]["vectors"]
    changed = f2 != r2
    world = "A" if changed else "B"
    print(f"\n  ④ EVERY HARNESS, BOTH STATES:")
    for n in names:
        print(f"     {n:<38}fixed {str(res[n]['fixed']['vectors']):<10}"
              f"reverted {str(res[n]['reverted']['vectors']):<10}"
              f"{'MOVED' if res[n]['fixed'] != res[n]['reverted'] else 'same'}")
    print(f"     {'attack_the_suite':<38}NOT RE-RUN — it hides the live campaign trees; four extra "
          f"runs to measure a fixture name it does not use would be cost with no information")

    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"`{k2}` ALSO moves — fixed {f2}, reverted {r2}. **R928's one-line fix repaired TWO "
        f"harnesses and reported one.** The second was planting invisibly under the same lowercase "
        f"name and nobody measured it."
        if changed else
        f"`{k2}` does NOT move — fixed {f2}, reverted {r2}. Its plants never depended on the "
        f"uppercase glob, so R928's claim was exactly the right size and the lowercase name is "
        f"harmless there. **A fix credited for one repair made one.**"))
    print(f"     ⚠ EITHER WAY this measures the FIXTURE-NAME channel only. A harness can still be "
          f"blind for reasons that have nothing to do with where it plants.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "results": res,
               "known_reproduced": {"harness": k, "fixed": fv, "reverted": rv},
               "prediction_target": {"harness": k2, "fixed": f2, "reverted": r2,
                                     "changed": bool(changed)},
               "placebo_live_planters": {n: res[n] for n in LIVE_PLANTERS},
               "not_rerun": {"attack_the_suite": "hides the live campaign trees; it does not use "
                                                 "fixture_dir, so four extra runs would be cost "
                                                 "with no information"},
               "restoration_verified": bool(c3),
               "scope": "the FIXTURE-NAME channel only; a harness can be blind for other reasons",
               "unit_note": "counts are VECTORS within a harness",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "second_harness.json", "w"), indent=2)
    print(f"\n  artifact: results/second_harness.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
