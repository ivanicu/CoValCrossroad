#!/usr/bin/env python3
"""
R860 · the exact MDE of `coval_core` against the blind MAXIMUM — the last number the quest owed.

⛔ THE WALL, NAMED THREE TIMES AND SHRUNK THREE TIMES.
  1382 — "the resolution needs the argmax's membership, which is not committed; requires a re-run"
  1383 — the margin is BOUNDED to +-0.00025 from committed artifacts, no re-run needed
  1384 — the 1,820 are the COMPLETE enumeration C(16,4); nothing was ever lost
  1385 — R331 takes no subset argument, but its pool IS `sat_genericpool16.npz`, on disk, and its
         scoring is already vectorised to a (1820 x N) per-subset per-prompt matrix.
**So the number is computable now, from released matrices, reusing R331's own construction.**

ESTIMAND        the paired per-prompt difference `coval_core - argmax_blind_subset` in A2, with a
                cluster bootstrap over prompts, and the MDE of THAT comparison — not a proxy.
IDENTIFICATION  exact. The blind family is the complete C(16,4)=1820 enumeration of the released
                16-criterion pool; the argmax is therefore well-defined and recoverable.
SCOPE           population: prompts with a human ranking and both matrices (n reported)
                instrument: A2 over the 6 induced pairs, EVERY annotator (no draw, no seed)
                baseline:   R331's own committed `blind_dist.max = 0.55747530882624`
                regime:     home release, judge J
KILL            CONDITIONAL: the recomputed blind max must reproduce R331's committed order
                statistic to <=1e-9, and the recomputed `coval_core` mean must reproduce
                0.5664774811929549 to <=1e-9. **If the construction cannot reproduce the two
                numbers this round is about, nothing it computes is readable.** Exit 2 otherwise.
POSITIVE CTRL   the argmax subset's own mean must EQUAL the recomputed max by construction — a
                degenerate check, so it is NOT load-bearing and is not relied on. The load-bearing
                controls are the two reproductions above, which CAN fail.
MULTIPLICITY    one comparison, pre-specified. The 1,820 maximisation is INSIDE the baseline by
                design — that is what "every" means — and is not a multiple test.
⚠ WINNER'S CURSE, STATED: the max over 1,820 is an extreme order statistic, so it is biased UP as
   an estimate of "a typical blind quadruple". That makes it a CONSERVATIVE bar for the core, which
   is the direction the universal reading wants. It is not corrected, and it is not quoted as an
   estimate of anything else.
ARTIFACT        results/exact_mde.json
IMPOSSIBLE      construct validity · cross-release. N/A with what each would require.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

R331_MAX = 0.55747530882624
CORE_MEAN = 0.5664774811929549
PAIRS = list(itertools.combinations(range(4), 2))
NBOOT = 4000


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    print(f"  prompts {N} · pool {npool} · C({npool},4) = {len(list(itertools.combinations(range(npool),4)))}")

    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    B = np.empty((len(subs), N))
    for n in range(N):
        Y = SAT[n][subs].sum(axis=1)
        C_ = np.sign(Y[:, ii] - Y[:, jj])
        B[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
    per_sub = B.mean(axis=1)
    k = int(per_sub.argmax())
    got_max = float(per_sub[k])

    core = np.array([np.mean([[cls(yvec(A[p], sorted({i for i, _ in A[p]})))[c] == h[c]
                               for c in range(6)] for h in H[n]]) for n, p in enumerate(pids)])
    got_core = float(core.mean())

    d_max = abs(got_max - R331_MAX); d_core = abs(got_core - CORE_MEAN)
    print(f"\n  KILL CHECK  blind max recomputed {got_max!r}")
    print(f"              R331 committed          {R331_MAX!r}   |Δ| = {d_max:.3e}  "
          f"{'PASS' if d_max <= 1e-9 else 'FAIL'}")
    print(f"  KILL CHECK  coval_core recomputed  {got_core!r}")
    print(f"              committed               {CORE_MEAN!r}   |Δ| = {d_core:.3e}  "
          f"{'PASS' if d_core <= 1e-9 else 'FAIL'}")
    if d_max > 1e-9 or d_core > 1e-9:
        print("\n  UNVERIFIED: the construction cannot reproduce the two numbers this round is")
        print("  about, so nothing it computes is readable. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "got_max": got_max, "got_core": got_core},
                  open(OUT / "exact_mde.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ ARGMAX subset (membership, NOT previously committed): {subs[k].tolist()}")
    d = core - B[k]
    rng = np.random.default_rng(31)
    bs = np.array([d[rng.integers(0, N, N)].mean() for _ in range(NBOOT)])
    lo, hi = np.percentile(bs, [2.5, 97.5]); se = float(bs.std(ddof=1)); mde = 2.802 * se
    obs = float(d.mean())
    print(f"  ⭐ margin core − argmax : {obs:+.10f}")
    print(f"     95% CI              : [{lo:+.10f}, {hi:+.10f}]")
    print(f"     SE                  : {se:.10f}")
    print(f"     ⭐ EXACT MDE         : {mde:.10f}")
    print(f"     ⭐ margin / MDE      : {obs/mde:.3f}   "
          f"{'CLEARS' if obs/mde >= 1.5 else 'BELOW'} this project's 1.5× bar")
    print(f"     CI excludes zero    : {'YES' if lo > 0 else 'NO'}")
    print(f"\n  ⚠ the proxy this replaces: entry 1383 used a neighbouring subset's own MDE,")
    print(f"    0.0066309665, giving 1.358. THIS is the MDE of the actual comparison.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": N, "argmax_subset": subs[k].tolist(),
               "blind_max_recomputed": got_max, "blind_max_committed": R331_MAX,
               "core_recomputed": got_core, "core_committed": CORE_MEAN,
               "margin": obs, "ci": [float(lo), float(hi)], "se": se, "mde": mde,
               "margin_over_mde": obs / mde, "ci_excludes_zero": bool(lo > 0),
               "replaces_proxy": {"entry": 1383, "proxy_mde": 0.0066309665, "proxy_ratio": 1.358}},
              open(OUT / "exact_mde.json", "w"), indent=2)
    print(f"\n  artifact: results/exact_mde.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
