"""Can a retired framing still be WRITTEN OUT by a round's code?

Why this exists (entry 142)
---------------------------
r12 carried two verdict paths. The function that `--reverdict` calls had been
corrected; a full inline COPY in the main run path had not, and it contained the
retired phrase **"the value-carrying share"** in a string literal assigned to
`verdict`. A real rerun would have written that framing into a results file.

Neither existing check could see it:

  * `no_withdrawn_framings.py`            scans results JSONs -- the phrase was
                                          not in one YET
  * `retired_framing_in_assertion_positions.py`
                                          scans PROSE (README, headings, table
                                          cells) -- the phrase was in SOURCE

So the surface between "a framing was withdrawn" and "a framing appears in a
document" was unguarded, and that surface is where a rerun turns the first into
the second.

What counts as EMITTABLE
------------------------
String literals reachable by an assignment or a return -- the shapes that end up
in a results file. Deliberately EXCLUDED:

  * docstrings, at module, class and function level
  * literals under 25 characters

A docstring narrating a withdrawal is not a defect; it is the only correct place
to explain one, and r12's fix comment names the retired phrase on purpose. A
check that could not tell those apart would punish the documentation of the very
correction it exists to enforce.

Measured before being built
---------------------------
Positive control: r12's source at HEAD~1, before the fix, yields exactly **1**
hit -- `value-carrying share` at line 361. Current tree: **0**. A zero from an
instrument that has demonstrated it speaks.

  PROPERTY     no retired framing can be written into an artifact by a rerun
  PROXY        retired-framing patterns in assignable/returnable string literals
  IMPLICATION  a hit means the phrase CAN reach a results file. A clean run means
               no LITERAL carries one -- it says nothing about a phrase assembled
               at run time from parts, which this cannot see.
  SAFE SIDE    reports the file, line, matched span and the replacement the
               registry names; never rewrites anything.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "assurance"))

from retired_framing_in_assertion_positions import PAT  # noqa: E402

MIN_LEN = 25


def emittable_strings(src: str):
    tree = ast.parse(src)
    docstrings = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(n, clean=False)
            if d:
                docstrings.add(d)
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, (ast.Assign, ast.Return)):
            continue
        for c in ast.walk(n):
            if isinstance(c, ast.Constant) and isinstance(c.value, str):
                if c.value in docstrings or len(c.value) < MIN_LEN:
                    continue
                out.append((getattr(c, "lineno", n.lineno), c.value))
            elif isinstance(c, ast.JoinedStr):
                txt = "".join(v.value for v in c.values
                              if isinstance(v, ast.Constant) and isinstance(v.value, str))
                if len(txt) >= MIN_LEN:
                    out.append((getattr(c, "lineno", n.lineno), txt))
    return out


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"OBSERVED NOTHING: {what} is empty. Not a clean bill -- a check with")
        print("nothing to look at, which is the state entry 64 found five checks in.")
        raise SystemExit(2)
    return n


def main() -> int:
    # TWO POPULATIONS, FLOORED SEPARATELY. A single combined count let the check
    # pass with every round hidden, because covalx/*.py alone kept it above zero
    # -- `attack_the_suite` caught it as BROKEN on the first run. My own attack
    # had called `_floor(0, ...)` directly and passed: that proves the floor
    # raises when called with zero, NOT that the check calls it with zero when its
    # population disappears. Testing a guard in isolation is not testing the path
    # to the guard.
    round_files = sorted(_ROOT.glob("[0-9][0-9]_*/r*/*.py"))
    covalx_files = sorted(_ROOT.glob("covalx/*.py"))
    _floor(len(round_files), "the set of round source files")
    _floor(len(covalx_files), "the set of covalx source files")
    files = round_files + covalx_files
    hits, scanned, unparsed = [], 0, []
    for f in files:
        try:
            strings = emittable_strings(f.read_text())
        except SyntaxError as e:
            unparsed.append(f"{f.relative_to(_ROOT)}: {e}")
            continue
        scanned += 1
        for lineno, txt in strings:
            for pat, why in PAT:
                m = pat.search(txt)
                if m:
                    hits.append((f.relative_to(_ROOT), lineno, m.group(0), why, txt[:80]))
    _floor(scanned, "the set of PARSEABLE round and covalx source files")
    if unparsed:
        print(f"  ⚠ {len(unparsed)} file(s) did not parse and were SKIPPED, not passed: "
              f"{'; '.join(unparsed[:3])}")
    print(f"source files parsed: {scanned}   emittable retired framings: {len(hits)}\n")
    for path, lineno, span, why, ctx in hits:
        print(f"  {path}:{lineno}  {span!r}")
        print(f"      -> {why}")
        print(f"      {ctx}")
    if not hits:
        print("  (none)")
    print("\n  Scope: string LITERALS only. A framing assembled at run time from")
    print("  fragments is invisible here. Docstrings are excluded on purpose --")
    print("  narrating a withdrawal is where a withdrawal belongs.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
