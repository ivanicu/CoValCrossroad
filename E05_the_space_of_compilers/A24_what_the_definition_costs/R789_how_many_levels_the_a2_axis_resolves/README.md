# R789 · the A2 axis resolves 9 levels, the core clears the blind baseline — and R788's own proposed fix works for the wrong reason

`run.py` · `PREREGISTRATION.txt` · `results/ladder.json` · 27 arms × 968 prompts · 351 pairs ·
**WORLD A** · two hash seeds byte-identical, md5 `97aaba3995d901986df65b4200866d2d`

## THE DECISION THIS MAKES SAFE

**The A2 axis is not as coarse as `q`.** Under the codebase's own resolution rule (`|t| ≥ 2.801585`,
R725) the 27 arms fall into **9 levels** by adjacent gaps and **10** by the greedy construction —
against `q`'s **4** distinct values (R787). So R787's *"`q` destroys information"* survives as a
statement about **resolvable** distinctions, not merely about point estimates. **My pre-registered
downgrade branch did not fire**, and it was written to fire on my own most recent headline.

⭐ **And the released core clears the blind baseline resolvedly**: `coval_core` − `generic` =
**+0.01512 [+0.00746, +0.02283]**, MDE **0.01069**, `t` **3.96** → **BEATS**, and **BEATS** again
under the hierarchical bootstrap. **WORLD C is dead**: a cut-based clause ② can, in principle, do the
one thing it must.

## ⛔⛔ AND THEN THE SHAM KILLED THE FIX I PROPOSED ONE ROUND AGO

R788's NEXT said clause ② should compare **A2 against a stated cut**. A stated cut is a **scalar**,
and a scalar has no per-prompt vector — so the comparison loses the pairing that D3 says the MDE
depends on. The SHAM removes exactly that ingredient and holds everything else fixed:

| arm | vs the SCALAR cut 0.539126 | vs the MEDIAN REFERENCE's vector |
|---|---|---|
| `coval_core` | +0.02735 · mde 0.01351 · **BEATS** | +0.02735 · mde 0.01088 · **BEATS** |
| **`generic`** | +0.01223 · mde 0.01351 · **BELOW RESOLUTION** | +0.01223 · mde **0.00591** · **BEATS** |
| `gen` | −0.00395 · mde 0.01516 · UNRESOLVED | −0.00396 · mde 0.01214 · UNRESOLVED |

**The effect is identical to five decimals; only the MDE moves.** So the scalar cut would exclude the
blind baseline — the outcome R788 wanted — **entirely by being 2.29× less powerful on that arm.**
Across the population: **23 of 27** arms resolve against the scalar cut versus **25 of 27** against a
paired reference vector, mean sd **0.15333** versus **0.13103**.

**A definition that excludes an arm because its test got noisier has not become more discriminating.**
This is §4's *the control fails for its own reasons*, promoted from a control to a **formulation**:
the fix I proposed looks like it repairs clause ② and instead lowers its resolution.

## ⛔ AND MY OWN NEGATIVE CONTROL COULD NOT FAIL — CAUGHT AND REPAIRED IN THIS ROUND

The first run printed a pairing-destruction inflation of **7,523,259,381×** and **PASS**. Its sweep
was `names[:8]`, which contains **exact-duplicate arms** whose paired sd is **0**, so the ratio was
`perm_sd / 1e-12` and the criterion `infl > 1.0` could not fail. Repaired: degenerate pairs excluded
and counted, the band made two-sided (`1.02 < r < 10`), the sweep run over every pair.

| | |
|---|---|
| MDE inflation when the pairing is destroyed | median **1.529×**, mean **1.795×** over **342** non-degenerate pairs |
| exact-duplicate pairs excluded | **9** |
| R768's independently measured value | ×2.25 [2.18, 2.32] — on its **five near-identical** arms; the pairing buys most where the arms track most, so the two numbers are a population difference, not a contradiction |
| synthetic independent arms (must be ≈1) | **1.036×** |

## ⚠ THE POPULATION IS 27 NAMES AND 20 OBJECTS

**9 of the 351 pairs are an arm compared with a byte-identical copy of itself** — `generic ==
generic_reprov`, `topw_k4 == _detA == _detB`, `oracle_k4 == _oracle_kA == _oracle_kB`,
`greedy_k4_greedy_kA == _kB`, `indep_k4_indep_kA == _kB`. Each returns eff exactly 0.000000 with sd
exactly 0. So the honest counts are **20 distinct arms**, **342** non-degenerate pairs, and **30**
genuinely UNRESOLVED ones — and the "20 distinct A2 values" in D1 is not a fact about A2's resolution
at all, it is the number of distinct **objects**.

## E2 · THE LADDER, OVER THE WHOLE GRID — INCLUDING THE CELL THAT KILLS THE WORLD

| rule | threshold on `t` | adjacent | greedy | greedy level sizes |
|---|---|---:|---:|---|
| point | 0 | 20 | 20 | *(every distinct A2 its own level — degenerate)* |
| ci_only | 1.959964 | 10 | 11 | 6·3·2·2·4·1·2·1·1·2·3 |
| **strict / mde** *(the codebase's own rule, pre-registered)* | **2.801585** | **9** | **10** | 8·1·2·2·4·1·2·2·2·3 |
| conservative | 4.761549 | **5** | 7 | 9·4·4·3·2·2·3 |

⛔ **The world verdict is rule-dependent and the whole curve is published.** `strict_mde` gives 9 →
**WORLD A**. **The conservative rule gives 5, which is inside WORLD B's registered range.** The rule
was fixed in advance as the one `corebench/report.py` implements; had I pre-registered the
conservative rule, this round would report that the axis is no finer than `q`.

| specification | adjacent | greedy | resolved pairs |
|---|---:|---:|---:|
| seeds 31337 / 31338 / 31339 × NBOOT 600 / 1200 — **all six cells** | 9 | 10 | 305 |
| **hierarchical bootstrap** (prompts, then annotators within prompt) | **9** | **10** | **305** |

**Resampling annotators changes nothing** — the level structure, the pair count and every decisive
verdict are identical. The annotator layer is not this design's binding constraint.

## E2 · WHAT THE LEVELS ACTUALLY ARE

Emitted by `run.py` into `results/ladder.json` — **the first draft of this table was derived by hand
in this README and put `gen` and `genericpool16` in separate levels, which is false** (their gap has
`t` 1.69). The composition is now computed, and prose does not re-derive it.

| level | arms | A2 |
|---|---|---|
| 1 | **9 arms** — every sham, every random, `topvar_k4`, `topabs_k4`, `topwvar_k4` | 0.4828–0.5040 |
| 2 | **`gen`, `genericpool16`** — both prompt-blind, and not separable | 0.5352–0.5422 |
| 3 | `generic`, `generic_reprov` | 0.5514 |
| **4** | **`topw_k4`, `_detA`, `_detB`, `coval_core`** | **0.5642–0.5665** |
| 5 | `indep_k4_fit1` | 0.5941 |
| 6 | `indep_k4_indep_kA`, `_kB` | 0.6031 |
| 7 | `greedy_k4_fit1`, `oracle_k4_fit1` | 0.6106–0.6142 |
| 8 | `greedy_k4_greedy_kA`, `_kB` | 0.6226 |
| 9 | `oracle_k4`, `_oracle_kA`, `_oracle_kB` | 0.6283 |

⭐ **`coval_core` is UNRESOLVED from `topw_k4`**: +0.002297 [−0.00378, +0.00844], MDE 0.00853, `t`
0.75 — **R768's five-arm finding reproduced at population scale**. The released core sits in a level
it shares, and every arm above it reads the target.

## E4 · THE CUT, AND WHAT IT ADMITS

Cuts admitting `coval_core` while excluding `generic` occupy a band **0.01512** wide — **1.41× that
pair's own MDE**, so the band is real but thin. **At any such cut 14 arms are admitted**, including
all four `oracle_k4` variants, which read the target. Widest plateau in the whole axis: between
`topwvar_k4` and `gen`, width **0.03122**, `t` 5.91.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 27 arms · 968 prompts · annotators/prompt median **16**, max **46** · **0** A2 mismatches against R782 beyond 1e-9 | PASS, else exit 2 |
| PLACEBO | an arm against itself: eff **0.000000**, CI **[0, 0]**, UNRESOLVED | PASS |
| POSITIVE | δ=0 **UNRESOLVED** (the floor fails, as required) · 0.002 UNRESOLVED · 0.005 UNRESOLVED · 0.01 **BELOW RESOLUTION** · 0.02 **BEATS** · 0.05 **BEATS**; empirical MDE **0.01331** | PASS, band non-degenerate |
| POSITIVE (constant plant) | resolves at **every** non-zero δ because a constant difference has sd 0 hence MDE 0 | **DEGENERATE, and predicted in the docstring before the run — it does not gate** |
| NEGATIVE | pairing destroyed → MDE ×**1.529** median; synthetic independent arms ×**1.036** | PASS **after repair** |
| SHAM | the second arm removed (a scalar cut): 23 of 27 resolve, mean sd 0.15333 | ⭐ **it demotes `generic` at fixed effect** |
| NEUTRAL | a non-arm per-prompt vector: 25 of 27 resolve, mean sd 0.13103 | the ingredient absent, not misdirected |
| NOISE FLOOR | annotator split-half, 20 draws: **0.003416** | ⚠ MARGINAL; see the unit note |

⚠ **UNIT NOTE, and it corrects a number this round itself printed.** The split-half floor is a
**per-arm marginal** quantity while every gap here is a **paired** difference in which the annotator
draw is common to both arms. So *"14 of 26 gaps sit below the annotator floor"* is **not a
like-for-like comparison and licenses nothing**. All **8** of the ladder's resolved adjacent gaps
exceed it, and the instrument that *is* like-for-like — the hierarchical bootstrap — leaves the
ladder at 9/10.

## MULTIPLICITY

**351 cells tested.** Surviving the verdict rule (CI excludes 0 **and** |eff| ≥ MDE): **305**;
**not** surviving: **46** (39 UNRESOLVED of which 9 are exact duplicates, 7 BELOW RESOLUTION).
Surviving BH at q=0.05 on the bootstrap p with no MDE floor: **311**; not surviving: **40**. BH's
threshold at rank *k* is `q·k/C`; `q/C` would be Bonferroni.

## WHAT DIED

- **WORLD C** — the core is resolvedly above the blind baseline, `t` 3.96, under both bootstraps.
- **R788's NEXT as stated** — "A2 against a stated cut" is not a neutral simplification. It costs
  the pairing, inflates `generic`'s MDE by 2.29×, and changes that arm's verdict **at an effect that
  did not move**.
- **my own NEGATIVE control's first version**, which could not fail.
- **this round's own "14 of 26 gaps below the annotator floor"**, retracted in the same run for
  comparing a marginal quantity to a paired one.
- **"27 arms"** as a population statement — it is 20 objects and 7 aliases.
- **this README's own first level table**, hand-derived, which split one level into two.

## WHAT SURVIVES

R787's *"`q` collapses 19 levels into 4"* — sharpened, because 9 of those levels are resolvable and
not merely distinct. And R768's finding that `coval_core` cannot be ordered against the arms clause ②
admits alongside it: measured here on the full population, at `t` 0.75.

## SCOPE

population 27 named arms / 20 distinct objects × 968 prompts · instrument A2 per prompt over all
annotators; estimator the paired mean difference; 1,200 bootstrap draws over prompt clusters, 600
hierarchical · baseline the other arm, and for the sham the class median A2 **0.539126** · regime
first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether A2 is the RIGHT target for clause ② | an external gold standard — an external gold standard for what a core should preserve — the register at `corebench/score.py:34`. ⚠ **R787–R791 cited this as "the wall (R631)"; that citation is FALSE — R631 is `the_unrecorded_retraction`. Corrected in R792.**. This round prices the axis, not its choice |
| a cut validated outside this release | a second values-annotation release with this schema |
| independently replicated | a second designer; the session prompt forbids agents |
| the judge's own pass-to-pass variance | repeated judge passes of one arm; the release ships one per arm (R788) |

## NEXT

Two rounds have now attacked clause ②'s *statistic* and both attacks landed on its **variance term**
— R788 measured that `q_resolved` pays 0.235 for low variance, and this round measured that removing
the reference class pays 2.29× on the blind baseline alone. Computed by this round's `run.py`, the
levels the axis resolves number 9 while the arms number 20, so more than half the population is
inside a level with something else. The step is therefore **not** another statistic: it is to ask what
clause ② is entitled to say about an arm that shares a level with the released core — measured in
R789 as `coval_core` against `topw_k4` at `t` 0.75 — because a definition that admits a set it cannot
order is making a **membership** claim, while the three formulations this arc has tried are **ranking**
ones: `q` (R787), `q_resolved` (R788) and a stated cut (R789).
