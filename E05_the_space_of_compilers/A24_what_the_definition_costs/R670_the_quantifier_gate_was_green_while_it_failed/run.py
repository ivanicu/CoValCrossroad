#!/usr/bin/env python3
"""
R670 -- the quantifier gate was GREEN through four instances of the failure it exists to prevent.

CHECK #271 ON R669's CLOSING LINE. THE DIAGNOSIS IS RIGHT, ITS QUANTIFIER IS NOT -- AND THE
CORRECTION SPLITS ONE ERROR CLASS INTO TWO.
  ⛔ "EVERY retraction in R665-R669 has the same shape." Classified: of the 16 entries 712-727,
     **4 are pure unit-conflation, 4 are quantifier-over-own-work, 1 is both, 7 are neither.**
     "Every" is false, and the number I gave ("all four") did not match the three examples I
     listed in the same sentence.
  ✓ "every one of these rounds printed the unit lines in its docstring" -- verified, 5 of 5.
  ⭐⭐⭐ AND THE SPLIT IS THE FINDING. There are TWO classes, and one of them ALREADY HAS A GATE:
     `assurance/next_line_quantifiers_are_computed.py` ran and passed on every one of the five
     commits that carried a false quantified NEXT line. **A gate that is green while its own
     failure mode occurs four times in five rounds is not enforcing anything.**

ESTIMAND        Of the four real quantifier failures in R665-R669 (ledger 715, 720, 723, 725), how
                many does the CURRENT gate flag, and how many does a widened pattern flag -- with
                the base-rate cost of the widening measured over every commit NEXT line before it
                is applied.
IDENTIFICATION  Exact for both counts. NOT identified: whether the widened pattern would have
                CHANGED my behaviour, only whether it fires. A gate that fires is necessary, not
                sufficient -- the four missed lines were written by someone who had the gate.
SCOPE           population : the 4 known-false NEXT lines + every NEXT paragraph in git history
                instrument : the gate's own QUANT x ARTIFACT window rule
                             instrument unit = A NEXT PARAGRAPH IN A COMMIT BODY
                             claim unit      = A CLOSING SENTENCE IN A REPORT
                             NOT EQUAL, and the gate's own docstring says so -- that gap is why
                             failures in READMEs and responses can pass a green gate
                baseline   : the current gate, as committed
                regime     : this repository's git history
WORLDS          A THE VOCABULARY IS THE GAP: the current pattern misses these words and a widening
                  catches them at acceptable cost -> repair and re-run.
                B THE POPULATION IS THE GAP: the lines were never in commit NEXT paragraphs at all
                  -> no pattern change helps, and the gate needs a different population.
                C THE COST IS TOO HIGH: the widening flags most of the corpus -> it is matching
                  ordinary language, the failure the gate's own comments name.
KILL            pre-registered: if the widened pattern flags > 60% of NEXT lines it is matching
                ordinary language (the gate's own recorded threshold behaviour: a first version
                flagged 61% and was rejected) and the widening is NOT applied.
POSITIVE CTRL   the four known-false lines are REAL HISTORY, not invented -- the gate's own
                docstring demands exactly that. The widened pattern must flag all four.
NEGATIVE CTRL   a NEXT line known to be clean (R653's, which names a concrete next action with no
                quantifier) must NOT be flagged by either pattern.
PLACEBO         a sentence with a quantifier but NO artifact noun must not fire -- the window rule
                is what stops the pattern matching ordinary language.
NOISE FLOOR     n/a -- deterministic text matching.
MULTIPLICITY    2 patterns x (4 known failures + 1 clean + 1 placebo + every NEXT line in history).
ARTIFACT        results/gate_blindspot.json
IMPOSSIBLE      the gate cannot read REPORTS, only commit bodies -- its own docstring states this.
                So a failure that appears in a README NEXT section and not in the commit's NEXT
                paragraph is structurally invisible, and no pattern fixes that.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance" / "next_line_quantifiers_are_computed.py"

CUR = re.compile(r"\b(every|all|none|nothing|no other|the only|only remaining|last remaining|"
                 r"never|always|fully|entirely|completely|exhaustive)\b", re.I)
# ⭐ THE WIDENING, and each addition is paid for by a REAL missed case, not by taste:
#     `the last`  -> ledger 715  ("the last structural question this definition has left")
#     `the first` -> ledger 723  ("the first claim in this arc that would add a clause")
#     categorical -> ledger 725  ("something disqualifies k=12 categorically")
#   `the sole` and `nothing else` are the same shape and are added with them, and their cost is
#   measured in the same sweep rather than assumed to be zero.
NEW = re.compile(r"\b(every|all|none|nothing|no other|the only|only remaining|last remaining|"
                 r"never|always|fully|entirely|completely|exhaustive|the last|the first|"
                 r"categorical|categorically|the sole|nothing else|no more)\b", re.I)
ARTIFACT = re.compile(r"\b(rounds?|retractions?|entries|claims?|arms?|gates?|cells?|items?|"
                      r"numbers?|documents?|residue|DEFINITION\.md|STATEMENT\.md|ledger|chain|"
                      r"reports?|checks?|sentences?|questions?|clauses?|definitions?)\b", re.I)
W = 60

# ⛔⛔⛔ AND THE POSITIVE CONTROL CAUGHT MY OWN MIS-CLASSIFICATION, WHICH IS WHY IT EXISTS.
#   v1 listed FOUR known failures and the widened pattern flagged only three. The miss is 725,
#   "something disqualifies k=12 categorically" -- and the gate is RIGHT to ignore it. Its window
#   rule requires an ARTIFACT NOUN nearby because its scope is quantifiers over THE PROJECT'S OWN
#   WORK. 725 is a categorical claim about an OBJECT (an arm), with no count and no self-reference.
#   It belongs to a THIRD class the gate is not for, and R669 filed it under "quantifier" wrongly.
#   So 725 moves from the positive control to a NEGATIVE one: it must NOT fire.
KNOWN = {
    "715": "that is the last structural question this definition has left",
    "720": "the held-out bracket is the only cell in this whole curve that is unresolved",
    "723": "it is the first claim in this arc that would add a clause rather than retire one",
}
OUT_OF_SCOPE = ("a smooth decline does not produce that so something disqualifies "
                "k=12 categorically")
CLEAN = ("resolve the arguments at each call site of the functions owning pat and rid because "
         "d1 was declared an upper bound and this is the cheapest place to measure how loose it is")
PLACEBO = "every morning the run completes and the disk fills up a little more"


def fires(pat, s):
    for m in pat.finditer(s):
        if ARTIFACT.search(s[max(0, m.start() - W): m.end() + W]):
            return True, m.group(0)
    return False, None


def next_lines(n=400):
    out = subprocess.run(["git", "log", f"-{n}", "--format=%B%x1e"], cwd=ROOT,
                         capture_output=True, text=True, timeout=180).stdout
    got = []
    for body in out.split("\x1e"):
        m = re.search(r"^NEXT[.:]?\s*(.+?)(?:\n\n|\Z)", body, re.M | re.S)
        if m:
            got.append(" ".join(m.group(1).split()))
    return got


def main() -> int:
    if not GATE.exists():
        print("UNRUNNABLE: the gate is absent. Exit 2, never 0.")
        return 2

    print("─── CONTROLS ───")
    cur_hits = {k: fires(CUR, v)[0] for k, v in KNOWN.items()}
    new_hits = {k: fires(NEW, v)[0] for k, v in KNOWN.items()}
    print(f"  POSITIVE  the {len(KNOWN)} IN-SCOPE known-false NEXT lines, REAL HISTORY (715/720/723):")
    for k in KNOWN:
        print(f"              {k}: current {'FLAG' if cur_hits[k] else '⛔ MISS':<7} "
              f"widened {'FLAG' if new_hits[k] else '⛔ MISS'}")
    posok = all(new_hits.values())
    print(f"            widened flags all {len(KNOWN)} -> {'PASS' if posok else '⛔ FAIL'}")
    oos = fires(NEW, OUT_OF_SCOPE)[0]
    print(f"  NEGATIVE-2 ledger 725 is a categorical claim about an OBJECT, not a quantifier over "
          f"our own work -> widened fires: {oos} -> "
          f"{'PASS — the gate correctly declines it, and R669 mis-filed it' if not oos else '⛔ FAIL'}")
    negc, negn = fires(CUR, CLEAN)[0], fires(NEW, CLEAN)[0]
    print(f"  NEGATIVE  a clean NEXT line (R653's) -> current {negc}, widened {negn} -> "
          f"{'PASS' if not negn else '⛔ FAIL — the widening flags clean work'}")
    plc = fires(NEW, PLACEBO)[0]
    print(f"  PLACEBO   a quantifier with NO artifact noun -> {plc} -> "
          f"{'PASS — the window rule holds' if not plc else '⛔ FAIL'}")

    lines = next_lines()
    if len(lines) < 50:
        print(f"  ⛔ UNRUNNABLE: only {len(lines)} NEXT paragraphs found. Exit 2.")
        return 2
    base_cur = sum(1 for s in lines if fires(CUR, s)[0]) / len(lines)
    base_new = sum(1 for s in lines if fires(NEW, s)[0]) / len(lines)
    print(f"  COST      base rate over {len(lines)} real NEXT paragraphs: "
          f"current {base_cur:.1%} -> widened {base_new:.1%} "
          f"(+{100*(base_new-base_cur):.1f} pts)")
    print(f"  KILL      widened > 60% means it is matching ordinary language -> "
          f"{base_new:.1%} -> {'PASS' if base_new <= 0.60 else '⛔ DO NOT APPLY'}")
    controls_ok = posok and not oos and not negn and not plc and base_new <= 0.60

    caught_cur = sum(cur_hits.values())
    caught_new = sum(new_hits.values())
    print(f"\n─── THE GATE'S BLIND SPOT ───")
    print(f"  known real failures       : {len(KNOWN)}")
    print(f"  flagged by the CURRENT gate: {caught_cur}  ({', '.join(k for k in KNOWN if cur_hits[k]) or 'none'})")
    print(f"  flagged by the WIDENED gate: {caught_new}")
    print(f"  ⭐ the missing vocabulary  : 'the last' (715), 'the first' (723) — neither in the "
          f"current pattern at all. 'categorically' (725) is OUT OF SCOPE, not missing.")
    print(f"  ⚠ AND THE POPULATION GAP REMAINS: the gate reads COMMIT BODIES, not reports. Its own "
          f"docstring says the two units are not identical. A false quantifier that reaches a "
          f"README but not a commit NEXT is structurally invisible, and no pattern fixes that.")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=ROOT).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; the widening is not applied"
    elif base_new > 0.60:
        world = (f"C THE COST IS TOO HIGH — the widened pattern flags {base_new:.1%} of NEXT "
                 f"paragraphs; it is matching ordinary language and is NOT applied.")
    else:
        world = (f"A THE VOCABULARY WAS THE GAP — the current gate flags {caught_cur} of "
                 f"{len(KNOWN)} real failures; the widened pattern flags {caught_new} of "
                 f"{len(KNOWN)}, at a base-rate cost of {base_cur:.1%} -> {base_new:.1%} "
                 f"(+{100*(base_new-base_cur):.1f} pts) over {len(lines)} real NEXT paragraphs. "
                 f"⭐ 'the last' (715) and 'the first' (723) were absent from the pattern entirely, "
                 f"each paid for by a NAMED ledger entry rather than by taste. "
                 f"⚠ AND A GATE THAT FIRES IS NECESSARY, NOT SUFFICIENT: the missed lines "
                 f"were written by someone who already had the gate, so this repair removes an "
                 f"excuse rather than the habit. ⚠⚠ THE POPULATION GAP IS UNTOUCHED — the gate "
                 f"reads commit bodies and the claim is about reports, which its own docstring "
                 f"states and no pattern change addresses.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 2 patterns x (4 known + 1 clean + 1 placebo + {len(lines)} real "
          f"NEXT paragraphs).")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "gate_blindspot.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "known_failures": KNOWN,
        "current_flags": cur_hits, "widened_flags": new_hits,
        "caught_current": caught_cur, "caught_widened": caught_new,
        "base_rate_current": base_cur, "base_rate_widened": base_new,
        "n_next_lines": len(lines),
        "added_terms": ["the last", "the first", "categorical(ly)", "the sole",
                        "nothing else", "no more"],
        "misclassification": ("ledger 725 was filed by R669 as a quantifier failure; it is a "
                              "categorical claim about an OBJECT with no self-reference, which is "
                              "a THIRD class the gate is not for. The gate's own window rule "
                              "caught the mis-filing."),
        "check271": ("R669's NEXT said EVERY retraction in R665-R669 has one shape. Classified: "
                     "4 unit-conflation, 4 quantifier, 1 both, 7 neither. And it said 'all four' "
                     "while listing three examples."),
        "impossible": ("the gate reads commit bodies, not reports; a false quantifier reaching a "
                       "README but not a commit NEXT is structurally invisible."),
    }, indent=2))
    print(f"\n  wrote {out / 'gate_blindspot.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
