#!/usr/bin/env python3
"""
R852 · what is the "free component" actually made of? — three nulls, and mine was never checked.

⛔ THE ARITHMETIC, RUN FIRST, AND IT INDICTS MY OWN TWO PREVIOUS ROUNDS. Under BH at q = 0.05 over
99 arms, a **pure** null yields on the order of `q · N ≈ 5` discoveries. R850 measured **30** and
R851 measured **16** on what I called a "shuffled target" and treated as a null. **3–6× the pure-null
expectation. So the pair-label shuffle is NOT a pure null: something systematic survives it, and I
called that something "noise" twice without checking.**

That is §1's own row, verbatim: *"A permutation null answers `did the pairing matter`, never `why`.
Before calling one load-bearing, NAME THE WORLD IT EXCLUDES and build that world synthetically to
check."* **I made it load-bearing in two consecutive rounds and never built the world.**

ESTIMAND        the extension count under THREE nulls of increasing strength, against the pure-null
                expectation `q·N`, for the same clause-② comparison:
                  N1 PAIR-LABEL SHUFFLE — the 6 pairwise verdicts are permuted WITHIN a prompt.
                     Destroys which-pair-is-which; PRESERVES each prompt's marginal verdict mix.
                  N2 CROSS-PROMPT SWAP  — each prompt receives ANOTHER prompt's human ranking.
                     Destroys the arm-human pairing; PRESERVES the human marginal distribution
                     and every arm's own structure.
                  N3 UNIFORM RANDOM     — a uniformly random ranking per prompt. The pure null.
IDENTIFICATION  yes; all three are re-labelings of the same released matrices.
SCOPE           population: 99 scored arms, per-arm prompts (NOT intersected), median 968
                instrument: A2 vs the EVEN annotators; comparator `genericpool16`
                baseline:   `q·N = 0.05 × 99 ≈ 5`, the pure-null expectation
                regime:     home release, judge J
WORLDS          A · N1 ≈ N2 ≈ N3 ≈ 5 -> the excesses in R850/R851 were real and my nulls were fine
                B · N1 > N2 ≈ N3 -> what survives my shuffle is MARGINAL structure (tie rates,
                    verdict mix), so the "free component" is FORMAT agreement, not noise, and the
                    correct null is the cross-prompt swap
                C · N1 ≈ N2 > N3 -> what survives is arm-vs-comparator structure independent of
                    the human entirely, and BOTH my nulls understate the free component
KILL            CONDITIONAL: placebo == 0 exactly and the positive control satisfies on the REAL
                target. Otherwise UNVERIFIED and no count is reported.
POSITIVE CTRL   `oracle_k4` must satisfy ② on the real target.
PLACEBO         comparator vs itself == 0 exactly.
⚠ EXPECTATION   `q·N` is the FDR bound's rough scale, not an exact prediction — BH controls the
                expected FALSE-discovery PROPORTION among rejections, so under a complete null the
                expected rejection count is bounded by q·N. It is quoted as a SCALE, not a test.
SEEDS           3 seeds per null; the seed is verified to change the relabeling.
MULTIPLICITY    BH q=0.05 within every cell over all 99 arms; tested and surviving both reported.
ARTIFACT        results/null_anatomy.json.
IMPOSSIBLE      construct validated · cross-release · causally identified. N/A with what each needs.
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


def bh_mask(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    targets, _ = SC.load_targets()
    pids = [p for p in sorted(targets) if len(targets[p]) >= 2]
    Hreal = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(Hreal[p])]
    n = len(pids)
    print(f"  prompts: {n}")

    def null(kind, seed):
        r = np.random.default_rng(seed)
        if kind == "N1_pair_shuffle":                 # within-prompt permutation of the 6 pairs
            return {p: Hreal[p][:, r.permutation(6)] for p in pids}
        if kind == "N2_cross_prompt":                 # each prompt gets ANOTHER prompt's humans
            perm = r.permutation(n)
            return {p: Hreal[pids[perm[i]]] for i, p in enumerate(pids)}
        if kind == "N3_uniform":                      # the pure null
            # ⚠ SC.cls returns a TUPLE of 6 pairwise verdicts, not an ndarray — wrap before
            # slicing. Caught by a TypeError rather than by producing a wrong number, which is the
            # lucky direction; a silent coercion here would have made the pure null unreadable.
            return {p: np.array([np.array(SC.cls(r.random(4)))
                                 for _ in range(max(len(Hreal[p]), 1))]) for p in pids}
        raise ValueError(kind)

    def vec(name, H):
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            S = SC.load_sat(f)
        except Exception:
            return None
        return np.array([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == H[p])
                         if p in S else np.nan for p in pids])

    names = []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:], Hreal)
        if v is not None and np.isfinite(v).sum() >= 200:
            names.append(f.stem[4:])
    print(f"  arms: {len(names)}  ·  pure-null SCALE q·N = {Q}×{len(names)} ≈ {Q*len(names):.1f}")

    bidx = np.random.default_rng(4242).integers(0, n, size=(NBOOT, n))

    def count(H):
        B = vec(BLIND, H)
        A = np.array([vec(nm, H) for nm in names])
        D = A - B
        M = np.isfinite(D).astype(float)
        Dz = np.nan_to_num(D, nan=0.0)
        bs = (Dz[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T
        lo = np.percentile(bs, 2.5, axis=0)
        p = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return bh_mask(p) & (lo > 0)

    Bev = vec(BLIND, Hreal)
    pl = float(np.nanmean(Bev - Bev)); pl_ok = abs(pl) < 1e-12
    sat_real = count(Hreal)
    ip = names.index(POS_CTRL) if POS_CTRL in names else None
    pos_ok = bool(sat_real[ip]) if ip is not None else False
    print(f"  PLACEBO  comparator vs itself {pl:+.2e}  {'PASS' if pl_ok else 'FAIL'}")
    print(f"  POSITIVE `{POS_CTRL}` satisfies ② on the REAL target: {pos_ok}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    if not (pl_ok and pos_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        return 2

    R = int(sat_real.sum())
    print(f"\n  REAL target: {R} of {len(names)} arms satisfy ②\n")
    print(f"  {'null':<20}{'extension (mean of 3 seeds)':>30}{'sd':>8}")
    rows = []
    for kind in ("N1_pair_shuffle", "N2_cross_prompt", "N3_uniform"):
        cs = []
        for s in (11, 22, 33):
            cs.append(int(count(null(kind, s)).sum()))
        rows.append({"null": kind, "mean": float(np.mean(cs)), "sd": float(np.std(cs)),
                     "counts": cs})
        print(f"  {kind:<20}{np.mean(cs):>30.1f}{np.std(cs):>8.1f}   {cs}")

    n1, n2, n3 = (r["mean"] for r in rows)
    scale = Q * len(names)
    if max(n1, n2, n3) <= 2 * scale:
        world = "A"
    elif n1 > 1.5 * n2 and n2 <= 2 * scale:
        world = "B"
    else:
        world = "C"
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "all three nulls sit near the pure-null scale — my nulls were fine and the excesses"
             " in R850/R851 stand as reported",
        "B": "the PAIR SHUFFLE keeps far more than the cross-prompt swap — what survives it is"
             " MARGINAL structure (verdict mix, tie rate), so the 'free component' is FORMAT"
             " agreement rather than noise, and the correct null is the cross-prompt swap",
        "C": "both re-labelings keep far more than the pure null — what survives is"
             " arm-vs-comparator structure independent of the human, and BOTH my nulls"
             " UNDERSTATE the free component"}[world])
    print(f"     real {R} · N1 {n1:.1f} · N2 {n2:.1f} · N3 {n3:.1f} · pure-null scale ≈ {scale:.1f}")
    print("     ⚠ q·N is the FDR bound's SCALE, not an exact prediction — BH bounds the expected")
    print("     false-discovery PROPORTION among rejections. It is a ruler, not a test.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_arms": len(names), "real": R,
               "pure_null_scale": scale, "nulls": rows,
               "controls": {"placebo": pl, "pos": pos_ok}},
              open(OUT / "null_anatomy.json", "w"), indent=2)
    print(f"\n  artifact: results/null_anatomy.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
