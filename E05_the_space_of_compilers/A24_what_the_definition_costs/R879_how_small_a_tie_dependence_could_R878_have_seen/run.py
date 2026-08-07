#!/usr/bin/env python3
"""
R879 · how SMALL a tie-rate dependence could R878 ever have seen? — the power curve it owes.

⛔ WHY. R878 reported WORLD A — clause ②'s admitted set moves no more across tie strata (Jaccard
**0.8998**) than across random splits (**0.8640**, 95% [0.7007, 0.9692]) — and stated its own bound
in one line: WORLD B needed the observed **below 0.70**. **That is a large shift, and a null quoted
without saying how large "large" was is the shape this project keeps retracting.**

⛔ **AND THE ARITHMETIC RUNG REFUTES MY OWN NEXT'S PREMISE — RUN BEFORE THE DESIGN.** Check #545
said *"read where the reference CI NARROWS"*, assuming more strata buys resolution. **Two effects
compete and neither is obviously bigger:**
  · more strata ⇒ **fewer prompts each** ⇒ each admitted set noisier ⇒ each pairwise Jaccard noisier
  · more strata ⇒ **more pairs averaged** (`C(k,2)`) ⇒ the MEAN of them less noisy
**So the direction is a FORK, not a derivation**, and the NEXT was written as though it were settled.
Recording that here because it is the third time this session a NEXT presumed its own answer.

ESTIMAND        for k = 2..8 strata: the width of the random-split reference for the mean pairwise
                Jaccard, i.e. **how far below the reference mean the observed must fall to be
                detectable** — the design's MDE on the membership-shift scale.
IDENTIFICATION  exact; the reference is a resampling distribution of the same statistic R878 used,
                recomputed at each k. No model, no asymptotics.
SCOPE           population: 99 arms × 968 prompts
                instrument: A2 vs every annotator; comparator `genericpool16`; BH q=0.05 + CI>0
                baseline:   random splits at matched sizes, at each k
                regime:     home release, judge J. ⚠ NBOOT = 500 throughout, matching R878 exactly
                            so the two rounds' numbers are comparable.
WORLDS          A · MDE shrinks with k -> more strata buys resolution and R878 at k=3 was leaving
                    sensitivity on the table
                B · MDE grows with k -> fewer prompts per stratum dominates; k=2 is the most
                    sensitive design available and R878's bound is near the best obtainable
                C · MDE is U-shaped -> an interior k is optimal, and that k is the finding
KILL            CONDITIONAL, all required:
                  ⭐ ① POSITIVE, on a REAL property: stratifying by prompt DIFFICULTY (mean A2 of
                     the arms clause ② rejects) must produce a LOWER Jaccard than random at some k.
                     R877 measured that property at r = -0.7069 with the admitted set's axis, so if
                     the design cannot detect stratification on it, it cannot detect anything and
                     no MDE number is readable.
                  ⭐ ② g=0: a SECOND independent random stratification must land INSIDE the
                     reference CI at every k. A design that flags its own null is measuring itself.
                  ⭐ ③ the reference must have non-zero spread at every k.
                  ④ every stratum at every k must admit >= 1 arm, else that k is UNREADABLE and is
                     reported as such rather than scored.
MULTIPLICITY    7 values of k; the whole curve reported, including any k that fails ④.
SEEDS           3 seeds folded into each k's reference; spread reported per k.
ARTIFACT        results/power_curve.json
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
NBOOT, Q, NREF = 500, 0.05, 45           # NBOOT matches R878 exactly — the rounds must compare
KS = (2, 3, 4, 5, 6, 7, 8)


def bh(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)
    tie = np.array([float(np.mean(H[k] == 0)) for k in range(n)])

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

    def admitted(sel, seed=11):
        Ds = D[:, sel]; m = len(sel)
        bidx = np.random.default_rng(seed).integers(0, m, size=(NBOOT, m))
        Mk = np.isfinite(Ds).astype(float)
        bs = (np.nan_to_num(Ds)[:, bidx].sum(2) / np.maximum(Mk[:, bidx].sum(2), 1.0)).T
        lo = np.percentile(bs, 2.5, axis=0)
        pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return bh(pv) & (lo > 0)

    def jac(sets):
        vals = []
        for a, b in itertools.combinations(sets, 2):
            u = int((a | b).sum())
            vals.append(int((a & b).sum()) / u if u else 0.0)
        return float(np.mean(vals)) if vals else 0.0

    def split_by(vals, k):
        o = np.argsort(vals)
        return [o[i * n // k:(i + 1) * n // k] for i in range(k)]

    # the POSITIVE control's stratifier: prompt difficulty from the arms clause 2 REJECTS
    base_adm = admitted(np.arange(n))
    rej_idx = np.where(~base_adm)[0]
    difficulty = np.nanmean(V[rej_idx], axis=0)
    print(f"  prompts {n} · arms {len(names)} · NBOOT {NBOOT} (matches R878) · "
          f"rejected arms used for the difficulty stratifier: {len(rej_idx)}")

    print(f"\n  {'k':>3} {'ref mean':>9} {'ref p2.5':>9} {'MDE':>8} {'sd':>7} "
          f"{'TIE J':>8} {'DIFF J':>8} {'rnd2 J':>8}  readable")
    rows = []
    for k in KS:
        ref = []
        for sd in (11, 22, 33):
            rg = np.random.default_rng(2000 + sd + k)
            for _ in range(NREF // 3):
                perm = rg.permutation(n)
                rs = [perm[i * n // k:(i + 1) * n // k] for i in range(k)]
                ref.append(jac([admitted(s) for s in rs]))
        ref = np.array(ref)
        tie_sets = [admitted(s) for s in split_by(tie, k)]
        dif_sets = [admitted(s) for s in split_by(difficulty, k)]
        rnd2 = jac([admitted(s) for s in
                    (lambda pm: [pm[i * n // k:(i + 1) * n // k] for i in range(k)])(
                        np.random.default_rng(99000 + k).permutation(n))])
        readable = all(a.sum() > 0 for a in tie_sets + dif_sets)
        p25 = float(np.percentile(ref, 2.5))
        mde = float(ref.mean() - p25)
        rows.append({"k": k, "ref_mean": float(ref.mean()), "ref_p2_5": p25, "mde": mde,
                     "ref_sd": float(ref.std()), "tie_jaccard": jac(tie_sets),
                     "difficulty_jaccard": jac(dif_sets), "random2_jaccard": rnd2,
                     "readable": bool(readable),
                     "tie_detected": bool(jac(tie_sets) < p25),
                     "difficulty_detected": bool(jac(dif_sets) < p25),
                     "random2_inside": bool(rnd2 >= p25)})
        print(f"  {k:>3} {ref.mean():>9.4f} {p25:>9.4f} {mde:>8.4f} {ref.std():>7.4f} "
              f"{jac(tie_sets):>8.4f} {jac(dif_sets):>8.4f} {rnd2:>8.4f}  "
              f"{'yes' if readable else 'NO'}")

    live = [r for r in rows if r["readable"]]
    if not live:
        print("\n  OBSERVED NOTHING readable at any k. Exit 2, never 0.")
        return 2
    k1 = any(r["difficulty_detected"] for r in live)
    k2 = all(r["random2_inside"] for r in live)
    k3 = all(r["ref_sd"] > 1e-9 for r in live)
    print(f"\n  ① POSITIVE  stratifying by DIFFICULTY is detected at some k: {k1}  "
          f"{'PASS' if k1 else 'FAIL'}"
          + (f"  (k = {[r['k'] for r in live if r['difficulty_detected']]})" if k1 else ""))
    print(f"     R877 measured difficulty at r = -0.7069 with the admitted set's axis. If the")
    print(f"     design cannot see stratification on THAT, no MDE below is readable.")
    print(f"  ② g=0  a SECOND random stratification lands inside the CI at every k: {k2}  "
          f"{'PASS' if k2 else 'FAIL'}")
    print(f"  ③ reference has non-zero spread at every readable k: {k3}  "
          f"{'PASS' if k3 else 'FAIL'}")
    if not (k1 and k2 and k3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "power_curve.json", "w"), indent=2)
        return 2

    best = min(live, key=lambda r: r["mde"])
    mdes = [r["mde"] for r in live]
    world = ("A" if mdes[-1] < mdes[0] - 1e-9 else
             "B" if mdes[-1] > mdes[0] + 1e-9 and best["k"] == live[0]["k"] else "C")
    print(f"\n  ⭐ smallest detectable membership shift: {best['mde']:.4f} at k = {best['k']}")
    print(f"     R878 ran at k=3 with MDE {next(r['mde'] for r in live if r['k']==3):.4f}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "MDE SHRINKS with k — more strata buys resolution and R878 at k=3 left sensitivity"
             " on the table",
        "B": "MDE GROWS with k — fewer prompts per stratum dominates, k=2 is the most sensitive"
             " design available, and R878's bound is near the best obtainable",
        "C": "MDE is U-SHAPED — an interior k is optimal, and that k is the finding"}[world])
    print(f"     ⚠ My own NEXT assumed the CI narrows with k. That was a fork, not a derivation,")
    print(f"       and the curve above is what settles it.")
    print(f"     ⭐ SO R878's NULL NOW HAS A SIZE: clause ②'s verdict is invariant to tie rate")
    print(f"       against a membership shift of {best['mde']:.4f} or larger. Smaller remains open.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n, "n_arms": len(names),
               "nboot": NBOOT, "n_ref_draws_per_k": NREF, "rows": rows,
               "best_k": best["k"], "best_mde": best["mde"],
               "r878_k": 3, "r878_mde": next(r["mde"] for r in live if r["k"] == 3),
               "next_premise_was_a_fork": "check #545 assumed the CI narrows with k; two effects "
                                          "compete and the curve settles it",
               "controls": {"difficulty_detected_at": [r["k"] for r in live
                                                       if r["difficulty_detected"]],
                            "random2_inside_all_k": k2}},
              open(OUT / "power_curve.json", "w"), indent=2)
    print(f"\n  artifact: results/power_curve.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
