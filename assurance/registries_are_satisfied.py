"""Verify the stampers' work by enumerating from the REQUIREMENT, not from what they could see.

Three consecutive failures had one shape:

  * `ASSURANCE.md` rendered `statement[:110]` and reported claims as present
  * `results_match_their_code.py` took `max()` over a round's results, so one
    current file hid four stale ones
  * `apply_freeze_status.py` looked only for a field named `verdict`, printed
    "20/20", and had silently missed three rounds using `conclusion` or nothing

Each tool reported completeness **over its own visible subset**. None was wrong
about what it saw; each was wrong about what it had been asked to cover.

The correction is structural: enumerate from the registry -- the list of things
that MUST carry an annotation -- and check each one, rather than counting what a
walker happened to reach. A round in a registry with zero inspectable files is
then a LOUD failure, not an absence from the denominator.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   every artifact entitled to an annotation carries it
  PROXY      for each registry entry, every non-smoke results JSON contains the
             registry's marker string somewhere
  IMPLICATION  missing => not carried, definitely.
               carried => the string is in the file, which is NOT the same as
               the annotation being correct or the reader finding it.
  SAFE SIDE  flags omission. It cannot judge whether a freeze or scope is the
             RIGHT one for a round -- only that the round was not skipped.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from covalx.frozen import REGISTRY as FROZEN  # noqa: E402


def results_of(round_dir: Path):
    return [f for f in round_dir.glob("results/**/*.json")
            if "SMOKE" not in f.name and not any(p.startswith("_") for p in f.parts)]


def carries(path: Path, marker: str) -> bool:
    try:
        return marker in path.read_text()
    except OSError:
        return False


def main() -> int:
    problems = []

    # ---- registry 1: the freeze -------------------------------------
    print("FREEZE REGISTRY (covalx/frozen.py) -- enumerated from the registry:")
    for name in sorted(FROZEN):
        d = _ROOT / "rounds" / name
        if not d.exists():
            print(f"  {name:28s} ROUND ABSENT ON DISK")
            problems.append(f"{name}: named in the freeze registry, no such round")
            continue
        files = results_of(d)
        if not files:
            print(f"  {name:28s} NO INSPECTABLE RESULTS")
            problems.append(f"{name}: frozen but has no results file to annotate")
            continue
        good = [f for f in files if carries(f, "FROZEN LINE")]
        ok = len(good) == len(files)
        print(f"  {name:28s} {len(good)}/{len(files)} files carry the freeze"
              f"{'' if ok else '   <- MISSING'}")
        if not ok:
            for f in files:
                if f not in good:
                    problems.append(f"{name}: {f.relative_to(_ROOT)} lacks the freeze")

    # ---- registry 2: the outcome-variable scope ----------------------
    # Enumerated from the CODE that declares OUTCOME_SCOPE, so a round that
    # declares one and never stamps it is caught.
    print("\nOUTCOME_SCOPE declarations -- enumerated from the code that declares them:")
    declarers = sorted(d for d in (_ROOT / "rounds").iterdir()
                       if (d / "run.py").exists()
                       and "OUTCOME_SCOPE" in (d / "run.py").read_text())
    if not declarers:
        print("  (none)")
    for d in declarers:
        files = results_of(d)
        if not files:
            print(f"  {d.name:28s} NO INSPECTABLE RESULTS")
            problems.append(f"{d.name}: declares OUTCOME_SCOPE, has no results file")
            continue
        good = [f for f in files
                if carries(f, "outcome_variable_scope") or carries(f, "OUTCOME_SCOPE")]
        ok = len(good) == len(files)
        print(f"  {d.name:28s} {len(good)}/{len(files)} files carry the scope"
              f"{'' if ok else '   <- MISSING'}")
        if not ok:
            for f in files:
                if f not in good:
                    problems.append(f"{d.name}: {f.relative_to(_ROOT)} lacks the outcome scope")

    print(f"\nregistry entries checked: freeze {len(FROZEN)}, "
          f"outcome-scope {len(declarers)}")
    if not problems:
        print("Every artifact entitled to an annotation carries it.")
        print("  Carried is not correct, and not prominent -- this flags omission only.")
        return 0
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print(f"  {p}")
    print("\nA registry entry with nothing to inspect is a LOUD failure here, because "
          "the\nthree bugs this check exists for all reported completeness over what they "
          "could see.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
