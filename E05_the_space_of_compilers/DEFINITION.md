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
> the conversation; **and**
>
> **④** scores better, under that same judge J, than **every rule computable from the response set
> alone**.
>
> Its size, **under that same judge J**, is **greater than one**.
>
> *(Reported, not required: sizes **3 to 8 are not distinguishable** by this release.)*

⚠ **The size line was two different things and is now written as two (R441).** *"3 to 8 are not
distinguishable"* is a statement about **resolution**, and a non-result cannot remove a member — it
excludes nothing **by construction**, so it is a **caveat, not a clause**. That is a derivation and
no measurement changes it. **"Greater than one" is left in the conjunction**, and here is its
evidence: of **52** arms with a k readable from their committed core file, exactly **1** has k=1
(`topw_k1`), and clause ② already excludes it — so on this evidence half A removes **0 of 1** arms
the other clauses admit. ⛔ **It is NOT demoted on n=1.** Retracting a clause on a single arm is the
cheap-attack failure this campaign's standard names explicitly: the most expensive error is the one
that retracts something true. **What would settle it** is constructing a k=1 core that ②∧③∧④ admits.
→ [`R441`](A24_what_the_definition_costs/R441_is_the_size_clause_a_clause)

**Clause ① is not a clause.** It is a consequence — see below.

## ⛔ THE EXTENSION — and this document states two incompatible answers (R442, 2026-08-04)

**What the conjunction actually admits on the home release, at judge J, over R360's 42-arm space:**

| | admits |
|---|---|
| ~~as IMPLEMENTED — hand-written 4-arm set~~ | ~~5~~ — **superseded, R444** |
| **as WRITTEN, now also as implemented** | **1**: `coval_core` |

⭐ **CLOSED 2026-08-04 (R444), by a DECISION rather than an experiment.** The set was corrected to
match the text, and the choice was **forced**: weakening the text was preferable only while ③-as-
written looked unenforceable, and R443 showed `select_core.py` names every selector consuming
annotator importance. `assurance/clause3_as_written.py` now derives ③ from the source —
**target-readers** (`oracle_k`, `indep_k`, `greedy_k`) **and w-readers** (`topw_k`, `topabs_k`,
`topwvar_k`), but **not** `topvar_k`, whose own comment calls the spread *"a property of the
responses, never of the human target"*. ③ goes from excluding **4** to **14** of 42; the extension
goes from **5** to **1**. ⚠ **7** arms have provenance the source cannot classify (`coval_core`,
`gen`, `generic`, `promptecho`, shams) and are returned **UNKNOWN, never silently admitted** —
`coval_core` survives on R443's separate containment measurement, not on anything ③ can decide.
⚠ **`[unchallenged]`** — this standard prescribes an adversary for a judgement call; agent dispatch
was unavailable, so the decision is recorded as unchallenged, not as clean.

⭐ **Neither is the published five** (`coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4`) —
only **2 of 5** overlap. The definition's boundary runs along the **selector** axis, not the k axis:
it admits `topw` at four sizes and rejects three sibling selectors at k=4. ④ and the size clause add
nothing to this (R440, R441).

⛔ **And under its own written clause ③ the extension is ONE ARM — the object the definition was
written from.** The ③ section below states that `topw_k` is *"not producible from the conversation
alone"* — which is this definition's **own opening phrase** — while the implemented set admits four
`topw_k` arms. **The document asserts both and reconciles neither.** ⚠ This is *not* a claim that
③'s derivation is wrong: if it stands the extension is one arm, if it falls the extension is five.
**What is certain is that the two cannot both be published as they are**, and until that is
resolved the extension must be quoted with which reading produced it.
✅ **And the extension under the written reading is 1, not 0 (R443).** ③ as written excludes
**three** selectors, not one — `select_core.py:131` computes `w = mean annotator score` and
`topw_k`, `topabs_k` and `topwvar_k` all consume it, while `topvar_k` does not. But `coval_core`
survives: only **0.0779** of its criteria appear verbatim in its own prompt's rubric, against a
cross-prompt sham of exactly **0.0000**, over **968** prompts. So its text is not drawn from the
rubric and the containment objection does not reach it. ⚠ **UNVERIFIED-leaning by construction:**
containment is *sufficient* for the provenance objection and *not necessary* — the same annotators
could have authored it in different words, and this instrument cannot see that. ⭐ The 7.8% that
*is* contained is real and strictly prompt-specific, since the sham is zero.
⭐ **AND THE ONE ARM IS A FINDING, NOT A THRESHOLD ARTIFACT (R445).** The extension is one arm
*not* because no third-source object exists: **`gen` — a home-release core generated from the
conversation alone — has been in the 42 the whole time**, ③-corrected does not exclude it, and **②
does**. Paired against ②'s own reference `POOL[0:4]` over **968** prompts, `gen` scores
**-0.0162 [-0.0270, -0.0051] against an MDE of 0.0151** — resolved, but at **1.07×** its floor —
while `coval_core` scores **+0.0178 [+0.0079, +0.0285]** vs 0.0146, at 1.22×. **The definition's
entire boundary at home separates the two by 0.0340 across a floor of ~0.015.** Resolved, and thin;
quoting only the first half would make a 1.07× margin sound like a verdict. Controls: an oracle
clears the reference by **+0.1702** (MDE 0.0184), the reference against itself is exactly 0, and the
wrong-prompt sham fails by **more** (**-0.0669**) as it must.
✅ **AND THAT VERDICT SURVIVES EVERY ADMISSIBLE REFERENCE (R446).** R331's standing defect is that
②'s reference `POOL[0:4]` was **chosen by file order**. Sweeping **all 1,820** size-4 subsets of the
pool, paired per prompt over 968 prompts: `gen` is **resolvedly** better than **0.4%** of them and
`coval_core` than **98.4%**, against an oracle admitted under **1820/1820**. **So the file-order
choice did not manufacture the verdict.** ⭐ And the point-vs-resolved gap is its own finding: `gen`
would be *"better"* than **26.2%** of references but is resolvedly better than 0.4% — a **25.8**-point
gap that is the resolution effect made visible, and the reason the naive quantile sweep would have
misled in the flattering direction. ⚠ This shows the ANSWER does not depend on the arbitrary choice;
it does not FIX the choice, which remains R331's open defect.
→ [`R446`](A24_what_the_definition_costs/R446_clause_two_over_every_admissible_reference) ·
[`R445`](A24_what_the_definition_costs/R445_is_the_extension_empty_on_a_resolved_difference) ·
[`R442`](A24_what_the_definition_costs/R442_the_extension_under_clause_three_as_written) ·
[`R443`](A24_what_the_definition_costs/R443_does_clause_three_as_written_exclude_the_core_itself)

⭐ **Clause ④ was ADOPTED 2026-08-04**, after every objection I could raise against it was measured
rather than argued: it is **statable** (its bar saturates at 6 of 30 rules, R435); it **excludes
nothing at home and everything on the second release** (R436/R434); the two bars **invert**, so it
binds exactly where ② goes slack (R437); the sign **does not flip** across strata of one release
(R438); and it is **not a reparameterisation of ②** — its bar sits at the **0.00th percentile** of
all 1,820 size-4 subsets of ②'s own reference pool, **0.0687 below the weakest of them** (R439) — where the published reference sits at 91.7.
⚠ **Its scope:** two releases, one judge, and a **30-rule hand-built family** standing in for "every
criterion-free rule". The family is published in R435's artifact so that extending it is how this
clause gets refuted.

---

## What each clause is measured to do

| clause | excludes | status | scope |
|---|---:|---|---|
| **①** better than a random draw of the prompt's own rubric | **0 of 41** | **DERIVED** — the region where ① could bind is empty by arithmetic (`GAP ≥ SLACK` on every arm) | R347 |
| **②** better than a prompt-blind set | **33 of 42** | **MEASURED** — carries the whole boundary among label-free arms | R360 |
| **③** no prompt labels | **14 of 42** | **DERIVED** from the source, not hand-listed (R444) — target-readers *and* w-readers | R360·R444 |
| **④** better than every criterion-free rule | **0 of 42** | **MEASURED** — coverage of this space is 42/42 | R440 |

⭐ **④'s zero is the argument, not an embarrassment.** On this release ④ **costs nothing** — it
removes no arm the definition already admits — while on the second release it removes **all 7** and
② removes **none** (R434). A clause that is free where the definition works and binding where it
fails is what a sufficiency clause is for; a **non-zero** here would have meant ④ was quietly
re-litigating ②'s boundary, which R439 independently ruled out. ⚠ **①'s row is on R347's 41-arm
space, not this one**, and is left unharmonised rather than given a denominator no round recomputed.

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
- ~~**It is emptied by a change of judge**: **5** arms admitted at Qwen3.5-2B-Base, **0** at
  Qwen3.5-0.8B-Base, on all 41 arms. *(R301)*~~ ⛔ **CORRECTED 2026-08-04 (R447): false as a
  statement about the JUDGE.** R301's `0` is measured at `POOL[0:4]` — the file-order draw. Swept
  over all **1,820** references judged by 0.8B, ② admits `coval_core` under **11.9%** of its own
  class and `gen` under **25.6%**, with an oracle admitted under 1820/1820 so the shares are
  measurements and not silence. ⭐ **And the ordering INVERTS**: at 2B `coval_core` clears 98.4% and
  `gen` 0.4%; at 0.8B `gen` clears more than `coval_core` does. **The judge does not merely move the
  threshold — it reorders the definition's two candidate members**, which is a stronger claim than
  the one being corrected. ⚠ Shares are comparable across judges; A2 LEVELS are not.
  **NARROWED 2026-08-04 (R448): the reordering is real but it is NOT a symmetric swap, and it has a
  measured mechanism.** Against a null built from the 1,820 references' own shifts, `gen` rises
  **+0.5319** in quantile where references starting at its rank move a median **+0.015…+0.054**
  (p ≤ 0.0055, **10 of 10** grid cells surviving BH), while `coval_core`'s **−0.3016** survives only
  at the two narrowest bands (4 of 10) **and its null is CENSORED** — it starts at quantile exactly
  1.0000, so its band can only move down and its p is an upper bound. **The mechanism is
  cross-judge criterion stability**: per-criterion sign agreement is `gen` **0.6302** vs the
  reference pool's **0.5899** (Δ **+0.0403**, MDE 0.0143, RESOLVED), while `coval_core` **0.6044** is
  *unresolved* against the same pool (Δ +0.0144, MDE 0.0147). **So `gen`'s absolute A2 FALLS
  (0.5374 → 0.4743) while its RANK rises, because the reference class falls further.** Regression to
  the mean is dead as the whole story; ties are dead as the mechanism (2B 0.045 → 0.8B 0.080, and
  dropping tied pairs changes no cell). *(R448)*
  **AND IT DOES NOT BECOME A FIFTH CLAUSE (R449).** Cross-judge criterion stability X is a **real
  axis**, measured: it varies across the 13 arms carrying both judges (permutation p = **0.0000**,
  between-arm sd 0.0251 vs null median 0.0063), it responds to a content manipulation (**5 of 5**
  arms beat their own wrong-prompt sham, pooled **+0.0417** [+0.0306,+0.0524] vs MDE 0.0152), and it
  is **not** a reparameterisation of clause ②'s score gap — paired at n=398 prompts,
  corr(ΔX, ΔA2) = **−0.0431** [−0.1424,+0.0578], so the two share **at most ~2.0%** of their
  variance. ⛔ **It is nevertheless not statable as a clause here**, and no measurement can change
  that: a stability predicate ranges over a judge **PAIR**, `n_judge_pairs = 1`, and the register
  records that no third judge exists. **A property can be real and unstatable at the same time.**
  ⚠ Measured on 398 prompts (the 13-arm intersection), not the 968 the rest of this document uses.
  *(R449)*

⭐ **THE EXTENSION OF 1 IS STRICTNESS, NOT TAUTOLOGY (R450) — §4's oldest suspicion about this
document is dead.** Every earlier round tested the clauses against arms built by *other selectors*;
none tested objects **adjacent to the released core itself**. Scoring `r` of the core's own criteria
plus `a` generic pool criteria — free, since per-criterion satisfaction is already on disk — the
share of the size-matched class beaten is **0.1661 · 0.4184 · 0.7187 · 0.9215 · 0.9868** for
`r = 0..4`, monotone across all five levels. **Variance of admission explained: by `r` 98.6%, by
`a` 1.0%.** So admission is governed almost entirely by how much of the released core survives, and
adding generic criteria is nearly free. **Dropping one criterion of four still clears 92% of the
class**, so the definition does not collapse on perturbation: **the extension of 1 is a fact about
WHICH ARMS WERE BUILT, not about the definition's strictness.** Anchored at both ends without a free
parameter — d=0 reproduces R446's committed **0.9841** through an independent code path, and the
floor matches the class's own computed self-share (**0.2198**; same-rule fixed subset 0.2563). ⚠ This
measures the definition's **extension**, never its correctness: whether a neighbour is *really* a core
needs a standard outside this definition. *(R450)*

⛔ **BUT THE NEIGHBOURHOOD IS ENTIRELY A NEIGHBOURHOOD OF ONE POINT (R451), AND R450'S READING ABOVE
IS NARROWED.** Every admitted object in R450's grid shares criteria with the released core — `r > 0`
by construction — so the question that had never been asked is whether anything **disjoint** from it
has ever been admitted. Over every disjoint object on this site at m=4: the **only** hindsight-free,
content-driven one ever built is `gen`, at **0.0038**, while an **oracle** selecting from that same
disjoint space clears **1.0000**. ⭐ **The oracle is what makes the zero a measurement rather than
silence: the space demonstrably contains admissible disjoint objects, and no generator we have finds
one.** So *"the extension of 1 is a fact about which arms were built"* is **too kind** —
prompt-specific arms **were** built and they fail. ⚠ The verdict is threshold-swept, not defended:
over t ∈ {0.50…0.90} the candidate-core verdict is `W-BALL` at **every** cell, while the
all-objects verdict flips below 0.80 on `generic` (0.7154) — which is prompt-**blind**, hence a
within-family comparison against the reference class and near-circular. ⚠ **This measures our
GENERATORS, not the category:** nothing here shows a disjoint core does not exist. *(R451)*

⚠ **AND THE ORACLE THAT MADE THAT ZERO READABLE IS ITSELF LARGELY A FIXED SUBSET (R452).** The oracle
selects, per prompt, the best of 1,820 prompt-blind subsets — but its **winners concentrate**: the
effective number of distinct winners is **57.8** of 1,820 (**3.2%**), and one single subset wins
**33.57%** of all prompts, **611×** the uniform rate. Against a synthetic pool with *no* per-prompt
criterion structure, assembled through the identical combinatorics so overlap is reproduced, the
no-structure baseline gives **185.7** effective winners — so the real oracle is **3.2× more
concentrated** than no-structure produces, and per-prompt structure would push concentration the
*other* way. ⛔ **So `per-conversation` overstates what the oracle does: its ceiling is largely a
FIXED better subset of generic criteria plus max-of-1820 inflation** (`oracle 0.6610` vs
`best fixed 0.5618`, a difference that is a **DERIVATION** — a max of 1,820 draws exceeds the best
single draw by construction). R451's control stands; its *interpretation* narrows. ⭐ **And it
sharpens the circularity already flagged for `generic`:** if a fixed prompt-blind set sits near the
top of the prompt-blind class, clause ② is a **within-family ranking** where it was meant to be a
prompt-specificity test. *(R452)*

⚠ **AND CLAUSE ② IS PARTIALLY A WITHIN-FAMILY RANKING — MEASURED, AS A BOUND (R453).** The circular
version of this test (the *best* subset's share against a class containing it) is near 1 by
construction; the non-circular version holds out. Choosing the best fixed prompt-blind subset on half
the prompts and scoring it on the other half, it reaches **0.5773** [0.3188, 0.7456] on prompts it
was never chosen on — above the class floor **0.2198** and above a destroyed-objective g=0 at
**0.1327**, but below the released core's own half-sample bar of **0.8194**. On the floor→core scale
that is **59.6%** of the way. **So ② is not purely a prompt-specificity test, and the released core
still clearly beats the best generalising prompt-blind set.** ⚠ Every number here is at n=484; the
pipeline anchor at the committed n=968 reproduces **0.9841** exactly. ⭐ **R452's concentration is
CONFIRMED, not narrowed:** under R452's own selection rule the top subset's win share goes
33.47% (train) → **33.68%** [31.29%, 36.43%] (held out). *(R453)*

⭐ **AND THAT BOUND SATURATES IN POOL BREADTH, SO IT IS NOT A POOL-SIZE ARTIFACT (R454).** Drawing the
reference class from a random `W` of the 16 pool criteria and re-running the hold-out at each breadth,
the position of the best fixed set between floor and core is **0.4518 · 0.5817 · 0.6639 · 0.6296 ·
0.6337** for `W = 8, 10, 12, 14, 16` — a rise of **+0.1298** from W=8 to W=10 and then a plateau
(sd over W=12…16 = **0.0153**). **R453's W=16 measurement is in the saturated regime: more breadth
would not move it.** ⚠ What this does NOT say is that the fraction is breadth-independent — below
W≈12 it clearly is not. The anchor reproduces R453's **0.5773** exactly through an independent path.
⛔ **And it remains a property of THIS prompt-blind family**: exactly one family on this site has
breadth ≥ 16 (`genericpool16`; `full` is the rubric, `provenance_probe` covers 4 prompts), so
`n_prompt_blind_families_with_breadth = 1` and no resampling makes a second. *(R454)*
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

## ⛔ ON THE SECOND RELEASE THE DEFINITION ADMITS **NO CORE AT ALL** 2026-08-04 (R434)

R433 showed clause ②'s subject loses to a length heuristic. R434 asked the next question of all
**7** criterion arms scored on that release — prompt-specific, prompt-blind, three randomly
reassigned, evaluatively vacuous, and the wrong-conversation sham — on one shared population of
**7,342 interactions over 2,200 conversations**:

> **Clause ② admits 0 of 7. And 0 of 7 beat the length rule.**
> **7 of 7 are statistically indistinguishable from the blind reference** — including the
> prompt-specific core — and **7 of 7 are resolvedly worse** than a rule that reads neither the
> conversation nor any criteria (**0.5135**, against a best arm of **0.4590**).

⭐ **The emptiness is a measurement, not silence.** A synthetic oracle run through the *same* two
membership tests lands in both by a wide margin: **+0.5503 against the blind reference (MDE 0.0158)
and +0.4865 against the length rule (MDE 0.0169)**. Both tests can return TRUE; neither did.

⚠ **What this is not.** Evidence that no core exists. Seven arms is a census of what this campaign
built, not a sample of criterion-space, and R432's oracle over five of them reaches 0.7220.

**And the structural point needed no measurement at all.** ③ is a *provenance* restriction, ② a
*comparative* test against another criterion **set**, the size clause a *bound*. **Every clause
compares a core to other criteria; none requires it to beat anything outside its own family.** A
sufficiency clause would have to be stated against a **non-criterion reference** — a different
*kind* of clause from anything this definition contains. ⚠ And *"add a clause excluding the length
rule"* is a **category error**: the definition's domain is "a set of evaluation criteria", the
length rule is not one, and it was never admissible.
→ [`R434`](A24_what_the_definition_costs/R434_does_the_definition_have_a_utility_floor)

---

## ⭐ A SUFFICIENCY CLAUSE IS STATABLE — the bar saturates after **6** rules 2026-08-04 (R435)

R434 named the missing piece: a clause stated against a **non-criterion reference**. Two things had
to be checked before one could be written, and the first refuted a sentence of my own.

**① There are four non-criterion references, not one.** R427's `baselines_prejudge`
(`computed_before_arms: true`) holds **chance 0.4194 · first 0.4375 · longest 0.5096 · shortest
0.3362**. So the clause cannot be *"better than the longest-reply rule"* — that **names the
instance**, the failure this document's own ledger row is about. It must quantify over a **class**.

**② A maximum over a class climbs as the class grows — so does the bar mean anything?** Over a
family of **30** judge-free rules (14 response-set features × {max, min}, plus first/last), the
maximum **saturates at m\* = 6**: `BAR(|F|) − BAR(6) = +0.0232`, inside the **0.0234** that the
conversation bootstrap says one accuracy can resolve. Adding the other 24 rules moves the bar by
less than the data can see. **The bar is not an artifact of how hard anyone looked.** Lift over a
signal-free family of the same size is **+0.0715**, ~3× the data floor.

**So the clause is statable, and here it is as a predicate:**

> **④** …and scores better, under that same judge J, than **every rule computable from the response
> set alone**.

| the remedy's two questions | answer |
|---|---|
| an admissible object it **EXCLUDES** | **all 7 arms on the second release** (R434), including the published prompt-blind `generic`. Not vacuous. |
| a useful object it **ADMITS** | an oracle arm, **+0.4865** over the length rule (R434). Not impossible. |

⭐ **AND R436 MEASURED IT AT HOME. THE TWO RELEASES SPLIT.** Scoring the same 30-rule family on the
home release's own statistic — **A2**, agreement on the 6 pairwise comparisons, computed through the
same `cls` the arms use — the bar is **`min_ttr` at 0.4512** (*not* the length rule). Against it:

| release | do the definition's arms beat every criterion-free rule? |
|---|---|
| **home**, at the named judge J | **yes** — `oracle_k4` sits **+0.1824** above the bar (MDE **0.0211**), and **no 2B arm is resolvedly below it** |
| **second** (R434) | **no — 0 of 7**, all seven resolvedly worse |

**④ excludes 22 of 93 arms overall but 0 of 56 at the judge the definition names** — every exclusion
is an `_08b` variant, where R301 already measured clause ② admitting nothing. **So ④ is not redundant
in general; it is redundant *where the definition already works*** — silent when things are fine,
binding when they are not, which is what a sufficiency clause should look like. On this evidence it
earns adoption, and its value is stated precisely: **it would have caught the second release before
anything was generated.**

⚠ Two defects found on the way, both in this round's own instrument: the kill first tested
*"excludes some"* when the remedy's word is **admissible** — 22 of 93 would have passed while
excluding nothing the definition admits; and the round was **not reproducible** (`hash(str)` is
randomised per process, giving 25 then 22) until the seed was made stable. Two runs are now
byte-identical.
⭐ **AND R437 FOUND THE REASON TO KEEP ④ THAT IS STRONGER THAN "IT WOULD HAVE CAUGHT ONE RELEASE".
THE TWO BARS INVERT.** Clause ② and candidate ④ are two bars on the same accuracy axis, and their
order **flips between releases**:

| release | statistic (chance) | BAR2 — ②'s reference | BAR4 — best criterion-free rule | GAP = BAR4 − BAR2 | binds |
|---|---|---|---|---|---|
| **home** | A2 over 6 pairs (0.5000) | `random_k4_s0` **0.4945** | `min_ttr` **0.4512** | **-0.0416** vs MDE 0.0237 · RESOLVED | **②** |
| **second** | top-1 (0.4194) | `generic` **0.4497** | `length` **0.5135** | **+0.0637** vs MDE 0.0231 · RESOLVED | **④** |

**Neither clause dominates.** A definition carrying both carries a **max over two bars**, not two
independent tests, and which one does the work is a property of the release: **④ binds exactly where
② goes slack**, and R434 measured ② admitting nothing on the second release.

⚠ **SIGN ONLY.** The two GAPs are on different statistics with different chance rates and **must not
be compared in magnitude**. ⚠ And at home **both bars sit below chance** (A2's base rate is 0.5,
while the real arms reach 0.51–0.64) — which is *why* ② binds there: a reference nearer chance is a
**higher** bar than a systematically wrong rule. ⚠ What is NOT established: that the max of the two
bars is the *right* bar, or that no third regime exists where both go slack.
✅ **AND R438 ATTACKED THAT ONTOLOGY WHERE IT WAS MOST LIKELY TO BREAK, AND IT HELD.** A structural
claim resting on n=2 releases is attacked most cheaply from *inside* one: if the GAP's sign flips
across strata of a single release, "release" is not the variable. Splitting the second release by
n_responses — the one axis that exists, since **home has 4 responses by construction** and the two
releases share no stratifier:

| stratum | interactions | chance | BAR2 | BAR4 | GAP | MDE | |
|---|---|---|---|---|---|---|---|
| n=2 | 5,204 | 0.5000 | 0.5081 | 0.5600 | **+0.0519** | 0.0283 | RESOLVED |
| n=3 | 454 | 0.3333 | 0.4053 | 0.4449 | +0.0396 | 0.0948 | — |
| n=4 | 1,684 | 0.2500 | 0.2815 | 0.3884 | **+0.1069** | 0.0490 | RESOLVED |

**2 of 3 resolve, both positive** — the sign holds across strata where **chance itself moves from
0.2500 to 0.5000**, so both bars had every opportunity to cross and did not. ⭐ The GAP also **grows
with n**: `generic` decays toward chance as responses are added while the criterion-free rule does
not. ⚠ **One attack survived is one attack survived** — this does not establish the framing is
right, and whether a stratum flip and a release flip are one phenomenon needs a shared axis that
does not exist. ⚠ Selection inflation from re-choosing the best rule per stratum was **measured**
(+0.0000 / +0.0022 / +0.0000), not assumed away.
→ [`R435`](A24_what_the_definition_costs/R435_is_a_sufficiency_clause_even_statable) ·
[`R436`](A24_what_the_definition_costs/R436_does_clause_four_exclude_anything_at_home) ·
[`R437`](A24_what_the_definition_costs/R437_do_the_two_bars_invert_between_releases) ·
[`R438`](A24_what_the_definition_costs/R438_does_the_gap_flip_inside_one_release)

---

## What this definition cannot claim

| | |
|---|---|
| **"a core", unindexed** | the admitted set is **empty at the second judge**; only *"a core under J"* is licensed — and J is named by R367's rule, not chosen |
| **a count of admitted arms** | the set moves within **0.25 MDE** (R332) and with the reference's percentile (R354) |
| **that its three clauses each test something** | one excludes nothing, one is judge-emptied, one is irreplaceable |
| **an unindexed size** | at 0.8B top-k loses to a size-matched blind set at **6 of 7** sizes (R362) |
| **that it works on responses it was NOT scored against** | **unresolved against a fair floor** — see the transport note below (R368, R370) |
| **transfer to another criterion pool** | every level here is a fact about **this 16-criterion pool** (R331) |
| **a prompt-SPECIFIC core anywhere else** | ⭐ **the route is now WALKED, not open.** R427 measured clause ②'s *comparator* on the second corpus and it **loses to a longest-reply rule**; clause ② itself is untestable there because its *subject* — a prompt-specific core — does not exist. **Requires: generating criteria from the conversation alone on a rubric-less corpus**, a job with its own assumptions, not a re-run. ⭐ **R432 gated that job at zero GPU and it is worth running:** over the five criterion texts already scored, the best single arm ranks the human's choice first on **0.4527** of interactions while *some* arm does on **0.7220** — headroom **+0.2693** against a floor of **0.0084**, and **the oracle clears the judge-free length rule (0.5096) by +0.2124**. So a prompt-specific arm that fails would be failing *about the criteria*, not about the instrument. ⚠ The oracle chooses **with hindsight, using the answer**: it is an upper bound, and the generated arm's bar is **0.5096**, never 0.7220. ⛔ **R433 RAN IT. `W-LOSES`.** A core generated from each conversation alone — clause ②'s subject, absent from every previous cross-release number — scores **0.4590** against a judge-free longest-reply rule at **0.5135** on the same 7,342 interactions: **-0.0545 [-0.0706, -0.0377] against its own MDE of 0.0235, resolved**, and resolved under the other weighting too (-0.0604 [-0.0781, -0.0418] vs 0.0258). **And clause ② is not even SATISFIED resolvedly:** its own statement is `core > neutral`, and that gap is **+0.0093 [-0.0008, +0.0186] against an MDE of 0.0140** — the interval contains zero. **So the clause names a bar its subject cannot be shown to clear, while a rule reading neither conversation nor criteria beats them both.** ⚠ The conversation-match itself buys **less than 0.0176**: the wrong-conversation sham costs only +0.0050. ⚠ What this does NOT establish: that no generator could. R432's oracle over five existing texts reaches 0.7220, so the ceiling is far above this one greedy decode — **the failure is this generator's** |
| **a k-free criterion share** | the criterion's share of satisfaction variance is **not scale-free in k**, and the cells compared differ (15 vs 4). **Requires: matched k across every cell**, which the home rubric's per-prompt criterion counts do not allow |
| **position randomisation** | unchanged in kind but now measured: the release carries **storage order only**, and R427's `first` baseline indexes that, never what a human saw. **Requires: a presentation-order field** |
| **a causal effect of response length on the human choice** | the target is length-loaded (tau **`+0.2113`**), and every test of it here is **nuisance-matching on a covariate**, never an ablation. **Requires: an intervention on response length** |
| **the MAGNITUDE of random-criteria scatter** | two random draws differ **4.0×** their own resolution in how they align with the hand-written arm — a **direction**, established. **Requires: many draws**; three cannot estimate the sampling distribution of a spread, and saying otherwise would be the bound-versus-point error again |
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

⚠ **This measures clause ②'s FLOOR, not clause ②** — see the next section.

### ⭐ `randblind` and `vacuous` have landed (2026-08-04, R427 + R429) — and the content contributes nothing

They were queued to decide whether the criteria's *content* contributes anything. It does not, and
**neither arm moves the result above**:

| arm | what it removes | accuracy | `generic` − arm | its MDE | verdict |
|---|---|---|---|---|---|
| `generic` | — (the comparator) | **0.4374** | — | 0.0171 | the floor |
| `randblind_s0` | the criteria↔prompt assignment | 0.4397 | **−0.0024** | 0.0189 | inside noise |
| `randblind_s1` | " (seed 1) | 0.4396 | **−0.0023** | 0.0217 | inside noise |
| `randblind_s2` | " (seed 2) | 0.4383 | **−0.0010** | 0.0182 | inside noise |
| `vacuous` | **all evaluative content** | 0.4276 | **+0.0097** | 0.0154 | inside noise |

**Stripping every evaluative word changes neither the accuracy nor which responses get picked.**
Three randblind seeds land *above* `generic`, not below — so the criteria's *assignment to a
prompt* carries nothing either, and the direction is the unflattering one in all three.

⛔ **And the pick-level agreement says where what remains lives.** Over ten arm-pairs,
`generic|vacuous` has the **highest excess agreement over its own marginal-matched null**, above
every randblind–randblind pair. R429 asked whether that rank is a *measurement* or an *ordering*
and ran the paired cluster bootstrap the ranking never had:

> **Δ(rank 1 - rank 2) = +0.0234 [+0.0103, +0.0364], p = 0.0003, surviving BH(q=0.10) over all 45
> ordered comparisons.** Controls: placebo Δ(P,P) = 0 exactly · plant at g=0.5 resolves and at
> g=1.0 does not · seed spread 0.00025 across 3 seeds.

<!-- ⚠ THE THREE NUMBERS ABOVE AND THE MEAN GAP BELOW USE AN ASCII HYPHEN, NOT THE TYPOGRAPHIC
     MINUS U+2212 THIS DOCUMENT OTHERWISE PREFERS. That is deliberate and it is load-bearing:
     `definition_matches_the_record.py` compares the captured string to the artifact's own
     `f"{x:+.4f}"`, which emits ASCII. With U+2212 the regex matched nothing and the gate FAILED
     LOUDLY -- which is the correct behaviour and is why this comment exists rather than a silent
     normalisation step. A gate that quietly folded the two characters together would also fold
     together every other pair of glyphs that look alike, and that is how a document drifts from
     its record while the gate keeps printing PASS. -->


**So what the arm responds to survives deletion of the criteria's meaning** — the axis is the
criteria's *topical phrasing*, not their evaluative content. This is a **stronger** statement than
the randblind comparison alone supports, and it **changes the reason**: randblind says *"the
prompt-matching does nothing"*; vacuous says *"the meaning does nothing."*

⚠ **Only ranks 1–3 of that grid are quotable.** R429 measured R427's permutation null against the
analytic expectation of R427's own construction — **all ten gaps carry the same sign, mean -0.0148
against a one-draw band half-width of 0.0104, only 2 of 10 inside** — and attributed the
disagreement to the **null construction**. ⛔ **R430 overturned that attribution the same day.**

The R427↔R429 comparison changed **two** things at once, and the decomposition names which one
carries the gap:

| | R427 | R429 |
|---|---|---|
| aggregation | **CONV** — mean over conversations of per-conversation means | **INTER** — pooled over interactions |
| null | **PERM** — one realised within-stratum permutation | **ANLY** — the closed-form expectation |

Reproducing R427's committed per-pair null from all four cells: **CONV/PERM 8 of 10 · CONV/ANLY 9
of 10 · INTER/PERM 2 of 10 · INTER/ANLY 2 of 10.** *Both* nulls reproduce R427 when aggregated by
conversation and *neither* does when pooled. **The two nulls agree to ~0.002; the two weightings
differ by ~0.013.** The gap is the **aggregation weight**, not the null.

**What survives unchanged:** rank 1 is `generic|vacuous` under *both* weightings, and its separation
from rank 2 resolves under both — **CONV +0.0226 [+0.0083, +0.0374] p=0.0027** and **INTER +0.0234
[+0.0107, +0.0367] p=0.0003**. The number is weighting-dependent and must be quoted with its
weighting, which R429 did not do.

**Where the ordering actually breaks, measured per axis instead of subtracted:** changing the
weighting alone moves **2 of 10** ranks (positions 9 and 10). Redrawing the *same* permutation null
30 times at fixed weighting moves a **median of 4** (IQR 2, range 0–6) — **positions 1, 2 and 3
never move in any draw; position 4 moves in 10 of 30.** So the mid-table ordering is
permutation-draw noise, and R429's own *"ranks 5–10"* named the wrong boundary and the wrong cause.
**Which null is correct remains UNVERIFIED** — that needs a corpus with known truth.

⭐ **And the weighting gap is 10× smaller on the quantity anyone reports.** R430's ~0.013 is the
CONV/INTER difference **on the null**. On the **excess** — agreement minus null, which is what every
round quotes — R431 measures it at **at most 0.0050** across all ten pairs, because reweighting
moves the agreement and the null *together* and the difference largely cancels. That is consistent
with R430's two headline Δ differing by only **0.0008**, and it is why the weighting choice does not
threaten any excess number in this document. **Neither weighting is size-confounded:** **0 of 30**
within-stratum size-association cells clear BH(q=0.10), and the apparent n=2 association at
rho ≈ **-0.19** is a granularity artifact the permutation null carries too (**-0.2116 ± 0.0203**,
observed **+1.21 sd inside it**). ⚠ **What R431 could not explain:** after standardising the stratum
mix the gap is inside its own floor for only **7 of 10** pairs — short of the 8 pre-registered — and
for some pairs standardisation makes it *larger*. Those 3 pairs are an open residual, and the
world they landed in was not among the three the round declared.
→ [`R429`](A24_what_the_definition_costs/R429_is_the_tightest_pair_a_resolved_claim) ·
[`R430`](A24_what_the_definition_costs/R430_is_the_null_gap_the_null_or_the_weighting) ·
[`R431`](A24_what_the_definition_costs/R431_is_the_excess_statistic_size_confounded)

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
