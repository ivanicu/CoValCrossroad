# A core — what stands

*One page. Every number here traces to a round whose verdict is not UNVERIFIED; the check is
mechanical (`assurance/statement_provenance.py`) and it fails if a citation is added that does not.
The reasoning and the corrections live in `DEFINITION.md` and `RETRACTIONS.md`; the retraction
count has one home and is not restated here.
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

## The formulation is a fork, not a fact awaiting measurement

**Everything below is settled enough to state the choice.** ① excludes an adversarially worst rubric
subset but no arm anyone built *(R464)*. ② is **satisfied by `coval_core`**, the one object anyone
calls a core — 0.5640 in A2 against the 0.5404 prompt-blind ceiling *(R475, R485)*. ④ excludes all
seven arms on the second release. **③ is what empties the definition**, and the ③-admissible side
holds exactly **one** prompt-responsive full-coverage arm *(R502)*.

⭐⭐⭐ **So "core" is not one definition with an unresolved parameter. It is two definitions, and the
record prices both.**

| | **A · core as an OBJECT-property** (drop ③) | **B · core as a PROCESS-property** (keep ③) |
|---|---|---|
| what it is a predicate on | a criterion set | a **(set, construction history)** pair |
| extension here | **5** arms (①∧②∧④) | **0** |
| what must be shipped for a third party to check it | **the criterion set** | **the criterion set AND its producer** — the generating code or a provenance declaration |
| what it admits that you may not want | arms that **read the human labels** — but their criteria are **100% verbatim items from the prompt's own rubric** *(R503)*: the **right** criteria, selected for the wrong reason. The cost of A is **provenance, not quality** | nothing; it admits nothing here |
| why the extension is what it is | the label-readers are the only arms clearing the ceiling *(R485)* | the site ships **one** admissible prompt-responsive generator *(R502)* |

⭐ **Reading B's emptiness is a fact about the RELEASE, not about the definition.** That is the whole
content of R502: `UNDETERMINED` was never "the definition cannot be settled", it was "there is one
candidate and a floor." **A second site with more ③-admissible prompt-responsive generators would
settle ②∧③ without changing a word of the definition.**

⚠⚠ **AND THE FORK ITSELF IS CONTINGENT ON AN OPEN EMPIRICAL QUESTION — it is not philosophy.** A and
B differ *only because ③ has no known behavioural surrogate*. If label-reading left a checkable
trace, B would become object-level and the fork would dissolve. **That question is `UNVERIFIED`, not
closed**: the one instrument tried (per-prompt A2 dispersion residualised on mean A2) failed its own
positive control — it could not place `oracle_k4`, the maximal label-reader, outside the middle of
the pack *(R501)*. **A candidate instrument must first be shown to rank `oracle_k4` at an extreme.**

⭐⭐⭐ **AND THE REASON NO SUCH INSTRUMENT HAS BEEN FOUND IS NOW MEASURED, NOT GUESSED.** Every
③-**excluded** arm draws **100.0%** of its criteria verbatim from the prompt's own rubric — and so do
the ③-**admissible** `random_k*` arms, while `gen` and `generic` draw **0.0%**. **The two sides of ③
inhabit the same object space and differ only in the selection map.** There is no textual property to
check because there is no textual difference to find. *(R503)*

⭐⭐⭐ **AND B'S COST IS NOT "UNVERIFIABLE" — IT IS "VERIFIABLE FROM A DIFFERENT ARTIFACT".** This is
a **derivation** from two measured facts, labelled as one: the ③ verdict for every arm here is
**derived from the generating source** *(R444)*, and the release **declares its own core's provenance
in its dataset card** — *"select up to four rubric items with the highest average ratings"* *(R475)*.
So ③ is checked the way every provenance standard is checked — by **attestation and inspection of the
producer**, never by looking harder at the product. **The earlier framing, "no third party can ever
verify a core", overstated it: what is impossible is verifying from the criterion set ALONE, which is
a statement about what must accompany the object, not about whether the property can be known.**

**What the choice costs, in one line each.** Choose **A** and a criterion set that read the answer key
counts as a core — though R503 shows those are **verbatim human rubric items**, so the cost is
provenance, not quality. Choose **B** and a core is only ever as trustworthy as the **producer** you
are shown alongside it.

### ⛔ The recommendation is WITHDRAWN — it compared two numbers from two instruments

**Retracted, one round after it was written.** The campaign recommended reading **B** because
`oracle_k4` (**0.6282**) exceeded the Bayes ceiling for any predictor (**0.6132**) — an object above
the prediction bound is not predicting. **Recomputed in one process, on one population of 968
prompts, with one hold-out convention and three seeds:**

| quantity | recomputed | as quoted |
|---|---|---|
| held-out ceiling | **0.6466** | 0.6132 |
| `oracle_k4` | **0.6325** | 0.6282 |

**Gap −0.0141 against a measured floor of 0.0220 — `oracle_k4` is BELOW the ceiling, and the
difference is inside the floor.** Controls all pass and all could fail: the in-sample ceiling
(0.6886) exceeds the held-out one, so the hold-out is genuinely applied; a shuffled-annotator ceiling
falls to 0.4144; a random predictor lands at 0.3321, not zero. *(R504)*

⭐ **The recommendation's own text named this check as the first an attacker should run. I wrote that
sentence and did not run it.**

⚠ **Three-valued, because the attack must not be over-trusted either.** Both recomputed figures are
*higher* than the quoted ones — a systematic offset, so my instrument differs from the campaign's in a
convention not yet isolated. **CONFIRMED: the two numbers are not comparable, which is enough to
withdraw.** **UNVERIFIED: whether `oracle_k4` exceeds the ceiling under the campaign's own
instrument** — nothing here adjudicates that.

**So this page states the fork and does not recommend a reading.** The three flip conditions from the
withdrawn recommendation are kept below, because they are specifications and do not depend on it:
① a ③-admissible prompt-responsive arm reaching **0.5404**; ② an instrument that ranks `oracle_k4` at
an extreme of the ③ split; ③ a use for "core" that does not require prediction, which is a question
about purpose and not about data.

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

⭐⭐⭐ **AND ② IS NOT THE CLAUSE AT FAULT — the one object anyone calls a core SATISFIES it.**
`coval_core` scores **0.5640** in A2 against the cross-fitted prompt-blind ceiling of **0.5404**, so
it clears ② comfortably. **The definition's empty extension is ③'s doing, not ②'s.** ⚠ Scope, because
the record carries two numbers for this arm under different **statistics**: **0.5640** is A2, the
metric ② is stated in; **0.6044** is per-criterion sign agreement, a different statistic that must
not be compared to an A2 ceiling. *(R475, R485)*
> ⚠ **DOWNGRADED to UNDETERMINED (R486, R487).** The observation stands — five of five arms clearing
> the ceiling are ③-excluded. The *interpretation* does not. Placing the best ③-admissible
> prompt-aware arm inside the class it must beat puts it at **percentile 32.6**, and over the **full**
> population — **23 scorable arms**, not the three R485 named — **22 of the other 22 sit at p0.0**,
> below every one of the 1,820 prompt-blind subsets. **A clause-level conflict requires the admissible
> side to be fairly represented, and a population whose maximum is p32.6 is not.** So this site cannot
> separate *"③ forbids the winning mechanism"* from *"nobody has built a good rating-blind
> prompt-aware arm here"*. Settling it needs a **strong** admissible arm, which is a
> generation-and-judging round. *(R486, R487)*

⭐⭐⭐ **AND THAT ARM IS NOT WEAK — IT IS ALONE.** Counted from the criterion **text**, the
③-admissible side is **1** prompt-responsive full-coverage arm (`gen`), **6** random draws, **2**
fixed sets and **3** partial-coverage arms, against **14** prompt-varying arms on the ③-excluded
side. **"p32.6 of 23 with 22 at p0.0" is one candidate and a floor, not a field.** `UNDETERMINED`
keeps its value and changes its scope: **the definition is not unresolvable — this site ships one
③-admissible prompt-responsive generator.** What a second site must supply is therefore named, and
no analysis here can produce it. ⚠ *Responsive* vs merely *varying* is assigned from construction
knowledge, not measured. *(R502)*

⭐⭐⭐ **AND CLAUSE ② IS A GENUINE WALL, NOT AN ARTIFACT OF AVERAGING.** The gap it turns on is
`gen − 0.5404` (the cross-fitted prompt-blind ceiling) — **−0.0067, inside the 0.0122 floor**. That
could mean the arms agree, or that they differ per prompt and cancel. The cancelling world required
the real pairs to **exceed** a null built from arms with no functional difference; they fall **below**
it, at **percentile 0.0 on both statistics**. **Prompt-awareness buys nothing per-prompt either.**

⭐⭐⭐ **And the severe form of that, which is a claim about the MECHANISM rather than the mean:**
`gen` and `generic` are **two different procedures**; `random_k4_s0/s1` are **two realisations of
one**. The two different procedures land **closer together** (r **0.9349**, true sd **0.1314**) than
the two realisations of a single random procedure (r **0.9574**, true sd **0.1557**). **So the
per-prompt differences prompt-awareness produces are no larger than those produced by drawing
criteria arbitrarily — at this resolution it is not distinguishable from arbitrariness.** ⚠ The
baseline is a **ceiling**, not a zero (two arbitrary k=4 sets are near-maximally different), so the
*non-exceedance* is what the design resolves and the *ordering* is directional at `n_eff = 3`.
*(R499)*

⛔ **AND FOUR ROUNDS WERE SPENT ON THE WRONG DIFFERENCE, BY A STATISTIC THAT COULD NOT SEE ITS OWN
BASELINE.** R494–R497 decomposed `coval_core − gen` and reported it reliable at **r = 0.9355**, true
sd **3.8×** noise. **Two seeds of one random procedure score higher — r = +0.9581, 4.76× noise.** The
statistic measures *"these are two distinct criterion sets"*, which is true of every pair here. The
placebo used throughout was an arm against **itself**, which removes the arm difference and so tests
the instrument rather than the claim. Four nulls (**repetition**, **discriminativeness across arms**,
**paired at n=968**, **criterion length**) stand as nulls and are now unsurprising. R497's **measured
noise floor 0.0353 stands**; the inference from reliability to mechanism does not.
*(R494, R495, R496, R497, R499 — R497's headline retracted by R499)*

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
