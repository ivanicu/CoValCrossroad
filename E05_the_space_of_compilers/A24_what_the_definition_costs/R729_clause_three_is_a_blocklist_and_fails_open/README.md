# R729 · clause three is a blocklist and fails open

**Clause ③ — *"the evaluation annotator is held out from the core's own construction"* — is
implemented in `R294:72` as four literal arm names. Of the 16 arms today's population admits,
7 are built by a rule that reads the human target, and ③ excludes 0 of them.**

## The finding
`select_core.py:102` loads the human target for exactly three rules: **`oracle_k`, `indep_k`,
`greedy_k`**. R294's clause ③ is `a not in {oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1}`.

| arm | route A (tag) | route B (selections) | target-reading | ③ excludes |
|---|---|---|---|---|
| `greedy_k4_greedy_kA` / `kB` | greedy_k | greedy_k | **both** | ✗ |
| `indep_k4_indep_kA` / `kB` | indep_k | indep_k | **both** | ✗ |
| `oracle_k4_08bR` | oracle_k | oracle_k | **both** | ✗ |
| `oracle_k4_oracle_kA` / `kB` | oracle_k | oracle_k | **both** | ✗ |
| `topw_k3/4/6/8`, `topw_k4_detA/B` | topw_k | topw_k | no | ✗ |
| `coval_core`, `coval_core_2bA/2bB` | — | — | no | ✗ |

**Population-wide, 13 target-reading arms pass ③ by default.** ③ excludes exactly and only its four
literal names — the directional holds.

⚠ **This does not say those arms leak.** Whether target-reading changes this evaluation is R295's
question and is not re-opened. **It says ③ never asks.** And the defect is structural: every arm
built after the census passes unless a person edits a literal, so **the clause's coverage decays
with every round that adds an arm.**

## Two independent provenance routes, agreeing on all 82 arms both can classify
- **A — the tag.** Parsed against `select_core.py:203-206`, where the tag is *emitted by the
  builder* from rule + k + seed + fit parity, not typed by a person.
- **B — the content.** Per-prompt Jaccard over `core_*.json` selections against each rule's
  canonical arm. **Never reads the name.**

**0 binary disagreements over 82 arms.** 6 arms (`generic`, `promptecho`, `gen`, and their shams)
carry no rule prefix because `select_core.py` never emitted them — reported as **single-route**, and
the one route B calls target-reading (`promptecho`) is marked **UNCORROBORATED and excluded from
every count.**

## ⛔ Three of my own instrument errors, each caught by a control
1. **The positive control returned 3/4** — route B could not classify `oracle_k4` because it *is*
   the oracle representative and my code excluded an arm from matching itself. Repaired with a
   second reference per rule. **Now 4/4 on both routes.**
2. **I registered `B` at the wrong unit.** v1 counted 9-way *rule* disagreements — 54 of 88 — but
   the claim's unit is **binary**, and route B cannot separate `oracle`/`greedy`/`indep` **by
   construction**: `select_core.py:157` says `indep_k` is *"fitted exactly like the oracle, but
   blind to interactions"*. A greedy arm scoring closest to oracle is the instrument **working**.
   The 9-way count is kept as a diagnostic and is not the estimand.
3. **I counted `None` as a disagreement.** Route A returning `None` is the *absence* of a verdict,
   not a verdict of "no". A disagreement requires two verdicts. That alone moved B from 6 to **0**.

## Controls — 6 PASS, 0 FAIL
**POSITIVE**: both routes re-derive R294's own four names **from construction**, band
`floor 0 < t 4 ≤ ceiling 4` — *the instrument is not echoing the list it audits* · **g=0**:
`topw_k4`, `random_k4_s0` (satisfaction-blind, `select_core.py:72`) flagged by neither ·
**NEGATIVE**: core files shuffled across arms → agreement collapses 34 → 8/6/14 of 88, excluding
*"route B assigns by file size or coverage"* · **SHAM**: route B against the arm itself, comparison
target **absent** → 1.000000 · **PLACEBO**: 1.0 · **NOISE FLOOR**: route-B margin median 0.1762,
5th pct 0.0000, 0 arms called AMBIGUOUS.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A admits built target-reading | 7 [0, 16] | **7** | yes |
| B binary route disagreements | 0 [0, 95] | **0** | yes |
| C admits ③ excludes | 0 [0, 16] | **0** | yes |
| D target-reading arms ③ admits | 7 [0, 92] | **13** | yes |
| DIRECTIONAL ③ excludes only its literals | — | **holds** | — |

⚠ **D's point prediction was wrong** — I registered 7, thinking of the admitted arms only; the
population-wide count is 13. The interval absorbed it.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r729_clause3_blocklist.json` · every arm with both routes' verdicts.
