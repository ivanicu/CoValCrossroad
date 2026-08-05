#!/usr/bin/env python3
"""R537 — does R533's weight-reading dose curve survive the 0.8B judge?

R533 measured the value of weight-selection over a per-prompt random draw at matched k, under the
2B judge: +0.0726 at k=4 decaying to exactly 0 at k=all. R536 showed the topw-vs-topvar ORDERING
survives a judge change. This asks the harder question about the whole CURVE.

⭐ THE ARTIFACT NAMING IS TWO CONVENTIONS, and confusing them would have stopped this round:
  sat_<arm>_08b.npz  = the SELECTION ARMS rebuilt under 0.8B (rebuild_selection_08b.sh)
  sat08_full.npz     = the 0.8B JUDGING of the FULL rubric (that script's own --full-npz input)
`sat_full_08b.npz` does not exist and never did; `sat08_full.npz` is the object that plays full's
role under this judge, which is what makes the per-prompt random comparator constructible.

ESTIMAND (before method): the advantage of topw_k over a per-prompt uniform k-draw from the same
  rubric, at k in {3,4,6,8} and at k=all, under the 0.8B judge.
IDENTIFICATION: fully identified -- topw_k*_08b and sat08_full are on disk.
SCOPE  population: the prompts sat08_full covers · instrument: A2 over all annotators · baseline:
  a per-prompt uniform k-draw · regime: SECOND judge, 3 seeds.
WORLDS  A · the curve survives -- positive at every k, monotone decay, zero at k=all. The
              dose-response is a fact about SELECTION.
        B · it does not -- sign flips, or the decay disappears. R533 was judge-specific.
KILL (pre-registered): any non-positive advantage at k in {3,4,6,8} kills world A.
POSITIVE CONTROL: the 0.8B arms must DIFFER from their 2B namesakes, else this is the same
  measurement twice. R536 showed it for topw_k4; re-checked here for every k used.
NEGATIVE CONTROL, forced: at k=all there is nothing to select, so the advantage must be exactly
  0. A curve that misses that endpoint indicts the construction. ⛔ DERIVATION, labelled.
NOISE FLOOR: 3 seeds per cell; spread reported.
MULTIPLICITY: 5 cells x 3 seeds; all printed.
IMPOSSIBLE HERE: coval_core under 0.8B -- sat_coval_core_08b is absent, so the RELEASED core is
  the one admitted arm whose curve position is unreplicated. Named, not marked planned.
"""
import itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls

RES = ROOT / "corebench/results"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT = 1200
KS = [3, 4, 6, 8]

def main():
    FULL8 = load_sat(RES / "sat08_full.npz")
    ARMS = {k: load_sat(RES / f"sat_topw_k{k}_08b.npz") for k in KS}
    targets, _ = load_targets()
    pids = sorted({p for p in FULL8 if p in targets and len(targets[p]) >= 2
                   and all(p in ARMS[k] for k in KS)})
    if not pids:
        print("  empty population -> UNRUNNABLE"); return 2
    HM = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    print(f"  prompts covered by sat08_full and every topw_k*_08b: {len(pids)}")

    def a2(sat, idx=None):
        out = []
        for a, p in enumerate(pids):
            ii = idx[p] if idx else sorted({i for i, _ in sat[p]})
            y = np.array([sum(sat[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(y[[i for i, _ in PAIRS]] - y[[j for _, j in PAIRS]])
            out.append(np.mean([(s == h).mean() for h in HM[a]]))
        return np.array(out)

    # POSITIVE CONTROL: the 0.8B arms must differ from their 2B namesakes
    def same(a, b):
        da, db = np.load(RES/f"sat_{a}.npz", allow_pickle=True), np.load(RES/f"sat_{b}.npz", allow_pickle=True)
        ma = np.array([str(k) for k in da["meta"]]); mb = np.array([str(k) for k in db["meta"]])
        oa, ob = np.argsort(ma, kind="stable"), np.argsort(mb, kind="stable")
        return (len(ma) == len(mb) and (ma[oa] == mb[ob]).all()
                and np.array_equal(np.asarray(da["sat"])[oa], np.asarray(db["sat"])[ob]))
    diff = [k for k in KS if not same(f"topw_k{k}", f"topw_k{k}_08b")]
    print(f"  POSITIVE CONTROL  0.8B arms differ from their 2B namesakes: {len(diff)}/{len(KS)} -> "
          f"{'PASS' if len(diff) == len(KS) else 'FAIL'}")
    if len(diff) != len(KS): return 0

    ib = np.random.default_rng(31337).integers(0, len(pids), (NBOOT, len(pids)))
    def contrast(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))

    print(f"\n  {'k':>4}{'advantage over per-prompt random @k':>38}{'spread':>9}{'95% CI':>24}")
    rows, ok = {}, True
    for k in KS + ["all"]:
        sat = FULL8 if k == "all" else ARMS[k]
        base = a2(sat)
        effs, cis = [], None
        for seed in (0, 1, 2):
            rng = np.random.default_rng(9000 + seed)
            idx = {}
            for p in pids:
                avail = sorted({i for i, _ in FULL8[p]})
                kk = len({i for i, _ in sat[p]}) if k != "all" else len(avail)
                idx[p] = [avail[t] for t in rng.choice(len(avail), size=min(kk, len(avail)),
                                                       replace=False)]
            c = contrast(base, a2(FULL8, idx)); effs.append(c[0])
            if seed == 0: cis = c[1:]
        m, sd = float(np.mean(effs)), float(np.std(effs))
        rows[str(k)] = {"adv": m, "spread": sd, "ci_seed0": list(cis)}
        if k != "all" and m <= 0: ok = False
        print(f"  {str(k):>4}{m:>+38.4f}{sd:>9.4f}   [{cis[0]:+.4f}, {cis[1]:+.4f}]")

    nc = abs(rows["all"]["adv"]) < 1e-9
    print(f"\n  NEGATIVE CONTROL (forced)  k=all advantage must be exactly 0: "
          f"{rows['all']['adv']:+.6f} -> {'PASS' if nc else 'FAIL'}")
    if not nc:
        print("  -> the construction is indicted; UNVERIFIED."); return 0
    mono = all(rows[str(KS[i])]["adv"] >= rows[str(KS[i+1])]["adv"] for i in range(len(KS)-1))
    world = "A" if ok else "B"
    print(f"  monotone decay across k={KS}: {mono}")
    print(f"  WORLD {world} -- " +
          ("the dose curve survives the judge change: weight-reading's value is a fact about "
           "SELECTION" if world == "A" else "the curve does not survive; R533 was judge-specific"))
    print(f"  ⚠ coval_core has no 0.8B artifact, so the RELEASED core's curve position is "
          f"unreplicated -- the one admitted arm this round cannot place.")

    out = pathlib.Path(__file__).parent / "results/dose_curve_08b.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "monotone": bool(mono), "world": world,
                               "n_prompts": len(pids)}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
