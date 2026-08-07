# CoVal Crossroads

An independent audit of [OpenAI's CoVal release](https://huggingface.co/datasets/openai/coval) — a
dataset in which ~1,000 people from 19 countries ranked four candidate assistant responses to
contentious prompts, *and wrote down the criteria they judged by*.

The release ships prompts, four responses each, crowd-written rubrics and 18,384 rankings — but
**not** the criterion-by-response satisfaction labels, so its own scoring cannot be reproduced from
it. This repository rebuilds that layer locally and then asks what the rubric measures.

**1,018 rounds · 28 arcs · 5 epochs · highest id R1048 · 1772 commits.**
Derived from the tree by [`R995`](E05_the_space_of_compilers/A27_is_the_bar_resolvable/R995_the_readme_head_was_570_rounds_stale/),
never typed.

> ⚠ **Only those five numbers are gate-derived.** Every other figure in this file is a QUOTE of what
> was true when some round measured it, carrying that round's id. Treat an unattributed number as of
> unknown vintage.
>
> ⛔ **The round that measures this head's staleness could not notice it being fixed, and that was
> found by rewriting the head.** `R995` compared the tree against `{"rounds": 415, "arcs": 24,
> "epochs": 5, "highest": 421}` — **written as literals in its source.** So it reported the same gap
> forever, against a head that had already stopped saying any of it: a snapshot wearing a gate's
> clothes. It now PARSES the five numbers above, and exits 2 if the head declares none, because an
> unparseable head is not a current one.
> ⭐ **A gate that hard-codes what it is auditing can only ever fire once.** Its second run is
> theatre, and nothing distinguishes the two from the outside.
>
> ⚠ **This rewrite made one debt worse, and it is not hidden.** Moving the long narrative to
> git history took 115 round mentions out of this file: `every_round_reaches_the_readme` goes from
> **861 to 976 unmentioned of 1,019**. That gate was already RED and is now redder. The trade was
> deliberate — a 1,769-line document whose first 57 lines were an apology is not read, and an
> unread findings index has a mention count and no reader — but it is a cost, not a saving.

---
## The definition, as it stands

⭐ **This is the deliverable.** The full annotated statement, with every clause's scope, lives in
[`E05_the_space_of_compilers/DEFINITION.md`](E05_the_space_of_compilers/DEFINITION.md) — **one home
per fact**, so nothing below restates the clause text.

> An arm is a **CORE** iff
> **②′** it **resolvably beats at least `q`% of the certified prompt-blind comparator family**
> — the 2.5th percentile of the bootstrapped paired difference is > 0 against that share,
> computed on the prompts the arm **actually covers** and never on imputed values (R1024),
> for a **declared `q`**, defaulting to **q = 90** — the only scale-free quantile whose
> false-admission rate reaches nominal (R1038); q=100 is excluded, the max never
> stabilises (R1036) — **and**
> **③** it **consumes no prompt-specific human labels**.
>
> **Reported, never required:** its **size**, and its **margin over a declared response-only class**
> as a lower bound with its interval.

**Its extension on this release, under the A2 target: 9 arms, 4 distinct objects** —
`coval_core`, `topw_k3`, `topw_k4` (with two deterministic twins), `topw_k6`, `topw_k8`.

⚠ **The target is part of the number.** R288's committed sweep found **four distinct admitted sets
across six targets** — `A1` admits **nothing**, `top1·mean` admits `topw_k4` and **not** the released
core (R1019). Every figure here is A2's.

### What it costs, and what it does not do

| | |
|---|---|
| both conditions **bind** | ② removes 64/61 arms nothing else removes; ③ removes 15/16 (R1004) |
| the **instance is admitted** | under both comparators (R1000) |
| it is **stable** where the release has the prompts | median churn **0** at N ≥ 484; at N = 242 one seed collapses it to **0 arms** (R1004) |
| ⛔ it **does not single out the instance** | 5 of 6 admitted arms are **not resolvably ordered** against `coval_core`; only `topw_k8` is (R1011) |
| ⛔ it is **not validated** | the release ships **no external standard** — its own card calls core *"a proof of concept … an invitation"* |

### Every route to a further clause is closed

| candidate | why it is dead |
|---|---|
| **size · size residual · size variability** | the sham shares them — `coval_core` 43, `coval_core_sham` **43** (R1013) |
| **vocabulary · length · within-set redundancy** | the instance's sham is an **exact derangement** of its own criterion sets, so every text-only property is identical by construction (R1014) |
| **discriminativeness** (the one quantity that *does* separate) | **post-hoc** (R1015) · measures **belonging, not merit** — random draws from the prompt's own pool sit at chance (R1016) · **evaluable for 4.2% of candidates** and **implied by ②** where it is (R1017) |
| **clause ④ as a filter** | vacuous or empty at **every** setting; its class is **not closed** (R1002, R1003) |
| **clause ①** | 0 unique removals — and that was **already in this document** before R1000 restated it (R1010) |

### What was retracted

**R1005's convergence (Δ = +0.0828)** — withdrawn by **R1007** on the negative control R1005 declared
in its own docstring and never implemented. Full account in
[`RETRACTIONS.md`](RETRACTIONS.md).

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
| The reliability shortfall against 0.707 is **CONSISTENT WITH a TIE-HANDLING artifact** — and is **NOT an identification**: several methods can share a value and the original method is unrecoverable, so this cannot show the original used it | the baseline reaches **0.6732** (**-0.0338**); counting tied pairs as 0.5 reaches **0.7040** (**-0.0030**) — the only arm landing within 0.01 of the target — while dropping ties gives **0.6745** and raising the rater floor to 12 gives **0.6933** on **784** prompts. Split-half **0.6667** → **0.6978** across the same swap | [r101](E03_the_instrument_was_the_object/A11_how_wide_every_interval_really_is/R101_reliability_offset) |
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
| The card's "highly rated" claim | **UNVERIFIED**, not refuted — selection is rating-*sensitive*, not rating-*ordered* (3.0→10.1% survival across weight bands), but raw-clustered crosses zero while stratified-clustered excludes it and the quartiles are non-monotonic, so **the specification curve does not survive its grid** | [r171](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R171_card_vs_artefact), [r181](E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary/R181_whose_criteria_survive) |
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

---

## What it cost

**1,339 entries in [`RETRACTIONS.md`](RETRACTIONS.md)**, each naming what killed it — the claim
graph refuses a retraction that names no killer. That file is the home; this section is the
compression, and the long-form narrative that used to live here is in
git history — `git show a8de100a:README.md` — and a local convenience copy in `_archive/`.
⚠ **`_archive/` is gitignored**, so on a fresh clone the git object is the only copy. Naming a
path that does not survive cloning is how an archive silently becomes a deletion.

⛔ **A count of retractions is not an achievement, and reporting it as one inverts the objective.**
Zero output has zero false claims. Rigour is the floor a deliverable clears, not the deliverable.
What this section owes a reader is therefore not the size of the ledger but **whether 1,339 entries
are one error repeated or many** — and the honest answer is that they are mostly a few shapes.

| shape, and it is the same shape each time | entries whose HEADING says so |
|---|---:|
| a control that could not reach the branch it was certifying, or whose null was degenerate | 158 |
| a population that was empty, wrong, or narrower than the sentence it licensed | 101 |
| a proxy read in the direction it cannot support | 31 |
| staleness: a fixed anchor evaluated inside a sliding window | 18 |
| the unit of the claim ≠ the unit of the instrument | 16 |
| a number that was never derived from the object it describes | 12 |

⚠ **This table is a KEYWORD PROXY over headings, and it classifies 336 of 1,339.** The remaining
**1,003 are unclassified, NOT "other"** — the proxy is a lower bound on how often each shape appears
and it is not a distribution. Presenting it as one would be the exact error it catalogues.

⭐ **The single most expensive class is the first.** A control that returns the right answer without
executing the branch it claims to test reads identically to a control that works, and it certifies
whatever it was pointed at. The contract this project ended up with:

> **control validity = the plant is reachable ∧ the target branch executes ∧ the output responds.**
> The last conjunct alone is what almost every withdrawn claim here had.

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
