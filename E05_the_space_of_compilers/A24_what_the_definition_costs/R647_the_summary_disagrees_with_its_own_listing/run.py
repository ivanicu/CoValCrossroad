#!/usr/bin/env python3
"""
R647 -- the suite's summary disagrees with its own printed listing, by exactly three

CHECK #248: I ASSERTED THE NAMES EXIST WITHOUT CONFIRMING.
  ⛔ "eleven live-debt failures, EACH NAMED" -- the suite printed a BREAKDOWN COUNT and I inferred
     names from it. It does name them, so the concern was unfounded -- but checking produced the
     round's actual finding, which asserting would not have.

① THE SUMMARY EXCEEDS THE LISTING BY EXACTLY THREE, IN BOTH COUNTS.
     printed : FAIL 10 · ERROR 3 · UNRUNNABLE 4 · LIVE-DEBT 8 · CONTROL-BROKE 1
     claimed : FAIL 13 · ERROR 3 · UNRUNNABLE 4 · LIVE-DEBT 11 · BY-DESIGN 1 · CONTROL-BROKE 1
  The +3 is uniform and equals the ERROR/timeout count exactly -- so the most likely reading is that
  the three 90-second timeouts are counted as FAIL in the summary and printed under ERROR in the
  listing. ⚠ THAT IS A HYPOTHESIS FROM AN ARITHMETIC COINCIDENCE, not a reading of the code, and it
  is labelled as one. What is MEASURED is the discrepancy; what is GUESSED is its cause.

② TWO OF THE EIGHT PRINTED LIVE-DEBT ENTRIES ARE BROKEN GATES, VISIBLE IN THEIR OWN MESSAGES.
  `retired_framing_in_emittable_source` shows a Traceback; `seed_filter_is_disclosed` shows
  `SyntaxWarning: invalid escape sequence`. Neither is a debt in the deliverable; both are gates
  that crashed. So among the printed rows, GENUINE LIVE DEBTS ARE 6 OF 8.
  ⭐ And the suite predicted this in its own caveat: the classifier "may only DEMOTE out of
  LIVE-DEBT, never promote in", so LIVE-DEBT is its catch-all and over-reports by construction.
  The caveat was correct and the number was still quoted without it -- by me, one round ago.

③ AND I COMMITTED THE SAME ERROR WHILE REPORTING IT. I counted nine FAIL rows by eye off a
  truncated display; the parse says ten. ⭐ An eyeball count of a display is the failure this round
  is about, and it survived into the round's own first reading.

IMPOSSIBLE: whether an UNPRINTED row is a genuine debt cannot be judged from a summary that does not
list it. The three unnamed FAILs are UNVERIFIED -- neither assumed real nor assumed spurious.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "discrepancy.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
