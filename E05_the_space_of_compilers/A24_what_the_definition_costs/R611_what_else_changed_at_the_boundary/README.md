# R611 · It is a schema change, not a loss — plus one genuine loss beside it

**Decision this makes safe:** what the ~430 boundary actually is. **The artifact convention swapped a
provenance field for a verdict field.**

| feature | before B = 431 | after | Δ | vs whole-grid null **0.2057** |
|---|---|---|---|---|
| **provenance** *(positive control)* | **0.9808** | **0.0455** | **−0.9353** | **CLEARS** |
| **`has_world`** | **0.0455** | **0.9808** | **+0.9353** | **CLEARS — the exact mirror** |
| **`has_controls`** | 0.8788 | 0.3269 | **−0.5519** | **CLEARS** |
| `readme_over_4k` | 0.7727 | 0.6154 | −0.1573 | inside |
| `py_over_8k` | 1.0000 | 0.9231 | −0.0769 | inside |
| `multi_artifact` | 0.1212 | 0.0577 | −0.0635 | inside |
| `many_keys` | 0.6061 | 0.5577 | −0.0484 | inside |
| `has_py` | 1.0000 | 0.9615 | −0.0385 | inside |
| `has_readme` | 1.0000 | 0.9808 | −0.0192 | inside |
| `has_mde` | 0.2273 | 0.2115 | −0.0157 | inside |

⭐⭐⭐ **Δ(prov) = −0.9353 and Δ(world) = +0.9353 — the same magnitude, opposite sign, to four
decimals.** That is a **substitution**, not a collapse: the same rounds that used to record where a
number came from began recording what it concluded.

⚠ **One genuine loss sits beside it:** `has_controls` falls **0.8788 → 0.3269**. That is *not*
mirrored by anything, so it is a real reduction in what artifacts carry — and it is the one the
register should own.

## What this does to the arc
| round | claim | status |
|---|---|---|
| R606 | cited rounds carry provenance 2.5× less | **stands** |
| R607 | *within-era selection* | ⛔ re-diagnosed (R610) |
| R610 | the switch is in the **work** | **stands, and is now named**: the work changed its schema |
| — | *"provenance recording stopped"* | ⚠ **too strong** — it was **replaced**, and separately `controls` was **lost** |

*Four rounds measured a real number and each named its cause a little better. The number never moved;
the story around it did, three times.*

## ⛔ Check #210: a category error in my own NEXT line
R610 proposed aligning R605's **101 scored matrices** with a per-round boundary. **Those matrices live
in `corebench/results/`, a shared pool with no round attribution at all** — two populations at
different levels of the hierarchy, merged because both were absences I had measured. **Ill-posed**,
and replaced with a question that is per-round throughout.

## Controls
| control | returned |
|---|---|
| **positive** — provenance itself, at the **fixed** B | Δ = **−0.9353** vs 0.2057 — **the boundary survives pooling and fixing the cut** |
| **positive @ g=0** — a feature independent of id | \|Δ\| = **0.0262** — PASS, it can fail |
| **placebo** — a constant feature | **0.0000** exactly |
| **whole-grid null** — 200 draws, 9 random features | median 0.1492 · **p95 0.2057** · max 0.2512 |

⭐ **B is CHOSEN, not fitted** — the midpoint of two independently measured cuts (434 cited, 428
uncited), fixed before any feature was read. **No feature selects its own boundary**, which is what
separates this from a second sweep. **The multiplicity correction is the null on the grid maximum.**

**IMPOSSIBLE, named:** **a boundary in id order is not a date and a correlate is not a cause.** This
names *what* differs across a position in the sequence, never *why* — fifth round running that the
register's `temporally resolved` row lands on my instrument.

## The sentence I can no longer write
> *"provenance recording stopped at ~430."*

**It was replaced.** A `world` key took its place at exactly the same rate. The thing that genuinely
stopped is `controls`.

## NEXT
The two mirrored Δs are **equal to four decimals**, which is either a perfect substitution or a
coincidence I have not excluded. **Count the rounds carrying BOTH keys and NEITHER**: a true swap
predicts near-zero in both cells, while independence at these marginals predicts a specific non-zero
count. That is a 2×2 table with a forced prediction, and it is the cheapest way to tell a substitution
from two unrelated trends that happen to cross.
