# R1099 — the bound's slack is **baseline-shaped**, and it scope-corrects R1095.

**The decision this round makes safe:** whether R1095's *"neither reading of ③ removes the generic
baselines"* transfers from the blind family to the released one. **For `gen` and `generic_reprov` it
does not** — the released ②′ set excludes them **without ③**.

## ⛔ The set intersection is bookkeeping, and is labelled first

R1094's exclusion lists and R1098's slack are both committed. Crossing them is arithmetic. **The
finding is what it does to R1095's headline**, which was measured under the blind family and never
checked against the released one.

## The slack — 9 arms the blind family admits and the released one does not

| arm | leakage | authorship | in released ②′ | |
|---|---|---|---|---|
| `gen` | survives | survives | **False** | ⭐ generic variant |
| `generic_reprov` | survives | survives | **False** | ⭐ generic variant |
| `greedy_k12_fit1` | EXCLUDED | EXCLUDED | False | |
| `greedy_k4_fit1_08bR` | EXCLUDED | EXCLUDED | False | |
| `indep_k12_fit1` | EXCLUDED | EXCLUDED | False | |
| `indep_k4_fit1_08bR` | EXCLUDED | EXCLUDED | False | |
| `topw_k1` · `topw_k12` · `topw_k2` | survives | survives | False | |

⭐ **World B — the slack is baseline-shaped.** Of the 5 arms surviving ③ under **both** readings,
**`gen` and `generic_reprov` are generic variants absent from the released ②′ set.** So **R1095's
headline is a blind-family artifact for those arms: under the released family, ②′ excludes them by
itself.**

⚠ **And it stays UNDEFINED for `generic` and `genericpool16`** — they are that family's comparators
and are excluded from candidacy. **Absence there is not exclusion**, and reading it as such would be
the false-acquittal direction.

## ⚠ The SHAM says the COUNT is unremarkable — the finding is the IDENTITY

③ removes **4 of 9**, against a chance band of **(3, 8)** over 2000 same-size random draws from the
blind set. **4 is inside the band.** So *"③ removes 4 of the extras"* says nothing: ③ removes roughly
its usual share of anything.

**What the band cannot speak to, and what the finding rests on, is WHICH arms survive** — and two of
the five are the baselines the definition was written to beat.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE the fitted arms among the 9 are in R1094's **leakage** list — the generator's own record | PASS |
| g=0 the three released cores are **not** in the slack (they are in both families) | PASS |
| NEGATIVE the 9 **recomputed here** equal R1098's `blind_only`, rather than copied | PASS |
| SHAM the chance rate is **computed**, and it is what disqualifies the count | PASS |
| PLACEBO the slack against itself is empty | PASS |

## Downgrade recorded

| round | claim | status |
|---|---|---|
| **R1095** | *neither reading of ③ removes the generic baselines* | **SCOPE-CORRECTED** — true under the blind family; **does not transfer** for `gen`/`generic_reprov`; **undefined** for `generic`/`genericpool16` |

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| whether the definition admits `generic`/`genericpool16` under the released family | **N/A** | a third comparator family containing neither |
| cross-release | **N/A** | a second release |

`run.py` · `results/which_side.json`
