# R520 · ③'s provenance set is complete where it was used, and incomplete one join away

**Decision this makes safe:** whether the definition's only working clause can be trusted, and over
which population.

**Estimand:** the number of arms whose generating rule opens the human labels but which are absent
from `USES_PROMPT_LABELS` — label-readers ③ would silently admit.
**Population:** the 56 arms scored by R294 (41) or R436 at the home judge (56).
**Instrument:** the code's own conditional, read from source — **not** a keyword search.
**Baseline:** the declared literal. **Regime:** first release, home judge.

## Why not a keyword search
A grep for scripts touching the labels returned **19 of 19** — a 100% rate, which §4 already calls
an extinct recogniser. `score.py` reads labels *to score*; that is not *building criteria from*
them. **Instrument's unit: "imports load_targets". Claim's unit: "the SELECTION consumed this
prompt's labels."** Only the second is the question, and only the source gate answers it.

## The gate, read from the object
`corebench/select_core.py:102` — `data/comparisons.jsonl` is opened **only** under
`if a.rule in ("oracle_k", "indep_k", "greedy_k")`. The round re-reads that conditional at runtime
and refuses to run if it has changed.

## Result — WORLD B

| | |
|---|---|
| arms in a label-reading family | **10** |
| declared in `USES_PROMPT_LABELS` | **4** |
| ⭐ **absent from the literal** | **6** |

The six: `oracle_k4_oracle_kA`, `oracle_k4_oracle_kB`, `greedy_k4_greedy_kA`,
`greedy_k4_greedy_kB`, `indep_k4_indep_kA`, `indep_k4_indep_kB`.

⭐ **None of the six carries a ③ verdict in R294's census.** They exist only in R436's 56.
**So the literal is COMPLETE over the 41 arms it was ever applied to, and R519's result is
unaffected** — no arm it admitted could have been one of these.

## Controls — all three passed
- **Positive** — the tag→rule derivation must recover all 4 declared members from their tags alone.
  **PASS**, so an absence claim is admissible.
- **Negative** — rules the source documents as label-blind (`random_k`, `topw_k`, `topabs_k`,
  `full`; 33 arms) must not be derived as readers. **PASS**, so the derivation is not over-broad —
  which is exactly where the keyword version failed.
- **Sham** — deriving on the *satisfaction* list (5 rules) instead of the *label* list (3) must give
  a different, larger set: **12 vs 10. PASS**, so the instrument reads the label gate specifically
  and not "any rule that consumes something".

## What this changes

⚠ **The hazard is live and one join away.** R518 and R519 both joined R294's verdicts to R436's
56 arms — for ④. **Any future round that extends ③ to that same 56 would silently admit six
label-readers**, because the literal carries no record of the population it was written for.

⭐⭐⭐ **A hardcoded set is scoped to the population it was authored against, and nothing in it
records that scope.** The remedy is mechanical and demonstrated here: **derive the set from the
code's own gate rather than declaring it.** The derivation passes three controls and is 6 lines.

**Impossible here:** whether an arm's tag faithfully records the rule it was built with. That needs
the generating invocation, which the `.npz` does not carry.
