# R1067 — is the clause itself inside the anchoring gate's coverage? ⛔⛔⛔ **No. 0 of 121 clause constants are noticed. `anchoring GREEN` has never said anything about the clause.**

**The decision this round makes safe:** how to read `anchoring GREEN` on every commit in this window.
**As saying nothing whatever about the definition.**

## Result

| | |
|---|---:|
| clause homes (`resolvably beats`) | **9** |
| numeric constants inside their windows | **121** |
| **mutated one at a time — noticed by the gate** | **0** |
| a value R1066 established as anchored, mutated | **RED** |

R1066 showed the gate **is** artifact-coupled. R1044 showed it covers **2.7–7.8%** of the document.
**Those two facts left the worst case open, and this is it:** the gate is perfectly coupled **to
values that are not the definition**, while the sentence this entire arc exists to defend sits in the
uncovered remainder.

## Controls — and the design is worthless without the positive one

- **NEGATIVE** — unmutated document is **green**.
- ⭐ **POSITIVE** — a value R1066 established as anchored **reds** when mutated. **Without this, 0 of
  121 would be silence rather than coverage** — exactly the *"a zero from an instrument never shown to
  return non-zero"* failure.
- **SHAM** — mutating a **word** (not a number) inside the clause does **not** red. So the result is
  *"these values are unguarded"*, not *"any edit to this region is ignored"*.
- **PLACEBO** — restore reproduces the baseline.
- **MULTIPLICITY** — all 121 constants mutated individually and reported, not a sample.
- **SAFETY** — the document is restored after every single mutation and in a `finally`; worktree
  verified clean.

## ⛔ What this does and does not license

⭐ **Coverage is not correctness.** This measures what the gate would **notice**, never what is true.
**An unguarded constant is not thereby wrong** — it is unguarded, which is a statement about the
instrument and a licence the instrument does not grant.

But the reading of the commit record changes completely: **every `all gates green` in this window
meant** *the expected strings are present* (currency, R1065) **and** *some values elsewhere in the
document still match their artifacts* (anchoring, R1066) — **and never** *the clause is anchored*.

## IMPOSSIBLE here

- **whether any unguarded clause constant is wrong** — **SETTLES: IN-RELEASE**, via each constant's
  own round, which is where it was measured; this round only says the gate would not catch a change.

`run.py` · `results/clause_coverage.json`
