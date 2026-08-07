# R448 · the inversion is **not** a swap — one arm rises, and the reason is measurable

**The decision this round makes safe:** whether R447's "the judge REORDERS the candidates" earns a
mechanism. **It does, but not the symmetric one the sentence implies** — `W-ARM`.

## ⛔ Rung 1 killed the announced statistic — three lines, zero compute

R447 closed with *"measure the per-criterion satisfaction VARIANCE each judge assigns… if 0.8B
compresses one arm's spread more, the reordering is a property of the judge's dynamic range."*

`score.py:41` is `sign(y_i − y_j)` and the arm score is a **mean** over criteria. So under
`s → a·s + b` with `a > 0`, **every sign is unchanged and A2 is exactly invariant.** A global
variance ratio *is* that affine part. **It has zero explanatory power by arithmetic.**
*Sixteenth announced step checked, ninth killed.*

## ⭐ And checking it surfaced the world the round should have been about

From committed artifacts — a **DERIVATION**, labelled:

| | q@2B | q@0.8B |
|---|---|---|
| `coval_core` | **1.0000** | 0.6984 |
| `gen` | 0.2610 | 0.7929 |

The quantile inverts too, so the bar did not move. **But an arm at quantile 1.000 has nowhere to go
but down.** Under *any* imperfect cross-judge correspondence, those two shifts are what regression to
the mean produces with **no differential mechanism at all** — and R447 was not entitled to one until
that world was dead.

## Result — the null is the 1,820 references themselves

Each reference underwent the same judge change. For references starting near an arm's quantile, their
own shifts are the reference distribution. No model.

| arm | SHIFT | band median | p | BH cells |
|---|---|---|---|---|
| **`gen`** | **+0.5319** | +0.015 … +0.054 | **0.0000 – 0.0055** | **10 of 10** |
| `coval_core` | −0.3016 | −0.020 … −0.039 | 0.0110 – 0.0747 | 4 of 10 |

⚠ **`coval_core`'s null is CENSORED.** It starts at exactly **1.0000**, the top of the scale, so every
reference in its band can only move down. Its p is an **upper bound** on how unusual it is, and it
survives only at the two narrowest bands. `gen` starts interior at 0.2610 and its test is clean.

> **So the inversion is not two arms swapping. It is `gen` rising further than any reference that
> started where it did, while `coval_core`'s fall is within what its boundary position explains.**

## The mechanism, measured on the same run

Per-criterion cross-judge **sign agreement** — invariant to the affine gauge, which is the point:

| | X | vs POOL16 | |
|---|---|---|---|
| `gen` | 0.6302 | **+0.0403** (MDE 0.0143) | **RESOLVED** |
| `coval_core` | 0.6044 | +0.0144 (MDE 0.0147) | *unresolved* |
| POOL16 (the reference class) | 0.5899 | — | |
| `gen_sham` | 0.5901 | — | |

**`gen`'s criteria transport across judges resolvably better than the reference pool's;
`coval_core`'s transport indistinguishably from it.** That is exactly why `gen`'s *absolute* A2 falls
(0.5374 → 0.4743) while its *rank* rises: the reference class falls further.

⭐ **Unplanned corroboration:** `gen_sham` (0.5901) and POOL16 (0.5899) agree to 4 decimals. Both are
criteria with no prompt-specific content, and they transport alike. Nothing in the design forced that.

## Controls — all PASS

| control | returned |
|---|---|
| POSITIVE — a strictly monotone judge | mean\|shift\| = **0.00e+00** ✅ |
| …and it must FAIL at g=0 | real data → **0.1361 > 0** ✅ |
| NEGATIVE — correspondence destroyed | **0.3331**, vs analytic `E\|U−V\| = 1/3 = 0.3333` ✅ |
| band: floor < observed < ceiling | 0 < [0.1311, 0.1414] < 0.3331 ✅ |
| g=0 — an arm against itself | shift **0.0e+00** ✅ |
| the null must itself regress | top decile **−0.0737**, bottom **+0.0643** ✅ |
| tie rate | 2B 0.0450 → 0.8B 0.0800; **dropping ties changes no cell** → `W-TIE` dead |

## ⛔ The control I had to repair mid-round — the fifth of its kind

The first NEGATIVE demanded `ceiling > 3 × observed`. For two independent rank vectors
`E|U−V| = 1/3` **exactly**, so the ceiling is capped at 0.3333 and that threshold silently required
the real shift to be under **1/9** — a bar derived from nothing. It printed `⛔ FAIL` and the round
correctly returned `UNVERIFIED`. Replaced by §4's own admissible form, `floor < observed < ceiling`
with bootstrap separation from **both** ends. **The repair is a derivation, not a relaxation** — the
new threshold is the analytic ceiling, computed without reference to the observed value.

## Reproducibility note, stated rather than hidden

`gen`'s q@2B reads **0.2610** here and **0.2615** in R446 — exactly **1 reference of 1,820**. A2 is
identical to 16 digits; the difference is float summation order (matmul here, row-loop there) landing
on an exact tie. Nothing downstream moves.

## Impossible here, named

- **a same-judge noise ceiling** — `sat_coval_core_2bA/2bB.npz` are **byte-identical**
  (`2076304c…`), a determinism artifact, not two draws. Using them would be §4's *determinism read as
  currency*. Would require a genuine re-run at nonzero temperature.
- **a third judge** — no third satisfaction set exists.
- **which judge is right** — two judges can refute a rule and never establish one.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
