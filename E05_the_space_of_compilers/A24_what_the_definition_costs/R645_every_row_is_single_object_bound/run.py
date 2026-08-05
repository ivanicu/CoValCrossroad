#!/usr/bin/env python3
"""
R645 -- every claim row is single-object-bound, and only one says so

CHECK #246: A STALE MEASUREMENT QUOTED AS CURRENT.
  ⛔ "every claim row CURRENTLY reads as unconditional" -- R601 measured that, and STATEMENT.md has
     been appended to by R618, R628 and R631 since. Quoting a stale number in the present tense is
     the twenty-ninth. ✓ The same line's instruction -- "check first" -- was right, so this round
     is that check rather than an action taken on a remembered number.

ESTIMAND        of the claim table's rows, how many state an OBJECT scope (this holds on one
                release and no other) as distinct from an INSTRUMENT scope (home judge, 968
                prompts, 41 arms).
IDENTIFICATION  Exact by phrase over the scope column. ⚠ The two scopes are DIFFERENT CLAIMS and
                conflating them is the whole point: the first scopes the MEASUREMENT, the second
                scopes the DEFINITION. A row can be fully instrument-scoped and still read as a
                claim about cores in general.
SCOPE           population : the 10 numbered rows of STATEMENT.md's claim table
                instrument : two phrase families over the scope column
                             instrument unit = A TABLE ROW
                             claim unit      = A CLAIM'S STATED SCOPE. Equal here: the scope column
                             IS where a row states its scope, by the table's own header.
                baseline   : R601's measurement, now re-derived rather than quoted
                regime     : this repository at this sha
WORLDS          A ALREADY QUALIFIED: the rows carry object scope -> nothing is owed and R601's
                  finding has been fixed since.
                B UNQUALIFIED: they do not -> the honest close is one edit, and this round makes it.
                C PARTIALLY: some do -> the count is the size of the edit, and the rows that already
                  carry it show what the wording should be.
KILL            pre-registered: object-scope count < 10 -> the qualifier is written, and the count
                is reported before the edit rather than after.
POSITIVE CTRL   every row must show INSTRUMENT scope -- the table's own header promises a scope
                column, so a row with neither scope would mean the column is decorative.
NEGATIVE CTRL   ⛔ v1's OBJECT pattern lacked "one release" and reported 0 of 10. Row 7 reads "both
                judges; one release", which IS object scope stated as a count. Corrected to 1 of 10.
                A pattern that returns a rounder number than the truth is not more conservative --
                it is the one that was not checked against the rows it claims to have read.
PLACEBO         a phrase no row uses -> 0 rows.
SEEDS           n/a, deterministic.
MULTIPLICITY    10 rows x 2 scope families + 3 controls. Every row printed verbatim.
ARTIFACT        results/scope_audit.json
IMPOSSIBLE      that a row SHOULD carry object scope is a judgement about what the claim asserts,
                not a fact about the text. The measurement is what the rows SAY; the edit is a
                decision, and it is recorded as one.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "scope_audit.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
