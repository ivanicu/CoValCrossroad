#!/usr/bin/env python3
"""R771 · is "which prompts separate cores" a question with an answer?

⛔ CHECK #373, THE ARITHMETIC, BEFORE ANY DESIGN — AND IT REPAIRED THE REGISTERED QUANTITY:
 ① THE RANK IS FORCED. Ten pairwise differences among FIVE arms span a 4-dimensional space. Measured
   rank **4**, eigenvalues [3.791, 2.957, 1.771, 1.481, 0, 0, 0, 0, 0, 0]. So the uniform reference
   is **1/4 = 0.25**, not 1/10, and comparing against 1/10 would manufacture a finding.
 ② MY FIRST ANALYTIC NULL WAS WRONG AND WAS REPLACED BEFORE THE RUN. Predicting the arm-sharing
   correlation from the RAW arm variances gave **+0.9271** against an observed **+0.2687** — the raw
   variance is dominated by prompt difficulty, which the difference removes. The null needs the
   RESIDUAL variances, and they are identifiable: 10 equations `var(d_ab) = v_a + v_b`, 5 unknowns.

⛔ FORCED, LABELLED:
  D1 rank 4 — algebra, not a finding.
  D2 arm-sharing pairs correlate even under pure independence: `v_a/(v_a+v_b)` = 0.5 at equal
     variances. **A positive mean correlation is NOT evidence of a common factor.** The measurement is
     the EXCESS over the per-pair fitted prediction.
  D3 THE SIGN OF THE EXCESS IS THE FORK. Above → a common prompt factor. Below → NEGATIVE dependence,
     i.e. prompts where one arm gains are prompts where another loses — a trade-off structure, a
     different world from noise. Registered before the run so neither outcome can be re-narrated.

CONTROLS  POSITIVE (a common factor injected at swept loading, sized against the statistic the test
          uses — the defect R770 caught in its own control one round ago) · g=0 (loading 0 detects
          nothing) · NEGATIVE (200 independent prompt permutations — excludes "any rank-4 set gives
          this share") · SHAM (200 simulations of INDEPENDENT residuals at the fitted variances —
          same rank, same variances, no shared prompt structure) · PLACEBO (an identical pair must be
          excluded by the machinery, not divided by zero).
UNIT      prompt (968 per vector) · pair (10) · arm (5) · rank (4) — all four reported separately.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
COM = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
NDRAW = 200


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def a2(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        o = np.zeros(P)
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            o[ai] = np.mean([(s == h).mean() for h in HC[ai]])
        return o

    A = {t: a2(t) for t in COM}
    pairs = list(itertools.combinations(COM, 2))
    D = np.array([A[a] - A[b] for a, b in pairs])
    rank = int(np.linalg.matrix_rank(D))
    C = np.corrcoef(D)
    ev = np.linalg.eigvalsh(C)[::-1]
    lead = float(ev[0] / ev.sum())
    print(f"  prompts {P}   pairs {len(pairs)}   arms {len(COM)}   rank {rank} (forced <= 4)")
    print(f"  eigenvalues {np.round(ev, 3).tolist()}")
    print(f"  leading share {lead:.4f}   uniform reference at rank {rank} = {1/rank:.4f}")

    # ---- PLACEBO · an identical pair must be excluded, not divided by zero ---------------------
    dd = A["topw_k4"] - a2("topw_k4_detA")
    plc = float(dd.std(ddof=1)) == 0.0
    print(f"\n  PLACEBO     `topw_k4` vs `_detA`: sd {dd.std(ddof=1):.10f} -> excluded from the "
          f"matrix by construction (a zero-variance vector has no correlation)  "
          f"{'PASS' if plc else '⛔ FAIL'}")

    # ---- E1 · identify the residual variances from the observed var(d) -------------------------
    obs_var = np.array([D[i].var(ddof=1) for i in range(len(pairs))])
    M = np.zeros((len(pairs), len(COM)))
    for i, (a, b) in enumerate(pairs):
        M[i, COM.index(a)] = 1.0; M[i, COM.index(b)] = 1.0
    v, *_ = np.linalg.lstsq(M, obs_var, rcond=None)
    fit_resid = float(np.linalg.norm(M @ v - obs_var) / np.linalg.norm(obs_var))
    ok_fit = bool((v > 0).all())
    print(f"\n  ⭐ E1 · RESIDUAL VARIANCES, identified from 10 equations in 5 unknowns")
    for t, val in zip(COM, v):
        print(f"     v[{t:<12}] = {val:.6f}")
    print(f"     relative fit residual {fit_resid:.4f}   all positive: {ok_fit}  "
          f"{'admissible' if ok_fit else '⛔ MODEL REFUTED — not clipped'}")

    # ---- E2 · predicted vs observed correlations, per pair-of-pairs ----------------------------
    def predict(i, j):
        a, b = pairs[i]; c, e = pairs[j]
        sh = ({a, b} & {c, e})
        if not sh: return 0.0
        s = sh.pop()
        sgn = 1.0 if ((a == s) == (c == s)) else -1.0
        return sgn * v[COM.index(s)] / math.sqrt((v[COM.index(a)] + v[COM.index(b)]) *
                                                 (v[COM.index(c)] + v[COM.index(e)]))

    share_obs, share_pre, disj_obs = [], [], []
    for i, j in itertools.combinations(range(len(pairs)), 2):
        p_ = predict(i, j)
        if p_ == 0.0: disj_obs.append(C[i, j])
        else: share_obs.append(C[i, j]); share_pre.append(p_)
    excess = float(np.mean(share_obs) - np.mean(np.abs(share_pre)) *
                   np.sign(np.mean(share_obs))) if share_obs else float("nan")
    # signed comparison, pair by pair, is the honest form:
    ex_pairwise = float(np.mean([abs(o) - abs(p_) for o, p_ in zip(share_obs, share_pre)]))
    print(f"\n  ⭐ E2 · OBSERVED vs the INDEPENDENCE PREDICTION (per pair, not a 0.5 constant)")
    print(f"     arm-sharing (n={len(share_obs)}): |observed| mean {np.mean(np.abs(share_obs)):.4f}"
          f"   |predicted| mean {np.mean(np.abs(share_pre)):.4f}   "
          f"EXCESS {ex_pairwise:+.4f}")
    print(f"     disjoint    (n={len(disj_obs)}): observed mean {np.mean(disj_obs):+.4f}   "
          f"predicted 0")

    # ---- SHAM · simulate independent residuals at the fitted variances --------------------------
    rng = np.random.default_rng(771)

    def lead_of(R):
        Dv = np.array([R[:, COM.index(a)] - R[:, COM.index(b)] for a, b in pairs])
        e = np.linalg.eigvalsh(np.corrcoef(Dv))[::-1]
        return float(e[0] / e.sum())

    sham = []
    for _ in range(NDRAW):
        R = rng.normal(0, np.sqrt(v)[None, :], (P, len(COM)))
        sham.append(lead_of(R))
    slo, shi = np.percentile(sham, 2.5), np.percentile(sham, 97.5)
    print(f"\n  SHAM        {NDRAW} simulations of INDEPENDENT residuals at the fitted variances: "
          f"leading share {np.mean(sham):.4f} [{slo:.4f}, {shi:.4f}]   vs observed {lead:.4f}")

    # ---- NEGATIVE · permute each vector's prompts independently --------------------------------
    neg = []
    for _ in range(NDRAW):
        Dp = np.array([D[i][rng.permutation(P)] for i in range(len(pairs))])
        e = np.linalg.eigvalsh(np.corrcoef(Dp))[::-1]
        neg.append(float(e[0] / e.sum()))
    print(f"  NEGATIVE    {NDRAW} independent prompt permutations: leading share "
          f"{np.mean(neg):.4f} [{np.percentile(neg,2.5):.4f}, {np.percentile(neg,97.5):.4f}]"
          f"   -> excludes 'any rank-10 set gives this'")

    # ---- POSITIVE · inject a common factor, swept ----------------------------------------------
    # ⛔ THE FIRST PLANT WAS THE WRONG OBJECT, AND THE REASON IS ALGEBRA I SHOULD HAVE DERIVED.
    # A factor loading EQUALLY on every arm — `R_a + lam*sqrt(v_a)*f` — CANCELS in every difference:
    # `d_ab = (R_a - R_b) + lam*(sqrt(v_a) - sqrt(v_b))*f`, which vanishes when the variances match
    # and is tiny otherwise. Measured: the leading share sat at 0.308–0.312 at EVERY loading including
    # 1.0, and was not even monotone. **Differencing removes what is common — that is precisely why
    # R770 used differences to strip prompt difficulty — so a COMMON factor is invisible here BY
    # CONSTRUCTION.** The object the test is meant to detect is a factor with DIFFERENTIAL loadings:
    # "some prompts separate these arms" means the factor pushes arms APART, not together. The plant
    # is rebuilt as differential loadings, which is correcting the plant to be the thing under test,
    # not loosening a criterion.
    print(f"\n  POSITIVE    a DIFFERENTIALLY-loading prompt factor injected at swept loading:")
    dose = {}
    base_R = rng.normal(0, np.sqrt(v)[None, :], (P, len(COM)))
    f = rng.normal(0, 1, P)
    load = np.array([+1.0, +0.5, 0.0, -0.5, -1.0])      # differential, sums to zero
    for lam in (0.0, 0.25, 0.5, 1.0):
        R = base_R + lam * (np.sqrt(v) * load)[None, :] * f[:, None]
        Dv = np.array([R[:, COM.index(a)] - R[:, COM.index(b)] for a, b in pairs])
        ls = lead_of(R)
        Cv = np.corrcoef(Dv)
        sh = [Cv[i, j] for i, j in itertools.combinations(range(len(pairs)), 2)
              if predict(i, j) != 0.0]
        dose[lam] = {"lead": ls, "mean_abs_sharing": float(np.mean(np.abs(sh))),
                     "detected": bool(ls > shi)}
        print(f"     lambda {lam:>4.2f}  leading share {ls:.4f}  |sharing| "
              f"{np.mean(np.abs(sh)):.4f}  detected (> sham 97.5) {ls > shi}")
    print(f"     loadings {load.tolist()} — differential, summing to zero, so the factor SEPARATES "
          f"arms rather than shifting them together")
    pos = dose[1.0]["detected"]
    g0 = not dose[0.0]["detected"]
    mono = all(dose[a]["lead"] <= dose[b]["lead"] + 1e-9
               for a, b in zip([0.0, 0.25, 0.5], [0.25, 0.5, 1.0]))
    print(f"     registered band — 0.00 must NOT detect, 1.00 must: "
          f"{pos and g0}  {'PASS' if pos and g0 else '⛔ FAIL'}   monotone: {mono}")
    print(f"     ⚠ the plant is sized against the SAME statistic the test uses (leading share vs the "
          f"sham interval) — the defect R770 caught in its own control")

    # ⭐ THE DOSE CURVE IS A CALIBRATION, so the observed statistic can be SIZED rather than only
    # compared. Interpolate the observed leading share on the plant's monotone lambda curve.
    xs = sorted(dose); ys = [dose[k]["lead"] for k in xs]
    if ys[0] <= lead <= ys[-1]:
        lam_hat = float(np.interp(lead, ys, xs))
        band = f"between lambda {max([k for k in xs if dose[k]['lead'] <= lead]):.2f} and " \
               f"{min([k for k in xs if dose[k]['lead'] >= lead]):.2f}"
    else:
        lam_hat, band = float("nan"), "outside the swept range"
    print(f"\n  ⭐ CALIBRATION  observed leading share {lead:.4f} interpolates to a differential "
          f"loading of lambda ~ {lam_hat:.2f} x the residual sd  ({band})")
    print(f"     ⚠ this sizes the factor; it does not establish it — the registered kill below is "
          f"what decides, and it is two-conditional")

    ctrl = plc and ok_fit and pos and g0
    if not ctrl:
        world = "UNVERIFIED"
    elif ex_pairwise >= 0.05 and lead > shi:
        world = "A · ONE LATENT PROMPT FACTOR"
    elif ex_pairwise <= -0.05:
        world = (f"C · NEGATIVE DEPENDENCE — observed sharing correlations sit {abs(ex_pairwise):.4f} "
                 f"BELOW the independence prediction; prompts where one arm gains are prompts where "
                 f"another loses")
    elif abs(ex_pairwise) < 0.05 and slo <= lead <= shi:
        world = "B · PAIR-SPECIFIC, NO FACTOR — no stratification could help"
    else:
        world = ("NO WORLD — the two estimands SPLIT: the pairwise excess says B "
                 f"({ex_pairwise:+.4f}, |.| < 0.05) while the spectrum says A "
                 f"({lead:.4f} > sham hi {shi:.4f}). Registered A and B each need BOTH, so neither "
                 "is claimed")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/prompt_factor.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "rank": rank, "eigenvalues": ev.tolist(), "leading_share": lead,
        "uniform_reference": 1 / rank,
        "residual_variances": {t: float(x) for t, x in zip(COM, v)},
        "fit_relative_residual": fit_resid, "fit_all_positive": ok_fit,
        "sharing_obs_mean_abs": float(np.mean(np.abs(share_obs))),
        "sharing_pred_mean_abs": float(np.mean(np.abs(share_pre))),
        "excess_pairwise": ex_pairwise,
        "disjoint_obs_mean": float(np.mean(disj_obs)),
        "sham_mean": float(np.mean(sham)), "sham_lo": float(slo), "sham_hi": float(shi),
        "negative_mean": float(np.mean(neg)),
        "dose": {str(k): val for k, val in dose.items()},
        "controls": {"placebo_zero_variance": plc, "positive": pos, "g0": g0, "monotone": mono},
        "calibrated_lambda": lam_hat, "calibration_band": band,
        "correlation_matrix": C.tolist(), "pairs": [f"{a} vs {b}" for a, b in pairs],
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
