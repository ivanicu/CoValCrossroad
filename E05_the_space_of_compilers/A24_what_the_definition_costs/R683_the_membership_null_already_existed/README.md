# R683 · the membership null already existed, and it is exact

**⭐⭐⭐ R682's NEXT proposed re-running R361 against ONE perturbed set. R361 already enumerates ALL
`C(9,4) = 126` membership assignments, exactly. And the committed answer is a scope condition on the
definition: the extension separates from the label-reading arms at the **2B** judge (gap **−4.50**,
0.8th percentile, **p = 0.0159, RESOLVED**) and **not** at **0.8B** (gap +2.25, 90.5th percentile,
p = 0.2857).**

## ⭐ CHECK #284 · THE PROPOSAL WAS STRICTLY WEAKER THAN THE COMMITTED INSTRUMENT
One perturbation versus an exact enumeration of 126. **And re-running a round destroyed its artifact
once already in this arc.** P4's prior-art gate found this **before any code was written**, which is
the only reason it cost nothing. ⭐ **Fourth time in this arc the answer sat in a committed
artifact** — R664's lesson, then R676, R678, and now here.

## THE COMMITTED NULL (G3 — both judges, no cell hidden)

| judge | gap | percentile | p | verdict |
|---|---|---|---|---|
| **2B** | **−4.50** | 0.8% | **0.0159** | **RESOLVED** |
| 0.8B | +2.25 | 90.5% | 0.2857 | **NOT RESOLVED** |

mean label rank **2.5** vs five **7.0** at 2B · **6.25** vs **4.0** at 0.8B
rank sd — label **3.59** at 0.8B vs **1.29** at 2B; five **1.58** at both

**Controls:** POSITIVE — R361's own committed `positive`/`g0`/`placebo` all true. **ARITHMETIC** — null
size must be `C(9,4) = 126` → committed 126. **g=0** — a percentile of 0.5 maps to two-sided p = 1.0.
PLACEBO — recomputation twice identical.

## ⭐ THE ARITHMETIC AUDIT CONFIRMED THE ARTIFACT AND CORRECTED MY READING OF IT
Recomputing the two-sided p **from `pct` alone** gives **0.1905** at 0.8B against the committed
**0.2857**. The committed value is the careful one: it computes **both tails separately**, which is
required because **the null has ties**. A pct-only formula cannot. **The audit confirms rather than
corrects — and the direction matters, because the naive recomputation is the one that would have
made the result look resolved.**

## WHAT THIS SAYS ABOUT THE DEFINITION
At 2B the **label-reading arms rank ABOVE** the extension and the split is resolved — which is
exactly what a provenance clause is for: **③ excludes the arms that win by reading labels.** At 0.8B
that separation does not survive. ⚠ **And the reason is visible in the spread**: the label group's
sd is **3.59** at 0.8B against **1.58** for the five — **the label-users SPLIT at the smaller judge,
so a mean gap is the wrong summary there**, which the round's own null already registers as
NOT RESOLVED rather than as a small effect.

**So the extension's separation from label-readers is INSTRUMENT-DEPENDENT**, and any statement of
the definition that omits the judge is missing a scope condition.

## IDENTIFICATION LIMIT
This reads a committed artifact; it does **not** re-execute R361. A number wrong in the file is wrong
here. **Internal consistency is what is claimed, and only that** — the source sha256 is recorded.

## NEXT
The separation holds at 2B and fails at 0.8B (`results/membership_null.json`, field `judges`), and
`STATEMENT.md` now carries that as a scope condition. Two judges is a thin basis for the word
"instrument-dependent": check how many of the arc's other clause verdicts were measured at **one**
judge only, by reading each round's `POOLS`/judge field out of its committed artifact. A clause
resolved at a single judge and a clause resolved at both are different claims, and the deliverable
does not currently distinguish them.
