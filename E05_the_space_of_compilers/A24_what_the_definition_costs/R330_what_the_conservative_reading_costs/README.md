# R330 — budget-matching admits the baseline, at every reading

**Decision this makes safe:** whether clause ② may use a budget-matched reference at all.
**It may not.** At all five readings the admitted set contains **`generic`** — a criterion set that
is *identical on every prompt*, i.e. **a member of clause ②'s own reference class.** The rule R328
proposed and R329 bracketed fails everywhere, and not at the end I was testing.

## W-ADMITS-THE-BASELINE

| reading | U (bracketed) | admitted |
|---|---:|---|
| U = committed count (R328's lower bound) | 11 | `coval_core` · **`generic`** · `topw_k3` · `topw_k4` · `topw_k6` · `topw_k8` |
| U1 rules-used × k-used | 35 | `coval_core` · **`generic`** · `topw_k4` · `topw_k6` |
| U2 all k-rules × k-used | 56 | `coval_core` · **`generic`** · `topw_k4` · `topw_k6` |
| U3 all k-rules × k∈1..16 | 128 | `coval_core` · **`generic`** · `topw_k6` |
| U4 U3 + fit-parity variants | 256 | `coval_core` · **`generic`** · `topw_k6` |

**5 of 5 readings admit a prompt-blind arm.** This is not a property of the conservative end.

## Why it happens — and it is the rule working exactly as specified

Clause ② says *better than the same number that **never read the conversation at all***. `generic`
never reads it: **one criterion set, 968 prompts, mechanically detected.** R294's **fixed** reference
excluded it correctly by self-comparison — `c2 = +0.0009`, inside its own MDE.

**Budget-matching destroys that self-comparison.** `generic` is a singleton, so it draws the
*weakest* reference (best-of-1 ≈ a random k-subset) and clears it at +0.014. The rule rewards not
searching — **correct in multiple-comparison terms, and exactly the channel the baseline walks in
through.**

## Controls — and two of them found real defects before the verdict

| control | result |
|---|---|
| **positive** — reproduce R294's committed clause-② gap for all **37** clause-③-passing arms | **0.000e+00**, exact |
| **positive @ g=0** — the same check against a *wrong* same-size subset | correctly fails, 1.657e-02 |
| **population** — every arm's n must equal R294's | PASS · `[398, 968]` |
| **prompt-blind detector** — `generic`=True, `topw_k4`=False, `coval_core`=False | PASS, none undetermined |
| **negative** — 22 random/sham arms at U=1, the most permissive reference any arm gets | **0 admitted** |
| **sham (partition)** — an even-name-length classifier must disagree with the construction one | PASS, overlap 4 of 23 |
| **placebo** — every arm against itself | 0.0 |
| seeds | admitted set identical at 3 seeds |
| noise floor | 5 of 185 cells inside `[0.95, 1.05]` |

### ⚠ Three defects of mine, all caught by controls rather than by reading

**① The population was the intersection of 41 arms — 398 prompts, not 968.** `promptecho` and
`promptecho_sham` cover only 398 and dragged every other arm down with them. R294 evaluates each arm
on **its own** population. Caught by the 41-arm reproduction failing.

**② The reference was not size-matched.** R294 compares a k=6 arm to a **six**-subset of the generic
pool; I used quadruples for every arm. **This is `comparing arms of different k` — the error the
campaign has warned about since R287 — committed by me in the round that repaired it.** The
reproduction control localised it exactly: it failed for every arm with k≠4 and for none with k=4.
Fixed by building a size-matched pool per k (16 … 12,870 subsets).

**③ The kill had no branch for the outcome that occurred.** `W-SURVIVES` was defined as *"contains an
arm that is not the incumbent"* — which fired on `generic`. **That is not the same question**, and a
verdict string that cannot name the failure mode in front of it is prose. The prompt-blind detector
and `W-ADMITS-THE-BASELINE` were added afterwards, and the detector carries its own control.

And one typed sentence in the closing block asserted *"the incumbent is the only admitted
singleton"*, which the round's own output contradicts — `generic` is one too, and that **is** the
finding. Now computed.

## What this kills

**R328's budget-matching and R329's bracket both rest on a reference rule that admits the baseline.**
R328's `coval_core` 2.64× / `topw_k4` 1.38× and R329's straddle bracket are arithmetically intact but
**no longer license a clause-② statement**, because the rule producing them fails a test the fixed
reference passes.

**R294's fixed size-matched reference is not superseded.** It excludes `generic` by construction, and
that property is worth more than budget-matching's correction for selection.

## Scope

R294's 41 judged arms · 968 prompts (398 for `promptecho`) with ≥2 annotators · Qwen3.5-2B-Base under
R234's canonical builder · references: R294's first-k-of-pool, and best-of-U over the size-matched
pool for k ∈ {1,2,3,4,6,8,12,13,15} · 20 replicates × 3 seeds · 185 cells across 5 readings.

## What this cannot do

Say whether a *repaired* budget-matched rule exists — one that corrects for selection **and** keeps
the self-comparison that excludes the reference class. That is a design question, and this round
establishes only that the obvious rule is not it.
