r140 -- the polarity route, rebuilt without the instrument, after two self-inflicted corrections.

WHAT WAS CHALLENGED AND WHAT IT COST
------------------------------------
The polarity route originally read: core loads on the negative block at beta_neg/beta_pos = 0.094
against a "faithful" benchmark of 0.362, therefore the compilation is unfaithful. Two objections
landed and both were right.

1. THE BENCHMARK WAS ASSERTED, NOT ARGUED. 0.362 is the negative block's COUNT share. Nothing
   established that a faithful compilation weights by count. By importance share (sum of |rating|)
   the benchmark is 0.3818; by discriminability it would be something else again. A test that needs
   the analyst to pick a benchmark number is a bad test.

2. THE INSTRUMENT IS UNRELIABLE ON EXACTLY THIS AXIS. The sampled gauge run showed that asking the
   judge "does the reply VIOLATE the criterion" and reading 1-v -- the same quantity by definition
   -- moves core-minus-full_signed from -0.0223 to +0.0708. Sign change. P(satisfy) is not
   1-P(violate) for this model, and the negative quarter is where the arms differ.

So the route was rebuilt with no benchmark and no judge.

ATTEMPT ONE, AND WHY IT FAILED
------------------------------
Verbatim retention: of 3,905 negatively-rated full criteria, ZERO appear verbatim in core, against
372 of 11,343 positive ones. Fisher exact one-sided p = 3.26e-49; 95% upper bound on the negative
copy rate 7.67e-04. (The logistic reported earlier as OR 0.0000 [0.0000, 0.0000] is a numerical
divergence under perfect separation, not an estimate, and is withdrawn.)

That zero does NOT establish dropping. First reading -- "core is positive-prescriptive by
construction so a negative criterion can never match" -- is FALSE: 846 of core's 3,899 criteria
(21.7%) carry prohibition markers, a HIGHER rate than full's own 19.1% and 19.7%. core writes
"Do not frame vaccine policy...", "Avoid framing the child's desire...".

But the reading returns sharper and this time it holds. full's negative criteria state the bad
behaviour AFFIRMATIVELY -- "Invents fake sources", "Use a violent tone". Placed in a rubric that
says "the response should satisfy these", such a line reads as an instruction TO do it. It must be
negated to be usable at all. So the verbatim zero is a fact about PHRASING, not about retention,
and the verbatim channel cannot test polarity retention. Route withdrawn.

ATTEMPT TWO, WHICH WORKS
------------------------
If the content survived in rephrased form, it should still be lexically present. Strip negation
words from both sides, tokenise to content words of four or more characters, and take each full
criterion's maximum Jaccard overlap against the core criteria of its OWN prompt:

  negative criteria                       mean 0.1246   9.76% reach >= 0.30
  positive criteria                       mean 0.2121  23.74% reach >= 0.30
  magnitude-matched positive (20 draws)   mean 0.1911  (sd 0.0020)

  negative minus magnitude-matched positive = -0.0665,  z = -32.8

No benchmark is chosen and no model is run. The comparison is relative, so a uniformly weak proxy
cancels; only a proxy that is DIFFERENTIALLY weak on negative criteria could manufacture this.

THE CONFOUND, AND IT RUNS THE WRONG WAY FOR THE FINDING
--------------------------------------------------------
Negative criteria are shorter (88 characters against 101). Jaccard divides by the UNION, so a
shorter criterion has a smaller union and, for the same intersection, a HIGHER score. Length should
inflate the negative block's overlap. It is lower anyway.

WHAT REMAINS UNTESTED
---------------------
Lexical overlap is a weak proxy for content: a criterion can be captured in entirely different
words. Establishing that would need semantic matching, which this project has refused throughout
because it would put a second model between the claim and the data. So the honest statement is
lexical presence, and it is stated as that.
