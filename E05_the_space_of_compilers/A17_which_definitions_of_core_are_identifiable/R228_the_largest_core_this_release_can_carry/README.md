# R228 — the largest core this release can carry

**Arc E05·A17.** R224–R227 all held `H_need = log₂C(n,k)` fixed and asked what could raise `H_have`.
But **`k` is a choice** — it belongs to the *definition* of core, not to the data — and the same
inequality solves for it.

## (a) The derivation

```
k_max(n, m) = max { k : C(n,k) ≤ a(m) }
```

At the release's median prompt, `n = 14`, `m = 4`, `a(4) = 75`:

```
C(14,1) =  14  ≤ 75   identifiable
C(14,2) =  91  >  75   NOT identifiable
```

| derived `k_max` | prompts | share |
|---:|---:|---:|
| **1** | 303 | **66.4%** |
| 2 | 112 | 24.6% |
| 4 | 3 | 0.7% |
| 6–8 | 38 | 8.3% |

## (b) The measurement — recovery of a planted subset, ranking observable

At `eps = 0.25`, R227's calibration to the release's own 47.8% human–human agreement:

| k | recovery | chance | excess | seed spread | |
|---:|---:|---:|---:|---:|---|
| **1** | 0.2462 | 0.0870 | **+0.1592** | 0.0594 | **above chance** |
| **2** | 0.0537 | 0.0182 | **+0.0355** | 0.0258 | **above chance** |
| 3 | 0.0154 | 0.0072 | +0.0082 | 0.0096 | inside |
| **4** | 0.0121 | 0.0053 | **+0.0068** | 0.0084 | **inside** |

**Empirical `k_max` = 2.**

### Controls

⚠ The first positive control demanded recovery > 0.9 at `eps = 0` and got **0.7269**, reading
"instrument broken". The instrument was fine; **the threshold was unreachable by construction.** At
zero noise recovery is exactly `E[1/|ties|]`, and ties are the very phenomenon under study — R221
measured a median of 3 subsets producing an identical ranking. Demanding > 0.9 demanded the
degeneracy not exist. **Third control-that-cannot-pass in this arc**, after R221 and R225.

The assertion that *can* fail is about the **matcher**: at zero noise the planted subset must always
be among the exact-distance hits. It is, at **1.0000**. Ceilings `E[1/ties]` are 0.7269 / 0.1951 /
0.0738 / 0.0373 for k = 1…4, and each cell achieves its ceiling exactly. Negative control: chance
recomputed per prompt at every k, never assumed.

## Reconciling 1 and 2 — they are bounds on different problems

The derivation asks how many bits distinguish `C(n,k)` hypotheses **with no side information**. The
measurement gives the analyst `W` and `S`, so the *effective* hypothesis space is smaller than
`C(n,k)` — many subsets produce indistinguishable scores and collapse together. That is why
measurement (2) can exceed the capacity bound (1) without contradiction, and it is why both belong
in the report.

**Both say the same thing about the number that matters: far below four.**

## What this says about the official core

> The official core has **four** criteria. At `k = 4` the recovery excess is **+0.0068 against a
> seed spread of 0.0084** — inside the floor. **Three of its four criteria are not recoverable from
> this release.**

They are a **choice**, and a defensible one — readability, coverage, the dataset card's own stated
purpose of a short readable summary. **They are not a measurement**, and nothing in the release makes
them one. This is reached from the inequality, not by attacking anyone's compiler.

## The formulation, now with a number in it

> A core is `(policy, certificate)`, admissible only if `log₂|H(Q)| ≤ H_have`. **On this release
> that resolves to `k ≤ 2`, and every criterion beyond the second is a declared editorial choice
> rather than an identified quantity — which the certificate must say.**

## The sentence that can no longer be written

*"The compiler selected four criteria."* It selected two it could have identified and two it could
not, and nothing in the artifact distinguishes them.

## Register

Whether a `k ≤ 2` core is **useful** is not tested here. Identifiability is not utility, and this
site cannot measure utility — that needs a downstream task the release does not carry.
