# R790 · a level is not an object — the threshold IS the definition, and my own NEXT dies to it

`run.py` · `PREREGISTRATION.txt` · `results/levels.json` · 20 distinct objects × 968 prompts ·
1,000 resamples · **WORLD B** · two hash seeds byte-identical, md5 `9041d5d0a807f2fc11d235a4199dd753`

## THE DECISION THIS MAKES SAFE

**The membership formulation R789 proposed cannot be written.** Over 1,000 cluster-bootstrap
resamples of the 968 prompts, with the partition rebuilt end-to-end in every draw,

> **`P(coval_core and generic share a level) = 0.339`** (adjacent) · **0.132** (greedy)

— **one resample in three puts the released core in the same level as the arm that never reads the
prompt.** And the level count itself takes **five** distinct values (7–11) with a modal share of only
**0.408**. A level is not stable enough to carry a definition.

## ⛔ AND THE SPECIFICATION CURVE IS THE FINDING, NOT A ROBUSTNESS CHECK

| rule | threshold on `t` | modal levels (share) | **P(core ~ generic)** | P(core ~ `topw_k4`) |
|---|---|---|---:|---:|
| point | 0 | 20 (1.000) | **0.000** | 0.000 |
| ci_only | 1.959964 | 10 (0.42–0.51) | **0.065 – 0.090** | 0.885 – 0.905 |
| **strict / mde** *(pre-registered)* | **2.801585** | 9 (0.42–0.45) | **0.310 – 0.339** | **0.970 – 0.980** |
| conservative | 4.761549 | 5 (0.34–0.41) | **0.920 – 0.955** | 1.000 |

**The probability that the released core is indistinguishable from the prompt-blind baseline runs
from 0.000 to 0.955 across four defensible thresholds on the same data.** Nothing about the arms
changed; only where the line was drawn. Three seeds per cell, all twelve cells published.

## ⛔ THE RELATION IS NOT TRANSITIVE — MEASURED, AND IT COULD HAVE COME OUT ZERO

| rule | intransitive chains | of | rate |
|---|---:|---:|---:|
| point | **0** | 0 | — |
| ci_only | **23** | 146 | 15.8% |
| strict / mde | **16** | 202 | 7.9% |
| conservative | **16** | 253 | 6.3% |

`a ~ b` and `b ~ c` but `a ≁ c` happens at every rule that resolves anything. **D1: a non-transitive
relation induces no partition**, so grouping requires a tie-break from outside the relation — which
is why R789 had to report two constructions and why they disagree (9 versus 10 levels, and
`P(core ~ generic)` 0.339 versus 0.132). *The two constructions were not a reporting choice; they
were forced, and I did not know that when I reported them.*

## E4 · THE FORMULATION, WRITTEN OUT AND THEN PRICED

*"A core is admissible iff it is strictly above the prompt-blind baseline's level."* `generic` sits
in level **3 of 9**.

| | |
|---|---|
| ADMITS | **8 classes = 14 named arms** — `coval_core`, all three `topw_k4` variants, `indep_k4_*`, `greedy_k4_*`, `oracle_k4_*` |
| EXCLUDES | **12 classes = 13 named arms** — every sham, every random, **`generic` and `generic_reprov`**, `gen`, `genericpool16`, `topabs_k4`, `topvar_k4`, `topwvar_k4` |
| **the same admitted set is returned in** | **0.640 of 300 resamples** |

⚠ **The representatives are not the population.** `topw_k4_detB` is the union-find representative of
`{topw_k4, topw_k4_detA, topw_k4_detB}`; printing reps alone would read as though the other two were
excluded. Both counts are now emitted by `run.py`, and 14 named arms matches R789's cut-based count
exactly.

**§4's remedy applied**: the clause excludes 13 named arms, including every sham and every random —
so it is not decoration. But it admits **every target-reading arm** and cannot separate `coval_core`
from `topw_k4` (**P = 0.975**), so what it certifies is a band, not the core.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 27 named arms → 9 alias pairs → **20 distinct objects**, 190 pairs; worst \|t − R789's committed t\| **1.066e-14** | PASS, else exit 2 |
| PLACEBO | the 9 alias pairs: P(same level) **exactly 1.000**, min and max | PASS — expected value fixed by D4 *before* the run |
| POSITIVE | δ=0 **0.990** · 0.005 0.955 · 0.01 0.755 · 0.02 0.110 · 0.05 **0.000** | band admissible; see the repair below |
| NEGATIVE | synthetic matched-spread arms: level count 3:0.053 4:0.373 **5:0.427** 6:0.137 7:0.007 8:0.003 — mode **5** against the real **9** | **DIFFERS** → World C does not fire |
| SHAM | equal-width bins at the same level count: adjusted Rand **0.7798** | ⚠ see below |
| NOISE FLOOR | the bootstrap level-count distribution itself, reported whole | — |

### ⛔ MY PRE-REGISTERED POSITIVE CRITERION FAILED, AND IT WAS THE CRITERION THAT WAS WRONG

I registered `floor == 1.000` at δ=0. It returned **0.990** and therefore **FAILED**. The arithmetic
that condemns the criterion needs no data: at δ=0 the planted copy is the original **plus zero-mean
noise**, so the two arms are genuinely different vectors and the rule separates them at its own
two-sided false-positive rate `α = 2(1 − Φ(2.801585)) = 0.005085`. Over 200 draws,
`P(floor == 1.000 | the instrument is correct) = 0.361` — **a 64% false-failure rate by
construction.** §4's *the control fails for its own reasons*. Repaired against its own binomial null,
a criterion derivable without seeing the result: `|floor − 0.99491| ≤ 3 sd = 0.01509`; observed
**−0.00491** → **PASS**. The original failure is recorded rather than quietly relaxed.

### ⚠ AND THE SHAM IS A CAVEAT ON HOW MUCH THE MACHINERY ADDS

Adjusted Rand **0.7798** between the real partition and plain equal-width binning of A2 at the same
level count. That is not World C — the NEGATIVE's synthetic level-count distribution (mode 5)
differs sharply from the real one (mode 9) — but **most of what the resolution test produces is
recoverable from the A2 spacing alone**, and a formulation resting on levels is resting largely on
where 20 numbers happen to sit.

## MULTIPLICITY

**190 unordered pairs** among the 20 distinct objects — not 351: the 9 alias pairs are the placebo,
not tests. The full co-level probability matrix (all 190 entries, both constructions) is in
`results/levels.json`. Bootstrap resolution is **1/1000**, so probabilities of 0 are reported as
`< 0.001` and never as zero. Level counts are published as distributions, never as means.

## WHAT DIED

- **R789's NEXT, in full** — "write clause ② as a membership claim" is not available: membership
  rests on levels, levels rest on a threshold, and the threshold moves `P(core ~ generic)` from
  0.000 to 0.955.
- **the two constructions as a stylistic choice** — D1 shows they are forced by intransitivity, and
  they disagree by a factor of 2.6 on this round's decisive probability.
- **my own POSITIVE control's criterion**, which had a 64% false-failure rate by construction.
- **a guard that skipped instead of failing** — `if a in ri and b in ri` silently omitted
  `P(core ~ generic)` from the first run's output, which is the one number the round exists for.

## WHAT SURVIVES

R789's point-estimate partition, exactly reproduced (worst `t` delta 1.066e-14), and its reading
that `coval_core` cannot be ordered against `topw_k4` — now strengthened from a single `t` of 0.75 to
**P(same level) = 0.975 over 1,000 resamples**. And the clause does exclude every sham and every
random arm, at 0.640 set-level stability.

## SCOPE

population 20 distinct objects (27 named arms, 9 alias pairs collapsed) × 968 prompts · instrument
A2 per prompt over all annotators, `t = eff/se` on the paired difference · baseline R789's committed
point-estimate partition · regime first release, home judge · B = 1,000 for the headline, 200–300 in
the specification and control cells, 3 seeds.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether the levels are the RIGHT grouping | an external criterion for what clause ② should admit — the construct-validity wall (R631) |
| a partition that is not construction-dependent | a transitive resolution relation, which this data does not supply (E1) |
| independently replicated | a second designer; the session prompt forbids agents |
| levels for arms outside modal-k=4 | their own comparator class and sat files |

## NEXT

Three formulations have now failed for the same reason, and the reason is not the statistic. `q`
(R787) is A2's percentile; `q_resolved` (R788) adds a variance term worth 0.235; a stated cut (R789)
forfeits the pairing; and a level (R790) moves `P(core ~ generic)` from 0.000 to 0.955 with the
threshold. Computed by this round's `run.py`, every one of those is a **threshold on a single
scalar**, and the released core's position on that scalar is `t` 0.75 from `topw_k4`. So the next
question is not where to put the line — it is whether clause ② should be a scalar comparison at all,
or whether the definition needs a quantity on which the core and `topw_k4` are **not** 0.75 apart.
That is a question about the *estimand*, and it is the first one this arc has asked that no
re-threshold can answer.
