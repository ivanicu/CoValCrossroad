#!/usr/bin/env python3
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
