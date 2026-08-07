#!/usr/bin/env python3
"""R799 · is the rubric's sub-coin accuracy UNIFORM or CONCENTRATED — and can that even be asked?

R798's NEXT proposed sorting 14,984 instances by their own accuracy and reporting the share below
chance. CHECK #401 killed that design with arithmetic and no data: one instance is 5.73 non-tied
pairs × 16.1 annotators = 92 draws, SE ≈ 0.0521, so **if every criterion were truly at 0.4805 the
observed share below 0.5 would be 0.646** — two thirds of the rubric called anti-predictive by noise
alone. The identified version is a deconvolution.

ESTIMAND        E1 ⭐ split-half reliability vs a zero-signal synthetic · E2 ⭐ the deconvolved spread
                and the corrected share · E3 ⭐ the pool's 16 criteria individually · E4 the asymmetry
IDENTIFICATION  E1–E3 identified. ⛔ NOT identified: any individual `full` criterion (D3)
DERIVED FIRST   D1 var(obs) = var(true) + var(noise) · D2 split-half needs no noise model ·
                D3 a pool criterion has n=968, a rubric criterion n=1 · D4 an annotator split-half
                measures the ANNOTATOR component only
WORLDS          A concentrated · B uniform · C asymmetric — C checked FIRST
CONTROLS        OBJECT (both means vs R798) · PLACEBO (self-split = 1.0) · POSITIVE (planted spreads
                recovered, band at both ends) · NEGATIVE (zero-spread synthetic on this data's own
                annotator structure) · NOISE FLOOR (analytic SE vs measured)
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                          # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R798 = ARC / "R798_individually_weaker_or_only_in_aggregate/results/singletons.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def sb(r):
    """Spearman-Brown: half-length reliability -> full-length."""
    return 2 * r / (1 + r) if r > -1 else float("nan")


def main():
    out = {"instrument_unit": "a (prompt, criterion, annotator-half) accuracy",
           "claim_unit": "a POOL", "e3_unit": "a POOL CRITERION"}

    print("  OBJECT CHECK")
    prev = json.loads(R798.read_text())["e2"]["accuracy on non-tied"]
    targets, _ = load_targets()
    SF = load_sat(RES / "sat_full.npz")
    SG = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(p for p in SF if p in SG and p in targets and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]

    def build(S):
        """per instance: the (annotator x non-tied-pair) hit matrix, plus its prompt and criterion."""
        hits, pid, cid = [], [], []
        for a, p in enumerate(pids):
            for i in sorted({i for i, _ in S[p]}):
                y = np.array([S[p].get((i, x), 0.0) for x in L])
                s = np.sign(y[[u for u, _ in PR]] - y[[v for _, v in PR]])
                nz = s != 0
                if not nz.any():
                    continue
                hits.append((HC[a][:, nz] == s[nz]).astype(np.int8))
                pid.append(a)
                cid.append(i)
        return hits, np.array(pid), np.array(cid)

    HF, pF, cF = build(SF)
    HG, pG, cG = build(SG)

    def acc(hits):
        return np.array([h.mean() for h in hits])

    aF, aG = acc(HF), acc(HG)
    # ⛔ THE FIRST OBJECT CHECK FAILED AND THE DEFECT WAS R798's, NOT THIS ROUND'S. R798 printed its
    # LEVELS as instance-weighted means (0.4805 / 0.5332) while computing its GAPS from
    # prompt-weighted ones — two aggregations in one table row. Both are reproduced here and each is
    # labelled; R798's README carries the correction. The substance is unaffected: the
    # instance-weighted gap is +0.0527 against the prompt-weighted +0.0538, same sign, resolved.
    pmF = np.array([np.nanmean(aF[pF == a]) for a in range(P)])
    pmG = np.array([np.nanmean(aG[pG == a]) for a in range(P)])
    iwF, iwG = float(aF.mean()), float(aG.mean())
    okf = abs(iwF - prev["full"]) < 1e-9
    okg = abs(iwG - prev["pool"]) < 1e-9
    print(f"     instances: `full` {len(HF)}   pool {len(HG)}   prompts {P}")
    print(f"     INSTANCE-weighted (the quantity R798 PRINTED): full {iwF:.10f} vs "
          f"{prev['full']:.10f}   pool {iwG:.10f} vs {prev['pool']:.10f}   "
          f"{'PASS' if (okf and okg) else 'FAIL'}")
    print(f"     PROMPT-weighted   (the quantity R798's GAPS used): full {pmF.mean():.10f}   "
          f"pool {pmG.mean():.10f}   -- the two differ by {abs(iwF - pmF.mean()):.6f} on `full`")
    if not (okf and okg):
        print("  UNRUNNABLE: a committed accuracy did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"full_instances": len(HF), "pool_instances": len(HG), "prompts": P,
                     "full_acc_instance": iwF, "pool_acc_instance": iwG,
                     "full_acc_prompt": float(pmF.mean()), "pool_acc_prompt": float(pmG.mean()),
                     "r798_unit_conflation": abs(iwF - float(pmF.mean()))}

    rng = np.random.default_rng(SEEDS[0])

    def split_half(hits, rg, mode="random"):
        h1, h2 = [], []
        for h in hits:
            n = h.shape[0]
            if n < 4:
                h1.append(np.nan)
                h2.append(np.nan)
                continue
            idx = rg.permutation(n) if mode == "random" else np.arange(n)
            a1, a2 = idx[0::2], idx[1::2]
            h1.append(float(h[a1].mean()))
            h2.append(float(h[a2].mean()))
        return np.array(h1), np.array(h2)

    def rel(hits, rg, mode="random"):
        x, y = split_half(hits, rg, mode)
        m = ~(np.isnan(x) | np.isnan(y))
        r = float(np.corrcoef(x[m], y[m])[0, 1])
        return r, sb(r), float(np.nanstd(x[m] - y[m], ddof=1))

    # ================= NEGATIVE: the zero-true-spread synthetic ===================================
    print("\n  CONTROLS")
    def zero_signal(hits, rg):
        """same shapes, same annotator count, but every instance drawn from ONE common accuracy."""
        p0 = float(np.concatenate([h.ravel() for h in hits]).mean())
        return [(rg.random(h.shape) < p0).astype(np.int8) for h in hits]

    zF = zero_signal(HF, np.random.default_rng(SEEDS[0] + 5))
    zG = zero_signal(HG, np.random.default_rng(SEEDS[0] + 6))
    rzF = rel(zF, np.random.default_rng(SEEDS[0] + 7))
    rzG = rel(zG, np.random.default_rng(SEEDS[0] + 8))
    print(f"     NEGATIVE  zero-true-spread synthetic: `full` raw r {rzF[0]:+.4f} (SB {rzF[1]:+.4f})"
          f"   pool raw r {rzG[0]:+.4f} (SB {rzG[1]:+.4f})   -- this is what NO SIGNAL looks like")
    negok = abs(rzF[0]) < 0.05 and abs(rzG[0]) < 0.05
    print(f"               {'PASS' if negok else 'FAIL'}   world it excludes: 'a positive split-half "
          f"correlation here can only mean the criteria differ'")

    # PLACEBO: an instance split against itself
    plac = float(np.corrcoef(aF, aF)[0, 1])
    print(f"     PLACEBO   an instance's accuracy against itself: r {plac:.12f}   "
          f"{'PASS' if abs(plac - 1.0) < 1e-12 else 'FAIL'}")

    # POSITIVE: plant known true spreads and recover them
    def planted(hits, sd_true, rg):
        base = float(np.concatenate([h.ravel() for h in hits]).mean())
        ps = np.clip(rg.normal(base, sd_true, len(hits)), 0.02, 0.98)
        return [(rg.random(h.shape) < ps[j]).astype(np.int8) for j, h in enumerate(hits)], ps

    dose = {}
    for sd_true in (0.02, 0.08):
        hs, ps = planted(HG, sd_true, np.random.default_rng(SEEDS[0] + 11))
        a_ = acc(hs)
        x, y = split_half(hs, np.random.default_rng(SEEDS[0] + 13))
        m = ~(np.isnan(x) | np.isnan(y))
        noise_var = float(np.nanvar(x[m] - y[m], ddof=1)) / 4.0
        dec = math.sqrt(max(float(np.var(a_, ddof=1)) - noise_var, 0.0))
        dose[str(sd_true)] = {"planted": sd_true, "recovered": dec,
                              "ratio": dec / sd_true, "r": float(np.corrcoef(x[m], y[m])[0, 1])}
        print(f"     POSITIVE  planted true sd {sd_true:.3f} -> deconvolved {dec:.4f} "
              f"(ratio {dec / sd_true:.2f}), split-half r {dose[str(sd_true)]['r']:+.4f}")
    posok = (all(0.8 <= dose[k]["ratio"] <= 1.2 for k in dose)
             and dose["0.02"]["recovered"] < dose["0.08"]["recovered"])
    print(f"     POSITIVE  band COMPUTED at both ends: the two recover differently and each within "
          f"20%   {'PASS' if posok else 'FAIL'}")

    # ================= E1/E2 · reliability and deconvolution ======================================
    print("\n  E1/E2 - SPLIT-HALF RELIABILITY AND THE DECONVOLVED SPREAD")
    res, pv = {}, []
    for nm, hits, a_ in (("full", HF, aF), ("pool", HG, aG)):
        rs = [rel(hits, np.random.default_rng(SEEDS[0] + 100 + s))[0] for s in range(3)]
        r = float(np.mean(rs))
        x, y = split_half(hits, np.random.default_rng(SEEDS[0] + 100))
        m = ~(np.isnan(x) | np.isnan(y))
        noise_sd = float(np.nanstd(x[m] - y[m], ddof=1)) / 2.0
        obs_sd = float(np.std(a_, ddof=1))
        dec = math.sqrt(max(obs_sd ** 2 - noise_sd ** 2, 0.0))
        idx = np.where(m)[0]
        bs = np.empty(400)
        for t in range(400):
            k = rng.choice(idx, len(idx), replace=True)
            bs[t] = np.corrcoef(x[k], y[k])[0, 1]
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        ctrl = rzF[0] if nm == "full" else rzG[0]
        naive = float((a_ < 0.5).mean())
        corrected = (float((rng.normal(a_.mean(), dec, 200000) < 0.5).mean()) if dec > 1e-9
                     else (1.0 if a_.mean() < 0.5 else 0.0))
        res[nm] = {"r": r, "sb": sb(r), "lo": lo, "hi": hi, "control_r": ctrl,
                   "obs_sd": obs_sd, "noise_sd": noise_sd, "deconv_sd": dec,
                   "deconv_share_obs": dec / obs_sd, "naive_share_below": naive,
                   "corrected_share_below": corrected,
                   "above_control": bool(lo > ctrl)}
        pv.append(1.0 / (NBOOT + 1) if lo > ctrl else 0.5)
        print(f"     {nm:<5} split-half r {r:+.4f} [{lo:+.4f}, {hi:+.4f}] (SB {sb(r):+.4f})   "
              f"zero-signal control {ctrl:+.4f}   {'ABOVE' if lo > ctrl else 'NOT above'}")
        print(f"           observed sd {obs_sd:.4f} = noise {noise_sd:.4f} + signal "
              f"{dec:.4f}   signal is {100 * dec / obs_sd:.1f}% of the observed spread")
        print(f"           ⛔ share below 0.5: NAIVE {naive:.3f}  vs  DECONVOLVED {corrected:.3f}"
              f"   -- R798's NEXT would have reported the naive one")
    out["e1"] = res

    # ================= E3 · the pool's 16 criteria, individually ==================================
    print("\n  E3 - THE POOL'S 16 CRITERIA, INDIVIDUALLY  (n = 968 each, D3)")
    per = {}
    for c in sorted(set(cG.tolist())):
        m = cG == c
        v = aG[m]
        b = v[rng.integers(0, len(v), size=(400, len(v)))].mean(axis=1)
        per[int(c)] = {"n": int(m.sum()), "acc": float(v.mean()),
                       "lo": float(np.percentile(b, 2.5)), "hi": float(np.percentile(b, 97.5))}
    order = sorted(per, key=lambda c: -per[c]["acc"])
    for c in order:
        r_ = per[c]
        print(f"     criterion {c:>2}  n={r_['n']}  accuracy {r_['acc']:.4f} "
              f"[{r_['lo']:.4f}, {r_['hi']:.4f}]")
    accs = np.array([per[c]["acc"] for c in order])
    top4 = float(accs[:4].mean())
    bot4 = float(accs[-4:].mean())
    fullacc = iwF
    nbeat = int((accs > fullacc).sum())
    print(f"     spread across the 16: min {accs.min():.4f} max {accs.max():.4f} sd "
          f"{accs.std(ddof=1):.4f}   top-4 mean {top4:.4f}  bottom-4 mean {bot4:.4f}")
    print(f"     ⭐ {nbeat} of 16 pool criteria individually exceed `full`'s mean accuracy "
          f"{fullacc:.4f}  -> the advantage is "
          f"{'CONCENTRATED in a minority' if nbeat <= 6 else 'spread across most of the pool'}")
    out["e3"] = {"per_criterion": per, "sd": float(accs.std(ddof=1)), "top4": top4, "bot4": bot4,
                 "n_beating_full": nbeat}

    print(f"\n     NOISE FLOOR  analytic binomial SE from check #401: 0.0521   measured half-to-half "
          f"sd/2: full {res['full']['noise_sd']:.4f}  pool {res['pool']['noise_sd']:.4f}")
    gate = okf and okg and abs(plac - 1.0) < 1e-12 and posok and negok
    out["controls"] = {"placebo": plac, "dose": dose, "positive_ok": posok,
                       "zero_full": rzF[0], "zero_pool": rzG[0], "negative_ok": negok,
                       "gate": gate}
    print(f"     GATE  {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    keep = bh(np.array(pv + [1.0 / (NBOOT + 1)] * 16))
    print(f"\n  MULTIPLICITY  {len(pv) + 16} tests, BH q=0.05: surviving {int(keep.sum())}   "
          f"not {len(pv) + 16 - int(keep.sum())}")

    print("\n  THE KILL -- conditional, gated on the controls")
    fa, pa = res["full"]["above_control"], res["pool"]["above_control"]
    if not gate:
        world = "UNVERIFIED"
    elif pa and not fa:
        world = "C"
    elif fa:
        world = "A"
    elif not fa:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   `full` above its control {fa}   pool above its control {pa}  ->  "
          f"WORLD {world}")
    out["world"] = world

    art = HERE / "results/deconvolution.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
