# R815 · a second human construct was on disk all along, and the ordering is identical under it

`run.py` · `PREREGISTRATION.txt` · `results/second_construct.json` · 293 prompts carrying both
blocks × 9 arms × 2 targets · **WORLD A** · two hash seeds byte-identical, md5
`6502c5a0b57d91eac92ef04efe0a4232`

## THE DECISION THIS MAKES SAFE

**Every A2 this campaign has published is against one of three human questions the release ships.
Asked the other one, the arms come out in exactly the same order.**

| | |
|---|---|
| Spearman between the two orderings | **1.0000** |
| Kendall τ | **1.0000** |
| concordant pairs | **36 / 36** |
| committed margins flipping sign | **0 of 4** |
| MDE at n=293 | **0.0173**, below the smallest margin tested (0.0256) |

## ⛔ CHECK #417 · R814's PREMISE WAS FALSE, AND THE THING BEHIND IT WAS BIGGER

R814 closed by calling the next step a **writing decision**, because the release "ships one judgement
per (annotator, prompt) pair" so the interaction is unidentifiable.

1. **There are 111 repeated (prompt, annotator) pairs.** The interaction is partially identified. The
   NEXT stated a flat fact that was not one.
2. ⭐ **`ranking_blocks` has three keys, not one**: `world` (18,384 rankings), `personal` (4,901),
   `unacceptable` (4,901). **This arc has scored against `world` alone, for its entire length.**
   Where the same annotator answered both on the same prompt, the rankings **differ in 2,374 of
   4,901 cases — 48.4%.**

Multiple rounds listed construct validity as needing "an external gold standard" and therefore
impossible. It is not external — but it is **a second question put to the same people about the same
responses**, and no round had used it.

## ⭐ E1/E2 · EVERY ARM ON BOTH TARGETS

| arm | world (968) | world (293) | **personal** | world − personal |
|---|---:|---:|---:|---|
| `oracle_k4_fit1` | 0.6142 | 0.5880 | **0.5939** | −0.0059 [−0.0121, +0.0003] |
| `greedy_k4_fit1` | 0.6106 | 0.5815 | 0.5869 | −0.0054 [−0.0113, +0.0008] |
| `indep_k4_fit1` | 0.5941 | 0.5706 | 0.5814 | −0.0108 [−0.0171, −0.0046] |
| `topw_k4` | 0.5642 | 0.5628 | 0.5719 | −0.0092 [−0.0154, −0.0035] |
| `coval_core` | 0.5665 | 0.5587 | **0.5707** | −0.0119 [−0.0182, −0.0059] |
| `genericpool16` | 0.5422 | 0.5331 | 0.5425 | −0.0094 [−0.0156, −0.0034] |
| `random_k4_s0` | 0.4927 | 0.4910 | 0.5009 | −0.0098 [−0.0162, −0.0040] |
| `full` | 0.5087 | 0.4876 | 0.4974 | −0.0099 [−0.0161, −0.0040] |
| `gen_sham` | 0.4828 | 0.4766 | 0.4871 | −0.0105 [−0.0164, −0.0048] |

⭐ **The shift is uniform and small: every arm scores HIGHER against `personal`, by 0.005–0.012.**
That is a level shift in the target, not a reordering — and it is exactly why the ordering survives.
**BH: 7 of 9 differences survive**; the two that do not are the two oracle-family arms.

## ⭐ E3/E4 · THE ORDERING AND THE COMMITTED MARGINS

> **world**: `oracle_k4_fit1` > `greedy_k4_fit1` > `indep_k4_fit1` > `topw_k4` > `coval_core` >
> `genericpool16` > `random_k4_s0` > `full` > `gen_sham`
> **personal**: **identical, position for position.**

| committed margin | world | personal | |
|---|---|---|---|
| R805 fitted − blind pool | +0.0549 [+0.0413, +0.0701] | +0.0514 [+0.0369, +0.0663] | same sign |
| R805 released core − blind pool | +0.0256 [+0.0136, +0.0386] | +0.0282 [+0.0157, +0.0410] | same sign |
| R811 rule effect (k=4) | +0.0717 [+0.0579, +0.0871] | +0.0711 [+0.0561, +0.0862] | same sign |
| the sham gap | +0.0822 [+0.0645, +0.1017] | +0.0836 [+0.0657, +0.1032] | same sign |

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `coval_core` on `world` over all 968: **0.5664774812** vs committed **0.5664774812** | PASS, else exit 2 |
| PLACEBO | an arm minus itself on either target: **0.0e+00** | PASS — exactly 0 |
| POSITIVE | an arm built **from `personal`'s modal class** scores **0.6555** on `personal`, above the best real arm's **0.5939** | PASS |
| g=0 | the **same construction from `world`** scores **0.6366** on `personal` — lower than 0.6555 | PASS — the control can fail |
| NEGATIVE | block labels shuffled within each assessment, 200 draws: null **+0.0002 [−0.0056, +0.0053]** against a real **−0.0119** | PASS |
| NOISE FLOOR | 20 half-splits of the 293 prompts: sd **0.0032** | measured |
| MDE | **0.0173** at n=293 vs smallest margin **0.0256** — **not underpowered**, and computed before any null was read | stated first |

⚠ **A display defect, fixed and recorded**: the E1 header first read "321 prompts". **321** is the
count with ≥1 annotator in each block; the population requires **≥2 in each** and is **293**. The
label was stale, the computation was not — `BOTH` was built with ≥2 throughout, and the printed n
in the MDE line was always 293.

## WHAT DIED

- **R814's premise** — 111 repeated (prompt, annotator) pairs exist, so the interaction is not
  wholly unidentifiable, and the release ships more than one judgement per pair in that sense.
- **"construct validity is impossible on this site"** — as an unqualified claim. It needs no external
  gold standard to ask whether a second question reorders the arms.
- **the worry this round was built for** — that every published number is scoped to `world`. It is,
  and it survives the other target unchanged.

## WHAT SURVIVES — AND THIS ROUND ADDS

The arc's entire ordering and all four load-bearing margins, now **construct-robust across the one
second construct the release offers**. And a fact about the annotators worth keeping: asked "how
should the world rank these" and "how do you personally rank these", the same person gives a
different answer **48.4%** of the time — yet that disagreement does not reorder a single arm.

## SCOPE

293 prompts carrying **both** blocks with ≥2 annotators each (of 1,078 in the release; 968 usable on
`world`) × 9 arms × 2 targets · paired bootstrap over prompts, NBOOT 1,200 · ⚠ these 293 are **not a
random third** — they are where the second question was asked, which is why the `world` column is
given on both populations · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| the `unacceptable` block as a third target | it records **ratings**, not a ranking (`"C is unacceptable"`), so `cls()` cannot consume it — **checked** against the raw record |
| construct validity against an EXTERNAL standard | a gold standard outside the release; this round tests invariance across two internal questions, which is weaker and is labelled as such |
| the same test at n=968 | the second question was asked on 321 prompts and answered twice on 293 — **checked**, and the MDE is reported rather than the shortfall being hidden |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The ordering is target-invariant at Spearman 1.0000 and no committed margin flips, so the arc's
numbers survive the one construct swap available. Computed by this round's `run.py`, the shift is
uniform: the nine arms each score 0.005–0.012 higher against `personal`, `coval_core` moving
0.5587 → 0.5707 and `gen_sham` 0.4766 → 0.4871.

That uniformity is the open thread. A target which nine unrelated predictors all find easier is a
target with **less spread among its own annotators**, and the release lets that be checked directly:
compute `CEIL_H` on the `personal` block and compare it against the **0.551880** this arc has
committed for `world`. If `personal` carries a higher inter-annotator ceiling, the whole shift is
target reliability and no property of any arm is involved; if it does not, the shift needs another
account. One recomputation, on data this round already loads.
