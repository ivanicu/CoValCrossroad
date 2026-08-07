# R633 · Fifteen conclusions stand on instruments that have since changed

**Decision this makes safe:** the size of the obligation R632 named. **15 (round, module) pairs**,
against a pre-registered sweep threshold of 3. **World B.**

| | v1 (mentions) | **v2 (imports)** |
|---|---|---|
| rounds referencing an assurance module | 68 | **30** |
| stale (round, module) pairs | 44 | **15** |
| mention-only pairs removed | — | **163** |

⛔ **v1 matched the module name ANYWHERE in the source** — docstrings, comments, prose *about* a
gate. **That is a mention, not an import: R631's own lesson, committed one round later in a new
place.** ⭐ *The verdict survived the correction only because the threshold was 3 — at a kill of 20 I
would have reported a sweep that does not exist.*

## The repair history I asserted from memory
| module | commits |
|---|---|
| **`definition_matches_the_record`** | **77** |
| `attack_the_suite` | 23 |
| `manifest` | 17 |
| `statement_provenance` | **3** |

**My closing line claimed `statement_provenance` was "widened once, repaired once, clause added
later" — three repairs. Git shows exactly 3 commits.** ⭐ **The number was right and the method was
wrong**, which is the least instructive outcome available: *a memory that happens to be right is not
a checked memory, and from the inside I had no way to tell which it was.* And the actual churn
champion is a **different module with 25× the history** — the one my line never named.

## Where the exposure sits
`statement_provenance` **12** stale rounds · `definition_matches_the_record` **6** ·
`seed_filter_is_disclosed` **5** · `run_all` **4** · and a tail. *(v1's `_isolated` at 10 was pure
mention-matching and is gone.)*

## Controls
| control | returned |
|---|---|
| **positive** — a module with >1 commit exists, so a stale pair is findable | PASS |
| **g=0** — single-commit modules can never produce a stale pair | PASS — the test can return nothing |
| **placebo** — a module that does not exist | **0 pairs**, no crash |

**MULTIPLICITY:** every (round, module) pair + 4 controls, full list printed.

**IMPOSSIBLE, named, and it cuts BOTH ways:**
- **OVERSTATES** — a commit may be a comment or rename changing no behaviour, and a round can import
  a module without depending on the repaired clause. Every hit is printed with its commit subject.
- **UNDERSTATES, in the direction that matters** — **rounds with INLINE copies of a rule are
  invisible to an import graph**, and R630's ledger test was inline. **That is exactly how the R632
  case escaped**, so this measurement cannot see the class it was built to size.

## ⛔ Check #232 — third consecutive closing line describing my own tooling from memory
#230 *"outside every gate"* · #231 *"asked only the ledger"* · #232 *"widened once, repaired once"*.
**All three are claims about my own instruments, which is the subject matter of every recent round.**
*The closing line is where I stop reading and start remembering.*

## The sentence I can no longer write
> *"the count of un-re-run conclusions is known for exactly one instrument."*

**It is 15 pairs across 9 modules — and the import graph still cannot see the inline copies, which
is where the only confirmed case lives.**

## NEXT
The instrument's own blind spot is now the sharpest thing it produced: **inline rule copies are
invisible to an import graph, and the one confirmed stale conclusion (R630's ledger test) was
inline.** Grep the round corpus for **inline reimplementations of a gate's predicate** — a
`RETRACTIONS.md` read, a citation regex, a decimal extractor — and count how many rounds carry their
own copy, because that count bounds a class this round measured at zero by construction.
