"""Does any file in results/ contain values that cannot be a measurement?

Why this exists
---------------
r79 wrote three artifacts into `results/` whose every value was NaN: internlm loads
under the cache shim and returns `hidden_states[1]` already NaN (entry 134). Two of
them were an embedding cache that r79's own reuse path would have loaded on the next
run, making the round refuse internlm for the *cache's* fault rather than the model's.

Nothing in this suite read results CONTENT. `results_match_their_code.py` compares
commit timestamps and cannot see an untracked file at all -- and an orphan of a
superseded run is exactly what "untracked in results/" looks like.

Measured before being built, twice
----------------------------------
A first version also flagged constant arrays. It produced **971 findings on 275
files**, almost all of them `_pairs_per_prompt.json` where every prompt legitimately
has the same pair count -- the low-precision flood declined at entry 108.

Narrowed to NON-FINITE content only, and applying the repository's own convention
that a path part starting with `_` is not a result: **2 findings on 285 files, both
real**, and the known case is caught. That is why this one was built and the other
two candidates were not.

  PROPERTY     no file presented as a result contains values that cannot be a measurement
  PROXY        non-finite content in .npy / .npz / numeric JSON lists
  IMPLICATION  non-finite => certainly not a measurement.  finite => nothing implied;
               a plausible wrong number is invisible here and always will be.
  SAFE SIDE    reports only the direction it is sound in, and never claims a file is
               correct because it is finite.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)


def nonfinite(a) -> str | None:
    a = np.asarray(a, dtype=float).ravel()
    if a.size < 3:
        return None
    bad = int((~np.isfinite(a)).sum())
    if bad == a.size:
        return f"ALL {a.size} values non-finite"
    if bad:
        return f"{bad} of {a.size} values non-finite"
    return None


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"OBSERVED NOTHING: {what} is empty. That is not a clean bill -- it is a")
        print("check that had nothing to look at, which is the state entry 64 found five")
        print("checks silently reporting as success.")
        raise SystemExit(2)
    return n


def scan(root: Path):
    hits, scanned = [], 0
    for f in sorted(root.glob("rounds/*/results/**/*")):
        if not f.is_file() or PROVISIONAL.search(str(f)):
            continue
        if any(p.startswith("_") for p in f.parts):
            continue
        scanned += 1
        try:
            if f.suffix == ".npy":
                d = nonfinite(np.load(f, allow_pickle=False))
                if d:
                    hits.append((f, "<array>", d))
            elif f.suffix == ".npz":
                z = np.load(f, allow_pickle=True)
                for k in z.files:
                    if z[k].dtype.kind in "fiu":
                        d = nonfinite(z[k])
                        if d:
                            hits.append((f, k, d))
            elif f.suffix == ".json":
                doc = json.loads(f.read_text())

                def walk(o, p=""):
                    if isinstance(o, dict):
                        for k, v in o.items():
                            walk(v, f"{p}.{k}")
                    elif isinstance(o, list) and len(o) >= 3 and all(
                            isinstance(x, (int, float)) and not isinstance(x, bool) for x in o):
                        d = nonfinite(o)
                        if d:
                            hits.append((f, p, d))
                    elif isinstance(o, list):
                        for i, v in enumerate(o[:400]):
                            walk(v, f"{p}[{i}]")

                walk(doc)
        except (OSError, ValueError, json.JSONDecodeError) as e:
            hits.append((f, "-", f"UNREADABLE {type(e).__name__}: {e}"))
    return hits, scanned


def main() -> int:
    hits, scanned = scan(_ROOT)
    _floor(scanned, "the set of files under rounds/*/results/")
    print(f"files read: {scanned}   findings: {len(hits)}\n")
    for f, key, why in hits:
        print(f"  {why}")
        print(f"      {f.relative_to(_ROOT)}  [{key}]")
    if not hits:
        print("  (none)")
    print("\n  Sound in ONE direction only: non-finite content cannot be a measurement, but")
    print("  finite content is not thereby correct. A plausible wrong number is invisible")
    print("  here and always will be -- this catches the instrument that never switched on,")
    print("  not the one that switched on and lied.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
