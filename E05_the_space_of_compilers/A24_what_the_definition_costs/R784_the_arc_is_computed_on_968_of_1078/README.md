# R784 · this arc is computed on 968 of 1078 ranked prompts, and whether that decile is representative cannot be resolved here

`run.py` · `PREREGISTRATION.txt` · `results/population.json` · 1078 ranked · 968 scored · 110 excluded

## THE DECISION THIS MAKES SAFE

**Every number in this arc carries an unstated population restriction, and it must be written into the
scope line from here on.** `load_targets()` returns **1078** prompts with parsed human rankings;
`core_full.json` covers **968**. **110 ranked prompts — 10.20% — have no rubric**, and no filter in
this repository accounts for it: the `>=2 rankings` rule drops **0**, and absence from the sat file
drops **0**. The arc's population is **89.80% of the ranked corpus**, selected upstream.

## ⛔ AND THE ROUND'S OWN HEADLINE DIED TO ITS PRE-REGISTERED ESTIMATOR

Check #386 found the 110 carry **2.4× the unacceptable flags** — mean **10.109** against **4.163** —
and that was the striking fact this round was built around. **It does not survive.**

| axis | mean 968 | mean 110 | median 968 | median 110 | variance ratio | rank statistic | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| rankings per prompt | 16.108 | 25.373 | 16.0 | 17.0 | **395.80** | +0.0526 | inside null |
| unacceptable flags | 4.163 | **10.109** | **0.0** | **0.0** | **82.99** | −0.0530 | inside null |
| flag rate per ranking | 0.341 | 0.290 | 0.0 | 0.0 | 0.99 | −0.0510 | inside null |

**Both medians are 0 and the rank statistic is −0.0530, inside its permutation null of [−0.0896,
+0.1029].** The 2.4× is entirely a tail effect — a variance ratio of **82.99**, with one prompt
carrying **1012** rankings.

⭐ **D2 fixed the estimand on medians and a rank statistic BEFORE the statistic ran**, on the variance
ratio alone. Had the mean been reported, this round would have published a false finding about the
corpus the whole arc rests on. Choosing the estimator after seeing the outcome is the specification
failure; choosing it from the variance in advance is what caught this.

## THE VERDICT IS **C — UNDERPOWERED**, NOT "NO DIFFERENCE"

| | |
|---|---|
| this design, n = 110 vs 968 | MDE **0.2819 SD** |
| R783's proposed n = 18 vs 968 | MDE **0.6665 SD** — priced rather than run |
| POSITIVE's measured sensitivity | resolves at **0.50 SD**, not at **0.25 SD** |

**A null at 0.28 SD does not license "the exclusion is incidental."** And the 110 is all there is — to
reach 0.20 SD needs n = **246**, 0.15 SD needs **545**, 0.10 SD needs **4,149**. **So the character of
the excluded decile is permanently unresolvable below ~0.28 SD on this site**, and that is the
finding: not that the exclusion is harmless, but that it cannot be shown to be.

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 1078 = 968 + 110 exactly · 986 released · 18 unscored (R783) · `>=2 rankings` drops 0 · sat-file absence drops 0 | PASS, else exit 2 |
| PLACEBO | the 968 against itself, rank statistic **+0.000000** | PASS |
| g=0 | 200 random 110-subsets of the 968 against their complements: rankings [−0.1063, +0.1074] · flags [−0.0857, +0.0931] · rate [−0.0980, +0.0859] | **D3's world built synthetically, not assumed** |
| POSITIVE | 0.00 SD inside · 0.25 inside · **0.50 RESOLVES** · 1.00 RESOLVES | PASS, band computed at both ends |
| NEGATIVE | group-label permutation, 200 draws | ⭐ **valid here** — see below |
| CONFOUND | flag **rate** reported beside the raw count, since a prompt with more rankings has more chances to be flagged | rate rank −0.0510, also inside null |
| ROBUST | mean, median and rank side by side with the variance ratio printed | the estimator choice is visible, not silent |

### ⭐ the permutation null is valid this time, and the difference is stated

Ledger 1125 and 1129 record two rounds that built an arm-side permutation null which was **void by
derivation** — a paired mean is invariant under it. **Here the permutation is over the GROUP LABEL**:
it destroys the grouping while preserving both marginals, and the world it excludes — *"any
110-subset of the ranked corpus looks like this"* — is **built synthetically as the g=0 control**
rather than asserted. The two bands agree to within 0.02, which is the check that the permutation and
the synthetic subset are measuring the same null.

## MULTIPLICITY

**3 primary cells** (3 axes × 1 rank estimator), **0 surviving**. The mean and median columns are
descriptive and are not tested — reporting them as tests would be three more cells. Non-survivors are
all three, printed above.

## WHAT DIED

- **R783's NEXT** — an 18-vs-968 comparison, killed on arithmetic before it was written: MDE 0.6665 SD.
- **this round's own headline** — the 2.4× flag difference, killed by the estimator its own
  preregistration fixed.
- **the claim that this arc's population is "the ranked corpus"** — it is 89.80% of it.

## WHAT SURVIVES

The population fact itself, which is exact and needs no statistics: **968 of 1078**, with the drop
occurring upstream of every filter this repository contains.

## SCOPE

population 1078 ranked prompts, 968 rubricked, 110 excluded, 986 released conversations · instrument
parsed rankings and `unacceptable` ratings from `comparisons.jsonl` · baseline the scored 968 ·
regime first release, this tree_sha.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| the bias on any clause-② verdict | rubrics for the 110. **No rubric means no rubric-derived arm has criteria there, so nothing can be scored** — checked against R468 before writing: there is no criterion text to join on, so unlike R783's false wall there is no key to recover |
| resolving the exclusion below ~0.28 SD | n = 246 for 0.20 SD, 545 for 0.15, 4,149 for 0.10 — and 110 is the whole excluded set |
| why those 110 lack a rubric | the rubric generator's inputs, off-repository (R605) |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The exclusion is upstream of everything this repository does, so the next question is not about the
110 but about what the arc's claims would have to say about themselves. As computed by this round's
`run.py`, the coverage is 89.80%, and a scope line reading "968 prompts" states a sample as though it
were the corpus; the honest form is "968 of 1078 ranked, the remaining decile unrubricked and its
character unresolvable below 0.28 SD". The step is mechanical rather than
experimental: a gate that fails a push when a scope line names a population size without naming the
frame it was drawn from — the same shape as `next_line_quantifiers_are_computed.py`, which catches an
unsourced count, applied to an unsourced denominator.
