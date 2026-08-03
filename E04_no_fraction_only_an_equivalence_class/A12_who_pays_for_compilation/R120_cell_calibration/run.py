"""r120 -- is a non-surviving cell a NULL or a SILENCE? Every cell classified against planted effects.

r118 reports 502 of 628 cells as non-survivors. This project's oldest rule says a zero from an
instrument never shown to return non-zero is silence and not an acquittal -- and at 628-cell scale
that rule cannot be discharged by one positive control, because the 628 cells are 628 instruments.

So the plant becomes a variation of the WHOLE grid (r118 --plant), and this round crosses the planted
grids against the base to give every cell one of three labels:

  CALIBRATED   the cell's statistic moves when the plant targets ITS OWN bearer. Its null is a
               measurement, and the smallest dose at which it moves is that cell's MDE.
  INSENSITIVE  the cell does not move at ANY dose on its own bearer. Its null is SILENCE. Every
               conclusion drawn from that cell's non-survival is withdrawn.
  MISDIRECTED  the cell moves on a plant aimed at a DIFFERENT bearer. That is worse than
               insensitive: it means the bearer axis LEAKS, and a "prompt-level sacrifice" could be
               a person-level effect arriving through the prompt statistic.

MISDIRECTED is the label this round exists for. The whole campaign's ontology rests on the bearers
being separable -- 107 of 111 full-depth cells are prompt-borne, and that sentence is only meaningful
if a prompt cell cannot be moved by a person-level plant. Nobody has checked. Checking it is the
cheapest possible attack on the campaign's headline and it costs nine grids already running.

WHAT COUNTS AS "MOVES"
----------------------
Not a p-value comparison: p is bounded below by 1/(N+1) and a strongly-significant cell cannot get
more significant, so a real effect can leave p unchanged. The statistic's OBSERVED value against its
own null spread is the right scale:

    move_z = |obs_planted - obs_base| / sd(null_base)

with a pre-registered threshold of 2. That is a shift of two null standard deviations in the
statistic itself, which is scale-free across the six statistics and does not saturate.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx.stamp import stamp  # noqa: E402

BASE = _ROOT / "E04_no_fraction_only_an_equivalence_class/A12_who_pays_for_compilation/R118_sacrifice_factorial/results/r118_sacrifice_factorial.json"
MOVE_Z = 2.0          # pre-registered: two null sd of the statistic itself
DOSES = ("0.02", "0.05", "0.10")


def key(g):
    return (g["block"], g["bearer"], g["arms"], g["stat"], str(g["eps"]), g["purge"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--planted", required=True,
                    help="comma-separated bearer:dose=path entries")
    ap.add_argument("--out", default=str(_RES / "r120_cell_calibration.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

    if not BASE.exists():
        print(f"REFUSING: base grid absent at {BASE}. Exits 2, never 0.", file=sys.stderr)
        return 2
    base = json.loads(BASE.read_text())
    B = {key(g): g for g in base["grid"]}

    planted = {}
    for spec in filter(None, (s.strip() for s in args.planted.split(","))):
        tag, _, path = spec.partition("=")
        bearer, _, dose = tag.partition(":")
        p = Path(path)
        if not p.exists():
            print(f"  MISSING {tag}: {path} -- not counted, and its absence is stated",
                  file=sys.stderr)
            continue
        planted[(bearer, dose)] = {key(g): g for g in json.loads(p.read_text())["grid"]}
    if not planted:
        print("REFUSING: no planted grids supplied, so every cell would be labelled INSENSITIVE by "
              "default -- a classification produced by having no evidence. Exits 2.", file=sys.stderr)
        return 2

    bearers = sorted({b for b, _d in planted})
    doses = sorted({d for _b, d in planted})
    print(f"base grid {len(B)} cells; planted grids: {len(planted)} "
          f"({len(bearers)} bearers x {len(doses)} doses)")

    # sd of each cell's own null, reconstructed from the base grid's floor and observed spread.
    # The grid stores floor (null mean) and p but not the null sd, so the sd is estimated from the
    # two-sided p and the observed departure -- stated because it is an approximation, not a read.
    def null_sd(g):
        from math import sqrt, erf
        p = min(max(g["p"], 1e-6), 1 - 1e-6)
        # invert a two-sided normal tail: |obs-floor| = z*sd  ->  sd = |obs-floor| / z(p)
        lo, hi = 0.0, 10.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if 2 * (1 - 0.5 * (1 + erf(mid / sqrt(2)))) > p:
                lo = mid
            else:
                hi = mid
        z = max((lo + hi) / 2, 1e-3)
        return abs(g["obs"] - g["floor"]) / z

    rows = []
    for k, g in B.items():
        sd = null_sd(g)
        if not np.isfinite(sd) or sd <= 0:
            rows.append({"cell": list(k), "label": "UNSCORABLE",
                         "why": "null sd not reconstructible from p and departure"})
            continue
        own, other, mde = {}, {}, None
        for (bearer, dose), P in planted.items():
            if k not in P:
                continue
            z = abs(P[k]["obs"] - g["obs"]) / sd
            if bearer == g["bearer"]:
                own[dose] = z
                if z >= MOVE_Z and (mde is None or float(dose) < float(mde)):
                    mde = dose
            else:
                other[f"{bearer}:{dose}"] = z
        moved_own = any(v >= MOVE_Z for v in own.values())
        moved_other = any(v >= MOVE_Z for v in other.values())
        if not own:
            label = "UNTESTED"
        elif moved_other and not moved_own:
            label = "MISDIRECTED"
        elif moved_own:
            label = "MISDIRECTED-ALSO" if moved_other else "CALIBRATED"
        else:
            label = "INSENSITIVE"
        rows.append({"cell": list(k), "bearer": g["bearer"], "stat": g["stat"],
                     "survivor": bool(g.get("bh") and g.get("purge")),
                     "label": label, "mde": mde,
                     "own_z": {d: round(v, 3) for d, v in sorted(own.items())},
                     "max_other_z": round(max(other.values()), 3) if other else None})

    counts = defaultdict(int)
    for r in rows:
        counts[r["label"]] += 1
    print(f"\n  {'label':<20}{'cells':>8}")
    for k2 in ("CALIBRATED", "INSENSITIVE", "MISDIRECTED", "MISDIRECTED-ALSO", "UNTESTED",
               "UNSCORABLE"):
        if counts[k2]:
            print(f"  {k2:<20}{counts[k2]:>8}")

    surv = [r for r in rows if r.get("survivor")]
    ins_surv = [r for r in surv if r["label"] == "INSENSITIVE"]
    mis_surv = [r for r in surv if r["label"].startswith("MISDIRECTED")]
    nonsurv = [r for r in rows if r.get("survivor") is False]
    ins_non = [r for r in nonsurv if r["label"] == "INSENSITIVE"]
    print(f"\n  OF THE {len(surv)} PURGED SURVIVORS: {len(ins_surv)} are INSENSITIVE "
          f"(they survived while being unable to detect a planted effect) and "
          f"{len(mis_surv)} are MISDIRECTED or also-misdirected.")
    print(f"  OF THE {len(nonsurv)} NON-SURVIVORS: {len(ins_non)} are SILENCE rather than null "
          f"({len(ins_non)/max(len(nonsurv),1):.0%}); the rest are measurements that found nothing.")

    by_b = defaultdict(lambda: defaultdict(int))
    for r in rows:
        if "bearer" in r:
            by_b[r["bearer"]][r["label"]] += 1
    print(f"\n  {'bearer':<15}{'CALIB':>8}{'INSENS':>8}{'MISDIR':>8}{'MIS-ALSO':>10}")
    for b in sorted(by_b):
        c = by_b[b]
        print(f"  {b:<15}{c['CALIBRATED']:>8}{c['INSENSITIVE']:>8}{c['MISDIRECTED']:>8}"
              f"{c['MISDIRECTED-ALSO']:>10}")

    mdes = defaultdict(list)
    for r in rows:
        if r.get("mde"):
            mdes[r["bearer"]].append(float(r["mde"]))
    if mdes:
        print(f"\n  MDE per bearer (smallest planted dose the cell detects):")
        for b, v in sorted(mdes.items()):
            print(f"    {b:<15}n={len(v):>4}  min {min(v):.2f}  median {np.median(v):.2f}  "
                  f"max {max(v):.2f}")

    leak = counts["MISDIRECTED"] + counts["MISDIRECTED-ALSO"]
    world = ("W-BEARERS-LEAK" if leak > 0.10 * len(rows) else
             "W-SILENCE-DOMINATES" if len(ins_non) > 0.5 * max(len(nonsurv), 1) else
             "W-CALIBRATED")
    conclusion = (
        f"Every one of {len(rows)} cells classified against {len(planted)} planted grids at doses "
        f"{', '.join(doses)}, using a shift of {MOVE_Z} null standard deviations in the statistic "
        f"itself rather than a p-value comparison, because p is floored at 1/(N+1) and a strongly "
        f"significant cell cannot become more significant. "
        f"CALIBRATED {counts['CALIBRATED']}, INSENSITIVE {counts['INSENSITIVE']}, MISDIRECTED "
        f"{counts['MISDIRECTED']}, also-misdirected {counts['MISDIRECTED-ALSO']}, untested "
        f"{counts['UNTESTED']}. Of the {len(nonsurv)} non-survivors, {len(ins_non)} "
        f"({len(ins_non)/max(len(nonsurv),1):.0%}) cannot detect a planted effect at any dose and "
        f"are therefore SILENCE rather than null; every conclusion resting on their non-survival is "
        f"withdrawn. Of the {len(surv)} purged survivors, {len(ins_surv)} are insensitive and "
        f"{len(mis_surv)} respond to a plant aimed at another bearer. WORLD: {world}. "
        + ("The bearer axis LEAKS: cells move on plants aimed at other bearers, so a prompt-level "
           "result cannot be distinguished from a person-level effect arriving through the prompt "
           "statistic, and the campaign's central ontological claim is not supported."
           if world == "W-BEARERS-LEAK" else
           "Most non-survivors are silence rather than null, so the grid's negative space carries "
           "far less information than its size suggests."
           if world == "W-SILENCE-DOMINATES" else
           "Cells respond to plants on their own bearer and not to plants on others, so the bearer "
           "axis separates and the non-survivors are measurements rather than silences."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_cells": len(rows), "n_planted_grids": len(planted), "move_z": MOVE_Z,
         "bearers": bearers, "doses": doses, "counts": dict(counts),
         "by_bearer": {b: dict(v) for b, v in by_b.items()},
         "mde_by_bearer": {b: {"n": len(v), "min": min(v), "median": float(np.median(v)),
                               "max": max(v)} for b, v in mdes.items()},
         "n_survivors": len(surv), "n_insensitive_survivors": len(ins_surv),
         "n_misdirected_survivors": len(mis_surv),
         "n_nonsurvivors": len(nonsurv), "n_silent_nonsurvivors": len(ins_non),
         "rows": rows, "world": world, "conclusion": conclusion, **stamp(__file__)},
        indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
