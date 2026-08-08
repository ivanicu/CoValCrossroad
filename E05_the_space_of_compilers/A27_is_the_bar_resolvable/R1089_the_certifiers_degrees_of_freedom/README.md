# R1089 — **28 of 99 arms** are decided by who picks the comparators. **71.7% is the arms.**

**The decision this round makes safe:** whether clause ②′ names a property of the arms or a property
of the certifier's choice. **It names both, and the split is computable exactly.**

## The partition, and monotonicity is what makes it exact

⭐ **A derivation, labelled and then verified.** Admission under the every-comparator rule is an
**intersection** over members, so `|admitted(F)|` is **monotone non-increasing** in `F` — adding a
comparator can only remove arms. Therefore the maximum is attained at some **singleton** and the
minimum at the **full family**, and **nothing between needs searching.** Checked on 200 random nested
pairs, no violation.

| block | arms | meaning |
|---|---:|---|
| admitted under **every** admissible family | **35** | a fact about the arm |
| admitted under **no** family | **36** | a fact about the arm |
| **decided by the certifier's choice** | **28 (28.3%)** | a fact about the choice |

**Permissive end 63 · strict end 35 · gap 28 of 99.** So **71.7% of the extension is fixed by the
arms** and **28.3% is a knob** — a large minority, not a majority.

| family | admitted |
|---|---:|
| `(3,)` — the weakest single subset | **63** |
| `(2,)` | 61 |
| `(1,)` | 59 |
| `(2,3)` | 53 |
| … the full 15 | **35** |

**SHAM — the same range with resolvability removed:** gap **23**. So resolvability *widens* the
certifier's freedom by 5 arms rather than narrowing it, which is the opposite of what a
"strictness" reading would predict.

## ⛔ What this does not say, and my first verdict said it

The first verdict string read *"the extension is **mostly** a fact about who picks the comparators."*
**Nobody computed "mostly", and it is false** — 28.3% is a minority. §4's *the verdict string is not a
computation*, caught by computing the partition the monotonicity argument already implied.

⚠ **And this is not R1034's endpoint.** R1034 measured the extension **empty** under closure over
pool16's 65,535 subsets. This is a different, smaller space — the 15 universally-available blind
subsets — whose full family admits **35**, not 0. **The two closures are different objects and their
numbers must not be pooled.**

## Controls — 4, all green

| control | result |
|---|---|
| POSITIVE monotonicity on 200 nested pairs — the derivation, verified not assumed | PASS |
| g=0 identical comparators give a gap of exactly 0 | PASS |
| NEGATIVE breaking the arm-comparator pairing **moves** the gap | PASS |
| PLACEBO a family against itself differs by 0 | PASS |

**Noise floor:** 3 bootstrap seeds, unanimity required; 7 of 1485 strict decisions and 0 point
decisions were not unanimous.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| what the release's certification rule would **allow** | **N/A** | R1056 measured it yields a family of 2, and which 2 is not a free choice |
| pooling with R1034's closure | **N/A** | a different comparator space (pool16's 65,535 subsets) |
| cross-release | **N/A** | a second release with its own blind space |

`run.py` · `results/certifier_freedom.json`
