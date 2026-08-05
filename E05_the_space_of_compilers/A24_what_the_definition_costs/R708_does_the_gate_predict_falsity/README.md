# R708 · do the gate's flags predict which NEXT lines turn out FALSE? — criterion validity, partial

**It caught `2` of the `15` NEXT lines this project later recorded FALSE. The gap against lines that
held is `+0.1333` and this design's MDE is `0.300`, so the gap is NOT readable — but one number is:
the Wilson 95% upper bound on sensitivity is `0.379`. **The gate catches at most ~38% of the NEXT
lines that later turn out false**, and that bound does not depend on the gap being resolvable.**

Population **the 27 NEXT lines this project has itself judged, from checks #258–#310** · instrument
**`flagged()` imported unchanged + R706's extractor, applied to the *target* round's commit body** ·
baseline **the corpus flag rate 0.2772, and a label-permutation null** · regime **this repository at
HEAD**.

## check #310 — the citation resolves; the method it proposed does not

✓ `chance_share_by_decile` **is** in R707's artifact, 10 entries, range 0.61–0.99. The first citation
in this thread that resolves; R706's did not.

⛔ **But its method is inadmissible.** It proposed I *"judge them by hand against the rule the gate
claims to enforce"*. **I wrote that rule and I wrote the gate**, so my hand-judgement correlates with
it by construction — it would measure my consistency, not the gate's validity. Self-review is void,
not weak, and independent judges are unavailable this session.

⭐ **The substitute is better than the proposal.** This project already produces a verdict on NEXT
lines by a process that **never consults the gate**: every round opens `CHECK #N ON R___'s NEXT LINE`
and records whether it held or was false. 110 numbered checks exist (#192–#309); 34 name a target and
carry a headline; 27 classify. **That is criterion validity — the row §2 marks impossible —
available in partial form.**

## the 2×2

| | flagged | not | n | rate | 95% Wilson |
|---|---|---|---|---|---|
| later recorded **FALSE** | **2** | 13 | 15 | 0.1333 | **[0.037, 0.379]** |
| later recorded **HELD** | 0 | 12 | 12 | 0.0000 | [0.000, 0.243] |

**gap = +0.1333** · permutation null 95% `[−0.1667, +0.1333]`, p = **0.4735** — inside · sham (flag →
coin at the corpus base rate) null `[−0.350, +0.367]`, noise floor spread **0.7167** over 3000 draws.

## the MDE — measured, because it was the likely answer

| true gap | 0.00 | 0.10 | 0.20 | **0.30** | 0.40 | 0.50 |
|---|---|---|---|---|---|---|
| power | 0.24 | 0.45 | 0.70 | **0.87** | 0.96 | 0.99 |

**MDE at 80% power = `0.300`. Observed |gap| = `0.1333`.** Not readable.

## specification sweep — the sign is not stable

| extractor | n | gap |
|---|---|---|
| commit body (live) | 27 | **+0.1333** |
| README `## NEXT` | 24 | +0.0000 |
| commit body, whole-paragraph window | 27 | **−0.2000** |

**−0.20 to +0.13 across three defensible extractors.** Sign instability is what an unreadable effect
looks like, and it is reported rather than resolved by picking a cell.

## controls — 5 PASS, 0 FAIL, two runs byte-identical

| control | returned |
|---|---|
| **POSITIVE (classifier)** | recovers #307, #308, #309 as FALSE and #279, #303 as HOLDS — verdicts whose content I can state independently of it |
| **g=0 (classifier)** | verdict words stripped → **0** still labelled. It abstains; it does not guess |
| NEGATIVE | pairing permuted at fixed counts → gap inside `[−0.1667, +0.1333]`, p = 0.4735 |
| SHAM | the gate's flag replaced by a coin at the corpus base rate — rate- and count-matched; its distribution *is* the null |
| PLACEBO / SEEDS / UNIT | identical runs differ by 0 · 3 streams differ · instrument unit ≠ claim unit |

**Unlabelled counted, never imputed:** 7 checks abstained; 0 target rounds lacked an extractable NEXT
paragraph.

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** sensitivity | 0.35 [0.10, 0.75] | **0.1333**, inside |
| **B** gap | +0.10 [−0.25, +0.50] | **+0.1333**, inside |
| **C** MDE | 0.35 [0.15, 0.80] | **0.300**, inside |
| directional | sensitivity > base rate 0.2772 | ⛔ **FAILS** — 0.1333 is *below* it |

## what this closes, and what it does not

- **Closed:** the gate's sensitivity has a measured ceiling. At most ~38% of the NEXT lines this
  project later called false were flagged; the two it did catch are the whole of its record.
- **Not closed and now bounded:** whether the gap is real. This corpus cannot say, and the MDE says
  why — 15 false and 12 held cannot resolve anything under 0.30.
- **Still standing as the strongest evidence about this gate:** R707's word-scramble result —
  **76%** of its flagging survives destroying word order.

## limits

- **The labels are independent of the GATE but not of ME.** That is the confound this design
  controls and the only one. An external judge remains impossible here and my own hand-judgement is
  not a substitute for one — that is precisely what check #310 rejected.
- The classifier reads a **recorded** verdict; it never forms one. Its positive control is five
  verdicts whose content is stateable without it.

## impossible here

| criterion | what it would require |
|---|---|
| construct validity by an external standard | a judge who did not write the rule |
| cross-release | the `NEXT` convention, the check protocol and the verdict vocabulary are all ours |
