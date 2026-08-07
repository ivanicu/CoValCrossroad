# R714 · the release ships `986` core instances, and the formulation's clauses do not share a unit

**`data/conversation_rubrics.jsonl` carries a `coval_core` for each of `986` conversations — objects
this site did NOT build, on disk in the release, untouched by this entire arc. ⛔ So
`STATEMENT.md`'s "THE RELEASE SHIPS ONE CORE" is true only at the ARM level: one core GENERATOR,
`986` core INSTANCES. ⭐⭐ And the formulation MIXES UNITS — F1 and F2 are predicates over a
generator, F3 over an instance — so it cannot be applied to any single object as written.**

## check #316 — the four rounds exist, and asking the line's own question broke its premise

✓ R696, R711, R712, R713 all exist with artifacts; the five pricings are theirs.

⛔ Its question — *"can a definition be attacked by a site that built the objects it is defined
over"* — **sent me to look for objects the site did not build, and there are 986.** The
impossibility register has used *"one released core"* as a hard limit round after round.

## the object

| field | instances | k distribution |
|---|---|---|
| `coval_core` | **986** | `{2: 1, 3: 43, 4: 942}` |
| `coval_full` | 986 | k 4–43, 32 distinct values |

## ⭐⭐ the unit of each clause — a READING of its wording, not a measurement

| clause | unit | why |
|---|---|---|
| **F1 provenance** | **GENERATOR** | *"the criteria were SELECTED without reading the outcome labels"* is a predicate over a **selection procedure** |
| **F2 behaviour** | **GENERATOR** | *"BEAT a baseline that never sees the prompt"* needs scores **across prompts**, so it ranks a procedure |
| **F3 size** | **INSTANCE** | *"more than one criterion, no more than the release's maximum"* is a predicate over **one list's cardinality** |

**2 distinct units among 3 clauses. A definition whose clauses range over different objects cannot be
applied to any single object as written — and no round in this arc has said so.**

## portability — the first application of any clause to objects we did not build

| clause | evaluable on the 986? | result |
|---|---|---|
| F1 provenance | **NO** | needs a provenance record the rubric file does not carry |
| F2 behaviour | **NO** | needs per-arm scores the rubric file does not carry |
| **F3 size** | **YES** | admits **1.0000** of the 986 |

**1 of 3 clauses is evaluable here. The other 2 are reported NOT EVALUABLE, never as passing.**

⚠ **And F3 admitting all 986 is WEAK evidence for F3** — its ceiling was read off *this release's
card*, so admitting *this release's* instances is close to circular. What it establishes is that the
card's statement is **true of the data**.

## controls — 6 PASS, 0 FAIL, byte-identical across runs and across a changed hash seed

| control | returned |
|---|---|
| **POSITIVE** | the card's own *"up to four, ~95% are four"* recovered from the file: max k = **4**, share at 4 = **0.9554** |
| **g=0** | a nonexistent field yields **0** instances — absence is not a silent empty pass |
| **NEGATIVE** | F3 on `coval_full`, the same file's other field: **rejects 0.9970** — the clause reads SIZE, not the file |
| **SHAM** | F3 with the bound removed (k ≥ 1): admits **1.0000** of both fields — the **bound** is what does the work |
| PLACEBO / UNIT | identical reads differ by 0 · instrument unit ≠ claim unit |

## specification sweep — 2 fields × 3 bounds, all reported

| field | bound | admits |
|---|---|---|
| `coval_core` | F3 `1<k≤4` | **1.0000** |
| `coval_core` | sham `k≥1` | 1.0000 |
| `coval_core` | `k==4` | 0.9554 |
| `coval_full` | F3 `1<k≤4` | **0.0030** |
| `coval_full` | sham `k≥1` | 1.0000 |
| `coval_full` | `k==4` | 0.0030 |

## registered vs observed

| | registered | observed |
|---|---|---|
| **A** core instances | 986 [1, 1000] | **986** |
| **B** F3 admission on objects we did not build | 1.00 [0.80, 1.00] | **1.0000** |
| **C** share at k=4 vs the card's ~95% | 0.955 [0.90, 0.99] | **0.9554** |
| directional | ≥1 clause NOT evaluable here | **HOLDS** |

## limits

- **F1 and F2 are NOT EVALUABLE here** and are reported as such, never as passing.
- F3's ceiling came from this release's card, so this is close to circular.
- **986 instances from ONE release is still one release.**

## impossible here

| criterion | what it would require |
|---|---|
| evaluating F1 and F2 on the 986 | a provenance record and per-arm scores the rubric file lacks |
| cross-release | a second release |
