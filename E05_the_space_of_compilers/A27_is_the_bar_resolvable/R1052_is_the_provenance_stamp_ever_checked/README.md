# R1052 — is the provenance stamp worth anything? ⛔ **Three findings: R1051's census is retracted (9 stamps, not 13), the ancestry test is UNVERIFIED against its own floor, and R1049's count is retracted from a quarter to two thirds.**

**The decision this round makes safe:** whether the stamp field adds anything to re-derivation.
**It does not, on this evidence** — and 4 artifacts counted as stamped carry no stamp at all.

## ⛔ Finding 1 — the census matched the KEY NAME, not the VALUE TYPE

Four artifacts have a `head` field holding a **title string**, not a hash:

| round | `head` value |
|---|---|
| R1000 | `the four cla…` |
| R1001 | `the operator…` |
| R1005 | `does the ext…` |
| R1012 | `does the loa…` |

⭐ **True provenance-stamp count: 9, not 13. Rounds with no usable stamp: 7, not 3.** The
instrument's unit was *"a key called `commit`/`head`"*; the claim's unit is *"a git hash"*. **The
sixth unit mismatch this window**, and the remedy §4 prescribes — name both units and require them
equal *before* designing the control — would have caught every one of them.

⭐⭐ **And it explains something R1051 could only scope, not justify: the true-stamp set is EXACTLY
the byte-mismatch set (`True`).** R1051 measured that 9 of 16 differ on bytes and narrowed its
mechanism to those 9 without being able to say why the other 4 "stamped" rounds didn't move. **A
stamp that tracks HEAD changes on every re-run; a title does not.**

## ⛔ Finding 2 — the ancestry test is UNVERIFIED against its own floor

The falsifiable prediction: a stamp records HEAD at **run** time, the artifact is committed **after**,
so every honest stamp must be an **ancestor** of its artifact's introducing commit.

| | |
|---|---:|
| checked | **9** |
| ancestor of its own introducing commit | **9 of 9 = 1.000** |
| **measured floor** — a *random* commit from this history, 3 seeds | **[0.889, 1.000]** |

⭐ **1.000 does not clear a floor of [0.889, 1.000].** Almost any commit in this history is an
ancestor of a past introducing commit, so **passing carries no information about the stamp**. Neither
world is separable. **UNVERIFIED — not a vindication of the stamp, and not a condemnation.**

⚠ The stamps are *individually* coherent — R921 stamps `070de951`, which is R920's introducing commit
— but a pattern that a random draw reproduces at ≥0.889 is not evidence.

## Controls

- **POSITIVE** — the ancestry test must return **False** for the current HEAD against a past
  introducing commit: **True**. A test never shown to return False is silence.
- **NEGATIVE** — a commit is an ancestor of itself, and the root is an ancestor of HEAD: **True**.
- **NOISE FLOOR** — random commits, 3 seeds: **[0.889, 1.000]**, and it is what decides the verdict.
- **PLACEBO** — unstamped artifacts contribute no denominator; reported (**3**), never scored.
- **EMPTY POPULATION** — exit **2**, never 0, at both stages.

## ⛔⛔ Finding 3 — R1049's count is retracted, and it was found the same way as R1048's

This round's own fact registered **GREEN with nothing written**, and only **one** of its two patterns
matched anything. Reading the gate's source settles why:

```python
ok = any(re.search(p, region, re.I | re.S) for p in pats)     # assurance/…arc.py:790
```

**The gate passes on ANY pattern.** R1049's multi-home predicate was `all(homes >= 2)` — **modelled
from memory rather than read** — so it demanded *every* pattern have a second home. Under `any()`
semantics **one loose pattern is enough to carry the pass**, so the correct predicate is
`any(homes >= 2)`.

| predicate | unattributable |
|---|---:|
| `all` — R1049's, wrong | **21 of 67** |
| **`any` — correct** | **45 of 67 = 0.672** |

⭐ **R1049 reported 0.254 and landed in neither pre-registered band. The corrected 0.672 clears
World B: the currency gate is permissive by construction.** Newly flagged includes `R1003 R1006
R1009 R1010 R1013 R1016 R1019 R1020 R1021 R1022 R1023 R1024` and more. **2 patterns remain
statically unreadable — reported, never dropped.**

⚠ **This propagates to R1050**, which used the 16. Its permutation floor would also rise with a
larger flagged set, so **R1050's `0.917` vs `[0.490, 0.524]` must be recomputed before it is quoted
again** — the direction of the change is not predictable from here.

## What stands

⭐ **Ancestry is necessary, never sufficient** — it cannot show the stamped commit is the one the code
ran under. **Re-derivation is the sufficient test, and R1051 has it for all 16.** So the 3 unstamped
artifacts are **no worse off** than the 9 genuinely stamped ones, and R1051's NEXT — trace the
unstamped 3 through git — was aiming at the weaker question.

## IMPOSSIBLE here

- **whether a stamped commit is the one the code actually ran under** — needs a record of the run,
  which is the very thing the stamp was supposed to be. **SETTLES: OUT-OF-RELEASE.**

`run.py` · `results/stamp_vs_history.json`
