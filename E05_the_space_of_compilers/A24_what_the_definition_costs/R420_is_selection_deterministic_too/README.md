# R420 — selection is deterministic too, so there was never any instability to find

**The decision this makes safe:** *where does R415's 0.116489 come from?* **Not from noise. The
pipeline is deterministic given its inputs, so the inputs differed.**

## Result — `W_SELECTION_DETERMINISTIC`. Three controls pass. **CPU only.**

| | |
|---|---|
| unseeded stochastic constructs in `select_core.py` | **0** |
| the one RNG present | `L119: rng = np.random.default_rng(a.seed)` — **seeded**, i.e. determinism |
| `core_topw_k4_detA` | `f498ca9ac905293b` |
| `core_topw_k4_detB` | `f498ca9ac905293b` |
| **identical** | **True — 0.0% of prompts changed** |

**Source and behaviour agree — which neither establishes alone.**

## ⚠ CORRECTION — R421: this round had no positive control, and now does

**This comparison reported "identical" and was never shown able to report anything else.** A hash
check that always returns equal — same path, ignored tag, stale file — would have produced exactly the
output below. *That is the ledger's oldest row, and it was missing here.*

[`R421`](../R421_the_last_three_rules_and_the_control_R420_lacked) supplies it: `random_k` at seed 0
vs seed 1 **must** emit different criteria, and the comparison **detects it**. **The verdict below is
correct and is now licensed** — it was unsupported before, and those are different things.

## ⛔ The contradiction this resolves

| stage | determinism | how established |
|---|---|---|
| **scoring** | **exactly zero floor** | R419, **measured** (bitwise, 200 prompts) |
| **selection** | **byte-identical** | this round, **scanned and measured** |
| **⇒ pipeline** | **deterministic given its inputs** | both stages |

**But R416 measured `core_X_08b.json` vs `core_X_08bR.json` differing on 91–99.6% of prompts.** Two
deterministic stages cannot produce that from the same inputs.

> **So the `_08b` / `_08bR` files are two DIFFERENT CONFIGURATIONS, not two draws. R415's 0.116489
> is a between-configuration difference and is not a noise floor of anything.**

**There was never any instability to find** — and four rounds went into establishing that, from a
filename suffix I read as "re-run".

## ⭐ Why this round could do what R417 could not

**R417 had to stop at a source scan**, because scoring needs the GPU. **Selection is CPU-only**, so
this round ran **rung 1 *and* the real test**, and let them cross-check. *A seeded RNG proves nothing
about dict ordering or tie-breaking; the empirical pair covers what the scan cannot.*

## Controls

| | returned |
|---|---|
| **SCAN (+)** | a planted `np.random.shuffle(` is flagged — `PASS` |
| **SCAN (−)** ⭐ | a **seeded** `default_rng(a.seed)` is **not** flagged — `PASS`. *Seeding is determinism, not a violation of it, and a scan that flagged it would condemn every correct script* |
| **PRODUCED** | both runs must actually emit a file — **an empty population passing would read as agreement here**, which is the ledger's named failure |
| **SELF (=)** | a file against itself hashes equal |
| **DISTINCT** | the two runs write to different tags, so neither overwrites the other |

## ⚠ What this makes remaining, and what it does not demonstrate

**Different inputs is now the remaining explanation.** It is **not demonstrated** — those two files
**record no inputs**. That is precisely the gap the provenance field closes for everything produced
from here on, and cannot close retroactively.

## Register

| criterion | status |
|---|---|
| **rules not run** | **N/A** — `topw_k` supplies 4 of 5 published arms, but `oracle_k`/`greedy_k`/`indep_k` take a `--select-npz` and are **not** exercised. Their determinism **does not follow and is not claimed** |
| **cross-machine determinism** | **N/A** — one machine |
| **proving the `08b`/`08bR` inputs differed** | **N/A** — can only be made the remaining explanation, never shown |

## The sentence I can no longer write

> *"the pipeline is not reproducible"* — **both stages are deterministic given their inputs.** What I
> found was two experiments wearing one name.

Artifact: `results/r420_selection_determinism.json`, source-stamped.
