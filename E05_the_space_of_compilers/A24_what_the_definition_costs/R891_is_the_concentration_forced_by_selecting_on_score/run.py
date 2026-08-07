#!/usr/bin/env python3
"""
R891 · is the admitted set's concentration caused by the DEFINITION, or forced by selecting on SCORE?

⛔ WHY — THE STRONGEST CONFOUND, AND THREE ROUNDS HAVE QUOTED THE NUMBER WITHOUT IT. R876 (25 arms),
R877 (PC1 = 77.1% of variance) and R890 (12 arms, PR 1.8751 vs null 3.2101, percentile 0.000) all
compared the admitted set against a **UNIFORM** random subset of the 99 arms. But the admitted arms
are, by construction, **the high-scoring ones** — clause ② admits exactly those that beat the
comparator resolvably. **If there are few ways to be right and many ways to be wrong, then any
high-scoring subset is concentrated, and the whole finding is an artifact of selecting on score.**

⭐ **THE SHAM THAT SEPARATES THEM IS EXACT AND COSTS NOTHING.** §1: *the same operation minus the
ingredient under study, matched on size and compute.* Draw 12 arms at random **from the 28 that
clause ② already admits**. Every draw is then score-matched by construction — all 28 cleared the same
bar — and the only ingredient removed is **clause ③'s label criterion**. Comparing the real 12
against that null asks what clause ③ contributes; comparing the 28-null against the uniform 99-null
asks what clause ② contributes. **The concentration decomposes between the two clauses.**

⚠ **AND MY OWN CLOSING SENTENCE WAS THE THING THAT NEEDED CHECKING.** R890's `next` proposed asking
"what IS the single shared axis" — **which is R877, already run, on the 29-arm set.** §4's row is
exact: *the `next gradient` line is the highest-risk sentence in a report; it is written last and it
is the only one with no control attached.* The prior-art gate caught it before compute was spent.
What survived as genuinely new is the second half — *is clause ② selecting on that axis rather than
on quality* — which is this round, reframed as a confound rather than an interpretation.

⛔ AND ONE PART IS A DERIVATION, LABELLED: `PR < n` means the correlation matrix has concentrated
eigenvalues, i.e. the arms are not mutually independent. That is forced by the algebra and is **not**
evidence. The measured question is only ever *concentrated RELATIVE TO WHAT*.

ESTIMAND        PR(the 12 admitted) minus PR(size-matched draws from clause ②'s 28), and
                PR(draws from the 28) minus PR(uniform draws from all 99) — the concentration
                attributable to clause ③ and to clause ② respectively.
IDENTIFICATION  exact for each PR. ⚠ The DECOMPOSITION is additive only in the sense that the two
                contrasts are reported separately; it is NOT a variance decomposition and the two
                gaps are not claimed to sum to anything.
SCOPE           population: the 12 (R889's artifact) inside the 28 (R881's admitted flags) inside
                            the 99 — all DERIVED, none globbed
                instrument: PR of the Pearson correlation matrix of per-prompt A2 vectors
                baseline:   TWO nulls — score-matched (from the 28) and uniform (from the 99)
                regime:     home release, judge J, 968 prompts, comparator genericpool16
WORLDS          A · the 12 sit BELOW the score-matched null -> clause ③ concentrates the set beyond
                    what scoring well already forces, and the definition really does select a
                    direction
                B · the 12 sit INSIDE the score-matched null while both sit below the uniform null
                    -> **the concentration is clause ②'s, i.e. it is forced by selecting on score,
                    and R890's percentile 0.000 against a uniform null OVERSTATES what the
                    definition does.** R876/R877/R890's headline would be downgraded, not retracted:
                    the set IS concentrated, but not BY the two-clause definition
                C · the score-matched null is itself as diffuse as the uniform one -> scoring well
                    does not force similarity here, the confound is absent, and the earlier rounds
                    were right for the reason they gave
KILL            CONDITIONAL — nothing is read until the wiring reproduces:
                  ⭐ ① WIRING: the uniform 99-null must reproduce R890's median 3.2101 to within
                     0.05 at the same seed and draw count. If it does not, this round and R890 are
                     not measuring the same thing and no comparison is admissible.
                  ⭐ ② PLACEBO: PR of 5 copies of one arm must be exactly 1.0.
                  ⭐ ③ THE NULL MUST BE ABLE TO GO EITHER WAY: the score-matched null must produce
                     at least one draw above AND one below the observed PR, else the contrast
                     cannot fail and the percentile is theatre.
                  ⭐ ④ SCORE-MATCHING MUST BE REAL: the margin distribution of the 28 must be
                     reported beside the 12's. If the 12 are the top-margin arms within the 28, the
                     "matching" is nominal and that is said out loud rather than assumed away.
MULTIPLICITY    one estimand, two contrasts; both null distributions reported whole.
ARTIFACT        results/score_matched_null.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · cross-model. ⚠ AND: this cannot say WHY scoring well would force
                similarity — only whether it does. ⚠ `the definition describes the instance` stays
                live and is not touched by this round.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

CORE, BLIND = "coval_core", "genericpool16"
NDRAW, SEED = 1000, 890                # SEED matches R890 so the wiring check is exact
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"


def pr(M):
    lam = np.clip(np.linalg.eigvalsh(M), 0, None)
    s = lam.sum()
    return float(s * s / max((lam ** 2).sum(), 1e-300)) if s > 0 else 0.0


def corr_of(V):
    return np.nan_to_num(np.corrcoef(V), nan=0.0)


def art(g, n):
    p = next(A24.glob(f"{g}/results/{n}"), None)
    return json.loads(p.read_text()) if p else None


def main() -> int:
    r889, r881, r890 = (art("R889_*", "two_admitted_sets.json"),
                        art("R881_*", "boundary_distance.json"),
                        art("R890_*", "twelve_diversity.json"))
    if r889 is None or r881 is None or r890 is None:
        print("  UNRUNNABLE: R889/R881/R890 artifact missing. Exit 2, never 0.")
        return 2
    twelve = r889["r888_corrected"]["surviving"]
    margin = {x["arm"]: x["margin"] for x in r881["arms"]}
    twentyeight = [x["arm"] for x in r881["arms"] if x["admitted"]]

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
    have12 = [a for a in twelve if a in idx]
    have28 = [a for a in twentyeight if a in idx]
    k = len(have12)
    print(f"  prompts {len(pids)} · arms available {len(names)} · the 12 -> {k} · the 28 -> "
          f"{len(have28)}")
    if k < 3 or len(have28) <= k:
        print("  UNRUNNABLE: the score-matched pool is not larger than the target. Exit 2.")
        return 2

    obs = pr(corr_of(V[[idx[a] for a in have12]]))
    rng = np.random.default_rng(SEED)
    uni = np.array([pr(corr_of(V[rng.choice(len(names), k, replace=False)]))
                    for _ in range(NDRAW)])
    rng2 = np.random.default_rng(SEED)
    i28 = np.array([idx[a] for a in have28])
    sm = np.array([pr(corr_of(V[rng2.choice(i28, k, replace=False)])) for _ in range(NDRAW)])

    # ---- CONTROLS -----------------------------------------------------------------------------
    c1 = abs(float(np.median(uni)) - r890["pr_null_median"]) < 0.05
    pr_dup = pr(corr_of(np.repeat(V[idx[CORE]][None, :], 5, axis=0)))
    c2 = abs(pr_dup - 1.0) < 1e-6
    c3 = bool((sm > obs).any() and (sm < obs).any())
    m12 = np.array([margin[a] for a in have12 if a in margin])
    m28 = np.array([margin[a] for a in have28 if a in margin])
    nominal = float(np.median(m12)) > float(np.percentile(m28, 75))
    print(f"  ① WIRING   uniform null median {np.median(uni):.4f} vs R890's "
          f"{r890['pr_null_median']:.4f}: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② PLACEBO  PR of 5 identical vectors = {pr_dup:.6f}: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"  ③ the score-matched null goes BOTH ways around the observed "
          f"({int((sm > obs).sum())} above, {int((sm < obs).sum())} below): {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")
    print(f"  ④ MATCHING margin of the 12: median {np.median(m12):+.4f} "
          f"[{m12.min():+.4f}, {m12.max():+.4f}]")
    print(f"              margin of the 28: median {np.median(m28):+.4f} "
          f"[{m28.min():+.4f}, {m28.max():+.4f}]")
    print(f"     the 12 are {'TOP-HEAVY within the 28 — matching is NOMINAL, said out loud'
                             if nominal else 'spread through the 28 — matching is REAL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [c1, c2, c3]},
                  open(OUT / "score_matched_null.json", "w"), indent=2)
        return 2

    p_uni = float((uni < obs).mean())
    p_sm = float((sm < obs).mean())
    print(f"\n  ⭐ observed PR of the {k} = {obs:.4f}")
    print(f"     UNIFORM null (draw {k} of {len(names)}):        median {np.median(uni):.4f}  "
          f"95% CI [{np.percentile(uni, 2.5):.4f}, {np.percentile(uni, 97.5):.4f}]  "
          f"pct {p_uni:.3f}")
    print(f"     SCORE-MATCHED null (draw {k} of the {len(have28)}): median {np.median(sm):.4f}  "
          f"95% CI [{np.percentile(sm, 2.5):.4f}, {np.percentile(sm, 97.5):.4f}]  "
          f"pct {p_sm:.3f}")
    lo, hi = np.percentile(sm, 2.5), np.percentile(sm, 97.5)
    world = "A" if p_sm <= 0.05 else ("C" if abs(np.median(sm) - np.median(uni)) < 0.25 else "B")
    print(f"\n  ⭐⭐ WORLD {world}: " + {
        "A": "the 12 sit BELOW the score-matched null — clause ③ concentrates the set beyond what "
             "scoring well already forces, and the definition really does select a direction",
        "B": "the 12 sit INSIDE the score-matched null while both sit below the uniform one — "
             "**the concentration is clause ②'s, forced by selecting on score.** R890's percentile "
             "0.000 against a UNIFORM null overstates what the two-clause definition does",
        "C": "the score-matched null is as diffuse as the uniform one — scoring well does not force "
             "similarity here, the confound is absent, and the earlier rounds were right for the "
             "reason they gave"}[world])
    print(f"\n  ⭐ THE TWO CONTRASTS, REPORTED APART AND NOT SUMMED:")
    print(f"     clause ② contributes: uniform {np.median(uni):.4f} -> score-matched "
          f"{np.median(sm):.4f}  ({np.median(sm) - np.median(uni):+.4f})")
    print(f"     clause ③ contributes: score-matched {np.median(sm):.4f} -> observed {obs:.4f}  "
          f"({obs - np.median(sm):+.4f})")
    print(f"     ⚠ NOT a variance decomposition. Two contrasts, reported separately; they are not")
    print(f"       claimed to sum to anything.")
    print(f"\n  ⛔ DERIVATION, not evidence: PR < n means the arms are not mutually independent.")
    print(f"     That is forced by the algebra. The measured question is only ever CONCENTRATED")
    print(f"     RELATIVE TO WHAT — which is why this round exists.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_draws": NDRAW, "k": k,
               "pr_observed": obs,
               "uniform_null": {"median": float(np.median(uni)), "pct": p_uni,
                                "ci95": [float(np.percentile(uni, 2.5)),
                                         float(np.percentile(uni, 97.5))]},
               "score_matched_null": {"median": float(np.median(sm)), "pct": p_sm,
                                      "ci95": [float(lo), float(hi)],
                                      "pool": have28, "pool_size": len(have28)},
               "contrast_clause2": float(np.median(sm) - np.median(uni)),
               "contrast_clause3": float(obs - np.median(sm)),
               "not_a_variance_decomposition": True,
               "matching_is_nominal": bool(nominal),
               "margin_12": {"median": float(np.median(m12)), "min": float(m12.min()),
                             "max": float(m12.max())},
               "margin_28": {"median": float(np.median(m28)), "min": float(m28.min()),
                             "max": float(m28.max())},
               "controls": {"wiring_reproduces_R890": c1, "placebo_identical_pr1": c2,
                            "null_goes_both_ways": c3},
               "derivation_not_evidence": "PR < n means arms are not mutually independent — forced "
                                          "by the algebra",
               "prior_art_note": "R890's NEXT proposed 'what IS the axis', which is R877, already "
                                 "run on the 25-arm set. Only the confound half was new.",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "score_matched_null.json", "w"), indent=2)
    print(f"\n  artifact: results/score_matched_null.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
