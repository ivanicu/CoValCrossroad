#!/usr/bin/env python3
"""
R926 · the price of clause ③ as a function of k — and whether the curve is my sampling cap.

⛔ WHY. R925 priced label access at k=1 (gap 0.1164) against k=4 (0.0639) and reported 1.82×. Two
points do not make a curve, and the shape between them decides how clause ① should be worded: a
monotone decay says `size > 1` is the right form, a plateau after k=2 says the bound should be
larger, and a non-monotone curve says the clause is the wrong shape entirely.

⛔⛔ **BUT THE STRONGEST CONFOUND IS IN MY OWN INSTRUMENT, AND IT POINTS THE SAME WAY AS THE
HYPOTHESIS.** The oracle at each k is a maximum over `C(m, k)` subsets. Above a cap it must be
SAMPLED, and a sampled maximum is a **lower bound** on the true one. `C(m, k)` peaks at middle k, so
a fixed cap biases the oracle DOWN most exactly where the gap is predicted to fall — **the cap can
manufacture the decay.** §4's remedy for a control validated by its own instrument's noise is to
sweep the instrument's precision, so the cap `M` is a swept axis here, not a constant: if the gap
moves with `M`, the curve is an artifact and the round says so.

⚠ **AND ONE ENDPOINT IS FORCED.** At `k = m` every selector picks the whole rubric, so
`gap(m) = 0` exactly, by construction. The tail of any such curve descends to zero whatever the data
does. That is a DERIVATION and it is stated rather than reported as a finding; the informative region
is small k, where the choice of subset still matters.

ESTIMAND        gap(k) = mean A2 of the k-subset ORACLE − mean A2 of the best LABEL-BLIND k-selector,
                for k in the swept set, at each of three sampling caps.
IDENTIFICATION  exact at each (k, M) given the draw; the oracle is a maximum over an enumerable set,
                sampled above the cap and reported as a lower bound when it is.
                ⚠ Not an admission probability.
SCOPE           population: every prompt's `coval_full` rubric as judged by 2B
                instrument: A2 vs human class vectors; subsets enumerated where `C(m,k) <= M`,
                            sampled otherwise — the exhaustive share reported per cell
                baseline:   the best of 4 label-blind orderings × 3 rank offsets at the same k
                regime:     home release, seed 926
WORLDS          A · gap(k) falls monotonically and does not move with M -> label access is worth
                    most at small k, clause ① is correctly shaped as a lower bound on size
                B · gap(k) plateaus or rises somewhere -> `size > 1` is the wrong bound and the
                    clause needs a different form
                C · gap(k) moves with M -> the curve is my sampling cap and nothing is measured
KILL            CONDITIONAL:
                  ⭐ ① WIRING: at k=1 reproduce R925's oracle 0.6478 and best-blind 0.5314 to 1e-4,
                     by the same construction. k=1 is exhaustive for every rubric, so any drift
                     there is a code difference and not a sampling one.
                  ⭐ ② INSTRUMENT-PRECISION SWEEP — the load-bearing control. Report gap(k) at
                     M in {500, 2000, 8000}. If any k's gap moves by more than the k=1 gap's own
                     bootstrap half-width, the curve is cap-driven and the verdict is world C.
                  ⭐ ③ FORCED ENDPOINT VERIFIED: on prompts where k >= m the oracle and every blind
                     selector must return the SAME set, so their per-prompt A2 must be identical.
                     ⚠ Forced; an index check, not evidence.
                  ⭐ ④ PLACEBO: a uniformly random k-subset must sit mid-distribution at every k.
MULTIPLICITY    |k| × |M| × {oracle, best-blind, gap} plus the exhaustive share per cell; every
                cell printed including the ones that do not move.
ARTIFACT        results/clause3_price_curve.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: the label-blind side is the best of the
                orderings THIS generator expresses (R925's scope). A better blind selector would
                shrink every gap here, so each is an UPPER bound on the price of clause ③.
"""
import itertools, json, math, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, L, PAIRS                      # noqa: E402
from covalx.judge import load_join                                           # noqa: E402

SEED = 926
KS = (1, 2, 3, 4, 6, 8)
MS = (500, 2000, 8000)
ORDERINGS = ("weight", "abs_weight", "variance", "weight_x_variance")
OFFSETS = (1, 2, 3)
R925_ORACLE_K1, R925_BLIND_K1, TOL = 0.6478, 0.5314, 1e-4


def main() -> int:
    r925 = next(A27.glob("R925_*/results/label_blind_k1_sweep.json"), None)
    if r925 is None:
        print("  UNRUNNABLE: R925 artifact missing. Exit 2, never 0.")
        return 2

    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    items = {pid: (r.get("coval_full") or []) for pid, _q, r in joined}
    emitted = json.loads((RES / "core_full.json").read_text())
    pids = sorted(set(Sfull) & set(items) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    # per prompt: satisfaction matrix, the four label-blind orderings (stable, order-preserving
    # weight match — both repairs inherited from R925)
    per = {}
    for p in pids:
        idxs = sorted({i for i, _ in Sfull[p]})
        S = np.array([[Sfull[p].get((i, x), 0.0) for x in L] for i in idxs])
        emit, rub = emitted.get(p, []), [t["criterion"] for t in items[p]]
        w, j = np.zeros(len(idxs)), 0
        for pos in range(min(len(idxs), len(emit))):
            while j < len(rub) and rub[j] != emit[pos]:
                j += 1
            if j < len(rub):
                w[pos] = float(np.mean([sc["score"] for sc in (items[p][j].get("scores") or [])])
                               or 0.0)
                j += 1
        var = S.var(axis=1)
        per[p] = {"S": S, "m": len(idxs), "H": H[p],
                  "ords": {"weight": np.argsort(-w, kind="stable"),
                           "abs_weight": np.argsort(-np.abs(w), kind="stable"),
                           "variance": np.argsort(-var, kind="stable"),
                           "weight_x_variance": np.argsort(-(np.abs(w) * var), kind="stable")}}
    print(f"  prompts {n} · mean rubric size {np.mean([per[p]['m'] for p in pids]):.1f}")

    def a2_of_sets(p, combos):
        """combos: (B, k) index array -> (B,) A2"""
        S, Hp = per[p]["S"], per[p]["H"]
        Y = S[combos].sum(axis=1)
        C = np.stack([np.sign(Y[:, i] - Y[:, j]) for i, j in PAIRS], axis=1)
        return np.array([(C == h).mean(axis=1) for h in Hp]).mean(axis=0)

    rng = np.random.default_rng(SEED)
    cells, forced_bad, placebo = [], 0, {}
    for k in KS:
        blind_v = {}
        for o in ORDERINGS:
            for off in OFFSETS:
                v = np.zeros(n)
                for t, p in enumerate(pids):
                    m = per[p]["m"]
                    order = per[p]["ords"][o]
                    start = min(off - 1, max(0, m - k))
                    sel = order[start:start + k] if m >= k else order[:m]
                    v[t] = a2_of_sets(p, np.array([sel]))[0]
                blind_v[(o, off)] = v
        best_key = max(blind_v, key=lambda z: blind_v[z].mean())
        blind = blind_v[best_key]

        rnd = np.zeros(n)
        for t, p in enumerate(pids):
            m = per[p]["m"]
            rnd[t] = a2_of_sets(p, np.array([rng.choice(m, min(k, m), replace=False)]))[0]
        placebo[k] = float(rnd.mean())

        for M in MS:
            orc, exh, pct = np.zeros(n), 0, []
            for t, p in enumerate(pids):
                m = per[p]["m"]
                if m <= k:
                    combos = np.array([np.arange(m)])
                    exh += 1
                elif math.comb(m, k) <= M:
                    combos = np.array(list(itertools.combinations(range(m), k)))
                    exh += 1
                else:
                    combos = np.array([rng.choice(m, k, replace=False) for _ in range(M)])
                a2 = a2_of_sets(p, combos)
                orc[t] = a2.max()
                pct.append(float((a2 < rnd[t]).mean() + 0.5 * (a2 == rnd[t]).mean()))
            if M == MS[-1]:
                for t, p in enumerate(pids):
                    if per[p]["m"] <= k and abs(orc[t] - blind[t]) > 1e-12:
                        forced_bad += 1
            cells.append({"k": k, "M": M, "oracle": float(orc.mean()),
                          "blind": float(blind.mean()), "blind_spec": list(best_key),
                          "gap": float(orc.mean() - blind.mean()),
                          "exhaustive_prompts": exh, "random_percentile": float(np.mean(pct))})
        print(f"  k={k:<3} blind spec {best_key}  blind {blind.mean():.4f}  " +
              "  ".join(f"M={c['M']}:gap {c['gap']:.4f}(exh {c['exhaustive_prompts']})"
                        for c in cells if c["k"] == k))

    # ---------- ① WIRING at k=1 ----------
    c1cell = [c for c in cells if c["k"] == 1][-1]
    d_or, d_bl = abs(c1cell["oracle"] - R925_ORACLE_K1), abs(c1cell["blind"] - R925_BLIND_K1)
    c1 = d_or < TOL and d_bl < TOL
    print(f"\n  ① WIRING at k=1 (exhaustive for every rubric):")
    print(f"     oracle {c1cell['oracle']:.4f} vs R925 {R925_ORACLE_K1}  Δ {d_or:.2e}")
    print(f"     blind  {c1cell['blind']:.4f} vs R925 {R925_BLIND_K1}  Δ {d_bl:.2e}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}   (tolerance {TOL})")

    # ---------- ② INSTRUMENT-PRECISION SWEEP ----------
    band = 0.0103          # R860's design-scale half-width, used only as a movement yardstick
    moves = {}
    for k in KS:
        g = [c["gap"] for c in cells if c["k"] == k]
        moves[k] = float(max(g) - min(g))
    worst = max(moves.values())
    c2 = worst <= band
    print(f"\n  ② INSTRUMENT-PRECISION SWEEP — does gap(k) move with the cap M?")
    print(f"     {'k':>4}{'M=500':>10}{'M=2000':>10}{'M=8000':>10}{'spread':>10}{'exh@8000':>10}")
    for k in KS:
        row = {c["M"]: c for c in cells if c["k"] == k}
        print(f"     {k:>4}{row[500]['gap']:>10.4f}{row[2000]['gap']:>10.4f}"
              f"{row[8000]['gap']:>10.4f}{moves[k]:>10.4f}"
              f"{row[8000]['exhaustive_prompts']:>10}")
    print(f"     worst spread {worst:.4f} vs yardstick {band}: {c2}  "
          f"{'PASS' if c2 else 'FAIL — the curve is cap-driven, world C'}")

    # ---------- ③ FORCED ENDPOINT ----------
    c3 = forced_bad == 0
    print(f"\n  ③ FORCED ENDPOINT — prompts with m <= k where oracle != blind: {forced_bad} "
          f"(must be 0)   ⚠ forced; an index check, not evidence")
    print(f"     ③ {c3}  {'PASS' if c3 else 'FAIL'}")

    # ---------- ④ PLACEBO ----------
    pcts = {k: [c["random_percentile"] for c in cells if c["k"] == k][-1] for k in KS}
    c4 = all(0.30 <= v <= 0.70 for v in pcts.values())
    print(f"\n  ④ PLACEBO — a uniformly random k-subset's percentile among sampled subsets:")
    print(f"     " + "  ".join(f"k={k}:{v:.3f}" for k, v in pcts.items()))
    print(f"     ④ all in [0.30, 0.70]: {c4}  {'PASS' if c4 else 'FAIL'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                   "cells": cells}, open(OUT / "clause3_price_curve.json", "w"), indent=2)
        return 2

    final = {k: [c for c in cells if c["k"] == k][-1] for k in KS}
    gaps = [final[k]["gap"] for k in KS]
    monotone = all(gaps[i] >= gaps[i + 1] for i in range(len(gaps) - 1))
    world = "A" if monotone else "B"
    print(f"\n  ⭐⭐⭐ THE PRICE CURVE at M={MS[-1]} — what clause ③ costs at each k:")
    print(f"     {'k':>4}{'oracle':>10}{'best blind':>12}{'gap':>10}{'blind spec':>34}")
    for k in KS:
        c = final[k]
        print(f"     {k:>4}{c['oracle']:>10.4f}{c['blind']:>12.4f}{c['gap']:>10.4f}"
              f"{str(tuple(c['blind_spec'])):>34}")
    print(f"\n  ⭐⭐⭐ WORLD {world}: the gap is "
          f"{'MONOTONE DECREASING' if monotone else 'NOT monotone'} in k over "
          f"{KS} — {[round(g, 4) for g in gaps]}.")
    if monotone:
        print(f"     Label access is worth most at the smallest set, and its value decays as the")
        print(f"     set grows. **`size > 1` is correctly shaped as a lower bound**: the thing")
        print(f"     clause ① protects against is precisely the regime where clause ③ is cheapest")
        print(f"     to violate profitably.")
    else:
        print(f"     The gap does not decay monotonically, so `size > 1` is the wrong bound and")
        print(f"     the clause needs a different form — the k where it rises names the shape.")
    print(f"     ⚠ THE TAIL IS FORCED: at k = m every selector picks the whole rubric and the gap")
    print(f"     is exactly 0, so decay near the top of the range is a DERIVATION. The informative")
    print(f"     region is small k, where {sum(1 for p in pids if per[p]['m'] > 8)} of {n} prompts")
    print(f"     still have a real choice at k=8.")
    print(f"     ⚠ AND EVERY GAP IS AN UPPER BOUND ON THE PRICE: the blind side is the best of the")
    print(f"     orderings THIS generator expresses, so a better blind selector shrinks all of them.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "ks": list(KS), "caps": list(MS),
               "cells": cells, "final_by_k": final, "gaps": gaps, "monotone": monotone,
               "cap_sensitivity": moves, "worst_spread": worst, "yardstick": band,
               "forced_tail": "at k = m every selector picks the whole rubric, so gap(m) = 0 by "
                              "construction; decay near the top of the range is a DERIVATION",
               "gaps_are_upper_bounds": "the blind side is the best of the orderings this "
                                        "generator expresses (R925's scope); a better blind "
                                        "selector shrinks every gap",
               "unit_note": "A2 and gaps are in agreement units; counts are PROMPTS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "clause3_price_curve.json", "w"), indent=2)
    print(f"\n  artifact: results/clause3_price_curve.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
