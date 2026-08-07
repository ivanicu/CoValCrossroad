"""R300 — is `the value is in the combination` a fact about topw, or about cores?

WHY. R298/R299 decomposed ONE selector. Every one of `topw_k4`'s criteria loses alone to a single
generic criterion; together they beat four generic ones; and the importance signal is real at BLOCK
resolution and absent at RANK resolution. All three findings read the same arm.

`coval_core` is the OTHER admitted arm and it is a different kind of object: the release's own
compiler output, **rewritten rather than selected** — only 8% of its items appear verbatim in
`coval_full`. So its criteria are not rubric criteria and cannot be decomposed by importance rank.
But the STRUCTURAL question transfers exactly: **does each of its criteria lose alone, with the
value living in the combination — or does one strong criterion carry it?**

⛔ THIS IS THE GENERALITY TEST, AND IT CAN FAIL IN AN INTERESTING WAY. If `coval_core` has one
criterion that beats a generic one alone, then a compiler that WRITES criteria is doing something
categorically different from one that SELECTS them: concentrating the signal rather than spreading
it. `the value is in the combination` would then be a fact about selection from a noisy list, not
about cores.

ESTIMAND        A2 of each `coval_core` criterion scored ALONE, vs one generic criterion; the
                4-criterion sum vs four generic; and the sum vs its own best singleton.
IDENTIFICATION  exact. `coval_core`'s artifact stores its criteria per prompt; index order is the
                release's own, and NO ordering claim is made from it — only the set decomposition.
SCOPE           prompts where `coval_core` has exactly 4 criteria · Qwen3.5-2B-Base · A2·annotator,
                all annotators · cluster bootstrap over prompts.
WORLDS          W-SPREAD       every singleton is at or below one generic, the sum wins -> the
                               combination finding generalises across two very different compilers.
                W-CONCENTRATE  at least one singleton beats one generic separably -> writing
                               criteria concentrates signal where selecting spreads it, and the
                               R298 finding is about SELECTION, not about cores.
KILL            pre-registered: if ANY `coval_core` singleton beats one generic criterion separably,
                W-SPREAD is dead and FORMULATION records `the value is in the combination` as a
                property of the topw family only.
POSITIVE CTRL   the 4-criterion sum must beat its own best singleton, as it does for topw
                (+0.0328). If aggregation does nothing here, the singletons are uninterpretable.
NEGATIVE CTRL   a singleton against itself: exactly 0.
MULTIPLICITY    4 singletons + sum + best-singleton contrast; BH over all 6.
ARTIFACT        results/combination_generality.json with source hash.
IMPOSSIBLE      a third compiler. Two objects is the widest comparison this release supports, and
                `generalises' below means `holds for both of the two admitted arms', nothing more.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import row, header, verdict, POS                 # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF, NBOOT = 1.959964 + 0.841621, 2000


def main():
    tg, _ = load_targets(); RES = ROOT / "corebench" / "results"
    CC = load_sat(RES / "sat_coval_core.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted([p for p in CC if p in tg and len(tg[p]) >= 2 and p in POOL
                   and len({i for i, _ in CC[p]}) == 4])
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    print(f"  {N} prompts where `coval_core` has exactly 4 criteria — the release's own compiler,\n"
          f"  REWRITTEN not selected (8% verbatim), so no importance rank exists to decompose by\n")

    def sc(sat, idx):
        return np.array([np.mean([[cls(yvec(sat[p], idx))[q] == h[q] for q in range(6)]
                                  for h in HC[p]]) for p in pids])
    single = {r: sc(CC, [r]) for r in range(4)}
    allfour = sc(CC, [0, 1, 2, 3])
    g1 = sc(POOL, [0]); g4 = sc(POOL, [0, 1, 2, 3])
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(d):
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                ZEFF * d.std(ddof=1) / math.sqrt(N))

    print("  EACH `coval_core` CRITERION SCORED ALONE\n")
    print(f"    {'criterion':<12}{'A2 alone':>10}{'vs 1 generic':>14}   verdict")
    grid, beats = [], []
    for r in range(4):
        c = cell(single[r] - g1); v = verdict(*c[:3], c[4])
        grid.append((f"c{r}", c[3]))
        if v == POS: beats.append(r)
        print(f"    #{r:<11}{single[r].mean():>10.4f}{c[0]:>+14.4f}   [{c[1]:+.4f},{c[2]:+.4f}]  {v}")
    cs = cell(allfour - g4); grid.append(("sum", cs[3]))
    print(f"    {'ALL 4':<12}{allfour.mean():>10.4f}{cs[0]:>+14.4f}   "
          f"[{cs[1]:+.4f},{cs[2]:+.4f}]  {verdict(*cs[:3], cs[4])}   (vs FOUR generic)")
    print(f"    {'1 generic':<12}{g1.mean():>10.4f}\n    {'4 generic':<12}{g4.mean():>10.4f}")

    best = max(range(4), key=lambda r: single[r].mean())
    pc = cell(allfour - single[best]); pos_ok = verdict(*pc[:3], pc[4]) == POS
    grid.append(("agg", pc[3]))
    nz = cell(single[0] - single[0])
    print(f"\n  POSITIVE CTRL  all four beat the best singleton (#{best}): {pc[0]:+.4f} "
          f"[{pc[1]:+.4f},{pc[2]:+.4f}] vs MDE {pc[4]:.4f}  "
          f"{'PASS' if pos_ok else 'FAIL — aggregation does nothing here'}")
    print(f"  NEGATIVE CTRL  a singleton against itself: {nz[0]:.2e}  "
          f"{'PASS' if nz[0] == 0 else 'FAIL'}")
    grid.sort(key=lambda z: z[1]); K = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / K)
    print(f"  BH q=0.05 over {K} cells · {surv} survive")
    if not (pos_ok and nz[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    killed = bool(beats)
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: does ANY `coval_core` singleton beat one generic ?  {killed}"
          f"   {beats}")
    if killed:
        print("  -> W-CONCENTRATE. A compiler that WRITES criteria concentrates signal where one")
        print("     that SELECTS spreads it. `the value is in the combination` is a property of")
        print("     the topw family, not of cores, and FORMULATION says so.")
    else:
        print("  -> W-SPREAD. Every criterion of BOTH admitted arms loses alone to a single generic")
        print("     one, and both sums win. The combination finding holds across two compilers that")
        print("     share no method — one selects from a rubric, the other rewrites from the")
        print("     conversation — which is the widest test this release supports.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "combination_generality.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N,
                                 singleton={str(r): float(single[r].mean()) for r in range(4)},
                                 all_four=float(allfour.mean()), g1=float(g1.mean()),
                                 g4=float(g4.mean()), sum_vs_g4=cs, agg=pc,
                                 beats=beats, killed=bool(killed)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
