# R358 — the closure defect replicates at a second judge, and at 0.8B no arm clears a safe reference

**The decision this makes safe:** *is R355's non-upward-closure a fact about the 2B judge, or about
the estimator?* **The estimator.** It replicates at Qwen3.5-0.8B-Base, on the same 16 criteria.

## Result — `W_ESTIMATOR`. Four controls PASS. Two runs byte-identical.

R355 named a mechanism that is a property of the **paired-MDE admission rule**, not of any model —
so it made a falsifiable prediction nothing had tested. `sat08_genericpool16.npz` is the identical
pool at the second judge; R301 loads it but **only ever as `POOL[0:k]`**. The blind class had never
been enumerated there.

| grid | 2B violations | 0.8B violations | k violating at **both** |
|---:|---:|---:|---|
| 9 | 0 | 0 | — |
| **45** | **18** | **4** | **12, 13** |
| **91** | **50** | **13** | **12** |

**Violations > 0 at both judges, at overlapping k.** The 9-point grid finds none at either — the
same blindness R355 measured, reproduced independently.

## ⛔ My pre-registered directional prediction failed in sign, and the branch would have hidden it

`W-WORSE` said: the noisier judge should show **more** violations, since larger and more erratic
paired sds make near-neighbour accidents commoner. Observed **4 vs 18 — 4.5× fewer.** The kill's
three branches had no home for "materially fewer", so the else-branch quietly returned
`W-ESTIMATOR`.

**And my first repair was wrong too.** The obvious explanation — a noisier judge has a larger MDE
and so admits *less of everything*, meaning raw counts are not comparable — predicts the
**normalised** rates should match. They do not:

| grid | 2B rate | 0.8B rate | ratio |
|---:|---:|---:|---:|
| 45 | 0.250 | 0.133 | **0.53×** |
| 91 | 0.338 | 0.203 | **0.60×** |

*(rate = violations ÷ candidate references above `first0`, the population at risk)*

> **The residual is named, not closed.** 0.8B's violation rate is about **half** 2B's after
> normalising and this round does not know why. Offering the MDE-scale story as the resolution would
> repeat exactly the error it replaces — an untested mechanism produced to absorb a failed
> prediction. A designed test would **sweep judge precision**, not compare two points.

**What stands:** replication rests on *violations > 0 at both judges* and the *k-overlap*, never on
a count comparison. **The dose-response reading is withdrawn.**

## Part B — at 0.8B the definition admits nothing at any safe reference

R301 reports the admitted set at 0.8B is empty **at the published reference**. Asking what a
*stricter* reference admits is **forced** (a subset of ∅), so that question is not asked. The
non-forced question is the **downward** one.

| arm | A2 | pool range (k=4) | highest reference cleared | vs 0.8B closure 0.4845 |
|---|---:|---|---:|---|
| `generic` | 0.4767 | [0.4444, 0.4883] | 0.4699 | **below** |
| `gen` | 0.4736 | [0.4444, 0.4883] | 0.4574 | **below** |
| `coval_core` | 0.4695 | [0.4444, 0.4883] | 0.4574 | **below** |
| `topw_k4` | 0.4659 | [0.4444, 0.4883] | 0.4444 | **below** |
| 7 others | 0.3811–0.4348 | — | **nothing** | below the weakest pool reference — **FORCED**, labelled |

**No arm clears any reference at or above 0.8B's own closure level.** Four arms clear *something*,
so the question was genuinely open — this is a measurement, not an arithmetic consequence.

⚠ **Population declared, not borrowed.** Part B uses only the **12 arms judged directly** at 0.8B.
R301 reaches 41 by **rebuilding 34 from `sat08_full.npz`** via a subset path; that path passes
R301's own parity control, but it is an assumption this round declines to inherit.

## Controls

| | returned |
|---|---|
| **PLACEBO** — every reference against itself | **0** self-admissions |
| **POSITIVE** — weakest reference (rate 0.954) injected above `first0` | flagged |
| **g=0** — class-max injected in the *same slot* | not flagged — fires on rate, not position |
| **NEGATIVE / SYNTHETIC** — every reference flattened to a constant at its own mean | **0 violations at 0.8B**, matching 2B |
| reproducibility | two runs **byte-identical** (`e4cf64c0d9f9`) |

The synthetic control is now satisfied at **both** judges — a stronger demand than R355 made of
itself.

## ⛔ And my own closing sentence from R357, corrected by running the count it quantified over

R357 closed with *"nothing in the campaign has asked what a third reading would admit."* Counted:
**six** round READMEs discuss admission together with the judge, and **R301 already loads the 0.8B
pool**. The real gap is narrower and sharper than the sentence claimed — *the pool is loaded but
never enumerated*. §4's remedy is cheap and I skipped it: **run the count before writing a sentence
that quantifies over your own work.**

## Register — what this site cannot do

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — no third checkpoint on the local store |
| **Part B at 41 arms** | needs R301's subset-rebuild path, declined here |
| **why the rate differs 2×** | **open** — needs a precision sweep, not a two-point comparison |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the non-upward-closure is a fact about the 2B judge."*

**It replicates at a second judge on the same pool, at overlapping k — it is the estimator.**

Artifact: `results/r358_second_judge.json`, source-stamped.
