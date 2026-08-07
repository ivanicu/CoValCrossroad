# R538 · The released core has no second judging — and the first wall of this session to survive

**Decision this makes safe:** whether R537's named gap is real, and whether a stronger judge is
genuinely unavailable.

## ⭐⭐⭐ The wall survives — and that matters more than another demolition

Six times this session a closing line raised a wall — *"needs a scoring run"*, *"needs new
computation"*, *"only whatever produced them could say"*, *"needs an install"* — and **six times the
data was already on disk.** That pattern was becoming a narrative, and §4 warns explicitly against
over-correcting into the opposite story.

**This one holds.** Artifacts from a judge stronger than the home 2B: **`*_7b*` → 0, `*qwen*` → 0.**

| family | artifacts |
|---|---|
| 2B (`sat_*`) | 101 |
| 0.8B judging (`sat08_*`) | 13 |
| 0.8B arms (`*_08b`) | 32 |
| **7B / qwen-tagged** | **0** |

**So "my walls are false" was a tendency, not a law** — and the only way to know which is to check
each one rather than to assume the pattern.

## And `coval_core_2bA` is not a second judging

R524 placed `coval_core_2b{A,B}` in a duplicate class **not containing** `coval_core`, with *"no
documented prediction either way."* That looked like a candidate second judging of the released core.

| | |
|---|---|
| `coval_core_2bA` | 200 prompts |
| `coval_core` | 968 prompts |
| shared | 200 |
| ⭐ **shared prompts whose cells differ** | **0 of 200** |

**It is the SAME judging on a 200-prompt subsample.** Its distinctness from `coval_core` is purely
the population, and its identity to `_2bB` is **the correct outcome for a deterministic judge run
twice** — which resolves R524's undocumented class.

⭐ **So R537's gap is real: the released core is the one admitted arm whose cross-judge position
cannot be replicated from anything on disk.**

## Controls
- **Positive** — the comparison must be able to find differences: `coval_core` vs its **sham** on
  the same 200 shared prompts differs on **200 of 200.** PASS. Without it, "0 differ" is silence.
- **Negative** — `coval_core` against itself: **0 differ.** PASS, so the comparison manufactures
  neither agreement nor disagreement.
- **No noise floor** — exact cell equality.

**Impossible here, and now checked rather than assumed:** a judge stronger than the home 2B.
`Qwen2.5-7B-Instruct` is named in the register at row 2 as **an install**, and nothing on disk
substitutes for it.
