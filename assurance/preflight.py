#!/usr/bin/env python3
"""assurance/preflight.py -- run the gates, then stage. The step that was missing.

WHY. R1018 measured that 21 of 21 commits touching the statement landed GREEN -- but the discipline
that produced that has NO ENFORCEMENT POINT. It survived because I followed it by hand 21 times, and
one commit earlier the NEXT-line check fired in the same command as the `git commit` it was meant to
gate, so its verdict arrived after the write.

⛔⛔ AND THIS IS NOT A CONSTRAINT. IT IS A HABIT WITH A VISIBLE BYPASS, AND THE DIFFERENCE IS THE
ONLY HONEST CLAIM HERE.
  * a `pre-commit` hook cannot be the enforcement point: this repo commits with `--no-verify` by
    standing rule, so a hook is bypassed by the very discipline it would enforce;
  * `git add` has no hook at all, so staging cannot be intercepted;
  * therefore anyone -- me -- can stage by typing `git add` instead of calling this.
⭐ What it buys is smaller and real: bypassing becomes an ACTION rather than an OMISSION. Forgetting
to run a check is invisible; typing a different command instead is a thing you did. That is the whole
gain, and claiming more would be the kind of sentence this file exists to prevent.

⚠ ATTACKED ON BUILD, SIX VECTORS, EACH ACTUALLY RUN (P7 -- a lock never attacked is a lock never
tested). ① no paths -> UNRUNNABLE, exit 2, because staging nothing and returning 0 is the empty
population passing. ② a nonexistent path -> UNRUNNABLE. ③ an EMPTY `--next` -> UNRUNNABLE, because a
blank line passes the pattern vacuously and a vacuous pass is not a green light. ④ a NEXT carrying an
uncomputed quantifier -> RED, exit 1. ⑤ a deliberately unmatchable fact registered in the currency
gate -> REFUSED, exit 1, and `git diff --cached` confirmed **0 paths staged**; the gate was restored
from a copy immediately after. ⑥ plain `git add` -> **still works**. Vector ⑥ is not a hole to fix, it
is the limit stated at the top, measured rather than assumed.

USAGE   python assurance/preflight.py --next "<the NEXT paragraph>" -- <paths to stage>
EXIT    0 all gates green and the paths are staged · 1 a gate refused, NOTHING is staged ·
        2 the preflight itself could not judge, NOTHING is staged.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATES = [
    ("currency", "assurance/a_statement_is_current_with_the_arc.py"),
    ("anchoring", "assurance/definition_matches_the_record.py"),
]


def run_gate(rel):
    p = subprocess.run([sys.executable, str(ROOT / rel)], cwd=ROOT,
                       capture_output=True, text=True, timeout=600)
    return p.returncode, (p.stdout.strip().splitlines() or ["(no output)"])[-1][:100]


def next_flag(text):
    spec = importlib.util.spec_from_file_location(
        "nq", ROOT / "assurance/next_line_quantifiers_are_computed.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.flagged(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", dest="nxt", default=None,
                    help="the NEXT paragraph; checked for uncomputed quantifiers")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args()

    # ⛔ EMPTY POPULATION. Staging nothing and reporting success is the failure this project's own
    #    standard opens with. Refuse, and refuse with exit 2 rather than 1: nothing was judged.
    if not a.paths:
        print("  UNRUNNABLE: no paths given. Staging nothing and returning 0 would be an empty "
              "population passing. Exit 2, never 0.")
        return 2
    missing = [p for p in a.paths if not (ROOT / p).exists()]
    if missing:
        print(f"  UNRUNNABLE: these paths do not exist: {missing}. Exit 2, never 0.")
        return 2

    bad = []
    for name, rel in GATES:
        rc, tail = run_gate(rel)
        # ⚠ EXIT 2 IS NOT A PASS. An UNRUNNABLE gate has judged nothing, and treating it as green is
        #    how a broken instrument becomes an acquittal.
        verdict = {0: "GREEN", 1: "RED", 2: "UNRUNNABLE"}.get(rc, f"rc={rc}")
        print(f"  {name:<10}{verdict:<12}{tail}")
        if rc != 0:
            bad.append((name, verdict))

    if a.nxt is None:
        print("  next      SKIPPED     no --next given; the NEXT line is NOT checked")
    else:
        # ⚠ an EMPTY next passes the pattern vacuously, which is not a green light.
        if not a.nxt.strip():
            print("  next      UNRUNNABLE  the NEXT text is empty; a blank line cannot be checked")
            bad.append(("next", "UNRUNNABLE"))
        else:
            f = next_flag(a.nxt)
            print(f"  next      {'RED' if f else 'GREEN':<12}{f or 'no uncomputed quantifier'}")
            if f:
                bad.append(("next", "RED"))

    if bad:
        print(f"\n⛔ REFUSED — {bad}. NOTHING has been staged.")
        return 2 if any(v != "RED" for _n, v in bad) else 1

    r = subprocess.run(["git", "add", "--"] + a.paths, cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"\n  UNRUNNABLE: git add failed: {r.stderr.strip()[:120]}. Exit 2, never 0.")
        return 2
    print(f"\n⭐ all gates green — staged {len(a.paths)} path(s).")
    print("⚠ AND THIS WAS A CHOICE, NOT A CONSTRAINT: `git add` would have worked without me.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
