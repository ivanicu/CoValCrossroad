# R1058 — does the clause admit a core it has never seen? ⛔ **UNVERIFIED ON IDENTIFICATION — and naming why is worth more than the rate.**

**The decision this round makes safe:** whether the clause defines a category or describes its
instance. **It cannot be decided inside this release**, and the reason is structural, not a lack of
effort.

## First: R1057's NEXT is closed, not run

R1057 proposed running the operator below the family threshold to see whether it errors, degrades, or
returns the `q=100` answer. **R1057's own table already answers it** — at k = 2, 4, 8 the two settings
give identical sets, so the operator **returns the `q=100` answer and emits no signal**: *silent
degradation*. Re-running it would have been a **third derivation reported as an experiment**.

## Result

| population | admitted |
|---|---:|
| released arms | **24 of 97 = 0.247** |
| never-seen synthetic cores (13 rules, 3 seeds each) | **0** |

**Verdict: UNVERIFIED on identification.** Not World A, not World B.

## ⛔ Three confounds, each caught only after building the round on it

1. **The positive control built the comparator.** My "strong never-seen core" used all 4 criteria
   common to every prompt — and those **are `generic`'s own selection**. The control asked whether the
   comparator resolvably beats itself. §4's *control fails for its own reasons*.
2. **The fixed-subset rules were subsets of the comparator.** Every subset of the common criteria is a
   subset of `generic`. `0 of 14 admitted` was not evidence of a provenance filter; it was evidence
   that a subset of X does not beat X. ⭐ **The verdict string fired World B on a rule set that could
   not separate the worlds** — §4's verdict-string row one level up: the **rule set**, not the branch,
   was what could not come out otherwise. Fixed by building cores per-prompt from **all** available
   criteria (965 of 968 prompts offer more than the common set), which are not subsets of anything.
3. ⛔⛔ **And the third cannot be engineered away.** Every rule available to me is **unselected** —
   positional or random. Every admitted released arm was **optimised** (`greedy_*`, `topw_*`,
   `coval_core`). So `0 of 13` is equally consistent with *the clause filters on provenance* and with
   *unoptimised selections are simply worse* — and **a definition ought to reject unoptimised
   objects.**

## ⭐ Why the gap cannot be closed here

A never-seen **good** core requires an optimiser other than the one that produced the released arms.
Using that optimiser makes the core no longer never-seen. **The clause's central claim — that it
defines a category rather than describing its instance — is UNIDENTIFIED on this site**, and that
statement is stronger than any rate, because it names *why no rate on this site can settle it*.

## Controls

- **HARNESS** — a **known-admitted** released arm from R1055's committed baseline must be admitted:
  **True**. Without it, every zero below would be silence rather than measurement.
- **NEGATIVE** — a comparator's own vector must **not** be admitted (nothing resolvably beats itself):
  **True**.
- **PLACEBO** — an empty selection is admitted at **0**: **True**.
- ⭐ **REPORTED AS A FINDING, NOT A CONTROL** — a never-seen core using **every** criterion available
  per prompt is **not admitted**. More criteria is not better agreement with humans.
- **NOISE FLOOR** — 3 seeds per rule; every rule reported with its seed count.
- **MULTIPLICITY** — all 13 rules reported, plus the released rate.
- ⚠ One `sat_*.npz` has a malformed meta key and is **named and skipped**, never silently dropped.

## IMPOSSIBLE here

- **whether a core built by a different optimiser would be admitted** — needs a second team or a
  second release. **SETTLES: OUT-OF-RELEASE.** This round converts that standing register entry from
  a formality into the **binding constraint on the clause's central claim**.

`run.py` · `results/never_seen_cores.json`
