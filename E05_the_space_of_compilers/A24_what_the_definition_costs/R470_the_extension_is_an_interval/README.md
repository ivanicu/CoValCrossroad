# R470 · the extension is **[0, 1]**, not 1 — and the convention that makes it 1 was never stated

**The decision this round makes safe:** what the definition's extension actually is.
**An interval, with a named convention.** `W-INTERVAL`.

## ⛔ My own announced sentence had the direction backwards

R469 closed: *"the document reports an extension of ONE arm, and that count silently treats the 19
UNKNOWN arms as **excluded**."* **It treats them as ADMITTED.** `coval_core` is itself UNKNOWN under
③ (R466), so under unknown-as-excluded the released core drops out and the extension is **0**.
*Thirty-eighth announced step checked; its premise inverted before anything ran.*

## ⛔ And the committed value rests on an instrument R469 killed

The document states *"the extension under the written reading is 1, not 0 (R443)"*, and **R443's
justification is the containment measurement (0.0779)**. R469 showed containment is **constant on ③'s
own partition** and therefore provably unable to decide it. **So the "1" is not a measurement — it is
a convention whose supporting instrument is now known not to support it.**

## Result

`P` = the arms admitted by ①∧②∧④ (committed by R442), and ③'s verdict on each:

| arm | ③'s verdict |
|---|---|
| **`coval_core`** | **UNKNOWN** |
| `oracle_k4` | EXCLUDED |
| `oracle_k4_fit1` | EXCLUDED |
| `greedy_k4_fit1` | EXCLUDED |
| `indep_k4_fit1` | EXCLUDED |

| reading of ③'s UNKNOWN | extension |
|---|---|
| unknown-as-**EXCLUDED** | **0** |
| unknown-as-**ADMITTED** | **1** ← reproduces the committed value |
| unknown-as-**UNVERIFIED** | **0 confirmed + 1 unverified** |

> ⛔ **The document's single integer rests on an unstated convention**, and the choice is not
> innocent: **the only arm it admits is `coval_core`, the object the definition was written from.
> Under the other reading the extension is EMPTY.**

⭐ **The honest form is the interval [0, 1] with the convention named** — and the third reading
(**0 confirmed, 1 UNVERIFIED**) is the one **this campaign's own proxy ledger requires**, since
UNVERIFIED must never be folded into either EXCLUDED or ADMITTED. **The document has been folding it
into ADMITTED for the whole campaign.**

## Controls

| control | returned |
|---|---|
| DETERMINISM — `clause3_as_written` re-run twice | identical ✅ *(it takes no seed; variation would mean the arm list is unstable underneath it)* |
| MEMBERSHIP — `coval_core` ∈ P | true ✅ *(a P without it would not be the set the document describes)* |
| **ANCHOR** — which reading reproduces the committed 1 | **unknown-as-ADMITTED** ✅ |
| g=0 — with an empty UNKNOWN set | the three readings coincide **by construction** — a DERIVATION, and precisely why the convention matters only here |

⚠ **NO POSITIVE CONTROL IS POSSIBLE, and that is stated rather than faked.** There is no ground-truth
extension to recover. Every number here is a **count under a stated convention**, and the claim is
about the **spread across conventions**, which is arithmetic once the sets are fixed. **A round that
cannot have a positive control should say so in the design, not omit the line.**

## What this closes

- **The extension is [0, 1]**, not 1. The document must name its convention or report the interval.
- **Under the reading this campaign's own standard requires**, the definition has **0 confirmed
  members** and **1 unverified** — and the unverified one is its own paradigm case.
- ⚠ **This does not say the definition is wrong.** It says the definition's extension has never been
  measured — it has been *counted under a convention*, and the convention was invisible.

## Impossible here, named

- **deciding which reading is correct** — a definitional choice, not a measurable fact. This round
  measures what the choice costs and declines to make it.
- **a ground-truth extension** — none exists; hence no positive control, said plainly.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
