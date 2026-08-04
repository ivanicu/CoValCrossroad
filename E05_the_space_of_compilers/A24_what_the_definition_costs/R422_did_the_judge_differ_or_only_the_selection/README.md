# R422 · the `_08b`/`_08bR` families — did the JUDGE differ, or only the SELECTION?

**The decision this round makes safe:** whether every cross-family number in this campaign is a
cross-*instrument* number. If the two families were emitted by different judges, comparisons across
them measure the judge; if by the same judge, they measure the selection. Nothing downstream can be
read correctly until that is settled, and the artifacts needed to settle it are already committed.

## What R419–R421 left open

| round | measured | left open |
|---|---|---|
| R419 | scoring floor **exactly zero**, bitwise | — |
| R420 | `topw_k` selection byte-identical (positive control supplied late, by R421) | 3 rules unexercised |
| R421 | `oracle_k`, `greedy_k`, `indep_k` byte-identical; seeded control detects | **which input differed** |

Jointly they force *the inputs differed*. They cannot say **which** input, and the last report closed
on *"`_08bR` is the outlier"* — a sentence that assigns fault to a file when the evidence supports
neither assignment.

## ⛔ Two errors in my own `NEXT`, both found before running anything

1. **It proposed rung 5 while rung 2 was uninspected.** `select_core.py` emits **two** artifacts per
   run — `core_*.json` *and* `sat_*.npz`. R420/R421 hashed only the first. The second is the judge's
   own emitted numbers, both families' copies are committed, and the discriminating question needs
   **zero runs**. The `NEXT` asked for ten CPU invocations.
2. **The inventory was five pairs, not two.** `oracle_k4`, `greedy_k4_fit1`, `indep_k4_fit1`,
   `topvar_k4`, `topwvar_k4` — four rules across two fit parities, plus an unpartnered
   `oracle_k4_fit1_08b`. R421's `n=1 rule` caveat described what R421 ran, not what was on disk.

## The separator

`--full-npz` supplies the satisfaction that is **emitted**; `--select-npz` supplies the satisfaction
that **runs the rule**, defaulting to the former.

| observation on a criterion present in both files | implies |
|---|---|
| same criterion, same response letter, **different value** | the **emitting** npz differed → two judges |
| same criterion, same response letter, **identical value** | one emitter → the **selection** input differed |

⛔ **Arithmetic trap.** Equality *given* a shared emitter is forced by the lookup — that is a
derivation, and it is what makes the test diagnostic. Not forced: whether any criteria are shared at
all, or which branch the real files fall in.

⚠ **The join key is the whole instrument.** `meta` is `pid|j|letter` where `j` is the criterion's
**position** in the selected set, so the same `j` names different criteria across the two files.
Joining on `j` would compare unrelated cells and fabricate a difference in every pair. The claim's
unit is a *criterion*, so the key is `(pid, criterion text, letter)`, read from the core JSON.

## Controls

| control | what it establishes |
|---|---|
| **g = 0** | an unperturbed copy reports **zero** — the criterion is not satisfied before the plant |
| **PLANT (+)** | one value nudged by `1e-3` is caught, and *exactly one* is. ⚠ invented case, weakest control here |
| **REAL (=)** | `topw_k4` vs `topw_k2` — genuinely different files sharing an emitter — must show non-empty overlap and **zero** differences |
| **REAL (+)** | `full` vs `full_sham` — the same criteria under a different scoring — must show differences. If they share nothing the control is **UNAVAILABLE** and the round says so |
| **NON-EMPTY** | a rule with an empty shared set is printed `UNVERIFIED`, never folded into agreement |

⚠ **The `REAL (=)` control was first written as R420's `detA` vs `detB`.** Those two are
byte-identical, so zero differences is *forced* — it would have been the `g = 0` case wearing a
corpus's clothes. A different-`k` pair is the non-degenerate version.

## Impossible here, named

- **which selection input differed** — `--select-npz` vs `--fit-parity` vs the target are not
  separable from artifacts that record no configuration. Exactly the gap the provenance field closes
  going forward, and it closes nothing retroactively.
- **what `08b` was meant to denote** — the only `08b`-named npz on disk is a **gold** file
  (`a08_gold_08b.npz`), not a satisfaction file. Not recoverable from filenames; not guessed.
- **cross-release** — one release.

---

## ⛔ CORRECTION, WRITTEN THE MOMENT THE ROUND RETURNED — the printed verdict is NOT this round's finding

The script printed `W-DIFFERENT-EMITTER`. **Do not read that as the result.** The pre-registered kill
said *"any value differs → different emitter"*, and comparing a quantity to **zero** instead of to
**its own null** is the failure this campaign has the most entries for.

| rule | shared criterion-cells | differing | **rate** |
|---|---|---|---|
| `oracle_k4` | 8,180 | 5 | **0.061 %** |
| `greedy_k4_fit1` | 7,868 | 9 | **0.114 %** |
| `indep_k4_fit1` | 7,516 | 11 | **0.146 %** |
| `topvar_k4` | 7,044 | 14 | **0.199 %** |
| `topwvar_k4` | 7,760 | 13 | **0.168 %** |

**A second judge changes essentially every value. One cell in a thousand is not a judge — it is a
defect somewhere else,** and the round's own branch had no way to say so.

**And the confound is in my join key, the very thing this README calls "the whole instrument."**
`select_core.py` emits `sat[pid][(i, letter)]` where `i` is the criterion's **original** index, while
I keyed on its **text**. A prompt whose criterion list repeats a text has two original indices with
the same text and *different* values — measured: **82 of 968 prompts (8.5 %) in `core_full.json`
carry a repeated criterion text**, plus 10 and 7 inside the two `oracle_k4` families themselves. My
dict keeps whichever came last, so two files selecting different duplicate instances register a
"difference" that is not a difference in the emitter at all.

**Verdict: UNVERIFIED.** Not OVERTURNED — a false retraction is as permanent as a false acquittal,
and the duplicate hypothesis is a hypothesis until it is measured. R423 measures it, with the join
repaired to a **set-valued** key (differing ⟺ the two value-sets are *disjoint*) and with every
differing cell checked against the default npz's own multiset.

⚠ **What survives regardless:** the `REAL (=)` control returned **0 differing of 7,728 shared** on
`topw_k4` vs `topw_k2` — two genuinely different files sharing an emitter. `select_core.py` performs
**zero judge calls**; it only looks values up. So *given a correct join*, a shared emitter forces
exact equality, and the separator itself is sound. It was the key, not the logic, that failed.

---

Findings, with their scope, live in the top-level README. This file states the design.
