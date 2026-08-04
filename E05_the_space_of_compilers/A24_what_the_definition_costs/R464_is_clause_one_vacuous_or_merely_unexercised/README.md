# R464 · clause ① is **unexercised**, not decoration — and "0 of 41" is a fact about the arm space

**The decision this round makes safe:** whether clause ① should be carried at all. **Yes.**
`W-UNEXERCISED`.

## ⛔ Two things were checked before this round existed

**① The announced step is largely a lookup.** R463 proposed finding the provenance of the 37
unlabelled anchors "from the artifact keys the gate already reads." **23 of the 37 already carry a
source tag inside the gate's own code** (`clause1_excludes`→R347, `clause2_excludes`→R360,
`clause3_excludes`→R444). *Thirty-second announced step checked.*

**② And the worry that replaced it was a case-sensitive grep.** Counting `EXCLUDES` in
`DEFINITION.md` returns **1**, which reads as *"§4's per-clause remedy was applied once."* The
document carries a full per-clause table under a **lowercase** `| clause | excludes |` header — the
true count is **4**. **A grep is a measuring instrument**, and this near-miss is recorded because it
is the same class §4 lists three times.

## What the table actually shows

| clause | excludes | status |
|---|---|---|
| **①** better than a random draw of the prompt's own rubric | **0 of 41** | DERIVED |
| ② better than a prompt-blind set | 33 of 42 | MEASURED |
| ③ no prompt labels | 14 of 42 | DERIVED from source |
| ④ better than every response-only rule | all 7 on the second release | MEASURED |

§4, verbatim: *"name an admissible object this clause EXCLUDES. If nothing you have built is
excluded, the clause is untested decoration."* **Clause ① excludes nothing.**

⚠ **But "excludes nothing built" and "excludes nothing constructible" are different claims, and only
the second makes a clause vacuous.** That is what this round measures — and it is not forced:
whether a deliberately-failing object is excluded depends on the inequality's strictness and the
noise floor, neither decided in advance.

## Result

| arm | gap vs a random rubric draw | MDE | CI | |
|---|---|---|---|---|
| `coval_core` | **+0.0797** | 0.0172 | [+0.0677, +0.0915] | not excluded |
| `rubric_random` | **+0.0088** | 0.0172 | [−0.0032, +0.0207] | **straddles zero** |
| `rubric_worst` | **−0.2779** | 0.0190 | [−0.2914, −0.2651] | **EXCLUDED** |

> ⭐ **Clause ① is a real predicate with a real extension.** The adversarially worst rubric subset is
> excluded decisively. **So `0 of 41` is a fact about the ARM SPACE, not about the clause, and §4's
> "untested decoration" verdict does not apply — the clause is UNEXERCISED.**

## Controls

| control | returned |
|---|---|
| **g=0 / PLACEBO** — `rubric_random` is a draw from the *same process* ① compares against | gap **+0.0088**, CI straddles zero, not excluded ✅ *if the reference process excluded itself, the test would be mis-calibrated* |
| **NEGATIVE** — the released core must not be excluded | **+0.0797**, not excluded ✅ |
| **POSITIVE** — the adversarially worst rubric subset | **EXCLUDED** ✅ *if ① could not exclude that, it could exclude nothing* |

⚠ **`rubric_anti` is not a fourth arm.** Under a single human target, "anti-matches the human" and
"worst A2" **coincide by definition**, so the round's code maps one to the other and the two rows are
the same object. **Three distinct arms, not four** — reporting it twice would inflate the control
count, and that is a DERIVATION, not a measurement.

## What this does and does not establish

- **Establishes:** ① has extension; carrying it is not decoration; the document's `0 of 41` needs its
  reading narrowed from *"the clause does nothing"* to *"no arm we built lands in it."*
- **Does not establish:** that any real **generator** would produce an ①-failing object. **The
  excluded arm was built adversarially, on purpose** — which is the point of the test and also its
  limit.

## Impossible here, named

- **whether a real generator would ever produce an ①-failing object** — needs a generator; this round
  constructs adversarially instead, deliberately.
- **clause ①'s behaviour on the second release** — the rubric does not exist there (R433).

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
