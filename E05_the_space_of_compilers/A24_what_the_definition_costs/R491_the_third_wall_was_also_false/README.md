# R491 · The third wall this session that was false when checked

⚠ **Action class: CLOSURE.** It retracts a register line written one round earlier.

**The decision this made safe.** R490 wrote into the register: *"What would settle ②∧③ is a judge
stronger than Qwen3.5-2B, and **this site has none**."* **That is false.**

| model | present | complete | shards |
|---|---|---|---|
| `Qwen3.5-0.8B-Base` | ✓ | ✓ | 1/1 |
| `Qwen3.5-2B-Base` | ✓ | ✓ | 1/1 |
| `Qwen3.5-9B` (CLAUDE.md says *partial*) | **✗** | — | — |
| **`Qwen2.5-7B-Instruct`** | **✓** | **✓** | **4/4, 29 GB** |

**Controls:** POSITIVE — the search finds the two known judges ✓. NEGATIVE — `Qwen3.5-9B`, which
CLAUDE.md lists as partial, comes back **absent** ✓, so the search does not find everything.

⭐ **And it was the POSITIVE CONTROL, not the estimand, that surfaced the 7B.** My first pass looked
only in the model store; widening the search to satisfy the control found `/home/ivan/Qwen2.5-7B-Instruct`.
**The control did not confirm the instrument — it corrected the question.**

## What it does and does not test

**Qwen2.5-7B-Instruct is a different FAMILY and an INSTRUCT model**; the campaign's judges are Qwen3.5
**Base**. So it tests **cross-architecture**, not scale — a *different* axis from the one the register
asked for, and by the standard's own list a stronger one. **29 GB against 16 GB of VRAM**: it needs
quantisation or offload. **Not free, and not absent.**

⚠ **A weakness in this round's own comparator, stated rather than hidden.** The Qwen3.5 configs do not
carry `hidden_size`, so the automated "larger" test compared `3584 > 0` — **degenerate**. The claim
rests on the parameter counts in the model names (7B vs 2B), corroborated by directory size (29 GB vs
4.3 GB). **A comparison against a missing field is not a comparison**, and it passed here only because
the answer was already known.

## Three walls, one session

| round | the wall | what was actually there |
|---|---|---|
| **R475** | *"③ is not decidable here"* | `data/DATASET_CARD.md`, unopened for 46 rounds |
| **R489** | *"no second release"* | 2,200 conversations, 74,048 judged cells, used since R434 |
| **R491** | *"no stronger judge"* | a complete 29 GB 7B model in `/home/ivan` |

⛔ **Every one was a claim about the SITE asserted immediately after correctly checking the RECORD.**
Door ① sends me to the object; in all three the object was one command away and the sentence went out
anyway. **The pattern is not carelessness about evidence — it is that a register entry reads as
settled, and settled things do not get re-measured.**

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R491_the_third_wall_was_also_false/run.py
