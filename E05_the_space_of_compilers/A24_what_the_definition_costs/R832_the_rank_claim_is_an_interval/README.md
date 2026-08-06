# R832 · R831's rank claim is an interval

**The decision this made safe:** whether R831's conclusion survives the population its instrument
never classified. **It does.** Only the rank *number* becomes an interval; the direction holds at
both ends.

Design in `PREREGISTRATION.txt`, committed before `run.py` existed. `run.py` committed before it ran.

## What I published one round ago, and why it overreached

> *"the best **label-free** substantive arm this site contains sits at rank 50 of 93"*

⛔ **The instrument's unit is `③-ADMITTED`. The sentence's unit is `label-free`.** They are not equal.
③ returns **11 UNKNOWN** over R831's 93 arms, and UNKNOWN does **not** mean *reads labels* — it means
`selector_of` returned `None` because the arm name carries no known selector prefix. Those 11 include
`generic` (rank 21) and `gen` (rank 27). **§4's instrument-unit-vs-claim-unit, third time this
session.**

⛔ **And P4 stopped the round I first wanted.** My instinct was to *decide* the 11 by record, as R475
decided `coval_core` from the dataset card. `DEFINITION.md` already records the decision **not** to:
*"7 arms have provenance the source cannot classify … and are returned UNKNOWN, never silently
admitted."* That is a deliberate three-valued discipline, committed. Re-opening it is not this
round's business.

## Result — an interval, and it is a DERIVATION

| reading of ③'s UNKNOWN | best substantive arm | rank | A2 |
|---|---|---|---|
| unknown-as-**ADMITTED** (lower end) | `coval_core` | **11** / 93 | 0.5715 |
| unknown-as-**EXCLUDED** (upper end) | `topvar_k4` | **50** / 93 | 0.4873 |

**Pre-registered interval: [11, 50].** Nothing was re-measured — committed ranks, committed partition.

⚠ **Post-hoc refinement, labelled.** The lower end is achieved by `coval_core`, which **R475 settled
as a label-reader by RECORD**. Removing that family: `generic` **21** · `generic_reprov` 22 ·
`genericpool16` 25 · `gen` 27. **Record-informed interval: [21, 50].** This was computed *after*
seeing which arm held the lower end, and is reported beside the pre-registered one, never instead.

## The robustness question — the only part that could come out otherwise

| cell | ③-EXCLUDED at the top |
|---|---|
| unknown-as-EXCLUDED · top 8 | **8 / 8** |
| unknown-as-EXCLUDED · top 16 | **16 / 16** |
| unknown-as-ADMITTED · top 8 | **8 / 8** |
| unknown-as-ADMITTED · top 16 | 13 / 16 |

**W-DIRECTION-SURVIVES.** The top 8 are label-readers under **both** readings, so R831's
W-SELF-DEFEATING is not an artifact of how UNKNOWN was read.

Controls: synthetic top-8 all-admitted → 0 excluded · all-excluded → 8 excluded · ③'s partition
recomputed from source twice → identical. Two-seed byte-identical.

## NEXT

The interval's width — rank 21 to rank 50 — is produced by the arms ③ cannot classify, listed in the
artifact's `unknown_arms` field (n = 11), and `DEFINITION.md` has already ruled they carry no
provenance record on this site. So the width is a property of the RELEASE's metadata, not of the
definition. What would narrow it is a per-arm construction record, which is a specification for the
next site rather than a measurement here.
