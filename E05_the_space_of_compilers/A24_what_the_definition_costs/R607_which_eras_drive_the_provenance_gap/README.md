# R607 · Provenance collapsed 13×, and citation concentrates exactly where it collapsed

**Decision this makes safe:** where a provenance repair would bite. **Two places, for two different
reasons — and neither is the one R606's closing line assumed.**

| era | round ids | n | cited | P(prov \| cited) | P(prov \| uncited) | **Δ** | citation rate | **provenance rate** |
|---|---|---|---|---|---|---|---|---|
| 0 | — | 0 | 0 | — | — | **UNDEFINED** | — | — |
| 1 | 220–242 | 23 | **0** | — | 0.0870 | **UNDEFINED** | 0.0000 | 0.0870 |
| 2 | 243–364 | 118 | 3 | 0.0000 | 0.1739 | −0.1739 | 0.0254 | 0.1695 |
| **3** | **365–485** | 118 | 35 | **0.2571** | **0.6627** | **−0.4055** | 0.2966 | **0.5424** |
| **4** | **486–606** | 119 | **68** | 0.0441 | 0.0392 | **+0.0049** | **0.5714** | **0.0420** |

⭐⭐⭐ **Provenance adoption collapsed 13× between era 3 (0.5424) and era 4 (0.0420) — and 57.1% of
era 4 is cited.** So the pooled **−0.1762** is **two things at once**:
- **a genuine within-era selection in era 3** — the corpus's best-documented band, where cited rounds
  carry provenance **0.2571 against 0.6627**;
- **a compositional effect** — citing heavily into a band where provenance had already collapsed for
  everyone, so its own Δ is **+0.0049**, effectively none.

## ⛔ Check #206: the conditional's antecedent was unverified, and it is now refuted
R606 closed with *"if it rose **while citation concentrated in the earlier era**"*. **Citation
concentrates LATE**: 0.0000 → 0.0254 → 0.2966 → **0.5714**. ⚠ And the fossil reading it offered had
already been largely closed by **R606's own time-stratified p = 0.0003** — *proposing as live a world
the previous round had shut.*

## ⛔ My placebo was a tautology, and it also could not pass
v1 shuffled **era labels** and asked whether the **pooled** Δ changed — but `gap(lab, sc)` **has no era
term**, so the answer is **forced by the algebra**. ⚠ **The arithmetic trap, committed inside a
control.** And it compared a `round(·, 4)` print value against an unrounded pooled one at **1e-9**
tolerance, so even the tautology reported FAIL.

⭐ Replaced with one that can genuinely go either way: **shuffle provenance WITHIN each era** and
require the per-era Δs to scatter near zero. **Mean |Δ| 0.0626 against the pooled 0.1772 — PASS**,
with the two empty eras correctly returning exactly 0.0 rather than noise.

## Controls
| control | returned |
|---|---|
| **positive** — cell-weighted mean of per-era Δs must reconstruct the pooled value | **−0.1625 vs −0.1772** — PASS, it *is* a decomposition of this quantity |
| **negative** — random `cited` at the same marginal | **−0.046 / −0.020 / −0.033** — PASS |
| **placebo** — provenance shuffled within era | mean \|Δ\| **0.0626** vs **0.1772** — PASS |

⚠ **Two eras have an empty arm and their Δ is UNDEFINED — reported as such, never as 0**, which is the
value an empty cell most resembles and least means. **They contribute nothing to the verdict, and the
verdict says so.**

⚠ **The verdict label is thinner than the table.** `B PERVASIVE` fires on *"negative in 2 of 3 defined
eras"* — and one of those two (era 2) rests on **3 cited rounds**. **The decomposition is the result;
the label is a summary of it.**

**EVERYTHING HERE IS A DERIVATION** — every cell is a count over a complete enumeration and **could
not have come out otherwise**. Only the reconstruction check is a test.

**IMPOSSIBLE, named:** **round id is a proxy for time, not time.** Two adjacent ids can be days apart,
and **nothing in the artifacts carries a timestamp** — which is the register's `temporally resolved`
row, appearing here as a limit on my own instrument rather than on the release.

## The sentence I can no longer write
> *"the page's numbers come from low-provenance artifacts because provenance recording is thin."*

**It is not thin everywhere.** In era 3 it reaches **66%** of uncited rounds — and the page cites the
**26%** instead. The other half of the gap is that the page draws most heavily from the band where the
practice had already collapsed.

## NEXT
Era 3 is the corpus's best-documented band and the page cites its worst-documented quarter. **Take the
35 cited rounds of era 3 and ask what distinguishes the 9 that carry provenance from the 26 that do
not** — same era, same practice window, so era is held fixed by construction. If the split tracks
something structural (arc, artifact count, whether the round has a `run.py`), the selection has a
mechanism; if it does not, it is arbitrary and the repair is simply to re-derive the 26.
