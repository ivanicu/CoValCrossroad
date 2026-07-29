# Claim card — the core compiler lineage

Written before any code, per the binding process rule.

---

## Claim

r33 established that CoVal-core scored with **no ratings at all** beats CoVal-full scored the
same way by **+0.0663** — core has internalised post-choice polarity into its criterion text.
That number is a **single confounded quantity**: the dataset card documents that core is
produced by polarity rewriting, cleanup, semantic merging, score adjustment, compatibility
selection and truncation to ≤4 items, and +0.0663 is their sum. Nothing says which step does
the work.

## Is the target observed?

**No, and this is the round's defining limitation — it changes what the round can be.**

The release ships **C0** (full criteria with ratings) and **C6** (core). The intermediate
artifacts C1–C5 **do not exist in any public file**, and OpenAI's compiler is not published.
Verified field by field before writing this card.

So a *decomposition* of the actual compiler is **impossible from this release**. What is
possible is a **reconstruction**: build a simulated pipeline whose stages are the documented
operations, measure the increment each simulated stage contributes, and then measure **the
residual between the simulated end state and the real core**.

The residual is the honest deliverable. It says how much of core my stages fail to explain,
and a large residual is a finding about what the compiler does that the card does not describe.
**No stage increment here may ever be reported as "step X of OpenAI's compiler contributes Y."**

## Estimand

For each simulated stage `k`, cross-fitted concordance against individual rater rankings:

```
Δ_k  = A(S_k) − A(S_{k−1})            stage increment
R    = A(core_real) − A(S_6)          residual the reconstruction does not explain
```

with `A` measured under **equal weights and no ratings**, which is r33's regime and the only
one in which the question "did the polarity move into the text?" is even askable.

## Alternative worlds

| world | prediction |
|---|---|
| **polarity rewrite does the work** | Δ at the rewrite stage dominates; residual small |
| **selection does the work** | Δ concentrated at compatibility selection / truncation — core is better because it keeps the *predictive* criteria, not because it rephrased them |
| **merging does the work** | Δ at dedup/merge; core wins by removing redundancy that equal weighting over-counts |
| **the card does not describe the compiler** | every simulated Δ small, **residual large** |

Worlds 1 and 2 are the interesting fork: *rewriting* is a claim about semantics, *selection* is
a claim about which criteria survived — and a selection effect would mean core encodes the
post-choice ranking through **which items it kept**, which is a different and stronger form of
the r33 finding.

## Intervention

Simulated stages are interventions **on my reconstruction**, not on CoVal. Causal language is
licensed about the reconstruction and about nothing else.

## Null / positive control

**Positive control:** a stage that is a no-op (identity transform) must return Δ ≈ 0. If an
identity stage produces a non-zero increment, the harness is measuring its own re-scoring noise
and every Δ is void.

**Null for selection:** the compatibility-selection stage picks ≤4 criteria. A *random* choice
of ≤4 must be run alongside, because keeping any 4 criteria changes the score, and the question
is whether the selection rule beats an arbitrary one of the same size. Without that, a
selection Δ measures truncation, not selection.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes — a large residual would say the
reconstruction is wrong, and that is a live outcome, not a failure mode.

**2. Does it observe the target?** **No.** C1–C5 are unobservable. Everything is a
reconstruction and every output sentence must carry that word.

**3. By what path can construction data reach evaluation?** The simulated stages are built from
the *ratings*, and evaluation is against the *rankings* those same raters gave. Stage
construction therefore uses the same elicitation as the outcome, so all stages are built on
**rater-disjoint folds** — otherwise a selection stage would trivially select the criteria that
predict its own raters.

**4. What other world produces the same result?** **Criterion count.** Core has ≤4 items and
full has many more; under equal weighting, fewer items is not neutral. Any Δ at a stage that
changes the count is confounded with the count itself, which is why the random-selection null
holds size fixed.

**5. Which decision changes?** If the gain is **selection**, then core is a post-choice artifact
in a way rephrasing alone would not make it, and the recommendation to consumers of CoVal-core
changes from "know that polarity is in the wording" to "know that item membership encodes the
original ranking". If the residual dominates, the card's description of core is incomplete and
that is what gets reported.

---

## Stopping rule

CPU only, reusing r04's satisfaction tensors for both full and core. Ends when every stage has
an increment, the identity control has returned ≈ 0, the selection stage has its size-matched
random null, and the residual is reported. If the identity control fails, nothing is reported.
