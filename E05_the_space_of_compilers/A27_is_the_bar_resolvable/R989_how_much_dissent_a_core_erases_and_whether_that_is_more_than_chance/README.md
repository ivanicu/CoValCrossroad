# R989 · the null inverts the number — rubric criteria are more sign-coherent than chance, not less

**THE DECISION THIS MAKES SAFE.** Whether "80% of rubric items are contested" can be reported.
**It cannot** — against its own null the same number means the **opposite**.

---

## The headline, and why the raw share is a trap

| | |
|---|---|
| observed: items whose annotators disagree in **sign** | **80.0%** (4,451 of 5,564) |
| **null** — within-prompt permutation preserving the score multiset and each item's annotator count | **93.3%** [92.9, 93.8] |
| observed vs null | **+0.1285 BELOW the lower bound**, on every seed |

**Read alone, 80% says "most criteria are contested." Read against its own null, it says criteria
attract markedly more sign-agreement than a reallocation of the same scores would produce.** With
~16 annotators spanning −10..+10, sign disagreement is nearly *guaranteed* by chance; the criteria
resist it.

## ⛔ And my verdict string got the direction backwards

v1 printed **"by −0.1379 above the highest upper bound"** and labelled the world *"ITEMS ARE GENUINELY
CONTESTED"*. The branch fired on `outside`, which is true on **either** side, and the prose assumed
the high one. **§4's *the verdict string is not a computation*, in my own script.**

The direction is now **derived from the sign**, and it reverses the world. A negative number printed
after the word *"above"* is what a typed conclusion looks like when the data disagrees with it.

## The cheap path was closed, and the wall is measured

R988's NEXT reached for non-conflict because the card says the construction *"rewrites all rubric
items to have positive weight"* — weights are numeric. **They are not published for the core**: a
`coval_core` item carries a `criterion` string and nothing else.

| | |
|---|---|
| core items matching a `coval_full` criterion **verbatim** | **303 of 3,899 = 7.8%** |

So the weights are not recoverable by identity either — **cores are genuinely synthesized**, and what
a *particular* core erased cannot be recovered from this release. **Measured, not assumed.**

## ⚠ Two senses of "conflict", and this round measures the other one

| | |
|---|---|
| **the card's** `non-conflicting` | **BETWEEN** selected items — *"remain compatible with each other"* |
| **what is measured here** | **WITHIN** an item — annotators disagree about one criterion |

**They are different quantities.** The between-item sense needs a semantic compatibility instrument
and is registered as not built, not claimed.

## Controls

| control | result |
|---|---|
| **POSITIVE** | the core size distribution reproduces the card: **942 of 986 = 95.5%** have four, against its stated *"about 95%"* — so the field being read **is** the core |
| **PLACEBO** | an all-positive item returns `contested = False` |
| **NEGATIVE** | items with < 3 scores are **excluded, not scored** — **9,684** such, counted rather than dropped silently |
| **NOISE FLOOR** | the permutation null above, 200 draws × 3 seeds, reported as a band |

⚠ **9,684 excluded against 5,564 included.** Most `coval_full` items carry fewer than three scores,
so this population is the well-rated minority — stated, because a share computed on the majority
would be a different number.

## What this does not say

- **It is not "dissent the core erases."** The 7.8% match rate makes that mapping unavailable; this
  bounds what the **rewrite step operates on**, not what any core discarded.
- **It says nothing about between-item conflict**, which is the card's actual criterion.
- **One release.**

## Alternatives considered

**Report the 80% with the null as a caveat.** Refused: the null does not qualify the number, it
**reverses** it. A caveat would leave the headline standing in the wrong direction.

**Drop the `< 3 scores` threshold to include all 15,248 items.** Refused: sign disagreement is
undefined for a single score and near-impossible for two, so the null and the observation would both
be dominated by items that cannot be contested — inflating agreement for free.
