# R541 · The throughput was measured on the wrong operation — 25.3 min, not 7.25 h

**Decision this makes safe:** the real wall-clock of the on-site round the register calls rows 3/4.

## The defect

R540 measured **decode** throughput (128 new tokens) and converted 16,440 calls to **7.25 h**.
**`judge_core.py` contains no `generate()` call** — it does `Judge(model).score(prompts)` on a
batch, and R417, quoted in that file's own provenance comment, established the judge has **no
stochastic step**. **The instrument's unit was tokens/sec; the claim's unit was judge-calls/sec.**

## ⭐ The project had already measured the right thing, four times

`judge_core.py:117` prints elapsed seconds beside the call count, so completed runs are the
instrument. No modelling needed.

| task | judge calls | seconds | calls/s |
|---|---|---|---|
| 634 | 3,168 | 40.1 | 79.0 |
| 635 | 3,168 | 40.0 | 79.2 |
| 636 | 3,168 | 40.0 | 79.2 |
| **642** | **15,488** | **199.3** | **77.7** |

## Corrected cost of one rows-3/4 round

| step | work | time |
|---|---|---|
| judging | 15,472 calls @ 77.7/s | **3.3 min** |
| generation | 968 × 110 tok @ 80.6 tok/s | **22.0 min** |
| **TOTAL** | | **25.3 min** |

**R540 said 7.25 h. Overstated 17×.**

## Controls
- **Positive** — the three 3,168-call runs are independent replicates and must agree:
  **79.0 / 79.2 / 79.2 calls/s, spread 0.25%.** PASS.
- **Negative** — the 15,488-call run must take proportionally longer, else the number measures
  startup rather than throughput: **4.89× the work took 4.98× the time.** PASS.
- **Source read** — no `generate()` in `judge_core.py`. PASS.

⭐ **R540 is not void.** Its decode figure is the correct instrument for the **generation** half.
**A correct measurement pointed at the wrong operation is not a wrong measurement — it is a wrong
application, and only naming both units catches it.**

**Impossible here:** the generation half under batching. `generate_core.py` decodes at
`max_new_tokens=110` and R540's figure is batch-1, so **22.0 min remains a lower bound**.
