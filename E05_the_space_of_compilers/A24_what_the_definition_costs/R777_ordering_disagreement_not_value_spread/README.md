# R777 · the second arm-free candidate dies too, and a *forced* prediction failed

**`orderdisagree(p)` — the mean pairwise disagreement of the 16 pool criteria's induced sign vectors,
with no arm, no selection and no difference — correlates with the six families' scales at **+0.07 to
+0.22**: **0 of 4** random-containing families reach 0.30, **5 of 6** sit below 0.15, and conditioning
on it drops the M×R co-movement by **0.4–0.7%**. **WORLD B.** ⭐⭐ And D3's *forced* prediction failed:
the same mechanism recovers **+0.55 to +0.65** in a synthetic pool where it is the only signal, so the
real arms show **6.5× less** of an effect that is supposed to be algebraic.**

## check #379 — k died on the composition table, without a measurement

| | k-set | k-overlap with M *(k = {4})* | relative correlation |
|---|---|---|---|
| `Ra/Rb/Rc` | {2, 3, 6, 8, 12} | **0.000** | **+0.7151 / +0.7033 / +0.7018** ← highest |
| `F3_target` | {4} | **1.000** | **−0.0137** ← lowest |

`corr(k-overlap, relative)` over the 15 pairs = **+0.1620**, with its two extremes **inverted**.
**R776's registered NEXT closes before this round begins** *(ledger 1113)*.

**What the ordering does track**: the top six pairs are exactly the six among `{Ra, Rb, Rc, M}` — the
four families containing `random_k` arms. And R776's mechanism was right in spirit, wrong in
statistic: two random draws differ where the pool's criteria **induce different orderings**, not where
their satisfaction **values** are spread.

## ⭐ D2, reported first as registered — the two covariates are genuinely different

**corr(orderdisagree, poolspread) = −0.5901** — different quantities, and *negatively* related: more
ordering disagreement goes with **less** value spread. So World C ("R776 relabelled") is excluded and
this round is a real second attempt *(ledger 1114)*.

## ⭐⭐ E2 — and the sign of the gap is backwards

| family | random? | corr(scale, orderdisagree) | partial (tie share) |
|---|---|---|---|
| `F1_committed` | — | **+0.2182** | +0.1755 |
| `F3_target` | — | **+0.1461** | +0.1089 |
| `Rb_random_s1` | RANDOM | +0.0994 | +0.0550 |
| `Rc_random_s2` | RANDOM | +0.0961 | +0.0236 |
| `M_mixed_sel` | RANDOM | +0.0956 | +0.0677 |
| `Ra_random_s0` | RANDOM | +0.0699 | +0.0385 |

**random-containing mean |corr| 0.0902 · others 0.1821 · gap −0.0919.** The **non-random** families
correlate *more* — the opposite of what D3 derived. **5 of 6 below 0.15 → WORLD B.**

## ⭐⭐⭐ D3 was a derivation and it failed, which is the round's real content

D3, written before the run: *"a random draw's expected |d| rises with ordering disagreement **by
construction** — if all 16 criteria induce one ordering, any two draws agree and |d| = 0 whatever k
is."* The POSITIVE control builds exactly that world and the mechanism fires:

| synthetic disagreement width | mean disagreement | recovered corr |
|---|---|---|
| 0.00 | 0.0000 | **UNDEFINED** *(every draw identical — printed as undefined, not as a small number)* |
| 0.25 | 0.1082 | **+0.6260** |
| 0.50 | 0.2037 | **+0.6503** |
| 1.00 | 0.3308 | +0.5465 |

**The mechanism recovers 6.5× more in simulation than the real `random_k` arms show** (0.65 vs 0.099).
⇒ **A relation I derived as algebraically forced is almost absent in the data it was derived about.**
The forcing argument is not wrong — the synthetic world proves it — so the real arms must be
constrained in some way the model omits *(ledger 1115)*.

⚠ **And the plant is not monotone at the top**: 0.6503 → 0.5465 from width 0.50 to 1.00, because at
high disagreement every prompt disagrees and the between-prompt variance the correlation needs
collapses. Registered band was 0-vs-1.0 and passed; the non-monotonicity is reported rather than
smoothed.

## ⛔ E3 — conditioning changes nothing

| pair | raw | holding `orderdisagree` fixed | drop |
|---|---|---|---|
| `Ra` × `M` | +0.6017 | +0.5992 | **0.4%** |
| `Rb` × `M` | +0.5917 | +0.5878 | **0.7%** |
| `Rc` × `M` | +0.5895 | +0.5857 | **0.6%** |

**The 0.59 co-movement is untouched.** Whatever generates it, the pool's ordering disagreement is not
a component of it.

## controls — 5 PASS

| control | returned |
|---|---|
| **POSITIVE** | synthetic sweep, detected at every non-degenerate width, **+0.5465 to +0.6503** |
| **g=0** | zero disagreement → correlation **UNDEFINED**, printed as such rather than as a number — the defect R776 caught in its own g=0 cell one round ago, avoided here by registering it |
| **NEGATIVE** | 200 permutations of the covariate → **+0.0011 [−0.0604, +0.0674]** |
| **SHAM** | a random draw from `orderdisagree`'s own distribution → **+0.0033 [−0.0657, +0.0662]** |
| **PLACEBO** | a family against itself → **1.000000** |
| **CONFOUND** *(registered)* | **corr(orderdisagree, tieshare) = +0.7392** — the tie axis is strong, and the partials shrink every correlation (F1 0.2182 → 0.1755), so part of even the small effect is tie structure |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| R776's NEXT — k-overlap as the axis | ⛔ **dead by derivation**: the k-identical pair is the lowest and a zero-overlap pair the highest |
| *"ordering disagreement explains the random families' co-movement"* | ⛔ **refuted** — 0.07–0.10 against a 0.65 synthetic recovery, and conditioning drops M×R by under 1% |
| the arm-free-covariate programme | **two candidates dead** — value spread (R776) and ordering disagreement (here). The register gains: *no pool statistic tried explains the co-movement* |
| a derivation I labelled "forced" | ⚠ **forced in the model, 6.5× absent in the data** — the derivation was sound and its premises do not describe these arms |

## the sentence I can no longer write

*"a random draw's |d| must rise with the pool's ordering disagreement, so that explains the random
families."* It must in simulation, by 0.65; in the release it does by 0.07.

## NEXT

Two arm-free pool statistics have failed while the co-movement sits at **0.59–0.72**, and the
synthetic control shows the mechanism I modelled would have produced **0.65** if it were operating.
The gap says the real `random_k` arms are **not** behaving like random draws from the pool — and there
is a direct check this round did not make: **`random_k` arms select from the pool by construction, so
their criterion sets should be uniform random k-subsets of the 16.** Test that against the committed
core JSONs: the per-prompt inclusion frequency of each of the 16 criteria across the three seeds, and
whether it is flat. ⚠ If the draws are **not** uniform — if some criteria are systematically included
— then the "random" families share structure the model denies them, which would explain both the high
mutual correlation and the absent covariate effect in one stroke, and it is one histogram to find out.
