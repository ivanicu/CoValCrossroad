# R1103 — the admitted set is **not an object**. |admitted| is **22.77 [17, 26]**, and **11 of 99 arms are coin flips** — including **all six `topw` arms**.

**The decision this round makes safe:** whether the counts this arc publishes — 24, 9, 6, 0, the
nesting, the slack — are properties of the definition or of the particular 968 prompts. **Of the
prompts.** R1055's committed noise floor said `0 unstable`; resampling the population instead of the
bootstrap seed gives **11**.

## ⛔ Two things that look like prior art, checked before building — and one is reproduced as the sham

| round | what it measured | why it is not this |
|---|---|---|
| **R1055** | *"the admitted set at 3 seeds: 24 always in, 75 always out, **0 unstable**"* | three **inner bootstrap seeds at a fixed prompt sample**. With NBOOT = 4000 the 2.5th percentile barely moves, so `0 unstable` is close to forced. §4's **determinism read as currency** |
| **R978** | churn at N ∈ {242, 484, 726, 968} | its **N=968 row is 0 by construction** — the corpus against itself, which R978 correctly labels its own PLACEBO. Its `registered band` of **4** at N=968 is used here as the pre-registration |

## ⭐ The result

**Instrument** R1055's operator, copied — 99 arms, target A2, comparators `{generic, genericpool16}`,
q = 100. **Outer** 1,000 bootstrap resamples of the 968 prompts × 3 seeds = **3,000 draws**.

| | |
|---|---:|
| point estimate (R1055's committed set) | **24** |
| **\|admitted\| across 3,000 resamples** | **22.77 [17, 26]**, min 14, max 27 |
| arms in the band (0.05, 0.95) **in every seed** | **11** |
| R978's registered band at N=968 | 4 |

⚠ **The bootstrap mean sits BELOW the point estimate** (22.77 vs 24). That is the expected direction:
membership requires clearing a one-sided bound, and a resample is on average noisier than the sample
it came from, so borderline arms fall out more often than they fall in.

### The 11 unstable arms

| arm | admission frequency | in R1055's 24 |
|---|---:|---|
| `topw_k6` | 0.937 | ✅ |
| `topw_k4` · `topw_k4_detA` · `topw_k4_detB` | 0.915 | ✅ |
| `coval_core_2bA` · `coval_core_2bB` | 0.873 | ✅ |
| `topw_k3` | 0.847 | ✅ |
| `oracle_k4_08bR` | 0.768 | ✅ |
| **`topw_k8`** | **0.552** | ✅ |
| `greedy_k12_fit1` | 0.116 | ❌ |
| `topw_k2` | 0.079 | ❌ |

**Monte-Carlo SE of a frequency: 0.016**, so none of these is a resolution artifact.

⛔⛔ **All six `topw` arms are in the band, and `topw_k8` is a coin flip at 0.552.** Those six are
exactly the arms R1101's ladder removes under the authorship reading — **so the ladder 24 → 9 → 6 → 0
that I committed two rounds ago is arithmetic over a set whose members are individually 55–94%
likely.** R1099's 9-arm slack and R1098's nesting inherit the same.

⭐ **And the set does not only lose members — it gains them.** `greedy_k12_fit1` and `topw_k2` are
outside R1055's 24 and are admitted in 12% and 8% of resamples. A "not admitted" is not a fact about
those arms either.

⚠ **`coval_core` itself is stable at 0.979** — the released core is one of the arms that does not
move. Its two twins are not (0.873), consistent with R1011's separate finding that they are scored on
200 of 968 prompts.

## ⭐ The sham is the finding's other half

**R1055's own control, rebuilt exactly:** hold the prompt sample fixed, vary only the inner bootstrap
seed, 3 seeds, NBOOT = 4000. **Result: 0 unstable arms** — R1055's committed number, reproduced.

**Same operator, same data, same arms; 0 versus 11.** R1055's noise floor certified that the
**estimator** is deterministic and never that the **set** is a property of anything. The two units
were written out as separate strings in the docstring *before* the controls were designed, because a
control that shares an instrument's blind spot licenses nothing.

## Controls — 6, all green

| control | result |
|---|---|
| POSITIVE the point estimate reproduces R1055's committed **24 by name** | PASS |
| PLACEBO the identity outer draw is deterministic | PASS |
| NEGATIVE an arm against itself is never admitted (`lo = 0`, and `> 0` is false) | PASS |
| INSTRUMENT the analytic inner bound agrees with R1055's 4,000-draw bootstrap on **every** arm — **0 disagreements** | PASS |
| SHAM R1055's inner-seed control returns **0** unstable, a different quantity | PASS |
| SEEDS the outer seed flag changes the draws | PASS |

**Instrument validation, not assumption.** The outer sweep takes the inner lower bound analytically
(`mean − 1.96·SE`) because the nested form is ~10⁴× the compute. On the identity sample its admission
decision matches R1055's full bootstrap on **all 99 arms**, and the disagreement list is reported
whether empty or not.

## ⚠ The strongest confound, named rather than dismissed

**"The 968 prompts *are* the population, so there is no sampling variability and the set is exactly
24."** That is a scope choice, not an empirical claim, and under it this round measures nothing.

It is not the scope this arc has been using. Every published sentence — *the definition admits*,
*the families nest*, *③ removes 4 of 9* — is worded as a property of the **definition**, and R978
already published prompt-count sensitivity as a finding rather than a curiosity. **If the counts are
about these 968 rows and nothing more, they need to say so; if they are about the definition, they
need this interval.**

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the **true** sampling distribution of the admitted set | **N/A** | a second independent draw of 968 prompts; the bootstrap approximates it and is labelled as an approximation throughout |
| whether an unstable arm **should** be admitted | **N/A** | an external criterion; A2 is agreement with this release's annotators |
| a stable set at this n | **N/A** | ≈ 8× the prompts for the borderline arms, since the cut's resolution scales as 1/√n and R1102 measured the MDE at 0.008–0.010 |
| cross-release | **N/A** | a second release |

`run.py` · `results/set_stability.json`
