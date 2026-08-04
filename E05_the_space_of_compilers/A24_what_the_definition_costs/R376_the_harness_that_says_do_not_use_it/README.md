# R376 — the harness that says "do not use this harness" was counting its own probe file

**The decision this makes safe:** *is the isolation harness admissible?* **Yes — containment holds.
The failing criterion was measuring the harness's own scaffolding.** One of R374's five born-red
gates is now **satisfied**, by a repair proven not to be a disarm.

## Result — `W_CRITERION_MALFORMED_REPAIRABLE`. Four controls PASS. Two runs byte-identical. **No GPU spent.**

R375's NEXT was to classify what four commits *did*. The instrument for that —
`what_did_each_check_actually_read.py`, which records every file a check opens via a CPython audit
hook — is built on `assurance/_isolated.py`, and `_isolated.py` fails its own selftest and prints,
in its own words:

> **`FAIL — do not use this harness`**

So R375's question was **deliberately not answered**. Answering it first would have meant building
on an instrument that says not to use it.

## The two paths, read instead of counted

The failing line was `g=0 (harmless subject): exit 0, dirtied 2 path(s)` against a criterion of
`len(changed) <= 1`. The subject's entire body is `print('noop')`. **What are the two paths?**

| status | tracked? | path |
|---|---|---|
| `??` | untracked | `.venv` |
| `??` | untracked | `assurance/_noop_probe.py` — **the probe the selftest itself writes** |

**Zero tracked.** The criterion was counting the linked interpreter and its own scaffolding as
contamination — `realstat §4 · the control fails for its own reasons`.

## The classifier is not blind — the saboteur proves it

| | |
|---|---:|
| saboteur paths dirtied | **97** |
| of those, **tracked** | **95** |
| MAIN tree epochs before/after | **5 / 5 — SAFE** |
| the subject actually ran | **True** |

**Containment holds.** A tree surviving an attack that never happened is not evidence, so `rc` being
an `int` is checked explicitly.

## ⛔ The repair, and the proof it is not a deletion

New criterion: **no TRACKED path may be dirtied by the g=0 subject.**

| | tracked dirtied | verdict |
|---|---:|---|
| g=0 (`print('noop')`) | **0** | **PASSES** |
| saboteur | **95** | **STILL FIRES** |

> **A loosened criterion is a deleted control unless it still fails.** That 0-vs-95 contrast is the
> only evidence separating a fix from a quiet disarm — and it is why the threshold was **not**
> simply raised from 1 to 2, which would have passed the benign case for no stated reason and
> silently narrowed the destructive one.

`_isolated.py` now exits **0**, and its dependent `what_did_each_check_actually_read.py` still runs
green.

## ⛔ The prior that would have got this right for the wrong reason

This campaign's own ledger measures `the control fails for its own reasons` at **4 of 7**
mis-specified controls in one day — the dominant mode — with exactly **1 of 7** failing in the
flattering direction. **Betting the base rate would have produced this verdict with no evidence.**
A prior that happens to excuse my own harness is the one to trust least, so both worlds were built
and the paths were read.

## Controls

| | returned |
|---|---|
| **CLASSIFIER (+)** | `assurance/_isolated.py` classifies as **tracked** — known independently |
| **CLASSIFIER (−)** | a freshly written probe classifies as **untracked**. Both directions, because a classifier calling everything tracked would also "pass" the positive control |
| **SABOTEUR (+)** ⭐ | **95 tracked** paths seen on a genuinely destructive subject — if the classifier could not see that, every zero above would be silence |
| **SABOTEUR RAN** | `rc` is an `int`, checked explicitly |
| reproducibility | two runs **byte-identical** (`01620a8694f4`) |

## Register

| criterion | status |
|---|---|
| **whether some OTHER subject leaks** | **N/A** — this measured the **two** subjects `_isolated.selftest` defines. *"No leak here" is not "no leak."* |
| **what the four R375 commits did** | **deferred by design** — it depends on this instrument, and is now unblocked |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"the isolation harness fails its own selftest, so the read-set instrument is untrusted."*

**Containment was never in question — the main tree survives a subject that deletes an epoch, and
the restore heals from git. What failed was a criterion that counted `.venv` and its own probe.**

Artifact: `results/r376_isolation.json`, source-stamped.
