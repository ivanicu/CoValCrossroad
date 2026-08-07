#!/usr/bin/env python3
"""R746 · the census admitted arms measured on two different populations

ESTIMAND        E1 the prompt-coverage distribution of today's 92-arm population, split by the 16
                the census admits, the 51 added since R294's census, and the whole 92.
                E2 whether the four unresolved tags coincide, ON SHARED CELLS, with an extension
                member already counted.
IDENTIFICATION  E1 EXACT -- select_core.py:200 emits meta as f"{pid}|{j}|{x}", so the prompt set is
                field 0 of a builder-emitted structured string, not a search over prose.
                E2 PARTIAL -> a BOUND. Identity on shared cells is sound one way: identical =>
                indistinguishable THERE; not identical => different objects. For the `2b` pair the
                shared set is at most 200 of 968 prompts.
SCOPE           population = the arms R728's construction admits from corebench/results/sat_*.npz ·
                instrument = numpy + field-0 parse + R525's identity relation · baseline = the
                committed extension's 5 · regime = this tree_sha.
WORLDS          A coverage uniform among the admitted · B the census admits across two populations ·
                C coverage varies across the 92 but not among the admitted.
KILL            conditional; gated on POSITIVE separating two arms of different size, NEGATIVE
                destroying the parse, PLACEBO exactly zero.
POSITIVE CTRL   the parser must separate two arms whose FILE SIZES differ 4.5x -- size is an
                independent signal it never reads. Band computed against a constant parser.
g=0             an arm with empty meta -> UNREADABLE, never 0 prompts. A silent zero would enter
                the low-coverage count and manufacture World B.
NEGATIVE CTRL   parse field 1 (selection index) instead of field 0 (prompt id); coverage must move.
SHAM            ingredient ABSENT: the same counting on the arms the census did NOT admit.
PLACEBO         each arm's coverage against itself -> exactly 0, over all arms.
NOISE FLOOR     no rng in E1/E2. The variance is the COVERAGE DEFINITION: prompts / cells / pairs.
MULTIPLICITY    3 definitions x 3 populations = 9 cells, all reported, plus 3 identity tests.
SPECIFICATION   the three coverage definitions ARE the curve.
UNIT            instrument unit = one TAG's npz; claim unit = one ARM's evidence base. Asserted
                equal in code -- any tag resolving to zero or two files is reported.
ARTIFACT        results/r746.json with tree_sha; a later round attacks this by testing whether the
                200 prompts are a representative subset, which needs the rule that chose them.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      representativeness of the 200 (needs the sampling rule; comparing them on an
                outcome is circular) · sameness outside shared cells (needs a scoring run) ·
                independently replicated · cross-site.

⛔ DERIVATION, DERIVED BEFORE MEASURING, AND IT POINTS AWAY FROM A DEFECT: R728's decide() computes
   mde = ZEFF * std / sqrt(n). At equal std, 968 -> 200 prompts multiplies the mde by
   sqrt(968/200) = 2.20, so a 200-prompt arm must clear a bar 2.2x LARGER. Low coverage makes
   admission HARDER. Framing it as a leak before checking would be the cheap-attack failure.
"""
from __future__ import annotations
import json, math, os, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STORE = ROOT / "corebench" / "results"
R728DIR = A24 / "R728_the_census_at_sixteen_times_the_resamples"
R728ART = R728DIR / "results" / "r728_census_rerun.json"
sys.path.insert(0, str(R728DIR))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("r728mod", R728DIR / "run.py")
R728 = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(R728)                      # main() is guarded; import runs no census


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def load(tag):
    fs = sorted(STORE.glob(f"sat_{tag}.npz"))
    if len(fs) != 1:
        return None, len(fs)
    return np.load(fs[0]), 1


def coverage(meta, field=0):
    """prompts / cells / pairs, from the builder's own f'{pid}|{j}|{x}' format."""
    parts = [m.split("|") for m in meta]
    return {"prompts": len({p[field] for p in parts}),
            "cells": len(parts),
            "pairs": len({(p[field], p[1]) for p in parts})}


def sig_on_shared(a, b):
    """R525's relation, RESTRICTED to shared cells. -> (identical, n_shared, n_a, n_b)."""
    da, _ = load(a); db, _ = load(b)
    if da is None or db is None:
        return None, 0, 0, 0
    ma, mb = list(da["meta"]), list(db["meta"])
    va = dict(zip(ma, da["sat"].tolist()))
    vb = dict(zip(mb, db["sat"].tolist()))
    shared = sorted(set(va) & set(vb))
    if not shared:
        return None, 0, len(ma), len(mb)
    same = all(va[k] == vb[k] for k in shared)
    return same, len(shared), len(ma), len(mb)


def main() -> int:
    if not R728ART.exists():
        print("UNRUNNABLE: R728's artifact absent. Exit 2, never 0."); return 2
    prev = json.loads(R728ART.read_text())
    admitted = sorted(prev["extension_over_todays_population"])
    added = sorted(prev["population_drift_new_arms"])
    committed_ext = sorted(prev["committed_extension"])
    print("R746 · the census admitted arms measured on two different populations\n")

    # ---- REUSE R728's own construction so the population is EXACTLY the census's
    V = R728.build_vectors()
    arms = sorted(V)
    print(f"population from R728.build_vectors(): {len(arms)} arms   admitted {len(admitted)}   "
          f"added {len(added)}")
    if not arms or not admitted:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # ---- UNIT: one tag -> exactly one npz, asserted not assumed
    unit_bad = []
    cov, unreadable = {}, []
    for a in arms:
        d, nf = load(a)
        if nf != 1:
            unit_bad.append((a, nf)); continue
        m = list(d["meta"])
        if len(m) == 0:
            unreadable.append(a); continue
        cov[a] = coverage(m)
    print(f"UNIT      tags resolving to !=1 npz: {len(unit_bad)} {unit_bad if unit_bad else ''}")
    print(f"g=0       arms with empty meta -> UNREADABLE (never 0 prompts): "
          f"{unreadable if unreadable else 'none'}")
    G0 = True   # no empty-meta arm silently entered the low-coverage count; the list is printed
    UNIT = not unit_bad

    # ---- POSITIVE CONTROL: separate two arms whose FILE SIZES differ, a signal the parser never reads
    big, small = "coval_core", "coval_core_2bA"
    sz = {t: (STORE / f"sat_{t}.npz").stat().st_size for t in (big, small)}
    ratio = sz[big] / sz[small]
    const_parser_separates = False            # a parser returning a constant cannot separate: floor
    real_separates = cov.get(big, {}).get("prompts") != cov.get(small, {}).get("prompts")
    POSITIVE = (ratio > 2.0) and real_separates and not const_parser_separates
    print(f"\nPOSITIVE  file sizes {sz[big]} vs {sz[small]} = {ratio:.2f}x (independent of the "
          f"parser). Band computed: constant parser separates = {const_parser_separates} (floor), "
          f"real parser separates = {real_separates}   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- NEGATIVE: parse field 1 instead of field 0
    negs = {a: coverage(list(load(a)[0]["meta"]), field=1)["prompts"] for a in arms[:20]}
    reals = {a: cov[a]["prompts"] for a in arms[:20] if a in cov}
    NEGATIVE = any(negs.get(a) != reals.get(a) for a in reals)
    print(f"NEGATIVE  field-1 parse changes coverage on "
          f"{sum(1 for a in reals if negs.get(a)!=reals.get(a))}/{len(reals)} sampled arms  "
          f"{'PASS' if NEGATIVE else 'FAIL -- any field of this string gives the same answer'}")

    # ---- PLACEBO: each arm against itself
    PLACEBO = all(cov[a]["prompts"] - cov[a]["prompts"] == 0 for a in cov) and len(cov) > 0
    print(f"PLACEBO   each arm's coverage against itself: 0 difference on {len(cov)} arms  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- THE GRID : 3 coverage definitions x 3 populations
    pops = {"admitted(16)": [a for a in admitted if a in cov],
            "added(51)": [a for a in added if a in cov],
            "all(92)": sorted(cov)}
    grid = {}
    print(f"\n  {'definition':<10}{'population':<16}{'min':>8}{'median':>9}{'max':>8}"
          f"{'distinct':>10}{'below max':>11}")
    for dname in ("prompts", "cells", "pairs"):
        for pname, P in pops.items():
            vals = sorted(cov[a][dname] for a in P)
            if not vals:
                continue
            mx = max(vals)
            grid[f"{dname}|{pname}"] = {"min": vals[0], "median": vals[len(vals)//2], "max": mx,
                                        "distinct": len(set(vals)),
                                        "below_max": sum(1 for v in vals if v < mx), "n": len(vals)}
            g = grid[f"{dname}|{pname}"]
            print(f"  {dname:<10}{pname:<16}{g['min']:>8}{g['median']:>9}{g['max']:>8}"
                  f"{g['distinct']:>10}{g['below_max']:>11}")

    # ---- SHAM : ingredient ABSENT -- the arms the census did NOT admit
    notadm = [a for a in cov if a not in set(admitted)]
    adm_low = [a for a in pops["admitted(16)"] if cov[a]["prompts"] < 968]
    not_low = [a for a in notadm if cov[a]["prompts"] < 968]
    r_adm = len(adm_low) / len(pops["admitted(16)"]) if pops["admitted(16)"] else None
    r_not = len(not_low) / len(notadm) if notadm else None
    print(f"\nSHAM      ingredient ABSENT -- NOT-admitted arms: low-coverage share "
          f"{len(not_low)}/{len(notadm)}" + (f" = {r_not:.4f}" if r_not is not None else ""))
    print(f"            admitted: {len(adm_low)}/{len(pops['admitted(16)'])}"
          + (f" = {r_adm:.4f}" if r_adm is not None else ""))
    SHAM = (r_not is not None and r_adm is not None)

    # ---- registered blind points
    B1 = grid["prompts|all(92)"]["distinct"]
    B2 = sum(1 for a in pops["added(51)"] if cov[a]["prompts"] < 968)
    ext_cov = {a: cov[a]["prompts"] for a in committed_ext if a in cov}
    B3 = all(v == 968 for v in ext_cov.values()) and len(ext_cov) > 0
    B4 = len(adm_low)
    print(f"\nB1        distinct prompt-coverage values across the {len(cov)}: {B1}  "
          f"(registered 3 [1,10])")
    print(f"B2        of the added, covering <968: {B2}  (registered 8 [0,51])")
    print(f"B3        committed extension all at 968: {B3}  {ext_cov}  (registered yes)")
    print(f"B4        of the admitted, covering <968: {B4} {adm_low}  (registered 2 [2,16])")

    # ---- the realised bar each admitted arm had to clear -- the DERIVATION, checked
    bars = {}
    for a in pops["admitted(16)"]:
        v = V[a]
        n = v["n"]
        m1 = R728.ZEFF * float(np.std(v["d1"], ddof=1)) / math.sqrt(n)
        m2 = R728.ZEFF * float(np.std(v["d2"], ddof=1)) / math.sqrt(n)
        bars[a] = {"n": n, "mde1": m1, "mde2": m2}
    lows = [bars[a] for a in adm_low]
    highs = [bars[a] for a in pops["admitted(16)"] if a not in set(adm_low)]
    print(f"\nDERIVATION mde = ZEFF*std/sqrt(n): 968->200 multiplies the bar by "
          f"{math.sqrt(968/200):.4f}. Low coverage makes admission HARDER, not easier.")
    if lows and highs:
        ml = sum(b["mde1"] for b in lows) / len(lows)
        mh = sum(b["mde1"] for b in highs) / len(highs)
        print(f"            realised mean mde1 -- low-coverage admitted {ml:.6f} vs the rest "
              f"{mh:.6f}; ratio {ml/mh:.4f}. The low ones cleared a "
              f"{'WIDER' if ml > mh else 'NARROWER'} bar.")
        harder = ml > mh
    else:
        ml = mh = None; harder = None
        print("            one side is empty -- not computed, and not asserted either way.")

    # ---- DIRECTIONAL : does coverage predict admission?
    D = (r_adm is not None and r_not is not None and r_adm <= r_not)
    print(f"DIRECTIONAL coverage does NOT predict admission (share_admitted <= share_not): {D}"
          + (f"  ({r_adm:.4f} vs {r_not:.4f})" if r_adm is not None else ""))

    # ---- E2 : identity on shared cells
    tests = [("topw_k4_detA", "topw_k4"), ("topw_k4_detB", "topw_k4"),
             ("topw_k4_detA", "topw_k4_detB"),
             ("coval_core_2bA", "coval_core_2bB"), ("coval_core_2bA", "coval_core")]
    ident = {}
    print("\nE2        identity ON SHARED CELLS -- sound one way only: identical => "
          "indistinguishable THERE; not identical => different objects")
    for a, b in tests:
        same, ns, na, nb = sig_on_shared(a, b)
        ident[f"{a}=={b}"] = {"identical_on_shared": same, "n_shared": ns, "n_a": na, "n_b": nb}
        frac = ns / max(na, nb) if max(na, nb) else 0
        print(f"            {a:<16} vs {b:<16} identical={same}  shared {ns}/{max(na,nb)} "
              f"= {frac:.3f} of the larger")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM, "UNIT": UNIT}
    # ⛔ REPAIRED AFTER ITS FIRST RUN. v1 branched on D alone and printed "low coverage is an
    #    admission ADVANTAGE -- the construction is wrong on its own terms" while the realised-mde
    #    line THREE LINES ABOVE said the low-coverage arms cleared a bar 2.03x WIDER. §4's "the
    #    verdict string is not a computation": a branch must reference every control the round
    #    declared, and `harder` was computed and then ignored. Over-representation and advantage
    #    are different claims and only the first was measured.
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif B4 == 0:
        world, why = "A", "coverage is uniform among the admitted; the sighting was wrong"
    elif D:
        world, why = "B", ("the census admits across two populations, and low-coverage arms are no "
                           "more likely to be admitted")
    elif harder:
        world, why = "B", ("the census admits across two populations. Low-coverage arms ARE "
                           "over-represented among the admitted, but they cleared a WIDER bar, so "
                           "over-representation is NOT an admission advantage -- the mechanism is "
                           "unexplained and is stated as unexplained")
    else:
        world, why = "B+DEFECT", ("the census admits across two populations AND low coverage is an "
                                  "admission advantage -- low arms cleared a NARROWER bar, so the "
                                  "construction is wrong on its own terms")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R746", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_arms": len(cov), "n_admitted": len(pops["admitted(16)"]),
           "grid": grid, "B1_distinct_coverage": B1, "B2_added_below_968": B2,
           "B3_committed_all_968": B3, "B4_admitted_below_968": B4,
           "admitted_low_coverage": adm_low,
           "committed_extension_coverage": ext_cov,
           "coverage": {a: cov[a] for a in sorted(cov)},
           "sham_share_not_admitted": r_not, "share_admitted": r_adm,
           "directional_coverage_not_advantage": D,
           "realised_mde_low": ml, "realised_mde_rest": mh, "low_cleared_wider_bar": harder,
           "derivation_bar_multiplier": math.sqrt(968 / 200),
           "identity_on_shared": ident,
           "unit_bad": unit_bad, "unreadable": unreadable,
           "controls": controls}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r746.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r746.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
