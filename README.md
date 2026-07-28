# CoVal Crossroads

**Does a public-input values rubric actually measure values?**

An independent, reproducible audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to contentious prompts *and wrote down the criteria they judged by*.

The release ships prompts, four candidate responses, crowd-written value rubrics and 18,384 human rankings. It does **not** ship the criterion-by-response satisfaction labels, so its published scoring cannot be reproduced. This repository rebuilds that layer locally, validates it against held-out human preference, and then asks what the rubric is actually made of.

---

## Headline

Grading responses against **an unrelated prompt's rubric** already recovers most of the apparent signal.

| grading the same responses with… | agreement with held-out human rankings |
|---|---:|
| the real, prompt-specific rubric | **0.686** |
| an unrelated prompt's rubric | 0.607 |
| response length alone | 0.532 |
| chance | 0.500 |

Of the 18.6 points above chance, **7.9 are prompt-specific criterion content and 10.7 are generic response quality any rubric earns for free** — using a randomly chosen prompt as the floor.

**That floor is a choice, and the number moves 2.2× with it.** [r19](rounds/r19_floor_choice)
reads r10's donors as a decay curve: a random prompt's rubric still retains 47–60% of the signal,
because a random prompt sometimes shares topic. Grading against a nearest-topic donor instead gives
attribution 0.047; against the most dissimilar donor, 0.102.

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

Stable across three judge/template configurations (0.064 ± 0.017) *at a fixed floor*.

### …and the prompt-specific part does not transfer

The criteria were written by participants **after reading the four candidates**. Measured on
rubric-blind responses those authors never saw, the advantage does not merely shrink — it inverts:

| response set | real rubric | unrelated rubric | advantage |
|---|---:|---:|---:|
| the four released candidates | 0.657 | 0.555 | **+0.102** [+0.071, +0.133] |
| fresh, rubric-blind, unseen | 0.478 | 0.520 | **−0.042** [−0.068, −0.015] |

A discrimination control confirms the fresh set is *more* separable than the released one, so this
is not an artifact of homogeneous generations. **What the released numbers measure is bounded to the
response set the eval was validated against.**

[r13](rounds/r13_seed_vs_writein) then refuted the obvious explanation. If the criteria simply encoded
facts about those four candidates, criteria written *after* reading them should carry the advantage.
They do not — the *seed* criteria, prepared alongside candidate generation and never tailored to them,
carry more:

| criterion provenance | real | unrelated | advantage |
|---|---:|---:|---:|
| seed (response-blind) | 0.584 | 0.537 | **+0.039** [+0.009, +0.069] |
| write-in (after reading) | 0.575 | 0.530 | +0.029 [−0.002, +0.060] |

So the bound is not about what the criteria encode. It is a property of the measurement apparatus off
distribution — a transfer boundary for rubric-graded evaluation, which is the open question this
repository now points at.

---

## Rounds

Each round is self-contained: its own question, runner, results and README.

| round | question | headline |
|---|---|---|
| [r01](rounds/r01_rater_structure) | Is disagreement noise or structure? | persists across disjoint prompts, ρ=0.147, survives removing response style, z=+16.6 |
| [r02](rounds/r02_label_and_regime) | Label bias; fatigue or regime change? | label B wins 22.5% vs 25% expected; effort steps −38.6% at task 6 (step R²=0.964 vs trend 0.448) |
| [r03](rounds/r03_stated_vs_revealed) | Do stated ideals predict own choices? | no lexical signal: +0.0017 [−0.006, +0.010] over a permuted-identity null |
| [r04](rounds/r04_rebuild_satisfaction) | Rebuild the withheld layer | 119,868 judgements, validated on 80,542 held-out human pairs at 0.686 |
| [r05](rounds/r05_value_taxonomy) | What does compression silence? | not a value family — the penalty for being contested is −0.31…−0.46 in *every* family |
| [r06](rounds/r06_rule_tournament) | Which aggregation rule wins? | four rules span 1.9 points; a consensus rule ties random selection |
| [r07](rounds/r07_anthropomorphism) | Is the rubric blind to anthropomorphism? | style predicts preference independently of the rubric (t=+4.02); 0.16% of criteria mention it |
| [r08](rounds/r08_gold_preference) | A gold model that never sees the rubric | held-out 0.661 vs 0.529 length baseline |
| [r09](rounds/r09_overoptimization) | Optimize the rubric, watch preference | pre-registered gaming prediction **refuted**: markers fell |
| [r10](rounds/r10_attribution_robustness) | Is the attribution an artifact? | stable across judge size and template; 23.7% of the gap is topic, not value |
| [r11](rounds/r11_backbone_control) | Was r09 backbone leakage? | **retracts r09's rise** — it vanishes with an independent backbone |
| [r12](rounds/r12_response_set) | Does the advantage transfer? | it **inverts** off-distribution: +0.102 → −0.042, discrimination control passed |
| [r13](rounds/r13_seed_vs_writein) | Seed criteria vs write-ins | **refutes r12's own mechanism**: response-blind seeds carry more attribution (+0.039) than write-ins (+0.029) |
| [r16](rounds/r16_minority_regret) | Conflict-aware, on its own turf | blocs are real (regret 2.07 vs 1.10 random), yet conflict-aware leaves the worst-off bloc **lowest of all rules** |
| [r17](rounds/r17_conditional_core) | Does conditional encoding rescue it? | **partly** — routing learned from a rater's *other* prompts helps only the rules carrying contested items (+0.195), and does not close the gap |
| [r18](rounds/r18_routing_difficulty) | Was r17's 84.6% routing accuracy free? | **inflated by +0.147, but real**: 0.666 [0.643, 0.688] where the blocs actually disagree |
| [r19](rounds/r19_floor_choice) | Which donor is the generic floor? | the headline moves **2.5×** with that choice; prompt-specific share is 27–67%, not a single figure |
| [r14](rounds/r14_paraphrase_gauge) | Is the judge paraphrase-invariant? | **no** — a semantically faithful rewording flips **15.4%** of Yes/No verdicts, so part of "criterion content" is criterion wording |
| [r15](rounds/r15_indistribution_transfer) | Do criteria transfer to a near-topic prompt? | **no** — own criteria +0.073 [+0.056, +0.091] over the floor, nearest-topic criteria +0.018 [−0.001, +0.037]. Real responses, real human rankings, no gold model |

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
- `consensus` in r06 is this repository's operationalisation, not OpenAI's LM-assisted synthesis. The official core scores 0.660, level with the best simple rule.

## Attribution

CoVal is © OpenAI, released under CC BY 4.0. This repository redistributes none of it; `data/fetch.py` downloads it and verifies the exact bytes the results were computed from.
