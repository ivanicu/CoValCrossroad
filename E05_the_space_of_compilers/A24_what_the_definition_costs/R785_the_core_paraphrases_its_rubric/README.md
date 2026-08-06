# R785 · the released core is a paraphrase of its rubric, not a subset — and `gen` is neither

`run.py` · `PREREGISTRATION.txt` · `results/rubric_affinity.json` · 986 released conversations ·
968 joined · **WORLD A**

## THE DECISION THIS MAKES SAFE

**The relation between the released core and its rubric has a name now, and it is neither
"containment" nor "independence".** The clause *"drawn from a rubric"* was retracted because a
conversation-only core is admissible — correctly, since only **1 of 986** cores is entirely inside its
rubric and **6.68%** of core criteria appear in it verbatim. But the content relation is strong:
**best-match token Jaccard 0.4951 against a cross-conversation null of 0.0555**, a difference of
**+0.4396 against an MDE of 0.0145 — thirty times — with 986 of 986 records in the same direction.**

## ⭐ AND IT SEPARATES THE ARM THAT PASSES CLAUSE ② FROM THE ONE THAT FAILS

| object | tok | verbatim | affinity | null | own − null | MDE | |
|---|---:|---:|---:|---:|---:|---:|---|
| `coval_core` | 3 | 0.0668 | 0.4938 | 0.0836 | **+0.4103** | 0.0139 | RESOLVES |
| `gen` | 3 | 0.0000 | 0.1410 | 0.1028 | +0.0382 | 0.0044 | RESOLVES |
| **core − gen** | 3 | | | | **+0.3535** | 0.0149 | **RESOLVES** |
| `coval_core` | 4 | 0.0668 | 0.4951 | 0.0555 | **+0.4396** | 0.0145 | RESOLVES |
| `gen` | 4 | **0.0000** | 0.0865 | 0.0356 | +0.0508 | 0.0048 | RESOLVES |
| **core − gen** | 4 | | | | **+0.4090** | 0.0154 | **RESOLVES** |
| `coval_core` | 5 | 0.0668 | 0.5014 | 0.0465 | **+0.4549** | 0.0147 | RESOLVES |
| `gen` | 5 | 0.0000 | 0.0867 | 0.0319 | +0.0549 | 0.0053 | RESOLVES |
| **core − gen** | 5 | | | | **+0.4150** | 0.0157 | **RESOLVES** |

**The discriminating cell resolves at all three tokenisations, same sign, +0.35 to +0.42.**
`coval_core`, which clears clause ② at q_resolved **0.9978** (R782), paraphrases its rubric.
`gen`, which fails at **0.0396**, sits at **0.0865** — barely above its own null of 0.0356 — and
shares **exactly zero** criteria with the rubric verbatim.

## ⚠ AND THE SCOPE THAT MATTERS MORE THAN THE NUMBER

**E3 has n = 2 arms**, and a correlation is undefined at n = 2, so none was computed. The pair is
reported as a pair:

| arm | rubric affinity | q_resolved (R782) |
|---|---:|---:|
| `coval_core` | 0.4951 | 0.9978 |
| `gen` | 0.0865 | 0.0396 |

**Two arms differing on two axes in the same direction is one bit of evidence, not a mechanism.**
Only arms whose criterion *texts* exist can be placed on this axis, and R782 established that
`coval_core` has no `core_*.json` — its texts live in the release. Every other scored arm is
`sat`-indices only. **So the population for E3 is 2, and it is stated rather than smoothed.**

⚠ The hypothesis this makes available and does not establish: **clause ② may be scoring rubric
affinity rather than quality.** With n = 2 that is a direction to test, not a finding.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 986 records with both fields · join ranking→release **exact 968, 0 unmatched, 0 ambiguous** (R468, rebuilt in R783) | PASS, else exit 2 |
| PLACEBO | a rubric against itself: **1.000000** | PASS — **after the fix below** |
| NULL | own rubric **0.4951** vs another conversation's **0.0555**, difference **+0.4396** [+0.4293, +0.4499], MDE 0.0145; **986 of 986** records own > other | RESOLVES |
| NULL-TOPIC | the registered confound: against the *nearest-topic* other rubric, **0.0819** vs own **0.4832**, difference **+0.4013**, MDE 0.0363 (n=150) | RESOLVES — shared topic does not explain it |
| POSITIVE | delete 0% → **1.0000** · 25% → 0.7536 · 50% → 0.4992 · 75% → 0.2523 | PASS, monotone, band computed at both ends |
| SWEEP | token length {3, 4, 5}, whole curve above | no tokenisation kills it |
| SHAM | ⛔ **not built** — D3: the ingredient is *being the same conversation*, and removing it **is** the NULL | declined in the preregistration, second round running |

### ⛔ THE FIRST RUN WAS **UNVERIFIED**, AND THE PLACEBO IS WHY

A rubric compared to itself returned **0.999848**, not 1.0, and the POSITIVE's floor returned 0.9998
rather than exactly 1.0. Both trace to one instrument defect: **Jaccard is undefined on two empty
sets, and my guard `max(len(a|b), 1)` turned 0/0 into 0** — so a criterion whose token set is empty
scored **zero against itself**.

**Three of 19,147 release criteria tokenise to nothing, and all three are junk**: `'Lwa'`, a bare
UUID `'d6886713-34db-4490-9aa8-6ac8a9e9f718'`, and an empty string. Two empty sets are identical, so
the value is **1.0**. That is a degenerate being *defined*, not a threshold being loosened — and the
control that caught it was doing precisely its job, which is the good case of §4's *the control fails
for its own reasons*: here the control was right and the instrument was wrong.

## WHAT DIED

- **"the core shares nothing with its rubric"** — true verbatim (6.68%, 792 of 986 at zero) and
  **false as content** (0.4951 against a 0.0555 null). **D4 in force: an exact-match instrument
  measures string identity; the claim was about content, and the two got different sentences.**
- **the first run's verdict**, killed by its own placebo.
- **R784's proposed gate**, declined on arithmetic: every scope line in 780+ READMEs says "968", so
  the only implementable form is a freeze, and the frozen ones stay wrong.

## WHAT SURVIVES

A named relation the definition does not have a clause for: **the released core paraphrases its
rubric at nine times the cross-conversation baseline while containing almost none of it.**

## SCOPE

population 986 released conversations, 968 joined · instrument verbatim set intersection and token
Jaccard at lengths {3,4,5} · baseline the cross-conversation pairing, and the nearest-topic pairing
for the confound · regime first release, this tree_sha. **E3's population is 2 arms.**

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| semantic rather than lexical similarity | an embedding model; a paraphrase sharing no vocabulary is invisible to a token measure, so 0.4951 is a **lower** bound on relatedness |
| whether the core was DERIVED from the rubric, or both from the conversation | the generator's inputs, off-repository (R605). Affinity is compatible with either and the round claims affinity only |
| rubric affinity for arms with no criterion text | `coval_core` has no `core_*.json` (R782); arms scored from sat indices alone cannot be placed on this axis |
| a correlation between affinity and clause-② standing | more than 2 arms with criterion text |

## NEXT

The hypothesis is sharp and its population is the obstacle: **clause ② may be scoring rubric affinity
rather than quality**, and only 2 arms currently have criterion text to test it on. But affinity is
computable for any arm built from the rubric — the `random_k*`, `topw_*`, `topabs`, `topvar` families
draw their criteria from `core_full.json`, so their texts exist and their affinity is **1.0 by
construction**, which makes them useless as a contrast and is worth stating rather than discovering.
The arms that would extend the axis are the ones built *without* the rubric, and by this round's
`run.py` there are exactly two of those with text. **So the next step is not another measurement on
this site**: it is to record in the definition that clause ②'s discriminating power has been shown to
covary with rubric affinity on the two arms where both quantities are measurable — a count computed by
this round's `run.py` and equal to 2 — and to name a second conversation-only generator as the thing
that would settle it.
