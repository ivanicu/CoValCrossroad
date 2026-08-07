# R514 · Clause ① is subsumed by clause ②

**Decision this makes safe:** how many independent clauses the definition of "core" actually has.

**Estimand (named before method):** the number of admissible objects satisfying ② and violating ①.
Zero ⇒ ① cannot narrow the extension and is not an independent criterion.
**Population:** the 41 arms of R294's census. **Instrument:** A2 against a scalar bar.
**Baseline:** the two bars themselves. **Regime:** ⚠ **bars aggregated GLOBALLY** — load-bearing.

## Worlds
- **A** · ① is independent and merely unexercised (what the STATEMENT table claimed).
- **B** · ① is **logically subsumed**: `bar₁ < bar₂`, so `a2 > bar₂ ⟹ a2 > bar₁` by transitivity.

**Pre-registered kill:** any arm with `ok2=True, ok1=False` kills B.

## Controls
- **Positive** — the census must contain arms that FAIL ①, else the verdict is degenerate:
  **24 of 41 fail ①. PASS.**
- **Negative** — the bar ordering must hold on **every** arm independently, not the one inspected:
  **41 of 41. PASS.** `bar₁ ∈ [0.4821, 0.4927]`, `bar₂ ∈ [0.5386, 0.5504]` — **disjoint, gap 0.0459.**

## Result
**0 arms satisfy ② and violate ①. World B.**

⛔ **This is a DERIVATION, not a measurement, and is labelled one.** Both clauses have the form
`a2 > bar`; the bars are global scalars on a common statistic and direction; `bar₁ < bar₂` on every
arm. The zero is forced by transitivity of `>`. The 41 arms tested nothing — the algebra did.

**Assumption it rests on:** both bars are *global*. **What would break it:** a **per-prompt** ①,
admitting an arm only if it beats *that conversation's own* random rubric draw. For some
conversations that bar exceeds the global 0.5404, and subsumption fails.

## Consequence for the formulation
**The definition has three independent clauses, not four** — ② ③ ④ — under the current
operationalisation. ① is either **deleted** or **re-operationalised per-prompt**, and the second is
the only version in which it does work.

**Impossible here:** whether ① binds per-prompt. The census stores aggregate contrasts only; it
would require re-scoring all 41 arms against each conversation's own random draw.
