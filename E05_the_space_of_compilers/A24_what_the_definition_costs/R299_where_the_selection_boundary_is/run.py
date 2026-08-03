"""R299 — selection carries +0.0715 and ordering carries nothing. Where exactly is the boundary?

WHY. Two measured facts sit uneasily together:
  · `topw_k4` beats `random_k4` by +0.0715 — SELECTION by importance carries a lot.
  · No rank ordering among topw's own top four is resolvable (R298) — ORDERING carries nothing.
Both cannot be about the same quantity. If order within the selected set is uninformative, then all
the information is in the CUT: which criteria are inside the top-k and which are not. That is
directly testable and free — `sat_topw_k8` stores ranks 1–8 in descending importance, so **ranks 5–8
are their own k=4 arm** and have never been scored.

⛔ THE THREE WORLDS, and they make different predictions about one cell.
  W-CUT      the top-4 cut is where the information is -> ranks 1–4 beat ranks 5–8 separably, and
             ranks 5–8 sit near `random_k4`.
  W-BROAD    importance matters broadly but not finely -> ranks 5–8 beat `random_k4` too, and the
             1–4 vs 5–8 gap is small. Then `top-k` is not a threshold, it is a gradient.
  W-NEITHER  ranks 5–8 match ranks 1–4 -> the +0.0715 over random is NOT about importance at all,
             and something else about `random_k4`'s draw explains it.

ESTIMAND        A2 of ranks 1–4, ranks 5–8, all 8, and `random_k4`/`random_k8`, on one population;
                and the three contrasts 1–4 vs 5–8, 5–8 vs random_k4, 1–8 vs random_k8.
IDENTIFICATION  exact. Rank blocks are the artifact's own index order, which is topw's sort key.
SCOPE           prompts with >=8 usable criteria (topw_k8's own population) · Qwen3.5-2B-Base ·
                A2·annotator, all annotators · cluster bootstrap over prompts.
KILL            pre-registered: if ranks 5–8 do NOT beat `random_k4` separably, W-BROAD is dead and
                the importance signal is a THRESHOLD at the cut rather than a gradient. If they DO,
                `top-k` in the definition's admitted arms is doing less work than its name implies.
POSITIVE CTRL   ranks 1–8 must beat `random_k8` — the same comparison the definition already
                admits at k=8. If it does not reproduce on this population, the population is the
                problem and no contrast below is readable.
NEGATIVE CTRL   a rank block against itself: exactly 0.
MULTIPLICITY    5 arms + 3 contrasts; BH over the tested cells.
ARTIFACT        results/selection_boundary.json with source hash.
IMPOSSIBLE      whether the boundary sits at 4 specifically — the cut is confounded with k, and
                separating them needs top-j-of-8 for every j, which is one more sweep, not a
                measurement this round makes.
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
    S8 = load_sat(RES / "sat_topw_k8.npz")
    R4 = load_sat(RES / "sat_random_k4_s0.npz")
    R8 = load_sat(RES / "sat_random_k8_s0.npz")
    pids = sorted([p for p in S8 if p in tg and len(tg[p]) >= 2
                   and len({i for i, _ in S8[p]}) == 8 and p in R4 and p in R8])
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    print(f"  {N} prompts with 8 usable criteria · topw_k8 stores ranks 1-8 in importance order\n")

    def sc(sat, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in pids])
    V = {"ranks 1-4": sc(S8, [0, 1, 2, 3]),
         "ranks 5-8": sc(S8, [4, 5, 6, 7]),
         "ranks 1-8": sc(S8),
         "random k=4": sc(R4), "random k=8": sc(R8)}
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(d):
        bs = d[IDX].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                ZEFF * d.std(ddof=1) / math.sqrt(N))

    print("  A2 BY RANK BLOCK\n")
    for k, v in V.items():
        print(f"    {k:<14}{v.mean():.4f}")

    print("\n  THE CONTRASTS\n  " + header("comparison", width=26))
    C = {"ranks 1-4 − ranks 5-8": cell(V["ranks 1-4"] - V["ranks 5-8"]),
         "ranks 5-8 − random k=4": cell(V["ranks 5-8"] - V["random k=4"]),
         "ranks 1-4 − random k=4": cell(V["ranks 1-4"] - V["random k=4"]),
         "ranks 1-8 − random k=8": cell(V["ranks 1-8"] - V["random k=8"])}
    grid = []
    for k, c in C.items():
        grid.append((k, c[3]))
        print("  " + row(k, *c[:3], c[4], width=26))

    pc = C["ranks 1-8 − random k=8"]; pos_ok = verdict(*pc[:3], pc[4]) == POS
    nz = cell(V["ranks 1-4"] - V["ranks 1-4"])
    print(f"\n  POSITIVE CTRL  ranks 1-8 beat random k=8 on this population: "
          f"{'PASS' if pos_ok else 'FAIL — the population is the problem'}")
    print(f"  NEGATIVE CTRL  a rank block against itself: {nz[0]:.2e}  "
          f"{'PASS' if nz[0] == 0 else 'FAIL'}")
    grid.sort(key=lambda z: z[1]); K = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / K)
    print(f"  BH q=0.05 over {K} cells · {surv} survive")
    if not (pos_ok and nz[0] == 0):
        print("\n  UNVERIFIED — controls did not behave.")
        return 1

    lower_beats_random = verdict(*C["ranks 5-8 − random k=4"][:3],
                                 C["ranks 5-8 − random k=4"][4]) == POS
    top_beats_lower = verdict(*C["ranks 1-4 − ranks 5-8"][:3],
                              C["ranks 1-4 − ranks 5-8"][4]) == POS
    print("\n  " + "=" * 76)
    print(f"  PRE-REGISTERED KILL: do ranks 5-8 beat random k=4 separably ?  {lower_beats_random}")
    print(f"    and do ranks 1-4 beat ranks 5-8 separably ?  {top_beats_lower}")
    if lower_beats_random and not top_beats_lower:
        print("  -> W-BROAD. Importance matters BROADLY and not finely: the second-tier block is")
        print("     as good as the top one, and both beat a random draw. `top-k` is a GRADIENT")
        print("     boundary at best, and the admitted arms' name overstates what selects them.")
    elif lower_beats_random and top_beats_lower:
        print("  -> W-CUT + gradient. Both hold: the top block is better AND the second tier still")
        print("     beats random, so importance is informative across a range with a real cut.")
    elif top_beats_lower:
        print("  -> W-CUT. The information is at the boundary: ranks 5-8 are no better than a")
        print("     random draw, and the top-4 cut is doing the work.")
    else:
        print("  -> W-NEITHER. Neither contrast separates: topw's advantage over random is NOT")
        print("     located by this decomposition, and something else about the draw explains it.")
    print("  " + "=" * 76)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "selection_boundary.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N,
                                 a2={k: float(v.mean()) for k, v in V.items()},
                                 contrasts=C, lower_beats_random=bool(lower_beats_random),
                                 top_beats_lower=bool(top_beats_lower)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
