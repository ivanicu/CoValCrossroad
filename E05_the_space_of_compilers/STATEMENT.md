# A core — what stands

*One page. Every number here traces to a round whose verdict is not UNVERIFIED; the check is
mechanical (`assurance/statement_provenance.py`) and it fails if a citation is added that does not.
The reasoning, the corrections and the 289 retractions live in `DEFINITION.md` and `RETRACTIONS.md`.
This page is the residue.*

---

## The definition

A **core** for a conversation is a set of criteria such that

- **①** it scores better than a random draw of that conversation's own rubric;
- **②** it scores better than the best **generalising** prompt-blind criterion set;
- **③** it was not built by reading the conversation's human labels;
- **④** it scores better than every rule computable from the responses alone.

Size: **more than one criterion**. The design cannot separate 3 from 8, so no number is named. *(R441)*

---

## What each clause is worth

| clause | type | excludes | status |
|---|---|---|---|
| **①** | behavioural | **0 of 41** arms | **UNEXERCISED, not vacuous** — an adversarially worst rubric subset *is* excluded, at **−0.2779** [−0.2914, −0.2651] *(R464)* |
| **②** | behavioural | **33 of 42** | carries the whole boundary among label-free arms |
| **③** | **provenance** | **14 of 42** | **cannot be checked on an object alone** *(R465)* |
| **④** | behavioural | **all 7** arms on the second release | not vacuous |

⭐ **①②④ can be checked by anyone handed a criterion set. ③ cannot** — it is a claim about how the set
was built, and two behaviourally identical sets can differ under it: a label-reading selector and a
label-free one emit the same criteria on **9 of 967** prompts, with identical A2 to machine
precision. *(R465)*

---

## The extension

**0**, under every reading. *(R475)*

Of the **5** arms admitted by ①∧②∧④, four are excluded by ③ as target-readers. The fifth,
`coval_core`, was carried as **UNKNOWN** until the release's own dataset card was read: it is selected
on *"the highest average ratings"*, i.e. it is a **w-reader**, and ③ excludes it too. *(R475)*

⛔ **The definition has no members — and the object it was written from is excluded by its own clause
③.** Either ③ must be weakened to forbid only the prompt's *rankings*, or this is a definition of some
object other than CoVal-core. **R475 does not decide which**, and the two differ in what "core" means.

---

## What is established about clause ②

- The released core beats the **best generalising** prompt-blind set by **+0.0095 to +0.0191** — a
  **bound**, sign-stable across every annotator count, resolved at 6 of 7 and not at m=16. *(R455, R456)*
- More annotators do not fix it: **α = 0.208**, so the MDE falls **1.19×** from 3 draws to all 16.
  The residual variance is **between prompts**, not annotator noise. *(R456)*
- That between-prompt variation is **real**: the value of having the right criteria on a given prompt
  replicates at **0.8419–0.8544** across the whole 1,820-comparator census. *(R457, R460)*
- And it is **unexplained**: 17 target-free features explain **4.4%** of it, against a planted-signal
  recovery of **0.9170**. *(R458)*
- Reliability is a joint property of the arm **and its comparator**: `corr(ρ, comparator strength)
  = −0.7995`. *(R460)*

---

## What is established about the arm space

- Admission is governed by **how much of the released core survives**: variance explained **98.6%**
  by criteria retained, **1.0%** by generic criteria added. Dropping one of four still clears **92%**
  of the size-matched class. *(R450)*
- **Nothing disjoint from the released core has ever been admitted** — the only content-driven
  disjoint object scores **0.0038**, while an oracle over the same space clears **1.0000**. The space
  contains admissible disjoint objects; no generator we have finds one. *(R451)*
- That oracle is **not** per-conversation selection: **57.8** effective winners of 1,820 against
  **185.7** under no-structure combinatorics, one subset taking **33.57%** of prompts. *(R452)*

---

## Instruments that outlive the questions

- **`definition_matches_the_record.py`** — every locatable claim in `DEFINITION.md` re-derived from a
  committed artifact. **298 anchors.** It has caught an anchor named for one quantity and pointed at
  another, a pattern matching a different round's sentence, a dropped sign, and a self-referential
  count going stale.
- **`comparator_scope.py`** — every difference-based claim must **declare** what it was measured
  against. **71 declared**, 0 flagged at any defensible window, across three independent blocks.
- **`clause3_as_written.py`** — ③ derived from `select_core.py` rather than hand-listed, returning
  three values and never folding UNKNOWN into ADMITTED.
- **`id_map.json`** — the two id spaces joined exactly: **968 of 968**, uniqueness 1.0000, validated
  on a channel it was not built from (**0.8811** vs **0.2859**). *(R468)*

---

## What this campaign has not done

- **No second release, no third judge, no second prompt-blind family with breadth.** Each is named in
  the impossibility register with what it would require.
- **③ is not decidable here.** Containment is *constant* on ③'s own partition — **0.9744** excluded
  against **0.9767** admitted — so it cannot implement ③, and no other instrument on this site does.
  *(R469)*
- **The definition's extension has never been measured.** It has been counted under a convention.
