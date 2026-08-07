# R563 · The gates were never silent — my regex was blind to the naming convention

**Decision this makes safe:** whether the nine failures can be triaged. **They can.**

**WORLD B.** R562 concluded *"6 of 9 gates name no concrete object"* using `\bR\d{3}\b`. **Every
round id in this project is `R422_did_the_judge…` — the digits are followed by an underscore, and
`_` is a word character, so the trailing `\b` can never match.** The pattern was blind to the exact
convention it was searching for.

| | gates naming ≥1 object | distinct objects |
|---|---|---|
| old `\bR\d{3}\b` | **3 / 9** | — |
| corrected | **6 / 9** | **182** |

`every_round_reaches_the_readme` names **136** objects and R562 recorded it as naming zero.

## ⭐⭐⭐ The control that makes this a diagnosis rather than a second guess
Both patterns were run on a string **whose answer is known** — `R422_did_the_judge_differ…`:
**the old pattern must MISS it and the new must FIND it.** It did. Without that contrast this would
be one guess replacing another, which is how R562's conclusion was reached in the first place.

## The grouping, now answerable
**182 distinct objects, largest shared appearing in 3 of 9 gates** (`R422`; then `R522`, `R531`,
`R499`, `R486`, `R523` at 2 each). **So the nine failures are mostly about different rounds —
closer to nine defects than to one — but with real overlap that a one-defect-per-round plan would
have missed.**

⚠ **3 gates still name nothing**: `attack_every_check`, `attack_outcome_variable_declared`,
`attack_scope_reaches_the_reader`. **All three are `attack_` meta-gates that audit other gates**, so
naming rounds may be the wrong expectation for them. **Not yet established — stated as open.**

⚠ **`every_round_reaches_the_readme` flags R556–R562 — my own rounds from this session.** Real debt,
created while auditing.
