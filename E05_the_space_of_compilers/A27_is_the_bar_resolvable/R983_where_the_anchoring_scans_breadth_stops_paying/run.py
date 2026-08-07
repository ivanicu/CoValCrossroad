#!/usr/bin/env python3
"""R983 — where does widening the anchoring scan stop paying?

⛔ WHY. R982 measured that widening the artifact scan from one arc to all arcs raised the collision
floor from 35–38% to ~92%: it improved coverage and destroyed the test's per-item resolution in the
same move. That is a trade-off with an optimum, and nobody has located it.

⭐ THE FLOOR IS NOT A SAMPLED QUANTITY — IT IS A COUNT, AND THAT IS THE ROUND'S FIRST CONTRIBUTION.
R625 and R982 both estimated it by drawing thousands of random decimals. But a 4-place decimal on
[0,1) lives on a 10,000-point grid, so
        floor(scan) = |values(scan) ∩ grid| / 10000
exactly. Evaluated on the full corpus: **9202/10000 = 0.9202**, against R982's sampled 0.919, 0.922,
0.912. Registered before the sweep, so the agreement is a test of the derivation rather than a fit.
This makes every point on the curve below noiseless in the floor dimension.

ESTIMAND        the scan breadth b maximising Youden's J = recall(b) − floor(b), where
                  recall(b) = share of the document's decimals that a size-b scan locates,
                              normalised to what the full scan locates
                  floor(b)  = the exact collision rate above
IDENTIFICATION  exact in floor, and identified in recall given the full scan as ground truth for
                "this decimal is locatable at all".
                ⚠ THE GROUND TRUTH IS THE FULL SCAN, so recall(full) = 1 BY CONSTRUCTION. That is a
                derivation, not a measurement, and it is why the positive control below is a
                different quantity.
SCOPE           population : the 785 committed round artifacts under E05, and DEFINITION.md's
                             distinct 3–4 place decimals
                instrument : value positions in parsed json (R622's v2 repair, inherited)
                baseline   : b = 0 (no scan), where floor = 0 and recall = 0
                regime     : 4-place decimals on [0,1) for the floor; the grid argument does not
                             transfer to 3 places, where the floor is already ~92% in R625
WORLDS          A MORE IS ALWAYS BETTER   J rises monotonically to b = 785; the widest scan is the
                                          right one and R982's trade-off is not a trade-off.
                B THERE IS AN INTERIOR OPTIMUM  recall saturates before the floor does, so J peaks
                                          at some b < 785 and the widest scan is over-broad.
                prediction matrix: A -> argmax J = 785. B -> argmax J strictly inside, with J
                                   falling measurably at the full scan.
KILL            pre-registered, CONDITIONAL on the controls: if argmax J = 785 at every seed, world
                B is dead. If it is interior at every seed, world A is dead and b* is reported with
                its spread, never as a point.
POSITIVE CTRL   the DERIVED floor must reproduce the SAMPLED floor at full breadth, within the
                sampling error of 12,000 draws. This tests the closed form — which is the part of
                the instrument that is new — rather than restating recall(full) = 1.
NEGATIVE CTRL   at b = 0: floor exactly 0, recall exactly 0, J exactly 0. An instrument returning
                anything else at an empty scan is not measuring breadth.
PLACEBO         a runtime-assembled decimal must be absent from the full scan, so the floor is
                below 1 and the test is not saturated to the point of vacuity.
NOISE FLOOR     the floor dimension is exact; the recall dimension is bootstrapped over which
                artifacts fall in the subset, 5 seeds per breadth.
MULTIPLICITY    every (breadth, seed) cell reported, survivors and non-survivors alike.
SEEDS           5 per breadth; b* reported per seed, never averaged.
ARTIFACT        results/breadth_curve.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: J optimises a detection trade-off, not correctness. A
                decimal found by the optimal scan is still only "some artifact holds these digits".
                cross-release — N/A: one corpus.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import random
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
DEF = E05 / "DEFINITION.md"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
GRID = {f"0.{i:04d}" for i in range(10000)}
BREADTHS = (0, 10, 25, 50, 100, 200, 400, 600, 785)
SEEDS = (1, 2, 3, 4, 5)
NDRAW = 12000


def values_of(path):
    out = set()

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float)):
            for f in (repr(o), f"{o:.4f}", f"{o:.3f}", f"{abs(o):.4f}", f"{abs(o):.3f}"):
                out.add(f.lstrip("+"))
        elif isinstance(o, str) and DEC.fullmatch(o.strip().lstrip("+-")):
            out.add(o.strip().lstrip("+-"))

    try:
        walk(json.loads(path.read_text(errors="ignore")))
    except Exception:
        return None
    return out


def main() -> int:
    SELF = HERE.resolve()
    files = [f for f in sorted(E05.glob("A*/R*/results/*.json"))
             if SELF not in f.resolve().parents]        # R982's self-contamination lesson
    per = [v for v in (values_of(f) for f in files) if v is not None]
    if len(per) < 100:
        print(f"  UNRUNNABLE: only {len(per)} artifacts parsed. Exit 2, never 0.")
        return 2
    full = set().union(*per)
    doc = sorted(set(DEC.findall(DEF.read_text())))
    locatable = [d for d in doc if d in full]
    print(f"POPULATION  {len(per)} artifacts · {len(full)} value strings · "
          f"{len(doc)} distinct decimals in the document, {len(locatable)} locatable at full scan")

    def floor_of(vals):
        return len(vals & GRID) / len(GRID)

    # ── POSITIVE CONTROL: the DERIVED floor must match a SAMPLED one at full breadth.
    rng = random.Random(4242)
    sampled = sum(1 for _ in range(NDRAW) if f"{rng.random():.4f}" in full) / NDRAW
    derived = floor_of(full)
    se = (sampled * (1 - sampled) / NDRAW) ** 0.5
    pos_ok = abs(derived - sampled) < 4 * se
    print(f"\nPOSITIVE CONTROL  derived floor {derived:.4f} vs sampled {sampled:.4f} "
          f"({NDRAW} draws, 4·se = {4*se:.4f}) -> {'PASS' if pos_ok else '⛔ FAIL'}")
    ghost = "0." + "8675" + "309"
    plac_ok = ghost not in full and derived < 1.0
    print(f"PLACEBO           a runtime-assembled decimal is absent and the floor is below 1: "
          f"{plac_ok}")

    # ── THE SWEEP
    print(f"\nBREADTH CURVE   J = recall − floor   ({len(BREADTHS)}×{len(SEEDS)} cells, all reported)")
    print(f"  {'b':>5}" + "".join(f"{f'seed {s}':>22}" for s in SEEDS[:3]) + "   (first 3 seeds)")
    rows, argmax = [], {}
    for s in SEEDS:
        r = random.Random(1000 + s)
        order = list(range(len(per)))
        r.shuffle(order)
        best, bestJ = None, -2.0
        for b in BREADTHS:
            vals = set().union(*[per[i] for i in order[:b]]) if b else set()
            fl = floor_of(vals)
            rec = (sum(1 for d in locatable if d in vals) / len(locatable)) if locatable else 0.0
            J = rec - fl
            rows.append({"seed": s, "b": b, "floor": fl, "recall": rec, "J": J})
            if J > bestJ:
                best, bestJ = b, J
        argmax[s] = (best, bestJ)
    for b in BREADTHS:
        line = f"  {b:>5}"
        for s_ in SEEDS[:3]:
            rr = next(x for x in rows if x["seed"] == s_ and x["b"] == b)
            cell = f"r{rr['recall']:.3f} f{rr['floor']:.3f} J{rr['J']:+.3f}"
            line += f"{cell:>22}"
        print(line)

    # ── NEGATIVE CONTROL at b = 0
    z = [x for x in rows if x["b"] == 0]
    neg_ok = all(x["floor"] == 0.0 and x["recall"] == 0.0 and x["J"] == 0.0 for x in z)
    print(f"\nNEGATIVE CONTROL  at b=0: floor, recall and J all exactly 0: {neg_ok}")
    ctrl_ok = pos_ok and plac_ok and neg_ok

    bs = sorted({argmax[s][0] for s in SEEDS})
    print(f"\nargmax J per seed: " + ", ".join(f"s{s}={argmax[s][0]} (J={argmax[s][1]:+.3f})"
                                               for s in SEEDS))
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the curve certifies nothing"
    elif bs == [BREADTHS[-1]]:
        world = f"A MORE IS ALWAYS BETTER — J peaks at the full scan on every seed; no trade-off"
    elif all(b < BREADTHS[-1] for b in bs):
        Jfull = [x["J"] for x in rows if x["b"] == BREADTHS[-1]]
        world = (f"B AN INTERIOR OPTIMUM — J peaks at b ∈ {bs} on every seed, against "
                 f"J(full) ∈ [{min(Jfull):+.3f}, {max(Jfull):+.3f}]")
    else:
        world = f"UNVERIFIED — the seeds straddle the boundary: argmax ∈ {bs}"
    print(f"\n⭐ {world}")

    out = HERE / "results" / "breadth_curve.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_artifacts=len(per), n_values_full=len(full), n_doc_decimals=len(doc),
        n_locatable=len(locatable), breadths=list(BREADTHS), seeds=list(SEEDS),
        derived_floor_full=derived, sampled_floor_full=sampled, ndraw=NDRAW,
        controls={"positive_derived_matches_sampled": pos_ok, "placebo_ghost_absent": plac_ok,
                  "negative_b0_zero": neg_ok, "all_ok": ctrl_ok},
        argmax={str(s): {"b": argmax[s][0], "J": argmax[s][1]} for s in SEEDS},
        rows=rows, world=world,
        note="recall(full)=1 by construction — the ground truth IS the full scan — so the positive "
             "control tests the derived floor instead, which is the new part of the instrument.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}   cells {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
