# Arc E05·A08 — triple-blind

**The decision this makes safe:** *is the E05 formulation a property of the object, or of the one
person who designed every measurement in it?*

## Why this arc exists

`realstat` §2.5 says **independently replicated** stops being structurally impossible: write one
implementation yourself, then dispatch **two clean-context agents told the QUESTION and never the
ALGORITHM**, at different seeds.

**E04 did this ten times** — `R125`, `R126`, `R129`, `R131`, `R134` each ship an `independent_A.py`
and an `independent_B.py`. **E05 has done it zero times.** Fourteen rounds, R220–R233, every one a
single implementation by the same author, several of them listing *independently replicated* in
their own register as impossible — **while the machinery sat in the previous epoch of the same
repository.**

That is the same failure class as `RETRACTIONS.md` **Entry 96**: an impossibility asserted while the
counter-artifact is in the repo. Entry 96 was about a candidate set. This is about a method.

## The three arms

| arm | who | seed | what they were given |
|---|---|---|---|
| **R231** | me | — | the whole context; my answer is *class agreement, and it depends on Q* |
| **R234** | clean-context agent A | 11 | the question in plain words, the data schema, `realstat`, a list of files they may not open |
| **R235** | clean-context agent B | 29 | the same, plus the alternate-judge tensors |

**Neither agent was given:** the estimand, the statistic, the aggregation, the controls, my numbers,
or my conclusion. *Designing the statistic is the task.* Both are blocked from
`E05_the_space_of_compilers/`, `RETRACTIONS.md`, `NORTH_STAR.md`, `EAR.md`, `README.md` and
`PREREGISTRATION.md` — every document that contains an answer.

## How the result will be read — fixed before it arrives

- **all three agree** → design-independent, the strongest form available at this site
- **agree on sign, differ on size** → the effect is real and the estimand is contested; **the spread
  is the finding**, not the mean
- **disagree on sign** → **the framing is the finding.** Do not adjudicate by picking the design I
  like; find the assumption they differ on and test *that*

⚠ **The three will not be averaged.** Averaging divergent designs hides the disagreement, which is
the informative part.

## What this cannot do

A second team is still a second team. Three designs from one model family test **framing**, not
**population** — and if all three share a blind spot native to the weights they were sampled from,
convergence would look identical to correctness. That is the register entry that does not close
here, and it is the reason §2.5 says this makes `independently replicated` *possible*, not *done*.
