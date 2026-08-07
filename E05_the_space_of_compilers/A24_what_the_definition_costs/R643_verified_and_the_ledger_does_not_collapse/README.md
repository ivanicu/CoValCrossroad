# R643 · Verified — and my diagnosis of the ledger is retracted by measuring it

**Decision this makes safe:** whether the prohibition and its cleanup work together. **Both do.**

| control | result |
|---|---|
| **POSITIVE** — byte-identical | **43** (was 38) — *that jump is the prohibition's effect* |
| **NEGATIVE** — tree restored to pre-run state | **PASS** ✓ |
| **PLACEBO** — files outside a round's `results/` | **0** |
| **VERDICT** | **B SOME MOVE — 12 of 43** |

**The repair survived**: the `PROHIBITION` token is still on disk after the run — which R642
established it would *not* be under the old directory-scoped restore. ⚠ The denominator moved
**38 → 43** and the numerator held at **12**: the design working, not the finding changing.

## ⛔ And the ledger diagnosis I gave last round is retracted, by measuring it
I found a prior commit recording the identical self-contamination vector I had just called **new**,
and concluded: *"the ledger works as a record and fails as an index."* **That framing implies an
index is the missing piece.** Measured:

| | |
|---|---|
| retraction entries | **390** |
| explicitly recording a hazard **already known** when it fired | **26 (7%)** — six most recent all from this arc |
| **10 candidate classes cover** | **98 (25%)** |
| **unclassified** | **292** |

⭐ **A ledger whose entries do not collapse cannot be fixed by indexing them.** The retrieval problem
is **not a missing index** — most of the ledger has never been classified at all, and **there is no
evidence the remaining 292 share any structure.**

## ⚠ And both counts measure the same thing: my current vocabulary
The phrase lists are mine, so **they can only find classes I have already named** — which is exactly
the class that would explain why a recorded hazard is re-encountered *without being recognised*.
**Neither 26 nor 98 is a property of the ledger; both are properties of what I can articulate today.**

**IMPOSSIBLE, named:** **no self-authored keyword instrument can discover a failure class its author
has not yet named.** That is not a defect of this design — it is why the question is hard, and it
bounds every number above.

## The sentence I can no longer write
> *"the ledger works as a record and fails as an index."*

**An index presumes classes.** 75% of the entries fall outside every class I could name, and the
instrument that found the other 25% was built from my own vocabulary.

## NEXT
The prohibition is verified at one site and the remaining four are inert-by-record (R641), so the
production work is done. **The open item that is not about instruments is the arc's oldest: `②`'s
baseline is unrebuildable on the second release (R605), and R618's five-field specification says what
a third object must provide.** Return to it — **check whether any object on disk besides the two
releases satisfies those five fields**, because if one does the definition becomes testable
cross-object for the first time, and if none does the specification is the deliverable and the arc
can close on it.
