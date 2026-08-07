# R979 · clause ③ orders arms identically to clause ② everywhere the design can tell them apart

**THE DECISION THIS MAKES SAFE.** Whether clause ③ can ever be checked from an artifact. It cannot —
so ③ is **irreducibly a provenance requirement**, and applying the definition to a core whose
production is unknown stays unsupported. That closes the question rather than deferring it.

---

## The unit R920 used was wrong for the job

R920 settled world C on **`R² = 0.998412`** regressing `pi` on the A2 margin. **R² is a magnitude
statistic, and a clause admits by ORDERING.** Two quantities can agree in magnitude to four nines and
still disagree about which of two arms is above the other — and that disagreement is the only thing
that would give ③ independent content. R922 already owns the right instrument: it settled clause ②
by counting **inversions**. Nobody had pointed it at ③.

## The result

| | |
|---|---|
| pairs enumerated | **78** (all reported) |
| inverted between `pi` and the A2 margin | **2** |
| of those, resolvable on A2 | **0** |

The two inversions, named:

| pair | A2 gap | resolvable (3 seeds) |
|---|---|---|
| `random_k4_s2` vs `random_k4_s0` | −0.00427 | False · False · False |
| `random_k4_s2` vs `topabs_k4` | −0.00097 | False · False · False |

Both gaps sit far inside the design's own committed resolution of **0.0099555**, and an 8000-draw
paired bootstrap confirms non-resolvability at every seed. **Clause ③ never reorders a pair this
design can order.**

## ⚠ R920's n is 13, not 21 — and the correction does NOT change its conclusion

Measured from its own artifact, the 21 rows collapse to **13 distinct `(pi, mean_a2)` points** across
**6 duplicate clusters** — `oracle_k4`, `oracle_k4_oracle_kA` and `oracle_k4_oracle_kB` are identical
to twelve decimals. The labelled side is **6** independent units, not 10; the label-blind side **7**,
not 11.

⭐ **My first guess was that the duplication inflated R². Measured, it does not:**

| | rows (21) | units (13) |
|---|---|---|
| R² | 0.998412 | **0.998205** |
| Spearman ρ | 0.992208 | **0.983516** |

So the correction is to the `n` any later round must quote, **not** to R920's finding. Recorded
because a guess that fails is worth the same as one that lands, and the flattering version of this
round would have been "I found an n_eff error that overturns a headline."

## Controls

| control | result |
|---|---|
| **POSITIVE** | `pi` shuffled → median **38** inversions against a random expectation of **39**. The instrument can see inversions; a 0 from it is a measurement, not silence |
| **NEGATIVE** | `pi` against itself → **0** inversions |
| **NOISE FLOOR** | resolvability measured per pair by bootstrap CI, not assumed from the committed resolution number |
| **SEEDS** | 3, reported per pair, never averaged — all three agree on both pairs |

## What this cannot say

- **`pi`'s own sampling error is not available.** R920's artifact carries point values only, and
  recomputing `pi` needs its 2000-subset sampler. Pairs are called unresolvable **on the A2 side
  only** — a conservative direction, since adding pi's noise can only move pairs *into* unresolvable,
  never out. So `0 resolvable` is an upper bound on ③'s ordering content, which is the safe side.
- **It does not retire clause ③.** R920 established ③ is a provenance claim; this shows the same
  thing in the unit the clause actually operates in. A provenance requirement is unaffected by an
  artifact-level result — it is simply not checkable there, and now that is measured rather than
  argued.
- **One release, one k (=4).** Whether ③ acquires ordering content at other k is untested.

## Where the three clauses now stand

| clause | what it turns out to be |
|---|---|
| ② the bar | a resolvable beat; its extension moves with N (R978) |
| ③ no prompt-specific labels | **no artifact-level ordering content — provenance only** (here) |
| ④ beats every response-only rule | overlap-limited, and its bar is design resolution (R975, R976) |

## Alternatives considered

**Re-run R920's sampler to get `pi`'s CI and call pairs unresolvable on both sides.** Deferred: it
would only *shrink* the resolvable set, which is already 0, so it cannot change this verdict. It
becomes necessary the moment someone reports a **non-zero** resolvable count.

**Report Spearman ρ = 0.9835 as the headline.** Refused — ρ is another magnitude summary of an
ordering. The admission-relevant quantity is *which* pairs invert and whether the design can order
them, and that is a named list of two.
