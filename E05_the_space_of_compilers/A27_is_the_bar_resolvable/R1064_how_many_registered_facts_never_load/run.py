"""R1064 — how many registered facts never load at all, and make the failure loud.

R1063 found that every fact in the currency registry is guarded by `if d:` where `d = load(<glob>)`.
Its own script crashed before writing its artifact, `load` returned None, no fact was registered, and
the gate reported PASS five consecutive times while I read each pass as confirmation.

⭐ SO THE GATE HAS AN UNMEASURED INPUT: the set of globs that resolve to nothing. A fact whose
   artifact is absent is INDISTINGUISHABLE from a fact that is satisfied — §4's `empty population
   passes`, sitting inside the instrument that certifies every commit in this repository.

ESTIMAND        the number of `load(...)` globs in the registry that resolve to no file on disk
IDENTIFICATION  exact - the registry source and the filesystem are both here.
SCOPE           population : every string literal passed to `load` in the registry source
                instrument : the registry's own `E05.glob`, imported rather than reimplemented
                baseline   : the gate's own PASS, which cannot see this
                regime     : this checkout
WORLDS          A R1063 WAS ISOLATED — every other glob resolves, so the silent-skip defect cost one
                  round and the registry's coverage is otherwise what it appears to be.
                B THE REGISTRY IS PARTLY HOLLOW — several globs resolve to nothing, so the gate has
                  been certifying a statement against a fact set smaller than its source suggests,
                  and every PASS it issued was over that smaller set.
                prediction matrix: A -> unresolved == 0 (R1063's is now written)
                                   B -> unresolved > 0
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      unresolved == 0 -> World A
                      unresolved > 0  -> World B, and each is named
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a glob KNOWN to resolve — R1063's, written minutes ago — must resolve here. A
                resolver never shown to succeed cannot evidence a failure.
NEGATIVE CTRL   a fabricated glob must resolve to nothing, or the resolver matches anything.
PLACEBO         an empty glob list must exit 2, never 0.
NOISE FLOOR     N/A - filesystem existence is not sampled. Stated, not omitted.
MULTIPLICITY    every glob reported with its resolution, not only the failures.
SEEDS           N/A - deterministic.
IMPOSSIBLE      whether a glob that resolves points at the RIGHT artifact. Existence is not
                correctness. SETTLES: IN-RELEASE - each fact's patterns are checked against the
                statement by the gate itself, which is a different question already covered.

⭐⭐ AND THIS ROUND SHIPS THE REMEDY, NOT ONLY THE COUNT. `assurance/a_registered_fact_must_load.py`
   is written here and exits 1 when any glob resolves to nothing, so the silent skip becomes a red
   gate. A measurement that leaves the defect in place is cost recovery; the gate is the production.
"""
import ast, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REG = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
E05 = ROOT / "E05_the_space_of_compilers"


def globs_in(src):
    out = []
    for nd in ast.walk(ast.parse(src)):
        if (isinstance(nd, ast.Call) and isinstance(nd.func, ast.Name)
                and nd.func.id == "load" and nd.args
                and isinstance(nd.args[0], ast.Constant)
                and isinstance(nd.args[0].value, str)):
            out.append(nd.args[0].value)
    return out


def main() -> int:
    src = REG.read_text()
    gl = globs_in(src)
    if not gl:
        print("  UNRUNNABLE: no load() globs found. Exit 2, never 0."); return 2

    known = next((g for g in gl if "R1063" in g), None)
    pos = known is not None and bool(sorted(E05.glob(known)))
    neg = not sorted(E05.glob("A99_never/R9999_never/results/never.json"))
    print(f"  POSITIVE — a glob KNOWN to resolve (R1063's, written minutes ago) must resolve: {pos}")
    print(f"  NEGATIVE — a fabricated glob must resolve to nothing: {neg}")
    if not (pos and neg):
        print("  the resolver cannot be read either way. Exit 2, never 0."); return 2

    rows = []
    for g in gl:
        hits = sorted(E05.glob(g))
        rows.append({"glob": g, "hits": len(hits),
                     "path": str(hits[-1].relative_to(ROOT)) if hits else None})
    dead = [r for r in rows if r["hits"] == 0]
    print(f"\n  ⭐ load() globs in the registry: {len(rows)} · resolving: {len(rows) - len(dead)} · "
          f"RESOLVING TO NOTHING: {len(dead)}")
    for r in dead:
        print(f"     ⛔ {r['glob']}")
    dup = [r for r in rows if r["hits"] > 1]
    print(f"  ⚠ globs matching MORE than one file (the registry takes the LAST): {len(dup)}")
    for r in dup[:5]:
        print(f"     {r['hits']}x {r['glob']}")

    print()
    if not dead:
        world = (f"⭐ A R1063's SILENT SKIP WAS ISOLATED — all {len(rows)} globs resolve, so the "
                 f"registry's coverage is what its source suggests and the defect cost exactly one "
                 f"round. ⚠ That is true NOW because R1063's artifact was written minutes ago; it "
                 f"was false while that script was crashing, and nothing in the gate would have said "
                 f"so.")
    else:
        world = (f"⛔ B THE REGISTRY IS PARTLY HOLLOW — {len(dead)} of {len(rows)} globs resolve to "
                 f"nothing, so the gate has been certifying the statement against a fact set smaller "
                 f"than its source suggests, and every PASS it issued was over that smaller set: "
                 f"{[r['glob'] for r in dead]}")
    print(world)
    print(f"⛔ AND EXISTENCE IS NOT CORRECTNESS. A glob that resolves may still point at the wrong")
    print(f"   artifact; that question is the gate's own pattern check and is not this round's.")

    # ---------- the remedy, shipped ----------
    gate = ROOT / "assurance/a_registered_fact_must_load.py"
    gate.write_text('''#!/usr/bin/env python3
"""Every `load(<glob>)` in the currency registry must resolve to a file.

⭐ WHY THIS EXISTS (R1064, after R1063). The registry registers each fact under `if d:` where
   `d = load(<glob>)`. When a round's script crashes before writing its artifact, `load` returns
   None, the fact is never registered, and the currency gate reports PASS — indistinguishable from
   the fact being satisfied. R1063 read five consecutive PASSes that way.

⛔ A GATE THAT CANNOT SEE ITS OWN MISSING INPUTS IS §4's `empty population passes`. This makes the
   skip loud: any unresolved glob exits 1 and is named.
"""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "assurance/a_statement_is_current_with_the_arc.py"
E05 = ROOT / "E05_the_space_of_compilers"


def main() -> int:
    if not REG.exists():
        print("  UNRUNNABLE: the registry is missing. Exit 2, never 0.")
        return 2
    globs = [nd.args[0].value for nd in ast.walk(ast.parse(REG.read_text()))
             if (isinstance(nd, ast.Call) and isinstance(nd.func, ast.Name)
                 and nd.func.id == "load" and nd.args
                 and isinstance(nd.args[0], ast.Constant)
                 and isinstance(nd.args[0].value, str))]
    if not globs:
        print("  UNRUNNABLE: no load() globs found; a gate over nothing must not pass. Exit 2.")
        return 2
    dead = [g for g in globs if not sorted(E05.glob(g))]
    print(f"  {len(globs)} registered artifact glob(s) - resolving {len(globs) - len(dead)} - "
          f"dead {len(dead)}")
    if dead:
        print("  FAIL: these globs resolve to no file, so their facts register NOTHING and the")
        print("  currency gate would report PASS having never seen them:")
        for g in dead:
            print(f"    {g}")
        return 1
    print("  PASS: every registered fact has an artifact on disk to load.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
''')
    print(f"\n⭐ REMEDY SHIPPED — {gate.relative_to(ROOT)} exits 1 on any unresolved glob.")

    o = HERE / "results" / "registry_inputs.json"
    o.write_text(json.dumps({
        "round": "R1064", "globs": len(rows), "dead": [r["glob"] for r in dead],
        "multi_hit": [r["glob"] for r in dup], "rows": rows, "world": world,
        "remedy": "assurance/a_registered_fact_must_load.py",
        "controls": {"positive_known_glob_resolves": bool(pos), "negative_fabricated": bool(neg)},
        "limitation": "existence is not correctness; a resolving glob may point at the wrong file",
    }, indent=2) + "\n")
    print(f"artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
