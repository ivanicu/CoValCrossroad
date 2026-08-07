# R368 — matched on difficulty, the core transports; and the pattern underneath is unexplained

**The decision this makes safe:** *may `DEFINITION.md` stay silent about transport?* **No.** It
mentions transport **zero** times, and the question is now answerable from cached data.

## Result — `W_TRANSPORTS`. All four controls PASS. Two runs byte-identical. **No GPU.**

R233 ran this test and **declined its own verdict**, naming the reason and the fix:

> *"the arms differ in difficulty… The design conflated `unseen` with `equally hard`."*
> *"What would settle it: match the arms on difficulty rather than assuming it."*

The 33,320 judgements are cached, so the fix is a **re-analysis**.

| metric | matched contrast | own MDE | ratio | unmatched raw |
|---|---:|---:|---:|---:|
| **exact** *(R233's own)* | **+0.0992** | 0.0654 | **1.52×** | +0.1160 |
| **pair** *(finer secondary)* | **+0.0612** | 0.0535 | **1.14×** | +0.0353 |

**Both positive, both resolved, same sign** — a two-cell specification curve that agrees.

## ⛔ v1 ran a different statistic than R233, and the floors caught it

v1 scored agreement as the **fraction** of the six pairs matching, and got random floors of
**0.83 / 0.82** against R233's reported **0.4044 / 0.4166** — a 2× gap that is not noise. R233's
*"preserves Full's class"* is an **exact** class match: all six pairs, or nothing.

> Running a different statistic and calling it a fix of R233 is §4's *"targets a different statistic
> than the one being reported."* **The floor mismatch is what caught it.**

Corrected, the exact-metric floors land at **0.4133 / 0.3960** — R233's, within draw noise. **That
agreement is the check that says this is its test.**

## ⚠ The contrast is resolved and it is MARGINAL, on 4 strata

1.52× and 1.14× of their own MDEs, and **the MDE is computed over 4 points** — the effective n for
the contrast is the number of strata, not the 250 prompts. A resolution ratio near 1.5 at 4 degrees
of freedom is a weak resolution, and it is reported as one.

## ⚠ And the pattern underneath is odd enough to name rather than explain

| stratum | core − floor, **original** | core − floor, **fresh** |
|---:|---:|---:|
| 0 | −0.0582 | +0.0994 |
| 1 | −0.0054 | +0.0421 |
| 2 | −0.0591 | +0.0000 |
| 3 | −0.0106 | +0.1206 |

**The core is at or below random on the responses it was built for, and above random on responses it
was not.** That is consistent with R231 (the core is indistinguishable from random on this Q), but
"transports" is a strange word for *no better than random where it was built, better than random
where it wasn't*.

**[UNTESTED]** I have no measured explanation for that shape, and this round does not supply one. It
is recorded as the residual rather than narrated.

## Controls

| | returned |
|---|---|
| **PLACEBO** — `full` against itself | **1.0** exactly |
| **FLOOR** — random draw, recomputed **inside each stratum** | orig **0.4133**, fresh **0.3960** — reproduces R233's 0.4044 / 0.4166 |
| **OVERLAP** — the arms must share strata | **4 of 4** occupied on both |
| **POSITIVE** — the full rubric's own top-k by weight vs the same floor | orig **+0.0827**, fresh **+0.1400** |
| reproducibility | two runs **byte-identical** (`5f8a77501a68`) |

R233's floors were computed **whole-arm**, which is what let the population leak in. Here the
baseline is drawn **within** each stratum, so it carries the same difficulty as the arm it judges.

## Register — one entry does not move

| criterion | status |
|---|---|
| **agreement with PEOPLE on fresh responses** | **N/A, unchanged from R233** — the fresh responses carry **no human rankings**. This measures transport of the **compilation** (agreement with the full rubric), never agreement with people |
| **a second judge** | **N/A** — the cache was judged by 2B only |
| **the MDE at 4 strata** | finer strata need more prompts per cell; 250 does not support them |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"candidate-set transport is unmeasured here."*

**It is measured, matched on the confound R233 named, resolved at 1.5× on its own metric — and the
core is below random where it was built.**

Artifact: `results/r368_matched_transport.json`, source-stamped.
