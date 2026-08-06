# R809 · B-SPECIFIC withdrawn — on a scale where λ cancels, the fitted arms rise LESS than honest ones

`run.py` · `PREREGISTRATION.txt` · `results/lambda_free.json` · 968 prompts × 5 arms + 2 synthetic ×
4 j · **WORLD B** — the branch that withdraws the previous round's finding · two hash seeds
byte-identical, md5 `4f2330e786d79fbd8a9fa13d0a6dfe71`

## THE DECISION THIS MAKES SAFE

**R808's B-SPECIFIC is withdrawn.** The fitted arms do not converge on their fit target faster than
arms that never saw a label — that reading was the multiplicative trap, for the third time in four
rounds.

| estimand | contrast | |
|---|---|---|
| E1 · **additive** (R808's NEXT as posed) | **+0.0242 [−0.0606, +0.1131]** | contains 0 |
| ⭐ E2 · **log**, where λ cancels by derivation | **−0.1317 [−0.4044, +0.1397]** | **contains 0, and points the other way** |

## ⛔ THE ARITHMETIC, FOUND BY CHECK #411 BEFORE THE BOOTSTRAP RAN

Every disattenuated value is `raw_slope / λ_j`, and **λ_j falls with j**: 0.5834 · 0.5658 · 0.5546 ·
0.4954. So every j=8 value carries a **common multiplicative inflation**, and an arm *starting
higher* collects a larger *absolute* rise for free.

> **[DERIVATION]** `log dis(a,j) = log raw(a,j) − log λ_j`, and λ_j is common to all arms at a given
> j — so it **cancels exactly** in a difference of log-rises between two arms.

## ⭐ E4 · AND THE DECOMPOSITION IS THE WHOLE STORY

| | |
|---|---|
| fitted arms **start** at | **0.383** |
| honest arms **start** at | **0.195** |
| ratio, before anything about *rising* is measured | **1.97×** |
| rises, additive scale | +0.122 vs +0.098 → **1.25×** |
| rises, **log** scale | +0.276 vs **+0.408** → **0.68×** |

**R808's "the fitted arms rise twice as fast" was the fitted arms starting twice as high.** In
relative terms they rise *less*.

| arm | j=1 | j=8 | additive | log | ratio |
|---|---:|---:|---:|---:|---:|
| `oracle_k4_fit1` | 0.416 | 0.559 | +0.142 | +0.294 | 1.341 |
| `greedy_k4_fit1` | 0.397 | 0.514 | +0.117 | +0.258 | 1.295 |
| `indep_k4_fit1` | 0.336 | 0.444 | +0.107 | +0.277 | 1.320 |
| `coval_core` (honest) | 0.204 | 0.282 | +0.078 | +0.322 | 1.380 |
| `topw_k4` (honest) | 0.185 | 0.304 | +0.118 | **+0.494** | **1.639** |
| `_target_full` (the fit target) | 0.483 | 0.936 | +0.453 | **+0.662** | 1.939 |
| `_leakcopy` (placebo) | 1.000 | 1.000 | +0.000 | **+0.000** | 1.000 |

⭐ **`topw_k4` — which never saw a human label for the prompt — has the steepest log-rise of any real
arm.** That single row is the finding: relative sensitivity to the proxy's identity is not a property
of having been fitted.

## ⛔ AND R808's CONTRAST WAS INSIDE ITS OWN SPLIT NOISE

R808 reported **+0.094** against a threshold of **0.079**, averaged over 20 splits. Measured here,
the **across-split sd of the log contrast is 0.1077** — larger than R808's entire contrast. The
single-split additive estimate is **+0.0242** where R808's 20-split average was +0.094, and both sit
inside that spread. **A threshold built from per-arm sds was never going to bound a contrast whose
own split-to-split variation is bigger than the effect.**

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R808's **whole** B table reproduced — all 4 λ_j and all 20 disattenuated cells, to 1e-6 | PASS, else exit 2 |
| D4 | λ_j falls with j — the round's own premise, checked rather than assumed | PASS |
| PLACEBO | the pure leak copy's log-rise: **+0.000000000** | PASS — exactly 0 |
| POSITIVE | `_target_full`, the fitted arms' **actual** fit target, log-rise **+0.6620** — the largest of any arm (next +0.4943) | PASS; band floor **+0.4081** < fitted < ceiling **+0.6620** |
| g=0 | the placebo must **not** rise, and does not | PASS — the control can fail |
| NEGATIVE | **arm-label permutation, EXACT over all 10 ways to split 5 arms 3/2**: null [−0.1317, +0.1021]; the real fitted/honest split ranks **1 of 10** | PASS **after repair** |
| NOISE FLOOR | across 20 independent splits, sd of the log contrast **0.1077** | the contrast is 1.22× it |
| LOG DOMAIN | cells with a non-positive disattenuated value: **0** — the log estimand is defined everywhere | stated, not assumed |

⛔ **The negative control failed first, and destroyed nothing.** It permuted `lk8[pm]` **and**
`arm8[a][pm]` with the *same* permutation — and a regression slope is **invariant to reordering
(x, y) pairs**. The null came back as a point mass **[−0.1317, −0.1317]**, exactly the observation,
which is the signature of a permutation that did not permute. Repaired to the null the estimand
actually rests on — the **arm-label** split — which with 5 arms is exactly enumerable rather than
sampled.

⚠ **And the real split ranks 1 of 10 — the most negative of every possible 3/2 labelling.** Under
B-SPECIFIC it should have ranked last.

## MULTIPLICITY

5 arms × 4 j × {additive, log} reported in full. BH q = 0.05 over the per-arm log-rises: **4 of 5
survive; `coval_core` does not** — named, not omitted.

## WHAT DIED

- **R808's B-SPECIFIC** — withdrawn. On the λ-free scale the contrast contains zero and points the
  other way, and the additive contrast contains zero too once it carries a CI.
- **"the fitted arms track the specific labels they were fitted to"** — not supported by this design.
- **my own negative control**, which permuted nothing.

## WHAT SURVIVES

R808's **A-axis** invariance, untouched: the disattenuated scale moved 0.0154 while its instrument
sharpened 2.3×. And R807's scale itself — the fitted arms still sit at 0.50–0.65 of a pure copy of
the leak. **What is withdrawn is the claim about how that position CHANGES as the proxy sharpens**,
not the position.

## SCOPE

968 prompts × 4 responses · annotators split by index parity; y-side a fixed half of parity-0,
x-side 4 from the complement · leak's modal class from j ∈ {1,2,4,8} parity-1 annotators · 5 named
arms + `_target_full` + `_leakcopy` · paired bootstrap over prompts, NBOOT 1,200, one fixed split ·
20 independent splits for the noise floor · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a λ that does not move with j | a proxy whose reliability is constant across its own construction; λ_j falling is a property of the object and is why the log scale is used — **checked** as D4 |
| more than 10 label permutations | more arms; with 5 the null is exact rather than sampled, which is better, and the count is stated |
| separating "rises less" from "already saturated" | a proxy that can exceed the full parity-1 set; at j=8 it already **is** the fit target — **checked**, and it is why `_target_full` is the ceiling |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The B-axis is closed: relative sensitivity to the proxy's identity does not distinguish fitted from
honest arms. Measured in this round's `run.py`, `topw_k4` — which uses no human label for its prompt
— has the steepest log-rise of any real arm at **+0.494**, against the three fitted arms' +0.294, +0.258 and
+0.277. What still separates the two groups is **level**, not slope: fitted arms sit at
**0.383** against honest **0.195** at j=1, a ratio of **1.97×**. That level is R807's finding, and
R808's A-axis sweep is the one attack it has survived.

The step is to attack it on an axis this arc has held fixed throughout: **the arm's own k**. The
three fitted arms in this round are k=4 by construction (`sat_*_k4_fit1.npz`), while `genericpool16`
carries 16 criteria and still scores below them — so size and fitting are confounded throughout this
round's table. Sweep the fitted arms' k over {2, 4, 8, 12} via `select_core.py --rule oracle_k --k <k>
--fit-parity 1` and re-measure the level gap at matched k. If it closes, the fitted route's advantage
is size; if it holds, R807's 0.50–0.65 is about fitting after all. That needs a selector run per k
and no judge pass, and its outcome is not forced.
