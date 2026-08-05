# R608 · The only thing separating them is when they happened — inside the band built to hold time fixed

**Decision this makes safe:** whether the era-3 provenance split has a structural mechanism.
**It does not. It has a temporal one, and my bin edge was in the wrong place.**

| feature | P(f \| provenance) | P(f \| none) | Δ | vs whole-grid null 0.4359 |
|---|---|---|---|---|
| **`late_in_era`** | **0.3333** | **1.0000** | **−0.6667** | **SURVIVES** |
| `many_artifacts` | 0.1111 | 0.0000 | +0.1111 | inside |
| `has_py` | 1.0000 | 0.9615 | +0.0385 | inside |
| `has_readme` | 1.0000 | 1.0000 | 0.0000 | inside |
| `big_readme` | 1.0000 | 1.0000 | 0.0000 | inside |
| `has_npz` | 0.0000 | 0.0000 | 0.0000 | inside |
| arc | all `A24` | all `A24` | — | no contrast exists |

⭐⭐⭐ **All 26 undocumented cited rounds sit in the late half of era 3; only 3 of the 9 documented
ones do.** Every non-temporal feature is flat.

## ⛔ So my own bin edge was arbitrary, and R607's framing is refined by it
R607 reported a *"genuine within-era selection"* in era 3 — but **five equal bands of ~120 rounds is
not holding time fixed.** The collapse happens **inside** era 3, not at the era-3/era-4 boundary I
drew. **The 13× figure stands; its location does not**, and the within-era selection is partly an
artifact of the bin width.

*The lesson is about stratification generally: a stratifier only holds a variable fixed at the
resolution of its bins, and a bin wide enough to contain the transition will attribute the transition
to whatever else varies across it.*

## ⚠ Power was computed BEFORE any feature was read
With **n = 35 (9 vs 26)** a null result would most likely have been silence, so the design's own
resolution came first: the null distribution of **max|Δ| over the whole 6-feature grid**, 200 draws —
median **0.2863**, **p95 = 0.4359**, max 0.5812. **A feature must exceed 0.4359 to clear it.** The
pre-registered kill (`MDE > 0.50 ⇒ verdict C regardless`) **did not fire**, so the features were
admissible to read — and only then were they read.

⭐ **The multiplicity correction is the null itself**, taken on the maximum across the grid rather
than applied afterwards to a per-feature p.

## Controls
| control | returned |
|---|---|
| **positive** — a feature perfectly correlated with provenance | \|Δ\| = **1.0000** vs MDE 0.4359 — PASS |
| **positive @ g=0** — a feature independent of provenance | \|Δ\| = **0.2051**, below MDE — PASS, it can fail |
| **placebo** — a constant feature | \|Δ\| = **0.0000** exactly — PASS |

## ⛔ Check #207
R607 closed calling `P(prov | cited) = 0.2571` **"the worst-documented quarter"** — a **rate among the
cited** read as a **rank position in the band**. *Two different quantities merged because both land
near a quarter.* And it proposed *"simply re-derive the 26"* — **a repair R605 had already priced out**,
having measured the construction step absent for 98 of 101 scored artifacts. **A closing line may not
propose a repair a previous round has shown impossible.**

**IMPOSSIBLE, named:** a structural correlate is **not a reason.** Why a round did or did not record
its source needs the round's author; everything here is descriptive.

## The sentence I can no longer write
> *"era 3 shows a genuine within-era selection against documented rounds."*

**It shows a transition my bin was too wide to see.** The rounds the page cites without provenance are
not a *kind* of round — they are a **stretch of time.**

## NEXT
`late_in_era` splits at a midpoint I chose (round 425), and the true transition is somewhere in
365–485. **Locate it: sweep the cut point across the band and find where provenance actually falls
off**, reporting the whole curve rather than the best cut — because a single chosen cut is exactly the
kind of specification this round just showed a bin can manufacture.
