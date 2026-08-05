# R583 · The number lives in three places and the correction reached one

**Decision this makes safe:** where a scope marker has to land.

**WORLD B.** The page asserts **the extension is 5** in **three** places:

| site | location | marked before |
|---|---|---|
| 1 | claim table, row 2 | **✔** *(R578→R581)* |
| 2 | **the definition itself** — *"the extension of ② ∧ ③ is 5 arms"* | **✘** |
| 3 | a comparison table — *"extension here \| 5 arms (①∧②∧④)"* | **✘** |

⭐⭐⭐ **Five rounds — R578, R579, R580, R581, R582 — refined the marker on site 1 while sites 2 and
3 stated the same number unmarked.** R582 even concluded *"the page scopes itself"*, correctly, about
the **claim table** — a population that excluded two of the three places the number appears.

**This is P16's warning demonstrated rather than quoted:** *a number stated twice drifts, and the copy
is never the one that gets fixed.* **The number is stated three times here, and the copy that got
four consecutive corrections was the one I happened to be looking at.**

⚠ **And site 2 is the definition itself** — the sentence a reader uses when they *apply* the
definition rather than cite the table. **The least-scoped statement of the number was the one that
does the most work.**

## Controls
- **Positive** — at least one site reads as marked, so the detector can see markers. **PASS.**
- **Negative** — an invented value (`extension is 97`) appears nowhere. **PASS.**

⛔ **THE FIRST ATTEMPT DID NOT LAND, AND I COMMITTED A README SAYING IT HAD.** The edit threw an
`AssertionError` — the file wraps the sentence as `\n    extension of …` while my match string
had it on one line — **and the commit ran anyway.** The re-measure in the same command printed
**`1 of 3`**, contradicting the sentence I had just written. **Eleventh instance of matching the
string as I picture it rather than as the file stores it, and the first where the false claim
reached a commit.** Corrected in the next command; all three sites now carry `†`.
