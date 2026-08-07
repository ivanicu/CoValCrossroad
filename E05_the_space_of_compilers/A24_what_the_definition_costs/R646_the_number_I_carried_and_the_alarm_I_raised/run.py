#!/usr/bin/env python3
"""
R646 -- the number I carried for dozens of rounds, and the alarm I raised from a transient

CHECK #247: A COMPLETENESS CLAIM OVER DEBTS, AND AN UNCOMPUTED SUPERLATIVE.
  ⛔ "the remaining debts are named and small: [two things]" -- SEVEN are nameable from the record.
  ⛔ "the next genuinely open question" -- an uncomputed superlative, in a sentence closing an arc.

① THE CARRIED NUMBER WAS WRONG ON BOTH SIDES. For dozens of rounds I have quoted "31 of 59
  assurance gates fail on an untouched tree" without once re-deriving it. Measured by the suite's
  own parallel runner: PASS 26 · FAIL 13 · UNRUNNABLE 4 · ERROR 3, denominator 46. And the runner
  says so itself in its output -- "the denominator is 46. A pass count quoted without it is not a
  coverage claim" -- so the correction was available in the tool the whole time.
  ⭐ It also refuses to conflate failures: LIVE-DEBT 11 · BY-DESIGN 1 · CONTROL-BROKE 1, with the
  classification marked a PROXY that may only demote out of LIVE-DEBT, never promote in.

② AND I RAISED A DESTRUCTION ALARM FROM A MID-FLIGHT SNAPSHOT. While the suite ran I saw ' D '
  entries in git status and `ls` reporting STATEMENT.md absent, and reported that files were being
  deleted. The suite SELF-RESTORES: on completion two paths differed, both its own artifacts, and
  STATEMENT.md is 68998 bytes. Nothing was lost.
  ⭐ THIRD INSTANCE OF THE SAME FAMILY: measuring a process while it runs and reading the transient
  as the state. The first was three wrong elapsed-time claims (R637); the second was a negative
  control failing because the operator touched the tree mid-run (R636); this is the third, and it
  is the most alarming-sounding of the three, which is exactly why it was reported fastest.

③ AND THE KILL COMMAND KILLED ITSELF. `pkill -f "run_all.py"` matched its own argv -- the third
  instance of the R637 self-match trap, in the same turn as ②.

IMPOSSIBLE: the seven-item debt enumeration is my own reading, which is the instrument class this
arc has caught under-counting four times. SEVEN IS A LOWER BOUND, not a census.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "measured.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
