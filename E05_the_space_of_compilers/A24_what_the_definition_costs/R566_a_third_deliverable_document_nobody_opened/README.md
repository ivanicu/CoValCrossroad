# R566 · There is a third deliverable document, and the provenance gate has never read it

**Decision this makes safe:** what the campaign's deliverable actually is.

**WORLD B.** `A23`'s README says every finding lives in **`E05/FORMULATION.md`** and
`RETRACTIONS.md`. **No round this session opened it.**

| document | size | distinct decimals | shared with STATEMENT |
|---|---|---|---|
| `STATEMENT.md` | 44.7 KB | 92 | — |
| `DEFINITION.md` | 185.2 KB | 522 | **92 — required** by the gate |
| **`FORMULATION.md`** | **156.2 KB** | **732** | **24 — checked by nothing** |

**24 shared decimals, past the pre-registered kill of 20.**

⭐⭐⭐ **`statement_provenance.py` contains zero occurrences of `FORMULATION`** — verified by grep.
It anchors the statement against `DEFINITION.md` alone. **A quantity could be stated one way on the
statement and another way in the formulation and no gate would see it.** P16: *one home per fact — a
number stated twice drifts, and the copy is never the one that gets fixed.*

## Controls
- **Positive** — a known statement value (`0.5640`, `coval_core`'s A2) is extracted, so the
  extractor is not blind and the overlap count means something. **PASS.**
- **Negative** — an invented decimal appears in none of the three. **PASS.**

⚠ **24 is an UPPER BOUND on duplication, not a duplication count.** Two documents may use the same
decimal for different quantities. **Which of the 24 are genuine collisions is unmeasured** — and the
structural fact is independent of that: **three documents, a gate spanning two.**

## ⚠ Two further findings from A23's README, recorded not fixed
- **It self-identifies as `A13`** while the directory is `A23`, and says *"28 rounds, R248–R275"*
  while the directory holds **35** (R248–R283). **Stale by 7 rounds and one renumbering.**
- **Its rounds are NOT superseded** — it records three closed decisions, including an MDE of
  **`[0.1250, 0.1250]`** with *"every substantive effect 3–30× below it"*, ⚠ **scoped to one
  detector**. **Whether that floor reaches A24's ~0.07 effects is UNMEASURED and is the open
  question this round hands forward.**
