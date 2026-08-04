"""R430/rank_stability -- which ranks actually move, and under WHICH axis. Measured, not inferred.

⛔ WHY. R429 wrote *"ranks 5-10 are not quotable"* from a comparison in which BOTH axes changed at
   once: R427 is CONV-weighted with a permutation null, R429 is INTER-weighted with an analytic
   null. `headline_under_both.py` then found that changing the WEIGHTING alone moves only ranks
   9 and 10. Subtracting one from the other gives "so the other four moves come from the null" --
   and that subtraction is an INFERENCE, not a measurement. It is exactly the arithmetic trap: a
   quantity computed from two other numbers and reported as though it had been tested.

   The sentence is about to be written into DEFINITION.md. It gets measured first.

ESTIMAND  For each axis A in {WEIGHTING, NULL} held against the other axis FIXED:
              moves(A) = number of the 10 rank positions that differ between the two settings of A
          and, because the PERM null is stochastic, the DISTRIBUTION of moves(NULL) over draws --
          a single draw's move count is one realisation, not the quantity.

IDENTIFICATION  fully identified. Four settings, all computable; the only stochasticity is the
                permutation draw, and it is enumerated by resampling rather than assumed away.

SCOPE  population 2,200 conversations / 7,344 interactions · instrument the five committed npz ·
       baseline the ANLY null at each weighting · regime 5 arms, 10 pairs, k=4

WORLDS
    W-NULL-NOISE   moves(NULL) is large and VARIES across draws -> the mid-table ordering is
                   permutation-draw noise, and no round may quote it, R427 included.
    W-NULL-REAL    moves(NULL) is large and STABLE across draws -> the two nulls really do order
                   the middle differently, which is a fact about the constructions.
    W-NEITHER      both move counts are small -> the ranking is more stable than R429 said and the
                   "5-10 not quotable" sentence is itself too strong.

PRE-REGISTERED KILL, conditional on the controls below
    median moves(NULL) >= 4 and its IQR >= 2  -> W-NULL-NOISE
    median moves(NULL) >= 4 and its IQR <= 1  -> W-NULL-REAL
    median moves(NULL) <= 2                   -> W-NEITHER, and R429's sentence is DOWNGRADED
    controls fail                             -> UNVERIFIED

CONTROLS
    PLACEBO    the same setting against itself must give 0 moves. For the stochastic PERM setting
               this means two draws with the SAME seed, which must be identical.
    POSITIVE   a synthetic reordering (reverse the excesses) must be detected as 10 moves. A move
               counter never shown to return non-zero cannot make its zero mean anything.
    g=0        an unchanged ranking must give 0 moves.
    SEEDS      >= 30 permutation draws, so the distribution is measured rather than a point.

MULTIPLICITY  2 axes reported, plus the full draw distribution; no selection among them.
ARTIFACT      results/r430_rank_stability.json
IMPOSSIBLE    * saying which ORDERING is correct -- see the parent round; this measures stability,
                not truth.

EXIT 0 a world is named · 2 UNVERIFIED
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ARMS = ["generic", "vacuous", "randblind_s0", "randblind_s1", "randblind_s2"]


def _mods():
    def load(name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        return m
    return (load("r429", A24 / "R429_is_the_tightest_pair_a_resolved_claim" / "run.py"),
            load("r430", HERE / "run.py"))


def ranking(P, order, pairs, weighting, nullkind, rng=None):
    """-> the 10 pairs ordered by excess = agreement - null, under one (weighting, null) setting."""
    out = {}
    for p in pairs:
        common = sorted(set(P[p[0]]) & set(P[p[1]]))
        by_conv: dict = {}
        for k in common:
            by_conv.setdefault(k[0], []).append(
                1.0 if P[p[0]][k][0] == P[p[1]][k][0] else 0.0)
        if weighting == "CONV":
            agree = float(np.mean([np.mean(v) for v in by_conv.values()]))
        else:
            agree = float(np.mean([x for v in by_conv.values() for x in v]))
        nul = R430.null_cell(P[p[0]], P[p[1]], order, weighting, nullkind, rng)
        out[p] = agree - nul
    return sorted(pairs, key=lambda q: -out[q]), out


def moves(a, b):
    return sum(1 for i in range(len(a)) if a[i] != b[i])


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    global R430
    R429, R430 = _mods()
    scored, targets = {}, None
    for a in ARMS:
        s, t = R429.load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2."); return 2
        scored[a] = s; targets = targets or t
    P = {a: R429.picks(scored[a], targets) for a in ARMS}
    order = {(t["conv"], t["inter"]): sorted(r["id"] for r in t["resp"]) for t in targets}
    pairs = list(itertools.combinations(ARMS, 2))

    print("R430/rank_stability · which ranks move, under WHICH axis — measured, not subtracted\n")

    # ------------------------------------------------------------------------------- controls
    ok = True
    rc, _ = ranking(P, order, pairs, "CONV", "ANLY")
    z = moves(rc, rc)
    ok &= (z == 0)
    print(f"  g=0       an unchanged ranking -> {z} moves, must be 0   {'PASS' if z == 0 else '⛔ FAIL'}")
    rev = moves(rc, list(reversed(rc)))
    ok &= (rev == 10)
    print(f"  POSITIVE  a fully reversed ranking -> {rev} moves, must be 10   "
          f"{'PASS' if rev == 10 else '⛔ FAIL — the counter cannot see a reordering'}")
    a1, _ = ranking(P, order, pairs, "CONV", "PERM", np.random.default_rng(77))
    a2, _ = ranking(P, order, pairs, "CONV", "PERM", np.random.default_rng(77))
    same = moves(a1, a2)
    ok &= (same == 0)
    print(f"  PLACEBO   two PERM draws at the SAME seed -> {same} moves, must be 0   "
          f"{'PASS' if same == 0 else '⛔ FAIL — the seed does not determine the draw'}")
    if not ok:
        print("\n  UNVERIFIED — a control is unfit.")
        (RES / "r430_rank_stability.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------- axis 1: WEIGHTING, null fixed
    ri, _ = ranking(P, order, pairs, "INTER", "ANLY")
    mw = moves(rc, ri)
    posw = [i + 1 for i in range(10) if rc[i] != ri[i]]
    print(f"\n  AXIS · WEIGHTING (null fixed at ANLY): {mw} of 10 move — positions {posw}")

    # -------------------------------------------------- axis 2: NULL, weighting fixed, 30 draws
    counts, posn = [], {}
    for s in range(30):
        rp, _ = ranking(P, order, pairs, "CONV", "PERM", np.random.default_rng(1000 + s))
        counts.append(moves(rc, rp))
        for i in range(10):
            if rc[i] != rp[i]:
                posn[i + 1] = posn.get(i + 1, 0) + 1
    counts = np.array(counts)
    med = float(np.median(counts)); iqr = float(np.percentile(counts, 75) - np.percentile(counts, 25))
    print(f"  AXIS · NULL (weighting fixed at CONV), 30 permutation draws:")
    print(f"    moves per draw: median {med:.1f} · IQR {iqr:.1f} · range {counts.min()}-{counts.max()}")
    print(f"    how often each position moves, over 30 draws:")
    for k in sorted(posn):
        print(f"      position {k:>2}: {posn[k]:>2}/30")

    world = ("W-NEITHER" if med <= 2 else
             "W-NULL-NOISE" if iqr >= 2 else
             "W-NULL-REAL" if iqr <= 1 else "UNVERIFIED")
    print(f"\n  WORLD: {world}")
    if world == "W-NULL-NOISE":
        print("    the mid-table ordering is PERMUTATION-DRAW NOISE: a different draw of the same")
        print("    null reorders it. No round may quote it, R427 included.")
    elif world == "W-NULL-REAL":
        print("    the two null constructions order the middle differently and STABLY — a fact")
        print("    about the constructions, not about the draw.")
    else:
        print("    the ranking is more stable than R429 said. Its 'ranks 5-10 are not quotable'")
        print("    was measured with BOTH axes moving at once and is DOWNGRADED: name the axis.")

    (RES / "r430_rank_stability.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "weighting_moves": mw, "weighting_positions": posw,
         "null_moves_median": med, "null_moves_iqr": iqr,
         "null_moves_range": [int(counts.min()), int(counts.max())],
         "null_position_freq": posn, "n_draws": 30,
         "baseline_ranking": [f"{p[0]}|{p[1]}" for p in rc]}, indent=1))
    print(f"\n  artifact -> {(RES / 'r430_rank_stability.json').relative_to(ROOT)}")
    return 0 if world != "UNVERIFIED" else 2


if __name__ == "__main__":
    sys.exit(main())
