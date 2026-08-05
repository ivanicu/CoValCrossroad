# R516 · A per-prompt clause ① is not well-defined

**Decision this makes safe:** whether clause ① can be rescued by per-prompt operationalisation, or
should be deleted.

**Estimand:** for each admitted arm, its per-prompt **win rate** against the ① comparator
(`random_k4_s0`), and the τ at which a rule "win on ≥τ of prompts" would exclude it.
**Population:** 968 prompts · **instrument:** per-prompt A2 over all annotators · **baseline:**
`random_k4_s0` · **regime:** each arm at its own k.

## Controls — all passed
| control | returned |
|---|---|
| **Positive** ×5 | every admitted arm reproduces its stored `c1[0]` **to 6 decimals** |
| **Placebo** | base vs itself: **0.0000 wins, 1.0000 ties** |
| **Negative (null)** | sibling random arm `random_k4_s1`: win **0.3781** |
| **Sham** | `coval_core_sham`: win **0.3998**, just above the null |

## Result

| arm | mean Δ | win | tie | loss |
|---|---|---|---|---|
| `coval_core` | +0.0738 | **0.5382** | 0.2655 | 0.1963 |
| `topw_k3` | +0.0705 | 0.5331 | 0.2696 | 0.1973 |
| `topw_k4` | +0.0715 | 0.5227 | 0.2934 | 0.1839 |
| `topw_k6` | +0.0714 | 0.5072 | 0.3244 | **0.1684** |
| `topw_k8` | +0.0666 | **0.4897** | 0.3316 | 0.1787 |
| *null* `random_k4_s1` | +0.0055 | 0.3781 | 0.2934 | 0.3285 |

**Every admitted arm beats the null (0.4897–0.5382 vs 0.3781), so a null-calibrated per-prompt ①
excludes nothing.** At **τ = 0.50** — the natural "majority" reading — it excludes `topw_k8`.

## ⭐⭐⭐ Why that exclusion is an artifact, and the clause is ill-posed

**Ranking by win rate and by loss rate disagree at Kendall τ = −0.600.**

| ranking | order |
|---|---|
| by **win** rate | `coval_core` > `topw_k3` > `topw_k4` > `topw_k6` > `topw_k8` |
| by **loss** rate | `topw_k6` > `topw_k8` > `topw_k4` > `coval_core` > `topw_k3` |

`coval_core` is **1st by wins and 4th by losses**; `topw_k6` is **4th by wins and 1st by losses**.

**Mechanism:** per-prompt A2 has only **7 levels over 6 pairs**, so ties are structural — and the tie
rate rises **monotonically with k** (0.2655 → 0.3316). A higher-k arm both wins less *and* loses
less. **A win-rate rule punishes an arm for tying; a loss-rate rule rewards it.** Under "ties as
half-wins" nothing is excluded below τ = 0.70.

⭐ **So the exclusion of `topw_k8` is produced by the tie convention, not by the arm.** A per-prompt
① is not one clause but a family whose members disagree about which arm fails, and the aggregation
choice does more work than the criterion.

**Conclusion: clause ① is deletable** — globally subsumed by ②, and per-prompt ill-posed.
**Impossible here:** whether some *other* per-prompt aggregation is principled. That is a construct
claim needing an external standard for what a core must do.
