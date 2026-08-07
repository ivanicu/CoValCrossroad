# R601 · The claim table cites zero of the 18 cross-release rounds

**Decision this makes safe:** the scope of every claim row. **All ten are home-release-only, and the
page now says so.**

**WORLD B UNCARRIED.** 18 rounds score on the second release. **The claim table cites 0.**

| the strongest uncarried members | their own README headings |
|---|---|
| **R433** | *clause ②'s **subject** on a second release — **`W-LOSES`*** |
| **R403** | *half the definition is a fact about CoVal's schema* |
| R427 | the first number on the second corpus |
| R398 | *"one release" was never a wall — it was a query nobody ran* |

R433, verbatim: *"whether clause ② is a property of **cores** or a description of **what CoVal did**.
**It is a description.**"* A core generated from the conversation alone — **the clause's own
subject** — **loses to a judge-free length heuristic by −0.0545, resolved.** `STATEMENT.md` cited
R433 exactly once, in the impossibility register, as **file provenance that a second release
exists.**

## ⚠ And the counter-reading is also absent, which is why the verdict is scoped rather than damning
**R399**: the second corpus is a **rating** corpus whose overlap with the home release is **3
strings, 2 of them greetings.** **R400**: the two share depth *support* and almost no depth *mass*.
**If those hold, ②-losing-there may be no evidence about cores at all.**

⭐ **So the page is silent about the cross-release results AND about the reason they might not
count.** Whether the silence is an omission or a correct exclusion is **`UNVERIFIED`**. **What is
established either way: every claim row is home-release-only and did not say so.** Now annotated in
the scope-constants table, where it belongs — one home, not one caveat per row.

## ⛔ Two controls failed first, and both defects were mine
| control | v1 | cause |
|---|---|---|
| **negative** — a home-only round must not be classed cross-release | ⛔ **R519 matched** | the recogniser included the bare word **`transport`**, colliding with the helper `judge_transport` and with the ordinary English word. **109 of 376 rounds** were classed cross-release |
| **placebo** — a nonexistent corpus token must match nothing | ⛔ **1 round matched** | **that round was R601 itself.** The instrument scanned a population containing its own source, so any literal it searches for is guaranteed present |

⭐⭐⭐ **The placebo failure is the sharper lesson: a round that measures a corpus it belongs to will
find whatever it looks for.** Same class as R598's harness reading a tree it was mutating. Fixed by
assembling the token at runtime **and** removing the round from its own population — *a round may not
be a member of the population it measures.*

**After tightening to what can only mean the second corpus** (its data file, its loader, its explicit
flag): **109 → 18**, negative and placebo both PASS.

## Controls, final
| control | returned |
|---|---|
| **positive** — claim-table block found and cites its known members (R519/R529/R527) | **2,390 chars, 17 rounds** — PASS |
| **g=0** — empty block | **0 citations** — PASS, it can fail |
| **positive** — cross-release recogniser finds known members R398/R427/R433 | **18 rounds, all three present** — PASS |
| **negative** — home-only R519 | **not classed** — PASS |
| **placebo** — nonexistent corpus token | **0** — PASS |
| **KILL threshold**, pre-registered | class size **18 ≥ 2** — an absence claim is admissible |

**MULTIPLICITY:** 2 recognisers × 376 rounds + 5 control checks. **18 cross-release · 0 carried · 18 not.**

**IMPOSSIBLE, named:** *"this round bears on clause ②"* lives in the round's prose, not its file
list. **Every member's heading is printed so a reader can overrule the classification.**

## ⛔ Check #200, recorded not pursued
R600 closed by calling **R288 a census round** — verified for R294, **inferred** for R288 from a
mention inside R558; two hypotheses collapsed on one round's evidence. And its *"if that class is
large… if it is small"* was **a decision rule with no threshold** — a pre-registration without a
number is a sentence, not a commitment. **This round's kill carries the number R600's lacked.**

## The sentence I can no longer write
> *"the definition is `② ∧ ③`."*

It is `② ∧ ③` **on the home release**, and eighteen rounds scored the second one without reaching
the claim table — one of them concluding, in its own words, that ② **is a description.**

## NEXT
The counter-reading rests on **R399** and **R400**, which are themselves uncited and unaudited: the
overlap figure of *3 strings, 2 of them greetings* decides whether R433 is evidence about cores or
about a different object entirely. **Re-derive that overlap from the two data files directly** —
it is the single number on which the whole cross-release question turns, and it currently rests on
one round nobody has attacked.
