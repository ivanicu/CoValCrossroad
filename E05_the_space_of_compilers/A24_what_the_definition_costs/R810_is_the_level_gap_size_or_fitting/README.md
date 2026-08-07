# R810 · three quarters of the fitted advantage was size — and the remaining quarter is resolved

`run.py` · `PREREGISTRATION.txt` · `results/size_or_fitting.json` · 968 prompts × 2 fitted rules ×
4 k × 3 baselines · **WORLD B**, with the size reading carrying most of the effect · two hash seeds
byte-identical, md5 `9ef91acfa074e09c3d044bb8cdcbba4d`

## THE DECISION THIS MAKES SAFE

**Matched on size, the fitted arms' advantage falls by a factor of four — and does not reach zero.**

| k | n | fitted | `topw_k` | `random_k` | `POOL[0:k]` | **gap vs `topw_k`** |
|---:|---:|---:|---:|---:|---:|---|
| 2 | 734 | 0.6046 | 0.5574 | 0.4807 | 0.5556 | **+0.0472 [+0.0374, +0.0580]** |
| 4 | 734 | 0.6032 | 0.5689 | 0.4920 | 0.5568 | **+0.0343 [+0.0256, +0.0426]** |
| 8 | 734 | 0.5896 | 0.5735 | 0.5066 | 0.5497 | **+0.0160 [+0.0096, +0.0223]** |
| 12 | 734 | 0.5645 | 0.5528 | 0.5154 | 0.5482 | **+0.0116 [+0.0070, +0.0162]** |

*(common intersection — the 734 prompts attaining nominal k at every k)*

> **monotone decreasing · 4× smaller at k=12 than k=2 · BH q=0.05: 4 of 4 survive**

**Both halves are the finding.** R805's `+0.0553` and R807's 0.50–0.65 were measured at k=4 against
a 16-criterion pool; **most of that was size**. What survives matched is **+0.0116 [+0.0070,
+0.0162]** — small, resolved, and 6.8× the noise floor of 0.0017.

## ⛔ CHECK #412 · R809's NEXT NAMED AN INFEASIBLE INSTRUMENT

It proposed `--rule oracle_k` across k. `select_core.py` caps enumeration at **20,000**
combinations and **samples** above it, logging the arm as a lower bound. Measured candidate sets:
median **15**, max **39**, min **4**. Prompts over the cap: **k=2 → 0 · k=4 → 31 · k=8 → 367 ·
k=12 → 254** of 968. So the oracle's *identity* changes with k and the sweep would confound size
with sampling density. `greedy_k` and `indep_k` are sequential and linear, and are used instead.

## ⚠ D2 · THE CLOSURE IS PARTLY FORCED, AND THE PREREGISTRATION SAID SO BEFORE THE RUN

A fitted arm at k = n **is** `full` — selection has nothing left to choose — so the gap **must**
reach zero at k = n by construction. On this population the median candidate count is **16**, so at
k=12 the median prompt leaves only **4** criteria unselected. **Part of the shrinkage is algebra,
not evidence**, and the round is only entitled to the claim because it was written down first.

⭐ **But the shrinkage is not merely "less freedom to choose."** Selection freedom is
**non-monotone** — median `C(16,k)` runs 120 · 1,820 · 12,870 · 1,820 at k = 2 · 4 · 8 · 12, peaking
near k=8 — while the gap falls monotonically throughout. **The gap tracks k, not the number of
options**, which is what a size explanation predicts and a freedom explanation does not.

## ⭐ E3 · THE EFFECTIVE k, MEASURED RATHER THAN ASSUMED

| nominal k | greedy | indep | topw | prompts attaining it |
|---:|---:|---:|---:|---|
| 2 | 2.00 | 2.00 | 2.00 | **968 / 968** |
| 4 | 4.00 | 4.00 | 4.00 | **968 / 968** |
| 8 | 7.92 | 7.92 | 7.92 | 919 / 968 |
| 12 | **11.32** | **11.32** | **11.32** | **734 / 968** |

At k=12 the emitted arms carry 11.32 criteria on average, because some prompts cannot supply 12.
**Both populations are reported** — "attaining nominal k" and the common intersection of 734 — and
the gaps agree to within 0.008 at every k.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `greedy_k4_fit1` **0.598415** and `indep_k4_fit1` **0.586595** on parity-0, against R805's committed values | PASS, else exit 2 |
| PLACEBO | the blind pool at k against **itself**: `0.0e+00` at all four k | PASS — exactly 0 |
| POSITIVE | D1, `topw_k` → `full` as k grows: 0.5574 · 0.5689 · 0.5735 · 0.5528 against `full` 0.5134; \|k12 − full\| **0.0395** < \|k2 − full\| **0.0441** | PASS ⚠ **weakly** — see below |
| g=0 | at k=2 the fitted and honest arms must **not** coincide, and do not: **+0.0472 [+0.0374, +0.0580]** | PASS — the control can fail |
| NEGATIVE | each prompt's fitted core scored against **another prompt's** parity-0 humans, 200 permutations: null **−0.1211 [−0.1325, −0.1107]**, max −0.1070; real **+0.0116** | PASS **after repair** — outside the entire null |
| NOISE FLOOR | 20 half-population resamples at k=12: sd **0.0017** | the surviving gap is 6.8× it |

⚠ **The positive control passed on a weak criterion and I am not upgrading it.** The `topw_k` curve
is **non-monotone** (0.5574 · 0.5689 · 0.5735 · 0.5528) and k=12 is closer to `full` than k=2 by only
0.0046. D1 asked whether the sweep converges toward `full`; it does, barely. A cleaner check would
need `topw_k` at k = n per prompt, which the release's arm set does not carry.

## ⛔ AND MY NEGATIVE CONTROL FAILED FIRST — THE SAME DEGENERATE SIGNATURE AS R809's

The first version permuted **which prompt's selected criteria** were applied, and returned a point
mass **+0.0156 [+0.0156, +0.0156]**. The cause is structural and worth recording: `select_core.py`
**re-indexes** the chosen criteria as `0..k−1` when it emits the npz (`meta.append(f"{pid}|{j}|{x}")`,
`j` the position in `sel`). **So "another prompt's selected indices" is always the same list**, and
the permutation permuted nothing. The selections are **not recoverable from the emitted npz at all**.
Repaired to destroy the structure the gap actually rests on — the prompt↔core pairing — which gives
a null far below the observation.

⚠ **That is two rounds running where a null returned a zero-width interval.** A degenerate null does
not look like a failure; it looks like an extremely precise measurement.

## WHAT DIED

- **R809's NEXT as named** — `oracle_k` cannot be swept; it samples above 20,000 combinations.
- **"the fitted route's advantage is fitting"** as an unqualified claim — **75% of it is size**.
- **"the fitted route's advantage is size"** as an unqualified claim — the residue is resolved at
  every k and survives BH 4 of 4.
- **my own negative control**, for the second round in a row.

## WHAT SURVIVES — AND THIS ROUND ADDS

A size-matched number where the arc previously had only a size-confounded one: **+0.0116 [+0.0070,
+0.0162]** at k=12, against **+0.0472** at k=2. Every prior statement about the fitted route —
R805's +0.0553, R807's 0.50–0.65, R809's 1.97× level ratio — was measured at k=4 against a
16-criterion pool, and now carries a size correction.

## SCOPE

968 prompts × 4 responses · annotators split by index parity; fitted arms fit on parity-1, every arm
scored on parity-0 · `greedy_k` and `indep_k` at k ∈ {2,4,8,12}, averaged · baselines `topw_k`,
`random_k_s0` and `POOL[0:k]` at matched k · paired bootstrap over prompts, NBOOT 1,200 · first
release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| the oracle rule swept across k | an enumeration budget above `C(39,8)`; `select_core.py` caps at 20,000 and samples — **checked**, 367 of 968 prompts affected at k=8 |
| k beyond 12 on a full population | more criteria per prompt; median is 16 and 734 of 968 reach 12 — **checked**, and the count is printed at every k |
| a gap free of D2's forced closure | a fitted arm at k ≪ n on every prompt; the release's median n is 16, so k=12 leaves 4 unselected on the median prompt — **checked**, and the freedom curve is reported because it is non-monotone |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The size correction is in: matched at k=12 the fitted advantage is **+0.0116 [+0.0070, +0.0162]**,
down 4× from **+0.0472** at k=2, and both ends of that range are computed by this round's `run.py`.
What is now unattacked is the other side of the comparison. `topw_k` is the honest arm this round
matched against, and it is a **rubric-weight** rule — it reads the rubric's own importance scores. The
size-matched prompt-blind baseline `POOL[0:k]` sits lower at every k (0.5556 · 0.5568 · 0.5497 ·
0.5482), so the gap against it is larger and barely moves with k: **+0.0490 → +0.0162**. The step is
to ask which of those two baselines the definition's clause ② should name, by testing whether
`topw_k`'s advantage over `POOL[0:k]` is itself resolved at matched k — if the rubric's weights buy
nothing over a blind pool, then "fitted beats honest" and "fitted beats blind" are the same claim and
clause ② has one baseline, not two.
