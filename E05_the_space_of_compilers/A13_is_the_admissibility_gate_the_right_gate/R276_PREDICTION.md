# What I expect the retraction classifier to return — written before it does

**Dispatched 2026-08-03**, clean context, one mechanical rule, no opinions about the research.

## The claim under test, and it is mine from one commit ago

> *"Three of this arc's rounds now have a real effect with a wrong mechanism attached — R249's
> redundancy, R272's grid claim, and this calibration term. **The mechanism is the part that
> transfers to another release, and it is the part that keeps failing.**"*

That is a mechanism claim about my own work, asserted from three instances and never tested.
**Fourth instance of the thing it names, and I wrote it one minute after naming the pattern.**

## The prediction, fixed now

| | |
|---|---|
| **MECHANISM > EFFECT** | what my claim requires |
| **my point estimate** | roughly **2:1** — I expect mechanisms to dominate but not overwhelmingly |
| **PROCESS is the wildcard** | I expect it to be **large, possibly the plurality**. Most of today's retractions were controls that could not fail, walls never checked, and thresholds that were impossible — none of which is an effect *or* a mechanism. If PROCESS dominates, **my claim is not so much wrong as mis-framed**: the thing that keeps failing is neither the number nor its story but the apparatus that was supposed to test both. |

## What each outcome does to the claim

- **MECHANISM ≫ EFFECT** → the claim stands and gets a ratio instead of an anecdote
- **EFFECT ≥ MECHANISM** → **retracted.** I generalised from three cases I had just been looking at,
  which is the availability heuristic wearing a pattern's clothes
- **PROCESS is the plurality** → the claim is **re-scoped, not confirmed**: what fails most is the
  apparatus, and "mechanisms fail more than effects" would be true of a minority of the file

## The thing I cannot do, and why the classifier is a clean context

I am classifying my own errors. Every entry in that file was written by me, in my own vocabulary,
with my own emphasis — so a self-classification would inherit exactly the framing that produced the
claim. **Ivan's standing rule applies: self-review is void, not weak.** The rule handed over is
mechanical and the classifier was told not to form opinions about the research, only to apply it.

## Scoring, fixed before the return

If the ratio lands within ±0.5 of 2:1 I will call the prediction good. If PROCESS is the plurality
and I did predict that here, that is a **half-credit**: I named the possibility but still led with
the mechanism claim in the commit body, which is where it will be read.

---

# SCORED, 2026-08-03 — the classifier returned

| category | n | share |
|---|---:|---:|
| **PROCESS** | **135** | **56%** |
| MECHANISM | 58 | 24% |
| EFFECT | 46 | 19% |
| *(flagged ambiguous)* | *27* | *11%* |
| **total** | **239** | |

## Against the prediction

| I predicted | actual | scored |
|---|---|---|
| MECHANISM > EFFECT **at ~2:1**, band ±0.5 → [1.5, 2.5] | **1.26 : 1** | ❌ **outside my own band. FAILS.** Direction right, magnitude wrong by enough to matter |
| PROCESS **large, possibly the plurality** | **56% — an outright majority** | ✅ right, and *stronger* than I said |
| the file holds **~100 entries** | **239** | ❌ **wrong by 2.4×**, and it caused a numbering collision (fixed, entries 236–239) |

**By my own scoring rule, written before the run: PROCESS is the plurality → the claim is
`RE-SCOPED, NOT CONFIRMED`, and I take HALF CREDIT** — I named the possibility here but still led
with the mechanism claim in the commit body, which is where it gets read.

## What the claim actually amounts to

> *"The mechanism is the part that transfers to another release, and it is the part that keeps
> failing."*

**True of 24% of the file. False of 56%.** Mechanisms do die more often than effects — `1.26:1`,
which is a real but weak margin — and **both are minorities.** What fails most is neither the number
nor its story: it is **the apparatus.** Unfit controls, blind instruments, unchecked walls,
corrections that were never carried into the document that states them.

## And that reframes today rather than excusing it

Nearly every retraction this session was PROCESS: a control that could not fail, a threshold that
was impossible, a kill that did not check its own controls, an interval invented rather than
computed. **I had read that as an unusually bad day. The file says it is the ordinary case** — 56%
of everything this programme has ever withdrawn.

## The bound on all of it

**27 of 239 entries (11.3%) were flagged ambiguous by the classifier**, several because a single
entry carries both a dead number and a dead explanation. So these shares carry roughly ±5 points of
classification slack, and the `1.26:1` ratio is well inside that. **The one conclusion the slack
cannot touch is the ordering: PROCESS is more than twice either of the other two.**
