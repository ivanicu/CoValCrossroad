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
LIMIT           the flag list is a NAME HEURISTIC. A check stored under a name outside FLAGISH is
                invisible here, so a clean report is not a clean bill -- it is silence about the
                names not searched. Counts from this scan do not extrapolate to other directories.
"""
from __future__ import annotations
import ast, pathlib, sys

FLAGISH = ("_ok", "fires", "monotone", "gate", "passed", "valid", "sane", "survives", "admissible")
VERDICT_WORDS = ("VERDICT", "WORLD", "BLIND", "UNVERIFIED", "OVERTURNED", "CONFIRMED", "KILL")
POS_CTRL, NEG_CTRL = "synthetic_world.py", "pairwise_matrix.py"


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
    flags = {t.id for n in ast.walk(tree) if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name) and any(k in t.id for k in FLAGISH)}
    if not flags:
        return set(), set(), False
    used, found = set(), False
    seen = set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.If) or id(n) in seen:
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
    print(f"\n  modules whose verdict chain ignores a flag it computed: {len(hits)} of {len(rows)}")
    for n, f, u, o in hits:
        print(f"     {n:<34} chain tests={u}\n     {'':34} ORPHANED={o}")
    if unjudgeable:
        print(f"\n  ⚠ cannot judge (flags, no verdict chain found): {unjudgeable}")
    print("\n  ⚠ LIMIT: the flag list is a name heuristic. A clean report is silence about the "
          "names\n     not searched, never a clean bill.")
    if not (pos and neg):
        print("\n  ⛔ a control failed — this scan's findings are INADMISSIBLE. Exit 2, never 0.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
