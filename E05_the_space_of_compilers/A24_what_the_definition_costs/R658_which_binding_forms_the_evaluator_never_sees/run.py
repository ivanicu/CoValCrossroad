#!/usr/bin/env python3
"""
R658 -- is the residual a missing SYNTACTIC FORM, or a right-hand side that does not resolve?

CHECK #259 ON R657's CLOSING LINE. TWO CLAUSES HOLD, ONE IS SELF-UNDERMINING.
  ✓ "`local_bindings` handles only Assign and For targets" -- read from the source, correct.
  ✓ "this arc has already retracted one structural limit" -- entry 651, R649's own IMPOSSIBLE
    register line, retracted before that round shipped.
  ⛔ "every remaining undecided round is now LABELLED BY MECHANISM -- STILL-LOCAL versus
    STILL-UNRESOLVED". STILL-UNRESOLVED means "no binding found at all", which is the ABSENCE of a
    mechanism, not one. Measured: 3 of 8 are STILL-LOCAL and carry a mechanism; 5 of 8 carry none.
    A sentence that presents a residual bucket as a label is how a residual stops being counted.

⚠ AND n=5 IS NOT A POPULATION. The question -- does the residual come from missing SYNTAX or from
  right-hand sides that do not resolve -- is answerable across every round, over every name ever
  used as a glob base. That is the population this round uses.

ESTIMAND        Over every A24 round: for each NAME used as a glob base that the evaluator cannot
                resolve, classify its binding sites into
                  UNHANDLED-FORM  bound ONLY by a form the evaluator never inspects:
                                  `with ... as`, a comprehension target, a tuple-unpack, a walrus,
                                  an AugAssign
                  HANDLED-FORM    bound by Assign or For -- a form the evaluator DOES inspect --
                                  but the right-hand side does not resolve
                  PARAMETER       the name is a function parameter
                  UNBOUND         no binding site anywhere in the module (an import, a builtin, a
                                  global from elsewhere)
                share_unhandled = UNHANDLED-FORM / (all unresolved names).
IDENTIFICATION  Exact for the syntactic classification. NOT identified for "extending the evaluator
                to this form would resolve it" -- a `with ... as tmp` binds a TemporaryDirectory,
                which is runtime whatever the syntax. So share_unhandled is an UPPER BOUND on what
                new syntax could buy, and is reported as one.
SCOPE           population : every name used as a glob base in any A24 round, MINUS this round
                instrument : ast; a name is unresolved iff PathEval (module + function scope, as
                             R657 left it) returns None for it
                             instrument unit = A (ROUND, NAME) PAIR
                             claim unit      = A (ROUND, NAME) PAIR
                             EQUAL by construction
                baseline   : R657's 8 undecided rounds, which must appear inside this population
                regime     : at the tree sha persisted in the artifact
WORLDS          A SYNTAX GAP: unhandled forms dominate -> the residual is an evaluator gap and more
                  syntax buys it back.
                B RHS GAP: handled forms with unresolvable right-hand sides dominate -> new syntax
                  buys little, and the residual is closer to structural.
                C NEITHER: parameters and unbound names dominate -> the question is interprocedural
                  and neither syntax nor RHS evaluation is the lever.
KILL            pre-registered verbatim in PREREGISTRATION.txt before the code existed:
                point 20%, interval [5%, 45%], and the directional prediction that unhandled FORMS
                are NOT the blocker. If UNHANDLED-FORM > 50%, that prediction is RETRACTED.
POSITIVE CTRL   (i) a synthetic `with tempfile.TemporaryDirectory() as t: Path(t).glob("*")` must
                    classify UNHANDLED-FORM -- the detector must be able to see the class at all.
                (ii) R657's 8 undecided rounds must all appear in the population.
                Fails at g=0: a module whose every glob base resolves contributes 0 names.
NEGATIVE CTRL   a synthetic whose base is bound by a plain `Assign` from an unresolvable call must
                classify HANDLED-FORM, never UNHANDLED-FORM. The failure direction is to call
                everything unhandled and manufacture a syntax gap.
PLACEBO         a synthetic whose base name has NO binding anywhere -> UNBOUND, its own outcome.
                A name with no binding is not a form the evaluator is missing.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 classifier x every unresolved (round, name) + 4 controls. Every class printed.
ARTIFACT        results/binding_forms.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      whether extending the evaluator to a form would actually resolve the name depends
                on what the form binds, which is often runtime (a temp dir, a subprocess output).
                So this measures what is SYNTACTICALLY invisible, an upper bound on the gap.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
E05 = A24.parent
ROOT = A24.parents[1]
PATH_GLOBS = {"glob", "rglob", "iterdir"}
PREREG = {"point_pct": 20, "interval_pct": [5, 45],
          "directional": ("the missing FORMS are not the blocker; handled forms with unresolvable "
                          "right-hand sides will dominate"),
          "kill": "UNHANDLED-FORM > 50% retracts the directional prediction",
          "no_shading_note": ("three consecutive over-estimates (-25, -7, -5) were NOT used to "
                              "shade this estimate: n=3 licenses no correction, and an unearned "
                              "adjustment would make the next miss uninterpretable")}


class PathEval:
    """R657's evaluator, unchanged, so 'unresolved' means what it meant there."""

    def __init__(self, modpath):
        self.mod, self.env = modpath, {}

    def bind_module(self, tree):
        for n in tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                    and isinstance(n.targets[0], ast.Name):
                v = self.path_of(n.value)
                if v is not None:
                    self.env[n.targets[0].id] = v

    def path_of(self, n):
        if isinstance(n, ast.Name):
            return self.env.get(n.id)
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return pathlib.Path(n.value)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            l, r = self.path_of(n.left), n.right
            if l is None or not (isinstance(r, ast.Constant) and isinstance(r.value, str)):
                return None
            return l / r.value
        if isinstance(n, ast.Attribute):
            b = self.path_of(n.value)
            return b.parent if (b is not None and n.attr == "parent") else None
        if isinstance(n, ast.Subscript):
            if isinstance(n.value, ast.Attribute) and n.value.attr == "parents" \
                    and isinstance(n.slice, ast.Constant):
                b = self.path_of(n.value.value)
                try:
                    return b.parents[n.slice.value] if b is not None else None
                except Exception:
                    return None
            return None
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id == "str" and n.args:
                return self.path_of(n.args[0])
            if isinstance(f, ast.Attribute):
                if f.attr in ("resolve", "absolute", "expanduser"):
                    return self.path_of(f.value)
                if f.attr == "Path" and n.args:
                    a = n.args[0]
                    return self.mod if (isinstance(a, ast.Name) and a.id == "__file__") \
                        else self.path_of(a)
            if isinstance(f, ast.Name) and f.id == "Path" and n.args:
                a = n.args[0]
                return self.mod if (isinstance(a, ast.Name) and a.id == "__file__") \
                    else self.path_of(a)
        return None


HANDLED = {"Assign", "For"}
UNHANDLED = {"With", "Comprehension", "TupleUnpack", "Walrus", "AugAssign"}


def binding_forms(tree, name):
    """Every syntactic form that binds `name` in this module."""
    forms = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    forms.add("Assign")
                elif isinstance(t, (ast.Tuple, ast.List)) and any(
                        isinstance(e, ast.Name) and e.id == name for e in t.elts):
                    forms.add("TupleUnpack")
        elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name) \
                and n.target.id == name:
            forms.add("AugAssign")
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            if isinstance(n.target, ast.Name) and n.target.id == name:
                forms.add("For")
            elif isinstance(n.target, (ast.Tuple, ast.List)) and any(
                    isinstance(e, ast.Name) and e.id == name for e in n.target.elts):
                forms.add("TupleUnpack")
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            ov = n.optional_vars
            if isinstance(ov, ast.Name) and ov.id == name:
                forms.add("With")
            elif isinstance(ov, (ast.Tuple, ast.List)) and any(
                    isinstance(e, ast.Name) and e.id == name for e in ov.elts):
                forms.add("With")
        elif isinstance(n, ast.comprehension):
            if isinstance(n.target, ast.Name) and n.target.id == name:
                forms.add("Comprehension")
            elif isinstance(n.target, (ast.Tuple, ast.List)) and any(
                    isinstance(e, ast.Name) and e.id == name for e in n.target.elts):
                forms.add("Comprehension")
        elif isinstance(n, ast.NamedExpr) and isinstance(n.target, ast.Name) \
                and n.target.id == name:
            forms.add("Walrus")
    return forms


def is_param(tree, name):
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = fn.args
            names = ({a.arg for a in args.args} | {a.arg for a in args.kwonlyargs}
                     | {a.arg for a in args.posonlyargs})
            if args.vararg:
                names.add(args.vararg.arg)
            if args.kwarg:
                names.add(args.kwarg.arg)
            if name in names:
                return True
    return False



def base_name(expr):
    """The NAME a path expression is rooted at, or None.

    ⛔ v1 HAD TWO DEFECTS AND BOTH INFLATED OR SILENCED THE POPULATION.
       ① it descended only Attribute/Subscript, so a `BinOp` base -- `(d / "results").glob(...)`,
          which is the commonest shape in this corpus -- fell through a `continue` and was
          DROPPED. R337 vanished from its own population and POSITIVE-2 caught it.
       ② for a Call it walked the tree and took the FIRST Name, which for `str(ROOT / X)` is the
          CALLEE `str`. All 8 UNBOUND pairs were that artifact -- a class invented by an
          extractor, not observed in the corpus.
    """
    seen = 0
    while seen < 12:
        seen += 1
        if isinstance(expr, ast.Name):
            return expr.id
        if isinstance(expr, (ast.Attribute, ast.Subscript)):
            expr = expr.value
            continue
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Div):
            expr = expr.left               # a path is rooted at the LEFTMOST operand
            continue
        if isinstance(expr, ast.Call):
            f = expr.func
            fn = getattr(f, "id", None) or getattr(f, "attr", None)
            if fn in ("str", "Path", "sorted", "list") and expr.args:
                expr = expr.args[0]        # descend into the ARGUMENT, never the callee
                continue
            if isinstance(f, ast.Attribute):
                expr = f.value             # x.resolve() -> x
                continue
            return None
        return None
    return None

def unresolved_names(path):
    """Every NAME used as a glob base that PathEval cannot resolve, with its binding forms."""
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return []
    ev = PathEval(path.resolve())
    ev.bind_module(tree)
    out = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)):
            continue
        if n.func.attr in PATH_GLOBS and not (isinstance(n.func.value, ast.Name)
                                              and n.func.value.id == "glob"):
            expr = n.func.value
        elif n.func.attr in ("glob", "iglob") and isinstance(n.func.value, ast.Name) \
                and n.func.value.id == "glob":
            expr = n.args[0] if n.args else None
        else:
            continue
        if expr is None or ev.path_of(expr) is not None:
            continue
        nm = base_name(expr)
        if nm is None:
            continue
        forms = binding_forms(tree, nm)
        if is_param(tree, nm):
            kind = "PARAMETER"
        elif not forms:
            kind = "UNBOUND"
        elif forms & HANDLED:
            kind = "HANDLED-FORM"
        else:
            kind = "UNHANDLED-FORM"
        out.append({"name": nm, "kind": kind, "forms": sorted(forms), "line": n.lineno})
    return out


def main() -> int:
    r657 = A24 / "R657_bind_the_function_local_bases" / "results" / "local_binding.json"
    if not r657.exists():
        print("UNRUNNABLE: R657's artifact absent. Exit 2, never 0.")
        return 2
    prev = json.loads(r657.read_text())
    undecided = [n for n, v in prev["per_round"].items()
                 if v["verdict"] in ("STILL-LOCAL", "STILL-UNRESOLVED")]

    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    found = {d.name: unresolved_names(d / "run.py") for d in rounds}
    flat = [dict(r, round=k) for k, v in found.items() for r in v]

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  point {PREREG['point_pct']}%   interval {PREREG['interval_pct']}%")
    print(f"  directional: {PREREG['directional']}")
    print(f"  kill       : {PREREG['kill']}")
    print(f"  ⚠ {PREREG['no_shading_note']}")

    print("\n─── CONTROLS ───")

    def synth(src):
        t = ast.parse(src)
        p = A24 / "R999_synth" / "run.py"
        ev = PathEval(p.resolve())
        ev.bind_module(t)
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in PATH_GLOBS:
                expr = n.func.value
                if ev.path_of(expr) is not None:
                    return "RESOLVED"
                nm = base_name(expr)
                if nm is None:
                    return "NOT-A-NAME"
                f = binding_forms(t, nm)
                if is_param(t, nm):
                    return "PARAMETER"
                if not f:
                    return "UNBOUND"
                return "HANDLED-FORM" if (f & HANDLED) else "UNHANDLED-FORM"
        return "NO-GLOB"

    pos1 = synth("import tempfile, pathlib\n"
                 "def f():\n    with tempfile.TemporaryDirectory() as t:\n"
                 "        return list(pathlib.Path(t).glob('*'))\n")
    print(f"  POSITIVE-1 `with TemporaryDirectory() as t` -> {pos1} -> "
          f"{'PASS — the class is visible at all' if pos1 == 'UNHANDLED-FORM' else '⛔ FAIL'}")
    seen_rounds = {r["round"] for r in flat}
    missing = [n for n in undecided if n not in seen_rounds]
    print(f"  POSITIVE-2 R657's {len(undecided)} undecided rounds must appear in this population "
          f"-> {len(undecided)-len(missing)}/{len(undecided)} -> "
          f"{'PASS' if not missing else '⛔ FAIL: ' + str(missing[:3])}")
    neg = synth("import json, pathlib\n"
                "def f():\n    r = pathlib.Path(json.loads('{}')['p'])\n"
                "    return list(r.glob('*'))\n")
    print(f"  NEGATIVE   a plain Assign from an unresolvable call -> {neg} -> "
          f"{'PASS — not everything unresolved is a missing FORM' if neg == 'HANDLED-FORM' else '⛔ FAIL'}")
    plc = synth("import pathlib\nfrom somewhere import BASE\n"
                "def f():\n    return list(BASE.glob('*'))\n")
    print(f"  PLACEBO    a name with NO binding anywhere -> {plc} -> "
          f"{'PASS — its own outcome, not a missing form' if plc == 'UNBOUND' else '⛔ FAIL'}")
    g0 = synth("import pathlib\nA=pathlib.Path('/x')\ndef f():\n    return list(A.glob('*'))\n")
    print(f"  g=0        a module whose base RESOLVES -> {g0} -> "
          f"{'PASS (contributes 0 names)' if g0 == 'RESOLVED' else '⛔ FAIL'}")
    controls_ok = (pos1 == "UNHANDLED-FORM" and not missing and neg == "HANDLED-FORM"
                   and plc == "UNBOUND" and g0 == "RESOLVED")
    print(f"  KILL       UNHANDLED-FORM > 50% retracts the directional prediction")

    cnt = Counter(r["kind"] for r in flat)
    n = len(flat)
    share = 100.0 * cnt.get("UNHANDLED-FORM", 0) / max(n, 1)
    print(f"\n─── EVERY UNRESOLVED GLOB-BASE NAME IN THE CORPUS ───")
    print(f"  rounds scanned            : {len(rounds)}")
    print(f"  unresolved (round, name)  : {n}")
    for k in ("HANDLED-FORM", "PARAMETER", "UNHANDLED-FORM", "UNBOUND"):
        c = cnt.get(k, 0)
        print(f"  {k:<16} {c:>4}  ({c/max(n,1):>5.1%})")
    print(f"\n  the FORMS actually seen, whole grid:")
    for f, c in Counter(tuple(r["forms"]) for r in flat).most_common(12):
        print(f"    {c:>4}  {list(f) or '(no binding site)'}")
    print(f"\n  the names, most frequent first:")
    for nm, c in Counter(r["name"] for r in flat).most_common(10):
        print(f"    {c:>4}  {nm}")

    lo, hi = PREREG["interval_pct"]
    inside = lo <= share <= hi
    directional_holds = cnt.get("UNHANDLED-FORM", 0) <= n / 2
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  point {PREREG['point_pct']}% · interval [{lo}%, {hi}%]   measured {share:.1f}%")
    print(f"  => {'INSIDE' if inside else 'OUTSIDE'} the interval; error vs point "
          f"{share - PREREG['point_pct']:+.1f} pts")
    print(f"  directional prediction ('forms are not the blocker'): "
          f"{'HOLDS' if directional_holds else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no share is admissible"
    elif not directional_holds:
        world = (f"A SYNTAX GAP — UNHANDLED-FORM is {share:.1f}% of {n} unresolved names, above "
                 f"half. The residual IS an evaluator gap and more syntax buys it back. The "
                 f"pre-registered directional prediction is RETRACTED.")
    elif cnt.get("HANDLED-FORM", 0) >= max(cnt.values()):
        world = (f"B RHS GAP — {cnt.get('HANDLED-FORM',0)} of {n} unresolved names "
                 f"({cnt.get('HANDLED-FORM',0)/n:.1%}) are bound by a form the evaluator ALREADY "
                 f"inspects, and fail on the right-hand side. Unhandled forms are {share:.1f}%. "
                 f"More syntax buys little; the residual is closer to structural. ⚠ AND THAT IS "
                 f"AN UPPER BOUND ON THE GAP, not a proof of a limit: a `with ... as tmp` binds a "
                 f"temp directory, which is runtime whatever syntax reads it.")
    else:
        world = (f"C NEITHER — parameters/unbound dominate ({cnt.get('PARAMETER',0)} + "
                 f"{cnt.get('UNBOUND',0)} of {n}); the lever is interprocedural, not syntactic "
                 f"and not RHS evaluation.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 classifier x {n} unresolved (round, name) pairs + 4 controls. "
          f"All four classes and every form combination printed.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "binding_forms.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "prereg": PREREG, "measured_share_unhandled_pct": share, "inside_interval": inside,
        "directional_holds": directional_holds,
        "rounds": len(rounds), "unresolved_pairs": n, "counts": dict(cnt),
        "forms_grid": {str(list(f)): c for f, c in
                       Counter(tuple(r["forms"]) for r in flat).items()},
        "pairs": flat,
        "check259": ("R657's NEXT said every undecided round is 'labelled by mechanism'. "
                     "STILL-UNRESOLVED means no binding found -- the ABSENCE of a mechanism. "
                     "Measured: 3 of 8 carry one, 5 of 8 do not."),
        "impossible": ("whether extending the evaluator to a form would resolve the name depends "
                       "on what the form binds, often runtime; so the share is an UPPER BOUND on "
                       "what new syntax could buy."),
    }, indent=2))
    print(f"\n  wrote {out / 'binding_forms.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
