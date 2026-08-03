#set page(paper: "a4", margin: (x: 2.2cm, y: 2.4cm), numbering: "1")
#set text(font: ("Libertinus Serif", "DejaVu Serif", "serif"), size: 10pt)
#set par(justify: true, leading: 0.62em)
#show heading.where(level: 1): it => block(above: 1.4em, below: 0.7em)[
  #set text(size: 13pt, weight: "bold"); #it.body]
#show heading.where(level: 2): it => block(above: 1.1em, below: 0.5em)[
  #set text(size: 11pt, weight: "bold"); #it.body]
#set table(stroke: 0.4pt + luma(60%), inset: 5pt)

#align(center)[
  #text(16pt, weight: "bold")[What survives an adversarial audit of a public-input values rubric]
  #v(0.3em)
  #text(10pt)[Three measurements on OpenAI's Collective Alignment release, and the
  one hundred and thirty-seven rounds that did not survive]
  #v(0.2em)
  #text(9pt, style: "italic")[2026-07-30 · 141 rounds · every number carries its own confidence card]
]

#v(0.5em)
#line(length: 100%, stroke: 0.6pt)
#v(0.5em)

= Abstract

We audited OpenAI's Collective Alignment release --- 1,078 prompts, 1,012 annotators, 15,248
participant-written evaluation criteria with per-annotator importance ratings, and a compiled
four-criterion rubric per prompt --- across 141 experimental rounds, of which 12 were dispatched to
independent clean-context designers who were given the question and never the algorithm.

The audit's largest single result is negative and concerns the audit itself. One hundred and forty
rounds ran before anyone opened `DATASET_CARD.md`. When it was read, most of what the campaign
believed it had discovered turned out to be the release's own published method description: the
compiled rubric is documented as rewriting all items to positive weight, selecting the four highest
average ratings, enforcing non-conflict, and as "often reflect[ing] the biases of dominant
perspectives". Four of five evidence routes against a faithfulness claim collapsed into a
verification that a documented method does what it documents. Nobody had claimed faithfulness.

Three measurements survive. Each is reported with a confidence card whose entries can independently
veto it.

= 1. What was measured, and what a claim here can mean

Every comparison of a compiled rubric against an uncompiled one requires scoring whether a response
satisfies a criterion. The release *does not ship those labels*, so any external audit must rebuild
that layer. We did, with a local 2-billion-parameter model. That instrument is not a source of
truth and was never used as one: its only required property is *arm-invariance*, that the same
fixed function is applied identically to both arms so its bias cancels in the difference.

That property is now known to fail on the axis that matters. Asking the model whether a reply
*violates* a criterion and reading $1-v$ --- the same quantity by definition --- moves the
core-minus-full contrast from $-0.0223$ to $+0.0708$. The sign changes. The compiled and uncompiled
arms differ precisely in their negatively-rated criteria, and that is where the instrument is least
symmetric.

We therefore partition every claim into *instrument-dependent* and *instrument-free*. Of
twenty-one claims this campaign made, seventeen were instrument-dependent. The three reported below
are not: no model is executed anywhere in their computation.

= 2. Finding A --- the negate step is not visible in the artifact

== The claim being tested

The dataset card documents that the compiler "merge[s], negate[s], and select[s]". Negatively-rated
criteria --- 25.6% of the corpus, phrased affirmatively as descriptions of undesirable behaviour
("Invents fake sources", "Use a violent tone") --- are therefore meant to enter the compiled rubric
in negated form, not to be dropped.

== Why the obvious test does not work

Of 3,905 negatively-rated criteria, *zero* appear verbatim in the compiled rubric, against 372 of
11,343 positive ones (Fisher exact one-sided $p = 3.26 times 10^(-49)$; upper bound on the rate
$7.67 times 10^(-4)$). This does *not* establish dropping. A criterion stating the bad behaviour
affirmatively, placed in a rubric that says "the response should satisfy these", reads as an
instruction to perform it; it must be negated to be usable at all. The zero is a fact about phrasing.

The competing reading --- that the compiled rubric is positive-prescriptive by construction --- is
separately false: 21.7% of its criteria carry prohibition markers, above the corpus's own 19.1% and
19.7%.

== The test that does work

If the content survived in negated form it would remain lexically present. We strip negation from
both sides and take each criterion's maximum overlap against the compiled criteria of *its own
prompt*, across three representations and five metrics, with the positive comparison group matched
separately on rating magnitude, on text length, and on rater count.

#table(columns: (auto, auto, auto, auto, auto, auto),
  align: (left, right, right, right, right, right),
  [*representation | metric*], [*neg*], [*pos*], [*Δ mag*], [*Δ len*], [*Δ raters*],
  [stem\_token | overlap\_min], [0.2535], [0.3626], [−0.0896], [−0.0991], [−0.0450],
  [raw\_token | overlap\_min],  [0.2336], [0.3433], [−0.0883], [−0.0988], [−0.0433],
  [stem\_token | dice],         [0.2070], [0.3062], [−0.0781], [−0.0893], [−0.0371],
  [raw\_token | dice],          [0.1909], [0.2905], [−0.0770], [−0.0892], [−0.0358],
  [char3gram | overlap\_min],   [0.3344], [0.4277], [−0.0767], [−0.0818], [−0.0396],
  [stem\_token | containment],  [0.2172], [0.3034], [−0.0692], [−0.0874], [−0.0332],
  [raw\_token | containment],   [0.1996], [0.2873], [−0.0691], [−0.0873], [−0.0326],
  [raw\_token | idf\_weighted], [0.2229], [0.3095], [−0.0687], [−0.0880], [−0.0312],
  [stem\_token | idf\_weighted],[0.2217], [0.3072], [−0.0683], [−0.0866], [−0.0317],
  [char3gram | dice],           [0.2730], [0.3593], [−0.0664], [−0.0741], [−0.0318],
  [stem\_token | jaccard],      [0.1360], [0.2250], [−0.0661], [−0.0812], [−0.0283],
  [raw\_token | jaccard],       [0.1252], [0.2131], [−0.0640], [−0.0798], [−0.0265],
  [char3gram | jaccard],        [0.1730], [0.2533], [−0.0584], [−0.0705], [−0.0251],
)

*42 of 42* representation × metric × matching cells are negative under all five seeds, and *42 of
42* prompt-clustered 95% intervals exclude zero.

The one confound that could manufacture this runs backwards. Negative criteria are *shorter* --- 88
characters against 101 --- and every overlap metric here divides by a union or a sum, so brevity
inflates their score. It is lower anyway.

#block(fill: luma(96%), inset: 8pt, radius: 3pt, width: 100%)[
*Confidence card.* n_eff = 968 prompts · effect/floor: seed spread ≤0.002 against effects of
0.03–0.10, ratio > 15 · CI width / |effect| ≈ 0.25 · spec survival 42/42 same sign, 42/42 CI
excludes zero · seeds 5 · held-out ABSENT · instrument NONE · prior-art: the negate step is
documented, its absence is not · multiplicity: whole grid reported, no cell selected.
]

*Limit, stated rather than argued away.* Lexical overlap is a weak proxy for content: a criterion
can be captured in entirely different words. Establishing more would require semantic matching,
which puts a second model between the claim and the data --- the thing this section exists to avoid.

= 3. Finding B --- the collective standard is 27% of what people said mattered

The card says the compiled rubric "often reflects the biases of dominant perspectives in our
participant pool". That is a qualitative admission. We give it a size.

For each criterion rated by at least four people, decompose the variance of its importance ratings
into a between-criteria component (a standard people read off) and a within-criteria component
(disagreement about the same criterion).

#table(columns: (auto, auto, auto, auto, auto, auto),
  align: (left, right, right, right, right, right),
  [*rater floor*], [*criteria*], [*ICC(1)*], [*95% CI (prompt)*], [*Krippendorff α*], [*median rater-pair r*],
  [n ≥ 4],  [5,564], [0.2698], [0.2584 – 0.2801], [0.2694], [0.3415],
  [n ≥ 5],  [5,546], [0.2697], [0.2588 – 0.2805], [0.2693], [0.3415],
  [n ≥ 10], [5,191], [0.2691], [0.2567 – 0.2804], [0.2689], [0.3551],
)

The floor that makes the number mean anything: permute *each rater's own ratings* across the
criteria they rated, preserving their scale usage, their extremeness and their mean exactly, and
destroying only the link to the criterion. It returns *0.0006*. The observed value is four hundred
times it.

*Seventy-three percent of the variance in "how important is this criterion" is about who is rating
it.* An aggregate is therefore a summary of a minority of the variance and may not be stated as the
panel's view.

#block(fill: luma(96%), inset: 8pt, radius: 3pt, width: 100%)[
*Confidence card.* n_eff = 968 prompts / 1,158 raters · effect/floor = 0.2698 / 0.0006 ≈ 450 ·
CI width / |effect| = 0.08 · spec survival: three rater floors × two cluster levels × two
independent estimands (ICC, Krippendorff α) all agree to three decimals · seeds 5 · held-out
ABSENT · instrument NONE · prior-art: asserted qualitatively in the card, never sized ·
multiplicity: 3 floors × 2 estimands, all reported.
]

= 4. Finding C --- a hole in the rater-count distribution

#table(columns: (auto, auto, auto, auto, auto, auto),
  align: (left, right, right, right, right, right),
  [*raters per criterion*], [1], [2], [3], [4–9], [≥10],
  [*criteria*], [9,684], [*0*], [*0*], [373], [5,191],
  [*share*], [63.5%], [0.0%], [0.0%], [2.4%], [34.0%],
)

Sixty-three and a half percent of criteria were rated by exactly one person. *Exactly zero* were
rated by two or three. A distribution that jumps from one straight to four is not a sampling curve;
it is a protocol signature --- two collection regimes glued together. The card does not mention it.

Its consequence is structural: any analysis comparing one rater's ratings against another's is
confined to the multiply-rated third of the corpus, and the single-rater majority --- the layer most
likely to carry idiosyncratic personal content --- cannot be examined that way at all.

#block(fill: luma(96%), inset: 8pt, radius: 3pt, width: 100%)[
*Confidence card.* n_eff = 15,248 criteria (exhaustive, not sampled) · effect/floor: N/A, this is a
census · CI: none needed · spec survival: N/A · seeds: N/A, deterministic · held-out: N/A ·
instrument NONE · prior-art: absent from the card · multiplicity: none.
]

= 5. What did not survive, and why that matters more

#table(columns: (auto, auto),
  align: (left, left),
  [*Withdrawn*], [*Why*],
  [12.46% of people are harmed by compilation],
  [Between-person spread 0.0687 against a within-person split-half floor of 0.0613. The count was a
   statement about how many prompts each person happened to see.],
  [The compiled rubric adds no information],
  [A zero-LLM sort by average rating matches it --- but that *is* the documented algorithm.],
  [Core beats a human peer at respecting vetoes],
  [Held-out splits: 7 of 12 partitions fail; the confirmation-half range crosses zero.],
  [The consensus gradient, +0.099 at p = 0.0025],
  [Adding the person's own predictability kills it entirely under one baseline and attenuates it to
   +0.074 under the other.],
  [Core is an unfaithful compilation, on four routes],
  [Nobody claimed faithfulness. The card documents the filter as the method.],
)

Twelve independent clean-context designs were commissioned across six attack vectors. Two returned
UNVERIFIED rather than a number when their own positive controls failed --- one diagnosing that the
weighted and unweighted summaries of the corpus correlate at $r = 0.957$, making its question nearly
unidentifiable before it starts. Those refusals are the most valuable outputs in the set.

= 6. The methodological result

The audit's own failure modes were more consistent than its findings.

*A defect measured where it occurs is not a defect measured where the claim lives.* Re-scoring the
entire grid under a different batching changed *every one* of 75,244 judgements --- zero identical,
mean $|Delta| = 9.5 times 10^(-3)$ --- and moved every published concordance by at most 0.0007.

*A container that cannot represent a state reports its absence as good news.* The claim graph held
seventeen of the campaign's own claims and zero refutations, because retractions had been entered as
settled claims *about* withdrawals rather than as refuted claims. A spotless record was an ontology
with no word for error.

*And the object's own description is part of the object.* One hundred and forty rounds, twelve
independent designs and several hundred thousand model forward passes went into rediscovering a
paragraph that had been sitting in `DATASET_CARD.md` the whole time.
