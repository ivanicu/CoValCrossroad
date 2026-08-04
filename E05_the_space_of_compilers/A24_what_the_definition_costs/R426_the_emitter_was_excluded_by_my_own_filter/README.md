# R426 · R424 said the emitter is not on disk. My own filter excluded the directory it is in.

**The decision this round makes safe:** whether 74 artifacts and 11 downstream rounds are
`instrument-UNKNOWN`. **They are not.** The instrument is **`Qwen3.5-0.8B-Base`**, and the table is
**`corebench/results/sat08_full.npz`**.

## ⛔ The defect is one line — mine

```python
for p in sorted(ROOT.rglob("*.npz")):
    if ".venv" in p.parts or p.parent == RES:   # RES == corebench/results
        continue
```

R424 skipped **`corebench/results` entirely — 106 files, 4 of them full-shaped.** I wrote that filter
to stop the *arms* being tested as their own candidates and **threw the emitter out with them.**

**The second filter compounded it.** A candidate was admitted only if its meta key set *equalled*
`sat_full.npz`'s — and a per-arm table's key set **cannot** equal a full table's, so the 49
rejections excluded, by construction, every file that could have answered the question.

> **A population defined so the answer cannot be in it returns a clean, confident, false zero — and
> prints the same string as a real absence.**

## The measurement

| `sat08_full.npz` contains | rate |
|---|---|
| `oracle_k4_08b` | **`1.0000`** (15,448 of 15,448) |
| `oracle_k4_08bR` | **`1.0000`** (15,460 of 15,460) |
| `topw_k4` | **`0.0369`** (570 of 15,440) |

**The exact mirror of the default table** (`1.0000` on `topw_k4`, `0.0380` on `_08b`). That reversal
*is* the emitter's signature — a table containing everything would score high on both, and the
`W-DENSE` branch existed to catch exactly that.

## Controls

| control | returned |
|---|---|
| ANCHOR (+) · default contains `topw_k4` (it emitted it) | `1.0000` (15,440 of 15,440) |
| ANCHOR (−) · default contains `oracle_k4_08b` — the floor | `0.0380` (587 of 15,448) |
| PLANT · a synthetic value is not contained | PASS |
| ⭐ **POPULATION** · `.npz` files R424's filter excluded | **106**, 4 full-shaped |

**`POPULATION` is the control R424 did not have, and its absence is the whole reason R424 is wrong.**
A search is an instrument and its *population* is part of it; no blindness in the pattern is needed
to return a false zero if the population cannot contain the answer.

## ⛔ And the source said so all along — the part that costs most

| file | line |
|---|---|
| `R290/run.py:58` | `JUDGES = {"2B  Qwen3.5-2B-Base": "sat_", "0.8B Qwen3.5-0.8B-Base": "sat08_"}` |
| `R301/run.py:123` | *"`topw_k4` and `random_k4_s0` were judged directly at 0.8B in R290"* |

**The model was named, in committed source, in rounds my own R425 census had already listed** — R301
is item 1 of its 11, and I never opened it. **The refutation was inside my own output.** I treated
artifact containment as the *only* admissible evidence about provenance and called the result an
impossibility: *a wall makes stopping feel earned, so it is never audited.*

## What each round now stands at

| round | status |
|---|---|
| R422 | UNVERIFIED (join key) — unchanged |
| R423 | repair sound; families agree at ≤ 0.03 % — **stands** |
| R424 | **OVERTURNED** — population error, not new data. Every artifact it tested, it tested correctly |
| R425 | census **stands** (15 / 11 / six knowns); its closing sentence **retracted** |
| **R426** | emitter identified; `instrument-UNKNOWN` retracted in both claim documents |

⚠ **Containment is necessary, not sufficient.** A superset table would also contain these values; the
`topw_k4` contrast bounds that but does not remove it. The artifact claim is *"the table whose values
these are"*, and the **model** behind it is **source-attested**, not artifact-verified. **Conflating
those two kinds of evidence is what built the wall in the first place.**

Findings, with their scope, live in the top-level README. This file states the design.
