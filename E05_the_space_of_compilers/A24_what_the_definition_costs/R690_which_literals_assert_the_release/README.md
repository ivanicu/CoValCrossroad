# R690 · which literals assert the release? — **`PUBLISHED_FIVE` names two different sets**

**⭐⭐⭐ Two rounds bind `PUBLISHED_FIVE` to different members — R360 to `coval_core topw_k3 topw_k4
topw_k6 topw_k8`, R442 to `coval_core topabs_k4 topvar_k4 topw_k4 topwvar_k4`. Same name, same claim
about the release, different sets. **That is a concrete cause for R676's "the number five is stable,
the membership is not": the SIZE was carried by a shared NAME while the MEMBERS diverged.****

## THE SWEEP (G3 — every release-asserting literal, none hidden)

| round | name | absent from the card |
|---|---|---|
| **R360** | `PUBLISHED_FIVE` L124 | **4/5** — `topw_k3 topw_k4 topw_k6 topw_k8` |
| **R442** | `PUBLISHED_FIVE` L107 | **4/5** — `topabs_k4 topvar_k4 topw_k4 topwvar_k4` |
| ⚠ R689 | `PUBLISHED` L49 | 4/5 — **this session's own retraction artifact** |

**366 `run.py` scanned · 3 literals · 2 naive instances · both mislabelled.**
Registered **A 8 [2,15] → 3, INSIDE (−5)** · **B 4 [1,10] → 3, INSIDE (−1)** · **directional HOLDS.**

**Controls (the name pattern is an instrument):** POSITIVE — R442's `PUBLISHED_FIVE` found. **g=0** —
`ARMS`, `LABELS` **not** flagged, *the pattern returns both values*. NEGATIVE — a pattern matching
nothing returns nothing. PLACEBO — identical.

## ⚠ ONE OF THE THREE IS MINE, AND IT IS EXCLUDED RATHER THAN HIDDEN
R689's `PUBLISHED` was written **this session, to document the retraction**. Counting it would
inflate the class with the artifact that reports the class. **Both counts are printed; the class
claim rests on the 2 naive instances.**

## ⛔ AND THE VERDICT STRING NAMED THE WRONG ROUND
v1 of the sentence reporting this attributed the sets by **indexing an unordered `set`** — so it
printed R442's members under R360's name. **§4's "the verdict string is not a computation", committed
inside the string that reports a naming defect.** Now computed per round; the failure is kept in the
output rather than quietly fixed.

## ⚠ FLOOR, NOT SIZE
The **NAME** is what is scanned. A set asserting a release property under a neutral name (`FIVE`,
`TARGET`) is invisible to this instrument. **Any count here is a floor on the class.**

## WHAT THIS ADDS TO THE DEFINITION WORK
R676 found six five-member sets whose membership diverged while the count stayed at five, and could
not say why. **This is the mechanism for at least one pair of them:** a shared variable name
asserting a release property, bound to different members in different rounds, with nothing in either
file recording which is meant. **A name is the cheapest thing to reuse and the most expensive thing
to get wrong, because it travels without its definition.**

## IMPOSSIBLE HERE
Whether an author *meant* a name as a release claim is not in the code. The name is the only evidence
and is read as one.

## NEXT
Two rounds bind the same release-asserting name to different members
(`results/release_literals.json`, field `hits`). Check whether the divergence is dated — read the
commit that introduced each binding and compare timestamps — because a name reused after its earlier
meaning was retracted is a different defect from two authors choosing it independently, and a gate on
the retraction ledger prevents the reuse case but not the coincidence case.
