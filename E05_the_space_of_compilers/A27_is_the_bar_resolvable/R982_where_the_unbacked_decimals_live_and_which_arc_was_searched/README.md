# R982 · no unbacked decimal sits in the statement — and my prediction about which half was better anchored was wrong

**THE DECISION THIS MAKES SAFE.** Whether the definition's own half carries prose-only numbers. It
does not: **0 of 129 distinct decimals in the statement region are held by no artifact**, against
~9.0 expected if every one had been invented.

---

## The result

| half | distinct decimals | T1 gate-verified | T2 anchorable | **T3 unbacked** | T1 share |
|---|---|---|---|---|---|
| **statement** | 129 | 20 | 109 | **0** | **15.5%** |
| record | 2,131 | 156 | 1,968 | 7 | 7.3% |
| whole | 2,175 | 157 | 2,011 | 7 | 7.2% |

**Floor pricing, and it is what makes the 0 mean anything:** the miss rate is **8.2%**, so if all 109
non-T1 statement decimals were invented, **~9.0 would land in T3 by chance alone**. Observed 0.

⚠ **My registered prediction was wrong, and it was wrong in the flattering-to-narrative direction.**
From R981 (340 : 3 assertions favour the record) I predicted the statement would be the worse-anchored
half. By decimal coverage it is the **better** one — 15.5% vs 7.3%. The two measures disagree because
an assertion sitting in the record can cover a decimal that also appears in the statement, which is
R981's own diagnosis read forward instead of backward.

## Two defects in the prior round, both directional

- **R622 scanned one arc.** Its glob is `A24/R*/results/*.json`, so its T3 meant *"absent from A24"*,
  not *"absent from every artifact"* — and every value from the A26/A27 rounds the statement now
  cites was outside its search by construction. Widened here to all arcs: **627 → 785 artifacts,
  36,362 → 103,543 value positions.**
- **R622 split by document, never by half.** `DEFINITION.md` vs `STATEMENT.md`, not statement-region
  vs record-region inside the file a reader opens.

## ⛔ Four control failures, each naming a different real defect

| # | what failed | cause |
|---|---|---|
| ① | **a control that could not fail** | v1 compared today's document to R622's counts with `>=` and passed on **4004 vs 642** — a 6× gap read as reproduction. §4's first row, built again. |
| ② | **wrong baseline revision** | `git log -1` returns the *latest* commit touching R622's artifact, not the one that **created** it. Fixed with `--reverse --diff-filter=A`. |
| ③ | **self-contamination** | two consecutive runs read 784 then 785 artifacts and the record's T3 moved 7 → 0, because run #2 saw run #1's own output. R947 at a new site; this round's own directory is now excluded. |
| ④ | **the unit was wrong** | R622's source reads `decs = sorted(set(DEC.findall(...)))` — **distinct decimals**. I counted **occurrences**: 952 where it committed 642, same regex, same text. |

**The round printed UNVERIFIED each time rather than a world.** Only after ④ did `n = 642` reproduce
exactly and the verdict become admissible.

⭐ **And the control's final form states what it cannot test.** `T1` (140 vs 119) and `T3` (4 vs 16)
are **not** reproducible: `derive()`'s label list and the A24 corpus have both grown since R622, and
both differences are directional. So the control tests the component this round's estimand rests on —
the decimal extractor — against a committed number, and **names the two it cannot test** instead of
loosening the comparison until everything fits.

## ⚠ What T2 is worth, measured rather than assumed

The collision floor, re-measured here at 3 seeds × 4,000 draws over 103,543 value positions:
**91.9% / 92.2% / 91.2%.** An invented four-place decimal matches an artifact value more than nine
times in ten. R625 measured 35–38% on the narrower A24-only scan; **widening the corpus raised the
floor to near-saturation.**

**So T2 is close to information-free per decimal.** What survives is the aggregate: 0 misses of 109
where ~9 were expected. **Widening the scan improved the coverage number and destroyed the
statistic's per-item resolution at the same time** — a better instrument in one direction is a worse
one in another, and only the floor makes that visible.

## What this does not say

- **T1 means an artifact drift breaks the build**, never that the number is correct — R622 states
  this and it is inherited, not weakened.
- **T2 is "some artifact holds these digits"**, never "this claim is checked". R949 measured
  quantity-level agreement separately at **0.200**.
- **One document, one project.** Nothing generalises.

## Alternatives considered

**Report the T1 shares as a headline.** Refused: 15.5% vs 7.3% rests on `derive()`'s hand-written
label list, which R981 showed divides 340 : 3 by a different unit. Two coverage measures that
disagree are a reason to report both, not to pick.

**Drop to 3-place decimals for more population.** Refused: R625 measured the floor at ~92% for three
places and 100% for two, and this round's own widened scan already sits at 92% for **four**. Going
shallower would put the whole census under the floor.
