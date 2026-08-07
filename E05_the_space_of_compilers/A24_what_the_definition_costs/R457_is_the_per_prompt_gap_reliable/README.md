# R457 · the per-prompt advantage **is** reliable — and my first estimand was contaminated by a shared term

**The decision this round makes safe:** whether a per-prompt stratification is licensed at all.
**Yes** — `W-STRUCTURED`, ceiling ρ_full = **0.8812**.

## ⛔ The announced covariate is inadmissible, and §4 names the defect twice

R456 closed proposing to stratify the gap by covariates **including annotator agreement**. The gap is
a **difference of two bounded scores**, and §4: *any covariate raising BOTH arms yields a differential
proportional to their gap.* Annotator agreement raises both by construction — when annotators agree
more, every criterion set tracks the target better. §4's neighbouring row, *conditioning on the
outcome*, is the same defect from the other side. *Twenty-fifth announced step checked.*

## And a gate had to run first, which the announced step skipped

R456 measured α = 0.208 and read it as *"some prompts carry the advantage and others do not."* **That
is a hypothesis, not a reading.** Between-prompt variance is signal only if it **replicates**. If the
per-prompt gap does not correlate between two independent annotator halves, every covariate analysis
is noise-mining whatever covariate is chosen. *Identification before power.*

## ⛔ My first estimand failed — and the sham control is what caught it

Splitting each prompt's annotators into two disjoint halves, baseline held fixed:

| arm | ρ_half | ρ_full (Spearman-Brown) | CI | seed sd |
|---|---|---|---|---|
| oracle | +0.7110 | +0.8311 | [+0.7888, +0.8548] | 0.0139 |
| core | +0.7174 | +0.8355 | [+0.7662, +0.8463] | 0.0223 |
| **sham** | +0.8039 | **+0.8913** | [+0.8612, +0.9097] | 0.0079 |

> ⛔ **The sham is MORE reliable than the core.** The sham has *no* prompt-specific content — so a
> test that ranks it highest cannot distinguish *"the core's advantage is prompt-structured"* from
> *"prompt difficulty is reliable."*

**The mechanism:** `d[p] = A2(arm,p) − A2(base,p)` inherits reliability from **both** terms, and the
baseline term is **common to every arm**. `A2(base,p)` is itself highly reliable — a fixed criterion
set on the same prompt — so `d[p]` is reliable for *any* arm. **A check that cannot fail.**

⚠ **And my verdict branch printed `W-STRUCTURED` while the sham line three rows above said
otherwise** — §4's *the verdict string is not a computation*, sub-kind ①. The branch is now required
to read the sham.

## ⭐ The arm-specific estimand — core **minus** sham, so the shared terms cancel

| | ρ_half | ρ_full | CI | seed sd |
|---|---|---|---|---|
| **core − sham** | +0.7876 | **+0.8812** | [+0.8460, +0.8946] | 0.0084 |

`A2(core,p) − A2(sham,p)` is **the value of having the RIGHT criteria on this prompt**, with the
shared baseline *and* the shared prompt-difficulty component both cancelled. It differs from both
contaminated versions (0.8355, 0.8913), so it is not a copy of either.

> **The value of prompt-specific criteria is a reliable per-prompt property.** Some prompts genuinely
> benefit far more than others, and that variation replicates across independent annotator halves.

## Controls

| control | returned |
|---|---|
| **POSITIVE** — the oracle's gap (chosen *using* the answer, so genuinely prompt-specific) | ρ_full **+0.8311** [+0.7888,+0.8548] ✅ |
| **NEGATIVE** — prompt labels of half B shuffled | **+0.0168** ✅ |
| g=0 — an arm's gap against itself | identically 0 → ρ **undefined**, and the code says so rather than returning a number ✅ |
| SHAM | **fired** — it is why this round has a second estimand |

## What this licenses, and what it does not

- **Licenses:** a per-prompt stratification, with **ceiling ρ_full = 0.8812** — a covariate has real
  headroom, and no covariate can explain more of the gap than the gap reliably has.
- **Requires:** the both-arms check on every covariate. `corr(cov, A2_core)` and `corr(cov, A2_base)`
  reported *separately*; anything raising both is reported and **not used**.
- **Does not license:** any claim about *which* prompts. That is the next round, and running it here
  would be the noise-mining this gate exists to prevent.

## Impossible here, named

- **separating conversation structure from annotator-pool structure** — both halves come from the
  same pool; would need two independent annotator pools per prompt.
- **a covariate that is a function of the target** — inadmissible by construction, not missing.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
