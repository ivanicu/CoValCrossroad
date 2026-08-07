# R660 · The join looked like 86% traceability. Against a random baseline it is BELOW chance.

**Decision this makes safe:** whether R659's proposed per-wall failure rate can be computed from the
named entries. **No — and not because the answer is low. The metric is a check that cannot fail.**

## The number, and the floor that kills it

| | |
|---|---|
| named wall-entries reaching a declaring round's register | **31 of 36 · 86.1%** |
| **naming rounds AT RANDOM** (5 seeds) | **96.1% · [94.4%, 100.0%]** |
| base rate: rounds declaring a register | **290 of 336 · 86.3%** |
| **excess over the random floor** | **−10.0% — BELOW it** |

⭐⭐⭐ **86.1% looked like near-perfect traceability. Given a floor, it lands under chance.** Because
86.3% of *all* rounds declare a register, *"the named round declares one"* is nearly forced — **§4's
first row, `check that cannot fail`, built by me one round after quoting it.**

**So neither claim survives:** R659's inference is not supported, **and my own pre-registered
counter-prediction is retracted on its stated terms** — the quantity both were about carries no
information.

⭐ **The one informative number is the reverse rate:** only **53 of 290 declaring rounds (18.3%)** are
named by any wall-entry at all.

## The pre-registration, written before any code

> **point 12 · interval [4, 25]** · **directional:** *most named entries do NOT reach the named
> round's own register* · **kill:** ≥50% reaching retracts it.

| | |
|---|---|
| magnitude | **31 — OUTSIDE [4, 25]**, error **+19**. Second consecutive under-estimate. |
| directional | ⛔ **RETRACTED** — the first directional failure in six. |

## ⛔⛔ Two defects, both caught by controls, both this arc's recurring mechanisms

**① The ledger grew under the comparison.** The positive control read `tight 40 vs 39` — because
**R659's own retraction entries (689–692) were appended after R659 ran**, and entry **690** matches
the tight pattern. *A round that writes to the corpus it measures — R654's mechanism, now inside the
ledger, and the fifth time in this arc that corpus growth moved a baseline.* Repaired by pinning the
population to **R659's horizon (entry ≤ 688)** and reporting the new entry separately.

**② The verdict string ignored the control it had just computed.** v1 printed *"world A TRACEABLE —
R659's inference was sound"* on 86.1% while the random baseline sat two lines above at 96.1%. §4's
sub-kind ①. The branch now **references the baseline**, which this round's own docstring required.

## ⛔ Check #261 — the count was right, the inference was not

| claim | truth |
|---|---|
| *"36 of the 39 tight members name a round"* | ✓ |
| *"…**so** each overturned wall is traceable to where it was **declared**"* | **Does not follow.** An entry names where the **error was found**; the declaring round is usually earlier. **Naming is not tracing.** |
| *"that is the **only** per-wall failure rate this corpus can support"* | **False** — a rate over *declaring rounds* is a second, equally available denominator, computed here at **18.3%**. |

## Controls

| control | returned |
|---|---|
| **positive** — reproduce R659 at its own horizon | **tight 39 = 39, named 36 = 36** — PASS |
| **negative** — an entry naming `R999` (nonexistent) | **DANGLING** — PASS, *a name is not a hit* |
| **placebo** — an entry naming no round | **0 enter the population** — PASS |
| **g=0** — an empty ledger | **0** — PASS |
| ⭐ **random baseline** — 5 seeds, the missing arm | **96.1% [94.4%, 100%]** — *the metric's floor* |

**MULTIPLICITY:** 1 join × 36 entries + a reverse count over 290 declaring rounds + 4 controls +
a 5-seed baseline; every outcome printed untruncated.

**IMPOSSIBLE, named:** whether an entry is *about* the named round's register is a judgement about
prose that no pattern decides — so `REACHES-REGISTER` was an upper bound even before the baseline
killed it, and **the per-wall rate stays uncomputed rather than estimated.**

## The sentence I can no longer write

> *"86% of overturned walls trace back to the round that declared them."*

**It is below chance.** A high share against no floor is not a finding, and this one was manufactured
by a base rate I had measured myself one round earlier.

## NEXT

**18.3% is the first number in this thread with a floor under it — but it has no floor yet either.**
53 of 290 declaring rounds are named by a wall-entry, and the obvious rival is that **entries name
RECENT rounds** — the arc's own rounds are named constantly while the 200s are not. **Compute the
naming rate as a function of round age**, because if recency explains 18.3% then the register's
failure rate is confounded with when a round was written, and the number means nothing about
registers at all. **This is the same defect I just found, one level up: a share with no floor.**
