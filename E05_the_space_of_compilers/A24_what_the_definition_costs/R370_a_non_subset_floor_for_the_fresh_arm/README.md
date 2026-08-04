# R370 — against a floor that is not a subset of its own target, the transport contrast collapses

**The decision this makes safe:** *is transport a candidate clause for the definition?* **No.** It is
a **stated limit.** R368 measured the floor's construction.

## Result — `W_COLLAPSES`. All three controls PASS. Two runs byte-identical.

⏱ **The kill was pre-registered and committed while pueue task 630 was still judging** — before
`sat_genericpool16_fresh.npz` existed or could be read. That ordering is the only thing that makes
it a commitment rather than a description.

| floor | metric | contrast | own MDE | verdict |
|---|---|---:|---:|---|
| **full** *(R368's subset floor)* | exact | +0.0992 | 0.0654 | **resolved +** |
| **full** | pair | +0.0612 | 0.0535 | **resolved +** |
| **pool** *(non-subset)* | exact | **+0.0810** | **0.0920** | **inside the MDE** |
| **pool** | pair | **+0.0161** | **0.0251** | **inside the MDE** |

**Both metrics agree** — no metric split, so the fourth branch did not fire.

## The subset advantage, measured directly

The floor levels are the cleanest thing here. On the original arm:

| metric | subset floor | non-subset floor | advantage |
|---|---:|---:|---:|
| exact | 0.4133 | 0.2720 | **+0.1413** |
| pair | 0.8311 | 0.7649 | **+0.0662** |

**A random draw from `full`'s own criteria reproduces `full` far better than an external pool does** —
which is exactly the structural advantage I suspected and could not test from cache. It is now a
number.

## How the collapse happens differs by metric, and saying "it collapses" flatly would hide that

| metric | contrast | MDE |
|---|---|---|
| exact | +0.0992 → +0.0810 (**−18%**) | 0.0654 → 0.0920 (**+41%**) |
| pair | +0.0612 → +0.0161 (**−74%**) | 0.0535 → 0.0251 (**−53%**) |

On **`pair`** the contrast itself collapses by three quarters while the MDE *shrinks* — the cleaner
signal. On **`exact`** the contrast barely moves and the **MDE grows 41%** — a wider, noisier
baseline. Same verdict by two different routes.

⚠ **Not refuted — not resolved.** Both point estimates stay positive. The honest statement is that
with a fair floor this design **cannot resolve** transport, not that transport is absent.

## Controls

| | returned |
|---|---|
| **REPRODUCTION** ⭐ | subset floor here vs R368 published: **+0.0992 vs +0.0992**, **+0.0612 vs +0.0612** — so this is about R368's quantity |
| **FLOOR CHECK** — run *before* any contrast was read | pool floor 0.2720 / 0.3080 (exact), 0.7649 / 0.7849 (pair) — **non-degenerate** |
| **PLACEBO** | `full` against itself = 1.0 |
| reproducibility | two runs **byte-identical** (`94742fcdc760`) |
| job | task 630: 16,000 labels, sd **0.2270** — the script refused its own output if constant |

The reproduction control's tolerance (0.02) was **argued, not picked**: the join drops prompts
lacking pool labels, so demanding exact equality would have been a control that cannot pass. It
matched to 4 dp anyway.

## What this does to the definition

⛔ **Transport moves from candidate clause to stated limit.** R368's *"the core reproduces the full
rubric's ordering on unseen responses better than random"* rested on a baseline drawn from **the very
criteria being summed to make the target**. With a baseline that is not, the finding does not
resolve.

**R368's number stands as a number.** What it measured was the floor.

## Register

| criterion | status |
|---|---|
| **agreement with people on fresh responses** | **N/A**, unchanged since R233 — the fresh responses carry **no human rankings**. Every number here is agreement with the **full rubric** |
| **a second judge** | **N/A** — task 630 judged with 2B only, matching the cache |
| **resolving transport at all** | needs more prompts or a lower-variance contrast; the pool floor's MDE is 0.0920 on exact |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"matched on difficulty, the core reproduces the full rubric's ordering on unseen responses better
> than a size-matched random draw."*

**Against a random draw that is not a subset of the target, it does not resolve — and the subset
floor sits +0.1413 above the non-subset one.**

Artifact: `results/r370_nonsubset_floor.json`, source-stamped. Labels:
`results/sat_genericpool16_fresh.npz` (task 630).
