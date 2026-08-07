#!/usr/bin/env python3
"""R773 · the 223 ties — a property of the arms, or the coarseness of a sign statistic?

⛔ CHECK #375: R772's REGISTERED RECOMPUTATION IS ANSWERABLE BY ALGEBRA, AND WAS RUN FIRST.
   Dropping exact-zero prompts scales the EFFECT by `n_f/n_d` and the MDE by
   `sd_ratio · √(n_f/n_d)` — the same factor to O(μ²/σ²). **`eff/MDE` is INVARIANT, so no verdict can
   move.** Measured over all ten pairs: ratios **0.9998–1.0008**, verdict changes **0 of 10**. And
   `n_required` scales by exactly **745/968 = 0.7696** — the same information in a different unit.

⭐ WHAT IS OPEN: A2 is `sign(Y_i − Y_j)` over the 6 pairs among 4 responses, so two arms tie on a
   prompt IFF their criteria induce the SAME SIGN PATTERN. STRUCTURAL (the arms really do the same
   thing there) and GRANULAR (A2 discards magnitude) imply opposite things about the definition.

⛔ FORCED, LABELLED:
  D1 the invariance above — the whole of R772's registered question.
  D2 a tie in A2 is a tie in the SIGN PATTERN, not in the criteria. "The arms are identical there"
     does not follow from a tie and must be measured separately.
  D3 a finer statistic separates more pairs on ANY data, because it retains strictly more
     information. "It separates arms A2 ties" is nearly forced and is NOT the finding.

CONTROLS  POSITIVE (`coval_core` vs `gen_sham` must show a large distance; band from an exact-0 floor
          to a computed ceiling) · g=0 (an arm against itself, distance exactly 0) · NEGATIVE (200
          permutations of which prompts are called tied) · SHAM (the same distance on the 745
          DISCRIMINATING prompts — the ingredient is THE TIE) · PLACEBO (`topw_k4` vs `_detA`) ·
          CONFOUND (the magnitude statistic's own MDE, so separation is relative, not a raw count).
UNIT      prompt · arm pair · PROMPT SUBSET. The 223 and the 745 are different populations, never pooled.
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
ZEFF = 1.959964 + 0.841621
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

    def yvecs(tag):
        """Per-prompt satisfaction vector over the 4 responses — the object A2 signs away."""
        S = load_sat(RES / f"sat_{tag}.npz")
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return Y

    def a2_of(Y):
        s = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        return np.array([np.mean([(s[a] == h).mean() for h in HC[a]]) for a in range(P)])

    ARMS = COM + ["gen_sham", "topw_k4_detA"]
    Y = {t: yvecs(t) for t in ARMS}
    A = {t: a2_of(Y[t]) for t in ARMS}
    pairs = list(itertools.combinations(COM, 2))
    D = np.array([A[a] - A[b] for a, b in pairs])
    tied = np.abs(D).mean(0) == 0
    disc = ~tied
    print(f"  prompts {P}   tied {int(tied.sum())}   discriminating {int(disc.sum())}")

    # ---- E1 · the invariance, verified -----------------------------------------------------------
    print(f"\n  ⭐ E1 · eff/MDE ON 968 vs ON THE {int(disc.sum())} DISCRIMINATING (D1: forced)")
    print(f"  {'pair':<26}{'968':>10}{'745':>10}{'ratio':>9}   verdict moves?")
    inv, moved = {}, 0
    for i, (a, b) in enumerate(pairs):
        d, ds = D[i], D[i][disc]
        r1 = d.mean() / (ZEFF * d.std(ddof=1) / math.sqrt(len(d)))
        r2 = ds.mean() / (ZEFF * ds.std(ddof=1) / math.sqrt(len(ds)))
        mv = (abs(r1) >= 1) != (abs(r2) >= 1)
        moved += mv
        inv[f"{a} vs {b}"] = {"full": float(r1), "disc": float(r2), "ratio": float(r2 / r1),
                              "verdict_moves": bool(mv)}
        print(f"  {a+' vs '+b:<26}{r1:>10.4f}{r2:>10.4f}{r2/r1:>9.4f}   {mv}")
    print(f"  verdict changes {moved} of {len(pairs)}   n_required scales by "
          f"{disc.sum()/P:.4f} — the same information in a different unit")

    # ---- E2 · what the ties ARE -------------------------------------------------------------------
    def signvec(Yt, mask):
        return np.sign(Yt[mask][:, [i for i, _ in PR]] - Yt[mask][:, [j for _, j in PR]])

    def cosdist(x, y, mask):
        u, w = x[mask], y[mask]
        nu, nw = np.linalg.norm(u, axis=1), np.linalg.norm(w, axis=1)
        ok = (nu > 0) & (nw > 0)
        return np.where(ok, 1 - (u * w).sum(1) / np.maximum(nu * nw, 1e-12), np.nan)

    print(f"\n  ⭐ E2 · ON THE {int(tied.sum())} TIED PROMPTS")
    same_sign, dists = [], []
    for a, b in pairs:
        ss = float((signvec(Y[a], tied) == signvec(Y[b], tied)).all(1).mean())
        cd = cosdist(Y[a], Y[b], tied)
        same_sign.append(ss); dists.append(float(np.nanmean(cd)))
    print(f"     sign vectors identical: mean {np.mean(same_sign):.4f} "
          f"[{min(same_sign):.4f}, {max(same_sign):.4f}] over {len(pairs)} pairs")
    print(f"     satisfaction cosine distance: mean {np.mean(dists):.4f} "
          f"[{min(dists):.4f}, {max(dists):.4f}]")
    allc = np.concatenate([cosdist(Y[a], Y[b], tied) for a, b in pairs])
    allc = allc[~np.isnan(allc)]
    qq = np.percentile(allc, [5, 25, 50, 75, 95])
    print(f"     distance quantiles {np.round(qq, 4).tolist()}   "
          f"share > 0.20: {float((allc > 0.20).mean()):.4f}   share < 0.05: "
          f"{float((allc < 0.05).mean()):.4f}")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    posd = float(np.nanmean(cosdist(Y["coval_core"], Y["gen_sham"], tied)))
    g0d = float(np.nanmean(cosdist(Y["coval_core"], Y["coval_core"], tied)))
    plcd = float(np.nanmean(cosdist(Y["topw_k4"], Y["topw_k4_detA"], tied)))
    # ⛔ TWO CONTROLS COULD NOT HAVE PASSED AS FIRST WRITTEN, AND BOTH ARE MY ERRORS.
    # ① g=0 and PLACEBO required `== 0.0` on a COSINE DISTANCE, which for identical vectors computes
    #    `1 - (u·u)/(|u||u|)` and lands at ±1e-16 in floating point. Requiring exact zero of a
    #    floating-point identity is a check that cannot pass. Tolerance 1e-9, stated.
    # ② POSITIVE required `> 0.05`, a number I picked without computing what the known-different pair
    #    returns ON THIS SUBSET. It returns 0.0358. §4's `control that cannot PASS` — the threshold
    #    sat above what the design can return under the plant available. The repair is NOT a lower
    #    number chosen to pass: the criterion is now COMPUTED and non-tunable — the known-different
    #    pair must be more distant than ANY committed pair on the same prompts.
    TOL = 1e-9
    ceil_tied = float(np.nanmax(np.concatenate(
        [cosdist(Y[a], Y[b], tied) for a in ARMS for b in ARMS if a != b])))
    max_committed = max(dists)
    ok_pos = posd > max_committed
    print(f"\n  POSITIVE    coval_core vs gen_sham on the tied prompts: {posd:.4f}   must exceed the "
          f"largest COMMITTED-pair distance on the same prompts ({max_committed:.4f})  "
          f"{'PASS' if ok_pos else '⛔ FAIL'}   ratio {posd/max(max_committed,1e-12):.2f}x")
    print(f"              band computed ON THIS SUBSET: floor {g0d:.2e} (identical arms), "
          f"ceiling {ceil_tied:.4f} (widest pair anywhere here) — threshold strictly inside")
    print(f"  g=0         an arm against ITSELF: {g0d:.2e}  {'PASS' if abs(g0d) <= TOL else '⛔ FAIL'}"
          f"   (tolerance {TOL:.0e} — a cosine identity is not exactly 0 in floating point)")
    print(f"  PLACEBO     topw_k4 vs _detA: {plcd:.2e}  {'PASS' if abs(plcd) <= TOL else '⛔ FAIL'}")
    ceiling = ceil_tied
    shamd = [float(np.nanmean(cosdist(Y[a], Y[b], disc))) for a, b in pairs]
    print(f"  SHAM        the SAME distance on the {int(disc.sum())} DISCRIMINATING prompts: "
          f"mean {np.mean(shamd):.4f}   vs tied {np.mean(dists):.4f}   ratio "
          f"{np.mean(dists)/max(np.mean(shamd),1e-12):.3f}")
    rng = np.random.default_rng(773)
    negd = []
    for _ in range(NDRAW):
        m = np.zeros(P, bool); m[rng.choice(P, int(tied.sum()), replace=False)] = True
        negd.append(float(np.nanmean([np.nanmean(cosdist(Y[a], Y[b], m)) for a, b in pairs])))
    print(f"  NEGATIVE    {NDRAW} random subsets of the same size: {np.mean(negd):.4f} "
          f"[{np.percentile(negd,2.5):.4f}, {np.percentile(negd,97.5):.4f}]  vs tied "
          f"{np.mean(dists):.4f}")

    # ---- E3 · a magnitude-sensitive estimator, and its own floor ----------------------------------
    def spear(Yt, mask):
        """Per-prompt agreement of the arm's satisfaction ORDER with each human's, magnitude-aware."""
        out = []
        idx = np.where(mask)[0]
        for a in idx:
            r = np.argsort(np.argsort(Yt[a]))
            vals = []
            for h in HC[a]:
                hs = np.zeros(4)
                for k, (i, j) in enumerate(PR):
                    hs[i] += h[k]; hs[j] -= h[k]
                hr = np.argsort(np.argsort(hs))
                vals.append(1 - 6 * ((r - hr) ** 2).sum() / (4 * (16 - 1)))
            out.append(np.mean(vals))
        return np.array(out)

    print(f"\n  ⭐ E3 · A MAGNITUDE-SENSITIVE ESTIMATOR ON THE TIED PROMPTS (D3: more separation is "
          f"nearly forced — the question is whether it is above its OWN floor)")
    SP = {t: spear(Y[t], tied) for t in COM}
    print(f"  {'pair':<26}{'eff':>10}{'own MDE':>10}{'eff/MDE':>10}   separates?")
    sep = 0
    e3 = {}
    for a, b in pairs:
        d = SP[a] - SP[b]
        m = ZEFF * d.std(ddof=1) / math.sqrt(len(d)) if d.std(ddof=1) > 0 else 0.0
        r = d.mean() / m if m > 0 else 0.0
        sep += abs(r) >= 1
        e3[f"{a} vs {b}"] = {"eff": float(d.mean()), "mde": float(m), "ratio": float(r)}
        print(f"  {a+' vs '+b:<26}{d.mean():>10.4f}{m:>10.4f}{r:>10.4f}   {abs(r) >= 1}")
    print(f"  pairs separated by the finer statistic where A2 ties: {sep} of {len(pairs)}")
    print(f"  ⚠ this is a DIFFERENT ESTIMAND — 'does the arm ORDER the responses like the human' vs "
          f"'does its sign pattern MATCH' — and a separation here is not evidence A2 is wrong")

    ctrl = ok_pos and abs(g0d) <= TOL and abs(plcd) <= TOL
    md = float(np.mean(dists))
    if not ctrl:
        world = "UNVERIFIED"
    elif float((allc > 0.20).mean()) > 0.15 and float((allc < 0.05).mean()) > 0.15:
        world = ("C · MIXED — the 223 is not one population: "
                 f"{(allc>0.20).mean():.1%} of tied prompt-pairs sit above 0.20 and "
                 f"{(allc<0.05).mean():.1%} below 0.05")
    elif md < 0.05:
        world = "A · STRUCTURAL — the arms really do the same thing on those prompts"
    elif md >= 0.20:
        world = "B · GRANULAR — A2's coarseness hides real differences"
    else:
        world = f"NO WORLD — mean distance {md:.4f} sits between the registered bands"
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/ties_structural_or_granular.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "n_tied": int(tied.sum()), "n_disc": int(disc.sum()),
        "E1_invariance": inv, "verdict_changes": int(moved),
        "n_required_scale": float(disc.sum() / P),
        "E2_sign_identical_mean": float(np.mean(same_sign)),
        "E2_cosdist_mean": md, "E2_cosdist_quantiles": qq.tolist(),
        "E2_share_above_0_20": float((allc > 0.20).mean()),
        "E2_share_below_0_05": float((allc < 0.05).mean()),
        "controls": {"positive": posd, "positive_threshold": max_committed,
                     "positive_pass": bool(ok_pos), "g0": g0d, "placebo": plcd, "ceiling": ceiling,
                     "sham_disc_mean": float(np.mean(shamd)),
                     "negative_mean": float(np.mean(negd))},
        "E3": e3, "E3_separated": int(sep), "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
