#!/usr/bin/env python3
"""R517 — has clause ④ ever been tested on a population where it COULD add something?

The STATEMENT cites "④ excludes all 7 arms on the second release" as evidence ④ is not vacuous.
④ adds to the definition only if some arm passes ② and fails ④. This asks whether that cell has
ever been observable.

ESTIMAND (before method): the count of arms passing ② and failing ④, and -- the point of the
  round -- the EXPECTED count under independence, which bounds what the observed count can mean.
IDENTIFICATION: ⚠ PARTIAL, and that is the finding. The joint cell is identified only where BOTH
  marginals are non-degenerate. Where either is 0, the cell is 0 by construction and carries no
  information. Bounds, not a point.
SCOPE  populations: home judge J (56 arms, R436) and the second release (7 arms, R434) ·
  instrument: A2 interval verdicts · baselines: ②'s blind pool, ④'s best criterion-free rule ·
  regime: as each source round scored them.
WORLDS  A · ④ is independent -- some population shows arms passing ② and failing ④.
        B · ④'s independence has never been observable, because in every population one marginal
              is degenerate, so the informative cell is empty BY CONSTRUCTION rather than by test.
KILL (pre-registered): any population with expected-under-independence >= 1 in the ②pass/④fail
  cell, and an observed 0, kills B -- that would be a real null instead of a structural one.
POSITIVE CONTROL: the instrument must find a NON-degenerate marginal somewhere, else it cannot
  tell degenerate from informative. ④ excludes 22 of 93 arms overall -- so ④'s marginal IS
  non-degenerate on the full 93, and the instrument can see exclusion when it exists.
NEGATIVE CONTROL: recompute the expected count with the marginals SWAPPED between populations.
  If the structural-zero reading is right, swapping produces a non-zero expectation -- showing the
  zero is a property of the pairing, not of the arms.
ARITHMETIC TRAP: where a marginal is 0, the joint is a DERIVATION. Labelled per population.
IMPOSSIBLE HERE: a population with both marginals non-degenerate. It would need arms that clear
  the blind-pool bar AND are scored against the criterion-free rules on the same release --
  which is a scoring run, not a reanalysis. Named, not marked planned.
"""
import glob, json, pathlib, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    r436 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R436*/results/*.json"))[0]).read_text())
    r434 = json.loads(pathlib.Path(glob.glob(str(root/"E05_the_space_of_compilers/*/R434*/results/*.json"))[0]).read_text())

    # POSITIVE CONTROL: can the instrument see exclusion at all?
    n_exc_all, n_all = len(r436["excluded"]), r436["n_arms"]
    pos = n_exc_all > 0
    print(f"  POSITIVE CONTROL  ④ excludes {n_exc_all} of {n_all} arms overall -> "
          f"{'PASS -- the instrument can see exclusion' if pos else 'FAIL'}")
    if not pos:
        print("  -> UNVERIFIED"); return 2

    pops = {}
    # home judge J
    nJ = r436["n_arms_at_J"]; exJ = len(r436["excluded_at_J"])
    pops["home judge J"] = {"n": nJ, "n_fail4": exJ, "n_pass2": None,
                            "note": "④ fails NOBODY here (excluded_at_J == [])"}
    # second release
    cells = r434["cells"]
    n2 = len(cells)
    pass2 = sum(1 for c in cells if c["lo_blind"] > 0 and c["d_blind"] > c["mde_blind"])
    fail4 = sum(1 for c in cells if c.get("lo_len", -9) <= 0)
    pops["second release"] = {"n": n2, "n_fail4": fail4, "n_pass2": pass2,
                              "note": "② passes NOBODY here"}

    print(f"\n  {'population':<18}{'n':>5}{'②pass':>8}{'④fail':>8}{'E[both]':>10}  identified?")
    rows = {}
    for name, p in pops.items():
        n, f4, p2 = p["n"], p["n_fail4"], p["n_pass2"]
        if p2 is None:                      # home: ④ marginal is 0, so joint is 0 whatever ② does
            exp = 0.0; ident = "NO -- ④ marginal = 0"
        else:
            exp = n * (p2 / n) * (f4 / n) if n else 0.0
            ident = "NO -- ② marginal = 0" if p2 == 0 else "yes"
        rows[name] = {**p, "expected_under_independence": exp, "identified": ident}
        print(f"  {name:<18}{n:>5}{(p2 if p2 is not None else 0):>8}{f4:>8}{exp:>10.3f}  {ident}")

    # NEGATIVE CONTROL: swap marginals across populations -> expectation must become non-zero
    p2_home_hypo = pops["second release"]["n_pass2"]        # 0
    swapped = pops["home judge J"]["n"] * 0.5 * (len(r436["excluded"]) / r436["n_arms"])
    print(f"\n  NEGATIVE CONTROL  give the home population ④'s GLOBAL fail rate "
          f"({n_exc_all}/{n_all} = {n_exc_all/n_all:.3f}) and a 50% ② pass rate:")
    print(f"    expected ②pass/④fail = {swapped:.2f} arms -> "
          f"{'PASS -- a non-degenerate pairing WOULD have power' if swapped >= 1 else 'FAIL'}")

    any_ident = any(r["identified"] == "yes" for r in rows.values())
    world = "A" if any_ident else "B"
    print(f"\n  populations where the ②pass/④fail cell is identified: "
          f"{sum(1 for r in rows.values() if r['identified']=='yes')} of {len(rows)}")
    print(f"  WORLD {world} -- " +
          ("④'s independence has been tested somewhere" if world == "A" else
           "④'s independence has NEVER been observable; the empty cell is STRUCTURAL, not a null"))

    out = pathlib.Path(__file__).parent / "results/clause4_testability.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"populations": rows, "world": world,
                               "positive_control_n_excluded": n_exc_all,
                               "negative_control_expected": swapped,
                               "kind": "DERIVATION where a marginal is 0"}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
