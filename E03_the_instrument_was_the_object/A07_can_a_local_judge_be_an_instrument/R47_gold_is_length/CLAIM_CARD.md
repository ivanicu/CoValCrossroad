# Claim card — is r12's inversion a property of the gold proxy rather than the rubric?

Written before any code, per the binding process rule.

---

## Claim

r12's inversion — the own-rubric advantage falling from **+0.102** on released candidates to
**−0.064** on fresh ones, replicated by r46 at **+0.085 / −0.072** — is the most robust
unexplained result in this project. Generic distance (r40), criterion-space novelty (r41) and
discriminating-power loss (r46) have each been ruled out.

Every one of those tested a property of the **rubric**. None tested the **outcome variable**.

The attribution is measured against the r08 gold head, and that head was fitted with **length as
an explicit feature** — `hstack([embedding, [char_len, word_len]]) @ w`, with the char-length
weight at |w| = 0.2085 against a mean embedding weight of 0.0620, roughly 2× per dimension.

**Claim to test:** on fresh responses, gold ordering is substantially more length-driven than on
the released candidates. If so, "own rubric vs donor rubric on fresh" is partly a contest over
which rubric correlates with **length**, and the inversion is a fact about the proxy rather than
about rubric transport.

## Estimand

Within each prompt, over its four responses:

```
q_set   = mean over prompts of corr( gold(r), word_count(r) )     for set ∈ {original, fresh}
```

and then the decisive one — attribution recomputed against a **length-residualised** gold, where
within each prompt gold is regressed on word count and the residual defines the ordering:

```
Δ_resid = attribution(ORIGINAL | gold⊥length) − attribution(FRESH | gold⊥length)
```

## Is the target observed?

**The proxy is fully observed; the target is not.** Gold, its length features, and the
satisfaction scores are all in hand, so the question "is gold ordering fresh responses by
length?" is answerable exactly.

What remains unobserved is whether **humans** would order them by length too. Length is not a
nuisance by definition — a longer answer is often genuinely better, and residualising it removes
real signal along with the artifact. So a shrinking inversion under residualisation does **not**
prove the inversion is spurious; it shows the inversion is *carried by* the length-aligned
component, which is a different and weaker statement. Both readings are reported.

## Alternative worlds

| world | prediction |
|---|---|
| **proxy artifact** | gold↔length much higher on fresh; inversion shrinks or vanishes under residualisation |
| **real transport failure** | gold↔length similar across sets; inversion survives residualisation |
| **length is real quality** | gold↔length higher on fresh, inversion shrinks, **but** so does the ORIGINAL-set advantage — length was load-bearing everywhere, not a fresh-set artifact |
| **mixed** | inversion shrinks partially; report the fraction, not a verdict |

The third row is why the ORIGINAL arm must be recomputed under the same residualisation. Testing
only the fresh arm would let a general loss of signal look like a targeted debunking.

## Intervention

None on data. The residualisation is an intervention on **my estimator**, and it is applied
identically to both arms and both response sets.

## Null / positive control

**Positive control:** residualising gold on a variable it does *not* encode (a per-response
random draw) must leave the attribution essentially unchanged. If a random residualisation moves
the number, the procedure is destroying signal by construction and no comparison is licensed.

**Sanity floor:** after residualisation gold must still order responses — if within-prompt gold
variance collapses, the comparison is void, and that is checked before any attribution is read.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes: gold↔length could be equal across
sets, and the inversion could survive residualisation unchanged. That outcome strengthens the
transport reading rather than weakening it.

**2. Does it observe the target?** It observes the proxy exactly and human preference not at all.

**3. By what path can construction data reach evaluation?** The gold head was fitted on r08's
data, which is the same release; but it is applied identically to both arms of both sets, so it
cannot favour own over donor rubrics. The length features are the specific channel under test.

**4. What other world produces this?** Degenerate generations. At temperature 0.9 some fresh
responses truncate or repeat, and those are both short and bad — so length may proxy genuine
quality specifically on the fresh set. Reported by measuring length variance per set rather than
asserting it either way.

**5. Which decision changes?** If the inversion is length-carried, then **H_fresh must collect
human rankings with response length recorded and controlled**, and r12 cannot be cited as
evidence of rubric transport failure without that caveat. If it survives, r12 hardens into a
result about rubrics and the human experiment is confirmatory rather than diagnostic.

---

## Stopping rule

CPU only, on tensors already persisted by r41 and r46. Ends when both response sets have their
gold↔length correlation, both arms have been recomputed under residualisation, and the random
residualisation control has passed. If the control fails, nothing else is reported.
