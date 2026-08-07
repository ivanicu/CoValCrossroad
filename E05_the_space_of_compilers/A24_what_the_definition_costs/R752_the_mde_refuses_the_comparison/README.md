# R752 · the MDE refuses the comparison — and the formula that computed it was itself too generous

**The empirical MDE of R751's restricted-detector comparison is **0.1604** — **3.95×** the largest
observed gap of **0.0406**. **0 of 24** cells in the design grid can detect it. Running the comparison
would produce a null that means nothing. It is **REFUSED**, and what stands instead is a **census of
4** figures read one by one, from which **no rate is computed**.**

## check #354 — computing the MDE first is what killed the round it was meant to enable

R751 closed by demanding the restricted detector be preregistered **and its MDE computed before the
run**. Doing that, in the preregistration:

| p̄ | SE | MDE (α .05, power .80, two-sided) |
|---|---|---|
| 0.05 | 0.0419 | **0.1174** |
| 0.10 | 0.0577 | 0.1616 |
| 0.15 | 0.0687 | 0.1924 |

against gaps of `ungrounded` **0.0206** and `corrected` **0.0406**. **The comparison was dead before
any code ran**, and the preregistration says so rather than discovering it afterwards.

## ⛔ and then the formula failed its own control

Planting a difference of **exactly the analytic MDE** and running the exact test it approximates:
**rejection 0.6237**, not 0.80 — across 3 seeds, spread 0.0101. **The normal approximation overstates
this design's power**, which is the confound written before the run: `0.05 × 33` is **under 2 expected
events**.

⭐ **The preregistration pre-authorised the repair**, so it was applied rather than improvised:
*"if the simulated rejection rate at the analytic MDE misses 0.80 badly, the FORMULA is what failed
and the refusal must be restated on the simulated MDE instead."*

| | analytic | **empirical (searched)** |
|---|---|---|
| MDE | 0.1174 | **0.1604** — **1.37× larger** |
| ratio to the gap | 2.89× | **3.95×** |
| required n per arm | 453 | **846** — against **33** available |

**The design is blinder than the formula claimed, so World B is strengthened, not weakened.**

⚠ **The positive control is the LADDER, not the search's own answer** — asserting that the searched
MDE rejects at 0.80 would be circular. Rejection must be **monotone in plant size**, checked at
`0 → m/2 → m → 2m`: **0.0395 → 0.4460 → 0.7999 → 0.9954`. Monotone.

## the grid — 24 cells, all reported

**0 of 24** detect the observed gap: every combination of p̄ ∈ {0.05, 0.10, 0.15} × α ∈ {0.05, 0.10}
× power ∈ {0.80, 0.90} × {two-sided, one-sided} returns **BLIND**. The most permissive cell
(p̄ 0.05, α 0.10, power 0.80, one-sided) is still **0.0838**, twice the gap.

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | the monotone ladder, `0.0395 → 0.4460 → 0.7999 → 0.9954`. Band computed: floor = rejection at zero plant **0.0395**, ceiling = rejection at a maximal plant **1.0000** |
| **g=0** | zero planted difference rejects at **0.0395 ≈ α**. A test rejecting at 0.30 under the null would make every MDE claim above it meaningless |
| **NEGATIVE** | at **10× n**: MDE 0.1174 → **0.0371**, ratio **3.16** against √10 = **3.16**, and the gap now rejects at **0.7823**. **The sample is the problem, not the estimator** |
| **SHAM** | ingredient **absent** — imbalance removed, both arms at the harmonic mean **54.1**: MDE **0.1174**, unchanged. **The imbalance is not the binding constraint; the total is** |
| **PLACEBO** | the analytic MDE computed twice differs by exactly **0** |

## E2 — the census, n = 4, and no rate is computed from it

| line | value | cites | keyword | scope language too? |
|---|---|---|---|---|
| 551 | `0.0022` | R741 | `corrected` | **yes** — ambiguous |
| 551 | `0.0995` | R741 | `corrected` | **yes** — ambiguous |
| 620 | `+0.0582` | R514, R515 | `ungrounded` | **no** — clean |
| 620 | `0.0200` | R514, R515 | `ungrounded` | **no** — clean |

⇒ **2 of 4 are unambiguous groundedness declarations** — the R591 pair the page already annotates.
The other 2 sit under a `CORRECTED` marker that **also** carries scope language, so the keyword alone
cannot tell which job it is doing. **That is the same confusion that inverted R751's pooled detector,
visible here at the level of the individual figure.**

⛔ **A census of 4 has no interval and no power to generalise.** Four items produce four verdicts,
never a percentage.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 rejection at the analytic MDE | 0.80, band [0.70, 0.90] | **0.6237** | ⛔ **FAILED — the formula, not the design** |
| P2 rejection at zero | 0.05, band [0.02, 0.09] | **0.0395** | ✓ |
| P3 required n per arm | 800, band [200, 5000] | **453** analytic / **846** empirical | ⚠ **the registration did not say WHICH**, because I did not know the formula would fail. Both reported; not scored by whichever lands closer *(ledger 1026)* |
| P4 census size | 4, band [0, 10] | **4** | ✓ exact |
| P5 groundedness without scope language | 2, band [0, 10] | **2** | ✓ exact |
| D balancing does not rescue | true | **true** | ✓ |

## the sentence I can no longer write

*"the restricted detector points the right way, so it is the better instrument."* At this n the design
cannot tell a 4-point gap from zero, and the analytic formula that said otherwise was **1.37×** too
generous about itself.

## NEXT

This round refused a comparison and produced a census, so what it leaves is a *requirement*: **846
figures per arm** against 33 available. That number is a specification for a second site, and the
impossibility register carries "cross-site" as a category rather than a quantity. Price it: count how
many numeric figures the OTHER deliverable documents in this repository carry — `FORMULATION.md` and
the round READMEs are on disk — and report how many such pages would be needed to reach 846. If the answer is a handful, the comparison is reachable and
the register's cross-site line becomes an action rather than a wall; if it is hundreds, the line is a
real limit and should say so with a number instead of a category.
