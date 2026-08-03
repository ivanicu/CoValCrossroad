# Claim card — criterion-level population heterogeneity

Written before any code, per the binding process rule.

---

## Claim

r42 established that every population contrast in this package is bounded inside
δ = 0.01 **in aggregate**. That is exactly the result that can coexist with substantial
disagreement underneath it, and the rescoped C19 says so explicitly. This round asks whether it
does:

1. do groups assign **opposite signs** to the same criterion?
2. are there criteria essentially **only one group raises**?
3. do **group-specific weights** predict that group's rankings better than pooled weights?

Question 3 is the decisive one, because 1 and 2 can be true while changing no decision — a
handful of reversed criteria that cancel out leave a shared rubric optimal for everybody.

## Estimand

For rating `r` by rater `i` on prompt `p`, criterion `c`, group `g`:

```
r_ipcg = μ_pc + δ_pcg + u_i + ε
```

- **sign-reversal rate**: over (p,c) rated by ≥2 groups with ≥`m` raters each, the fraction where
  `sign(μ_pc + δ_pcg)` differs between groups
- **minority-only criteria**: (p,c) whose raters come overwhelmingly from one group, reported
  against the base rate that group's share of raters already implies
- **weight specificity**: `A(own-group weights) − A(pooled weights)`, both estimated on
  **rater-disjoint** folds, evaluated on the held-out group members' individual rankings

## Is the target observed?

**Partly, and the gaps are load-bearing.**

- 148 of 1,160 criterion raters (12.8%) have **no annotator record**, hence no group. Every
  statement here is scoped to the 87.2% who do — including any statement of *absence*.
- Groups are demographic proxies (country, generative-AI usage, age), not value constituencies.
  r16–r18's latent partition was frozen precisely because it named no constituency; using
  demographics instead does not fix that, it just makes the label honest.
- The **direction** being tested is itself post-choice. If two groups agree on a sign because the
  menu made it salient to both, this round records agreement and cannot see the shared cause.

## Alternative worlds

| world | prediction |
|---|---|
| **shared rubric is adequate** | low reversal rate, no minority-only excess, group weights ≤ pooled |
| **aggregate hides real conflict** | reversal rate above its own null, **and** group weights beat pooled |
| **reversals are noise** | reversal rate at or below the permutation null; group weights **worse** than pooled (fewer raters, more variance) |
| **conflict exists but doesn't matter** | reversals above null, group weights **not** better — the disagreements do not move choices |

Worlds 2 and 4 are separated only by question 3, which is why the round is not just a
reversal count.

## Intervention

None. Observational, on the released ratings.

## Null / positive control

**The reversal rate has a mandatory null.** With finite raters per cell, sign disagreement occurs
by sampling alone; a raw reversal rate is uninterpretable. The null **permutes group labels within
each (p,c)**, preserving cell sizes and the rating distribution, so it holds everything constant
except the group structure. The reported quantity is observed **minus** null.

**Positive control:** inject a synthetic group whose ratings on a random 20% of criteria are
sign-flipped, and confirm the pipeline recovers an elevated reversal rate and a group-weight
advantage. A heterogeneity detector that has never returned "heterogeneous" cannot be trusted
when it returns "homogeneous" — that is silence, not an acquittal.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes, and the positive control is exactly
the demonstration that it can.

**2. Does it observe the target?** It observes demographic groups, not value constituencies, and
only for the 87.2% with an annotator record. Both scopes travel with every number.

**3. By what path can construction data reach evaluation?** Weights and rankings come from the
same elicitation. Question 3 is therefore run **rater-disjoint**, the same isolation r34/r37
established as necessary; without it, group-specific weights would win trivially by memorising
their own raters.

**4. What other world produces the same result?** **Group size.** A smaller group yields noisier
weights and noisier per-criterion signs, which inflates reversal counts and depresses
group-weight performance simultaneously — one nuisance producing an apparent answer to both
questions. Controlled by matching group sizes by subsampling and by reporting the null, which
inherits the same cell sizes.

**5. Which decision changes?** If group weights beat pooled, a single CoVal rubric is the wrong
object and the aggregation question (layer 5) becomes live and unavoidable. If they do not, the
shared rubric stands **for these groups at this resolution**, and the human protocol does not
need to stratify recruitment on demographics.

---

## Stopping rule

CPU only. It ends when the reversal rate has a null, the weight comparison is cross-fitted and
size-matched, and the positive control has passed. If the positive control fails, **nothing else
in the round is reported**.
