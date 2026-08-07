# R1060 — the exhaustive bound. ⛔ **The bound binds: 4,943 fixed subsets, best held-out margin negative in 5 of 5 splits.**

**The decision this round makes safe:** whether R1058/R1059's provenance-vs-quality confound is
breakable on this site by any rule of this shape. **It is not** — and that is a bound, not another
failed attempt.

## Result

| seed | best subset | in-sample | **held-out** | comparator | **margin** | sham |
|---:|---|---:|---:|---:|---:|---:|
| 3 | [0,4,6,8,12] | 0.6066 | 0.5643 | 0.5891 | **−0.0248** | 0.5720 |
| 11 | [0,1,6,7,9] | 0.5979 | 0.5751 | 0.5894 | **−0.0144** | 0.5593 |
| 23 | [0,1,3,5,7] | 0.5968 | 0.5859 | 0.5913 | **−0.0054** | 0.5686 |
| 37 | [0,1,2,8,12] | 0.5962 | 0.5815 | 0.5915 | **−0.0101** | 0.5647 |
| 53 | [0,2,4,11,12] | 0.6189 | 0.5528 | 0.5816 | **−0.0288** | 0.5501 |

**Family: 4,943 fixed subsets of size 1–5 over the 15 criteria available on ≥50% of prompts.**
**5 of 5 splits negative.** No rule of this shape closes the gap here.

## Controls

- **POSITIVE** — the comparator's own selection `[0,1,2,3]` must be **inside** the enumerated family:
  **True**. If enumeration cannot reproduce a known member, the search is not over the space it
  claims.
- **NEGATIVE** — the **worst** subset must fall below the comparator: **True** (0.3017 vs 0.5880), so
  the family is not degenerate and a maximum over it means something.
- **SHAM** — selection replaced by a **random** subset, evaluated honestly: honest selection is worth
  **+0.0090** held-out. Above the 0.005 pre-registration, so the search *is* selecting — **but only
  just**, and that is reported rather than smoothed.
- **SELECTION OPTIMISM** — in-sample minus held-out: **+0.0314**. ⭐ **Larger than every margin
  measured**, which is exactly why the held-out split is the only admissible number here; the
  in-sample best would have shown the comparator beaten in all 5 splits.
- **MULTIPLICITY** — the maximum is taken over 4,943 cells; the held-out evaluation is what makes it
  admissible at all.

## ⛔⛔ And an estimand check that landed harder than intended

`generic` scores **0.5880** under this round's **consensus** aggregation, **0.5023** under my quick
reimplementation of R1059's **per-annotator** one — and **R1059 itself reported 0.5514**. **Three
numbers for one arm.**

⭐ So the honest statement is not *"different estimands"* but **"the two rounds' scales are UNVERIFIED
against each other"**. A 3-line reimplementation is not evidence about what R1059 computed, and I will
not claim to know its estimand from one. **R1059's `+0.0651` and this round's margins must not be
quoted against each other** until one round re-derives the other's number with the other's code. Each
round's *internal* comparison — arm vs comparator, same prompts, same aggregation — stands.

## What this establishes

⭐ **Every fixed-subset core's non-admission is FORCED by the release**, not by the clause. So the
question *"does the clause test provenance?"* is **unanswerable by this family** — no experiment of
this shape can carry information about it, however well built. That closes the line R1058 opened, by
bounding it rather than by another attempt.

## IMPOSSIBLE here

- **whether a PROMPT-CONDITIONED rule could clear the bar** — outside the enumerated family by
  construction. **SETTLES: IN-RELEASE** — it is a larger search on this same release, not a different
  release.

`run.py` · `results/fixed_rule_bound.json`
