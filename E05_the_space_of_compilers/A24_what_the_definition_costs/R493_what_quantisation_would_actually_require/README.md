# R493 · What the quantisation route actually requires

⚠ **Action class: CLOSURE.** It prices a capability the register names; it tests nothing about the
definition.

**The decision this made safe.** R492 closed by proposing to judge the 2B at int8 to de-confound the
cross-architecture comparison — *"a fifth of the 7B's cost."* **That prices GPU time, which is the
only resource the round happened to meter.**

| quantisation path | present |
|---|---|
| `bitsandbytes` | **✗** |
| `optimum` | ✗ |
| `auto_gptq` | ✗ |
| `awq` | ✗ |

**Controls:** POSITIVE — the probe finds `accelerate`, `torch`, `transformers`, all present ✓.
NEGATIVE — a nonexistent package reports absent ✓. **So the four ABSENTs are measurements, not
silence.**

**World C: AN ENVIRONMENT CHANGE.** What it would require, in order:

1. install a **compiled CUDA package** (`bitsandbytes`) against **capability (12, 0)** with **torch 2.11.0+cu128**
2. **into the shared `.venv`** that `covalx/judge.py` and every committed `sat_*.npz`'s harness use
3. add a quantisation knob to `covalx.judge.Judge` — it takes `dtype=` only
4. **re-judge the 2B quantised**, or the comparison confounds size, family **and** precision

⭐ **The cost I quoted was the only cost visible from inside R492.** GPU-hours are visible because
pueue meters them; **an install that could break the instrument behind every prior result is invisible
until someone asks what the flag needs.** A cost estimate that counts only the resource the round
happens to meter is not an estimate — it is a receipt for one line item.

⚠ **And it compounds R492's own lesson.** R492 found the fix was a **confound** rather than a
configuration. This finds the confound's fix is an **environment change** rather than an install.
**Two rounds, two layers, and each looked like the last one from where I was standing.**

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R493_what_quantisation_would_actually_require/run.py
