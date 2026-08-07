# R1075 — ⛔⛔⛔ **The premise of five rounds is void: the "unstored" values are all stored at full precision, and the cause is a defect R1047 already fixed.**

**The decision this round makes safe:** whether to write anything back. **No** — there is nothing to
write; the values are on disk.

## The retraction

R1070 declared 31 clause decimals **"stored by no round"** using an **exact float comparison**. They
are stored — at full precision:

| clause value | exact match | **stored as** |
|---|---|---|
| `0.559311` | **False** | `0.5593110791885862` |
| `0.551354` | **False** | `0.5513543391990778` |
| `0.009103` | **False** | `0.009102604212460431` |

**3 of 3 checked are stored.** The statement prints a **rounded display value**; the artifact stores
the **full one**; exact matching finds nothing.

⛔ **This kills R1070's `31 unstored`, and with it R1071 (`recording failure`), R1073 (`three gaps`),
R1074 (`3 distinct values`) and this round's own premise.**

## ⭐ The lesson is worth more than the chain it killed

**R1047 found and fixed this exact defect** — display rounding versus stored precision — and wrote
`has_rounded()` for it. **R1070 wrote a fresh exact `has()` instead of reusing it.**

> **A fix that lives inside one round's script does not propagate.**

Five rounds inherited the broken population without re-deriving it, and every control in each of them
was correctly aimed at the wrong question. **Not one of those controls could have caught this**,
because each tested the round's own instrument against the round's own population — and the population
was the defect.

## How it was caught

**Not by a control.** By the **currency gate going green when it should have gone red**: my registered
pattern `0.559311.{0,80}0.551354` matched a table in `DEFINITION.md` reading
`0.5593110792 … 0.5513543392` — **longer values, in the document, that my six-digit tokens were
truncations of.** The coincidental match was the evidence.

## What survives

The origin classification is **internally sound** and its controls fired:

| value | round | position (R1074) | **origin (this round)** |
|---|---|---|---|
| `0.009103` | R981 | incidental | CONSUMED |
| `0.559311` | R1000 | candidate | PRODUCED |
| `0.551354` | R782 | candidate | PRODUCED |

⭐ **Two independent instruments agreed** — position-in-README and literal-in-source. That convergence
is real. **It answers a question that no longer needs asking.**

## Controls (of the origin test, which stands)

- **POSITIVE** — a known hardcoded constant detected in its own source (R923 `NBOOT=8000`): **True**.
- **NEGATIVE** — a computed, f-string-printed value absent from source (R1074's `0.667`): **True**.
- **PLACEBO** — a round with no `run.py` yields `NO_SOURCE`, never an assumption.

## IMPOSSIBLE here

- **recovering what R1070–R1074 would have concluded on the correct population** — they must be re-run,
  not reinterpreted. **SETTLES: IN-RELEASE**, at one re-run each.

`run.py` · `results/produced_or_consumed.json`
