# R421 — all three label-reading rules are deterministic, the control R420 lacked fires, and `_08bR` is the anomaly

**The decision this makes safe:** *is any selection path in this campaign non-deterministic?* **No —
and today's run reproduces `_08b` exactly, which names which file of R415's pair diverged.**

## Result — `W_ALL_DETERMINISTIC`. Control fires. **CPU only.**

| control (placed **first**, because it can invalidate a prior round) | |
|---|---|
| `random_k` seed 0 | `5b706e69a51ea602` |
| `random_k` seed 1 | `72a311f62fe6a587` |
| **the comparison detects a seeded difference** | **True — PASS** |

| rule (two invocations, identical arguments) | run A | run B | identical |
|---|---|---|---|
| `oracle_k` | `22c61b3aefbe6550` | `22c61b3aefbe6550` | **True** |
| `greedy_k` | `1486efe712b855d4` | `1486efe712b855d4` | **True** |
| `indep_k` | `39e5bce5ec8ec1b4` | `39e5bce5ec8ec1b4` | **True** |

## ⛔ The gap in R420 that I should have caught inside it

**R420 reported "identical" and was never shown able to report anything else.** A hash comparison that
always returns equal — same path, ignored tag, stale file — would have produced *exactly* its output.

> **That is the ledger's oldest row — "a zero from an instrument never shown to return non-zero is
> silence, not an acquittal" — and I ran it five rounds after writing that sentence into three other
> rounds.**

The control costs **one run**: `random_k` at two seeds **must** differ. It does. **R420's verdict is
now licensed retroactively — it was correct and it was unsupported**, and those are different things.

## ⭐ And it identifies the anomaly by name

Today's deterministic `oracle_k` selection hashes **`22c61b3aefbe6550`**.

| | hash | matches today |
|---|---|---|
| `core_oracle_k4_08b.json` | `22c61b3aefbe6550` | **YES** |
| `core_oracle_k4_08bR.json` | `635698235fd1bb13` | no |

> **`_08b` is what this pipeline deterministically produces. `_08bR` is the outlier** — so it was made
> with different inputs, which is exactly what R419+R420+R421 jointly imply and what no round could
> pin to a file until now.

⚠ **One rule.** Only `oracle_k` had both files under a comparable name; the `_fit1` variants are named
differently and are not included. **n = 1 rule for this identification.**

## ⛔ Where the pipeline stands

| stage | determinism | established |
|---|---|---|
| scoring | **exactly zero floor** | R419, measured bitwise |
| selection, `topw_k` | byte-identical | R420 — **now licensed** |
| selection, `oracle_k`/`greedy_k`/`indep_k` | byte-identical | **this round** |

**No remaining mechanism inside the pipeline can produce R415's divergence.** The inputs differed —
and those files record none.

## Controls

| | returned |
|---|---|
| **SEED (+)** ⭐ | the control R420 lacked, placed **first** because a failure would have retroactively unverified R420 rather than only this round |
| **PRODUCED** | every run must emit a file — **a missing file is not agreement**, and an empty population passing would read as determinism |
| **DISTINCT** | every run writes its own tag, so no comparison is secretly a file against itself — *the exact way this test could go blind* |
| **SEEDS** | the control varies the seed **deliberately**; the three rules hold it **fixed**. Opposite manipulations, labelled as such |

## The sentence I can no longer write

> *"two runs agreed, so the process is deterministic"* — **not until the comparison has been shown
> able to disagree.**

Artifact: `results/r421_selection_rules.json`, source-stamped.
