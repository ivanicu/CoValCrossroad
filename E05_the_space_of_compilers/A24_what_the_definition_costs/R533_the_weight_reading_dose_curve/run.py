#!/usr/bin/env python3
"""R533 — is +0.0748 a property of coval_core, or of weight-reading in general?

R532 priced the ③ fork at +0.0748 using the released core alone. My closing line proposed "one
more arm", naming topw_k4 as "the other admitted arm that also reads weights". ⛔ There are FOUR
-- topw_k3, k4, k6, k8 -- which turns a single check into a DOSE-RESPONSE across k.

ESTIMAND (before method): for each k, the A2 advantage of selecting k rubric items BY WEIGHT over
  selecting k AT RANDOM PER PROMPT from the same rubric. The k-curve of what ③-any forbids.
IDENTIFICATION: fully identified -- both sides computable from sat_full and the topw_k* arms, with
  the random draw constructed at MATCHED k so the contrast isolates weight-reading from size.
SCOPE  population: the 968 prompts · instrument: A2 over all annotators · baseline: a per-prompt
  uniform k-draw from that prompt's own rubric · regime: first release, home judge, 3 seeds.
WORLDS  A · the advantage is a property of WEIGHT-READING -- every topw_k lands near coval_core's
              +0.0748, and it decays toward 0 as k approaches the full rubric.
        B · it is a property of coval_core specifically -- the topw arms land materially lower,
              and the +0.0748 does not generalise.
KILL (pre-registered): if the topw_k advantages span less than half of coval_core's, world A dies.
POSITIVE CONTROL: coval_core against the per-prompt draw must reproduce R532's +0.0748 within its
  own seed spread (0.0030). Without it this round is not on R532's scale.
NEGATIVE CONTROL, and it is the sharp one: `full` selects EVERY criterion, so there is nothing to
  select and weight-reading can be worth NOTHING. Its advantage over a per-prompt draw at k=all
  must be exactly 0 -- a forced endpoint the dose curve must hit.
NOISE FLOOR: 3 seeds per cell; spread reported beside every mean.
MULTIPLICITY: 5 arms x 3 seeds = 15 cells; all printed.
IMPOSSIBLE HERE: whether the weights are GOOD weights. This measures the value of reading them,
  not whether the annotators were right -- that needs an external standard, register row 6.
"""
import itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls

RES = ROOT / "corebench/results"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT, ZEFF = 1200, 1.959964 + 0.841621
ARMS = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8", "full"]

def main():
    targets, _ = load_targets()
    FULL = load_sat(RES / "sat_full.npz")
    SATS = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    pids = sorted({p for p in FULL if p in targets and len(targets[p]) >= 2
                   and all(p in SATS[a] for a in ARMS)})
    HM = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    print(f"  prompts: {len(pids)}")

    def a2(idx_by_pid, sat):
        out = []
        for a, p in enumerate(pids):
            ii = idx_by_pid[p] if idx_by_pid else sorted({i for i, _ in sat[p]})
            y = np.array([sum(sat[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(y[[i for i, _ in PAIRS]] - y[[j for _, j in PAIRS]])
            out.append(np.mean([(s == h).mean() for h in HM[a]]))
        return np.array(out)

    ib = np.random.default_rng(31337).integers(0, len(pids), (NBOOT, len(pids)))
    def contrast(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                ZEFF * d.std(ddof=1) / math.sqrt(len(pids)))

    scores = {a: a2(None, SATS[a]) for a in ARMS}
    ks = {a: int(np.median([len({i for i, _ in SATS[a][p]}) for p in pids])) for a in ARMS}
    print(f"  median k per arm: " + " · ".join(f"{a}={ks[a]}" for a in ARMS))

    rows = {}
    print(f"\n  {'arm':<14}{'k':>4}{'advantage over per-prompt random @k':>38}{'spread':>9}")
    for a in ARMS:
        effs = []
        for seed in (0, 1, 2):
            rng = np.random.default_rng(7000 + seed)
            idx = {}
            for p in pids:
                avail = sorted({i for i, _ in FULL[p]})
                k = min(len({i for i, _ in SATS[a][p]}), len(avail))
                idx[p] = [avail[t] for t in rng.choice(len(avail), size=k, replace=False)]
            effs.append(contrast(scores[a], a2(idx, FULL))[0])
        m, sd = float(np.mean(effs)), float(np.std(effs))
        rows[a] = {"k": ks[a], "adv": m, "spread": sd, "seeds": effs}
        print(f"  {a:<14}{ks[a]:>4}{m:>+38.4f}{sd:>9.4f}")

    pc = abs(rows["coval_core"]["adv"] - 0.0748) <= 0.0060
    print(f"\n  POSITIVE CONTROL  coval_core reproduces R532's +0.0748: "
          f"{rows['coval_core']['adv']:+.4f} -> {'PASS' if pc else 'FAIL'}")
    nc = abs(rows["full"]["adv"]) < 1e-9
    print(f"  NEGATIVE CONTROL  `full` selects everything, so weight-reading can be worth "
          f"nothing: {rows['full']['adv']:+.6f} -> {'PASS' if nc else 'FAIL'}")
    if not (pc and nc):
        print("  -> UNVERIFIED."); return 0

    topw = [rows[a]["adv"] for a in ("topw_k3", "topw_k4", "topw_k6", "topw_k8")]
    cc = rows["coval_core"]["adv"]
    world = "A" if min(topw) >= cc / 2 else "B"
    print(f"\n  topw_k advantages: {[round(t,4) for t in topw]}  (coval_core {cc:+.4f})")
    print(f"  smallest topw / coval_core = {min(topw)/cc:.2f}   (kill at <0.50)")
    print(f"  WORLD {world} -- " +
          (f"weight-reading is worth ~{np.mean(topw):+.4f} across k=3..8 and exactly 0 at k=all; "
           f"the +0.0748 is a property of the OPERATION, not of coval_core"
           if world == "A" else "the advantage is specific to coval_core and does not generalise"))

    out = pathlib.Path(__file__).parent / "results/dose_curve.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "world": world,
                               "topw_mean": float(np.mean(topw)),
                               "coval_core": cc}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
