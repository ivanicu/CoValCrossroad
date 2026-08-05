# R467 · same conversations, different text — and this round's first verdict was FALSE

**The decision this round makes safe:** whether R466's UNVERIFIED is a data limit or a gap in that
round. **A data limit — but not the one either round first named.** `UNVERIFIED`.

## ⛔ The announced step indicted the round that proposed it

R466 concluded the two ③-instruments *"cannot be joined on disk without a mapping, and none was
used."* **But the satisfaction files are keyed in the RANKING id space while their criteria came from
the RUBRIC file** — so a mapping must already exist somewhere, or `sat_coval_core.npz` could not have
been built. *Thirty-fifth announced step checked; R466's headline was a candidate over-claim.*

## ⛔ And this round's first verdict was FALSE — caught by its own null

The first run reported **`W-DISJOINT`: coverage 0.0000, "the two files describe different
conversations, every campaign number crossing them inherits that."** That is a campaign-wide claim,
and it was **wrong**.

**What caught it:** the NEGATIVE control returned **0.0000 too**. ⭐ **When a result equals its own
null, it is silence, not a measurement** — and the round had flagged that shuffling preserves the
multiset and is therefore not a proper null for coverage. Looking at the object settled it.

**The normaliser was broken.** The two files use **different message schemas** — rubric messages carry
**no `role`** and their content is `{'content_type':'text','parts':[…]}`; comparison messages carry
`role` and a plain string. **The two normalisations could never match, so coverage was 0 by
construction.**

**The control the first version lacked:** a **cross-file** case where the answer is known. A
within-file uniqueness check (which passed at 1.0000 both ways) **cannot catch a normaliser that is
merely incomparable across files** — §4: *a positive control that shares the instrument's blind spot
confirms the instrument and licenses nothing.*

## ⭐ The diagnosis is the result

Record 0 of each file **is the same exchange**:

| | text |
|---|---|
| comparisons | *"…should people stop **eating** beef in the world"* |
| rubric | *"…should people stop **eat** beef in the world"* + `all finished_successfully` tokens |

> **The files describe the SAME conversations in DIFFERENT TEXT.** Neither an id join (intersection
> **0**, confirmed) nor an exact-text join (**0.0000** after the schema fix) can bridge them, and a
> fuzzy join is excluded by design because it would decide the question by threshold.

## What this changes

- ⛔ **`W-DISJOINT` is dead.** The far larger claim — *"the two files describe different
  conversations"* — is **false**, and it would have contaminated every campaign number crossing them.
- ✅ **R466's UNVERIFIED stands**, but for a reason R466 did not give: not *"no mapping was used"* but
  *"no exact mapping exists, because the same conversation is stored with different wording."*
- ⚠ **Still open:** whether a fuzzy join would be sound. Deliberately not attempted here.

## Controls

| control | returned |
|---|---|
| ANCHOR — the id join recomputed | intersection **0** ✅ *(R466 measured 0)* |
| g=0 — each file against itself | unique-text share **1.0000** / **1.0000** ✅ — *a DERIVATION: it tests the normaliser, not the join* |
| NEGATIVE — vs a shuffled copy | **0.0000** ⚠ *shuffling preserves the multiset, so this is **not** a null for coverage — it only detects a collapsing normaliser, and saying so is what exposed the artifact* |
| **CROSS-FILE** *(added after the first run)* | **FAIL** ✅ — *and its failure is what makes coverage 0.0000 silence rather than a finding* |
| LENGTH | min 126 / median 276 / max 4150 — no truncation spike |

## Impossible here, named

- **a fuzzy join** — excluded by design; a threshold would decide the question rather than measure it.
- **proving two identical-text conversations are the same release object** — necessary, not
  sufficient; moot here, since no texts are identical.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
