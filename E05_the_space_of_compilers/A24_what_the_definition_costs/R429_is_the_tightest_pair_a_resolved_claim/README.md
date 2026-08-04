# R429 · "the tightest pair" was a RANK. Is it a RESOLVED claim?

> ## ⛔ ANNOTATION 2026-08-04, two hours after this round was committed — **`W-BIAS` BELOW IS RETRACTED BY [R430](../R430_is_the_null_gap_the_null_or_the_weighting)**
>
> **What stands, unchanged and re-verified:** the headline. Rank 1 is `generic|vacuous` under *both*
> aggregation weightings and separates from rank 2 under both — **CONV +0.0226 [+0.0083, +0.0374]
> p=0.0027**, **INTER +0.0234 [+0.0107, +0.0367] p=0.0003**. ⚠ The Δ this round reports is the
> INTER one, and it never said so; the number is weighting-dependent and must be quoted with its
> weighting.
>
> **What falls:** the attribution. The −0.0148 gap is real and reproduces — but it is the
> **aggregation weight**, not the null construction. R427 aggregates by CONVERSATION
> (`lib/cluster.py`), this round pools by INTERACTION, and R430's 2×2 shows *both* nulls reproduce
> R427 under CONV (**8/10** and **9/10**) and *neither* under INTER (**2/10**, **2/10**). The two
> nulls agree to ~0.002; the two weightings differ by ~0.013.
>
> **Also falls:** *"ranks 5–10 are not quotable."* That was a **subtraction** across a comparison in
> which both axes moved. Measured per axis: weighting alone moves **2** ranks (9, 10); redrawing the
> same permutation null 30× moves a **median of 4**, and **positions 1–3 never move in any draw**.
> Wrong boundary (4, not 5) and wrong cause (the draw, not the construction).
>
> **The mode**, logged as `RETRACTIONS.md` entry 244: *a difference measured across two changed
> factors, attributed to the one I was thinking about.* Every number below is correct and every
> control below passed. The comparison had two free axes and the write-up had one mechanism.
>
> Kept verbatim below rather than rewritten — annotate, never rewrite. Read the `W-BIAS` section as
> a correct measurement with a wrong explanation attached.

**The decision this round makes safe:** whether `generic|vacuous` being rank 1 of ten arm-pairs is
something the definition may rest on. **It is — for rank 1 only.** Ranks 5–10 are not quotable from
either round, and the reason turned out to be a defect neither round had looked for.

## The claim under attack, in my own words

`780c7b0`: *"vacuous and generic are the tightest pair in the grid."* **A rank is not a measurement
of separation.** The ordering is a fact about point estimates; whether rank 1 is distinguishable
from rank 2 is a different question, and nobody asked it.

## Result — **`W-RESOLVED`** on rank 1, **`W-BIAS`** on the null

| | |
|---|---|
| **Δ(rank 1 − rank 2)** | **+0.0234 [+0.0103, +0.0364]**, p = 0.0003 |
| multiplicity | survives **BH(q=0.10) over all 45** ordered comparisons |
| cells surviving | **42 of 45** — the 3 non-survivors are listed in the artifact, not hidden |
| seed spread | **0.00025** across 3 bootstrap seeds |
| unit | **the conversation** (R413: `kappa_chosen` = 1.0 within one; rows would shrink every interval 1.82×) |

**Population** 2,200 conversations / 7,344 interactions of `data/utterances.jsonl` · **instrument**
Qwen3.5-2B-Base at k=4 · **baseline** each pair's own marginal-matched null · **regime** n ∈ {2,3,4}.

## Why the paired estimator, and what the negative control priced

The conservative propagation treats the two excesses as independent; they are computed on the
**same** conversations, so it is the estimator that manufactures a false *unresolved*. The negative
control permutes conversation labels between the two vectors and is **two-sided by design**:

- the **point** must not move — that is arithmetic, and a control testing only it would be testing
  `1+1=2`. It did not move (`+0.0233` vs `+0.0234`).
- the **spread** must widen, or the pairing carries no shared noise and this round's premise is
  false. **sd ratio unpaired/paired = 1.038** — the pairing buys ~4%, which is small and is the
  honest price of the round rather than a reason to hide it.

## ⛔ The disagreement I nearly dismissed as noise

R427 and R429 compute the same-named quantity on the same data and disagree: **ranks 1–4 identical,
six of ten positions swapped below.** My first reading — *"R427's null is one permutation draw, so
this is sampling noise"* — was a story. `null_estimator.py` tested it with a pre-registered kill in
both directions and **refuted it**:

| | |
|---|---|
| R427 null vs the analytic expectation of R427's own construction | **2 of 10 inside** the one-draw band |
| mean gap | **−0.0148** vs band half-width **0.0104** |
| all ten gaps share a sign | **yes** |
| offset spread across pairs | **0.0059** (−0.0246 … −0.0036) |

**A constant offset reorders nothing. A pair-varying one reorders exactly the ranks whose gaps are
smaller than it** — which is 5–10, and is why the two rounds agree on 1–4 and disagree below.

⚠ **Which null is correct is UNVERIFIED.** The simulation is a positive control on *R429's*
construction and shares its blind spots — it can measure that the two differ and in which
direction; it cannot adjudicate R427's. *A positive control asks "can this instrument see", never
"is what it sees the thing I am about to claim about".*

## ⛔ The round's own defect: three worlds declared, two branches coded

The docstring named `W-NOISE`, `W-FRAMING` and **`W-BIAS`**; the code folded `W-BIAS` into
`W-FRAMING`. The data landed **squarely in the missing branch** — the verdict-string failure in its
purest form, a world that existed in prose and had no branch. Fixed by making the discriminator the
offset's *spread across pairs*, which is the quantity that decides whether anything reorders.

## Controls, and what each returned

| control | returned |
|---|---|
| PLACEBO — Δ(P,P) over all 10 pairs | max abs = **0.0e+00** ✅ |
| POSITIVE — plant g = 0.5 | Δ +0.1736 [+0.1689, +0.1785], **resolves** ✅ |
| g=0 — plant g = 1.0 | Δ +0.0000 [0, 0], **does not resolve** ✅ |
| NEGATIVE — conversation labels permuted | point unmoved, sd ratio **1.038** ✅ |
| POSITIVE (null sim) — band must contain the analytic value | [0.4212, 0.4434] ∋ 0.4326 ✅ |
| g=0 (null sim) — identity permutation | band width **0.00e+00** ✅ |
| NEGATIVE (null sim) — subsample to 25% | sd **0.00530 → 0.01132**, widens ✅ |

## Impossible here, named

- **deciding which null is correct** — both constructions are defensible. Requires an external
  criterion for what "the same picks" means.
- **construct validity of "tightness"** — excess-over-marginal-null is one operationalisation.
- **a causal reading** — `vacuous` is different *text*, not an ablation inside the judge. Requires
  editing the judge.
- **cross-model** — one judge. Requires a second scored on the same responses, ~74k calls per arm.
- **generalising past k=4** — every arm carries 4 criteria and the statistic depends on k.
- **recovering R427's exact permutation** — the artifact stores the result, not the draw. This is
  why the test is distributional rather than a re-derivation.

Findings and their scope live in `DEFINITION.md` and the top-level README. This file states the
design and the round's own corrections.
