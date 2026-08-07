# R1046 — is the number a round ASSERTS the number it MEASURED? ⛔ **Between 16.4% and 27.2% are not in its own artifact — and the first specification I ran said 0.0%.**

**The decision this round makes safe:** whether READMEs need the anchoring discipline that guards
`DEFINITION.md`. **They do** — and the arc has run 24 rounds without it.

## ⛔ The specification curve is the finding, because two cells give OPPOSITE verdicts

| cell — what counts as an assertion | rounds contributing | numbers | unbacked | share |
|---|---:|---:|---:|---:|
| **h1** — the first heading line only | **4 of 24** | **7** | **0** | **0.000** → World A |
| **body** — every number in the README | **24 of 24** | **1064** | **289** | **0.272** → World B |

⭐ **I built the h1 cell first and it would have carried a world verdict off 7 numbers.** Its positive
and negative controls both passed — they test the **containment rule**, and never ask whether the
population is the one the claim is about. **§4's search-instrument row, with the positive control
already in place:** *a control asks "can this instrument see?" and never "is what it sees the thing I
am about to claim about?"* The instrument's unit was **first heading line**; the claim's unit is
**numbers this round asserts**. They are not equal, and 20 of 24 rounds contributed nothing.

## The bracket, and why the lower end is the real number

Splitting the **289** unbacked numbers by whether they appear in **any** round's artifact in this arc:

- **114** do — plausibly **quoted from an earlier round**, which is correct practice, not a defect.
- **175** appear in **no artifact in this arc at all**.

⭐ **`[0.164, 0.272]`** — and **the lower end is the one citation cannot explain away.** Both ends are
reported; **neither is a point**, because no rule available here separates a legitimate quote from a
true miss. **Even 0.164 clears the pre-registered World B threshold of 0.25… it does not** — but it
sits far above World A's 0.10, so **World B holds at the upper end and the lower end is in neither
band**. The honest reading: *between a sixth and a quarter*, and the design cannot narrow it further.

## Controls

- **POSITIVE** — a value drawn **at runtime** from each round's own artifact must read as backed, in
  all **24**: **True**. Drawn at runtime so it cannot be satisfied by a rule that returns "backed" for
  everything — the NEGATIVE shares the same machinery.
- **NEGATIVE** — that same value plus a large offset must read as **unbacked** everywhere: **True**.
- **PLACEBO** — a README with no numbers contributes no denominator: excluded, not scored 0.
- **EMPTY POPULATION** — exit **2**, never 0.
- **MULTIPLICITY** — both cells reported with their populations, not only the one that fired.
- **ROUND IDS EXCLUDED** — `R1044` is an address, not a measurement; stripped lexically before
  counting.

## What this round cannot say

Whether an unbacked number is **wrong**. Absence from the artifact means the sentence is **not
re-derivable from the round's own persisted output** — not that the value is false.

## IMPOSSIBLE here

- **separating a quote from a miss** — needs a citation field the READMEs do not carry.
  **SETTLES: IN-RELEASE** — each of the 175 is resolvable by reading the round it refers to, at one
  reading per miss; unattempted, not unavailable.

`run.py` · `results/headline_backing.json`
