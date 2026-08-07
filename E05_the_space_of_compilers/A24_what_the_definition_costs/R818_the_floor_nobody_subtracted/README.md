# R818 · a fixed ordering already reaches 65% of the ceiling — the released core captures half of what is left

`run.py` · `PREREGISTRATION.txt` · `results/floor_subtracted.json` · 968 prompts × 9 arms × 75 weak
orders · **WORLD C** · two hash seeds byte-identical, md5
`66ace1b805a68e80ca1ca355ac07d6e8`

## THE DECISION THIS MAKES SAFE

**Every "fraction of attainable" this arc has quoted sits on a scale whose floor is 0.65, not 0.**

> a single fixed ordering, identical on every prompt, scores **0.449421** — **65.1%** of the
> attainable **0.686265**.

| arm | raw | ÷ attainable | **share of the INFORMATIVE range** |
|---|---:|---:|---|
| `oracle_k4_fit1` | 0.6142 | 0.8949 | **+0.6991 [+0.6715, +0.7255]** |
| `greedy_k4_fit1` | 0.6106 | 0.8898 | +0.6844 [+0.6574, +0.7121] |
| `indep_k4_fit1` | 0.5941 | 0.8656 | +0.6152 [+0.5853, +0.6445] |
| **`coval_core`** | 0.5665 | **0.8255** | **+0.5001 [+0.4631, +0.5331]** |
| `topw_k4` | 0.5642 | 0.8221 | +0.4905 [+0.4530, +0.5246] |
| `genericpool16` | 0.5422 | 0.7901 | +0.3990 [+0.3596, +0.4338] |
| `full` | 0.5087 | 0.7413 | +0.2591 [+0.2165, +0.2985] |
| `random_k4_s0` | 0.4927 | 0.7179 | +0.1922 [+0.1485, +0.2329] |
| `gen_sham` | 0.4828 | 0.7035 | **+0.1509 [+0.1071, +0.1950]** |

**`coval_core` reads 0.8255 of attainable and 0.5001 of the informative range.** R817's 0.8132 and
this round's 0.8255 are the same statement on a scale that starts at zero; on the scale that starts
at what a constant order already achieves, the released core captures **half**.

## ⛔ CHECK #420 · R804 HAD THIS NUMBER FOR FOURTEEN ROUNDS AND LEFT IT IN A PARENTHESIS

`R804/run.py:197` computes the best constant weak order and prints it **inside a negative control's
parenthetical**: *"(best single constant weak order corpus-wide 0.451773)"*. No round used it.
R817's NEXT proposed computing it afresh.

## ⛔⛔ AND THE OBJECT CHECK CAUGHT A UNIT INCONSISTENCY INSIDE THAT SAME LINE

R804's `BESTC` **concatenates all annotator rows across all prompts** and means over the pool —
**annotator-weighted**. Its `CEIL_ATT` takes a per-prompt max and means over prompts —
**prompt-weighted**. They were printed side by side as if on one scale.

| | |
|---|---:|
| R804's annotator-weighted floor (reproduced exactly) | **0.451773** |
| the **prompt-weighted** floor — the scale every A2 in this arc uses | **0.449421** |
| difference | **−0.002352** |

Small, and it propagates: my own CHECK #420 quoted `0.451773 / 0.686265 = 65.8%` — mixing the two
weightings. Prompt-weighted throughout, it is **65.1%**.

## ⚠⚠ WHAT IS A DERIVATION HERE, STATED BEFORE THE RUN

**The corpus-level rescaling is affine** — subtract a constant, divide by a constant — so it
**cannot reorder the arms**. D1 said so first, which is what stops "the ordering survived" being
reported as a result. Only the shares are measurements, and only E3 can come out otherwise.

⭐ **And D2 was written before the run too**: the held-out floor is ≤ the in-sample one, so the
correction runs **against** the arms. Measured: held-out **0.446628 ± 0.006628**, in-sample
**0.449421**, optimism **0.002792** — small, because a choice among 75 options over 968 prompts
barely overfits.

## ⭐ E3 · THE PER-PROMPT VERSION REORDERS, AND FOUR ARMS GO NEGATIVE

| arm | corpus-level | per-prompt |
|---|---:|---:|
| `oracle_k4_fit1` | 0.6991 | 0.4282 |
| `greedy_k4_fit1` | 0.6844 | 0.4215 |
| `indep_k4_fit1` | 0.6152 | 0.2778 |
| `coval_core` | 0.5001 | **0.0617** |
| `topw_k4` | 0.4905 | 0.0609 |
| `genericpool16` | 0.3990 | **−0.1118** |
| `full` | 0.2591 | **−0.4221** |
| `gen_sham` | 0.1509 | **−0.5398** |
| `random_k4_s0` | 0.1922 | **−0.5938** |

**Spearman +0.9833** — one swap, at the bottom: `gen_sham` and `random_k4_s0` exchange places.
⭐ **Four arms score BELOW the single fixed ordering when measured prompt by prompt.**

⚠ The per-prompt statistic is an average of ratios with varying denominators and is sensitive to
prompts where `att_p − floor_p` is small; **48 of 968 (5.0%)** are excluded because the ratio is
undefined there. It is reported as a second view, not as the headline.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R804's annotator-weighted **0.451773** reproduced exactly, and `CEIL_ATT` **0.686265** | PASS after the weighting was separated |
| PLACEBO | the constant arm's own share of [floor, ceiling]: **0.0e+00** | PASS — exactly 0 |
| POSITIVE | a synthetic arm at known fraction f = 0 / 0.25 / 0.5 / 1.0 recovers **0.000000 / 0.250000 / 0.500000 / 1.000000**, max \|Δ\| **2.2e-16** | PASS |
| f=0 | recovers 0 and not more | PASS — the control can fail |
| NEGATIVE | a **synthetic world with no aggregate human tendency** (every annotator a uniform weak order), floor refitted, prompt-weighted, 200 draws: **0.416423 [0.414047, 0.419088]**, max **0.420731** vs real **0.449421** | PASS **after repair** — the whole null lies below |
| NOISE FLOOR | held-out floor over 20 prompt half-splits: sd **0.006628** | measured |

⛔ **The first negative control failed for two reasons, both of them this round's own subject.**
① It permuted **which prompt** an annotator belongs to — but a constant order sees no prompt
information, so the pooled multiset is unchanged and **the statistic is invariant by construction**:
a control that cannot fail. ② It pooled rows (**annotator-weighted**) against a **prompt-weighted**
observation — **the exact mixing this round caught in R804, committed inside the control checking for
it.** It returned 0.454859 > 0.449421 and printed FAIL. Repaired per §1 by naming the world the null
excludes and **building it**.

## WHAT DIED

- **R817's NEXT as posed** — the number existed in R804 already.
- **"`coval_core` captures 81% of attainable"** as a statement about what a core achieves — on the
  informative range it is **50%**.
- **my own negative control**, twice over.

## WHAT SURVIVES — AND THIS ROUND ADDS

Every ordering, and the scale itself now has a measured floor: **0.449421 prompt-weighted, 65.1% of
attainable, with a synthetic null at 0.4164 confirming the floor is real structure and not
arithmetic.** Clause ② can now be written against a range rather than a ceiling.

## SCOPE

968 prompts × 9 arms × 75 weak orders · floor = the best single constant order, in-sample and
held-out over 20 prompt half-splits · per-prompt version excludes the **48** prompts where
`att_p = floor_p` · bootstrap over prompts, NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a floor free of in-sample optimism | choosing the constant order without seeing any of the data; the held-out version costs **0.002792** and is reported beside the in-sample one — **measured, not assumed** |
| a per-prompt share defined everywhere | prompts where a constant order is not already optimal; **48 of 968** are not — **counted and excluded**, with the rate printed |
| an ordering claim from the corpus-level rescaling | it is affine and cannot reorder — **a derivation, labelled before the run** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The scale now has both ends and a floor: **0.449421 → 0.686265**, with `coval_core` at **0.5001** of
the informative range and `gen_sham` at **0.1509**. Computed by this round's `run.py`, four arms fall
**below** the constant floor when measured prompt by prompt — `genericpool16` −0.1118, `full`
−0.4221, `gen_sham` −0.5398, `random_k4_s0` −0.5938.

That is the thread. Those four beat a fixed ordering **on average** while losing to it **prompt by
prompt**, which can only happen if their advantage concentrates where the span `att_p − floor_p` is
wide and their deficit falls where it is narrow. The step is to test that directly: regress each
arm's per-prompt margin over the constant order on the span itself. A margin proportional to the span
means those arms carry no prompt-specific skill and the corpus-level average is a width artifact; a
flat margin means the per-prompt statistic is the misleading one and the corpus number stands.
