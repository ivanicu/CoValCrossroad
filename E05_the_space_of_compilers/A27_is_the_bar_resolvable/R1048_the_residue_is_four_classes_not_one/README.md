# R1048 — partition the residue. ⛔ **UNVERIFIED: the derivation test calls 97.5% of RANDOM numbers "derived", and my verdict string printed a world anyway.**

**The decision this round makes safe:** whether the 43-number residue can be exculpated as arithmetic.
**It cannot be, by this instrument** — and the instrument's failure is more informative than the
partition would have been.

## ⛔ The test cannot fail, and its own floor says so

| | |
|---|---:|
| residue | **60** |
| — CONSTANT (in the round's own `run.py`) | **17** |
| — EXTERNAL (frozen release-level list) | **0** |
| — DERIVED (a product/sum/ratio/difference of two artifact values) | 43 |
| — FLOATING | 0 |
| **measured coincidence floor for DERIVED, 3 seeds** | **[0.965, 0.975]** |
| observed DERIVED share | **0.717** |

⭐ **The observed share is BELOW the floor.** Real residue numbers are matched *less* often than
random ones — the diagnostic that the test is **saturated**, not merely noisy. With **410** artifact
values and four operations there are **~672,400** candidate results; at a README's 2–4 decimal places
the reachable set is dense in the unit interval, so *"is x a product of two of these"* is very nearly
*"is x a number"*.

**Verdict: UNVERIFIED.** Not World A, not World B. **CONSTANT 17** survives because it never routed
through this test — it is R1047's exact source check. **The remaining 43 are UNCLASSIFIED: never
FLOATING, and never exculpated.** A false acquittal is permanent, because nobody re-examines a cleared
claim.

## ⛔ And the verdict string fired World B before the floor was consulted

The first version compared the floating share to its pre-registered bands and printed **"the residue
dissolves"** — while the line two above it said the class was inside its own coincidence floor. The
pre-registered kill already said *"if the controls fire"*, and **the floor is one of the controls; it
was measured and then not read.** §4's *`the verdict string is not a computation`*, built in a round
whose subject is instruments. Fixed: the branch now requires `d_share > hi`.

## ⛔ A sixth defect, found in this round's own example output

The residue prints `| A2 | genericpool16 | −0.1247 |` — a **negative** value written with a **unicode
minus**. The number regex captures magnitude only, so the checker searches for `+0.1247` while the
artifact stores `−0.1247`. **Measured: 3 of 60** residue entries are sign-blind in exactly this way.
Small, but it is the same defect class as R1047's rounding blindness, and it was again found by
**looking at the object** — this time at my own script's printed examples.

## Controls

- **POSITIVE** — a product of two artifact values must classify DERIVED: **True**.
- **NEGATIVE** — that product plus a large offset must not: **True**.
- ⚠ **BOTH PASSED AND BOTH ARE WORTHLESS HERE**, which is the point: they establish the test *responds*
  and never that it *discriminates*. **Only the measured floor does that**, and it is the control the
  first draft computed and ignored.
- **NOISE FLOOR** — measured over 3 seeds, spread `[0.965, 0.975]`, not assumed.
- **PLACEBO** — a round with an empty residue contributes no denominator.
- **EMPTY POPULATION** — exit **2**, never 0, at both stages.

## The remedy is not a tighter tolerance

⭐ It is requiring the derivation to be **named in the text** — which is what realstat's own
arithmetic-trap section demands of a derivation in the first place: *"say so, state the assumption it
rests on, and stop calling it evidence."* A number the author derived says so; a number that merely
*could* be derived says nothing.

## IMPOSSIBLE here

- **whether a DERIVED number was actually derived that way by its author** — needs intent, which no
  committed text records. **SETTLES: OUT-OF-RELEASE.**

`run.py` · `results/residue_partition.json`
