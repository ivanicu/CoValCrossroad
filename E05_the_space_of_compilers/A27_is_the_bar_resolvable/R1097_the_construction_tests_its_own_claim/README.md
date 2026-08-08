# R1097 — ⛔ **R1096 is RETRACTED.** `prompt-blind` has two referents, and the arc uses both.

**The decision this round makes safe:** whether R1096's repair — *"a certifiable-and-disjoint
comparator is one committed selection file away"* — is real. **It is not.** Building it is what
killed it.

## ⛔ The sham was validated against a string I invented

R1096's SHAM wrote `f"criterion {i}"` — **the same text on every prompt** — so the rule saw one
distinct selection and certified it. **The real selection is not constant.**

| comparator | distinct criterion-**text** selections over 968 prompts |
|---|---:|
| `generic` — the rule's own anchor (R918's `fixed`) | **1** |
| index-blind subset, indices `(0,)` | **968** |
| index-blind subset, indices `(0,1,2)` | **968** |
| index-blind subset, indices `(0,1,2,3)` | **968** |
| `full` — the maximally specific pole | **968** |

**An index-blind subset is indistinguishable from `full` under the rule that certifies.** Writing the
file does not help — it would honestly record **968**, against a strict cell of **≤ 1**, and the rule
would refuse. §4's *a control validated only against cases you invented is validated against your
imagination*, committed one round ago.

**RETRACTED: R1096's headline.** **STANDS: R1096's derivation** (the rule types arms, so the certified
family is an arm subset) **and its population measurement** (0 of 15 blind subsets in the rule's
population).

## ⭐ The structural fact underneath — the third term in this arc with two referents

| sense | meaning | who is blind |
|---|---|---|
| **INDEX-blind** | the same **positional** selection on every prompt | R1057's 15 subsets |
| **TEXT-blind** | the same criterion **strings** on every prompt | `generic`, `genericpool16` |

**R1056's certification rule types TEXT.** So **the certified family (2) and the synthetic family (15)
are blind in different senses**, and every cross-family statement in this arc carries that seam.

R1094 found the same shape in clause ③'s two readings; R1091→R1092 found it in a wall that was not
a wall. **This is the third, and in each case the control could not separate the referents.**

## ⚠ And the id spaces do not join

`data/conversation_rubrics.jsonl` keys on a **conversation** id whose overlap with the 968 scored
`prompt_id`s is **0**; `comparisons.jsonl` overlaps at **968**. No join was needed for this round —
and **none is available by id**, which is worth recording before someone attempts one.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE `generic` returns exactly **1** — the rule's own anchor | PASS |
| g=0 `full` returns **968** — the other pole, so the middle is calibrated | PASS |
| NEGATIVE the result holds for **three** index sets, not one | PASS |
| SHAM the invented constant certifies **and the real selection does not** — the retraction, made computable | PASS |
| PLACEBO re-reading a selection file returns an identical count | PASS |

## Impossibility register — corrected, not repeated

| criterion | status | what it would require |
|---|---|---|
| a comparator that is **TEXT-blind and not an arm** | **N/A in this release** | a fixed external rubric committed as a comparator and excluded from candidacy. Text-blindness over prompt-specific rubrics means a **fixed external criterion set** — which is exactly what `generic` is, **and `generic` is an arm** |
| joining the rubric release to the scoring matrices by id | **N/A** | a shared identifier; the overlap is 0 |
| cross-release | **N/A** | a second release |

`run.py` · `results/two_senses_of_blind.json`
