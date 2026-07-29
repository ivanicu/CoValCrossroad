# Preregistration — the three human experiments

> **Review status: `[unchallenged]`, not clean.** Every experiment below was designed, attacked
> and repaired by the same process that wrote it, and no independent reviewer has read it. What
> I expect an adversary to overturn is written down in advance in
> [`ADVERSARY_FORECAST.md`](ADVERSARY_FORECAST.md), so that when one runs, its findings score
> this document's calibration rather than being absorbed into it.

Written **before** any human data exists, which is the only time a preregistration means
anything. Frozen frame: `rounds/r45_protocol_freeze/results/r45_frozen_frame.json`,
manifest `313044eafe5d18a9335408f7c35a0e76f2b08e4a436f765cede756e78b3dfa4b`, 60 prompts,
**480 hashed responses** (60 prompts × 4 original + 4 fresh), four equal cells of 15. ⚠ This read **540** until 2026-07-29. 540 is the count of hashed **objects** — the 480 responses plus one `prompt_sha256` each — so the old figure overstated the responses by **60**, or 12.5%, in the document Experiment 2's per-response budget is read from. Found by pointing `readme_agrees_with_results` at this file for the first time.

Everything in this repository is now blocked on one of the three counterfactuals below. They do
not exist in any public data and cannot be computed from it — **74 rounds** now carry a non-smoke
result, and the exhaustion ledger in the README enumerates the thirteen mechanisms tried, five
genuinely refuted and five limited by their own detection floors. ⚠ *"Exhausting the alternatives"*
was asserted here for a long time as **45 rounds** without either updating the count or enumerating
what had been exhausted; both are now done, and the honest form of the argument is the ledger with its
floors, not the round count.

---

## Why these three and nothing else

The object is `M(R, J, π, Q, P)` — a rubric is a scoped, compiled, context-indexed normative
measurement program, and each layer needs separate validation. The layers this release **can**
reach have been reached. What remains is exactly what the release's own protocol design
forecloses:

| unknown | why no computation can reach it |
|---|---|
| **S_pre** — response-blind criterion direction | **nobody in the release rated a criterion before seeing four responses.** Verified field by field. Every isolation rung r37 can climb is a rung *within* post-exposure data |
| **H_fresh** — human rankings on unseen responses | the release contains human rankings only for the four candidates the criteria authors saw |
| **τ_c** — the causal effect of one criterion | requires intervening on a response's satisfaction of one criterion while holding the rest fixed. No observational contrast identifies it |

---

## Experiment 1 — S_pre: is the direction response-blind?

**The question.** r34 showed the post-ranking criterion direction generalises across people
(+0.0576 cross-fitted). That refutes *individual* circularity. It does **not** touch shared-menu
endogeneity: every participant saw the same four responses, so `menu → shared salience → Sᵢ` can
produce cross-rater agreement that is still menu-induced construction.

**Two scopes on that +0.0576, both established after this section was first written.**

- r34's estimate is computed on the **majority-rated 36.5%** of criteria — 5,564 of 15,248 — a
  filter five rounds shared without stating it (entry 51). r48 then showed that subset is
  **structurally identified**: the pre-seeded six per prompt, 0.1% ambiguous.
- **r49 tested the discarded 63.5%** and the direction transfers *better* there: write-in criteria,
  authored by **one** participant and rated by **only** that participant, carry **+0.0777**
  [+0.0674, +0.0883] against **+0.0599** [+0.0514, +0.0687] for the shared six — paired gap
  **+0.0172** [+0.0034, +0.0307], excluding zero.

**So one channel of shared-menu endogeneity is already closed and this experiment must not be sold
as testing it.** Shared criterion *text* is excluded: a criterion no other participant ever saw
still transfers. What survives is shared **response exposure** — every write-in was still authored
after reading the same four candidates, and there *"shared-response artifact"* and *"population
property"* make the same prediction (r49). **That, and only that, is what the PRE arm separates.**

**Design.** Two arms, between-subjects, same prompts.

| arm | procedure |
|---|---|
| **PRE** | shown the prompt only. Writes criteria and assigns each a direction, **before seeing any response** |
| **POST** | the released procedure: ranks four responses, then rates seeded criteria |

**Primary outcome, declared now.** Agreement between PRE-arm directions and POST-arm directions
on the same criterion, measured as the rate at which the two arms assign the same sign, against a
chance baseline computed from each arm's own marginal sign distribution — **not** against 0.5,
because the POST arm's signs are overwhelmingly positive and a naive baseline would manufacture
agreement.

**⚠ "The same criterion" names a step this design did not specify, and it is load-bearing.** PRE
participants **write their own** criteria; POST participants **rate pre-seeded** ones. Those are not
the same objects, so every PRE/POST sign comparison passes through a **matcher**, and an unnamed
matcher is exactly the defect that broke Experiment 3's check. A semantic matcher is the obvious
choice and the worst one available here: r14 measured that a *model* paraphrase flips **15.4%** of
this judge's Yes/No verdicts where a *mechanical* rewording flips **2.5%**, so a model asked whether
two criterion texts "are the same criterion" is operating in its least stable regime.

**Committed: matching is HUMAN, blind, and adjudicated.** Two annotators who see neither arm's
directions match PRE criteria to POST criteria; disagreements go to a third. Inter-matcher agreement
is reported. A model matcher may be run **alongside** and its disagreement rate with the humans
reported, but it never produces the primary number.

**And the unmatched rate is not an exclusion — but it is only interpretable as an EXCESS.** A POST criterion with no PRE counterpart *may* be one that only arises after seeing the responses. It may equally be one nobody could match to anything. [r62](rounds/r62_matching_floor) measured that floor on the release: two authors who saw the **same four responses on the same prompt** write criteria that fail to match each other **87.3%** of the time at Jaccard ≥ 0.20, and **53.3%** at the most lenient threshold tested — against a cross-prompt null of 99.6%, so the matcher is tracking real content and the floor is real too.

**So: committed.** The unmatched rate is reported as an **excess over a within-arm floor measured in the same study with the same human matchers** — PRE participants matched against each other, POST against each other, and the raw rate never quoted without both. A design that reported the PRE/POST rate alone would be reporting mostly the idiosyncrasy of free-text criterion writing and calling it menu-induced construction.

**Predictions, committed before data.**

| world | prediction |
|---|---|
| direction pre-exists the menu | PRE/POST sign agreement high; PRE-derived weights predict POST rankings about as well as POST-derived ones |
| direction is menu-constructed | agreement near the marginal-matched baseline; PRE weights predict poorly |
| partially constructed | agreement above baseline but PRE weights strictly worse — the expected outcome, and the one requiring an effect *size*, not a test |

**⚠ THE SCALE'S MIDPOINT IS NOT A HYPOTHETICAL — it was measured and it is unavailable in practice
([r82](rounds/r82_scale_use_by_provenance)).** Across **102,147** released ratings on a 21-point
−10…+10 scale, the midpoint **w = 0 was used exactly once**. Two consequences for this design, both
measured rather than assumed:

1. **The neutral option is not a refinement, it is the missing level.** A participant with no view had
   no way to say so, and every such view was recorded as a signed weight. That is the state this arm
   exists to change.
2. **The scale carries far less resolution than its 21 points suggest**
   ([r82](rounds/r82_scale_use_by_provenance)). **29.55%** of all weight mass falls on just **5 or
   10**, and **16.96%** on \|w\| = 10 alone.
   ⚠ **And the magnitudes' predictive contribution is already measured — I nearly rebuilt it.**
   [r32](rounds/r32_channel_decomposition) has the cell: moving from **sign** to **signed magnitude**
   is worth **+0.0055 [+0.0018, +0.0094]**, against **+0.0876** for the sign itself — so magnitude is
   **6.3%** of the sign channel. Reported the way this document requires: the effect **differs from
   zero** *and* is **practically equivalent to zero at the preregistered δ = 0.01**, its whole interval
   lying inside the margin. So the correct statement is not that magnitude carries nothing, but that
   **asking for a number on a −10…+10 scale buys about a sixteenth of what asking for a direction
   buys** — which bears on Experiment 3's design as much as on this one.

**Registered directional prediction, with its way to be wrong.** r82 found that low-magnitude ratings
(\|w\| = 1 or 2) are **19.21%** of *pre-seeded* criteria against **6.98%** of *participant-authored*
ones — a gap of **+0.1223** against a within-prompt permutation null of [−0.0016, +0.0095]. **Two
explanations survive that finding and r82 cannot separate them**: displacement (people with no view
were forced to a signed weight, and reached for the smallest one) or selection (you author a criterion
*because* you already care, so it earns a strong weight).

> **Prediction:** if displacement is doing the work, adding *"no general direction"* will absorb a much
> larger share of the **seed** low-magnitude mass than of the **write-in** low-magnitude mass.
> **If it absorbs both roughly equally, displacement is not the explanation** and r82's gap is
> selection — a result that would retire the forced-choice worry rather than confirm it.

**And the cost side of that arm is now measured, not assumed
([r83](rounds/r83_low_magnitude_drop)).** A neutral option only helps if absorbing those ratings does
not throw away signal the rubric is using. Deleting **every** rating with \|w\| ≤ 2 — **18,154 of
100,530**, 18.06% of all ratings — and recomputing each criterion's weight from the survivors moves
agreement with **real human** pairwise rankings by **−0.0000248**, equivalent to zero at δ = 0.01 by a
factor of **403**. The arm that makes that mean anything is a **size-matched random deletion**
repeated 200×: **0.6832** [0.6803, 0.6865] against the targeted **0.6860**. So removing the weakest
fifth of all ratings costs nothing, while removing as much arbitrary data costs ≈0.003.

> **Design consequence, claimable rather than hoped for:** adding *"no general direction"* is **free at
> the aggregate level**. If it absorbs the low-magnitude mass, Experiment 1 loses no predictive signal.
> ⚠ It does **not** follow that it is free at the *criterion* level — r83 deleted ratings and measured
> the aggregate, so a neutral option could still change which individual criteria survive compilation.

This is registered now, before any data, because the same evidence supports both readings and choosing
between them afterwards would be a narrative. It is also the **only** prediction in this document
contributed by a round that explicitly could not test its own hypothesis.

**A neutral option must be on the screen in both arms.** r35 established only that abstention
*after the fact* costs nothing; it could not simulate what a participant would do given
"no general direction", "depends on implementation", or "cannot judge without seeing a response"
**at elicitation time**. Their usage rates are a primary outcome, not a nuisance.

**Power, computed from the release rather than deferred to the pilot ([r61](rounds/r61_s_pre_power)).**
The POST arm's sign marginal is **measured**: **77.01%** positive across 102,147 released ratings
(the count is [r82](rounds/r82_scale_use_by_provenance)'s; r61 stores the marginal, not the total),
with the neutral point used **once**. So if the PRE arm shared that marginal, two independent
sign-assigners would agree **0.6459** of the time **by marginals alone** — a test against 0.5
would report agreement far above chance while measuring nothing but a shared tendency to write
positive criteria. Rater clustering is real: ICC **0.0915** across 1,108 raters, giving a design
effect of **1.37** at 5 criteria per participant.

| matched criterion pairs | minimum detectable departure from baseline |
|---:|---:|
| 400 | **0.0548** |
| 1,600 | 0.0274 |
| **3,001** | **0.02** |

⚠ **The PRE marginal is unobserved by anyone** — no participant in this release wrote a criterion
before seeing responses, which is why S_pre needs an experiment — so it is **swept** across
0.50–0.95 and every figure is conditional on the swept value. Across that sweep the room above
chance never falls below **0.2569**, so sign agreement is not ceiling-compressed.

**The baseline needs no further adjustment for the seed class, and this was checked rather than
assumed ([r73](rounds/r73_direction_from_text_alone)).** A worry the design does not address on its own:
if a criterion's direction were recoverable from its *wording*, a PRE participant could score well
above 0.6459 while reproducing a phrasing convention rather than a prior. Measured on exactly the class
an S_pre participant faces — pre-written, response-blind seed criteria — a text-only predictor with
prompts held out captures **1.2% of available headroom** (+0.0020 [−0.0007, +0.0049]), and its
*in-sample* fit clears the marginal by only +0.0160, so this bounds learnable signal rather than
reporting a held-out miss. **r61's 0.6459 stands for the seed arm.**

⚠ **It does not stand for any arm built on write-in text.** There a text-only predictor captures
**26.4%** of headroom (+0.0821 [+0.0746, +0.0904]). Any variant of this experiment that shows
participants participant-authored criteria must use a **text-only predictor as its baseline**, not the
marginal. Registered here because discovering it after the data would make the choice of baseline a
narrative.

**Registered directional prediction, from [r74](rounds/r74_specificity_vs_exposure).** Text-only
predictability within write-ins is strongly moderated by length — short criteria capture **33.3%** of
headroom, long ones **0.5%** — while seeds and write-ins are already length-matched in the release
(14.6 vs 14.9 words). So: **if the PRE arm's criteria come out systematically shorter than the POST
arm's, the two arms are not comparable on sign agreement alone** and criterion length must be reported
and matched. This is a design failure mode, not a hypothesis, and it is cheap to monitor.

**Stopping rule.** Fixed n, decided from a pilot of 20 participants per arm, **and the target n
is now derived rather than guessed**: state the departure worth detecting, read the pair count
off the table above, divide by the expected match rate. No optional stopping.

---

## Experiment 2 — H_fresh: do the criteria predict choices on responses nobody wrote them for?

**⚠ WHAT THIS EXPERIMENT CANNOT TEST, AND WHY THAT IS CORRECT** (entry 160). The frozen frame is
**100% long-form** prompts, and the inheritance is traceable: `data/comparisons.jsonl` is sorted by
collection form (lines 0–320 long, 321–1077 short); r12 takes a head slice `[:250]`, so its prompts are
entirely long-form; `r45/freeze.py` draws the 60 from **r12's saved generations**. H_fresh is *defined*
as human rankings on **r12's exact saved fresh responses**, so it could not have been otherwise.

- **What it will therefore establish:** whether r12's inversion survives replacing the model gold head
  with real humans, **on r12's instrument**.
- **What it will not:** anything about the **757 short-form prompts**. Those have no personal ranking,
  no unacceptable check, and were never in r12's slice.
- **The only cross-form evidence available** stays [r46](rounds/r46_spread_replication) — 83.6%
  short-form, showing the same inversion (+0.0847 → −0.0716). Uncontrolled, since no prompt exists
  under both forms, and not upgradeable by this experiment.

**This is registered rather than fixed.** Extending H_fresh to short-form prompts would require
generating a new fresh response set, which breaks comparability with r12 — the one thing this
experiment exists to test against. The bound is the right trade and is stated so that a later reader
does not mistake H_fresh's silence about the short form for evidence about it.

**⚠ REGISTERED BEFORE THE DATA: positive and negative criteria must be collected and analysed
separately, and here is the prediction that says why.** [r75](rounds/r75_menu_read_direction) joined
each write-in to *its own author's* ranking — 9,122 criteria, no aggregation across people — and found
that overlap with the response that rater ranked **best**, minus the one they ranked **worst**, is
**+0.0407** for criteria they scored positive and **+0.0039** for negative; gap **+0.0368** [+0.0298,
+0.0439], **+0.0203** [+0.0147, +0.0257] after residualising containment on response length within
prompt. The effect is **asymmetric**: praise tracks the preferred answer (+0.0176 residualised),
criticism is flat (−0.0027).

[r76](rounds/r76_absence_cannot_overlap) tested the mechanical rival — an absence has no words to
overlap — on the prediction only that rival makes, and it failed: presence-type negatives do **not**
track the worst answer (−0.0028 [−0.0073, +0.0017]), absence-shaped wording is only **4.1%** of
write-ins, and absence-type *positives* carry the **largest** effect (+0.0381).

**So the registered expectations for H_fresh are:**

1. **Pooling positive and negative criteria will understate whatever is measured**, because the two
   classes do not behave alike. Report them separately as a primary analysis, not a subgroup.
2. **Predicted, with a way to be wrong**: on the saved fresh responses, criteria whose direction was
   assigned positively will show a *larger* association with the new rankings than negative ones. If
   the difference is **zero or reversed**, the menu-reading account developed in r75/r76 does not
   transfer off the original menu, and that is a result about construction, not a nuisance.
3. **⚠ The one thing none of this settles**, stated so it is not quietly assumed later: r75 measures
   association *within* a rater and cannot separate a menu that **created** the direction from one that
   **supplied the words** for a direction already held. Only Experiment 1 separates those. H_fresh must
   not be read as evidence on that question in either direction.


**The question.** r12 found the own-rubric advantage *inverts* on fresh responses, replicated on
250 untouched prompts by r46. r40 ruled out monotone degradation under three generic distance
metrics; r41 ruled out criterion-space support, and its one apparent survivor —
discriminating-power loss — **failed to replicate** (r46, entry 48). r47 then found the outcome
variable itself carries part of it: roughly half the inversion rides on the gold proxy's length
channel, and on held-out prompts the fresh arm stops being negative once length is removed
(entry 50).

**One more mechanism was proposed and closed after this section was written.** The judge's lexical
channel is real and **causal** (r51, r52) — the obvious candidate for r12. It does not explain it:
the own-vs-donor overlap advantage collapses from **+0.1294 to +0.0945** on fresh responses
(drop +0.0349 [+0.0266, +0.0434]) but **does not predict which prompts drop** (corr −0.0736
[−0.2059, +0.0612], r54), and the ordering component is **equivalent to zero at δ = 0.01** — own
criteria are as selective about fresh responses as about originals, collapse **+0.0002**
[−0.0056, +0.0059] (r55). So a mechanism with a measured causal effect on the judge still fails to
account for the transport failure, which is the strongest available argument that H_fresh is not
answerable by any further computational round.

**So what needs humans is now sharper.** That the advantage *fails to transfer* replicates on two
samples. That an unrelated rubric *beats* the own rubric there is **withdrawn**. H_fresh decides
whether the failure to transfer is a fact about rubrics or about model-scored proxies — which is
why length is a recorded variable below, not a covariate chosen afterwards.

**Design.** Participants rank the **four frozen fresh responses** for a prompt. Exactly the
responses in the manifest — this is why they are hashed.

**⚠ WHICH ranking, and it was never specified.** CoVal collected **two** orderings per assessment:
*personal* (*"their own personal values and preferences"*) and *world* (*"best for the world
overall… rather than just their personal taste"*). Every number this experiment is compared against
— r12's +0.102 → −0.064 included — is measured on the **world** ranking (`covalx/judge.py:245`).
H_fresh must therefore collect the **world** ranking or it is not comparable to the quantity it
exists to check.

**Committed: collect BOTH, with world as primary.** The personal ranking exists for **26.7%** of
released assessments (4,901 of 18,384) and this project has never used it. **Where both exist they disagree often**: the two orderings are identical in only **53.2%** of cases, the top choice differs in **29.0%**, and **9.70%** of strict world pairs are *reversed* in the personal ordering.

**⚠ But the world-vs-personal CONTRAST is out of reach, and that is committed now rather than discovered after collection.** r60 ran it on the release: on the 1,422 reversed pairs it could reach, the rubric sides with world on **0.5267** [0.4951, 0.5587] — inconclusive, with a half-width of 0.0318. Resolving δ = 0.01 needs about **14,358** reversed pairs; the *entire* release holds **2,444**. H_fresh at 60 prompts × ≥8 raters yields on the order of **10²**. So collecting the personal ranking is worth its one extra screen for **descriptive** reporting and for reuse, and **it is not powered to answer whether the rubric tracks the normative or the preference ordering**. That must not be claimed from it. Collecting both costs one extra screen and
yields a contrast the release can support and nobody has run — *does a values rubric predict the
normative ordering better than the preference ordering?* Personal is **secondary and labelled
exploratory**; world is the primary outcome, because that is the one r12 measured.

**Sampling.** The r38 frame: 60 prompts, four equal cells crossing rubric-vs-proxy disagreement
with surface distance, sampling weights 2.80 / 3.67 / 5.53 / 4.67, ≥8 raters per prompt. Weights
are reported with every estimate so one collection yields **both** a population estimate and an
anomaly-subset estimate. Power ≈0.98 for +0.05 clustered on prompt; r12's 0.16 is detectable in
every cell.

**Why PROMPT is the clustering unit, and what that frees**
([r90](rounds/r90_resampling_unit), [r93](rounds/r93_clustering_unit_transfers), 2026-07-29). r90
measured all three units on the release: prompt clustering **dominates**, the annotator-clustered
interval is **0.45×** the prompt one, and the two-way crossed interval is only **2.0%** wider than
prompt-only on attribution and **8.3%** on agreement. The mechanism is that an annotator bootstrap
still covers ~every prompt, so it barely resamples the prompt axis.
**r93 checks that this transfers to *this* design rather than assuming it.** A prompt is lost only
when **all** its raters are missed — `P = [(1−1/n)ⁿ]^RPP ≈ e^−RPP` — so the binding parameter is
**raters-per-prompt**, already fixed at **≥8**, and *not* the crossing. Across prompts-per-rater from
**1 to 60**, two orders of magnitude, coverage moves by **0.01%** (99.9667% → 99.9806%).
- **Consequence, and it is a freedom rather than a constraint: prompts-per-rater is NOT fixed here.**
  Choose it on fatigue, recruitment cost and order-effect grounds — clustering on prompt stays
  justified at any value. Note the order-effect evidence below is itself per-participant, so k
  interacts with the priming window, not with the clustering choice.
- **The ≥8 floor is doing the work, so it is not negotiable downward.** At k=8, coverage falls to
  **95.2%** at 3 raters per prompt, **86.7%** at 2, and **63.5%** at 1. A design that thinned the floor
  below ~5 would become crossing-sensitive and this justification would lapse.
- **What does not transfer:** r90's variance *components*. Whether prompt clustering dominates in
  H_fresh's actual data is measurable only from H_fresh's actual data, and is not assumed here.

**Power for PER-PROMPT correlate analyses, which is a different question and was nearly missed.**
r38's power figure is for a **mean difference**. Any analysis that correlates a per-prompt
covariate with the per-prompt attribution is limited instead by the *reliability* of that
per-prompt quantity — and r57 (entry 55) found the model-proxy version is barely reliable
(0.302 / 0.422 across two samples), which silently capped six mechanism searches at a detection
floor of true *r* ≈ 0.2.

The human outcome is **much better**, measured directly on the released ratings for the original
responses rather than assumed:

| raters/prompt | reliability | attenuation √rel | smallest true *r* detectable at n=60·weights |
|---:|---:|---:|---:|
| 6 | 0.644 | 0.802 | 0.16 |
| **8 (the frozen protocol)** | **0.707** | **0.841** | **0.15** |
| 12 (median in the release) | 0.783 | 0.885 | 0.14 |
| gold proxy, for comparison | 0.302 | 0.549 | 0.23 |

Averaging 8 humans per prompt buys a per-prompt outcome roughly **2.3× more reliable** than the
single gold ordering every computational round has used. So H_fresh can support per-prompt
correlate analyses that the proxy could not — and any such analysis must still **state its
detection floor before it runs**, because a null below that floor is silence.

⚠ The detection floors above use the n=250 CI half-width for comparability with r57. H_fresh has
**60** prompts, so its own floors are larger by roughly √(250/60) ≈ 2.0×; the *ranking* of the
outcomes is unaffected but no per-prompt correlate analysis on 60 prompts should be planned as
primary.

**Primary outcome.** Own-rubric minus reference-rubric concordance against **human** rankings on
fresh responses — the quantity r12 estimated against a model proxy.

**⚠ This replaces ONE model in the chain, not both.** r12 scores both sets with
`Judge(MODEL_DIR, batch=32)` (`rounds/r12_response_set/run.py:208`). Human rankings replace the
**gold head** — the ranking target — and leave the **satisfaction layer** model-produced. The
rubric side of "own-rubric concordance" is still a judge deciding *does response r satisfy criterion
c?*, and that judge scores lexical overlap **causally** (r51, r52).

**The instrument carries exactly the validity gap this experiment exists to measure.** r04 validates
the satisfaction layer against human rankings on the **released** responses — 0.686 on 80,542 pairs
— and nothing validates it on **fresh** ones. So H_fresh would measure transport failure using a
satisfaction layer whose own transport is unestablished. That is not a reason to abandon the
experiment; it is a reason not to describe its result as human-measured without qualification.

**Committed: a TWO-ARM satisfaction sub-study, sized, with an invalidation rule
([r64](rounds/r64_satisfaction_substudy_power)).** The earlier one-arm version could not have
worked: **the release ships no satisfaction labels at all** — rebuilding them is why r04 exists —
so the judge's agreement with humans is unmeasured on ORIGINAL responses too, and a lone
fresh-arm number would have had nothing to be compared against.

- **Estimand:** `Δ_sat` = human-judge satisfaction agreement on **original** pairs **minus** the
  same on **fresh** pairs. The judge's unknown absolute accuracy cancels in the difference.
- **Size:** **402 adjudicated (criterion, response) pairs per arm, 804 total**, at a base rate of
  0.80 and a difference of 0.10, α = 0.05, power 0.80, design effect 1.37 from r61. The base rate
  is **unmeasured** and swept 0.60–0.90, over which the requirement runs **273–531** per arm, so
  the pilot estimates it before n is fixed.
- **Sampling frame:** pairs drawn from the frozen 60-prompt frame, stratified by its four cells,
  balanced across the two arms so the same criteria appear in both.
- **INVALIDATION RULE.** If `Δ_sat` is significantly positive **and** its magnitude exceeds the
  observed change in the own-minus-reference gap, the transport failure is attributable to the
  **satisfaction layer** and H_fresh's primary result is reported **UNVERIFIED for transport** —
  not annotated, not reworded. If the sub-study is not run at all, the primary result is reported
  as *"human rankings against a model-scored rubric"*, never as *"human-measured"*.

**Committed in advance:**
- **response length is recorded for every response and reported with every estimate**, and the
  primary outcome is reported both raw and with within-prompt length partialled out. r47 showed
  the model proxy's correlation with length rises from ~+0.05 on released candidates to ~+0.50 on
  generated ones, and that roughly half the observed inversion rides on that channel. Without
  length, human rankings on the frozen responses **cannot** separate "the rubric fails to
  transport" from "the proxy was reading length"
- the contrast is **own-rubric vs reference-rubric**, and it will **never** be described as
  values vs non-values
- the reference rubric is drawn by the r19/r30 donor procedure, and the **floor donor is named in
  the headline** — it moves the answer 2.47×
- results are reported **per judge family**, never averaged, because r22 showed the judge moves
  the floor as much as the donor does
- significance and equivalence at δ = 0.01 are reported **separately**, per r42

**The decisive comparison.** If the human-measured advantage on fresh responses is clearly positive
while the proxy-measured one is at or below zero, **r12 was a proxy failure** and the transport
claim dissolves. If the human-measured advantage is at or below zero too, transport failure is
real and this project's central negative result stands on human data for the first time. Note the
predicted quantity is now **zero, not negative**: after r47 the licensed proxy-side claim is
absence of advantage, not inversion, so a human result near zero *confirms* rather than
contradicts.

---

## Experiment 3 — τ_c: does changing one criterion change the choice?

**The question.** Everything in CoVal is observational. No contrast in it distinguishes
*"this criterion explains the choice"* from *"this criterion co-occurs with what explains it"*.

**Design — SYMMETRIC pairs, not base-vs-edited.** For a prompt with rubric criteria c₁…c_K and a
base response R, generate **two** edits of the same base:

| arm | construction |
|---|---|
| **R⁺** | edited to *satisfy* criterion c |
| **R⁻** | edited to *violate* criterion c, matched to R⁺ in length and in lexical distance from R |

Participants choose between **R⁺ and R⁻**. The base R is never shown as an option.

**Why symmetric, and not the obvious base-vs-edited pair.** Two reasons, and the first was nearly
missed.

1. **The manipulation check's instrument responds to editing itself.** r51/r52 show the judge scores
   lexical overlap *causally*, so comparing an edited response against an unedited one makes every
   criterion's judged satisfaction move — the check for *"the others did not change"* would be
   reading the edit, not the criteria. Under symmetry the check becomes
   `s(c_j, R⁺) − s(c_j, R⁻)` for each j ≠ c: both arms are **the same kind of object**, so whatever
   effect editing has cancels in the difference. **This is exactly r52's own design logic** — *"the
   appendage is the same KIND of object in both arms, so whatever effect gluing a token list onto a
   criterion has cancels"* — turned on the check instead of on the judge.
2. **Base-vs-edited also confounds the OUTCOME.** One response would be machine-edited and the other
   not, so a participant could prefer the unedited one for fluency artifacts having nothing to do
   with criterion c. Symmetry removes that confound outright rather than controlling for it.

**Verification, in three layers, because no single one is sound alone.**

- **Constructibility screen, before anything else, with its rate as a headline.** Each criterion is
  judged for whether a matched two-sided edit exists at all — and it often does not.
  [r65](rounds/r65_edit_symmetry_floor) measures a **floor of 18.62%**: that share of core criteria
  is prohibitive on its surface (*"do not provide step-by-step tactics"*), so satisfying is an
  **absence** and violating a **presence**, and the two arms must insert categorically different
  kinds of content. That is a floor, not an estimate — an affirmative surface does not imply a
  symmetric edit. **Criteria failing the screen are reported as τ_c NOT IDENTIFIED, never
  estimated anyway**, and the excluded share is stated beside every τ.
- **Mechanical locality.** The diff between R⁺ and R⁻ must be confined to a bounded span, checked on
  the text, not by a model. This is the only layer with no instrument in it.
- **Differential judge check.** `|s(c_j, R⁺) − s(c_j, R⁻)|` below a pre-set threshold for every
  j ≠ c, and *above* it for j = c. **Its own positive control:** a placebo pair edited on a criterion
  *not* in the rubric must show the difference ≈ 0 for all rubric criteria — if it does not, the
  check is reading the edit and the round reports UNVERIFIED rather than a τ.
- **Human adjudication on a sub-sample**, to bound how much of the exclusion is instrument rather
  than manipulation.

**Primary outcome.** `τ_c` = P(choose R⁺) − ½, per criterion.

**The manipulation check is the experiment.** Pairs failing verification are **excluded before any
outcome is examined** and their count reported. An unreported exclusion rate would turn a failed
manipulation into a clean-looking effect.

**Symmetry removes the first-order edit effect, not every order of it.** The differential check
cancels whatever editing does *in common* to both arms. What it cannot cancel is a systematic
difference in the lexical character of a satisfy-edit versus a violate-edit — if satisfying criterion
c reliably imports the criterion's own vocabulary and violating it does not, the difference
`s(c_j, R⁺) − s(c_j, R⁻)` still moves for j ≠ c sharing that vocabulary. So, committed now:

- **lexical distance from the base is recorded for both arms and reported with every τ**, and the
  two arms' distances are matched by construction rather than checked afterwards
- **the exclusion rate is reported against lexical distance**, so a reader can see whether surviving
  pairs are the low-change ones
- **τ_c is reported overall and stratified by lexical distance**; if the strata disagree, the
  headline is the stratified result
- **a human adjudication sub-sample** bounds how much exclusion is instrument rather than
  manipulation

**⚠ Expect small effects, and power for them (r59).** Leave-one-criterion-out on the judge's induced
ranking flips the top choice for only **14.7%** [12.6%, 17.1%] of 991 criteria — **below** the
**26.1%** produced by within-prompt permutation, because a rubric's criteria **agree with each
other**. That is judge-relative and is *not* a measurement of humans, so it is a **prior, not a
result**: if human choices are similarly concordant, a single-criterion manipulation moves them
rarely, and an underpowered τ_c would read as "criteria do not cause choices" when it means "this
design could not have seen it." The pilot must estimate the human flip rate **before** n is fixed.

**Committed in advance.** τ_c is expected to be **heterogeneous across prompts** and will not be
pooled into a single number. r43 found country-level sign reversals above a permutation null even
while group-specific weights did not beat pooled ones; a pooled τ would average over exactly that.

---

## Recruitment and protocol fidelity — the layer π, which none of this specified

Every number these experiments are compared against was produced by a **specific elicitation
protocol**, and π is one of the five layers the research object names. The design above specified
instruments and outcomes and said **nothing** about who is recruited or what they are put through
before they answer — so it could have been executed against a different population and a different
procedure and the comparison to r12 would have silently broken.

**Recruited to match, and the deviation reported either way.** CoVal used an online platform with an
English-reading requirement, aiming for a diverse global pool within that constraint, and ran an
intake survey covering age bucket, gender, race/ethnicity, employment, education, country of
residence, country of origin, generative-AI usage frequency and AI-concern level. Committed: **the
same intake instrument**, and the achieved demographics **reported against the release's own
distribution**, so a reader sees the deviation rather than being told there isn't one.

**⚠ The onboarding quiz is part of π, and it is a fork this design has to take deliberately.**
Participants could not reach the tasks until they passed a rubric-writing quiz teaching *objective
vs subjective*, *prompt-specific vs generic*, *both polarities*, and *weight calibration*. So every
released criterion was written by a **trained** participant, and "what people write as criteria" in
this dataset means "what people write **after that training**".

- The **POST** arm must take the quiz. It *is* the released procedure; without it the arm is not
  replicating anything.
- The **PRE** arm takes it too. S_pre asks whether direction pre-exists the **menu**, not whether it
  pre-exists the **training** — omitting it would confound the arms with a variable the released
  data never varied.
- **A quiz-free third arm is worth running and is labelled exploratory.** That the quiz is part of
  what the rubric measures is itself an untested claim about π, and this is the cheapest place it
  will ever be testable.

**Task position is a controlled variable, not a nuisance.** r31 measured that the same **933**
people drop **−179 characters [−196, −162], −53.3%** at task 6 — within-person, and exactly at the
platform's minimum-task boundary, so effort is confounded with a pay threshold. Committed: **position
randomised within participant**, recorded for every response, and its effect reported. A protocol
that let position ride along would reproduce the release's own artefact and call it a finding.

**The released task flow is replicated in order or the ranking is not the released ranking.** An
unacceptable-content check came *before* the rankings and primes attention toward safety; the
personal ranking came before the world one. Both are kept in that order for the arms that claim
comparability, and any departure is stated in the same sentence as the estimate it affects.

> **⚠ THE UNACCEPTABLE CHECK WAS NOT ASKED ON EVERY TASK, and this paragraph assumed it was**
> (measured 2026-07-29, entry 155). Counting `ranking_blocks["unacceptable"]` by each rater's task
> position across all **18,384** released assessments:
>
> | task position | assessments | with a `world` ranking | with an `unacceptable` block |
> |---:|---:|---:|---:|
> | 1 | 1,012 | 1,012 | **1,012** |
> | 2 | 1,012 | 1,012 | **1,012** |
> | 3 | 997 | 997 | 997 |
> | 4 | 995 | 995 | 993 |
> | 5 | 990 | 990 | **887** |
> | 6 and beyond | — | all present | **0** |
>
> Only **26.66%** of released assessments carry it, and always a rater's **earliest** tasks. So the
> safety priming applied to roughly the first five tasks per participant and to nothing after.
>
> **Consequence for this commitment, stated as a design decision rather than a detail:** replicating
> the check on *every* task would **over-apply** a priming the release applied to a quarter of its
> assessments. The arms claiming comparability must either (a) apply it to the first five tasks per
> participant and not after, or (b) apply it uniformly and state that the released rankings are a
> **mixture** of primed and unprimed conditions in a 27/73 split. Option (a) is chosen; (b) is
> recorded so the choice is visible rather than assumed.
>
> **⚠ THE SAME BOUNDARY GOVERNS THE `personal` RANKING** (entry 156): it is present on the *identical*
> 4,901 assessments and on none past task five. **And the partition is by PROMPT** (entry 158): 1,078
> prompts split into **321 long-form** and **757 short-form** with **intersection zero**, so no prompt
> was ever collected under both instruments and no cross-form comparison exists in this release. So the release has a **long form** (world + personal +
> unacceptable) for a rater's first ~5 tasks and a **short form** (world only) after. Experiment 2, if
> it wants personal rankings, inherits the same choice — collect them on early tasks only and match the
> release, or collect them throughout and accept that its rankings are not comparable to 73% of the
> released ones.
>
> **And the boundary is visible in the data, which is why it must be designed around rather than
> noted** (entry 157). Mean rationale length is **269.1** characters across the long form and **164.7**
> across the short — a **−104.5** step at the boundary. Within the long form the trend is
> **−3.81 chars/task [−17.21, +9.95]**, covering zero; within the short form **−1.44 [−3.05, −0.38]**,
> excluding it. So there is a small real decline *inside* the short form, and the step at the boundary
> is about **73 tasks' worth** of it in a single move. **Any experiment that changes form mid-session
> will produce a discontinuity of that size in its own data**, and must either hold the form fixed or
> report the step.

**Compensation is reported because it is part of the instrument.** The release paid $60 for the
survey plus 5 tasks (≈2 h), then $30/task with a $90 bonus for 15 within 7 days, to a maximum of
$540, at a median 22 minutes per task. Committed: **at or above that rate**, and stated — attention
is bought, the release's numbers were produced at that price, and a cheaper study is not measuring
the same thing.

---

## Rules binding all three

1. **The frozen manifest is the admissibility gate.** Rankings of responses that do not hash to
   `r45_frozen_frame.json` are not analysable as H_fresh.
2. **No optional stopping.** n fixed from a pilot, before the main collection.
   **⚠ And δ = 0.01 must be sized, not merely declared** ([r91](rounds/r91_precision_budget),
   2026-07-29). Three rounds preceding this document fixed δ = 0.01 and then could not reach it
   (r86 fell back to 0.026, r87 to 0.0231, r90 to a two-way crossed width). Under half ∝ 1/√n —
   **verified, not assumed**, by [r89](rounds/r89_floor_draw_at_panel_size) across three panel
   sizes at 11.5% worst deviation — on this release's own published half-widths:
   **a LEVEL reaches δ = 0.01 at ≈1.6× the current 968-prompt join; a DIFFERENCE needs ≈5.3×**,
   because a difference carries two intervals and so costs about 4× a level.
   **All three experiments below are differences**, so the 5.3× figure is the binding one, not
   the 1.6×. Two consequences for this protocol:
   - **Part of the cost is compute, not annotators.** The donor draw is **20%** of the attribution
     interval's variance and does *not* shrink with more prompts under a single draw
     ([r88](rounds/r88_donor_draw_variance)). Averaging **m = 10** draws cuts the requirement
     1458 → **1195** prompts; m = 100 buys only 27 more. **Donor-averaging at m ≥ 10 is therefore
     required of the analysis, and it is the cheapest precision available here.**
   - **This sizes PRECISION, not power.** It states when an interval reaches ±0.01, never what
     effect is detectable — that needs a prior on τ_c, which is one of the quantities being
     measured. So n fixed from the pilot governs; this bounds the pilot rather than replacing it.
   The same arithmetic is already applied to the world-vs-personal contrast below, which needs
   **14,358** reversed pairs against the **2,444** the release holds — the one place where it
   returns *out of reach* rather than a number to collect.
3. **Every outcome above is primary or it is exploratory**, and exploratory results are labelled
   as such in the same sentence as their number.
4. **Analysis code is written and committed against synthetic data before real data arrives**, so
   the pipeline cannot be tuned to the result.
5. **Three-valued verdicts.** CONFIRMED / OVERTURNED / **UNVERIFIED**. A check unfit for its
   question is never an acquittal.
6. **Positive controls before nulls.** Any instrument reporting "no effect" must first have
   returned a non-zero effect on something.
7. **δ = 0.01 is a stipulation, now ANCHORED to a decision this project can point at.** It is
   swept and the sweep is reported, because at δ = 0.0025 only 4 of 21 existing contrasts are
   equivalent. But a margin should encode *"an effect this small would not change what anyone
   does"*, and until now nothing said who or what.

   **The decision is which aggregation rule to use** — a live choice the release explicitly invites,
   calling CoVal-core *"an invitation for others to develop and validate better synthesis and
   aggregation methods"*. [r06](rounds/r06_rule_tournament) ran five of them:

   | | accuracy | vs no-compression |
   |---|---:|---:|
   | utility | 0.6575 | **+0.0067** |
   | constituency | 0.6567 | **+0.0070** |
   | majority | 0.6552 | +0.0044 |
   | conflict-aware | 0.6446 | −0.0058 |
   | consensus | 0.6387 | **−0.0113** |

   The five span **0.0188**, and consensus ties random selection (0.6384). So **δ = 0.01 is 53% of
   the entire distance between the best and worst aggregation rule anyone has proposed**, and larger
   in magnitude than three of the five rules' effects against no-compression.

   **That fixes the reading of every equivalence claim in this package.** "Equivalent to zero at
   δ = 0.01" now means *"smaller than half the swing you get from changing the aggregation rule"* —
   which is a decision somebody makes, with a number attached, rather than a threshold chosen
   because it is round.

---

## What this project will conclude if the experiments are never run

Stated now so that it cannot be softened later. The computational programme has established:

- the rebuilt satisfaction layer predicts held-out human rankings well above chance (r04)
- the own-rubric advantage is **semantic, not lexical** — 97.4% survives faithful paraphrase (**r20** measures the retention; **r14** supplies the fidelity filter and measures something else — that a *model* paraphrase flips 15.4% of the judge's Yes/No verdicts while a *mechanical* one flips 2.5%)
- post-ranking polarity is the largest predictive channel — **+0.0876 (47%) when added last to
  text alone (r32), but a Shapley value of +0.0214 (12%) averaged over all 16 coalitions (r36),
  whose verdict states r32's split "over-attributed to polarity"** — and it is **not
  primarily same-rater circularity** (r34/r36/r37)
- that advantage **does not transfer** to responses the criteria authors never saw — replicated on
  250 untouched prompts (r46) — and neither generic distance (r40) nor criterion-space support
  (r41) explains why
- the stronger reading, that an *unrelated* rubric **beats** the own rubric there, is **not
  established**: roughly half of it rides on the gold proxy's length channel, and on held-out
  prompts the fresh arm stops being negative once length is removed (r47)
- source specificity is **3.2%–65.8%** depending on floor donor and judge family — analyst
  choices the source package never reports
- the population nulls are **not equivalence**: enumerating every interval contrast in the package
  finds **125**, of which the equivalence round tested **21**, and **9 of r43's group cells are
  INCONCLUSIVE at δ = 0.01** — non-significant *and* not bounded inside the margin (r58). "No group
  is predicted better by its own weights" survives as *no detected effect*, not as *no effect*
- a rubric's criteria **agree with each other more than chance**, and not because the compiler
  selected them so: dropping one changes the judge's top choice for **14.7%** of criteria against
  **26.1%** under permutation, and criteria borrowed from *other prompts* flip at **14.9%** (r59)
- CoVal-core **internalises polarity into criterion semantics**, and a reconstruction attributes
  +0.0733 of it to the polarity rewrite (r44) — ⚠ a stage that applies the crowd's rating **sign
  numerically**, so it bounds from above what a text rewrite could achieve rather than measuring
  it. Compatibility selection **costs −0.0181** and
  beats a size-matched random choice by **+0.0149**, so choosing *which* items survive **recovers
  most of what truncating to four destroys and does not repay it** — membership is mitigation,
  not gain

And it cannot say what that polarity **is**, because no rater in the release rated a criterion
before seeing responses. **That is the finding.** The measurement program is well-specified,
internally valid on the elicitation manifold, and **unvalidated off it** — and the release's own
protocol is what makes the missing validation unreachable.
