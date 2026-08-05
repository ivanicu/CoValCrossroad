# R597 · The allowance fires exactly once, correctly bound — and my own filter would have said zero

**Decision this makes safe:** the repaired gate can stay as it is. **Its unsound direction is real
and reachable, and `STATEMENT.md` does not exercise it.** A scope, not a repair.

| layer | count |
|---|---|
| **L0** paragraphs with ≥1 citation | 50 |
| **L1** + contains the token `UNVERIFIED` | 3 |
| **L2** + cites ≥2 rounds — **R596's filter** | **0** |
| **L3** + ≥1 cited round *is* unverified — **where the rule fires** | **1** |

⛔ **R596's closing line was wrong in both directions at once.** It called L2 *"the exact size of the
population where the new rule is unsound"*:
- **a SUPERSET** — the rule only fires when a cited round actually *is* unverified;
- **and simultaneously a SUBSET, which is the worse half** — unsoundness does **not** require multiple
  citations. A paragraph citing **one** round can contain the word for an unrelated reason and allow
  it by accident.

⭐ **L2 = 0 while L3 = 1. My own filter would have reported the population as empty when the one real
case exists.** I narrowed by a **proxy** (citation count) for a **property** (marker intent) — the
same error class as the previous seventeen, committed *inside the correction to one of them.*

## The single member, and it is sound
> **para 41: cites [501], unverified [501] → BOUND** — one citation, so the marker can only be about
> the round it allows.

## Reachability, by exit code rather than by argument
| plant | expected | exit |
|---|---|---|
| R507 unverified · paragraph's `UNVERIFIED` refers to a **different** round | the hole | **0 — ALLOWED** *(both runs)* |
| R507 unverified · paragraph has **no** marker | must be stopped | **1** |
| R507 normal verdict `B` | must be allowed | **0** |

**The unsound direction is REACHABLE and UNEXERCISED.** Those are different facts and the round
reports them separately.

## ⚠ A measured zero, made admissible
The first inspection returned **0**, which is exactly when P5's ★ rule applies. The counter was
pointed at corpora where the answer should be positive:

| corpus | L0 | L1 | L2 | **L3** |
|---|---|---|---|---|
| `DEFINITION.md` | 135 | 9 | 1 | **2** |
| `FORMULATION.md` | 80 | 2 | 2 | **2** |
| round READMEs | 141 | 6 | 3 | **5** |

**The counter returns non-zero.** Only then is `STATEMENT.md`'s L2 = 0 a measurement rather than
silence. Further controls: empty document → `(0,0,0,0)` · synthetic doc citing rounds with no token →
L1 = 0 · placebo token `ZZQ` over the real statement → L1 = 0.

## ⛔ And my verdict label fired on a condition its own pre-registration does not name
v1 printed **`B LIVE`** on `len(L3) > 0`. **World B was pre-registered as *"a round is being allowed
by a word that was not about it"*** — which requires an **accidental** marker, not merely that the
allowance fires. Every L3 member is BOUND, so B is false and the branch was asserting something the
round had not established.

⭐ **Same row as R593's non-partition `elif`, one arc later: a label fired on a condition its own
definition does not name.** The states are now separated, and the correct verdict is a fourth one —
**D FIRES ONCE, CORRECTLY BOUND.**

## IMPOSSIBLE, named
*"The marker was about **this** round"* is **intent, not string.** A single-citation paragraph is
**BOUND by construction**; everything else is reported **UNDECIDABLE**, never asserted to be
accidental. Deciding it would need the author or an external reader.

## The sentence I can no longer write
> *"the size of the unsound population is the number of paragraphs citing several rounds alongside
> the word."*

That number is **0** and the true count is **1** — my filter excluded the only case there is.

## NEXT
The three positive-control corpora carry **L3 = 2, 2 and 5** — nine paragraphs outside `STATEMENT.md`
where an unverified round is cited alongside the token. **None of them is gated by anything**:
`statement_provenance.py` reads `STATEMENT.md` alone. **Check whether `DEFINITION.md` and
`FORMULATION.md` are gated by any assurance script at all** — R566 found no gate reads `FORMULATION.md`,
and whether that is still true after six rounds of gate work is a `grep` over the suite, not a judgement.
