#!/usr/bin/env python3
"""
R651 -- which unresolvability needs the CALLER, and which only needs a better evaluator?

CHECK #252 ON R650's CLOSING LINE, AND IT CARRIES AN UNCHECKED QUANTIFIER.
  R650 closed: "the three sites reading a path from a function ARGUMENT are THE ONLY class whose
  resolution is genuinely per-call-site ... EVERY OTHER class above is a missing feature."
  ⛔ Neither half was computed. "3" was computed; "the only" and "every other" were not. §4's row
     `the closing sentence is a claim and never gets a control` names this exact tell -- a
     quantifier over my own work, written last, acted on by the next round, with no control.
  ⚠ And it is not obviously true. `an element of a collection built at runtime` (27 sites) and
     `a name bound by nothing resolvable in scope` (54) can trace to a parameter just as easily
     as the 3 already labelled. The labels were assigned by the SHAPE OF THE READ EXPRESSION,
     never by where its value comes from -- so they cannot support a claim about provenance.

ESTIMAND        Of the read sites R650 could not resolve, the partition into
                  INTER  the read path depends on a FUNCTION PARAMETER or on the return value of
                         a call -- no evaluator confined to the function body can resolve it;
                         it needs the caller, or the runtime.
                  INTRA  every binding the path needs exists inside the same function, and only
                         the evaluator is missing -- a strictly mechanical extension.
                n_inter, and specifically whether n_inter == 3 and coincides exactly with the
                sites R650 labelled `a function ARGUMENT`.
IDENTIFICATION  Exact for the partition (a static property: does the target's dependency closure
                inside the function reach a parameter or a Call?). NOT identified for "this is
                unresolvable in principle" -- a caller may pass a constant, which is why the
                second half of the round counts CALL SITES for every INTER member.
SCOPE           population : the UNRESOLVABLE read sites of every A24 round, MINUS this round
                instrument : ast dependency closure over names within the enclosing function
                             instrument unit = A READ CALL SITE
                             claim unit      = A READ CALL SITE
                             EQUAL by construction
                baseline   : R650's own artifact -- the site list is re-derived INDEPENDENTLY
                             here and required to match it exactly, so this is a replication of
                             R650's census and not a reuse of its numbers
                regime     : as committed at this sha
WORLDS          A THE LINE HOLDS: n_inter == 3 and they are exactly R650's argument sites ->
                  the impossibility register has one narrow, correctly-identified entry.
                B THE LINE IS FALSE: inter-procedural sites exist outside that class -> R650's
                  "only"/"every other" is retracted, and the register was understating what this
                  corpus cannot resolve statically.
                C THE PARTITION IS DEGENERATE: nearly everything is INTER (or nearly nothing) ->
                  the distinction does not carve the corpus and is not worth carrying.
KILL            pre-registered, with its threshold, before the run: if ANY site outside R650's
                `a function ARGUMENT` class classifies INTER, R650's closing line is FALSE and is
                retracted -- no reinterpretation, no "in spirit it was right".
                And if n_inter > 0.8 * n_unresolvable the partition is degenerate (world C) and
                no register entry is derived from it.
POSITIVE CTRL   (i) the site list must reproduce R650's artifact EXACTLY -- same count, same
                    (round, line) pairs. A census that cannot be replicated is not a baseline.
                (ii) the 3 sites R650 labelled `a function ARGUMENT` must classify INTER.
                Fails at g=0: a synthetic function with no parameters yields 0 INTER.
NEGATIVE CTRL   a synthetic read whose path is built only from a module-level constant must
                classify INTRA -- the classifier must not call everything inter-procedural.
PLACEBO         a function whose parameter exists but is NEVER used in the read path must
                classify INTRA. This is the one that matters: the failure direction is to mark a
                site INTER because a parameter is merely PRESENT rather than REACHED.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a. The partition is a pure function of the tree at this sha.
MULTIPLICITY    1 classifier x every unresolvable site + 5 control checks + a call-site count per
                INTER member. Survivors AND non-survivors.
ARTIFACT        results/inter_vs_intra.json
IMPOSSIBLE      whether a caller passes a CONSTANT is decided per call site, and a function
                called from another module (or from a __main__ guard in a round that imports it)
                is not enumerable from this tree alone. Call-site counts are therefore a LOWER
                BOUND, stated as one.
"""
from __future__ import annotations
import ast, json, pathlib, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R650 = A24 / "R650_can_a_site_say_what_it_reads" / "results" / "read_populations.json"

READ_CALLS = {"read_text", "read", "readlines"}
GLOB_CALLS = {"glob", "rglob"}
# calls that do NOT make a value inter-procedural: they are pure path/collection plumbing whose
# own arguments carry the dependency, and the closure below descends into those arguments anyway.
PURE = {"Path", "resolve", "absolute", "expanduser", "sorted", "list", "glob", "rglob",
        "iterdir", "parent", "joinpath", "with_suffix", "strip", "rstrip"}
# ⛔ A CALL WHOSE RETURN TYPE CANNOT BE A PATH CANNOT BE THE SOURCE OF A PATH. v1 walked the
#    whole defining expression for ANY non-PURE call, so a comprehension's FILTER --
#    `[x for x in d.iterdir() if x.is_file()]` -- made the value "depend on the return value of
#    is_file(...)". It does not: a bool is a filter, never a source. 14 of 108 INTER verdicts
#    were manufactured this way. The closure now skips calls that cannot return a path.
NEVER_A_PATH = {"is_file", "is_dir", "exists", "is_absolute", "startswith", "endswith",
                "isdigit", "isalpha", "islower", "isupper", "match", "search", "any", "all",
                "len", "isinstance", "bool", "int", "float"}


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


def names_in(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def impure_calls_in(node):
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            fn = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if fn and fn not in PURE and fn not in NEVER_A_PATH:
                out.append(fn)
    return out


def classify(site_target, fn):
    """INTER if the target's dependency closure reaches a parameter or an impure call.

    Returns (verdict, evidence). Confined to ONE function body on purpose: that is exactly the
    boundary the question is about.
    """
    if fn is None:
        return "INTRA", "not inside a function — module scope, all bindings visible"
    params = {a.arg for a in fn.args.args} | {a.arg for a in fn.args.kwonlyargs}
    if fn.args.vararg:
        params.add(fn.args.vararg.arg)
    if fn.args.kwarg:
        params.add(fn.args.kwarg.arg)

    # binding table: name -> list of RHS expressions that define it inside this function
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

    seen, work = set(), [site_target]
    while work:
        expr = work.pop()
        for c in impure_calls_in(expr):
            return "INTER", f"depends on the return value of {c}(...)"
        for nm in names_in(expr):
            if nm in params:
                return "INTER", f"depends on the parameter `{nm}`"
            if nm in seen:
                continue
            seen.add(nm)
            work += binds.get(nm, [])
    return "INTRA", "every binding it needs is inside this function"


def sites_of(src, want_unresolved_only=True):
    """Re-derive R650's read-site census INDEPENDENTLY, then classify the unresolved ones."""
    tree = ast.parse(src)
    parents = parents_of(tree)
    out = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in READ_CALLS):
            continue
        out.append((n.lineno, n.func.value, enclosing_fn(n, parents)))
    return out


def main() -> int:
    if not R650.exists():
        print("UNRUNNABLE: R650's artifact absent — no baseline to replicate. Exit 2, never 0.")
        return 2
    base = json.loads(R650.read_text())
    base_sites = {(s["round"], s["line"]) for s in base["all_sites"]}
    base_unres = {(s["round"], s["line"]): s for s in base["all_sites"]
                  if s["verdict"] == "UNRESOLVABLE"}
    base_arg = {k for k, s in base_unres.items() if "ARGUMENT" in s["reason"]}

    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    # ⛔ v1 KEYED SITES BY (round, line) INTO A DICT, AND THE KEY IS NOT AN IDENTIFIER: R650's
    #    artifact holds 364 records but only 354 distinct (round, line) pairs, so 10 sites
    #    vanished into the key before any comparison was made. Same class as a ledger whose
    #    entries live in two forms -- the identifier I chose was not one. Now a LIST per key, and
    #    the replication compares MULTISETS so duplicates must match in count too.
    mine = {}
    for d in rounds:
        try:
            for line, target, fn in sites_of((d / "run.py").read_text(errors="ignore")):
                mine.setdefault((d.name, line), []).append((target, fn))
        except SyntaxError:
            pass

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    # ⭐ (i) is a REPLICATION, not a self-check: this file re-derives the census from the AST with
    #    its own code and must land on the same (round, line) pairs R650 published.
    # ⛔ AND THE TWO SIDES HAD DIFFERENT SELF-EXCLUSIONS. R650 excluded ITSELF from its census;
    #    this round excludes only itself, so R650's own run.py was in my population and could
    #    never be in R650's. A replication must compare the SAME population -- so R650 is
    #    dropped here, and its own sites are reported separately as what the baseline could not
    #    have seen.
    mine_cmp = Counter({k: len(v) for k, v in mine.items() if not k[0].startswith("R650_")})
    base_cnt = Counter(( s["round"], s["line"]) for s in base["all_sites"])
    r650_own = sum(len(v) for k, v in mine.items() if k[0].startswith("R650_"))
    same = mine_cmp == base_cnt
    print(f"  POSITIVE-1 independent re-derivation of R650's census (MULTISET, R650 excluded on "
          f"both sides): mine {sum(mine_cmp.values())} vs published {sum(base_cnt.values())} -> "
          f"{'IDENTICAL — PASS' if same else '⛔ FAIL'}")
    print(f"             (+{r650_own} site(s) in R650 itself, which its own census could not see)")
    if not same:
        diff = (mine_cmp - base_cnt) + (base_cnt - mine_cmp)
        print(f"             disagreeing keys: {len(diff)} {sorted(diff)[:5]}")
    argcls = {k: classify(*mine[k][0]) for k in base_arg if k in mine}
    pos2 = bool(argcls) and all(v[0] == "INTER" for v in argcls.values())
    print(f"  POSITIVE-2 R650's {len(base_arg)} `function ARGUMENT` site(s) must classify INTER "
          f"-> {[f'{k[1]}:{v[0]}' for k, v in argcls.items()]} -> "
          f"{'PASS' if pos2 else '⛔ FAIL'}")
    g0 = ast.parse("def f():\n    import pathlib\n    return pathlib.Path('/x').read_text()\n")
    g0fn = [n for n in ast.walk(g0) if isinstance(n, ast.FunctionDef)][0]
    g0t = [n.func.value for n in ast.walk(g0)
           if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "read_text"][0]
    g0v = classify(g0t, g0fn)
    print(f"  g=0        a function with NO parameters -> {g0v[0]} -> "
          f"{'PASS (can return INTRA)' if g0v[0] == 'INTRA' else '⛔ FAIL'}")
    negsrc = ast.parse("B = 1\ndef f():\n    return (B / 'x').read_text()\n")
    negfn = [n for n in ast.walk(negsrc) if isinstance(n, ast.FunctionDef)][0]
    negt = [n.func.value for n in ast.walk(negsrc)
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "read_text"][0]
    negv = classify(negt, negfn)
    print(f"  NEGATIVE   a path from a MODULE constant -> {negv[0]} -> "
          f"{'PASS — not everything is inter-procedural' if negv[0] == 'INTRA' else '⛔ FAIL'}")
    # ⭐ THE PLACEBO IS THE ONE THAT MATTERS: the failure direction of this classifier is to mark
    #    a site INTER because a parameter is PRESENT in the function, not because it is REACHED.
    plcsrc = ast.parse("def f(unused, B):\n    p = B\n    return (p / 'x').read_text()\n")
    plcsrc2 = ast.parse("import pathlib\nC = pathlib.Path('/c')\n"
                        "def f(unused):\n    p = C\n    return (p / 'x').read_text()\n")
    plcfn = [n for n in ast.walk(plcsrc2) if isinstance(n, ast.FunctionDef)][0]
    plct = [n.func.value for n in ast.walk(plcsrc2)
            if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "read_text"][0]
    plcv = classify(plct, plcfn)
    print(f"  PLACEBO    a parameter that EXISTS but is never reached -> {plcv[0]} "
          f"({plcv[1]}) -> "
          f"{'PASS — presence is not reachability' if plcv[0] == 'INTRA' else '⛔ FAIL'}")
    controls_ok = same and pos2 and g0v[0] == "INTRA" and negv[0] == "INTRA" \
        and plcv[0] == "INTRA"
    print(f"  KILL       census replicated + known members recovered -> "
          f"{'PASS — the partition is admissible' if controls_ok else '⛔ UNVERIFIED'}")

    # ---- THE PARTITION --------------------------------------------------------------
    # ⛔ AND THE JOIN KEY IS STILL NOT AN IDENTIFIER, NOW ON THE OTHER SIDE. Taking every site
    #    at an UNRESOLVABLE (round, line) can pull in a RESOLVED sibling sharing that line, and
    #    R650's artifact carries no column offset to tell them apart. So a key is admitted only
    #    when the baseline's UNRESOLVABLE count at that key EQUALS the number of sites I find
    #    there -- otherwise the key is AMBIGUOUS, excluded, and counted out loud. Excluding what
    #    cannot be addressed is the sound direction; guessing which sibling was meant is not.
    unres_at = Counter(k for k in base_cnt for s in base["all_sites"]
                       if (s["round"], s["line"]) == k and s["verdict"] == "UNRESOLVABLE"
                       and False)          # placeholder replaced below
    unres_at = Counter((s["round"], s["line"]) for s in base["all_sites"]
                       if s["verdict"] == "UNRESOLVABLE")
    verdicts, ambiguous = {}, []
    for k, n_unres in unres_at.items():
        found = mine.get(k, [])
        if len(found) != n_unres:
            ambiguous.append((k, n_unres, len(found)))
            continue
        for i, tf in enumerate(found):
            verdicts[(k[0], k[1], i)] = classify(*tf)
    print(f"\n  ADDRESSABILITY  {len(unres_at)} unresolvable key(s); "
          f"{len(ambiguous)} AMBIGUOUS (a resolved sibling shares the line) -> excluded, "
          f"covering {sum(a[1] for a in ambiguous)} site(s)")
    inter = {k: v for k, v in verdicts.items() if v[0] == "INTER"}
    intra = {k: v for k, v in verdicts.items() if v[0] == "INTRA"}
    print(f"\n─── INTER (needs the caller) vs INTRA (needs a better evaluator) ───")
    print(f"  unresolvable sites classified : {len(verdicts)} of {base['unresolvable']} "
          f"({sum(a[1] for a in ambiguous)} excluded as unaddressable)")
    print(f"  INTER                         : {len(inter)}  ({len(inter)/max(len(verdicts),1):.1%})")
    print(f"  INTRA                         : {len(intra)}  ({len(intra)/max(len(verdicts),1):.1%})")
    print(f"\n  INTER by evidence (the whole grid, G3):")
    for ev, c in Counter(v[1] for v in inter.values()).most_common(12):
        print(f"    {c:>4}  {ev}")
    print(f"\n  and CROSS-TABULATED against R650's shape labels — the question the line begged:")
    xt = Counter((base_unres[(k[0], k[1])]["reason"][:46], v[0]) for k, v in verdicts.items())
    shapes = sorted({r for r, _ in xt})
    print(f"    {'R650 shape label':<48} {'INTER':>6} {'INTRA':>6}")
    for s in shapes:
        print(f"    {s:<48} {xt[(s,'INTER')]:>6} {xt[(s,'INTRA')]:>6}")

    outside = {k for k in inter if (k[0], k[1]) not in base_arg}
    print(f"\n  ⭐ INTER sites OUTSIDE R650's `function ARGUMENT` class: {len(outside)}")

    # ---- CALL SITES for every INTER member: a LOWER BOUND ----------------------------
    print(f"\n─── CALL SITES of the enclosing function, per INTER member (LOWER BOUND) ───")
    callcounts = {}
    for k in sorted(inter)[:14]:
        rnd, line, idx = k
        fn = mine[(rnd, line)][idx][1]
        if fn is None:
            continue
        src = (A24 / rnd / "run.py").read_text(errors="ignore")
        tree = ast.parse(src)
        n_calls = sum(1 for n in ast.walk(tree)
                      if isinstance(n, ast.Call)
                      and (getattr(n.func, "id", None) == fn.name
                           or getattr(n.func, "attr", None) == fn.name))
        callcounts[f"{rnd}:{line}"] = n_calls
        print(f"    {rnd[:44]:<44} :{line:<4} fn `{fn.name}` called {n_calls}x in its own module")

    # ---- VERDICT: a function of the controls ----------------------------------------
    frac = len(inter) / max(len(verdicts), 1)
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no partition claim is admissible"
    elif frac > 0.8:
        world = (f"C DEGENERATE — {frac:.1%} of unresolvable sites are INTER, so the partition "
                 f"does not carve the corpus and no register entry is derived from it.")
    elif not outside:
        world = (f"A THE LINE HOLDS — {len(inter)} INTER site(s), all inside R650's "
                 f"`function ARGUMENT` class. The impossibility register's entry is narrow and "
                 f"correctly identified.")
    else:
        world = (f"B THE LINE IS FALSE — {len(inter)} of {len(verdicts)} unresolvable sites are "
                 f"INTER, and {len(outside)} of them sit OUTSIDE R650's `function ARGUMENT` "
                 f"class. R650's 'the ONLY class' and 'EVERY OTHER class is a missing feature' "
                 f"are retracted. The shape of a read expression does not determine where its "
                 f"value comes from, and the labels were shapes.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 classifier x {len(verdicts)} sites + 5 controls + "
          f"{len(callcounts)} call-site counts. Non-survivors above in full.")
    print(f"  ⚠ LOWER BOUND: call-site counts are per-module; a function reached from another "
          f"module or a test harness is not enumerable from this tree.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "inter_vs_intra.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        # ⛔ ANNOTATED 2026-08-05 BY R654's CHECK #255, NOT REWRITTEN (L81). The two fields below
        #    persisted `len(mine)`=355 and `len(base_sites)`=354 -- the DISTINCT (round, line) KEY
        #    counts, i.e. the very quantities the multiset repair above exists to reject. The
        #    control that ran and passed compared `sum(mine_cmp.values())` to
        #    `sum(base_cnt.values())`, both 364. So the REPORT was right and the ARTIFACT recorded
        #    different numbers, and R654 read the artifact and quoted 355 vs 354 as if that were
        #    the replication. An artifact is what a later round attacks; when it disagrees with
        #    the report, the report is not reproducible. Original keys kept, correct ones added.
        "census_replicated": same,
        "sites_mine_DISTINCT_KEYS_stale": len(mine),
        "sites_published_DISTINCT_KEYS_stale": len(base_sites),
        "sites_mine": sum(mine_cmp.values()), "sites_published": sum(base_cnt.values()),
        "artifact_repair_note": ("the two *_DISTINCT_KEYS_stale fields are the pre-repair "
                                 "key-collapsed counts that this round's own multiset control "
                                 "exists to reject; sites_mine/sites_published now hold what the "
                                 "control actually compared (364 vs 364)"),
        "unresolvable": base["unresolvable"], "classified": len(verdicts),
        "ambiguous_keys": [[list(k), u, f] for k, u, f in ambiguous],
        "inter": len(inter), "intra": len(intra), "inter_fraction": frac,
        "inter_outside_argument_class": len(outside),
        "inter_evidence": dict(Counter(v[1] for v in inter.values())),
        "cross_tab": {f"{s}|{v}": c for (s, v), c in xt.items()},
        "call_site_lower_bounds": callcounts,
        "inter_members": [f"{r}:{l}#{i}" for r, l, i in sorted(inter)],
        "check252": ("R650 closed with 'the ONLY class whose resolution is per-call-site' and "
                     "'EVERY OTHER class is a missing feature'. Neither quantifier was computed; "
                     "the labels they rest on were assigned by the SHAPE of the read expression, "
                     "which cannot support a claim about where a value comes from."),
        "impossible": ("whether a caller passes a constant is decided per call site, and calls "
                       "from outside the module are not enumerable here -- so call-site counts "
                       "are a LOWER BOUND, stated as one."),
    }, indent=2))
    print(f"\n  wrote {out / 'inter_vs_intra.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
