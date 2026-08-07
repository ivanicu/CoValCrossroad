# R475 · The dataset card decides clause ③

**The decision this made safe.** Whether clause ③'s verdict on `coval_core` is *unknowable here* — the
position held since R466 — or *decided*. It is decided, and it goes against the object the definition
was written from. **The extension of the definition is 0, not [0, 1].**

## What was asked

R474's next step: check whether the release documents *why* it ships one core, because
*"the dataset card is a file on disk that nobody in 46 rounds has opened."*

## What the card says, verbatim

> *"**Core rubrics**: In post-processing, for each prompt we keep only a small set of highly rated,
> non-redundant, and non-conflicting rubric items. … Our process first rewrites all rubric items to
> have positive weight and then merges semantically redundant rubric items while adjusting their
> scores. Then, **it aims to select up to four rubric items with the highest average ratings** that
> remain compatible with each other and do not repeat the same idea."*

`w = mean(annotator score)` is exactly what `W_READERS = {topw_k, topabs_k, topwvar_k}` consume, and
③ excludes them. **`coval_core` is EXCLUDED.**

## Why the object still had to be asked

A card is a description, and a convincing description is the most dangerous evidence there is. So the
card was made to make a **falsifiable prediction** and the object was allowed to refuse it.

| arm | pct(\|w\|) | pct(w) | sim | role |
|---|---|---|---|---|
| oracle (matcher removed) | **0.8437** | **0.8495** | 1.0000 | the ceiling, MEASURED |
| verbatim top-4 plant | 0.8399 | 0.8462 | 1.0000 | POSITIVE — recovers ceiling within 0.01 |
| verbatim random plant | 0.4992 | 0.5026 | 1.0000 | g=0 — the control could have failed |
| **real core** | **0.5681** | **0.6068** | 0.4882 | the estimand |
| cross-prompt core | 0.4926 | 0.5166 | 0.1002 | NEGATIVE — null |

**The core sits 27.1% of the way from chance to a pure top-4-by-`w` selector (21.5% on `|w|`) — both
LOWER BOUNDS**, because the matcher recovers the rewritten source at only `sim ≈ 0.49` and imperfect
matching attenuates toward chance. Stable across three tokenisations. Placebo (file index) null.

## What the object refused

The card says items are rewritten to positive weight *before* ranking, predicting `|w|` should track
the core more tightly than `w`. **It is the reverse: 27.1% on `w` against 21.5% on `|w|`.** The core
tracks items rated **highly**, not items rated **strongly**. The card is right that ratings are
consumed and wrong about which functional of them.

## Why four rounds missed it

The released core items carry **only `criterion`** — no `rubric_item_id`, no `scores`. The rewrite
severs the join, so R469's measurement was correct: **no instrument here can recover the provenance.**
Its *conclusion* quantified over the wrong domain. ③ is a **provenance predicate**, and provenance is
established by a **record**, not a measurement. The release publishes the record.

## The ontology shift

**A definition of "core" whose extension excludes CoVal-core is not a definition of CoVal-core.**
③ was derived from `corebench/select_core.py` — *this campaign's* arm-generation code — then applied
to an object whose construction pipeline is not released. Either ③ is too strong and should forbid
only the prompt's **rankings**, or 32 rounds have defined an object other than the one measured.
**R475 does not adjudicate this**, and the branches differ in what "core" means.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R475_the_card_decides_clause_three/run.py

Seed 0 · 983 prompts · artifact `results/r475_card_vs_object.json` · exit 2 if any control fails.
