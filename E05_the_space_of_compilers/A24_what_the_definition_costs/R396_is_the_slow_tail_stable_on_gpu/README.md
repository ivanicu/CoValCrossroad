# R396 — the expensive round does not reproduce at unchanged source

**The decision this makes safe:** *is the source-hash cache key sound on the slow tail?* **No — and
R388's committed gate has a live false-conviction mode there.**

## Result — `W_TAIL_MOVES`. Three controls pass. *(1h50m on the pueue `gpu` group.)*

| | |
|---|---|
| subject | `R130_judge_gauge`, run **twice** at unchanged source |
| return codes | `[0, 0]` — **both succeeded**, so `DIFFER` is a real difference and not two identical crashes |
| numbers per run | **140** |
| result | **DIFFER** |
| differing tokens | `02 · 04 · 05 · 06 · 1.22 · 1.41 · 10 · 104.63 · 112.92 · 117 · 117.28 · 117.56` |

| control | |
|---|---|
| **CUDA (+)** | a bf16 matmul runs on the GPU — `PASS`. Without it a STABLE result could be the CPU path, i.e. silence |
| **PLANT (+)** | an unseeded rng draw → classified unstable — `PASS` |
| **PLANT (−)** | a constant → classified stable — `PASS` |
| **EXITCODE** ⭐ | a non-zero exit is its own class. **A crash repeats byte-identically**, so without this the comparison could have printed STABLE for a round that never ran |

## ⚠ CORRECTION — R418: the stated CAUSE does not survive

[`R418`](../R418_what_differed_was_not_the_claims) tested the 12 differing tokens against the shape
R130 prints its claims in (`0.dddd`, from `mean_sat {…:.4f} core {…:.4f} full_eq {…:.4f}`).
**Zero of 12 match.**

**The round's reported values did not move.** What moved is everything else the extractor swept up.
**The operational conclusion below stands — R388's gate would convict an honest backfill — but the
cause is a defect in the gate's EXTRACTOR, not instability in a scoring round's findings, and the two
call for opposite fixes.**

## What this means for the cache

The source-hash key would **certify a stale verification exactly where 80% of the gate's cost lives**
(R393). ⚠ But given R418, the right repair is **narrow the extractor to claim-shaped tokens**, not
*exclude scoring rounds from re-run verification* — which is what this round's own verdict proposed.

Artifact: `results/r396_tail_stability.json`, source-stamped.
