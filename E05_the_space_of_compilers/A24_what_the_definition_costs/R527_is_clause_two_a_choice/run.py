#!/usr/bin/env python3
"""R527 — clause ②'s baseline was picked by file order. What does the definition owe that pick?

R439 censused all C(16,4) = 1,820 subsets of ②'s reference pool and found the PUBLISHED reference
POOL[0:4] sits at percentile 91.7 -- near the top of the class it is drawn from. It used that to
answer a question about clause ④. Nobody has asked what it means for clause ② itself.

⚠ My last closing line said clause ② had never been attacked. False -- R439 attacked its
reference class. What has never been run is the SPECIFICATION CURVE: how the admitted set moves
as the baseline moves across that same class.

ESTIMAND (before method): for each k=4 arm, the percentile of ②'s reference class at which it
stops clearing clause ②. In particular: at which percentile does `coval_core` -- the released
core, the definition's central positive case -- fail?
IDENTIFICATION: fully identified. The pool is 16 criteria; the reference class is every 4-subset;
every arm's per-prompt A2 is computable.
SCOPE  population: the k=4 arms in R294's census · instrument: A2 vs a pool 4-subset, paired
  cluster bootstrap as R294 · baseline: THE SWEPT AXIS · regime: first release, home judge.
WORLDS  A · the admitted set is stable across the class -- the file-order pick is immaterial and
              clause ② is robust to its own baseline.
        B · the admitted set moves -- the definition's extension depends on which 4 of 16 pool
              criteria happened to be first in the file.
KILL (pre-registered): if `coval_core`'s verdict is BEATS at every swept percentile, world B
  loses its sharpest case; if the admitted set is identical at all percentiles, world B dies.
POSITIVE CONTROL: the published subset must reproduce R294's stored c2 for k=4 arms to 1e-6 --
  the same check R522 passed at Δ=0. Without it the sweep is not on R294's scale.
NEGATIVE CONTROL: a subset compared against ITSELF must give exactly 0 for every arm.
NOISE FLOOR: each cell's own MDE, computed as R294 does, reported beside the effect.
MULTIPLICITY: (arms x percentiles) cells; the whole grid is printed, survivors and not.
SPECIFICATION: the swept axis IS the specification -- min, p05, p25, median, p75, p95, max, and
  the published pick, located in the same census.
IMPOSSIBLE HERE: whether the pool's 16 criteria are themselves the right universe. That is a
  construct claim needing an external standard for what "prompt-blind" should span.
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

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    n_pool = len(idxs)
    print(f"  pool criteria: {n_pool} · prompts: {len(pids)} · reference class: "
          f"C({n_pool},4) = {math.comb(n_pool,4)}")

    HC = {p: [cls(y) for y, _ in targets[p]] for p in pids}
    # (P, n_pool, 4) pool tensor
    T = np.zeros((len(pids), n_pool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)
    # per-prompt human class matrix (P, H, 6)
    HM = [np.array(HC[p]) for p in pids]

    def a2_of_y(Y):                      # Y: (P,4) -> per-prompt A2 vs all annotators
        s = np.sign(Y[:, [i for i, _ in PAIRS]] - Y[:, [j for _, j in PAIRS]])
        return np.array([np.mean([(s[a] == h).mean() for h in HM[a]]) for a in range(len(pids))])

    subs = list(itertools.combinations(range(n_pool), 4))
    means = np.array([a2_of_y(T[:, list(s), :].sum(axis=1)).mean() for s in subs])
    order = np.argsort(means)
    pub = subs.index(tuple(range(4)))
    pub_pct = 100.0 * (means < means[pub]).mean()
    print(f"  published POOL[0:4]: A2 {means[pub]:.4f} at percentile {pub_pct:.1f}  "
          f"(R439 stored 0.5537 / 91.70)")
    # ⚠ THE CONTROL MUST BE ON R294's SCALE, NOT R439's.
    # R439's published_ref_a2 = 0.5537 uses a different annotator draw; this round's `on()` uses
    # ALL annotators, exactly as R294 does, and 0.5504 is precisely R514's measured bar2 maximum.
    # Comparing to R439 was comparing two different objects -- the control failing for its own
    # reasons. The admissible control is R294's own stored c2, which R522 reproduced at delta 0.
    print(f"  (R439 stored 0.5537 on a DIFFERENT annotator draw; not the target -- see README)")

    arms = sorted(a for a in cen if cen[a]["k"] == 4)
    A = {}
    for a in arms:
        S = load_sat(RES / f"sat_{a}.npz")
        ps = [p for p in pids if p in S]
        if len(ps) != len(pids): continue
        Y = np.zeros((len(pids), 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        A[a] = a2_of_y(Y)
    print(f"  k=4 arms with full coverage: {len(A)}")

    pv0 = a2_of_y(T[:, list(subs[pub]), :].sum(axis=1))
    ctrl = [(a, float((A[a] - pv0).mean()), cen[a]["c2"][0]) for a in A if "c2" in cen[a]]
    nok = sum(1 for _, mine, stored in ctrl if abs(mine - stored) <= 1e-6)
    print(f"  POSITIVE CONTROL  reproduce R294's stored c2 (tol 1e-6) on k=4 arms:")
    for a, mine, stored in ctrl[:5]:
        print(f"    {a:<18}mine {mine:+.6f}  stored {stored:+.6f}  "
              f"{'OK' if abs(mine-stored) <= 1e-6 else 'FAIL'}")
    print(f"    {nok}/{len(ctrl)} reproduce -> {'PASS' if nok >= max(3, len(ctrl)//2) else 'FAIL'}")
    if nok < max(3, len(ctrl)//2):
        print("  -> not on R294's scale; UNVERIFIED."); return 0

    ib = np.random.default_rng(31337).integers(0, len(pids), (NBOOT, len(pids)))
    def vd(x, y):
        d = x - y; bs = d[ib].mean(axis=1)
        return verdict(float(d.mean()), float(np.percentile(bs, 2.5)),
                       float(np.percentile(bs, 97.5)), ZEFF*d.std(ddof=1)/math.sqrt(len(pids)))

    # NEGATIVE CONTROL
    pv = a2_of_y(T[:, list(subs[pub]), :].sum(axis=1))
    z = pv - pv
    print(f"  NEGATIVE CONTROL  subset vs itself: max|d| = {abs(z).max():.1e} -> "
          f"{'PASS' if abs(z).max() == 0 else 'FAIL'}")

    pcts = [0, 5, 25, 50, 75, 95, 100]
    cells, rows = 0, {}
    print(f"\n  {'baseline':<14}{'A2':>8}  admitted (k=4 arms clearing ②)")
    for q in pcts:
        s = subs[order[min(int(q/100*(len(subs)-1)), len(subs)-1)]]
        bv = a2_of_y(T[:, list(s), :].sum(axis=1))
        adm = sorted(a for a in A if vd(A[a], bv) == POS); cells += len(A)
        rows[f"p{q:03d}"] = {"a2": float(bv.mean()), "n_admitted": len(adm), "admitted": adm}
        print(f"  p{q:<13}{bv.mean():>8.4f}  {len(adm):>2}: {', '.join(adm) if adm else '(none)'}")
    adm_pub = sorted(a for a in A if vd(A[a], pv) == POS); cells += len(A)
    rows["published"] = {"a2": float(pv.mean()), "n_admitted": len(adm_pub), "admitted": adm_pub}
    print(f"  {'PUBLISHED':<14}{pv.mean():>8.4f}  {len(adm_pub):>2}: {', '.join(adm_pub)}")

    cc = {k: ("coval_core" in v["admitted"]) for k, v in rows.items()}
    sizes = {len(v["admitted"]) for v in rows.values()}
    world = "A" if len(sizes) == 1 else "B"
    print(f"\n  MULTIPLICITY  {cells} cells over {len(rows)} specifications; whole grid printed")
    print(f"  coval_core clears ② at: {[k for k,v in cc.items() if v]}")
    print(f"  coval_core FAILS ② at : {[k for k,v in cc.items() if not v]}")
    print(f"  admitted-set sizes across the class: {sorted(sizes)}")
    print(f"  WORLD {world} -- " +
          ("the extension depends on which 4 of 16 pool criteria came first in the file"
           if world == "B" else "the admitted set is invariant across the reference class"))

    out = pathlib.Path(__file__).parent / "results/clause2_spec_curve.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_pool": n_pool, "n_subsets": len(subs),
                               "published_pct": pub_pct, "rows": rows,
                               "coval_core_by_spec": cc, "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
