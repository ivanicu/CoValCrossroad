# R754 · era does not explain it where it CAN be measured — and where the effect lives, it cannot be measured at all

**Within `DEFINITION.md`, holding governance constant and letting era vary, the flagged rate is
**0.3958** for old-era citations and **0.4054** for new — a difference of **−0.0096**, sitting at the
**14.5th percentile** of its own 5,000-shuffle permutation null. **Era does not carry it here.** ⛔ And
for the contrast that carried R753's 0.6207 gap, era and document are **UNIDENTIFIABLE, not
under-powered**: `FORMULATION.md` has **zero** figures in two of four era bins.**

## check #356 — the identification check ran before the design and killed the main contrast

| document | `<300` | `300-450` | `450-600` | `600+` | total |
|---|---|---|---|---|---|
| `STATEMENT.md` | 4 | 6 | 86 | 88 | 184 |
| `DEFINITION.md` | 5 | 43 | 55 | 19 | 122 |
| **`FORMULATION.md`** | **110** | **15** | **0** | **0** | 125 |

| pair | joint bins | |
|---|---|---|
| STATEMENT vs DEFINITION | **4/4** | **IDENTIFIABLE** |
| STATEMENT vs FORMULATION | 2/4 | ⛔ **UNIDENTIFIABLE** |
| DEFINITION vs FORMULATION | 2/4 | ⛔ **UNIDENTIFIABLE** |

⛔ **An empty joint bin cannot be stratified. That is definitional** — an **identification** failure,
not a power failure, and the two are not reported as one. **Only `DEFINITION.md` spans both ranges**,
so it alone can hold governance constant while era varies — **and it is not the document carrying the
effect.**

## E2 — within `DEFINITION.md`, era does not explain the rate

| document | n_old | n_new | rate_old | rate_new | diff |
|---|---|---|---|---|---|
| **`DEFINITION.md`** | 48 | 74 | **0.3958** | **0.4054** | **−0.0096** |
| `STATEMENT.md` | 10 | 174 | 0.5000 | 0.1609 | +0.3391 |
| `FORMULATION.md` | 125 | **0** | 0.8000 | **UNDEFINED** | n/a |

⛔ **`FORMULATION.md`'s new-era rate is UNDEFINED, not zero.** An undefined rate is never plotted as 0.

⚠ **The `STATEMENT.md` row is not evidence of an era slope.** `n_old = 10`; its MDE is far larger than
the +0.3391 it shows. It is printed because the preregistration demanded the confound be visible, and
it is reported as **uninformative at that n**, not as a corroborating result.

## the permutation null — and ⛔ my first negative control presupposed a non-null effect

v1 asked whether **one** shuffle produced a smaller `|diff|` than the real one, and reported **FAIL**.
But the real difference is **−0.0096**, essentially zero, and a single shuffle produces a difference of
order the standard error — which almost always **exceeds** a near-null effect. **§4 row ②, verbatim:**
*"`|permuted| < |real|` is a coin flip when the real effect is null, which is exactly when you are
running it."* **The control presupposed what it was testing** *(ledger 1032)*.

**Repaired to the shuffle DISTRIBUTION**, 5,000 draws: sd **0.0915**, 2.5–97.5 percentile
**[−0.1813, +0.1622]**. The real difference sits at the **14.5th percentile** of `|null|` —
**unremarkable, which CONFIRMS the null** rather than failing the control.

⭐ **And the SHAM says the same independently:** five *arbitrary* split points give `|diff|` up to
**0.0763**. **The R450 split is LESS different than an arbitrary one.**

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | the monotone ladder `0.0504 → 0.2833 → 0.7991 → 1.0000`. Band computed: floor **0.0504**, ceiling **1.0000** |
| **g=0** | zero planted difference rejects at **0.0497 ≈ α** |
| **NEGATIVE** | the 5,000-shuffle null; the real difference at the **14.5th** percentile |
| **SHAM** | ingredient **absent** — five arbitrary split points, max `|diff|` **0.0763** |
| **PLACEBO** | recomputed twice, difference exactly **0** |

⭐ **The formula was honest again** — analytic MDE **0.2545**, empirical **0.2565**, ratio **1.01×**,
matching R753 and unlike R752's 1.37×. Expected count here is ~19–30 per arm.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| **P1** old-minus-new, within DEFINITION | +0.30 ⚠ **prior-art-informed** from R607's 13× era effect | **−0.0096** | in band, **point badly wrong — and the prior did not transfer** *(ledger 1033)* |
| P2 figures spanning the split | 15, band [0, 60] | **4** | ✓ |
| P3 analytic MDE | 0.25, band [0.10, 0.50] | **0.2545** | ✓ nearly exact |
| P4 simulated rejection at that MDE | 0.78, band [0.60, 0.92] | **0.7939** | ✓ |
| P5 unidentifiable pairs | 2, band [0, 3] | **2** | ✓ exact |
| **D** DEFINITION's old rate closer to FORMULATION's | true | **false** — 0.3958 is closer to 0.1793 | ⛔ |

⚠ **R607 measured a 13× provenance difference between eras across ROUNDS.** It does **not** reproduce
at the level of a document's cited figures. **A strong prior-art effect measured on one unit does not
transfer to another unit**, and registering it as a prediction is how I got P1 wrong by 0.31.

## the sentence I can no longer write

*"`FORMULATION.md` is worse because it is older."* Where age can be tested with governance held fixed,
it changes nothing; and where the effect actually lives, age and governance cannot be separated at all.

## NEXT

R753's directional survives its strongest confound but the decisive contrast stays unidentifiable, and
this round shows why: `FORMULATION.md` stopped citing at R360 while the other two ran to R753. That is
not a property of governance or of age — it is that **the document stopped being maintained**, and
"maintained" is a third variable this arc has not measured. It is measurable from git: the
commit dates and the number of commits touching each deliverable are on disk. The registered quantity
is commits-per-document since R360's date against each document's flagged rate, which separates
*ungated* from *abandoned* — and those need different repairs, since a gate cannot fix a file that
receives no edits.
