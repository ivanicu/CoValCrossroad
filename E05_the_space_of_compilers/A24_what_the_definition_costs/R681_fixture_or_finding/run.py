#!/usr/bin/env python3
"""
R681 -- fixture or finding? What the hard-coded set literals are actually DOING.

CHECK #282 ON R680's NEXT LINE -- IT HOLDS.
  `results/n_eff.json`'s `rounds` list carries `literals: 5` for R360, R361 and R676, the citation
  names the field it uses, and the distinction it proposes (assertion vs output field) is separable
  from source. Nothing to retract. ⭐ Third NEXT line in this arc to survive its check intact.

ESTIMAND        for each round carrying the ③-extension members as code literals, does the literal
                reach an OUTPUT field (json.dump / a results dict) or only a COMPARISON (assert, if,
                ==)? Counts of FIXTURE / OUTPUT / BOTH / NEITHER.
IDENTIFICATION  ⚠ UPPER BOUND. Reaching an output field is not the same as being REPORTED AS A
                FINDING -- dumping a fixture for provenance is good practice, not circularity. So
                OUTPUT bounds circular use from above.
SCOPE           population : all 12 rounds R680 found carrying >=1 member literal
                instrument : AST -- literal lists containing members, their bound names, and where
                             those names appear
                             instrument unit = A NAME BOUND TO A MEMBER-BEARING LITERAL
                             claim unit      = A CIRCULAR REPORT
                             ⚠ NOT EQUAL -- hence the bound, carried into the verdict.
                baseline   : R680's literal counts
                regime     : this repository at HEAD
WORLDS          A MOSTLY FIXTURES: the literals are comparison targets; R680's 12 restaters are
                  doing legitimate work and the n_eff bound is unaffected.
                B REPORTED: literals reach output fields, so some artifacts publish a hard-coded set
                  as a result, and any round consuming them inherits it as if measured.
KILL            pre-registered: fewer than half classified -> not identified, no share reported.
POSITIVE CTRL   a literal passed to json.dump -> OUTPUT.
g=0             a literal only compared -> FIXTURE, not OUTPUT; the classifier returns both values.
NEGATIVE CTRL   a literal bound and never used -> NEITHER, not silently OUTPUT.
PLACEBO         run twice identical.
ARTIFACT        results/fixture_or_finding.json
IMPOSSIBLE      whether a dumped value is PRESENTED as a finding is a fact about the prose that
                quotes it, not about the code; separating that needs the reader, not the AST.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
PRIOR = ARC / "R680_citations_are_not_computations" / "results" / "n_eff.json"
FIVE = {"coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"}


def classify(src: str):
    """Names bound to a member-bearing literal, then where those names are used."""
    try: tree = ast.parse(src)
    except SyntaxError: return None
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AnnAssign)):
            val = n.value
            if not isinstance(val, (ast.List, ast.Set, ast.Tuple)): continue
            elts = [e.value for e in val.elts if isinstance(e, ast.Constant)
                    and isinstance(e.value, str)]
            if not (set(elts) & FIVE): continue
            tgts = [n.target] if isinstance(n, ast.AnnAssign) else n.targets
            for t in tgts:
                if isinstance(t, ast.Name): names.add(t.id)
    # a bare literal inside a dump call or a comparison counts too, under a synthetic name
    inline_out = inline_fix = False
    for n in ast.walk(tree):
        lit_here = any(isinstance(e, ast.Constant) and e.value in FIVE
                       for sub in ast.walk(n) for e in [sub])
        if isinstance(n, ast.Call) and lit_here:
            f = n.func
            nm = (f.attr if isinstance(f, ast.Attribute) else
                  (f.id if isinstance(f, ast.Name) else ""))
            if nm in ("dump", "dumps", "write_text"): inline_out = True
        if isinstance(n, (ast.Compare, ast.Assert)) and lit_here: inline_fix = True

    out = inline_out
    fix = inline_fix
    if names:
        for n in ast.walk(tree):
            used = {x.id for x in ast.walk(n) if isinstance(x, ast.Name)} & names
            if not used: continue
            if isinstance(n, ast.Call):
                f = n.func
                nm = (f.attr if isinstance(f, ast.Attribute) else
                      (f.id if isinstance(f, ast.Name) else ""))
                if nm in ("dump", "dumps", "write_text"): out = True
            if isinstance(n, (ast.Compare, ast.Assert)): fix = True
    # ⭐ A FOURTH CATEGORY, ADDED AFTER THE FIRST RUN CALLED THREE ROUNDS "NEITHER" AND I CHECKED.
    #   R676's literals are ARGUMENTS to its own control calls -- jac([...], [...]) -- and R360/R361
    #   bind names used in ways the three categories never enumerated. "NEITHER" was a RESIDUAL
    #   BUCKET wearing a measurement's name, which is ledger 748 exactly, 33 entries later. So:
    #   UNUSED = the literal is genuinely never referenced; OTHER_USE = referenced somewhere this
    #   classifier does not model, and therefore UNVERIFIED as to fixture-vs-finding.
    referenced = False
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id in names and isinstance(n.ctx, ast.Load):
            referenced = True
    lit_as_arg = any(isinstance(n, ast.Call) and any(
        isinstance(a, (ast.List, ast.Set, ast.Tuple)) and
        {e.value for e in a.elts if isinstance(e, ast.Constant)} & FIVE for a in n.args)
        for n in ast.walk(tree))
    if out and fix: return "BOTH"
    if out: return "OUTPUT"
    if fix: return "FIXTURE"
    if referenced or lit_as_arg: return "OTHER_USE"
    return "UNUSED"


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R680's artifact absent. Exit 2, never 0."); return 2
    prior = json.loads(PRIOR.read_text())["rounds"]
    pop = [r["round"] for r in prior if r["literals"] > 0]
    five5 = [r["round"] for r in prior if r["literals"] == 5]

    print("─── CONTROLS ───")
    pos = classify('import json\nX = ["coval_core","topw_k3"]\njson.dump({"e": X}, f)')
    g0 = classify('X = ["coval_core","topw_k3"]\nif got == X:\n    pass')
    neg = classify('X = ["coval_core","topw_k3"]\nY = 1')
    plc = classify('X = ["coval_core","topw_k3"]\nY = 1') == neg
    print(f"  POSITIVE  a literal passed to json.dump -> {pos} -> "
          f"{'PASS' if pos in ('OUTPUT','BOTH') else '⛔ FAIL'}")
    print(f"  g=0       a literal only COMPARED -> {g0} -> "
          f"{'PASS — the classifier returns both values' if g0 == 'FIXTURE' else '⛔ FAIL'}")
    print(f"  NEGATIVE  a literal bound and never used -> {neg} -> "
          f"{'PASS' if neg == 'UNUSED' else '⛔ FAIL — an unused literal reads as reported'}")
    oth = classify('X = ["coval_core","topw_k3"]\nZ = set(X) | other\n')
    print(f"  4th-CAT   a literal used in a way the 3 categories miss -> {oth} -> "
          f"{'PASS — OTHER_USE is separable from UNUSED' if oth == 'OTHER_USE' else '⛔ FAIL'}")
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pos in ("OUTPUT", "BOTH") and g0 == "FIXTURE" and neg == "UNUSED" and plc and oth == "OTHER_USE"

    rows = []
    for rd in pop:
        d = next(iter(ARC.glob(f"{rd}_*")), None)
        if not d or not (d / "run.py").is_file():
            rows.append({"round": rd, "kind": "UNPARSED"}); continue
        k = classify((d / "run.py").read_text(errors="ignore"))
        rows.append({"round": rd, "kind": k or "UNPARSED", "five5": rd in five5})

    from collections import Counter
    c = Counter(r["kind"] for r in rows)
    classified = sum(v for k, v in c.items() if k not in ("UNPARSED", "OTHER_USE"))
    print(f"\n─── WHAT THE LITERALS DO (G3 — every restating round, none sampled) ───")
    for r in sorted(rows, key=lambda r: (r["kind"], r["round"])):
        mark = "  ⭐ 5/5 literal set" if r.get("five5") else ""
        print(f"  {r['round']:<7} {r['kind']}{mark}")
    print(f"\n  population (rounds with >=1 member literal) : {len(pop)}")
    for k in ("OUTPUT", "BOTH", "FIXTURE", "OTHER_USE", "UNUSED", "UNPARSED"):
        if c[k]: print(f"    {k:<9}: {c[k]}")
    reaches = c["OUTPUT"] + c["BOTH"]
    print(f"  ⭐ literal REACHES an output field : {reaches}")
    print(f"  registered A 5 [2,10] -> {reaches}: "
          f"{'INSIDE' if 2 <= reaches <= 10 else '⛔ OUTSIDE'}, error {reaches-5:+d}")
    f5 = sum(1 for r in rows if r.get("five5") and r["kind"] in ("OUTPUT", "BOTH"))
    print(f"  of the three 5/5 rounds, reaching output : {f5}")
    print(f"  registered B 2 [0,3] -> {f5}: "
          f"{'INSIDE' if 0 <= f5 <= 3 else '⛔ OUTSIDE'}, error {f5-2:+d}")
    r676 = next((r for r in rows if r["round"] == "R676"), None)
    dirn = bool(r676 and r676["kind"] in ("OUTPUT", "BOTH"))
    print(f"  DIRECTIONAL R676's literal reaches an output field -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}  (R676 = {r676['kind'] if r676 else 'absent'})")
    killed = classified < len(pop) / 2

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no classification is admissible."
    elif killed:
        world = (f"NOT IDENTIFIED — only {classified} of {len(pop)} classified. No share reported.")
    else:
        world = (f"⭐⭐ {reaches} of {len(pop)} restating rounds let the hard-coded set reach an "
                 f"OUTPUT field; {c['FIXTURE']} use it only as a comparison target, "
                 f"{c['OTHER_USE']} use it in a way this classifier does not model (UNVERIFIED as "
                 f"to fixture-vs-finding, NOT 'unused'), and {c['UNUSED']} never reference it. ⭐ SO THE 12 RESTATERS ARE NOT ONE KIND OF THING — "
                 f"a fixture compared against is legitimate work, and R680's n_eff bound is "
                 f"unaffected by those; the ones that DUMP it publish a hard-coded set into an "
                 f"artifact that a later round can read as if measured, which is exactly the "
                 f"copy-through-a-file channel R680 could not separate. ⚠ UPPER BOUND: dumping a "
                 f"fixture for provenance is good practice, not circularity — whether a dumped value "
                 f"is PRESENTED as a finding is a fact about the prose that quotes it, and no AST "
                 f"reads that.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(pop)} rounds × 1 set, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"fixture_or_finding.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "population": len(pop), "counts": dict(c), "reaches_output": reaches,
        "five5_reaching_output": f5, "rows": rows, "kill_fired": killed,
        "directional_holds": dirn,
        "registered": "A 5 [2,10]; B 2 [0,3]; R676 reaches output; kill if <half classified",
        "upper_bound": ("reaching an output field is not being reported as a finding; dumping a "
                        "fixture for provenance is good practice. OUTPUT bounds circular use."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'fixture_or_finding.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
