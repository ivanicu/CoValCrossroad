# R606 · The provenance mechanism exists, and it misses the page's own sources

**Decision this makes safe:** whether R605's gap is design or adoption. **Adoption — and the adoption
runs the wrong way.**

| | cited by `STATEMENT.md` | not cited |
|---|---|---|
| rounds | **105** | 272 |
| **carry a provenance key** | **11.43%** | **29.04%** |

**Δ = −0.1762 · time-stratified p = 0.0003** over 12,000 draws · **identical at both strictness
levels** (key *present* −0.1762; key *non-empty* −0.1725, p = 0.0008).

⭐ **The corpus has the mechanism** — 109 of 426 artifacts (25.6%) carry `source_sha256` /
`source_name` / `sha256` / `src_sha`. **It reaches the rounds the page does NOT cite roughly 2.5×
more often than the ones it does.**

## ⛔ My under-powered gate was degenerate by construction, and the round detects it rather than firing
The plant strips provenance from cited rounds — which moves Δ **monotonely away from zero, starting
from the observed value.** So every planted |Δ| is **≥ |Δ_obs| by construction**, and `|obs| < MDE` is
true *no matter what the data say*. v1 printed **BOUND ONLY** on a band that **cannot contain the
observation** — §4's *control that cannot PASS*, in mirror.

⭐ Detected, not assumed: smallest planted |Δ| **0.1857** vs observed **0.1762** ⇒ the band is flagged
**DEGENERATE** and the observed effect is judged by **its own stratified permutation**, which is the
only admissible test for it. *This is the third variant of the same error this session — R593's
spread-vs-concentrated plant, R592's MDE-vs-p — and the first where the round names the degeneracy in
its own output instead of me catching it afterwards.*

## ⛔ Check #205: an "only" refuted by my own passing control
R605 closed calling three artifacts *"the **only** place in this tree where a construction and a
committed matrix sit side by side."* **R605's own placebo was R604's `baseline_name.json`, written by
R604's own `run.py`** — exactly that, and there are hundreds. R605 had scanned only
`corebench/results/sat_*.npz`.

⚠ **The control that PASSED contained the counterexample to the sentence written after it.** *The
closing line does not merely lack a control — it can contradict one the round already ran.*

## Controls
| control | returned |
|---|---|
| **positive** — provenance stripped from every cited round | Δ = **−0.2904**, p = **0.0001** — PASS |
| **positive @ g=0** — nothing stripped | reproduces Δ = −0.1762 exactly — PASS, it can fail |
| **negative** — permutation **within 5 time bands** | p = **0.0003** (unstratified 0.0002) — the era is not the explanation |
| **placebo** — random label at the same marginal, 3 seeds | +0.035 / +0.101 / −0.057 — PASS |
| **strictness sweep** | *present* and *non-empty* agree in sign, size and significance |

**Δ is a DERIVATION** forced by four counts over a complete enumeration; **only the permutation p is
tested.**

**IMPOSSIBLE, named:** a recorded hash proves a source was **NAMED**, not that the **bytes match it**.
Verifying that needs the source file at the recorded path — and R605 established most are not in this
tree. **So even the 11.4% is an upper bound on attributability.**

## The sentence I can no longer write
> *"the gap is adoption rather than design, so the mechanism only needs extending."*

**The mechanism is adopted at 25.6% and adopted *least* where the deliverable draws from.** Extending
it is not the same problem as reversing a selection.

## NEXT
R592 measured code persistence decaying with round number and R594 measured verdict vocabulary
*tightening* with it — two practices moving oppositely over the same rounds. **Provenance is a third,
and its direction across the corpus is unmeasured here** because this round stratified time away
rather than describing it. **Fit provenance adoption against round id directly**: if it *rose* while
citation concentrated in the earlier era, the −0.1762 is a fossil of when the page was written rather
than a property of what it selected — and those two readings license very different repairs.
