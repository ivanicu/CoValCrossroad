# R820 · the null-degeneracy detector — validated on ten labelled cases, and installed

`run.py` · `PREREGISTRATION.txt` · `results/detector_validation.json` · 10 labelled cases × 2 rules ×
6 thresholds · **WORLD A** · two hash seeds byte-identical, md5 `5417140e491d138179c74e2ee28bfc9e`

## THE DECISION THIS MAKES SAFE

**Five degenerate negative controls shipped this session and every one was caught by its output
looking wrong, never by a check. One of the two candidate rules works; the other must not be used.**

| rule | fires on BROKEN | fires on REPAIRED | verdict |
|---|---:|---:|---|
| **R1 · zero spread** | **4 / 5** | **0 / 5** | **install** |
| R2 · overshoot | 2 / 5 | **2 / 5** | **unusable** |

**R1 separates cleanly at every threshold from 0 to 1e-3** and breaks at 1e-2 (where it takes one
repaired case). ⭐ **R2 was predicted to fail before the run** — D1 said it cannot separate R816's
bad null from R819's good one, because both have |null| > |observation| with the same sign. It
false-positives on **two** passing controls, R810's and R819's.

## ⛔ CHECK #422 · A COMMIT-TIME GATE IS STRUCTURALLY BLIND TO THIS CLASS

R819 proposed adding this to the seven existing gates. **The committed artifacts do not contain the
degenerate nulls** — each was repaired before anything was written, so every `results/*.json` holds
the *repaired* value. Only 9 recent rounds record a null field at all, under six inconsistent names
(`null_lo/hi`, `null_mean/max`, `null_sd`, `null_spearman`, `null_floor`, `label_null`).

**So the detector cannot be retrospective. It is a runtime assertion**, called where the null is
computed rather than where it is reported.

## ⛔⛔ THE TRANSCRIPTION CHECK FIRED ON 6 OF 10 — AND IT WAS RIGHT

§4: *a control validated only against cases you invented is validated against your imagination.*
These cases are transcriptions from committed files, so the round verifies **every value appears
literally in the file it cites**, before any rule is evaluated. On the first run:

> **verified 4 of 10 · missing 6 → exit 2**

The cause was mundane and total: my table used **ASCII hyphens where the committed files use the
Unicode minus U+2212**, and cited `RETRACTIONS.md` for values that live only in a round README.
Every literal was then located at its source and re-verified.

## ⛔⛔ AND I MANUFACTURED THE SIGNATURE ON R816 BY ENCODING IT AS A POINT

The corrected run first reported **R1 firing on 5 of 5** — better than R819 predicted. That was my
own encoding: R816's broken null was **not** degenerate in spread. Its output was
`−0.870 [−1.283, −0.416]` over 200 draws; only its **centre** was wrong, overshooting the
observation of −0.553. **I recorded a reported centre as a zero-width interval, which manufactured
exactly the signature R1 detects.**

Corrected to its real interval, R1 does not fire on R816 and the count returns to **4 / 5 — the
number R819 predicted**. ⚠ *A validation set is an instrument too, and encoding a point estimate as
an interval is the same class of error as the nulls it was built to catch.*

## ⭐ THE TEN CASES

| round | label | null | observed | R1 | R2 |
|---|---|---|---:|---|---|
| R809 | BROKEN | [−0.1317, −0.1317] | −0.1317 | **FIRES** | — |
| R810 | BROKEN | [+0.0156, +0.0156] | +0.0116 | **FIRES** | FIRES |
| R813 | BROKEN | [+0.0099, +0.0099] | +0.0099 | **FIRES** | — |
| R816 | BROKEN | [−1.2830, −0.4160] | −0.5530 | — | FIRES |
| R819 | BROKEN | [+0.5162, +0.5162] | +0.5162 | **FIRES** | — |
| R809 | REPAIRED | [−0.1317, +0.1021] | −0.1317 | — | — |
| R810 | REPAIRED | [−0.1325, −0.1107] | +0.0116 | — | **FIRES** ⛔ |
| R813 | REPAIRED | [+0.0090, +0.0104] | +0.0099 | — | — |
| R816 | REPAIRED | [−0.0910, +0.0860] | +0.3680 | — | — |
| R819 | REPAIRED | [+1.0591, +1.2287] | +0.0617 | — | **FIRES** ⛔ |

⭐ **R813's repaired null is the hard case** — a weak pass whose centre (0.0097) sits within one sd
of the observation (0.0099). D3 put it in the set for that reason, and **R1 correctly stays silent**,
because R1 never references the observation at all. That is why it is the more robust rule.

## E3 · THE THRESHOLD SWEEP

| eps | BROKEN | REPAIRED | |
|---|---:|---:|---|
| 0 · 1e-9 · 1e-6 · 1e-4 · 1e-3 | 4/5 | 0/5 | separates |
| 1e-2 | 4/5 | **1/5** | does **not** separate |

**Widest safe threshold: 1e-3.** The installed default is **1e-9**, six orders inside it.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | all ten literals found in the files they cite | PASS **after two repairs** |
| PLACEBO | a null with genuine spread centred on zero: R1 silent, R2 silent | PASS |
| POSITIVE | spread ladder at eps=1e-6 — fires at sd **0** and **1e-9**, silent at **1e-6**, **1e-3**, **1e-2** | PASS — monotone and can fail |
| NEGATIVE | R819's own **repaired** six-member null [+1.0591, +1.2287]: silent | PASS |
| NOISE FLOOR | the detector is **deterministic** given its inputs — it has no spread, and inventing one would be the arithmetic trap | stated, not fabricated |

## E4 · INSTALLED

`assurance/null_is_informative.py`, exercised independently of the round:

```
good null                      -> {'spread': 0.2, 'centre': 3.3e-18, 'sd': 0.0589}
all-zero                       -> raised: DEGENERATE NULL. spread 0.000e+00 <= 1e-09 over 50 draws
point mass on the observation  -> raised: DEGENERATE NULL. spread 0.000e+00 <= 1e-09 over 50 draws
one draw                       -> raised: a null needs >=2 draws, got 1
```

Its message names the diagnosis rather than the symptom: *"a null with no variation destroyed
nothing — the permutation is a no-op on this statistic. Check whether the statistic is invariant to
it BY CONSTRUCTION."* That sentence is the one thing four of these five rounds needed and none had.

## WHAT DIED

- **R2, the overshoot rule** — it false-positives on two passing controls, exactly as D1 predicted.
- **"a commit-time gate would catch these"** — the artifacts never held the broken values.
- **my own transcription** (6 of 10), and **my own encoding of R816** (which inflated 4/5 to 5/5).

## WHAT SURVIVES — AND THIS ROUND ADDS

A validated instrument with a stated false-positive rate of **0 of 5** on this set, a threshold with
six orders of headroom, and an honest bound: **it catches the zero-spread signature and not the
overshoot one.** R816's failure mode remains undetected, and the rule that would detect it costs
more in false alarms than it buys.

## SCOPE

10 labelled cases — 5 broken and 5 repaired negative controls from R809, R810, R813, R816, R819 —
transcribed from `RETRACTIONS.md` and `R819/README.md`, each verified literally at its source ·
2 rules × 6 thresholds · ⚠ **n = 10, and no rate beyond this set is claimed** · the detector is
deterministic.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| a retrospective gate over past rounds | artifacts containing the broken nulls; **they contain only the repaired ones** — measured, 9 rounds record a null field under 6 different names |
| catching R816's overshoot | a rule keyed on the null's centre; the only such rule false-positives on 2 of 5 passing controls — **measured, not assumed** |
| a validation set larger than 10 | more degenerate controls, which would mean more shipped defects; the set grows only by failing again |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The detector is installed and bounded: it catches the zero-spread signature at 4 of 5 with no false
alarms on this set, and does not catch R816's overshoot. Computed by this round's `run.py`, the
widest separating threshold is **1e-3** against an installed default of **1e-9**.

What it cannot do is make a round *call* it. Five rounds computed a null and declared it in five
different shapes — `results/*.json` carries **six field names for the same object across nine
rounds**, measured in CHECK #422. The step is the schema, not another rule: require each round's
artifact to carry `null: {draws, centre, spread, observed, statistic}` under one name, and add a
commit-time gate that fails when a round reports a negative control in prose without emitting that
block. That makes the runtime assertion auditable after the fact — the one property this round's
validation set had to be hand-built to supply, at a cost of six failed transcriptions.
