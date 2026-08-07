# R524 · 56 tags are 46 objects — and most of the collapse is intentional

**Decision this makes safe:** which prior counts are counts of objects and which are counts of tags.

**Estimand:** the number of equivalence classes of the 56 home-judge tags under **exact** equality
of the saturation matrix. **Instrument:** array equality after a stable sort on meta keys — no
tolerance, because a tolerance is what let a four-decimal agreement pass as identity in R522.

## Result — WORLD B

⭐ **56 tags → 46 distinct objects. 10 duplicate tags across 8 classes.**

| class | tags | reading |
|---|---|---|
| `topw_k4` = `topw_k4_det{A,B}` | 3 | **determinism controls — identity is the expected PASS** |
| `oracle_k4` = `oracle_k4_oracle_k{A,B}` | 3 | the R523 alias |
| `random_k4_s0` = `random_k4_s0_ctlS0` | 2 | control tag, byte-identical |
| `random_k4_s1` = `random_k4_s1_ctlS1` | 2 | control tag, byte-identical |
| `generic` = `generic_reprov` | 2 | re-provenance run |
| `coval_core_2bA` = `coval_core_2bB` | 2 | duplicate run |
| `greedy_k4_greedy_k{A,B}` | 2 | R523 |
| `indep_k4_indep_k{A,B}` | 2 | R523 |

⭐⭐⭐ **Most of the collapse is deliberate.** `_detA/_detB` is a determinism check whose *correct*
outcome is byte-identity; `_ctlS0/_ctlS1` are control tags. **That is exactly why nobody noticed:
the duplicates are supposed to be there, and only their effect on denominators is a defect.**

## Controls
- **Positive** — the partition must recover all four identities R523 found by hand. **4/4. PASS.**
  A partition that missed one would not be sensitive enough for the ones it claims.
- **Negative** — `coval_core` ≠ `generic`, and a shuffled copy does not match its original, so the
  comparison is order-sensitive rather than a multiset test. **PASS.**
- **No noise floor, by construction.** Exact equality has none.

## What moves, and what does not

| prior claim | status |
|---|---|
| R436's "0 of 56 excluded at J" | **denominator is 46 objects.** The **zero is unchanged.** |
| R518's margins 4.90×–8.65× MDE | **safe** — per-arm, not a count |
| R519's "③ removes 4 of 9" | **safe** — R523 measured 0 alias pairs among R294's 41 |
| R520–R522's "6 missing/6 BEATS" | already corrected to **2 objects** in R523 |

⭐ **Bound: any denominator drawn from this population is overstated by up to 10.**

⚠ **One flag worth carrying:** `random_k4_s1` — R516's **null** — has a byte-identical twin tagged
`_ctlS1`. The null itself is unaffected, but a tag named as a control that is the same object as
what it controls **cannot control anything**, and nothing in the name says so.

**Impossible here:** the second release's 37 tags, a different schema family; and *why* two tags
name one object, which lives in the generating invocation the `.npz` does not carry.
