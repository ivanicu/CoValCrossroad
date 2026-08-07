# R799 · the spread is real and it is PROMPT, not criterion — and the pool is what proves it

`run.py` · `PREREGISTRATION.txt` · `results/deconvolution.json` · 968 prompts · 14,979 `full` × 15,482
pool instances · **WORLD A** · two hash seeds byte-identical, md5 `317087c6b010e321cda83b468a2e7e65`

## THE DECISION THIS MAKES SAFE

**Instance-level accuracy has a large real spread — and for the one pool where criterion and prompt
can be separated, almost none of it belongs to the criterion.**

| | `coval_full` | `genericpool16` |
|---|---:|---:|
| split-half reliability (annotators) | **+0.8204 [+0.8172, +0.8278]**, SB **+0.9013** | **+0.7597 [+0.7531, +0.7668]**, SB **+0.8635** |
| zero-signal control | +0.0080 | −0.0060 |
| observed sd | 0.1853 | 0.1649 |
| noise sd | 0.0578 | 0.0609 |
| **deconvolved signal sd** | **0.1760 (95.0% of observed)** | **0.1532 (92.9%)** |

⭐⭐ **And the pool decides what the rubric cannot.** Its 16 criteria each span all 968 prompts, so
their spread is criterion-attributable:

> **across the 16 pool criteria: sd 0.0157** (range 0.5048 – 0.5585)
> **across pool instances: sd 0.1532**

**So roughly a tenth of the instance-level signal is the criterion and the rest is the prompt.** For
`coval_full` this decomposition is unavailable in principle — each criterion appears on exactly one
prompt (D3), so criterion and prompt are perfectly confounded and its 95% signal **cannot be
attributed to criterion text**. The round says so instead of estimating it.

## ⭐ AND THE POOL'S ADVANTAGE IS NOT A MINORITY

**16 of 16** pool criteria individually exceed `coval_full`'s mean accuracy of 0.4805 — the weakest,
criterion 12, is 0.5048 [0.4944, 0.5154]; the strongest, criterion 0, is 0.5585 [0.5491, 0.5683].
Top-4 mean 0.5526, bottom-4 0.5133. **The generic pool beats the rubric everywhere, not through a few
strong criteria.**

## ⛔ CHECK #401 KILLED R798's PROPOSED DESIGN — AND ITS OWN ILLUSTRATIVE NUMBER WAS WRONG

R798's NEXT proposed sorting instances by their own accuracy and reporting the share below chance.
The check showed one instance is **5.73 non-tied pairs × 16.1 annotators = 92 draws**, SE ≈ 0.0521,
so ranking noisy estimates measures the noise. That killed the design correctly.

⚠ **But the check's illustration — "if every criterion were truly at 0.4805 the observed share below
0.5 would be 0.646" — described a world this data refutes.** It assumed zero true spread; the
measured signal sd is **0.1760**. The honest numbers:

| | naive share below 0.5 | deconvolved |
|---|---:|---:|
| `coval_full` | 0.509 | **0.544** |
| `genericpool16` | 0.388 | **0.416** |

**The deconvolution raises the share rather than deflating it.** The design was still wrong for the
reason given — an unranked estimate is not a ranking — but *my own worked example was an artifact of
the uniform world I was arguing against.*

## ⛔⛔ AND THE OBJECT CHECK CAUGHT A DEFECT IN R798, NOT IN THIS ROUND

The first run exited 2: `full` accuracy reproduced at **0.4795** against R798's committed **0.4805**.
Diagnosed at the object — **R798 printed its LEVELS as instance-weighted means while computing its
GAPS from prompt-weighted ones**, two aggregations in one table row.

| | instance-weighted | prompt-weighted |
|---|---:|---:|
| `full` accuracy | **0.4805** | 0.4795 |
| gap to pool | **+0.0527** | **+0.0538** |

**The substance is unaffected** — same sign, both resolved — but the columns were not on one footing.
R798's README now carries the correction, and this round reports both.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | R798's committed accuracies reproduced to 1e-9 **once the right aggregation was used** | PASS after the defect above was located |
| PLACEBO | an instance's accuracy against itself: r **1.000000000000** | PASS |
| POSITIVE | planted true sd **0.020 → recovered 0.0200** (ratio 1.00) · **0.080 → 0.0791** (0.99) | PASS — band at both ends, and the two differ |
| NEGATIVE | zero-true-spread synthetic on this data's own annotator structure: `full` r **+0.0080**, pool **−0.0060** | PASS — this is what no signal looks like |
| NOISE FLOOR | analytic binomial SE **0.0521** vs measured half-to-half sd/2 — `full` **0.0578**, pool **0.0609** | the binomial model understates it, as D1's assumption warned |

## MULTIPLICITY

**18 tests** — 2 reliabilities + 16 per-criterion — BH at q = 0.05: **18 survive, 0 do not.**

## WHAT DIED

- **"uniform"** — World B is out: the split-half reliability is +0.82 against a control of +0.008.
- **the reading that the spread is about criteria** — for the pool, where it is measurable, criterion
  spread is **0.0157** against instance spread **0.1532**.
- **check #401's own worked example (0.646)** — it assumed the uniform world the data refutes.
- **R798's table as a single-unit object** — levels instance-weighted, gaps prompt-weighted.

## WHAT SURVIVES

R798's gap, both ways (+0.0527 instance-weighted, +0.0538 prompt-weighted), and R797's aggregate.
And the answer to "which criteria are bad" is now **provably unavailable for `coval_full` from this
release** rather than merely unmeasured.

## SCOPE

968 prompts × all annotators (median 16) · 14,979 `coval_full` and 15,482 pool instances with at
least one non-tied pair · instrument per-instance accuracy on non-tied pairs · split halves over
ANNOTATORS only, so prompt variation sits inside "signal" (D4) · NBOOT 1,200 · first release, home
judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| any individual `coval_full` criterion's quality | that criterion on more than one prompt (D3); the release gives each exactly one |
| separating criterion from prompt for the rubric | the same rubric criterion applied to different prompts — only the generic pool provides it |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

The decomposition now has a shape: for the generic pool, criterion identity contributes **sd 0.0157**
while the instance-level signal is **sd 0.1532**, so the large reliable variation is about **which
prompt and responses a criterion faces**, not which criterion it is. Computed by this round's
`run.py`, all 16 pool criteria beat the rubric's mean, so the rubric's deficit is not a few bad
criteria either. The step is to take that prompt-level variation seriously as the object: measure,
per prompt, whether the rubric's deficit against the pool is concentrated in a minority of prompts or
spread across them — a question that IS identified, because both pools are observed on every one of
the 968.
