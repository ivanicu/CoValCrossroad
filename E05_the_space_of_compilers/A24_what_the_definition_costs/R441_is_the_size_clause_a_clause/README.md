# R441 · the size line is two things — one is a derivation, the other is decoration **on n=1**

**The decision this round makes safe:** whether the size line belongs in the definitional
conjunction. **Half B does not — that is forced. Half A is not demoted, because the evidence is one
arm.**

## The line is two different things, which is why it survived unexamined

> *"Its size, under that same judge J, is **greater than one**; sizes **3 to 8 are not
> distinguishable** by this release."*

| | status |
|---|---|
| **HALF B** — *"3 to 8 are not distinguishable"* | **A DERIVATION.** A statement about *resolution* cannot remove a member. It excludes nothing **by construction** — it is a **caveat, not a clause**, and no measurement changes that. |
| **HALF A** — *"greater than one"* | A clause *if* it removes something ②∧③∧④ leaves. **Measured below.** |

## Result — `W-DECORATION`, on one arm

| | |
|---|---|
| arms with a **readable k** | **52** (k values present: 1, 2, 3, 4, 6, 8, 12, 16, 39) |
| arms with **k = 1** | **1** — `topw_k1` |
| its status | ② **✗** · ③ ✓ · ④ ✓ → **already excluded by ②** |
| **arms half A removes that ②∧③∧④ would admit** | **0 of 1** |

## ⛔ And half A is *not* demoted — deliberately

The evidence is **a single k=1 arm**. This standard's own §3 says a cheap attack that appears to
kill a claim is the most expensive kind of error, because **it retracts something true**. Removing a
clause from a definition on n=1 is exactly that.

**So: the finding is recorded, the clause stays, and what changes is the document's honesty about
it** — half B is restated as the caveat it provably is, and half A carries its evidence.

**What would settle it:** constructing a k=1 core that ②∧③∧④ *admits*. That is a generation job with
its own assumptions, and its absence here is a statement about **the arms this campaign built**, not
a proof about k=1 cores.

## Controls

| control | returned |
|---|---|
| **POSITIVE — k read from the OBJECT must recover k encoded in NAMES** | **43 arms carry both; 0 disagreements** ✅ |
| g=0 — arms with no core file → **UNKNOWN**, never 0, never dropped | **4**: `coval_core`, `coval_core_2bA`, `coval_core_2bB`, `generic_reprov` ✅ |
| NEGATIVE — the k distribution must have spread | **[1, 2, 3, 4, 6, 8, 12, 16, 39]** ✅ |
| PLACEBO — arms excluded by `k > 0`, which every core meets | **0** ✅ |

⚠ **k is read from the committed core JSON, never parsed from the arm's name.** A name-parse is a
grep and a grep is an instrument — `random_k12_s0` and `topw_k1` differ by one character, and this
campaign's ledger carries **three** separate entries for loose patterns returning confident wrong
answers. The name-parse is kept **only as a control on the file-read**, and it is what makes "0
disagreements" a measurement rather than a convenience.

⚠ **A missing core file is UNKNOWN, never 0.** Defaulting a missing k to 1 would have manufactured
the very exclusion under test.

## Impossible here, named

- **whether a k=1 core could exist that ②∧③∧④ admits** — requires constructing one.
- **half B's status as anything but a caveat** — it is a derivation; no measurement changes it.
- **the 3-to-8 bound itself** — R373's job, not re-derived here.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
