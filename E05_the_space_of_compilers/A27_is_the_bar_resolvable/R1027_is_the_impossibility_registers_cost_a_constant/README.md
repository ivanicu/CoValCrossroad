# R1027 — `15,488 judge calls` decides what this arc calls impossible. It had never been re-derived.

**The decision this round makes safe:** what a new comparator actually costs. It is **not a constant**
— it is `prompts × replies × k`, and the register quoted one arm's price as universal.

## The wall never checked

The figure appears in `DEFINITION.md` twice and in four rounds' impossibility registers, always as a
**constant**. Nobody re-derived it. That is the *"wall never checked"* shape: a permanent limit
asserted from a citation, while the falsifying arithmetic sits in the committed files.

## ⛔ The derivation, from the source, before any counting

`covalx/judge.py:151` — `build_prompt(criterion: str, reply: str, ...)`. **One call scores one
(criterion, reply) pair**, so cost = `prompts × replies × k` and is **linear in k**. Forced by the
signature. What is *measured* is `replies`, each arm's `k`, and therefore **which arm the quoted
number describes**.

⚠ **I almost adopted the wrong reading from my own repo.** `STATEMENT.md:2085` says *"the pool's
15,488 instances are 16 criteria seen 968 times"* — which reads as 968 × 16 and would make the figure
a **sixteen**-criterion pool's cost. `968 × 16 = 15,488` is arithmetically true, so the sentence is
self-consistent and wrong for this purpose: it describes a criterion-instance pool, not an arm's judge
cost. **A number that factorises two ways is a number to check, not to quote.**

## Result — **World B.** The wall scales with k.

`cells == prompts × replies × k` holds with residual **exactly 0** for **all 74** fixed-k arms.
`replies = 4`, inferred from `generic` and then *required* of every other arm.

| k | judge calls at full coverage (968 × 4) | |
|---:|---:|---|
| **1** | **3,872** | ← **4× cheaper than quoted** |
| 2 | 7,744 | |
| 3 | 11,616 | |
| **4** | **15,488** | ← **the quoted figure** |
| **16** | **61,952** | ← **`genericpool16`, already a certified comparator — 4× MORE** |

⚠ Plus one partial-coverage cell, which is the **second** factor: `398 prompts × k=4 = 6,368`.

**So the register is wrong in both directions**: it overstates the cost of the small-k comparators
most likely to be tried, and understates by 4× the cost of a comparator the certified set **already
contains**.

## ⚠ And the register mis-states the currency as well as the amount

The judge loads with `device_map="cuda"` at batch 32. **The unit is local GPU time, not paid API
spend.** This round does **not** run it and claims **no** runtime; what that would require is one
timed batch.

## Controls

- **POSITIVE** — the identity must hold with residual **exactly 0** (not "small") across all 74
  fixed-k arms: **PASS, 0 violations**. It could have failed: a batched judge, a cached criterion, or
  a per-prompt reply count would each break it.
- **NEGATIVE** — an arm whose `k` **varies** per prompt must **not** satisfy the identity for any
  single integer k, or the identity is reading file size rather than k: `coval_core_sham` **3.9545**,
  `full` **15.4793**, `gen` **3.9959** — all non-integer as required: **PASS**.
- **NOISE FLOOR / SEEDS** — **N/A**, these are exact counts, not estimates. Stated rather than omitted.

## ⚠ My own table was wrong first

The first version collapsed `(k, cost)` across arms with **different prompt counts** and printed
**two** k=4 rows — 6,368 and 15,488 — attaching *"THE QUOTED FIGURE"* to one arbitrarily. `6,368 =
398 × 4 × 4` is a partial-coverage arm. **Cost depends on both factors, and a table that hides one of
them is a verdict string wearing a table's clothes.**

## What does NOT change

**R1026's finding stands.** A cheaper comparator still has to be **built** and be **prompt-blind**,
and no such arm exists in this release. **The cost was never the only obstacle — it was the one the
register named, and it named it wrongly.**

`run.py` · `results/cost_by_k.json`
