# R1008 · the unwired signature predicts — in the 11% of cases where anything can be decided

**THE DECISION THIS MAKES SAFE.** Whether the gate built last round detects a real failure or a style
smell. **It detects — and the honest statement leads with its denominator: the classifier can decide
only 6 of 53 cases, and in all 6 the machinery was never wired.**

---

## The result, with the bound first

```
53 unwired constants over 47 rounds
    UNDECIDABLE     47   (89%)   ← the classifier cannot say
    NOT-PERFORMED    6   (11%)
    PERFORMED        0
```

⚠⚠ **"6 of 6" is a share whose denominator is 11% of the population.** Reporting *"the signature is
100% precise"* would be the failure this standard names — a number quoted without the scope over
which it holds. **What is established: where the method can decide, it has never once found the role
performed by other means.** Where it cannot decide — 89% — nothing is established at all.

**Why so much is undecidable:** the method needs a plain numeric constant to search for as a loop
bound. `SEEDS = [0, 1, 2, 3, 4]` is a list; `DOSES = GRID["prompt"]` is an expression. Neither can be
matched this way, and folding them into either arm would manufacture a precision.

## The three candidates published last round

| round | constant | verdict | why |
|---|---|---|---|
| R243 | `SEEDS` | **UNDECIDABLE** | a list, not a plain number |
| **R267** | **`DRAWS`** | **NOT-PERFORMED** | **no loop in the file runs `range(20)`** |
| R273 | `DOSES` | **UNDECIDABLE** | an expression, not a plain number |

⭐ **One of three is mechanically confirmed; two are beyond this method.** That is a better outcome
than either "all three are real" or "all three are noise", and it is the reason they were published
as candidates rather than verdicts.

## ⛔ The positive control caught my classifier before it produced a number

The first version searched for the constant's value **anywhere in the file**. It classified R1005's
`NSHUF = 200` as **PERFORMED** — because `200` appears at line 117 in
`if np.isfinite(sc).sum() >= 200`, a **minimum-prompt threshold** with nothing to do with shuffles.

> **The instrument's unit was "any occurrence of the number". The claim's unit is "a loop that runs
> that many times."**

That is the standard's own remedy — *name the instrument's unit and the claim's unit as two separate
strings and require them to be equal, before the control is even designed*. Corrected: the literal
must be an argument to `range()`, which is what a draw, shuffle or replicate count **is** in this
repo's idiom. **R1005 then classifies NOT-PERFORMED, and the round was allowed to proceed.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | R1005's `NSHUF` must classify **NOT-PERFORMED** — R1007 established the shuffles never ran. **Failed on v1, passed on v2** |
| **NEGATIVE** | a value appearing as a `range()` bound more than 6 times is **ambient**; a match there proves nothing, so it returns UNDECIDABLE. Without it the search would clear rounds by coincidence |
| **PLACEBO** | a wired constant is never classified — the population is read from the gate's own artifact, so the two rounds cannot drift apart |
| **NOISE FLOOR** | **n/a**, labelled: this is a classification over a fixed finite population, not an estimate with sampling error. The relevant uncertainty is the UNDECIDABLE share, reported above as the bound |

## ⚠ Impossible here, with what it would require

**Ground truth for all 47.** Establishing that a control never ran takes a round each — **R1005
needed R1007**. Only R1005 has one. So the number above is precision against a **mechanical proxy for
performance**, not against adjudicated truth. **It bounds the gate; it is not a verdict on the 47
rounds**, and none of them is corrected on this evidence.

## Alternatives considered

**Report "the signature is 100% precise".** Refused — the denominator is 11% of the population, and a
share without its scope is eleven of twelve retractions in this project's own history.

**Fold UNDECIDABLE into PERFORMED (the conservative-looking choice).** Refused: it manufactures a low
precision as surely as the other fold manufactures a high one. **An unavailability claim in the
flattering direction is still an unavailability claim** — and here "flattering" would mean flattering
my own scepticism, which is the same error wearing modesty.

**Register this in `DEFINITION.md`.** Refused: the currency gate exists so *measured facts about the
definition* reach the statement. This is a fact about instrumentation. Registering it would put noise
in the one document that has to stay about cores.
