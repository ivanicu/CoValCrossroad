# R443 · ③ as written leaves `coval_core` standing — the extension is **1**, not 0

**The decision this round makes safe:** whether the definition, under its own written clause ③,
admits **nothing at all**. **It does not** — `W-CORE-SURVIVES`, with the identification limit stated
before the number existed.

## ⭐ The source settled half of it mechanically

`corebench/select_core.py:131` computes `w[i] = mean(annotator score)` from
`conversation_rubrics.jsonl`. Exactly **three** selectors consume it:

| selector | key | consumes `w` |
|---|---|---|
| `topw_k` | `-w[i]` | **yes** |
| `topabs_k` | `-abs(w[i])` | **yes** |
| `topwvar_k` | `-(abs(w[i]) * var[i])` | **yes** |
| `topvar_k` | `-var[i]` from satisfaction | **no** — its own comment: *"a property of the responses, never of the human target"* |

**So ③ as written excludes three selectors, not one.** Two were already outside ②'s admit list, so
that alone leaves R442's extension of 1 standing.

## The part the source cannot settle — and the measurement

`coval_core` is not produced by `select_core.py` at all; it ships with the release. So the question
is **provenance**: were its criteria drawn from the annotator-authored rubric?

| | |
|---|---|
| prompts carrying both a `coval_core` and a `coval_full` | **968 of 968** |
| **containment** of `coval_core` in its **own** prompt's rubric | **0.0779** |
| prompts where *every* core criterion appears verbatim | **1 of 968 (0.1%)** |
| **cross-prompt sham** | **0.0000** — exactly |

**92.2% of `coval_core`'s criteria do not appear in its own prompt's rubric.** The text is not drawn
from it, so the containment objection does not reach it, and **the extension under ③ as written
stays at 1**.

⭐ **The 7.8% that *is* contained is real, not noise** — the cross-prompt sham is exactly zero, so no
core criterion appears in *another* prompt's rubric. The overlap is small and **strictly
prompt-specific**. Reported because it is there.

⚠ **UNVERIFIED-leaning by construction, and said so before running.** Containment is **sufficient**
for the provenance objection and **not necessary** — the same annotators could have authored the
core in different words, and this instrument cannot see that. Only a *high* share would have been
decisive.

## Controls

| control | returned |
|---|---|
| POSITIVE — `coval_full` against itself | **1.0000** ✅ |
| PLACEBO — a rubric against itself minus one item | **0.8889**, exactly (n−1)/n ✅ — the matcher is graded, not binary |
| g=0 — an empty criterion list | **0.0000**, no exception ✅ |
| NEGATIVE — cross-prompt sham | **0.0000** — the scale the real number is judged against |

## ⛔ The kill divided by a sham of exactly zero

It was written as a **ratio** (`containment ≥ 3× sham`, `≤ 2× sham`). The sham came back **0.0000**,
so the ratio was `+inf`, which failed `≤ 2.0` and routed a containment of **0.0779** — plainly low —
into `W-PARTIAL`. **The verdict word was defensible and the computation that produced it was not.**

**A ratio to zero is not a scale.** The decision now rests on the **absolute share**, which is what
*"drawn from the rubric"* actually means. And a zero sham is **informative, not a problem**: it is
what makes the 7.8% prompt-specific.

## Impossible here, named

- **authorship rather than textual containment** — requires an annotator field the release does not
  carry for `coval_core`.
- **ruling that `coval_core` is producible from the conversation alone** — low containment is not
  evidence of that, and the identification note said so before the number existed.
- **re-adjudicating R363's derivation about `topw_k`** — it stands or falls on its own.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
