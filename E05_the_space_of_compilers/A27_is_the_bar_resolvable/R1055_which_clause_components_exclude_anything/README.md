# R1055 — which clause components EXCLUDE anything? ⛔ **Two bind with named excluded arms; `q` is inert until the comparator family reaches 10, and this one has 2.**

**The decision this round makes safe:** which parts of the definition are load-bearing. **Two are, one
is untested in this population, and one cannot be exercised at all as the clause currently runs.**

⭐ This is §4's remedy run against the real operator: *name an admissible object this clause
EXCLUDES.* 99 arms, 968 prompts, target A2, comparators `generic` + `genericpool16`.

## Result — the ablation table

| component | Δ admitted | what it excludes |
|---|---:|---|
| **resolvability** (2.5th pct → point estimate) | **2** | removing it **admits** `greedy_k12_fit1`, `topw_k2` |
| **coverage, not imputed** (own prompts → imputed) | **2** | imputing **loses** `coval_core_2bA`, `coval_core_2bB` |
| comparator **family** (two → one) | **0** | nothing on disk |
| `q = 90` → `q = 100` (the pre-R1032 form) | **0** | ⛔ **forced by algebra — see below** |

⭐⭐ **Two named excluded objects each**, which is exactly what §4 asks for and what no previous round
in this arc supplied. ⭐ And the coverage row **independently reproduces R1032**: the twins
`coval_core_2bA/2bB` are precisely the arms the as-written imputing operator wrongly admitted.

## ⛔⛔ The `q` row is a DERIVATION, not a measurement — and that is the finding

At family size *k*, `need(q=90) = ceil(0.9k)` and `need(q=100) = k`. These are **equal for every
k < 10**:

| \|family\| | 2 | 3 | 4 | 5 | 8 | **10** |
|---|---|---|---|---|---|---|
| need @ q=90 | 2 | 3 | 4 | 5 | 8 | **9** |
| need @ q=100 | 2 | 3 | 4 | 5 | 8 | **10** |

**The certified family has 2 members.** So `q=90` and `q=100` are the *same operator*, and the Δ=0
**could not have come out otherwise**. Per the arithmetic trap: label it, state its assumption
(family size), and stop calling it evidence.

⭐ **The clause declares a parameter its own certified family is too small to exercise.** R1036–R1038
measured `q`'s onset curve and set its default at 90; none of that is wrong, and **none of it is
exercised by the operator as the clause currently runs.** `q` first becomes testable at **|family| =
10** — five times the current family.

## Controls

- **POSITIVE** — resolvability must bind, since R1032 measured that it does: **True** (Δ=2).
- **NEGATIVE** — ablating nothing reproduces the baseline exactly: **True**.
- **SHAM** — changing only the bootstrap seed leaves the set unchanged: **True**.
- **NOISE FLOOR** — the admitted set at 3 seeds: **24 always in, 75 always out, 0 unstable**. Unstable
  arms would have been excluded from every symmetric difference; none were needed.
- ⚠ **The scoring is copied from R923's own `vec()`, not invented.** My first version indexed
  `S[p]` as an array; `load_sat` returns `{pid: {(criterion, letter): value}}`. The traceback was the
  object saying so — the seventh unit error this window, caught early only because Python refuses to
  divide a dict.

## What this round cannot say

**Binding is necessity, never correctness.** A component that changes the admitted set is doing work,
not thereby the *right* work — R1032 showed the pre-repair form also bound, and it bound *wrongly*.

## IMPOSSIBLE here

- **whether a component excluding nothing HERE would exclude something elsewhere** — needs a second
  release. **SETTLES: OUT-OF-RELEASE**, the register's standing entry.
- **exercising `q`** — needs a certified family of **≥ 10**. **SETTLES: IN-RELEASE** in principle: the
  family is built by a certification procedure that could admit more comparators; unattempted.

`run.py` · `results/component_ablation.json`
