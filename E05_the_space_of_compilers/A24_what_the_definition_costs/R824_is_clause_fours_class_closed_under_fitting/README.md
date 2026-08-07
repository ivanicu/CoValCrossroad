# R824 · Is ④'s class closed under fitting? The text is silent, and the extension is 0 or 25

**E05 · A24 · R824. WORLD B.** 968 prompts × 4 responses × 14 features · 58 arms · 21 specification
cells × 20 splits. Two seeds byte-identical: `f8a732269642f50859134c630172bd86`. Source `8b7c3298`.

## The decision this makes safe

④ reads, verbatim (`DEFINITION.md:24`): *"scores better, under that same judge J, than **every rule
computable from the response set alone**."*

That constrains what a rule **consumes at inference**. It is **silent about what its construction
consumed.** R435's thirty are hand-built and read no labels ever. A supervised predictor reads only
responses at inference but was fit on *other prompts'* human labels. Two defensible readings — and
③'s own wording (*"no information from **that prompt's** own human labels"*) shows the deliverable
already uses the fit-on-other-prompts distinction elsewhere, so the ambiguity is not hypothetical.

**Nobody in 400 rounds had built an object that distinguishes them.**

## Result — the extension depends on a reading of the definition's own text

| reading | ④'s bar | ④ excludes |
|---|---:|---:|
| **STRICT** — no parameters fit on human data | **0.455679** (`max_len_chars`, R823) | **0 of 58** |
| **PERMISSIVE** — fit on other prompts allowed | **0.519689 ± 0.005438** | **25 of 58** |

**The 25 are exactly the arms that read nothing or are shams**: every `random_k*`, `topvar_k4`,
`topabs_k4`, `topwvar_k4`, `full_sham`, `gen_sham`, `topw_k4_sham`, `coval_core_sham`.

**Every load-bearing arm survives**:

| arm | A2 | permissive margin |
|---|---:|---|
| `oracle_k4` | 0.6283 | +0.1086 [+0.0950, +0.1222] |
| `coval_core` | 0.5665 | +0.0468 [+0.0326, +0.0609] |
| `topw_k4` | 0.5642 | +0.0445 [+0.0302, +0.0587] |
| `generic` | 0.5514 | +0.0317 [+0.0175, +0.0459] |
| `genericpool16` | 0.5422 | +0.0225 [+0.0082, +0.0369] |
| **`gen`** | 0.5352 | **+0.0155 [+0.0005, +0.0304]** |
| `full` | 0.5087 | −0.0110 [−0.0257, +0.0038] — UNVERIFIED |

⭐ **`gen` clears ④'s permissive bar by +0.0005 at the lower bound.** R822 found `gen`'s ② verdict
straddling its threshold across weightings; it now sits on ④'s threshold too. **The arm the ②∧③
question rests on is marginal under two independent clauses.**

## Specification curve — 19 of 21 cells clear the strict bar

`all14|logistic_C1.0` **0.519689** · `all14|logistic_C10.0` 0.519508 · `all14|logistic_C100.0`
0.519343 · `all14|logistic_C0.1` 0.518603 · `all14|logistic_C0.01` 0.516207 · `all14|ridge` 0.513486
· `non_length|*` 0.4995–0.5063 · `all14|gboost` 0.500110 · `length_only|*` 0.4269–0.4600.

**Only `length_only|logistic_C0.01` (0.454833) and `length_only|gboost` (0.426911) fall below the
strict bar.** The result is not one cell: it holds across model class, regularisation and feature
set, and **the non-length features alone (0.5063) already beat the strict bar by more than 10×
its noise floor.**

## Controls

| control | returned |
|---|---|
| **OBJECT** | `max_len_chars` reproduces R823's **0.455679** |
| **PLACEBO** | labels shuffled at fit: **0.431479** vs random-scorer chance **0.428742** — at chance, below the strict bar |
| **POSITIVE** | dose-response against **the plant**: g=1.0 → **0.9863**, g=0.5 → 0.5792, g=0.2 → 0.5179, **g=0.0 → 0.5104**. Monotone; recovers; fails at zero dose. |
| **NEGATIVE** | synthetic arm from the bar's own distribution: **−0.00015 ± 0.00529** vs real **+0.08188** |
| **SHAM ⭐** | the identical learner on **14 random features**: held-out **0.429425 ± 0.004633** — fitting on noise buys **+0.000684** over chance, so the learned bar sits **+0.090263 above the sham** |
| **NOISE FLOOR** | best cell across 20 splits: **0.005438** |
| **BH** | 58 arm tests: 57 survive, 1 does not |

⭐ **The sham is what makes the +0.064 rise attributable.** Held-out fitting on pure noise buys
**+0.0007**. The rise from 0.4557 to 0.5197 is **not** an artifact of fitting; it is the features.

## What this round got wrong

**The first positive control scored a planted model against the real human labels instead of against
the plant.** It planted `w = len_chars`, fit on it, then evaluated with `a2_from_scores` — which
compares to `H`, the humans. So it measured how well a length-planted rule predicts humans
(**0.4511**, i.e. the strict bar), and reported that as failed recovery. §4: *the control targeted a
different statistic than the one being reported*, and its two sides were not the same object.

**And its g=0 arm returned `nan`.** Planting `w = 0` makes every target sign zero, and `pairdata`
drops zero-signed pairs, so the fit set was empty. **A control that returns `nan` is not a control**
— it cannot fail, and it cannot pass. Rebuilt as a dose-response with g=0 planting *random* signs: a
learnable-shaped target with no learnable signal.

**The gate correctly refused the verdict** while this was broken, and the run printed
`WORLD UNVERIFIED` beside a 0-vs-25 result. That is the gate doing its job on the largest result of
the session.

## Verdict and what it downgrades

**WORLD B — the reading decides the extension.** ④'s text must be disambiguated in the deliverable.

⚠ **R821's "free-but-real" verdict on ④ is DOWNGRADED to a scope claim.** ④ excludes nothing at home
*under the strict reading only*. Under the permissive reading it is a **binding** clause that removes
25 of 58 arms — every random and every sham. R823's confirmation is scoped the same way: it widened
the **strict** class from 6 rules to 30.

## What this round cannot do

| criterion | requires |
|---|---|
| decide which reading is *correct* | an authorial intent the text does not record; this round measures only that the choice matters |
| "every rule computable from the response set" | an infinite class; 14 features × 7 model classes stand in for it |
| independently replicated | a second release |
| cross-dataset / cross-model | a second site |
