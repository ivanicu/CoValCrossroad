# R839 · the threshold curve the record never had

**The decision this made safe:** whether the campaign's 1×/2× MDE inconsistency is cosmetic.
**It is not** — the per-artifact **median 15.6%** of verdicts move between the two thresholds.

Design in `PREREGISTRATION.txt`, committed before `run.py` ran.

## My own NEXT invoked pre-registration to avoid this curve

It said re-thresholding 133 pre-registered rounds *"would invalidate the pre-registrations."*
⛔ **G4 says the opposite in the standard's own words**: enumerate every defensible choice and run
all of them, reporting the cells that kill the finding. **A pre-registration protects against
CHOOSING a threshold after seeing the result; it does not forbid REPORTING the curve.** R836 already
did exactly this for R835. **And the data was on disk**: of 563 artifacts under `A24`, **44** persist
an effect with its MDE — **1,330 cells** whose sweep costs nothing.

## Result

| | |
|---|---|
| artifacts swept · out of scope | **44** · **520** (no MDE persisted) |
| cells · verdicts that change | **1,330** · **239** (**18.0%** pooled) |
| pooled share **excluding the largest artifact** | **22.0%** (R789 alone holds 416 cells) |
| **per-artifact median share** | **15.6%** (min 0.0% · max 100.0%) |
| controls: 1.5× flips · 5× stable · zero never separable | PASS · PASS · PASS |
| three seeds | byte-identical |

**W-THRESHOLD-DEPENDENT.** A material part of the committed record depends on a choice that was
never stated as a choice.

## Where it concentrates

| artifact | 1× → 2× | share |
|---|---|---|
| `R331_what_makes_a_clause2_reference_safe` | **3 → 0** | 100% |
| `R455_can_clause_two_be_strengthened` | **3 → 0** | 100% |
| `R456_the_strengthened_gap_on_every_annotator` | 7 → 0 | 87.5% |
| `R767_the_fifth_member_is_below_resolution` | 17 → 0 | 73.9% |
| `R327_clause2_names_no_reference` | 4 → 1 | 60% |
| `R326_the_clause2_baseline_curve` | 8 → 3 | 50% |

⭐ **Of the 11 artifacts where ≥40% of verdicts move, 6 are clause ② rounds** — its baseline, its
reference, whether it can be strengthened. **The evidence base for ② is the most
threshold-sensitive part of the record.** ⚠ **That is a NAME match, not a content audit** — a
candidate pattern, and the next round that touches ② should treat it as one.

## ⛔ A labelling bug the numbers survived

v1 used `f.parts[2]`. `A24` is an **absolute** path, so `parts[2]` is `ivan` — **all 44 rows were
labelled with a home-directory component.** The counts were correct and the table was unreadable,
which is the failure a reader meets first.

## What is not claimed

⚠ **Cells are not commensurable across artifacts.** The share counts **verdict changes**, never a
pooled effect size, and **no artifact is dropped for being small** — which is why the kill reads the
per-artifact **median** rather than the pooled number dominated by wherever cells accumulated.

## NEXT

⛔ **CORRECTED THE NEXT ROUND — the wall was overstated by 13.** *"The 519 artifacts that persist
no MDE cannot be swept at all"* measured **"has a key literally named `mde`"**. Re-probed: **13
artifacts across 13 rounds carry a CI with an effect** — the same information under a different
key, sweepable by a different route (CI-excludes-zero rather than a k×MDE multiple, so not a
drop-in). The re-probe that found those 13 also counted **503**, not 519, carrying no MDE, no CI
and no p beside an effect. **Instrument unit vs claim unit, again.**
The R839 numbers do not move; the impossibility claim does.

The remaining 503 artifacts genuinely cannot be swept from what is on disk, so this curve covers
the part of the record that already recorded its own resolution. Whether the unswept remainder is threshold-free or
merely unmeasurable is decided by what each of those rounds persisted, and that is a property of the
artifact format rather than of the finding.
