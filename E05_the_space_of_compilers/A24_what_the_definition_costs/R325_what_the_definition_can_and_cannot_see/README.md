# R325 — the definition's clause-① exclusions are non-admissions, not refutations

**Decision this makes safe:** how the definition's table may be read. **Four of the five excluded
arms sit below their own MDE — the site cannot say they are worse, only that it cannot say they are
better.**

## What this round deliberately did NOT do

Four rounds decomposed A23's MDE. That number **does not govern the definition** — different
statistic, different comparand, different n — and `FORMULATION.md` already says so. Importing it
here would be the exact scope error the page warns against.

The in-scope question: the table reports clause ② with intervals and clause ① **without them**,
except one row. R306's artifact holds 45 pairwise cells each carrying `eff`, `mde`, `bh`, `res`.
**The MDEs exist; the table simply does not show them.**

## W-SPLIT — 5 of 9 rows clear their own MDE

| arm | clause-① eff | its own MDE | eff/MDE | BH | reading |
|---|---:|---:|---:|:--:|---|
| `coval_core` | +0.0738 | 0.0132 | **5.61** | ✓ | resolvably BETTER |
| `topw_k4` | +0.0715 | 0.0128 | **5.58** | ✓ | resolvably BETTER |
| `generic` | +0.0587 | 0.0144 | 4.09 | ✓ | resolvably BETTER |
| `gen` | +0.0425 | 0.0149 | 2.84 | ✓ | resolvably BETTER |
| `full` | +0.0160 | 0.0113 | **1.41** | ✓ | resolvably BETTER |
| `topwvar_k4` | +0.0113 | 0.0134 | **0.84** | **✓** | **NOT RESOLVABLY EITHER** |
| `topabs_k4` | −0.0033 | 0.0154 | 0.21 | ✗ | NOT RESOLVABLY EITHER |
| `topvar_k4` | −0.0064 | 0.0134 | 0.48 | ✗ | NOT RESOLVABLY EITHER |
| `gen_sham` | −0.0099 | 0.0165 | 0.60 | ✗ | NOT RESOLVABLY EITHER |

## ⚠ The exclusions are non-admissions

**Four excluded arms sit below their own MDE.** `excluded (①)` is *correct* for an admission rule
requiring a resolvable positive — but it is **not evidence against the arm**. Below the MDE the sign
is not readable, so "worse than the baseline" is a claim this design cannot make about any of them.

## ⚠ BH and resolution disagree on `topwvar_k4`

**BH survivor at 0.84× its own MDE** — significant and unresolvable at once. That is why the two are
reported side by side rather than merged: a multiplicity correction asks *is this distinguishable
from zero across the family*, and an MDE asks *could this design have seen an effect this size*.
They are different questions and this row answers them differently.

**And `full` at 1.41× is the thinnest resolved row** — the table quotes `+0.0160` with no hint that
it clears its own resolution by less than half of what the admitted arms do.

## Controls

| control | result |
|---|---|
| **positive** — both admitted arms resolvably positive | 5.61× and 5.58× |
| **negative** — the sham must not be resolvably positive | `gen_sham` −0.0099, 0.60× |
| **placebo** — a self-comparison must give exactly 0 | **structurally absent**: R306 emits no self-pairs, reported as absent rather than substituted |

## Scope

968 prompts · 15,593 annotations · Qwen3.5-2B-Base · baseline `random_k4_s0` · A2·annotator. This
round **reads** R306's committed cells and adds no estimate of its own, so it inherits R306's design
entirely.

## What this cannot do

**Say whether an unresolved arm is worse.** Below the MDE the sign is not readable — which is
precisely the distinction being drawn.
