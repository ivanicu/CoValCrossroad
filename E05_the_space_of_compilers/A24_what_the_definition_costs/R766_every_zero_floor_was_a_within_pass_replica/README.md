# R766 · the discrepancy is a systematic offset, the floor is still unmeasured, and the whole thread is decision-inert

**`share(generic > pool) = 0.1793`, far outside the registered symmetric band [0.40, 0.60], so the
957-prompt discrepancy is **a judge or setting difference, not run-to-run variance** — **WORLD B**.
⇒ **The across-pass scoring floor remains UNMEASURED at this site**, which is not the same as zero
and not the same as R419's and R765's zeros being wrong. ⭐ And the question is **decision-inert**:
the comparator's percentile is **93.74** recomputed, **[91.59, 96.59]** under the measured
discrepancy — R527's committed **93.7** sits inside it, so ② does not move.**

## check #368 — three hypotheses killed before any round was built, all for free

| hypothesis | killed by | cost |
|---|---|---|
| **the pool tensor's column order ≠ the core JSON's list order** *(R765's NEXT)* | `score.py:58` stores `int(i)`, so `sorted()` is **numeric**; `idxs[0:4] == [0,1,2,3]` | one `sed` |
| **satisfaction depends on the co-scored set** | the nested `topw_k{1,2,3,4,6,8,12}` family gives a shared criterion **the same value to 9 decimals at every k** | one loop |
| **the anchor test can name `generic`'s judge** | its criteria appear in **no** full table, so the positive control (`topw_k4` vs `sat_full`) returns **0.1087**, near the ~0.03 coincidence floor. **The instrument is inadmissible here** *(P5's ★ rule)* | one census |

**R765's NEXT was wrong about the mechanism, and the attack ladder found that in three commands.**

## ⭐ E1 · the discrepancy, at the cell level

15,488 cells (968 prompts × 4 criteria × 4 responses), identical criterion strings, same indices,
same letters.

| | |
|---|---|
| differing **cells** | **5,235 / 15,488 = 0.3380** |
| differing **prompts** | **957 / 968** |
| \|Δ\| mean · median · p95 · max | **0.008574** · **0.000000** · 0.030967 · 0.062419 |
| **signed mean** | **+0.000613** |
| **share(`generic` > `pool`)** | ⚠ **0.1793** — registered band [0.40, 0.60] |

**Two thirds of cells are exact and the rest are lopsided**: when they differ, `pool` is higher 82%
of the time while the signed mean is near zero. That is the signature of a **systematic offset**, not
of symmetric run-to-run noise, and the registered confound is what caught it *(ledger 1077)*.

## controls — 4 PASS, and the SHAM says the comparison is genuinely about scoring

| control | returned |
|---|---|
| **POSITIVE** | nested `topw_k` sweep, one criterion across k = 1…12: worst spread **0.000e+00**. Band: an all-different instrument fails this, an all-same one fails NEGATIVE — unreachable from either end |
| **g=0** | `sat_generic` vs itself: **0** differing of 15,488 |
| **NEGATIVE** | two *different* criteria differ on **0.9287** of cells — the values are not so coarse that anything matches anything |
| **PLACEBO** | `topw_k4` vs `_detA` **at the cell level**: **0** differing of 15,488 |
| **SHAM** | `generic` vs `gen` (criteria not identical, overlap 0.0010): \|Δ\| mean **0.190755** vs **0.008574**. **Criterion identity buys 95.5%** — E1 is about scoring, not about criteria |

## ⛔ what this re-scopes, and what it does NOT retract

**R765 published** *"same judge, identical criteria → \|Δ A2\| = 0.0000 on 10 pairs"* as the scoring
floor. Of the **48** identical-criteria pairs in the release, **16 carry a replication marker**
(`_det`, `_ctl`, `_kA`, `_kB` — determinism controls, or the same object under R730). **A pair built
to be identical cannot measure whether scoring is identical**: §4's first row, published as a finding
*(ledger 1078)*.

**And R419 published the same zero long before** — *"the scoring-only floor is exactly zero, two runs
of identical criteria bitwise identical on all 200 prompts"*. **P4 did not find it**, because I
searched for overlap and Jaccard rounds and not for the thing I was about to measure *(ledger 1079)*.

⚠ **But neither zero is OVERTURNED.** The placebo confirms cell-level determinism on a replay pair,
which is exactly what those rounds measured and exactly what their names say. What is true is
narrower and worth stating plainly: **within-pass determinism is established; the across-pass floor
has never been measured, and this round could not measure it either**, because its one candidate pair
turns out to differ by setting. `UNVERIFIED`, not an acquittal and not a retraction.

## ⭐ E3 · and the whole thread does not move a decision

| | percentile of `POOL[0:4]` in its own 1,820-subset class |
|---|---|
| committed *(R527)* | **93.7** |
| recomputed here | **93.74** |
| perturbed ×200 at the measured discrepancy *(sd = 0.012816)* | **94.16 [91.59, 96.59]** |

**The point sits inside the interval.** ② is defined against this comparator, so a discrepancy that
cannot move its percentile cannot move any ② verdict. **This thread — R415 → R419 → R765 → R766 —
is decision-inert for the deliverable**, and saying so is the round's most useful output *(§0.2)*.

## ⛔ this round is CLOSURE, and is labelled CLOSURE

It protects two existing conclusions by narrowing their scope and closes a thread. It opens no world.
Billing a scope correction as a discovery is exactly what §0.2 forbids.

## the sentence I can no longer write

*"the scoring-only floor is zero."* Within a pass it is; **across passes nothing here can say**, and
the one pair that looked like it could differs by setting instead.

## NEXT

The floor thread is closed as decision-inert, so the gradient goes back to the clause. R764 left
③-any non-empty at exactly one cell — `gen` at the class minimum, pool-overlap 0.0010 — and **R766's
SHAM just measured what `gen` is**: its satisfaction values differ from `generic`'s by \|Δ\| mean
**0.19**, twenty-two times the identical-criteria discrepancy, so it is a genuinely different
generator and not a relabelled comparator. What has never been asked is whether `gen` clears ②
**resolvedly** at p000 or merely on the point estimate — R764 recorded the admission, and R765's D1
showed that for the comparator the admission was algebra. The registered quantity is `gen`'s ② verdict
at p000 with its own CI and MDE, against the same estimator, because a single-cell extension resting
on an unresolved comparison is the same defect this campaign has now found four times.
