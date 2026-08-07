#!/usr/bin/env python3
"""R744 · is NO_ARMS a measurement or silence? — an attack on the round committed before it

ESTIMAND        among the rounds R743 classified NO_ARMS, how many reach the arm store through a
                static path its flat regex cannot see (a local import, or a cache written by a
                round that itself reaches the store).
IDENTIFICATION  PARTIAL -> the answer is a BOUND. Transitive closure only ADDS reach, so it lower-
                bounds the reachers and upper-bounds NO_ARMS. Non-reachability is not establishable
                statically. R650 measured the general resolution question undecidable (172/364 read
                sites resolve); this round asks only the binary the bound can answer.
SCOPE           population = the 16 cited rounds with code, and the 6 NO_ARMS in particular ·
                instrument = ast + repo-local import resolution, depth<=2 · baseline = R743's flat
                detector (L0) · regime = static, at this tree_sha, no execution.
WORLDS          A NO_ARMS is a measurement (L2 adds 0) · B NO_ARMS is silence (L2 adds >=1).
KILL            conditional; gated on POSITIVE firing, PLACEBO exactly zero, and L0==R743.
POSITIVE CTRL   THE ABSENCE DIRECTION R743 never tested: mechanically move R294's store-touching
                lines into a helper module. Flat must go blind on REAL refactored code; L1 must not.
g=0             a helper with no store reference must add NOTHING -- else the detector counts edges.
NEGATIVE CTRL   empty the import graph; L1 and L2 must equal L0 exactly on every round.
SHAM            ingredient ABSENT, not inverted: L1 on cited rounds with zero resolvable imports.
PLACEBO         L0 recomputed twice differs by exactly 0; L1 with an emptied graph equals L0 on 16.
NOISE FLOOR     no rng; the variance is the LEVEL choice -- three levels, all reported.
MULTIPLICITY    3 levels x 3 populations = 9 cells, all printed.
SPECIFICATION   L0/L1/L2 ARE the curve.
UNIT            instrument unit = a source FILE reached; claim unit = a ROUND. They are not equal,
                and that inequality is the finding -- printed as separate columns.
ARTIFACT        results/r744.json with tree_sha; a later round attacks this by executing a round
                under an audit hook, which is the only thing that can beat a static bound.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      proving non-reachability (needs execution tracing, and a runtime path is still
                constructible) · independently replicated (a second team) · cross-site.

⛔ DERIVATION, NOT EVIDENCE: L0 <= L1 <= L2 is forced by construction -- each level is a superset.
   Only the SIZE of the gain is a measurement, and the report says so.
"""
from __future__ import annotations
import ast, json, os, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
sys.path.insert(0, str(ROOT / "assurance"))
import arm_population_is_derived as APD          # the SAME gate R743 used -- L0 must reproduce it

R743 = A24 / "R743_a_derived_population_is_a_timestamp" / "results" / "r743.json"


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


# ---------------------------------------------------------------- reach detectors
def reaches_flat(src: str) -> bool:
    """L0 -- EXACTLY R743's gate: does this source name an arm artifact itself?"""
    return bool(APD.LOADS.search(src))


def local_imports(path: pathlib.Path, src: str):
    """Modules imported by this source that resolve to a file inside this repository.

    ⚠ A round's `sys.path.insert` targets are string literals; we resolve an import name against
    (a) the round's own directory, (b) every literal path inserted into sys.path in this file,
    (c) the repo's lib/ and assurance/ directories. Anything unresolvable is REPORTED, never
    silently dropped -- an unresolved import is exactly where a false NO_ARMS would hide.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return [], ["<unparseable>"]
    names = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names += [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            names.append(n.module.split(".")[0])
    roots = [path.parent, ROOT / "lib", ROOT / "assurance", ROOT,
             A24, ROOT / "corebench"]
    for m in re.findall(r"sys\.path\.\w+\(\s*(?:0\s*,\s*)?str\(([^)]*)\)", src):
        pass  # expression form; the literal roots below cover the realised cases
    for lit in re.findall(r"sys\.path\.\w+\(\s*(?:0\s*,\s*)?[\"']([^\"']+)[\"']", src):
        roots.append((path.parent / lit).resolve())
    found, unresolved = [], []
    for nm in sorted(set(names)):
        hit = None
        for r in roots:
            for cand in (r / f"{nm}.py", r / nm / "__init__.py"):
                if cand.exists() and ROOT in cand.resolve().parents:
                    hit = cand.resolve(); break
            if hit:
                break
        if hit:
            found.append(hit)
        elif nm not in ("ast", "json", "os", "re", "sys", "math", "pathlib", "subprocess",
                        "collections", "itertools", "random", "hashlib", "typing", "csv",
                        "statistics", "functools", "textwrap", "datetime", "time", "glob",
                        "numpy", "np", "scipy", "__future__", "warnings", "dataclasses"):
            unresolved.append(nm)
    return found, unresolved


CACHE_RE = re.compile(r"[\"']([^\"']*\.(?:npz|json))[\"']")


def cache_edges(src: str, tight: bool):
    """L2 -- path literals naming a cache that some ROUND wrote.

    ⛔ THE LOOSE FORM IS AN UNCONTROLLED SEARCH AND IT IS KEPT ONLY TO BE REPORTED AGAINST.
    v1 globbed `R*/results/<basename>` for every `.npz`/`.json` literal. Basenames like
    `results.json` are shared across the tree, so one literal matched 155 round directories and
    every NO_ARMS round "reached" the store through files it never names. That is §4's *a search
    is an instrument* -- and it produced a 6/6 headline. The TIGHT form requires the literal to
    carry a round-directory component (`R###...`), i.e. to name WHICH round's cache it reads.
    Both are computed; the difference between them IS the specification curve for this level.
    """
    out = []
    for lit in CACHE_RE.findall(src):
        p = pathlib.PurePath(lit)
        rounddir = next((part for part in p.parts if re.fullmatch(r"R\d{3}_.*", part)), None)
        if tight:
            if rounddir:
                for hit in A24.glob(f"{rounddir}/results/{p.name}"):
                    out.append(hit.resolve())
        else:
            for hit in A24.glob(f"R*/results/{p.name}"):
                out.append(hit.resolve())
    return sorted(set(out))


def reach(path: pathlib.Path, level: int, graph_on: bool = True, tight: bool = True):
    """-> (reaches, files_examined, unresolved_imports). L0 own file; L1 +imports; L2 +caches."""
    src = path.read_text()
    files = [path.resolve()]
    unres = []
    if level >= 1 and graph_on:
        imps, u = local_imports(path, src)
        unres += u
        files += imps
    if level >= 2 and graph_on:
        for c in cache_edges(src, tight):
            owner = c.parent.parent / "run.py"
            if owner.exists():
                s2 = owner.read_text()
                i2, _ = local_imports(owner, s2)
                if reaches_flat(s2) or any(reaches_flat(p.read_text()) for p in i2
                                           if p.exists()):
                    files.append(owner.resolve())
    files = sorted(set(files))
    hit = any(reaches_flat(p.read_text()) for p in files if p.exists())
    return hit, files, sorted(set(unres))


def run_py(rid: int):
    for d in sorted(A24.glob(f"R{rid:03d}_*")):
        if (d / "run.py").exists():
            return d / "run.py"
    return None


def main() -> int:
    if not R743.exists():
        print("UNRUNNABLE: R743's artifact absent -- there is nothing to attack. Exit 2."); return 2
    prev = json.loads(R743.read_text())
    per = {int(k): v["medium"] for k, v in prev["per_round"].items()}
    cited = sorted(per)
    no_arms = sorted(r for r, c in per.items() if c == "NO_ARMS")
    print("R744 · is NO_ARMS a measurement or silence?\n")
    print(f"R743's cited-with-code population: {len(cited)}   NO_ARMS: {no_arms}")
    if not cited or not no_arms:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # ---- P3, a HARD REQUIREMENT: L0 must reproduce R743 exactly, or this is a different instrument
    l0 = {r: reach(run_py(r), 0)[0] for r in cited}
    agree = sum(1 for r in cited if l0[r] == (per[r] != "NO_ARMS"))
    P3 = (agree == len(cited))
    print(f"P3        L0 reproduces R743's reach/no-reach split: {agree}/{len(cited)}  "
          f"{'PASS' if P3 else 'FAIL -- this is not R743 instrument'}")

    # ---- POSITIVE CONTROL: blindness demonstrated on REAL refactored code
    # ⛔ v1 DELETED the store-touching LINES from R294 and the remainder did not PARSE, so L1 found
    #    no imports and the control failed on ITS OWN construction, not on the detector. §4's
    #    dominant mode again, in the same session. The repair keeps the code REAL and SYNTACTICALLY
    #    VALID: the `sat_` literals are moved into a helper constant and each occurrence in the
    #    round becomes a concatenation with it. The refactor is asserted to PARSE before the
    #    control is allowed to mean anything -- a control that passes on unparseable code is void.
    donor = run_py(294)
    dsrc = donor.read_text()
    hp = HERE / "results" / "_poshelper.py"
    hp.parent.mkdir(exist_ok=True)
    hp.write_text('# generated by run.py for the positive control\nS = "sat_"\n')
    stub = re.sub(r'([\"\'])sat_', r'\1" + _poshelper.S + \1', dsrc)      # literal moves out
    stub = re.sub(r'f([\"\'])" \+ _poshelper\.S \+ \1', r'_poshelper.S + f\1', stub)
    stub_full = "import sys, pathlib\nsys.path.insert(0, str(pathlib.Path(__file__).parent))\n" \
                "import _poshelper\n" + stub
    sp = HERE / "results" / "_posround.py"
    sp.write_text(stub_full)
    try:
        ast.parse(stub_full); parses = True
    except SyntaxError:
        parses = False
    flat_before = reaches_flat(dsrc)
    flat_after = reaches_flat(stub_full)
    l1_after = reach(sp, 1)[0]
    POSITIVE = parses and flat_before and (not flat_after) and l1_after
    print(f"POSITIVE  band computed: floor = flat on untouched R294 = {flat_before}, "
          f"ceiling = L1 on refactored = {l1_after}; refactor parses = {parses}")
    print(f"            flat on REFACTORED source -> {flat_after} (must be False = blind)   "
          f"{'PASS' if POSITIVE else 'FAIL'}")

    # ---- g=0 : an import that carries no store reference must add nothing
    zp = HERE / "results" / "_zerohelper.py"
    zp.write_text("VALUE = 1\n")
    z_round = HERE / "results" / "_zeroround.py"
    z_round.write_text("import _zerohelper\nx = _zerohelper.VALUE\n")
    G0 = (reach(z_round, 1)[0] is False)
    print(f"g=0       importing a store-free helper adds reach: {not G0}  "
          f"{'PASS' if G0 else 'FAIL -- the detector counts EDGES, not data'}")

    # ---- the grid : 3 levels x 3 populations
    pops = {"NO_ARMS(6)": no_arms, "all cited(16)": cited,
            "complement": sorted({int(m.group(1)) for d in A24.glob("R*_*")
                                  if (m := re.match(r"R(\d{3})_", d.name))
                                  and (d / "run.py").exists()} - set(cited))}
    grid, gained, unres_all, files_seen = {}, {}, {}, {}
    LEVELS = [("L0", 0, True), ("L1", 1, True), ("L2 tight", 2, True), ("L2 loose", 2, False)]
    for lname, lv, tight in LEVELS:
        for pname, P in pops.items():
            n = 0
            for r in P:
                p = run_py(r)
                if p is None:
                    continue
                hit, files, u = reach(p, lv, tight=tight)
                n += bool(hit)
                if pname == "NO_ARMS(6)":
                    gained.setdefault(r, {})[lname] = bool(hit)
                    files_seen.setdefault(r, {})[lname] = len(files)
                    if u:
                        unres_all.setdefault(r, sorted(set(unres_all.get(r, []) + u)))
            grid[f"{lname}|{pname}"] = {"reach": n, "n": len(P)}
    print(f"\n  {'level':<11}{'NO_ARMS(6)':>13}{'all cited(16)':>16}{'complement':>14}")
    for lname, _, _ in LEVELS:
        row = f"  {lname:<9}"
        for pname in pops:
            g = grid[f"{lname}|{pname}"]
            row += f"{g['reach']}/{g['n']}".rjust(13 if pname == "NO_ARMS(6)" else
                                                  16 if pname.startswith("all") else 14)
        print(row)
    print("  ⛔ 'L2 loose' is the UNCONTROLLED search kept for contrast: one shared basename "
          "matched 155 round dirs. The tight column is the one that was tested.")
    print("  ⛔ L0 <= L1 <= L2 is FORCED (each level is a superset) -- a DERIVATION. "
          "Only the SIZE of the gain is measured.")

    p1 = grid["L1|NO_ARMS(6)"]["reach"] - grid["L0|NO_ARMS(6)"]["reach"]
    p2 = grid["L2 tight|NO_ARMS(6)"]["reach"] - grid["L0|NO_ARMS(6)"]["reach"]
    p2_loose = grid["L2 loose|NO_ARMS(6)"]["reach"] - grid["L0|NO_ARMS(6)"]["reach"]
    print(f"\nP1        of the 6 NO_ARMS rounds, reach at L1: {p1}  (registered 2, band [0,5])")
    print(f"P2        of the 6 NO_ARMS rounds, reach at L2 TIGHT: {p2}  (registered 3, band [0,6])")
    print(f"            the same at L2 LOOSE, the uncontrolled search: {p2_loose} -- reported so the "
          f"gap between a tested and an untested pattern is legible")
    for r in no_arms:
        g = gained.get(r, {})
        print(f"            R{r:03d}  L0={g.get('L0')} L1={g.get('L1')} L2t={g.get('L2 tight')} "
              f"L2l={g.get('L2 loose')}   files {files_seen.get(r,{}).get('L0')}/"
              f"{files_seen.get(r,{}).get('L1')}/{files_seen.get(r,{}).get('L2 tight')}/"
              f"{files_seen.get(r,{}).get('L2 loose')}"
              + (f"   UNRESOLVED IMPORTS {unres_all[r]}" if r in unres_all else ""))

    # ---- P4 / DIRECTIONAL / SHAM
    edges = {r: len(local_imports(run_py(r), run_py(r).read_text())[0]) for r in cited}
    P4 = sum(1 for v in edges.values() if v)
    no_edge = [r for r in cited if not edges[r]]
    sham_gain = sum(1 for r in no_edge if reach(run_py(r), 1)[0] != reach(run_py(r), 0)[0])
    SHAM = (sham_gain == 0)
    gain_rounds = [r for r in no_arms
                   if gained.get(r, {}).get("L2 tight") and not gained.get(r, {}).get("L0")]
    DIRECTIONAL = all(edges.get(r, 0) > 0 for r in gain_rounds) if gain_rounds else None
    print(f"\nP4        cited rounds with >=1 resolvable local import: {P4}  (registered >=5)")
    print(f"SHAM      ingredient ABSENT -- L1 gain on the {len(no_edge)} import-free cited rounds: "
          f"{sham_gain}  {'PASS' if SHAM else 'FAIL -- L1 is looser for reasons other than imports'}")
    print(f"DIRECTIONAL gaining rounds all carry an import edge: {DIRECTIONAL}  "
          f"(gainers {gain_rounds})")

    # ---- NEGATIVE + PLACEBO
    neg_bad = [r for r in cited
               if reach(run_py(r), 2, graph_on=False)[0] != reach(run_py(r), 0)[0]]
    NEGATIVE = not neg_bad
    twice = all(reaches_flat(run_py(r).read_text()) == l0[r] for r in cited)
    PLACEBO = NEGATIVE and twice
    print(f"NEGATIVE  import graph emptied -> L2 equals L0 on {len(cited)-len(neg_bad)}"
          f"/{len(cited)}  {'PASS' if NEGATIVE else 'FAIL'}")
    print(f"PLACEBO   L0 recomputed differs by exactly 0: {twice}   "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- UNIT : the two units are NOT equal, and that is the finding
    tot_files_l2 = sum(files_seen.get(r, {}).get("L2 tight", 1) for r in no_arms)
    print(f"\nUNIT      instrument unit = source FILE reached ({tot_files_l2} examined across the 6); "
          f"claim unit = ROUND ({len(no_arms)}). NOT equal -- the round claim is the UNION over "
          f"its files, taken before wording.")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM, "P3_is_R743": P3}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire; never OVERTURNED, never CONFIRMED"
    elif p2 == 0:
        world, why = "A", "NO_ARMS is a MEASUREMENT -- transitive closure adds nothing; R743 stands"
    else:
        world, why = "B", ("NO_ARMS is SILENCE -- it is an UPPER BOUND, and R743's sentence must be "
                           "narrowed to a claim about FILES")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R744", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "cited": cited, "no_arms": no_arms,
           "grid": grid, "P1_L1_gain": p1, "P2_L2_tight_gain": p2, "P2_L2_loose_gain": p2_loose,
           "P3_reproduces_R743": P3, "P4_rounds_with_import_edge": P4,
           "per_no_arms_round": {str(k): v for k, v in sorted(gained.items())},
           "files_examined": {str(k): v for k, v in sorted(files_seen.items())},
           "unresolved_imports": {str(k): v for k, v in sorted(unres_all.items())},
           "import_edges": {str(k): v for k, v in sorted(edges.items())},
           "sham_gain_on_import_free": sham_gain, "n_import_free": len(no_edge),
           "directional": DIRECTIONAL, "gainers": gain_rounds,
           "positive_detail": {"refactor_parses": parses, "flat_before": flat_before,
                               "flat_after": flat_after, "l1_after": l1_after},
           "controls": controls,
           "monotonicity_is_a_derivation": True}
    (HERE / "results" / "r744.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r744.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
