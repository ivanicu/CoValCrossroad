# R435 · a sufficiency clause needs a bar. **The bar is well-defined** — it saturates after 6 rules

**The decision this round makes safe:** whether *"better than every rule that reads no criteria"* has
a stable referent, or is a bar that climbs with however hard you look. **Stable.** `W-STATABLE`.

## ⛔ First: my own closing sentence was false, and the count took one command

R434 closed with *"the length rule is **the only** non-criterion reference on hand."* R427's
pre-registered artifact (`computed_before_arms: true`) holds **four**:

| rule | acc | vs chance |
|---|---|---|
| `longest` | 0.5096 | +0.0901 |
| `first` | 0.4375 | +0.0181 |
| chance | 0.4194 | — |
| `shortest` | 0.3362 | **−0.0832** |

**The ledger's tell fired exactly as written:** a closing sentence containing *"only"* is a
quantifier over my own work — the population I am worst at enumerating.

**And being wrong changed the clause's shape.** With one reference the clause reads *"better than the
longest-reply rule"* — which **names the instance**, and its own remedy would reject it. With a
family it must quantify over a **class** — and a maximum over a growing class **climbs by
construction**, which is exactly the defect clause ② already carries (`POOL[0:k]`, chosen by *file
order*, at the 93.7th percentile of 1,820 subsets).

## Result

| | |
|---|---|
| family | **30 rules**: 14 response-set features × {max, min}, plus `first`/`last` — published verbatim in the artifact so it can be **extended** |
| best rule | **`max_len_chars` 0.5135** · chance **0.4324** · worst `min_len_chars` 0.3563 |
| what the data can resolve | **0.0234** — the conversation-bootstrap 95% width on *one* rule's accuracy |
| **saturation** | **`m* = 6` of 30.** `BAR(|F|) − BAR(6) = +0.0232`, inside 0.0234 |
| lift over signal-free rules | **+0.0715** at the full family, ~3× the data floor |

**Six randomly drawn rules already reach the bar.** The remaining twenty-four move it by less than
the data can resolve — so the bar is *not* an artifact of how hard I looked.

**Population** 7,342 interactions / 2,200 conversations, 0 dropped for missing text · **instrument
NONE** — every rule is judge-free, which is the point · **baseline** chance and a signal-free family
· **regime** n ∈ {2,3,4}.

## Controls

| control | returned |
|---|---|
| POSITIVE — plant an oracle rule | max **0.5135 → 1.0000** ✅ |
| g=0 — plant nothing | unchanged ✅ |
| PLACEBO — duplicate the best rule | max unmoved ✅ *(a max is over values, not members)* |
| NEGATIVE — 30 signal-free rules | mean **0.4314** sd 0.0053, sits at chance **0.4324** ✅ |

## ⛔ Two degenerate kills in one round, in opposite directions, from one root

1. **First version:** floor from resampling *rules*. At `m = |F|` there is exactly one subset, so the
   floor is **0.0000** and `climb > 0` is **forced** — `W-CLIMBING` always. A check that cannot fail.
2. **First repair:** compare `max(full family)` to `max(first half)`. But the best rule is
   `names[0]`, so it is **always** in the first half: the difference is identically **0.0000** with a
   floor of **0.0000**, and `0 ≤ 0` **forced `W-STATABLE`**. A check that cannot fail, inverted.

**Both had the same root: a floor that was a property of *my partition* rather than of the data.**
The kill now rests on `m*` — the smallest family size reaching within the data's own resolution of
the full-family bar — which could have landed anywhere in 1…30.

## The clause this licenses, stated as a predicate

> **④** …and scores better, under that same judge J, than **every rule computable from the response
> set alone**.

| the remedy's two questions | answer |
|---|---|
| an admissible object it **EXCLUDES** | **all 7 arms on the second release** (R434) — including the published prompt-blind `generic` and the prompt-specific `gen`. **Not vacuous.** |
| a useful object it **ADMITS** | an oracle arm — R434 measured **+0.4865** over the length rule. **Not impossible.** |

⚠ **What is NOT yet known, and it is the discriminating question:** whether ④ excludes anything on
the **home** release, where clause ② admits 33 of 42. The home arms have **never** been scored
against the criterion-free family. **Until that runs, ④ is a candidate, not a clause** — and adding
it now would be fitting it to the one release where everything already fails.

## Impossible here, named

- **the supremum over all criterion-free rules** — the class is infinite; this is a hand-built family
  of 30 and the round says so rather than implying its family *is* the class. Requires a search.
- **that the plateau holds on another release** — one corpus.
- **construct validity of `chosen`** — the release's own human choice.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
