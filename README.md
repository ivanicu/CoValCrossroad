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

**The sign runs the wrong way for measurement failure.** The inversion *shrinks* as fresh
responses move away from the original support and is worst on the ones that look most like the
released candidates. If it were an artifact of judging out-of-distribution text it should have
run the other way.

The effect is small (|r| ≈ 0.13) and this is a single axis, so it does **not** establish
genuine transport failure — it removes the easiest alternative to it. Two consequences follow.
**Mahalanobis disagrees in sign across lineages, so it is a property of a representation, not
of the responses** — which is exactly why every distance is reported per lineage and never
averaged. And **the human sample must not be drawn from the far tail**, where the anomaly is
mildest.

⚠ Length is partialled out throughout, because fresh responses are systematically *longer*
(89 vs 76 median words) — the 180-token cap never bound, and the released candidates are the
short ones.

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
| **A2** held-out rater folds | a disjoint 5-fold | 0.6438 | +0.0027 [−0.0002, +0.0056] |
| **A3** held-out **country** | every *other* country | 0.6458 | +0.0007 [−0.0033, +0.0048] |
| A3 held-out AI-usage | other usage bands | 0.6437 | +0.0028 [−0.0009, +0.0066] |
| A3 held-out age | other age bands | 0.6425 | +0.0040 [−0.0001, +0.0080] |

**Every rung is non-significant.** Where the drop happens is the diagnosis, and there is no
drop: not individual circularity, not small-sample group fitting, not population dependence.
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
T         0.1277    0.1264     +0.0013 [-0.0002, +0.0029]   spans zero
S         0.0214    0.0205     +0.0008 [+0.0000, +0.0017]
M         0.0128    0.0126     +0.0002 [-0.0009, +0.0015]   spans zero
V         0.0002    0.0001     +0.0001 [-0.0001, +0.0004]   spans zero
```

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
| **forced** — every criterion gets a direction | 0.6419 | 100% |
| **confident** — abstain unless ≥90% agree | **0.6419** | **45.7%** |
| **posterior** — weight by `p₊ − p₋` | **0.6503** | 97.4% |

```
confident − forced   −0.0003 [−0.0074, +0.0063]   spans zero
posterior − forced   +0.0084 [+0.0043, +0.0124]   excludes zero
```

**Abstaining on 54% of the criteria costs nothing measurable.** And down-weighting contested
criteria instead of forcing them to ±1 *improves* concordance. So the signal lives where
raters agree, and the forced direction on the rest is not carrying it — **the forced-choice
concern does not bite.**

Read with r34, the polarity channel now looks like a genuine cross-rater direction: it
survives rater-disjoint cross-fitting (92%), it concentrates in criteria with agreement, and
it is robust to abstention. **Two of the three worlds are closed.** What remains is the one
no split of these annotators can reach — every one of them saw the four candidates before
rating — so *stable population value* versus *direction constructed by seeing the menu* still
needs weights from people who never saw a response.

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
| **cross-fit sign** | **raters disjoint from the target** | **0.6419** |
| same-sample sign | everyone, incl. the target rater | 0.6465 |
| leave-one-rater-out sign | everyone except the target rater | 0.6414 |
| random sign *(null)* | signs shuffled, ratio preserved | 0.5687 |
| donor-prompt sign *(null)* | another prompt's signs | 0.5533 |

```
D_population  crossfit − attribute   +0.0578 [+0.0490, +0.0671]
D_same        same     − attribute   +0.0631 [+0.0542, +0.0730]
D_leakage     same     − crossfit    +0.0053 [+0.0024, +0.0082]    ← 8% of the effect
```

**Roughly 92% of the polarity gain survives rater-disjoint cross-fitting.** Both nulls sit
*below* the direction-free arm — shuffled signs −0.018, donor-prompt signs −0.034 — so the
sign channel is not a free parameter; the specific directions carry the signal.

**So same-sample circularity is not the explanation.** The post-choice direction generalises
across people, and "leakage" is the wrong word for the bulk of it.

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

### What CoVal-core actually is

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

| judge | family | own | random floor | attribution | prompt-specific share |
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

| judge | family | vs nearest-topic floor | vs random floor |
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

**What that means for the headline.** "Less than half of a values evaluation measures values"
is not a finding about CoVal. The quantity is **unidentified without naming the floor donor,
the judge family, and the sampling uncertainty** — and no published version of this number,
including three of my own, named any of them.

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

| [r32](rounds/r32_channel_decomposition) | Text or post-choice weights? | post-ranking **polarity nearly doubles** above-chance concordance (9.0 → 17.8 pts, +0.0876 [+0.0784,+0.0976]). Whether that is stable cross-rater value direction, preference construction, or **same-sample leakage is unidentified** — cross-fitting queued |

| [r33](rounds/r33_core_launders_polarity) | What is CoVal-core? | **a transformation, not a subset.** Scored with *no ratings*, core reaches 0.6563 against full's 0.5899 — recovering ~76% of the post-choice polarity channel **in its sentences**. It ships with no weights, so nothing marks that |

| [r34](rounds/r34_global_rater_crossfit) | Is the polarity signal leakage? | **no.** Global rater-disjoint 5-fold cross-fitting keeps **92%** of it: D_population +0.0578 [+0.0490,+0.0671] against a same-sample premium of only **+0.0053**. Both nulls fall below the direction-free arm |

| [r35](rounds/r35_polarity_abstention) | Does it depend on forcing a direction? | **no.** Abstaining wherever raters split (dropping **54%** of criteria) moves cross-fitted accuracy by **−0.0003 [−0.0074,+0.0063]**, and down-weighting contested criteria *helps* (+0.0084). The scale's neutral point is used **once in 102,147 ratings** |

| [r36](rounds/r36_channel_shapley) | Channel split without order dependence | all 16 coalitions. **Magnitude without direction reaches 0.628 vs sign's 0.644** — near-substitutes, so r32's sequential split over-attributed to polarity. φ_S(same)−φ_S(cross) = **+0.0008**, tiny under every ordering. Visibility ≈ 0 |

| [r37](rounds/r37_leakage_topology) | How does the signal decay with isolation? | **it doesn't.** A0→A1→A2→A3 all non-significant; cross-**country** weights cost **+0.0007 [−0.0033,+0.0048]**. Not individual, not small-sample, not country/usage/age-conditional. `A4` response-blind is **undefined, not zero** |

| [r38](rounds/r38_human_sampling_power) | Which prompts to send to humans, and how many? | **frame-limited, not power-limited.** 60 prompts × 8 raters detects **+0.05 at 98%** power clustered on prompt; r12's 0.16 is detectable everywhere. Equal-cell stratified frame with sampling weights so one collection gives both a population and an anomaly estimate |

| [r39](rounds/r39_feature_cache) | Cache representations, analyse nothing | one GPU pass, three lineages (qwen/phi/internlm), 2,000 responses. Load failures recorded as **environment claims**, not model properties |
| [r40](rounds/r40_ood_map) | Is r12's inversion an OOD artifact? | **no — the sign runs the wrong way.** Nearest-neighbour distance correlates at **−0.125**, 2/3 lineages, same sign 3/3: the anomaly is **worst where fresh responses most resemble the released ones** |

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
