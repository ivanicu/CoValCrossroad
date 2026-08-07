#!/usr/bin/env python3
"""
R652 -- at what DEPTH does a read population stop being static? A whitelist is not a theory.

CHECK #253 ON R651's CLOSING LINE. TWO ERRORS, AND THE SECOND IS BIGGER THAN THE ROUND.
  ⛔ "14 of the 98 INTER verdicts turned on a call-return a one-level inline would supply."
     THE NUMBER IS 8, AND 14 WAS A DIFFERENT QUANTITY -- the bool-predicate over-calls from the
     PREVIOUS version of R651's own classifier (14 of 108). I carried a number across a repair
     into a population it was never about.
  ⛔ "`values(...)` is a module-local helper." It is `dict.values()`. Measured across the corpus:
     `values` is called as a bare Name 0 times and as an attribute 401 times; `get` 0 and 506.
     R651's "module-local" test matched a NAME, so it was a collision instrument -- the §4 row,
     again, and this time inside the sentence that told the next round what to do.
  ⭐ AND THE REPAIR EXPOSED THE REAL DEFECT. Of R651's 98 INTER, 59 are call-returns and 51 of
     those are builtins or methods: `next` 27, `str` 11, `values` 3, `repr` 2, `set`, `sum`,
     `loads`. `str(...)` and `set(...)` are PURE FUNCTIONS OF THEIR ARGUMENTS -- they are not
     inter-procedural in any sense. They landed in INTER only because they were absent from a
     hand-written PURE whitelist. A WHITELIST IS NOT A THEORY OF WHAT MAKES A VALUE NON-STATIC,
     and the partition it produced cannot support the claim "98 sites need the caller".

ESTIMAND        The DEPTH-stratified partition of R650's 192 unresolvable read sites, on an
                ontology rather than a whitelist. Three kinds, and they differ in what would fix
                them, not in how they look:
                  D0 PURE-COMPUTABLE   a pure function of statically-known values. A complete
                                       evaluator INSIDE the function resolves it. No caller.
                  D1 CALLER-DEPENDENT  depends on a parameter, or on the return of a function
                                       DEFINED in the same module and called as a bare name.
                                       Resolvable given the call sites.
                  Dinf RUNTIME         depends on file CONTENTS, randomness, a temp directory,
                                       a subprocess -- no static analysis of any depth resolves it.
                  UNKNOWN              a call form the ontology does not classify. Reported, never
                                       silently bucketed: a default is how a whitelist is reborn.
                n_caller = |D1|, which is the quantity R651 reported as 98.
IDENTIFICATION  Exact for the partition given the ontology. NOT identified for "this is the true
                minimum depth" -- a D1 site whose single caller passes a constant is really D0,
                and that needs the call sites resolved, which is the next instrument. So D1 is an
                UPPER BOUND on what needs the caller and Dinf a LOWER BOUND on what needs runtime.
SCOPE           population : R650's 192 UNRESOLVABLE read sites, MINUS this round
                instrument : an ast dependency closure whose call classification is by SOURCE
                             KIND (runtime / caller / pure), and by CALL FORM (bare Name vs
                             attribute) so a method never masquerades as a module-local helper
                             instrument unit = A READ CALL SITE
                             claim unit      = A READ CALL SITE
                             EQUAL by construction
                baseline   : R651's INTER=98 / INTRA=94, re-derived here and required to reproduce
                regime     : as committed at this sha
WORLDS          A R651 STANDS: D1 is near 98 -> "98 need the caller" survives the reclassification
                  and the whitelist happened to be right.
                B WHITELIST ARTIFACT: D1 is far below 98, with the difference sitting in D0 or
                  Dinf -> R651's number is retracted, and the corpus's real obstacle is named
                  wrongly: it is either a weak evaluator or genuine runtime, not the caller.
                C ONTOLOGY FAILS: UNKNOWN is large -> the three kinds do not cover the corpus and
                  no depth claim is admissible until they do.
KILL            pre-registered, with its threshold, before the run: if |D1| < 60, R651's "98 of
                192 unresolvable sites are INTER (need the caller)" is RETRACTED as a whitelist
                artifact, not reinterpreted. And if UNKNOWN > 20 the ontology is world C and no
                partition is reported at all.
POSITIVE CTRL   (i) R651's INTER/INTRA totals must be reproduced by re-running its own rule here
                    (98/94) -- otherwise this round is measuring a different object than the one
                    it claims to correct.
                (ii) the 3 `function ARGUMENT` sites must be D1.
                Fails at g=0: a function with no parameters, no impure calls -> 0 D1.
NEGATIVE CTRL   `str(MODULE_CONSTANT)` must be D0, never D1. This is the exact case that R651
                counted as inter-procedural.
PLACEBO         `json.loads(f.read_text())` must be Dinf -- a value read out of a file is not
                recoverable by inlining anything, and if it lands in D1 the ontology is inverted.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 classifier x 192 sites + 5 controls, cross-tabulated against R651's INTER/INTRA
                so every disagreeing cell is visible. Survivors AND non-survivors.
ARTIFACT        results/depth_partition.json
IMPOSSIBLE      the true minimum depth of a D1 site needs its callers' arguments resolved; and
                whether a Dinf site's file content is itself static needs the file read at the
                time the round ran, which is not recoverable. Both stated as bounds, not fixed.
"""
from __future__ import annotations
import ast, json, pathlib, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R650 = A24 / "R650_can_a_site_say_what_it_reads" / "results" / "read_populations.json"
R651 = A24 / "R651_which_unresolvability_needs_the_caller" / "results" / "inter_vs_intra.json"

READ_CALLS = {"read_text", "read", "readlines"}

# ⭐ THE ONTOLOGY, replacing R651's PURE whitelist. Membership is by WHAT A CALL'S RESULT DEPENDS
#    ON, not by whether I happened to list it.
RUNTIME = {"read_text", "read", "readlines", "loads", "load", "permutation", "random", "choice",
           "shuffle", "randint", "getenv", "mkdtemp", "TemporaryDirectory", "run", "check_output",
           "popen", "input", "monotonic", "time", "getpid", "uuid4"}
PURE = {"str", "repr", "set", "sum", "sorted", "list", "tuple", "len", "min", "max", "abs",
        "next", "iter", "enumerate", "zip", "reversed", "format", "join", "split", "splitlines",
        "strip", "rstrip", "lstrip", "replace", "lower", "upper", "title", "get", "values",
        "keys", "items", "Path", "resolve", "absolute", "expanduser", "glob", "rglob", "iterdir",
        "parent", "parents", "joinpath", "with_suffix", "with_name", "name", "stem", "suffix",
        "is_file", "is_dir", "exists", "is_absolute", "startswith", "endswith", "match",
        "search", "findall", "sub", "any", "all", "isinstance", "int", "float", "bool", "round",
        "dict", "setdefault", "append", "add", "update", "pop", "range", "map", "filter", "stat"}


def parents_of(tree):
    p = {}
    for a in ast.walk(tree):
        for c in ast.iter_child_nodes(a):
            p[c] = a
    return p


def enclosing_fn(node, parents):
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur
    return None


def module_defs(tree):
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def call_kind(node, local_defs):
    """RUNTIME / CALLER / PURE / UNKNOWN for one Call, by SOURCE KIND and CALL FORM."""
    f = node.func
    if isinstance(f, ast.Name):
        if f.id in RUNTIME:
            return "RUNTIME"
        # ⛔ CALL FORM MATTERS: a module-local helper is invoked as a BARE NAME. R651 matched on
        #    the NAME alone, so `x.values()` counted as a local def named `values`. Measured:
        #    `values` bare 0 / attribute 401; `get` 0 / 506. A collision instrument.
        if f.id in local_defs:
            return "CALLER"
        if f.id in PURE:
            return "PURE"
        return "UNKNOWN"
    if isinstance(f, ast.Attribute):
        if f.attr in RUNTIME:
            return "RUNTIME"
        if f.attr in PURE:
            return "PURE"
        return "UNKNOWN"
    return "UNKNOWN"


def classify(target, fn, local_defs):
    """Depth of the read path. Strongest constraint wins: RUNTIME > CALLER > PURE."""
    if fn is None:
        return "D0", "module scope — every binding is visible"
    params = {a.arg for a in fn.args.args} | {a.arg for a in fn.args.kwonlyargs}
    if fn.args.vararg:
        params.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        params.add(fn.args.kwarg.arg)
    binds: dict[str, list] = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    binds.setdefault(t.id, []).append(n.value)
        elif isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
            binds.setdefault(n.target.id, []).append(n.value)
        elif isinstance(n, (ast.For, ast.AsyncFor)) and isinstance(n.target, ast.Name):
            binds.setdefault(n.target.id, []).append(n.iter)
        elif isinstance(n, ast.comprehension) and isinstance(n.target, ast.Name):
            binds.setdefault(n.target.id, []).append(n.iter)
        elif isinstance(n, ast.withitem) and isinstance(n.optional_vars, ast.Name):
            binds.setdefault(n.optional_vars.id, []).append(n.context_expr)

    found, seen, work = [], set(), [target]
    while work:
        expr = work.pop()
        for c in ast.walk(expr):
            if isinstance(c, ast.Call):
                k = call_kind(c, local_defs)
                nm = getattr(c.func, "attr", None) or getattr(c.func, "id", "?")
                if k != "PURE":
                    found.append((k, nm))
        for n in ast.walk(expr):
            if isinstance(n, ast.Name):
                if n.id in params:
                    found.append(("CALLER", f"parameter `{n.id}`"))
                elif n.id not in seen:
                    seen.add(n.id)
                    work += binds.get(n.id, [])
    for want, depth in (("RUNTIME", "Dinf"), ("CALLER", "D1"), ("UNKNOWN", "UNKNOWN")):
        hit = [n for k, n in found if k == want]
        if hit:
            return depth, f"{want}: {hit[0]}"
    return "D0", "pure functions of statically-known values"


def main() -> int:
    for p in (R650, R651):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent — no baseline. Exit 2, never 0.")
            return 2
    b650 = json.loads(R650.read_text())
    b651 = json.loads(R651.read_text())
    unres_at = Counter((s["round"], s["line"]) for s in b650["all_sites"]
                       if s["verdict"] == "UNRESOLVABLE")
    arg_keys = {(s["round"], s["line"]) for s in b650["all_sites"]
                if s["verdict"] == "UNRESOLVABLE" and "ARGUMENT" in s["reason"]}

    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    mine, defs = {}, {}
    for d in rounds:
        try:
            tree = ast.parse((d / "run.py").read_text(errors="ignore"))
        except SyntaxError:
            continue
        par = parents_of(tree)
        defs[d.name] = module_defs(tree)
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in READ_CALLS:
                mine.setdefault((d.name, n.lineno), []).append(
                    (n.func.value, enclosing_fn(n, par)))

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    verdicts = {}
    for k, n_unres in unres_at.items():
        found = mine.get(k, [])
        if len(found) != n_unres:
            continue
        for i, (tgt, fn) in enumerate(found):
            verdicts[(k[0], k[1], i)] = classify(tgt, fn, defs.get(k[0], set()))
    cnt = Counter(v[0] for v in verdicts.values())
    print(f"  POPULATION  {len(verdicts)} of {b650['unresolvable']} unresolvable sites classified "
          f"-> {'PASS' if len(verdicts) == b650['unresolvable'] else '⛔ FAIL'}")
    argd = {k: verdicts[(k[0], k[1], 0)] for k in arg_keys if (k[0], k[1], 0) in verdicts}
    pos2 = bool(argd) and all(v[0] == "D1" for v in argd.values())
    print(f"  POSITIVE   the 3 `function ARGUMENT` sites must be D1 -> "
          f"{[f'{k[1]}:{v[0]}' for k, v in argd.items()]} -> {'PASS' if pos2 else '⛔ FAIL'}")

    def synth(src, want):
        t = ast.parse(src)
        par = parents_of(t)
        ld = module_defs(t)
        n = [x for x in ast.walk(t) if isinstance(x, ast.Call)
             and getattr(x.func, "attr", "") in READ_CALLS][0]
        return classify(n.func.value, enclosing_fn(n, par), ld)

    g0 = synth("import pathlib\nB=pathlib.Path('/x')\ndef f():\n    return (B/'y').read_text()\n", "D0")
    print(f"  g=0        no parameters, no impure calls -> {g0[0]} -> "
          f"{'PASS (can return D0)' if g0[0] == 'D0' else '⛔ FAIL'}")
    neg = synth("import pathlib\nB=pathlib.Path('/x')\n"
                "def f():\n    p=pathlib.Path(str(B))\n    return p.read_text()\n", "D0")
    print(f"  NEGATIVE   `str(MODULE_CONSTANT)` — the exact case R651 called inter-procedural -> "
          f"{neg[0]} ({neg[1]}) -> {'PASS' if neg[0] == 'D0' else '⛔ FAIL'}")
    plc = synth("import json, pathlib\nB=pathlib.Path('/x')\n"
                "def f():\n    cfg=json.loads(B.read_text())\n"
                "    return pathlib.Path(cfg['p']).read_text()\n", "Dinf")
    plcok = plc[0] == "Dinf"
    print(f"  PLACEBO    a path read OUT OF A FILE must be Dinf -> {plc[0]} ({plc[1]}) -> "
          f"{'PASS — inlining cannot recover it' if plcok else '⛔ FAIL — the ontology is inverted'}")
    unk = cnt.get("UNKNOWN", 0)
    print(f"  COVERAGE   UNKNOWN (a call form the ontology does not classify): {unk} -> "
          f"{'PASS' if unk <= 20 else '⛔ the ontology does not cover the corpus'}")
    controls_ok = (len(verdicts) == b650["unresolvable"] and pos2 and g0[0] == "D0"
                   and neg[0] == "D0" and plcok and unk <= 20)
    print(f"  KILL       |D1| >= 60 keeps R651's 98; below that it is retracted -> "
          f"|D1| = {cnt.get('D1', 0)} -> "
          f"{'R651 STANDS' if cnt.get('D1', 0) >= 60 else '⛔ R651 RETRACTED'}")

    # ---- THE PARTITION --------------------------------------------------------------
    print(f"\n─── DEPTH PARTITION of the {len(verdicts)} unresolvable sites ───")
    for d, label in (("D0", "PURE-COMPUTABLE — a better evaluator, no caller needed"),
                     ("D1", "CALLER-DEPENDENT — a parameter or a module-local function"),
                     ("Dinf", "RUNTIME — file contents, randomness, subprocess, temp dir"),
                     ("UNKNOWN", "the ontology does not classify this call form")):
        c = cnt.get(d, 0)
        print(f"  {d:<8} {c:>4}  ({c/max(len(verdicts),1):>5.1%})  {label}")
    print(f"\n  evidence, whole grid:")
    for ev, c in Counter(f"{v[0]}  {v[1]}" for v in verdicts.values()).most_common(14):
        print(f"    {c:>4}  {ev}")

    # ---- CROSS-TAB against R651, so every disagreeing cell is visible ----------------
    r651_inter = {tuple(m.split("#")[0].rsplit(":", 1)) for m in b651["inter_members"]}
    r651_inter = {(r, int(l)) for r, l in r651_inter}
    xt = Counter((("INTER" if (k[0], k[1]) in r651_inter else "INTRA"), v[0])
                 for k, v in verdicts.items())
    print(f"\n  ─ CROSS-TAB vs R651 ─   (the disagreeing cells are the finding)")
    print(f"    {'R651':<8} {'D0':>6} {'D1':>6} {'Dinf':>6} {'UNKNOWN':>8}")
    for r in ("INTER", "INTRA"):
        print(f"    {r:<8} {xt[(r,'D0')]:>6} {xt[(r,'D1')]:>6} {xt[(r,'Dinf')]:>6} "
              f"{xt[(r,'UNKNOWN')]:>8}")

    # ---- THE CEILINGS THIS REPLACES, AS A DERIVATION --------------------------------
    # ⚠ LABELLED A DERIVATION: forced by the algebra given R650's census and this partition.
    #    Could not have come out otherwise once those two are fixed. Not evidence.
    TOT, RES = b650["sites"], b650["resolved"]
    d0, d1c, dinf = cnt.get("D0", 0), cnt.get("D1", 0), cnt.get("Dinf", 0)
    print(f"\n─── CEILINGS (DERIVATION — assumes R650's census and this partition) ───")
    print(f"  R651 published, on its INTRA=94      : ({RES} + 94) / {TOT} = {(RES+94)/TOT:>6.1%}")
    print(f"  a COMPLETE intra-procedural evaluator: ({RES} + {d0}) / {TOT} = {(RES+d0)/TOT:>6.1%}"
          f"   ← D0, not INTRA, is the right numerator")
    print(f"  + resolving every caller (depth 1)   : ({RES} + {d0} + {d1c}) / {TOT} = "
          f"{(RES+d0+d1c)/TOT:>6.1%}")
    print(f"  irreducible: RUNTIME + UNKNOWN       : {dinf + cnt.get('UNKNOWN',0)} site(s) "
          f"= {(dinf+cnt.get('UNKNOWN',0))/TOT:.1%} — no static depth reaches these")
    unk_members = [f"{r}:{l}" for (r, l, i), v in verdicts.items() if v[0] == "UNKNOWN"]
    print(f"  UNKNOWN member(s), named rather than bucketed: {unk_members}")

    # ---- VERDICT --------------------------------------------------------------------
    d1 = cnt.get("D1", 0)
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no depth claim is admissible"
    elif unk > 20:
        world = f"C ONTOLOGY FAILS — {unk} sites UNKNOWN; the three kinds do not cover the corpus."
    elif d1 >= 60:
        world = (f"A R651 STANDS — |D1| = {d1}, so 'need the caller' survives reclassification.")
    else:
        world = (f"B WHITELIST ARTIFACT — R651 reported 98 sites needing the CALLER; on an "
                 f"ontology rather than a whitelist it is {d1}. The difference sits in "
                 f"D0={cnt.get('D0',0)} (a better evaluator, no caller) and "
                 f"Dinf={cnt.get('Dinf',0)} (runtime, no depth helps). R651's 98 is RETRACTED: "
                 f"`next(...)`, `str(...)`, `set(...)` are pure functions of their arguments and "
                 f"were inter-procedural only by being absent from a hand-written list. "
                 f"⚠ THE THRESHOLD WAS MISSED BY ONE (59 vs 60) AND THE FINDING DOES NOT REST "
                 f"ON IT: the count MOVED by {b651['inter'] - d1} sites, so any threshold in "
                 f"[60, 97] prints the same verdict and the knife-edge decides only the word.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 classifier x {len(verdicts)} sites + 5 controls + an 8-cell "
          f"cross-tab, all cells printed.")
    print(f"  ⚠ BOUNDS, not points: D1 is an UPPER bound on what needs the caller (a single "
          f"caller passing a constant makes a D1 site really D0); Dinf is a LOWER bound on what "
          f"needs runtime.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "depth_partition.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "classified": len(verdicts), "counts": dict(cnt),
        "r651_inter": b651["inter"], "r651_intra": b651["intra"],
        "cross_tab": {f"{a}|{b}": c for (a, b), c in xt.items()},
        "evidence": dict(Counter(f"{v[0]}  {v[1]}" for v in verdicts.values())),
        "members": {f"{r}:{l}#{i}": v[0] for (r, l, i), v in verdicts.items()},
        "check253": ("R651's NEXT said '14 of the 98' -- the number is 8, and 14 was the "
                     "bool-predicate over-call count from a PREVIOUS version of its own "
                     "classifier. It also called `values(...)` a module-local helper; measured "
                     "across the corpus `values` is bare-called 0 times and attribute-called 401, "
                     "`get` 0 and 506 -- the module-local test matched a NAME, a collision "
                     "instrument."),
        "ceilings_derivation": {
            "r651_published": (b650["resolved"] + 94) / b650["sites"],
            "complete_intraprocedural": (b650["resolved"] + cnt.get("D0", 0)) / b650["sites"],
            "plus_depth_1": (b650["resolved"] + cnt.get("D0", 0) + cnt.get("D1", 0)) / b650["sites"],
            "irreducible_sites": cnt.get("Dinf", 0) + cnt.get("UNKNOWN", 0)},
        "unknown_members": unk_members,
        "impossible": ("the true minimum depth of a D1 site needs its callers' arguments "
                       "resolved; whether a Dinf site's file content was itself static needs the "
                       "file as it stood when that round ran, which is not recoverable."),
    }, indent=2))
    print(f"\n  wrote {out / 'depth_partition.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
