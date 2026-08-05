#!/usr/bin/env python3
"""Backfill the artifact R543-R546 never persisted, by RE-VERIFYING each claim against source.

⛔ WHY. Four consecutive rounds read source rather than running an experiment, created an empty
results/ directory, and persisted nothing. An empty results/ reads as "persisted" to a loose
check -- mine, one command earlier. Their findings are cited by the register, so they are
load-bearing with no checkable evidence behind them.

This does NOT file the old conclusions. It re-reads the source and records what is there now,
with a sha256 of every file consulted, so a later round can attack the claim rather than the memory.

POSITIVE CONTROL: a predicate KNOWN true must verify (judge_core.py exposes --model).
NEGATIVE CONTROL: a predicate known FALSE must not (judge_core.py exposes --nonsense).
"""
import hashlib, json, pathlib, re, sys

root = pathlib.Path(__file__).resolve().parents[2]  # this file sits at A-level, not R-level
def sha(p):
    return hashlib.sha256((root / p).read_bytes()).hexdigest()[:16]
def src(p):
    return (root / p).read_text()

CLAIMS = {
  "R543_the_command_was_in_the_log_too": [
    ("generate_core.py takes --batch, so batch size is a recorded field",
     lambda: "--batch" in src("corebench/generate_core.py"), "corebench/generate_core.py"),
  ],
  "R544_the_generator_is_greedy": [
    ("generation is greedy (do_sample=False), so a re-run is byte-identical",
     lambda: "do_sample=False" in src("corebench/generate_core.py"), "corebench/generate_core.py"),
  ],
  "R545_the_generator_has_no_knobs": [
    ("generate_core.py exposes NO --model flag",
     lambda: "--model" not in src("corebench/generate_core.py"), "corebench/generate_core.py"),
    ("FEWSHOT is a module-level constant, not a parameter",
     lambda: re.search(r"^FEWSHOT\s*=", src("corebench/generate_core.py"), re.M) is not None,
     "corebench/generate_core.py"),
  ],
  "R546_rows_three_and_four_are_nested": [
    ("judge_core.py DOES expose --model (the asymmetry rows 3+4 lack)",
     lambda: "--model" in src("corebench/judge_core.py"), "corebench/judge_core.py"),
    ("covalx/judge.py hard-codes device_map=\"cuda\"",
     lambda: 'device_map="cuda"' in src("covalx/judge.py"), "covalx/judge.py"),
  ],
}

pc = "--model" in src("corebench/judge_core.py")
nc = "--nonsense" in src("corebench/judge_core.py")
print(f"  POSITIVE CONTROL  a known-true predicate verifies: {pc} -> {'PASS' if pc else 'FAIL'}")
print(f"  NEGATIVE CONTROL  a known-false predicate does not: {not nc} -> {'PASS' if not nc else 'FAIL'}")
if not pc or nc:
    sys.exit(2)

allok = True
for rd, claims in CLAIMS.items():
    d = root / "E05_the_space_of_compilers" / "A24_what_the_definition_costs" / rd / "results"
    d.mkdir(parents=True, exist_ok=True)
    out = {"round": rd, "backfilled_by": "R551", "note":
           "re-verified against source; NOT a copy of the original conclusion", "claims": []}
    print(f"\n  {rd}")
    for text, fn, f in claims:
        v = bool(fn())
        allok &= v
        out["claims"].append({"claim": text, "verified": v, "file": f, "sha256_16": sha(f)})
        print(f"    [{'OK ' if v else 'XX '}] {text}")
        print(f"           {f} @ {sha(f)}")
    (d / "backfilled_evidence.json").write_text(json.dumps(out, indent=2) + "\n")

print(f"\n  every re-verified claim still holds: {allok}")
sys.exit(0 if allok else 1)
