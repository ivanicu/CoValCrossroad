# R1057 — my own NEXT was a derivation. Built the world where `q` acts instead. ⭐ **`q` buys 2 arms at `k=10` and 2 at `k=15`, and the decision is KEEP with the precondition stated.**

**The decision this round makes safe:** whether to drop `q` from the clause. **Keep it** — it is a
real parameter awaiting a real family, not a dead one.

## ⛔ First, the round I did not run, and why

R1056 closed by proposing to restate the clause with and without `q` and re-run R1055's ablation.
**That cannot produce evidence.** At |family| = 2, `need(q=90) = ceil(0.9·2) = 2 = need(q=100)` — the
two are **the same operator**, so the ablation returns Δ=0 by algebra. **My own NEXT even said they
are "indistinguishable at this family size" and then proposed running them anyway.** §4's closing-
sentence failure: written last, acted on later, no control attached.

## The world where `q` can act — §3's ladder step 4

A prompt-blind comparator is a **fixed criterion selection used on every prompt** — R918's own
`fixed` predicate. A fixed subset of the rubric satisfies it **by construction**, so a legitimate
family of any size can be built.

⛔⛔ **Except it cannot: the space is bounded.** Only **4** criterion indices are present on every
prompt, so the fixed subsets well-defined everywhere number **2⁴ − 1 = 15**. My first attempt asked
for 20 and the round **correctly refused to run**. ⭐ **Even synthetically, a blind family caps at
15** — and a clause needing k > 15 would be unsatisfiable by construction, not merely unsupported.

## Result

| k | need @ q=90 / q=100 | admitted | **Δ** |
|---:|---|---:|---:|
| 2 | 2 / 2 | 46 / 46 | **0** |
| 4 | 4 / 4 | 46 / 46 | **0** |
| 8 | 8 / 8 | 37 / 37 | **0** |
| **10** | **9 / 10** | 39 / 37 | **2** |
| 12 | 11 / 12 | 37 / 37 | **0** |
| **15** | **14 / 15** | 37 / 35 | **2** |

⭐ **`q` buys 2 arms at the two cells where it bites, and nothing at `k=12`.** The effect is **not
monotone in k** — it depends on whether any arm beats *exactly* `k−1` comparators, which is a
property of the population, not of `q`. Reporting the zero cell is the point.

## Controls

- **POSITIVE** — every synthetic comparator uses **one** selection on every prompt (R918's `fixed`),
  asserted in code: **True**, 15 built.
- **NEGATIVE** — at `k < 10` the two settings must agree **exactly**, which is R1055's arithmetic:
  **True** (Δ=0 at k=2,4,8). If the harness had shown a difference there it would not be implementing
  `q` at all.
- **SHAM** — 12 **identical** comparators must leave `q` inert, since beating one is beating all:
  **True**. A family whose size is nominal rather than real buys nothing.
- **PLACEBO** — `k = 0` admits nothing: **True**.
- **NOISE FLOOR** — 3 seeds per cell; arms unstable across them (0–2 per cell) are **excluded from
  every difference** and counted.
- **MULTIPLICITY** — the whole k curve is reported, including the cell where Δ = 0.

## The decision

⭐ **KEEP `q`, with its precondition written into the clause**: *`q` is inert below |family| = 10;
this release supplies 2; the blind-comparator space caps at 15.* Dropping it would discard a
parameter that demonstrably changes the admitted set the moment the family exists.

## IMPOSSIBLE here

- **whether a real second release yields ≥ 10 genuinely blind comparators** — the family here is
  **synthetic**: constructed, blind by construction, legitimate under R918's rule, and **not a
  release**. **SETTLES: OUT-OF-RELEASE**, the register's standing entry.

`run.py` · `results/q_in_its_own_world.json`
