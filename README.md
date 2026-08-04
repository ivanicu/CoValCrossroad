# CoVal Crossroads

An independent audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a
dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to
contentious prompts, *and wrote down the criteria they judged by*.

**343 rounds** in **5 epochs** and **24 arcs**, numbered to **R348** — **53 standing claims, 13
withdrawn**, and **46 defect checks on the release, 16 of them clean.** (**337 of the 343 carry a
non-smoke result**, and the six that do not are named by
[`every_round_reaches_the_readme.py`](assurance/every_round_reaches_the_readme.py) on every run —
which is why this line is recounted from the gate rather than incremented by hand.)

⚠ **The claim count has a narrower population than the round count, and adding them would mislead.**
Both consolidators below re-derive on every run and were re-run at R340: the ledger reports
**53 standing / 13 withdrawn of 66**, and the defect list **46 checks — 6 blocking, 16 serious,
8 noted, 16 checked-clean**. But **the claim graph's evidence spans `r123–r200`**. The fourteen
rounds that took the definition apart (**R327–R340**, below) are *not claims in that graph at all* —
they are recorded in their own round directories and summarised here, and nothing has promoted them
to ledger claims.

The release ships prompts, four responses per prompt, crowd-written rubrics and 18,384 rankings —
but **not** the criterion-by-response satisfaction labels, so its own scoring cannot be reproduced
from it. This repository rebuilds that layer locally and then asks what the rubric measures.

---

## The short version

**The apparatus works better than its critics would guess and worse than its numbers suggest.**

| question | answer |
|---|---|
| Does the crowd's rubric beat a dumb heuristic? | **Yes, clearly.** It picks the human top choice 50.3% of assessments against 37.3% for "pick the longest response" — +13.0 points, stable across weighting and outlier removal. |
| Is that good? | It closes **66–67%** of the reachable band. The ceiling is not 100%: two humans on the same prompt pick the same best response only **47.8%** of the time. |
| Do the criteria say what people value? | **Partly.** They are also descriptions of the answer their author had already chosen — authoring happens *after* ranking, and the effect is +0.0478 on a same-texts comparison. |
| Does compilation fix that? | **No.** The distillation into `coval_core` passes it through unchanged (+0.013, z 1.0, adequately powered). |
| Does compilation cost anything? | **Yes.** It gives back ~40% of the fairness the full rubric had gained over the panel's own plurality vote. |
| Is the "unacceptable" flag trustworthy? | **It is the most reliable channel here** — raters agree on *which* response is unacceptable at Spearman-Brown **+0.827**. |
| Do demographic groups have different values? | **Barely.** 2 of 28 demographic levels cluster above chance, both countries, at ~+4.5% — against +73.7% for a planted bloc. |
| Can anyone compile a *better* core than the official one? | **Nobody wins every axis.** Eight compilers, seven axes, five judges ([r220](E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost/R220_compiler_tournament)): the official core beats all 20 size-matched random draws on every judge, and our own decision-fitted core beats it **only on the judge it was fitted with** (+0.025 there, −0.008 and −0.003 on the two held-out judges). |
| Can a compiler be caught selecting predictors instead of values? | **The question has no resolution here.** On **100%** of prompts *some single criterion alone reproduces the whole 4-response ranking*, with a median of **3** tied at that perfect score ([R221](E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost/R221_contamination)). A planted perfect predictor is indistinguishable from the real ones. `log₂(4!) = 4.6` bits cannot rank 15 criteria. |
| Is a "core" even identifiable from this release? | **The class always; the member never.** `log₂\|H(Q)\| ≤ H_eff` — and the class is identifiable *by construction* because `Q`'s classes are defined by the observation (13 classes per prompt, 3.70 bits against 6.23 available). The largest identifiable **member** core is `k ≤ 2`; the official core prints **4** ([R224](E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/R224_the_identifiability_bound), [R228](E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/R228_the_largest_core_this_release_can_carry), [R230](E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/R230_the_class_not_the_member)). |
| Would asking a *finer* question help? | **No — at real human noise.** A 10-point score beats a ranking by **+0.56** at zero noise and **+0.012** at the noise level calibrated to this release's own 47.8% two-rater agreement, inside a spread of 0.030. **Precision does not close the gap; independence does** ([R227](E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/R227_two_currencies)). |
| Then why is it unidentifiable? | **The per-prompt factoring, not the data volume.** Within a prompt the bits do not add; across 986 prompts they do — **[1006, 3402]**. A *global* core of `k ≤ 119` is identifiable where a per-prompt core of **2** is not, and CoVal ships the per-prompt object ([R239](E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/R239_global_vs_per_prompt), a **derivation**). Whether such a core *exists* is being measured. |
| Does the arc meet its own standard? | **80.9% declared, and 19.4% of what is declared has no evidence behind it.** The committed figure was **46.9%** over **23** rounds; the same code re-run over today's **124** covers 1405 of 1736 cells. Declaration nearly doubled — and the declared-but-not-evidenced rate went the other way, **3.9% → 19.4%**, so the arc declares far more and evidences a smaller share of it ([R242](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R242_self_audit)). The old number was never wrong for its stated population; it had simply stopped describing the arc, and nothing in the suite could tell. |
| Which of the compiler's operations costs what? | **Not equally, and one pays for itself.** All 2⁵ combinations, exact Shapley ([R222](E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost/R222_factorial)): **truncation** is the expensive one for prediction (−0.0164), **selection** for causal direction (−0.0615), **merge** is the only one that destroys provenance (−0.0227) and buys 0.33 of a rule — and **rewriting negatives into positive form more than halves the rubric's dependence on which judge scores it** (gauge −0.1240 → −0.0571). |
| Does the rewrite make criteria easier to judge? | **No — my own reading of R222 is refuted.** The rewritten text is if anything *more* instrument-dependent (Δgauge **+0.0063**, controls valid: verbatim pairs 0.0191 apart, shuffled-lineage null flat at −0.0035 across 5 seeds). The gain is the **selection it reorders**: normalising polarity promotes criteria that are individually stabler (0.6491 → **0.6385**) ([R223](E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost/R223_the_textual_half)). |
| Is the negative-to-positive rewrite a loss? | **It is decision-null by derivation.** `−w(1−s) = −w + w·s` — the original term plus a response-independent constant, so no `argmax`, pair or ranking moves. Measured identical to six decimals. Its whole effect is on the *text*, and on *which* criteria selection then keeps: +0.0000 applied alone, **+0.0041** applied on top of select+truncate. |
| What does compression actually cost? | **Not what any of the arms assumed.** Keeping every criterion and reducing each weight to **one bit** loses ~0.005 of ranking accuracy and inverts **0%** of source interventions; keeping 4 criteria with exact weights inverts **10.3–22.7%**. The expensive thing to drop is the criteria, not the numbers. |

---

## Where the definition of a "core" stands (R327–R347)

⛔ **Clause ① has never excluded anything clause ② admits.** Over all **41** judged arms the cell
(① fails, ② passes) is **empty**; ② excludes **8** that ① admits. The mechanism: the clause-② reference scores **0.5462**
against **0.4922** for a random draw from *this prompt's own rubric* — **+0.0540, minimum +0.0470,
never negative** — and that is what makes ② the binding clause. ⚠ **But it is CURATION, not
blindness** (R348): that reference draws from a pool of **16 criteria authored for the benchmark**,
and crowd criteria applied to the *wrong* conversation are **0 of 5 resolvably better and 2
resolvably worse**. The earlier reading — *"a criterion set that never reads the conversation beats a
random draw of that conversation's own criteria"* — is **retracted**; it was true of the curated pool
and false as stated.
→ [`R348`](E05_the_space_of_compilers/A24_what_the_definition_costs/R348_is_it_blindness_or_curation)

⛔ **And neither clause's wording describes what it computes.** Clause ① says *"drawn at random from
that conversation's own rubric"* and the census uses **one fixed k=4 draw, seed 0, for every arm** —
not size-matched for 23 of 41, not re-drawn, while the correct per-k references sit unused on disk.
Clause ② says *"the same number that never read the conversation at all"* and computes **the first k
rows of a curated 16-criterion pool** — a subset chosen by **file order**, sitting at the **63rd
percentile** between a random draw and the best of 1,820. Since clause ② is the binding one, the
whole admitted set rests on that slice, and the set moves **7 → 0** across ~0.019 of reference level.
**Two repairs are possible — narrow the wording, or broaden the implementation — and choosing is a
decision, not a measurement.** Neither is taken here; what decides it is permuting the pool and
recounting, which turns *63rd percentile* into a distribution over admitted sets. **The empty cell is a DERIVATION**: a counterexample needs `GAP < SLACK`
(`GAP = ref₂ − ref₁`, `SLACK = mde₁ − mde₂`), and **min GAP 0.0470 vs max SLACK 0.01217 — 3.9× on
the tightest arm, GAP ≥ SLACK on all 41.** No arm of any size here can be one. *(This round's first
version used a sufficient condition instead of the necessary one, called 18 arms "contingent" and
said a counterexample was constructible; it is not.)* Permuting the pairing fills the cell
(6, 5, 6 over three seeds), so the emptiness is about which arm carries which margin. Clause ① stays — the implication rests on a
measured reference gap rather than on the definition's logic, and another release could break it —
but the definition must stop reading as though both clauses contribute an exclusion.
→ [`R347`](E05_the_space_of_compilers/A24_what_the_definition_costs/R347_does_clause_one_ever_bind)



Fourteen rounds took the definition apart clause by clause. **Every clause now carries its own
measured limit**, and two of the three limits are bounds rather than values.

**Clause ① — *better than the same number drawn at random from that conversation's own rubric*.**
Closes **structurally**, and not because its margins are large. Its reference class is
**quality-degenerate**: members are per-prompt random draws, so they are exchangeable and there is no
percentile for a reference to sit at. Measured, across-member sd over sampling error, **τ/se = 0.72
against exchangeability's predicted 1/√2 = 0.707**; closure rate **0.0000**.
→ `R334_why_clause_one_closes`

**Clause ② — *better than the same number that never read the conversation at all*.** Named a class
and **no member** for forty rounds. Its reference is now a **procedure**: the *lowest closed level*
of the size-matched blind class, where closed means no prompt-blind set of the same size is
resolvably better. Measured over **all 1,820** quadruples: a random reference admits **23.3%** of the
blind class, the reference this project had been publishing admits **3 of 1,820**, and closure admits
**0**. *Budget-matching — the obvious alternative — admits the baseline itself at all five readings
tested, and is out.*
→ `R327_clause2_names_no_reference` · `R328_the_three_readings_are_one_budget` ·
`R329_the_budget_is_unobservable` · `R330_what_the_conservative_reading_costs` ·
`R331_what_makes_a_clause2_reference_safe` · `R332_the_closure_level_derives_reading_A`

**Clause ③ — *built without any human label for the conversation it describes*.** A source-reading,
and its **testability** is now bounded from both sides. Detection through **performance** is refuted:
the leak slope correlates with arm quality at **r = +0.934**, and quality-adjusted the maximally
leaky arm sits **3.25 sd below** what its quality predicts. Detection through **selection** works for
the release's one annotated rule family — held-out-arm **AUC 0.866** — and reaches **chance (0.510)**
on a second mechanism, which the same features cannot see even trained on it (0.565).
→ `R335_can_provenance_be_detected` · `R336_clause_three_tested_not_declared` ·
`R337_the_wall_is_the_population` · `R338_does_the_signature_transfer_to_a_new_rule`

### ⛔ What the admitted set actually is

**Not a list.** Cluster-bootstrapped over prompts, the five-arm set this project publishes recurs in
**53.4%** of resamples across **30 distinct sets**. Per-arm inclusion probability: `topw_k6` 0.995 ·
`topw_k3` 0.943 · `coval_core` 0.919 · `topw_k8` 0.882 · **`topw_k4` 0.763** — and two arms excluded
at the point estimate, `topw_k2` at **0.130** and `generic` at **0.051**. **Clause ② carries 100% of
that uncertainty**: `P(clause ①) = 1.000` for every arm with any clause-② mass.
→ `R339_the_conjunction_is_a_different_object`

### ⛔ And it cannot be sharpened here

`MDE(N,m) = Z·√(σ_b² + σ_w²/m)/√N` with **σ_b = 0.1077, σ_w = 0.1777**. The annotator axis is
**spent** — at the release's median of 16 the MDE sits at **1.08× its m→∞ floor**, so infinite
annotation buys **7.6%**. Reaching the band needs **~12,500 prompts, 12.9× this release.**
**Deciding which arms clause ② admits is not achievable by re-analysis.**
→ `R333_the_resolution_floor`

### ✅ It survives a deliberate adversary

Three **label-free** arms built to satisfy the definition rather than to be cores — imitate the full
rubric, maximise verdict confidence, maximise disagreement with the blind reference — are **all
rejected**, at clause-② ratios of −3.42×, −3.04× and **−8.39×**. The objective aimed most directly at
clause ②'s numerator produces the **worst** arm on the page (A2 **0.3601**, below the 0.4927 random
floor), because disagreeing with the blind reference means disagreeing with the humans too. An
**oracle** allowed to read labels *is* admitted (11.79× / 9.33×), so the search budget was
sufficient and those three rejections are measurements rather than silence. *At 300 candidate
subsets per prompt; a larger budget can only help the adversary.*
→ `R340_the_definition_against_an_adversary`

---

## What was established

Every number below states its unit, because five of seven headline figures in this project were
published without one. The check that found that is [`HEADLINES.py`](assurance/HEADLINES.py) and it re-runs.

### The pipeline

| finding | number | round |
|---|---|---|
| Crowd rubric vs. length heuristic | **+13.0 pts** [+10.3, +15.8] · 50.3% of assessments vs 37.3% | [r178](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R178_rubric_versus_length) |
| …how much of that is the *weights* | **+14.6 pts**; shuffling them drops the rubric to the length heuristic's level | [r178](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R178_rubric_versus_length) |
| …how much is circular (rater's own ratings) | **+0.6 pts** — leave-one-annotator-out barely moves it | [r178](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R178_rubric_versus_length) |
| The reachable ceiling | **61.5–62.3%** of assessments (leave-one-out modal human choice) | [r179](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R179_against_the_ceiling) |
| Human–human agreement | **47.8%** of prompts, chance 25% | [r179](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R179_against_the_ceiling) |
| Reconstructed satisfaction layer | **0.686** pairwise concordance, 80,542 pairs | [r04](E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction) |

### The compilation step

| finding | number | round |
|---|---|---|
| The positive-weight rewrite is real and targeted | 82.5% of negative-weight sources flip polarity vs 6.1% of positive · z +33 | [r176](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R176_nonconflicting_nonredundant) |
| …but it loses the individual criterion | flipped items correlate **−0.14** with their source; unflipped **+0.81** | [r189](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R189_does_the_rewrite_preserve_direction) |
| Compilation gives back fairness | **+4.2 pts** of group disadvantage returns, full → core · z +3.3, 851 strata | [r146](E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_the_standard/R146_does_compilation_add) |
| …and the full rubric was *fairer* than the plurality | 5.5 pts vs 15.6 pts | [r146](E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_the_standard/R146_does_compilation_add) |

### The criteria themselves

| finding | number | round |
|---|---|---|
| Criteria encode their author's prior choice | **+0.0478** [+0.0336, +0.0620], 4,504 author pairs, same two texts | [r187](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R187_post_hoc_rationalisation) |
| Compilation neither concentrates nor removes it | +0.013, z 1.0 · MDE 0.037 = 76% of the incoming effect | [r188](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R188_does_compilation_keep_the_rationalisations), [r204](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R204_the_nulls_need_power_not_jackknives) |
| The card's "highly rated" claim | **fails** as stated; selection is rating-*sensitive*, not rating-*ordered* (3.0→10.1% survival across weight bands) | [r171](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R171_card_vs_artefact), [r181](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R181_whose_criteria_survive) |
| "non-redundant" / "non-conflicting" | **UNVERIFIED** — a style confound of the same magnitude blocks the first; the proxy is blind to the second | [r176](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R176_nonconflicting_nonredundant) |

### The people

| finding | number | round |
|---|---|---|
| Dissent is a stable individual trait | split-half **+0.486**, survives residualising on prompt assignment | [r180](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R180_is_the_disagreement_a_person) |
| Demographic groups that actually cluster | **2 of 28** levels — Netherlands +6.3%, Mexico +6.0% | [r183](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R183_does_any_attribute_mark_a_bloc) |
| …and what they cluster *about* | **nothing measurable** — 0 of 14 axis tests survive | [r186](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R186_what_do_the_blocs_want) |
| The veto identifies content, not raters | S-B **+0.827** on *which* response, over 1,288 pairs | [r192](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R192_is_the_veto_about_the_responses) |
| What gets flagged as unacceptable | the response that **hedges less** — z −5.6, and it is not length | [r193](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R193_what_gets_flagged) |

---

## What the release does not ship

Six things, each of which blocks a question someone will want to ask.

| missing | consequence |
|---|---|
| criterion→response satisfaction labels | the published scoring cannot be reproduced; this repo rebuilds it with a local judge |
| lineage from a core criterion to its source | "did this criterion survive compilation" is a text-similarity guess (7.8% verbatim, 30.8% at 0.80) |
| authorship for multiply-rated criteria | 36% of the pool cannot be attributed, so "what people wrote" is 36% not what people wrote |
| where the four candidate responses came from | nothing supports a claim about model behaviour — only about these 4,312 texts |
| four documented demographic fields | race/ethnicity, country of origin, employment, self-description — collected per the card, never shipped, and the sanitization section does not mention it |
| any refusal in the response set | **5 of 4,312** candidates decline. The most contested question in alignment was never put to the panel. |

Full list, ordered by the concrete wrong answer each produces:
[`DEFECTS.py`](assurance/DEFECTS.py) — **6 blocking, 16 serious, 8 noted, 16 clean.**

---

## What this project got wrong

**13 withdrawn claims.** [`RETRACTIONS.md`](RETRACTIONS.md) has all 235 entries, each naming what killed it — the claim graph refuses a
retraction that names no killer.

The failure mode changed halfway. Early phases retracted **measurements**. From r175 on, the sweep
turned on its own output and retracted **descriptions of measurements that were correct**:

- *"the panel is concentrated in a few countries"* — 63% in three countries is right; the release
  publishes no sampling frame, so there is nothing to be concentrated *relative to*
- *"the scale is used as a near-binary"* — all 21 values are used, 4.04 bits of a possible 4.39
- *"length matters less on prompts with a right answer"* — **one prompt, counted 929 times**,
  produced the entire +4.9 points. Removing it collapses the effect tenfold.

That last one is entry 230, and it caused entry 231: a **retraction of a retraction**, where the
verdict was right and the stated mechanism was false.

**Two tools exist because of it.** [`covalx/estimand.py`](covalx/estimand.py) refuses a mean over
grouped data until the caller says whether the unit is the observation or the group.
[`covalx/robust.py`](covalx/robust.py) is a calibrated jackknife whose verdict is three-valued,
because its own threshold turned out to be a distribution. Both failed their first attack; both
attacks are in the repo.

**And the gates get it wrong too.** `point estimate inside its own interval` is the most
unarguable check in this repo — it needs no knowledge of the estimand and the guard's own ledger
calls the implication **sound**. It is not sound for one named class: a **ratio estimator summarised
by its bootstrap mean**. R235 publishes `eta = mean(d_core/gap)` beside a percentile interval over
the same bootstrap array; when the denominator approaches zero the replicates are Cauchy-like and
the mean sits outside its own central 95% with nothing wrong — **13 distinct cells do, up to
offcentre 2.48**. The gate has never fired on them only because `eta` is not a name its regex
recognises. Also counted for the first time: **583 published intervals with `lo == hi`**, which the
`inverted` test misses because it compares strictly.
The same round retracts its predecessor's closing sentence — *"the largest unexamined population in
the repo"* was **one round and one key pair**, and the day of reading it proposed was not owed.
→ [`R341`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R341_is_the_skipped_population_real)

**And the exposure is a bound, because the reader is the limit.** Asking how many of the 389 checked
points are ratios needs the *source*, not the artifact — a published `0.0128` is a difference, a
ratio and a coefficient in the same JSON, so the quantity is unidentified from artifacts at any
sample size. An AST census of the 42 distinct keys returns **1 flagged, 28 clean, 13 unreadable**
(31%, above the pre-registered 25% ceiling) → **RATIO_DATA ∈ [1, 14]**, never a point. The one flag
divides by `max(count, 1)`, bounded below by one, and is adjudicated safe **by a source read rather
than by a new rule** — a rule added after seeing which case it clears is a threshold fitted to a
result. Four reader repairs, each forced by a planted control or a declared conservatism, **each
moved the count**; one was caught only because a pre-registered cross-instrument prediction
*disagreed* with the artifact side.
→ [`R342`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R342_how_many_checked_points_are_ratios)

**And the same shape sits under the whole suite.** Every artifact-side verdict here assumes the JSON
beside a `run.py` came from that `run.py`, and nothing tests it. Measured: **277 rounds edited to
compute a median instead of a mean, every artifact left byte-identical, and zero of 21 checks moved**
— not one exit code, not one report digest. A read census from an audit hook shows **7 of 21 open a
round's source at all**, and all seven read it for *structure*, never for provenance. The positive
control (one point moved outside its own CI) did move, so the zero is a measurement rather than
silence. **A stale artifact, a hand-edited artifact and an honest one are indistinguishable to this
suite.**
→ [`R343`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R343_does_any_check_tie_artifact_to_source)

**The record already existed; the reader never did.** [`covalx/stamp.py`](covalx/stamp.py) writes
`sha256` of a round's own source into its output, 22 rounds call it, and its docstring states the
failure verbatim — *"a round patched after it ran passes that gate forever while its persisted
numbers no longer exist in any output."* `grep -rl source_sha256` across `assurance/`, `covalx/` and
`db/` returns **one file: the definition itself.** Measured over 79 rounds carrying a stamp-like
key: **33 STALE, 14 FRESH, 32 UNVERIFIED** — of the stamps resolvable at all, **70% no longer match
the source beside them**, `R141_verification` among them. The UNVERIFIED bucket is load-bearing: a
key-name match said 38, a tight self-hash regex said 14, and both were wrong, because
`**stamp(__file__)` puts the hash in another file where no regex over the round's own text can see
it. A stamp detects **drift, never forgery** — whoever edits an artifact can write any hash into it.
→ [`R345`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R345_the_stamp_nobody_reads)

**And re-running IS affordable — but it does not say the numbers are right.** A stratified sample of
45 rounds, executed in an isolated copy: **41 complete inside 90 s (91%)**, 80% inside 30 s. Of the
40 with an artifact to compare, **30 regenerate it and 10 do not** — and `byte-identical` equals
`json-equal` at 30/40, so **not one of the ten differs merely in formatting; every difference is a
value.** Crossed against the stamp census: where a stamp exists it agreed with re-running (both
STALE rounds differ, the single FRESH one reproduces), but **a stamp exists for 3 of these 40 rounds
and 7 of the 10 failures carry none** — the drift check's sign is right and its coverage would have
caught 2 of 10. *Its isolation control failed on two earlier valid runs, both times because I was
committing while it measured; the third compares per path and returned 765 artifacts, 0 changed, 0
vanished.*
→ [`R344`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R344_what_fraction_can_be_rerun)

**The reader now exists** — [`assurance/source_stamp_is_current.py`](assurance/source_stamp_is_current.py),
three-valued, in the suite registry (**22/22** on an empty population). It is a **ratchet, not a
gate**: the 33 stale rounds are frozen in `KNOWN_STALE.json` so the debt cannot grow silently, and
the check *also* fails if a frozen entry becomes FRESH — so the list shrinks and cannot become the
kind of confession nobody re-reads. Attacked five ways before it was trusted: new drift on a fresh
round → caught; a frozen entry silently fixed → caught; the frozen list deleted → exit 2, not a
clean bill; every artifact removed → exit 2; the classifier neutered to always say FRESH → its own
planted control fails it. Regenerating the 33 is a cost question, not this check's decision.

---

## Where this is going

[`NORTH_STAR.md`](NORTH_STAR.md) — the research direction, stated as a **conservation law** rather
than a score: which normative distinctions may be compressed, which must be causally preserved, and
which become type errors when lost. It carries three claims that can die, and the observation that
kills each.

Its one sentence: *normative information is the set of source distinctions required to answer a
declared family of queries, and it is preserved when intervening on a distinction changes downstream
behaviour — not when the downstream object merely agrees with it.*

---

## Navigating

| epoch | the object it turned out to be studying | arcs | rounds |
|---|---|---|---|
| [`E01`](E01_the_rubric_was_the_object) | the rubric — until R011 showed the number belonged to the **judge** (+0.53 → +0.05 on an independent backbone) and R019 to the **floor** (27%–67%, span 2.47×) | 3 | R001–R022 |
| [`E02`](E02_the_plural_public_dissolved) | the plural public — until R023 showed agreement survives **with no blocs at all** under reliability heterogeneity (actor takes 47.2% of dyad variance) | 3 | R023–R045 |
| [`E03`](E03_the_instrument_was_the_object) | the instrument: judge, floors, direction-from-text, resampling unit, width. The judge tracks lexical overlap at **+0.21** | 5 | R046–R109 |
| [`E04`](E04_no_fraction_only_an_equivalence_class) | no fraction exists — normative information is `[N]_Q`. Self-dated: *"asking for that number is the error this project made for sixty rounds"* | 5 | R110–R219 |
| [`E05`](E05_the_space_of_compilers) | the space of compilers, not the released one — our own arms carrying no immunity. The formulation it arrived at is [`FORMULATION.md`](E05_the_space_of_compilers/FORMULATION.md) | 11 | R220– |

An **epoch** closes when the object under study turns out to be a different object; an **arc** when a
decision becomes safe; a **round** is one belief update. Each boundary is defended by a citable event
in [`EAR.md`](EAR.md), and [`PATHMAP.tsv`](PATHMAP.tsv) resolves any pre-2026-08-02 path.

**Three generated consolidators** — each re-derives from the data on every run, so a number in one
that disagrees with a round means the *round* is stale:

- [`DEFECTS.py`](assurance/DEFECTS.py) — every defect, by the wrong answer it produces
- [`HEADLINES.py`](assurance/HEADLINES.py) — every headline mean under both estimands
- [`db/ledger.py`](db/ledger.py) — the claim graph: standing, withdrawn, and every kill edge

---

## Reproducing

```bash
python -m venv .venv && .venv/bin/pip install numpy   # that is the whole dependency
.venv/bin/python DEFECTS.py        # the defect list
.venv/bin/python HEADLINES.py      # every headline, both units
.venv/bin/python E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R178_rubric_versus_length/run.py
```

Every round is a self-contained `run.py` writing `results/*.json`. Rounds that need the rebuilt
satisfaction tensor read `E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/`. The claim graph
needs PostgreSQL and `psql` on PATH; everything else needs only numpy.

---

## Boundaries

**Everything routing through the judge is a claim about that judge.** The satisfaction layer is a
locally rebuilt Qwen3.5-2B-Base reading `sigmoid(logit(" Yes") − logit(" No"))`. Where a comparison
holds the judge fixed on both arms — which is most of them — a judge bias cannot produce the
result. Where it does not, the claim says so.

**The prompts are synthetic and single-turn** (90.9%), median 128 characters. Whether anything here
transfers to production traffic is untested, and this project withdrew the claim that it does not.

**One prompt was rated by 929 people** against a median of 14, and its text is garbled. It carries
79% of all annotator pairs in the corpus. Any statistic averaged over assessments rather than
prompts is substantially a statement about that one prompt — which is how this project's one
fabricated finding happened.

**Nothing here is a claim about the people.** Group-level numbers compare a group to its
co-panelists on the same prompts; "unserved by the plurality" and "departs from the majority" are
the same event, so a group's apparent disadvantage is partly its own dissent rate.

---

## Attribution

CoVal is OpenAI's release: [dataset](https://huggingface.co/datasets/openai/coval). This audit is
independent and not affiliated with OpenAI. Errors here are mine, and 235 of them are written down.

*The previous README — a chronological research diary, 1,433 lines — is in git history:*
`git show 6a099d7f34:README.md`
