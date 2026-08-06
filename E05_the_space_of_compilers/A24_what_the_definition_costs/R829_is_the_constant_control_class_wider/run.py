#!/usr/bin/env python3
"""R829 -- is the constant-control class wider than the rule that found it?

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        the count of additional algebraically-constant control expressions under three
                forms the existing `a OP a` rule provably cannot see. Named before the method.
IDENTIFICATION  syntactic only. SEMANTIC constancy is out of reach BY CONSTRUCTION and is what a
                differential detector would address; this round measures whether one is worth
                building, and never substitutes for it.
SCOPE           population corebench + assurance + E01..E05, identical to the run that produced
                the 6, so counts are comparable. instrument: AST over committed source.
                baseline: the existing rule's 6. regime: syntactic.
WORLDS          W-BROADER (>=1 instance -> a differential detector has a target population) vs
                W-SATURATED (0 -> the syntactic width already saturates this corpus).
KILL            CONDITIONAL. Evaluated only if every positive control fires, the g=0 synthetic is
                clean, and the negative control is null. Otherwise UNVERIFIED, and no count is
                reported in either direction.
POSITIVE CTRL   one synthetic source per form; each must be flagged AND its form named.
NEGATIVE CTRL   `a = f(); b = g(); a - b` -- two DIFFERENT producers. Must NOT be flagged. This is
                where a naive alias tracker manufactures a false accusation.
MULTIPLICITY    3 sound forms + 4 NaN-conditional forms, all reported.
ARTIFACT        results/r829_wider_class.json with source hash.
"""
from __future__ import annotations
import ast, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
RES = HERE / "results"

# NaN-conditional: constant EXCEPT at NaN. `x == x` is a legitimate NaN idiom, so treating these
# as constant would be unsound in exactly the direction that manufactures a false accusation.
NAN_COND = {ast.Eq: "x == x", ast.LtE: "x <= x", ast.GtE: "x >= x"}


def _aliases(tree):
    """names bound directly to another name: `a = b`. Only single, unconditional bindings count --
    a name rebound anywhere else is dropped, because then `a - b` is not provably constant."""
    binds, rebound = {}, set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            t = n.targets[0].id
            if t in binds or t in rebound:
                rebound.add(t); binds.pop(t, None); continue
            if isinstance(n.value, ast.Name):
                binds[t] = n.value.id
            else:
                rebound.add(t)
        elif isinstance(n, (ast.AugAssign, ast.For)):
            for m in ast.walk(n.target if isinstance(n, (ast.AugAssign, ast.For)) else n):
                if isinstance(m, ast.Name):
                    rebound.add(m.id); binds.pop(m.id, None)
    return {k: v for k, v in binds.items() if k not in rebound and v not in rebound}


def scan(src: str):
    """returns (sound_hits, nan_conditional_hits). Each hit: (form, lineno, unparsed)."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None, None
    al = _aliases(tree)
    sound, nan = [], []
    for n in ast.walk(tree):
        # ---- F1 ALIASING: `a = b` then `a - b` / `a / b`  (identical in value to `a - a`)
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Sub, ast.Div)):
            l, r = n.left, n.right
            if isinstance(l, ast.Name) and isinstance(r, ast.Name) and l.id != r.id:
                if al.get(l.id) == r.id or al.get(r.id) == l.id:
                    sound.append(("F1_alias", n.lineno, ast.unparse(n)))
        if not isinstance(n, ast.Compare) or len(n.ops) != 1:
            continue
        op, l, r = type(n.ops[0]), n.left, n.comparators[0]
        try:
            ls, rs = ast.unparse(l), ast.unparse(r)
        except Exception:
            continue
        # ---- F2 STRICT SELF-COMPARISON: always False, NaN included
        if op in (ast.Lt, ast.Gt) and ls == rs:
            sound.append(("F2_strict_self", n.lineno, ast.unparse(n)))
        # ---- F3 TYPE-BOUNDED: len() is a non-negative int, so no NaN case exists
        if (isinstance(l, ast.Call) and isinstance(l.func, ast.Name) and l.func.id == "len"
                and isinstance(r, ast.Constant) and isinstance(r.value, int)):
            if (op is ast.GtE and r.value <= 0) or (op is ast.Gt and r.value < 0) \
                    or (op is ast.NotEq and r.value < 0):
                sound.append(("F3_type_bounded", n.lineno, ast.unparse(n)))
        # ---- NaN-CONDITIONAL: counted, labelled, EXCLUDED from the estimand
        if op in NAN_COND and ls == rs:
            nan.append((NAN_COND[op], n.lineno, ast.unparse(n)))
        if (op is ast.GtE and isinstance(l, ast.Call) and isinstance(l.func, ast.Name)
                and l.func.id == "abs" and isinstance(r, ast.Constant) and r.value == 0):
            nan.append(("abs(x) >= 0", n.lineno, ast.unparse(n)))
    return sound, nan


# --------------------------------------------------------------------------- controls
PLANTS = {
    "F1_alias": "def f():\n    b = compute()\n    a = b\n    ok = abs(a - b) < 1e-9\n    return ok\n",
    "F2_strict_self": "def f():\n    ok = score(x) < score(x)\n    return ok\n",
    "F3_type_bounded": "def f():\n    ok = len(rows) >= 0\n    return ok\n",
}
CLEAN = "def f():\n    a = compute_left()\n    b = compute_right()\n    ok = abs(a - b) < 1e-9\n    return ok\n"
NEGATIVE = "def f():\n    a = f1()\n    b = f2()\n    ok = (a - b) == 0 and len(a) > 3 and a < b\n    return ok\n"


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R829 · IS THE CONSTANT-CONTROL CLASS WIDER THAN THE RULE THAT FOUND IT?\n")

    pos = {}
    for form, code in PLANTS.items():
        s, _ = scan(code)
        pos[form] = bool(s) and any(f == form for f, _, _ in s)
        print(f"  POSITIVE  {form:<18} planted -> "
              f"{'flagged, form named   PASS' if pos[form] else '⛔ MISSED — blind for this form'}")
    g0, _ = scan(CLEAN)
    neg, _ = scan(NEGATIVE)
    print(f"  g=0       a clean source (two different producers subtracted) -> "
          f"{'not flagged   PASS' if not g0 else '⛔ FLAGGED — over-fires'}")
    print(f"  NEGATIVE  two DIFFERENT producers, near-miss forms -> "
          f"{'not flagged   PASS' if not neg else '⛔ FLAGGED — a false accusation'}")

    dirs = ["corebench", "assurance"] + sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    mods = sorted(q for d in dirs for q in (ROOT / d).rglob("*.py"))
    hits, nanhits, parsed = [], [], 0
    for m in mods:
        if HERE.name in m.parts:                      # never scan this round's own plants
            continue
        s, nn = scan(m.read_text(errors="ignore"))
        if s is None:
            continue
        parsed += 1
        for form, ln, txt in s:
            hits.append({"file": str(m.relative_to(ROOT)), "line": ln, "form": form, "expr": txt})
        for form, ln, txt in nn:
            nanhits.append({"file": str(m.relative_to(ROOT)), "line": ln, "form": form,
                            "expr": txt})
    if parsed == 0:
        print("\n  ⛔ EMPTY POPULATION — nothing was examined. Exit 2, never 0.")
        return 2
    print(f"\n  population: {parsed} modules parsed under {len(dirs)} directories")

    controls_ok = all(pos.values()) and not g0 and not neg
    if controls_ok:
        world = "W-BROADER" if hits else "W-SATURATED"
        verdict = (f"{len(hits)} instance(s) invisible to the `a OP a` rule -- the class is wider "
                   f"and a differential detector has a target population" if hits else
                   "0 instances under any sound form -- the existing syntactic width already "
                   "saturates this corpus at these forms")
    else:
        world, verdict = "UNVERIFIED", "a control is unfit; the count is NOT reported"
    print(f"\n  SOUND FORMS (the estimand): {len(hits) if controls_ok else 'WITHHELD'}")
    for h in hits[:20]:
        print(f"     {h['file']}:{h['line']}  [{h['form']}]  {h['expr'][:70]}")

    print(f"\n  ⚠ NaN-CONDITIONAL, counted and EXCLUDED from the estimand: {len(nanhits)}")
    byform: dict = {}
    for h in nanhits:
        byform[h["form"]] = byform.get(h["form"], 0) + 1
    for k, v in sorted(byform.items()):
        print(f"     {k:<16} {v}")
    print("     these are constant EXCEPT at NaN, and `x == x` is a legitimate NaN idiom.")
    print("     Calling them constant would be unsound in the direction that manufactures a")
    print("     false accusation -- the failure attack_every_check.py measured at 3 of 6.")

    print(f"\n  VERDICT: {world} -- {verdict}\n")
    out = {"world": world, "verdict": verdict, "n_sound": len(hits) if controls_ok else None,
           "sound": hits if controls_ok else None, "n_nan_conditional": len(nanhits),
           "nan_conditional_by_form": byform, "positive": pos, "g0_clean": not g0,
           "negative_null": not neg, "n_modules": parsed,
           "baseline_a_op_a_rule": 6,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r829_wider_class.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r829_wider_class.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
