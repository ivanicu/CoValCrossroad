#!/usr/bin/env python3
"""R488 — three rounds bounded a class by hand. The practice, not the class, is the defect.

⚠ ACTION CLASS: PRODUCTION. It builds an instrument; it separates no worlds.

WHY. R477 bounded the rival class by the nine arms carrying a `.npz` (R478: the class is 1,820).
R485 bounded the admissible class by a list of 14. R486 asserted three arms "are the whole
population" (R487: 30 admissible-and-prompt-aware, 23 scorable). Each fix went to the class that had
just failed, never to the practice. `comparator_scope.py` enforces this shape for comparators and
`register_requirements.py` for requirements; nothing enforced it for arms.

ESTIMAND  of rounds that load arm artifacts, how many DERIVE their population from a rule, how many
    DECLARE a typed one with a reason, and how many simply type it.

IDENTIFICATION  by `ast`, grounded in the object: an arm list is a literal sequence containing >= 3
    strings that ARE arm names on disk. ⚠ PROXY, one direction: TYPED is reliable; DERIVED means
    "not obviously hand-enumerated", never "the rule is right".

SCOPE  population: every `E*/A*/R*/run.py` · instrument: `assurance/arm_population_is_derived.py`.

WORLDS  A LOCAL (a handful) · B SYSTEMIC (a substantial share of arm-comparing rounds).

KILL  the gate's own POSITIVE CONTROL, built from the four real rounds: R477/R485/R486 must classify
    TYPED and R487 DERIVED. A detector that cannot re-find the cases it was built from is unfit.

ARTIFACT  results/r488_arm_populations.json  ·  the instrument and its frozen ledger are the product.
"""
import json, pathlib, subprocess, sys
OUT = pathlib.Path(__file__).parent/"results"
r = subprocess.run([sys.executable, "assurance/arm_population_is_derived.py"],
                   capture_output=True, text=True)
print(r.stdout.rstrip()[:2400])
frozen = json.loads(pathlib.Path("assurance/KNOWN_TYPED_ARM_POPULATION.json").read_text())
world = "B (SYSTEMIC)" if frozen["count"] > 5 else "A (LOCAL)"
print(f"\n  frozen typed-population rounds: {frozen['count']}")
print(f"  VERDICT {'MEASURED' if r.returncode == 0 else 'DEBT CHANGED'}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"gate_exit": r.returncode, "frozen_count": frozen["count"], "world": world},
          open(OUT/"r488_arm_populations.json", "w"), indent=2)
sys.exit(r.returncode)
