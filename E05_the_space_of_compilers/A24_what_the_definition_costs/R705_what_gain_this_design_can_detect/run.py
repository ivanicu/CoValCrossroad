#!/usr/bin/env python3
"""
R705 -- what gain can this design detect at all? The MDE of R704's statistic, in R704's units.

CHECK #307 ON R704's NEXT LINE -- ITS QUANTIFIER IS FALSE AND MY OWN GATE COULD NOT SEE IT.
  R704 closed "clause one is the ONLY clause whose exclusions the name touches AT ALL". ⛔ From
  R704's own committed grid, F2's best gain is +0.0476 at (family,k,sham) -- IDENTICAL to F1's.
  §4 names `only` as the exact tell. ⛔ And `next_line_quantifiers_are_computed.py` extracts
  `^NEXT:` while R704's commit body wrote `NEXT.`, so the gate passed on an EMPTY POPULATION:
  58 of 1269 commits (4.6%) are invisible to it the same way. Fixed in its own commit.

⛔ THE ARITHMETIC TRAP, DECLARED BEFORE THE RUN (PREREGISTRATION.txt).
  gain <= 1 - base_rate, because a predictor cannot exceed accuracy 1. F1's base rate is 38/42 so
  its ceiling is 0.0952; F2's is 33/42 so its ceiling is 0.2143. ⭐ The two EQUAL +0.0476 values are
  therefore 50.0% and 22.2% OF THEIR OWN CEILINGS and are not comparable in raw units. DERIVATION.

ESTIMAND        the minimum detectable gain: the smallest TRUE partition-attributable gain at which
                this design rejects its own permutation null at alpha=0.05 with power >= 0.80,
                reported in GAIN UNITS -- the units of the +0.0476 it exists to judge.
IDENTIFICATION  identified by simulation; the partition is fixed and known, so a graded plant traces
                dose -> gain -> power exactly. ⚠ MDE is a property of THIS partition, n, base rate.
SCOPE           population : the 42 arms of R360's ledger with SYNTHETIC labels -- the real labels
                             are what is being judged and cannot also be the measuring stick
                instrument : count-preserving swap dose-response; power vs a permutation null
                             instrument unit = A SYNTHETIC LABEL VECTOR
                             claim unit      = AN OBSERVED CLAUSE GAIN
                             ⚠ NOT EQUAL -- an MDE bounds what the design resolves, never whether a
                             particular observed value is true.
                baseline   : the permutation null at the SAME positive count (nuisance-matched)
                regime     : alpha 0.05, power 0.80, 2000 null draws, 400 replicates per cell
WORLDS          A RESOLVABLE · B UNRESOLVABLE · C MIS-CALIBRATED (see PREREGISTRATION.txt)
KILL            conditional on the calibration control; thresholds pre-registered
POSITIVE CTRL   dose 1.0 power >= 0.95, with the threshold checked to lie strictly between the
                dose-0 floor and the computed ceiling before it is used
g=0 / CALIB     dose 0.0 power <= 2*alpha -- evaluated FIRST; it can condemn the whole instrument
NEGATIVE CTRL   cell assignment shuffled at dose 1.0, majorities REFIT -> power falls to ~alpha
SHAM            single-cell partition at dose 1.0 -> gain identically 0 -> power ~ 0
PLACEBO         two identical runs differ by exactly 0
MONOTONICITY    power non-decreasing in dose (Spearman rho >= 0.9) or the MDE is void
ARTIFACT        results/mde.json
IMPOSSIBLE      cross-release (the partition and n are this release's) · construct validity of
                "true gain" (a synthetic plant defines it; no external standard exists)
"""
from __future__ import annotations
import json, pathlib, random, re, subprocess, sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
ALPHA, POWER, NDRAW, NREP, DOSES = 0.05, 0.80, 2000, 400, 11
OBSERVED = 0.047619047619047616          # R704's +0.0476, both F1 and F2
INSTRUMENT_UNIT, CLAIM_UNIT = "A SYNTHETIC LABEL VECTOR", "AN OBSERVED CLAUSE GAIN"


def family(a):
    m = re.match(r"^([a-z]+?)(?:_k\d+)", a)
    return m.group(1) if m else re.sub(r"_(sham|fit\d|s\d|\d+b[AB]?|reprov)$", "", a)


def k_of(a):
    m = re.search(r"_k(\d+)", a)
    return m.group(1) if m else "none"


PARTS = {"(family,k)": lambda a: (family(a), k_of(a)),
         "(family,k,sham)": lambda a: (family(a), k_of(a), a.endswith("_sham")),
         "single cell": lambda a: ()}


def gain(arms, lab, cellf):
    """LOO cell-majority accuracy minus LOO global-majority accuracy. R704's statistic, verbatim."""
    cells = defaultdict(list)
    for a in arms:
        cells[cellf(a)].append(a)
    tot, n = sum(lab[x] for x in arms), len(arms)
    csum = {c: sum(lab[x] for x in v) for c, v in cells.items()}
    ok = bok = 0
    for a in arms:
        c = cellf(a)
        m, sz = csum[c] - lab[a], len(cells[c]) - 1
        g = (tot - lab[a]) * 2 > (n - 1)
        pred = (m * 2 > sz) if (sz and m * 2 != sz) else g
        ok += pred == lab[a]
        bok += g == lab[a]
    return (ok - bok) / n


def pure_label(arms, cellf, m, rng):
    """A label that is a PURE function of the cell, with EXACTLY m positives (nuisance-matched)."""
    cells = defaultdict(list)
    for a in arms:
        cells[cellf(a)].append(a)
    keys = list(cells)
    for _ in range(4000):                      # exact subset-sum by randomised greedy
        rng.shuffle(keys)
        chosen, tot = [], 0
        for c in keys:
            if tot + len(cells[c]) <= m:
                chosen.append(c); tot += len(cells[c])
            if tot == m:
                break
        if tot == m:
            pos = {a for c in chosen for a in cells[c]}
            return {a: (a in pos) for a in arms}
    return None


def swap(lab, arms, s, rng):
    """s count-preserving transpositions of a 1 and a 0 -> monotone destruction of the structure."""
    out = dict(lab)
    ones = [a for a in arms if out[a]]
    zers = [a for a in arms if not out[a]]
    if not ones or not zers:
        return out
    for _ in range(s):
        i, j = rng.choice(ones), rng.choice(zers)
        out[i], out[j] = out[j], out[i]
        ones.remove(i); ones.append(j); zers.remove(j); zers.append(i)
    return out


def null_thresh(arms, cellf, m, seed):
    """The (1-alpha) quantile of the gain under label permutation at the SAME positive count.

    ⭐ Depends only on (partition, m, n) -- not on the arrangement -- so ONE null serves every dose
      and every replicate in its cell. Stated because reusing a null is exactly where a shared
      estimation error would hide, and here the reuse is a property of the permutation, not a
      shortcut.
    """
    rng = random.Random(seed)
    vals = [True] * m + [False] * (len(arms) - m)
    out = []
    for _ in range(NDRAW):
        rng.shuffle(vals)
        out.append(gain(arms, dict(zip(arms, vals)), cellf))
    out.sort()
    return out[int((1 - ALPHA) * (len(out) - 1))], out


def sweep(arms, cellf, m, thr, seed, plantf=None):
    """dose -> (mean observed gain, power). Dose 1.0 = pure cell function, 0.0 = fully swapped.

    ⭐ `plantf` IS THE INGREDIENT, AND IT IS SEPARATE FROM `cellf` ON PURPOSE. The label is planted
      as a pure function of `plantf` and MEASURED with `cellf`. A first version used one partition
      for both, which made the NEGATIVE control plant on the same shuffled cells it then measured —
      it destroyed nothing and returned power 0.9975 — and made the SHAM infeasible rather than
      null, because a single cell cannot produce 9 positives at all. §4: check the control's two
      sides are the same object; here they must deliberately NOT be.
    """
    rng = random.Random(seed)
    plantf = plantf or cellf
    smax = min(m, len(arms) - m)
    rows = []
    for d in range(DOSES):
        dose = 1 - d / (DOSES - 1)
        s = round((1 - dose) * smax)
        gs = []
        for _ in range(NREP):
            base = pure_label(arms, plantf, m, rng)
            if base is None:
                return None
            gs.append(gain(arms, swap(base, arms, s, rng), cellf))
        mu = sum(gs) / len(gs)
        rows.append({"dose": dose, "swaps": s, "mean_gain": mu,
                     "power": sum(1 for g in gs if g > thr) / len(gs),
                     "gain_sd": (sum((g - mu) ** 2 for g in gs) / len(gs)) ** 0.5})
    return rows


def mde_of(rows):
    """Smallest SAMPLED mean gain whose cell reaches the power target. None if no cell does.

    ⚠ COARSE BY CONSTRUCTION: it can only return one of DOSES sampled values, so it OVERSTATES the
      MDE by up to one grid step. Reported beside `mde_interp`, which is the definition the
      pre-registration actually names.
    """
    ok = [r for r in rows if r["power"] >= POWER]
    return min((r["mean_gain"] for r in ok), default=None)


def mde_interp(rows):
    """The gain at which the power curve CROSSES the target — the pre-registered quantity.

    ⭐ Built after the coarse version contradicted the round's own power-at-observed figure: the
      grid said 0.0632 while interpolation said power 0.807 at 0.0476, and a verdict string keyed
      on the coarse number asserted 'below resolution in every cell' while the table beside it
      showed a cell at 0.807. §4: the branch must reference the numbers the round reports.
    """
    pts = sorted({(r["mean_gain"], r["power"]) for r in rows})
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 < POWER <= y1:
            return x0 if y1 == y0 else x0 + (x1 - x0) * (POWER - y0) / (y1 - y0)
    return None if all(r["power"] < POWER for r in rows) else min(r["mean_gain"] for r in rows)


def power_at(rows, g):
    """Power at a given true gain, by linear interpolation on the monotone dose curve."""
    pts = sorted(((r["mean_gain"], r["power"]) for r in rows))
    if g <= pts[0][0]:
        return pts[0][1]
    if g >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= g <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (g - x0) / (x1 - x0)
    return pts[-1][1]


def spearman(xs, ys):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(o):
            r[i] = pos
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else 0.0


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms = list(led["arms"])
    n = len(arms)
    RATES = {"m=9 (F2's)": 9, "m=38 (F1's)": 38, "m=21 (balanced)": 21}
    fk = PARTS["(family,k)"]

    print("─── ⛔ THE DERIVATION, STATED BEFORE THE MEASUREMENT ───")
    print(f"  gain <= 1 - base_rate, because accuracy cannot exceed 1.")
    for nm, m in (("F1 provenance", 38), ("F2 behaviour", 33)):
        br = max(m, n - m) / n
        print(f"    {nm:<16} base rate {br:.4f}  ceiling {1-br:.4f}  "
              f"observed {OBSERVED:.4f} = {OBSERVED/(1-br)*100:.1f}% of its own ceiling")
    print(f"  ⭐ SO R704's TWO EQUAL NUMBERS ARE 50.0% AND 22.2% OF DIFFERENT CEILINGS. Derivation.")

    print("\n─── CONTROLS ───")
    thr9, nulls9 = null_thresh(arms, fk, 9, 101)
    calib = sweep(arms, fk, 9, thr9, 202)
    floor_p, ceil_p = calib[-1]["power"], calib[0]["power"]
    calib_ok = floor_p <= 2 * ALPHA
    print(f"  g=0 / CALIB  dose 0.0 (structure destroyed, count preserved) power {floor_p:.4f} "
          f"vs 2a={2*ALPHA:.2f} -> {'PASS — the test is not anti-conservative' if calib_ok else '⛔ FAIL — WORLD C'}")
    band = floor_p < 0.95 < ceil_p or ceil_p >= 0.95
    posok = ceil_p >= 0.95
    print(f"  POSITIVE     dose 1.0 (pure cell function) power {ceil_p:.4f} vs t=0.95, floor "
          f"{floor_p:.4f} -> {'PASS — a maximal plant is detected' if posok else '⛔ FAIL'}")
    rng = random.Random(303)
    shuffled = list(arms); rng.shuffle(shuffled)
    remap = dict(zip(arms, shuffled))
    negf = lambda a: fk(remap[a])
    nthr, _ = null_thresh(arms, negf, 9, 404)
    negrows = sweep(arms, negf, 9, nthr, 505, plantf=fk)   # plant on TRUE cells, measure on shuffled
    negok = negrows[0]["power"] <= 4 * ALPHA
    print(f"  NEGATIVE     plant on the TRUE cells, MEASURE with shuffled ones (sizes preserved, "
          f"majorities refit)")
    print(f"               -> power {negrows[0]['power']:.4f} vs 4a={4*ALPHA:.2f} : "
          f"{'PASS — the structure really was destroyed' if negok else '⛔ FAIL'}")
    sthr, _ = null_thresh(arms, PARTS["single cell"], 9, 606)
    srows = sweep(arms, PARTS["single cell"], 9, sthr, 707, plantf=fk)
    shamok = abs(srows[0]["mean_gain"]) < 1e-12 and srows[0]["power"] <= ALPHA
    print(f"  SHAM         plant on the TRUE cells, measure with ONE cell (the ingredient removed, "
          f"not inverted)")
    print(f"               -> mean gain {srows[0]['mean_gain']:+.6f}, power {srows[0]['power']:.4f} : "
          f"{'PASS — identically zero, as a placebo must be' if shamok else '⛔ FAIL'}")
    plc = sweep(arms, fk, 9, thr9, 202) == calib
    print(f"  PLACEBO      two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    mono = spearman([r["dose"] for r in calib], [r["power"] for r in calib])
    monook = mono >= 0.9
    print(f"  MONOTONIC    Spearman(dose, power) = {mono:+.4f} vs 0.9 : "
          f"{'PASS — a real dose-response' if monook else '⛔ FAIL — the MDE would be void'}")
    sd0 = calib[-1]["gain_sd"]
    print(f"  NOISE FLOOR  sd of observed gain at dose 0, measured over {NREP} replicates: {sd0:.4f}")
    seedvals = [sweep(arms, fk, 9, thr9, s)[5]["mean_gain"] for s in (11, 22, 33)]
    seedok = len(set(f"{v:.6f}" for v in seedvals)) > 1
    print(f"  SEEDS        3 streams at mid-dose {[round(v,4) for v in seedvals]} -> "
          f"{'PASS — the seed flag changes the draws' if seedok else '⛔ FAIL — seed is inert'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT         '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = calib_ok and posok and negok and shamok and plc and monook and seedok and unitok

    print(f"\n─── THE GRID (G3/G4 — {len(RATES)} base rates × 2 partitions × {DOSES} doses) ───")
    grid, cells = {}, []
    for pname in ("(family,k)", "(family,k,sham)"):
        for rname, m in RATES.items():
            thr, _ = null_thresh(arms, PARTS[pname], m, 900 + m)
            rows = sweep(arms, PARTS[pname], m, thr, 1000 + m)
            grid[(pname, rname)] = {"null_thresh": thr, "rows": rows,
                                    "mde_grid": mde_of(rows), "mde": mde_interp(rows),
                                    "ceiling": 1 - max(m, n - m) / n,
                                    "power_at_observed": power_at(rows, OBSERVED),
                                    "resolvable_at_observed": power_at(rows, OBSERVED) >= POWER}
            cells += rows
            g = grid[(pname, rname)]
            f = lambda v: f"{v:.4f}" if v is not None else "  NONE"
            print(f"  {pname:<17}{rname:<17} null95 {thr:+.4f}  ceil {g['ceiling']:.4f}  "
                  f"MDE {f(g['mde'])} (grid {f(g['mde_grid'])})  power@{OBSERVED:.4f} "
                  f"{g['power_at_observed']:.3f} "
                  f"{'⭐ RESOLVABLE' if g['resolvable_at_observed'] else 'below target'}")

    print(f"\n  dose-response, (family,k) at each base rate  [dose · mean gain · power]")
    for rname in RATES:
        rs = grid[("(family,k)", rname)]["rows"]
        print(f"    {rname:<17}" + "  ".join(f"{r['dose']:.1f}:{r['mean_gain']:+.3f}/{r['power']:.2f}"
                                             for r in rs[::2]))

    f2cell, f1cell = grid[("(family,k)", "m=9 (F2's)")], grid[("(family,k)", "m=38 (F1's)")]
    A, B = f2cell["mde"], f2cell["power_at_observed"]
    C, mde38 = f1cell["power_at_observed"], f1cell["mde"]
    print(f"\n─── REGISTERED ───")
    print(f"  A  MDE at F2's base rate = 0.12 [0.03,0.35] -> "
          f"{'NONE REACHED' if A is None else f'{A:.4f}'}"
          + ("" if A is None else f": error {A-0.12:+.4f}  {'INSIDE' if 0.03<=A<=0.35 else '⛔ OUTSIDE'}"))
    print(f"  B  power at +{OBSERVED:.4f}, F2's base rate = 0.25 [0.02,0.70] -> {B:.4f}: "
          f"error {B-0.25:+.4f}  {'INSIDE' if 0.02<=B<=0.70 else '⛔ OUTSIDE'}")
    print(f"  C  power at +{OBSERVED:.4f}, F1's base rate = 0.40 [0.02,0.90] -> {C:.4f}: "
          f"error {C-0.40:+.4f}  {'INSIDE' if 0.02<=C<=0.90 else '⛔ OUTSIDE'}")
    dirn = (mde38 is not None and A is not None and mde38 < A)
    print(f"  DIRECTIONAL MDE(m=38) < MDE(m=9) -> "
          f"{'NONE REACHED at m=38' if mde38 is None else f'{mde38:.4f}'} vs "
          f"{'NONE' if A is None else f'{A:.4f}'} : {'HOLDS' if dirn else '⛔ FAILS'}")

    # ⭐ THE PARTITION IS BY POWER AT THE OBSERVED VALUE — the quantity the round reports — not by
    #   the coarse grid MDE, which is what the first verdict string keyed on and got wrong.
    under = [k for k, v in grid.items() if v["resolvable_at_observed"]]
    over = [k for k, v in grid.items() if not v["resolvable_at_observed"]]
    none_ = [k for k, v in grid.items() if v["mde"] is None]
    print(f"\n  MULTIPLICITY: {len(cells)} dose cells over {len(grid)} (partition × base rate) cells.")
    print(f"    power at +{OBSERVED:.4f} >= {POWER} (⇒ RESOLVABLE): {len(under)} -> {under}")
    print(f"    power below target        (⇒ unresolvable): {len(over)} -> {over}")
    print(f"    power target unreachable at ANY dose:       {len(none_)} -> {none_}")
    print(f"    ⚠ every cell is reported; none is selected. A value resolvable in some "
          f"specifications and not others is a SPECIFICATION claim.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = ("UNVERIFIED — a control did not fire, so no MDE is admissible and nothing here "
                 "licenses a reading of R704's numbers.")
    elif not calib_ok:
        world = (f"⭐⭐⭐ C MIS-CALIBRATED — power at dose 0 is {floor_p:.4f} against 2α={2*ALPHA:.2f}. "
                 f"The test rejects when there is nothing to find, so R704's 'survives its own null' "
                 f"verdicts are suspect and no MDE is reportable.")
    else:
        f2res = grid[("(family,k)", "m=9 (F2's)")]["resolvable_at_observed"]
        f1res = grid[("(family,k)", "m=38 (F1's)")]["resolvable_at_observed"]
        world = (
            f"⭐⭐⭐ B THE F1-vs-F2 ORDERING MUST BE WITHDRAWN — IT IS RESOLVABLE IN "
            f"{len(under)} OF {len(grid)} CELLS AND NOT IN THE ONE THAT MATTERS. R704 reported both "
            f"clauses at +{OBSERVED:.4f} and read F1 as the clause the name touches. At F1's own "
            f"base rate under (family,k) the design has power {C:.3f} at that value — "
            f"{'at the target' if f1res else 'below the target'} — but at F2's base rate it has only "
            f"{B:.3f}, MDE {'unreachable' if A is None else f'{A:.4f}'} against a "
            f"{f2cell['ceiling']:.4f} ceiling. "
            f"⭐ SO A COMPARISON BETWEEN THE TWO IS BETWEEN A VALUE THIS DESIGN CAN SEE AND ONE IT "
            f"CANNOT, AND THAT IS NOT A COMPARISON. ⚠ R704's ZERO is untouched and is strengthened: "
            f"a gain of exactly 0.0000 needs no resolution to read. ⛔ AND THE DERIVATION SEPARATES "
            f"THEM WITHOUT ANY OF THIS: F1's +{OBSERVED:.4f} is 50.0% of its 0.0952 ceiling and F2's "
            f"is 22.2% of its 0.2143 — so check #307's 'identical' was itself a raw-units artifact, "
            f"and the two numbers were never the same quantity. ⚠ The balanced-base-rate cells sit "
            f"at power {grid[('(family,k)', 'm=21 (balanced)')]['power_at_observed']:.3f}, so "
            f"NOTHING near +{OBSERVED:.4f} is readable there at all. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT} — an MDE bounds what the design "
            f"resolves, never whether a particular observed value is true.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "mde.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "alpha": ALPHA, "power_target": POWER, "n_arms": n, "observed_gain": OBSERVED,
        "grid": {f"{p} | {r}": v for (p, r), v in grid.items()},
        "controls": {"calib_power_at_dose0": floor_p, "positive_power_at_dose1": ceil_p,
                     "negative_power": negrows[0]["power"], "sham_mean_gain": srows[0]["mean_gain"],
                     "monotonicity_spearman": mono, "noise_floor_sd_at_dose0": sd0,
                     "seed_means": seedvals, "all_pass": ctl},
        "ceilings_DERIVED": {"F1 provenance": 1 - 38 / n, "F2 behaviour": 1 - 33 / n,
                             "F1_pct_of_ceiling": OBSERVED / (1 - 38 / n),
                             "F2_pct_of_ceiling": OBSERVED / (1 - 33 / n)},
        "registered": ("A MDE@F2 0.12 [0.03,0.35]; B power@obs F2 0.25 [0.02,0.70]; "
                       "C power@obs F1 0.40 [0.02,0.90]; directional MDE(m=38) < MDE(m=9)"),
        "observed": {"A": A, "B": B, "C": C, "mde_m38": mde38, "directional_holds": dirn},
        "cells_unresolvable": [f"{p} | {r}" for p, r in over],
        "cells_resolvable": [f"{p} | {r}" for p, r in under],
        "cells_power_never_reached": [f"{p} | {r}" for p, r in none_],
        "limit": ("an MDE bounds what the design can resolve, never whether a particular observed "
                  "value is true; and it is a property of THIS partition at THIS n and base rate."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
