# R758 · git pins the population — both of them — and the correct pin is the PARENT commit

**Pinned to R753's **parent** tree, all three rates reproduce **EXACTLY**: `0.1793 / 0.3814 / 0.8000`,
including DEFINITION.md's 118 figures and 45 flagged. **R757's failed NEGATIVE control is repaired.**
⭐ And the reason it needed the parent is the finding: **a round's own commit holds the document AFTER
that round appended to it**, so pinning to the commit over-counts by exactly that round's own
additions — DEFINITION.md reads **122 figures at the commit, 118 at the parent.****

## check #360 — and my first lookup this round failed silently

`git log --grep` matched nothing, leaving the commit variable **empty**, and `git show :path` with an
empty prefix resolves to the **index** — today's file. It printed three deltas of **+0**, which reads
as *"nothing moved"*. **A failed search produced a reassuring answer** *(ledger 1045)*. The repaired
command asserts the lookup is non-empty and refuses to proceed; the round's `main()` does the same and
**exits 2** on an empty commit.

## the two populations, and why R757 could not attribute

R757 diagnosed *"the deliverables grow every round"* and left `UNVERIFIED`. It named one population.
**There are two**, and it pinned neither:

| | at R753 | at HEAD |
|---|---|---|
| `STATEMENT.md` | 1205 lines | 1255 (+50) |
| `DEFINITION.md` | 4677 lines | 4875 (+198) |
| `FORMULATION.md` | 2397 lines | 2397 (**+0**) |
| A24 artifact rounds | 456 | 460 |
| repo-wide artifact rounds | 525 | 529 |

## the grid — 3 documents × {parent, commit, today} × {A24, repo-wide}

| document | tree | A24 rate | repo rate | vs R753 (A24) |
|---|---|---|---|---|
| `STATEMENT.md` | **PARENT** | **0.1793** | 0.1793 | **EXACT** |
| `STATEMENT.md` | commit | 0.1793 | 0.1793 | EXACT |
| `STATEMENT.md` | today | 0.1784 | 0.1784 | −0.0009 |
| **`DEFINITION.md`** | **PARENT** | **0.3814** | 0.3814 | **EXACT** |
| `DEFINITION.md` | commit | 0.4016 | 0.4016 | **+0.0202** |
| `DEFINITION.md` | today | 0.4000 | 0.4000 | +0.0186 |
| `FORMULATION.md` | **PARENT** | **0.8000** | 0.3680 | **EXACT** |
| `FORMULATION.md` | commit | 0.8000 | 0.3680 | EXACT |
| `FORMULATION.md` | today | 0.8000 | 0.3680 | EXACT |

⛔ **A larger corpus can only LOWER a rate; a longer document can move it either way.** The **sign** is
diagnostic and is read that way.

⭐ **`DEFINITION.md` goes 118 → 122 figures between parent and commit — those four are R753's own
appended DEFINITION section.** The preregistration named this limit before the run
(*"R753 ran BEFORE its own commit"*) and the round printed the bracket; **the bracket turned out to be
the answer.**

## controls — 5 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | recovered deltas `{STATEMENT +50, DEFINITION +198, FORMULATION +0}`. Band computed: a recovery returning today's file gives **all-zero** deltas — **the exact failure my first lookup produced** — and one returning nothing gives empty blobs. Measured sits strictly between |
| **g=0** | HEAD's own tree reproduces **today's** rates exactly — the recovery path is not lossy |
| **NEGATIVE** | both crossed cells fail to reproduce R753 (`hist docs + today corpus`: False; `today docs + hist corpus`: False) — **both populations are needed** |
| **SHAM** | ingredient **absent** — R750's trees instead: `0.1803 / 0.3596 / 0.8000`, reproducing R753 in **1 of 3**. **Reproduction is specific to the right tree**, so it is evidence rather than coincidence |
| **PLACEBO** | the same tree recovered twice is byte-identical, 0 of 3 |

**CONFOUND, and it is decisive:** artifacts present at both commits **574**, **changed in place: 0**,
added since: **4**. **Nothing was edited under the measurement** — only added — which is what leaves
the document as the sole explanation.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| **P1** R753's rates reproduce when pinned | **YES** *(hard)* | **yes at the PARENT**, no at its own commit | ✓ — with the pin corrected |
| P2 FORMULATION A24→repo drop, pinned | 0.43, band [0.10, 0.70] | **0.4320** | ✓ |
| **P3** DEFINITION document-drift contribution | 0.017, band [0.000, 0.100] | **0.0016** | in band, **point 10× wrong — drift was not the cause** |
| P4 R756's variance ratio, repo-wide | 2.0, band [0.5, 5.0] | **2.47×** (0.1036 / 0.0420, n=97) | ✓ |
| P5 A24 rounds at R753 | 455, band [400, 540] | **456** | ✓ |
| D document drift > corpus drift for DEFINITION | true | **true** | ✓ |

⭐ **R756's central finding SURVIVES the corpus correction**: recomputed repo-wide, between-round
variance is **0.1036** against a null of **0.0420** — **2.47×**, against the 2.30× it reported on the
narrow corpus. **The rate belongs to rounds, and that was not an artifact of the scoping defect.**

## the pin, applied to this round's own numbers

`STATEMENT.md` **1255 lines / `f792bdd6bfc417e3`** · `DEFINITION.md` **4875 / `7fbde36cf36daf8d`** ·
`FORMULATION.md` **2397 / `36ae2fbc2875c9f4`** — recorded in the artifact, so a later round can tell a
moved number from a moved document without re-deriving it from git.

## the sentence I can no longer write

*"the rates could not be reproduced."* They reproduce to four decimal places against the parent tree,
and what looked like irreproducibility was a round measuring a document it then edited.

## NEXT

The pinning works and R756's finding survives, so the substantive debt R757 named is now half paid:
the **corpus** correction is verified and the **document** drift is quantified at 0.0016 for the one
document where it could be isolated. What is unpaid is the rest of R748–R756, whose numbers were each
computed on the narrow corpus and are individually recomputable by the method proven here — pin to the
round's parent, rebuild both corpora, recompute. That is mechanical, and the honest question is
whether it is worth the passes: the two headline numbers that moved are already corrected on the page,
and a round that recomputes seven more figures nobody has cited since would be spending compute to
tidy a ledger. Measure first which of those numbers any later round or deliverable actually reads,
and recompute only those — the unit is the number's downstream reader, not the number.
