# R1037 — the clause named no parameter. State it, and verify the **stated** form computes.

**The decision this round makes safe:** what the clause a reader implements actually says. It now
carries **q as a declared parameter with its measured onset** — never a fabricated value.

## The gap

`DEFINITION.md:808` and `README.md:65` read *"resolvably beats the certified prompt-blind comparator
set"*. R1034 measured that quantifying over the **closed** set is **vacuous**; R1035/R1036 replaced
the max with a family **quantile** whose onset size grows with q. **None of that was in the clause** —
no q, no family, no closure. A reader implementing the sentence implemented the vacuous form.

## ⛔ §4 decides what the clause may say

> *"A definition that names a number it cannot resolve is how 'four' got in. State the bound the
> design supports, not the value the instance happens to have."*

R1036 found **three** scale-free quantiles (50, 75, 90) and **no evidence selecting among them**. So
the clause carries q as a **declared parameter**, not a value — and **not silence**.

## Result — ⭐ **World A. The stated form computes.**

The literal reading — *"resolvably beats at least q% of the certified prompt-blind family"* —
reproduces R1036's committed grid, **produced by different code in a different round**, at every q:

| q | 0 | 50 | 75 | 90 | 95 | 99 | 100 |
|---|---:|---:|---:|---:|---:|---:|---|
| stated | 73 | 12 | 12 | 11 | 9 | 8 | unstable |
| R1036 | 73 | 12 | 12 | 11 | 9 | 8 | unstable |
| agree | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Controls

- **POSITIVE** — R1036's grid, different code, different round: agreement at **all** q, 3 seeds.
- **NEGATIVE** — R1035's **ill-posed** reading (*"beats the q-th percentile **comparator**"*) run
  across the **whole curve**: it differs at **2 of 7** quantiles — q=0 (**73 vs 24**) and q=100
  (**unstable vs 2**). **They are different rules.**
  ⚠ **My first version compared them at q=90 only, got 11 = 11, and reported the wording as
  under-specified** — while the table showed all seven agreeing. R1025 explains the coincidence: the
  two certified comparators are near-interchangeable in the **point** estimate, so at a mid quantile
  the two readings can land on the same set **without being the same rule**. A control must run where
  the readings *can* differ.
- **PLACEBO** — q=0 imposes no requirement (73 arms); reported and **excluded as degenerate**.

## ⚠ And my verdict fired on the wrong branch — third time this session

The first run branched on `ok_all and neg_ok`; the negative was False, so it printed **World B**,
whose text says *"the literal reading does not reproduce R1036"* — which the table **refuted line by
line**. The verdict is now **computed from the rows**, not from a conjunction of controls.

## What the clause now says, and what it does not

- ⭐ **q is DECLARED, not fixed.** Scale-stability is **necessary, not sufficient** (R1036): q ∈
  {50, 75, 90} are all size-independent and no measurement over this release selects among them.
- ⚠ **q=100 is excluded by measurement, not taste** — R1036 showed the max **never stabilises** in
  family size, so *"beats the whole family"* cannot be stated at any size this release reaches.
- **N/A** — which q is *right* needs an external criterion for what the comparator family
  **represents** (R1028).

`run.py` · `results/stated_form_verifies.json`
