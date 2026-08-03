# Pre-registration — `topw_k4` vs its sham

**Written before the judge job finished.** Job 606 submitted, result not yet on disk.

## Why this exists

`gen` was tested for aboutness with a sham — same generator, wrong prompt's conversation — and
that sham collapsing to the constant (0.0424 vs 0.0420) is what made `gen`'s advantage over
random readable as *aboutness* rather than vocabulary.

**`topw_k4` — the best arm in the whole benchmark — has never had one.** Its +0.0692 over random
has been reported as importance-ordered selection working, and nobody checked whether the
criteria it selects are *about their prompt* or merely *generically good*.

## Estimand

Paired A2 difference, `topw_k4` − `topw_k4_sham`, over 968 prompts, 3 held-out draws.
The sham gives prompt *i* the top-4 criteria of prompt *i+1* — same rule, same k, same judge,
same compute, **wrong prompt**. 0 of 968 came out accidentally identical.

## Worlds

| | prediction | what it means |
|---|---|---|
| **W1 aboutness** | Δ > 0, interval excludes zero | topw's advantage is prompt-specific, as `gen`'s was (+0.0224). The definition's second clause admits it. |
| **W2 generic quality** | Δ ≈ 0 | topw's +0.0692 over random is **criterion quality, not aboutness**. Then the definition's aboutness clause **excludes the best arm in the benchmark** — and by my own exclusion test, either the clause is false or the arm is not a core. |

## Pre-registered kill

Paired bootstrap CI on Δ. **Includes zero → W2.** No re-reading, no switching to A1 or A5 to
find a version that separates — the estimand is A2 because that is what every arm has been
ranked on since the retraction.

## What I expect, recorded so it can be scored

**W1**, and not confidently. High-importance criteria plausibly read as generic — *"the reply
should be accurate"* is exactly the kind of thing annotators rate important, and it would score
on any prompt. `gen`'s sham collapsed all the way to the constant; if topw's does not, the two
arms differ in kind and not only in degree.
