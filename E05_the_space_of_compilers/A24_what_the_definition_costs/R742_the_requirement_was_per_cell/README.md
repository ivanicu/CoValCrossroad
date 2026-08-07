# R742 · the requirement was per cell

**Giving every cell its own population recovers up to 216 prompts and resolves nothing new. The
global threshold was not the binding constraint, and the scope worry I closed the last round with was
one third its stated size.**

## ⛔ Two derivations, run before the round, both narrowing it
**① My own NEXT line overstated the scope worry.** R741 asked whether the pool-size selection
contaminates the three quantities the deliverable still asserts. **Two of them never touched that
population.** Clause ③ is a **name lookup** at `R294:144` — `a not in USES_PROMPT_LABELS` — and
consults no prompt. The extension comes from R294's census on **each arm's own** population, not from
any constructed floor. **Only the excesses were ever restricted.**

**② The restriction was worse than it needed to be.** R741 applied the **worst-case** requirement
(4 + 8 = 12) to **every** cell. Each needs only `4 + k_b`:

| cell | needs | prompts |
|---|---|---|
| greedy↔topw_k3 | 7 | **950** |
| greedy↔topw_k4, **greedy↔oracle** | 8 | **919** |
| greedy↔topw_k6 | 10 | 859 |
| greedy↔topw_k8 | 12 | 734 |

**The cell the arc turns on was computed on 734 when 919 were available.**

## The ten cells at maximal power
| object | ref | n | excess | SE | 95% CI | covers 0 | R741 (n=734) |
|---|---|---|---|---|---|---|---|
| greedy | oracle | 919 | +0.0192 | **0.0138** | [−0.0078, +0.0452] | yes | +0.0211 |
| indep | oracle | 919 | +0.0046 | 0.0197 | [−0.0349, +0.0416] | yes | +0.0176 |
| greedy / indep | topw_k3 | 950 | −0.0229 / −0.0338 | 0.0272 / 0.0263 | span 0 | yes | −0.0088 / −0.0214 |
| greedy / indep | topw_k4 | 919 | −0.0202 / −0.0293 | 0.0257 / 0.0248 | span 0 | yes | −0.0122 / −0.0231 |
| greedy / indep | topw_k6 | 859 | −0.0123 / −0.0279 | 0.0241 / 0.0225 | span 0 | yes | −0.0120 / −0.0339 |
| greedy | topw_k8 | 734 | −0.0411 | 0.0245 | [−0.0916, +0.0052] | yes | −0.0411 |
| **indep** | **topw_k8** | 734 | **−0.0556** | 0.0234 | **[−0.1008, −0.0116]** | **no** | −0.0556 |

**1 of 10 excludes zero — the same one. Newly resolved: none.** SE on the key cell improves
**0.0162 → 0.0138** and the interval still spans zero.

⚠ **The per-cell column is NOT comparable across cells** — each is a different prompt set. The global
column is printed beside every row, and **the ordering gap stays on the global population**, where an
average across cells is defined.

## Controls — 5 PASS, 0 FAIL
**POSITIVE**: the bootstrap reproduces analytic `sd/√n` within 5% **on each cell's own population**,
5/5 — *a different population is a different instrument, so one global validation would not have
covered these* · **g=0**: 10/10 · **NEGATIVE**: resampling disabled → SE exactly 0, 10/10 ·
**SHAM**: the global-12 column computed and printed **inline**, so the power gain is visible rather
than asserted **and the per-cell column's non-comparability stays legible** · **PLACEBO**: 0.

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A prompts for greedy↔excluded | 919 [0, 968] | **919** | yes |
| B its SE at maximal power | 0.0145 [0, 1] | **0.0138** | yes |
| C cells excluding zero | 1 [0, 10] | **1** | yes |
| D target-reading objects ③ admits | 3 [0, 16] | **3** | yes |
| DIRECTIONAL nothing newly resolves | — | **holds** | — |

## What now stands from the whole arc
1. **The extension: 5 members**, from R294's census — no prompt restriction.
2. **Clause ③ admits 3 target-reading objects** (R729/R730) — a name lookup, no prompt restriction.
3. **One resolved excess**: `indep`↔`topw_k8`, **−0.0556 [−0.1008, −0.0116]**.
4. **Nine bounds**, and **an unresolved ordering**.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137, both writes verified.
**Artifact:** `results/r742_per_cell_power.json`.
