# R471 · the page can be written — the definition has a publishable core

**The decision this round makes safe:** whether this campaign's output is a definition or only an
instrument set and a ledger. **A definition, with its scope attached.**

## The question, made failable

R470 closed asking whether a one-page statement of what stands can be written **without any number
whose scope is currently UNVERIFIED**. That is §0.2's demand — *lead with what stands, never with the
ledger* — and it is answerable mechanically rather than by taste.

**Only two rounds in the arc carry `UNVERIFIED`: R466 and R467**, both on the id-join question, and
**both superseded** — R468 found the exact join, R469 characterised what it settles. So the page is
writable if it cites their successors instead.

## Result

`STATEMENT.md`, one page: the four clauses, their **types**, what each excludes, the extension as an
**interval with its convention named**, what is established about ② and about the arm space, the
instruments, and what the campaign has not done.

**`assurance/statement_provenance.py` — PASS.** All **14** cited rounds carry a settled verdict.

| check | returned |
|---|---|
| every `(R###)` citation names a non-UNVERIFIED round | **14 of 14** ✅ |
| **POSITIVE CONTROL** — the checker can reject | R466, R467 identified as rejectable ✅ *a gate that cannot fail certifies nothing* |
| no artifact / no world | treated as **failure**, not as a pass — *silence is not a pass* |
| **TRANSITIVE ANCHORING** | **16 of 16** decimal values also appear in `DEFINITION.md`, hence artifact-anchored by the existing gate ✅ |

⭐ **The transitive check closes the gap the gate itself declared.** Its stated limit is that it
checks *citations*, not *sentences* — a number mis-transcribed from a sound round would pass. Rather
than transcribe every value a second time, the gate requires each value on the statement to **already
appear** in the document `definition_matches_the_record.py` re-derives from artifacts. **A value in
both is anchored through the chain; a value only on the statement is named as an unchecked
transcription.**

## What the page says that this arc earned

- **The extension is [0, 1]** with the convention named, and **zero confirmed members** — stated on
  the page, not buried.
- **①②④ are checkable on an object; ③ is not.** A reader given a criterion set can verify three of
  four clauses.
- **② is a bound, not a point**: +0.0095 to +0.0191, sign-stable, and **more data does not resolve it**
  (α = 0.208).
- **The per-prompt advantage is real and unexplained**: replicates at 0.8419–0.8544, explained at 4.4%.

## Impossible here, named

- **checking the statement's sentences** — this gate's unit is the **round**; value-level checking is
  `definition_matches_the_record.py`'s, and keeping them separate is deliberate.
- **a verdict on whether the definition is CORRECT** — every result here is about its extension, its
  clause types and its scope. Correctness needs a standard outside it.

Findings and their scope live in `DEFINITION.md`. `STATEMENT.md` is the residue.
