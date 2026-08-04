# R447 · "② is emptied by a change of judge" is **false as stated** — and the arm ordering inverts

**The decision this round makes safe:** whether the definition's judge index rests on a fact about
the judge or about one arbitrary reference. **About the reference** — `W-REFERENCE`.

## ⛔ The announced step was forced

R446 closed with *"re-run the whole chain at 0.8B."* R301 already commits that ② admits **0 arms**
there, so the conjunction is empty by arithmetic. *Fifteenth announced step, eighth killed.*

**But R301's "0" is measured at `POOL[0:4]`** — the draw R331 showed was chosen by **file order** —
and R446 measured a point-vs-resolved gap of **25.8 points** at the other judge.

## Result — all 1,820 references, judged by 0.8B, 968 prompts

| arm | A2@0.8B | **SHARE@0.8B** | SHARE@2B | quantile@0.8B |
|---|---|---|---|---|
| **`gen`** | 0.4743 | **0.2560** | **0.0038** | 0.7929 |
| **`coval_core`** | 0.4712 | **0.1187** | **0.9841** | 0.6984 |
| `gen_sham` | 0.4362 | 0.0000 | 0.0000 | 0.0000 |
| *ORACLE (control)* | 0.7238 | **1.0000** | 1.0000 | 1.0000 |

> **② is not emptied at 0.8B.** It admits `coval_core` under **11.9%** of its own reference class and
> `gen` under **25.6%**. R301's `0` was one reference, and that reference is unrepresentative of its
> class at this judge.

## ⭐ And the ordering **inverts**

| | `coval_core` | `gen` |
|---|---|---|
| **@2B** | **98.41%** | 0.38% |
| **@0.8B** | 11.87% | **25.60%** |

**At 2B the definition admits the released core and rejects the generated one. At 0.8B, by admitted
share, the generated core does better.** That is a stronger statement than "the judge matters": it
says the definition's *ranking* of its two candidate members is judge-dependent, not just its
threshold.

## Controls — and the positive one is what makes this readable

| control | returned |
|---|---|
| **POSITIVE — an oracle ordering at 0.8B** | admitted under **1820/1820** ✅ |
| g=0 — a 0.8B reference against itself | **0.0e+00**, admitted **False** ✅ |
| NEGATIVE — `gen_sham` ≤ `gen` | **0.0000 ≤ 0.2560** ✅ |
| PLACEBO — same prompt-keyed rng as R446 | the two sweeps differ **only in the judge** |

**Without the oracle control, a low share at 0.8B would be silence** — and R301's `0` would be
unreadable for exactly that reason. The oracle clears every reference, so these shares are
measurements.

⚠ **Shares are comparable across judges; A2 levels are not.** Each share is a share of *that judge's
own* reference class. The two judges induce different satisfaction distributions and share no scale,
so `0.4743` and `0.5374` are not on one axis and are never compared here.

## What this changes, and what it does not

- **Changes:** *"It is emptied by a change of judge: 5 arms admitted at 2B, 0 at 0.8B"* is false as a
  statement about the **judge**. It is true about **`POOL[0:4]` at 0.8B**.
- **Does not change:** that the judge matters. It matters *more* than stated — it reorders the
  candidates, which no threshold story predicts.
- **Does not establish:** which judge is right. ⚠ *Two judges can refute a rule and never establish
  one* — this document's own words.

## Impossible here, named

- **comparing A2 levels across judges** — no common scale.
- **a third judge** — no third set of satisfaction files exists.
- **construct validity of A2** — the release's own human rankings.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
