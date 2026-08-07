# R399 — the second corpus is a RATING corpus, and the overlap is 3 strings, 2 of them greetings

**The decision this makes safe:** *which estimand may a transport test use?* **Not CoVal's ordering.
Either a rating-agreement estimand, or `if_chosen` — which is a genuine pairwise preference on 26,886
interactions.**

## Result — `RATING | W_OVERLAP`. Five controls pass. **No GPU spent.**

### (A) measurement type

| | |
|---|---:|
| value range | **[1, 100]** over 68,371 rows |
| within-interaction values form a `1..k` permutation | **0.1%** |
| pre-registered thresholds | RANKING > 80% · RATING < 20% |
| **verdict** | **RATING** |

### (B) pairwise structure

| responses per interaction | 1 | **2** | 3 | **4** |
|---|---:|---:|---:|---:|
| interactions | 21 | **19,323** | 1,608 | **6,220** |

**27,151** interactions have ≥2 responses; **26,886 (99.0%) have exactly one marked `if_chosen`.**

### (C) overlap

| cut | CoVal distinct user turns | matches |
|---|---:|---:|
| **ANY** user turn (more sensitive — the headline) | 1,201 | **3** |
| **LAST** user turn (strict analogue) | 1,078 | **1** |

**The three: `does god exist?` · `hello` · `hi`.**

> ⚠ **Two of the three are degenerate.** `hello` and `hi` are common short utterances that collide by
> chance across any two conversation corpora; they are not evidence of a shared source. **Reading
> "W-OVERLAP = 3" as contamination would overstate it by 3×.** The substantive count is **1**, and the
> exclusion list is cheap either way — drop all three.

## ⛔ Why this was a blocker and not a detail

CoVal's unit is a **comparison**, and **every clause of the definition is stated against an
ordering.** A bounded 1–100 rating and an ordering are **different quantities**. Running the ordering
test on rating data would have rebuilt **R233's error one release over** — a correct number reported
against the wrong scope, which is *eleven of twelve* retractions in the audited programme.

## ⭐ And the corpus carries BOTH measurements

Declared in the docstring **before** the run, so the round could not pick the one that suited: the
second corpus has a numeric `score` **and** a boolean `if_chosen`. **`if_chosen` is structurally
closest to a CoVal comparison** — a preference among simultaneously-shown responses — and it is clean
on 99.0% of multi-response interactions. **So the ordering estimand is not lost; it just does not come
from `score`.**

## Controls

| | returned |
|---|---|
| **CLASSIFIER (+)** | synthetic **permutation** groups → `RANKING` (perm share 1.00) — `PASS` |
| **CLASSIFIER (−)** | synthetic **bounded-value** groups → `RATING` (perm share 0.00) — `PASS`. Both directions, because a classifier answering RATING always would pass a one-sided check |
| **MATCHER (+)** | a second-corpus prompt is found in the second-corpus index — `PASS` (tests the **index**) |
| **MATCHER (+2)** ⭐ | a CoVal prompt matches **itself** through the same normalisation — `PASS` (tests the **normalisation**, on the **claim's own unit**). *A control sharing the instrument's blind spot confirms the instrument and licenses nothing* |
| **MATCHER (−)** | an absent string returns no match — `PASS`, so zero is attainable |

⭐ **The comparable unit was a specification, not a detail.** CoVal's `prompt` is a *conversation*
(`{id, messages}`); the second corpus's is a single turn. **Both cuts are reported, and the headline
uses the more sensitive one** — because `DISJOINT` is the flattering answer here, so the detector was
pointed in the direction that could embarrass it.

## Register

| criterion | status |
|---|---|
| **paraphrase-level overlap** | **N/A** — exact matching is one-sided; 3 is a **lower bound** on sharing |
| **whether the two scales are commensurable** | **UNTESTED** — a rating and a preference can coexist and still not be comparable; needs a linking study |
| **any transport result** | **N/A** — this round ran no test and computed no core |
| **a rubric for corpus two** | **ABSENT** — R398 already recorded it |

## The sentence I can no longer write

> *"test the core's transport against the second corpus's human scores"* — **as though `score` and a
> CoVal comparison measured the same thing.** They do not. The field that does is `if_chosen`.

Artifact: `results/r399_estimand_admissibility.json`, source-stamped.
