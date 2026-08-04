# R390 — the untitled tier is not silent: 5 of 8 state a verdict anyway

**The decision this makes safe:** *is the 68-round tier unbackfillable?* **No — but it is not uniform
either.** `W-MIXED`, and the counts are the estimate.

## Result — `W_MIXED`. Three controls PASS. **The live tree was never a subject's cwd.**

| | |
|---|---:|
| subjects run | **8 of 68** |
| RAN / UNVERIFIED | **8 / 0** |
| **state a verdict in output** | **5 (62%)** |
| silent | **3** |

| round | secs | verdict? |
|---|---:|---|
| R144_information_loss | 10.2 | no |
| R145_who_is_unserved | 4.7 | **YES** |
| R147_tracking_vs_serving | 4.6 | no |
| R148_departure_from_the_line | 6.8 | **YES** |
| R149_price_of_inclusion | 8.7 | **YES** |
| R150_does_the_veto_do_anything | 0.4 | no |
| R151_none_of_the_above | 3.3 | **YES** |
| R152_what_fails_the_menu | 10.7 | **YES** |

**R389's split was a property of the docstrings, not of the findings** — most of the untitled tier
still says what it concluded, in the place that matters.

## ⛔ Safety is why this round is built the way it is

R389's first copy was destroyed by running `_isolated.py` **as a script**: its selftest plants a
saboteur that deletes an epoch directory, and it ran against the **live tree** — 1,408 tracked files
plus every uncommitted one. **This round manages its own worktree and never imports or executes that
module.** The live tree was never a subject's cwd, and it is clean after the run.

## ⛔ Two defects, both caught by the positive control, both mine

**① Avoiding `_isolated` cost me its input linking.** A fresh worktree holds only **tracked** files,
so `data/` contains `fetch.py` and none of the 69 MB release, and `.venv` is absent. R21 and R28 load
models and died; R24 does not and ran. **The linking is replicated here per entry** — a directory git
has materialised for a tracked file must be *filled in*, not skipped, which is the exact repair
`_isolated` records having made after every isolated run in its history executed against an empty
`data/`.

**② My timeout was too small and would have convicted the tier with my own clock.** R28 completes in
36 s warm and exceeded **120 s** cold — model loading across a symlinked store is slower on first
touch. The control reported `None`. Raised to **300 s**.

> **A timeout is a statement about the budget, never about the subject** — and had `TIMEOUT` been
> folded into "silent", the untitled tier would have been convicted by a number I chose.

## Controls

| | returned |
|---|---|
| **VERDICT (+)** ⭐ | the three units already paid are all detected — **their answer comes from R389**, not from this pattern. This control caught both defects above |
| **VERDICT (−)** | a bare table of numbers is **not** detected. Both directions, because a pattern matching any line would pass the positive control and mean nothing |
| **ISOLATION** | subjects run only in this round's own worktree; `_isolated.py` never imported |
| **UNVERIFIED** | counted apart from silent. **A dead round is not a quiet round** |

## Register

| criterion | status |
|---|---|
| **whether a verdict line is TRUE** | **N/A** — detection is structural; truth is a judgement |
| **whether a silent round HAD a finding** | **N/A** — absence bounds what can be **read**, not what was found. *A round with no stated verdict may still have had a finding its author never wrote down — which is the whole reason this debt exists* |
| **all 68** | **8 run, 60 untried** — named, not assumed |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect at least some of the 68 to be unbackfillable at any honest cost, because a
> round that never named what it was for may not have HAD a finding."*

**Five of eight state a verdict in the place that matters. The docstring title was cosmetic for most
of them — and for the three that are silent, the question is still open, because a round that
printed no verdict may simply never have been asked to.**

Artifact: `results/r390_untitled_tier.json`, source-stamped.
