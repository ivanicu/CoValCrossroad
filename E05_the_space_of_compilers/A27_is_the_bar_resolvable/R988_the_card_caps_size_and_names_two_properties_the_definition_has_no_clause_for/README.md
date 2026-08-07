# R988 · the card caps size, and names two properties the definition has no clause for

**THE DECISION THIS MAKES SAFE.** Whether SIZE is the right property for clause ①. **Not as a lower
bound** — the release's own card sets an **upper** one, and the definition admits **4 objects the
card's construction could not produce**.

---

## ⛔ First, a prior-art failure of mine, two rounds old

R986's headline was *"`coval_core`'s per-prompt size runs 2 to 4."* `data/DATASET_CARD.md` says it:

> *"Most prompts end up with four core rubric items (**about 95%**), with the remainder having **two
> or three**."*

**So that claim is a VERIFICATION that the object does what it says, not a finding.** §4's own rule
applies — `prior_art` non-empty ⇒ verification — and R986's framing is **downgraded here** rather
than left standing. ⚠ I found it by reading the card *in this round*, which is the round the card
should have been read in.

**What survives from R986** is the part the card does not contain: the decomposition across 96 arms
into **pool capping** (a prompt property, 28 arms, every `k12`/`k8`/`k6` family byte-identical) versus
**arm selection** (6 arms).

## And reading the card answers R987's open question

> *"we keep only a small set of highly rated, **non-redundant**, and **non-conflicting** rubric
> items … it aims to select **up to four** … that remain compatible with each other and do not repeat
> the same idea."*

All four quotes were verified against the file before anything was computed.

| the card | the definition |
|---|---|
| size: **up to four** — an **upper** bound | clause ①: **greater than one** — a **lower** bound |
| **non-redundant** | *no clause* |
| **non-conflicting** | *no clause* |

**They constrain opposite ends of the same quantity.**

## The measurement

| | |
|---|---|
| prompt-pool arms | 96 |
| above the card's cap of 4 | 28 |
| **admitted by clause ② AND above the cap** | **4** |

`greedy_k8_fit1` (8) · `indep_k8_fit1` (8) · `topw_k6` (6) · `topw_k8` (8)

**Four objects the definition calls cores that the release's own construction could not produce.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | the operator also admits **20 of 68** arms at or below the cap — so the comparison measures the **cap**, not the operator |
| **NEGATIVE** | `random_k4_s0` (margin −0.0587) is not admitted |
| **PLACEBO** | `generic` against itself: `lo = 0.0`, never admitted |
| **CARD QUOTES** | all four verified present in `DATASET_CARD.md` before computing — a quote that did not verify would have exited 2 |

Seeds: 3, unanimity required.

## ⚠ What is NOT measured, and what it would require

**Non-redundancy and non-conflict.** Their **absence from the definition is established by reading**;
their **consequence is not measured**. Doing so needs criterion **text** plus a semantic-similarity
and weight-compatibility instrument — a different instrument and a different round. Named here with
what it would take, not marked "planned".

## What this does not say

**It does not say the definition is wrong to depart from the card.** The card itself calls core *"a
proof of concept … an invitation for others to develop and validate better synthesis and aggregation
methods for this format."* A definition that departs deliberately is doing what was invited.

⭐ **But the departure is currently not stated anywhere** — and a definition that silently inverts the
direction of its source's own size criterion is not departing deliberately, it is departing by
omission.

## Alternatives considered

**Add an upper bound to clause ① and re-run.** Refused in this round: it would change the extension
by fiat in the same breath as discovering the gap, and R987 established that reading choices should
be made deliberately rather than folded into a measurement.

**Report the 28 over-cap arms as the finding.** Refused: 24 of them fail clause ② anyway, so the
number that matters is the 4 that survive both. Reporting 28 would inflate a gap the operator mostly
closes on its own.
