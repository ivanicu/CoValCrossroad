# R598 · `FORMULATION.md` flips zero gates — 156 KB no check in the suite can contradict

**Decision this makes safe:** stop treating the three deliverable documents as equally guarded.
**Two are gated, one is not**, measured by intervention rather than by reading the source.

| document | gates flipped when **emptied** | which |
|---|---|---|
| `STATEMENT.md` | **3 / 28** | `residue_debt` · `retraction_reaches_the_artifact` · `statement_provenance` |
| `DEFINITION.md` | **4 / 28** | the same three **+ `definition_matches_the_record`** |
| **`FORMULATION.md`** | **0 / 28** | — |

**WORLD C PARTIAL.** Emptying is the **maximal** mutation, so a zero is decisive: no lesser edit
could flip a gate that total deletion does not. **R566's finding stands after six rounds of gate
work.**

## ⛔ The instrument R597 proposed would have given the wrong answer
`grep` names `DEFINITION.md` in **9** scripts and `FORMULATION.md` in **1** — but that one is
`generate_round_index.py`, a **generator** that exits 0 regardless. **A script that OPENS a file is
not a GATE on it.** Instrument unit = *the filename appears in the source*; claim unit = *this
document's content can make the suite fail*. **Not equal**, and mutation is what closes the gap.

## ⛔⛔ One bug of mine produced three wrong numbers, and I invented a second mechanism for one of them
v1 ran the 59 scripts **concurrently in one tree**. **22 of the 59 write into the tree**, so every
run was reading a surface the others were mutating — L62, read isolation, not just write isolation.

| | concurrent (v1) | **serial (correct)** |
|---|---|---|
| baseline reproducibility | 57/59 | **59/59** |
| baseline passing | 19/59 | **28/59** |
| placebo flips | 1 (`source_stamp_is_current`) | **0** |

⭐⭐⭐ **And when the negative control failed, I diagnosed a "tree-change-sensitive gate" and built an
exclusion for it. There was no such gate.** The same concurrency bug caused the control failure, the
under-count of passes, *and* the false non-determinism. **One cause, three symptoms — and I invented
a second mechanism for the second symptom instead of asking whether one explanation covered both.**

**Confirmed independently on the live tree:** `definition_matches_the_record` and
`statement_provenance` each return `0 0 0` across three serial runs. **Stable. The instability was
mine.**

## ⚠ And my cost alarm was wrong in the same way
I measured `du -sh --exclude=.git .` → **7.7 GB** and raised an alarm about copying that six times.
**The sandbox is 321 MB**: the 7.3 GB is `.venv`, which `ignore_patterns` already excludes. **I
measured one population and made a claim about another** — the session's recurring error, this time
aimed at my own cost model.

## Controls
| control | returned |
|---|---|
| **baseline ×2 on the same tree** | **59/59 identical** — the suite is deterministic when run serially |
| **positive** — empty `STATEMENT.md` | **3 flips** — the harness can detect gating |
| **negative** — empty `NEXT_SITE.md` | **0 flips** — a flip localises to the document emptied |
| **placebo** — create a file that never existed | **0 flips** |
| **excluded** | 31 gates already failing in the baseline; only a gate that **passes** untouched can flip |

⭐ **31 of 59 assurance scripts fail on an untouched tree.** That is the live debt R561 found, now
counted — and it means **just over half the suite cannot gate anything at all** until repaired.

**IMPOSSIBLE, named:** construct validity for *"gated WELL"*. A flip proves a document's content can
fail the suite; it says nothing about whether the check is good. **R596 measured a gate that fired on
1 of 8 spellings and still "gated" `STATEMENT.md`.**

## The sentence I can no longer write
> *"none of them is gated by anything, since `statement_provenance` reads `STATEMENT.md` alone."*

**Two of three are gated**, and `DEFINITION.md` is gated *more* tightly than `STATEMENT.md`.

## NEXT
**31 of 59 gates fail on an untouched tree**, so the suite's protective surface is roughly half what
its file count suggests. **Partition those 31 by their exit code and first output line** — a gate
exiting 2 on an empty population is a different object from one exiting 1 on a real assertion, and
which of the two dominates decides whether the debt is repair work or deletion work.
