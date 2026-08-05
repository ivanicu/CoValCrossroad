# R624 · C3-share is an inverted usability metric — optimising it optimises for asking less

**Decision this makes safe:** whether a looser binding unit rescues the anchoring rule. **No.**
Section scope makes the output **100% about numbers** — and buys that by **passing 361 pairs the
paragraph rule flags.**

| scope | pairs | pass | flags | C1 no-cite | C2 no-artifact | C3 mismatch | **C3/flags** | **laxity** |
|---|---|---|---|---|---|---|---|---|
| paragraph | 1058 | 49.2% | 537 | 447 | 4 | 86 | 16.0% | 82 |
| **section** | 919 | **91.1%** | 82 | **0** | **0** | 82 | **100.0%** | **361** |
| document | 777 | 96.3% | 29 | 0 | 0 | 29 | 100.0% | 392 |

**Pre-registered kill required BOTH C3 ≥ 33% and pass ≤ 90%. No scope meets both. World B.**

## ⭐⭐ The law this buys, and it generalises past this project
> **The share of flags that are "meaningful" rises monotonically as a gate gets weaker, because
> weakening removes the mechanical failure classes first.**

`C1` — *no citation in scope* — is **exactly** the class a wider scope eliminates by construction, so
`C3/flags` climbs to a perfect 100% at the moment the gate stops asking. **A metric that improves as
the instrument weakens is not a quality metric; it is a laxity metric with the sign flipped.** Had
this round reported `C3/flags` alone — the number R623's own NEXT line pointed at — **section scope
would have looked like a total success.**

⭐ *The laxity column is the whole finding: pairs a scope PASSES that the strictest scope FLAGS.*

## ⛔ The premise the previous round acted on was false
*"No current syntax binds a decimal to a specific round"* — **`DEFINITION.md` is built of `## R###`
records, and I have been appending one every round for the last ten.** The binding existed; I
declared it absent while writing into it.

⚠ **Two counts, both correct, of different things:** `^## R` matches **45**; any heading *naming* a
round matches **57** (and 1 in `STATEMENT.md`). The wider regex is what the rule uses, and the
difference is headings like `### ⭐ … (R### + R###)`.

## ⛔ And the negative control still fails at the new scope
`0.5451` in an `R294` section **still flags C3**. So even the output that is "100% about numbers"
contains at least one condemnation of a value `definition_matches_the_record` verifies — **section
scope does not repair R623's case, it only hides the other 447.**

## Controls
| control | returned |
|---|---|
| **positive** — a runtime-assembled fake decimal in an R-headed section | flags **C3** — PASS |
| **g=0** — the same section unmodified | **no such flag** — PASS |
| **placebo** — a section headed with a nonexistent round | **C2, not C3** — PASS |
| **negative** — a T1 value in its own R-headed section | **still flags C3** — ⛔ FAIL, reported |

**MULTIPLICITY:** 3 scopes × every pair × 3 causes across both documents + 4 controls. All reported.
⚠ **R622's contamination still not repeated** — the planted literal is assembled at runtime and never
persisted as a value position.

**IMPOSSIBLE, named:** *"this flag is a real error"* needs a reader per line **at every scope**, and
**C3 loosens as the scope widens** — which is precisely why laxity is reported beside it.

## The sentence I can no longer write
> *"C3's share of flags tells you whether the rule is about numbers."*

**It tells you how much the rule has stopped asking.** At the scope where it reads 100%, the gate is
passing 91% of everything.

## NEXT
Three rounds have tried to make provenance mechanical and each found the same wall from a new side:
**a check can bind tightly and flag prose, or bind loosely and pass fabrications, and the document's
existing structure does not support a middle.** The next move is not a fourth rule. **Take the 82
section-scope C3 pairs — the smallest honest flag set this project has produced — and read them**,
because 82 is a size a person can actually adjudicate, and whether they are errors or artefacts of
the value-position test is now the only thing standing between this arc and a provenance claim.
