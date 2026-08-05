# R592 · The audit arc that checked everyone's provenance shipped no instrument of its own

**Decision this makes safe:** the deliverable's evidence is **not** systematically concentrated in
unattackable rounds — **but the last 14 audit rounds were, and that is a fact about my practice, not
about the corpus.**

**29 of 584 rounds (5.0%) persist no code. R577–R590 is an unbroken run of 14.**

## The rival won, and it won decisively

| | Δ = P(cited \| codeless) − P(cited \| has code) | p |
|---|---|---|
| **raw** | **+0.1263** *(27.6% vs 15.0%)* | 0.1057 |
| **stratified, late half only** | **−0.0105** | **1.0000** |

⭐ **The entire raw gap is the time trend.** Codeless rate is **0.68% in the early half and 9.28% in
the late half — 13.6×, p = 0.0001** — and `STATEMENT.md` was written in the R451–559 era, so recent
rounds are both more codeless *and* more cited. **Holding time roughly fixed, the association
vanishes and even reverses sign.**

## ⛔ The raw Δ was never resolvable, and my verdict branch ignored the MDE it had just computed
`|Δ| = 0.1263` sits **below this design's own MDE of +0.1626** *(dose-response: 10% planting is the
first cell to clear p < 0.05)*. **v1 printed `A INCIDENTAL — inside the permutation null`. That is
silence read as an acquittal**, and it is §4's *verdict string is not a computation* — **fifth
instance this session**. Corrected branch: **UNDER-POWERED. Worlds A and B are both still live at
this effect size**, and only the stratified test settles anything.

## ⛔ And check #192 killed this round's own predecessor line before it ran
R591 closed with *"count how many rounds carry a runnable `run.py`."* **`run.py` is a filename; the
property is re-runnability.** Measured immediately: **339 rounds ship `run.py`**, but the corpus also
holds `selftest.py`, `speccurve.py`, `strata.py`, `recovery.py` and 20 more one-off names — a
`run.py` census would have mis-scored every round that named its script after its question.
**Instrument unit ≠ claim unit, the fifteenth instance of that class this session.**

## The streak, named
```
R577 R578 R579 R580 R581 R582 R583 R584 R585 R586 R587 R588 R589 R590
```
⭐⭐⭐ **Every one is a document-audit round — the arc whose entire subject was whether other rounds'
numbers could be traced.** R590 is where it cost something concrete: its citation extractor could not
be read, so R591 had to establish the truncation indirectly through a specification curve.
**The practice resumed at R591**, which is the round where check #191 first forced the question.

## Controls
| control | returned |
|---|---|
| **positive** — plant: the 29 most-cited rounds forced codeless | **Δ = +0.8883, p = 0.0001** — PASS |
| **positive @ g=0** — nothing planted | **Δ = +0.1263 = observed exactly** — PASS, it can fail |
| **dose-response** | 5% → p 0.1039 · **10% → 0.0365 (MDE)** · 20% → 0.0045 · 50% → 0.0005 · 100% → 0.0005 |
| **negative** — permutation null, 3 seeds × 5,000 (15,000 draws, floor 0.00007) | p = 0.1057 |
| **placebo** — random flag at the same marginal, 3 seeds | −0.0188 · +0.0900 · −0.0188 — PASS |
| **duplicate round ids** — P16 requires global continuity | **none** across all 584 |

**IMPOSSIBLE, named:** persisting code is **necessary and not sufficient** for a later round to
attack the instrument — a script may import a deleted module or a dead path. Establishing sufficiency
would need 583 scripts executed against their original environments, which no artifact records.
**Every number here is an UPPER BOUND on attackability and is reported as one.**

**The point estimate is a DERIVATION** — Δ is forced by four counts over a complete enumeration.
**Only the permutation p is tested.**

## The sentence I can no longer write
> *"the rounds the statement leans on are the ones whose instruments cannot be read."*

They are not. **The codeless rounds are the recent ones, and the recent ones are the audit arc.**

## NEXT
**8 codeless rounds are cited by the deliverable** — `R444 · R544 · R545 · R546 · R578 · R580 · R581
· R585`. Their claims rest on artifacts nobody can regenerate. **Check whether each one's `results/`
JSON is even internally sufficient to state its claim** — a persisted number with no code is
attackable if the artifact carries its own scope, and inert if it does not, and which of the two
holds is a property of the artifact rather than of the missing script.
