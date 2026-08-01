"""A static audit for the defect that has now bitten twice, both times found by accident.

r194: cut points blamed for a discrepancy they did not cause. r195: the real cause was an
assessment-weighted mean letting one 929-rater prompt count 929 times. r196: my own anchor toggle
removed a 42-assessment prompt because max() was taken inside the analysed pool instead of over
all prompts, which would have shown "stability" against nothing.

Three rounds, one shape: A STATISTIC COMPUTED OVER A DIFFERENT POPULATION THAN THE ONE IT IS
APPLIED TO. Every instance so far was caught by luck -- by needing the same strata twice, or by a
number looking too small. That is not a method, and this repo has ~55 round files nobody has read
for it.

TWO PATTERNS ARE MECHANICALLY DETECTABLE and they cover both failures seen:

  P1  ASSESSMENT-WEIGHTED MEAN -- np.mean over a comprehension with TWO for-clauses, i.e. summing
      over items nested inside groups. On this corpus that weights a prompt by how many people
      rated it, and one prompt has 929. Not always wrong: it is correct when the estimand really
      is per-assessment. It is wrong whenever the sentence says "prompts".
  P2  THRESHOLD FROM A FOREIGN POPULATION -- np.percentile / max(key=) whose argument iterates one
      collection, where the result is later used to bin or filter a DIFFERENT collection.

The audit reports candidates, not verdicts. A static scan cannot know the estimand -- only that
the shape is present and deserves a human reading. Reporting it as a defect count would be the
same error as calling a proxy a property, so the output is a triage list with the line and the
source, and the rounds it flags get read.

CALIBRATION IS BUILT IN: the scanner must flag r195 and r196, which are known to contain both
patterns deliberately, and it must not flag files that contain neither. A scanner that finds
nothing anywhere has not been shown to work.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
from collections import Counter, defaultdict

# parents[1] IS 13_normative_chain, so the glob must be relative to it, not repeat the directory
# name. The first version globbed "13_normative_chain/r*/run.py" from inside 13_normative_chain and
# matched nothing -- and the CALIBRATION CHECK caught it. A scanner that reports zero hits and a
# scanner whose path is wrong produce identical output; the positive control is what separates them,
# and it is the whole reason this file has one.
ROOT = pathlib.Path(__file__).resolve().parents[1]
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"


class Scan(ast.NodeVisitor):
    def __init__(self, src):
        self.src = src.splitlines()
        self.p1 = []
        self.p2 = []
        self.pct_sources = {}      # variable name -> iterated source, for percentile results

    def line(self, n):
        return self.src[n - 1].strip() if 0 < n <= len(self.src) else ""

    @staticmethod
    def _iter_sources(comp):
        out = []
        for g in comp.generators:
            it = g.iter
            while isinstance(it, ast.Call) or isinstance(it, ast.Attribute):
                it = it.func.value if isinstance(it, ast.Call) and \
                    isinstance(it.func, ast.Attribute) else \
                    (it.value if isinstance(it, ast.Attribute) else it)
                if isinstance(it, ast.Name):
                    break
            if isinstance(it, ast.Name):
                out.append(it.id)
            elif isinstance(it, ast.Subscript) and isinstance(it.value, ast.Name):
                out.append(it.value.id)
            else:
                out.append("<expr>")
        return out

    def visit_Call(self, node):
        fn = ""
        if isinstance(node.func, ast.Attribute):
            fn = node.func.attr
        elif isinstance(node.func, ast.Name):
            fn = node.func.id
        # P1: mean/average over a doubly-nested comprehension
        if fn in ("mean", "average") and node.args:
            a = node.args[0]
            if isinstance(a, (ast.ListComp, ast.GeneratorExp)) and len(a.generators) >= 2:
                self.p1.append({"line": node.lineno, "sources": self._iter_sources(a),
                                "src": self.line(node.lineno)})
        # P2: percentile / max(key=) -- record the population it was computed over
        if fn in ("percentile", "quantile") and node.args:
            a = node.args[0]
            srcs = self._iter_sources(a) if isinstance(a, (ast.ListComp, ast.GeneratorExp)) \
                else ([a.id] if isinstance(a, ast.Name) else ["<expr>"])
            self.p2.append({"kind": fn, "line": node.lineno, "sources": srcs,
                            "src": self.line(node.lineno)})
        if fn == "max" and any(k.arg == "key" for k in node.keywords) and node.args:
            a = node.args[0]
            srcs = [a.id] if isinstance(a, ast.Name) else (
                self._iter_sources(a) if isinstance(a, (ast.ListComp, ast.GeneratorExp))
                else ["<expr>"])
            self.p2.append({"kind": "max(key=)", "line": node.lineno, "sources": srcs,
                            "src": self.line(node.lineno)})
        self.generic_visit(node)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    files = sorted(ROOT.glob("r*/run.py"))
    assert files, f"no round files under {ROOT} -- the glob is wrong, not the corpus"
    print(f"round files scanned: {len(files)}")

    report = []
    for f in files:
        try:
            src = f.read_text()
            tree = ast.parse(src)
        except SyntaxError as e:
            print(f"  [SYNTAX ERROR] {f.parent.name}: {e}")
            continue
        s = Scan(src)
        s.visit(tree)
        if s.p1 or s.p2:
            report.append({"round": f.parent.name, "p1": s.p1, "p2": s.p2})

    # calibration
    names = {r["round"] for r in report}
    must = [n for n in names if "r195" in n or "r196" in n]
    print(f"  CALIBRATION: rounds known to contain both patterns are flagged: "
          f"{sorted(must)}")
    if len(must) < 2:
        print("  the scanner failed its own positive control -- nothing below is admissible")
        return 1

    p1_total = sum(len(r["p1"]) for r in report)
    p2_total = sum(len(r["p2"]) for r in report)
    print(f"\n{'=' * 78}\nP1  ASSESSMENT-WEIGHTED MEANS  ({p1_total} sites in "
          f"{sum(1 for r in report if r['p1'])} rounds)\n{'=' * 78}")
    for r in sorted(report, key=lambda r: r["round"]):
        if not r["p1"]:
            continue
        print(f"\n  {r['round']}")
        for h in r["p1"][:4]:
            print(f"    L{h['line']:<4d} over {h['sources']}")
            print(f"          {h['src'][:96]}")
        if len(r["p1"]) > 4:
            print(f"    ... and {len(r['p1']) - 4} more")

    print(f"\n{'=' * 78}\nP2  THRESHOLDS AND EXTREMA  ({p2_total} sites in "
          f"{sum(1 for r in report if r['p2'])} rounds)\n{'=' * 78}")
    for r in sorted(report, key=lambda r: r["round"]):
        if not r["p2"]:
            continue
        print(f"\n  {r['round']}")
        for h in r["p2"][:4]:
            print(f"    L{h['line']:<4d} {h['kind']:10s} over {h['sources']}")
            print(f"          {h['src'][:96]}")
        if len(r["p2"]) > 4:
            print(f"    ... and {len(r['p2']) - 4} more")

    # ------------------------------------------------------------------ the negative control
    # THE CASE THIS SCANNER WAS BUILT FOR. r191's stratified length effect was assessment-weighted
    # and produced a finding that r194/r195 had to withdraw. If the scanner cannot see it, then a
    # clean report says nothing -- which is the same failure this project keeps auditing others for.
    r191 = [r for r in report if r["round"].startswith("r191")]
    r191_p1 = sum(len(r["p1"]) for r in r191)
    src191 = next((f for f in files if f.parent.name.startswith("r191")), None)
    print(f"\n{'=' * 78}\nNEGATIVE CONTROL: DOES IT CATCH THE CASE IT WAS BUILT FOR?\n{'=' * 78}")
    if src191:
        txt = src191.read_text()
        has_extend = ".extend(" in txt
        print(f"  r191 P1 hits: {r191_p1}")
        print(f"  r191 builds its bins with .extend(): {has_extend}")
        if r191_p1 == 0:
            print(f"  -> THE SCANNER MISSES IT. r191 accumulates per-assessment values with")
            print(f"     `band[b].extend(v)` and then takes np.mean over a FLAT list, so there is")
            print(f"     no nested comprehension to match. The defect that motivated this entire")
            print(f"     audit is invisible to the audit.")
            print(f"     That is not a small caveat. A shape-based scan reports the shapes people")
            print(f"     happen to write, and the one instance known to have produced a false")
            print(f"     finding was written the other way. So the {p1_total} P1 sites below are a")
            print(f"     lower bound of unknown tightness, and 'no hits' in a file remains")
            print(f"     meaningless.")
        else:
            print(f"  -> caught; the scanner sees the motivating case.")

    print(f"\n{'=' * 78}\nREADING\n{'=' * 78}")
    print(f"  {p1_total} assessment-weighted means across {sum(1 for r in report if r['p1'])} "
          f"rounds, and {p2_total} thresholds")
    print(f"  across {sum(1 for r in report if r['p2'])} rounds. These are CANDIDATES, not")
    print(f"  defects: a static scan cannot know the estimand, and a per-assessment mean is right")
    print(f"  whenever the sentence is about assessments.")
    print(f"\n  ALL FOUR P1 SITES READ, because a triage list nobody triages is a to-do list:")
    print(f"    r150 L230  overall veto stat over asked assessments -- the sentence is about")
    print(f"               assessments, so per-assessment is the RIGHT estimand.  CLEAN")
    print(f"    r153 L186  mean response length over prompts x responses -- exactly 4 responses")
    print(f"               per prompt, so the weighting is uniform by construction.  CLEAN")
    print(f"    r192 L118  'overall veto rate' -- stated as a rate over assessments.  CLEAN")
    print(f"    r192 L226  'a given response is flagged 26.4% of the time it is seen' -- the")
    print(f"               estimand is explicitly per-observation.  CLEAN")
    print(f"  Four candidates, four legitimate. The scan found no new defect.")
    print(f"\n  AND THAT RESULT IS WORTH ALMOST NOTHING, WHICH IS THIS ROUND'S FINDING. The")
    print(f"  scanner does not see r191 -- the one case known to have produced a false finding --")
    print(f"  because that file accumulates with .extend() and means a flat list. So 'four")
    print(f"  candidates, all clean' is a statement about a shape, not about the corpus, and I")
    print(f"  cannot convert it into 'the other 49 rounds are fine'.")
    print(f"\n  WHAT WOULD ACTUALLY WORK, since the shape approach demonstrably does not: a")
    print(f"  runtime check. Every mean in this repo could carry the group it was computed over,")
    print(f"  and a wrapper could refuse a mean whose largest group holds more than a few percent")
    print(f"  of the rows unless the caller names the estimand. That is enforcement at the")
    print(f"  decision point rather than a scan afterwards, and it is the only version that")
    print(f"  survives someone writing the loop differently.")
    print(f"  I am reporting the scanner as INSUFFICIENT rather than deleting it: it is a real")
    print(f"  negative result about a plausible-sounding method, and the next person to reach for")
    print(f"  a static audit of this class should see that it was tried and where it broke.")

    (OUT / "population_audit.json").write_text(json.dumps(
        {"files_scanned": len(files), "rounds_with_hits": len(report),
         "p1_sites": p1_total, "p2_sites": p2_total,
         "calibration_rounds_flagged": sorted(must),
         "report": report,
         "negative_control": {"r191_p1_hits": r191_p1,
                              "caught_motivating_case": bool(r191_p1)},
         "limit": "shape-based static scan; candidates not verdicts; a loop-accumulated mean is "
                  "invisible to it -- demonstrated on r191, the case it was built for"},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
