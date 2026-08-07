"""How many of the points this suite CHECKS are ratios -- the class its invariant convicts wrongly?

R341 named an exception class for the guard's first invariant and stopped there. `point estimate
inside its own interval` is stated SOUND in the guard's own proxy ledger and gated on, and it is
not sound for a RATIO ESTIMATOR SUMMARISED BY ITS BOOTSTRAP MEAN: when the denominator approaches
zero the replicate distribution is Cauchy-like and the mean can sit far outside its own percentile
interval with nothing wrong. R235 has 13 such cells at |offcentre| up to 2.48.

R341 could stop there because R235's `eta` is not a MEANISH name, so the guard never looked at it.
That is an accident of naming, not a property of the suite. THE QUESTION THIS ROUND ASKS IS THE
ONE R341 DEFERRED: of the pairs the guard DOES check, how many are ratios? For each such pair a
violation would be a FALSE CONVICTION and a pass means nothing, so until this is counted the
guard's coverage number is an upper bound on its own validity.

ESTIMAND, named before the method
---------------------------------
Over the 42 distinct (round, mean_key) pairs behind the guard's 389 checked pairs, the count whose
point estimate is CONSTRUCTED BY DIVISION in the round's own source, split by whether the
denominator is data-derived (can approach zero -> the pathology is live) or a constant/count
(cannot -> it is arithmetic normalisation and invariant 1 is safe).

IDENTIFICATION -- and this is why the round is a source read, not an artifact scan
----------------------------------------------------------------------------------
A published number carries no record of how it was built. `0.0128` is a difference, a ratio and a
regression coefficient in exactly the same JSON. So the quantity is NOT identified from artifacts at
any sample size, and no amount of offcentre arithmetic decides it. It is identified from the source,
by the construction of the expression assigned to the key. That is an AST question, so it is asked
with an AST rather than a regex -- realstat §4: a search is a measuring instrument, and a substring
search for "/" would match every path literal and every comment in the corpus.

FOUR-VALUED, and the fourth value is the honest one
-----------------------------------------------------
  RATIO_DATA   a Div whose denominator is a data expression      -> the pathology is LIVE here
  RATIO_CONST  a Div by a literal, len(...), or a count name     -> normalisation; invariant 1 safe
  NON_RATIO    no Div anywhere in the resolved expression        -> invariant 1 sound
  UNRESOLVED   the key's value is a Name this round cannot follow, or the key is not in the source
               -> UNVERIFIED. NEVER folded into NON_RATIO. A key I cannot read is not a key I have
               cleared, and folding it into the clean bucket is how a false acquittal is minted.

The RATIO_DATA / RATIO_CONST split is a NAME-BASED JUDGEMENT and is labelled as one: the denominator
is called a count if it is a numeric literal, a `len(...)`, or one of a short stated list of count
names. That rule is an instrument and gets its own planted controls below, both directions.

SCOPE
  population  the 42 distinct (round, mean_key) pairs the guard actually checks -- a CENSUS
  instrument  Python's own AST over each round's committed run.py; resolution follows bare Names
              through at most MAXDEPTH module-level or function-level assignments
  baseline    R341's finding that the class exists but was never counted inside the checked set
  regime      sources as committed at this hash

WORLDS
  W1 DORMANT     zero RATIO_DATA among the checked pairs. The exception class is real but has never
                 touched a verdict; the guard's current output stands as published.
  W2 LIVE        >=1 RATIO_DATA. Every verdict on those pairs is unsound in BOTH directions and the
                 guard's coverage number must be reported net of them.
  W3 UNREADABLE  UNRESOLVED dominates. The question is not answerable by this instrument and the
                 honest output is a bound, not a count.

PREDICTION MATRIX -- and it includes a CROSS-INSTRUMENT prediction, which is what makes it severe
  A RATIO_DATA point with a near-zero denominator should ALSO show a large |offcentre| in R340's
  artifact-side table. So:
     W1 -> 0 RATIO_DATA, and R340's table stays at <=0.21 for 37 of 38 rounds        (agree)
     W2 -> >=1 RATIO_DATA, and those rounds should be the HIGH-offcentre ones        (agree)
     W2' -> >=1 RATIO_DATA sitting at offcentre 0.02                                 (DISAGREE:
            two instruments, one source-side and one artifact-side, contradict. Then the framing
            is the finding and neither count is reportable until the disagreement is resolved.)
  A prediction that cannot come out W2' is not a test; this one can.

PRE-REGISTERED KILL, written before the run
    if the planted controls fire in BOTH directions and the g=0 case is handled as UNRUNNABLE:
        RATIO_DATA >= 1  -> the guard's coverage is CONTAMINATED. Name the pairs; each needs a read.
        RATIO_DATA == 0 and UNRESOLVED <= 25% -> the class is NAMED BUT DORMANT. Coverage stands.
        UNRESOLVED > 25% -> W3. Report a BOUND (RATIO_DATA is between 0 and 0+UNRESOLVED), never a
                            point, and say the instrument is the limit.
    else:
        UNVERIFIED.

⛔ ARITHMETIC TRAP. Could this come out otherwise? Yes: the corpus contains divisions (R235 is one),
and nothing about the guard's selection rule excludes them. The result is a measurement, not algebra.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- the census would be silence
    2  no checked pairs, or no sources: an empty population, never a silent pass
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
MAXDEPTH = 3
# A denominator is a COUNT if it is a literal, a len(...), or one of these names. Stated, because
# it is a name-based rule and therefore an instrument with a blind spot, not a fact.
COUNTNAMES = {"n", "N", "nboot", "NBOOT", "n_boot", "total", "denom_n", "count", "size", "nrow",
              "n_prompts", "n_total", "B", "k", "K", "reps", "n_seeds", "len"}
# Calls this reader may see THROUGH. Each either performs no division at all, or divides by a
# COUNT (np.mean is sum/n), which is the safe kind -- the pathology needs a DATA denominator that
# can approach zero. `average` is deliberately absent: its denominator is a sum of weights, which
# is data. Anything not on this list and not defined locally is UNRESOLVED, never NON_RATIO.
SAFE_REDUCTIONS = {"mean", "nanmean", "sum", "nansum", "median", "nanmedian",
                   "percentile", "nanpercentile", "quantile", "nanquantile",
                   "max", "min", "nanmax", "nanmin", "amax", "amin", "abs", "absolute",
                   "float", "int", "round", "array", "asarray", "item", "tolist",
                   "std", "nanstd", "var", "nanvar", "sqrt", "sorted", "list", "len"}


def load_guard():
    p = ROOT / "assurance" / "artifacts_are_internally_coherent.py"
    spec = importlib.util.spec_from_file_location("coh_guard", p)
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m, hashlib.sha256(p.read_bytes()).hexdigest()[:12]


G, GUARD_HASH = load_guard()


# ------------------------------------------------------------------ the checked population ------
def checked_pairs():
    """Every (rid, mean_key) the guard actually pairs. Re-walked rather than read off `all_pairs`,
    because that key stores the VALUE and drops the mean's NAME, and the name is what links an
    artifact number to the line that built it."""
    rows = []

    def walk(o, rid, path):
        if isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, rid, f"{path}[{i}]")
            return
        if not isinstance(o, dict):
            return
        cks = [(k, o[k]) for k in o if G.CIISH.match(k) and G.is_ci(o[k])]
        mks = [(k, o[k]) for k in o
               if G.MEANISH.match(k) and not G.PVALUE.match(k)
               and isinstance(o[k], (int, float)) and not isinstance(o[k], bool)]
        stem = set()
        for mk, _ in mks:
            for ck, _cv in cks:
                if mk.lower() in ck.lower() or ck.lower().replace("_ci", "") == mk.lower():
                    stem.add((mk, ck))
                    rows.append((rid, mk, ck, "stem"))
        sole_null = len(mks) == 1 and bool(G.NULLNAME.search(mks[0][0]))
        ci_stem = re.sub(r"_ci$|^ci_", "", cks[0][0], flags=re.I) if len(cks) == 1 else None
        spoken = bool(ci_stem and ci_stem != cks[0][0] and ci_stem in o
                      and not any(ci_stem == m for m, _ in mks))
        if len(mks) == 1 and len(cks) == 1 and not stem and not sole_null and not spoken:
            rows.append((rid, mks[0][0], cks[0][0], "sole"))
        for k, v in o.items():
            walk(v, rid, f"{path}.{k}" if path else k)

    for f in sorted(ROOT.glob("E*/A*/R*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            walk(json.load(open(f)), f.parts[-3], "")
        except Exception:
            continue
    return rows


# ------------------------------------------------------------------------- the classifier -------
def denom_is_count(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return True
    if isinstance(node, ast.Name) and node.id in COUNTNAMES:
        return True
    if isinstance(node, ast.Call):
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if name in ("len", "size", "count", "sqrt"):
            return True
    # arithmetic on counts is still a count: `n + 1` is the permutation p-value floor's
    # denominator throughout this corpus, and treating it as data made `1.0/(n+1)` a live ratio.
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        return denom_is_count(node.left) and denom_is_count(node.right)
    return False


def divisions(node: ast.AST):
    """Every division in an expression, as its denominator node. `np.divide(a,b)` counts too --
    an AST that only knows the `/` operator would clear a file that spells it out."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            out.append(n.right)
        elif isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
            if nm in ("divide", "true_divide") and len(n.args) >= 2:
                out.append(n.args[1])
    return out


def assignments(tree: ast.AST) -> dict[str, list[ast.AST]]:
    """⚠ v1 recorded only `ast.Name` targets, and that ONE omission produced 7 of this round's 9
    UNRESOLVED keys. Every one of them is a TUPLE UNPACK -- `d, lo, hi = ci(a_s - a_c)`,
    `m2, ci2, below2 = paired(...)`, `pm, plo, phi = ...` -- which is how this package returns an
    estimate beside its interval, i.e. the single commonest shape in the corpus. The instrument was
    blind to the idiom the population is written in, and 21% UNRESOLVED read as a property of the
    sources rather than of the reader. A tuple element cannot be attributed to one part of the RHS,
    so the whole RHS is bound to every name in the target: that can only ever OVER-detect a ratio,
    never clear one, which is the safe direction for this question."""
    out: dict[str, list[ast.AST]] = {}
    fns = functiondefs(tree)

    def tuple_shape(value):
        """The RHS as an element list, when that is knowable EXACTLY: a tuple literal, or a call to
        a local function all of whose returns are tuple literals of one length. Otherwise None.

        ⚠ THIS EXISTS BECAUSE THE CONSERVATIVE RULE PRODUCED A FALSE POSITIVE, exactly where the
        docstring above said it could. R127 does `d_all, lo_all, hi_all, p_all = paired_boot(...)`,
        and `paired_boot` returns `(mean(dd), pct(dd,2.5), pct(dd,97.5), max(p, 1.0/(n+1)))`. The
        only division is the permutation p-value FLOOR, which belongs to the FOURTH element -- and
        binding the whole RHS to every name handed it to `d_all`, the plain mean that the guard
        actually checks. The cross-instrument prediction is what caught it: the source side called
        R127 a live ratio while the artifact side put it at offcentre 0.02, and a real ratio
        pathology cannot be centred. Positional binding is EXACT here, not merely tighter."""
        if isinstance(value, (ast.Tuple, ast.List)):
            return list(value.elts)
        if isinstance(value, ast.Call):
            f = value.func
            nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            rets = fns.get(nm) or []
            shapes = [r.elts for r in rets if isinstance(r, (ast.Tuple, ast.List))]
            if rets and len(shapes) == len(rets) and len({len(s) for s in shapes}) == 1:
                # one slot may be built differently on different return paths: keep all candidates
                return [ast.Tuple(elts=[s[i] for s in shapes], ctx=ast.Load())
                        for i in range(len(shapes[0]))]
        return None

    def bind(target, value):
        if isinstance(target, ast.Name):
            out.setdefault(target.id, []).append(value)
        elif isinstance(target, (ast.Tuple, ast.List)):
            elts = tuple_shape(value)
            if elts is not None and len(elts) == len(target.elts) \
                    and not any(isinstance(e, ast.Starred) for e in target.elts):
                for t, v in zip(target.elts, elts):
                    bind(t, v)
            else:
                for el in target.elts:      # shape unknown -> conservative, over-detects only
                    bind(el, value)
        elif isinstance(target, ast.Starred):
            bind(target.value, value)

    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                bind(t, n.value)
        elif isinstance(n, (ast.AnnAssign, ast.AugAssign)):
            if n.value is not None:
                bind(n.target, n.value)
        elif isinstance(n, (ast.For, ast.AsyncFor)):
            bind(n.target, n.iter)
        elif isinstance(n, ast.withitem) and n.optional_vars is not None:
            bind(n.optional_vars, n.context_expr)
    return out


def functiondefs(tree: ast.AST) -> dict[str, list[ast.AST]]:
    """name -> the expressions it can return. A division inside `ci()` or `paired()` is invisible
    to any reader that stops at the call site, and those two helpers build most of this corpus's
    published pairs."""
    out: dict[str, list[ast.AST]] = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rets = [r.value for r in ast.walk(n) if isinstance(r, ast.Return) and r.value]
            out[n.name] = rets
    return out


def classify_expr(expr: ast.AST, asg: dict, depth: int = 0, maxdepth: int = MAXDEPTH,
                  fns: dict | None = None, seen: frozenset = frozenset()):
    """Resolve bare Names through assignments and local calls into their bodies, then look for a
    Div. Returns (label, evidence)."""
    fns = fns or {}
    divs = divisions(expr)
    if divs:
        if all(denom_is_count(d) for d in divs):
            return "RATIO_CONST", ast.unparse(expr)[:110]
        return "RATIO_DATA", ast.unparse(expr)[:110]
    if isinstance(expr, ast.Name):
        if depth >= maxdepth or expr.id not in asg:
            return "UNRESOLVED", f"bare name {expr.id!r}, depth {depth}"
        labels = [classify_expr(v, asg, depth + 1, maxdepth, fns, seen) for v in asg[expr.id]]
        for want in ("RATIO_DATA", "RATIO_CONST", "UNRESOLVED"):
            for lab, ev in labels:
                if lab == want:
                    return lab, ev
        return "NON_RATIO", ast.unparse(expr)[:110]
    if isinstance(expr, ast.Call):
        f = expr.func
        nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
        # a LOCAL function: the division may live in its body, invisible at the call site
        if nm in fns and nm not in seen and depth < maxdepth:
            labels = [classify_expr(r, asg, depth + 1, maxdepth, fns, seen | {nm})
                      for r in fns[nm]]
            for want in ("RATIO_DATA", "RATIO_CONST", "UNRESOLVED"):
                for lab, ev in labels:
                    if lab == want:
                        return lab, f"{nm}() -> {ev}"
            if labels:
                return "NON_RATIO", f"{nm}() -> {labels[0][1]}"
        # ⚠ AN EXTERNAL CALL IS NOT TRANSPARENT, and v1 treated it as one. `d, lo, hi =
        # opaque_call()` came back NON_RATIO -- a function whose body this reader has never seen,
        # CLEARED. That is the false acquittal the fourth value exists to prevent, and only the
        # planted control found it, because every real case in this corpus happens to call a
        # reduction. So: a stated allowlist of reductions that cannot divide by a DATA quantity is
        # transparent (np.mean divides by a count, which is the safe kind); everything else
        # external is UNRESOLVED.
        if nm in SAFE_REDUCTIONS:
            # `np.mean(x)` puts the operand in args[0]; `x.mean()` puts it in the ATTRIBUTE's base
            # and has NO args. Missing the second form sent 12 keys and 240 checked pairs to
            # UNRESOLVED under a label reading `opaque call mean()` -- a reduction on the allowlist,
            # reported as unreadable, because of where the operand sits in the tree.
            operand = expr.args[0] if expr.args else (
                f.value if isinstance(f, ast.Attribute) else None)
            if operand is not None:
                return classify_expr(operand, asg, depth + 1, maxdepth, fns, seen)
        if nm not in fns:
            return "UNRESOLVED", f"opaque call {nm or '<expr>'}(), depth {depth}"
    return "NON_RATIO", ast.unparse(expr)[:110]


def classify_key_in_source(src: str, key: str, maxdepth: int = MAXDEPTH):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return "UNRESOLVED", "source does not parse"
    asg, fns = assignments(tree), functiondefs(tree)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    found.append(classify_expr(v, asg, 0, maxdepth, fns))
        elif isinstance(node, ast.Call):                       # dict(delta=..., ...)
            for kw in node.keywords:
                if kw.arg == key:
                    found.append(classify_expr(kw.value, asg, 0, maxdepth, fns))
    if not found:
        return "UNRESOLVED", "key not assigned anywhere in this round's source"
    for want in ("RATIO_DATA", "RATIO_CONST", "UNRESOLVED"):
        for lab, ev in found:
            if lab == want:
                return lab, ev
    return "NON_RATIO", found[0][1]


# ----------------------------------------------------------------------------- controls ---------
def planted_controls():
    """Both directions, and the count/data split gets its own pair. A classifier that returns the
    same label on a division and on a mean measures nothing."""
    cases = [
        ('x = {"delta": d_core / gap}', "delta", "RATIO_DATA"),
        # ⚠ v1 of this case wrote `{"delta": float(np.mean(ds))}` with `ds` UNDEFINED and expected
        # NON_RATIO. The classifier said UNRESOLVED and the classifier was right: an unfollowable
        # name is not a cleared name, and clearing it is exactly the false acquittal the fourth
        # value exists to prevent. MY EXPECTATION WAS THE DEFECT, not the instrument -- realstat §4,
        # `the control fails for its own reasons`, in its flattering-to-nobody direction. The case
        # is kept with `ds` defined, and the undefined form is now its own case two rows down.
        ('ds = a - b\nx = {"delta": float(np.mean(ds))}', "delta", "NON_RATIO"),
        ('x = {"delta": float(np.mean(ds))}', "delta", "UNRESOLVED"),
        ('ds = a / b\nx = {"delta": float(np.mean(ds))}', "delta", "RATIO_DATA"),
        ('x = {"delta": total / len(rows)}', "delta", "RATIO_CONST"),
        ('r = a - b\nx = {"delta": r}', "delta", "NON_RATIO"),          # follow a Name
        ('r = a / b\nx = {"delta": r}', "delta", "RATIO_DATA"),         # ...and it must still fire
        ('x = {"delta": np.divide(a, b)}', "delta", "RATIO_DATA"),      # spelled-out division
        ('x = {"other": a / b}', "delta", "UNRESOLVED"),                # key absent -> never clean
        ('x = {"delta": some_opaque_name}', "delta", "UNRESOLVED"),     # unfollowable -> never clean
        # the two capabilities added after the first run. Each is asserted in BOTH directions,
        # because a reader that gains a power gains a way to be wrong with it.
        ('m, lo, hi = p / q\nx = {"delta": m}', "delta", "RATIO_DATA"),   # tuple unpack, ratio
        ('m, lo, hi = p - q\nx = {"delta": m}', "delta", "NON_RATIO"),    # tuple unpack, difference
        ('def ci(v):\n    return v / w\nm, lo, hi = ci(z)\nx = {"delta": m}',
         "delta", "RATIO_DATA"),                                          # division inside a helper
        ('def ci(v):\n    return v - w\nm, lo, hi = ci(z)\nx = {"delta": m}',
         "delta", "NON_RATIO"),                                           # ...and it must not fire
        ('def f():\n    return f()\nx = {"delta": f()}', "delta", "NON_RATIO"),   # recursion halts
        # POSITIONAL binding, the third capability. R127's real shape: the only division is in the
        # LAST slot and the checked key is the FIRST, so a positional reader must not fire...
        ('def pb():\n    return (np.mean(dd), lo, hi, max(p, 1.0 / (n + 1)))\n'
         'd, lo2, hi2, pv = pb()\nx = {"delta": d}', "delta", "NON_RATIO"),
        # ...and must still fire when the division IS in the slot being read.
        ('def pb():\n    return (a / b, lo, hi, pv)\nd, lo2, hi2, p2 = pb()\nx = {"delta": d}',
         "delta", "RATIO_DATA"),
        ('d, lo, hi = (a / b, x, y)\nx2 = {"delta": d}', "delta", "RATIO_DATA"),
        ('d, lo, hi = (a - b, x, y / z)\nx2 = {"delta": d}', "delta", "NON_RATIO"),
        # ...and where the shape is UNKNOWABLE it must fall back to over-detecting, not to clean.
        ('d, lo, hi = opaque_call()\nx = {"delta": d}', "delta", "UNRESOLVED"),
        ('x = {"delta": 1.0 / (n + 1)}', "delta", "RATIO_CONST"),   # count arithmetic, not data
        # METHOD form of a reduction: the operand is the attribute base, not an argument.
        ('r = a - b\nx = {"delta": r.mean()}', "delta", "NON_RATIO"),
        ('r = a / b\nx = {"delta": r.mean()}', "delta", "RATIO_DATA"),
        ('x = {"delta": r.mean()}', "delta", "UNRESOLVED"),          # ...operand still unfollowable
    ]
    rows, ok = [], True
    for src, key, want in cases:
        got, _ev = classify_key_in_source(src, key)
        rows.append((src.replace("\n", " ; ")[:44], want, got, got == want))
        ok &= (got == want)
    return ok, rows


def real_controls():
    """Two KNOWN cases from this repo, because a control validated only on cases I invented is
    validated against my imagination (realstat §4)."""
    out = []
    r235 = ROOT / "E05_the_space_of_compilers/A19_triple_blind/R235_independent_B/run.py"
    r141 = ROOT / "E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/R141_verification/run.py"
    if r235.exists():
        lab, ev = classify_key_in_source(r235.read_text(encoding="utf-8", errors="replace"), "eta")
        out.append(("R235 `eta` (d_core/gap -- diagnosed at R341)", "RATIO_DATA", lab, ev))
    if r141.exists():
        lab, ev = classify_key_in_source(r141.read_text(encoding="utf-8", errors="replace"),
                                         "delta_mean")
        out.append(("R141 `delta_mean` (np.mean(ds))", "NON_RATIO", lab, ev))
    ok = bool(out) and all(want == got for _l, want, got, _e in out)
    return ok, out


def main() -> int:
    print(f"R342 · how many CHECKED points are ratios?   guard sha256[:12] = {GUARD_HASH}\n")

    p_ok, p_rows = planted_controls()
    print("  PLANTED CONTROLS, both directions and the count/data split:\n")
    print(f"    {'source':<46}{'want':<13}{'got':<13}")
    for src, want, got, ok in p_rows:
        print(f"    {src:<46}{want:<13}{got:<13}{'OK' if ok else 'MISMATCH'}")
    print(f"  -> {'PASS' if p_ok else 'FAIL'}")

    r_ok, r_rows = real_controls()
    print("\n  REAL CONTROLS, two cases from this repo whose answer is already known:")
    for label, want, got, ev in r_rows:
        print(f"    {label:<46}want {want:<12}got {got:<12}{'OK' if want == got else 'MISMATCH'}")
        print(f"        {ev}")
    print(f"  -> {'PASS' if r_ok else 'FAIL'}")

    pairs = checked_pairs()
    if not pairs:
        print("\n  UNRUNNABLE: the guard checks no pairs. Exit 2, never 0.")
        return 2
    distinct = sorted({(rid, mk) for rid, mk, _ck, _r in pairs})
    print(f"\n  {len(pairs)} checked pairs -> {len(distinct)} distinct (round, mean_key)\n")

    # source per round, once
    src_cache: dict[str, str | None] = {}
    for rid, _mk in distinct:
        if rid in src_cache:
            continue
        hits = list(ROOT.glob(f"E*/A*/{rid}/run.py"))
        src_cache[rid] = hits[0].read_text(encoding="utf-8", errors="replace") if hits else None

    counts = {"RATIO_DATA": 0, "RATIO_CONST": 0, "NON_RATIO": 0, "UNRESOLVED": 0}
    rows = []
    npairs = {}
    for rid, mk, _ck, _r in pairs:
        npairs[(rid, mk)] = npairs.get((rid, mk), 0) + 1
    for rid, mk in distinct:
        src = src_cache[rid]
        if src is None:
            lab, ev = "UNRESOLVED", "no run.py for this round"
        else:
            lab, ev = classify_key_in_source(src, mk)
        counts[lab] += 1
        rows.append({"rid": rid, "mean_key": mk, "label": lab, "evidence": ev,
                     "n_checked_pairs": npairs[(rid, mk)]})

    print(f"    {'label':<13}{'keys':>6}{'checked pairs':>15}")
    for lab in ("RATIO_DATA", "RATIO_CONST", "NON_RATIO", "UNRESOLVED"):
        npair = sum(r["n_checked_pairs"] for r in rows if r["label"] == lab)
        print(f"    {lab:<13}{counts[lab]:>6}{npair:>15}")
    unres_share = counts["UNRESOLVED"] / len(distinct)

    # ---- SPECIFICATION CURVE over the one tunable this instrument has --------------------------
    # MAXDEPTH decides how far a bare Name is followed. It is the only knob here, and a knob whose
    # value is CHOSEN rather than SWEPT is where a convenient answer comes from. The whole curve is
    # printed, including any depth that changes the verdict.
    print("\n  SPECIFICATION CURVE over MAXDEPTH -- the only tunable, so it is swept, not picked:\n")
    print(f"    {'depth':>6}{'RATIO_DATA':>12}{'RATIO_CONST':>13}{'NON_RATIO':>11}{'UNRESOLVED':>12}")
    curve = {}
    for d in (1, 2, 3, 4, 6, 10):
        c = {"RATIO_DATA": 0, "RATIO_CONST": 0, "NON_RATIO": 0, "UNRESOLVED": 0}
        for rid, mk in distinct:
            s = src_cache[rid]
            lab = "UNRESOLVED" if s is None else classify_key_in_source(s, mk, d)[0]
            c[lab] += 1
        curve[d] = c
        mark = "   <- reported" if d == MAXDEPTH else ""
        print(f"    {d:>6}{c['RATIO_DATA']:>12}{c['RATIO_CONST']:>13}{c['NON_RATIO']:>11}"
              f"{c['UNRESOLVED']:>12}{mark}")
    signs = {tuple(sorted(c.items())) for c in curve.values()}
    ratio_at_any_depth = max(c["RATIO_DATA"] for c in curve.values())
    print(f"    -> RATIO_DATA is {sorted({c['RATIO_DATA'] for c in curve.values()})} across the "
          f"curve; the verdict below does not depend on the knob unless that set has >1 value.")

    for lab in ("RATIO_DATA", "RATIO_CONST", "UNRESOLVED"):
        sel = [r for r in rows if r["label"] == lab]
        if not sel:
            continue
        print(f"\n  {lab} ({len(sel)}):")
        for r in sorted(sel, key=lambda r: -r["n_checked_pairs"])[:12]:
            print(f"      {r['rid']}:{r['mean_key']}  ({r['n_checked_pairs']} pair(s))")
            print(f"          {r['evidence']}")

    # ---- ADJUDICATION BY READING, and the line where instrument repair had to stop ---------------
    # Four repairs were made to this reader while the round ran: tuple targets, local function
    # bodies, positional binding, and the method form of a reduction. Each was forced by a PLANTED
    # CONTROL failing or by a conservatism this file had already declared in writing -- never by
    # disliking the number. Each moved the count, which is the finding about this class of
    # instrument as much as any census is.
    #
    # The FIFTH repair would have been different in kind, and it is not made. R06 is flagged
    # RATIO_DATA on `wins / max(n, 1) - wins_b / max(n_b, 1)` (run.py:210-211). `max(count, 1)` is
    # bounded below by one, so the denominator cannot approach zero and the pathology cannot occur.
    # Teaching the reader about `max(x, c)` would be a rule added AFTER seeing which case it
    # clears, which is a threshold chosen to fit a result. So the rule stays, the flag stands, and
    # the case is adjudicated where the design always said it would be -- in the source, by a read,
    # labelled a judgement rather than folded into a count.
    adjudicated = []
    for r in rows:
        if r["label"] == "RATIO_DATA" and r["rid"].startswith("R06_"):
            adjudicated.append({
                "rid": r["rid"], "key": r["mean_key"], "flag": "RATIO_DATA",
                "read": "run.py:210-211 -- denominators are max(count, 1), bounded below by 1",
                "judgement": "SAFE: the denominator cannot approach zero",
                "kind": "source read, not a rule change"})
    if adjudicated:
        print("\n  ADJUDICATED BY SOURCE READ (the flag stands; the judgement is separate):")
        for a in adjudicated:
            print(f"      {a['rid']}:{a['key']}  flagged {a['flag']}")
            print(f"          {a['read']}")
            print(f"          -> {a['judgement']} ({a['kind']})")

    # ---- the cross-instrument prediction, which is what makes this severe ------------------------
    print("\n  CROSS-INSTRUMENT CHECK. A live ratio should ALSO show a large |offcentre| on the")
    print("  ARTIFACT side (R340's table). Agreement is weak evidence; DISAGREEMENT would mean the")
    print("  framing is the finding and neither count is reportable.")
    tri = ROOT / "assurance" / "interval_is_centred_on_its_point.py"
    hi_rounds = set()
    if tri.exists():
        spec = importlib.util.spec_from_file_location("tri", tri)
        m = importlib.util.module_from_spec(spec)
        sys.argv = ["tri"]
        with contextlib.redirect_stdout(io.StringIO()):
            spec.loader.exec_module(m)
            coh = m._load("artifacts_are_internally_coherent")
            rr = coh.scan(ROOT)
        import statistics as st
        by = {}
        for rid, _p, mv, (lo, hi) in rr["all_pairs"]:
            oc = m.offcentre(mv, lo, hi)
            if oc is not None:
                by.setdefault(rid, []).append(abs(oc))
        hi_rounds = {k for k, v in by.items() if st.median(v) > m.BOUND}
    ratio_rounds = {r["rid"] for r in rows if r["label"] == "RATIO_DATA"}
    print(f"      rounds the ARTIFACT side calls off-centre : {sorted(hi_rounds) or '(none)'}")
    print(f"      rounds the SOURCE side calls RATIO_DATA   : {sorted(ratio_rounds) or '(none)'}")
    contradiction = sorted(ratio_rounds - hi_rounds)
    print(f"      ratio rounds the artifact side says are CENTRED: {contradiction or '(none)'}")

    # ---- the pre-registered kill -----------------------------------------------------------------
    print()
    if not (p_ok and r_ok):
        print("  UNVERIFIED: a control misbehaved, so the census above is silence.")
        verdict = "UNVERIFIED"
    elif unres_share > 0.25:
        print(f"  W3. UNRESOLVED is {unres_share:.0%} of the checked keys, above the 25% pre-registered")
        print(f"  ceiling. The instrument is the limit: RATIO_DATA is between {counts['RATIO_DATA']} and")
        print(f"  {counts['RATIO_DATA'] + counts['UNRESOLVED']}. A point estimate here would be a guess wearing a count's clothes.")
        verdict = "W3_BOUND_ONLY"
    elif counts["RATIO_DATA"] >= 1:
        print(f"  W2 -- CONTAMINATED. {counts['RATIO_DATA']} checked key(s) are live ratios, covering")
        print(f"  {sum(r['n_checked_pairs'] for r in rows if r['label'] == 'RATIO_DATA')} of the "
              f"{len(pairs)} checked pairs. For those, a violation is a FALSE CONVICTION and a pass")
        print("  is meaningless. The guard's coverage must be reported net of them.")
        verdict = "W2_CONTAMINATED"
    else:
        print(f"  W1 -- NAMED BUT DORMANT. Zero of {len(distinct)} checked keys are live ratios")
        print(f"  ({unres_share:.0%} unresolved, under the 25% ceiling). The exception class R341")
        print("  found is real and has never touched a verdict this suite published.")
        verdict = "W1_DORMANT"

    art = {
        "guard_sha256_12": GUARD_HASH,
        "checked_pairs": len(pairs), "distinct_keys": len(distinct),
        "counts": counts, "unresolved_share": unres_share,
        "maxdepth_curve": {str(k): v for k, v in curve.items()},
        "ratio_data_at_any_depth": ratio_at_any_depth,
        "controls": {"planted": p_ok, "real": r_ok},
        "planted_rows": [{"src": s, "want": w, "got": g} for s, w, g, _ in p_rows],
        "real_rows": [{"label": l, "want": w, "got": g} for l, w, g, _ in r_rows],
        "artifact_side_offcentre_rounds": sorted(hi_rounds),
        "source_side_ratio_rounds": sorted(ratio_rounds),
        "contradiction": contradiction,
        "adjudicated": adjudicated,
        "repair_ledger": [
            {"repair": "tuple-unpack targets", "forced_by": "7 of 9 UNRESOLVED were `d, lo, hi = ...`"},
            {"repair": "local function bodies", "forced_by": "the division lives inside ci()/paired()"},
            {"repair": "positional tuple binding", "forced_by": "planted+cross-instrument: R127's "
                                                                "1.0/(n+1) belonged to slot 4"},
            {"repair": "method form of a reduction", "forced_by": "planted control: x.mean() has "
                                                                  "no args, operand is the base"},
            {"repair": "NOT MADE: max(x, c) as a bounded denominator",
             "forced_by": "would be a rule chosen after seeing which case it clears"},
        ],
        "verdict": verdict, "rows": rows,
    }
    outp = HERE / "results" / "r342_ratio_census.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE. This reads CONSTRUCTION, not meaning. RATIO_CONST is a name-based judgement")
    print("    (a denominator is a count if it is a literal, a len(), or one of a stated list), and")
    print("    a round that divides by a data quantity which happens never to approach zero is")
    print("    counted RATIO_DATA here and is nonetheless safe. This bounds the exposure; it does")
    print("    not enumerate the harm.")
    return 0 if (p_ok and r_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
