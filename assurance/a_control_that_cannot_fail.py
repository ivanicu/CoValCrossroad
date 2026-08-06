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


def main(argv):
    dirs = argv[1:] or ["corebench", "assurance"]
    mods = sorted(p for d in dirs for p in pathlib.Path(d).rglob("*.py"))
    rows, scanned = [], 0
    for m in mods:
        h = audit(m.read_text(errors="ignore"))
        if h is None:
            continue
        scanned += 1
        if h:
            rows.append((m.name, h))
    if scanned == 0:                       # §4: an empty population must not pass
        print("  ⛔ EMPTY POPULATION -- nothing was examined. Exit 2, never 0.")
        return 2
    names = {r[0] for r in rows}
    pos, neg = POS_CTRL in names, NEG_CTRL not in names
    print(f"  population: {scanned} modules parsed under {dirs}")
    print(f"  POSITIVE CONTROL {POS_CTRL} flagged: {pos}   "
          f"{'PASS' if pos else 'FAIL — the scan is blind'}")
    print(f"  NEGATIVE CONTROL {NEG_CTRL} NOT flagged: {neg}   "
          f"{'PASS' if neg else 'FAIL — the scan over-fires'}")
    print(f"\n  CONTROLS THAT CANNOT FAIL: {len(rows)} module(s)")
    for n, h in rows:
        for name, line, expr, why in h:
            print(f"     {n}:{line}  `{name}`  contains  {expr}   ->  {why}")
    print("\n  ⚠ LIMIT: sound in ONE direction. A flag PROVES constancy; the absence of a flag "
          "proves\n     nothing, because constancy has forms this syntactic rule cannot see. "
          "Never report\n     this scan's silence as 'the remaining controls can fail'.")
    if not (pos and neg):
        print("\n  ⛔ a control failed — this scan's findings are INADMISSIBLE. Exit 2, never 0.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
