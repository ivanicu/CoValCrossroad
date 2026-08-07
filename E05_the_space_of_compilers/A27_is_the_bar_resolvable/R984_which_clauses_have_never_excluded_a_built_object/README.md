# R984 · two of the four clauses have never excluded an object somebody built

**THE DECISION THIS MAKES SAFE.** Whether ① and ④ do work on the inventory. **They do not** — each
binds only on an object that had to be constructed to make it bind. R440's *"the definition is a
pair"* survives a 2.4× population.

---

## The table

| clause | drops **passers** | drops **rejects** | population |
|---|---|---|---|
| **① size > 1** | **0** | 1 | 42 arms with a recorded `k` (**57 UNSCOREABLE**) |
| ③ no prompt labels | **10** | 0 | 21 arms with recorded provenance |
| **④ beats response-only** | **0** | 36 | 99 arms |

R440 committed **① 0/24 · ③ 4/0 · ④ 0/0** on 41 arms. The passer columns replicate exactly.

⚠ **The reject column for ① does NOT replicate — 1 here against 24 there** — because only 42 arms
carry a recorded `k` and most rejects are not among them. R440's subsumption claim ("① discriminates,
but only where ② already has") is **not re-established at this scale**, and saying so is the point of
reporting the column.

⭐ **③ is the only clause that cuts where ② does not**: 10 passers, 0 rejects. Orthogonal by
measurement, on a larger provenance set than R440's.

## And the reason ① and ④ look idle is not that they cannot bind

Both were **reopened** after R440 — and each by an object built for the purpose:
- **①** — R925 constructed **120 label-blind size-1 arms**; none clears ②.
- **④** — R821 **planted an arm below the floor**; ④ removes it, down to δ = 0.01.

Neither reopening came from the inventory. So the honest statement is not *"idle clauses"* but
**"clauses whose excluded objects exist only because we built them to check."**

## ⛔ The defect that inverted this round's headline, and the control that could not catch it

v1 reported **① drops 15 of 24 passers** — world B, the opposite conclusion.

`K.get(nm) is not None and K[nm] > 1` reads an arm **absent** from R360's ledger as **failing** the
clause. R360 covers **42** arms; this round scores **99**. Measured on the 15: **15 missing, 0
genuinely k=1** — and every one carries its own k in its name (`greedy_k8_fit1` has k = 8).

⚠ **My negative control passed throughout**, because it tested a `k` I *supplied* and never a `k` that
was *absent* — §4's *control validated on imagined cases*. The repair is both:
- three-valued scoring: unknown is **UNSCOREABLE**, never a drop (P6 — folding UNVERIFIED into
  OVERTURNED manufactures verdicts);
- **a new control that can catch it**: an arm with no recorded `k` must be unscoreable. It reports
  **57 such arms**, so the number is visible rather than absorbed.

## Controls

| control | result |
|---|---|
| **POSITIVE** | clause ② against its own admitted set drops **0** — the join is sound |
| **POSITIVE** | clause ③ drops **10** passers — the instrument can see a clause bite, so the zeros elsewhere are measurements |
| **NEGATIVE** | a synthetic k=1 arm **is** dropped by ① |
| **NEGATIVE** | a synthetic arm 0.05 below the floor **is** dropped by ④ |
| **NEGATIVE (new)** | an arm with no recorded `k` is **unscoreable, not dropped** — 57 such |
| **PLACEBO** | any clause against the empty set drops 0 |

Seeds: 3, and a drop counts only if **all three agree**.

## ⚠ What this structurally cannot say

*"Has never excluded a built object"* is a statement about **an inventory we built**. It cannot
separate

- a clause that is idle, from
- a clause whose excluded object nobody has constructed yet.

That distinction needs a **third party building arms without seeing the definition**, and it is the
sharpest thing this site cannot do. It is registered here, not deferred.

## Alternatives considered

**Score ① from the arm names, which visibly carry `k`.** Refused: parsing a name is a proxy for a
property, and the round that just caught itself scoring missing data as a verdict is the wrong place
to introduce a second inference. The 57 stay unscoreable until a ledger records them.

**Report ① as subsuming 24 rejects, following R440.** Refused: at this population it is 1, and
carrying the older number forward because it tells a tidier story is how a stale count survives.
