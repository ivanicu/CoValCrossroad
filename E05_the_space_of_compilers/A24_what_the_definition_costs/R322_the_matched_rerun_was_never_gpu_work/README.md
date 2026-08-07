# R322 — the wall was fake, and behind it the hypothesis died

**Decision this makes safe:** whether the four-bracket spread is a replicate-count artifact.
**It is not, and the `tau` explanation I proposed for the residual is dead.**

## The wall first

R321 closed with *"matched re-runs at equal replicate counts are GPU work through pueue."*
**R274 contains zero references to torch, cuda, or any model loader.** It reads a committed `.npz`
and does binomial simulation. The whole sweep below is a CPU job that took minutes.

`realstat §4 · a fabricated impossibility`: a wall makes stopping feel earned, so it is the one
claim nobody audits — and I wrote it into a scope block one round ago.

## The sweep — R274's own pipeline, REPS swept, everything else identical

| reps | tau | bracket |
|---:|---:|---|
| 40 | **0.4240** | [0.085, 0.125] |
| 100 | **0.4240** | [0.090, 0.125] |
| 400 | **0.4240** | [0.105, 0.125] |

**W-TAU-INVARIANT.** `tau` is identical at every replicate count, because it is calibrated from
`NCAL = 3000` draws that `REPS` does not touch. **The "two channels" story is wrong** — REPS reaches
the MDE through the dose-response curve only, exactly as R321 already modelled it.

**So R268's `tau = 0.416` against R274's `0.424` is not a replicate effect and remains
unexplained.** A smaller residual than before, and a different one.

**What the sweep does show, within one rule:** the bracket's lower end falls with fewer replicates
(0.105 → 0.090 → 0.085) while the upper end stays 0.125. That is a CI narrowing from one side —
what a CI-containment interval does — **not a bias in the estimate.**

## Controls

| control | result |
|---|---|
| **placebo / positive** — REPS=400 reproduces the committed bracket and tau | `[0.105, 0.125]`, `0.4240` |
| **knob alive** — 40 and 400 must differ | they do |
| all cells executed | 3/3 |
| negative | none available, and named: destroying the structure means a different tensor, which R319 showed moves the answer for other reasons |

## ⚠ Three defects in this round's harness, two of them inherited from my own earlier work

1. **The `covalx` bootstrap R320 inserted into every repointed round** does
   `next(p for p in parents if (p/'covalx').is_dir())`. Under `/tmp` no parent holds `covalx`, so
   the copy died with `StopIteration` — a harness broken by a line a previous round of mine added.
2. **The "refusing to run an unmodified copy" guard fired on the positive control.** At REPS=400
   the substitution is a correct no-op, and a guard keyed on *text changed* rather than *pattern
   matched* condemned the one cell that validates the harness. `a check that cannot pass`.
3. **The pre-registered kill compared incommensurable ends** — `matched(100) hi` is a CI upper
   bound; the arc's 0.100 is a point crossing. That is precisely the error R321 diagnosed, repeated
   one round later. The kill now tests the tau hypothesis, which is what the round was for.

## Scope

R257's canonical tensor, 250 prompts · R274's calibrated detector · REPS swept, NCAL/NHOLD held at
3000, dose grid held at 0.005. This bounds the replicate channel **inside one pipeline**. R267 and
R268 are separate scripts with their own grids and rules, so it does not decompose the whole gap —
and porting their rules onto one harness is real work with **no GPU**, written here as a task
rather than as a wall.
