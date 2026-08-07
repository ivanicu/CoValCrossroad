# R1074 — headline or incidental? ⛔ **The reading exposed a unit error: the "6 values" are 6 occurrences of 3 distinct ones — and by the same rule every count in this chain is occurrences.**

**The decision this round makes safe:** which unstored values are worth writing back. **Two** — and
the count of candidates was never 6.

## ⛔⛔ The unit correction, which the reading forced

R1073 built its list by deduplicating clause tokens **by offset**, so the **same value at two
positions counts twice**.

| | occurrences | **distinct values** |
|---|---:|---:|
| unstored clause decimals (R1070's "31") | 31 | **18** |
| single-carrier (R1073's "6") | 6 | **3** |

`0.009103` appears **3×**, `0.559311` **2×**. ⭐ **By the same rule R1073's `6 / 15 / 10` and R1070's
`31` are OCCURRENCE counts stated as value counts.** Both are now reported rather than silently
switched. **This is the same unit failure the window has caught repeatedly — and it survived four
rounds because every one of them inherited the population from the last.**

## Result — 3 distinct values, read

| value | round | section | role |
|---|---|---|---|
| `0.009103` | **R981** | *"Two controls failed before one passed"* | **incidental** |
| `0.559311` | **R1000** | *"④'s inertness is a DERIVATION"* | candidate-finding |
| `0.551354` | **R782** | *"E2 · R604's QUESTION, CLOSED — WORLD B"* | candidate-finding |

**Candidate-finding 2 of 3.** And the sentences are printed because they, not the count, are the
evidence:

- `0.009103` — *"That is not a coverage finding, it is a **population error** — `0.009103` is in the
  statement, but…"* ⭐ **R981 itself calls it an error being corrected.** Persisting it would store a
  number the round wrote to disown.
- `0.551354` — `| A2 | POOL[0:4] 0.550436 · generic 0.551354 |` — a comparator mean in a result table.
- `0.559311` — a bar quoted beside `0.482016` in a derivation discussion.

## The proxy ledger, written before the run

| | |
|---|---|
| **PROPERTY** | the value is a finding worth persisting |
| **PROXY** | it appears outside a controls/limitations section |
| **IMPLICATION** | `controls/limitations ⇒ incidental` **SOUND** · `result section ⇒ finding` **NOT SOUND** |
| **WITNESS** | a result section also carries baselines and quoted comparisons — `0.551354` is exactly that |
| **SAFE SIDE** | result placement returns **CANDIDATE**, never CONFIRMED; the sentence is printed |

## Controls

- **POSITIVE** — every value must locate a section in its carrying README: **True**.
- **NEGATIVE** — an absent string yields no section: **True**.
- **PLACEBO** — a README with no headings falls back to `unsectioned` and is reported as such.
- **MULTIPLICITY** — all values reported with section **and** sentence, not a count alone.

## IMPOSSIBLE here

- **whether a result-section value is a finding or a quoted baseline** — the proxy is unsound in that
  direction **by construction**, which is why the sentences are printed. **SETTLES: IN-RELEASE** by
  reading; **three sentences is the entire remaining cost.**

`run.py` · `results/role_of_the_six.json`
