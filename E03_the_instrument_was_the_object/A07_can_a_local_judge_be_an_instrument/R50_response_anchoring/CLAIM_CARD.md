# Claim card — can the shared-response channel be separated after all?

Written before any code. This round exists because I asserted, in a report, that
*"'shared-response artifact' and 'population property' make identical predictions in every design
this release permits."* That is a universal claim about designs, made by me, and the honest
response to it is to look for a design rather than to repeat it.

---

## Claim

r49 showed the cross-rater direction transfers on **private** write-in criteria (+0.0777 vs
+0.0599 for the shared six, paired gap +0.0172). That closed the shared-**criterion** channel and
left the shared-**response** one open: every write-in was still authored after seeing the same
four candidates.

But write-ins are not uniform in how much they are *about* those four candidates. Some describe
a specific thing a specific response did — *"invents a statute"*, *"tells the user to lie to
their landlord"* — and some are general — *"maintain a respectful tone"*.

**Claim to test:** if the transferable direction is a shared-response artifact, it should
concentrate in the **response-anchored** write-ins. If it is a population property, low-anchored
criteria should transfer too.

## Estimand

Anchoring is measured as the maximum lexical containment of a criterion's content words in any
one of the prompt's four original responses:

```
anchor(c) = max over the 4 responses of  |tokens(c) ∩ tokens(r)| / |tokens(c)|
```

Then, within write-ins only, split at the **within-prompt median** and compute the cross-fitted,
rater-disjoint, size-matched direction advantage per stratum:

```
D_high − D_low
```

## Is the target observed?

**No — anchoring is a proxy for "about these responses", and a coarse one.** Lexical containment
rises with a criterion being concrete and topical, which correlates with being predictive for
reasons that have nothing to do with the response menu. A criterion can also be entirely about
one response while sharing few of its words.

So this round can **detect** a concentration; it cannot cleanly attribute one. A null result is
the more interpretable outcome: if transfer is flat across anchoring, the response-artifact story
has to explain why its supposed carrier does not matter.

## Alternative worlds

| world | prediction |
|---|---|
| **shared-response artifact** | `D_high` ≫ `D_low`; low-anchored write-ins transfer weakly |
| **population property** | `D_high` ≈ `D_low` |
| **anchoring is just concreteness** | `D_high` > `D_low` **and** the same gap appears among the pre-seeded six, which are not participant-authored and whose anchoring varies for unrelated reasons |
| **proxy too coarse** | both strata near the pooled value with wide intervals |

Row 3 is why the **seeded** class gets the same split as a control. If anchoring predicts transfer
there too, the effect is about concreteness, not about menu-induced construction.

## Intervention

None. Re-analysis with a text-derived stratification.

## Null / positive control

- **Positive control:** the pooled write-in arm must reproduce r49's +0.0777, or the stratification
  is built on a different estimator.
- **Null:** permute anchoring scores across criteria **within prompt**, preserving the marginal
  distribution and the strata sizes, destroying only the link between a criterion and its own
  anchoring.
- **Control class:** the same high/low split run on the pre-seeded six.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes — a large `D_high − D_low` would
support the artifact story and undercut r49's reading, which is my own recent result.

**2. Does it observe the target?** No. Lexical containment is a proxy for aboutness, stated in the
output and in every sentence that quotes the number.

**3. By what path can construction data reach evaluation?** Anchoring is computed from criterion
text and response text only — never from ratings or rankings — so the stratification cannot
encode the outcome. Folds stay rater-disjoint.

**4. What other world produces this?** Concreteness, handled by the seeded control; and criterion
**length**, since containment is normalised by criterion length and short criteria score high by
accident. Length is reported per stratum.

**5. Which decision changes?** If transfer concentrates in anchored criteria, S_pre's PRE arm
becomes the only informative design and my "narrowed to the response channel" sentence needs
withdrawing. If it is flat, the response-artifact story loses its most natural mechanism and
S_pre becomes confirmatory rather than decisive.

---

## Stopping rule

CPU only. Ends when both classes have a stratified estimate, the pooled arm reproduces r49, and
the permutation null has run. If the pooled arm does not reproduce r49, nothing is reported.
