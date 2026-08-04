# R331 — a clause-② reference is safe because of its PERCENTILE, and R330's mechanism was wrong

**Decision this makes safe:** how to choose a clause-② reference. **Put it high in the blind
distribution — the rule is a number, and it is p99, not p94.**

## W-PERCENTILE — the blind admission rate, over all 1,820 prompt-blind quadruples

Every one of the 1,820 k=4 subsets of the generic pool *never reads the conversation*, so **every one
is a member of clause ②'s own reference class.** A reference that admits any of them is refuted by
clause ②'s own words. The rate is the whole class, not a sample:

| reference | A2 | percentile | admitted | rate | BH |
|---|---:|---:|---:|---:|---:|
| p0 | 0.5144 | 0.0 | 1788 | **98.2%** | 1810 |
| p10 | 0.5273 | 10.0 | 1308 | 71.9% | 1417 |
| p25 | 0.5329 | 25.0 | 855 | 47.0% | 988 |
| p50 | 0.5391 | 50.0 | 424 | **23.3%** | 504 |
| p75 | 0.5446 | 74.9 | 101 | 5.6% | 146 |
| p90 | 0.5490 | 89.9 | 16 | 0.9% | 32 |
| **R294 first-4** | **0.5504** | **93.7** | **3** | **0.16%** | 13 |
| p95 | 0.5511 | 94.9 | 6 | 0.3% | 16 |
| **p99** | 0.5547 | 99.0 | **0** | **0.0%** | **0** |
| p100 | 0.5575 | 99.9 | 0 | 0.0% | 0 |

> **The design rule is a number: a clause-② reference must sit at or above p99 of its blind class.**
> R294's sits at p93.7 and is *nearly* safe — 3 of 1,820, not 0.

## ⛔ R330's closing mechanism is replaced, not qualified

> *"the reference is drawn from the same pool as the arm under test, so an arm that **is** the pool
> compares to itself and cannot win"* — R330, written last, acted on next, no control attached.

**Self-comparison protects against exactly one object.** It says nothing about the other 1,819. The
**sham decides it**: ten *different* subsets at the same percentile give rates
`[0.0055, 0.0033, 0.0049, 0.0049, 0.0033, 0.0022, 0.0049, 0.0022, 0.0049, 0.0038]` — spread 0.0033,
indistinguishable from R294's own 0.0016. **Identity does no work once altitude is fixed.**

**And it explains R330 better than R330 did.** Budget-matching didn't destroy a self-comparison — it
replaced a p94 reference with best-of-1, a random draw at ~p50, dropping the bar by ~0.013, **more
than one MDE**. `generic` walked in through a **23.3% door**.

## ⚠ The derivation was right in direction and wrong about the 3 — and the miss is the lesson

Pre-registered from R286's committed numbers: *best blind set − reference = 0.00704 against a typical
MDE of ~0.0106, i.e. 0.66 MDE, so nothing blind can clear.* **Three cleared.** Measured:

| subset | A2 | gap | MDE | ratio | shared criteria |
|---|---:|---:|---:|---:|---:|
| (0, 1, 9, 14) | 0.5566 | +0.0062 | 0.0059 | 1.04 | 2 |
| (0, 2, 3, 14) | 0.5561 | +0.0056 | 0.0055 | 1.02 | 3 |
| (0, 3, 9, 13) | 0.5572 | +0.0068 | 0.0066 | 1.02 | 2 |

Median per-pair MDE: **0.0070** for sets sharing *no* criteria with the reference, **0.0046** for
sets sharing ≥3. The three that clear share **2.33** criteria on average against **1.00** across all
1,820.

> **A paired MDE is a property of the PAIR, not of the design.** A near-neighbour has a small paired
> sd, so it clears its own resolution on a tiny gap. Quoting one "typical MDE" is blind to exactly
> the cell class that survives — and all three sit at ratios 1.02–1.04, right on the boundary.

## Controls

| control | result |
|---|---|
| **positive** — the reference against itself | gap `+0.0e+00`, does not clear |
| **positive @ g=0** — the *same* set against the weakest reference (p0) | `+0.0361`, **clears** — the instrument can detect admission |
| **negative** — `coval_core` must clear R294's reference, `gen_sham` must not | +0.0160/0.0106 ✓ · −0.0676 ✗ |
| **sham** — 10 different subsets at the same percentile | rates within 0.0033; **percentile, not identity** |
| **placebo** — every reference against itself | 0.0 across all candidates |
| multiplicity | 1,820 × 10 = **18,200 cells**; raw *and* BH counts printed |

⚠ **BH admits *more* than the MDE criterion at every row** (13 vs 3 at R294's). Not an inconsistency:
the MDE folds in power (`ZEFF = 1.96 + 0.84`), so it is a *resolution* threshold and BH is a
*significance* one. Both are published; neither is chosen after the fact.

## Scope

968 CoVal prompts with ≥2 annotators · Qwen3.5-2B-Base under R234's canonical builder · **all 1,820
k=4 subsets of the 16-criterion generic pool enumerated exhaustively** — the population is the whole
blind class, not a sample of it · k=4 exactly, all annotators.

## What this cannot do

Transfer the **number**. A different pool has a different spread, so `0.5504` and `p99` are facts
about this 16-criterion pool. **The rule transfers; the threshold must be re-measured per pool** —
and measuring it is now a two-line procedure rather than a judgement call.
