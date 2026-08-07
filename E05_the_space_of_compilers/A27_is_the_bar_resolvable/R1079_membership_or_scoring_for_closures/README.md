# R1079 — ⛔ **The pre-registered kill fired: count withheld. And three rounds, three classifiers, each failing its own control, is the finding.**

**The decision this round makes safe:** whether to build a fourth classifier. **No** — the population
cannot be enumerated mechanically at acceptable cost, and the remedy never needed a census.

## The kill fired as written

| control | required | result |
|---|---|---|
| **POSITIVE** | R1070's `cands` — the one confirmed defect — must classify MEMBERSHIP | **False** |
| **NEGATIVE** | all seven scoring helpers R1078 named must be excluded | **False** — `toks` survives |

**Pre-registered:** *zero stowaways AND `cands` present → report the count; otherwise withhold.*
**8 candidates were found. The number is not reported.**

⭐ **The rule sounded right and lost the case it was built for.** Requiring the closure's free
variable to be a container built from artifact values excludes 6 of 7 stowaways — and drops `cands`,
which is the only function in this repository *known* to have caused a retraction.

## ⭐⭐ Three attempts, three failures, each better argued than the last

| round | rule | outcome |
|---|---|---|
| **R1076** | two-argument shape | 3 repairs, count fell **132 → 38** — and it still **excluded the one confirmed defect** |
| **R1078** | one-argument shape | readmitted **7** scoring helpers; count **withheld** |
| **R1079** | closure over an artifact-built container | excludes 6 of 7, **still admits `toks`**, and **loses `cands`** |

⛔ **"Membership test" versus "scoring helper" is a SEMANTIC distinction, and I have now tried three
times to recover it from SYNTAX.** Every attempt had a better rationale than the one before, and every
one failed a control it could not have passed.

**The honest reading is not "try a fourth rule."** It is that **this population cannot be enumerated
mechanically at acceptable cost** — and every count built on it inherits that, including R1076's `38`
and R1077's `34 → 12`.

## ⭐ Which redirects the remedy

`assurance/valuematch.py` **does not need a census to be useful.** It needs to be **the thing reached
for at the point of use.**

**Enumerating past sites was the expensive path. Making the next comparison correct is the cheap
one — and it was available from R1076 onward without any of this.** Three rounds bought the knowledge
that the cheap path was always the right one.

## Controls

- **POSITIVE** — `cands` must be found: **False**, and that failure is the round's verdict rather
  than a bug to route around.
- **NEGATIVE** — the seven named stowaways must be excluded: **False** (`toks`). ⭐ **This control had
  already failed once, on a different design** — which is exactly why it was worth keeping.
- **PLACEBO** — a file parsing to nothing contributes nothing and is not counted as clean.
- **KILL** — pre-registered before the run, and **fired**. The 8 candidates are in the artifact,
  unreported as a count.

## IMPOSSIBLE here

- **a syntactic separator for a semantic distinction** — three designs, three failures.
  **SETTLES: OUT-OF-RELEASE** for a mechanical rule; **IN-RELEASE** only by reading each function,
  which is the cost this line was trying to avoid and never undercut.

`run.py` · `results/closure_membership.json`
