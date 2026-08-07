# R1018 · no commit landed while the currency gate was red — the sequencing error was a near-miss

**THE DECISION THIS MAKES SAFE.** Whether the sequencing failure found one commit ago — a check run
*beside* the commit instead of *before* it — ever let a bad state through. **It did not.** 21 of 21.

---

## ⚠ The NEXT it answers was not answerable as written

The previous commit asked whether the same error reached the currency and anchoring gates, *"readable
from how each is invoked in this session's commits."* **How a gate was invoked lives in shell history,
which the repository does not contain** — the same shape as R1010's *"intent is not in the record."*

⭐ **What is in the record is the CONSEQUENCE:** whether any commit landed in a state the gate would
have refused. A sequencing error that never let a red state through cost nothing; one that did has a
hash.

## The result

**21 commits** touched `DEFINITION.md` or its gate. Each was judged by **the gate as it existed at
that commit**, against **that commit's statement** — so a commit is measured by the rules it was
written under, not today's.

**Every one: GREEN.**

⭐ So the red-first discipline — *register the fact → confirm the gate goes RED → annotate the
statement → confirm GREEN → commit* — **kept the consequence at zero even though the order was
enforced nowhere but in my hands.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | today's gate against the **oldest** statement — which registers facts not yet written — returns **RED**. Without this, an all-green sweep is **silence, not a measurement** |
| **NEGATIVE** | the newest commit is **GREEN**, matching the live tree |
| **NOISE FLOOR** | **n/a**, labelled — exact verdicts over a finite commit list |

## ⚠ Method note: no checkout

Both files are reconstructed with `git show <sha>:<path>` into a scratch directory, with everything
the gate reads symlinked from the live tree. **A checkout in this repo already cost one incident**
(five epoch directories stashed in `/tmp` for twelve minutes), so the reconstruction avoids touching
the working tree at all.

⛔ The first staging attempt symlinked `E05_the_space_of_compilers` **after** creating it to hold
`DEFINITION.md`, and died on `FileExistsError`. E05 must be a **real** directory here — it is the one
being reconstructed — so its **arc subdirectories** are linked individually while the other epochs are
linked whole.

## ⚠ What this does not show

**That the gate was actually RUN before each commit.** It measures whether the state it would have
judged was acceptable — **the consequence, not the process.** The process question is unanswerable
from the repository, and saying so is the finding's boundary rather than a gap in it.

## Alternatives considered

**Report "the discipline works".** Refused — what is shown is that **the outcome was clean**, not that
the procedure is safe. The procedure has no enforcement point; it survived because I happened to
follow it 21 times. **A habit with a perfect record is still a habit.**

**Judge each commit by today's gate.** Refused: today's gate registers facts that later rounds
established, so every early commit would read RED for a reason that is not a defect. Judging a commit
by rules written after it is the same error as quoting a number without its scope.
