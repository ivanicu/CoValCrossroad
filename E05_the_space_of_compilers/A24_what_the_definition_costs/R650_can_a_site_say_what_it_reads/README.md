# R650 · The fork was the wrong fork — a threshold on the instrument cannot decide a question about the object

**Decision this makes safe:** whether R649's binding test can be made general by resolving each
site's read population automatically instead of from a hand-written table. **The question as posed
is undecidable, and the specification curve is what shows it.**

## The number, with its scope

**172 of 364 file-read sites (47.3%)** state their own read population statically — population:
every `.read_text()/.read()/.readlines()` call in **325** committed A24 rounds; instrument: `ast`
plus a symbolic `pathlib` evaluator; baseline: R649's hand table, which resolved **1**; regime: at
this sha. **A resolved population is an UPPER BOUND** — a loop may `continue`.

## ⭐⭐⭐ And the pre-registered fork does not survive its own specification curve

| + resolve this class | n | cumulative rate |
|---|---:|---:|
| *(none — as built)* | | **47.3%** |
| a name bound by nothing resolvable in scope | 54 | **62.1%** ← **crosses the pre-registered 50%** |
| a `base / literal` whose base is not statically known | 45 | 74.5% |
| a loop variable over an unresolvable iterable | 37 | 84.6% |
| an element of a collection built at runtime | 27 | 92.0% |
| a comprehension variable | 12 | 95.3% |
| `Path(...)` result | 11 | 98.4% |
| a function argument | 3 | 99.2% |
| `joinpath(...)` · `next(...)` | 2 · 1 | 99.7% · 100.0% |

**World A** was *"the corpus is why R649 returned UNVERIFIED"*; **world B** was *"my code is."* They
were separated by a **resolution rate** — and a resolution rate is a property of **the resolver**.
**One more feature flips the verdict.** So the threshold measures how much code I chose to write,
and *"the corpus, not my code"* is **UNVERIFIED and unverifiable by any amount of running this
design.**

> This is the meta-separator firing: not *which world survives* but *the decomposition itself was
> wrong.* I would have reported world A — literally correct against the pre-registered line — as a
> fact about the corpus.

## ⛔ Check #251 retracted R649's own closing line

R649 closed: *"the hand-written table … is a control that fails toward `nothing to see`."* **It is
not.** R649 prints `1 further site(s) UNVERIFIED — population not re-derivable` and carries that
count into its verdict string. **UNVERIFIED is named, never folded into an acquittal.** I accused my
own code of P6's failure while the code was doing P6 correctly.

## ⛔⛔ Two positive controls failed, each naming a different defect

| control | v1 | cause |
|---|---|---|
| **POSITIVE-1** | `901 ≠ 900` | **the threshold was stale.** R649's 900 was hand-derived before this round's directory existed; R601's glob has no self-exclusion. **Corpus growth inside a control's threshold** — the third time this mechanism has moved a number (R636, R648). Repaired by **re-deriving** the expected value with R649's own hand method on today's tree: **902**, and the resolver returns 902. |
| **POSITIVE-2** | `UNRESOLVABLE` | **dead code by construction.** The per-loop branch that resolves `(d / "README.md")` was guarded by `elif direct is not None` — it could only run when the path did *not* depend on the loop variable, which is the one case it was written for. |
| **POSITIVE-2** *(again)* | `426 ≠ 425` | **a bound compared against an exact count.** The resolver deliberately does not model `if not d.is_dir(): continue`. The extra member is real: **`A23_…/R276_PREDICTION.md`**, a stray file matching the round-directory pattern. |

## Controls

| control | returned |
|---|---|
| **positive-1** — R601:104 vs the hand method re-derived on today's tree | **902 = 902** — PASS |
| **positive-2** — R601:109, a *different expression shape* | **426 = 426** — PASS |
| **g=0** — an empty program | **0 sites** — PASS, *the rate is undefined, not 100%* |
| **negative** — a hard-coded literal path | **RESOLVED n=1** — one file, not an invented population |
| **negative-2** — a path from a function argument | **UNRESOLVABLE** — PASS, *it refuses rather than guesses* |
| **placebo** — a glob over a nonexistent directory | **RESOLVED n=0** — PASS, *distinguishable from UNRESOLVABLE* |

**MULTIPLICITY:** 1 resolver × **364 sites** + 6 controls. **192 non-survivors typed into 9 classes
and reported in full** — a single reason string for 192 failures is not a grid.

**IMPOSSIBLE, named:** runtime-dependent populations (a path from a computed string, a glob pattern
built per iteration). Resolving them would require **executing 324 programs** — a different
instrument, not a harder version of this one.

## The sentence I can no longer write

> *"only 47.3% of sites resolve, so the corpus is why the binding test cannot be made general."*

**47.3% is a fact about my resolver.** The corpus's own contribution is not separated by this
design, and no run of it would separate them.

## NEXT

**The three sites reading a path from a function ARGUMENT are the only class whose resolution is
genuinely per-call-site rather than per-definition, and there are exactly 3.** Every other class
above is a missing feature; that one is a different *kind* of unresolvability — it needs the caller,
not more evaluator. **Check whether those 3 are called from a single site each**, because if they
are, the class is resolvable after all and the impossibility register has one fewer entry — and if
any is called from several, it is the first genuinely non-static read population in this corpus and
should be named as the boundary rather than counted with the rest.
