# R1026 — the certification predicate is the last unexamined input. Does it discriminate?

**The decision this round makes safe:** whether the two-member comparator set — upstream of every
extension figure in this arc — rests on a discriminating test. It does, and **it was not a choice.**

## ⛔ Reading the source corrects a sentence I committed one round ago

R1025's annotation said *"R921 certified 2 comparators **from a larger pool**"*, implying a curatorial
choice among viable alternatives. **R918 computes `fixed` over 96 arms and exactly 2 satisfy it.**
There was no selection: the predicate is a **filter**, and it admitted everything that qualified.
That sentence is **withdrawn and replaced, not annotated beside**.

## ⛔ The witness search is a join of two committed artifacts, and is labelled as one

*"Is any potential comparator both stricter than `generic` and prompt-blind?"* joins R921's
`admitted_counts` to R918's `properties`. **26 of 99** arms are stricter than `generic` (which admits
24). **Prompt-blind among them: 0.**

| of the 26 stricter arms | count |
|---|---:|
| `exact == 1.0` (selection ⊆ *that prompt's* rubric) | **23** |
| `exact < 0.5` | 1 — `coval_core` (0.0010), the instance; cannot be its own comparator |
| untyped | 2 — `coval_core_2bA/B`, the twins |

It **could** have come out otherwise — a stricter prompt-blind arm would have refuted the certified
set — so the join is informative. It consumes no new evidence.

## The measurement: is `exact` discriminating, or an artifact of rubric size?

| k | prompt-blind (global pool) | **SHAM** (a *different* prompt's rubric) | PLACEBO (own rubric) |
|---:|---:|---:|---:|
| 2 | 0.0000 | **0.0000** | 1.0000 |
| 4 | 0.0000 | **0.0000** | 1.0000 |
| 8 | 0.0000 | **0.0000** | 1.0000 |
| 12 | 0.0000 | **0.0000** | 1.0000 |

Binomial SE (worst case, 2904 draws): **±0.0093**. Worst per-seed spread: **0.0000**.

### ⛔ Which of those zeros is forced — most of them

Pool **14,810** criteria vs median rubric **15** → ratio **987:1**. Chance is `(r/|pool|)^k`:

| k | analytic chance | measured |
|---:|---:|---:|
| 2 | 1.03e−06 | 0.0000 |
| 4 | 1.05e−12 | 0.0000 |
| 12 | 1.17e−36 | 0.0000 |

**The prompt-blind row is a DERIVATION once the size ratio is known.** What was genuinely unknown is
**the ratio**, and that is what this round measured.

### ⭐ The SHAM is the cell that could have failed — and it is the real finding

It draws **real** criteria from **another prompt's real** rubric, so shared boilerplate would make it
non-zero. Measured **0.0000**. Directly: the share of adjacent prompt pairs sharing **any** criterion
at all is **0.0000**. **Rubric criteria are prompt-unique across this corpus** — a fact about the
release, not about pool size, and it is what licenses reading `exact` as *prompt-matching* rather than
*"looks like a rubric criterion"*.

## Result — **World A. The predicate discriminates, and the set is complete.**

`exact ≈ 1` marks real prompt-specific consumption. The 2-member set is the **complete population of
prompt-blind arms in the release**, so **the constraint belongs to the RELEASE, not to the
definition** — clause ②′'s satisfiability is hostage to the release containing prompt-blind arms at
all, which is a much sharper statement than "a choice was made".

## Controls

- **POSITIVE ①** — my loader reproduces R918's committed `exact` anchors: `generic` **0.0**,
  `topw_k4` **1.0**: **PASS**. Any loader drift breaks it.
- **POSITIVE ② (ceiling)** — a draw from the prompt's own rubric must return exactly **1.0000** at
  every k, or a low base rate says nothing: **PASS**.
- **SHAM** — the prompt **misdirected**. ⚠ Not a poison here: the ingredient under study **is** the
  prompt-matching, so misdirection is exactly its absence.
- **Empty rubrics** — **0** excluded, counted rather than silently skipped.
- **SEEDS** — 3; spread 0.0000.

## What this cannot say

- ⚠ **Whether a prompt-blind comparator stricter than `generic` could EXIST.** Every arm that would
  bind is ruled out, but **ruling out what was built is not ruling out what is possible.** Building
  and scoring one costs **15,488 judge calls** (R914). **N/A, not planned.**
- ⚠ **`exact` remains a proxy sound in one direction.** `selection ⊆ this prompt's rubric ⇒
  prompt-specific consumption` is what the numbers support. The **converse** is not established here
  — and `fixed`, the predicate actually used, is strictly stronger.
- ⚠ **My first run exited UNRUNNABLE on a hardcoded arc path I had guessed.** There are two `A25_*`
  directories in this tree; the path is now globbed.

`run.py` · `results/certification_predicate.json`
