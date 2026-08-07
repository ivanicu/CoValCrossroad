# R1059 — built the second optimiser. ⛔ **UNVERIFIED again, and now with the mechanism measured: the quality gap is `+0.0651`, so non-admission is fully explained without provenance.**

**The decision this round makes safe:** whether R1058's provenance-vs-quality confound can be broken
by building better objects. **It cannot — it reproduces.** And the round is worth its cost because it
says *why*, with numbers.

## What was built

| optimiser | objective | search | shares with released `greedy_*`/`topw_*` |
|---|---|---|---|
| **varmax** | criteria that discriminate most among the 4 responses — **never sees the human target** | per-prompt ranking | **neither axis** |
| **heldout** | agreement with the human target | global ranking fitted on **half** the prompts, judged on the other half | objective only, not search |

## Result

| optimiser | k=2 | k=3 | k=4 |
|---|---|---|---|
| varmax — admitted | 0/3 | 0/3 | 0/3 |
| varmax — **sham (ranking reversed)** | 0/3 | 0/3 | 0/3 |
| heldout — admitted (held-out half only) | 0/3 | 0/3 | 0/3 |

**Released arms: 0.247. Neither optimiser admitted.** But the verdict is **not** World B.

## ⛔⛔ Two controls fired, and both point the same way

1. **The sham condition I wrote could only fire if the optimiser was admitted** (`sham ≥ admitted >
   0`) — a check that **cannot fail in the case that actually occurred**, since both were 0. Read on
   the **continuous score** instead, where it has power: reversing varmax's ranking moves mean
   agreement by **`[+0.0094, −0.0004, −0.0015]`**. ⭐ **The target-free objective contributes nothing.**
   `varmax` is a size-matched selection rule wearing an optimiser's name — **only `heldout` is a real
   optimiser, and one optimiser is n = 1.**
2. ⛔⛔ **The quantity that decides the round is the one I almost didn't look at.** Best synthetic core
   **0.4863** vs comparator `generic` **0.5514** — a gap of **`+0.0651`**. **Non-admission is fully
   explained by quality.** R1058's confound is not resolved; it is **reproduced with better-built
   objects**.

## Controls

- **POSITIVE** — a known-admitted released arm from R1055's baseline must be admitted here: **True**.
  Without it every zero above would be silence.
- **NEGATIVE** — a comparator's own vector must not be admitted: **True**.
- **SHAM** — varmax with its ranking **reversed**: same size, same search, ingredient inverted. Fired,
  and it is what unmasked one of the two "optimisers".
- **LEAKAGE** — `heldout` is judged **only on the half of prompts its ranking was not fitted on**;
  `varmax` never touches the target, so leakage is impossible by construction.
- **NOISE FLOOR** — 3 seeds per cell; 3 independent fit/eval splits for `heldout`.
- **MULTIPLICITY** — both optimisers × 3 values of k, all cells reported.

## What this round establishes, and it is not nothing

⭐ **A negative result with a measured mechanism beats an unexplained one.** R1058 could say only *"the
comparison is confounded"*. This round says *"the confound persists, and here is the size of the gap
that sustains it: 0.0651 in mean agreement, against a comparator scoring 0.5514."* **Any future attempt
to break the confound must first close that gap** — that is a concrete specification, not an
aspiration.

## IMPOSSIBLE here

- **whether a second TEAM would build a core clearing 0.55** — I built both of these, so
  *independent* means *shares no named design choice*, never *built by someone else*.
  **SETTLES: OUT-OF-RELEASE.**

`run.py` · `results/second_optimiser.json`
