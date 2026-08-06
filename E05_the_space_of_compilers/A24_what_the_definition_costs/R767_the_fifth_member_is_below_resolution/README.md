# R767 · the extension is 4 CONFIRMED + 1 UNRESOLVED, and the convention only bites at the published comparator

**`topw_k8` — one of the five committed extension members — is **BELOW RESOLUTION** at the published
comparator: effect **+0.0089**, CI **[0.0009, 0.0163]** excluding zero, MDE **0.0107**, **eff/MDE =
0.827**. Stable at B = 1200 / 4800 / 19200. The other four are BEATS at eff/MDE **1.152–1.311**.
⭐ **Removing the MDE floor changes exactly one verdict — `topw_k8` → BEATS — so "the extension is 5"
IS the two-valued reading.** And the two conventions agree at every baseline except **p095 and
published**, which is where the release sits. **WORLD A.**

## check #369 — R766's NEXT was already answered by R764's own estimator

It asked whether `gen` clears ② *"resolvedly"*. R764's admission test is
`verdict(eff, lo, hi, mde) == POS` *(run.py:192-196)*, and `report.py:25-35` returns `POS` only when
the CI excludes zero **and** `|eff| ≥ MDE`. **Every admission in that grid was already resolved.**
**Fifth NEXT line this arc killed by the next round's first check** *(ledger 1081)*.

## what the same comparison turned up instead — two of my own rounds disagree

| round | at the published baseline, target-reading rules excluded |
|---|---|
| **R760** `admitted_rule` | **9 tags / 5 objects** — incl. `coval_core_2bA`, `_2bB`, **`topw_k8`** |
| **R764** published `3-rank` | **6 tags / 4 objects** — none of those three |

`coval_core_2bA/_2bB` are R764's declared coverage exclusion (200 of 968 prompts). **`topw_k8` is in
both populations and gets opposite ② verdicts.**

## ⭐ E1 · the five committed members at the published comparator

| arm | A2 | eff | CI | MDE | **eff/MDE** | verdict |
|---|---|---|---|---|---|---|
| `coval_core` | 0.5665 | +0.0160 | [0.0083, 0.0241] | 0.0106 | **1.509** | BEATS |
| `topw_k6` | 0.5641 | +0.0137 | [0.0059, 0.0209] | 0.0104 | **1.311** | BEATS |
| `topw_k4` | 0.5642 | +0.0137 | [0.0054, 0.0216] | 0.0109 | **1.264** | BEATS |
| `topw_k3` | 0.5632 | +0.0127 | [0.0045, 0.0203] | 0.0111 | **1.152** | BEATS |
| **`topw_k8`** | 0.5593 | **+0.0089** | **[0.0009, 0.0163]** | **0.0107** | **0.827** | ⛔ **BELOW RESOLUTION** |

Identical at B = 4800 and B = 19200. **D2 says why a B-sweep cannot help**: raising B narrows the CI
and leaves the MDE untouched (`z·sd/√n`, no bootstrap in it). R728's B sweep found nothing for
exactly that reason, and this round reports the sweep to *show* that rather than to test it.

## ⭐⭐ the SHAM is the whole finding — the ingredient is the MDE floor

| | verdicts |
|---|---|
| **with the floor** | `coval_core` BEATS · `topw_k3` BEATS · `topw_k4` BEATS · `topw_k6` BEATS · **`topw_k8` BELOW RESOLUTION** |
| **floor removed** (`mde=None`) | all five **BEATS** |
| verdicts that change | **1** — `topw_k8` |

**The extension is 4 with the floor and 5 without it.** Removing the floor is precisely what a
two-valued reading does, so the sham *measures* the convention instead of arguing about it
*(ledger 1082)*.

## ⚠ the registered confound is answered, and it strengthens the reading

Is this a k-trend rather than one arm? **It is a trend, and `topw_k8` is on its descending limb:**

| k | A2 | eff | eff/MDE | verdict |
|---|---|---|---|---|
| 1 | 0.5256 | −0.0249 | −1.825 | LOSES |
| 2 | 0.5536 | +0.0031 | 0.263 | UNRESOLVED |
| 3 | 0.5632 | +0.0127 | 1.152 | BEATS |
| 4 | 0.5642 | +0.0137 | 1.264 | BEATS |
| **6** | 0.5641 | +0.0137 | **1.311** | BEATS |
| **8** | 0.5593 | +0.0089 | **0.827** | **BELOW RESOLUTION** |
| 12 | 0.5380 | −0.0124 | −1.094 | LOSES |

An inverted U peaking at k = 6, and `eff/MDE` falls monotonically 6 → 8 → 12. **`topw_k8` is not an
anomaly; it is where the curve crosses back inside the floor.**

## ⭐ E3 · and the convention only bites where the release published

| baseline | BEATS (floor) | passing (no floor) | `topw_k8` |
|---|---|---|---|
| p000 · p005 · p025 · p050 · p075 | **5** | **5** | BEATS |
| **p095** | **4** | 5 | BELOW RESOLUTION |
| **published** | **4** | 5 | BELOW RESOLUTION |
| p100 | 0 | 1 | UNRESOLVED |

**At every weaker comparator the two readings agree at 5.** They separate at p095 and at the
published draw — the one the release chose *(ledger 1083)*.

## controls — 4 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | 4 of 5 committed members return BEATS. Band: a BEATS-everything instrument also passes the placebo arms below; a BEATS-nothing one fails here — unreachable from either end |
| **g=0** | baseline vs **itself**: eff 0.000000 → **UNRESOLVED**, not BEATS |
| **NEGATIVE** | `topw_k8` with the pairing destroyed ×200: **200/200 UNRESOLVED** — BELOW RESOLUTION is *not* what this design returns for everything |
| **PLACEBO** | `coval_core_sham`, `topw_k4_sham`, `gen_sham` → **LOSES**, all three |

## what this changes in the deliverable

| carried | stands as |
|---|---|
| *"the extension of ② ∧ ③ is **5 arms**"* | ⛔ **4 CONFIRMED + 1 UNRESOLVED** at the published comparator. P6: folding the third value into either side manufactures a verdict, and `5` folds it toward pass |
| *"`topw_k8` is an extension member"* | its effect is **inside its own design's resolution** — `eff/MDE 0.827`. It is not excluded and not admitted |
| R760's `admitted_rule` = 9 tags / 5 objects | **explained**: two tags are R764's coverage exclusion, and `topw_k8` is the three-valued verdict read two-valued |
| *"3 to 8 are indistinguishable"* *(the k-bound already on the page)* | **strengthened and sharpened**: k = 3, 4, 6 clear; k = 8 does not; k = 2 is unresolved; k = 1 and 12 lose |

## the sentence I can no longer write

*"the extension is five arms."* Four clear the comparator; the fifth sits inside the floor, and the
number 5 exists only if the floor is dropped.

## NEXT

The k-curve peaks at **k = 6** (eff/MDE 1.311), not at the released core's **k = 4** (1.264) — and the
page's size bound reads *"more than one, and 3 to 8 are indistinguishable"*, which this round's own
table contradicts in both directions: k = 8 is now distinguishable *from* the passing band, and k = 6
outscores k = 4. ⚠ But 1.311 vs 1.264 is a **ratio of two estimated quantities** with no interval on their
difference. This round compares each arm to the **baseline** — `cell(A[t], bv, B)`, computed by `run.py` — and
makes no arm-to-arm comparison; whether earlier rounds did is not something a grep settles here,
because the loose pattern that would find them also matches an arm-vs-baseline difference. The
registered quantity is the paired
`topw_k6 − topw_k4` difference with its own CI and MDE, because if that is unresolved then "the
optimum is at k=6" is exactly the two-valued reading this round just retracted, one level up.
