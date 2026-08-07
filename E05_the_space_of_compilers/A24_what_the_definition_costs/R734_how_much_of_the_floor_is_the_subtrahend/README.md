# R734 · how much of the floor is the subtrahend

**The shared subtrahend alone buys a correlation of 0.3062. The random arms R733 used as its floor
reach 0.5034 — a difference of +0.1972, or 10.4 seed SDs. R733's floor was too HIGH, so its excesses
were UNDERSTATED and its conclusion is strengthened, not weakened.**

## ⛔ First: three lines of algebra killed the round R733 proposed
R733's NEXT line proposed building a floor by re-pairing a real arm's per-prompt **margin** to
prompts at random. A margin is `(a_p − r_p)`. **Re-pairing it destroys the alignment of the shared
subtrahend too**, so it collapses to the shuffle null R733 had already run as its NEGATIVE control.

| construction | synthetic demo |
|---|---|
| real margins, shared subtrahend | **0.5107** |
| re-pair the **margin** *(what I proposed)* | **0.0374** — the shuffle null, renamed |
| re-pair the **arm's own part**, keep `r` aligned *(used here)* | **0.4796** |

**The gauge test is first on the attack ladder for exactly this reason: it cost nothing and killed my
own next step before any compute was spent.**

## The two floors on the real arms
| pair | R733 floor | corrected | seed SD | pool component |
|---|---|---|---|---|
| `random_k4_s1` ‖ `random_k4_s2` | 0.4686 | 0.3108 | 0.0212 | +0.1578 |
| `random_k4_s1` ‖ `random_k8_s0` | 0.5206 | 0.3060 | 0.0173 | +0.2146 |
| `random_k4_s2` ‖ `random_k8_s0` | 0.5211 | 0.3019 | 0.0183 | +0.2192 |
| **mean** | **0.5034** | **0.3062** | **0.0190** | **+0.1972 = 10.4 SDs** |

## R733's verdicts re-scored under both floors — neither changes
| object | r to excluded | r to blind | excess @R733 | excess @corrected | verdict |
|---|---|---|---|---|---|
| `greedy` | 0.9747 | 0.7447 | 0.4712 vs 0.2412 | 0.6684 vs 0.4384 | **EXCLUDED** both |
| `indep` | 0.9239 | 0.7769 | 0.4204 vs 0.2734 | 0.6177 vs 0.4706 | **EXCLUDED** both |

**The ordering never depended on this choice.**

⚠ **The difference names a MAGNITUDE, not a CAUSE.** Calling +0.1972 "the criterion pool" would be an
attribution this design cannot make; identifying it needs an intervention on the pool.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: on synthetic vectors with a planted subtrahend, recover the **analytic** floor
`var(r)/√((var(a)+var(r))(var(b)+var(r)))` within 0.02 — *a threshold from the algebra, not chosen* ·
**g=0**: subtrahend set to zero → |floor| < 0.05 · **NEGATIVE**: different subtrahends on the two
sides → collapses, excluding *"any common construction produces this correlation"* · **SHAM**: both
arms' own parts shuffled, `r` still aligned → **0.6421 vs 0.6420**, unchanged, *because the floor
never depended on either arm's signal* · **PLACEBO**: 1.000000.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A R733's floor reproduced | 0.5034 [0, 1] | **0.5034** | yes |
| **B corrected floor** | **0.48 [0, 1]** | **0.3062** | yes |
| **C pool component** | **0.02 [−1, 1]** | **0.1972** | yes |
| D verdicts changed | 0 [0, 2] | **0** | yes |
| DIRECTIONAL corrected below R733's | — | **holds** | — |

⚠ **B and C were badly wrong as point predictions** — I expected the random arms to add ~0.02 beyond
the subtrahend and they add **0.1972, an order of magnitude more.** The intervals absorbed it, which
is what wide intervals do and why they cannot score calibration. **I under-estimated how much
structure two random-selection arms share.**

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, **both writes verified**.
**Artifact:** `results/r734_subtrahend_floor.json`.
