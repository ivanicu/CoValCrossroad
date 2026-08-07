# R418 — none of the 12 differing tokens has the shape of a claim

**The decision this makes safe:** *does R396's `DIFFER` mean a scoring round's findings are unstable?*
**No. It means the gate's extractor is too wide — and that calls for the opposite fix.**

## Result — `W_CLAIMS_STABLE`. **0 of 12.** Three controls pass. **No GPU.**

R130 prints its claims through one line — `mean_sat {v.mean():.4f}  core {1-e_core:.4f}
full_eq {1-e_fe:.4f}` — so a **claim-value has the shape `0.dddd`**.

| differing token | claim-shaped |
|---|---|
| `02` `04` `05` `06` `10` `117` | False |
| `1.22` `1.41` `104.63` `112.92` `117.28` `117.56` | False |
| **claim-shaped among the differing** | **0 of 12** |

## ⛔ I guessed the cause twice and was wrong twice — in a report

1. *"`1.22`, `104.63`, `117.28` look like timings"* — **R130 prints no timings.** `grep` for
   `time.time` / `elapsed` / `perf_counter` returns nothing.
2. *"they look like tqdm progress rates"* — **no `tqdm`** in R130, in `covalx/judge.py`, or in
   `corebench/*.py`.

**Two hypotheses, two refutations, zero measurements.** So this round asks the question that **does
not need the cause at all**, and answers it from committed data.

## ⛔ What flips

| | |
|---|---|
| **R396's operational conclusion** | **SURVIVES** — R388's gate uses the same extractor over `stdout+stderr` and **would convict an honest backfill** |
| **R396's stated cause** | **DOES NOT** — the claims were identical; what differed is what the extractor swept up |
| **the fix** | **narrow the extractor to claim-shaped tokens** — *not* exclude scoring rounds from re-run verification, which is what R396's verdict proposed. **The two diagnoses call for opposite repairs** |

## Controls

| | returned |
|---|---|
| **EMISSION (+)** ⭐ | R130's source must actually emit `:.4f` values — **`True`**. Without it, *"no claim-shaped token differed"* is **vacuous**: a shape the round never prints cannot informatively be absent. *That is the check-that-cannot-fail the ledger names* |
| **SHAPE (+/−)** | `0.5234` classified claim-shaped, `117.28` not — both directions, because a classifier saying no to everything would pass trivially |
| **EXTRACTOR** | tested against **R396's own committed token list**, not a re-derivation, so the population is exactly the one that produced the verdict |
| **HONESTY** | the two failed hypotheses are **recorded in the round**, not quietly dropped — a report that guessed twice then presented a third story as the first would be the narrative failure this campaign is built against |

## Register

| criterion | status |
|---|---|
| **the ORIGIN of the non-claim tokens** | **UNKNOWN, and I am not guessing a third time.** R396 did not persist the captured outputs — **my omission in its design** — and no reasoning recovers them. It needs a re-run that saves stdout and stderr |
| **a general claim about scoring rounds** | **N/A** — one round, one pair of runs |

## The sentence I can no longer write

> *"the round's numbers differ, so its findings are unstable"* — **its findings are the `0.dddd`
> values, and not one of them moved.**

Artifact: `results/r418_shape_of_the_difference.json`, source-stamped.
