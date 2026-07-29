# Claim card — does the cross-rater direction survive on criteria nobody else saw?

Written before any code, per the binding process rule.

---

## Claim

r34 showed the post-ranking criterion direction generalises across people (+0.0576 cross-fitted).
Item 1 rescoped that correctly: it refutes *individual* circularity and leaves **shared-menu
endogeneity** untouched, because every participant saw the same four responses.

But r48 established that participants also shared something else: **the same six pre-seeded
criteria**, identically for every rater on a prompt. The write-in criteria are not shared —
each was authored by one participant and, per r48's structural gap, rated by exactly that one
person.

So the shared-menu concern has **two** channels that have never been separated:

```
shared RESPONSES  →  shared salience  →  Sᵢ        (unavoidable in this release)
shared CRITERIA   →  shared salience  →  Sᵢ        (avoidable: write-ins are private)
```

**Claim to test:** the cross-fitted direction advantage survives when it is estimated from
**write-in criteria only** — criteria one participant wrote and only that participant ever rated,
used to predict a *different* participant's ranking.

## Estimand

Cross-fitted, rater-disjoint, per provenance class:

```
D_prov = A(sign weights from TRAIN raters, criteria of class `prov`)
       − A(direction-free weights, same criteria)          prov ∈ {seed, writein}
```

with the two classes **size-matched by subsampling to equal criteria per prompt**, because seed
carries ~5.7 and write-in ~10.2 per prompt and more criteria is not neutral.

## Is the target observed?

**Partly, and the residual is the point.** The provenance classes are exactly identified (r48:
0.1% gap, 6-per-prompt cap). Rater identity and fold assignment are observed. So "does the
direction transfer across people on private criteria?" is answerable.

What remains unobserved is the **response** channel: even a write-in criterion was written after
seeing the same four candidates everyone else saw. So a positive result narrows shared-menu
endogeneity to the *response* channel; it does **not** eliminate it. Nothing in this release can.

## Alternative worlds

| world | prediction |
|---|---|
| **direction is a shared-criterion artifact** | `D_seed` ≫ `D_writein`; write-in transfer collapses toward zero |
| **direction is a shared-response artifact** | both classes transfer about equally — the shared thing is the menu of responses, and private criteria inherit it |
| **direction is a population property** | both transfer, and roughly equally |
| **write-ins are just noisier** | `D_writein` < `D_seed` but with wide intervals and no collapse |

⚠ Worlds 2 and 3 make the **same** prediction here and this round cannot separate them. That is
stated because a result showing both classes transfer will be tempting to read as world 3, and
world 2 remains fully alive.

## Intervention

None. Re-analysis of released ratings with the r34 cross-fitting scheme.

## Null / positive control

- **Positive control:** the `all`-criteria arm must reproduce r34's direction advantage
  (≈ +0.058). If it does not, the reimplementation is not r34's estimator and no per-class number
  is interpretable.
- **Null:** shuffled signs within each provenance class, which r34 showed must fall **below** the
  direction-free arm if the sign channel carries real structure.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes — write-in transfer collapsing to zero
is a live outcome and would show the direction is carried by the shared criteria.

**2. Does it observe the target?** The criterion channel yes; the response channel no.

**3. By what path can construction data reach evaluation?** A write-in criterion's single rater is
also a ranker. If that rater were in both train and test the estimate would be circular — so folds
are **rater-disjoint** and a write-in contributes a weight only when its author is in TRAIN and is
never evaluated on its author's own ranking.

**4. What other world produces this?** **Criterion count**, controlled by size-matching, and
**rater count per criterion** — seeded items have ~15 raters averaging into a stable sign,
write-ins have one. A single-rater sign is noisier, which biases *against* write-ins, so a
positive write-in result is conservative and a negative one is ambiguous. Stated in the output.

**5. Which decision changes?** If write-in transfer holds, S_pre's design can drop the shared-
criteria arm and concentrate on response-blindness. If it collapses, the PRE arm must randomise
criterion *provision* as well as response exposure, which is a different and more expensive study.

---

## Stopping rule

CPU only, on released ratings. Ends when both classes have a size-matched cross-fitted estimate
with its null, and the `all` arm has reproduced r34. If the positive control fails, nothing is
reported.
