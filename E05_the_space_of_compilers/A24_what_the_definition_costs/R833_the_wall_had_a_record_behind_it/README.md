# R833 · the wall had a construction record behind it

**The decision this made safe:** whether the interval's width is a permanent property of this
release. **It is not.** A per-arm construction record exists in the repository — in the git log —
and I declared it absent one round after using that discipline on every commit I made.

Design in `PREREGISTRATION.txt`, committed before `run.py` existed. `run.py` committed before it ran.

## The wall, and why it was the first thing checked

R832 closed: *"Narrowing it needs a per-arm construction record — that is a requirement for the next
release, not something this one can answer."* **§4: an unchecked wall is UNVERIFIED, never SETTLED.**

The wall rested on `DEFINITION.md`'s *"7 arms have provenance the source cannot classify."*
⛔ **"The source" there means `select_core.py`'s `SELECTORS` list. I read it as a claim about the
repository.** Instrument-unit vs claim-unit — **fourth time this session, and the first time I
inherited the error from my own document rather than making it fresh.**

## Result — W-RECORD-EXISTS

| | |
|---|---|
| UNKNOWN arms examined | **11** |
| decided by a record already in the repo | **7** |
| controls: positive (`coval_core`-style → must not be ADMITTED) · negative (silent → UNDECIDED) · g=0 | **EXCLUDED · UNDECIDED · identical** |
| two-seed | byte-identical `49c8cb9347adeb3e404851e391b0c717` |

**The wall is false.** One record is enough, and there are at least two unambiguous ones:

- **`generic`** (rank **21**) — *"The object that settles it: four GENERIC quality criteria,
  identical on every prompt"*, with the four listed verbatim. No labels, no rubric, no prompt.
- **`promptecho`** (rank 66) — *"use the prompt's own user sentences as the four criteria."*

⭐ **And R831's NEXT — *"build a second family of label-free substantive arms"* — is answered by arms
already on disk.** P4 again: the thing I proposed to build was committed.

## ⛔ The rule over-fires, and quoting every decisive sentence is what showed it

**3 of the 7 "decided" statuses are misreadings — adjudicated by reading the quotes the artifact
carries:**

| arm | rule said | why it is wrong |
|---|---|---|
| `gen` | EXCLUDED | quote is *"the generator **never having seen** coval_full"* — **a negation**. The rule matched `coval_full` as evidence of use while the sentence asserts non-use |
| `genericpool16` | EXCLUDED | the quote is about the **clause's wording**, not the arm's inputs |
| `coval_core_sham` | ADMITTED | the quote is a commit **subject line** about clause testing, not a construction record |

⭐ **The general finding is the negation blindness.** A regex rule cannot distinguish *"X was used"*
from *"X was never seen"*, and here it **inverted the meaning of the sentence it matched**. §4's *a
search is an instrument* — with the sign flipped rather than the count.

**So: the existence claim is CONFIRMED (it needs one record, and two are unambiguous); the per-arm
table is a CANDIDATE LIST with a measured ~43% misread rate, and adjudication is the measurement.**

## What this round may not do

It does **not** change ③'s committed partition or `DEFINITION.md`'s three-valued discipline — those
are the instrument's output and a deliberate policy. ⚠ And a record for an arm **I built** is a
record of my own **action**; `coval_core` is someone else's object and correctly required the
release's own dataset card (R475). The round does not collapse those two situations.

## NEXT

The rule's failure is negation, and negation is what a construction record is full of — *"never
saw"*, *"does not read"*, *"without access to"*. A record-reading instrument that cannot parse
negation will mis-sign exactly the arms whose records are most careful. That is a property of the
rule, not of the corpus, and it is what a replacement has to handle.
