# R1045 — R1044 called it "a habit rather than an incident". ⛔ **The count says incident, and R1044's closing sentence is withdrawn.**

**The decision this round makes safe:** whether the exit-code-over-output error found in R1043 needs a
mechanical remedy across this arc. **It does not** — the population is **one**, and it is the round
already retracted.

## The claim under attack is my own, written one round ago

R1044 retracted R1043's headline and closed by generalising the cause, verbatim from its commit body:

> *"Whether other rounds in this arc do the same is checkable from their run.py sources"* — proposed
> because the error was **"a habit rather than an incident"**.

⭐ **I sharpened it before running it**, because R1043 used `capture_output=True` and touched only
`.returncode`: capturing output and never reading it is the same failure, so the test is `.stdout`
appearing anywhere in the source, not whether output was captured.

## Result — ⛔ **World B. n = 1.**

| axis | population | failing | share |
|---|---:|---:|---:|
| ① invokes `subprocess`, reads `returncode` but never `.stdout` | **3** | **1** (R1043) | 0.333 |
| ② loads an artifact, checks only that it EXISTS, never a value | **14** | **0** | 0.000 |

**R1044 asserted a pattern from a single instance while the population that could have exhibited one
was three rounds.** §4's own row predicted this exact over-correction: *"of the same 7, exactly 1
failed in the flattering direction. Asserting 'they all flattered me' was itself a narrative claim
that the count refuted."* Here the narrative ran the other way — self-critical rather than
flattering — and **the direction of a narrative claim does not change that it is one.**

## ⚠ The negative control caught my classifier, not R1044

The first implementation defined *reads values* by regex (`d[`, `.get(`) and *opens an artifact* as
`json.loads(...) OR read_text()`. It scored **R1044 as failing both axes** — the round that reads
`.stdout`, indexes `doc[a:b]`, and iterates `A.values()`.

⭐ **The control was not wrong; the demand was ill-posed.** R1044 never binds a name from
`json.loads`, so it is **not in axis ②'s population at all** — scoring it zero on an axis it does not
join is the empty-denominator failure one level down. The fix was **AST, not a wider regex**: a round
enters axis ② iff a name is bound from `json.loads`, and reads values iff that name is later
subscripted or has an attribute accessed. Rounds that never load an artifact are **excluded**.

## Controls

- **POSITIVE** — R1043, the known case, must classify as reading `rc` without `stdout`: **True**.
- **NEGATIVE** — R1044 must read `stdout` **and** be excluded from axis ②: **True**. A classifier
  that cannot separate the retracted round from the round that retracted it separates nothing.
- **PLACEBO** — a round with no artifact access is excluded, not scored 0.
- **EMPTY POPULATION** — exit **2**, never 0, on either axis.
- **NOISE FLOOR** — binomial SE printed beside the share; at 0 of 14 it is 0.000, and the honest
  reading is **`≤ 3/14 ≈ 0.21` at 95%**, not "none exist".

## ⚠ What a value-reading rate does not license

**Reading the object is necessary, not sufficient.** R1043 read artifact values throughout and still
reported an exit code as its finding. A 0-of-14 existence-only rate says the rounds open the object;
it says nothing about whether they read the right part of it.

## IMPOSSIBLE here

- **whether a round that read VALUES read the RIGHT values** — the one question that would settle the
  paragraph above. **SETTLES: IN-RELEASE** — every round's source and artifact are committed, so it is
  answerable per round at the cost of one reading each; it is unattempted, not unavailable.

`run.py` · `results/habit_or_incident.json`
