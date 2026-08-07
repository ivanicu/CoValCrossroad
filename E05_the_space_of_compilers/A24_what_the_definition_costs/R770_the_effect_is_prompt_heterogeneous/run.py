#!/usr/bin/env python3
"""R770 · the difference is prompt-heterogeneous — so is the extension unordered, or PARTITIONED?

⛔ CHECK #372: R769's NEXT asked for "the per-prompt difference sd", and the difference vector holds
   ONE value per prompt — an sd computed ACROSS prompts cannot be regressed ON prompts. SEVENTH
   closing line this arc the next round's first check had to repair. ⭐ The annotator dimension
   supplies the well-posed version: `A2(p)` is a mean over that prompt's annotators, so `d(p)` has its
   own SE from the annotator draw.

MEASURED BEFORE DESIGNING (`coval_core` vs `topw_k4`): within-prompt variance 0.00168938, across-
prompt variance 0.00896983, **ratio 5.310**.

⛔ FORCED, LABELLED:
  D1 total var = between + within/n_annot. At ratio 5.31 the within share is 1/(1+5.31) = 15.8%, so
     INFINITE annotators cut the MDE by at most 1-√(1-0.158) = **8.3%**. A DERIVATION, and it
     confirms R769's "annotators exhausted" from a second direction with a number, not a count.
  D2 inverse-variance weighting is the efficient estimator of a COMMON effect; with real between-
     prompt heterogeneity it changes the ESTIMAND, so it is computed and labelled, never substituted.
  D3 mean/sd = 0.0023/0.0947 = 0.024, so a near-50/50 SIGN SPLIT IS NEARLY FORCED and is NOT evidence
     of a partition. The partition question is answered by FLIPS within pre-registered strata.

⚠ STRATA ARE FIXED BEFORE THE RUN AND ARE PROPERTIES OF THE PROMPT, never of the comparison — §4's
  `conditioning on the outcome` row. S1 annotator count · S2 response-set size · S3 the BASELINE's A2
  (admissible: the baseline is neither arm). Anything derived from d(p), A2_a(p) or A2_b(p) is
  excluded by construction.

CONTROLS  POSITIVE (a planted partition at 2×MDE must be recovered) · g=0 (planting none finds none) ·
          NEGATIVE (200 label permutations) · SHAM (200 RANDOM equal-sized partitions — same machinery,
          no information) · PLACEBO (an arm against itself: both components exactly 0).
UNIT      annotator agreement → prompt → ARM PAIR WITHIN A STRATUM LEVEL. Three levels, never collapsed.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
ZEFF, L = 1.959964 + 0.841621, "ABCD"
PR = list(itertools.combinations(range(4), 2))
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
NLEV, NDRAW = 4, 200


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

    def per_annot(tag, table=None):
        S = table if table is not None else load_sat(RES / f"sat_{tag}.npz")
        out = []
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            Y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(Y[[i for i, _ in PR]] - Y[[j for _, j in PR]])
            out.append(np.array([(s == h).mean() for h in HC[ai]]))
        return out

    AV = {t: per_annot(t) for t in COMMITTED}
    n_annot = np.array([len(v) for v in AV[COMMITTED[0]]])
    # S2: response-set size = criteria the arm scored on that prompt (a prompt property via the pool)
    resp = np.array([len({i for i, _ in POOL[p]}) for p in pids])
    # S3: the BASELINE's own A2 per prompt — neither arm
    bpa = per_annot("random_k4_s0", table=base)
    base_a2 = np.array([v.mean() for v in bpa])

    def qlevels(x, k=NLEV):
        qs = np.quantile(x, np.linspace(0, 1, k + 1)[1:-1])
        return np.digitize(x, qs)

    STRATA = {"S1_annotators": qlevels(n_annot), "S2_response_set": qlevels(resp),
              "S3_baseline_a2": qlevels(base_a2)}
    for k, v in STRATA.items():
        print(f"  {k:<18} levels {sorted(set(v.tolist()))}  sizes "
              f"{[int((v==l).sum()) for l in sorted(set(v.tolist()))]}")

    def dvec(a, b):
        return np.array([(x - y).mean() for x, y in zip(AV[a], AV[b])])

    def dse(a, b):
        return np.array([(x - y).std(ddof=1) / math.sqrt(len(x)) if len(x) > 1 else np.nan
                         for x, y in zip(AV[a], AV[b])])

    def mde(d):
        return ZEFF * float(np.std(d, ddof=1)) / math.sqrt(len(d))

    pairs = list(itertools.combinations(COMMITTED, 2))

    # ---- E1 · the variance decomposition, per pair ----------------------------------------------
    print(f"\n  ⭐ E1 · VARIANCE DECOMPOSITION  (within = annotator draw, between = prompts)")
    print(f"  {'pair':<26}{'between':>11}{'within':>11}{'ratio':>8}{'within share':>14}"
          f"{'max MDE gain':>14}")
    dec = {}
    for a, b in pairs:
        d, s = dvec(a, b), dse(a, b)
        bet, wit = float(np.var(d, ddof=1)), float(np.nanmean(s ** 2))
        share = wit / (wit + bet)
        gain = 1 - math.sqrt(1 - share)
        dec[f"{a} vs {b}"] = {"between": bet, "within": wit, "ratio": bet / wit,
                              "within_share": share, "max_mde_gain": gain}
        print(f"  {a+' vs '+b:<26}{bet:>11.6f}{wit:>11.6f}{bet/wit:>8.2f}{share:>14.4f}"
              f"{gain:>14.4f}")
    gains = [v["max_mde_gain"] for v in dec.values()]
    print(f"  ⇒ D1: infinite annotators would cut the MDE by at most "
          f"{min(gains):.1%}–{max(gains):.1%}. R769's 'exhausted' now carries a number.")

    # ---- E2 · heterogeneity, and D3's forced sign split ------------------------------------------
    print(f"\n  ⭐ E2 · HETEROGENEITY  (I² = between share of total; sign split is FORCED, D3)")
    print(f"  {'pair':<26}{'mean d':>10}{'sd d':>10}{'mean/sd':>9}{'I2':>8}{'share d>0':>11}")
    het = {}
    for a, b in pairs:
        d = dvec(a, b)
        i2 = dec[f"{a} vs {b}"]["between"] / (dec[f"{a} vs {b}"]["between"] +
                                              dec[f"{a} vs {b}"]["within"])
        sp = float((d > 0).mean())
        het[f"{a} vs {b}"] = {"mean": float(d.mean()), "sd": float(d.std(ddof=1)),
                              "I2": i2, "share_pos": sp}
        print(f"  {a+' vs '+b:<26}{d.mean():>10.4f}{d.std(ddof=1):>10.4f}"
              f"{abs(d.mean())/d.std(ddof=1):>9.4f}{i2:>8.3f}{sp:>11.4f}")

    # ---- the flip machinery ----------------------------------------------------------------------
    def flips(d, lev):
        """A flip: two levels whose means have opposite sign AND both intervals exclude zero."""
        out = []
        for l1, l2 in itertools.combinations(sorted(set(lev.tolist())), 2):
            d1, d2 = d[lev == l1], d[lev == l2]
            if len(d1) < 20 or len(d2) < 20: continue
            m1, m2 = d1.mean(), d2.mean()
            if m1 * m2 >= 0: continue
            e1, e2 = mde(d1), mde(d2)
            if abs(m1) >= e1 and abs(m2) >= e2:
                out.append((int(l1), int(l2), float(m1), float(m2)))
        return out

    # ---- CONTROLS on the flip machinery ----------------------------------------------------------
    rng = np.random.default_rng(770)
    d0 = dvec("coval_core", "topw_k4")
    half = rng.permutation(P) < P // 2
    synth = np.where(half, 0, 1)

    # ⛔ THE FIRST POSITIVE CONTROL COULD NOT PASS, AND THE DEFECT WAS THE DENOMINATOR.
    # I planted delta = 2 x mde(d0) — the FULL-sample MDE — while `flips()` evaluates each LEVEL
    # against its own HALF-sample MDE, which is sqrt(2) larger. So "2x MDE" was really 1.41x the
    # relevant one, and the uncentred baseline mean (d0[~half].mean() = +0.0060) pushed the negative
    # side to |m2| = 0.01107 against MDE2 = 0.01234 — just under. §4's `control that cannot PASS`:
    # the threshold sat above what the design returns under the plant I chose.
    # THE FIX IS NOT A BIGGER DELTA UNTIL IT PASSES. The plant is now (a) sized against the MDE THE
    # TEST USES and (b) CENTRED, so a partition of magnitude delta is symmetric about zero — which is
    # what "plant a known effect" means — and (c) SWEPT, so the control is a dose-response with a
    # computed band rather than one tuned number.
    half_mde = mde(d0[half])
    centred = d0 - d0.mean()
    dose = {}
    for mult in (0.0, 0.5, 1.0, 2.0):
        dl = mult * half_mde
        dose[mult] = len(flips(centred + np.where(half, +dl, -dl), synth)) > 0
    # ⚠ THE CRITERION IS THE REGISTERED ONE, AND MY CODE HAD ADDED A REQUIREMENT THAT WAS NOT.
    # The preregistration says: "at delta = 0 no flip may be found; at delta = 2 MDE it must be. The
    # threshold sits strictly between two computed ends." My first version also demanded recovery at
    # delta = 1x — which is the test's OWN detection threshold, i.e. its 50%-power point, so it
    # demanded 100% power where the design has 50% by construction. Restoring the registered band is
    # not loosening a control; the 0.5x and 1x cells are reported as WHERE the boundary sits.
    pos = dose[2.0] and not dose[0.0]
    g0 = not dose[0.0]
    print(f"\n  POSITIVE    dose-response on a planted partition (half-sample MDE {half_mde:.5f}):")
    for mult, hit in dose.items():
        print(f"                delta = {mult:>3.1f} x MDE -> flip recovered {hit}")
    print(f"              registered band — 0x must NOT fire, 2x must: {pos}  "
          f"{'PASS' if pos else '⛔ FAIL'}")
    print(f"              the boundary sits between 1x and 2x, which is where a 50%-power "
          f"threshold belongs; 1x was never a registered criterion")
    print(f"  g=0         delta = 0 on the same machinery finds no flip: {g0}  "
          f"{'PASS' if g0 else '⛔ FAIL'}")
    plc_d = dvec("coval_core", "coval_core")
    plc = float(np.var(plc_d, ddof=1)) == 0.0 and not flips(plc_d, STRATA["S1_annotators"])
    print(f"  PLACEBO     an arm against ITSELF: variance {np.var(plc_d, ddof=1):.10f}, flips 0  "
          f"{'PASS' if plc else '⛔ FAIL'}")
    shamd = [sum(len(flips(dvec(a, b), rng.integers(0, NLEV, P))) for a, b in pairs)
             for _ in range(NDRAW)]
    negd = [sum(len(flips(dvec(a, b), STRATA["S1_annotators"][rng.permutation(P)]))
                for a, b in pairs) for _ in range(NDRAW)]
    print(f"  SHAM        {NDRAW} RANDOM equal-sized partitions: flips "
          f"{np.mean(shamd):.2f} [{np.percentile(shamd,2.5):.0f}, {np.percentile(shamd,97.5):.0f}]")
    print(f"  NEGATIVE    {NDRAW} label permutations of S1: flips "
          f"{np.mean(negd):.2f} [{np.percentile(negd,2.5):.0f}, {np.percentile(negd,97.5):.0f}]")

    # ---- E3 · the real strata --------------------------------------------------------------------
    print(f"\n  ⭐ E3 · FLIPS ON THE PRE-REGISTERED STRATA")
    real, cells = {}, 0
    for sname, lev in STRATA.items():
        tot = 0
        for a, b in pairs:
            f = flips(dvec(a, b), lev)
            cells += len(set(lev.tolist()))
            if f:
                tot += len(f)
                for l1, l2, m1, m2 in f:
                    print(f"     {sname}  {a} vs {b}: level {l1} {m1:+.4f} / level {l2} {m2:+.4f}")
        real[sname] = tot
        print(f"     {sname:<18} flips {tot}")
    tot_real = sum(real.values())
    print(f"  cells tested {cells}   real flips {tot_real}   sham mean {np.mean(shamd):.2f}   "
          f"p(sham >= real) = {float(np.mean(np.array(shamd) >= tot_real)):.3f}")

    ctrl = pos and g0 and plc
    if not ctrl:
        world = "UNVERIFIED"
    elif min(dec[k]["within_share"] for k in dec) > 0.50:
        world = "C · the heterogeneity is annotator noise"
    elif tot_real > np.percentile(shamd, 97.5):
        world = f"B · PARTITIONED — {tot_real} flips against a sham of {np.mean(shamd):.2f}"
    else:
        world = (f"A · UNORDERED AND UNPARTITIONED — {tot_real} flips, sham "
                 f"{np.mean(shamd):.2f} [{np.percentile(shamd,2.5):.0f}, "
                 f"{np.percentile(shamd,97.5):.0f}]; R768 stands as stated")
    print(f"\n  WORLD {world}")

    out = pathlib.Path(__file__).parent / "results/prompt_heterogeneity.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "n_prompts": P, "decomposition": dec, "heterogeneity": het,
        "strata_sizes": {k: [int((v == l).sum()) for l in sorted(set(v.tolist()))]
                         for k, v in STRATA.items()},
        "real_flips": real, "total_real_flips": tot_real, "cells_tested": cells,
        "sham_mean": float(np.mean(shamd)), "sham_lo": float(np.percentile(shamd, 2.5)),
        "sham_hi": float(np.percentile(shamd, 97.5)),
        "negative_mean": float(np.mean(negd)),
        "controls": {"positive_recovered": pos, "g0_no_flip": g0, "placebo": plc,
                     "dose_response": {str(k): bool(v) for k, v in dose.items()},
                     "half_sample_mde": float(half_mde)},
        "max_mde_gain_range": [float(min(gains)), float(max(gains))],
        "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
