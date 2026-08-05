#!/usr/bin/env python3
"""R571 · Is the run-to-run flip a TIMEOUT BOUNDARY rather than a race?

R570 established the suite's failure count is unstable (serial 9, serial 10, parallel 13) and left
the mechanism unverified, having refuted a concurrency race as sufficient. A concrete rival: gates
are killed at 90s, and a gate whose runtime is NEAR 90s flips depending on machine load. Serial is
less loaded than 12 workers, which predicts serial < parallel failures -- observed.

ESTIMAND  the per-gate runtime distribution, and how many gates sit in a band where load could
          carry them across the 90s limit.
IDENT     fully identified: time each gate serially, on an unloaded machine.
SCOPE     population = gates run_all discovers · instrument = wall clock via run_one · baseline =
          the 90s timeout · regime = serial, this box.
WORLDS    A no gate is near 90s -> the timeout cannot explain the flip; some other mechanism.
          B >=1 gate sits in a load-sensitive band -> the timeout is a sufficient explanation for
            at least part of the 9->13 spread.
KILL      pre-registered: if the only gates above 30s are the three that ALWAYS time out, and no
          gate sits between 30s and 90s, WORLD A.
POS CTRL  the three known-timeout gates must be observed at the cap, else the timer is not
          measuring what run_all measures.
NEG CTRL  a gate known to be fast (statement_provenance, ~0.1s) must read as fast.
ARTIFACT  results/timing_band.json
"""
import json, pathlib, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "assurance"))
import run_all

rows = []
for p in run_all.discover():
    name, rc, secs, _out = run_all.run_one(p)
    rows.append((name, rc, secs))
rows.sort(key=lambda r: -r[2])

cap = 90.0
timeouts = [r for r in rows if r[1] == -1]
fast = next((r for r in rows if r[0] == "statement_provenance"), None)
print(f"  POSITIVE CONTROL  known-timeout gates observed at the cap: {len(timeouts)} -> "
      f"{'PASS' if timeouts else 'FAIL — the timer is not measuring run_all''s quantity'}")
print(f"  NEGATIVE CONTROL  a known-fast gate reads fast: "
      f"{fast[2] < 1.0 if fast else None} -> {'PASS' if fast and fast[2] < 1.0 else 'FAIL'}")
if not timeouts or not (fast and fast[2] < 1.0):
    sys.exit(2)

print(f"\n  slowest gates, serial, unloaded:")
for n, rc, s in rows[:10]:
    flag = " ⏱ TIMEOUT" if rc == -1 else ""
    print(f"    {s:7.2f}s  rc={rc:>3}  {n}{flag}")

band = [r for r in rows if r[1] != -1 and 30.0 <= r[2] < cap]
near = [r for r in rows if r[1] != -1 and 10.0 <= r[2] < cap]
print(f"\n  gates that TIME OUT even unloaded : {len(timeouts)}")
print(f"  gates in [30s, 90s) — load-flippable: {len(band)}   {[n for n,_,_ in band]}")
print(f"  gates in [10s, 90s)                 : {len(near)}   {[n for n,_,_ in near]}")

world = "B" if band else "A"
print(f"\n  WORLD {world} -- " + (
    f"{len(band)} gate(s) sit where load can carry them past 90s; the timeout is a sufficient "
    f"partial explanation for the 9->13 spread."
    if world == "B" else
    "no gate sits between 30s and the cap, so the timeout cannot explain the flip. The mechanism "
    "is something else and stays UNVERIFIED."))
(pathlib.Path(__file__).parent / "results" / "timing_band.json").write_text(json.dumps(
    {"world": world, "cap_s": cap, "n_gates": len(rows),
     "always_timeout": [n for n, _, _ in timeouts],
     "band_30_to_90": [{"gate": n, "secs": round(s, 2)} for n, _, s in band],
     "band_10_to_90": [{"gate": n, "secs": round(s, 2)} for n, _, s in near],
     "slowest": [{"gate": n, "rc": rc, "secs": round(s, 2)} for n, rc, s in rows[:10]],
     "note": "timed SERIAL and unloaded; under 12 workers every gate is slower"}, indent=2))
