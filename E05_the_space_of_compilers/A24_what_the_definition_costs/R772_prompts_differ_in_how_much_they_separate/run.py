#!/usr/bin/env python3
"""R772 · prompts differ in how much they SEPARATE arms — a multiplicative scale, not an additive one.

⛔ CHECK #374 REFUTES R771's REGISTERED NUISANCE FROM R771's OWN ALGEBRA. It named "a prompt whose
   annotators disagree more depresses each arm's A2 together" — an ADDITIVE COMMON term, which
   cancels exactly in every difference and which R771's own failed plant demonstrated at four
   loadings. **Eighth closing line this arc needing repair, and the first refuted by the round that
   wrote it.**
⭐ What does NOT cancel is a MULTIPLICATIVE scale: `d_ab(p) = c(p)·delta_ab + noise` predicts exactly
   R771's three observations — small positive DISJOINT correlations, ~zero excess among arm-SHARING
   pairs, and extra spectral concentration.

⛔ FORCED, LABELLED:
  D1 an additive common term cancels — proven in R771.
  D2 |d| co-moves among ARM-SHARING pairs with no scale at all, because they share an arm. **Only the
     15 DISJOINT pairs are admissible evidence.**
  D3 dividing by a scale estimated from the same data shrinks correlations MECHANICALLY. A quick probe
     gave 0.3791 → 0.3330 that way; **that number is inadmissible and is not reported as evidence.**
     Leave-one-pair-out breaks the circularity.
  D4 `c(p)` has a floor at zero; quantiles are reported, never a min/max ratio, and the divisor's
     floor is stated.

CONTROLS  POSITIVE (a MULTIPLICATIVE plant, swept — the object under test, unlike R771's additive
          one) · g=0 · NEGATIVE (200 permutations of c) · SHAM (normalise by a random draw from c's
          own empirical distribution — same marginal, no alignment) · PLACEBO (an identical pair) ·
          CONFOUND (corr(c, within-prompt SE): a noise-amplitude map, not a separability map).
UNIT      prompt · arm pair (10) · the per-prompt SCALE, which is a property of the PROMPT.
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

    def per_annot(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        out = []
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            out.append(np.array([(s == h).mean() for h in HC[ai]]))
        return out

    AV = {t: per_annot(t) for t in COM}
    A = {t: np.array([v.mean() for v in AV[t]]) for t in COM}
    pairs = list(itertools.combinations(COM, 2))
    D = np.array([A[a] - A[b] for a, b in pairs])
    AB = np.abs(D)
    disj = [(i, j) for i, j in itertools.combinations(range(len(pairs)), 2)
            if not (set(pairs[i]) & set(pairs[j]))]
    shar = [(i, j) for i, j in itertools.combinations(range(len(pairs)), 2)
            if (set(pairs[i]) & set(pairs[j]))]
    Cab = np.corrcoef(AB)
    d_obs = float(np.mean([Cab[i, j] for i, j in disj]))
    s_obs = float(np.mean([Cab[i, j] for i, j in shar]))
    print(f"  prompts {P}   pairs {len(pairs)}   disjoint cells {len(disj)}   sharing cells {len(shar)}")
    print(f"\n  ⭐ E1 · |d| CO-MOVEMENT   disjoint mean {d_obs:+.4f}   arm-sharing mean {s_obs:+.4f}")
    print(f"     D2: only the disjoint block is admissible — sharing pairs co-move with no scale")

    # ---- the scale and its confound ------------------------------------------------------------
    c = AB.mean(0)
    qs = np.percentile(c, [0, 25, 50, 75, 100])
    print(f"  c(p) quantiles (D4: never a min/max ratio) "
          f"{np.round(qs, 4).tolist()}   zeros {int((c == 0).sum())}")
    se = np.array([np.mean([(AV[a][i] - AV[b][i]).std(ddof=1) / math.sqrt(len(AV[a][i]))
                            if len(AV[a][i]) > 1 else np.nan for a, b in pairs])
                   for i in range(P)])
    ok = ~np.isnan(se)
    c_se = float(np.corrcoef(c[ok], se[ok])[0, 1])
    print(f"  ⚠ CONFOUND  corr(c, within-prompt SE) = {c_se:+.4f}  -> "
          f"{'NOISE-AMPLITUDE MAP' if abs(c_se) >= 0.5 else 'not merely a noise map'}")
    agree = np.array([np.mean([(h1 == h2).mean() for h1, h2 in itertools.combinations(HC[i], 2)])
                      if len(HC[i]) > 1 else np.nan for i in range(P)])
    oka = ~np.isnan(agree)
    c_ag = float(np.corrcoef(c[oka], agree[oka])[0, 1])
    print(f"  ⭐ E2 · corr(c, per-prompt ANNOTATOR AGREEMENT) = {c_ag:+.4f}  over {int(oka.sum())} "
          f"prompts  -> R771's registered nuisance, in the form the algebra permits")

    # ---- PLACEBO ---------------------------------------------------------------------------------
    dd = A["topw_k4"] - np.array([v.mean() for v in per_annot("topw_k4_detA")])
    plc = float(np.abs(dd).max()) == 0.0
    print(f"\n  PLACEBO     `topw_k4` vs `_detA`: max |d| {np.abs(dd).max():.10f} -> contributes no "
          f"correlation, excluded by construction  {'PASS' if plc else '⛔ FAIL'}")

    # ---- the simulated independence reference for E1 ---------------------------------------------
    obs_var = np.array([D[i].var(ddof=1) for i in range(len(pairs))])
    M = np.zeros((len(pairs), len(COM)))
    for i, (a, b) in enumerate(pairs):
        M[i, COM.index(a)] = 1.0; M[i, COM.index(b)] = 1.0
    v, *_ = np.linalg.lstsq(M, obs_var, rcond=None)
    rng = np.random.default_rng(772)

    def sim(width=0.0, R=None):
        if R is None:
            R = rng.normal(0, np.sqrt(np.maximum(v, 1e-12))[None, :], (P, len(COM)))
        Dv = np.array([R[:, COM.index(a)] - R[:, COM.index(b)] for a, b in pairs])
        if width > 0:
            s = rng.lognormal(0, width, P)
            Dv = Dv * s[None, :]
        return Dv

    ref = []
    for _ in range(NDRAW):
        Cs = np.corrcoef(np.abs(sim()))
        ref.append(float(np.mean([Cs[i, j] for i, j in disj])))
    rlo, rhi = np.percentile(ref, 2.5), np.percentile(ref, 97.5)
    print(f"  reference   {NDRAW} independence simulations: disjoint |d| corr "
          f"{np.mean(ref):+.4f} [{rlo:+.4f}, {rhi:+.4f}]   vs observed {d_obs:+.4f}")

    # ---- POSITIVE · a MULTIPLICATIVE plant, swept ------------------------------------------------
    print(f"\n  POSITIVE    a MULTIPLICATIVE scale planted at swept width (the object under test):")
    dose = {}
    for w in (0.0, 0.25, 0.5, 1.0):
        vals = []
        for _ in range(40):
            Cs = np.corrcoef(np.abs(sim(width=w)))
            vals.append(float(np.mean([Cs[i, j] for i, j in disj])))
        dose[w] = float(np.mean(vals))
        print(f"     width {w:>4.2f}  disjoint |d| corr {dose[w]:+.4f}  detected (> ref 97.5) "
              f"{dose[w] > rhi}")
    pos = dose[1.0] > rhi
    g0 = not (dose[0.0] > rhi)
    mono = all(dose[a] <= dose[b] + 1e-9 for a, b in zip([0.0, 0.25, 0.5], [0.25, 0.5, 1.0]))
    print(f"     registered band — 0.00 must NOT detect, 1.00 must: {pos and g0}  "
          f"{'PASS' if pos and g0 else '⛔ FAIL'}   monotone: {mono}")

    # ---- E3 · LEAVE-ONE-PAIR-OUT normalisation --------------------------------------------------
    floor = float(np.percentile(c[c > 0], 5))
    print(f"\n  ⭐ E3 · LEAVE-ONE-PAIR-OUT normalisation (D3: no pair divided by its own scale)")
    print(f"     divisor floor = 5th pct of the positive scales = {floor:.5f}")
    Dn = np.empty_like(D)
    for i in range(len(pairs)):
        ci = np.delete(AB, i, axis=0).mean(0)
        Dn[i] = D[i] / np.maximum(ci, floor)
    ev_raw = np.linalg.eigvalsh(np.corrcoef(D))[::-1]
    ev_lopo = np.linalg.eigvalsh(np.corrcoef(Dn))[::-1]
    lead_raw = float(ev_raw[0] / ev_raw.sum()); lead_lopo = float(ev_lopo[0] / ev_lopo.sum())
    sham = []
    for _ in range(NDRAW):
        rc = rng.choice(c, P, replace=True)
        Ds = D / np.maximum(rc, floor)[None, :]
        e = np.linalg.eigvalsh(np.corrcoef(Ds))[::-1]
        sham.append(float(e[0] / e.sum()))
    slo, shi = np.percentile(sham, 2.5), np.percentile(sham, 97.5)
    neg = []
    for _ in range(NDRAW):
        pc = c[rng.permutation(P)]
        Ds = D / np.maximum(pc, floor)[None, :]
        e = np.linalg.eigvalsh(np.corrcoef(Ds))[::-1]
        neg.append(float(e[0] / e.sum()))
    print(f"     leading share  raw {lead_raw:.4f}   LOPO-normalised {lead_lopo:.4f}")
    print(f"  SHAM        normalise by a random draw from c's OWN distribution, {NDRAW}x: "
          f"{np.mean(sham):.4f} [{slo:.4f}, {shi:.4f}]")
    print(f"  NEGATIVE    normalise by a PERMUTED c, {NDRAW}x: {np.mean(neg):.4f} "
          f"[{np.percentile(neg,2.5):.4f}, {np.percentile(neg,97.5):.4f}]")
    beats_sham = lead_lopo < slo
    print(f"     LOPO beats the sham band (lower is more explained): {beats_sham}")

    ctrl = plc and pos and g0
    if not ctrl:
        world = "UNVERIFIED"
    elif abs(c_se) >= 0.5:
        world = f"B · NOISE-AMPLITUDE MAP — corr(c, within-SE) = {c_se:+.4f}"
    elif d_obs <= rhi:
        world = f"C · no scale — disjoint |d| corr {d_obs:+.4f} inside the reference band"
    elif beats_sham:
        world = ("A · A REAL SEPARABILITY SCALE — disjoint |d| co-movement above the band, and "
                 "leave-one-pair-out normalisation explains more than a matched random divisor")
    else:
        world = (f"NO WORLD — the disjoint co-movement is real ({d_obs:+.4f} vs [{rlo:+.4f}, "
                 f"{rhi:+.4f}]) but LOPO normalisation ({lead_lopo:.4f}) does not beat a matched "
                 f"random divisor ([{slo:.4f}, {shi:.4f}]); the scale is not the whole story")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/separability_scale.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "disjoint_abs_corr": d_obs, "sharing_abs_corr": s_obs,
        "reference_mean": float(np.mean(ref)), "reference_lo": float(rlo), "reference_hi": float(rhi),
        "c_quantiles": qs.tolist(), "c_zeros": int((c == 0).sum()),
        "corr_c_within_se": c_se, "corr_c_annotator_agreement": c_ag,
        "dose": {str(k): val for k, val in dose.items()},
        "lead_raw": lead_raw, "lead_lopo": lead_lopo, "divisor_floor": floor,
        "sham_mean": float(np.mean(sham)), "sham_lo": float(slo), "sham_hi": float(shi),
        "negative_mean": float(np.mean(neg)),
        "controls": {"placebo": plc, "positive": pos, "g0": g0, "monotone": mono},
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
