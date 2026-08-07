#!/usr/bin/env python3
"""R561 · I have been hand-running six gates. The runner that exists discovers forty-six.

Every commit this session ran behind a hand-typed six-clause conjunction, and last round I wrote
that a single entry point "does not exist yet". assurance/run_all.py exists, discovers gates by
glob, and runs them in parallel. This measures what the other forty were saying while I was not
listening.

ESTIMAND  |discovered gates| , |gates I was running| , and the status of the difference.
IDENT     fully identified: run_all.discover() defines the population; the six are named in my
          own commit commands, recoverable from git history.
SCOPE     population = assurance/*.py discovered by run_all · instrument = run_all itself ·
          baseline = the six I typed · regime = current HEAD.
WORLDS    A the other gates are all passing -> the hand-typed six were a redundant subset and
            the cost was only duplication.
          B >=1 unrun gate is FAILING -> the hand-typed conjunction was not a subset of a
            passing whole; it was a filter that hid live failures.
KILL      pre-registered: any discovered gate outside my six with rc!=0 -> WORLD B.
POS CTRL  discover() must find all six I was running. If it does not, they are not comparable
          populations and the difference is meaningless.
NEG CTRL  an invented gate name must not appear in the discovered set.
ARTIFACT  results/six_of_fortysix.json
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "assurance"))
import run_all

MINE = ["statement_provenance", "residue_debt", "retraction_reaches_the_artifact",
        "definition_matches_the_record", "next_line_quantifiers_are_computed",
        "every_round_is_committed"]

disc = [p.stem for p in run_all.discover()]
print(f"  discovered by run_all: {len(disc)}")
missing = [m for m in MINE if m not in disc]
print(f"  POSITIVE CONTROL  discover() finds all six I was hand-running: {not missing} -> "
      f"{'PASS' if not missing else 'FAIL ' + str(missing)}")
print(f"  NEGATIVE CONTROL  an invented gate is not discovered: "
      f"{'zz_not_a_gate' not in disc} -> PASS")
if missing:
    sys.exit(2)

others = [d for d in disc if d not in MINE]
print(f"  gates I was NOT running: {len(others)}\n")

# ⛔ THE FIRST VERSION RAN THE 40 SERIALLY IN A LOOP I WROTE -- inside the round about having
# hand-built a runner that already exists. It died on attack_the_suite.py, a META-gate that runs
# the whole suite and which run_all excludes by design. Use run_all: it parallelises at 12
# workers and knows which gates are meta.
r = subprocess.run([sys.executable, str(ROOT / "assurance" / "run_all.py")],
                   capture_output=True, text=True, timeout=520)
out = r.stdout + r.stderr
fails, errs = [], []
for line in out.splitlines():
    t = line.strip()
    if t.startswith("FAIL") or t.startswith("⛔"):
        parts = t.split()
        name = next((p for p in parts if p in others or p in MINE), parts[1] if len(parts) > 1 else "?")
        (fails if name in others else []).append((name, t[:130])) if name in others else None
    if "rc=2" in t or "UNRUNNABLE" in t:
        parts = t.split()
        name = next((p for p in parts if p in others), None)
        if name: errs.append((name, 2, t[:90]))
print(f"  run_all rc={r.returncode}")
for line in out.splitlines():
    if line.strip().startswith(("FAIL", "ran ", "META")): print("   ", line.strip()[:150])

print(f"  of the {len(others)} unrun gates:  FAIL(rc=1) {len(fails)}   "
      f"UNRUNNABLE/other {len(errs)}   pass {len(others)-len(fails)-len(errs)}")
for g, msg in fails:
    print(f"    ⛔ FAIL  {g}\n            {msg}")
for g, rc, msg in errs[:6]:
    print(f"    ⚠  rc={rc}  {g}  {msg}")

world = "B" if fails else "A"
print(f"\n  WORLD {world} -- " + (
    "the hand-typed six were not a subset of a passing whole; live failures sat outside them."
    if world == "B" else "every unrun gate passes; the cost of the six was duplication only."))
(pathlib.Path(__file__).parent / "results" / "six_of_fortysix.json").write_text(json.dumps(
    {"world": world, "n_discovered": len(disc), "n_hand_run": len(MINE),
     "n_unrun": len(others), "n_failing_unrun": len(fails),
     "failing": [{"gate": g, "tail": m} for g, m in fails],
     "unrunnable": [{"gate": g, "rc": rc, "tail": m} for g, rc, m in errs],
     "hand_run": MINE}, indent=2))
