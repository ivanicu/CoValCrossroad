# R523 · The six are two — an alias masqueraded as a distinct arm for three rounds

**Decision this makes safe:** how many objects ③'s literal actually misses, and whether R519's
reduction survives.

**Estimand:** for each of the six, exact equality of its saturation matrix against (i) its A/B
sibling and (ii) every arm in R294's census. **Identity, not closeness of a summary statistic** —
a tolerance is precisely what let "matches to four decimals" pass as identity for three rounds.

## Result — WORLD C, and both hypotheses were true

| | |
|---|---|
| `oracle_k4_oracle_kA` == `oracle_k4_oracle_kB` | **True** |
| `greedy_k4_greedy_kA` == `greedy_k4_greedy_kB` | **True** |
| `indep_k4_indep_kA` == `indep_k4_indep_kB` | **True** |
| `oracle_k4_oracle_k{A,B}` == **`oracle_k4`** | ⛔ **True** — an arm the literal already declares |

**Six tags name three objects. One of the three is `oracle_k4`, already in `USES_PROMPT_LABELS`.**

⭐⭐⭐ **So the literal misses TWO distinct objects, not six.**

## ⛔ What this retracts from my own last three rounds

**R521 claimed "four of the six outscore every currently admitted arm."** Wrong three ways:
1. **Two of that four were `oracle_k4` itself.**
2. The remaining margin is `greedy` **0.6292 vs 0.6283 = +0.0009 — inside the MDE of ~0.0105.**
   `indep` at **0.6079** is resolvedly *below*.
3. **The arm being outscored is `oracle_k4`, which ③ excludes** — the comparison baseline was
   itself a label-reader.

**R520's "6 missing" and R522's "6 of 6 BEATS" are counts of TAGS.** The verdicts are correct
per tag; the population was never a list of objects.

## ⭐ What survives
- **R519 is safe.** 0 exact alias pairs among R294's 41 (all 41 readable, positive control passed),
  so its counts — ③ removes 4 of 9 — are counts of **objects**. **The definition ② ∧ ③ stands.**
- **The literal is still incomplete**, by two distinct label-reading objects, and **both BEAT ②**
  (R522's intervals hold per object). **The six-line fix is still warranted.**
- What is dead is the framing: **not "a leaderboard topped by label-readers" — "two more
  label-readers admitted, neither demonstrably above the admitted set."**

## Controls
- **Positive** — arm vs itself equal, `coval_core` vs `generic` unequal. **PASS.**
- **Negative** — a shuffled copy compares **unequal**, so the test is order-sensitive rather than
  comparing a multiset. **PASS.**
- **No noise floor, by design.** Exact equality has none — which is why it is the right instrument
  and a four-decimal agreement was the wrong one.

⭐⭐⭐ **The lesson: R522 saw the match, called it "consistent with oracle-family construction", and
moved on. A narrative reading of what was available as an identity test, for free.**

**Impossible here:** *why* two tags name one object. That lives in the generating invocation, which
the `.npz` does not carry.
