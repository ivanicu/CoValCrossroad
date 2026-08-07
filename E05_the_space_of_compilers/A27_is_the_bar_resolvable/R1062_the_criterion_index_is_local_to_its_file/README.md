# R1062 — the criterion index is LOCAL to its file. ⛔ **Every cross-file number in this line is void — including R1061's own headline, written one round ago.**

**The decision this round makes safe:** whether R1061's prescribed repair (swap in `sat_generic`)
should be executed. **It must not be.** It would compare two measurements whose labels are unrelated.

## The check that killed it, in one command

| | |
|---|---:|
| shared `(criterion, letter)` keys between `sat_generic` and `sat_full` | **15,488** |
| **disagree** at 1e-12 | **14,878 = 0.9606** |
| disagree at 1e-6 | **14,878 = 0.9606** (the verdict does not rest on last bits) |

⭐ **The integer `i` in `(i, letter)` is a POSITION IN THAT ARM'S OWN CRITERION LIST, not a global
criterion id.** `generic`'s criterion 0 and `full`'s criterion 0 are different criteria sharing an
index.

**And no correspondence repairs it.** Searching all `4 × 39` pairs for a value-preserving match:

| generic criterion | closest full criterion | mean \|Δ\| | |
|---:|---:|---:|---|
| 0 | 30 | 0.1217 | no match |
| 1 | 34 | 0.1495 | no match |
| 2 | 32 | 0.0977 | no match |
| 3 | 34 | 0.1260 | no match |

**0 of 4 exact matches.** World C.

## ⛔⛔ What this retracts, and it is mine from one round ago

**R1061's headline is withdrawn**: *"the true comparator scores 0.6632 and the bound binds five times
harder."* That number read **one file's comparator against another file's subsets** — a cross-file
comparison, computed **one round after I wrote that cross-round numbers must not be mixed without
re-derivation**.

⭐ **The rule was right; I applied it to the wrong grain — rounds, not files.** R1060 refused to quote
across *rounds* without re-deriving. R1061 quoted across *files* without checking they share an index
space.

## ⭐ And what this restores

**R1060's margins are internally valid after all** — a single file, one consistent index space. Only
its **label** was wrong: `comparator` should read **`full` restricted to its own first four
criteria**. Its bound stands as originally reported, neither five times harder nor softer.

**R1059's `0.5514`** remains the real `generic`, read from its own file, and is not comparable to any
`sat_full`-derived number.

## Controls

- **POSITIVE** — a file against **itself** must show **0** disagreement: **True**. A comparison that
  cannot return *identical* cannot evidence *different*.
- **NEGATIVE** — two different arms must disagree somewhere: **True**.
- **PLACEBO** — a criterion matched against itself has distance exactly 0.
- **NOISE FLOOR** — reported at **both** 1e-12 and 1e-6; identical, so the finding is not a
  floating-point artefact.
- **MULTIPLICITY** — the correspondence search covers **every** generic × full criterion pair, not a
  sample.

## IMPOSSIBLE here

- **recovering what each index MEANS** — the criterion **text** is not in these files.
  ⭐ **SETTLES: IN-RELEASE** — `data/conversation_rubrics.jsonl` carries the rubric text, so a global
  criterion identity is obtainable by joining on **text** rather than position. **Unattempted, not
  impossible**, and it is the only route that makes any cross-arm criterion claim admissible.

`run.py` · `results/index_locality.json`
