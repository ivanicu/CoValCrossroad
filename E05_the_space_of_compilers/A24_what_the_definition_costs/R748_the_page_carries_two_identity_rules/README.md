# R748 · the page's two object counts differ in THREE factors at once, and both move under the rule

**`46` is `[raw cells × full overlap × 56 tags]`. `81` is `[aggregated vectors × subset × 93 tags]`.
They differ in **quantity, rule and population simultaneously** and the deliverable presents them as
one kind of quantity. Holding quantity and population fixed, **both stated counts move under the rule
alone**: 56 tags are **46** objects under full overlap and **39** under subset; 93 tags are **83**
under full overlap and **81** under subset.**

## check #350 — P4 on *every* question, which is R747's own lesson

R747 closed by proposing that the subset-vs-full-overlap choice be priced at the claim level. Running
the gate on that question turned up something larger than a price:

| round | relation | on what |
|---|---|---|
| **R524** | `len(ma)==len(mb) and (ma==mb).all() and array_equal(sa,sb)` | **full overlap**, raw cells |
| **R730** | equal on **shared** prompts, guard `≥0.5·min` | **subset**, aggregated vectors |

…and they disagree on a class both computed: R524's `multi_tag_classes` has
`['coval_core_2bA','coval_core_2bB']`; R730's has `['coval_core','coval_core_2bA','coval_core_2bB']`.

## ⛔ my first implementation was wrong and the control caught it

v1 applied both rules to the **raw satisfaction cells**. `P4` returned **70** against R730's committed
**81** — and the control was right. **R730's relation never touches raw cells**; it compares
`build_vectors()` output, a **per-prompt aggregated agreement score**. So the two published rules
differ in **two ways at once**, the overlap rule *and* the quantity — **R732's failure, in this same
arc** *(ledger 1011)*. Pricing the rule requires holding the quantity fixed, so the grid became
2 quantities × 2 rules × 2 populations.

## the grid — 8 cells, all reported

| quantity | population | full overlap | subset | gap |
|---|---|---|---|---|
| **raw cells** | **56 (R524)** | **46** ← *the page's number* | **39** | 7 |
| raw cells | 93 (R730) | 83 | 70 | 13 |
| agg vectors | 56 (R524) | 45 | 44 | 1 |
| **agg vectors** | **93 (R730)** | **83** | **81** ← *the page's number* | 2 |

⛔ **`subset ≤ full` is FORCED** — full overlap refines subset. *"The count went up"* is not a
finding; only the **gap** is.

⭐ **The quantity matters more than the rule on the 56, and less on the 93** — gaps of 7 vs 1, and 13
vs 2. Aggregation absorbs most of what the overlap rule would otherwise separate.

## E2 — both stated counts move

| stated on the page | full overlap | subset | |
|---|---|---|---|
| *"56 tags are 46 objects"* | **46** | **39** | ⛔ MOVES |
| *"93 tags are 81 objects"* | **83** | **81** | ⛔ MOVES |
| *"13 tags are 10 objects"* | — | — | population not reconstructible — **OUT OF SCOPE**, not assumed unaffected |

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 56 tags under subset | 45, band [40, 46] | **39** raw / **44** agg | ⚠ **the registration was under-specified** — it presupposed one quantity and the finding is that there are two. Reported both; **not** scored by whichever lands in band *(ledger 1012)* |
| P2 93 tags under full overlap | 83 | **83** on both quantities | ✓ |
| P3 reproduce R524's 46 | yes *(hard)* | **46 = 46** | ✓ |
| P4 reproduce R730's 81 | yes *(hard)* | **81 = 81** after the repair | ✓ |
| P5 claims whose stated count moves | 1, band [0, 10] | **2** | in band, point wrong |
| P6 disagreeing classes on the 93 | 2, band [0, 20] | **2** | ✓ exact |
| **D** every disagreeing class carries a strict subset | true | **false** — 1 of 2 | ⛔ **the mechanism is not only subsetting** |

⭐ **D failing is the informative part.** The two disagreeing classes are
`['coval_core','coval_core_2bA','coval_core_2bB']` (**strict subset**, 200 ⊂ 968) and
`['generic','generic_reprov','provenance_probe']` (**no strict subset**). The second is a **partial
overlap** — neither contains the other, yet they share ≥ 50% of the smaller. **My framing that
subsetting is the mechanism is refuted; there are two.**

## ⛔ D2, a DERIVATION asserted and not counted as evidence

The extension's five members sit in **5 classes under subset and 5 under full overlap** — the
extension is **5 objects under both**. A refinement cannot merge what is already separate, so this was
**forced**. It is verified in code and is **not** offered as a result.

## controls — 7 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | a **synthetic strict-subset pair** equal on shared prompts: subset merges **True**, full overlap **False** — **opposite sides**. Band computed: merge-nothing gives 0, merge-everything gives 1 |
| **g=0** | a synthetic **unequal** pair: both rules refuse. **A subset rule that merged unequal arms would have manufactured P1** |
| **NEGATIVE** | distinct seeded noise, 3 seeds → **(93, 93)** every time — both partitions shatter. Excludes *"the partition is driven by tag names"* |
| **SHAM** | ingredient **absent**: the 88 arms sharing one prompt set → full **79**, subset **79**. **The rules agree exactly where overlap is constant** |
| **PLACEBO** | each rule against itself → **0** disagreeing classes, stated as 0 of 93 |
| **P3 / P4** | both instruments reproduce their own committed numbers |

⭐ **The SHAM is what makes the whole grid readable**: where the ingredient is absent the two rules
are *identical*, so the gaps above are attributable to overlap structure and not to two different
implementations quietly disagreeing.

## the sentence I can no longer write

*"56 tags are 46 objects and 93 tags are 81 objects."* Both numbers carry an unstated rule, an
unstated quantity and an unstated population, and both move when the rule alone is changed.

## NEXT

The page now needs each object count to carry its cell — quantity, rule, population — and the eight
cells above supply them. What it does **not** supply is which cell the *claims* should use, and that is not
a matter of taste: claim row 8 (③ misses 2 distinct objects) and claim row 9 both descend from a
partition, and the two rows may descend from **different** cells of this grid. Trace each object-count
claim to the round that computed it, read that round's relation and quantity out of its source the way
this round did, and report the cell per claim. The unit is the claim's provenance rather than the
partition, the instrument is source-reading rather than array comparison, and the outcome is either a
single consistent cell or a list of rows to re-derive.
