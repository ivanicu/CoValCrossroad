# R542 · Every modelled figure was wrong; every logged figure held

**Decision this makes safe:** the real wall-clock of one rows-3/4 round, and whether to model or read.

| step | measured | source |
|---|---|---|
| generation | **79 s → 1.32 min** | tasks 602/603, batched |
| judging | **199.3 s → 3.32 min** | task 642 |
| **TOTAL** | **4.63 min** | |

| my estimate | claimed | logged | error |
|---|---|---|---|
| R540 total (decode) | 435.0 min | 4.63 min | **93.9×** |
| R541 generation (batch-1) | 22.0 min | 1.32 min | **16.7×** |

⛔ **`generate_core.py` batches** — `for i in range(0, len(items), a.batch)` — so R541's "batch-1
lower bound" was the wrong regime, exactly as R540's decode was the wrong operation.

## Controls
- **Positive** — replicates agree: `[79, 80]` at **1.3%**, `[157, 157, 158, 159]` at **1.3%**.
- **Negative** — the two clusters are distinct populations (157 > 80 × 1.5), so pooling is wrong.
- **Source read** — the batching loop, quoted.

⭐⭐⭐ **Score across R539–R542: counted-from-artifacts 1/1 · read-from-logs 2/2 · MODELLED 0/2**,
wrong by 17× and 94×. **Three times I reached for a model when a log existed** — logs written by this
project, recording exactly the quantity each estimate was inventing.

**R541 named the remedy — "name the instrument's unit and the claim's unit before converting" — and
it was insufficient: the deeper error was converting at all when the thing had been measured.**
