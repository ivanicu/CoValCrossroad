# R1019 · every extension figure in this arc is A2's answer, and nothing said so

**THE DECISION THIS MAKES SAFE.** Whether *"the extension is 9 arms"* can be stated without naming a
target. **It cannot** — and the number itself survives the one alternative target computed here.

---

## ⛔ Prior art first, because it is the scope

R558, from R288's committed `target_sweep.json` — **968 prompts, six targets, four distinct admitted
sets**:

| target | admits |
|---|---|
| `A2·annot`, `A2·consensus` | `coval_core`, `topw_k4` |
| `A1·annot`, `A1·consensus` | **∅ — nothing** |
| `tau·mean` | **`coval_core` alone** |
| `top1·mean` | `topw_k4` — **not the released core** |

**That sweep is over 10 arms.** This arc spent nineteen rounds reporting an extension over **96** and
**never named the target.**

## What this round adds

The **current** formulation ②′∧③ — not clause ② alone, which is what R288 swept — over the full 96
arms, under **A2** and under a **per-annotator Kendall tau-b**:

| target | extension |
|---|---:|
| A2 | **9** |
| tau-b | **9** |
| only under A2 | **0** |
| only under tau-b | **0** |

**Identical.** Between those two targets the extension is stable, and the released core is admitted
under both.

## ⛔⛔ And my tau is not R288's tau

R288 records `coval_core` **alone** under `tau·mean`; this round's tau-b gives the same 9 as A2.

> **Same name, different statistic.** R288's is a tau against a **mean ranking**; this is a
> **per-annotator** tau averaged — at a different population (10 vs 96).

⚠ **The positive control validated the A2 branch only.** It reproduces R288's `A2·annot` answer on
R288's own subset and **licenses nothing about tau** — the blind-spot case the standard names: *a
positive control asks "can this instrument see?" and never "is what it sees the thing I am about to
claim about?"* **So R288's tau result is neither reproduced nor contradicted here.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | on R288's own subset, the A2 branch admits exactly `{coval_core, topw_k4}` — R288's committed answer |
| **NEGATIVE** | a **monotone rescaling** (A2 × 2) gives the **identical** set, because clause ② is a paired comparison and must be invariant to a positive affine change of the target. If rescaling moved the set, the operator would not be doing what it says |
| **PLACEBO** | A2 against A2, symmetric difference **0** |
| **NOISE FLOOR** | **n/a**, labelled — a set comparison. The bootstrap seed is held fixed across targets so the target is the only moving part |

## ⚠ Not recomputed, and why not

**`A1·annot`, `A1·consensus`, `top1·mean`** and the consensus variant. They need scoring conventions
this round would have to reconstruct — and **reconstructing a target in order to sweep it is how a
specification curve becomes an invention.** R288's committed answer stands for them, at its population
of 10.

## ⭐ The correction, which follows regardless of the stability result

**The extension figure carries a target, and it is A2.** R288's sweep shows at least one target under
which the definition admits **nothing**, and one under which it excludes **its own instance** — so the
label is not decoration. Written into `DEFINITION.md` and the README in this round.

## Alternatives considered

**Report "target-stable" unqualified.** Refused: it is stable across the two targets computed, and
R288's committed sweep says four of six give different answers. Quoting the stable pair as the result
would be the multiplicity failure with manners, applied to targets.

**Treat the tau disagreement as a contradiction of R288.** Refused — the statistics differ under one
name. Calling that a contradiction would manufacture a conflict out of a naming collision, which is
the error one round below it in the same standard.
