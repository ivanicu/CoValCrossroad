"""Write the normative-chain phase (r142-r153) into the claim graph.

Twelve rounds produced claims, four retractions and six method defects, and all of it currently
exists only as prose in commit bodies. Prose stating a relation is a missing edge: "r148 overturned
r146's headline" is a sentence a future reader has to find and believe, while an `overturns` edge is
a thing a query returns. This makes them queryable.

THE DEFECTS ARE ENTERED AS FIRST-CLASS NODES, not as footnotes on the claims they nearly ruined.
Six checks in this phase were unfit -- a subspace measure whose null equalled its observation, a
verdict function with no NEITHER branch, a tolerance below the precision of the file it read, a
transposed nerve orientation that enumerated 2^39 subsets, a boundary-matrix index swap that three
green controls never exercised, and a loader that saw one of the release's two message schemas.
Every one was caught by something -- a null, a control, a printed count -- and recording WHICH
mechanism caught which defect is the only way the next round knows what to keep running.

An audit whose ontology has no word for its own errors reports none.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json  # noqa: E402

from derivation_chain import edge, evid, node, q  # noqa: E402

R = "13_normative_chain"


def build() -> dict:
    N: dict[str, int] = {}

    # ---------------------------------------------------------------- facts, instrument-free
    N["provenance-signature"] = node(
        "provenance-signature", "fact",
        "Criterion authorship is recoverable from the release: 9,684 of 15,248 criteria have "
        "exactly one rater, 5,564 have four or more, and exactly zero have two or three. An item "
        "only its author ever saw was authored in that author's own session.",
        d=8, status="settled")
    evid(N["provenance-signature"], "r142-provenance-recovery",
         "empty band at n=2,3 where a single-population binomial expects 1,235; prohibition share "
         "31.1% self-authored vs 16.0% pre-seeded as an independent second signature", 8)

    N["force-never-elicited"] = node(
        "force-never-elicited", "fact",
        "Normative force was never collected. Across all 15,248 criteria, absolute-force markers "
        "appear in 0.72%, scope qualifiers in 0.60%, exceptions in 0.72%. Only 'should' is common "
        "at 13.06%, and it does not distinguish a veto from a mild preference.",
        d=8, status="settled")
    evid(N["force-never-elicited"], "r143-markers",
         "measured on the full population, not the study corpus, because selecting on extreme "
         "weight could select terse criteria and manufacture the result", 8)
    evid(N["force-never-elicited"], "r143-annotator-control",
         "two model families agree at kappa 0.152 on force and 0.010 on generality for real "
         "criteria, while both score 0.833-1.000 on constructed criteria that state the value -- "
         "so the instruments read these fields when the text carries them", 7)

    N["veto-is-distinct"] = node(
        "veto-is-distinct", "fact",
        "The unacceptable block is not the bottom of the ranking. People mark their own "
        "top-ranked response unacceptable 2.6% of the time; a rank-only model reaches McFadden "
        "pseudo-R2 of 0.0559; 82.9% veto nothing and 1.1% veto all four.",
        d=8, status="settled")
    evid(N["veto-is-distinct"], "r150-veto", "coverage is 100% of 18,562 assessments", 8)

    N["menu-can-fail"] = node(
        "menu-can-fail", "fact",
        "Rejecting the entire menu concentrates on particular prompts 5.01x beyond what rater "
        "style explains, under a permutation preserving each person's own rejection count.",
        d=8, status="settled")
    evid(N["menu-can-fail"], "r151-none-of-the-above",
         "variance 0.004163 observed vs 0.000830 null, tight across five seeds", 8)
    evid(N["menu-can-fail"], "r152-what-fails",
         "non-rejecting raters veto more on exactly those prompts, r=+0.312, replicating on five "
         "held-out splits; disagreement is less than half as strong at +0.134", 8)

    # ---------------------------------------------------------------- claims
    N["loss-does-not-compose"] = node(
        "loss-does-not-compose", "my_claim",
        "Information loss along the chain is not the product of its stages. Stage cosines are "
        "+0.697, +0.710 and +0.534, multiplying to 0.264, while the observed end-to-end composite "
        "is +0.571 -- more than twice what the stagewise accounting predicts.",
        d=7, status="partial")
    evid(N["loss-does-not-compose"], "r144-information-loss",
         "n=968 conversations; what each arrow destroys is largely orthogonal to what the next "
         "destroys", 7)

    N["group-not-individual"] = node(
        "group-not-individual", "my_claim",
        "The unserved third has a group-level bearer and no individual one. Between-person spread "
        "is 1.06x its within-person floor, so no person may be named; but within prompt and "
        "matched on decisiveness, South African participants are unserved 15.6 points more than "
        "co-panelists on a 34% base.",
        d=7, status="partial")
    evid(N["group-not-individual"], "r145-who-is-unserved",
         "15 of 45 groups clear BH within prompt against 11 of 29 in the confounded version -- "
         "removing prompt difficulty ADDED power rather than explaining the effect away", 7)

    N["menu-is-binding"] = node(
        "menu-is-binding", "my_claim",
        "No aggregation rule could have served them. A chooser optimising specifically for the "
        "group reaches 0.669, while a size-matched random subgroup reaches 0.746 from its own "
        "oracle -- so the candidate set fails them 7.8 points beyond what internal heterogeneity "
        "explains. Inclusion costs 1.48 other people per 1 gained.",
        d=7, status="partial",
        props={"limitation": "the size-matched control ran at a single seed; seed spread is "
                             "UNCOMPUTED, not small"})
    evid(N["menu-is-binding"], "r149-price-of-inclusion", "human rankings only, no model run", 7)

    N["release-cannot-explain-itself"] = node(
        "release-cannot-explain-itself", "my_claim",
        "The property determining menu failure is not in the release. Seven topic families and "
        "nine response-text features -- similarity, length, refusal, hedging -- all null, with an "
        "MDE of |r|=0.085 bounding the null rather than merely reporting it.",
        d=7, status="settled")
    evid(N["release-cannot-explain-itself"], "r152-what-fails", "topics null, max |r| 0.024", 7)
    evid(N["release-cannot-explain-itself"], "r153-menu-itself",
         "nothing explains more than 0.3% of the variance", 7)

    N["departure-from-the-line"] = node(
        "departure-from-the-line", "fact",
        "For the serving outcome the arithmetic line has slope k=+0.50746, fit on this outcome "
        "rather than imported: half of any group's level converts into a core-versus-full "
        "differential automatically, before compilation does anything. The estimand is therefore "
        "the departure from that line, never the raw difference.",
        d=8, status="settled",
        props={"note": "fcaa949 used k=0.26514 for a continuous agreement error; importing it "
                       "would have been the same class of error the correction exists to catch"})
    evid(N["departure-from-the-line"], "r148-departure-from-the-line",
         "positive control recovers planted effects at a flat 74.9% across g=0.01,0.02,0.04 with "
         "z=2.63 at the largest, MDE 0.0475; the null is bounded, excluding departures above "
         "+0.028, not clean", 7)

    # ---------------------------------------------------------------- retractions
    ret = [
        ("compilation-adds-cost",
         "Compilation doubles the worst group's disadvantage: core-minus-full is +0.0418 for "
         "South Africa.",
         "departure-from-the-line",
         "92% of that differential is the arithmetic line. Fit on this outcome k=+0.50746, so the "
         "line predicts +0.0387 and the departure is +0.0035 [-0.0214,+0.0284], p=0.78, inside a "
         "matched synthetic band, with 0 of 43 groups BH-significant.",
         "r148-departure-from-the-line"),
        ("content-preserved-force-lost",
         "A pipeline that records only content preserves content and loses force, and the loss is "
         "invisible to any audit that reads text.",
         "force-never-elicited",
         "Force never entered the pipeline, so compilation cannot have lost it. The accusation was "
         "aimed one stage too late.",
         "r143-markers"),
        ("veto-block-partial-coverage",
         "Only 330 of 1,100 prompts carry the unacceptable block.",
         "veto-is-distinct",
         "The block is present on 100% of 18,562 assessments. My loader kept only NON-EMPTY veto "
         "sets, so 330 was the count of prompts where somebody cast a veto, reported as the count "
         "where the question was asked -- an availability claim in the flattering direction.",
         "r150-veto"),
        ("nonbinary-veto-rate",
         "Non-binary participants mark 1.606 responses unacceptable against 0.865 for others.",
         "veto-is-distinct",
         "Computed on the subset conditioned on someone having vetoed. Unconditionally the overall "
         "mean is 0.285 and the group did not clear the n>=50 floor at all.",
         "r150-veto"),
        ("subjectivity-inversion-prompt-level",
         "At the prompt level, full rejection goes with believing the answer does NOT depend on "
         "values.",
         "release-cannot-explain-itself",
         "r=-0.066, p=0.030 alone, and NOT significant under BH once the seven topic features join "
         "the family. Significant in the small family, gone in the honest one. The person-level "
         "version stands on its own data.",
         "r152-what-fails"),
    ]
    for name, stmt, killer, why, exp in ret:
        rid = node(name, "my_claim", stmt, d=4, status="refuted")
        edge(N[killer], rid, "overturns", note=why)
        evid(rid, exp, why, 7)
        N[name] = rid

    # ---------------------------------------------------------------- controls that did the work
    ctrl = [
        ("control-annotator-positive",
         "Same annotator, same wording, on criteria whose field value is unambiguous by "
         "construction: both families score 0.833-1.000 against chances of 0.167-0.333.",
         "force-never-elicited",
         "Without it, near-chance agreement on real criteria would have been silence rather than "
         "evidence about the text."),
        ("control-leave-one-out-line",
         "The arithmetic line is fit excluding the group being judged.",
         "compilation-adds-cost",
         "Fitting on all groups let a departing group drag the line toward itself; planted effects "
         "returned at 61-65% and the MDE was 0.056, larger than the differential under test. "
         "Leave-one-out raised recovery to a flat 74.9% and cut the MDE to 0.0475."),
        ("control-size-matched-oracle",
         "A random subgroup of the same size drawn from the same panel, carrying the identical "
         "internal-heterogeneity penalty and no group identity.",
         "menu-is-binding",
         "An oracle below 1.0 can mean the candidate set fails the group or merely that its "
         "members disagree with each other; only this separates them."),
        ("control-rejection-permutation",
         "Each person's own rejections permuted across the prompts THEY rated.",
         "menu-can-fail",
         "A harsh rater stays exactly as harsh, so whatever concentration survives is the part "
         "rater style cannot explain."),
    ]
    for name, stmt, target, why in ctrl:
        cid = node(name, "control", stmt, d=8, status="settled")
        edge(cid, N[target], "acquits" if target in N else "supports", note=why)
        N[name] = cid

    # ---------------------------------------------------------------- my own method defects
    defects = [
        ("defect-degenerate-subspace",
         "Counting preserved dimensions by principal angles returned exactly 3.00 at every arrow "
         "and every cutoff -- and 3.00 in the null. In a 3-dimensional ambient space every stage "
         "spans everything, so the measure could not have read anything but perfect preservation.",
         "running the null alongside the observation"),
        ("defect-verdict-without-neither",
         "A verdict function picked whichever of two mechanisms had the larger |r| and named it. "
         "With both at 0.03 it announced a mechanism -- a label attached to a comparison between "
         "two nulls.",
         "noticing no feature survived BH while a verdict was still printed"),
        ("defect-tolerance-below-precision",
         "An algebraic identity was checked at 1e-6 against a JSON rounding to five decimals, so "
         "it could never pass regardless of the data -- the mirror of a check that cannot fail.",
         "the consistency run reporting a failure whose magnitude was 1e-5"),
        ("defect-nerve-orientation",
         "The nerve was computed over the transposed matrix, enumerating 2^39 subsets of "
         "annotators instead of 2^4 subsets of responses.",
         "the run failing to terminate"),
        ("defect-boundary-transposition",
         "The 2-face boundary matrix indexed (face, index) instead of (index, face). Three green "
         "controls never built a 2-face, so it surfaced only on real data.",
         "adding a filled-triangle control that exercises the path"),
        ("defect-single-schema-loader",
         "The release ships two message schemas. Reading only the nested one returned prompt text "
         "for zero of 1,095 prompts; every topic feature came out constant and seven features "
         "vanished from the table with no error.",
         "printing how many prompts matched text"),
    ]
    for name, stmt, caught in defects:
        did = node(name, "defect", stmt, d=8, status="settled",
                   props={"caught_by": caught})
        N[name] = did

    return N


def main() -> int:
    N = build()
    apply_adversary_verdicts()
    print(f"normative-chain phase written: {len(N)} nodes")
    for kind, cnt in q("SELECT kind, count(*) FROM node GROUP BY kind ORDER BY 2 DESC"):
        print(f"   {kind:20s} {cnt}")
    print("\nretracted claims and what killed each:")
    for name, killer, why in q(
            "SELECT n.name, s.name, e.note FROM node n JOIN edge e ON e.dst=n.id "
            "JOIN node s ON s.id=e.src WHERE n.status='refuted' AND e.kind='overturns' "
            "ORDER BY n.name"):
        print(f"   {name:38s} <- {killer}")
    # SCOPED TO CLAIMS. The unscoped version returned seven orphans, six of which are `defect`
    # nodes marked refuted -- a defect is a record that something was wrong, and nothing needs to
    # overturn it. Six false positives around one true one is a check that buries its own finding,
    # so the kind filter is the fix rather than a larger tolerance.
    orphan = q("SELECT name FROM node WHERE status='refuted' AND kind <> 'defect' AND id NOT IN "
               "(SELECT dst FROM edge WHERE kind='overturns')")
    print(f"\nretracted with NO incoming kill edge: {len(orphan)}"
          + ("".join(f"\n   {r[0]}" for r in orphan) if orphan else "  (none)"))
    print("\nmethod defects recorded, with what caught each:")
    for name, props in q("SELECT name, props::text FROM node WHERE kind='defect' ORDER BY name"):
        try:
            c = (json.loads(props) if isinstance(props, str) else (props or {})).get("caught_by")
        except (ValueError, AttributeError):
            c = None
        if c:
            print(f"   {name:34s} caught by {c}")
    return 0




def apply_adversary_verdicts() -> None:
    """Two independent clean-context adversaries, given the claims and the raw data and told to
    refute them. Applied idempotently here so re-running the builder reproduces the corrected state
    rather than the pre-adversary one -- a verdict that lives only in a psql session I once typed is
    a verdict the next rebuild silently discards.

    Adversary A, on the instrument-free set: three of four OVERTURNED.
    Adversary B, on the distributive set:    four of four CONFIRMED, three materially corrected.

    The asymmetry is itself the result. The claims that fell were the ones resting on a PARSER --
    on my reading of how the release encodes an unanswered question. The claims that held were the
    ones resting on human rankings, which are present for every assessment and need no
    interpretation to count.
    """
    d1 = node(
        "defect-not-asked-is-an-empty-list", "defect",
        "A guard written specifically to separate a missing answer from an empty one tested whether "
        "the block IS NONE. The key is always present and not-asked is encoded as an EMPTY LIST, so "
        "the guard never fired once and 13,672 of 18,678 assessments where the veto question was "
        "never posed were counted as asked-and-answered-zero. The same hole exists in any "
        ".get(key, []) default.",
        d=8, status="settled",
        props={"caught_by": "an independent adversary told to refute the claims",
               "affects": "r150 coverage, r150 veto distribution, r151 concentration ratio, "
                          "and r150's retraction of r149"})
    d2 = node(
        "defect-absence-of-proxy-certified-absence-of-property", "defect",
        "Force was declared never elicited because under 1% of criteria carry absolute-force "
        "wording. The release elicits force through the SIGNED WEIGHT, exactly as its own dataset "
        "card states: 28.32% of criteria reach |mean score| >= 8 and 98.68% of those carry no such "
        "wording. PROPERTY force-present vs PROXY force-wording: the implication runs one way and "
        "it was used backwards.",
        d=8, status="settled",
        props={"caught_by": "an independent adversary reading the object's own documentation"})
    d3 = node(
        "defect-split-half-floor-scaling", "defect",
        "The within-person split-half floor was scaled by 1/sqrt(2). For a statistic computed on "
        "FULL data the defensible scaling is 1/2, because a half-sample carries twice the variance "
        "of the full estimate. The lenient scaling inflates the floor and deflates the ratio: 1.06 "
        "becomes 1.44-1.53, moving an effect from comfortably inadmissible to sitting on the line.",
        d=8, status="settled",
        props={"caught_by": "an independent adversary re-deriving the floor instead of reusing it",
               "affects": "every effect-over-floor number in this phase"})

    for name, status, stmt in [
        ("force-never-elicited", "refuted",
         "WITHDRAWN. Force IS elicited, through the signed weight. The lexical measurement stands "
         "only as a measurement of WORDING -- absolute-force markers in 0.72% of criteria -- and "
         "licenses no claim about the construct."),
        ("content-preserved-force-lost", "partial",
         "RESTORED. Force was collected in the signed weight, and coval_core items carry exactly "
         "one key -- criterion -- in 3,899 of 3,899 cases. Compilation does delete force. The r143 "
         "withdrawal rested on the mistaken finding that force was never collected, and is itself "
         "withdrawn."),
        ("veto-is-distinct", "partial",
         "NARROWED. On the 5,006 assessments where the question was actually asked: 36.42% veto "
         "nothing, 3.90% veto all four, people veto their own top choice 9.25% of the time, and the "
         "rank-only pseudo-R2 is 0.128. Still not merely the bottom of the ranking, but far less "
         "distinct than the withdrawn 82.9% / 1.1% / 2.6% / 0.0559."),
        ("menu-can-fail", "partial",
         "Concentration is real and highly significant but the ratio is about 2.6x, not 5.01x: the "
         "permutation spread each person's flag across never-asked slots where the outcome was "
         "structurally forced to zero, shrinking the null."),
    ]:
        rows = q("SELECT id FROM node WHERE name=%s", (name,))
        if rows:
            q("UPDATE node SET status=%s, statement=%s WHERE id=%s", (status, stmt, rows[0][0]))

    for defect, target, note in [
        (d2, "force-never-elicited",
         "28.32% of criteria reach |mean|>=8 and 98.68% of those carry no wording"),
        (d1, "veto-is-distinct",
         "the withdrawn figures counted 13,672 never-asked assessments as answered-zero"),
        (d1, "menu-can-fail", "permutation exchangeability violated by never-asked slots"),
        (d3, "group-not-individual",
         "only the INDIVIDUAL half of this claim depends on the floor scaling; the group half does "
         "not depend on it at all"),
    ]:
        rows = q("SELECT id FROM node WHERE name=%s", (target,))
        if rows:
            edge(defect, rows[0][0],
                 "refines" if target == "group-not-individual" else "overturns", note=note)

    # the retraction that was itself issued by the broken instrument
    rows = q("SELECT id FROM node WHERE name='veto-block-partial-coverage'")
    if rows:
        q("UPDATE node SET status='settled', statement=%s WHERE id=%s",
          ("UN-RETRACTED. Coverage is 26.8%, not 100%. r150 overturned this figure using the "
           "broken parser, so the retraction is retracted and the original statement stands closer "
           "to the truth than its replacement did.", rows[0][0]))
        q("DELETE FROM edge WHERE dst=%s AND kind='overturns'", (rows[0][0],))

    node("price-of-inclusion-is-per-capita", "fact",
         "The 1.48 exchange rate is a RATE RATIO -- cost share over gain share -- not a headcount. "
         "Read literally as people the trade is 7.85 losing per 1 gaining for South Africa and 6.2 "
         "on average. The population-imbalance attack FAILS: pop ratio is 5.4 for SA and 7.4 on "
         "average, anti-correlated with the rate ratio at r=-0.86. And it is a central tendency, "
         "not a law: 8 to 10 of 34 groups come in under 1.0, a net win even after the externality.",
         d=7, status="settled")


if __name__ == "__main__":
    raise SystemExit(main())
