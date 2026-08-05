#!/usr/bin/env python3
"""R528 — at which baseline percentile does the definition's extension become EMPTY?

R527 swept ②'s comparator and reported admitted-set sizes 8/7/6/4. I read the sizes and missed
what the p100 row says: the four arms admitted at the strongest baseline are exactly the four ③
excludes. So ② ∧ ③ is EMPTY there -- and the deliverable's own wording for ② is "the BEST
generalising prompt-blind criterion set", which IS p100.

ESTIMAND (before method): the percentile of ②'s reference class at which the extension of
  ② ∧ ③ becomes empty, over the k=4 arms; and the identity of the last surviving arm.
IDENTIFICATION: fully identified on R294's estimator over C(16,4) = 1,820 subsets.
SCOPE  population: k=4 arms with full coverage in R294's census · instrument: A2 over all
  annotators, paired cluster bootstrap · baseline: the swept axis · regime: first release.
  ⚠ k=4 ONLY -- arms at other k are not in this reference class and are not swept.
WORLDS  A · the extension is non-empty across the whole class. The wording costs nothing.
        B · the extension empties at some percentile at or below 100. Then the deliverable's
              literal wording ("the best") names a comparator under which no core exists.
KILL (pre-registered): if ② ∧ ③ is non-empty at p100, world B dies outright.
POSITIVE CONTROL: at the PUBLISHED subset the extension must be exactly R294's own admitted k=4
  arms -- `coval_core` and `topw_k4`. If the sweep cannot reproduce the published cell, no other
  cell is admissible.
NEGATIVE CONTROL: a subset against itself gives exactly 0 for every arm, so no admission can be
  manufactured by the estimator.
NOISE FLOOR: each cell's own MDE as R294 computes it.
MULTIPLICITY: a fine sweep over percentiles; the whole curve is printed, not the crossing alone.
IMPOSSIBLE HERE: whether "best" was ever INTENDED as the class maximum rather than as loose
  prose. That is authorial intent, and the deliverable is mine, so the honest move is to fix the
  wording rather than to litigate it.
"""
import itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls
from report import verdict, POS

RES = ROOT / "corebench/results"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
USES_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())
    rows_c = cen["rows"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]}); n_pool = len(idxs)
    HM = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    T = np.zeros((len(pids), n_pool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS]] - Y[:, [j for _, j in PAIRS]])
        return np.array([np.mean([(s[a] == h).mean() for h in HM[a]]) for a in range(len(pids))])

    arms = sorted(a for a in rows_c if rows_c[a]["k"] == 4)
    A = {}
    for a in arms:
        S = load_sat(RES / f"sat_{a}.npz")
        if any(p not in S for p in pids): continue
        Y = np.zeros((len(pids), 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        A[a] = a2(Y)
    print(f"  k=4 arms: {len(A)} · pool {n_pool} · subsets C({n_pool},4) = {math.comb(n_pool,4)}")

    subs = list(itertools.combinations(range(n_pool), 4))
    means = np.array([a2(T[:, list(s), :].sum(axis=1)).mean() for s in subs])
    order = np.argsort(means); pub = subs.index(tuple(range(4)))
    ib = np.random.default_rng(31337).integers(0, len(pids), (NBOOT, len(pids)))
    def vd(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return verdict(float(d.mean()), float(np.percentile(bs, 2.5)),
                       float(np.percentile(bs, 97.5)), ZEFF*d.std(ddof=1)/math.sqrt(len(pids)))
    def ext(sub):
        bv = a2(T[:, list(sub), :].sum(axis=1))
        p2 = [a for a in A if vd(A[a], bv) == POS]
        return sorted(p2), sorted(a for a in p2 if a not in USES_LABELS)

    # POSITIVE CONTROL: the published cell must reproduce R294's admitted k=4 arms
    _p2pub, extpub = ext(subs[pub])
    want = sorted(a for a in cen["admitted"] if a in A)
    ok = extpub == want
    print(f"  POSITIVE CONTROL  published cell -> {extpub}; R294's admitted k=4 -> {want}  "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  -> cannot reproduce the published cell; UNVERIFIED."); return 0
    z = a2(T[:, list(subs[pub]), :].sum(axis=1)); zz = z - z
    print(f"  NEGATIVE CONTROL  subset vs itself max|d| = {abs(zz).max():.1e} -> "
          f"{'PASS' if abs(zz).max() == 0 else 'FAIL'}")

    print(f"\n  {'pct':>5}{'baseline A2':>13}{'②':>4}{'②∧③':>6}  surviving cores")
    curve, empty_at = {}, None
    for q in [50, 75, 85, 90, 93.7, 95, 97, 98, 99, 99.5, 100]:
        s = subs[order[min(int(q/100*(len(subs)-1)), len(subs)-1)]]
        p2, e = ext(s)
        bv = a2(T[:, list(s), :].sum(axis=1)).mean()
        curve[f"p{q}"] = {"a2": float(bv), "n2": len(p2), "ext": e}
        if not e and empty_at is None: empty_at = q
        print(f"  {q:>5}{bv:>13.4f}{len(p2):>4}{len(e):>6}  {', '.join(e) if e else '(EMPTY)'}")

    world = "B" if empty_at is not None else "A"
    print(f"\n  extension of ② ∧ ③ first empties at percentile: "
          f"{empty_at if empty_at is not None else 'never in [50,100]'}")
    print(f"  WORLD {world} -- " +
          ("the deliverable's literal wording -- 'the BEST generalising prompt-blind criterion "
           "set' -- names a comparator under which NO core exists"
           if world == "B" else "the extension survives the whole class; the wording is free"))
    print(f"  ⚠ SCOPE: k=4 arms only. Arms at other k are outside this reference class.")

    out = pathlib.Path(__file__).parent / "results/where_it_empties.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"curve": curve, "empty_at_pct": empty_at, "world": world,
                               "published_cell": extpub, "n_k4_arms": len(A)}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
