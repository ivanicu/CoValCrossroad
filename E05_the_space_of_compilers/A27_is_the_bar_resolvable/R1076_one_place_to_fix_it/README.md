# R1076 — one place to fix it. ⛔ **38 independent value-membership implementations, 34 precision-blind — and the helper is shipped.**

**The decision this round makes safe:** whether R1075's *"a fix inside one round's script does not
propagate"* was a lapse or a pattern. **A pattern** — and it now has one place to live.

## Result

| | |
|---|---:|
| independent value-membership implementations | **38** |
| **precision-blind (exact)** | **34** |
| precision-aware / tolerance | **4** |

⭐ **The fix has never had one place to live**, so every round re-makes the choice and R1075's
collapse was waiting to happen again.

## ⭐⭐ The remedy, shipped — `assurance/valuematch.py`

```python
def matches(token: str, value: float) -> bool:      # token as written in prose
    dp = len(token.split(".")[1]) if "." in token else 0
    return round(float(value), dp) == round(float(token), dp)
```

**Acceptance test, not the gate's own green:**

| check | result |
|---|---|
| finds the three values R1070's exact test **missed** | **True** |
| still says **no** to an unrelated value | **True** |

The rule it encodes: **when one side of a comparison is a value read from prose, match at that
value's own displayed precision.** Exact matching is correct only when both sides come from the same
computation.

## ⛔ Three classifier repairs, each caught by a control — and the count fell 132 → 38

1. **`main` was classified as a membership test.** Any long function contains ` in `, `==`, `abs(`.
   **Length became part of the definition**, not a convenience.
2. **`cls`, `agree`, `top1`, `rank_obs` were counted** — pairwise-sign and scoring helpers. ⭐ **The
   positive control passed anyway**, because it only checks that known cases are *found*, never that
   what is found is the thing being claimed. **§4's row verbatim.** Fixed by requiring true
   container-membership semantics: ≥2 args, iteration over the second, comparison of the first.
3. **`agree` survived that** — it iterates and compares but **returns a number**. A membership test
   returns a **verdict**. Excluding numeric aggregations is what distinguishes *is it present* from
   *how much does it score*.

**The first count was 132. It is 38.** Each repair was forced by a control that fired, and the
negative control — a named list of known non-membership helpers that must not appear — is what made
repairs 2 and 3 possible at all.

## Controls

- **POSITIVE** — both known implementations found and classified: `has_rounded` → **precision-aware**,
  `has` → **tolerance**. A classifier that misses a known case cannot count unknown ones.
- **NEGATIVE** — a named list of known **non**-membership helpers must not be counted: **True** after
  three repairs; each failure named the stowaway.
- **PLACEBO** — a file with no functions contributes nothing.
- **ACCEPTANCE** — the shipped helper is tested against the values that caused R1075's retraction.

## What this cannot say

⚠ **The classifier recognises membership tests by shape, so 38 is a LOWER bound on
re-implementation.** And **a precision-blind test is not thereby wrong** — exactness is correct when
both sides come from the same computation; it fails only when one side is a displayed value.

## IMPOSSIBLE here

- **whether any particular exact test was wrong in its own round** — needs reading what it compares.
  **SETTLES: IN-RELEASE**, one reading per site.

`run.py` · `results/membership_tests.json` · **ships:** `assurance/valuematch.py`
