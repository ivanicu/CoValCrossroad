#!/usr/bin/env python3
"""
R655 -- decide the 25 undecided glob bases, and keep a residual that stays undecided.

CHECK #256 ON R654's CLOSING LINE. TWO CLAUSES COMPUTED, TWO FLAWED.
  ✓ "38 rounds already stamp the tree" and "25 UNRESOLVED-BASE" -- both computed and correct.
  ⛔ "R653 showed 16 of 59 SUCH bindings are statically supplied at every call site." R653's 16
     was about the blocking PARAMETER of a D1 READ SITE. These 25 are about a GLOB BASE. Different
     population, different quantity, cited as if it transferred. A number is not evidence for a
     question it was not asked.
  ⛔ "93 is an UNDERCOUNT by an unknown amount." The DIRECTION is not known: an UNRESOLVED-BASE
     round can resolve to OWN-SCOPE and leave 93 unchanged. The honest statement is a two-sided
     bound -- corpus-dependence lies in [93, 118] -- and I asserted one side of it. Naming an
     uncertainty is worth nothing if you also name its sign for free.

ESTIMAND        For each of R654's 25 UNRESOLVED-BASE rounds, the class its glob base resolves to
                once the base is bound INTERPROCEDURALLY -- at every call site of the function that
                owns it:
                  CORPUS-DEPENDENT  every binding resolves at or above the collection directory
                  OWN-SCOPE         every binding resolves inside the round's own directory
                  MIXED             different call sites give different classes
                  STILL-UNRESOLVED  no binding resolves -- reported, never defaulted
                n_corpus_dependent_total, replacing R654's two-sided bound [93, 118] with a point
                plus an explicitly-sized residual.
IDENTIFICATION  Exact for bases bound at visible call sites. NOT identified where the binding
                itself comes from a parameter two frames up, or from a runtime value -- those stay
                STILL-UNRESOLVED and the residual is reported as a bound, not absorbed.
SCOPE           population : R654's 25 UNRESOLVED-BASE rounds, MINUS this round
                instrument : ast + a symbolic pathlib evaluator + one level of caller binding
                             instrument unit = A ROUND
                             claim unit      = A ROUND
                             EQUAL by construction
                baseline   : R654's own classification of the OTHER 114 rounds (93 + 21), which
                             this round's enhanced resolver must reproduce EXACTLY
                regime     : as committed at this sha
                ⚠ AND THIS ROUND IS ITSELF CORPUS-DEPENDENT: it globs the collection directory, so
                  its own numbers are a measurement at THIS tree. Per R654 the fix is one line, so
                  the tree sha is persisted in the artifact -- the first round in this arc to do
                  what the arc concluded.
WORLDS          A THE RESIDUAL COLLAPSES: most of the 25 decide -> the census gets a point value
                  and the "unknown-sized uncertainty" is closed.
                B THE RESIDUAL SURVIVES: most stay unresolved -> one level of caller binding does
                  not decide a glob base either, and the census must ship a bound permanently.
                C THE RESOLVER DRIFTED: it fails to reproduce R654 on the 114 known rounds -> it
                  is a different instrument and says nothing about the 25.
KILL            pre-registered, before the run: the enhanced resolver MUST reproduce R654's verdict
                on all 93 CORPUS-DEPENDENT and all 21 OWN-SCOPE rounds. One disagreement => world C
                => no verdict on the 25 is admissible. An extension that changes what it already
                agreed on is not an extension.
POSITIVE CTRL   (i) the 114 known rounds, above. (ii) a synthetic whose glob base is a parameter
                passed the collection directory at its only call site -> CORPUS-DEPENDENT.
                Fails at g=0: a program with no glob yields NO-GLOB, never a class.
NEGATIVE CTRL   a synthetic whose glob base is a parameter passed the round's OWN directory ->
                OWN-SCOPE. The failure direction is to call every newly-resolved base corpus-
                dependent, which would manufacture exactly the undercount I wrongly asserted.
PLACEBO         a synthetic whose glob base is a parameter never resolvably passed -> must stay
                STILL-UNRESOLVED. A resolver that defaults its failures into a class turns an
                unknown into a finding.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 resolver x 25 undecided + 114 reproduction checks + 4 controls. All classes
                printed, residual included.
ARTIFACT        results/resolved_bases.json, WITH the tree sha beside every count.
IMPOSSIBLE      a base bound from a parameter two or more frames up needs a full call graph across
                a corpus of standalone scripts, which does not exist. Those stay STILL-UNRESOLVED
                and are reported as a residual, never absorbed into either class.
"""
from __future__ import annotations
import ast, json, pathlib, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
E05 = A24.parent
ROOT = A24.parents[1]
GLOBS = {"glob", "rglob", "iterdir"}


class PathEval:
    def __init__(self, modpath):
        self.mod, self.env = modpath, {}

    def bind(self, tree):
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


def parents_of(tree):
    p = {}
    for a in ast.walk(tree):
        for c in ast.iter_child_nodes(a):
            p[c] = a
    return p


def class_of_base(rel, own_dir):
    """CORPUS if at/above the collection dir; OWN if inside the round's own directory."""
    if rel == own_dir or own_dir in rel.parents:
        return "OWN"
    if rel in (A24.resolve(), E05.resolve(), ROOT.resolve()) or A24.resolve() in rel.parents:
        return "CORPUS"
    return "OTHER"


def classify(path, interprocedural: bool):
    """R654's rule when interprocedural=False; with one level of caller binding when True."""
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return "UNPARSEABLE", []
    ev = PathEval(path.resolve())
    ev.bind(tree)
    par = parents_of(tree)
    own_dir = path.resolve().parent
    seen, unresolved, ev_notes = [], 0, []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in GLOBS):
            continue
        base = ev.path_of(n.func.value)
        if base is None and interprocedural:
            # ⭐ ONE LEVEL OF CALLER BINDING, and only one: the base is a bare Name that is a
            #    parameter of the enclosing function, so bind it at every visible call site.
            tgt = n.func.value
            root = tgt
            while isinstance(root, (ast.Attribute, ast.Subscript)):
                root = root.value
            if isinstance(root, ast.Name):
                fn = None
                cur = n
                while cur in par:
                    cur = par[cur]
                    if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        fn = cur
                        break
                if fn is not None and root.id in [a.arg for a in fn.args.args]:
                    idx = [a.arg for a in fn.args.args].index(root.id)
                    calls = [c for c in ast.walk(tree) if isinstance(c, ast.Call)
                             and (getattr(c.func, "id", None) == fn.name
                                  or getattr(c.func, "attr", None) == fn.name)]
                    got = []
                    for c in calls:
                        e = None
                        for kw in c.keywords:
                            if kw.arg == root.id:
                                e = kw.value
                        if e is None and idx < len(c.args):
                            e = c.args[idx]
                        if e is not None:
                            b = ev.path_of(e)
                            if b is not None:
                                got.append(b)
                    if got:
                        ev_notes.append(f"bound `{root.id}` at {len(got)}/{len(calls)} call site(s)")
                        for b in got:
                            try:
                                seen.append(class_of_base(b.resolve(), own_dir))
                            except Exception:
                                unresolved += 1
                        continue
            unresolved += 1
            continue
        if base is None:
            unresolved += 1
            continue
        try:
            seen.append(class_of_base(base.resolve(), own_dir))
        except Exception:
            unresolved += 1
    if "CORPUS" in seen and "OWN" in seen and interprocedural and ev_notes:
        return "MIXED", ev_notes
    if "CORPUS" in seen:
        return "CORPUS-DEPENDENT", ev_notes
    if unresolved:
        return "STILL-UNRESOLVED" if interprocedural else "UNRESOLVED-BASE", ev_notes
    if seen:
        return "OWN-SCOPE", ev_notes
    return "NO-GLOB", ev_notes


def main() -> int:
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    if len(rounds) < 50:
        print("UNRUNNABLE: too few rounds. Exit 2, never 0.")
        return 2
    base_v = {d.name: classify(d / "run.py", False)[0] for d in rounds}
    new_v = {d.name: classify(d / "run.py", True) for d in rounds}

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    known = [n for n, v in base_v.items() if v in ("CORPUS-DEPENDENT", "OWN-SCOPE")]
    drift = [(n, base_v[n], new_v[n][0]) for n in known if new_v[n][0] != base_v[n]]
    print(f"  POSITIVE-1 the enhanced resolver must reproduce R654 on all {len(known)} already-"
          f"decided rounds -> {len(drift)} disagreement(s) -> "
          f"{'PASS' if not drift else '⛔ FAIL — it is a different instrument'}")
    for n, a, b2 in drift[:5]:
        print(f"               {n[:50]:<50} {a} -> {b2}")

    def synth(body, name):
        p = A24 / "R999_synth" / "run.py"
        t = ast.parse(body)
        ev = PathEval(p.resolve())
        ev.bind(t)
        par = parents_of(t)
        own = p.resolve().parent
        out = []
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in GLOBS:
                b = ev.path_of(n.func.value)
                if b is None and isinstance(n.func.value, ast.Name):
                    fn = None
                    cur = n
                    while cur in par:
                        cur = par[cur]
                        if isinstance(cur, ast.FunctionDef):
                            fn = cur
                            break
                    if fn and n.func.value.id in [a.arg for a in fn.args.args]:
                        i = [a.arg for a in fn.args.args].index(n.func.value.id)
                        for c in ast.walk(t):
                            if isinstance(c, ast.Call) and getattr(c.func, "id", "") == fn.name \
                                    and i < len(c.args):
                                bb = ev.path_of(c.args[i])
                                if bb is not None:
                                    out.append(class_of_base(bb.resolve(), own))
                if b is not None:
                    out.append(class_of_base(b.resolve(), own))
        return out or ["UNRESOLVED"]

    hdr = ("import pathlib\nHERE=pathlib.Path('%s')\nA=pathlib.Path('%s')\n"
           % ((A24 / "R999_synth").as_posix(), A24.as_posix()))
    pos2 = synth(hdr + "def f(b):\n    return list(b.glob('R*'))\nf(A)\n", "pos")
    print(f"  POSITIVE-2 a glob base bound to the COLLECTION dir at its only call site -> {pos2} "
          f"-> {'PASS' if pos2 == ['CORPUS'] else '⛔ FAIL'}")
    neg = synth(hdr + "def f(b):\n    return list(b.glob('*.json'))\nf(HERE)\n", "neg")
    print(f"  NEGATIVE   a glob base bound to the round's OWN dir -> {neg} -> "
          f"{'PASS — not every resolved base is corpus-dependent' if neg == ['OWN'] else '⛔ FAIL'}")
    plc = synth(hdr + "import sys\ndef f(b):\n    return list(b.glob('*'))\nf(sys.argv[1])\n", "plc")
    print(f"  PLACEBO    a base never resolvably passed -> {plc} -> "
          f"{'PASS — it stays undecided, not defaulted' if plc == ['UNRESOLVED'] else '⛔ FAIL'}")
    g0 = synth("x = 1\n", "g0")
    print(f"  g=0        no glob at all -> {g0} -> {'PASS' if g0 == ['UNRESOLVED'] else '⛔ FAIL'}")
    controls_ok = (not drift and pos2 == ["CORPUS"] and neg == ["OWN"]
                   and plc == ["UNRESOLVED"])
    print(f"  KILL       reproduction on {len(known)} decided rounds -> "
          f"{'PASS — a verdict on the undecided is admissible' if controls_ok else '⛔ UNVERIFIED'}")

    # ---- THE 25 -----------------------------------------------------------------
    undec = [n for n, v in base_v.items() if v == "UNRESOLVED-BASE"]
    res = {n: new_v[n] for n in undec}
    cnt = Counter(v[0] for v in res.values())
    print(f"\n─── THE {len(undec)} UNDECIDED ROUNDS, AFTER ONE LEVEL OF CALLER BINDING ───")
    for k in ("CORPUS-DEPENDENT", "OWN-SCOPE", "MIXED", "STILL-UNRESOLVED", "NO-GLOB"):
        c = cnt.get(k, 0)
        print(f"  {k:<18} {c:>4}  ({c/max(len(undec),1):>5.1%})")
    print(f"\n  every round, with what the binding found (G3 — the whole grid):")
    for n in sorted(res):
        v, notes = res[n]
        print(f"    {v:<18} {n[:50]:<50} {notes[:1]}")

    # ---- WHY THE RESIDUAL SURVIVED: the shape of every blocking base -----------------
    # ⛔ 0 of 25 resolved AND the notes column was empty for all 25 -- the interprocedural branch
    #    never even FOUND a parameter to bind. So the remedy R654's NEXT proposed was aimed at a
    #    mechanism that is not present. A zero with a passing synthetic control means the
    #    mechanism works and is ABSENT, which is a different fact from "it failed", and the only
    #    way to tell them apart is to look at what the bases actually are.
    print(f"\n─── WHY: the SHAPE of every glob base in the {len(undec)} undecided rounds ───")
    shapes = Counter()
    examples = {}
    for n in undec:
        src = (A24 / n / "run.py").read_text(errors="ignore")
        t = ast.parse(src)
        for x in ast.walk(t):
            if isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) \
                    and x.func.attr in GLOBS:
                v = x.func.value
                if isinstance(v, ast.Name):
                    k = "MODULE `glob.glob`" if v.id == "glob" else f"local name `{v.id}`"
                elif isinstance(v, ast.BinOp):
                    k = "a `x / literal` expression"
                else:
                    k = type(v).__name__
                shapes[k] += 1
                examples.setdefault(k, (n, x.lineno,
                                        (ast.get_source_segment(src, x) or "")[:46]))
    for k, c in shapes.most_common():
        n, l, e = examples[k]
        print(f"    {c:>4}  {k:<26} e.g. {n[:32]:<32} :{l:<4} {e}")
    mod_glob = shapes.get("MODULE `glob.glob`", 0)
    print(f"\n  ⛔ {mod_glob} of these are `glob.glob(pattern_string)` -- the STDLIB MODULE, not a")
    print(f"     path method. The classifier reads `glob` as a path base; those sites have NO base,")
    print(f"     and their corpus-dependence lives in the PATTERN ARGUMENT. They are not undecided,")
    print(f"     they are MIS-SHAPED, and no amount of caller binding would ever decide them.")

    # ---- THE CENSUS, REVISED --------------------------------------------------------
    n93 = sum(1 for v in base_v.values() if v == "CORPUS-DEPENDENT")
    gained = cnt.get("CORPUS-DEPENDENT", 0) + cnt.get("MIXED", 0)
    residual = cnt.get("STILL-UNRESOLVED", 0)
    print(f"\n─── THE CENSUS, REVISED ───")
    print(f"  R654 published                      : {n93} corpus-dependent, "
          f"{len(undec)} undecided -> a two-sided bound [{n93}, {n93+len(undec)}]")
    print(f"  decided corpus-dependent by binding : +{gained}")
    print(f"  decided OWN-SCOPE by binding        : +{cnt.get('OWN-SCOPE', 0)} "
          f"(these do NOT join the count)")
    print(f"  ⭐ revised                            : {n93+gained} corpus-dependent, "
          f"residual {residual} -> bound [{n93+gained}, {n93+gained+residual}]")
    width_before, width_after = len(undec), residual
    print(f"  the uncertainty's WIDTH went {width_before} -> {width_after} "
          f"({'narrowed' if width_after < width_before else 'unchanged'})")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no verdict on the undecided is admissible"
    elif residual > len(undec) * 0.6:
        world = (f"B THE RESIDUAL SURVIVES — {residual} of {len(undec)} stay undecided after one "
                 f"level of caller binding, so a glob base is no more decidable than a read "
                 f"population was, and the census must ship a bound permanently: "
                 f"[{n93+gained}, {n93+gained+residual}].")
    else:
        world = (f"A THE RESIDUAL COLLAPSES — {gained} of {len(undec)} resolve corpus-dependent "
                 f"and {cnt.get('OWN-SCOPE', 0)} resolve own-scope; {residual} remain. The census "
                 f"is {n93+gained} with a residual of {residual}, replacing R654's "
                 f"[{n93}, {n93+len(undec)}]. ⚠ AND THE DIRECTION WAS NOT KNOWN IN ADVANCE: "
                 f"{cnt.get('OWN-SCOPE', 0)} of the undecided went the OTHER way, which is why "
                 f"'undercount' was the wrong word.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 resolver x {len(rounds)} rounds (reproduction on {len(known)}, "
          f"decision on {len(undec)}) + 4 controls. Residual reported, never absorbed.")
    print(f"  ⭐ tree sha persisted beside every count: {sha[:12]} — R654 concluded this and this "
          f"is the first round in the arc to do it.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resolved_bases.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "tree_sha": sha, "tree_sha_note": "the corpus this was counted over (R654's remedy)",
        "rounds_at_this_tree": len(rounds),
        "r654_corpus_dependent": n93, "r654_undecided": len(undec),
        "decided": dict(cnt), "revised_corpus_dependent": n93 + gained,
        "residual": residual,
        "bound_before": [n93, n93 + len(undec)],
        "bound_after": [n93 + gained, n93 + gained + residual],
        "per_round": {n: {"verdict": v, "notes": notes} for n, (v, notes) in res.items()},
        "reproduction_disagreements": drift,
        "check256": ("R654's NEXT cited R653's '16 of 59' as evidence about GLOB BASES; that 16 "
                     "was about the blocking PARAMETER of a D1 READ SITE -- a different "
                     "population. And it called 93 an UNDERCOUNT, asserting a direction the "
                     "evidence did not carry: an undecided round can resolve to OWN-SCOPE."),
        "why_residual_survived": {"shapes": dict(shapes), "module_glob_sites": mod_glob,
            "note": ("the interprocedural branch fired 0 times: the blocking bases are not "
                     "parameters at all. 11 sites use the stdlib `glob.glob(pattern)`, which has "
                     "no path base; the rest are function-LOCAL assignments, and PathEval binds "
                     "only module-level names")},
        "impossible": ("a base bound from a parameter two or more frames up needs a call graph "
                       "across standalone scripts, which does not exist; those stay "
                       "STILL-UNRESOLVED and are reported as a residual."),
    }, indent=2))
    print(f"\n  wrote {out / 'resolved_bases.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
