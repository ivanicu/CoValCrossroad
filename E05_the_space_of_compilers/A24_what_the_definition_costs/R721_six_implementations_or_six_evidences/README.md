# R721 · six independent implementations, or six independent evidences?

**The block SURVIVES, and my own prediction was wrong by a factor of five. I registered `2` distinct
upstream sources behind the six derivers, expecting them to collapse onto R294's census; there are
`11`. ⚠ But the survival is qualified: `3` files are read by more than one deriver, `clause_ledger.json`
by `4 of 6`, and **all 6** read at least one shared file. They are 11 files with 3 in common — not
disjoint evidences — and the block's word "at most" is exactly what makes it survivable.**

## check #323 — it holds, and the block is more careful than my line assumed

✓ "7 rows cite 22 rounds" and "at most SIX independent computations" are both in the block; R680's
artifact carries 8 derivers, 2 of which read a prior artifact.

⭐ **The block already labels its number a ceiling, twice** — *"at most SIX"* and *"a ceiling twice
over — absent literals remove one way of copying, not all."* **The naive attack is one it has already
made against itself.**

## what each deriver reads

| round | glob? | sources |
|---|---|---|
| R294 | yes | `full_census.json`, `sat_*.npz` |
| R404 | no | `clause_ledger.json`, `conjunct_decomposition.json` |
| R405 | no | `clause_ledger.json`, `readings.json`, `universal_reading.json` |
| R408 | yes | `clause_ledger.json`, `literal_test.json`, `sat_*.npz` |
| R409 | no | `literal_test.json`, `ordering.json` |
| R667 | no | `clause2_spec_curve.json`, `clause_ledger.json`, `extension.json`, `extension_reconciled.json` |

**11 distinct upstream sources.** ⚠ **Shared: 3** — `clause_ledger.json` in **4 of 6**, `sat_*.npz`
and `literal_test.json` in 2 each. **6 of 6 derivers read at least one shared file.**

## controls — 6 PASS, 0 FAIL *(the one ⛔ is the registered directional, a prediction, not a control)*

| control | returned |
|---|---|
| **POSITIVE** | R294, the producer R678 names → paths recovered — the extractor reads paths |
| **g=0** | a file with no data access → 0 data paths, no default |
| **NEGATIVE** | 6 random arc rounds → `[15, 15, 14]` distinct sources vs the derivers' **11** — **the derivers are only slightly more convergent than the corpus** |
| **SHAM** | docstring-only extraction → **0** sources vs the body's 11 — the executable body is the ingredient |
| PLACEBO / UNIT | identical runs differ by 0 · instrument unit ≠ claim unit |

## specification sweep

| extraction | population | distinct sources |
|---|---|---|
| literal only | the 6 derivers | 10 |
| literal + glob | the 6 derivers | **11** |
| literal + glob | 6 random arc rounds | [15, 15, 14] |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** derivers naming a data path | 5 [2, 6] | **6** |
| **B** distinct upstream sources | 2 [1, 6] | ⛔ **11 — OUTSIDE** |
| **C** derivers using glob | 3 [0, 6] | **2** |
| directional | sources < 6 | ⛔ **FAILS** |

⭐ **The failed directional is the round's most useful output.** I predicted the six would collapse to
one source and they did not. **An attack that fails is evidence about the claim, and this is the first
block in this arc to survive one.**

## limits

- **Sharing a source does not make a computation wrong** and does not merge two into one — **it makes
  them one evidence.**
- Extraction is bounded both ways: a commented path is **over-counted**, a glob-built one
  **under-counted**. 2 of 6 use glob, and the sweep reports both counts.

## impossible here

| criterion | what it would require |
|---|---|
| whether any of the six is correct | this round measures support, never correctness |
| cross-release | a second release |
