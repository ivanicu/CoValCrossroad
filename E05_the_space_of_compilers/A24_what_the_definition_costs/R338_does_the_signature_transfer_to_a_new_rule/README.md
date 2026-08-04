# R338 — the signature does not reach a second leak mechanism, and the round can say why

**Decision this makes safe:** whether R337's AUC 0.866 licenses a general clause-③ test.
**It does not** — but the reason is not the one I pre-registered. **W-BLIND.**

## The numbers

| | AUC |
|---|---:|
| **transfer** — R337-trained classifier → R335's manufactured mechanism | **0.510** |
| **trained ON the manufactured mechanism**, held-out seeds | **0.565** (0.565 · 0.558 · 0.573) |
| R337's held-out-arm, for contrast | 0.866 |

**Score by dose is flat**: `0.00 → −2.57 · 0.10 → −2.55 · 0.25 → −2.49 · 0.50 → −2.53 · 0.75 →
−2.52 · 1.00 → −2.58`. No dose response at all.

## ⚠ Why the transfer number is UNREADABLE — and why that was worth building

I designed this round to separate two worlds:

- **W-LEAKAGE** — the features detect label-driven selection as such
- **W-RULE** — they detect *those four rules*, and would miss any other route

**Neither applies.** Trained *on* the manufactured mechanism the features reach only **0.565**, so
they cannot see that mechanism at all. **A transfer failure against a mechanism your features are
blind to is silence, not evidence** — and without the trained-on-manufactured control I would have
reported W-RULE, which the data does not support.

## What IS established

**Two leak mechanisms. One visible in these features (0.866), one not (0.565).** So the signature is
**mechanism-specific**, which is most of what W-RULE would have claimed — reached honestly, and
without asserting that R337's 0.866 was *only* rule-detection.

**R337 stands for the page's rule family and does not generalise beyond it.**

## Controls

| control | result |
|---|---|
| **negative** — shuffle **dose** labels among manufactured arms | **0.499** |
| **placebo** — dose-0 arms scored against each other | 0.478 |
| **positive @ g=0** — two dose-0 arms differing *only* by draw, split by prompt | **0.463**, indistinguishable |
| **sham** — the `k` feature, excluded and reported | 0.510 with, 0.510 without |

The **sham** matters: manufactured arms are all k=4 while the page's span k=1..15, so a k-tracking
feature would transfer for a reason unrelated to leakage. Excluding it changes nothing, which makes
the exclusion **checkable rather than trusted**.

### ⚠ And the g=0 control was malformed first

v1 held out one seed's dose-0 rows and asked for `seed == SEEDS[0]` — **every row in a held-out fold
shares that seed, so the test label is constant and AUC is `nan`.** It returned neither pass nor
fail. Fixed by putting both classes in the test set, split by prompt.

## The sentence I can no longer write

> *"a label-free selection signature exists and transfers"* — it transfers across **arms of one
> family**, and reaches a second mechanism at chance.

## Scope

R294's 40 arms with a committed core json (4 annotated leaky) · **398 prompts** in the intersection
· 18 manufactured arms at 6 doses × 3 seeds · features from the rubric and judge satisfaction only ·
2 feature sets × 2 training populations × 3 seeds.

## What this cannot do

Test a second leak mechanism **from the release itself**. The release annotates one family; the
second mechanism here is manufactured, so *"generalises to any leak"* stays out of reach and only
*"generalises beyond one family"* was testable — and it is answered in the negative for the one
alternative that could be built.
