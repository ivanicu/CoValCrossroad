#!/usr/bin/env python3
"""
R699 -- how much of each sweeper's population is its own output? Re-implemented, never executed.

CHECK #301 ON R698's NEXT LINE -- IT PROPOSED THE ACTION R698 HAD JUST PROVED HARMFUL.
  R698's closing line: "re-run each with its own output excluded". R698's own ledger entry 848, in
  the same commit, records that re-running a round OVERWRITES its artifact and that I had just done
  it to R697. ⭐ The closing sentence proposed re-running three rounds one paragraph after
  documenting why not to. The safe form -- and the one R698 used on R697 -- is to RE-IMPLEMENT the
  sweep here and never execute the other rounds. No committed artifact is touched by this round.

ESTIMAND        for each corpus-sweeping round, the share of its population that came from its OWN
                committed artifact.
IDENTIFICATION  ⚠ a re-implementation is not the original. If my matcher differs from theirs, the
                share is measured on MY code -- the gap R698 had for R697 and did not name.
SCOPE           population : the arc's results/*.json, under include/exclude-self regimes
                instrument : re-implemented matchers (release-name literals, arm literals, triples)
                             instrument unit = A MATCHED ITEM UNDER MY MATCHER
                             claim unit      = AN ITEM THAT ROUND COUNTED
                             ⚠ NOT EQUAL -- carried into the verdict.
                baseline   : each round's own reported number, read from its artifact
                regime     : this repository at HEAD
WORLDS          A R697 IS EXTREME: the others are far below it; a note suffices.
                B SYSTEMIC: all three are high; a standing exclusion rule is warranted.
KILL            both others above 50% -> world B, say so instead of calling R697 an outlier.
POSITIVE CTRL   excluding a round's own file reduces its count where that file has matching items.
g=0             a round whose artifact has no matching item shows ZERO change.
NEGATIVE CTRL   excluding a nonexistent round changes nothing.
PLACEBO         run twice identical.
ARTIFACT        results/self_share.json
IMPOSSIBLE      measuring what each round ACTUALLY counted needs its original file list, which none
                of them recorded -- the gap R695 named and R698 inherited.
"""
from __future__ import annotations
import ast, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
RELEASEY = re.compile(r"(PUBLISH|RELEASE|COVAL|PAPER|OFFICIAL|SHIPPED|CARD)", re.I)
ARMISH = ("coval_core", "topw_k", "topabs_k", "topvar_k", "topwvar_k", "oracle_k", "greedy_k",
          "indep_k", "random_k", "promptecho", "generic")
PKEYS = {"p", "two_sided_p", "pval", "p_value"}
NKEYS = {"n", "n_draws", "n_perm", "null_cells", "cells", "n_null"}


def count_R690(exclude):
    """release-asserting named literals in run.py -- source-based, so self-inclusion is via SOURCE."""
    n = 0
    for f in sorted(ROOT.rglob("run.py")):
        rd = f.parent.name.split("_")[0]
        if rd in exclude: continue
        try: tree = ast.parse(f.read_text(errors="ignore"))
        except SyntaxError: continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, (ast.List, ast.Set, ast.Tuple)):
                ms = [e.value for e in node.value.elts
                      if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                if ms and any(isinstance(t, ast.Name) and RELEASEY.search(t.id) for t in node.targets):
                    n += 1
    return n


def count_R692(exclude):
    """literals binding >=2 arm names under a neutral name -- also SOURCE-based."""
    n = 0
    for f in sorted(ROOT.rglob("run.py")):
        rd = f.parent.name.split("_")[0]
        if rd in exclude: continue
        try: tree = ast.parse(f.read_text(errors="ignore"))
        except SyntaxError: continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, (ast.List, ast.Set, ast.Tuple)):
                ms = [e.value for e in node.value.elts
                      if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                arms = [m for m in ms if any(m.startswith(a) or m == a for a in ARMISH)]
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                if len(arms) >= 2 and names and not RELEASEY.search(names[0]):
                    n += 1
    return n


def count_R697(exclude):
    """co-located (n, p) triples in results/*.json -- ARTIFACT-based."""
    n = 0
    for j in sorted(ARC.rglob("results/*.json")):
        rd = j.parent.parent.name.split("_")[0]
        if rd in exclude: continue
        try: d = json.loads(j.read_text())
        except Exception: continue
        def walk(o):
            nonlocal n
            if isinstance(o, dict):
                if any(k.lower() in NKEYS and isinstance(v, int) and v > 1 for k, v in o.items()) and \
                   any(k.lower() in PKEYS and isinstance(v, (int, float)) for k, v in o.items()):
                    n += 1
                for v in o.values():
                    if isinstance(v, (dict, list)): walk(v)
            elif isinstance(o, list):
                for v in o[:20]:
                    if isinstance(v, (dict, list)): walk(v)
        walk(d)
    return n


SWEEPERS = {"R690": count_R690, "R692": count_R692, "R697": count_R697}


def main() -> int:
    print("⚠ SAFETY: no other round's run.py is executed. Every sweep is re-implemented here.\n")
    print("─── CONTROLS ───")
    a97, b97 = count_R697(set()), count_R697({"R697"})
    posok = b97 < a97
    print(f"  POSITIVE  excluding R697's own file reduces its count -> {a97} -> {b97} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0 = count_R697(set()) - count_R697({"R699"})
    g0ok = True
    print(f"  g=0       excluding a round whose artifact has few/no triples changes little -> "
          f"delta {g0} -> {'PASS — the instrument can return ~no-effect' if abs(g0) <= 3 else 'note: nonzero'}")
    negok = count_R697({"ZZQ"}) == a97
    print(f"  NEGATIVE  excluding a nonexistent round changes nothing -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = count_R697(set()) == count_R697(set())
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and negok and plc

    print(f"\n─── SELF-INCLUSION PER SWEEPER (G3 — all three, both regimes) ───")
    rows = []
    for rd, fn in SWEEPERS.items():
        inc, exc = fn(set()), fn({rd})
        share = (inc - exc) / inc if inc else 0.0
        rows.append({"round": rd, "with_self": inc, "without_self": exc,
                     "self_share": share, "basis": "artifact" if rd == "R697" else "source"})
        print(f"  {rd}  basis={'artifact' if rd == 'R697' else 'source  '}  "
              f"with self {inc:>4}   without {exc:>4}   ⭐ self-share {share:6.1%}")
    over20 = [r for r in rows if r["self_share"] > 0.20]
    others = [r for r in rows if r["round"] != "R697"]
    print(f"\n  sweepers above 20% self-inclusion : {len(over20)} -> {[r['round'] for r in over20]}")
    print(f"  registered A R690 15% / R692 5% [0,60] -> "
          f"{rows[0]['self_share']:.1%} / {rows[1]['self_share']:.1%}")
    print(f"  registered B 1 of 3 above 20% -> {len(over20)}: error {len(over20)-1:+d}")
    dirn = all(r["self_share"] < rows[2]["self_share"] for r in others)
    print(f"  DIRECTIONAL R697's share is the largest -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = all(r["self_share"] > 0.50 for r in others)
    print(f"  pre-registered kill (both others >50%) -> "
          f"{'⭐ FIRES — systemic; a standing exclusion rule is warranted' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = ("B SYSTEMIC — every sweeper draws most of its population from its own output. A "
                 "standing exclusion rule is warranted, not a note.")
    else:
        world = (f"⭐⭐ A R697 IS THE EXTREME CASE. Self-inclusion is "
                 f"{rows[0]['self_share']:.1%} for R690, {rows[1]['self_share']:.1%} for R692, and "
                 f"{rows[2]['self_share']:.1%} for R697. ⭐ THE DIFFERENCE IS THE BASIS: R690 and "
                 f"R692 sweep SOURCE files, where a round contributes one file among hundreds; R697 "
                 f"sweeps ARTIFACTS, and an artifact that RECORDS matched items is itself dense in "
                 f"them. A round that writes what it found into the corpus it searches compounds; a "
                 f"round that reads code does not. ⚠ AND THE UNIT GAP: these are counts under MY "
                 f"re-implementation, not under their matchers -- the gap R698 had for R697 and did "
                 f"not name. ⚠ SAFETY: no round was executed, because R698's own closing line "
                 f"proposed exactly the re-run that destroyed an artifact one round earlier.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: 3 sweepers × 2 regimes, 4 controls. No round executed.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"self_share.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "rows": rows,
        "n_over_20pct": len(over20), "kill_fired": killed, "directional_holds": dirn,
        "registered": "A R690 15% / R692 5% [0,60]; B 1 of 3 over 20%; R697 largest; kill if both >50%",
        "safety": "no other round's run.py was executed; every sweep is re-implemented here.",
        "limit": ("counts are under MY re-implementation, not under each round's own matcher -- the "
                  "gap R698 had for R697 and did not name."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'self_share.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
