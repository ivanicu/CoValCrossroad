# The definition, stated once

`FORMULATION.md` is 2,000+ lines and is the **evidence record** — every clause that was written,
attacked and corrected, in the order it happened. It is titled *"stated once"* and it opens with a
correction, because the statement itself was never separated from its history.

**This file is the statement.** Every number in it is checked against a committed artifact on every
run by [`assurance/definition_matches_the_record.py`](../assurance/definition_matches_the_record.py),
so it cannot drift from the evidence without the suite failing.

---

## The definition

> A **core** for a conversation is a small set of evaluation criteria, **producible from the
> conversation alone**, that
>
> **③** uses **no information from that prompt's own human labels** — not from the construction, and
> not from any half of them; **and**
>
> **②** scores better, **under a named judge J**, than a size-matched criterion set that never read
> the conversation.
>
> Its size is **greater than one**; sizes **3 to 8 are not distinguishable** by this release.

**Clause ① is not a clause.** It is a consequence — see below.

---

## What each clause is measured to do

| clause | excludes | status | scope |
|---|---:|---|---|
| **①** better than a random draw of the prompt's own rubric | **0 of 41** | **DERIVED** — the region where ① could bind is empty by arithmetic (`GAP ≥ SLACK` on every arm) | R347 |
| **②** better than a prompt-blind set | **33 of 42** | **MEASURED** — carries the whole boundary among label-free arms | R360 |
| **③** no prompt labels | **4 of 42** | **DERIVED** that it excludes the label-users; **MEASURED** that nothing else can | R360 |

### ① — a consequence, not a test

On this arm space clause ② **implies** clause ①. The cell *(① fails, ② passes)* is **empty**, and
empty **by derivation**: a counterexample needs `GAP < SLACK`, and the measured minimum GAP exceeds
the maximum SLACK on all 41 arms. It could not have come out otherwise.

**Do not delete it** — the implication rests on a *measured* reference gap, not on the definition's
own logic, so a release with a weaker blind reference restores its bite. **State it as a consequence
and stop presenting it as independent evidence.**

### ② — real, and it must carry a judge index

It excludes the most, and every one of the following is measured:

- It tests a **curated instrument, not blindness.** Crowd-written sets that never read the
  conversation do *no better* than clause ①'s own reference, and 2 of 5 are resolvably worse. *(R348)*
- The reference is `POOL[0:k]` — chosen by **file order** — sitting at the **93.7th percentile** of
  all 1,820 size-4 subsets, where it admits **3 members of the class the clause defines itself
  against**. *(R331)*
- The admitted set is **not stable**: two distinct sets inside **0.25 of one MDE**. *(R332)*
- The "closure level" is the **first** closed reference, not the lowest safe one — at 6 of 9 k,
  **stronger** references admit blind sets again. This replicates at a second judge, so it is a
  property of the **estimator**, not of one model. *(R355, R358)*
- **It is emptied by a change of judge**: **5** arms admitted at Qwen3.5-2B-Base, **0** at
  Qwen3.5-0.8B-Base, on all 41 arms. *(R301)*
- **Self-normalising does not repair that.** At matched strictness the relative and absolute forms
  are indistinguishable — 9 vs 9 at 2B, 0 vs 0 at 0.8B. The judge-dependence is in the **arms'
  ordering**, which no reference can reorder. *(R359, R356, R357)*

**Therefore clause ② is stated with a judge index and the claim it licenses is *"a core under J"*,
never *"a core"*.**

### ③ — the one unsubstitutable clause

That clause ③ excludes the four label-using arms is **forced** — it *is* "no prompt labels". The
measured part is that **nothing else can do its job**:

> Across all **45** reference levels the label-user count **never falls below 4**, while the
> published five fall to **0** at the strongest reference. At p=100 the only arms still admitted are
> the four that read the prompt's labels. *(R360)*

**Strengthening clause ② removes the arms the definition exists to admit and leaves exactly the arms
it exists to exclude.**

And its wording is load-bearing: it must say **held out from the PROMPT**, not "from the
construction". Three fitted arms pass the weaker reading, and in the quintile where two annotator
halves disagree **their entire advantage is gone**. *(R295)*

---

## The size

**Not four.** The release ships exactly one core, of size four, and "four criteria" was a
description of that instance rather than a property of the category — the k-sweep cannot separate 3
from 8. The largest identifiable *member* core is **k ≤ 2**; the class is identifiable where the
member is not. *(R224, R228, R230)*

**State the bound the design supports: more than one, and 3–8 indistinguishable.**

---

## What this definition cannot claim

| | |
|---|---|
| **"a core", unindexed** | the admitted set is **empty at the second judge**; only *"a core under J"* is licensed |
| **a count of admitted arms** | the set moves within **0.25 MDE** (R332) and with the reference's percentile (R354) |
| **that its three clauses each test something** | one excludes nothing, one is judge-emptied, one is irreplaceable |
| **transfer to another criterion pool** | every level here is a fact about **this 16-criterion pool** (R331) |
| **transfer to another release** | one release |

---

## The one sentence

> **What survives every attack in this campaign is clause ③.** Clause ① is a consequence, clause ②
> holds only under a named judge, and the size is a bound rather than a number — but *a core may not
> be built from the labels of the prompt it is for*, and no strengthening of any other clause can
> substitute for saying so.
