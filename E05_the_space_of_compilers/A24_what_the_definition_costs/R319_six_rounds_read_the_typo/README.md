# R319 — six rounds read the tensor built with a hand-retyped prompt

**Decision this makes safe:** whether A23's six tensor-reading rounds may stand as published.
**Five may, with 37 corrected magnitudes. One may not — R267 was UNREADABLE only because of the
typo, and reading it changes what the arc concludes.**

## The provenance, proven by git object hash

| | sha256 |
|---|---|
| `4135f31` 06:00:32 **pre-fix** `R257/results/instruments.npz` | `f29c6e02…` |
| `_archive/r257_first_pass/instruments_retyped_prompt.npz` | **`f29c6e02…` identical** |
| `f6e3bbd` 06:12:56 **post-fix** | `42a84f65…` |
| the committed tensor now | **`42a84f65…` identical** |

Draw A **is** the hand-retyped output; draw B **is** the canonical one. Not a filename, not an
inference — D8.

The change itself is recorded where this project says the WHY lives, the commit body of `4498585`:

> *"my own positive control caught me retyping the prompt instead of importing it … r 0.9407 /
> MAD 0.0632 against the r04 cache, where R234's faithful re-implementation gets 0.998 / 0.008.
> I HAND-RETYPED the few-shot block instead of importing `covalx.judge.build_prompt`."*

**R318 called this "an unrecorded change" and built an impossibility on it. That was a wall never
checked.**

## Why it happened — mechanism, not blame

The fix landed **06:02:28**. A reader first pointed at the archived first pass **06:06:13**. The
canonical re-run only arrived **06:12:56**. For those ten minutes the defective tensor was the
*only* tensor, and nobody re-pointed the readers afterwards.

## Result — W-VERDICT-MOVES

| round | keys | moved | verdict label |
|---|---:|---:|---|
| R260 | 5 | 2 | *(none)* |
| **R267** | 11 | 5 | **`UNVERIFIED` → `W-COARSE`** |
| R268 | 14 | 8 | `W-COARSE` → `W-COARSE` |
| R269 | 16 | 7 | `W-COARSE` → `W-COARSE` |
| R274 | 16 | 9 | `W-FALLS-FAR` → `W-FALLS-FAR` |
| R275 | 8 | 6 | `W-CANCEL` → `W-CANCEL` |

**37 published quantities move. One verdict label moves.**

### R267 is the one that matters, and the direction is the finding

| tensor | R267's own positive control | verdict |
|---|---|---|
| hand-retyped | **fails** — *"the detector misses a planted effect twice the largest noise source"* | `UNVERIFIED` |
| canonical | **passes** — 0.900 → 0.925 | `W-COARSE`, MDE **(0.08, 0.09]** |

**The typo broke R267's positive control, and a round whose positive control fails cannot report.**
On the canonical tensor it reports, and what it reports is
*"NO EFFECT THIS ARC REPORTED WAS RESOLVABLE AT THIS INSTRUMENT."*

⚠ **Whether that is compatible with R274 is NOT established here.** R274 retracts exactly that
sentence, under *both* tensors, and the two rounds use different detectors and different brackets —
R267's (0.08, 0.09] against R274's [0.105, 0.125]. Two rounds of one arc now assert opposite things
about the same claim, and adjudicating that needs its own round.

## Controls

| control | result |
|---|---|
| **provenance** — archived == pre-fix blob, committed == post-fix blob, and they differ | established |
| **placebo** — each round re-run on its OWN input must reproduce its committed artifact | **6 of 6 PASS** |
| negative | none available: destroying the structure means a third prompt typing, which needs the GPU. Named, not improvised. |

## ⚠ Three defects in this round, and its first two verdicts were both fabricated

**① The first run executed nothing and printed `W-INERT`.** I substituted `repr(str(LIVE))` — a
*string* literal — so `ROOT / "data"` raised `TypeError` and both runs died at import. `copytree`
had already placed the committed artifact in `results/`, so **the placebo compared it to itself and
passed**, the repointed run compared it to itself and "moved 0 keys", and every control was green
having done nothing. It contradicted R318's measured `[0.125,0.125] → [0.105,0.125]`, which is the
only reason I looked. Fixed by substituting a `Path`, **clearing `results/` before each run**, and
gating on the return code.

**② The verdict comparison compared strings that embed numbers.** These rounds interpolate their own
values into the verdict sentence, so any moved number reads as a moved verdict — *precisely what
this round measures*. It reported 5 of 5; the truth is 1 of 5. **Third time this session a string
shortcut manufactured a verdict.** The label is the token before the em-dash.

**③ R260 was reported `RUN-FAILED`, and the failure was mine.** It derives its root as
`next(p for p in parents if (p/"covalx").is_dir())`, not `parents[3]` — the only idiom my pin
rewrote. Now the whole `ROOT = …` assignment is rewritten, because **what varies is how the root is
derived and what matters is only what it ends up being.**

## Scope

The 6 rounds under A23 reading `_archive/r257_first_pass/` · Qwen3.5-2B-Base under R234's canonical
builder vs a hand-retyped approximation of it · R257's 250-prompt grid · one release.

## What this cannot do

Establish that the canonical builder's output is **correct** rather than merely **intended**. That
needs an external criterion the release does not carry. What is established is which tensor each
round meant to read.
