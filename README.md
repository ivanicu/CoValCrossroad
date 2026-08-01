# CoVal Crossroads

An independent audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a
dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to
contentious prompts, *and wrote down the criteria they judged by*.

**202 rounds** across 13 phases, numbered to r205 — **53 standing claims, 13 withdrawn**, and
**46 defect checks on the release, 16 of them clean.**

The release ships prompts, four responses per prompt, crowd-written rubrics and 18,384 rankings —
but **not** the criterion-by-response satisfaction labels, so its own scoring cannot be reproduced
from it. This repository rebuilds that layer locally and then asks what the rubric measures.

---

## The short version

**The apparatus works better than its critics would guess and worse than its numbers suggest.**

| question | answer |
|---|---|
| Does the crowd's rubric beat a dumb heuristic? | **Yes, clearly.** It picks the human top choice 50.3% of assessments against 37.3% for "pick the longest response" — +13.0 points, stable across weighting and outlier removal. |
| Is that good? | It closes **66–67%** of the reachable band. The ceiling is not 100%: two humans on the same prompt pick the same best response only **47.8%** of the time. |
| Do the criteria say what people value? | **Partly.** They are also descriptions of the answer their author had already chosen — authoring happens *after* ranking, and the effect is +0.0478 on a same-texts comparison. |
| Does compilation fix that? | **No.** The distillation into `coval_core` passes it through unchanged (+0.013, z 1.0, adequately powered). |
| Does compilation cost anything? | **Yes.** It gives back ~40% of the fairness the full rubric had gained over the panel's own plurality vote. |
| Is the "unacceptable" flag trustworthy? | **It is the most reliable channel here** — raters agree on *which* response is unacceptable at Spearman-Brown **+0.827**. |
| Do demographic groups have different values? | **Barely.** 2 of 28 demographic levels cluster above chance, both countries, at ~+4.5% — against +73.7% for a planted bloc. |

---

## What was established

Every number below states its unit, because five of seven headline figures in this project were
published without one. The check that found that is [`13_normative_chain/HEADLINES.py`](13_normative_chain/HEADLINES.py) and it re-runs.

### The pipeline

| finding | number | round |
|---|---|---|
| Crowd rubric vs. length heuristic | **+13.0 pts** [+10.3, +15.8] · 50.3% of assessments vs 37.3% | [r178](13_normative_chain/r178_rubric_versus_length) |
| …how much of that is the *weights* | **+14.6 pts**; shuffling them drops the rubric to the length heuristic's level | [r178](13_normative_chain/r178_rubric_versus_length) |
| …how much is circular (rater's own ratings) | **+0.6 pts** — leave-one-annotator-out barely moves it | [r178](13_normative_chain/r178_rubric_versus_length) |
| The reachable ceiling | **61.5–62.3%** of assessments (leave-one-out modal human choice) | [r179](13_normative_chain/r179_against_the_ceiling) |
| Human–human agreement | **47.8%** of prompts, chance 25% | [r179](13_normative_chain/r179_against_the_ceiling) |
| Reconstructed satisfaction layer | **0.686** pairwise concordance, 80,542 pairs | [r04](01_object_and_rebuild/r04_rebuild_satisfaction) |

### The compilation step

| finding | number | round |
|---|---|---|
| The positive-weight rewrite is real and targeted | 82.5% of negative-weight sources flip polarity vs 6.1% of positive · z +33 | [r176](13_normative_chain/r176_nonconflicting_nonredundant) |
| …but it loses the individual criterion | flipped items correlate **−0.14** with their source; unflipped **+0.81** | [r189](13_normative_chain/r189_does_the_rewrite_preserve_direction) |
| Compilation gives back fairness | **+4.2 pts** of group disadvantage returns, full → core · z +3.3, 851 strata | [r146](13_normative_chain/r146_does_compilation_add) |
| …and the full rubric was *fairer* than the plurality | 5.5 pts vs 15.6 pts | [r146](13_normative_chain/r146_does_compilation_add) |

### The criteria themselves

| finding | number | round |
|---|---|---|
| Criteria encode their author's prior choice | **+0.0478** [+0.0336, +0.0620], 4,504 author pairs, same two texts | [r187](13_normative_chain/r187_post_hoc_rationalisation) |
| Compilation neither concentrates nor removes it | +0.013, z 1.0 · MDE 0.037 = 76% of the incoming effect | [r188](13_normative_chain/r188_does_compilation_keep_the_rationalisations), [r204](13_normative_chain/r204_the_nulls_need_power_not_jackknives) |
| The card's "highly rated" claim | **fails** as stated; selection is rating-*sensitive*, not rating-*ordered* (3.0→10.1% survival across weight bands) | [r171](13_normative_chain/r171_card_vs_artefact), [r181](13_normative_chain/r181_whose_criteria_survive) |
| "non-redundant" / "non-conflicting" | **UNVERIFIED** — a style confound of the same magnitude blocks the first; the proxy is blind to the second | [r176](13_normative_chain/r176_nonconflicting_nonredundant) |

### The people

| finding | number | round |
|---|---|---|
| Dissent is a stable individual trait | split-half **+0.486**, survives residualising on prompt assignment | [r180](13_normative_chain/r180_is_the_disagreement_a_person) |
| Demographic groups that actually cluster | **2 of 28** levels — Netherlands +6.3%, Mexico +6.0% | [r183](13_normative_chain/r183_does_any_attribute_mark_a_bloc) |
| …and what they cluster *about* | **nothing measurable** — 0 of 14 axis tests survive | [r186](13_normative_chain/r186_what_do_the_blocs_want) |
| The veto identifies content, not raters | S-B **+0.827** on *which* response, over 1,288 pairs | [r192](13_normative_chain/r192_is_the_veto_about_the_responses) |
| What gets flagged as unacceptable | the response that **hedges less** — z −5.6, and it is not length | [r193](13_normative_chain/r193_what_gets_flagged) |

---

## What the release does not ship

Six things, each of which blocks a question someone will want to ask.

| missing | consequence |
|---|---|
| criterion→response satisfaction labels | the published scoring cannot be reproduced; this repo rebuilds it with a local judge |
| lineage from a core criterion to its source | "did this criterion survive compilation" is a text-similarity guess (7.8% verbatim, 30.8% at 0.80) |
| authorship for multiply-rated criteria | 36% of the pool cannot be attributed, so "what people wrote" is 36% not what people wrote |
| where the four candidate responses came from | nothing supports a claim about model behaviour — only about these 4,312 texts |
| four documented demographic fields | race/ethnicity, country of origin, employment, self-description — collected per the card, never shipped, and the sanitization section does not mention it |
| any refusal in the response set | **5 of 4,312** candidates decline. The most contested question in alignment was never put to the panel. |

Full list, ordered by the concrete wrong answer each produces:
[`13_normative_chain/DEFECTS.py`](13_normative_chain/DEFECTS.py) — **6 blocking, 16 serious, 8 noted, 16 clean.**

---

## What this project got wrong

**13 withdrawn claims.** [`RETRACTIONS.md`](RETRACTIONS.md) has all 235 entries, each naming what killed it — the claim graph refuses a
retraction that names no killer.

The failure mode changed halfway. Early phases retracted **measurements**. From r175 on, the sweep
turned on its own output and retracted **descriptions of measurements that were correct**:

- *"the panel is concentrated in a few countries"* — 63% in three countries is right; the release
  publishes no sampling frame, so there is nothing to be concentrated *relative to*
- *"the scale is used as a near-binary"* — all 21 values are used, 4.04 bits of a possible 4.39
- *"length matters less on prompts with a right answer"* — **one prompt, counted 929 times**,
  produced the entire +4.9 points. Removing it collapses the effect tenfold.

That last one is entry 230, and it caused entry 231: a **retraction of a retraction**, where the
verdict was right and the stated mechanism was false.

**Two tools exist because of it.** [`covalx/estimand.py`](covalx/estimand.py) refuses a mean over
grouped data until the caller says whether the unit is the observation or the group.
[`covalx/robust.py`](covalx/robust.py) is a calibrated jackknife whose verdict is three-valued,
because its own threshold turned out to be a distribution. Both failed their first attack; both
attacks are in the repo.

---

## Navigating

| phase | rounds | n | what |
|---|---|---|---|
| [01](01_object_and_rebuild) | r1–r9 | 9 | rebuild the missing satisfaction layer |
| [02](02_attribution_under_attack) | r10–r22 | 13 | does the own-rubric advantage survive attack |
| [03](03_person_or_pair) | r23–r32 | 10 | person-level vs pair-level structure |
| [04](04_what_core_is) | r33–r37 | 5 | what the compiled core actually is |
| [05](05_human_protocol_and_power) | r38–r45 | 8 | the elicitation protocol and its power |
| [06](06_the_judges_mechanism) | r46–r59 | 14 | what the satisfaction judge is using |
| [07](07_floors_for_the_counterfactuals) | r60–r72 | 13 | floors under every counterfactual |
| [08](08_direction_from_text) | r73–r84 | 12 | recovering criterion direction from text |
| [09](09_form_donor_draw_and_unit) | r85–r94 | 10 | form, donor, draw and unit |
| [10](10_meta_separator_and_triage) | r95–r99 | 5 | layer separability |
| [11](11_reliability_and_the_width_chain) | r100–r109 | 10 | reliability and the width chain |
| [12](12_compilation_redistribution) | r110–r141 | 31 | compilation redistribution |
| [13](13_normative_chain) | r142–r205 | 62 | end-to-end normative preservation, then self-audit |

**Three generated consolidators** — each re-derives from the data on every run, so a number in one
that disagrees with a round means the *round* is stale:

- [`13_normative_chain/DEFECTS.py`](13_normative_chain/DEFECTS.py) — every defect, by the wrong answer it produces
- [`13_normative_chain/HEADLINES.py`](13_normative_chain/HEADLINES.py) — every headline mean under both estimands
- [`db/ledger.py`](db/ledger.py) — the claim graph: standing, withdrawn, and every kill edge

---

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install numpy   # that is the whole dependency
.venv/bin/python 13_normative_chain/DEFECTS.py        # the defect list
.venv/bin/python 13_normative_chain/HEADLINES.py      # every headline, both units
.venv/bin/python 13_normative_chain/r178_rubric_versus_length/run.py
```

Every round is a self-contained `run.py` writing `results/*.json`. Rounds that need the rebuilt
satisfaction tensor read `01_object_and_rebuild/r04_rebuild_satisfaction/results/`. The claim graph
needs PostgreSQL and `psql` on PATH; everything else needs only numpy.

---

## Boundaries

**Everything routing through the judge is a claim about that judge.** The satisfaction layer is a
locally rebuilt Qwen3.5-2B-Base reading `sigmoid(logit(" Yes") − logit(" No"))`. Where a comparison
holds the judge fixed on both arms — which is most of them — a judge bias cannot produce the
result. Where it does not, the claim says so.

**The prompts are synthetic and single-turn** (90.9%), median 128 characters. Whether anything here
transfers to production traffic is untested, and this project withdrew the claim that it does not.

**One prompt was rated by 929 people** against a median of 14, and its text is garbled. It carries
79% of all annotator pairs in the corpus. Any statistic averaged over assessments rather than
prompts is substantially a statement about that one prompt — which is how this project's one
fabricated finding happened.

**Nothing here is a claim about the people.** Group-level numbers compare a group to its
co-panelists on the same prompts; "unserved by the plurality" and "departs from the majority" are
the same event, so a group's apparent disadvantage is partly its own dissent rate.

---

## Attribution

CoVal is OpenAI's release: [dataset](https://huggingface.co/datasets/openai/coval). This audit is
independent and not affiliated with OpenAI. Errors here are mine, and 235 of them are written down.

*The previous README — a chronological research diary, 1,433 lines — is in git history:*
`git show 6a099d7f34:README.md`
