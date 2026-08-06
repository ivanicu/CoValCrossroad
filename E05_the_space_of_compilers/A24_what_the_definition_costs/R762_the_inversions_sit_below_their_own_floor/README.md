# R762 · R761's inversions were never resolved, and its counterexample has no interval

**At **0.5× the design's own paired MDE** the inversion count R761 published falls from **4 to 0**,
with **319 of 346** pairs still standing, while a **random** subset of the same size retains **3.70**
and reaches zero in **0.000** of 200 draws. ⭐ And the arm carrying three of those four inversions is
**scored by a different judge**. R761's **prose** reading survives and sharpens; its **registered
branch and its fired verdict do not**, and its World C counterexample is **UNRESOLVED** — which is
not an acquittal for the claim R761 attacked.**

## check #364 — a three-line gauge test answered the round I had proposed spending a day on

R761's NEXT: *"what separates `oracle_k4_08bR` from `oracle_k4` — same rule, same target access,
0.0634 less A2."* **They are not the same object.**

- `select_core.py:75` — `--tag-suffix` is **MANDATORY when `--full-npz` is not the default**.
- `corebench/rebuild_selection_08b.sh`, its own header: **`_08bR` RERUN — the rule itself re-run
  under 0.8B**, i.e. the foreign source table R426 named (`sat08_full.npz`, Qwen3.5-0.8B-Base).
- R416 measured the consequence on this arm: **91.1% of prompts changed selection**.

### the anchor test, both controls present

| arm | matches `sat08_full` (0.8B) | matches `sat_full` (default) |
|---|---|---|
| **`oracle_k4_08bR`** | **0.4609** | 0.0345 |
| `oracle_k4` | 0.0342 *(floor)* | **0.5342** *(positive)* |

**The two arms are measured by two different judges** *(ledger 1061)*. R761 ranked 27 arms on one
axis with one of them on a different instrument — **and it was the arm the round was about.**

## ⛔ two results were forced, and are labelled

**D1 — a floor can only REMOVE inversions.** Filtering is a subset operation, so the count is
monotone non-increasing. *"Fewer inversions after filtering"* is algebra. **The measurement is whether
it reaches ZERO**, and the sham — a random subset of the same size — is what attributes it.
**D2 — R761's four pairs are two events.** `topw_k3`, `topw_k4`, `topw_k6` lie within 0.0010, so one
arm inverting against all three is **one event with three labels**. Computed: **4 pairs → 2 events**.

## ⭐ the floor curve — only the zero is a finding, and the SHAM is what earns it

| floor | surviving pairs | inversions | SHAM, random equal-size subset |
|---|---|---|---|
| **0** *(R761's count)* | 346 | **4** | — *(identity row)* |
| **0.5× paired MDE** | **319** | **0** | mean **3.70**, P(=0) = **0.000** |
| 1× paired MDE | 304 | **0** | mean 3.54, P(=0) = 0.000 |
| 2× paired MDE | 280 | **0** | mean 3.35, P(=0) = 0.000 |
| R415's 0.116489 *(a different object)* | 81 | 0 | mean 0.90, P(=0) = 0.375 |

**Removing 27 *specific* pairs kills every inversion; removing 27 random pairs essentially never
does.** The confound written before the run — *a filter that keeps nothing cannot invert* — is
answered by the surviving-pair column: **319 of 346 remain.**

**E1 · the resolution itself.** Paired MDE of a between-arm ΔA2: median **0.0136**, IQR
**[0.0097, 0.0149]**, max 0.0237. R761's four inversions all sit at **|ΔA2| ≤ 0.0017** *(ledger 1062)*.

## ⛔ the controls failed first, and the failure was a population defect two rounds old

POSITIVE-1 and g=0 both returned **False** on the first run because `mde_min` was **exactly 0.0000**:
**five pairs have identical per-prompt vectors** — R730's replica arms, one object wearing two tags.
For those `floor == ceiling`, **no threshold is admissible** (§4), and `|ΔA2| = 0 ≥ 0` would have read
as **RESOLVED at every floor**. R761 carried them inside its 351 unnoticed, because *an inversion
count never divides by anything*. Excluded and counted: **346 resolvable pairs** *(ledger 1063)*.

## ⭐⭐ E3 — rob had no interval, and with one, nothing separates

Nested bootstrap, **120 outer prompt-resamples × 300 inner** (POSITIVE-2: inner 1200 → 300 moves rob
by **0.0000** on all 27 arms).

| arm | rob | 2.5% | 97.5% | share of draws at exactly 1.0 |
|---|---|---|---|---|
| `oracle_k4` | 1.0000 | 1.0000 | 1.0000 | **1.000** |
| `coval_core` | 0.9978 | 0.8943 | 1.0000 | 0.250 |
| `topw_k6` | 0.9863 | 0.8463 | 1.0000 | 0.092 |
| `topw_k4` | 0.9835 | 0.8411 | 1.0000 | 0.067 |
| `topw_k3` | 0.9703 | 0.7997 | 1.0000 | 0.067 |
| **`oracle_k4_08bR`** | **0.9401** | **0.6077** | **1.0000** | **0.092** |

Paired **`08bR` − `coval_core` = −0.0932 [−0.3584, +0.0212]** — **not separated.**
**Only `oracle_k4` is resolvably at the ceiling.** Every other arm reaches rob = 1.0 in 6.7–25% of
prompt-resamples, so **R761's `{rob = 1.0}` partition is a point estimate with no resolution behind
it.** *(The 2.5% of 120 draws is the 3rd order statistic and is coarse — which is why the at-ceiling
share, not a tail percentile, is what the verdict rests on.)*

## controls — 8 reported, all PASS after the repair

| control | returned |
|---|---|
| **PROVENANCE** | R761's committed rob reproduced **EXACTLY on 27/27** arms; exits 2 otherwise — this round must *be* R761 before it may contradict it |
| **POSITIVE-1** | planted ΔA2 at 2× MDE reads RESOLVED **346/346**; at 0.5× reads UNRESOLVED. Band: a rule resolving nothing fails the first, one resolving everything fails the second |
| **POSITIVE-2** | inner draws 1200 → 300: worst \|Δrob\| = **0.0000** (threshold 0.005) |
| **g=0** | a planted ΔA2 of exactly 0 is never called resolved |
| **NEGATIVE** | pairing destroyed → MDE **inflates ×1.80 [0.96, 3.70]**, so the paired floor is the *conservative* one and not an artifact of correlated arms |
| **SHAM** | as above — the ingredient removed is **resolution filtering**, replaced by a size-matched random subset |
| **PLACEBO** | **215** pairs with \|ΔA2\| > 0.05: **0** inversions at every floor |
| **NOISE** | two floors reported as **different objects**: the paired ΔA2 MDE (0.0136 median) and R415's committed re-selection shift (0.116489) |

## what this changes in the deliverable

| carried *(R761)* | stands as |
|---|---|
| ⚠ **R761 said THREE different things off one number** | its **prose**: *"rob carries essentially no information that mean A2 does not"* · its **registered branch** at inv ≥ 3: *"rob carries information A2 does not"* (B′) · its **fired verdict**: **C**. The prose was right, the registration was answered on noise, and nothing in the round noticed they disagreed *(ledger 1065)* |
| the count itself — 4 of 351 inversions | ⛔ **RETRACTED as a measurement.** 0 resolved inversions at 0.5× the design's own MDE, 319 of 346 pairs surviving |
| *"the separating case is `oracle_k4_08bR`"* | ⛔ **RETRACTED twice over** — cross-instrument, and rob 0.9401 vs 1.0000 is **UNRESOLVED** |
| *"the causation is backwards — A2 buys robustness, not target-reading"* | **downgraded to UNVERIFIED.** ⚠ **This is NOT an acquittal for R527's sentence** — it returns to *unattacked*, not to *true* |
| *"robustness is 98.9% a rank statistic of A2"* | ⭐ **CONFIRMED and strengthened to 100% of the resolved range** — the residual is zero wherever ΔA2 clears its floor. This round's largest effect is a confirmation, not a retraction |
| *"③rule Jaccard 0.909 vs ③name 0.400 vs sham 0.254"* | the **ordering** survives across the whole t-curve; the point Jaccards at t = 1.00 rest on an **unresolved partition** and the resolved end of the curve (t = 0.75: 0.647 / 0.235 / 0.500) is what carries it |

## the sentence I can no longer write

*"rob inverts against A2 in 4 of 351 pairs"* — as a **measurement**. Every one of the four sits below
the floor, three of them on an arm measured by a different judge, and the four pairs are two events.
⚠ And I can no longer write a round whose prose settles a question its own pre-registered branch
answered the other way **without saying so in the round**: R761 did exactly that, and was right by
accident.

## NEXT

Two rounds in a row have now spent their budget on the reference-class axis and neither produced a
statement about the definition — R761 produced a retracted residual, R762 retracted it. The axis is
exhausted **because rob has no resolution below the ceiling**: only one arm of the six measured
separates from 1.0000, so **no ordering of the extension by baseline-robustness is admissible at this
n**, and getting one would need more prompts, not more references. What that leaves open is a
different quantity the same nested bootstrap can reach at this n: `③rule` and `③name` differ on
**11 vs 4** arms, and the whole *"which clause does the work"* question has been argued from point
Jaccards. The registered quantity is an interval on the Jaccard itself, over the same outer
resamples — because **if 0.909 and 0.400 overlap, then R760's repair to ③ is unproven too**, and that
is a claim currently sitting on the page.
