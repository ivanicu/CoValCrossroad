#!/usr/bin/env python3
"""A verdict branch may not compare against a BARE literal it invented on the spot.

⛔ WHY, and it is the most-repeated error of this session, measured. **Six times in one session I
assigned a world by comparing a measured quantity to a number I chose in the same line**, named the
error in the report each time, and did it again the next round:
  · R869 `frac < 0.5` · R872 `eo/len >= 0.15` · R875 `rmin < 0.7` · R876 (PR vs a chosen CI) ·
  · R879 (MDE ranking) · **R881 `closest/mde_typ < 0.25`, where the measured value was 0.28 —**
  **0.02 from printing the opposite verdict.**
**Naming it at the moment of commission has not reduced the rate.** So it becomes mechanical.

⭐ **THE RULE, AND THE DISTINCTION IT TURNS ON.** Not every constant is a defect:
  · `lo > 0` · `x != 0` · `n >= 1` — **structural**: 0 and ±1 are boundaries of the quantity
    itself, not choices. A margin either clears zero or it does not.
  · `r < 0.25` · `frac >= 0.15` — **chosen**: nothing in the design says 0.25, and R881 proved how
    much turns on it.
**So: in a world-assignment comparison, the right operand must be a NAME (or contain one). A bare
numeric literal other than 0, ±1 is flagged.** A named constant is not automatically justified —
but it is declared in one place, greppable, and auditable, which a magic number in a branch is not.

PROXY LEDGER
  PROPERTY    the verdict was decided against a measured or declared reference
  PROXY       the comparison's right operand is a Name, not a bare literal
  IMPLICATION **bare literal ⇒ not a measured reference** is SOUND.
              **Name ⇒ measured** is NOT — `FLOOR = 1.5` is still a choice, merely a visible one.
              This rules on ABSENCE of declaration only, and says so rather than implying more.
  SAFE SIDE   flags undeclared literals; a named threshold is UNVERIFIED, never certified.

⚠ It only inspects assignments to a variable named `world`/`verdict`. A round that decides its
verdict some other way is outside the population, and that is named here rather than discovered.
"""
import ast, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_LITERAL_VERDICTS.json"
TARGETS = {"world", "verdict"}
STRUCTURAL = {0, 1, -1, 0.0, 1.0, -1.0}


def literal_cmps(src):
    """-> [(lineno, dumped comparison)] for bare-literal comparisons inside a verdict assignment."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    hits = []

    def scan_cmp(node, lineno):
        for c in ast.walk(node):
            if not isinstance(c, ast.Compare):
                continue
            for comp in c.comparators:
                if isinstance(comp, ast.Constant) and isinstance(comp.value, (int, float)) \
                        and not isinstance(comp.value, bool) and comp.value not in STRUCTURAL:
                    try:
                        txt = ast.unparse(c)
                    except Exception:
                        txt = "<compare>"
                    hits.append((lineno, txt))

    for node in ast.walk(tree):
        tgt = None
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id in TARGETS:
                    tgt = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id in TARGETS:
            tgt = node.value
        if tgt is not None:
            scan_cmp(tgt, node.lineno)
    return hits


def controls() -> bool:
    bad = ("mde_typ = 1.0\nclosest = 1.0\nnb = 0\n"
           "world = ('C' if closest / mde_typ < 0.25 else 'B' if nb == 0 else 'A')\n")
    good_struct = "lo = 1.0\nworld = 'A' if lo > 0 else 'B'\n"
    good_named = "FLOOR = 1.5\nr = 1.0\nworld = 'A' if r < FLOOR else 'B'\n"
    p1 = len(literal_cmps(bad)) == 1
    g1 = literal_cmps(good_struct) == []
    g2 = literal_cmps(good_named) == []
    print(f"  POSITIVE  R881's REAL branch `closest/mde_typ < 0.25` is flagged: {p1}  "
          f"{'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       a STRUCTURAL comparison `lo > 0` is not flagged: {g1}  "
          f"{'PASS' if g1 else 'FAIL'}")
    print(f"  g=0       a NAMED threshold `r < FLOOR` is not flagged: {g2}  "
          f"{'PASS' if g2 else 'FAIL'}")
    print("    The positive arm uses R881's actual expression, not an invented one — a control")
    print("    validated against cases I made up is validated against my imagination.")
    return p1 and g1 and g2


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2
    runs = sorted(ROOT.glob("E0*/A*/R*/run.py"))
    if not runs:
        print("\n  OBSERVED NOTHING: no round files. A check with no population has not passed.")
        return 2
    flagged, unparsed, scanned = [], [], 0
    for f in runs:
        h = literal_cmps(f.read_text(encoding="utf-8", errors="ignore"))
        if h is None:
            unparsed.append(str(f.relative_to(ROOT))); continue
        scanned += 1
        for ln, txt in h:
            flagged.append({"file": str(f.relative_to(ROOT)), "line": ln,
                            "cmp": " ".join(txt.split())[:110]})
    frozen = set(json.loads(FROZEN.read_text())["keys"]) if FROZEN.exists() else set()
    new = [x for x in flagged if f"{x['file']}:{x['line']}" not in frozen]
    print(f"\n  {scanned} round file(s) scanned"
          + (f" · {len(unparsed)} unparseable (UNEXAMINED, not clean)" if unparsed else ""))
    print(f"  {len(flagged)} verdict comparison(s) against a bare literal · {len(frozen)} frozen · "
          f"{len(new)} NEW")
    if new:
        print(f"\n  FAIL: {len(new)} verdict(s) decided by an undeclared number:")
        for x in new[:10]:
            print(f"    {x['file']}:{x['line']}  {x['cmp']}")
        print("  Move the number to a module-level NAME, or better, compare against a measured")
        print("  reference. R881's verdict turned on 0.28 vs a 0.25 I chose in the same line.")
        return 1
    print("\n  PASS: no NEW bare-literal verdict comparison. ⚠ A NAMED threshold is UNVERIFIED,")
    print("  never certified — `FLOOR = 1.5` is still a choice, only a visible one. And a round")
    print("  that assigns its verdict without a `world`/`verdict` variable is outside this")
    print("  gate's population entirely.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
