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

**So what needs humans is now sharper.** That the advantage *fails to transfer* replicates on two
samples. That an unrelated rubric *beats* the own rubric there is **withdrawn**. H_fresh decides
whether the failure to transfer is a fact about rubrics or about model-scored proxies — which is
why length is a recorded variable below, not a covariate chosen afterwards.

**Design.** Participants rank the **four frozen fresh responses** for a prompt. Exactly the
responses in the manifest — this is why they are hashed.

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

**Design.** For a prompt with rubric criteria c₁…c_K, generate **minimal pairs**: a response
edited to change satisfaction of exactly one criterion, verified by (a) a judge panel of ≥2
unrelated lineages agreeing the target criterion changed, and (b) agreeing the others did not.
Participants choose between the pair.

**Primary outcome.** `τ_c` = change in choice probability per unit change in criterion `c`'s
satisfaction, per criterion.

**The manipulation check is the experiment.** If the edit moves other criteria too, τ_c is not
identified, and pairs failing the check are **excluded before any outcome is examined** and their
count reported. An unreported exclusion rate would turn a failed manipulation into a clean-looking
effect.

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
- CoVal-core **internalises polarity into criterion semantics**, and a reconstruction attributes
  +0.0733 of it to the polarity rewrite (r44). Compatibility selection **costs −0.0181** and
  beats a size-matched random choice by **+0.0149**, so choosing *which* items survive **recovers
  most of what truncating to four destroys and does not repay it** — membership is mitigation,
  not gain

And it cannot say what that polarity **is**, because no rater in the release rated a criterion
before seeing responses. **That is the finding.** The measurement program is well-specified,
internally valid on the elicitation manifold, and **unvalidated off it** — and the release's own
protocol is what makes the missing validation unreachable.
