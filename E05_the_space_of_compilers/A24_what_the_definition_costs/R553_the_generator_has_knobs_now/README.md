# R553 · The edit rows 3+4 were blocked on, made and tested

**Decision this makes safe:** whether the on-site register rows are reachable.

**WORLD B — the flags reach the call sites and the default path is unchanged.** The edit is
**12 insertions, 3 deletions** in `corebench/generate_core.py`. *"Small enough"* is now a number,
after being an unmeasured quantifier in my own closing line *(check #153)*.

| control | result |
|---|---|
| **NEGATIVE** — an invented flag rejected by argparse (exit 2) | **PASS** |
| **PLACEBO** — unflagged run loads **exactly** `MODEL` at both load sites | **PASS** |
| **PLACEBO** — unflagged prompt starts with **exactly** `FEWSHOT` | **PASS** |
| **POSITIVE** — `--model <sentinel>` reaches every load site | **PASS** |
| **POSITIVE** — `--fewshot-file` replaces the prefix | **PASS** |

**The placebo is the binding one.** An edit that adds a knob and silently moves the default would
invalidate every generation result already on disk. **Exact equality was required, not similarity.**

⭐⭐⭐ **And R552's kill — proven fireable by *simulation* last round — fired for real.** Re-running
it unchanged now returns **`row 3+4 … compute-bound: True` → WORLD A**, because the blocker it was
measuring is gone. **A pre-registered kill that later fires on reality is the only evidence that the
simulation was honest.**

⚠ **Scope: no generation was run.** This tests that the knobs reach the loader, not that a different
checkpoint produces a better core. That is now a compute question — **the first on-site register row
for which that is true.**

## ⚠ A stub that broke an unrelated module
The first harness stubbed `torch` with a `SimpleNamespace` lacking `inference_mode`, which
`covalx/judge.py` uses at **class-definition time**. The failure surfaced as a traceback inside the
code under test. **Fixed by using real `torch`** — it touches no GPU by itself, and the sentinel
fires at tokenisation before any `.to("cuda")`.
