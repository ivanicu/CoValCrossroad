# R513 · The size of my own assurance surface

**Decision this makes safe:** whether the campaign's assurance surface can be cited as evidence
that the deliverable's claims are checked — and at what coverage.

**Estimand (G1, named before method):** the fraction of *verdict-asserting gates* that declare a
positive control. **Population:** the gates `assurance/run_all.py::discover()` returns — asked from
the code, **not** re-derived by glob. **Instrument:** a case-insensitive search for
`positive control` / `negative control|placebo|sham` in each gate's source. **Baseline:** none
required; this is a census. **Regime:** the surface as committed at this sha.

**Direction of the proxy (P6).** `no mention of the words ⇒ no DECLARED control` is sound.
`mention ⇒ has a control that fires` is **not**, and using it in that unsound direction is what
voided the previous round's audit (retraction 345). Only the sound direction is used here.

## Worlds
- **A · the surface is controlled** — most asserting gates carry a positive control, so a PASS from
  the suite is an acquittal.
- **B · the surface is half-uncontrolled** — a large minority declare neither control, so their
  PASS is, by G2, silence rather than acquittal.

## Controls
- **Positive control on the population instrument:** `discover()` must exclude a known non-gate.
  It excludes 8 by name and 2 prefixes; verified against a raw glob, which over-counted by 13.
- **Positive control on the "silence" reading, free:** 2 of the 18 flagged gates are the census's
  standing FAILs, proving they *can* return non-zero. So the 18 is an **upper bound** on
  uncontrolled gates, not a count of broken ones.
- **Pre-registered kill:** if fewer than 25% declare neither control, world B dies.

## Result
45 gates · **both 8 (18%) · positive only 13 (29%) · negative only 1 (2%) · neither 23 (51%)**.
Of the 23, **18 also carry no empty-population guard**. World B survives; A is dead.

⚠ **The finding is bounded, and the bound is the point.** 51% declare no positive control; that
does not make 51% broken, because at least 2 demonstrably fail today. What it establishes is that
**the suite's aggregate PASS cannot be cited as an acquittal**, because for half its members
nobody has shown the check could have failed.

## What this round is really about
Four consecutive rounds produced four sizes for this surface — **14, 45, 54, 0** — and
`run_all.discover()` has returned the correct **45** the entire time. Every wrong number came from
re-deriving a population that was already defined in code.
