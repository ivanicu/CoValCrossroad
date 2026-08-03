# R242 — E05 audited against E05's own standard

**Arc E05·A11.** Twenty-three rounds have audited CoVal. **Nothing had audited E05.** Constitution
L03: *"I apply every law to the system and none to the document that designed it."*

## The obvious way to do this is broken, and it broke here first

Grepping a docstring for `POSITIVE CTRL` measures whether I **typed the words**, not whether the
round did the thing. So every item has a **behavioural** check beside its textual one.

⚠ **And the first version's behavioural check searched the whole file, docstring included.** Its own
positive plant — a docstring declaring all fourteen items over a body of `pass` — scored **3/14 on
behaviour**, because the words *"positive control"*, *"placebo"* and *"floor"* in the prose satisfied
the patterns meant to detect the **code**. **The audit built to separate typing from doing was
reading the typing as the doing.** The docstring is now stripped before any behavioural search.

| control | after the fix |
|---|---|
| **positive** — declares everything, does nothing | text **14/14**, behaviour **0/14** ✔ |
| **negative** — empty docstring | text **0/14** ✔ |

## The score

| item | declared | evidenced | declared-but-not-evidenced |
|---|---:|---:|---:|
| ESTIMAND | 18/23 | *(text only)* | — |
| IDENTIFICATION | 18/23 | *(text only)* | — |
| SCOPE | 16/23 | *(text only)* | — |
| WORLDS | 13/23 | *(text only)* | — |
| KILL | 14/23 | 21/23 | 0 |
| POSITIVE_CTRL | 13/23 | 16/23 | 0 |
| NEGATIVE_CTRL | 13/23 | 15/23 | **1** |
| PLACEBO | **5/23** | 5/23 | **1** |
| NOISE_FLOOR | 11/23 | 19/23 | 0 |
| MULTIPLICITY | 9/23 | 10/23 | **3** |
| SPECIFICATION | **2/23** | 7/23 | **2** |
| SEEDS | **0/23** | 10/23 | 0 |
| ARTIFACT | 3/23 | 20/23 | **1** |
| IMPOSSIBLE | 16/23 | *(text only)* | — |

```
declared overall            151/322 = 46.9%
evidenced where checkable   123/207 = 59.4%
DECLARED BUT NOT EVIDENCED  8   (3.9% of checkable cells)
```

## What the numbers say

**46.9% declared.** A prior audit on this machine scored three projects at **6–49%** and recorded
that near-100% is the signature of a broken detector. **E05 sits at the top of that band, not
outside it.**

**The most-skipped items are the ones hardest to fake:** `SPECIFICATION` declared in **2 of 23**,
`SEEDS` in **0 of 23**, `PLACEBO` in **5 of 23**. Those are the checklist items that require
building a grid rather than writing a sentence.

**`SEEDS` is the inverse case and worth its own line:** declared 0, evidenced **10**. Ten rounds do
sweep ≥3 seeds; none of them wrote the header. **Doing without declaring is the harmless direction —
but it is why the declared column alone would have scored this arc at 46.9% when the work is better
than that, and why both columns exist.**

## The audit's ceiling, named

It measures **presence, never quality**. R238 declared *and implemented* a positive control that was
**worthless** — the stratifier it validated predicted nothing — and this audit scores that round
compliant on every control item. **A round can pass every cell here and still be theatre.**

## The sentence that can no longer be written

*"E05 meets the standard it applies."* It declares 46.9% of it, evidences 59.4% of what is
checkable, and the audit cannot tell a good control from a bad one.
