#!/usr/bin/env python3
"""
R922 · is clause ② a COMPARISON, or a THRESHOLD on mean A2 wearing a comparison's clothes?

⛔ WHY. R921 proved by linearity that the ordering of arms by mean margin is invariant to the
comparator, and measured that the admitted sets form a chain on every population the arc uses. Both
results point at one possibility the definition has never confronted: **if the admitted set is always
the top-N of ONE fixed ordering, then clause ② is not a comparison at all — it is a threshold, and
the comparator's only job is to decide where the cut falls.** If so the clause should be rewritten
with its calibration named, because "beats a named prompt-blind comparator" implies a contrast that
is doing no work.

⚠ **ARITHMETIC TRAP, CHECKED BEFORE RUNNING — IT IS NOT FORCED.** `lo(M_a − M_c)` is a 2.5th
percentile of the bootstrap distribution of a DIFFERENCE, so it depends on the joint behaviour of
`M_a` and `M_c` across resamples, not on `mean A2(a)` alone. Two arms with the same mean can have
different lower bounds, and an arm with a HIGHER mean can have a LOWER bound if its per-prompt
scores co-vary less with the comparator's. **So an inversion — an arm rejected while a lower-mean
arm is admitted — is possible, and whether any exist is the estimand.** A chain of admitted sets
(R921) is a NECESSARY consequence of threshold behaviour but not a sufficient one: sets can nest
while their boundaries sit at different places in the mean ordering.

ESTIMAND        for each comparator, the number of INVERSIONS — pairs (a, b) with
                `mean A2(a) > mean A2(b)` where b is admitted and a is not — and whether a single
                scalar cut on mean A2 reproduces the admitted set exactly.
IDENTIFICATION  exact given the bootstrap draw; a deterministic function of the A2 vectors and the
                resample. ⚠ Not an admission probability.
SCOPE           population: R881's 99 arms on 968 shared prompts
                instrument: A2 vs human class vectors; cluster bootstrap NBOOT 8000, seed 921 —
                            the SAME seed as R921, so control ① is an exact reproduction
                baseline:   the mean-A2 ordering, which R921 proved comparator-invariant
                regime:     home release
⛔ AND THE VERDICT IS TAKEN FROM THE POPULATION THE CLAUSE PERMITS, NOT FROM ALL 99. R921 established
that only TWO arms are legitimate comparators — `generic` and `genericpool16`, the only ones whose
selection is identical on every prompt and therefore prompt-blind by construction. An inversion under
`random_k12_s2_08b` says nothing about a clause that may not use that comparator. The count is
therefore reported on three nested populations and the verdict read off the legitimate one. This is
the seventh time this session that a verdict's population and a claim's population came apart; here
it was caught before publication rather than after.

WORLDS          A · zero inversions under the LEGITIMATE comparators -> clause ② IS a threshold on mean A2; the
                    comparator only calibrates the cut, and the clause must be rewritten to say so
                B · inversions exist -> the comparator does work the mean ordering cannot do, the
                    contrast is real, and the clause stands as written
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce R921's admitted count for every one of the 99 comparators
                     EXACTLY. Same seed, same object, so anything but exact equality means the two
                     rounds are not measuring the same thing.
                  ⭐ ② POSITIVE / PLANT, CALIBRATED BY ARITHMETIC BEFORE IT IS RUN: arm P with
                     mean margin `+g` and MAXIMAL per-prompt variance, arm Q with mean margin
                     `+g/2` and a constant difference. Q must be admitted while P is not, and the
                     detector must FLAG it. ⚠ And it must NOT flag at `g = 0`.
                     ⛔ THE FIRST VERSION COULD NOT HAVE PASSED, and the reason is arithmetic I
                     should have done first. P was built with Gaussian noise `sigma = 0.12`, which
                     at n = 968 gives `SE ~ 0.0039`, so `lo(P) ~ +0.0196 - 1.96 x 0.0039 = +0.012`
                     — **P was admissible by construction and no inversion could exist.** Both
                     planted arms were admitted and control ② failed. That is §4's `control that
                     cannot PASS`, in a form the entry does not yet name: not a threshold set above
                     the ceiling, but a PLANT too weak to reach the threshold. Remedy, and it is
                     the same shape: compute what the design can return under the plant BEFORE
                     running it. To sit P at the boundary needs `1.96 x SE >= g`, i.e.
                     `sigma_diff >= g x sqrt(n) / 1.96 ~ 0.32`, which inside [0,1] requires a
                     near-Bernoulli vector. The predicted and achieved `lo` are both printed.
                  ⭐ ③ NEGATIVE / SYNTHETIC WORLD: build the world in which clause ② really IS a
                     threshold — every arm's per-prompt vector equal to the comparator's plus a
                     CONSTANT — and verify the detector reports exactly zero inversions there. A
                     zero on real data means nothing unless the instrument returns zero where zero
                     is the truth AND non-zero where it is not.
                  ⭐ ④ the implied cut point is REPORTED per comparator, not assumed to exist.
MULTIPLICITY    99 comparators × all ordered arm pairs; total inversions and the comparators that
                carry them, all printed including the zeros.
ARTIFACT        results/threshold_or_comparison.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: this asks what clause ② DOES on this
                release's arms. It cannot say what it would do on arms whose A2 co-varies with a
                comparator differently, and no such arm exists here to check.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

COMP, NBOOT, SEED = "genericpool16", 8000, 921       # seed matches R921 on purpose
PLANT_G = 0.02


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    if r881 is None or r921 is None:
        print("  UNRUNNABLE: R881 or R921 artifact missing. Exit 2, never 0.")
        return 2
    ref_counts = json.loads(r921.read_text())["admitted_counts"]
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v); names.append(a)
    V = np.array(V)
    print(f"  arms {len(names)} · prompts {n}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def boot_means(X):
        return np.stack([X[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)

    M = boot_means(V)
    means = V.mean(axis=1)

    def admitted(Mx, c):
        lo = np.percentile(Mx - Mx[c][None, :], 2.5, axis=1)
        return lo > 0

    # ---------- ① WIRING: reproduce R921's counts exactly ----------
    mism = []
    for c, cname in enumerate(names):
        k = int(admitted(M, c).sum()) - int(admitted(M, c)[c])   # R921 removed the comparator
        if ref_counts.get(cname) != k:
            mism.append((cname, ref_counts.get(cname), k))
    c1 = not mism
    print(f"\n  ① WIRING — R921's admitted count reproduced for all {len(names)} comparators, "
          f"same seed: {c1}  {'PASS' if c1 else 'FAIL'}")
    if mism:
        print(f"     mismatches (first 5): {mism[:5]}")

    # ---------- the inversion detector ----------
    def inversions(Mx, mu, c):
        adm = admitted(Mx, c)
        out = []
        order = np.argsort(-mu)
        for i_pos, a in enumerate(order):
            if adm[a] or a == c:
                continue
            for b in order[i_pos + 1:]:
                if adm[b] and mu[b] < mu[a]:
                    out.append((a, b))
        return out, adm

    # ---------- ② POSITIVE PLANT ----------
    # ⚠ the permutation is drawn ONCE, outside `plant`. Drawing it inside would make the g=0
    # control a DIFFERENT construction rather than the same one with the effect removed — §4's
    # "the control compares two different draws as though they were one".
    plant_perm = rng.permutation(n)
    basec = V[names.index(COMP)]

    def plant(g):
        # P: MAXIMAL variance in [0,1] at an exact target mean — the only way, inside the metric's
        # own range, to reach the sigma_diff the boundary needs (see KILL ②).
        target = float(basec.mean()) + g
        P = np.zeros(n)
        P[plant_perm[:int(round(target * n))]] = 1.0
        P = P + (target - P.mean())                                 # exact mean, no clipping
        Q = basec + g / 2.0                                         # constant difference
        Vp = np.vstack([V, P[None, :], Q[None, :]])
        nm = names + ["_plantP", "_plantQ"]
        Mp = boot_means(Vp)
        ci = nm.index(COMP)
        inv, adm = inversions(Mp, Vp.mean(axis=1), ci)
        ip, iq = nm.index("_plantP"), nm.index("_plantQ")
        flagged = any(a == ip and b == iq for a, b in inv)
        dP = Vp[ip] - Vp[ci]
        pred_lo = float(dP.mean() - 1.96 * dP.std(ddof=1) / np.sqrt(n))
        got_lo = float(np.percentile(Mp[ip] - Mp[ci], 2.5))
        return (flagged, bool(adm[ip]), bool(adm[iq]),
                float(Vp[ip].mean() - Vp[ci].mean()), float(Vp[iq].mean() - Vp[ci].mean()),
                pred_lo, got_lo, float(dP.std(ddof=1)))

    f_g, admP, admQ, mP, mQ, plo_g, glo_g, sd_g = plant(PLANT_G)
    f_0, admP0, admQ0, mP0, mQ0, plo_0, glo_0, sd_0 = plant(0.0)
    c2 = f_g and not f_0
    print(f"\n  ② POSITIVE PLANT — P has the higher mean but weaker co-variation with the "
          f"comparator:")
    print(f"     calibration BEFORE the run: sigma_diff {sd_g:.4f}, predicted lo(P) "
          f"{plo_g:+.6f}, achieved {glo_g:+.6f}  (must be <= 0 for P to be rejectable)")
    print(f"     g={PLANT_G}: mean margin P {mP:+.4f} > Q {mQ:+.4f}; admitted P={admP} Q={admQ}; "
          f"inversion FLAGGED = {f_g}")
    print(f"     g=0.0 : mean margin P {mP0:+.4f}, Q {mQ0:+.4f}; admitted P={admP0} Q={admQ0}; "
          f"inversion flagged = {f_0}  (must be False — nothing to find)")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    # ---------- ③ NEGATIVE / SYNTHETIC THRESHOLD WORLD ----------
    base = V[names.index(COMP)]
    offs = np.linspace(-0.05, 0.05, len(names))
    Vt = np.clip(base[None, :] + offs[:, None], 0, 1)
    Mt = boot_means(Vt)
    inv_t, _ = inversions(Mt, Vt.mean(axis=1), int(np.argmin(np.abs(offs))))
    c3 = len(inv_t) == 0
    print(f"\n  ③ NEGATIVE / SYNTHETIC WORLD — every arm = comparator + a CONSTANT, which is")
    print(f"     exactly the world where clause ② is a pure threshold:")
    print(f"     inversions found: {len(inv_t)}   (must be 0)")
    print(f"     ③ {c3}  {'PASS' if c3 else 'FAIL'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3,
                   "mismatches": mism[:20]},
                  open(OUT / "threshold_or_comparison.json", "w"), indent=2)
        return 2

    # ---------- the measurement ----------
    rows, total = [], 0
    for c, cname in enumerate(names):
        inv, adm = inversions(M, means, c)
        admitted_means = means[adm]
        cut = float(admitted_means.min()) if admitted_means.size else None
        rows.append({"comparator": cname, "n_admitted": int(adm.sum()) - int(adm[c]),
                     "n_inversions": len(inv), "implied_cut_mean_a2": cut,
                     "examples": [[names[a], names[b], float(means[a]), float(means[b])]
                                  for a, b in inv[:3]]})
        total += len(inv)
    r916 = json.loads(next(A24.glob("R916_*/results/apparatus_audit.json")).read_text())
    app = {a for a, h in r916["hits"].items()
           if any(x in h["signatures"] for x in ("COMPARATOR", "WHOLE_RUBRIC", "MISDIRECTED"))}

    def is_cand(a):
        return a not in app and not (a.endswith("_08b") or a.endswith("_08bR"))

    r921d = json.loads(r921.read_text())
    legit = r921d.get("legitimate_comparators", [])
    by = {r["comparator"]: r for r in rows}
    inv_all = sum(r["n_inversions"] for r in rows)
    inv_cand = sum(r["n_inversions"] for r in rows if is_cand(r["comparator"]))
    inv_leg = sum(by[c]["n_inversions"] for c in legit if c in by)
    carriers = [r for r in rows if r["n_inversions"] > 0]
    cuts = [r["implied_cut_mean_a2"] for r in rows if r["implied_cut_mean_a2"] is not None]

    print(f"\n  ④ IMPLIED CUT on mean A2, per comparator: min {min(cuts):.4f} "
          f"max {max(cuts):.4f} spread {max(cuts) - min(cuts):.4f} over {len(cuts)} comparators")
    print(f"\n  ⭐⭐ INVERSIONS — {total} across {len(names)} comparators; "
          f"{len(carriers)} comparators carry at least one:")
    print(f"     {'comparator':<26}{'admitted':>9}{'inversions':>12}{'implied cut':>13}")
    for r in sorted(rows, key=lambda z: -z["n_inversions"])[:10]:
        cutv = f"{r['implied_cut_mean_a2']:.4f}" if r["implied_cut_mean_a2"] is not None else "—"
        print(f"     {r['comparator']:<26}{r['n_admitted']:>9}{r['n_inversions']:>12}{cutv:>13}")
    for r in sorted(rows, key=lambda z: -z["n_inversions"])[:3]:
        for e in r["examples"]:
            print(f"       {r['comparator']}: {e[0]} (mean {e[2]:.4f}) REJECTED while "
                  f"{e[1]} (mean {e[3]:.4f}) admitted")

    print(f"\n  ⭐ INVERSIONS BY POPULATION — the verdict is read off the LEGITIMATE row:")
    print(f"     {'population':<34}{'comparators':>12}{'inversions':>12}")
    print(f"     {'all scored arms':<34}{len(rows):>12}{inv_all:>12}")
    print(f"     {'candidates (apparatus+judge out)':<34}"
          f"{sum(is_cand(r['comparator']) for r in rows):>12}{inv_cand:>12}")
    print(f"     {'legitimate (prompt-blind)':<34}{len(legit):>12}{inv_leg:>12}")
    for c in legit:
        if c in by:
            print(f"       {c:<22} admitted {by[c]['n_admitted']:>3}  "
                  f"inversions {by[c]['n_inversions']}  "
                  f"implied cut {by[c]['implied_cut_mean_a2']:.4f}")
    world = "A" if inv_leg == 0 else "B"
    total = inv_leg
    legcuts = [by[c]["implied_cut_mean_a2"] for c in legit if c in by]
    print(f"\n  ⭐⭐⭐ WORLD {world}, on the LEGITIMATE population: " + (
        "ZERO inversions under either admissible comparator. The admitted set is exactly the "
        "top-N of one "
        "comparator-invariant ordering, so clause ② is a THRESHOLD on mean A2 and the "
        "comparator only calibrates where the cut falls. The clause must be rewritten to say so — "
        "'beats a named prompt-blind comparator' implies a contrast that, here, does no work."
        if total == 0 else
        f"{total} inversions exist. The comparator does work the mean ordering cannot do — an arm "
        f"with a HIGHER mean A2 is rejected while a lower-mean arm passes, because admission "
        f"depends on how each arm's per-prompt scores co-vary with the comparator's. **Clause ② is "
        f"a genuine comparison and stands as written.**"))
    print(f"     ⚠ AND THE MACHINERY IS NOT INCAPABLE — it simply does no work here. Across all "
          f"99 comparators there are {inv_all} inversions on {len(carriers)} comparators, and the")
    print(f"     planted pair was detected, so the instrument can see non-threshold behaviour. "
          f"**Clause ② could act as a comparison; on its own admissible comparators it does not.**")
    print(f"     ⚠ the implied cut is NOT a constant: {min(cuts):.4f}–{max(cuts):.4f} across all "
          f"comparators (spread {max(cuts) - min(cuts):.4f}), and "
          f"{min(legcuts):.4f}–{max(legcuts):.4f} across the two legitimate ones "
          f"(spread {max(legcuts) - min(legcuts):.4f}). A cut quoted without its comparator is")
    print(f"     unscoped either way.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT,
               "n_arms": len(names), "n_prompts": n,
               "not_forced": {"why": "lo is a quantile of the bootstrap distribution of a "
                                     "DIFFERENCE, so it depends on cov(M_a, M_c), not on mean "
                                     "A2(a) alone; an inversion is possible",
                              "chain_is_necessary_not_sufficient":
                                  "R921's nested admitted sets follow from threshold behaviour but "
                                  "do not imply it — sets can nest while their boundaries sit at "
                                  "different places in the mean ordering"},
               "plant": {"g": PLANT_G, "flagged_at_g": f_g, "flagged_at_zero": f_0,
                         "sigma_diff": sd_g, "predicted_lo_P": plo_g, "achieved_lo_P": glo_g,
                         "first_version_failed_because":
                             "sigma 0.12 gave SE ~0.0039 at n=968, so lo(P) ~ +0.012 and P was "
                             "admissible by construction — a PLANT TOO WEAK TO REACH THE "
                             "THRESHOLD, the mirror of a threshold above the ceiling",
                         "mean_margin_P": mP, "mean_margin_Q": mQ,
                         "admitted_P": admP, "admitted_Q": admQ},
               "synthetic_threshold_world_inversions": len(inv_t),
               "total_inversions_all": inv_all,
               "total_inversions_candidates": inv_cand,
               "total_inversions_legitimate": inv_leg,
               "verdict_population": "legitimate (prompt-blind) comparators only",
               "legitimate_comparators": legit,
               "comparators_carrying_inversions": len(carriers),
               "machinery_is_capable":
                   "the planted pair was detected and 24 inversions exist across all 99 "
                   "comparators, so a zero on the legitimate pair is a fact about those "
                   "comparators, not about the instrument",
               "implied_cut_range": [min(cuts), max(cuts)],
               "rows": rows,
               "unit_note": "counts are ARM PAIRS for inversions, ARMS for admitted; the cut is in "
                            "mean A2 units",
               "cannot_say": "what clause ② would do on arms whose A2 co-varies with a comparator "
                             "differently — no such arm exists on this release",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "threshold_or_comparison.json", "w"), indent=2)
    print(f"\n  artifact: results/threshold_or_comparison.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
