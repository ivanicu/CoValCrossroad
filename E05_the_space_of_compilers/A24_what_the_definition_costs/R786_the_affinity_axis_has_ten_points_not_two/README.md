# R786 · `generic` has zero rubric affinity and clears clause ② at 0.7780 — one counterexample beats the correlation

`run.py` · `PREREGISTRATION.txt` · `results/affinity_axis.json` · 89 arms with text · **WORLD C**

## THE DECISION THIS MAKES SAFE

**R785's hypothesis — that clause ② may score rubric affinity rather than quality — does not survive
its own extended population.** The decisive datum is not a correlation, it is a single arm:

| arm | affinity @4 | its own null | q_resolved |
|---|---:|---:|---:|
| `coval_core` | 0.4954 | 0.0552 | 0.9978 |
| **`generic`** | **0.0249** | **0.0249** | **0.7780** |
| `gen` | 0.0865 | 0.0357 | 0.0396 |

**`generic`'s affinity equals its own cross-conversation null to four decimals — zero rubric affinity
above chance — and it clears clause ② at 0.7780.** High ② standing therefore does not require rubric
affinity, and one counterexample settles that more cleanly than any r at n = 3.

## ⛔ AND R785's POPULATION WAS TYPED, NOT COUNTED

R785 reported *"arms with criterion TEXT available: 2"* from a literal dict
`q782 = {"coval_core": 0.9978, "gen": 0.0396}`. **A literal cannot return a different value**, so that
population claim had no severity — a check that cannot fail, in the round that had just caught its own
placebo.

Counted in code here: **89 arms carry criterion text.** **79 are rubric-derived** (verbatim overlap
≥ 0.5), **10 are not**: `coval_core`, `coval_core_sham`, `full_sham`, `gen`, `gen_sham`, `generic`,
`genericpool16`, `promptecho`, `promptecho_sham`, `topw_k4_sham`. **Five times R785's number.**

## E2 · THE AXIS, ENUMERATED

| arm | verbatim | aff@3 | aff@4 | aff@5 | null@4 | A2 | q_res |
|---|---:|---:|---:|---:|---:|---:|---:|
| `coval_core` | 0.0670 | 0.4944 | **0.4954** | 0.5018 | 0.0552 | 0.5665 | 0.9978 |
| `promptecho` | 0.0006 | 0.1479 | 0.1401 | 0.1478 | 0.0359 | — | — |
| `gen` | 0.0000 | 0.1410 | 0.0865 | 0.0867 | 0.0357 | 0.5352 | 0.0396 |
| `topw_k4_sham` | 0.0000 | 0.0905 | 0.0564 | 0.0471 | 0.0562 | 0.4909 | 0.0000 |
| `full_sham` | 0.0000 | 0.0885 | 0.0561 | 0.0465 | 0.0579 | — | — |
| `coval_core_sham` | 0.0000 | 0.0836 | 0.0550 | 0.0459 | 0.0558 | 0.4956 | 0.0000 |
| `gen_sham` | 0.0000 | 0.1028 | 0.0356 | 0.0319 | 0.0360 | 0.4828 | 0.0000 |
| `promptecho_sham` | 0.0000 | 0.0595 | 0.0352 | 0.0214 | 0.0353 | — | — |
| `genericpool16` | 0.0000 | 0.1094 | 0.0316 | 0.0265 | 0.0316 | — | — |
| **`generic`** | 0.0000 | 0.1212 | **0.0249** | 0.0243 | **0.0249** | 0.5514 | 0.7780 |

**Only `coval_core` sits meaningfully above its null.** Every other non-rubric-derived arm is at or
near chance, and `generic` and `genericpool16` are *exactly* at theirs.

## E3 · AND THE CONFOUND I REGISTERED BEFORE THE RUN IS THE EXPLANATION

| population | n | r(affinity, q_res) @3 / @4 / @5 | MDE (D3) | |
|---|---:|---|---:|---|
| with shams | 6 | +0.7678 / +0.6907 / +0.6993 | 0.924 | **inside the MDE** |
| sham-free | 3 | +0.6421 / +0.5841 / +0.5841 | undefined at n<4 | **inside** |

**A2-CHECK, the registered confound's control:**

| population | corr(affinity, A2) | **corr(A2, q_resolved)** |
|---|---:|---:|
| with shams | +0.6391 | **+0.8747** |
| sham-free | +0.7878 | **+0.9601** |

⭐ **`q_resolved` is very nearly a re-expression of A2** — it counts how many of a fixed 0.043-wide
reference band an arm beats, so an arm's A2 largely determines it. At r = **+0.9601** sham-free,
"affinity predicts ② standing" reduces to "affinity predicts A2", and that relation (+0.79) sits
inside any MDE this population can support. **The confound was written down before the run and it won.**

⚠ Arms with text but **no** q_resolved, listed rather than silently dropped: `full_sham`,
`genericpool16`, `promptecho`, `promptecho_sham` — R782's modal-k=4 population excludes them
(`promptecho` covers 398 prompts, `genericpool16` is k=16, `full_sham` is the rubric's sham).

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R782's artifact loads with q_resolved for 26 arms; the enumeration is **computed in code** and printed with its count | PASS, else exit 2 |
| PLACEBO | a rubric against itself: **1.000000** | PASS |
| POSITIVE | the rubric-derived arms must return **1.0** (D1) — `greedy_k4_fit1`, its two judge variants, `greedy_kA`, `greedy_kB`, `indep_k4_fit1` all exactly 1.0 | PASS — **a derivation used as an instrument check, not a result** |
| NULL | cross-conversation affinity, per arm, in the E2 table | `generic` and `genericpool16` sit *exactly* on theirs |
| SHAM-SPLIT | the registered specification: with shams n=6, without n=3, both printed | shams do not rescue it |
| A2-CHECK | the registered confound | **it is the explanation** |
| SWEEP | token length {3, 4, 5} | no tokenisation changes the verdict |
| MDE-FIRST | D3 printed **before** any r: n=5 → 0.963 · 6 → 0.924 · 7 → 0.886 · 8 → 0.849 · 10 → 0.785 | so no r here could have resolved |

## WHAT DIED

- **R785's "n = 2"** — a hard-coded dict; the true count is 10 non-rubric-derived arms of 89 with text.
- **R785's hypothesis** that clause ② scores rubric affinity — `generic` has zero affinity above its
  own null and clears ② at 0.7780, and what covaries with q_resolved is **A2** at +0.9601.
- **R785's NEXT** — "the axis cannot be extended on this site" was false by a factor of five, and the
  extension is what killed the hypothesis the NEXT wanted recorded in the definition.

## WHAT SURVIVES

R785's **paraphrase measurement** is untouched: `coval_core` sits at 0.4954 against a 0.0552 null,
nine times chance, and it is the **only** arm in the population that does. That remains a fact about
the released core; what it does not do is explain clause ②.

## SCOPE

population 89 arms with criterion text, 10 non-rubric-derived, 6 with q_resolved, 3 sham-free · 968
joined conversations · instrument verbatim intersection and best-match token Jaccard at {3,4,5} ·
baseline the cross-conversation pairing and R782's q_resolved · regime first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| a correlation with useful resolution | tens of arms carrying both text and q_resolved; **D3 priced it before the run** — at n=6 the MDE is 0.924 |
| q_resolved for `promptecho`, `genericpool16`, `full_sham`, `promptecho_sham` | R782's modal-k=4 population, which excludes them by coverage and by k |
| semantic rather than lexical affinity | an embedding model; the token measure bounds the lexical part only (R785) |
| whether affinity CAUSES ② standing | generating an arm at a chosen affinity and scoring it — the generator (R605) |

## NEXT

The affinity hypothesis is closed and the A2-CHECK is what closed it, which raises a question about
the instrument rather than the object: **`q_resolved` correlates with A2 at +0.9601, so it may be
carrying almost no information beyond the arm's raw score.** If so, four rounds of "clause ② standing"
have been reporting a monotone transform of A2 against a fixed band, and the band's only contribution
is where it cuts. Computed by this round's `run.py`, that correlation is +0.8747 with shams and
+0.9601 without, over 6 and 3 arms respectively — too few to settle it. The step is to compute
`q_resolved` and A2 across the modal-k=4 population, whose size of 26 was measured in R782 and where
both quantities already exist, then ask whether the residual of q_resolved on A2 is distinguishable
from zero.
