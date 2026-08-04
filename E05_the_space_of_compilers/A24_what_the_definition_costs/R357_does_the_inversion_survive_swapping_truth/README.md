# R357 — the gauge test partitions R356: the inversion survives, the "forced agreement" does not

**The decision this makes safe:** *may R356's two halves be quoted together?* **No.** One is
invariant under swapping which judge is called truth; the other is not, and is withdrawn.

## Result — `W_ASYMMETRIC_PARTITIONED`. Four controls PASS, and the gauge provably moved.

Spearman is symmetric, so the **observed ρ is identical in both directions**. What moves is the
**null**: whose ordering is truth, whose `se` is which, and the fitted slope.

| cell | ρ | 2B is truth | 0.8B is truth | status |
|---|---:|---:|---:|---|
| `random_k` ① | −0.512 | **0.00%** | **0.00%** | **INVARIANT · flagged** |
| `random_k` ② | −0.429 | **0.00%** | **0.00%** | **INVARIANT · flagged** |
| `topw_k` ① | +0.810 | 20.16% | **1.43%** | **GAUGE-DEPENDENT** |
| `topw_k` ② | +0.667 | 9.72% | **1.97%** | **GAUGE-DEPENDENT** |

**Survives:** R356's **inversion** finding. `random_k` sits at the 0.00 percentile of its own null
in *both* directions — the disagreement is a property of the **pair**, not of the reference choice.

**⛔ Withdrawn:** R356's reading of `topw_k` as *"inside, therefore forced, therefore carries no
information."* Under the other direction it is resolvably **below** its band.

## The direction is consistent even where the verdict is not

Both gauge-dependent cells sit in the **low tail in both directions** — 20.16% / 9.72% and 1.43% /
1.97%. **It is the resolution that moves, not the sign.**

> So *"`topw_k` agrees less than its separation forces"* is the surviving statement.
> *"Resolvably so"* is what the gauge decides, and it decides differently by direction.

R356 called it `inside` and moved on. That was the wrong thing to conclude from a number at the
**20th percentile of its own null** — low, not central.

## Why the two directions differ: regression to the mean, and the naive reversal I avoided

An OLS slope is **not symmetric**: `β_yx · β_xy = R²`.

| clause | β(2B→0.8B) | β(0.8B→2B) | product | R301's R² | `1/β` would have been |
|---:|---:|---:|---:|---:|---:|
| ① | 0.4340 | 1.4112 | 0.6124 | 0.6124 ✓ | **2.3044** |
| ② | 0.4006 | 1.3595 | 0.5447 | 0.5447 ✓ | **2.4960** |

**The reverse slope is an EXPANSION (1.41), not a reciprocal (2.30).** Taking the noisier judge as
truth and fitting an expansion **inflates the apparent separation**, tightening the null — the
`topw_k` floor rises from **+0.66 to +0.83** at `r=0.6`. That is the whole mechanism, and it is the
classical one.

⚠ **The product identity is an independent cross-check, not decoration.** My plain OLS reproduces
R301's cluster-bootstrap β to four decimals (0.4340, 0.4006) and the product lands exactly on
R301's committed R². Two different estimators, same numbers.

## Controls

| | returned |
|---|---|
| **PLACEBO** — family against itself, 8 cells | ρ = 1.0 exactly |
| **POSITIVE** — exact reversal flagged below the band | **8/8**, both directions |
| **g=0** — exact null (other = β·truth, no noise) not flagged | **8/8** |
| **GAUGE ACTUALLY MOVED** | slopes differ ✓ · bands differ ✓ · max band shift **0.2827** |
| reproducibility | two runs **byte-identical** |
| multiplicity | 2 directions × 2 families × 2 clauses = 8 cells, all printed with percentiles |

**The fourth control is the one this round needed and R356 did not.** A gauge test whose two code
paths compute the same numbers **passes trivially** — the purest *check that cannot fail*. So the
two directions' slopes and null bands are required to **differ** before any invariance claim is
allowed. Both directions run **R356's own imported `spearman` and `null_band`**, so this tests the
framing and not a re-implementation.

## ⛔ Two of my own claims corrected, both by checking rather than assuming

**① The fit population, not the estimator.** v1 fitted the slope on all 41 arms and got β = 0.4535
against R301's 0.4340. R301 holds out **`promptecho` and `promptecho_sham`**, which cover **398
prompts, not 968** — a *different population*, whose effects must not enter a slope estimated over
the others. Matched, β reproduces exactly. **Reading the gap as an estimator difference and moving
on was the flattering explanation available.**

**② A third judge is not "a drop-in".** R356's next-gradient line, and R301's register before it,
said so on the grounds that the prompt contract is byte-identical between `covalx/judge.py` and
`E01/R04/run.py`. **The contract is; the model is not.** The local store holds exactly two Qwen3.5
checkpoints — 0.8B and 2B — plus one quantised GGUF of a different family and an "uncensored"
fine-tune unsuited to a values judge. A third reading needs a **download and a second serving
stack**. The register entry is corrected from `NOT-ATTEMPTED` to
**`NOT-ATTEMPTED-AND-NOT-CHEAP`** — an availability claim in the flattering direction is still an
availability claim.

## Register — what this site cannot do

| criterion | status |
|---|---|
| **which judge is right** | **N/A** — both nulls are self-consistent. Only a third reading estimates the true ordering independently of either judge, and see ② above for what that costs |
| **n<5 families** | excluded by R356's stated rule; Spearman is 4-valued at n=3 |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"`topw_k`'s +0.81 is forced by its separation and carries no information."*

**It sits in the low tail of its own null in both directions, and is resolvably below in one.**

Artifact: `results/r357_gauge_swap.json`, source-stamped. Input: R301's `judge_slope.json`,
`sha256[:16] 4041dd0bdc6077f6`.
