# R555 · Row 2 named a model where it meant a requirement

**Decision this makes safe:** whether a stronger judge needs an install on this box. **It does not.**

**WORLD B.** `Qwen/Qwen3.5-4B` loads in bf16 and scores 24 real prompts at **8.89 GB peak against
16 GB** — 7 GB of headroom.

| judge | peak VRAM | secs | distinct | mean |
|---|---|---|---|---|
| `Qwen3.5-2B-Base` — home, **positive control** | 4.00 GB | 4.3 | 15 | 0.4038 |
| **`Qwen3.5-4B`** | **8.89 GB** | 21.2 | 16 | 0.4058 |

⭐⭐⭐ **The row's error was categorial.** It asked for *"a second, stronger judge"* and then named
`Qwen2.5-7B-Instruct`, so that model's OOM became the row's blocker. **The requirement is a
property** — stronger than `Qwen3.5-2B-Base` *(`covalx/judge.py:48`)* — and a model satisfying it
was already on disk. **§4's "the definition describes the instance", one level up: a register row
described the instance instead of the requirement.**

⚠ **The register's size was also wrong**: **15.23 GB** measured on every copy, not 29 — an fp32 slip
(7.6B × 4 bytes ≈ 30). At 15.23 the 7B's OOM is *tight*, not hopeless.

## Controls
- **Negative** — a nonexistent checkpoint fails to load, so *"it loaded"* is informative. **PASS.**
- **Positive** — the home 2B judge loads and returns **15 distinct** scores on the same batch;
  a degenerate vector would have made the 4B result meaningless. **PASS.**

⚠ **Scope: `stronger` is a proxy** — 2× parameters, same family. What is shown is that it **loads,
fits, and scores non-degenerately**, not that it judges *better*.

⚠ **My first version guessed the schema and crashed** — `rub` is a dict and `build_prompt` takes
`(criterion, reply)`. Fixed by mirroring `corebench/judge_core.py:66-77`, the canonical call site,
rather than inventing a second way to build the same prompt.
