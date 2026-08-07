# R600 · The gate passes because it does not look, and looking would break it for the wrong reason

**Decision this makes safe:** whether to widen the provenance gate's citation regex. **No — and the
reason is measured, not argued.**

**8 rounds are referenced by `STATEMENT.md` and invisible to its own gate. 4 of them would be
REJECTED if it saw them.**

| round | gate's verdict if visible | why | what it carries |
|---|---|---|---|
| **R294** | ⛔ reject | no `world` **or** `verdict` | **the scope-constants table governing every claim row** — 41 arms · 968 prompts · 46 objects |
| **R288** | ⛔ reject | no `world` **or** `verdict` | the six-target sweep artifact behind R558 |
| **R398** | ⛔ reject → **repaired** | records under **`verdict`**, not `world` | *"one release was never a wall — it was a query nobody ran"* |
| **R427** | ⛔ reject → **repaired** | records under **`verdict`**, not `world` | the first number on the **second corpus** |
| R340 · R433 · R437 · R544 | would pass | settled | — |

## ⭐⭐⭐ The structure, and it is the whole R594→R600 arc in one sentence
**The gate's rule is "no `world` ⇒ reject", over a field R594 measured at 44% prevalence.** So:

> **Widening the regex would make the gate FAIL on rounds that are not defective.**
> **The visibility hole is load-bearing in a way nobody chose.**

Two of the four are rejectable **only for a key name**. The other two are **census rounds** — R294
produces the 41-arm arm space, not a claim — **and the rule has no category for "this round is a
measurement, not an assertion."**

## The fix was measured BEFORE it was applied
Reading `verdict` as well as `world`:

| | rejectable before | after |
|---|---|---|
| the **84 visible** rounds | 1 | **1** — *0 newly broken, 0 repaired* |
| the **8 invisible** rounds | 4 | **2** *(R288, R294 remain)* |

⭐ **It is inert today and correct later** — applied for that reason, with the measurement in the
gate's own comment. **The regex is deliberately left alone**, because widening it now would fail on
two census rounds for a category error rather than a provenance defect.

## ⛔ Check #199 caught me misdescribing my own code
R599 closed with *"`live` depends on the literal string `SUPERSEDED`"*. **The regex has four
alternatives** — `SUPERSEDED|superseded|no longer the definition|predates` — so a round built on that
sentence would have measured the wrong rule. **And its population was wrong**: only corrections
attached to a *definition-asserting site* can move the count, not the deliverable's corrections at
large. Both recorded as Closure, neither pursued.

## ⭐ And checking before assuming saved a round built on a false premise
§4's row says *"the definition has never been checked against an object other than the one it was
written from."* **It has**: R427, R433, R466 are transport rounds — and **R433's verdict is
`W-LOSES`.** The cross-object test exists and clause ②'s subject lost on the second release. **I was
one command from designing a round to do work already done.**

## Controls
| control | returned |
|---|---|
| **positive** — a round matched by both regexes is in neither difference set | **PASS** |
| **positive (plant)** — a page citing `(R466)`, known UNVERIFIED | seen by the gate **and** classified rejectable — **PASS** |
| **g=0** — a page with no citations | **0 cites** — PASS, it can fail |
| **negative** — 3-digit ids that are not round directories | **0** — nothing spurious to exclude |
| **placebo** — 4-digit ids | `R1234` matches as `123`; **0 four-digit ids exist on the page**, so the collision is inert — *named, not waved away* |

**MULTIPLICITY:** 2 regexes × 92 ids + 3 control corpora. **8 invisible, 4 rejectable, 2 repaired.**

**IMPOSSIBLE, named:** *"the page LEANS on this round"* is not decidable from a mention — a round may
be named in passing. **Every member's surrounding text is printed so a reader can overrule, and the
count is an upper bound.**

## The sentence I can no longer write
> *"all 84 cited rounds carry a settled verdict."*

True **of what the gate looked at**. Eight more are referenced and unexamined, and half of those it
would refuse.

## NEXT
The gate's rule is binary — settled or rejected — and **two of the eight are neither: they are census
rounds that produce a population, not a verdict.** Count how many of the corpus's 589 rounds carry
**no verdict-shaped key at all**, because if that class is large the gate needs a third category
before its regex can ever be widened, and if it is small these two are simply owed a `world`.
