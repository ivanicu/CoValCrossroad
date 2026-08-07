#!/usr/bin/env python3
"""R576 · Count the subprocess spawns. Nine patterns have failed; an audit hook cannot.

R575's static matcher returned 0 for all seven meta-gates -- the ninth pattern failure of this
session. `sys.addaudithook` observes the actual `subprocess.Popen` event, so it cannot miss a call
because of how the interpreter variable was named.

ESTIMAND  the number of subprocess spawns each meta-gate makes, within a fixed wall-clock window.
IDENT     PARTIAL for the cappers: they are cut off at the window, so their count is a LOWER BOUND
          and a RATE, never a total. Fully identified for gates that finish inside the window.
SCOPE     population = the 7 meta-gates · instrument = sys.addaudithook on subprocess.Popen ·
          baseline = 0 spawns · regime = a 25s window per gate, serial.
WORLDS    A the cappers and non-cappers overlap in spawn count -> fleet size does NOT separate.
          B they separate cleanly -> fleet size is established as the discriminator.
KILL      pre-registered: if any non-capper's count exceeds any capper's lower bound, WORLD A.
POS CTRL  a gate KNOWN to spawn (attack_no_withdrawn_framings, 1 subprocess call site, 6.18s)
          must return >0. A hook that counts 0 everywhere is the R575 failure repeated.
NEG CTRL  statement_provenance makes no subprocess call and must return exactly 0.
ARTIFACT  results/spawns.json
"""
import json, pathlib, subprocess, sys, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[3]
WINDOW = 25

HARNESS = textwrap.dedent('''
    import sys, json, runpy, threading, os
    n = [0]
    def hook(event, args):
        # ⛔ THE FIRST VERSION ONLY DUMPED IN `finally`, which never runs when the OUTER
        # subprocess.run times out and kills this child -- so every capper returned nothing and
        # the round was UNVERIFIED for a reason that was mine. Emit on EVERY spawn: a truncated
        # run then still leaves a trail, and the last line seen is a valid LOWER BOUND.
        if event == "subprocess.Popen":
            n[0] += 1
            print(json.dumps({"spawns": n[0], "finished": False}), file=sys.stderr, flush=True)
    sys.addaudithook(hook)
    target = sys.argv[1]
    def dump():
        print(json.dumps({"spawns": n[0], "finished": fin[0]}), file=sys.stderr, flush=True)
    fin = [False]
    try:
        sys.argv = [target]
        runpy.run_path(target, run_name="__main__")
        fin[0] = True
    except SystemExit:
        fin[0] = True
    except BaseException:
        pass
    finally:
        dump()
''')
hp = pathlib.Path("/tmp/claude-1000/-home-ivan/spawn_harness.py")
hp.parent.mkdir(parents=True, exist_ok=True)
hp.write_text(HARNESS)

GATES = ["attack_scope_reaches_the_reader", "attack_every_check",
         "attack_outcome_variable_declared", "attack_no_withdrawn_framings",
         "attack_the_suite", "what_did_each_check_actually_read",
         "backfilled_findings_are_rederivable"]
CAPS = {"attack_the_suite", "what_did_each_check_actually_read",
        "backfilled_findings_are_rederivable"}

def measure(name):
    p = ROOT / "assurance" / f"{name}.py"
    try:
        r = subprocess.run([sys.executable, str(hp), str(p)], cwd=ROOT,
                           capture_output=True, text=True, timeout=WINDOW)
        for line in reversed((r.stderr or "").splitlines()):
            try:
                d = json.loads(line); return d["spawns"], d["finished"]
            except Exception:
                continue
        return None, False
    except subprocess.TimeoutExpired as e:
        # ⛔ THE FIRST VERSION RETURNED "TIMEOUT" HERE AND DISCARDED e.stderr. TimeoutExpired
        # CARRIES everything the child printed before it was killed -- the measurement had
        # succeeded and the error path threw it away. This is not a pattern failure like the
        # previous nine; it is collected data destroyed on the way out.
        buf = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
        for line in reversed(buf.splitlines()):
            try:
                d = json.loads(line); return d["spawns"], False
            except Exception:
                continue
        return "TIMEOUT", False

neg, _ = measure("statement_provenance")
print(f"  NEGATIVE CONTROL  statement_provenance spawns 0: {neg == 0} -> "
      f"{'PASS' if neg == 0 else f'FAIL (got {neg})'}")
pos, posfin = measure("attack_no_withdrawn_framings")
ok_pos = isinstance(pos, int) and pos > 0
print(f"  POSITIVE CONTROL  a known-spawning gate returns >0: {pos} -> "
      f"{'PASS' if ok_pos else 'FAIL — the hook is blind, which is R575 repeated'}")
if neg != 0 or not ok_pos:
    sys.exit(2)

print(f"\n  {'gate':<44} {'caps':>5} {'spawns':>10} {'finished':>9}")
rows = []
for g in GATES:
    s, fin = measure(g)
    rows.append({"gate": g, "caps": g in CAPS, "spawns": s, "finished_in_window": bool(fin)})
    print(f"  {g:<44} {str(g in CAPS):>5} {str(s):>10} {str(bool(fin)):>9}")

nums = {r["gate"]: r["spawns"] for r in rows if isinstance(r["spawns"], int)}
capn = [v for k, v in nums.items() if k in CAPS]
nonn = [v for k, v in nums.items() if k not in CAPS]
print(f"\n  cappers (lower bounds, cut at {WINDOW}s): {capn}")
print(f"  non-cappers:                              {nonn}")
overlap = bool(capn and nonn and max(nonn) >= min(capn))
world = "A" if overlap else ("B" if capn and nonn else "UNVERIFIED")
print(f"\n  WORLD {world} -- " + (
    "a non-capper spawns at least as many as a capper; fleet size does NOT separate."
    if world == "A" else
    "the groups separate on spawn count within the window; fleet size is the discriminator."
    if world == "B" else
    "one group produced no integer counts, so no comparison is licensed."))
print(f"  ⚠ capper counts are LOWER BOUNDS: cut at {WINDOW}s, not run to completion.")
(pathlib.Path(__file__).parent / "results" / "spawns.json").write_text(json.dumps(
    {"world": world, "window_s": WINDOW, "rows": rows, "capper_lower_bounds": capn,
     "non_capper_counts": nonn, "overlap": overlap,
     "identification": "PARTIAL — capper counts are lower bounds truncated by the window"},
    indent=2))
