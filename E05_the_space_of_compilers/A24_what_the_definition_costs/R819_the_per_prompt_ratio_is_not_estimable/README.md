# R819 · R818's per-prompt statistic was one estimator with 6× the noise — its reordering is retracted

`run.py` · `PREREGISTRATION.txt` · `results/estimator_family.json` · 968 prompts, 920 with a defined
ratio × 9 arms × 7 estimators · **WORLD C** · two hash seeds byte-identical, md5
`574e0639422046ebc82607161a358494`

## THE DECISION THIS MAKES SAFE

**R818 returned WORLD C on a reordering (Spearman +0.9833) and reported "four arms fall below the
constant floor". Both appear under the naive mean alone.**

| estimator | Spearman vs corpus-level | arms below the floor | half-split sd |
|---|---:|---:|---:|
| **naive** (R818's) | **+0.9833** | **4** | **0.0693** |
| trim5 | **+1.0000** | 2 | — |
| trim10 | **+1.0000** | 1 | 0.0151 |
| trim20 | **+1.0000** | 0 | — |
| median | **+1.0000** | 0 | 0.0167 |
| winsor | +0.9833 | 3 | — |
| **weighted** ( = corpus-level, by identity) | **+1.0000** | **0** | **0.0110** |

**The reordering survives under exactly the two fattest-tailed members**, and the naive estimator
carries **6.3× the half-split noise** of the weighted one.

## ⛔ CHECK #421 KILLED R818's NEXT ON ARITHMETIC BEFORE ANY REGRESSION

R818's NEXT proposed regressing each arm's margin on the span, to test proportionality. **[D2] If
`margin_p = c · span_p` exactly, every member of the family returns c — proportionality produces
AGREEMENT, not the divergence observed.** The NEXT asked a question whose affirmative answer would
explain the opposite of what R818 saw.

The real cause is the denominator: span mean **0.2368**, median **0.2131**, with **12.8% of prompts
below 0.05** and **24.5% below 0.10**. The ratio runs to **−29.00**. The smallest-span decile
averages **−3.105** against the other nine at **+0.414**, and **contributes −503.1% of the total
sum** — it flips the aggregate's sign on its own.

## ⭐ THE ESTIMATOR FAMILY

| arm | naive | trim10 | median | **weighted** |
|---|---:|---:|---:|---:|
| `oracle_k4_fit1` | 0.4282 | 0.6276 | 0.8000 | **0.7082** |
| `greedy_k4_fit1` | 0.4215 | 0.6077 | 0.7829 | 0.6922 |
| `indep_k4_fit1` | 0.2778 | 0.5376 | 0.7308 | 0.6288 |
| **`coval_core`** | **0.0617** | 0.4136 | 0.5965 | **0.5162** |
| `topw_k4` | 0.0609 | 0.3850 | 0.5714 | 0.5033 |
| `genericpool16` | **−0.1118** | 0.2737 | 0.4721 | 0.4220 |
| `full` | **−0.4221** | 0.1377 | 0.3062 | 0.2835 |
| `gen_sham` | **−0.5398** | −0.0200 | 0.1476 | 0.1801 |
| `random_k4_s0` | **−0.5938** | 0.0398 | 0.2265 | 0.2162 |

⭐ **D1 holds exactly**: `weighted` = `Σmargin / Σspan` **is** the corpus-level ratio — max
\|difference\| **6.66e-16**. So the corpus-level number was always a member of this family, and the
**minimum-variance** one. That is a derivation, not a discovery, and it was written down first.

## ⚠ WORLD C, NOT A — THE ORDERING AGREES BUT THE LEVEL DOES NOT

The median-based ordering matches the corpus-level ordering at **Spearman 1.0000**, but `trim10`'s
`coval_core` of **0.4136** sits **outside** the corpus-level bootstrap CI **[0.4827, 0.5499]**. So:

- **retracted**: R818's reordering, and its claim that four arms fall below the constant floor.
- **not established**: that the per-prompt and corpus-level shares are the *same number*. A trimmed
  mean is a **different estimand**, not a better estimate of the same one, and the round says so
  rather than declaring agreement.

## ⛔⛔ THREE CONTROLS FAILED FIRST, ALL MINE, ALL §4 ENTRIES

**① D1's identity failed at 3.91e-02** — I computed `weighted` on the 920-prompt `keep` subset and
`corpus` on all 968 with a pooled floor. On the same population the identity is exact. **Two
populations compared as though they were two quantities.**

**② The separating dose was built in the one shape D2 had already forbidden.** It planted
`m = f·s` **exactly** — perfect proportionality — which D2 says collapses the family to a single
number. **A control that cannot separate, built after writing down that it cannot.** It also targeted
the **mean**, when what distinguishes these estimators is **variance**: `r = f + ε/s` is unbiased for
symmetric ε, so the naive mean stays put while its spread explodes. Repaired to a spread-based dose:

> at eps = 0.05 — naive **±0.0348** · trim10 **±0.0125** · median **±0.0098** · weighted **±0.0073**;
> at eps = 0, every spread is exactly **0.0000**.

**③ The negative control returned a point mass** — **+0.5162 [+0.5162, +0.5162]**, exactly the
observation. `weighted = Σm/Σs` is **permutation-invariant by construction**: reordering `m` cannot
change `Σm`. **The fifth degenerate null of this session** (R809, R810, R813, R816, R819). Repaired
by naming the invariant member and testing the six that can move:

| member | null | real |
|---|---|---|
| naive | +1.1439 ± 0.0848 | **+0.0617** |
| trim10 | +0.6734 ± 0.0251 | +0.4136 |
| median | +0.4670 ± 0.0169 | +0.5965 |

Every movable member's real value lies outside its own null spread.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R818's per-prompt `coval_core` **+0.0617** and `random_k4_s0` **−0.5938** reproduced exactly | PASS, else exit 2 |
| PLACEBO | the constant arm (margin identically 0) under every member: **0.0e+00** | PASS — exactly 0 everywhere |
| POSITIVE | a plant at f = 0 / 0.25 / 0.5 recovers f exactly under every member | PASS |
| separating dose | spreads at eps = 0.05 above, exactly 0 at eps = 0 | PASS **after repair** |
| NEGATIVE | six movable members, each real value outside its null | PASS **after repair** |
| NOISE FLOOR | 20 half-splits: naive **0.0693** · trim10 0.0151 · median 0.0167 · **weighted 0.0110** | measured |

## WHAT DIED

- **R818's E3 reordering and its WORLD C reasoning** — both rest on the naive mean alone.
- **"four arms fall below the constant floor"** — that count is 4 / 2 / 1 / 0 / 0 / 3 / 0 across the
  family, and **0 under the minimum-variance member**.
- **R818's NEXT** — killed by D2 before any regression.
- **three of my own controls.**

## WHAT SURVIVES — AND THIS ROUND ADDS

R818's corpus-level numbers, untouched and now known to be the **minimum-variance member** of the
family they were always part of. And a bound on the per-prompt statistic: with an eighth of prompts
under a span of 0.05, it is estimable only under trimming, and different trims give different levels.

## SCOPE

968 prompts, **920** carrying a defined ratio × 9 arms × 7 estimators · floor = the best constant
weak order, prompt-weighted · bootstrap over prompts NBOOT 1,200 · 200-draw permutation null · 20
half-splits · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a per-prompt ratio estimable without trimming | prompts whose span is bounded away from 0; **12.8% sit below 0.05** — measured, and it is why the naive mean has 6.3× the noise |
| testing `weighted` with a margin permutation | a statistic that is not `Σm/Σs`; it is permutation-invariant **by derivation**, so the control names it and excludes it rather than reporting a false pass |
| declaring the trimmed and corpus-level shares equal | they are different estimands; the family is reported and each claim names its member |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The per-prompt statistic is bounded rather than settled: the ordering is stable under every trimmed
member (Spearman 1.0000) while the level is not (trim10's 0.4136 outside the corpus CI [0.4827,
0.5499]). Computed by this round's `run.py`, the naive member carries a half-split sd of 0.0693
against the weighted member's 0.0110.

That ratio is the thread worth pulling, and not toward more estimators. **Five of this session's
negative controls have been degenerate** — R809's permuted both sides of a regression identically,
R810's permuted indices the selector had already re-indexed, R813's wrote to a name no closure read,
R816's left a shared term in both arms, R819's targeted a permutation-invariant statistic. Each was
caught by its output looking wrong rather than by a check. **The step is to write that check**: an
assurance gate running each round's declared null twice at different seeds, failing when the spread
is zero or the null's centre equals the observation. Four of those five would have been stopped
before the round shipped, and it needs no new measurement — only the discipline the other seven gates
already apply to the prose.
