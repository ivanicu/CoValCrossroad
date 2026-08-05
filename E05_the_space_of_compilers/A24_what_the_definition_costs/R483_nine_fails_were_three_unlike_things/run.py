#!/usr/bin/env python3
"""R483 — the census returned 9 FAIL. They are three unlike things, and one wanted a one-line fix.

⚠ ACTION CLASS: CLOSURE + PRODUCTION. No fork separated. It triages a count R482 produced and adds
the bucket that makes the count readable.

WHY. R482 ran all 42 gates and returned 9 FAIL. Treated as nine defects, that is a large standing
debt. Read individually, three unlike things are pooled under one word, and a count that conflates a
live defect, a documented register and a broken control WILL be quoted as nine defects.

ESTIMAND  the partition of the FAIL bucket into
    LIVE-DEBT      a real, payable finding
    BY-DESIGN      a gate that cannot exit 0 by construction (a standing register)
    CONTROL-BROKE  a gate whose own control misbehaved -> it reports nothing about the repo

IDENTIFICATION  by each gate's own output. ⚠ PROXY, sound in ONE direction: a phrase identifies a
    non-live failure; its ABSENCE proves nothing, so the classifier may only DEMOTE out of LIVE-DEBT.

SCOPE  population: the 9 FAILs from R482's census · instrument: `run_all.classify_fail` on FULL output.

WORLDS
    A  ALL LIVE      nine payable defects -> stop and pay.
    B  MIXED         some are registers or broken controls -> the count is not a defect count.

KILL  B if any FAIL carries a by-design or control-failure phrase in its full output.

CONTROLS
    POSITIVE  the classifier is fed the two REAL messages that motivated it, plus a live one and the
              empty string; all four must classify correctly. A classifier validated on invented
              strings is validated against imagination.
    g=0       the empty string must classify LIVE-DEBT — silence is never an acquittal.

ARTIFACT  results/r483_fail_kinds.json
"""
import json, pathlib, sys
sys.path.insert(0, "assurance"); import run_all
OUT = pathlib.Path(__file__).parent/"results"
FAILS = ["artifacts_are_internally_coherent", "attack_every_check", "attack_no_withdrawn_framings",
         "attack_outcome_variable_declared", "every_round_reaches_the_readme",
         "next_gradient_labels_its_hypotheses", "outcome_variable_declared",
         "seed_filter_is_disclosed", "source_stamp_is_current"]
print("  POSITIVE CONTROL on the classifier (real messages + a live one + silence):")
ok = run_all._classifier_selftest()
rows = []
for g in FAILS:
    p = pathlib.Path("assurance")/f"{g}.py"
    if not p.exists(): continue
    name, rc, el, msg = run_all.run_one(p, timeout=90)
    kind = msg.split("]")[0].lstrip("[") if rc == 1 else ("PASS" if rc == 0 else f"rc{rc}")
    rows.append({"gate": g, "rc": rc, "kind": kind})
    print(f"    {g:<40} rc={rc}  {kind}")
import collections
c = collections.Counter(r["kind"] for r in rows)
print(f"\n  partition: {dict(c)}")
world = "A (ALL LIVE)" if set(c) <= {"LIVE-DEBT"} else "B (MIXED — the count is not a defect count)"
print(f"  VERDICT {'MEASURED' if ok else 'UNVERIFIED'}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"rows": rows, "partition": dict(c), "classifier_selftest": bool(ok), "world": world},
          open(OUT/"r483_fail_kinds.json", "w"), indent=2)
sys.exit(0 if ok else 2)
