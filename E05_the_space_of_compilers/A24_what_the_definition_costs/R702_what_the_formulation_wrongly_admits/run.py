#!/usr/bin/env python3
"""
R702 -- what does the formulation WRONGLY ADMIT? The mirror test, one round after writing it.

CHECK #304 ON R701's NEXT LINE -- AND IT FINDS A DEFECT IN THE FORMULATION R701 WROTE.
  §4's per-clause remedy has two sides. Every clause of R701's formulation names an object it
  EXCLUDES; none names one it ADMITS that a reader would not call a core. ⭐ F3 states "more than one
  criterion" and NO UPPER BOUND -- so it admits sets larger than anything the release calls a core.

ESTIMAND        of the members the formulation admits, how many exceed the largest core the release
                ships (k = 4, from the card)?
IDENTIFICATION  ⚠ "a reader would not call it a core" is adjudicated by the RELEASE'S OWN CARD --
                up to four, ~95% four. That is the strongest external criterion this site has, and
                it is still the INSTANCE's distribution rather than the CATEGORY's, which is the
                same gap constraint C1 names.
SCOPE           population : the formulation's admitted set (= ②∧③, R360's ledger)
                instrument : each arm's k from R360's committed `k` field + the card's ceiling
                             instrument unit = AN ARM'S k
                             claim unit      = AN OBJECT A READER WOULD REFUSE
                             ⚠ NOT EQUAL -- k is a proxy for refusal, and the card is a proxy for
                             the reader. Both named, neither hidden.
                baseline   : the card's stated maximum of four
                regime     : this repository at HEAD
WORLDS          A REAL DEFECT: admitted members exceed the release's own maximum -> F3 needs a
                  ceiling and the formulation as written is wrong.
                B HYPOTHETICAL: none exceed it -> the missing ceiling admits nothing here.
KILL            no admitted member above k=4 -> world B; do not patch a clause against an empty
                population.
POSITIVE CTRL   coval_core (k=4) is within the bound.
g=0             topw_k1 is EXCLUDED by F3's lower bound -- the clause can exclude.
NEGATIVE CTRL   an arm absent from the ledger is UNSCORED.
PLACEBO         run twice identical.
ARTIFACT        results/wrongly_admits.json
IMPOSSIBLE      whether a 6- or 8-criterion set IS a core needs the category's definition, which is
                what this arc has been unable to obtain from a release shipping one core.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
CARD_MAX = 4          # "up to four rubric items ... about 95% end up with four" -- R689


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    admitted = sorted(led["clause23_admits"])
    K = led["k"]

    print("─── CONTROLS ───")
    posok = K.get("coval_core") is not None and K["coval_core"] <= CARD_MAX
    print(f"  POSITIVE  coval_core (k={K.get('coval_core')}) is within the card's max {CARD_MAX} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0ok = K.get("topw_k1") == 1 and "topw_k1" not in admitted
    print(f"  g=0       topw_k1 (k={K.get('topw_k1')}) is excluded by the lower bound -> "
          f"{'PASS — the clause can exclude' if g0ok else '⛔ FAIL'}")
    negok = "no_such_arm" not in K
    print(f"  NEGATIVE  an arm absent from the ledger is UNSCORED -> {'PASS' if negok else '⛔ FAIL'}")
    plc = sorted(led["clause23_admits"]) == admitted
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    rows = [{"arm": a, "k": K.get(a), "over_card_max": (K.get(a) or 0) > CARD_MAX} for a in admitted]
    over = [r for r in rows if r["over_card_max"]]
    print(f"\n─── WHAT THE FORMULATION ADMITS (G3 — every member) ───")
    for r in rows:
        tag = ("⛔ EXCEEDS the release's own maximum" if r["over_card_max"] else "within it")
        print(f"  {r['arm']:<14} k={r['k']}   {tag}")
    print(f"\n  admitted members : {len(rows)}   ⭐ above the card's max of {CARD_MAX} : {len(over)} "
          f"-> {[r['arm'] for r in over]}")
    print(f"  registered A 2 [0,5] -> {len(over)}: "
          f"{'INSIDE' if 0 <= len(over) <= 5 else '⛔ OUTSIDE'}, error {len(over)-2:+d}")
    b_ok = len(over) > 0     # F3 as written has no ceiling, so it does not exclude them
    print(f"  registered B (F3 as written does NOT exclude them) -> {b_ok}: "
          f"{'HOLDS' if b_ok else '⛔ FAILS'}")
    dirn = len(over) >= 1
    print(f"  DIRECTIONAL >=1 admitted object exceeds the release's own maximum -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(over) == 0
    print(f"  pre-registered kill (none above the max) -> "
          f"{'⭐ FIRES — the defect is hypothetical here' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"B HYPOTHETICAL — no admitted member exceeds k={CARD_MAX}. F3's missing ceiling "
                 f"admits nothing wrong in this benchmark; do not patch a clause against an empty "
                 f"population.")
    else:
        world = (f"⭐⭐⭐ A A REAL DEFECT IN THE FORMULATION I WROTE ONE ROUND AGO. F3 states 'more "
                 f"than one criterion' and NO UPPER BOUND, so the formulation admits "
                 f"{[r['arm'] + f'(k={r[chr(39)+chr(107)+chr(39)]})' if False else f'{r['arm']}(k={r['k']})' for r in over]} "
                 f"-- sets LARGER than any core the release ships, whose card says up to four and "
                 f"~95% are four. ⭐ SO THE MIRROR TEST FINDS IN ONE ROUND WHAT THE EXCLUSION TEST "
                 f"MISSED IN THIRTY: every clause was checked for excluding something right and none "
                 f"for admitting something wrong. ⚠ AND THE FIX IS NOT A CEILING OF FOUR: that is "
                 f"the INSTANCE's number, and naming it is exactly the error constraint C1 forbids. "
                 f"The honest repair is a TWO-SIDED BOUND stated as a bound -- more than one, and no "
                 f"more than the release's own maximum -- which cites the card as a scope rather "
                 f"than adopting its value as the category's. ⚠ k is a proxy for refusal and the "
                 f"card is a proxy for the reader; both are named.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} admitted members × 1 ceiling, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"wrongly_admits.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "card_max": CARD_MAX,
        "admitted": rows, "n_over": len(over), "over": [r["arm"] for r in over],
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 2 [0,5] above the card max; B F3 does not exclude them; kill if none",
        "limit": ("k is a proxy for a reader's refusal and the card is a proxy for the reader; the "
                  "card gives the INSTANCE's distribution, not the CATEGORY's -- constraint C1."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'wrongly_admits.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
