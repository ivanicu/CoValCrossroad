"""Stamp each round's OUTCOME_SCOPE into its published results files.

The declaration lives in the round's own `run.py` as a module constant, so
there is exactly one source for it.  This utility copies it into the artifacts.

Why a utility rather than just re-running the rounds: r09, r11 and r12 all
GENERATE responses stochastically with no seed, so re-running them produces a
different response set and would silently invalidate everything built on the
saved one -- r39's feature cache, r40, r41's satisfaction tensor, r46's
comparison.  And best-of-n (r09/r11) is frozen.  So the artifacts have to be
annotated in place.

This is not hand-writing a conclusion.  The string describes the METHOD -- which
outcome variable the round scored against -- and it is read from the code that
implements that method, not composed here.  Re-running a round and re-stamping
gives the same result; the operation is idempotent.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

# A provisional run is not a result. Matching one WORD failed twice: once on
# case (a04_smoke.json, entry 71) and once on vocabulary (a06_dryrun.json,
# entry 75). Match the class, and prefer the results/_smoke/ directory rule,
# which does not depend on the name at all.
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip",
                         re.I)

_ROOT = Path(__file__).resolve().parents[1]
FIELD = "outcome_variable_scope"


def load_constant(run_py: Path, name: str):
    spec = importlib.util.spec_from_file_location(f"_r_{run_py.parent.name}", run_py)
    mod = importlib.util.module_from_spec(spec)
    src = run_py.read_text()
    # Execute only the module-level constant, not the whole file: these modules
    # import torch and transformers at top level and would cost a GPU load.
    ns: dict = {}
    start = src.index(f"{name} = (")
    depth, i = 0, start + len(f"{name} = ")
    while i < len(src):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                break
        i += 1
    exec(src[start:i + 1], ns)  # noqa: S102 -- a string literal from our own repo
    return ns[name]


def main() -> int:
    changed = total = 0
    for d in sorted(_ROOT.glob("[0-9][0-9]_*/r*/")):
        run = d / "run.py"
        if not run.exists() or "OUTCOME_SCOPE" not in run.read_text():
            continue
        scope = load_constant(run, "OUTCOME_SCOPE")
        files = [f for f in d.glob("results/**/*.json")
                 if not PROVISIONAL.search(f.name) and "_smoke_archive" not in f.parts]
        if not files:
            print(f"  ! {d.name}: OUTCOME_SCOPE declared but no results file to stamp")
            continue
        for f in files:
            try:
                doc = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            if not isinstance(doc, dict):
                continue
            total += 1
            if doc.get(FIELD) == scope:
                continue
            doc[FIELD] = scope
            f.write_text(json.dumps(doc, indent=1))
            changed += 1
            print(f"  stamped {f.relative_to(_ROOT)}")
    print(f"\n{changed} file(s) updated, {total} checked (idempotent: a second run "
          f"changes nothing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
