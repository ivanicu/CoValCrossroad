# R1031 — the caller existed all along, and I never passed the flag

**The decision this round makes safe:** whether R1030's named repair works. **It does not** — built
and measured, it catches **0 of 4** real cases, so it is **not wired**.

## ⭐ The measurement: `--next` usage, from the committed log

`preflight.py` has accepted `--next` throughout, and `preflight_log.jsonl` records `next_checked`:

| rounds | passed `--next` |
|---|---|
| R1019–R1021 | **4 of 4** |
| R1022–R1030 | **0 of 11** |
| **total** | **4 of 15 = 0.267** |

The split is **clean**, and the boundary is exactly where the session's context was **compacted**.
**The capability never degraded; the memory of it did.**

⚠ **0.267 lands beside R858's 0.269 by coincidence.** Two unrelated ratios; no mechanism is claimed
and none should be read in.

## ⛔ The repair R1030 named was built, and it fails

`assurance/a_next_names_its_prior_art.py` matches a NEXT against **round directory names** on content
words — the form R1030 showed the existing gate cannot see. Measured against the **four real
committed NEXT lines** it exists to catch:

| case | verdict | the prior art it missed |
|---|---|---|
| R1027 | green | R921/R918 certification |
| R1028 | green | `R472_the_register_half_complies` |
| R1029 | green | `assurance/register_requirements.py` |
| R1030 | green | `preflight` already accepted `--next` |

**0 of 4.**

## ⛔ And its calibration PASSED — which is the whole lesson

Its positive control fires **because I wrote the control's text to contain R472's title words**. The
real R1028 NEXT says *"whether each entry names a requirement"*; R472's title says *"the register half
complies"*. **Same subject, different words.**

> *A control validated only against cases you invented is validated against your imagination.*

Committed **while building the repair for a different failure**.

## ⭐ Why no lexical gate reaches this

Prior art here is **semantic**. A round is named for its question; a NEXT is written in fresh prose;
the two describe one subject with **disjoint vocabulary**. Four instruments were tried and all fail on
the same gap: substring matching (`next_gradient_is_new`), path indexing, separator normalisation,
title-word overlap. **Lowering the threshold does not help** — R1030 already measured that a permissive
setting manufactures 7/7.

## ⚠ Deliberately NOT wired

A gate with measured recall **0/4** that exits 0 would **manufacture assurance** — §4's *check that
cannot fail*, installed on purpose. The file is kept, re-headed as a **measured negative**, so a later
round attacks it rather than rebuilds it.

**The honest state: this defect has no mechanical detector.** The only thing that has ever caught it
is reading the round listing before writing the NEXT — and R1019–R1021 did pass `--next`, so the habit
existed and was lost to compaction, not to disbelief.

`results/flag_usage_and_repair_recall.json` · `../../../assurance/a_next_names_its_prior_art.py`
