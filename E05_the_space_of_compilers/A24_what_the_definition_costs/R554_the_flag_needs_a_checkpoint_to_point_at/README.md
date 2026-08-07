# R554 · The flag has something to point at — and it is not the one anybody named

**Decision this makes safe:** whether last round's register move (rows 3+4 → compute-bound) is real.

**WORLD A. 2 checkpoints are complete, larger than the incumbent, and fit in 16 GB bf16.**

| checkpoint | shards | GB | complete | larger | fits bf16 |
|---|---|---|---|---|---|
| `judge_llama31_8b` | 4 | 16.06 | ✔ | ✔ | ✘ |
| `Qwen2.5-7B-Instruct` | 4 | 15.23 | ✔ | ✔ | **✘** — confirms row 2's OOM |
| ⭐⭐⭐ **`Qwen/Qwen3.5-4B`** | 2 | **9.32** | ✔ | ✔ | **✔** |
| `judge_phi35_mini` | 2 | 7.64 | ✔ | ✔ | ✔ |

⭐⭐⭐ **`Qwen3.5-4B` is the result.** Same family as the incumbent `Qwen3.5-2B-Base`, **2× the
parameters**, complete, and inside VRAM. **It is not in any inventory I hold** — the environment note
lists 2B, 0.8B and a *partial* 9B and does not mention a 4B at all. **So rows 3+4 are independently
compute-bound, and last round's register move was right for a reason I had not checked when I made
it.**

## ⚠ Three defects in my own instrument, each caught by reading its output

1. **The first scan covered ONE store** and its positive control **passed** — the incumbent lives
   there. It returned 0 stronger checkpoints and would have concluded **WORLD B** from a blind
   instrument. Instrument unit: *"top-level dirs of one store."* Claim unit: *"checkpoints `--model`
   can point at."* **Not equal** — §4's row exactly.
2. **HF snapshots are symlinks into `blobs/`.** A pruned blob leaves a dangling link, so *the
   directory exists* is not *the weights exist*. Now resolved and required.
3. **The de-dup keyed on `p.name`**, which for an HF cache is the **snapshot hash** — so every
   result was named `851bf6e8…`. **A finding named by a hash is not a finding.**

## ⚠ The proxy, stated
**`larger` is not `stronger`.** Size is what this design can measure; strength needs the benchmark
that rows 3+4 are priced for. **Same family + 2× parameters is a defensible proxy and is still a
proxy.**

## Controls
- **Positive** — the incumbent is found and reads COMPLETE. **PASS.**
- **Negative** — an invented model directory reads as absent. **PASS.**
- **Identification** — `fits_bf16` is a **bound** from on-disk size, not a load test.
