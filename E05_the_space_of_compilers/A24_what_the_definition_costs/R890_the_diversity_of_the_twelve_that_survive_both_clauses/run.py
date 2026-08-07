#!/usr/bin/env python3
"""
R890 · how diverse is the set the TWO-clause definition actually admits — the 12, not the 29?

⛔ WHY. R888/R889 established that the definition admits **12 arms**, not 28: clause ② admits 28 and
clause ③ removes 16 of them for consuming human labels. **Every diversity figure in the headline was
computed on the clause-② set** — `25 procedurally distinct`, `PR = 1.6368` against `3.6` for a random
25 — and is currently marked SUPERSEDED in `DEFINITION.md`. This round recomputes them on the 12,
with R876's estimator unchanged so the two are comparable.

⭐ **AND THERE IS A NAME-LEVEL STORY THAT MUST NOT BE ALLOWED TO STAND AS EVIDENCE.** The 12 read as
3 `coval_core*`, 2 `generic*`, 7 `topw_k*` — *three procedures wearing twelve names*. **That is a
prefix, and a prefix is not a measurement.** R888 was built precisely on the rule that a name is not
evidence about the object, and the same discipline applies to my own suspicion. The alias criterion
is R875's committed one — `r > 0.9999` on per-prompt score vectors — and it decides this, not me.

⚠ **AND THE ESTIMATOR IS THRESHOLD-FREE BY CONSTRUCTION, WHICH IS WHY IT IS REUSED.** `PR = (Σλ)²/Σλ²`
takes no cutoff. R875's `rmin < 0.7` was an invented cutoff — the fifth commission of that error in
this session — and R876 replaced it for exactly this reason. Changing estimators between the 29 and
the 12 would make the comparison a specification difference rather than a population difference.

ESTIMAND        (a) the number of arms among the 12 that are procedurally distinct under R875's
                    committed alias criterion (r > 0.9999);
                (b) the participation ratio of their per-prompt score correlation matrix, against
                    size-matched random subsets of all available arms.
IDENTIFICATION  exact. PR is a deterministic function of eigenvalues of a matrix built from released
                score vectors; the reference is a resampling distribution, not a model.
                ⚠ **PARTIAL for (a) at the boundary**: `r > 0.9999` is a criterion inherited from
                R875, not re-derived here. Pairs near it are reported with their r so a reader can
                see how much the count depends on it.
SCOPE           population: the 12 arms surviving BOTH clauses, read from R889's committed artifact
                            — DERIVED (it IS the definition's extension), never globbed
                instrument: Pearson correlation of per-prompt A2 vectors over shared prompts
                baseline:   PR of NDRAW size-matched random subsets of the available arms
                regime:     home release, judge J, 968 prompts, comparator genericpool16
WORLDS          A · PR(12) at or BELOW the size-matched null -> the definition's extension is ONE
                    cluster, and its apparent breadth is an artifact of counting ARMS rather than
                    KINDS. The `1.6 of 3.6` story survives and gets worse.
                B · PR(12) ABOVE the null -> the 12 are more mutually distinct than a random draw of
                    the same size, and losing 57% of the extension REMOVED redundancy rather than
                    variety — the definition would then be sharper, not narrower.
                C · PR(12) inside the null's bulk -> at n=12 this design cannot separate, and the
                    honest report is the interval, not a verdict.
KILL            CONDITIONAL, controls inherited from R876 because they are already validated there:
                  ⭐ ① PLACEBO: PR of 5 copies of one arm must be exactly 1.0. A PR that does not
                     collapse on identical vectors is not counting directions.
                  ⭐ ② POSITIVE: adding the 2 REAL aliases R875 measured to a base set must raise PR
                     by <= 1.0. Real aliases, not invented duplicates — a control validated on
                     invented cases is validated against imagination.
                  ⭐ ③ the null must be able to EXCEED the observed: at least one random subset with
                     PR above PR(12), else the comparison cannot fail and the percentile is theatre.
                  ④ the population must be READ from R889's artifact, not retyped.
MULTIPLICITY    one estimand, two sub-quantities; the full alias table and the whole null
                distribution reported, not only the survivors.
ARTIFACT        results/twelve_diversity.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · cross-model. ⚠ AND: `the definition describes the instance` stays
                LIVE. Measuring the diversity of what one release admits says nothing about what a
                second release would admit.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

CORE, BLIND = "coval_core", "genericpool16"
NDRAW, SEED = 1000, 890
ALIAS_R = 0.9999                       # R875's committed criterion, inherited not invented
KNOWN_ALIASES = ("coval_core_2bA", "coval_core_2bB")


def pr(M):
    lam = np.clip(np.linalg.eigvalsh(M), 0, None)
    s = lam.sum()
    return float(s * s / max((lam ** 2).sum(), 1e-300)) if s > 0 else 0.0


def corr_of(V):
    return np.nan_to_num(np.corrcoef(V), nan=0.0)


def main() -> int:
    r889 = next((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs").glob(
        "R889_*/results/two_admitted_sets.json"), None)
    if r889 is None:
        print("  UNRUNNABLE: R889's artifact missing. Exit 2, never 0.")
        return 2
    twelve = json.loads(r889.read_text())["r888_corrected"]["surviving"]
    print(f"  ④ population READ from R889's artifact: {len(twelve)} arms surviving BOTH clauses")

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]

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
    have = [a for a in twelve if a in idx]
    print(f"  prompts {len(pids)} · arms available {len(names)} · of the 12, {len(have)} have "
          f"score vectors")
    if len(have) < 3:
        print("  UNRUNNABLE: fewer than 3 of the 12 have vectors. Exit 2, never 0.")
        return 2

    # ---- CONTROLS, inherited from R876 --------------------------------------------------------
    pr_dup = pr(corr_of(np.repeat(V[idx[CORE]][None, :], 5, axis=0)))
    c1 = abs(pr_dup - 1.0) < 1e-6
    base = [a for a in have if a not in KNOWN_ALIASES][:8]
    pr_base = pr(corr_of(V[[idx[a] for a in base]]))
    with_al = base + [a for a in KNOWN_ALIASES if a in idx]
    pr_al = pr(corr_of(V[[idx[a] for a in with_al]]))
    c2 = (pr_al - pr_base) <= 1.0 + 1e-9
    print(f"  ① PLACEBO  PR of 5 identical vectors = {pr_dup:.6f} (must be 1.0): {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")
    print(f"  ② POSITIVE adding the 2 REAL aliases to a {len(base)}-arm set: "
          f"PR {pr_base:.4f} -> {pr_al:.4f}, rise {pr_al - pr_base:+.4f} <= 1.0: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")

    # ---- (a) alias structure, MEASURED, never read off the prefixes ---------------------------
    M = corr_of(V[[idx[a] for a in have]])
    pairs = [(have[i], have[j], float(M[i, j]))
             for i in range(len(have)) for j in range(i + 1, len(have))]
    alias_pairs = sorted([p for p in pairs if p[2] > ALIAS_R], key=lambda x: -x[2])
    near = sorted([p for p in pairs if 0.99 < p[2] <= ALIAS_R], key=lambda x: -x[2])[:6]
    parent = {a: a for a in have}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for a, b, _ in alias_pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    distinct = sorted({find(a) for a in have})

    # ---- (b) PR against a size-matched null ---------------------------------------------------
    pr_obs = pr(M)
    rng = np.random.default_rng(SEED)
    null = np.array([pr(corr_of(V[rng.choice(len(names), len(have), replace=False)]))
                     for _ in range(NDRAW)])
    pct = float((null < pr_obs).mean())
    c3 = bool((null > pr_obs).any())
    print(f"  ③ the null CAN exceed the observed ({int((null > pr_obs).sum())}/{NDRAW} draws): "
          f"{c3}  {'PASS' if c3 else 'FAIL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [c1, c2, c3]},
                  open(OUT / "twelve_diversity.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ (a) ALIAS STRUCTURE among the {len(have)}, at R875's r > {ALIAS_R}:")
    for a, b, r in alias_pairs:
        print(f"     {a:<22} == {b:<22} r = {r:.6f}")
    if not alias_pairs:
        print(f"     none — no pair exceeds the criterion")
    print(f"     -> {len(distinct)} procedurally distinct of {len(have)}")
    print(f"     nearest pairs BELOW the criterion (so the reader can see its grip):")
    for a, b, r in near:
        print(f"       {a:<22} ~  {b:<22} r = {r:.6f}")

    print(f"\n  ⭐ (b) PR of the {len(have)} = {pr_obs:.4f}")
    print(f"     size-matched null over {NDRAW} random {len(have)}-subsets: "
          f"median {np.median(null):.4f}, 95% CI [{np.percentile(null, 2.5):.4f}, "
          f"{np.percentile(null, 97.5):.4f}]")
    print(f"     observed percentile within the null: {pct:.3f}")

    world = "A" if pct <= 0.05 else "B" if pct >= 0.95 else "C"
    print(f"\n  ⭐⭐ WORLD {world}: " + {
        "A": "the definition's extension is ONE cluster — its apparent breadth is an artifact of "
             "counting ARMS rather than KINDS",
        "B": "the 12 are MORE mutually distinct than a random draw of the same size — losing 57% "
             "of the extension removed redundancy, not variety",
        "C": "PR sits inside the null's bulk — at n=%d this design cannot separate, and the "
             "interval is the honest report" % len(have)}[world])
    print(f"\n  ⚠ NOT RETIRED: `the definition describes the instance`. The diversity of what ONE")
    print(f"    release admits says nothing about what a second would admit.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED,
               "population": have, "n_population": len(have),
               "n_procedurally_distinct": len(distinct), "distinct_representatives": distinct,
               "alias_criterion": ALIAS_R, "alias_criterion_source": "R875, inherited not invented",
               "alias_pairs": alias_pairs, "near_misses_below_criterion": near,
               "pr_observed": pr_obs, "pr_null_median": float(np.median(null)),
               "pr_null_ci95": [float(np.percentile(null, 2.5)),
                                float(np.percentile(null, 97.5))],
               "percentile": pct, "n_null_draws": NDRAW,
               "controls": {"placebo_identical_pr1": c1, "positive_alias_rise_le_1": c2,
                            "null_can_exceed": c3},
               "comparable_to": "R876 on the 29-arm clause-2 set: 25 distinct, PR 1.6368 vs ~3.6 "
                                "for a random 25. Same estimator, different population.",
               "unit_note": "counts are ARMS; PR is EFFECTIVE DIMENSIONS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "twelve_diversity.json", "w"), indent=2)
    print(f"\n  artifact: results/twelve_diversity.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
