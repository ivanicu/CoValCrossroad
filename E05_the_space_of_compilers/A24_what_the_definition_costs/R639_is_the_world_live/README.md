# R639 · The world that fires on nothing is live in committed code, in 7 harnesses not 1

**Decision this makes safe:** the scope of the repair. **Seven harnesses, and the failure count is
load-bearing.**

| | |
|---|---|
| rounds scanned | 314 |
| **harnesses that RUN another round** | **7** — my closing line said *"only one"* |
| mention a `run.py` path without executing | 22 |
| shell out to a **gate** only | 27 |
| run nothing | 221 |

## ⛔ The `failed` count reaches a VERDICT branch — the world is live
`elif len(failed) >= len(names) / 3:` is present in R636. **The world-C threshold is computed from
the failure count**, and R638 established that a non-zero exit is a **verdict** in 95 of 313 rounds.
**So it is not a reporting nicety.** ⚠ **DERIVATION, labelled:** the branch either references the
count or it does not; this could not have come out otherwise.

## The repair, and its intervention
> **THE PROHIBITION: a non-zero exit is UNKNOWN, never failure. Only an unrunnable path counts.**

| cell | classification |
|---|---|
| exit 0, path exists | RAN |
| **exit 1, path exists** | **RAN (non-zero verdict, UNKNOWN)** |
| **exit 2, path exists** | **RAN (non-zero verdict, UNKNOWN)** |
| nonexistent path | **FAILED** |

**World-C count: 3 of 4 under the old rule → 1 of 4 under the prohibition.**

## ⛔⛔ The pattern was wrong in BOTH directions, and only the positive control told them apart
- **v1 over-matched:** `/ "run.py"` fires on any round that merely *builds* a path — the
  mention-vs-use error of R631 and R633, **a third time**. It reported **25**.
- **v2 under-matched:** it required `run.py` *outside* any parenthesised subexpression, while every
  real call nests it — `subprocess.run([str(PY), str(A24 / n / "run.py")], …)`. It reported **5** and
  **missed R636**, the one round I had watched execute 43 others.
- **v3** windows the match and is validated against the known member **before** the count is read: **7**.

⭐ *A loose pattern and a tight pattern disagreed, and neither was "more conservative" — both were
wrong. The positive control is what distinguished them, exactly as §4 prescribes.*

## Controls
| control | returned |
|---|---|
| **positive** — R636, which demonstrably runs rounds | **found** — PASS *(failed under v2, which is how v2 was caught)* |
| **g=0** — gate-only rounds are not counted as round-harnesses | **27 excluded** — PASS |
| **negative** — a planted exit-1 round must not count as failed, an unrunnable path must | **PASS** |
| **placebo** — rounds that run nothing | **221 not counted** — PASS |

**MULTIPLICITY:** 314 rounds × 1 scan + 4 intervention cells + 4 controls.

**IMPOSSIBLE, named:** **no classifier is checkable beyond the prohibition itself.** R638 found **18
meanings for `EXIT 1`**, so a repaired harness cannot be validated against the corpus's semantics —
only against the weak negative rule.

## ⛔ Check #240
*"**Only one** harness runs rounds"* — **seven.** *"Cheap to install"* — **the third uncomputed cost
claim in four rounds**, after *"re-runs are expensive"* (to avoid work) and *"the fix is one line"*
(to justify it). ⭐ **All three felt obviously true; the two that were later measured were wrong by
260× and by "there is no fix at all".**

## The sentence I can no longer write
> *"only one harness in the corpus runs rounds, so the repair is local."*

**Seven do, and the count they compute feeds a verdict.**

## NEXT
The prohibition is one predicate and seven call sites, but **six of the seven predate this arc and
their conclusions are already committed.** Before editing any of them, **check whether each actually
reports a failure count** — R396 and R390 may run rounds for timing or content, never for
success/failure — because editing a harness that never classifies would be a change with no
consequence, and the count of harnesses that *do* classify is the real size of this repair.
