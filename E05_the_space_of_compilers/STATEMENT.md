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
③.** *(R475)*

⛔⛔ **AND THE EMPTINESS IS A CONFLICT, NOT AN ABSENCE.** Every arm that clears the cross-fitted
prompt-blind ceiling (**0.5404**) is one ③ excludes — five of five, reaching it by reading the prompt's
rankings or ratings. The best ③-admissible **prompt-aware** arm is **0.5337**, a gap of **−0.0067**,
inside the **0.0122** floor. **② asks an arm to beat a class that already performs at the level
prompt-awareness alone can reach, and only the human labels ③ forbids go further.** *(R485)*
> ⚠ **DOWNGRADED to UNDETERMINED (R486, R487).** The observation stands — five of five arms clearing
> the ceiling are ③-excluded. The *interpretation* does not. Placing the best ③-admissible
> prompt-aware arm inside the class it must beat puts it at **percentile 32.6**, and over the **full**
> population — **23 scorable arms**, not the three R485 named — **22 of the other 22 sit at p0.0**,
> below every one of the 1,820 prompt-blind subsets. **A clause-level conflict requires the admissible
> side to be fairly represented, and a population whose maximum is p32.6 is not.** So this site cannot
> separate *"③ forbids the winning mechanism"* from *"nobody has built a good rating-blind
> prompt-aware arm here"*. Settling it needs a **strong** admissible arm, which is a
> generation-and-judging round. *(R486, R487)*

⭐ **AND THE SEARCH FOR THAT ARM IS VALIDATED RATHER THAN OPEN-ENDED.** The per-prompt deficit
`coval_core − gen` is a **reliable** quantity: mean **+0.0311**, true sd **0.1342** against a measured
noise floor of **0.0353** (**3.8×**), test-retest **r = +0.9355**. **`gen` wins on some prompts and
loses badly on others, reproducibly** — its spread is 4.3× its mean. Four candidate explanations are
excluded, each by a control that could have confirmed it: **repetition**, **discriminativeness across
arms**, **discriminativeness paired at n=968** (+0.0013, CI [−0.0640, +0.0608], control firing at
+0.2577), and **criterion length** (+0.0319, CI spanning zero). **The target is real; the predictors
were wrong.** *(R494, R495, R496, R497)*

⭐ **③ STAYS AS WRITTEN, and the reason is measured rather than stipulated.** R475 left the choice of
weakening ③ to permit the ratings. What decides it is what the ratings are **worth**: against the best
③-admissible arm on disk (`generic`, a fixed prompt-blind set at **0.5376**), `topw_k4` gains
**+0.0099** [+0.0009, +0.0189] against a **measured** floor of **0.0122** — `effect/floor` **0.81**,
**no count admissible, direction only**. **③ forbids nothing a good rating-blind selector cannot
match, so keeping it costs nothing.** *(R477)*

⚠ **Scope.** Established on the 2B judge, whose admissible class holds 9 arms. The 0.8B judge has no
`_08b` build of five of them, so "the best admissible" is unbounded there: **UNVERIFIED, which is
neither agreement nor disagreement.** *(R477)*

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

## What the score is actually made of

⛔ **The 0.54 band every arm converges to is the JUDGE, not the target.** The maximum any scorer
*without sight of the target* can reach — the modal human ranking scored against a **held-out**
annotator — is **0.6132** (resolution 0.0093, four seeds). Against the best non-oracle arm that leaves
**+0.0467 of headroom, 3.8× the floor.** **The band is not a ceiling.** *(R479)*

⛔⛔ **And the same criteria attain 0.738 of that ceiling under Qwen3.5-2B and 0.193 under 0.8B** — a
gap of **0.545**. `random_k4_s0` attains **−0.106** at 0.8B, below chance. ② already says a core is
only ever *"a core under J"*; **this says the judge index is not a caveat but the dominant term.**
*(R479)*

⭐ **Leave-one-out is worth +0.0388.** Including the held-out annotator in the mode that scores
against it gives 0.6520 instead of 0.6132 — an error running in exactly the direction that
manufactures headroom. And a free control: single-annotator-vs-annotator returns **0.5458** against
this campaign's independently committed human ceiling of **0.5451**, Δ **+0.0007**. *(R479)*

⚠ **The judge preserves which FAMILY is better and reverses which SIZE is better.** On pairs resolved
under 2B, sign survival is **0.8019** against a split-half **same-judge** placebo of **0.9848** —
across-family **0.9130**, within-family **0.3692**. Below chance is reversal, not disagreement.
**A size claim is judge-relative in a way a family claim is not.** *(R480)*

⚠ **And that reversal must name its aggregator.** Every A2 here **sums** satisfaction over the
selected criteria (`corebench/score.py:63`), a choice never swept until R481. `cls(mean) ≡ cls(sum)`
by algebra. The reversal holds under `sum` and `median`, is absent under `min`, and **`max` and
`midrange` cannot resolve k at all** (range 0.0084 / 0.0086, below the floor) — so their nulls are
silence. **2 of the 3 aggregators that can see k, not 2 of 5.** *(R481)*

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

- **No third judge, and no second prompt-blind family with breadth.** Each is named in the
  impossibility register with what it would require.
  > ⚠ **CORRECTED (R489):** this line read *"no second release"*. **There is one** — 2,200
  > conversations in `data/utterances.jsonl`, used by R434, R436, R437 and R438, with 74,048 judged
  > cells in the `transport_*` arms. What it lacks is the **rank-string schema** the home release
  > carries, which is what the register's *"with this schema"* qualifier always meant. **A stale
  > register line understates a site, and understating is not the safe direction: it forecloses work.**
- **③ is not decidable BY ANY INSTRUMENT here.** Containment is *constant* on ③'s own partition —
  **0.9744** excluded against **0.9767** admitted — so it cannot implement ③. *(R469)*
  > ⚠ **AND THAT DOES NOT MAKE ③ UNDECIDABLE (R475).** ③ is a **provenance** predicate, and provenance
  > is established by a **record**, not a measurement. `data/DATASET_CARD.md` states the released core
  > is selected on *"the highest average ratings"* — a w-reader — so ③ **excludes** it. R469 measured
  > correctly and then quantified over the wrong domain.
- **What would settle ②∧③ is a judge stronger than Qwen3.5-2B.** *(R490)*
  > ⛔ **CORRECTED (R491): this line read *"and this site has none"*. It has one.**
  > `/home/ivan/Qwen2.5-7B-Instruct` — **complete, 4/4 shards, 29 GB**. ⚠ It is a different **family**
  > and an **instruct** model against this campaign's Qwen3.5 **Base** judges, so it tests
  > **cross-architecture**, not scale; and 29 GB against 16 GB of VRAM needs quantisation or offload.
  > **Not free, and not absent.** ⚠ **AND MEASURED SINCE (R492): it does not RUN in bf16 on this
> card.** Weights load at **15,744 MiB of 16,303**, leaving 559; batch 16 OOMs at 52 MiB and
> batch 2 at 16 MiB, so the deficit tracks batch and bf16 is out. **Quantisation is required —
> and it makes the 7B a different instrument from the bf16 judges every committed number uses,
> confounding SIZE, FAMILY and PRECISION at once.** The register entry is therefore *present,
> not runnable at this precision*, which is neither *absent* nor *available*.
> ⛔ **AND WHAT IT WOULD ACTUALLY REQUIRE, priced (R493):** `bitsandbytes` is **ABSENT**, as is
> every other quantisation path (`optimum`, `auto_gptq`, `awq`). So the route is: install a
> **compiled CUDA package** against **CUDA capability 12.0 (Blackwell) + torch 2.11.0+cu128**,
> **into the shared `.venv` that every committed number's harness runs on**; add a quantisation
> knob to `covalx.judge.Judge`; and **re-judge the 2B quantised** so the comparison is not
> three-axis. ⭐ **This is not a download — it is an environment change whose blast radius is
> the instrument behind every committed result**, which is precisely the kind of cost §2 asks a
> register to state instead of the word *planned*.
> ⛔ **Third wall this session that was false when checked** — after
  > R475 (the dataset card) and R489 (the second release). All three were claims about the SITE
  > asserted right after correctly checking the RECORD.
  Not a second judge: the 0.8B is **weaker** — `oracle_k4`, which reads the human target directly,
  attains **0.105** of the Bayes ceiling under it against **1.088** under 2B. Scoring a new arm there
  measures that judge. ⭐ And not a new generator either: `corebench/generate_core.py` already builds
  rating-blind, rubric-blind, prompt-aware cores — **`gen` is its output**, and it is the best
  ③-admissible arm on the site at **percentile 32.6** of the prompt-blind class.
- **The definition's extension has never been measured.** It has been counted under a convention.
