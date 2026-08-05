# R599 · The deliverable was stating two different definitions of "core"

**Decision this makes safe:** which definition the deliverable asserts. **One, now — `② ∧ ③`,
agreeing with the artifact.** Before this round: **two.**

| site | asserted | vs artifact `②③` |
|---|---|---|
| `STATEMENT.md` line 90 *(claim table)* | **②③** | ✓ |
| `STATEMENT.md` line 165 *(formulation)* | **②③④** | ✗ **stale** |
| `DEFINITION.md` line 1820 | **②③④** | ✗ **stale** |
| `FORMULATION.md` | — | 0 sites |

⭐ **Found by reading the object, not by running a gate** — while R598's suite was still executing.

## The baseline is the artifact, not any document
R519's `results/` records, over 41 arms and 9 ②-passers:

| clause | drops among the 9 passers |
|---|---|
| ① | **0** |
| ③ | **4** |
| ④ | **0** |

**④ adds nothing — identical to ①.** So `② ∧ ③` is what the measurement supports, line 90 is
current, and the other two were written while ④ was still in and **never updated when R519 retired
it.** *A correction must reach the artifact that provoked it* — the retirement reached the claim
table and stopped there.

## ⚠ `definition_matches_the_record.py` passes
Its unit is **document vs artifact**, never **document vs itself** — so a deliverable can hold two
incompatible statements of its own central claim and clear the gate. R598 measured that same gate as
one of the four `DEFINITION.md` flips, so it *is* live; **it simply does not ask this question.**

## ⛔ Two recogniser defects, both caught by the positive control
1. **`(.{0,60})` with `re.S` consumed across sentence boundaries**, so `finditer`'s non-overlapping
   matches cannibalised each other — **3 planted sentences were found as 1.**
2. **It captured clauses the sentence RETIRES.** Line 90 reads *"The definition is ② ∧ ③. ① and ④ are
   retired"* and v1 recorded **①②③④**. **A recogniser that cannot tell assertion from retirement is
   measuring mentions, not definitions.** Fixed by cutting the tail at the first negation cue, with
   **both readings reported as a specification axis** — they agree.

## ⭐⭐⭐ And the repair exposed a conflict between two rules I hold
**L81 says annotate, never rewrite.** So after correcting both lines, the superseded sentences are
still in the document — and the count **did not move**: still 2 distinct sets, now over 5 sites.

> **Under `annotate-never-rewrite`, a metric counting ASSERTED sets can never reach 1.**

The estimand had to become **live** sets: a site is dead if a supersession marker follows it within
260 characters. **Live distinct sets: 1.** ⚠ The rule also marks the *annotations themselves* dead,
which is conservative — it leaves exactly the canonical statement standing.

*This was invisible until the repair landed and the number refused to move. A doctrine and a
measurement can be individually right and jointly incoherent, and only an intervention shows it.*

## Controls
| control | returned |
|---|---|
| **positive** — 3 planted sentences, 3 different sets | **3 sites, 3 distinct** — PASS |
| **g=0** — text with no such sentence | **0** — PASS, it can fail |
| **negative** — clauses mentioned but not defined | **0 sites, FPR 0.000** — PASS |
| **placebo** — nonexistent glyph `⑨` across all three documents | **0** — PASS |
| **specification axis** — negation trimmed vs raw | **agree** |

**IMPOSSIBLE, named:** *"this sentence ASSERTS the definition"* is intent, not string — a historicised
statement reads identically to a live one. **Every hit is printed verbatim so a reader can overrule
the count, and the count is an upper bound.**

## The sentence I can no longer write
> *"the deliverable states one definition of a core."*

It stated **two**, in two documents, for as long as ④ has been retired — and the gate named for
checking the definition could not see it.

## NEXT
The supersession marker is now load-bearing: **`live` depends on the literal string `SUPERSEDED`
appearing within 260 characters.** That is an untyped string rule over prose — **exactly what R594–R596
showed cannot be made sound.** Count how many of the deliverable's existing corrections use that
marker versus some other wording, because if most say something else, this round's `live` count is
measuring my last hour's phrasing rather than the document's state.
