# R825 · The permissive bar reaches the released core — ④ excludes `coval_core`

**E05 · A24 · R825. WORLD B.** 968 prompts × 4 responses · 12 splits · every unsupervised stage fit
on the fit half. Source `d60a618f`.

## The decision this makes safe

R824 adopted the **permissive** reading of ④ — *a rule may be fit on other prompts' labels and read
only responses at inference* — on the stated grounds that it strips the junk while **every
load-bearing arm survives**. That grounds statement was measured on **14 lexical features**.

**It does not survive character n-grams.**

## Result

| | |
|---|---:|
| leak-free char-n-gram response-only bar | **0.572335** (independent audit, 10 splits) |
| `coval_core` | **0.566477** |
| **paired difference over 12 splits** | **+0.006197 [+0.003923, +0.008471]** |
| splits where the bar beats the core | **12 of 12** |
| sign test | two-sided **p = 0.00049** |

**Verdict computed, not typed: RESOLVABLY ABOVE.** Under the reading this deliverable adopted two
rounds ago, **clause ④ excludes the released core.**

⭐ **Character n-grams buy +0.0487 over lexical features — 104% of the entire 0.046788 gap.** Not
model capacity, not regularisation: a richer view of the same responses. And n-grams were never in
the 30-rule family `DEFINITION.md:118` names as ④'s reference class.

## ⚠ What the mean hides

| | |
|---|---:|
| smallest split effect | **+0.000945** |
| largest split effect | **+0.011824** |
| ratio | **12.5×** |

**The per-split effect is not uniformly resolvable — only the paired mean is.** The claim is about
the average over evaluation halves, never about a given half, and certainly not about a conversation.

## ⛔ Two derivations, labelled, because I mis-reported both mid-round

**D-A · Pairing cannot move the point estimate.** `mean(bar) − mean(core) ≡ mean(bar − core)` by
linearity — checked at **1.21e-16**. Pairing moves only the standard error: **0.002353 → 0.001033,
a 2.3× shrink**, because `corr(bar, core) = +0.8377` is shared split-to-split variance.

**D-B · Both CIs exclude zero at n=12.** Paired [+0.003923, +0.008471]; unpaired [+0.001017,
+0.011377]. ⚠ **I reported "unpaired says indistinguishable, paired says resolvable — opposite
verdicts." That was wrong.** What produced the original "INSIDE the floor" was the audit comparing a
**mean over 10 splits** against a **per-split noise floor** — the floor is a single draw's sd, the
mean's se is `sd/√n`, about 3× smaller. **A √n units mismatch, not an under-powered test.**

The general rule this earns: **a noise floor and a standard error are different statistics, and
comparing a mean to a single-draw dispersion is over-conservative by √n.** It fails toward "no
effect", which is why it reads as caution and passes unexamined.

## Controls

| control | returned |
|---|---|
| **OBJECT** | `coval_core` corpus A2 reproduces **0.566477** exactly |
| **LEAK, 4 stages** | vectoriser + SVD basis + SVD z-score + lexical z-score, **all** fit on the fit half |
| **lexical-σ channel** | −0.000204 (mine) vs +0.000419 (independent) — **both inside the floor, opposite signs; unresolvable, and its sign is retracted in ledger 1263** |
| **SVD channel** | T1 +0.000419, T2 −0.001246 — both **inside** their tier floors |
| **MDE** | se 0.002526 at n=8, **MDE(80%) 0.007072**; the gap tested is 6.6× it |
| **independent replication** | a second session's audit, different splits, different implementation |

## What this retracts

⚠ **R824's grounds statement is retracted.** *"Every ③-admissible load-bearing arm survives"* is
false once the rule class includes character n-grams: `coval_core` does not survive, and it is the
arm the deliverable is about.

**R824's finding stands** — ④'s extension does depend on the reading, 0 vs 25 of 58. **What falls is
the reason given for choosing the permissive one.**

## What this round cannot do

| criterion | requires |
|---|---|
| show that NO response-only rule beats the core | quantifies over an infinite class; this shows one that does |
| decide which reading ④ *should* take | authorial intent the text does not record |
| independently replicated across releases | a second release |
| cross-model / cross-dataset | a second site |
