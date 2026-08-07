# R776 · the arm-free covariate refutes my own hypothesis, and my block labelling was wrong

**Six disjoint families, 15 pairs. ⭐ The first quantity in this thread that no arm participates in —
`poolspread(p)`, the spread of the 16 fixed pool criteria on a prompt — correlates with the families'
scales at **−0.049 to −0.178**: **0 of 6** above 0.30, **5 of 6** below 0.15, against a sham band of
**[−0.064, +0.059]**. **WORLD B — rule artifact.** The prompt-property reading I argued for in D2 is
refuted by the instrument built to test it. ⚠ And the registered axis test returns **p = 0.2000**
because **my block labelling was wrong**: `M_mixed_sel` holds **3 of 5** `random_k` arms, so every
M×R pair I called "diff-rule" is majority same-rule.**

## check #378 — two corrections before designing, one of them to my own arithmetic

**①** R775's NEXT claimed *"2⁶ − 2 = 62 labelings"*. That counts **bipartitions**; the axis test labels
each family by its **rule**, so with six families of which three share one the count is **C(6,3) =
20** and the p floor is **0.05**, not 1/62. The improvement over R775's 1/4 is real (5×) and smaller
than I claimed *(ledger 1109)*.

**②** And R775's reading may have been backwards, which is why this round was built: `random_k` arms
draw criteria **at random**, so two random families with different seeds hold **different** criteria —
yet their difference magnitudes would still co-move wherever the **pool** is heterogeneous, which is a
**prompt** property. **D2 argued the same-rule block is the strongest evidence FOR a prompt
component.** The round was designed to test that, and it fails.

## ⭐ E3 · the arm-free covariate — and it says no

`poolspread(p)` involves **no arm, no selection rule and no difference vector**.

| family | corr(scale, poolspread) | with poolmean | partial |
|---|---|---|---|
| `F1_committed` | **−0.1782** | +0.0250 | −0.1861 |
| `F3_target` | −0.0914 | −0.0248 | −0.1139 |
| `Rb_random_s1` | −0.0767 | +0.1244 | −0.0248 |
| `M_mixed_sel` | −0.0688 | +0.0703 | −0.0423 |
| `Rc_random_s2` | −0.0664 | +0.1016 | −0.0244 |
| `Ra_random_s0` | −0.0490 | +0.1138 | +0.0010 |

**0 of 6 ≥ 0.30 · 5 of 6 < 0.15**, against a **SHAM** of **−0.0005 [−0.0644, +0.0591]** (a random
draw from `poolspread`'s own distribution). ⇒ **the pool's per-prompt criterion spread does not
explain the scale**, and D2's mechanism is refuted *(ledger 1110)*.

⚠ **D3 bounds the claim**: `poolspread` and the scales read the same satisfaction table, so this tests
*"is the scale a function of the pool's spread"*, not *"is it a prompt property in some judge-free
sense"*. The saturation axis is real — corr(poolspread, poolmean) = **−0.4387** — and the partials
barely move, so saturation is not the story either.

## ⛔ E2 · the registered axis test, and why its answer is uninformative

| | mean relative correlation |
|---|---|
| SAME-RULE (3 pure-`random_k` pairs) | **0.6279** |
| "diff-rule" (12 pairs, **as registered**) | **0.2677** |
| difference | **+0.3602**, rank **4/20**, **p = 0.2000** (floor 0.0500) |

⚠ **The labelling was wrong and it is a composition fact I could have checked first.**
`M_mixed_sel` = `random_k4_s0/s1/s2, topabs_k4, topvar_k4` — **3 of its 5 members are `random_k`**, so
`Ra×M = 0.7151`, `Rb×M = 0.7033`, `Rc×M = 0.7018` are majority-same-rule pairs sitting in the
"diff-rule" block and pulling its mean from 0.14 to 0.27 *(ledger 1111)*.

**Post-hoc, and labelled post-hoc:** pure-random pairs **0.6279** (n=3) against pairs containing **no**
pure-random family **0.1406** (n=3) — a **4.5×** gap. That is the cleaner comparison and it is *not*
the registered one, so it is reported as a separate quantity rather than substituted for it.

## the 15 pairs

| block | pairs | relative |
|---|---|---|
| pure-random × pure-random | Ra×Rb, Ra×Rc, Rb×Rc | **0.6283 · 0.6386 · 0.6168** |
| pure-random × mixed *(3/5 random)* | Ra×M, Rb×M, Rc×M | **0.7151 · 0.7033 · 0.7018** |
| pure-random × committed | Ra×F1, Rb×F1, Rc×F1 | 0.1995 · 0.2578 · 0.2224 |
| committed × mixed | F1×M | 0.2835 |
| committed × target | F1×F3 | 0.1519 |
| target × anything | F3×Ra/Rb/Rc/M | −0.0023 · 0.0033 · −0.0103 · −0.0137 |

## controls — 5 PASS after one repair

| control | returned |
|---|---|
| **DISJOINT** | 6 × 5 arms, **0** shared objects under R730; exit 2 otherwise |
| **POSITIVE** | planted prompt-scale: width 0.25 → min **+0.2866**, covariate **0.5806** · 0.50 → **+0.5792**, **0.7962** · 1.00 → **+0.7814**, **0.9106**. Monotone, all 15 detected from 0.25 |
| **g=0** | width 0 → min −0.0359, **not** all detected |
| **NEGATIVE** | 200 one-sided permutations → **+0.0058 [−0.0607, +0.0651]** |
| **SHAM** | scale vs a random draw from `poolspread`'s own distribution → **−0.0005 [−0.0644, +0.0591]** |
| **PLACEBO** | a family against itself → **1.000000** |

⛔ **The g=0 control could not pass as first written.** At width 0 the planted scale is a constant
vector, so `corr(scale, constant)` divides by a zero sd and is **NaN — undefined, not zero** — and my
criterion required it below 0.15. NaN fails every comparison. Repaired: the covariate clause applies
only where a covariate **exists**, and the width-0 cell prints `undefined (no plant)`
*(ledger 1112)*.

## what this changes in the deliverable

| carried | stands as |
|---|---|
| D2's hypothesis — the random families' agreement is a **prompt** property | ⛔ **refuted by the arm-free covariate**: 0 of 6 families reach 0.30, 5 of 6 sit below 0.15 |
| R775's rule gradient | **strengthened, and by a cleaner contrast**: pure-random pairs **0.6279** against no-pure-random pairs **0.1406** |
| the registered axis p | **0.2000**, and **uninformative** — the blocks were mislabelled by a composition fact |
| *"which prompts separate cores"* | **has no answer via criterion spread**; whatever the co-movement is, the pool's own per-prompt heterogeneity is not it |

## the sentence I can no longer write

*"the random families co-move because the pool is heterogeneous on some prompts."* The pool's spread
correlates with every family's scale at under 0.18, and with five of six at under 0.15.

## NEXT

The one comparison that would separate *rule* from *arm-set* has not been run and is available: the
three pure-random families differ **only in seed**, so their **0.6279** is what identical rules on
different draws buy. But `M_mixed_sel` reaches **0.70+** with each of them while containing only
**three** random arms — **higher than the pure-random block** — which no rule story predicts and which
the composition table makes visible rather than explains. ⚠ The obvious reading is that `M`'s three
`random_k4` members are *the same k* as nothing else in the design, so k may be the shared axis rather
than the rule. The registered quantity is the cross-family correlation as a function of **k-overlap**
between two families, holding rule fixed — because if k explains it, then every "rule" result in
R775 and here is a k result wearing a rule's name.
