# R674 · does PROVENANCE open the file it accepts?

**⭐⭐⭐ 47.5% of cited numbers occur in the file cited — against a 3.8% random baseline. Citations
here carry real information and **more than half of them still do not check out**.**

## ⭐ CHECK #275 KILLED THE ROUND'S OWN PREMISE FIRST
R673's NEXT said *"run it over the two known takers of the escape"*. Measured over all **1,233**
commits under the gate's own rule: there is **ONE** taker, `8da27ea`. **Neither R672 nor R673 is
it.** Their quantifiers had no `ARTIFACT` word inside the gate's window, so the lines were never
flagged and `PROVENANCE` never ran on them. R672's commit body announced it was *"deliberately
taking the escape"* — **the gate had not offered it one.** Ledger 743 is annotated in place; its
instance is retracted, its mechanism survives as a **derivation**.

## ⚠ THE ARITHMETIC TRAP, DECLARED BEFORE THE NUMBER
*"A regex cannot open a file"* is read off the source and **could not have come out otherwise**. It
is a DERIVATION and carries no evidential weight. The measurable question — the one this round
answers — is whether the numbers people write beside citations are in the artifacts they cite.

## THE MEASUREMENT

| | |
|---|---|
| (path, number) pairs found | 107 |
| ⚠ unresolvable path — reported **separately**, not folded into failures | 27 |
| decidable | 80 |
| ⭐ number occurs in the cited file | **38 (47.5%)** |
| number absent | 42 |
| **random baseline** (same numbers vs a randomly chosen artifact) | **3.8%** |
| ⭐ **lift** | **+43.8 pts** |

Registered **40% [15%, 70%] → observed 47.5%, INSIDE, error +7.5 pts.**

**Controls.** POSITIVE: a number that *is* in the file verifies. **g=0**: the same control **fails**
on a number the file lacks — it can fail. NEGATIVE: a real file lacking the number fails. PLACEBO: a
nonexistent path returns UNRESOLVABLE, never "verified".

## ⚠ THE DIRECTIONAL FAILED, AND IT IS **UNVERIFIED**, NOT REFUTED
Registered: README verifies **lower** than commit bodies. Observed **60.0% vs 44.6%, +15.4 pts the
other way** — but the 95% bootstrap CI is **[−11.3%, +42.1%]** over n_readme=15, n_commit=65. **The
interval straddles zero.** Calling this a measured reversal would be reading noise; the registered
direction is UNVERIFIED. *A failed prediction is not automatically a discovery in the opposite
direction.*

## SCOPE LIMIT, STATED NOT CORRECTED
Files are read at **HEAD**, not at the commit that cited them. A number true when written and edited
since reads here as a failure. **This biases 47.5% DOWNWARD** — it is a floor on citation quality.

## IMPOSSIBLE HERE
Whether a cited number *means* what its sentence claims needs a reader, not a grep. **Occurrence is
an upper bound on provenance quality**, never a certificate of it.

## NEXT
27 of the 107 cited paths resolve to no file at HEAD (`results/provenance_semantics.json`, field
`unresolvable`). Separate the two causes that share that bucket — a path that never existed, versus
one renamed or archived since — by resolving each against the tree of the commit that cited it
rather than against HEAD. Until they are separated, the 47.5% cannot be corrected for staleness in
either direction, and the size of that correction is unknown rather than small.
