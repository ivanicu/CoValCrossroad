# R688 · does ③ exclude published cores? — **the falsifier does not fire**

**⭐⭐⭐ CoVal published five arms; ③'s extension contains two of them. The other three —
`topabs_k4`, `topvar_k4`, `topwvar_k4` — **all fail clause ② anyway**. So ③ adds no exclusion the
behaviour had not already made, and §4's falsifier for a definition **does not fire against ③**.**

> **⚠ PREMISE CORRECTED BY R689 (D8).** *"CoVal's published five"* is **R442's hard-coded literal**, not the release. `data/DATASET_CARD.md` names **`coval_core` only**; the other four are our own `corebench` constructions. **The verdict below SURVIVES and strengthens** — the one core the release publishes is *in* ③'s extension — but the population it was run on was one released object and four we built. R688's impossibility line ("needs the release's own text") was a **wall never checked**: the card was on disk throughout.

## THE TEST §4 SPECIFIES FOR A DEFINITION
> *"Name an admissible object this clause EXCLUDES. If the excluded object is one your own benchmark
> ACCEPTS, the clause is false."*

| | |
|---|---|
| CoVal's published five | `coval_core topabs_k4 topvar_k4 topw_k4 topwvar_k4` |
| ③'s extension | `coval_core topw_k3 topw_k4 topw_k6 topw_k8` |
| ⭐ overlap | **`coval_core topw_k4`** |
| ⛔ published but ③-excluded | `topabs_k4 topvar_k4 topwvar_k4` |
| **excluded by ③ ALONE** | **0 of 3** — every one already fails ② |

**Controls:** POSITIVE — `coval_core` passes ② → true. **g=0** — 33 arms are known to fail ② → *the
reader returns both values*. NEGATIVE — an absent arm → UNKNOWN, never false. PLACEBO — identical.

## ⛔ I PREDICTED ③ WOULD LOOK FALSE, AND BOTH ROWS SAY OTHERWISE
Registered **A = 2 of 3** passing ② → observed **0**, error **−2**. Registered **directional: ≥1
passes ②** → **FAILS.** **My prior was that the definition over-excludes**, and the measurement says
② does the work while ③ adds nothing wrong on this population. **This is a survival, not a
retraction — and it is the first in this arc.**

## ⚠ THE UNIT GAP IS ③'s ACTUAL DEFENCE, AND IT CUTS BOTH WAYS
*"Published as an arm"* is **not** *"accepted as a core"*. CoVal publishes comparison arms it does
not call cores, and this corpus records the **list**, not the intent. So the test just run is the
strongest version available here, and a stronger one needs the release's own text — which is named in
the impossibility register rather than promised.

## ⭐ THE DRIFT AUDIT RAN *BEFORE* THE ROUND WAS CHOSEN, FOR THE FIRST TIME
R687's NEXT proposed a fifth consecutive corpus round. The audit over R672–R687: **4 object headlines
of 16, and the last SIX all corpus.** R676 caught this drift once, R664 before it. **Third
occurrence, so the interrupt is now a step taken before choosing the round, not a diagnosis made
after noticing.**

## ⛔ AND I REGISTERED AN UNFAILABLE INTERVAL AGAIN, ONE ROUND AFTER WRITING LEDGER 803
`A [0, 3]` on a population of 3. I **named it as unfailable in the pre-registration itself** and
registered it anyway. Naming a defect while committing it is better than not naming it — **and it is
still committing it.** The **point error** and the **directional** are what carry information here.

## WHAT NOW STANDS ABOUT THE DEFINITION
- ③'s extension shares **two** members with the published five, not five *(R442, R688)*
- the three it does not share are excluded by **② already**, not by ③ *(R360, R688)*
- so **§4's falsifier does not fire against ③** on the population this corpus can reach

## NEXT
③ excludes four of ②'s nine passers — `greedy_k4_fit1 indep_k4_fit1 oracle_k4 oracle_k4_fit1`
(R519's `admitted`, and R683 showed these rank *above* the extension at the 2B judge). Those four are
the population where the falsifier could still fire, because they pass ② and ③ alone removes them.
Check whether any of the four appears in CoVal's release under a name suggesting acceptance rather
than comparison, by reading the release's arm manifest rather than this corpus's record of it.
