# R681 · fixture or finding?

**⭐⭐⭐ Only 1 of the 12 rounds hard-coding the ③ extension lets it reach an output field. Eight use
it purely as a comparison target. The hard-coding is overwhelmingly legitimate — which strengthens
R680's "at most 6 independent computations" instead of threatening it.**

## THE RESULT

| what the literal does | rounds |
|---|---|
| **BOTH — compared *and* dumped** | **R442** |
| **FIXTURE — comparison target only** | R301 R330 R332 R339 R354 R529 R534 **R677** |
| **OTHER_USE — used in a way this classifier does not model** | R360 R361 **R676** *(the three 5/5 sets)* |
| UNUSED | none |

- reaches an output field: **1 of 12** · Registered **A 5 [2,10] → 1, OUTSIDE (−4)**
- of the three 5/5 rounds reaching output: **0** · Registered **B 2 [0,3] → 0, INSIDE**
- **DIRECTIONAL FAILS** — R676 (mine) is `OTHER_USE`, not `OUTPUT`

**Controls:** POSITIVE — a literal passed to `json.dump` → `OUTPUT`. **g=0** — a literal only compared
→ `FIXTURE`, *the classifier returns both values*. NEGATIVE — bound and never used → `UNUSED`.
**4th-CAT** — used in a way the three categories miss → `OTHER_USE`, separable from `UNUSED`.
PLACEBO — run twice identical.

## ⚠ `NEITHER` WAS A RESIDUAL BUCKET WEARING A MEASUREMENT'S NAME
The first run called R360, R361 and R676 **`NEITHER`** — which reads as *"the literal is never used"*.
Checking the AST parents: **R676's literals are arguments to its own control calls** (`jac([...],
[...])`), and R360/R361 bind `PUBLISHED_FIVE` / `FIVE` to names used in ways the three categories
never enumerated. **None of them is unused.** Split into `OTHER_USE` (referenced, unmodelled,
**UNVERIFIED** as to fixture-vs-finding) and `UNUSED` (genuinely never referenced).

**This is ledger 748 — *"a bucket named for what it lacks hides how many distinct causes are in it"* —
recurring 33 entries after I wrote it.**

## ⭐ ADDING A CATEGORY ADDS A WAY TO BE WRONG, SO IT NEEDS ITS OWN CONTROL
Renaming `NEITHER` → `UNUSED` **broke the negative control's expectation**, and the control failed
loudly — which is what a control is for. A fifth control was added for the new category, because a
classifier with an unexercised category has an untested branch.

## WHAT THIS DOES TO R680
R680 bounded independent computations at **≤6** and could not separate copying-through-a-file. This
round shows the 12 restaters are **not a threat to that bound**: eight compare against the set
(legitimate), three use it unmodelled, and only R442 dumps it — and R442's own estimand *is* the
extension as written, so a comparison set in its output is expected. **The hard-coded set is not
circulating as false evidence.**

⚠ **UPPER BOUND:** reaching an output field is not *being reported as a finding*. Dumping a fixture
for provenance is good practice. Whether a dumped value is **presented** as a result is a fact about
the prose that quotes it, and **no AST reads that**.

## IMPOSSIBLE HERE
Separating "dumped as provenance" from "dumped as a finding" needs the reader, not the parser.

## NEXT
Three rounds sit in `OTHER_USE` — R360, R361, R676 (`results/fixture_or_finding.json`, the `rows`
list). The classifier models comparison and dumping and nothing else, so those three are unverified
rather than cleared. Read the two Assign cases directly: `PUBLISHED_FIVE` in R360 and `FIVE` in R361
are module-level names, and what a module-level constant feeds is answerable by tracing its Load
sites, which the current classifier collapses into one boolean.
