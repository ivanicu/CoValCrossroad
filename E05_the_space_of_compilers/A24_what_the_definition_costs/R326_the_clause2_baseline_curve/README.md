# R326 — the clause-② baseline curve: `topw_k4`'s admission is baseline-dependent

**Decision this makes safe:** whether the two admissions hold across every legitimate clause-②
reference. **`coval_core` does. `topw_k4` does not — at the strongest one it sits at 0.92× its own
MDE.**

## ⛔ First: the obvious plot is the arithmetic trap

`gap = arm_A2 − ref_A2`, and the arm is fixed — so plotting the gap against the reference's own A2
plots a quantity against something it is *defined as a difference from*. **Verified to four decimals
at all six points.** The monotone decline is a **DERIVATION** and is labelled one.

What is *not* forced is where the ratio to each cell's **own MDE** crosses 1.0, because those MDEs
are measured per cell and vary independently (0.0099–0.0108).

## The curve — five distinct legitimate references, ordered by strength

| reference | ref A2 | legit | `coval_core` | `topw_k4` |
|---|---:|:--:|---|---|
| budget 0 · random draw | 0.5397 | yes | +0.0268 / 0.0100 = **2.69×** | — |
| neutral pool-16 | 0.5403 | yes | +0.0262 / 0.0099 = 2.63× | +0.0239 / 0.0100 = 2.39× |
| budget 1 · hand-picked | 0.5504 | yes | +0.0160 / 0.0106 = 1.51× | — |
| `generic` at matched k=4 | 0.5514 | yes | +0.0151 / 0.0107 = 1.41× | +0.0128 / 0.0108 = 1.19× |
| **best held-out of 1,820** | 0.5546 | **yes** | +0.0119 / 0.0101 = **1.18×** | +0.0096 / 0.0104 = **0.92× UNRESOLVED** |
| in-sample argmax | 0.5575 | **NO** | +0.0090 / 0.0104 = 0.87× | — *(negative control, carried not deleted)* |

## W-CROSSES

At the **strongest legitimate reference**, `topw_k4` falls **below its own MDE**. Its CI still
excludes zero and it still survives BH — **the same split R325 drew for clause ①, now landing on an
ADMITTED arm at the definition's strongest baseline.**

The page currently says *"both separable, both BH survivors"*. True, and **one of the two is below
its own resolution there.**

## Controls

| control | result |
|---|---|
| **positive** — the weakest legitimate reference must give the largest ratio | it does, at both arms |
| **knob** — the curve must not be flat | spread 1.76× |
| **negative** — the disqualified in-sample argmax carried, not deleted | present, `coval_core` 0.87× |
| **placebo / derivation check** — gap ≡ arm − ref to 4 dp | exact at all six points |

## ⚠ The kill missed it once, and the reason is structural

R287 and R286 both report the held-out best of 1,820 at A2 0.5546 — **one carries `coval_core`, the
other carries both arms.** Selecting the strongest by `max(ref_a2)` picked the row holding only
`coval_core`, found nothing unresolved, and printed **W-STABLE**.

**The verdict was computed over a population that did not contain the case.** Fifth instance this
session; the fix is again to make the population explicit in code — duplicate references are now
merged before the kill.

## Scope

968 prompts · 15,593 annotations · Qwen3.5-2B-Base · A2·annotator, clause ② · references as
published by R286, R287, R307, R308. This round **reads** their committed cells and adds no estimate.

## What this site cannot do

Provide a legitimate reference stronger than the held-out best of 1,820. The in-sample argmax is
stronger and is **not legitimate**; anything beyond needs a larger candidate pool — a generation
cost, not a release limit.
