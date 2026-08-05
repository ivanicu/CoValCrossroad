#!/usr/bin/env python3
"""R566 · There is a third deliverable document and this session never opened it.

A23's README says every finding lives in `E05/FORMULATION.md` and `RETRACTIONS.md`. FORMULATION.md
is 156 KB and no round this session has read it. P16 requires ONE HOME PER FACT: a number stated
twice drifts, and the copy is never the one that gets fixed.

ESTIMAND  how many decimal values appear in BOTH FORMULATION.md and STATEMENT.md, and whether any
          named quantity is stated differently in the two.
IDENT     fully identified: both are text. ⚠ A shared decimal is NOT proof of a shared claim --
          two documents can use 0.5640 for different things. So the overlap is an UPPER BOUND on
          duplication, and that is how it is reported.
SCOPE     population = decimals with >=3 places in each document · instrument = a regex both
          documents' own gate already uses · baseline = zero overlap (disjoint homes) · regime = HEAD.
WORLDS    A the documents are disjoint -> two homes for two different fact sets, P16 satisfied.
          B they overlap heavily -> two homes for one fact set, which is what P16 forbids.
KILL      pre-registered: >20 shared decimals -> WORLD B.
POS CTRL  a value KNOWN to be on the statement (0.5640, coval_core's A2) must be found there.
          Else the extractor is blind and any overlap count is meaningless.
NEG CTRL  an invented decimal must appear in neither.
ARTIFACT  results/third_document.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
docs = {n: (E05 / f"{n}.md") for n in ("STATEMENT", "DEFINITION", "FORMULATION")}
for n, p in docs.items():
    print(f"  {n+'.md':<18} {'ABSENT' if not p.exists() else f'{p.stat().st_size/1024:7.1f} KB'}")
if not all(p.exists() for p in docs.values()):
    print("  a document is absent -> UNRUNNABLE"); sys.exit(2)

# the same pattern statement_provenance.py uses on this page
PAT = r"(?<![\w.])(\d+\.\d{3,4})(?![\w])"
vals = {n: set(re.findall(PAT, p.read_text())) for n, p in docs.items()}

pc = "0.5640" in vals["STATEMENT"]
print(f"\n  POSITIVE CONTROL  a known statement value (0.5640) is extracted: {pc} -> "
      f"{'PASS' if pc else 'FAIL — extractor is blind'}")
nc = any("0.7777" in v for v in vals.values())
print(f"  NEGATIVE CONTROL  an invented decimal appears nowhere: {not nc} -> "
      f"{'PASS' if not nc else 'FAIL'}")
if not pc or nc:
    sys.exit(2)

for n in vals:
    print(f"  {n:<12} distinct decimals: {len(vals[n])}")
sf = vals["STATEMENT"] & vals["FORMULATION"]
sd = vals["STATEMENT"] & vals["DEFINITION"]
fd = vals["FORMULATION"] & vals["DEFINITION"]
print(f"\n  STATEMENT ∩ FORMULATION : {len(sf)}")
print(f"  STATEMENT ∩ DEFINITION  : {len(sd)}   (expected -- the provenance gate REQUIRES this)")
print(f"  FORMULATION ∩ DEFINITION: {len(fd)}")
print(f"  shared by all three     : {len(vals['STATEMENT'] & vals['FORMULATION'] & vals['DEFINITION'])}")

world = "B" if len(sf) > 20 else "A"
print(f"\n  WORLD {world} -- " + (
    f"{len(sf)} decimals appear on BOTH the statement and the formulation: two homes for one fact "
    f"set, which P16 forbids."
    if world == "B" else
    f"only {len(sf)} decimals are shared; the documents are largely disjoint."))
print(f"  ⚠ UPPER BOUND, not duplication: a shared decimal is not proof of a shared claim.")
(pathlib.Path(__file__).parent / "results" / "third_document.json").write_text(json.dumps(
    {"world": world, "sizes_kb": {n: round(p.stat().st_size/1024, 1) for n, p in docs.items()},
     "n_decimals": {n: len(v) for n, v in vals.items()},
     "overlap_statement_formulation": len(sf), "overlap_statement_definition": len(sd),
     "overlap_formulation_definition": len(fd),
     "shared_examples": sorted(sf)[:15],
     "caveat": "a shared decimal is an UPPER BOUND on duplication, not evidence of a shared claim"},
    indent=2))
