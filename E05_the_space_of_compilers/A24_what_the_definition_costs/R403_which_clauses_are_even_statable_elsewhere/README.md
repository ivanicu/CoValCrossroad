# R403 — half the definition is a fact about CoVal's schema

**The decision this makes safe:** *which clauses can a second-corpus test even evaluate?* **Only ②,
③a and the size clause. The other three cannot be said there at all.**

## Result — `W_TRANSPORTS_PART`. Both detector controls pass. **No GPU spent.**

| clause | needs | CoVal *(positive control)* | **corpus two** |
|---|---|---|---|
| **①** better than a random draw of the prompt's **own rubric** | a per-prompt rubric | STATABLE | **NOT-STATABLE** |
| **②** better than a size-matched set that never read the conversation | responses + human target + criterion pool | STATABLE | **STATABLE** |
| **③a** no information from that prompt's own human labels | per-prompt human labels | STATABLE | **STATABLE** |
| **③b** …not from any **HALF** of them | **≥2 annotators per prompt** | STATABLE | **NOT-STATABLE** |
| **③c** …and not by way of a **rubric those annotators wrote** | a per-prompt rubric | STATABLE | **NOT-STATABLE** |
| **size** >1; 3–8 indistinguishable | a judge + a k sweep | STATABLE | **STATABLE** |

**3 of 6 clause-parts are unsayable on an object the definition was not written from.**

## ⛔ The prior question, sharper than the remedy as written

The failure table says: *per clause, name an admissible object this clause EXCLUDES.* **But before
asking what a clause excludes on a new corpus, ask whether it can be SAID there.** A clause whose
subject does not exist is **not satisfied and not violated** — it is **NOT-STATABLE**, a third value.
Folding it into either of the others manufactures a verdict. *This is the CONFIRMED / OVERTURNED /
UNVERIFIED discipline applied to the clause rather than to the evidence.*

## ⭐ The measured fact that decides ③b

**`max raters on any interaction = 1`** — **0 of 27,172** interactions carry ≥2 distinct annotators.
Clause ③b quantifies over *halves of the annotator set*. **You cannot split one rater in half.** This
was measured, not inferred from the schema.

## ⛔ CoVal's column is a positive control, not a finding

**That CoVal satisfies its own definition's preconditions is FORCED** — the definition was written
from CoVal, so every field it names exists there by construction. **Any `NOT-STATABLE` in CoVal's
column would have meant the detector was broken, not the definition**, and the round exits 1 on that
condition rather than reporting it.

| | returned |
|---|---|
| **PRESENCE (+)** | `prompt` in CoVal *and* `score` in corpus two — `PASS` |
| **PRESENCE (−)** | a fabricated field in **neither** — `PASS`. A detector reporting *absent* for everything would produce a dramatic result and no information |
| **DEGENERACY** | `binding` requires more than presence, so the deciding count is measured and printed |

## What this does to clause ①

① was already **DERIVED vacuous** on CoVal — the region where it could bind is empty by arithmetic
(0 of 41). **Now it is also unsayable elsewhere.** A clause that excludes nothing where it was born
and cannot be stated anywhere else is not a weak clause; **it is a description of one schema.**

## ⭐ What survives is exactly the load-bearing part

**Clause ② and clause ③a are both statable on corpus two** — and ② is the clause that carries the
whole boundary (33 of 42 exclusions, R360), with R401 showing it is powered there at **n = 26,789**
and R402 showing the harness can see it.

> **The transportable residue of the definition is: *label-free, and better than prompt-blind*.**

## ⚠ This round does NOT restate any clause

Rewriting a clause so it survives on a new corpus is an act of **definition**, not a measurement.
**Doing it in the same breath as the diagnosis is how a definition gets tuned to whatever object is
in front of it** — which is the very failure being diagnosed.

## Register

| criterion | status |
|---|---|
| **restating a clause to survive** | **N/A** — an act of definition, deliberately not attempted |
| **whether a statable clause HOLDS there** | **N/A** — needs the judge; that is the test R402 prepared |
| **a rubric for corpus two** | **MEASURED ABSENT** here rather than cited from R398 — *a cited absence is not a measured one* |

## The sentence I can no longer write

> *"the definition's clauses are about cores"* — **three of six are about CoVal's schema.** They are
> not wrong; they are unsayable off their home object, which no amount of measurement on that object
> could have revealed.

Artifact: `results/r403_clause_statability.json`, source-stamped.
