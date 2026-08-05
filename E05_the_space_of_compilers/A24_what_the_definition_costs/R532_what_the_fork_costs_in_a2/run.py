#!/usr/bin/env python3
"""R532 — price the ③ fork: what is weight-reading worth, against a TRUE per-prompt random draw?

R529 forked ③. ③-any forbids reading the rubric's annotator-assigned weights; ③-rank permits it.
The fork's cost is the value of that operation. The census already contains a number for it --
coval_core's clause-① contrast, +0.0738 against random_k4_s0 -- but R531 found random_k4_s0 uses
the SAME criterion indices for every prompt. It is one random draw reused, not a per-prompt draw.

⚠ And my last closing line proposed auditing that comparator "because clause one compares every
arm against it". Clause ① was RETIRED eight rounds ago (R516/R519). The comparator still matters,
but for this reason instead.

ESTIMAND (before method): the A2 advantage of selecting 4 rubric items BY WEIGHT over selecting 4
  AT RANDOM PER PROMPT -- i.e. what ③-any forbids, priced.
IDENTIFICATION: fully identified. Both sides are computable from sat_full (all criteria) and the
  released core; the per-prompt random draw is constructed here rather than reused.
SCOPE  population: the 968 prompts · instrument: A2 over all annotators · baseline: a per-prompt
  uniform 4-draw from THAT prompt's own rubric · regime: first release, home judge, 3 seeds.
WORLDS  A · the advantage survives against a true per-prompt draw, so +0.0738 was a fair price
              and the fork is expensive.
        B · it shrinks materially, so the published figure was inflated by a fixed-index
              comparator and the fork costs less than the record says.
KILL (pre-registered): if the per-prompt advantage falls below half of +0.0738, world A dies.
POSITIVE CONTROL: the FIXED-index comparator must reproduce R294's stored c1 for coval_core to
  1e-6. Without it the two comparators are not on one scale and the difference means nothing.
NEGATIVE CONTROL: the per-prompt draw must actually vary -- assert the index set differs across
  prompts, which is exactly what random_k4_s0 fails.
NOISE FLOOR: 3 seeds for the per-prompt draw; the spread is reported beside the mean.
MULTIPLICITY: 2 comparators x 3 seeds; all cells printed.
IMPOSSIBLE HERE: whether ③-any is the right reading. That is register row 7, a decision about
  purpose. This round prices the choice; it does not make it.
"""
import itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls

RES = ROOT / "corebench/results"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT, ZEFF = 1200, 1.959964 + 0.841621

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    targets, _ = load_targets()
    FULL = load_sat(RES / "sat_full.npz")
    CORE = load_sat(RES / "sat_coval_core.npz")
    FIX  = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in CORE if p in targets and p in FULL and p in FIX
                   and len(targets[p]) >= 2})
    HM = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    print(f"  prompts: {len(pids)}")

    def a2_from(sat, idx_by_pid=None):
        out = []
        for a, p in enumerate(pids):
            ii = idx_by_pid[p] if idx_by_pid else sorted({i for i, _ in sat[p]})
            y = np.array([sum(sat[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(y[[i for i, _ in PAIRS]] - y[[j for _, j in PAIRS]])
            out.append(np.mean([(s == h).mean() for h in HM[a]]))
        return np.array(out)

    core = a2_from(CORE)
    fixv = a2_from(FIX)
    ib = np.random.default_rng(31337).integers(0, len(pids), (NBOOT, len(pids)))
    def contrast(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                ZEFF * d.std(ddof=1) / math.sqrt(len(pids)))

    c_fix = contrast(core, fixv)
    stored = cen["coval_core"]["c1"][0]
    ok = abs(c_fix[0] - stored) <= 1e-6
    print(f"  POSITIVE CONTROL  fixed-index contrast {c_fix[0]:+.6f} vs R294's stored c1 "
          f"{stored:+.6f} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  -> comparators not on one scale; UNVERIFIED."); return 0

    # NEGATIVE CONTROL: the per-prompt draw must vary
    rows, means = {}, []
    for seed in (0, 1, 2):
        rng = np.random.default_rng(5000 + seed)
        idx = {}
        for p in pids:
            avail = sorted({i for i, _ in FULL[p]})
            k = min(4, len(avail))
            idx[p] = [avail[t] for t in rng.choice(len(avail), size=k, replace=False)]
        if seed == 0:
            first = set(idx[pids[0]]); varies = any(set(idx[p]) != first for p in pids[1:])
            print(f"  NEGATIVE CONTROL  the per-prompt draw actually varies: {varies} -> "
                  f"{'PASS' if varies else 'FAIL'}   (random_k4_s0 varies: False -- R531)")
            if not varies: return 0
        pv = a2_from(FULL, idx)
        c = contrast(core, pv)
        rows[f"seed{seed}"] = {"eff": c[0], "lo": c[1], "hi": c[2], "mde": c[3],
                               "baseline_a2": float(pv.mean())}
        means.append(c[0])
        print(f"    seed {seed}: baseline A2 {pv.mean():.4f} · advantage {c[0]:+.4f} "
              f"[{c[1]:+.4f}, {c[2]:+.4f}] · mde {c[3]:.4f}")

    m, sd = float(np.mean(means)), float(np.std(means))
    world = "A" if m >= stored / 2 else "B"
    print(f"\n  fixed-index comparator (published): {stored:+.4f}")
    print(f"  TRUE per-prompt draw, 3 seeds     : {m:+.4f}  (spread {sd:.4f})")
    print(f"  ratio to the published figure     : {m/stored:.2f}x   (kill at <0.50x)")
    print(f"  WORLD {world} -- " +
          (f"the advantage survives a per-prompt draw, so ③-any forbids an operation worth "
           f"{m:+.4f} in A2" if world == "A" else
           "the published figure was inflated by the fixed-index comparator"))

    out = pathlib.Path(__file__).parent / "results/fork_price.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"published_fixed_index": stored, "per_prompt_mean": m,
                               "per_prompt_sd": sd, "ratio": m/stored, "seeds": rows,
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
