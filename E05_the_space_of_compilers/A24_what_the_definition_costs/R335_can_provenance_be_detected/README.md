# R335 — clause ③'s detector existed, was never calibrated, and it works

**Decision this makes safe:** whether clause ③ can carry a computed test instead of a provenance
annotation. **It can.** The classes separate from a leak dose of **0.10** upward, at **32.9**
across-seed sd, against a **quality-matched** clean boundary. **W-DECIDABLE.**

## ⛔ R334's closing line was false — third in a row about my own work

> *"clause ③ … has no instrument at all"*

**R295 built one** — the slope of the clause-② margin across quintiles of within-prompt
half-agreement, with a `fitted` label per arm and an excess over an unfitted floor.

**What is actually missing is sharper.** R295's artifact carries **6 arms: 4 fitted, 2 unfitted.**
A detector validated on **4 positives and 2 negatives** has no operating characteristic — no
sensitivity, no specificity, no threshold with an error rate. It was shown to *fire on things known
to leak*. It was never shown *not to fire on things known not to*, beyond n=2.

## The population the calibration needed — 18 arms, zero judge calls

Selection consumes only already-judged satisfaction, so arms of **known** provenance are free:

> `dose f` = the fraction of this prompt's parity-1 annotators the selection may fit on.
> `f = 0` → a random draw, clean by construction. `f = 1` → fitted on every parity-1 annotator.

| dose | slope (3 seeds) | Q1 | fires? |
|---:|---|---:|---|
| **0.00** | −0.0196 · −0.0198 · −0.0214 | −0.027 … −0.006 | **no** |
| 0.10 | 0.0249 · 0.0225 · 0.0214 | −0.021 … −0.010 | YES |
| 0.25 | 0.0274 · 0.0298 · 0.0272 | −0.011 … −0.004 | YES |
| 0.50 | 0.0289 · 0.0299 · 0.0293 | −0.005 … +0.012 | YES |
| 0.75 | 0.0315 · 0.0289 · 0.0280 | +0.011 … +0.015 | YES |
| **1.00** | 0.0307 · 0.0304 · 0.0315 | +0.011 … +0.013 | YES |

## ⚠ The boundary is quality-matched, and that changes the number

My `f=0` arms are **random** draws sitting at slope ≈ **−0.020** — far below R295's *real* unfitted
arms (`coval_core` **+0.00855**, `topw_k4` **+0.00458**). A fitted arm is **better AND fitted**, so
*fitted-vs-random* would confound provenance with quality.

**The clean boundary is therefore `max(clean) = +0.0085` — `coval_core`, an arm as good as anything
admitted** — not the random floor. Separation survives it:

| dose | min fitted slope | clean boundary | disjoint? | separation |
|---:|---:|---:|---|---:|
| 0.10 | 0.0214 | 0.0085 | ✓ | **32.9 sd** |
| 0.25 | 0.0272 | 0.0085 | ✓ | 38.1 |
| 1.00 | 0.0304 | 0.0085 | ✓ | 40.9 |

## Controls

| control | result |
|---|---|
| **positive** — reproduce R295's committed slope for *both* its unfitted arms | `+0.008547932270` · `+0.004579883562`, **exact to 1e-12** |
| **positive @ g=0** — the 3 provably-clean `f=0` arms must not fire | none fired |
| **negative** — `f=1` fitted on a **different prompt's** labels: a *real* fit, wrong labels | slopes **−0.047, −0.048, −0.049**, none fire |
| **placebo** — two independent `f=0` arms | differ by 0.00021 vs 3sd 0.00297 |
| noise floor | across-seed sd at `f=0` = **0.00099** |
| multiplicity | 6 doses × 3 seeds × 2 signatures, every cell printed |

**The negative control is the one that matters.** It separates *"was optimised"* from *"was optimised
on this prompt"* — a genuine f=1 fit on the wrong prompt's labels lands at **−0.047**, *below* even
the random arms. The detector responds to this conversation's labels, not to optimisation.

## ⛔ Declared arithmetic

That a fitted arm **scores higher** is forced — it was selected to. **The detector is not about the
level, it is about the SHAPE**: whether the advantage concentrates where the two annotator halves
agree. The dose-response, the separation, and the detection limit are what was measured.

## What this settles for the definition

> **Clause ③ can carry a computed test with a stated detection limit** — leakage at a dose of 0.10
> of a prompt's annotators is already separable — **instead of a provenance annotation read off
> `select_core.py`.**

## Scope

968 CoVal prompts with ≥1 annotator in **each** parity · Qwen3.5-2B-Base under R234's canonical
builder · baseline the size-matched first-k blind subset · k=4, fit on parity 1, scored on parity 0 ·
300 candidate subsets searched per prompt · 6 doses × 3 seeds.

## What this cannot do

**Certify an arm this round did not build.** The manufactured population *calibrates* the detector;
it cannot classify an arm whose construction is unknown, because the mapping from construction to
dose is exactly what the release does not carry. And whether the detection limit transfers needs a
second release.
