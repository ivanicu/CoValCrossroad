# R757 · the artifact corpus was scoped to ONE arc of ten, and nine rounds inherited it

**`E05_the_space_of_compilers/` holds **ten arcs, A16–A25**. A24 begins at **R276**. Every round from
R748 to R756 resolved artifacts with `A24.glob(f"R{rid:03d}_*")` — **98 of 577 artifacts, across 72
round directories, were invisible.** Recomputed against the full corpus, `FORMULATION.md`'s flagged
rate falls **0.8000 → 0.3680**, while `STATEMENT.md` and `DEFINITION.md` fall **exactly 0.0000**. ⛔
**The round is `UNVERIFIED`** — its NEGATIVE control failed, and for a reason that matters more than
the number.**

## check #359 — R756 contradicted itself, and the object settled it

R756's era table said **17 of 17** rounds below R300 have artifacts. Its g=0 said **27 cited rounds
have none**, listing R220–R274. **Both cannot be true.** They are not artifact-less — **they live in
A17 and A23**, and my lookup never left A24 *(ledger 1041)*.

| | count |
|---|---|
| arcs present | **A16 … A25 (ten)** |
| round directories: A24 / repo-wide | 460 / **532** |
| artifacts: A24 / repo-wide | 479 / **577** — **98 invisible** |

**This is §4's *a search is an instrument* at repository scale**, and the same class as R728's finding
that a census population was a directory glob: **the population of artifacts was a glob scoped to the
wrong level**, and every *"the cited round does not hold this value"* verdict inherited it.

## the recomputation — internally valid, and that part is clean

| document | A24 corpus | repo-wide | drop | flagged |
|---|---|---|---|---|
| `STATEMENT.md` | 0.1784 | 0.1784 | **0.0000** | 33 → 33 |
| `DEFINITION.md` | 0.3984 | 0.3984 | **0.0000** | 51 → 51 |
| **`FORMULATION.md`** | **0.8000** | **0.3680** | **0.4320** | **100 → 46** |

⭐ **Both arms use the same document text**, so this contrast is internally valid whatever else drifts.
`STATEMENT.md` cites only A24 rounds and moves **not at all**; `FORMULATION.md` cites A16–A23 and
loses **more than half** its flagged figures. **The directional predicted exactly this.**

⛔ **The repo corpus CONTAINS the A24 one, so the rate can only fall.** *"It fell"* is algebra; only
the **size** and the **sham comparison** are measurements.

## ⛔ my first SHAM was more generous than the treatment

v1 appended the whole size-matched blob to **every** figure's lookup and reported a drop of **0.4880**
— *larger* than the real 0.4320 — which would have read as World C, the movement being the haystack.
**But the real correction gives each figure only its OWN out-of-A24 round**, while that sham handed
every figure 98 rounds' worth of text *(ledger 1042)*.

**Repaired to per-figure matching** — each figure gets one randomly chosen non-artifact file of the
size its own correction supplies:

| | drop |
|---|---|
| real correction | **0.4320** |
| per-figure size-matched sham, 3 seeds | 0.072 / 0.088 / 0.080, **mean 0.0800** |
| ratio | **0.185** |

**The haystack accounts for 18.5%. The correction is 5.4× the sham.** It is evidence, not corpus size.

## ⛔ the NEGATIVE control failed, and that is the more important finding

Restricted to A24, the rates no longer reproduce R753's committed numbers:

| document | R753 committed | today, same corpus |
|---|---|---|
| `STATEMENT.md` | 0.1793 | **0.1784** |
| `DEFINITION.md` | 0.3814 | **0.3984** |
| `FORMULATION.md` | 0.8000 | 0.8000 |

**Because I have appended a section to `STATEMENT.md` and `DEFINITION.md` in every round since.**
**The deliverable is a MOVING POPULATION**, so any round comparing its rate to an earlier round's is
comparing across two different documents *(ledger 1043)*. `FORMULATION.md` matches exactly — it is the
one document nobody has edited, which is why the control localises the drift precisely.

⇒ **The corpus defect is established; its size relative to R753's PUBLISHED numbers is not**, and the
verdict is `UNVERIFIED` rather than a corrected figure.

## controls — 4 PASS, 1 FAIL

| control | returned |
|---|---|
| **POSITIVE** | `0.6602` found **verbatim by direct search** — not by the matcher — in `A16/R220/tournament.json`: **flagged under A24, supported repo-wide**. Band: flagged-under-both and supported-under-both are the degenerate ends; **the FLIP is unreachable from either** |
| **g=0** | fabricated `0.918273645` stays flagged under **both** corpora — the matcher does not support invented numbers |
| **NEGATIVE** | ⛔ **FAIL** — see above; the documents moved |
| **SHAM** | per-figure size-matched non-artifact text → **0.0800** vs the real **0.4320** |
| **PLACEBO** | recomputed under one corpus, difference exactly **0** |

**CONFOUND, printed not absorbed** — newly-resolved matches by arc:
`A23: 25 · A19: 16 · A20: 7 · A16: 4 · A17: 4 · A18: 1`. **Spread across six arcs**, so it is not one
arc's storage format.

## registered vs measured — all five hit

| | registered | measured | |
|---|---|---|---|
| P1 FORMULATION repo-wide | 0.35, band [0.05, 0.75] | **0.3680** | ✓ |
| P2 STATEMENT repo-wide | 0.17, band [0.10, 0.20] | **0.1784** | ✓ |
| P3 rounds now resolvable | 27, band [20, 27] | **26** | ✓ |
| P4 max between-document difference | 0.20, band [0, 0.62] | **0.2201** | ✓ |
| P5 sham drop | 0.05, band [0, 0.60] | **0.0800** | ✓ |
| D FORMULATION falls more | true | **true** — 0.4320 vs 0.0000 | ✓ |

**The first round in this arc where every registered point landed** — and the round is still
`UNVERIFIED`, because a control failed. **Prediction accuracy is not a verdict.**

## the sentence I can no longer write

*"the cited round does not hold this value."* For nine rounds that sentence meant *"no A24 round holds
it"*, and one document in three cites almost nothing in A24.

## NEXT

Two things are now owed and they are different in kind. The **numbers** from R748 to R756 rest on the
narrow corpus and each must be recomputed — that is mechanical and the instrument for it is in this
round. The **comparison method** is the harder one: two of the three deliverables grow each round, so a rate
published in one round is not comparable to the same rate in the next, and this round located that
drift because the third document has stopped changing. Pin the population — record with each rate the document's
line count and content hash, so a later comparison can tell a moved number from a moved document. The
unit is the (rate, document-version) pair rather than the rate, and lacking it leaves any trend across
this arc confounded with my own editing.
