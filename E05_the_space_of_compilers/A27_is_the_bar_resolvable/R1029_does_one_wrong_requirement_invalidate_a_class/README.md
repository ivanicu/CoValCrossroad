# R1029 — R1028 falsified one requirement string. Does it propagate? ⛔ **The question is not identified.**

**The decision this round makes safe:** whether the register can be audited for whether its
requirements are *right*. **It cannot, as stored** — and the repair is structural, not analytic.

## ⛔ Prior art, and it already contains R1028's proposed NEXT

R1028 closed by proposing a re-score of the register on whether each entry **names** a requirement.
**R472 did exactly that** — 100 entries: `explicit` **35** · `implied` **11** · `none` **54**, with
types tabulated (`a second release / corpus` **17**, `a second judge` 10, `an external gold standard`
6, `a generator` 5, …). **That question is closed and was not re-run.**

R472 measured **presence**. R1027 and R1028 each found a named requirement that is **wrong** — a
different property, and the one this round went after.

## Result — ⛔ **UNVERIFIED on identification.** The estimand fails G1 before power is even asked.

Three instruments, three denominators for *"how many entries name the falsified requirement"*:

| instrument | count |
|---|---:|
| R472's committed type tabulation | **17** |
| this round's token matcher (≥ n−1 tokens) | **9** |
| direct phrase regex on the same texts | **7** |

**The spread is not noise — the requirement TYPE was never stored as a field.** R472 derived its
tabulation with a phrasing classifier and said so in its own README, verbatim:

> *"the instrument's unit is **phrasing**, the claim's unit is **naming a requirement**"*

So **17 is a phrasing count, not a population** — and neither is 9 nor 7. Reporting `affected /
matched` would put a real numerator over an invented denominator.

⭐ **The repair is structural: store the requirement type when the entry is WRITTEN.** A register
whose requirements must be recovered afterwards by a classifier **cannot be audited for whether those
requirements are right** — which is the one audit that decides whether it is a **specification** or a
**list of excuses**.

## ⛔ The numerator stands even though the share does not

At least **4** committed entries — **R450, R451, R453, R464** — name the requirement R1028 falsified
**and** guard a criteria-based check, so **R1028's repair applies to them whatever the true
denominator is**. Plus **1** (R458) naming a quantity the disjoint population actually carries.

**A lower bound is a result; a share over a guessed population is not.**

## Controls

- **POSITIVE** — the classifier must flag a **known** criteria-based sentence (R1028's own line):
  **True**.
- **NEGATIVE (constructed)** — must **not** flag a sentence about annotator agreement alone: **True**.
- **g=0** — on the empty string it must return **neither** class, not a default: **True**.
- **NEGATIVE (discrimination)** — criteria-based share among the falsified requirement **0.44** vs
  **0.28** across all other requirement types: it **discriminates**, so it is not merely reading the
  register's general vocabulary.
- **MULTIPLICITY** — all 7 requirement types reported, not only the falsified one.
- **P6 sound direction** — *mentions criteria ⇒ criteria-based* is what the positive control
  licenses. **The converse is not**, so the `FALSE / runnable` column required its own evidence: the
  field actually existing in the data.

## What this round cannot say

Whether each affected check would **actually run** on the disjoint population. That needs the check
implemented and executed, **one round per entry**. **N/A** — this round's contribution is bounding
the population that would need it, not clearing any of them.

`run.py` · `results/requirement_class.json`
