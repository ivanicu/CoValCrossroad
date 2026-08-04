# R439 · ④ is not a reparameterisation of ② — its bar sits **below every one of 1,820 subsets**

**The decision this round makes safe:** whether adopting ④ as a fourth conjunct double-counts a
single axis. **It does not.** `W-DIFFERENT-KIND`.

## ⛔ First: the announced joint census was forced

R438 closed with *"run a joint census: which of ②/③/④ admits each arm."* Both cells are arithmetic:

- **home** — R436 measured ④ excluding **0 of 56** at J, so ④ admits all ⇒ conjunction = **② ∩ ③**
- **second** — R434 measured ② admitting **0 of 7**, so the conjunction is **empty** whatever ③ and ④ do

**Eighth announced step checked, sixth killed.**

## The question that is not forced

> *"A reparameterisation is not a measurement — regress the candidate on what is **published**; no
> residual = an identity, however meaningful it sounds."*

Clause ②'s reference is a size-4 subset of a 16-item generic pool; the published choice is
`POOL[0:4]`, picked by **file order**. **If ④'s bar sits inside the distribution ②'s reference is
drawn from, ④ is a weaker setting of ②'s existing knob — one clause with a dial, not two clauses.**

## Result — a **census** of the reference class, not a sample

All **C(16,4) = 1,820** subsets, on 968 prompts:

| | A2 |
|---|---|
| min | **0.5199** |
| 5th pct | 0.5286 |
| median | 0.5433 |
| 95th pct | 0.5549 |
| max | 0.5618 |
| sd | 0.00803 |
| **④'s bar (`min_ttr`)** | **0.4512 → percentile 0.00** |

**④'s bar is 0.0687 below the *weakest* subset in ②'s entire reference class.** No admissible
setting of ②'s knob reaches it, so ④ is not reachable by turning that knob.

⭐ **And a random-scoring rule lands at 0.4351** — so at home the best criterion-free rule is barely
above a random scorer and far below every criterion subset. **Criteria genuinely work on the home
release**, which is the same fact R437 read off the bar inversion, arrived at independently.

## Controls

| control | returned |
|---|---|
| POSITIVE — the human's own ranking | A2 **0.7238**, percentile **100.0** ✅ |
| g=0 — a pool subset against its own distribution | **0.549185 vs 0.549185**, exact ✅ |
| NEGATIVE — a random-scoring rule; distribution spread | 0.4351 at pct 0.0; **sd 0.00803 > 0** ✅ |
| **PLACEBO — the published reference `POOL[0:4]`** | A2 0.5537, **percentile 91.7** vs R331's published **93.7** ✅ |

⚠ **The placebo is the load-bearing control and it is not exact.** 91.7 against a published 93.7 —
a 2-point difference, inside my ±8 tolerance but real, and attributable to a different
annotator-draw seeding. It ties this round's scale to the record; **it does not certify the scales
are identical**, and a tolerance that loose would not have caught a modest scale error.

## What this settles, and what it does not

- **Settles:** ②'s knob cannot reach ④'s bar. Adopting ④ is not double-counting one dimension.
- **Does not settle:** whether *equal* A2 would make two objects the same axis. That is a construct
  question neither release can answer. **The round proves the weaker and sufficient thing.**

## Impossible here, named

- **a criterion for when two objects are "the same axis"** — construct validity; no release provides it.
- **the supremum over criterion-free rules** — R435's 30-member family, restated.
- **generalising past k=4** — the pool sweep is size-4 by construction.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
