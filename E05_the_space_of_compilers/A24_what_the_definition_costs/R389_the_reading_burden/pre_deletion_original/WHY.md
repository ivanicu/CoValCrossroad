# The pre-deletion original of R389, recovered 2026-08-04 by R428

**This is not an archive of a superseded draft. It is the round as it existed before the tooling
destroyed it, recovered from `/tmp` two days later.**

R389's own README is titled *"...and my tooling deleted the round"*, and its artifact carries
`"destroyed_and_rewritten": true`. The round in the parent directory is therefore the **rewrite**.
These three files are the **original**, and their bytes had never been committed to git — R428's
`what_was_lost.py` established that with `git cat-file -e`, which found the blobs absent from the
object database entirely.

| | original (here) | rewrite (parent) |
|---|---|---|
| the statistic's name | `marker_pos` / `marker_neg` | `title_pos` / `title_neg` |
| `n_with_markers` | 158 | *(replaced by `n_my_format` 99)* |
| the README's claim | "The debt has **two tiers**" | "The debt is **two projects, not one**" |

**They are not the same analysis.** The rewrite renamed what was being counted, which means the
two documents answer slightly different questions, and reading either alone hides that the
question moved. That is why the original is kept rather than discarded: the rewrite is the
current round and remains the citable one, but the fact that a destruction event silently changed
an estimand is only visible when both exist.

**Where these bytes lived until today:** `/tmp/attack_rounds_zkpljpn8/`, one of **eight** orphaned
stashes left by `assurance/attack_the_suite.py` when a `finally:`-block restore was interrupted by
SIGKILL. `/tmp` is reaped. Had nobody looked, this would have gone.

⚠ **And the first attempt to preserve it put it in `_archive/`, which `.gitignore:3` ignores** —
recovering a never-committed file into an untracked path recreates exactly the loss it repairs.
`recover.py` now runs `git check-ignore` on its own destination and refuses.

Round: `E05.../A25_can_the_instrument_be_run_at_all/R428_did_the_eight_mutilations_cost_untracked_data`.
