# R440 · the four clauses on **one** arm space — and ④'s zero is the argument

**The decision this round makes safe:** whether the definition's cost table can carry a fourth row
without committing the scope error the campaign has retracted most. **It can** — `W-FILLABLE`,
coverage **42/42**.

## The table, all four rows on R360's published 42-arm space

| clause | excludes | status |
|---|---:|---|
| ① better than a random draw of the prompt's own rubric | **0 of 41** | DERIVED — *R347's space, not this one; left as is rather than silently harmonised* |
| ② better than a prompt-blind set | **33 of 42** | MEASURED |
| ③ no prompt labels | **4 of 42** | DERIVED |
| **④ better than every criterion-free rule** | **0 of 42** | **MEASURED** |

## ⭐ The zero is the argument, not an embarrassment

**④ costs the home release nothing** — it removes no arm the definition already admits. On the
second release it removes **all 7** while ② removes **none** (R434).

**A clause that is free where the definition works and binding where it fails is what a sufficiency
clause is for.** A *non-zero* here would have meant ④ was quietly re-litigating ②'s boundary — which
is exactly what R439 ruled out from the other direction (its bar is at the 0.00th percentile of ②'s
own reference pool).

## Controls

| control | returned |
|---|---|
| **POSITIVE — reproduce ②'s published row from the artifact** | **33 of 42**, matching `DEFINITION.md` ✅ |
| NEGATIVE — ③'s set counted **verbatim**, not recomputed | `{greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1}` → **4 of 42** ✅ |
| coverage — R436's scored set over R360's space | **42/42 = 1.0000**, printed *before* any count ✅ |
| PLACEBO — arms excluded by "no clause at all" | **0** ✅ |
| g=0 — no arm excluded on a zero difference | ✅ |

**The POSITIVE is the load-bearing one.** Had it failed, this round would have been reading a
*different population* than the table's other rows, and its fourth row would have been a fourth
population presented as a comparison.

⚠ **③ is counted verbatim on purpose.** The definition applies clause ③ *by inspection* with a
hand-written list; deriving it from a rule of my own would substitute my reading for the document's
text and the count would silently become a claim about my rule.

## ⛔ The pre-check that got it backwards

Before writing this round I ran an inline check that sampled **13 arm names from the definition's
prose**, found all 13 present in R436's scored set (`missing = []`), and printed **"the spaces are
NOT nested"** — a verdict string contradicting its own data.

**And the check was unfit even where it was right:** its unit was *13 hand-picked names*; the claim's
unit was *a 42-arm space*. Both failures are on this campaign's ledger, and the fix was the same one
both rows prescribe: **read the arm list from R360's artifact instead of sampling names.** It turned
out to be complete coverage — which the loose check could not have established either way.

## Impossible here, named

- **a fourth row on the second release's space** — ② admits 0 there (R434), so every count is 0 and
  the row would carry no information. Requires a release where ② is non-empty *and* ④ is scored.
- **①'s row on this space** — DERIVED, not measured; recomputing it is R347's job. Its `of 41`
  denominator is left visible rather than harmonised, because a harmonised denominator I did not
  recompute would be a number with no round behind it.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
