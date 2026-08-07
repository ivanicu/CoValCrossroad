# R369 — R368's contrast agrees in sign across metrics and decomposes the opposite way in each

**The decision this makes safe:** *may R368's transport result be read as "the core transports"?*
**Only with the baseline's movement stated** — because under one defensible metric the baseline moves
the other way.

## Result — `W_UNSTABLE`. Reproduction control PASSES. Two runs byte-identical.

R368 computed the floors per stratum per arm **and never printed them.**

| metric | Δcore | Δfloor | contrast | R368 published | reproduces? |
|---|---:|---:|---:|---:|---|
| **exact** | **+0.1300** | **+0.0308** | +0.0992 | +0.0992 | **yes** |
| **pair** | **+0.0425** | **−0.0187** | +0.0612 | +0.0612 | **yes** |

Per-stratum `Δfloor` — the table R368 had and did not print:

| metric | s0 | s1 | s2 | s3 |
|---|---:|---:|---:|---:|
| exact | −0.0131 | **+0.0552** | **+0.0453** | **+0.0364** |
| pair | −0.0606 | −0.0068 | −0.0041 | −0.0027 |

**Under `exact` the random baseline RISES on the fresh arm; under `pair` it FALLS.**

## ⚠ And the instability is BOUNDED — saying otherwise would overstate it

My first verdict string said *"this design cannot separate them."* Reading the same table it prints:

- **Δcore is positive in BOTH metrics** (+0.1300, +0.0425)
- **and larger in magnitude than Δfloor in both**

So **the core term dominates the contrast under either metric.** What is metric-dependent is the
**attribution of magnitude** between core and floor, **not the direction of the finding.**

⛔ **R368 still needs narrowing**: it reported the contrast and not the decomposition, so *"the core
transports"* was stated as though the baseline held still. It does not, and under one metric it moves
the other way.

## ⛔ The check that looked like it settled the subset question was wrong

The floor is a random draw from **`full`'s own criteria** — among the items being summed to make the
target — while the core is a **rewrite** (the campaign's own finding: only 8% of its items appear in
full). A subset of an aggregation has a structural advantage at reproducing it.

I checked, and it looked settled: **core indices are a subset of full's in 250 of 250 prompts.** Then
I looked at the values:

> **241 prompts: `(0,1,2,3)`. 9 prompts: `(0,1,2)`. Purely positional.**

`core ⊆ full` is an **indexing artifact** and carries **no information about criterion identity.** The
loose check said "settled"; the tight one said "you learned nothing."

## Controls

| | returned |
|---|---|
| **REPRODUCTION** ⭐ | recovers R368's published contrasts to 4 dp — so this decomposes **its** quantity, not a new one |
| **DISTINCTNESS** | the two metrics give different Δcore (+0.1300 vs +0.0425) — a sign flip between identical metrics would be vacuous |
| **PLACEBO** | inherited from R368: `full` against itself = 1.0 on both metrics |
| reproducibility | two runs **byte-identical** (`fe098d3c40a6`) |

## What remains unseparated, named rather than waved at

A difference-in-differences cancels the subset advantage **only if it is additive across arms** —
which is exactly what the flipping Δfloor puts in doubt. Separating it needs a floor drawn from
criteria **outside `full`**, and this cache contains only `core` and `full`.

**That is the next instrument, not a caveat.**

## Register

| criterion | status |
|---|---|
| **separating subset-advantage from transport** | **N/A here** — needs a non-subset floor; not in this cache |
| **agreement with people on fresh responses** | **N/A**, unchanged from R233/R368 — no human rankings there |
| **a second judge** | **N/A** — the cache was judged by 2B only |

## The sentence I can no longer write

> *"matched on difficulty, the core transports"* — with the baseline unstated.

**The core term is positive and dominant under both metrics; the floor moves in opposite directions
between them, and R368 reported neither.**

Artifact: `results/r369_decomposition.json`, source-stamped.
