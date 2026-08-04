# R375 — four commits, not one; and the gate I was most confident about flickers

**The decision this makes safe:** *is the six-gate regression one repair or a backlog?* **A backlog —
four separate repairs.** My own pre-registered hypothesis is refuted.

## Result — `W_CLUSTERED`. All seven controls PASS. Two runs byte-identical. **No GPU spent.**

R374 localised six green→red transitions to one 256-commit bracket and I wrote:

> *"[HYPOTHESIS] I expect a single commit to account for most or all six, because six independent
> regressions inside one bracket is a far worse explanation than one shared cause."*

**It does not.** 86 evaluations over 85 checkouts:

| distinct breaking commit | date | gates | commit subject |
|---|---|---:|---|
| `380fcfb18` | 07-31 | **2** | *The README was a 1,433-line research diary…* |
| `3c3fe2482` | 07-30 | 1 | *Three findings, each verified as a grid rather…* |
| `9273f32e0` | 07-29 | 1 | *The donor draw does not cancel across bins…* |
| `60f3871b5` | 07-29 | 1 | *The package was one commit away from shipping…* |

**5 monotone gates → 4 distinct commits.** Neither one shared cause nor six independent ones. Only
`seed_filter_is_disclosed` and `synthesis_cites_recent_work` share a break, and the transitions span
**three days**, not a moment.

## ⛔ The monotonicity control fired, and it is the reason this round is worth anything

**A bisect presumes monotonicity.** Binary search for "the first red commit" is well defined only if
the gate goes green…green red…red exactly once. So after each transition, 3 commits were probed on
each side.

**`attack_every_check` flickers.** It is red at `0c6620678` and `8e2660d3a` — *before* the commit the
bisect returned. A plain bisect would have handed me **`2580fb140`** with full confidence, and that
commit is not where it broke, because there is no single place where it broke.

> **`The commit that broke it` is not a well-formed object for that gate.** It is withdrawn from the
> count rather than given a spurious answer.

## Controls

| | returned |
|---|---|
| **HARNESS** | `consistency` **0 live / 0 worktree**; `seed_filter_is_disclosed` **1 live / 1 worktree** — a harness that cannot reproduce HEAD's status makes every red its own artifact |
| **ENDPOINTS** ⭐ | re-measured **here**, not inherited from R374: all **6 of 6** reproduce green→red. R374's ladder and this bisect must agree about the bracket they share, and they do |
| **MONOTONICITY** ⭐ | 3 probes each side per gate. **Fired on 1 of 6** |
| **CACHE** | keyed on the full sha, so a repeated probe returns the same answer — 86 evaluations, 85 checkouts |
| reproducibility | two runs **byte-identical** (`2f741c0e76fa`) |

## Why the count could have come out otherwise

The six breaking commits were free to be six, one, or any grouping — **each gate was bisected
independently against its own endpoints**, and the grouping is read off afterwards rather than
fitted.

⚠ **Labelled, because it is partly forced:** a commit that touches nothing a gate reads cannot change
its verdict, so gates reading the *same* surface have correlated transitions **by construction**.
That is why "one commit" would have been interesting only if the commit were also *plausible* as a
cause — and this round measures the commit, never the causation.

## What this round does NOT do

**It returns a commit, never a cause.** No sentence here says what `380fcfb18` did to
`seed_filter_is_disclosed`. Reading a cause off a diff is a separate step and is deliberately not
attempted, because a plausible story about a diff is exactly the kind of evidence that costs nothing
to produce.

## Register

| criterion | status |
|---|---|
| **WHY each commit broke each gate** | **N/A by design** — returns a commit. Naming the cause is the next step |
| **the five BORN RED gates** | **N/A** — they have no transition to find (R374) |
| **`attack_every_check`'s break** | **UNVERIFIED, not unknown** — it flickers, so the object does not exist in the form the question assumed |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"six gates changing state in one bracket is one commit far more plausibly than six."*

**It is four commits over three days, and a fifth gate whose transition is not a point at all. The
bracket was an artifact of a 12-rung ladder, exactly as the W-INDEPENDENT branch warned — and I
wrote that branch and still predicted the other one.**

Artifact: `results/r375_bisect.json`, source-stamped.
