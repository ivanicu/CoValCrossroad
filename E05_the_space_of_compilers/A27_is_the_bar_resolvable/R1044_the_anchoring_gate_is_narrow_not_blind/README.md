# R1044 — R1043 called the anchoring gate **blind**. It is **narrow**, it says so, and I never read it.

⛔ **This round retracts the headline of the round committed immediately before it.**

## The two errors, both mine

**① The value I corrupted was not one the gate asserts.** R1043 said *"anchoring passes a corruption
of a value it explicitly asserts"*. `0.0098` is **not inside any assertion span** — it appears in the
gate's *source* and in the document, but its located-assertion set does not cover it. **That sentence
is false.**

**② The gate had been printing its own coverage the whole time.** I read its **exit code** and never
its **output**:

```
bold_any     142 of  1831 numeric claims covered      7.8%
decimal      182 of  5767 numeric claims covered      3.2%
sig2plus     157 of  5333 numeric claims covered      2.9%
all_number   317 of 11647 numeric claims covered      2.7%
⚠ the gate checks 2.7%-7.8% of this document depending on what counts as a claim.
  A PASS certifies the anchored numbers, never the document.
```

**That is door ① — a description instead of the object — inside a round whose entire subject was
whether instruments can be trusted.**

## Result — ⭐ **World A. Narrow but sound.**

| value | covered | rc | reading |
|---|---|---:|---|
| `0.0098` | **False** | 0 | outside the assertion table — **GREEN is correct** |
| `0.034722` | **True** | **1** | inside it — **RED, so the gate detects** |

**Corrupting a covered value turns it RED; an uncovered one stays GREEN.** The gate detects within
its **declared** scope. **R1043's "one of the three commit gates is blind" is withdrawn.**

What stands is the gate's **own published** figure: **343 assertions, 349 located spans, 2.7%–7.8%
document coverage** — *a PASS certifies the anchored numbers, never the document.*

## Controls

- **POSITIVE** — the covered/uncovered split is non-trivial and uses **the gate's own** ASSERTIONS
  regexes to define "covered", so the word is its, not mine.
- **NEGATIVE** — the uncovered mutation **reproduces R1043's GREEN exactly**. That is what makes this
  a **scoping correction rather than a contradiction**: both results are real; they differ in which
  value was touched.
- **PLACEBO** — untouched tree GREEN before either mutation.
- **RESTORE in `finally`**, gate re-run on the restored tree.

## What R1043 got right and still stands

- `attack_the_suite.py` tests the **empty-input floor**, not detection.
- **currency** and **next** do detect, under mutations verified to break what they key on.
- **The mutation is itself an instrument needing its own control** — which is exactly the discipline
  that caught this one.

## What this cannot say

Whether the **92–97%** the gate does **not** cover contains an error. **Coverage is a denominator, not
a verdict on the remainder.**

**SETTLES: IN-RELEASE** — every uncovered number is in `DEFINITION.md` and in some round's committed
artifact, so each is checkable, at the cost of one assertion per number, which is what the gate's 343
entries already are.

`run.py` · `results/narrow_not_blind.json`
