# R412 — the winning model is constant within a conversation, so the conversation is the unit and the replication is marginal

**The decision this makes safe:** *is the second-corpus replication powered?* **No — 2.47×, at
R411's pessimistic endpoint, and now for a measured reason rather than a worst-case assumption.**

## Result — `W_HIGH_ICC`. Four controls pass. **No GPU.**

| proxy | conversations | m̄ | ICC / κ | shuffled |
|---|---:|---:|---:|---:|
| `score` | 8,011 | 8.53 | **0.1978** | 0.0006 |
| **winning model** (pairwise κ) | 8,011 | 3.42 | **1.0000** | 0.0025 |

**`P(same winner \| same conversation) = 1.0000`** over **43,735** within-pairs.
**`P(same winner \| different conversations) = 0.0557`.**

| | ICC | DEFF | n_eff | ratio |
|---|---:|---:|---:|---:|
| `score` | 0.1978 | 2.490 | 10,756 | 2.89× |
| **winning model** | **1.0000** | **3.425** | **7,822** | **2.47×** |

## ⭐ What that 1.0000 means

**Within a conversation, the model the user chose never changes.** So an arm's success on interaction
2 is not independent of interaction 1 — **the target is literally the same model.** The conversation
is the independent unit, and the effective n is **7,822, not 26,789.**

⚠ **The mechanism is an inference, the measurement is not.** A corpus where each conversation
continues with the model the user picked would produce exactly this; that reading is **D5** and is not
needed — the 43,735 within-pairs are the evidence, whatever produced them.

## ⛔ Two errors of my own, caught here

**① R411's NEXT named a quantity that needs the judge** — the outcome's own ICC requires an arm run on
this corpus, and none has been. *"Measure it"* made an unavailable thing sound like a task. **Third
consecutive closing sentence of mine with an unexamined step.**

**② My first model proxy was a check that could not fail, in the null direction — and it returned
exactly `0.0000`, which was the tell.** I scored each interaction against **its own conversation's
modal winner**, a label defined *within* the group, which removes between-group variance **by
construction**. It could not have come out non-zero whatever the corpus did. **The proxy was replaced
— with a pairwise κ that has no within-group normalisation — not the criterion.**

## ⛔ And R411's "range" was already the whole range

`DEFF = 1 + (m̄−1)·ICC` with m̄ ≈ 3.4 gives **ICC = 0 → 4.57×** and **ICC = 1 → ~2.47×**. Those are
*exactly* R411's two endpoints. **So what R411 called "a range whose ends imply opposite decisions"
was ICC ∈ [0,1] with the interior blank** — a derivation I did not notice while writing it. This round
fills the interior, and the answer sits at the top of it.

## Controls

| | returned |
|---|---|
| **SYNTH (+)** | a corpus built at ICC = 0.80 recovers **0.800** (seeds 0.803/0.799/0.797) — `PASS` |
| **SYNTH (−)** | a corpus with no structure returns **0.000** — `PASS`. An estimator always returning 0.8 would pass (+) alone |
| **SHUFFLE** ⭐ | conversation labels destroyed **on the real data** → **0.0025** — `PASS`. The null on the actual object, not on my imagination |
| **m̄** | measured, not taken from R398's ratio, because DEFF is linear in it |

## ⚠ This owes R402 an annotation

R402's harness validated at **n = 26,789 interactions**. That count **overstates independence** if the
target is constant within a conversation. **The harness itself is unaffected** — its controls were
about whether it can see an effect — but any *power* claim resting on that n must use **7,822**.
R402's README is annotated.

## Register

| criterion | status |
|---|---|
| **the outcome's own ICC** | **N/A** — needs an arm run on this corpus. Named, not approximated |
| **a causal reading of ICC** | **N/A** — a variance decomposition, not a mechanism |
| **why the winner is constant** | **D5** — an inference about corpus construction, not measured here, and not needed |

## The sentence I can no longer write

> *"the replication has 26,789 independent units"* — **it has about 7,822**, and the factor of 3.4 is
> the difference between a powered experiment and a marginal one.

Artifact: `results/r412_clustering.json`, source-stamped.
