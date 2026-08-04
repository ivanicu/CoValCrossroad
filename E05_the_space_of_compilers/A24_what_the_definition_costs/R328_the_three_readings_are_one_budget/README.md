# R328 — the three readings are three points on one scalar, and the arms were never matched to it

**Decision this makes safe:** whether clause ②'s reference is Ivan's to choose. **It is not — the
campaign already owns the principle that fixes it, and applying it admits both arms.** R327 stopped
one step short of an answer it had the materials for.

## W-MATCHED-AGREES

| arm | its own budget | matched reference A2 | gap | MDE | ratio | verdict |
|---|---:|---:|---:|---:|---:|---|
| `coval_core` | 1 | 0.54026 | +0.0262 | 0.0099 | **2.64×** | BEATS |
| `topw_k4` | ≥11 | 0.55061 | +0.0136 | 0.0098 | **1.38×** | BEATS |
| `gen_sham` *(neg)* | 1 | 0.54026 | −0.0575 | 0.0130 | 4.43× | LOSES |

Admitted set `{coval_core, topw_k4}` — the set of **readings B and C**, and not of **A**.

## Why this is not a fourth opinion: R287 already wrote the rule and never applied it to the arms

> *"comparing a searched baseline to an unsearched arm is not 'strict', it is **MISMATCHED** — the
> same class of error as comparing arms of different k."* — R287, about the baseline side only.

Every round since has held all arms to **one** reference. But the two admitted arms did not cost the
same to find:

- `coval_core` — the release's own core. **This campaign selected nothing**; budget 1 here.
- `topw_k4` — one cell of a rule × k grid this campaign scored **on these same 968 prompts**. Eleven
  deterministic rule × k cores are committed under `corebench/results/`. Budget **≥ 11, in-sample**.

If a baseline's budget must be stated, so must an arm's.

## ⛔ The provenance control fired, and it is the round's hardest number

R326 hard-codes `0.5575138121466373` as *"budget 1820 · IN-SAMPLE (ceiling, unattainable)"*,
`"source": "R287"`. Asserted mechanically, not described:

| question | answer |
|---|---|
| is it anywhere in R287's artifact? | **False** — R287 disqualified the ceiling and never committed it |
| is it R286's true in-sample argmax? | **False** — that is `dist["max"] = 0.55747530882624` |
| is it R286 `selection["best"][0][1]`? | **True** — the **held-out** score of split 0 |

**A held-out number is published as the in-sample ceiling, attributed to a round that never computed
it, while the real ceiling sits in the same artifact one key away.** This round's pipeline reproduces
the true argmax to 1e-12. R327 carried the wrong value into its table as the disqualified row.

## The budget curve — and the part of it that is algebra

| m | in-sample | held-out | coinflip (NEG) |
|---:|---:|---:|---:|
| 1 | 0.54026 | 0.53770 | 0.53766 |
| 11 | 0.55061 | 0.54963 | 0.53920 |
| 64 | 0.55423 | 0.55179 | 0.53928 |
| 1820 | 0.55748 | 0.55402 | 0.53869 |

⛔ **In-sample best-of-m is non-decreasing in m by construction — that it rises is a DERIVATION.**
What is not forced: the held-out curve (a split can overfit), each cell's own MDE, and where the
curve crosses each arm. The coinflip arm holds flat across the whole grid (span 0.0032 vs mean seed
sd 0.0015), so the rise is `argmax` and not the draw count.

⛔ **R327's `unmeasured` cell is a derivation too.** `topw_k4` at budget 0 is
`0.564181 − 0.539706 = +0.024475`, admitted at **2.26×–2.46×** under *every* MDE committed anywhere
in R326. Running it would have been Closure wearing a round's clothes; it is computed and labelled.

## Sensitivity — the budget is a lower bound, so where does the conclusion turn?

| arm | mode | counted | first m that fails | headroom |
|---|---|---:|---:|---:|
| `coval_core` | in-sample | 1 | 512 | 512× |
| `coval_core` | held-out | 1 | *never on this grid* | — |
| `topw_k4` | in-sample | 11 | **64** | **6×** |
| `topw_k4` | held-out | 11 | 512 | 47× |

**`topw_k4`'s admission survives a true budget six times the counted one.** Uncommitted candidates
are uncountable, and the sign of that error is stated: a larger budget raises its reference and can
only make admission *harder*.

## ⚠ The agreement is on the SET, not on the REFERENCE

Budget-matching puts `topw_k4` against **0.55061**; reading B uses **0.55135**. Two different
references that happen to license the same admissions. **Reading B was accidentally near
budget-matched — that is luck, and must never be reported as its justification.**

## Controls

| control | result |
|---|---|
| **positive** — reproduce three committed references, read not typed | **3 of 3 exact to 1e-12** |
| **positive @ g=0** — on *shared* draws, argmax-of-1 ≡ coinflip-of-1 | exact, 0.0e+00 |
| **negative** — coinflip-of-m, selection destroyed, draw count kept | flat: span 0.0032 vs sd 0.0015 |
| **negative (arm side)** — `gen_sham` at its matched budget | LOSES, 4.43× |
| **placebo** — each arm against itself | 0.0 ulp |
| **provenance** — where R326's ceiling literal comes from | defect CONFIRMED |
| multiplicity | 90 cells, BH q=0.05, **88 survive**; non-survivors named |

## ⚠ Two of my own defects, both caught by controls rather than by reading

**① The g=0 control failed on its own noise.** v1 compared best-of-1 and coinflip-of-1 computed from
**different rng streams**, then thresholded against a 3-seed sd (|Δ|=0.0026 vs 3sd=0.0021). Nothing
was wrong with the instrument. §4 `the control fails for its own reasons`, sub-kind ① — two different
draws treated as one. At m=1 the two rules select the same element *by construction*, so on shared
draws the identity is **exact** and there is no threshold left to get wrong.

**② The verdict reported a tie as a winner.** Readings B and C carry the *same* admitted set;
`same[0]` printed B and dropped C silently. All matching readings are now named, and the
non-matching one too.

## Scope

968 CoVal prompts with ≥2 annotators · Qwen3.5-2B-Base under R234's canonical builder ·
16-criterion generic pool, all 1,820 quadruples enumerated · k=4 exactly · all annotators ·
15 budgets × 2 modes × 3 arms × 3 seeds, 20 replicates per cell.

## What this cannot do

Recover `coval_core`'s **true** construction budget, which was set outside this campaign by the
release's authors and would need their construction log. Its budget *within* this campaign is 1, and
that is the only claim made. Nor can it count uncommitted candidates for `topw_k4` — hence the
sensitivity table above, which is what a lower bound is allowed to license.
