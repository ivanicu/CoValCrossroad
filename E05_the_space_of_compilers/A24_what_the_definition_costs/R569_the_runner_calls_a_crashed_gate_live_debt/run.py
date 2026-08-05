#!/usr/bin/env python3
"""R569 · Gates behave differently under run_all than standalone. How many, and which way?

I set out to show run_all mislabels crashed gates as LIVE-DEBT. The positive control failed:
`source_stamp_is_current` shows a Traceback in run_all's listing and does NOT crash standalone.
That is the third instance of a divergence R562 recorded and left undiagnosed. So the estimand
changes to the divergence itself -- named before the method, not after.

ESTIMAND  the number of gates whose exit code differs between run_all (12 workers, parallel) and
          a standalone serial run, and the DIRECTION of each difference.
IDENT     fully identified: two exit codes per gate.
SCOPE     population = gates run_all discovers, minus meta and known-timeout · instrument = rc ·
          baseline = identical rc · regime = HEAD, same working tree, back to back.
WORLDS    A no divergence -> R562's observation and my failed control were both flukes.
          B divergence -> the suite's verdict depends on HOW it is invoked, and every count of
            failures quoted this session inherits that.
KILL      pre-registered: >=1 gate whose rc differs between the two -> WORLD B.
POS CTRL  a gate that passes in BOTH must be observed, else "differs" is not distinguishable from
          "everything is noise".
NEG CTRL  running the same gate standalone TWICE must give the same rc, else the standalone arm is
          itself unstable and no comparison is licensed.
ARTIFACT  results/invocation_divergence.json
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "assurance"))
import run_all
SKIP = {"attack_the_suite", "backfilled_findings_are_rederivable",
        "what_did_each_check_actually_read", "audit_the_auditors"}

def solo(n, timeout=110):
    try:
        r = subprocess.run([sys.executable, str(ROOT / "assurance" / f"{n}.py")],
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode
    except subprocess.TimeoutExpired:
        return -1

# NEGATIVE CONTROL: is the standalone arm itself stable?
probe = "statement_provenance"
a, b = solo(probe), solo(probe)
print(f"  NEGATIVE CONTROL  the same gate twice standalone gives the same rc: {a}=={b} -> "
      f"{'PASS' if a == b else 'FAIL — standalone arm unstable, no comparison licensed'}")
if a != b:
    sys.exit(2)

# run_all's own verdicts
rr = subprocess.run([sys.executable, str(ROOT / "assurance" / "run_all.py")],
                    capture_output=True, text=True, timeout=500)
suite = {}
for line in (rr.stdout + rr.stderr).splitlines():
    m = re.match(r"\s*(PASS|FAIL|ERROR|UNRUNNABLE)\s+(\S+)\s+rc=(-?\d+)", line)
    if m: suite[m.group(2)] = int(m.group(3))
print(f"  run_all reported rc for {len(suite)} gates")
if len(suite) < 10:
    print("  could not parse run_all's rows -> UNRUNNABLE"); sys.exit(2)

both_pass, diff = [], []
for n, rc_suite in sorted(suite.items()):
    if n in SKIP: continue
    rc_solo = solo(n)
    if rc_solo == rc_suite == 0: both_pass.append(n)
    if rc_solo != rc_suite: diff.append((n, rc_suite, rc_solo))

print(f"  POSITIVE CONTROL  gates passing in BOTH arms: {len(both_pass)} -> "
      f"{'PASS' if both_pass else 'FAIL — cannot distinguish divergence from noise'}")
if not both_pass:
    sys.exit(2)

print(f"\n  gates compared: {len([n for n in suite if n not in SKIP])}")
print(f"  DIVERGENT: {len(diff)}")
for n, rs, ro in diff:
    d = "suite FAILS, solo PASSES" if rs and not ro else \
        "suite PASSES, solo FAILS" if ro and not rs else f"rc {rs} vs {ro}"
    print(f"    {n:<46} suite={rs:>3}  solo={ro:>3}   {d}")

world = "B" if diff else "A"
print(f"\n  WORLD {world} -- " + (
    f"{len(diff)} gate(s) give a different verdict depending on HOW they are invoked; every "
    f"failure count quoted this session inherits that."
    if world == "B" else "no divergence; R562's observation and my failed control were flukes."))
(pathlib.Path(__file__).parent / "results" / "invocation_divergence.json").write_text(json.dumps(
    {"world": world, "n_compared": len([n for n in suite if n not in SKIP]),
     "n_both_pass": len(both_pass), "n_divergent": len(diff),
     "divergent": [{"gate": n, "rc_suite": rs, "rc_solo": ro} for n, rs, ro in diff],
     "note": "estimand changed BEFORE the method when the first positive control failed"},
    indent=2))
