# R1002 · the only surviving wording rests on a class boundary we drew

**THE DECISION THIS MAKES SAFE.** Whether the arc's one surviving repair — entry 1368's *"the best
rule in a NAMED reference class R"*, instantiated by R849 — is a **definition** or a **boundary**.
**It is a boundary.** R is not closed under the predicate the clause quantifies over, and a witness
is exhibited by name.

---

## What R actually is

Re-enumerated from R849's own construction, reproducing its committed count **exactly**:

```
14 hand-picked lexical features
  bullets · colons · commas · digits · distinct_words · len_chars · len_words
  mean_word_len · newlines · parens · questions · sentences · ttr · uppercase

  30 singletons  +  364 signed pairs  =  394        R849 committed 394 — POSITIVE CONTROL PASS
```

⭐ **So R is: every linear rule in at most TWO of fourteen hand-chosen lexical features.**

## The witness

The clause says *"every rule computable from **responses alone**."*

**R825's char 3–5-gram TF-IDF + SVD predictor** is computable from responses alone, **is not in R**,
and is **known to beat the instance** (R825: bar 0.572335 vs `coval_core` 0.566477, 12 of 12 splits).

**⇒ R849's bar is a max over a PROPER SUBSET of what the clause names.**

## ⛔ The repair inherits the defect 1368 diagnosed, one level up

| | what was killed | what replaced it |
|---|---|---|
| **entry 1368** | *"every"* — ranged over a convenience family | *"the best rule in a NAMED class R"* |
| **here** | — | **R is a convenience family too** |

**Naming the class makes the bar honest and reproducible. It does not make it closed.**
⭐ **The definition's verdict on its own instance is a property of a boundary we drew.**

## ⭐ This is a DERIVATION, and it is labelled

A max over a superset is ≥ a max over a subset, **by definition**. No experiment can overturn the
closure failure. An experiment could only say **how much** the bar moves — and that is deliberately
**not claimed**, because R825's number is on its own 12 splits and R849's is on parity halves.
**Different splits, different units, not compared.**

## ⚠ Not the size axis — that is prior art

| round | finding |
|---|---|
| **R847** | enlarged the family once: bar **raised**, **not crossed** |
| **R848** | dose-response **+0.007412 per e-fold**, with an extrapolation whose own artifact key reads `extrapolated_n_for_core_D4_NOT_A_MEASUREMENT` |

R1001's NEXT asked about **enlargement**; the size axis is answered, so this round asks **closure**
instead and re-asks neither.

## Controls

| control | result |
|---|---|
| **POSITIVE** | re-enumeration reproduces **394 exactly** — this is what makes my reading of R *be* R849's R. A mismatch would have made everything here inadmissible |
| **PLACEBO** | R849's own selected bar rule `+mean_word_len+uppercase` tests as a **member** |
| **NEGATIVE** | `oracle_k4` is outside R **and** inadmissible under the clause. Without this, *"outside R"* alone would make **every arm in the release** look like a witness |

**Multiplicity: n/a**, labelled rather than omitted — this is a closure question settled by a single
witness. Nothing is selected over and no p-value is computed.

## ⚠ The one step a reader could reasonably dispute, stated rather than hidden in a boolean

R825's source touches the human ranking, because **scoring any rule needs it**. Reading the witness as
response-**only** is a judgement about what the **rule** consumes versus what its **evaluation**
consumes. It is R826's own framing — that artifact calls the family response-only — and it is
recorded in the artifact as an authorial judgement, not as a passing test.

## ⚠ Impossible here, with what it would require

**How far the bar moves once the witness is admitted.** It would require re-running R825's predictor
under R849's odd/even parity split. ⭐ **The closure claim does not need it** — closure is a
membership fact; the magnitude is a separate, empirical question.

**Construct validity — N/A.** This says the class is **not closed**, never that a closed class is
**achievable**. A class closed under *"computable from responses alone"* may be uncountable, which is
itself a fact about the clause rather than about this instantiation.

## Alternatives considered

**Score the witness on R849's halves and report the bar rise.** Refused *for this round*: it is a
different question (magnitude), it needs compute, and reporting a cross-split number as if it were
comparable is the units error this arc has already made and retracted.

**Treat "outside R" as sufficient for a closure failure.** Refused — that is what the negative control
exists to forbid, and without it the finding is vacuous.
