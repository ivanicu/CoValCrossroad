# R221 — the contamination test

**Arc E05·A02.** The decision this round must make safe: *when a compiler selects four criteria to
reproduce the source's decisions, is it selecting normative content, or whatever predicts the
decisions?*

R220's `K2` cleared `D_decision` against a size-matched **random** draw. That is the weakest possible
opponent. A random subset carries no information about the outcome, so beating it shows only that
selection is not noise — it cannot distinguish *selecting norms* from *selecting predictors*. This
round builds the opponent that can.

---

## ESTIMAND

For each compiler arm `a` and each plant class `c`, the **selection rate**

```
sel(a, c) = P[ the planted criterion is among the k the arm keeps ]
```

compared against `k / (n+1)`, the rate at which an indifferent selector would pick *any one* of the
`n+1` criteria now present. And the **change in human agreement**, `Δ rank_acc`, when the plant is
in the rubric.

## IDENTIFICATION

Fully identified and requires no judge pass, because **each plant is defined by its satisfaction
vector rather than by text that has to be scored**. That is the point of the design: the plants are
not hypotheses about what a judge would say, they are exact constructions.

## WORLDS

| | what a decision-fitting compiler is doing | predicts |
|---|---|---|
| **W1 — normative** | keeping the criteria that carry the source's values | plants that carry no values are selected at chance, whatever their predictive power |
| **W2 — proxy** | keeping whatever reproduces the observed decision | the `posthoc` plant — which by construction predicts the winner perfectly and means nothing — is selected far above chance |

The two worlds differ **ontologically**, not by a parameter: under W1 the object being compiled is a
set of values, under W2 it is a decision-reproducing regression, and the same code produces both.

## THE PLANTS

Each is added to a prompt's rubric as one extra criterion, with a satisfaction vector over `A–D`.

| class | satisfaction | weight | what it is |
|---|---|---|---|
| `posthoc` | one-hot on the source's current winner | median \|w\| | **POSITIVE CONTROL.** A perfect post-hoc rationalisation: maximal predictive power, zero normative content. A decision-fitter *must* take it. If it does not, the detector is broken and nothing else here reads |
| `inert` | constant 0.5 | median \|w\| | **NEGATIVE CONTROL.** Contributes an identical amount to every response, so it cannot change any `argmax`. Must never be selected above chance |
| `duplicate` | copy of the highest-\|w\| real criterion | its weight | redundancy the compiler is documented to remove |
| `permuted` | a real criterion's satisfaction, shuffled across responses | its weight | real text, real weight, decorrelated from these responses |
| `style_length` | normalised response character length | median \|w\| | the confound the project already measured: "pick the longest" reaches 37.3% on its own |

`permuted` and `style_length` are **sham** rather than placebo: same size, same weight scale, same
arithmetic, one ingredient removed.

## PRE-REGISTERED KILL — a conditional, not a threshold

```
if sel(D_decision, posthoc) > chance          # positive control fires
   and sel(D_decision, inert) <= chance:      # negative control is null
       if sel(D, posthoc) > sel(D, real criteria of matched weight):
             W1 REFUTED -- decision-fitting selects the proxy
       else: W2 REFUTED
else:  UNVERIFIED     # never REFUTED, never CONFIRMED
```

The instrument has to demonstrate it can see selection at all before its verdict on any other plant
is admissible. R220 shipped a kill that fired off a constant the author chose; this one cannot fire
unless both controls behave.

## SCOPE

**Population** 968 prompts, all with ≥4 rated criteria. **Instrument** the cached Qwen3.5-2B
satisfaction tensor for the *real* criteria; the plants carry no instrument at all. **Baseline**
`k/(n+1)` per prompt. **Regime** k ∈ {3,4,5}; one plant at a time and all five at once.

## SPECIFICATION AND MULTIPLICITY

5 plant classes × 5 arms × 3 values of k × 3 seeds × 2 injection modes. The whole grid is reported,
including the cells that kill the finding.

## WHAT THIS SITE STILL CANNOT DO

| | what it would require |
|---|---|
| a plant judged as *text* rather than constructed as a vector | a judge pass over generated criteria, which re-opens the instrument choice this round is designed to hold fixed |
| whether a *human* would have selected the plant | new elicitation |
| whether the contamination reaches a trained model | R220's register, unchanged: no `Y` in the release |

---

## OUTCOME — `UNVERIFIED`, with the cause identified

The kill did not fire, twice, and the second failure is the finding.

**First positive control (`posthoc`, one-hot on the winner): selected at 0.0537 against chance
0.2713.** Not resistance to proxies — I had built a control against an objective the compiler does
not optimise. `greedy_decision_subset` maximises agreement with the **full ranking**; a one-hot
vector fixes one position of four and destroys the other three. A control that *cannot succeed* is
the mirror image of a check that cannot fail.

**Corrected positive control (`rank_clone`, alone reproduces the ranking exactly): 0.1477, still
below chance.** That one needed a different explanation, and measuring it gave one:

| | |
|---|---|
| prompts where **some single criterion alone reproduces the whole ranking** | **100.0%** of 968 |
| criteria tied at that perfect score | median **3**, mean **4.1** |
| `rank_clone` is **among** the tied best | **100.0%** |
| `rank_clone` is the **unique** best | **12.7%** |

The greedy breaks ties by array position and the plant is appended last, so `0.1477` is essentially
`12.7%` — **its selection rate measures where it sits in the list, not whether it is good.**

### The belief that changed

A ranking over four responses carries at most `log₂(24) = 4.6` bits. Against a median of 15
criteria, that is not enough resolution to prefer one criterion over another: **the
decision-preservation objective has a median of three equally perfect answers at `k=1`, on every
prompt in the release.**

Consequences, none of which were visible from R220:

- **R220's `K5` is explained, not merely observed.** Bootstrap instability — 26.3% of selected
  criteria appearing in under half the resamples while accuracy moved 0.0028 — is what a flat
  objective looks like from the outside.
- **`D_decision`'s regret of 0.0001 is not skill.** Reproducing the ranking is nearly free.
- **No contamination test can discriminate here.** A plant that predicts perfectly is
  indistinguishable from the three real criteria that also predict perfectly. The instrument is
  unfit for the question, which is `UNVERIFIED` — never an acquittal.

### The sentence that can no longer be written

*"A decision-preserving core selects the criteria that carry the decision."* On this release it
selects **one of several** criteria that carry it, and which one is decided by tie-breaking.

### What would make this answerable

More candidates per prompt. The resolution of the objective is set by `log₂(m!)` for `m` responses:
at `m=4` it is 4.6 bits, at `m=8` it is 15.3. That is the same missing design feature R220's
register already names — and it is now quantified rather than asserted.
