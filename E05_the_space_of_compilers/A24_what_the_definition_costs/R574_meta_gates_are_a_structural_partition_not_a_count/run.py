#!/usr/bin/env python3
"""R574 · Partition the suite structurally, because the failure COUNT is a draw.

My NEXT line said the suite's "sixteen non-passes" should be re-counted. R570 established that
count is unstable (9, 10, 13 across three runs), so re-counting produces another draw. What IS
stable is a structural property: does a gate RUN other gates? A meta-gate's cost is ~46x an
ordinary one's, which R573 showed is why one sits at the 90s cap.

ESTIMAND  the partition of the 46 discovered gates into META (runs other gates) and ORDINARY.
IDENT     fully identified: a static read of each source. No run, so no draw.
SCOPE     population = run_all.discover() · instrument = source patterns that RUN a sibling gate ·
          baseline = every gate ordinary · regime = HEAD.
WORLDS    A the meta set is exactly the 3 that hit the cap -> cost explains the ERRORs entirely.
          B it is larger or smaller -> the cap-hitters are not coextensive with the meta-gates,
            and cost is not the whole story.
KILL      pre-registered: if META != the 3 cap-hitters, WORLD B.
POS CTRL  what_did_each_check_actually_read must classify META -- R573 read its loop directly.
NEG CTRL  statement_provenance must classify ORDINARY -- it opens two documents and exits.
ARTIFACT  results/meta_partition.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "assurance"))
import run_all

# a gate is META if its SOURCE runs sibling gate files. Three shapes, all present in this repo.
PATS = [
    (r"assurance.*glob\(\s*['\"]\*\.py", "globs assurance/*.py"),
    (r"discover\(", "calls run_all.discover()"),
    (r"run_isolated\(", "runs a subject in isolation"),
    # ⛔ THE FIRST VERSION REQUIRED THE LITERAL `executable` IN THE ARG LIST. attack_the_suite
    # writes `subprocess.run([PY, f"assurance/{check}.py"])` -- a module-level alias -- so the
    # pattern returned a FALSE NEGATIVE and the partition came back 1 META against 3 cap-hitters.
    # Seventh instrument defect of this class this session. Match the OBJECT being run, not the
    # name of the interpreter variable.
    (r'subprocess\.\w+\(\s*\[[^]]*["\']assurance/', "subprocess-runs an assurance script"),
    (r'subprocess\.\w+\(\s*\[[^]]*f"assurance/', "subprocess-runs an assurance script (fstring)"),
    (r'subprocess\.\w+\(\s*\[[^]]*["\']run\.py["\']', "subprocess-runs a round's run.py"),
    (r"for\s+\w+\s+in\s+\w*(scripts|gates|checks)\w*", "iterates a script/gate list"),
]

rows = {}
for p in run_all.discover():
    src = p.read_text()
    hits = [why for pat, why in PATS if re.search(pat, src)]
    rows[p.stem] = hits

pos = bool(rows.get("what_did_each_check_actually_read"))
neg = not rows.get("statement_provenance")
print(f"  POSITIVE CONTROL  what_did_each_check_actually_read classifies META: {pos} -> "
      f"{'PASS' if pos else 'FAIL'}")
print(f"  NEGATIVE CONTROL  statement_provenance classifies ORDINARY: {neg} -> "
      f"{'PASS' if neg else 'FAIL'}")
if not pos or not neg:
    print(f"    wdc hits={rows.get('what_did_each_check_actually_read')}  "
          f"sp hits={rows.get('statement_provenance')}")
    sys.exit(2)

meta = sorted(n for n, h in rows.items() if h)
ordinary = sorted(n for n, h in rows.items() if not h)
CAP = {"attack_the_suite", "backfilled_findings_are_rederivable",
       "what_did_each_check_actually_read"}

print(f"\n  gates: {len(rows)}   META: {len(meta)}   ORDINARY: {len(ordinary)}")
for n in meta:
    mark = " ⏱ hits the 90s cap" if n in CAP else ""
    print(f"    META  {n:<44} {rows[n]}{mark}")
missing = sorted(CAP - set(meta))
print(f"\n  cap-hitters NOT classified META: {missing or 'none'}")

world = "A" if set(meta) == CAP else "B"
print(f"  WORLD {world} -- " + (
    "the meta set is exactly the three cap-hitters; cost explains the ERRORs entirely."
    if world == "A" else
    f"the meta set ({len(meta)}) is not the three cap-hitters, so cost is not the whole story "
    f"and the partition is the more useful object than either count."))
(pathlib.Path(__file__).parent / "results" / "meta_partition.json").write_text(json.dumps(
    {"world": world, "n_gates": len(rows), "meta": meta, "n_meta": len(meta),
     "n_ordinary": len(ordinary), "cap_hitters": sorted(CAP),
     "cap_hitters_not_meta": missing,
     "why": {n: rows[n] for n in meta},
     "note": "STRUCTURAL partition: a static source read, so unlike the failure count it is not "
             "a draw (R570: 9, 10, 13 across three runs)"}, indent=2))
