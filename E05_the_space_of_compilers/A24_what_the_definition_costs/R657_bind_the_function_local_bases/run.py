#!/usr/bin/env python3
"""
R657 -- bind function-local assignments, against an estimate written before the code.

CHECK #258 ON R656's CLOSING LINE. THREE CLAIMS, ONE CORRECT, TWO WRONG -- AND ONE OF THEM IS THE
ARC'S OLDEST FAILURE COMMITTED AGAIN.
  ✓ "14 of the 21 remaining are FUNCTION-LOCAL" -- correct.
  ⛔ "12 of those bind a SINGLE name" -- it is 13. And I READ THAT OFF A GRID PRINTING `notes[:1]`,
     one note per round, so R554 looked like `RECV unresolved` when it names `d`, and R337 names
     TWO (`d`, `sub`). This arc has now spent four rounds on truncations (R630 `[:12]`, R646
     `head -3`, R647 `tail -25`, and this) and the display was MY OWN, printed three lines above
     the sentence that misread it.
  ⛔ The name list was also wrong: `s` and `st` appear NOWHERE in the FUNCTION-LOCAL set -- they
     came from R655's SHAPE table, a different population -- while `sub` does and was omitted.
  ⛔ "this round's forecast was wrong by 7 and THE PREVIOUS ONE BY 11": no forecast in this arc was
     off by 11. Eleven was the forecast's VALUE. I named an error magnitude by reusing the number
     that had just been refuted, which is retraction 662's shape exactly.

⭐ AND THE ESTIMATE FOR THIS ROUND WAS WRITTEN BEFORE ANY CODE, AS AN INTERVAL, because two
   consecutive point forecasts (25->0 and 11->4) landed outside anything I would have drawn:
     POINT 11 · INTERVAL [8, 14]
     REASONING: 13 of 14 bind exactly one local name; 7 bind `root`, which in this corpus is
       usually `Path(__file__).resolve().parents[N]` and resolves; 3 bind `d`, usually a FOR-LOOP
       variable rather than an assignment, and those are the doubtful ones.
     KILL: a measurement OUTSIDE [8, 14] means the FORECASTING PROCEDURE failed, not just the
       number, and the report must say so rather than quoting the new value as though the method
       were sound.

ESTIMAND        Of R656's 14 FUNCTION-LOCAL rounds, how many become DECIDED (all sites classified)
                once the evaluator also binds names assigned INSIDE a function -- plain
                assignments and for-loop targets over a resolvable iterable.
                n_decided, against the pre-registered [8, 14] with point 11.
IDENTIFICATION  Exact for a name with a single unambiguous binding in its enclosing scope. NOT
                identified where a name is rebound on several branches with different values, or
                where the binding traces to a parameter: those return AMBIGUOUS and STILL-LOCAL
                respectively, both reported, neither folded into decided.
SCOPE           population : R656's 14 FUNCTION-LOCAL rounds, MINUS this round
                instrument : ast + a symbolic pathlib evaluator with function-scope binding
                             instrument unit = A GLOB SITE
                             claim unit      = A ROUND
                             NOT EQUAL -- a round is decided only if EVERY site is, which is the
                             discipline R656 had to repair mid-round
                baseline   : R656's classification, reproduced on every round it decided
                regime     : at the tree sha persisted in the artifact
WORLDS          A THE BINDING WORKS: most of the 14 decide -> the residual was an evaluator gap and
                  the census can close to a small number.
                B THE BINDING FAILS: few decide -> a function-local base is not resolvable by scope
                  binding either, and the residual is structural rather than a missing feature.
                C THE ESTIMATE WAS THE PROBLEM: the count lands outside [8, 14] -> whichever way it
                  goes, my forecasting procedure is what needs reporting, not the number.
KILL            pre-registered above, verbatim, before the code existed. Outside [8, 14] => world C
                is declared IN ADDITION to A or B.
POSITIVE CTRL   (i) every round R656 DECIDED must keep its verdict.
                (ii) a synthetic `def f(): r = ROOT / "x"; return r.glob("*")` -> CORPUS.
                Fails at g=0: with no local assignment the binder adds nothing.
NEGATIVE CTRL   a synthetic whose local is assigned from a PARAMETER -> STILL-LOCAL, not decided.
                The failure direction is to bind anything that has an assignment anywhere.
PLACEBO         a synthetic whose local is assigned TWO different paths on two branches ->
                AMBIGUOUS, never silently taking the first. This is the control the round turns
                on: a binder that takes the first binding manufactures a decision.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 binder x 14 rounds x every glob site + reproduction over every decided round
                + 5 controls. Every outcome printed.
ARTIFACT        results/local_binding.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      a local assigned from a parameter needs the call graph, which does not exist across
                standalone scripts; a local rebound in a loop over runtime data is not static at
                all. Both named, neither attempted.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
E05 = A24.parent
ROOT = A24.parents[1]
PATH_GLOBS = {"glob", "rglob", "iterdir"}
PREREG = {"point": 11, "interval": [8, 14],
          "reasoning": ("13 of 14 bind exactly one local name; 7 bind `root`, usually "
                        "Path(__file__).resolve().parents[N]; 3 bind `d`, usually a FOR-LOOP "
                        "variable, and those are the doubtful ones"),
          "kill": ("a measurement outside [8, 14] means the FORECASTING PROCEDURE failed, not "
                   "merely the number")}


class PathEval:
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


def enclosing_fn(node, parents):
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur
    return None


def parents_of(tree):
    p = {}
    for a in ast.walk(tree):
        for c in ast.iter_child_nodes(a):
            p[c] = a
    return p


def local_bindings(fn, ev):
    """name -> resolved Path, or the sentinel AMBIGUOUS / PARAM for names that must not bind.

    ⭐ THE PLACEBO THIS ROUND TURNS ON: a name assigned two different paths on two branches must
       NOT take the first. A binder that takes the first binding manufactures a decision.
    """
    params = {a.arg for a in fn.args.args} | {a.arg for a in fn.args.kwonlyargs}
    cand: dict[str, list] = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    cand.setdefault(t.id, []).append(("assign", n.value))
        elif isinstance(n, (ast.For, ast.AsyncFor)) and isinstance(n.target, ast.Name):
            cand.setdefault(n.target.id, []).append(("loop", n.iter))
    out = {}
    for name, defs in cand.items():
        if name in params:
            out[name] = "PARAM"
            continue
        # ⛔ THE NEGATIVE CONTROL CAUGHT A REAL CONFLATION. v1 marked a name PARAM only when the
        #    name IS a parameter. `r = base` with `base` a parameter left `r` absent from the
        #    table entirely, so it read as "unresolved" -- collapsing a NAMED residual
        #    (traces to a caller) into an anonymous one (I could not resolve it). The whole point
        #    of STILL-LOCAL is that it says WHY. Propagated: an assignment whose RHS mentions a
        #    parameter marks the target PARAM too.
        if any(kind == "assign" and ({x.id for x in ast.walk(expr) if isinstance(x, ast.Name)}
                                     & params) for kind, expr in defs):
            out[name] = "PARAM"
            continue
        vals = []
        for kind, expr in defs:
            if kind == "assign":
                v = ev.path_of(expr)
            else:
                # a loop target: bind to the ITERABLE's base, which is what a glob under it
                # addresses. `for d in A24.glob("R*")` -> d lives under A24.
                base = expr
                while isinstance(base, ast.Call) and isinstance(base.func, ast.Attribute):
                    if base.func.attr in PATH_GLOBS:
                        base = base.func.value
                        break
                    base = base.func.value
                if isinstance(base, ast.Call) and isinstance(base.func, ast.Name) \
                        and base.func.id in ("sorted", "list") and base.args:
                    b2 = base.args[0]
                    while isinstance(b2, ast.Call) and isinstance(b2.func, ast.Attribute):
                        if b2.func.attr in PATH_GLOBS:
                            b2 = b2.func.value
                            break
                        b2 = b2.func.value
                    base = b2
                v = ev.path_of(base)
            if v is not None:
                vals.append(v)
        if not vals:
            continue
        if len({str(v) for v in vals}) > 1:
            out[name] = "AMBIGUOUS"
        else:
            out[name] = vals[0]
    return out


def classify(path, with_local: bool):
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return "UNPARSEABLE", []
    ev = PathEval(path.resolve())
    ev.bind_module(tree)
    par = parents_of(tree)
    own = path.resolve().parent
    seen, notes, unres, floc, ambig = [], [], 0, 0, 0

    def cls(p):
        try:
            rel = p.resolve()
        except Exception:
            return None
        if rel == own or own in rel.parents:
            return "OWN"
        s = str(rel)
        if rel in (A24.resolve(), E05.resolve(), ROOT.resolve()) or A24.resolve() in rel.parents \
                or str(A24.resolve()) in s or str(E05.resolve()) in s:
            return "CORPUS"
        return "OTHER"

    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        is_path = isinstance(n.func, ast.Attribute) and n.func.attr in PATH_GLOBS \
            and not (isinstance(n.func.value, ast.Name) and n.func.value.id == "glob")
        is_mod = isinstance(n.func, ast.Attribute) and n.func.attr in ("glob", "iglob") \
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "glob"
        if not (is_path or is_mod):
            continue
        expr = n.func.value if is_path else (n.args[0] if n.args else None)
        if expr is None:
            unres += 1
            continue
        p = ev.path_of(expr)
        if p is None and with_local:
            fn = enclosing_fn(n, par)
            if fn is not None:
                lb = local_bindings(fn, ev)
                saved = dict(ev.env)
                bad = False
                for k, v in lb.items():
                    if v == "AMBIGUOUS":
                        continue
                    if v == "PARAM":
                        continue
                    ev.env[k] = v
                p = ev.path_of(expr)
                names = {x.id for x in ast.walk(expr) if isinstance(x, ast.Name)}
                if p is None:
                    if any(lb.get(k) == "AMBIGUOUS" for k in names):
                        ambig += 1
                        notes.append(f"AMBIGUOUS local: {sorted(names & set(lb))[:2]}")
                        ev.env = saved
                        continue
                    if any(lb.get(k) == "PARAM" for k in names):
                        floc += 1
                        notes.append(f"local from a PARAMETER: {sorted(names & set(lb))[:2]}")
                        ev.env = saved
                        continue
                ev.env = saved
                if p is not None:
                    notes.append(f"bound local -> {p.name or p}")
        if p is None:
            unres += 1
            notes.append("unresolved")
            continue
        c = cls(p)
        if c is None:
            unres += 1
        else:
            seen.append(c)
            notes.append(f"-> {c}")
    if unres or floc or ambig:
        if seen:
            return "PARTIAL-UNDECIDED", notes
        if ambig:
            return "AMBIGUOUS", notes
        if floc:
            return "STILL-LOCAL", notes
        return "STILL-UNRESOLVED", notes
    if "CORPUS" in seen and "OWN" in seen:
        return "MIXED", notes
    if "CORPUS" in seen:
        return "CORPUS-DEPENDENT", notes
    if "OTHER" in seen and "OWN" not in seen:
        return "OUTSIDE-BOTH", notes
    if seen:
        return "OWN-SCOPE", notes
    return "NO-GLOB", notes


DECIDED = {"CORPUS-DEPENDENT", "OWN-SCOPE", "MIXED", "OUTSIDE-BOTH"}


def main() -> int:
    r656 = A24 / "R656_two_apis_one_rule" / "results" / "api_dispatch.json"
    if not r656.exists():
        print("UNRUNNABLE: R656's artifact absent. Exit 2, never 0.")
        return 2
    b = json.loads(r656.read_text())
    targets = [n for n, v in b["per_round"].items() if v["verdict"] == "FUNCTION-LOCAL"]
    already = [n for n, v in b["per_round"].items() if v["verdict"] in DECIDED]

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  point {PREREG['point']}   interval {PREREG['interval']}")
    print(f"  reasoning: {PREREG['reasoning']}")
    print(f"  kill     : {PREREG['kill']}")

    print("\n─── CONTROLS ───")
    # ⛔ v1's POSITIVE-1 WAS "REPRODUCE R656 EXACTLY", AND THAT ENFORCES REPRODUCING A DEFECT.
    #    R656 repaired its residual-folding for OWN-SCOPE and LEFT IT IN PLACE for
    #    CORPUS-DEPENDENT: its order tests `if "CORPUS" in seen` BEFORE the residual check, so a
    #    round with one CORPUS site and three unresolved ones was called decided. R319 is exactly
    #    that. This round orders the residual check first, so it correctly UN-decides R319 -- and
    #    a control demanding agreement would have forced me to re-introduce the fold.
    #    Repaired: a disagreement is admissible IFF it is a fold R656 committed, and each one is
    #    NAMED. Any other disagreement still fails.
    kept, folds, bad = [], [], []
    for n in already:
        v, notes = classify(A24 / n / "run.py", True)
        if v in DECIDED:
            kept.append(n)
        elif b["per_round"][n]["verdict"] == "CORPUS-DEPENDENT" and v == "PARTIAL-UNDECIDED":
            folds.append((n, notes))
        else:
            bad.append((n, b["per_round"][n]["verdict"], v))
    print(f"  POSITIVE-1 R656's decided rounds: {len(kept)} reproduced, {len(folds)} were R656 "
          f"FOLDS now un-decided, {len(bad)} unexplained -> {'PASS' if not bad else '⛔ FAIL'}")
    for n, notes in folds:
        print(f"               ⛔ R656 FOLD  {n[:44]:<44} {notes}")

    def synth(src):
        t = ast.parse(src)
        p = A24 / "R999_synth" / "run.py"
        ev = PathEval(p.resolve())
        ev.bind_module(t)
        par = parents_of(t)
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in PATH_GLOBS:
                fn = enclosing_fn(n, par)
                if fn is None:
                    return "NO-FN"
                lb = local_bindings(fn, ev)
                names = {x.id for x in ast.walk(n.func.value) if isinstance(x, ast.Name)}
                for k in names:
                    if lb.get(k) == "AMBIGUOUS":
                        return "AMBIGUOUS"
                    if lb.get(k) == "PARAM":
                        return "STILL-LOCAL"
                for k, v in lb.items():
                    if not isinstance(v, str):
                        ev.env[k] = v
                q = ev.path_of(n.func.value)
                if q is None:
                    return "UNRESOLVED"
                s = str(q.resolve())
                if str((A24 / "R999_synth").resolve()) in s:
                    return "OWN"
                return "CORPUS" if str(A24.resolve()) in s else "OTHER"
        return "NO-GLOB"

    hdr = ("import pathlib\nA24=pathlib.Path('%s')\nHERE=pathlib.Path('%s')\n"
           % (A24.as_posix(), (A24 / "R999_synth").as_posix()))
    pos2 = synth(hdr + "def f():\n    r = A24 / 'x'\n    return list(r.glob('*'))\n")
    print(f"  POSITIVE-2 a local assigned a module-derived path -> {pos2} -> "
          f"{'PASS' if pos2 == 'CORPUS' else '⛔ FAIL'}")
    neg = synth(hdr + "def f(base):\n    r = base\n    return list(r.glob('*'))\n")
    print(f"  NEGATIVE   a local assigned from a PARAMETER -> {neg} -> "
          f"{'PASS — not everything with an assignment binds' if neg == 'STILL-LOCAL' else '⛔ FAIL'}")
    plc = synth(hdr + "def f(c):\n    if c:\n        r = A24 / 'x'\n    else:\n        r = HERE / 'y'\n"
                      "    return list(r.glob('*'))\n")
    plcok = plc == "AMBIGUOUS"
    print(f"  PLACEBO    a local assigned TWO different paths on two branches -> {plc} -> "
          f"{'PASS — it refuses rather than taking the first' if plcok else '⛔ FAIL'}")
    g0 = synth(hdr + "def f():\n    return list(A24.glob('*'))\n")
    print(f"  g=0        no local assignment at all -> {g0} -> "
          f"{'PASS (the binder adds nothing)' if g0 == 'CORPUS' else '⛔ FAIL'}")
    controls_ok = (not bad and pos2 == "CORPUS" and neg == "STILL-LOCAL"
                   and plcok and g0 == "CORPUS")
    print(f"  KILL       measurement outside {PREREG['interval']} => the FORECASTING PROCEDURE "
          f"failed, reported as such")

    res = {n: classify(A24 / n / "run.py", True) for n in targets}
    cnt = Counter(v[0] for v in res.values())
    decided = sum(c for k, c in cnt.items() if k in DECIDED)
    print(f"\n─── THE {len(targets)} FUNCTION-LOCAL ROUNDS, WITH SCOPE BINDING ───")
    for k in ("CORPUS-DEPENDENT", "OWN-SCOPE", "MIXED", "OUTSIDE-BOTH", "PARTIAL-UNDECIDED",
              "AMBIGUOUS", "STILL-LOCAL", "STILL-UNRESOLVED"):
        c = cnt.get(k, 0)
        print(f"  {k:<18} {c:>4}  ({c/max(len(targets),1):>5.1%})")
    print(f"\n  every round, with EVERY note (not notes[:1] — check #258's lesson):")
    for n in sorted(res):
        v, notes = res[n]
        print(f"    {v:<18} {n[:44]:<44} {notes}")

    lo, hi = PREREG["interval"]
    inside = lo <= decided <= hi
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  point {PREREG['point']} · interval [{lo}, {hi}]   measured {decided}")
    print(f"  => {'INSIDE the interval — the forecasting procedure survives' if inside else 'OUTSIDE the interval — THE FORECASTING PROCEDURE FAILED, not just the number'}")
    print(f"  error vs point: {decided - PREREG['point']:+d}")

    # ⭐ THREE FORECASTS, ALL IN ONE DIRECTION -- PRICED AGAINST ITS OWN NULL BEFORE BEING CALLED
    #    A PATTERN. §4 forbids over-correcting into a narrative the count does not carry.
    hist = [("R654 NEXT -> R655", 25, 0), ("R655 NEXT -> R656", 11, 4),
            ("R657 prereg -> here", PREREG["point"], decided)]
    print(f"\n─── MY OWN FORECAST RECORD, with its null ───")
    print(f"    {'forecast':<22} {'predicted':>10} {'measured':>9} {'error':>7}")
    for lbl, pr, me in hist:
        print(f"    {lbl:<22} {pr:>10} {me:>9} {me-pr:>+7d}")
    same = all((me - pr) < 0 for _, pr, me in hist)
    pnull = 2 ** -len(hist)
    print(f"  all {len(hist)} over-estimates: {same}. Under a symmetric null the probability of "
          f"{len(hist)}/{len(hist)} same-signed errors is {pnull:.3f}")
    print(f"  => a DIRECTION, not an established bias: n={len(hist)} cannot clear any correction, "
          f"and the honest statement is that the magnitude is shrinking (-25, -7, "
          f"{decided-PREREG['point']:+d}) while the sign has not flipped.")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no binding claim is admissible"
    else:
        core = (f"A THE BINDING WORKS — {decided} of {len(targets)} decide once function-scope "
                f"assignments are bound." if decided >= len(targets) / 2 else
                f"B THE BINDING FAILS — only {decided} of {len(targets)} decide; a function-local "
                f"base is not resolvable by scope binding either.")
        world = core + (f" The measurement is INSIDE the pre-registered [{lo}, {hi}] "
                        f"(point {PREREG['point']}, error {decided-PREREG['point']:+d}), so the "
                        f"forecasting procedure survives this round." if inside else
                        f" ⛔ AND WORLD C: {decided} is OUTSIDE the pre-registered [{lo}, {hi}], so "
                        f"the FORECASTING PROCEDURE failed, not merely the number — three "
                        f"consecutive forecasts in this arc have now missed.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 binder x {len(targets)} rounds x every glob site + "
          f"{len(already)} reproduction checks + 4 controls. Every outcome printed.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "local_binding.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "prereg": PREREG, "measured_decided": decided, "inside_interval": inside,
        "forecast_record": [{"forecast": l, "predicted": pr, "measured": me, "error": me - pr}
                            for l, pr, me in hist],
        "forecast_record_null": {"n": len(hist), "all_same_sign": same,
                                 "p_under_symmetric_null": pnull,
                                 "reading": "a direction, not an established bias"},
        "counts": dict(cnt),
        "per_round": {n: {"verdict": v, "notes": notes} for n, (v, notes) in res.items()},
        "r656_folds_uncovered": [n for n, _ in folds],
        "check258": ("R656's NEXT said '12 bind a single name' -- it is 13, and I read it off a "
                     "grid printing notes[:1]. The name list was also wrong (`s`,`st` came from "
                     "R655's SHAPE table; `sub` was omitted). And 'the previous forecast was "
                     "wrong by 11' names an error magnitude by reusing the forecast's VALUE."),
        "impossible": ("a local assigned from a parameter needs the call graph, absent across "
                       "standalone scripts; a local rebound from runtime data is not static."),
    }, indent=2))
    print(f"\n  wrote {out / 'local_binding.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
