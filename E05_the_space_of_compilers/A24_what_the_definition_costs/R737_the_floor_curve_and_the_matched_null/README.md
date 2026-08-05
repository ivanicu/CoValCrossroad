# R737 · the floor curve and the matched null

**The floor is a curve in criteria overlap, and the arms the deliverable compares sit on it. Their
matched floors are 0.8299 and 0.7234 — the fourth pair of floors this arc has used for the same
comparison, and the first matched on the quantity that drives it.**

## The curve — k=4, 968 prompts held FIXED across every target
| j (shared criteria) | raw corr | model | ~~j/K~~ | **floor** | seed sd |
|---|---|---|---|---|---|
| 0 | 0.3385 | 0.3385 *(fitted)* | 0.0000 | **0.4244** | 0.0254 |
| 1 | 0.5026 | 0.5038 | 0.2500 | 0.5654 | 0.0178 |
| 2 | 0.6646 | 0.6692 | 0.5000 | 0.7076 | 0.0165 |
| 3 | 0.8321 | 0.8346 | 0.7500 | 0.8517 | 0.0091 |
| 4 | 1.0000 | 1.0000 | 1.0000 | **1.0000** | 0.0000 |

## ⛔ My registered prediction was wrong, and the repair is a stronger control
I registered `raw corr = j/K` — **which assumes independent per-criterion satisfactions.** A good
response satisfies many criteria, so **every pair of subsets shares a per-response component**. The
correct one-parameter form is `ρ + (1−ρ)·j/K`.

⭐ **Fitting ρ = 0.3385 at j = 0 ALONE predicts the four held-out targets to 0.0046.** One parameter
fit at one point predicting four others is a **stronger** positive control than the one I registered —
and it is derived from the construction's definition, so it does **not** share the instrument's blind
spot, which is the failure R736 was written about.

⛔ **`g=0` failed for the same reason** — it demanded `raw ≈ 0` at j=0, which the shared component
forbids. **The control asked for something the design cannot produce.** Repaired to what the design
actually needs: j=0 must sit below j=1 by more than the seed band (**+0.1642 > 0.0790**).

## The consequence
| pair | actual shared criteria | **matched floor** | R735 used |
|---|---|---|---|
| `greedy` vs excluded `oracle` | **2.8492** | **0.8299** | 0.6458 |
| `indep` vs excluded `oracle` | **2.1095** | **0.7234** | 0.6458 |

**Four floors have now been used for this comparison — 0.5034, 0.3062, 0.6458 and these — and only
these are matched on measured overlap.**

⚠ **I did NOT compute the blind-side matched floors**, so the excess comparison is *not* re-run here.
The registered scope was the curve and the actual overlap; re-scoring the verdicts needs
`greedy`↔`topw` and `indep`↔`topw` overlaps too, and that is the next step, not a claim of this one.

⚠ **And it is a RANDOM-SUBSET floor.** A constructed arm draws from the scored pool; the real arms
were produced by rules that may prefer criteria with particular satisfaction profiles. **Whether a
rule-produced arm behaves like a random subset at the same overlap is not identified here.**

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: one-parameter model, 4 held-out points, max |Δ| **0.0046** · **PLACEBO**: j=4 → raw and
floor **exactly 1.000000** · **g=0**: j=0 vs j=1 gap **+0.1642 > 3sd 0.0790** · **NEGATIVE**: shared
set drawn at random so nominal j ≠ realised j → floor range **0.0189 vs 0.5756**, excluding *"the
curve comes from the label j"* · **SHAM**: both arms from one draw → **1.0 at every j**, no
dependence on the label.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A max \|raw − model\|, held out | 0.05 [0, 1] | **0.0046** | yes |
| B floor at j=0 | 0.31 [0, 1] | **0.4244** | yes |
| C floor at j=4 | 1.00 [0, 1] | **1.0000** | yes |
| D greedy~oracle overlap | 2.0 [0, 4] | **2.8492** | yes |
| DIRECTIONAL differs from 0.6458 | — | **holds** | — |

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r737_floor_curve.json`.
