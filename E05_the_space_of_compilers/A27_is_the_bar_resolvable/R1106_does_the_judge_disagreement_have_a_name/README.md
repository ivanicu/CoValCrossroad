# R1106 — it is **both**, and they split the casualties **5 / 4**. Compression shrinks every margin by **29%**; a real reordering (**Spearman 0.663** vs **0.938** for pure compression) takes the rest.

**The decision this round makes safe:** whether R1105's collapse is repairable by renormalising the
comparator. **Partly.** Five of the nine sign flips are what compression alone predicts; four are
not — and the four have a name.

## ⛔ The arithmetic trap, labelled before the run

*That the ordering changed somewhere* is **already forced** by R1105's committed table (`coval_core`
leads `generic` under 2B, trails it under 8B). Re-reporting that is 1+1=2. **The open question is
whether the reordering exceeds what a pure scale change produces anyway** — a judge with a smaller
dynamic range compresses margins toward zero, and small margins then cross zero *without the judge
disagreeing about the ordering at all*.

⛔ **And the obvious contrast has n=2, measured not assumed.** Counting distinct criterion sets across
968 prompts in each `core_<arm>.json`: **only `generic` and `genericpool16` have exactly one** —
every other arm has 398–968. A `fixed vs prompt-specific` arm contrast has two units on one side and
both are the comparators. **So the unit is the prompt and the quantity is the margin over the
comparator**, which cancels the level shift by construction.

## ⭐ The result

| quantity | value | bootstrap CI | threshold |
|---|---:|---|---|
| **Spearman** on arm levels (43 arms) | **0.6631** | [0.6358, 0.7722] | ≥ 0.90 for world A |
| Kendall | 0.4355 | — | — |
| **R²** of the margin regression | **0.9063** | [0.8897, 0.9176] | ≥ 0.80 for world A |
| **slope** (the compression factor) | **0.7142** | [0.6907, 0.7353] | — |
| intercept | −0.0251 | — | — |

⭐ **World A (pure compression) is KILLED — but not because compression is absent.** The slope says
margins shrink **29%** and R² says compression explains **91%** of their variance. What kills world A
is the rank correlation: **0.663**, against **0.938** for a synthetic compression world built from
the 2B data itself.

Stable across the specification curve: baseline `genericpool16` gives slope 0.7157, R² 0.9057,
Spearman 0.6619; the level-normalised variant is identical to four places.

## ⭐⭐ Which flips does compression explain? 5 of 9 — and the other 4 have a name

| arm | 2B margin | predicted 8B by compression | observed 8B | residual | compression explains? |
|---|---:|---:|---:|---:|---|
| `oracle_k4` | +0.0770 | **+0.0299** | −0.0283 | **−0.0582** | ❌ |
| `oracle_k4_fit1` | +0.0628 | **+0.0198** | −0.0325 | **−0.0522** | ❌ |
| `greedy_k4_fit1` | +0.0593 | **+0.0173** | −0.0290 | **−0.0462** | ❌ |
| `indep_k4_fit1` | +0.0427 | +0.0054 | +0.0044 | −0.0010 | ❌ (still ahead) |
| `topw_k8` · `topw_k6` · `topw_k4` · `topw_k3` | +0.008…+0.013 | **negative** | negative | −0.005…+0.008 | ✅ |
| `coval_core` | +0.0151 | **−0.0143** | −0.0072 | +0.0071 | ✅ |

⭐ **`coval_core`'s flip is a scale effect.** Its residual is **+0.0071** — it did *better* than
compression predicted and still crossed zero, because the compression line already puts it at
−0.0143. **Renormalising the comparator would recover it.**

## ⭐ The residual has a shape, and the release's own code names it

| rule | residual | fits the target? | set-aware? |
|---|---:|---|---|
| `oracle_k4` · `oracle_k4_fit1` | **−0.0582 · −0.0522** | yes | **yes** (searches combinations) |
| `greedy_k4_fit1` | **−0.0462** | yes | **yes** (sequential, conditional) |
| `indep_k4_fit1` | −0.0011 | yes | **no** (scores criteria independently) |
| `topvar_k4` · `topwvar_k4` | +0.0182 · +0.0175 | no (reads satisfaction, not the target) | — |
| `topw_k1…k8` · `topabs_k4` · `random_k4_s0` · `full` | **−0.0092 … +0.0118** | no | — |

**The two rules that fit SET STRUCTURE to the human target under the 2B judge's satisfaction are the
ones that fall beyond compression. The rule that fits the same target INDEPENDENTLY does not.**
`select_core.py`'s own comment already draws that line: *"the oracle-minus-indep difference isolates
SET STRUCTURE from mere fitting."*

⚠ **n = 2 rules, 3 arms.** This is a **pattern consistent with** set-structure overfitting to the
first judge, not a tested claim, and it is stated with its population rather than its story.
⭐ It is corroborated from a different cell: R1105 measured that `oracle_k4`, `greedy_k4_fit1` and
`indep_k4_fit1` **all return** under `_08bR` — the rule **re-run** under the 8B judge — which is what
refitting the set structure to the new instrument should do.

## Controls — 4, all green after one repair

| control | result |
|---|---|
| PLACEBO 2B against itself is exact (ρ = 1, slope = 1, R² = 1, residuals 0) | PASS |
| **SYNTHETIC** world A rebuilt from the 2B data **is recognised** as compression — ρ 0.9379, R² 0.9929 | PASS |
| POSITIVE a planted swap is flagged by the two largest residual **changes** | PASS |
| NEGATIVE the 2B margins are not degenerate | PASS |

⭐ **The synthetic world is what makes the low ρ readable.** Compress the 2B per-cell scores about
their own mean by the observed variance ratio (0.953), add noise matched to the observed per-cell
residual sd (0.1674), and run the whole pipeline: the instrument returns **ρ = 0.9379, R² = 0.9929**.
**So the design can recognise compression when it is there**, and the real **0.6631** is not the
design failing to see it.

⛔ **The positive control failed on the first run, for its own reasons.** v1 ranked by **|residual| in
the planted run** and required the swapped pair to be the top two. It flagged `indep_k4_fit1` and
**`promptecho`** — because `promptecho` already carries a large *real* residual (−0.0277) and adding
a plant drags the fitted line, so a near-twin can outrank the plant. **A plant laid on top of real
structure cannot top an absolute list unless it exceeds everything real — and this round's finding is
that real structure exists.** §4's *the control fails for its own reasons*, sub-kind ③: it targeted a
different statistic. Repaired to the **change** in residual, which separates cleanly: **0.2815** and
**0.1717** for the swapped pair against **0.0591** for the next arm.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| whether either judge is **correct** | **N/A** | an external gold standard |
| a fixed-vs-prompt-specific **arm** contrast | **N/A** | more than 2 fixed arms; the release ships exactly two and both are comparators — **measured here, not assumed** |
| a **tested** set-structure claim | **N/A at n=2 rules** | more set-aware fitted rules, or the same two swept over k. The observation is reported with its population |
| Qwen3B and Phi | **N/A** | their comparator files; `E04/…/R164_instrument/` ships `sat_full_*` and `sat_core_*` only |
| cross-release | **N/A** | a second release |

`run.py` · `results/compression_or_reordering.json`
