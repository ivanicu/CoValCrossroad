# What R240 will change — registered before it returns

**Written while task 554 is still judging.** The two blind designs have a reading rule fixed in
advance (`A08/README.md`); 554 does not, and a result whose reading is decided afterwards is a
result I will read as confirmation.

## The claim at risk

`FORMULATION.md` claim **6** is `DERIVED` and claim **7** is `OPEN`:

> **6** — the identifiability failure is a property of the per-prompt factoring; across 986 prompts
> the bits add to `[1006, 3402]` and a global core of `k ≤ 119` is identifiable.
> **7** — whether a global core *exists* is open.

**Claim 6 is about the channel. Claim 7 is about the object.** A channel with capacity for a signal
that is not there is a true statement about nothing, and R239 said so at the time.

## The prediction matrix, fixed now

| outcome of R240 | what it does to the formulation |
|---|---|
| **held-out agreement above the floor's best draw at ≥1 value of k** | claim 7 becomes `MEASURED`. **A global core exists and transfers to prompts it was never fitted to.** Claim 6 stops being a statement about capacity and becomes the explanation for why CoVal's per-prompt object was the wrong factoring. This is the strongest available outcome and I should distrust it accordingly |
| **held-out inside the floor at every k, fit-half above it** | the fitter works and there is **nothing to fit**. Claim 6 survives *as arithmetic* and is **demoted to irrelevant**: the bits add and no global core exists to use them. FORMULATION claim 6 gets an explicit "true and inconsequential" annotation |
| **fit-half also inside the floor** | `UNVERIFIED`. The positive control failed, the fitter cannot beat random on data it was fitted to, and **no held-out number is readable.** Nothing about claim 7 either way |
| **negative control non-null** (shuffled fit/eval still shows a gain) | `UNVERIFIED`, and worse — it would mean the split is not doing what a split does, and R240's design is wrong rather than its answer |

## What I expect, recorded so it can be wrong

**I expect the second row.** The bits add, and I expect no global core to be found — because R232
established that every `coval_core` item carries exactly one field and R239 established that of
15,058 criterion token-sets exactly **one** recurs across prompts. **Criteria in this release are
prompt-specific by construction, and a vocabulary chosen for genericness is still built from
prompt-specific text.**

If the first row happens instead, **that expectation was wrong and the finding is larger than the
formulation currently allows for.**

## What no outcome of R240 can establish

- that a global core is **useful** — no downstream task exists here
- that **humans** would endorse it — no labels for a global object exist
- that it transfers **beyond this release** — one site, and R242 just scored this arc at 46.9% of
  the standard it applies

## The one thing that would invalidate the round regardless of its number

The vocabulary was selected by **token document frequency across prompts** — the most
generic-sounding criteria — and selection was made **before** any satisfaction value was read. If
that turns out to have peeked at the outcome in any way, the round is void independent of what it
found. The selection code is `run.py` lines above the judge call, and it touches only `criterion`
text.

---

# POST-HOC — resolved 2026-08-03, against the matrix above

**Row 2 fired: "held-out inside the floor at every k, fit-half above it."** That is the row this file
recorded as *what I expect*, and the expectation held — but **not on R240's own reading.**

| | |
|---|---|
| what 554 printed | *"A GLOBAL CORE TRANSFERS ... Identifiable at 1 of 6 sizes tested."* — row 1 |
| what its negative control printed, two lines above | `+0.0950 NOT NULL` — **row 4** |
| what row 4 says here, written before the run | `UNVERIFIED ... R240's design is wrong rather than its answer` |
| what R246 then measured | the negative control's evaluation set is **50.00%** training data — it destroys nothing and cannot come back null |
| what R247 measured at 10 seeds and 500 floor draws | held-out **0.3060** (was 0.3500 at 3 seeds), empirical p **0.0699–0.1637**, **BH kills all six k** |

**Row 4 dominated row 1, and the matrix said so in advance.** Without this file I would have kept
the headline: it is the strongest-sounding outcome, its own script printed it in capitals, and the
line that contradicted it was a control I had already written off as noise.

## What the matrix got wrong

It offered four rows and **none of them was "the verdict and the control disagree, and the control is
itself broken."** Row 4 assumed a non-null negative control meant *leakage*; it actually meant
*contamination of the control*, which is a different defect with the same printout. The repaired
control — permute the targets, refit, evaluate on true targets — came back correctly null
(0.2080 vs a floor of 0.2649 at k=32), so **overfitting was never the problem and the original arm
had been answering a question nobody asked.**

## The rivals that died, which is what makes the null admissible

- **modal-class predictor**: 0.0633. The target distribution is nearly flat — 24 classes, entropy
  4.485 bits against 4.585 for uniform-over-24.
- **response length alone**: 0.0420.
- **selection itself**: the unselected all-200 vocabulary scores 0.2550, inside the fitted arm's
  seed spread at every k. **Even had the transfer cleared the floor, there would be no core** — no
  compression, just the vocabulary.

## The one thing this round establishes positively

Greedy selection on **true** targets transfers strictly better than greedy selection on **scrambled**
targets (0.3060 vs 0.2080 at k=32, 6 of 6 k same sign). The fitter is not overfitting. It has
nothing left to find once the vocabulary is granted.
