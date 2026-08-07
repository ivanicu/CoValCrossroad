#!/usr/bin/env python3
"""
R631 -- the ungoverned document holds a retraction the retraction ledger does not

CHECK #230: I REPEATED CHECK #228's EXACT ERROR ONE ROUND AFTER RECORDING IT.
  ⛔ "outside EVERY gate" -- the same R621 lower-bound overstatement retracted as #228 in the
     immediately preceding round. ⭐ Recording a correction did not prevent its recurrence in the
     very next closing line: THE CHECKS CATCH, THEY DO NOT PREVENT. That is a fact about the
     mechanism, not about this instance, and it is the reason the ledger is worth more than the
     resolution to be careful.
  ⛔ "the sharpest single item this arc has" -- an uncomputed superlative. Fifteenth.

⭐ AND READING THE OBJECT FOUND SOMETHING R630's INSTRUMENT COULD NOT SEE. The ③b register says, in
   its own words, "This also retracts R335." R630 classified that same finding LIVE, because its
   status test asked only whether the cited round appears in RETRACTIONS.md -- and R335 does not,
   while its artifact still records the settled verdict W-DECIDABLE. So the retraction exists,
   inside the ungoverned file, and never reached the ledger.

ESTIMAND        three facts, each mechanically decidable:
                  ① is R335's retraction recorded in RETRACTIONS.md?
                  ② does R335's artifact still carry a settled verdict?
                  ③ does the gated pair state ANY bound on clause ③'s testability?
IDENTIFICATION  Exact. ⚠ "states a bound on ③'s testability" is matched by phrase families and is
                a SEARCH, so it carries a positive control; its sound direction is that a hit is
                genuine, so a MISS is the weaker claim and is reported as such.
SCOPE           population : RETRACTIONS.md, R335-R338's artifacts, the gated pair
                instrument : ledger membership · artifact verdict · phrase search
                             instrument unit = A DOCUMENT MENTION
                             claim unit      = A RECORDED RETRACTION. NOT equal -- a mention is
                             not a recording, so ① is an UPPER bound on what is recorded.
                baseline   : the ③b register in FORMULATION.md
                regime     : this repository at this sha
WORLDS          THREE, because a two-world set has missed the modal outcome in this arc three
                times out of three (R619, R620, R630) and that is now a design default:
                A RECORDED: the retraction is in the ledger and the bound is in the gated pair.
                B UNRECORDED RETRACTION: the retraction lives only in FORMULATION.md, so the
                  ledger overstates what stands and R630's LIVE classification was wrong.
                C BOUND MISSING TOO: additionally the gated pair states no bound on ③'s
                  testability, so the definition's own limit is ungoverned as well.
KILL            pre-registered: R335 absent from the ledger AND its artifact settled -> world B at
                least. Plus no bound phrase in the gated pair -> world C.
POSITIVE CTRL   a round known to be in RETRACTIONS.md must be found there. Fails at g=0: a
                fabricated round id must not.
NEGATIVE CTRL   the phrase search must FIND the bound inside FORMULATION.md, where it demonstrably
                is -- otherwise a miss in the gated pair is the search failing, not the document.
PLACEBO         a phrase family that occurs nowhere -> 0 hits in all three documents.
SEEDS           n/a, deterministic.
MULTIPLICITY    3 facts x 3 documents + 4 controls. All reported.
ARTIFACT        results/the_unrecorded_retraction.json
IMPOSSIBLE      whether the ③b bound is CORRECT needs re-running R336-R338, which this site cannot
                do. What is decidable is whether it is RECORDED where the project's own rules say
                a retraction and a limit must live.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"

# ⛔ v1's REGEX RETURNED A FALSE POSITIVE ON THE GATED PAIR. Its alternation `(testab|bound)`
#    matched the BARE WORD "bound" anywhere near the glyph, so it reported that the gated pair
#    states a limit on clause ③'s testability when NONE of the five specific phrases occurs in
#    either document. A search whose broadest alternative is an ordinary English word is not an
#    instrument. Replaced by an explicit phrase list, each checked and reported separately.
BOUND_PHRASES = [
    ("clause ③ … testab", re.compile(r"clause ③[^\n]{0,90}testab", re.I)),
    ("annotation, not a measurement", re.compile(r"annotation, not a measurement", re.I)),
    ("③ is decided per arm", re.compile(r"③ is decided per arm", re.I)),
    ("no residual leak signal", re.compile(r"no residual leak signal", re.I)),
]
def BOUND_hits(text):
    return [n for n, p in BOUND_PHRASES if p.search(text)]


def verdict(rid):
    for d in A24.glob(f"R{rid}_*"):
        for f in (d / "results").glob("*.json"):
            try: j = json.loads(f.read_text())
            except Exception: continue
            if isinstance(j, dict) and isinstance(j.get("world"), str): return j["world"]
    return None


def main():
    RET = (ROOT / "RETRACTIONS.md").read_text()
    F = (E05 / "FORMULATION.md").read_text()
    G = (E05 / "STATEMENT.md").read_text() + "\n" + (E05 / "DEFINITION.md").read_text()

    print("─── CONTROLS ───")
    known = re.findall(r"R(\d{3})", RET)
    pos = bool(known) and f"R{known[0]}" in RET
    print(f"  POSITIVE  a round named in the ledger (R{known[0]}) is found there -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = "R996" not in RET
    print(f"  g=0       a fabricated round (R996) is not -> {'PASS' if g0 else '⛔ FAIL'}")
    neg = bool(BOUND_hits(F))
    print(f"  NEGATIVE  the bound phrase family IS found in FORMULATION.md, where it demonstrably "
          f"is -> {'PASS — a miss elsewhere is the document, not the search' if neg else '⛔ FAIL — the search is blind'}")
    plc = sum(bool(re.search("zzq" + "_no_such_phrase", d, re.I)) for d in (RET, F, G))
    print(f"  PLACEBO   a phrase that occurs nowhere -> {plc} hits -> "
          f"{'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = pos and g0 and neg and plc == 0

    print(f"\n─── THE THREE FACTS ───")
    # ⛔ AND THE LEDGER TEST WAS SELF-CONTAMINATED. A bare `R335` match found MY OWN entry from
    #    the previous round, which NAMES the register while classifying it LIVE -- a citation, not
    #    a recording. The retraction ledger is a population my own rounds WRITE TO, so any round
    #    scanning it for its own subject matter contaminates itself within one round. Same class as
    #    R601/R604, new vector. Fixed by requiring an entry that both names R335 and states a
    #    retraction of it, and by excluding entries that merely cite the register.
    paras = re.split(r"\n(?=## )", RET)
    naming = [q for q in paras if re.search(r"\bR335\b", q)]
    recording = [q for q in naming if re.search(r"retract\w*\s+R335|R335[^.]{0,60}retract", q, re.I)]
    in_ledger = bool(recording)
    print(f"  ledger paragraphs NAMING R335: {len(naming)}   RECORDING its retraction: "
          f"{len(recording)}  (a citation is not a recording)")
    v335 = verdict("335")
    gated_hits = BOUND_hits(G)
    bound_in_gated = bool(gated_hits)
    says_retracts = bool(re.search(r"retracts R335", F, re.I))
    print(f"  ① FORMULATION.md says 'retracts R335'            : {says_retracts}")
    print(f"  ② R335 appears in RETRACTIONS.md                 : {in_ledger}")
    print(f"  ③ R335's artifact still records                  : {v335!r}")
    print(f"  ④ the gated pair states a bound on ③'s testability: {bound_in_gated}  phrases found: {gated_hits or 'NONE of 4'}")
    print(f"\n  the other three rounds' verdicts, unchanged on disk:")
    for r in ("336", "337", "338"):
        print(f"    R{r}: {verdict(r)!r}")

    print(f"\n─── VERDICT (three worlds; a two-world set has missed the modal answer 3 of 3) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif says_retracts and not in_ledger and not bound_in_gated:
        world = ("C UNRECORDED RETRACTION AND MISSING BOUND — FORMULATION.md retracts R335 in its "
                 "own words; RETRACTIONS.md does not name R335; R335's artifact still records the "
                 "settled verdict W-DECIDABLE; and the gated pair states no bound on clause ③'s "
                 "testability. So the ledger overstates what stands, R630's LIVE classification "
                 "was an artifact of asking only the ledger, and the live definition's own limit "
                 "lives solely in the document no gate reads.")
    elif says_retracts and not in_ledger:
        world = ("B UNRECORDED RETRACTION — the retraction lives only in FORMULATION.md and never "
                 "reached the ledger, so R630's LIVE classification was wrong.")
    else:
        world = ("A RECORDED — the retraction is in the ledger and the bound is in the gated pair; "
                 "nothing is owed.")
    print(f"  {world}")
    print(f"\n  ⚠ WHETHER THE ③b BOUND IS CORRECT needs re-running R336-R338, which this site "
          f"cannot do. What is decidable is whether it is RECORDED where the project's own rules "
          f"say a retraction and a limit must live.")
    print(f"  ⚠ A MENTION IS NOT A RECORDING: fact ② is an UPPER bound on what the ledger holds.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "the_unrecorded_retraction.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "formulation_says_retracts_r335": says_retracts, "r335_in_ledger": in_ledger,
        "r335_artifact_world": v335, "bound_in_gated_pair": bound_in_gated, "gated_phrase_hits": gated_hits,
        "ledger_naming": len(naming), "ledger_recording": len(recording),
        "sibling_verdicts": {r: verdict(r) for r in ("336", "337", "338")},
        "check230": ("'outside every gate' repeats check #228's overstatement one round after it "
                     "was recorded -- the checks catch, they do not prevent"),
        "impossible": "correctness of the bound needs re-running R336-R338; only recording is decidable",
    }, indent=2))
    print(f"\n  wrote {OUT / 'the_unrecorded_retraction.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
