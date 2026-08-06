# R849 · does the PROPOSED clause survive the test it was written to pass?

**Arc A24 — what the definition costs.**

## ⛔ WHY — the arc's own question, aimed at my own wording

Entry 1368 showed **both** readings of ④ fail: strict excludes **0 of 42** (untested decoration, by
the register's own rule), permissive excludes **25 of 58 including `coval_core`** (empty extension).
It proposed a repair. **A proposal is a suggestion until its extension is counted**, and this arc has
condemned four clauses with one question — *name an admissible object this clause EXCLUDES.* **That
question now points at me, and it could have failed here.**

## ⭐ CONTROLS — all three required, all three passed

| control | result |
|---|---|
| **PLACEBO** the bar rule against itself | **+0.00e+00 exactly · PASS** |
| **POSITIVE** `oracle_k4` must satisfy ④′ | **True, margin +0.1390 · PASS** |
| **NEGATIVE** `random_k4_s0` must NOT satisfy | **True · PASS** |

⚠ **Selection is held out — the other writer's R843 remedy verbatim.** The bar rule is chosen on the
**ODD** annotators (`+mean_word_len+uppercase`, odd-half A2 **0.4785**) and every margin is evaluated
on the **EVEN** half (bar **0.4820**). Selecting the bar on the scoring set is the winner's curse; it
would **inflate** the bar and **deflate** the extension — i.e. it would **flatter** the clause by
making it look more selective than it is.

## ⭐⭐ RESULT — world C. 1,078 prompts · reference class R = 394 rules, named in full.

| | |
|---|---:|
| arms tested | **99** |
| surviving BH at q=0.05 | **77** (22 non-survivors) |
| **EXTENSION of ④′** | **41** |
| **arms EXCLUDED** | **58** |
| `coval_core` | **+0.0794 [+0.0667, +0.0915] — SATISFIES** |

⭐ **The extension is strictly between 1 and 99**, so ④′ is neither the *describes-the-instance*
failure nor decoration. **It excludes 58 admissible objects** — which is exactly what the register
demands and what neither reading of the original ④ could do.

## ⭐⭐⭐ THE NEGATIVE CONTROL IS THE ARGUMENT FOR THE MARGIN FORM

`random_k4_s0` has a **positive point estimate: +0.0057.** Under the original wording — *"scores
better than"* — a point comparison **admits it**. Under ④′, its interval does not exclude zero and it
is **rejected**.

⭐ **So the margin form excludes an admissible object that the original form admits, and that object
is a random arm.** The original clause would have called a random baseline "better than every rule
computable from responses alone."

## ⚠ WHAT THIS DOES *NOT* CLAIM

- **41 of 99 is not "selective enough to define a core."** It is one clause of four; ①②③ do the rest.
  **The claim is that ④′ does definitional WORK, not that it alone identifies a core.**
- **The extension is scoped to this reference class R.** A richer R — char n-grams, per R825 — moves
  the bar up and would shrink it. **The clause's own wording requires R to be stated, and this is R.**
- **No external gold standard exists** for "is this really a core", so **construct validity is
  untouched** and is not claimed.

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| construct validated | an external gold standard for corehood |
| cross-release | a second release |
| causally identified | an intervention on the compiler |

⚠ **N/A with what each would require — never "planned".**
