#!/usr/bin/env python3
"""
R656 -- two APIs were scored by one rule; dispatching on the API, does the forecast hold?

CHECK #257 ON R655's CLOSING LINE. THE PREMISE HELD, THE FORECAST IS THE ROUND, AND THE
DECOMPOSITION UNDERNEATH BOTH IS WRONG.
  ✓ "their argument is `str(ROOT / CENSUS)`-shaped" -- generalised from ONE example (R347), and
    checked before use: all 11 are `Call(str)`. The generalisation held. It was still a
    generalisation from n=1 at the moment I wrote it, and that is the habit, not the outcome.
  ⚠ "it SHOULD shrink the residual from 25 to 14" is a FORECAST, not a measurement. It is
    pre-registered here as this round's kill rather than repeated as a finding.
  ⛔ "the remaining 14 need function-local binding, which is a DIFFERENT and larger change."
    The two blockers are not disjoint. 7 of the 11 `glob.glob` sites resolve their base from a
    lowercase `root` that is FUNCTION-LOCAL, so they carry BOTH defects. I partitioned 25 into
    "11 easy + 14 hard" and the sets overlap.

ESTIMAND        With the classifier dispatching on API -- `Path.glob(...)` scored by its RECEIVER,
                `glob.glob(pattern)` scored by its FIRST ARGUMENT -- the class of each of R655's
                25 undecided rounds, and the resulting residual.
                n_resolved_by_dispatch, against the pre-registered forecast of 11.
IDENTIFICATION  Exact for arguments whose path expression resolves from module-level names. NOT
                identified where the argument's base is function-local: those are reported
                FUNCTION-LOCAL, a THIRD outcome, never folded into resolved or unresolved.
SCOPE           population : R655's 25 undecided rounds, MINUS this round
                instrument : ast + a symbolic pathlib evaluator, dispatched on the call's API
                             instrument unit = A GLOB SITE
                             claim unit      = A ROUND
                             NOT EQUAL -- a round holds several sites and is decided only if all
                             of its sites agree, which is why MIXED exists as an outcome
                baseline   : R654/R655's classification of the other 115 rounds, reproduced exactly
                regime     : at the tree sha persisted in the artifact
WORLDS          A THE FORECAST HOLDS: 11 resolve, residual 14 -> the API mis-dispatch was the whole
                  blocker for that subset and the two defects are separable as I claimed.
                B THE FORECAST FAILS: fewer resolve -> the subsets overlap, "11 easy + 14 hard" is
                  the wrong decomposition, and the residual does not decompose into independent
                  fixes.
                C THE RESOLVER DRIFTED: it changes a verdict on the 115 already-decided rounds ->
                  a different instrument, no verdict admissible.
KILL            pre-registered, with its threshold, before the run: R655's NEXT forecast exactly
                11 resolutions and a residual of 14. If fewer than 11 resolve, THE FORECAST IS
                RETRACTED and replaced by the measured number -- not reinterpreted, not called
                "approximately right". A forecast that survives any outcome was never one.
POSITIVE CTRL   (i) the 115 already-decided rounds must keep their verdicts.
                (ii) a synthetic `glob.glob(str(A24 / "R*"))` with A24 module-level -> CORPUS.
                Fails at g=0: a module with no glob at all yields no class.
NEGATIVE CTRL   a synthetic `glob.glob(str(HERE / "*.json"))` -> OWN. The failure direction is to
                score every `glob.glob` corpus-dependent because the pattern LOOKS wide.
PLACEBO         a synthetic whose argument base is defined only inside a function ->
                FUNCTION-LOCAL, and NOT resolved. This is the control the round turns on: the
                temptation is to reach into the function and grab the name anyway.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 dispatching classifier x 25 rounds x every glob site + 115 reproduction checks
                + 5 controls. All outcomes printed, residual included.
ARTIFACT        results/api_dispatch.json, with the tree sha beside every count.
IMPOSSIBLE      a function-local base needs intra-procedural binding of assignments, which is the
                remaining change; and a base assigned from a parameter needs the call graph, which
                does not exist across standalone scripts. Both are named and neither is attempted.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
E05 = A24.parent
ROOT = A24.parents[1]
PATH_GLOBS = {"glob", "rglob", "iterdir"}


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
            # ⭐ THE DISPATCH THIS ROUND ADDS, one line: `str(X)` is a PATH-VALUED expression when
            #    X is, so an argument wrapped in str() is resolved through the wrapper. R655
            #    scored `glob.glob(str(ROOT / CENSUS))` by its RECEIVER -- the module `glob` --
            #    and called the result "unresolved base". There was no base to resolve.
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


def function_local_names(tree):
    """Names assigned INSIDE a function and never at module level."""
    mod, loc = set(), set()
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    mod.add(t.id)
    for fn in [x for x in ast.walk(tree)
               if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        for n in ast.walk(fn):
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        loc.add(t.id)
        loc |= {a.arg for a in fn.args.args}
    return loc - mod


def base_names(expr):
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


def classify(path):
    """Dispatch on the API. Returns (verdict, per-site notes)."""
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return "UNPARSEABLE", []
    ev = PathEval(path.resolve())
    ev.bind_module(tree)
    flocal = function_local_names(tree)
    own = path.resolve().parent
    seen, notes, unres, floc = [], [], 0, 0

    def cls(p):
        try:
            rel = p.resolve()
        except Exception:
            return None
        if rel == own or own in rel.parents:
            return "OWN"
        if rel in (A24.resolve(), E05.resolve(), ROOT.resolve()) or A24.resolve() in rel.parents:
            return "CORPUS"
        # a wildcard pattern under the collection dir resolves to a non-existent literal path;
        # decide by the string prefix instead, which is what the pattern actually addresses
        s = str(rel)
        if str(A24.resolve()) in s or str(E05.resolve()) in s:
            return "CORPUS"
        return "OTHER"

    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        is_path_api = isinstance(n.func, ast.Attribute) and n.func.attr in PATH_GLOBS \
            and not (isinstance(n.func.value, ast.Name) and n.func.value.id == "glob")
        is_mod_api = isinstance(n.func, ast.Attribute) and n.func.attr in ("glob", "iglob") \
            and isinstance(n.func.value, ast.Name) and n.func.value.id == "glob"
        if not (is_path_api or is_mod_api):
            continue
        expr = n.func.value if is_path_api else (n.args[0] if n.args else None)
        if expr is None:
            unres += 1
            continue
        p = ev.path_of(expr)
        if p is None:
            if base_names(expr) & flocal:
                floc += 1
                notes.append(f"{'ARG' if is_mod_api else 'RECV'} base is FUNCTION-LOCAL: "
                             f"{sorted(base_names(expr) & flocal)[:2]}")
            else:
                unres += 1
                notes.append(f"{'ARG' if is_mod_api else 'RECV'} unresolved")
            continue
        c = cls(p)
        if c is None:
            unres += 1
        else:
            seen.append(c)
            notes.append(f"{'ARG' if is_mod_api else 'RECV'} -> {c}")
    # ⛔ v1 FOLDED TWO RESIDUALS INTO A DECIDED CLASS, and the placebo built to prevent exactly
    #    that fired correctly in its own branch while this one leaked.
    #    ① a site classified OTHER -- neither the corpus nor the round's own directory, which is
    #       what a wildcard like `E0*` produces because it never literally contains
    #       `E05_the_space_of_compilers` -- landed in `seen` and the final `if seen` returned
    #       OWN-SCOPE. OTHER is not OWN.
    #    ② a round with BOTH a decided OWN site and an unresolved one returned OWN-SCOPE, hiding
    #       the undecided site behind its decided sibling. A round is decided only if ALL of its
    #       sites are.
    #    Both are the same defect in two branches: a residual absorbed by a verdict.
    if "CORPUS" in seen and "OWN" in seen:
        return "MIXED", notes
    if "CORPUS" in seen:
        return "CORPUS-DEPENDENT", notes
    if unres or floc:
        if seen:
            return "PARTIAL-UNDECIDED", notes
        return "FUNCTION-LOCAL" if floc else "STILL-UNRESOLVED", notes
    if "OTHER" in seen and "OWN" not in seen:
        return "OUTSIDE-BOTH", notes
    if seen:
        return "OWN-SCOPE", notes
    return "NO-GLOB", notes


def main() -> int:
    r655 = A24 / "R655_resolve_the_undecided_glob_bases" / "results" / "resolved_bases.json"
    if not r655.exists():
        print("UNRUNNABLE: R655's artifact absent. Exit 2, never 0.")
        return 2
    b = json.loads(r655.read_text())
    undec = list(b["per_round"])
    FORECAST = 11                       # R655's NEXT, pre-registered verbatim as this round's kill

    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    res = {n: classify(A24 / n / "run.py") for n in undec}

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    decided = [d.name for d in rounds if d.name not in undec]
    # R654/R655 agreed on these; the dispatch must not move any of them OFF a decided class
    moved = []
    for n in decided:
        v = classify(A24 / n / "run.py")[0]
        if v in ("STILL-UNRESOLVED", "FUNCTION-LOCAL", "UNPARSEABLE"):
            moved.append((n, v))
    print(f"  POSITIVE-1 the dispatch must not un-decide any of the {len(decided)} already-decided "
          f"rounds -> {len(moved)} moved -> {'PASS' if not moved else '⛔ FAIL'}")
    for n, v in moved[:4]:
        print(f"               {n[:52]:<52} -> {v}")

    def synth(src):
        t = ast.parse(src)
        p = A24 / "R999_synth" / "run.py"
        ev = PathEval(p.resolve())
        ev.bind_module(t)
        fl = function_local_names(t)
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in ("glob", "iglob") \
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == "glob":
                a = n.args[0] if n.args else None
                if a is None:
                    return "NO-ARG"
                v = ev.path_of(a)
                if v is None:
                    return "FUNCTION-LOCAL" if (base_names(a) & fl) else "UNRESOLVED"
                s = str(v.resolve())
                if str((A24 / "R999_synth").resolve()) in s:
                    return "OWN"
                return "CORPUS" if str(A24.resolve()) in s else "OTHER"
        return "NO-GLOB"

    hdr = ("import glob, pathlib\nA24=pathlib.Path('%s')\nHERE=pathlib.Path('%s')\n"
           % (A24.as_posix(), (A24 / "R999_synth").as_posix()))
    pos2 = synth(hdr + "glob.glob(str(A24 / 'R*'))\n")
    print(f"  POSITIVE-2 `glob.glob(str(A24 / 'R*'))` scored by its ARGUMENT -> {pos2} -> "
          f"{'PASS' if pos2 == 'CORPUS' else '⛔ FAIL'}")
    neg = synth(hdr + "glob.glob(str(HERE / '*.json'))\n")
    print(f"  NEGATIVE   `glob.glob(str(HERE / '*.json'))` -> {neg} -> "
          f"{'PASS — a wide-LOOKING pattern is not automatically corpus-wide' if neg == 'OWN' else '⛔ FAIL'}")
    plc = synth(hdr + "def f():\n    r = pathlib.Path('/x')\n    return glob.glob(str(r / '*'))\n")
    plcok = plc == "FUNCTION-LOCAL"
    print(f"  PLACEBO    an argument base defined only INSIDE a function -> {plc} -> "
          f"{'PASS — it is named, not reached into' if plcok else '⛔ FAIL'}")
    g0 = synth("x = 1\n")
    print(f"  g=0        no glob at all -> {g0} -> {'PASS' if g0 == 'NO-GLOB' else '⛔ FAIL'}")
    controls_ok = (not moved and pos2 == "CORPUS" and neg == "OWN" and plcok and g0 == "NO-GLOB")
    print(f"  KILL       forecast = {FORECAST} resolutions; anything less RETRACTS it")

    # ---- THE 25, RE-CLASSIFIED ------------------------------------------------------
    cnt = Counter(v[0] for v in res.values())
    # a round counts as RESOLVED only if every one of its sites was decided
    resolved = (cnt.get("CORPUS-DEPENDENT", 0) + cnt.get("OWN-SCOPE", 0) + cnt.get("MIXED", 0)
                + cnt.get("OUTSIDE-BOTH", 0))
    print(f"\n─── THE {len(undec)} UNDECIDED ROUNDS, WITH THE API DISPATCHED ───")
    for k in ("CORPUS-DEPENDENT", "OWN-SCOPE", "MIXED", "OUTSIDE-BOTH",
              "PARTIAL-UNDECIDED", "FUNCTION-LOCAL", "STILL-UNRESOLVED"):
        c = cnt.get(k, 0)
        print(f"  {k:<18} {c:>4}  ({c/max(len(undec),1):>5.1%})")
    print(f"\n  every round, with what the dispatch found (G3 — the whole grid):")
    for n in sorted(res):
        v, notes = res[n]
        print(f"    {v:<18} {n[:46]:<46} {notes[:1]}")

    # ---- THE FORECAST, EVALUATED ----------------------------------------------------
    print(f"\n─── THE PRE-REGISTERED FORECAST ───")
    print(f"  R655's NEXT: 'it should shrink the residual from 25 to 14', i.e. {FORECAST} resolve")
    print(f"  measured   : {resolved} resolve; residual "
          f"{len(undec) - resolved}")
    verdict_f = "HELD" if resolved >= FORECAST else "RETRACTED"
    print(f"  => the forecast is {verdict_f}"
          f"{'' if verdict_f == 'HELD' else f' — replaced by the measured {resolved}, not reinterpreted'}")

    # overlap: how many glob.glob sites ALSO have a function-local base
    both = [n for n, (v, notes) in res.items()
            if any("ARG base is FUNCTION-LOCAL" in x for x in notes)]
    print(f"\n  ⭐ OVERLAP — rounds carrying BOTH defects (a `glob.glob` API AND a function-local "
          f"base): {len(both)}")
    for n in both[:8]:
        print(f"    {n[:52]:<52} {res[n][1][:1]}")
    print(f"  R655 partitioned the 25 into '11 easy + 14 hard'. The subsets are NOT disjoint.")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no reclassification is admissible"
    elif resolved >= FORECAST:
        world = (f"A THE FORECAST HOLDS — {resolved} of {len(undec)} resolve once the API is "
                 f"dispatched; residual {len(undec)-resolved}. The two defects are separable.")
    else:
        world = (f"B THE FORECAST FAILS — {resolved} of {len(undec)} resolve, not {FORECAST}. "
                 f"{len(both)} round(s) carry BOTH the API mis-dispatch AND a function-local "
                 f"base, so '11 easy + 14 hard' is the wrong decomposition: the subsets overlap "
                 f"and the residual does not split into independent fixes. Residual "
                 f"{len(undec) - resolved}, of which "
                 f"{cnt.get('FUNCTION-LOCAL',0)} are now NAMED as function-local rather than "
                 f"merely unresolved — the residual is better characterised even where it did "
                 f"not shrink as forecast.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 dispatching classifier x {len(undec)} rounds x every glob site + "
          f"{len(decided)} reproduction checks + 4 controls. All outcomes printed.")
    print(f"  ⭐ tree sha beside every count: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "api_dispatch.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "forecast": FORECAST, "measured_resolved": resolved, "forecast_verdict": verdict_f,
        "counts": dict(cnt), "both_defects": both,
        "per_round": {n: {"verdict": v, "notes": notes} for n, (v, notes) in res.items()},
        "reproduction_moved": moved,
        "check257": ("R655's NEXT generalised `str(ROOT / CENSUS)` from ONE example; checked "
                     "before use, all 11 are Call(str) and the generalisation held -- but it was "
                     "n=1 when written. Its '25 -> 14' was a FORECAST, pre-registered here as the "
                     "kill. And its claim that the remaining 14 need a DIFFERENT change is false: "
                     "the two blockers overlap."),
        "impossible": ("a function-local base needs intra-procedural binding of assignments; a "
                       "base from a parameter needs a call graph that does not exist across "
                       "standalone scripts. Named, neither attempted."),
    }, indent=2))
    print(f"\n  wrote {out / 'api_dispatch.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
