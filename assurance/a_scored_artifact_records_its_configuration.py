"""A scored artifact must record the configuration that produced it.

⛔ WHY THIS EXISTS, IN FOUR ROUNDS OF ARCHAEOLOGY. R414 could not tell whether two 0.8B naming
   families were the same scoring run, and had to restrict its scope on a guess. R415 called five
   pairs "same arm, same code, different run" and published a noise floor from them. R416 hashed the
   committed criterion files and found they differed on 91-99.6% of prompts, so "same code" was
   wrong. R417 then showed the judge has NO stochastic step at all, which leaves CONFIGURATION --
   batch size, dtype, model path -- as the only non-stochastic mover, and the artifacts recorded
   none of it.

   Four rounds spent inferring what four fields would have stated. This gate makes the producer
   state them.

⛔ AND IT IS A SPECIFICATION FOR THE FUTURE, NOT A MEASUREMENT OF THE PAST -- the distinction R373
   paid for. 93 `sat_*.npz` files already exist and none carries provenance. A gate that demanded it
   of them would fail forever and be switched off, which is how a gate becomes decoration. So:

     GATE 1  the PRODUCER must write provenance.        <- fails the build
     GATE 2  the legacy debt is COUNTED and printed.    <- reported, never failed

   Legacy artifacts are exempt BY AGE, NOT BY MERIT, and the count is printed every run so the
   exemption stays visible rather than becoming invisible.

⚠ AND A SYNTAX CHECK IS NOT AN EXECUTION CHECK. While adding this, `ast.parse` passed on a producer
  whose `hashlib` was never imported -- the parse succeeds because names are not resolved. GATE 1
  therefore EXECUTES the producer module and requires the names it uses to be BOUND, rather than
  merely reading its source for a string.

CONTROLS
  PLANT (+)   a synthetic producer with the provenance write REMOVED must FAIL gate 1. Without it,
              a pass proves only that the checker found nothing.
  PLANT (-)   a synthetic producer that writes provenance must PASS, so the check distinguishes.
  EXECUTION   the real producer is imported and its module namespace inspected, so an unimported
              name cannot pass as a source-level string match.
  EMPTY       if no producer is found, exit 2 -- never a silent pass.

EXIT
    0  the producer records its configuration
    1  it does not -- the build fails
    2  the producer is missing -- never a silent pass
"""
from __future__ import annotations
import importlib.util
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "corebench" / "judge_core.py"
RESULTS = ROOT / "corebench" / "results"
REQUIRED = ("model", "batch", "core", "producer_sha256")


def writes_provenance(text: str) -> bool:
    """Source-level: does it pass a `provenance=` key to savez?

    ⚠ MY FIRST PATTERN WAS `savez_compressed\([^)]*provenance=` AND THE NEGATIVE CONTROL CAUGHT IT.
    `[^)]*` cannot cross the `)` in `np.array(meta)`, so it rejected a producer that DOES write
    provenance -- and would have rejected the real one, whose argument is
    `np.array(json.dumps(prov, sort_keys=True))`. A bounded window tolerant of nesting replaces it.
    The control fired in the direction that would have blocked a correct build, which is the harder
    direction to notice."""
    return bool(re.search(r"savez_compressed\(.{0,400}?provenance\s*=", text, re.S))


def names_bound(path: pathlib.Path):
    """EXECUTION-level: import it and report which names its body actually binds.
    A syntax check passes on a module whose imports are missing; this does not."""
    spec = importlib.util.spec_from_file_location("_probe", path)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(m)
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"
    return m, None


def main() -> int:
    if not PRODUCER.exists():
        print(f"  UNRUNNABLE: {PRODUCER} absent. Exit 2, never 0."); return 2
    src = PRODUCER.read_text()

    # ---- CONTROLS -------------------------------------------------------------------------------
    plant_bad = "np.savez_compressed(out, meta=np.array(meta), sat=sat)\n"
    plant_good = "np.savez_compressed(out, meta=np.array(meta), sat=sat, provenance=np.array(p))\n"
    pos_ok = not writes_provenance(plant_bad)
    neg_ok = writes_provenance(plant_good)
    print("  CONTROLS on the provenance check")
    print(f"    PLANT (+)  a producer WITHOUT the provenance write is caught: {pos_ok}   "
          f"{'PASS' if pos_ok else 'FAIL — a pass below would prove only that nothing was found'}")
    print(f"    PLANT (-)  a producer WITH it is accepted: {neg_ok}   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the checker is blind in one direction. Exit 1."); return 1

    # ---- GATE 1 · the producer ---------------------------------------------------------------------
    src_ok = writes_provenance(src)
    mod, err = names_bound(PRODUCER)
    exec_ok = mod is not None
    used = re.findall(r"\b(hashlib|json|np|pathlib)\.", src)
    missing = sorted({n for n in set(used) if mod is not None and not hasattr(mod, n)})
    print(f"\n  GATE 1 — the PRODUCER must record its configuration")
    print(f"    writes a `provenance=` key to savez : {src_ok}")
    print(f"    module EXECUTES (not merely parses) : {exec_ok}   {err or ''}")
    print(f"    names used but not bound            : {missing or 'none'}")
    print(f"    ⚠ a syntax check is not an execution check — while adding this, `ast.parse` passed")
    print(f"      on a producer whose `hashlib` was never imported, because parsing does not")
    print(f"      resolve names")
    for f in REQUIRED:
        print(f"    records `{f}`: {bool(re.search(chr(34) + f + chr(34) + r'\s*:', src))}")
    gate1 = src_ok and exec_ok and not missing and all(
        re.search(chr(34) + f + chr(34) + r"\s*:", src) for f in REQUIRED)

    # ---- GATE 2 · the legacy debt, counted not failed -----------------------------------------------
    have = lack = 0
    for p in sorted(RESULTS.glob("sat*.npz")):
        try:
            with np.load(p, allow_pickle=True) as d:
                (have := have + 1) if "provenance" in d.files else (lack := lack + 1)
        except Exception:
            lack += 1
    print(f"\n  GATE 2 — the legacy debt, REPORTED and never failed")
    print(f"    scored artifacts carrying provenance : {have}")
    print(f"    legacy artifacts without it          : {lack}")
    print(f"    exempt BY AGE, NOT BY MERIT — printed every run so the exemption stays visible")

    print()
    if gate1:
        print(f"  PASS: the producer records model, batch, core and its own source hash, so the next")
        print(f"  artifact can answer `same configuration?` without archaeology. The {lack} legacy")
        print(f"  files cannot, and that is a debt this gate reports rather than pretends away.")
        return 0
    print(f"  FAIL: the producer does not record its configuration. Four rounds were spent inferring")
    print(f"  what these fields state; do not let it regress.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
