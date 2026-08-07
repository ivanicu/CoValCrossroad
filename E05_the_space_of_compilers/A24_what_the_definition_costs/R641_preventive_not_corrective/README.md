# R641 · The repair is entirely preventive — and four artifact reads replaced four re-runs

**Decision this makes safe:** whether installing the prohibition reissues any committed conclusion.
**No. Not one.**

| harness | committed failure count | corrective? |
|---|---|---|
| R319 | `n_failed = 0` | no |
| R322 | `failures = {}` | no |
| R388 · R396 | **no failure key persisted** | no — they classify in code, never in the record |
| **R636** | `failed = 5` | **no — all 5 declare an `EXIT` convention** |

**5 of 5 of R636's "failures" are verdicts**, so under the prohibition its count is **0**. **Every
classifying harness records zero. The repair guards the future only.**

## ⭐⭐ The cost claim justified the expensive plan, again
My closing line proposed **re-running the four harnesses** to diff their counts. Those harnesses
**run other rounds** — R396 is **GPU work** — so the plan was to execute a large fraction of the
corpus. **Four artifact reads answered the same question**, because *a harness that never recorded a
non-zero count cannot have its conclusion changed by a rule that only reclassifies non-zero exits.*

⭐ **Fifth uncomputed cost claim in six rounds** — *expensive · one line · cheap to install · one
predicate and seven call sites · small enough for one round* — **and this is the second time the
cheapest path was not the one the claim pointed at.**

## Controls
| control | returned |
|---|---|
| **positive** — R636 must be found recording a non-zero count | **5** — PASS |
| **g=0** — a harness recording zero must not count as corrective | R319, R322 excluded — PASS |
| **negative** — a harness with no failure key classifies as **"no record"**, never as zero | R388, R396 — PASS; **absence and zero are different claims** |
| **placebo** — a key name no artifact uses | **0** — PASS |

**MULTIPLICITY:** 5 harnesses × every artifact key + 5 entry lookups + 4 controls.

**IMPOSSIBLE, named:** **console output is not the record.** A harness that prints a wrong failure
count without persisting it is invisible here — **R388 and R396 are exactly that case**, so they are
"no change to the record", not "no change at all".

## ⛔ Check #242
✓ *"four of the five predate the current line"* — **correct, and the first closing-line count in five
rounds to survive its own check.** ⛔ *"small enough to repair and verify in one round"* — the fifth
uncomputed cost claim.

## The sentence I can no longer write
> *"re-run those four and diff their failure counts."*

**Their counts are on disk.** Three of the four never recorded one, and the fourth recorded zero.

## NEXT
The repair is now fully scoped and provably inert against the record, so **install it** — one
predicate at five call sites — **and the verification is not a re-run but a re-read**: after editing,
the five artifacts must be **byte-identical** to what they are now. **A repair that is preventive
must leave the record untouched, and that is a testable claim rather than an assurance.**
