#!/usr/bin/env python3
"""
R697 -- how many "not resolved" verdicts were silence? The floor, computed for every cell that has one.

CHECK #299 ON R696's NEXT LINE -- IT HOLDS, and its instrument caveat is what shaped this round.
  `resolution_floor` is present in R696's artifact and the question it poses has a live kill.

⚠ THE INSTRUMENT DECISION, MADE BEFORE THE SWEEP. 14 artifacts carry a resolve-flag and a field named
  `n`, but `n` is a SAMPLE size in one round, a SPEC count in another, a NULL CELL count in a third.
  Taking every `n` as a null size is the R695 failure exactly -- matching a name and claiming a
  quantity. ⭐ Discriminating rule: a null size is `n` CO-LOCATED IN THE SAME DICT as a p-value.

ESTIMAND        across this arc, how many verdicts reported as NOT RESOLVED came from a design whose
                minimum achievable p exceeded the 0.05 threshold -- i.e. could not have resolved?
IDENTIFICATION  ⚠ floor = 2/n assumes n is the null's cardinality and the test two-sided. Where a
                round stored draws rather than cells, or tested one-sided, the floor is off by 2x.
                Reported as a sensitivity, not hidden.
SCOPE           population : every results/*.json in the arc
                instrument : co-located (n, p, resolve) triples + floor arithmetic
                             instrument unit = A CO-LOCATED TRIPLE
                             claim unit      = A VERDICT THAT COULD NOT HAVE RESOLVED
                             ⚠ NOT EQUAL -- a triple may describe a cell whose verdict was never
                             reported as a finding. Carried into the verdict.
                baseline   : the 0.05 threshold these rounds used
                regime     : this repository at HEAD
WORLDS          A A CLASS: several non-resolutions could not have resolved -> "not resolved" has
                  been reported as evidence when it was silence.
                B ONE INSTANCE: only R495 -> R696's closing claim narrows to a single case.
KILL            zero such cells -> world B, say so instead of generalising.
POSITIVE CTRL   R361's 0.8B cell must be FOUND and correctly NOT flagged (floor 0.0159 << 0.05).
g=0             a synthetic n=10, p=0.3, not-resolved cell MUST be flagged.
NEGATIVE CTRL   a resolve flag with no p is not counted.
PLACEBO         run twice identical.
ARTIFACT        results/floors.json
IMPOSSIBLE      whether a round's `n` counted draws or exact cells is not recorded; the 2x
                sensitivity is the honest expression of that.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
THRESH = 0.05
PKEYS = {"p", "two_sided_p", "pval", "p_value"}
NKEYS = {"n", "n_draws", "n_perm", "null_cells", "cells", "n_null"}
RKEYS = {"resolved", "is_resolved", "rank_resolved", "resolvable"}


def triples(o, where, path="", out=None):
    """(n, p, resolved) CO-LOCATED in one dict. Co-location is the discriminating rule."""
    if out is None: out = []
    if isinstance(o, dict):
        n = next((v for k, v in o.items() if k.lower() in NKEYS and isinstance(v, int) and v > 1), None)
        p = next((v for k, v in o.items() if k.lower() in PKEYS and isinstance(v, (int, float))), None)
        r = next((v for k, v in o.items() if k.lower() in RKEYS and isinstance(v, bool)), None)
        if n is not None and p is not None:
            out.append({"where": f"{where}:{path or '(root)'}", "n": n, "p": p, "resolved": r})
        for k, v in o.items():
            if isinstance(v, (dict, list)): triples(v, where, f"{path}.{k}" if path else k, out)
    elif isinstance(o, list):
        for i, v in enumerate(o[:20]):
            if isinstance(v, (dict, list)): triples(v, where, f"{path}[{i}]", out)
    return out


def main() -> int:
    cells = []
    for j in sorted(ARC.rglob("results/*.json")):
        try: d = json.loads(j.read_text())
        except Exception: continue
        cells += triples(d, j.parent.parent.name.split("_")[0])
    if not cells:
        print("UNRUNNABLE: 0 co-located triples. Exit 2, never 0."); return 2

    print("─── CONTROLS ───")
    r361 = [c for c in cells if c["where"].startswith("R361") and abs(c["p"] - 0.2857) < 1e-3]
    posok = bool(r361) and 2 / r361[0]["n"] < THRESH
    print(f"  POSITIVE  R361's 0.8B cell found (n=126, p=0.2857) and correctly NOT flagged "
          f"(floor {2/r361[0]['n']:.4f} << {THRESH}) -> {posok} -> "
          f"{'PASS' if posok else '⛔ FAIL — the instrument cannot find a real cell'}")
    syn = triples({"n": 10, "p": 0.3, "resolved": False}, "SYNTH")
    g0ok = bool(syn) and 2 / syn[0]["n"] > THRESH
    print(f"  g=0       a synthetic n=10, p=0.3 cell IS flagged (floor {2/10:.2f} > {THRESH}) -> "
          f"{g0ok} -> {'PASS — the detector returns both values' if g0ok else '⛔ FAIL'}")
    negok = not triples({"resolved": False, "note": "no p here"}, "SYNTH")
    print(f"  NEGATIVE  a resolve flag with no p is not counted -> {'PASS' if negok else '⛔ FAIL'}")
    plc = len(triples(json.loads(next(ARC.glob("R361_*/results/*.json")).read_text()), "x")) == \
          len(triples(json.loads(next(ARC.glob("R361_*/results/*.json")).read_text()), "x"))
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    # ⭐⭐⭐ CO-LOCATION WAS NOT SUFFICIENT, AND THAT IS R695's FAILURE ONE ROUND AFTER NAMING IT.
    #     `R431:slope_cells` carries n=2..4 beside p=0.87 -- but a permutation/exact p over N cells
    #     MUST be an integer multiple of 1/N, and 0.87 is not a multiple of 1/2. So that `n` is a
    #     SAMPLE SIZE, not a null cardinality, and treating it as one inflated the count.
    #     ⭐ THE DECISIVE TEST: p is admissible as coming from an N-cell null only if p is an integer
    #     multiple of 1/N (within float tolerance). Cells failing it are EXCLUDED, not counted.
    def multiple_of(p_, n_):
        if n_ <= 0: return False
        q = p_ * n_
        return abs(q - round(q)) < 1e-6
    kept, dropped = [], []
    for c in cells:
        (kept if multiple_of(c["p"], c["n"]) else dropped).append(c)
    print(f"\n  ⚠ CO-LOCATION IS NOT ENOUGH: of {len(cells)} co-located triples, {len(dropped)} have "
          f"a p that is NOT an integer multiple of 1/n, so their `n` is a SAMPLE SIZE and not a null "
          f"cardinality. Excluded. {len(kept)} remain.")
    from collections import Counter
    for w, k in Counter(c["where"].split(":")[0] for c in dropped).most_common(5):
        print(f"     dropped {k:>3} from {w}")
    # ⭐ AND p = 1.0 IS A MULTIPLE OF EVERYTHING, so the filter above is DEGENERATE exactly there.
    #   A cell with p=1.0 carries no information about whether its `n` is a null cardinality, so it
    #   is UNVERIFIED as to instrument and is reported separately -- never counted as evidence that
    #   a design could not resolve. Third filter in one round; the `n` field in this corpus is not a
    #   stable quantity and that is itself the finding.
    degenerate = [c for c in kept if abs(c["p"] - 1.0) < 1e-9]
    kept = [c for c in kept if abs(c["p"] - 1.0) >= 1e-9]
    print(f"  ⚠ AND p=1.0 IS A MULTIPLE OF EVERYTHING: {len(degenerate)} cell(s) have p=1.0, where "
          f"the filter cannot discriminate. UNVERIFIED as to instrument, reported separately, not "
          f"counted. {len(kept)} cells remain with 0 < p < 1.")
    cells = kept
    if not cells:
        print("  UNRUNNABLE after the multiple-of-1/n filter: 0 cells. Exit 2."); return 2

    for c in cells:
        c["floor_2s"] = 2 / c["n"]
        c["floor_1s"] = 1 / c["n"]
        c["could_not_resolve_2s"] = c["floor_2s"] > THRESH
        c["could_not_resolve_1s"] = c["floor_1s"] > THRESH
        c["at_its_floor"] = abs(c["p"] - c["floor_2s"]) < 1e-9

    notres = [c for c in cells if c["resolved"] is False or (c["resolved"] is None and c["p"] >= THRESH)]
    blind2 = [c for c in notres if c["could_not_resolve_2s"]]
    blind1 = [c for c in notres if c["could_not_resolve_1s"]]
    atfloor = [c for c in cells if c["at_its_floor"]]

    print(f"\n─── THE FLOORS (G3 — every co-located cell) ───")
    print(f"  co-located (n, p, resolve) cells : {len(cells)}")
    print(f"  reported NOT resolved            : {len(notres)}")
    print(f"  ⭐ COULD NOT HAVE RESOLVED (two-sided floor > {THRESH}) : {len(blind2)}")
    print(f"  ⚠ same count under a ONE-sided floor                   : {len(blind1)}  "
          f"(the 2x sensitivity, reported not hidden)")
    for c in blind2[:10]:
        print(f"     {c['where'][:56]:<58} n={c['n']:<5} p={c['p']:.4f} floor={c['floor_2s']:.4f}")
    # ⭐ AND THE "AT FLOOR" CELLS ARE MOSTLY ONE MEASUREMENT, COPIED. Dedupe by (n, p) before
    #   quoting a count -- R680 measured that this corpus re-quotes numbers across artifacts.
    uniq_at = {(c["n"], round(c["p"], 6)) for c in atfloor}
    print(f"  ⭐ cells sitting EXACTLY AT their own floor: {len(atfloor)} occurrences, "
          f"⭐ {len(uniq_at)} DISTINCT (n,p) -- the rest are the same measurement re-quoted across "
          f"artifacts, including this round's own copies (R680's finding, live here).")
    for c in atfloor[:5]:
        print(f"     {c['where'][:56]:<58} n={c['n']:<5} p={c['p']:.4f}")
    print(f"\n  registered A 18 [3,60] -> {len(cells)}: "
          f"{'INSIDE' if 3 <= len(cells) <= 60 else '⛔ OUTSIDE'}, error {len(cells)-18:+d}")
    print(f"  registered B 2 [0,10] -> {len(blind2)}: "
          f"{'INSIDE' if 0 <= len(blind2) <= 10 else '⛔ OUTSIDE'}, error {len(blind2)-2:+d}")
    others = [c for c in blind2 if not c["where"].startswith("R495")]
    dirn = len(others) >= 1
    print(f"  DIRECTIONAL >=1 such cell besides R495's -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(blind2) == 0
    print(f"  pre-registered kill (zero such cells) -> "
          f"{'⭐ FIRES — R495 is unique; narrow R696s claim' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"B ONE INSTANCE — no co-located cell in this arc reports a non-resolution from a "
                 f"design whose floor exceeded {THRESH}. R495's case is singular and R696's closing "
                 f"claim narrows to it.")
    else:
        world = (f"⭐⭐⭐ A A CLASS — {len(blind2)} of {len(notres)} non-resolutions came from a design "
                 f"whose minimum achievable two-sided p EXCEEDED {THRESH}: those verdicts could not "
                 f"have resolved, so 'not resolved' there is SILENCE, not evidence. "
                 f"{len(others)} are outside R495. ⭐ AND {len(atfloor)} cell(s) sit EXACTLY at their "
                 f"own floor -- the most extreme value the design permits, which is the mirror "
                 f"failure: a p that cannot go lower reported as though it could. ⚠ SENSITIVITY: "
                 f"under a one-sided floor the count is {len(blind1)}, because whether a round's `n` "
                 f"counted draws or exact cells is not recorded anywhere. ⚠ AND THE UNIT GAP: a "
                 f"co-located triple is a CELL, not necessarily a REPORTED FINDING -- some of these "
                 f"were never quoted as verdicts.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(cells)} cells × 2 floor conventions, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"floors.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "threshold": THRESH,
        "n_cells": len(cells), "n_dropped_not_multiple": len(dropped), "n_degenerate_p1": len(degenerate),
        "degenerate": degenerate[:20], "n_not_resolved": len(notres),
        "n_could_not_resolve_two_sided": len(blind2), "n_could_not_resolve_one_sided": len(blind1),
        "n_at_their_floor": len(atfloor), "n_distinct_at_floor": len({(c["n"], round(c["p"],6)) for c in atfloor}), "blind": blind2, "at_floor": atfloor,
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 18 [3,60]; B 2 [0,10]; >=1 besides R495; kill if zero",
        "limit": ("floor = 2/n assumes n is the null's cardinality and a two-sided test; the "
                  "one-sided count is reported beside it as the sensitivity."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'floors.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
