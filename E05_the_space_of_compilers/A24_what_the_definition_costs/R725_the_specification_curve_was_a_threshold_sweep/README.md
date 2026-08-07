# R725 · the specification curve was a threshold sweep

**Two results, and the first must be labelled correctly or the second is unreadable.**

## ⛔ (1) DERIVATION — R724's five "defensible readings" are four thresholds on one statistic
`mde = ZEFF·sd/√n` with `ZEFF = 2.801585` *(R294:59, 121)*, and the CI is a percentile bootstrap of
the same mean. So every rule is a threshold on `t = eff/SE`:

| rule | predicate | ⟺ |
|---|---|---|
| point | `eff > 0` | `t > 0` |
| ci_only | `lo > 0` | `t > 1.959964` |
| mde_only | `eff ≥ mde` | `t ≥ 2.801585` |
| **strict** *(R294's own)* | `lo > 0 ∧ eff ≥ mde` | `t ≥ 2.801585` — **identical to mde_only when eff > 0** |
| conservative | `lo > mde` | `t > 4.761549` |

**Four distinct thresholds among five labels**, so R724's 5×5 grid has at most **16 distinct rule
pairs of 25**, and its "100 cells" overstate the dimensionality explored. **This is algebra. It is
not evidence, and it is not quoted as any.**

⭐ **What IS evidence: the equivalence holds on the artifact — 0 mismatches over 410 checks.** The
derivation assumes `SE_bootstrap = SE_analytic`; measured, the two disagree by up to **7%**
(ratio min 0.9478, median 1.0049, max 1.0691). Zero mismatches means **no arm sits close enough to
a threshold for that discrepancy to change a verdict.** The algebra says the rules *should* collapse;
the 410 checks say they *do*, here.

## ⭐ (2) MEASUREMENT — my own proposed attack fails, and R724's qualification stands
R724 excluded `coval_core` under `lo > mde` while treating every `mde` as exact. `mde` is estimated
from the same sample as the effect, so the natural attack is that its sampling error flips the
verdict. **It cannot.**

| | |
|---|---|
| `coval_core` clause-② `t` | **4.2336** |
| conservative threshold | **4.7615** |
| gap | 0.5280 |
| the mde's own relative sampling SD at n = 968 | 0.022739 = `1/√(2(n−1))` |
| **gap in sampling SDs of the mde** | **8.29** |
| crossing probability, seeds 11/12/13 | **zero at all three**, MC sd 0 |

**So the exclusion is a property of the arm, not of a noisy threshold.**

## Controls — 5 PASS, 0 FAIL
**POSITIVE + g=0 in one band**: an arm planted *at* the threshold returns crossing probability
**0.5053**; at `t = 0` it returns **0** and at `t = 20` it returns **1** — `floor 0 < planted 0.5053
≤ ceiling 1`. An instrument returning zero everywhere would be blind, and this is what separates
that from a real null · **NEGATIVE**: permuting SE across cells breaks the agreement (**6**
mismatches vs **0**), excluding *"any t-threshold reproduces these rules"* · **SHAM**: threshold
removed → agreement trivially 410/410, the same operation minus the ingredient · **PLACEBO**: each
rule against itself → 0 · **UNIT**: instrument unit *"a threshold on t recovered from the CI and
mde"* and claim unit *"the rule R294 actually applied"* are asserted **equal only because B = 0**.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A distinct thresholds ⛔ derivation | 4 [1, 5] | **4** | yes |
| B rule/threshold mismatches | 0 [0, 410] | **0** | yes |
| C distinct rule pairs of 25 ⛔ derivation | 16 [1, 25] | **16** | yes |
| D gap in mde sampling SDs | 7.0 [0, 100] | **8.29** | yes |
| DIRECTIONAL — mde noise cannot flip it | — | **holds** | — |

⭐ **The directional was registered as the refutation of my own previous NEXT line.** R724 closed by
suspecting the conservative rule was "not stricter, just noisier". Writing that suspicion down as a
failable directional *before* measuring is the only reason its failure counts for anything.

## Residue, stated rather than waived
The crossing probability is **model-based**: it assumes the per-prompt differences are normal, which
this artifact cannot check because it does not carry the raw difference vectors. **The 8.29 sampling
SDs is the assumption-light version of the same statement** and does not depend on normality.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137; 3 seeds for the simulation.
**Artifact:** `results/r725_threshold_sweep.json`.
