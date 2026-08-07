# R1073 — attributable or propagated? ⛔ **Propagated: only `0.194` have a single carrier, and the margin over the floor is `+0.065`.**

**The decision this round makes safe:** whether R1071's recording gap can be closed by writing, or
needs reading. **It needs reading** — presence does not name an origin for four fifths of the values.

## ⛔ First: half of my own NEXT was forced

R1071 proposed checking whether the round whose README reports an unstored value also **stores** it.
**The population was defined by R1070 as "stored by no round"**, so that check could only ever return
100%. **It would have printed a clean-looking result that restates the selection criterion.** Not run,
and named here so it is closed rather than dropped.

## Result — the carrier count, which is not forced

| | |
|---|---:|
| unstored clause decimals | **31** |
| **exactly one** upstream README carries it | **6** |
| **many** carry it | **15** |
| **no upstream README** (present only in sources/commits) | **10** |
| single-carrier share | **0.194** |
| **measured floor**, random decimals at matched precision, 3 seeds | **[0.000, 0.129]** |
| **SHAM** — same values in the release data | **0 of 31** |

⚠ **The margin over the floor is `+0.065` and the World-B threshold is `≤0.20` — the observation sits
at `0.194`, close to both.** Reported as resolved-and-B, with the narrowness stated rather than
rounded away.

⭐ **And a third group R1071 could not see**: **10 values have no upstream README carrier at all**,
though R1071 found all 31 somewhere. R1071's corpus included **`run.py` sources and commit bodies**;
this one is READMEs only. **The same value can be in the record and still have no round that reported
it in prose.**

Examples: `0.5514` is carried by **12** rounds (R1059–R1062 among them — propagation in action);
`0.009103` by exactly **one** (`R981`); `0.005730`, `0.012488`, `0.009956` by **none**.

## Controls

- **POSITIVE** — a value with a carrier resolves to ≥1 (`0.009103` → `R981`): **True**.
- **NEGATIVE** — a constructed-absent decimal resolves to **0** carriers: **True**.
- **SHAM** — the same 31 values searched in the **release data**: **0 hits**, so "carried" is not
  "these digits occur in any large text".
- ⭐ **NOISE FLOOR** — how often a *made-up* decimal at matched precision is carried by **exactly one**
  upstream README: **[0.000, 0.129]**. Without it, "6 of 31" has no scale.
- **PLACEBO** — an empty candidate list exits **2**, never 0.
- ⚠ **Corpus restricted to rounds before R1067**, since the audit rounds quote these values wholesale
  — R1071's contamination lesson, carried forward rather than relearned.

## What this leaves

⭐ **6 values are attributable to one round each** — a one-line write in a known place. **15 are
propagated** and their origin is not recoverable from presence. **10 are in code or commits but no
README.** The gap is three gaps, and only the first is mechanical.

## IMPOSSIBLE here

- **whether a single carrier AUTHORED the value or quoted it from outside the arc** — **SETTLES:
  IN-RELEASE** by reading that round; the round's product is that there is now **one round to read
  per value** instead of a corpus.

`run.py` · `results/carrier_cardinality.json`
