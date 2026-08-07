# R736 · the wall was an inverted index

**R735's wall is FALSE — the experiment it deferred to a new selection run is a reanalysis. And the
89% "finding" that led me here was my own inverted index, which my positive control could not see.**

## What happened, in order
1. R735 declared that separating overlap from selection size **needs a new selection run**.
   *"A wall never checked"* is a named failure mode, so I checked it.
2. Satisfaction is stored per `(prompt, index, letter)`. I read the **letter** as the criterion index
   and joined arms on `(prompt, index, criterion text)`. **That returned 89% inconsistency** — which
   would have meant the judge's score depends on which other criteria share the set. A large claim.
3. ⛔ **It was my bug.** `corebench/judge_core.py:77` builds **one judge call per criterion**, so
   set-dependence is impossible by construction — *the source said so before any measurement.*
   A k=12 arm carries indices **0..11** and letters **A..D**: **the index is the criterion, the
   letter is the response.**

## ⛔⛔ My positive control passed on the bug
The same-object pair *(R730: `random_k4_s1` ≡ `random_k4_s1_ctlS1`)* returns **0.000000 under the
corrected join AND 0.000000 under the inverted one** — because the inversion applies identically to
both sides and **cancels**.

> **§4:** *a control that shares the instrument's blind spot confirms the instrument and licenses
> nothing.*

**I quoted that row three rounds ago while building the control it warns about.**

⭐ **The control that CAN see it** is running **both joins** and requiring them to disagree — now the
round's gate. It returns a gap of **+0.851120**.

## The measurement
| join | rate |
|---|---|
| **corrected** `(prompt, response, criterion)` | **0.002643** |
| inverted *(the bug)* | **0.853763** |
| criterion texts permuted *(negative)* | 0.888624 |
| criterion text dropped *(sham)* | 0.897859 |

**Satisfaction is a function of `(prompt, response, criterion)` to 0.997357.**

## The consequence — the wall is false
| | |
|---|---|
| distinct criteria scored per prompt | min 4, **median 15**, max 38 |
| prompts with ≥ 8 scored criteria | **917 of 968** |
| prompts reachable at target overlap 0/1/2/3/4 | 917 / 948 / 964 / 965 / **968** |

**Arms with CHOSEN overlap can be assembled from scores already on disk.** R735's next step needs no
new judge run.

⚠ **The residual 0.002643 is not zero**, and **R419 measured the scoring-only floor at exactly 0.0**
on identical criteria — so it is real. **This round bounds it and does not explain it**; naming its
cause needs the judge re-run.

## Controls — 6 PASS, 0 FAIL
**DISCRIMINATING** *(the new one)*: both joins run, gap **+0.851120 > 0.10** · **POSITIVE**:
same-object pair → 0.000000, *labelled NECESSARY and INSUFFICIENT* · **g=0**: arm against itself → 0 ·
**NEGATIVE**: criterion texts permuted → 0.888624, excluding *"the criterion text is doing no work"* ·
**SHAM**: text dropped from the key → 0.897859, ingredient **absent** · **PLACEBO**: 0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A corrected join rate | 0.003 [0, 1] | **0.002643** | yes |
| B inverted join rate | 0.89 [0, 1] | **0.853763** | yes |
| C median scored criteria | 14 [1, 100] | **15** | yes |
| D prompts with ≥ 8 | 900 [0, 968] | **917** | yes |
| DIRECTIONAL the wall is false | — | **holds** | — |

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, **both writes verified**.
**Artifact:** `results/r736_join_and_wall.json` · 190 key-sharing pairs.
