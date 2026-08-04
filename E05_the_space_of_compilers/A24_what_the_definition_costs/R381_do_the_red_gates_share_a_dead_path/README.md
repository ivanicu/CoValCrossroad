# R381 — the verdict moved against my hypothesis at every improvement to the instrument

**The decision this makes safe:** *do the remaining nine red gates share one dead path?* **No.**
R380's repair generalises to nothing, and each remaining gate is its own round.

## Result — `W_NOT_A_PATH_PROBLEM`. Three controls PASS. Two runs byte-identical. **No GPU spent.**

R380's NEXT proposed *"grepping every assurance script for the literal `rounds/` prefix."*

## ⛔ That instrument presupposes its own answer

A grep for `rounds/` can only find gates dead in the **one way already known**. A gate pointing at
`campaigns/`, or renamed for an unrelated reason, is invisible to it — so a zero would read as *"no
others"* while meaning *"none of the kind I looked for"*. Instrument unit: **the string I guessed**.
Claim unit: **a path expression that resolves to nothing.** Not equal.

So every path expression was extracted with `ast` and handed to the filesystem.

## ⭐ The verdict changed four times, and every change was a false positive removed

| instrument | red gates with a dead round-path | verdict |
|---|---:|---|
| v1 · string literals | — | **control FAILED, caught before publication** |
| v2 · composed expressions | 2 | `W-ONE-DEAD-PATH` — *"they are ONE fix"* |
| v3 · regexes separated | 1 | `W-EACH-ITS-OWN` |
| v4 · written-into-text excluded | **0** | **`W-NOT-A-PATH-PROBLEM`** |

**Every precision improvement moved the verdict *against* the hypothesis I had written.** The ledger
puts it exactly: *when a loose and a tight pattern disagree, the tight one is not "more
conservative", it is the one that was tested.*

## The three false positives, each a different kind

**① v1 could not see the target at all.** R380's dead path is written
`(ROOT / "rounds").glob("E*/A*/R*/run.py")` — **two literals, neither dead alone**: `"rounds"` has
no separator, and `"E*/A*/R*/run.py"` matches **363** files relative to ROOT. **The dead path is not
a literal, it is a composition.** The positive control caught it *because its answer came from a
prior round*, not from this one.

**② A regex is not a path.** `donor_numbers_carry_their_draw_scope` was flagged for
`rounds/r8[89]_[a-z_]+\)` — a pattern matched against README **text**, never globbed. Asking the
filesystem whether it exists answers a question nobody posed.

**③ A literal written *into* text is not a path read from disk.** `attack_every_check` contains
`text.replace(<real round link>, "rounds/_no_such_round")` — the replacement is **designed** not to
exist, planted to make a check fire. Excluded **structurally** (the second argument of a `.replace`
call), not by a word list, so the rule does not depend on the fixture being named `_no_such_*`.

## ⭐ A different candidate class did emerge — and it needs a different instrument

**Three red gates carry regexes encoding a stale link format:**

| gate | pattern |
|---|---|
| `donor_numbers_carry_their_draw_scope` | `rounds/r8[89]_[a-z_]+\)` |
| `synthesis_cites_recent_work` | `(?:\d\d_[a-z0-9_]+/)?r(\d+)_` |
| `seed_filter_is_disclosed` | `len\(raters\)\s*\+\s*1\)\s*//\s*2\|>=\s*thr\b` |

**Separated and NOT counted**, because the right question for a pattern is *does it match anything in
the documents it is applied to* — which `glob` cannot answer.

## Controls

| | returned |
|---|---|
| **EXTRACTOR (+)** ⭐ | the **pre-repair** gate, read out of git, must be flagged carrying `rounds/E*/A*/R*/run.py`. **The answer comes from R380, not from here** — which is the only reason v1 could fail before publication rather than after |
| **EXTRACTOR (−)** | a live glob is not flagged, **and** the post-repair gate comes back clean. Both directions, because an extractor flagging every literal would pass the positive control |
| **JOIN** | a dead literal alone is not a defect — every candidate is joined to R379's independently measured read-set, and both counts are printed so the join is visible rather than assumed |
| reproducibility | two runs **byte-identical** (`8ea9e7935e4e`) |

## Register

| criterion | status |
|---|---|
| **runtime-assembled paths** | **N/A, and the blind spot has a size**: **715** f-string expressions across 44 modules are invisible to `ast`. A number, not a disclaimer |
| **whether a dead literal CAUSES a failure** | **N/A** — R380 needed a whole round to prove that for one gate, with a disarm proof. This **locates candidates** |
| **the three stale regexes** | **candidates, not findings** — they need an instrument that matches patterns against documents |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect `rounds/` to be a dead directory that several gates still point at …
> if several gates share one dead path then they are one fix."*

**Zero red gates carry a dead path that is a defect. R380's repair generalises to nothing, and the
one-round-per-gate rate it measured is the rate to plan with.**

Artifact: `results/r381_dead_paths.json`, source-stamped.
