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

⭐ **AND ② CAN BE STRENGTHENED — THE FIRST REPAIR IN THIS ARC RATHER THAN A NARROWING (R455).** Since
most of what ② demands is reachable without reading the prompt, the fix is to strengthen its
**baseline**: require a core to beat not a size-matched member of the prompt-blind class but **the
best prompt-blind set that GENERALISES**. Cross-fitted over 10 folds so no prompt's baseline is
chosen using it, the released core clears that stronger bar by **+0.0141**, CI
**[+0.0047, +0.0236]**, resolved at all three seeds with a seed spread of 0.0001. ⚠ **That is
1.04× its own MDE — the edge of what this design can see, so the INTERVAL is the claim and not the
point.** The controls are what make it readable: an oracle clears the same baseline by **+0.1034**
(so the design has power), a wrong-prompt sham **loses** at −0.0558, and — decisively — the
prompt-blind arm `generic` sits at **−0.0020 [−0.0086, +0.0045]**, *unresolved*, so this separates
*the core is good* from *anything beats a cross-fitted pick*. ⭐ **And an IN-FOLD baseline gives
+0.0011**: the naive design finds nothing, so cross-fitting did not inflate this effect, it revealed
one that an unfairly strong in-sample baseline was hiding. **R453's 59.6% therefore stops being an
objection to the definition** — it remains a true statement about how weak the original baseline was.
⚠ Stated against THIS prompt-blind family; exactly one with breadth exists. *(R455)*

⛔ **AND THAT RESOLUTION CLAIM NARROWS TO A BOUND — THE DATA DID NOT HAVE MORE TO GIVE (R456).** Every
A2 above uses 3 annotator draws while the release ships a median of 16 on this population (min 4, mean
16.1, max 46, **15,593** total). Recomputing the strengthened gap across the whole annotator ladder
`m = 1,2,3,5,8,16,ALL`: the gap is **positive in 7 of 7** cells but clears its own MDE in only
**6 of 7**, failing at **m=16** (gap **+0.0095**, MDE 0.0104, ratio 0.92). ⭐ **The measured exponent
is α = 0.208, not the 0.500 that √ would give** — the MDE falls just **1.19×** from m=3 to all
annotators, so **the between-prompt spread is not annotator noise and no annotator count resolves
this gap cleanly.** The honest statement is therefore a bound: the released core sits above the best
generalising prompt-blind set by **+0.0095 to +0.0191**, sign stable across every specification,
resolution not. ⭐ The oracle clears the same baseline at **8.5–11.6×** its MDE at every m, which is
what makes this a measurement rather than silence: the design can resolve a large gap throughout and
simply cannot resolve this one. *(R456)*

⭐ **AND THAT BETWEEN-PROMPT VARIANCE IS SIGNAL, NOT NOISE (R457) — SO ②'s ADVANTAGE IS NOT UNIFORM
ACROSS PROMPTS.** Splitting each prompt's annotators into two disjoint halves with the baseline held
fixed, the *value of having the right criteria on a given prompt* — `A2(core,p) − A2(sham,p)`, which
cancels both the shared baseline and the shared prompt-difficulty term — replicates at
**ρ_full = 0.8812**, CI **[+0.8460, +0.8946]**, seed sd 0.0084. ⛔ **The naive version of this test is
contaminated and its own sham control says so:** `A2(arm,p) − A2(base,p)` inherits reliability from
the baseline term that every arm shares, and on that statistic the **sham scores 0.8913 — HIGHER than
the core's 0.8355** — so it cannot distinguish *the core's advantage is prompt-structured* from
*prompt difficulty is reliable*. ⭐ **What this licenses is a per-prompt stratification with a
measured ceiling of 0.8812**, subject to a both-arms check on every covariate; ⚠ what it does NOT
license is any claim about *which* prompts, and the covariate R456 proposed — annotator agreement —
is **inadmissible**, because it raises both arms of a bounded difference and manufactures a gradient.
*(R457)*

⛔ **AND NOTHING ON THIS SITE PREDICTS WHERE THAT ADVANTAGE LIVES (R458) — SO THE DEFINITION GAINS NO
SCOPE LINE.** Cross-fitting a ridge from **17 target-free features** (core/sham/pool satisfaction
means, sds, ranges, per-response spreads and k, plus response-length mean/sd/range) onto R457's
arm-specific gap gives out-of-fold **R² = +0.0384** — **4.4%** of the 0.8812 ceiling. Per block:
core-only +0.0135, sham-only +0.0170, pool-only +0.0167, lengths-only **−0.0040**. ⭐ **The positive
control makes that a measurement rather than silence: a planted `d + noise` column is recovered at
R² = +0.9170**, 24× the observed value, and a pure-noise column does not move it. ⭐ **And the
both-arms diagnostic caught §4's trap in the act — 8 of 17 features raise BOTH arms**, with
`core_range` at **+0.4520 / +0.3676** against the two arms but only **+0.0636** against their
difference: a naive stratification on satisfaction spread would have shown a large arm gap produced
entirely by both arms rising. **So clause ②'s advantage is prompt-specific, replicable at 0.88, and
unexplained at 0.04 by everything the release yields without a second instrument** — structured, but
not by anything on this site. ⚠ Scope is that named feature set, not "observables"; a semantic
representation of the prompt is the next instrument and is deliberately outside this round. *(R458)*

⭐ **AND THAT RELIABILITY IS NOT A PARTNER ARTIFACT (R459).** R457's estimand subtracts a sham that
applies **another prompt's** criteria, and the partner is **fixed per prompt** — so an annotator
split counts partner variance as perfectly reliable while it is no property of the prompt. Tested
against a **partner-free** estimand (`generic` is a single fixed criterion set, verified in-run at
**1** distinct criterion-index tuple): `core − generic` replicates at **0.8363**
[+0.7684, +0.8474] against `core − sham`'s **0.8812** — **Δ = −0.0449**, inside the ±0.15 band, with
R457's committed value reproduced **exactly** through an independent path. ⭐ **And the component
table shows why the paired design works at all: `d_sham` (0.8812) is MORE reliable than either of its
parts (core 0.8378, sham 0.8593)** — a difference exceeding both its components is what happens when
their noise is positively correlated and cancels in the subtraction. ⚠ **This does NOT decompose
partner variance** — impossible here, since the partner is fixed per prompt — it shows the conclusion
survives without a partner at all. *(R459)*

⛔ **AND BOTH OF THOSE NUMBERS ARE OUTLIERS — R459 INHERITED THE DEFECT IT WAS BUILT TO TEST (R460).**
R459 answered an n=1-draw objection with `core − generic`, itself **one** fixed prompt-blind set.
Every such set is a row of the C(16,4) matrix, so a **census of all 1,820** is free. The reliability
of `core − F` across that whole population: min **0.8226**, p25 0.8419, median **0.8486**, p75 0.8544,
max **0.8675** — **IQR 0.0125**. ⛔ **R459's `generic` sits at 0.8114, percentile 0.000 — below every
one of the 1,820 — and R457's sham at 0.8726, above the census maximum.** The entire population lies
**between** the two numbers whose agreement R459 read as evidence, and
**corr(ρ, comparator strength) = −0.7995**: reliability rises as the comparator weakens, because a
weak comparator contributes less signal variance and the difference is dominated by the core's own
reliable variation. ⚠ **What this does NOT overturn: the per-prompt advantage is reliable — the census
MINIMUM is 0.8226, so every comparator agrees.** What it narrows is the number and its reading: the
honest quantity is the census IQR **0.8419–0.8544**, and any single-comparator figure must name its
comparator. *(R460)*

⭐ **AND THAT CLASS DEFECT DID NOT REACH THIS DOCUMENT (R461).** Since a difference is a joint
statement about the arm and its comparator, every difference-based claim here must name what it was
measured against. Rather than grep for them — **a grep is a measuring instrument with no positive
control** — the comparator is now **DECLARED per anchor and checked** by
`assurance/comparator_scope.py`, with the containment window **swept rather than chosen**:
**18** declared difference-anchors, **0 flagged** at windows 400/800/1600 and **3** at the tightest
200 (`r456_gap16`, `r456_ratio16`, `r460_iqr`) — **a window artifact, and the sweep is the only thing
that distinguishes it from a real defect.** The window mechanism is positive-controlled on a
comparator planted at a known distance (flagged below it, passing above it, at both 300 and 1200
chars), and a declared-absolute claim is never flagged. ⚠ **Declaration coverage is 27 of 330 anchors
(10.3%)** — ⛔ a SELF-REFERENTIAL count: this sentence lives inside the document the
gate checks, so it goes stale the moment an anchor is added, and it did, one commit after R461 ran; the 230 undeclared are **not passes**, and that count measures the instrument's coverage
rather than any property of this document. **The product of that round is the enforced instrument: a
future difference-anchor cannot be added without naming its comparator.** *(R461)*

⭐ **AND THE OLDEST BLOCK IS CLEAN TOO (R462) — declaration coverage now 80 of 330.** The proposed
ordering for the remaining work was *"oldest first, because old numbers have survived the most
rewrites"*; nothing measured that, and every anchor defect this campaign's value-gate has caught was
in a **newly written** anchor. Declaring the whole **R442–R454** block — the one called riskiest —
gives a flag rate of **0 of 32** at windows 400/800/1600, against the recent block's **0 of 18**;
at the tightest window 200 the flags are **all** from the recent block and **none** from the old.
**The ordering is refuted, and doing the work was the test.** ⚠ This does not establish that the
remaining **181** undeclared anchors are clean — undeclared is not a pass — and it leaves the correct
ordering **open**, since the only proposed basis has been eliminated. *(R462)*

⭐ **AND A THIRD BLOCK IS CLEAN — 71 DECLARED DIFFERENCES, 0 FLAGGED (R463); coverage 154 of 265.**
The ordering proposed to replace refuted-age was *"count, per anchor, how many clause-sections cite
its round"*: measured, `sections_citing(round)` is **min 1, max 1 over 21 rounds** — **flat by
construction**, since each round's paragraph lives in exactly one section. **Two orderings proposed,
both eliminated**, so the remaining order is **arbitrary and is stated to be arbitrary** rather than
dressed in a third story; the block declared was simply the next contiguous one. Across three
independent blocks — R430–R441 (21), R442–R454 (32), R455–R462 (18) — **0 flagged at windows
400/800/1600**, with 6 at the tightest 200 split 3/0/3 between the outer blocks. ⚠ This says nothing
about the **111** still undeclared; undeclared is not a pass. ⭐ **A separate fact the census gives:
clause ② carries 19 of the 21 round-markers and clause ③ carries 2** — 90% of this campaign's
attention went into one clause. *(R463)*

⭐ **AND CLAUSE ① IS UNEXERCISED, NOT DECORATION (R464).** The per-clause table records ① as excluding
**0 of 41** arms, and §4's remedy reads *"if nothing you have built is excluded, the clause is
untested decoration."* ⚠ **But "excludes nothing BUILT" and "excludes nothing CONSTRUCTIBLE" are
different claims, and only the second makes a clause vacuous.** Building objects designed to fail ①
from each prompt's own rubric: the adversarially **worst** rubric subset is excluded at
**−0.2779** [−0.2914, −0.2651] against an MDE of 0.0190, while the released core sits at
**+0.0797** [+0.0677, +0.0915] and is not excluded, and a **random** rubric draw — a sample from the
very process ① compares against — sits at **+0.0088** with a CI straddling zero, exactly as a
correctly-calibrated boundary requires. ⭐ **So ① is a real predicate with a real extension, and
`0 of 41` is a fact about the ARM SPACE rather than about the clause.** ⚠ What it does not establish
is that any real *generator* would produce such an object: the excluded arm was built adversarially,
on purpose, which is both the point of the test and its limit. *(R464)*

⭐ **AND ③ IS A PREDICATE OF A DIFFERENT TYPE FROM ①②④ (R465) — THE FORMULATION MIXES TWO KINDS OF
CLAUSE.** ③ is derived from *which selector built the arm*, so it is invariant under every measurable
property of the object: criteria, satisfaction scores, A2. Constructing the collision directly — a
label-**reading** selector against a label-**free** one at matched k — they emit **exactly the same
criterion set on 9 of 967** prompts where a genuine choice exists (rate **0.0097**, seed spread
0.0018), with **identical A2 to machine precision** on every collided prompt, while ③ excludes one and
admits the other. ⚠ Against a label-free/label-free baseline of **0.0062** that rate is **not a
resolved difference and does not need to be**: the estimand is **existence**, and one collision
suffices. The single prompt whose rubric admits exactly one subset collides at 1.0000 by construction
and is excluded as a **DERIVATION**. ⭐ **What this costs the formulation: ①, ② and ④ can be checked on
an object you are handed; ③ cannot** — a reader given a criterion set can verify three of four clauses
and must be given the construction history for the fourth. That is not a defect to remove but a fact
the definition must state, because four uniform-looking predicates silently promise a check one of
them cannot deliver. *(R465)*

⛔ **AND ③'s TWO INSTRUMENTS RANGE OVER DISJOINT ID SPACES (R466) — SO "`coval_core` SURVIVES ③" IS
UNVERIFIED, NOT REFUTED.** Running `clause3_as_written.partition` over every arm with a satisfaction
file gives **39 EXCLUDED, 43 ADMITTED, 19 UNKNOWN** — and **`coval_core` is UNKNOWN**: the object the
definition was written from cannot be classified by the instrument that implements ③. The document
resolves that with containment (**0.0779**), but ③ as derived forbids consuming the **rankings** and
the **annotator scores**, while containment measures copying of the rubric's **text**. Measured:
rubric-text ids **986**, ranking ids **1078**, **intersection 0** — the two instruments cannot be
joined on disk without a mapping, and none was used. **Containment is therefore not a weak proxy for
③; it is computed over a population that does not intersect the one ③ quantifies over.** The decisive
construction — a label-reading arm with zero verbatim overlap — is consequently **unrunnable**, and is
recorded as **UNVERIFIED, never OVERTURNED**. ⚠ The containment instrument itself is sound: it
reproduces its anchor (**0.0778** vs 0.0779), its cross-prompt floor is **0.0000** and a verbatim copy
scores **1.0000**. **What is defective is the join, not the clause** — and **19 arms remain UNKNOWN
under ③, the paradigm case among them, so the definition still owes a third verdict.** *(R466)*

⚠ **AND THE REASON IS NOT THE ONE R466 GAVE (R467).** R466's *"cannot be joined"* invited the far
larger reading that the two files describe **different conversations** — and an early version of R467
printed exactly that. **It is false.** Record 0 of each file is manifestly the same exchange; the
rubric file simply stores a **different wording** (*"should people stop **eat** beef"* against
*"…stop **eating** beef"*) and interleaves metadata tokens. **The files describe the SAME
conversations in DIFFERENT TEXT**, so neither an id join (intersection **0**) nor an exact-text join
(**0.0000** after the schema was corrected) bridges them, and a fuzzy join is excluded because a
threshold would decide the question rather than measure it. ⛔ **What caught the false verdict was
that the NEGATIVE control returned the same 0.0000 as the result** — *when a result equals its own
null it is silence* — and the missing control was a **cross-file** case with a known answer: the
within-file uniqueness checks passed at **1.0000** both ways and could not see a normaliser that was
merely *incomparable across files*. **R466's UNVERIFIED therefore stands, for a better reason, and
the campaign-wide claim is dead.** *(R467)*

⛔ **AND BOTH OF THOSE CONCLUSIONS WERE OVER-STATED — THE JOIN EXISTS (R468).** R466 and R467 both
joined on **conversation** text, which the rubric file stores degraded. The **criterion** texts are
short exact strings carried in *both* id spaces, and joining on them needs no threshold: **coverage
1.0000 (968 of 968), uniqueness 1.0000, 0 ambiguous.** ⭐⭐ **And it is validated on a channel it was
not built from** — built from criteria, checked on conversations: joined pairs are **0.8811** similar
against **0.2859** for random pairs, so the validation cannot be an artifact of the construction. Both
prior numbers are reproduced as anchors before anything is narrowed (id intersection **0**;
conversation-text coverage **0.0000**). ✅ **So R466's UNVERIFIED is now DECIDABLE: ③'s two instruments
can be pointed at one population, and the 19-arm UNKNOWN region can be revisited.** ⭐ **The pattern
across three rounds is the lesson: a failed join licenses "this join failed", never "no join exists"**
— the second quantifies over every possible key, and neither round enumerated one. ⚠ 18 rubric-space
records have no ranking-space partner (986 > 968) and are reported rather than explained away.
*(R468)*

⛔ **AND WITH THE JOIN IN HAND, CONTAINMENT TURNS OUT TO BE CONSTANT ON ③'s OWN PARTITION (R469) — SO
IT CANNOT IMPLEMENT ③ AT ALL.** Every selector in `select_core.py` draws from the prompt's own rubric,
the ③-excluded ones and the ③-admitted ones alike, so containment is ~1.0 for both by construction —
a **DERIVATION**, confirmed by measurement rather than asserted: **EXCLUDED 0.9744** (n=39, sd 0.1581)
against **ADMITTED 0.9767** (n=43, sd 0.1507), **separation −0.0023**. The **UNKNOWN** class sits at
**0.0002** (n=7), which is the mechanism made visible: those arms are the ones *not* built by a rubric
selector, so neither instrument can separate them and **the arms the two instruments both fail on are
the same arms**. ⭐ **This converts R466's UNVERIFIED from "not yet decided" into "NOT DECIDABLE BY
THIS INSTRUMENT", and makes the definition's third verdict PERMANENT for the 19-arm UNKNOWN region
rather than provisional.** Controls: the core reproduces **0.0778** vs its committed 0.0779, the
cross-prompt floor is **0.0000**, and `full` — every rubric criterion — returns **0.9999**, without
which a low number would be silence. ⚠ It rules out **one** instrument; another would need its own
round, and this round says so rather than generalising. *(R469)*

⛔ **AND THEREFORE THE EXTENSION IS AN INTERVAL, NOT AN INTEGER (R470).** Of the **5** arms admitted by
①∧②∧④, four — `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` — are **EXCLUDED** by
③, and **`coval_core` is the sole UNKNOWN**. So the extension is **0** under unknown-as-excluded,
**1** under unknown-as-admitted, and **0 confirmed + 1 unverified** under the three-valued reading.
**The committed value of 1 corresponds to unknown-as-ADMITTED — a convention this document has never
named** — and its justification (R443's containment argument) is the instrument R469 showed to be
constant on ③'s partition. ⛔ **The choice is not innocent: the only arm it admits is the object the
definition was written from, and under the other reading the extension is EMPTY.** ⭐ **The honest
form is the interval [0, 1] with the convention named, and the three-valued reading is the one this
campaign's own proxy ledger requires**, since UNVERIFIED must never be folded into EXCLUDED or
ADMITTED — which is what has been happening. ⚠ This does not say the definition is wrong; it says its
extension has never been *measured*, only **counted under an invisible convention**. *(R470)*

⛔⛔⛔ **AND THE RELEASE'S OWN DATASET CARD DECIDES ③ — AGAINST THE OBJECT THE DEFINITION WAS WRITTEN
FROM (R475).** `data/DATASET_CARD.md`, 432 lines, **opened for the first time in round 475**, says in
its own words: *"it aims to **select up to four rubric items with the highest average ratings** that
remain compatible with each other and do not repeat the same idea"*, having *"first rewrit[ten] all
rubric items to have positive weight"*. **That is `topabs_k` / `topw_k`, and both are in `W_READERS`.
So clause ③ as derived by R444 EXCLUDES `coval_core`, and the extension is 0 under EVERY reading —
not the interval [0, 1] committed one round earlier.** *(R475)*

⭐ **AND R469 WAS RIGHT ABOUT THE INSTRUMENT AND WRONG ABOUT THE WORLD.** The released core items
carry **only `criterion`** — no `rubric_item_id`, no `scores` — so the rewrite severs the link to the
rated items and **no instrument on this site can recover the provenance**. R469's measurement was
sound. Its conclusion, *"③ is not decidable here"*, quantified over the wrong domain: **③ is a
provenance predicate, and provenance is established by a RECORD, not by a measurement.** The release
publishes the record. **Four rounds — R466, R469, R470, R471 — reasoned about ③'s undecidability
while the answer sat in an unopened file in `data/`.** *(R475)*

⭐ **AND THE OBJECT WAS MADE TO JUDGE THE CARD, NOT ONLY QUOTED FROM IT.** Matching each core item to
its nearest `coval_full` item within the same prompt and reading off that item's weight percentile:
the core sits **27.1%** of the way from chance to a pure top-4-by-`w` selector, and **21.5%** of the
way to a pure top-4-by-`|w|` one — **both LOWER BOUNDS**, because the matcher recovers the source text
at only `sim ≈ 0.49` and imperfect matching attenuates toward chance. All four controls hold: the
verbatim plant is recovered to within **0.01** of a **measured** ceiling (0.8399 vs **0.8437**; 0.8462
vs **0.8495**), a verbatim *random* plant lands at **0.492–0.502** so the control could have failed,
the cross-prompt null is **0.486–0.523**, and the file-index placebo is null. *(R475)*

⚠ **AND THE CARD'S STATED MECHANISM IS THE ONE THING THE OBJECT DOES NOT CONFIRM.** The card says the
process rewrites every item to positive weight *before* ranking, which predicts `|w|` should track the
core more closely than `w`. **It is the other way round — 27.1% on `w` against 21.5% on `|w|`.** So the
negation step exists but does not govern selection: the core tracks items annotators rated **highly**,
not items they rated **strongly**. **The card is right that ratings are consumed and wrong about which
functional of them.** *(R475)*

⭐⭐⭐ **THE ONTOLOGY SHIFT, AND IT IS THE LARGEST OF THIS CAMPAIGN. A definition of "core" whose
extension excludes CoVal-core is not a definition of CoVal-core.** Clause ③ was derived by R444 from
`corebench/select_core.py` — **this campaign's own arm-generation code** — and then applied to an
object built by a pipeline that **is not released** and that the card describes as consuming exactly
what ③ forbids. One of two things must now give: **either ③ is too strong** and should forbid only the
prompt's *rankings* (`TARGET_READERS`) while permitting its *ratings*, **or the campaign has spent 32
rounds defining an object other than the one it measures.** ⛔ **This is not a repair that can be made
by choosing the convenient branch** — the two differ in what "core" *means*, and R475 does not
adjudicate them. *(R475)*

⭐⭐ **AND THE GAP THAT LEAVES ②∧③ UNDETERMINED HAS REAL PER-PROMPT STRUCTURE (R494–R497).** Settling
②∧③ needs a better ③-admissible arm than `gen` (p32.6). Four candidate explanations for its deficit
were tested and four died. **Repetition:** `gen` repeats phrasings up to 29× against `coval_core`'s
near-total uniqueness, but stratifying prompts by that repetition gives a gradient of **−0.0357** in
`gen` and **−0.0393** in `generic` — whose criteria are identical on every prompt and therefore cannot
repeat differentially, so the gradient is prompt difficulty. **Discriminativeness across arms:**
`corr(mean SD, A2)` = **−0.4758** over 7 arms, and dropping `topvar_k4` alone flips it to **+0.4819**
— one arm, built to be extreme on the predictor, owns the sign. **Discriminativeness paired:** at
n=968 the correlation with the deficit is **+0.0013** [−0.0640, +0.0608] while the same predictor
tracks `generic`'s score at **+0.2577**, so the control fires and the null is evidence. **Length:**
`gen` writes **9.34** words against `coval_core`'s **13.25**, and correlates with the deficit at
**+0.0319**, CI spanning zero. *(R494, R495, R496)*

⭐⭐⭐ **AND THE ADMISSIBLE SIDE IS NOT A WEAK FIELD — IT IS ONE ARM (R502).** Counted from the
criterion **text** (`core_<arm>.json`, 968 prompts each) rather than from the scores, the
③-admissible population is **1** prompt-responsive full-coverage arm (`gen`), **6** prompt-varying
but *random* draws, **2** prompt-blind fixed sets and **3** partial-coverage arms — against **14**
prompt-varying arms on the ③-**excluded** side. ⭐ **So "p32.6 of 23, with 22 at p0.0" was never a
field of weak candidates: it is one candidate and a floor**, and the 22 at p0.0 are random draws and
fixed sets behaving exactly as they should. **`UNDETERMINED` keeps its value and changes its scope —
the definition is not unresolvable; the SITE ships one ③-admissible prompt-responsive generator.**
That is a property of the release, and it names what a second site must supply, which no analysis
here can produce. ⚠ Bound: *responsive* vs merely *varying* is assigned from construction knowledge,
not measured — measuring it needs the generator, not its output. *(R502)*

⭐⭐⭐ **AND THE FIFTH CANDIDATE — THAT THERE IS NOTHING TO EXPLAIN — DIED TOO, WHICH IS THE ONE THAT
MATTERS.** Three large between-arm differences with three null within-prompt correlations invites the
conclusion that the deficit is a constant offset. It is not: mean **+0.0311**, observed sd **0.1388**
against a **measured** noise floor of **0.0353**, implied true sd **0.1342** — **3.8× the noise** — and
**test-retest reliability +0.9355** across independent held-out-annotator draws. ⛔⛔ **RETRACTED BY R499 — see below; two arms with NO functional difference score higher.** ⭐ **The floor is
supplied by the instrument itself**: A2 samples a held-out annotator per prompt, so a second seed is a
second draw of the same quantity. **`gen` does not lose uniformly — its deficit's spread is 4.3× its
own mean, it wins on some prompts and loses badly on others, reproducibly.** *(R497)*

⚠ **SO THE SEARCH IS VALIDATED, NOT EXCUSED.** There is a large, stable, per-prompt target; four
predictors are simply wrong about it. ⛔ **And the design that keeps suggesting itself — "look at the
prompts where `gen` loses most" — is selection on the outcome (Oldham 1962), proposed twice and killed
twice before running.** *(R496, R497)*

⛔⛔⛔ **AND THE WHOLE THREAD RESTED ON A STATISTIC THAT CANNOT TELL A MECHANISM FROM TWO ARBITRARY
CRITERION SETS (R499).** `random_k4_s0 − random_k4_s1` — two seeds of one random procedure, no
functional difference of any kind — returns **r = +0.9581, true sd 0.1553, 4.76× noise**, higher on
every statistic than any real pair. Against a null of three such pairs (r ∈ [+0.9532, +0.9604],
true sd ∈ [0.1525, 0.1589]), `coval_core − gen`, `gen − generic` and `gen − genericpool16` all sit at
**percentile 0.0 on both statistics**. So *"these two arms differ reliably per prompt"* is true of
**every** pair of distinct k=4 sets in this release, and R494–R497 spent four rounds explaining a
distinctness that was never in question. **The placebo used throughout — an arm against ITSELF —
removes the arm difference and therefore asks whether the instrument is noisy, never whether a
difference between two arms means anything.** *(R499)*

⭐⭐⭐ **AND THAT IS ALSO THE ANSWER TO CLAUSE ②, WHICH IS WHAT THE ROUND WAS FOR (R499).** The gap
that matters is not `coval_core − gen` but **`gen − 0.5404`**, the cross-fitted prompt-blind ceiling:
`gen` is at **0.5337**, a gap of **−0.0067**, inside the **0.0122** floor. Two worlds: the arms
**agree**, or they **differ per prompt and cancel**. The cancelling world required the real pairs to
**exceed** the no-difference null; they fall **below** it. **So prompt-awareness buys nothing
per-prompt either, and clause ② is a genuine wall for ③-admissible prompt-aware arms rather than an
artifact of aggregation.** ⚠ The further suggestion — that `gen` lands *closer* to a prompt-blind arm
than two random arms land to each other — is **directional only**: k=4 affords 3 independent
no-difference pairs, so `n_eff = 3` and the permutation floor is `p ≥ 0.25`. *(R499)*

⚠⚠ **AND THAT NULL IS A CEILING, NOT A ZERO — WORDING CORRECTED, CONCLUSION SURVIVES AND SHARPENS
(R499, re-read under §0's severity test).** I called `random_k4_s0` vs `random_k4_s1` a pair with
*"no functional difference"*. They share a **procedure** and differ in **realisation** — two
arbitrary k=4 sets, which is near the **maximum** difference two criterion sets can have, not zero.
So *"gen − generic does not EXCEED it"* was decided against a high baseline and could not easily have
come out otherwise. **That specific comparison is not severe, and World B is killed against a
ceiling rather than cleanly.**

⭐⭐⭐ **WHAT SURVIVES IS STRONGER, AND IT IS THE SENTENCE TO KEEP.** The severe comparison runs the
other way. `gen` and `generic` are **two different procedures**; `random_k4_s0/s1` are **two
realisations of one**. Two different procedures landing **closer together** (r **0.9349**, true sd
**0.1314**) than two realisations of a single random procedure (r **0.9574**, true sd **0.1557**) is
**not forced by any algebra** — it could have gone either way, and did not.

⭐ **The definitional statement, in the scope the design supports:** *whatever prompt-awareness does
to `gen`'s criteria, the per-prompt differences it produces are **no larger than those produced by
drawing criteria arbitrarily** — so at this resolution **prompt-awareness is not distinguishable
from arbitrariness**.* That is why clause ②'s admissible side is empty, and it is a claim about the
**mechanism**, not about the mean. ⚠ `n_eff = 3` for the baseline, so the **ordering** is
directional; the **non-exceedance** is what the design resolves. *(R499)*

⛔ **AND THE COMPUTE THAT WOULD SETTLE ②∧③ IS NOT THE COMPUTE I NAMED (R490).** The generator already
exists — `corebench/generate_core.py` states in its own docstring that it *"MUST NOT SEE `coval_full`"*
and *"sees the CONVERSATION and the FOUR RESPONSES only"*, i.e. rubric-blind, rating-blind and
prompt-aware — and **`gen` is its output**, the best ③-admissible arm at percentile 32.6. And the
second judge cannot adjudicate: `oracle_k4`, which reads the human target **directly**, keeps only
**0.105** of the Bayes ceiling under Qwen3.5-0.8B against **1.088** under 2B, while `topw_k4`
collapses to 0.193 — so the collapse is the judge, not the oracle. **A judge on which an arm that
reads the answer scores at a tenth cannot separate a +0.0067 gap. What would settle ②∧③ is a judge
STRONGER than 2B, and this site has none.** *(R490)*

⛔⛔⛔ **AND THE EXTENSION IS EMPTY BECAUSE ② AND ③ CONFLICT, NOT BECAUSE THE RELEASE OMITS A MEMBER
(R485).** An empty extension is unremarkable if the world merely contains no member; it is a **defect**
if the clauses cannot be jointly satisfied. Measured against R478's **cross-fitted** prompt-blind
ceiling of **0.5404** (not its in-sample max, since ② says *the best* set and a max over 1,820 is an
order statistic): **every arm that clears the ceiling is one ③ excludes.** Five of five —
`oracle_k4` **0.6282**, `greedy_k4_fit1` **0.6071**, `indep_k4_fit1` **0.5915**, `coval_core`
**0.5640**, `topw_k4` **0.5618** — reaching it by reading the prompt's rankings, its ratings, or (for
the released core) via a pipeline that does. **The best ③-admissible prompt-AWARE arm is `gen` at
0.5337, a gap of −0.0067, inside the 0.0122 floor.** *(R485)*

⭐ **AND THE NULL IS EVIDENCE RATHER THAN SILENCE, BECAUSE THE BAR IS DEMONSTRABLY REACHABLE.** The
positive control is the excluded class itself: five arms clear the ceiling, so the design can detect
clearing it, and `random_k4_s0` (0.4920) does not, so the bar is not one a random arm meets. Placebo
**0.4309** against measured chance 0.428. ⚠ And prompt-BLIND admissible arms — `generic` 0.5505,
`genericpool16` 0.5416, `promptecho` 0.4540 — are held OUT of the numerator: an arm compared against
its own class is a degenerate comparison, and folding them in would have produced a "pass" that means
nothing. *(R485)*

⭐⭐ **THE SHARPER HALF, AND IT IS ABOUT PROMPT-AWARENESS RATHER THAN ABOUT ③.** The best rating-blind
prompt-aware arm (**0.5337**) is **indistinguishable from a criterion set that never sees the prompt
at all** (`generic` **0.5505**; the cross-fitted class **0.5404**) — the difference sits inside the
floor. **Seeing the prompt, without reading what humans said about it, buys nothing measurable here.**
That is the mechanism behind the conflict: ② asks an arm to beat a class that already performs at the
level prompt-awareness alone can reach, and only the human labels ③ forbids go further. *(R485)*

⚠ **WHAT THIS DOES NOT SHOW.** That ②∧③ is unsatisfiable *in principle* — that would require
enumerating all prompt-aware rating-blind selectors, which is not a finite object. It bounds **what
has been built here**, on 968 prompts and the 2B judge; five admissible arms have no `_08b` build, so
the second judge cannot host the comparison. **A limit, named, not a result.** *(R485)*

⭐⭐ **AND THE AGGREGATION WAS NEVER A CHOICE ANYONE MADE — IT WAS `score.py:63` (R481).** Every A2 in
this campaign sums satisfaction over the selected criteria, and `/yvec/` and `/sum/` both returned
**0** in this document before this round. A sum's variance grows with k, so a k-gradient is precisely
where an aggregation artifact would hide. ⛔ **Half the sweep is void by algebra**: `mean = sum/k` with
k fixed within a prompt and `cls()` reading signs of differences, so `cls(mean) ≡ cls(sum)` — **2000/2000
on random matrices, and 0.00e+00 across 26 real arm×judge cells.** MEAN is therefore used as a
**positive control on the implementation**, not as a specification. *(R481)*

⭐⭐⭐ **AND THE NULL WAS NEARLY COUNTED WITH BLIND INSTRUMENTS IN IT.** The reversal is present under
`sum` and `median` and absent under `max`, `min` and `midrange` — which reads as 2 of 5. **But `max`
and `midrange` cannot resolve k at all**: their A2 range across the whole ladder is 0.0084/0.0059 and
0.0086/0.0077, **below the 0.0122 floor**, because `max` reports only the single best-satisfied
criterion and is structurally blind to accumulation. **A null from an instrument that cannot see the
effect is silence, not an acquittal.** Correct denominator: **2 of the 3 aggregators that can resolve
k**, with `min` the sole genuine disagreement. *(R481)*

⚠ **AND THE SYNTHETIC NULL DOES NOT RESCUE THE REVERSAL, THOUGH IT INDICTS THE LEVELS.** On
structureless iid data the spurious `corr(k, A2)` is **+0.4176** for `sum` — **the largest of any
aggregator**, against +0.0125 for `max` and +0.0036 for `midrange`. So the campaign's committed
aggregator is the most mechanically k-dependent one. ⭐ **But that term is a property of the
AGGREGATOR and is identical for both judges, so it shifts both correlations equally and cannot create
a sign difference between them.** It explains levels, never the reversal. *(R481)*

⭐ **AND THE IDENTITY CONTROL CAUGHT A DEFECT IN ANOTHER CONTROL.** The synthetic null's first version
printed `sum = +0.4176` and `mean = −0.4790` — two algebraically identical quantities disagreeing,
which is impossible, so the control was broken (one generator consumed in aggregator order, giving
each aggregator different random data). ⭐ **An algebraic identity embedded in a sweep is a tripwire
that fires on any defect in the sweep's plumbing** — shared state, ordering, caching, seeding — and it
was the only control here capable of catching a bug located inside a control. *(R481)*

⛔⛔ **AND THE JUDGE MOVES THE ORDER, NOT ONLY THE LEVEL — BUT ONLY IN ONE PLACE (R480).** ② is a
COMPARATIVE, so what matters is whether *"better than"* survives a judge swap. Over 31 arms carrying
both judges, on the 318 of 465 pairs resolved under 2B, sign survival is **0.8019** [0.7610, 0.8396]
against a split-half **same-judge** placebo of **0.9848** — a gap of **−0.1829**. ⭐ **Stratified, the
pooled number is two different facts: across-family survival is 0.9130 (253 pairs) and within-family
survival is 0.3692 (65 pairs).** Below chance is not disagreement, it is **reversal**. *(R480)*

⭐⭐ **AND THE ENTIRE REVERSAL IS ONE FAMILY, WITH A DIRECTION.** `corr(k, A2)` for the `random`
family is **+0.8570** at 2B and **−0.5026** at 0.8B — **adding criteria to an UNSELECTED set helps the
larger judge and hurts the smaller one** (sign survival 14/55). The `topw` family, which *selects*,
agrees in direction under both (−0.0211 / −0.4234, survival 10/10). **The judges agree on the ordering
of selective rules and disagree on the effect of SIZE for unselected ones.** ⛔ **This lands on the
definition's size clause**: *"more than one; 3–8 indistinguishable"* was established on 2B, and the
k-gradient for unselected sets has the opposite sign under 0.8B. **A size claim is judge-relative in a
way a family claim is not.** *(R480)*
> ⚠ **DOWNGRADED (R481): that correlation is one cell of a two-cell sweep.** With **one seed per
> budget** instead of three the same quantity is **+0.9381 / +0.0111** — the 0.8B sign flips and the
> reversal vanishes. The population is not the cause (968 prompts either way, own-pop ≡ common-pop).
> **The pairwise sign-survival statistic above stands; the directional gloss on this correlation does
> not.** A correlation over arms is a statistic whose SAMPLE is a design choice, and R480 swept the
> threshold axis while silently fixing the arm axis.

⭐ **AND THE SPLIT-HALF PLACEBO IS WHY ANY OF THIS IS READABLE.** Splitting the prompts and treating
the halves as "two judges" gives **0.9848**, so the design demonstrably resolves order and the gap is
attributable to the instrument rather than to noise. Without it, 0.80 would be uninterpretable. The
disagreement is also **concentrated in small differences** — survival rises 0.8019 → 0.9109 → 0.9522
across thresholds of 1×, 2×, 3× floor while the placebo stays ≈1.0. **At 3× floor the judges agree; at
the resolution this definition actually operates at, they do not.** *(R480)*

⚠ **AND THE STEP THIS ROUND WAS SUPPOSED TO BE WAS VOID BY ALGEBRA.** R479 proposed selecting criteria
to maximise *attainment* rather than A2; attainment is affine in A2 with slope **5.3997 > 0**, so the
two objectives have identical `argmax`. **A quantity I had just derived was immediately proposed as
something to measure** — the arithmetic trap arriving inside a `next gradient` line, which is the
sentence written last and controlled never. Cost zero: rung 1 of the attack ladder is three lines.
*(R480)*

⭐⭐⭐ **AND THE 0.54 BAND IS NOT THE TARGET'S NOISE — IT IS THE JUDGE (R479).** Four unrelated routes
converge at 0.54–0.55, which admits three explanations with opposite next moves: the criteria, the
judge, or the target's own irreducible disagreement. The maximum A2 any scorer *without sight of the
target* can reach is the **modal human ranking scored against a HELD-OUT annotator** — the Bayes point
predictor under per-pair 0/1 loss. It is **0.6132** (resolution **0.0093**, measured at four seeds).
Against the best non-oracle arm (`coval_core`, 0.5665) that leaves **+0.0467 of headroom, 3.8× the
floor.** **The band is not a ceiling.** *(R479)*

⛔ **AND THE SAME CRITERIA ATTAIN 0.738 OF THAT CEILING UNDER ONE JUDGE AND 0.193 UNDER THE OTHER.**
`topw_k4`: attainment **0.738** at Qwen3.5-2B, **0.193** at 0.8B — a gap of **0.545**, five times the
0.10 pre-registered threshold. `random_k4_s0` attains **−0.106** at 0.8B, i.e. *below chance*.
**World B: the instrument is what the band is made of, not the criteria.** This is the quantitative
form of what ② already encodes qualitatively — a core is only ever *"a core under J"* — and it says
the judge index is not a caveat but the dominant term. *(R479)*

⭐ **AND THE LEAVE-ONE-OUT DISCIPLINE IS THE WHOLE DESIGN, WORTH +0.0388.** Including the held-out
annotator in the mode that is scored against it gives **0.6520** instead of 0.6132 — and that error
runs in exactly the direction that manufactures headroom and licenses *"the criteria are the
problem"*. The leakage is **reported beside** the honest number rather than argued away. ⭐ And a free
positive control fell out: single-annotator-vs-annotator returns **0.5458** against this campaign's
independently committed human ceiling of **0.5451**, **Δ +0.0007** — a loader written this round
reproducing a number computed by other code in another round. *(R479)*

⚠ **`oracle_k4` ATTAINS 1.088, AND THAT IS NOT A DEFECT.** It was fitted on the prompt's own rankings,
so it is not a member of the class BAYES bounds; **its +0.088 excess is the fitting advantage, now
measured rather than asserted.** ⚠ **And R479's population is 1,078 prompts (≥3 rankings), not
R477/R478's 968** — so `topw_k4` reads 0.5647 here and 0.5475 there, **both correct for their own
populations**. This round rules on the ORDERING and the attainment ratio, never on a level quoted
across the two. *(R479)*

⭐⭐ **AND THE RIVAL CLASS WAS CENSUSED IN FULL — 1,820 MEMBERS, NOT THE NINE ON DISK (R478).** R477
bounded the ③-admissible class by the arms that happened to carry a `.npz`, which is the defect R477's
own retraction had just named. Evaluating **every** 4-subset of `genericpool16` (968 prompts × 16
criteria, complete on disk): min **0.5049**, median **0.5261**, max **0.5433**. `generic` sits at
**0.5377**, percentile **94.4** — a strong comparator, not a weak one. **`topw_k4` at 0.5475 is
percentile 100.0, above every member of the class.** *(R478)*

⭐ **AND THE MAXIMUM OVER 1,820 IS AN ORDER STATISTIC, SO IT WAS CROSS-FITTED.** Selecting the argmax
on half the prompts and scoring it on the other half over 20 splits gives **0.5404 ± 0.0061**, against
an in-sample max of 0.5433 — **selection inflation of just +0.0029**, so the best subset is genuinely
selectable rather than a noise peak. **`topw_k4` − cross-fitted best = +0.0071**, still inside the
**0.0122** floor. **③ stays cheap, and the margin is SMALLER than R477 reported, not larger.** *(R478)*

⚠ **AND THE PREMISE THAT SENT R478 THERE WAS FALSE.** This document's own line — `generic` at
percentile 0.000 of a 1,820-member census — is about the **replication** statistic (0.8114 against
0.8226–0.8675), **not** A2. I matched the two censuses on the phrase *"percentile of the 1,820"* when
`1820` is just C(16,4) and any subset census of this pool has it. ⭐ **A census is identified by its
STATISTIC, not by its size.** The round survived its own bad premise and tightened the estimand
anyway, which is the argument for running it. *(R478)*

⭐ **A STRUCTURAL FINDING THE SWEEP HANDED OVER FREE.** Cross-fitted best is **flat at ~0.538 from
k=2 to k=6** (0.5364 · 0.5393 · 0.5386 · 0.5381 · 0.5371) while the census median rises with k. **The
prompt-blind class has a ceiling near 0.54 that more criteria do not raise** — the best small set is
as good as the best large one, across 14,876 subsets. *(R478)*

⭐⭐⭐ **AND THE FORK IS DECIDED BY EVIDENCE, NOT BY STIPULATION (R477).** R475's fork — weaken ③ to
forbid only the prompt's *rankings*, or keep it strong and exclude CoVal-core — **is a choice of
convention, and no measurement adjudicates a convention.** What decides it is measurable: **what does
a core GAIN by reading the annotator ratings?** Against the best ③-admissible arm on disk (`generic`,
a fixed prompt-blind set, **0.5376**), `topw_k4` gains **+0.0099 [+0.0009, +0.0189]** against a
**measured** floor of **0.0122** — `effect/floor` = **0.81**, so **no count is admissible, only a
direction**. ⛔ **③ is CHEAP: it forbids nothing that a good rating-blind selector cannot match.
③ stays as written, `coval_core` stays EXCLUDED, and the extension stays 0.** *(R477)*

⚠ **AND THE FIRST ANSWER WAS THE OPPOSITE, KILLED BY ITS OWN SHAM'S SCORE.** Measured against
`topvar_k4` the gain is **+0.0695 [+0.0587, +0.0809]**, 5.7× the floor — which would have licensed
*"③ forbids the mechanism"*. **`topvar_k4` scores 0.4780, BELOW the random baseline (0.4856 · 0.4913 ·
0.4790).** It is a poison, not a placebo, and `+0.0695` is the ratings' value **plus the cost of
ranking by response variance**. ⭐ **A sham answers "is the ingredient doing the work" only when the
sham is otherwise COMPETENT; a weak sham measures the ingredient plus its own incompetence, and both
terms are positive, so the number always flatters.** The comparator must be the **best member of the
rival class**, and a class is not bounded by one arm. *(R477)*

⭐ **CONTROLS, AND CHANCE IS NOT WHERE ANYONE WOULD HAVE PUT IT.** The floor is **measured** from three
`random_k4` arms differing in nothing but the draw (0.0122 · 0.0096). `oracle_k4`, which reads the
human target directly, clears it on both judges (**+0.1184** · **+0.0365**). And the placebo — every
arm re-scored against *shuffled* rankings — lands at **0.4250–0.4293**, spread 0.0043: **A2's chance
level is 0.428, not 0.5**, because `cls()` emits {−1, 0, +1} per pair and ties are not coin flips.
The design **measured** it instead of assuming it. *(R477)*

⚠ **AND ONE JUDGE CANNOT ANSWER THE QUESTION AT ALL.** The 0.8B judge has no `_08b` build of
`generic`, `genericpool16`, `gen`, `full` or `promptecho`, so its admissible class holds **4** arms and
"the best admissible" is unbounded there. **UNVERIFIED on 0.8B — which is neither agreement nor
disagreement**, and folding it into either would be the false-acquittal direction. *(R477)*

⭐ **A SIDE FINDING THAT LANDS ON CLAUSE ②, NOT ③.** `generic` reads no ratings, no rankings, and not
even the prompt — and it scores **0.5376**, within the floor of `topw_k4`. Clause ② is precisely
*"better than the best generalising prompt-blind set"*. **Seen from this side, `topw_k4` does not
clear ②** — consistent with the committed census in which only 5 arms pass ①∧②∧④. *(R477)*
> ⛔ **RETRACTED ONE ROUND LATER (R478).** `topw_k4` scores **0.5475 — percentile 100.0** of the
> 1,820-member reference class, **above every single member**; its margin over the *cross-fitted*
> best is **+0.0071**, inside the 0.0122 floor. ② is **UNRESOLVED** for `topw_k4`, not failed.
> **Folding UNRESOLVED into FAILED is the false-retraction direction** — permanent, because nobody
> re-examines a withdrawn claim. The sentence above is kept, not edited, because the error is
> instructive: it sat in the `next gradient` line, which is written last and controlled never.

⛔⛔ **AND THE GATE THAT POLICES THIS DOCUMENT CHECKS BETWEEN A QUARTER AND TWO-THIRDS OF IT (R476).**
`definition_matches_the_record.py` reported *"302 of 302 assertions"* — its count at the time — and nothing else — **a fact
about the LIST, not about the document** — and that is how R475's substring replace corrupted a
measured `+0.1298` while the gate returned PASS. Measuring the denominator it owed: coverage is
**69.2%** of author-emphasised numbers (**117** of 169), **35.2%** of decimals (156 of 443), **34.3%**
of values carrying ≥2 decimal places (134 of 391), and **28.0%** of every number (282 of 1007). *(R476)*

⭐ **AND THE SPREAD IS THE ANSWER, NOT A DEFECT IN THE MEASUREMENT.** The denominators differ by
**5.96×**, because *"a numeric claim"* is a choice and not a property of the file. So **there is no
single coverage number to quote**, and any one of the four alone would be a specification cherry-pick.
Coverage is decided **by span, never by value** — a number counts as checked only if its own character
offsets lie inside the span an anchor captured *at that site* — because value-matching would certify
every `0.5` in the document on the strength of one anchor capturing a `0.5` elsewhere. *(R476)*

⚠ **WHAT THIS DOES NOT SAY.** It does not say the document is wrong; every anchored number still
re-derives from a committed artifact, and the four controls hold (the probe site `0.8437` at char
41653 is COVERED, R475's corrupted `+0.1298` is UNCOVERED, an absent literal extracts 0× and appears
once injected, and never-matching anchors give exactly 0). **It says a PASS certifies the anchored
numbers and never the document** — and the gate now prints that sentence itself, with its own
denominator, on every run. *(R476)*

⚠ **AND THE FIGURE IS SCOPED TO THE DOCUMENT THAT WAS MEASURED, WHICH THIS PARAGRAPH ALREADY IS NOT.**
Writing R476's result into DEFINITION.md added numeric claims to the very population R476 counted, so
the live gate now reports **69.0% / 27.7%** where the round measured **69.2% / 28.0%**. That is not
drift and neither number is wrong: **a document that states its own coverage changes its coverage by
stating it.** The round's numbers hold at commit `8b57ace` **measured with the gate's 330 anchors** — both halves of the scope, because the instrument grows too; the gate's line is the current value, and
the two are expected to differ by exactly the size of whatever was last written. *(R476)*
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


⛔⛔⛔ **AND THE RECOMMENDATION THAT RESTED ON THE PREDICTION CEILING IS WITHDRAWN, ONE ROUND AFTER IT
WAS MADE (R504).** The campaign recommended reading ② over ③-dropping because `oracle_k4` (**0.6282**)
exceeded the Bayes ceiling for any predictor (**0.6132**). Recomputed **in one process, on one
population of 968 prompts, with one hold-out convention and three seeds**:

| quantity | recomputed | seed range | as quoted |
|---|---|---|---|
| held-out ceiling (majority of the non-held-out annotators) | **0.6466** | [0.6408, 0.6534] | 0.6132 |
| in-sample ceiling (scored annotator included — the biased one) | **0.6886** | [0.6801, 0.6971] | 0.6520 |
| `oracle_k4` | **0.6325** | [0.6279, 0.6355] | 0.6282 |
| random predictor | **0.3321** | [0.3275, 0.3411] | — |
| ceiling on shuffled annotator assignment | **0.4144** | [0.4005, 0.4225] | — |

**Gap `−0.0141` against a measured noise floor of `0.0220`: `oracle_k4` sits BELOW the ceiling, and
the difference is inside the floor.** Controls all pass and all could fail — the in-sample ceiling
exceeds the held-out one by more than the floor, which is the control that would have caught a
silently biased ceiling; the shuffled ceiling falls toward chance; the random predictor lands at
0.3321 rather than at zero.

⭐ **The recommendation's own text named this as the first check an attacker should run. I wrote that
sentence and did not run it** — and it is the same error as two rounds earlier, when `coval_core`
0.6044 (per-criterion sign agreement) was set against an A2 ceiling. **Twice in three rounds, the
second time with my own warning already in the artifact.**

⚠ **Three-valued, because the attack must not be over-trusted either.** Both recomputed figures come
in *higher* than the quoted ones — a systematic offset rather than noise, so this instrument differs
from the campaign's in a convention not yet isolated. **CONFIRMED: the two compared numbers are not
comparable, which suffices to withdraw. UNVERIFIED: whether `oracle_k4` exceeds the ceiling under the
campaign's own instrument.** *(R504)*


⭐⭐⭐ **AND THE WITHDRAWAL IS ITSELF REVERSED — A CORE IS A RANKER, SO ONE CEILING APPLIES, AND AT THE
CAMPAIGN'S OWN 20-DRAW CONVENTION THE GAP RESOLVES (R505, R506).** Two facts settle it, and the first
is a **derivation** read out of `corebench/score.py` rather than measured: `yvec()` returns **one
scalar per response** and `cls()` takes signs of scalar differences, so a core's six pairwise verdicts
are **necessarily transitive**. It cannot emit the intransitive patterns the per-pair mode uses on
**33.5%** of prompts. **So the RANKER ceiling is the only bound that can apply to a core, and the
PAIR-PREDICTOR ceiling is unattainable by one — comparing a core to it was R504's category error.**

| recomputed at **20 draws/prompt**, 968 prompts, 3 seeds | value | seed range |
|---|---|---|
| `oracle_k4` | **0.6293** | [0.6283, 0.6308] |
| **RANKER ceiling — the applicable bound** | **0.6220** | [0.6200, 0.6235] |
| pair-predictor ceiling (unattainable by a core) | 0.6437 | [0.6415, 0.6451] |
| in-sample ceiling (the biased one — hold-out control) | 0.6863 | [0.6840, 0.6877] |
| random predictor | 0.3342 | [0.3327, 0.3356] |
| shuffled-annotator ceiling | 0.4099 | [0.4077, 0.4123] |

**Gap `+0.0073` against a conservative floor of `0.0047` — RESOLVED.** The resolution sweep is the
evidence that the earlier verdict was about **effort**, not nature: `reps=1` gap +0.0042 floor 0.0091
(inside) · `reps=5` +0.0056 / 0.0082 (inside) · **`reps=20` +0.0073 / 0.0035 (resolved)**. The floor
falls while the gap holds. **R504 and R505 both stopped at "inside the floor" without asking for more
draws, and R479 had been averaging twenty all along.** *(R505, R506)*

⚠ **Bound stated, not smoothed:** the recomputed ranker ceiling is **0.6220** against R479's quoted
**0.6132** — smaller than the discrepancy it replaced, and **still not isolated**. *(R506)*


⭐⭐⭐ **AND THE LAST RESIDUAL IS CLOSED — IT WAS ARM COVERAGE, AND THE FILTER I BLAMED EXCLUDES
NOTHING (R507).** R506 reported a ranker ceiling of **0.6220** against R479's quoted **0.6132** and
left it open. On R479's **actual** population — all prompts with ≥3 rankings — the ceiling recomputes
to **0.6174**, which is **0.0042** from the quoted value and **inside R479's own stated resolution of
0.0093**. On the **968** prompts `oracle_k4` covers it is **0.6218**. **The residual was the
arm-coverage restriction, and R506's comparison stays correct BECAUSE of it** — comparing an arm to a
ceiling requires both sides on the same prompts.

⛔ **The hypothesis that round was built on died to its own positive control.** I opened on
`R479:91`'s `len(v) >= 3` against my `>= 2`. Swept: **n = 1078 at m = 1, 2 and 3 alike** — every
prompt in the release carries at least three rankings, so **R479's filter excludes nothing and is a
no-op.** The control requiring the sweep to move **FAILED**, the script refused to report, and the
round redirected to the axis that does vary. **A flat sweep is not evidence of no effect; it is
evidence the axis was mis-chosen, and only the control tells those apart.** *(R507)*


⭐⭐⭐ **AND ③ HAS A PARTIAL BEHAVIOURAL SURROGATE AFTER ALL — IN THE SELECTION, NOT THE TEXT
(R508).** R501 failed its own positive control looking for one in per-prompt A2 dispersion. R503 then
showed both sides of ③ draw **100.0%** of their criteria verbatim from the *same* rubric pool, which
means no textual test can exist and moves the search to **which items are picked**.

Mean **normalised position** of an arm's selected criteria within that prompt's own rubric list:

| arm | mean position | |
|---|---|---|
| `oracle_k4` | **0.2791** | ③-excluded label-**optimiser** — separates |
| `greedy_k4_fit1` | **0.2880** | ③-excluded label-**optimiser** — separates |
| `random_k4_s0` / `s1` / `s2` | **0.5012** / **0.5039** / **0.5071** | uniform selectors, spread **0.0059** |
| `topw_k8` | **0.5051** | ⛔ ③-excluded and **MISSED** |
| `topwvar_k4` | **0.5090** | ⛔ ③-excluded and **MISSED** |

**POSITIVE control:** `oracle_k4` separates — the case R501's instrument could not see.
**NEGATIVE control:** uniform selectors land where uniform selection predicts, which validates the
position index and was discovered to be a control rather than designed as one.

⛔ **The pre-registered kill fired: a surrogate that misses a KNOWN reader cannot certify an unknown
one, so ③ is NOT replaceable and the fork does not dissolve.** ⭐ **But the shape of the failure is
the finding: every reader that OPTIMISES against the labels is caught, and every miss is RULE-BASED
selection. What escapes is rule-following, not optimisation** — sharper than *"no surrogate exists"*,
and what R501 could not reach. ⚠ Arms whose rule is *stated over the rubric ordering* also separate;
that is a **derivation** and counts for nothing. *(R503, R508)*


⛔⛔⛔ **AND A CHECKABLE ③ DOES NOT RESCUE THE DEFINITION — IT MAKES THE SAME VACUITY HARDER TO SEE
(R509).** R508's surrogate invites an obvious reformulation: replace ③ *"not built by reading the
labels"* (provenance) with **③′ *"not OPTIMISED against the labels"*** (checkable from the criterion
set plus the prompt's rubric). Applied to the **5** arms admitted by ①∧②∧④:

| arm | criterion text | ③′ verdict |
|---|---|---|
| `oracle_k4`, `greedy_k4_fit1`, `indep_k4_fit1` | yes | **EXCLUDED — separate as optimisers (measured)** |
| `topw_k4` | yes | excluded by **derivation** (rule stated over the ordering) |
| **`coval_core`** | **no** | ⛔ **CANNOT RULE — no criterion text, so no positions** |

**③ extension 0. ③′ extension 1 — and that 1 is `coval_core`, with 0 adjudicated members and 1 blind
spot.** Of **95** arms carrying a criterion-text file, the **released core is not one of them**; only
its sham is. **POSITIVE control passes: the instrument ruled on 4 of 5 by measurement.**

⭐ **A zero from an instrument that could not look is silence, not an acquittal — so `coval_core` is
not a member of ③′, it is missing data wearing a member's clothes.** The reformulation converts
*"empty because ③ excludes everything"* into *"one member the instrument cannot see"*: the same
vacuity, less visible. ⭐⭐ **The fork is therefore not provenance-vs-checkability but AN HONEST ZERO
VS A FLATTERING ONE.** *(R508, R509)*


⛔⛔⛔ **AND R509's PREMISE WAS FALSE — THE RELEASED CORE'S CRITERIA ARE IN THE RELEASE, AND
ADJUDICATING THEM MAKES ③′ CHANGE NOTHING AT ALL (R510).** R509 called `coval_core` an
un-adjudicable blind spot because `corebench/results/` has no `core_coval_core.json`.
**`data/conversation_rubrics.jsonl` carries a `coval_core` field with `criterion` text** — sixth
false wall this session, and like the other five it was asserted right after correctly checking
something adjacent.

**Adjudicated:** `coval_core`'s mean normalised selection position within its own conversation's
`coval_full` is **0.2746** (median **0.2222**), against `oracle_k4` **0.2791**, `greedy_k4_fit1`
**0.2880**, and a uniform-selector null band of **[0.4894, 0.5189]**. **It sits with the
label-optimisers. ③′ EXCLUDES it, so ③′'s extension is 0 — exactly ③'s.**

⭐ **The correction makes the result simpler and stronger.** R509 said a checkable clause *hides* the
vacuity; it does not — **it changes nothing.** The definition is empty under both readings, and the
fork's B-column loses the extra cost R509 gave it.

⚠⚠ **SCOPE, and it is large: only 256 of 3,899 core criteria — 6.6% — are locatable verbatim in
`coval_full`.** The statistic is a subsample and may be biased. ⭐ **And that is itself a finding: the
released core is NOT a pure subset of the full rubric**, so 93.4% of its criteria are rewritten or
drawn from elsewhere — which R503's `coval_core (no text)` row concealed by looking in
`corebench/results/` rather than in the release. **The claim WAS bounded as "on every criterion this instrument can
locate" — and that bound is not sufficient (R511).**

⛔⛔ **R510's NUMBER IS DOWNGRADED TO `UNVERIFIED`, AND THE ACCUSATION AGAINST THE CARD IS
RETRACTED.** The dataset card states the construction in full: *"Our process first **REWRITES** all
rubric items to have positive weight and then **MERGES** semantically redundant rubric items while
adjusting their scores. **THEN**, it aims to select up to four rubric items with the highest average
ratings"* — plus *"LM-assisted synthesis plus human review"* and an explicit warning that the method
*"can produce core rubrics that **drift from the data**."* **The 93.4% non-match is the documented
REWRITE step. I quoted step three of three and called the object non-compliant with it.**

**And that voids the statistic.** The 6.6% locatable subset is *exactly the criteria that survived
rewriting unchanged* — a selection with no reason to be independent of selection position. **0.2746
is a reading about the unrewritten remainder, not about `coval_core`.** ⭐ What survives: the released
core's criterion text **is** in the release, so R509's "blind spot" stays retracted. *(R511)*


⛔⛔⛔ **AND R508's SURROGATE IS RETRACTED — MEASURED ON THE ACTUAL RATINGS IT IDENTIFIES THE WRONG
ARMS (R512).** R468's `id_map.json` joins corebench's prompt ids to the release at **968 of 968**, and
`coval_full[i].scores` carries the per-annotator ratings — so ③′ is testable against **the quantity
the dataset card names**, *"the highest average ratings"*, rather than against list position.

| arm | **mean rating percentile** | position (R508) |
|---|---|---|
| `oracle_k4` | **0.4888** | 0.2791 — "separates" |
| `greedy_k4_fit1` | **0.4964** | 0.2880 — "separates" |
| `indep_k4_fit1` | 0.5356 | ~0.29 — "separates" |
| `topw_k4` | **0.7857** | 0.5378 — "derivation" |
| `topw_k8` | **0.6547** | 0.5051 — ⛔ "missed" |
| `topwvar_k4` | **0.5036** | 0.5090 — ⛔ "missed" |
| `random_k4_s0/s1/s2` | 0.4381 / 0.4498 / 0.4473 | 0.5012 / 0.5039 / 0.5071 |

⛔⛔ **The proxy LOSES RECALL — it does not invert.** Against a random band of **[0.4146, 0.4734]**
(3 seeds, spread 0.0118), **every ③-excluded arm sits ABOVE it**, including the two position missed.
So its catches are real and its misses are genuine. ⚠ My first write-up said *inverted*, comparing
0.4888 to a remembered "≈0.5" instead of to the computed band. ⭐ **The
mechanism: `coval_full`'s list order is not rating order.** Position measured *where an item sits in a
list*; ③′ is about *how highly it was rated*. **Instrument's unit ≠ claim's unit, inside the check
built to catch that failure.** ⚠ `gen`, `generic` and `coval_core` remain N/A — no pool overlap — so
③′ stays open and R340's derivation stands. *(R512)*

---

## R514 · Clause ① is subsumed by clause ②, and it is a derivation

**The question.** `STATEMENT.md` had said since R464 that ① *"excludes 0 of 41 arms — UNEXERCISED,
not vacuous"*, defended by an adversarially-constructed worst rubric subset it does exclude at
−0.2779. The label was never checked against the obvious rival: that ① excludes nothing because it
**cannot**.

**The method — no new compute.** R294's census stores, per arm, the A2 score and the two clause
contrasts `c1`, `c2` over the same 968 prompts. Each clause bar is therefore recoverable as
`a2 − c[0]`. Both clauses have the form `a2 > bar`.

**The result.** Across all 41 arms:

| bar | range | meaning |
|---|---|---|
| **bar₁** | **[0.4821, 0.4927]** | a random draw of the prompt's own rubric |
| **bar₂** | **[0.5386, 0.5504]** | the generalising prompt-blind ceiling |

**The ranges are disjoint, gap 0.0459, on every arm.** So `a2 > bar₂ ⟹ a2 > bar₁` by transitivity
of `>`, and the count of arms satisfying ② while violating ① is **0 by construction**.

⛔ **DERIVATION, not measurement.** The 41 arms tested nothing; the algebra did. The assumption it
rests on is that **both bars are global scalars** on a common statistic (A2) and direction — which
is how the census computes them, and which is the only reason the implication holds.

**Controls.** Positive: **24 of 41** arms do fail ①, so the ① verdict is not degenerate and a
"0 violations" reading is admissible. Negative: the bar ordering was verified on **every** arm, not
the one first inspected — a single-arm read would have generalised from n=1.

⭐⭐⭐ **Consequence: the definition has THREE independent clauses — ② ③ ④.** ① is either deleted
or **re-operationalised per-prompt**: admit an arm only if it beats *that conversation's own* random
rubric draw. That is the only reading in which ① can bind, because for individual conversations the
local bar exceeds the global 0.5404. **No round has run it**, and the census stores aggregate
contrasts only, so running it means re-scoring against each conversation's own draw.

**What this does NOT overturn.** The R464 adversarial subset is still excluded at −0.2779; ① is a
*true statement about cores*. It is simply not doing work in the definition as operationalised.

---

## R515 · The per-prompt escape is real, and R514's warrant was wrong

**R514's mechanism claim is retracted.** It said both clauses have the form `a2 > bar`, so `bar₁ <
bar₂` forces subsumption by transitivity. **Reading R294's code shows they are not.** Line 139:

```python
c1 = cell_a(on(S[a], ps), on(S["random_k4_s0"], ps))
c2 = cell_a(on(S[a], ps), on(POOL, ps, list(range(min(K[a], npool)))))
ok1 = verdict(*c1[:3], c1[4]) == POS
```

Both clauses are **paired-difference interval verdicts with an MDE**, against two comparator **arms**
— ① against `random_k4_s0`, ② against the blind pool truncated to the arm's own k.

**Why that matters.** Transitivity of `>` does not carry to interval verdicts, because the two
contrasts have different variances. **`c1`'s CI is WIDER than `c2`'s on 20 of 41 arms**, so the
route by which ① could fail while ② passes is genuinely open. What closes it is not algebra but
**margin**: the tightest ②-passer clears ① by **+0.0582** against a mean CI width of **0.0200** —
about three widths of headroom.

⭐ **Corrected claim: ① is subsumed by ② EMPIRICALLY on all 41 arms with ~3 CI-widths of slack,
NOT by derivation.** The conclusion (① adds nothing as operationalised) survives; the warrant is an
empirical regularity, not a theorem. Calling it a derivation made it sound more certain than it is
and removed the reason to check the flip route.

**And the escape R514 named is real.** Per prompt, `random_k4_s0` scores **0.4927** on average and
the pool **0.5504**, gap **+0.0577** — but the ordering **reverses on 26.96% of prompts** (20.56%
exact ties, sd of the per-prompt difference 0.1597). So the global gap is an average concealing a
large minority.

⭐⭐⭐ **Consequence for the formulation.** ① is **not deletable**. As a global bar it is subsumed;
**per-prompt it has something to bind on, on roughly a quarter of conversations.** The open question
is no longer *"is ① vacuous"* but *"does any actual arm fail a per-prompt ①"*, which needs each
admitted arm re-scored prompt-by-prompt against `random_k4_s0`.

**Instrument note, carried because it will recur:** the release ships **two** saturation families,
`sat_*` and `sat08_*`. Both load without error. R294 uses `sat_*`; a reconstruction on `sat08_*`
reproduces the aggregate to +0.0685 instead of +0.0577 and looks entirely plausible.

---

## R516 · A per-prompt clause ① is not one clause, and ① is deletable

**R515 closed by saying ① is "not deletable" because per-prompt it has something to bind on.**
That escape exists — the comparator ordering does reverse on 26.96% of prompts — but **using it
requires an aggregation, and the aggregation determines the answer.**

**Every admitted arm scored per-prompt against the ① comparator, with all five positive controls
reproducing their stored `c1[0]` to six decimals:**

| arm | win | tie | loss |
|---|---|---|---|
| `coval_core` | **0.5382** | 0.2655 | 0.1963 |
| `topw_k3` | 0.5331 | 0.2696 | 0.1973 |
| `topw_k4` | 0.5227 | 0.2934 | 0.1839 |
| `topw_k6` | 0.5072 | 0.3244 | **0.1684** |
| `topw_k8` | **0.4897** | 0.3316 | 0.1787 |
| null `random_k4_s1` | 0.3781 | 0.2934 | 0.3285 |
| sham `coval_core_sham` | 0.3998 | 0.2149 | 0.3853 |

**Every admitted arm clears the null by a wide margin, so a null-calibrated per-prompt ① excludes
nothing.** At the natural majority reading **τ = 0.50 it excludes `topw_k8`** — and that exclusion
is an artifact.

⭐⭐⭐ **Win rate and loss rate rank the admitted arms at Kendall τ = −0.600.** `coval_core` is 1st
by wins and **4th by losses**; `topw_k6` is 4th by wins and **1st by losses**. The mechanism is
resolution: per-prompt A2 has **7 levels over 6 pairs**, ties are structural, and the tie rate rises
**monotonically with k** (0.2655 → 0.3316). A higher-k arm wins less *and* loses less. **A win-rate
rule punishes an arm for tying; a loss-rate rule rewards it.** Under ties-as-half-wins nothing is
excluded below τ = 0.70.

**So a "per-prompt ①" is a family of rules that disagree about which arm fails, and the aggregation
choice does more work than the criterion.** It is not a clause; it is a knob.

⭐ **Resolution of the ① question, across R514–R516:** globally ① is subsumed by ② (empirically, on
all 41 arms, with ~3 CI-widths of slack); per-prompt it is ill-posed. **① is deletable, and now for
a demonstrated reason rather than an assumed one.** The definition is **② ③ ④**. ⚠ **SUPERSEDED — the definition is ② ∧ ③** *(R519, R599)*. This line predates R519, which measured clause **④ dropping 0 of the 9 ②-passers — identical to ①** — so ④ adds nothing and was retired alongside it. **The retirement reached the claim table and not this sentence**, which is why the deliverable stated two different definitions for 80 rounds. Annotated rather than rewritten (L81): the reasoning below about ① is unaffected and still correct.

**What is NOT claimed:** that no principled per-prompt aggregation exists. Choosing one is a
construct claim and needs an external standard for what a core must do — which this site does not
have, and which the impossibility register already names.

---

## R517 · Clause ④ has never been placed where it could fail

**R439 established ④ is not a reparameterisation of ②** — its bar (**0.4512**) sits **0.0687 below
the weakest of all C(16,4) = 1,820 subsets** in ②'s reference class (min 0.5199, percentile 0.00).
That is a claim about **reachability of the bar within ②'s knob**, and it is sound.

⚠ **The deliverable read it as a claim about the extension, and those are different properties.**
④ adds to the definition only if some arm **passes ② and fails ④**. That cell:

| population | n | ②pass | ④fail | E[both] | identified? |
|---|---|---|---|---|---|
| home judge J | 56 | 0 | **0** | 0.000 | ⛔ **④'s marginal is 0** |
| second release | 7 | **0** | 7 | 0.000 | ⛔ **②'s marginal is 0** |

**In both populations one marginal is degenerate, so the cell is 0 by construction.** A derivation,
not a null. The negative control shows the design is not the problem: pairing the home population
with ④'s global fail rate (22/93) and a 50% ② pass rate expects **6.62 arms** in that cell.

⭐ **So "④ excludes all 7 arms on the second release" is true and is not evidence of independence** —
**② excludes the same 7** *(R434)*. And at home ④ excludes nobody *(R436, `W-REDUNDANT-AT-J`)*.

⭐⭐⭐ **④ is UNVERIFIED, and that is NOT ①'s situation.** ① was measured redundant across 41 arms
with a mechanism and a margin; ④ has simply never been tested where it could fail. **The definition
is ② ③ with ④ carried as unverified** — dropping it would be as unwarranted as asserting it.

**What would settle it:** arms that clear the blind-pool bar scored against the criterion-free rules
on the same release. That is a scoring run, and it is the cheapest open item in the register.

---

## R518 · ④ is redundant at home, and R517 under-claimed

**R517's wall — "settling ④ needs a scoring run rather than a reanalysis" — is false.** **41 arms
carry both a ② verdict (R294) and a ④ score (R436)**, and at the home judge **②'s marginal is 9,
not 0**. The joint was one merge away.

**Among the 9 arms passing ②, the margin over ④'s bar in units of each arm's own MDE:**

| | margin |
|---|---|
| `topw_k8` (smallest) | **4.90×** |
| `coval_core` | 5.16× |
| `oracle_k4` (largest) | **8.65×** |

**Pre-registered kill was 2.00×.** So "④ excludes 0 of 56 at home" is a **measurement with power**,
not a resolution limit — ④ cannot exclude a ②-passer here.

**Negative control:** the scale does place an arm below ④'s bar — `promptecho_sham` at d = −0.0106.
⚠ But it is **under-resolved** (|d|/MDE = 0.29) **and fails ②**, so it cannot populate the
informative cell in either direction.

⭐⭐⭐ **④ is REDUNDANT at the judge the definition names — the same status as ①, by a different
route.** ① is redundant because its bar sits *below* ②'s; ④ because its bar sits **so far** below
(0.0687 under the weakest of ②'s 1,820 subsets, R439) that only arms ② already rejects come near it.

⚠ **On the second release ④ remains genuinely unidentified** — ② admits 0 of 7 *(R434)*, so nothing
there can distinguish the clauses. Unchanged from R517.

**Correction to R517, and the direction matters.** It marked ④ UNVERIFIED in *both* populations,
which is right for one and wrong for the other. **A false UNVERIFIED manufactures work**: it invented
a scoring run that the record already answered. A false acquittal is permanent because nobody
re-examines a cleared claim; a false *unverified* is expensive because everybody re-runs it.

---

## R519 · Only ③ narrows what ② admits — all four clauses, one population, one instrument

R514–R518 tested ① and ④ against ② in separate rounds with separate instruments. Putting all four
on the **41 arms** that carry both R294's verdicts and R436's ④ scores:

| clause | drops of the **9 ②-passers** | drops of the **32 ②-rejects** | reading |
|---|---|---|---|
| **①** | **0** | **24** | **nested inside ②** |
| **③** | **4** | **0** | ⭐ **orthogonal to ②** |
| **④** | **0** | **0** | discriminates nothing at home |

⭐⭐⭐ **The sham column is what makes this a mechanism rather than a tally.** ① *does* discriminate
— on 24 arms — but every one of them is an arm ② has already removed, which is subsumption made
visible. ④ discriminates on nothing at all here. **③ alone cuts where ② does not, and cuts nothing
where ② already has.**

**The four arms ③ removes are the highest scorers**, and all four read the prompt's labels:
`oracle_k4` (all annotators), `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` (parity 1).

**Surviving all four clauses:** `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` —
**identical to the census's own `admitted`**, confirming ①∧④ contribute nothing to it.

**Controls.** Negative: ② against its own admitted set drops 0 — the join is sound. Positive: ③
drops 4, so ①'s and ④'s zeros are measurements rather than silence. Noise floor: R518 put every
②-passer at 4.90×–8.65× MDE above ④'s bar.

⭐⭐⭐ **So the definition is a PAIR, and the two clauses are orthogonal by measurement:**

> A **core** for a conversation is a set of criteria that **② scores better than the best
> generalising prompt-blind criterion set**, and **③ was not built by reading that conversation's
> human labels**.

⚠ **The tension, now measured rather than asserted: the only clause doing independent work is the
one that cannot be checked from the object.** ② is behavioural and anyone can run it. ③ is
provenance — it needs the producer. And it earns its place by removing the *best-performing* arms,
which score highest precisely because they read the answer.

---

## R520 · ③'s provenance literal is complete where used, incomplete one join away

R519 left the definition resting on **② ∧ ③**, with ③ the only clause narrowing anything. ③'s
verdicts come from a **4-element hardcoded literal** in R294 — `USES_PROMPT_LABELS` — declared, not
derived. So the definition's entire working content is one Python set.

**The keyword route fails first, and instructively.** Grepping for scripts that touch the labels
returns **19 of 19** — `score.py` reads labels *to score*. **Instrument's unit: "imports
load_targets". Claim's unit: "the SELECTION consumed this prompt's labels."** Only the source gate
separates them: `select_core.py:102` opens `comparisons.jsonl` **only** under
`a.rule in ("oracle_k", "indep_k", "greedy_k")`.

**Deriving from that gate over the 56-arm universe:**

| | |
|---|---|
| arms in a label-reading family | **10** |
| declared in the literal | **4** |
| **absent** | **6** — `oracle_k4_oracle_k{A,B}`, `greedy_k4_greedy_k{A,B}`, `indep_k4_indep_k{A,B}` |

⭐ **None of the six carries a ③ verdict in R294's census** — they exist only in R436's 56. **The
literal is complete over the 41 arms ③ was ever applied to, so R519 stands unchanged.**

**Controls.** Positive: the derivation recovers all 4 declared members from tags alone. Negative:
none of the 33 documented label-blind arms is derived as a reader — where the keyword version failed.
Sham: deriving on the *satisfaction* list gives 12, not 10, so the instrument reads the label gate
specifically rather than "any rule that consumes something".

⚠ **The hazard is live one join away.** R518 and R519 both joined R294's verdicts to R436's 56 arms
for ④. **A future round extending ③ to that same 56 would silently admit six label-readers.**

⭐⭐⭐ **The general point: a hardcoded set is scoped to the population it was authored against, and
nothing in it records that scope.** The remedy is six lines and is demonstrated here — **derive the
set from the code's own gate instead of declaring it.**

---

## R521 · What the declared literal costs, and a forced check demoted to a control

**The previous round's announced next step could not have failed.** "Does the derivation reproduce
R294's admitted set over the 41?" — R520's output forces *yes*: `derived − declared` = 6 arms, **0**
of which carry a ③ verdict, and `declared ⊆ derived` was already established. **Used here as a
positive control (it passes at 0 disagreements), never as a finding.**

**The version that can fail is the wider population.** Over R436's 56 home-judge arms, literal and
gate disagree on exactly the 6 R520 named, and **all six sit above the ② bar**:

| arm | A2 |
|---|---|
| `oracle_k4_oracle_k{A,B}` | **0.6353** |
| `greedy_k4_greedy_k{A,B}` | **0.6292** |
| `indep_k4_indep_k{A,B}` | 0.6079 |

The current 9 ②-passers span **0.5593–0.6283**. **Four of the six outscore all of them.**

**Controls.** Negative: the 33 label-blind arms disagree on 0. Sham: the *satisfaction* partition
disagrees on 8 versus the label partition's 6, so the price is specific to the label gate rather
than to any rule split. Noise floor: the ② bar is taken at the conservative top of its measured
range [0.5386, 0.5504], so every candidate clears it under every setting.

⚠ **Bound: candidacies, not verdicts** — 15 of the 56 carry no ② interval verdict, and producing
one is a scoring run.

⭐⭐⭐ **The pattern, now three times: the highest scorers are the label-readers.** R519 found ③
removes the top 4 of the 9 admitted; here the 6 the literal misses would be the top 4 of the
extended set. **③ does its work at the top of the distribution, which is where a benchmark's
headline comes from — without it the leaderboard ranks how much each arm read the answer.**

---

## R522 · The six are verdicts, not candidacies

**The wall fell first.** R521 closed saying the real ② verdicts for the six needed a scoring run.
**All six saturation matrices are on disk**, so R294's own contrast machinery re-runs directly —
reanalysis, not scoring. **Third false "needs new computation" wall this session.**

**All six clear ② as interval verdicts:**

| arm | c2 | 95% CI | MDE | verdict |
|---|---|---|---|---|
| `oracle_k4_oracle_k{A,B}` | **+0.0779** | [+0.0701, +0.0853] | 0.0107 | **BEATS** |
| `greedy_k4_greedy_k{A,B}` | +0.0722 | [+0.0643, +0.0797] | 0.0105 | **BEATS** |
| `indep_k4_indep_k{A,B}` | +0.0527 | [+0.0447, +0.0600] | 0.0104 | **BEATS** |

**Controls.** Five positive: the reconstruction reproduces R294's stored `c2` for `coval_core`,
`topw_k4`, `gen`, `generic` and `oracle_k4` at **Δ = 0.00e+00**. Negative: an arm against itself
gives exactly 0 with a degenerate CI. Multiplicity: BH over C = 47.

⭐ `oracle_k4_oracle_kA` reproduces `oracle_k4`'s stored +0.077867 exactly, so the doubled-tag arms
behave as the same object — consistent with oracle-family construction.

⭐⭐⭐ **Settled: under the declared literal, widening the population to the 56 admits six
label-reading arms that BEAT ②, four of them outscoring every currently-admitted arm. Under the
derived gate, all six are excluded.** The fix is six lines (R520) and the cost of not applying it is
a leaderboard topped by arms that read the answer.

---

## R523 · The six are two — and R519 survives because its population had no aliases

**Exact matrix comparison, not a summary statistic:**

- all three A/B pairs are **byte-identical** → six tags name **three objects**;
- `oracle_k4_oracle_k{A,B}` **is exactly `oracle_k4`**, an arm the literal already declares.

⭐⭐⭐ **The literal misses TWO distinct objects — the greedy and indep families — not six.**

**This retracts three of my own claims.** R521's *"four of the six outscore every currently
admitted arm"* fails three ways: two of that four were `oracle_k4` itself; the remaining margin is
`greedy` **0.6292 vs 0.6283 = +0.0009, inside the MDE of ~0.0105**, with `indep` at **0.6079**
resolvedly below; and the arm being outscored is `oracle_k4`, which **③ excludes** — the comparison
baseline was itself a label-reader. R520's "6 missing" and R522's "6 of 6 BEATS" are counts of
**tags**; the per-tag verdicts hold, the population was never a list of objects.

⭐ **R519 is safe.** All 41 census arms are readable and **0 exact alias pairs** exist among them, so
its counts are counts of objects. **The definition ② ∧ ③ stands unchanged, as does ③ removing 4 of
the 9 ②-passers.**

⭐ **And the defect is still real:** two distinct label-reading objects that **BEAT ②** are admitted
by the literal and excluded by the derived gate. The six-line fix remains warranted. What is dead is
the framing — **not "a leaderboard topped by label-readers", but "two more label-readers admitted,
neither demonstrably above the admitted set."**

**Controls:** arm vs itself equal, `coval_core` vs `generic` unequal (positive); a shuffled copy
compares unequal, so the test is order-sensitive (negative). **Exact equality has no noise floor,
which is why it is the right instrument and a four-decimal agreement was the wrong one.**

---

## R524 · The tag population is 56 tags and 46 objects

Partitioning all 56 home-judge tags under **exact** saturation-matrix equality: **46 distinct
objects, 10 duplicate tags in 8 classes.** Controls: the partition recovers **4/4** of R523's
hand-found identities (positive); `coval_core` ≠ `generic` and a shuffled copy does not match its
original (negative, order-sensitive).

⭐⭐⭐ **Most of the collapse is intentional and that is why it went unseen.** `topw_k4_det{A,B}` is
a determinism check whose correct outcome is byte-identity; `random_k4_s{0,1}_ctlS{0,1}` are control
tags; `generic_reprov` is a re-provenance run. **They are supposed to be duplicates. Only their
effect on denominators is a defect.**

**What moves:** R436's *"0 of 56 excluded at J"* has a denominator of **46 objects** — the **zero is
unchanged**. **What does not:** R518's per-arm margins (4.90×–8.65× MDE) and R519's *"③ removes 4 of
9"*, since R523 measured **0** alias pairs among R294's 41.

⚠ **One flag:** `random_k4_s1` — R516's null — has a byte-identical twin tagged `_ctlS1`. The null
stands, but **a tag named as a control that is the same object as what it controls cannot control
anything**, and nothing in the name says so.

---

## R525 · Three variant runs produced no variant, and the source said they should

**The wall fell first.** R524 called the duplicates' intent *"a question about the generating
invocations rather than about the artifacts."* **`select_core.py`'s own `--select-npz` help text
makes the prediction**: the five satisfaction-consuming rules *"change IDENTITY, not just score"*
under a second selection, while `random_k`, `topw_k`, `topabs_k`, `full` are *"satisfaction-blind
and the two specifications coincide for them exactly."* **Fourth false wall of the session.**

**Splitting R524's 8 duplicate classes by that rule partition:**

| | classes | reading |
|---|---|---|
| satisfaction-**blind** | **3** | `topw_k4_det{A,B}`, `random_k4_s{0,1}_ctlS{0,1}` — **duplicate is correct** |
| outside the rule families | 2 | `coval_core_2b{A,B}`, `generic_reprov` |
| ⛔ satisfaction-**consuming** | **3** | `oracle_k`, `greedy_k`, `indep_k` — **should have differed** |

⭐⭐⭐ **So three variant runs were designed to change identity and produced byte-identical
artifacts — a control that did not control.** Controls: all 3 blind-rule variants ARE duplicates, as
the source predicts (positive, and a differing blind variant would have voided the partition);
`oracle_k4` ≠ `oracle_k4_fit1`, so the consuming family can produce distinct objects (negative).

**This gives R523's "alias" a mechanism.** `oracle_k4_oracle_kA` is not a deliberate alias but a
**failed variant run**. ⭐ **And the campaign's "six missing label-readers" trace entirely to three
such runs** — the literal misses **2 distinct objects**, both existing only because a variant run
produced no variant.

⚠ **R524's `_ctlS1` flag is WITHDRAWN.** Those tags are `random_k`, satisfaction-blind, so their
identity is the documented correct outcome. **I flagged them on the naming convention rather than on
the rule — a label read as a description.**

---

## R526 · Closure — the variant mechanism works where the invocation is recorded

**The wall fell first, fifth of the session.** R525 closed saying only "whatever produced them"
could settle the remaining tags. **`corebench/rebuild_selection_08b.sh` records a natural experiment
for the mechanism**: `frozen()` passes `--select-npz` (selection fixed), `rerun()` omits it (rule
re-run under the new judge). **Five arms get both treatments, all five satisfaction-consuming.**

**All 5 pairs differ.** Pre-registered kill was ≥1 identical; it did not fire. Positive control:
`_08b` differs from the home-judge arm of the same name in **5/5**, so the judge swap genuinely
changed the artifacts and the family is not a mislabelled copy.

⭐⭐⭐ **So `--select-npz` does change identity when invoked, and R525's reading stands: the three
home-judge identities are runs where the variant treatment was never applied.**

⚠ **Limit, stated:** this tests the **mechanism** on the second-release population. The home-judge
A/B invocations are genuinely unrecorded — the round establishes the flag is capable of what R525
assumed, not what was typed elsewhere. **Labelled CLOSURE, not a new world.**

---

## R527 · ②'s baseline is a choice, and the baseline-robust arms are the ones ③ excludes

**Sweeping ②'s comparator across its own reference class** — all C(16,4) = 1,820 pool subsets, k=4
arms, R294's estimator:

| baseline | A2 | admitted |
|---|---|---|
| p0 | 0.5144 | **8** |
| p5 · p25 · p50 | 0.5242–0.5391 | **7** |
| p75 · p95 · **PUBLISHED (0.5504, pct 93.7)** | 0.5446–0.5511 | **6** |
| p100 | 0.5575 | **4** |

**The published reference is `POOL[0:4]`, picked by FILE ORDER, landing at percentile 93.7** — a
strict comparator, and the extension moves from **4 to 8** across the class.

⭐⭐⭐ **The four arms admitted at every specification are exactly the four ③ excludes.** The
label-readers are baseline-robust *because* they read the answer; **every arm whose admission is
contingent on the pick is a ③-admissible one.**

⭐ **`coval_core` clears ② at 7 of 8 specifications**, failing only against the strongest of 1,820
subsets — an extreme order statistic, so over-strict by §4. **Its admission is robust; its scope is
not "beats the prompt-blind pool" but "beats it at every baseline below the class maximum."**

**Controls.** Positive: **16/16** k=4 arms reproduce R294's stored `c2` at **Δ ≤ 1e-6**. Negative: a
subset against itself gives exactly 0. ⚠ The first version failed its own positive control and
returned UNVERIFIED, targeting R439's 0.5537 — **a different annotator draw**; 0.5504 is R514's
measured bar₂ maximum, i.e. R294's scale. **The control was comparing two different objects.**

**What the formulation owes:** ②'s *"best generalising prompt-blind criterion set"* hides a choice.
The record should name the subset, that file order picked it, and that it sits at p93.7.

---

## R528 · The definition is non-empty only because "best" was not taken literally

R527 reported admitted-set **sizes**. Reading the p100 **membership** shows what the sizes hid: the
four arms admitted at the strongest baseline are exactly the four ③ excludes.

**Sweeping the upper tail of ②'s reference class, k=4 arms:**

| pct | baseline A2 | ② | **② ∧ ③** | surviving cores |
|---|---|---|---|---|
| 50 | 0.5391 | 7 | **3** | `coval_core`, `generic`, `topw_k4` |
| 75 – 98 | 0.5446–0.5529 | 6 | **2** | `coval_core`, `topw_k4` |
| 99 – 99.5 | 0.5545–0.5555 | 5 | **1** | `coval_core` |
| **100** | 0.5575 | 4 | **0** | ⛔ **(EMPTY)** |

⭐⭐⭐ **The deliverable said ② compares against "the BEST generalising prompt-blind criterion set."
Taken literally that is p100 — and there the definition has no extension at all.** The definition is
non-empty only because the published comparator is `POOL[0:4]` at **p93.7**, not the class maximum.

⭐ **`coval_core` is the last survivor**, holding alone from p99 to p99.5. **The released core is the
most baseline-robust ③-admissible arm in the class** — a genuine positive result about the object.

**Controls.** Positive: the published cell must reproduce R294's own admitted k=4 arms —
`['coval_core', 'topw_k4']` both ways. **PASS.** Negative: a subset against itself gives exactly 0.
⚠ **Scope: k=4 arms only**; arms at other k are outside this reference class.

**Wording corrected in `STATEMENT.md`:** ② now says *"a **strong** generalising prompt-blind
criterion set — the released pool's first four, at percentile 93.7 of its own 1,820-subset class"*,
with the emptiness at the maximum stated in the same clause.

---

## R529 · ③ has been two clauses the whole time, and the page asserted both

**The deliverable said, two sentences apart:** *"② is satisfied by `coval_core`"* and *"③ is what
**empties** the definition."* R294's census has `coval_core` passing both ② and ③, so both could not
hold. Tracing it: `DEFINITION.md` recorded R475 excluding `coval_core` as a **w-reader**, while
R294's code admits it.

**The release settles what a w-reader reads:**

- `DATASET_CARD.md:73` — annotators *"assign **signed weights** ranging from −10 to +10 … the
  absolute value indicated the **importance**"*;
- `DATASET_CARD.md:74` — core selects *"up to four rubric items with the **highest average
  ratings**"*;
- `select_core.py:16` — `topw_k` is *"the k criteria with the highest MEAN importance score.
  **Non-leaky: the weights come from the rubric, not from the outcome.**"*

⭐⭐⭐ **So the ratings ARE annotator-authored, and they are NOT the ranking labels A2 predicts.
`coval_core` is a weight-reader and not a ranking-reader — and ③'s phrase is two-valued:**

| reading | extension of ② ∧ ③ |
|---|---|
| **③-rank** — not built from the response **rankings** | **5**: `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` |
| **③-any** — no annotator signal for the prompt at all | **0 — EMPTY** |

**Controls.** Positive: under ③-rank the extension must equal R294's own `admitted` restricted to
②-passers — it does, exactly, so **③-rank is what the code implements**. Negative: the two readings
disagree on **16** arms, so the distinction is not vacuous.

⭐⭐⭐ **This resolves the campaign's central contradiction without retracting either sentence.**
*"② is satisfied by `coval_core`"* is true under ③-rank; *"③ empties the definition"* is true under
③-any. **Neither said which reading it used, and the difference is exactly "the released core IS a
core" versus "no core exists."**

⚠ **Which reading is right is NOT a measurement.** The card describes construction, not a definition
of core. The impossibility register already carries this as **row 7 — a decision about purpose** —
and this round makes it concrete: *does a core have to be producible without any annotator input for
that conversation, or only without the outcome it is scored against?*

---

## R530 · What the empty world costs: 1.29 MDE

R529 forked ③; under **③-any** the extension is empty. **A verdict of "empty" is not a
specification**, and register row 4 asked for *"a strong ③-admissible prompt-aware arm"* without
saying how strong. Measured from R294's stored contrasts:

| ③-any-admissible arm | c2 | MDE | shortfall | mode |
|---|---|---|---|---|
| `generic` | **+0.0009** | 0.0022 | — | **UNRESOLVED** |
| ⭐ `gen` | **−0.0153** | 0.0119 | **1.29 MDE** | LOSES |
| `full` | −0.0310 | 0.0119 | 2.60 MDE | LOSES |
| `random_k12_s0` | −0.0332 | 0.0122 | 2.74 MDE | LOSES |

⚠ **`generic` is excluded from the headline on purpose**: it is a *fixed blind set* measured against
the *blind pool*, so the contrast is near self-comparison — its interval straddles zero. **Row 4 asks
for a prompt-RESPONSIVE arm, and the closest one is `gen`.**

⭐⭐⭐ **So the ③-any world is 1.29 MDE from non-empty, and what would fill it is a `gen`-like
generator ~0.0153 A2 stronger.** "EMPTY" understates how close it is.

**Controls.** Positive: `ok2` reconstructed from each stored `(eff, lo, hi, mde)` via
`report.verdict` matches the census for **41 of 41** arms — so the reading of *why* an arm fails ②
is the code's, not mine. Negative: both failure modes are present (**29** resolvedly-below, **3**
unresolved), so "shortfall" does not conflate them.

**Register rows 3 and 4 now carry the fork and the number.** They were always ③-any rows; under
③-rank neither binds.

---

## R531 · Prompt-responsiveness derived, and the 1.29 MDE survives

**R530's "prompt-responsive" filter was a hardcoded tuple** — `a in ("gen","gen_sham") or
a.startswith("promptecho")` — **the exact defect R520 logged in `USES_PROMPT_LABELS`, committed
three rounds later by its author.** Its closing line then claimed `gen` was *"the ONE"* such arm,
which a hand-written list cannot establish.

**Derived instead from the artifacts** — an arm is index-varying iff its criterion index set differs
across prompts: **18 of 41 vary, 14 are also ③-any-admissible.** `gen` is the closest at
**1.29 MDE**, then `full` at 2.60, then the `random_k12/8/6` family, out to `full_sham` at 5.83.

⭐⭐⭐ **R530's number survives; only the word "one" was wrong — the set has 14 members.**

**Controls.** Positive: `coval_core` VARYING, `generic` BLIND. Negative: `random_k6_s0` is
index-varying while **prompt-blind by construction**, so the proxy measures index variation and not
semantics. ⚠ **That control took two repairs** — it first named `random_k4_s0`, which R294 **skips**
as the clause-① comparator so it could not run, and which loaded directly comes out **FIXED**,
because at small k the same indices exist in every prompt. **The instrument was right both times;
my expectation was wrong.**

⭐ **A fact surfaced in passing and worth carrying: the clause-① comparator `random_k4_s0` uses the
SAME criterion indices for every prompt.** Nothing in the record said so.

**Proxy limit, now demonstrated rather than asserted:** index variation is sound for *"the criteria
differ by prompt"* and **not** for *"the criteria were written for this prompt."*

---

## R532 · The ③ fork costs +0.0748 in A2

**My previous closing line proposed auditing `random_k4_s0` "because clause ① compares every arm
against it" — clause ① was retired eight rounds ago.** The comparator matters for a different
reason: `coval_core`'s **+0.0738** over it is what prices the ③ fork, and R531 showed it uses the
**same criterion indices for every prompt**.

**Re-measured against a TRUE per-prompt uniform 4-draw from each prompt's own rubric, 3 seeds:**

| | |
|---|---|
| published (fixed-index) | **+0.0738** |
| per-prompt draw, 3 seeds | **+0.0748**, spread 0.0030 |
| ratio | **1.01×** (kill at 0.50×) |

**Controls.** Positive: the fixed-index contrast reproduces R294's stored `c1` at
**+0.073790 = +0.073790**, so both comparators share a scale. Negative: the per-prompt draw varies
across prompts where `random_k4_s0` does not.

⭐⭐⭐ **So ③-any forbids an operation worth +0.0748 in A2 — selecting rubric items by their
annotator-assigned weights rather than at random.** Against R530's finding that the ③-any world sits
**1.29 MDE ≈ 0.0153** from non-empty, **the forbidden operation is worth ~5× the gap.** ③-any is not
marginally restrictive; it removes the largest single source of advantage a ③-rank core has.

⭐ **And the fixed-index property did not bias the number** — a flag I raised that turned out not to
bite, which is worth saying as plainly as if it had.

---

## R533 · Weight-reading is the operation, not the core: a dose curve to a forced zero

My previous closing line called `topw_k4` *"the other admitted arm that reads weights"* — **there
are four**, which turns one check into a dose-response.

| arm | k | advantage over a per-prompt random draw @k | spread |
|---|---|---|---|
| `coval_core` | 4 | **+0.0726** | 0.0031 |
| `topw_k3` | 3 | +0.0724 | 0.0057 |
| `topw_k4` | 4 | +0.0705 | 0.0015 |
| `topw_k6` | 6 | +0.0644 | 0.0007 |
| `topw_k8` | 8 | +0.0585 | 0.0020 |
| **`full`** | **15** | **+0.000000** | 0.0000 |

⭐⭐⭐ **`coval_core` (+0.0726) is indistinguishable from `topw_k4` (+0.0705): the released core's
advantage IS generic top-weight selection.** The number prices the **operation**, not the object.

**Controls.** Positive: `coval_core` reproduces R532's +0.0748 at +0.0726, within its seed spread.
Negative: `full` selects every criterion, so weight-reading can be worth nothing — **+0.000000,
exactly**. ⛔ **That zero is a DERIVATION** (at k=all both arms take the same items), which is what
makes it a good endpoint: **a curve failing to hit it would indict the construction.** It hits to
six decimals.

⭐ **So the fork's price is a curve: ③-any forbids an operation worth +0.0726 at k=4, decaying to 0
by k=15.** Fewer items kept ⇒ selecting them by weight is worth more.

⚠ **Not shown: that the weights are GOOD.** This prices reading them, not whether the annotators
were right — register row 6, an external standard.

---

## R534 · ③ has three input classes, not two

R529's partition put `topvar_k`/`topwvar_k` in the **weight** bucket. `select_core.py` disagrees:
`topw_k` sorts on `-w[i]` and `topabs_k` on `-abs(w[i])` (**annotator weights**), while `topvar_k`
sorts on `var(ssat)` — **judged satisfaction** — with the code's own comment: *"Non-leaky: the spread
is a property of the **responses**, never of the human target."* `topwvar_k` reads both.

⭐⭐⭐ **So an arm can read the responses' judged satisfaction while reading no human input at all**
— a class ③-any's phrase does not cover, **because a judge is not an annotator.**

| class | n | | reading | extension |
|---|---|---|---|---|
| rank | 4 | | ③-rank | **5** *(R529: 5)* |
| weight | 10 | | ③-any | **0** *(R529: 0)* |
| **sat** | **1** (`topvar_k4`) | | **③-judge** *(new)* | **0** |
| weight+sat | 1 | | | |

**Both extensions unchanged — R529's conclusion survives and only its taxonomy was wrong.** On this
population ③-any and ③-judge coincide because no ②-passer is in the `sat` class; **a future
satisfaction-reading arm clearing ② would separate them.**

**Controls.** Source read: 4/4 selection expressions confirmed verbatim. Positive: the ③-rank
extension equals R294's own `admitted` restricted to ②-passers. Negative: all three classes
non-empty on real arms.

⚠ **Register row 7 now carries three options, not two:** must a core be producible without the
rankings, without any annotator signal, or without any judged signal either?

---

## R535 · ③-judge is remote, and spread-selection loses to weight-selection

**Pricing the third reading rather than restating its verdict:**

| arm | reads | A2 | shortfall (MDE) | ② |
|---|---|---|---|---|
| `coval_core` | weights | **0.5665** | −1.51 | **True** |
| `topw_k4` | weights | **0.5642** | −1.26 | **True** |
| `topwvar_k4` | weights+sat | 0.5040 | 3.24 | False |
| `topvar_k4` | **sat** | 0.4863 | **4.24** | False |

⭐ **③-judge is 4.24 MDE from becoming distinguishable, against `gen`'s 1.29 for ③-any** *(R530)* —
**remote, not nearly-live.**

⭐⭐⭐ **And the release's own selection rationale is refuted.** `select_core.py` argues in a comment
marked *"DERIVATION, not a hunch"* that spread-selection is **"the direct fix"** for `topw_k`'s
blindness to arithmetically-inert criteria. **Measured, `topw_k4` 0.5642 beats `topvar_k4` 0.4863 by
0.0779**, and the hybrid `topwvar_k4` at 0.5040 is still **0.0602** below weights alone.

**The mechanism in the comment is right** — an inert criterion flips no pairwise sign. **The
inference is wrong: selecting FOR spread optimises the wrong quantity, because high spread with low
importance is noise.** Even multiplying importance by spread loses to importance alone.

**Controls.** Source read: rationale confirmed verbatim. Positive: `ok2` reconstructed for **41/41**
arms. Negative: `topw_k4` and `coval_core` **clear** ②, so the shortfall scale is anchored on both
sides. ⚠ **Scope correction to R534:** one sat-class arm in *this census*; `topvar_k4_08b` and
`_08bR` are on the second release. ⚠ **Impossible here:** whether spread wins under a different
judge — register row 2.

---

## R536 · The selector ordering survives a second judge

**The wall fell first, for the sixth time.** R535 closed saying a second judge needs *"an install"*.
**`rebuild_selection_08b.sh` had already re-run every selection arm under the 0.8B judge** — 32
`_08b` artifacts on disk.

**Which arms, from the source:** `topw_k` is satisfaction-blind, so its frozen and rerun
specifications *"coincide exactly"* — hence **no `topw_k4_08bR` exists**, and `topw_k4_08b` *is* the
0.8B-judge topw arm. `topvar_k4_08bR` is the 0.8B-judge topvar arm.

| judge | n | topw | topvar | diff | 95% CI |
|---|---|---|---|---|---|
| **2B** | 968 | 0.5642 | 0.4863 | **+0.0779** | [+0.0679, +0.0879] |
| **0.8B** | 968 | 0.4646 | 0.4009 | **+0.0636** | [+0.0551, +0.0720] |

⭐⭐⭐ **Weights beat spread under both judges. R535's refutation of `select_core.py`'s own "direct
fix" rationale is a fact about SELECTION, not about the 2B model** — and the `cross-model` criterion
the register lists as needing another site is **met on this one**.

**Controls.** Source read: the satisfaction-blind claim confirmed, and the **absence** of
`topw_k4_08bR` confirms it operationally. Positive: `topw_k4_08b` differs from `topw_k4`, so the
judge swap bit. Negative: `topvar_k4_08b` differs from `_08bR`, so the 0.8B topvar arm is a distinct
object. ⚠ **Correction to my own caveat: both judges resolve to n = 968, not different populations —
an over-cautious scope statement is still a wrong one.**

---

## R537 · The dose curve replicates under the 0.8B judge

R533 measured weight-selection's advantage over a per-prompt random draw at matched k under the 2B
judge. Re-run under the 0.8B judge, using `topw_k*_08b` and `sat08_full`:

| k | 2B | **0.8B** | ratio |
|---|---|---|---|
| 3 | +0.0724 | **+0.0521** | 0.72 |
| 4 | +0.0705 | **+0.0519** | 0.74 |
| 6 | +0.0644 | **+0.0443** | 0.69 |
| 8 | +0.0585 | **+0.0410** | 0.70 |
| **all** | +0.000000 | **+0.000000** | — |

⭐⭐⭐ **Positive at every k, monotone, exact zero at the endpoint, under both judges — and
attenuating consistently to ~0.7× under the weaker one.** Weight-reading's value is a fact about
**selection**, replicated cross-model for the second time *(R536 was the first)*.

**Controls.** Positive: all **4** 0.8B arms differ from their 2B namesakes, so this is not the same
measurement twice. Negative, forced: k=all returns **+0.000000** — a derivation, and the reason it
is a good endpoint is that a curve missing it would indict the construction.

⭐ **A naming trap worth carrying:** `sat_<arm>_08b` are the rebuilt **selection arms**;
`sat08_full` is the 0.8B **judging of the full rubric**. **`sat_full_08b` does not exist** — reading
its absence as missing data would have made this round look impossible.

⚠ **`sat_coval_core_08b` is absent, so the released core is the one admitted arm whose curve
position is unreplicated.**

---

## R538 · No second judging of the released core, and the first wall to survive

**The wall check, which this session has run seven times and which failed six:** artifacts from a
judge stronger than the home 2B are **`*_7b*` → 0, `*qwen*` → 0**. **This one holds.** Six false
walls made "my walls are false" feel like a law; it was a tendency, and only checking each one
distinguishes them.

**And `coval_core_2bA` is not the missing second judging.** R524 had it in a duplicate class not
containing `coval_core`, with no documented prediction. Measured: it covers **200 prompts** against
`coval_core`'s 968, and on the **200 shared prompts 0 cells differ**. It is the **same judging on a
subsample**; its identity to `_2bB` is the correct outcome for a deterministic judge run twice.

**Controls.** Positive: `coval_core` vs its **sham** on the same 200 shared prompts differs on
**200 of 200**, so a zero is a measurement rather than silence. Negative: `coval_core` against
itself gives **0**.

⭐ **So R537's gap is real: the released core is the one admitted arm whose cross-judge position
cannot be replicated from anything on disk** — and `Qwen2.5-7B-Instruct`, register row 2, remains
**an install**, now verified rather than assumed.

---

## R539 · The on-site round is 16,440 model calls

My last line said the honest version of *"why not run rows 3 and 4"* is a cost that had not been
measured. It is measurable exactly, because **`gen` already exists** — a generation round has been
run here, so the work is readable rather than estimated.

| component | calls |
|---|---|
| generation — one criterion set per prompt | **968** |
| judging — 16 satisfaction cells per prompt × 968 | **15,472** |
| **TOTAL** | **16,440** |

⭐⭐⭐ **Comfortably within one local-model session. Cost cannot be the reason not to spend rows 3
and 4.**

**Controls.** Positive: the counter must read judge cells, so `topw_k4` must give exactly **k × 4 =
16** per prompt — it does. Negative: `full` keeps every criterion and must exceed any k-limited arm
— **60 > 16**.

⚠ **Not measured and not guessed: wall-clock and money.** Converting 16,440 calls to time needs a
measured tokens/sec for the local model on this GPU, through pueue. **That is the one number a "why
not" would have to cite.**

⭐ `coval_core` ranges **[8, 16]** cells per prompt and `gen` **[4, 16]** — consistent with the
dataset card's *"about 95% end up with four … the remainder two or three."* **The artifact and the
card agree without being asked to.**

---

## R540 · R541 · The on-site round is 25.3 minutes, and the first figure was 17× too high

**R539 priced one rows-3/4 round at 16,440 model calls and named wall-clock as unmeasured.**
R540 measured decode throughput on the two sizes that *are* the campaign's judges — **89.2 tok/s
(0.8B), 80.6 tok/s (2B)**, both controls passing — and converted it to **7.25 h**.

⛔ **The conversion was wrong. The judging step does not decode.** `judge_core.py` calls
`Judge(model).score(prompts)` on a batch and contains no `generate()`; R417, quoted in that file's
own provenance comment, had already established the judge has no stochastic step.

⭐ **And the project had measured the right thing four times, in its own pueue logs**, because
`judge_core.py:117` prints elapsed seconds beside the call count:

| task | calls | seconds | calls/s |
|---|---|---|---|
| 634 / 635 / 636 | 3,168 | 40.1 / 40.0 / 40.0 | 79.0 / 79.2 / 79.2 |
| **642** | **15,488** | **199.3** | **77.7** |

| step | time |
|---|---|
| judging — 15,472 calls @ 77.7/s | **3.3 min** |
| generation — 968 × 110 tok @ 80.6 tok/s | **22.0 min** |
| **TOTAL** | **25.3 min** |

**Controls.** Positive: three replicates agree at **0.25%** spread. Negative: **4.89×** the work took
**4.98×** the time — throughput, not startup.

⭐ **R540 is not void — its decode figure is the right instrument for the GENERATION half.**
**A correct measurement pointed at the wrong operation is a wrong APPLICATION, and only naming the
instrument's unit and the claim's unit separately catches it.**

⭐ **Register row 2 is confirmed by a real failure**, not asserted: pueue task 654 (`r492-7b-b2`)
attempted Qwen2.5-7B judging on 2026-08-04 and died with
`torch.OutOfMemoryError: 14.60 GiB in use of 15.40 GiB`. **R538's "no 7B artifacts exist" now has
its mechanism — attempted, not unattempted.**

## R555 · Register row 2 named a model where it meant a requirement — and it is unblocked

Row 2 read *"a second, stronger judge — `Qwen2.5-7B-Instruct` is present (29 GB, 4/4 shards) but
OOMs in bf16"*, and treated **that model's** OOM as the row's blocker. The **requirement** is a judge
stronger than the home judge. `covalx/judge.py:48,258` name the campaign's two judges as
`Qwen3.5-2B-Base` (home) and `Qwen3.5-0.8B-Base` (second) — so anything above 2B satisfies it.

**`Qwen/Qwen3.5-4B` loads and scores.** On 24 real prompts from the home release, judged through
`covalx.Judge` exactly as the campaign does:

| judge | peak VRAM | secs | distinct scores | mean |
|---|---|---|---|---|
| `Qwen3.5-2B-Base` (home, positive control) | **4.00** GB | 4.3 | 15 | **0.4038** |
| **`Qwen3.5-4B`** | **8.89** GB | 21.2 | 16 | **0.4058** |

**8.89 against 16 GB is 7 GB of headroom** — not marginal. The negative control confirms a
nonexistent checkpoint fails to load, so *"it loaded"* is informative rather than vacuous.

⚠ **And the register's size for the 7B was wrong.** Every real copy on this box measures
**15.23** GB of safetensors, not 29 — consistent with an fp32 arithmetic slip (7.6B × 4 bytes).
At 15.23 GB the 7B's OOM on a 16 GB card is *tight*, not hopeless, which is a different claim from
the one the row was making.

⚠ **Scope: `stronger` remains a proxy.** 2× parameters in the same family is defensible and is not a
demonstration that the 4B is a *better* judge. What is demonstrated is that it **loads, fits, and
returns non-degenerate scores** — which is what row 2 said could not be had without an install.

## R556 · Row 5 offered two alternatives and one was already satisfied

Row 5 prices independent replication at *"another site"*, requiring *"a second team **or** a second
release"*. **The second release is on disk** — `data/utterances.jsonl`, 68.2 MB — and **3 of 376
artifacts** were computed on it *(R556)*, under `R398_…` · `R427_…` · `R433_…`.
⚠ Those directory names are **file provenance, not citations**: R398 and R427 predate the
`world` convention and record `verdict`/`controls` keys instead, so they carry evidence and
settle nothing. Only R433 has a world. **The count is this round's claim, not theirs.**

⚠ **Two axes, which I nearly conflated and which the register does too.** A *second **judge***
(`Qwen3.5-0.8B-Base`, used by R536/R537) scores **the same release**; a *second **corpus*** is a
different release. They discharge different criteria, and only the second is what row 5 names.

**So the row is wrong in KIND rather than in price.** What is missing is not a site — it is a
**second designer**, and §2.5 states that is dischargeable here by clean-context agents given the
QUESTION and never the ALGORITHM. ⚠ **Not available this session:** the operating instructions in
force forbid dispatching agents unless asked, so the remedy is named and **not** claimed as planned.

⚠ **My count was 4 before I read the hits.** The fourth was R550's gate audit, whose amended-rounds
dict holds the directory name `R399_what_estimand_does_the_second_corpus_admit`. **The instrument
matched a round's NAME and would have been reported as a corpus RESULT.**

## R557 · Row 1 measured VERBATIM overlap on an object its own card documents as a REWRITE

Row 1 blocks ③′ on the released core because only **6.6%** of core criteria appear verbatim in
`coval_full`, and asks for the field `coval_core[i].source_rubric_item_ids`. **The dataset card
documents a rewrite and merge before selection** — so a rewrite is precisely what an exact-match
instrument cannot see. **The row named an OBJECT where the requirement is a PROPERTY: a recoverable
mapping from core item to source items.**

Matching by **similarity** instead of identity, per prompt, over 968 prompts and 3,828 core items:

| | value |
|---|---|
| **POSITIVE CONTROL** — top-1 on the 298 items whose source is known verbatim | **1.0000** |
| **PLACEBO** — a *different* prompt's rubric matches at least as well | **0.0000** |
| margin (top1−top2), KNOWN median | **0.8035** |
| margin, UNKNOWN median (n=3,530) | **0.3101** |
| unknown items clearing the KNOWN set's 10th-percentile margin | **21.0%** |

⚠ **21.0% is a BOUND ON IDENTIFIABILITY, not an accuracy.** There is no ground-truth mapping — that
absence *is* row 1 — so accuracy is identified **only** on the verbatim subset and merely bounded
elsewhere. **Partial identification means bounds, not a point.**

⚠ **My verbatim share is 7.8% (298/3,828), the row says 6.6%.** My normalisation — lowercase plus
whitespace collapse — is strictly more permissive, and a looser rule returning a larger share is
consistent rather than contradictory. **Both are reported; neither silently overrides the other.**

**So the row's PRICE is right for a COMPLETE mapping and wrong for the requirement.** A partial
mapping is available on this site with no new field, and the publisher's field remains the only
route to a *complete* one.

## R558 · The scope column named every axis but the one that empties the definition

Register row 6 asks *"construct validity — is A2-vs-held-out-annotator the right target?"* and
prices it at **another site**. **That is two questions in one row.** Construct validity — does A2
measure core-ness — genuinely needs an external standard. **Target robustness — does the choice of
agreement statistic change the answer — was measured on this site and the artifact has been on disk
throughout.**

**968 prompts, six targets, four distinct admitted sets** *(R558)*, from the sweep artifact
under `R288_does_the_partition_survive_the_target/results/target_sweep.json` — named as file
provenance, because that round predates this campaign's `world` convention and settles nothing
on its own:

| target | admits |
|---|---|
| `A2·annot`, `A2·consensus` | `coval_core`, `topw_k4` |
| `A1·annot`, `A1·consensus` | **∅** |
| `tau·mean` | `coval_core` |
| `top1·mean` | `topw_k4` — **not** `coval_core` |

**And the claim table did not say so.** Parsed mechanically: **10 of 10** rows name a known axis
(judge, prompts, arms); **0 of 10** name the target. The positive control is what makes that zero a
measurement rather than silence — the parse demonstrably sees scope tokens.

⭐⭐⭐ **So every extension count on the page — the 5, the two 0s — has been readable as
unconditional, while two of six defensible targets send the extension to zero and a third excludes
the only released core.** The fix is one scope note above the table, stated once: a scope restated
per row drifts, and the copy is never the one that gets corrected.

## R559 · The B recommendation is one cell of a two-cell curve, and row 7 calls it "not a measurement"

Register row 7 reads *"whether reading **A** is correct after all"*, removed by *"a use for 'core'
that does not require prediction"*, priced as **"not a measurement — a decision about purpose"**.
**But the recommendation of B rests entirely on a measurement**: `oracle_k4` clearing the ranker
ceiling, because an object that beats the bound for its own class is reading rather than predicting.

**Two rounds computed that gap. Both persist 4-of-4 passing controls. Their ratios straddle P14's
admissibility line of 1.5.**

| instrument | gap (rank) | floor | **effect / floor** | admissible |
|---|---|---|---|---|
| `R505_…` | **0.009527** | **0.022039** | **0.432** | **no** |
| `R506_…` — the cell on the statement | **0.007338** | **0.004666** | **1.573** | barely |

**Range 0.432 – 1.573, a spread of 3.64×, and the page shows one cell.** G4 asks for the whole
specification curve including the cells that kill the finding; **this is the curve, and one of its
two cells kills it.**

⚠ **What is NOT claimed here.** R506 argues by derivation that only the ranker ceiling applies —
`corebench/score.py`'s `yvec()` returns one scalar per response, so a core's six verdicts are
necessarily transitive. **That derivation is not attacked.** What is shown is narrower and enough:
the *floor* against which the surviving gap is judged differs by **4.7×** between two rounds whose
controls both pass, and only the flattering one is published. **A negative control excludes the
cross-round ratio (0.333) as a cell nobody ran.**

⭐⭐⭐ **So row 7 is wrong in the same way rows 1, 2, 5 and 6 were, and worse: it does not merely name
an object where a property is meant — it declares a measurement to be a decision, which removes the
question from the register's own jurisdiction.** The decision about purpose is real and downstream;
the measurement in front of it is at **1.57 by one instrument and 0.43 by another.**

## R560 · The scope column's defect is a SHAPE, and `baseline` was stated by zero rows

R558 found the **target** missing from 10 of 10 claim rows and fixed it with one note. That was one
axis, found by hand. **G1 requires four.** Measured across all ten rows:

| dimension | rows stating it |
|---|---|
| **baseline** | **0 / 10** |
| **regime** | 4 / 10 |
| instrument | 6 / 10 |
| population | 8 / 10 |
| **all four** | **0 / 10** |

**The positive control is what makes the zero admissible**: `population` was found in **8 of 10**, so
the vocabulary demonstrably matches this page's own usage. **An axis vocabulary that finds nothing
everywhere is a broken vocabulary; one that finds `population` in 8 rows and `baseline` in none is a
measurement.** A negative control (an invented axis vocabulary) matched **0** rows.

⭐⭐⭐ **`baseline` at 0/10 is the consequential one.** ②'s comparator is `POOL[0:4]` **by file
order**, at percentile **93.7** of its 1,820-subset reference class — and **the extension moves
4 → 8 across that class.** So every extension count on the page was conditional on a baseline the
page never named, in the same way it was conditional on a target the page never named.

⭐ **This is why the fix is structural rather than another note.** Patching one axis per round would
have taken four rounds and converged on nothing, because the defect is that **the column had no
shape**: it was prose, and prose omits silently. The constants now sit in one table with four named
fields, and a row's own cell carries only its departures from them.

---

## R602 · The two corpora are disjoint on the string axis

Re-derived directly from `data/comparisons.jsonl` (home, **1078** distinct prompts) and
`data/utterances.jsonl` (second, **68371** rows carrying a text key, **26673** distinct), because
R399's *"3 strings, 2 of them greetings"* was an **exact-match** count and comparability need not be
an exact-match question.

| definition of overlap | home vs second | shuffled-vocabulary floor |
|---|---|---|
| exact identity | **0** | 0 |
| normalised identity | **0** | 0 |
| token-Jaccard, median max per prompt | **0.1654** | **0.1654** |

Per seed, real vs floor: **0.1667 / 0.1667 · 0.1628 / 0.1628 · 0.1667 / 0.1667**. p90 **0.2117**
against a floor of **0.2117**. Maximum observed **0.2778**.

⭐ **The real and shuffled medians are identical to four places**, so the apparent token overlap is
**shared English function words with no shared content.** The negative control — shuffle tokens to
preserve the vocabulary and destroy the strings — is what makes that separation, and the gap it
measures is **0.0000**.

**Controls:** home-vs-home returns exact **1078/1078** and Jaccard max **1.0000**; the synthetic
placebo returns exact **0** and Jaccard max **0.0000**.

⚠ **Bounded below:** the Jaccard sweep runs against a **3000**-text subsample, so a max over a subset
cannot exceed the max over the whole — a small value is conservative.

⚠ **Discrepancy, reported:** R399 says **3**, this says **0**. Different extractions of the home
population; the direction replicates and the exact figure does not.

⚠ **IMPOSSIBLE:** string overlap is not topical comparability. A corpus can share no strings and ask
the same question. One axis, bounded.

---

## R606 · Provenance recording misses the page's own sources

The corpus carries a source-hash mechanism: **109** of **426** parseable artifacts (**25.6%**) hold a
`source_sha256` / `source_name` / `sha256` / `src_sha` key. Adoption by citation status, at the round
level over 377 rounds with artifacts:

| | cited by `STATEMENT.md` | not cited |
|---|---|---|
| rounds | 105 | 272 |
| **carry a provenance key** | **0.1143** | **0.2904** |

**Δ = −0.1762**, time-stratified permutation **p = 0.0003** over 12,000 draws; unstratified 0.0002.
At the stricter *non-empty value* level the picture is unchanged: **0.1143 vs 0.2868, Δ = −0.1725,
p = 0.0008.**

**Controls.** Plant — provenance stripped from every cited round — returns **Δ = −0.2904 at
p = 0.0001**; at g=0 the unplanted statistic reproduces **−0.1762** exactly; the placebo at the same
marginal returns **+0.0350 / +0.1011 / −0.0574** across three seeds.

⚠ **The dose-response MDE is DEGENERATE for this plant and is not used.** Stripping moves Δ monotonely
away from zero starting at the observed value, so the smallest planted |Δ| (**0.1857**) necessarily
exceeds the observed (**0.1762**) and the band cannot contain the observation. The observed effect is
judged by its own stratified permutation.

⚠ **Δ is a DERIVATION** forced by four counts over a complete enumeration; only the permutation p is
tested. ⚠ **A recorded hash proves a source was NAMED, not that the bytes match it**, so 0.1143 is an
upper bound on attributability.

---

## R607 · Which eras drive the provenance gap

R606's pooled gap of −0.1762 decomposed over five equal round-id bands, 378 rounds, 106 cited.
**Every cell is a DERIVATION** — a count over a complete enumeration; only the reconstruction check
is a test.

| era | round ids | n | cited | P(prov \| cited) | P(prov \| uncited) | Δ |
|---|---|---|---|---|---|---|
| 0 | — | 0 | 0 | — | — | UNDEFINED |
| 1 | 220–242 | 23 | 0 | — | 0.0870 | UNDEFINED |
| 2 | 243–364 | 118 | 3 | 0.0000 | 0.1739 | −0.1739 |
| 3 | 365–485 | 118 | 35 | **0.2571** | **0.6627** | **−0.4055** |
| 4 | 486–606 | 119 | 68 | 0.0441 | 0.0392 | **+0.0049** |

**Citation rate by era:** 0.0000 · **0.0254** · **0.2966** · **0.5714** — citation concentrates LATE.
**Provenance rate by era:** 0.0870 · 0.1695 · **0.5424** · **0.0420** — a 13× collapse between the
last two bands.

So the pooled value is two effects: a within-era selection in the best-documented band (era 3), and a
compositional effect from citing heavily into the band where the practice had collapsed (era 4).

**Controls.** The cell-weighted mean of the per-era Δs reconstructs the pooled value at **−0.1625 vs
−0.1772**. A random `cited` label at the same marginal returns **−0.0461 / −0.0199 / −0.0330**.
Shuffling provenance **within** each era gives per-era Δs of mean magnitude **0.0626** against the
pooled **0.1772**.

⚠ Two eras have an empty arm and their Δ is **UNDEFINED, never 0**. ⚠ Round id is a proxy for time,
not time; no artifact carries a timestamp.

---

## R608 · What separates era 3's documented cited rounds

Population: the **35** rounds in 365–485 that `STATEMENT.md` cites, split **9** with a provenance key
against **26** without. Era and citation are held fixed by construction.

**Power was computed before any feature was read.** Null distribution of max|Δ| over the whole
6-feature grid, 200 draws: median **0.2863**, p95 **0.4359**, max 0.5812 — so a feature must exceed
**0.4359** to clear the grid. The pre-registered kill (MDE above 0.50 ⇒ unresolvable regardless) did
not fire.

| feature | P(f \| provenance) | P(f \| none) | Δ |
|---|---|---|---|
| **`late_in_era`** | **0.3333** | **1.0000** | **−0.6667** — SURVIVES |
| `many_artifacts` | 0.1111 | 0.0000 | +0.1111 |
| `has_py` | 1.0000 | **0.9615** | +0.0385 |
| `has_readme` | 1.0000 | 1.0000 | 0.0000 |
| `big_readme` | 1.0000 | 1.0000 | 0.0000 |
| `has_npz` | 0.0000 | 0.0000 | 0.0000 |

Arc offers no contrast: all 35 are in `A24`.

**Controls.** A feature perfectly correlated with provenance returns |Δ| = **1.0000**; a feature
independent of it returns **0.2051**, below the grid null, so the instrument can fail; a constant
feature returns exactly **0.0000**.

⭐ **All 26 undocumented cited rounds are in the band's late half**, and every non-temporal feature is
flat. The separation is temporal, so **R607's within-era selection is partly an artifact of a
120-round bin**: the collapse happens inside era 3, not at the boundary drawn. The 13× figure stands;
its location does not.

⚠ A structural correlate is not a reason; why a round recorded its source needs the round's author.

---

## R609 · Where the unattributable evidence begins

Sweeping every admissible cut (at least 5 rounds each side) across band 365–485, cited rounds only,
n=35 with 9 carrying provenance. **26 cuts tested; the null is taken on the MAXIMUM across them**, so
the winning cut earns no credit for being the best of many.

**Best cut 434 · Δ = 1.0000** against a max-over-cuts null of median **0.3095**, p95 **0.4800**, max
**0.6333** over 400 label permutations.

Every cited round below 434 records its source; **not one at or above it does**. The right-hand side
is `P(prov | ≥ c) = 0.0000` at every cut from 434 through 477 — 0.6923, 0.6429, 0.6000, 0.5625,
0.5294, 0.5000, 0.4737, 0.4500, 0.4286, 0.4091, 0.3913, 0.3750, 0.3600, 0.3462, 0.3333, 0.3214,
0.3103 and 0.3000 on the left as the cut moves right, and zero on the right throughout.

**Controls.** A step planted at 450 is recovered **at 450** with |Δ| = 1.0000; provenance independent
of id returns max|Δ| = **0.2857**, below the null, so the instrument can fail; constant provenance
returns **0.0000** at every cut.

⚠ **The shape claim is one-sided.** The round also reported a rank correlation of **−0.1471** failing
to clear its null of **0.7961**, implying *step rather than slope* — but the outcome is binary with 26
ties, so that statistic is degenerate, and a perfect step is also the extreme slope. **The separation
is established; its shape is not.**

⚠ Round ids order the work; they do not date it.

---

## R610 · The switch appears in the uncited rounds too

The sweep of R609 rerun through one code path on both arms of band 365–485, each read against **its
own** max-over-cuts null because the arms differ in size.

| arm | n | with provenance | cuts | best cut | Δ | own null p95 | median | max |
|---|---|---|---|---|---|---|---|---|
| CITED | 35 | 9 | 26 | **434** | **1.0000** | 0.4800 | 0.3095 | 0.6333 |
| UNCITED | 83 | 55 | 74 | **428** | **1.0000** | 0.4923 | 0.2841 | 0.7051 |

**Distance between boundaries: 6.** Both switches are total — every round below the cut records its
source, none at or above it does.

**Controls, on the uncited arm.** A step planted at 412 is recovered **at 412** with |Δ| = 1.0000
against 0.5385. Provenance independent of id returns |Δ| = **0.4567** against its null of **0.4722** —
a pass by **0.0155**, narrow enough that the conclusion rests on the observed 1.0000 rather than on
the control's comfort. Constant provenance returns **0.0000** at every cut.

So the shortfall R606 measured is real and its cause is the **work**, not the **selection**:
provenance recording ended corpus-wide at ~430 and the page's citations concentrate after it.

⚠ A boundary in id order is not a change in practice — it is equally consistent with a reorganisation,
a renumbering or a gap in the record, and nothing here carries a timestamp.

---

## R611 · What else changed at the boundary

Band 365–485, **both arms pooled**, n=118, cut fixed at **B = 431** — the midpoint of R610's two
independently measured boundaries (434 cited, 428 uncited), **chosen before any feature was read**, so
no feature selects its own cut. Whole-grid null on max|Δ| over 9 random features, 200 draws: median
**0.1492**, p95 **0.2057**, max **0.2512**.

| feature | before | after | Δ | clears 0.2057 |
|---|---|---|---|---|
| provenance *(positive control)* | 0.9808 | 0.0455 | **−0.9353** | yes |
| `has_world` | 0.0455 | 0.9808 | **+0.9353** | yes |
| `has_controls` | 0.8788 | 0.3269 | **−0.5519** | yes |
| `readme_over_4k` | 0.7727 | 0.6154 | −0.1573 | no |
| `py_over_8k` | 1.0000 | 0.9231 | −0.0769 | no |
| `multi_artifact` | 0.1212 | 0.0577 | −0.0635 | no |
| `many_keys` | 0.6061 | 0.5577 | −0.0484 | no |
| `has_py` | 1.0000 | 0.9615 | −0.0385 | no |
| `has_readme` | 1.0000 | 0.9808 | −0.0192 | no |
| `has_mde` | 0.2273 | 0.2115 | −0.0157 | no |

The provenance and `world` shifts are **equal in magnitude and opposite in sign to four decimals**, so
the convention **substituted** a verdict field for a provenance field rather than losing one. The
`controls` fall is **unmirrored** and is a genuine reduction.

**Controls.** Provenance clears at the fixed B (**−0.9353** vs 0.2057), so the boundary survives
pooling and fixing; a feature independent of id returns **0.0262**, so the instrument can fail; a
constant feature returns **0.0000**.

⚠ A boundary in id order is not a date and a correlate is not a cause.

---

## R614 · How much of the era the claim table draws on

Population: rounds **431–606** with at least one parseable `results/*.json` — **171** of them. The
numbered claim table cites **17 distinct** rounds, spanning **519–581**; that span holds **63** id
positions and **63** existing rounds, so it is dense.

| quantity | value |
|---|---|
| coverage of the era | 17/171 = **0.0994** |
| coverage within the span | 17/63 = **0.2698** |
| observed mean gap between cited rounds | **3.8750** |
| null over 2,000 random 17-subsets | 5% **8.5000** · median **10.0000** · 95% **10.8125** |

The observed gap sits far below the null's 5th percentile, so the cited set is **more clustered than
chance**: the concentration is a habit rather than a shortage, and **154 rounds of the same era exist
and are not cited.**

**Controls.** A contiguous block of 17 returns a mean gap of **1.0000** against the same null, so
clustering is detectable; a random 17-subset returns **10.0625**, inside [8.5000, 10.8125], so the
instrument can fail; the full era as its own cited set returns coverage exactly **1.0000**. The
pre-registered kill required at least 10 cited rounds for the clustering statistic; 17 clears it.

⚠ Coverage is a **DERIVATION** over a complete enumeration — only the clustering is tested. ⚠ A
citation may carry a caveat rather than a number, so coverage bounds the evidence base from **above**.

---

## R615 · Does the citation selection track outcome?

Population: rounds **431–606** with artifacts (**171**), split by whether the numbered claim table
cites them (**17** / 154). Classification is the first token of `world`, case-folded and
punctuation-stripped — the rule `statement_provenance.py` already uses.

| quantity | value |
|---|---|
| rounds writing a `world` | 170 of 171 |
| with a classifiable first token | **117** = 0.6842 |
| classifiable among the cited | **17 of 17** |
| classifiable among the uncited | 100 of 154 |
| class mix | B **73** · A **27** · C **9** · UNVERIFIED **7** · D **1** |
| Δ on the most common class, cited − uncited | **+0.0271** |
| permutation null, 2,100 draws | **[−0.2482, +0.2335]** |

The observed Δ sits inside the null, so **the selection does not track outcome on the classifiable
slice**: R614's clustering is positional.

**Kill, evaluated before any distribution was read:** classifiable cited **17 ≥ 8** and smallest
expected cell **6.00 ≥ 5** — both cleared, so the comparison was admissible.

**Controls.** A synthetic population with cited all one class and uncited all another returns Δ =
**+1.0000**; classes assigned independently of citation return **−0.0200**; a constant class returns
**+0.0000** exactly.

⚠ Conditional on classifiability: that subset is non-random — R594 measured short values as commoner
late — so nothing here speaks for the 54 rounds whose verdict is unclassifiable. ⚠ A first-token class
is a convenience, not a type: R595 measured this field as open **corpus-wide**, which is a different
population from this era.

---

## R616 · Is the cited set's six-token rate more than chance?

Property: the first token of `world`, case-folded and punctuation-stripped, lies in
{A, B, C, D, E, UNVERIFIED}. **This is FORM, not legibility or quality** — R591's own value,
`"MIXED — …"`, is a well-formed verdict the rule excludes.

| quantity | value |
|---|---|
| era 431–606, six-token rate | 117/171 = **0.6842** |
| cited | **17/17 = 1.0000** |
| uncited | **0.6494** |
| Δ = cited − uncited | **+0.3506** |
| null, 2,100 random 17-subsets | 2.5% **−0.2372** · median **+0.0241** · 97.5% **+0.2200** |

The observed Δ sits **above** the null, so the cited set takes the six-token form more often than
drawing 17 rounds from the era at random would give. The pre-registered ceiling kill — unresolvable
if the era rate exceeds 0.95 — did not fire at 0.6842.

**Controls.** A cited set drawn only from six-token rounds returns **+0.3506**, ⚠ *identical to the
observation*, since the cited set already is 17/17 and the ceiling is 1.0: the control proves the
value is **attainable**, not that it could be **exceeded**, so the verdict rests on the null. A random
17-subset returns **+0.1547**, inside the interval, so the instrument can fail. A property every round
has returns **+0.0000** exactly.

Taken with R614 (position: clustered) and R615 (outcome: flat), the selection is sensitive to **when**
and **how** a round wrote and not to **what it concluded**.

---

## R617 · Does the `controls` key track controls being run?

Population: rounds **431–606** with artifacts (**171**). The property under test is a JSON key named
`controls` at any depth; the construct is checked against two independent signals before any contrast
is read.

| quantity | value |
|---|---|
| rounds writing the key | **0.1462** |
| rounds whose README discusses controls | **0.9006** |
| rounds whose `.py` carries control-shaped names | **0.8596** |
| agreement key ↔ README prose | **0.2339** |
| agreement key ↔ code names | **0.2865** |

Both agreements fall far below the pre-registered floor of 0.60, so the kill fired and the contrast
was **not read as evidence**. Ninety per cent of rounds discuss controls and eighty-six per cent carry
control-shaped code while fifteen per cent write the key: **the key is a schema habit.**

**So R611's `has_controls` fall from 0.8788 to 0.3269 is a schema change, not a loss of controls** —
retracting the one unmirrored casualty the R605–R617 arc had identified.

**Controls.** A round with key and signal alongside one with neither scores agreement **1.0000**;
shuffling the key across rounds moves agreement to **0.2456 / 0.1754 / 0.2105**, so the observed value
is not merely the marginal; a key every round has scores **0.9006**, exactly the signal's own rate
rather than 1, so the statistic does not saturate.

The contrast was computed and printed for completeness — Δ = **−0.1623** against a null of
**[−0.1623, +0.1642]** — and marked NOT READ AS EVIDENCE.

⚠ README prose and code identifiers are proxies too; agreement bounds the construct from above and
nothing here shows any round's controls were correct.

## R618 · What a next site must provide for clause ② to be evaluable

**This belongs in the definition and not only in the audit**: it is the condition under which the
definition can be *stated* about an object at all.

| a release must carry | it serves ②'s phrase | home | second |
|---|---|---|---|
| a prompt / user turn | *…for a conversation…* | ✓ | ✓ |
| multiple responses per unit | *…scores RESPONSES…* | ✓ | ✓ |
| a human preference target | *…better THAN…* | ✓ | ✓ |
| **a released criterion POOL** | *…drawn from the RELEASED POOL…* | ✓ | ⛔ |
| **a released CORE** | *…a CORE scores…* | ✓ | ⛔ |

Validated by reproduction against R603 — home evaluable, second not, missing exactly those two — with
the g=0 control showing that stripping the home release of the same two fields reproduces the second
release's exact failure. ⚠ **NECESSARY, NOT SUFFICIENT**: R602 measured the second corpus as disjoint
in content, which no schema check can see.

## R628 · What the assurance suite establishes about a number — the bound

> **Provenance cannot be INFERRED. It must be DECLARED, and then checked.**

Four register lines, each written as a prediction and tested by intervention; all four held.
**UNVERIFIED citation → CAUGHT · laundered value → NOT caught · a real value asserted as a different
quantity → NOT caught · a drifted re-derived label → CAUGHT.**

The two measured limits behind it: **the collision floor** — an invented decimal matches a persisted
artifact value **35.15 / 36.12 / 37.60%** of the time at 4 dp — R625's own verdict is
`UNVERIFIED`, since its decomposition's controls failed; **this null is the measured part**
(R625, 3 seeds × 4000) — and **the
rarity signal being the gate's own selection**, gate-verified precision **0.072 → 0.905** across the
threshold sweep against gate-blind **0.450 → ~0.70** (R627).

⚠ The drift was caught by transitive anchoring, not by re-derivation, so a drift in a value
`STATEMENT.md` does not also carry is untested. ⚠ The register's completeness is not testable from
its own lines.

## R631 · Clause ③'s testability — the bound, carried in from FORMULATION.md

**Clause ③ is decided per arm by reading `select_core.py`. That is an annotation, not a
measurement**, and whether it *could* be a measurement was tested along both available routes.
**Both bound out.**

- **Route 1 · through PERFORMANCE — REFUTED.** The leak slope has sensitivity **1.000** and
  specificity **0.886** blind over 41 arms, but `corr(slope, A2) = +0.934`, its four false positives
  are exactly the admitted set, and `oracle_k4` — the *maximally* leaky arm — sits **3.25 sd BELOW**
  what its quality alone predicts. **No residual leak signal.** The confound is structural: fitting
  on labels is *what makes an arm better*, so a performance detector measures the leak's effect and
  cannot be separated from it.
- **Route 2 · through SELECTION — one rule family only.** Label-free features of the selected
  criterion set reach **0.866** held-out-by-arm (structure+text), but **0.510 — chance — held out by
  MECHANISM.**

⛔ **Route 1's refutation also retracts R335**, whose 32.9-sd dose-response separated *dose-induced
quality*. R335's artifact still records `W-DECIDABLE`; **that verdict is superseded.**

⚠ Whether this bound is *correct* needs re-running R336–R338, which this site cannot do. What R631
established is that it was **stated only in `FORMULATION.md`**, which no gate reads.

## R704 · What the generator's name is worth once an arm is held out

R693 measured that clause ②'s verdict is **88.1%** predictable from the arm's rule family, and R694
that a memorising fit on `(family, k)` scores **95.2%**. Both are fits scored on their own data and
both said so. R704 measures the matching floor: **leave-one-out**, against the **base rate** (the
majority class, no partition at all), over **all 42 arms** rather than over the arms a clause happens
to exclude.

The gain from the `(family,k)` partition for clause ② is **+0.000** — base rate **0.786**, with the
partition **0.786**. Across five partitions (`family` · `k` · `(family,k)` · `(family,k,sham)` · a
single cell) the best gain is **+0.048**, two arms of 42, and **no partition clears its own
2000-draw permutation null**. F1 provenance reaches **+0.048** at best. F3's **+0.286** under a
`k`-partition is a **derivation**, not a measurement: F3 *is* the predicate `1 < k <= 4`.

So the asymmetry R703 opened — clause ② carrying 20 unique exclusions against 4 and 2 — is a
**count**: ② excludes **33 of 42** arms, and a demanding clause produces many unique exclusions
whatever it encodes. At n=42 the resolution is **0.024** per arm, so the cross-clause ordering is
reported and the cross-clause difference is not.

Two designs failed before the object did, each caught by a control registered before the run. The
round's registered headline — a cell-determined share — was refuted by its own **sham**: a
single-cell partition scored **1.000** against the treatment's **0.650**, because under one cell every
prediction books as cell-determined. And the registered population was **outcome-conditioned**:
evaluating a clause on its own exclusions fixes the base rate at 1.000 for any clause excluding a
majority and 0.000 for any clause excluding a minority, by algebra, before any data is read. That
population was named in R703's closing sentence, so the defect was inherited from the question.

## R705 · What gain this design can detect, and what that withdraws

R704 reported the `(family,k)` partition as worth `+0.0476` to clause F1 and `+0.0000` to clause ②,
and read a difference between them. R705 prices that number against the design's own floor.

The minimum detectable gain — the smallest true partition-attributable gain at which this design
rejects its own nuisance-matched permutation null at alpha 0.05 with power 0.80 — was measured by a
count-preserving swap dose-response over 66 cells: 3 base rates by 2 partitions by 11 doses, 400
replicates per cell, 2000 null draws. **The observed `+0.0476` is resolvable in 1 of 6 cells.** At
F1's base rate under `(family,k)` power is **0.807** and the MDE **0.0468**; at clause ②'s base rate
power is **0.564** and the MDE **0.0792**; at a balanced base rate power is **0.037** and the
permutation null alone sits at **+0.4048**. Under `(family,k,sham)` the power target is never reached
at any dose at F1's base rate.

So the F1-versus-② ordering is **withdrawn as unresolvable, not as wrong**: a comparison between a
value this design can see and one it cannot is not a comparison. **The zero is untouched and is
strengthened** — a gain of exactly 0.0000 requires no resolution to read, and the refutation of
R703's premise rests on it.

A derivation separates the two clauses without any of that. Since `gain <= 1 - base_rate`, F1's
ceiling is **0.0952** and clause ②'s is **0.2143**, so the same `+0.0476` is **50.0%** of one and
**22.2%** of the other. Equality in raw units across different ceilings is not equality.

Controls: calibration at dose 0 returned power **0.0625** against a 2-alpha bound of 0.10, so the
test is not anti-conservative; a maximal plant returned power 1.0000; the negative control — planting
on the true cells and measuring with shuffled ones — returned **0.0275**; the sham, planting on the
true cells and measuring with a single cell, returned a mean gain of exactly zero; monotonicity of
power in dose gave Spearman **+0.9909**; the noise floor, the standard deviation of the gain at dose
zero, is **0.0453**. Two of these were mis-specified on the first run in the same way — the label was
planted as a function of the very partition it was then measured with, so the negative control
destroyed nothing and returned power **0.9975** — and the correction is that the ingredient must be
removed from the measurement while the plant stays on the true structure.

## R709 · Whether clause F1's n=1 is the corpus or the definition that counted it

R685 reported that the judge-dependence of clause ③'s separation rests on a single verdict pair, and
`STATEMENT.md` carried that as "one verdict pair". R709 applies the standard's own remedy — count
what the release contains against what the code consumed.

Eleven rounds in this repository carry both judge keys; R685 examined seven. The four it skipped are
R683 through R686, the instrument rounds themselves, so that exclusion is a self-inclusion control
and not a search failure. R685 then reduced seven rounds to one pair by counting only booleans and
small closed-set strings, stating that continuous per-judge values differ by construction and are
excluded — while clause F1's scope claim is itself about a continuous quantity's sign across judges.

Measured under three nested rules: R685's own gives **1** pair, reproducing its count exactly; adding
the SIGN of continuous per-judge numerics gives **15** comparisons at **0.8000** agreement; adding
vector orderings gives 17 at 0.7647. Six of the widened comparisons bear on the separation — two
disagree and four agree — against the one R685 could use.

**All six are in R361.** Widening the rule added fields, not independent rounds, and correlated
measurements of a single comparison are not a second comparison. So the phrase understated the
corpus and is corrected to "one round"; the conclusion is unchanged. What does change is the
surrounding claim: the two judges are not broadly discordant, agreeing at eighty percent across the
widened set while disagreeing on this quantity, which makes the disagreement more specific rather
than less real.

The round's own first pass returned ten pairs under R685's rule rather than one. Nine of the ten were
control flags — positive, g=0, placebo and sham — which pass at both judges by design. R685 had
already found and excluded exactly that defect, and the audit reimplemented the walk from scratch
while reading R685's verdict string rather than its exclusion logic. Reported, it would have
retracted a correct result.

## R711 · Whether the core-versus-sham residual is above a same-size random admission

Clause F2 was kept, after its agreement with A2 was shown to be arithmetic, for the residual it was
said to genuinely own — the released core against its own sham. R711 tests that residual against the
only null that matters: a clause that admits the same number of arms with no regard to shams at all.

The ledger holds five sham pairs. Clause ② separates two of them, `coval_core` and `topw_k4`, and
zero of the other three, because it rejects both members of those. Separation is therefore only
possible where the base arm is admitted, which is two of the five pairs, so the residual is two of
two possible rather than two of five — a ceiling of two, and reaching a ceiling of two is precisely
what makes the exact probability large.

Enumerated over all **445,891,810** admissions of nine arms from forty-two, the separation count has
mean **1.7247** and the exact probability of reaching two or more is **0.5727**. The enumeration was
cross-checked against a sixty-thousand-draw sampled null agreeing to within **0.00154**, so the
figure carries no Monte-Carlo error. Swept over admission sizes the exact probability never clears
0.05: **0.2876** at k=5 and **0.7577** at k=14.

Controls: a plant admitting all five bases and rejecting all five shams yields five separations at an
exact probability of **0.002581**, so the instrument registers a maximal effect; an admission drawn
only from non-pair arms yields zero separations, so the statistic is not free; and three same-family
non-sham control pairs yield zero separations at an exact probability of 1.0000, so sham-ness is the
ingredient and removing it removes the signal.

So the justification is downgraded. This does not say the two separations are wrong — they are real
verdicts — it says they are not evidence for the clause, since a clause with no sham sensitivity
produces them fifty-seven percent of the time. Why they separate is untestable here: the prompt
having been withheld is an interpretation of a verdict, and no counterfactual over the generator
exists in this release. F2 stands on its exclusions and no longer on a justification.

## R712 · Whether a clause's unique-exclusion count is above a same-size random admission

After its A2 agreement was shown circular and its sham residual shown to be at chance, clause F2 was
left standing on one thing: the twenty arms it uniquely excludes, the largest count of the three
clauses. R712 gives that count the null it never had.

A clause's unique exclusions are the arms the other two clauses admit and it does not, so the ceiling
is the size of that intersection. For F2 the ceiling is twenty-three, making its count twenty of
twenty-three possible rather than twenty of forty-two. Under a uniformly random admission of nine
arms from forty-two the expected count is **18.0714**, and the exact probability of reaching twenty
or more is **0.1405**, enumerated hypergeometrically over all **445,891,810** admissions with no
Monte-Carlo error, cross-checked against a sixty-thousand-draw sample agreeing to within **0.00097**.

Running the identical machinery on all three clauses inverts the asymmetry the campaign has carried
since R703. F1 provenance excludes **4** against a ceiling of **7** at an exact probability of
**0.0003**; F2 behaviour excludes **20** of **23** at **0.1405**; F3 size excludes **2** of **5** at
**0.5956**. Under Benjamini-Hochberg at q equals 0.10 over the whole nine-cell sweep only F1 at its
observed admission size survives. So the clause with the fewest unique exclusions is the only one
whose count beats its own null, and the raw ranking that put F2 first was a statement about its
admission size.

Controls: a clause admitting nine arms entirely outside the ceiling set yields the full ceiling at an
exact probability of **0.000207**, so the instrument registers a maximal effect; a clause admitting
nine arms drawn only from the ceiling set yields fourteen, below the null mean, so the statistic can
move down as well as up.

This does not say F2 is wrong, nor that the arms it excludes are the wrong arms. It says the count is
not evidence, and whether the excluded arms are the right ones is construct validity requiring a
standard outside this repository. All three of F2's supports have now fallen — the A2 agreement to
circularity, the sham residual to chance, the exclusion count to admission arithmetic — and the
clause is retained while carrying no evidential support this site can supply.

## R713 · Whether clause F1's exclusions are stipulated or discovered

R712 left clause F1 as the only one whose unique-exclusion count beat its own null, at an exact
probability of three ten-thousandths. R713 asks what that number is measuring.

F1 excludes exactly four arms and nothing else in the forty-two-arm ledger: greedy_k4_fit1,
indep_k4_fit1, oracle_k4 and oracle_k4_fit1. The name predicate matching oracle or the fit1 suffix
returns exactly that set — four of four, no false positive, no false negative, a miss of **zero**
arms. The best predicate for clause F2 over the same families misses **five**, and clause F3's exact
match under a k-predicate is a derivation because F3 is that predicate.

So F1's probability measures that we built four label-reading arms and a clause that excludes
label-reading arms. A uniformly random admission is a meaningful null for a clause whose exclusions
are discovered and an empty one for a clause whose exclusions are stipulated, and the exact name
agreement is what distinguishes the two cases here. F1 is therefore the most constructed of the three
clauses rather than the most informative, and R712's reading is corrected accordingly.

This is not a defect in the clause. A clause stating that criteria were selected without reading
outcome labels should exclude exactly the arms built to read labels, and exact agreement is the
clause working. What is void is the probability, not the clause.

Controls: a predicate known wrong for F1 misses by thirteen arms, so the matcher does not match
everything; three thousand random four-arm subsets reproduce F1's exclusions zero times against an
exact chance of one in one hundred eleven thousand nine hundred thirty; and scrambling arm names
against verdicts at fixed multisets gives zero exact matches in three thousand draws, which excludes
the world in which any predicate can be made to fit four of forty-two strings.

Two defects in the round's own instruments were caught and fixed before it landed. Its first sweep
compared every predicate only against a clause's exclusion set, so F3's own k-predicate scored a miss
of forty-two and looked like the worst fit on the board when it is the exact complement and therefore
a perfect reproduction; the miss is now the minimum over both polarities. And its negative control
built a list from a set before shuffling, so the seed fixed the permutation but not the input order
and two runs returned one match and zero; sorting first makes the round byte-identical across runs
and across a changed hash seed.

The limit is the claim unit. Exact name agreement is evidence about construction and never proof of
it: that the arms were built to be excluded is a fact about this project's history rather than about
the ledger, and this round measures reproducibility while reasoning about what a null can price.

## R714 · How many cores the release ships, and whether the clauses share a unit

R713 closed by asking whether a definition can be attacked at all by a site that built the objects it
is defined over. Taking that question literally meant looking for objects this site did not build,
and there are 986 of them two directories away: `data/conversation_rubrics.jsonl` carries a
`coval_core` for each of 986 conversations, with criteria counts distributed two at one, three at
forty-three, and four at nine hundred forty-two.

So the deliverable's headline, that the release ships one core, is true at the arm level — one core
generator — and false at the object level, where the release ships **986** core instances. The page
never stated which it meant, while the impossibility register used one released core as a hard limit
round after round.

The larger finding is that the formulation mixes units. F1 and F2 are predicates over a generator: a
selection procedure, and a score across prompts. F3 is a predicate over an instance: the cardinality
of one criteria list. A three-clause definition whose clauses range over different objects cannot be
applied to any single object as written, and no round in this arc had said so — invisible while every
round tested the formulation against the forty-two arms, because an arm carries both a generator
identity and a criteria list, so the distinction never had to be made. The 986 instances force it:
they have a size and no provenance record, so they can satisfy F3 and cannot even be asked about F1.

Measured on the 986, **F3 is evaluable and admits 1.0000**, while **F1 and F2 are not evaluable** and
are reported as such rather than as passing. Controls: the card's own published statistic reproduces
from the file at a maximum of four and **0.9554** at exactly four; a nonexistent field yields zero
instances rather than a silent empty pass; F3 applied to the same file's `coval_full` field rejects
**0.9970**, so the clause reads size rather than the file; and F3 with its bound removed admits
everything in both fields, so the bound is what does the work.

F3 admitting all 986 is weak evidence for F3. Its ceiling was read off this release's card, so
admitting this release's instances is close to circular, and what the result establishes is that the
card's statement is true of the data — a verification of the object's own documentation rather than a
finding about cores.

## R715 · Whether any per-instance predicate separates, and whether it is clause F1

R714 established that the release ships 986 core instances and that only the size clause can be
evaluated on them, where it admits every one. R715 asks whether any per-instance predicate separates
at all.

The size clause's instance form is **degenerate** over the 986: one distinct value, admitting
everything. A provenance predicate is not. The share of a core's criteria appearing verbatim in its
own full rubric has mean **0.0655**, ranges from zero to one across seven distinct values, and
**794** of the 986 conversations have **zero** overlap, with exactly **one** core drawn wholly from
its rubric.

So the released cores are written fresh rather than selected from the full rubric. That is what the
retired clause about being drawn from a rubric asserted, and it had never been measured per instance.
The negative control puts the same overlap against a different conversation's rubric at **0.0000**,
so the figure is a property of the pairing rather than of criteria vocabulary in general, and the
sweep over three matchings — verbatim, casefolded, and a forty-character prefix — runs 0.0655, 0.0778
and 0.1777 on the own-conversation comparison while the shifted control stays at 0.0000, 0.0000 and
0.0003. Verbatim is the strictest matching, so a looser one can only raise the overlap, and the sweep
bounds the answer from both sides rather than reporting a single cell.

This predicate is **not** clause F1, and the preregistration said so before the run. F1 concerns
criteria selected without reading the outcome labels; the full rubric is not the labels, and the
labels do not appear in that file. Naming the predicate as a restatement of F1 would substitute a
label for a description. F1 therefore remains without an instance form, and of the three clauses one
has a degenerate instance form, one has none, and the separating predicate that does exist belongs to
neither.

Separating is not being right. Whether this predicate is the one a definition of core should use is
construct validity and is impossible at this site.

## R716 · What the provenance statistic can and cannot resolve

R715 found a per-instance predicate that separates: the share of a core's criteria appearing verbatim
in its own full rubric. R716 prices what that share can support, because a quantity that varies is not
thereby a quantity that resolves.

The share is quantised. With criteria counts of two, three or four, the ratio can take exactly seven
values — zero, a quarter, a third, a half, two thirds, three quarters and one — and that count is
forced before any data is read rather than observed. All seven do appear, which is the measurement.
The smallest non-zero value a single instance can take is **0.2500**, against a population mean of
**0.0655**: a ratio of **3.82**. So no single instance can express a value near the mean, which is
carried entirely by the minority that overlap at all.

The group mean, by contrast, is resolvable. Its bootstrap standard error over four thousand five
hundred resamples is **0.00469**, with a ninety-five percent interval of 0.0566 to 0.0749, and the
minimum detectable difference for an even split of the 986 is **0.040** — below the quantum. A
between-group difference smaller than one instance's smallest step is therefore detectable in
aggregate while a per-instance reading of the same statistic is not a fine measurement of anything.
That is the distinction R705 had to make for the gain statistic, and it is the second time in this
campaign that a statistic has been precise in the mean and coarse in the unit.

Controls: a planted shift of one tenth is detected at unity, with a no-shift floor of 0.07 and a
maximal-shift ceiling of 1.00, so the eighty-percent target lies strictly inside a real band; a shift
of exactly zero rejects at 0.07 against a two-alpha bound of 0.10; shuffling the group labels at
fixed sizes gives a ninety-five percent interval of minus 0.0171 to plus 0.0181, containing zero, so
no split of these instances shows a difference by itself; and the same question asked of the full
rubric against itself, which is identically one, returns a bootstrap standard error of exactly zero,
which is what the machinery should return when there is nothing to resolve.

No analysis choice can improve the quantum. It follows from the release's own bound of at most four
criteria per core, so only a release shipping larger cores could reduce it. The raw match count,
swept as the other side of that bound, has a minimum detectable difference five to seven times worse
and degrades as the split becomes uneven, while the share's does not.

## R717 · Why the k-split of the provenance share is biased, and what it can bound

R716 closed by proposing that the provenance share be compared between the cores carrying four
criteria and the forty-four carrying two or three. The share is the match count divided by the
criteria count, so that split conditions on the statistic's own denominator, and the groups do not
share a support: four criteria admit zero, a quarter, a half, three quarters and one, while two admit
only zero, a half and one.

The bias therefore has a sign that can be derived before any data is read. At the same match count of
one, the share is **0.2500** at four criteria and **0.5000** at two, so identical counts force a
higher share in the smaller group. The bias pushes the small group up.

Measured, the small group is **lower** on both statistics — **−0.0131** on the share and **−0.1052**
on the raw count — so the observed direction runs against the bias, which would make it informative
in principle, since a biased comparison landing opposite to its bias understates rather than
manufactures.

None of it is readable. The minimum detectable difference at the true forty-four against
nine-hundred-forty-two imbalance is **0.080**, exactly twice the even-split figure of 0.040, against
an observed absolute difference of **0.0131**. Zero of six specification cells survive their own
permutation null. So the caution R716 attached to its own proposal was correct: an even-split minimum
detectable difference does not carry over to a group of forty-four, and the question remains
unanswerable at this site.

The bias cannot be analysed away. Every share with the criteria count in its denominator inherits it,
and only the raw match count avoids it, at a resolution five to seven times worse.

## R719 · Whether the falsifier verdict against clause three survives its own population

R718 certified two blocks on the statement as standing unamended, one of them the finding that the
standard's falsifier does not fire against clause three. R719 asks what that finding was computed
over.

Its population is the five-arm literal that R689 retracted one round after it was written. The
finding reads that the three published arms outside the clause's extension all fail clause two
anyway, and those three — topabs_k4, topvar_k4 and topwvar_k4 — are three of the four arms R689
showed the release does not name. The release's card names **one** of the five, and at a population
of one the test cannot be run at all: it requires a set of published arms outside the extension, and
the corrected set contains none.

So the block is downgraded to **unevaluable** rather than refuted. The clause itself is not shown to
be decoration: over R360's forty-two arms it excludes thirty-seven, and four that clause two does
not. What falls is the evidence R688 offered for it.

The instrument R718 used could not have seen this. It computed amendment as a round cited in a
block's body outranking the highest round cited in its heading, and R688's block cites only R683 and
R688 — the retraction lives in a different block entirely. Measured across the statement, **two of
the three** blocks touching the retracted literal never cite the retracting round, and both are the
blocks R718 reported as standing. An amendment test scoped to a block cannot see a retraction filed
elsewhere, so the earlier count is an overcount.

The round's own positive control caught a defect of the same shape before any verdict was printed.
Its first version reconstructed the clause's extension from a sibling round's formula, which admits
the three arms R688 excludes; the recomputation returned an empty list against R688's committed
three, the control failed, and the round printed unverified. Reading the extension from R688's own
committed artifact fixed it. Auditing a round means using that round's object rather than a sibling's
algebra.

## R720 · Premise or contrast, and what the deliverable still asserts

R719 closed by proposing that a retraction anywhere on the statement reaches every block citing the
retracted literal. Applied literally that rule leaves a residue of zero, and it is too coarse.

The lineage block cites the retracted five-arm literal in order to distinguish its own object from
it. Its "number 5" is clause three's extension — coval_core, topw_k3, topw_k4, topw_k6, topw_k8 — and
the sentence containing the literal reads that five other five-member arm sets are committed in this
corpus and denote other objects. A block that cites a retracted literal to say it is not that does
not rest on it.

Measured across the twelve claim blocks, three cite a retracted literal: one as a premise, which is
R688's falsifier block already downgraded by R719; one as a contrast, the lineage block; and one as
the retraction itself. The role-aware residue is therefore **one** block, against **zero** under the
naive rule, so the naive rule over-kills by one.

The real defect in the surviving block is smaller and still real. It glosses the literal as CoVal's
publication list, the exact description R689 retracted, without citing R689. That is a defect in the
prose rather than in the claim, and it has been corrected on the statement to name the list as
retracted with the retracting round cited. Conflating a stale gloss with a compromised claim is the
over-kill this round exists to prevent, and it is the mirror of R719's finding: there a retraction
reached a claim nobody had connected to it, here a retraction reaches only a phrase.

Controls: the reading classifies R688 as premise and the lineage block as contrast, two roles that
can be stated independently of it; blocks citing no retracted literal return no role rather than a
default; the block recording the retraction reads as the retraction rather than as a victim of
itself; and removing the contrast markers flips the lineage block to premise, so the markers are the
ingredient.

The round's own first residue was wrong. It computed asserting-and-not-premise and returned three,
counting two blocks R718 had already found amended by later rounds, so the registered point would
have landed inside its interval for the wrong reason. A new criterion is a conjunct rather than a
substitute, and with the earlier amendment test restored the residue is one.

## R721 · Whether the six independent computations are six independent evidences

The one block on the statement that no later round has undermined asserts that the number five is
supported by one identified set with a named producer and by at most six independent computations.
R721 asks what independent means there, since the block does not say.

R680's six derive the set with no member literals in executable source and without reading a prior
round's results file. That is independence from copying. It is not independence of source, and R678
names the extension's unique producer as R294's census with R294 itself among the six, so six
programs computing the same predicate over the same data would agree by construction.

Measured, they do not share one source. The six read **eleven** distinct upstream files. The
registered prediction was two, so the round's directional failed by a factor of five, and that
failure is its most useful output: an attack that fails is evidence about the claim, and this is the
first block in this campaign to survive one.

The survival is qualified rather than clean. Three files are read by more than one deriver, the
clause ledger by four of the six, and all six read at least one shared file. They are eleven files
with three in common rather than six disjoint evidences, and the block's phrase at most is precisely
what makes it survivable. A negative control puts six randomly chosen rounds from the same arc at
fifteen, fifteen and fourteen distinct sources against these six's eleven, so the derivers are
slightly more convergent than the corpus and not dramatically so.

The block had also already made the naive attack against itself, calling its own number a ceiling
twice over and noting that absent literals remove one way of copying rather than all. A block that
names its own ceiling twice cannot be killed by pointing at the ceiling, and the only live attack
remaining was on the meaning of independent, which the measurement answered in the block's favour.

## R722 · Whether the shared file is a shared input

R721 measured that four of the six derivations behind the number five read the same file, the clause
ledger. R722 asks whether they read the same part of it, since two rounds taking disjoint fields from
one file share a path and no data.

All four readers parse, and they share four fields. The clause-two-and-three admission list is read
by three of the four; the clause-two admission list, the sweep and the criteria count by two each. So
the sharing is not nominal: two of the six derivations take the same field from the same file, which
is a shared input rather than a shared path, and R721's description of eleven files with three in
common as not-disjoint evidences was right and understated.

The probe run while writing the previous round's closing line was an uncontrolled search. It returned
fields for two readers and nothing for the other two, which is silence rather than zero, and
reporting those as reading no fields would have been a fabricated absence. This round replaces it
with a pattern ladder, reports coverage as a first-class number, and treats unmeasured as a value
distinct from zero that the two branches never print alike. With the ladder all four parse, so the
registered prediction that coverage would be incomplete failed, which is the right way for that
prediction to die.

The round's negative control also had to be repaired. It required the extractor to recover at least
three schema fields from the round that writes the ledger, and the ceiling is two: that round builds
its dictionary from variables, so only two of fifteen schema keys appear as string literals anywhere
in its source. The control could not pass and the round printed unverified. The repair computes the
band — floor zero, ceiling two, threshold one — rather than lowering the number, because recovering
any schema field from the writer is what the control exists to show. A threshold that is picked is a
guess; a threshold that is computed is a control.

## R723 · the ceiling on independent computations is one, not six

The count of independent computations behind the extension was measured again at the unit the claim
is about. Of the eight rounds that derive the set without carrying its members as literals, seven
read a prior round's artifact, and the round that certified the earlier bound found two of those
seven, a recall of 0.2857. The corrected ceiling on independent computations is therefore one, and
that one is the round that produced the set. The earlier instrument searched executable source for
the substring results-slash or a round directory followed by a slash. A path assembled from pathlib
operands places quotation marks and spaces between its segments, so neither substring occurs, and
the search was invariant under a rewrite that the property it stood for is not. The five rounds it
missed are exactly the five that build their paths from operands, and the two it found are exactly
the two that write the path inside a single string, so the partition is complete in both directions.
A strict specification requiring every cross-round reference to sit inside a path-shaped literal
returns the same seven, which is what makes the count reportable rather than an artifact of a loose
pattern. The bound remains a ceiling and not a count, because reading an artifact is measured here
and using its value is not.

## R724 · the producer could have returned otherwise, and the released core is not invariant

The single computation the deliverable rests on was tested for whether its answer was forced. Over
the decision-rule space of the producer's own procedure — five defensible readings of each measured
clause, the provenance clause on or off, and the k-capped arms kept or dropped, one hundred cells in
all — six distinct extensions are reachable and the released set of five is the answer in thirty of
them, which is the modal cell and the answer of fifteen of the twenty-five rule combinations with
the provenance clause on. So the producer is a measurement and not a derivation, and the arc's one
independent computation stands as one rather than collapsing to zero. Two further facts belong with
that number. Every reading that requires the whole interval of the second clause to sit above the
design's resolution excludes the released core itself and leaves a single arm, topw_k6, admitted
alone; the released core's second-clause interval runs from 0.008274 to 0.024117 against a minimum
detectable effect of 0.010616, so its point estimate clears resolution while its lower bound does
not. Membership of the core in its own extension therefore rests on reading the clause as effect
above resolution rather than interval above resolution, and that is a choice. Second, the axis
dropping k-capped arms changed nothing in any of the fifty rule combinations, so it is an axis that
could not have moved the answer and is reported as such. The count of six is a lower bound: the
bootstrap seed, the number of resamples, the multiplicity level and the annotator filter are fixed
inside the persisted artifact and would need the census re-run to vary.

## R725 · the rule space is one statistic with four thresholds, and the core's exclusion is not noise

The five readings of a measured clause swept in the previous round are not five criteria. The
minimum detectable effect is the effective z multiplied by the sample standard deviation over the
root of the sample size, and the interval is a percentile bootstrap of the same mean, so every
reading is a threshold on the ratio of the effect to its standard error. The point reading is that
ratio above zero, the interval reading above 1.959964, the resolution reading and the round's own
conjunction both above 2.801585, and the strict reading requiring the whole interval above
resolution is that ratio above 4.7615. Four thresholds carried by five labels, and the conjunction
is identical to the resolution reading whenever the effect is positive. That is algebra and not
evidence. What is evidence is that the equivalence holds on the artifact across four hundred and ten
checks with no disagreement, even though the bootstrap and analytic standard errors differ by up to
seven percent, which means no arm sits close enough to a threshold for that discrepancy to change a
verdict. The consequence for the previous round is that its hundred cells contain at most sixteen
distinct rule pairs of twenty five, so its coverage was narrower than its cell count suggested.
Separately, the exclusion of the released core under the strict reading was tested for whether the
minimum detectable effect's own sampling error could move it. The core's ratio is 4.2336 against a
threshold of 4.7615, a gap of more than eight sampling standard deviations of that quantity at a
sample size of nine hundred and sixty eight, and the crossing probability is zero at every seed. The
exclusion is a property of the arm. The crossing probability assumes the per-prompt differences are
normal, which this artifact cannot check; the distance in sampling standard deviations does not.

## R726 · the collapse is structural, and the check that established it was smaller than it looked

The previous round found no disagreement between the interval-based admission rules and the
threshold on the ratio of effect to standard error, and left open whether that zero was a property
of the rules or of where these particular arms happen to sit. It is a property of the rules. The
ratio of the two standard error estimates runs from 0.9478 to 1.0691 across eighty two cells, and
the interval of the statistic within which the two constructions can disagree is 0.237796 wide at
the interval reading and identically wide at the strict reading, the equality holding by algebra
because both boundaries move with the same coefficient. No cell falls inside either interval and
none would change verdict at the adverse end of the observed range. A dose response multiplying the
spread by nought, a half, one, two and four gives widths that are monotone and exactly zero at
nought, with the first occupancy appearing only when the spread is doubled, so the design's
resolution is stated as a factor rather than asserted as safety. Two qualifications belong with
this. The range used is a minimum and a maximum over eighty two draws, which are extreme order
statistics; the fifth to ninety fifth percentile range gives 0.172352, and the difference between
those two spreads is the floor. And of the four hundred and ten checks the previous round reported,
only one hundred and sixty four had a boundary that could move at all, because three of the five
readings never touch the interval estimate; the other two hundred and forty six could not have
disagreed however the data fell. The zero stands, over a failable population smaller than the one
it was quoted against.

## R727 · the disagreement zone is a resample count, and one skew test had no power

The spread that sets the previous round's disagreement zone was attributed. It is not a property of
the arms. A synthetic normal world at a sample size of nine hundred and sixty eight with twelve
hundred resamples, containing no skew and no arm-to-arm variation of any kind, reproduces a standard
deviation of the ratio of 0.027699 against the observed 0.027341, and an asymptotic derivation from
the sampling error of a bootstrap percentile independently gives 0.027821. Two routes, one answer.
Sweeping the resample count over three hundred, twelve hundred, four thousand eight hundred and
nineteen thousand two hundred gives a fitted log-log slope of 0.4951 in magnitude and negative in
sign, which is the half-power of Monte-Carlo error. So the zone narrows when the resample count
rises, and the previous round's statement that the spread would have to double describes a constant
chosen in the producing round rather than anything the data does. Two further findings belong here.
The correlation between the ratio and the interval's asymmetry is an underpowered detector of skew
at this resample count: planting real skew moves it by less than three standard deviations of its
own seed spread at twelve hundred resamples while moving it clearly at nineteen thousand two
hundred, so a null from it is silence. On the statistic whose power is established by the positive
control, the mean asymmetry, the observed cells give a value of minus 0.00410 with a standard error
of 0.00296, which is one point four standard errors from zero skew and nine point four from the
planted skewed world, so these cells carry no detectable skew by a powered test. And the sample size
cannot be tested at all: it takes two values across the arms with four of eighty two cells at the
minority level, which is an unidentified covariate and is recorded as unidentified rather than as a
null.

## R728 · the census reproduced from the object, and its population is a directory glob

The producing round's census was re-run from the saturation store rather than read from its summary,
which no round in this arc had done. Its committed verdicts are reproduced on all forty one arms
exactly. Raising the resample count sixty four fold, from twelve hundred to seventy six thousand
eight hundred, changes no admission and leaves the extension identical, and neither does changing the
bootstrap seed across five values at the shipped count, with the seed verified to move the draws.
The largest movement of any interval bound across the whole sweep is 0.001408. Most of that outcome
is forced: the minimum detectable effect does not depend on the resample count, only the lower bound
does, and the one cell within Monte-Carlo reach of its own boundary, at a ratio of 2.1458, is already
excluded by the count-invariant half. What is not forced is the reproduction itself, and that is what
this round establishes. Separately, and found by the failure of the round's own anchor rather than
registered in advance, the census defines its population by a glob over a results directory that
later rounds write into. That directory held forty one usable arms when the census was committed and
holds ninety two now, and re-running the same procedure over today's population admits sixteen rather
than five. The additional arms were built by later rounds for other purposes and their admissibility
is a separate question, so this is not a correction to the extension. It is a statement about the
procedure: the same code returns a different answer depending on when it is run, because its
population is not fixed by anything the definition says.

## R729 · the provenance clause is a blocklist and admits by default

The third clause requires the evaluation annotator to be held out from the core's own construction.
It is implemented as a set of four literal arm names. The selection program loads the human target
for exactly three of its rules, and any arm built by one of those rules is an object the clause was
written to exclude. Of the sixteen arms today's population admits, seven are built by such a rule and
the clause excludes none of them; across the whole population thirteen target-reading arms pass by
default. The clause excludes exactly and only its four literal names. Two independent routes agree on
every one of the eighty two arms both can classify, with no disagreement: one parses the tag the
builder emits from the rule, the size, the seed and the fit parity, and the other compares the
selected criteria per prompt and never sees a name. Both re-derive the four names the census already
knew, from construction rather than from the list, which is what makes the rest readable rather than
circular. Six arms carry no rule prefix because the selection program never emitted them; they are
reported as single-route and the one called target-reading by that single route is marked
uncorroborated and excluded from every count. None of this says those arms leak into the evaluation,
which is a question settled elsewhere and not re-opened. It says the clause never asks. The defect is
structural rather than clerical: an arm built after the census passes unless someone edits a literal,
so the clause's coverage decays with every round that adds an arm.

## R729 addendum · this finding belongs to R520, and what is new is that the defect is now realised

The blocklist finding recorded above was established earlier, by the round asking whether the
provenance set is complete. That round used the same line of the selection program, the same
positive control recovering the four declared names from tags alone, and the same negative control
over the label-blind rules, and it named six of the arms the literal misses. The present round did
not check for it before building and found the overlap only when a gate refused an unrelated
citation. Three things survive as additions. The earlier round recorded that every arm it flagged
carried no third-clause verdict at all, because those arms sat outside the scored population; on
today's population seven of them are admitted, so what was latent is now realised. The universe has
grown from fifty six arms to ninety two, which adds a seventh admitted target-reader and takes the
population-wide count that the clause admits to thirteen. And the classification is now corroborated
by a route that never reads a name, comparing the selected criteria per prompt, which agrees with the
tag route on all eighty two arms both can classify -- a corroboration worth having because the
earlier round's own record notes that a keyword search on this same question failed nineteen times
out of nineteen. The headline is the earlier round's.

## R730 · the seven admitted arms are four objects, and the clause already excludes one of them

The previous round's count of admitted target-reading arms was over tags. Resolved to objects by
exact per-prompt satisfaction-vector identity, the seven tags are four objects. One of those objects
carries a tag the provenance clause names, so the clause excludes it; what it fails to do is
recognise two further tags of the same object. The clause therefore admits three distinct
target-reading objects rather than seven, and the defect is real but smaller than both the round that
found it and the round that restated it claimed. Today's ninety three tags partition into eighty one
objects across eight multi-tag classes, and the partition is identical at every tolerance tried
because the smallest non-zero difference anywhere in the population is 4.762e-02, far above any
floating-point threshold, so exact equality is not a knife-edge choice. Computed from the same
partition though not registered in advance, the population-wide count of thirteen tags resolves to
ten objects of which the clause admits nine. The unit error is the third of its kind in three
consecutive rounds — a denominator the design could not return, a nine-way rule where the claim was
binary, and now tags where the claim is objects — and this one ran in the flattering direction,
inflating a defect attributed to someone else's definition.

## R731 · two of the three admitted objects carry the excluded object's size, and the third does not

The three target-reading objects the provenance clause admits were compared, at the object level with
each object counted once, against the object the clause excludes and against the four label-blind
arms, on both measured clauses. The greedy object's second-clause margin is 0.072210 and the
independent object's is 0.052679, against the excluded oracle object's 0.077867 and a label-blind
mean near 0.0169, with the released core at 0.016042. In units of the spread among the label-blind
objects, which is 0.003122 on the second clause, the greedy object sits 1.81 from the excluded object
and 17.71 from the blind group, and the independent object 8.07 against 11.45. Both sit with what the
clause excludes, on both clauses, and the two clauses agree on the nearest group for every object.
The third admitted object does not. It is built by the oracle rule and named for it, and its
second-clause margin is 0.014483, a ratio to its own minimum detectable effect of 1.04 against the
excluded oracle object's 7.29; it sits 0.78 spreads from the label-blind group and 20.30 from the
oracle. So construction and behaviour come apart, and a predicate over construction alone — which is
what the two preceding rounds proposed as the remedy — would exclude an object that behaves like the
ones the definition accepts. The mean distances to the two reference groups, 0.0314 and 0.0312, are
indistinguishable precisely because that third object drags the mean across, which is why the
per-object table in spread units is the reportable form and the two means are not. This compares
outcomes and not mechanisms: a margin near the excluded object's does not establish that the same
construction produced it, and establishing that would require an intervention this site cannot run.

## R732 · the third admitted object differs in two ways at once, so its cell carries nothing

The comparison that placed the third admitted object with the label-blind arms mixed two factors. That
object and the excluded oracle object select identical criteria on only 0.0888 of their 968 shared
prompts, against a floor of 1.0000 that every same-object tag pair in the partition returns, so the
selection genuinely differs; and their per-cell satisfaction agreement is 0.0354, with an earlier
round having established that the suffixed family is scored by an emitter foreign to the default one.
Their margin gap is therefore a sum of a selection effect and an emitter effect and neither term is
identified from the gap. No arm on disk carries the third object's criteria under a default-emitter
score, so the design that would separate them does not exist at this site. The reading drawn from
that cell — that construction and behaviour come apart — is withdrawn to unverified. It is not
refuted, and unverified is not an acquittal in either direction, so the proposal that the provenance
clause needs a predicate over construction returns to untested rather than being restored. Two things
are untouched. The greedy and independent objects both sit with the excluded object on both clauses
and both are scored by the default emitter, so that comparison mixes no instruments. And the rule
name is a poor proxy for construction, which is now measured directly at 8.9 percent selection
agreement between two arms that share a rule, rather than inferred from a margin.

## R733 · the two admitted objects move with the excluded one, prompt by prompt

The question left standing was whether the two admitted target-reading objects merely land at the
same level as the object the provenance clause excludes, or share its per-prompt structure. They
share it. Against a shared-subtrahend floor of 0.5034, computed in this round's own units from three
pairs of random-selection arms that have no shared mechanism, the greedy object's per-prompt margin
correlates with the excluded object's at an excess of 0.4632 and the independent object's at 0.3965,
against excesses of 0.1592 and 0.1966 toward the label-blind arms. The two measured clauses agree on
the ordering, and all forty eight cells of the grid survive a Benjamini-Hochberg correction over the
whole grid. The precondition was established elsewhere: the per-prompt gap is reliable, with a
split-half value of 0.8311 against a shuffled null of 0.0168, so this is not a correlation of noise.
Three limits attach. Correlation of outcomes excludes unrelatedness and cannot identify a shared
mechanism; that needs an intervention on the construction. The floor is essential and not decorative,
because every margin here subtracts the same baseline arm, so a large raw correlation is guaranteed
before any mechanism is shared. And the raw correlation of 0.9747 for the greedy object exceeds the
attenuation ceiling that the reliability estimate implies, which means that estimate does not
transfer to these arms or the shared subtrahend inflates past it; the disattenuated column is
therefore a diagnostic and not a correlation.

## R734 · the floor the previous round used was too high, so its excesses were understated

The floor against which the previous round measured profile similarity was built from pairs of
random-selection arms. Those arms share the subtrahend and they also share whatever structure their
common selection pool imposes. Isolating the subtrahend by re-pairing one arm's own contribution to
prompts at random, while leaving the subtrahend aligned, gives a floor of 0.3062 against the
random-arm value of 0.5034, a difference of 0.1972 which is more than ten times the seed spread of
0.0190. So the random arms do carry structure beyond the subtrahend, the floor used was too high, and
the excesses reported were understated rather than inflated. Re-scoring the previous round's
comparisons under both floors changes neither verdict: both admitted objects sit with the excluded
one either way, so the ordering never depended on the choice. Two limits. The difference names a
magnitude and not a cause; attributing it to the selection pool would require an intervention on that
pool. And the design the previous round proposed for this measurement would have measured nothing,
because re-pairing the margin destroys the subtrahend's alignment along with the arm's own signal and
collapses to a null that round had already run under another name — established by algebra before any
compute was spent.

## R735 · the floor depends on how many criteria the compared arms share

The floor used in the two preceding rounds was a single number built from three pairs of one size
family. Measured across one hundred and fifty three pairs of random-selection arms spanning six
selection sizes, the floor tracks the criteria the two arms actually share, at a correlation of
0.9264, rising from 0.4003 where arms select two criteria to 0.8438 where they select twelve. The
size-matched floor for the four-criterion arms the definition's comparisons involve is 0.6458. That
reverses the direction of the previous round's correction: measuring against a floor that strips all
overlap gave 0.3062 and suggested the excesses were understated, but the arms being compared all
select four criteria, and two unrelated four-criterion arms already reach 0.6458, so for the
comparison that matters the floor was too low and the excesses were overstated. Both admitted objects
still sit with the excluded one under every floor tried; the margins halve. Two limits. Overlap rises
with selection size by construction and each same-size stratum holds three pairs, so this design
cannot separate a floor that depends on overlap from one that depends on size, and the within-stratum
test is underpowered rather than negative. And the pool size used to predict overlap is the union of
observed selections, a lower bound, which biases the prediction upward and explains why measured
overlap is 0.9694 of predicted rather than equal to it.

## R735 addendum · the corrected excesses at the size-matched floor

Re-read against the size-matched floor of 0.6458 rather than the 0.5034 previously used, the greedy
object's excess toward the excluded object is 0.3289 and toward the label-blind arms 0.0989, and the
independent object's are 0.2781 and 0.1311. Both orderings are unchanged from every earlier floor and
both margins are roughly halved. These four values are the ones the statement carries and they are
recorded here so each resolves to this round rather than standing alone on the deliverable.

## R736 · the deferred experiment is a reanalysis, and the finding that led there was an indexing error

The previous round declared that separating overlap from selection size requires a new selection run.
It does not. Satisfaction scores are stored per prompt, criterion index and response letter, and
joining arms on prompt, response and criterion text shows the score to be a function of that triple
to 0.997357 across one hundred and ninety key-sharing pairs. A median of fifteen distinct criteria
carry a score on each prompt and nine hundred and seventeen of nine hundred and sixty eight prompts
carry at least eight, which is enough to assemble two four-criterion arms at any chosen overlap from
zero to four; the reachable prompt counts at those five targets are nine hundred and seventeen, nine
hundred and forty eight, nine hundred and sixty four, nine hundred and sixty five and nine hundred
and sixty eight. So the deferred experiment is available without asking the judge anything new. The
route to that conclusion began with an inverted index: reading the response letter as the criterion
position produced an apparent eighty five percent inconsistency, which would have said the judge's
score depends on which other criteria share the set. The scoring source builds one judge call per
criterion, so that world was impossible by construction. The control that should have caught it did
not, because it compared two tags of a single object and the inversion cancelled on both sides; the
control that does catch it runs both joins and requires them to disagree, which they do by 0.851120.
A residual inconsistency of 0.002643 survives the corrected join and is real, since an earlier round
measured the scoring floor at exactly zero on identical criteria; it is bounded here and not
explained.

## R737 · the floor is a curve in overlap, and the compared arms sit on it

Assembling four-criterion arms from scores already on disk at a chosen number of shared criteria, on
nine hundred and sixty eight prompts held fixed across every target, gives a floor of 0.4244 where the
arms share no criterion, rising through 0.5654, 0.7076 and 0.8517 to exactly one where they share all
four. The construction is validated by a one-parameter model: writing the raw correlation of two
subsets sharing j of k criteria as a shared per-response component plus the independent part, fitting
that component at zero shared criteria alone gives 0.3385 and predicts the four remaining targets to
within 0.0046. The simpler form registered in advance, the ratio of shared to total, assumes the
per-criterion satisfactions are independent, and they are not, because a good response satisfies many
criteria at once; that prediction was wrong and the construction was not. Applied to the definition's
own comparison, the greedy object shares 2.8492 criteria with the excluded object and the independent
object shares 2.1095, so their matched floors are 0.8299 and 0.7234. Four floors have now been used
for this one comparison and only these are matched on the quantity that drives it. Two limits. The
floors for the comparison against the label-blind arms were not computed here, so the excesses are not
re-scored in this round. And this is a floor for random subsets of the scored pool; the real arms were
produced by rules that may prefer criteria with particular satisfaction profiles, and whether a
rule-produced arm behaves like a random subset at the same overlap would need a new selection run.

## R738 · matched on every side, the admitted objects fall below the floor rather than above it

The comparison the previous rounds left half matched was completed. Each side is now read off a curve
built for its own pair of selection sizes rather than one curve for all, because three of the four
comparisons cross sizes; the four curves give shared-component values of 0.3026, 0.3361, 0.3826 and
0.4007 and each is validated by fitting that component at zero shared criteria alone and predicting
every remaining target, with a pooled worst deviation of 0.0100. Against those matched floors every
one of the ten excesses is negative. The greedy object correlates with the excluded object at 0.8123
against a matched floor of 0.8299, and with the label-blind arms at a mean 0.1151 below their floors;
the independent object is 0.0638 below against the excluded object and 0.1212 below against the blind
arms. So the ordering reported earlier survives, with gaps of 0.0975 and 0.0574 against a band of
0.0151, but it is now a comparison of two shortfalls rather than of two excesses. The earlier reading,
that these objects track the excluded object beyond what shared selection explains, does not survive a
floor matched on measured overlap: they track it less far below expectation than they track the blind
arms, which is a weaker statement and the one the evidence supports. Every floor here is built from
random subsets of the scored pool, and the arms being measured were produced by rules; whether a
rule-produced arm should meet a random-subset floor at equal overlap is not identified at this site
and is precisely what the negative excesses now make the open question.

## R739 · the rules do not select higher-variance criteria, so the shortfall is not a population artifact

The previous round's negative excesses had one obvious candidate explanation: the floor is built from
random subsets while the arms measured against it were produced by rules, and the selection source
derives that a criterion whose satisfaction is identical across the four responses contributes nothing
to any pairwise comparison, so a rule fitting the human target should avoid such criteria and a random
subset should take them at the pool rate. Measured against the full candidate set, that is false. The
mean percentile rank of a selected criterion's across-response variance, whose null is one half by
construction, is 0.5028 for the excluded object, 0.4677 and 0.5318 for the two admitted ones, and
between 0.4925 and 0.4982 for the label-blind arms, while uniformly random arms return 0.5005 with a
seed spread of 0.0029. The instrument is validated by a known-answer case from the same source: the
rule that selects by this variance ranks first at 0.8528. Matching the floor on variance as well as
overlap therefore moves none of the ten excesses to zero or above; the magnitudes shrink and every
sign holds. So the shortfall is a property of the arms rather than of the population the null was
drawn from, and one candidate explanation is eliminated rather than confirmed. Eliminating a confound
does not name a cause, and the shortfall is now unexplained rather than explained away.

## R740 · nine of the ten shortfalls, and both orderings, are inside their own resolution

Three rounds reasoned about ten negative excesses and one tried to explain them without anyone having
measured what the design can resolve. Bootstrapping prompts and recomputing the correlation, its
overlap-matched floor and the overlap itself together on every resample, only one of the ten has a
ninety five percent interval excluding zero, and that one is the independent object against the
eight-criterion label-blind arm at minus 0.0556 with an interval from minus 0.1009 to minus 0.0116.
Both ordering gaps cover zero: 0.0396 with an interval from minus 0.0102 to 0.0904, and 0.0511 from
minus 0.0022 to 0.0995. The signs are not stable either — the greedy object against the excluded one
is plus 0.0211 under joint resampling against a point estimate of minus 0.0176 two rounds earlier,
which is the same fact as the interval covering zero arriving as a change of sign. So the ordering
that survived every floor does not survive its own resolution, and the honest report for nine cells
is a bound rather than a shortfall. The naive combination of the three uncertainty sources in
quadrature gives 0.0213 while the joint bootstrap gives 0.0162 and resampling the correlation alone
gives 0.0181, so the correlation and its floor move together and treating them as independent
overstates the width. The intervals are conditional on this criterion pool; pricing the pool itself
would need a second release.

## R741 · the two rounds ran on two populations, and the disagreement was the pool

The round that measured ten excesses and the round that priced them ran on different prompt sets
against different candidate pools. The first built its pool from the union of every arm's observed
selections, which a later round showed is a sample of the candidate set biased by the rules under
study; the second used the full candidate set, against which fewer prompts supply the twelve criteria
the widest comparison needs, so its population is seven hundred and thirty four rather than nine
hundred and sixty eight. The mean absolute difference this makes across the ten cells is 0.0857,
several times the bootstrap standard errors, and it is the whole of the disagreement between them. On
the corrected population the pricing round's point estimates reproduce within their own standard
error in every one of the ten cells, so those numbers stand and the ten excesses computed on the
union pool are withdrawn. What was wrong was the comparison between them: the difference was read as
a change of sign under resampling when it is a change of population. On one correct population, one
of the ten excesses excludes zero and neither ordering gap does, so the ordering remains unresolved
and the honest report is a set of bounds. Correcting the pool drops two hundred and thirty four
prompts, and because the criterion threshold is applied against the true pool that drop is a selection
on pool size rather than a random subsample; the surviving population is therefore not the release,
and both pool-size distributions are recorded rather than exchangeability assumed.

## R741 addendum · the one surviving interval, as this round computes it

The single excess whose interval excludes zero is the independent object against the eight-criterion
label-blind arm, at minus 0.0556 with a ninety five percent interval from minus 0.1008 to minus
0.0116 on the corrected population. The pricing round reported minus 0.1009 for the same lower bound;
the two runs differ in their bootstrap draws and the third decimal is the estimator's own noise, not a
disagreement. The value recorded on the statement is this round's, and both are within the
Monte-Carlo error each round reports.

## R742 · maximal power resolves nothing new, and two of the three quantities were never restricted

The previous round applied the widest comparison's criterion requirement, twelve, to every cell,
leaving seven hundred and thirty four prompts throughout. Each cell needs only four plus its own
reference size: seven, eight, eight, ten and twelve, which against the true candidate set give nine
hundred and fifty, nine hundred and nineteen, nine hundred and nineteen, eight hundred and fifty nine
and seven hundred and thirty four prompts. Recomputed at that maximal power the cell the arc turns on
rises from seven hundred and thirty four prompts to nine hundred and nineteen and its standard error
falls from 0.0162 to 0.0138, and its interval still spans zero. One of the ten excesses excludes zero,
the same one as before, and no cell resolves that did not. So the global threshold was not the binding
constraint and the bounds stand as reported. Separately, the scope worry that closed the previous
round applied to one of the three quantities rather than all three: the provenance clause is a name
lookup that consults no prompt, and the extension comes from a census computed on each arm's own
population, so neither is a function of the restricted set. The admission count is three and the
extension has five members, both without any prompt restriction. The per-cell figures are not
comparable across cells because each rests on a different prompt set, which is why the global column
is recorded beside them and why the ordering gap is left on the global population, where an average
across cells is defined.

## R743 · what the claim table's population constant actually rests on

**Question.** The four-row constants table declares one population — *"R294's 41 arms · 968 prompts ·
the 56-tag / 46-object census"* — for all ten claim rows. Do the rounds those rows cite establish that
population, and is the number a scope or a timestamp?

**Estimand, named before the method.** Among the rounds cited inside the ten claim rows, the fraction
whose `run.py` obtains its arm population by a live glob rather than by explicit enumeration.

**Identification.** From SOURCE, by `ast`. **Not** from artifact fields: across **465** artifacts a
population size is recorded under **19** distinct key spellings, the commonest (`n_arms`) covering
**35**. An instrument reading one key measures spelling. The gauge test killed that estimand before
any code existed *(ledger 991)*.

**Instrument.** The classifier is **reused** from `assurance/arm_population_is_derived.py`, whose
`ARM_NAMES` come from the arm store on disk rather than from a naming convention. Three detectors
sweep the one free choice — what counts as a population-bearing glob:

| detector | rule |
|---|---|
| `loose` | any `glob`/`iglob`/`iterdir`/`listdir`/`discover` call anywhere — **the existing gate's rule** |
| `medium` | a glob whose pattern literal contains `sat_` or `.npz` |
| `tight` | a glob whose pattern literal starts with `sat_` — the arm store's own pattern |

**The grid — 3 detectors × 2 populations, all six cells reported.** `f = DERIVED / (DERIVED + TYPED +
DECLARED)`, denominator fixed in the preregistration before any code.

| detector | population | DERIVED | TYPED | DECL | NO_ARMS | NONE | n with a population | f |
|---|---|---|---|---|---|---|---|---|
| loose | cited | 2 | 4 | 0 | 6 | 4 | 6 | 0.3333 |
| loose | complement | 49 | 38 | 1 | 262 | 53 | 88 | 0.5568 |
| **medium** | **cited** | **1** | **4** | **0** | **6** | **5** | **5** | **0.2000** |
| medium | complement | 26 | 41 | 1 | 262 | 73 | 68 | 0.3824 |
| tight | cited | 1 | 4 | 0 | 6 | 5 | 5 | 0.2000 |
| tight | complement | 25 | 41 | 1 | 262 | 74 | 67 | 0.3731 |

**The SHAM is the complement population — the ingredient ABSENT, not inverted.** The ingredient is
*being cited by a claim row*. Globbing is **more** common outside the cited set (0.3824) than inside
it (0.2000) at the same detector, so "the cited rounds glob" is not a property of the tree that the
citation inherits — it is a property the citation *lacks*.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 distinct rounds cited | 17 [12, 24] | **18** | ✓ |
| P2 glob fraction, medium | 0.60 [0.30, 0.90] | **0.2000** | ⛔ **outside the band, low side** |
| P3 cited derived globs returning ≠ 41 today | ≥ 1 | **1 of 1** | ✓ |
| P4 detector agreement per round | ≥ 0.70 | **15/16 = 0.9375** | ✓ |
| D directional: derived rounds spread across eras | true | **false** — there is exactly one | ⛔ |

**Controls — 5 PASS, 0 FAIL, both after repair.**

| control | returned |
|---|---|
| **POSITIVE** | `R728 → DERIVED`, `R477 → TYPED`. Band **computed**: floor 0 DERIVED, ceiling 16 parseable cited rounds, threshold 2 — `0 < 2 ≤ 16` |
| **g=0** | a source with no arm code → `NO_ARMS` — unknown, never a silent class |
| **NEGATIVE** | every glob call deleted from R728's source, everything else kept → `DERIVED → TYPED`. Excludes *"the classifier fires on any file"* |
| **PLACEBO** | 410 `README.md` → **0 DERIVED**, reported as **0 of 410** and not 0 of 0; 21 of them mention an arm artifact in prose, so the detector was pointed at a real population |
| **UNIT** | 0 cited rounds map to >1 `run.py`; the 2 mapping to **zero** are named (`R580`, `R581`) and excluded from every denominator by construction |

**⛔ Both repaired controls had failed for their own reasons** *(ledger 993)* — the positive control's
second case expected `R719 → TYPED` when R719 loads no arm artifact at all, and the unit control
demanded exactly one source file per round when codeless rounds are a known category here.

**⛔ The confound is UNCONTROLLED, and the script now says so** *(ledger 994)*. Written before the run:
class might be a function of ERA rather than of the claim. With `|DERIVED| = 1` and `|TYPED| = 4`,
separability of the two round-number sets is **forced** — a single point is separable from every set —
so the computed `true` was algebra, not evidence. It prints `UNINFORMATIVE`.

**Verdict.** `WORLD A` on the registered threshold (`f ≤ 0.25`): the constant is a scope for the rows.
**But the shape none of the three worlds named is the finding**: the constant's *source* is derived and
expired (`sat_*.npz` → **101** today vs the stated **41**) while its *inheritors* are stable, and **11
of 16** cited rounds with code name no arm population in their own source — **6** naming no arm
artifact and **5** naming one without a classifiable population.

> ⛔ **CORRECTED BY R744** *(ledger 995, 996)*. This paragraph first read *"establish no arm population
> at all"*, and the block above reported the 6 as a count. Following named cache edges, **5 of the 6
> reach the arm store**; only `R558` does not. **The 6 is an upper bound on a FILE-level property, and
> the sentence asserted a ROUND-level one.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 12345, **both writes confirmed to disk
before the comparison ran**. No rng in the design.

## R744 · is `NO_ARMS` a measurement or silence? — the bound on R743's central count

**Question.** R743 reported 6 cited rounds as `NO_ARMS` — loading no arm artifact — from a **regex over
each round's own file**. Its positive control validated the `DERIVED`/`TYPED` split *among rounds that
already pass that gate*, and never asked whether the gate can MISS.

**Estimand.** Among those 6, how many reach the arm store through a static path the flat regex cannot
see (a local import, or a cache written by a store-reading round).

**Identification — PARTIAL, so the answer is a BOUND.** Transitive closure only ADDS reach, so it
lower-bounds the reachers and upper-bounds `NO_ARMS`. Non-reachability is not establishable statically.
R650 already measured the general resolution question undecidable (**172 of 364** read sites resolve);
this round asks only the binary a bound can answer.

**The grid — 4 levels × 3 populations.**

| level | NO_ARMS(6) | all cited(16) | complement(404) |
|---|---|---|---|
| **L0** own file *(= R743's detector)* | **0/6** | 10/16 | 142/404 |
| **L1** + locally imported modules | **0/6** | 10/16 | 145/404 |
| **L2 tight** + caches naming their round dir | **5/6** | 15/16 | 165/404 |
| ⛔ L2 loose *(uncontrolled, for contrast)* | 6/6 | 16/16 | 259/404 |

⛔ **`L0 ≤ L1 ≤ L2` is FORCED** — each level is a superset. **A derivation.** Only the gain is measured.

**Per round.** `R519, R520, R529, R530, R534` gain at L2-tight; **`R558` does not.**

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 reach at L1 | 2, band [0, 5] | **0** | in band, point wrong |
| P2 reach at L2 tight | 3, band [0, 6] | **5** | in band, point wrong |
| P3 L0 reproduces R743 | 16/16 (hard) | **16/16** | ✓ |
| P4 cited rounds with an import edge | ≥ 5 | **8** | ✓ |
| **D** gainers carry an import edge | true | **false** | ⛔ mechanism refuted |

⭐ **The directional failing is the finding.** Imports contribute **0** to the gain in every cell; the
tree shares data through **artifacts**, not through code.

**Controls — 6 PASS, 0 FAIL.**

| control | returned |
|---|---|
| **POSITIVE** | R294's `sat_` literals moved into an imported constant → flat goes **blind**, L1 still reaches; refactor **asserted to parse**; band computed `True → True` |
| **g=0** | a store-free helper adds **no** reach — the detector counts data, not edges |
| **NEGATIVE** | import graph emptied → L2 equals L0 on **16/16** exactly |
| **SHAM** | ingredient **absent**: L1 gain on the 8 import-free cited rounds = **0** |
| **PLACEBO** | L0 recomputed differs by exactly **0** |
| **P3** | L0 is R743's instrument, not a lookalike |

⛔ **Both of this round's own instruments were broken first** — a positive control whose refactor did
not parse *(ledger 997)*, and an L2 cache detector matching by basename across **155** round
directories, which would have printed **6/6** *(ledger 998)*.

**What it retracts.** R743's *"11 of 16 never load an arm artifact"* → **6 name none + 5 name one
without a classifiable population** *(995)*; the 6 → **an upper bound**, ≥5 of 6 reach the store
*(996)*; `NO_ARMS` as a round property → **a file property**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 99, **both writes confirmed to disk**
before the comparison ran (3384 and 3385 bytes, differing only in the recorded seed).

## R745 · are the added arms candidate cores, or our own apparatus?

**Question.** R728 measured the census admitting **16** on today's 92-arm store against **5** on the
committed 41, and called it a scope condition. Its residue, verbatim: *"whether R294's construction is
the right one is not addressed here."* Are the added arms candidate cores at all?

**Estimand.** The class composition of the 51 arms present today and absent from the committed 41, and
separately of the 11 newly admitted, under a partition **read off the builder**.

**Identification — from `corebench/select_core.py`, asserted at runtime.**

| line | establishes |
|---|---|
| `:50-52` | the rule vocabulary is a closed set of **nine** |
| `:102` | `if a.rule in ("oracle_k", "indep_k", "greedy_k"):` **loads the human target** |
| `:204` | the tag is **emitted by the builder** from rule + k + seed + fit-parity + `tag_suffix` |

⇒ **TARGET-READING** `oracle_k · indep_k · greedy_k` · **RANDOM** `random_k` · **CEILING** `full` ·
**SELECTOR** `topw_k · topabs_k · topvar_k · topwvar_k`. The round **exits 2** if the source does not
carry all three assertions.

⚠ **Gauge bound.** A name is invariant under renaming while the property is not, so name
classification is blind **in general**; it is admissible here **only** because `:204` emits the tag
from the rule. Non-parsing tags return **`UNPARSED`**, never a class.

**The grid — 3 classifiers × 3 populations.**

| classifier | population | SEL | TGT | RND | CEIL | UNPARSED | non-SEL share |
|---|---|---|---|---|---|---|---|
| loose / **tight** / family | added(51) | 14 | 13 | 20 | 0 | 4 | **0.7021** |
| loose / **tight** / family | newly admitted(11) | 2 | 7 | 0 | 0 | 2 | **0.7778** |
| loose / **tight** / family | committed extension(5) | 4 | 0 | 0 | 0 | 1 | **0.0000** |

⚠ **The curve is FLAT and that is a fact about the tags, not robustness** — every tag here is
builder-emitted with a clean rule prefix, so the three classifiers **could not have differed**
*(ledger 1002)*.

**The 11, named.** `oracle_k4_08bR`, `oracle_k4_oracle_kA/kB`, `greedy_k4_greedy_kA/kB`,
`indep_k4_indep_kA/kB` → **TARGET-READING** (7). `topw_k4_detA/detB` → **SELECTOR** (2).
`coval_core_2bA/2bB` → **UNPARSED** (2).

⚠ **`UNVERIFIED`:** whether the four suffixed tags are **replicas** of `coval_core` and `topw_k4` —
which would leave the 11 containing **no new object at all** — is not readable from a name, because
`tag_suffix` is caller-supplied rather than rule-emitted. It needs **R525's satisfaction-vector
partition on today's 92**.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 share of the 51 parsing | ≥ 0.70 | **0.9216** | ✓ |
| P2 non-SELECTOR share of the 51 | 0.55 [0.20, 0.90] | **0.7021** | ✓ in band |
| P3 non-SELECTOR of the 11 | 9 [0, 11] | **7** | in band, point wrong *(1001)* |
| **D** the 11 exceed the 51 | true | **true**, 0.7778 vs 0.7021 | ✓ |

⚠ **P3 was PARTIALLY SIGHTED**, declared in the preregistration: 6 of the 11 names were visible in a
truncated print before registration. ⛔ **The 11 are a SUBSET of the 51** — a within-population
contrast, **no significance claimed**, and labelled a derivation.

**Controls — 6 PASS, 0 FAIL.**

| control | returned |
|---|---|
| **PROVENANCE** | all three source assertions hold; otherwise exit 2 |
| **POSITIVE** | `random_k8_s0 → RANDOM`, `topw_k4 → SELECTOR`, **different classes**; band computed — at a floor classifier assigning one class they **cannot** separate |
| **g=0** | out-of-grammar tags → `UNPARSED`; a silent `SELECTOR` default would have **manufactured World A** |
| **NEGATIVE** | rule→class shuffled → `{TGT 29, SEL 14, CEIL 2, RND 2}` vs real `{RND 20, SEL 14, TGT 13}` |
| **SHAM** | ingredient **absent**: the committed extension, **0/4** non-SELECTOR |
| **PLACEBO** | 10 non-tag strings → 0 in every class, stated as **0 of 10** |

⚠ **SHAM shortfall stated:** R728 records the committed **count** (41), not the committed **names**, so
the sham ran on the **5** it does record.

**Verdict — `WORLD B`.** The census's new admissions are dominated by apparatus. **World A is killed:
the wider population is not a wider sample of cores**, and `16` beside `5` would present our own
instruments as rival subject matter *(ledger 1000)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 7777, **both writes confirmed to
disk** before the comparison ran (5734 / 5737 bytes, differing only in the recorded seed).

## R746 · the census admitted arms measured on two different populations

**Question.** R745 left four tags unresolved and proposed exact satisfaction-vector identity to settle
them. ⛔ **The objects refused half of it before any code:** `sat_coval_core.npz` holds 15,312 cells
over 968 prompts; `sat_coval_core_2bA/2bB.npz` hold 3,168 over **200**. Identity across different cell
sets is **undefined**, not false *(ledger 1004)*.

**E1 estimand.** The prompt-coverage distribution of today's 92-arm population, split by the 16
admitted, the 51 added, and the whole 92. **Identified exactly** — `select_core.py:200` emits meta as
`f"{pid}|{j}|{x}"`, so the prompt set is field 0 of a builder-emitted structured string.

**E2 estimand.** Whether the four unresolved tags coincide with an extension member, **on shared
cells**. **Partially identified → a BOUND**: `identical ⇒ indistinguishable THERE`; `not identical ⇒
different objects`.

**E2 result — all four are replicas.**

| pair | identical | shared / larger |
|---|---|---|
| `topw_k4_detA` / `detB` vs `topw_k4` | ✓ | 15,488 / 15,488 = **1.000** |
| `coval_core_2bA` vs `coval_core_2bB` | ✓ | 3,168 / 3,168 = **1.000** |
| `coval_core_2bA` vs `coval_core` | ✓ | 3,168 / 15,312 = **0.207** |

⇒ **the 11 extra admissions contain no new SELECTOR object** — 7 target-reading *(R745)* + 4
duplicates. ⚠ Whether the 7 target-reading **tags** are 7 **objects** is `UNVERIFIED`; R730's
precedent (7 → 4) says expect fewer.

**E1 result — the coverage grid, 3 definitions × 3 populations.**

| definition | population | min | median | max | distinct | below max |
|---|---|---|---|---|---|---|
| **prompts** | **admitted(16)** | **200** | 968 | 968 | **2** | **2** |
| prompts | added(51) | 4 | 968 | 968 | 3 | 3 |
| prompts | all(92) | **4** | 968 | 968 | **4** | 5 |
| cells | admitted / added / all | 3,168 / 256 / 256 | 15,488 | 30,680 / 43,812 / 59,936 | 6 / 9 / 13 | 15 / 47 / 90 |
| pairs | admitted / added / all | 792 / 64 / 64 | 3,872 | 7,670 / 10,953 / 14,984 | 6 / 9 / 13 | 15 / 47 / 90 |

⭐ **The committed extension is uniform — all five at 968.** The heterogeneity arrived with the drift.

**⛔ The arithmetic, derived before measuring, points AWAY from a defect.** `mde = ZEFF·std/√n`, so
968 → 200 multiplies the bar by **2.2000**. Realised, the low-coverage admissions cleared a mean
`mde1` of **0.026962** against **0.013275** for the rest — **2.03× wider**. They were admitted
**despite** a harder threshold.

⛔ **The first verdict string said the opposite and the same run refuted it three lines above**
*(ledger 1006)*: it branched on the share comparison alone while the realised-threshold comparison sat
computed and unused. **Over-representation ≠ advantage.** The branch now references it and the
mechanism is reported as **unexplained**.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| B1 distinct coverage values over the 92 | 3 [1, 10] | **4** | in band, point wrong |
| B2 added arms below 968 | 8 [0, 51] | **3** | in band, point wrong *(1007)* |
| B3 committed extension all at 968 | yes | **yes** | ✓ |
| B4 admitted arms below 968 | 2 [2, 16] | **2** | ✓ |
| B5 the five identity tests | all yes | **all yes** | ✓ |
| **D** coverage does not predict admission | true | **false** — 0.1250 vs 0.0395 | ⛔ |

⚠ **World A was dead before registration and the preregistration declares it** — the 200-prompt
coverage was visible while inspecting the objects. Second declared sighting in two rounds.

**Controls — 6 PASS, 0 FAIL.** POSITIVE separates two arms whose **file sizes** differ 4.52×, a signal
the parser never reads, against a floor parser that cannot separate them · g=0 an empty-meta arm →
`UNREADABLE`, never `0`, since **a silent zero would have manufactured World B** · NEGATIVE field-1
parsing moves coverage on 20/20 · SHAM the ingredient **absent**, the 76 non-admitted arms (3/76) ·
PLACEBO 0 on all 92 · UNIT every tag → exactly one `.npz`, asserted.

**Verdict — `WORLD B`.** The census admits across two populations. Low-coverage arms are
over-represented among the admitted, **but cleared a wider bar**, so it is not an admission advantage
and the mechanism is unexplained.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 424242, **both writes confirmed to
disk** (11,963 / 11,968 bytes, differing only in the recorded seed).

## R747 · 81 objects is *not* a transitive-closure artifact — the attack failed

**Question.** R730's object partition merges tags that are equal **on the prompts they share**, with a
guard `len(shared) ≥ 0.5·min(|A|,|B|)`, and builds classes by **union-find**. Equality on a shared
subset is **not transitive**, and union-find takes the closure regardless. Since **81** is the
denominator R730, R745, R746 and this page all rest on, it is worth attacking.

**Estimand.** E1 how many of R730's multi-tag classes are **not cliques** under its own `same()`.
E2 the object count under the **clique** partition. **Exact and finite** — 93 tags, 4,278 pairs, R730's
own cached vectors, imported rather than re-implemented.

**Result — the attack failed.**

| | registered | measured | |
|---|---|---|---|
| P1 non-clique multi-tag classes | 1, band [0, 8] | **0** | in band, point wrong |
| P2 clique-partition object count | 83, band [81, 93] | **81** | at the floor, point wrong |
| P3 reproduce R730's 81 with its own code | yes *(hard)* | **81 = 81** | ✓ |
| **P4** pairs rejected **only** by the guard | **≥ 1** | **0** | ⛔ **FAILED** *(ledger 1010)* |

**8 multi-tag classes, 4 of size ≥ 3, 0 not cliques.**

**Specification curve — flat, and the flatness is arithmetic, not robustness.**

| guard | 0.00 | 0.25 | **0.50** | 0.75 | 1.00 |
|---|---|---|---|---|---|
| objects | 81 | 81 | **81** | 81 | 81 |
| non-clique | 0 | 0 | **0** | 0 | 0 |

⛔ The guard is `len(shared) ≥ g·min(|A|,|B|)`. For a **strict subset** pair `len(shared) = min`, so
the test is `min ≥ g·min` — **true for every g ≤ 1**. The guard can only reject a **partial** overlap,
and this population has none. That is why `P4 = 0`, and it means the sweep could not have failed.

⛔ `E2 ≥ union-find count` is **FORCED** — the clique partition refines the closure. Only the **size**
of the increase is a measurement, and it is **0**.

**⭐ But the subset rule IS load-bearing, and the SHAM locates it.** Ingredient **absent** — require
**identical** prompt sets — gives **83 objects**, still 0 non-cliques. So the count carries **one
unstated parameter worth 2 objects**: `81` under shared-subset merging, `83` under full overlap. The
two extra are the `coval_core`/`_2b*` case R746 measured at 200 of 968 prompts. **R730's own residue
already calls this a modelling choice, and this round does not adjudicate it.**

**Controls — 6 PASS, 0 FAIL.** POSITIVE is a **synthetic** non-transitive triple built by construction
(A≈B, B≈C, A≢C): union-find merges to 1 class and the clique test flags it, against a never-flagging
floor of 0 — **that is what makes the zero on real data admissible rather than silent** · g=0 a
synthetic clique triple → 0 flagged, since flagging every multi-tag class would have manufactured
World B · NEGATIVE `same()` forced False → 93 singletons, 0 violations · SHAM as above · PLACEBO 73
singletons → 0, stated as 0 of 73 · P3 the instrument is R730's, not a lookalike.

**Verdict — `WORLD A`.** Union-find added nothing the relation did not already give. **81 is well
defined and every downstream count is clear of a chaining artifact.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 31337, **both writes confirmed to
disk** (1,357 / 1,361 bytes, differing only in the recorded seed).

## R748 · the page's two object counts differ in three factors, and both move under the rule

**Question.** R747 priced one unstated parameter and closed by proposing it be priced at the claim
level. Running P4 on that question — on **every** question the round asks, which is R747's own lesson
— found something larger: the deliverable's two object counts were computed by **different relations
on different quantities over different populations**.

| round | relation | quantity |
|---|---|---|
| **R524** | `len(ma)==len(mb) and (ma==mb).all() and array_equal(sa,sb)` | **full overlap**, raw satisfaction cells |
| **R730** | equal on **shared** prompts, guard `≥ 0.5·min` | **subset**, per-prompt aggregated agreement vectors |

They disagree on a class both computed: R524 has `['coval_core_2bA','coval_core_2bB']`; R730 has
`['coval_core','coval_core_2bA','coval_core_2bB']`.

**⛔ The first implementation was wrong and its own control caught it** *(ledger 1011)*. v1 applied both
rules to raw cells and `P4` returned **70** against R730's committed **81**. R730's relation never
touches raw cells. The two published rules differ in **two ways at once** — R732's failure in this same
arc — so the grid became **2 quantities × 2 rules × 2 populations**.

**The grid — 8 cells.**

| quantity | population | full overlap | subset | gap |
|---|---|---|---|---|
| **raw cells** | **56 (R524)** | **46** ← *the page's number* | **39** | 7 |
| raw cells | 93 (R730) | 83 | 70 | 13 |
| agg vectors | 56 (R524) | 45 | 44 | 1 |
| **agg vectors** | **93 (R730)** | **83** | **81** ← *the page's number* | 2 |

⛔ `subset ≤ full` is **FORCED** — full overlap refines subset. Only the **gap** is measured.
⭐ **Aggregation absorbs most of what the overlap rule would separate** — gaps 7→1 on the 56 and
13→2 on the 93.

**E2 — both stated counts move under the rule alone.** *"56 tags are 46 objects"* → 46 full / **39**
subset. *"93 tags are 81 objects"* → **83** full / 81 subset. *"13 tags are 10 objects"* → population
not reconstructible, **OUT OF SCOPE**, not assumed unaffected.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 56 under subset | 45 [40, 46] | **39** raw / **44** agg | ⚠ **under-specified as written** — it presupposed one quantity *(1012)* |
| P2 93 under full overlap | 83 | **83** on both quantities | ✓ |
| P3 / P4 reproduce 46 and 81 | yes *(hard)* | **46 = 46**, **81 = 81** | ✓ |
| P5 stated counts that move | 1 [0, 10] | **2** | in band, point wrong |
| P6 disagreeing classes | 2 [0, 20] | **2** | ✓ exact |
| **D** all disagreements carry a strict subset | true | **false — 1 of 2** | ⛔ *(1013)* |

⭐ **D failing is the informative part**: the second disagreeing class is a **partial overlap** with no
containment, so there are **two** mechanisms and a fix aimed at subsetting alone would leave half in
place.

⛔ **D2, a DERIVATION asserted and excluded from the findings** *(1014)*: the extension's 5 members sit
in 5 classes under both rules — forced, because a refinement cannot merge what is already separate.

**Controls — 7 PASS, 0 FAIL.** POSITIVE a synthetic **strict-subset** pair: subset merges, full overlap
does not — **opposite sides**, band computed against merge-nothing/merge-everything · g=0 a synthetic
**unequal** pair, both refuse, since a subset rule merging unequal arms would have manufactured P1 ·
NEGATIVE distinct seeded noise ×3 seeds → **(93, 93)** every time · **SHAM** the ingredient **absent**,
the 88 arms sharing one prompt set → **79 = 79**, so the rules are identical where overlap is constant
and the gaps are attributable to overlap structure · PLACEBO 0 of 93 · P3/P4 both instruments are the
ones they claim to be.

**Verdict — `WORLD B`.** Both stated counts move; **every object count must carry its cell**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 98765, **both writes confirmed to
disk** (1,905 / 1,909 bytes, differing only in the recorded seed).

## R749 · which cell did each object-count claim come from?

**Question.** R748 established an 8-cell identity grid and that the page's two headline counts sit in
different cells. Which cell does *each* object-count claim descend from?

**⛔ First, a defect in R748's own instrument** *(ledger 1015)*. It enumerated claims with one pattern
matching **3** sentences; a medium pattern matches **5**. Its `P5` was a share of an under-counted
population — §4's *a search is an instrument*, one round after quoting it.

| pattern | sentences | live | in a retracted block |
|---|---|---|---|
| tight *(R748's)* | 3 | 3 | 0 |
| **medium** | **5** | 5 | 0 |
| loose | 50 | 50 | 0 |

⛔ `loose ≥ medium ≥ tight` is **FORCED**. The order is algebra; only the gaps measure.

**The five, resolved.**

| count | cites | cell | how |
|---|---|---|---|
| **46** | R524 | `raw cells × full overlap` | defined in its own source |
| **81** | R730 | `agg vectors × subset` | defined in its own source |
| **2** | R520, R523, R525 | **UNRESOLVED** | R520 holds no identity relation |
| **4** | — | **UNRESOLVED** | the sentence cites nothing |
| **10** | — | **UNRESOLVED** | the sentence cites nothing |

**E3 = 2 distinct cells among the resolved → `WORLD B`:** the rows are not comparable and each must
carry its cell.

**Registered against measured.**

| | registered | measured | |
|---|---|---|---|
| P1 assertions per pattern | ⚠ **SIGHTED**, declared before registering | 3 / 5 / 50 | — |
| P2/E3 distinct cells | 2 [1, 4] | **2** | ✓ exact |
| P3 assertions resolving | 3 [0, 5] | **2** | in band, point wrong |
| **P4** resolved rounds importing their relation | 2 [0, 10] | **0** | in band, point wrong |
| P5 citing a round with no `run.py` | 0 [0, 5] | **0** | ✓ |
| **D** the unresolved are the importers | true | **false** | ⛔ *(1017)* |

⭐ **D failing is the finding.** Import-following was built because R747 and R748 both import
`same()` — a real limitation, correctly anticipated, that **never bit**. The three failures are
**missing citations**, which no instrument improvement can repair.

⚠ **The resolver takes the FIRST citation and that choice has a measured cost**: the NEGATIVE control
rotates it and **2 of 5** cells change. So *"row 8 is untraceable"* is a statement about the resolver,
not about the row.

**Controls — 5 PASS, 0 FAIL.** POSITIVE resolves R524 and R730 to their known cells, **correct and
distinct**, against a constant-cell floor that cannot separate them · g=0 an uncited assertion →
`UNRESOLVED`, since **a default cell would have manufactured World A** · NEGATIVE rotation moves 2/5 ·
SHAM ingredient **absent**: 36 of the first 40 rounds hold no locatable relation and every one returns
`UNRESOLVED` · PLACEBO 0 of 5.

⛔ **A CENSUS HAS NO CONFIDENCE INTERVAL.** n = 5 is every object count on the page: no sampling
uncertainty, and **no power to generalise**. None is reported.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 55555, **both writes confirmed to
disk** (2,756 / 2,760 bytes, differing only in the recorded seed).

## R750 · when a sentence cites several rounds, how many of them hold the number?

**Severity check first, and it changed the round.** R749's NEXT asked about multi-cited **object-count**
sentences — there is exactly **1**. **A round with n = 1 is not a measurement.** One level up the page
holds **1,389** sentences, **65** citing ≥2 rounds, **17** of those carrying a number, with group sizes
2, 3, 4, 5, 8. That is measurable; the narrower version was not.

**Estimand.** For each such sentence, the **support depth**: how many cited rounds' own artifacts
contain the stated number.

**⚠ R590's repair reused.** Its prefix matcher required the printed value to be a prefix of a stored
float, so rounded-up values failed — 13 orphans of which **9 were its own bug**. R590 has no `run.py`,
so the relation is re-implemented with the repair carried forward and the prefix rule kept only to
price it.

| matcher | population | n | median | share ≥2 | share = 0 |
|---|---|---|---|---|---|
| prefix *(broken)* | multi-cited | 17 | 1.0 | 0.4118 | **0.2353** |
| **rounded** *(repair)* | **multi-cited** | **17** | **1.0** | **0.4118** | **0.1176** |
| **rounded** | **single-cited (SHAM)** | **37** | **1.0** | — | **0.2162** |
| tolerance | multi-cited | 17 | 1.0 | 0.4706 | 0.1176 |

⛔ `support ≤ group size` **ALWAYS**. ⛔ The **SHAM's `share ≥2` is structurally 0** — a single-citation
sentence cannot have support 2; its informative column is `share = 0`.
⭐ **The broken rule manufactures 2 extra orphans on this page** (4 vs 2) — R590's bug, re-measured.

**Registered against measured.** P1 median 1 **[0,3] → 1** ✓ · P2 share≥2 0.35 → **0.4118** ✓ ·
P3 SHAM 0.79 → **0.7838** ⚠ **prior-art informed from R590's 15/19, declared, not scored as a blind
hit** *(ledger 1021)* · P4 zero-support 2 → **2 of 17** ✓ · P5 manufactured orphans ≥1 → **2** ✓ ·
D no growth with size → **true on usable sizes** ✓.

⚠ **The directional excludes sizes with n < 3.** Sizes 4 and 8 hold **one sentence each** at mean 4.00;
a mean over n=1 is not a trend *(ledger 1020)*. They stay in the table with their counts visible.

**⛔ The NEGATIVE control could not have fired** *(ledger 1019)*. v1 rotated the group **within** a
sentence — but `support` **sums over every member**, so rotation permutes a set being summed and the
count is invariant **by construction**. ⭐ **The identical operation was a valid control one round
earlier**, because R749's resolver reads exactly one citation and order is load-bearing there.
**A control is a property of its design and cannot be carried across.** Repaired by giving each
sentence **another sentence's** group: **10 of 17** change.

**Controls — 4 PASS, 0 FAIL.** POSITIVE `0.0316`, found by **direct search** in both R294 and R426 —
not by the matcher — scores **2** against a never-matching floor of 0 · g=0 a number in no artifact →
**0, reported not skipped**, since a skipped zero would raise the median by deleting the worst cases ·
NEGATIVE as above · PLACEBO 0 of 17 · SHAM the ingredient **absent** · UNIT **7 of 17** sentences state
more than one number, so support is per **number** and the sentence value is the **maximum**.

**⚠ The confound, written before the run, does not rescue the result.** Against the rounds' READMEs
rather than their artifacts: **median 1.0, share ≥2 = 0.4118** — identical. Reported beside, never
merged.

**Verdict — `WORLD B`.** A citation group is not joint grounding. **Where a figure matters, the page
must name which citation computed it.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 13579, **both writes confirmed to
disk** (7,990 / 7,994 bytes, differing only in the recorded seed).

## R751 · `UNVERIFIED` — the annotation detector inverted its own SHAM

**Question.** How much of what a defect-flag counts is **already repaired** on the page? R750 reported
2 zero-support figures as residue; one of them is the row this page already annotates as ungrounded
*(ledger 1022)*.

**⛔ P4 first, and it stopped the fourth rebuild in this arc.** R750's proposed corpus-wide value search
**is R591**, which scanned 355 rounds for R590's four orphans and returned four different verdicts,
including `0.0200` **CONFIRMED UNGROUNDED**.

**The grid — 3 matchers × 3 windows, SHAM arm beside every cell.**

| matcher | window | flagged | annot | share | **SHAM (supported)** |
|---|---|---|---|---|---|
| **rounded** | **tight** | **33** | **6** | **0.1818** | **0.4600** |
| rounded | medium | 33 | 8 | 0.2424 | 0.4667 |
| **rounded** | **loose** | **33** | **10** | **0.3030** | **0.5133** |
| prefix | tight / loose | 71 | 23 / 27 | 0.3239 / 0.3803 | 0.4643 / 0.5357 |

⛔ `annotated ≤ flagged` and `loose ≥ tight` are **both FORCED** — order is algebra, only gaps measure.

**⛔ The SHAM did not match, it INVERTED.** Supported figures carry annotation keywords **more** often
than flagged ones, at every window and matcher. **Annotation does not track groundedness**, so the
question is unanswerable with this detector and the verdict is `UNVERIFIED`.

**Where the failure lives — the confound run on BOTH arms:**

| keyword | flagged | supported | |
|---|---|---|---|
| **`ungrounded`** | **0.0606** | 0.0400 | flagged 1.5× |
| **`corrected`** | **0.0606** | 0.0200 | flagged 3.0× |
| `retracted` | 0.1515 | **0.2867** | supported |
| `unverified` | 0.1818 | **0.4400** | supported |

**A keyword detector cannot separate *"this number is ungrounded"* from *"this claim's scope is
unverified"*.** ⚠ **The restricted detector is NOT reported as a result** — selecting it after seeing
which subset favours the hypothesis is choosing the specification from the outcome *(ledger 1024)*.

**Registered against measured.** P1 10 [3,40] → **33** in band, point wrong · P2/P3 ⛔ **registered with
bands `[0.00, 1.00]`, which no share can fall outside — a check that cannot fail, in the
preregistration of a round about instruments that cannot fail** *(ledger 1023)* · P4 the known case
found loose and **missed tight** ✓ *(hard)* · P5 2 [0,10] → **10**, at the ceiling · D ✓.

**Controls — 4 PASS, 1 FAIL.** POSITIVE `0.0200` missed tight, found loose, against a never-annotating
floor — **a detector finding it at every window would not be measuring the window** · g=0 **23** flagged
figures carry no keyword anywhere · NEGATIVE detached windows drop the share 0.3030 → 0.2424 · PLACEBO
0 of 33 · **SHAM FAIL, inverted** · UNIT **17 of 33** flagged figures share a line.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 24680, **both writes confirmed to
disk** (3,356 / 3,360 bytes, differing only in the recorded seed).

## R752 · the MDE refuses the comparison, and the formula computing it was too generous

**Question.** R751 demanded the restricted detector be preregistered **and its MDE computed before the
run**. Done in the preregistration: at **n = 33 vs 150**, MDE ∈ **[0.1174, 0.1924]** against gaps of
**0.0206** and **0.0406**. **The comparison was dead before any code ran.**

**⛔ Then the formula failed its own control.** Planting a difference of exactly the analytic MDE and
running the exact test it approximates rejects **0.6237**, not 0.80 — 3 seeds, spread **0.0101**. The
confound was written before the run: `0.05 × 33` is **under 2 expected events**.

⭐ **The preregistration pre-authorised the repair**, so it was applied rather than improvised:

| | analytic | **empirical (searched)** |
|---|---|---|
| MDE | 0.1174 | **0.1604** — 1.37× larger |
| ratio to the gap | 2.89× | **3.95×** |
| required n per arm | 453 | **846** vs **33** available |

⚠ **The positive control is the monotone LADDER, not the search's own answer** — asserting the searched
MDE rejects at 0.80 would be circular. `0 → m/2 → m → 2m` gives **0.0395 → 0.4460 → 0.7999 → 0.9954**.

**The grid — 0 of 24 cells detect the gap.** Even the most permissive (p̄ 0.05, α 0.10, power 0.80,
one-sided) is **0.0838**, twice the gap.

**Controls — 5 PASS, 0 FAIL.** g=0 rejects at **0.0395 ≈ α** · NEGATIVE at 10× n moves the MDE
0.1174 → **0.0371**, ratio **3.16** against √10 = 3.16, and the gap then rejects at **0.7823** —
**the sample is the problem, not the estimator** · SHAM with the imbalance removed (both arms at the
harmonic mean 54.1) leaves the MDE **unchanged**, so the imbalance is not the binding constraint ·
PLACEBO exactly 0.

**E2 — the census, n = 4, no rate computed.**

| line | value | cites | keyword | scope language too? |
|---|---|---|---|---|
| 551 | `0.0022`, `0.0995` | R741 | `corrected` | **yes** — ambiguous |
| 620 | `+0.0582`, `0.0200` | R514, R515 | `ungrounded` | **no** — clean |

⇒ **2 of 4 are unambiguous groundedness declarations**; the other 2 sit under a `CORRECTED` marker that
also carries scope language. **The same confusion that inverted R751's pooled detector, visible at the
level of the individual figure** *(ledger 1027)*. ⛔ A census of 4 has **no interval and no power to
generalise**.

**Registered against measured.** P1 0.80 [0.70, 0.90] → **0.6237** ⛔ **FAILED, and it is the formula
that failed, not the design** *(1025)* · P2 0.05 → **0.0395** ✓ · P3 800 → **453 analytic / 846
empirical**, ⚠ **the registration named neither and neither is scored as a hit** *(1026)* · P4 4 → **4**
✓ · P5 2 → **2** ✓ · D ✓.

**Verdict — `WORLD B`.** The design is blind; the comparison is **REFUSED**; the census is the round's
only claim about the page.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 86420, **both writes confirmed to
disk** (4,259 / 4,263 bytes, differing only in the recorded seed).

## R753 · the three deliverables are not one population, and the ungated one is 4.5× worse

**Question.** R752 left a requirement of **846 figures per arm** and asked how many pages reach it.
⛔ **That is division.** The count settles itself; the question worth asking is whether pooling is
legitimate — §1's G1, *asking for power on an unidentified quantity is how a well-powered-looking
round gets built*.

| document | figures | lines | flagged | **rate** | median cited era |
|---|---|---|---|---|---|
| `STATEMENT.md` | 184 | 68 | 33 | **0.1793** | R607 |
| `DEFINITION.md` | 118 | 67 | 45 | **0.3814** | R439 |
| **`FORMULATION.md`** | 125 | 57 | **100** | **0.8000** | R256 |
| **pooled** | **427** | | 178 | 0.4169 | — |

**427 / 846 = 0.50 of one arm**; **12** documents of average size would be needed.

**Pairwise, with the MDE computed before interpretation.**

| pair | diff | MDE (figures) | MDE (lines) | verdict |
|---|---|---|---|---|
| STATEMENT vs DEFINITION | 0.2020 | 0.1629 | 0.2378 | **DIFFERENT** |
| **STATEMENT vs FORMULATION** | **0.6207** | 0.1601 | 0.2481 | **DIFFERENT** |
| DEFINITION vs FORMULATION | 0.4186 | 0.1773 | 0.2489 | **DIFFERENT** |

⭐ **The SHAM makes it readable.** Ingredient **absent** = being a different document: two halves of
`STATEMENT.md`, exchangeable **by construction**, differ by **0.0933**. The largest between-document
difference is **6.7×** that.

⚠ **The confound is live and unresolved** *(ledger 1029)*. The ungated document is also the **oldest**
— governance and era are the same column here. The directional fires (`FORMULATION.md` at **4.5×**
this page's rate) but **"being ungated caused it" is not established**, and the era is printed beside
each rate.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the monotone ladder `0.0529 → 0.2955 → 0.8026 → 0.9999` ·
g=0 rejects at **0.0532 ≈ α** · NEGATIVE document labels shuffled collapses the spread **0.6207 →
0.0482** · SHAM as above · PLACEBO exactly 0.

⭐ **The formula was honest here** — analytic **0.1601**, empirical **0.1620**, ratio **1.01×**, against
**1.37×** in R752. **The difference is expected count**: under 2 events there, ~52 here. *The
approximation's failure is predictable from the counts* *(ledger 1030)*.

**Registered against measured.** P1 0.18 → **0.1793** ✓ · **P2 0.30 → 0.8000 ⛔ at the ceiling** ·
**P3 0.12 → 0.6207 ⛔ outside the band** · P4 0.125 → **0.1601** ✓ · P5 0.75 → **0.7955** ✓ · D ✓.
**I under-predicted the disagreement between my own pages by 5×** *(ledger 1028)*.

**Verdict — `WORLD C`.** The documents are **not exchangeable**; pooling would manufacture power
without validity, which is worse than the shortfall. **And the shortfall stands regardless.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 97531, **both writes confirmed to
disk** (2,287 / 2,291 bytes, differing only in the recorded seed).

## R754 · era does not explain it where it can be measured, and where the effect lives it cannot be

**Question.** R753 found the ungated `FORMULATION.md` at a **0.8000** flagged rate and flagged that
governance and era are confounded. Separate them by comparing eras *within* a document.

**⛔ The identification check ran first and killed the main contrast.**

| document | `<300` | `300-450` | `450-600` | `600+` | total |
|---|---|---|---|---|---|
| `STATEMENT.md` | 4 | 6 | 86 | 88 | 184 |
| `DEFINITION.md` | 5 | 43 | 55 | 19 | 122 |
| **`FORMULATION.md`** | **110** | **15** | **0** | **0** | 125 |

**2 of 3 pairs have an empty joint bin ⇒ UNIDENTIFIABLE.** Only `STATEMENT`–`DEFINITION` is 4/4.
⛔ **An empty joint bin cannot be stratified — definitional.** This is an **identification** failure,
not a power failure *(ledger 1031)*, and more data does not repair it.

**E2 — within `DEFINITION.md`, governance constant, era varying.**

| | n_old | n_new | rate_old | rate_new | diff |
|---|---|---|---|---|---|
| **`DEFINITION.md`** | 48 | 74 | **0.3958** | **0.4054** | **−0.0096** |
| `STATEMENT.md` | 10 | 174 | 0.5000 | 0.1609 | +0.3391 ⚠ **n_old = 10, far below its MDE — uninformative** |
| `FORMULATION.md` | 125 | **0** | 0.8000 | **UNDEFINED** | ⛔ undefined is **not** zero |

**The difference sits at the 14.5th percentile** of a 5,000-shuffle permutation null (sd **0.0915**,
95% band **[−0.1813, +0.1622]**). ⭐ And five **arbitrary** split points give `|diff|` up to **0.0763**
— **the era split is less different than an arbitrary one.**

**⛔ My first negative control presupposed a non-null effect** *(ledger 1032)*. It asked whether one
shuffle beat the real difference; with a real difference of −0.0096 that is **§4 row ② verbatim** —
*"a coin flip when the real effect is null, which is exactly when you are running it."* Repaired to the
shuffle **distribution**.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the monotone ladder `0.0504 → 0.2833 → 0.7991 → 1.0000` ·
g=0 at **0.0497 ≈ α** · NEGATIVE as above · SHAM the arbitrary splits · PLACEBO exactly 0.
⭐ The formula was honest again: analytic **0.2545**, empirical **0.2565**, **1.01×**.

**Registered against measured.** **P1 +0.30 ⚠ prior-art-informed from R607's 13× era effect → −0.0096**
— in band, point badly wrong, and **the prior did not transfer from rounds to a document's figures**
*(ledger 1033)* · P2 15 → **4** ✓ · P3 0.25 → **0.2545** ✓ · P4 0.78 → **0.7939** ✓ · P5 2 → **2** ✓ ·
**D false** — DEFINITION's old-era rate is closer to STATEMENT's than to FORMULATION's.

**Verdict — `WORLD B`.** Era does not explain it where it can be measured, so **the governance reading
survives its strongest confound** — the most it can do, since the decisive contrast is unidentifiable.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 11223, **both writes confirmed to
disk** (2,830 / 2,834 bytes, differing only in the recorded seed).

## R755 · era, governance and maintenance are one variable here, and it is n = 1

**Question.** R754 proposed measuring MAINTENANCE from git to separate *ungated* from *abandoned*.

**⛔ The design died twice before running.** ① A correlation over **three** documents is not a
measurement — three points always admit a line. ② `git blame`: every line of all three deliverables
was last touched inside a **two-day** window (`distinct days = 2` each). **No maintenance gradient
exists in wall-clock time.**

**⛔⛔ The ontology error, running back through R753 and R754** *(ledger 1034)*:

| document | commits | last touched | new citations | **max R ever cited** |
|---|---|---|---|---|
| **`FORMULATION.md`** | **99** | **2026-08-04T02:11** | 105 | **R360** |
| `STATEMENT.md` | 131 | 2026-08-05T18:51 | 202 | R754 |

**It is not abandoned** — 99 commits, stopped **41 hours** ago. **Round ids 164–755 are a LOGICAL
clock**, and *old-era*, *ungated* and *unmaintained* are **one variable**: position in a three-day
burst. ⚠ **One document stopped ⇒ the treatment is n = 1**, collinear with document identity; 417
commits do not repair a document-level contrast *(ledger 1036)*. **This line is CLOSED.**

**What IS identified — within `FORMULATION.md`, governance constant.**

| | value |
|---|---|
| new citations per commit, mean | **1.0606** |
| slope, raw / per added line | **−0.0090** / −0.001052 — **same sign**, not a commit-size artifact |
| shuffled-order slopes ×5 | mean −0.0021, sd **0.0046** |
| first 10 / last 10 commits | **23** / **11** |
| terminal zero-adding run | **1** |

**Neither a reliable slope (−0.0090 against a −2σ threshold of −0.0092, missing by 0.0002) nor a
cutoff ⇒ `UNRESOLVED`, and the series is published rather than a slope.**

**⭐ The informative residue is a registered point whose SIGN I got wrong** *(ledger 1035)*. I
registered `STATEMENT.md`'s slope at **+0.05**; it is **−0.0074** — **the same decline as the stopped
document**. A declining citation rate is not a property of abandonment; it is what happens when a
document consumes uncited rounds faster than the pool refills.

**Controls — 5 PASS, 0 FAIL.** POSITIVE the live stream adds **23** citations in its last 20 commits,
band `0 < 23 ≤ 202` · g=0 **31 of 99** zero-adding commits are **in the series, not skipped** ·
NEGATIVE shuffled order → mean −0.0021 · **SHAM** the ingredient **absent** — added `⛔` markers slope
**+0.0032** against the citation slope **−0.0090**, so the trend is about **citing**, not commit style ·
PLACEBO exactly 0.

⛔ **A derivation I failed to label in the preregistration:** *new distinct citations per commit* is
partly self-exhausting. For `FORMULATION.md`, whose pool froze at R360, it is close to forced. **The
parity with `STATEMENT.md`, whose pool kept growing, is what makes the comparison informative.**

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 44556, **both writes confirmed to
disk** (2,158 / 2,162 bytes, differing only in the recorded seed).

## R756 · the flagged rate belongs to ROUNDS — and R753's headline was mostly artifact ABSENCE

**⛔⛔ RETRACTION.** R753 reported `FORMULATION.md` at **0.8000** against `STATEMENT.md`'s **0.1793**
and read it as governance. **93 of FORMULATION's 125 figures — 74.4% — cite ONLY rounds with no
`results/` directory**, against **4.0%** (DEFINITION) and **0.0%** (STATEMENT). The matcher scored
*"no artifact"* identically to *"artifact does not hold this value"* *(ledger 1038)*.

**⭐ And the direction REVERSES once absence is separated:** among rounds that DO have artifacts,
FORMULATION's average **0.2188**, STATEMENT's **0.4455** *(ledger 1039)*.

**Two cheap checks did the work.** ① Artifact availability by era is **uniform** (1.00/1.00/0.98/1.00),
killing the era-level version of the rival. ② At the exact-round level the documents are
**near-disjoint** — 43 / 61 / 97 rounds cited by figures, **`F ∩ S = 0`**, DEFINITION matching
FORMULATION on **5 of 125**. **A matched comparison is structurally unavailable, not under-powered.**

**The identified estimand — the ROUND as the unit.** 1,186 (figure, round) **pairs** from 416 figures.
⭐ **The g=0 control caught the retraction:** **27** cited rounds have no artifact and return
**UNDEFINED**, excluded **with their count printed** — never `0.0` (perfect support) nor `1.0` (total
failure). **R753 had no such control.**

| | all rounds | ≥3 figures |
|---|---|---|
| n | 138 | 76 |
| between-round variance | 0.1396 | **0.0905** |
| sampling null (5 seeds) | 0.1165 | **0.0394** |
| ratio | 1.20× | **2.30×** |

⛔ A round cited by ONE figure is 0 or 1 **by construction**; the columns are never merged.

**⚠ The SHAM bounds it.** Line-blocked at the same sizes: **0.0852** vs observed **0.0905** — only
**1.06×**. Random reassignment destroys all structure; line-blocking preserves **positional**
clustering. **Much of the clustering is positional**, and that is reported rather than resolved
favourably *(ledger 1040)*.

**Controls — 5 PASS, 0 FAIL.** POSITIVE **R392**, chosen by **artifact size** (116,141 B) *before* its
rate was seen — **not selected on the outcome** — scores **0.2000** vs pooled **0.6233** · g=0 as above ·
NEGATIVE 0.0905 → 0.0394 · SHAM as above · PLACEBO exactly 0. **CONFOUND printed:**
`corr(artifact size, rate) = −0.1382`.

**Registered against measured.** P1 150 → **138** ✓ · P2 0.09 → **0.0905** ✓ near-exact · P3 0.03 →
**0.0394** ✓ · **P4 ⚠ its band spanned [0,1] and could not fail — reported, not scored, and labelled**
(R751 made that mistake silently) · P5 20 → **36** ✓ · **D predicted true, measured FALSE and
INVERTED**.

⛔ **The document-level implication is ALGEBRA**: with near-disjoint round sets a document's rate is a
weighted average of its rounds', so *"documents differ"* **follows**. Only the variance was measured.

**Verdict — `WORLD A`.** The rate belongs to **rounds**; R753's document headline is a shadow of
**which rounds each document cites**.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 66778, **both writes confirmed to
disk** (1,866 / 1,870 bytes, differing only in the recorded seed).

## R757 · the artifact corpus was scoped to ONE arc of ten

**Question.** R756 contradicted itself — its era table said 17 of 17 early rounds have artifacts, its
g=0 said 27 cited rounds have none. **Both cannot be true.**

**⛔ The object settles it.** `E05_the_space_of_compilers/` holds **ten arcs, A16–A25**; **A24 begins
at R276**. The "artifact-less" rounds live in **A17 and A23**. Every round from **R748 to R756**
resolved `A24.glob(f"R{rid:03d}_*")` — **98 of 577 artifacts across 72 round directories were
invisible** *(ledger 1041)*. **§4's *a search is an instrument*, at repository scale.**

| document | A24 corpus | repo-wide | drop | flagged |
|---|---|---|---|---|
| `STATEMENT.md` | 0.1784 | 0.1784 | **0.0000** | 33 → 33 |
| `DEFINITION.md` | 0.3984 | 0.3984 | **0.0000** | 51 → 51 |
| **`FORMULATION.md`** | **0.8000** | **0.3680** | **0.4320** | **100 → 46** |

⭐ **Both arms use the same document text**, so this contrast is internally valid. ⛔ The repo corpus
**contains** the A24 one, so the rate can only fall — *"it fell"* is algebra.

**⛔ My first SHAM was more generous than the treatment** *(ledger 1042)*: it appended the whole blob
to **every** figure and dropped **0.4880**, which would have read as pure haystack. The real correction
gives each figure **its own** out-of-arc round. **Per-figure matched:** sham **0.0800** vs real
**0.4320** — **ratio 0.185**, so the correction is **5.4×** the haystack.

**⛔ The NEGATIVE control FAILED, and it is the more important finding** *(ledger 1043)*. Restricted to
A24, today's rates do not reproduce R753's: `DEFINITION.md` **0.3814 → 0.3984**, `STATEMENT.md`
**0.1793 → 0.1784**, `FORMULATION.md` **0.8000 → 0.8000** exactly. **The two that moved are the two I
append to every round; the one that matches is the one nobody edits.** The deliverable is a **moving
population**. ⇒ **the corpus defect is established, its size against published numbers is not, and the
verdict is `UNVERIFIED`.**

**Controls — 4 PASS, 1 FAIL.** POSITIVE `0.6602` found **verbatim by direct search** in
`A16/R220/tournament.json` — flagged under A24, supported repo-wide; **the FLIP is unreachable from
either degenerate end** · g=0 a fabricated value stays flagged under **both** · SHAM as above ·
PLACEBO exactly 0. **CONFOUND printed:** newly-resolved matches span **six arcs**
(`A23:25 · A19:16 · A20:7 · A16:4 · A17:4 · A18:1`), so it is not one arc's format.

**Registered — all five landed** (P1 **0.3680** · P2 **0.1784** · P3 **26** · P4 **0.2201** ·
P5 **0.0800**, D true). **And the round is still `UNVERIFIED`: prediction accuracy is not a verdict**
*(ledger 1044)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 13131, **both writes confirmed to
disk** (1,979 / 1,983 bytes, differing only in the recorded seed).

## R758 · git pins the population — both of them — and the correct pin is the PARENT commit

**Question.** R757 failed its NEGATIVE control and left `UNVERIFIED`, diagnosing *"the deliverables
grow every round"*. **Git holds every version, so the population can be pinned retrospectively.**

**⭐ Result.** Pinned to R753's **parent** tree, all three rates reproduce **EXACTLY**:
`0.1793 / 0.3814 / 0.8000`, including `DEFINITION.md`'s **118** figures and **45** flagged.

| document | PARENT | commit | today | vs R753 |
|---|---|---|---|---|
| `STATEMENT.md` | **0.1793** | 0.1793 | 0.1784 | **EXACT at parent** |
| **`DEFINITION.md`** | **0.3814** | **0.4016** | 0.4000 | **EXACT at parent, +0.0202 at its own commit** |
| `FORMULATION.md` | **0.8000** | 0.8000 | 0.8000 | **EXACT** (A24 corpus) |

⭐ **The correct pin is the PARENT**, because a round's own commit holds the document **after** that
round appended to it: `DEFINITION.md` is **122** figures at the commit and **118** at the parent, and
the four are R753's own appended section *(ledger 1046)*. **The preregistration named this limit before
the run and printed the bracket; the bracket was the answer.**

⚠ **The earlier diagnosis was right in kind and 10× too small** *(ledger 1047)*: isolated document
drift contributes **0.0016**, against a **0.0202** discrepancy.

**Two populations, and R757 pinned neither.** At R753: documents 1205 / 4677 / 2397 lines; A24 rounds
**456**; repo-wide **525**. At HEAD: 1255 / 4875 / 2397; **460**; **529**.

**Controls — 5 PASS, 0 FAIL.** POSITIVE recovered deltas `{+50, +198, +0}`; band computed — a recovery
returning today's file gives **all-zero** deltas, **the exact failure this round's own first lookup
produced** *(ledger 1045)* · g=0 HEAD's tree reproduces today's rates exactly · NEGATIVE **both**
crossed cells fail, so **both** populations are needed · **SHAM** R750's trees reproduce R753 in only
**1 of 3**, so reproduction is specific to the right tree · PLACEBO byte-identical.
**CONFOUND, decisive:** 574 artifacts present at both commits, **0 changed in place**, 4 added.

**⭐ R756's finding SURVIVES the corpus correction** *(ledger 1048)*: repo-wide, between-round variance
**0.1036** vs null **0.0420** = **2.47×**, against 2.30× narrow. **The rate belongs to rounds, and that
was not an artifact of the scoping defect.**

**Registered.** P1 **yes at the parent** *(hard)* · P2 0.43 → **0.4320** ✓ · **P3 0.017 → 0.0016**, in
band but **10× wrong — drift was not the cause** · P4 2.0 → **2.47** ✓ · P5 455 → **456** ✓ · D ✓.

**The pin, applied to this round's own numbers:** `STATEMENT.md` 1255 / `f792bdd6bfc417e3` ·
`DEFINITION.md` 4875 / `7fbde36cf36daf8d` · `FORMULATION.md` 2397 / `36ae2fbc2875c9f4`.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 99887, **both writes confirmed to
disk** (4,386 / 4,390 bytes, differing only in the recorded seed).

## R759 · the provenance arc is WRITE-ONLY, and it closes here

**Question.** R758 refused to pay the recomputation debt blindly and asked which of R748–R756's
numbers anything actually reads.

**Answer.** Of **110 distinctive** numbers (≥4 dp) published across those nine rounds, **15 — 13.6% —**
appear in any strictly later round.

| class | era | n | **read by a later round** |
|---|---|---|---|
| **distinctive** | **R748–R756** | **110** | **0.1364** |
| NON-distinctive *(SHAM)* | R748–R756 | 65 | **0.6154** — **4.51× inflation** |
| distinctive | R700–R747 | 174 | **0.1954** — with 8 more rounds of exposure |

⛔ **"Appears in a deliverable" is NEAR-FORCED** — every round appends its own numbers to this file.
Printed, **excluded from the verdict**. ⛔ **A number can only be read by later rounds**, so decline
toward the present is partly mechanical — which is why the older era was measured.

⚠ **The confound bounds it, and was written before the run:** later rounds cite a round's **ID** 30
times against **9** value-reprints — **3.3×**. `13.6%` measures *numbers reprinted*, not *findings
used*, and the two are not converted into each other.

**Controls — 5 PASS, 0 FAIL.** POSITIVE `0.8000` read by [754, 756, 757, 758], band `0 < 2 ≤ 6` ·
g=0 a fabricated value read by **0** · NEGATIVE shuffled publishing rounds give 0.44–0.49 against the
real **0.1364** · SHAM as above · PLACEBO 0 of 110.

⛔ **Two defects in this round's own instrument, both caught by its controls.** ① The tracer scanned
**its own `run.py`**, detecting the fabricated constant it defines and counting itself as a reader —
**the instrument was part of its own corpus** *(ledger 1049)*. ② The **two-seed check** caught a real
non-determinism: `published()` returns a **set**, and hash-seed-dependent iteration resolved the
first-publisher tie-break differently, so a different value could win a tie and carry a different
reader set *(ledger 1050)*.

**⭐ The four most-read values are all R753's — `0.8000 / 0.3814 / 0.1793 / 0.6207` — and all four were
subsequently corrected.** The numbers this arc reused are the ones that turned out to be wrong: a
working retraction chain, and also reuse *for correction* rather than for building *(ledger 1052)*.

**Verdict — `WORLD B`.** The debt is near zero. **The provenance sub-arc closes** *(ledger 1051)*.
What outlives it is three instruments, not their rates: the one-arc lookup defect *(R757)*, the
parent-commit pin *(R758)*, and the 4.51× spurious-match price on non-distinctive values *(here)*.

**Reproducibility.** Byte-identical under `PYTHONHASHSEED` 0 and 31415 **after** the set-ordering
repair, **both writes confirmed to disk**.

## R760 · clause ③ by RULE instead of by NAME — the `16 vs 5` tension dissolves

**Question.** ③ is implemented as **four literal arm names**; R520 and R729 showed it **fails open**,
and R745 measured the cost — the census admits **3 target-reading objects** ③ is meant to exclude.
The builder names those rules exactly at `select_core.py:102`. **What does ③-by-rule cost?**

**⚠ P4 on both questions.** R509 killed a **behavioural** ③′ (*"makes the same vacuity harder to
see"*); R623 is a documentation-anchor rule. **A rule-based PROVENANCE ③ keeps ③'s type and changes
only its implementation — that is the gap.**

| clause ③ | admitted tags | admitted **objects** | excluded tags |
|---|---|---|---|
| **name** (current) | **16** | **9** | 76 |
| **RULE** | **9** | **5** | 83 |
| inverted *(block selectors)* | 14 | 8 | 78 |

**The 7 newly excluded** — `greedy_k4_greedy_kA/kB`, `indep_k4_indep_kA/kB`, `oracle_k4_08bR`,
`oracle_k4_oracle_kA/kB` — **are exactly R729's seven and R730's four objects.** Three rounds converge
on the same set from different directions. **All 5 committed members survive**, and `② ∧ ③rule` admits
**9 tags / 5 objects — NON-VACUOUS**.

⇒ **The extension over today's 92-arm population is 5 objects, identical to the committed one. The
`16 vs 5` tension was ③ being a list** *(ledger 1054)*.

**⛔ Two results were FORCED and are labelled.** **D1** the rule set is a **superset** of the blocklist
(every blocklisted name carries a target-reading prefix, asserted in code), so *"rule excludes more"*
is algebra and only the **size** measures. **D2** no committed member carries a target-reading prefix,
so the committed 5 are **invariant** — stated before the run, verified 5/5 on the outcome.

**⭐ The SHAM prices the list.** Five **random** size-4 blocklists admit **[20, 20, 19, 20, 19]**,
mean **19.6**, against the actual blocklist's **16** and the rule's **9**. **The four names buy 3.6
arms over an arbitrary list; the rule buys 10.6** *(ledger 1055)*.

**Controls — 6 PASS, 0 FAIL.** PROVENANCE all three source facts hold, else **exit 2** · POSITIVE
rule-③ **excludes** `oracle_k4_oracle_kA` and **keeps** `topw_k4`, against a band where a ③ blocking
**nothing** and one blocking **everything** are both unable to separate them · g=0 **0 UNPARSED** tags,
none silently admitted or blocked · NEGATIVE inverting the rule changes the set (14 vs 16), so **③ is
not decoration** · SHAM as above · **PLACEBO name-③ reproduces R728's committed 16 EXACTLY — the
harness *is* the census.**

⚠ **This repairs ③'s IMPLEMENTATION, not whether ③ is the right CLAUSE** — that still requires the
external criterion the impossibility register has always named.

**Reproducibility.** Two `PYTHONHASHSEED` runs, both writes confirmed to disk.

## R761 · ②-robustness over the full reference class, and its residual on A2 rank

**Scope.** population = 27 arms (R294's 18 k=4 census arms ∪ R729's seven target-reading tags ∪ the
five committed extension members); instrument = R294's estimator (paired cluster bootstrap, NBOOT
1200, seed 31337, MDE floor, three-valued `verdict`), reproduced at **1e-6 on 16/16** stored `c2`;
baseline = **the swept axis**, all C(16,4) = **1,820** size-4 subsets of `sat_genericpool16`; regime =
first release, home judge, **968** prompts. `promptecho_sham` has coverage **398/968** and is flagged;
the identity is recomputed on the 26 coverage-complete arms and is unchanged.

**rob(a)** = share of the 1,820 references at which arm *a* clears ②.

| arm | A2 | rob | ③name | ③rule |
|---|---|---|---|---|
| `oracle_k4` · `oracle_k4_oracle_kA` · `oracle_k4_oracle_kB` | 0.6283 | 1.0000 | 1 of 3 | BLK |
| `greedy_k4_greedy_kA` · `greedy_k4_greedy_kB` | 0.6226 | 1.0000 | . | BLK |
| `oracle_k4_fit1` | 0.6142 | 1.0000 | BLK | BLK |
| `greedy_k4_fit1` | 0.6106 | 1.0000 | BLK | BLK |
| `indep_k4_indep_kA` · `indep_k4_indep_kB` | 0.6031 | 1.0000 | . | BLK |
| `indep_k4_fit1` | 0.5941 | 1.0000 | BLK | BLK |
| `coval_core` | 0.5665 | 0.9978 | . | . |
| **`oracle_k4_08bR`** | **0.5649** | **0.9401** | **.** | **BLK** |
| `topw_k6` | 0.5641 | 0.9863 | . | . |
| `topw_k4` | 0.5642 | 0.9835 | . | . |
| `topw_k3` | 0.5632 | 0.9703 | . | . |
| `topw_k8` | 0.5593 | 0.8857 | . | . |
| `generic` | 0.5514 | 0.7780 | . | . |
| `gen` | 0.5352 | 0.0396 | . | . |
| the 6 sham/random/topabs/topvar/topwvar arms | 0.4828–0.5040 | 0.0000 | . | . |
| `promptecho_sham` *(coverage 398)* | 0.2599 | 0.0000 | . | . |

**E2 · inversions** rob vs mean A2: **4 of 351** pairs — `oracle_k4_08bR` vs `topw_k3` (ΔA2 +0.0017,
Δrob −0.0302), vs `topw_k4` (+0.0007, −0.0434), vs `topw_k6` (+0.0008, −0.0462), and `topw_k4` vs
`topw_k6` (+0.0001, −0.0027). SHAM S1, random ordering, 200 draws: **131.3 [89, 174]**, computed
ceiling 176.

**E3 · Jaccard with { rob = 1.0 }** ③name **0.400** · ③rule **0.909** · SHAM S2 random size-11
blocklist **0.254 [0.105, 0.500]**, exact-match rate **0.000**. Threshold curve
t ∈ {1.00, 0.99, 0.95, 0.90, 0.75} → ③name {0.400, 0.364, 0.286, 0.267, 0.235},
③rule {0.909, 0.833, 0.667, 0.733, 0.647}; **set equality at none**.

**Controls.** PROVENANCE 16/16 at 1e-6 · POSITIVE R527's committed `coval_core_by_spec` **8/8**
(band: admit-everything 7/8, admit-nothing 1/8) · g=0 planted null **0.0050 of 200** (band [0, ~0.50])
· NEGATIVE `coval_core` 0.9978 vs permuted **0.8422 [0.8242, 0.8599]**, `oracle_k4` 1.0000 vs 1.0000
· PLACEBO four `*_sham` arms **0.0000**. **WORLD C.**

**Derived, not measured.** ① rob is monotone in A2 up to the paired SE, so the arm ordering is forced
and only the residual measures. ② the 1,820-wide bootstrap is exact at marginal cost (linearity of the
bootstrap mean; `var(x−y)` by one matrix product) — asserted at 4 probe cells. ③ the exact self-cell
is `UNRESOLVED` by `verdict()`'s first branch.

## R762 · the resolution behind R761's ordering, and the interval rob never had

**Scope.** population = R761's 27 arms unchanged (so the rounds are comparable), of which **5 pairs
are degenerate** — identical per-prompt vectors, one object under R730 — leaving **346** resolvable
pairs of 351; instrument = R294's estimator, reproduced **exactly on 27/27** arms before any
contradiction was permitted; baseline = all 1,820 references; regime = first release, home judge,
968 prompts.

**E1 · resolution of a between-arm ΔA2** paired MDE median **0.0136**, IQR **[0.0097, 0.0149]**,
min 0.0031, max 0.0237. A second and **different** floor, R415's committed run-to-run re-selection
shift, is **0.116489**; the two are not interchangeable and both are reported.

**E2 · the floor curve**

| floor | surviving pairs | inversions | SHAM mean | P(sham = 0) |
|---|---|---|---|---|
| 0 | 346 | 4 | — | — |
| 0.5× MDE | 319 | **0** | 3.70 | 0.000 |
| 1× MDE | 304 | **0** | 3.54 | 0.000 |
| 2× MDE | 280 | **0** | 3.35 | 0.000 |
| 0.116489 | 81 | 0 | 0.90 | 0.375 |

R761's 4 inverting pairs collapse to **2 independent events** (`oracle_k4_08bR`, `topw_k4`).

**E3 · nested-bootstrap intervals on rob** (120 outer × 300 inner; POSITIVE-2: inner 1200 → 300 moves
rob by 0.0000 on all 27)

| arm | rob | 2.5% | 97.5% | share of outer draws at 1.0 |
|---|---|---|---|---|
| `oracle_k4` | 1.0000 | 1.0000 | 1.0000 | 1.000 |
| `coval_core` | 0.9978 | 0.8943 | 1.0000 | 0.250 |
| `topw_k6` | 0.9863 | 0.8463 | 1.0000 | 0.092 |
| `topw_k4` | 0.9835 | 0.8411 | 1.0000 | 0.067 |
| `topw_k3` | 0.9703 | 0.7997 | 1.0000 | 0.067 |
| `oracle_k4_08bR` | 0.9401 | 0.6077 | 1.0000 | 0.092 |

paired `08bR − coval_core` = **−0.0932 [−0.3584, +0.0212]**, not separated.

**Instrument identity of `oracle_k4_08bR`** — anchor test, both controls: matches `sat08_full.npz`
(0.8B) at **0.4609**, `sat_full.npz` (default) at **0.0345**; `oracle_k4` matches them at **0.0342**
and **0.5342**. `select_core.py:75` makes `--tag-suffix` mandatory off-default; R416 measured 91.1%
of this arm's prompts changing selection.

**Controls.** PROVENANCE 27/27 exact (exit 2 otherwise) · POSITIVE-1 346/346 at 2× MDE, none at 0.5× ·
POSITIVE-2 worst |Δrob| 0.0000 · g=0 planted zero never resolved · NEGATIVE pairing destroyed → MDE
×**1.80 [0.96, 3.70]** · PLACEBO 215 pairs at |ΔA2| > 0.05, **0** inversions · SHAM as tabled.
**WORLD A**, E3 verdict **UNRESOLVED**.

**Derived, not measured.** ① a floor can only remove inversions (monotone by subset), so only reaching
zero measures, and the size-matched random subset is what attributes it. ② three of R761's four pairs
are one arm against three arms lying within 0.0010 of each other — one event, three labels.

## R763 · whether a round moved the definition, measured three ways

**Scope.** population = the 24 rounds R739–R762 (matched to R664's n = 24 so the eras compare);
instrument = three classifiers, each with its own control set; baseline = R664's committed
**0 of 24** over R640–R663; regime = this repository, this tree_sha.

| unit | what it tests | % of page | count / 24 | own sham 95% | admissible |
|---|---|---|---|---|---|
| **C1** | R664's keyword rule on the headline | — | **1** | R664's control set | **YES** |
| C2 | commit edits `## The definition` block | 36.7% | 9 | [4, 12] | **NO** |
| C3 | commit edits a clause bullet | 3.1% | 2 | [0, 2] | **NO** |

**Rounds editing `STATEMENT.md` at all: 23 of 24**, so a positional unit covering *p* of the page is
hit at ≈ *p* of them by chance — C2 caught 9 of 23 = 39% against a 36.7% block.

**2×2 (C1 × C2).** OBJECT/OBJECT **1** (`R760`) · OBJECT/apparatus **0** · apparatus/OBJECT **8**
(`R739 R740 R741 R742 R745 R746 R761 R762`) · apparatus/apparatus **15**.

**Controls.** POSITIVE-1 C1 reproduces R664's committed `0 of 24` on R664's own era **exactly** ·
POSITIVE-2 C1 fires on R527/R519, C2 fires on R760 · NEGATIVE C1 not OBJECT on R654; 1 round touches
no `STATEMENT.md` and C2 fired on 0 of it · g=0 empty headline and empty diff both negative ·
PLACEBO keyword-free headline negative · SHAM ×2 as tabled. **WORLD A on the only admissible unit.**

**Combined with R664: 1 object headline in 48 rounds** (R640–R663: 0 of 24; R739–R762: 1 of 24).

**Impossible here, and now named with what it would require.** *Whether a round moved the definition*
is **not reconstructible from diffs** — two positional units, two sham failures. It would require a
**per-round declaration recorded at the time**: each README naming the clause it moves or naming NONE.
Intent is not in a diff.

## R764 · the three readings of ③ over 86 arms and ②'s whole baseline curve

**Scope.** population = **86** arms with full 968-prompt coverage (R534: 41); instrument = R294's
estimator for ②, `select_core.py`'s own selection expressions for ③; baseline = **the swept axis**,
8 percentiles of the 1,820-subset class including the published one; regime = first release, home
judge, this tree_sha.

**Readings, corrected from R534's own text before any code was written.**

| reading | excludes | admits |
|---|---|---|
| ③-rank | rank | weight, sat, weight+sat, neither |
| ③-any | rank, weight, weight+sat | **sat**, neither |
| ③-judge | rank, weight, sat, weight+sat | neither |

R534 computed ③-any and ③-judge with the same expression; its headline says *"a judge is not an
annotator"*, which admits the sat class to ③-any. Nesting `judge ⊆ any ⊆ rank` is **derived**.

**E1 · partition over 86 arms** rank **17** · weight **20** · sat **3** (`topvar_k4`, `_08b`,
`_08bR`) · weight+sat **3** (`topwvar_k4`, `_08b`, `_08bR`) · neither **42** · UNPARSED **1**
(`generic_reprov`, a re-provenance run of `generic` — **0 objects** under R730's partition).

**E3 · the grid**, tags (objects):

| baseline | \|②\| | ③-rank | ③-any | ③-judge |
|---|---|---|---|---|
| p000 | 24 | 11 (9) | **2 (2)** `gen`, `generic` | **2 (2)** |
| p005 | 23 | 10 (8) | **1 (1)** `generic` | **1 (1)** |
| p025 | 21 | 9 (7) | **1 (1)** `generic` | **1 (1)** |
| p050 | 21 | 9 (7) | **1 (1)** `generic` | **1 (1)** |
| p075 | 18 | 7 (5) | 0 | 0 |
| p095 | 16 | 6 (4) | 0 | 0 |
| **published** | 17 | **6 (4)** | **0** | **0** |
| p100 | 10 | 0 | 0 | 0 |

**Controls.** PROVENANCE R534's 41-arm partition reproduced exactly (exit 2 otherwise) · POSITIVE
four arms into four classes, band from both degenerate ends · g=0 `zzz_k4` UNPARSED not `neither` ·
NEGATIVE 200 random 5-class partitions → ③-any at published **6.90 [4, 11]** vs real **0** · PLACEBO
3 `*_sham` arms in 0 extensions · SHAM ② with no clause = the `|②|` column. **WORLD B** (object
unit; the tag-unit branch says C — both printed).

**Excluded, on evidence, named.** 7 foreign-key-schema artifacts (`transport_*`, another corpus);
5 with partial prompt coverage (`coval_core_2bA/2bB`, `promptecho`, `promptecho_sham`,
`provenance_probe`).

## R765 · the comparator in the census, and the pipeline's variance decomposition

**Scope.** population = **88** arms with a committed `core_*.json`; instrument = string equality on
per-prompt criterion sets, plus R294's estimator; baseline = all 8 percentiles as R764; regime =
first release, home judge, 968 prompts, this tree_sha.

**E1 · containment against `genericpool16`.** Comparator-identical (exact prefix on every shared
prompt): **`generic` alone**, 968/968, k=4, overlap 1.0000. `gen` 0.0010 · `full` 0.0000 ·
`coval_core_sham` 0.0000 · all 84 others 0.0000. **`coval_core` has no committed core JSON** (R441).

**E2 · ③-any with the comparator excluded.**

| baseline | ③-any as R764 ran it | comparator excluded |
|---|---|---|
| p000 | `gen`, `generic` | **`gen`** (pool-overlap 0.0010) |
| p005 · p025 · p050 | `generic` | — |
| p075 · p095 · published · p100 | — | — |

**1 of 8 cells**, not 4. `POOL[0:4]` at percentile 93.7 clears ② below itself by **construction**.

**E3 · the variance decomposition, from 34 identical-criteria groups.**

| class | pairs | \|Δ A2\| mean | min | max |
|---|---|---|---|---|
| same judge, identical criteria | **10** | **0.0000** | 0.0000 | 0.0000 |
| different judge, identical criteria | **38** | **0.0969** | 0.0597 | 0.1799 |
| same judge, re-selected criteria *(R415)* | — | **0.1165** | — | — |

Exact same-judge pairs: `topw_k4`/`_detA`/`_detB` · `random_k4_s0`/`_ctlS0` · `random_k4_s1`/`_ctlS1`
· `oracle_k4`/`_oracle_kA`/`_oracle_kB` · `greedy_k4_greedy_kA`/`kB` · `indep_k4_indep_kA`/`kB`.

**Open anomaly.** `generic` vs `genericpool16[:4]` = **0.0009 [−0.0006, +0.0024]**, identical on
**896/968** where every other same-judge pair is exact. Candidates: the pool tensor sums by index
order while the core JSON lists by string order, or the two artifacts scored different response sets.
The registered confound check passed on all pairs it could evaluate (**0 failures**) and cannot
evaluate this one.

**Controls.** PROVENANCE R764's 8×3 grid reproduced (exit 2 otherwise) · POSITIVE `generic` 1.0000
**and** `gen` 0.0010, band from both degenerate ends · g=0 shuffled pool → prefix 0.0000 · SHAM random
size-4 subsets → prefix 0.0000, subset 1.0000 · PLACEBO `full` 0.0000 · NEGATIVE **uninformative by
construction** — `generic` has **1** distinct criterion set across 968 prompts, so a derangement
changes nothing. **WORLD B.**

## R766 · the across-pass scoring floor, and why the thread is decision-inert

**Scope.** population = the 15,488 cells (968 prompts × 4 criteria × 4 responses) shared by
`sat_generic` and `sat_genericpool16[0:4]`, criterion strings identical (R765, 968/968); instrument =
direct value comparison, plus R294's estimator for the propagation; regime = first release, home
judge, this tree_sha.

**E1 · the discrepancy.** differing cells **5,235 / 15,488 = 0.3380** · differing prompts **957 / 968**
· \|Δ\| mean **0.008574**, median **0.000000**, p95 **0.030967**, max **0.062419** · signed mean
**+0.000613** · **share(`generic` > `pool`) = 0.1793**, outside the registered symmetric band
[0.40, 0.60] ⇒ **systematic offset, not run-to-run variance**.

**E2 · identical-criteria pairs.** 48 total; **16 carry a replication marker** (`_det`, `_ctl`,
`_kA`, `_kB` — determinism controls, or the same object under R730); 32 across-pass candidates.
⚠ LOWER BOUND: "same pass" is recorded nowhere in the release and is inferred from naming and R730.

**E3 · propagation to the decision.**

| | percentile of `POOL[0:4]` in its 1,820-subset class |
|---|---|
| committed *(R527)* | 93.7 |
| recomputed | **93.74** |
| perturbed ×200 at sd = 0.012816 | **94.16 [91.59, 96.59]** |

The point lies inside the interval — **the discrepancy cannot move any ② verdict**.

**Controls.** POSITIVE nested `topw_k` sweep, worst spread **0.000e+00** · g=0 artifact vs itself **0**
differing · NEGATIVE two different criteria differ on **0.9287** of cells · PLACEBO `topw_k4` vs
`_detA` at the **cell** level **0** differing · SHAM `generic` vs `gen` \|Δ\| mean **0.190755** vs
**0.008574**, so criterion identity buys **95.5%**. **WORLD B.**

**Status of the two published zeros.** R419 (`--limit 200`) and R765 (10 pairs) both measured
**within-pass** determinism and both are correct at that scope. The **across-pass** floor is
`UNVERIFIED` — neither measured nor refuted here.

**Impossible, named.** Whether two artifacts came from one scoring pass would need a run identifier
the release does not carry · whether a sat file scored the strings its core JSON lists would need
criterion **strings** in the npz, which stores **indices** · whether the offset is temperature, judge
version or batching would need the scoring harness's logs.

## R767 · the five committed members, three-valued

**Scope.** population = the five committed extension members plus the `topw_k` family and 3 placebo
arms; instrument = R294's estimator with `report.verdict`, B ∈ {1200, 4800, 19200}; baseline =
`POOL[0:4]` published (A2 **0.550436**) and the 8-point percentile curve; regime = first release,
home judge, **968** prompts, this tree_sha.

| arm | A2 | eff | CI | MDE | eff/MDE | verdict |
|---|---|---|---|---|---|---|
| `coval_core` | 0.5665 | +0.0160 | [0.0083, 0.0241] | 0.0106 | 1.509 | BEATS |
| `topw_k6` | 0.5641 | +0.0137 | [0.0059, 0.0209] | 0.0104 | 1.311 | BEATS |
| `topw_k4` | 0.5642 | +0.0137 | [0.0054, 0.0216] | 0.0109 | 1.264 | BEATS |
| `topw_k3` | 0.5632 | +0.0127 | [0.0045, 0.0203] | 0.0111 | 1.152 | BEATS |
| **`topw_k8`** | 0.5593 | **+0.0089** | **[0.0009, 0.0163]** | **0.0107** | **0.827** | **BELOW RESOLUTION** |

Unchanged at B = 4800 and B = 19200.

**The `topw_k` family** (the registered confound): k=1 **−0.0249 / −1.825 LOSES** · k=2 +0.0031 /
0.263 UNRESOLVED · k=3 BEATS · k=4 BEATS · **k=6 +0.0137 / 1.311 BEATS (peak)** · k=8 BELOW
RESOLUTION · k=12 −0.0124 / −1.094 LOSES. An inverted U with eff/MDE monotone falling 6 → 8 → 12.

**The convention, measured by the SHAM** (`mde=None`, the floor absent): exactly **1** verdict
changes — `topw_k8` → BEATS. **Extension = 4 with the floor, 5 without.**

**Across the baseline curve** — p000·p005·p025·p050·p075: **5 / 5** (both conventions agree) ·
**p095: 4 / 5** · **published: 4 / 5** · p100: 0 / 1.

**Controls.** POSITIVE 4 of 5 return BEATS, band from both degenerate ends · g=0 baseline vs itself
eff 0.000000 → **UNRESOLVED** · NEGATIVE `topw_k8` with the pairing destroyed ×200 → **200/200
UNRESOLVED** · PLACEBO `coval_core_sham`, `topw_k4_sham`, `gen_sham` → **LOSES**. **WORLD A.**

**This explains R760 vs R764.** R760's `admitted_rule` = 9 tags / 5 objects; R764's published
`3-rank` = 6 / 4. Two tags are R764's declared coverage exclusion (`coval_core_2bA/_2bB`, 200 of 968
prompts); the third, `topw_k8`, is the three-valued verdict read two-valued.

## R768 · the pairwise ordering matrix over the extension

**Scope.** population = the 5 committed extension members and the 7-arm `topw_k` family (11 distinct
arms); instrument = R294's estimator on **paired per-prompt differences**, B = 1200, `report.verdict`;
baseline = **none — these are arm vs arm**, the baseline appears only in controls; regime = first
release, home judge, 968 prompts, this tree_sha.

| a | b | eff | CI | MDE | verdict |
|---|---|---|---|---|---|
| `coval_core` | `topw_k8` | +0.0072 | [+0.0012, +0.0131] | 0.0085 | BELOW RESOLUTION |
| `topw_k4` | `topw_k8` | +0.0049 | [−0.0001, +0.0101] | 0.0076 | UNRESOLVED |
| `topw_k6` | `topw_k8` | +0.0048 | [+0.0009, +0.0087] | 0.0056 | BELOW RESOLUTION |
| `topw_k3` | `topw_k8` | +0.0039 | [−0.0024, +0.0095] | 0.0087 | UNRESOLVED |
| `coval_core` | `topw_k3` | +0.0033 | [−0.0031, +0.0096] | 0.0090 | UNRESOLVED |
| `coval_core` | `topw_k6` | +0.0024 | [−0.0030, +0.0075] | 0.0079 | UNRESOLVED |
| `coval_core` | `topw_k4` | +0.0023 | [−0.0038, +0.0084] | 0.0085 | UNRESOLVED |
| `topw_k3` | `topw_k4` | −0.0010 | [−0.0048, +0.0028] | 0.0054 | UNRESOLVED |
| `topw_k3` | `topw_k6` | −0.0009 | [−0.0062, +0.0040] | 0.0076 | UNRESOLVED |
| `topw_k4` | `topw_k6` | **+0.0001** | [−0.0041, +0.0044] | 0.0063 | UNRESOLVED |

**Resolvable by verdict: 0 of 10.** Surviving BH on the bootstrap p with no MDE floor: **2** —
`topw_k6 vs topw_k8`, `coval_core vs topw_k8`. The gap between those two counts is the MDE floor.

**Multiplicity**: 31 unordered pairs (D3 — antisymmetric, not 62), BH at q = 0.05, **17 survivors**,
all k-family pairs involving `k1`, `k2` or `k12`, the arms that lose outright.

**The ranking decomposition.** by **eff**: k4, k6, k3, k8, k2, k12, k1 · by **eff/MDE**: k6, k4, k3,
k8, k2, k12, k1 · by eff/**pooled** sd (sd removed): k4, k6, … — **1 transposition vs 0**, so the
"peak at k=6" is exactly one sd-driven inversion. `MDE = z·sd/√n`, so eff/MDE ranks by eff/sd.

**Controls.** POSITIVE `coval_core` vs `gen_sham` **+0.0837 [+0.0733, +0.0936]**, MDE 0.0153, BEATS ·
g=0 arm vs itself eff **0.000000** → UNRESOLVED · PLACEBO `topw_k4` vs `_detA` eff **0.000000** ·
NEGATIVE pairing destroyed ×200 → MDE **×2.25 [2.18, 2.32]** · CONFOUND corr(criterion overlap,
|eff|/MDE) = **−0.3949** over 27 pairs, so resolution does not track overlap. **WORLD A.**

## R769 · contains vs consumed, and the n each ordering would require

**Scope.** population = the release's **1,078** prompts against the estimator's **968**; instrument =
R294's estimator on paired per-prompt differences; regime = first release, home judge, this tree_sha.

**Contains vs consumed.** prompts 1,078 / 968 · annotations **18,384 / 15,593 = 0.8482** · annotators
per prompt median **16** on both sides — **the annotator dimension is exhausted**.

**Why the 110 drop.** absent from the base arm only **0** · absent from the pool only **0** · fewer
than 2 annotators **0** · **both coverage clauses at once 110**. **Recoverable for the five committed
arms: 0.** So 968 is the correct population and the campaign's numbers carry no hidden scope.

**The power curve** (`coval_core` vs `topw_k4`, 50 subsamples per n; the 1/√n law asserted, not fitted):

| n | MDE | sd | law | ratio | sham (with replacement) | negative / real |
|---|---|---|---|---|---|---|
| 100 | 0.02648 | 0.00304 | 0.02653 | 0.998 | 0.02689 | 2.22 |
| 200 | 0.01871 | 0.00160 | 0.01876 | 0.998 | 0.01864 | 2.23 |
| 400 | 0.01347 | 0.00064 | 0.01327 | 1.015 | 0.01337 | 2.23 |
| 600 | 0.01079 | 0.00038 | 0.01083 | 0.996 | 0.01082 | 2.26 |
| 800 | 0.00935 | 0.00017 | 0.00938 | 0.997 | 0.00932 | 2.26 |
| 968 | 0.00853 | 0.00000 | 0.00853 | 1.000 | 0.00796 | 2.17 |

Worst deviation **1.5%**.

**Required n per pair — a DERIVATION from the measured sd under a stated stability assumption:**
`topw_k6`/`topw_k8` **1,293** · `coval_core`/`topw_k8` **1,373** · `topw_k4`/`topw_k8` **2,376** ·
`topw_k3`/`topw_k8` **4,880** · `coval_core`/`topw_k3` **7,132** · `coval_core`/`topw_k6` **10,761** ·
`coval_core`/`topw_k4` **13,346** · `topw_k3`/`topw_k4` **28,456** · `topw_k3`/`topw_k6` **63,241** ·
**`topw_k4`/`topw_k6` 9,534,441**.

**Controls.** POSITIVE the 1/√n law to 1.5% · g=0 reproduces R768's committed MDEs exactly · NEGATIVE
pairing destroyed → ratio **2.17–2.26** at every n · SHAM drawing with replacement gives the same MDE
(0.993 at n = 400), so only NEW prompts move the curve · PLACEBO self-difference MDE **0.0** ·
CONFOUND **UNIDENTIFIED** — 0 recoverable, so the sd comparison could not be made. **WORLD B.**

## R770 · the variance decomposition, and the partition test

**Scope.** population = 968 prompts, the 5 committed members (10 pairs); instrument = annotator-level
agreement vectors, paired per-prompt differences; regime = first release, home judge, this tree_sha.

**E1 · decomposition** (within = annotator draw, between = prompts):

| pair | between | within | ratio | within share | max MDE gain |
|---|---|---|---|---|---|
| `coval_core`/`topw_k3` | 0.009901 | 0.001867 | 5.30 | 0.1587 | 8.3% |
| `coval_core`/`topw_k4` | 0.008970 | 0.001689 | 5.31 | 0.1585 | 8.3% |
| `coval_core`/`topw_k6` | 0.007637 | 0.001529 | 4.99 | 0.1668 | 8.7% |
| `coval_core`/`topw_k8` | 0.008982 | 0.001546 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k4` | 0.003657 | 0.000659 | 5.55 | 0.1527 | 8.0% |
| `topw_k3`/`topw_k6` | 0.007135 | 0.001228 | 5.81 | 0.1469 | 7.6% |
| `topw_k3`/`topw_k8` | 0.009287 | 0.001464 | 6.34 | 0.1362 | 7.1% |
| `topw_k4`/`topw_k6` | 0.004871 | 0.000823 | 5.92 | 0.1446 | 7.5% |
| `topw_k4`/`topw_k8` | 0.007177 | 0.001139 | 6.30 | 0.1370 | 7.1% |
| `topw_k6`/`topw_k8` | 0.003805 | 0.000635 | 5.99 | 0.1431 | 7.4% |

**E2 · heterogeneity** I² **0.833–0.864**; `mean/sd` **0.0009–0.0779**, so a balanced sign split is
nearly forced (D3) and the observed `d > 0` shares of **0.16–0.32** are **not** read as a minority
carrying the mean, because the complement includes exact ties.

**E3 · partition test** — a flip = two levels with opposite-sign means, both clearing their own MDE.
S1 annotator count **0** · S2 response-set size **0** · S3 baseline A2 **0**. **90 cells, 0 flips**;
sham (200 random equal-sized partitions) **0.00 [0, 0]**; negative (200 label permutations) **0.00**.

**Controls.** POSITIVE a centred, swept plant: 0× **False**, 0.5× False, 1.0× False, **2.0× True** —
the registered band is *0× must not fire, 2× must*; 1× is the test's own 50%-power point and was never
a registered criterion. g=0 delta 0 finds nothing · PLACEBO an arm against itself, variance **0.0**,
flips 0. **WORLD A.** ⚠ Resolution: a flip needs ≳2× the half-sample MDE ≈ **0.024**.

## R771 · the correlation structure of the ten difference vectors

**Scope.** population = 968 prompts, 5 committed members, their 10 pairwise differences; instrument =
per-prompt A2 over all annotators, Pearson correlation across prompts; baseline = a **generated**
independence model, not a chosen number; regime = first release, home judge, this tree_sha.

**Rank and spectrum.** rank **4** (forced: 5 arms − 1); eigenvalues **[3.791, 2.957, 1.771, 1.481,
0, 0, 0, 0, 0, 0]**; leading share **0.3791**; uniform reference at rank 4 = **0.2500**.

**E1 · residual variances**, identified from 10 equations in 5 unknowns (`var(d_ab) = v_a + v_b`):
`coval_core` **0.005878** · `topw_k3` **0.004042** · `topw_k8` **0.003799** · `topw_k4` **0.002273** ·
`topw_k6` **0.001864**. Relative fit residual **0.1748**, all positive → admissible. A negative `v`
would have refuted the model at that arm; clipping was forbidden in advance.

**E2 · observed vs the independence prediction** (computed per pair from the fitted `v`, never a 0.5
constant): arm-sharing (n=30) |observed| **0.4864** vs |predicted| **0.4938**, **excess −0.0074**;
disjoint (n=15) observed **+0.0312** vs predicted **0**.

**E3 · spectrum vs simulation.** sham — 200 draws of independent residuals at the fitted variances —
**0.3072 [0.2974, 0.3172]**; observed **0.3791**, above the band.

**Calibration.** The positive control's monotone dose curve (differential loadings
[+1.0, +0.5, 0, −0.5, −1.0]): λ 0.00 → 0.3121 · 0.25 → 0.3183 · 0.50 → 0.3556 · 1.00 → 0.4843.
Observed 0.3791 interpolates to **λ ≈ 0.59 × the residual sd**.

**Controls.** POSITIVE monotone, detected from λ = 0.25, not at 0 · g=0 λ = 0 inside the sham band ·
SHAM as above · NEGATIVE 200 independent prompt permutations → **0.1164 [0.1127, 0.1207]** · PLACEBO
`topw_k4` vs `_detA` sd **0.0** and excluded by construction.
**WORLD: none claimed — the two estimands split, and A and B each required both.**

⛔ **A factor loading EQUALLY on all arms is invisible in differences** — `d_ab` retains only
`λ(√v_a − √v_b)·f`, which vanishes at equal variances. The first plant was that object and produced
0.308–0.312 at every loading including 1.0.

## R772 · the per-prompt separability scale

**Scope.** population = 968 prompts, 5 committed members, 10 pairwise differences; instrument =
per-prompt A2 over all annotators; baseline = a generated independence model with a planted
multiplicative scale; regime = first release, home judge, this tree_sha.

**E1 · |d| co-movement.** disjoint (15 cells, admissible) **+0.2974** · arm-sharing (30 cells, co-move
with no scale by D2) +0.4560 · independence reference over 200 simulations **+0.0000 [−0.0314,
+0.0323]**. Dose curve: width 0.25 → +0.0950 · 0.50 → +0.2731 · 1.00 → +0.5204 ⇒ observed calibrates
to a **lognormal width ≈ 0.55**.

**E2 · what the scale is.** corr(`c`, per-prompt annotator agreement) **+0.1246** · corr(`c`,
per-prompt within-SE) **+0.5278** (r² **0.2786**) against a pre-registered line of **0.50** — fires by
**+0.0278**. `c(p)` quantiles **[0.0000, 0.0055, 0.0333, 0.0667, 0.3042]**, **223 zeros**.

**E3 · leave-one-pair-out normalisation** (the all-pairs version is circular and its 0.3330 is
inadmissible): raw leading share **0.3791** → LOPO **0.3298**; SHAM, a random draw from `c`'s own
distribution, **0.3822 [0.3541, 0.4090]**; NEGATIVE, a permuted `c`, **0.3826 [0.3528, 0.4099]**.
Both controls **raise** the share; only the aligned scale lowers it. Divisor floor **0.00893**.

**Controls.** POSITIVE a **multiplicative** plant, monotone, detected from width 0.25 not at 0 · g=0
width 0 inside the band · PLACEBO `topw_k4` vs `_detA` max |d| **0.0** · SHAM/NEGATIVE as above.
**WORLD B — a partly noise-amplitude map**, called on a 0.028 margin, with r² printed beside the label.

## R773 · the 223 ties, and the invariance of eff/MDE to dropping them

**Scope.** population = 968 prompts split into **223 tied** and **745 discriminating** — two
populations, never pooled; instrument = A2 (sign-based) plus a magnitude-sensitive alternative, both
stated; regime = first release, home judge, this tree_sha.

**E1 · the invariance (a DERIVATION).** Dropping exact zeros scales the effect by `n_f/n_d` and the
MDE by `sd_ratio·√(n_f/n_d)` — the same factor to O(μ²/σ²), μ/σ = 0.024. Measured over ten committed
pairs: ratios **0.9998–1.0008**, **verdict changes 0 of 10**, `n_required × 0.7696`.

**E2 · on the 223 tied prompts.** sign vectors identical **0.9740** [0.9596, 0.9910] · satisfaction
cosine distance **0.0046** [0.0014, 0.0082] · quantiles **[0.0002, 0.0008, 0.0021, 0.0051, 0.0185]** ·
share > 0.20 **0.0000** · share < 0.05 **0.9969**.

**E3 · a magnitude-sensitive estimator on the same prompts.** Largest eff/MDE **0.570**
(`topw_k3`/`topw_k4`); **0 of 10** pairs separate. ⚠ A different estimand — *"does the arm order the
responses like the human"* vs *"does its sign pattern match"* — so a separation would not have shown
A2 wrong.

**Controls.** POSITIVE `coval_core` vs `gen_sham` on tied prompts **0.0358** against the largest
committed pair **0.0082** (**4.36×**), band computed on this subset [−8.46e-18, 0.2794] · g=0
**−8.46e-18**, PLACEBO **−4.98e-19**, both at tolerance **1e-9** (a floating-point cosine identity is
not exactly zero) · SHAM the same distance on the 745 discriminating prompts **0.0066** vs tied
**0.0046** (0.696) · NEGATIVE 200 random equal-sized subsets **0.0062 [0.0055, 0.0069]**.
**WORLD A — STRUCTURAL.**

## R774 · who owns the scale — the prompt, or the five arms that defined it

**Scope.** population = 968 prompts; committed family = the 5 extension members; comparison family =
`random_k4_s0/s1/s2`, `topabs_k4`, `topvar_k4` — **disjoint**, asserted, exit 2 otherwise; instrument =
A2 per prompt over all annotators, cosine distance on satisfaction vectors; regime = first release,
home judge, this tree_sha.

**E1/E2 · two curves, never their ratio** (D1: corr(c, committed) = +0.2042 puts the regressor in the
denominator):

| c quartile | n | c | committed | sham | ratio |
|---|---|---|---|---|---|
| Q1 | 242 | 0.0003 | 0.0047 | 0.0354 | 7.47 |
| Q2 | 237 | 0.0200 | 0.0059 | 0.0376 | 6.32 |
| Q3 | 244 | 0.0486 | 0.0061 | 0.0313 | 5.15 |
| Q4 | 245 | 0.1124 | 0.0078 | 0.0340 | 4.34 |

**corr(c, sham) = −0.0212** (flat) · **corr(c, committed) = +0.2042** (rising).

**E3 · ownership.** split-half reliability committed **0.8806**, comparison **0.8438**, attenuation
ceiling **0.8620**. Cross-family **+0.2438 = 0.283× ceiling**. SHAM — the committed five split into
**overlapping** halves — **+0.5097**, i.e. arm-sharing buys **2.09×**. NEGATIVE 200 one-sided
permutations **−0.0021 [−0.0654, +0.0665]**. PLACEBO a family against itself **1.000000**.

**Calibration.** Planted prompt-scale dose curve: 0.00 → −0.0192 · 0.25 → +0.3380 · 0.50 → +0.6076 ·
1.00 → +0.8582. Observed **+0.2438** interpolates to a width of **≈0.18**; R772's within-family
spectral estimate was **0.59**.

**Confound printed, not assumed away.** mean A2 committed **0.5635** vs comparison **0.4910**; `c`
quartiles committed [0.0055, 0.0333, 0.0667] vs comparison [0.0416, 0.0856, 0.1479].

**WORLD: none claimed** — registered A needed ≥0.5× the ceiling, B ≤0.2×, and 0.283 is neither.

## R775 · four disjoint families, and the rule gradient

**Scope.** population = 968 prompts; four families of five arms with **zero shared objects** under
R730, every member default-judge (no `_08b`, R765) and non-replica (no `_ctl`/`_det`, R766) —
F1 committed `coval_core, topw_k3/k4/k6/k8` · F2 selector-seed `random_k4_s0/s1/s2, topabs_k4,
topvar_k4` · F3 target-reading `oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1,
greedy_k4_greedy_kA` · F4 selector-k `random_k2/k3/k6/k8/k12_s0`; regime = first release, home judge,
this tree_sha.

| pair | raw | ceiling | relative | class |
|---|---|---|---|---|
| F2 × F4 *(both `random_k`)* | 0.6017 | 0.8410 | **0.7154** | sel–sel |
| F1 × F2 | 0.2438 | 0.8580 | **0.2841** | sel–sel |
| F1 × F4 | 0.1716 | 0.8565 | **0.2003** | sel–sel |
| F1 × F3 | 0.1353 | 0.8863 | 0.1527 | sel–TARGET |
| F3 × F4 | −0.0020 | 0.8688 | −0.0023 | sel–TARGET |
| F2 × F3 | −0.0120 | 0.8702 | −0.0138 | sel–TARGET |

**Reliabilities** F1 0.8738 · F2 0.8424 · F3 0.8990 · F4 0.8396.
**Family levels** mean A2 0.5635 / 0.4910 / **0.6140** / 0.4942 · internal mean |d| 0.0457 / 0.1017 /
**0.0305** / 0.0935 — **F3 is compressed to a third of the selector families**.

**Controls.** DISJOINT 0 shared objects (exit 2 otherwise) · POSITIVE a planted prompt-scale, all six
detected from width 0.25, min **+0.2770 → +0.7871**, monotone · g=0 width 0 not all detected ·
NEGATIVE 200 one-sided permutations **+0.0017 [−0.0629, +0.0603]** · PLACEBO **1.000000** · SHAM
within-family overlapping halves F1 **+0.5097** · F2 **+0.6545** · F3 **+0.8512** · F4 **+0.4256**.
**WORLD C** — the target-reading family is compressed.

⚠ **The axis null is under-powered by construction**: four families admit four labelings, so the
observed difference **+0.3544** equals the permutation interval's upper end **[−0.2117, +0.3544]**.

## R776 · six families, and the first quantity with no arm in it

**Scope.** population = 968 prompts; six families of five arms, **zero shared objects** under R730,
all default-judge and non-replica — `Ra/Rb/Rc` = `random_k{2,3,6,8,12}_s{0,1,2}` (pure `random_k`,
differing only in seed) · `F1_committed` · `F3_target` · `M_mixed_sel`; regime = first release, home
judge, this tree_sha.

**E3 · the arm-free covariate** `poolspread(p)` = spread of the 16 pool criteria × 4 responses.

| family | corr | with poolmean | partial |
|---|---|---|---|
| F1_committed | **−0.1782** | +0.0250 | −0.1861 |
| F3_target | −0.0914 | −0.0248 | −0.1139 |
| Rb_random_s1 | −0.0767 | +0.1244 | −0.0248 |
| M_mixed_sel | −0.0688 | +0.0703 | −0.0423 |
| Rc_random_s2 | −0.0664 | +0.1016 | −0.0244 |
| Ra_random_s0 | −0.0490 | +0.1138 | +0.0010 |

**0 of 6 ≥ 0.30 · 5 of 6 < 0.15**; SHAM **−0.0005 [−0.0644, +0.0591]**; corr(poolspread, poolmean)
**−0.4387**. **WORLD B — rule artifact; the prompt-property mechanism is refuted.**

**E1 · the 15 pairs, relative to each pair's own ceiling.** pure-random × pure-random **0.6283 ·
0.6386 · 0.6168** · pure-random × mixed **0.7151 · 0.7033 · 0.7018** · pure-random × committed
**0.1995 · 0.2578 · 0.2224** · committed × mixed **0.2835** · committed × target **0.1519** ·
target × anything **−0.0023 · 0.0033 · −0.0103 · −0.0137**.

**E2 · the registered axis test.** SAME-RULE **0.6279** (n=3) vs "diff-rule" **0.2677** (n=12),
difference **+0.3602**, rank 4/20, **p = 0.2000** (floor **0.0500** — C(6,3) = 20 assignments).
⚠ **Uninformative**: `M_mixed_sel` holds 3 of 5 `random_k` arms, so three majority-same-rule pairs sat
in the diff-rule block. **Post-hoc**: pure-random pairs **0.6279** vs pairs with no pure-random family
**0.1406**.

**Controls.** DISJOINT 0 shared objects · POSITIVE planted scale, all 15 detected from width 0.25,
covariate 0.5806 → 0.9106, monotone · g=0 not all detected at width 0 · NEGATIVE **+0.0058 [−0.0607,
+0.0651]** · SHAM as above · PLACEBO **1.000000**.

## R777 · ordering disagreement — the second arm-free candidate, and a failed derivation

**Scope.** population = 968 prompts; R776's six disjoint families unchanged; instrument = A2 per
prompt over all annotators, plus `orderdisagree(p)` = mean pairwise disagreement of the 16 pool
criteria's induced sign vectors over the 6 response pairs; regime = first release, home judge, this
tree_sha.

**k is dead by derivation.** `F3` × `M` share k exactly (both {4}) → **−0.0137**, the lowest of 15;
`Ra` × `M` share none → **+0.7151**, the highest. corr(k-overlap, relative) = **+0.1620**.

**The covariates are distinct.** corr(orderdisagree, poolspread) = **−0.5901**; corr(orderdisagree,
tieshare) = **+0.7392** (the registered confound). `orderdisagree` mean **0.2618**, sd **0.1210**.

| family | random? | corr | partial (tie share) |
|---|---|---|---|
| F1_committed | — | **+0.2182** | +0.1755 |
| F3_target | — | +0.1461 | +0.1089 |
| Rb_random_s1 | RANDOM | +0.0994 | +0.0550 |
| Rc_random_s2 | RANDOM | +0.0961 | +0.0236 |
| M_mixed_sel | RANDOM | +0.0956 | +0.0677 |
| Ra_random_s0 | RANDOM | +0.0699 | +0.0385 |

random-containing mean |corr| **0.0902** · others **0.1821** · **gap −0.0919** (backwards).
**0 of 4** random families ≥ 0.30; **5 of 6** < 0.15. **WORLD B.**

**Conditioning changes nothing.** `Ra`×`M` 0.6017 → 0.5992 (**0.4%**) · `Rb`×`M` 0.5917 → 0.5878
(0.7%) · `Rc`×`M` 0.5895 → 0.5857 (0.6%).

**The failed derivation.** D3 held that |d| must rise with ordering disagreement by construction. The
synthetic control confirms the mechanism — width 0.25 → **+0.6260**, 0.50 → **+0.6503**, 1.00 →
**+0.5465**, and **UNDEFINED** at zero disagreement — so it recovers **6.5×** what the real arms show.
⚠ Not monotone at the top: at high disagreement the between-prompt variance the correlation needs
collapses.

**Controls.** POSITIVE as above · g=0 undefined at zero, printed as undefined · NEGATIVE 200
permutations **+0.0011 [−0.0604, +0.0674]** · SHAM random draw from the covariate's own distribution
**+0.0033 [−0.0657, +0.0662]** · PLACEBO **1.000000**.

## R778 · the covariates were computed on the wrong criterion set

**Scope.** population = 968 prompts; R776's six disjoint families unchanged; instrument = A2 per
prompt over all annotators, covariates from the prompt's own rubric (`sat_full.npz` /
`core_full.json`); regime = first release, home judge, this tree_sha.

**Object check.** distinct pool sets across 968 prompts **1** (prompt-blind) · `random_k4_s0` ⊂ pool
**0/968** · `topw_k4` ⊂ pool **0/968** · `random_k4_s0` ⊂ **rubric 968/968** · distinct criteria used
**3,869** against the pool's **16**. Rubric size median **15**, range **4–39**.

| family | random? | `n_rubric` | `rubricdisagree` | `rubricspread` |
|---|---|---|---|---|
| Ra_random_s0 | RND | +0.1052 | **+0.3206** | +0.1041 |
| Rb_random_s1 | RND | +0.1549 | **+0.3393** | +0.0653 |
| Rc_random_s2 | RND | +0.1119 | **+0.3588** | +0.0977 |
| M_mixed_sel | RND | +0.1289 | **+0.3649** | +0.0742 |
| F1_committed | — | −0.0181 | +0.2742 | −0.0911 |
| F3_target | — | −0.0552 | +0.1689 | −0.0612 |
| **≥ 0.30 among the 4 random** | | **0/4** | **4/4** | **0/4** |

**Degenerate prompts** (`n_rubric ≤ k`, the draw is the whole rubric and |d| = 0): k=4 **3** · k=6
**18** · k=8 **80** · **k=12 302 (31%)**.

**Conditioning on each covariate**, M × R raw 0.5895–0.6017: `n_rubric` **+1.1%** · `rubricdisagree`
**+9.6%** · `rubricspread` **+0.4%**.

**Controls.** OBJECT as above (exit 2 otherwise) · POSITIVE synthetic k-subsets, size-spread 0.25 →
+0.0379, 0.50 → +0.1273, 1.00 → **+0.3109**, monotone · g=0 fixed size → **UNDEFINED** · NEGATIVE 200
permutations **−0.0003 [−0.0552, +0.0667]** · SHAM **+0.0010 [−0.0619, +0.0549]** · PLACEBO
**1.000000** · CONFOUND corr(`n_rubric`, a baseline arm's A2) **−0.0190**. **WORLD B.**

## R779 · the mediation bound

`corr(A,B)` between arm families **0.5943**. Required single-covariate correlation `sqrt(r)`
**0.7709**. Best achieved with either scale **0.3649** (`rubricdisagree`) → **2.11× short**.

**Bound vs measured drop**, 6 covariates × 3 M×R pairs, largest four:

| covariate × pair | r(Z,A) | r(Z,B) | bound | measured | gap |
|---|---|---|---|---|---|
| rubricdisagree × Rc | +0.3588 | +0.3649 | +0.1309 | +0.0618 | −0.0691 |
| rubricdisagree × Rb | +0.3393 | +0.3649 | +0.1238 | +0.0575 | −0.0663 |
| rubricdisagree × Ra | +0.3206 | +0.3649 | +0.1170 | +0.0521 | −0.0649 |
| overlap × Rb | −0.1708 | −0.1543 | +0.0264 | +0.0110 | −0.0154 |

**All 18 gaps negative**; worst |gap| **0.0691**. Spearman bounds are larger than Pearson in every
cell, so the Pearson figure does not flatter the null.

**In-sample multiple correlation** (a ceiling, not an estimate): Ra **0.3938** · Rb **0.4110** ·
Rc **0.4133** · F1 **0.3102** · F3 **0.2034** · M **0.4290**. Reaching 0.7709: **0 of 6**.

**Overlap shared across families 0.8871** against scales at **0.5943**.

**Controls.** PLACEBO **1.000000** · g=0 **+0.0000** inside the negative band · NEGATIVE 200
permutations **+0.0001 [−0.0010, +0.0023]** · SHAM **+0.0000** · POSITIVE (rebuilt, generative share
1.0 by construction) recovered **1.0526** at w=0.5 and **1.0000** at w=1.0 · SPEARMAN on every
correlation. **WORLD A.**

## R780 · clause ② across two releases

**Release 2**: 2,200 conversations · 7,344 interactions · strata 2:**5204** / 3:**456** / 4:**1684** ·
7 arms · blind reference `core_generic.json`, **the same file as release 1's**.

| contrast | n | eff | CI | MDE | verdict |
|---|---:|---:|---|---:|---|
| r1 `gen` − blind | 968 | **−0.0267** | [−0.0424, −0.0115] | 0.0216 | **LOSES** |
| r2 `gen` − blind | 1684 | **+0.0020** | [−0.0065, +0.0104] | 0.0124 | **UNRESOLVED** |
| r1 `gen_sham` − blind | 968 | −0.1043 | [−0.1191, −0.0887] | 0.0219 | LOSES |
| r2 `gen_sham` − blind | 1684 | −0.0243 | [−0.0346, −0.0134] | 0.0151 | LOSES |
| r2 `vacuous` − blind | 1684 | −0.0396 | [−0.0487, −0.0306] | 0.0131 | LOSES |
| r2 `randblind_s0` − blind | 1684 | −0.0313 | [−0.0424, −0.0192] | 0.0168 | LOSES |
| r2 `randblind_s1` − blind | 1684 | −0.0516 | [−0.0664, −0.0358] | 0.0219 | LOSES |
| r2 `randblind_s2` − blind | 1684 | −0.0221 | [−0.0317, −0.0112] | 0.0153 | LOSES |
| r1 `gen` − blind, ALL annotators *(specification)* | 968 | −0.0162 | [−0.0247, −0.0082] | 0.0119 | LOSES |
| r2 n=2 *(not gauge-matched)* | 5204 | +0.0065 | [−0.0050, +0.0183] | 0.0170 | UNRESOLVED |
| r2 n=3 *(not gauge-matched)* | 456 | +0.0117 | [−0.0124, +0.0358] | 0.0357 | UNRESOLVED |

**Blind-arm spread on release 2: 0.0295**, against an MDE of 0.0124–0.0219.
**Required n** to resolve a release-1-sized effect on release 2: **366**, have **1,684**.
**Census**: 21 unscoped-wall lines, **13** at or before R556, **8** after.

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.000000** both · g=0 **0.000000** both ·
NEGATIVE target-permuted 200 draws r1 **[−0.0215, +0.0221]**, r2 **[−0.0159, +0.0161]** · the
pairing permutation is a **DERIVATION** (3.4e-18 / 7.5e-19), labelled not reported · SHAM
prompt-specificity ABSENT **−0.0313** · POSITIVE swept 0 → **UNRESOLVED**, 0.25/0.50/1.00 → BEATS on
both releases, band floor **+0.0000** < t < ceiling **+0.4478** · SEARCH positive and negative both
PASS. **NO WORLD CLAIMED.**

## R781 · the reference class, measured

**Class**: C(16,4) = **1820** subsets of `sat_genericpool16.npz` · 968 prompts · mean A2 **0.5386** ·
range **[0.5144, 0.5575]** = **0.0431** wide · mean pairwise correlation **+0.8709** →
**n_eff = 1.1**.

**q = fraction of the class an arm beats, leave-one-out** (20 k=4 arms, full coverage):

| arm | A2 | q | q resolved |
|---|---:|---:|---:|
| oracle_k4 / _oracle_kA / _oracle_kB | 0.6283 | 1.0000 | 1.0000 |
| greedy_k4_greedy_kA / _kB | 0.6226 | 1.0000 | 1.0000 |
| oracle_k4_fit1 | 0.6142 | 1.0000 | 1.0000 |
| greedy_k4_fit1 | 0.6106 | 1.0000 | 1.0000 |
| indep_k4_indep_kA / _kB | 0.6031 | 1.0000 | 1.0000 |
| indep_k4_fit1 | 0.5941 | 1.0000 | 1.0000 |
| topw_k4 / _detA / _detB | 0.5642 | 1.0000 | 0.9835 |
| **generic = POOL[0:4]** | 0.5504 | **0.9379** | 0.7422 |
| topwvar_k4 | 0.5040 | 0.0000 | 0.0000 |
| random_k4_s1 | 0.4981 | 0.0000 | 0.0000 |
| random_k4_s0 | 0.4927 | 0.0000 | 0.0000 |
| topabs_k4 | 0.4894 | 0.0000 | 0.0000 |
| random_k4_s2 | 0.4884 | 0.0000 | 0.0000 |
| topvar_k4 | 0.4863 | 0.0000 | 0.0000 |

**Shape**: in [0.35, 0.65] **0 of 20** · outside [0.10, 0.90] **20 of 20**. Self-matching references
excluded: **1**.

**Release 2** (5-member blind class, q takes 6 values): transport_gen 0.5541 / 1.00 ·
transport_generic 0.5522 / 1.00 · randblind_s2 0.5301 / 0.75 · gen_sham 0.5278 / 0.60 ·
randblind_s0 0.5209 / 0.50 · vacuous 0.5126 / 0.25 · randblind_s1 0.5006 / 0.00.

**DERIVED, not measured**: median-dominance IS p50; mean-dominance is the skew's percentile.

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.0000** · g=0 a class member returns
**0.7273** against its own rank **0.7269** · POSITIVE dominating plant **1.0000**, dominated
**0.0000**, all real arms inside the measured band · ⛔ NEGATIVE **[0.9374, 0.9379]** vs real 0.9379 —
**VOID, a derivation** · ⛔ SHAM **1.0000 > 0.9379** — **VOID, a poison**. **WORLD B printed; the
distributional reading UNVERIFIED on n_eff.**

## R782 · realised size, the comparator pair, and the corrected population

**Size read from the sat file** (distinct criterion indices per prompt), 50 arms, **18 ragged**:

| arm | size distribution | off-modal |
|---|---|---:|
| `full` (the rubric) | 4 … 39 | 887 of 968 |
| `random_k12_s0/s1/s2` · `topw_k12` | {4:3, 5:1, 6:14, 7:31, 8:31, 9:29, 10:57, 11:68, 12:734} | 234 |
| `random_k8_s0/s1/s2` · `topw_k8` | {4:3, 5:1, 6:14, 7:31, 8:919} | 49 |
| **`coval_core`** · `coval_core_sham` | **{2:1, 3:42, 4:925}** | **43** |
| `random_k6_s0/s1/s2` · `topw_k6` | {4:3, 5:1, 6:964} | 4 |
| `gen` · `gen_sham` | {1:1, 3:1, 4:966} | 2 |

**Prompts whose rubric holds fewer than 4 criteria: 0.** Core files and sat files agree on size for
all **48** arms with a readable core file; `coval_core` and `generic_reprov` have none.

**`POOL[0:4]` vs `sat_generic.npz`**: arrays identical **False**, max |dY| **0.120967** · A2
**0.550436** vs **0.551354** · paired **−0.000918** [−0.002430, +0.000562], MDE **0.002188**,
**UNRESOLVED** · differs on **73 of 968** prompts, max |diff| **0.2500**.

**Filters**: name regex **20** · strict k=4 everywhere **22** · modal k=4 **26**.
`modal \ name` = coval_core, coval_core_sham, gen, gen_sham, generic, generic_reprov.
`modal \ strict` = coval_core, coval_core_sham, gen, gen_sham. `name \ modal` = ∅.

**q over the corrected 26** (n_eff 1.1, so a band fraction, not a probability): oracle family
0.6283/1.0000 · greedy_kA/kB 0.6226/1.0000 · oracle_fit1 0.6142/1.0000 · greedy_fit1 0.6106/1.0000 ·
indep_kA/kB 0.6031/1.0000 · indep_fit1 0.5941/1.0000 · **coval_core 0.5665/1.0000, q_res 0.9978** ·
topw_k4/detA/detB 0.5642/1.0000, q_res 0.9835 · generic & generic_reprov 0.5514/0.9538, q_res 0.7780 ·
**gen 0.5352/0.3308, q_res 0.0396** · nine arms 0.4828–0.5040 at 0.0000.
**Shape: middle band 0.0000 · extreme 0.9615 · the one arm in neither is `gen`.**

**Controls.** OBJECT as above, exit 2 otherwise · PLACEBO **0.000000** · g=0 same file twice
**0.000000**, UNRESOLVED · REPLICA `topw_k4` vs `topw_k4_detA` **0.000000** — the negative's job, the
permutation null being void by derivation · POSITIVE 0× / 0.5× / 1× UNRESOLVED, 4× **BEATS**, band
computed at both ends · ⛔ SHAM **INADMISSIBLE**: a sham is undefined for a prompt-blind arm.
**WORLD B — different objects, below resolution.**

## R783 · the release side, measured

**Release** `data/conversation_rubrics.jsonl`: **986** records, **986** distinct ids, **0**
duplicates, **0** missing a key.

| field | release | scored sat file |
|---|---|---|
| `coval_core` size | **{2: 1, 3: 43, 4: 942}** | **{2: 1, 3: 42, 4: 925}** |
| `coval_full` size | min **4** max **39**, below 4 **0** | min **4** max **39**, below 4 **0** |
| fewer than 4 criteria | **44 of 986 = 4.46%** | **43 of 968 = 4.44%** |

**Residual** per cell {2: 0, 3: 1, 4: 17}, worst **17**, D1 bound **18**.
**Join** on rubric criterion texts: **968 of 968 exact**, 0 unmatched, 0 ambiguous (R468 reproduced).
**Unscored**: **18**, core sizes **{3: 1, 4: 17}**; `release − unscored` = **{2: 1, 3: 42, 4: 925}** =
the scored distribution **exactly**.
**Short-core mechanism**: empty **0** · whitespace-only **0** · duplicate-within-record **0** ·
criterion text length min **31** median **89** max **215**.

**`coval_core` clause-② standing**: all 968 prompts A2 **0.5665**, q **1.0000**, q_res **0.9978** ·
4-criterion-only 925 prompts A2 **0.5671**, q **1.0000**, q_res **0.9978**. ⚠ near-determined — R782
had already measured 0.9978.

**Controls.** OBJECT as above, exit 2 otherwise · CROSS-INSTRUMENT exact after the join · PLACEBO
identical recount · g=0 empty list counts 0, **0** empty cores · POSITIVE injected {0,1,4,39}
recovered exactly, broken character-counter returns {2,20,80,809} · DUPLICATES **0** ·
⛔ NEGATIVE and SHAM **declined in the preregistration** on D2 and D3. **WORLD A.**

## R784 · the population, measured

| set | n |
|---|---:|
| ranked (parsed human rankings) | **1078** |
| rubricked (`core_full.json`) | **968** |
| scored (this arc's population) | **968** |
| released conversations | **986** |
| **ranked WITHOUT a rubric** | **110 (10.20%)** |
| rubricked without rankings | 0 |
| dropped by the `>=2 rankings` rule | **0** |
| dropped by absence from the sat file | **0** |
| released but never scored | 18 (R783) |

**The 110 against the 968**, three estimators, 3 primary cells, **0 surviving**:

| axis | mean 968 | mean 110 | med 968 | med 110 | var ratio | rank | verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| rankings per prompt | 16.108 | 25.373 | 16.0 | 17.0 | 395.80 | +0.0526 | inside null |
| unacceptable flags | 4.163 | 10.109 | 0.0 | 0.0 | 82.99 | −0.0530 | inside null |
| flag rate per ranking | 0.341 | 0.290 | 0.0 | 0.0 | 0.99 | −0.0510 | inside null |

**MDE**: this design **0.2819 SD** · R783's proposed n=18 **0.6665 SD** · required n for 0.20 SD
**246**, 0.15 SD **545**, 0.10 SD **4,149**.

**Controls.** OBJECT 1078 = 968 + 110 exactly, exit 2 otherwise · PLACEBO **+0.000000** · g=0 200
random 110-subsets: rankings [−0.1063, +0.1074], flags [−0.0857, +0.0931], rate [−0.0980, +0.0859] ·
POSITIVE 0.00 inside · 0.25 inside · **0.50 RESOLVES** · 1.00 RESOLVES · NEGATIVE group-label
permutation (**valid here, unlike ledger 1125/1129**) rankings [−0.1271, +0.1150], flags [−0.0896,
+0.1029], rate [−0.0988, +0.0807] · CONFOUND flag rate reported beside the raw count. **WORLD C.**

## R785 · rubric affinity, measured

**Join** ranking→release: exact **968**, unmatched **0**, ambiguous **0** (R468, rebuilt in R783).

| object | tok | verbatim | affinity | null | own − null | MDE | |
|---|---:|---:|---:|---:|---:|---:|---|
| coval_core | 3 | 0.0668 | 0.4938 | 0.0836 | +0.4103 | 0.0139 | RESOLVES |
| gen | 3 | 0.0000 | 0.1410 | 0.1028 | +0.0382 | 0.0044 | RESOLVES |
| **core − gen** | 3 | | | | **+0.3535** | 0.0149 | **RESOLVES** |
| coval_core | 4 | 0.0668 | 0.4951 | 0.0555 | +0.4396 | 0.0145 | RESOLVES |
| gen | 4 | 0.0000 | 0.0865 | 0.0356 | +0.0508 | 0.0048 | RESOLVES |
| **core − gen** | 4 | | | | **+0.4090** | 0.0154 | **RESOLVES** |
| coval_core | 5 | 0.0668 | 0.5014 | 0.0465 | +0.4549 | 0.0147 | RESOLVES |
| gen | 5 | 0.0000 | 0.0867 | 0.0319 | +0.0549 | 0.0053 | RESOLVES |
| **core − gen** | 5 | | | | **+0.4150** | 0.0157 | **RESOLVES** |

**Containment**: cores entirely inside their rubric **1 of 986**; records with zero verbatim overlap
**792 of 986**.

**The pair** (n = 2, no correlation computed): coval_core affinity **0.4951**, q_resolved **0.9978** ·
gen affinity **0.0865**, q_resolved **0.0396**.

**Controls.** OBJECT join exact, exit 2 otherwise · PLACEBO **1.000000** · NULL **+0.4396**
[+0.4293, +0.4499], MDE 0.0145, 986 of 986 · NULL-TOPIC **+0.4013**, MDE 0.0363, n=150 · POSITIVE
delete 0% → **1.0000**, 25% → 0.7536, 50% → 0.4992, 75% → 0.2523, monotone · SWEEP {3,4,5} ·
⛔ SHAM not built (the ingredient's removal IS the null). **WORLD A.**
**Release data quality**: **3 of 19,147** criteria tokenise to nothing — `'Lwa'`, a bare UUID, an
empty string.

## R786 · the affinity axis, enumerated

**Arms with criterion text: 89** (counted in code). **Rubric-derived (verbatim ≥ 0.5): 79.**
**Not rubric-derived: 10.**

| arm | verbatim | aff@3 | aff@4 | aff@5 | null@4 | A2 | q_res |
|---|---:|---:|---:|---:|---:|---:|---:|
| coval_core | 0.0670 | 0.4944 | **0.4954** | 0.5018 | 0.0552 | 0.5665 | 0.9978 |
| promptecho | 0.0006 | 0.1479 | 0.1401 | 0.1478 | 0.0359 | — | — |
| gen | 0.0000 | 0.1410 | 0.0865 | 0.0867 | 0.0357 | 0.5352 | 0.0396 |
| topw_k4_sham | 0.0000 | 0.0905 | 0.0564 | 0.0471 | 0.0562 | 0.4909 | 0.0000 |
| full_sham | 0.0000 | 0.0885 | 0.0561 | 0.0465 | 0.0579 | — | — |
| coval_core_sham | 0.0000 | 0.0836 | 0.0550 | 0.0459 | 0.0558 | 0.4956 | 0.0000 |
| gen_sham | 0.0000 | 0.1028 | 0.0356 | 0.0319 | 0.0360 | 0.4828 | 0.0000 |
| promptecho_sham | 0.0000 | 0.0595 | 0.0352 | 0.0214 | 0.0353 | — | — |
| genericpool16 | 0.0000 | 0.1094 | 0.0316 | 0.0265 | 0.0316 | — | — |
| **generic** | 0.0000 | 0.1212 | **0.0249** | 0.0243 | **0.0249** | 0.5514 | **0.7780** |

**Correlation** affinity vs q_resolved: with shams n=6, r **+0.7678 / +0.6907 / +0.6993** ·
sham-free n=3, r **+0.6421 / +0.5841 / +0.5841**. **D3 MDE** n=5 **0.963** · 6 **0.924** · 7 **0.886**
· 8 **0.849** · 10 **0.785**, printed before any r. **All inside.**
**A2-CHECK**: corr(affinity, A2) **+0.6391** with shams, **+0.7878** sham-free ·
**corr(A2, q_resolved) +0.8747** with shams, **+0.9601** sham-free.

**Arms with text but no q_resolved**, listed: full_sham, genericpool16, promptecho, promptecho_sham.

**Controls.** OBJECT enumeration computed in code, exit 2 otherwise · PLACEBO **1.000000** · POSITIVE
rubric-derived arms return **1.0** exactly (D1, a derivation used as an instrument check) · NULL
per-arm cross-conversation · SHAM-SPLIT both populations printed · A2-CHECK the registered confound ·
SWEEP {3,4,5} · MDE printed FIRST. **WORLD C — underpowered, as D3 predicted.**

## R787 · q against A2

**Identity** `sign(mean(v − REF)) == sign(A2_arm − A2_ref)`: **0 disagreements of 47,320 pairs**
(26 arms × 1,820 references).

| | distinct values, 26 arms |
|---|---:|
| A2 | **19** |
| q | **4** |
| q_resolved | **6** |

**Kendall tau(A2, q)** +1.0000, 197 concordant, **0 discordant** ·
**tau(A2, q_resolved)** +1.0000, 240 concordant, **0 discordant**. ⚠ the first is a DERIVATION.

**The class**: reference A2 min **0.514375**, max **0.557475**, range **0.043100** ·
p0 0.5144 · p5 0.5242 · p25 0.5329 · p50 0.5391 · p75 0.5446 · p95 0.5511 · p100 0.5575.
**Baseline-conditional ⇔ A2 ∈ [0.5144, 0.5575]** → `generic` 0.5514, `gen` 0.5352.

**SHAM (class removed, ONE reference at A2 0.5504)**: agrees with `q > 0.5` on **26 of 26** arms.

**E4, the variance term** (two synthetic arms, identical A2): ratio 1.0 → 0.9835 / 0.9835 no
inversion · **1.5 → 0.9819 / 0.9835 INVERTS** · 2.0 → 0.9731 / 0.9835 · 4.0 → 0.8385 / 0.9835 ·
8.0 → 0.1714 / 0.9835. Real arms' per-reference sd **[0.0711, 0.1744]**, ratio **2.453** —
**inversion is inside the observed range**.

**Controls.** OBJECT 1820 rebuilt, exit 2 otherwise · PLACEBO **0.000000** · PLACEBO-2 a class member
returns q **0.726923** = its own A2 rank **0.726923** · POSITIVE `gen` swept 0 → **0.3308**, +0.02 →
**0.9923**, +0.05 → **1.0000**, +0.30 → **1.0000**, all matching the independent percentile to 1e-12,
band **admissible** · ⛔ NEGATIVE not built (D1 makes a permutation void). **WORLD B.**

## R788 · membership, the exclusion rule, and the variance advantage

**`generic` IS a class member**: `core_generic.json` = pool indices **[0, 1, 2, 3]** = reference
**#0** of the C(16,4) = 1,820.

| exclusion rule | references excluded for `generic` |
|---|---:|
| satisfaction-based (R781/R782) | **0** |
| criterion-based (the right unit) | **1** (reference #0) |

**POSITIVE**: jitter 0 → satisfaction rule catches **1**; 0.001 → **0**; observed 0.005638 → **0**;
criterion rule catches **1** at every level.

| | q | q_resolved |
|---|---:|---:|
| published (R782) | 0.9538 | 0.7780 |
| recomputed | 0.9538 | 0.7780 |
| self-reference #0 removed | 0.9538 | 0.7784 (**+0.000428**, D1 bound 0.000549) |
| **sd scaled to `gen`'s (1.871×)** | — | **0.5429 (−0.2352)** |

**CONFOUND (it won)**: `generic` blind AND member, k=4, sd **0.0711** · `genericpool16` blind, NOT a
member, k=16, sd **0.0635** — ratio **0.893**. **Blindness, not membership.**

**sd(v − REF) by arm class**: blind **0.0635–0.0711** · prompt-specific **0.123–0.174** · no arm
crosses the gap.

**Controls.** OBJECT membership verified, exit 2 otherwise · E1 decomposition worst mismatch
**2.082e-17** · PLACEBO **0.000000** · POSITIVE band computed at both ends · COUNTERFACTUAL labelled a
construction. **WORLD C.**

## R789 · what the A2 axis can resolve, and why a scalar cut is not a free simplification

**The question.** R788's NEXT proposed replacing `q_resolved` with A2 against a stated cut. A cut is
only as good as its axis, so this round prices the axis: how many levels does A2 resolve, and is the
released core resolvedly above the prompt-blind baseline?

**Derived before measuring.** D1 the admitted set `{arm : A2 > c}` changes at each distinct A2 value,
so ℝ gives (#distinct)+1 admitted sets — algebra, not a finding. D2 a cut's plateau IS the gap it
sits in, and a gap below its pair's MDE is not a distinction. D3 `var(a−b)=var(a)+var(b)−2cov(a,b)`,
so the paired MDE cannot be predicted from marginals and the pairing must be destroyed to be priced.
D4 #levels ≤ #distinct A2, so the measurement is where in [1, 20] it lands.

**The ladder, over the whole grid.**

| rule | `t` | adjacent | greedy |
|---|---|---:|---:|
| point | 0 | 20 | 20 |
| ci_only | 1.959964 | 10 | 11 |
| **strict / mde** (pre-registered, the rule `corebench/report.py` implements) | **2.801585** | **9** | **10** |
| conservative | 4.761549 | 5 | 7 |

**The levels** (strict, adjacent; emitted by `run.py`, not derived in prose): ① 9 floor arms
0.4828–0.5040 · ② `gen`, `genericpool16` 0.5352–0.5422 · ③ `generic`, `generic_reprov` 0.5514 ·
④ **`topw_k4`, `_detA`, `_detB`, `coval_core` 0.5642–0.5665** · ⑤ `indep_k4_fit1` 0.5941 ·
⑥ `indep_k4_indep_kA/kB` 0.6031 · ⑦ `greedy_k4_fit1`, `oracle_k4_fit1` 0.6106–0.6142 ·
⑧ `greedy_k4_greedy_kA/kB` 0.6226 · ⑨ `oracle_k4`, `_kA`, `_kB` 0.6283.

**The decisive pairs.**

| pair | eff | CI | MDE | `t` | verdict |
|---|---|---|---|---|---|
| `coval_core` − `generic` | **+0.01512** | [+0.00746, +0.02283] | 0.01069 | 3.96 | **BEATS** |
| `coval_core` − `gen` | +0.03130 | [+0.02314, +0.04002] | 0.01223 | 7.17 | BEATS |
| `generic` − `gen` | +0.01618 | [+0.00816, +0.02470] | 0.01185 | 3.82 | BEATS |
| `coval_core` − `genericpool16` | +0.02424 | [+0.01649, +0.03183] | 0.01081 | 6.29 | BEATS |
| `generic` − `genericpool16` | +0.00912 | [+0.00570, +0.01278] | 0.00489 | 5.23 | BEATS |
| **`coval_core` − `topw_k4`** | +0.002297 | [−0.00378, +0.00844] | 0.00853 | 0.75 | **UNRESOLVED** |

**SHAM (the second arm removed) versus NEUTRAL (a non-arm vector).** Scalar cut **0.539126**, median
reference **#1151** of 1,820.

| arm | vs the SCALAR cut | vs the median reference's VECTOR |
|---|---|---|
| `coval_core` | +0.02735 · mde 0.01351 · BEATS | +0.02735 · mde 0.01088 · BEATS |
| **`generic`** | +0.01223 · mde 0.01351 · **BELOW RESOLUTION** | +0.01223 · mde **0.00591** · **BEATS** |
| `gen` | −0.00395 · mde 0.01516 · UNRESOLVED | −0.00396 · mde 0.01214 · UNRESOLVED |

Population-wide: **23 of 27** resolve against the scalar, **25 of 27** against the vector; mean sd
**0.15333** versus **0.13103**.

**Controls.** OBJECT 27 arms · 968 prompts · annotators median 16, max 46 · **0** A2 mismatches
against R782 beyond 1e-9, exit 2 otherwise · PLACEBO eff 0.000000, CI [0,0], UNRESOLVED · POSITIVE
δ=0 UNRESOLVED (the floor fails, as required) → 0.01 BELOW RESOLUTION → 0.02 BEATS → 0.05 BEATS,
empirical MDE **0.01331**; the constant plant resolves at every δ>0 because its sd is 0 and it is
labelled degenerate in the docstring before the run · NEGATIVE pairing destroyed → MDE ×**1.529**
median, ×1.795 mean over 342 non-degenerate pairs, 9 duplicates excluded, synthetic independent arms
×1.036 · SHAM and NEUTRAL as above · NOISE FLOOR annotator split-half **0.003416**, and it is a
MARGINAL quantity that may not be compared to paired gaps.

**Multiplicity.** 351 cells tested · 305 survive the verdict rule · 46 do not (39 UNRESOLVED, of
which 9 are byte-identical duplicates; 7 BELOW RESOLUTION) · 311 survive BH at q=0.05 with no MDE
floor. **WORLD A.**

## R790 · whether a LEVEL can carry a definition, and why the answer is no

**The question.** R789's NEXT proposed rewriting clause ② as a membership claim. Membership needs
levels to be objects; this round asks whether they are.

**Derived before measuring.** D1 a non-transitive relation induces no partition, so the two
constructions are FORCED. D2 the sort key is an estimate, so the partition is rebuilt end-to-end in
every draw and never by re-thresholding a fixed order. D3 `t = |Δ|√P/sd`, so a rule change is a pure
rescaling — every difference between the four rules is threshold placement alone. D4 the 9 alias
pairs must return P = 1.000 exactly, which is this round's placebo with a known expected value.

**E1 · the relation is not an equivalence relation.**

| rule | intransitive chains | of | rate |
|---|---:|---:|---:|
| point | 0 | 0 | — |
| ci_only | 23 | 146 | 15.8% |
| strict / mde | 16 | 202 | 7.9% |
| conservative | 16 | 253 | 6.3% |

**E2/E3 · the bootstrap, B = 1,000.** Level count (adjacent) 7:0.084 · 8:0.359 · **9:0.408** ·
10:0.138 · 11:0.011. Greedy 8:0.022 · 9:0.209 · **10:0.560** · 11:0.192 · 12:0.017.

| pair | P(same level) adjacent | greedy |
|---|---:|---:|
| **`coval_core` ~ `generic`** | **0.339** | **0.132** |
| `coval_core` ~ `topw_k4` | **0.975** | 0.758 |
| `generic` ~ `gen` | 0.045 | 0.094 |
| `coval_core` ~ `gen` | 0.004 | <0.001 |
| `coval_core` ~ `genericpool16` | 0.005 | <0.001 |
| `coval_core` ~ `indep_k4_fit1` | <0.001 | <0.001 |

**The specification curve** (3 seeds per cell, all twelve published): `P(core ~ generic)` = 0.000
(point) · 0.065–0.090 (ci_only) · 0.310–0.339 (strict) · 0.920–0.955 (conservative).

**E4 · the formulation.** `generic` in level **3 of 9**; admits 8 classes = **14 named arms**;
excludes 12 classes = **13**; the same admitted set in **0.640** of 300 resamples.

**Controls.** OBJECT 20 distinct objects from 27 named arms, worst `t` delta against R789
**1.066e-14**, exit 2 otherwise · PLACEBO the 9 alias pairs at exactly **1.000** · POSITIVE δ sweep
0.990 → 0.955 → 0.755 → 0.110 → **0.000**, band admissible; ⛔ **the pre-registered criterion
`floor == 1.000` FAILED at 0.990 and was itself mis-specified** — at δ=0 the plant adds zero-mean
noise, so the rule fires at `α = 0.005085` and `P(floor == 1) = 0.361` over 200 draws, a **64%
false-failure rate by construction**; repaired against its own binomial null, |−0.00491| ≤ 0.01509,
PASS · NEGATIVE synthetic matched-spread arms mode **5** against the real **9**, so World C does not
fire · SHAM equal-width binning at the same level count, adjusted Rand **0.7798**.

**Multiplicity.** 190 unordered pairs among 20 objects — not 351; the 9 alias pairs are the placebo.
Bootstrap resolution 1/1000, so 0 is reported as `< 0.001`. **WORLD B.**
