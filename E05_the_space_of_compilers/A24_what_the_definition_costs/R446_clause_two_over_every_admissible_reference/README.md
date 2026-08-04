# R446 · clause ② over **all 1,820** references — the file-order choice did not manufacture the verdict

**The decision this round makes safe:** whether *"the extension is one arm"* is a statement about the
definition or about `POOL[0:4]`. **About the definition** — `W-ROBUST`, over a census of every
admissible reference.

## The defect this closes

R331 measured clause ②'s reference as `POOL[0:k]` — **chosen by file order** — sitting at the 93.7th
percentile of all 1,820 size-4 subsets of its own pool. **Every ② verdict in this campaign, including
R445's `gen −0.0162`, was measured against that one arbitrary draw.**

## ⚠ And the naive version of this sweep is the arithmetic trap

R439 already committed the 1,820 subset **means**, so comparing point A2s is **forced**. But clause ②
requires *resolvedly* better, and each pair carries its own MDE. **The resolved share is the round.**

## Result — 968 prompts × 1,820 references × 3 arms = 5,460 decisions

| arm | A2 | **ADMITTED share** | point quantile | gap |
|---|---|---|---|---|
| `coval_core` | 0.5715 | **0.9841** | 1.0000 | 0.0159 |
| **`gen`** | 0.5374 | **0.0038** | 0.2615 | **0.2577** |
| `gen_sham` | 0.4868 | 0.0000 | 0.0000 | 0.0000 |
| *ORACLE (control)* | 0.7238 | 1.0000 | 1.0000 | — |

> **`gen` is admitted under 0.4% of the reference class; `coval_core` under 98.4%.** The file-order
> choice did **not** manufacture R445's verdict, and *"the extension is one arm"* survives a census
> of every admissible reference.

## ⭐ The point-vs-resolved gap is the finding inside the finding

**`gen` would be "better" than 26.2% of references but is *resolvedly* better than 0.4%** — a
**25.8-point** gap. That gap **is** the resolution effect, and it is exactly why the naive quantile
sweep would have been misleading in the flattering direction. `coval_core`'s gap is 1.6 points;
`gen_sham`'s is zero. **The arm nearest the boundary is the one the resolution effect moves most.**

## Controls

| control | returned |
|---|---|
| POSITIVE — an oracle ordering | admitted under **1820/1820** ✅ |
| g=0 — a reference against **itself** | delta **0.0e+00**, admitted **False** ✅ |
| NEGATIVE — `gen_sham` share ≤ `gen` share | **0.0000 ≤ 0.0038** ✅ |
| PLACEBO — annotator draw held **common** across all 5,460 comparisons | same prompt-keyed rng |

## ⛔ The g=0 control failed first, and the failure was the control's

The first version computed `REF[0]`'s share against the **whole class** and demanded it be < 0.5, on
the reasoning that *"nothing is resolvedly better than itself"*. It returned **0.6253** and failed.

**But `REF[0]` *is* `POOL[0:4]`, the 91.7th-percentile subset** — being resolvedly better than 62.5%
of the *other* 1,819 is exactly what it should do. **The branch tested "not better than most others"
while asserting "not better than itself"** — the ledger's *control fails for its own reasons*, form
④. The check now tests the sentence it makes: the **self** comparison, which is exactly 0 and
unadmitted. The 62.5% is reported **as context, not as a control**.

## Impossible here, named

- **choosing the right reference** — a decision about the definition, not a measurement. R331's
  defect is that the choice was arbitrary; this round shows the *answer* does not depend on it, which
  is a different and weaker thing than fixing it.
- **references outside this 16-item pool** — a larger pool is a different class and needs its own
  judging.
- **construct validity of A2** — the release's own human rankings.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
