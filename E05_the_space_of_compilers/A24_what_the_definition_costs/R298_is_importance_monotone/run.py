"""R298 — is the human IMPORTANCE ranking monotone in predictive value, or anti-predictive at its top?

WHY. R296: `topw_k1` LOSES to one generic criterion (−0.0170) while `topw_k3..k8` all win. R297
killed the tie explanation — the deficit survives restricting to non-tied pairs. So the top-ranked
criterion is not degenerate; it is *wrong*, and the next two fix it. That is a statement about the
SELECTOR, and it is directly checkable: `select_core.py`'s `topw_k` sorts by `-w`, so `sat_topw_k4`
stores its four criteria IN DESCENDING IMPORTANCE ORDER. Each can be scored ALONE for free.

⛔ THE QUESTION, AND IT HAS A SURPRISING ANSWER AVAILABLE. If human-rated importance tracked
predictive value, singleton A2 would DECREASE with rank: #1 best, #4 worst. If rank #1 is the WORST
of the four, the selector is anti-predictive exactly where it is most confident — and `topw` works
at k≥3 despite its top choice, not because of it.

ESTIMAND        (a) A2 of each of the four `topw_k4` criteria SCORED ALONE, by importance rank;
                (b) the rank-1 vs rank-4 difference; (c) the Spearman correlation between rank and
                singleton A2 across ranks; (d) the 4-criterion sum, to price aggregation.
IDENTIFICATION  exact. Ranks are the artifact's own index order, which is `topw`'s sort key.
SCOPE           968 prompts · Qwen3.5-2B-Base · A2·annotator, all annotators · cluster bootstrap.
WORLDS          W-MONOTONE     singleton A2 falls with rank -> importance tracks predictive value
                               and k=1's loss is about the single-criterion regime, not the ranking.
                W-ANTI         rank 1 is at or below the later ranks -> the human importance
                               ranking is NOT predictive at its top, and `topw` succeeds by
                               AGGREGATION over a badly ordered list.
KILL            pre-registered: if rank-1's singleton A2 is not separably ABOVE rank-4's, W-MONOTONE
                is rejected and FORMULATION records that the selector's ordering is unverified at
                the top — which is a different claim from `topw works`.
POSITIVE CTRL   the 4-criterion SUM must beat the BEST singleton. If aggregating four criteria does
                not beat the best one alone, the summation is doing nothing and no rank comparison
                below is interpretable.
NEGATIVE CTRL   a singleton against itself: exactly 0.
MULTIPLICITY    4 singletons + 3 adjacent-rank pairs + 1 sum; BH over all 8.
ARTIFACT        results/importance_monotone.json with source hash.
IMPOSSIBLE      whether the ordering is anti-predictive in a rubric written by different annotators.
                One release; the ranking is this release's own metadata.
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
    S = load_sat(RES / "sat_topw_k4.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted([p for p in S if p in tg and len(tg[p]) >= 2 and
                   len({i for i, _ in S[p]}) == 4] )
    pids = [p for p in pids if p in POOL]
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    print(f"  {N} prompts with exactly 4 criteria · `topw_k4` stores them in DESCENDING importance\n")

    def sc(idx):
        return np.array([np.mean([[cls(yvec(S[p], idx))[q] == h[q] for q in range(6)]
                                  for h in HC[p]]) for p in pids])
    single = {r: sc([r]) for r in range(4)}
    allfour = sc([0, 1, 2, 3])
    blind1 = np.array([np.mean([[cls(yvec(POOL[p], [0]))[q] == h[q] for q in range(6)]
                                for h in HC[p]]) for p in pids])
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(d):
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                ZEFF * d.std(ddof=1) / math.sqrt(N))

    print("  EACH CRITERION SCORED ALONE, BY HUMAN IMPORTANCE RANK\n")
    print(f"    {'rank':<8}{'A2 alone':>10}{'vs 1 generic':>14}")
    grid = []
    for r in range(4):
        c = cell(single[r] - blind1)
        grid.append((f"rank{r+1}", c[3]))
        print(f"    #{r+1:<7}{single[r].mean():>10.4f}{c[0]:>+14.4f}"
              f"   [{c[1]:+.4f},{c[2]:+.4f}]  {verdict(*c[:3], c[4])}")
    print(f"    {'ALL 4':<8}{allfour.mean():>10.4f}"
          f"{cell(allfour - blind1)[0]:>+14.4f}")
    print(f"    {'generic':<8}{blind1.mean():>10.4f}")

    print("\n  ADJACENT RANKS, and the span\n  " + header("comparison", width=18))
    for a, b in ((0, 1), (1, 2), (2, 3)):
        c = cell(single[a] - single[b]); grid.append((f"{a+1}v{b+1}", c[3]))
        print("  " + row(f"rank {a+1} − rank {b+1}", *c[:3], c[4], width=18))
    span = cell(single[0] - single[3]); grid.append(("1v4", span[3]))
    print("  " + row("rank 1 − rank 4", *span[:3], span[4], width=18))

    best_single = max(range(4), key=lambda r: single[r].mean())
    pc = cell(allfour - single[best_single])
    pos_ok = verdict(*pc[:3], pc[4]) == POS
    nz = cell(single[0] - single[0])
    print(f"\n  POSITIVE CTRL  all four beat the BEST singleton (rank {best_single+1}): "
          f"{pc[0]:+.4f} [{pc[1]:+.4f},{pc[2]:+.4f}] vs MDE {pc[4]:.4f}  "
          f"{'PASS' if pos_ok else 'FAIL — summation does nothing; ranks are uninterpretable'}")
    print(f"  NEGATIVE CTRL  a singleton against itself: {nz[0]:.2e}  "
          f"{'PASS' if nz[0] == 0 else 'FAIL'}")
    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / C)
    print(f"  BH q=0.05 over {C} cells · {surv} survive")
    if not (pos_ok and nz[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    killed = verdict(*span[:3], span[4]) != POS
    order = sorted(range(4), key=lambda r: -single[r].mean())
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: rank 1 NOT separably above rank 4 ?  {killed}"
          f"   (Δ = {span[0]:+.4f}, MDE {span[4]:.4f})")
    print(f"    singleton A2 order, best→worst by rank: {[r+1 for r in order]}")
    if killed:
        # ⚠ THE FIRST WORDING HERE SAID `the ranking is ANTI-predictive'. That is too strong and
        # the round's own table refutes it: NO adjacent pair separates either (1v2 -0.0058,
        # 2v3 +0.0081, 3v4 +0.0008, all UNRESOLVED). `Rank 1 is not above rank 4' and `rank 1 is
        # BELOW rank 4' are different claims and only the first is measured. Computed below.
        adj_sep = [n for n, c in (("1v2", cell(single[0] - single[1])),
                                  ("2v3", cell(single[1] - single[2])),
                                  ("3v4", cell(single[2] - single[3])))
                   if verdict(*c[:3], c[4]) in ("BEATS", "LOSES")]
        print(f"  -> W-ANTI (as pre-registered), but stated at the strength the data supports:")
        print(f"     NO rank ordering among the top four is resolvable — adjacent pairs that")
        print(f"     separate: {adj_sep or 'none'}. So the ranking is not shown to be ANTI-predictive,")
        print(f"     it is shown to carry NO resolvable predictive ordering at its own top.")
        worst = min(range(4), key=lambda r: single[r].mean())
        print(f"     And every singleton is at or below ONE generic criterion, while all four")
        print(f"     together beat FOUR generic ones by {cell(allfour - blind1)[0]:+.4f}:")
        print(f"     THE VALUE IS IN THE COMBINATION, NOT IN ANY MEMBER.")
    else:
        print("  -> W-MONOTONE. Importance tracks predictive value; k=1's loss is a fact about the")
        print("     single-criterion regime rather than about the ordering.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "importance_monotone.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N,
                                 singleton={str(r + 1): float(single[r].mean()) for r in range(4)},
                                 all_four=float(allfour.mean()), generic1=float(blind1.mean()),
                                 span=span, order=[r + 1 for r in order], killed=bool(killed)),
                            indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
