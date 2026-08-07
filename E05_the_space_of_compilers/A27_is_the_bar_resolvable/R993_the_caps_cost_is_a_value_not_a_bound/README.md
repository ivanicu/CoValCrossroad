# R993 · the cap's cost is a value, not a bound — 2 arms, and the control caught my first derivation

**THE DECISION THIS MAKES SAFE.** What closing the size departure costs. **Exactly 2 arms** —
`topw_k6` and `topw_k8` — down from R992's bound of ≤ 4.

---

## The provenance was already in the object

R992 could only bound the cost because clause ③'s provenance is unrecorded for the four arms, and its
NEXT called recording it a small job. **It is smaller still: the generator writes it.**

`corebench/select_core.py:102` — `if a.rule in ("oracle_k","indep_k","greedy_k"):` is the **only**
branch that reads human rankings. `:204` — `tag = f"{a.rule}" + …` writes the rule as the tag's
**prefix**. So the rule is a **generator-written field**, not a name I am parsing, and R984's
objection to name-parsing does not reach it.

| arm | rule | ③ excludes it? |
|---|---|---|
| `greedy_k8_fit1` | greedy | **yes** |
| `indep_k8_fit1` | indep | **yes** |
| `topw_k6` | topw | no |
| `topw_k8` | topw | no |

**Cap's unique cost: 2.** R992's bound of 4 was loose by exactly the two label-consuming arms.

## ⛔ My first derivation was wrong, and R920's committed table refused it

v1 keyed on the **`_fit` marker**: `_fit\d` present ⇒ labels consumed. The control returned **15 of
21**, and every mismatch was the same shape — `oracle_k4`, `greedy_k4_greedy_kA`, `indep_k4_indep_kA`
carry **no `_fit`** and are committed **True**.

**Because `select_core.py:100` reads the human target *"for the ORACLE arm only"* whether or not a
parity was supplied. The `_fit` marker records WHICH parity was fitted, never WHETHER labels were
used.** A marker that co-occurs with the property is not the property.

⭐ **The control could fail in both directions** — R920 commits **10 True and 11 False** — which is
what makes 21 of 21 a pass rather than a coincidence. And it is the second time this session that a
committed table from an earlier round refused a derivation I was about to build on.

## Controls

| control | result |
|---|---|
| **SOURCE** | the guard at `:102` and the tag grammar at `:204` are both verified **present in the file** before anything is derived; absent ⇒ exit 2 |
| **POSITIVE** | reproduces R920's committed labels on **21 of 21**, 10 True / 11 False |
| **PLACEBO** | `full` — which the grammar gives no k and no fit marker — derives False |
| **NOISE FLOOR** | none: a source-level derivation, not an estimate |

## Where the size departure now stands

- **stated** (R991)
- **priced**: closing it excludes **exactly 2** admitted arms, `topw_k6` and `topw_k8`
- **not decided**: whether to close it. That remains authorial, and the price is now a value rather
  than a range, which is the whole point of the round.

## Alternatives considered

**Keep the `_fit` derivation and note the mismatches.** Refused: it is wrong in general — it would
call `oracle_k4`, the benchmark's leakiest arm, label-free — and a derivation that is right on the
four cases I care about and wrong on six others is right by accident.

**Ask R920 to extend its table to all 99.** Unnecessary: the generator's own field covers every arm
it produced, and the 21-arm table is better spent as the control that validated it.
