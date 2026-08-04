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
> **③** uses **no information from that prompt's own human labels** — not from the construction, not
> from any half of them, **and not by way of a rubric those same annotators wrote**; **and**
>
> **②** scores better, **under a named judge J**, than a size-matched criterion set that never read
> the conversation.
>
> Its size, **under that same judge J**, is **greater than one**; sizes **3 to 8 are not
> distinguishable** by this release.

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

⭐ **AND J CAN NOW BE NAMED (R367).** The rule: **name the judge that best tracks the human.** On the
full rubric — a fixed criterion set that is neither an admitted arm nor the clause-② reference — A2
is **0.5087 at 2B against 0.4120 at 0.8B**, paired **+0.0967 vs MDE 0.0160**.

⛔ **And that rule names the judge under which the definition is non-empty, which is the answer
already published — so it was checked against a DEFINITION-EXTERNAL channel.** On the release's
`unacceptable` ratings, which no clause of the definition reads, 2B ranks the unacceptable response
last **0.7019** of the time against 0.8B's **0.5839** (paired +0.1180 vs MDE 0.0638, on the **161**
prompts carrying such a rating). **Same judge named.** A synthetic judge built to rank it last scores
1.0000, so the channel can separate; shuffled labels score 0.59–0.63, which is where **0.8B nearly
sits**.

⚠ The external rule resolves at **1.85×** its MDE against the adjacent rule's 6×, and **two judges can
refute a rule and never establish one.** What is earned is *"not refuted, and not circular on the one
external channel available"*.

### ③ — the one unsubstitutable clause

That clause ③ excludes the four label-using arms is **forced** — it *is* "no prompt labels". The
measured part is that **nothing else can do its job**:

> Across all **45** reference levels the label-user count **never falls below 4**, while the
> published five fall to **0** at the strongest reference. At p=100 the only arms still admitted are
> the four that read the prompt's labels. *(R360)*

**Strengthening clause ② removes the arms the definition exists to admit and leaves exactly the arms
it exists to exclude.**

⛔ **AND THAT IS 2B-SPECIFIC (R361).** At Qwen3.5-0.8B-Base the label-user count over the same sweep
falls to **0** — references *do* purge them there. The rank dominance is **resolved at 2B**
(gap −4.50, exact two-sided p = **0.0159** over all C(9,4)=126 assignments) and **not resolved at
0.8B** (+2.25, p = 0.2857), so the inversion is a direction rather than a finding.

**Corrected: clause ③ is unsubstitutable at 2B; at 0.8B a strong enough reference substitutes for
it.** The *rule* still stands — it is a **provenance** requirement that applies by inspection and
needs no judge at all. That is a weaker and different argument than irreplaceability.

And its wording is load-bearing: it must say **held out from the PROMPT**, not "from the
construction". Three fitted arms pass the weaker reading, and in the quintile where two annotator
halves disagree **their entire advantage is gone**. *(R295)*

⛔ **AND AS IMPLEMENTED IT CLOSES ONLY THE RANKING CHANNEL (R363).** Clause ③ is applied everywhere
by one hand-written set — `{oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1}` — duplicated
across four rounds. Audited against `corebench/select_core.py`, that set is **correct about the
rankings**: `comparisons.jsonl` is opened only for `oracle_k / indep_k / greedy_k`.

But `topw_k` — **four of the published five** — selects on `w = mean importance score` from
`conversation_rubrics.jsonl`, and the annotators who wrote those scores are, at **95.3%**, the same
people whose rankings define that prompt's target (cross-prompt sham **0.016**, ratio **58×**, over
**1,160** distinct annotators against a median panel of 16; **473 of 968** prompts have complete
overlap and **none** has zero).

⚠ **MEASURED** is the overlap — a census, with no judge anywhere in it. **DERIVED**, from that plus
this release's own finding that rubrics are authored *after* ranking, is that `topw_k` is **not
producible from the conversation alone**.

✅ **AND THE CHANNEL CARRIES NOTHING MEASURABLE (R364).** Rebuilding `topw_k4`'s weights from
annotators overlapping the evaluators in a swept fraction, the margin is **flat**: paired
`margin(d=1) − margin(d=0)` is **−0.0000 against its own MDE of 0.0096**, with three seeds
straddling zero. A **planted** person-specific channel is detected from **+0.0297** upward and not
at g=0, so the null has demonstrated power; the sham that permutes *which annotator's scores carry
which id* lands inside the MDE, so the dose was measuring identity.

⚠ **A bound, not a zero:** `topw_k4`'s margin is +0.0139, so this rules out a channel larger than
~69% of it and says nothing about a smaller one. **So clause ③'s wording was wrong and stays
corrected; the published five are not compromised at this resolution.**

⭐ **AND IT IS NOT A 2B STATEMENT (R365).** The dose is flat at **both** judges — −0.0000 vs MDE
0.0096 at 2B, **+0.0000 vs MDE 0.0107 at 0.8B** — and 0.8B's MDE is only **1.11×** 2B's, so that
design could have excluded what 2B excluded. The planted channel is detected at **both** judges and
undetected at g=0 at both, so neither null is silence. **After a change of judge emptied clause ②,
inverted an arm family's ordering, destroyed the size band's premise and cost clause ③ its
irreplaceability, this is the first claim here to come through unchanged.**

⚠ Two judges can **refute** instrument-independence and never establish it, so what is earned is
**"not refuted at a second judge"** — and at 0.8B the level itself is unresolved (−0.0126 vs 0.0145),
so it is a flat dose on a null level.

⛔ **AND THAT SURVIVAL IS CHEAPER THAN IT SOUNDS (R366).** Under **any** scaling `x → βx` a true
**zero maps to zero exactly**, while a true nonzero maps to `β·nonzero` and may fall below its MDE —
so **a null surviving a shrink is the cheapest possible survival**, and this claim is a null. My own
explanation for it — *"it is a difference, and differences are what shrink transformations
preserve"* — is **refuted**: R362's size-band steps are differences of differences too, and **1 of 3**
survive. Over the whole population of **7** claims run at both judges, neither `difference` (Fisher
**p = 1.0000**) nor `null` (**p = 0.4286**) sorts survival, on a test where a perfect split **would**
have reached **p = 0.0286**. **So nothing in this record predicts which claims survive the judge, and
the proposal to restate the definition in differences is withdrawn.**

---

## The size

**Not four.** The release ships exactly one core, of size four, and "four criteria" was a
description of that instance rather than a property of the category — the k-sweep cannot separate 3
from 8. The largest identifiable *member* core is **k ≤ 2**; the class is identifiable where the
member is not. *(R224, R228, R230)*

**State the bound the design supports: more than one, and 3–8 indistinguishable.**

⛔ **AND THAT BAND IS ALSO JUDGE-INDEXED (R362).** At 0.8B there is no band to bound: the rubric's
top-k margin against a size-matched blind reference is **negative at 6 of 7 sizes** and resolvably so
at k=12. Only the band's **exit** (8→12) resolves at both judges; both entry steps (1→2, 2→3) resolve
at 2B and not at 0.8B, and 0.8B resolves an interior step (3→4) that 2B does not.

⚠ The median margin ratio is **−0.343** against R301's fitted shrink **β = +0.401** — a *sign
inversion* at **4 of 7 sizes**, not attenuation. Two parts of the size question were **not** re-run
because they are settled: the upper bound `k_max = max{k : C(n,k) ≤ a(m)}` is **combinatorial with no
judge in it** (R224/R228), and the k-curve's *shape* across judges was already measured by R356
(ρ = +0.667, inside its forced band).

---

## ⛔ THE PIPELINE'S OWN FLOOR IS UNMEASURED AT THIS JUDGE 2026-08-04 (R415)

**5** committed re-run pairs exist at the 0.8B judge — ⚠ **same RULE, not same code: R416 hashed the
committed criterion sets and all five differ, on 91–99.6% of prompts.** Re-running the rule END TO END
— re-selecting the criteria and re-scoring them — shifts an arm's
**mean A2 by up to `0.116489`**, which is 13× the +0.009002 clause ②'s headline rests on.
⚠ This is a **rule-level** floor, not a scoring floor, and it does **not** establish that scoring is
unstable. ⭐ **FULLY RESOLVED 2026-08-04 (R419 + R420): IT WAS NEVER A FLOOR.** Scoring is deterministic
(R419, bitwise on 200 prompts) and selection is deterministic (R420, byte-identical criteria, 0
unseeded stochastic constructs), so the pipeline is deterministic **given its inputs** — and two
deterministic stages cannot produce a 91–99.6% criteria difference from the same inputs. **The
`_08b`/`_08bR` files are two different CONFIGURATIONS, not two draws, and `0.116489` is a
between-configuration difference rather than a noise floor of anything.**
⭐ **AND THE TWO CONFIGURATIONS ARE NOW NAMED (R422–R424, 2026-08-04).** The families agree with each
other at `≤ 0.03%` disjoint cells but are **~96% absent from the default judge's table** — `0.0380`
(587 of 15,448) against that table's `1.0000` (15,440 of 15,440) on a known default-emitted arm. So
`0.116489` is a difference between **`--select-npz` frozen at the default** and **the rule re-run
under a second judge**, and that second judge's table is **not committed anywhere in this repo**.
⛔ ~~Every number on this page computed from an `_08b` arm is therefore instrument-UNKNOWN.~~
**RETRACTED the same day by R426.** R424's candidate loop skipped `corebench/results` — 106 files, 4
of them full-shaped — so it never tested the emitter. `sat08_full.npz` contains both families at
`1.0000` (15,448 of 15,448) while containing `topw_k4` at `0.0369`, the exact mirror of the default
table. ⭐ **The
instrument is `Qwen3.5-0.8B-Base`, named in committed source at `R290/run.py:58`.** ⚠ Containment is
necessary, not sufficient — the artifact evidence names *the table whose values these are*, and the
model behind it is **source-attested**, not artifact-verified. *Conflating those two kinds of
evidence is what built the wall.*

⭐ **(R419): the scoring-only floor is EXACTLY ZERO.** Two runs of
identical criteria at this judge — proven identical by their committed `criteria_sha256` — are
**bitwise identical on all 200 prompts**. So the shift above is located **entirely in SELECTION**, and
**every A2 figure on this page is a fixed quantity given its criteria**, at batch 32.

**No such pair exists at the 2B judge that produced every number on this page.** So the floor here is
**not measured**, and every A2 figure in this document rests on an assumption of pipeline stability
that **failed at the only judge where it could be checked**.

⚠ The cause is not separated: a 0.1 shift is large for kernel non-determinism, so either the pipeline
is wildly unstable **or** two configurations share a filename. Both disqualify those files as
replicates, and neither branch is claimed.

⚠ This does not retract any number. It scopes them: they are single draws whose draw-to-draw spread
is unknown at this judge, and §1's *"noise floor: measured, not assumed"* is unmet for the first time
explicitly rather than by omission.

## ⛔ READ LITERALLY, CLAUSE ② ADMITS ALL FIVE — INSIDE THEIR OWN NOISE 2026-08-04 (R408)

The clause says **scores better than**. The code says `e > 0 AND |e| >= ZEFF*se` — *significantly*
better. Run both at the per-k maximum blind set:

| label-free admitted | |
|---|---|
| **STRICT** (`e>0` and `\|e\| >= ZEFF*se`) | **0** |
| **LITERAL** (`e>0`) | **5** — `coval_core`, `topw_k3/4/6/8` |

`coval_core` scores **`+0.009002`** against `se = 0.003703` — **0.87 of its own significance bar.**
The other four label-free arms reach 0.38–0.81. The four **label-reading** arms reach **3.4×–6.7×**.

**So clause ② at the universal reference IS satisfiable without label access, under the definition's
own wording — and every arm that satisfies it does so by a margin it cannot distinguish from zero.**
The honest statement is not that a core was found; it is that **the definition as written has no error
control**, and the order-of-magnitude gap between the label-free and label-reading arms is exactly
what the significance term was separating.

⚠ One release. An unguarded positive mean is the quantity least likely to survive a second.

## ⛔ AT THE MAXIMUM BLIND SET ONLY THE LABEL-READERS SURVIVE 2026-08-04 (R407)

The universal reading is answerable from a **single cell**, which needs no strictness ordering — only
that the cell's reference be the maximum, and `ref_at(k, 100)` returns `order[-1]`, the highest-scoring
prompt-blind set of that arm's own size.

**At that reference the admitted set is `{greedy_k4_fit1, indep_k4_fit1, oracle_k4, oracle_k4_fit1}` —
all four of which read the prompt's own rankings. Label-free admitted: 0.**

Per arm, the highest grid point still admitting it: `topw_k8` 95.0 · `topw_k3` 95.5 · `topw_k4` 98.0 ·
**`coval_core` 99.5** · `topw_k6` 99.5 · the four label-readers 100.0. **The released core clears the
99.5th-percentile blind set and not the maximum.**

⛔ **And this answers a test the sentence does not contain.** The code's `admits` is
`e > 0 AND |e| >= ZEFF*se` — *significantly* better — while the definition says **scores better than**.
The coded test is STRICTER, in the direction that flatters. **The literal `e > 0` reading has never
been run.** That is the fourth under-specification in clause ②, after the missing member, held-out vs
in-sample, and the percentile called *every*.

## ⛔ THE UNIVERSAL READING HAS NEVER BEEN RUN 2026-08-04 (R406)

Clause ② names a class and no member, and the campaign's answer has been R327's three readings, of
which **A** was labelled *"better than EVERY prompt-blind set of that size"* — the plain-English one.

**It was instantiated at `0.5546019830`, the best HELD-OUT of 1,820. The MAXIMUM over the same 1,820
is `0.5574753088`.** The gap is **`+0.0028733259`**, and the reference brackets **below the committed
p99**: between **1% and 10%** of the blind subsets beat the bar the word *every* was tested against.
*(A bracket, not a count — R331 committed seven order statistics, not 1,820 scores.)*

**So the universal reading of clause ② has never been run**, and the disagreement about whether this
definition admits its own instance is exactly that `0.0029`: `coval_core` clears a p99 bar and does
not clear the maximum.

⚠ This does not retract R327 — its divergence finding stands and is strengthened. What is corrected is
the **name of one rung**. ⚠ And no control could have caught it from inside R327, whose controls all
concerned the **ordering** of its readings: an ordering can be perfectly correct while every rung is
mislabelled.

## ⛔ CONJUNCT DECOMPOSITION 2026-08-04 (R404) — clause ③ is not one clause, and its third part is not implemented

Clause ③'s exclusion is published as one number, `4 of 42`, attributed to the clause as a whole.
Decomposed against `corebench/select_core.py`'s rule dispatch — **not against the arm names** — the
three conjuncts do wildly different amounts of work:

| conjunct | excludes on its own | **beyond ③a** |
|---|---:|---:|
| **③a** reads the prompt's own rankings | 4 | — |
| **③b** fitted on a **half** of them | 3 | **0** |
| **③c** weights from an annotator-written **rubric** | 13 | **13** |

**③b excludes nothing whatsoever.** Every `_fit1` arm already reads the rankings, so ③a has removed it
first. And enforcing ③c **as written** collapses the admitted set from **5 to 1 — `coval_core` alone**,
the object this definition was written from.

**So the definition sits between two failures.** *As implemented*, ③c does no work and R363's
`W_CHANNEL_OPEN` stands — arms are admitted that the text forbids. *As written*, it admits only its own
instance. **Neither is a definition of a category.**

⚠ The count is a **lower bound**: a label route the rule dispatch does not reveal would mean more
exclusions, not fewer. ⚠ And whether ③c *should* be enforced is an act of definition, not a
measurement, and is not decided here.

## ⛔ STATABILITY 2026-08-04 (R403) — three of six clause-parts cannot be SAID off this release

Applied to the second corpus R398 found, the clauses split. **Not into true and false — into sayable
and unsayable**, which is a third value and was never available while there was one object.

| clause-part | needs | corpus two |
|---|---|---|
| **①** vs a draw of the prompt's **own rubric** | a per-prompt rubric | **NOT-STATABLE** |
| **③b** …not from any **HALF** of the annotators | ≥2 annotators per prompt | **NOT-STATABLE** — measured: **max 1 rater**, 0 of 27,172 interactions have 2 |
| **③c** …nor via a **rubric those annotators wrote** | a per-prompt rubric | **NOT-STATABLE** |
| **②** vs a prompt-blind size-matched set | responses + human target + pool | **STATABLE** |
| **③a** no information from the prompt's own labels | per-prompt human labels | **STATABLE** |
| **size** >1; 3–8 indistinguishable | a judge + a k sweep | **STATABLE** |

**3 of 6 clause-parts are NOT-STATABLE off this release.**

**Clause ① is now doubly hollow.** It was already `DERIVED` vacuous here — the region where it could
bind is empty by arithmetic. It is now also **unsayable elsewhere**. A clause that excludes nothing
where it was born and cannot be stated off that object is a description of a **schema**, not of cores.

⚠ **No clause is restated here.** Rewriting one so it survives on a new corpus is an act of
definition, not a measurement, and doing it in the same breath as the diagnosis is how a definition
gets tuned to whatever object is in front of it.

**The transportable residue: *label-free, and better than prompt-blind*** — clauses ③a and ②, which is
also the pair that carries the whole measured boundary.

## What this definition cannot claim

| | |
|---|---|
| **"a core", unindexed** | the admitted set is **empty at the second judge**; only *"a core under J"* is licensed — and J is named by R367's rule, not chosen |
| **a count of admitted arms** | the set moves within **0.25 MDE** (R332) and with the reference's percentile (R354) |
| **that its three clauses each test something** | one excludes nothing, one is judge-emptied, one is irreplaceable |
| **an unindexed size** | at 0.8B top-k loses to a size-matched blind set at **6 of 7** sizes (R362) |
| **that it works on responses it was NOT scored against** | **unresolved against a fair floor** — see the transport note below (R368, R370) |
| **transfer to another criterion pool** | every level here is a fact about **this 16-criterion pool** (R331) |
| **transfer to another release** | ~~one release~~ — ⛔ **RETRACTED 2026-08-04 (R398). This line was never a wall; it was a query nobody ran.** `data/utterances.jsonl` — **68 MB, fetched 2026-07-29** and referenced by 0 files in this repository — holds **68,371 rows over 8,011 conversations, 100% carrying a human `score`, with 26,285 prompts having ≥2 distinct model responses across 21 models.** A second corpus has been on disk the whole time. ⚠ It has **no rubric**, so clauses defined against `full` still cannot transport; **clause ② and the human-agreement target can.** |

---

## ⛔ CORRECTION 2026-08-04 — the limit below is not structural, it is untested

The transport section closes on R233's limit, stated in the definition's strongest terms: the fresh
responses carry **no human rankings**, so transport is of the **compilation** and *"never agreement
with people"*. **That sentence describes this release, and was silently read as describing the
world.**

[`R398`](A24_what_the_definition_costs/R398_is_there_a_second_object_on_disk) asked the cheapest
question left and it had never been asked: **a second corpus with 68,371 human-scored responses has
been sitting in `data/` since 2026-07-29, referenced by no round and named in no document.**

**What changes:** *"agreement with people on responses the core was not built for"* moves from
**impossible** to **untested**. **What does not:** every number below still stands as measured — R398
ran no transport test, computed no core, and reports no effect. It established that the object exists
and nothing more.

## ⭐ THE FIRST CROSS-RELEASE NUMBER 2026-08-04 (R427) — and clause ②'s comparator loses to a length heuristic

**74,048 judge calls, 2,200 seeded conversations, 7,342 interactions of the second corpus.** The
prompt-blind arm — clause ②'s own comparator — picks the human-chosen response at **`0.4374`**. The
judge-free *longest-reply* rule reaches **`0.5096`**.

| arm | ACC | note |
|---|---|---|
| `generic` (prompt-blind) | **`0.4374`** | 74,048 calls |
| chance | `0.4194` | derivation, `mean(1/n_responses)` |
| **longest reply** | **`0.5096`** | **no judge, no criteria, no compute** |
| first (position) | `0.4375` | `generic` is indistinguishable from it |

⛔ **And the bar was fixed before the arm existed.** Read against chance alone, `+0.0179` at 1.05× its
MDE would have been reported as transport. Against the shortcut it is a loss of **−0.0722**, 2.85× the
MDE.

**Robust across the whole grid: `generic` clears the shortcut in 0 of 24 cells** — aggregation
{mean, min, max, median} × restriction {all, n=2, n≥3} × unit {conversation, interaction}, the length
baseline recomputed *inside* every cell. ⚠ Those four aggregations are monotone transforms of the
same values, so this is a **falsification sweep, not a replication**.

⭐ **A pooling attack on the one positive number FAILED, and the scope it leaves is narrower.**
Chance is `1/n` and n varies, so the pooled `+0.0179` could have been a weighting artifact. Stratified
against each stratum's own chance, with the length arm firing as positive control in all three:

| n responses | chance | `generic` − chance | MDE | verdict |
|---|---|---|---|---|
| **2** (2,191 convs) | 0.5000 | **+0.0071** | 0.0229 | **at chance** |
| 3 | 0.3333 | +0.0720 | 0.0646 | clears |
| 4 | 0.2500 | +0.0315 | 0.0307 | clears |

**So the apparatus carries a small real signal only where ≥ 3 responses are compared, and none at
all in the two-response case that is almost the whole corpus.**

⚠ **This measures clause ②'s FLOOR, not clause ②** — see the next section. And `randblind`/`vacuous`
are still judging; they decide whether the criteria's *content* contributes anything, and cannot
change either result above.

---

## ⛔ `generic` IS CLAUSE ②'s COMPARATOR, NOT ITS SUBJECT 2026-08-04 (R403 + R427)

R403 measured which clause-parts can even be SAID off the home release: **3 of 6 are STATABLE on the
second corpus** — the *size* bound, clause **②**, and **③a**. The three that cannot: **①** and **③c**
need a per-prompt rubric the corpus does not have, and **③b** needs ≥ 2 annotators per prompt where
the corpus carries **`max_raters = 1`** and **0** multi-rater interactions.

⚠ **And a STATABILITY verdict is a fact about the release's FIELDS, not about whether anyone ran the
test.** Clause ② is statable there and, until R427 lands, unstated.

⛔ **The precision error worth naming.** Clause ② reads *"better than a size-matched set that never
read the conversation."* **`core_generic.json` IS such a set** — prompt-blind by construction. So
R427 measures **the comparator's own accuracy on a second release**, i.e. clause ②'s **floor**. It
cannot test clause ② itself, because clause ②'s *subject* — a prompt-specific core — **does not exist
for this corpus and must be generated before the clause has two arms.** Saying "R427 tests clause ②
elsewhere" would have inverted which side of the inequality was measured.

---

## Transport — the clause this definition does not have

Every clause above certifies a core against **the four responses it was scored on**. Nothing says it
works on new ones, and until R368 nothing had measured it: `transport` appeared here **zero** times.

Matched on per-prompt difficulty — the confound R233 named when it declined its own verdict — the
core reproduces the full rubric's ordering on **unseen** responses better than a size-matched random
draw, by **+0.0992 against an MDE of 0.0654** on R233's own exact-class metric, and **+0.0612 vs
0.0535** on a finer pair metric. Same sign, both resolved.

⚠ **Marginal, and stated as such**: 1.52× and 1.14× of their own MDEs, where the MDE is computed over
**4 strata** — the effective n is the strata, not the 250 prompts.

⚠ **And the shape underneath is unexplained.** The core is **at or below random on the responses it
was built for** and above random on responses it was not. **[UNTESTED]** nothing here explains that,
and it is recorded as the residual.

⚠ **R233's limit does not move:** the fresh responses carry **no human rankings**, so this is
transport of the **compilation** — agreement with the full rubric — and never agreement with people.

⛔ **AND THE CONTRAST DECOMPOSES THE OPPOSITE WAY UNDER THE TWO METRICS (R369).** R368 computed the
floors per stratum per arm and never printed them: `Δfloor` is **+0.0308** on exact and **−0.0187** on
pair — under one metric the random baseline **rises** on the fresh arm, under the other it **falls**.
The instability is **bounded**: `Δcore` is positive under both (**+0.1300**, +0.0425) and larger in
magnitude than `Δfloor` in both, so the core term dominates either way. What is metric-dependent is
the **attribution of magnitude**, not the direction.

⚠ And a structural asymmetry remains unseparated: the floor is drawn from **`full`'s own criteria** —
among the items summed to make the target — while the core is a rewrite. A difference-in-differences
cancels that only if it is additive across arms, which the flipping `Δfloor` puts in doubt.
Separating it needs a floor drawn from criteria **outside `full`**.

⛔ **AND AGAINST A FLOOR THAT IS NOT A SUBSET OF ITS OWN TARGET, IT DOES NOT RESOLVE (R370).** The
suspicion was testable and the test needed new labels: the generic 16-criterion pool, identical
across prompts and therefore outside any prompt's `full` rubric by construction, judged against the
fresh responses (16,000 labels). With that floor the contrast is **+0.0810 vs MDE 0.0920** (exact)
and **+0.0161 vs 0.0251** (pair) — **inside the MDE on both**.

**The subset advantage is now a number**: on the original arm the subset floor sits **+0.1413** above
the non-subset floor (exact; +0.0662 on pair). A random draw from `full`'s own criteria reproduces
`full` far better than an external pool does.

⚠ **Not refuted — not resolved.** Both point estimates stay positive; with a fair floor this design
**cannot resolve** transport. And the collapse arrives two ways: on `pair` the contrast falls **74%**
while the MDE shrinks, on `exact` the contrast barely moves and the **MDE grows 41%**.

⛔ **AND THAT VERDICT IS ITSELF A SPECIFICATION CHOICE (R371).** R370 fixed the stratification at
**S = 4** and never swept it. Sweeping S on the same data, the `exact` contrast **resolves at S = 2
and S = 5** and does not at S = 3, 4, 6, 8. On `pair` it is inside the MDE at every S. So
*"transport collapses"* is what S=4 says, not what the data says.

⚠ The between-stratum spread is **sampling noise, not structure**: against a *no-heterogeneity* null
the median ratio is **0.98**. And the MDE **rises** with S, because smaller strata get noisier faster
than √S recovers — so more prompts would help only **at fixed S**, never by adding strata.

⛔⛔ **AND R371'S OWN READING DIED THE SAME WAY (R372) — the curve is no more reportable than the
cell was.** R371 closed by saying *"the honest statement is the curve, not the cell."* Re-run on
**480 random halves** of the same 250 prompts:

| | |
|---|---:|
| R371's set `{2, 5}` recurs | **2.9%** of halves |
| modal outcome | **∅**, at **41.5%** — with **38** distinct sets |
| two halves of one split agree on the set | **4.4%** *(both-empty agreements removed)* |
| `exact` set at full n under an order-independent floor | **{2, 3, 5}**, not `{2, 5}` |

**And the curve's shape is a derivation, not a measurement:** R371 itself measured that the MDE rises
with S while the contrast does not, which makes the resolution rate fall with S **by algebra**.
**S = 2 tops every ranking because its between-stratum sd has ONE degree of freedom and collapses**
— below half the typical contrast in **28.3%** of halves against at most **7.3%** anywhere else
(3.9×). The tell was a full-sample `pair|2` cell returning **MDE = 0.0007**.

⚠ R371's floor was also **order-dependent** — one rng shared across a call, so a prompt's floor
depended on its company. 12 permutations move the `exact|S=4` contrast across **+0.0540 … +0.1185**.

⛔ **AND R368'S OWN MDE IS UNDER-PRICED, WHICH THE CAMPAIGN HAD NO RECORD TO NOTICE (R373).** The
transport MDE above divides by the square root of a count of **strata**, and that count is **4**. A
4-unit sd estimate lands **below half its true value 13.9%** of the time and below three quarters
**36.0%** of the time — so `+0.0992 vs 0.0654` is a comparison against a threshold that is itself a
4-point estimate. **Not refuted; under-priced** — and the distinction matters because nobody
re-examines a cell that reported RESOLVED.

⚠ Of **55** MDE call sites across **38** rounds, **5** divide by a count of aggregated units rather
than the sample, and after resolving each k, **R368 is the only one outside R370–R372 with k < 10**
(R355 is flagged and its k is **25**, which is fine). *The flag is not the severity; only k is.*

> **`The resolving set` is not a well-defined object of this design.** R371 was right that R370's
> S = 4 was a specification choice, and then read a SET off the same single draw — **the error it
> convicted R370 of, one level up.**

**So transport is a stated LIMIT, not a candidate clause** — and the limit is now stronger and
simpler than R370's or R371's version: **the transport contrast is not resolvable by this design at
any stratification, and no stratum count is preferable to another on this data.** R368's number
stands as a number; what it measured was the floor.

## The one sentence

> **What survives every attack in this campaign is clause ③'s RULE — but stated more strictly than
> the campaign has ever implemented it, and on provenance rather than irreplaceability.** Clause ① is a consequence, clause ② holds only under a named judge, the size is
> a bound rather than a number, and *"nothing else can do clause ③'s job"* is **2B-specific**
> (R361). What is left is the rule itself: **a core may not be built from the labels of the prompt
> it is for** — which is checkable by inspection, needs no judge, and is the one claim here that no
> instrument can empty.

⚠ *That closing sentence was published unconditionally one round earlier and was corrected by
attacking it rather than by building on it. It had survived exactly one round.*
