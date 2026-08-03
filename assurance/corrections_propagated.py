"""A claim corrected in one document must not survive uncorrected in another.

Why this exists (entry 83)
--------------------------
Two corrections made in this session landed in README.md and RETRACTIONS.md and
did NOT reach the other documents making the same claim:

  entry 66  "97.4% survives faithful paraphrase (r14/r20)" -- only r20 measures
            retention; r14 measures the fidelity filter and a 15.4% flip rate.
            Still uncorrected in PREREGISTRATION.md AND FROZEN.md.
  entry 79  "+0.0733 to the polarity rewrite with a further +0.0149 to which
            items survive" -- omits that the selection stage COSTS -0.0181.
            Still uncorrected in PREREGISTRATION.md.

PREREGISTRATION.md opens by saying it is written so its conclusions "cannot be
softened later". It was carrying two superseded claims.

`retired_framing_in_assertion_positions.py` watches the same three documents but
only for RETIRED FRAMINGS, and only in assertion positions. These were number and
attribution corrections in body prose, which nothing scanned.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   no document states a form of a claim that was corrected elsewhere
  PROXY      the superseded form's pattern does not appear in any watched file
  IMPLICATION  present => the stale form is there, definitely.
               absent  => that PATTERN is gone, and NOTHING about whether other
               paraphrases of the same stale claim survive.
  SAFE SIDE  flags a known stale form. It cannot discover corrections that were
             never registered here, so the registry is the check's real limit and
             adding to it is part of making a correction.

Each entry names the superseded form, the entry that corrected it, and what the
correct statement is -- so a hit tells a reader what to write, not just that
something is wrong.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
# ASSURANCE.md is GENERATED into assurance/, not the repo root. The first
# version of this list said "ASSURANCE.md", which resolves to a file that does
# not exist -- so the check would have reported 3 of 4 watched and silently
# skipped the generated claim ledger, which is exactly the kind of quiet
# under-coverage this whole session has been about.
WATCHED = ("README.md", "FROZEN.md", "PREREGISTRATION.md", "assurance/ASSURANCE.md",
           "ADVERSARY_FORECAST.md")

# (pattern, correcting entry, what the correct statement is)
CORRECTED = [
    # r68's 0.9132 and r40's 0.188 depend on encoder features that cannot be
    # regenerated (entries 134-135). Any document stating either number without
    # the not-regenerable caveat is stating it as if it were repeatable.
    # `[\s\S]` not `.`: the caveat sits on the FOLLOWING line, and `.` does not
    # cross a newline, so the lookahead never saw it. The first version of this
    # pattern fired identically with and without the caveat present -- a check
    # with no discriminating power, caught by attacking it rather than by
    # reading it (P7).
    (r"Spearman-Brown \*\*0\.9132\*\*(?![\s\S]{0,600}?[Nn]ot regenerable)", 135,
     "0.9132 rests on r39's cached encoder features; internlm returns 100% NaN under "
     "transformers 5.14.1, so the three-lineage agreement is NOT regenerable on this machine"),

    (r"r14\s*/\s*r20|r14 and r20|\(r14, r20\)", 66,
     "97.4% retention is r20 ALONE; r14 supplies the fidelity filter and measures "
     "a 15.4% model-paraphrase flip rate against 2.5% mechanical"),
    (r"further \+?0\.0149 to (?:\*\*)?which items survive", 79,
     "compatibility selection COSTS -0.0181 and beats size-matched random by +0.0149 -- "
     "membership is mitigation, not gain"),
    (r"\+0\.102\s*(?:→|->)\s*(?:\*\*)?[-−]0\.042", 81,
     "r12's fresh arm is -0.064 [-0.092, -0.037]; 0.042 appears nowhere in r12's results"),
    (r"replicates at (?:\*\*)?[-−]0\.058", 81,
     "the held-out replication is +0.0847 -> -0.0716 (r46 controls)"),
    (r"filtered at 99\.2%", 76,
     "r14's fidelity_kept.model is 0.9911616 -- 99.1%"),
    # Entry 84: not a wrong FORM but a stale PREMISE -- a document may state a
    # superseded state of knowledge without any individual sentence being false.
    # The pattern targets the specific unqualified framing, and its absence is
    # weaker evidence than for the others, which is why it says so here.
    (r"polarity carries roughly half the above-chance", 104,
     "+0.0876 (47%) is sign added LAST to text alone (r32); the Shapley value over all 16 "
     "coalitions is +0.0214 (12%) (r36), whose verdict says r32 over-attributed to polarity"),
    (r"r56'?s? (?:held-out )?(?:value|interval|result) (?:is|was|of) \+?0\.0198(?!.{0,200}UNVERIFIED)", 101,
     "r56's numbers have no artifact and no committed code; r66 could not recompute them. Its "
     "CONCLUSION survives an independent method, its INTERVAL does not"),
    (r"attributes\s*\n?\s*\+0\.0733 of it to the polarity rewrite \(r44\)\. Compatibility", 98,
     "the +0.0733 stage applies the crowd's RATING SIGN numerically (r44 run.py:112); it bounds "
     "from above what a text rewrite could achieve and does not measure one"),
    (r"personal ranking (?:is present|exists) for \*\*76\.9%\*\*", 89,
     "26.7% -- 4,901 of 18,384. The 76.9% came from sampling the head of "
     "comparisons.jsonl instead of reading all of it"),
    (r"It does \*\*not\*\* touch shared-menu\s+endogeneity: every participant saw the same four "
     r"responses, so `menu → shared salience → S\u1d62` can\s+produce cross-rater agreement that is "
     r"still menu-induced construction\.\s*\n\s*\n\*\*Design", 84,
     "r49 closed the shared-criterion-TEXT channel (+0.0777 vs +0.0599, paired +0.0172 excluding "
     "zero); only shared RESPONSE exposure survives, and that is what the PRE arm separates"),
]


# ---- cross-round corrections, discovered from VERDICTS -------------------
#
# Entry 104: r36's verdict corrects r32 -- "r32's +0.0876 was the value of adding
# sign LAST to text alone -- one path through the lattice, not the channel's
# average worth" -- and that correction never reached the layer table or the
# preregistration, both of which kept r32's figure.
#
# Neither of this file's other mechanisms could see it. The REGISTRY above only
# knows what someone added to it, and entry 84's RETRACTIONS sweep only sees
# corrections written as retraction entries. This one lived in one round's
# verdict, about another round.
#
# Reported as a STANDING LIST, not a gate: a verdict can name another round to
# agree with it, and telling agreement from correction is not mechanical. The
# swept class is small -- four sentences across every verdict in the package --
# so the list is short enough to re-read whenever it changes.
_SKIPPED_NON_DICT: list[str] = []   # stated, never swallowed
NAMES_ROUND = re.compile(r"\br(\d{2})'?s?\b")
CORRECTIVE = re.compile(
    r"(over-?attribut|under-?attribut|was the value of|one path|not the channel|retract|"
    r"supersed|corrects?\b|refut|overturn|was wrong|too strong|withdraw|is not what|"
    r"rather than what|inflat|weaker than|does not survive|neither confirms)", re.I)
PROVISIONAL_RE = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)


def cross_round_corrections() -> list[tuple[str, list[str], str]]:
    out = []
    for f in sorted(_ROOT.glob("E*/A*/R*/results/*.json")):
        if PROVISIONAL_RE.search(f.name):
            continue
        rid = f.parts[-3].split("_")[0]
        try:
            doc = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            # NOT `except Exception`. This function returned 0 for its whole first
            # life because `json` was not imported at module level, every file
            # raised NameError, and a bare except swallowed all 238 of them into a
            # clean zero. Catch what a bad file raises; let a broken function crash.
            continue
        # ⚠ A results file whose TOP LEVEL IS A LIST carries no verdict key -- 14 exist (the
        # census waves, the triple-blind grids, `_ops.json`). That is a legitimate shape, not a
        # bad file. But `doc.get` raises AttributeError on it, and because the except above is
        # deliberately narrow -- so a broken FUNCTION crashes rather than returning a clean zero
        # -- the crash made this check exit 1 on EVERY tree, clean or not. `attack_every_check`
        # convicted it as "fires on the CLEAN tree too, not specific", which is exactly right:
        # a check that always says no carries the same information as one that always says yes.
        # Skipped EXPLICITLY and COUNTED, because a silent skip is how the original 238-file
        # NameError hid for this function's whole first life.
        if not isinstance(doc, dict):
            _SKIPPED_NON_DICT.append(f.name)
            continue
        v = doc.get("verdict") or doc.get("conclusion")
        if not isinstance(v, str):
            continue
        for sent in re.split(r"(?<=[.;])\s+", v.split(" || ")[0]):
            named = sorted({f"r{m}" for m in NAMES_ROUND.findall(sent)} - {rid})
            if named and CORRECTIVE.search(sent):
                out.append((rid, named, sent.strip()[:150]))
    return out


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0


def main() -> int:
    files = [(f, (_ROOT / f)) for f in WATCHED if (_ROOT / f).exists()]
    absent = [f for f in WATCHED if not (_ROOT / f).exists()]
    print(f"watched documents present: {len(files)} of {len(WATCHED)}  "
          f"({', '.join(f for f, _ in files)})")
    if absent:
        print(f"  ABSENT AND THEREFORE UNCHECKED: {', '.join(absent)}")
        print("  A watched document that is not on disk is not clean -- it is unscanned.")
    print(f"registered corrections: {len(CORRECTED)}\n")

    hits = []
    for name, path in files:
        text = path.read_text()
        for pat, entry, correct in CORRECTED:
            for m in re.finditer(pat, text, re.I):
                line = text[:m.start()].count("\n") + 1
                hits.append((name, line, m.group(0)[:60], entry, correct))

    floor = _floor(len(files) * len(CORRECTED), "the watched-document x correction grid")
    if floor:
        return floor

    xr = cross_round_corrections()
    print(f"cross-round corrections stated in verdicts: {len(xr)}")
    for rid, named, sent in xr:
        print(f"  {rid} -> {', '.join(named)}: {sent[:110]}")
    print("  A standing list, not a gate -- a verdict can name another round to AGREE with it,")
    print("  and telling agreement from correction is not mechanical. Re-read when it changes;")
    print("  entry 104 is what happens when one of these never reaches the summaries.\n")

    if not hits:
        print("No superseded form survives in a watched document.")
        print("  This covers only the corrections REGISTERED above. A correction not added")
        print("  here is invisible to this check, so registering is part of correcting.")
        return 0

    print(f"{len(hits)} superseded form(s) still present:\n")
    for name, line, frag, entry, correct in hits:
        print(f"  {name}:{line}  \"{frag}\"")
        print(f"      corrected by entry {entry} -- {correct}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
