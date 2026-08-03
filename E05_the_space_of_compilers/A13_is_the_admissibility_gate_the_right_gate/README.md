# A13 — table of contents

**28 rounds, R248–R275.** Per P16 this file is a **table of contents only**: the sub-round → what it
asked. Every finding, its interval and its scope live in `E05/FORMULATION.md` and `RETRACTIONS.md`.
**One home per fact** — a number stated twice drifts, and the copy is never the one that gets fixed.

---

## ⚠ THIS DIRECTORY IS THREE ARCS AND SHOULD HAVE BEEN THREE DIRECTORIES

P16: *an arc closes when a **decision becomes safe**, and the count is **discovered, never chosen**.*
By that rule A13 holds **three** closed decisions, and I discovered that by writing this file rather
than by planning it.

| what it should have been | rounds | the decision, and where it closed |
|---|---|---|
| **A13** is the admissibility gate the right gate? | R248–R253 | **Closed at R253**: no. `A_real` predicts recovery no better than the criterion count, so the gate reverted to `C(n,k) ≤ a(m)` — two steps behind where it started. |
| **A14** what does the instrument do to these numbers? | R254–R266 | **Closed at R266**: draw noise is 1/16 of the largest term. Three unrelated axes — label order, batch bf16, `PYTHONHASHSEED` — all say R231's central comparison was never a comparison. |
| **A15** what can this release resolve at all? | R267–R275 | **Closed at R274/R275**: MDE `[0.1250, 0.1250]` ⚠ **for THIS detector only** (R277), every substantive effect 3–30× below it, and the two corrections that produced that number **interact more strongly than either acts alone**. |

**Not restructured, annotated** (L81: annotate, never rewrite; `mv`, never `rm`). Renaming 28
directories late in a long session risks the references in 28 docstrings for a gain that is
navigational only. **The finding is recorded here; the move is a separate action with its own
verification.**

---

## R248–R253 · is the gate the right gate?

| round | what it asked |
|---|---|
| `R248` capacity versus realised alphabet | does the gate's right-hand side predict when recovery fails? |
| `R249` which printed criteria do work | the `representative` field, by exhaustive leave-one-out |
| `R250` can provenance be reconstructed | a dose curve on 298 verbatim ground-truth items |
| `R251` substitution is the dose that can kill | the perturbation deletion could not perform |
| `R252` was it redundancy or the marginal | claim 8 against its strongest confound |
| `R253` is `A_real` just `n` in a costume | **the meta-separator** — does the gate's quantity carry information? |

## R254–R266 · what does the instrument do?

| round | what it asked |
|---|---|
| `R254` targeted substitution · where the real core sits | concentration vs noise, and the crossover |
| `R255` is the redundancy lexical at all | lexis vs discrimination, clustered by prompt |
| `R256` is the rubric rank one | a common factor, against a **measured** null |
| `R257` label-order gauge propagation | R234's `r = 0.77` pushed into four load-bearing claims |
| `R258` size-matched rank one | R256's own gap, at matched subset size |
| `R259` does the rate survive noise | `U(k)` at the release's own rater noise |
| `R260` instrument-noise intervals | resampled batch noise onto every published quantity |
| `R261` hash-seed sweep | 13 of 19 E05 seeds keyed on a string |
| `R262` the floors R261 said it could not reach | two of three needed no GPU; one `grep` said so |
| `R263` the remaining salted rounds | R241's conclusion flips with an environment variable |
| `R264` how often does R241 hold | the flip as a **rate**: 15 of 24 |
| `R265` is R241's control validated by noise | a control that improving the instrument breaks |
| `R266` which noise actually binds | the hierarchy of three error sources on one number |

## R267–R275 · what can this release resolve?

| round | what it asked |
|---|---|
| `R267` what this release can resolve | first MDE attempt — **refused its own reading** |
| `R268` a calibrated detector and the real MDE | α calibrated and held out |
| `R269` a sham that can fail | the void sham, and why the obvious repair is also void |
| `R270` the arc chose the coarser statistic | the human-ranking statistic's floor |
| `R271` the clustering inflation with a number on it | 93,558 rows over 968 clusters |
| `R272` the inflation with a calibration that takes | the check R271 omitted |
| `R273` the inflation as an interval | a point estimate off a grid is a bracket-read |
| `R274` the site MDE at fine resolution | R268's number, at 0.005 and 3000 draws |
| `R275` what a replication can and cannot catch | the 2×2 that prices what R269 held fixed |

---

## The one thing a later reader should take from the shape rather than the contents

⚠ **The first version of this paragraph said "twelve of these 28" and "nine of those". Both were
typed, not counted** — in a file whose whole subject is numbers that were typed rather than counted.

Counted, by a stated rule — *a round is corrective iff its opening docstring block names an earlier
round AND contains a defect word* (`wrong|void|refus|defect|could not|retract|failed|no-op|
impossible|mis-scaled|omitted|inherited|over/understated`):

| | |
|---|---:|
| rounds with a `run.py` | **28** |
| **corrective by that rule** | **24** |
| of those, the earlier round is **also in A13** — same directory, same day | **20** |

**The rule is generous** and I am not hiding that: it counts a round that merely *cites* an earlier
round while using a defect word about something else.

⚠ **I then said "the honest figure is between my typed 12 and this rule's 24". That interval is
also wrong, on both ends.** Sweeping the rule itself — *corrective iff an earlier round-id occurs
within `W` characters of a defect word* — gives a specification curve:

| W | corrective | self (A13) | share of 28 |
|---:|---:|---:|---:|
| 20 | **16** | 12 | 0.57 |
| 40 | 19 | 14 | 0.68 |
| 60 | 21 | 15 | 0.75 |
| 100 | 22 | 16 | 0.79 |
| 200 | 25 | 19 | 0.89 |
| 400 | 27 | 21 | 0.96 |
| 800 | **28** | 24 | **1.00** |
| whole docstring | 28 | 26 | 1.00 |

**The range is 16 to 28 of 28 — 57% to 100% — and at every window ≥ 800 characters it is all of
them.** My lower bound of 12 was too low and my upper bound of 24 was too high.

> **The width is the finding. "How corrective is this arc" has no rule-free answer**, and any single
> number I quote is a statement about the window I chose. That is more honest than the interval I
> gave and much more honest than the point I typed first.

What survives either reading: **the arc is not a sequence of findings with corrections appended. It
is mostly corrections, and the findings are what survived them.** That is the honest description of
what an audit at this severity produces, and it is worth knowing before starting one.

The dependency chain is also visible in the counts: `R268 → R269 → R270 → R271 → R272 → R273 → R274
→ R275`, each opening by naming its predecessor. **Eight rounds to settle one MDE, and the last one
found that fixing two of its defects interacts more strongly than either acts alone.**

---

## ⚠ SCOPE REPAIR 2026-08-03 (R277) — the word `site` in the A15 row was an overshoot

The row above once read **`site MDE [0.1250, 0.1250]`**. Read as written, that forbids quoting any
paired arm comparison anywhere in E05. It does not, and the reason is the scope, not the number:

| | R274's MDE | the paired arm comparisons |
|---|---|---|
| estimand | `g = P(force class agreement)` | paired A2 difference between two arms |
| comparand | a subset-core vs **the full rubric** | an arm vs **human classes** |
| statistic | A1-style exact class agreement | pairwise accuracy over 6 pairs |
| n | 250 prompts | 968 prompts |
| test | one-sample calibrated detector | paired cluster bootstrap |

**Four differences, any one of which breaks the transfer.** The measurement was correct; the noun
was too big. `site` names a property of the release when the number is a property of **one detector
on one statistic at one n** — frontier §2's overshoot, and the variety that propagates hardest
because a hard limit is exactly the kind of sentence nobody re-derives.

The MDE of the paired design is **[0.0100, 0.0200]** (R277), i.e. **6–12× smaller**. That does not
rescue everything: two of the four claims A16 was quoting still sit at or below it. It means the
number that governs a claim has to be measured **for that claim's design**, and A13 never was.
