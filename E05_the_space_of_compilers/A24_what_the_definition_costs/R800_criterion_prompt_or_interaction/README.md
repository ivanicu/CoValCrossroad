# R800 · criterion identity is 0.9% of the variance; the prompt is 67%

`run.py` · `PREREGISTRATION.txt` · `results/components.json` · 16 criteria × 968 prompts, fully
crossed · **WORLD B** · two hash seeds byte-identical, md5 `29f5cdd028974135d044abe2ecac3dba`

## THE DECISION THIS MAKES SAFE

**On the only fully-crossed grid this release contains, which criterion it is explains almost
nothing.**

| component | variance | sd | share |
|---|---:|---:|---:|
| **criterion** | 0.000237 | 0.0154 | **0.9%** |
| **prompt** | **0.018197** | **0.1349** | **67.0%** |
| interaction (criterion × prompt) | 0.004965 | 0.0705 | 18.3% |
| annotator noise | 0.003773 | 0.0614 | 13.9% |
| total | 0.027171 | | |

**A criterion is not globally good, and it is not even prompt-specifically good** — the interaction is
18.3% against the prompt's 67.0%. **Which prompt and responses a criterion faces determines nearly
everything about whether it predicts the humans.**

⚠ **D2 held, as stated in advance**: R799's across-criteria sd of 0.0157 was an *upper bound* carrying
`(s2_int + s2_e)/968`; corrected it is **0.0154** — a small correction, predicted before the run so a
small correction could not be reported as a discovery.

## ⭐ AND THE DEFICIT: THE RUBRIC LOSES ON THREE PROMPTS IN FOUR

| | |
|---|---|
| deficit (`coval_full` − pool), mean | **−0.0538** |
| observed sd | 0.0885 = noise **0.0309** + signal **0.0829** |
| share of prompts where the rubric loses — **naive** | 0.733 |
| — **deconvolved** | **0.743** |

## ⛔⛔ AND D3 WAS LOAD-BEARING — THE WRONG NOISE MODEL WOULD HAVE ERASED THE SIGNAL

The deficit is **paired**: both pools are scored by the same annotators on the same responses, so
their noise partially cancels. Measured **on the difference**, the noise sd is **0.0309**. Assembled
from each pool's own — the natural mistake — it would have been **0.0869**, nearly 3× larger and
almost the entire observed spread of 0.0885. **That version would have concluded the per-prompt
deficit is all noise.** D3 was registered before the run for exactly this.

## ⛔ AND R799's OWN NEXT PROPOSED THE DESIGN R799 KILLED

R799 diagnosed that ranking 14,979 noisy per-instance estimates and reading a share off the ranking
measures the noise — then closed by asking to rank **968 noisy per-prompt estimates** and read a
share off *that*. The same error, one aggregation level up, **one round after diagnosing it**. Check
#402 caught it, and the identified version is what this round reports (naive 0.733 against
deconvolved 0.743 — here the bias is small, but it was not knowable in advance).

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | instance sd **0.1648692616** and across-criteria sd **0.0156900510**, both against R799's committed values to 1e-9 | PASS, else exit 2 |
| PLACEBO | a cell against itself: **0.0e+00** | PASS |
| POSITIVE | **interaction-heavy** planted c/p/i sd 0.01/0.03/0.12 → recovered **0.012/0.030/0.118**; **prompt-heavy** 0.01/0.12/0.03 → **0.013/0.123/0.027** | PASS — band at both ends, both mixes distinguished in the right direction |
| NEGATIVE | criterion labels shuffled **within** each prompt: `s2_criterion` **0.000237 → 0.000004**, total unchanged to **3.5e-18** | PASS |
| CONFOUND | `full` carries 4–39 criteria (mean 15.48); size-matched deficit **−0.0543** against raw **−0.0538** | worth 0.0006 — negligible |
| NOISE FLOOR | per-cell annotator split-half **s2_e 0.003773** (sd 0.0614); on the difference **0.0309** | measured both ways |

## MULTIPLICITY

The four variance components are a **decomposition** — they sum to the total by construction — so they
are reported whole rather than tested individually, and that distinction is stated rather than
blurred. The deficit estimates and the two shares are the only tested quantities.

## WHAT DIED

- **World A (interaction dominates)** — 18.3% against the prompt's 67.0%.
- **"criteria differ in quality" as a useful statement** — 0.9% of the variance, even where it is
  measurable.
- **R799's NEXT as posed** — it repeated the design R799 had just killed.
- **the unpaired noise model for the deficit**, which would have made the signal vanish.

## WHAT SURVIVES

R799's numbers, reproduced to 1e-9, and its qualitative reading — most reliable variation is not the
criterion — now with the interaction separated out and a number attached. And the deficit itself:
`coval_full` loses to a generic 16-criterion pool on **74%** of prompts.

## SCOPE

968 prompts × 16 pool criteria, fully crossed (15,482 of 15,488 cells present) × all annotators
(median 16) · instrument per-cell accuracy on non-tied pairs · variance components by the marginal
identities on a crossed grid (D1) with the noise measured by annotator split-half · first release,
home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| the same decomposition for `coval_full` | its criteria on more than one prompt; the release gives each exactly one (R799 D3) |
| why a prompt is hard for every criterion | the prompts' and responses' content — the construct wall (`corebench/score.py:34`) |
| independently replicated | a second designer; the session prompt forbids agents |
| cross-release | a second values-annotation release |

## NEXT

The variance is now located: **67.0% prompt, 18.3% interaction, 13.9% noise, 0.9% criterion**, and the
rubric loses on 74% of prompts by a mean of −0.0538. Computed by this round's `run.py`, the prompt
term is 77× the criterion term. So a definition that specifies *which criteria* a core contains is
specifying the smallest component of what determines whether it predicts humans. The step is to write
that into the formulation: state clause ② over the quantity that actually varies — **per-prompt
predictive standing** — and check whether a core selected to be robust across prompts differs from one
selected to maximise the pooled mean — which is the objective `corebench/select_core.py`
implements for `topw_k`, `topvar_k`, `indep_k`, `greedy_k` and the oracle alike.
