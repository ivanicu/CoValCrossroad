# R723 · the path was built, not written

**Decision this makes safe:** whether the deliverable may keep saying *at most six independent
computations* stand behind the ③ extension. It may not. **The corrected ceiling is one, and that one
is the set's own producer.**

## What was asked
R680 classified 8 of 20 rounds as DERIVING the extension (no member literals in executable source),
then tightened its own bound by subtracting rounds that read a prior round's `results/` file — it
found **2**, and published **at most 6**. R722 then measured that **four** rounds read
`r360_clause_ledger.json`. Those two counts cannot both be right.

## What was found
**7 of the 8 derivers read a prior round's artifact.** R680's regex found 2 — **recall 0.2857**.

| round | R680 | strict (S5) | path style | reads |
|---|---|---|---|---|
| R294 | ✗ | ✗ | no cross-round path | — (the release's own `corebench/results`) |
| R353 | ✓ | ✓ | single literal | R294 |
| R404 | ✗ | ✓ | built from operands | R360 |
| R405 | ✗ | ✓ | built from operands | R327, R360 |
| R408 | ✗ | ✓ | built from operands | R360 |
| R409 | ✗ | ✓ | built from operands | R408 |
| R519 | ✓ | ✓ | single literal | R294, R436 |
| R667 | ✗ | ✓ | built from operands | R360, R442, R527 |

**The mechanism partitions the population exactly.** R680's regex needs the substring `results/` or
`Rnnn…/results`. A path assembled with pathlib operands — `HERE.parent / "R360_…" / "results" /
"r360_clause_ledger.json"` — contains neither, because the quotes and spaces sit between the
segments. So R680 caught **all** and **only** the rounds that wrote the path inside one string, and
missed **all** and **only** the ones that built it from operands. The measurement is invariant under
a rewrite the property is not — **the same gauge failure R680 itself used to kill R679's proposal
one round earlier.**

## Registered, and what it returned
| point | registered | measured | in interval |
|---|---|---|---|
| A readers at the claim's unit | 7 [2, 8] | **7** | yes |
| B corrected ceiling | 1 [0, 6] | **1** | yes |
| C R680's recall | 0.29 [0, 1] | **0.2857** | yes |
| DIRECTIONAL misses == operand-built | — | **holds** | — |

⚠ **A/B/C were not blind.** `PREREGISTRATION.txt` discloses that an eyeball read of five source
files preceded them. What stayed failable: whether an AST instrument reproduces the eyeball set,
whether the style mechanism discriminates, and every control. Two of those went against me.

## Two of my own instruments failed first
- **v1's style classifier had no positive control.** It matched `R\d{3}[\w*]*/` against every
  executable literal and called R409 *single literal* on the strength of a **prose sentence** —
  `'(R358/R359), so a second judge cannot host this comparison'`. The DIRECTIONAL failed, and the
  cause was my instrument, not the mechanism. *A style classifier is a search, and a search is an
  instrument.*
- **The same prose false-positive was in the headline path.** `cross_round_refs` counted a round id
  inside prose as a cross-round reference. **S5** re-runs the count requiring every reference to sit
  in a *path-shaped* literal. It returns **7** — identical to S2 — so the headline survives the
  strict specification, which is the only reason it is reportable.

## Controls — 7 PASS, 0 FAIL
POSITIVE: R680's own two true positives recovered, band `floor 0 < t 2 ≤ ceiling 8` computed ·
**g=0**: no cross-round literal → 0 · NEGATIVE: R294 reads the **release's** `corebench/results` and
must not flag — the excluded world is *"any file read is dependence"* · SHAM: path in the docstring
only, no read → 0 (absence, not inversion) · PLACEBO: rounds counted as reading themselves → exactly
0 · STYLE: the directional's own classifier, positive on both path styles and null on prose ·
UNIT: instrument unit and claim unit stated as two strings, with the residue named.

## Residue, stated rather than waived
This round measures that the artifact is **read**. It does not measure that its value is **used**.
That is R722's NEXT line, and it is now sharper, not answered.

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r723_reader_recount.json` · 40 classifications, all reported.
