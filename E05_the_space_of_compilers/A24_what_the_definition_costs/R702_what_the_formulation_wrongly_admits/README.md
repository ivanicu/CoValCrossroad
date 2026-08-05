# R702 · what the formulation wrongly admits

**⭐⭐⭐ The formulation written one round ago **admits `topw_k6` and `topw_k8`** — sets larger than
any core the release ships. **F3 gave a lower bound and no upper one.** The mirror test found in one
round what the exclusion test missed in thirty.**

## THE TEST §4 SPECIFIES HAS TWO SIDES AND THIS ARC RAN ONE
Every clause of R701's formulation names an object it **excludes**. **None named one it admits that a
reader would refuse.** *A clause admitting something obviously wrong is as broken as one excluding
something obviously right.*

## WHAT IT ADMITS (G3 — every member)

| member | k | |
|---|---|---|
| `coval_core` | 4 | within |
| `topw_k3` | 3 | within |
| `topw_k4` | 4 | within |
| **`topw_k6`** | **6** | ⛔ **exceeds the release's own maximum** |
| **`topw_k8`** | **8** | ⛔ **exceeds the release's own maximum** |

Registered **A 2 [0,5] → 2, error 0** · **B (F3 does not exclude them) HOLDS** · **directional
HOLDS** · kill did not fire.

**Controls:** POSITIVE — `coval_core` (k=4) is within the card's max. **g=0** — `topw_k1` **is**
excluded by the lower bound, *so the clause can exclude*. NEGATIVE — an absent arm is unscored.
PLACEBO — identical.

## ⛔ AND THE FIX IS NOT A CEILING OF FOUR
**4 is the instance's number**, and naming it is exactly the error **constraint C1 forbids**. The
honest repair is a **two-sided bound stated as a bound**: *more than one, and no more than the
release's own maximum* — **citing the card as a scope rather than adopting its value as the
category's.** Landed in `STATEMENT.md`; R701 annotated.

## ⚠ TWO PROXIES, BOTH NAMED
**`k` is a proxy for a reader's refusal**, and **the card is a proxy for the reader**. The card gives
the **instance's** distribution, not the **category's** — the same gap C1 names, now appearing inside
the repair to C1's own clause.

## WHY THIRTY ROUNDS MISSED IT
§4's remedy reads as one question and is two. **The exclusion side is the one that kills a clause,
so it is the one that feels like rigour** — and the admission side only bites once a formulation
exists to be over-permissive. **The arc had no formulation until one round ago**, so the test had
nothing to run on.

## IMPOSSIBLE HERE
Whether a 6- or 8-criterion set **is** a core needs the **category's** definition — the thing a
release shipping one core cannot supply.

## NEXT
F3 is repaired; F1 and F2 have not had the mirror test run on them (`results/wrongly_admits.json`,
field `admitted`). Run it: for F1, name an admitted arm whose selection is label-free but which a
reader would refuse — `random_k4_s0` is label-free by construction. For F2, name an admitted arm that
beats a prompt-blind floor without being a core. Each is a one-line lookup against the same ledger,
and F3's defect was invisible until the same lookup was done.
