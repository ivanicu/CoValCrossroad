# R506 · A core is a ranker by construction — so one ceiling applies, and the gap resolves at 20 draws

**Decision this makes safe:** which ceiling bounds a core, and whether `oracle_k4` clears it.
**The ranker ceiling, and yes.** The recommendation of reading **B** is **restored**.

## The derivation that picks the ceiling — read from `score.py`, not measured

`yvec(sat_p, idxs)` returns **one scalar per response** (the sum of that response's saturations over
the selected criteria); `cls(y)` takes `sign(y[i] − y[j])`. **A scalar per item induces a total
order, so a core's six pairwise verdicts are necessarily transitive.** It cannot emit the intransitive
patterns the per-pair mode uses on **33.5%** of prompts *(R505)*.

- **RANKER ceiling** — the only bound that can apply to a core.
- **PAIR-PREDICTOR ceiling** — unattainable by any core. **Comparing a core to it was the category
  error R504 committed.**

**Labelled as a derivation.** Once `yvec` returns a scalar this could not have come out otherwise.

## The resolution sweep — the earlier verdict was about effort, not nature

| reps per prompt | gap (`oracle_k4` − ranker ceiling) | floor | |
|---|---|---|---|
| 1 | +0.0042 | 0.0091 | inside |
| 5 | +0.0056 | 0.0082 | inside |
| **20** — the campaign's own convention | **+0.0073** | **0.0035** | **RESOLVED** |

**`oracle_k4` 0.6293 vs ranker ceiling 0.6220.** The floor falls **0.0091 → 0.0035** as draws go
1 → 20 while the gap holds. **R504 and R505 both stopped at "inside the floor" without asking for
more draws** — which is §4's longest entry verbatim: *a correction inherits the resolution of whatever
made it, and nobody asks the cheapest question left: does the data have more to give?* **It had 20×
more, and R479 had been using it all along.**

## The four-step sequence, which is the real record

1. `0.6282 > 0.6132, therefore B` — two numbers from **two instruments**, never checked.
2. Recomputed → oracle **below** the ceiling → **withdrawn**. Right that they were incomparable,
   **wrong that there is one ceiling**.
3. **Two ceilings** — both legitimate, bounding different constraint classes; gap inside the floor of
   both. Right about the structure, **still under-resolved**.
4. **The core is a ranker** (derivation), so one ceiling applies; at 20 reps the gap **resolves**.

**Every step used the best instrument available at that moment; every step was overturned by a better
instrument, never by a better argument.**

## Controls

Unchanged from R504/R505 and all passing: the in-sample ceiling exceeds the held-out one, so the
hold-out is genuinely applied; a shuffled-annotator ceiling falls toward chance; the random predictor
lands well above zero. The verdict branches on `gap_rank` **alone** — the pair-predictor figure is
printed as context, never as a criterion.

## The bound that remains

The recomputed ranker ceiling is **0.6220** against R479's quoted **0.6132**. Smaller than the gap it
replaced and **still not isolated** — stated rather than smoothed over.
