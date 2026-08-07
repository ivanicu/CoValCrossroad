# R434 · on a second release the definition admits **no core at all** — `W-EMPTY`

**The decision this round makes safe:** whether R433's failure is about one generator or about the
definition's *shape*. **Neither, as it turns out.** Clause ② admits **0 of 7** criterion arms on the
second release, and **7 of 7** lose to a rule that reads nothing.

## ⛔ First: the announced next step was a category error, killed for zero compute

R433 closed with *"the definition needs a clause that excludes the length rule."* From the object:

> A **core** for a conversation is a small **set of evaluation criteria**, producible from the
> conversation alone, that ③ … and ② …

**The longest-reply rule is not a set of evaluation criteria — it is outside the domain.** The
definition never admitted it, so there is nothing to exclude. **Fourth round running whose announced
next step presumed its own conclusion, and the fourth time a three-line check killed it first.**

## The measurement

| arm | acc | vs blind (clause ②) | vs length (useful) |
|---|---|---|---|
| `gen` — prompt-specific | 0.4590 | +0.0093 vs MDE 0.0143 | **−0.0545** vs 0.0237 |
| `gen_sham` | 0.4540 | +0.0042 vs 0.0154 | **−0.0595** vs 0.0228 |
| `generic` — the blind reference | 0.4497 | +0.0000 *(itself)* | **−0.0637** vs 0.0238 |
| `randblind_s0` | 0.4501 | +0.0004 vs 0.0175 | **−0.0633** vs 0.0232 |
| `randblind_s1` | 0.4527 | +0.0030 vs 0.0195 | **−0.0607** vs 0.0223 |
| `randblind_s2` | 0.4500 | +0.0003 vs 0.0169 | **−0.0635** vs 0.0234 |
| `vacuous` | 0.4405 | −0.0093 vs 0.0146 | **−0.0730** vs 0.0247 |
| **`length` rule** | **0.5135** | *not a criterion set — outside the domain* | — |

> **SAT2 = 0 of 7 · USEFUL = 0 of 7.**
> **7 of 7 arms are statistically indistinguishable from the blind reference** — including the
> prompt-specific core. **7 of 7 are resolvedly worse than the length rule.**

**Population** 7,342 interactions / 2,200 conversations, the intersection of all seven arms ·
**instrument** Qwen3.5-2B-Base at k=4 · **baselines** `generic` for clause ②, longest-reply for
usefulness · **regime** n ∈ {2,3,4}, one release, no rubric.

⚠ The `randblind` accuracies here (0.4501 / 0.4527 / 0.4500) differ from R427's (0.4397 / 0.4396 /
0.4383) because **this is a different population** — the intersection with the two generated arms.
Same arms, same judge, different denominator; the numbers are not interchangeable and neither
supersedes the other.

## ⭐ The control that makes an emptiness mean something

**A zero from an instrument never shown to return non-zero is silence.** So a synthetic oracle arm
was run through the *same* membership tests:

| control | returned |
|---|---|
| **POSITIVE — oracle must land in BOTH sets** | vs blind **+0.5503** > MDE 0.0158 · vs length **+0.4865** > MDE 0.0169 ✅ |
| PLACEBO — an arm against itself | **0.0e+00** ✅ |
| g=0 — the blind arm cannot satisfy ② against itself | **False** ✅ |
| NEGATIVE — length hits permuted across conversations | point unmoved (**+0.5021**) — prices the *pairing*, not the membership |

**Both membership tests can return TRUE, by a wide margin. So `0 of 7` is a measurement.**

## What this is, and what it is not

- **It is:** on a second release, *every* criterion set this campaign has built — prompt-specific,
  prompt-blind, randomly reassigned, and evaluatively empty — is indistinguishable from the blind
  reference and resolvedly worse than a heuristic that reads nothing. **The clause is not lax here;
  it is empty.**
- **It is not:** evidence that no core exists. **7 arms is a census of what this campaign built**,
  not a sample of criterion-space, and R432's oracle over five of them reaches **0.7220** — so the
  ceiling sits far above every arm here.
- **The SAT2→USEFUL relation is UNVERIFIED**, and honestly so: with an empty SAT2 the relation has
  no referent. The round reports the two membership tests instead of pretending the relation
  resolved.

## The structural point, which no measurement was needed for

| clause | what kind of thing it is |
|---|---|
| ③ | a **provenance** restriction — where criteria may not come from |
| ② | a **comparative** test — against another criterion *set* |
| size | a **bound** — greater than one; 3–8 indistinguishable |

**Every clause compares a core to other criteria. None requires it to beat anything outside its own
family.** A sufficiency clause would have to be stated against a **non-criterion reference**, which
is a different *kind* of clause from anything the definition now contains.

## Impossible here, named

- **that no core can be useful** — requires generating and scoring far more than 7.
- **a clause excluding the length rule** — a category error; it is outside the domain.
- **construct validity of `chosen`** — the release's own human choice; no external gold standard.
- **cross-model** — one judge. Requires a second scored on the same responses.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
