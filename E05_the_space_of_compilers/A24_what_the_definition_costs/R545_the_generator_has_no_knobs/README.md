# R545 · The generator has no knobs — row 3 needs a code change, not a flag

**Decision this makes safe:** what register row 3 actually costs, stated in the right units.

**Estimand:** the flags of `generate_core.py` that alter *what* is generated for a fixed prompt.
**Instrument:** its `argparse` surface, read from source. **This is a reading, not a run.**

| flag | line | what it varies |
|---|---|---|
| `--out` | 77 | where to write |
| `--sham` | 78 | the misdirection arm — a poison, not a variant *(R535)* |
| `--limit` | 80 | how many prompts |
| `--batch` | 81 | throughput only |
| `--corpus` · `--second-path` · `--convs` · `--seed` | 89–92 | **which** prompts |

⛔ **There is no `--model` flag and no prompt flag. `FEWSHOT` is a module constant at line 42.**

⭐⭐⭐ **So no flag varies the output on a fixed prompt, and `do_sample=False` removes the only
other source *(R544)*. `gen` is the UNIQUE output of this generator on the home release — no
second `gen`-like arm is reachable by any flag combination.**

## What it changes in the register

Row 3's cost reads **"a generation round, on this site."** Corrected: **a code change — a new
`FEWSHOT`, or a `--model` flag that does not exist — and then a generation round.** Still on-site,
still 4.63 min of compute, but **a different kind of work**, and the register's purpose is to say
what a row would *require*.

⚠ **Not forced.** The file could have exposed `--model`; it does not. That is a **measurement of
the code**, not an arithmetic consequence.

⭐ **Two rounds, one direction:** R544 showed a re-run is worthless (greedy), R545 shows no flag
helps either. **Together they convert row 3 from "cheap compute" to "cheap compute after an edit."**
