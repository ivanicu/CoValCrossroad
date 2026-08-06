# R860 · the exact MDE of the universal reading — the last number the quest owed

**Arc A24.** ⭐ **Closed. And it corrects entry 1383's proxy in the unflattering direction.**

## ⛔ THE WALL, NAMED FOUR TIMES AND SHRUNK FOUR TIMES

| entry | what it said | what happened |
|---|---|---|
| **1382** | *"needs the argmax's membership; requires a re-run"* | named as a blocker |
| **1383** | — | margin **bounded to ±0.00025** with no re-run |
| **1384** | — | the 1,820 are the **complete** C(16,4) enumeration; nothing was lost |
| **1385** | — | R331's pool **is** `sat_genericpool16.npz`, its scoring already vectorised — **computable now** |

## ⭐ KILL CHECKS — the load-bearing ones, and they can fail

| check | result |
|---|---|
| recomputed blind max vs R331's committed order statistic | **0.55747530882624 · \|Δ\| = 0.000e+00 · PASS** |
| recomputed `coval_core` vs the committed value | **0.5664774811929549 · \|Δ\| = 0.000e+00 · PASS** |

⚠ **The construction reproduces the two numbers the round is about before computing anything new.**
The argmax's own mean equalling the max is **degenerate by construction** and is **not relied on**.

## ⭐⭐ RESULT

⭐ **ARGMAX subset: `[0, 3, 9, 14]`** — membership never previously committed anywhere.

| | |
|---|---:|
| margin `coval_core` − argmax | **+0.0090021724** |
| **95% CI** | **[+0.0017734642, +0.0163000494]** |
| SE | 0.0036914813 |
| **EXACT MDE** | **0.0103435305** |
| **margin / MDE** | **0.870** |
| CI excludes zero | **YES** |

## ⛔⛔ THE PROXY WAS OPTIMISTIC BY 56%

Entry 1383 borrowed a neighbouring subset's own MDE — **0.0066309665** — and got **1.358**. The real
MDE of this comparison is **0.0103435305**, **1.56× larger**, and the true ratio is **0.870**.

⭐ **1383 wrote that a proxy must not be quoted near a threshold. This measures what that costs: the
proxy moved the ratio across 1.0 and toward the 1.5 bar.**

## ⭐⭐⭐ THE FINAL STATEMENT — it holds two things at once

**The margin is RESOLVABLY POSITIVE**: the CI excludes zero, so `coval_core` **does** clear the
maximum of all 1,820 prompt-blind quadruples. **And it is NOT ADMISSIBLE AS A MAGNITUDE**: at
**0.870×** the design's own MDE, below this project's **1.5×** floor.

**Sign established. Size not.** ⚠ Those are different criteria and both are reported — **reporting
only the CI would overstate it, and reporting only the ratio would understate it.**

## ⚠ WINNER'S CURSE — stated, not corrected

The max over 1,820 is an **extreme order statistic**, biased *up* as an estimate of a typical blind
quadruple. **That makes it a CONSERVATIVE bar for the core** — the direction the universal reading
wants — and it is **not quoted as an estimate of anything else**.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |
