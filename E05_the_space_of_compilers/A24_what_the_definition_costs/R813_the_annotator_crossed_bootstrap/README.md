# R813 · the intervals are 14–30% too narrow, and nothing breaks

`run.py` · `PREREGISTRATION.txt` · `results/crossed_bootstrap.json` · 968 prompts × 964 parity-0
annotators × 4 headlines × 3 resampling schemes · **WORLD C** · two hash seeds byte-identical,
md5 `0ff2484996f9b496ad84d46fd448756f`

## THE DECISION THIS MAKES SAFE

**Annotators are crossed with prompts and this arc has never resampled them. Correcting that widens
every interval by 14–30% and costs no verdict.**

| headline | point | prompt CI | annotator CI | **crossed CI** | **DE** |
|---|---:|---|---|---|---:|
| **H1** R805 `oracle_k4_fit1` − `genericpool16` | +0.0553 | [+0.0456, +0.0653] | [+0.0506, +0.0605] | **[+0.0435, +0.0666]** | **1.17** |
| **H2** R810 fitted − `topw_k12` at k=12 | +0.0116 | [+0.0069, +0.0164] | [+0.0093, +0.0143] | **[+0.0054, +0.0178]** | **1.30** |
| **H3** R811 rule effect at k=12 | +0.0419 | [+0.0356, +0.0482] | [+0.0393, +0.0447] | **[+0.0346, +0.0493]** | **1.17** |
| **H4** R811 source effect at k=12 | +0.0373 | [+0.0272, +0.0483] | [+0.0319, +0.0417] | **[+0.0249, +0.0489]** | **1.14** |

**All four remain resolved.** The most at-risk — H2, the arc's smallest surviving effect — widens
from a half-width of 0.0047 to 0.0062 and still excludes zero.

## ⛔ CHECK #415 KILLED R812's NEXT TWICE OVER

R812 closed by proposing a prompt-level cluster bootstrap.

1. **Every round already bootstraps prompts** — `rng.integers(0, N, (NBOOT, N))` is in each `run.py`.
   The NEXT asked for what was already being done.
2. **There is no coarser grouping.** Measured: the release carries **1,078 conversations for 1,078
   prompts, max 1 prompt each, 0 conversations spanning more than one.**

⭐ **But the same check found the real dependence, and it is not over prompts.** **1,012 annotators,
each judging a median of 19 prompts** across the release; restricted to parity-0, **964 annotators at
a median of 8 prompts each, max 20.** Every interval this arc quotes holds that panel fixed.

## ⭐ THE INSTRUMENT WORKS AND THE DATA HAS LITTLE TO FIND — BOTH CONTROLS SAY SO, TOGETHER

| dose *g* of a planted annotator-specific offset | annotator width | prompt width |
|---:|---:|---:|
| 0.00 | 0.0096 | 0.0197 |
| 0.05 | 0.0120 | 0.0195 |
| 0.15 | **0.0228** | 0.0199 |

**The annotator scheme responds monotonically to planted annotator structure while the prompt scheme
does not move (ratio 1.01).** So the instrument can see annotator-level dependence.

⚠ **And the negative control says the real data has almost none.** Reassigning annotator ids at
random — destroying the crossing entirely — gives width **0.0097 ± 0.0007** against the real
**0.0099**. It passes the pre-registered criterion (mean below real) **by 0.0002 against an sd of
0.0007**, which the noise does not support. **I am reporting that as a weak pass, not upgrading it.**

**Read together the two controls are more informative than either alone**: the scheme *can* detect
annotator structure, and finds so little of it that breaking the crossing barely changes anything.
**That is why the design effect is only 1.14–1.30** — it comes mostly from resampling a second axis
at all, not from real annotator dependence.

## ⛔ THREE OBJECT-CHECK FAILURES BEFORE THE ROUND COULD RUN, EACH LOCALISING A DIFFERENT DEFECT

The object check exited 2 twice and localised both:

- **First run**: H1 reproduced exactly, H2/H3/H4 did not. **R810 and R811 restrict to the 734-prompt
  common intersection** (prompts attaining nominal k at every k) while R805 uses all 968. The
  population was wrong for three of four headlines.
- **Second run**: H1/H2 exact, H3/H4 off by **0.0045**. **R811 averages `random_k` over three
  committed seeds**; I had used s0 alone.
- **Third, in a control rather than the object**: the negative control printed a width **identical**
  to the real one with an sd of **exactly 0.0000**. `rows_a` is local to `main()`, so
  `globals()["rows_a"] = fake` set a name the closures never read — **the reassignment did nothing.**
  This is the **third round running** (R809, R810, R813) whose negative control returned a degenerate
  output, and the tell has been the same every time: **a zero-width or exactly-equal result does not
  look like a failure, it looks like precision.**

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | all four committed points reproduced: **+0.0553 · +0.0116 · +0.0419 · +0.0373** | PASS after two repairs |
| PLACEBO | an arm minus **itself** under the crossed scheme, max \|value\| over 200 draws: **0.0e+00** | PASS — zero width everywhere |
| POSITIVE | planted annotator offset, dose 0 → 0.05 → 0.15: annotator width **0.0096 → 0.0120 → 0.0228**, monotone; prompt width flat at ratio **1.01** | PASS, and it does not fire at g=0 |
| NEGATIVE | annotator ids reassigned at random, 20 draws: **0.0097 ± 0.0007** vs real **0.0099** | ⚠ **weak pass** — the separation is inside its own noise |
| D1 | the crossed interval is never narrower than the prompt interval | PASS — a violation would have meant the code was wrong |
| DROPPED | prompts left with zero annotators: **2.6 / 968 (0.3%)** per draw | well under the 10% stopping rule |
| NOISE FLOOR | crossed width across three seeds: H1 sd **0.0004**, H2 sd **0.0009** | measured |

## WHAT DIED

- **R812's NEXT, in both of its parts** — the prompt bootstrap already existed, and no coarser
  grouping does.
- **"the intervals are fine as quoted"** — they are 14–30% too narrow.
- **"the intervals are badly wrong"** — no verdict changes, and H2 survives at its widest.

## WHAT SURVIVES — AND THIS ROUND ADDS

Every headline, at a wider and better-specified interval, plus the design effect itself: a number
this arc can attach to any future claim rather than rediscovering the question.

## SCOPE

968 prompts (H1) and the 734-prompt common intersection (H2–H4) × 964 parity-0 annotators ×
3 resampling schemes × NBOOT 1,200 · annotator identity recovered from
`comparisons.jsonl`'s `metadata.assessments[].annotator_id`, which `load_targets()` discards ·
first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a prompt-level cluster bootstrap | a grouping over prompts; the release has **1,078 conversations for 1,078 prompts, max 1 each** — **checked and measured**, not assumed |
| a variance decomposition into prompt and annotator components | a hierarchical model rather than a resampling scheme; the design effect bounds the total without attributing it |
| the same correction on the second release | a judge pass over `utterances.jsonl`'s 68,371 utterances — **checked** |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The design effect is measured at **1.14–1.30** and every headline survives at its widest interval, so
the resampling question is closed for this arc. What the negative control exposed instead is a
sharper target: it separated by **0.0002 against an sd of 0.0007**, meaning the annotator panel
carries almost no shared error at the level A2 aggregates over. That is surprising given R793's
`CEIL_H` of 0.551880 — annotators disagree with each other a great deal, yet their *errors* appear
close to independent. Those two facts are in tension, and the step is to test it directly: estimate
the intraclass correlation of a single annotator's per-prompt agreement across the prompts they
judge, and compare it against the disagreement rate `CEIL_H` already commits to. If the ICC is near
zero while pairwise agreement is 0.55, then annotator disagreement is prompt-driven rather than
rater-driven, and clause ③'s whole framing — which treats annotators as the unit held out — is
pointed at the wrong source of variance.
