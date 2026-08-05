# R678 · git supplies the lineage the artifacts omit — producer, not popularity

**⭐⭐⭐ All 6 five-member sets have a unique producing commit, and exactly ONE denotes a ③-reading
extension: `{coval_core, topw_k3, topw_k4, topw_k6, topw_k8}`, produced by R294. R677's range 0–1
collapses to 1 — the majority aggregator was simply wrong.**

## THE LINEAGE (G3 — all six printed)

| producer | field | what it denotes |
|---|---|---|
| **R294** | `admitted` | ⭐ **`a_three_extension`** — the one genuine ③ reading |
| R404 | `rubric_rules` | a ③ round, but a different field |
| R416 | `arms` | unrelated (which arms' criteria differ) |
| R442 | `published_five` | **CoVal's publication list** |
| R470 | `P` | **before ③ is applied** |
| R509 | `five` | **before ③′ is applied** |

**Registered A: 5 [3,6] → 6, INSIDE (+1). Registered B: 2 [1,4] → 1, INSIDE (−1).**

## ⛔ THE DIRECTIONAL FAILED, AND THE FAILURE IS THE USEFUL PART
Registered: the producer-based count differs from **both** R677 aggregators (0 majority, 1
any/earliest). **It equals the any/earliest one.** So the lineage fact does not overturn both rules —
**it adjudicates between them**: majority-over-citations was wrong, any/earliest was right for the
right reason. R677's *"not identified, range 0–1"* is now **identified at 1**.

## ⭐⭐⭐ THE g=0 CONTROL VOIDED THE FIRST RESULT, AND WITHOUT IT THIS ROUND SHIPS A FICTION
v1 asked `all(f'"{m}"' in blob for m in s)` — whether five strings **co-occur** in a file. A
**synthetic combination never committed** resolved to `corebench/results/leaderboard.json`, because
that file lists **every** arm. So did three sets "produced by" R294's `full_census.json`, for the
same reason. **Instrument unit was "five strings present in a blob"; claim unit is "a file holds this
SET as a value."** Repair: parse the JSON and require a list field whose sorted contents **equal**
the set. **A unit fix the control demanded — not a threshold moved after seeing the answer.**

**Controls after repair:** POSITIVE — a set with a known producing round → **R442** → PASS. **g=0** —
never-committed combination → **none** → PASS, *it locates rather than matches*. NEGATIVE — real arm
names in an uncommitted combination → none. PLACEBO — search run twice → identical.

## ⚠ I REGRESSED TO A CRUDER CLASSIFIER ONE ROUND AFTER VALIDATING A BETTER ONE
The first B used a bare *"does ③ appear in the producer's ESTIMAND"* test and returned **5** — counting
`R470`, whose estimand is literally *"the extension **BEFORE** ③ is applied"*. **That is the exact
error R677 was built to catch.** Re-running with R677's validated classifier (`b_before_three` /
`c_publication_list` / `a_three_extension`) gives **1**. Both numbers are recorded.

## THE LIMIT, CARRIED INTO THE VERDICT AND NOT LEFT IN A DOCSTRING
**Git records WRITES, not COMPUTATIONS.** A set computed in one round and first written in another is
attributed to the **writer**. That gap is not closable from history alone, which is why this is
**lineage**, not provenance. *(Ledger 750: naming a limit in prose does not propagate it into the
number — so it is stated in the verdict string itself.)*

## IMPOSSIBLE HERE
Attributing a computation rather than a write would need every round re-executed against its own
inputs; **93 rounds in this arc are corpus-dependent** and would not reproduce. Named, not planned.

## NEXT
One set is the ③ extension and five are other objects (`results/lineage.json`, fields
`producer_fields` and `n_three_by_producer`). The deliverable's claim table cites the number 5 for
the extension. Compare each such row's cited round against the producer map in
`results/lineage.json` — whose `producer_fields` names R294, R404, R416, R442, R470 and R509 — and
report how many rows cite a set that does not denote what the row says it does. A row resting on
`R442.published_five` or `R470.P` would be citing a publication list or a pre-③ set for a ③ claim.
