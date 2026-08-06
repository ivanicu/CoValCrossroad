# R802 · the impossibility register audited — 1 of 30 lines is false, and it is one I wrote 8 times

`run.py` · `PREREGISTRATION.txt` · `results/register_audit.json` · 13 rounds × 52 register lines ·
**WORLD A** · two hash seeds byte-identical, md5 `3f2476e4abd9c399ba916d32ce16a050`

## THE DECISION THIS MAKES SAFE

**The impossibility register is mostly sound — and the one line that is false is mine, repeated
across 8 rounds of this session.**

| | |
|---|---|
| register lines written by R789–R801 | **52** (tight extractor) · 65 (loose) · ratio 1.25 |
| distinct claims after normalisation | **30** |
| **claims that did not survive one grep** | **1** |
| **base rate** | **3.3%** |
| rounds the false line contaminated | **8** — R791, R792, R793, R795, R796, R798, R799, R800 |

⚠ **And the over-correction is refuted by the same count.** World B — "impossibility is a genre
convention here" — required ≥ 2 false lines and got 1. §4's own warning against reading a defect as a
pattern applies to this round's author, and the number is what stops it.

## ⛔⛔ THE FALSE LINE, AND WHERE ITS REFUTATION HAS BEEN SITTING

Eight rounds wrote *"cross-release: a second values-annotation release"* into their IMPOSSIBLE
tables. **`data/utterances.jsonl` exists — 68,231,088 bytes, 68,371 records — and 23 rounds of this
arc open it in their `run.py`.** `STATEMENT.md`, the document I appended to in every one of those
rounds, has quoted R601 all along: *"Eighteen rounds score on `data/utterances.jsonl`, the second
release."*

⚠ **D2 makes the count conservative**: a `run.py` grep cannot overcount readers, so **23 is a lower
bound**, and it already exceeds R601's committed 18.

## ⚠ BUT THE LINE IS TOO BROAD, NOT SIMPLY FALSE — D3, BOTH READINGS

| reading | verdict | why |
|---|---|---|
| (i) *any second corpus with human judgement* | **FALSE** | 68,371 utterances carry a human `score` (1–12), 2–4 responses per turn, and **R413 already derives an ORDERING from it** — the exact structure `cls()` consumes |
| (ii) *a second corpus with RUBRICS and per-annotator rankings* | **UNVERIFIED** | `utterances.jsonl` has **no rubric criteria and no ranking blocks**, so the pool comparisons of R795–R801 genuinely cannot be made there |

**Calling the line false outright would be the cheap attack §3 forbids.** What is established is that
it was written at a width its author never checked, and that width made a real second release
invisible for eight rounds.

## ⛔ AND R801's OWN CLOSING SENTENCE WAS WRONG IN BOTH NUMBERS

R801 closed with *"the §4 test … which this arc has run on two of its five clauses."*

| | claimed | measured |
|---|---|---|
| clauses in the definition | five | markers in STATEMENT + DEFINITION: **① 6 · ② 56 · ③ 18 · ④ 0 · ⑤ 0** — and R436 is titled `does_clause_four_exclude_anything_at_home`, so ④ exists by title while carrying no marker |
| rounds running the exclusion test | two | **7** — R360, R403, R436, R464, R665, R688, R790 |

**"Five" was imported from §4's narrative about a different morning's clauses.** §4's remedy — *run
the count before writing a sentence that quantifies* — would have cost one grep, and this is the
**fourth** closing-sentence quantifier this session to fail it (R796's, R799's, R801's, and the
"five clauses" here).

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `utterances.jsonl` present, **68,231,088 bytes**; **23** readers against R601's committed floor of 18 | PASS, else exit 2 |
| PLACEBO | the extractor over an **empty** file list: **0** lines, not an error swallowed as 0 | PASS |
| POSITIVE | a known-**true** line (*"independently replicated — the session prompt forbids agents"*) → **UNVERIFIED** | PASS — **not condemned**; an instrument that condemned it would be over-firing |
| NEGATIVE | a known-**false** line (*"requires a fourth response per prompt"*, which the release supplies) → **FALSE** | PASS — condemned; without this the extractor was untested in one direction |
| BOTH EXTRACTORS | tight 52, loose 65, ratio **1.25** — inside the pre-registered factor of 2 | PASS |
| SELF | R802 excluded from its own population (D4), and the exclusion printed | as R793 had to |

## MULTIPLICITY

No line was selected for examination by its content, so there is nothing to correct. **All 29
non-refuted claims are listed in full** in the run output rather than summarised — a register audit
that reports only its hits is the multiplicity failure with manners. The most-repeated survivors are
*independently replicated* (13 rounds), *construct validity* (3) and *a blind pool larger than 16*
(2).

## WHAT DIED

- **the cross-release line as written** — too broad, and 8 rounds inherited it.
- **R801's "two of its five clauses"** — both numbers wrong, both checkable with one grep.
- **World B, the flattering-in-the-other-direction reading** — 1 false line of 30 is not a habit, and
  saying it was would have been its own error.

## WHAT SURVIVES

**29 of 30 impossibility claims**, unrefuted by this audit — which is *not* an acquittal (D1: an
impossibility is a universal claim; FALSE needs one counterexample, TRUE needs an argument this data
cannot supply). And the register's value: it is the only reason the cross-release lapse was
findable at all, because the lines were written down in a fixed place and could be extracted
mechanically.

## SCOPE

13 rounds (R789–R801), R802 self-excluded · 52 tight / 65 loose register lines → 30 distinct claims ·
instrument a mechanical extractor over `## IMPOSSIBLE HERE` tables, run in both forms and validated
in both directions · this repository at this tree_sha.

## IMPOSSIBLE HERE — each checked before being written

| | what it would require |
|---|---|
| whether an impossibility line is TRUE | an argument, not data (D1) — this round returns UNVERIFIED and never "confirmed" |
| scoring a core's criteria on the second release | a judge pass over its 68,371 utterances; `sat_*.npz` are keyed to the first release only — **checked**, no sat file covers utterance ids |
| independently replicated | a second designer; the session prompt forbids agents — used here as the POSITIVE control rather than taken on faith |

## NEXT

The register's one false line hid a second release with 68,371 human-scored responses that 23 rounds
have already read. Computed by this round's `run.py`, reading (i) of that line is refuted and reading
(ii) stands. So the step is the one the false line was suppressing: **take R794's Q2 — the released
core beating `coval_full` at predicting humans, +0.0578 [+0.0502, +0.0658] — and ask what of it is
statable on `utterances.jsonl`**, where the human judgement exists but the rubric does not. That is a
transportability question with a real second corpus, and it is the first one this arc can ask without
a new judge run only if the answer turns out to live in the human side alone — which is exactly what
the round must establish before spending anything.
