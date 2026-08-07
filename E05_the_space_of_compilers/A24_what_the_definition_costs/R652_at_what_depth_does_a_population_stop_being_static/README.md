# R652 · A whitelist is not a theory — "98 need the caller" was 59, and 123 needed nobody

**Decision this makes safe:** what to build if read populations are to be resolved generally.
**Not an interprocedural analysis. A complete evaluator** — 64.1% of the unresolvable sites need no
caller at all, and only 4.7% are beyond any static depth.

## The partition, with its scope

| depth | n | % | what would fix it |
|---|---:|---:|---|
| **D0 pure-computable** | **123** | 64.1% | a complete evaluator *inside* the function. **No caller.** |
| **D1 caller-dependent** | **59** | 30.7% | a parameter or a module-local function — needs the call sites |
| **D∞ runtime** | **9** | 4.7% | nothing. File contents, `TemporaryDirectory`, `json.loads` |
| **UNKNOWN** | **1** | 0.5% | named, not bucketed: `R513_the_size_of_my_own_assurance_surface:30` |

Population: R650's 192 unresolvable read sites · instrument: an `ast` dependency closure classifying
calls by **source kind** *and* **call form** · baseline: R651's INTER=98 / INTRA=94 · regime: this sha.

## ⛔ The pre-registered KILL fired: `|D1| = 59 < 60`. R651's 98 is retracted.

**I will not reinterpret a threshold I set.** But the finding does not rest on it: **the count moved
by 39 sites**, so any threshold in `[60, 97]` prints the same verdict. *The knife-edge decides only
which word is printed.*

## ⭐⭐⭐ The cross-tabulation is structurally clean, and that is the real result

| R651 | D0 | D1 | D∞ | UNKNOWN |
|---|---:|---:|---:|---:|
| **INTER (98)** | **29** | **59** | **9** | **1** |
| **INTRA (94)** | **94** | 0 | 0 | 0 |

**Every one of R651's 94 INTRA sites is D0 — not one mislabelled.** The contamination is entirely
inside INTER, and it is one-directional. R651's instrument never called a static thing
inter-procedural *by accident*; it did so **by construction**, because `next(...)`, `str(...)`,
`set(...)`, `sum(...)` were absent from a hand-written `PURE` list.

> **A whitelist has no failure mode that announces itself.** Anything unlisted becomes "impure", and
> the count grows in the direction that makes the corpus look harder than it is.

## ⛔⛔ Check #253 — two errors in R651's closing line

| claim | truth |
|---|---|
| *"**14** of the 98 INTER verdicts turned on a call-return"* | **8.** And **14 was a different quantity** — the bool-predicate over-calls from a *previous version of R651's own classifier* (14 of 108). **A number carried across a repair into a population it was never about.** |
| *"`values(...)` … module-local helper"* | It is `dict.values()`. Measured: **`values` bare-called 0×, attribute-called 401×; `get` 0× and 506×.** R651's module-local test matched a **name** — a collision instrument. |

## The ceilings this replaces — a DERIVATION

*Forced by the algebra given R650's census and this partition. Could not have come out otherwise.*

| | |
|---|---|
| R651 published, on its INTRA=94 | `(172 + 94) / 364` = **73.1%** |
| a **complete intra-procedural evaluator** | `(172 + 123) / 364` = **81.0%** ← **D0, not INTRA, is the right numerator** |
| + resolving every caller (depth 1) | `(172 + 123 + 59) / 364` = **97.3%** |
| **irreducible** — runtime + unknown | **10 sites = 2.7%**, unreachable at any static depth |

## Controls

| control | returned |
|---|---|
| **population** — every unresolvable site classified | **192 / 192** — PASS |
| **positive** — the 3 `function ARGUMENT` sites | **3/3 D1** — PASS |
| **g=0** — no parameters, no impure calls | **D0** — PASS, it can return D0 |
| **negative** — `str(MODULE_CONSTANT)`, *the exact case R651 called inter-procedural* | **D0** — PASS |
| **placebo** — a path read **out of a file** | **D∞ (`RUNTIME: loads`)** — PASS, *inlining cannot recover it* |
| **coverage** — UNKNOWN call forms | **1**, named — PASS (threshold 20) |

**MULTIPLICITY:** 1 classifier × 192 sites + 5 controls + an **8-cell cross-tab, every cell
printed**, including the four zeros that are the finding.

**IMPOSSIBLE, named:** the *true* minimum depth of a D1 site needs its callers' arguments resolved —
so **D1 is an UPPER bound** on what needs the caller. Whether a D∞ site's file content was itself
static needs the file as it stood when that round ran, which is not recoverable — so **D∞ is a LOWER
bound**.

⚠ **And the honest limit of this round's own instrument:** `PURE` and `RUNTIME` are still *lists*.
What makes them a theory rather than a whitelist is that **anything unlisted falls to UNKNOWN and is
named**, instead of defaulting into a bucket. One site did. **A default is how a whitelist is
reborn.**

## The sentence I can no longer write

> *"98 of 192 unresolvable sites need the caller."*

**59 do.** **123 need only a better evaluator, and 10 need something no static analysis can supply.**

## NEXT

**`parameter pat` accounts for 14 of the 59 D1 sites and `rid` for 11 — 25 of 59 in two parameter
names.** If those two parameters are each passed a constant at every call site, 25 D1 sites collapse
to D0 and the caller-dependent count falls below half. **Resolve the arguments at each call site of
the functions owning `pat` and `rid`**, because D1 was declared an upper bound and this is the
cheapest place to find out how loose it is — and unlike the depth question, the answer is a
per-call-site constant that either is or is not there.
