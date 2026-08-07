#!/usr/bin/env python3
"""R1080 — is `assurance/valuematch.py` unreachable, or merely unknown?

R1079's committed NEXT: *"a helper that requires a path fiddle to import will be re-implemented
rather than reused, and that is the mechanism this whole line failed on."* That sentence contains a
causal claim about WHY R1047's rounding-aware comparison was re-implemented from scratch by R1070,
and it has never been tested. This round tests it.

ESTIMAND        two quantities, named before any method:
                (Q1) EXECUTED reachability — for a script at directory depth d under the repository,
                     invoked in mode m, does idiom i put `assurance/valuematch.py` on the path so
                     that `import valuematch` succeeds? A boolean per (i, d, m) cell.
                (Q2) ADOPTED idiom — among ROOT-assignment statements in committed round scripts,
                     the count that derive the repository root by LEVEL COUNTING (depth-fragile)
                     versus by LANDMARK SEARCH (depth-robust). Unit: an AST assignment statement,
                     not a round and not a file. Files reported separately.
IDENTIFICATION  Q1 is fully identified: it is executed, not inferred. Q2 is fully identified over
                the syntactic population but is SILENT on semantics -- see WORLDS/C.
SCOPE           population: every `.py` under `E*/` for Q2; a synthesised probe tree for Q1.
                instrument: CPython 3.14 subprocess for Q1; `ast` for Q2. baseline: the `bare`
                idiom (no path work at all). regime: this checkout, PYTHONPATH as inherited.
WORLDS          A MECHANICAL BARRIER  reaching assurance/ needs a fiddle that is absent or fragile,
                                      so re-implementation is the rational act.
                B DISCOVERY BARRIER   reaching it is a solved two-line idiom used at scale; the
                                      re-implementation happened because the helper was unknown.
                C LOCALITY CONVENTION rounds are conventionally self-contained, so shared code is
                                      not reached for even when reachable and known.
                Prediction matrix, executed cells:
                  A -> landmark or parents[3] FAILS at some depth the repo actually contains,
                       and/or assurance/ is imported by ~0 round scripts.
                  B -> both idioms succeed at every real depth AND a landmark idiom is already
                       adopted at scale AND assurance/ already has round-script importers.
                  C -> B's evidence, plus shared-directory imports being COMMON rather than rare
                       (if rounds routinely import corebench/covalx, self-containment is not the
                       convention, and C weakens).
KILL            pre-registered, evaluated ONLY if the control gate below opens:
                  world A is KILLED if (i) `landmark` succeeds in every in-repo depth cell in every
                  invocation mode, and (ii) >= 100 committed ROOT-assignments already use a landmark
                  search, and (iii) >= 1 committed round script already imports from `assurance/`.
                  All three, or A survives. Anything less than all three -> UNVERIFIED, never
                  "A killed".
POSITIVE CTRL   at canonical depth (component count 4, where 1006 of 1007 round scripts sit) the
                `parents3` idiom MUST succeed. If it fails, the probe harness is broken and no cell
                is readable. Retention/MDE: this is a deterministic boolean instrument -- its MDE is
                one cell, and its retention under a maximal plant is reported as the `landmark`
                row. It fails at g=0 by construction: see `nonexistent`.
NEGATIVE CTRL   at a NON-canonical depth `parents3` MUST fail. The structure destroyed is the
                depth assumption, everything else preserved. World it excludes: "the probe is
                insensitive to depth and would print success anywhere".
SHAM            same operation minus the ingredient: the landmark search, looking for a marker
                directory that does not exist. Must fail at every depth. Note it must fail by
                StopIteration, i.e. the search runs and finds nothing -- not by a different error.
PLACEBO         `bare` -- no path work at all. Must return exactly zero successes. A single success
                means something outside this round (PYTHONPATH, a .pth, an installed package) is
                supplying the module and every other cell is uninterpretable.
g=0 GUARD       `nonexistent` -- the correct landmark path, importing a module that is not there.
                Must fail in every cell. This is the check that the probe cannot pass vacuously.
NOISE FLOOR     none: the instrument is deterministic. Measured, not assumed, by running the entire
                grid TWICE and requiring the two result vectors to be byte-identical.
MULTIPLICITY    the whole grid is reported: 6 idioms x 7 depths x 3 invocation modes = 126 cells,
                survivors and non-survivors alike. No correction is applied because no cell is a
                hypothesis test -- each is a deterministic observation, and saying so is the
                honest treatment rather than decorating booleans with a q-value.
SPECIFICATION   axes swept: idiom x depth x invocation mode. The cells that would kill the finding
                are named in advance: any in-repo depth where `landmark` fails.
SEEDS           N/A -- no stochastic component. Substituted: two-run byte-identical reproduction.
ARTIFACT        results/reachable_or_unknown.json, with the source hash of this file.
IMPOSSIBLE      cross-release / cross-site: this measures ONE repository, and a second would be
                required to say anything about the convention in general. Construct validity of
                "why a helper was re-implemented": would require the author's state at the time,
                which is not recoverable -- so B vs C is only PARTIALLY identified here and is
                reported as a bound, never as a point.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "reachable_or_unknown.json"
MARKER = "covalx"                      # the landmark the repo already uses, 243 times
TARGET = "valuematch"                  # the helper whose reachability is the question
PKG = "assurance"


# ----------------------------------------------------------------------------------------------
# Q1 · EXECUTED REACHABILITY
# ----------------------------------------------------------------------------------------------

def probe_source(idiom: str) -> str:
    """the body of a probe script. Each idiom is a real, quotable two-line import preamble."""
    lm = (f'next(p for p in _P(__file__).resolve().parents if (p / "{MARKER}").is_dir())')
    sham_lm = 'next(p for p in _P(__file__).resolve().parents if (p / "NOT_A_REAL_MARKER").is_dir())'
    bodies = {
        # the dominant committed idiom: level counting from a canonical depth
        "parents3": f'import sys\nfrom pathlib import Path as _P\n'
                    f'sys.path.insert(0, str(_P(__file__).resolve().parents[3] / "{PKG}"))\n'
                    f'import {TARGET}\n',
        # the repair already committed at ledger 735: a landmark, not a level
        "landmark": f'import sys\nfrom pathlib import Path as _P\n'
                    f'sys.path.insert(0, str({lm} / "{PKG}"))\n'
                    f'import {TARGET}\n',
        # the alternative remedy: put the ROOT on the path and import the package path
        "namespace": f'import sys\nfrom pathlib import Path as _P\n'
                     f'sys.path.insert(0, str({lm}))\n'
                     f'import {PKG}.{TARGET} as {TARGET}\n',
        # PLACEBO -- no path work at all. Must be zero everywhere.
        "bare": f'import {TARGET}\n',
        # SHAM -- the same search, minus the ingredient (a marker that exists)
        "sham": f'import sys\nfrom pathlib import Path as _P\n'
                f'sys.path.insert(0, str({sham_lm} / "{PKG}"))\n'
                f'import {TARGET}\n',
        # g=0 GUARD -- correct path, absent module. Must be zero everywhere.
        "nonexistent": f'import sys\nfrom pathlib import Path as _P\n'
                       f'sys.path.insert(0, str({lm} / "{PKG}"))\n'
                       f'import {TARGET}_this_module_does_not_exist\n',
    }
    body = bodies[idiom]
    # the probe must prove it imported the REAL helper, not merely that no exception fired:
    # it exercises the one behaviour R1047 established and R1070 lost.
    check = (f'\nassert {TARGET}.matches("0.507", 0.50713), "helper present but wrong behaviour"\n'
             f'print("REACHED", {TARGET}.__file__)\n')
    if idiom == "nonexistent":
        check = '\nprint("REACHED", "impossible")\n'
    return body + check


IDIOMS = ["parents3", "landmark", "namespace", "bare", "sham", "nonexistent"]
ROLE = {"parents3": "committed-dominant", "landmark": "committed-robust",
        "namespace": "candidate-remedy", "bare": "PLACEBO", "sham": "SHAM",
        "nonexistent": "g=0 GUARD"}


def build_probe_tree(base: pathlib.Path, depths: list[int]) -> dict[int, pathlib.Path]:
    """a probe file whose COMPONENT COUNT from the repository root is exactly d.

    component count of `E05_x/A27_y/R1080_z/run.py` is 4 -- the depth 1006 of 1007 round
    scripts sit at, and the depth `parents[3]` is correct for.
    """
    placed = {}
    for d in depths:
        # base is at component count `base_cc`; nest until the file lands at component count d
        base_cc = len(base.relative_to(ROOT).parts)
        need = d - base_cc - 1
        if need < 0:
            raise ValueError(f"cannot place a probe at component count {d} under {base}")
        p = base
        for i in range(need):
            p = p / f"d{i}"
        p.mkdir(parents=True, exist_ok=True)
        placed[d] = p / "probe.py"
    return placed


def run_cell(script: pathlib.Path, mode: str, scratch: pathlib.Path) -> dict:
    """three invocation modes, because sys.path[0] is a claim about the invocation, not the file."""
    if mode == "abs_from_root":
        cwd, arg = ROOT, str(script)
    elif mode == "rel_from_own_dir":
        cwd, arg = script.parent, script.name
    elif mode == "abs_from_far":
        cwd, arg = scratch, str(script)
    else:
        raise ValueError(mode)
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)          # recorded below; removed so the placebo is interpretable
    try:
        r = subprocess.run([sys.executable, arg], cwd=str(cwd), env=env,
                           capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"ok": False, "err": "TIMEOUT"}
    ok = r.returncode == 0 and "REACHED" in r.stdout
    err = ""
    if not ok:
        tail = [l for l in r.stderr.strip().splitlines() if l.strip()]
        err = tail[-1][:120] if tail else f"rc={r.returncode}"
    return {"ok": ok, "err": err}


def marker_confound() -> dict:
    """⚠ STRONGEST CONFOUND, written before the verdict was read and controlled in this iteration.

    `landmark` succeeded at every depth in a probe tree that contains no intervening marker. A real
    round sitting beneath a directory that has its own `covalx/` child would stop the upward search
    early and resolve to the WRONG root -- depth-robust but ambiguous. Two parts:
      (a) OBSERVED   every directory in this checkout that has a `covalx` child. >1 == live risk.
      (b) SENSITIVITY plant a decoy marker above a probe and require the landmark to resolve to the
                      DECOY, not the repository root. If it still finds the real root, the search is
                      not doing what its name says and (a) would not have detected anything.
    """
    holders = sorted(str(p.relative_to(ROOT)) or "." for p in ROOT.rglob("*")
                     if p.is_dir() and p.name == MARKER and p.parent != p)
    holders = sorted({str(pathlib.Path(h).parent) for h in holders})
    tmp = ROOT / "_r1080_decoy_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    resolved = None
    try:
        decoy = tmp / "decoy_root"
        (decoy / MARKER).mkdir(parents=True)
        (decoy / PKG).mkdir(parents=True)            # a DIFFERENT assurance/, without the helper
        probe = decoy / "a" / "b" / "probe.py"
        probe.parent.mkdir(parents=True)
        probe.write_text(
            'import sys\nfrom pathlib import Path as _P\n'
            f'r = next(p for p in _P(__file__).resolve().parents if (p / "{MARKER}").is_dir())\n'
            'print("RESOLVED", r)\n')
        env = dict(os.environ); env.pop("PYTHONPATH", None)
        r = subprocess.run([sys.executable, str(probe)], cwd=str(ROOT), env=env,
                           capture_output=True, text=True, timeout=60)
        resolved = r.stdout.strip().split(" ", 1)[-1] if r.returncode == 0 else f"ERR {r.stderr[-80:]}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    stops_at_decoy = bool(resolved and resolved.endswith("decoy_root"))
    return {"dirs_holding_a_marker": holders, "marker_is_unique": len(holders) == 1,
            "decoy_resolution": resolved, "search_stops_at_nearest_marker": stops_at_decoy}


def sweep(depths: list[int], modes: list[str]) -> list[dict]:
    cells = []
    tmp_root = ROOT / "_r1080_probe_tmp"
    scratch = pathlib.Path(tempfile.mkdtemp(prefix="r1080_far_"))
    off_tree = pathlib.Path(tempfile.mkdtemp(prefix="r1080_offtree_"))
    try:
        if tmp_root.exists():
            shutil.rmtree(tmp_root)
        tmp_root.mkdir()
        placed = build_probe_tree(tmp_root, depths)
        placed[-1] = off_tree / "probe.py"       # -1 == OFF-TREE: no repository above it at all
        for idiom in IDIOMS:
            src = probe_source(idiom)
            for d, path in sorted(placed.items()):
                path.write_text(src)
                for mode in modes:
                    r = run_cell(path, mode, scratch)
                    cells.append({"idiom": idiom, "role": ROLE[idiom], "depth": d,
                                  "mode": mode, **r})
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
        shutil.rmtree(scratch, ignore_errors=True)
        shutil.rmtree(off_tree, ignore_errors=True)
    return cells


# ----------------------------------------------------------------------------------------------
# Q2 · ADOPTED IDIOM -- by AST, because R1077 measured that a text scan counts MENTIONS as USES
# ----------------------------------------------------------------------------------------------

def classify_root_expr(node: ast.AST) -> str:
    """how does this expression derive a directory: by counting levels, or by finding a landmark?

    ⛔ REPAIR, and the control caught it. The first implementation matched substrings of
       `ast.dump()` -- `"Call(func=Name(id='next')"` -- which never fires, because `ast.dump`
       emits `Name(id='next', ctx=Load())`. It labelled all 243 committed landmark searches
       `other` and its POSITIVE control said so before any verdict was read. Matching a
       serialisation of a tree is a TEXT SCAN wearing an AST's clothes; this walks the tree.
    """
    nodes = list(ast.walk(node))
    # LANDMARK: a search over `.parents` that stops at a directory test -- level-independent
    over_parents = any(isinstance(n, (ast.GeneratorExp, ast.ListComp))
                       and any(isinstance(g.iter, ast.Attribute) and g.iter.attr == "parents"
                               for g in n.generators)
                       for n in nodes)
    tests_dir = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr in ("is_dir", "exists", "is_file") for n in nodes)
    if over_parents and tests_dir:
        return "landmark"
    # LEVEL COUNTED: `.parents[k]` or a `.parent` chain -- correct only at one depth
    subscripted_parents = any(isinstance(n, ast.Subscript) and isinstance(n.value, ast.Attribute)
                              and n.value.attr == "parents" for n in nodes)
    parent_chain = any(isinstance(n, ast.Attribute) and n.attr == "parent" for n in nodes)
    if subscripted_parents or parent_chain:
        return "level_counted"
    return "other"


def census() -> dict:
    per_class: dict[str, int] = {}
    files_per_class: dict[str, set] = {}
    unparsable = 0
    scanned = 0
    for p in sorted(ROOT.glob("E*/**/*.py")):
        try:
            tree = ast.parse(p.read_text(errors="replace"))
        except SyntaxError:
            unparsable += 1
            continue
        scanned += 1
        for n in ast.walk(tree):
            if not isinstance(n, ast.Assign):
                continue
            names = [t.id for t in n.targets if isinstance(t, ast.Name)]
            if not any(nm.lstrip("_") == "ROOT" for nm in names):
                continue
            c = classify_root_expr(n.value)
            per_class[c] = per_class.get(c, 0) + 1
            files_per_class.setdefault(c, set()).add(str(p.relative_to(ROOT)))
    allfiles = set().union(*files_per_class.values()) if files_per_class else set()
    return {"statements": per_class,
            "files": {k: len(v) for k, v in files_per_class.items()},
            "distinct_files_with_any_root_assignment": len(allfiles),
            "statements_total": sum(per_class.values()),
            "files_scanned": scanned, "unparsable": unparsable}


def census_second_instrument() -> int:
    """⭐ A CROSS-CHECK, not a control. A line-oriented count of the same population by a method
    that shares none of the AST classifier's machinery. It cannot validate the CLASSES -- only the
    POPULATION -- and the two must agree on the statement total or one of them is reading a
    different object. Sound direction: a top-level `ROOT =` line IS an assignment statement; the
    converse fails for continuations, so this is a LOWER bound on the AST count and equality is
    the informative outcome."""
    import re
    pat = re.compile(r"^\s*_?ROOT\s*=")
    n = 0
    for p in sorted(ROOT.glob("E*/**/*.py")):
        n += sum(1 for line in p.read_text(errors="replace").splitlines() if pat.match(line))
    return n


def valuematch_adoption() -> dict:
    """who actually reaches the helper, by mechanism -- static import vs dynamic vs prose only.

    ⛔ NO SYNTACTIC CLASSIFICATION OF INTENT. R1076/R1078/R1079 each tried to recover a semantic
       category from syntax and each failed a control. This counts three MECHANICALLY DISTINCT and
       non-overlapping things and names them; it does not ask what any file meant to do.
    """
    static, dynamic, prose_only = [], [], []
    for p in sorted(ROOT.glob("E*/**/*.py")):
        txt = p.read_text(errors="replace")
        if TARGET not in txt:
            continue
        rel = str(p.relative_to(ROOT))
        try:
            tree = ast.parse(txt)
        except SyntaxError:
            continue
        is_static = any(
            (isinstance(n, ast.Import) and any(a.name.split(".")[-1] == TARGET for a in n.names))
            or (isinstance(n, ast.ImportFrom) and n.module
                and n.module.split(".")[-1] == TARGET)
            for n in ast.walk(tree))
        is_dynamic = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "import_module"
            and any(isinstance(a, ast.Constant) and a.value == TARGET for a in n.args)
            for n in ast.walk(tree))
        (static if is_static else dynamic if is_dynamic else prose_only).append(rel)
    return {"static_import": static, "dynamic_import": dynamic, "names_it_only": prose_only}


def importers_of(pkgdir: str) -> dict:
    """round scripts that already reach into a shared directory -- by AST, not by grep."""
    hits, target_hits = [], []
    for p in sorted(ROOT.glob("E*/**/*.py")):
        try:
            txt = p.read_text(errors="replace")
            tree = ast.parse(txt)
        except SyntaxError:
            continue
        # a path insert naming the directory, anywhere in the file's real code
        inserts = False
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value == pkgdir:
                inserts = True
        imports = {a.name.split(".")[0] for n in ast.walk(tree)
                   if isinstance(n, ast.Import) for a in n.names}
        imports |= {n.module.split(".")[0] for n in ast.walk(tree)
                    if isinstance(n, ast.ImportFrom) and n.module}
        if inserts:
            hits.append(str(p.relative_to(ROOT)))
        if TARGET in imports:
            target_hits.append(str(p.relative_to(ROOT)))
    return {"files_naming_dir": hits, "files_importing_target": target_hits}


def census_controls() -> dict:
    """the classifier is an instrument. Plant known cases; require the labels."""
    def cls(src):
        m = ast.parse(src)
        return classify_root_expr(m.body[0].value)
    pos_level = cls("ROOT = pathlib.Path(__file__).resolve().parents[3]")
    pos_level2 = cls("ROOT = HERE.parent.parent.parent")
    pos_land = cls('ROOT = next(p for p in pathlib.Path(__file__).resolve().parents '
                   'if (p / "covalx").is_dir())')
    neg_other = cls('ROOT = pathlib.Path(".")')
    # DISCRIMINATION: a `next()` over `.parents` with NO directory test is not a landmark search
    neg_nodir = cls("ROOT = next(p for p in pathlib.Path(__file__).parents if p.name == 'x')")
    # REGRESSION: the exact committed form the first classifier missed, verbatim from the repo
    reg = cls('_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())')
    # g=0: a file that only MENTIONS the words in a comment and a string must contribute nothing
    g0 = ast.parse('# ROOT = pathlib.Path(__file__).resolve().parents[3]\n'
                   'x = "ROOT = HERE.parent.parent"\n')
    g0_rows = sum(1 for n in ast.walk(g0) if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id.lstrip("_") == "ROOT"
                          for t in n.targets))
    return {
        "POSITIVE level-counted subscript labelled level_counted": pos_level == "level_counted",
        "POSITIVE .parent chain labelled level_counted": pos_level2 == "level_counted",
        "POSITIVE landmark search labelled landmark": pos_land == "landmark",
        "NEGATIVE a constant path is neither": neg_other == "other",
        "NEGATIVE a parents-search with no dir test is NOT a landmark": neg_nodir != "landmark",
        "REGRESSION the committed landmark form, verbatim": reg == "landmark",
        "g=0 a comment and a string contribute no rows": g0_rows == 0,
    }


# ----------------------------------------------------------------------------------------------

def main() -> int:
    depths = [2, 3, 4, 5, 6, 8]
    modes = ["abs_from_root", "rel_from_own_dir", "abs_from_far"]

    run1 = sweep(depths, modes)
    run2 = sweep(depths, modes)
    key = lambda cs: [(c["idiom"], c["depth"], c["mode"], c["ok"]) for c in cs]
    reproducible = key(run1) == key(run2)

    cen = census()
    cc = census_controls()
    cen2 = census_second_instrument()
    cen["second_instrument_lines"] = cen2
    cen["instruments_agree"] = (cen2 == cen["statements_total"])
    imp = importers_of(PKG)
    imp_corebench = importers_of("corebench")
    adopt = valuematch_adoption()
    conf = marker_confound()
    rounds_since = sorted(int(m.group(1)) for m in
                          (__import__("re").match(r"R(\d+)_", d.name)
                           for d in ROOT.glob("E*/A*/R*") if d.is_dir()) if m)
    rounds_after_1076 = [r for r in rounds_since if r > 1076]

    grid = {}
    for c in run1:
        grid.setdefault(c["idiom"], {})[(c["depth"], c["mode"])] = c["ok"]

    def all_ok(idiom, ds):
        return all(grid[idiom][(d, m)] for d in ds for m in modes)

    def none_ok(idiom):
        return not any(grid[idiom].values())

    in_repo = [d for d in depths]
    CANON = 4

    # ---- controls, read BEFORE the verdict, and the verdict branch references every one ----
    pos = all(grid["parents3"][(CANON, m)] for m in modes)
    neg = not any(grid["parents3"][(d, m)] for d in in_repo if d != CANON for m in modes)
    placebo = none_ok("bare")
    sham = none_ok("sham")
    g0 = none_ok("nonexistent")
    census_ok = all(cc.values())
    # k2 rests on the census population; a second instrument must agree on it before k2 is read
    cross = cen["instruments_agree"]
    gate_open = pos and neg and placebo and sham and g0 and census_ok and reproducible and cross

    # ---- the three KILL conditions, each computed, none typed ----
    # k1 is conditioned on the confound: an ambiguous marker would make "reaches" mean "reaches
    # SOMETHING", and the sensitivity plant is what shows the search can be misled at all.
    k1 = (all_ok("landmark", in_repo) and conf["marker_is_unique"]
          and conf["search_stops_at_nearest_marker"])
    k2 = cen["statements"].get("landmark", 0) >= 100
    k3 = len(imp["files_naming_dir"]) >= 1
    a_killed = bool(k1 and k2 and k3)

    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so no cell licenses a claim about either world. "
                   "A kill that can fire on a broken instrument is not a commitment.")
    elif a_killed:
        verdict = ("world A (MECHANICAL BARRIER) is KILLED — the landmark idiom reaches the helper "
                   "from every depth this repository contains, it is already adopted at scale, and "
                   f"{len(imp['files_naming_dir'])} committed round script(s) already reach into "
                   f"{PKG}/. The re-implementation was not caused by unreachability.")
    else:
        verdict = ("world A SURVIVES — " + "; ".join(
            n for n, v in [("landmark fails at some in-repo depth", not k1),
                           ("landmark not adopted at scale", not k2),
                           (f"no committed round script reaches {PKG}/", not k3)] if v))

    off = [c for c in run1 if c["depth"] == -1]
    boundary = {i: all(c["ok"] for c in off if c["idiom"] == i) for i in IDIOMS}

    art = {
        "round": "R1080",
        "question": "is assurance/valuematch.py unreachable, or merely unknown?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "pythonpath_inherited": os.environ.get("PYTHONPATH", ""),
        "grid": {"idioms": IDIOMS, "depths": depths + [-1], "modes": modes,
                 "cells_tested": len(run1),
                 "cells_reaching": sum(1 for c in run1 if c["ok"]),
                 "canonical_depth": CANON},
        "cells": run1,
        "controls": {
            "POSITIVE parents3 succeeds at canonical depth 4, all modes": pos,
            "NEGATIVE parents3 fails at every non-canonical in-repo depth": neg,
            "PLACEBO bare import succeeds nowhere": placebo,
            "SHAM landmark for an absent marker succeeds nowhere": sham,
            "g=0 correct path + absent module succeeds nowhere": g0,
            "census classifier controls": cc,
            "two-run byte-identical grid": reproducible,
            "CROSS-INSTRUMENT census statement total agrees with a line scan": cross,
        },
        "kill": {"k1_landmark_reaches_every_in_repo_depth": k1,
                 "k2_landmark_statements_ge_100": k2,
                 "k3_a_round_script_already_reaches_assurance": k3,
                 "gate_open": gate_open, "world_A_killed": a_killed},
        "census_Q2": cen,
        "importers": {"assurance": {"files_naming_dir": len(imp["files_naming_dir"]),
                                    "files_importing_valuematch": imp["files_importing_target"]},
                      "corebench_files_naming_dir": len(imp_corebench["files_naming_dir"])},
        "adoption_Q3": {
            "static_import": adopt["static_import"],
            "dynamic_import": adopt["dynamic_import"],
            "names_it_only": adopt["names_it_only"],
            "rounds_committed_after_R1076": len(rounds_after_1076),
            "note": ("adoption is measured by MECHANISM, not by intent. Whether any of these "
                     "rounds HAD an occasion to use it is a semantic question and R1076/78/79 "
                     "measured that this repository's semantic questions do not survive syntactic "
                     "classification. It is left UNRESOLVED here, with the discriminator named in "
                     "the README."),
        },
        "off_tree_boundary": boundary,
        "strongest_confound": conf,
        "derivations_not_measurements": [
            "the `parents3` row is FORCED: parents[3] of a file at component count d lands at "
            "component count d-3, which equals the repository root only at d=4. The row was "
            "executed, but it could not have come out otherwise. It is reported as the NEGATIVE "
            "control's evidence, not as a finding.",
            "the `bare` and `nonexistent` rows are forced given an empty PYTHONPATH and no "
            "installed package; they are recorded because the assumption (empty PYTHONPATH) is "
            "the thing being asserted, and it is checked rather than assumed.",
        ],
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    # ------------------------------------------- report -------------------------------------
    print("R1080 — is the helper unreachable, or merely unknown?\n")
    print("  CONTROLS (read before the verdict; the branch below references every one)")
    for k, v in art["controls"].items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(f"    {'PASS' if vv else '⛔ FAIL'}  census · {kk}")
        else:
            print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  GRID — {len(IDIOMS)} idioms × {len(depths)+1} depths × {len(modes)} modes = "
          f"{len(run1)} cells · {sum(1 for c in run1 if c['ok'])} reach the helper")
    print(f"    {'idiom':<12}{'role':<20}" + "".join(f"{('d'+str(d)) if d>0 else 'off-tree':>10}"
                                                     for d in depths + [-1]))
    for i in IDIOMS:
        row = "".join(f"{sum(grid[i][(d,m)] for m in modes)}/{len(modes):<9}"
                      for d in depths + [-1])
        print(f"    {i:<12}{ROLE[i]:<20}{row}")
    print("\n  Q2 · ADOPTED IDIOM — unit: an AST ROOT-assignment STATEMENT, not a round")
    for k in sorted(cen["statements"], key=lambda k: -cen["statements"][k]):
        print(f"    {k:<16}{cen['statements'][k]:>6} statements   "
              f"{cen['files'][k]:>5} files")
    print(f"    files scanned {cen['files_scanned']}   unparsable {cen['unparsable']}   "
          f"distinct files with a ROOT assignment {cen['distinct_files_with_any_root_assignment']}")
    print(f"    cross-instrument: AST {cen['statements_total']} statements vs line scan "
          f"{cen['second_instrument_lines']} lines — {'AGREE' if cross else '⛔ DISAGREE'}")
    print(f"\n  reach into {PKG}/ : {len(imp['files_naming_dir'])} files   "
          f"reach into corebench/ : {len(imp_corebench['files_naming_dir'])} files")
    print(f"\n  Q3 · ADOPTION OF THE HELPER — by mechanism, {len(rounds_after_1076)} rounds "
          f"committed since R1076 shipped it")
    print(f"    static  `import {TARGET}`          : {len(adopt['static_import'])}  "
          f"{[x.split('/')[-2] for x in adopt['static_import']]}")
    print(f"    dynamic `import_module(\"{TARGET}\")`: {len(adopt['dynamic_import'])}  "
          f"{[x.split('/')[-2] for x in adopt['dynamic_import']]}")
    print(f"    names it in prose only            : {len(adopt['names_it_only'])}  "
          f"{[x.split('/')[-2] for x in adopt['names_it_only']]}")
    print(f"\n  STRONGEST CONFOUND — an ambiguous marker would make 'reaches' mean 'reaches "
          f"something'")
    print(f"    directories holding a `{MARKER}` child: {len(conf['dirs_holding_a_marker'])} "
          f"{conf['dirs_holding_a_marker']}   unique={conf['marker_is_unique']}")
    print(f"    SENSITIVITY a planted decoy marker must capture the search: "
          f"{conf['search_stops_at_nearest_marker']}  -> {conf['decoy_resolution']}")
    print(f"\n  KILL  k1={k1}  k2={k2}  k3={k3}  gate_open={gate_open}")
    print(f"\n  {'⭐' if a_killed else '⛔'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
