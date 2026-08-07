# R549 · Not one on-site register row is compute-bound

**Decision this makes safe:** what the register's cost column should be measuring.

| on-site requirement | blocker | evidence |
|---|---|---|
| row 2 — offload | **missing flag** | `covalx/judge.py:169` hard-codes `device_map="cuda"`; no `device_map`/`max_memory` in `judge_core.py` |
| row 2 — quantisation | **an install** | `bitsandbytes`/`optimum`/`auto_gptq`/`awq` absent *(R548)* |
| rows 3+4 *(nested, R546)* | **missing flag** | no `--model`; `FEWSHOT` a constant; `do_sample=False` *(R544/R545)* |

**0 of 3 are compute-bound. The register prices all of them in compute.**

⭐⭐⭐ **The asymmetry that explains the session's economics:** `judge_core.py` **does** expose
`--model` — which is exactly why R536's cross-judge replication and R537's dose-curve replication
were **reanalyses rather than edits**. **The flags that already exist decide which questions are
cheap, and the register shows none of that.**

## Controls
- **Positive** — `--model` must be found where it exists, else an absence cannot be reported. **PASS.**
- **Negative** — an invented flag resolves in none of the three files. **PASS.**

⚠ **Scope correction to my own closing line:** it said *"four rows, every one gated by a flag."*
After R546's nesting there are **two** on-site requirements, and **rows 5–7 are not flag-gated** —
they need another site or a decision.

**Impossible here:** whether the edits work once made. That is a run; this is a reading.
