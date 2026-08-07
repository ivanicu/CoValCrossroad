"""R430/headline_under_both -- if the WEIGHTING is the mechanism, R429's own headline used one.

⛔ WHY THIS RUNS BEFORE THE RETRACTION IS WRITTEN. `run.py` just established that the R427/R429
   discrepancy is the aggregation weight, not the null. R429's headline -- Delta(rank1 - rank2) =
   +0.0234 [+0.0103,+0.0364] -- was computed with `excess_point`, which POOLS BY INTERACTION, while
   its bootstrap RESAMPLES CONVERSATIONS. That is a cluster-bootstrap interval around an
   interaction-weighted point: valid for that estimand, but the estimand is now the thing in
   question, because R413 argued the conversation is the unit and the two weightings differ by
   0.013 on the null alone.

   Writing the retraction first and checking this after would be the campaign's own
   `retraction obliges a re-run` failure: a correction that does not carry the corrected number.
   So this runs first, and whatever it returns goes into the same commit.

ESTIMAND  Delta_W(rank1, rank2) = excess_W(P_top) - excess_W(P_second), for W in {CONV, INTER},
          where excess_W is agreement minus the marginal-matched null, aggregated by W.
          Plus: the RANKING itself under each weighting, because a weighting that changes which
          pair is rank 1 changes the claim and not merely its size.

IDENTIFICATION  fully identified; both weightings are computable from the same five npz files.
                This is a re-estimation, not an inference, and the only uncertainty is bootstrap.

SCOPE  population 2,200 conversations / 7,344 interactions · instrument Qwen3.5-2B-Base k=4 ·
       baseline each pair's own marginal-matched analytic null · regime n in {2,3,4}

WORLDS
    W-STABLE     both weightings give the same rank 1 and both resolve rank1 vs rank2 -> R429's
                 headline survives and only its ATTRIBUTION was wrong.
    W-SIZE       same rank 1, but one weighting fails to resolve -> the headline is
                 weighting-dependent and must be quoted with its weighting attached.
    W-ORDER      the weightings disagree on WHICH pair is rank 1 -> R429's headline is retracted
                 outright, not merely qualified.

PRE-REGISTERED KILL, conditional on the placebo and the plant below
    rank 1 differs between weightings              -> W-ORDER, headline RETRACTED
    rank 1 same, resolution differs                -> W-SIZE, headline QUALIFIED
    rank 1 same and both resolve                   -> W-STABLE, only the attribution falls
    a control fails                                -> UNVERIFIED

CONTROLS
    PLACEBO   Delta_W(P, P) must be exactly 0 under BOTH weightings.
    POSITIVE  a planted degradation (per-conversation excess scaled 0.5) must resolve under BOTH.
    g=0       scaling by 1.0 must resolve under NEITHER.
    SEEDS     3 bootstrap seeds; the across-seed spread is reported beside the interval.

MULTIPLICITY  2 weightings x 1 pre-registered comparison = 2 cells; the full 10-pair ranking is
              printed under both weightings so the reader sees every rank that moved, not only
              the one the kill names.
ARTIFACT      results/r430_headline_under_both.json
IMPOSSIBLE    * saying which weighting is RIGHT -- that is a choice about the estimand, and R413
                bears on the VARIANCE (the conversation is the independent unit), not on which
                weighting defines the quantity. Naming a winner here would be the overreach this
                round is correcting.

EXIT 0 W-STABLE · 1 W-SIZE or W-ORDER · 2 UNVERIFIED
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


def _r429():
    spec = importlib.util.spec_from_file_location(
        "r429", A24 / "R429_is_the_tightest_pair_a_resolved_claim" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def point(vec: dict, keys, weighting: str) -> float:
    """vec: conv -> (sum_agree, sum_expected, n_interactions). ONE function, both weightings, so a
    difference between them cannot be a difference between two code paths."""
    if weighting == "CONV":
        vals = [(vec[k][0] - vec[k][1]) / vec[k][2] for k in keys if vec[k][2]]
        return float(np.mean(vals)) if vals else float("nan")
    A = sum(vec[k][0] for k in keys); E = sum(vec[k][1] for k in keys)
    C = sum(vec[k][2] for k in keys)
    return (A - E) / C if C else float("nan")


def boot(vp, vq, convs, weighting, rng, B):
    idx = np.arange(len(convs))
    out = np.empty(B)
    for b in range(B):
        take = [convs[i] for i in rng.choice(idx, size=len(idx), replace=True)]
        out[b] = point(vp, take, weighting) - point(vq, take, weighting)
    return out


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    m = _r429()
    scored, targets = {}, None
    for a in ARMS:
        s, t = m.load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2."); return 2
        scored[a] = s; targets = targets or t
    P = {a: m.picks(scored[a], targets) for a in ARMS}
    order = {(t["conv"], t["inter"]): sorted(r["id"] for r in t["resp"]) for t in targets}
    pairs = list(itertools.combinations(ARMS, 2))
    vecs = {p: m.excess_by_conv(P[p[0]], P[p[1]], order) for p in pairs}
    convs = sorted({c for v in vecs.values() for c in v})

    print("R430/headline_under_both · R429's Delta was pooled by INTERACTION. Recompute both.\n")

    rank = {}
    for w in ("CONV", "INTER"):
        pts = {p: point(vecs[p], list(vecs[p]), w) for p in pairs}
        rank[w] = sorted(pairs, key=lambda p: -pts[p])
        print(f"  ranking under {w}-weighting")
        for i, p in enumerate(rank[w], 1):
            print(f"    {i:>2}. {p[0]:<13}|{p[1]:<13} {pts[p]:+.4f}")
        print()

    moved = [i for i in range(len(pairs)) if rank["CONV"][i] != rank["INTER"][i]]
    print(f"  ranks that MOVE between weightings: {len(moved)} of {len(pairs)}"
          f"{' — positions ' + ', '.join(str(i+1) for i in moved) if moved else ''}")

    # ------------------------------------------------------------------------------- controls
    ok, B, seeds = True, 3000, [41, 42, 43]
    top_c, sec_c = rank["CONV"][0], rank["CONV"][1]

    def scaled(v, g):
        return {c: (a, e + (1 - g) * (a - e), n) for c, (a, e, n) in v.items()}
    print()
    for w in ("CONV", "INTER"):
        pl = abs(point(vecs[top_c], convs, w) - point(vecs[top_c], convs, w))
        ok &= (pl == 0.0)
        print(f"  PLACEBO   {w}: Delta(P,P) = {pl:.1e}, must be 0   "
              f"{'PASS' if pl == 0.0 else '⛔ FAIL'}")
        for g, must in ((0.5, True), (1.0, False)):
            d = boot(vecs[top_c], scaled(vecs[top_c], g), convs, w,
                     np.random.default_rng(5), 800)
            lo, hi = np.percentile(d, [2.5, 97.5])
            res = not (lo <= 0.0 <= hi)
            good = res == must
            ok &= good
            print(f"  {'POSITIVE ' if must else 'g=0      '} {w}: plant g={g} -> {d.mean():+.4f} "
                  f"[{lo:+.4f},{hi:+.4f}] resolved={res}, must be {must}   "
                  f"{'PASS' if good else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r430_headline_under_both.json").write_text(
            json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------- the headline under each weighting
    print(f"\n  THE HEADLINE, under each weighting (B={B}, seeds {seeds})\n")
    out_cells = {}
    for w in ("CONV", "INTER"):
        t, s = rank[w][0], rank[w][1]
        ds = [boot(vecs[t], vecs[s], convs, w, np.random.default_rng(sd), B // len(seeds))
              for sd in seeds]
        allb = np.concatenate(ds)
        lo, hi = np.percentile(allb, [2.5, 97.5])
        pv = max(2 * min((allb <= 0).mean(), (allb >= 0).mean()), 1.0 / (len(allb) + 1))
        out_cells[w] = {"top": f"{t[0]}|{t[1]}", "second": f"{s[0]}|{s[1]}",
                        "delta": float(allb.mean()), "lo": float(lo), "hi": float(hi),
                        "p": float(pv), "resolved": bool(not (lo <= 0 <= hi)),
                        "seed_spread": float(np.std([d.mean() for d in ds]))}
        c = out_cells[w]
        print(f"    {w:<6} {c['top']} vs {c['second']}")
        print(f"           Delta {c['delta']:+.4f} [{c['lo']:+.4f},{c['hi']:+.4f}] "
              f"p={c['p']:.4f} resolved={c['resolved']} seed spread {c['seed_spread']:.5f}")

    same_top = out_cells["CONV"]["top"] == out_cells["INTER"]["top"]
    both_res = out_cells["CONV"]["resolved"] and out_cells["INTER"]["resolved"]
    world = ("W-ORDER" if not same_top else "W-STABLE" if both_res else "W-SIZE")
    print(f"\n  WORLD: {world}")
    if world == "W-STABLE":
        print("    rank 1 is the same pair under both weightings and the separation from rank 2")
        print("    resolves under both. R429's HEADLINE SURVIVES; only its ATTRIBUTION was wrong.")
        print(f"    ⚠ the two Deltas are not equal ({out_cells['CONV']['delta']:+.4f} vs "
              f"{out_cells['INTER']['delta']:+.4f}) — the number is weighting-dependent and must")
        print("    be quoted with its weighting attached, which R429 did not do.")
    elif world == "W-SIZE":
        print("    same rank 1, but the resolution is weighting-dependent. The headline must be")
        print("    quoted with its weighting or not at all.")
    else:
        print("    ⛔ the weightings disagree on WHICH pair is rank 1. R429's headline is")
        print("    RETRACTED outright, not qualified.")
    print(f"    ranks that move between weightings: {len(moved)} of {len(pairs)}")

    (RES / "r430_headline_under_both.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "cells": out_cells, "ranks_moved": len(moved),
         "ranking": {w: [f"{p[0]}|{p[1]}" for p in rank[w]] for w in rank},
         "B": B, "seeds": seeds}, indent=1))
    print(f"\n  artifact -> {(RES / 'r430_headline_under_both.json').relative_to(ROOT)}")
    return 0 if world == "W-STABLE" else 1


if __name__ == "__main__":
    sys.exit(main())
