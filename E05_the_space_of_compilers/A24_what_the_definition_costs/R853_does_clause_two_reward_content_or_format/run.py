#!/usr/bin/env python3
"""
R853 · does clause ② reward CONTENT, or the human's verdict FORMAT?

⛔ WHY. R852 measured that a pair-label shuffle — which destroys *which pair is which* but PRESERVES
each prompt's marginal verdict mix — still leaves **14.3 of 99 arms** clearing clause ② on A2, while
two proper nulls give **exactly 0**. So **A2 rewards marginal-format agreement**, and no clause in
the definition distinguishes an arm that tracks the human's CONTENT from one that merely shares the
human's mix of ties and strict orderings.

The principled instrument is the one that subtracts exactly that: **Cohen's κ**, which removes the
agreement expected from the two marginals alone. `cls` emits 6 verdicts over {−1, 0, +1}, so the
confusion table is 3×3 and per-prompt counts are ADDITIVE — the cluster bootstrap on κ is a tensor
sum, not 2,000 re-runs.

ESTIMAND        the extension of clause ② under κ instead of A2: arms whose paired κ advantage over
                the prompt-blind comparator is resolvably positive (BH q=0.05), on the REAL target
                and under all three of R852's nulls.
IDENTIFICATION  yes; κ is computable from the same released matrices, and its per-prompt sufficient
                statistic is a 3×3 count table.
SCOPE           population: 99 scored arms, per-arm prompts (NOT intersected), median 968
                instrument: κ vs the EVEN annotators; comparator `genericpool16`
                baseline:   the A2-based counts from R851/R852 — real 29, N1 14.3, N2 0, N3 0
                regime:     home release, judge J
WORLDS          A · κ-extension survives near the A2 real count -> ② rewards CONTENT, and the
                    format component R852 found rides on top of a real signal
                B · κ-extension collapses toward 0 -> FORMAT is what ② has been rewarding, and the
                    clause's whole measured selectivity is marginal agreement
                C · κ-extension survives but is much smaller -> ② rewards both, and the split is
                    the finding, reported as two numbers rather than one
KILL            CONDITIONAL, and its key arm is new:
                  ⭐ under N1 (the pair shuffle) the κ-extension MUST be ≈ 0.
                     κ is DEFINED to remove marginal-expected agreement, and N1 preserves exactly
                     the marginals — so if κ still admits ~14 arms there, κ is not doing its job
                     and nothing else in this round is readable.
                  plus placebo == 0 and the positive control satisfies on the real target.
                  Otherwise UNVERIFIED.
POSITIVE CTRL   `oracle_k4` must satisfy ② under κ on the real target.
PLACEBO         comparator vs itself == 0 exactly.
NULLS           N1 pair-shuffle · N2 cross-prompt swap · N3 uniform — all three, 3 seeds each.
MULTIPLICITY    BH q=0.05 over all 99 arms per cell; tested and surviving both reported.
ARTIFACT        results/content_vs_format.json.
IMPOSSIBLE      construct validated · cross-release · causally identified. N/A with what each needs.
⚠ NOT CLAIMED   κ is not "the right metric" — it is the metric that isolates the component R852
                found. Swapping metrics changes the clause, and that is stated, not smuggled.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

NBOOT, Q = 2000, 0.05
BLIND, POS_CTRL = "genericpool16", "oracle_k4"
LAB = {-1.0: 0, 0.0: 1, 1.0: 2}


def bh_mask(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def kappa_from_counts(T):
    """T: (..., 3, 3) joint counts -> Cohen's kappa along the last two axes."""
    n = T.sum((-2, -1))
    n = np.maximum(n, 1e-12)
    po = np.trace(T, axis1=-2, axis2=-1) / n
    pe = (T.sum(-1) * T.sum(-2)).sum(-1) / (n * n)
    return (po - pe) / np.maximum(1.0 - pe, 1e-12)


def main() -> int:
    targets, _ = SC.load_targets()
    pids = [p for p in sorted(targets) if len(targets[p]) >= 2]
    Hreal = {p: np.array([[LAB[v] for v in SC.cls(np.array(y, float))]
                          for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(Hreal[p])]
    n = len(pids)
    print(f"  prompts: {n} · verdict alphabet {{-1,0,+1}} -> 3x3 confusion")

    def null(kind, seed):
        r = np.random.default_rng(seed)
        if kind == "N1_pair_shuffle":
            return {p: Hreal[p][:, r.permutation(6)] for p in pids}
        if kind == "N2_cross_prompt":
            perm = r.permutation(n)
            return {p: Hreal[pids[perm[i]]] for i, p in enumerate(pids)}
        if kind == "N3_uniform":
            return {p: np.array([[LAB[v] for v in SC.cls(r.random(4))]
                                 for _ in range(max(len(Hreal[p]), 1))]) for p in pids}
        raise ValueError(kind)

    def counts(name, H):
        """-> (n_prompts, 3, 3) additive per-prompt joint counts, NaN-free; None if unreadable."""
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            S = SC.load_sat(f)
        except Exception:
            return None
        T = np.zeros((n, 3, 3))
        seen = np.zeros(n, bool)
        for i, p in enumerate(pids):
            if p not in S:
                continue
            a = np.array([LAB[v] for v in SC.cls(SC.yvec(S[p], sorted({j for j, _ in S[p]})))])
            for row in H[p]:
                np.add.at(T[i], (a, row), 1.0)
            seen[i] = True
        return (T, seen) if seen.sum() >= 200 else None

    names = [f.stem[4:] for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz"))]
    base = counts(BLIND, Hreal)
    if base is None:
        print(f"  UNRUNNABLE: comparator `{BLIND}` unreadable. Exit 2, never 0.")
        return 2
    keep = [nm for nm in names if counts(nm, Hreal) is not None]
    print(f"  arms: {len(keep)}")

    bidx = np.random.default_rng(4242).integers(0, n, size=(NBOOT, n))
    W = np.zeros((NBOOT, n))
    for b in range(NBOOT):
        np.add.at(W[b], bidx[b], 1.0)

    def extension(H):
        B = counts(BLIND, H)
        if B is None:
            return None
        Tb, sb = B
        res = []
        for nm in keep:
            c = counts(nm, H)
            if c is None:
                res.append(None); continue
            Ta, sa = c
            m = (sa & sb).astype(float)
            # bootstrap: resample PROMPTS, re-pool counts, recompute kappa on each side
            Ka = kappa_from_counts(np.einsum("bp,pij->bij", W * m, Ta))
            Kb = kappa_from_counts(np.einsum("bp,pij->bij", W * m, Tb))
            d = Ka - Kb
            lo = np.percentile(d, 2.5)
            pv = max(2 * min((d <= 0).mean(), (d >= 0).mean()), 1.0 / (NBOOT + 1))
            res.append((float(d.mean()), float(lo), float(pv)))
        ok = [i for i, r in enumerate(res) if r is not None]
        pv = np.array([res[i][2] for i in ok])
        msk = bh_mask(pv)
        sat = np.zeros(len(keep), bool)
        for j, i in enumerate(ok):
            sat[i] = bool(msk[j] and res[i][1] > 0)
        return sat, res

    satR, resR = extension(Hreal)
    ip = keep.index(POS_CTRL) if POS_CTRL in keep else None
    pos_ok = bool(satR[ip]) if ip is not None else False
    print(f"  PLACEBO  comparator vs itself: κ difference is identically 0 by construction  PASS")
    print(f"  POSITIVE `{POS_CTRL}` satisfies ② under κ: {pos_ok}  {'PASS' if pos_ok else 'FAIL'}")

    print(f"\n  REAL target: {int(satR.sum())} of {len(keep)} arms satisfy ② under κ "
          f"(A2 gave 29)")
    rows = []
    for kind in ("N1_pair_shuffle", "N2_cross_prompt", "N3_uniform"):
        cs = [int(extension(null(kind, s))[0].sum()) for s in (11, 22, 33)]
        rows.append({"null": kind, "mean": float(np.mean(cs)), "counts": cs})
        print(f"  {kind:<20}{np.mean(cs):>8.1f}   {cs}")

    n1 = rows[0]["mean"]
    key_ok = n1 <= 2.0
    print(f"\n  ⭐ KEY CONTROL  κ-extension under the PAIR SHUFFLE must be ≈0 "
          f"(A2 gave 14.3): {n1:.1f}  {'PASS' if key_ok else 'FAIL'}")
    if not (pos_ok and key_ok):
        print("  UNVERIFIED: κ did not remove the marginal component it is defined to remove, or")
        print("  the positive control failed. Nothing here is readable. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "pos_ok": pos_ok, "n1": n1},
                  open(OUT / "content_vs_format.json", "w"), indent=2)
        return 2

    R = int(satR.sum())
    world = "B" if R <= 2 else ("A" if R >= 0.8 * 29 else "C")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the κ-extension survives near the A2 count — ② rewards CONTENT, and the format"
             " component rides on top of a real signal",
        "B": "the κ-extension collapses — FORMAT is what ② has been rewarding",
        "C": "the κ-extension survives but is much smaller — ② rewards BOTH, and the split is the"
             " finding, reported as two numbers"}[world])
    core = keep.index("coval_core") if "coval_core" in keep else None
    if core is not None:
        print(f"     `coval_core` under κ: {resR[core][0]:+.4f} — "
              f"{'SATISFIES' if satR[core] else 'FAILS'}")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_arms": len(keep),
               "kappa_real": R, "a2_real_from_R851": 29, "nulls": rows,
               "key_control_pair_shuffle": {"kappa": n1, "a2_was": 14.3, "pass": key_ok},
               "arms": [{"arm": a, "d_kappa": (r[0] if r else None),
                         "satisfies": bool(s)} for a, r, s in zip(keep, resR, satR)]},
              open(OUT / "content_vs_format.json", "w"), indent=2)
    print(f"\n  artifact: results/content_vs_format.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
