"""Point every check at the state it exists to detect: ABSENCE.

Entry 64. Five of six checks returned exit 0 on an empty population -- including
one built two turns earlier specifically to catch delivery failures. Each had
been tested against the defect it hunts and none against having nothing to hunt
in. A `_floor()` was added to each; this verifies it, for all of them, rather
than for the one I happened to demonstrate.

For each check: empty its input, confirm exit 2 (not 0), restore, confirm exit 0.
Everything is restored in a `finally`, and the final line re-runs the live suite
so a broken restore cannot pass silently.

This does NOT replace the per-check attack scripts, which inject the specific
defect each check hunts. It covers the axis those all missed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The interpreter that is RUNNING this file, not a path guessed relative to the
# repo. A clean-clone run (entry 114) found this was the only check that could
# not run from a fresh clone: it invoked <repo>/.venv/bin/python, which exists
# only in the working copy. The first patch wrote `ROOT / sys.executable`, which
# works only because pathlib discards the left side when the right is absolute --
# accidentally correct, so it is written plainly instead.
PY = sys.executable


def run(check: str) -> int:
    return subprocess.run([PY, f"assurance/{check}.py"], cwd=ROOT,
                          capture_output=True, text=True).returncode


def empty_manifest_claims():
    p = ROOT / "assurance/MANIFEST.json"
    bak = p.read_text()
    d = json.loads(bak)
    d["claims"] = []
    p.write_text(json.dumps(d, indent=1))
    return lambda: p.write_text(bak)


def hide_rounds():
    src = ROOT / "rounds"
    tmp = Path(tempfile.mkdtemp(prefix="attack_rounds_"))
    dst = tmp / "rounds"
    shutil.move(str(src), str(dst))
    src.mkdir()
    def restore():
        shutil.rmtree(src, ignore_errors=True)
        shutil.move(str(dst), str(src))
        shutil.rmtree(tmp, ignore_errors=True)
    return restore


def empty_frozen_registry():
    p = ROOT / "covalx/frozen.py"
    bak = p.read_text()
    i = bak.index("REGISTRY = {")
    j = bak.index("}", i)
    p.write_text(bak[:i] + "REGISTRY = {}\n" + bak[j + 1:])
    return lambda: p.write_text(bak)


# (check, how to empty its population, expected exit when emptied, why)
#
# Expected 2 = "observed nothing", the entry-64 floor.
#
# registries_are_satisfied expects 1, and that is the design working rather than
# an exception being carved for it. It enumerates from the REQUIREMENT -- the
# rounds FROZEN.md names -- so emptying the registry does not blind it, it makes
# it report 11 rounds that should be registered and are not. A check that knows
# what OUGHT to exist cannot be silenced by deleting what does. That is exactly
# what entry 60 built it to do, and it is why this row differs.
CASES = [
    ("scope_reaches_the_reader", empty_manifest_claims, 2,
     "zero claims in the manifest -> nothing to check"),
    ("every_round_reaches_the_readme", hide_rounds, 2,
     "zero rounds with results -> nothing to check"),
    ("no_withdrawn_framings", hide_rounds, 2,
     "zero results files to scan -> nothing to check"),
    ("outcome_variable_declared", hide_rounds, 2,
     "zero gold-scored rounds -> nothing to check"),
    ("registries_are_satisfied", empty_frozen_registry, 1,
     "empty registry is a DETECTED FAILURE: FROZEN.md still names 11 rounds"),
    ("results_are_not_degenerate", hide_rounds, 2,
     "zero results files to read -> nothing to check (entry 137)"),
    ("retired_framing_in_emittable_source", hide_rounds, 2,
     "zero source files to parse -> nothing to check (entry 143)"),
]


# Uses sys.executable, NOT a hardcoded .venv path (entry 114). A clean-clone
# run found this check was the only one that could not run from a fresh clone:
# it invoked <repo>/.venv/bin/python, which exists only in the working copy.
def main() -> int:
    results = []
    for check, emptier, want, what in CASES:
        before = run(check)
        restore = None
        try:
            restore = emptier()
            after = run(check)
        finally:
            if restore:
                restore()
        back = run(check)
        ok = (before == 0 and after == want and back == 0)
        results.append((check, before, after, back, ok))
        print(f"  {'OK    ' if ok else 'BROKEN'} {check:32s} live={before} "
              f"empty={after} (want {want}) restored={back}   ({what})")

    print("\n  Emptied must NEVER be 0. Either the check reports it observed nothing (2)")
    print("  or it detects a real failure from a population it did not lose (1).")
    n = sum(1 for *_, ok in results if ok)
    print(f"\n{n}/{len(results)} checks refuse to pass on an empty population")
    if n != len(results):
        print("  A check that passes with no population has not passed -- it has not run.")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
