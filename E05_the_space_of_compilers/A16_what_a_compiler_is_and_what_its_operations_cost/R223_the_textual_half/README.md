# R223 — the textual half of the rewrite

**Arc E05·A16.** The decision this makes safe: *R222 found polarity normalisation to be
decision-null by derivation yet the largest positive contributor to instrument stability in the
lattice. Both cannot be about the same thing. Which half of the operation carries the gauge gain?*

The algebra **cannot** change instrument dependence — it re-labels a number *after* the judge has
spoken and never reaches the judge at all. So the gain, if real, had to be in the **text**. R222
could not see that, because it implemented the arithmetic and called it the operation.

## Why this needed no GPU

I was about to queue a judge pass over generated rewrites. **The rewrites already exist and are
already judged**: `coval_core` *is* the official positive-form rewrite, human-reviewed, and r164
scored it under all five instruments. Generating my own would have made the rewrite **my**
instrument and answered a question about my prompt rather than about OpenAI's compiler.

## The prediction, stated before measuring

If the rewrite were only the algebra, the judge would score the rewritten text at exactly
`s′ = 1 − s`. **Every departure from that line is what the text does that the algebra does not.**

---

## Results — 1,185 inferred (full → core) pairs

| stratum | n | gauge full | gauge core | Δ | \|s′−(1−s)\| | \|s′−s\| |
|---|---:|---:|---:|---:|---:|---:|
| all pairs | 1185 | 0.6394 | 0.6359 | −0.0035 | 0.3863 | 0.1246 |
| **negative source (a flip)** | 158 | 0.6189 | 0.6252 | **+0.0063** | **0.2345** | 0.2982 |
| …lineage Jaccard ≥ 0.5 | 43 | 0.6462 | 0.6237 | **−0.0225** | 0.2132 | 0.2926 |
| positive source (**sham**) | 1027 | 0.6425 | 0.6376 | −0.0050 | 0.4097 | **0.0979** |
| verbatim (**positive control**) | 92 | 0.6555 | 0.6537 | −0.0018 | 0.4197 | **0.0191** |

**Controls, all behaving:**

- **Positive control** — verbatim pairs: `|s′−s| = 0.0191` and `Δgauge = −0.0018`. Identical text
  scores identically. The pairing and the gauge measurement are valid.
- **Sham** — positive-source pairs, where no flip was supposed to happen: `|s′−(1−s)| = 0.4097`
  against `|s′−s| = 0.0979`. **The flip signature appears only where a flip was performed.**
- **Negative control** — shuffled lineage, 5 seeds: `Δgauge = −0.0035`, identical to four decimals
  across every seed. Null.

### The official rewrite does what it says

On negative-source pairs the rewritten text reads to the judge as **closer to the negation than to
the original**: `0.2345 < 0.2982`, and the sham inverts that ordering. This is the first controlled
confirmation in this project that the polarity rewrite is a real polarity change in behaviour, not
only in wording.

### But it does not carry the gauge gain — my own R222 reading is refuted

`Δgauge = +0.0063` on flipped pairs: the rewritten text is, if anything, **slightly more**
instrument-dependent. **R222's +0.0343 is not the text.**

⚠ **The high-lineage subgroup has the opposite sign** (−0.0225, n = 43) and I am not taking it. A
subgroup of 43 with a reversed sign, selected after seeing the result, is the exact failure this
project keeps catching. The honest statement is that **the sign is not stable across lineage
strata**, and the effect is small against a gauge level of ≈0.62 either way.

---

## So where does R222's +0.0343 come from? The selection it reorders

Eliminated: not the algebra (never reaches the judge), not the rewritten text's own instrument
spread (wrong sign, controls valid). The remaining candidate is the interaction R222 itself
predicted — normalising polarity **reorders the "highest-rated" list**, so a *different* four
criteria survive the cut. Measured directly:

| the four criteria kept by… | mean instrument spread of the kept set |
|---|---:|
| top-4 by rating (polarity not normalised) | 0.6491 |
| top-4 by \|rating\| (i.e. after normalising) | **0.6385** |
| | **−0.0107** |

> **The rewrite's benefit is not that it makes criteria easier to judge. It is that it changes
> which criteria get kept, and the ones it promotes happen to be the individually stabler ones.**

That makes the benefit **contingent on the selection rule** — it is a property of the *pipeline*,
not of the rewrite, and it would not survive a compiler that selected differently. No round in this
project could have seen that while compilation was reported as one number.

---

## Scope, and the limitation that bounds every gauge number here

**Population** — 1,185 inferred pairs over the prompts where a core criterion exists. **Instrument
coverage is not uniform**: `base`, `phi` and `qwen3b` cover 968 prompts; `swapped` and
`no_fewshot` cover **300**. Every gauge figure is therefore over the five-instrument intersection,
and the selection-reordering table is `n = 300` prompts. Stated here because a spread computed over
a differently-sized intersection is a different quantity.

**Lineage is inferred.** The release ships no `source_criterion_id`; pairs are matched by
content-word Jaccard, and R219 measured that statistic at median 0.444 matched against 0.050
shuffled. This is why every row is stratified by lineage confidence and why the shuffled-lineage
null is run — and it is why the single missing field in the release keeps being the cheapest thing
that would sharpen this whole arc.

## The sentence that can no longer be written

*"Rewriting negatives into positive form makes the rubric easier for a judge to score."* It does
not. It changes which criteria a rating-ordered selector keeps.
