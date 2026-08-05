# R706 · widening a detector is an experiment — the gate's blind spot, priced before the fix shipped

**The gate could not read `65` of `1270` commits (`58` inside its own 400-commit window). Widened, it
loses `0`, produces `0` false positives against 8 measured wrapped-prose lines, and surfaces `26`
newly-flagged NEXT lines in-window — `0` of which are new violations. The pre-registered kill FIRED
and its own confound explains it: the newly-visible paragraphs are `2.0×` longer, and this gate's
flag rate is a function of verbosity.**

Population **1270 commits, and the gate's own last-400 window, both reported** · instrument **two
regexes plus the gate's existing `flagged()` predicate, held fixed** · baseline **the gate's
documented 37.2% commit-body flag rate** · regime **this repository at HEAD**.

## check #308 — my own count was wrong, by my own failure mode

R705 published *"fifty-eight commits"*. ⛔ **The true figure is 65.** I measured 58 with a hand-picked
character class `^NEXT[.\-—\s]`; the general `^NEXT[^A-Za-z]` finds 7 more, all genuine `NEXT, and …`
paragraphs. §4: **a search is an instrument**, and mine had no positive control — I chose the class,
then published the number in a commit body and a terminal report.

⚠ **And the separator was never the discriminator.** Over 1270 commits a line-initial `NEXT` is
followed by:

| separator | count | what they are |
|---|---|---|
| `:` | 1002 | genuine |
| `.` | 58 | genuine |
| `,` | 7 | genuine |
| ` ` | 6 | **wrapped prose** |
| `-` | 2 | **wrapped prose** |

Requiring **paragraph-initial** `(?:\A|\n\n)NEXT[:.,]` returns 1067 and **zero** space or dash
matches. The paragraph break separates them; the punctuation never did.

⚠ **My control for that was mis-specified too** — I printed "7 known wrapped-prose commits still
matched" at *commit* level while the claim was at *line* level. Those 7 match through their own
genuine `NEXT:` paragraphs. Instrument unit vs claim unit, inside a probe checking a gate that exists
to police exactly that.

## the three registered quantities

| | registered | observed |
|---|---|---|
| **A** newly visible in the 400 window | 25 [5, 65] | **58**, error +33, inside |
| **B** flag rate on the newly visible | 0.40 [0.10, 0.75] | **0.4615**, error +0.062, inside |
| **C** LOSS — paragraphs the old rule found and the new does not | 0 [0, 10] | **0** |
| directional | \|rate difference\| inside the null | ⛔ **FAILS** — the kill fired |

## ⛔ the kill fired, and its own confound explains it

Raw: newly visible **0.4615** vs already visible **0.2655**, difference **+0.1961**, p = **0.0008**,
outside the permutation null `[−0.1152, +0.1142]`. World B — *a different population*.

Then the confound, **written after the fact and labelled as post-hoc, which is the weakness**:
`flagged()` scans a 60-char window, so a longer paragraph has more chances **by construction**.

| pooled length decile | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| already visible | 0.065 | 0.204 | 0.170 | 0.229 | 0.173 | 0.272 | 0.340 | 0.272 | 0.371 | **0.620** |
| newly visible (n) | – | – | – | – | 1 | 2 | 6 | 12 | **37** | 7 |

Median length **479 vs 242** chars. **The shortest four deciles contain zero newly-visible
paragraphs** — the raw comparison was between two barely-overlapping length distributions.
Length-matched, the difference falls to **+0.0908**, inside a stratified null `[−0.1335, +0.1337]`,
p = **0.1933**. **54% of the raw gap is length.**

⭐⭐ **The instrument finding is the bigger one:** this gate's flag rate is monotone in verbosity —
`0.065 → 0.620` from shortest to longest decile — so *"quantified NEXT lines"* partly counts long
paragraphs. **Every round in this arc has been passing that gate.**

## controls — 7 PASS, 0 FAIL

| control | returned |
|---|---|
| POSITIVE | the gate's own known-false NEXT lines: old finds 3, new finds 3, all flagged |
| FALSE-POSITIVE | 8 **measured** wrapped-prose lines wrongly extracted: **0** — real corpus lines, never invented ones |
| g=0 | old-vs-old: loss 0, gain 0 — the machinery returns nothing when nothing changed |
| NEGATIVE | label-permutation null, then a **length-stratified** one after the confound appeared |
| SHAM | localisation removed (first 200 chars of each body): **0.2039** vs the located **0.2774** |
| PLACEBO | two identical runs differ by exactly 0 |
| UNIT | instrument unit `A NEXT PARAGRAPH` ≠ claim unit `A COMMIT` |

## specification curve — 2 windows × 4 separator sets, all reported

| window | separators | found | loss | gain | flag rate | false pos |
|---|---|---|---|---|---|---|
| 400 | `:` | 329 | 0 | 0 | 0.2948 | 0 |
| 400 | `:.` | 387 | 0 | 58 | 0.3178 | 0 |
| 400 | `:.,` | 387 | 0 | 58 | 0.3178 | 0 |
| 400 | `:., -` | 387 | 0 | 58 | 0.3178 | 0 |
| all | `:` | 1002 | 0 | 0 | 0.2655 | 0 |
| all | `:.` | 1060 | 0 | 58 | 0.2755 | 0 |
| all | `:.,` | **1067** | **0** | **65** | 0.2774 | **0** |
| all | `:., -` | 1067 | 0 | 65 | 0.2774 | 0 |

⚠ The unsafe set is included so the curve shows what it costs rather than asserting it. Under the
paragraph-initial rule the space and dash separators add **nothing** — which is itself the evidence
that the paragraph break, not the punctuation, is doing the work.

## what shipped

1. **Extractor** → `(?:\A|\n\n)NEXT[:.,]`, with the measurement above written into the code beside it.
2. **Per-item empty-population guard** — HEAD having no extractable NEXT paragraph now exits 1. The
   corpus-level guard could never fire when *one* commit contributed nothing, which is precisely how
   R704's false quantifier passed. **Positive-controlled**: planting HEAD into the missing list
   returns exit 1; and 0 of the 13 genuinely-missing commits contain even a leading `next` line.
3. **26 newly-flagged lines frozen with an individual reason** — *invisible to the pre-R706
   extractor*. All 26 were invisible to the old rule, so **none is a new violation**; they are
   history the gate could not read, frozen as history and not as an acquittal of the sentences.

## limits

- The flag-rate comparison is a property of **this history**, not of NEXT lines in general.
- `flagged()` is held **fixed**: this round tests the extractor and deliberately never the predicate.
  The verbosity dependence measured here is a finding *about* the predicate that this round does not
  act on.
- The confound was found **after** the kill fired. It should have been pre-registered, and the fact
  that it turned a p = 0.0008 into p = 0.1933 is the argument for pre-registering it.

## impossible here

| criterion | what it would require |
|---|---|
| cross-release | the `NEXT` convention is this project's |
| construct validity of "a quantifier needing a source" | `flagged()` *is* the construct here |

---

## ⚠ ANNOTATED BY R707 (2026-08-05) — two corrections

**① This round's citation does not resolve.** Its NEXT line cites the decile rates *"from
`results/widening.json`"*. That artifact holds **no** decile table, no length-matched difference and
no stratified null — `0.065` and `0.620` appear only inside the prose `world` string. §5 requires the
artifact to carry what a later round needs to ATTACK the result, and this round's central finding —
the confound that overturned its own pre-registered kill — was printed and discarded. R707 recomputes
and persists it as fields; this artifact is not re-run (ledger 848).

**② The instrument finding above is LARGELY RETRACTED.** "This gate's flag rate is a function of
verbosity, the wrong direction" reads a `9.6×` rise across length deciles as a defect. R707
decomposes it: **`9.571 = 5.324 × 1.798`** — opportunities per paragraph × a per-opportunity
residual. `flagged()` is a **presence** detector, so `1−(1−p)ⁿ` rises with n by construction, and the
length-normalisation this round's NEXT line proposed **would have broken a mostly-correct detector**.
⭐ What R707 found instead is worse and different: a word-scrambled corpus still flags at `0.2100`
against the real `0.2772`, so **≈76% of the flagging is proximity by chance**.
