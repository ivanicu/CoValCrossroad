# R804 · the human ceiling is not a ceiling — it is the k=1 point, and the real one is 0.6863

`run.py` · `PREREGISTRATION.txt` · `results/ceiling.json` · 968 prompts × 4 responses × all
annotators × 27 arms × 75 weak orders · **WORLD A** · two hash seeds byte-identical, md5
`96ea69bc250a82f5588ebd1f1d56b2ee`

## THE DECISION THIS MAKES SAFE

**R803's closing worry — that 14 arms score "above the human self-agreement ceiling" — was a units
error, and the number it rested on was never a ceiling.**

`whose_verdicts.py:65` computes `CEIL_H` as `a2(annotator_i, annotator_j)`: **noise on both sides**.
An arm is a deterministic predictor scored against each annotator: **noise on one side**. A noiseless
predictor of the human central tendency beats pair-agreement by construction.

| | A2 | what it is |
|---|---:|---|
| judge-free floor (R803) | 0.4557 | response length |
| **`CEIL_H`** | **0.551880** | **one annotator predicting another — the k=1 point** |
| best arm `oracle_k4` | 0.6283 | |
| **`CEIL_HO`** | **0.633370** | ⭐ **the generalising ceiling** — best weak order fitted on half the annotators, scored on the other half |
| **`CEIL_ATT`** | **0.686265** | ⭐ **the exact in-sample supremum over ALL scoring functions** |

**Calling 0.5519 a ceiling understated the attainable maximum by 0.134.**

## ⭐ E1 · THE CEILING IS EXACTLY COMPUTABLE, NOT ESTIMATED

Four responses admit **75 weak orders** (the ordered Bell number `a(4) = 75`), and every scoring
function induces one. So the supremum of A2 is a per-prompt brute-force max — no model, no sampling.

| | |
|---|---:|
| `CEIL_ATT` — max over all 75 weak orders, per prompt | **0.686265** |
| `CEIL_PLUR` — per-pair plurality, transitivity ignored (an upper bound) | 0.686701 |
| **D3 · the cost of human INTRANSITIVITY** | **+0.000436** |

⭐ **The human plurality is very nearly transitive**: allowing an incoherent predictor that answers
each pair separately buys **0.0004**. Nobody had measured this.

## ⛔ AND THE FORCED CHECK, WHICH IS A DERIVATION AND NEVER EVIDENCE

Every arm is a scoring function, so `arm_A2 ≤ CEIL_ATT` is **algebra, not a result**. It is run as a
**code check**: 27 arms, **0 violations**. Had one exceeded it, the round's own arithmetic would be
wrong. Reporting "no arm beats the ceiling" as a finding would be the arithmetic trap.

## ⭐ E2 · WHERE THE ARMS ACTUALLY SIT

| arm | A2 | % of the in-sample range | ⭐ % of the **generalising** range | headroom to `CEIL_HO` |
|---|---:|---:|---:|---:|
| `oracle_k4` | 0.6283 | 74.9% | **97.1%** | +0.0051 |
| `greedy_k4_greedy_kA` | 0.6226 | 72.4% | 94.0% | +0.0107 |
| `coval_core` | 0.5665 | 48.0% | **62.4%** | +0.0669 |
| `generic` | 0.5514 | 41.5% | 53.8% | +0.0820 |
| `genericpool16` | 0.5422 | 37.5% | 48.7% | +0.0911 |
| `gen_sham` | 0.4828 | 11.8% | 15.3% | +0.1506 |

**14 of 27 arms sit above `CEIL_H`; 0 above `CEIL_ATT` (forced).** Headroom to the exact ceiling is
resolved for every arm and **27 of 27 survive BH** — i.e. **no arm is at the ceiling**, `oracle_k4`
included, whose headroom is **+0.0580 [+0.0529, +0.0633]**.

⚠ `oracle_k4` reaching 97.1% of the generalising range is **not** a benchmark result: it is an
ORACLE arm, selected using the humans it is scored against. The honest reading is the released one —
**`coval_core` captures 62.4% of the range a generalising predictor could capture.**

## ⛔ E3 · MY OWN PRE-REGISTERED DIAGNOSTIC FIRED AND BLOCKED THE HEADLINE STATISTIC

I wanted to report each arm in **annotator-equivalents**. D4 required the k-consensus curve to be
monotone. **It is not, under either estimator, so no equivalent is quoted.**

| k | sign-sum consensus | ⭐ mean-score consensus |
|---:|---:|---:|
| 1 | 0.551055 | 0.551055 ± 0.005372 |
| 2 | **0.505779** | 0.550943 ± 0.003903 |
| 3 | 0.590465 | 0.584223 ± 0.004008 |
| 4 | 0.578880 | 0.597517 ± 0.003815 |
| 6 | 0.605877 | 0.614237 ± 0.002787 |
| 8 | 0.616671 | 0.620795 ± 0.001683 |
| 12 | 0.621461 | 0.624963 ± 0.002755 |

**The sign-sum estimator saws on parity**: `sign(Σ signs)` TIES whenever k annotators split evenly,
and a tie can never match a strict held-out sign, so even k is penalised — 0.5511 / 0.5058 / 0.5905 /
0.5789. Switching to a real scoring function (`cls` of the mean y-vector, which is what every arm
is) removes almost all of it: the only remaining violation is **−0.000112 at k=2, against a k=1 sd of
0.005372**, i.e. **1/48 of its own noise**. ⚠ The pre-registration still binds — **no equivalents are
quoted** — but the magnitude is reported so the reader is not left thinking the curve is broken.

⭐ **The pre-registered estimand survived the unfit method.** What was registered is *"does a k ≤ 3
consensus beat `CEIL_H`"*; `equiv()` was one implementation of it, and interpolation needs
monotonicity. The estimand itself does not: a **3-annotator consensus scores 0.584223 against
`CEIL_H` 0.551880 — it beats it directly**, no interpolation involved. Substituting a direct
evaluation of the same estimand is a repair; changing the estimand would have been a moved goalpost.

⚠ **And `CEIL_H` landing at k=1 (0.551880 vs 0.551055, |Δ| 0.000826) is FORCED, not discovered** —
both are "a random annotator predicting another annotator". It functions as a **positive control on
the curve**, and is labelled as such rather than quoted as a finding.

## ⭐ E5 · THE ORACLE CEILING IS IN-SAMPLE, AND SAYING SO COSTS 0.0529

`CEIL_ATT` picks each prompt's best weak order **after seeing that prompt's annotators**, so no
predictor that must generalise can reach it.

> `CEIL_ATT` **0.686265** · `CEIL_HO` **0.633370** · **optimism +0.052895**

Both are reported. Quoting only `CEIL_ATT` would flatter every arm by understating its share of the
achievable range — `coval_core` moves 48.0% → **62.4%** when the ceiling is made honest.

## ⭐ E4 · THE TIE STRUCTURE, WHICH R803 ASKED ABOUT

R803 found a constant predictor banks **0.1397** from ties alone. Does the arms' advantage live there?

| | best arm | one annotator |
|---|---:|---:|
| on human-**TIED** pairs | **0.0186** | 0.2182 |
| on human-**STRICT** pairs | **0.7220** | 0.5875 |

**No — the opposite.** A strict predictor almost never agrees on a tied pair (0.0186), so it
**forfeits the tie mass outright**, and still wins: its advantage on strictly-ordered pairs alone is
**+0.1346**. D2 holds, and World C is dead.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `CEIL_H` reproduced by **R793's own method** (`R793/run.py:174-183`, exhaustive over all annotator pairs): **0.551880** vs committed **0.551880** | PASS, else exit 2 |
| PLACEBO | constant predictor (all ties) **0.1397355039** vs human tie rate **0.1397355039** | PASS — derived, not fitted |
| POSITIVE | one annotator used as a predictor: **0.555874** vs `CEIL_H` **0.551880**; band computed at both ends **0.1397 < t < 0.6863** | PASS |
| NEGATIVE | each annotator slot filled from a **different prompt**: **0.686265 → 0.527548** (best single constant weak order corpus-wide **0.451773**) | PASS **after repair** |
| NOISE FLOOR | annotator split-half on `CEIL_ATT`, 20 draws: sd **0.001991** | every headroom is ≫ 25× it |

## ⛔ TWO OF MY OWN INSTRUMENTS WERE BROKEN, AND BOTH ANNOUNCED THEMSELVES

- **The object check exited 2 on a silent Python defect.** `score.cls` returns a **tuple**, so
  `np.mean(cls(a) == cls(b))` compares two tuples as objects — one scalar `False` — and returns
  **0.083488** where the truth was 0.5519. It reads as a measurement. Swept the arc: every other use
  is `float(tuple == tuple)`, an **exact-match indicator**, which is those rounds' intended
  semantics — **no committed number is contaminated**.
- **The first NEGATIVE control could not fail.** It permuted *which prompt* an annotator-set attached
  to. `CEIL_ATT` is a **per-prompt max**, so that permutes the multiset of per-prompt values and
  leaves the mean **exactly** invariant — measured, **0.686265 → 0.686265**. `CEIL_ATT` has no
  cross-prompt structure to destroy; what it measures is **within-prompt annotator concentration**,
  and that is what the repaired control breaks.

⚠ **And a third, in the artifact under audit**: `whose_verdicts.py`'s shipped sampled ceiling is
**0.551251** (sorted) / **0.546143** (dict-insertion order) — **dict-order dependent, and neither
equals the committed 0.551880**, which came from the exhaustive method. R793 showed this constant
decides WORLD A vs WORLD B; the shipped version of it moves with iteration order.

## MULTIPLICITY

**27 arm-vs-ceiling tests**, BH q = 0.05: **27 survive, 0 do not.** The two ceilings and the seven k
values are reported as complete curves, not as selected cells.

## WHAT DIED

- **"several arms score above the human ceiling"** — they score above **one annotator**, which a
  deterministic predictor of the central tendency does by construction.
- **World C** — the excess is not the tie structure; strict predictors forfeit the tie mass and win
  anyway.
- **my annotator-equivalents statistic** — killed by my own D4 before it was quoted.

## WHAT SURVIVES — AND THIS ROUND ADDS

An A2 axis with **both ends nailed down**: judge-free floor **0.4557** (R803), exact supremum
**0.686265**, generalising ceiling **0.633370**. Every committed number in this arc can now be read
as a fraction of what is achievable — and `coval_core`'s 0.5665 is **62.4%** of it.

## SCOPE

968 prompts × 4 responses × all annotators (median 16) × 27 named arms (20 distinct objects) × 75
weak orders · instrument A2, identical to every prior round · paired bootstrap over prompts, NBOOT
1,200 · first release, home judge · `CEIL_HO` and the k-curve resampled 8/16 draws over annotator
splits.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| the same ceiling on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances; `sat_*.npz` are keyed to release one — **checked** |
| an exact ceiling for >4 responses | the ordered Bell number grows 75 → 541 → 4,683; the release ships exactly 4, so the brute force is exact **here** and not in general |
| whether A2 is the right instrument | an external gold standard for what a core should preserve — `corebench/score.py:34`'s open register |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The axis now has both ends. Computed by this round's `run.py`, the released `coval_core` captures
**62.4%** of the generalising range and the blind `genericpool16` **48.7%**, while the two oracle
arms reach 94–97% — and an oracle arm is selected on the humans it is scored against, so that gap is
a **selection** gap, not a knowledge gap. The step is to price it: **re-run the oracle selection
under cross-validation over prompts** — select the k=4 subset on one fold, score it on the held-out
fold — which converts "the oracle reaches 97%" into "a selector that must generalise reaches X%",
and X is the number the definition's clause ② should be written against. That is one selection
experiment on an existing arm, needs no judge pass, and its outcome is not forced: if X collapses to
`genericpool16`'s 48.7%, prompt-specific selection buys nothing and the clause must say so.
