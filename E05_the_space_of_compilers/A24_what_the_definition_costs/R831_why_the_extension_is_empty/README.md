# R831 · why is the definition's extension empty?

**The decision this made safe:** whether the empty extension is a fact about the **release** (too few
candidates) or about the **definition** (it asks for something that cannot exist here). **The
definition.** ③ forbids exactly the information that the A2 ordering is monotone in.

Design in `PREREGISTRATION.txt`, committed before `run.py` existed. `run.py` committed before it ran.

## The correction that came first

My previous NEXT asked whether **④** can be restated so R826's saturation does not make it vacuous.
⛔ **R475 had already settled ③ against the released core** from the release's own dataset card —
*"select up to four rubric items with the highest average ratings"* is `topw_k`, which is in
`W_READERS` — and `DEFINITION.md:503` records *"the extension is 0 under EVERY reading"*. **No
restatement of ④ rescues a conjunction ③ has already emptied.** The gradient I named was flat.

What is recorded is **that** the extension is 0. What is not — measured by anchored search with a
positive control — is **why**: 0 occurrences of *anti-correlated · self-contradictory · mutually
exclusive · why the extension is empty* anywhere in the deliverable.

## Result

| | |
|---|---|
| population | **93** arms with both a committed A2 and a satisfaction file |
| ③ partition | **39 EXCLUDED · 43 ADMITTED · 11 UNKNOWN** |
| mean rank, ③-admitted − ③-excluded | **+27.25** on a 93-arm scale (positive = admitted rank worse) |
| permutation p over the 82 labelled arms | **0.00005** |
| positive controls (independent · bottom-half) · g=0 (partition twice) | p=0.6629 · p=0.00005 · identical |
| two-seed | byte-identical |

**The top 8 arms are all ③-EXCLUDED**, every one a label-reader:

```
rank 1-3  0.6353  EXCLUDED  oracle_k4, oracle_k4_oracle_kA/kB
rank 4-5  0.6292  EXCLUDED  greedy_k4_greedy_kA/kB
rank 6-8  0.6079+ EXCLUDED  oracle_k4_fit1, greedy_k4_fit1, indep_k4_indep_kA
```

**W-SELF-DEFEATING.** A2 performance on this site is monotone in how much human-label information an
arm consumed, and ③ forbids exactly that information. **The definition asks for a set that beats
label-readers without reading labels.**

## ⚠ The confound control, which decides how far this reads

Pre-registered, with its classifier fixed in source before any rank was computed. The ③-admitted set
is dominated by random baselines — arms *I* chose to build — so a rank shift over all of them is a
selection fact about my inventory. **Substantive ③-admitted arms: 3.**

| arm | A2 | rank |
|---|---|---|
| `topvar_k4` | 0.4873 | **50 / 93** |
| `topvar_k4_08b` | 0.4236 | 72 / 93 |
| `topvar_k4_08bR` | 0.4018 | **93 / 93** |

> ⭐ **SUPERSEDED BY R834 — the set is 6 arms across 4 families, not 3 in 1.** Reading the eleven
> UNKNOWN arms' construction records adjudicated `generic` (**21**), `gen` (27) and `promptecho`
> (66) as ③-admissible, each on a verbatim quote committed as data. **`gen`'s is measured, not
> asserted**: I2 verbatim 0.0000, I3 novel 0.9920 against `coval_full`.
> **Best substantive rank moves 50 → 21, and the top 8 stay 8/8 label-readers**, so
> W-SELF-DEFEATING is strengthened rather than moved. The `BASELINE` regex and rank source are
> unchanged, so the two numbers are comparable.
> ⚠ **And this round's NEXT — *"build a second family"* — was answered by arms already on disk.**

**n = 3.** The permutation p is computed over 82 arms, most of them baselines. **The substantive
claim is a description of three arms, not a tested effect** — the best **③-ADMITTED** substantive arm
sits at rank 50 of 93, and no p is available at that n.

> ⛔ **CORRECTED BY R832, and the original sentence is the reason.** It read *"the best **label-free**
> substantive arm this site contains sits at rank 50"*. **The instrument's unit is `③-ADMITTED`; the
> sentence's unit is `label-free`, and they are not equal.** ③ returns **11 UNKNOWN** here, and
> UNKNOWN does not mean *reads labels* — it means `selector_of` found no known selector prefix in
> the arm's name. Those 11 include `generic` (rank 21) and `gen` (rank 27).
> **So the claim is an INTERVAL, not a point:**
> **[11, 50]** as pre-registered (lower end = unknown-as-ADMITTED), and **[21, 50]** once `coval_core`
> is removed at the lower end because **R475 settled it as a label-reader by RECORD** — that
> refinement is **post-hoc** and labelled as such.
> ⭐ **W-SELF-DEFEATING survives both ends**: the **top 8 are ③-EXCLUDED under BOTH readings**
> (top-16: 16/16 strict, 13/16 lenient). Only the rank *number* moves; the direction does not.
> §4's *instrument's unit vs claim's unit*, for the third time in this session.

## The 11 arms ③ cannot classify

`coval_core` is **rank 11** and UNKNOWN to ③'s instrument — but R475 settled it by **record**, not by
measurement: the dataset card says it selects by highest average ratings. **So the released core is a
label-reader sitting among label-readers, and ③ excludes it for the same reason it excludes the top
8.** `gen`, the conversation-only arm, is rank 27 and also UNKNOWN.

## NEXT

The definition's two halves pull against each other on this site, and that is now stated rather than
implied. What is **not** established is whether the anti-correlation is a property of A2 as a target
or of this release's arm inventory. The artifact's `substantive_admitted` field lists the subset:
`topvar_k4`, `topvar_k4_08b`, `topvar_k4_08bR` — three arms of one family. A second family of
label-free substantive arms would move this from a description to a measurement.
