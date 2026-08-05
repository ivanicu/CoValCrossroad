#!/usr/bin/env python3
"""
R648 -- the suite was consistent, I truncated its output, and committing a round moved its numbers

CHECK #249 HELD (8 printed minus 2 broken = 6 was correct arithmetic on a wrong population).

① R647 IS RETRACTED. It reported "the summary exceeds its own printed listing by exactly three."
  Reading run_all.py: lines 151-153 print every member of buckets["FAIL"]; line 161 counts
  len(buckets['FAIL']). The same list. THE SUMMARY CANNOT EXCEED THE LISTING.
  The discrepancy was mine: I invoked the suite as `run_all.py 2>&1 | tail -25` and treated the
  surviving lines as complete. The capture lacks both the "ran N gates" header and the "META-gates
  excluded" line, which print BEFORE the listing.
  ⭐ AND R647 SAW THE TRUNCATION WITHOUT FOLLOWING IT HOME -- it corrected an eyeball count of nine
  to a parsed ten and wrote "off a truncated display" in its own README, then treated that same file
  as the population. The symptom was fixed and the cause left standing, in adjacent sentences.

② THE COMPLETE CAPTURE: PASS 25 of 46 · FAIL 15 · UNRUNNABLE 3 · ERROR 3, and the labels
  LIVE-DEBT 13 + BY-DESIGN 1 + CONTROL-BROKE 1 sum to exactly 15. The suite is consistent.
  ⚠ My parse said 16 FAIL rows: `^\s+FAIL\s` matched the suite's OWN SECTION HEADER, "FAIL
  breakdown — a single count conflates three unlike things:". A pattern that matches the report's
  furniture as data -- the same class as every over-matching search in this arc.

③ THE MIS-FILED GATES ARE 4 OF 13, NOT 2 OF 8. `code_states_a_bound_the_reader_never_sees`,
  `retired_framing_in_emittable_source`, `seed_filter_is_disclosed`, `source_stamp_is_current` all
  show a Traceback or a SyntaxWarning in their own message. Two of them I had never seen, because
  they were in the rows my pipe removed. The earlier "2 of 8" had the right observation and the
  wrong denominator.

④ AND COMMITTING A ROUND ABOUT THE SUITE MOVED THE SUITE'S NUMBERS. Between the two runs: PASS
  26->25, FAIL 13->15, UNRUNNABLE 4->3. R647's commit added 4 files and 123 insertions. That is
  R636's mechanism -- the corpus is the population and every round adds to it -- arriving on the
  instrument that measures the corpus. ⚠ NOT non-determinism: the tree differed, and the diff is
  in the git log.

IMPOSSIBLE: the classifier reads MESSAGES, so "the gate broke" is inferred from output text. A gate
that fails silently while broken is invisible to this count, which is therefore a LOWER bound.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "consistent.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
