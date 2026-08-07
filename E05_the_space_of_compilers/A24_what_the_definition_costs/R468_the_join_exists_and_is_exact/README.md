# R468 · the join exists, is exact and total — and two rounds' headlines were over-stated

**The decision this round makes safe:** whether R466's UNVERIFIED is a permanent data limit.
**It is not.** `W-EXACT`.

## ⛔ The announced calibration was circular

R467 closed proposing to calibrate a fuzzy threshold from *"the conversations whose text happens to be
unambiguous."* **Identifying true pairs is what the join provides** — estimating their similarity
distribution presupposes it. *Thirty-sixth announced step checked.*

## ⭐ And neither prior round tried the criterion texts

R466 and R467 both joined on **conversation** text, which the rubric file stores degraded
(*"eat"* vs *"eating"*, plus `all finished_successfully` tokens). But the **criterion** texts are
short exact strings carried in **both** spaces — `core_full.json` in the ranking space,
`conversation_rubrics.jsonl`'s `coval_full` in the rubric space. **No threshold is needed at all.**

## Result

| | |
|---|---|
| **coverage** | **1.0000** (968 of 968) |
| **uniqueness** | **1.0000** |
| ambiguous | **0** |
| no-hit | 0 |
| surplus rubric records | 18 (986 − 968) |

## ⭐⭐ Validated on a different channel from the one it was built on

The join is built from **criteria** and checked on **conversations** — two independent data channels.

| | conversation similarity |
|---|---|
| **joined pairs** | **0.8811** |
| random pairs | **0.2859** |
| a record against itself | 1.0000 — **DERIVATION** |

**A high validation number here cannot be an artifact of the construction**, because the construction
never looked at conversation text.

## Controls — both anchors are the prior rounds' own numbers

| control | returned |
|---|---|
| **ANCHOR-1** — R466's id join | intersection **0** ✅ |
| **ANCHOR-2** — R467's conversation-text join | **0.0000** ✅ |
| NEGATIVE — random pairings | 0.2859, the only baseline that makes 0.8811 readable |
| AMBIGUITY | **0**, printed even though zero — *"unique" is a claim, not a default* |

⭐ **Requiring a round to reproduce the numbers it is about to narrow** is what separates a correction
from a competing measurement: both anchors passed before anything was overturned.

## What this overturns

- ⛔ **R466: *"the two instruments cannot be joined on disk without a mapping, and none was used."*
  Over-stated** — an exact mapping is recoverable from the release itself.
- ⛔ **R467: *"no exact join exists, because the same conversation is stored with different
  wording."*** True of **conversation** text, **false as stated** — the criteria join exactly.
- ✅ **Consequence: R466's UNVERIFIED is now DECIDABLE.** ③'s two instruments can be pointed at one
  population, and the 19-arm UNKNOWN region can be revisited.

⭐ **The pattern across three rounds is the lesson.** R466 concluded *"cannot be joined"* from one
failed join; R467 concluded *"different conversations"* from a second; both generalised from **the
instrument they happened to try** to **what the data permits**. **A failed join licenses "this join
failed", never "no join exists"** — the second is a claim over every possible key, and neither round
enumerated one.

## Impossible here, named

- **proving a joined pair is the same release object** — shared criteria plus 0.8811 conversation
  similarity is strong evidence; the release ships no cross-space key to settle it.
- **the 18 surplus rubric records** — 986 > 968, reported rather than explained away.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
