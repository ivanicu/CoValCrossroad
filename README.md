# CoVal Crossroads

An independent audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a
dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to
contentious prompts, *and wrote down the criteria they judged by*.

**415 rounds** in **5 epochs** and **24 arcs**, numbered to **R421** — **53 standing claims, 13
withdrawn**, and **46 defect checks on the release, 16 of them clean.** (**359 of the 365 carry a
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
rows of a curated 16-criterion pool** — a subset chosen by **file order**, sitting at the
**93.7th percentile of all 1,820 size-4 subsets** — rank 1707 of 1820, exhaustively enumerated
(median 0.5391, max 0.5575, published 0.5504). *This rank was already in `FORMULATION.md` for the
incumbent `generic` — the same subset at the same 0.5504 — so the enumeration VERIFIES it; what is
new is only the distribution's shape. It retracts a "63rd percentile" I had published into that same
file one cycle earlier.* Since clause ② is the binding one, the
whole admitted set rests on that slice, and the set moves **7 → 0** across ~0.019 of reference level.
**Two repairs are possible — narrow the wording, or broaden the implementation — and choosing is a
decision, not a measurement.** Neither is taken here; what decides it is permuting the pool and
recounting, which turns the reference's rank into a distribution over ADMITTED SETS. **The empty cell is a DERIVATION**: a counterexample needs `GAP < SLACK`
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

### Backfilled findings — the R384 debt, paid one round at a time

R384 measured that **243 of 377 rounds have no finding site at all**; R386 that a finding's numbers
are only **9%** recoverable from its artifact; R387 that the code still **runs**, so the debt is
payable by re-running and reading. These rows are that debt being paid. They are marked as backfill
rather than blended into the rows above, because a row written months after the round is a different
object from one written beside it — and pretending otherwise is the drift those rounds were about.

| finding | number | round |
|---|---|---|
| The "nearest-topic" donor is **nearly a same-question restatement**, so its failure to transfer is a strong result rather than a weak one | near-donor cosine **0.8804** vs random-pair **0.7495**; the near donor covers **91.4%** of the distance from random to a paraphrase of the same prompt, and sits at the **97.85th** percentile of all pairs · n = **300** prompts | [r21](E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R21_donor_distance) |
| …and the embedding was shown able to tell related from unrelated **before** any donor distance was read from it | prompt vs its own paraphrase **0.8927**, vs a random other prompt **0.7495**, separation **+0.1432** | [r21](E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R21_donor_distance) |
| Rationale length falls in a **REGIME STEP**, not a fatigue slope — and it survives being matched on the breakpoint search itself | step **R² = 0.9644** against a selection-matched null whose 95th percentile is **0.4055** (z **+7.09**); a straight line reaches only **0.4480**; level change **-38.6%** · n = **1012** at the first position | [r24](E02_the_plural_public_dissolved/A04_structured_plurality_or_reliability/R24_regime_receipt) |
| …and the mechanism is not fatigue, because effort **RISES inside every segment** | within-segment slope **+6.84** chars/task before the break and **+1.04** after — a monotone fatigue trend cannot produce that | [r24](E02_the_plural_public_dissolved/A04_structured_plurality_or_reliability/R24_regime_receipt) |
| The additive rater decomposition is **demonstrably misspecifiable** — and the multiplicative alternative is **NOT thereby established** | in sample multiplicative **0.6604** beats additive **0.5784** at equal effective df; out of sample the order **inverts**, additive **+0.3879** vs multiplicative **+0.2514**, and the multiplicative R² ranges **[-1.6442, +0.5109]** against the additive's tight **[+0.3377, +0.4208]** · **924** raters | [r28](E02_the_plural_public_dissolved/A04_structured_plurality_or_reliability/R28_multiplicative) |
| The reliability shortfall against 0.707 is a **TIE-HANDLING artifact**, not a property of the raters | the baseline reaches **0.6732** (**-0.0338**); counting tied pairs as 0.5 reaches **0.7040** (**-0.0030**) — the only arm landing within 0.01 of the target — while dropping ties gives **0.6745** and raising the rater floor to 12 gives **0.6933** on **784** prompts. Split-half **0.6667** → **0.6978** across the same swap | [r101](E03_the_instrument_was_the_object/A11_how_wide_every_interval_really_is/R101_reliability_offset) |
| The "correlation across 7 arm pairs" is **one parameter with 4 df**, not seven observations | one shared shrink **λ = 0.4521** (se **0.0287**) fits all five arms: χ² **3.26** on 4 df, **p = 0.5152** against a pre-registered critical **9.4877**, largest per-arm **\|z\| = 1.59**. The algebraic equivalence holds to **1.11e-16**. **POWER stated because a test that cannot refuse is not a test**: refusing constancy needs the spread **1.71×** wider — and the same λ's quoted *without* their errors span **72.0%** of the smallest, which is the form in which I first mistook them for a refutation | [r115](E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/R115_shrink_is_one_parameter) |

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

⛔ **And seven of those ten are real drift.** Re-running each twice in one isolated copy separates
the causes mechanically: **7 CODE DRIFT** (deterministic, corpus-blind, and still disagreeing —
*published numbers their own code no longer produces*), **2 NONDETERMINISTIC** (unseeded draws, a
design choice, but numbers no re-running gate can ever certify), **1 CORPUS-DEPENDENT** (`R242`
counts rounds; the corpus grew 23 → 124). **The pre-registered cross-instrument prediction held 2 of
2**: the only two of the ten that R345 had independently flagged STALE from a recorded source hash
are both CODE DRIFT — a static hash and a live re-run, sharing no code, agreeing on both. **5 of the
7 drifters carry no stamp at all.** *Its corpus-read control failed twice first — a regex called R242
blind and R347 corpus-reading, then the behavioural plant went into the wrong epoch — so the property
is now measured by planting 24 rounds in E05 and re-running.*
→ [`R350`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R350_why_the_ten_differ)

✅ **And no published number moved.** Diffing each drifted artifact against its regenerated twin:
**27 differing leaves**, of which **6 rendering collisions across 2 leaves** — both traced to their
true source and refuted. The page's `② − ① = +0.0540` is `R347.ref_gap_mean` (0.05403), not R34's CI
bound (0.05398); the page's *"verbatim pairs 0.0191 apart"* is `R223.verbatim.err_vs_identity`
(0.0190797), not R34's (0.0190795) — **two unrelated estimates agreeing to six decimals**, which is
exactly how a rendering search manufactures a false identity. *The drift is real and confined to
fields nobody cites, at a floor of 3 significant figures over these two documents — a bound, not a
clean bill.*
→ [`R351`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R351_did_a_published_number_move)

✅ **Nor their own writeups — so regenerating them is safe.** The population R351 deliberately
excluded, checked *before* regenerating rather than after (regeneration would destroy the evidence):
**0 of the 27 differing leaves is quoted in its own round's README.** The pre-registered prediction —
that `R34` and `R36`, holding 22 of the 27, would be the exposed ones — **failed**: drift volume does
not predict prose exposure. *Cross-citation between rounds is still uncovered, and is the real gap.*
→ [`R352`](E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/R352_would_regenerating_break_their_own_readmes)

⛔ **And the admitted set of five recurs in 7.7% of pool orderings.** The clause-② reference is a
**prefix of a file**; permuting the pool (400 orderings × 2 seeds) gives **24–25 distinct admitted
sets**, a mean size of **6.8**, and P(published five) = **0.070–0.077**. The published set is a
**tail draw** — its reference sits at the 93.7th percentile of size-4 subsets, so the baseline is
unusually strict. Three arms it excludes are admitted under most orderings: `generic` **0.76–0.80**,
`topw_k2` **0.69–0.72**, `topw_k1` **0.42–0.43**. ⭐ And R339's **prompt** bootstrap put `topw_k2` at
**0.13** and `generic` at **0.05** — two uncertainty sources, opposite pictures, both correct and
answering different questions. *The identity permutation reproduces the committed five exactly.*
→ [`R353`](E05_the_space_of_compilers/A24_what_the_definition_costs/R353_the_admitted_set_under_every_pool_order)

⛔⛔ **And at the reference this campaign itself argued for, the definition admits TWO.** R331 derived
the rule — **p99, not p94** — because every blind k=4 subset is a member of clause ②'s own reference
class, so a reference admitting any of them is refuted by the clause's own words; the published one
admits **3**, p99 admits **0**. The rule had never been evaluated. Applied: **7** arms at a median
reference, **5 flat across p75–p95** including the published p93.7, and **2 at p99** —
`coval_core` and `topw_k6`. *So the published reference is not where the collapse happens; the
choice between p94 and p99 is, and R331 already argued it.* ⚠ **And the "two" is a measurement of an
unstable quantity**: R332 had already found **two distinct admitted sets within 0.25 MDE** at this
altitude, so what the level supports is the surviving **pair** — `coval_core` and `topw_k6` — not a
count.
→ [`R354`](E05_the_space_of_compilers/A24_what_the_definition_costs/R354_what_the_safe_reference_admits)

**And the "closure level" those three rounds all lean on was measuring the wrong object.** R332
defines it as *"the LOWEST reference that is closed: anything stronger is gratuitous"* and computes
the **first** grid point with a zero blind-admission rate. Those coincide only if the closed region
is an **upward set**, and it is not: at **6 of 9 k**, **18 references stronger than the published
closure admit blind sets again**. The mechanism is R331's own — *a paired MDE is a property of the
PAIR* — applied to the **reference** axis R331 never applied it to, and the excess is resolved
(**+1.19 shared criteria over each k's own null, MDE 0.42**, positive at all six violating k). The
rival world was **built**, not imagined: flatten each reference to a constant vector at its own mean,
making admission a pure threshold, and the violations go to **zero at every k**. Corrected safe
levels sit at **p96.2–p99.5**, so at k=6 and k=8 even p99 is below safe. R331 saw none of this
because its **9-point grid returns 0 violations**; 45 points give 18 and 91 give 50 — a lower bound,
not a converged number.
→ [`R355`](E05_the_space_of_compilers/A24_what_the_definition_costs/R355_is_the_closed_region_upward_closed)

**And the whole admitted set is judge-specific — at a second judge it is EMPTY, measured on all 41
arms, and that round had reached no page at all.** `R301` re-judged every arm at Qwen3.5-0.8B-Base
and returned **`{}`** where 2B returns five. `FORMULATION.md` carried the claim but scoped it to
**"3 arms of 41" (R290)**, so the page **understated its own evidence by 13.7×** while R301 sat
committed on disk, cited nowhere. Nothing catches this: the coverage gate requires a round to reach
*a* README, and 289 of 343 rounds live only in an arc index.

**`R356` then priced what R301 could not settle.** R301 printed `UNRESOLVED` between *shrink*
(β ≈ 0.40–0.43, ordering intact) and *reorder*, because its worst leave-one-family-out R² was 0.4817
on the `random_k` family. Scoring each family's between-judge ρ against the null its **own arm
separation** implies: `random_k` (2.2 se apart) sits at the **0.00 percentile** of its own null and
survives Bonferroni — **a real inversion** — while `topw_k`'s +0.81 sits at the *20th* percentile of
what **5.7 se of separation forces**, and carries no information at all. **So `REORDER` survives with
an address**, and no family agrees *more* than forced, so the shared-judge-error confound that would
inflate every between-judge number here is **not observed**. I designed the round expecting the
opposite — that `random_k` was noise — and the unit nearly hid it: separation printed in **MDE** units
reads 0.79 ("below resolution"), in **se** units 2.21 ("well ordered"), and `MDE = 2.80 × se`.
→ [`R356`](E05_the_space_of_compilers/A24_what_the_definition_costs/R356_is_the_within_family_disagreement_resolvable)

**Then the gauge test partitioned that round, and one of its two halves is withdrawn.** R356's null
calls the 2B effects *truth*; but *do these judges disagree beyond noise* is a **relation**, so
swapping which judge is truth must leave it unchanged. It does not, and the split is informative:
`random_k` is flagged at the **0.00 percentile in both directions** — **the inversion is a property
of the pair and survives** — while `topw_k` moves from 20.16% to **1.43%** and its reading as
*"forced, therefore no information"* is **⛔ withdrawn**. The direction is consistent even where the
verdict is not: `topw_k` sits in the **low tail both ways**, so *agrees less than its separation
forces* survives and *resolvably so* does not. The mechanism is **regression to the mean** —
`β(2B→0.8B) = 0.4340` but `β(0.8B→2B) = 1.4112`, an **expansion, not the reciprocal 2.30** — and
taking the noisier judge as truth inflates the apparent separation, lifting `topw_k`'s floor from
+0.66 to +0.83. Two further corrections came from checking rather than assuming: my slope differed
from R301's because I had **mixed in two arms measured on 398 prompts instead of 968** (the
population, not the estimator), and **a third judge is not "a drop-in"** — the prompt contract is
byte-identical but **no third checkpoint exists locally**, so that register line moves from
`NOT-ATTEMPTED` to `NOT-ATTEMPTED-AND-NOT-CHEAP`.
→ [`R357`](E05_the_space_of_compilers/A24_what_the_definition_costs/R357_does_the_inversion_survive_swapping_truth)

**And the closure defect is the ESTIMATOR, not the judge — it replicates.** R355's mechanism is a
property of the paired-MDE admission rule, so it predicted its own replication at a second model.
On the identical 16-criterion pool at Qwen3.5-0.8B-Base — loaded by R301 but **never enumerated** —
violations appear at **both** judges at **overlapping k (12, 13)**, and the 9-point grid finds none
at either, reproducing R355's blindness independently. At 0.8B **no arm clears any reference at or
above that judge's own closure**, and four arms clear *something*, so this is a measurement rather
than the forced consequence of an already-empty set. ⛔ My pre-registered `W-WORSE` — *noisier judge,
more violations* — **failed in sign** (4 vs 18), and my first repair failed too: if the MDE scale
explained it the **normalised** rates would match, and they are **0.53× and 0.60×**. That residual is
**named, not closed**. Replication rests on the k-overlap, never on a count comparison.
→ [`R358`](E05_the_space_of_compilers/A24_what_the_definition_costs/R358_does_the_closure_defect_replicate_at_the_second_judge)

**And clause ② cannot be repaired by restating it relatively — the judge-dependence is in the ARMS,
not the reference.** The definition admits 5 at 2B and 0 at 0.8B, so it has no judge-invariant
content. The obvious fix is to state clause ② **self-normalising** — beat the p-th percentile of the
blind class *as scored by whatever judge is in use* — instead of beating one fixed criterion set
whose level every judge rescales. **At matched strictness it changes nothing:** R331 puts the
published reference at the **93.7th percentile**, and there the two formulations are
indistinguishable — **9 vs 9 at 2B, 0 vs 0 at 0.8B**, on 42 arms. The relative form *does* admit arms
at 0.8B for p = 50–75, but every one of those bars is **below 93.7 by construction**, and reading a
lower threshold as a better definition is the trap this round was most likely to fall into. **There
is no percentile at or above the published strictness at which the second judge admits a single arm,
under either formulation.** This matches R356/R357: a reference sits *above* an ordering and cannot
*reorder* it — so a judge-invariant definition needs a judge named inside its text, or a different
observable. ⛔ And I twice declined validated evidence: 30 of the 42 arms reach 0.8B by a path R301
**parity-controlled** (Δ +0.00131 vs MDE 0.01193, `parity_can_fail: True`), and refusing it left v1
with 12 arms and **not one defined percentile**.
→ [`R359`](E05_the_space_of_compilers/A24_what_the_definition_costs/R359_can_clause_two_be_made_judge_invariant)

**⭐ And one clause survives everything: ③ is unsubstitutable.** Running §4's mechanical test — *name
an admissible object this clause excludes* — across all three at once: clause ① excludes **0**
(derived, R347), clause ② excludes **33 of 42** (measured), clause ③ excludes **4** — and the four are
exactly the arms that read the prompt's own labels, which is forced by what clause ③ *is*. The one
non-forced question is whether a **stricter clause ② could do clause ③'s job**, and the answer is no,
maximally: **across all 45 reference levels the label-user count never falls below 4**, while the
published five fall to **0** at the strongest reference. At p=100 the only arms still admitted are
`oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` — **strengthening clause ② removes
the arms the definition exists to admit and leaves exactly the arms it exists to exclude.** So on a
definition whose clause ① never binds and whose clause ② is emptied by a change of judge, **clause ③
is the one part measured to be irreplaceable.** ⛔ My pre-registered branches had no home for this
and the default one printed *"at most partly replaceable"* — the reverse of the data.
→ [`R360`](E05_the_space_of_compilers/A24_what_the_definition_costs/R360_which_clause_is_load_bearing)

**⛔ And the sentence I published as the campaign's one unconditional claim survived exactly one
round.** R360 ran at **2B only**; its register waved the second judge off as *"nothing is admitted
there anyway"*, which is true about **admission** and does not settle a claim about an **ORDERING**.
Recomputed at 0.8B: the label-user count over the same 45-level sweep **falls to 0** — references
*do* purge them there — so **clause ③'s irreplaceability is 2B-specific.** The rank dominance is
**resolved at 2B** (gap −4.50, exact two-sided **p = 0.0159** over all **C(9,4)=126** assignments)
and **not resolved at 0.8B** (+2.25, p = 0.2857), where the label-users **split** — one ranks 1st,
one ranks 8th. ⛔ My first branch fired `W-INVERTED` on a bare comparison of two means and was about
to publish *"the judges disagree about which arms to exclude"* — **an unresolved statistic
preempting a resolved one**; the verdict now rests on the sweep, which needs no rank. **What
survives is the rule on PROVENANCE grounds**, which apply by inspection and need no judge — a weaker
and different argument than irreplaceability. `DEFINITION.md` is corrected, and its gate now checks
**13 of 13** claims.
→ [`R361`](E05_the_space_of_compilers/A24_what_the_definition_costs/R361_does_clause_three_hold_at_the_second_judge)

**And the size band's PREMISE fails at the second judge, not merely its boundaries.** The size claim
was the last quantitative statement in the definition whose supporting round predated the judge axis.
Recomputed at both: only the band's **exit** (8→12) resolves at *both* judges; both entry steps
(1→2, 2→3) resolve at 2B and **not** at 0.8B, and 0.8B resolves an **interior** step (3→4) that 2B
does not — so *neither* "collapses" nor "moves" describes it, and the round carried a fourth branch
for exactly that. ⛔ **And my own "is it forced?" line hid the finding inside an absolute value:** the
median margin ratio is **−0.343** against R301's fitted shrink **β = +0.401** — a **sign inversion at
4 of 7 sizes**, not attenuation. At 0.8B the rubric's top-k margin is **negative at 6 of 7 sizes**
and resolvably so at k=12: it does not beat a size-matched blind set at any size, so there is no band
there to have boundaries. Two parts were **not** re-run because they are settled — the upper bound
`k_max = max{k : C(n,k) ≤ a(m)}` is **combinatorial with no judge in it**, and the k-curve's *shape*
was already measured by R356. `DEFINITION.md`'s size claim is now judge-indexed; its gate checks
**15 of 15**.
→ [`R362`](E05_the_space_of_compilers/A24_what_the_definition_costs/R362_does_the_size_band_survive_the_judge)

**⛔ And clause ③ — the campaign's last unindexed claim — closes only the RANKING channel.** It is
applied everywhere by one hand-written set, `{oracle_k4, oracle_k4_fit1, greedy_k4_fit1,
indep_k4_fit1}`, duplicated across four rounds and **never checked against the code that builds the
arms**. Audited against `corebench/select_core.py`: the set is **correct about the rankings** —
`comparisons.jsonl` is opened only for those three rules. But **`topw_k`, which supplies four of the
published five**, selects on `w = mean importance score` from the rubric, and the annotators who
wrote those scores are **95.3%** the same people whose rankings define that prompt's target.
**Cross-prompt sham 0.016 — a 58× ratio** over **1,160** distinct annotators against a median panel
of 16; **473 of 968** prompts have complete overlap and **none** has zero, so this is provenance and
not pool size. ⚠ **MEASURED** is the overlap (a census, **no judge anywhere in it** — the only claim
here of that kind). **DERIVED**, with the release's own finding that rubrics are authored *after*
ranking, is that `topw_k` is **not producible from the conversation alone**. **UNMEASURED** is how
much of its advantage the channel carries. `DEFINITION.md`'s clause ③ is narrowed; its gate now
checks **19 of 19**.
→ [`R363`](E05_the_space_of_compilers/A24_what_the_definition_costs/R363_clause_three_does_not_close_the_rubric_channel)

**✅ And the channel is open and carries nothing measurable — so the wording was wrong and the arms
are not.** Rebuilding `topw_k4`'s weights from annotators overlapping the evaluators in a swept
fraction, the margin is **flat**: paired `margin(d=1) − margin(d=0)` = **−0.0000 against its own MDE
0.0096**, three seeds straddling zero (+0.0035 / +0.0001 / −0.0036). ⚠ **A bound, not a zero** —
`topw_k4`'s margin is +0.0139, so this rules out a channel above ~69% of it and says nothing about a
smaller one. ⛔ **v1 had placebo, sham and split and NO positive control**, and I was one commit from
publishing a null with no demonstrated power; a planted person-specific channel is now detected from
**+0.0297** upward and **not** at g=0. The sham — permuting *which annotator's scores carry which
id* — lands inside the MDE, so the dose really was measuring identity. **And the question was
unaskable with the standard tools**: `score.py:88 load_targets()` reads `annotator_id` on line 103
and returns `(ranking, demographics)`, dropping it, so no round using that loader could align a
ranking to the person who wrote the rubric. Gate now checks **21 of 21**.
→ [`R364`](E05_the_space_of_compilers/A24_what_the_definition_costs/R364_how_much_does_the_rubric_channel_carry)

**⭐ And the empty channel is NOT a 2B statement — the first claim in this definition to survive a
change of judge.** R364's null ran through A2 and so through a judge, which is exactly the exposure
that emptied clause ②, inverted an arm family's ordering, destroyed the size band's premise and cost
clause ③ its irreplaceability. Re-run with **one input changed** — the same function computing both
judges — the dose is flat at **both**: **−0.0000 vs MDE 0.0096** at 2B and **+0.0000 vs MDE 0.0107**
at 0.8B. **0.8B's MDE is only 1.11× 2B's**, so that design *could* have excluded what 2B excluded —
and the kill carried a pre-registered `W-UNINFORMATIVE` branch for the case where it could not
(**silence, not agreement**), which did not fire. The planted channel is **detected at both judges
and undetected at g=0 at both**, so neither null is silence. ⚠ Two judges can **refute**
instrument-independence and never establish it, so what is earned is **"not refuted at a second
judge"** — and at 0.8B the level itself is unresolved (−0.0126 vs 0.0145), making it a flat dose on a
null level. Gate now checks **23 of 23**.
→ [`R365`](E05_the_space_of_compilers/A24_what_the_definition_costs/R365_is_the_empty_channel_a_2B_statement)

**⛔ And my explanation for that survival is refuted by an artifact I had already committed.** R365's
commit closed with a mechanism *and an action* — *"it survived because it is a DIFFERENCE, and
differences are what shrink transformations preserve … the definition should be restated in
differences."* **R362's size-band steps are differences of differences too, and 1 of 3 survive.**
Over the whole population of **7** claims run at both judges, neither `difference` (Fisher
**p = 1.0000**) nor `null` (**p = 0.4286**) sorts survival — **on a powered test**, since a perfect
split at n=7 reaches **p = 0.0286**. So this is a null, not silence, and **nothing in the record
predicts which claims survive the judge.** ⛔ **`Restate the definition in differences` is
withdrawn.** And the rival explanation is a **derivation** that downgrades my own headline: under any
scaling `x → βx` a true **zero maps to zero exactly**, so **a null surviving a shrink is the cheapest
possible survival** — and R365 *is* a null. Its measurement stands; **what changes is what that
survival is evidence for.** Gate now checks **27 of 27**.
→ [`R366`](E05_the_space_of_compilers/A24_what_the_definition_costs/R366_does_anything_predict_which_claims_survive_the_judge)

**⭐ And J can now be named, so the definition becomes applicable.** It carried *"under a named judge
J"* four times while **nothing in 366 rounds said which J, or how to pick one** — an instruction
nobody could follow. The rule: **name the judge that best tracks the human.** On the full rubric
(neither an admitted arm nor the clause-② reference) A2 is **0.5087 at 2B vs 0.4120 at 0.8B**, paired
**+0.0967 vs MDE 0.0160**. ⛔ **But that rule names the judge under which the definition is non-empty
— the answer I already published — and A2 is the definition's own quantity**, so it was checked on a
**definition-external** channel: the release's `unacceptable` ratings, which no clause reads. There
2B ranks the unacceptable last **0.7019** of the time vs **0.5839** (paired +0.1180 vs MDE 0.0638, on
**161** prompts). **Same judge.** A synthetic judge built to rank it last scores 1.0000 (so the
channel separates); shuffled labels score 0.59–0.63 — **where 0.8B nearly sits**. ⚠ The external rule
resolves at only **1.85×** its MDE, and two judges can **refute** a rule and never establish one, so
what is earned is *"not refuted, and not circular on the one external channel available"*. Gate now
checks **30 of 30**.
→ [`R367`](E05_the_space_of_compilers/A24_what_the_definition_costs/R367_can_the_judge_be_named_non_circularly)

**And the clause the definition never had: TRANSPORT.** It certifies a core against the four
responses it was scored on and said nothing about new ones — **`transport` appeared zero times**.
R233 measured it once and **declined its own verdict**, naming the confound (*"the design conflated
`unseen` with `equally hard`"*) and the fix (*"match the arms on difficulty"*). The 33,320
judgements are cached, so the fix was a **re-analysis, no GPU**. Matched on per-prompt difficulty,
the core reproduces the full rubric's ordering on **unseen** responses better than a size-matched
random draw: **+0.0992 vs MDE 0.0654** on R233's exact-class metric, **+0.0612 vs 0.0535** on a finer
one — same sign, both resolved. ⛔ **v1 ran a different statistic and the floors caught it**: scoring
the *fraction* of pairs gave random floors of 0.83/0.82 against R233's 0.4044/0.4166; corrected to
exact class match they land at **0.4133/0.3960**, and *that agreement is the check that this is
R233's test*. ⚠ **Marginal** — 1.52× and 1.14×, with the MDE over **4 strata**, so the effective n is
the strata, not the 250 prompts. ⚠ **And the shape is unexplained**: the core is **at or below random
on the responses it was built for** and above random on responses it was not — **[UNTESTED]**,
recorded as the residual rather than narrated. R233's limit stands: fresh responses carry **no human
rankings**, so this is transport of the *compilation*, never agreement with people. Gate **32 of 32**.
→ [`R368`](E05_the_space_of_compilers/A24_what_the_definition_costs/R368_transport_matched_on_difficulty)

**⛔ And that contrast decomposes the opposite way under the two metrics — R368 computed the floors
and never printed them.** `Δfloor` is **+0.0308** on exact and **−0.0187** on pair: under one
defensible metric the random baseline **rises** on the fresh arm, under the other it **falls**. So
*"the core transports"* was stated as though the baseline held still. ⚠ **The instability is
bounded, and saying otherwise would overstate it**: `Δcore` is positive under both (**+0.1300**,
+0.0425) and larger in magnitude than `Δfloor` in both, so the core term dominates either way — what
is metric-dependent is the **attribution of magnitude**, not the direction. ⛔ **And the check that
looked like it settled the underlying question was wrong**: the floor is drawn from `full`'s own
criteria while the core is a rewrite, and `core ⊆ full` held in **250 of 250** prompts — until the
index sets turned out to be `(0,1,2,3)` in 241 and `(0,1,2)` in 9. **Purely positional. An indexing
artifact carrying no information about criterion identity.** Separating subset-advantage from
transport needs a floor drawn from criteria **outside `full`** — the next instrument, not a caveat.
Gate **34 of 34**.
→ [`R369`](E05_the_space_of_compilers/A24_what_the_definition_costs/R369_the_transport_contrast_decomposes_two_ways)

**⛔ And against a floor that is NOT a subset of its own target, the transport contrast collapses —
so transport becomes a stated LIMIT, not a candidate clause.** The suspicion needed new labels, so
the generic 16-criterion pool — identical across prompts, hence outside any prompt's `full` rubric by
construction — was judged against the fresh responses (**16,000 labels**, pueue task 630). ⏱ **The
kill was pre-registered and committed while the job was still judging**, and verified to refuse to
run early. With the fair floor the contrast is **+0.0810 vs MDE 0.0920** (exact) and **+0.0161 vs
0.0251** (pair) — **inside the MDE on both**, no metric split. **The subset advantage is now a
number**: the subset floor sits **+0.1413** above the non-subset one on the original arm. ⚠ **Not
refuted — not resolved**: both point estimates stay positive, and the collapse arrives two ways (on
`pair` the contrast falls **74%**; on `exact` the **MDE grows 41%**). The reproduction control
recovered R368's **+0.0992 / +0.0612 exactly**, so this is about that quantity. **R368's number
stands as a number; what it measured was the floor.** Gate **36 of 36** — and it caught a regex
collision doing it, where the bare pattern matched R367's +0.0967 instead.
→ [`R370`](E05_the_space_of_compilers/A24_what_the_definition_costs/R370_a_non_subset_floor_for_the_fresh_arm)

**⛔ And R370's verdict is itself a specification choice — it fixed S=4 and never swept it.** R370's
NEXT said *"the binding constraint is now n"*, but its MDE is `ZEFF · sd(per-stratum contrasts) /
√n_STRATA` — a **between-strata** error over **four points**, which more prompts do not shrink. So the
718-prompt job was **priced for free before any GPU**. Sweeping S: the `exact` contrast **resolves at
S = 2 and 5** and does not at S = 3, 4, 6, 8; on `pair` it is inside the MDE everywhere. **The honest
statement is the curve, not the cell.** The between-stratum spread is **sampling noise, not
structure** — median ratio **0.98** against a *no-heterogeneity* null — and the MDE **rises** with S,
so **more prompts help only at fixed S, never by adding strata.** ⛔ **Two of my own defects, caught
before publishing**: the null was **malformed and nearly forced** (v1 resampled each stratum *from
itself*, so `observed ≤ bootstrap` by construction — it returned 0.65 and I would have published
`W-OVERFIT`; rebuilt as the pooled-draw world it moves to 0.98 and the verdict **inverts**), and the
else-branch **asserted "the MDE falls with S" while the line above printed that it does not** — fifth
verdict-string failure this session, with **no branch for the world that obtains**. Gate **37 of 37**.
→ [`R371`](E05_the_space_of_compilers/A24_what_the_definition_costs/R371_would_more_prompts_resolve_transport)

**⛔ And R371's own reading died the same way — the curve is no more reportable than the cell was.**
Re-running the whole S-sweep on **480 random halves** of the same 250 prompts: R371's set `{2, 5}`
recurs in **2.9%** of halves, the modal outcome is the **empty set at 41.5%** across **38** distinct
sets, and the two halves of one split agree on the set **4.4%** of the time once both-empty
agreements are removed (the raw 18.3% is 14.6 points of exactly that). **Three separate reasons the
curve cannot be read, and I built the second.** ① `p(S) separates` is a **derivation** — R371 itself
measured that the MDE rises with S while the contrast does not, which makes resolution fall by
algebra; the pre-registered kill is reported **as written** rather than moved after the data.
② **S = 2 tops every ranking because its denominator collapses**: a between-stratum sd at S strata
has S−1 df, so at S=2 it has **one**, and it lands below half the typical contrast in **28.3%** of
halves against at most **7.3%** elsewhere — 3.9×. The tell was a `pair|2` cell returning **MDE =
0.0007**. ③ R371's floor was **order-dependent** (one rng shared per call), and 12 permutations move
the `exact|S=4` contrast across **+0.0540 … +0.1185**; repaired, the full-sample set is **{2, 3, 5}**.
**The resolving set is not a quantity** — R371 was right that R370's S=4 was a specification choice,
then read a SET off the same single draw. Gate **44 of 44**.
→ [`R372`](E05_the_space_of_compilers/A24_what_the_definition_costs/R372_is_the_resolving_set_stable)

**And the collapse reaches exactly one round outside that family — the one the definition cites.**
`P(sd_hat < f·σ) = chi2.cdf(f²(k−1), k−1)` is **algebra**, and its assumption is *tested*: the ratio
p10/median of the MDE carries **no free parameter**, and against R372's **24** measured cells the
prediction misses by at most **0.0642** (tolerance 0.10) while itself ranging 0.186→0.668. Census:
**55** MDE call sites across **38** rounds; **5** divide by a count of aggregated units; after
resolving each k, **R368 alone outside R370–R372 has k < 10 — at k = 4**, where the sd lands below
half its true value **13.9%** of the time. R368 is the transport row of `DEFINITION.md`: **not
refuted, under-priced.** ⛔ **Two instruments corrected before publishing**: a census keyed on the
sibling `k` would have called R301 a 4-unit design (**`k` here means core size**, beside an MDE over
968 prompts), and a word list measuring *"who records their denominator"* returned 2 of 38 with
**R355 and R368 both false negatives** — withdrawn as UNVERIFIED, because a guessed list cannot prove
an absence. ⭐ **The debt is paid, not frozen**: a new gate flagged R368 and R370, both were re-run
with `n_units` recorded, and **only `n_units` and the stamp changed** — 5 of 5 compliant. Suite
**25/25**, gate **51 of 51**.
→ [`R373`](E05_the_space_of_compilers/A24_what_the_definition_costs/R373_can_the_campaign_audit_its_own_resolution)

**And the report that found all this was itself running on a broken measurement.** R373's commit
corrected it: a shell loop read `$?` after a command substitution had already run `basename`, so it
printed basename's exit code and reported **"41 doc gates exit 0"** while **twelve were red**. Asked
properly — *were they ever green?* — the eleven not attributable to this session split in two.
**Five have NEVER exited 0 since the day they were committed** (`attack_no_withdrawn_framings`,
`attack_outcome_variable_declared`, `_isolated`, `pueue_wait`, `verdict_cites_its_own_contrasts`):
a gate that never passed is **a claim about the corpus that the corpus never made**, and there is no
regression to find. **The other six were green at HEAD~512 (07-29) and red by HEAD~256 (08-03) —
all six in the same bracket**, which is one commit far more plausibly than six. Ladder: 12 rungs over
**692** commits, **132** cells, the gate **as it was** on the tree **as it was**, with both harness
controls (a known-green and a known-red gate reproduced through the worktree) passing first.
⛔ **R373's own hypothesis is partly refuted by the table**: it argued exit-2 gates were stale
registrations, but `readme_row_carries_the_verdict` and `synthesis_cites_recent_work` both exit 2
today and **both exited 0 at HEAD~512** — an exit-2 gate can be a regression that destroyed its own
input.
→ [`R374`](E05_the_space_of_compilers/A24_what_the_definition_costs/R374_were_the_red_gates_ever_green)

**And bisecting that bracket refuted the prediction I had just written into it.** R374's NEXT said a
single commit was *"far more plausible than six"*. It is **four distinct commits over three days**:
`380fcfb18` (07-31) took two gates, `3c3fe2482`, `9273f32e0` and `60f3871b5` one each. Neither one
cause nor six — **a backlog of four repairs**, and the bracket was an artifact of a 12-rung ladder,
exactly as R374's own W-INDEPENDENT branch warned. ⛔ **And the monotonicity control is why this
round is worth anything**: a bisect presumes the gate goes green…green red…red exactly once, so 3
commits were probed each side of every transition — **`attack_every_check` flickers**, red at two
commits *before* the one the search returned. A plain bisect would have handed me `2580fb140` with
full confidence; **"the commit that broke it" is not a well-formed object for that gate**, and it is
withdrawn from the count rather than given a spurious answer. Endpoints were **re-measured here, not
inherited** — 6 of 6 reproduce, so R374's ladder and this bisect agree about the bracket they share.
86 evaluations, 85 checkouts, two runs byte-identical. ⚠ This round returns a **commit, never a
cause** — reading a cause off a diff is a story that costs nothing to produce.
→ [`R375`](E05_the_space_of_compilers/A24_what_the_definition_costs/R375_one_commit_or_six)

**And reaching for the instrument that would answer R375's next question found it declaring itself
unfit.** Classifying what those four commits *did* needs the read-set of each gate, which
`what_did_each_check_actually_read.py` measures with a CPython audit hook — but that is built on
`assurance/_isolated.py`, which fails its own selftest and prints **`FAIL — do not use this
harness`**, and which R374 had already counted among the five born red. So R375's question was
**deliberately left unanswered** and the harness was measured instead. The failing line was *"g=0
(harmless subject): dirtied 2 path(s)"* against `len(changed) <= 1`, for a subject whose whole body
is `print('noop')`. **Reading the two paths rather than counting them**: `.venv` and
`assurance/_noop_probe.py` — the linked interpreter and **the probe the selftest itself writes**.
**Zero tracked.** Containment was never in question: the saboteur that deletes an epoch dirties
**95 tracked** paths, the MAIN tree is **5/5 intact**, the restore heals from git, and the subject
verifiably ran. ⭐ **Repaired to `no TRACKED path may be dirtied` — 0 on the benign subject, still
firing at 95 on the destructive one.** That contrast is the only evidence separating a fix from a
quiet disarm, and it is why the threshold was not simply raised from 1 to 2. `_isolated.py` now
exits 0 and its dependent still runs green — **one of the five born-red gates satisfied, not
retired.** ⚠ This campaign's ledger puts *"the control fails for its own reasons"* at **4 of 7**, so
betting the base rate would have produced this verdict with no evidence; both worlds were built and
the paths were read.
→ [`R376`](E05_the_space_of_compilers/A24_what_the_definition_costs/R376_the_harness_that_says_do_not_use_it)

**And R376's closing sentence was wrong, which the next round measured rather than argued.** R376
blamed a read-isolation hazard: three rounds pointing at `scratchpad/assurance_wt`, also
`_isolated.py`'s default worktree. But `attack_every_check` runs with `cwd=ROOT` — the live tree —
and *"the source says so in one line"* is exactly the convincing description this campaign distrusts,
because the subject **invokes six other checks** and an indirect coupling would make the refutation
wrong. **All seven files grepped: worktree references NONE of 7.** Only then does the withdrawal
stand. Run 8× at one commit: **one exit code, one verdict table, zero runs leaving the tree dirty** —
so the `1 → 2 → 1` I observed is **not run-to-run noise but tree-state dependence**, and nothing about
the `_isolated` repair is required to explain it. ⭐ **What that does to R375**: its withdrawal of
`attack_every_check`'s breaking commit was correct **and now for a stated reason** — a check
deterministic given the tree that behaves non-monotonically across commits is responding to a real
difference in corpus, not to noise. *"The commit that broke it"* stays ill-formed, but because the
property turns on and off, not because the instrument is unreliable. ⚠ The state variable itself is
**UNVERIFIED** — a corpus hypothesis is labelled and untested. ⚠ And the round excludes its **own**
directory from its start-clean check, which is R376's finding applied to myself one round later.
→ [`R377`](E05_the_space_of_compilers/A24_what_the_definition_costs/R377_is_the_flicker_in_the_check_itself)

**And an INTERVENTION refuted R377's hypothesis — the placebo is the only reason a false structural
claim was not published.** R377 proposed that `attack_every_check`'s state variable was whether
`every_round_reaches_the_readme` passes, since it is one of six checks the subject plants into.
Three README states, three runs each: **BASE** (as committed), **KNOCKOUT** (the newest round's link
line removed, which really does flip that gate 0 → 1), and **PLACEBO** (a byte-different edit that
leaves every gate's verdict alone). Knockout moved the subject **1 → 2** — and **so did the placebo,
which was a single appended newline.** ⛔ So the dependence is on the **FILE**, not on another
gate's verdict: `W-ANY-EDIT`, and R377's hypothesis is **refuted by intervention**. Without the
placebo the knockout alone would have read as *"one gate decides another"*, and the ten red gates
would have been declared a dependency graph whose repair order matters. **They are not shown to be
one.** ⚠ And the round then failed its own re-run: its artifact made R378 a round mentioned in no
README, so the baseline gate went red and the KNOCKOUT control correctly reported **UNVERIFIED** —
the subject exits reproduced exactly, the *baseline* did not. **A round whose artifact joins the
corpus its own gates read cannot re-run itself into the same baseline**, which is R376's scaffolding
lesson at a third level.
→ [`R378`](E05_the_space_of_compilers/A24_what_the_definition_costs/R378_does_one_gate_decide_another)

**And the plan for grouping the ten reds was wrong at its root — abandoned before it was written.**
R378's NEXT proposed grouping them by the population each says it lost, *because four exit 2*. That
is a **search instrument with no positive control**: its unit is *words I chose to look for*, while
the claim's unit is *the set of files a gate actually examined*. Not equal, so the objective
instrument was used — **the audit-hook harness R376 had repaired two rounds earlier**, used here for
the first time on a question it was not repaired for. Measured: by **exit code** the ten split 6/4;
by **read-set** they split 5/5, and **five gates cross**.
`readme_row_carries_the_verdict` exits **2** while opening **587** round artifacts and
`verdict_cites_its_own_contrasts` exits **2** while opening **529**, whilst
`attack_no_withdrawn_framings`, `attack_outcome_variable_declared` and
`donor_numbers_carry_their_draw_scope` all exit **1** having opened **zero**. ⛔ So *"exit 2 means it
lost its population"* is **false here** and the grouping would have been drawn on the one fact that
carries no information about the other. ⛔ **And I built a control that could not pass — the fifth in
this ledger**: it demanded >100 round files from a gate whose design ceiling is ~24, because that
gate *iterates* directories and only *opens* arc READMEs. Replaced by a plant with an exactly known
answer — a probe opening **50** real artifacts, reported as **50**. Reproduction against
`what_each_check_read.json`, written earlier by another script for another purpose: **10 of 10,
exactly**. ⚠ Three rounds have now measured *when* (R374), *which commit* (R375) and *what each
reads* (R379), and **stacking them still does not say why**.
→ [`R379`](E05_the_space_of_compilers/A24_what_the_definition_costs/R379_the_exit_code_is_not_the_population)

**And the first repair found a gate that convicted seventeen rounds using a glob matching zero
files.** `donor_numbers_carry_their_draw_scope` printed *"17 registry entries name a round that no
longer constructs a donor mapping — the registry has drifted from the source"*, having globbed
`rounds/E*/A*/R*/run.py`: **0 files**, while the tree holds **363** at `E0*/A*/R*/`. Pointed at the
real tree its own two regexes locate **17 of 17**. ⛔ **A zero from a detector never shown to return
non-zero is silence — and here it produced an ACCUSATION**, whose obvious remedy was to delete
seventeen registry entries to satisfy a typo. The gate's own docstring had warned of *"a check that
is right about what it iterates over and blind to what is missing"*; the confession was written and
the code did the opposite. ⭐ **Repairing the path immediately did the job the gate exists for**:
`R106_share_level_under_redraw` and `R109_donor_arm_is_text_blind` construct donor mappings and were
in no registry — both now registered with reasons. ⛔ **And repairing only that half would have
disarmed the gate by making it green**: GATE 2 rules on README table rows, the root README stopped
being a per-round table, and it locates **0** rows for **20** registry rounds. Its property stands,
its proxy is gone — so the repaired gate **says it examined nothing and exits 2**. *Fixing a gate is
not the same as making it green.* ⛔ **My own guard then masked a real finding** — v1 returned 2 even
when GATE 1 had caught an unregistered round, so the plant fired, the FINDING printed, and the exit
code said *empty population*. Precedence fixed and both directions demonstrated **on the live gate**:
**1** with a plant, **2** at g=0.
→ [`R380`](E05_the_space_of_compilers/A24_what_the_definition_costs/R380_the_gate_convicted_a_registry_it_never_read)

**And the follow-up refuted its own hypothesis, each time by making the instrument more precise.**
R380's NEXT proposed grepping every assurance script for `rounds/`. **That presupposes its answer** —
a grep for one known string can only find gates dead in the one way already found, so a zero would
read as *no others* while meaning *none of the kind I looked for*. Every path expression was
extracted with `ast` instead. The verdict then moved at every improvement: **2 gates share a dead
prefix** → **1** → **0**, ending at `W-NOT-A-PATH-PROBLEM`. The three removals are three different
false positives. ① v1 extracted *literals* and could not see the target at all: R380's dead path is
`(ROOT / "rounds").glob("E*/A*/R*/run.py")` — **two literals, neither dead alone**, since `"rounds"`
has no separator and `"E*/A*/R*/run.py"` matches **363** files. **The dead path is a composition, not
a literal**, and the positive control caught it *because its answer came from R380 rather than from
here*. ② A **regex is not a path** — `rounds/r8[89]_[a-z_]+` is matched against README text, never
globbed. ③ A literal **written into** text is not a path read from disk: `attack_every_check` plants
`"rounds/_no_such_round"` as a `.replace` target, designed not to exist; excluded **structurally**,
not by a word list. ⭐ A different candidate class did surface — **three red gates carry regexes
encoding a stale link format**, separated and *not* counted, because the right question for a pattern
is whether it matches anything in the documents it is applied to. ⚠ The blind spot has a size rather
than a disclaimer: **715** f-string expressions are invisible to `ast`. **R380's repair generalises to
nothing, and its one-round-per-gate rate is the rate to plan with.**
→ [`R381`](E05_the_space_of_compilers/A24_what_the_definition_costs/R381_do_the_red_gates_share_a_dead_path)

**And the class R381 handed forward was two, not three — then split again under measurement.**
`seed_filter_is_disclosed`'s pattern was flagged as a stale link format because it contains `//`,
which is **integer division**; R381's number was right about what it measured and wrong as a
description of what it found — the **fourth** false-positive class that census produced. Of the two
genuine link patterns, run against **every** corpus they could be applied to rather than a target I
inferred (1 + 24 + 364 files, 5.6 M chars): `donor_numbers…SCOPE` = `rounds/r8[89]_…` matches
**0 everywhere**, while `synthesis_cites_recent_work.CITE` matches **505** times. ⭐ The zero is an
**independent second confirmation**: R380 established that gate's GATE 2 vacuous by counting
**locatable README table rows** (0), and R382 reaches the same vacancy by counting **pattern
matches** (0) — two instruments, one conclusion. And the 505 **refutes** the stale-format reading for
`synthesis_cites_recent_work`, whose exit 2 has another cause entirely. ⛔ **The negative control
failed first and was right to**: an impossible token matched **twice**, both inside *this round's own
source*, which would have inflated all three pattern counts because the round prints the patterns it
measures. A round whose own text joins the corpus must exclude itself — R376's scaffolding lesson at
a fourth level. **They are separate repairs, and calling them one would be the grouping error R379
already cost a round.**
→ [`R382`](E05_the_space_of_compilers/A24_what_the_definition_costs/R382_does_the_pattern_match_anything)

**And testing the replacement proxy before adopting it produced a pre-registration I then refused to
follow.** Three candidate sites for the 14 governed rounds: the root README paragraph covers **14%**,
the round's own README **29%**, the arc README row **100%**. The rule fixed before any count —
highest site coverage, adopt at ≥80% — **elects the arc row**. ⛔ **I then invented two criteria aimed
at the winner and both failed**: capacity (66 chars, above the floor) and question-rate (36%, below
the cut). A third would have been a criterion tuned until it produced the answer I wanted, so I
stopped and both stay as *reported diagnostics*. ⛔ **My own docstring was false and my own measure
caught it** — I had written that the arc row's second column is empty; capacity returned 66, so I
read one: the arc README holds **two** tables and the second carries `r21 -- Is the "nearest-topic"
donor actually topically near?`. **A question.** And that explains the 2 of 14 that appeared to carry
a scope: the pattern matched `donor-draw` inside **R88's and R89's own question titles** — *both
numbers false positives of my own instruments, one level apart, and neither added criterion caught
it.* ⭐ **The pre-registration was on the wrong quantity: site coverage cannot tell a document that
STATES findings from one that LISTS them.** Real scope coverage: **0 of 14**. Adopting would give a
gate ruling on question titles — vacuous in a new way, which is what R380 refused. **The refusal
overrides a pre-registration, so it is declared rather than hidden.**
→ [`R383`](E05_the_space_of_compilers/A24_what_the_definition_costs/R383_test_the_proxy_before_adopting_it)

**And the assumption underneath all four of those rounds is false: 243 of 377 rounds have no finding
site at all.** The sites are not my choice this time — every arc README says of itself *"Each round's
README states its design; the finding lives in `../../README.md`"*. Measured against the campaign's
own specification: **114 rounds (30%)** have their own README, **84 (22%)** are named in the root
README, and **243 (64%) have NEITHER** — while **372 of 377 produced an artifact**, so it is not that
they had nothing to report. ⭐ **Which makes the nine remaining red gates ONE problem rather than
nine**: not a dead path, not a stale pattern, not a coupling, but a corpus whose findings were never
written where its own documents say they live. ⭐ **And a GREEN gate had already confessed it.**
`every_round_reaches_the_readme` accepts the root README *or* the arc README, and **293 of 377 (78%)
pass it only via an arc index row** — which R383 measured to be an index of *questions*. Its own
docstring reads: *"read the pass honestly: this check passes today because `generate_round_index.py`
wrote those arc tables in the same session. That is a CONSTRUCTION, not a discovery, and it is weak
evidence of the property."* **The confession was written; what was never done is measure how much it
admits** — and four rounds this session walked past it while auditing the *red* gates. ⚠ The number
is flattering by construction: the rounds written this session are in the root README because I
appended a paragraph for each, so coverage of everything older is lower than the headline.
→ [`R384`](E05_the_space_of_compilers/A24_what_the_definition_costs/R384_where_the_findings_are_not)

**And the test R384 proposed for filling that gap was void as written, so it was replaced by one
whose answer does not pass through my opinion.** It asked whether *a reader* could tell a generated
line from a hand-written one — **I am the reader**, and a judgement I make about text I generated is
self-review, which this campaign treats as void rather than weak. ⭐ **A ground truth already
existed**: 46 rounds have both a committed artifact and a root-README paragraph naming only them, so
a line generated from the artifact alone can be **matched back** to its own paragraph. Result:
**top-1 = 0.457** against a chance of **0.022** — 21× chance — with the true paragraph at **median
rank 2 of 46** and a permutation null at exactly chance. **A generated line narrows the field without
identifying the finding**: enough for a draft a person corrects, not enough to publish. ⛔ **The
positive control caught a broken population first**: a paragraph queried with itself retrieved itself
only **63%** of the time, because **one root-README paragraph names ten rounds** and **41 of 84
candidates share theirs**. A retrieval task with duplicated targets has no unique right answer;
restricted to unique targets the control forces to **1.00**. ⛔ **And my prediction about the
arithmetic trap was wrong in magnitude** — I wrote that leaving round identifiers in would force
top-1 to ~1.0; measured, **0.478 un-stripped vs 0.457 stripped**, a difference of **+0.021**. The
precaution was right to take and its size was mine to measure, not to assert. ⚠ These 46 are rounds
someone *chose* to write about, so **0.457 is an upper bound on the 243 that have none**, never a
floor.
→ [`R385`](E05_the_space_of_compilers/A24_what_the_definition_costs/R385_can_the_artifact_write_the_finding)

**And the draft reading did not survive one more measurement: a finding's numbers are 9% in the
artifact that produced it.** R385's NEXT asked me to hand-write findings and compare — **not
constructible here**, because I would write them and I have been appending to the root README all
session, the document holding the targets. That arm leaks by construction and *"I did not use what I
remember"* is unverifiable from outside, so it is **named as impossible rather than approximated**.
The decision was still answerable without writing anything: a finding's checkable content is its
**numbers**. Median per-round recall of a paragraph's numbers in its own artifact is **0.091** on
numbers of ≥3 characters, against a permutation null of **exactly 0.000** — small *and* real,
provenance rather than collision. **44% of rounds share no long number at all with their artifact**;
7% share every one. ⛔ **The collision control is the whole result**: recall over *all* numbers is
**0.500**, and without the long-number split I would have reported 50% and called generation a
partial success — small integers collide between any two numeric texts, long decimals do not.
⭐ **What it does to R385**: 46% top-1 came from vocabulary and verdict strings, not quantitative
content, so a generated line drafts a round's **identity** and not its **finding**. **The 243 is a
debt only writing can pay.**
→ [`R386`](E05_the_space_of_compilers/A24_what_the_definition_costs/R386_what_the_artifact_cannot_say)

**And the debt turns out to be collectable: 9 of 9 decided rounds still re-run, none fail.** R386's
NEXT asked whether a finding is still *recoverable* — **my judgement again**, so it was replaced by
one the machine answers: **can the round still be re-run?** Re-running the **12 oldest** rounds that
have an artifact, a `run.py` and no finding site, each in a git worktree restored between subjects:
**RAN 9 · FAILED 0 · TIMEOUT 3**. The findings do not have to be reconstructed from JSON at 9% —
**the code still runs and the output can be read.** ⛔ **Three of my own defects, all caught by the
controls before a single subject was scored**: ① the worktree sat where R375 left it, so newer rounds
returned `MISSING` — *not* `FAILED`, and merging those classes would have scored twelve subjects as
broken corpus; ② the negative probe was **erased before it could run**, which `_isolated`'s own
docstring warns of in as many words — **I quoted a confession from another gate one round ago and
walked into its twin**; ③ the negative control **re-implemented the classifier and disagreed with
it**, so it tested the copy rather than the check. ⚠ Executability is **necessary, not sufficient** —
this measured that the door opens, never what is behind it — and 12 of 229 is a **lower bound on
health**, since age is the strongest reason to expect rot.
→ [`R387`](E05_the_space_of_compilers/A24_what_the_definition_costs/R387_is_the_debt_collectable)

**And then one unit of the debt was actually paid, and priced: 21.3 s of machine time, 7 numbers
verified.** Eight rounds had established that the findings are missing, that generation cannot write
them, and that the code still runs — *a complete answer to "can this be done" and no answer to "is it
worth doing"*. **Eight rounds of diagnosis with no paragraph written is an audit presented as a
product**, so R388 wrote one: `R21_donor_distance`'s finding now sits in the table above under a
heading marking it as **backfill**, because a row written months after its round is a different
object from one written beside it. ⛔ **The real risk is fabrication, not cost** — nothing about a
backfilled row distinguishes a copied number from a remembered one — so **every number was checked
against a fresh run**, not the artifact, which R386 measured at 9%. All seven verify, and a planted
number absent from the run is caught, because *"all numbers verified" would otherwise restate "I
copied carefully"*. ⭐ **The verification is now a permanent gate** (`backfilled_findings_are_rederivable`,
suite **26/26**) — and two of my own defects were caught first: its positive control was **a check
that cannot fail** (`[n for n in [FAKE] if n not in set()]`), and **the suite corrected my
registration**, since the gate re-runs from a git worktree at HEAD and the emptying cannot reach it.
⚠ **n = 1**: R387 measured 3 of 12 rounds over 90 s, so multiplying 21.3 s by 237 would be the
arithmetic trap wearing a project plan. **The debt is a writing project — the harder kind to
pipeline, the easier kind to start.**
→ [`R388`](E05_the_space_of_compilers/A24_what_the_definition_costs/R388_one_unit_of_the_debt)

**Two more units paid — and then my own tooling deleted the round that priced them.** Running every
`assurance/*.py` in a bulk loop executes `_isolated.py`, whose selftest plants a saboteur that
deletes an epoch directory, and it ran against the **live tree**: **1,408 tracked files deleted, all
1,408 recovered by `git restore`, and 0 of the untracked work** — this round's whole directory and
two backfilled README rows. **Only committed work survived**; R388 had been committed and was intact.
The round was rewritten and **reproduces its census exactly**, an unplanned second measurement.
⛔ **R388's NEXT asked me to time my own attention** — unverifiable by anyone — so it was replaced by
a property of the object: *does the round state its own finding?* ⛔ **My first instrument measured my
own habit**: a marker list of `ESTIMAND`/`WORLDS`/`KILL` scored the three units I had just read at
**1, 0 and 0**. Reading their docstrings gave the corpus's real convention — a first line
`rNN -- <one sentence naming what the round is for>`. Measured over 226 rounds: **158 (70%) titled**
against **99 (44%)** for my own format. And **3 of 3 paid units end in a verdict line the round wrote
itself**, so the sentence was **read**, not constructed. ⚠ `W-SPLIT` — **the debt is two projects**,
and quoting the 70% alone would be the cell reported as the curve.
→ [`R389`](E05_the_space_of_compilers/A24_what_the_definition_costs/R389_the_reading_burden)

**And the untitled tier turns out not to be silent: 5 of 8 state a verdict anyway.** R389 split the
debt into 158 titled rounds (the sentence is *read*) and 68 untitled (it would have to be
*constructed*). Running 8 of the 68 in an isolated worktree: **8 ran, 0 unverified, 5 (62%) print a
verdict line the round wrote itself.** **R389's split was a property of the docstrings, not of the
findings.** ⛔ **Safety shaped the design**: R389's first copy died to `_isolated.py`'s saboteur
running against the live tree, so this round manages its own worktree and never imports that module —
and the live tree was never a subject's cwd. ⛔ **Two defects, both caught by the positive control**:
avoiding `_isolated` cost me its **input linking** (a fresh worktree holds only tracked files, so
`data/` was nearly empty and the model-loading rounds died), and my **120 s timeout** was too small —
R28 takes 36 s warm and longer cold. *A timeout is a statement about the budget, never about the
subject*, and folding it into "silent" would have convicted the tier with a number I chose. `W-MIXED`
— **8 run, 60 untried, named rather than assumed.**
→ [`R390`](E05_the_space_of_compilers/A24_what_the_definition_costs/R390_does_the_untitled_tier_state_anything)

**And two of the three silent rounds turn out to be infrastructure, not unwritten findings.**
`R150_does_the_veto_do_anything` is read by **four** other places (`R133`, `R173`, `R314` and
`assurance/consistency.py`) and `R144_information_loss` by **two**; `R147_tracking_vs_serving` by
none this instrument can reach. **Marking a consumed round "no finding" would retract work that was
never wrong, and writing one for it would invent a result for a script never asked to produce any** —
so the debt shrinks by two for a *recorded reason* rather than a judgement call. ⭐ **The search's
control has an answer I did not produce here**: two consumption edges committed earlier for a
different purpose — `sat_genericpool16_fresh.npz` → R371 and `r371_power.json` → R372 — both found,
and a filename that exists nowhere returns 0. ⚠ **The blind spot biases toward the flattering
answer**: a consumer building its path dynamically is invisible to a literal search, so R147 is
**`no consumer found`, not `no consumer`**.
→ [`R391`](E05_the_space_of_compilers/A24_what_the_definition_costs/R391_step_or_orphan)

**At corpus scale, 72 of 226 rounds (32%) are consumed as data — and 23 more are only cited.**
R391's detector counted a round as consumed if another source named **either** its artifact **or** its
directory; those are different relations, and naming a directory is often a **prose citation** —
R21's docstring opens *"r15 and r20 both rest on a neighbour arm"*, an argument about those rounds
rather than a read of their output. At n=3 the merge was tolerable; over 226 it would inflate
infrastructure with every literature reference in the corpus. Split: **artifact-consumed 72, name-
mentioned 74, mentioned-but-not-read 23** — and R391's own numbers are corrected (R144 is **1**
artifact consumer, not 2; its conclusion stands, its count did not). ⛔ **The negative control failed
and the reason is a finding**: R391 used `zzq_no_such_artifact_zzq.json` as *its* nowhere-file, so
that string is now **in the corpus** and returned 1 consumer. **A corpus absorbs its own
instruments** — a nowhere-token is only nowhere until a round uses it. ⚠ The blind spot biases the
estimand **downward**, toward *backfill it* — the direction that creates work rather than excuses it.
→ [`R392`](E05_the_space_of_compilers/A24_what_the_definition_costs/R392_how_much_is_infrastructure)

**The verification gate will cost ≥39 minutes at full table — and 80% of that is two rounds.**
R392's NEXT asked whether the gate's cost grows in rounds rather than numbers. ⛔ **It grows in rounds
by construction** — the gate re-runs every cited round, so its cost *is* the sum of those runtimes;
measuring that would have been 1+1=2 reported as a finding. What is not forced is the **sum**, so a
seeded sample of 15 from the **owing** population was timed at a 90 s cap: **13 complete, 2 censored**,
sample total **≥226 s**, projecting **≥39 min** at 154 rows. ⛔ **And a mean over a heavy tail
misdescribes where the cost lives**: the mean is ≥15.1 s but the **median round is 3.4 s**, and the
**two censored rounds contribute 180 s of the 226 s total — 80%**. *A cache buys the tail and almost
nothing else*, which is a far sharper brief than "the gate is slow". ⚠ The projection is a **lower
bound only** — censored draws contribute the cap, not their value, and no upper bound is available at
any budget spendable here. ⭐ The cache's shape is fixed before it is built: **keyed on the round's
source hash**, because *a cache that serves a stale verification is worse than a slow gate — it
certifies without checking.*
→ [`R393`](E05_the_space_of_compilers/A24_what_the_definition_costs/R393_what_the_gate_will_cost)

**The source hash is a valid cache key for the 13 rounds measured — and cannot speak for the tail the
cache exists to serve.** R393's NEXT specified a cache keyed on source hash *"so a changed round
invalidates its own row"*, ⛔ **and never examined the converse**: a hash keys a cache only if an
*unchanged* source yields unchanged numbers, which nothing in Python guarantees. ⛔ **Nor was this
about a future cache** — R388's gate already re-runs every cited round, so a round that moves at fixed
source makes that gate **convict an honest backfill**. Two consecutive runs of each of R393's 13
complete rounds: **13 of 13 stable across 538 numbers**, with an unseeded-rng plant caught and a
constant plant passed, and the gate's own `NUM` regex **imported rather than copied**. ⚠ It was
measured **under concurrent load**, which is *one-directional*: contention can manufacture instability,
never stability, so the omitted guard could only have produced a false UNSTABLE. ⚠ `STABLE` means
*not caught in two draws*, never *deterministic*; ⚠ and the population is **selected toward this
answer** — these are the rounds that finished inside 90 s, loading no model and drawing no samples.
*R393's two censored rounds carry 80% of the gate's cost and are exactly the rounds this design cannot
speak for.*
→ [`R394`](E05_the_space_of_compilers/A24_what_the_definition_costs/R394_is_the_source_hash_a_valid_key)

**A source-level gauge test does discriminate — and it halves the expensive step to one round.**
R394's blind spot was the two censored rounds carrying 80% of the gate's cost. ⛔ The question was
*not* "are they risky": a pattern matching `random` or `time` flags nearly every scientific script,
returns *both are at risk*, and reads as an answer. The prior question is whether such a detector
discriminates at all — ⭐ and **the answer key already existed**, since R394 labelled 13 rounds STABLE
for a different purpose, so every hit among them is a **false positive by construction**. Measured:
**quiet on 10 of 13, false-positive rate 23%**; of the censored pair, **`R114` is quiet and
`R130_judge_gauge` carries one construct — `gpu`**. ⚠ But **6 of the 7 pattern families were never
positively controlled** — only `unseeded_rng` has ever caught a genuinely varying script — so the
`gpu` hit is a **hypothesis, not a detection**, and a quiet round is *unflagged*, never *cleared*.
→ [`R395`](E05_the_space_of_compilers/A24_what_the_definition_costs/R395_can_a_gauge_test_replace_the_rerun)

**The instrument behind the last two findings never read an exit code — and 13 of 13 subjects exited
0 anyway.** ⛔ Writing R396's docstring surfaced the failure it must not commit — *a crash is
byte-identical twice* — and that sentence indicted **R394, committed an hour earlier**: it reads
`stdout + stderr` and **never `returncode`**, so a round that could not run would have matched itself
and been recorded **STABLE**. R393 is worse in the same direction: `COMPLETE` meant *finished inside
90 s*, not *succeeded*. ⛔ **And it propagated** — R395 scored its detector against R394's 13 STABLE
labels as false-positives-by-construction, so a corrupted key would have carried the verdict that
halved the expensive step. ⚠ There was a **named mechanism**, not a generic worry: R393 purged
untracked files between subjects, and the release data under `data/` *is* untracked. **It did not
happen — 13 of 13 exited 0 with no traceback**, so both verdicts stand. The defect is real, remains
uncorrected in those two rounds, and the fix is R396's `UNRUNNABLE_HERE` class going forward rather
than a retroactive excuse.
→ [`R397`](E05_the_space_of_compilers/A24_what_the_definition_costs/R397_did_the_stable_subjects_actually_succeed)

**⛔ "One release" was never a wall — it was a query nobody ran.** The definition's impossibility
register listed `transfer to another release` as needing a second release, and R233's limit is stated
in the strongest terms the document contains: the fresh responses carry no human rankings, so
transport is of the **compilation** and *"never agreement with people"*. **That sentence described
this release and was read as describing the world.** `data/utterances.jsonl` — **68 MB, fetched
2026-07-29, referenced by 0 files in this repository and absent from the dataset card** — holds
**68,371 rows over 8,011 conversations, 100% carrying a human score, with 26,285 prompts having ≥2
distinct model responses across 21 models**. ⛔ This campaign's own failure table predicted the miss
twice — *a wall never checked*, and *nobody asks whether the data has more to give*. ⚠ The round
**computed no core and ran no transport test**: *a second object exists* is the whole claim, and the
corpus has **no rubric**, so clauses defined against `full` still cannot transport. The register row
and the transport section were both corrected, and all five counts were added as gate assertions
(51 → 56).
→ [`R398`](E05_the_space_of_compilers/A24_what_the_definition_costs/R398_is_there_a_second_object_on_disk)

**The second corpus is a RATING corpus — so CoVal's ordering estimand does not transfer, and the field
that does is `if_chosen`.** ⛔ A blocker, not a detail: every clause of the definition is stated
against an **ordering**, and running an ordering test on rating data would rebuild R233's error one
release over. Measured: `score` spans **[1, 100]** and forms a `1..k` permutation in **0.1%** of
interactions → **RATING** (pre-registered: RANKING > 80%, RATING < 20%). ⭐ But the corpus carries
**both** measurements, declared before the run so the round could not pick the convenient one:
**26,886 of 27,151** multi-response interactions (99.0%) have exactly one `if_chosen`, which is a
genuine pairwise preference and structurally closest to a CoVal comparison. **Overlap: 3 CoVal user
turns appear verbatim** (ANY cut, the more sensitive of two reported; LAST cut gives 1) — ⚠ **but two
of the three are `hello` and `hi`**, degenerate collisions rather than shared provenance, so reading
`3` as contamination overstates it 3×. The substantive count is **1**, and all three are cheap to
exclude.
→ [`R399`](E05_the_space_of_compilers/A24_what_the_definition_costs/R399_what_estimand_does_the_second_corpus_admit)

**The two corpora share depth *support* and almost no depth *mass* — a depth-matched transport test
can draw at most 99 pairs.** CoVal is **90.9% single-turn**; the second corpus contains **one**
single-turn conversation and sits at depths 2–4. ⛔ **And my pre-registered threshold was applied to
the wrong quantity**: *"matched pool ≥ 100"* counted second-corpus conversations at shared depths
(**6,935** → `MATCHED`), but a transport test needs **pairs**, so each depth is bounded by the smaller
side — **balanced pool = 99** → `DISJOINT`. The threshold was **not retuned**, it was re-applied
unchanged to the quantity a test can actually draw from, and the override moves toward the **less
convenient** answer. ⚠ 99 vs 100 is a knife-edge, so the composition is the finding, not the verdict
word: **77 of the 99 sit at depth 2**, and **CoVal's modal object — depth 1, 90.9% of its corpus — has
exactly one counterpart.** Transport, if run, would say nothing about the conversations CoVal is
mostly made of.
→ [`R400`](E05_the_space_of_compilers/A24_what_the_definition_costs/R400_is_conversation_depth_a_confound)

**The cross-corpus transport route is closed at n=99; the clause-② route is open by two orders of
magnitude.** ⛔ Priced before building, and the MDE formula is labelled a **DERIVATION** — `ZEFF·sd/√n`
could not have come out otherwise; what is not forced is the **comparison**. Swept over the whole
discordance range, the MDE at n=99 exceeds the largest effect this campaign has measured (**+0.0992**,
R368) in **10 of 12 cells**, crossing at **p_d = 12.4%** — the test would resolve only if two
differently-built criterion sets disagreed on fewer than 12.4% of conversations. ⛔ **But that verdict
is scoped to ONE design**, which I almost failed to notice: n=99 binds a *depth-matched cross-corpus*
test, while **clause ② is an INTRA-corpus comparison that never touches CoVal's sample** — n = **8,011**
conversations or **26,886** interactions, MDE **0.0171** and **0.0094**, both comfortably resolvable.
⚠ They are **different questions**, and neither substitutes for the other. Controls established
floor < threshold < ceiling (n=4 → 0.7674 above every effect; n=10⁶ → 0.00048 below all), and all four
reference effects were **asserted present in `DEFINITION.md`** before use rather than recalled.
→ [`R401`](E05_the_space_of_compilers/A24_what_the_definition_costs/R401_can_n99_resolve_anything)

**The clause-② harness was attacked with judges whose answer was already known — before any GPU was
spent on it.** ⛔ If the first real run is also the first test of the apparatus, a null is
**unattributable**: *"the core has no advantage"* and *"the harness cannot see an advantage"* print the
same string. Driven by three stub judges at 3 seeds over **26,789** interactions (chance floor
**0.4328**): **ORACLE → ABOVE**, **RANDOM → NULL**, **ADVERSARY → BELOW**, and the oracle **stops**
passing when labels are destroyed (**NULL ×3**). ⛔ **ADVERSARY is the arm that matters** — if the
harness took an absolute value anywhere, a systematically *wrong* judge would read as a large
*positive* effect, which ORACLE and RANDOM cannot catch. ⛔ And the arithmetic trap has bite: **that
ORACLE scores 1.0000 is FORCED** and is not reported as a finding; what is not forced is the
inferential layer's classification. ⭐ R399's 3 prompt strings removed **97** interactions, and the
round refuses to proceed if a non-empty filter drops zero rows. ⭐ Free cross-check: this harness's
MDE and R401's independent derivation agree at **0.0094** to four decimals. ⚠ A stub judge's errors are
independent; a real judge's correlate with content — **this validated the harness, never the
experiment.**
→ [`R402`](E05_the_space_of_compilers/A24_what_the_definition_costs/R402_does_the_harness_fire_before_the_judge)

**Half the definition is a fact about CoVal's schema — 3 of 6 clause-parts cannot be SAID on the
second corpus at all.** ⛔ The failure table's remedy is *per clause, name an object it excludes*; this
asks the **prior** question — can the clause be **said** there? A clause whose subject does not exist
is **not satisfied and not violated**: `NOT-STATABLE`, a third value, and folding it into either of
the others manufactures a verdict. **①** (needs the prompt's own rubric), **③b** (*"any half of the
annotators"* — measured: **max 1 rater**, 0 of 27,172 interactions have 2) and **③c** (needs a rubric
those annotators wrote) are all unsayable there. ⛔ **CoVal's column is a positive control, not a
finding** — the definition was written from CoVal, so any `NOT-STATABLE` there would have meant the
detector was broken, and the round exits 1 on that. **Clause ① is now doubly hollow**: already
`DERIVED` vacuous where it was born, and unsayable off that object. ⭐ **What survives is exactly the
load-bearing pair — ③a and ②**, powered at n=26,789 (R401) with a validated harness (R402). ⚠ **No
clause is restated here**: rewriting one so it survives on a new corpus is an act of *definition*, and
doing it in the same breath as the diagnosis is how a definition gets tuned to whatever object is in
front of it.
→ [`R403`](E05_the_space_of_compilers/A24_what_the_definition_costs/R403_which_clauses_are_even_statable_elsewhere)

**Clause ③ is not one clause: ③a does all the work, ③b does none, and ③c is not implemented — and
enforcing it as written admits only the object the definition was written from.** Decomposed against
`corebench/select_core.py`'s rule dispatch rather than the arm names: **③a excludes 4**, **③b excludes
3 — but 0 beyond ③a** (every `_fit1` arm already reads the rankings), **③c excludes 13**, of which
**4 are among the 5 currently admitted**. The nested admitted sets run **9 → 5 → 5 → 1**, and that
final **1** is `coval_core` itself. ⛔ **So the definition sits between two failures**: *as implemented*
③c does no work and R363's `W_CHANNEL_OPEN` stands, so arms are admitted that the text forbids; *as
written* it admits only its own instance. **Neither is a definition of a category** — the *"definition
describes the instance"* failure, measured rather than suspected. ⭐ The key-reproduction control
**caught a real bug in my own parser** (a lazy regex ate the `_k`, so the derived set came back empty
and the round exited 1); the parser was fixed rather than the control relaxed, and the derived key
then matched the one hand-written in four rounds. ⚠ Counts are a **lower bound**, and whether ③c
*should* be enforced is an act of definition, not decided here.
→ [`R404`](E05_the_space_of_compilers/A24_what_the_definition_costs/R404_which_conjunct_of_clause_three_does_the_work)

**`UNVERIFIED` — there is no "strictest reading", and the round that assumed there was failed its own
control.** Composing R360's committed 45-cell reference sweep with clause ③a gives a curve running
**9 → 0**, and at the top cell the only arms surviving clause ② are **exactly the four that read the
labels**, so ②∧③a is empty there. ⛔ **But the MONOTONE control FAILED**: `pct 75 (n=5)` → `pct 80
(n=6)`, gaining **`generic`** — a blind set. A percentile that can *gain* arms as it rises is not a
strictness ordering, so the top cell is **not "the strictest reading", merely the last one**, and
reporting the emptiness as a verdict would be printing a headline while a control above says the
round is unreadable. ⭐ **And the failure explains a standing disagreement**: R327's universal reading
admits `{coval_core}` using the best **held-out** of 1,820, while this sweep uses the **in-sample**
maximum and admits nothing — *a third under-specification*, named in neither round and decided by no
sentence of the definition. ⛔ The phenomenon is already recorded (*"stronger references admit blind
sets again"*); the **consequence** — that clause ②'s strictest reading is ill-defined — is not. This
round writes **nothing** into `DEFINITION.md`: an UNVERIFIED round has not earned a line in it.
→ [`R405`](E05_the_space_of_compilers/A24_what_the_definition_costs/R405_at_its_own_strictest_reading_the_definition_admits_nothing)

**"Better than EVERY prompt-blind set" was tested against the 99th percentile — and the universal
reading of clause ② has never been run.** ⛔ R405's NEXT said this needed a run; **it did not.** R331
had committed the blind distribution's order statistics — including `max` — over the same 1,820
subsets, and R327 had committed the reference it used: two rounds, neither citing the other, both
numbers already on disk. R327's reading A used `0.5546019830`, the best **held-out**; the **maximum**
is `0.5574753088`; the gap is **`+0.0028733259`**, and the reference brackets **below p99** — between
**1% and 10%** of subsets beat the bar the word *every* was tested against *(a bracket, not a count:
R331 stored seven order statistics, not 1,820 scores)*. ⭐ **This resolves R405's disagreement
exactly**: `coval_core` clears a p99 bar and does not clear the maximum, and that `0.0029` decides
whether the definition admits its own instance or nothing. ⚠ **The unit discipline is the point** —
the claim's unit was *the maximum*, the instrument's was *the best held-out*, and **no control in R327
could have caught it**, because its controls all concerned the **ordering** of its readings, and an
ordering can be perfectly correct while every rung is mislabelled. ⚠ R327 is **not** retracted; the
**name of one rung** is.
→ [`R406`](E05_the_space_of_compilers/A24_what_the_definition_costs/R406_the_universal_reading_was_not_universal)

**At the maximum prompt-blind set, the only arms admitted are the four that read the prompt's own
rankings — label-free admitted: 0.** ⛔ R405 blocked the *ordering* claim correctly and blocked a
weaker one with it: *"no label-free arm beats the maximum blind set of its own size"* is a statement
about **one cell**, needing only that the cell's reference **be** that maximum — **no monotonicity is
used anywhere in this round.** Verified from source rather than assumed: `ref_at(k, 100)` sorts blind
sets of size *k* and returns `order[-1]`. ⭐ **Per-arm brackets, reported at arm resolution for the
first time**: `topw_k8` 95.0 · `topw_k3` 95.5 · `topw_k4` 98.0 · **`coval_core` 99.5** · `topw_k6`
99.5 · the label-readers 100.0 — **the released core clears the 99.5th-percentile blind set and not
the maximum**. ⛔ **And this answers a test the sentence does not contain**: the code requires
*significantly* better (`e > 0 AND |e| ≥ ZEFF·se`) while the definition says *scores better than* —
stricter, in the flattering direction, and **the literal `e > 0` reading has never been run**. That is
clause ②'s **fourth** under-specification, after the missing member, held-out vs in-sample, and the
p99 bar called *every*. ⚠ One numeric cross-check is recorded **OWED**, not quietly skipped.
→ [`R407`](E05_the_space_of_compilers/A24_what_the_definition_costs/R407_the_universal_reading_answered_without_an_ordering)

**Read literally, clause ② admits all five label-free arms at the universal reference — and every one
of them by a margin inside its own noise.** The clause says *scores better than*; the code says
`e > 0 AND |e| ≥ ZEFF·se`. Run both at the per-k maximum blind set: **STRICT admits 0 label-free arms,
LITERAL admits 5** — `coval_core` at **`+0.009002`** against `se = 0.003703`, **0.87 of its own
significance bar**, the others 0.38–0.81. **The four label-reading arms reach 3.4×–6.7×.** ⛔ So
**R407's emptiness was partly an artifact of a significance term the definition does not contain** —
but the honest report is *not* that a core was found: it is that **the definition as written has no
error control**, and the order-of-magnitude gap between label-free and label-reading arms is exactly
what that term was separating. ⭐ **The re-implementation was the risk and was controlled before use**:
the scoring layer is **imported** from the module R360 itself uses, and my strict variant had to
reproduce R360's committed `p=100` cell **arm for arm** before any literal number was admissible — it
did. `literal ⊇ strict` is **forced**, so it is asserted as a sanity check and **not** reported as a
finding. ⚠ One release; an unguarded positive mean is the quantity least likely to survive a second.
→ [`R408`](E05_the_space_of_compilers/A24_what_the_definition_costs/R408_the_literal_test_at_the_universal_reference)

**The ordering of the five carries information — but it is roughly two facts, not five, and the
verdict cleared its own threshold by 1.7 points.** ⛔ R408's NEXT proposed testing the ordering across
judge and metric; **that is a claim with no control**, and it presupposes the ordering is
distinguishable from noise on the data that produced it — with effects spanning `+0.0041…+0.0090` at
`se ≈ 0.0037`, the pairwise gaps are one arm's uncertainty wide. Cluster-bootstrapped over prompts
(B=2,000, 3 seeds): **`coval_core` holds rank 1 in 51.7%–53.2%** against a 20% coin, and `topw_k3`
sits **last** in 53%. ⚠ The pre-registered line was **≥0.50** — at 0.55 this would have read PARTIAL,
and that is stated rather than left to be noticed. ⭐ **The rank matrix says more than the verdict**:
the extremes are separable, the middle is a smear (`topw_k4`/`topw_k8` spread over ranks 2–5, no mode
above 0.33), and *"the released core is the best label-free arm"* is barely better than a coin flip
against `topw_k6` (0.53 vs 0.32). **The honest summary is a partial order.** Controls:
`oracle_k4` ranks first in **100%** of resamples (without it a uniform result could not be told from a
blind bootstrap), and two identical objects split **0.480/0.520**. ⚠ Cross-judge stability is
**structurally unavailable** — at 0.8B nothing is admitted at any safe reference.
→ [`R409`](E05_the_space_of_compilers/A24_what_the_definition_costs/R409_is_the_ordering_of_the_five_information)

**Neither size nor provenance is resolvable — the partial order has no decomposition this design can
reach.** ⛔ R409's NEXT asserted *"size alone cannot explain it"*; **one fact settles that as a
DERIVATION** — `coval_core` and `topw_k4` are both k=4 and land in different tiers, and a function of
k alone cannot map one input to two outputs. The release then offers a clean 2-factor split: `topw_k*`
varies **size** with provenance pinned, and at k=4 `coval_core` vs `topw_k4` varies **provenance** with
size pinned. ⭐ At matched size the reference **cancels exactly** (`2.8e-17`), so it is *not* a
difference of two differences. **Result: all three adjacent-k CIs straddle zero, and
`coval_core − topw_k4 = +0.0023` against its own MDE of `0.0085` — 0.27 of its resolution. Nothing
survives Holm; nothing is close even raw** (smallest p 0.147). Controls: `oracle_k4 − topw_k4` = **+0.0641**,
~28× the contrasts of interest; an arm minus itself is **exactly** 0.0; analytic and bootstrap CIs
agree to ~3e-4. ⚠ **This downgrades R409's own summary** — its partial order describes bootstrap rank
frequencies, not an established ordering, and R409's README is annotated in place.
→ [`R410`](E05_the_space_of_compilers/A24_what_the_definition_costs/R410_size_and_provenance_decomposed)

**The naive comparison said 0.96×; standardised it is 2.50× or 4.57×, and the clustering unit decides
which.** ⛔ R410's NEXT set `+0.009` beside R401's MDE of `0.0094` and read *marginal* — **but the
first is in CoVal's A2-agreement units and the second in `if_chosen` accuracy units against a chance
floor of 0.4328.** That is comparing a length to a mass because both print as four decimals, and it
was my own sentence. Standardised (`d = e/sd = 0.07814`, resolution `ZEFF/√n`): **4.57× at n=26,789
interactions, 2.50× at n=8,011 conversations.** ⭐ **The real finding is that the clustering unit
decides the answer** — same effect, same design, and the only difference is whether the independent
unit is the interaction or the conversation (≈3.4 per conversation). *Nobody has measured the
within-conversation correlation, so the power statement is a range.* ⛔ **The gauge control failed for
its own reasons and the control was fixed, not the criterion**: uncentred noise moved the signal as
well as the dispersion — two changes, one question — so it was **centred**, with the uncentred version
kept beside it over 200 replicates to show the repair is to the manipulation. ⚠ Conditional on a
transport assumption that no object on this box can validate.
→ [`R411`](E05_the_space_of_compilers/A24_what_the_definition_costs/R411_are_the_two_effects_even_commensurable)

**The winning model is constant within a conversation, so the conversation is the unit and the
replication is marginal at 2.47×.** Measured: **`P(same winner | same conversation) = 1.0000`** over
43,735 within-pairs, against **0.0557** across conversations. **The effective n is ≈7,822, not
26,789** — a factor of 3.4 that separates a powered experiment from a marginal one. ⛔ **Two errors of
mine caught here.** R411's NEXT named a quantity that **needs the judge** (the outcome's own ICC) —
the third consecutive closing sentence of mine with an unexamined step. And my first model proxy was
**a check that could not fail in the null direction**, returning exactly `0.0000`: I scored each
interaction against **its own conversation's modal winner**, a label defined *within* the group, which
removes between-group variance by construction. **The proxy was replaced, not the criterion.**
⛔ **And R411's "range" was already the whole range** — `DEFF = 1+(m̄−1)·ICC` makes 4.57× and 2.47×
exactly the ICC=0 and ICC=1 cases, a derivation I missed while writing it. ⚠ R402's README is
annotated: its **controls stand**, but any power claim on its n must use 7,822.
→ [`R412`](E05_the_space_of_compilers/A24_what_the_definition_costs/R412_the_clustering_that_decides_the_power)

**Score offers no escape — the corpus is conversation-limited whatever outcome I target, and ~8,000 is
the ceiling.** ⛔ R412's NEXT proposed re-scoping onto `score` because its raw levels cluster at only
0.1978. But **a clause-② test consumes an ORDERING**, and the ordering is conversation-constant too:
**κ(argmax model) = 1.0000** over 37,973 pairs, and `argmax(score)` agrees with `if_chosen` **99.47%**
of the time — score changes the label, not the information. ⚠ **And my own cancellation derivation
failed in the data**: I argued a within-interaction contrast subtracts a conversation-level offset
exactly, as R410 verified at 2.8e-17 — but the **gap's ICC came out 0.2383, *above* the raw levels'
0.1978.** Differencing hurt. *The derivation assumed a purely additive offset; the data is not purely
additive, and it was labelled a derivation before the run.* Implied power: `if_chosen` 2.47×,
score-ordering **2.51×**, against an unreachable ICC=0 ideal of 4.57×. **The second corpus cannot
power the replication at any outcome choice** — a dead end found for one round's cost, which is the
cheapest way to find one. ⭐ Controls include a **cross-round reproduction** (my κ instrument returns
R412's committed 1.0000) and **1,579 tied-top interactions excluded rather than broken by array
order**.
→ [`R413`](E05_the_space_of_compilers/A24_what_the_definition_costs/R413_does_score_escape_the_clustering)

**`UNVERIFIED` — the second judge cannot rank, and an escape hatch in my own kill nearly published a
false retraction.** R413's NEXT noted that *"at 0.8B nothing is admitted"* is a **binary** verdict
about admission, leaving the **continuous** effect unexamined — and the 0.8B scores were already on
disk, so a cross-model replication cost no GPU. Computed: `coval_core` at 0.8B is **−0.0188**, a sign
flip against the committed **+0.0090** at 2B. ⛔ **But the instrument control fails**: `full` — the
complete rubric, the target's own source — scores **−0.0558** against the blind maximum. **A judge
that ranks the rubric below a random blind draw cannot host any comparison**, so the negative is
silence about the core and a statement about the judge. ⛔ **And the hole was mine**: my pre-registered
kill read *"(oracle_positive_at_08b **if oracle usable**)"*, and when the two 0.8B naming families
turned out not to be the same run, that condition simply evaporated. **Without the repair this would
have published `W-SIGN-FLIP` — a false retraction, the most expensive kind of error, because nobody
re-examines a withdrawn claim.** ⭐ The repair used `full`, an arm inside the same family, and is
explicitly **weaker than an oracle**: it bounds *can this judge rank*, not *can it detect leakage*.
**R408's +0.009 is untouched — the attack was ruled inadmissible, not answered.**
→ [`R414`](E05_the_space_of_compilers/A24_what_the_definition_costs/R414_does_the_effect_replicate_at_the_second_judge)

**Re-running the same arm at the same judge shifts its mean by 13× the effect the campaign has been
chasing — and §1 has required this measurement all along.** ⭐ *"NOISE FLOOR: measured, not assumed.
Replicates beat models."* **The replicates were on disk the whole time**: five `_08bR` pairs — R for
**re-run** — same arm, same judge, same code, both committed. Surfaced by the git history, whose
commit for those files is titled *"a committed artifact in this repo is not a function of its
committed code"* — **a prior round had already said it and nothing downstream acted on it.** Measured:
run-to-run shifts in mean A2 of **−0.116, −0.098, −0.034, +0.022, +0.023**, worst **0.116489** against
R408's **+0.009002** — **13×**. ⛔ **My first comparison used the wrong units** (a mean beside a
per-prompt spread); the sd column is kept because *dropping a column after seeing it is how a table
becomes an argument*. ⚠ **The cause is not separated**: 0.1 is large for kernel non-determinism, so
either the pipeline is wildly unstable **or** two configurations share a filename — **both disqualify
these as replicates, and neither branch is claimed** (it also explains R414's family split). ⚠ **No
re-run pair exists at 2B**, so the correct statement is not *"R408's effect is inside the noise"* — it
is that **every 2B number this session produced rests on an assumption of pipeline stability that has
now failed at the only judge where it could be checked.**
→ [`R415`](E05_the_space_of_compilers/A24_what_the_definition_costs/R415_the_pipelines_own_noise_floor)

**R415's "re-run pairs" scored DIFFERENT criteria — its framing was wrong one round after I published
it.** ⛔ R415 called them *"same arm, same judge, **same code**, different run"* and offered a
disjunction: *the pipeline is wildly unstable* **or** *two configurations share a filename*. **Each arm
has a committed core JSON, and all 5 pairs differ — criteria changed on 91.1%–99.6% of prompts.** Not
whitespace: a near-total re-selection. **The second branch was true, checkable against committed files
in one line, and I listed it without testing it.** **SURVIVES**: the magnitude (0.116489, still 13× the
effect), that these files are **not** usable as replicates — now *established* rather than disjunctive
— and that the **2B floor remains UNMEASURED**. **DOWNGRADED**: *"the pipeline is wildly unstable"* is
**not supported**; the shift is fully compatible with different criteria and no scoring instability at
all. ⚠ **Ruling out one branch's evidence is not evidence for the other** — this does not show the
pipeline is stable, only that R415's measurement never bore on it. R415's README and `DEFINITION.md`
are corrected in place.
→ [`R416`](E05_the_space_of_compilers/A24_what_the_definition_costs/R416_the_rerun_pairs_are_not_scoring_replicates)

**The judge has no stochastic step, so the 0.116 was never scoring noise — and the GPU re-score both
prior rounds proposed is not needed.** ⭐ **Rung 1 of the attack ladder**: *"gauge test, 3 lines, zero
compute… cheapest kill available, always try first."* The transformation is **re-running**, and
whether the output *can* differ under it is a property of the scoring path — **readable from source**.
Scanned `Judge.score` and its call site for `do_sample` / `temperature` / `top_p` / `top_k` /
`.generate(` / `multinomial`: **NONE**. The judge is, in its own words, *"scored not generated: one
forward pass per pair"*, under `@torch.inference_mode()`, reading `sigmoid(logits[yes] − logits[no])`.
⛔ So **R415's 0.116489 cannot be sampling noise**, and **R416's residual is `selection vs
CONFIGURATION`, not `selection vs scoring noise`** — a configuration difference is not a noise floor.
**R415 measured, R416 corrected the measurement, and both proposed a GPU re-score before anyone read
the twenty lines that answer it.** ⚠ Against my own conclusion: a source scan **bounds what CAN vary,
it does not measure what DOES** — this is an inference, and the verdict is about *admissibility* and
*whether to spend the GPU*, not a measured floor; and the committed `.npz` files carry **no batch
field**, so batch equality is **unrecoverable** and is the most likely non-stochastic explanation left
standing.
→ [`R417`](E05_the_space_of_compilers/A24_what_the_definition_costs/R417_the_judge_has_no_stochastic_step)

**R396 landed after 1h50m on the GPU: the expensive round does NOT reproduce at unchanged source —
and R418 shows none of the 12 differing tokens is a claim.** R396 ran `R130_judge_gauge` twice, both
exiting 0 (so `DIFFER` is a real difference, not two identical crashes), and found **140 numbers per
run, DIFFERING**. ⛔ **I then guessed the cause twice in a report and was wrong twice** — *"timings"*
(R130 prints none) and *"tqdm rates"* (no tqdm anywhere in the path). **Two hypotheses, two
refutations, zero measurements.** So R418 asked the question that **needs no cause**: R130 prints its
claims as `0.dddd` (`mean_sat`/`core`/`full_eq` at `:.4f`), and **0 of the 12 differing tokens has
that shape.** ⭐ **R396's operational conclusion survives and its stated cause does not**: R388's gate
uses the same extractor over `stdout+stderr`, so it **would** convict an honest backfill — but on
**non-claim tokens while the claims were identical**. **The fix inverts: narrow the extractor, rather
than exclude scoring rounds from verification.** ⚠ R418's emission control matters — R130 must
*actually* print `:.4f` values, or *"no claim-shaped token differed"* would be vacuous. ⚠ And the
**origin of the other tokens is still unknown; I am not guessing a third time** — R396 did not persist
its captured outputs, which was my omission in its design.
→ [`R418`](E05_the_space_of_compilers/A24_what_the_definition_costs/R418_what_differed_was_not_the_claims)

**The scoring-only floor is EXACTLY ZERO — bitwise identical on all 200 prompts — which locates
R415's 0.116489 entirely in SELECTION.** ⭐ `--core coval_core` reads criteria deterministically from
the rubric, so two runs share them **by construction**, and the provenance field added two rounds ago
**proves** it: both artifacts carry `criteria_sha256 = d9a198b6…` over **3,828 criteria**, 3,168 judge
calls each. Measured: mean, sd and **max |difference| all `0.000000000`.** ⛔ **Four rounds resolve at
once**: R415's number was a *rule-level* floor, R416 found the criteria differed on 91–99.6%, R417
*inferred* from source that scoring adds nothing — **and this promotes that inference to a
measurement.** **Every A2 figure in `DEFINITION.md` is a fixed quantity given its criteria.** ⛔ **An
override was available and was not taken**: the first `B` run carried a different `producer_sha256`,
differing only in *where a hash is computed* — provably untouchable by a score — so waiving the
pre-registered pair check was defensible. **B was re-run instead, at a cost of one minute**, because a
rule written one turn earlier should not be bent when honouring it is cheap. ⚠ Scope is now
*statable* rather than guessed: **batch 32, one judge, 200 prompts** — exactly what the provenance
field makes expressible and what could not have been said three rounds ago.
→ [`R419`](E05_the_space_of_compilers/A24_what_the_definition_costs/R419_the_scoring_only_floor_measured)

**Selection is deterministic too — so there was never any instability to find.** `select_core.py`
holds **0 unseeded stochastic constructs** (its one RNG is `default_rng(a.seed)`, which is
determinism), and two invocations with identical arguments emit **byte-identical criteria, 0.0% of
prompts changed**. ⭐ **Source and behaviour agree, which neither establishes alone** — and unlike
R417, which had to stop at a scan because scoring needs the GPU, **selection is CPU-only so rung 1 and
the real test both fit.** ⛔ **The contradiction this resolves**: scoring is deterministic (R419,
measured bitwise) and selection is deterministic (here), so the pipeline is deterministic **given its
inputs** — yet R416 measured the `_08b`/`_08bR` criteria differing on **91–99.6%** of prompts. **Two
deterministic stages cannot do that from the same inputs.** So those files are **two different
CONFIGURATIONS, not two draws**, and R415's `0.116489` is a **between-configuration difference, not a
noise floor of anything.** ⚠ That is now the *remaining* explanation, **not a demonstrated one** —
those two files record no inputs, which is exactly the gap the provenance field closes going forward
and cannot close retroactively.
→ [`R420`](E05_the_space_of_compilers/A24_what_the_definition_costs/R420_is_selection_deterministic_too)

**All three label-reading rules are deterministic — and the run reproduces `_08b` exactly, naming
which file of R415's pair diverged.** ⛔ **First, the gap in R420 I should have caught inside it**: it
reported *"identical"* and **was never shown able to report anything else** — a hash check that always
returns equal would have produced exactly its output. *The ledger's oldest row, run five rounds after
I wrote that sentence into three other rounds.* The control costs one run: `random_k` at seeds 0 vs 1
**must** differ, and the comparison **detects it** — so **R420 is licensed retroactively; it was
correct and it was unsupported, and those are different things.** Then `oracle_k`, `greedy_k` and
`indep_k` each emit **byte-identical** criteria across two invocations. ⭐ **And today's deterministic
`oracle_k` hashes `22c61b3aefbe6550` — matching `core_oracle_k4_08b.json` exactly and NOT `_08bR`.**
⛔ ~~So `_08b` is what the pipeline deterministically produces and **`_08bR` is the outlier**, made
with different inputs.~~ **RETRACTED 2026-08-04 by R422–R424.** The hash match is real; *"outlier"*
was not measured, and it is false. **No remaining mechanism inside the pipeline can produce R415's
divergence.**
→ [`R421`](E05_the_space_of_compilers/A24_what_the_definition_costs/R421_the_last_three_rules_and_the_control_R420_lacked)

⭐ **Neither file is an outlier: they are the two arms of a frozen-vs-rebuilt selection experiment
under a SECOND, UNIDENTIFIED judge — and every claim resting on an `_08b` arm is
instrument-UNKNOWN.**  ⛔ *(the `instrument-UNKNOWN` half is RETRACTED by R426 — see below; the
frozen-vs-rebuilt finding stands.)* Reading the sat halves that R420/R421 emitted and never hashed, with the join
repaired to a **set-valued** key (`meta`'s index is a *position*, and **82 of 968 prompts repeat a
criterion text**), across the **five** committed pairs: the two families agree **with each other** at
`≤ 0.03%` disjoint (0/0/1/0/2 of 7,044–8,180 cells), and **both are ~96% absent from the default
judge's own table** — anchored by that table containing `topw_k4` at **`1.0000` (15,440 of 15,440)**
and `_08b` at **`0.0380` (587 of 15,448)**. Every committed table in the repo was tested; the two
other instruments score `0.0056` and `0.0000`. ⛔ ~~**The emitter is not on disk.**~~ **RETRACTED the
same day by R426: `sat08_full.npz` contains both families at `1.0000` (15,448 of 15,448 and 15,460 of
15,460) while containing `topw_k4` at `0.0369` — the exact mirror of the default table's pattern, and
the emitter's signature.** R424's candidate loop read `if ".venv" in p.parts or p.parent == RES:
continue`, so it skipped **`corebench/results` entirely — 106 files, 4 of them full-shaped.** *The
wall was not measured; it was constructed by one line I wrote to keep the arms out of their own
candidate set.* **The instrument is `Qwen3.5-0.8B-Base`, named in committed source at
`R290/run.py:58`** — evidence of a different kind from containment, and conflating the two is what
produced the wall. Given `select_core.py`
makes **zero judge calls**, criteria identical to a default run *plus* foreign values force
`--select-npz default --full-npz <foreign>` — the tool's own documented *"freeze the selection to
re-score a fixed criterion set"* — while `_08bR`'s 91–99.6% different criteria at the *same* foreign
values force the rule re-run under that judge. **`R` is `rebuilt`, not `wrong`.** ⚠ **74 `_08b`
artifacts, 30 rounds cite them.** ⛔ ~~Their instrument is *unknown*, which is worse than *other*.~~
**RETRACTED by R426:** the emitter is `sat08_full.npz` (`1.0000` containment, both families), and
`R290/run.py:58` names the model `Qwen3.5-0.8B-Base`. **The suffix meant exactly what it said.**
→ [`R424`](E05_the_space_of_compilers/A24_what_the_definition_costs/R424_name_the_foreign_emitter)

**And the surface where those errors actually live is now gated.** R366 measured the cost — five of
nine consecutive rounds corrected a claim published within the previous three — so the obvious move
was a causal-clause gate on `DEFINITION.md`. **Measuring first killed that:** 80 units, **5** tight
causal connectives, every one a derivation already citing its round, *because that document is
gated*. The errors live in commit **`NEXT:` blocks**, which nothing checked — **7 of 40** stated a
causal claim with no round citation, including both sentences R366 refuted.
[`next_gradient_labels_its_hypotheses.py`](assurance/next_gradient_labels_its_hypotheses.py)
enforces **labelling, never correctness**: a causal claim in a NEXT block must cite a round or be
marked `HYPOTHESIS`/`UNTESTED`. ⛔ **Its first positive control failed for exactly the right
reason** — `5422ffa`'s block says *"or marked UNTESTED"* as **subject matter**, and the gate read
that as a label on its own claim, excusing the very commit it was built from. **A label is a form,
not a mentioned word.** Attacked five ways (new offender · frozen list emptied · frozen entry
silently fixed · detector neutered · no NEXT blocks → exit 2), and **the suite rejected my first
registration** (23/24) because `hide_rounds` doesn't touch commit messages — a pass for the wrong
reason. Suite now **24/24**, frozen debt **12**.

**⭐ And the definition is now stated once, in one place, with a gate holding it to the record.**
[`E05/DEFINITION.md`](E05_the_space_of_compilers/DEFINITION.md) — `FORMULATION.md` is 2,389 lines of
accreted evidence, is titled *"stated once"*, and **opens with a correction**; the statement had
never been separated from its history. The definition it now carries: a core is a small criterion
set, producible from the conversation alone, that **uses no information from that prompt's own human
labels** (③, and the wording must say *from the PROMPT*, not *from the construction* — R295) **and**
scores better **under a named judge J** than a size-matched prompt-blind set (②). **Clause ① is
stated as a consequence, not a test.** Size is **a bound, not a number**: more than one, 3–8
indistinguishable. Ten quantitative claims in it are re-derived from committed artifacts on every run
by [`definition_matches_the_record.py`](assurance/definition_matches_the_record.py) — **attacked five
ways before being trusted**: a mutated number → caught; a reworded claim the pattern can no longer
find → caught, because a claim that vanished is not a pass; the document deleted → exit 2; the
artifacts hidden → exit 2; and the comparison neutered to always agree → **its own positive control
fails it**, which works only because the control calls the function the gate rules with rather than
restating it. **That last hole was created by the first fix.** Suite now **23/23** on an empty
population.

**Three statements about the published reference, not four — and I had been counting one of them
twice.** They are also not one finding arriving by three routes, which is what I expected to find:
R331 measures a **rate** (`rate(R294 ref) > 0` → 3 of 1,820 at k=4), R332 compares **levels**
(`r294_a2 < closure_a2`, at 7 of 9 resolvable k), and R355 shows those two predicates are **not
equivalent** — they agree on this release but the non-monotone rate lets them come apart. R354 is a
third quantity entirely: which **arms** are admitted, over a different population. The "fourth
independent statement" I named in a commit body was **R332's own table column** — R332 counted twice.

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
