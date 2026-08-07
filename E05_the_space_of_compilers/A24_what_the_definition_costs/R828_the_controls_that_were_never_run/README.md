# R828 · the controls that were registered and never run

**The decision this made safe:** whether the numbers of the rounds carrying a collapsed control can
still be cited. **They can.** All three recoverable checks pass; what was missing was the assurance,
not the result.

Design in `PREREGISTRATION.txt`, committed before `run.py` was executed. `run.py` committed before
it was run.

## What was flagged, and how each was adjudicated

`assurance/a_control_that_cannot_fail.py` found 6 rounds in `E05/A24` whose registered control is
algebraically constant. R436 was adjudicated in the previous round. The remaining five:

| round | the collapsed expression | second producer? | verdict |
|---|---|---|---|
| R332 | `\|v − v\|.max() == 0` | **`rate()`** `run.py:155` | **RECOVERED · PASS** |
| R672 | `len(s0 − s0) == 0` | **`versions()`** `run.py:64` | **RECOVERED · PASS** |
| R731 | `abs(M[…]["eff"] − M[…]["eff"]) == 0` | **`cell()`** `run.py:43` | **RECOVERED · PASS** |
| R361 | `rank[j][a] − rank[j][a] == 0` | none — a dict comprehension | **UNRECOVERABLE** |
| R746 | `cov[a]["prompts"] − itself` | none | **PARTIAL** |

**The discriminator was named before any answer was looked at**: a collapsed control is recoverable
**iff a second producer of the same quantity exists**. R436 established it — two scoring call sites
existed and the check named their agreement.

- **R361 is unrecoverable, not failed.** `rank[j]` is built by one dict comprehension, and a
  *duplicated* arm would receive an **adjacent** rank, not an equal one — so the registered property
  is not merely un-implemented, it is **false as stated**. UNVERIFIED, never a pass and never a fail.
- **R746 is partial.** Its constant difference is conjoined with `and len(cov) > 0`, which is a real
  empty-population guard. Half the control is live.

## The arm that makes this a measurement

Every perturbed producer is fed to **both** checks:

| | recovered check | the original `x − x` |
|---|---|---|
| unperturbed (g=0) | **PASS** ×3 | PASS ×3 |
| perturbed | **FAIL** ×3 | **PASS ×3 — it was blind** |

R332 separates **0.0 → 1.0**: a row cannot beat itself, and the `>=`-perturbation makes it beat
itself always, while `|v−v|.max()` stays exactly 0 through both.

**Without that second column, "the collapsed control had no power" is an assertion about code I
read. With it, it is a measurement.**

## What it rests on

- the kill is a **conditional**, not a threshold: the world is evaluated only if every positive
  control fires **and** every original stays blind. Otherwise `UNVERIFIED`.
- a producer that will not run is **UNRUNNABLE**, exits 2, and is never scored as a pass or a fail.
- two-seed byte-identical: `PYTHONHASHSEED` 1 and 2 → `1c35cc0c7eaca56fa1b0f095738e36a3`.
- artifact `results/r828_recovered_controls.json` with the source hash of every module read.

⚠ `R672.n_versions` is a function of repository history and grows with each commit. It is stable
within a run and is **not** a stable cross-time value; nothing is claimed from its magnitude.

## NEXT

`assurance/a_control_that_cannot_fail.py` is sound in one direction only — a flag proves constancy
and its silence proves nothing, because constancy has forms a syntactic rule cannot see. The next
step is a **differential** detector: perturb a producer and check that the round's own control
notices, which is what this round did by hand three times.
