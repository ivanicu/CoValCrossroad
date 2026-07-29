# Claim card — out-of-sample replication of the spread-loss effect

Written before any code, and **committed before the round runs**. The commit timestamp is the
only thing that distinguishes a replication from a second exploratory pass, so the prediction
below is numeric and it is recorded now.

---

## Claim being tested

r41 (entry 48) found, **post hoc**, that r12's attribution drop concentrates where the prompt's
own rubric loses its ability to separate the four responses:

```
D_spread_loss = sd(own-rubric score over the 4 originals) − sd(over the 4 fresh)
```

`r = +0.2309` length-controlled (p = 0.0010) on r12's 250 prompts, surviving a donor-arm control
at `+0.2693` while the donor arm alone gave `−0.0351` (p = 0.586).

It was discovered while serving as a nuisance control. **That provenance is exactly why this
round exists.**

## Why an out-of-sample test is possible at all

r12 used the **first 250** joined prompts. **718 are untouched** — by r12, r39, r40 and r41. They
have never been generated for, scored, or looked at in this project. Fresh responses for 250 of
them are a genuine held-out sample, not a re-analysis.

Generating them is permitted now and was not before: the GPU rule was *"generate response sets
only after the human protocol is frozen,"* and r45 + `PREREGISTRATION.md` froze it. This round
does not touch the frozen 60 and does not alter them.

## PREREGISTERED PREDICTION — recorded before the run

| quantity | predicted | counts as |
|---|---|---|
| `D_spread_loss` vs drop, length-controlled | **positive, r ∈ [+0.12, +0.34]**, 95% CI excluding 0 | **REPLICATED** |
| same, donor arm partialled out | positive, CI excluding 0 | supports non-mechanical reading |
| **donor** spread loss vs drop | **not significant**, \|r\| < 0.12 | supports non-mechanical reading |
| corr(spread loss, generic embedding distance) | \|r\| < 0.15 | confirms it is a distinct axis |
| hull violation, length-controlled | **negative or ns** — novelty stays refuted | confirms r41's refutation |

**FAILURE conditions, declared now:**
- point estimate **≤ 0**, or 95% CI includes 0 → **NOT REPLICATED**, and entry 48 is downgraded
  to a single-sample artifact in the register
- donor arm becomes **significant with a similar magnitude** → the mechanical reading wins after
  all, and the non-mechanical claim is retracted
- point estimate positive but **below +0.12** → **WEAKER THAN CLAIMED**; the effect survives and
  the r41 magnitude is reported as inflated by the selection that discovered it

No outcome here leaves the r41 sentence unchanged, which is the test of whether this is worth
GPU time.

## Is the target observed?

**No — same limitation as r41, and it does not shrink with sample size.** `D_spread_loss` is
measured by the same judge whose off-distribution validity is the open question, and the outcome
is attribution against a **model gold proxy**, not human rankings. A perfect replication here
confirms the effect is *real and stable in the proxy world*. It cannot confirm it is about human
preference. That is H_fresh, and this round is not a substitute for it.

## Alternative worlds

| world | prediction |
|---|---|
| **real scope effect** | replicates in range; donor arm stays null |
| **selection artifact of r41** | point estimate collapses toward 0 |
| **mechanical accuracy identity** | replicates, but the donor arm now replicates too |
| **inflated by discovery** | replicates positive but materially below +0.23 |

## Intervention

None on CoVal. Generation is an intervention on **my** response distribution, with r12's exact
parameters (temperature 0.9, top_p 0.95, max_new_tokens 180, same few-shot preamble, same
generator) so the response distribution is the same object r12 sampled.

## Null / positive control

- **Discrimination control** (r12's, reused): if gold cannot order the fresh responses, the whole
  comparison is void. Reported before any correlation.
- **Permutation null** on every correlation, as in r41.
- **Positive control on the judge**: the ORIGINAL-set attribution must come back **positive**, as
  it did in r12 (+0.102). If the held-out originals do not reproduce a positive own-rubric
  advantage, the pipeline is broken on this slice and no fresh-response result is interpretable.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes — the failure conditions above are
declared with numbers, before the run.

**2. Does it observe the target?** No. Proxy gold, same judge. Stated in the output.

**3. By what path can construction data reach evaluation?** The criteria for these prompts were
written by raters who saw *their* four original responses — never these fresh ones. The rubric
cannot have been fitted to the generated text. The donor permutation is drawn within the
held-out slice so no donor is a prompt's own rubric.

**4. What other world produces this?** Length, and the mechanical accuracy identity. Length is
partialled out; the mechanical reading is tested by the donor arm, which is the whole reason the
donor satisfaction tensor is persisted rather than discarded.

**5. Which decision changes?** If it replicates, the spread-loss axis enters the human protocol
as a stratification variable and entry 48 is upgraded from exploratory to replicated-in-proxy.
If it fails, entry 48 is downgraded in the register and the README sentence is withdrawn.

---

## Stopping rule

One generation pass and one judge pass over 250 held-out prompts. No sweeps, no second sampling
temperature, no best-of-n. The round ends when the preregistered table above has been filled in
and the register updated in whichever direction the numbers point.
