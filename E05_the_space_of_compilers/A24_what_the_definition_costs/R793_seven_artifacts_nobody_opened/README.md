# R793 · seven artifacts nobody opened, and a definitional clause retired on 1 normalisation of 3

`run.py` · `PREREGISTRATION.txt` · `results/coverage.json` · 11 artifacts × 468 `run.py` files ·
7 arms × 968 prompts × all annotators · **WORLD A** · two hash seeds byte-identical, md5 `84c3474600a3dfa0295c6c224c3272b1`

## THE DECISION THIS MAKES SAFE

**`whose_verdicts.json` retired the clause *"a core preserves ITS verdicts"* on the one normalisation
of three that returns that answer — and it is the non-standard one.**

| statistic | `coval_core` | vs FULL | verdict | |
|---|---:|---:|---|---|
| **raw difference** | −0.2185 [−0.2336, −0.2024] | — | **WORLD A** | ⭐ **the statistic the artifact's own docstring REGISTERS** |
| **/ CEIL_H** | **1.0264** | 0.7850 | **WORLD B** | the statistic it SHIPS |
| **/ √CEIL_H** | **0.7625** | 0.7850 | **WORLD A** | standard disattenuation — **D4, written before the run** |

**CEIL_H = 0.551880 [0.544992, 0.558997]** over all annotator pairs. Swept across its own bootstrap
interval the ceiling cell returns B in **1.000 of 400 draws** — so **the fragility is not in the
ceiling estimate, it is in the choice of normalisation.** And a "fraction of ceiling" of **1.0264** is
itself a tell: the shipped quantity is not a proportion.

## ⭐ E1 · THE COVERAGE, WITH BOTH CONTROLS

| | |
|---|---|
| deliberate artifacts in `corebench/results/` (not `sat_`, `sat08_`, `core_`) | **11** |
| opened by at least one of this arc's **468** `run.py` files | **4** |
| **UNREAD BY EVERY ROUND** | **7** |
| `pairwise.json` | read by **39** rounds |
| `leaderboard.json`, `subgroup_…json` | read by **1** round each |

Unread: `ablate_novel` · `dimension_curve` · `importance_recoverable` · `similarity_gradient` ·
`synthetic_world` · `unit_robustness` · `whose_verdicts`. **All eleven were committed on 2026-08-03**
— one batch, four of it read.

## ⛔ AND THE ENUMERATION CONTAMINATED ITSELF WITHIN ONE ROUND, TWICE

The first run scanned **its own `run.py`**, which names three of the artifacts it was counting.

- **UNREAD fell 7 → 5.** The round changed the population it was measuring, by existing.
- **The NEGATIVE control FAILED**, because its sentinel string was a literal in a scanned file.

R631 recorded this exact vector — *"a round scanning a population its own rounds write to
contaminates itself within one round"* — and R780 fixed it the same way. `THIS_ROUND` is now excluded
and printed; the sentinel is assembled at runtime so the literal never exists on disk. **A count and
a control, both wrong, from the same one-line cause.**

## ⚠ THE ARTIFACT'S DEFECT IS NARROWER THAN IT LOOKED, AND SAYING OTHERWISE WOULD BE THE CHEAP ATTACK

The docstring's KILL reads *"paired CI on (agreement with human − agreement with full)… **Positive**
and excluding zero for the top arms → world B."* The raw difference is **negative** and excludes zero,
which by that branch is **World A**. But `whose_verdicts.py:54` **documents** the switch: *"first
version of this script printed a WORLD A verdict off it. Fix: measure the human ceiling… and report
each agreement AS A FRACTION OF ITS OWN TARGET'S CEILING."* The reason is real — the human ceiling is
0.55, the rubric's is 1.0 by construction. **What was never done is updating the ESTIMAND and the
KILL to match**, so the JSON ships a verdict its own preregistration contradicts and records only the
answer string.

## ⭐ AND THE INSTRUMENT: 1 ANNOTATOR OF 16, BUT D3 HELD

`whose_verdicts.py:79` samples **one random annotator per prompt** over 3 seeds; the release ships a
median of **16**. Recomputed on **all** annotators:

| arm | vs HUMAN (all) | shipped (1 ann) | Δ | vs FULL | raw difference |
|---|---:|---:|---:|---:|---|
| `coval_core` | 0.5665 | 0.5682 | −0.0018 | 0.7850 | −0.2185 [−0.2336, −0.2024] |
| `topw_k4` | 0.5642 | 0.5650 | −0.0008 | 0.8049 | −0.2407 [−0.2567, −0.2255] |
| `gen` | 0.5352 | 0.5386 | −0.0035 | 0.7414 | −0.2062 [−0.2217, −0.1914] |
| `full` | 0.5087 | 0.5136 | −0.0049 | **1.0000** | −0.4913 [−0.5009, −0.4811] |
| `random_k4_s0` | 0.4927 | 0.5005 | −0.0078 | 0.8247 | −0.3320 [−0.3454, −0.3176] |

**Largest point move 0.0078**, every one negative — the under-powered design slightly *overstated*
the human column. **D3 predicted exactly this** (sampling 1 of 16 inflates variance and leaves
expectation alone), so **World C correctly did not fire**: the instrument was not the problem, the
normalisation is.

## E4 · AND IT QUALIFIES THE ROUND I COMMITTED AN HOUR AGO

`unit_robustness.json` ships *"the ordering is UNIT-ROBUST; the day's prompt-default was harmless"* —
prompt order == annotator order, **0 inversions**. R792 measured **11 of 190 pair verdicts flip**
between those same two units. **Both hold.** An ORDERING claim and a PAIRWISE-RESOLUTION claim are
different objects, and R792's headline needs that qualifier — it has it here.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT (D1) | recomputed `vs FULL` against the shipped column: worst \|Δ\| **1.110e-16** — deterministic, it *cannot* move | PASS, else exit 2 |
| PLACEBO | `full` against FULL = **1.000000000000** | PASS |
| POSITIVE | raw difference by planted δ: 0 → −0.2185 · 0.05 → −0.1685 · 0.10 → −0.1185 · 0.20 → −0.0185 · **0.30 → +0.0815, crosses** | PASS, band admissible |
| NEGATIVE | `full`'s class shuffled across prompts: vs FULL **0.7850 → 0.4998**; vs HUMAN unchanged to **0.0e+00** (a derivation, checked) | PASS |
| SHAM | the same comparison against `random_k4_s0`'s class: **0.7342** against 0.7850 | the compressed object's identity is worth 0.05 |
| NOISE FLOOR | CEIL_H bootstrap [0.544992, 0.558997]; annotator split-half on the human column **0.003523** | measured |
| E1 POSITIVE | R792 found for the file R792 opens | PASS |
| E1 NEGATIVE | a runtime-assembled sentinel matches nothing | PASS **after repair** |

## MULTIPLICITY

7 arms × 3 normalisation cells + the CEIL_H sweep. The normalisations are a **specification curve** —
the same test under different transforms of the same data — and are reported whole rather than
corrected as though independent. The 7 raw paired CIs all exclude zero, all negative.

## WHAT DIED

- **`whose_verdicts.json`'s WORLD B as a settled result** — it is 1 of 3 defensible normalisations,
  and the other two, including the standard one, return World A. ⚠ **Not overturned — UNVERIFIED.**
  Which normalisation is right is an argument about what the two ceilings mean, and this data does
  not identify it.
- **"7 of 11 unread" as a stable number** — it was 7 before this round and 5 during it, until the
  scanner stopped counting itself.
- **my own negative control**, whose sentinel was a literal in the corpus it searched.

## WHAT SURVIVES

R792's finding, now qualified: the estimand moves **verdicts** and not the **ordering**, and both
artifacts are right about their own object. And `whose_verdicts`'s deterministic column, reproduced
to **1.1e-16** by different code — the shipped `vs FULL` figures are exactly right.

## SCOPE

11 artifacts × 468 `run.py` files (this round excluded) · 7 arms × 968 prompts × all annotators
(median 16) · CEIL_H over all annotator pairs · NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| which normalisation is CORRECT | an argument about what the two ceilings mean; not identified by this data |
| construct validity | an external gold standard — `corebench/score.py:34` |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

Five artifacts remain unread and this round opened two of them; both bore on committed work, which is
2 for 2. Computed by this round's `run.py`, the shipped `whose_verdicts` verdict rests on a
normalisation that returns a fraction-of-ceiling of 1.0264, and its own registered statistic returns
the opposite world. The step is to settle the normalisation by argument rather than by measurement —
state what each ceiling means, decide whether the human column should be compared to the rubric
column at all given one is a proportion of a noisy target and the other of a deterministic one, and
write the answer into the definition's own text. That is a formulation act, and it is the first thing
in this arc that no further computation can decide.
