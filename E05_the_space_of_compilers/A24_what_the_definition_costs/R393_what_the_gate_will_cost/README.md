# R393 — ≥39 minutes at full table, and 80% of it is two rounds

**The decision this makes safe:** *is a per-row cache justified yet?* **Yes — but it buys the tail
and almost nothing else.**

## Result — `W_CACHE_JUSTIFIED`. Two controls PASS. **No GPU spent.**

| | |
|---|---:|
| owing population | **154** |
| sample (seed 1) | 15 |
| complete / **censored** | 13 / **2 (13%)** |
| sample total | **≥ 226 s** |
| **mean** per round | ≥ 15.1 s |
| **median** per round | **3.4 s** *(p10 0.4, p90 90.0)* |
| **the 2 censored rounds' share of the total** | **180 s of 226 s — 80%** |
| **projected first-run cost at 154 rows** | **≥ 39 min** |

## ⛔ My own question was partly a derivation

R392's NEXT asked whether the gate's cost grows *"linear in rounds rather than in numbers."* **It
grows in rounds by construction** — the gate re-runs every cited round, so its cost **is** the sum of
those runtimes; the string work is microseconds. **Measuring that would have been 1+1=2 reported as a
finding.**

What is *not* forced is the **sum**, because runtimes here span **0.4 s to over 90 s** — a
distribution nobody had sampled, not a count anybody can multiply.

## ⛔ A mean over a heavy tail misdescribes where the cost lives

`≥ 15.1 s per round` is true and misleading: the **median round finishes in 3.4 s**, and **two
censored rounds contribute 80% of the sample total.**

> **A cache buys the tail and almost nothing else** — which is a sharper design brief than *"the gate
> is slow"*, and it means the cache's value is concentrated in a handful of rounds that could equally
> be identified and handled by name.

Quoting the mean alone would be the same error as the ledger's *min/max quoted as an interval*: a
summary that hides where the quantity actually comes from.

## ⚠ The projection is a lower bound and only a lower bound

**2 of 15 draws are right-censored** at the 90 s cap and contribute **the cap, not their value**. An
**upper bound is unavailable at any budget spendable here**, because the censored tail has no
measured length. So the answer is an **inequality**, and averaging a censored draw as though it were
complete is the arithmetic trap this round was designed around — the same one R388 refused when it
declined to multiply 21.3 s by 237.

## Controls

| | returned |
|---|---|
| **TIMER (+)** | a 3 s sleep times at **3.02 s** — tolerance [2.5, 6.0] allows interpreter startup |
| **TIMER (−)** | a script that does nothing times at **0.01 s**. Both directions, because a timer reporting a constant would pass the positive control |
| **CENSORING** | every capped run counted separately; the projection stated as an inequality |
| **SAMPLE** ⭐ | drawn with a fixed seed from the **owing** population — *not* the rounds that happened to be convenient. R392's NEXT made exactly that correction about which rounds get **paid**; it applies equally to which get **timed** |
| **ISOLATION** | subjects run in this round's worktree, never the live tree |

## And the cache's required shape, stated before it is built

**Keyed on the round's source hash**, so a changed round invalidates its own row. **A cache that
serves a stale verification is worse than a slow gate, because it certifies without checking** — and
that is the failure mode the whole R380–R392 line has been about.

## Register

| criterion | status |
|---|---|
| **an UPPER bound** | **N/A** — the censored tail has no measured length at any budget spendable here |
| **the cost WITH a cache** | **N/A** — that is the next decision's subject. This measures **what a cache must beat** |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"measure how long the full gate takes at 5 rows and at 10, and confirm the growth is linear in
> rounds rather than in numbers."*

**The growth in rounds is algebra. The measurement that mattered is the distribution — and it says
80% of the cost is two rounds, so the cache is justified and also far narrower than "cache
everything".**

Artifact: `results/r393_gate_cost.json`, source-stamped.
