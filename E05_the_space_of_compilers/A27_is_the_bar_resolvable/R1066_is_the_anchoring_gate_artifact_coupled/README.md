# R1066 — the anchoring gate attacked from the ARTIFACT side. ⭐ **It is artifact-coupled. The two gates differ in kind.**

**The decision this round makes safe:** whether R1065's "text-only" finding generalises to the
discipline. **It does not.** It is about **one** gate.

## The intervention

Target: `A24…/R444_clause_three_reconciled/results/r444_decision.json`, key `clause3_excludes_before`.

| cell | mutation | exit |
|---|---|---:|
| baseline | none | **0** |
| POSITIVE | mutate that value in the **document** | **1** |
| **⭐ INTERVENTION** | artifact `4 → 7781`, **statement untouched** | **1 — RED** |
| **SHAM** | add a key the gate asserts nothing about | **0** = baseline |
| PLACEBO | restore everything | **0** = baseline |

⭐ **The intervention/sham pair is what carries the finding.** Mutating one JSON number turns the gate
red while the document is untouched; adding an unasserted key leaves it green. **That is coupling to
that value specifically**, not sensitivity to any file edit.

## ⛔ Two of my own controls were malformed, and both failures were their own

1. **The target resolver looked in the wrong place.** I searched `load(...)` globs under `E05`; the
   gate's globs are **round-directory patterns** (`R427_*`) resolved against arc directories. **The
   round refused to run** rather than reporting "no artifact found" as a result.
2. **The first positive control replaced the first `"4"` anywhere in a 2,400-line document** — an
   arbitrary digit, not the asserted one — and the green it returned said nothing. §4's *control fails
   for its own reasons*. ⚠ **And its repair is blunt, which is stated rather than hidden:** `4` occurs
   **933** times as a standalone number, so mutating all of them proves only that **the gate can
   return red at all**. It does not isolate the asserted occurrence — **the artifact side does that.**

## What this establishes

⭐ **Currency certifies that words were written. Anchoring certifies that the words match a
measurement.** R1065's finding stands and is now **scoped to one gate**, which is a materially
different conclusion from the one that round's own NEXT anticipated.

⚠ And R1044's ceiling still binds: anchoring covers **2.7–7.8%** of the document. **Artifact-coupled
within its coverage** is the whole claim — not *"the statement is anchored."*

## Controls

- **NEGATIVE** — unmutated repository green: **True**.
- **POSITIVE** — document mutation reds: **True**, but **blunt** (see above); it licenses only *the
  gate can fail*.
- **SHAM** — an unasserted key leaves the verdict unchanged: **True**. Without it, the intervention
  result would mean *any edit reds it*.
- **PLACEBO** — full restore reproduces baseline: **True**.
- **SAFETY** — artifact and document both restored in a `finally`; worktree verified clean.

## IMPOSSIBLE here

- **whether a gate SHOULD be artifact-coupled** — intent, not behaviour. **SETTLES: OUT-OF-RELEASE**
  for intent; **IN-RELEASE** for behaviour, measured here.

`run.py` · `results/anchoring_coupling.json`
