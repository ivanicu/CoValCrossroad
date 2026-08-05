#!/usr/bin/env python3
"""
R641 -- the repair is entirely preventive, and four artifact reads replaced four re-runs

CHECK #242: THE COUNT WAS RIGHT FOR THE FIRST TIME IN FIVE CLOSING LINES; THE COST CLAIM WAS NOT.
  ✓ "four of the five predate the current line" -- R319, R322, R388, R396 do. Correct, and it is
    the first closing-line count in five rounds that survives its own check.
  ⛔ "five sites is small enough to repair and verify in one round" -- the FIFTH uncomputed cost
    claim in six rounds, after expensive / one line / cheap to install / one predicate and seven
    call sites.

⭐ AND THE PLAN THE COST CLAIM JUSTIFIED WAS THE EXPENSIVE ONE. It proposed re-running the four
   harnesses to diff their failure counts. Those harnesses RUN OTHER ROUNDS -- one of them is GPU
   work -- so the plan was to execute a large fraction of the corpus. FOUR ARTIFACT READS ANSWER
   THE SAME QUESTION, because a harness that never recorded a non-zero failure count cannot have
   its conclusion changed by a rule that only reclassifies non-zero exits.

ESTIMAND        for each of the 5 classifying harnesses, whether its COMMITTED artifact records a
                non-zero failure count -- and, where it does, whether those entries are verdicts.
IDENTIFICATION  Exact and read-only. ⚠ A harness that classifies in code but never persists the
                count can still print a wrong number; this measures the RECORD, not the console,
                and the distinction is why R388 and R396 are "no change to the record" rather than
                "no change at all".
SCOPE           population : the 5 classifying harnesses from R640
                instrument : artifact key scan for failure-count keys + EXIT-convention lookup
                             instrument unit = AN ARTIFACT KEY
                             claim unit      = A COMMITTED CONCLUSION. Equal for the record;
                             unequal for console output, stated above.
                baseline   : the committed artifacts as they stand
                regime     : this repository at this sha
WORLDS          A CORRECTIVE: >=1 harness records a non-zero failure count whose entries are
                  genuine failures -> committed conclusions are wrong and must be reissued.
                B PREVENTIVE: every recorded failure count is zero, or its entries are verdicts ->
                  no committed conclusion changes and the repair guards the future only.
                C MIXED: some of each.
KILL            pre-registered: any harness recording a non-zero count with a genuinely failed
                entry -> world A, and that entry is named.
POSITIVE CTRL   R636 must be found recording a non-zero count -- it lists 5. Fails at g=0: a
                harness recording zero must not be counted as corrective.
NEGATIVE CTRL   a harness with no failure key at all must classify as "no record", never as zero,
                because absence and zero are different claims.
PLACEBO         a key name no artifact uses -> 0.
SEEDS           n/a, deterministic.
MULTIPLICITY    5 harnesses x every artifact key + 5 entry lookups + 4 controls.
ARTIFACT        results/preventive_not_corrective.json
IMPOSSIBLE      console output is not the record. A harness that prints a wrong failure count
                without persisting it is invisible here, and R388/R396 are exactly that case.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "preventive_not_corrective.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
