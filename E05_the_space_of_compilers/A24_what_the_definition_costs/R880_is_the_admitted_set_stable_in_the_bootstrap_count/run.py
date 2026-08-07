#!/usr/bin/env python3
"""
R880 · is clause ②'s admitted set stable in NBOOT? — the parameter every later round inherited.

⛔ WHY, AND WHY THIS FORM RATHER THAN THE ONE MY NEXT PROPOSED. Check #546 asked whether rounds that
fixed a parameter by convention sat near their worst resolution — a question about my HABITS. Five
consecutive rounds of that kind (R869–R873) is exactly the drift the governing constitution names:
*a retraction ledger is infrastructure, not product*. **The object-relevant form of the same question
is sharper and it is the one run here.**

**R878 used `NBOOT=500`. R865 used `2000`. R875/R876/R877 inherited whichever they were handed.** If
clause ②'s admitted set moves with that number, then **"25 admitted arms" and everything stacked on
it — the 1.6 effective dimensions, the tie-rate axis, the invariance result — is parameter-dependent
and nobody checked.** That is a claim about the DELIVERABLE, not about my habits.

⛔ **THE DERIVATION, STATED SO IT IS NOT MISTAKEN FOR THE FINDING.** Bootstrap Monte-Carlo error
falls as `NBOOT → ∞`, so **the largest NBOOT is the best available estimate** — that is forced by
the arithmetic and is not evidence of anything. **What is measured is HOW FAST the set converges,
and whether 500 was already enough.**

ESTIMAND        the admitted set of clause ② as a function of NBOOT, and its Jaccard against the
                largest-NBOOT set — i.e. how much of "25 arms" is a property of the data and how
                much of the resampling budget.
IDENTIFICATION  exact; every cell is the same released comparison at a different budget. The
                reference is the same statistic at the largest budget, which is best BY DERIVATION.
SCOPE           population: 99 scored arms × 968 prompts (the full set, no stratification)
                instrument: A2 vs every annotator; comparator `genericpool16`; BH q=0.05 + CI>0
                baseline:   the NBOOT = 8000 set
                regime:     home release, judge J
WORLDS          A · the set is stable from a low NBOOT -> 500 was enough, every downstream round is
                    safe, and R878's parameter choice cost nothing here
                B · the set keeps moving up to the largest budget -> "25 arms" is partly a
                    resampling artifact and every count built on it needs restating
                C · the set is stable but a DIFFERENT arm flips at each budget -> the count is
                    stable and the membership is not, which is worse than B because the count is
                    what has been quoted
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE: `oracle_k4` admitted at EVERY budget. If the ceiling flickers, the
                     comparison is too noisy at some budget for any of this to be readable.
                  ⭐ ② NEGATIVE: `random_k4_s0` admitted at NO budget.
                  ⭐ ③ SEED-vs-BUDGET SEPARATION: at the SAME budget, two different bootstrap seeds
                     must agree at least as well as adjacent budgets do. **Without this arm a
                     budget effect and plain Monte-Carlo noise are indistinguishable**, and the
                     round would report the second as the first.
                  ④ every budget must admit >= 1 arm, else exit 2.
MULTIPLICITY    6 budgets × 2 seeds; every cell reported, including the ones that agree.
ARTIFACT        results/nboot_stability.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND, CORE, POS, NEG = "genericpool16", "coval_core", "oracle_k4", "random_k4_s0"
Q = 0.05
BUDGETS = (250, 500, 1000, 2000, 4000, 8000)
SEEDS = (11, 77)


def bh(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def jac(a, b):
    u = int((a | b).sum())
    return int((a & b).sum()) / u if u else 0.0


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return None if np.isfinite(v).sum() < 200 else v

    names, V = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:])
        if v is not None:
            names.append(f.stem[4:]); V.append(v)
    V = np.array(V)
    D = V - vec(BLIND)
    Mk = np.isfinite(D).astype(float)
    Dz = np.nan_to_num(D)
    print(f"  prompts {n} · arms {len(names)}")
    print(f"  ⛔ DERIVATION, not a finding: Monte-Carlo error falls as NBOOT -> inf, so the largest")
    print(f"     budget is the best estimate BY ARITHMETIC. What is measured is the CONVERGENCE.")

    def admitted(nboot, seed):
        bidx = np.random.default_rng(seed).integers(0, n, size=(nboot, n))
        bs = (Dz[:, bidx].sum(2) / np.maximum(Mk[:, bidx].sum(2), 1.0)).T
        lo = np.percentile(bs, 2.5, axis=0)
        pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (nboot + 1))
        return bh(pv) & (lo > 0)

    sets = {(b, s): admitted(b, s) for b in BUDGETS for s in SEEDS}
    ref = sets[(BUDGETS[-1], SEEDS[0])]
    ip, ineg = names.index(POS), names.index(NEG)
    k1 = all(bool(sets[k][ip]) for k in sets)
    k2 = not any(bool(sets[k][ineg]) for k in sets)
    k4 = all(sets[k].sum() > 0 for k in sets)

    print(f"\n  {'NBOOT':>7} {'n(s1)':>6} {'n(s2)':>6} {'J vs ref':>9} {'J seed-vs-seed':>15}"
          f"  {'flips vs ref':>13}")
    rows = []
    for b in BUDGETS:
        a1, a2 = sets[(b, SEEDS[0])], sets[(b, SEEDS[1])]
        jr, js = jac(a1, ref), jac(a1, a2)
        flips = sorted(set(np.where(a1 ^ ref)[0]))
        rows.append({"nboot": b, "n_seed1": int(a1.sum()), "n_seed2": int(a2.sum()),
                     "jaccard_vs_ref": jr, "jaccard_seed_vs_seed": js,
                     "flips_vs_ref": [names[i] for i in flips]})
        print(f"  {b:>7} {int(a1.sum()):>6} {int(a2.sum()):>6} {jr:>9.4f} {js:>15.4f}"
              f"  {len(flips):>13}")

    # KILL ③ — is a BUDGET effect separable from Monte-Carlo noise?
    adj = [jac(sets[(BUDGETS[i], SEEDS[0])], sets[(BUDGETS[i + 1], SEEDS[0])])
           for i in range(len(BUDGETS) - 1)]
    seedj = [r["jaccard_seed_vs_seed"] for r in rows]
    k3 = float(np.mean(seedj)) >= float(np.mean(adj)) - 1e-12
    print(f"\n  ① POSITIVE `{POS}` admitted at EVERY budget: {k1}  {'PASS' if k1 else 'FAIL'}")
    print(f"  ② NEGATIVE `{NEG}` admitted at NO budget: {k2}  {'PASS' if k2 else 'FAIL'}")
    print(f"  ③ SEED-vs-BUDGET  mean seed-agreement {np.mean(seedj):.4f} >= mean adjacent-budget "
          f"agreement {np.mean(adj):.4f}: {k3}  {'PASS' if k3 else 'FAIL'}")
    print(f"     Without this arm a budget effect and plain Monte-Carlo noise are")
    print(f"     indistinguishable, and the round would report the second as the first.")
    print(f"  ④ every budget admits >=1 arm: {k4}  {'PASS' if k4 else 'FAIL'}")
    if not (k1 and k2 and k3 and k4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "nboot_stability.json", "w"), indent=2)
        return 2

    at500 = next(r for r in rows if r["nboot"] == 500)
    counts = [r["n_seed1"] for r in rows]
    stable_from = next((r["nboot"] for r in rows if r["jaccard_vs_ref"] >= 0.95), None)
    count_spread = max(counts) - min(counts)
    memb_moves = any(r["flips_vs_ref"] for r in rows if r["nboot"] >= 1000)
    world = ("A" if (stable_from is not None and stable_from <= 500) else
             "C" if (count_spread <= 1 and memb_moves) else "B")
    print(f"\n  ⭐ admitted counts across budgets: {counts}  (spread {count_spread})")
    print(f"  ⭐ R878/R879 ran at NBOOT=500: {at500['n_seed1']} arms, Jaccard vs the 8000-set "
          f"{at500['jaccard_vs_ref']:.4f}, {len(at500['flips_vs_ref'])} flip(s)")
    if at500["flips_vs_ref"]:
        print(f"     flipped: {at500['flips_vs_ref']}")
    print(f"  ⭐ first budget reaching Jaccard >= 0.95 vs the reference: {stable_from}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the set is stable from a low budget — 500 was enough and every downstream round is"
             " safe on this axis",
        "B": "the set keeps moving up to the largest budget — '25 arms' is partly a resampling"
             " artifact and every count built on it needs restating",
        "C": "the COUNT is stable while MEMBERSHIP moves — worse than B, because the count is what"
             " has been quoted and it hides the churn underneath"}[world])
    print(f"     ⚠ The reference is best BY DERIVATION, not by measurement. This round measures")
    print(f"       convergence speed; it cannot tell you the 8000-set is 'right', only that it is")
    print(f"       the least Monte-Carlo-noisy estimate available here.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n, "n_arms": len(names),
               "budgets": list(BUDGETS), "seeds": list(SEEDS), "rows": rows,
               "counts": counts, "count_spread": count_spread,
               "stable_from_nboot": stable_from,
               "at_500": at500,
               "reference": {"nboot": BUDGETS[-1], "seed": SEEDS[0],
                             "why": "largest budget is best BY DERIVATION (MC error -> 0)"},
               "controls": {"oracle_all": k1, "random_none": k2,
                            "seed_vs_budget_separable": k3,
                            "mean_seed_jaccard": float(np.mean(seedj)),
                            "mean_adjacent_budget_jaccard": float(np.mean(adj))}},
              open(OUT / "nboot_stability.json", "w"), indent=2)
    print(f"\n  artifact: results/nboot_stability.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
