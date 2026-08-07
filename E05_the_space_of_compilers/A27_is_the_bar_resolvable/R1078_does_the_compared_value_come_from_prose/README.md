# R1078 — ⛔⛔⛔ **R1076's census provably excludes the one confirmed defect. And my attempt to size the gap reproduced the same contamination.**

**The decision this round makes safe:** whether R1076's `38` and R1077's `34 → 12` characterise the
problem. **They do not** — the population was wrong, and the trace question is deliberately not
answered on a population known to be incomplete.

## The finding — n = 1, verified

R1070's membership test is **`cands(t)`: one argument, closing over its container.** R1076's
classifier required `len(args) >= 2`.

⭐ **So R1070 has NO rows in that census at all** — **the single confirmed exposure in this
repository, the cause of R1075's retraction, was never among the 38.**

⛔ **And R1076's positive control passed throughout**, because it checked `has`/`has_rounded`, which
happen to take two arguments. **§4's row at a new level: it confirmed the instrument could see *a*
membership test, never *the* one the claim was about.** R1077's 34 → 12 narrowing inherits the hole.

## ⛔ How big the missing population is: **UNVERIFIED**

My one-argument scan returned **249**. **Its own sizing control fails.** It readmitted
`cls`, `pair_sign`, `rank_obs`, `toks`, `canon`, `content_toks`, `kendall_pairs` — **the very scoring
helpers R1076 removed in three successive repairs.**

⭐ **I reproduced the contamination in the round whose entire subject was that instrument's blind
spot.** So `249` is not a count, is not reported as one, and no corrected total is claimed.

**What stands is n = 1, verified, and it is enough to void the census as a characterisation.**

## ⛔ The trace question is not answered here, deliberately

Tracing arguments through a population known to be incomplete would produce a tidy number over the
wrong set — **precisely the error R1075 cost five rounds to find.** The population is fixed first; the
traces are the next round's work, on a corrected list.

## Controls

- **POSITIVE** — R1070's own membership test must appear in the *missed* population: **True**
  (`cands`). This is the control that turned the round: it was written to prove the tracer worked and
  instead proved the census did not.
- **NEGATIVE** — `main` must not appear among them: **True**.
- ⛔ **SIZING** — known scoring helpers must not appear: **FALSE**, and it names all seven. **This is
  why no number is reported.**

## IMPOSSIBLE here

- **the true size of the missing population** — needs a classifier that separates membership from
  scoring for one-argument closures, which is the same problem R1076 solved for two-argument
  functions in three repairs. **SETTLES: IN-RELEASE**, at that cost.

`run.py` · `results/argument_traces.json`
