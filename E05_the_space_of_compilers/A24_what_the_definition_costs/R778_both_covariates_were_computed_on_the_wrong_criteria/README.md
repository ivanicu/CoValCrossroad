# R778 · two rounds of "arm-free covariates" measured criteria no arm uses

**The 16-criterion "pool" is **prompt-blind** — one identical set for all 968 prompts — and **no arm
draws from it**: `random_k4_s0` uses **3,869** distinct criteria with **zero** pool overlap, while
**968/968** of its sets are subsets of the prompt's own **rubric** (median 15, range 4–39).
⇒ **R776's `poolspread` and R777's `orderdisagree` were computed on a criterion set disjoint from
every arm's, so both nulls were guaranteed by construction and are retracted as evidence.**
⭐⭐ Recomputed on the right object, R777's statistic reaches **≥0.30 on 4 of 4** random families
(**0.3206–0.3649**) against **0.0699–0.0994** on the pool — a **3.7×** gain from changing nothing but
which criteria it reads. **WORLD B — right hypothesis, wrong object.**

## check #380 — at the object, before any design

| | |
|---|---|
| distinct pool sets across 968 prompts | **1** *(prompt-blind)* |
| `random_k4_s0` criteria ⊂ the pool | **0 / 968** |
| `topw_k4` criteria ⊂ the pool | **0 / 968** |
| `random_k4_s0` criteria ⊂ the **rubric** | **968 / 968** |
| distinct criteria `random_k4_s0` uses | **3,869** — against the pool's **16** |

**This is §4's unit rule exactly**: the instrument's unit was *the generic pool's criteria*, the
claim's unit was *the arms' criteria*, and the two sets share **nothing** *(ledger 1116)*.

## ⭐⭐ E1/E2 — the same statistics, on the criteria the arms actually use

| family | random? | `n_rubric` | **`rubricdisagree`** | `rubricspread` |
|---|---|---|---|---|
| `Ra_random_s0` | RND | +0.1052 | **+0.3206** | +0.1041 |
| `Rb_random_s1` | RND | +0.1549 | **+0.3393** | +0.0653 |
| `Rc_random_s2` | RND | +0.1119 | **+0.3588** | +0.0977 |
| `M_mixed_sel` | RND | +0.1289 | **+0.3649** | +0.0742 |
| `F1_committed` | — | −0.0181 | +0.2742 | −0.0911 |
| `F3_target` | — | −0.0552 | +0.1689 | −0.0612 |
| | | **0/4 ≥ 0.30** | **4/4 ≥ 0.30** | **0/4 ≥ 0.30** |

**R777's hypothesis was right and its object was wrong** — the pool version gave 0.07–0.10, the rubric
version 0.32–0.36. **R776's was wrong in both**: `rubricspread` is still dead, 6/6 below 0.15
*(ledger 1117)*.

Partials on the difficulty axis barely move anything (corr(`n_rubric`, a baseline arm's A2) =
**−0.0190**), so difficulty is not the story.

## ⛔ D2's *forced* prediction had the sign backwards, and the control caught it

D2, written before the run: *"two k-subset draws from an n-criterion rubric overlap in expectation
k²/n, so their difference shrinks as n falls … **a NEGATIVE correlation between `n_rubric` and |d| is
therefore partly forced**."* **If |d| shrinks as n falls, |d| grows with n — the forced sign is
POSITIVE.** My mechanism and my stated sign contradicted each other in the same sentence. The
synthetic control settles it: **+0.0379 → +0.1273 → +0.3109** as size-spread rises, and **UNDEFINED**
at fixed size *(ledger 1118)*.

And the real families show **+0.105 to +0.155**, **0 of 4** reaching 0.30 — so **draw geometry
(World A) is not the mechanism** even with the sign corrected.

## ⛔ D3 · the degenerate prompts, counted

| k | prompts with `n_rubric ≤ k` — the draw is the whole rubric and \|d\| = 0 by construction |
|---|---|
| 4 | **3** |
| 6 | **18** |
| 8 | **80** |
| **12** | **302** — **31% of the population** |

**`random_k12` is degenerate on nearly a third of prompts**, which is R772's 223 ties seen from the
construction side rather than the score side, and a scope fact the k-sweep family carried unstated.

## ⛔ E3 · and the co-movement is still mostly unexplained

| pair | raw | holding `rubricdisagree` fixed | drop |
|---|---|---|---|
| `Ra` × `M` | +0.6017 | +0.5496 | **8.7%** |
| `Rb` × `M` | +0.5917 | +0.5342 | **9.7%** |
| `Rc` × `M` | +0.5895 | +0.5276 | **10.5%** |

**Mean drop 9.6%** — real, and 20× what the pool version managed (0.6%), but **90% of the 0.59
co-movement survives**.

## controls — 5 PASS

| control | returned |
|---|---|
| **OBJECT** | the arms' sets are subsets of the rubric on **968/968** and share **0** criteria with the pool; exits 2 otherwise — the whole round rests on which set the arms use |
| **POSITIVE** | synthetic uniform k-subsets: size-spread 0.25 → +0.0379 *(not detected)* · 0.50 → **+0.1273** · 1.00 → **+0.3109**, monotone |
| **g=0** | fixed rubric size → **UNDEFINED**, printed as undefined rather than a small number |
| **NEGATIVE** | 200 permutations of `n_rubric` → **−0.0003 [−0.0552, +0.0667]** |
| **SHAM** | a random draw from `n_rubric`'s own distribution → **+0.0010 [−0.0619, +0.0549]** |
| **PLACEBO** | a family against itself → **1.000000** |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| R776's *"value spread does not explain it"* | ⛔ **retracted as evidence** — computed on criteria no arm uses. Recomputed on the rubric it is **still** dead (6/6 < 0.15), so the conclusion survives its own retraction, by accident |
| R777's *"ordering disagreement is not the axis"* | ⛔ **retracted and reversed** — on the right criteria it reaches **0.32–0.36** for **4/4** random families |
| R777's *"the mechanism is 6.5× absent from the data"* | ⛔ **explained**: the mechanism was measured on the wrong criterion set. On the arms' own criteria the gap closes to ~2× |
| D2's draw-geometry story | **sign corrected and refuted anyway** — `n_rubric` reaches 0.30 for 0 of 4 |
| the 0.59 co-movement | **9.6% explained**, 90% still open |

## the sentence I can no longer write

*"the pool's criteria tell us something about how the arms differ."* The arms and the pool share
**zero** criteria, and the pool is one prompt-blind set of 16 against the arms' 3,869.

## NEXT

`rubricdisagree` explains **9.6%** of the co-movement and reaches 0.32–0.36 on the random families —
real, and an order of magnitude short of the 0.59 it is meant to account for. The obvious remaining
structure is one the composition table already exposes and no round has used: **two `random_k` arms on
the same prompt draw from the *same* rubric, so their criterion sets OVERLAP**, and that overlap is
computable per prompt per pair from the committed core JSONs — `|A ∩ B| / |A ∪ B|`. ⚠ D2's arithmetic
says the expected overlap is `k²/n`, which the round just showed is **not** what drives |d| through
`n_rubric` alone; but the *realised* overlap is a different variable from its expectation, and it is
the one each pair's difference actually sees. The registered quantity is the per-prompt realised
Jaccard overlap between two arms' criterion sets, against their |d|, per family — because if that is
what the scale measures, then the whole co-movement thread is arms sharing criteria, and no prompt
property is required to account for it.
