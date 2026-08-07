# R694 · the definition is two parameters we chose, plus the sham

**⭐⭐⭐ Over 42 arms in 24 `(family, k)` cells, both ② and ②∧③ are irreducible in exactly **2** cells:
`coval_core` vs `coval_core_sham`, and `topw_k4` vs `topw_k4_sham`. **A memorising fit on those two
parameters scores 95.2% by construction** — so the definition is our own parameterisation, plus
precisely the sham distinction.**

## ⛔ A GAUGE TEST KILLED R693's PROPOSED ROUND AT ZERO COMPUTE
It proposed fitting `(family, k)` jointly and reading the accuracy as evidence. **12 of 24 cells are
singletons**, so a memorising fit's accuracy is forced by **cell cardinality**. *Could it have come
out otherwise? No.* **Reporting it would have been the arithmetic trap the standard opens by
forbidding** — and the attack ladder's cheapest rung has now been the most productive check in this
arc.

## ⛔⛔ AND THE GAUGE TEST ITSELF WAS WRONG, CAUGHT BY ABSURDITY RATHER THAN BY A CONTROL
I computed a memorising fit's errors as `sum(min(counts_per_cell))` — which **charges one error to
every PURE cell** — and it printed **4.8%**. A memorising fit **cannot** score below the 78.6%
majority floor; that impossibility is what exposed it. Correct: `len(cell) − max(counts)` → **95.2%**.
**An ARITHMETIC control now enforces `accuracy ≥ floor` for every reading**, so the next instance
fails loudly instead of needing to look absurd.

## THE CELL STRUCTURE (G3 — every reading, every mixed cell)

| reading | cells | singletons | ⭐ MIXED | memorising fit | floor |
|---|---|---|---|---|---|
| **②** | 24 | 12 | **2** | 95.2% | 78.6% ✓ |
| **②∧③** | 24 | 12 | **2** | 95.2% | 88.1% ✓ |

Both irreducible at **`coval_core / coval_core_sham`** and **`topw_k4 / topw_k4_sham`**.

Registered **A 2 [0,6] → 2, error 0** · **directional (②∧③ ≤ ②) HOLDS (2 vs 2)** · kill did not fire.

**Controls:** POSITIVE — a synthetic both-label cell → MIXED. **g=0** — a pure cell → **not** mixed,
*the detector returns both values*. NEGATIVE — an empty cell not counted. **ARITHMETIC** — memorising
fit ≥ floor for every reading → **PASS**. PLACEBO — identical.

## ⛔ REGISTERED POINT B IS **UNCOMPUTED**, AND A DRAFT SATISFIED IT BY RELABELLING
R360's ledger holds `clause2_admits` and `clause23_admits` — **not ③ alone**. My first draft set the
third reading to **the same set as ②∧③ under the label "③"**, and it printed as an independent
reading agreeing with the other two. **A duplicate wearing a third reading's name reads as
corroboration.** Removed; **B is reported as uncomputed rather than quietly dropped.** *§4's "a label
is not a description", committed in a dict key.*

## ⚠ THE UNIT GAP IS THE WHOLE READING
`(family, k)` is **our** parameterisation of arms **we** built. A mixed cell shows the clause is **not
reducible to those two parameters**; it does **not** show what the clause *is*.

## IMPOSSIBLE HERE
A parameterisation we did **not** choose would test reducibility properly. Every arm here is ours
except one.

## NEXT
Both mixed cells are sham pairs (`results/cells.json`, field `rows`), and R693 measured that ②
separates 2 of 5 sham pairs. Take the 3 sham pairs ② does **not** separate and compare each
sham's committed A2 mean against its arm's. A pair whose two means are equal is unseparable by any
clause, so the 2-of-5 would be a ceiling set by the shams rather than a limit of the definition.
