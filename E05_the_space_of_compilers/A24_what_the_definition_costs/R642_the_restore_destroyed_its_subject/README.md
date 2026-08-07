# R642 · The restore destroyed its own subject, and "strictly more general" was not better

**Decision this makes safe:** whether the prohibition works, and which predicate to install.
**It works. Install the keyword list, not the stderr rule.**

| | before | **after the prohibition** |
|---|---|---|
| byte-identical reproductions | 38 | **43** |
| verdict-bearing changes | 12 | **12** — unchanged, as pre-registered |
| artifacts changed | 18 | 19 |

**The five rounds the harness called "failures" all exit 1 as a declared verdict**, so they now count
as `ran`. **That is the measurement.**

## ⛔⛔⛔ And the round's own negative control reverted the repair, mid-run
`git checkout -- <A24>` is scoped to a directory **that contains this harness.** It restored
`run.py` along with the artifacts, **wiping the prohibition**; the tree then differed from its
recorded pre-state and the control failed. **Verified after the fact: the `PROHIBITION` token count
on disk was 0.**

> **A cleanup scoped to a directory that contains the instrument will revert the instrument.**

**Seventh self-contamination in this arc, and a new vector** — not the artifact inside its population
(R601, R604, R621, R634), not the operator acting on it (R636), not the instrument matching itself
(R637), but **the instrument's cleanup destroying the instrument's modification.**
**Repaired:** the restore now walks each round's `results/` and never touches source.

## ⛔ The "better predicate" is retracted — by the round I named as its only risk
Last turn I proposed the stderr rule, called it *strictly more general*, and bounded its failure
population at **"≤ 1 of 317"**. ⭐ **That bound was doing the opposite work I read it as doing: it did
not mean *almost safe*, it meant *there is exactly one candidate — go look.*** One grep:

**`R576` writes JSON to stderr as an IPC channel AND calls `sys.exit(2)`.**

| rule | unseen crash types | `R576` (a verdict) |
|---|---|---|
| **keyword list** (installed) | misses them | **RAN ✓** |
| stderr rule | catches them | **FAILED ✗** |

> **"Strictly more general" is not "better."** Generality bought coverage of *hypothetical* crashes
> at the price of the corpus's *one actual* verdict. **Neither dominates.**

## Controls
| control | returned |
|---|---|
| **positive** — byte-identical reproduction | **43** — PASS, and the 38→43 jump *is* the prohibition's effect |
| **negative** — tree restored to its pre-run state | ⛔ **FAIL** — diagnosed above, repaired |
| **placebo** — files touched outside a round's `results/` | **0** — PASS |

**VERDICT: `UNVERIFIED`.** A failed negative control is not overridden by a passing positive one.
What stands is ① as a measurement and ② as a diagnosed cause with a repair.

**IMPOSSIBLE, unchanged:** **no rule can decode the 18 semantics of `EXIT 1`.** Only the
deliberate-vs-crash distinction is available, and it is **operational, not semantic**.

## The sentence I can no longer write
> *"the stderr rule is strictly more general, and its failure population is bounded at one, so it is
> safe to install."*

**The one was real, and a bound that small is an instruction to check, not a licence to stop.**

## NEXT
The restore is repaired but **untested** — and this round is precisely the case that shows an
untested restore can destroy what it was protecting. **Re-run R636 once more and check only the
negative control**, because if it passes, both the prohibition and its cleanup are verified together;
and if it fails again the cause is no longer the scope, since source is now excluded by construction.
