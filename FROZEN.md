# Frozen lines

A line is frozen when further computation on it cannot identify what it is measuring. Freezing
is not a verdict that the line was wrong — several of these produced correct numbers. It is a
verdict that **the next round on this line would not change any decision**, because the
ambiguity is in the object rather than in the estimate.

Each entry records what the line was trying to identify, how it failed, and **what would
unfreeze it** — because a freeze without an unfreeze condition is just abandonment with better
manners.

---

## 1. The rater-structure ontology — `r23`, `r25`, `r26`, `r27`, `r28`

**What it was trying to identify.** Whether r01's cross-prompt persistence (ρ=0.147) means
value blocs (M2) or raters differing in reliability (M1b) — the premise the whole r16–r18 arm
was built on.

**Four consecutive failures to identify the ontology, each with a *different* cause:**

| round | the separator | why it could not separate |
|---|---|---|
| r23 | pair-specific residual vs dyad-permutation null | its sharper test — reliably-disagreeing pairs — read `z=+10.26` at 2 null reps and `+1.40` at 40 |
| r26 | sign of the centred residual | mean agreement is +0.25, so a zero-competence pair scores "reliably disagreeing" **without ever disagreeing**. The statistic gave the two worlds the same number |
| r27 | raw-scale negative tail + agreeable-pair control | under **unequal bloc sizes a majority member *is* agreeable by construction**, so the control selects same-bloc pairs and could not have found blocs if they existed |
| r28 | multiplicative vs additive functional form | "one fewer parameter" was false (design rank-deficient by exactly 1); the reported `z` moved with `PYTHONHASHSEED`; and held-out R² spans **[−1.64, +0.51]** against additive's tight [+0.34, +0.42] |

**What survives.** The algebra of entry 31: fitting `μ + aᵢ + aⱼ` to a multiplicative surface
leaves residual `(ρᵢ−m)(ρⱼ−m)`, a U-shape with no blocs in the generating process. So the
additive decomposition those rounds relied on **is** misspecifiable. The multiplicative
alternative is **not** thereby established.

**Status: UNRESOLVED, frozen.** Not "no pair structure" and not "blocs exist."

**What would unfreeze it.** Not another metric, null or estimator on the same data — four have
now failed for four different reasons. It needs either **anchor items** (criteria with
objectively checkable satisfaction, repeated equivalent items, known polarity) so that rater
reliability becomes separately measurable, or a held-out predictive comparison between explicit
generative models — one target with heterogeneous reliability, continuous latent axes, latent
classes — scored on **entirely unseen prompts per rater**.

---

## 2. The task-position regime reading — `r02`, `r24`, `r31`

**What survives (established).** The discontinuity is real and **within-person**: on the 933
people present at both positions, −179.2 chars [−196.2, −162.3], −53.3%, against 6.1%
attrition. Composition is excluded.

**Why the interpretation is frozen.** `DATASET_CARD.md:81` sets a five-task minimum and
sessions of 5 or 15 prompts. The release carries **no session identifier and no timestamp** —
verified field by field. So for anyone whose first batch held five prompts, position 6 is the
first task of a **later session**, and within-session fatigue is not separable from
between-session habituation.

**Status: real phenomenon, mechanism UNIDENTIFIABLE from this release.** Do not call it fatigue.

**What would unfreeze it.** Session identifiers or timestamps, which would have to come from
OpenAI.

---

## 3. The bloc / minority / constituency reading — `r16`, `r17`, `r18`

**Why frozen.** The partition is a median split on a principal component carrying **0.541%** of
the singular mass, and it is not any nameable constituency: gender (1.145) and country (1.198)
regret both fail r16's *own* 1.15× bar of 1.267. And 148 of 1,160 criterion raters (12.8%) have
no demographics at all, so both the bloc claim and its refutation are scoped to 87.2% of the
pool.

**Status: "latent profile partition", never "bloc", "minority" or "constituency".**

**What would unfreeze it.** A model with stable rater-specific value dimensions that predicts
held-out choices **on new prompts for the same person** better than reliability-plus-prompt
effects — which is the same requirement as line 1.

---

## 4. Extensions that add cost without adding an argument

Frozen because more of the same produces agreement, not ground truth.

- **more metric cells** on r25 — the sweep already confirmed its pre-registered gauge prediction on both branches; additional cells refine a residual whose interpretation is frozen under line 1
- **more judges** — three unrelated lineages already answer "is this a single-lineage artifact". A fourth cannot produce human ground truth, and judge agreement is not criterion validity
- **more gold backbones** — two disagree at r=+0.4775 already; a third adjudicates nothing
- **more donor floors** — r19/r30 established the floor is a *choice* spanning 2.47×. More points map the same choice
- **more paraphrase sweeps** — r14/r20 settled that the advantage is semantic rather than lexical at 97.4%
- **more best-of-n** — this failed once already: r09's rise vanished under r11's independent backbone. Without fresh human rankings and a human-calibrated judge, optimising a proxy and adjudicating with another proxy touches no target variable

---

## 4b. The anthropomorphism lexicon — `r07`

**Frozen by the queue and, until now, recorded nowhere here.** Found by comparing the queue's
frozen list against this file: 11 of 12 items were present, this one was not.

**Why it is frozen: the same instrument failed twice, in the same way, after being fixed.**

- **[Entry 2]** the first lexicon reported *"2.96% of crowd-written criteria address
  anthropomorphism"*. It was substring matching: `persona` caught *personal*, *personality*,
  *personalities*; `friend` caught *friendly*, *friendships*. **321 of 452 hits were false.**
  Word-boundary regexes gave **0.16%** — twelve times smaller. The finding got *stronger* through
  a bug.
- **[Entry 20]** the fixed lexicon's 0.16% failed too, on construct review of all 24 hits. Seven
  or eight of the nine `personal opinion` matches **instruct the model to avoid** opinions; one
  `as an ai` hit is literally an anti-anthropomorphism disclosure rule; four `persona` hits are
  content roleplay on request. At most 11 of 24 are on-construct — true rate **~0.05–0.09%**.

**Status: a keyword lexicon cannot measure this construct.** Both failures were the same shape —
the match rule is not the concept — and fixing the match rule did not fix that. The second failure
came *after* the repair, which is the reason to stop rather than to iterate again.

**What would unfreeze it.** Not a better regex. A construct-validated instrument: annotator
adjudication of a labelled sample with an inter-rater figure, against which any automatic matcher
is scored before its rate is quoted.

## 5. The computational headline

**Frozen as of 2026-07-28.** Source specificity is **3.2%–65.8%** including sampling error,
across (judge family × floor donor), with the far-donor corner unobserved for phi and internlm
absent. No further computation moves this: the width is caused by analyst choices the source
package never reports, not by estimation noise.

**What would unfreeze it.** Human rankings on a response distribution — at which point the
quantity stops being a subtraction between two model-scored arms and becomes a transport curve.

---

## The three counterfactuals that unfreeze the project

Everything above is frozen against the same wall. These do not exist in any public data and
cannot be computed from it:

```
S_pre     response-blind criterion direction    — nobody in this release rated before seeing responses
H_fresh   human rankings on the exact saved fresh responses
tau_c     the causal effect of intervening on one criterion
```

C38 has the frame ready: 60 prompts, four cells, populations 42/55/83/70, weights
2.80/3.67/5.53/4.67, and power 0.98 at +0.05 with 8 raters per prompt.
