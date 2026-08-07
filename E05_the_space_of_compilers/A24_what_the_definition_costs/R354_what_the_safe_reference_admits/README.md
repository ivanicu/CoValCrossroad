# R354 — at the campaign's own safe reference, the definition admits two

**The decision this makes safe:** *may the page keep printing five?* **Only by also printing the
reference it depends on.** At the p99 reference R331 argued for, the definition admits **two**.

## Result — `W2_RULE_IS_EXPENSIVE`. All three controls PASS.

| percentile | ref level (k=4) | \|admitted\| | set |
|---:|---:|---:|---|
| 50 | 0.5391 | **7** | + `generic`, `topw_k2` |
| 75 | 0.5446 | 5 | |
| 90 | 0.5490 | 5 | |
| **93.7** | **0.5504** | **5** | **← the published reference** |
| 95 | 0.5511 | 5 | |
| **99** | **0.5545** | **2** | **`coval_core`, `topw_k6`** |

**The published reference is not where the collapse happens.** The set is flat at five across
**p75 → p95** — a wide, stable band. It falls to two only at **p99**, the level R331 derived.

## Why p99 and not p94

R331's argument, in its own words: every one of the 1,820 k=4 subsets **never reads the
conversation**, so each is a **member of clause ②'s own reference class** — and *a reference that
admits any of them is refuted by clause ②'s own words.* Its ideal blind-admission rate is **0**.

| reference | percentile | blind sets that clear it |
|---|---:|---:|
| **R294 first-4** (published) | 93.7 | **3** |
| p95 | 94.9 | 6 |
| **p99** | 99.0 | **0** |

So the choice between p94 and p99 is not a taste call: **p94 admits three members of the class the
clause defines itself against.** The campaign made that argument and then never evaluated the
reference it recommends.

## Controls

| | returned |
|---|---|
| **REPRODUCTION** | the census's own reference yields **exactly** R294's committed five |
| **R331 CROSS-CHECK** | p99 level at k=4 = **0.5545** (R331: 0.5547); blind sets **resolvably** better = **0** (R331: 0) |
| **MONOTONICITY** | the set shrinks as the reference strengthens |

### ⛔ The cross-check failed first, on a tautology

v1 counted blind subsets scoring **numerically above** the reference and got **19** where R331
committed **0**. **Nineteen is arithmetically forced** — the 99th percentile of 1,820 values has ~18
above it *by definition*. The control was computing a tautology and comparing it to a measurement.

R331's predicate, read from its source rather than its prose — `(e > 0) & (|e| >= mde)` — is
**resolvably** better. Corrected, it returns 0 and both numbers are printed, the forced one labelled.

*And R331's own summary line looked self-contradictory: "the best of 1,820 blind sets beats the
reference by 0.66 MDE, below resolution" beside a table saying that reference admits 3. Both are
right — 0.0106 is a **typical** per-cell MDE, and the three that clear have their own smaller ones.
A typical-MDE summary cannot decide individual cells.*

## ⭐ The prediction I revised mid-run was right on both halves

| | `coval_core` at p99 | set size |
|---|---|---|
| original — from a uniform-shift **screen** | excluded | ≤ 2 |
| revised — from R353's **measured** inclusion probabilities | **survives** | collapses |
| **measured** | **survives** | **5 → 2** |

**The screen was wrong; the measurement I already owned was right.** R353 had been committed an hour
before R354 was designed, and I wrote the first prediction without opening it.

## Reconciling with R353

R353 permuted the **whole pool**, so the k=6 and k=8 references moved *independently* of the k=4 one
— 24–25 distinct admitted sets. Here every k is held at the **same percentile**, so the references
move together and the picture is far more orderly. **Different objects, both real**: the first asks
what an arbitrary file order does, the second what a stated rule does.

## Register

| criterion | status |
|---|---|
| k ≤ 8 | arms with larger k are not admitted even at the weakest reference — stated, not silently applied |
| percentiles | on **one fixed** prompt population so levels are comparable across k; each arm's contrast keeps its own population, as the census does |
| clauses ① and ③ | taken from the census unchanged. They do not depend on the clause-② reference, so they cannot bias this curve — but they are not re-derived here |

## The sentence I can no longer write

> *"the definition admits five."*

**It admits five across p75–p95, and two at the reference this campaign's own safety argument
requires.**

Artifact: `results/r354_safe_reference.json`.

---

## ⚠ THE "TWO" INHERITS AN INSTABILITY R332 HAD ALREADY MEASURED

Found by running the prior-work gate *after* writing this round up, which is one cycle later than it
should have been.

**R332 swept the k=4 reference across the band this round's p99 point sits in** — 46 blind
references spanning **0.25 of `coval_core`'s own MDE** — and found **two distinct admitted sets
inside that quarter-MDE**:

| reference A2 | admitted |
|---:|---|
| 0.551951 (closure) | `coval_core` · `topw_k3` · `topw_k4` · `topw_k6` |
| … | *same* |
| **0.554524** | `coval_core` · `topw_k3` · `topw_k6` |

Its conclusion, verbatim: *"the admitted set is **not a stable quantity at this site**, and any
statement of the form 'N arms are admitted' inherits that."*

**This round's p99 (0.5545) lands inside that band.** So *"the definition admits two at p99"* is a
correct measurement of an unstable quantity, and must be read with R332's caveat attached rather
than as a settled count.

### R332 says three there and this round says two — and that is not a contradiction

| | policy | at ≈0.5545 |
|---|---|---|
| R332 | moves **only** the k=4 reference; k=3 and k=6 stay at **their own closure levels** | 3 — `coval_core`, `topw_k3`, `topw_k6` |
| R354 | puts **every** k at the **same percentile** | 2 — `coval_core`, `topw_k6` |

`topw_k3` is a k=3 arm: under R332 it faces the k=3 **closure** level, under R354 the k=3 **p99**
level. **Different reference policies, both stated, neither wrong** — and the difference is exactly
one arm, which is the size of the instability R332 measured.

**What survives both**: `coval_core` and `topw_k6` are admitted under every reference at this
altitude. That is the claim this altitude supports — not a count.
