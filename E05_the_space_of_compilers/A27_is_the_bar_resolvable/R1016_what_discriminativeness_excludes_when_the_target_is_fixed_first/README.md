# R1016 · discriminativeness measures belonging, not merit

**THE DECISION THIS MAKES SAFE.** What R1015's candidate can and cannot be a clause about. **It
detects criteria that came from another prompt. It does not rank criterion quality.**

---

## The pre-registration

R1015's candidate was post-hoc — chosen after `topw` was named as the rival. This round fixes the
quantity **first** and names the sets it should separate **without mentioning `topw` or
`coval_core`**:

| LOW set | why it is named, from the release's construction | prediction |
|---|---|---|
| every `*_sham` | criteria pointed at the **wrong** prompt | should rank low |
| every `random_k*` | criteria drawn at **random** from the pool | should rank low |
| everything else | — | **no prediction** ⚠ including the arms R1015 compared |

## The result — a split

| set | below the rest's median (0.025619) |
|---|---|
| shams | **5 / 5 (100%)** |
| `random_k*` | **18 / 38 (47%)** — chance |

**And every sham resolvably below its own parent:**

| sham | parent | Δ (parent − sham) | lo |
|---|---|---:|---:|
| `coval_core_sham` | `coval_core` | +0.013993 | +0.012825 |
| `promptecho_sham` | `promptecho` | +0.011653 | +0.010892 |
| `full_sham` | `full` | +0.010842 | +0.010095 |
| `topw_k4_sham` | `topw_k4` | +0.010233 | +0.009179 |
| `gen_sham` | `gen` | +0.006752 | +0.005610 |

**5 of 5 resolvable.**

## ⛔ The refuted half is the informative one

Criteria drawn **at random from this prompt's own pool** are as discriminative as anything else. The
quantity falls **only** when the criteria come from *another* prompt.

> **So it measures BELONGING, not merit.**

That bounds what any clause built on it could ever claim — and **it was invisible from R1015's
comparison alone**, which only ever contrasted arms that were all on the right prompt.

## ⚠ My verdict string was not a computation

The first run printed *"the LOW sets do not sit below (shams 5/5, random 18/38)"* — **self-
contradictory**, because 5/5 *is* sitting below. The branch collapsed two pre-registered predictions
into one sentence and then described both with the text of the failing one. Each prediction now
carries its own verdict and the world is composed from them, so no clause of the sentence can be true
of a set it is not about.

## Controls

| control | result |
|---|---|
| **POSITIVE** | core − its sham reproduces R1015's **+0.013993** to 1e-6 — this is the same quantity |
| **NEGATIVE** | an arm against itself: exactly **0** |
| **PLACEBO** | deterministic pair: exactly **0**, interval width **0.00000000** |
| **NOISE FLOOR** | that placebo width, measured on a known-zero effect in the same design |

## ⚠ What this does not show

**That the excluded objects should be excluded in any absolute sense.** The LOW sets are named from
the release's own construction — a sham is misdirected *by definition*, a random draw is random *by
definition*. That is the closest thing to a reason available without an external standard, and it is
weaker than one.

## Alternatives considered

**Read 5/5 on shams as vindicating R1015.** Refused: the pre-registration had two halves and one
failed. Reporting the passing half as the result is the multiplicity failure with manners, applied to
predictions instead of cells.

**Drop the `random_k*` prediction as ill-chosen.** Refused — it was named before the run, from the
release's construction, and dropping a pre-registered prediction because it failed is what
pre-registration exists to prevent. Its failure is what produced the round's actual finding.
