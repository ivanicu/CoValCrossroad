# R1071 — recording failure, or absent from the record? ⭐ **31 of 31. It is a recording failure. Nothing in the clause is unsupported.**

**The decision this round makes safe:** what R1070's `31 unsourced` actually means. **Rounds reported
values they never persisted** — the remedy is a writing habit, not a search.

## Result

| | |
|---|---:|
| clause decimals | 38 |
| unstored in any artifact (R1070) | **31** |
| **found in the committed prose record** | **31 of 31 = 1.000** |
| **appearing nowhere at all** | **0** |
| **measured floor** — random decimals at matched precision, 3 seeds | **[0.032, 0.161]** |
| **SHAM** — same values searched in the release data, which cannot contain them | **0 of 31** |

⭐ **The floor and the sham together are what make `1.000` a measurement.** A made-up decimal at the
same precision is found 3–16% of the time; the release data yields **zero**. So "found" means found,
not "these digits occur in any large text."

## ⛔ The negative control caught contamination — twice over

1. **My sentinel `0.987654321` was FOUND** — because **R1070's `run.py`, written minutes earlier,
   contains it as *its* sentinel**. Replaced with a fresh one.
2. ⭐ **And the same contamination was far worse for the real question.** The corpus included
   **R1067–R1070 — the very rounds that quote these clause decimals wholesale.** "Found in the prose
   record" would have been trivially true for anything the audit rounds mentioned. **That is R1070's
   *a quoter is not a source*, one level along.** Rounds from **R1067 on are excluded**; they are
   downstream of the clause, so finding a value there is no evidence it was ever measured. Commit
   bodies are skipped by the same count.

**Without that exclusion this round would have reported `1.000` for the wrong reason** — and reported
it as a clean result.

## Controls

- **POSITIVE** — a decimal present in the record must be found (`0.009103`): **True**. A searcher never
  shown to find a present value cannot evidence an absence.
- **NEGATIVE** — a constructed-absent decimal found nowhere: **True**, after the sentinel was replaced.
- **SHAM** — the same 31 values searched in the **release data**: **0 hits**.
- **NOISE FLOOR** — random decimals at matched precision, 3 seeds: **[0.032, 0.161]**.
- **PLACEBO** — an empty candidate list exits **2**, never 0.

## What this does not settle

⚠ **Presence in prose is not provenance.** A README may quote a value it did not compute — exactly
what R1070 found on the artifact side. This separates **"in the record"** from **"absent"**; it does
**not** separate **"measured"** from **"quoted"**.

## IMPOSSIBLE here

- **whether a value found in prose was computed there** — the same limit R1070 hit.
  **SETTLES: IN-RELEASE** by reading each occurrence.

`run.py` · `results/prose_or_nowhere.json`
