# R795 · the specificity was target SIZE, and my own negative control was a poison

`run.py` · `PREREGISTRATION.txt` · `results/size_or_identity.json` · 968 prompts × 6 k-cells × 2
content sources × 20 draws · **NO WORLD CLAIMED** — registered in advance for exactly this outcome ·
two hash seeds byte-identical, md5 `8a13641dac0e0afe7c7f2bd752f96605`

## THE DECISION THIS MAKES SAFE

**R794's specificity gap of +0.0487 was a size effect, and the size-matched version runs the other
way.** Holding the target's size at k = 4:

> a random 4-subset of the prompt's own rubric agrees with `coval_core` at **0.7362**
> the mean k = 4 **other core** agrees at **0.7734**
> **contrast −0.0372 [−0.0446, −0.0294], p 0.0008 — RESOLVED, and NEGATIVE**

So among same-size targets the prompt's own rubric is **worse** matched to the core than a typical
other core is. **"Its own rubric" is not licensed by this data.**

## ⭐ THE SIZE DOSE IS THE MECHANISM

| k | matched (subsets of this prompt's `full`) | mismatched (another prompt's `full`) | gap |
|---:|---:|---:|---:|
| 1 | 0.6403 (sd 0.0066) | 0.4762 | +0.1641 |
| 2 | 0.6944 (sd 0.0094) | 0.4975 | +0.1969 |
| 4 | 0.7362 (sd 0.0058) | 0.4999 | +0.2362 |
| 8 | 0.7691 (sd 0.0039) | 0.4995 | +0.2696 |
| 12 | 0.7801 (sd 0.0031) | 0.5029 | +0.2772 |
| **all (15.48)** | **0.7850** | 0.5053 | +0.2796 |

Monotone, terminating exactly at R794's committed 0.7850 — **D1's POSITIVE control, PASS**. Agreement
rises **0.6403 → 0.7850** with target size alone, content fixed. R794 compared `vs full` at k = 15.48
against a k = 4 arm and read the difference as identity. **It is 0.0488 of dose.**

## ⛔⛔ AND MY OWN NEGATIVE CONTROL WAS A POISON, NOT A PLACEBO

The mismatched-prompt dose sits flat at **≈0.50** at every k — that is *another prompt's specific
criteria* pointed at these responses, which is **misdirection**, not absence. §4's poison row exactly.
The genuinely **NEUTRAL** target — criteria that never see the prompt — is `genericpool16`, and it is
size-matched to `full`:

| target | k | prompt-aware? | `coval_core` agrees |
|---|---:|---|---:|
| `full` | 15.48 | **yes** | 0.7850 |
| **`genericpool16`** | 16 | **no** | **0.7886** |
| contrast | | | **−0.0036 [−0.0195, +0.0119], p 0.6550 — UNRESOLVED** |

**A prompt-blind target of the same size matches the core as well as its own rubric does.** So the
+0.2796 gap over the mismatched dose measures *the cost of pointing a target at the wrong prompt*,
not the value of pointing it at the right one — and R794's Q1 excess of +0.2961 over a shuffled
rubric inherits that reading.

## ⛔ NO WORLD CLAIMED, AND WHY THAT IS THE HONEST OUTCOME

The prediction matrix registered **A** (E3 positive and resolved), **B** (E3 contains zero) and
**C** (the dose flat). E3 came back **resolved and negative** — a fourth outcome, covered only by the
pre-registered *"otherwise → report; claim no world."* Naming a world here would mean choosing one
after seeing a result none of them predicted.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | the k = all cell reproduces R794's `vs full`: **0.7849517906** vs **0.7849517906**, \|Δ\| **0.000e+00** | PASS, else exit 2 |
| PLACEBO | `coval_core` against its OWN class: **1.000000000000** | PASS |
| POSITIVE | D1's dose: **monotone**, band 0.6403 → 0.7850, terminating at the committed value | PASS |
| NEGATIVE | the mismatched-prompt dose below the matched one at every k ≥ 2 | PASS ⚠ **but it is a POISON — see above** |
| DEGENERACY | share of all-zero target classes, every k: **0.000** | D2's worry did not materialise |
| NOISE FLOOR | largest subset-draw sd across cells **0.0094** | measured |

## MULTIPLICITY

**21 size-matched k = 4 comparators**, BH at q = 0.05: **17 survive, 4 do not**. Both tails are
printed — `topw_k4_sham` (+0.0203) and `topabs_k4` (+0.0155) are the only arms the full-subset beats
resolvedly, while `topw_k4` and its aliases beat it by **−0.0990 [−0.1097, −0.0880]**. Plus the 12
dose cells, reported whole.

## WHAT DIED

- **R794's specificity gap of +0.0487** — it is dose, not identity. The size-matched contrast is
  **−0.0372 [−0.0446, −0.0294]**.
- **"a core preserves ITS OWN rubric's verdicts"** — what is licensed is *its own prompt's*
  responses, at a level set by the target's size.
- **my own NEGATIVE control** — a mismatched-prompt target is misdirection, and the neutral
  comparison lands at the matched value.
- ⚠ **and R794's Q1 excess of +0.2961 as a measure of matching** — it is measured against a poison
  floor. **DOWNGRADED, not overturned**: the matching claim is true against a wrong-prompt target and
  unsupported against a prompt-blind one.

## WHAT SURVIVES

R794's Q2 — the core beats `full` at predicting the human, +0.0578 [+0.0502, +0.0658] — is untouched
here: it never involved `full`'s class as a target. And the object check, the third consecutive round
reproducing a prior committed number to **0.000e+00**.

## SCOPE

968 prompts · targets built from `coval_full`'s per-criterion satisfactions (min 4, mean 15.48,
max 39 criteria) · 20 subset draws per cell · NBOOT 1,200 · instrument pairwise-sign agreement
between `coval_core`'s class and the target's class · first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| whether the core tracks the rubric's MEANING | an external gold standard — `corebench/score.py:34` |
| a subset of `full` containing the core's own criteria | the core is 98.8% novel (R785, D4) |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

The clause R794 proposed must lose a word. Computed by this round's `run.py`, agreement with a target
is set by the target's SIZE (0.6403 → 0.7850 across k, content fixed) and not by whose criteria it
is: at matched size the prompt's own rubric loses to other cores by −0.0372, and a prompt-blind
target of the same size ties it at −0.0036. So the step is to re-run R794's Q1 against the NEUTRAL
baseline rather than the poison one — `coval_core` against `genericpool16` and against size-matched
blind targets across the whole arm population — and see what remains of "preserves the rubric's
verdicts" when the floor is absence rather than misdirection.
