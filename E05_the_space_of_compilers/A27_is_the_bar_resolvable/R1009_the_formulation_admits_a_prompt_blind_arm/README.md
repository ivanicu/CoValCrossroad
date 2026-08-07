# ⛔⛔ CORRECTION BY R1010 — THE MEMBERSHIP FACT AND THE REPAIR WERE BOTH COMMITTED AT R921

> R921's artifact already carries **`admitted_by_at_least_one_legitimate` (28)** and
> **`survives_all_legitimate` (24)**, and their difference is exactly
> `['generic', 'generic_reprov', 'greedy_k12_fit1', 'topw_k2']`. **So both this round's finding
> — that `generic` is admitted — and its repair — quantify over ALL certified comparators —
> were on disk before it ran**, and the repair's name was already the field's name.
> ⭐ **What this round genuinely adds** is narrower and is what should have been claimed:
> the **READING** (R921 framed it as comparator-choice sensitivity; that admitting a
> prompt-blind arm means the definition admits its own null is not in R921), the
> **RESOLVABILITY** of the admission (`lo = +0.0057`) with its self-comparison and sham
> controls, and the repair's **cost at the full ②∧③ conjunction** (9 vs 12) where R921's
> 24/28 are clause-② alone.
> ⚠ The claim *"reading the extension arm by arm turned this up"* stands as a description of
> how I found it and **not** as a claim that it was unknown.

---

# R1009 · the formulation admits an arm that never reads the conversation — and the repair costs three arms

**THE DECISION THIS MAKES SAFE.** Whether clause ②, as written, excludes a criterion set that never
sees the prompt. **It does not.** And the fix is one word, with its cost measured.

---

## ⛔ Why this and not R1008's NEXT

R1008's NEXT asked for AST dataflow. **That would have been the third consecutive instrumentation
round**, while R1007's retraction had moved the object-level state without anyone restating it.
Reading R1000's committed extension arm by arm — the restating — turned this up, and it is not an
instrument question at all.

## The finding

| comparator | prompt-blind arm | Δmean | lo | hi | admitted |
|---|---|---:|---:|---:|---|
| `generic` | `genericpool16` | −0.0091 | −0.0125 | −0.0057 | no |
| **`genericpool16`** | **`generic`** | **+0.0091** | **+0.0057** | +0.0125 | **YES** |

**`lo = +0.0057` — resolvable, not marginal.** R921 certified `generic` as **prompt-blind**; clause ②
is *"resolvably beats a NAMED prompt-blind comparator"*. **Under one certified comparator, the other
qualifies as a core.**

## ⭐ The mechanism

The two certified comparators are **not of equal strength** — `generic` resolvably beats
`genericpool16`. The clause says *"a NAMED prompt-blind comparator"* and **never says which**, so
naming the weaker one lets the stronger one through.

> **The standard's own test for a clause is: name an admissible object it EXCLUDES.**
> Clause ② excludes 68–72 arms and does **not** exclude the comparator it is defined against.

## ⭐ The repair, with its cost measured

> **②′** it resolvably beats **EVERY** comparator in the certified prompt-blind set — not *a* named one.

| | |
|---|---:|
| extension under `generic` alone | 9 |
| extension under `genericpool16` alone | 12 |
| **②′ — the intersection** | **9** |
| `coval_core` survives | **yes** |
| `generic`, `generic_reprov` excluded | **yes** |
| only other loss | `topw_k2` |

⚠ The intersection equals `generic`'s extension exactly — so **`generic`'s extension is contained in
`genericpool16`'s**. **Measured, not derived:** resolvable beats are not transitive in general, so
that containment is a fact about this release and not a theorem.

## Controls

| control | result |
|---|---|
| **POSITIVE** | R922's cut and count reproduced at 1e-9 |
| **POSITIVE** | `coval_core` admitted under both comparators, as R1000 established |
| **NEGATIVE** | **an arm is never admitted against itself** — the paired difference is identically zero, so `lo > 0` is False. Without this every count here would be void |
| **PLACEBO** | `topw_k4_sham`, the same operation with the ingredient **inverted**, is excluded under both. A definition that admits the sham has no content |

**Noise floor:** the 2.5th percentile of the bootstrapped paired difference **is** the resolution
here — admission is `lo > 0`, so marginality is read straight off `lo` and reported rather than
assumed.

## ⚠ What this does not say

**That the release intends `generic` to be a candidate arm.** R921 certified it as a **comparator**;
nothing in the release says it may not also be scored, and the definition as written places no
restriction. **The silence is the defect** — and ②′ removes it without appealing to intent.

## Alternatives considered

**Rule `generic` out by fiat — "comparators are not candidates".** Refused: that is a restriction the
release does not state, so adopting it would be describing the instance again rather than defining
the category. ②′ achieves the same exclusion from the clause's own logic.

**Report the defect and defer the repair.** Refused, and the kill was pre-registered against it: a
definition that admits its own null is not a finding to schedule.
