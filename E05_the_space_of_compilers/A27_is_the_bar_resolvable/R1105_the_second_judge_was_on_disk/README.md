# R1105 — the definition admits **9 arms under the 2B judge and 0 under the 8B judge**. 8 of the 9 are **sign flips**. The 8B files were committed the whole time.

**The decision this round makes safe:** whether ②′ membership is a property of the arms or of the
(arm, judge) pair. **Of the pair.** And the wall that kept this unmeasured was one I printed myself.

## ⛔ The wall was never checked, and I wrote it twice

`corebench/results/` holds `sat08_full.npz`, `sat08_generic.npz`, `sat08_genericpool16.npz`,
`sat08_coval_core.npz` and **32 selection arms already rebuilt under the 8B judge** — materialised,
committed, **zero further judge calls**.

Meanwhile **R1100** and **R1101** each printed, in their impossibility registers:

> *the verdict for `*_08bR` arms — **N/A** — the 8B judge npz, a different instrument axis*

**That marked as unavailable a file sitting in the same directory as the one those rounds read.**
§4's *a wall never checked*: an unchecked wall is UNVERIFIED, never SETTLED — **and a register line
saying `N/A` is precisely what stops anyone looking.**

## ⭐ The result

**Population** the **43** arms carrying both a 2B and an 8B satisfaction file (27 excluded for want
of an 8B counterpart, named in the artifact — comparing 99 arms to 43 would attribute a population
change to the judge). **Operator** R1055's, unchanged. **Comparators** taken from the judge under test.

| | 2B judge | 8B judge |
|---|---:|---:|
| **admitted ②′** | **9** | **0** |
| only under this judge | `coval_core`, `greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4`, `oracle_k4_fit1`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` | — |
| symmetric difference | **9** against a threshold of 4 | |

⛔⛔ **`coval_core` — the released core, the object this definition was written from — is not admitted
under the 8B judge.**

## ⭐ Sign flip or resolution loss? Classified, because R1102 downgraded a round for not asking

| arm | class | min Δ vs a comparator, 8B |
|---|---|---:|
| `coval_core` | **SIGN FLIP** | **−0.0072** |
| `topw_k3` · `topw_k4` · `topw_k6` · `topw_k8` | **SIGN FLIP** | −0.0088 · −0.0122 · −0.0172 · −0.0243 |
| `greedy_k4_fit1` · `oracle_k4` · `oracle_k4_fit1` | **SIGN FLIP** | −0.0290 · −0.0283 · −0.0325 |
| `indep_k4_fit1` | resolution loss | +0.0044, no longer resolvable |

**8 of 9 are sign flips.** This is not intervals widening — the arms are genuinely **behind** the
generic comparators under the 8B judge.

## ⭐ The mechanism, measured: the ordering itself inverts

| arm | mean A2, 2B | mean A2, 8B |
|---|---:|---:|
| `coval_core` | **0.5665** | 0.4695 |
| `generic` | 0.5514 | **0.4767** |
| `genericpool16` | 0.5422 | 0.4655 |
| `topw_k4` | 0.5642 | 0.4646 |
| `random_k4_s0` | 0.4927 | 0.4084 |

**Under 2B the prompt-specific core leads the fixed generic rubric; under 8B the generic rubric
leads.** And `oracle_k4` — the release's own **leaky upper bound**, fitted to the human target — sits
**0.0283 behind `generic`** under the 8B judge.

## ⭐ The specification curve, and both cells were on disk

Measured from the objects: `core_topvar_k4_08b.json` carries the **same criterion texts** as the 2B
arm while `_08bR` does not. So the release's two suffixes are the two defensible specifications:

| | `_08b` — 2B-selected criteria **re-scored** by 8B | `_08bR` — the rule **re-run** under 8B |
|---|---|---|
| measures | **measurement** sensitivity | whole-**pipeline** sensitivity |
| `greedy_k4_fit1` | ❌ | **✅** |
| `indep_k4_fit1` | ❌ | **✅** |
| `oracle_k4` | ❌ | **✅** |
| `topvar_k4` · `topwvar_k4` | ❌ | ❌ |

⭐ **A fixed arm does not survive the judge change; a pipeline allowed to refit under the new judge
partly does.** Compared on the 18 arms both builds contain — the `_08bR` build falls back to a
smaller population, and differencing unrestricted would attribute a population change to the
specification.

⚠ **DERIVATION, labelled:** `select_core.py`'s own help states the two specifications **coincide
exactly** for the satisfaction-blind rules (`random_k`, `topw_k`, `topabs_k`, `full`), so no `_08bR`
exists for them and none is missing.

## Controls — 6, all green

| control | result |
|---|---|
| POSITIVE the 2B run equals R1055's committed set restricted to the common population | PASS |
| NEGATIVE the two judges are not the same instrument — **96.4%** of cells differ, corr **0.483** | PASS |
| **POSITIVE the 8B judge can still ORDER** — `generic` − `random_k4_s0` = **+0.0683 [lo +0.0581]** | PASS |
| SHAM the same operation with the judge held **fixed** moves nothing | PASS |
| PLACEBO each judge's set against itself is empty | PASS |
| INSTRUMENT the analytic inner bound equals the 4,000-draw bootstrap under **both** judges | PASS |

⛔ **Without the third control, `9 → 0` would be silence.** An instrument that orders nothing fails
every arm for reasons unrelated to the definition. The 8B judge separates `generic` from random at
**+0.0683**, *wider* than the 2B judge's **+0.0587** — so it discriminates at least as well, and the
collapse is a measurement.

## The two axes, side by side and never subtracted

| axis | what it moves | measured |
|---|---|---|
| **sampling** (R1103/R1104) | which 968 prompts were drawn | \|admitted\| 22.77 **[17, 26]** |
| **instrument** (here) | which judge scored the criteria | **9 → 0**, 8 of 9 sign flips |

**The instrument axis is the larger one, and it had no interval at all.**

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the 8B verdict for the 27 excluded arms | **N/A** | judging those arms' criteria with the 8B model — real inference, not a re-read |
| **Qwen3B and Phi**, which also sit on disk at 968 prompts (`E04/…/R164_instrument/`) | **N/A** | their **comparator** files; that directory ships `sat_full_*` and `sat_core_*` only, so ②′ is not computable there. ⭐ A real N/A, stated with exactly what would lift it |
| whether either judge is **correct** | **N/A** | an external gold standard. A2 is agreement with this release's annotators *as scored by a named judge* — R1011's caveat now needs that clause |
| cross-release | **N/A** | a second release |

`run.py` · `results/second_judge.json`
