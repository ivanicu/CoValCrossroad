"""The twenty-five rounds the claim graph never heard about, including six retractions.

The graph was last built at r174. Since then r175-r199 landed, and the gap matters more than a
normal staleness would, because six of those rounds RETRACTED something -- and a graph that shows
13 standing claims while six of them have been withdrawn elsewhere is not merely out of date, it
is actively misleading. `db/ledger.py` prints "3 withdrawn" and the true count is higher.

This extends rather than rebuilds, for the same reason HEADLINES.py did not edit the rounds: the
existing nodes are a record of what was believed and when, and the kill edges are what make the
retractions legible. Overwriting them would produce a cleaner graph that has forgotten why it is
clean.

WHAT GOES IN, in three groups:

  RETRACTIONS   six claims withdrawn since r174, each with the round that killed it and what the
                killing showed. Two of them are retractions OF retractions -- r195 corrected the
                reason r194 gave, and r183 withdrew r182's explanation while leaving its
                measurement standing -- and the graph has to be able to express that without
                pretending the intermediate state never existed.
  FINDINGS      the substantive results, each with its instrument named where one is involved.
  INSTRUMENTS   two nodes for the tools built in r197 and r198, because a project that builds a
                guard and does not record what the guard is for has built a file.

EVERY NODE CARRIES ITS UNIT after HEADLINES.py, and the descriptions say "of prompts" or "of
assessments" explicitly. That is the whole lesson of r191-r199 and it belongs in the ontology, not
only in the prose.
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))

from derivation_chain import edge, evid, node  # noqa: E402


def main() -> int:
    N: dict[str, int] = {}

    # ================================================================ RETRACTIONS
    N["length-by-contestedness"] = node(
        "length-by-contestedness", "my_claim",
        "WITHDRAWN. That the length preference is weaker on prompts the panel says have a single "
        "correct answer. Published in r191 as +5.0pp (z +2.1, non-monotonic) and used to correct "
        "r177's null. r194 found the sign unstable across specifications; r195 identified the "
        "mechanism exactly -- one anchor prompt with 929 assessments, subjectivity 0.803 against a "
        "pool median 0.650 so it lands in the contested bin, and its own longest-first rate 54.3% "
        "against a 34% baseline. Removing that ONE prompt collapses the gap from +4.3pp to +0.4pp "
        "under assessment weighting; under prompt weighting it is ~0 either way.",
        d=8, status="refuted")
    evid(N["length-by-contestedness"], "r195-specification-grid",
         "8 cells over weighting x bins x anchor; sign flips 5/3; the effect is an interaction "
         "between assessment weighting and one prompt, not a main effect of either", 8)

    N["cutpoints-caused-the-disagreement"] = node(
        "cutpoints-caused-the-disagreement", "my_claim",
        "WITHDRAWN, and it was my own retraction's stated reason. r194 attributed the r191/r194 "
        "disagreement to cut points computed on a neighbouring population. r195 re-read r191's "
        "source: it computes its percentiles on exactly the prompts it analyses. The verdict of "
        "the retraction was right and its mechanism was wrong, which is its own defect -- anyone "
        "applying the stated lesson would not have caught the real cause.",
        d=8, status="refuted")
    evid(N["cutpoints-caused-the-disagreement"], "r195-source-reread",
         "r191 line: qs = np.percentile([psub[p] for p in hits if p in psub], ...) -- the "
         "analysed population", 8)

    N["south-africa-not-a-bloc"] = node(
        "south-africa-not-a-bloc", "my_claim",
        "WITHDRAWN. r182 read South Africa's -2.0pp within-minus-cross agreement as showing the "
        "group carrying the demographic dissent effect is not a coherent values bloc. r183 "
        "measured the estimator's own resolution floor at 2.57pp (p95 over 20 random labellings) "
        "and the per-group permutation null puts that -2.0pp at z -1.4. The DEMOGRAPHIC EFFECT "
        "stands; the explanation does not.",
        d=7, status="refuted")
    evid(N["south-africa-not-a-bloc"], "r183-resolution-floor",
         "negative control p95 = 0.0257 against a preregistered 0.02 bound; read as a floor "
         "rather than relaxed", 8)

    N["blocs-are-values-groups"] = node(
        "blocs-are-values-groups", "my_claim",
        "WITHDRAWN as stated. r183 found Netherlands (+6.25%) and Mexico (+5.96%) cluster above "
        "chance -- 2 of 28 demographic levels, the only demographic signal in the release. r184 "
        "showed the between-country matrix is one-dimensional and a pure CONSISTENCY model "
        "(agreement = chance + q_i*q_j) reproduces 69% of the off-diagonal, with the second "
        "spectral component BELOW what shuffled labels produce. The clustering is real; calling "
        "it a values group is not established.",
        d=7, status="refuted")
    evid(N["blocs-are-values-groups"], "r184-spectral-null",
         "second-component share 37.6% observed against 39.6% +/- 2.6% permuted, z -0.8", 7)

    N["dissenters-criteria-are-deleted"] = node(
        "dissenters-criteria-are-deleted", "my_claim",
        "WITHDRAWN to UNVERIFIED. Whether the compilation drops criteria written by people who "
        "dissent. Raw contrast -2.4pp at z -2.8 iid; clustered on author and prompt it is z -1.8 "
        "and crosses zero, while the stratified version excludes zero at z -2.4. Two "
        "specifications one covariate apart landing on opposite sides, on non-monotonic quartiles "
        "(10.0/6.7/6.3/7.6). The specification curve does not survive its own grid.",
        d=7, status="refuted")
    evid(N["dissenters-criteria-are-deleted"], "r181-clustered-and-monotonic",
         "clustering inflates the SE 1.6x; rank correlation across quartile means -0.40, not "
         "-1.00", 7)

    N["band-share-is-67-5"] = node(
        "band-share-is-67-5", "my_claim",
        "WITHDRAWN as a point value. r179 published that the crowd rubric closes 67.5% of the "
        "band between chance and the leave-one-out human ceiling. r196 recomputed the ceiling "
        "across weighting and anchor: it ranges 61.5-62.3%, so the band share is 66-67% and must "
        "be quoted as a range. The comparison itself is unaffected.",
        d=8, status="refuted")
    evid(N["band-share-is-67-5"], "r196-ceiling-grid",
         "oracle 61.9 / 62.3 / 61.5 / 61.5 across assessment|prompt x anchor in|out", 8)

    # ================================================================ FINDINGS
    N["rewrite-is-targeted"] = node(
        "rewrite-is-targeted", "fact",
        "The card's 'rewrites all rubric items to have positive weight' is real and targeted: "
        "82.5% of core items whose source carried a NEGATIVE weight have their polarity flipped, "
        "against 6.1% of positive-weight sources. z +33.2 over 2,356 matchable core items. r171 "
        "had marked this claim UNTESTABLE.",
        d=8, status="settled")
    evid(N["rewrite-is-targeted"], "r176-polarity-flip",
         "221/268 negative-weight sources flipped vs 127/2088 positive", 8)

    N["rewrite-loses-the-item"] = node(
        "rewrite-loses-the-item", "my_claim",
        "The rewrite preserves the POPULATION and loses the ITEM. Negative-weight sources flip "
        "sign with 80% of their magnitude (-0.1056 -> +0.0850, predicted +0.1056) and positive "
        "sources pass through at 106%. But per-item correlation between source and compiled "
        "encoding is -0.138 for FLIPPED criteria against +0.805 for unflipped -- a faithful "
        "per-item flip would give about -0.80. Negative normative content survives as a "
        "population average, not as an individual statement. INSTRUMENT: Qwen3.5-2B-Base judge, "
        "both arms on the same four responses.",
        d=7, status="settled")
    evid(N["rewrite-loses-the-item"], "r189-encoding-across-rewrite",
         "612 matched source->core pairs with an identified author and both tensors", 7)

    N["post-hoc-rationalisation"] = node(
        "post-hoc-rationalisation", "my_claim",
        "Criteria are partly descriptions of the response their author had already chosen. The "
        "card's task order puts rubric authoring LAST. Difference-in-differences holding a PAIR "
        "of responses fixed and scoring two authors' criteria on the same two texts: +0.0478 "
        "[+0.0336, +0.0620], z +6.6 over 4,504 author pairs, 14.2% of the judge's within-criterion "
        "range. Controlling for response quality made the effect LARGER, not smaller (+0.0261 "
        "raw). INSTRUMENT: Qwen3.5-2B-Base judge; the DiD cancels response quality exactly.",
        d=7, status="settled")
    evid(N["post-hoc-rationalisation"], "r187-did",
         "8,216 sole-authored criteria, 947 prompts, 587 authors; own choice best-satisfied 37.3% "
         "vs 25% chance", 7)

    N["compilation-passes-it-through"] = node(
        "compilation-passes-it-through", "my_claim",
        "The distillation into coval_core neither concentrates nor removes the rationalisation. "
        "Within one author on one prompt, criteria that survive encode the author's prior choice "
        "+0.0131 more than those dropped -- 0.06 sd, z +1.1 against a within-group permutation "
        "that shuffles WHICH criteria survived. So the core rubric inherits the first-stage defect "
        "in full.",
        d=7, status="settled")
    evid(N["compilation-passes-it-through"], "r188-within-author",
         "373 (author, prompt) groups with mixed survival, 1,128 criteria", 7)

    N["apparatus-is-coherent"] = node(
        "apparatus-is-coherent", "fact",
        "A positive control on the whole apparatus, found while looking for something else. Four "
        "independently produced quantities -- the judge's satisfaction scores, the criterion text, "
        "the annotator's signed weight and the annotator's ranking -- agree in sign and in order "
        "across all four weight bands: encoding runs -0.0719 / +0.0395 / +0.0968 / +0.1199 from "
        "negative to positive weight, corr +0.379 over 8,217 criteria. Any one being broken would "
        "show as a flat or scrambled column.",
        d=8, status="settled")
    evid(N["apparatus-is-coherent"], "r188-weight-band-monotonicity",
         "monotone across four bands; expected because a negatively weighted criterion SHOULD be "
         "less satisfied by its author's choice", 8)

    N["veto-is-about-the-responses"] = node(
        "veto-is-about-the-responses", "fact",
        "The veto is the most reliable channel in the release and it identifies CONTENT, not "
        "raters. Split-half across half-panels: Spearman-Brown +0.690 for whether anything was "
        "flagged, +0.798 for how many, and +0.827 for WHICH individual response -- the strict "
        "version, over 1,288 (prompt, response) pairs. Control on the same prompts with the same "
        "code: prompt importance +0.581. Rate: 63.6% of assessments, 67.5% of prompts.",
        d=8, status="settled")
    evid(N["veto-is-about-the-responses"], "r192-veto-gate",
         "322 prompts with >=6 asked assessments; the rater side is blocked by the 5-item ceiling "
         "and is not needed", 8)

    N["flagged-responses-hedge-less"] = node(
        "flagged-responses-hedge-less", "my_claim",
        "What people converge on calling unacceptable is the answer that does not concede the "
        "question is open. Most-flagged minus least-flagged response WITHIN prompt: hedging "
        "-0.22, z -5.6 against a 300-permutation null, 1 of 7 testable axes surviving |z|>3. NOT "
        "length (z -0.8). Neither of the card's two named categories. And independently: the "
        "response the crowd's own criteria score worst is the most-flagged one 56.1% of the time "
        "against 25% chance, z +10.6, with within-prompt corr(rubric, flag) = -0.596.",
        d=7, status="settled")
    evid(N["flagged-responses-hedge-less"], "r193-two-routes",
         "regex route and judge route built to fail independently; refusal axis UNTESTABLE, 5 of "
         "4,312 candidates carry one", 7)

    N["nonconformity-is-a-person"] = node(
        "nonconformity-is-a-person", "fact",
        "Departing from the prompt's majority is a stable individual trait. Split-half "
        "reliability Spearman-Brown +0.485 over 929 raters, permutation null -0.003, and it "
        "SURVIVES residualising on which prompts the rater drew (+0.486; the assignment's own "
        "reliability is +0.015). Length preference by contrast is +0.107, UNVERIFIED. Veto "
        "propensity is untestable -- the 5-item ceiling leaves halves of two.",
        d=7, status="settled")
    evid(N["nonconformity-is-a-person"], "r180-split-half",
         "effort proxy (rationale length) correlates with nonconformity at -0.045, so the "
         "low-effort reading is unsupported though not excluded", 7)

    N["strata-fields-describe-the-prompt"] = node(
        "strata-fields-describe-the-prompt", "fact",
        "Of the three self-reported assessment fields, two really do describe the prompt and one "
        "does not. importance S-B +0.706 prompt / +0.799 rater; subjectivity +0.724 / +0.701 -- "
        "BOTH, so a stratum built from one assessment's answer mixes a prompt property with a "
        "person property. representativeness +0.177 / +0.833 -- a RATER TRAIT, licensing no "
        "corpus-level claim, and its lowest scale option is used ZERO times in 11,023 assessments.",
        d=8, status="settled")
    evid(N["strata-fields-describe-the-prompt"], "r191-both-split-halves",
         "prompt side on prompts with >=6 raters, rater side on raters with >=6 assessments", 8)

    # ================================================================ INSTRUMENTS
    N["static-scan-is-insufficient"] = node(
        "static-scan-is-insufficient", "instrument",
        "A NEGATIVE RESULT ABOUT A METHOD, kept rather than deleted. An AST scan over 53 round "
        "files for assessment-weighted means found 4 sites, all legitimate on reading -- and "
        "scores ZERO hits on r191, the one file known to have produced a false finding through "
        "exactly that defect, because r191 accumulates with .extend() and means a flat list. A "
        "shape-based scan finds the shapes people happen to write. Its own calibration check also "
        "caught a broken glob that would have reported a clean bill over zero files.",
        d=8, status="settled")
    evid(N["static-scan-is-insufficient"], "r197-population-audit",
         "53 files, 4 P1 sites, 55 P2 sites, 0 hits on the motivating case", 8)

    N["runtime-guard"] = node(
        "runtime-guard", "instrument",
        "covalx.estimand.mean_by refuses a mean over grouped data unless the caller names whether "
        "the unit is the OBSERVATION or the GROUP, and refuses the observation form when the two "
        "disagree by more than TOL=0.005. 11 attack vectors pass; it fires on r191's own data "
        "(0.3730 vs 0.3562). Its FIRST version used a share threshold -- a shape test, one round "
        "after shape testing was diagnosed as the failure -- and its own attack suite killed it. "
        "Ceiling: np.mean remains one import away and no library can close that.",
        d=8, status="settled")
    evid(N["runtime-guard"], "r198-attack-suite",
         "A7 (every row its own group) failed v1 because the estimands coincide there; v2 tests "
         "the outcome instead", 8)

    N["headlines-carry-their-unit"] = node(
        "headlines-carry-their-unit", "fact",
        "Re-derived through the guard, 5 of 7 published headline means never named their unit and "
        "move by more than TOL when it is named. The largest gap is the veto rate and it runs the "
        "OPPOSITE way from every other row -- 63.6% per assessment against 67.5% per prompt, "
        "because heavily-rated prompts are vetoed LESS. No single sign rule would have been right. "
        "Nothing is overturned: every refused claim clears its null under both weightings.",
        d=8, status="settled")
    evid(N["headlines-carry-their-unit"], "HEADLINES.py",
         "generated from the data, re-runnable; also surfaces a third specification axis -- which "
         "population clears the filter -- worth 0.8pp on the ceiling", 8)

    # ================================================================ THE KILLERS
    # A refuted my_claim REQUIRES an incoming overturns edge -- the schema enforces it, and that
    # constraint is the reason this file exists in the shape it does.
    # THREE SCHEMA REFUSALS BEFORE THIS RAN, and each was the ontology correcting my vocabulary:
    #   1. kinds "inference" and "measurement" -- neither exists; the graph knows my_claim, fact,
    #      counterexample, control, instrument and eighteen others, and "inference" is a word I
    #      brought with me from the prose.
    #   2. status "withdrawn" and "standing" -- also mine. The graph says refuted and settled, and
    #      status_domains.py enforces which kinds may carry which.
    #   3. kind "result" for the killers -- also absent. They are counterexamples and controls,
    #      which is a sharper description than "result" and one I would not have written unprompted.
    # A vocabulary that lives only in my prose is not the ontology. Three rounds ago I wrote that
    # prose is what a reader gets; here the database made the opposite point, that prose is what
    # the writer gets away with.
    for nm, kind, desc, dlev, src in [
        ("r195-anchor-mechanism", "counterexample",
         "One prompt with 929 assessments, subjectivity 0.803 (pool median 0.650) so it sits in "
         "the contested bin, longest-first rate 54.3% against a 34% baseline. Removing it "
         "collapses the effect tenfold under assessment weighting and changes nothing under "
         "prompt weighting.", 8, ["length-by-contestedness"]),
        ("r195-cutpoints-were-correct", "counterexample",
         "r191 computes its percentiles on exactly the prompts it analyses; the cut points were "
         "never the problem.", 8, ["cutpoints-caused-the-disagreement"]),
        ("r183-resolution-floor-2p57", "control",
         "20 random labellings give a p95 max|within-cross| of 2.57%, above the preregistered "
         "0.02 bound. Read as a resolution floor rather than relaxed; the per-group permutation "
         "null puts South Africa's -2.0pp at z -1.4.", 8, ["south-africa-not-a-bloc"]),
        ("r184-consistency-model", "counterexample",
         "Agreement = chance + q_i*q_j reproduces 69% of the between-country off-diagonal, and "
         "the second spectral component (37.6%) is BELOW the permuted 39.6% +/- 2.6%.", 7,
         ["blocs-are-values-groups"]),
        ("r181-clustering-and-monotonicity", "control",
         "Clustering on author and prompt inflates the SE 1.6x and the contrast crosses zero; the "
         "quartile means are non-monotonic at 10.0/6.7/6.3/7.6, rank correlation -0.40.", 7,
         ["dissenters-criteria-are-deleted"]),
        ("r196-ceiling-is-a-range", "counterexample",
         "The leave-one-out ceiling ranges 61.5-62.3% across weighting and anchor, so any band "
         "share computed from it is a range.", 8, ["band-share-is-67-5"]),
    ]:
        N[nm] = node(nm, kind, desc, d=dlev, status="settled")
        for target in src:
            if target in N:
                edge(N[nm], N[target], "overturns", note="kill edge")

    # ================================================================ EDGES
    for src, dst, kind, note in [
        ("length-by-contestedness", "cutpoints-caused-the-disagreement", "refines",
         "the retraction was right; its stated mechanism was not"),
        ("rewrite-is-targeted", "rewrite-loses-the-item", "supports",
         "the flip is real, which is what makes the per-item loss measurable at all"),
        ("post-hoc-rationalisation", "compilation-passes-it-through", "supports",
         "the second stage inherits the first stage's defect unchanged"),
        ("apparatus-is-coherent", "post-hoc-rationalisation", "supports",
         "the rationalisation sits inside an apparatus whose parts agree, so it is not an "
         "artefact of one of them being wrong"),
        ("veto-is-about-the-responses", "flagged-responses-hedge-less", "supports",
         "the channel is reliable, so asking what it is about is a well-posed question"),
        ("nonconformity-is-a-person", "blocs-are-values-groups", "refutes",
         "individual disposition is a stronger signal (+0.486) than any group membership shipped "
         "here"),
        ("static-scan-is-insufficient", "runtime-guard", "depends_on",
         "the scan's failure is the argument for enforcement at the point of computation"),
        ("runtime-guard", "headlines-carry-their-unit", "tested_by",
         "a guard nothing calls is a file"),
        ("headlines-carry-their-unit", "band-share-is-67-5", "overturns",
         "the ceiling is a range, so the share is too"),
        ("strata-fields-describe-the-prompt", "length-by-contestedness", "supports",
         "the stratifier was valid; the weighting was not, which is why the lean died and the "
         "field survived"),
    ]:
        if src in N and dst in N:
            edge(N[src], N[dst], kind, note=note)

    print(f"added {len(N)} nodes for r175-r199")
    print(f"  FOUR schema refusals before this ran, each correcting my vocabulary rather than my")
    print(f"  facts: kinds 'inference'/'measurement'/'result' (none exist), statuses")
    print(f"  'withdrawn'/'standing' (the graph says refuted/settled), and edge kinds")
    print(f"  'supersedes'/'contradicts'/'motivates'/'enables' (the graph has overturns, refutes,")
    print(f"  depends_on, tested_by). Every one was a word I brought from the prose. The ontology")
    print(f"  is the constraint set, and prose is what the writer gets away with.")
    withdrawn = [k for k in N if k in (
        "length-by-contestedness", "cutpoints-caused-the-disagreement", "south-africa-not-a-bloc",
        "blocs-are-values-groups", "dissenters-criteria-are-deleted", "band-share-is-67-5")]
    print(f"  of which WITHDRAWN: {len(withdrawn)}")
    for w in withdrawn:
        print(f"    {w}")
    print(f"  two of these are retractions OF retractions: cutpoints-caused-the-disagreement")
    print(f"  (r195 correcting r194's stated reason) and south-africa-not-a-bloc (r183 withdrawing")
    print(f"  r182's explanation while its measurement stands).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
