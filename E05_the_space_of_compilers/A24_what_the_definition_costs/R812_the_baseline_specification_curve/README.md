# R812 · the baseline was a 96th-percentile draw and it changed nothing — all 1,820 swept

`run.py` · `PREREGISTRATION.txt` · `results/baseline_curve.json` · 968 prompts × 5 arms ×
**C(16,4) = 1,820 baselines enumerated in full** · **WORLD A** · two hash seeds byte-identical,
md5 `e5a8b4a29f7deb5dfcf2132db3086018`

## THE DECISION THIS MAKES SAFE

**R811 was right that `POOL[0:4]` is a near-best draw, and wrong that it matters.** Every verdict
R806–R809 rest on holds at **1,820 of 1,820** baselines.

| verdict | holds at |
|---|---|
| every fitted arm above every honest arm | **1,820 / 1,820** (100.0%) |
| no arm reaches the pure-copy ceiling of 1.000 | **1,820 / 1,820** (100.0%) |
| R809's log contrast is **negative** | **1,820 / 1,820** (100.0%) |

## ⭐ AND D3 PREDICTED THE REASON BEFORE THE RUN

The baseline is subtracted from **both** sides of the slope — from the leak's margin and from the
arm's — so it partially cancels. Writing that down first is what stops a small spread being read as
a null result.

| arm | committed | family mean | sd | range | **committed percentile** |
|---|---:|---:|---:|---|---:|
| `oracle_k4_fit1` | 0.6497 | 0.6740 | 0.0229 | [0.5912, 0.7328] | 15.6% |
| `greedy_k4_fit1` | 0.6115 | 0.6379 | 0.0241 | [0.5547, 0.7023] | 14.9% |
| `indep_k4_fit1` | 0.5035 | 0.5356 | 0.0312 | [0.4388, 0.6100] | 18.2% |
| `coval_core` | 0.3489 | 0.3917 | 0.0430 | [0.2717, 0.4991] | 18.0% |
| `topw_k4` | 0.3379 | 0.3640 | 0.0347 | [0.2715, 0.4626] | 25.2% |

⭐ **No arm's committed value is in a tail** (all 14.9–25.2%), which answers the question R811 could
not: **extreme for the pool's own A2 is not extreme for the derived slope.** A slope depends on the
baseline's per-prompt covariance, not its level, and the two percentiles are 96.0 and ~18.

⚠ **But the point estimates do move, and in the direction that made the arms look better.** The
committed baseline sits *below* the family mean for every arm, so R807's scale was **conservative**:
at a typical baseline the fitted arms read **0.54–0.67** rather than 0.50–0.65, and across the whole
family **0.44–0.73**. Higher means *more leak-like*, so the committed choice understated how much of
the fitted arms is the leak.

## ⭐ AND THE BASELINE IS SECOND-ORDER AGAINST SAMPLING

| source of uncertainty | sd |
|---|---:|
| prompt bootstrap at the committed baseline | **0.0496** |
| the entire 1,820-baseline family | **0.0229** |

**Choosing the baseline is worth less than half of what sampling the prompts is worth.** The two are
reported side by side and **never pooled**, because they answer different questions.

## E2 · R809's CONTRAST ACROSS THE FAMILY

> committed **−0.1317** (reproduced exactly) · family mean **−0.1256** · sd **0.0347** · range
> **[−0.2428, −0.0374]** · committed at the **43.1st** percentile · **negative at 100% of baselines**

R809's WORLD B — the fitted arms rise *less* than honest ones in relative terms — is not a property
of one baseline.

## ⛔ TWO DEFECTS IN THIS ROUND, BOTH MINE, BOTH CAUGHT BY ITS OWN CHECKS

**① E2 did not reproduce R809 on the first run** — it returned **+0.0815** against a committed
**−0.1317**, a sign flip. R809 draws a **fresh** parity-0 half-split inside each `build(j)` call
(seed 90000+j); this round had reused R807's fixed split (seed 20240). **A sweep of a different
estimator cannot speak to R809's verdict**, and the object check had anchored only R807. Fixed by
rebuilding R809's own split per j and adding an object check on E2 itself, which now matches to
**1e-6**.

**② The negative control failed on the wrong statistic.** I compared standard deviations — permuted
0.0223 against the family's 0.0229 — and asserted permuting must move the scale "far more". That was
never derived: the family's sd is variation across **1,820 different subsets**, the permuted sd is
variation across draws of **one subset's misassigned values**; two different sources with no ordering
between them. Meanwhile the permuted range **[0.782, 0.900]** is entirely **disjoint** from the real
family's **[0.591, 0.733]** — the control had separated perfectly and my criterion could not see it.
realstat §4, *"the control targets a different statistic than the one being reported"*.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R807's λ **0.459704** and all five disattenuated values reproduced at the committed baseline | PASS, else exit 2 |
| OBJECT (E2) | R809's contrast **−0.131725** vs committed **−0.131725** | PASS **after repair** |
| PLACEBO | D1, an arm minus **itself** as baseline: max \|margin\| **0.0e+00** | PASS — identically 0 |
| POSITIVE | D2, `_perfect_leak` on itself under all 1,820 baselines: max deviation from 1.000 **0.0e+00** | PASS |
| g=0 | the honest arms must **not** sit at 1.000 — closest approach **0.501** away | PASS — the control can fail |
| NEGATIVE | baseline permuted across prompts, 200 draws: **[0.782, 0.900]** vs the real family's **[0.591, 0.733]** — **disjoint** | PASS **after repair** |
| DEGENERACY | baselines with λ ≤ 0: **0 of 1,820** (0.00%) | the family is whole, not mutilated |

## WHAT DIED

- **R811's NEXT as posed** — swapping the first-4 for the subset mean is one cell for another; the
  estimand is the curve, and the curve says the choice is not load-bearing.
- **"four rounds rest on a near-best draw, so their conclusions are suspect"** — the conclusions
  hold at every one of the 1,820.
- **my own E2**, on the first run, and **my own negative control's criterion**.

## WHAT SURVIVES — AND THIS ROUND ADDS

R806–R809's verdicts, now with a **specification curve over the one axis nobody had swept**, and a
correction to their point estimates: the committed baseline is conservative by roughly **+0.026 to
+0.043** on the disattenuated scale.

## SCOPE

968 prompts × 4 responses · annotators split by index parity · 5 named arms + 2 synthetic ·
**C(16,4) = 1,820 baselines enumerated exhaustively** — these are population quantities over the
family, not estimates of it · prompt bootstrap NBOOT 400 at the committed baseline, reported
separately · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| sweeping R805's `+0.0553` | it uses `genericpool16`, all sixteen, so it has **no subset choice to sweep** — D4, stated before the run rather than discovered after |
| a baseline outside the released pool | a second generic criterion set; the release ships one, of 16 — **checked** |
| the same sweep at k ≠ 4 | R810's baselines are `POOL[0:k]`; C(16,8) = 12,870 is enumerable and C(16,12) = 1,820 is too, so this is **feasible and simply not this round's estimand** — named so it is not mistaken for a limit |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The baseline axis is closed at k=4: exhaustive, and each of the three verdicts holds at 1,820 of
1,820. Computed by this round's `run.py`, the family spans **0.5912–0.7328** for `oracle_k4_fit1`
against a committed 0.6497, and the prompt bootstrap's **0.0496** is more than double the family's
**0.0229**.

That last ratio is the step. Two axes have now been swept exhaustively — annotator precision in R808,
baseline choice here — and both moved the estimate less than resampling the 968 prompts does. So the
dominant term is the prompt sample itself, and no round in this arc has asked what those 968 prompts
are a sample **of**. The step is to resample at the **prompt** level rather than the annotator or
baseline level — a cluster bootstrap over whatever grouping the release carries, if it carries one —
and ask whether the fitted-vs-honest ordering survives there. If it does not, the intervals this arc
has been quoting are narrower than the object supports, and the correction would reach the
`DEFINITION` broadly rather than one round's headline.
