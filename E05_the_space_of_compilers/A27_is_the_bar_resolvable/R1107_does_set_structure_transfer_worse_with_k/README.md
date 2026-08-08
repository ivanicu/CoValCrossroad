# R1107 — **no dose.** The gap peaks at **k = 4** — the single dose R1106 looked at — and the placebo would have vetoed a positive finding anyway. What survives is stronger: **refitting under the second judge reverses the deficit at 4 of 4 doses.**

**The decision this round makes safe:** whether R1106's *set structure* label may be used as the name
of the cross-judge failure. **It may not.** But the intervention that would repair it is now measured
at four doses instead of one.

## ⛔ The cost meter ran first and changed the design

`oracle_k` searches combinations under a 20,000-per-prompt cap; at k = 8 and 12 that is tens of
minutes per cell per judge. **`greedy_k` is the other set-aware rule** — sequential, each pick
conditional on those already chosen — and costs ~3 s. So the sweep runs `greedy` vs `indep`, which is
the contrast `select_core.py` itself names (*"the oracle-minus-indep difference isolates SET
STRUCTURE from mere fitting"*), with `oracle_k4` as the committed corroborating point. **The
expensive complete success was refused for the cheap decisive one, and the refusal is in the
register rather than silent.**

⭐ **And the rebuild was verified before it was used.** `--full-npz sat08_full.npz --select-npz
sat_full.npz --tag-suffix _08b` reproduces the committed `sat_greedy_k4_fit1_08b.npz` and
`sat_indep_k4_fit1_08b.npz` **byte-identically** (`meta` and `sat` both `array_equal`). Without that,
new k cells would not be comparable to R1106's.

## ⛔ The result: world A is killed

`gap(k) = residual(indep_k) − residual(greedy_k)`, residuals taken against the compression line
**fitted on R1106's 42 held-out arms** (slope 0.7142, intercept −0.0251).

| k | 2 | 4 | 8 | 12 |
|---|---:|---:|---:|---:|
| **gap** (`_08b`, re-scored) | +0.0175 | **+0.0452** | +0.0391 | +0.0224 |
| **gap** (`_08bR`, re-run under 8B) | **−0.0123** | **−0.0189** | **−0.0107** | **−0.0044** |
| **placebo** `topw_k` residual | +0.0069 | +0.0037 | −0.0049 | −0.0073 |

**Not monotone.** `gap(12) − gap(2)` has a bootstrap CI of **[−0.0027, +0.0124]** — it straddles zero.
⭐ **And the gap PEAKS at k = 4, which is the one dose R1106 observed.** That is the shape of a
reported cell selected by where it was looked at.

⚠ **What survives:** the gap is **positive at all four k** — `greedy` transfers worse than `indep`
at every dose. The *direction* holds; *"more set structure ⇒ less transfer"* does not.

## ⭐⭐ The negative control is the round's real finding

Under `_08bR` — the rule **re-run** under the 8B judge — the gap **reverses sign at 4 of 4 doses**
(−0.0123, −0.0189, −0.0107, −0.0044). Refitting to the new instrument does not merely collapse
`greedy`'s deficit; it makes `greedy` the **better** transferrer.

**So the deficit is an artifact of being fitted under the FIRST judge, not a property of set-aware
fitting as such.** That is an intervention on the fitting judge, consistent across four doses.

⚠ **Its limit, stated:** the bootstrap CI in this round is on the **dose contrast** only. The sign
reversal is four point estimates with a consistent direction and **no interval** — reported as a
direction at 4 of 4, not as a magnitude.

## ⛔ The placebo failed — and it had passed for the wrong reason first

**v1 tested only *increasing* monotonicity.** `topw_k` drifts **monotone decreasing**, so
`not topw_mono` was `True` and the control passed while the placebo was in fact trending at **51% of
the gap's own span** (0.0141 vs 0.0277). Direction-agnostic now, and it **fires**.

⭐ **The repair changed what the control can gate, and that asymmetry was missing from v1.**

| | needs |
|---|---|
| **the KILL** (no monotone trend exists) | the rebuild control only |
| a **SURVIVAL** (a real dose in k) | the rebuild control **and** a flat placebo |

A drifting placebo vetoes a *positive* dose claim — the trend would belong to **k** (set size,
coverage, saturation), not to fitting. It cannot veto a finding that attributes nothing to anything.
**So: even had the gap been monotone, this design could not have called it a fitting effect.**

## Controls — 4, reported whole

| control | result |
|---|---|
| POSITIVE the rebuild reproduces two committed `_08b` cells **byte-identically** | PASS |
| **PLACEBO `topw_k`, which fits nothing, shows no comparable trend in k** | **FAIL** (drifts at 0.509 of the gap's span) |
| GATE the rebuild alone licenses the kill; survival would also need the placebo | PASS |
| NEGATIVE refitting under 8B (`_08bR`) collapses the gap | PASS (it reverses it) |

**20 cells tested**, all reported — trend and no-trend, both specifications.

## What R1106 must now be read as

| R1106 said | after R1107 |
|---|---|
| the residual pattern is *"consistent with set-structure overfitting"*, n = 2 rules | **the label is withdrawn as a name.** The gap does not grow with k and peaks at the observed dose |
| `oracle`/`greedy` fall, `indep` does not | **holds at every k** as a direction — `greedy` > `indep` deficit at 2, 4, 8, 12 |
| R1105's `_08bR` recovery corroborates | **strengthened**: the recovery is a sign **reversal**, at 4 of 4 doses |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| `oracle_k` at k = 8 and 12 | **N/A on cost** | tens of minutes per cell per judge under the 20,000-combination cap. Refused explicitly, not dropped |
| attributing any k-trend to **fitting** | **N/A in this design** | a placebo that does not itself drift with k; `topw_k` drifts at 0.509 of the gap's span |
| an interval on the `_08bR` sign reversal | **N/A here** | its own bootstrap; this round's CI is on the dose contrast |
| whether either judge is **correct** | **N/A** | an external gold standard |
| cross-release | **N/A** | a second release |

`run.py` · `results/set_structure_dose.json`
