# R651 · A shape label cannot carry a claim about provenance — R650's "only" was wrong by 32×

**Decision this makes safe:** whether the impossibility register gains one narrow entry (3 sites
needing a caller) or a wide one. **Wide: 98 of 192 unresolvable sites are inter-procedural, and 95
of them are outside the class R650 named.**

## The number, with its scope

| | |
|---|---|
| **INTER** — the read path reaches a parameter or a call's return | **98 / 192 · 51.0%** |
| **INTRA** — every binding is in the same function; only the evaluator is missing | **94 / 192 · 49.0%** |
| **INTER outside R650's `function ARGUMENT` class** | **95** — the line said **0** |

Population: R650's 192 unresolvable read sites across 324 rounds · instrument: an `ast` dependency
closure inside the enclosing function · baseline: R650's published census, **re-derived
independently here and required to match** · regime: this sha.

## ⛔ Check #252 — the retracted sentence, verbatim

> *"the three sites reading a path from a function ARGUMENT are **the only** class whose resolution
> is genuinely per-call-site … **every other** class above is a missing feature."*

`3` was computed. **`the only` and `every other` were not.** And they rest on labels assigned by the
**shape of the read expression** — which cannot say where a value comes from.

## The cross-tabulation the line begged for

| R650 shape label | INTER | INTRA |
|---|---:|---:|
| an element of a collection built at runtime | **24** | 3 |
| a name bound by nothing resolvable in scope | **20** | 34 |
| a loop variable over an unresolvable iterable | **19** | 18 |
| a `base / literal` whose base is not statically known | **13** | 32 |
| the result of a call: `Path(...)` | **11** | 0 |
| a comprehension variable | **6** | 6 |
| **a function ARGUMENT** | **3** | 0 |
| `joinpath(...)` · `next(...)` | 2 · 0 | 0 · 1 |

⭐ **Every shape but one contains INTER members.** The labels are not noise — `Path(...)` is 11/11
and `collection built at runtime` 24/27 — **but "the only" was false by a factor of 32.**

## ⛔⛔⛔ Three defects in the apparatus, all found by the replication control

| | v1 | cause |
|---|---|---|
| **census** | `355 ≠ 354` | **two different self-exclusions.** R650 excluded *itself*; R651 excludes only itself, so R650's own site was in my population and could never be in R650's. Compared on the same population: **364 = 364.** |
| **key** | 364 records → **354** pairs | **`(round, line)` is not an identifier.** 10 sites vanished into a `set` before any comparison. Repaired to a multiset, and the *join* is now admitted per key only when the baseline's unresolvable count equals the sites found there — measured: **0 ambiguous**, so the join is proven safe rather than assumed. |
| **classifier** | 108 INTER | **a bool cannot be a path.** The closure walked the whole defining expression for any non-pure call, so a comprehension's *filter* — `[x for x in d.iterdir() if x.is_file()]` — made the value "depend on the return value of `is_file(...)`". **14 of 108 INTER verdicts were manufactured this way.** |

## Controls

| control | returned |
|---|---|
| **positive-1** — independent re-derivation of R650's census (multiset, same population) | **364 = 364** — PASS |
| **positive-2** — R650's 3 `function ARGUMENT` sites | **3/3 INTER** — PASS |
| **g=0** — a function with no parameters | **INTRA** — PASS, it can return INTRA |
| **negative** — a path from a module constant | **INTRA** — PASS, *not everything is inter-procedural* |
| **placebo** — a parameter that exists but is never reached | **INTRA** — PASS, *presence is not reachability* |
| **addressability** — keys where a resolved sibling shares the line | **0** — the join is exact |

**MULTIPLICITY:** 1 classifier × **192 sites** + 5 controls + 14 call-site counts; the INTER
evidence table and the full cross-tab are published, non-survivors included.

**IMPOSSIBLE, named:** whether a caller passes a *constant* is decided per call site, and calls from
outside the module are not enumerable here. **Call-site counts are a LOWER BOUND** — measured 1× for
most INTER members, 2–4× for `load`-style helpers.

## The sentence I can no longer write

> *"three sites need the caller; everything else is a missing evaluator feature."*

**Ninety-eight need the caller.** Extending the evaluator — the whole specification curve R650 drew
— tops out at **49% of the remainder**, not 100%.

## What this does to R650's specification curve — a DERIVATION, run here rather than deferred

R650's curve reached **100%** by assuming every failure class is a missing evaluator feature. **It
is not.** Under the partition:

- **true ceiling of any intra-procedural evaluator: `(172 + 94) / 364 = 73.1%`**, not 100%.
- sites needed to cross R650's pre-registered 50%: `ceil(0.5 × 364) − 172 = **10**`.
- largest **intra-only** class: **34** — and three classes clear 10 on their own (34, 32, 18).

**⇒ the 50% line is still crossed by ONE class, at 56.6%. R650's "the fork was the wrong fork"
SURVIVES this correction.** *Labelled a derivation: forced by the algebra given the census and the
partition, not a new measurement.* ⚠ I nearly shipped a NEXT line asserting the crossing needed a
class larger than 54 — **the threshold is 10, and I had every number needed to check it.**

## NEXT

**The `73.1%` ceiling assumes an evaluator confined to one function body, and 14 of the 98 INTER
verdicts turned on a call-return that a one-level caller inline would supply** — `load_json(...)`,
`find_src(...)`, `values(...)` are module-local helpers, not opaque runtime. **Measure how many
INTER sites become INTRA under exactly one level of interprocedural inlining**, because the
register's entry should name the *depth* at which a population stops being static, not merely that
it is not static at depth 0 — and the call-site counts already collected (1× for most, 2–4× for
`load`-style helpers) say the inlining is well-defined for at least some of them.
