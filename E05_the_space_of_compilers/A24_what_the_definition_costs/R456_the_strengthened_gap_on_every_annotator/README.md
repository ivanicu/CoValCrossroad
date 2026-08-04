# R456 · the data did **not** have more to give — α = 0.208, and R455's resolution claim narrows

**The decision this round makes safe:** whether R455's marginal `1.04× MDE` was an under-powered
design or a real limit. **A real limit.** `W-LIMIT`.

## ⚠ The announced step survived; its arithmetic did not

R455 closed: *"if the MDE falls as √(16/3) ≈ 2.3 suggests, +0.0141 moves to ~2.4× its floor."*
**That factor is an upper bound, not a prediction.** The MDE is `ZEFF·sd(d)/√968` over the
**between-prompt** gap vector; more annotators shrink only its *annotator-noise* component, and
genuine prompt-level differences set a floor the exponent cannot cross. *Twenty-fourth announced step
checked.* So the exponent was **measured**, not assumed — which is the whole difference between
running a prediction and checking one.

## Result — the annotator dose-response

| m | used | GAP | MDE | **g/MDE** | oracle | o/MDE | neutral | sham | g=0 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.0 | +0.0191 | 0.0184 | 1.04 | +0.1665 | 11.6 | +0.0038 | −0.0510 | 0 |
| 2 | 2.0 | +0.0154 | 0.0140 | 1.10 | +0.1075 | 9.1 | −0.0001 | −0.0533 | 0 |
| 3 | 3.0 | +0.0161 | 0.0124 | 1.30 | +0.0987 | 9.7 | +0.0001 | −0.0535 | 0 |
| 5 | 5.0 | +0.0150 | 0.0117 | 1.28 | +0.0831 | 8.7 | −0.0043 | −0.0553 | 0 |
| 8 | 7.9 | +0.0142 | 0.0109 | 1.31 | +0.0755 | 8.5 | −0.0036 | −0.0565 | 0 |
| **16** | 14.2 | **+0.0095** | 0.0104 | **0.92** | +0.0681 | 8.5 | −0.0060 | −0.0619 | 0 |
| ALL | 16.1 | +0.0119 | 0.0104 | 1.14 | +0.0699 | 8.6 | −0.0032 | −0.0590 | 0 |
| *CAP16* | 14.2 | +0.0109 | 0.0105 | 1.04 | | | | | *skew control* |

> ⭐ **α = 0.208** against √'s 0.500. MDE falls **1.19×** from m=3 to ALL, not the **2.3×** assumed.
> **The between-prompt spread is not annotator noise.**

## ⛔ Two corrections to my own recent claims

**① R455's `W-STRONGER` narrows to a bound.** Across the annotator specification curve the gap is
**positive in 7 of 7** cells but clears its own MDE in only **6 of 7** — it fails at **m = 16**, the
median annotator count and arguably the most defensible single specification. **Sign is stable;
resolution is not.** The honest claim: the released core is above the best generalising prompt-blind
set by **+0.0095 to +0.0191**, and *no annotator count resolves it cleanly.*

**② The 1012-annotator prompt is not in this population.** I reported max = 1012 from the full
**1078**-prompt target file. On the **968** prompts this campaign actually uses: min 4, median 16,
mean 16.1, **max 46**, total **15,593** — which is exactly §4's *"median of 16 (15,593 annotations)"*.
The skew control was therefore aimed at an object outside the population; it is kept because CAP16
(+0.0109) confirms no single prompt drives the result, but **the number I quoted last turn described
a different set.**

## Controls — all PASS at every m, which is what makes the negative readable

| control | across the whole ladder |
|---|---|
| **POSITIVE** — ORACLE − baseline | resolved at **8.5–11.6×** MDE at every m ✅ *the design has power throughout* |
| g=0 — baseline vs itself | **0.0e+00** at every m ✅ |
| **NEUTRAL** — `generic` − baseline | −0.0060 … +0.0038, **never resolved positive** ✅ |
| SHAM — wrong-prompt core | **−0.0510 … −0.0619**, loses at every m ✅ |
| SKEW — CAP16 | +0.0109 at 1.04×, ≈ ALL ✅ |

**The oracle staying at 8.5×+ throughout is what makes `W-LIMIT` a measurement rather than silence:**
the instrument can resolve a large gap at every annotator count; it simply cannot resolve *this* one.

## ⭐ What this says about §4's longest entry

That entry ends: *"a retraction feels so much like the end of an audit that nobody asks the cheapest
question left: does the data have more to give?"* — after a case where it had **5× more**.

**Here the same question was asked and the answer is no.** α = 0.208 means the unused annotators buy
19% of precision, not 130%. **The useful form of that lesson is not "the data always has more to
give" — it is "count it, because you cannot tell from the inside which case you are in."** This
round's negative is worth exactly as much as that entry's positive, and neither was knowable in
advance.

## Impossible here, named

- **more annotators than the release ships** — 15,593 on this population is the ceiling and this
  round reaches it.
- **whether the annotators are right** — construct validity needs a standard outside the release.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
