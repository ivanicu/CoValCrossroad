# R1090 — the released core beats **15 of 15** and is in `always`. Its **sham** is `movable`.

**The decision this round makes safe:** whether the certifier's 28-arm degree of freedom (R1089)
reaches the object the definition was written from. **It does not.** All three released cores are
admitted under **every** admissible blind family; the choice cannot touch them.

## The named blocks

⭐ **A derivation makes the partition free, labelled as one.** Monotonicity (R1089) means an arm is
admitted under every family iff it beats **all 15** subsets, and under none iff it beats **0**. The
blocks are a threshold on one integer per arm. **Which arm has which count is the measurement.**

| arm | beats | block | seed-stable |
|---|---:|---|---|
| `coval_core` | **15 / 15** | **always** | ✔ |
| `coval_core_2bA` | **15 / 15** | **always** | ✔ |
| `coval_core_2bB` | **15 / 15** | **always** | ✔ |
| `coval_core_sham` | 4 / 15 | *movable* | ✔ |

**Block sizes: always 35 · movable 28 · never 36** — reproducing R1089's counts exactly from an
independent route, which is the check that the derivation is the same object.

`always` includes both released comparators (`generic`, `genericpool16`) and `greedy_k12_fit1`.
`movable` includes every `random_k*` arm and `full`. `never` includes `promptecho`, `oracle_k4_08b`
and every `*_08b` variant sampled.

⭐ **World A: the definition admits its own instance whatever the certifier picks.** That is the
strongest form available here, and it was not guaranteed — 28 arms *are* choice-dependent, and the
core could have been one of them.

⭐⭐ **And the sham is a control I got for free.** `coval_core_sham` beats **4 of 15** and is
**movable** — so the clause *can* tell the core from its sham, and the separation is 11 subsets wide.
A sham admitted under every family would have meant the clause cannot distinguish them.

## ⛔ My verdict string fired the wrong world, on a sham

The first version matched `"coval_core" in name`, swept in **`coval_core_sham`**, and printed
*"world B — the definition admits its own instance only if the certifier chooses right."* **The
three real cores are unambiguously `always`.** The instrument's population contained an object the
claim's unit excludes — §4's *name the instrument's unit and the claim's unit and require them
equal* — in the round whose whole job was naming members.

**Fixed by splitting the populations**, and the sham became a control rather than a contaminant.

## Controls — 6, all green

| control | result |
|---|---|
| g=0 the three blocks **partition** the arms (sizes sum to 99, no overlap) | PASS |
| POSITIVE planted counts 15 / 7 / 0 land in always / movable / never | PASS |
| NEGATIVE permuting a row leaves its **count** and so its block unchanged | PASS |
| PLACEBO recomputing from the same matrix gives identical blocks | PASS |
| SHAM the point estimate gives a **different** partition (9 arms move) | PASS |
| SHAM the core's own sham is **not** admitted under every family | PASS |

**Noise floor: 0 arms change block across the three bootstrap seeds.** The 7 non-unanimous
(arm, subset) decisions R1089 reported never cross a block boundary.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| what the release's certification rule would allow | **N/A** | R1056 measured it yields a family of 2 |
| generalising beyond the 15 blind subsets | **N/A** | `2⁴−1` is a hard cap on that space |
| cross-release | **N/A** | a second release |

`run.py` · `results/named_blocks.json`
