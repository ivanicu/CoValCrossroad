# R1087 — one of the two rows is a draw and the other is a **value**. Coverage is invariant across all 32,767 families.

**The decision this round makes safe:** whether R1086's finding generalises — whether *every* number
in R1055's ablation table is a family draw. **It does not.** Resolvability's exclusion count spans
**2–14** over the whole family space; coverage's is **−2 in every single family**.

## The result

**Population** every non-empty family of the 15 universally-available blind subsets — **2¹⁵ − 1 =
32,767**, enumerated whole, per ablation. **Instrument** R1055's own operator (cluster bootstrap,
2.5th percentile), 3 seeds, a decision counts only if all three agree. **Baseline** the unablated
`(resolvable, own-prompts)` variant. **Regime** 968 prompts, target A2, the every-comparator rule.

| ablation | span over 32,767 families | distinct values | mode | full distribution |
|---|---|---:|---:|---|
| **resolvability** | **[2, 14]** | **9** | 7 | `{2:1, 3:2, 4:4, 5:12288, 7:17408, 8:2056, 10:512, 11:384, 14:112}` |
| **coverage** | **[−2, −2]** | **1** | −2 | `{-2: 32767}` |

⭐ **World A is KILLED for resolvability only.** Its count takes 9 distinct values, and the value
**2** occurs in **exactly 1 of 32,767 families** — the single lowest cell in the space, and it does
not occur at all at family size 2.

⭐⭐ **And coverage is a genuine invariant.** `−2` in every family at every size, 100% mode share
throughout. **The arc's emerging story — "these numbers are all draws" — is refuted by its own
instrument**, which is the check a narrative needs and rarely gets.

| k | families | resolvability min / mode / max | coverage |
|---:|---:|---|---|
| 1 | 15 | 2 / 14 / 14 | −2 (100%) |
| **2** | 105 | **3 / 5 / 14** — `2` never appears | −2 (100%) |
| 5 | 3003 | 5 / 7 / 14 | −2 (100%) |
| 10 | 3003 | 5 / 7 / 10 | −2 (100%) |
| 15 | 1 | 7 / 7 / 7 | −2 (100%) |

## ⚠ What this does NOT say, and the limit is structural

**R1055's own comparators — `generic`, `genericpool16` — are released arms, not blind subsets, so
they are not in this space.** This round measures the **shape** of the two numbers over a comparable
family space; it cannot restate R1055's cell and **does not claim R1055 undercounted.**

The direction is in fact explicable: a blind subset built from 4 universally-available criteria is a
**weak** comparator, so more arms beat it, so relaxing resolvability admits more. That the span sits
above R1055's 2 is consistent with its comparators being **stronger objects**, not with its number
being wrong. **The finding is the variability, not the level.**

## Controls — 8, all green

| control | result |
|---|---|
| the blind subsets cover every prompt, so the mask collapses to the arm's — **verified, not assumed** | PASS |
| g=0 ablating nothing gives 0 on every sampled family | PASS |
| PLACEBO each variant against itself is 0 everywhere | PASS |
| POSITIVE a planted arm only the relaxed variant admits is recovered (and the strict one does not) | PASS |
| NEGATIVE relabelling comparators leaves **both** distributions identical | PASS |
| NEGATIVE breaking the arm-comparator pairing **moves** the distribution | PASS |
| SHAM `k` copies of one comparator equals its `k=1` value | PASS |
| POSITIVE resolvability **binds** somewhere in the family space | PASS |

⭐ **The mask collapse is what made the enumeration exact.** R1055's coverage mask is
`COV[i] & COV[j]`; the blind subsets are built from criteria present on *every* prompt, so `COV[j]`
is all-true and the mask depends on the **arm alone**. That factorises the bootstrap per arm and
turns 32,767 families into lookups. It is checked rather than assumed — the first control.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| restating R1055's own cell | **N/A** | its comparators are released arms, outside the blind space |
| `k > 15` | **N/A** | more than 4 universally-available criteria; `2⁴−1` is a hard cap |
| whether any of these families could be **certified** | **N/A** | R1056 measured the certified family is 2 at every defensible threshold |
| cross-release | **N/A** | a second release with its own blind space |

`run.py` · `results/other_two_clauses.json`
