# R1032 — four repairs live only as annotations. Does the stale clause text **compute** the same?

**The decision this round makes safe:** whether annotation was enough. **It was not** — but only on
one target, and the shipped figures are unaffected.

## The question, sharpened past R1031's count

R1031 established *by count* that the canonical clause text is unchanged at **exactly 2 sites**
(`DEFINITION.md:808`, `README.md:65`). The question here is different: does a reader who implements
the text **as written** compute a **different extension** from one implementing it **as repaired**?
That is the line between a documentation defect and a wrong deliverable.

Only two of the four repairs could move it — R1026 and R1027 change no computation.

## Result — ⭐ **World B, and target-dependent, which neither world anticipated**

| target | seed | as written | as repaired | sym. diff | differing arms |
|---|---:|---:|---:|---:|---|
| `A2` | 1032 / 2064 / 3096 | 9 | 9 | **0** | — |
| `A1·consensus` | 1032 / 2064 / 3096 | 4 | 2 | **2** | `coval_core_2bA`, `coval_core_2bB` |

**Identical under `A2`; differ by 2 arms under `A1·consensus`.** Since R1019 established that **every
extension figure in this arc is A2's answer**, the **shipped numbers are right** — and the shipped
**sentence** is wrong in a way that bites only when a reader changes target.

⛔ **And the mechanism is already committed.** The differing arms are the **twins**, admitted by the
as-written reading because it **imputes 768 of their 968 values** (R1021), excluded by the repaired
one because it does not. **R1024's repair and R1011's withdrawal are the same correction reached
twice by different routes — and the canonical text still encodes the version that needed
withdrawing.**

## ⚠ The expected result was World A, and it was wrong

R1025's 94/94 and R1022's four partial-coverage arms made agreement likely. **An expected outcome is
not a derived one**: the two readings are separate programs over the same data, and one target
separated them. That is why it was run rather than argued.

## Controls

- **POSITIVE** — two anchors from **two different rounds**, one code path: as-written reproduces
  R1000's conjunction of **9**; full-coverage reproduces R1011's **7**. Both **PASS**; either could
  have failed on any loader or operator drift.
- **NEGATIVE** — a deliberately **wrong** reading (`beats genericpool16` alone, the *looser*
  comparator) must give a different extension: **12 vs 9**, Δ = `generic`, `generic_reprov`,
  `topw_k2`: **PASS**. Without it, a measured zero would mean nothing.
- **PLACEBO** — the as-written reading against **itself**: symmetric difference **0**: **PASS**.
- **SEEDS** — 3; every cell identical across all three, so neither the agreement nor the difference
  is a bootstrap artifact.

## ⚠ My own closing paragraph fired on the wrong branch

The first run printed *"`COSMETIC` IS NOT `HARMLESS`"* — written for **World A** — under a **World B**
verdict. **A verdict string is prose that looks like output; so is the paragraph after it.** Both are
now computed from the per-target result.

## What this cannot say

Whether the **repaired** wording is the **right** definition. That is construct validity and needs an
external criterion this release does not carry. **This round compares two readings of one clause,
never the clause against the world.**

`run.py` · `results/two_readings.json`
