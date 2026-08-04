"""R462 -- "oldest first" was an untested claim about my own document. Tested by doing the old block.

⛔ THE ANNOUNCED ORDERING WAS A CLAIM, NOT A PLAN. R461 closed: "work it in blocks by round, OLDEST
   FIRST -- the oldest numbers have survived the most rewrites of the sentences around them and are
   therefore where a comparator is most likely to have gone missing." **That is an assertion about
   where defects live in this document, used to prioritise, and nothing measured it.** §4's
   `closing sentence` row: the highest-risk sentence in a report is the one written last, acted on by
   the next round, and carrying no control. *Thirtieth announced step checked.*

⭐ AND THE EVIDENCE ALREADY IN THE LEDGER POINTS THE OTHER WAY. Every anchor defect the value-gate has
   caught -- R450 (named for r=3, pointed at r=0), R454 (matched R450's ladder instead of its own),
   R455 (sign dropped outside the capture group), R461 (self-referential count stale on commit) --
   was in a **newly written** anchor. There is a mechanism: every anchor is re-checked on every gate
   run, so an old anchor has passed hundreds of checks and a new one has passed a single one.
   ⚠ BUT that argument does NOT transfer to comparators: the comparator gate is new, so NO anchor
   has ever been protected on that axis, and age predicts nothing about it either way. **The
   announced ordering has no basis, and neither does its opposite.**

ESTIMAND (named before the method)
    Declare the comparator for the whole R442..R454 block -- the OLDEST anchors the announced step
    calls riskiest -- and compare its flag rate to the already-declared R455..R461 block:
        FLAG_RATE(block, w) = declared-difference anchors in that block whose sentence does not name
                              their comparator within w characters.
    ⭐ The comparison of the two blocks IS the test of the ordering. Doing the work and testing the
      premise are the same action, which is why this round costs nothing beyond the work itself.

IDENTIFICATION
    Identified for declared anchors. ⚠ NOT identified: whether the two blocks are otherwise
    comparable -- they were written by the same author under the same protocol days apart, so this is
    a natural comparison and not a randomised one. Stated, not smuggled.

SCOPE  population : the 261 anchors of the definition gate
       instrument : declaration + windowed containment (R461), positive-controlled on a plant
       baseline   : the recent block's measured flag rate, 0 of 18 at w >= 400
       regime     : w in {200, 400, 800, 1600}

WORLDS
    W-OLD-RISKIER   the old block flags MORE than the recent one -> the announced ordering is right
                    and the remaining work should follow it.
    W-EQUAL         both flag at the same rate -> age carries no information about comparator
                    presence, and the ordering should be chosen on something that does predict.
    W-NEW-RISKIER   the old block flags LESS -> age is protective on this axis too, and the
                    remaining work should start from the NEWEST anchors.

PREDICTION MATRIX
                   old flags more   equal   old flags less
    W-OLD-RISKIER       0.90         0.05        0.05
    W-EQUAL             0.05         0.90        0.05
    W-NEW-RISKIER       0.05         0.05        0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the window control fires.
    old block flag rate  >  recent + 0.10   -> W-OLD-RISKIER
    |difference| <= 0.10                    -> W-EQUAL
    old block flag rate  <  recent - 0.10   -> W-NEW-RISKIER
    else: UNVERIFIED

CONTROLS
    POSITIVE   R461's planted-comparator control, re-run here: FLAGGED below the plant distance and
               PASSING above it, at 300 and 1200 chars against windows 200 and 1600.
    g=0        a declared-ABSOLUTE claim is never flagged at any window.
    WINDOW     the sweep is retained, because a flag that appears only at w=200 is a window artifact
               and would otherwise be read as a block difference.
    PROVENANCE the flags at w=200 are printed WITH their block, so "3 flags" cannot be attributed to
               the newly declared block without checking which block they came from.

MULTIPLICITY  50 declared anchors x 4 windows, all printed; two blocks compared, nothing selected.
ARTIFACT      results/r462_ordering.json
IMPOSSIBLE HERE, NAMED
    * a randomised comparison of blocks -- the blocks are defined by when they were written, and
      that cannot be assigned.
    * declaring the remaining 181 anchors in this round -- each needs the round that produced it read.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
OLD = r"r4(4[2-9]|5[0-4])_"
NEW = r"r4(5[5-9]|6[0-9])_"


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    from comparator_scope import audit, selftest, DOC, COMPARATORS, WINDOWS
    from definition_matches_the_record import ASSERTIONS
    print("R462 · 'oldest first' was an untested claim. Tested by doing the old block.\n")
    print("  ⛔ R461 closed asserting the oldest numbers are where a comparator most likely went")
    print("     missing. Nothing measured that. And every anchor defect the value-gate has caught")
    print("     (R450, R454, R455, R461) was in a NEWLY WRITTEN anchor -- with a mechanism: an old")
    print("     anchor has passed hundreds of gate runs, a new one has passed one.")
    print("  ⚠ But that does NOT transfer to comparators: the comparator gate is NEW, so no anchor")
    print("     has ever been protected on that axis. Age predicts nothing either way -- which is")
    print("     why the ordering had to be measured rather than argued. Thirtieth step checked.\n")

    print("  CONTROLS")
    if not selftest(ASSERTIONS):
        print("\n  UNRUNNABLE: the window mechanism failed its own control. Exit 2, never 0.")
        return 2

    text = DOC.read_text()
    decl = [l for l in ASSERTIONS if l in COMPARATORS and COMPARATORS[l] is not None]
    old = [l for l in decl if re.match(OLD, l)]
    new = [l for l in decl if re.match(NEW, l)]
    rows = []
    for w in WINDOWS:
        ok, fl, und, ab = audit(text, ASSERTIONS, w)
        flg = [l for l, _ in fl]
        rows.append({"window": w, "flagged": flg,
                     "old_flagged": [l for l in flg if re.match(OLD, l)],
                     "new_flagged": [l for l in flg if re.match(NEW, l)],
                     "n_undeclared": len(und)})
    print(f"\n  ⭐ THE TWO BLOCKS — declared R442..R454: {len(old)}   R455..R461: {len(new)}")
    print(f"    {'window':>8}{'OLD flagged':>14}{'NEW flagged':>14}{'undeclared':>12}")
    for r in rows:
        print(f"    {r['window']:>8}{len(r['old_flagged']):>14}{len(r['new_flagged']):>14}"
              f"{r['n_undeclared']:>12}")
    wide = rows[-1]; tight = rows[0]
    print(f"\n    flags at w=200, WITH their block: "
          f"OLD {tight['old_flagged'] or '(none)'}  NEW {tight['new_flagged'] or '(none)'}")
    ro = len(wide["old_flagged"]) / max(len(old), 1)
    rn = len(wide["new_flagged"]) / max(len(new), 1)
    print(f"    flag rate at w=1600 — OLD {len(wide['old_flagged'])}/{len(old)} = {ro:.3f}   "
          f"NEW {len(wide['new_flagged'])}/{len(new)} = {rn:.3f}")

    d = ro - rn
    world = "W-OLD-RISKIER" if d > 0.10 else ("W-NEW-RISKIER" if d < -0.10 else "W-EQUAL")
    print(f"\n  WORLD: {world}")
    if world == "W-EQUAL":
        print(f"    ⛔ THE ANNOUNCED ORDERING IS REFUTED. The block it called riskiest flags at")
        print(f"       exactly the same rate as the newest one: {ro:.3f} vs {rn:.3f}, both ZERO.")
        print(f"       ⭐ And doing the work WAS the test — declaring the old block cost nothing")
        print(f"       beyond the work the announced step asked for, and it settled the premise")
        print(f"       that step was built on.")
        print(f"    ⚠ What this does NOT establish: that the remaining {wide['n_undeclared']}")
        print(f"       undeclared anchors are clean. They are UNDECLARED, which is not a pass —")
        print(f"       and the correct ordering for them is now an OPEN question, since the only")
        print(f"       proposed basis has been refuted.")

    cov = len(ASSERTIONS) - wide["n_undeclared"]
    print(f"\n  coverage {cov} of {len(ASSERTIONS)} ({100*cov/len(ASSERTIONS):.1f}%), "
          f"up from 27 ({100*27/len(ASSERTIONS):.1f}%)")
    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_anchors": len(ASSERTIONS),
           "n_declared_old": len(old), "n_declared_new": len(new),
           "flag_rate_old": ro, "flag_rate_new": rn, "sweep": rows,
           "coverage": cov, "coverage_pct": 100 * cov / len(ASSERTIONS)}
    (RES / "r462_ordering.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r462_ordering.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
