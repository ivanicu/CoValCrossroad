# R604 · Clause ②'s baseline is named with a string no scorer ever wrote

**Decision this makes safe:** which label the definition's baseline numbers are actually anchored to.
**Not the one the page uses.**

| candidate name for ②'s comparator | as a JSON **key** *(an arm a round scored)* | in a **string** *(a name a round quoted)* |
|---|---|---|
| **`POOL[0:4]`** — what `STATEMENT.md` says | **0** | 2 — **both register/scope audits of this page** |
| **`sat_genericpool16[:4]`** — what the scorers wrote | **13** | 3 |

**Artifacts containing both names: 0.** So whether they denote the same arm is **`UNVERIFIED` from
names alone — it needs the scorer, not a search.** The percentile **93.7** the page attaches to
`POOL[0:4]` was computed against the `genericpool16` label.

## ⛔ Two proxies of mine failed first, and the second I had already written the cure for
**① "scoring artifact" = "contains a decimal."** R472 and R560 are **register audits** whose artifacts
are full of compliance decimals, so `POOL[0:4]` was credited with a scoring artifact it never had and
the verdict fired **A ONE OBJECT, TWO NAMES**. Replaced with a **JSON-namespace** split: a name
appearing as a **key** is an arm the round scored; a name inside a **string value** is one it quoted.

**② The round scanned a population containing its own artifact.** R604's `tally` dict carries every
searched name as a key, so it credited `POOL[0:4]` to round **604** and fired the placebo on
`nevertheless`.

⭐⭐⭐ **R601 hit exactly this two rounds ago and I wrote the general remedy into the ledger as entry
497 — *a round may not be a member of the population it measures* — and then did it again.**
**Writing a remedy is not installing one.** It is now in the code rather than in the prose.

## Controls, final
| control | returned |
|---|---|
| **positive** — `topw_k4`, a known scored arm | **59** artifacts as a key — PASS |
| **negative** — an invented arm name | **0** — PASS |
| **placebo** — a prose-only word (`nevertheless`) | **0 total, 0 scoring** — PASS, the split can put something on the prose side |

**MULTIPLICITY:** 5 names × 424 artifacts + 3 control checks.

**IMPOSSIBLE, named:** two names denote one arm **only if a scorer says so.** Without re-running the
scorer this **bounds** the question and does not close it — which is why the verdict is *the label is
unanchored*, not *the baseline is wrong*.

## ⛔ Check #203
R603 closed with *"a rubric could be generated and a core selected from it, **which is what R433
did**."* **R433 generated the TREATMENT**, not the baseline. From its own table: `gen` 0.4590 · `sham`
0.4540 · `generic` 0.4497 · `length` **0.5135**; the resolved contrast was `gen − length`, and its
prompt-blind comparator was `generic`. **The measurement that line proposed was ill-posed.**

⭐ And reading R433 properly surfaced the sharper number: **`gen − generic` is clause ②'s own claim,
and it is +0.0093 [−0.0008, +0.0186] against MDE 0.0140 — NOT RESOLVED.** The clause names a bar its
subject cannot be shown to clear.

## The sentence I can no longer write
> *"②'s comparator is `POOL[0:4]`, at percentile 93.7 of its 1,820-subset class."*

**Percentile 93.7 is real.** The name it is attached to appears in nothing that computed it.

## NEXT
The two labels are plausibly one arm under a rename, and **the scorer can settle it where a search
cannot**: `corebench/score.py` and the rounds that built `genericpool16` define the arm
constructively. **Read how `genericpool16[:4]` is assembled and compare it to "the released pool's
first four by file order"** — if the construction matches, this is an untracked rename and the
percentile stands; if it does not, every ② number is against a comparator the definition does not
describe.
