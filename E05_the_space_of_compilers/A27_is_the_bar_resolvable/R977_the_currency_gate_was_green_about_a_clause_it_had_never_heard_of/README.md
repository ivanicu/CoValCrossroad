# R977 · the currency gate was green about a clause it had never been told about

**THE DECISION THIS MAKES SAFE.** Whether `DEFINITION.md` states clause ④ with the scope its own
measurements require. It now does — and the round is **production**, not another retraction: the
statement carries what R975 and R976 established, and the gate that certifies it went red before it
went green.

---

## The defect

`a_statement_is_current_with_the_arc.py` exists because a **consistency** gate cannot see
**currency** — a statement can match every artifact it cites and be wrong about every artifact it
does not. It read **PASS, 7 of 7**, while R975 and R976 sat committed and unmentioned.

⭐ **Its facts are a hard-coded list of six artifacts, so it has the very defect it was built to
catch, one level up.** You cannot grep for the absence of a fact you were never told about.

## The repair, and why the order matters

Both patterns were run against the **unrepaired** statement first. Neither matched. Only then was
the statement changed. **A repair that never turned the gate red would be decoration**, and the
round's exit code is wired to that: it returns 1 if either pattern matched the parent revision.

| fact | parent `HEAD` | working tree | verdict |
|---|---|---|---|
| R975 · clause ④ is overlap-limited | absent | present | **REAL — the repair moved it** |
| R976 · clause ④'s bar is design resolution | absent | present | **REAL — the repair moved it** |

The "before" is read with `git show HEAD:…`, so it is **recoverable, not my recollection**.

## Controls

| control | result |
|---|---|
| **POSITIVE** | R921's "2 legitimate comparators" present in **both** revisions — without it, "absent everywhere" could equally mean the parent's region failed to load |
| **NEGATIVE** | a runtime-assembled sentinel absent from both. Assembled from fragments because *documenting* an absent marker is what puts it in the corpus — this project did that three times |
| **ANCHORING** | `definition_matches_the_record.py` (340 assertions) still exits 0, which is the evidence that I **annotated** and did not edit the clause text (L81) |
| **TRANSITION** | gate exit **1 → 0** across the repair |

## What the statement now says about ④

- **Overlap-limited, not mean-determined** (R975): at δ = 0.01 held fixed, ④ stops removing once the
  arm is above the floor on ~40–50% of prompts; the interval widens 0.00255 → 0.01136 while the
  point estimate is pinned by algebra.
- **A closed form with no clause content and no corpus term** (R976):
  `φ* = (δ²N/(z·STEP)² − δ/STEP)/2`, within 1.5 grid steps on 13 of 14 cells.
- **Therefore any statement of ④'s reach must carry `N` and `δ`** — R821's headline is a fact about
  a 968-prompt design; at N = 242 the same δ is defeated near overlap 0.10.
- **Not established:** whether φ\* also depends on the corpus.

## A second defect, found by running rather than reading

The gate returned **2** on a genuine FAIL. In this suite `run_all.py` buckets `rc=2` as
**UNRUNNABLE** — *"a check with no population has not passed, it has not run."* A stale statement is
the **opposite** claim: the gate looked, and the corpus violated it. Fixed to **1**, with the
matcher-broken path keeping 2 because that one genuinely is unrunnable.

⚠ The file's own docstring declared the wrong contract too (*"Exit 2 on failure, never 1"*), so the
declaration was repaired in the same commit — a fix that reaches the code and not the sentence
describing it is how the next reader gets it wrong again.

## ⚠ The unit gap, stated rather than implied by a green run

| | |
|---|---|
| instrument's unit | a regex matches inside the statement region |
| claim's unit | a reader can tell the scope of clause ④ |

**These are not equal.** This round shows the sentence *arrived*. It cannot show the sentence is
*readable*, and it says nothing about whether R975's and R976's facts are **true** — that is their
business, not this round's.

## Alternatives considered

**Make the fact registry automatic — discover artifacts rather than list them.** This is the real
repair and it is deliberately not attempted here: a discovery rule needs its own false-positive
measurement over ~900 round artifacts, and bolting it on inside a production round is how an
unvalidated instrument enters a gate. Named in the NEXT line instead of implied by this green run.

**Edit the clause text at the head to carry the scope inline.** Refused: that text is anchored by
340 assertions, and L81 says annotate rather than rewrite. The scopes section already exists for
exactly this, and it already carried ①②③.
