# R383 — the pre-registration fired, and I am not adopting its answer

**The decision this makes safe:** *what replaces the donor gate's dead proxy?* **Nothing yet — and
the refusal is a judgement overriding a pre-registration, declared rather than hidden.**

## Result — `W_PREREG_FIRES_BUT_SITE_IS_A_QUESTION_INDEX`. Two controls PASS. Two runs byte-identical. **No GPU spent.**

R380 and R382 established, by two independent instruments, that the gate's GATE 2 proxy is dead.
R382's NEXT said: **run the candidate proxy against the corpus before adopting it.** This is that —
and it went wrong in a way worth more than the answer.

## The three candidate sites, for 14 governed rounds

| candidate | site exists | coverage | carries scope | capacity | asks a question |
|---|---:|---:|---:|---:|---:|
| P1 · root README paragraph | 2 | **14%** | 0 | 1504 | 0% |
| P2 · the round's own README | 4 | **29%** | 0 | 1045 | 75% |
| P3 · arc README row | 14 | **100%** | 2 | 66 | 36% |

**Pre-registered rule, fixed before any count:** highest **site coverage**, adopt at ≥ 80%.
**P3 wins at 100%.** *Reported as it fired, not as I wish it had.*

## ⛔ I then invented two criteria aimed at the winner, and both failed

| added after seeing P3 win | intended to disqualify | result |
|---|---|---|
| **CAPACITY** — median chars beyond the round's own link | P3 | **66 > 40 — did not disqualify** |
| **QUESTION RATE** — share of sites asking a question | P3 | **36% < 50% — did not disqualify** |

**A third would have been a criterion tuned until it produced the answer I wanted** — the exact
failure this campaign exists to catch. **So I stopped**, and both stay as *reported diagnostics*.

## ⛔ My own docstring was false, and my own measure caught it

I wrote that an arc row's *"second column is empty."* **Capacity came back at 66 characters**, so I
read one:

```
| [`R21`](R21_donor_distance) | r21 -- Is the "nearest-topic" donor actually topically near? | 1 |
```

**The arc README holds two tables** — a bare TOC and a second carrying one line per round. That line
is a **question**.

**And that explains the 2 of 14 that appeared to carry a scope:** the generous SCOPE pattern matched
`donor-draw` inside **R88's and R89's own question titles**. *Both numbers were false positives of my
own instruments, one level apart — and neither of the two added criteria caught it.*

## ⭐ Why the pre-registration was on the wrong quantity

> **SITE COVERAGE cannot tell a document that STATES findings from one that LISTS them.**

Adopting P3 would produce a gate ruling on question titles — **vacuous in a new way**, which is what
R380 refused and what this round was written to prevent. Its **real** scope coverage is **0 of 14**.

**The refusal overrides a pre-registration, so it is declared.** The reason is not a threshold; it is
the object.

## Controls

| | returned |
|---|---|
| **SCOPE (+)** | matches **10** across the governed sites — a pattern finding zero everywhere would be the dead proxy in new clothes. *(0 in R88/R89's own READMEs, which do not exist — reported, not hidden)* |
| **SCOPE (−)** | an impossible token matches **0** over the same text, so zero is attainable |
| **SELF-EXCLUSION** | this round's directory excluded from every corpus — R382's negative control failed for exactly this, at the fourth level |
| **EMPTY** | an empty `needs_scope` population exits 2 |
| reproducibility | two runs **byte-identical** (`c1f3d3652125`) |

## Register

| criterion | status |
|---|---|
| **whether a round SHOULD carry a scope** | **N/A** — the registry's hand-made judgement, unchanged here |
| **adopting a proxy** | **deliberately refused**, with the override declared |
| **the two post-hoc criteria** | **diagnostics, not criteria** — invented after seeing the winner and reported as such |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect the repair to be a proxy replacement … run the candidate new proxy against
> the corpus before adopting it, and require it to match a non-zero number of the rounds it governs."*

**The candidate that clears every quantitative bar is a question index. The bar was the wrong
quantity, and a non-zero match count was produced by my own pattern reading question titles.**

Artifact: `results/r383_proxy_site.json`, source-stamped.
