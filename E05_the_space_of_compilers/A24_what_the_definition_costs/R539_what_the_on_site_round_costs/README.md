# R539 · The on-site round costs 16,440 model calls — so cost is not the reason not to run it

**Decision this makes safe:** whether "why not spend register rows 3 and 4" has a cost answer.

**Estimand:** the LLM calls a rows-3/4 round requires, split into generation and judging.
⭐ **Measured, not estimated: `gen` already exists**, so a generation round has been run on this
site and its work is readable from the artifact.

| arm | cells | prompts | per-prompt median [min, max] |
|---|---|---|---|
| `gen` | 15,472 | 968 | 16 [4, 16] |
| `topw_k4` | 15,488 | 968 | 16 [16, 16] |
| `full` | 59,936 | 968 | 60 [16, 156] |
| `coval_core` | 15,312 | 968 | 16 [8, 16] |

## The price

| component | calls |
|---|---|
| generation — one criterion set per prompt | **968** |
| judging — 16 satisfaction cells per prompt | **15,472** |
| **TOTAL** | **16,440** |

⭐⭐⭐ **WORLD A: 15,472 judge cells is comfortably within one local-model session. Cost cannot be
the reason not to run rows 3 and 4.**

## Controls
- **Positive** — the counter must be reading judge cells: `topw_k4` must give exactly **k × 4 = 16**
  per prompt. **16.** PASS.
- **Negative** — `full` keeps every criterion, so it must exceed any k-limited arm: **60 > 16.**
  PASS. An inverted ordering would mean the counter reads something else.
- **No noise floor** — exact counts.

## ⚠ What is NOT measured, and is not guessed

**Wall-clock and money.** Converting 16,440 calls to time needs a measured tokens/sec for the
specific local model on this GPU, through pueue. **That is the one number a "why not" would have to
cite, and this round does not invent it.**

⭐ **A detail worth carrying:** `coval_core` ranges **[8, 16]** cells per prompt and `gen` **[4, 16]**
— consistent with the dataset card's *"most prompts end up with four core rubric items (about 95%),
with the remainder having two or three."* The artifact and the card agree without being asked to.
