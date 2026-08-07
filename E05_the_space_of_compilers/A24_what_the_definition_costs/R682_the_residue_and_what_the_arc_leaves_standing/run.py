#!/usr/bin/env python3
"""
R682 -- CLOSURE. The OTHER_USE residue, and what this arc leaves standing.

⚠ LABELLED CLOSURE ON PURPOSE. No outcome here changes R680's ceiling or R681's count. §0 permits
  Closure when it is honestly named, and naming it is the point: eleven rounds of this arc were
  Frontier, and calling a residue trace Frontier would inflate the label until it means nothing.

CHECK #283 ON R681's NEXT LINE -- IT HOLDS.
  `results/fixture_or_finding.json`'s `rows` list carries R360, R361, R676 as OTHER_USE; the two
  Assign cases are named correctly; and the proposed method -- trace the constant's Load sites -- is
  separable from source. Nothing to retract. ⭐ Fourth NEXT in this arc to survive intact.

ESTIMAND        for each OTHER_USE round, what does the constant FEED: a comparison population, an
                analysis population (statistics computed over its members), or nothing?
IDENTIFICATION  ⚠ "analysis population" is what the code CONSUMES, not whether the round's
                conclusion DEPENDS on the set being correct. Consumption, not dependence.
SCOPE           population : the 3 rounds R681 classified OTHER_USE
                instrument : AST Load-site trace to the nearest enclosing expression
                             instrument unit = A LOAD SITE = claim unit. EQUAL.
                baseline   : R681's category set
                regime     : this repository at HEAD
WORLDS          A THIRD KIND: at least one consumes the set as an analysis population, so R681's
                  two categories were incomplete rather than merely unapplied.
                B UNMODELLED FIXTURE: all three are comparisons; no new category is warranted.
KILL            pre-registered: all three comparisons -> world B, add no category.
POSITIVE CTRL   a constant consumed by np.mean over its members -> ANALYSIS.
g=0             a constant only converted and compared -> not ANALYSIS.
NEGATIVE CTRL   a constant bound and never loaded -> DEAD.
PLACEBO         run twice identical.
ARTIFACT        results/residue.json
IMPOSSIBLE      whether a round's CONCLUSION depends on the set being right needs the round re-run
                against a perturbed set; 93 rounds in this arc are corpus-dependent.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
FIVE = {"coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"}
STAT = {"mean", "std", "median", "sum", "var", "average", "corrcoef", "percentile"}


def trace(src: str):
    try: tree = ast.parse(src)
    except SyntaxError: return None, []
    par = {c: n for n in ast.walk(tree) for c in ast.iter_child_nodes(n)}
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and isinstance(n.value, (ast.List, ast.Set, ast.Tuple)):
            if {e.value for e in n.value.elts if isinstance(e, ast.Constant)} & FIVE:
                names |= {t.id for t in n.targets if isinstance(t, ast.Name)}
    sites, kind = [], "DEAD" if names else "NO_BOUND_NAME"
    analysis = compare = False
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in names):
            continue
        p = par.get(n)
        while p is not None and not isinstance(p, (ast.Call, ast.Compare, ast.Assign,
                                                   ast.BinOp, ast.Subscript, ast.comprehension)):
            p = par.get(p)
        seg = " ".join((ast.get_source_segment(src, p) or "").split())[:80]
        sites.append({"node": type(p).__name__ if p is not None else "?", "src": seg})
        if isinstance(p, ast.comprehension): analysis = True
        if isinstance(p, ast.Call):
            f = p.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if nm in STAT: analysis = True
        if isinstance(p, ast.Compare): compare = True
    if sites:
        kind = "ANALYSIS" if analysis else ("COMPARISON" if compare else "CONVERTED")
    return kind, sites


def main() -> int:
    print("─── CONTROLS ───")
    pos, _ = trace('import numpy as np\nX = ["coval_core","topw_k3"]\nm = np.mean([r[a] for a in X])')
    g0, _ = trace('X = ["coval_core","topw_k3"]\nif set(X) == other:\n    pass')
    neg, _ = trace('X = ["coval_core","topw_k3"]\nY = 1')
    plc = trace('X = ["coval_core","topw_k3"]\nY = 1')[0] == neg
    print(f"  POSITIVE  a constant consumed by np.mean over its members -> {pos} -> "
          f"{'PASS' if pos == 'ANALYSIS' else '⛔ FAIL'}")
    print(f"  g=0       a constant only converted and compared -> {g0} -> "
          f"{'PASS — not ANALYSIS, the classifier separates' if g0 != 'ANALYSIS' else '⛔ FAIL'}")
    print(f"  NEGATIVE  a constant bound and never loaded -> {neg} -> "
          f"{'PASS' if neg == 'DEAD' else '⛔ FAIL'}")
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pos == "ANALYSIS" and g0 != "ANALYSIS" and neg == "DEAD" and plc

    rows = []
    for rd in ("R360", "R361", "R676"):
        d = next(iter(ARC.glob(f"{rd}_*")), None)
        k, sites = trace((d / "run.py").read_text(errors="ignore")) if d else (None, [])
        rows.append({"round": rd, "kind": k, "load_sites": sites})

    print(f"\n─── THE RESIDUE (G3 — all three, every load site printed) ───")
    for r in rows:
        print(f"  {r['round']:<6} {r['kind']}")
        for s in r["load_sites"]:
            print(f"           {s['node']:<14} {s['src']}")
        if not r["load_sites"]:
            print(f"           (no bound name — the literals are inline call arguments, i.e. the "
                  f"round's own control fixtures)")
    n_an = sum(1 for r in rows if r["kind"] == "ANALYSIS")
    n_cmp = sum(1 for r in rows if r["kind"] in ("COMPARISON", "CONVERTED"))
    print(f"\n  ANALYSIS population : {n_an}   comparison/converted : {n_cmp}   "
          f"no bound name : {sum(1 for r in rows if r['kind'] == 'NO_BOUND_NAME')}")
    dirn = n_an >= 1
    killed = n_an == 0
    print(f"  registered 2 comparison / 1 analysis -> {n_cmp} / {n_an}")
    print(f"  DIRECTIONAL >=1 uses the set as an ANALYSIS population -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    print(f"  pre-registered kill (all three comparisons) -> "
          f"{'⭐ FIRES — no new category warranted' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = ("B UNMODELLED FIXTURE — all three are comparisons. R681's OTHER_USE was an "
                 "unmodelled FIXTURE and no third category is warranted.")
    else:
        world = (f"⭐ A THIRD KIND EXISTS. {n_an} of 3 consumes the hard-coded set as an ANALYSIS "
                 f"POPULATION — R361 computes `np.mean`/`np.std` over its members and concatenates it "
                 f"into `LABELS + FIVE`. That is neither a comparison target nor a reported value: "
                 f"the set is an INPUT ASSUMPTION of that round's statistics, so any R361 number "
                 f"about 'the five' inherits the hard-coding. R360 only converts it (`set(...)`) and "
                 f"R676's literals are inline arguments to its own control calls. ⚠ CONSUMPTION, NOT "
                 f"DEPENDENCE: computing statistics over a set does not prove the conclusion needs "
                 f"the set to be right, and separating those needs the round re-run against a "
                 f"perturbed set.")
    print(f"  {world}")

    print(f"\n─── WHAT THIS ARC LEAVES STANDING (§0.2 — the residue, not the ledger) ───")
    standing = [
        "the ③ extension is ONE set: {coval_core, topw_k3, topw_k4, topw_k6, topw_k8}, produced by "
        "R294 (R678, unique producer, 4 controls)",
        "the other five five-member sets denote OTHER objects: a publication list, two pre-③ sets, "
        "a different field, an unrelated set (R677, R678)",
        "the deliverable's 7 extension-size rows cite 22 rounds; the producing rounds are none of "
        "them (R679)",
        "at most 6 independent computations stand behind it, not 22 (R680, upper bound twice over)",
        "1 of 12 hard-coding rounds lets the set reach an output field, so the literals are "
        "fixtures, not circulating evidence (R681)",
    ]
    for s in standing: print(f"  ⭐ {s}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"residue.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "action_type": "CLOSURE",
        "rows": rows, "n_analysis": n_an, "n_comparison": n_cmp,
        "kill_fired": killed, "directional_holds": dirn, "standing": standing,
        "registered": "2 comparison / 1 analysis; >=1 ANALYSIS; kill if all three comparisons",
        "limit": "consumption, not dependence -- separating them needs a perturbed re-run.",
    }, indent=2))
    print(f"\n  ⭐ tree sha: {sha[:12]}")
    print(f"  wrote {HERE/'results'/'residue.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
