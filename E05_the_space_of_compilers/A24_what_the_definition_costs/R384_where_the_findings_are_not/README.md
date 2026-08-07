# R384 — 243 of 377 rounds have no finding site at all, and a green gate said so before I measured it

**The decision this makes safe:** *are the nine remaining red gates nine problems?* **No — they are
one.** Not a dead path, not a stale pattern, not a coupling: **a corpus whose findings were never
written where its own documents say they live.**

## Result — `W_FINDINGS_UNWRITTEN`. Both controls PASS. Two runs byte-identical. **No GPU spent.**

| over 377 round directories | all | produced an artifact |
|---|---:|---:|
| has its **own README** (the designated *design* site) | 114 · **30%** | 114 · 31% |
| named in the **root README** (the designated *finding* site) | 84 · **22%** | 84 · 23% |
| **NEITHER** | **243 · 64%** | **238 · 64%** |

**372 of 377 rounds produced an artifact** — so it is not that they had nothing to report.

## ⭐ The sites are not my choice — the campaign's own documents name them

Every arc README says, in its own words:

> *"Table of contents only. Each round's README states its design; the finding lives in
> `../../README.md`"*

That removes the failure R383 walked into, where **I** chose three candidate sites and then ranked
them on the wrong quantity. Here the corpus specifies the sites and the only question is whether they
are populated.

## ⭐ What a GREEN gate admits — and it confessed this itself

`every_round_reaches_the_readme` **passes**, accepting the root README **or** the round's arc README.

> **293 of 377 rounds (78%) pass it only via an arc index row** — which R383 measured to be an index
> of *questions*.

And its own docstring already says:

> *"read the pass honestly: this check passes today because `generate_round_index.py` wrote those arc
> tables in the same session. That is a **CONSTRUCTION, not a discovery**, and it is weak evidence of
> the property."*

**The confession was written. What was never done is measure how much it admits** — and four rounds
this session walked past it while auditing the *red* gates. *A confession is never audited.*

## Controls, both against answers established before this question existed

| | returned |
|---|---|
| **POSITIVE** | the 4 rounds I wrote root-README paragraphs for this session (R380–R383) all count as named — a census missing them would be broken in the direction that matters |
| **NEGATIVE** | `R106_share_level_under_redraw` and `R109_donor_arm_is_text_blind` still count as lacking their own README, as **R380 established by listing their directories** before this question existed. Both directions, because a census reporting everything present would pass the positive control and mean nothing |
| **SELF** | this round's directory excluded — R382's negative control failed for exactly this; now standard, not a discovery |
| reproducibility | two runs **byte-identical** (`d6400a7d157c`) |

## ⚠ The number is flattering, and the direction is stated

**The rounds written this session are in the root README by construction** — I appended a paragraph
for each. **Coverage of everything older is lower than the headline.**

## Register

| criterion | status |
|---|---|
| **whether a round SHOULD state a finding** | **N/A** — a judgement. The artifact restriction (372 of 377) is the closest objective proxy and is reported separately rather than assumed either way |
| **whether existing text IS a finding** | **N/A** — R383 showed a site can exist and hold a *question*. **This counts SITES, never content** |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"every round reaches the readme."*

**It does — through a table-of-contents row. 78% reach it no other way, 64% have no finding site at
all, and the gate certifying it wrote down why its own pass was weak evidence before I ever ran this.**

Artifact: `results/r384_finding_sites.json`, source-stamped.
