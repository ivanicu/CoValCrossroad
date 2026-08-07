# R1049 — was R1048's false PASS one entry or the gate? ⛔ **16 of 63 registered facts are multi-home: their gate PASS is not attributable to their own annotation.**

**The decision this round makes safe:** whether the currency gate's verdict can be read as evidence
that a round wrote its annotation. **For 16 named facts it cannot** — and the verdict lands in
**neither pre-registered band**, which is reported rather than rounded to the nearer one.

## The mutation, and its proxy ledger written before the run

Delete the span a pattern matches; ask whether it still matches. A **second home** means a PASS cannot
be attributed to the annotation.

| | |
|---|---|
| **PROPERTY** | the gate's PASS is caused by the round's own annotation |
| **PROXY** | the pattern matches in exactly one place |
| **IMPLICATION** | `≥2 homes ⇒ not attributable` **SOUND** · `1 home ⇒ attributable` **NOT SOUND** |
| **WITNESS** | R1048's original pair — one home was `97.5%` in an unrelated table, and that was its *only* extra home |
| **SAFE SIDE** | single-home returns **UNVERIFIED**, never CLEAN |

## Result

| | |
|---|---:|
| statically readable facts | **63** |
| **multi-home** (every pattern has ≥2 homes) | **16** — share **0.254** |
| patterns not statically readable — reported, never dropped | **2** |
| **measured floor**: random 3-letter patterns that are multi-home, 3 seeds | **[0.092, 0.183]** |

⭐ **0.254 is above the floor**, so it is not explained by the document merely being dense enough that
any short pattern repeats. **But the pre-registered bands were ≥0.30 → World B and ≤0.10 → World A,
and 0.254 is in neither.** Reporting the gap I fell into is why two bands were registered.

**Flagged:** `R921 R922 R920 R925 R926 R975 R978 R986 R989 R1000 R1001 R1005 R1012 R1027` and two
more. **These are now UNVERIFIED on currency — not overturned, and not clean.**

## ⚠ One post-hoc observation, labelled, because it is not a finding

Multi-home share **before R1022: 0.361** (36 facts) · **from R1022 on: 0.111** (27 facts). **The
covariate was chosen after seeing the list**, there is one test and no multiplicity control, and the
direction was picked by looking. **It licenses a pre-registered test in a later round and nothing
more.**

## Controls

- **POSITIVE** — R1048's **original** loose pair, a **real measured failure quoted from the commit
  that fixed it**, must read multi-home: **True**. Not an invented case — §4's *validated against your
  imagination*.
- **NEGATIVE** — a 160-character literal lifted **at runtime** from the document must be single-home:
  **True**.
- **NOISE FLOOR** — measured over 3 seeds, `[0.092, 0.183]`, not assumed.
- **PLACEBO** — a fact with no statically readable pattern contributes no denominator; **counted and
  reported (2)**, because a silent drop shrinks the denominator in the flattering direction.
- **EMPTY POPULATION** — exit **2**, never 0.

## What this round cannot say

Whether a **single**-home fact is anchored. Its one home may itself be unrelated text — **exactly how
R1048 failed**. Folding UNVERIFIED into CLEAN manufactures a false acquittal, and a false acquittal is
permanent because nobody re-examines a cleared claim.

## IMPOSSIBLE here

- **whether a single home is the round's own annotation** — needs the matched span read against that
  round's README. **SETTLES: IN-RELEASE**, one reading per fact; unattempted, not unavailable.

`run.py` · `results/gate_coincidence.json`
