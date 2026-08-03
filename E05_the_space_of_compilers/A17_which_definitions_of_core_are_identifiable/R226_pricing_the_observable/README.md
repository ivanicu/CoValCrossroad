# R226 — pricing the observable

**Arc E05·A04.** R224's bound has two assumptions. R225 attacked the rater half and it survived.
This attacks the other: **"the observable is the ordering."** It need not be — a richer per-prompt
observable raises `H_have` **without adding a single candidate**, and the release chose which one to
ship.

Two numbers per observable, and they are not the same number: **capacity** `log₂|values|` is a
derivation and an upper bound; **achieved** is the empirical entropy in the release and can only be
lower. R224 bounded with capacity. If achieved ≪ capacity, R224 was *optimistic*.

## Controls, run before any number was read

| | | |
|---|---|---|
| **positive** | uniform over the 75 weak orderings | H = 6.2285, target 6.2288 ✔ |
| **negative** | one ordering repeated 200,000× | H = 0.0000 ✔ |

## The price list — `H_need = log₂ C(15,4) = 10.41 bits`

| observable | capacity | achieved | Miller-Madow | n | closes the gap? |
|---|---:|---:|---:|---:|---|
| `world_ordering` | 6.2288 | **5.9532** | 5.9561 | 18,384 | no |
| `personal_ordering` | 6.2288 | 5.8362 | 5.8471 | 4,901 | no |
| `veto_set` | 4.0000 | 3.2080 | 3.2102 | 4,901 | no |
| `ordering + veto` | 10.2288 | **7.8406** | 7.9168 | 4,901 | no |
| `graded 5-pt per response` | 9.2877 | *not shipped* | — | — | no |
| **`graded 10-pt per response`** | **13.2877** | *not shipped* | — | — | **YES** |
| **`pairwise confidence, 5-pt`** | **13.9316** | *not shipped* | — | — | **YES** |
| **`per-criterion satisfaction`** | **60.0000** | *not shipped* | — | — | **YES** |

Bootstrap spread over 5 resamples: 0.0145 (`world_ordering`), 0.0388 (`ordering+veto`).

## The arithmetic impossibility that exposed a bug

The first run returned **6.3868 achieved against a capacity of 6.2288 — 102.5%.** An empirical
entropy **cannot** exceed the log of its own alphabet. That impossibility is the only reason the bug
surfaced: `"A=B>D=C"` and `"A=B>C=D"` are the **same** weak ordering written two ways, and I was
counting raw strings. **I was measuring the entropy of the encoding, not of the observable.** An
assertion now guards it.

## What it says

**R224 was optimistic, but only slightly.** The release uses **95.6%** of its observable's capacity,
so the real deficit is **4.46 bits**, not the 4.19 R224 published. The bound is tight; the direction
was right and the magnitude barely moves.

**The cheapest fix is not more candidates.** R224 solved the inequality for `m` and got six. But the
gap closes at `m = 4` by changing the *response format* instead:

- a **10-point score per response** — 13.29 bits, closes a 4.46-bit gap
- **pairwise confidence** — 13.93 bits
- **per-criterion satisfaction** — 60 bits, **ten times the ordering**

> No new responses. No new recruits. The same four candidates, asked a question with more room in
> the answer.

And the largest of the three is **the one field the release does not ship** — the criterion-by-
response satisfaction that r04 had to rebuild with a local judge, and that every instrument caveat in
this repository exists because of. It is worth **60 bits against the ordering's 5.96**.

## The formulation this sharpens

R224: a core is `(policy, certificate)`, admissible only if `log₂|H(Q)| ≤ H_have`. R226 makes
`H_have` a **design variable rather than a constant**:

> `H_have` is set by the *elicitation format*, not by the candidate count alone. A release that ships
> orderings has chosen a 6-bit channel. One that ships per-criterion satisfaction has chosen a 60-bit
> channel for the same human effort.

## The sentence that can no longer be written

*"The release cannot identify a decision-preserving core because it only shows four responses."* It
cannot, but the candidate count is the **expensive** half of the reason. The cheap half is that it
asked for a ranking.
