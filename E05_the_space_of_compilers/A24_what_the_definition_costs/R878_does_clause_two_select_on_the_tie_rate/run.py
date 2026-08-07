#!/usr/bin/env python3
"""
R878 · does clause ② select on the TIE RATE, or on something invariant to it?

⛔ WHY. R877 measured that the admitted set's single axis co-varies with `human_tie_rate` at
**+0.5662**, and **+0.3700 after partialling out prompt difficulty** — so it is not the difficulty
proxy renamed. That leaves a live alternative reading of clause ②: **it may be rewarding
tie-handling behaviour rather than criterion quality**, and correlation cannot separate those.

⭐ **THE TEST THAT CAN.** Stratify the prompts by tie rate and recompute clause ②'s admitted set
INSIDE each stratum. **A clause whose admitted set changes membership across strata is selecting on
the stratifier.** One whose membership holds is rewarding something invariant to it.

⛔⛔ **AND THE ENTIRE DIFFICULTY IS ONE CONFOUND, NAMED BEFORE THE RUN.** Stratifying cuts n from
968 to ~323, so **admitted sets shrink and membership moves FROM POWER LOSS ALONE** — with no
selection on the stratifier whatsoever. A bare "membership changed" would therefore be uninformative
and would look like a finding. **The reference is RANDOM SPLITS AT MATCHED SIZE**: how far does
membership move when the only thing that changed is which prompts you drew? Every number below is
read against that, not against 1.0.

ESTIMAND        the mean pairwise Jaccard overlap of clause ②'s admitted sets across TIE-RATE
                strata, against the same statistic across RANDOM strata of identical sizes.
IDENTIFICATION  exact; both are recomputations of the same released comparison on subsets of the
                same prompts. The only difference between arms of the comparison is HOW the subset
                was chosen, which is the intervention.
SCOPE           population: 99 scored arms × 968 prompts, split into 3 strata
                instrument: A2 vs every annotator; comparator `genericpool16`; criterion BH q=0.05
                            + CI lower bound > 0 (②'s criterion B, the looser of the two)
                baseline:   random splits at matched sizes, 90 draws
                            ⚠ was 200 at NBOOT=1500; the first run timed out on 600 reference
                            calls. NBOOT dropped 1500 -> 500 and NREF 200 -> 90 **for BOTH arms**,
                            because cheapening only the reference would put the observed value and
                            its null on DIFFERENT instruments. Both numbers are noisier than the
                            first attempt and they remain comparable to each other, which is the
                            only property this round needs.
                regime:     home release, judge J
WORLDS          A · tie-strata overlap ≈ random-split overlap -> membership moves no more than
                    resampling explains; clause ② is NOT selecting on the tie rate, and R877's
                    correlation is a property of the axis rather than of the clause's verdict
                B · tie-strata overlap MUCH LOWER than random -> the admitted set is
                    stratum-specific; clause ② IS selecting on the tie rate, and its verdict is
                    a statement about tie-handling
                C · tie-strata overlap HIGHER than random -> the tie rate is aligned with whatever
                    ② rewards, so stratifying on it concentrates rather than splits the signal
KILL            CONDITIONAL, all required, because a low-power stratum makes everything look
                unstable and that is the failure this design is most exposed to:
                  ⭐ ① POSITIVE: `oracle_k4` must be admitted in EVERY tie stratum. If the ceiling
                     cannot survive the split, the strata are underpowered and no overlap number
                     is readable. This is the arm that decides whether the round can run at all.
                  ⭐ ② NEGATIVE: `random_k4_s0` must be admitted in NO stratum.
                  ⭐ ③ the random-split reference must have non-zero spread across its draws.
                  ④ every stratum must admit at least one arm, else exit 2.
MULTIPLICITY    BH q=0.05 within each stratum over all 99 arms; every stratum's admitted set
                reported whole, survivors and non-survivors.
SEEDS           3 seeds for the random reference; spread reported.
ARTIFACT        results/tie_strata.json
IMPOSSIBLE      cross-release · construct validated · causally identified (the stratification is an
                intervention on the SAMPLE, not on the mechanism that makes an arm score well).
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND, CORE, POS, NEG = "genericpool16", "coval_core", "oracle_k4", "random_k4_s0"
# ⚠ NBOOT REDUCED FOR **BOTH** ARMS, NEVER JUST THE REFERENCE. The first run timed out on
# the 600 reference calls. Cheapening only the reference would put the observed value and
# its null on DIFFERENT instruments — the borrowed-quantity error this project has spent
# a dozen rounds catching. The observed Jaccard is recomputed at the same NBOOT, so the
# comparison stays internal even though both numbers are noisier than the first attempt.
NBOOT, Q, NSTRAT, NREF = 500, 0.05, 3, 90


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
    B = vec(BLIND)
    D = V - B
    print(f"  prompts {n} · arms {len(names)} · tie rate: min {tie.min():.3f} "
          f"median {np.median(tie):.3f} max {tie.max():.3f}")

    def admitted(sel, seed=11):
        """Clause ② admitted set restricted to the prompt subset `sel`."""
        Ds = D[:, sel]
        m = len(sel)
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
        return float(np.mean(vals)), vals

    order = np.argsort(tie)
    strata = [order[i * n // NSTRAT:(i + 1) * n // NSTRAT] for i in range(NSTRAT)]
    sizes = [len(s) for s in strata]
    tie_sets = [admitted(s) for s in strata]
    print(f"\n  TIE strata (by human tie rate), sizes {sizes}:")
    for i, (s, a) in enumerate(zip(strata, tie_sets)):
        print(f"    stratum {i}  tie {tie[s].min():.3f}–{tie[s].max():.3f}  "
              f"admits {int(a.sum()):>3} arm(s)")

    ip, ineg = names.index(POS), names.index(NEG)
    k1 = all(bool(a[ip]) for a in tie_sets)
    k2 = not any(bool(a[ineg]) for a in tie_sets)
    k4 = all(a.sum() > 0 for a in tie_sets)
    print(f"  ① POSITIVE `{POS}` admitted in EVERY tie stratum: {k1}  {'PASS' if k1 else 'FAIL'}")
    print(f"     (if the ceiling cannot survive the split, the strata are underpowered and no")
    print(f"      overlap number is readable — this arm decides whether the round can run)")
    print(f"  ② NEGATIVE `{NEG}` admitted in NO stratum: {k2}  {'PASS' if k2 else 'FAIL'}")
    print(f"  ④ every stratum admits >=1 arm: {k4}  {'PASS' if k4 else 'FAIL'}")

    obs, obs_pairs = jac(tie_sets)
    ref, spreads = [], []
    for sd in (11, 22, 33):
        rg = np.random.default_rng(1000 + sd)
        draws = []
        for _ in range(NREF // 3):
            perm = rg.permutation(n)
            rs = [perm[sum(sizes[:i]):sum(sizes[:i + 1])] for i in range(NSTRAT)]
            draws.append(jac([admitted(s, seed=11) for s in rs])[0])
        ref += draws; spreads.append(float(np.std(draws)))
    ref = np.array(ref)
    k3 = float(ref.std()) > 1e-9
    print(f"  ③ the random-split reference has non-zero spread: sd={ref.std():.4f}  "
          f"{'PASS' if k3 else 'FAIL'}  (per-seed {[round(x,4) for x in spreads]})")
    if not (k1 and k2 and k3 and k4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "tie_jaccard": obs,
                   "sizes": sizes, "k": [k1, k2, k3, k4]},
                  open(OUT / "tie_strata.json", "w"), indent=2)
        return 2

    lo, hi = float(np.percentile(ref, 2.5)), float(np.percentile(ref, 97.5))
    pct = float((ref < obs).mean() * 100)
    print(f"\n  ⭐ mean pairwise Jaccard, TIE strata:    {obs:.4f}   pairs {[round(x,3) for x in obs_pairs]}")
    print(f"  ⭐ mean pairwise Jaccard, RANDOM strata: {ref.mean():.4f}  "
          f"95% [{lo:.4f}, {hi:.4f}]  over {len(ref)} draws")
    print(f"     the tie-strata value sits at the {pct:.1f}th percentile of the random reference")
    world = "B" if obs < lo else ("C" if obs > hi else "A")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "tie-strata overlap is INSIDE the random-split reference — membership moves no more"
             " than resampling explains, so clause ② is NOT selecting on the tie rate and R877's"
             " correlation is a property of the axis rather than of the clause's verdict",
        "B": "tie-strata overlap is BELOW the random reference — the admitted set is"
             " stratum-specific, so clause ② IS selecting on the tie rate and its verdict is a"
             " statement about tie-handling",
        "C": "tie-strata overlap is ABOVE the random reference — the tie rate is aligned with what"
             " ② rewards, so stratifying on it concentrates rather than splits the signal"}[world])
    print(f"     ⚠ Everything is read against the RANDOM reference, never against 1.0. Cutting n")
    print(f"       from {n} to ~{sizes[0]} moves membership by itself, and a bare 'membership")
    print(f"       changed' would have looked like a finding while measuring only power loss.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n, "n_arms": len(names),
               "strata_sizes": sizes, "tie_jaccard": obs, "tie_pairs": obs_pairs,
               "random_jaccard_mean": float(ref.mean()), "random_ci95": [lo, hi],
               "observed_percentile": pct, "n_reference_draws": len(ref),
               "admitted_per_stratum": [[names[i] for i in np.where(a)[0]] for a in tie_sets],
               "controls": {"oracle_all_strata": k1, "random_no_stratum": k2, "ref_spread": k3},
               "confound_named_before_run": "stratifying cuts n and moves membership by itself; "
                                            "the reference is random splits at matched sizes"},
              open(OUT / "tie_strata.json", "w"), indent=2)
    print(f"\n  artifact: results/tie_strata.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
