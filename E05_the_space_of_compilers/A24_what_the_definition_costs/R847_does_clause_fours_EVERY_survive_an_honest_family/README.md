# R847 · does clause ④'s "EVERY" survive an honest enlargement of the family?

**Arc A24 — what the definition costs.**

## ⛔ WHY — R406 found this defect in clause ②, and clause ④ has the same shape

R406: *"better than **EVERY** prompt-blind set"* had been tested against a **p99** bar, while the
**max** over 1,820 blind subsets is **0.5574753088** against a reference of **0.5546019830** —
between **18 and 182** subsets beat the bar the word "EVERY" was tested against.

**Clause ④ says *"better than every rule computable from responses alone"*, and R436 realises that
as a max over 30 hand-picked single-feature argmin/argmax rules.** A max over a convenience family
is not a universal quantifier — and nobody had said so.

⚠ **The attack carries the OTHER WRITER's control.** Their R843 found a **max over 1,820 subsets
scores higher on a pure-noise target than on the real one**. An enlarged-family search is exactly
that shape, so the noise arm here is **the kill condition, not a formality**.

## ⭐ CONTROLS

| control | result |
|---|---|
| **POSITIVE** human ranking vs itself | **1.0000 · PASS** |
| **NEGATIVE** reversed ranking | **0.2523 · PASS** — the scorer can return a low value |
| **NOISE ARM** identical search, pair labels shuffled | ran on **both** families; its max is what family size buys for free |

## ⭐⭐ RESULT — world B. 1,078 prompts, EVERY annotator, no fitting on labels anywhere.

| family | rules | best rule | A2 | noise max | **excess over noise** |
|---|---:|---|---:|---:|---:|
| **F0** — R436's committed | 30 | `min_ttr` | 0.4560 | 0.4412 | **+0.0148** |
| **F1** — + two-feature combinations | **394** | `+mean_word_len+uppercase` | **0.4801** | 0.4451 | **+0.0351** |

⭐ **The raw max moved +0.0241. The NOISE max moved only +0.0039.** So the gain is **not** a search
artifact: the excess over noise **more than doubled**, +0.0148 → +0.0351.

⭐⭐ **A mechanical enlargement — every normalised two-feature combination, no label fitting, so
"computable from responses alone" on any reading — raises the response-only bar by +0.0241.**

## ⚠ WHAT IS AND IS NOT ESTABLISHED

- **IS: clause ④'s bar understates the response-only supremum by ≥ +0.0241.** The word "EVERY" is a
  max over a convenience family, exactly as R406 found for clause ②. **The bar is a LOWER BOUND on
  the supremum, not the supremum.**
- **IS NOT: clause ④ is not flipped.** `coval_core` at **0.5664774812** still clears the enlarged bar
  by **0.0864**. **`crossed` = False.**
- ⚠ **IS NOT: the gap is not shown safe.** The first honest push closed **21%** of it
  (0.0241 / 0.1153). Triples, ratios and other transforms are **untested**, and the supremum is
  unknown and **≥ 0.4801**.
- ⚠ **A second, independent understatement:** F0's max here is **0.4560** against R436's committed
  **0.4512** — the difference is **using every annotator instead of 3 draws** (R841). So the
  committed bar was understated twice over: **+0.0048 from annotator sampling, +0.0241 from family
  size.**

## ⭐⭐⭐ THE FORMULATION CONSEQUENCE

**A universal clause whose bar is a max over an enumerated family must say so, and must report the
bar as a lower bound.** *"Better than every rule computable from responses alone"* reads as a
supremum and is implemented as a max over 30 rules — **and the number moves the moment anyone
enlarges the family in the most obvious way available.**

⭐ **This is the same defect in both universal clauses of the definition** — R406 measured it for ②,
this round measures it for ④. **The pattern is the finding: the definition's "every"s are searches,
and a search reports what it searched.**

## STRUCTURALLY IMPOSSIBLE HERE
| criterion | what it would require |
|---|---|
| the true supremum | an exhaustive characterisation of "computable from responses alone", which is not a finite set |
| causally identified | an intervention, not a re-scoring |
| cross-release | a second release |

⚠ **N/A with what each would require — never "planned".** ⭐ And the first line is why the bar can
only ever be reported as a **lower bound with its family named**.
