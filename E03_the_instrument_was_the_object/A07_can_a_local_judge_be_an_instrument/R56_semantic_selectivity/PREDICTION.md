# Preregistered prediction — semantic selectivity collapse vs the attribution drop

**Committed before the held-out correlation is computed.** Entry 48 is why: `D_spread_loss` looked
solid on the discovery sample, accumulated three same-sample confirmations, and died out of
sample. The only thing that distinguishes this from that is the order of operations.

## What is already known (both samples, computed)

Per-criterion **semantic** selectivity = mean over a prompt's criteria of the sd of judge
satisfaction across the four responses. Distinct from r41's `D_spread_loss`, which aggregated
criteria *first*; this takes the per-criterion spread and then aggregates.

| | discovery (250) | held out (250) |
|---|---:|---:|
| own advantage, original | +0.0403 | +0.0461 |
| own advantage, fresh | +0.0264 | +0.0231 |
| **collapse** | **+0.0139 [+0.0053, +0.0226]** | **+0.0230 [+0.0146, +0.0316]** |

The collapse itself **replicates**. That part is not at issue.

## What is NOT yet computed, and is predicted here

`corr(per-prompt selectivity collapse, per-prompt attribution drop)` on the **held-out** sample.

Discovery value: **+0.1806 [+0.0708, +0.2880]** — significant, positive, and **not preregistered**.

| | prediction |
|---|---|
| point estimate | **positive, r ∈ [+0.06, +0.30]** |
| 95% CI | excludes zero |

**Failure conditions, declared now:**

- CI includes zero → **NOT REPLICATED.** The correlation was selection on the discovery sample,
  exactly as entry 48 was. The collapse would still stand as a replicated fact, but its link to
  r12 would not.
- point estimate **negative** → not replicated, and the discovery value is withdrawn outright.
- positive but **below +0.06** → replicated in sign, magnitude inflated by discovery.

## Why this is worth the discipline rather than just reporting the discovery number

r55 established that *lexical* selectivity does **not** collapse (+0.0002, equivalent to zero at
δ=0.01) and explicitly stated it was blind to the semantic analogue. This is that analogue. If the
correlation holds out of sample it is the first mechanism for r12 to survive an out-of-sample
test — every prior candidate (r40 generic distance, r41 criterion novelty, r46 spread loss, r47
length, r54/r55 overlap) has failed or been ruled out.

That is precisely why it must not be believed on discovery-sample evidence.

## Scope that travels regardless of outcome

Selectivity is measured from judge satisfaction, and the attribution it is correlated against is
scored by the r08 model gold head (entry 50). **Both sides of this correlation are proxy-world.**
A held-out replication would establish the mechanism is real and stable in the proxy; it would not
establish it is about human preference. That remains H_fresh.

---

# OUTCOME (computed after the above was committed as `5cb7426`)

| | discovery | held out |
|---|---:|---:|
| corr(selectivity collapse, attribution drop) | +0.1806 [+0.0708, +0.2880] | **+0.0198 [−0.1196, +0.1592]** |

**NOT REPLICATED.** The CI includes zero and the point estimate falls far below the predicted
floor of +0.06. Per the declared failure condition, **the discovery correlation is withdrawn**: it
was selection on the sample that produced it.

## What survives, and it is not nothing

The **collapse itself replicated** — +0.0139 [+0.0053, +0.0226] on discovery and +0.0230
[+0.0146, +0.0316] held out, both excluding zero, the held-out value larger. So:

> Per-criterion semantic selectivity really does fall on fresh responses. It does **not** predict
> which prompts show the attribution drop.

That is the same shape r54 found for mean lexical overlap: a real mechanism with no per-prompt
link to the outcome. Two different channels, same verdict.

## What this says about the process rather than the data

This is the **second** time a promising r12 mechanism has been killed by writing the prediction
down first — entry 48 was the first. In both cases the discovery-sample number was significant,
positive, and had a plausible story; in both cases the held-out number was near zero.

The relevant fact is not that I was wrong twice. It is that **without the preregistration both
would have been reported as findings**, and the second would have been reported more confidently
than the first, because the collapse underneath it genuinely replicates and would have lent it
borrowed credibility.
