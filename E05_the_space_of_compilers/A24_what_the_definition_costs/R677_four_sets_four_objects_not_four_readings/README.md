# R677 · four sets, four OBJECTS — and the count is not identified

**⭐⭐⭐ The number of five-member sets denoting a ③-reading extension is 0–1, decided entirely by
whether a set's meaning comes from its PRODUCER or from its 21 RE-CITATIONS. Nothing in these
artifacts marks which citation computed a set, so a lineage question silently becomes a popularity
contest.**

## ⭐ CHECK #278 · R676's CLOSING ATTRIBUTION WAS ASSERTED, NEVER CHECKED
R676 closed: *"Each was produced by a different ③ variant — ③-rank, ③-as-written, ③-checkable,
③-published."* Reading the four rounds' own `ESTIMAND` lines:

| set | what its round actually says it is |
|---|---|
| `R470.P` | **"the arms admitted by ①∧②∧④ — the extension BEFORE ③ is applied"** |
| `R442.published_five` | the arms **CoVal published**; R442's own output prints *"and NEITHER is the published five"* |
| `R509.five` | a set inside a round whose stated answer is an extension of **ONE** |
| the 22×-cited set | the ③-rank extension — the only genuine ③ reading |

**Second time in this arc I asserted a mechanism produced something without checking (ledger 745 was
the first), and both times it was the round's LAST sentence — the one with no control attached.**

## THE SPECIFICATION CURVE OVER THE AGGREGATOR (G4 — every cell, including the killers)

| aggregator | genuine ③-reading extensions |
|---|---|
| **majority** over a set's citations | **0** |
| **any** citation stating ③ | **1** |
| **earliest** round id | **1** |

**Registered 1 [1,3]. It scores INSIDE under two aggregators and OUTSIDE under one — that split is
the tell.** The specifications disagree, so **no point is admissible, only the range 0–1.**

**Controls** (the classifier is a text instrument and gets its own): POSITIVE — the ③-rank set
classifies as a ③ extension → **PASS**. **g=0** — `R470.P`, a known pre-③ set, must *not* so classify
→ `b_before_three` → **PASS, it can separate**. NEGATIVE — `R404.rubric_rules` → `d_other`. PLACEBO —
a field in a round never mentioning ③ → `d_other`.

## ⚠ TWO MECHANICAL BUGS IN MY OWN INSTRUMENT, BOTH FOUND BY A CONTROL FAILING
1. **`or` short-circuits on a truthy string.** `kind_of("R339.published") or kind_of("R294.admitted")`
   never consulted the fallback, so the control asked **R339** — whose `ESTIMAND` contains no ③ — for
   a ③ verdict, and I nearly read its FAIL as the classifier's. *§4's "the control fails for its own
   reasons": its two sides were not the same object.*
2. **`\bpublished\b` cannot match `published_five`** — `_` is a word character, so there is no
   boundary. `R442.published_five` was classified a ③ extension when it is CoVal's publication list.

Both are coding defects, fixed as such. **Neither was a threshold tuned after seeing the answer.**

## ⛔ WHAT IS RETRACTED FROM R676
*"Four extension readings sharing `coval_core`"* — the four were **one ③ reading, one pre-③ set, one
publication list, and one intermediate**. R676's census (6 distinct five-member arm sets) stands; its
**interpretation as four readings of one clause does not.**

## ⭐ THE STANDING FINDING IS A MISSING FIELD
**32 citations of these sets exist in the corpus and not one records whether it COMPUTED the set or
COPIED it.** That absence is what let a set cited 22× outvote its own producer, and it is what
produced R676's error one round earlier. A next site inherits this at the artifact layer, not the
clause layer.

## IMPOSSIBLE HERE
Proving a round's code computed what its docstring says would need re-execution of 600+ rounds
against their own inputs, and 93 of them are corpus-dependent (measured earlier in this arc).
**Stated denotation is what is available, and it bounds field-name/object agreement from above.**

## NEXT
The producer/copier distinction is absent from all 32 citations
(`results/denotation.json`, field `spec_curve_aggregator`, which is 0 under majority and 1 otherwise).
Git can supply it without any new convention: for each set, find the earliest commit whose diff
ADDS those members to a `results/*.json`, and treat that round as the producer. Report how many of
the 6 sets get a unique producer that way, and how many remain ambiguous because several rounds
introduced identical members in the same commit.
