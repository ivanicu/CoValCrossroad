# R1033 — a third prompt-blind comparator costs **zero**, and it removes 6 of the 9 extension arms

**The decision this round makes safe:** whether R1032's wording choice was load-bearing. **It was** —
and the reason is that the certified set can be enlarged for free, which three committed rounds
implied it could not.

## ⛔ The derivation, before any compute

`score.yvec(sat_p, idxs)` sums satisfaction over an **arbitrary criterion index subset**, and
`sat_genericpool16.npz` holds all 16 × 4 × 968 cells. So **every subset of pool16's criteria is a
fixed checklist** — prompt-blind **by construction** under R918's own `fixed` predicate, since a
constant selection cannot vary with the prompt — **and it is already scored.**

**A third certified comparator costs 0 judge calls, not `968 × 4 × k` (R1027).**

## Result — ⭐ **World B**

| k | subsets | min admits | median | max |
|---:|---:|---:|---:|---:|
| 1 | 16 | 28 | 33 | 43 |
| 2 | 120 | **17** | 30 | 33 |
| 3 | 560 | **17** | 29 | 33 |
| 15 | 16 | 28 | 28 | 28 |
| 16 | 1 | 28 | 28 | 28 |

**35 of 713** subsets are stricter than `generic`'s **24**. The strictest admits **17** at **k=2**.

### And it removes 6 of the 9 committed extension arms

| | |
|---|---|
| **fall** | `topw_k3`, `topw_k4`, `topw_k4_detA`, `topw_k4_detB`, `topw_k6`, `topw_k8` |
| **survive** | `coval_core`, `coval_core_2bA`, `coval_core_2bB` |

**The three survivors are the released core and its two twins.** So under a comparator that costs
nothing to add, the definition's extension collapses to the instance and its duplicates.

⭐ **Dropping `EVERY` in R1032 was load-bearing, not cautious** — the SET wording excludes arms the
`generic` wording admits, and the separating object is free.

## Controls

- **POSITIVE** — two committed anchors through the subsetting path: the full 16-subset reproduces
  `genericpool16`'s **28**, and `generic` reproduces **24**: **PASS**. Either breaks on any drift.
- **NEGATIVE (selection)** — the strictest of 713 is a **maximum over a search**. Selected on prompts
  1–484, re-measured on the **held-out** 485–968: winner admits **15**, `generic` admits **24** there.
  **Strictness holds out.**
- **SEEDS** — stricter than `generic` under all **3**.
- **MULTIPLICITY** — the **distribution per size** is reported, not the winner alone; the family is
  pre-registered **by size**, never by outcome.
- ⚠ **Cost:** the first implementation re-bootstrapped 96 arms for each of 713 subsets and did not
  finish. Removed by an **identity, not an approximation** — a bootstrap replicate's mean is linear,
  so `mean(v_a − v_c) = mean(v_a) − mean(v_c)`; each arm is bootstrapped once per seed. Same numbers,
  ~700× less work.

## What does NOT fall

**R1026 is not contradicted.** It measured that **2 of 96 arms in the release** are prompt-blind, and
that stands. What falls is the **implication** carried beside it and in R1027's cost line — that a
third comparator must be **built and scored**. For this family it must not.

## What this cannot say

Whether a stricter comparator exists **outside** pool16's criteria. That needs new criteria written
and scored at `968 × 4 × k` judge calls. **N/A, not planned.** This round bounds what is reachable
**from the committed cells**.

`run.py` · `results/free_third_comparator.json`
