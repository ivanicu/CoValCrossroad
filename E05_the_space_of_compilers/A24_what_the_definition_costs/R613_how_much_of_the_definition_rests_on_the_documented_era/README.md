# R613 · Ten of ten claim rows cite only post-boundary rounds

**Decision this makes safe:** whether eight rounds of provenance work touch the definition. **They do.
Entirely.**

| | |
|---|---|
| claim rows | **10** |
| **anchored** — citing ≥1 round before B = 431 | **0** |
| **post-only** | **10** |
| uncited | **0** |

**Earliest citation anywhere in the claim table: R519** — 88 rounds past the boundary. Row citations
run 519, 520, 523, 524, 525, 527, 528, 529, 530, 533, 534, 535, 536, 537, 558, 580, 581.

⭐⭐⭐ **So the thread R605–R612 is not about the corpus's filing habits. It is about this claim set.**

## The precise scope, because the numbers *are* still anchored
`statement_provenance.py` requires every decimal on the page to appear in `DEFINITION.md`, which is
re-derived from artifacts. So the chain is not broken — it is **one link short**:

> **Every claim rests on artifacts that do not record where THEIR numbers came from.**

**One link is verified; the one behind it is absent.** That is a scope statement, not a retraction —
and it is exactly what six rounds of measuring corpus properties were for.

⚠ **Upper bound, and here it is vacuous in the helpful direction.** *"Cites a pre-B round"* is not
*"takes its number from one"* — but the count is **0**, so there is nothing to over-credit. **The zero
is exact**, and every row is printed so a reader can overrule the classification anyway.

## Controls
| control | returned |
|---|---|
| **parse check (KILL)** | rows parsed **10** = rows visible **10** — a mis-parse would have voided the fraction |
| **positive** | known cited rounds **519, 527, 529** all recovered |
| **g=0** | empty block → **0 rows** — PASS, it can fail |
| **negative** | synthetic post-B row → `pre=[]`; synthetic pre-B row → `pre=[400]` — both classified correctly |
| **placebo** | a row with **no citation** → counted as **neither**, not silently as unanchored |

⭐ **The placebo is the one that mattered to design**: *no citation* and *a late citation* are different
states, and collapsing them would have inflated `post_only` with rows that cite nothing at all. Here
`uncited = 0`, so the distinction changed no number — **but it was made before the count, not after
seeing it.**

**IMPOSSIBLE, named:** which citation carries a row's **number** rather than its **caveat** is not
decidable from the row's text. That needs a round-by-round derivation the page does not carry.

## ⛔ Check #212
R612 closed with *"**every** quantity in this arc is now a property of ARTIFACTS"* — **R602 measured
corpus overlap and R603 measured release schemas, both properties of the DATA FILES.** An "every" over
my own work, false as written. And *"**six** rounds of corpus archaeology"* — **the thread is R605
through R612, eight.** A bare count, wrong, and of exactly the kind the commit gate exists to catch.

## The sentence I can no longer write
> *"the provenance findings are about the corpus, not about the definition."*

**Ten of ten.**

## NEXT
The claim table's citations span **R519–R581**, a 63-round window entirely inside the undocumented era.
**Check whether that window is narrow by necessity or by habit**: count how many rounds in 431–606
exist at all, and what fraction the claim table draws from. If the page cites a small slice of a large
era, the question is why those rounds and not others; if it cites nearly everything available, the
concentration is structural and there was no wider choice to make.
