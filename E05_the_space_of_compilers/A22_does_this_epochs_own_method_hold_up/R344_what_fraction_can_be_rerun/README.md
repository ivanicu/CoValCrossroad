# R344 — what fraction of the corpus can be re-run, and what reproduces

**The decision this makes safe:** whether re-running is a practical gate for the provenance hole
R343 found. **It is — for 91% of the corpus, at 90 seconds a round. And a quarter of what re-runs
does not reproduce.**

## Result — `W1_CLOSABLE`

**Sample:** 45 rounds, stratified by static import screen, seed 344. All four controls PASS.

### `p_cheap(T)` — one execution per round, so the whole curve is free

| T (s) | completed ≤ T | rate |
|---:|---:|---:|
| 5 | 23 | 0.51 |
| 10 | 31 | 0.69 |
| 30 | 36 | 0.80 |
| 60 | 40 | 0.89 |
| **90** | **41** | **0.91** |

### Reproduction, of those that completed

**40 had an artifact to compare. 30 regenerate it; 10 do not.**

| stratum | sampled | in corpus | completed | reproduces | differs |
|---|---:|---:|---:|---:|---:|
| pure | 40 | 303 | 38 | 27 | **10** |
| cpu-ml | 2 | 7 | 2 | 2 | 0 |
| gpu/ml | 3 | 20 | 1 | 1 | 0 |

**`byte-identical` and `json-equal` are both 30/40** — no round differs only in float formatting.
**Every one of the ten differs in a value.**

| the ten | secs |
|---|---:|
| `R242_self_audit` | 0.0 |
| `R328_the_three_readings_are_one_budget` | 2.1 |
| `R115_shrink_is_one_parameter` | 2.7 |
| `R102_margin_calibration` | 4.4 |
| `R107_joint_resample` | 4.6 |
| `R36_channel_shapley` | 8.1 |
| `R227_two_currencies` | 22.6 |
| `R34_global_rater_crossfit` | 29.4 |
| `R121_is_the_advantage_the_metric` | 41.5 |
| `R221_contamination` | 89.5 |

## The pairing with R345 — and it is mostly a coverage failure

| stamp (R345) | reproduces | DIFFERS |
|---|---:|---:|
| FRESH | 1 | 0 |
| **STALE** | 0 | **2** |
| UNVERIFIED | 2 | 1 |
| **NO STAMP** | 27 | **7** |

Where a stamp exists it **agreed** with re-running — both STALE rounds differ, the one FRESH round
reproduces. But **a stamp exists for only 3 of these 40 rounds**, and **7 of the 10 real failures are
in rounds carrying no stamp at all.**

⚠ `FRESH` is **n = 1**. Nothing here says a fresh stamp *predicts* reproduction; the cell is a count,
not a rate.

**So the drift check's sign is right and its coverage is the problem** — exactly the 24%-of-corpus
limit R345 named, made concrete: it would have caught **2 of 10**.

## Controls — and this round printed UNVERIFIED twice before they held

| | returned |
|---|---|
| TIMEOUT | `sleep(110)` → TIMEOUT; instant script → completed |
| NEGATIVE (the comparison) | corrupted artifact → byte `False`, json `False` |
| POSITIVE (`R342`) | completes **and** reproduces |
| **ISOLATION** | of **765** artifacts present at the start, **0 changed, 0 vanished** after executing 45 rounds |

**The isolation control failed on two earlier, valid runs**, both times because the author was
working while it measured:

- **v1** `sha256(git status --porcelain)` — five of my own commits moved the string
- **v2** one hash over **all** artifacts — I created two new rounds' results, so new **paths** moved it

Zero tracked artifacts were modified on either occasion. *"Nothing anywhere changed"* is strictly
stronger than *"no round overwrote an artifact"*, and approximating the second by the first cost two
complete censuses, both correctly UNVERIFIED. **v3 compares per path** over paths present at the
start; an added path is not evidence about isolation and is ignored.

Two further defects were caught by controls before any number was believed: rounds that rewrite
artifacts **in place** wrote *through* a hardlink copy into the real tree (`R242`, `R307`; restored
with `git checkout`, and the copy is now a true copy), and a round that **ERRORED** was scoring as a
perfect reproduction because nothing had been written to compare.

## Prior work I did not check before proposing this

- `R302_are_the_artifacts_reproducible` — re-ran 8 artifacts, **742 leaf values differed**, three
  inside a `verdict` string
- `R315_how_many_rounds_can_still_run` — **25 of 278** cannot resolve their inputs

`assurance/next_gradient_is_new.py` finds both in one command on the exact words I used, and **I
wrote that file because I had made this mistake four times.** What is new here: **cost as a
dose-response curve** (R315 measured whether a round can *start*), and a **stratified corpus sample**
rather than the eight artifacts that happened to be dirty in git — which is a stratum, not a sample.

## Register

| criterion | status |
|---|---|
| **network not blocked** | a round that fetches would count as cheap here and would not be on a cold machine. The static screen finds no network imports — **bounds it, does not prove it** |
| a round that DIFFERS is not thereby **wrong** | an unseeded draw, a timestamp or a dict order explains a difference with no defect. This measures **regenerability**, not correctness |
| self-referential rounds | `R343` and `R344` excluded — both copy the repo and execute its rounds; sampling them measures the harness, not the corpus. **Stated in the artifact, not quietly trimmed** |
| the 4 that did not complete | 3 `gpu/ml` + 1, all timeouts or import errors under `CUDA_VISIBLE_DEVICES=""` |

## The sentence I can no longer write

> *"re-running the corpus is too expensive to be a gate."*

**91% at 90 seconds.** What it will not do is tell you the numbers are right — **a quarter of what
re-runs comes back different.**

Artifact: `results/r344_rerun_cost_census.json`.
