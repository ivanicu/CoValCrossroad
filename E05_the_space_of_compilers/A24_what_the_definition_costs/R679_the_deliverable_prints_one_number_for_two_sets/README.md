# R679 · the deliverable's extension rows cite no producing round

**⭐⭐⭐ All 7 lines in STATEMENT.md asserting an extension size cite 22 rounds between them. The
rounds that PRODUCED those sets are R294, R404, R416, R442, R470, R509. **The intersection is
EMPTY.** The deliverable's central number cannot be traced to the artifact that computed it, by the
deliverable's own citations.**

## ⭐ CHECK #280 · R678's NEXT CITED THE WRONG FIELD
It said `producer_fields` *"names R294, R404, R416, R442, R470 and R509"*. It holds **field** names —
`admitted`, `rubric_rules`, `arms`, `published_five`, `P`, `five`. The round names are in
`producers`. **Third citation defect in this arc**, and R674 measured the class at **47.5%
corpus-wide** — so this is the population, not an anomaly. The numbers in that line were right; only
the pointer was wrong, which is the harder failure to notice, because the sentence reads as verified.

## WHAT WENT WRONG IN THIS ROUND, TWICE, BEFORE IT GOT ANYWHERE

**① The identical regex defect I wrote ledger 762 about — two rounds later.**
`\bR(\d{3})\b` cannot match `R294_the_definition_against_everything`: **`_` is a word character**, so
there is no boundary. The producer map built **0 rounds from 5 paths**. Asymmetric, which is why it
hid: on a *line* like `(R529, R534)` the trailing `\b` works, so half the instrument was fine.

**② The verdict printed a substantive conclusion from an empty population — twice.**
First with a 0-round map, then again after the fix: `killed = len({...}) <= 1` is **TRUE at zero**, so
the round printed *"B NO COLLISION"* about a population that did not exist. **A kill must be gated on
the resolved count before it is gated on its own threshold.**

**③ And the g=0 control PASSED THROUGH BOTH.** Its expectation — *"a line citing a nonexistent round
resolves to nothing"* — is satisfied by a **dead resolver**, because "resolves to nothing" is
simultaneously the control's success criterion and the instrument's failure mode. *§4: a control that
shares the instrument's blind spot confirms the instrument and licenses nothing.* What caught it was
`MULTIPLICITY: 7 lines × 0 producing rounds` printed in the footer.

## THE RESULT

| | |
|---|---|
| lines asserting an extension size | **7** |
| resolving to the ③ extension | **0** |
| resolving to a different set | 0 |
| ⚠ unresolved — cite no producing round | **7** (reported separately, never folded in) |
| rounds cited by those lines | 22 — `R391 R392 R426 R449 R454 R477 R479 R485 R499 R508 R527 R529 R534 R545 R549 R552 R553 R558 R580 R581 R604 R605` |
| rounds that produced the sets | 5 resolved — `R294 R404 R416 R442 R509` |
| ⭐ **overlap** | **EMPTY** |

Registered **A 6 [2,12] → 0, OUTSIDE (−6)** · **B 2 [1,3] → 0, OUTSIDE (−2)** · **directional FAILS.**
**Both registrations presumed the rows were attributable at all.**

## ⚠ WHAT THIS DOES *NOT* SAY
It does **not** say the rows are wrong. A row citing R529 may have re-derived the extension perfectly
well. The claim is exactly: **no extension-size row cites the round that first wrote the set it
names** — a traceability fact, not a correctness one. And the collision question R676 opened is
**UNANSWERED here, not answered negatively**; reporting *"no collision"* would have been a verdict
about an empty population.

## ⛔ A DEFECT IN R678's OWN ARTIFACT, FOUND BY CONSUMING IT
`producers` is keyed by a **two-member prefix** — `"/".join(sorted(s)[:2])` — and `R470.P` and
`R509.five` both begin `coval_core/greedy_k4_fit1`. **Six sets, five keys; R470 was silently
overwritten.** A key built from a truncation is not a key.

## NEXT
The 22 rounds cited by these rows and the 5 producing rounds do not intersect
(`results/deliverable_rows.json`, fields `cited_rounds` and `producer_rounds`). Take the most-cited
of the 22 — R529 and R534, which carry the `③-rank (extension 5)` row — and check whether each
recomputed the set from data or restated it from an earlier round, by looking for the set as a value
in its own `results/` output versus only in its prose. That separates a legitimate re-derivation from
a citation chain with no computation at its end.
