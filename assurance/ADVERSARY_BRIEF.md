# Adversary brief

Every finding in this repository was sorted into "established" or "interpreted" by
the same process that produced it. That is not a weak check; it is not a check at
all. A reviewer sampled from the same weights can only attack the claims the author
already anticipated, which is exactly why those read as fluent.

No independent challenger has run against this work. This file is what one should
be handed.

---

## Mandate

You have not seen this repository before and you are not being asked to appreciate
it. Your only job is to move claims **down** a bucket.

1. For every claim marked established, name the reading that was smuggled in with
   the number.
2. Find a place where the repository contains its own counterevidence and did not
   notice. (There are twelve known ones in [RETRACTIONS.md](../RETRACTIONS.md).
   Find a thirteenth.)
3. Attack the **boundary** of each claim — name a regime where it is asserted but
   never tested.
4. Return one of three verdicts per contested row: CONFIRMED, OVERTURNED, or
   **UNVERIFIED** — the check was unfit, which is not an acquittal.

You are given: the repository, `data/fetch.py` to obtain the release, one consumer
GPU, and no obligation to be kind. Budget: the full pipeline is 0.36 measured
GPU-hours, so re-running anything you doubt is cheap.

---

## Pre-registered predictions

**Written before any adversary ran, so that what they actually find can be scored
against it.** If a challenger overturns something from the "safe" column, my sense
of my own work is worse calibrated than I think — and that is the more useful
result.

### Most likely to fall (I would bet against these myself)

| # | Claim | The attack I expect |
|---|---|---|
| A1 | **The blocs in r16/r17/r18 are a real constituency** | The split is a median cut on the top principal component of a matrix where that component carries **0.541%** of the singular mass. A 0.5% axis is a thin thing to call a bloc. My defence is the regret control — profile splits give 2.07 against 1.10 for random splits — but a challenger should ask whether that gap survives a bloc definition I did not choose, e.g. demographic or country strata. |
| A2 | **r05's "compression is content-blind"** | Survival is a lexical token-overlap threshold. I showed absolute rates move 0.354→0.124 across thresholds and argued only the *ordering* is stable. A challenger should test whether the ordering survives a semantic survival measure, since the ordering is the whole claim. |
| A3 | **r07's anthropomorphism markers** | The lexicon is hand-written and already produced one twelve-fold error (2.96% → 0.16% after word boundaries). The regression is within-prompt and length-controlled, but the construct is mine and nobody has attacked the marker list itself. |
| A4 | **The satisfaction judge measures satisfaction** | It is a Yes/No logit gap from a 2B base model behind two few-shot examples. It may be measuring surface plausibility. r14 tests paraphrase invariance and had not run when this was written; if the judge is not paraphrase-invariant, r04's attribution is partly a wording measurement and much of this repository is scoped much harder. |
| A5 | **The gold preference model** | A linear head on mean-pooled embeddings, trained on the same 18,384 rankings it is used to adjudicate. Held-out 0.60 (2B) and 0.66 (0.8B) against a 0.529 length baseline — real, but not commanding. The two heads correlate only **+0.4775**, which already says two equally-validated golds disagree substantially. |

### Least likely to fall (attack these hardest — if one goes, the surprise is large)

| # | Claim | Why I think it holds |
|---|---|---|
| B1 | **Cross-prompt rater agreement persists** (ρ=0.147, z=+16.6) | Permutation null, prompt-difficulty control, and a response-style control that moved it only 0.1479→0.1471. Three independent ways to kill it, none did. |
| B2 | **9,684 of 15,248 criteria carry one score, and n^¼ gives them 38% of top-four slots** | Arithmetic on primary counts, independently recomputed from raw JSONL without the release's code. |
| B3 | **The two-regime split at task six** | Step model R²=0.964 against 0.448 for a trend, and effort *rises* within each segment. A trend explanation has to explain a rise. |
| B4 | **r19's floor sensitivity, span 2.47×** | Pure arithmetic on numbers r10 had already stored. Nothing to overturn except the choice to exclude the 0.5405 cell, which is stated. |

### What I expect to be told and do not think is right

- *"The judge is too small to conclude anything."* It reaches 0.686 pairwise against
  the ~0.60 the release authors report for their own scoring. The prompt-level
  concordance is genuinely worse (0.61 vs ~0.75) and both numbers are in the README.
  Size is a real limit on the *concordance* claim and not on the *decomposition*,
  which is a difference between arms measured with the same instrument.
- *"You should not audit a dataset you did not collect."* The release ships an
  incorrect personal-ranking count in its own card, which the audit found by
  counting. That is what external assurance is for.

---

## The single thing I most want checked

**r12 and r13 together produce a state I cannot explain.** The attribution is real,
carried by criteria authored *without sight of the responses*, and still does not
transfer to responses those criteria were not written against. Three explanations
were proposed; one is dead (r13), one is untested (r14), and one is a bare
restatement of the observation.

If a challenger can name a fourth explanation I did not consider, that is worth more
than any verdict on the rows above.
