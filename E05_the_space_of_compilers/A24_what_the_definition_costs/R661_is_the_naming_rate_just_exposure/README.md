# R661 · A null with power — and the rival I proposed had its arrow backwards

**Decision this makes safe:** whether R660's 18.3% is an artifact of when a round was written.
**No age gradient is detectable, at a unit where a planted 5× gradient IS.** Recency does not explain
it — and the recency rival was inverted when I wrote it.

## The result, with its scope

| | |
|---|---|
| **planted 5× residual gradient** (positive control, bin unit) | **0.929** vs null **[0.238, 0.857]** — **detected** |
| **pure-exposure sham** | **0.429** — **removed by the correction, as it must be** |
| **observed** | **0.762 — INSIDE the null** |
| **verdict** | **a NULL WITH POWER: no age gradient detectable** |

Population: 290 rounds declaring an `IMPOSSIBLE` register, 86 mentions · instrument: Spearman over
`mentions / exposure`, exposure = wall-entries written after the round existed · null: 5-seed
permutation of round-ids · regime: tree `758f667d`.

⚠ **MDE, stated:** with **8 bins** the null is wide and the planted gradient clears it by only
**0.071** — **this design sees a gradient of roughly 5× across the range and nothing weaker.**

## ⛔⛔⛔ The per-round statistic had NO power, and its own positive control proved it

`|rho| = 0.048` on a **planted 5× gradient** — inside its own null. **86 mentions over 290 rounds
leaves most rounds at zero**, so the rank vector is ~70% ties and Spearman is near-degenerate.
**The unit was wrong, not the gradient.** The observed per-round `0.167` — which had looked "above
the spread" — is **WITHDRAWN**.

> **A number computed at a unit with no demonstrated power is not a weak result. It is not a result.**

## ⛔⛔ And two of my controls were SWAPPED

v1 made the pure-exposure world its **positive** control and it failed — **correctly**. The statistic
*divides by exposure*, so a world where mentions ∝ exposure is **flat by construction** and must land
in the null. Demanding a large `|rho|` there is a **check that cannot pass** — §4's row, the mirror
of the one R660 committed one round earlier.

| | correct role |
|---|---|
| pure exposure | **SHAM** — must go null after correction ✓ (0.429) |
| gradient exposure cannot explain | **POSITIVE** — must survive the division ✓ (0.929) |

## ⛔ Check #262 — a self-contradicting sentence and an inverted rival

| claim | truth |
|---|---|
| *"18.3% is the first number **with a floor under it** — but **it has no floor** yet either"* | **Both cannot hold.** The commit body says *"with any content"* and is coherent; **the README carries the broken version, and the README is what a successor opens.** |
| *"entries name RECENT rounds"* | **Arrow backwards.** An entry can only name a round that **already existed**, so an **old** round has had **more** chances. |
| *"the arc's own rounds are named constantly while the 200s are not"* | **False.** Mentions peak at **R450–499 (27)**; the most recent full block **R550–599 has 3** — second lowest. **A middle peak is what neither rival predicts, and I stated it as fact in a NEXT line.** |

## The binned profile, whole

| bin | n | mentions | exposure | rate |
|---|---:|---:|---:|---:|
| R250–299 · R300–349 · R350–399 | 16 · 39 · 45 | 5 · 6 · 1 | 544 · 1324 · 1485 | .0092 · .0045 · .0007 |
| R400–449 · R450–499 · R500–549 | 47 · 35 · 44 | 11 · 18 · 20 | 1551 · 1039 · 685 | .0071 · .0173 · .0292 |
| R550–599 · R600–649 · R650–699 | 9 · 44 · 11 | 1 · 12 · 0 | 66 · 211 · 0 | .0152 · .0569 · — |

**Profile monotone in round age? No.**

## Pre-registration

> **point `|rho|` 0.20 · interval [0.00, 0.60]** · **directional:** *the profile is NOT monotone* ·
> **kill:** `|rho| > 0.60` AND monotone.

**Magnitude 0.167 — INSIDE, error −0.033** (the first magnitude to land inside in seven).
**Directional HOLDS.** ⚠ Both are reported on the **withdrawn** per-round statistic, so neither
should be counted toward the record without that caveat — **the estimate was right about a number
that turned out not to exist.**

**IMPOSSIBLE, named:** why a particular round was named is an **authored act**; no statistic recovers
intent. This settles the **sufficiency** of recency/exposure only. And **exposure is a proxy** — an
entry's write-time is taken as the highest round it names, which **biases toward more exposure for
old rounds, the direction that would manufacture the rival.**

## The sentence I can no longer write

> *"the obvious rival is that entries name recent rounds."*

**Exposure runs the other way, and the data peaks in the middle.** I proposed a rival without
checking either its direction or its shape.

## NEXT

**The MDE is the binding constraint and it is set by having 8 bins, not by the data.** 86 mentions
would support a finer grid if the null were built from a model rather than 5 shuffles of 8 points —
**and the null's own width `[0.238, 0.857]` is itself estimated from 5 draws, which is the
`min/max of N draws quoted as an interval` failure this standard names.** **Re-run the null at ≥200
permutations and report the empirical percentile rather than the min–max spread**, because the
current pass/fail of every arm here — including the positive control clearing by 0.071 — rests on two
extreme order statistics.
