# R573 · They are not hanging — they are meta-gates under a 90-second cap

**Decision this makes safe:** whether `ERROR 3` is a defect. **It is a budget mismatch.**

**WORLD B, and it retracts my own claim from two rounds ago.**

## The localisation, step by step
| step | result |
|---|---|
| module import | **completes, rc=0** |
| `ensure_worktree()` | **0.0s** |
| `restore(wt)` | **0.1s** |
| the loop | **runs EVERY `assurance/*.py` inside the worktree, with a `restore` between each** |

⭐⭐⭐⭐ **So it is not hanging. It is a meta-gate doing ~46 gates' work — plus a git restore per
subject — under a 90-second cap. R571 measured the suite itself at 4–5 minutes serially. 90s is
unreachable by arithmetic.** The exact `90.09s` is a **cap-kill mid-work**, not a deadlock.

## What this retracts
**R571 said the three gates "do not terminate" and that `ERROR 3` "is a hang, not a tuning
problem."** ⛔ **Both wrong for at least this one.** The reasoning was: 43 gates under 6.2s, 3 pinned
exactly at the cap ⇒ terminating vs non-terminating. **The bimodality is real and the inference was
not** — the 3 are pinned at the cap because they are **doing 46× the work**, which produces exactly
the same signature.

## Three hypotheses refuted inside this round alone
1. **the re-entrancy guard explains it** — it is a **re-entrancy** guard (`if os.environ.get(...)`),
   so standalone it is the first sweep and never fires. **0 bytes of output confirmed it never ran.**
2. **it hangs at import** — import completes.
3. **the git ops are slow on a 293 MB repo** — 0.0s and 0.1s.

⚠ **Still open:** whether `backfilled_findings_are_rederivable` (4 subprocess calls) is the same
shape. **Not established here**, and R572's two-sided result — subprocess neither necessary nor
sufficient — still stands.

⭐ **Fifth consecutive round with a refuted central hypothesis, and the second in a row that still
answered its question.**
