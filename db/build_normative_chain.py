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

R = "E04"


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

    # THE MEASUREMENT AND THE INFERENCE ARE SEPARATE NODES. They were one, and the conflation let
    # a false reading inherit a sound count's credibility -- caught only because a `fact` may not
    # carry status `refuted` and the domain check refused it.
    N["force-wording-is-rare"] = node(
        "force-wording-is-rare", "fact",
        "MEASUREMENT ONLY. Absolute-force wording appears in 0.72% of 15,248 criteria, scope "
        "qualifiers in 0.60%, exceptions in 0.72%, must in 0.71%, should in 13.06%. Measured on "
        "the full population. A fact about WORDING; it licenses nothing about whether force was "
        "elicited.", d=8, status="settled")
    evid(N["force-wording-is-rare"], "r143-markers",
         "full population, not the study corpus, because selecting on extreme weight could select "
         "terse criteria and manufacture the result", 8)

    N["force-was-never-elicited"] = node(
        "force-was-never-elicited", "my_claim",
        "WITHDRAWN. Read off the wording count: that the release never collected normative force. "
        "False. Force is carried by the SIGNED WEIGHT exactly as the dataset card states -- 28.32% "
        "of criteria reach |mean score| >= 8 and 98.68% of those carry no force wording at all.",
        d=4, status="refuted")
    evid(N["force-was-never-elicited"], "r154-the-empty-list",
         "PROPERTY force-present vs PROXY force-wording: a one-way implication used backwards", 8)

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
         "force-wording-is-rare",
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
         "force-was-never-elicited",
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
        # LOUD, NOT SILENT. The first version indexed N[target] directly and threw a KeyError the
        # moment a node was renamed -- which is correct behaviour. What was not correct was that I
        # ran the builder with output redirected to /dev/null twice afterwards and then read the
        # STALE graph as though it were the rebuild's result. A build step whose output you discard
        # is a build step you have stopped checking.
        if target not in N:
            raise KeyError(f"control {name!r} points at unknown node {target!r}; rename it or fix "
                           f"the control, but do not let the graph keep an edge to nothing")
        edge(cid, N[target], "acquits", note=why)
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
    build_compilation_thread()
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
        ("subjectivity-inversion-prompt-level", "partial",
         "RESTORED AND STRONGER. On the corrected 326-prompt population the prompt-level inversion "
         "is r=-0.153, p=0.0056, and it SURVIVES BH over the full 14-feature family, agreeing on "
         "sign in four of five held-out splits. It was withdrawn on the phantom population where it "
         "read -0.066 -- withdrawn for the right reason on the wrong data."),
        ("group-not-individual", "partial",
         "GROUP level CONFIRMED and hardened by an adversary: 136 South African annotators across "
         "953 of 1,078 prompts, 16.3pp on the world block and 15.6pp on personal, surviving "
         "stratification inside every level of five demographic axes at 11-27pp, cluster-bootstrap "
         "CI [13.5, 19.3], still 10.4pp after dropping the 30 largest contributors of 136. "
         "INDIVIDUAL level UNDECIDED: under the corrected 1/2 floor scaling the ratio is 1.49 "
         "against a 1.50 threshold, not the 1.06 first reported, so the design cannot decide rather "
         "than having decided. Blind spot: the release carries no batch or timestamp field, so a "
         "recruitment-batch confound can be neither ruled out nor confirmed."),
        ("menu-is-binding", "settled",
         "No aggregation rule could have served them, and the control is now multi-seed. A chooser "
         "optimising specifically for the group reaches 0.669; a size-matched random subgroup "
         "reaches 0.740 over 25 draws per prompt across 722 prompts, excess -0.071 [-0.089, "
         "-0.053]. An independent adversary reproduced it with a stronger control -- relabelling "
         "136 fake-SA annotators onto their REAL assessments, preserving co-occurrence, 300 "
         "permutations: real 0.668 against null 0.751 +- 0.011, z = -7.57, below 100% of "
         "permutations."),
        ("menu-can-fail", "settled",
         "Concentration of full rejection on particular prompts is real and highly significant, but "
         "the ratio is 2.56x rather than 5.01x, and on the corrected 326-prompt population the "
         "MECHANISM reverses: disagreement between raters is the strongest predictor at +0.188, "
         "above the non-rejectors' veto mean at +0.172, while the veto SHARE falls to +0.118 and no "
         "longer clears BH. The SHARED INADEQUACY verdict is withdrawn in favour of DISPERSED "
         "DEMAND. Superseded text follows: the ratio is about 2.6x, not 5.01x, because the "
         "permutation spread each person's flag across never-asked slots where the outcome was "
         "structurally forced to zero, shrinking the null."),
    ]:
        rows = q("SELECT id FROM node WHERE name=%s", (name,))
        if rows:
            q("UPDATE node SET status=%s, statement=%s WHERE id=%s", (status, stmt, rows[0][0]))

    for defect, target, note in [
        (d2, "force-was-never-elicited",
         "28.32% of criteria reach |mean|>=8 and 98.68% of those carry no wording; a lexical scan "
         "cannot see a numeric channel"),
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

    # RESTORATIONS MUST LIVE HERE, NOT IN A PSQL SESSION. I wrote exactly that warning into this
    # file and then two rounds later restored the subjectivity claim by hand anyway; the next
    # rebuild silently reset it to refuted and the ledger's withdrawn count jumped from 3 to 5. A
    # rule you state and then do not encode is a rule you will break while quoting it.
    # UNCONDITIONAL. The first version only acted when the node was still `refuted`, so once the
    # status loop above had already set it to `partial` the edge deletion never ran and the node sat
    # in the ledger as WITHDRAWN with a live kill edge from a killer that had itself been withdrawn.
    # A restoration has to remove the edge whether or not it also has to change the status.
    for name in ("subjectivity-inversion-prompt-level", "content-preserved-force-lost",
                 "veto-block-partial-coverage"):
        rows = q("SELECT id FROM node WHERE name=%s", (name,))
        if rows:
            q("DELETE FROM edge WHERE dst=%s AND kind='overturns'", (rows[0][0],))

    # the retraction that was itself issued by the broken instrument
    rows = q("SELECT id FROM node WHERE name='veto-block-partial-coverage'")
    if rows:
        q("UPDATE node SET kind='fact', status='settled', statement=%s WHERE id=%s",
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

def build_compilation_thread() -> None:
    """r155-r160: what compilation does, once the audit stopped asking only what it destroys.

    This thread reverses the phase's own direction. It began as an attempt to price the deletion of
    force and ended by measuring two things the compiler does WELL and one it does not pay for.
    """
    n1 = node("weight-deletion-is-free", "fact",
              "Deleting the weight from the compiled rubric costs nothing measurable: core_keep "
              "minus core_drop is +0.0015 [-0.0021, +0.0051], z=0.83. Not because the weights are "
              "uninformative -- randomising their signs collapses concordance to the shuffled "
              "floor, 0.5003 against 0.5021, and real-versus-random is +0.1393 at z=50.5.",
              d=7, status="settled")
    evid(n1, "r155-does-the-weight-matter", "one judge shared by every arm, so it cannot produce a "
         "between-arm difference", 7)

    n2 = node("the-compiler-does-not-select-by-weight", "fact",
              "Of core items matching a source at 0.80, only 27.9% came from the top magnitude "
              "slots and the mean normalised magnitude rank is 0.471 where 0.5 is chance. The "
              "documented selection rule is not visible in the artefact.",
              d=6, status="partial",
              props={"limitation": "only 30.9% of core items match anything, because the compiler "
                                   "rewrites; if the unmatched 69% are disproportionately "
                                   "high-magnitude the rule could hold on the part not visible"})
    evid(n2, "r156-the-compression-curve", "and top-k beats random-k by at most 0.021 anywhere on "
         "the sweep, so selecting by magnitude would not buy much even if it were done", 6)

    n3 = node("compilation-does-two-things-well", "my_claim",
              "Selection and rewriting are separable and both positive. On criteria matched to "
              "their own source: random criteria 0.5502, surviving criteria in original wording "
              "0.5941, the same criteria as rewritten 0.6116. Selection +0.0439, rewriting +0.0175 "
              "[+0.0148, +0.0202] at z=12.75. The rewriting effect is dose-responsive -- +0.0121 "
              "near-identical, +0.0169 moderate, +0.0269 heavier, outer intervals disjoint.",
              d=7, status="settled")
    evid(n3, "r158-the-rewriting-itself", "selection held fixed by construction: it is literally "
         "the same criterion in two wordings", 7)
    evid(n3, "r157-is-it-a-quality-detector", "the deflationary rival is refuted -- core beats a "
         "generic goodness index by +0.057, response length by +0.109, and its criteria are no more "
         "inter-correlated than raw ones", 7)

    n4 = node("compilation-is-a-net-loss-on-accuracy", "my_claim",
              "Against the only alternative that matters -- not compiling -- compilation loses "
              "0.0229 on the mean rater, 0.0078 on the worst-served, 0.0197 at the tenth "
              "percentile, and buys 0.0011 in equality. The ordering of arms is identical under "
              "utilitarian, maximin and p10 outcomes, so compression is not distributively "
              "selective here. Held out on raters who contributed nothing to the weights the gap "
              "narrows to +0.0095 but does not close.",
              d=7, status="settled")
    evid(n4, "r159-which-outcome", "four outcomes, same arms, same prompts, same judge", 7)
    evid(n4, "r160-out-of-sample", "57% of the in-sample advantage was fitting the panel; the "
         "four-weight arm shrinks by 0.0001 against fifteen weights' 0.0125, so what overfits is "
         "the weighting and not the selection", 7)
    edge(n1, n4, "supports", note="the weight is not where the loss is")
    edge(n3, n4, "confounds", note="two real gains that are still not enough to pay for the "
         "discarding")

    node("legibility-is-unpriced", "fact",
         "Compilation's only remaining justification is one this release cannot price: whether a "
         "human can hold four criteria in mind and not fifteen. It is a real cost and it may well "
         "dominate the 0.01-0.02 concordance loss. It is simply not in the data.",
         d=8, status="settled")

    d = node("defect-two-baselines-summed", "defect",
             "I reported compilation as 'nearly balancing' by adding -0.027 for discarding criteria "
             "to +0.061 for selection and rewriting. The first is measured against keeping "
             "everything and the second against random criteria. Summing them compares one object "
             "to two different alternatives and reports the total as a single quantity.",
             d=8, status="settled",
             props={"caught_by": "scoring the arms directly against each other in the next round"})
    edge(d, n4, "refines", note="the direct comparison replaces the summed one")


if __name__ == "__main__":
    raise SystemExit(main())
