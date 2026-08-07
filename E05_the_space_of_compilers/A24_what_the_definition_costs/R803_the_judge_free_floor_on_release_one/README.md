# R803 · the judge-free floor is 0.4557 and all 27 arms clear it — the scale is earned

`run.py` · `PREREGISTRATION.txt` · `results/judge_free_floor.json` · 968 prompts × 4 responses × all
annotators × 27 arms · **WORLD A** · two hash seeds byte-identical, md5 `801f4a8b2d0171b17d52bb809f4d703d`

## THE DECISION THIS MAKES SAFE

**Every committed A2 in this campaign sits above a baseline that needs no judge, no rubric and no
criteria — and until this round nobody had drawn it on release one.**

| | A2 |
|---|---:|
| **the judge-free floor** — characters, longer-is-better | **0.4557** |
| weakest arm (`gen_sham`) | 0.4828 — **+0.0271 [+0.0134, +0.0409]**, RESOLVED |
| `coval_core` | 0.5665 — **+0.1108 [+0.0989, +0.1233]**, RESOLVED |
| `oracle_k4` | 0.6283 — **+0.1726 [+0.1610, +0.1844]**, RESOLVED |

**27 of 27 arms beat the floor resolvedly, and 27 of 27 survive BH.** The floor sits **below every
arm in the population, including the shams** — so response length is a *weaker* predictor of the human
ordering than random criteria are.

## ⭐ THE WHOLE PREDICTOR CURVE, NOT THE WINNER

A max over six predictors is a selection, so all six are reported:

| predictor | longer-is-better | shorter-is-better |
|---|---:|---:|
| characters | **0.4557** | 0.4023 |
| whitespace tokens | 0.4351 | 0.4063 |
| position index | 0.4182 | 0.4421 |

D2 registered that the sign was **not** forced — humans could have preferred concision. They prefer
length, weakly, and the best judge-free reading is still 0.0271 below the worst arm.

## ⭐ AND THE ARMS ARE NOT LENGTH IN DISGUISE

D4's confound: if longer responses satisfy more criteria, an arm's A2 could be length wearing a
rubric. Regressing each arm's per-prompt A2 on the floor's:

> **slope mean +0.1211, range [+0.0632, +0.1738]** · `coval_core` **+0.1005**

The arms are largely independent of the length signal. ⚠ **And the residual MEAN is 0 by
construction** — OLS forces it — so the informative quantity is the slope, not the residual mean the
script also prints. ⚠ The residual is in any case a **lower** bound, since partialling removes shared
prompt difficulty along with length.

## CONTROLS — AND THE PLACEBO LANDED EXACTLY ON ITS DERIVED VALUE

| control | returned | |
|---|---|---|
| OBJECT | `coval_core` recomputed **from raw response text + annotators**: **0.5664774812** vs R789's committed **0.5664774812** | PASS, else exit 2 |
| **PLACEBO** | a **constant** predictor (all four responses equal → every sign 0) gives A2 **0.1397355039**; the human tie rate is **0.1397355039** | **PASS — identical to 10 decimals, computed not assumed** |
| POSITIVE | `oracle_k4` − floor **+0.1726 [+0.1610, +0.1844]** | PASS — band computed at both ends: placebo **0.1397** → oracle **0.6283** |
| NEGATIVE | lengths shuffled **within** each prompt: **0.4557 → 0.4305** | PASS |
| NOISE FLOOR | annotator split-half on the floor, 20 draws: **0.003295** | the weakest arm's margin is 8× it |

The placebo is the strongest control this session produced: a constant predictor **must** score the
human tie rate exactly, and it does, which validates the whole class-construction path from raw text
to A2 in one number.

## MULTIPLICITY

**27 arm-vs-floor tests**, BH at q = 0.05: **27 survive, 0 do not.** The six judge-free predictors are
reported as a curve, and the fact that the floor is a **max over six** is stated rather than hidden —
taking the max is a selection, and it makes the floor *harder* to beat, so it works against the
conclusion rather than for it.

## WHAT DIED

- **R802's NEXT as posed** — transporting R794's Q2 to release two needs a judge pass over 68,371
  utterances that does not exist; R802's own register said so and the NEXT proposed it anyway.
- **the worry that A2 is a word count** — the floor is below every arm, shams included.

## WHAT SURVIVES — AND THIS ROUND ADDS

The campaign's instrument, with a floor under it for the first time. Every A2 in the arc's committed
tables now has a judge-free baseline of **0.4557** to be read against, and `coval_core`'s **0.5665**
is **+0.1108** above it. The object check also reproduces a committed arm **from the raw release text**
rather than from a stored `sat` file — a longer chain than any prior round's anchor.

## SCOPE

968 prompts × 4 responses × all annotators (median 16) × 27 named arms · instrument A2, pairwise-sign
agreement, identical to every prior round · predictors computed from `data/comparisons.jsonl`'s
`responses[].messages` · NBOOT 1,200 · first release, home judge.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| scoring any arm on the second release | a judge pass over its 68,371 utterances; `sat_*.npz` are keyed to release one — **checked**, and it is why R802's NEXT was not followed |
| whether humans *should* prefer length | a normative claim; this round measures only whether they do on these 968 prompts |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The floor exists now and 27 of 27 arms clear it — computed by this round's `run.py` — so the
instrument is not measuring length. The gap from floor to the weakest arm is **+0.0271** and to `coval_core`
**+0.1108**, against an annotator noise floor of **0.003295**. What that leaves open is the span
between: the arms occupy **0.4828–0.6283** while the floor is 0.4557 and the human ceiling measured
in R793 is **0.551880** — so several arms score **above the human self-agreement ceiling**, which no
round has yet reconciled. The step is to ask what an A2 above the human ceiling means: whether those
arms exploit the tie structure the placebo just exposed (a constant predictor already scores 0.1397
from ties alone), or whether the ceiling and the arms are measured on different quantities.
