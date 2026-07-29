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

# A provisional run is not a result. Matching one WORD failed twice: once on
# case (a04_smoke.json, entry 71) and once on vocabulary (a06_dryrun.json,
# entry 75). Match the class, and prefer the results/_smoke/ directory rule,
# which does not depend on the name at all.
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip",
                         re.I)


def results_of(round_dir: Path):
    return [f for f in round_dir.glob("results/**/*.json")
            if not PROVISIONAL.search(f.name) and not any(p.startswith("_") for p in f.parts)]


def carries(path: Path, marker: str) -> bool:
    try:
        return marker in path.read_text()
    except OSError:
        return False


def _floor(n: int, what: str) -> int:
    """Refuse to report success on an empty observation (entry 63/64).

    "Nothing outstanding" and "nothing observed" are different states, and every
    check in this package returned 0 for both. A check whose population is empty
    has measured nothing; that is exit 2, distinct from pass (0) and fail (1).
    """
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0

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

    # ---- registry 3: is the registry COMPLETE against its own source? ----
    # A registry can be internally satisfied and still miss a whole frozen line.
    # FROZEN.md's numbered sections 1-3 are INTERPRETATION freezes and name the
    # rounds they cover in their headers. Sections 4 and 5 freeze activities
    # ("more best-of-n") and a headline, which are not round annotations, so they
    # are deliberately not required here -- and that exemption is stated rather
    # than silently applied.
    print("\nFREEZE REGISTRY vs FROZEN.md sections 1-3 (interpretation freezes):")
    fro = (_ROOT / "FROZEN.md")
    if not fro.exists():
        print("  ! FROZEN.md absent -- completeness UNCHECKED, not clean")
        problems.append("FROZEN.md absent: registry completeness unverified")
    else:
        txt = fro.read_text()
        named = set()
        for m in re.finditer(r"^## ([123])\.[^\n]*$", txt, re.M):
            named |= set(re.findall(r"`(r\d+)`", m.group(0)))
        have = {re.match(r"r\d+", k).group(0) for k in FROZEN}
        missing = sorted(named - have)
        print(f"  rounds named in sections 1-3: {len(named)}   in the registry: "
              f"{len(named & have)}")
        if missing:
            print(f"  NOT IN THE REGISTRY: {missing}")
            for m_ in missing:
                problems.append(f"{m_}: named in a FROZEN.md interpretation freeze, "
                                f"absent from covalx/frozen.py")
        else:
            print("  every round named in an interpretation freeze is in the registry")

    # ---- registry 4: does FROZEN.md cover the QUEUE's frozen list? --------
    # Last turn I said this was "a human comparison". It is not -- the queue is
    # stable and reproduced verbatim in every task prompt, so it can be encoded
    # and diffed. Doing so found "anthropomorphism regex" frozen by the queue and
    # recorded nowhere in FROZEN.md: 11 of 12 items present, one absent.
    #
    # This is where the chain of authorisation stops being mechanical. The list
    # below is transcribed BY HAND from the queue, so it verifies FROZEN.md
    # against a transcription, not against the queue itself.
    QUEUE_FROZEN = ["r25", "r16", "r17", "r18", "r28", "r24", "anthropomorphism",
                    "best-of-n", "gold backbone", "donor floor", "paraphrase sweep",
                    "more judges"]
    print("\nFROZEN.md vs the QUEUE's frozen list (hand-transcribed):")
    if fro.exists():
        low = txt.lower()
        absent = [q for q in QUEUE_FROZEN if q.lower() not in low]
        print(f"  queue items: {len(QUEUE_FROZEN)}   recorded in FROZEN.md: "
              f"{len(QUEUE_FROZEN) - len(absent)}")
        if absent:
            print(f"  ABSENT: {absent}")
            for q in absent:
                problems.append(f"'{q}': frozen by the queue, absent from FROZEN.md")
        else:
            print("  every queue-frozen item is recorded")

    print(f"\nregistry entries checked: freeze {len(FROZEN)}, "
          f"outcome-scope {len(declarers)}")
    floor = _floor(len(FROZEN) + len(declarers), "the registries being checked")
    if floor:
        return floor
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
