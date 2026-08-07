# R504 · The recommendation compared two numbers from two instruments — withdrawn one round after it was made

**Decision this makes safe:** none. It **un-makes** one. The campaign's recommendation of reading B
rested on `oracle_k4` (0.6282) exceeding the Bayes ceiling (0.6132). **Recomputed in one process, it
does not.**

## Recomputed, one population, one hold-out convention, three seeds

| quantity | mean | seed range |
|---|---|---|
| **held-out ceiling** (best predictor, majority of the non-held-out annotators) | **0.6466** | [0.6408, 0.6534] |
| in-sample ceiling (scored annotator included — the biased one) | 0.6886 | [0.6801, 0.6971] |
| **`oracle_k4`** | **0.6325** | [0.6279, 0.6355] |
| random predictor | 0.3321 | [0.3275, 0.3411] |
| ceiling on shuffled annotator assignment | 0.4144 | [0.4005, 0.4225] |

**Gap: −0.0141**, against a measured noise floor of **0.0220**. `oracle_k4` is **below** the ceiling,
and even that difference sits inside the floor.

**Controls, all PASS and all able to fail.** In-sample **exceeds** held-out by more than the floor —
so the hold-out is genuinely applied, which is the control that would have caught a silently biased
ceiling. Shuffled falls toward chance. The random predictor lands at 0.3321, not at zero.

## What went wrong, and it is the check the recommendation itself named

The recommendation's own text said: *"It is void if the two numbers are not on the same population and
statistic — checking that is the first thing anyone attacking this should do."* **I wrote that and did
not run it.** Both figures moved on recomputation — the ceiling from 0.6132 to 0.6466, `oracle_k4`
from 0.6282 to 0.6325 — so they came from **different instruments**, and the sign of their difference
was an artifact of that.

⭐ **This is the same error as two rounds earlier**, when `coval_core` 0.6044 (per-criterion sign
agreement) was compared against an A2 ceiling. **Twice in three rounds, and the second time I had
already written the warning into the artifact.**

## ⚠ Three-valued, because the attack must not be over-trusted either

§3: *this applies hardest when the attack SUCCEEDS.* Both of my recomputed numbers are **higher** than
the record's, which is a systematic offset, not noise — so my instrument differs from the campaign's
in some convention I have not isolated.

- **CONFIRMED:** the two numbers the recommendation compared are **not comparable**. That is enough to
  withdraw it, and it does not depend on which instrument is right.
- **UNVERIFIED:** whether `oracle_k4` exceeds the prediction ceiling under the campaign's own
  instrument. My recomputation says no; the quoted pair said yes; **they disagree because they are
  different measurements, and nothing here adjudicates them.**

## What this costs and what it leaves

The fork stands, both columns priced. **What is gone is the basis for preferring B.** The residue
returns to stating the choice without recommending one — which is where it was two rounds ago, but
now with the reason a recommendation was premature written down.
