# R332 — the closure level and reading A agree; their admitted sets do not, and neither is stable

**Decision this makes safe:** whether the closure rule can *derive* clause ②'s reading. **The LEVEL
can; the SET cannot** — a reference shift of **0.25 MDE** changes the admitted set. **W-SET-DIFFERS.**

## The headline is a stability measurement, not a level

| | value |
|---|---:|
| closure level at k=4 | **0.551951** |
| reading A (R286/R287 held-out best of 1,820) | **0.554602** |
| \|difference\| | 2.65e-03 = **0.25 of `coval_core`'s own MDE** |
| admitted at closure | `coval_core` · `topw_k3` · `topw_k4` · `topw_k6` |
| admitted under reading A (R326) | `coval_core` |

Sweeping the k=4 reference across the band **between** them — 46 blind references, width 0.25 MDE:

| reference A2 | admitted |
|---:|---|
| 0.551951 | `coval_core` · `topw_k3` · `topw_k4` · `topw_k6` |
| 0.552271 | *same* |
| 0.552676 | *same* |
| 0.553460 | *same* |
| **0.554524** | `coval_core` · `topw_k3` · **`topw_k6`** |

> **2 distinct admitted sets inside a quarter of one MDE.** The admitted set is **not a stable
> quantity at this site**, and any statement of the form *"N arms are admitted"* inherits that.

*(The sweep moves only the k=4 reference; `topw_k3` and `topw_k6` are held at their own closure
levels and must not be read as reading-A verdicts.)*

## Closure level per k — and R294's published reference is not closed

| k | \|class\| | closure A2 | pctile | rate one step below | R294 ref | class max | minimal? |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 16 | 0.5320 | 75.0 | 0.0625 | 0.5425 | 0.5425 | ✓ |
| 2 | 120 | 0.5528 | 95.8 | 0.0083 | 0.5464 | 0.5577 | ✓ |
| 3 | 560 | 0.5519 | 94.8 | 0.0036 | 0.5452 | 0.5591 | ✓ |
| 4 | 1820 | 0.5520 | 96.4 | 0.0005 | 0.5504 | 0.5575 | ✓ |
| 6 | 8008 | 0.5519 | 98.5 | 0.0002 | 0.5433 | 0.5559 | ✓ |
| 8 | 12870 | 0.5505 | 98.5 | 0.0001 | 0.5441 | 0.5545 | ✓ |
| 12 | 1820 | 0.5462 | 93.5 | 0.0022 | 0.5420 | 0.5495 | ✓ |
| 13 | 560 | 0.5451 | 87.9 | 0.0054 | 0.5397 | 0.5482 | ✓ |
| 15 | 16 | 0.5423 | 50.0 | 0.1250 | 0.5437 | 0.5443 | ✓ |

**At all 7 resolvable k, R294's published reference sits BELOW closure — it is not closed.** And
**closure sits below the class max at every k**, so *"better than the BEST prompt-blind set"* is
sufficient and **not minimal**.

## ⛔ R331's number was inflated by its own grid — a coarse grid reads high

R331 put the k=4 closure at **0.554667** on a **nine-point** percentile grid, and that near-identity
with reading A (6.5e-5) is what motivated this round. On a **45-point** grid it is **0.551951**. The
agreement is real but far weaker than advertised: **indistinguishable at this design's resolution**,
not identical. **A grid is an instrument, and a coarse one reports the level too high.**

## ⚠ The transfer control was UNFIT — transfer is UNVERIFIED, in neither direction

The held-out test selected the level on half the prompts and measured it on the other half; raw
rates were non-zero, which looks like a transfer failure. **It isn't readable as one.** A half sample
has a √2-larger MDE, so its class closes at a *lower* level — and the diagnostic is unanimous:

**7 of 7 resolvable k close lower on the fit half, mean Δ = −0.0031.** (k=1 and k=15 are excluded:
their 45-point grid yields only **8 distinct** references each, too coarse to resolve a 0.002 shift —
a cut on the instrument's granularity, declared as ≥20 distinct references, not on the outcome.)

**So the control compared two different levels.** Whether closure generalises is **UNVERIFIED** —
and an unfit control is not a pass. The first version printed *"PASS — the level generalises"*, which
is the false-acquittal direction and is permanent, because nobody re-examines a cleared claim.

## Controls

| control | result |
|---|---|
| **positive · minimality** — one grid step below closure the rate must be **> 0** | **PASS at all 9 k** (0.0001 … 0.125) |
| **positive @ g=0** — the weakest reference must admit most of the class | 0.75 … 0.997 |
| **negative** — 22 random/sham arms at the closure reference | **0 admitted** |
| **placebo** — each closure reference against itself | 0.0 |
| **sham · transfer** | **UNVERIFIED** — control unfit, see above |
| multiplicity | per k, \|class\| × 45 grid points; 37 arms computed, 4 admitted |

## What moved

- **`topw_k8` drops** at closure (0.82×) — R294 admits it, closure does not.
- **R294's reference is not closed** at any resolvable k.
- **The k=4 closure/reading-A gap is 0.25 MDE and flips `topw_k4`.**

## Scope

968 prompts (398 for `promptecho`) with ≥2 annotators · Qwen3.5-2B-Base under R234's canonical
builder · every C(16,k) subset enumerated for k ∈ {1,2,3,4,6,8,12,13,15} — the blind class is the
population, not a sample · 45-point percentile grid · 3 splits for the transfer attempt.

## What this cannot do

Establish that closure generalises out of sample — the control for that was unfit and a fit one needs
a design where the level and the evaluation share a resolution. Nor can it say reading A is *right*
in any sense beyond self-consistency: closure says the other readings admit what they quantify over;
it does not say the clause measures anything worth measuring.
