# R848 · what does the word "every" COST? — the bar's dose-response in family size

**Arc A24 — what the definition costs.**

## ⛔ THE ARITHMETIC TRAP KILLED THE OBVIOUS QUESTION, AND THAT IS THE FIRST RESULT

R847's NEXT proposed *"is membership monotone in search effort?"* **Clause ④ requires
`core > max(family)`, and a max is non-decreasing in the family — so membership is monotonically
NON-INCREASING BY CONSTRUCTION.** A derivation, the same trap caught one round earlier in entry
1364. **It is not asked here.**

The non-forced question is the dose-response the standard names: **how fast does the bar grow with
family size, against how fast a max over NOISE grows for free?**

## ⭐ CONTROLS

| control | result |
|---|---|
| **POSITIVE** human ranking vs itself | **1.0000 · PASS** |
| **NEGATIVE** reversed ranking | **0.2523 · PASS** |
| **SEED CHECK** a different draw seed changes the subfamily | **True · PASS** — entry 1358 found **29 files** where a seeds flag changed nothing |
| **NOISE ARM** identical family, shuffled pair-labels | ran at every size; its curve is what family size buys free |

## ⭐⭐ THE CURVE — 1,078 prompts, every annotator, 24 subfamily draws per size

| n | real max | noise max | **excess** |
|---:|---:|---:|---:|
| 5 | 0.4461 | 0.4326 | +0.0135 |
| 10 | 0.4553 | 0.4349 | +0.0204 |
| 20 | 0.4606 | 0.4395 | +0.0211 |
| **30** *(R436's committed family)* | 0.4636 | 0.4397 | +0.0240 |
| 50 | 0.4714 | 0.4425 | +0.0289 |
| 100 | 0.4716 | 0.4423 | +0.0293 |
| 200 | 0.4758 | 0.4442 | +0.0317 |
| 300 | 0.4796 | 0.4450 | +0.0347 |
| **394** | **0.4801** | 0.4451 | **+0.0351** |

**Slope per `ln(n)`: real +0.00741 · noise +0.00278 · separation +0.00464.**

⭐ **WORLD A — the real curve grows 2.7× faster than noise.** Enlarging the family buys **content**,
not merely search. ⭐ And R847's *"the excess more than doubled"* is now visible as a **smooth
monotone rise** from +0.0135 to +0.0351, not a jump — a coherent dose-response.

⚠ **The noise slope is POSITIVE (+0.00278) and that is a result too**: it quantifies the other
writer's R843 mechanism — a max over a larger family *is* larger on pure noise, at a measurable rate.

## ⭐⭐⭐ WHAT THIS BUYS THE DEFINITION — the first POSITIVE result about clause ④ in this arc

**"Every" now has a price.** Within this family class the bar rises **+0.0074 per e-fold of family
size**, and `coval_core` leads the 394-rule bar by **0.0864** — about **11.7 e-folds** of headroom.

> ⚠ **EXTRAPOLATION, D4, NOT A MEASUREMENT.** Fitting `max ≈ 0.4377 + 0.00741·ln(n)`, reaching
> `coval_core` = 0.5665 would need **n ≈ 3.5 × 10⁷ rules**. **A2 is bounded above by 1 and by the
> human ceiling, so a log fit MUST eventually break.** This is what the fitted model says, not what
> the world says, and it is a 9-point fit.

⭐ **So clause ④ is not merely "unflipped" — it has a MARGIN WITH A RATE ATTACHED.** That is a
different kind of statement from every previous result in this arc, all of which were caveats.

## ⚠ SCOPE — the rate belongs to a family CLASS, not to "responses alone"

- **Population of rules**: single- and two-feature rules over **14** response features. **A richer
  class — learned features, embeddings, fitted combiners — is a different curve entirely**, and this
  round says nothing about it.
- The log model is a **9-point fit on a bounded statistic**. D4.
- **This does not make clause ④ safe.** It makes its exposure *quantified within one class*.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| the true supremum | "computable from responses alone" is not a finite set |
| cross-class | a family class with learned features, which is a different experiment |
| causally identified | an intervention, not a re-scoring |

⚠ **N/A with what each would require — never "planned".**

## ⭐ AND AN ARTIFACT R847 SHOULD HAVE SHIPPED

`results/dose_response.json` **persists all 394 per-rule real and noise scores**, so a later round can
re-cut the curve without recomputing anything. R847 shipped only its summary — *"what a LATER round
needs to ATTACK this"* is a checklist line, and R847 missed it.
