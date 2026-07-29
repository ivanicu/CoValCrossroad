# Claim card — criterion-space support geometry

Written **before any code**, per the binding process rule. If this card cannot be completed,
the round does not get written.

---

## Claim

The r12 discrepancy — the rubric's own-vs-unrelated advantage falling from +0.102 on the
released candidates to −0.058 on fresh ones — concentrates on prompts whose fresh responses fall
**outside the criterion-satisfaction support** of the original four.

## Estimand

For each prompt, with `z_R(r) = (s(c₁,r), …, s(c_K,r))` the criterion-satisfaction vector under
rubric `R` and judge `J`:

```
corr( per-prompt attribution drop ,  novelty of {z_R(fresh)} w.r.t. {z_R(original)} )
```

reported per novelty measure, prompt-level bootstrap, with the **length gap partialled out**
(r40 established fresh responses are *longer*: 89 vs 76 median words).

## Is the target observed?

**No, and this is the round's largest limitation.** The target is *human preference on fresh
responses*. What is observed is a **judge-relative** geometry: `z_R` is produced by the same
satisfaction judge whose validity on fresh responses is itself unestablished. If the judge is
miscalibrated off-distribution, its criterion vectors are miscalibrated too, and novelty
measured in that space inherits the miscalibration.

So this round **cannot** distinguish *"fresh responses genuinely occupy new normative
territory"* from *"the judge scores them incoherently"*. It can only say whether the discrepancy
is **spatially organised** in criterion space rather than diffuse. That is worth knowing and it
is not the answer.

## Alternative worlds

| world | prediction |
|---|---|
| **rubric-conditioned support failure** | discrepancy rises with criterion-space novelty; generic distance stays flat (r40 found it *negative*) |
| **judge incoherence off-distribution** | novelty rises *and* judge-family disagreement in criterion space rises, and they are collinear |
| **proxy OOD** | discrepancy tracks neither; it tracks the gold head's own instability |
| **genuine value mismatch** | discrepancy is diffuse in criterion space — present at low novelty too |

Worlds 1 and 2 are separated by **judge-family disagreement**, which is why it is one of the
measures and not an afterthought. Worlds 3 and 4 are **not** separable here and need human data.

## Intervention

None. This is observational. No causal language is licensed anywhere in the output.

## Null

Permute the per-prompt novelty values across prompts, preserving their marginal distribution,
and recompute every correlation. Reported alongside, because a correlation across ~250 prompts
with four measures × three lineages invites exactly the multiplicity this project has already
been caught by.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?**
Yes. If the discrepancy were concentrated on prompts whose fresh responses land *inside* the
original criterion hull, every correlation flips sign. r40's generic-distance version already
returned an unexpected sign, so this is not a formality.

**2. Does it observe the target?**
**No** — see above. Judge-relative throughout.

**3. By what path can construction data reach evaluation?**
The criteria defining the space are the same criteria whose attribution drop is the outcome.
`z_R(original)` is therefore *guaranteed* to sit in a region the rubric describes well — that is
what the rubric was written for. **The hull is fitted on originals only**, and novelty is
measured for fresh responses against it, so the outcome cannot define the space it is measured
in. But the space is still rubric-conditioned, and a prompt with a more discriminating rubric
will have both a larger attribution and a more structured hull. That confound is real and
un-eliminated; it is reported, not solved.

**4. What other world produces the same result?**
Length and verbosity. A longer response can satisfy more criteria simultaneously, producing a
novel *combination* without occupying new normative territory. Partialled out, and the
correlation between novelty and the length gap is reported alongside.

**5. Which decision changes?**
If the discrepancy is spatially organised, the human-ranking sample (C38) must span the
criterion-novelty axis, and the judge-calibration sample must be stratified on it. If it is
diffuse, neither stratification is needed and the axis is dropped. **Either answer changes the
human protocol**, which is the only reason to spend GPU on it.

---

## Stopping rule

One GPU pass to persist the criterion×response satisfaction matrices for both response sets on
the **already-saved** fresh responses — no regeneration, no new sampling. All analysis on CPU.
If the null-permuted correlations are indistinguishable from the observed ones, the axis is
dropped from the human protocol and this line is frozen.
