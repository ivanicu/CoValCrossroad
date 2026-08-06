#!/usr/bin/env python3
"""R774 · is `c(p)` a property of the PROMPT or of the five arms that defined it?

⛔ CHECK #376: R773's REGISTERED RATIO IS CONTAMINATED. `c(p)` IS the committed-pair A2 distance and
   the ratio's DENOMINATOR is the committed-pair satisfaction distance — the same quantity in another
   metric. Measured first: **corr(c, committed distance) = +0.2042**, so `sham/committed` falls in `c`
   by construction. Run as two SEPARATE curves the answer inverts: **corr(c, SHAM distance) =
   −0.0212** — flat across the whole range — while the committed distance rises 1.7×. The ratio's
   decline is entirely its denominator, and R773's "those prompts compress everything" is not what the
   full population shows.

⛔ FORCED, LABELLED:
  D1 a ratio whose denominator tracks the regressor trends by construction. Two curves, never one ratio.
  D2 nothing forces two DISJOINT families' `c` to correlate: each is a within-family difference
     magnitude, and differencing removes what is common (R771's result, used here as a tool). So E3 is
     a genuine measurement.
  D3 attenuation — two noisy estimates correlate at most at the geometric mean of their
     reliabilities, so the cross-family correlation is read against a MEASURED split-half ceiling,
     never against 1.0.

CONTROLS  DISJOINT (exit 2 if the families share an arm) · POSITIVE (a planted prompt-level scale,
          swept) · g=0 · NEGATIVE (200 one-sided permutations) · SHAM (split the COMMITTED five into
          overlapping halves — the ingredient removed is "a different arm set") · PLACEBO (a family
          against itself = 1.0) · CONFOUND (each family's A2 level and `c` distribution printed).
UNIT      prompt · the SCALE, whose ownership is the question.
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
OTH = ["random_k4_s0", "random_k4_s1", "random_k4_s2", "topabs_k4", "topvar_k4"]
NDRAW = 200


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    # ---- CONTROL · DISJOINTNESS, before anything else -------------------------------------------
    if set(COM) & set(OTH):
        print(f"UNRUNNABLE: families share {set(COM) & set(OTH)}. Exit 2, never 0."); return 2
    print(f"  DISJOINT    committed {COM}\n              comparison {OTH}   shared members: 0  PASS")

    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    P = len(pids)
    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]

    def Yv(t):
        S = load_sat(RES / f"sat_{t}.npz")
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c_, x in enumerate(L):
                Y[ai, c_] = sum(S[p].get((i, x), 0.0) for i in ii)
        return Y

    def a2(Y):
        s = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        return np.array([np.mean([(s[a] == h).mean() for h in HC[a]]) for a in range(P)])

    ARMS = COM + OTH + ["gen_sham"]
    Y = {t: Yv(t) for t in ARMS}
    A = {t: a2(Y[t]) for t in ARMS}

    def scale(fam):
        pr = list(itertools.combinations(fam, 2))
        return np.abs(np.array([A[a] - A[b] for a, b in pr])).mean(0)

    def cosd(x, y):
        nu, nw = np.linalg.norm(x, axis=1), np.linalg.norm(y, axis=1)
        ok = (nu > 0) & (nw > 0)
        return np.where(ok, 1 - (x * y).sum(1) / np.maximum(nu * nw, 1e-12), np.nan)

    c = scale(COM); c2 = scale(OTH)
    print(f"  ⚠ CONFOUND  mean A2: committed {np.mean([A[t].mean() for t in COM]):.4f}   "
          f"comparison {np.mean([A[t].mean() for t in OTH]):.4f}")
    print(f"              c quantiles  committed {np.round(np.percentile(c,[25,50,75]),4).tolist()}"
          f"   comparison {np.round(np.percentile(c2,[25,50,75]),4).tolist()}")

    # ---- E1/E2 · two curves, never a ratio -------------------------------------------------------
    cpairs = list(itertools.combinations(COM, 2))
    comm = np.nanmean([cosd(Y[a], Y[b]) for a, b in cpairs], axis=0)
    sham = cosd(Y["coval_core"], Y["gen_sham"])
    ok = ~np.isnan(comm) & ~np.isnan(sham)
    q = np.digitize(c[ok], np.quantile(c[ok], [.25, .5, .75]))
    print(f"\n  ⭐ E1/E2 · TWO CURVES (D1: never their ratio)")
    print(f"  {'quartile':<10}{'n':>6}{'c':>10}{'committed':>12}{'sham':>10}{'ratio':>8}")
    curves = {}
    for l in range(4):
        m = q == l
        cm, sm = float(comm[ok][m].mean()), float(sham[ok][m].mean())
        curves[f"Q{l+1}"] = {"n": int(m.sum()), "c": float(c[ok][m].mean()),
                             "committed": cm, "sham": sm, "ratio": sm / max(cm, 1e-12)}
        print(f"  Q{l+1:<9}{int(m.sum()):>6}{c[ok][m].mean():>10.4f}{cm:>12.4f}{sm:>10.4f}"
              f"{sm/max(cm,1e-12):>8.2f}")
    r_sham = float(np.corrcoef(c[ok], sham[ok])[0, 1])
    r_comm = float(np.corrcoef(c[ok], comm[ok])[0, 1])
    print(f"  corr(c, sham) {r_sham:+.4f}   corr(c, committed) {r_comm:+.4f}   "
          f"-> the ratio's decline is the DENOMINATOR")

    # ---- D3 · the split-half reliability ceiling -------------------------------------------------
    rng = np.random.default_rng(774)

    def splithalf(fam, draws=NDRAW):
        pr = list(itertools.combinations(fam, 2))
        M = np.abs(np.array([A[a] - A[b] for a, b in pr]))
        rs = []
        for _ in range(draws):
            idx = rng.permutation(len(pr))
            h1, h2 = M[idx[:len(pr) // 2]].mean(0), M[idx[len(pr) // 2:]].mean(0)
            if h1.std() > 0 and h2.std() > 0:
                rr = float(np.corrcoef(h1, h2)[0, 1])
                rs.append(2 * rr / (1 + rr) if rr > -1 else 0.0)   # Spearman-Brown
        return float(np.mean(rs))
    rel1, rel2 = splithalf(COM), splithalf(OTH)
    ceiling = math.sqrt(max(rel1, 0) * max(rel2, 0))
    print(f"\n  D3 CEILING  split-half reliability: committed {rel1:.4f}   comparison {rel2:.4f}   "
          f"attenuation ceiling {ceiling:.4f}")

    # ---- E3 · the ontology test ------------------------------------------------------------------
    r_cross = float(np.corrcoef(c, c2)[0, 1])
    print(f"\n  ⭐ E3 · corr(c committed, c' comparison) = {r_cross:+.4f}   "
          f"= {r_cross/max(ceiling,1e-12):.3f} x the ceiling")

    # ---- CONTROLS --------------------------------------------------------------------------------
    plc = float(np.corrcoef(c, c)[0, 1])
    print(f"\n  PLACEBO     a family against ITSELF: {plc:.6f}  "
          f"{'PASS' if abs(plc - 1.0) < 1e-9 else '⛔ FAIL'}")
    negd = [float(np.corrcoef(c, c2[rng.permutation(P)])[0, 1]) for _ in range(NDRAW)]
    nlo, nhi = np.percentile(negd, 2.5), np.percentile(negd, 97.5)
    print(f"  NEGATIVE    {NDRAW} one-sided permutations: {np.mean(negd):+.4f} "
          f"[{nlo:+.4f}, {nhi:+.4f}]  -> excludes 'any two |d| vectors correlate'")
    shf = list(itertools.combinations(COM, 2))
    M = np.abs(np.array([A[a] - A[b] for a, b in shf]))
    ha = M[[i for i, pr_ in enumerate(shf) if "coval_core" in pr_]].mean(0)
    hb = M[[i for i, pr_ in enumerate(shf) if "coval_core" not in pr_]].mean(0)
    r_sham_fam = float(np.corrcoef(ha, hb)[0, 1])
    print(f"  SHAM        the COMMITTED five split into overlapping halves (arms SHARED): "
          f"{r_sham_fam:+.4f}   vs disjoint {r_cross:+.4f}")

    dose = {}
    v = np.array([np.var(A[t]) for t in COM + OTH])
    for w in (0.0, 0.25, 0.5, 1.0):
        s = rng.lognormal(0, w, P) if w > 0 else np.ones(P)
        Asim = {t: rng.normal(0, math.sqrt(max(vv, 1e-12)), P) * s
                for t, vv in zip(COM + OTH, v)}

        def sc(fam):
            pr = list(itertools.combinations(fam, 2))
            return np.abs(np.array([Asim[a] - Asim[b] for a, b in pr])).mean(0)
        dose[w] = float(np.corrcoef(sc(COM), sc(OTH))[0, 1])
        print(f"  POSITIVE    planted prompt-scale width {w:>4.2f} -> corr {dose[w]:+.4f}   "
              f"detected (> {nhi:+.4f}) {dose[w] > nhi}")
    pos = dose[1.0] > nhi
    g0 = not (dose[0.0] > nhi)
    mono = all(dose[a] <= dose[b] + 1e-9 for a, b in zip([0.0, 0.25, 0.5], [0.25, 0.5, 1.0]))
    print(f"              registered band — 0.00 must NOT detect, 1.00 must: {pos and g0}  "
          f"{'PASS' if pos and g0 else '⛔ FAIL'}   monotone: {mono}")

    ctrl = pos and g0 and abs(plc - 1.0) < 1e-9
    rel = r_cross / max(ceiling, 1e-12)
    if not ctrl:
        world = "UNVERIFIED"
    elif ceiling < 0.4:
        world = f"C · UNIDENTIFIED — the split-half ceiling is only {ceiling:.4f}"
    elif rel >= 0.5:
        world = f"A · `c` IS A PROMPT PROPERTY — {rel:.3f} x the ceiling"
    elif rel <= 0.2:
        world = (f"B · `c` IS AN ARM-SET PROPERTY — {r_cross:+.4f} against a ceiling of {ceiling:.4f} "
                 f"({rel:.3f}x). It measures how close THESE FIVE are, not the prompt's separating power")
    else:
        world = f"NO WORLD — {rel:.3f} x the ceiling sits between the registered bands"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/scale_ownership.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "committed": COM, "comparison": OTH,
        "curves": curves, "corr_c_sham": r_sham, "corr_c_committed": r_comm,
        "reliability_committed": rel1, "reliability_comparison": rel2, "ceiling": ceiling,
        "cross_family_corr": r_cross, "relative_to_ceiling": rel,
        "controls": {"disjoint": True, "placebo": plc, "negative_mean": float(np.mean(negd)),
                     "negative_hi": float(nhi), "sham_shared_arms": r_sham_fam,
                     "dose": {str(k): val for k, val in dose.items()},
                     "positive": bool(pos), "g0": bool(g0), "monotone": bool(mono)},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
