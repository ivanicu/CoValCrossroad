# R337 — a label-free selection signature DOES generalise, at AUC 0.866

> ⚠ **The directory name records my prediction, and the data refuted it.** I expected
> `W-POPULATION` — that every clause-③ route dies to n=4 leaky arms. It does not. The name is kept
> (annotate, never rewrite) so the wrong prediction stays visible next to the result.

**Decision this makes safe:** whether clause ③ can carry a computed test after R336 killed the
performance route. **It can.** **W-SIGNATURE.**

## The result

| feature set | within-arm AUC | **held-out-arm AUC** | folds |
|---|---:|---:|---|
| structure only | 0.836 ±0.005 | **0.834** | 0.871 · 0.748 · 0.860 · 0.857 |
| text only | 0.654 ±0.007 | 0.658 | 0.658 · 0.636 · 0.667 · 0.671 |
| **structure + text** | **0.870** ±0.003 | **0.866** | 0.901 · **0.789** · 0.889 · 0.885 |

**Leave-one-ARM-out**, not leave-one-prompt-out — holding out prompts would let the classifier
memorise the arm. Within-arm and held-out-arm AUC are **the same**, which is the opposite of the
overfitting signature I predicted.

**Features are label-free throughout**: importance weight of the selected criteria (mean/max/sd),
satisfaction variance and mean, rubric position, criterion length, token count, within-set token
Jaccard, verbatim-match rate. **None touches a human label.**

## Controls — and the planted one is why the AUC is readable

| control | result |
|---|---|
| **positive** — plant a feature that *is* the label + noise (dose 6.0) | held-out AUC **1.000** — the harness can see a signature that is there |
| **positive @ g=0** — the same feature at pure noise | returns to **0.866**, the unplanted value |
| **negative** — shuffle **ARM** labels (not rows) | **0.509**, chance |
| **placebo** — pure-noise features | within 0.520, held-out 0.521 |

**Shuffling rows would have left each arm's identity intact** — the permutation has to destroy the
thing under test, and shuffling at the arm level is what does that.

## ⛔ And R250 is not this — conflating them would have been the fifth error

R250 (86 rounds old) recovers a criterion's **PARENT** — provenance of *text*, 0.9871 recovery at
40% token drop against chance 0.0792. **Clause ③ asks how the SUBSET was CHOSEN.** A leaky core and a
clean core draw from the same rubric, so their criteria share textual ancestry; what differs is
*which* were picked. **Two estimands.**

## ⚠ Four consecutive next-gradient lines wrong about my own work

| round | the closing claim | what already existed |
|---|---|---|
| R333 | *"every A2 samples ONE annotator"* | **R306** migrated to all 16, 26 rounds earlier |
| R334 | *"clause ③ has no instrument at all"* | **R295** built one |
| R336 | *"criterion text … never touched in 300+ rounds"* | **R250** did it 86 rounds earlier |
| R333 | *"margins are 5.6×, so it closes trivially"* | wrong on mechanism (R334) |

**Three of the four manufactured work that already existed.** §4 says the direction is not
systematic; over these four it is.

## ⚠ Two scope limits, both mine

**① 398 prompts, not 968.** The arm intersection is dragged down by `promptecho` — **the same
defect R330 caught, third occurrence.** The estimate is honest on that subpopulation; it is not the
full release, and the population is stated rather than rounded up.

**② One fold sits at 0.789.** With 4 leaky arms the fold spread (0.789–0.901) is the real
uncertainty, and it is wider than the across-seed sd suggests.

## What this settles

> **A label-free signature of label-driven selection exists and transfers to an arm the classifier
> never saw.** Clause ③ is not confined to a source-reading annotation — but the test's confidence
> is bounded by 4 positive arms, and the fold spread is what to quote.

## Scope

R294's 40 arms with a committed core json · 398 prompts in the 3-way intersection · features from
the rubric and the judge's satisfaction only · logistic discrimination on standardised features ·
3 feature sets × 3 seeds × 4 held-out folds.

## What this cannot do

Extend past 4 positive arms. Manufacturing more (as R335 did) makes them **mine** rather than the
release's — which is exactly the generalisation under test, so it cannot be fixed by manufacturing.
