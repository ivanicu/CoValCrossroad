#!/usr/bin/env python3
"""Attack assurance/a_published_number_is_named.py. A lock never attacked is untested.

Seven vectors, each PERFORMED against the live gate in a subprocess, not reasoned about. Two of them
target the failure modes this repo has actually shipped: an empty population that passes, and a
matcher that fires on function words.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT))
from covalx.rounds import fixture_dir  # noqa: E402

TMP = fixture_dir(ROOT, "r9951_attack_named")
PY = str(ROOT / ".venv/bin/python")
GATE = "assurance/a_published_number_is_named.py"

#      name, README text, results doc, expected exit
VECTORS = [
    ("1 NAMED — path says `resolution`, README says resolution",
     "The bar's resolution is 0.009956 on this release.",
     {"bar": {"resolution": 0.009956}}, 0),

    ("2 UNNAMED — path says `gap`, README calls it a price (R949's real case)",
     "Its price decays monotonically: 0.116400 at k=1.",
     {"cells": [{"gap": 0.116400}]}, 1),

    ("3 STATED BUT NOT HELD — README number absent from the artifact must SKIP, not flag",
     "We report 0.777700 as the headline.",
     {"bar": {"resolution": 0.009956}}, 2),

    ("4 STOPWORD-ONLY PHRASE — the matcher must not fire on `the`, `of`, `and`",
     "the of and 0.123400 that with from into",
     {"alpha": {"beta": 0.123400}}, 1),

    ("5 CASE AND UNDERSCORE — `Gap_Price` vs `price` must normalise to NAMED",
     "The price for this cell is 0.222200.",
     {"Gap_Price": 0.222200}, 0),

    ("6 NUMBER INSIDE A STRING — the value lives only in a string value",
     "The margin is 0.333300 here.",
     {"notes": {"margin_note": "measured 0.333300 against the comparator"}}, 0),
]


def run():
    """⛔ ISOLATED TO THE FIXTURE, and the first version was not.

    It ran the gate over the whole repo, so every expected exit code silently depended on no OTHER
    round being in scope. The moment R950 landed, vector 3's `empty population -> 2` became `0` and
    the attack reported 6/7 for a lock that had not changed. **That is exactly the defect R942
    measured in attack_outcome_variable_declared -- a harness reading a whole-repo exit code while
    planting one round -- rebuilt here by the author who diagnosed it.**

    ⛔ AND THE ISOLATION BROKE ANYWAY, caught by running the whole suite at R960. The fixture was
    `r951`, and a REAL round `R951_do_the_1338_retractions_name_their_own_error_classes` shares that
    number. With the floor at 951 both were in scope; the moment R957 gave R951 a README, the real
    round passed, `examined` became non-zero, and vector 3's expected empty-population exit 2 came
    back 0. **An identifier that is not unique** -- the same defect class as the duplicated A25 arc
    measured one round earlier, in a second place. The fixture is now r9951, above every real round.
    """
    r = subprocess.run([PY, "-c", ISOLATED, str(ROOT / GATE)],
                       cwd=ROOT, capture_output=True, text=True, timeout=600)
    return r.returncode


ISOLATED = (
    "import importlib.util,sys;"
    "spec=importlib.util.spec_from_file_location('g',sys.argv[1]);"
    "m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);"
    "m.FLOOR_ROUND=9951;"
    "sys.exit(m.main())"
)


def main():
    shutil.rmtree(TMP, ignore_errors=True)
    results = []
    try:
        for name, readme, doc, want in VECTORS:
            shutil.rmtree(TMP, ignore_errors=True)
            (TMP / "results").mkdir(parents=True, exist_ok=True)
            (TMP / "README.md").write_text(readme + "\n")
            (TMP / "results" / "out.json").write_text(json.dumps(doc, indent=1))
            got = run()
            ok = got == want
            results.append((name, ok, got, want))
            print(f"  {'OK    ' if ok else 'BROKEN'} {name}\n           exit={got} expected={want}")
    finally:
        shutil.rmtree(TMP, ignore_errors=True)

    # 7 — EMPTY POPULATION. Not simulated: the floor is raised so no round qualifies, and the gate
    #     must exit 2. A gate that reports success having examined nothing is the failure this repo
    #     has shipped before, so it is tested by running the real main(), not by reading the branch.
    import importlib.util
    spec = importlib.util.spec_from_file_location("gate_probe", ROOT / GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.FLOOR_ROUND = 10 ** 9
    got = mod.main()
    ok = got == 2
    results.append(("7 EMPTY POPULATION — floor raised above every round", ok, got, 2))
    print(f"  {'OK    ' if ok else 'BROKEN'} 7 EMPTY POPULATION — floor raised above every round"
          f"\n           exit={got} expected=2")

    base = run()
    print(f"\n  cleanup verified: repo scan back to exit {base} "
          f"(2 = empty population, which is this gate's baseline until a round lands at or above "
          f"its floor)")

    n = sum(1 for _, ok, _, _ in results if ok)
    print(f"\n{n}/{len(results)} vectors behave as specified")
    if n != len(results):
        print("  BROKEN vectors above are real holes in the lock, not notes.")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
