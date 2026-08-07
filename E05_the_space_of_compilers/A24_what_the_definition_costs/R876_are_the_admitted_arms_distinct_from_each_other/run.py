#!/usr/bin/env python3
"""
R876 · are the 25 admitted arms distinct from EACH OTHER, or one cluster plus outliers?

⛔ WHY. R875 established that the two retained clauses admit **25 procedurally distinct arms**, with
the minimum correlation to `coval_core` (+0.5406) sitting BELOW the random negative control's own
(+0.5798). That answers *does the definition reach past its instance*. It does not answer *what it
reaches*: **a definition admitting 25 copies of one alternative is a different object from one
admitting 25 different things**, and both look identical in a min-correlation statistic.

⚠ **AND THE MEASURE MUST BE THRESHOLD-FREE.** R875's verdict line used `rmin < 0.7`, a cutoff I
invented — the fifth commission of that error this session. Clustering the 25 arms would need a
linkage threshold and reproduce it exactly. **The participation ratio of the correlation matrix's
eigenspectrum, `PR = (Σλ)² / Σλ²`, is an effective count of independent directions and takes no
cutoff at all.** PR = 1 for a set of identical vectors; PR = k for k mutually orthogonal ones.

⭐ **AND IT GETS A REFERENCE, WHICH IS WHAT R875's NEXT WAS ABOUT.** An absolute PR says nothing:
all 99 arms score the same 968 prompts against the same human target, so a shared component is
forced and PR is compressed for ANY subset. **The null is size-matched random subsets of the 99**,
plus the random-family arms as a second reference. R875's `0.7` looked like a number rather than a
guess precisely because no round had ever built a reference for a similarity.

ESTIMAND        the participation ratio of the per-prompt score correlation matrix over the arms
                the definition admits, against the PR of size-matched random subsets of all arms.
IDENTIFICATION  exact; PR is a deterministic function of the eigenvalues of a matrix computed from
                released score vectors. The reference is a resampling distribution, not a model.
SCOPE           population: the arms admitted by the two retained clauses under criterion B
                            (BH q=0.05 + CI at comparator `genericpool16`) — DERIVED from the
                            estimand, and with the two `coval_core_*` ALIASES EXCLUDED, because
                            R875 measured them at r > 0.9999 and an alias is the instance again
                instrument: Pearson correlation of per-prompt A2 vectors over shared prompts
                baseline:   PR of 1000 size-matched random subsets of the 99 arms
                regime:     home release, judge J, 968 prompts
WORLDS          A · PR(admitted) is at or below the size-matched null -> the admitted set is ONE
                    cluster; the definition reaches past its instance but only toward a single
                    alternative, and its breadth is an artifact of counting arms rather than kinds
                B · PR(admitted) is above the null -> the admitted arms are more mutually distinct
                    than a random draw of the same size, and the definition admits several KINDS
                C · PR(admitted) sits inside the null's bulk -> the set is neither more nor less
                    diverse than chance, and the honest answer is that this design cannot separate
                    A from B
KILL            CONDITIONAL, all required:
                  ⭐ ① PLACEBO: PR of k identical vectors must be EXACTLY 1.0. A measure that does
                     not collapse duplicates cannot be read as a count of distinct things.
                  ⭐ ② POSITIVE: adding the two known aliases (`coval_core_2bA/2bB`) to a set must
                     NOT raise its PR by more than ~1 — they carry no new direction. Uses the REAL
                     aliases R875 measured, not invented duplicates.
                  ⭐ ③ g=0 / SPREAD: the null must have non-zero spread across its 1000 draws. A
                     degenerate reference cannot locate anything, and this session has already
                     passed one null whose outcome was forced by arithmetic.
                  ④ non-empty admitted set, else exit 2.
MULTIPLICITY    one statistic against one reference distribution; the whole null is reported, not
                just its tail.
SEEDS           3 seeds for the reference; spread reported.
ARTIFACT        results/admitted_diversity.json
IMPOSSIBLE      cross-release · construct validated · causally identified. ⚠ And unchanged from
                R875: nothing here retires `the definition describes the instance`.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

CORE, BLIND = "coval_core", "genericpool16"
NDRAW = 1000
ALIASES = ("coval_core_2bA", "coval_core_2bB")


def pr(M):
    """Participation ratio of a correlation matrix: (sum l)^2 / sum l^2. No threshold."""
    lam = np.linalg.eigvalsh(M)
    lam = np.clip(lam, 0, None)
    s = lam.sum()
    return float(s * s / max((lam ** 2).sum(), 1e-300)) if s > 0 else 0.0


def corr_of(V):
    C = np.corrcoef(V)
    return np.nan_to_num(C, nan=0.0)


def main() -> int:
    r875 = next((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs").glob(
        "R875_*/results/admits_beyond_instance.json"), None)
    if r875 is None:
        print("  UNRUNNABLE: R875's artifact missing. Exit 2, never 0.")
        return 2
    d875 = json.loads(r875.read_text())
    admitted = [r["arm"] for r in d875["rows"]
                if r["admit_B"] and r["r_with_core"] is not None and r["arm"] not in ALIASES]
    print(f"  admitted by clause ② under criterion B, ALIASES EXCLUDED: {len(admitted)} arm(s)")
    print(f"    (R875 measured {ALIASES} at r > 0.9999 — an alias is the instance again)")

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
        return v if np.isfinite(v).sum() >= 200 else None

    names, V = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:])
        if v is not None:
            names.append(f.stem[4:]); V.append(np.nan_to_num(v, nan=np.nanmean(v)))
    V = np.array(V)
    idx = {nm: i for i, nm in enumerate(names)}
    print(f"  prompts {n} · arms available {len(names)}")

    # ---- CONTROLS -----------------------------------------------------------------------------
    dup = np.repeat(V[idx[CORE]][None, :], 5, axis=0)
    pr_dup = pr(corr_of(dup))
    c1 = abs(pr_dup - 1.0) < 1e-6
    base_set = [a for a in admitted if a in idx][:10]
    pr_base = pr(corr_of(V[[idx[a] for a in base_set]]))
    with_al = base_set + [a for a in ALIASES if a in idx]
    pr_al = pr(corr_of(V[[idx[a] for a in with_al]]))
    c2 = (pr_al - pr_base) <= 1.0 + 1e-9
    print(f"  ① PLACEBO  PR of 5 identical vectors = {pr_dup:.6f} (must be 1.0): "
          f"{c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② POSITIVE adding the 2 REAL aliases to a 10-arm set: PR {pr_base:.4f} -> "
          f"{pr_al:.4f} (Δ={pr_al-pr_base:+.4f} must be <= 1): {c2}  {'PASS' if c2 else 'FAIL'}")

    k = len(admitted)
    ok = [a for a in admitted if a in idx]
    if not ok:
        print("\n  OBSERVED NOTHING: no admitted arm has a vector. Exit 2, never 0.")
        return 2
    pr_obs = pr(corr_of(V[[idx[a] for a in ok]]))

    nulls, spreads = [], []
    for seed in (11, 22, 33):
        rng = np.random.default_rng(seed)
        draws = [pr(corr_of(V[rng.choice(len(names), len(ok), replace=False)]))
                 for _ in range(NDRAW // 3)]
        nulls += draws; spreads.append(float(np.std(draws)))
    nulls = np.array(nulls)
    c3 = float(nulls.std()) > 1e-6
    print(f"  ③ g=0/SPREAD  the reference has non-zero spread: sd={nulls.std():.4f}  "
          f"{'PASS' if c3 else 'FAIL'}   (per-seed sd {[round(x,4) for x in spreads]})")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "admitted_diversity.json", "w"), indent=2)
        return 2

    pct = float((nulls < pr_obs).mean() * 100)
    lo, hi = float(np.percentile(nulls, 2.5)), float(np.percentile(nulls, 97.5))
    rand_fam = [nm for nm in names if nm.startswith("random")]
    pr_rand = pr(corr_of(V[[idx[a] for a in rand_fam]])) if len(rand_fam) >= 3 else None
    print(f"\n  ⭐ PR(admitted, n={len(ok)}) = {pr_obs:.4f}")
    print(f"     size-matched null over {len(nulls)} draws: median {np.median(nulls):.4f} · "
          f"95% [{lo:.4f}, {hi:.4f}]")
    print(f"     observed sits at the {pct:.1f}th percentile of the null")
    if pr_rand is not None:
        print(f"     PR(random family, n={len(rand_fam)}) = {pr_rand:.4f}  — a second reference")
    world = "B" if pr_obs > hi else ("A" if pr_obs < lo else "C")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "PR is BELOW the size-matched null — the admitted set is ONE cluster, and its"
             " breadth is an artifact of counting arms rather than kinds",
        "B": "PR is ABOVE the null — the admitted arms are more mutually distinct than a random"
             " draw of the same size, so the definition admits several KINDS",
        "C": "PR sits INSIDE the null's bulk — the admitted set is neither more nor less diverse"
             " than chance, and this design cannot separate one cluster from many kinds"}[world])
    print(f"     ⚠ PR takes no threshold, which is why it was chosen: R875's verdict used a 0.7")
    print(f"       cutoff I invented, and clustering here would have needed the same kind of guess.")
    print(f"     ⚠ Nothing here retires `the definition describes the instance` — unchanged.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_admitted_excl_aliases": len(ok),
               "aliases_excluded": list(ALIASES), "pr_observed": pr_obs,
               "null_median": float(np.median(nulls)), "null_ci95": [lo, hi],
               "observed_percentile": pct, "pr_random_family": pr_rand,
               "n_null_draws": len(nulls), "null_sd": float(nulls.std()),
               "controls": {"pr_of_identical": pr_dup, "pr_alias_delta": pr_al - pr_base},
               "measure": "participation ratio (sum l)^2/sum l^2 — threshold-free by construction",
               "does_not_retire": "the definition describes the instance"},
              open(OUT / "admitted_diversity.json", "w"), indent=2)
    print(f"\n  artifact: results/admitted_diversity.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
