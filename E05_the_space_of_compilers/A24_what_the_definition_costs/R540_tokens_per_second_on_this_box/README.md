# R540 · Decode throughput on this box — ⚠ correctly measured, wrongly applied

**Measured via pueue on the two sizes that ARE the campaign's judges** (`sat_*` is 2B, `sat08_*`
is 0.8B):

| model | tok/s | reps | spread |
|---|---|---|---|
| 0.8B | **89.2** | 88.2 / 90.3 | 2.4% |
| 2B | **80.6** | 81.4 / 79.8 | 2.0% |

**Controls.** Positive: 2B slower than 0.8B — else it is not measuring decode. Negative: repeats
within 20% at both sizes. Both PASS. ⚠ batch-1 `transformers`, `vllm` absent — a **lower bound**.

## ⛔ This round's conversion to wall-clock is WRONG, and R541 corrects it

It multiplied **16,440 calls × 128 tokens** to get 7.25 h. **The judging step does not decode** —
`judge_core.py` calls `Judge(model).score(prompts)` on a batch and contains no `generate()`.
**Overstated 17×; the true figure is 25.3 min** *(R541)*.

⭐ **The measurement itself stands.** It is the right instrument for the **generation** half, which
does decode at `max_new_tokens=110`. **It was applied to the wrong half.**

**Verified before running, not assumed:** the model store holds `Qwen3.5-0.8B-Base` and
`Qwen3.5-2B-Base`; `torch` + `transformers` are in this venv (`vllm` is not); the 5080 sat at
791/16303 MiB; `gpu-run` is on PATH.
