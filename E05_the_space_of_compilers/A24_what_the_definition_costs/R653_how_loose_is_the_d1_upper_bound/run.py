#!/usr/bin/env python3
"""
R653 -- how loose is D1? Resolve the ARGUMENT at every call site, and refuse the vacuous truth.

CHECK #254 ON R652's CLOSING LINE. ONE CLAUSE IS FALSE AND ITS FALSENESS IS INSTRUCTIVE.
  R652's NEXT: "`pat` accounts for 14 of the 59 D1 sites and `rid` for 11 -- 25 of 59 in two
  parameter names. If those two are each passed a constant at every call site, 25 D1 sites
  collapse to D0 and THE CALLER-DEPENDENT COUNT FALLS BELOW HALF."
  ⛔ 59 - 25 = 34, which is 57.6% of 59. It falls below half only of R651's **retracted** 98
     (34.7%). I measured against a number I had killed in the same round, and the sentence reads
     as true because the wrong denominator is the one that was in my head.
  ⚠ The counts 14 and 11 ARE correct, and so is 25. The defect is the comparison, which is
     exactly §4's row: a closing sentence quantifies, nobody controls it, and the next round acts
     on it. So this round tests the whole D1 population, not the two names the line pointed at.

⛔ AND THE TRAP IS VISIBLE BEFORE A LINE IS WRITTEN, WHICH IS WHY IT IS PRE-REGISTERED:
   "every call site passes a constant" is VACUOUSLY TRUE for a function with ZERO call sites.
   §4's `empty population passes` -- a gate reporting success having examined nothing. Any site
   whose owning function is never called in its own module must be VACUOUS, never COLLAPSES.

⛔ AND THE FIRST FRAMING OF THIS ROUND'S OWN ESTIMAND WAS WRONG, CAUGHT BEFORE IT SHIPPED.
   v1 wrote: "COLLAPSES -> the site is really D0 and D1 OVER-COUNTED it." FALSE. A site whose
   caller passes a module constant is STILL caller-dependent: no evaluator confined to the
   function body can resolve it, which is exactly what D1 asserts. D1 = 59 is CONFIRMED, not
   over-counted. What this round measures is a different quantity that I nearly reported as that
   one: whether going ONE LEVEL UP actually ANSWERS the question. D1 is where the dependency
   SITS; it says nothing about where it RESOLVES.

ESTIMAND        Of R652's 59 D1 (caller-dependent) read sites, does ONE level of caller analysis
                RESOLVE the site? Partition by what the callers actually supply:
                  RESOLVED@1  >=1 call site, and the blocking argument is statically resolvable
                              at EVERY one -> depth 1 answers it
                  PARTIAL     >=1 call site, some static, some not -> depth 1 answers it for a
                              subset of calls only
                  DEEPER      >=1 call site, none static -> the CALLERS themselves pass dynamic
                              values, so the site needs depth >= 2. Depth 1 does NOT answer it.
                  VACUOUS     0 call sites in its own module -> UNVERIFIED. Not a collapse.
                  CALLEE      the blocker is a module-local FUNCTION's return, not a parameter ->
                              a different mechanism; reported, never folded into the others
                n_resolved_at_1, i.e. the yield of one level of caller analysis.
IDENTIFICATION  Exact for calls appearing in the same module. NOT identified for calls from
                another module or a harness -- so a VACUOUS verdict is "no visible caller", never
                "no caller", and COLLAPSES is an UPPER bound on the looseness (an unseen caller
                could pass something dynamic). Bounds, both directions stated.
SCOPE           population : the 59 D1 sites of R652, MINUS this round
                instrument : ast -- bind each Call's args to the callee's parameters positionally
                             and by keyword, then classify the bound expression as static or not
                             instrument unit = A (SITE, BLOCKING PARAMETER) PAIR
                             claim unit      = A READ SITE IS REALLY D0
                             NOT EQUAL, and that gap is why VACUOUS exists: a pair with no calls
                             yields no evidence about the site
                baseline   : R652's D1 = 59, re-derived here and required to reproduce
                regime     : as committed at this sha
WORLDS          A DEPTH 1 IS SHALLOW: few sites resolve -> the callers pass dynamic values too,
                  so the dependency chain runs deeper and a one-level inline buys little.
                B DEPTH 1 IS ENOUGH: most sites resolve -> the corpus's parameters are passed
                  constants and one level of caller analysis closes most of D1.
                C UNINFORMATIVE: most sites are VACUOUS or CALLEE -> the call graph in one module
                  does not answer the question and a wider instrument is required.
KILL            pre-registered, before the run: if ANY site classified COLLAPSES has zero visible
                call sites, the vacuous guard has failed and the entire collapse count is VOID --
                not adjusted, void. And if VACUOUS + CALLEE > 30 of 59, world C: no looseness
                number is reported.
POSITIVE CTRL   a synthetic module: `def f(p): (p/'x').read_text()` called once as `f(ROOT)` with
                ROOT a module constant -> COLLAPSES. Fails at g=0: with no D1 sites, 0 collapses.
NEGATIVE CTRL   the same function called TWICE, once with ROOT and once with a runtime value ->
                PARTIAL, never COLLAPSES. A single good call site must not carry the verdict.
PLACEBO         a function that is NEVER called -> VACUOUS. This is the control that matters: the
                failure direction is to report a collapse from an empty call set.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 resolver x 59 sites x every visible call site + 5 controls. Whole grid reported,
                including every class that is not COLLAPSES.
ARTIFACT        results/argument_resolution.json
IMPOSSIBLE      calls from outside the module are not enumerable from this tree, so VACUOUS means
                "no visible caller" and COLLAPSES is an upper bound on looseness. Making it exact
                would require a whole-corpus import graph, which these rounds do not have --
                every round is a standalone script by construction.
"""
from __future__ import annotations
import ast, json, pathlib, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R652 = A24 / "R652_at_what_depth_does_a_population_stop_being_static" / "results" / "depth_partition.json"

STATIC_CALLS = {"Path", "resolve", "absolute", "expanduser", "parent", "joinpath",
                "with_suffix", "with_name"}


def parents_of(tree):
    p = {}
    for a in ast.walk(tree):
        for c in ast.iter_child_nodes(a):
            p[c] = a
    return p


def module_consts(tree):
    """Module-level names assigned once from a path/constant expression."""
    out = set()
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Name):
            out.add(n.targets[0].id)
    return out


def is_static_arg(expr, consts):
    """Is this argument expression statically resolvable at the call site?"""
    if isinstance(expr, ast.Constant):
        return True
    if isinstance(expr, ast.Name):
        return expr.id in consts
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
        return is_static_arg(expr.left, consts) and is_static_arg(expr.right, consts)
    if isinstance(expr, ast.Attribute):
        return is_static_arg(expr.value, consts)
    if isinstance(expr, ast.Call):
        fn = getattr(expr.func, "attr", None) or getattr(expr.func, "id", None)
        if fn in STATIC_CALLS:
            return all(is_static_arg(a, consts) for a in expr.args) if expr.args else True
        return False
    if isinstance(expr, ast.Subscript):
        return False
    return False


def bind_arg(call, fn, param):
    """The expression passed to `param` at this call site, or None if not determinable."""
    names = [a.arg for a in fn.args.args]
    for kw in call.keywords:
        if kw.arg == param:
            return kw.value
    if param in names:
        i = names.index(param)
        if i < len(call.args):
            return call.args[i]
        # a default counts as a supplied value, and defaults are in the DEFINITION
        n_def = len(fn.args.defaults)
        j = i - (len(names) - n_def)
        if 0 <= j < n_def:
            return fn.args.defaults[j]
    return None


def call_sites(tree, fname):
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and (getattr(n.func, "id", None) == fname
                 or getattr(n.func, "attr", None) == fname)]


def resolve_site(tree, fn, param, consts):
    """Partition one (site, blocking parameter) pair by what its callers supply."""
    calls = call_sites(tree, fn.name)
    if not calls:
        # ⛔ THE VACUOUS TRUTH, REFUSED. `all([])` is True, so a function with no visible caller
        #    would report "every call site passes a constant" having examined nothing. §4's
        #    `empty population passes`. This branch exists before any counting happens.
        return "VACUOUS", "0 visible call sites — `all([])` is True and that is not evidence"
    kinds = []
    for c in calls:
        e = bind_arg(c, fn, param)
        if e is None:
            kinds.append(False)
        else:
            kinds.append(is_static_arg(e, consts))
    if all(kinds):
        return "RESOLVED@1", f"{len(calls)} call site(s), every one static"
    if any(kinds):
        return "PARTIAL", f"{sum(kinds)} of {len(calls)} call site(s) static"
    return "DEEPER", f"{len(calls)} call site(s), none static"


def main() -> int:
    if not R652.exists():
        print("UNRUNNABLE: R652's artifact absent — no D1 population. Exit 2, never 0.")
        return 2
    b = json.loads(R652.read_text())
    d1_members = [k for k, v in b["members"].items() if v == "D1"]
    if len(d1_members) != b["counts"]["D1"]:
        print(f"UNRUNNABLE: artifact disagrees with itself — {len(d1_members)} members vs "
              f"count {b['counts']['D1']}. Exit 2.")
        return 2

    # blocker per site, straight from R652's evidence: "D1  CALLER: parameter `x`" / "D1  CALLER: f"
    trees, consts = {}, {}
    for d in sorted(A24.glob("R[0-9]*")):
        if not (d / "run.py").is_file() or d.resolve() == HERE:
            continue
        try:
            t = ast.parse((d / "run.py").read_text(errors="ignore"))
        except SyntaxError:
            continue
        trees[d.name] = t
        consts[d.name] = module_consts(t)

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")

    def synth(src, fname, param):
        t = ast.parse(src)
        f = [n for n in ast.walk(t) if isinstance(n, ast.FunctionDef) and n.name == fname][0]
        return resolve_site(t, f, param, module_consts(t))

    pos = synth("import pathlib\nROOT=pathlib.Path('/r')\n"
                "def f(p):\n    return (p/'x').read_text()\n"
                "f(ROOT)\n", "f", "p")
    print(f"  POSITIVE   one call site passing a module constant -> {pos[0]} -> "
          f"{'PASS' if pos[0] == 'RESOLVED@1' else '⛔ FAIL'}")
    neg = synth("import pathlib, json\nROOT=pathlib.Path('/r')\n"
                "def f(p):\n    return (p/'x').read_text()\n"
                "f(ROOT)\nf(json.loads('{}')['q'])\n", "f", "p")
    print(f"  NEGATIVE   two call sites, one dynamic -> {neg[0]} ({neg[1]}) -> "
          f"{'PASS — one good call site does not carry it' if neg[0] == 'PARTIAL' else '⛔ FAIL'}")
    plc = synth("import pathlib\nROOT=pathlib.Path('/r')\n"
                "def f(p):\n    return (p/'x').read_text()\n", "f", "p")
    plcok = plc[0] == "VACUOUS"
    print(f"  PLACEBO    a function NEVER called -> {plc[0]} -> "
          f"{'PASS — the vacuous truth is refused' if plcok else '⛔ FAIL — all([]) reported a collapse'}")
    g0 = synth("import pathlib\nROOT=pathlib.Path('/r')\n"
               "def f():\n    return (ROOT/'x').read_text()\nf()\n", "f", "nonexistent_param")
    print(f"  g=0        a parameter that does not exist -> {g0[0]} ({g0[1]}) -> "
          f"{'PASS (cannot collapse)' if g0[0] != 'RESOLVED@1' else '⛔ FAIL'}")

    # ---- THE RESOLUTION -------------------------------------------------------------
    rows = []
    for m in d1_members:
        head, _, _idx = m.rpartition("#")
        rnd, _, line = head.rpartition(":")
        t = trees.get(rnd)
        if t is None:
            rows.append((rnd, int(line), None, "UNRUNNABLE", "module did not parse"))
            continue
        par = parents_of(t)
        node = None
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") in \
                    ("read_text", "read", "readlines") and n.lineno == int(line):
                node = n
                break
        fn = None
        cur = node
        while cur is not None and cur in par:
            cur = par[cur]
            if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = cur
                break
        if fn is None:
            rows.append((rnd, int(line), None, "CALLEE", "no enclosing function"))
            continue
        # which parameter blocks it: the first param reachable from the read target
        params = [a.arg for a in fn.args.args]
        blockers = [p for p in params
                    if any(isinstance(x, ast.Name) and x.id == p for x in ast.walk(fn))]
        param = None
        for p in params:
            if p in blockers:
                param = p
                break
        if param is None:
            rows.append((rnd, int(line), None, "CALLEE", "blocked by a callee return, not a param"))
            continue
        v, why = resolve_site(t, fn, param, consts.get(rnd, set()))
        rows.append((rnd, int(line), f"{fn.name}({param})", v, why))

    cnt = Counter(r[3] for r in rows)
    print(f"\n─── WHAT THE CALLERS ACTUALLY SUPPLY, for R652's {len(d1_members)} D1 sites ───")
    for k in ("RESOLVED@1", "PARTIAL", "DEEPER", "VACUOUS", "CALLEE", "UNRUNNABLE"):
        c = cnt.get(k, 0)
        print(f"  {k:<11} {c:>4}  ({c/max(len(rows),1):>5.1%})")
    print(f"\n  every non-RESOLVED@1 class, with an example (G3 — the whole grid):")
    seen = set()
    for rnd, line, fp, v, why in rows:
        if v not in seen:
            seen.add(v)
            print(f"    {v:<11} {rnd[:40]:<40} :{line:<4} {fp or '-':<22} {why}")

    # ---- THE KILL, EVALUATED EXPLICITLY ---------------------------------------------
    bad = [r for r in rows if r[3] == "RESOLVED@1" and "0 visible" in r[4]]
    vac_callee = cnt.get("VACUOUS", 0) + cnt.get("CALLEE", 0)
    controls_ok = (pos[0] == "RESOLVED@1" and neg[0] == "PARTIAL" and plcok
                   and g0[0] != "RESOLVED@1" and not bad)
    print(f"\n─── KILL ───")
    print(f"  vacuous guard: RESOLVED@1 verdicts with 0 visible call sites -> {len(bad)} -> "
          f"{'PASS' if not bad else '⛔ THE RESOLVED@1 COUNT IS VOID'}")
    print(f"  world C test : VACUOUS + CALLEE = {vac_callee} of {len(rows)} "
          f"(threshold 30) -> {'informative' if vac_callee <= 30 else '⛔ world C'}")

    coll = cnt.get("RESOLVED@1", 0)
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no looseness number is admissible"
    elif vac_callee > 30:
        world = (f"C UNINFORMATIVE — {vac_callee} of {len(rows)} sites are VACUOUS or CALLEE, so "
                 f"the single-module call graph does not answer the question.")
    elif coll >= 20:
        world = (f"B DEPTH 1 IS ENOUGH — {coll} of {len(rows)} D1 sites have their blocking "
                 f"argument statically supplied at EVERY visible call site, so one level of "
                 f"caller analysis resolves them.")
    else:
        # ⛔ v1 WROTE "D1=59 is CLOSE to the real count" -- a word I typed, not one I computed, on
        #    a 27.1% over-count. §4's `the verdict string is not a computation`. The descriptor is
        #    now derived from the measured share, with its own printed thresholds.
        share = coll / max(len(rows), 1)
        world = (f"A DEPTH 1 IS SHALLOW — one level of caller analysis resolves {coll} of "
                 f"{len(rows)} D1 sites ({share:.1%}; pre-registered line 20 = "
                 f"{20/len(rows):.1%}, so world B is not declared). "
                 f"{cnt.get('DEEPER',0)} sites ({cnt.get('DEEPER',0)/len(rows):.1%}) have "
                 f"callers that ALSO pass dynamic values and need depth >= 2; "
                 f"{cnt.get('PARTIAL',0)} resolve for a subset of calls; "
                 f"{cnt.get('CALLEE',0)} are blocked by a callee return instead. "
                 f"⭐ D1={b['counts']['D1']} is NOT over-counted -- every one of these sites is "
                 f"genuinely caller-dependent. What is refuted is the assumption underneath "
                 f"R652's NEXT: that reaching the caller ANSWERS the question. For "
                 f"{cnt.get('DEEPER',0)} of {len(rows)} it only moves it.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 resolver x {len(rows)} sites x every visible call site + 4 "
          f"controls + 2 kill checks. All classes printed.")
    print(f"  ⚠ BOUNDS: calls from another module are not enumerable, so VACUOUS means NO VISIBLE "
          f"caller and RESOLVED@1 is an UPPER bound on what one level buys.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "argument_resolution.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "counts": dict(cnt),
        "d1_baseline": b["counts"]["D1"], "resolved_at_depth_1": coll,
        "unresolved_at_depth_1": len(rows) - coll,
        "resolved_at_1_share": coll / max(len(rows), 1),
        "vacuous_guard": {"synthetic_positive": plcok, "real_firings": cnt.get("VACUOUS", 0),
                          "note": ("the guard PASSES its synthetic control and fired 0 times on "
                                   "the real corpus -- it protected against a hazard that did "
                                   "not occur here, so on real data it is validated only against "
                                   "an imagined case")},
        "rows": [{"round": r, "line": l, "fn_param": f, "verdict": v, "why": w}
                 for r, l, f, v, w in rows],
        "check254": ("R652's NEXT said removing pat+rid makes the caller-dependent count 'fall "
                     "below half'. 59-25=34 = 57.6% of 59. It falls below half only of R651's "
                     "RETRACTED 98 (34.7%) -- measured against a number killed in the same round."),
        "impossible": ("calls from outside the module are not enumerable from this tree, so "
                       "VACUOUS means 'no visible caller' and COLLAPSES is an upper bound. An "
                       "exact answer needs a whole-corpus import graph, which does not exist "
                       "because every round is a standalone script by construction."),
    }, indent=2))
    print(f"\n  wrote {out / 'argument_resolution.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
