# R1070 — `sourceable` names no source. ⛔⛔ **31 of 38 clause decimals are stored by NO round — and that retracts R1069's headline.**

**The decision this round makes safe:** whether R1068's gate can be extended mechanically to the
clause's decimals. **It cannot** — most of them are not measurements anywhere.

## The correction that inverts the previous round

R1069 reported the clause's decimals **0.789 sourceable** against a floor of ~0.15. That extractor
pulled numbers out of **strings inside artifacts** — so a value merely **quoted in another round's
verdict text** counted as sourced.

**Quoter inflation, measured: mean `+4.8` candidate rounds per value, max `+59`.**

Restricting candidacy to rounds that **stored** the value as a numeric leaf:

| | quoted-text extractor | **stored-leaf extractor** |
|---|---:|---:|
| unsourced (0 rounds) | 8 | **31 of 38 = 0.816** |
| ambiguous (>1) | 28 | 6 |
| **unique (exactly 1)** | 2 | **1** |

⭐ **The clause's decimals are sourceable AS TEXT and largely not AS MEASUREMENTS.**

## By precision — and the tell that exposed the bug

| precision | n | unique | ambiguous | **unsourced** | random-unique floor |
|---:|---:|---:|---:|---:|---|
| 1 | 2 | 1 | 1 | 0 | [0.000, 0.000] |
| 3 | 2 | 0 | 2 | 0 | [0.000, 0.500] |
| 4 | 15 | 0 | 3 | **12** | [0.000, 0.200] |
| 6 | 19 | 0 | 0 | **19** | [0.000, 0.000] |

⛔ **The tell was the precision curve running backwards.** 6-decimal values are nearly unique by
construction, yet **0 of 19** resolved to a single round under the first extractor. That is not how
precision behaves — which is what sent me back to the walker. Under the corrected one, **all 19 are
unsourced**, which is consistent and much worse.

## Verdict — neither pre-registered world

I registered *"most are addressable"* (≥0.50) and *"ambiguity dominates"* (≤0.20). **The modal
outcome is neither: it is UNSOURCED at 0.816.** Reporting the category I did not anticipate, rather
than forcing the result into one of my two, is the whole point of naming bands in advance.

## Controls

- **POSITIVE** — a value with a known round (`0.917`, R1053) resolves to ≥1 candidate: **True**.
- **NEGATIVE** — a constructed-absent decimal resolves to **0**: **True**.
- ⭐ **NOISE FLOOR, PER PRECISION** — the random-unique rate at each precision, 3 seeds. Without it,
  "1 of 38 unique" could not be distinguished from what chance produces.
- **PLACEBO** — precision classes reported with their sizes; none merged to hide an empty one.

## What this leaves

⭐ **The practical product is small and honest: 1 decimal whose provenance can be checked by opening
one file instead of searching 820 rounds.** A single candidate is an **address**, never a proof of
citation.

## IMPOSSIBLE here

- **whether a uniquely-resolving value is actually cited from that round** — cardinality cannot say.
  **SETTLES: IN-RELEASE**, one reading, now against **one** round instead of 820.

`run.py` · `results/decimal_addresses.json`
