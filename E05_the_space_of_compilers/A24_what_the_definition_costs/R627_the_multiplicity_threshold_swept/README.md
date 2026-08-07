# R627 · The multiplicity signal was the gate's own selection bias

**Decision this makes safe:** whether to build a rarity-weighted anchoring gate. **No.** The signal
R626 found is a property of **which values the gate already knows**, not of being a measurement.

| m0 | P1 prec | P1 rec | **P1 F1** | P2 prec | P2 rec | **P2 F1** |
|---|---|---|---|---|---|---|
| 1 | 0.072 | 1.000 | 0.133 | 0.450 | 1.000 | **0.621** ← peak |
| 5 | 0.248 | 0.571 | 0.346 | 0.647 | 0.298 | 0.408 |
| **9** | 0.382 | 0.420 | **0.400** ← peak | 0.681 | 0.136 | 0.227 |
| 20 | 0.905 | 0.170 | 0.286 | 0.750 | 0.005 | 0.010 |

*(full 20-row curve in the artifact and printed by the round)*

**Pre-registered kill: |argmax F1(P1) − argmax F1(P2)| > 4 → world B. Measured |9 − 1| = 8.**

## ⭐⭐ What the precision columns actually say
- **P1 precision climbs 0.072 → 0.905** across the sweep — a huge, clean gradient.
- **P2 precision starts at 0.450 and reaches only ~0.70** — it barely moves.

The gate's `derive()` list was **hand-built from headline numbers that get cited constantly**, so of
course they are carried by many rounds. **The high-multiplicity signature is "this number is famous
in the project", not "this number was measured."** A round's own reported numbers — the ones a human
put in its results table — are **indistinguishable from random draws by this axis at any threshold
worth using**, and thresholding costs them recall far faster than it buys precision.

## What this does to R626
**R626's measurement stands** — T1 median 14.5, document 3.0, random 1.0 are what they are.
**R626's interpretation is retracted**: *"high multiplicity is the measurement signature"* is refuted
by the class the gate has never read. ⭐ *Two rounds ago the sign was wrong; this round the signal
itself turns out to belong to the instrument rather than the object.*

## ⛔ The circularity was in the closing line, and the check is what caught it
Check #226 flagged *"the gate-verified arm as the positive class"* as circular — **T1 is selected by
the very instrument the rule would extend.** Adding a gate-blind second class cost one extractor and
**overturned the round's headline.** ⭐ *The most valuable thing in this round is a class I only built
because a closing-line check refused to let the positive class stand unexamined.*

⛔ Also caught: *"the previous four rounds each picked one cell"* — **false.** R624 reported a
three-cell curve, R625 a three-band null over three seeds. **Tenth uncomputed quantifier in seventeen
closing lines, and the first to manufacture a fault rather than excuse one** — §4 says the direction
is not systematic, and it now has a measured instance on each side.

## Controls
| control | returned |
|---|---|
| **positive** — recall must be 1.0 at m0=1 for both classes | **1.000 / 1.000** — the positive sets are subsets of the matched population |
| **seeds** — 3, flag verified to change the draws | PASS |
| **negative** — R621's fabricated value | multiplicity **1**, below either peak |
| **placebo** — a threshold above the corpus maximum (m0=191) | recall **0.00**, precision undefined and handled |

**MULTIPLICITY:** 20 thresholds × 2 positive classes × 3 seeds. **The whole curve is reported.**

**IMPOSSIBLE, named:** **neither class is a gold standard.** P1 is the gate's selection; P2 is a
README's, which can name a number its round never measured. **Their agreement would have been the
evidence — they disagree, which is the finding — and two proxies sharing one corpus could not have
ruled out a bias in the corpus itself.**

## The sentence I can no longer write
> *"high multiplicity is the measurement signature."*

**It is the citation signature.** The two coincide only for numbers the project talks about a lot.

## NEXT
Every mechanical route to provenance has now failed for the same underlying reason: **each candidate
signal turned out to be a property of the corpus or of the gate rather than of the number.** That is
four rounds of consistent negative evidence, which is enough to state a bound rather than try a
fifth signal. **Write the bound into `STATEMENT.md`'s register**: name what the assurance suite does
and does not establish about a number, with the 36% collision floor and this circularity as its two
measured limits — because the register is what a next site is checked against, and it currently
implies more than the suite can deliver.
