# R522 · The six candidacies are verdicts — all clear ②, and the wall was false again

**Decision this makes safe:** whether ③'s hardcoded literal must be replaced before the population
widens, at full interval-verdict strength rather than as a point comparison.

## ⛔ First — the wall, tested before anything else

`426a409` closed with *"the honest way to close them is to compute the blind-pool contrast for the
15 arms that lack one, and that cost is the thing to measure."* **All six saturation matrices are
on disk.** R294's own contrast machinery re-runs on them directly — **no scoring, only reanalysis.**
**Third false "needs new computation" wall this session**, after `469a8b9`.

## Result — WORLD B, 6 of 6 BEATS

| arm | k | n | c2 | 95% CI | MDE | verdict |
|---|---|---|---|---|---|---|
| `oracle_k4_oracle_kA` | 4 | 968 | **+0.0779** | [+0.0701, +0.0853] | 0.0107 | **BEATS** |
| `oracle_k4_oracle_kB` | 4 | 968 | **+0.0779** | [+0.0701, +0.0853] | 0.0107 | **BEATS** |
| `greedy_k4_greedy_kA` | 4 | 968 | +0.0722 | [+0.0643, +0.0797] | 0.0105 | **BEATS** |
| `greedy_k4_greedy_kB` | 4 | 968 | +0.0722 | [+0.0643, +0.0797] | 0.0105 | **BEATS** |
| `indep_k4_indep_kA` | 4 | 968 | +0.0527 | [+0.0447, +0.0600] | 0.0104 | **BEATS** |
| `indep_k4_indep_kB` | 4 | 968 | +0.0527 | [+0.0447, +0.0600] | 0.0104 | **BEATS** |

Pre-registered kill: <4 BEATS weakens to a bound, 0 retracts R521. **6 of 6.**

⭐ `oracle_k4_oracle_kA`'s c2 is **+0.0779**, matching `oracle_k4`'s stored **+0.077867** — the
doubled-tag arms behave as the same object, which is consistent with them being oracle-family.

## Controls
- **Positive** ×5 — the reconstruction must reproduce R294's stored `c2` to 1e-6:
  `coval_core`, `topw_k4`, `gen`, `generic`, `oracle_k4` all at **Δ = 0.00e+00**. **5 of 5.**
- **Negative** — an arm against itself: effect **+0.000000**, CI **[+0.000000, +0.000000]**.
  The estimator manufactures nothing where the two sides are one object.
- **Multiplicity** — 6 new cells alongside the census's 41, BH over C = 47.

## What it settles

**R521's "candidacies" are verdicts.** Under the declared literal, extending the definition to the
56-arm population admits **six label-reading arms that BEAT ②**, four of which outscore every
currently-admitted arm. Under the derived gate, all six are excluded.

⭐⭐⭐ **So the fix is not hygiene — it is the difference between a leaderboard topped by cores and
one topped by arms that read the answer.** The replacement is six lines and passed three controls
in R520.

**Impossible here:** ③ for these arms by any route other than the code gate. Their construction is
in this repository, so the gate *is* the evidence, and R520 read it.
