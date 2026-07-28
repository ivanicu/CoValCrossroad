# CoVal Crossroads

**Does a public-input values rubric actually measure values?**

An independent, reproducible audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to contentious prompts *and wrote down the criteria they judged by*.

The release ships prompts, four candidate responses, crowd-written value rubrics and 18,384 human rankings. It does **not** ship the criterion-by-response satisfaction labels, so its published scoring cannot be reproduced. This repository rebuilds that layer locally, measures its concordance with the released rankings, and then asks what the rubric is actually made of.

> **⚠ Scope correction, 2026-07-28.** Earlier versions called the 80,542 pairs "held-out human
> preference". They are **pairwise decompositions of the same rankings**, on the same prompts and the
> same four candidates the criteria were written about, by participants who had already ranked them.
> Holding out individual *pairs* does not break that dependence. OpenAI ran a **separate** validation
> study with new raters and new completions precisely because the original rankings are unsuitable for
> out-of-sample rubric validity. So r04 establishes **internal reconstructive concordance on the
> elicitation manifold** — which is real and useful — and not out-of-sample human preference validity.

---

## Headline

Grading responses against **an unrelated prompt's rubric** already recovers most of the apparent signal.

| grading the same responses with… | concordance with the original human rankings |
|---|---:|
| the real, prompt-specific rubric | **0.686** |
| an unrelated prompt's rubric | 0.607 |
| response length alone | 0.532 |
| chance | 0.500 |

Of the 18.6 points above chance, **7.9 are prompt-specific criterion content and 10.7 are generic response quality any rubric earns for free** — using a randomly chosen prompt as the floor.

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

Applying that range to the headline's own 42.5% prompt-specific share gives **27%–67%**.

Neither endpoint is clean — the far donor is adversarially selected and may simply be refused by the
judge, the near donor shares topic. **The generic-quality floor is bracketed, not measured, so any
single figure must name its floor.**

### …and the judge moves it as much as the floor does

[r22](rounds/r22_cross_family) grades the same 300 prompts with judges from **two model families**.
The decomposition survives — every judge shows a positive attribution with an interval clear of zero,
so it is **not an artifact of the Qwen lineage**. But the magnitude is not portable:

| judge | family | own | random floor | attribution | prompt-specific share |
|---|---|---|---:|---:|---:|
| qwen3.5-2b-base | qwen | 0.6522 | 0.5759 | +0.0763 [+0.0585, +0.0944] | 50.1% |
| qwen2.5-3b-instruct | qwen | 0.6660 | 0.5767 | +0.0894 [+0.0672, +0.1114] | 53.8% |
| phi-3.5-mini-instruct | **phi** | 0.6410 | **0.6053** | +0.0357 [+0.0186, +0.0541] | **25.3%** |

phi clears its own positive control at 0.641, level with the Qwen judges — but its *unrelated-rubric
floor* is 0.605 against their 0.576. It extracts more generic response quality for free, leaving less
room for prompt-specific content.

**So the share has two independent sources of variation, and they multiply:**

```
floor choice, fixed judge     2.47×      (r19)
judge family, fixed floor     2.13×      (r22)
observed range, both varying  13.6% (phi, near floor) … ~74% (qwen, far floor)   ≈ 5.4×
```

**This is the headline's real scope.** "Less than half of a values evaluation measures values" is not
a property of the dataset. It is a property of *(dataset, floor donor, judge family)*, and the last
two — both of them analyst choices, neither reported in the source package — move the answer more
than fivefold. A single figure here does not constrain anything unless it names both.

⚠ `internlm2-chat-1.8b` could not be loaded at all (tokenizer parse error) and is reported as a
**load failure, not a judge verdict**. A third family remains untested.

### …and the prompt-specific part does not transfer

The criteria were written by participants **after reading the four candidates**. Measured on
rubric-blind responses those authors never saw, the advantage does not merely shrink — it inverts:

| response set | real rubric | unrelated rubric | advantage |
|---|---:|---:|---:|
| the four released candidates | 0.657 | 0.555 | **+0.102** [+0.071, +0.133] |
| fresh, rubric-blind, unseen | 0.478 | 0.520 | **−0.042** [−0.068, −0.015] |

A discrimination control confirms the fresh set is *more* separable than the released one, so this
is not an artifact of homogeneous generations. Re-run on an entirely new temperature-0.9 sample the
inversion replicates at **−0.058 [−0.085, −0.031]**.

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
facts about those four candidates, criteria written *before anyone saw them* should carry no advantage.
They carry a clear one — the *seed* criteria, prepared alongside candidate generation and never tailored
to the responses, are as informative as criteria authored after reading them:

| criterion provenance | real | unrelated | advantage |
|---|---:|---:|---:|
| seed (response-blind) | 0.583 | 0.537 | **+0.046** [+0.023, +0.069] |
| write-in (after reading) | 0.559 | 0.533 | **+0.026** [+0.002, +0.051] |
| **difference, paired on 293 shared prompts** | | | **+0.023 [−0.008, +0.054]** |

**Both arms are corrected and the third row is the honest one.** An earlier version reported +0.039 vs
+0.029 and read the write-in interval as spanning zero, making seeds look *better*. Two errors: the
attribution differenced a positional prefix of one array against a differently-ordered subset
([entry 15](RETRACTIONS.md)), and the *difference* was quoted with no interval at all. Repaired, every
point estimate rose — and the ordering died, because +0.023 spans zero. Which of the two provenances
carries *more* is **not established**.

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

| round | question | headline |
|---|---|---|
| [r01](rounds/r01_rater_structure) | Is disagreement noise or structure? | persists across disjoint prompts, ρ=0.147, z=+16.6. Most of it is an additive per-rater effect (r23). Whether anything **pair**-specific survives is **UNRESOLVED** — r28 showed the decomposition's functional form is itself unvalidated. The "survives removing response style" control was invariant by construction |
| [r02](rounds/r02_label_and_regime) | Label bias; fatigue or regime change? | label B wins 22.5% vs 25% expected. The task-6 effort drop is **real and within-person** (r31) but its **mechanism is unidentified** — position 6 is the study's minimum-task boundary |
| [r03](rounds/r03_stated_vs_revealed) | Do stated ideals predict own choices? | no lexical signal: +0.0017 [−0.006, +0.010] over a permuted-identity null |
| [r04](rounds/r04_rebuild_satisfaction) | Rebuild the withheld layer | 119,868 judgements, validated on 80,542 held-out human pairs at 0.686 |
| [r05](rounds/r05_value_taxonomy) | What does compression silence? | not a value family — the penalty for being contested is −0.31…−0.46 in *every* family |
| [r06](rounds/r06_rule_tournament) | Which aggregation rule wins? | four rules span 1.9 points; a consensus rule ties random selection |
| [r07](rounds/r07_anthropomorphism) | Does the rubric see anthropomorphic style? | a **residual association**, not established blindness: a response-level marker retains t=+4.02 after controlling for rubric score and length, but the effect is carried by `user_directed_warmth`, which is **warmth, not anthropomorphism**. **0.046%** of criteria address the construct (7 of 15,248, hand-adjudicated), split 4 anti / 3 pro. Measures immediate preference, **not impacts** — trust, reliance, disclosure and attachment are untested |
| [r08](rounds/r08_gold_preference) | A gold model that never sees the rubric | held-out 0.661 vs 0.529 length baseline |
| [r09](rounds/r09_overoptimization) | Optimize the rubric, watch preference | pre-registered gaming prediction **refuted**: markers fell |
| [r10](rounds/r10_attribution_robustness) | Is the attribution an artifact? | stable across judge size and template; 23.7% of the gap is topic, not value |
| [r11](rounds/r11_backbone_control) | Was r09 backbone leakage? | **retracts r09's rise** — it vanishes with an independent backbone |
| [r12](rounds/r12_response_set) | Does the advantage transfer? | it **inverts** off-distribution: +0.102 → −0.042, discrimination control passed |
| [r13](rounds/r13_seed_vs_writein) | Seed criteria vs write-ins | **refutes r12's own mechanism**: response-blind seeds carry real attribution (+0.046 [+0.023,+0.069]). The seed-vs-write-in *ordering* is NOT established — paired difference +0.023 [−0.008,+0.054] |
| [r16](rounds/r16_minority_regret) | Conflict-aware, on its own turf | profile splits show regret 2.07 vs 1.10 random, yet conflict-aware leaves the worst-off group **lowest of all rules**. ⚠ These are **not** a demographic constituency: gender (1.145) and country (1.198) splits both fail r16's own bar |
| [r17](rounds/r17_conditional_core) | Does conditional encoding rescue it? | **partly** — routing learned from a rater's *other* prompts helps only the rules carrying contested items (+0.195), and does not close the gap |
| [r18](rounds/r18_routing_difficulty) | Was r17's 84.6% routing accuracy free? | **inflated by +0.147, but real**: 0.666 [0.643, 0.688] where the blocs actually disagree |
| [r19](rounds/r19_floor_choice) | Which donor is the generic floor? | the headline moves **2.47×** with that choice; prompt-specific share is 27–67%, not a single figure. ⚠ rests on **2 usable judge cells** with no prompt-level CI |
| [r14](rounds/r14_paraphrase_gauge) | Is the judge paraphrase-invariant? | **no** — a semantically faithful rewording flips **15.4%** of Yes/No verdicts, so part of "criterion content" is criterion wording |
| [r15](rounds/r15_indistribution_transfer) | Do criteria transfer to a near-topic prompt? | **no** — own criteria +0.073 [+0.056, +0.091] over the floor, nearest-topic criteria +0.018 [−0.001, +0.037]. Real responses, real human rankings, no gold model. r21 shows that neighbour is 91.6% of the way to being the same question |
| [r20](rounds/r20_paraphrase_transfer) | Is the advantage content or wording? | **content** — reword every criterion and **97.4%** of the advantage survives; original−paraphrased +0.002 [−0.007, +0.011] |
| [r21](rounds/r21_donor_distance) | Is the "near-topic" donor actually near? | **yes, near the ceiling** — it sits at the 97.86th percentile of all pairs and covers **91.6%** of the distance from a random prompt to the same question reworded |

| [r22](rounds/r22_cross_family) | Does the attribution survive a change of judge family? | **yes, and the magnitude does not** — positive on qwen and phi with intervals clear of zero, but the prompt-specific share runs 25.3% (phi) to 53.8% (qwen2.5-3b) at a fixed floor, a **2.13× judge span** on top of r19's 2.47× floor span. The first run falsely claimed this on two Qwen judges because "family" was `name.split("-")[0]`; phi was scoreable only after a tokenizer fix |
| [r23](rounds/r23_actor_vs_dyad) | Is r01's persistence about people or about pairs? | **mostly people**: an additive actor model takes 47.2% of dyad variance and actor-only persistence (0.254) *exceeds* the headline. Pair-specific residual 0.034, z=+4.67 — real, and a fifth of what r01 reported. Its sharper test (reliably-disagreeing pairs) is **null at z=+1.40** |
| [r24](rounds/r24_regime_receipt) | Receipt for "step R²=0.964 vs trend 0.448" | the number existed in no script. Reproduced, **and given the control it never had**: a null that re-searches the breakpoint on every shuffle reaches only 0.172. Observed 0.964, p=0.0001, breakpoint found at position 6 by search |
| [r25](rounds/r25_actor_dyad_sweep) | Is r23's residual stable, or a property of Pearson? | 144-cell sweep: 4 agreement metrics × 3 overlap thresholds × 3 shared-item thresholds × style × centring — *running* |

| [r26](rounds/r26_sign_no_split) | Are there pairs that reliably *disagree*? | the split-half estimator returned **z = 1.40, 2.26, 2.68 and 10.26 on identical data**, varying only with how many coin flips were averaged. Rebuilt without any split |
| [r27](rounds/r27_raw_negative_tail) | Anti-correlation on the *raw* scale | the negative tail is real and grows with depth (1.20×→1.43×), and 3.02% of pairs are negative on **every** shared prompt vs a 1.93% null. Its actor control was confounded — under unequal blocs a majority member is "agreeable" by construction |
| [r28](rounds/r28_multiplicative) | Was the functional form wrong? | **the additive one is misspecifiable — and the alternative is not established.** Fitting a sum to a product leaves a U-shape with no blocs in it, which is what r27 measured. But "one fewer parameter" was **false** (the additive design is rank-deficient by exactly one; effective dof are *equal*), and out of sample the multiplicative fit spans R² **[−1.64, +0.51]** against additive's tight **[+0.34, +0.42]**. **Verdict: FUNCTIONAL FORM UNRESOLVED**, and the surviving `both_low` residual is not a measurement of anything |

| [r30](rounds/r30_scope_grid) | The headline, with an interval in every cell | replaces three successive point-estimate ranges (43%, 27–67%, 13.6–74%) with a (judge × floor) grid, each cell a ratio-of-means bootstrap over prompts |
| [r31](rounds/r31_within_person) | Is the task-6 drop composition or behaviour? | **within-person and real** — the same 933 people drop **−179 chars [−196, −162], −53.3%**, against only **6.1% attrition**. But position 6 is the study's minimum-task boundary and, with no session id in the release, is **perfectly confounded with "first task of a later session"** |

---

## What is unusual here

**[RETRACTIONS.md](RETRACTIONS.md) lists every claim this repository made and then killed.**
Twelve entries; nine are a later round destroying an earlier round's conclusion, and in seven of
those both rounds are mine. Read by round number this looks like a sequence of findings. It is not.

Every round carries its own null, and several of the killed claims are the author's own:

- a permutation null, a response-style control and a prompt-difficulty control (r01)
- a step-versus-trend model comparison rather than a fitted slope (r02)
- a permuted-identity null, not a chance baseline (r03)
- a shuffled-rubric arm and a length-only arm before any headline (r04)
- a no-compression control and a random-selection floor (r06)
- a pre-registered prediction that failed, reported as failed (r09)
- an independent-backbone control that retracted the author's own result (r11)
- an out-of-distribution transfer test that scoped the repository's own headline (r12)

**[assurance/ADVERSARY_BRIEF.md](assurance/ADVERSARY_BRIEF.md)** is what an independent challenger
should be handed, including a pre-registered list of what I expect them to overturn — so their
actual findings can be scored against my sense of my own work.

`assurance/` freezes thirteen claims against stated thresholds. **Four fail** — including the one that
scopes this repository's own headline. An assurance package with no failures is not an assurance package.

It also distinguishes `BROKEN_HARNESS` from `UNSUPPORTED`: when the repository was reorganised, every
claim source moved and the manifest silently resolved them all to "unmeasured". A package that cannot
tell "we never measured this" from "I can no longer find my own evidence" is not an assurance package
either.

---

## Reproducing

Verified from a clean clone: `git clone`, `python data/fetch.py`, then every CPU round and the
manifest run without further setup.

```bash
python -m venv .venv && .venv/bin/pip install numpy pandas scipy scikit-learn torch transformers
python data/fetch.py                            # downloads + verifies the release by SHA-256
python rounds/r01_rater_structure/run.py        # CPU only
python rounds/r04_rebuild_satisfaction/run.py   # needs a GPU
python assurance/manifest.py                    # regenerate the claim table
```

Judge and gold models are read from `COVALX_MODEL_2B` / `COVALX_MODEL_08B`, defaulting to the Hugging Face ids.

**Measured cost of the full pipeline: 0.36 GPU-hours on one consumer GPU, zero API spend.** No paid inference is used anywhere.

---

## Boundaries

- The judge is a 2B base model. It reaches 0.686 pairwise against the ~0.60 the release authors report, but only 0.61 on picking a single best response against their ~0.75. Both numbers belong in any citation of this work.
- The gold preference model is learned from the same 18,384 rankings. It is not fresh human data and inherits the label bias and two-regime split found in r02.
- No new human data was collected. Nothing here establishes what any population would say.
- `consensus` in r06 is this repository's operationalisation, not OpenAI's LM-assisted synthesis. The released CoVal-core rubric scores **0.660** ([r04](rounds/r04_rebuild_satisfaction), `a04_core.json`) — but that is **not comparable to r06's 0.6575 arm**: r04-core is the released 3,899-criterion rubric on 968 prompts, r06's arms are k=4 compressions of `coval_full` on 945. Different rubric source, different panel, different compression. An earlier version of this line called them "level"; nothing in this repository has measured them against each other.

## Attribution

CoVal is © OpenAI, released under CC BY 4.0. This repository redistributes none of it; `data/fetch.py` downloads it and verifies the exact bytes the results were computed from.
