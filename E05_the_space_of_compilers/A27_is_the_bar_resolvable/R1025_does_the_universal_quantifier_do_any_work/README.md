# R1025 — clause ②′ says "beats **every** comparator". The set has two members. Is `every` irreducible?

**The decision this round makes safe:** how clause ②′ should be worded. On this release it reduces to
**"resolvably beats `generic`"** — the second certified comparator never binds.

## Two things settled before any compute

- **⛔ The cheap version is already answered on disk and is not re-run.** R921 committed *both*
  `survives_all_legitimate` (24) and `admitted_by_at_least_one_legitimate` (28). They differ — about
  `generic`, `generic_reprov`, `greedy_k12_fit1`, `topw_k2` — so the comparators are not
  interchangeable. **Reading that off a committed artifact is a lookup, and a lookup cannot fail.**
  It is prior art; this round starts after it.
- **⛔ R921's own derivation decides what is left to ask.** In its words: *"mean margin(A,C) = mean
  A2(A) − mean A2(C); the second term is the same for every A"*. So the **point-estimate ordering is
  comparator-invariant** — algebra, not measurement. `lo` is a bootstrap percentile, which depends on
  the paired **variance**, and that does depend on `C`.
  ⇒ **The entire content of "every comparator" is which comparator yields the tighter interval.**
  Verified as a falsifier: the invariance holds to a span of **6.9e−17** across 97 arms.

## Result — **World A.** `every` is a shorthand; `generic` is uniformly the binding comparator.

| target | + (`generic` tighter) | − (`pool16` tighter) | resolved flips | median \|Δlo\| | seed-spread floor |
|---|---:|---:|---:|---:|---:|
| `A2` | 0 | **94** | **0** | 0.00911 | 0.00021 |
| `A1·consensus` | 0 | **94** | **0** | 0.00517 | 0.00103 |

`Δlo = lo(A, generic) − lo(A, genericpool16)` is negative for **every** candidate on **both** targets:
`generic` always gives the lower bound, so `min` over comparators always selects it.

⭐ **On this release clause ②′ reduces to `resolvably beats generic`.** The universal quantifier over
a two-member set is notation, not content.

## ⚠ The verdict flipped twice on my own audit — both times a degenerate diagonal wearing a name

1. First run: **2 resolved flips**, `generic` and `generic_reprov` → World B. But `generic` **is a
   comparator**; `lo(generic, generic) ≡ 0` by construction.
2. Second run, comparators excluded: **1 resolved flip**, `generic_reprov` → still World B. But its
   paired sd against `generic` is **exactly 0.0000** on `A1·consensus` — it *is* `generic` on that
   target under another name.
3. Third run, with the exclusion **computed rather than hand-picked** — *an arm is not a candidate
   against `C` on target `T` if its paired sd against `C` is exactly 0 there* — **0 flips → World A.**

**Both false flips would have been reported as evidence that `every` is irreducible.** The rule that
catches them is mechanical and belongs in any future comparison over a population that contains its
own baselines.

## Controls

- **NEGATIVE (the derivation as falsifier)** — mean-margin(A,gen) − mean-margin(A,p16) constant
  across all 97 arms: span **6.939e−17**: **PASS**. Without this the whole reduction is void.
- **POSITIVE ①** — reproduces R921's committed sets exactly: |survives all| **24**, |at least one|
  **28**, same membership: **PASS**.
- **POSITIVE ②** — sign-detection: a synthetic comparator = `generic` + iid mean-matched noise is
  strictly noisier, so it must be uniformly less tight. **g=0 → all 97 signs vanish** (the control
  fails when it should); **g=0.05 and g=0.20 → 0 resolved minority signs**: **PASS**.
  ⚠ **First version scored this by strict one-sidedness and printed FAIL at g=0.05 on a single
  noise-flip (96/1).** That is the *control that cannot PASS* — a threshold above what the design
  returns at a small dose, **and a different statistic from the kill's**. Rescored by the kill's own
  rule.
- **PLACEBO** — `lo(A,generic) − lo(A,generic)` exactly 0 for all 97 arms: **0.0e+00**: **PASS**.
- **SEEDS** — 3; every reported sign stable across all three.

## Bounds on what this can mean

- ⛔ **Algebra, not this measurement, caps the quantifier's meaning.** Whatever the sign test
  returned, `every comparator` can never encode a difference in **which arm is better** — only in
  **how confidently that is known**. That follows from R921's committed invariance.
- ⚠ **The certified set is a CHOICE the clause does not mention.** R921 certified 2 comparators from
  a larger pool; the quantifier inherits its strength from that certification step, not from the word
  *every*. **N/A here:** testing it over comparators never scored costs **15,488 judge calls each**
  (R914) — that is what a third comparator would require.
- ⚠ **Scope:** 94 candidates, this release, these two targets. A third comparator could bind.

`run.py` · `results/quantifier_work.json`
