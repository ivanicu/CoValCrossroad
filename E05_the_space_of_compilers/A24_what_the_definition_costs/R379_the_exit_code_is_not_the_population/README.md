# R379 — the exit code is not the population, and my grouping plan was wrong at its root

**The decision this makes safe:** *can the ten red gates be grouped by exit code?* **No.** The two
partitions cut the ten differently, and **five gates cross**.

## Result — `W_ORTHOGONAL`. Three controls PASS. Reproduction exact, 10 of 10. Two runs byte-identical. **No GPU spent.**

R378's NEXT proposed grouping the ten by the population each says it lost, *"because four of the ten
exit 2 (empty population) and an empty population usually means one moved path rather than ten."*

## ⛔ The plan was abandoned before it was written

Grouping ten free-text failure messages *"by the population they say they lost"* is a **search
instrument with no positive control** — the failure this campaign has logged four times. The ledger's
remedy is to name both units and require them to be equal:

| | |
|---|---|
| the **claim's** unit | *the set of files a gate actually examined* |
| a **keyword scan's** unit | *words I chose to look for* |

**Not equal.** So the objective instrument was used instead — and it only became admissible **two
rounds ago**, when R376 repaired the audit-hook harness that had been printing *"do not use this
harness."* This is the first use of that repair for a question it was not repaired for.

## The ten, measured rather than read

| gate | exit | round files | reads the corpus? |
|---|---:|---:|---|
| artifacts_are_internally_coherent | 1 | **593** | YES |
| attack_every_check | 1 | 1 | YES |
| **attack_no_withdrawn_framings** | **1** | **0** | **no** |
| **attack_outcome_variable_declared** | **1** | **0** | **no** |
| **donor_numbers_carry_their_draw_scope** | **1** | **0** | **no** |
| pueue_wait | 2 | 0 | no |
| **readme_row_carries_the_verdict** | **2** | **587** | **YES** |
| seed_filter_is_disclosed | 1 | 382 | YES |
| synthesis_cites_recent_work | 2 | 0 | no |
| **verdict_cites_its_own_contrasts** | **2** | **529** | **YES** |

**by exit code:** 6 / 4 — **by read-set:** 5 / 5. **Five gates cross**, and they are named rather
than summarised, because a partition claim without its counterexamples is a story.

> **`exit 2 means it lost its population` is FALSE here.** A gate can read **587** artifacts and
> still exit 2 for a reason of its own; a gate can read **zero** and still exit 1.

## ⛔ I built a control that could not pass — the fifth in this ledger

v1's positive control demanded **>100** round artifacts from `every_round_reaches_the_readme`. That
gate **iterates** round directories and only **opens** each arc's README — a design ceiling of about
**24**. The threshold sat above the ceiling, so its failure said nothing about the harness.

**Replaced by a plant whose answer is known exactly rather than argued:** a probe opening a fixed
list of **50** real round artifacts, where the harness must report **50**. It does. The old gate is
still run and printed as a **reference, never a criterion** — its number is informative about the
gate and uninformative about the instrument.

## Controls

| | returned |
|---|---|
| **INSTRUMENT (+)** ⭐ | a probe planted to open **exactly 50** round artifacts is reported as **50** |
| **INSTRUMENT (−)** | a `print('noop')` subject opens **0**. Both directions — a harness reporting hundreds for everything would pass the positive control and mean nothing |
| **REPRODUCTION** ⭐ | `what_each_check_read.json`, written **earlier, by another script, for another purpose**, agrees on **10 of 10** gates — and exactly, not merely in order of magnitude |
| reproducibility | two runs **byte-identical** (`e8fbee4b5fce`) |

## Register

| criterion | status |
|---|---|
| **whether the files opened are the RIGHT files** | **N/A** — that is *aiming*, a different question. This measures that a gate opened some |
| **WHY any gate is red** | **N/A, and three rounds have now stopped short of it on purpose** — R374 measured *when*, R375 *which commit*, R379 *what each reads*. **Stacking them still does not say why** |
| **a zero as a defect** | **not claimed** — a gate scoped to documents legitimately opens no round artifact |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"four of the ten exit 2, and an empty population usually means one moved path rather than ten."*

**Two of those four read 587 and 529 round artifacts. The exit code and the population are
independent facts, and I was about to group by the one that carries no information about the other.**

Artifact: `results/r379_read_sets.json`, source-stamped.
