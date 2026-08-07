"""R427/spread_resolution -- can three draws answer the question I promised they would?

I have twice closed a report with: "s2 turns the two-point spread into three; if the pairwise
excesses scatter as widely as +0.2346 and +0.0975 already do, `random criteria` is a DISTRIBUTION
rather than a baseline."

⛔ THAT IS A PREDICTION ABOUT MY OWN DESIGN'S RESOLUTION AND I NEVER COMPUTED IT. §0 asks whether the
   result would probably have failed had the claim been false. With three draws the spread of three
   pairwise excesses is itself a statistic with enormous sampling variability -- an apparent scatter
   can be noise and so can an apparent agreement. Promising a verdict the design cannot deliver is
   how a well-powered-looking round gets built.

⭐ AND THE ANSWER IS AVAILABLE BEFORE THE ARM LANDS, which is the only time a bar is a bar. The
   baselines round fixed 0.5096 before any judged arm existed and that is what turned a "win against
   chance" into a loss; the same discipline applies to a spread.

⛔ ARITHMETIC TRAP. The resolution below is ZEFF x se, propagated -- algebra, not evidence. What it
   settles is whether the QUESTION is answerable here, never what the answer is.

ESTIMAND        (A) the resolution of a DIFFERENCE between two pairwise excesses, given each
                    excess's own committed MDE;
                (B) whether the already-observed two-point gap exceeds it;
                (C) what a third draw can therefore decide, and what it cannot.

IDENTIFICATION  Exact given the committed MDEs. NOT identified: the sampling distribution of the
                SPREAD of three draws from a criterion pool -- that needs many draws, not three, and
                is named rather than estimated.

SCOPE           the three committed pairwise excesses of R427/pairwise_excess, conversation-clustered,
                2,200 conversations each.

WORLDS
  W-ALREADY-RESOLVED  the observed two-point gap already exceeds the resolution. Then "scattered vs
                      consistent" is SETTLED with two draws, and s2 tests something narrower --
                      whether the third excess falls inside the observed range.
  W-UNDERPOWERED      the gap is inside the resolution. Then the two-point spread was never
                      resolvable, my closing sentences overstated what two draws showed, and three
                      will not fix it.

PREDICTION MATRIX
  W-ALREADY-RESOLVED -> |gap| > ZEFF-propagated resolution
  W-UNDERPOWERED     -> |gap| <= it

PRE-REGISTERED KILL
    if both excesses carry a committed MDE:
        |excess_A - excess_B| > sqrt(mde_A^2 + mde_B^2) -> W-ALREADY-RESOLVED
        else                                            -> W-UNDERPOWERED, and the closing sentence
                                                            is retracted before the data arrives
    else: UNVERIFIED -- the artifact is missing.

CONTROLS
  COMMITTED    the MDEs are read from R427/pairwise_excess's persisted artifact, not recomputed here,
               so this cannot quietly adopt a more convenient precision than the one published.
  PROPAGATION  the difference of two independent estimates has se = sqrt(se_A^2 + se_B^2); since each
               committed MDE is ZEFF x se, the propagated MDE is sqrt(mde_A^2 + mde_B^2). Stated so
               the arithmetic is checkable rather than asserted.
  ⚠ NOT-INDEPENDENT  the two excesses SHARE the generic arm, so they are positively correlated and
               the true se of their difference is SMALLER than the propagation above. The check is
               therefore CONSERVATIVE: it can only under-claim resolution, never over-claim it. Named
               because a shared arm is exactly the kind of dependence that usually flatters.

ARTIFACT        results/r427_spread_resolution.json with the source hash.

IMPOSSIBLE HERE
  the sampling distribution of a 3-draw spread -- needs many draws.
  a claim about criterion pools in general     -- one pool, one corpus.

EXIT
    0  the resolution is reported and a branch is reached
    1  the artifact is missing -- UNVERIFIED
    2  never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
SRC = HERE / "results" / "r427_pairwise_excess.json"


def main() -> int:
    if not SRC.exists():
        print("  UNVERIFIED: r427_pairwise_excess.json absent. Exit 1."); return 1
    a = json.loads(SRC.read_text())["pairs"]

    print("R427 · spread_resolution — can three draws answer what I promised they would?\n")
    print("  ⛔ I CLOSED TWO REPORTS ON A PREDICTION ABOUT MY OWN DESIGN'S RESOLUTION AND NEVER")
    print("     COMPUTED IT. With three draws the SPREAD of three excesses is itself a statistic")
    print("     with large sampling variability — apparent scatter can be noise, and so can")
    print("     apparent agreement.\n")

    print(f"    {'pair':<32} {'excess':>9} {'its MDE':>9}")
    for k, v in a.items():
        print(f"    {k.replace('|', ' vs '):<32} {v['excess']:>+9.4f} {v['excess_mde']:>9.4f}")

    gA, gB = a["generic|randblind_s0"], a["generic|randblind_s1"]
    gap = abs(gA["excess"] - gB["excess"])
    res = float(np.hypot(gA["excess_mde"], gB["excess_mde"]))
    ratio = gap / res
    print(f"\n  CONTROLS")
    print(f"    COMMITTED    MDEs read from the persisted artifact, never recomputed here, so this")
    print(f"                 cannot adopt a more convenient precision than the one published")
    print(f"    PROPAGATION  se(A−B) = sqrt(se_A² + se_B²), and each committed MDE is ZEFF×se, so the")
    print(f"                 propagated MDE is sqrt({gA['excess_mde']:.4f}² + {gB['excess_mde']:.4f}²)"
          f" = {res:.4f}")
    print(f"    ⚠ NOT-INDEPENDENT  the two excesses SHARE the generic arm, so they are positively")
    print(f"                 correlated and the TRUE se of their difference is SMALLER. This check is")
    print(f"                 therefore CONSERVATIVE — it can only under-claim resolution.")

    print(f"\n  THE TWO-POINT GAP  |{gA['excess']:+.4f} − {gB['excess']:+.4f}| = {gap:.4f}")
    print(f"  AGAINST ITS RESOLUTION  {res:.4f}   ratio {ratio:.2f}×")

    print()
    if gap > res:
        v = "W_ALREADY_RESOLVED"
        print(f"  W-ALREADY-RESOLVED — the gap is {ratio:.1f}× its own resolution, so `do two random")
        print(f"  draws behave differently` is SETTLED with two draws. It does not need a third.")
        print(f"  ⛔ SO MY CLOSING SENTENCE WAS POINTING s2 AT A QUESTION ALREADY ANSWERED. What s2")
        print(f"     can actually decide is narrower and worth stating precisely: whether the third")
        print(f"     excess falls INSIDE the observed [{min(gA['excess'], gB['excess']):.4f},")
        print(f"     {max(gA['excess'], gB['excess']):.4f}] range, and whether s0↔s2 and s1↔s2")
        print(f"     reproduce s0↔s1's {a['randblind_s0|randblind_s1']['excess']:+.4f}.")
        print(f"  ⚠ AND WHAT THREE DRAWS STILL CANNOT DO: estimate the sampling distribution of the")
        print(f"    spread. `random criteria is a DISTRIBUTION rather than a baseline` needs many")
        print(f"    draws to state as a magnitude; with three it can only be stated as a direction.")
    else:
        v = "W_UNDERPOWERED"
        print(f"  W-UNDERPOWERED — the gap ({gap:.4f}) is inside its resolution ({res:.4f}). The")
        print(f"  two-point spread was never resolvable, my closing sentences overstated what two")
        print(f"  draws showed, and a third will not fix it. RETRACTED before the data arrived.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               gap=gap, resolution=res, ratio=ratio, verdict=v,
               excesses={k: v2["excess"] for k, v2 in a.items()},
               mdes={k: v2["excess_mde"] for k, v2 in a.items()})
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_spread_resolution.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
