/-
  The CoVal attack campaign's derivation chain, projected from the claim graph in
  PostgreSQL (database `coval`, schema `claim`). GENERATED -- edit db/derivation_chain.py
  and re-run db/emit_lean.py; edits made here are overwritten.

  Empirical measurements enter as axioms named for the experiment that produced them.
  Inference rules enter as axioms too, because deciding that an underweighted polarity
  block means the compilation is unfaithful is a definitional choice, not a measurement.

  `#print axioms A1_is_refuted` returns the complete set of both that the conclusion
  actually rests on -- checked by the elaborator, not by me.

  A claim carrying an OPEN confound edge gets that confound as a required hypothesis, so
  its theorem cannot be closed until a control discharges it.
-/
namespace Coval

/-! ## The propositions -/

/-- **defect** · status `refuted` · D8
    r04's inline Judge takes yes_id, no_id = encode(' Yes')[0], encode(' No')[0] with no guard,
    unlike covalx/judge.py which raises when one encoding prefixes the other. The tensors
    predate that guard's commit (eb1f0b7, 2026-07-28 11:54) by 19 hours. -/
opaque defect_yes_no_token_id : Prop

/-- **defect** · status `refuted` · D8
    tokenizer(truncation=True, max_length=1024) truncates from the right, and the prompt's final
    token is 'Answer:' -- the exact position whose logits are read. Any over-length judgement
    would be reading a mid-reply next-word prediction instead of a verdict. -/
opaque defect_right_truncation_1024 : Prop

/-- **defect** · status `refuted` · D8
    build_prompt() cuts every reply at 1400 characters before tokenising, so the judge is
    structurally blind to anything late in a long response, and differentially so within a
    prompt whose four responses differ in length. -/
opaque defect_1400_char_reply_cut : Prop

/-- **their_assumption** · status `refuted` · D8
    coval_core, four compiled criteria carrying no ratings, is a faithful compilation of
    coval_full's ~15.8 participant-written criteria and their -10..+10 importance ratings. -/
opaque A1_core_is_a_faithful_compilation : Prop

/-- **their_assumption** · status `partial` · D5
    Aggregating criteria across participants produces a standard that is collective rather than
    an artefact of who happened to be asked. -/
opaque A3_aggregation_yields_a_collective_standard : Prop

/-- **their_assumption** · status `partial` · D7
    The -10..+10 per-criterion ratings carry usable importance information. -/
opaque A6_ratings_are_meaningful_importance_weights : Prop

/-- **fact** · status `settled` · D9
    Of coval_full's 15,248 rated criteria, 63.5% carry exactly one rating and 34.0% carry ten or
    more; 0.2% lie between. Among the 3,905 negatively-rated criteria, 77.2% are single-rater,
    against 58.8% of the positive ones. -/
opaque fact_63pct_of_criteria_have_one_rater : Prop

/-- **fact** · status `settled` · D8
    Among the 890 negatively-rated criteria with at least three raters, 99.1% have at least one
    rater on the positive side, the median share of positive raters is 38.5%, and 47.9% have at
    least 40% of raters positive. Bootstrapping the rater set, 18.9% of the n>=10 criteria flip
    sign in more than 10% of resamples. -/
opaque fact_negative_criteria_are_splits_not_evils : Prop

/-- **my_claim** · status `settled` · D8
    Regressing core's within-prompt-centred response score on full's positive and sign-flipped
    negative components gives beta_neg/beta_pos = 0.094 (95% CI [0.073, 0.114]). A faithful
    summary weighting each polarity block by its share of the input would give 0.362. Core
    therefore carries the negatively-rated quarter at roughly a quarter of proportional weight
    and a tenth of the positive block's weight. -/
opaque core_retains_the_negative_quarter_at_one_tenth_weight : Prop

/-- **my_claim** · status `settled` · D8
    Whether coval_full beats coval_core at reproducing human world rankings is decided by how
    the analyst treats the 25.6% of criteria carrying negative ratings. Sign-ignored: core wins.
    Sign-corrected: full wins. Both are true statements about the same release. -/
opaque the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment : Prop

/-- **my_claim** · status `partial` · D6
    coval_core's concordance is statistically indistinguishable from simply deleting every
    negatively-rated criterion from coval_full and averaging what remains. -/
opaque core_is_indistinguishable_from_dropping_the_negatives : Prop

/-- **my_claim** · status `partial` · D6
    Per criterion flipped, the concordance gained from a negative sign is monotone in the
    evidential basis of that sign: multi-rater and bootstrap-stable 0.0496 per 1000, middle
    0.0419, unstable 0.0340, single-rater 0.0215. Single-rater signs fall BELOW a count-matched
    draw from the whole negative pool (z=-5.58); stable ones sit above it (z=+4.03). -/
opaque a_negative_signs_value_rises_with_the_number_of_raters_behind_it : Prop

/-- **my_claim** · status `settled` · D8
    Three implementation-level attacks on the satisfaction judge -- wrong Yes/No token ids,
    right-truncation cutting the read position, and the 1400-character reply cut -- were run
    against the object and all three failed. This clears the judge's CODE. It says nothing about
    the judge's BEHAVIOUR, which no second judge has ever cross-checked. -/
opaque the_judges_implementation_carries_no_established_defect : Prop

/-- **my_claim** · status `settled` · D8
    The premise all three K1 designs share -- that a negative mean rating means satisfying the
    criterion is bad, so satisfaction should be read as 1-v -- was tested rather than assumed.
    Scoring responses on negatively-rated criteria FLIPPED predicts held-out human world
    rankings at 61.0%; UNFLIPPED at 39.0%. Text inspection agrees: the negatively-rated criteria
    are affirmative descriptions of a behaviour ('Invents fake sources', 'Use a violent tone'),
    not prohibitions, so high satisfaction means the response did the thing. -/
opaque the_flip_reading_of_a_negative_rating_is_measured_not_assumed : Prop

/-- **my_claim** · status `partial` · D7
    Regressing core's within-prompt-centred score on full's flat average and on the part of
    full's importance-weighted average orthogonal to it gives b1 = 0.861 [0.848, 0.872] and b2 =
    0.084 [0.055, 0.112] in standardised units: core is overwhelmingly a flat summary with a
    statistically real but structurally minor weighted component, 62% of the ceiling the noise
    level permits. Compilation discards most of the importance structure, not all. -/
opaque core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual : Prop

/-- **fact** · status `settled` · D8
    Across a prompt's four responses, the importance-weighted and the equal-weight summaries of
    coval_full correlate at mean r = 0.957, median 0.992, p10 0.902. Averaging over ~15 criteria
    washes out almost everything the -10..+10 magnitudes could change, so any design that asks
    'does core behave weighted or unweighted' by comparing response-level aggregates is
    near-unidentifiable before it starts. -/
opaque weighted_and_unweighted_full_are_near_collinear_in_this_release : Prop

/-- **my_claim** · status `partial` · D7
    At a matched budget of four criteria, coval_core scores 0.6563 pairwise concordance and a
    deterministic sort of the release's own human importance ratings scores 0.6589-0.6600 --
    statistically indistinguishable, and numerically ahead. Core does beat selection rules that
    cannot see the ratings: random-4 by +1.4pp and a text-only mechanical rule by 0 to +2.0pp.
    So compilation adds real work over a blind selector and no measurable work over a free sort
    of data already collected. -/
opaque a_zero_LLM_importance_sort_matches_the_compiler : Prop

/-- **fact** · status `settled` · D8
    The -0.95 correlation between criterion text length and judge decisiveness, which two K13
    designs reported and which I passed on as K18's mechanism, is an ARM-LEVEL correlation over
    roughly thirteen points, each an arm's mean. At the level the mechanism would have to
    operate -- the individual criterion -- it is -0.036 over 14,984 instances and -0.037 over
    18,811, i.e. r-squared about 0.001. An ecological correlation was read as an individual one,
    by them and then by me. -/
opaque fact_the_length_decisiveness_correlation_was_ecological : Prop

/-- **my_claim** · status `settled` · D8
    Holding authorship and criterion count fixed and varying only text length inside coval_full,
    the SHORTER four-criterion subset scores WORSE, not better: -0.0287 [-0.0424, -0.0149]. Core
    beats the terse human subset by +0.1009 [+0.0892, +0.1126], more than it beats full at
    large. Controlling for log length does not shrink core's advantage at all -- the
    style-explained share is 1.035 [1.022, 1.050], i.e. slightly negative. And core (88.2 chars,
    decisiveness 0.219) is MORE decisive than a 65.1-char human subset (0.211), so decisiveness
    does not track brevity. -/
opaque cores_advantage_is_content_and_the_style_mechanism_runs_backwards : Prop

/-- **fact** · status `settled` · D9
    298 of coval_core's 3,828 criteria (7.8%) match a coval_full criterion exactly after
    normalisation. The release carries no provenance link, but that subset IS provenance for
    7.8% of the compilation, and it makes one proxy-free retention test possible. -/
opaque fact_7_8pct_of_core_criteria_are_verbatim_copies : Prop

/-- **fact** · status `settled` · D9
    The rater-count distribution has a literal hole: 63.5% of criteria carry exactly one rating,
    ZERO carry two or three, about 2.4% carry four to nine, and 34.0% carry ten or more. My
    earlier statement that 0.2% lie between counted only n=2 and n=3 and understated the 4-9
    band by an order of magnitude. The jump from 1 straight to 4 is a protocol signature, not a
    sampling curve: two collection regimes were glued together. -/
opaque fact_no_criterion_has_two_or_three_raters : Prop

/-- **my_claim** · status `partial` · D7
    Among 4,127 coval_full criteria on which raters split by sign, the ones whose satisfaction
    fingerprint survives detectably into the compiled arm side with the rater MAJORITY 88.7% of
    the time [86.7%, 90.7%], and the rate scales monotonically with how lopsided the split is:
    58.1% at the weakest splits, 98.1% at the strongest. The failure mode is not that dissent is
    erased at random -- it is that the majority takes the compiled criterion. -/
opaque when_a_contested_criterion_survives_the_majority_captures_it : Prop

/-- **my_claim** · status `partial` · D4
    Both K8 designs find the raw association -- contested criteria are retained far less often.
    They DISAGREE on whether it survives adjustment for rating magnitude, and the disagreement
    is a design difference, not noise: A regresses a continuous matchability score linearly on
    |mean rating| and gets +0.003 [-0.019, 0.025], a magnitude-mediated null; B fits a logistic
    on a thresholded nearest-neighbour retention indicator with standardised |mean| and log
    rater count and gets OR 0.354 [0.247, 0.493]. B additionally has a proxy-free arm A did not
    use as an outcome: among the 286 multi-rated criteria KNOWN to have been copied verbatim
    into core, 11.2% are contested against a 40.9% population base rate, z=-10.2 -- but that arm
    is unadjusted for magnitude, which is exactly the quantity in dispute. -/
opaque whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled : Prop

/-- **defect** · status `refuted` · D9
    The first draft of the gauge round built its prompt variants by chained .replace on a
    template. Two of five came out broken: the negated-question variant's second and third
    replacements cancelled, leaving a Yes exemplar under a 'does the reply VIOLATE' question,
    and the reordered-fewshot variant lost its second exemplar's question line. Both then
    reported large concordance drifts that were my own malformed prompts, not the judge's gauge
    dependence. Caught by reading the constructed strings, not by the numbers -- the numbers
    looked like a finding. -/
opaque defect_my_own_gauge_variants_were_malformed : Prop

/-- **my_claim** · status `settled` · D8
    Rounds r116-r119 reported counts of harmed people under compilation. Re-measured with a
    within-person floor -- split each annotator's own prompt set in half at random and compute
    the identical gain on each half -- the between-person spread does NOT exceed that floor
    under either baseline: 0.06870 against 0.06130 (full_equal), 0.05348 against 0.05062
    (full_signed). '12.8% of people are harmed' and '59.4% of people are harmed' are statements
    about how many prompts each person happened to see, not about people. Every person-level
    sacrifice COUNT this project has published on this data is withdrawn. -/
opaque person_level_harm_COUNTS_are_withdrawn : Prop

/-- **my_claim** · status `partial` · D6
    The person-level spread is noise-dominated, but it is not structureless: if it were, no
    covariate could predict it. Two do, after partialling out a person's prompt count -- the
    noise-shrinkage confound, named before the control ran and only weakly related to either
    covariate. Against the signed baseline, where the aggregate favours full, a person's
    deviation from their peers' rating means predicts a HIGHER gain (partial r +0.099,
    permutation p 0.0025) and the number of criteria they rated predicts a LOWER one (-0.129, p
    0.0000). full's ratings encode the majority's view, so the ratings-free compiled arm is
    relatively kinder to the people furthest from it. About 1% of variance. -/
opaque core_serves_the_people_furthest_from_consensus_relatively_better : Prop

/-- **my_claim** · status `partial` · D6
    Compilation reproduces a person's own ranking 1.25pp worse than that person's own
    importance-weighted full arm [-2.01, -0.48], which is BH-significant and Cohen's d -0.047.
    But core also trails a NON-personalised pooled full arm by 2.05pp, a LARGER gap. So the
    shortfall is dominated by having four criteria instead of fifteen, not by losing the
    person's own weighting. The redistribution story, at the level this project originally posed
    it, is not what the data shows. -/
opaque most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation : Prop

/-! ## Confounds that are named but not yet ruled out.
    No term of type `¬c` exists for any of these, so every theorem below that needs
    one is stated with it as a hypothesis and cannot be discharged today. -/

/-- Both exemplars in the judge's two-shot prompt state a criterion in positive prescriptive
    form. If the judge is a systematically noisier reader of criteria that describe an
    undesirable behaviour, that alone attenuates every measurement on the negative quarter --
    the same quarter that carries the polarity result, the sign-flip result, and most of the
    contested criteria. Named by an independent design as the most credible way its own
    conclusion could be an underestimate. -/
opaque K19_the_judges_fewshot_only_demonstrates_positive_criteria : Prop

/-- The second K3 design's positive control failed, so its near-zero result is silence rather
    than acquittal and may never be folded in with design A's as agreement. Recorded so that no
    later reader counts two designs where there is one measurement and one refusal. -/
opaque K3_design_B_returned_UNVERIFIED_not_a_null : Prop

/-! ## Evidence. A witness for a claim, never the claim itself. -/

axiom Evidence : Prop → Type

/-- Experiment `session-direct-check-2026-07-30` (D8).
    Qwen2Tokenizer gives ' Yes'->[7179] and ' No'->[2233]: both single tokens, distinct. The
    SentencePiece failure mode cannot arise on this BPE tokenizer. ACQUITTED. -/
axiom ev_defect_yes_no_token_id_by_session_direct_check_2026_07_30 : Evidence defect_yes_no_token_id

/-- Experiment `session-direct-check-2026-07-30` (D8).
    Over all 75,248 rebuilt judge prompts: median 236 tokens, p99 321, max 537. Zero exceeded
    1024 (0.0000%). truncation_side is indeed 'right', so the mechanism is real but never fires
    on this corpus. ACQUITTED. -/
axiom ev_defect_right_truncation_1024_by_session_direct_check_2026_07_30 : Evidence defect_right_truncation_1024

/-- Experiment `session-direct-check-2026-07-30` (D8).
    3,872 responses: median 525 chars, p95 691, max 2,624. Six responses (0.2%) exceed 1400,
    across 6 of 968 prompts, never all four in one prompt. Median within-prompt length spread
    1.30x. ACQUITTED as negligible, not as absent. -/
axiom ev_defect_1400_char_reply_cut_by_session_direct_check_2026_07_30 : Evidence defect_1400_char_reply_cut

/-- Experiment `session-direct-count-2026-07-30` (D9).
    Counted straight off data/conversation_rubrics.jsonl; no model, no inference. -/
axiom ev_fact_63pct_of_criteria_have_one_rater_by_session_direct_count_2026_07_30 : Evidence fact_63pct_of_criteria_have_one_rater

/-- Experiment `session-direct-count-2026-07-30` (D8).
    Text inspection confirms the class: 'Take an explicit position on whether Chile should
    expand or restrict access to abortion' (-5.23, n=13) is a contested stance, not a harm. -/
axiom ev_fact_negative_criteria_are_splits_not_evils_by_session_direct_count_2026_07_30 : Evidence fact_negative_criteria_are_splits_not_evils

/-- Experiment `independent-design-A-seed-8101` (D8).
    A third estimand again: ratio of |corr(neg-component, core)| to |corr(pos-component, core)|
    = 0.20 [0.150, 0.249]. Size-matched subsample 0.235 (5 seeds, sd 0.002); split-half
    reliability correction (rel_pos 0.86, rel_neg 0.69) 0.222 -- both controls move the estimate
    UP, not down. r_pos +0.892, r_neg -0.178 [-0.222,-0.133]. The three designs return 0.094 /
    0.094 / 0.20 because they estimate different quantities; the direction, not the magnitude,
    is what replicates. -/
axiom ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_independent_design_A_seed_8101 : Evidence core_retains_the_negative_quarter_at_one_tenth_weight

/-- Experiment `independent-design-B-seed-4409` (D8).
    Independent estimand, independent code, seed 4409: ratio 0.094 [0.073, 0.114], beta_pos
    1.124. Synthetic placebo recovers planted (0.7,0.2) as (0.701,0.201) and (0.7,0.0) as
    (0.697,0.001). -/
axiom ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_independent_design_B_seed_4409 : Evidence core_retains_the_negative_quarter_at_one_tenth_weight

/-- Experiment `r124-my-own-decomposition` (D8).
    beta_pos=+1.1253 (se 0.0093, t=121.3), beta_neg=+0.1067 (se 0.0077, t=13.8), R^2=0.8056 over
    924 prompts / 3,696 units; corr(components)=+0.0877. Placebo: decomposing full's own
    positive arm returns exactly (1.0000, -0.0000). -/
axiom ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_r124_my_own_decomposition : Evidence core_retains_the_negative_quarter_at_one_tenth_weight

/-- Experiment `independent-design-A-seed-8101` (D8).
    Exact decomposition: total(signed-core)=+0.0256, sign(signed-uniform)=+0.0919,
    compile(uniform-core)=-0.0663. Sham permuting which criterion gets which sign, magnitudes
    fixed, 500 reps: observed sits ~23 sd outside. -/
axiom ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_independent_design_A_seed_8101 : Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment

/-- Experiment `independent-design-B-seed-4409` (D8).
    Five treatments: UNWT 0.590, SIGNED 0.683, DROP 0.648, FLIP 0.678, MAGSHAM 0.601.
    SIGNED-MAGSHAM=+0.082 [+0.072,+0.091] isolates the sign from the weighting. Dose response
    across quartiles of a prompt's negative share: +0.044 -> +0.147. -/
axiom ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_independent_design_B_seed_4409 : Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment

/-- Experiment `r127-arms` (D8).
    full sign-ignored 0.5941 [0.5827,0.6051]; full all-negatives-flipped 0.6806 [0.6709,0.6901];
    core 0.6604 [0.6502,0.6706]; 80,542 pooled human ordered pairs. -/
axiom ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_r127_arms : Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment

/-- Experiment `independent-design-A-seed-8101` (D5).
    posonly 0.6606 vs core 0.6604, difference +0.0003 [-0.006,+0.007], p=0.92 on pooled
    concordance and p=0.71 on per-prompt Spearman. FLAGGED BY ITS OWN AUTHOR AS POST-HOC AND
    EXPLORATORY, outside the corrected family. One design, one seed, not replicated. -/
axiom ev_core_is_indistinguishable_from_dropping_the_negatives_by_independent_design_A_seed_8101 : Evidence core_is_indistinguishable_from_dropping_the_negatives

/-- Experiment `independent-design-A-seed-8101-negation-markers` (D6).
    Negation markers appear in 13.0% of negatively-rated full criteria against 12.8% of positive
    ones, so core is not reaching the same place by rephrasing them as prohibitions. -/
axiom ev_core_is_indistinguishable_from_dropping_the_negatives_by_independent_design_A_seed_8101_negation_markers : Evidence core_is_indistinguishable_from_dropping_the_negatives

/-- Experiment `r127-whose-sign` (D6).
    SINGLE k=2975 gain +0.06394 (+0.0215/1k, z=-5.58); STABLE k=336 +0.01665 (+0.0496/1k,
    z=+4.03); MIDDLE k=75 (+0.0419/1k, z=+1.15); UNSTABLE k=444 (+0.0340/1k, z=+2.14). Positive
    control flip-all vs flip-none +0.08644 [+0.07711,+0.09586]. Placebo flipping the empty set
    reproduces the unflipped arm at |diff|=0.00e+00. -/
axiom ev_a_negative_signs_value_rises_with_the_number_of_raters_behind_it_by_r127_whose_sign : Evidence a_negative_signs_value_rises_with_the_number_of_raters_behind_it

/-- Experiment `session-direct-check-2026-07-30` (D8).
    Three attacks run against the object, three failures: ' Yes'->[7179] / ' No'->[2233] single
    and distinct; max prompt 537 tokens against a 1024 cap; 6 of 3,872 replies over the
    1400-character cut. Each is an acquittal of the CODE and of nothing else. -/
axiom ev_the_judges_implementation_carries_no_established_defect_by_session_direct_check_2026_07_30 : Evidence the_judges_implementation_carries_no_established_defect

/-- Experiment `independent-design-A-seed-8101` (D8).
    Sign-convention check: flipped 61.0% [0.599,0.622] vs unflipped 39.0% against chance 50%. -/
axiom ev_the_flip_reading_of_a_negative_rating_is_measured_not_assumed_by_independent_design_A_seed_8101 : Evidence the_flip_reading_of_a_negative_rating_is_measured_not_assumed

/-- Experiment `session-text-inspection-2026-07-30` (D7).
    20 randomly drawn negatively-rated criteria read directly; none is phrased as a prohibition.
    Independently corroborated: negation markers appear at 13.0% in negative criteria against
    12.8% in positive ones. -/
axiom ev_the_flip_reading_of_a_negative_rating_is_measured_not_assumed_by_session_text_inspection_2026_07_30 : Evidence the_flip_reading_of_a_negative_rating_is_measured_not_assumed

/-- Experiment `independent-design-A-seed-8101` (D6).
    b1 std 0.861, b2 std 0.084, dominance ratio 0.097; high-dispersion tertile b2 = 0.122
    [0.075,0.168], larger where weights actually vary. Length covariate moves b2 by 0.0002.
    Author disclosed that its 0.30 dominance bar was chosen post-hoc after both terms cleared
    significance -- the ratio 0.097 is far from any defensible co-equal line, but the threshold
    itself was not pre-registered. -/
axiom ev_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_by_independent_design_A_seed_8101 : Evidence core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual

/-- Experiment `independent-design-B-seed-4409` (D8).
    Measured while diagnosing its own FAILED positive control: a synthetic core built 100% from
    the weighted formula returned delta = +0.036 against a pre-registered bar of 0.15. The
    design returned UNVERIFIED rather than reporting the near-zero as a null. -/
axiom ev_weighted_and_unweighted_full_are_near_collinear_in_this_release_by_independent_design_B_seed_4409 : Evidence weighted_and_unweighted_full_are_near_collinear_in_this_release

/-- Experiment `independent-design-A-seed-8101` (D7).
    core 0.6563; top-importance-4 0.6589 (delta -0.26pp, perm p 0.575 Holm 1.0); mechanical-4
    0.6587 (delta -0.24pp, p 0.627); random-4 0.6422 (delta +1.40pp, Holm 0.0006); all-full
    0.6769; placebo 0.5006. Its CV search for the best mechanical rule converged on alpha ~ 1.0
    in 40 of 50 folds -- inter-rater agreement adds nothing beyond raw importance magnitude. -/
axiom ev_a_zero_LLM_importance_sort_matches_the_compiler_by_independent_design_A_seed_8101 : Evidence a_zero_LLM_importance_sort_matches_the_compiler

/-- Experiment `independent-design-B-seed-4409` (D7).
    core 0.6563 (identical to design A to four decimals, on an independently written harness);
    top-importance-4 0.65998 (delta -0.37pp, Holm 0.42); random-4 +1.38pp; mechanical-4 +1.98pp
    (Holm 0.0012); worst-importance-4 +5.10pp. Diverges from design A on mechanical-4 --
    distinguishable there, not here -- because the two built different mechanical rules.
    Unoriented sensitivity: top-4 without the free sign information falls to 0.5606, 9.6pp BELOW
    core. -/
axiom ev_a_zero_LLM_importance_sort_matches_the_compiler_by_independent_design_B_seed_4409 : Evidence a_zero_LLM_importance_sort_matches_the_compiler

/-- Experiment `independent-design-K18-A-seed-8101` (D8).
    Within-arm criterion-level rho = -0.036 (n=14,984), partial rho = -0.052 controlling a
    hedge/conjunction/comma density proxy for content complexity. -/
axiom ev_fact_the_length_decisiveness_correlation_was_ecological_by_independent_design_K18_A_seed_8101 : Evidence fact_the_length_decisiveness_correlation_was_ecological

/-- Experiment `independent-design-K18-B-seed-4409` (D8).
    Per-instance rho = -0.037 (n=18,811), reached independently and independently diagnosed as
    an arm-level artefact of the project's wider battery of arms. -/
axiom ev_fact_the_length_decisiveness_correlation_was_ecological_by_independent_design_K18_B_seed_4409 : Evidence fact_the_length_decisiveness_correlation_was_ecological

/-- Experiment `independent-design-K18-A-seed-8101` (D8).
    short4 - long4 = -0.0287, Wilcoxon p=3.1e-5, survives BH over 6 cells; core - short4 =
    +0.1009 (rank-biserial +0.50); style-attributable share -26% vs sham and -43% vs long4, both
    NEGATIVE. Label-shuffle negative control returns 0.4992; list-position placebo +0.0009
    (p=0.78) despite a real length gap. -/
axiom ev_cores_advantage_is_content_and_the_style_mechanism_runs_backwards_by_independent_design_K18_A_seed_8101 : Evidence cores_advantage_is_content_and_the_style_mechanism_runs_backwards

/-- Experiment `independent-design-K18-B-seed-4409` (D8).
    r_style = 1.035 [1.022, 1.050] over 5 seeds x 2000 draws; length-matched tercile (63.9
    chars, shorter than core's 88.2) still trails core by -0.081 [-0.088,-0.073], which is 117%
    of the raw gap. All 6 pre-registered tests reject under Holm. -/
axiom ev_cores_advantage_is_content_and_the_style_mechanism_runs_backwards_by_independent_design_K18_B_seed_4409 : Evidence cores_advantage_is_content_and_the_style_mechanism_runs_backwards

/-- Experiment `independent-design-K8-B-seed-4409` (D9).
    298/3828 exact-text matches after normalisation; the remaining 92% are paraphrased or
    synthesised and are not recoverable by reading text. -/
axiom ev_fact_7_8pct_of_core_criteria_are_verbatim_copies_by_independent_design_K8_B_seed_4409 : Evidence fact_7_8pct_of_core_criteria_are_verbatim_copies

/-- Experiment `independent-design-K8-B-seed-4409` (D9).
    Verified independently while checking the facts it was handed rather than taking them from
    the brief -- which is why the understatement was caught. -/
axiom ev_fact_no_criterion_has_two_or_three_raters_by_independent_design_K8_B_seed_4409 : Evidence fact_no_criterion_has_two_or_three_raters

/-- Experiment `independent-design-K8-A-seed-8101` (D7).
    997 majority-side / 127 minority-side / 3,003 washed out; binomial p=5.7e-168;
    prompt-clustered bootstrap CI [86.7%, 90.7%]; stable at rater thresholds 5/10/15 (88.1% /
    88.7% / 88.6%). Positive control on 304 exact-text matches: median r=0.866 against a null
    median of 0.007. -/
axiom ev_when_a_contested_criterion_survives_the_majority_captures_it_by_independent_design_K8_A_seed_8101 : Evidence when_a_contested_criterion_survives_the_majority_captures_it

/-- Experiment `independent-design-K8-A-seed-8101` (D5).
    Raw -0.098 [-0.117,-0.079]; magnitude-adjusted +0.003 [-0.019,0.025];
    magnitude-quintile-matched +0.008 with no consistent sign; robust at rater thresholds
    5/10/15. Verdict UNVERIFIED on its own pre-registered bar. -/
axiom ev_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_by_independent_design_K8_A_seed_8101 : Evidence whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled

/-- Experiment `independent-design-K8-B-seed-4409` (D6).
    Adjusted OR 0.354 [0.247,0.493], retention 2.6% vs 13.9% (-11.3pp); unadjusted OR 0.168, so
    the magnitude confound is real and large but the effect survives it; stable in both
    rater-count regimes (4-9: 0.387; >=10: 0.356); mismatched-prompt placebo returns OR ~0.82,
    near null. Verdict CONFIRMED. -/
axiom ev_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_by_independent_design_K8_B_seed_4409 : Evidence whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled

/-- Experiment `session-self-audit-2026-07-30` (D9).
    Rebuilt from a structured exemplar spec; the malformed run's max drift 0.2131 fell to 0.1736
    and relocated entirely to the negated-question x sign-flipped cell, which is a double
    negation rather than a template artefact. A prompt template is code: it gets built, not
    patched. -/
axiom ev_defect_my_own_gauge_variants_were_malformed_by_session_self_audit_2026_07_30 : Evidence defect_my_own_gauge_variants_were_malformed

/-- Experiment `independent-design-K5-A-seed-8101` (D8).
    Reached the same conclusion from a different direction and more starkly: median
    WITHIN-person sd of the person-prompt gain is 23.15pp against a BETWEEN-person sd of 8.51pp,
    so the between-person spread is about a THIRD of its own resampling floor. ICC 0.022 with
    permutation p 0.0 over 5 seeds -- real structure, tiny share of variance, and it warns
    against over-reading that p at n=15,031. -/
axiom ev_person_level_harm_COUNTS_are_withdrawn_by_independent_design_K5_A_seed_8101 : Evidence person_level_harm_COUNTS_are_withdrawn

/-- Experiment `r131-who-is-served` (D8).
    975 annotators with >=4 prompts and >=8 ordered pairs, 15,103 person-prompt cells, 200
    random half-splits per person. Mean gain +0.06809 [+0.06373,+0.07242] against full_equal and
    -0.01887 [-0.02218,-0.01545] against full_signed; worst decile -0.04907 and -0.11114. WORLD:
    W-UNIFORM under the pre-registered 1.5x-floor rule. -/
axiom ev_person_level_harm_COUNTS_are_withdrawn_by_r131_who_is_served : Evidence person_level_harm_COUNTS_are_withdrawn

/-- Experiment `independent-design-K5-A-seed-8101` (D7).
    Distance from pooled consensus predicts a LESS negative person-level gain, rho +0.133 (p
    2.6e-5), the same sign as the +0.099 partial found here; engagement (criteria rated per
    prompt) rho -0.215, also the same sign as -0.129. CRUCIALLY it baselines against the
    person's OWN importance-weighted full arm, not the pooled one, and offers a rival reading
    for its own version: an idiosyncratic rater's own ratings predict their own ranking more
    noisily, which weakens their personal baseline rather than core serving them better. That
    reading cannot explain the pooled-baseline version, so the two designs agreeing on sign
    across DIFFERENT baselines is worth more than either alone. -/
axiom ev_core_serves_the_people_furthest_from_consensus_relatively_better_by_independent_design_K5_A_seed_8101 : Evidence core_serves_the_people_furthest_from_consensus_relatively_better

/-- Experiment `r131-who-is-served` (D6).
    dev_from_mean raw +0.109 -> partial +0.099 (p 0.0025); n_rated raw -0.133 -> partial -0.129
    (p 0.0000); correlations of each covariate with prompt count are -0.085 and +0.037, so
    exposure is not the driver. Under full_equal the same gradients appear with the opposite
    sign, so the direction is baseline-conditional and may never be stated without naming the
    convention. -/
axiom ev_core_serves_the_people_furthest_from_consensus_relatively_better_by_r131_who_is_served : Evidence core_serves_the_people_furthest_from_consensus_relatively_better

/-- Experiment `independent-design-K5-A-seed-8101` (D6).
    core vs personal -1.25pp (p 0.0014, two-way cluster on person x prompt, 15,031 rows, 79,640
    pairs); core vs full_pooled -2.05pp (p 1.6e-8). Below its own pre-registered 2.0pp practical
    floor, hence UNVERIFIED rather than OVERTURNED. Sign-convention spec cell: against UNSIGNED
    pooled full, core WINS by +6.89pp -- the negative-quarter fact is load-bearing, not
    cosmetic. -/
axiom ev_most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_by_independent_design_K5_A_seed_8101 : Evidence most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation

/-! ## Establishing rules. The arity of each is how many independent measurements
    the graph actually holds for that claim -- read it off the type. -/

/-- 1 independent measurement(s) establish `defect_yes_no_token_id`. -/
axiom defect_yes_no_token_id_established : Evidence defect_yes_no_token_id → defect_yes_no_token_id
theorem defect_yes_no_token_id_holds : defect_yes_no_token_id := defect_yes_no_token_id_established ev_defect_yes_no_token_id_by_session_direct_check_2026_07_30

/-- 1 independent measurement(s) establish `defect_right_truncation_1024`. -/
axiom defect_right_truncation_1024_established : Evidence defect_right_truncation_1024 → defect_right_truncation_1024
theorem defect_right_truncation_1024_holds : defect_right_truncation_1024 := defect_right_truncation_1024_established ev_defect_right_truncation_1024_by_session_direct_check_2026_07_30

/-- 1 independent measurement(s) establish `defect_1400_char_reply_cut`. -/
axiom defect_1400_char_reply_cut_established : Evidence defect_1400_char_reply_cut → defect_1400_char_reply_cut
theorem defect_1400_char_reply_cut_holds : defect_1400_char_reply_cut := defect_1400_char_reply_cut_established ev_defect_1400_char_reply_cut_by_session_direct_check_2026_07_30

/-- 1 independent measurement(s) establish `fact_63pct_of_criteria_have_one_rater`. -/
axiom fact_63pct_of_criteria_have_one_rater_established : Evidence fact_63pct_of_criteria_have_one_rater → fact_63pct_of_criteria_have_one_rater
theorem fact_63pct_of_criteria_have_one_rater_holds : fact_63pct_of_criteria_have_one_rater := fact_63pct_of_criteria_have_one_rater_established ev_fact_63pct_of_criteria_have_one_rater_by_session_direct_count_2026_07_30

/-- 1 independent measurement(s) establish `fact_negative_criteria_are_splits_not_evils`. -/
axiom fact_negative_criteria_are_splits_not_evils_established : Evidence fact_negative_criteria_are_splits_not_evils → fact_negative_criteria_are_splits_not_evils
theorem fact_negative_criteria_are_splits_not_evils_holds : fact_negative_criteria_are_splits_not_evils := fact_negative_criteria_are_splits_not_evils_established ev_fact_negative_criteria_are_splits_not_evils_by_session_direct_count_2026_07_30

/-- 3 independent measurement(s) establish `core_retains_the_negative_quarter_at_one_tenth_weight`. -/
axiom core_retains_the_negative_quarter_at_one_tenth_weight_established : Evidence core_retains_the_negative_quarter_at_one_tenth_weight → Evidence core_retains_the_negative_quarter_at_one_tenth_weight → Evidence core_retains_the_negative_quarter_at_one_tenth_weight → core_retains_the_negative_quarter_at_one_tenth_weight
theorem core_retains_the_negative_quarter_at_one_tenth_weight_holds : core_retains_the_negative_quarter_at_one_tenth_weight := core_retains_the_negative_quarter_at_one_tenth_weight_established ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_independent_design_A_seed_8101 ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_independent_design_B_seed_4409 ev_core_retains_the_negative_quarter_at_one_tenth_weight_by_r124_my_own_decomposition

/-- 3 independent measurement(s) establish `the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment`. -/
axiom the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_established : Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment → Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment → Evidence the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment → the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment
theorem the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_holds : the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment := the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_established ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_independent_design_A_seed_8101 ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_independent_design_B_seed_4409 ev_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_by_r127_arms

/-- 2 independent measurement(s) establish `core_is_indistinguishable_from_dropping_the_negatives`. -/
axiom core_is_indistinguishable_from_dropping_the_negatives_established : Evidence core_is_indistinguishable_from_dropping_the_negatives → Evidence core_is_indistinguishable_from_dropping_the_negatives → core_is_indistinguishable_from_dropping_the_negatives
theorem core_is_indistinguishable_from_dropping_the_negatives_holds : core_is_indistinguishable_from_dropping_the_negatives := core_is_indistinguishable_from_dropping_the_negatives_established ev_core_is_indistinguishable_from_dropping_the_negatives_by_independent_design_A_seed_8101 ev_core_is_indistinguishable_from_dropping_the_negatives_by_independent_design_A_seed_8101_negation_markers

/-- 1 independent measurement(s) establish `a_negative_signs_value_rises_with_the_number_of_raters_behind_it`. -/
axiom a_negative_signs_value_rises_with_the_number_of_raters_behind_it_established : Evidence a_negative_signs_value_rises_with_the_number_of_raters_behind_it → a_negative_signs_value_rises_with_the_number_of_raters_behind_it
theorem a_negative_signs_value_rises_with_the_number_of_raters_behind_it_holds : a_negative_signs_value_rises_with_the_number_of_raters_behind_it := a_negative_signs_value_rises_with_the_number_of_raters_behind_it_established ev_a_negative_signs_value_rises_with_the_number_of_raters_behind_it_by_r127_whose_sign

/-- 1 independent measurement(s) establish `the_judges_implementation_carries_no_established_defect`. -/
axiom the_judges_implementation_carries_no_established_defect_established : Evidence the_judges_implementation_carries_no_established_defect → the_judges_implementation_carries_no_established_defect
theorem the_judges_implementation_carries_no_established_defect_holds : the_judges_implementation_carries_no_established_defect := the_judges_implementation_carries_no_established_defect_established ev_the_judges_implementation_carries_no_established_defect_by_session_direct_check_2026_07_30

/-- 2 independent measurement(s) establish `the_flip_reading_of_a_negative_rating_is_measured_not_assumed`. -/
axiom the_flip_reading_of_a_negative_rating_is_measured_not_assumed_established : Evidence the_flip_reading_of_a_negative_rating_is_measured_not_assumed → Evidence the_flip_reading_of_a_negative_rating_is_measured_not_assumed → the_flip_reading_of_a_negative_rating_is_measured_not_assumed
theorem the_flip_reading_of_a_negative_rating_is_measured_not_assumed_holds : the_flip_reading_of_a_negative_rating_is_measured_not_assumed := the_flip_reading_of_a_negative_rating_is_measured_not_assumed_established ev_the_flip_reading_of_a_negative_rating_is_measured_not_assumed_by_independent_design_A_seed_8101 ev_the_flip_reading_of_a_negative_rating_is_measured_not_assumed_by_session_text_inspection_2026_07_30

/-- 1 independent measurement(s) establish `core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual`. -/
axiom core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_established : Evidence core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual → core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual
theorem core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_holds : core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual := core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_established ev_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_by_independent_design_A_seed_8101

/-- 1 independent measurement(s) establish `weighted_and_unweighted_full_are_near_collinear_in_this_release`. -/
axiom weighted_and_unweighted_full_are_near_collinear_in_this_release_established : Evidence weighted_and_unweighted_full_are_near_collinear_in_this_release → weighted_and_unweighted_full_are_near_collinear_in_this_release
theorem weighted_and_unweighted_full_are_near_collinear_in_this_release_holds : weighted_and_unweighted_full_are_near_collinear_in_this_release := weighted_and_unweighted_full_are_near_collinear_in_this_release_established ev_weighted_and_unweighted_full_are_near_collinear_in_this_release_by_independent_design_B_seed_4409

/-- 2 independent measurement(s) establish `a_zero_LLM_importance_sort_matches_the_compiler`. -/
axiom a_zero_LLM_importance_sort_matches_the_compiler_established : Evidence a_zero_LLM_importance_sort_matches_the_compiler → Evidence a_zero_LLM_importance_sort_matches_the_compiler → a_zero_LLM_importance_sort_matches_the_compiler
theorem a_zero_LLM_importance_sort_matches_the_compiler_holds : a_zero_LLM_importance_sort_matches_the_compiler := a_zero_LLM_importance_sort_matches_the_compiler_established ev_a_zero_LLM_importance_sort_matches_the_compiler_by_independent_design_A_seed_8101 ev_a_zero_LLM_importance_sort_matches_the_compiler_by_independent_design_B_seed_4409

/-- 2 independent measurement(s) establish `fact_the_length_decisiveness_correlation_was_ecological`. -/
axiom fact_the_length_decisiveness_correlation_was_ecological_established : Evidence fact_the_length_decisiveness_correlation_was_ecological → Evidence fact_the_length_decisiveness_correlation_was_ecological → fact_the_length_decisiveness_correlation_was_ecological
theorem fact_the_length_decisiveness_correlation_was_ecological_holds : fact_the_length_decisiveness_correlation_was_ecological := fact_the_length_decisiveness_correlation_was_ecological_established ev_fact_the_length_decisiveness_correlation_was_ecological_by_independent_design_K18_A_seed_8101 ev_fact_the_length_decisiveness_correlation_was_ecological_by_independent_design_K18_B_seed_4409

/-- 2 independent measurement(s) establish `cores_advantage_is_content_and_the_style_mechanism_runs_backwards`. -/
axiom cores_advantage_is_content_and_the_style_mechanism_runs_backwards_established : Evidence cores_advantage_is_content_and_the_style_mechanism_runs_backwards → Evidence cores_advantage_is_content_and_the_style_mechanism_runs_backwards → cores_advantage_is_content_and_the_style_mechanism_runs_backwards
theorem cores_advantage_is_content_and_the_style_mechanism_runs_backwards_holds : cores_advantage_is_content_and_the_style_mechanism_runs_backwards := cores_advantage_is_content_and_the_style_mechanism_runs_backwards_established ev_cores_advantage_is_content_and_the_style_mechanism_runs_backwards_by_independent_design_K18_A_seed_8101 ev_cores_advantage_is_content_and_the_style_mechanism_runs_backwards_by_independent_design_K18_B_seed_4409

/-- 1 independent measurement(s) establish `fact_7_8pct_of_core_criteria_are_verbatim_copies`. -/
axiom fact_7_8pct_of_core_criteria_are_verbatim_copies_established : Evidence fact_7_8pct_of_core_criteria_are_verbatim_copies → fact_7_8pct_of_core_criteria_are_verbatim_copies
theorem fact_7_8pct_of_core_criteria_are_verbatim_copies_holds : fact_7_8pct_of_core_criteria_are_verbatim_copies := fact_7_8pct_of_core_criteria_are_verbatim_copies_established ev_fact_7_8pct_of_core_criteria_are_verbatim_copies_by_independent_design_K8_B_seed_4409

/-- 1 independent measurement(s) establish `fact_no_criterion_has_two_or_three_raters`. -/
axiom fact_no_criterion_has_two_or_three_raters_established : Evidence fact_no_criterion_has_two_or_three_raters → fact_no_criterion_has_two_or_three_raters
theorem fact_no_criterion_has_two_or_three_raters_holds : fact_no_criterion_has_two_or_three_raters := fact_no_criterion_has_two_or_three_raters_established ev_fact_no_criterion_has_two_or_three_raters_by_independent_design_K8_B_seed_4409

/-- 1 independent measurement(s) establish `when_a_contested_criterion_survives_the_majority_captures_it`. -/
axiom when_a_contested_criterion_survives_the_majority_captures_it_established : Evidence when_a_contested_criterion_survives_the_majority_captures_it → when_a_contested_criterion_survives_the_majority_captures_it
theorem when_a_contested_criterion_survives_the_majority_captures_it_holds : when_a_contested_criterion_survives_the_majority_captures_it := when_a_contested_criterion_survives_the_majority_captures_it_established ev_when_a_contested_criterion_survives_the_majority_captures_it_by_independent_design_K8_A_seed_8101

/-- 2 independent measurement(s) establish `whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled`. -/
axiom whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_established : Evidence whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled → Evidence whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled → whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled
theorem whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_holds : whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled := whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_established ev_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_by_independent_design_K8_A_seed_8101 ev_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_by_independent_design_K8_B_seed_4409

/-- 1 independent measurement(s) establish `defect_my_own_gauge_variants_were_malformed`. -/
axiom defect_my_own_gauge_variants_were_malformed_established : Evidence defect_my_own_gauge_variants_were_malformed → defect_my_own_gauge_variants_were_malformed
theorem defect_my_own_gauge_variants_were_malformed_holds : defect_my_own_gauge_variants_were_malformed := defect_my_own_gauge_variants_were_malformed_established ev_defect_my_own_gauge_variants_were_malformed_by_session_self_audit_2026_07_30

/-- 2 independent measurement(s) establish `person_level_harm_COUNTS_are_withdrawn`. -/
axiom person_level_harm_COUNTS_are_withdrawn_established : Evidence person_level_harm_COUNTS_are_withdrawn → Evidence person_level_harm_COUNTS_are_withdrawn → person_level_harm_COUNTS_are_withdrawn
theorem person_level_harm_COUNTS_are_withdrawn_holds : person_level_harm_COUNTS_are_withdrawn := person_level_harm_COUNTS_are_withdrawn_established ev_person_level_harm_COUNTS_are_withdrawn_by_independent_design_K5_A_seed_8101 ev_person_level_harm_COUNTS_are_withdrawn_by_r131_who_is_served

/-- 2 independent measurement(s) establish `core_serves_the_people_furthest_from_consensus_relatively_better`. -/
axiom core_serves_the_people_furthest_from_consensus_relatively_better_established : Evidence core_serves_the_people_furthest_from_consensus_relatively_better → Evidence core_serves_the_people_furthest_from_consensus_relatively_better → core_serves_the_people_furthest_from_consensus_relatively_better
theorem core_serves_the_people_furthest_from_consensus_relatively_better_holds : core_serves_the_people_furthest_from_consensus_relatively_better := core_serves_the_people_furthest_from_consensus_relatively_better_established ev_core_serves_the_people_furthest_from_consensus_relatively_better_by_independent_design_K5_A_seed_8101 ev_core_serves_the_people_furthest_from_consensus_relatively_better_by_r131_who_is_served

/-- 1 independent measurement(s) establish `most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation`. -/
axiom most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_established : Evidence most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation → most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation
theorem most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_holds : most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation := most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_established ev_most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_by_independent_design_K5_A_seed_8101

/-! ## Inference rules, and what they close. -/

/-- SUPPORTS (d_forward 8). a COUNT of losers needs the spread to clear the floor and does not; a GRADIENT on a person
    characteristic does not need that, and two are real -/
axiom person_level_harm_COUNTS_are_withdrawn_supports_core_serves_the_people_furthest_from_consensus_relatively_better : person_level_harm_COUNTS_are_withdrawn → core_serves_the_people_furthest_from_consensus_relatively_better
theorem core_serves_the_people_furthest_from_consensus_relatively_better_is_supported_via_person_level_harm_COUNTS_are_withdrawn : core_serves_the_people_furthest_from_consensus_relatively_better := person_level_harm_COUNTS_are_withdrawn_supports_core_serves_the_people_furthest_from_consensus_relatively_better person_level_harm_COUNTS_are_withdrawn_holds

/-- SUPPORTS (d_forward 6). the same asymmetry reached from the opposite direction: the ratings carry the majority, so
    distance from the majority is what the compiled arm relieves -/
axiom core_serves_the_people_furthest_from_consensus_relatively_better_supports_when_a_contested_criterion_survives_the_majority_captures_it : core_serves_the_people_furthest_from_consensus_relatively_better → when_a_contested_criterion_survives_the_majority_captures_it
theorem when_a_contested_criterion_survives_the_majority_captures_it_is_supported_via_core_serves_the_people_furthest_from_consensus_relatively_better : when_a_contested_criterion_survives_the_majority_captures_it := core_serves_the_people_furthest_from_consensus_relatively_better_supports_when_a_contested_criterion_survives_the_majority_captures_it core_serves_the_people_furthest_from_consensus_relatively_better_holds

/-- SUPPORTS (d_forward 6).  -/
axiom most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_supports_person_level_harm_COUNTS_are_withdrawn : most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation → person_level_harm_COUNTS_are_withdrawn
theorem person_level_harm_COUNTS_are_withdrawn_is_supported_via_most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation : person_level_harm_COUNTS_are_withdrawn := most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_supports_person_level_harm_COUNTS_are_withdrawn most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_holds

/-- SUPPORTS (d_forward 8). the mechanism K18 needed does not exist at the criterion level -/
axiom fact_the_length_decisiveness_correlation_was_ecological_supports_cores_advantage_is_content_and_the_style_mechanism_runs_backwards : fact_the_length_decisiveness_correlation_was_ecological → cores_advantage_is_content_and_the_style_mechanism_runs_backwards
theorem cores_advantage_is_content_and_the_style_mechanism_runs_backwards_is_supported_via_fact_the_length_decisiveness_correlation_was_ecological : cores_advantage_is_content_and_the_style_mechanism_runs_backwards := fact_the_length_decisiveness_correlation_was_ecological_supports_cores_advantage_is_content_and_the_style_mechanism_runs_backwards fact_the_length_decisiveness_correlation_was_ecological_holds

/-- REFUTES (d_forward 5). a zero-LLM rule reproduces the compiler on this axis -- but at D5, one design -/
axiom core_is_indistinguishable_from_dropping_the_negatives_refutes_A1_core_is_a_faithful_compilation : core_is_indistinguishable_from_dropping_the_negatives → ¬A1_core_is_a_faithful_compilation
theorem A1_core_is_a_faithful_compilation_is_refuted_via_core_is_indistinguishable_from_dropping_the_negatives : ¬A1_core_is_a_faithful_compilation := core_is_indistinguishable_from_dropping_the_negatives_refutes_A1_core_is_a_faithful_compilation core_is_indistinguishable_from_dropping_the_negatives_holds

/-- SUPPORTS (d_forward 6). the sign's value tracks collective backing, which is what A3 needs -/
axiom a_negative_signs_value_rises_with_the_number_of_raters_behind_it_supports_A3_aggregation_yields_a_collective_standard : a_negative_signs_value_rises_with_the_number_of_raters_behind_it → A3_aggregation_yields_a_collective_standard
theorem A3_aggregation_yields_a_collective_standard_is_supported_via_a_negative_signs_value_rises_with_the_number_of_raters_behind_it : A3_aggregation_yields_a_collective_standard := a_negative_signs_value_rises_with_the_number_of_raters_behind_it_supports_A3_aggregation_yields_a_collective_standard a_negative_signs_value_rises_with_the_number_of_raters_behind_it_holds

/-- SUPPORTS (d_forward 6). locates where in the negative block the sign-flip advantage lives -/
axiom a_negative_signs_value_rises_with_the_number_of_raters_behind_it_supports_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment : a_negative_signs_value_rises_with_the_number_of_raters_behind_it → the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment
theorem the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_is_supported_via_a_negative_signs_value_rises_with_the_number_of_raters_behind_it : the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment := a_negative_signs_value_rises_with_the_number_of_raters_behind_it_supports_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment a_negative_signs_value_rises_with_the_number_of_raters_behind_it_holds

/-- SUPPORTS (d_forward 8). an attack that failed -/
axiom defect_yes_no_token_id_supports_the_judges_implementation_carries_no_established_defect : defect_yes_no_token_id → the_judges_implementation_carries_no_established_defect
theorem the_judges_implementation_carries_no_established_defect_is_supported_via_defect_yes_no_token_id : the_judges_implementation_carries_no_established_defect := defect_yes_no_token_id_supports_the_judges_implementation_carries_no_established_defect defect_yes_no_token_id_holds

/-- SUPPORTS (d_forward 8). an attack that failed -/
axiom defect_right_truncation_1024_supports_the_judges_implementation_carries_no_established_defect : defect_right_truncation_1024 → the_judges_implementation_carries_no_established_defect
theorem the_judges_implementation_carries_no_established_defect_is_supported_via_defect_right_truncation_1024 : the_judges_implementation_carries_no_established_defect := defect_right_truncation_1024_supports_the_judges_implementation_carries_no_established_defect defect_right_truncation_1024_holds

/-- SUPPORTS (d_forward 8). an attack that failed -/
axiom defect_1400_char_reply_cut_supports_the_judges_implementation_carries_no_established_defect : defect_1400_char_reply_cut → the_judges_implementation_carries_no_established_defect
theorem the_judges_implementation_carries_no_established_defect_is_supported_via_defect_1400_char_reply_cut : the_judges_implementation_carries_no_established_defect := defect_1400_char_reply_cut_supports_the_judges_implementation_carries_no_established_defect defect_1400_char_reply_cut_holds

/-- SUPPORTS (d_forward 8). the shared premise of all three designs, promoted from assumption to measurement -/
axiom the_flip_reading_of_a_negative_rating_is_measured_not_assumed_supports_core_retains_the_negative_quarter_at_one_tenth_weight : the_flip_reading_of_a_negative_rating_is_measured_not_assumed → core_retains_the_negative_quarter_at_one_tenth_weight
theorem core_retains_the_negative_quarter_at_one_tenth_weight_is_supported_via_the_flip_reading_of_a_negative_rating_is_measured_not_assumed : core_retains_the_negative_quarter_at_one_tenth_weight := the_flip_reading_of_a_negative_rating_is_measured_not_assumed_supports_core_retains_the_negative_quarter_at_one_tenth_weight the_flip_reading_of_a_negative_rating_is_measured_not_assumed_holds

/-- SUPPORTS (d_forward 8).  -/
axiom the_flip_reading_of_a_negative_rating_is_measured_not_assumed_supports_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment : the_flip_reading_of_a_negative_rating_is_measured_not_assumed → the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment
theorem the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_is_supported_via_the_flip_reading_of_a_negative_rating_is_measured_not_assumed : the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment := the_flip_reading_of_a_negative_rating_is_measured_not_assumed_supports_the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment the_flip_reading_of_a_negative_rating_is_measured_not_assumed_holds

/-- SUPPORTS (d_forward 7). the ratings carry information; the compilation mostly does not carry it forward
    Blocked on unresolved confound(s): K3_design_B_returned_UNVERIFIED_not_a_null. -/
axiom core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_supports_A6_ratings_are_meaningful_importance_weights : ¬K3_design_B_returned_UNVERIFIED_not_a_null → core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual → A6_ratings_are_meaningful_importance_weights
theorem A6_ratings_are_meaningful_importance_weights_is_supported_via_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual (h0 : ¬K3_design_B_returned_UNVERIFIED_not_a_null) : A6_ratings_are_meaningful_importance_weights := core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_supports_A6_ratings_are_meaningful_importance_weights h0 core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_holds

/-- REFUTES (d_forward 7). faithfulness on the weighting axis fails
    Blocked on unresolved confound(s): K3_design_B_returned_UNVERIFIED_not_a_null. -/
axiom core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_refutes_A1_core_is_a_faithful_compilation : ¬K3_design_B_returned_UNVERIFIED_not_a_null → core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual → ¬A1_core_is_a_faithful_compilation
theorem A1_core_is_a_faithful_compilation_is_refuted_via_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual (h0 : ¬K3_design_B_returned_UNVERIFIED_not_a_null) : ¬A1_core_is_a_faithful_compilation := core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_refutes_A1_core_is_a_faithful_compilation h0 core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_holds

/-- SUPPORTS (d_forward 7). explains why design A had to orthogonalise, and why design B could not resolve at all -/
axiom weighted_and_unweighted_full_are_near_collinear_in_this_release_supports_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual : weighted_and_unweighted_full_are_near_collinear_in_this_release → core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual
theorem core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_is_supported_via_weighted_and_unweighted_full_are_near_collinear_in_this_release : core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual := weighted_and_unweighted_full_are_near_collinear_in_this_release_supports_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual weighted_and_unweighted_full_are_near_collinear_in_this_release_holds

/-- SUPPORTS (d_forward 9). corrects the size of the middle band without touching the bimodality -/
axiom fact_no_criterion_has_two_or_three_raters_supports_fact_63pct_of_criteria_have_one_rater : fact_no_criterion_has_two_or_three_raters → fact_63pct_of_criteria_have_one_rater
theorem fact_63pct_of_criteria_have_one_rater_is_supported_via_fact_no_criterion_has_two_or_three_raters : fact_63pct_of_criteria_have_one_rater := fact_no_criterion_has_two_or_three_raters_supports_fact_63pct_of_criteria_have_one_rater fact_no_criterion_has_two_or_three_raters_holds

/-- SUPPORTS (d_forward 6). the proxy-free arm exists only because of it -/
axiom fact_7_8pct_of_core_criteria_are_verbatim_copies_supports_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled : fact_7_8pct_of_core_criteria_are_verbatim_copies → whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled
theorem whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_is_supported_via_fact_7_8pct_of_core_criteria_are_verbatim_copies : whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled := fact_7_8pct_of_core_criteria_are_verbatim_copies_supports_whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled fact_7_8pct_of_core_criteria_are_verbatim_copies_holds

/-- REFUTES (d_forward 7). the compiler's output is reachable without the compiler -/
axiom a_zero_LLM_importance_sort_matches_the_compiler_refutes_A1_core_is_a_faithful_compilation : a_zero_LLM_importance_sort_matches_the_compiler → ¬A1_core_is_a_faithful_compilation
theorem A1_core_is_a_faithful_compilation_is_refuted_via_a_zero_LLM_importance_sort_matches_the_compiler : ¬A1_core_is_a_faithful_compilation := a_zero_LLM_importance_sort_matches_the_compiler_refutes_A1_core_is_a_faithful_compilation a_zero_LLM_importance_sort_matches_the_compiler_holds

/-- REFUTES (d_forward 8). faithfulness on the polarity axis fails
    Blocked on unresolved confound(s): K19_the_judges_fewshot_only_demonstrates_positive_criteria. -/
axiom core_retains_the_negative_quarter_at_one_tenth_weight_refutes_A1_core_is_a_faithful_compilation : ¬K19_the_judges_fewshot_only_demonstrates_positive_criteria → core_retains_the_negative_quarter_at_one_tenth_weight → ¬A1_core_is_a_faithful_compilation
theorem A1_core_is_a_faithful_compilation_is_refuted_via_core_retains_the_negative_quarter_at_one_tenth_weight (h0 : ¬K19_the_judges_fewshot_only_demonstrates_positive_criteria) : ¬A1_core_is_a_faithful_compilation := core_retains_the_negative_quarter_at_one_tenth_weight_refutes_A1_core_is_a_faithful_compilation h0 core_retains_the_negative_quarter_at_one_tenth_weight_holds

/-! ## The audit. Each line prints the COMPLETE dependency set of one conclusion. -/

#print axioms core_serves_the_people_furthest_from_consensus_relatively_better_is_supported_via_person_level_harm_COUNTS_are_withdrawn
#print axioms when_a_contested_criterion_survives_the_majority_captures_it_is_supported_via_core_serves_the_people_furthest_from_consensus_relatively_better
#print axioms person_level_harm_COUNTS_are_withdrawn_is_supported_via_most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation
#print axioms cores_advantage_is_content_and_the_style_mechanism_runs_backwards_is_supported_via_fact_the_length_decisiveness_correlation_was_ecological
#print axioms A1_core_is_a_faithful_compilation_is_refuted_via_core_is_indistinguishable_from_dropping_the_negatives
#print axioms A3_aggregation_yields_a_collective_standard_is_supported_via_a_negative_signs_value_rises_with_the_number_of_raters_behind_it
#print axioms the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_is_supported_via_a_negative_signs_value_rises_with_the_number_of_raters_behind_it
#print axioms the_judges_implementation_carries_no_established_defect_is_supported_via_defect_yes_no_token_id
#print axioms the_judges_implementation_carries_no_established_defect_is_supported_via_defect_right_truncation_1024
#print axioms the_judges_implementation_carries_no_established_defect_is_supported_via_defect_1400_char_reply_cut
#print axioms core_retains_the_negative_quarter_at_one_tenth_weight_is_supported_via_the_flip_reading_of_a_negative_rating_is_measured_not_assumed
#print axioms the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_is_supported_via_the_flip_reading_of_a_negative_rating_is_measured_not_assumed
#print axioms A6_ratings_are_meaningful_importance_weights_is_supported_via_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual
#print axioms A1_core_is_a_faithful_compilation_is_refuted_via_core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual
#print axioms core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_is_supported_via_weighted_and_unweighted_full_are_near_collinear_in_this_release
#print axioms fact_63pct_of_criteria_have_one_rater_is_supported_via_fact_no_criterion_has_two_or_three_raters
#print axioms whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_is_supported_via_fact_7_8pct_of_core_criteria_are_verbatim_copies
#print axioms A1_core_is_a_faithful_compilation_is_refuted_via_a_zero_LLM_importance_sort_matches_the_compiler
#print axioms A1_core_is_a_faithful_compilation_is_refuted_via_core_retains_the_negative_quarter_at_one_tenth_weight
#print axioms defect_yes_no_token_id_holds
#print axioms defect_right_truncation_1024_holds
#print axioms defect_1400_char_reply_cut_holds
#print axioms fact_63pct_of_criteria_have_one_rater_holds
#print axioms fact_negative_criteria_are_splits_not_evils_holds
#print axioms core_retains_the_negative_quarter_at_one_tenth_weight_holds
#print axioms the_full_vs_core_verdict_depends_on_the_analysts_sign_treatment_holds
#print axioms core_is_indistinguishable_from_dropping_the_negatives_holds
#print axioms a_negative_signs_value_rises_with_the_number_of_raters_behind_it_holds
#print axioms the_judges_implementation_carries_no_established_defect_holds
#print axioms the_flip_reading_of_a_negative_rating_is_measured_not_assumed_holds
#print axioms core_behaves_as_a_flat_summary_with_a_small_real_weighted_residual_holds
#print axioms weighted_and_unweighted_full_are_near_collinear_in_this_release_holds
#print axioms a_zero_LLM_importance_sort_matches_the_compiler_holds
#print axioms fact_the_length_decisiveness_correlation_was_ecological_holds
#print axioms cores_advantage_is_content_and_the_style_mechanism_runs_backwards_holds
#print axioms fact_7_8pct_of_core_criteria_are_verbatim_copies_holds
#print axioms fact_no_criterion_has_two_or_three_raters_holds
#print axioms when_a_contested_criterion_survives_the_majority_captures_it_holds
#print axioms whether_disagreement_ITSELF_predicts_being_dropped_is_unsettled_holds
#print axioms defect_my_own_gauge_variants_were_malformed_holds
#print axioms person_level_harm_COUNTS_are_withdrawn_holds
#print axioms core_serves_the_people_furthest_from_consensus_relatively_better_holds
#print axioms most_of_the_compiled_arms_shortfall_is_item_count_not_lost_personalisation_holds

end Coval
