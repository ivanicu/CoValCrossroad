# R653 · D1 is where the dependency SITS, not where it RESOLVES — one level buys 16 of 59

**Decision this makes safe:** whether a one-level interprocedural inline is worth building.
**No. It answers 27.1% of the caller-dependent sites; 52.5% have callers that are themselves
dynamic and need depth ≥ 2.**

## The number, with its scope

| what one level of caller analysis does | n | % |
|---|---:|---:|
| **RESOLVED@1** — every visible call site passes a static value | **16** | 27.1% |
| **PARTIAL** — some call sites static, some not | **8** | 13.6% |
| **DEEPER** — no call site static; **the callers are dynamic too** | **31** | 52.5% |
| **CALLEE** — blocked by a module-local function's return, not a parameter | **4** | 6.8% |
| **VACUOUS** — no visible caller | **0** | 0.0% |

Population: R652's 59 D1 sites · instrument: `ast` argument binding (positional, keyword, and
**defaults**, which live in the definition) · baseline: R652's D1 = 59 · regime: this sha.

## ⛔⛔⛔ The round's own estimand was wrong, and it was caught before it shipped

v1 defined the winning class as **"COLLAPSES → the site is really D0 and D1 over-counted it."**
**False.** A site whose caller passes a module constant is **still caller-dependent** — no evaluator
confined to the function body can resolve it, which is precisely what D1 asserts.

> ⭐ **D1 = 59 is CONFIRMED, not over-counted.** What this round measures is a *different quantity*
> I nearly reported as that one: **whether going one level up ANSWERS the question.** For 31 of 59,
> it only moves it.

**And the verdict string typed a word it had not computed** — v1 called a 27.1% figure *"close to
the real count."* §4's `the verdict string is not a computation`; the descriptor is now derived from
the measured share against printed thresholds.

## ⛔ Check #254 — R652's closing line, one false clause

> *"…25 D1 sites collapse to D0 and **the caller-dependent count falls below half**."*

**59 − 25 = 34 = 57.6% of 59.** It falls below half **only of R651's retracted 98** (34.7%). *I
measured against a number I had killed in the same round, and the sentence read as true because the
wrong denominator was the one in my head.* The counts 14, 11 and 25 are correct — **the comparison
was the defect**, so this round tested the whole D1 population rather than the two names.

## Controls

| control | returned |
|---|---|
| **positive** — one call site passing a module constant | **RESOLVED@1** — PASS |
| **negative** — two call sites, one dynamic | **PARTIAL (1 of 2)** — PASS, *one good call site does not carry it* |
| **placebo** — a function **never called** | **VACUOUS** — PASS, ⭐ *`all([])` is True and the guard refuses it* |
| **g=0** — a parameter that does not exist | **DEEPER** — PASS, it cannot resolve |
| **kill** — RESOLVED@1 verdicts with 0 visible call sites | **0** — PASS, the count is not void |
| **world-C test** — VACUOUS + CALLEE | **4 of 59** (threshold 30) — informative |

⚠ **The vacuous guard passes its synthetic control and fired 0 times on the real corpus.** It
protected against a hazard that did not occur here — so on *real* data it is validated only against
an imagined case. Stated, not counted as a success.

**MULTIPLICITY:** 1 resolver × 59 sites × every visible call site + 4 controls + 2 kill checks; all
six classes printed including the two zeros.

**IMPOSSIBLE, named:** calls from another module are not enumerable from this tree — every round is
a standalone script by construction — so **VACUOUS means "no visible caller"** and **RESOLVED@1 is
an UPPER bound** on what one level buys. An exact answer needs a whole-corpus import graph that does
not exist.

## The sentence I can no longer write

> *"reaching the caller resolves a caller-dependent site."*

**It resolves 16 of 59.** For 31 the caller passes something dynamic, and the question moves up
rather than closing.

## NEXT

**The 4 CALLEE sites are blocked by a module-local function's RETURN rather than by a parameter, and
they were routed out of the resolver rather than through it** — `load_json`, `site_text`, `coverage`.
That is a *different* mechanism with a different fix: the callee's return expression must itself be
resolvable, which is the same intra-procedural question one frame over. **Classify each of the 4 by
whether its callee's return expression is D0 in its own body**, because if it is, the site resolves
with no caller information at all and the D1 label was attached to the wrong frame — and 4 is small
enough that the answer is exact rather than a bound, which nothing else in this arc has been.
