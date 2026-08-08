#!/usr/bin/env python3
"""A gate's coverage may not depend on the directory it was invoked from.

⭐ WHY THIS EXISTS (R1083). `definition_matches_the_record` read 8 of its artifacts through a
   HARD-CODED RELATIVE PATH -- `json.load(open("E05_the_space_of_compilers/A24_.../results/x.json"))`.
   A relative path resolves against the process's CWD, so from the repository root the gate
   evaluated all 343 anchors, and from anywhere else **32 of them went `⚠ UNEVALUABLE` and it still
   exited 0**. Nine percent of the document's coverage, decided by the caller's working directory,
   silently, in the direction of passing.

⛔ THIS IS A GAUGE TEST MADE PERMANENT. The transformation `run it from somewhere else` must leave a
   gate's verdict AND its coverage identical, because neither is a property of the caller. Where the
   measurement is invariant and the property is not, the measurement is blind (realstat §3, rung 1);
   here it is the reverse -- the property is invariant and the MEASUREMENT was not, which is the same
   defect seen from the other side.

⚠ WHAT THIS DOES NOT COVER, NAMED RATHER THAN LEFT IMPLICIT. It compares two runs of the same gate
   and cannot say whether the coverage they agree on is CORRECT: two identical runs that both lose
   32 anchors pass here. The complementary check is `an_anchor_binds_to_one_number.py` (R1082) plus
   the gate's own UNEVALUABLE line, which this gate reports but does not fail on -- making
   UNEVALUABLE fatal is a policy change with its own risk and is NOT smuggled in here.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

# gates whose coverage must not move. Each is (label, path, a token whose COUNT in stdout is the
# coverage signal). A gate with no such token is still checked on its exit code.
#
# ⭐ THE LIST IS DERIVED FROM `preflight.GATES`, NOT TYPED. R1083 shipped this watching three
#    hard-coded names and said so as a limitation; a hard-coded watch list is the same defect as a
#    hard-coded path -- it goes stale the moment a gate is added, and it goes stale silently.
#    Reading preflight's own list means a new commit gate is watched the day it is wired.
COVERAGE_TOKEN = {
    "anchoring": "UNEVALUABLE",
    "currency": "never reached",
    "one-home": "match nothing at all",
}


def watched():
    out, seen = [], set()
    try:
        import preflight                                     # same directory, on sys.path above
        for name, rel in preflight.GATES:
            p = ROOT / rel
            if p.resolve() == pathlib.Path(__file__).resolve():
                continue                                     # never recurse into this gate
            # ⛔ A GATE WITH NO REGISTERED TOKEN IS COMPARED ON ITS WHOLE NORMALISED STDOUT, not on
            #    a token that does not appear in it. The first version defaulted to "⛔", which
            #    occurs 0 times in both runs and therefore matched every time -- so a newly wired
            #    gate was watched on its EXIT CODE alone. Attacked immediately after shipping (P7)
            #    by wiring a cwd-dependent gate into preflight: the list grew to 4 and the guard
            #    still said GREEN. A silent default in the flattering direction.
            out.append((name, p, COVERAGE_TOKEN.get(name)))
            seen.add(p.resolve())
    except Exception as e:                                    # noqa: BLE001 - reported, not hidden
        print(f"  ⚠ preflight's gate list is unreadable ({e}); falling back to the named three.")
        for name, rel in (("anchoring", "assurance/definition_matches_the_record.py"),
                          ("currency", "assurance/a_statement_is_current_with_the_arc.py"),
                          ("one-home", "assurance/an_anchor_binds_to_one_number.py")):
            p = ROOT / rel
            if p.resolve() not in seen:
                out.append((name, p, COVERAGE_TOKEN.get(name)))
    return out


WATCHED = watched()


def run_from(script: pathlib.Path, cwd: pathlib.Path):
    r = subprocess.run([sys.executable, str(script)], cwd=str(cwd),
                       capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout


def main() -> int:
    present = [(n, p, t) for n, p, t in WATCHED if p.exists()]
    if not present:
        print("  UNRUNNABLE: not one watched gate exists. A gate that examined nothing has not "
              "passed. Exit 2, never 0.")
        return 2

    other = pathlib.Path(tempfile.mkdtemp(prefix="cwdinv_"))
    bad = []
    try:
        # ---- CONTROL: the harness must be able to SEE a difference before it certifies sameness.
        # A script whose output depends on the CWD is planted and must be caught. Without this, a
        # broken comparator would certify every gate as invariant.
        probe = other / "probe.py"
        probe.write_text("import pathlib\nprint('MARK ' * len(list(pathlib.Path('.').iterdir())))\n")
        a = run_from(probe, ROOT)[1].count("MARK")
        b = run_from(probe, other)[1].count("MARK")
        can_see = a != b
        # and it must NOT report a difference for a script that has none
        stable = other / "stable.py"
        stable.write_text("print('MARK')\n")
        blind = run_from(stable, ROOT)[1].count("MARK") == run_from(stable, other)[1].count("MARK")
        print(f"  CONTROLS on this gate, before its own verdict:")
        print(f"    {'PASS' if can_see else '⛔ FAIL'}  POSITIVE a cwd-dependent probe IS detected "
              f"({a} vs {b} marks)")
        print(f"    {'PASS' if blind else '⛔ FAIL'}  NEGATIVE a cwd-independent probe is NOT "
              f"reported as differing")
        if not (can_see and blind):
            print("  the comparator does not separate the known cases. Exit 2, never 0.")
            return 2

        print(f"\n  {len(present)} gate(s), each run from the repository root and from {other}")
        print(f"    {'gate':<12}{'root rc':>9}{'other rc':>10}{'root n':>9}{'other n':>9}   token")
        def scrub(s):
            for q in (str(ROOT), str(other)):
                s = s.replace(q, "<PATH>")
            return s

        for name, path, tok in present:
            rc1, o1 = run_from(path, ROOT)
            rc2, o2 = run_from(path, other)
            if tok is None:
                # no registered coverage token -> compare the WHOLE normalised output
                n1, n2 = len(scrub(o1)), len(scrub(o2))
                same_cov = scrub(o1) == scrub(o2)
                shown = "<whole stdout>"
            else:
                n1, n2 = o1.count(tok), o2.count(tok)
                same_cov = n1 == n2
                shown = repr(tok)
            ok = (rc1 == rc2) and same_cov
            if not ok:
                bad.append((name, rc1, rc2, n1, n2, shown))
            print(f"    {name:<12}{rc1:>9}{rc2:>10}{n1:>9}{n2:>9}   {shown}"
                  f"   {'ok' if ok else '⛔ MOVES'}")
    finally:
        for f in other.glob("*"):
            f.unlink(missing_ok=True)
        other.rmdir()

    if bad:
        print("\n  ⛔ RED — a gate's verdict or coverage depends on where it was invoked from:")
        for name, rc1, rc2, n1, n2, tok in bad:
            print(f"     {name}: exit {rc1}->{rc2}, {tok!r} count {n1}->{n2}")
        print("     A relative path in a gate resolves against the CALLER's directory. Build every")
        print("     path from the module's own ROOT. R1083 repaired 8 such sites in the anchoring")
        print("     gate, which lost 32 of 343 anchors and still exited 0.")
        return 1

    print("\n  GREEN — every watched gate returns the same verdict and the same coverage from both.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
