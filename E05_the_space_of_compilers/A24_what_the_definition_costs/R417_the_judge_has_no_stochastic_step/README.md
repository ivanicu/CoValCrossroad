# R417 — the judge has no stochastic step, so the 0.116 was never scoring noise and the GPU re-score is not needed

**The decision this makes safe:** *should the GPU be spent re-scoring identical criteria to split
R415's floor?* **Not for the sampling question — rung 1 of the attack ladder settles it for free.**

## Result — `W_NO_SAMPLING`. Both plants pass. **Zero compute.**

| scanned | stochastic constructs |
|---|---|
| `covalx/judge.py::score` | **NONE** |
| `corebench/judge_core.py` | **NONE** |

Searched for: `do_sample=True` · `temperature=` · `top_p=` · `top_k=` · `.generate(` · `multinomial`/`np.random`/`random.`

**The judge is, in its own source's words, *"scored not generated: one forward pass per pair"*** — under `@torch.inference_mode()`, reading `sigmoid(logits[yes] − logits[no])` at the final position.

## ⛔ What this does to the last two rounds

| | |
|---|---|
| **R415** claimed 0.116489 as a *pipeline noise floor* | **It cannot be sampling noise.** There is no sampling step to be noisy |
| **R416** left the residual as *"selection vs scoring, needs the GPU"* | **The residual is `selection vs CONFIGURATION`** — and a configuration difference is not a noise floor |
| **R416's proposed GPU re-score** | **Not needed for this question.** It would measure kernel non-determinism and batch sensitivity — real, bounded far below 0.1 in a sigmoid of a logit gap, and **not what R415 claimed to have found** |

## ⭐ Rung 1 of the ladder, and both prior rounds skipped past it

> *"Gauge test (3 lines, zero compute): name the transformations that leave behaviour identical…
> **Cheapest kill available, always try first.**"*

**The transformation is re-running.** Whether the output *can* differ under it is a property of the
scoring path — **readable from source**. R415 measured, R416 corrected the measurement, and **both
went to a GPU re-score before anyone read the twenty lines that answer it.**

## Controls

| | returned |
|---|---|
| **PLANT (+)** | a synthetic `generate(do_sample=True, temperature=0.7, top_p=0.9)` snippet → flagged on `do_sample`, `temperature`, `top_p`, `generate` — `PASS`. *Five times this campaign has paid for a search with no positive control* |
| **PLANT (−)** | a pure logit-read snippet → **not** flagged — `PASS`, so the scan distinguishes rather than flags everything |
| **UNIT** ⭐ | instrument's unit = `Judge.score` body + its call site; claim's unit = *the scoring path*. **Written out and required equal** — a file-wide grep would break this silently by matching a `generate` in an unrelated helper |
| **QUALIFIERS** | the non-stochastic movers are reported too — `batch` (L3, padding inside a batch changes what the model attends to) and `dtype` — so **"deterministic" is never printed unqualified** |

## ⚠ Two limits, both against my own conclusion

1. **A source scan bounds what CAN vary; it does not measure what DOES.** This is an *inference*
   about behaviour. The verdict is about **the admissibility of R415's framing** and **whether to
   spend the GPU** — **not a measured floor.**
2. **The committed `.npz` files carry no batch field**, so whether the two runs used the same batch
   size **cannot be recovered**. That is a provenance gap — **named, not guessed** — and it is the
   most likely non-stochastic explanation left standing.

## Register

| criterion | status |
|---|---|
| **bitwise run-to-run equality** | **N/A** — only a re-run measures it, and this round argues it is not worth the GPU *for the sampling question* |
| **the size of kernel non-determinism** | **NOT MEASURED** — real and bounded, but not quantified here |
| **whether the two runs shared a batch size** | **UNRECOVERABLE** — no batch field in the artifacts |

## The sentence I can no longer write

> *"how much of the shift is scoring noise cannot be known without the GPU"* — **there is no sampling
> step in the scoring path.** Two rounds proposed an expensive measurement of a quantity the source
> says is not there.

Artifact: `results/r417_no_sampling.json`, source-stamped, `inference_not_measurement: true`.
