# Preregistration — the three human experiments

Written **before** any human data exists, which is the only time a preregistration means
anything. Frozen frame: `rounds/r45_protocol_freeze/results/r45_frozen_frame.json`,
manifest `313044eafe5d18a9335408f7c35a0e76f2b08e4a436f765cede756e78b3dfa4b`, 60 prompts,
540 hashed responses, four equal cells of 15.

Everything in this repository is now blocked on one of the three counterfactuals below. They do
not exist in any public data and cannot be computed from it — 45 rounds have established that by
exhausting the alternatives, which is the only argument for spending money on people.

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

**And the unmatched rate is not an exclusion — it is the measurement.** A PRE criterion with no POST
counterpart is a criterion someone produced *without having seen the responses*; a POST criterion
with no PRE counterpart is one that **only arises after seeing them**. The second rate is
menu-induced construction, measured directly, and it is a **primary outcome** rather than a
housekeeping figure. An experiment that quietly dropped unmatchable criteria would discard its own
strongest signal.

**Predictions, committed before data.**

| world | prediction |
|---|---|
| direction pre-exists the menu | PRE/POST sign agreement high; PRE-derived weights predict POST rankings about as well as POST-derived ones |
| direction is menu-constructed | agreement near the marginal-matched baseline; PRE weights predict poorly |
| partially constructed | agreement above baseline but PRE weights strictly worse — the expected outcome, and the one requiring an effect *size*, not a test |

**A neutral option must be on the screen in both arms.** r35 established only that abstention
*after the fact* costs nothing; it could not simulate what a participant would do given
"no general direction", "depends on implementation", or "cannot judge without seeing a response"
**at elicitation time**. Their usage rates are a primary outcome, not a nuisance.

**Stopping rule.** Fixed n, decided from a pilot of 20 participants per arm. No optional stopping.

---

## Experiment 2 — H_fresh: do the criteria predict choices on responses nobody wrote them for?

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

**Committed: collect BOTH, with world as primary.** The personal ranking exists for **76.9%** of
released assessments and this project has never used it. Collecting both costs one extra screen and
yields a contrast the release can support and nobody has run — *does a values rubric predict the
normative ordering better than the preference ordering?* Personal is **secondary and labelled
exploratory**; world is the primary outcome, because that is the one r12 measured.

**Sampling.** The r38 frame: 60 prompts, four equal cells crossing rubric-vs-proxy disagreement
with surface distance, sampling weights 2.80 / 3.67 / 5.53 / 4.67, ≥8 raters per prompt. Weights
are reported with every estimate so one collection yields **both** a population estimate and an
anomaly-subset estimate. Power ≈0.98 for +0.05 clustered on prompt; r12's 0.16 is detectable in
every cell.

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

**Committed: a satisfaction sub-study, or the headline is scoped.** On a sub-sample of
(criterion, fresh response) pairs, humans answer the satisfaction question directly, giving a
human-vs-judge agreement rate **on fresh responses** — the quantity r04 supplies for originals and
nobody supplies here. If that sub-study is not run, the primary result is reported as
*"human rankings against a model-scored rubric"*, never as *"human-measured"*.

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

## Rules binding all three

1. **The frozen manifest is the admissibility gate.** Rankings of responses that do not hash to
   `r45_frozen_frame.json` are not analysable as H_fresh.
2. **No optional stopping.** n fixed from a pilot, before the main collection.
3. **Every outcome above is primary or it is exploratory**, and exploratory results are labelled
   as such in the same sentence as their number.
4. **Analysis code is written and committed against synthetic data before real data arrives**, so
   the pipeline cannot be tuned to the result.
5. **Three-valued verdicts.** CONFIRMED / OVERTURNED / **UNVERIFIED**. A check unfit for its
   question is never an acquittal.
6. **Positive controls before nulls.** Any instrument reporting "no effect" must first have
   returned a non-zero effect on something.
7. **δ = 0.01 is a stipulation.** It is swept, and the sweep is reported, because at δ = 0.0025
   only 4 of 21 existing contrasts are equivalent.

---

## What this project will conclude if the experiments are never run

Stated now so that it cannot be softened later. The computational programme has established:

- the rebuilt satisfaction layer predicts held-out human rankings well above chance (r04)
- the own-rubric advantage is **semantic, not lexical** — 97.4% survives faithful paraphrase (**r20** measures the retention; **r14** supplies the fidelity filter and measures something else — that a *model* paraphrase flips 15.4% of the judge's Yes/No verdicts while a *mechanical* one flips 2.5%)
- post-ranking polarity carries roughly half the above-chance concordance, and it is **not
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
  +0.0733 of it to the polarity rewrite (r44). Compatibility selection **costs −0.0181** and
  beats a size-matched random choice by **+0.0149**, so choosing *which* items survive **recovers
  most of what truncating to four destroys and does not repay it** — membership is mitigation,
  not gain

And it cannot say what that polarity **is**, because no rater in the release rated a criterion
before seeing responses. **That is the finding.** The measurement program is well-specified,
internally valid on the elicitation manifold, and **unvalidated off it** — and the release's own
protocol is what makes the missing validation unreachable.
