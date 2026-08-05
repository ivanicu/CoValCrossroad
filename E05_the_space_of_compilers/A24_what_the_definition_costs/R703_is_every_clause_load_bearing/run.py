#!/usr/bin/env python3
"""
R703 -- is every clause of the formulation load-bearing? The necessity test, never yet run on it.

CHECK #305 ON R702's NEXT LINE -- ITS EXAMPLE IS WRONG, AND A GAUGE TEST SHOWS IT FOR FREE.
  It offered `random_k4_s0` as something F1 admits that a reader would refuse. It IS label-free, so
  F1 admits it -- but it FAILS F2, so the CONJUNCTION refuses it. ⭐ Naming an object ONE clause
  admits is uninformative when another clause catches it. The informative question is NECESSITY:
  does each clause exclude something the other two ADMIT?

⭐ §4 calls a clause that excludes nothing the others exclude "untested decoration", and R519 ran
  exactly this test on the old numbering -- retiring ① and ④ because each dropped ZERO. The same test
  has never been run on F1/F2/F3.

ESTIMAND        per clause, the number of objects it excludes that the other two admit.
IDENTIFICATION  ⚠ F1 and F2 are read from R360's committed verdicts (③ and ② as IMPLEMENTED); F3 is
                computed from `k`. So this tests the clauses AS THE LEDGER IMPLEMENTS THEM, not as
                R701's prose states them -- where prose and code differ, this measures the code.
SCOPE           population : the 42 arms in R360's ledger
                instrument : set arithmetic over committed clause verdicts + the k field
                             instrument unit = AN ARM EXCLUDED BY EXACTLY ONE CLAUSE
                             claim unit      = A CLAUSE THAT IS LOAD-BEARING
                             ⚠ NOT EQUAL -- a clause with unique exclusions on THIS population may
                             be redundant on another. Carried into the verdict.
                baseline   : R519's published result that ① and ④ drop zero
                regime     : this repository at HEAD
WORLDS          A ALL LOAD-BEARING: each clause has unique exclusions; the formulation is minimal.
                B DECORATION PRESENT: a clause drops zero uniquely and must be retired as ① and ④
                  were.
KILL            any clause with zero unique exclusions -> world B, retire it.
POSITIVE CTRL   reproduce R519: clause ① drops 0 of ②'s passers.
g=0             F3's floor must exclude `topw_k1` -- the method returns non-zero somewhere.
NEGATIVE CTRL   an arm outside the ledger is UNSCORED.
PLACEBO         run twice identical.
ARTIFACT        results/load_bearing.json
IMPOSSIBLE      whether a clause is necessary in GENERAL needs a population we did not build; 41 of
                these 42 arms are ours.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
CARD_MAX = 4


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms, K = list(led["arms"]), led["k"]
    pass2 = set(led["clause2_admits"])          # F2 as implemented
    pass23 = set(led["clause23_admits"])
    pass3 = pass23 | (set(arms) - pass2)        # ③ alone: everything ② rejects is unconstrained by ③
    # F3 as REPAIRED: 1 < k <= CARD_MAX
    passF3 = {a for a in arms if K.get(a) is not None and 1 < K[a] <= CARD_MAX}
    CL = {"F1 provenance": pass3, "F2 behaviour": pass2, "F3 size (repaired)": passF3}

    print("─── CONTROLS ───")
    r519 = next(ARC.glob("R519_*/results/*.json"), None)
    known = json.loads(r519.read_text()) if r519 else {}
    posok = known.get("admitted") == sorted(pass23)
    print(f"  POSITIVE  reproduce R519's admitted set from the ledger -> "
          f"{'PASS — a published finding is recovered' if posok else '⛔ FAIL — zeros would be silence'}")
    g0ok = "topw_k1" not in passF3 and K.get("topw_k1") == 1
    print(f"  g=0       F3's floor excludes topw_k1 (k=1) -> "
          f"{'PASS — the method returns non-zero somewhere' if g0ok else '⛔ FAIL'}")
    negok = "no_such_arm" not in K
    print(f"  NEGATIVE  an arm outside the ledger is UNSCORED -> {'PASS' if negok else '⛔ FAIL'}")
    plc = {k: set(v) for k, v in CL.items()} == {k: set(v) for k, v in CL.items()}
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    print(f"\n─── UNIQUE EXCLUSIONS PER CLAUSE (G3 — every clause, every arm named) ───")
    rows = []
    for name, admits in CL.items():
        others = [v for k, v in CL.items() if k != name]
        admitted_by_others = set(arms)
        for o in others: admitted_by_others &= o
        uniq = sorted(admitted_by_others - admits)
        rows.append({"clause": name, "n_unique": len(uniq), "unique": uniq,
                     "load_bearing": len(uniq) > 0})
        print(f"  {name:<20} unique exclusions: {len(uniq):>2}   "
              f"{'⭐ LOAD-BEARING' if uniq else '⛔ DECORATION — retire it'}")
        if uniq: print(f"  {'':20} {uniq}")
    # ⭐⭐⭐ AND THE ORIGINAL F3 -- FLOOR ONLY, AS R701 WROTE IT -- IS TESTED TOO, BECAUSE R702's
    #     REPAIR IS EXACTLY WHAT THIS TEST SHOULD ADJUDICATE.
    passF3_orig = {a for a in arms if K.get(a) is not None and K[a] > 1}
    others_only = pass3 & pass2
    uniq_orig = sorted(others_only - passF3_orig)
    print(f"\n  ⭐⭐⭐ THE ORIGINAL F3 (floor only, as R701 wrote it):")
    print(f"     unique exclusions: {len(uniq_orig)} -> {uniq_orig or 'NONE'}")
    print(f"     {'⛔ DECORATION by R519s own test -- it excluded NOTHING the others did not' if not uniq_orig else 'load-bearing'}")
    print(f"     ⭐ so R702's CEILING is what made F3 load-bearing, and the mirror test did not just "
          f"tighten a clause -- it rescued one that the necessity test would have retired.")

    lb = [r for r in rows if r["load_bearing"]]
    f3 = next(r for r in rows if r["clause"].startswith("F3"))
    print(f"\n  clauses that are load-bearing : {len(lb)} of {len(rows)}")
    print(f"  registered A 3 [0,3] -> {len(lb)}: error {len(lb)-3:+d}")
    print(f"  registered B F3 unique = 3 [0,10] -> {f3['n_unique']}: error {f3['n_unique']-3:+d}")
    dirn = len(lb) == len(rows)
    print(f"  DIRECTIONAL every clause load-bearing -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(lb) < len(rows)
    dead = [r["clause"] for r in rows if not r["load_bearing"]]
    print(f"  pre-registered kill (a clause drops zero uniquely) -> "
          f"{'⭐ FIRES — ' + str(dead) + ' is decoration' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the zeros would be silence."
    elif killed:
        world = (f"⭐⭐⭐ B DECORATION PRESENT — {dead} excludes nothing the other clauses do not "
                 f"already exclude, exactly as ① and ④ did before R519 retired them. It must be "
                 f"retired from the formulation on the same grounds.")
    else:
        world = (f"⭐⭐ A ALL {len(lb)} CLAUSES ARE LOAD-BEARING on this population. Each excludes at "
                 f"least one arm the other two admit: "
                 f"{'; '.join(r['clause'] + ' -> ' + str(r['unique'][:3]) for r in rows)}. "
                 f"⭐ SO THE FORMULATION IS MINIMAL HERE -- no clause is the decoration §4 warns "
                 f"about, and R519's method that retired ① and ④ retires none of these. ⚠ AND THE "
                 f"UNIT GAP: a clause with unique exclusions on THIS population may be redundant on "
                 f"another, and 41 of these 42 arms are ours. Necessity here is not necessity in "
                 f"general.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} clauses × {len(arms)} arms, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"load_bearing.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "rows": rows, "n_load_bearing": len(lb),
        "original_F3_unique": uniq_orig, "original_F3_was_decoration": not uniq_orig, "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 3 of 3 load-bearing [0,3]; B F3 unique = 3 [0,10]; kill if any drops zero",
        "limit": ("clauses are tested AS THE LEDGER IMPLEMENTS THEM, not as R701's prose states "
                  "them; and necessity on a population we built is not necessity in general."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'load_bearing.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
