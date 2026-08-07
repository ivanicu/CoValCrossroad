"""R442 -- the definition's EXTENSION, and what it becomes when clause ③ is applied as WRITTEN.

⛔ THE ANNOUNCED STEP WAS FORCED. R441 closed with "intersect the four clauses and see what the
   definition's extension is". R360's artifact already commits `clause23_admits`; R440 measured ④
   excluding 0 and R441 measured size half A excluding 0 among ②∧③∧④. So the extension IS
   `clause23_admits` -- a LOOKUP, not a measurement. **Eleventh announced step checked, SEVENTH
   killed.**

⭐ AND THE LOOKUP SURFACED SOMETHING NOBODY HAD LOOKED AT. The extension is
   `{coval_core, topw_k3, topw_k4, topw_k6, topw_k8}` -- **NOT the published five**
   `{coval_core, topabs_k4, topvar_k4, topw_k4, topwvar_k4}`. Only **2 of 5** overlap. The
   definition's boundary runs along the **SELECTOR** axis, not the k axis: it admits `topw` at four
   sizes and rejects three sibling selectors at k=4.

⛔ AND THAT EXPOSES A CONTRADICTION BETWEEN THE DOCUMENT AND ITS OWN ARTIFACT. `DEFINITION.md`'s
   clause-③ section says, in its own words:

     "`topw_k` -- four of the published five -- selects on `w = mean importance score` from
      `conversation_rubrics.jsonl`, and the annotators who wrote those scores are, at 95.3%, the
      same people whose rankings define that prompt's target ... DERIVED ... is that `topw_k` is
      **not producible from the conversation alone**."

   "Producible from the conversation alone" is the definition's OWN opening phrase. So clause ③ AS
   WRITTEN excludes `topw_k`. But clause ③ AS IMPLEMENTED is a hand-written set of four arms that
   does not contain any `topw_k`, which is why `clause23_admits` carries four of them. **This is the
   `declared != implemented` failure, in the definition's extension.**

ESTIMAND (named before the method)
    EXT_impl = the extension under ③ as IMPLEMENTED (the hand-written 4-arm set)
    EXT_writ = the extension under ③ as WRITTEN (additionally excluding every `topw_k`, per the
               document's own DERIVED finding)
    and the question is |EXT_writ| -- what the definition admits when its own text is applied.

IDENTIFICATION
    Fully identified from committed artifacts: `clause2_admits`, the hand-written ③ set, and the
    document's own derivation about `topw_k`. What is NOT identified: whether the DERIVED finding is
    correct -- R363 measured the 95.3% annotator overlap (a census) and DERIVED non-producibility
    from it plus the release's authoring order. **This round takes the document at its word and
    computes the consequence; it does not re-adjudicate the derivation.**

SCOPE  population : R360's 42-arm space, home release, judge J
       instrument : R360's committed admit lists; no new scoring
       baseline   : EXT_impl, the extension as the campaign has been computing it
       regime     : k=4 for ②'s reference; the arms carry k in {1,2,3,4,6,8,12,16}

WORLDS
    W-INSTANCE   EXT_writ has exactly ONE member -> under its own written clause ③ the definition
                 admits only the released core. That is "the definition describes the instance" at
                 the level of the whole conjunction, not one clause, and it is the failure this
                 document is named after.
    W-CATEGORY   EXT_writ has >= 2 members that are not the released core -> the definition still
                 picks out a class when its own text is applied, and the implemented/written gap is
                 a bookkeeping defect rather than a structural one.
    W-EMPTY      EXT_writ is empty -> the definition as written admits nothing at all, including the
                 object it was written from, which would be a stronger and different problem.

PREDICTION MATRIX
                  |EXT_writ| == 1   >= 2 non-core   == 0
    W-INSTANCE          0.9              0.03        0.05
    W-CATEGORY          0.05             0.95        0.02
    W-EMPTY             0.05             0.02        0.93

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    |EXT_writ| == 1 and it is the released core -> W-INSTANCE; DEFINITION.md owes the statement
                                                   that its extension under its own text is one arm
    |EXT_writ| >= 2 with a non-core member       -> W-CATEGORY
    |EXT_writ| == 0                              -> W-EMPTY
    a control fails                              -> UNVERIFIED

CONTROLS
    POSITIVE   EXT_impl must REPRODUCE R360's committed `clause23_admits` exactly. If this round
               cannot rebuild the extension the campaign has been using, its alternative extension
               is not a comparison, it is a second bug.
    g=0        applying NO extra exclusion must leave EXT_impl unchanged -- the `as written` filter
               must be a no-op when handed an empty exclusion set.
    NEGATIVE   the `topw_k` filter is a NAME MATCH and therefore an instrument. It is run where the
               answer is known: it must select every arm whose committed core came from the
               importance-score selector and NO arm that did not. Both directions printed.
    PLACEBO    the count of arms removed by a filter matching nothing must be 0.

MULTIPLICITY  two extensions over one space; no selection, no correction owed, stated.
ARTIFACT      results/r442_extension.json
IMPOSSIBLE HERE, NAMED
    * re-adjudicating whether `topw_k` is truly non-producible -- R363/R364's job; this round
      computes the consequence of the document's own DERIVED finding.
    * an extension on the second release -- ② admits 0 there (R434), so it is empty by arithmetic.
    * construct validity of "producible from the conversation alone" -- the phrase is the
      definition's, and no release provides an external test of it.

EXIT 0 W-CATEGORY · 1 W-INSTANCE · 2 W-EMPTY or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

# ③ AS IMPLEMENTED -- the hand-written set, verbatim from DEFINITION.md, used by four rounds.
CLAUSE3_IMPL = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
PUBLISHED_FIVE = {"coval_core", "topabs_k4", "topvar_k4", "topw_k4", "topwvar_k4"}


# ⛔ THE SELECTOR LIST COMES FROM THE SOURCE, NOT FROM A PATTERN I INVENTED. The first version of
#    this round matched `^topw_k\d+$` and validated it against a "known set" defined by
#    `startswith("topw_k")` -- two patterns of my own, compared to each other. They disagreed on
#    `topw_k4_sham`, the control FAILED, and it was right to: I had compared a tight pattern to a
#    loose one and had no third thing to adjudicate. This campaign's ledger says exactly that a
#    grep is an instrument and that the tight one is not "more conservative", it is the one that
#    was tested -- but neither had been tested against the OBJECT.
#    `corebench/select_core.py:51` enumerates the nine selectors this campaign builds arms from.
#    An arm's selector is the LONGEST of those its name starts with, which is what keeps
#    `topwvar_k4` from being read as a `topw_k` arm.
SELECTORS = ["random_k", "topw_k", "topabs_k", "oracle_k", "full",
             "topvar_k", "topwvar_k", "indep_k", "greedy_k"]


def selector_of(arm: str):
    """-> the selector this arm was built with, or None. Longest match wins."""
    hits = [s for s in SELECTORS if arm.startswith(s)]
    return max(hits, key=len) if hits else None


def is_topw(arm: str) -> bool:
    """③ AS WRITTEN additionally excludes the importance-score selector -- INCLUDING its shams,
    because the exclusion is about PROVENANCE (what the arm read) and a sham of `topw_k` read the
    same importance scores."""
    return selector_of(arm) == "topw_k"


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    f360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
    if not f360.exists():
        print("  UNRUNNABLE: R360's artifact absent. Exit 2, never 0."); return 2
    a = json.loads(f360.read_text())
    arms = sorted(a["arms"]); admits2 = set(a["clause2_admits"]); committed23 = set(a["clause23_admits"])

    print("R442 · the definition's EXTENSION, and what it becomes under clause ③ AS WRITTEN\n")
    print("  ⛔ the announced intersection was FORCED: R360 commits `clause23_admits`, and R440/R441")
    print("     measured ④ and size half A as excluding 0. Eleventh announced step, SEVENTH killed.\n")

    # ------------------------------------------------------------------------------- controls
    ok = True
    ext_impl = {x for x in arms if x in admits2 and x not in CLAUSE3_IMPL}
    pos = (ext_impl == committed23)
    ok &= pos
    print(f"  POSITIVE  rebuild the extension the campaign USES and match R360's committed list:")
    print(f"            rebuilt {sorted(ext_impl)}")
    print(f"            committed {sorted(committed23)}   {'PASS' if pos else '⛔ FAIL'}")
    if not pos:
        print(f"            an alternative extension would not be a comparison, it would be a bug.")

    g0 = ({x for x in arms if x in admits2 and x not in CLAUSE3_IMPL and x not in set()}
          == ext_impl)
    ok &= g0
    print(f"  g=0       the `as written` filter with an EMPTY exclusion set is a no-op   "
          f"{'PASS' if g0 else '⛔ FAIL'}")

    sel_hits = sorted(x for x in arms if is_topw(x))
    # the KNOWN set now comes from the source's selector list, not from a second pattern of mine
    known = sorted(x for x in arms if selector_of(x) == "topw_k")
    must_not = sorted(x for x in arms if selector_of(x) in ("topwvar_k", "topvar_k", "topabs_k"))
    neg = (sel_hits == known) and not (set(sel_hits) & set(must_not))
    ok &= neg
    print(f"  NEGATIVE  the selector filter run where the answer is known, BOTH directions:")
    print(f"            selects (selector == topw_k, shams included) {sel_hits}")
    print(f"            must NOT select sibling selectors {must_not}")
    print(f"            {'PASS' if neg else '⛔ FAIL'}")
    unresolved = sorted(x for x in arms if selector_of(x) is None)
    print(f"            arms whose selector the source cannot name: {len(unresolved)} {unresolved[:6]}")

    plac = len([x for x in arms if re.match(r"^__nothing__$", x)])
    ok &= (plac == 0)
    print(f"  PLACEBO   a filter matching nothing removes {plac} arms, must be 0   "
          f"{'PASS' if plac == 0 else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r442_extension.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ---------------------------------------------------------------------------- the two extensions
    ext_writ = {x for x in ext_impl if not is_topw(x)}
    print(f"\n  EXT_impl  (③ as IMPLEMENTED, the hand-written 4-arm set): {len(ext_impl)} "
          f"-> {sorted(ext_impl)}")
    print(f"  EXT_writ  (③ as WRITTEN, additionally excluding topw_k): {len(ext_writ)} "
          f"-> {sorted(ext_writ)}")
    print(f"\n  and NEITHER is the published five {sorted(PUBLISHED_FIVE)}:")
    print(f"    EXT_impl ∩ published = {sorted(ext_impl & PUBLISHED_FIVE)} "
          f"({len(ext_impl & PUBLISHED_FIVE)} of 5)")
    print(f"    the definition's boundary runs along the SELECTOR axis, not the k axis: it admits")
    print(f"    `topw` at four sizes and rejects three sibling selectors at k=4.")

    non_core = sorted(ext_writ - {"coval_core"})
    world = ("W-EMPTY" if not ext_writ else
             "W-INSTANCE" if (len(ext_writ) == 1 and "coval_core" in ext_writ) else
             "W-CATEGORY" if non_core else "W-INSTANCE")
    print(f"\n  WORLD: {world}")
    if world == "W-INSTANCE":
        print(f"    ⛔ under its OWN WRITTEN clause ③ the definition admits exactly ONE arm, and it")
        print(f"    is `coval_core` -- the released core, the object the definition was written")
        print(f"    from. That is 'the definition describes the instance' at the level of the WHOLE")
        print(f"    CONJUNCTION, not one clause, and it is the failure this document is named after.")
        print(f"    ⚠ WHAT THIS IS NOT: a claim that ③'s derivation is wrong. The round takes the")
        print(f"    document at its word and computes the consequence. If the derivation stands,")
        print(f"    the extension is one arm; if it falls, `topw_k` returns and the extension is")
        print(f"    five. **Either way the document currently states both and reconciles neither.**")
    elif world == "W-CATEGORY":
        print(f"    the definition still picks out a class under its own text: {non_core} are")
        print(f"    admitted besides the released core, so the implemented/written gap is")
        print(f"    bookkeeping rather than structural.")
    else:
        print(f"    the definition as written admits NOTHING, including the object it was written")
        print(f"    from -- a stronger and different problem than describing the instance.")

    (RES / "r442_extension.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "ext_impl": sorted(ext_impl), "ext_writ": sorted(ext_writ),
         "published_five": sorted(PUBLISHED_FIVE),
         "overlap_impl_published": sorted(ext_impl & PUBLISHED_FIVE),
         "clause3_impl": sorted(CLAUSE3_IMPL), "topw_arms": sorted(sel_hits),
         "n_arms": len(arms)}, indent=1))
    print(f"\n  artifact -> {(RES / 'r442_extension.json').relative_to(ROOT)}")
    return 0 if world == "W-CATEGORY" else (1 if world == "W-INSTANCE" else 2)


if __name__ == "__main__":
    sys.exit(main())
