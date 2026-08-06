#!/usr/bin/env python3
"""assurance/a_control_that_cannot_fail.py -- a control whose value is forced by the algebra.

§4's FIRST row (`check that cannot fail`, built 4x caught 4x) crossed with §0's ARITHMETIC TRAP:
a control is registered in the docstring, computed, printed PASS -- and its expression contains
`a - a` or `a / a`, so it is 0 or 1 for EVERY possible input. It tests floating-point arithmetic,
not the instrument. A PASS from it is a derivation wearing a measurement's clothes.

FOUND BY: the `cannot judge` bucket of assurance/kill_is_wired_into_the_branch.py. Three modules
had flags and no verdict chain. Two (score.py, select_core.py) are a scorer and a builder and
correctly have no verdict. The third, price_of_annotation.py, is a full round -- and its two
registered controls read, verbatim at lines 71-72:

    okT = abs(((T-R).mean()/(T-R).mean()) - 1.0) < 1e-12   # POSITIVE: "topw against itself = 1.0"
    okR = abs(((R-R).mean())) < 1e-12                       # PLACEBO:  "random against itself = 0"

GAUGE TEST (rung 1, zero compute): 2000 worlds with T and R drawn independently -- no relationship
between the arms at all -- gave **0 failures out of 2000 for each**. okT fails only when the
denominator is identically zero, i.e. 0/0 -> nan, which is a crash and not a diagnostic. The
MEASUREMENT is invariant under every transformation of the data; the PROPERTY (is the share's
scale anchored?) is not. Measurement invariant + property not => the measurement is BLIND.

⚠ AND THE DOCSTRING'S INTENT IS ALSO A DERIVATION, so this is not a typo. "topw against itself
  must give a share of exactly 1.0" is a property of the RATIO FORMULA, true before any data is
  read. Fixing the code cannot rescue it; the control has to be replaced by one that could return
  something else -- e.g. recomputing the share on an arm whose advantage is KNOWN by construction.

ESTIMAND        per module: names assigned a boolean expression containing a binary operation
                whose two operands are syntactically identical under `-` or `/`. Named first.
IDENTIFICATION  SOUND IN ONE DIRECTION ONLY (P6 proxy ledger).
                  flagged     => the sub-expression is constant                    CONFIRMED
                  not flagged => nothing. Constancy has infinitely many other forms UNVERIFIED
                A count from this scan is a LOWER bound on the defect and an UPPER bound on
                nothing. It may never be reported as "the other controls can fail".
POPULATION      .py files under the directories given (default: corebench assurance).
POSITIVE CTRL   price_of_annotation.py MUST be flagged -- it is the case that motivated the scan
                and its constancy is established by the 2000-world gauge test above, not by
                reading. If it is not flagged the scan is blind.
NEGATIVE CTRL   is_importance_recoverable.py MUST NOT be flagged. Its ok_neg compares a shuffled
                target's mean to 0.02, which is a real quantity that has returned both signs.
                If it is flagged the scan is over-firing.
⚠ BOTH CONTROLS ARE REQUIRED. A positive control bounds blindness; only a known-clean case bounds
  noise. The sibling scan kill_is_wired_into_the_branch.py reported a 1-in-2 false positive rate
  with a PASSING positive control, which is why one-sided validation is not accepted here.
"""
from __future__ import annotations
import ast, pathlib, sys

POS_CTRL, NEG_CTRL = "price_of_annotation.py", "is_importance_recoverable.py"
CONSTANT_OPS = {ast.Sub: "a - a is identically 0", ast.Div: "a / a is identically 1"}


def _boolish(v) -> bool:
    return isinstance(v, (ast.Compare, ast.BoolOp)) or (
        isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
        and v.func.id in ("all", "any", "bool"))


def constant_subexprs(node):
    """every `a OP a` under this node, OP in {-, /}, compared by unparsed source."""
    out = []
    for n in ast.walk(node):
        if isinstance(n, ast.BinOp) and type(n.op) in CONSTANT_OPS:
            try:
                l, r = ast.unparse(n.left), ast.unparse(n.right)
            except Exception:
                continue
            if l == r:
                out.append((ast.unparse(n), CONSTANT_OPS[type(n.op)]))
    return out


def audit(src: str):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    hits = []
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Assign) and _boolish(n.value)):
            continue
        names = [t.id for t in n.targets if isinstance(t, ast.Name)]
        for expr, why in constant_subexprs(n.value):
            hits.append((names[0] if names else "<unnamed>", n.lineno, expr, why))
    return hits


# ⛔ THE FILE-BASED CONTROLS ARE CONTINGENT ON THIS REPOSITORY'S HISTORY, AND THAT IS A DEFECT.
#    `price_of_annotation.py` was introduced 2026-08-03T09:34, eleven hours before the earliest of
#    the six rounds this gate exists to catch (R332, 2026-08-03T20:47). It happened to be there.
#    Had this gate been written a day earlier it would have exited 2 -- "the scan is blind" --
#    permanently, on a corpus where it detects the defect perfectly well. And it cannot be pointed
#    at any OTHER corpus at all. A positive control that is a FILE validates the population, never
#    the rule.
#    R829 demonstrated the remedy one round earlier: SYNTHETIC PLANTS, one per form, carried inside
#    the module. These validate the RULE and are independent of every corpus, so the file controls
#    can now degrade to N/A when absent instead of manufacturing a blind verdict. The two changes
#    are inseparable: N/A without a synthetic control would be `empty population passes`.
SYNTH = {
    "a / a is identically 1": "def f():\n    ok = (d.mean() / d.mean()) == 1.0\n    return ok\n",
    "a - a is identically 0": "def f():\n    ok = abs(v - v) < 1e-09\n    return ok\n",
}
SYNTH_CLEAN = "def f():\n    ok = abs(left.mean() - right.mean()) < 1e-09\n    return ok\n"


def synthetic_controls():
    """validate the RULE, not the population. Corpus-independent by construction."""
    fired = {}
    for why, code in SYNTH.items():
        h = audit(code) or []
        fired[why] = any(w == why for _, _, _, w in h)
    clean_ok = not (audit(SYNTH_CLEAN) or [])
    return fired, clean_ok


def main(argv):
    dirs = argv[1:] or ["corebench", "assurance"]
    mods = sorted(p for d in dirs for p in pathlib.Path(d).rglob("*.py"))
    # ⛔ THE CONTROLS MUST BE IN THE POPULATION OR THEY MEASURE NOTHING. Pointed at the arc
    #    directories alone, this gate exited 2 with "the scan is blind" -- correct, but the cause
    #    was that POS_CTRL lives under corebench/ and was simply not scanned. That is the same
    #    defect as a positive control whose object sits outside the scanned set. The controls now
    #    travel with the gate, so the population can never exclude them.
    requested = set(mods)                  # what the CALLER asked to scan, before controls travel
    have = {p.name for p in mods}
    for ctrl in (POS_CTRL, NEG_CTRL):
        if ctrl not in have:
            mods += sorted(pathlib.Path(".").rglob(ctrl))
    rows, scanned, req_scanned = [], 0, 0
    for m in mods:
        h = audit(m.read_text(errors="ignore"))
        if h is None:
            continue
        scanned += 1
        req_scanned += m in requested
        if h:
            rows.append((m.name, h))
    # ⛔ §4 `empty population passes`, AND I BUILT IT MYSELF TWO ROUNDS AGO. Making the controls
    #    TRAVEL fixed one defect and created this one: `scanned` counted the appended control files,
    #    so an empty target directory came back as 2 modules and exited 0. The guard has to test the
    #    REQUESTED population, never the augmented one. Caught by attack vector 3, not by a run.
    if req_scanned == 0:
        print(f"  ⛔ EMPTY POPULATION -- {dirs} contains no parseable module. "
              f"The controls travel with the gate and must not be counted as coverage. "
              f"Exit 2, never 0.")
        return 2
    names = {r[0] for r in rows}
    present = {p.name for p in mods}
    print(f"  population: {scanned} modules parsed under {dirs}")

    # ---- SYNTHETIC controls first: they validate the RULE and hold on any corpus.
    fired, synth_clean = synthetic_controls()
    for why, ok in fired.items():
        print(f"  SYNTHETIC POSITIVE  a plant of `{why}` -> "
              f"{'flagged, reason named   PASS' if ok else '⛔ MISSED — the rule is blind'}")
    print(f"  SYNTHETIC g=0       two DIFFERENT operands -> "
          f"{'not flagged   PASS' if synth_clean else '⛔ FLAGGED — the rule over-fires'}")
    synth_ok = all(fired.values()) and synth_clean

    # ---- FILE controls second: they validate THIS corpus, and degrade to N/A when absent.
    pos = POS_CTRL in names if POS_CTRL in present else None
    neg = (NEG_CTRL not in names) if NEG_CTRL in present else None
    print(f"  CORPUS POSITIVE  {POS_CTRL} flagged: "
          f"{'N/A — not in this population' if pos is None else pos}   "
          f"{'skipped' if pos is None else ('PASS' if pos else 'FAIL — blind on this corpus')}")
    print(f"  CORPUS NEGATIVE  {NEG_CTRL} NOT flagged: "
          f"{'N/A — not in this population' if neg is None else neg}   "
          f"{'skipped' if neg is None else ('PASS' if neg else 'FAIL — over-fires here')}")
    pos = True if pos is None else pos
    neg = True if neg is None else neg
    print(f"\n  CONTROLS THAT CANNOT FAIL: {len(rows)} module(s)")
    for n, h in rows:
        for name, line, expr, why in h:
            print(f"     {n}:{line}  `{name}`  contains  {expr}   ->  {why}")
    print("\n  ⚠ LIMIT: sound in ONE direction. A flag PROVES constancy; the absence of a flag "
          "proves\n     nothing, because constancy has forms this syntactic rule cannot see. "
          "Never report\n     this scan's silence as 'the remaining controls can fail'.")
    if not (synth_ok and pos and neg):
        print("\n  ⛔ a control failed — this scan's findings are INADMISSIBLE. Exit 2, never 0.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
