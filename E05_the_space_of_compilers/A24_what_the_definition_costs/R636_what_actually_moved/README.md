# R636 · I measured the cost of failing and called it the cost of doing

**Decision this makes safe:** whether to substitute a proxy for re-running the 43. **No — but not
for the reason I gave, and not for the reason I then "measured".**

## THE RESULT — verdict `UNVERIFIED`, and the cause was me

**Positive control first, as pre-registered: 38 of 38 re-runnable rounds reproduced BYTE-IDENTICALLY
→ PASS.** So "changed" and "nondeterministic" are distinguishable and the diff count is interpretable.

⛔ **The NEGATIVE control failed.** It compares `git status` before and after — and **I ran
`git add -A` and `git reset` while the round was measuring the repository.** ⭐⭐ **Fifth
self-contamination, and a new vector: not the round's own artifact inside its population, but the
OPERATOR acting on the population during the measurement.** Per P6 the verdict stays `UNVERIFIED`;
a clean re-run with nothing else touching the repo is owed.

| | |
|---|---|
| re-runnable | **38 of 43** (5 exit 1 — below the 1/3 world-C threshold) |
| wall clock | **284 s** |
| byte-identical | **38** |
| textually changed | 18 |
| **verdict-bearing changes** | **12** |

### ⭐⭐⭐ And the mechanism is not the one this arc was chasing
| round | before → after |
|---|---|
| R500 | inconsistency at **18/98 → 20/174** |
| R601 | **18 → 21** cross-release rounds |
| R596 | `R[501]` → `R[501, 604, 625]` |
| R593 | p = **0.0012 → 0.0366** |
| R597 | `D FIRES ONCE, correctly bound` → **`B LIVE`** — a paragraph may ride a word not about the round it allows |
| R463 | `W-FORCED` → **`W-DISCRIMINATES`** |

**Every one is the denominator growing.** **The corpus is the population, it grows every round, and
these rounds measure the corpus** — so their conclusions have a **shelf life measured in rounds**.
**R635's narrow key set, this arc's entire premise for the 43, is not what moved them.**

⚠ **Observations, not verdicts** — the round is `UNVERIFIED` and these are reported as what was seen,
not as what was established.

⚠ **STATUS (superseded): the re-run has completed.** What is established below does not depend on its result;
the verdict on what moved is **PENDING** and is not reported here as anything else.

## ⛔⛔ The triple reversal, in order
| step | claim | what it rested on |
|---|---|---|
| 1 | *"re-runs are expensive, so the cheap question first"* | **nothing** — an uncomputed cost |
| 2 | *"false by three orders of magnitude — 0.1 min for all 43"* | **43 crashes**, timed |
| 3 | the honest re-run under the project venv | **exceeded a 2-minute timeout, still running** |

⭐ **So the original claim was unjustified when made and closer to true than the refutation I built
against it.** Same shape as R633's *right number, wrong method* — **twice in one session.** *A memory
that happens to be right is the worst case, not the best: it survives, it gets quoted, and nothing in
the process distinguishes it from the ones that are wrong.*

## ⭐ A load failure is an environment claim — and the alarming reading was one step away
Under the system python all 43 exit 1 in 0.1 s on `ModuleNotFoundError: numpy`. **"43 rounds do not
execute" was available, cheap, quotable, and false.** The project ships `.venv` on miniforge 3.13.13
with numpy 2.4.6 and they import fine under it.

**And it generalises:** **155 of 312 rounds (50%)** import numpy, torch, scipy or sklearn.

> **A 0.1 s exit-1 is indistinguishable from a fast successful run if you only time it.**

That is exactly the mistake in step 2, and it was available across half the corpus.

## The design, which stands whatever the run returns
- **Estimand:** of the 43, how many produce a **different verdict** when re-run today.
- **Separation:** verdict-bearing diffs vs cosmetic ones (timestamps, source hashes).
- **Positive control:** at least one artifact must reproduce **byte-identically**, or "changed"
  cannot be distinguished from "nondeterministic".
- **Negative control:** the tree is restored with `git checkout --` and `git status` must return to
  its pre-run state.
- **Placebo:** no file outside a round's own `results/` may be touched.
- **World C is reported FIRST** if ≥1/3 fail to run, because **an unreproducible round's key set is
  moot** — reproducibility outranks the question that motivated the round.

**IMPOSSIBLE, named:** **a round can be deterministic and still wrong.** Re-running proves only that
today's code on today's data gives today's answer; **it cannot validate the answer.**

## ⛔ Check #235
⛔ *"**Both** remaining directions are re-runs"* — a universal over a set never enumerated.
⛔⛔ *"re-runs are **expensive**"* — the fabricated-wall shape: an asserted cost that makes
substituting a proxy feel earned, **and a wall nobody audits because stopping already feels
justified.**

## The sentence I can no longer write
> *"re-running is too expensive, so measure a proxy instead."*

**Not because it is false — it may well be true — but because I had not measured it, and when I did,
I measured crashes.**

## NEXT
The verdict on what moved is pending. **When it lands, the first thing to check is the POSITIVE
CONTROL**, not the headline: if no artifact reproduces byte-identically, then "changed" and
"nondeterministic" are the same observation and the entire diff count is uninterpretable — which
would make the round a reproducibility measurement rather than a debt measurement, and that is the
outcome world C was pre-registered to catch.
