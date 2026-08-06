# R787 · `q` is exactly A2's percentile, and one reference does the work of 1,820 — but `q_resolved` is not

`run.py` · `PREREGISTRATION.txt` · `results/q_is_a2.json` · 26 arms × 1,820 references = 47,320 pairs
· **WORLD B**

## THE DECISION THIS MAKES SAFE

**Clause ②'s measurement `q` is not an independent quantity — it is the arm's percentile in the
reference A2 distribution, by algebra.** Since
`mean(v_arm − REF_i) = A2_arm − A2_ref_i`, an arm beats a reference **iff** its A2 exceeds that
reference's. Verified on **all 47,320 (arm, reference) pairs: 0 disagreements.**

⭐ **And the 1,820-member class buys nothing over one reference.** The SHAM removed the class entirely
and compared each arm to a **single** reference at A2 0.5504: it **agrees with `q > 0.5` on 26 of 26
arms.** The class's whole contribution is a set of cut points on the A2 axis — of which the 26 arms
resolve **four**.

## E2 · AND `q` DESTROYS INFORMATION

| | distinct values over 26 arms |
|---|---:|
| A2 | **19** |
| q | **4** |
| q_resolved | **6** |

**Kendall tau(A2, q) = +1.0000** — 197 concordant, **0 discordant**.
**Kendall tau(A2, q_resolved) = +1.0000** — 240 concordant, **0 discordant**.

⚠ **D2 in force: the tau of +1 for `q` is a DERIVATION, not evidence.** It could not have come out
otherwise, and it is printed as a check that the code implements the algebra. What it licenses is the
statement that no analysis downstream of `q` can recover an ordering `q` has already collapsed —
19 levels into 4.

## E3 · WHAT THE CLASS ACTUALLY IS

Reference A2: **min 0.514375, max 0.557475, range 0.043100.**

| p0 | p5 | p25 | p50 | p75 | p95 | p100 |
|---|---|---|---|---|---|---|
| 0.5144 | 0.5242 | 0.5329 | 0.5391 | 0.5446 | 0.5511 | 0.5575 |

⭐ **So "baseline-conditional" has a one-line criterion**: an arm is conditional iff its A2 lies inside
**[0.5144, 0.5575]**. Of R782's 26 arms that is `generic` (0.5514) and `gen` (0.5352) — **exactly the
two arms R781 and R782 identified empirically, now derived rather than observed.** Everything above
the range is q = 1, everything below is q = 0.

## ⛔ E4 · AND THE ROUND DOES **NOT** GET TO SAY "q IS A2" — **WORLD B**

`q_resolved` adds each reference's own MDE, `ZEFF·sd(v − REF_i)/√P`, which depends on the **variance**
of the per-prompt difference. That term **can** invert the A2 order:

| variance ratio | higher-variance arm | lower-variance arm | |
|---|---:|---:|---|
| 1.0 | 0.9835 | 0.9835 | no inversion |
| **1.5** | 0.9819 | 0.9835 | **INVERTS** |
| 2.0 | 0.9731 | 0.9835 | INVERTS |
| 4.0 | 0.8385 | 0.9835 | INVERTS |
| 8.0 | 0.1714 | 0.9835 | INVERTS |

Two synthetic arms with **identical A2** and different per-prompt variance separate from a ratio of
**1.5** — and the real arms span **[0.0711, 0.1744], a ratio of 2.453.** **The capability is inside
the observed range.**

**So the zero discordant pairs in E2 is a fact about THIS population, not about the statistic.** I
expected World A and the pre-registered synthetic refused it. `q` is A2's percentile exactly;
`q_resolved` is A2's percentile *plus a live variance term that simply did not fire on these 26 arms*.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R782's artifact loads · 26 arms rebuilt from sat files · references rebuilt to exactly **1820** | PASS, else exit 2 |
| PLACEBO | an arm against itself: paired mean **0.000000** | PASS |
| PLACEBO-2 | a class member against the class: q **0.726923** vs its own A2 rank **0.726923** | **identical** — the control that catches self-comparison |
| POSITIVE | `gen` swept: shift 0 → q **0.3308**, +0.02 → **0.9923**, +0.05 → **1.0000**, +0.30 → **1.0000**, every one matching the independently computed percentile to 1e-12 | PASS, band **admissible** |
| SHAM | the class removed — one reference at A2 0.5504 | agrees with `q > 0.5` on **26 of 26** |
| VARIANCE | E4's sweep, with the arms' observed ratio marked | **inverts in range** |
| NEGATIVE | ⛔ **not built** — D1: `q` is an algebraic function of A2, so permuting an arm across prompts leaves both unchanged | the void control of ledger 1125/1129, **declined for the third round running, now for a derived reason rather than a remembered one** |

### ⛔ AND THE FIRST POSITIVE CONTROL HAD A DEGENERATE BAND

The first draft swept `sorted(arms)[0]` — `coval_core`, at A2 0.5665, **above the entire class** — so
every shift returned q = 1.0 and I printed *"band computed at both ends"* when **floor == ceiling ==
1.0**. That is §4's *control that cannot PASS*, sub-kind one: a degenerate band admits no threshold,
and the identity check passing alongside it made the degeneracy easy to miss. The arm is now **chosen
in code** as the one nearest the class median — which selects `gen` — and the band runs 0.3308 → 1.0000.

## WHAT DIED

- **`q` as an independent measurement** — it is A2's percentile, on 47,320 pairs, 0 disagreements.
- **the 1,820-member class as a rich object for clause ②** — one reference reproduces its binary
  verdict on 26 of 26 arms. R781 measured n_eff = 1.1; this says *why*.
- **my own expected World A** — the pre-registered synthetic showed the variance term inverts at 1.5
  while the arms span 2.453.
- **the first positive control's band**, degenerate at both ends.

## WHAT SURVIVES

Every q-based ordering this arc reported: they are all equivalent to the A2 ordering, so R781's shape,
R782's `gen`, R783's `coval_core` and R786's counterexample stand as stated. **What changes is what
they mean** — each was an A2 statement wearing a percentile's clothes.

## SCOPE

population R782's 26 modal-k=4 arms · 1,820-subset reference class · 968 prompts · instrument A2 over
all annotators, q and q_resolved exactly as R781/R782 computed them · baseline A2 itself · regime
first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether a finer statistic would rank arms differently | a statistic that is not a function of the paired mean; every one used in this arc is |
| whether the class's cut points are the RIGHT ones | an external criterion for what clause ② should admit — an external gold standard for what a core should preserve — the register at `corebench/score.py:34`. ⚠ **R787–R791 cited this as "the wall (R631)"; that citation is FALSE — R631 is `the_unrecorded_retraction`. Corrected in R792.** |
| observing the variance inversion in real arms | two real arms with equal A2 and a variance ratio ≥ 1.5; the population has no such pair |
| q for arms outside modal-k=4 | their own C(16,k) class |

## NEXT

The variance term is live yet unexercised — measured in R787 as 0 discordant pairs over 240 — which is
a statement about the arms rather than the statistic, so the question is what an arm would have to
look like to exercise it. E4's synthetic
needed a ratio of 1.5 at equal A2; computed by this round's `run.py`, the real arms' per-reference sd
spans [0.0711, 0.1744] but their A2 values differ, so no observed pair isolates the term. The step is
to ask what drives per-reference sd — it is the variance of `v_arm − REF_i` across prompts, i.e. how
*unevenly* an arm beats the class rather than how much — and whether that quantity is anything the
definition should care about. If it is, clause ② has a second dimension nobody has named; if it is
not, `q_resolved` should be replaced by A2 and a stated cut, which is simpler and loses nothing.
