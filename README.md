# CoVal Crossroads

**What does a public-input values rubric actually measure, and at what scope?**

> ⚠ This repository's original subtitle was *"Does a public-input values rubric actually measure
> values?"* — the framing this project withdrew and then left standing as its own headline for
> fourteen turns. The contrast every number here computes is **own-rubric minus reference-rubric
> performance**: a comparison between two rubrics, never between rubric content and its absence.
> Whatever an unrelated prompt's rubric recovers is itself made of accuracy, clarity, caution,
> non-deception, relevance and proportionality — norms, not the lack of them. The correct name is
> **source specificity**, and the layer table below is what replaced the question.

An independent, reproducible audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to contentious prompts *and wrote down the criteria they judged by*.

The release ships prompts, four candidate responses, crowd-written value rubrics and 18,384 human rankings — **two per assessment: a *personal* ranking and a *world* ranking**, and every number in this repository is measured against the **world** one (`covalx/judge.py:245`, `ranking_blocks["world"]`). It does **not** ship the criterion-by-response satisfaction labels, so its published scoring cannot be reproduced. This repository rebuilds that layer locally, measures its concordance with the released rankings, and then asks what the rubric is actually made of — layer by layer, since a rubric is a measurement program `M(R, J, π, Q, P)` rather than a value function.

> **⚠ Scope correction, 2026-07-28.** Earlier versions called the 80,542 pairs "held-out human
> preference". They are **pairwise decompositions of the same rankings**, on the same prompts and the
> same four candidates the criteria were written about, by participants who had already ranked them.
> Holding out individual *pairs* does not break that dependence. OpenAI ran a **separate** validation
> study with new raters and new completions precisely because the original rankings are unsuitable for
> out-of-sample rubric validity. So r04 establishes **internal reconstructive concordance on the
> elicitation manifold** — which is real and useful — and not out-of-sample human preference validity.

---

> ### ⚠ The outcome variable is the WORLD ranking, and that was never stated
>
> CoVal asked each participant for **two** orderings of the same four responses: a **personal**
> one — *"according to their own personal values and preferences"* — and a **world** one — *"what
> would be best for the world overall (a more impartial or societal perspective, rather than just
> their personal taste)"* (`data/DATASET_CARD.md`, task flow).
>
> **This project has used the world ranking throughout.** `covalx/judge.py:245` reads
> `ranking_blocks["world"]`; the function's own docstring says *"strict pairwise preferences from
> world rankings"*. So **0.686**, **+0.102 → −0.064**, **+0.0576** and every other concordance
> number here means *agreement with what people said is best for the world*, **not** *agreement
> with what people preferred*.
>
> Neither this README nor `PREREGISTRATION.md` said so until now. The personal ranking is present
> for **26.7%** of assessments (4,901 of 18,384) and **has never been used in this project** — an
> entire second outcome, and the one that speaks directly to the distinction the reframed object
> rests on:
> a preference ordering and a normative ordering are different objects, and only one of them has
> been measured.

## The object, layer by layer

A CoVal rubric is not a value function. It is a **scoped, compiled, context-indexed normative
measurement program** — `M(R, J, π, Q, P)` — and each layer needs validating separately. This
table is the project's state; every cell points at the round that settled or failed to settle it.

| layer | what it is | established | **not** established |
|---|---|---|---|
| **R** rubric | the criteria and their weights | the own-rubric advantage is **semantic, not lexical** — `advantage_retained_under_paraphrase` = **0.9739** ([r20](rounds/r20_paraphrase_transfer)), on paraphrases whose fidelity [r14](rounds/r14_paraphrase_gauge) filtered at **99.1%** kept (`fidelity_kept.model` = 0.99116). Post-ranking **polarity** is the largest predictive channel, and *how much* depends on how you ask: adding sign **last to text alone** is worth **+0.0876** — 47% of the above-chance signal ([r32](rounds/r32_channel_decomposition)) — while its **Shapley value averaged over all 16 coalitions is +0.0214**, or 12% ([r36](rounds/r36_channel_shapley)). ⚠ r36's own verdict says r32's figure *"was the value of adding sign LAST to text alone — one path through the lattice, not the channel's average worth"*, so **"roughly half" is the maximum over entry orders, not the channel's contribution**, and it transfers across people even on **private** write-in criteria ([r49](rounds/r49_provenance_crossfit)) | **what the polarity IS.** No rater in the release rated a criterion before seeing four responses, so a response-blind direction is unreachable — that is **S_pre**. Also: r34–r37 and r43 are computed on the **pre-seeded 36.5%** of criteria, not the participant-authored remainder ([entry 51](RETRACTIONS.md)) |
| **J** judge | the satisfaction instrument | reconstructs the missing satisfaction layer well enough to reach **0.686** pairwise concordance on 80,542 pairs ([r04](rounds/r04_rebuild_satisfaction)) — ⚠ **internal reconstructive concordance on the elicitation manifold**, not held-out human preference, per this file's own scope correction above; three unrelated lineages agree in direction ([r39](rounds/r39_feature_cache), [r40](rounds/r40_ood_map)) | **a measured defect, not a gap:** it reads lexical overlap — **+0.2068** correlationally ([r51](rounds/r51_judge_lexical)) and **+0.2507 causally** under intervention ([r52](rounds/r52_overlap_intervention)). Whether that is *error* is unknown: the release has no satisfaction ground truth to set the ceiling. Accuracy on generated responses is unvalidated |
| **π** protocol | how criteria were elicited and rated | the seed/write-in partition is **exactly identified** — 0.1% in the gap, six pre-seeded per prompt ([r48](rounds/r48_provenance_identified)). Concordance is **robust to post-hoc abstention** ([r35](rounds/r35_polarity_abstention)) | **the forced-choice effect at elicitation time.** The scale runs −10..+10 and 0 appears **once in 102,147 ratings**, so "no general direction" was never available to a participant. Filtering afterwards cannot simulate having had the option |
| **Q** responses | which response distribution is scored | the own-rubric advantage **does not transfer** to responses the criteria authors never saw — +0.102 → −0.064 ([r12](rounds/r12_response_set)), replicated on 250 untouched prompts at +0.085 → −0.072 ([r46](rounds/r46_spread_replication)) | **whether that is about rubrics or about proxies.** The outcome is a model gold head that reads length (+0.077 → +0.458 across response sets), and **roughly half the inversion rides on that channel** — 57% survives residualisation against the procedure's own null, and on held-out prompts the fresh arm **stops being negative** once length is removed ([r47](rounds/r47_gold_is_length)). So *"the advantage does not transfer"* replicates; *"an unrelated rubric beats it"* does not, and every mechanism tested — generic distance, criterion novelty, spread loss, overlap — has failed or failed to replicate. That is **H_fresh** |
| **P** population | whose values are measured | no aggregate loss in the splits tested, and **equivalent to zero at δ = 0.01** rather than merely non-significant ([r37](rounds/r37_leakage_topology), [r42](rounds/r42_equivalence)) — ⚠ δ is **stipulated, not measured**, and r42's own verdict says the nulls hold *"at this margin and at no other"*: **12/21 contrasts are equivalent at 0.01, 7/21 at 0.005, 4/21 at 0.0025**, and r42's population was **four hand-listed rounds, not the package** — enumerating gives 125 interval contrasts ([r58](rounds/r58_equivalence_census)) | **value constituencies**, and **that the population nulls are equivalence rather than silence.** Country sign-reversals exceed a label-permutation null (+0.0190) but **0 of 17** group tests survive BH correction, splitting 2 positive / 2 negative — symmetric noise ([r43](rounds/r43_criterion_heterogeneity)). ⚠ **9 of r43's group cells are INCONCLUSIVE at δ=0.01** — non-significant *and* not bounded inside the margin, so for those cells "no group is predicted better by its own weights" is an absence of detection, not a demonstration of absence ([r58](rounds/r58_equivalence_census)). These are demographic proxies, not constituencies |

**What ties the "not established" column together.** Four of the five gaps are the *same three*
counterfactuals: **S_pre** (R), **H_fresh** (Q), **τ_c** — the causal effect of intervening on one
criterion, which no observational contrast in this release identifies. π's gap needs a neutral
option on the screen at elicitation time, which is S_pre's PRE arm. **None of them is computable
from this release**, and **64 rounds with published results** establish that by exhausting the alternatives rather than by
assertion.

⚠ One cross-cutting scope note that belongs on every row: the per-prompt attribution drop these
rounds correlate against has **split-half reliability 0.302–0.422** ([r57](rounds/r57_outcome_reliability)),
so any mechanism with a true per-prompt correlation below ≈0.2 is invisible to all of them
([entry 55](RETRACTIONS.md)).

## Headline

**What is robust here is an ordering, not a share.** Grading responses against **an unrelated
prompt's rubric** already recovers most of the apparent signal.

| grading the same responses with… | concordance with the original human rankings |
|---|---:|
| the real, prompt-specific rubric | **0.686** |
| an unrelated prompt's rubric | 0.607 |
| response length alone | 0.532 |
| chance | 0.500 |

That ordering holds across every judge and every floor tested. **The split of the 18.6 points above
chance does not.** Against a randomly chosen prompt as the floor it is 7.9 / 10.7 — but that is one
cell of a grid, and the grid spans a factor of twenty:

- the **floor donor** moves it **2.47×** ([r19](rounds/r19_floor_choice))
- the **judge family** moves it **2.13×** on top of that — derived from [r30](rounds/r30_scope_grid)'s shares (53.8% qwen2.5-3b ÷ 25.3% phi), *not* a value r22 stores
- with an interval in every cell, source specificity runs **3.2% – 65.8%** ([r30](rounds/r30_scope_grid))

So **7.9 and 10.7 are not two quantities, they are one cell**, and the second is *not* identified as
"generic quality" by anything measured here — [r59](rounds/r59_criterion_influence) finds criteria
borrowed from other prompts are just as concordant about these responses as a prompt's own, which is
consistent with a shared normative backbone and with several other things. **The contrast is
own-rubric minus reference-rubric performance, and naming its parts is an interpretation, not a
measurement.**

**That floor is a choice, and the number moves 2.47× with it.** [r19](rounds/r19_floor_choice)
reads r10's donors as a decay curve: a random prompt's rubric still retains 47–60% of the signal,
because a random prompt sometimes shares topic. Grading against a nearest-topic donor instead gives
attribution 0.047; against the most dissimilar donor, 0.115.

Measured on r10's 300-prompt panel, excluding one judge cell whose own accuracy (0.5405) sits too
close to chance to be decomposed at all:

| floor | attribution | relative to the random floor |
|---|---:|---:|
| nearest-topic donor | 0.047 | ×0.64 |
| random donor *(what the headline used)* | 0.073 | ×1.00 |
| most dissimilar donor | 0.115 | ×1.58 |

Applying that range to the 42.5% prompt-specific share of the random-floor cell gives **27%–67%**
— **floor variation alone**. Crossing it with the judge dimension — 2.13×, derived from r30's own shares — is
what produces r30's **3.2%–65.8%**, and that is the figure any single number must be read against.

Neither endpoint is clean — the far donor is adversarially selected and may simply be refused by the
judge, the near donor shares topic. **The generic-quality floor is bracketed, not measured, so any
single figure must name its floor.**

### The exhaustion ledger — every mechanism proposed for r12's inversion, and what happened to it

The claim that these rounds *"exhaust the alternatives"* is only meaningful if the alternatives can
be listed. They can. **A list bounds exhaustiveness from below and can never prove it** — no
enumeration shows that no other mechanism exists — so this is the set that was proposed and tested,
not a proof that the set is complete.

| # | proposed mechanism | round | outcome |
|---|---|---|---|
| 1 | criteria memorise the four candidate **strings** | [r13](rounds/r13_seed_vs_writein) | **refuted** — participant-blind seeds carry +0.046 [+0.023, +0.069] |
| 2 | criteria are merely **topic**-specific | [r15](rounds/r15_indistribution_transfer) | **refuted** — near-topic criteria +0.018 [−0.001, +0.037]. ⚠ r15's own verdict: this does **not** resolve r12 |
| 3 | fresh responses are **off-distribution** by generic distance | [r40](rounds/r40_ood_map) | **refuted, and inverted** — the drop is worst at *short* distance, r=−0.125 |
| 4 | fresh responses leave the rubric's **criterion-space support** | [r41](rounds/r41_criterion_support) | **confounded** — hull violation −0.1837 does not survive the discriminating-power control |
| 5 | the rubric loses **discriminating power** on fresh responses | [r41](rounds/r41_criterion_support) → [r46](rounds/r46_spread_replication) | **failed to replicate** — +0.2309 discovery, +0.0496 [−0.068, +0.169] held out |
| 6 | the **gold head is unstable** off-distribution | [r29](rounds/r29_gold_ood) | **refuted** — 0.590 fresh vs 0.543 original. ⚠ reliability, not validity |
| 7 | the **gold head reads length** | [r47](rounds/r47_gold_is_length) | **PARTLY CONFIRMED** — ~half the inversion rides on it; the "unrelated rubric beats it" reading is withdrawn |
| 8 | the **judge scores lexical overlap** (correlational) | [r51](rounds/r51_judge_lexical) | **confirmed as a channel** — +0.2068 vs a −0.0034 null |
| 9 | …and **causally** | [r52](rounds/r52_overlap_intervention) | **confirmed** — +0.2507 [+0.2300, +0.2714] under intervention |
| 10 | that overlap channel **explains r12** | [r54](rounds/r54_overlap_transfer) | **refuted** — real, but does not predict *which* prompts drop (−0.0736 [−0.2059, +0.0612]) |
| 11 | its **ordering component** explains r12 | [r55](rounds/r55_overlap_selectivity) | **refuted** — collapse +0.0002 [−0.0056, +0.0059], equivalent to zero at δ=0.01 |
| 12 | **semantic selectivity** collapse explains r12 | r56 | **failed to replicate** — ⚠ and r56's numbers have no artifact; [r66](rounds/r66_r56_reconstruction) could not recompute them |
| 13 | criteria carry **independent** normative content | [r59](rounds/r59_criterion_influence) | **refuted** — they are concordant, and *not* own-rubric-specifically (14.7% vs 14.9% borrowed) |

**⚠ Read every "refuted" in rows 3, 4, 5, 10 and 12 against a floor, and the floor is not one
number.** [r57](rounds/r57_outcome_reliability) measured the per-prompt attribution drop's split-half
reliability at **0.302 / 0.422**. Each correlational row's own published interval gives its own
detection floor — the smallest |r| it could have separated from zero:

| row | half-width | floor, predictor assumed perfect | **floor, predictor reliability measured** |
|---|---:|---:|---:|
| 3 · generic distance (r40) | 0.0988 | 0.180 | **0.188** ⚠ⁿʳ |
| 4 · criterion-space support (r41) | 0.1010 | 0.184 | **0.224** |
| 5 · spread loss, held out (r46) | 0.1175 | 0.214 | **0.260** |
| 10 · overlap transfer (r54) | 0.1336 | 0.243 | **0.367** |

*(at r57's pessimistic outcome reliability, 0.302)*  ·  **⚠ⁿʳ = not regenerable.** Row 3's 0.188 divides by r68's 0.9132, which was computed from r39's cached encoder features. One of those three lineages (internlm) **cannot be rerun in this environment** — it returns 100% NaN under transformers 5.14.1 — and no receipt records the environment that produced the cache ([r80](rounds/r80_panel_freeze), entries 134–135). The number is not impugned; it is **unrepeatable on this machine**, which is a different and quieter status than the rest of this table carries.

**A criterion's direction is recoverable from its wording — but only when the wording was written after seeing the responses.** [r73](rounds/r73_direction_from_text_alone) predicts sign(mean score) from criterion text alone, prompts held out entirely, no response and no judge entering the computation. Because the two provenance classes have very different marginals, the honest comparison is the share of *available headroom* each captures:

| class | n | marginal | held-out accuracy | above marginal | headroom captured |
|---|---:|---:|---:|---|---:|
| **seeds** — pre-written, response-blind, shown to every rater | 5,506 | 0.8400 | 0.8420 | **+0.0020** [−0.0007, +0.0049] | **1.2%** |
| **write-ins** — authored after reading all four responses | 9,683 | 0.6886 | 0.7707 | **+0.0821** [+0.0746, +0.0904] | **26.4%** |

**The seed result is not a generalisation failure.** Its *in-sample* fit reaches only +0.0160 above marginal — the pipeline cannot learn direction from response-blind criterion text even when allowed to memorise it, which bounds the learnable signal rather than reporting a held-out miss. Both nulls ran first: shuffling labels inside training collapses every arm to its marginal (−0.0006, +0.0000, −0.0026), and the write-in margin survives the phrasing-convention control — restricted to the 7,266 criteria with no overt negation marker it is **+0.0954**, larger, not smaller.

**So text-recoverable direction is a product of exposure, not evidence against it.** A rater who has read the four responses writes the direction into the sentence; a criterion drafted before anyone saw them does not carry one. ⚠ This does **not** contradict the R-layer row above, and does not measure S_pre: no person in this release rated anything pre-exposure, and nothing here can see whether they held a direction. What it removes is the reading that text-predictability would have demonstrated one. **For the preregistration it is a positive result** — S_pre's PRE arm faces exactly the response-blind seed class, where a text-only predictor adds **1.2% of headroom**, so r61's chance baseline needs no adjustment there. Any arm built on **write-in** text would need one.

**And underneath every floor sits a proxy that was validated once, and the validation was never read out.** Every row above scores its outcome with the r08 model gold head, and says so. The release does contain **real human rankings** for the four released candidates, so on the *original* arm the proxy is checkable — [r47](rounds/r47_gold_is_length) computed that check, stored it as `proxy_validation_on_original`, and **its numbers appear nowhere in this document**. [r72](rounds/r72_proxy_validity_coefficient) recomputes them independently (the gold side reproduces r47's stored 0.1020 exactly) and reports the two halves the process rules require to be kept apart:

| | gold head | real humans | human − gold |
|---|---:|---:|---|
| attribution, original arm | +0.1020 | +0.0876 | **−0.0144** [−0.0392, +0.0086] |

**Significance and equivalence disagree, and only one of them was ever quoted.** The difference does not differ from zero — which is what r47's stored `differ: False` records. It is **not equivalent** at the preregistered δ=0.01: the 90% interval [−0.0344, +0.0060] is **2.0× wider than the margin**, and the point estimate alone is **1.4× the margin**. So `differ: False` is a non-result, not the reassurance its phrasing invites.

**The number that matters more is the per-prompt one: the validity coefficient is 0.6029** — the gold-scored and human-scored attributions share about **36%** of their variance across prompts, and per-prompt is the resolution at which every correlational row in the ledger operates. ⚠ **It is deliberately NOT applied to those rows as a third attenuation term.** Their outcome is the *drop* (original − fresh); this coefficient is measured on the original attribution alone, because the release has no human rankings for generated responses. Carrying it across that boundary would be the error of entries 110, 119 and 120 a fourth time — and here the boundary is not crossable by any recomputation, only by **H_fresh**. What it does establish is that the proxy is validated exactly where it is least stressed, the same asymmetry r47 identified for its length channel.

**The other half of every floor was audited too, and it holds.** Each floor divides by `rel_predictor × rel_outcome`, and the outcome term is [r57](rounds/r57_outcome_reliability)'s single number applied to all four rows — the same shape as the predictor mistake above. It is legitimate here: r40, r41, r46 and r54 all correlate against **the same quantity r57 measured**, the per-prompt attribution drop, and each row's half-width comes from that round's *raw* arm, not a partialled one. One imprecision found and not worth a correction: row 4's verdict (*confounded*) is carried by r41's length-and-spread-controlled arm, half-width **0.1028**, while the table used the raw arm's **0.1010** — a floor of 0.231 rather than 0.227. The rule it illustrates is worth more than the number: **a floor must be read off the arm that carries the verdict.**

**[r67](rounds/r67_predictor_reliability) measured the missing term.** The middle column takes the
**predictor** as perfectly reliable — stated as a lower bound when it was published. Splitting each
prompt's criteria 2-2 and recomputing gives a Spearman-Brown reliability of **0.657** — re-measured
over 200 random splits by [r71](rounds/r71_r67_split_variance) at **0.6751**, which multiplies
**r41's and r46's** floors by **1.217×**. ⚠ **That single number was applied to two rows
whose predictors it never measured, and it was wrong in both directions.**
[r68](rounds/r68_r40_predictor_reliability) measures r40's at **0.9132** — far above it — and
[r69](rounds/r69_r54_predictor_reliability) measures r54's at **0.4381**, far below. So **r54's
floor is 0.367, not 0.300**: it could not have detected a true correlation below ≈0.37, and
*"the overlap channel does not explain r12"* rules out even less than the previous version of this
paragraph said. **A ledger-wide reliability is not a conservative simplification** — it moved one row
up and one row down, and only measuring each predictor separately says which. ⚠ **r40's floor is
measured, not assumed, and the 1.23× never applied to it.** Its predictor is an
embedding distance with no criteria to split, so r67's criteria-split reliability does not
transfer. The right estimator is agreement between **instruments**, and
[r68](rounds/r68_r40_predictor_reliability) computes it from r39's cached representations:
recomputing the per-prompt distance in each of three unrelated pretraining lineages gives
pairwise agreements of **+0.9023, +0.7234, +0.7085** (mean +0.7781, Spearman-Brown **0.9132**).
A highly reliable instrument, so the floor is **0.188** — below the assumed-perfect 0.180 only by
the small correction reliability 0.91 implies, and **well below the 0.222 an earlier version
published**. Row 3 is the strongest refutation in this table, not the vaguest.
⚠ **And it is not regenerable.** One of those three lineages (internlm) returns 100% NaN under
transformers 5.14.1, so this agreement **cannot be recomputed on this machine**, and no receipt
records the environment that produced r39's cache ([r80](rounds/r80_panel_freeze), entries 134–135).
The strongest row in the table is also the only one whose reliability input is unrepeatable — those
two facts belong in the same sentence, which is why this clause exists.

**Those rows say "not detected above their own floor", not "absent".** Rows 1, 2, 6, 11 and 13 rest
on tightly-bounded contrasts rather than correlations and do not inherit this limit.

**What survives:** the inversion replicates (+0.102 → −0.064; held out +0.0847 → −0.0716), the
outcome variable carries roughly half of it (row 7), and **nothing proposed explains the remainder**.
That is the state H_fresh exists to resolve.

### r12's inversion is worst where the fresh responses look MOST like the released ones

The easiest explanation for r12 — the rubric's advantage inverting on fresh responses — is
that the judge and the preference proxy are being asked about text unlike anything they were
validated on. That predicts a specific geography: **the anomaly should grow with distance from
the original support.**

[r39](rounds/r39_feature_cache) caches representations of all 2,000 responses from **three
unrelated pretraining lineages** (Qwen · Phi · InternLM) in one GPU pass and analyses nothing.
[r40](rounds/r40_ood_map) does the map on CPU, with the PCA basis fitted on **original
responses only** so fresh ones cannot define the space they are then measured in.

`drop = attribution(ORIGINAL) − attribution(FRESH)`, so **positive** r means the anomaly grows
with distance and **negative** r means it is worst where fresh responses most resemble the
released ones.

| distance measure | r per lineage | sig | same sign |
|---|---|---:|---|
| **nearest neighbour** | **−0.132, −0.143, −0.101** | **2/3** | **yes** |
| log-likelihood gap | −0.139, −0.099, −0.059 | 0/3 | yes |
| Mahalanobis | −0.046, +0.043, +0.180 | 1/3 | **no** |
| conditional ll gap | −0.014, −0.033, +0.005 | 0/3 | no |

**The sign runs the wrong way for the simplest measurement-failure story.** The discrepancy
*shrinks* as fresh responses move away from the original support and is worst on the ones that
look most like the released candidates.

**⚠ The defensible statement is narrow: the discrepancy is not explained by monotone degradation
under the three generic distance metrics tested.** It says nothing about whether the judge is
still accurate on fresh responses, whether the preference proxy is still valid there, or whether
the responses sit inside the rubric's own **criterion-satisfaction support** — which is the
distance that actually matters. A fresh response can be close in embedding, style, length and
likelihood while combining criterion satisfactions that no original candidate exhibited. Generic
embedding distance cannot see that. **[r41](rounds/r41_criterion_support) now measures it, and
the answer is that criterion space does not explain r12 either** — see below.

The effect is small (|r| ≈ 0.13) and this is a single axis, so it does **not** establish
genuine transport failure — it removes the easiest alternative to it. Two consequences follow.
**Mahalanobis disagrees in sign across lineages, so it is a property of a representation, not
of the responses** — which is exactly why every distance is reported per lineage and never
averaged. And **the human sample must not be drawn from the far tail**, where the anomaly is
mildest.

⚠ Length is partialled out throughout, because fresh responses are systematically *longer*
(89 vs 76 median words) — the 180-token cap never bound, and the released candidates are the
short ones.

### The inversion is at least partly a property of the gold proxy, not the rubric

r40, r41 and r46 each tested a property of the **rubric** and each came back empty. None tested
the **outcome variable**. r08's gold head is `hstack([embedding, [char_len, word_len]]) @ w` —
length is one of its *inputs*, at |w| = 0.2085 against a mean embedding weight of 0.0620.

Fresh responses vary **3.4×** more in length than the released candidates (word-count sd 34.2–34.4
vs 10.1–10.2), and gold's within-prompt correlation with length tracks that, on **both** samples:

| | discovery (250) | held out (250) |
|---|---:|---:|
| corr(gold, word count), **originals** | +0.0770 | +0.0259 |
| corr(gold, word count), **fresh** | **+0.4579** | **+0.5482** |

⚠ Read the *signed* correlation, not the magnitude. At four responses per prompt, two
**independent** vectors already give E|r| = 0.5005, so a raw |r| of 0.62 is mostly the sample
size — the excesses are only +0.104 and +0.192. An earlier version of this section quoted the
bare magnitudes (entry 49).

**A prescient caveat, filled in eighteen rounds later.** [r29](rounds/r29_gold_ood) had already
asked whether the gold head is unstable off-distribution and found it is not: two independently
fitted heads agree about as well on generated responses (0.590) as on released ones (0.543). It
recorded its own limit — *"RELIABILITY only — the two heads share an architecture and an embedding
model, so a bias common to both is invisible here."* r47 is that bias: **length is an explicit
feature of the shared architecture**, so both heads read it and their agreement could never have
revealed it. Two heads agreeing is not two instruments.

**The proxy is sound where it can be checked — which is the wrong place.** Human rankings exist
only for the original candidates, so:

| | discovery | held out |
|---|---:|---:|
| attribution vs GOLD | +0.1020 | +0.0853 |
| attribution vs HUMAN rankings | +0.0876 | +0.0742 |
| difference | −0.0144 [−0.0376, +0.0095] | −0.0112 [−0.0355, +0.0132] |

Indistinguishable in both, per-prompt r = +0.60 and +0.65. And humans do **not** systematically
prefer longer responses there (signed +0.041, CI spans zero). So the proxy is validated exactly
where its length channel is weakest, and applied where it is strongest.

**Removing length, against the procedure's own null.** Residualising four responses on *any*
variable removes one of three degrees of freedom and costs ≈0.025 by itself, so
length-residualisation is measured against **noise**-residualisation rather than against raw:

| | discovery | held out |
|---|---:|---:|
| inversion, raw | +0.1660 | +0.1460 |
| inversion, noise-residualised (the null) | +0.1303 | +0.1153 |
| inversion, **length**-residualised | +0.0833 | +0.0567 |
| share surviving vs the null | 64.0% | 49.1% |

**And the sharpest point does not replicate**, which is itself the finding:

| fresh arm, length-residualised | discovery | held out |
|---|---:|---:|
| | −0.0307 [−0.0567, −0.0053] | **+0.0047 [−0.0213, +0.0320]** |

On the held-out sample the fresh arm stops being negative once length is removed. So **"the own
rubric is *beaten* by an unrelated one on generated responses" — the bizarre claim that made r12
worth chasing — is not established.** What replicates across both samples is the ordinary one:
the own-rubric advantage **does not transfer**. The inversion itself is at least partly length.

**Consequence for the human experiment:** r12 cannot be cited as evidence of rubric transport
failure without recording response length, and H_fresh must collect it.

### Criterion space is a different axis from embedding space, and it does not explain r12 either

A rubric does not measure responses where an embedding does. It measures them in the space its
own criteria span:

```
z_R(r) = ( s(c₁,r), …, s(c_K,r) )        s ∈ (0,1)
```

r12 computed that tensor and threw it away on the line that aggregated it
(`rounds/r12_response_set/run.py:152`). [r41](rounds/r41_criterion_support) rebuilds it on the
**saved** fresh responses — no regeneration, because r12's generation is stochastic and unseeded
and a re-run would replace the response set r39/r40/r41 are all built on.

**The rebuild had to prove it was r12's instrument, not a lookalike.** bf16 batched inference is
composition-dependent; a last-bit difference flips a near-tied pairwise comparison and moves a
per-prompt accuracy by 1/6. So the pass rescores in r12's exact task order at r12's exact batch
size, including the shuffled arm it never uses, purely to keep batch composition identical.
**All 1,500 published per-prompt values reproduce with max |diff| = 0.00e+00.**

| measure | length-controlled | **+ discriminating-power control** |
|---|---:|---:|
| hull violation (outside the originals' criterion support) | **−0.1837** (p=0.003) | −0.0653 (p=0.31) |
| rank instability under criterion bootstrap | **+0.1993** (p=0.002) | +0.0793 (p=0.21) |
| criterion-combination novelty, thresholds 0.3–0.7 | flat at every threshold | flat |
| cross-lineage judge disagreement (qwen vs phi) | +0.0550 (p=0.38) | +0.0345 (p=0.60) |

**Both survivors die to one control, and it is the control the result demanded.** A rubric that
cannot *separate* the four fresh responses must score near chance against gold — so "unstable
ranking" and "large drop" risk being two views of one quantity rather than a relationship
between two. Partialling out the rubric's own score spread removes both effects, and their
correlations with that spread are **+0.563** and **−0.597**. The geometry collapses into a single
fact: **the rubric separates the fresh responses less than it separated the originals**
(corr with the drop = −0.2246).

**One criterion-space quantity looked like it survived — and it did not replicate.**
`D_spread_loss`, how much *less* the prompt's own rubric separates the fresh responses than it
separated the originals, reached **+0.2309** length-controlled (p = 0.0010) on r12's 250 prompts:
the largest effect in the round, orthogonal to embedding distance (−0.056), surviving a donor-arm
control (+0.2693 while the donor alone gave −0.0351 ns), recovered independently by a second judge
lineage (phi, +0.1724), and not attributable to the fresh responses being more homogeneous — they
are measurably *less* alike (lexical self-similarity 0.083 vs 0.108) and *more* spread by the gold
head (3.44 vs 2.00).

It entered as a nuisance control and was promoted to a measure after it explained the others, so
it was labelled **exploratory** and a numeric prediction was committed to git *before* testing it
on prompts nothing in this project had touched.

**[r46](rounds/r46_spread_replication) tested it on 250 held-out prompts and it is gone:**

| | r12's 250 (discovery) | 250 held out |
|---|---:|---:|
| spread loss → drop, length-controlled | +0.2309 [+0.107, +0.343] | **+0.0496 [−0.068, +0.169]** (ns) |
| donor arm alone | −0.0351 (ns) | +0.0318 (ns) |

Predicted range was [+0.12, +0.34]. The result is outside it and the interval includes zero, which
is the declared **NOT REPLICATED** branch. Retraction entry 48 is downgraded to a single-sample
artifact: **the effect was found by selection and does not generalise.**

**What that costs, and what it does not.** Four separate checks agreed with the effect — donor
control, second judge lineage, two rubric-independent heterogeneity measures — and all four ran on
the *same 250 prompts*. Robustness to the instrument is not generalisation across samples, and
stacking same-sample checks felt like accumulating evidence when it was not. That is the lesson,
and it is worth more than the effect would have been.

**r12's phenomenon itself replicated cleanly**, which is the part that matters. On the held-out
prompts the own-rubric advantage is **+0.0847** on the original candidates (r12: +0.102) and
**−0.0716** on fresh ones (r12: −0.064). ⚠ **And the replication is stronger than "untouched
prompts" says** (entry 159): `data/comparisons.jsonl` is **perfectly ordered by collection form** —
lines 0–320 are long-form (world + personal + unacceptable), 321–1077 short-form (world only), with
**no interleaving**. r12 takes a head slice `[:250]`, so its prompts are **100% long-form**; r46's
held-out set at offset 250 spans file positions 280–556 and is **83.6% short-form**. So the inversion
survives a change of **collection instrument**, not merely a change of prompts — and since no prompt
exists under both forms (entry 158), that is the only cross-form evidence this release can supply.
The inversion is real, independent of the specific
prompts, and **still unexplained** — generic distance (r40), criterion-space novelty (r41) and
now discriminating-power loss (r46) have each been ruled out.

The round still earns its cost. Criterion space correlates with generic embedding distance at
only **+0.25** and **+0.19** — roughly 5% shared variance — so this was a genuinely different
axis and it is now checked rather than assumed. And **two unrelated judge lineages disagree
0.0077 *less* on fresh responses than on the originals**, and their disagreement does not track
the drop, so the discrepancy is not where the judges fall apart. That is a non-rejection of the
judge-incoherence reading, **not** an exclusion of it: two lineages can be wrong the same way.

⚠ Everything here is **judge-relative**. `z_R` comes from the same judge whose off-distribution
validity is the open question, so this round cannot separate *"fresh responses occupy new
normative territory"* from *"the judge scores them incoherently"*. It establishes that the
discrepancy is **not spatially organised** in criterion space. r12 remains unexplained.

### Non-significance was doing the work of equivalence, in eleven places

Several load-bearing statements here are **null claims** — "no detected loss", "costs nothing
measurable", "the decay is flat". Every one was read off a non-significant result, which says
the study could not see an effect, not that one is absent.

Testing that needs the paired per-prompt vectors, and r34/r35/r36/r37 each bootstrapped one,
printed a 95% CI and discarded it — and a 95% CI is the interval for the *significance*
question, not for a TOST at α = 0.05. All four rounds take 4–23 seconds, so they were patched to
persist the vector and re-run; **all four reproduce their published numbers byte-identically.**

[r42](rounds/r42_equivalence) then tests `H₀: |Δ| ≥ δ` at δ = 0.01 over all **21** contrasts:

| | equivalent at δ | not equivalent |
|---|---|---|
| **significant** | 4 — real but negligible | 8 — real and material |
| **not significant** | 9 — no material effect | **0 — inconclusive** |

**Nothing lands in the inconclusive cell.** Every non-significant result in this package is also
*bounded* inside the margin, so the null readings survive — which is the first time that was a
finding rather than an assumption. The four "real but negligible" cells are the ones significance
alone would have misreported: `D_same_sample_premium` +0.0055, `A2` +0.0026, `φ_T` +0.0017, `φ_S` +0.0008.

⚠ **δ is a stipulation, not a measurement.** Nothing in the data says 0.01 accuracy points is
where a rubric becomes unfit, because no purpose has been specified that precisely. So the round
sweeps it, and the sweep is the honest form: **12/21 equivalent at 0.01, but 7/21 at 0.005 and
4/21 at 0.0025.** The nulls hold at the declared margin and at no tighter one.

Both controls ran before any row was read: `D_population` (+0.0576, 5.8× the margin) must return
NOT EQUIVALENT, and a zero vector must return EQUIVALENT. An equivalence test that cannot say
"not equivalent" reports every claim as tightly bounded, which is silence dressed as precision.

⚠ This is **aggregate** equivalence. A contrast can be equivalent in aggregate and heterogeneous
underneath — criterion-level sign reversals and minority-only criteria are
[r43](rounds/r43_criterion_heterogeneity), not this.

### The polarity rewrite is where core's advantage comes from — and membership carries some too

r33 found CoVal-core scored with **no ratings at all** beats CoVal-full by **+0.0663**. That is a
sum: the dataset card documents polarity rewriting, cleanup, semantic merging, compatibility
selection and truncation to ≤4, and nothing said which step did the work.

**The intermediate artifacts do not exist.** The release ships C0 and C6; C1–C5 live inside a
compiler OpenAI did not publish. So [r44](rounds/r44_compiler_lineage) cannot decompose that
compiler and does not claim to — it builds a **reconstruction** from the documented operations,
measures each simulated stage, and reports **the residual it cannot explain**.

| reconstructed stage | Δ | 95% CI |
|---|---:|---|
| **polarity rewrite** (see ⚠ below) | **+0.0733** | [+0.0647, +0.0822] |
| cleanup | +0.0052 | [+0.0029, +0.0075] |
| dedup | −0.0053 | [−0.0092, −0.0014] |
| compatibility selection | −0.0181 | [−0.0241, −0.0125] |
| **selection vs SIZE-MATCHED random** | **+0.0149** | [+0.0082, +0.0221] |
| total, full → **real** core | +0.0662 | [+0.0571, +0.0752] |
| **residual, reconstruction → real** | **+0.0112** | [+0.0039, +0.0184] |

The rewrite alone is **larger than the entire full→core gap**; later stages give part of it back.
The reconstruction accounts for **83%** of the total, and the +0.0662 independently reproduces
r33's +0.0663 through a different code path.

> **⚠ The +0.0733 is an upper bound on the rewrite, not a measurement of it.** `run.py:112` says so
> in its own comment — *"The text rewrite cannot be simulated; its EFFECT can"* — and implements the
> stage as `s1 = -1 if mean_train_rating < 0 else 1`: it **complements satisfaction using the crowd's
> rating sign**, on rater-disjoint folds. The real compiler has no such channel. It must encode
> polarity **in rewritten words** and hope a judge that never sees a rating recovers it — and
> [r65](rounds/r65_edit_symmetry_floor) shows the rewrite leaves **18.62%** of core criteria still
> phrased as prohibitions, *more* than the 12.85% in the un-rewritten full set. So +0.0733 measures
> **what having the polarity is worth**, and bounds from above what putting it into prose can achieve.

**Selection is damage control, not gain — and the two numbers must be read together.** The stage
itself **costs −0.0181** (0.6647 → 0.6465): truncating to four criteria throws information away.
Against a **size-matched random** choice of the same four, it recovers **+0.0149** (random lands at
0.6317). So choosing *which* items survive recovers most of what truncating to four destroys, and
does not repay it. Core encodes the post-choice ranking partly through **which items survive**, not
only through wording — but membership is a **mitigation of the compression, not a contribution on
top of it**.

Read as an arc: the polarity rewrite takes 0.5915 → **0.6648**, and every reconstructed stage after
it nets **−0.0183**, landing at 0.6465. The **real** core sits at **0.6577**, +0.0112 above my
reconstruction — which is the part of OpenAI's compiler this cannot see.

The identity control — a stage that does nothing — returns Δ = **0.000000**, so none of these
increments is re-scoring noise.

### Groups disagree about criteria, and it does not change which response wins

r42's equivalence is **aggregate**, which is exactly the result that can coexist with real
disagreement underneath. [r43](rounds/r43_criterion_heterogeneity) asks three questions of
country, generative-AI usage and age, and only the third can move a decision.

**The positive control comes first, because a heterogeneity detector that has never returned
"heterogeneous" cannot be believed when it returns "homogeneous".** Injecting a synthetic group
whose ratings are sign-flipped on a random 20% of criteria lifts the reversal rate from
**0.122 to 0.283**. The instrument works; a low rate on the real groups therefore means
something.

| axis | sign-reversal rate | label-permutation null | excess |
|---|---:|---:|---:|
| **country** | **0.2363** | 0.2172 [0.2087, 0.2247] | **+0.0190, above** |
| generative-AI usage | 0.2177 | 0.2158 [0.2081, 0.2247] | +0.0018, inside |
| age | 0.2012 | 0.2033 [0.1945, 0.2109] | −0.0022, inside |

The null permutes **group labels within each (prompt, criterion)**, holding cell sizes and the
rating multiset fixed, because with a handful of raters per cell sign disagreement happens by
sampling alone and a raw reversal rate is uninterpretable.

**But the decisive question is whether a group's own weights predict that group better**, and
they do not. Across 17 group tests — rater-disjoint folds, pooled arm subsampled to the same
number of raters so the shared rubric cannot win on sample size — **0 survive Benjamini-Hochberg
at q = 0.05.** Uncorrected, 2 are significantly positive and **2 significantly negative**; a
group predicted *worse* by its own weights has no mechanism, so that symmetry is what the noise
distribution looks like, and quoting only the positives would be reporting half of it.

So: **countries do assign opposite signs to the same criterion more often than chance, and it
does not change which response wins.** The aggregate equivalence is not hiding a decision.

⚠ These are **demographic proxies, not value constituencies** — r16–r18's latent partition was
frozen precisely because it named no constituency, and using country instead makes the label
honest without making it the right object. Scoped to raters with an annotator record
(87.2%). And the "minority-only criteria" measure at a 90% concentration threshold **never
fires**, so its zero is reported as **inert**, not as evidence: the largest group supplies on
average 0.40–0.46 of a cell's raters, p95 0.57–0.66.

### The human experiment is frame-limited, not power-limited

Everything above leaves one question, and it needs people. [r38](rounds/r38_human_sampling_power)
decides which prompts to send them and how many, **before** anyone is paid to rank anything.

**Power is not the constraint.** Clustering on prompt — six comparisons from one rater's
ranking of four responses are *one object*, not six draws — with variance components measured
from r22's per-prompt arrays (total sd 0.149 → between-prompt 0.140, binomial 0.049):

| effect | 40p × 8r | 60p × 8r | 100p × 8r |
|---:|---:|---:|---:|
| +0.03 | 0.51 | 0.69 | 0.88 |
| +0.05 | 0.91 | **0.98** | 1.00 |
| +0.16 *(r12's observed drop)* | 1.00 | 1.00 | 1.00 |

**60 prompts × 8 raters detects +0.05 at 98% power**, and r12's 0.16 is detectable in every
cell of the grid.

**The frame is the constraint.** The tempting sample is the prompts where r12's inversion is
largest — which yields a number about the strangest prompts that reads as a number about
transport. So prompts are stratified on original–fresh distance (and, once r12's per-prompt
attribution lands, on rubric–proxy disagreement), sampled **equally within cells**, and carry
**sampling weights** so one collection yields both a population estimate and an anomaly-subset
estimate.

Two bugs in this round are worth recording because both would have silently set the sample.
A feature with zero spread across released responses — *refusal markers*, identically zero —
was being divided by a `1e-9` guard, giving one prompt a distance of **1e9** and letting a
single unchecked feature decide the whole axis. And the per-prompt variance was **hardcoded at
0.16** under a comment claiming it was measured; the real value is 0.149, and the round now
refuses to emit a power grid when the between-prompt component would clip to a floor. That
guard fired on its author's own wrong divisor before producing anything.

### The endogeneity map is flat all the way to the edge of what this data can isolate

"Is it leakage?" is one rung of a ladder. What matters for anyone reusing a CoVal rubric is
how the signal decays as the people supplying the direction are moved further from the people
whose choices are being predicted. [r37](rounds/r37_leakage_topology) draws the whole ladder,
reporting `L(k) = A0 − Ak` rather than a single bias number.

| isolation level | weights come from | accuracy | `L(k)` |
|---|---|---:|---|
| **A0** same participants | everyone | 0.6465 | — |
| **A1** leave-one-rater-out | everyone except the target | 0.6460 | +0.0005 [−0.0017, +0.0026] |
| **A2** held-out rater folds | a disjoint 5-fold | 0.6439 | **+0.0026 [+0.0004, +0.0049]** |
| **A3** held-out **country** | every *other* country | 0.6458 | +0.0007 [−0.0033, +0.0048] |
| A3 held-out AI-usage | other usage bands | 0.6437 | +0.0028 [−0.0009, +0.0066] |
| A3 held-out age | other age bands | 0.6425 | +0.0040 [−0.0001, +0.0080] |

**One rung is significant and it is not the one that would matter.** A2 — moving to
rater-disjoint folds — costs **+0.0026 [+0.0004, +0.0049]**, about **0.4%** of a 0.6465 base.
Every other rung spans zero, including held-out **country** (+0.0007), which costs *less* than
A2 does.

**⚠ Non-significance is not equivalence, and the earlier wording treated it as such.** The
defensible claim is **no detected aggregate loss in the splits tested** — not "not
population-conditional". `p > 0.05` on six countries is silence about anything smaller than this
design can see, and an aggregate accuracy can conceal criterion-level **sign reversals**,
minority-only criteria, and groups choosing alike *for different reasons*. Establishing
population invariance needs an equivalence test against a pre-declared margin and a
criterion-level heterogeneity model, neither of which has been run.

⚠ This corrects the first published version, which reported A2 as non-significant from a
**2-seed** run whose interval was wider. The full 8-seed run is above.
Weights estimated in Mexico, the Netherlands or South Africa predict the choices of raters in
the United States about as well as those raters' own ratings do. Within the isolation this
release permits, criterion direction behaves like a **population-level property**.

**The rung that matters most cannot be climbed here.** `A4` — weights from people who never
saw a response — is **undefined, not zero**: nobody in this dataset rated a criterion without
first seeing four candidates. The map is flat right up to the boundary of what is measurable,
and the one question left sits on the other side of it.

⚠ 148 of 1,160 criterion raters (12.8%) have no annotator record and therefore no country
([entry 22](RETRACTIONS.md)). They can supply *weights* but can never be a held-out stratum,
so A3 covers 87.2% of the pool and the excluded eighth is not random with respect to anything
known.

### The channels overlap, so the sequential split was attributing to direction what importance also explains

r32 added channels in one order — text, then sign, then magnitude, then visibility — and
reported the increments. Pairwise accuracy is not additive, so those are the value of adding
each channel **last** to whatever preceded it, not contributions.
[r36](rounds/r36_channel_shapley) computes all sixteen coalitions.

The cells r32 never ran are the informative ones:

| coalition | what it is | accuracy |
|---|---|---:|
| `T` | criterion text, direction-free | 0.5839 |
| **`MT`** | **magnitude *without* direction** | **0.6277** |
| `ST` | sign | 0.6438 |
| `MST` | sign + magnitude | 0.6594 |
| `TV` | visibility alone | 0.5839 |

**Weighting by how *strongly* people rated a criterion — ignoring which way — already reaches
0.628 against direction's 0.644.** The two channels are near-substitutes, so the +0.0876 r32
attributed to polarity was largely the value of *any* informative weighting arriving first.

Shapley values, averaged over every arrival order:

```
channel   φ same    φ cross    φ_same − φ_cross
T         0.1277    0.1261     +0.0017 [+0.0005, +0.0028]
S         0.0214    0.0205     +0.0008 [+0.0001, +0.0015]
M         0.0128    0.0123     +0.0005 [-0.0005, +0.0016]   spans zero
V         0.0002    0.0000     +0.0002 [-0.0000, +0.0004]   spans zero
```
*(5-seed full run. An earlier version of this table came from a 2-seed smoke run in which the
T gap spanned zero; it does not.)*

**φ_S(same) − φ_S(cross) = +0.0008** — the plan's target estimand, and it is tiny under every
ordering, not just the one r34 tested. Visibility is worth essentially nothing (φ_V = 0.0002),
confirming r32's finding that it *hurts* when applied multiplicatively.

⚠ **One caveat that must travel with these numbers.** φ_T is large partly by construction:
sign, magnitude and visibility are all unusable without criteria, so `v(C) = 0.5` for every
coalition lacking T, and the orderings where a weight channel arrives before the text
contribute nothing to it. **φ_T therefore absorbs the "you need criteria at all" value, and
"text is six times sign" is not a licensed reading.** What the decomposition does establish is
order-independence of the same-vs-cross gap, and the near-substitutability of sign and
magnitude.

### …and it is not an artifact of forced-choice elicitation either

One measured fact makes that question urgent. Across all **102,147** criterion ratings in the
release, the value **0 appears exactly once**. The scale runs −10…+10 and its neutral point is
in practice unavailable — every rater assigned a direction to every criterion they saw.
*"This property has no general direction"*, *"it depends"*, and *"I can't say without seeing a
response"* have **no representation in this data**. Forced-choice elicitation is a known way
to turn weak or absent preference into apparently stable preference.

[r35](rounds/r35_polarity_abstention) classifies every shared seed criterion by how much its
raters agreed on direction, then compares three ways of scoring:

| polarity class | share |
|---|---:|
| stable (≥90% one direction) | 40.5% |
| leaning (60–90%) | 48.0% |
| **contested (<60%)** | **11.5%** |

| rule, cross-fitted | accuracy | criteria kept |
|---|---:|---:|
| attribute-only | 0.5834 | 100% |
| **forced** — every criterion gets a direction | 0.6423 | 100% |
| **confident** — abstain unless ≥90% agree | **0.6406** | **45.8%** |
| **posterior** — weight by `p₊ − p₋` | **0.6505** | 97.4% |

```
confident − forced   −0.0017 [−0.0084, +0.0051]   spans zero
posterior − forced   +0.0082 [+0.0042, +0.0121]   excludes zero
```
*(10-seed full run.)*

**Abstaining on 54% of the criteria costs nothing measurable.** And down-weighting contested
criteria instead of forcing them to ±1 *improves* concordance.

**⚠ What this establishes is robustness to POST-HOC abstention, not the absence of a
forced-choice effect.** Dropping low-consensus criteria after collection cannot simulate what a
participant would have written had *"no general direction"*, *"depends on implementation"* or
*"cannot judge without seeing a response"* been on the screen. Elicitation format changes the
response it elicits; that is not recoverable by filtering the responses it already produced. The
real test requires those options **at elicitation time** — which is the PRE arm of the
outstanding human experiment.

Read with r34, the polarity channel now looks like a genuine cross-rater direction: it
survives rater-disjoint cross-fitting (92%), it concentrates in criteria with agreement, and
it is robust to abstention. **Two of the three worlds are closed.** What remains is the one
no split of these annotators can reach — every one of them saw the four candidates before
rating — so *stable population value* versus *direction constructed by seeing the menu* still
needs weights from people who never saw a response.

### What the satisfaction judge is using

Every cross-rater result here runs through one instrument — the judge answering *"does response r
satisfy criterion c?"*. r04 validated it in aggregate against held-out human rankings. Nothing
asked what it was **using**, and r50 gave a reason to.

[r51](rounds/r51_judge_lexical) measures, within a fixed (prompt, criterion), whether satisfaction
across the four responses tracks lexical overlap between criterion and response:

| | |
|---|---:|
| mean **signed** corr(overlap, satisfaction) | **+0.2068 [+0.1966, +0.2161]** |
| response-permutation null | −0.0034 [−0.0090, +0.0020] |
| with response **length** partialled out | +0.1886 [+0.1768, +0.2010] |
| criteria with positive human rating | +0.2252 |
| criteria with **negative** human rating | +0.1527 |

Both polarities are positive, so there is no negation trap hiding two opposing mechanisms — for a
criterion like *"the model moralises"*, a response that moralises does contain the words, and
scoring it satisfied is correct.

⚠ Read the **signed** value. At four responses, two independent vectors give E|r| ≈ 0.50, so a
bare magnitude here would repeat [entry 49](RETRACTIONS.md).

**And the mechanism is causal, not just correlational.**
[r52](rounds/r52_overlap_intervention) intervenes: take the *same* criterion, append six
distinctive tokens from response A in one arm and from response B in the other, and read the
judge's A-vs-B satisfaction gap. The appendage is the same kind of object in both arms, so its
semantic effect cancels — only the *source* of the words differs.

| | |
|---|---:|
| baseline gap `s(c,A) − s(c,B)` | +0.0234 [−0.0098, +0.0570] |
| **intervention Δ** | **+0.2507 [+0.2300, +0.2714]** |
| unrelated-token null | −0.0045 [−0.0181, +0.0094] |
| absolute shift from appending unrelated tokens | A −0.0648, B −0.0603 |

Six copied words move the gap by a quarter of the 0–1 scale. The unrelated-donor arm — equally
rare tokens matching neither response — does nothing, so this is the **source** of the tokens and
not the act of appending; and the absolute shifts are small and symmetric, so the perturbation did
not simply break the instrument.

This is the only **interventional** round in the project. Everything else is observational on a
fixed release.

**Does that channel explain r12?** It is the obvious candidate — own criteria were written by
people looking at the original four responses, so they share vocabulary with them; donor criteria
come from another prompt and share vocabulary with neither. On fresh responses the own-rubric
overlap advantage should evaporate. [r54](rounds/r54_overlap_transfer) measures it:

| criterion set × response set | mean containment |
|---|---:|
| own × original | 0.1482 |
| own × fresh | 0.1158 |
| donor × original | 0.0189 |
| donor × fresh | 0.0213 |

The advantage really does collapse, **+0.1294 → +0.0945** (drop +0.0349 [+0.0266, +0.0434]), and
given r52's causal +0.2507 that collapse must depress own-rubric satisfaction on fresh responses.

**But it does not explain r12.** The per-prompt collapse does not predict which prompts show the
attribution drop: **corr = −0.0736 [−0.2059, +0.0612]**. That left one escape — a *uniform*
contribution, invisible to a per-prompt correlation.

[r55](rounds/r55_overlap_selectivity) closes it by measuring the right quantity instead of the
same one again. Attribution is an **ordering** statistic, and a shift that raises all four
responses equally cannot move an ordering. What can is **selectivity** — the sd of containment
across the four, high when a criterion overlaps the one response it was written about:

| | original | fresh |
|---|---:|---:|
| own criteria | 0.0738 | **0.0776** |
| donor criteria | 0.0220 | 0.0259 |
| **own − donor** | **+0.0518** | **+0.0517** |

**Collapse: +0.0002 [−0.0056, +0.0059] — equivalent to zero at δ = 0.01**, tested rather than
merely non-significant. Own criteria are as selective about responses they were never written for
as about the ones they were.

So the component that could have acted uniformly is the one that does not vary, and the component
that would have to vary does not change. **The judge's overlap channel is real (r51, r52) and
cannot explain r12.**

**This gives r50's anchoring effect a live instrument explanation**: anchored criteria may
transfer better because they are the ones the judge scores accurately. It does **not** establish
that overlap-driven scoring is *wrong* — overlap and genuine satisfaction are correlated in the
world, and the release contains no satisfaction ground truth against which to set the ceiling
(**verified**: streaming every field name from all four release files — 1,078 + 986 + 18,384 +
1,012 lines, 103 distinct fields — returns no satisfaction-, meets- or per-criterion-score field) a
correct judge would show. And the claim card's real positive control — having the judge score a
criterion copied out of a response — **was not run**; it needs a GPU pass, and the round says so
in its own output rather than passing off an estimator check as the control.

### …and it transfers on criteria nobody but the author ever saw

Item 1 rescoped "not leakage" to leave **shared-menu endogeneity** open, because every
participant saw the same four responses. r48 then showed the menu had a *second* shared part:
the same six pre-seeded criteria, identical for every rater on a prompt.

And [entry 51](RETRACTIONS.md) established that r34, r35, r36, r37 and r43 all filter to
majority-rated criteria — which **is** that pre-seeded set. They analyse **5,564 of 15,248
criteria (36.5%)**, discarding the 9,684 participant-authored write-ins. Nobody chose that; the
rater-count threshold did it, and "reliably-rated criteria" and "the criteria OpenAI supplied"
turned out to be the same operation described two ways.

So the shared-criterion channel was not a residual worry in those results — it was their entire
population. [r49](rounds/r49_provenance_crossfit) tests the excluded half, size-matched to the
same 6 criteria per prompt:

| arm | cross-fitted direction advantage | shuffled-sign null |
|---|---:|---:|
| pre-seeded six (r34's population) | +0.0599 [+0.0514, +0.0687] | −0.0831 |
| **write-ins** (one author, one rater) | **+0.0777 [+0.0674, +0.0883]** | −0.0668 |
| **paired gap** | **+0.0172 [+0.0034, +0.0307]** | — |

The control reproduces r34 (+0.0599 against its +0.0576) before any per-class number is read.
**Private criteria transfer better than shared ones** — and that is *conservative*, since a
write-in's sign comes from a single rater while a seeded item's averages ~17.

So the transferable direction is **not an artifact of shared criterion text**. ⚠ It narrows
shared-menu endogeneity to the **response** channel; it does not remove it. Every write-in was
still authored after seeing the same four candidates.

⚠ **I originally added that this channel was unreachable by any design this release permits. That
was wrong** ([entry 52](RETRACTIONS.md)). [r50](rounds/r50_response_anchoring) builds one — split
write-ins by how much their words overlap the four candidates — and it returns a signal: anchored
criteria carry **+0.0271 [+0.0134, +0.0405]** more direction than generic ones. It still cannot
*attribute* that signal, because the pre-seeded control trends the same way and the excess spans
zero. A design existing and a design deciding are different things, and only the first is
established.

### The direction transfers across people — so it is not the raters' own rankings coming back

The sharpest of the three live worlds was **same-sample target leakage**: the ratings that
build the weights and the rankings being predicted come from the *same people on the same
prompt*, so `ranking → polarity → rubric score → predicts ranking` is a closed loop.

[r34](rounds/r34_global_rater_crossfit) breaks the loop. Annotators are split into 5 global
folds — a person belongs to exactly one fold for the whole run, never re-randomised per
prompt. Weights come from **train** raters; the evaluation target is each **test** rater's
*individual* ranking, never an aggregate that would carry their own choices back in.

| arm | weights from | accuracy |
|---|---|---:|
| attribute-only | none (direction-free) | 0.5834 |
| **cross-fit sign** | **raters disjoint from the target** | **0.6421** |
| same-sample sign | everyone, incl. the target rater | 0.6466 |
| leave-one-rater-out sign | everyone except the target rater | 0.6415 |
| random sign *(null)* | signs shuffled, ratio preserved | 0.5687 |
| donor-prompt sign *(null)* | another prompt's signs | 0.5556 |

```
D_population  crossfit − attribute   +0.0576 [+0.0486, +0.0671]
D_same        same     − attribute   +0.0631 [+0.0540, +0.0720]
D_same_sample_premium     same     − crossfit    +0.0055 [+0.0025, +0.0085]    ← 9% of the effect
```
*(25-seed full run; fold-seed sd of the arm is 0.0012.)*

**Roughly 91% of the polarity gain survives rater-disjoint cross-fitting.** Both nulls sit
*below* the direction-free arm — shuffled signs −0.018, donor-prompt signs −0.034 — so the
sign channel is not a free parameter; the specific directions carry the signal.

**So SAME-RATER circularity is not the explanation.** The post-choice direction generalises
across people.

**⚠ This does not exclude menu-induced construction, and the earlier wording implied it did.**
What is ruled out is the individual loop — *this rater's own weight predicting this rater's own
ranking*. What is untouched is the shared one: **every participant saw the same four-response
menu**, so

```
menu  →  shared salience  →  Sᵢ
```

can produce directions that agree across people *and* are still constructed by the menu. Cross-rater
agreement is evidence against individual circularity and **is not evidence for a pre-existing
norm**. No split of these annotators can separate those, because none of them rated a criterion
before seeing responses.

**What this does not settle**, and cannot: *every* rater in this dataset saw the four
candidates before rating the criteria. So the two remaining worlds — a **stable population
value direction** versus a direction **constructed by seeing the menu** — are still both live,
and no split of these annotators can separate them. That needs weights from people who never
saw a response, which is the cheapest outstanding human experiment and now the highest-value
one.

### Post-ranking polarity nearly doubles the concordance — and what that means is unidentified

CoVal's protocol is sequential: participants **ranked the four candidates first**, and only
then saw the seeded criteria, rated them, and could write their own. So a criterion's
*sentence* can predate the candidates while the *sign and magnitude* attached to it cannot.

[r32](rounds/r32_channel_decomposition) holds the judge, the responses and the criterion text
fixed and varies **only the weighting**, using the satisfaction matrix r04 already computed:

| what the score uses | accuracy | above chance |
|---|---:|---:|
| criterion **text** only (equal weights) | 0.5899 | 9.0 pts |
| + post-choice **polarity** (human-rated sign) | 0.6775 | 17.8 pts |
| + post-choice **magnitude** (mean rating) | 0.6831 | 18.3 pts |
| + **visibility** (× n raters) | 0.6697 | *worse* |

**Polarity alone is worth +0.0876 [+0.0784, +0.0976]**, paired on prompts.

**⚠ What this does and does not say.** It says: *adding a direction measured after the rater
ranked the candidates raises above-chance concordance on the original candidate set from 9.0
to 17.8 points.* It does **not** say half the rubric's ability is post-choice leakage, and
three earlier drafts of this section did. Four reasons:

- **A criterion sentence is usually an *attribute*, not a value judgement.** "Response
  moralises" has no direction until someone supplies one. So equal weighting is an
  **attribute-only diagnostic**, not a "text-only value score", and its 0.5899 is not the
  rubric-minus-weights counterfactual.
- **Accuracy is not additive.** 0.5899 → 0.6775 is not a causal contribution, and the
  decomposition depends on the order channels are added. A Shapley-style all-coalitions
  version is queued.
- **Measured after ≠ generated after.** The polarity could be a stable value direction that
  merely happened to be recorded post-ranking.
- **+0.0876 and the +0.0791 own-vs-shuffled attribution are different contrasts** — a
  sequential increment against an arm difference. They are numerically comparable and not
  algebraically substitutable.

At least three worlds remain live and this experiment cannot separate them: **stable
cross-rater value direction**, **response-induced preference construction**, and **same-sample
target leakage** — the last because the ratings that build the weights and the rankings being
predicted come from *the same people on the same prompt*:

```
ranking  →  criterion polarity  →  rubric score  →  predicts ranking
```

The sharpest defensible statement is therefore about r04, not about values:
**a large share of r04's internal concordance is driven by post-outcome information, and until
rater-disjoint cross-fitting is run, that share cannot be counted as independent predictive
ability.**

Two things follow that were not visible before.

**r04's unweighted alternative is not neutral.** An equal-weight mean *rewards* a response for
satisfying a criterion the raters marked **negative** — "the model should not moralise" scored
as something to maximise. That is why the equal arm sits at 0.590.

**r13 was measured at equal weights**, which is the most response-blind configuration available,
so its seed-vs-write-in comparison was genuinely a comparison of *text*. That narrows what
[entry 38](RETRACTIONS.md) withdrew: the polarity channel is closed for r13's specific number,
and open for the released scoring rule.

### What CoVal-core actually is — a normative compiler

*(The round's directory is named `r33_core_launders_polarity`. "Launders" imputes intent and is
withdrawn as a description: the accurate statement is that **core internalises polarity into
rewritten criterion semantics while discarding most of the original rating and disagreement
provenance.** That is an artifact-design consequence, not a deception.)*

The dataset card says core is built by a process that **"first rewrites all rubric items to
have positive weight"** (`DATASET_CARD.md:74`). That makes core not a *subset* of full but a
**transformation** — and one of its steps takes the sign a participant supplied *after*
ranking the candidates and rewrites it into the criterion's wording.

[r33](rounds/r33_core_launders_polarity) pre-registered three predictions and tested them on
the satisfaction matrices r04 already computed:

| rubric | weighting | accuracy |
|---|---|---:|
| full | equal — **no human ratings used** | 0.5899 |
| **core** | equal — **no human ratings used** | **0.6563** |
| full | + post-choice sign and magnitude | 0.6831 |

**P1 confirmed: +0.0663 [+0.0574, +0.0754].** Core scored with *no ratings at all* recovers
about **76%** of the +0.0876 that full only reaches once the post-choice weights are applied.

Two things this settles.

**The released core rubric ships with no weights.** Its items carry only `criterion` — no
`scores`, no ids — verified field by field. So equal weighting is the *only* rule defined on
core, and P2 (`core/signed ≈ core/equal`) is **tautological, not evidence**: there is nothing
to apply.

**Core is therefore the artifact most likely to be misread.** It is short, readable,
positively phrased, four items — it looks exactly like a hand-written value checklist
authored independently of any response. It is the one where that reading is least available,
because the information making it work was produced by people who had already chosen.
P3 shows it does not recover everything: full-with-weights still leads core by 0.0268.

### …and the judge moves it as much as the floor does

[r22](rounds/r22_cross_family) grades the same 300 prompts with judges from **two model families**.
The decomposition survives — every judge shows a positive attribution with an interval clear of zero,
so it is **not an artifact of the Qwen lineage**. But the magnitude is not portable:

| judge | family | own | random floor | attribution ([r22](rounds/r22_cross_family)) | prompt-specific share ([r30](rounds/r30_scope_grid)) |
|---|---|---|---:|---:|---:|
| qwen3.5-2b-base | qwen | 0.6522 | 0.5759 | +0.0763 [+0.0585, +0.0944] | 50.1% |
| qwen2.5-3b-instruct | qwen | 0.6660 | 0.5767 | +0.0894 [+0.0672, +0.1114] | 53.8% |
| phi-3.5-mini-instruct | **phi** | 0.6410 | **0.6053** | +0.0357 [+0.0186, +0.0541] | **25.3%** |

phi clears its own positive control at 0.641, level with the Qwen judges — but its *unrelated-rubric
floor* is 0.605 against their 0.576. It extracts more generic response quality for free, leaving less
room for prompt-specific content.

**So the share has two independent sources of variation, and they multiply.**
[r30](rounds/r30_scope_grid) puts an interval in every cell — a ratio-of-means bootstrap
resampling prompts, replacing three successive point-estimate ranges (43%, 27–67%, 13.6–74%)
that never carried one:

| judge ([r30](rounds/r30_scope_grid)) | family | vs nearest-topic floor | vs random floor |
|---|---|---:|---:|
| phi-3.5-mini | phi | **13.6%** [3.2%, 23.7%] | 25.3% [13.7%, 37.2%] |
| qwen2.5-3b | qwen | 30.5% [20.1%, 41.0%] | **53.8%** [42.1%, 65.8%] |
| qwen3.5-2b | qwen | 36.9% [26.4%, 47.7%] | 50.1% [39.4%, 61.2%] |

```
point estimates alone      13.6% .. 53.8%   = 3.94×
including sampling error    3.2% .. 65.8%
```

**The second line is the defensible one**, and the grid's true upper corner is not even in
it: the farthest-donor floor (~74% on Qwen, r19) was never run against phi, and internlm2
could not be loaded at all. Every cell also shares one 300-prompt panel, so the span is not
a confidence statement about a population of judges.

**⚠ The quantity was misnamed from the start, and the name is retired.** This contrast is

```
own-rubric predictive performance  −  SELECTED reference-rubric performance
```

It is **not** `values − non-values`. Whatever an unrelated prompt's rubric recovers is itself
made of accuracy, clarity, caution, non-deception, relevance, proportionality — norms, not the
absence of them. The correct name is **source specificity**, or incremental prompt-conditioned
information. *"Less than half of a values evaluation measures values"* was never a licensed
reading of this subtraction and is withdrawn as a framing, independently of the numbers, which
stand.

**This is the quantity's real scope.** Source specificity is not a property of the dataset. It
is a property of *(dataset, floor donor, judge family)*, and the last two — both analyst choices,
neither reported in the source package — move the answer more than fivefold. A single figure
constrains nothing unless it names both.

⚠ `internlm2-chat-1.8b` could not be loaded at all (tokenizer parse error) and is reported as a
**load failure, not a judge verdict**. A third family remains untested.

### …and the prompt-specific part does not transfer

The criteria were written by participants **after reading the four candidates**. Measured on
rubric-blind responses those authors never saw, the advantage does not merely shrink — it inverts:

| response set ([r12](rounds/r12_response_set)) | real rubric | unrelated rubric | advantage |
|---|---:|---:|---:|
| the four released candidates | 0.657 | 0.555 | **+0.102** [+0.071, +0.133] |
| fresh, rubric-blind, unseen | 0.481 | 0.545 | **−0.064** [−0.092, −0.037] |

A discrimination control confirms the fresh set is *more* separable than the released one, so this
is not an artifact of homogeneous generations. Re-run on an entirely new temperature-0.9 sample
([r46](rounds/r46_spread_replication), `controls`) the inversion replicates: **+0.0847 → −0.0716**
on 250 prompts this project had never touched, overlap with r12 exactly **0**.

> **⚠ What this is NOT.** There are **no human rankings on the fresh responses** and there cannot be
> without new data collection. The yardstick is a learned preference head fitted on human rankings of
> the *original* responses. So the measured object is **disagreement between the rubric score and an
> original-distribution-trained proxy, under a response-distribution shift** — not inversion of human
> preference. A discrimination control shows the proxy is *more discriminative* on the fresh set; it
> does **not** show it is *correct* there. Variance is not calibration, and a broken thermometer reads
> a wide range on unfamiliar objects. The two gold heads correlate only **+0.4775**, which is evidence
> for this concern rather than a curiosity. **Human rankings on the exact saved fresh responses are the
> single highest-information next action in this project.**

[r13](rounds/r13_seed_vs_writein) then refuted the obvious explanation. If the criteria simply encoded
facts about those four candidates, criteria not written by someone who had read them should carry no
advantage. They carry a clear one — and **which provenance carries more is not established**, because
the paired difference spans zero:

> **⚠ What "response-blind" means here, exactly.** The dataset card (line 73) says the seed items were
> prepared ***in parallel*** with candidate generation — not before it, and not by anyone blind to it.
> The same team was simultaneously writing four candidates chosen "to represent a range of potential
> model behaviors" and writing example criteria for that prompt. So the seeds are response-blind with
> respect to **participant exposure**, which is what the leakage argument needs, and **not** independent
> of the responses by **design**, which is what an S_pre reading would need. An earlier draft of this
> paragraph said the seeds were "written *before anyone saw them*" and "never tailored to the
> responses"; the card supports neither.

| criterion provenance | real | unrelated | advantage |
|---|---:|---:|---:|
| seed (participant-blind) | 0.583 | 0.537 | **+0.046** [+0.023, +0.069] |
| write-in (after reading) | 0.559 | 0.533 | **+0.026** [+0.002, +0.051] |
| **difference, paired on 293 shared prompts** | | | **+0.023 [−0.008, +0.054]** |

**Both arms are corrected and the third row is the honest one.** An earlier version reported +0.039 vs
+0.029 and read the write-in interval as spanning zero, making seeds look *better*. Two errors: the
attribution differenced a positional prefix of one array against a differently-ordered subset
([entry 15](RETRACTIONS.md)), and the *difference* was quoted with no interval at all. Repaired, every
point estimate rose — and the ordering died, because +0.023 spans zero. Which of the two provenances
carries *more* is **not established** — and neither is their *equivalence*: the 95% interval spans
0.062, **3.1× the ±0.01 window**, so this contrast is **INCONCLUSIVE**, not a null
([r58](rounds/r58_equivalence_census)).

> **⚠ Retracted claim.** This round previously concluded *"response-set knowledge is not the
> mechanism."* **That is too strong and is withdrawn.** What it rules out is only the narrowest channel:
> literal memorisation of the final candidate *strings*. At least three others survive, and the release
> cannot close them:
>
> - **post-choice weighting** — seed criteria were *rated* after participants ranked the candidates.
>   *(Closed in this estimator, and stated because it must be: r13 scores by an unweighted mean of
>   judge satisfaction and uses no human rating sign or magnitude anywhere.)*
> - **shared viewpoint generator** — OpenAI produced candidates by first generating varying *viewpoints*
>   on the ideal answer. Nothing establishes that seed criteria were generated independently of that
>   scaffold, so a criterion can know the candidate *distribution* without knowing any candidate.
> - **prompt-construction manifold** — prompts were synthesised for specific Model-Spec tensions and
>   candidates instantiate them. A seed rubric can be predictive on that designed manifold and not on a
>   free generation occupying a different one.
> - **post-choice selection into core** — CoVal-core is an LM-assisted synthesis of *highly rated*
>   criteria, so which response-blind sentences survive is decided by post-response ratings.
>
> The defensible claim is: **multiply-rated seed criteria carry local predictive signal without literal
> string memorisation. Seed provenance, post-choice weighting, shared viewpoint generation and
> manifold dependence remain unresolved.**

One further caveat this table cannot show: "seed" is **inferred from rating count**, not read from a
release field. The bimodality is real — 9,684 criteria carry exactly one score and nothing sits between
one and each prompt's majority threshold — but it measures *visibility*, and cannot separate "prepared
response-blind" from "one annotator's write-in, later shown to everyone".

So the bound is not about what the criteria encode. It is a property of the measurement apparatus off
distribution — a transfer boundary for rubric-graded evaluation, which is the open question this
repository now points at.

---

## Rounds

Each round is self-contained: its own question, runner, results and README.

⚠ **Several lines are frozen — see [FROZEN.md](FROZEN.md).** A line is frozen when further
computation cannot identify what it is measuring, which is a statement about the object rather
than about the estimate. Each entry records what would *unfreeze* it, because a freeze without
an unfreeze condition is abandonment with better manners. The rater-structure ontology
(r23/r25/r26/r27/r28) failed **four consecutive separators for four different reasons** and is
frozen UNRESOLVED — neither "no pair structure" nor "blocs exist". The computational headline is
frozen at **3.2%–65.8%**: its width comes from analyst choices the source package never reports,
not from estimation noise, so no further computation narrows it.

| round | question | headline |
|---|---|---|
| [r01](rounds/r01_rater_structure) | Is disagreement noise or structure? | persists across disjoint prompts, ρ=0.147, z=+16.6. Most of it is an additive per-rater effect (r23). Whether anything **pair**-specific survives is **UNRESOLVED** — r28 showed the decomposition's functional form is itself unvalidated. The "survives removing response style" control was invariant by construction |
| [r02](rounds/r02_label_and_regime) | Label bias; fatigue or regime change? | label B wins 22.5% vs 25% expected. The task-6 effort drop is **real and within-person** (r31) but its **mechanism is unidentified** — position 6 is the study's minimum-task boundary |
| [r03](rounds/r03_stated_vs_revealed) | Do stated ideals predict own choices? | **equivalent to chance at the preregistered δ=0.01**, which is stronger than the *"no evidence"* this row used to report. Over **11,327** judgements from **1,007** annotators: hit rate **0.5033** vs a label-permuted null of **0.5016**, difference **+0.0017** [−0.0061, +0.0097] — the interval lies inside the margin with **0.0003** to spare, so this is a *tight* null, not an unpowered one. (95% interval used where TOST asks for 90%: conservative, since the 90% is narrower.) ⚠ The raw hit rate splits **0.5138** / **0.4903** by whether the top pick is longer — but [r81](rounds/r81_stated_signal_by_length) tested it and **the nulls split too** (0.5133 / 0.4870): against their own baselines the strata are **+0.0005** and **+0.0033**, gap **−0.0028** [−0.0180, +0.0120], covering zero. **A raw split against a common baseline is not a split in the effect** |
| [r81](rounds/r81_stated_signal_by_length) | Is r03's equivalence hiding a length-conditional signal? | **no — the split is in the null, not the effect.** Entry 139 flagged a raw hit-rate gap of +0.0235 between judgements where the top pick is longer and shorter, ten times r03's aggregate difference, and tested it nowhere. Stratified against **each stratum's own** permuted null: longer **+0.0005** [−0.0101, +0.0111], shorter **+0.0033** [−0.0083, +0.0148], difference of differences **−0.0028** [−0.0180, +0.0120]. The nulls themselves split 0.5133 / 0.4870 — a different person's text also "predicts" better when the top pick is longer, because longer text shares more vocabulary with anything. ⚠ **Equivalence is n-dependent**: the aggregate clears δ=0.01, neither half does, because splitting halves the sample. Rebuild control reproduces r03's 0.5033 and +0.0017 exactly before any stratum is read |
| [r82](rounds/r82_scale_use_by_provenance) | How was the weight scale actually used? | **the midpoint of a 21-point scale was used ONCE in 102,147 ratings** — ⚠ a fact r35's `scale_note` already stated; what is new here is the *shape*. Splitting by provenance: low-magnitude ratings (|w|=1 or 2) are **19.21%** of seed ratings against **6.98%** of write-ins — a gap of **+0.1223** against a within-prompt provenance-permutation null of [−0.0016, +0.0095]. ⚠ **Displacement and selection are unseparated**: a rater authors a write-in *because* they already care, which predicts the same direction with no forced-choice pressure at all, and I failed to write that rival before the run. Scale-use facts worth having anyway: **77.01%** of ratings positive, **16.96%** at the extreme \|w\|=10, and **29.55%** on 5 or 10 — over a third of all weight mass on two of twenty-one values. ⚠ **Nobody in this release was offered a neutral option**, so what a participant *would* have done is unobservable and this round cannot simulate it — it measures scale *use*, not the counterfactual, which is why the neutral-option arm is preregistered |
| [r83](rounds/r83_low_magnitude_drop) | Do r82's weakest ratings carry anything? | **no — they are free to delete.** Removing every rating with \|w\| ≤ 2 (**18,154** of **100,530**, 18.06%) and recomputing each criterion's weight from the survivors moves agreement with **real human** pairwise rankings by **−0.0000248** — equivalent to zero at δ=0.01 by a factor of **403**. The arm that carries it is a **size-matched random deletion** repeated 200×: **0.6832** [0.6803, 0.6865] against the targeted **0.6860**. So removing the weakest fifth of all ratings costs nothing, while removing as much arbitrary data costs ≈0.003. ⚠ **Deletion acts on the rating set, not on people** — it says what the rubric loses without these numbers, never what a rater would have written given a neutral option, so r82's displacement-vs-selection question is untouched |
| [r84](rounds/r84_core_polarity_in_words) | Is core's polarity actually *in its words*? | **yes — and it fills a cell that has been `NaN` since r33.** r33 proved core beats full by +0.0663 with equal weights and no ratings, then recorded `negative_share: {full: 0.2483, core: NaN}` — core carries no ratings, so its direction has no numeric home. A sign classifier trained on **15,223** full criteria (held-out prompts, so no core criterion is scored by a model that saw its own prompt) calls **96.69%** of core positive against **92.22%** of full: gap **+0.0447** [+0.0381, +0.0515], which is **57%** of the only 0.0778 of headroom available. Shuffling the training labels collapses accuracy to 0.7432 ≈ the 0.7435 marginal and the gap to **−0.0001**. ⚠ **This reconciles r65 rather than contradicting it**: core is *more* prohibitive in form (18.62% vs 12.85%) **and** more positive in direction — *"avoid moralising"* is both. A predicted-positive rate is a model's reading of wording, never a rating |
| [r04](rounds/r04_rebuild_satisfaction) | Rebuild the withheld layer | 119,868 judgements, validated on 80,542 held-out human pairs at 0.686 |
| [r05](rounds/r05_value_taxonomy) | What does compression silence? | not a value family — the penalty for being contested is −0.31…−0.46 in *every* family. ⚠ Its own caveats: the cited embedding result (**0.736 vs 0.520**) is **computed nowhere in this repository or its history and remains UNVERIFIED**, and both instruments here are lexical, so a **shared blindness to paraphrase is not excluded** |
| [r06](rounds/r06_rule_tournament) | Which aggregation rule wins? | **five** rules span **0.0188** (utility 0.6575 → consensus 0.6387); a consensus rule **ties random selection** (0.6387 vs 0.6384). Only utility (+0.0067) and constituency (+0.0070) beat no-compression; consensus is **worse** (−0.0113). ⚠ This row said *four* rules — the artifact holds five plus two baselines |
| [r07](rounds/r07_anthropomorphism) | Does the rubric see anthropomorphic style? | a **residual association**, not established blindness: a response-level marker retains t=+4.02 after controlling for rubric score and length, but the effect is carried by `user_directed_warmth`, which is **warmth, not anthropomorphism**. **0.046%** of criteria address the construct (7 of 15,248, hand-adjudicated), split 4 anti / 3 pro. Measures immediate preference, **not impacts** — trust, reliance, disclosure and attachment are untested |
| [r08](rounds/r08_gold_preference) | A gold model that never sees the rubric | held-out 0.661 vs 0.529 length baseline |
| [r09](rounds/r09_overoptimization) | Optimize the rubric, watch preference | pre-registered gaming prediction **refuted**: markers fell |
| [r10](rounds/r10_attribution_robustness) | Is the attribution an artifact? | **the own-vs-unrelated advantage survives every cell** — +0.0869, +0.0594, +0.0449 (mean +0.0638, sd 0.0174) — though it nearly **halves** from the 2B judge to the 0.8B. ⚠ The **topic share is not stable in the dimension the word "stable" names**: +0.3004, +0.4486, **−0.0369** across those same three cells, so the previously quoted **23.7% is a mean over a quantity that inverts sign**, and in the 0.8B cell `near` sits *below* `random`. This is own-rubric vs reference-rubric, never values vs non-values |
| [r11](rounds/r11_backbone_control) | Was r09 backbone leakage? | **retracts r09's rise** — it vanishes with an independent backbone. ⚠ Its own caveat: this is a statement about the **proxy-world measurement** — the correct scope for overturning r09, which is also proxy-world, and **not** a statement about human preference |
| [r12](rounds/r12_response_set) | Does the advantage transfer? | it **inverts** off-distribution: **+0.102 [+0.071, +0.133] → −0.064 [−0.092, −0.037]**, discrimination control passed. Replicated on held-out prompts at +0.0847 → −0.0716 ([r46](rounds/r46_spread_replication)) |
| [r13](rounds/r13_seed_vs_writein) | Seed criteria vs write-ins | **refutes r12's own mechanism**: participant-blind seeds carry real attribution (+0.046 [+0.023,+0.069]) — ⚠ the card says these were prepared *in parallel with* candidate generation, so they are blind to participant exposure, **not** independent of the responses by design. The seed-vs-write-in *ordering* is NOT established — paired difference +0.023 [−0.008,+0.054] |
| [r16](rounds/r16_minority_regret) | Conflict-aware, on its own turf | profile splits show regret 2.07 vs 1.10 random, yet conflict-aware leaves the worst-off group **lowest of all rules**. ⚠ These are **not** a demographic constituency: gender (1.145) and country (1.198) splits both fail r16's own bar |
| [r17](rounds/r17_conditional_core) | Does conditional encoding rescue it? | **partly** — routing learned from a rater's *other* prompts helps only the rules carrying contested items (+0.195), and does not close the gap |
| [r18](rounds/r18_routing_difficulty) | Was r17's 84.6% routing accuracy free? | **inflated by +0.147, but real**: 0.666 [0.643, 0.688] where the blocs actually disagree |
| [r19](rounds/r19_floor_choice) | Which donor is the generic floor? | the headline moves **2.47×** with that choice; prompt-specific share is 27–67%, not a single figure. ⚠ rests on **2 usable judge cells** with no prompt-level CI |
| [r14](rounds/r14_paraphrase_gauge) | Is the judge paraphrase-invariant? | **no — and the answer moves 6.2× with who does the rewording.** A *model* paraphrase flips **15.4%** of Yes/No verdicts (r=0.871, fidelity kept 99.1%); a *mechanical* rewording flips **2.5%** (r=0.989, fidelity kept **100%**). Part of "criterion content" is criterion wording — but the 15.4% quoted throughout this repository is **the model arm**, and the arm with higher measured fidelity is the one that barely moves |
| [r15](rounds/r15_indistribution_transfer) | Do criteria transfer to a near-topic prompt? | **no** — own criteria +0.073 [+0.056, +0.091] over the floor, nearest-topic criteria +0.018 [−0.001, +0.037]. Real responses, real human rankings, no gold model. r21 shows that neighbour is 91.6% of the way to being the same question. ⚠ The round's own verdict: **SCOPE CORRECTION — this does NOT resolve r12** |
| [r20](rounds/r20_paraphrase_transfer) | Is the advantage content or wording? | **content** — reword every criterion and **97.4%** of the advantage survives; original−paraphrased +0.002 [−0.007, +0.011] |
| [r21](rounds/r21_donor_distance) | Is the "near-topic" donor actually near? | **yes, near the ceiling** — it sits at the 97.86th percentile of all pairs and covers **91.6%** of the distance from a random prompt to the same question reworded |

| [r22](rounds/r22_cross_family) | Does the attribution survive a change of judge family? | **yes, and the magnitude does not** — positive on qwen and phi with intervals clear of zero, but the prompt-specific share runs 25.3% (phi) to 53.8% (qwen2.5-3b) at a fixed floor, a **2.13× judge span** (derived as 53.8÷25.3 from [r30](rounds/r30_scope_grid)'s shares, not stored by r22) on top of r19's 2.47× floor span. The first run falsely claimed this on two Qwen judges because "family" was `name.split("-")[0]`; phi was scoreable only after a tokenizer fix |
| [r23](rounds/r23_actor_vs_dyad) | Is r01's persistence about people or about pairs? | **mostly people**: an additive actor model takes 47.2% of dyad variance and actor-only persistence (0.254) *exceeds* the headline. Pair-specific residual 0.034, z=+4.67 — real, and a fifth of what r01 reported. Its sharper test (reliably-disagreeing pairs) is **null at z=+1.40** |
| [r24](rounds/r24_regime_receipt) | Receipt for "step R²=0.964 vs trend 0.448" | the number existed in no script. Reproduced, **and given the control it never had**: a null that re-searches the breakpoint on every shuffle reaches only 0.172. Observed 0.964, p=0.0001, breakpoint found at position 6 by search |
| [r25](rounds/r25_actor_dyad_sweep) | Is r23's residual stable, or a property of Pearson? | **complete — and the answer is both.** All **144** cells ran (4 metrics × 3 overlaps × 3 shared-item thresholds × standardise × centre); **138 usable, and the residual clears z>2 in 100% of them**, so it is not a Pearson artifact. But its *share* spans **0.2018–0.7000** (median **0.2650**) — a **3.5× range** — so the residual's *existence* is metric-invariant and its *size* is not. Gauge control behaved as predicted: Pearson invariant to centring (Δ=2.8e-17), cosine and negl1 not (Δ=0.0339, 0.0907). ⚠ This row reports the sweep's own numbers only; the rater-structure ontology it feeds stays **FROZEN as UNRESOLVED** |

| [r26](rounds/r26_sign_no_split) | Are there pairs that reliably *disagree*? | the split-half estimator returned **z = 1.40, 2.26, 2.68 and 10.26 on identical data**, varying only with how many coin flips were averaged. Rebuilt without any split |
| [r27](rounds/r27_raw_negative_tail) | Anti-correlation on the *raw* scale | the negative tail is real and grows with depth (1.20×→1.43×), and 3.02% of pairs are negative on **every** shared prompt vs a 1.93% null. Its actor control was confounded — under unequal blocs a majority member is "agreeable" by construction |
| [r28](rounds/r28_multiplicative) | Was the functional form wrong? | **the additive one is misspecifiable — and the alternative is not established.** Fitting a sum to a product leaves a U-shape with no blocs in it, which is what r27 measured. But "one fewer parameter" was **false** (the additive design is rank-deficient by exactly one; effective dof are *equal*), and out of sample the multiplicative fit spans R² **[−1.64, +0.51]** against additive's tight **[+0.34, +0.42]**. **Verdict: FUNCTIONAL FORM UNRESOLVED**, and the surviving `both_low` residual is not a measurement of anything |

| [r30](rounds/r30_scope_grid) | The headline, with an interval in every cell | replaces three successive point-estimate ranges (43%, 27–67%, 13.6–74%) with a (judge × floor) grid, each cell a ratio-of-means bootstrap over prompts |
| [r31](rounds/r31_within_person) | Is the task-6 drop composition or behaviour? | **within-person and real** — the same 933 people drop **−179 chars [−196, −162], −53.3%**, against only **6.1% attrition**. But position 6 is the study's minimum-task boundary and, with no session id in the release, is **perfectly confounded with "first task of a later session"** |

| [r32](rounds/r32_channel_decomposition) | Text or post-choice weights? | post-ranking **polarity nearly doubles** above-chance concordance (9.0 → 17.8 pts, +0.0876 [+0.0784,+0.0976]). Whether that is stable cross-rater value direction, preference construction, or **same-sample leakage is unidentified** — cross-fitting queued |

| [r33](rounds/r33_core_launders_polarity) | What is CoVal-core? | **a normative compiler, not a subset.** Scored with *no ratings*, core reaches 0.6563 against full's 0.5899 — it **internalises polarity into rewritten criterion text** while discarding rating and disagreement provenance. ⚠ the 76% figure is not decomposed: rewrite, merge, dedup, compatibility-selection and truncation are confounded |

| [r34](rounds/r34_global_rater_crossfit) | Is the polarity signal leakage? | **no.** Global rater-disjoint 5-fold cross-fitting keeps **91%** of it: D_population +0.0576 [+0.0486,+0.0671] against a same-sample premium of only **+0.0055**. Both nulls fall below the direction-free arm |

| [r35](rounds/r35_polarity_abstention) | Does it depend on forcing a direction? | **unanswered — only *post-hoc abstention* was tested.** Abstaining wherever raters split (dropping **54%** of criteria) moves cross-fitted accuracy by **−0.0017 [−0.0084,+0.0051]**, and down-weighting contested criteria *helps* (+0.0082). The scale's neutral point is used **once in 102,147 ratings**. ⚠ The round's own verdict: **NOT ESTABLISHED — the absence of a forced-choice effect.** Elicitation format changes what it elicits, and filtering criteria already produced cannot simulate a participant who had a neutral option at the time |

| [r36](rounds/r36_channel_shapley) | Channel split without order dependence | all 16 coalitions. **Magnitude without direction reaches 0.628 vs sign's 0.644** — near-substitutes, so r32's sequential split over-attributed to polarity. φ_S(same)−φ_S(cross) = **+0.0008**, tiny under every ordering. Visibility ≈ 0 |

| [r37](rounds/r37_leakage_topology) | How does the signal decay with isolation? | **almost not at all.** Only A2 (rater folds) is significant, at **+0.0026 [+0.0004,+0.0049]** ≈0.4%; cross-**country** costs **+0.0007**, spanning zero. `A4` response-blind is **undefined, not zero**. ⚠ The round's own verdict: **NOT ESTABLISHED — population invariance.** No aggregate loss was *detected* in the tested splits; 9 of r43's group cells are INCONCLUSIVE at δ=0.01 ([r58](rounds/r58_equivalence_census)) |

| [r38](rounds/r38_human_sampling_power) | Which prompts to send to humans, and how many? | **frame-limited, not power-limited.** 60 prompts × 8 raters detects **+0.05 at 98%** power clustered on prompt; r12's 0.16 is detectable everywhere. Equal-cell stratified frame with sampling weights so one collection gives both a population and an anomaly estimate |

| [r39](rounds/r39_feature_cache) | Cache representations, analyse nothing | one GPU pass, three lineages (qwen/phi/internlm), 2,000 responses. Load failures recorded as **environment claims**, not model properties |
| [r40](rounds/r40_ood_map) | Is r12's inversion an OOD artifact? | **no — the sign runs the wrong way.** Nearest-neighbour distance correlates at **−0.125**, 2/3 lineages, same sign 3/3: the anomaly is **worst where fresh responses most resemble the released ones** |
| [r41](rounds/r41_criterion_support) | Is the drop organised in the rubric's OWN criterion space? | **no.** Hull violation −0.1837 and rank instability +0.1993 die to the discriminating-power control; spread loss looked like it survived at +0.2309 but **failed to replicate** (r46). Tensor reproduces **all 1,500** of r12's per-prompt numbers exactly. ⚠ Its own caveat: `z_R` is produced by **the same judge whose off-distribution validity is unestablished**, so this round **cannot separate** "new normative territory" from the judge behaving incoherently on fresh responses |
| — | **What the six searches actually establish** | see [entry 56](RETRACTIONS.md): disattenuated, they split three ways — conclusions on tight *direct* estimates hold (r47, r55), conclusions on *correlations* are much weaker than reported (r40, r41, r54), and two failed *preregistered* replications at their claimed magnitude without being shown absent (entry 48, r56) |
| [r57](rounds/r57_outcome_reliability) | Could those searches have found anything? | **only large effects.** The per-prompt attribution drop has split-half reliability **0.302 / 0.422** across two samples, so observed correlations are attenuated by ~0.55–0.65. At n=250 the smallest *true* correlation distinguishable from zero is **≈0.2** — every "no mechanism" result is bounded by that (entry 55) |
| [r68](rounds/r68_r40_predictor_reliability) | Is r40's distance predictor reliable? | **yes — Spearman-Brown 0.9132.** Recomputing the per-prompt nearest-neighbour distance in three unrelated pretraining lineages from r39's 57 MB cache gives pairwise agreement **+0.9023, +0.7234, +0.7085** over 250 prompts; controls self 1.0000, prompt-shuffled −0.0980. r40's floor is **0.188**, replacing a published range of 0.180–0.222. ⚠ Written because entries 109 and 110 both asserted these embeddings were not persisted — **they are, and tracked in git**. ⚠ **Not regenerable**: internlm returns 100% NaN under transformers 5.14.1, so this three-lineage agreement cannot be recomputed on this machine, and no receipt records the environment that produced the cache ([r80](rounds/r80_panel_freeze), entries 134–135) |
| [r69](rounds/r69_r54_predictor_reliability) | Is r54's *lexical* predictor reliable? | **no — Spearman-Brown 0.4381**, against the 0.657 the ledger transferred onto it. Splitting each prompt's four core criteria 2-2 and recomputing r54's own containment gives split-half **+0.2805 averaged over 200 random splits** (sd 0.0399, range +0.183 to +0.387). So r54's floor **rises to 0.367**, and the row already called the ledger's weakest test is weaker still. ⚠ **I predicted the opposite** — r54 calls its quantity an exact text statistic, and I read determinism as high reliability. Determinism is a property of the *instrument*; this reliability is a property of the *criteria sample*. Positive control: splitting the **responses** instead returns 0.8020, so the estimator can report a high value and the low one is a fact about the criteria |
| [r70](rounds/r70_outcome_criterion_axis) | Do the two reliabilities in a floor even belong to the same axis? | **no, and nobody had written that down.** r57 measured the OUTCOME by splitting the 6 pairs (response axis); r67 and r69 measured PREDICTORS by splitting criteria. Rebuilding r12's attribution drop from half a prompt's criteria — a rebuild that reproduces every published per-prompt value exactly — gives a criterion-axis outcome reliability of **0.3013**, close to r57's 0.302/0.422, so for the *outcome* the axes agree. The ladder is the finding: accuracy **0.6462**, attribution **0.2695**, drop **0.3013** — the criterion split does not destroy signal, so the loss belongs to the contrast, confirming r57's own untested worry. Crossed split **+0.0785 [+0.0061, +0.1480]** vs +0.0463 if independent and +0.1808 if one shared source → **independent**, so the axes may be multiplied. ⚠ **Which axes a floor is entitled to divide by is not empirical** — three worlds reported with their arithmetic, no winner declared |
| [r71](rounds/r71_r67_split_variance) | Was r67's 0.657 also a single draw? | **yes, but it survives.** Re-running r67's estimator verbatim 200 times instead of once: spread loss **0.6849** (sd 0.0294), criterion-space geometry **0.6653** (sd 0.0304), mean **0.6751** against the published 0.657 — a shift of +0.018. Multiplier 1.217× not 1.234×; r41's floor 0.227→**0.224**, r46's 0.264→**0.260**. ⚠ **Correction to this row as first written.** I called the relative-spread pattern a finding; it is mostly arithmetic. The **absolute** across-split sd is near-constant across all six quantities measured — 0.0294 to 0.0448, a 1.5× range — so the 5.6%→28.8% spread in the *relative* figure is the denominator moving, not the volatility. The honest statement: a single split perturbs a raw correlation by about **±0.04 regardless of the quantity**, which is negligible at r≈0.51 and material at r≈0.18. Same practical conclusion, but it follows from a constant additive error, not from a scaling law. Shuffled null re-run every draw and reported as a **maximum** (0.2016), never a mean |
| [r72](rounds/r72_proxy_validity_coefficient) | How close is the model gold head to real humans? | **the one human-validated number in the package, never published until now.** On the original arm the attribution is **+0.1020** by gold head and **+0.0876** by real human rankings; difference **−0.0144 [−0.0392, +0.0086]** — not significant, and **NOT equivalent** at δ=0.01 (90% interval 2.0× the margin, point estimate 1.4× it). Per-prompt validity coefficient **0.6029**, i.e. ~36% shared variance. Rebuild control reproduces r47's stored 0.1020 to 0.0e+00. ⚠ **Not transferable to the ledger's rows** — measured on the original attribution, not the drop, and only H_fresh can cross that boundary |
| [r73](rounds/r73_direction_from_text_alone) | Is a criterion's direction in its words? | **only if the words came after the menu.** Predicting sign(mean score) from text alone, prompts held out: pre-written **seeds capture 1.2%** of available headroom (+0.0020 [−0.0007, +0.0049]), post-exposure **write-ins capture 26.4%** (+0.0821 [+0.0746, +0.0904]). Seeds' *in-sample* fit reaches only +0.0160, so this bounds learnable signal rather than reporting a held-out miss. Nulls collapse to marginal; the no-negation control makes the write-in margin **larger** (+0.0954). ⚠ Does **not** measure S_pre and does not contradict it — no rater in the release rated pre-exposure. It removes the reading that text-predictability would have demonstrated a prior, and confirms r61's baseline needs no adjustment for the seed-based PRE arm |
| [r74](rounds/r74_specificity_vs_exposure) | Is r73's effect about exposure, or about what write-ins *are*? | **exposure — it survived both threats.** Holding exposure constant (all write-ins) and varying lexical specificity: low/mid/high containment capture **8.9% / 16.5% / 24.0%** of headroom. The *least* response-specific third still captures ten times the seed class's 0.9%, so the effect does not require referring to the responses. ⚠ **The length gradient is larger and opposite** — short **33.3%**, long **0.5%** (seed-level). But seeds and write-ins are already length-matched in the release (14.6 vs 14.9 words), and write-ins resampled decile-by-decile to the seed length distribution still capture **16.2%** [13.6%, 18.8%] against seeds' **0.9%** [−0.7%, 2.6%], non-overlapping. Length is a strong *within*-class moderator and cannot be the *between*-class explanation |
| [r75](rounds/r75_menu_read_direction) | Does a criterion's direction track which response its own author ranked best? | **yes — the M → S_i path, observed rather than inferred.** A write-in carries its author's `annotator_id`, and that author's own world ranking is in the release, so criterion, sign and ranker join with no aggregation across people. Over **9,122** write-ins, overlap with the rater's own top response minus their own bottom is **+0.0407** for criteria they scored positive and **+0.0039** for negative — gap **+0.0368** [+0.0298, +0.0439]. Residualising containment on response length within prompt (longer answers overlap everything and rank higher) leaves **+0.0203** [+0.0147, +0.0257]; shuffled signs collapse to −0.0033. ⚠ **Asymmetric**: positive criteria track the preferred answer (+0.0176 residualised), negative ones are flat (−0.0027) — praise is drawn from the menu, criticism much less so. ⚠ Association within a rater, not causation: it cannot say whether the menu *created* the direction or supplied the *words* for one already held — that separation needs S_pre |
| [r76](rounds/r76_absence_cannot_overlap) | Is r75's asymmetry real, or can an absence just not overlap? | **real — the mechanical rival loses on its own prediction.** A criterion about an absence (*"fails to mention X"*) cannot lexically overlap the text that lacks it, which would explain flat negatives with no claim about raters. It doesn't: absence-shaped wording is only **4.1%** of write-ins (3.6% of positives, 5.0% of negatives), far too rare to flatten 2,880 negatives. The deciding prediction — that **presence-type** negatives should track the *worst* answer — fails: **−0.00278** [−0.00733, +0.00168], CI spanning zero. And absence-type **positives** show the *largest* effect (**+0.03814**), the opposite of what the rival predicts. Gap survives in both partitions: presence **+0.01955** [+0.01388, +0.02500], absence **+0.03945** [+0.01691, +0.06134]. ⚠ The shuffled-sign null for presence-type is **+0.00409**, about a fifth of the observed gap — small but not zero, and stated rather than rounded away |
| [r77](rounds/r77_topicality_control) | Is the menu-reading just topicality? | **no — it survives stripping every word the prompt supplied.** The strongest rival r75/r76 left standing: the best-ranked answer is plausibly the one engaging the *question* most fully, so it reuses prompt vocabulary, and criteria are about that question too — association with no rater reading anything. Removing from each criterion the tokens the prompt already supplied (**16.1%** of content words on average; only **14 of 9,122** criteria emptied, 0.2%), the positive-minus-negative gap goes **+0.02025** → **+0.02114** [+0.01569, +0.02647] — **104% retained**. Shuffled-sign null **+0.00052**. So the overlap is with what that *answer* said, not with what the *question* was about |
| [r78](rounds/r78_tokeniser_robustness) | Does the r75 line depend on the stoplist I typed by hand? | **no — 18 of 18 cells exclude zero.** `containment` uses ≥4-character tokens and a hand-written stoplist including *response, answer, model, user* — words a criterion can be about — and three rounds were built on it without varying it. Across min-length 3/4/5 × stoplist project/none/sklearn × unigram/bigram: **all 18 positive, all excluding zero**, largest shuffled null 0.0047. ⚠ **The spread is one axis, not scatter**: unigram cells average **+0.0199**, bigram **+0.0073** (2.7×), so the all-cell median +0.0121 would hide the only choice that moves the number. The two things I *did* choose barely matter — min length gives +0.0193/+0.0197/+0.0204, stoplist +0.0209 (mine) / +0.0173 (none) / +0.0212 (sklearn). Bigram is smaller because adjacent pairs must match exactly; a stricter measure returning a smaller positive number is what it should do |
| [r79](rounds/r79_semantic_menu_read) | The rival I said I couldn't build: measure it **semantically** | **direction survives; size does not transfer.** Every earlier control varied the *tokeniser*, not the decision to use lexical overlap at all. Replacing containment with embedding cosine in the backbones r39/r40 already use: **qwen +0.00626** [+0.00388, +0.00867], **phi +0.00043** [+0.00013, +0.00074] — both positive, both excluding zero, nulls −0.0007 and +0.0001. ⚠ **They differ 15× in magnitude**, while r68 measured these same backbones agreeing at 0.9132 on another quantity — so the semantic effect is real in direction and **instrument-dependent in size**. ⚠ **internlm ran under a cache shim and returned 100% NaN — refused** (`DynamicCache.from_legacy_cache` removed in transformers 5.x; a shim restores execution but `hidden_states[1]` is already NaN, so the vendored attention code is broken against this version) — named and refused, not omitted. **⚠ There is no three-lineage *judge* panel and never was** — [r80](rounds/r80_panel_freeze) separates the **judge** panel (qwen + phi, full size, r22's `usable_families=['phi','qwen']`) from the **encoder** panel (qwen + phi + internlm, r39's cache). internlm breaking cost the ability to *regenerate* encoder features, not a judge, and r39's cache — which r40 and r68's 0.9132 rest on — was built in an environment no receipt in this repository records. Cosine and containment share no scale, so **no comparison to the lexical +0.02114 is licensed** — only the sign and the exclusion of zero transfer |
| [r67](rounds/r67_predictor_reliability) | How reliable are the predictors behind the "refuted" rows? | **0.657 Spearman-Brown**, so every detection floor in the exhaustion ledger **multiplies by 1.23×**. Split-half on a prompt's criteria, 2-2, 241 prompts (9 excluded for K<4); controls: self-correlation 1.0000, shuffled half +0.0992. r54's floor was reported here as **0.300** — ⚠ **superseded**: [r69](rounds/r69_r54_predictor_reliability) measures r54's own predictor at 0.4381, not 0.657, so its floor is **0.367**. ⚠ The 1.23× does **not** apply to r40: an embedding distance has no criteria to split, and its three lineages agree (−0.1324, −0.1428, −0.1011, SD 0.0217), so its floor is reported as the range **0.180–0.222** |
| [r66](rounds/r66_r56_reconstruction) | Can r56's preregistered failure be recomputed? | **no, and r56 has no code in this repository.** `rounds/r56_semantic_selectivity/` has held only `PREDICTION.md` in every commit it has ever appeared in; its CI bounds **0.1592** and **0.2880** appear in no artifact anywhere. Reconstructing from the persisted tensors gives discovery **+0.0365** vs published +0.1806 and held-out **+0.0985** vs +0.0198 — **neither reproduces**, so by this round's pre-declared null it is **UNVERIFIED about r56, not a refutation**. ⚠ r56's *conclusion* survives: the recomputed held-out CI **[−0.0188, +0.2124] includes zero**, failing its own preregistered criterion. ⚠ This reconstructs a **number** and does not re-adjudicate whether the quantity was worth measuring |
| [r56](rounds/r56_semantic_selectivity) | Does semantic selectivity collapse explain the drop? | **NOT REPLICATED** (+0.1806 discovery → +0.0198 held out, predicted [+0.06,+0.30] with CI excluding zero). ⚠ **No code and no results file exist for this round** — the numbers live in commit `664c568`, `PREDICTION.md` and RETRACTIONS prose only, and [r66](rounds/r66_r56_reconstruction) could not recompute them |
| [r65](rounds/r65_edit_symmetry_floor) | Can τ_c's two arms be the same kind of edit? | **not for at least 18.62% of core criteria** — they carry a **deontic prohibition** (*"do not X"*), so satisfying is an **absence** and violating a **presence**, and the arms must insert categorically different content. ⚠ **A floor only**, and squeezed from both sides: a looser negation regex gives 21.31%, but its **105** extra matches are affirmative criteria with an incidental negation (*"Explain that… has **no** effect"*), while an affirmative surface still does not imply a symmetric edit. The null is its own finding — `coval_full`, **not** polarity-rewritten, sits at **12.85%**, so core is **1.45×** as prohibitive as the set it was compiled from: r44's +0.0733 rewrite changes **weights, not wording**. Upholds [ADVERSARY_FORECAST](ADVERSARY_FORECAST.md) objection 3 |
| [r64](rounds/r64_satisfaction_substudy_power) | How big must H_fresh's satisfaction sub-study be? | **two arms or nothing — 804 adjudications.** A single fresh-arm agreement rate has **nothing to compare against**: the release ships **no satisfaction labels at all**, so the judge's human agreement is unmeasured on originals too. The estimand is **Δ_sat = original − fresh**, in which the judge's unknown absolute accuracy cancels. **402 pairs per arm** at base 0.80, d=0.10, α=0.05, power 0.80, DEFF 1.37; **273–531** across the swept base rate. Answers [ADVERSARY_FORECAST](ADVERSARY_FORECAST.md) objection 4 |
| [r63](rounds/r63_r60_projection_audit) | Does r60's "not answerable" projection survive its own clustering? | **yes — objection 6 not upheld.** The design effect implied by r60's cluster bootstrap is **1.499** (half-width 0.03178 vs binomial 0.02595), so clustering was *already inside* the interval the projection scaled from. Pairs come from **238 of 250** prompts, top 26% carrying half — mild, not a pile-up; uniform-redistribution null returns **0.886**. The release's remaining pairs live in the other 718 prompts, so growth is **prompt-extensive** and DEFF holds; rater-intensive growth would raise it to 2.099 and inflate the requirement 1.40× |
| [r62](rounds/r62_matching_floor) | Can an unmatched criterion mean anything? | **not on its own — the floor is enormous.** Two authors who saw the **same four responses** on the **same prompt** write criteria that fail to match at **87.3%** (Jaccard≥0.20) and **53.3%** at the most lenient threshold tested. Cross-prompt null 99.6%, excess **+12.3** points, so the matcher does track prompt-specific content. **Upholds [ADVERSARY_FORECAST](ADVERSARY_FORECAST.md) objection 2**: the PRE/POST unmatched rate cannot be a primary outcome unless it clears a within-arm floor measured the same way. ⚠ Lexical matcher — a lower bound on agreement |
| [r61](rounds/r61_s_pre_power) | Can Experiment 1 detect anything? | **the baseline is 0.6459, not 0.5.** The POST arm writes **77.01%** positive criteria over 102,147 ratings (the neutral point used **once**), so two independent sign-assigners agree ~65% of the time by marginals alone — a naive test against 0.5 would report huge agreement while measuring the shared tendency to write positive criteria. Rater ICC **0.0915** → design effect **1.37** at 5 criteria/participant. MDE **0.0548** at 400 matched pairs; **3,001** pairs for 0.02. ⚠ The PRE marginal is unobserved by anyone and is **swept**, never assumed |
| [r60](rounds/r60_world_vs_personal) | When a person's WORLD ordering contradicts their own PERSONAL one, which does the rubric follow? | **the release cannot say.** On the **1,422** pairs a participant ordered one way for themselves and the other way for the world — the only pairs where the two make opposite predictions — the rubric sides with world on **0.5267** [0.4951, 0.5587] against an *exact* chance of 0.5; shuffled rubric 0.5183. **INCONCLUSIVE**, and the power statement is the finding: resolving δ=0.01 needs ~**14,358** reversed pairs and the entire release holds **2,444**, so the answerable margin is about **δ=0.024**. The only estimand here with human data on **both** arms. ⚠ **And the shortage is structural, not just small**: the `personal` block exists on **4,901 of 18,384** assessments (**26.66%**), on **none past a rater's fifth task**, and — the stronger fact — for only **321 of the release's 1,078 prompts**. The long-form and short-form prompt sets are **disjoint, intersection zero**: 757 prompts have no personal ranking at all, and **no prompt appears under both instruments**. Form, task position and prompt identity are all three perfectly confounded, so the missing pairs were never collected and no cross-form comparison is available to recover them |
| [r59](rounds/r59_criterion_influence) | How much does any ONE criterion matter to the judge's ranking? | **the rubric is robust to losing one, and not for the reason a claim card would predict.** Dropping a single criterion flips the top-1 response for **14.7%** of 991 criteria [12.6%, 17.1%] — **below** the **26.1%** from within-prompt column permutation, a null preserving each criterion's own spread and destroying only its link to the responses (paired **−0.1140 [−0.1483, −0.0797]**). ⚠ **Not own-rubric-specific**: criteria borrowed from *other* prompts flip at **14.9%**, so the agreement is a property of criterion rows against this response set, **not** a product of the compiler's compatibility selection. ⚠ **Judge-relative and equal-weight — this is not τ_c** |
| [r58](rounds/r58_equivalence_census) | Does r42's equivalence verdict describe the *package*? | **no — it describes its own hand-written population.** Enumerating every interval contrast finds **125**, of which r42 tested **21 (17%)**. Classified at δ=0.01: 60 real and material, 9 real but negligible, 24 no material effect, **9 INCONCLUSIVE**, 23 **UNVERIFIED** (a mean and a 95% CI were published but no raw paired vector, so the 90% CI TOST needs cannot be recovered). All 9 inconclusive cells are r43 group-weight contrasts. ⚠ UNVERIFIED is not folded into any pass, and **δ=0.01 is STIPULATED, not measured** |
| [r55](rounds/r55_overlap_selectivity) | …and can it move an *ordering*? | **no, equivalently so.** Own criteria are as selective about fresh responses (0.0776) as about the originals (0.0738); the own-minus-donor advantage goes +0.0518 → +0.0517, collapse **+0.0002 [−0.0056, +0.0059]**, equivalent to zero at δ=0.01. Closes r54's uniform-contribution escape. ⚠ Its own caveat: this **does not establish that no semantic selectivity changed** |
| [r54](rounds/r54_overlap_transfer) | Does the judge's overlap channel explain r12? | **the mechanism is real and does not explain it.** The own-vs-donor overlap advantage collapses from **+0.1294 to +0.0945** on fresh responses (drop +0.0349 [+0.0266, +0.0434]) — but it does not predict *which* prompts drop: corr **−0.0736 [−0.2059, +0.0612]**. A uniform contribution is **not** ruled out |
| [r29](rounds/r29_gold_ood) | Is the gold head itself unstable on fresh responses? | **stable — but that is reliability, not validity.** Two independently-fitted heads agree about as well on generated responses (0.590) as on released ones (0.543). Its own caveat: *"a bias common to both is invisible here"* — and [r47](rounds/r47_gold_is_length) later found one (length is an explicit feature of the shared architecture) |
| [r53](rounds/r53_join_audit) | Is the rubric↔prompt join every round rests on correct? | **yes, and the cutoff is not what defines the population.** Both fuzzy pairs are the same prompt up to a typo (0.9896, 0.9903). The 18 unmatched rubrics have median best-similarity **0.7727** to *any* released prompt — absent from the comparison file, not narrowly missed. Analysed set: **968 of 1,078 (89.8%)** |
| [r52](rounds/r52_overlap_intervention) | Does overlap *cause* the judge's score to move? | **yes.** Appending six distinctive tokens from response A rather than B moves the A-vs-B satisfaction gap by **+0.2507 [+0.2300, +0.2714]** for the *same* criterion; unrelated-token null **−0.0045**, spanning zero. The project's only interventional round. ⚠ bounds overlap-sensitivity on *perturbed* text |
| [r51](rounds/r51_judge_lexical) | What is the satisfaction judge actually using? | **it tracks lexical overlap.** Within a fixed (prompt, criterion), satisfaction across the four responses correlates with word overlap at **+0.2068** against a permutation null of −0.0034; **+0.1886** with response length partialled out. Gives r50's anchoring effect a live instrument explanation. ⚠ NOT shown to be error — overlap and real satisfaction covary, and the release has no satisfaction ground truth |
| [r50](rounds/r50_response_anchoring) | Is the transfer carried by criteria ABOUT the four responses? | **a design exists; it does not attribute yet.** Anchored write-ins carry more direction than generic ones (**+0.0271 [+0.0134, +0.0405]**), but the pre-seeded control trends the same way (+0.0106) and the **excess spans zero** (+0.0141 [−0.0050, +0.0326]). Withdraws my "no design permits this" claim (entry 52); does not settle the channel |
| [r49](rounds/r49_provenance_crossfit) | Does the direction transfer on criteria nobody else saw? | **yes, and better.** Size-matched, write-in criteria — one author, one rater — transfer at **+0.0777** vs **+0.0599** for the shared six; paired gap **+0.0172 [+0.0034, +0.0307]**. Control reproduces r34 (+0.0599 vs +0.0576); both shuffled-sign nulls strongly negative. Narrows shared-menu endogeneity to the RESPONSE channel |
| [r48](rounds/r48_provenance_identified) | Is the seed/write-in split a heuristic? | **no — identified.** 63.5% of criteria have 1 rater, 36.4% have ≥5, **18 (0.1%)** lie between and **zero** are ambiguous under the rounds' own rule. The many-rated class is capped at exactly **6 per prompt** (728/986 at the cap), matching documented pre-seeding. Does **not** reach S_pre: pre-populated ≠ response-blind |
| [r47](rounds/r47_gold_is_length) | Is the inversion a property of the gold PROXY? | **partly — and the round's own verdict says this is a SHARE, not a verdict: near enough to half that no binary reading is licensed.** gold↔length rises +0.08→+0.46 and +0.03→+0.55 across two samples; ~57% of the inversion survives length-residualisation against the procedure's own null; the fresh arm stops being negative in the held-out sample. Proxy matches human rankings on the ORIGINAL arm, which is where its length channel is weakest |
| [r46](rounds/r46_spread_replication) | Does the spread-loss effect hold out of sample? | **no — prediction committed to git first, then falsified.** +0.0496 [−0.068, +0.169] on 250 untouched prompts against a predicted [+0.12, +0.34]. Controls passed, and **r12's inversion itself replicated**: +0.0847 original, −0.0716 fresh |
| [r42](rounds/r42_equivalence) | Are the null claims equivalent, or just non-significant? | **equivalent at δ=0.01 — 0 of 21 contrasts inconclusive.** 4 are significant AND negligible. But only 7/21 hold at δ=0.005 and 4/21 at 0.0025, and **δ is stipulated, not measured**. ⚠ **Those 21 are four hand-listed rounds, not the package** — see [r58](rounds/r58_equivalence_census) |
| [r44](rounds/r44_compiler_lineage) | Which compiler step makes core beat full? | **polarity rewrite, +0.0733** — alone larger than the whole full→core total of +0.0662, and every reconstructed stage after it nets **−0.0183**. ⚠ That stage **applies the crowd's rating sign numerically** (`run.py:112`, *"the text rewrite cannot be simulated; its EFFECT can"*), so it is an **upper bound on what a text rewrite could achieve** — the real core must carry polarity in words to a judge that never sees a rating. ⚠ Compatibility selection **costs −0.0181** [−0.0241, −0.0125]; it beats a **size-matched random** choice by **+0.0149** [+0.0082, +0.0221], so choosing *which* four survive **recovers most of what truncating to four destroys and does not repay it** — membership is mitigation, not gain. Reconstruction explains 83%; **C1–C5 are unobservable**, so this describes my pipeline, not OpenAI's |
| [r45](rounds/r45_protocol_freeze) | What exactly do the humans rank? | 60 prompts, 4 equal cells, **540 responses hashed**, manifest `313044ea…`. r12's generation is unseeded, so this file is the only definition of the object H_fresh refers to. ⚠ `frozen_at_commit` was **hard-coded to `None`** and never stamped; `69bda3b9` is *recovered from git history* and bounds only when the frame entered the repository, not what tree the freeze ran against. `freeze.py` now stamps HEAD and a tree-dirty flag |
| [r43](rounds/r43_criterion_heterogeneity) | Does aggregate equivalence hide group conflict? | **conflict without consequence.** Country sign-reversals run **+0.0190 above** a label-permutation null; **0 of 17** group tests survive BH, and the significant ones split **2 positive / 2 negative** — symmetric noise. Positive control recovers an injected 20% flip (0.122→0.283) |

---

## What is unusual here

**[RETRACTIONS.md](RETRACTIONS.md) lists every claim this repository made and then killed.**
**120 entries** — 54 as table rows, 66 written out, numbered to 111. Most are a later round
destroying an earlier round's conclusion, and in every one of those both rounds are mine. Read by
round number this looks like a sequence of findings. It is not.

Every round carries its own null, and several of the killed claims are the author's own:

- a permutation null, a response-style control and a prompt-difficulty control (r01)
- a step-versus-trend model comparison rather than a fitted slope (r02)
- a permuted-identity null, not a chance baseline (r03)
- a shuffled-rubric arm and a length-only arm before any headline (r04)
- a no-compression control and a random-selection floor (r06)
- a pre-registered prediction that failed, reported as failed (r09)
- an independent-backbone control that retracted the author's own result (r11)
- an out-of-distribution transfer test that scoped the repository's own headline (r12)

**Two documents exist for the reviewer who has not read this**, and they do different jobs.
[assurance/ADVERSARY_BRIEF.md](assurance/ADVERSARY_BRIEF.md) is the mandate — what to attack and what
I most want checked. [ADVERSARY_FORECAST.md](ADVERSARY_FORECAST.md) is the scoring sheet: **six
objections with probabilities, committed before any review**, so a challenger's findings measure my
calibration rather than being absorbed into the text. All six have since been **self-examined and are
excluded from the hit rate** — what will matter is what a reviewer raises that is **not on the list**.

`assurance/` freezes **20 claims** against stated thresholds: **11 hold, 3 are marginal, 6 fail** —
including the one that scopes this repository's own headline. **An assurance package with no failures
is not an assurance package.** Twelve executable checks run beside it; their own defect histories are
in RETRACTIONS, because a check that has never been wrong has never been tested.

**And one thing that works is not an instrument at all.** The two most recent errors — a half-width
taken from the wrong interval, a reliability applied to the wrong kind of predictor — were caught by
**running the number before asserting it**, after twelve checks passed on both. Entry 111 measures a
thirteenth check built for that class: it would have flagged 82 numbers and caught **neither**. The
practice has a better record here than the apparatus, and it is written down because it is easier to
add a check than to keep a habit.

It also distinguishes `BROKEN_HARNESS` from `UNSUPPORTED`: when the repository was reorganised, every
claim source moved and the manifest silently resolved them all to "unmeasured". A package that cannot
tell "we never measured this" from "I can no longer find my own evidence" is not an assurance package
either.

---

## Reproducing

**Re-verified from a fresh local clone**, with no virtualenv inside it and `data/*.jsonl` absent
(they are gitignored — `python data/fetch.py` fetches them):

| | |
|---|---|
| round + assurance + `covalx` source files parsed | **94, 0 syntax errors** |
| assurance checks that run from a bare clone | **12 of 12** |
| data-free rounds that run from a bare clone | **5 of 7** |
| the other 2 (r61, r63) | fail on missing `data/*.jsonl` — the documented `fetch.py` step, deliberately skipped here |

**One real defect found and fixed:** `assurance/attack_the_suite.py` invoked
`<repo>/.venv/bin/python`, a path that exists only in a working copy, so it was the single check that
could not run from a clone. It now uses the interpreter that is running it.

**And the thing entry 113 flagged as unverified is now verified:** the persisted `.npz` tensors *are*
committed, so [r66](rounds/r66_r56_reconstruction) and [r67](rounds/r67_predictor_reliability) — which
import across round modules — both run from the clone.

```bash
python -m venv .venv && .venv/bin/pip install numpy pandas scipy scikit-learn torch transformers
python data/fetch.py                            # downloads + verifies 5 files by SHA-256, incl. the dataset card
python rounds/r01_rater_structure/run.py        # CPU only
python rounds/r04_rebuild_satisfaction/run.py   # needs a GPU
python assurance/manifest.py                    # regenerate the claim table
```

Judge and gold models are read from `COVALX_MODEL_2B` / `COVALX_MODEL_08B`, defaulting to the Hugging Face ids.

**Zero API spend — no paid inference is used anywhere.** That part is exact.

⚠ **The GPU-hours figure was one round's runtime described as the pipeline's.** `r04` is the only
round in this repository that records its own elapsed time — **1,352 s = 0.375 h** across its three
result files. **17 rounds use the GPU** (r04, r08, r09, r10, r11, r12, r13, r14, r15, r20, r21, r22,
r29, r39, r41, r46, r52) and **16 of them measure nothing**, so the true total is unmeasured and
strictly larger. The earlier "0.36 GPU-hours" is retained here only as what r04 cost; it was never
a pipeline measurement. **A cost claim that counts one round and names the whole is the same shape as
a population that counts what it can reach** — see [entry 102](RETRACTIONS.md).

---

## Boundaries

- The judge is a 2B base model. It reaches 0.686 pairwise against the ~0.60 the release authors report, but only 0.61 on picking a single best response against their ~0.75. Both numbers belong in any citation of this work.
- The gold preference model is learned from the same 18,384 rankings. It is not fresh human data and inherits the label bias and two-regime split found in r02.
- No new human data was collected. Nothing here establishes what any population would say.
- `consensus` in r06 is this repository's operationalisation, not OpenAI's LM-assisted synthesis. The released CoVal-core rubric scores **0.660** ([r04](rounds/r04_rebuild_satisfaction), `a04_core.json`) — but that is **not comparable to r06's 0.6575 arm**: r04-core is the released 3,899-criterion rubric on 968 prompts, r06's arms are k=4 compressions of `coval_full` on 945. Different rubric source, different panel, different compression. An earlier version of this line called them "level"; nothing in this repository has measured them against each other.

## Attribution

CoVal is © OpenAI, released under CC BY 4.0. This repository redistributes none of it; `data/fetch.py` downloads it and verifies the exact bytes the results were computed from.
