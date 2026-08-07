# R669 · `P_arm` is not clause ② — and I restricted the pool one round after catching that error

**Decision this makes safe:** whether R668's level-set result says anything about clause ②. **No.
It holds inside the `topw` family only, and it was measured against a different quantity.**

## The contradiction, in one table

| | |
|---|---|
| arms in R353's map | **41** |
| in `clause2_admits` | **9** — coval_core, greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1, topw_k3/k4/k6/k8 |
| at `P_arm = 0` at every seed | **32** |
| ⭐ **BOTH** | **4** — `greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1` |

| seed | min(P \| admitted) | max(P \| rejected) | level set |
|---|---:|---:|---|
| 3531 | **0.0000** | 0.8000 | **False** |
| 3532 | **0.0000** | 0.7575 | **False** |

## ⛔⛔⛔ Three things fall

**① "Something disqualifies k=12 categorically" — RETRACTED.** **32 arms score exactly 0**, spanning
**k = 2, 3, 4, 6, 8, 12**, including every `random_k*`, every sham, `topabs_k4`, `topvar_k4`,
`topwvar_k4`, `full`, `promptecho`. **Zero is the MODAL value.** *I read the default as an event.*

**② R668's level set fails globally.** It holds within `topw` — the negative control confirms that,
so R668 was not *wrong locally* — but `clause2_admits` contains **four arms at `P_arm = 0`**.
⛔ **The same pool-restriction error R667 caught in R665, committed by me one round later.**

**③ And the deeper defect: `P_arm` is not clause ②.** It is R353's probability that an arm survives
a random **pool order**. **I tested the k-band against a different quantity and reported the fit as
though ② produced it.**

## Controls

| control | returned |
|---|---|
| **positive** — arms both in `clause2_admits` and at `P_arm = 0` | **4 found** — PASS, *the contradiction exists* |
| **negative** — the inequality must still hold within `topw` | **True** — PASS, *so this is a SCOPE failure, not a wrong result* |
| **placebo** — an arm in neither set | **PASS** |

**MULTIPLICITY:** 2 seeds × 41 arms + 3 controls; **the 32-arm zero-set printed in full**, because
the whole point is that zero is modal.

**IMPOSSIBLE, named:** **what clause ② actually thresholds is NOT settled here.** Finding it needs
②'s own per-arm statistic, and **this round explicitly does not claim to have located it** — which is
the discipline the previous four rounds kept failing.

## The sentence I can no longer write

> *"the k-band is a level set of the admission profile, so ② already says it."*

**It is a level set of a different statistic, inside one family of arms.**

## What actually stands after R664–R669

| **STANDS** | |
|---|---|
| ② is a predicate on **(object, baseline)** pairs — the extension moves with the baseline | R664, from R527 |
| `② ∧ ③` = **5 arms**: coval_core + topw_k3/k4/k6/k8 | R667, from R360 ≡ R442 |
| p100 **is** the in-sample ceiling | R666, from R328 |

| **WITHDRAWN** | |
|---|---|
| "the definition admits exactly two objects" | R667 |
| "empty at its literal reading — could have come out otherwise" | R666 |
| "an unstated band is a clause nobody wrote" | R668 |
| "the k-band is a level set of ②" | **this round** |
| "something disqualifies k=12 categorically" | **this round** |

## NEXT

**Every retraction in R665–R669 has the same shape: I reached for the nearest committed number and
treated it as the quantity my sentence was about.** `P_arm` for ②'s admission; R527's curve for the
full extension; the in-sample ceiling for a baseline. **The gate that would have caught all four is
not prior-art — it is `instrument unit == claim unit`, which every one of these rounds printed in its
own docstring and none enforced.** **Make it executable**: a round must name the artifact field it
reads and the claim it supports, and fail if the field's own round defined it as a different
quantity. That is a gate, not a resolution — and it is the first repair in this arc aimed at the
error class rather than at an instance of it.
