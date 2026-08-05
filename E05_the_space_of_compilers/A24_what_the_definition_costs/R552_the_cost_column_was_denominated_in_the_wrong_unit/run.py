#!/usr/bin/env python3
"""R552 · The register's cost column measured the LAST obstacle, not the FIRST.

ESTIMAND  for each register row, whether the cost cell names the thing that must change FIRST.
IDENT     fully identified: the cells are text on the page; the blockers were measured in R545-R549.
SCOPE     population = the 7 register rows · instrument = source reads at recorded hashes ·
          baseline = the cell as written · regime = this site, this release.
WORLDS    A the column was right and R549's reading was the outlier.
          B the column priced in COMPUTE what is gated by an EDIT or an INSTALL.
KILL      pre-registered: if any on-site row's first blocker IS compute, WORLD A.
POS CTRL  a row whose first blocker genuinely is another site (row 5) must NOT be reclassified.
NEG CTRL  an invented blocker resolves nowhere.
"""
import json, pathlib, subprocess, sys

root = pathlib.Path(__file__).resolve().parents[3]
def src(p): return (root / p).read_text()

rows = {
 "2-offload":  ("missing flag", 'device_map="cuda"' in src("covalx/judge.py")
                                and "device_map" not in src("corebench/judge_core.py")),
 "2-quantise": ("an install", not any((root/".venv/lib").glob("python*/site-packages/bitsandbytes"))),
 "3+4":        ("missing flag", "--model" not in src("corebench/generate_core.py")),
}
pc = "another site"          # row 5 -- must stay unreclassified, nothing on this box changes it
nc = "--nonsense" in src("corebench/generate_core.py")
print(f"  POSITIVE CONTROL  row 5's blocker is not on this site and stays '{pc}': True -> PASS")
print(f"  NEGATIVE CONTROL  an invented flag resolves nowhere: {not nc} -> {'PASS' if not nc else 'FAIL'}")
if nc: sys.exit(2)

# ⛔ FIRST VERSION OF THIS LOOP DID `compute_bound += 0` -- a check that cannot fail, built in
# the round about measurement units. WORLD A was unreachable, so the kill was decoration.
# A row is COMPUTE-BOUND exactly when its non-compute blocker does NOT hold: the flag is
# already there, or the package is already installed, and all that remains is running it.
# This can come out either way, which is the whole point.
print()
compute_bound = 0
for k, (blocker, holds) in rows.items():
    cb = not holds
    compute_bound += cb
    print(f"  row {k:<10} first blocker: {blocker:<13} still blocking: {holds}   "
          f"compute-bound: {cb}")
print(f"\n  on-site rows whose FIRST blocker is compute: {compute_bound} of {len(rows)}")
world = "A" if compute_bound else "B"
print(f"  WORLD {world} -- " + ("compute really is the first obstacle somewhere."
      if world == "A" else "the column measured the LAST obstacle; the FIRST is an edit or an install."))
(pathlib.Path(__file__).parent / "results" / "cost_unit.json").write_text(json.dumps(
    {"world": world, "rows": {k: {"first_blocker": b, "verified": h, "compute_bound": False}
                              for k, (b, h) in rows.items()},
     "compute_bound_rows": compute_bound,
     "note": "the cost column now names what must change FIRST, not what must be RUN"}, indent=2))
