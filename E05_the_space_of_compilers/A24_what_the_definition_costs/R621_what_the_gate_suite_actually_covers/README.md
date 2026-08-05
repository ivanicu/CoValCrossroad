# R621 · A fabricated number passes all six gates if you write it into the anchor first

**Decision this makes safe:** whether the assurance suite establishes that the deliverable's numbers
are real. **It does not.** The transitive anchoring can be satisfied **by writing into the anchor**,
and the anchor has no gate.

## ⛔⛔⛔ The laundering path, with its confound isolated
| arm | what changed | six gates say |
|---|---|---|
| **1** | orphan decimal + **UNVERIFIED** citation on `STATEMENT.md` | `statement_provenance` ⛔ |
| **3** *(confound)* | orphan decimal + **settled** citation, **not** in `DEFINITION.md` | `statement_provenance` ⛔ |
| **2** | same decimal **written into `DEFINITION.md` first**, then cited | **⛔ NOTHING FIRES** |

**Arm 3 is what makes this a mechanism and not a coincidence.** A settled citation alone is still
caught; only the `DEFINITION.md` write launders it. **`0.9187` is a number I invented in this
round's source, and it clears every gate the deliverable has.**

⭐ **The structure, and it is the whole point.** `statement_provenance` closes the transcription gap
**transitively** — a decimal on `STATEMENT.md` must also appear in `DEFINITION.md`, which
`definition_matches_the_record` re-derives from artifacts. **The chain's root was never checked in
the write direction.** *An anchoring argument is only as good as the anchor, and I built the chain
without ever asking whether anything guards its far end.*

## Coverage by intervention — one fixed mutation, five files, thirty cells
| file | flips | which gate noticed |
|---|---|---|
| `STATEMENT.md` | **1** | `statement_provenance` |
| `FORMULATION.md` | 0 | — |
| `DEFINITION.md` | **0** | — *(the gate named for it notices nothing)* |
| `RETRACTIONS.md` | 0 | — |
| an arbitrary round README | 1 | `every_round_is_committed` |

## ⛔ And the verdict string is wrong for the third time in four rounds
It printed **"A NEGLECT — FORMULATION.md flips 0 while an arbitrary round README flips 1"**. **The
README's flip is `every_round_is_committed` reacting to DIRTINESS, not to content** — it would fire
for any modification, including a correct one. **So the floor case flipped for a reason unrelated to
the defect class the mutation encodes, and the A-vs-B discriminator was void.**

**Corrected: content coverage under this mutation is 1 of 4 documents — `STATEMENT.md` alone.**

## Controls
| control | returned |
|---|---|
| **positive** — `STATEMENT.md` must flip ≥1 | **1** — the mutation is not inert, so a zero elsewhere is a measurement |
| **g=0** — the unmutated tree | **all six pass** — every flip is caused by M |
| **negative** — the tree returns to all-pass after each restore | **PASS**, checked after every arm |
| **placebo** — a mutation to a nonexistent path | excluded before running, no crash |

**MULTIPLICITY:** 5 files × 6 gates = 30 cells + 3 laundering arms + 4 controls. All reported.

⚠ **LOWER BOUND, NOT COVERAGE:** one mutation probes **one defect class**. A gate policing a file
against a different defect is invisible here, so `n_flip` **understates** coverage and **no file is
certified by a zero.**

## ⚠ The round is a member of the population it measures — twice
`every_round_is_committed` failed the baseline because **this round's own directory was untracked**,
and again once `results/` appeared. Staging it first is the workaround, but the structural fact is
worth recording: **a gate over working-tree cleanliness makes the suite non-idempotent for any round
that runs the suite.** Same class as R601 and R604.

## ⛔ Check #220
*"three consecutive rounds have been about the gate"* — **two.** R618 was the third-object
specification. **Fifth uncomputed count in nine closing lines**, and this one inflated my own drift
rather than excusing it.

## The sentence I can no longer write
> *"every number on the deliverable traces to a settled round."*

**It traces to a settled round ID and a matching string in a file nothing guards.** Those are not the
same claim, and the gate that reports the first reads as though it establishes the second.

## NEXT
The cheapest repair is not a new gate over `DEFINITION.md` — it is to make the anchoring
**directional**: a decimal in `DEFINITION.md` should have to match a value **re-derived from a
round's persisted artifact**, which `definition_matches_the_record` already does for the values it
knows. Measure first how many of `DEFINITION.md`'s decimals that gate currently re-derives versus how
many it merely reads, because if most are merely read, the laundering path is the normal case rather
than an attack.
