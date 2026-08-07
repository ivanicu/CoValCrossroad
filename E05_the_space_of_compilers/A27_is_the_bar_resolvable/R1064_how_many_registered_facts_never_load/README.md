# R1064 — how many registered facts never load? ⭐ **All 79 globs resolve — and the round ships the gate that makes the next one loud.**

**The decision this round makes safe:** whether R1063's silent-skip defect cost more than one round.
**It did not** — and the defect is now closed rather than merely counted.

## Result

| | |
|---|---:|
| `load(...)` globs in the registry | **79** |
| resolving to a file | **79** |
| **resolving to nothing** | **0** |
| matching more than one file (registry takes the last) | **0** |

⚠ **That is true NOW because R1063's artifact was written minutes ago.** It was **false** while that
script was crashing, and **nothing in the currency gate would have said so.** The count is reassuring
about the past only because the past has just been repaired.

## ⭐⭐ The remedy, shipped — not just measured

`assurance/a_registered_fact_must_load.py` exits **1** on any unresolved glob and names it. §0.2: a
round that leaves the defect in place is cost recovery; **the gate is the production.**

## ⭐ And the lock was attacked before being trusted

| attack | result |
|---|---|
| redirect one glob to a nonexistent round | **exit 1**, and the dead glob is **named**: `A27_*/RNEVER__*/results/criterion_universes.json` |
| registry containing **no** `load()` calls at all | **exit 2** — a gate over nothing must not pass |
| restore the registry | **exit 0**, 79 of 79 |

**A lock never attacked is a lock never tested.** The second attack matters most: without it, deleting
the registry's contents would have turned the new gate green.

## Controls

- **POSITIVE** — a glob **known** to resolve (R1063's, written minutes earlier) must resolve here:
  **True**. A resolver never shown to succeed cannot evidence a failure.
- **NEGATIVE** — a fabricated glob must resolve to nothing: **True**.
- **PLACEBO / EMPTY POPULATION** — no globs found → exit **2**, never 0. Verified by attack 2.
- **MULTIPLICITY** — all 79 reported with their resolution, plus the multi-hit count, not only
  failures.

## What this round cannot say

**Existence is not correctness.** A glob that resolves may still point at the wrong artifact — that is
the gate's own pattern check, a different question already covered by the currency gate itself.

## IMPOSSIBLE here

- **whether a resolving glob points at the RIGHT artifact** — **SETTLES: IN-RELEASE**, and it is
  already the currency gate's job; this round guards only its inputs.

`run.py` · `results/registry_inputs.json` · **remedy:** `assurance/a_registered_fact_must_load.py`
