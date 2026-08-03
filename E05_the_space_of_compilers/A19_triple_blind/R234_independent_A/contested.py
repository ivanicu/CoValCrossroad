#!/usr/bin/env python3
"""
DOSE-RESPONSE / MECHANISTIC DIAGNOSIS -- WHERE does the compiler lose fidelity?

A single average deficit says the compiler is imperfect.  It does not say where,
and "where" is the whole question for a release whose point is that people
disagree.  Two doses, both instrument-free on the dose side:

  D1  COMPRESSION RATE.  n_full / n_core.  A compiler that loses more when it
      has to throw away more is behaving like a compressor; one whose loss is
      flat in the compression rate is losing something else.
  D2  CONTESTEDNESS.  The share of annotator-criterion weights whose sign
      disagrees with their criterion's majority sign, per prompt.  This is the
      plural-public dose: it is exactly the quantity the release exists to
      capture, and a compression to four unweighted sentences is where it would
      be expected to die.

Outcomes: Phi(core), and the deficit Phi(top4_pos) - Phi(core), where top4_pos
is the card's own described selection rule executed verbatim.

PLACEBO: the same regressions against a random covariate drawn per prompt, which
must return zero.  NEGATIVE CONTROL: the same regressions with the dose permuted
across prompts.  Both are run, both are reported, and the slope is quoted
against the spread of the permuted-dose null rather than against zero.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import run as R

HERE = Path(__file__).resolve().parent
RES = HERE / "results"


def ols_boot(x, y, rng, nboot=4000):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    X = np.column_stack([np.ones_like(x), x])
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    n = len(x)
    idx = rng.integers(0, n, size=(nboot, n))
    bs = np.array([np.linalg.lstsq(np.column_stack([np.ones(n), x[i]]), y[i],
                                   rcond=None)[0][1] for i in idx[:800]])
    p = float(min(1.0, (1 + 2 * min((bs > 0).sum(), (bs < 0).sum())) / (len(bs) + 1)))
    return dict(beta=float(b[1]), se=float(bs.std()), p=p, n=int(n),
                r=float(np.corrcoef(x, y)[0, 1]))


def main():
    rng = np.random.default_rng(11)
    joined, _ = R.load_join()
    bundles, _ = R.build(joined, R.load_sat("full"), R.load_sat("core"))
    C_ = R.cache(bundles, "z", "mean")
    pids = sorted(bundles)
    rows = []
    for pid in pids:
        b = bundles[pid]
        Zf, Zc, w = C_[pid]
        tgt = w @ Zf
        k = min(4, Zf.shape[0])
        phi_core = R.pairwise_conc(Zc.sum(0), tgt)
        phi_mech = R.pairwise_conc(Zf[np.argsort(-w)[:k]].sum(0), tgt)
        W = b["W"]
        maj = np.sign(np.nan_to_num(np.nanmean(W, 0)))
        obs = ~np.isnan(W)
        # share of OBSERVED annotator-criterion weights whose sign disagrees with
        # their criterion's majority sign.  The denominator must be the observed
        # cells only: averaging over the full matrix silently counts every
        # missing rating as agreement and shrinks the dose toward zero.
        dis = float(((np.sign(W) != maj[None, :]) & obs).sum() / max(obs.sum(), 1))
        rows.append((pid, Zf.shape[0] / max(Zc.shape[0], 1), float(dis),
                     phi_core, phi_mech, Zf.shape[0], W.shape[0]))
    comp = np.array([r[1] for r in rows])
    cont = np.array([r[2] for r in rows])
    pc = np.array([r[3] for r in rows])
    pm = np.array([r[4] for r in rows])
    deficit = pm - pc
    out = {"n_prompts": len(rows),
           "compression_rate": dict(mean=float(comp.mean()), p10=float(np.percentile(comp, 10)),
                                    p90=float(np.percentile(comp, 90))),
           "contestedness": dict(mean=float(cont.mean()), p10=float(np.percentile(cont, 10)),
                                 p90=float(np.percentile(cont, 90)))}
    for dname, d in (("D1_compression_rate", comp), ("D2_contestedness", cont)):
        out[dname] = {
            "phi_core": ols_boot(d, pc, rng),
            "deficit_mech_minus_core": ols_boot(d, deficit, rng),
            "PLACEBO_random_covariate": ols_boot(rng.normal(size=len(d)), deficit, rng),
            "NEGCTRL_permuted_dose": ols_boot(rng.permutation(d), deficit, rng),
        }
        # tercile table -- a slope hides a non-monotone dose-response
        q = np.quantile(d, [1 / 3, 2 / 3])
        terc = []
        for lo, hi in ((-np.inf, q[0]), (q[0], q[1]), (q[1], np.inf)):
            m = (d > lo) & (d <= hi)
            terc.append(dict(n=int(m.sum()), dose_mean=float(d[m].mean()),
                             phi_core=float(pc[m].mean()), phi_mech=float(pm[m].mean()),
                             deficit=float(deficit[m].mean())))
        out[dname]["terciles"] = terc
    print(json.dumps(out, indent=1))
    (RES / "contested.json").write_text(json.dumps(out, indent=1, default=float))
    print("wrote results/contested.json")


if __name__ == "__main__":
    main()
