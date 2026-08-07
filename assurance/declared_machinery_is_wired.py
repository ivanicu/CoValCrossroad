#!/usr/bin/env python3
"""assurance/declared_machinery_is_wired.py -- a constant defined for a control and never referenced.

WHY, AND IT IS THE SHARPER HALF OF A GATE WRITTEN ONE ROUND AGO.
`a_declared_control_reaches_the_artifact.py` can say NOT-RECORDED and cannot say NOT-RUN: it reads
the artifact, so a round that ran a control without recording it (R1006, 5,000 shuffles at lines
198-200) is indistinguishable from one that never ran it (R1005). **This gate reads the CODE.**

It is exactly the check that caught R1005 by hand: its docstring declared

    NEGATIVE CTRL   shuffle the membership labels ... >=200 shuffles.

and `NSHUF = 200` sat at module level, **referenced nowhere**. One grep for an unused name. R1007 then
ran the missing control and RETRACTED R1005's headline. **Declared machinery that is never wired is a
claim about what ran, and it is statically detectable.**

⚠⚠ PROXY LEDGER.

    PROPERTY     every control the docstring declares was actually EXECUTED
    PROXY        no module-level CONSTANT is assigned and never loaded anywhere in the file
    IMPLICATION  an unused constant  =>  some declared machinery was never wired          [SOUND-ish]
                 no unused constant  =>  every declared control ran                       [NOT SOUND]
    WITNESS      **from the very case that motivates this gate.** R1005 declared TWO controls and ran
                 neither. The NEGATIVE one had `NSHUF = 200` and IS caught here. The PLACEBO needed
                 no new constant -- it would have reused the existing partition and draw counts -- so
                 **this gate would have missed it entirely.** One of two, on the round it was written
                 for. That is the bound on what it can promise.
    SAFE SIDE    the verdict is UNWIRED CONSTANT, never "the control did not run". It names a
                 specific dead name at a specific line; it does not adjudicate the docstring.

⭐ AND IT IS SOUND WHERE THE ARTIFACT GATE IS NOT: this reads the file with `ast`, so a name is
"used" only if it appears as a Load anywhere in the module. No regex, no naming convention, nothing
that depends on a habit the repo never adopted -- which is what made the artifact gate flag 95% of
the corpus on its first run.

SCOPE. Every round with a `run.py` that DECLARES at least one control. A round that declares none is
not making the claim this gate checks, and is not in the population.

POSITIVE CONTROL, on real rounds with known answers, both directions:
  * R1005 MUST be flagged, on `NSHUF` -- established by R1007 and RETRACTIONS.md.
  * a majority of rounds MUST pass. ⚠ The predecessor gate's control read "at least one round must
    pass" and was satisfied at a 5% pass rate; `>= 1` is a check that cannot fail. This one requires
    the pass rate to exceed one half, so a pattern that flags everything is UNRUNNABLE, not a result.

⭐ WHAT ITS FIRST RUN FOUND, and it is why the gate was worth building rather than a tidy-up.
47 of 399 rounds define a constant they never reference. Three of them name DESIGN MACHINERY the
round's own docstring declares:

    R243  line 56  `DRAWS, SEEDS = 20, [0, 1, 2, 3, 4]`   -- DRAWS is used, SEEDS is not,
                    and the docstring reads "SEEDS  5, on the floor draws."
    R267  line 83  `DRAWS = 20`                            -- unused, in a round declaring five
                    controls including a measured noise floor
    R273  line 63  `DOSES = GRID["prompt"]`                -- unused, in a round about dose-response

⚠⚠ THESE ARE CANDIDATES AND ARE NOT CLAIMED AS FAILURES. An unused constant is not proof a control
did not run; the round may use a literal instead. Each needs its own check, exactly as R1005 needed
R1007. What is established is the SIGNATURE, and it is the same signature as the failure that cost a
retraction: machinery named in a docstring, assigned at module level, and wired to nothing.

⚠ AND IT FLAGS THE ROUND THAT MOTIVATED IT AND ONE OF MY OWN. R1000 defines `RULE` -- a compiled
regex -- and never uses it. That is dead code, NOT a missing control, and the distinction is the
whole point of the proxy ledger above: this gate names a dead name, it does not adjudicate a claim.

EXIT   0 nothing unwired · 1 unwired constants found · 2 the gate could not judge.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs  # noqa: E402

DECLARED = re.compile(r"^(POSITIVE CTRL|NEGATIVE CTRL|SHAM|PLACEBO|NOISE FLOOR)", re.M)
CONST = re.compile(r"^[A-Z][A-Z0-9_]*$")
# `__all__`-style and dunder names are conventions, not machinery.
EXEMPT = {"ROOT", "HERE", "RES", "NEW", "OUT"}


def scan(run: pathlib.Path):
    src = run.read_text()
    if '"""' not in src or not DECLARED.search(src.split('"""')[1] if '"""' in src else ""):
        return None
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {"unwired": [], "unparseable": True}
    assigned = {}
    for node in tree.body:                      # MODULE level only
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for t in targets:
            for nm in ([t] if isinstance(t, ast.Name) else
                       list(t.elts) if isinstance(t, (ast.Tuple, ast.List)) else []):
                if isinstance(nm, ast.Name) and CONST.match(nm.id) and nm.id not in EXEMPT:
                    assigned.setdefault(nm.id, nm.lineno)
    loaded = {n.id for n in ast.walk(tree)
              if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    # a name used inside an f-string or a string is NOT a use; ast already handles that correctly.
    unwired = sorted((k, v) for k, v in assigned.items() if k not in loaded)
    return {"unwired": unwired, "unparseable": False}


def main() -> int:
    rows = []
    for d in iter_round_dirs(ROOT):
        run = d / "run.py"
        if not run.exists():
            continue
        r = scan(run)
        if r is None:
            continue
        rows.append({"round": d.name, "unwired": [[k, v] for k, v in r["unwired"]],
                     "unparseable": r["unparseable"]})
    if not rows:
        print("  UNRUNNABLE: no round declares a control. An empty population must not pass. "
              "Exit 2, never 0.")
        return 2

    flagged = [r for r in rows if r["unwired"]]
    rate = 1.0 - len(flagged) / len(rows)
    pos_a = any(r["round"].startswith("R1005_") and
                any(k == "NSHUF" for k, _ in r["unwired"]) for r in flagged)
    pos_b = rate > 0.5
    print(f"  POSITIVE CONTROL — R1005 must be flagged on `NSHUF` (R1007 and RETRACTIONS.md "
          f"establish it): {'PASS' if pos_a else '⛔ FAIL'}")
    print(f"  POSITIVE CONTROL — a MAJORITY must pass, or the pattern flags everything and means "
          f"nothing: {'PASS' if pos_b else '⛔ FAIL'} (pass rate {rate:.0%} of {len(rows)})")
    print(f"     ⚠ the predecessor gate's version of this read 'at least one round must pass' and "
          f"was satisfied at 5%. `>= 1` is a check that cannot fail.")
    if not (pos_a and pos_b):
        print("\n  UNRUNNABLE: the gate is unfit. Exit 2, never 0.")
        return 2

    print(f"\n  {len(rows)} rounds declare a control · {len(flagged)} define a constant that is "
          f"never referenced")
    for r in sorted(flagged, key=lambda x: x["round"]):
        names = ", ".join(f"{k}:{v}" for k, v in r["unwired"])
        print(f"    {r['round'][:56]:<56} {names}")

    print("\n  ⚠ VERDICT IS **UNWIRED CONSTANT**, never 'the control did not run'. And the bound is\n"
          "     measured on the round this gate was written for: R1005 declared TWO controls and ran\n"
          "     NEITHER. The negative one had `NSHUF` and is caught. The PLACEBO needed no new\n"
          "     constant and is MISSED. One of two — that is what this gate can promise.")

    out = ROOT / "assurance" / "results" / "declared_machinery.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"n_declaring": len(rows), "n_flagged": len(flagged),
                               "pass_rate": rate, "rows": rows}, indent=1))
    print(f"  artifact {out.relative_to(ROOT)}")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
