#!/usr/bin/env python3
"""
R643 -- the prohibition is verified, and my diagnosis of the ledger is retracted by measuring it

① VERIFIED. Re-running the harness with the repaired restore: all three controls pass.
   POSITIVE 43 byte-identical (was 38 -- that jump IS the prohibition's effect, since the five
   rounds it used to call failures all exit 1 as a declared verdict). NEGATIVE the tree restores
   to its pre-run state. PLACEBO 0 files outside any round's results/. VERDICT B SOME MOVE,
   12 of 43. The repair survived: the PROHIBITION token is still on disk after the run, which is
   what R642 established it would not be under the old directory-scoped restore.
   ⚠ The denominator moved 38 -> 43 and the numerator held at 12. That is the design working, not
   a change in the finding.

② AND THE LEDGER MEASUREMENTS, WHICH REFUTE MY OWN DIAGNOSIS IN THE SAME ROUND THAT MADE IT.
   Last round I found a prior commit recording the identical self-contamination vector I had just
   called NEW, and concluded: "the ledger works as a record and fails as an index."
   That framing implies an index is the missing piece. Measured:
     - 26 of 390 entries (7%) explicitly record a hazard that was ALREADY KNOWN when it fired,
       and the six most recent such entries are all from this arc;
     - but 10 candidate classes cover only 98 of 390 entries -- 25%. 292 are unclassified.
   ⭐ A LEDGER WHOSE ENTRIES DO NOT COLLAPSE CANNOT BE FIXED BY INDEXING THEM. The retrieval
   problem is not a missing index; most of the ledger has never been classified at all, and there
   is no evidence the remaining 292 share any structure.

③ AND BOTH COUNTS MEASURE THE SAME THING: MY CURRENT VOCABULARY. The phrase lists are mine, so
   they can only find classes I have already named -- which is precisely the class that would
   explain why a recorded hazard is re-encountered without being recognised. Neither 26 nor 98 is
   a property of the ledger; both are properties of what I can articulate today.

IMPOSSIBLE, named: no self-authored keyword instrument can discover a failure class its author has
not yet named. That bound is not a limitation of this round's design -- it is the reason the
question is hard, and it applies to every measurement in ② and ③.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "verified.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
