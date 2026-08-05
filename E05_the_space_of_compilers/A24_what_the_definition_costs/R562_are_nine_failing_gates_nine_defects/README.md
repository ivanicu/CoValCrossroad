# R562 · UNVERIFIED — the grouping instrument sees a third of its population

**Decision this makes safe:** none yet. **That is the result.**

**Question:** are the nine failing gates nine defects, or one defect seen from nine angles?

**Answer: UNVERIFIED.** **6 of 9 gates name no concrete object** — no round id, no path — so the
grouping could only see **3 of 9**. **A disjointness verdict over a third of the population is not a
measurement.**

| gate | rc | objects named |
|---|---|---|
| `arm_population_is_derived` | 1 | 1 |
| `artifacts_are_internally_coherent` | 1 | 3 |
| `corrections_propagated` | **0** | 1 |
| `attack_scope_reaches_the_reader` | **0** | 0 |
| `attack_every_check` · `attack_outcome_variable_declared` · `every_round_reaches_the_readme` · `outcome_variable_declared` · `seed_filter_is_disclosed` | 1 | **0** |

## ⛔ My verdict string ignored its own control
The first version branched **only** on `max_share` and printed **"WORLD A — nine defects"** while
the positive control's own words sat on the screen above it: *6 of 9 name no object*. **§4's
verdict-string failure, committed inside the round about reading failures properly.** The branch now
references every control the round declared, and returns **UNVERIFIED** when the control is partial.

## ⚠ The count of nine is itself unstable
`attack_scope_reaches_the_reader` and `corrections_propagated` return **rc=0 standalone** but were
**FAIL under `run_all`**. **So "nine failing gates" is a number that depends on how they were
invoked** — and R561 reported it without checking that.

## Controls
- **Positive** — every gate must name ≥1 concrete object. **PARTIAL: 6 of 9 name none.** This is
  what forces UNVERIFIED rather than a disjointness claim.
- **Negative** — an invented R-id appears in no gate's output. **PASS.**

**What would resolve it:** the six silent gates must be made to **name what they flag**. A gate that
reports a failure without naming its object cannot be triaged, deduplicated, or fixed.
