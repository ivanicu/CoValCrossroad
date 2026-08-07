# R1003 · clause ④ has no viable setting as a filter — and the core's margin is smaller than one rule

**THE DECISION THIS MAKES SAFE.** Whether clause ④ can be worded as a **filter** at all. **It cannot
on this release.** At every class setting it is either vacuous or it admits nothing.

---

## Why one ruler was the whole point

Every prior verdict on ④ came from a **different unit system** — R849 on annotator parity halves,
R825/R826 on prompt splits, R847 on 1,078 prompts. **Comparing across them is this arc's recurring
error.** So everything here is rebuilt on **one ruler** (A2, 968 prompts) under **one protocol**
(R825's own: select on the fit half, score on the eval half, 8 splits).

## The grid

| class | bar | ④ admits | conjunction | ④ unique removals | `coval_core` in |
|---|---:|---:|---:|---:|---|
| lexical-394 (R849's class) | 0.481738 | 58 | 9 / 12 | **0 — vacuous** | yes |
| lexical-394 ∪ {witness} | 0.572551 | 14 | **0 — empty** | 9 / 12 | **no** |
| the witness alone (permissive) | 0.572551 | 14 | **0 — empty** | 9 / 12 | **no** |

⭐⭐⭐ **Either it does nothing, or it admits nothing.** And there is no class in between: **row 3 is
row 2**, because once the witness is admitted it *is* the max. That is not a gap in the sweep — it is
what "max over a class" means.

## ⭐ The debt R1002 refused to pay, now legitimate

```
admitting ONE admissible rule:   0.481738  ->  0.572551   = +0.090813
coval_core's margin over R849's class:                       +0.084740
```

⭐⭐ **The released core's entire margin under the only surviving wording is SMALLER than what a
single admissible rule adds to the bar.** That is R1002's closure failure with a magnitude attached,
and it is why *"name the class"* cannot rescue the clause: **the verdict is decided by one membership
decision, not by the object.**

## Controls

| control | result |
|---|---|
| **POSITIVE** (ruler) | `coval_core` A2 = **0.566477**, the exact value R825 compared its bar to — so the imported bar sits on this ruler |
| **POSITIVE** (class) | R849's own selected rule `+mean_word_len+uppercase` returns at **median rank 1 of 394**. My re-implementation picks exactly the rule R849 picked |
| **POSITIVE** (wiring) | R922's cut and count reproduced at 1e-9 |
| **NEGATIVE** | a constant rule lands at **0.139736**, far below the bar — so "the bar is high" means something |
| **PLACEBO** | a one-rule class's max equals that rule |

The KILL was pre-registered on the second of these: had R849's rule not ranked in the top decile, the
re-implementation would not have been scoring what R849 scored and **no number here would have been
admissible**.

## ⚠ Corroboration, not reproduction

B(lexical) here is **0.481738** against R849's committed **0.482016** — agreement to ~3e-4 across
**different split protocols** (prompt split vs annotator parity). ⭐ That is convergent evidence from
a design R849 did not use, which is worth more than a re-run — **and it is not the same measurement**,
so it is not reported as a reproduction.

## ⚠ Impossible here, with what it would require

**A per-split value for the witness.** R826 committed its bar as a mean over splits, not per split, so
the union class's bar is `max` of two **means** and its variance is understated. The **point** value —
the quantity every verdict above uses — is unaffected. It would require R825 persisting its per-split
bars.

**Construct validity — N/A.** This asks which wording is **coherent on this release**, never which one
correctly defines a core.

## What this leaves standing

The only form of ④ not refuted is the one that **makes no universal claim at all**: a **margin
reported with its interval against a declared class**, where the class is stated and the number is a
**lower bound**, not a filter. Every filter reading is now measured and dead.

## Alternatives considered

**Sweep more classes to find one between vacuous and empty.** Refused as incoherent: the bar is a
**max**, so admitting the witness sets the bar to the witness. The two rows are the two ends and there
is no interior.

**Report B(lexical) as a reproduction of R849.** Refused — different protocol. Calling convergence
across designs a reproduction is exactly the cross-unit slide this round exists to stop.
