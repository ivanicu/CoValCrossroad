#!/usr/bin/env python3
"""assurance/kill_is_wired_into_the_branch.py -- a computed check that never reaches a condition.

§4's `the verdict string is not a computation`: a module computes a flag, prints it PASS/FAIL, and
then branches its verdict on something else. The flag looks like a control and licenses nothing.

⛔ THE FIRST VERSION OF THIS SCAN HAD A 1-IN-2 FALSE POSITIVE RATE ON ITS OWN FINDINGS. It collected
   names from `n.test` only for `If` nodes whose BODY contained a verdict keyword. In an
   `if / elif / else` chain the outermost test guards a body that may say UNVERIFIED rather than
   WORLD -- so the scan skipped the `if`, scored the `elif`, and reported the outermost flag as
   orphaned. `pairwise_matrix.py` was flagged that way and is CLEAN: `pos_ok` gates its chain.
   A passing POSITIVE control did not prevent this: it showed the scan could SEE one case, never
   that its rule was right. That is why this version carries a NEGATIVE control too.

ESTIMAND        per module: computed flag names absent from EVERY test in the chain that decides
                the verdict. Named before the method.
POPULATION      the .py files under the directories given on the command line (default: corebench).
POSITIVE CTRL   synthetic_world.py MUST be flagged: it computes dose_ok and monotone, prints both,
                and branches on `fires` alone. If it is not flagged the scan is blind.
NEGATIVE CTRL   pairwise_matrix.py MUST NOT be flagged: `pos_ok` is the outermost test of its
                if/elif/else. If it is flagged the scan is over-firing, which is the defect above.
LIMIT           detection is STRUCTURAL (any name assigned a boolean expression), so it OVER-FIRES
                on loop and helper intermediates. Every hit is a CANDIDATE for adjudication and a
                count is an UPPER BOUND, never a rate. Counts do not extrapolate across directories.
⛔ TWO FURTHER DEFECTS THE SCAN'S OWN OUTPUT EXPOSED, both fixed here:
   (a) `if __name__ == "__main__":` was being matched as a verdict chain, because the verdict
       string lives inside its body. Three of four "candidates" were that. The guard is now skipped.
   (b) a verdict decided by a TERNARY (`v = A if cond else B`) is an ast.IfExp, not an ast.If, and
       was invisible. is_importance_recoverable.py decides that way -- the finding there was real
       and the scan had reached it for the wrong reason. IfExp is now walked too.

⭐ ADJUDICATION RECORD -- read this before believing any count. Every hit is a CANDIDATE and 3 of
   the 5 this scan produced needed a human read to dismiss or reclassify:
     synthetic_world.py          REAL, unmarked   `dose_ok` IS its docstring's registered kill,
                                                  computed, printed FAIL, absent from the branch.
     is_importance_recoverable.py REAL, unmarked  ok_pos/ok_neg/ok_pla all orphaned; the ternary
                                                  tests d.max() alone.
     dimension_curve.py          REAL, SELF-DISCLOSED  `ok` is a per-dimension control the verdict
                                                  does not consult -- and the module says so in a
                                                  comment at the decision point. A documented
                                                  limitation is not the same defect as a silent one.
     learned_core.py             FALSE POSITIVE   `ok`/`items` are LOOP VARIABLES (`for pid, items,
                                                  ok in test:`); the verdict tests `lo > 0`.
     unit_robustness.py          FALSE POSITIVE   `both`/`ok` are per-pair/per-unit loop
                                                  descriptors; the verdict tests its inversion rule.
   So: 2 unmarked defects, 1 self-disclosed, 2 artifacts, out of 8 judgeable. The raw count of 5
   OVERSTATES by 2, and across four versions of this scan the number ran 2 -> 1 -> 4 -> 5 -> 2,
   every change caused by fixing the INSTRUMENT and none by new evidence. ADJUDICATION IS THE
   MEASUREMENT; the scan only generates candidates.
"""
from __future__ import annotations
import ast, pathlib, sys

VERDICT_WORDS = ("VERDICT", "WORLD", "BLIND", "UNVERIFIED", "OVERTURNED", "CONFIRMED", "KILL")
POS_CTRL, NEG_CTRL = "synthetic_world.py", "pairwise_matrix.py"


def _boolish(v) -> bool:
    return isinstance(v, (ast.Compare, ast.BoolOp)) or (
        isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
        and v.func.id in ("all", "any", "bool"))


def chain(node: ast.If):
    """every If in one if/elif/else chain -- elif is an If inside orelse."""
    out = [node]
    while (len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)):
        node = node.orelse[0]
        out.append(node)
    return out


def audit(src: str):
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    # ⛔ THE NAME HEURISTIC IS RETIRED. It had `_ok` and missed `ok_pos`/`ok_neg`/`ok_pla` --
    #    is_importance_recoverable.py's ENTIRE control block -- on one character of prefix order,
    #    in a module whose verdict this project had already folded into its deliverable.
    #    Detection is now STRUCTURAL: a flag is any name assigned a boolean-valued expression.
    #    That is complete over boolean assignments and OVER-FIRES on intermediates, so every hit
    #    is a CANDIDATE requiring adjudication, never a finding.
    flags = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name) and _boolish(n.value)}
    if not flags:
        return set(), set(), False
    used, found = set(), False
    seen = set()
    # ⭐ a verdict decided by a TERNARY is an IfExp, not an If -- walk those first
    for n in ast.walk(tree):
        if isinstance(n, ast.IfExp):
            body = ast.dump(n.body) + ast.dump(n.orelse)
            if any(w in body for w in VERDICT_WORDS):
                found = True
                for m in ast.walk(n.test):
                    if isinstance(m, ast.Name):
                        used.add(m.id)
    for n in ast.walk(tree):
        if not isinstance(n, ast.If) or id(n) in seen:
            continue
        # ⛔ skip the module guard: its body contains the verdict but it decides nothing
        if (isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Name)
                and n.test.left.id == "__name__"):
            continue
        ch = chain(n)
        for c in ch:
            seen.add(id(c))
        # ⭐ the whole chain decides together: dump every branch body, not just the first
        bodies = "".join(ast.dump(ast.Module(body=c.body, type_ignores=[])) for c in ch)
        bodies += "".join(ast.dump(ast.Module(body=ch[-1].orelse, type_ignores=[])))
        if any(w in bodies for w in VERDICT_WORDS):
            found = True
            for c in ch:                      # names from EVERY test in the chain
                for m in ast.walk(c.test):
                    if isinstance(m, ast.Name):
                        used.add(m.id)
    return flags, used, found


def main(argv):
    dirs = argv[1:] or ["corebench"]
    mods = sorted(p for d in dirs for p in pathlib.Path(d).rglob("*.py"))
    rows, unjudgeable = [], []
    for m in mods:
        r = audit(m.read_text(errors="ignore"))
        if r is None:
            continue
        flags, used, found = r
        if not flags:
            continue
        if not found:
            unjudgeable.append(m.name); continue
        orphan = sorted(flags - used)
        rows.append((m.name, sorted(flags), sorted(used), orphan))
    hits = [r for r in rows if r[3]]
    names = {r[0] for r in hits}
    pos = POS_CTRL in names
    neg = NEG_CTRL not in {r[0] for r in rows} or NEG_CTRL not in names
    print(f"  population: {len(mods)} modules under {dirs} · {len(rows)} judgeable · "
          f"{len(unjudgeable)} with flags but no locatable verdict chain")
    print(f"  POSITIVE CONTROL {POS_CTRL} flagged: {pos}   "
          f"{'PASS' if pos else 'FAIL — the scan is blind'}")
    print(f"  NEGATIVE CONTROL {NEG_CTRL} NOT flagged: {neg}   "
          f"{'PASS' if neg else 'FAIL — the scan over-fires'}")
    print(f"\n  CANDIDATES -- verdict chains ignoring a boolean they computed (adjudicate each): {len(hits)} of {len(rows)}")
    for n, f, u, o in hits:
        print(f"     {n:<34} chain tests={u}\n     {'':34} ORPHANED={o}")
    if unjudgeable:
        print(f"\n  ⚠ cannot judge (flags, no verdict chain found): {unjudgeable}")
    print("\n  ⚠ LIMIT: structural detection is complete over boolean assignments and OVER-FIRES on "
          "loop\n     and helper intermediates. Each hit is a CANDIDATE. A count from this scan is "
          "an\n     upper bound, never a rate.")
    if not (pos and neg):
        print("\n  ⛔ a control failed — this scan's findings are INADMISSIBLE. Exit 2, never 0.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
