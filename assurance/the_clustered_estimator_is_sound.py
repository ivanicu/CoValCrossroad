"""lib/cluster.ByConv is infrastructure now — so it gets an instrument, not an assertion.

⛔ WHY. This helper was built THIS SESSION because the same estimator shape failed three times: a
   clustered observed rate against a flat expectation (twice, verbatim), and a pooled dict that
   OVERWROTE a conversation appearing in several strata. It is already used by two analyses and will
   be trusted by every later one. Its only test so far was three inline lines I ran once.

   A wrong helper does not fail loudly. It shifts every number that flows through it, in one
   direction, silently — which is precisely the failure it was built to stop.

⭐ AND THE TEST THAT MATTERS IS THE MUTATION. Every check below is run twice: once against the real
   helper, once against a DELIBERATELY BROKEN copy whose `add` ASSIGNS instead of APPENDS — the exact
   defect. A test suite that passes on the broken copy is decoration, and this file exits 1 if that
   happens.

CHECKS, each with the world it excludes
  APPEND      a conversation observed in two strata keeps BOTH observations. Excludes: the pooled-dict
              defect, where the second stratum silently replaces the first and the loss looks like a
              smaller n.
  PAIRED-ZERO paired(x, x) is EXACTLY 0.0. Excludes: an estimator that drifts on identical inputs.
  PAIRED-NE-MEANS when a conversation carries x but NOT y, paired(x,y) = 0.0 while
              mean(x) − mean(y) = +0.167. paired() restricts to units having BOTH; mean() does not.
              Excludes: the class of error where a difference is taken across units that were never
              matched -- the situation every arm comparison here is in, because arms cover different
              interaction sets. ⚠ Named for what it tests only after a correction: the first version
              asserted EQUALITY under a name promising difference, on a fixture where the two
              coincide.
  MDE-SCALES  4× the conversations at the same spread halves the MDE, within 10%. Excludes: an MDE
              that ignores n — the failure that would make every interval meaningless while every
              number stayed plausible.
  TOO-FEW     fewer than 2 conversations returns None, never a number. Excludes: an n=1 "estimate"
              with an undefined spread being read as a measurement.
  MUTATION    all of the above are re-run against the broken copy, and at least one MUST fail.

EXIT
    0  every check passes on the real helper AND the broken copy is caught
    1  a check fails, or the broken copy passes — the suite is decoration
    2  the helper is missing — never a silent pass
"""
from __future__ import annotations
import collections
import importlib.util
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
HELPER = ROOT / "lib" / "cluster.py"


def load(broken: bool):
    src = HELPER.read_text()
    if broken:
        # THE EXACT DEFECT: assign instead of append.
        src = src.replace("self._d[conv][name].append(float(value))",
                          "self._d[conv][name] = [float(value)]")
    ns = {}
    exec(compile(src, "<cluster>", "exec"), ns)                     # noqa: S102
    return ns["ByConv"]


def checks(ByConv):
    out = {}
    b = ByConv()
    b.add("c1", v=1.0); b.add("c1", v=0.0); b.add("c2", v=1.0)
    out["APPEND"] = (b.n_obs("v") == 3)

    b2 = ByConv()
    for i in range(20):
        b2.add(f"c{i}", x=float(i % 3), y=float(i % 5))
    p = b2.paired("x", "x")
    out["PAIRED-ZERO"] = (p is not None and p[0] == 0.0)

    # ⛔ THIS CHECK ASSERTED THE OPPOSITE OF ITS OWN NAME FOR ONE MINUTE. My first fixture gave
    #    every conversation BOTH quantities, where paired() and mean(x)-mean(y) are algebraically
    #    EQUAL -- so it was named PAIRED-NE-MEANS and tested equality. The name promised one thing
    #    and the assertion checked another, which is the instrument-unit-vs-claim-unit failure in
    #    miniature.
    #    THE REAL INVARIANT: paired() restricts to conversations carrying BOTH quantities; mean()
    #    does not. They diverge exactly when some conversation has one and not the other -- which is
    #    the situation every arm comparison in this campaign is in, because arms cover different
    #    interaction sets.
    b3 = ByConv()
    b3.add("both1", x=1.0, y=0.0)
    b3.add("both2", x=0.0, y=1.0)
    b3.add("only_x", x=1.0)                      # carries x and NOT y
    pd = b3.paired("x", "y")
    md = b3.mean("x")[0] - b3.mean("y")[0]
    # paired uses {both1, both2} -> (1-0 + 0-1)/2 = 0.0
    # means use x over all three (0.667) minus y over two (0.5) = +0.167
    out["PAIRED-NE-MEANS"] = (pd is not None and abs(pd[0]) < 1e-12
                              and abs(md - (2 / 3 - 0.5)) < 1e-9 and abs(pd[0] - md) > 1e-6)

    rng = np.random.default_rng(0)
    small, big = ByConv(), ByConv()
    for i in range(50):
        small.add(f"s{i}", v=float(rng.normal()))
    rng2 = np.random.default_rng(0)
    for i in range(200):
        big.add(f"b{i}", v=float(rng2.normal()))
    ms, mb = small.mean("v"), big.mean("v")
    out["MDE-SCALES"] = (ms is not None and mb is not None
                         and abs(mb[1] / ms[1] - 0.5) < 0.10)

    b4 = ByConv(); b4.add("only", v=1.0)
    out["TOO-FEW"] = (b4.mean("v") is None)
    return out


def main() -> int:
    if not HELPER.exists():
        print(f"  UNRUNNABLE: {HELPER} absent. Exit 2, never 0."); return 2
    real = checks(load(False))
    broken = checks(load(True))

    print("  lib/cluster.ByConv — an instrument, not an assertion\n")
    print(f"    {'check':<18} {'real':>6} {'broken copy':>13}")
    for k in real:
        print(f"    {k:<18} {'PASS' if real[k] else 'FAIL':>6} "
              f"{'passes' if broken[k] else 'CAUGHT':>13}")

    all_real = all(real.values())
    caught = [k for k in broken if not broken[k]]
    print(f"\n    real helper: {sum(real.values())} of {len(real)} pass")
    print(f"    ⚠ ONLY SOME CHECKS CAN SEE THE MUTATION, and that is correct rather than a")
    print(f"      weakness: the others test DIFFERENT properties. What would be a weakness is")
    print(f"      reading one CAUGHT as evidence the suite is broadly sensitive — it is not.")
    print(f"    MUTATION — the broken copy ASSIGNS instead of APPENDING, the exact defect this")
    print(f"    helper exists for. Checks that CAUGHT it: {caught or 'NONE'}")
    print(f"    ⛔ a suite that passes on the broken copy is decoration, and this file exits 1 if")
    print(f"       that happens — the same standard every round in this campaign is held to.")

    print()
    if all_real and caught:
        print(f"  PASS: every check holds on the real helper, and the deliberate defect is caught by")
        print(f"  {caught}. The two invariants that actually failed in practice — same units on both")
        print(f"  sides, and appending across strata — are now enforced by something that has been")
        print(f"  shown able to fail.")
        return 0
    if not all_real:
        print(f"  FAIL: the real helper does not satisfy {[k for k, v in real.items() if not v]}.")
    else:
        print(f"  FAIL: the broken copy passes EVERY check. The suite cannot see the defect it was")
        print(f"  written for, which makes it decoration rather than a control.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
