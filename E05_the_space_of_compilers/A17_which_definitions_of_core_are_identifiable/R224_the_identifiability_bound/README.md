# R224 — which definitions of "core" this release can identify

**Arc E05·A04.** `realstat` G1: **estimand before method, identification before power.** Asking for
power on an unidentified quantity is how a well-powered-looking round gets built. So: before
proposing any definition of `core`, is it identifiable here?

## The derivation

A definition of the form *"the k-subset of n criteria that best preserves the decision"* ranges over
`C(n,k)` hypotheses and needs `log₂ C(n,k)` bits. The release offers, per prompt, an ordering over
`m` candidate responses — at most `log₂ a(m)` bits, where `a(m)` is the ordered Bell number.

> ⚠ **Adding raters does not raise `H_have`.** Every rater orders the *same* `m` responses. Their
> disagreement is information about **raters**, not about which criteria are right. There is one
> consensus ordering per prompt. R raters buy precision on a 6-bit object, never a 60-bit one.

**Identifiable ⟺ `log₂ C(n,k) ≤ log₂ a(m)`.**

At the release's own numbers — median `n=15`, `k=4`, `m=4`:

```
H_need = log₂ C(15,4) = log₂ 1365 = 10.41 bits
H_have = log₂ a(4)    = log₂ 75   =  6.23 bits
deficit 4.19 bits  →  18× more hypotheses than the observable can separate
```

**This is a DERIVATION, labelled as one** — it could not have come out otherwise. It independently
predicts R221's *measurement* that 100% of prompts admit a single criterion reproducing the whole
ranking, median 3 tied. The bound says that had to happen.

## Per prompt, and the design number it yields

| | |
|---|---|
| identifiable at `m=4`, ties allowed | **8.2%** of 986 prompts |
| identifiable at `m=4`, strict orderings | **1.8%** |
| candidate-set size required | median **6**, p90 **7**, max **8** |

| `m` | share identifiable |
|---:|---:|
| 4 (the release) | 8.2% |
| 5 | 31.2% |
| **6** | **78.6%** |
| 7 | 99.7% |
| 8 | 100.0% |

R220 and R223 both ended on "more candidates per prompt". It is now **six**, and seven for
near-complete coverage.

## Which definitions survive

| definition | H_need | H_have | verdict |
|---|---:|---:|---|
| minimal k-subset preserving the source's **decision** | 10.41 | 6.23 | **NOT IDENTIFIED** — the definition E05 was built on |
| the k-subset maximising **human agreement** | 10.41 | 6.23 | **NOT IDENTIFIED** — same space, same observable |
| the k **highest-rated** criteria | 0.00 | 6.23 | IDENTIFIED — a function of the ratings; no inference |
| a **typed policy + certificate** naming its query family | 0.00 | 6.23 | IDENTIFIED — the estimand is observed, not inferred |

## The formulation

> **A core is not a compression of the rubric. It is a pair `(policy, certificate)`, where the
> certificate names a query family `Q`, and the policy is admissible only if
> `log₂|H(Q)| ≤ log₂ a(m)` — the hypothesis space the sufficiency question ranges over is no larger
> than the candidate orderings the source data can distinguish.**

The inequality is what makes the definition **failable**, which is the point: a definition of
`core` that cannot be shown unidentifiable on *some* dataset is not a definition, it is a name. On
this release the decision-preserving definition fails it at 91.8% of prompts — **a fact about the
release's design, not about any compiler.**

## What this does not do

It bounds identifiability from **information content only**. It says nothing about whether a
identifiable estimand is *worth* identifying, and it assumes the observable is the ordering. A
richer observable per prompt (graded scores, pairwise confidence, per-criterion satisfaction —
which the release does **not** ship) would raise `H_have` without adding candidates.
