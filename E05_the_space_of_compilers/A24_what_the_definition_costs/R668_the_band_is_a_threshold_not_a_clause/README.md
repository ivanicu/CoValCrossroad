# R668 · The k-band is a THRESHOLD cutting a unimodal curve — not "a clause nobody wrote"

**Decision this makes safe:** whether the definition needs an extra clause about k. **No. ② already
says it, and my proposal to add one is retracted.**

## The admission profile, both seeds

| arm | k | admitted | seed 3531 | seed 3532 |
|---|---:|---|---:|---:|
| topw_k1 | 1 | no | 0.4300 | 0.4150 |
| topw_k2 | 2 | no | 0.7225 | 0.6850 |
| **topw_k3** | 3 | **YES** | 0.9550 | 0.9600 |
| **topw_k4** | 4 | **YES** | 0.9850 | 0.9875 |
| **topw_k6** | 6 | **YES** | **0.9975** | **0.9975** |
| **topw_k8** | 8 | **YES** | 0.9625 | 0.9375 |
| topw_k12 | 12 | no | **0.0000** | **0.0000** |

## Is the admitted set a level set?

| seed | min(P \| admitted) | max(P \| rejected) | level set | margin |
|---|---:|---:|---|---:|
| 3531 | 0.9550 | 0.7225 | **True** | **+0.2325** |
| 3532 | 0.9375 | 0.6850 | **True** | **+0.2525** |

> ⭐⭐⭐ **The admitted set IS a level set of `P_arm` at both seeds.** So the band `{3,4,6,8}` is
> exactly what a **threshold** does to a **unimodal** profile — **② already says it, and no clause
> is missing.**

⛔ **§0's arithmetic trap: I read a shape forced by thresholding as a discovery about the
definition.** The available k values are 1, 2, 3, 4, 6, 8, 12 and the admitted set is **contiguous**
in that grid — the tell was visible before any data was opened.

## ⚠ The residual, and it is real

The rise is smooth — **0.43 → 0.72 → 0.96 → 0.99 → 1.00** — while **the fall 8 → 12 is a CLIFF:
0.96 → 0.0000, at both seeds.** **A unimodal story explains the band; it does not explain a hard
zero.** That is about how `topw_k12` is built, **not about the definition.**

## Controls

| control | returned |
|---|---|
| **positive** — the profile must be non-constant (range > 0.5) | **0.998 at both seeds** — PASS |
| **negative** — a deliberately NON-level set (drop k=4, keep k=1) must fail | **0.4300 vs 0.9850 → not a level set** — PASS, *the test is not passed by any subset* |
| **placebo** — the two seeds must agree | **True, True** — PASS |

**MULTIPLICITY:** 2 seeds × 7 arms + 3 controls; the whole profile printed, both seeds, all 7 k.

## ⛔ Check #269 — the fact held, the inference did not

| claim | truth |
|---|---|
| *"`topw_k1, k2, k12` are not admitted"* | ✓ confirmed against `clause2_admits` |
| *"an unstated band is **a clause nobody wrote**"* | **False.** It is a level set of a unimodal profile — precisely what ② states. |
| *"the **first** claim in this arc that would ADD a clause"* | **Uncomputed quantifier over my own work**, and the sentence a later round would have acted on. |

⭐ **And the prior-art gate was run FIRST this time** — after three consecutive rounds in which it
was not. **It returned the answer immediately.**

**IMPOSSIBLE, named:** **why** `P_arm(k)` rises to k=6 and collapses at k=12 is about **arm
construction**, not the definition. This round settles only whether the band needs an extra clause.

## The sentence I can no longer write

> *"the definition encodes an unstated band, and an unstated band is a clause nobody wrote."*

**The band is the level set of a threshold the definition already contains.**

## NEXT

**`topw_k12` scores `P_arm = 0.0000` at both seeds — not small, exactly zero — while `topw_k8` is
0.96.** A smooth decline does not produce that, so **something disqualifies k=12 categorically**.
The pool is **16**, and k=12 is the only admitted-family arm within a factor of ~1.3 of it.
**Measure whether the zero is a pool-size interaction** — i.e. whether every arm with k > some
fraction of the pool collapses — because if it is, then the definition's apparent k-preference is
**partly an artefact of the pool it was scored against**, which is the same class of finding as
R664's *(object, baseline)* result and would extend it from the baseline to the pool.
