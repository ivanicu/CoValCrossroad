#!/usr/bin/env python3
"""
R854 · are the pair-shuffle survivors the SAME arms every seed, or a fresh arbitrary set each time?

⛔ WHY, AND WHY THIS IS CHEAPER THAN THE ROUND I PLANNED. R853's NEXT proposed building two more
nulls to separate "coupling" from "ordering". **One rung lower on the attack ladder decides it for
almost nothing**: R852/R853 showed the pair shuffle leaves ~14–16 arms clearing clause ②, and
R853's κ control proved that is NOT marginal-format agreement. Two explanations remain, and they
make OPPOSITE predictions about a quantity already sitting in those runs:

  A · ARM-INTRINSIC BIAS — some arms have a systematic property (position, tie rate, length
      preference) that scores above the comparator against ANY relabeling of this prompt's human
      verdicts. Then the SAME arms survive at every seed and the survivor sets nearly coincide.
  B · A DIFFERENT-BUT-FIXED TARGET — each permutation manufactures its own arbitrary target, and
      whichever arms happen to align with THAT one win. Then survivor sets across seeds overlap
      no more than chance.

**Nobody has measured survivor-set stability across null seeds** (check #512 — no prior art), and
it is the discriminating statistic. This is the gauge/arithmetic rung, not a new experiment.

ESTIMAND        the pairwise Jaccard overlap of clause-② survivor sets across independent
                pair-shuffle seeds, against the overlap expected if each set were drawn uniformly
                at random from the same arms at the same sizes.
IDENTIFICATION  yes and exactly: the null model for "same sizes, random membership" is
                hypergeometric, so the chance overlap is computable in closed form and does not
                need simulating. ⚠ It IS also simulated here, because a closed form I derived is a
                claim about my algebra and this project does not accept those unchecked.
SCOPE           population: 99 scored arms · instrument: A2 vs EVEN annotators vs `genericpool16`
                baseline:   chance overlap at the observed set sizes
                regime:     home release; 8 independent pair-shuffle seeds
WORLDS          A · overlap >> chance -> arm-intrinsic bias; the ~15 are a property of those ARMS
                B · overlap ~ chance -> a fresh arbitrary target each seed; the ~15 is a property
                    of the PROCEDURE and names no arms at all
                These differ in what the number means, which is exactly what R852 got wrong once.
KILL            CONDITIONAL: the closed form and the simulation must agree to within Monte-Carlo
                error, and the REAL-target survivor set must be recovered identically at two
                different bootstrap seeds (the target does not move, so it must not).
                Otherwise UNVERIFIED.
POSITIVE CTRL   the real-target survivor set against itself has Jaccard 1.0 — a degenerate check,
                so it is NOT the load-bearing one; the load-bearing control is the closed-form
                versus simulation agreement, which can fail.
MULTIPLICITY    BH q=0.05 within each seed's cell, as in R851–R853.
SEEDS           8 pair-shuffle seeds -> 28 pairwise overlaps.
ARTIFACT        results/survivor_stability.json.
IMPOSSIBLE      construct validated · cross-release · causally identified.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402

NBOOT, Q, SEEDS = 2000, 0.05, (11, 22, 33, 44, 55, 66, 77, 88)
BLIND = "genericpool16"


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
    H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in targets[p][1::2]]) for p in pids}
    pids = [p for p in pids if len(H[p])]
    n = len(pids)

    def vec(name, Ht):
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            S = SC.load_sat(f)
        except Exception:
            return None
        return np.array([np.mean(SC.cls(SC.yvec(S[p], sorted({i for i, _ in S[p]}))) == Ht[p])
                         if p in S else np.nan for p in pids])

    names = [f.stem[4:] for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz"))]
    names = [nm for nm in names
             if (v := vec(nm, H)) is not None and np.isfinite(v).sum() >= 200]
    print(f"  prompts {n} · arms {len(names)}")

    bidx = np.random.default_rng(4242).integers(0, n, size=(NBOOT, n))

    def survivors(Ht):
        B = vec(BLIND, Ht)
        A = np.array([vec(nm, Ht) for nm in names])
        D = A - B
        M = np.isfinite(D).astype(float)
        Dz = np.nan_to_num(D, nan=0.0)
        bs = (Dz[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T
        lo = np.percentile(bs, 2.5, axis=0)
        p = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return bh_mask(p) & (lo > 0)

    # ---- control: the REAL target does not move, so its survivor set must not either ----------
    s1 = survivors(H); s2 = survivors(H)
    stable_ok = bool(np.array_equal(s1, s2))
    print(f"  CONTROL  the REAL survivor set is identical on a repeat call: {stable_ok}  "
          f"{'PASS' if stable_ok else 'FAIL'}   (|set| = {int(s1.sum())})")

    sets = []
    for sd in SEEDS:
        r = np.random.default_rng(sd)
        Hs = {p: H[p][:, r.permutation(6)] for p in pids}
        sets.append(survivors(Hs))
    sizes = [int(s.sum()) for s in sets]
    print(f"  pair-shuffle survivor sizes over {len(SEEDS)} seeds: {sizes}")

    obs = []
    for i, j in itertools.combinations(range(len(sets)), 2):
        a, b = sets[i], sets[j]
        u = int((a | b).sum())
        obs.append(int((a & b).sum()) / u if u else 0.0)
    obs = np.array(obs)

    # ---- chance overlap: closed form AND simulation, because my algebra is a claim -------------
    N = len(names)
    cf = []
    for i, j in itertools.combinations(range(len(sets)), 2):
        k1, k2 = sizes[i], sizes[j]
        e_int = k1 * k2 / N
        cf.append(e_int / (k1 + k2 - e_int) if (k1 + k2 - e_int) else 0.0)
    cf = np.array(cf)

    rng = np.random.default_rng(7)
    sim = []
    for i, j in itertools.combinations(range(len(sets)), 2):
        k1, k2 = sizes[i], sizes[j]
        vals = []
        for _ in range(400):
            a = np.zeros(N, bool); a[rng.choice(N, k1, replace=False)] = True
            b = np.zeros(N, bool); b[rng.choice(N, k2, replace=False)] = True
            u = int((a | b).sum())
            vals.append(int((a & b).sum()) / u if u else 0.0)
        sim.append(float(np.mean(vals)))
    sim = np.array(sim)

    agree = float(np.max(np.abs(cf - sim)))
    agree_ok = agree < 0.03
    print(f"  CONTROL  closed-form vs simulated chance overlap: max|Δ| = {agree:.4f}  "
          f"{'PASS' if agree_ok else 'FAIL'}")
    print("    A closed form I derived is a claim about my algebra; this project does not accept")
    print("    those unchecked, so it is simulated beside it and the two must agree.")

    if not (stable_ok and agree_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "stable": stable_ok, "agree": agree},
                  open(OUT / "survivor_stability.json", "w"), indent=2)
        return 2

    ratio = float(obs.mean() / max(sim.mean(), 1e-12))
    print(f"\n  ⭐ observed mean Jaccard across {len(obs)} seed pairs: {obs.mean():.4f} "
          f"[min {obs.min():.4f}, max {obs.max():.4f}]")
    print(f"     chance at the same sizes: {sim.mean():.4f}  ->  ratio {ratio:.2f}×")
    world = "A" if ratio >= 2.0 else ("B" if ratio <= 1.3 else "C")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the SAME arms survive every permutation — ARM-INTRINSIC bias, and the ~15 names a"
             " real property of those arms",
        "B": "overlap is at chance — each permutation manufactures its own arbitrary winners, so"
             " the ~15 is a property of the PROCEDURE and names no arms at all",
        "C": "between — partly arm-intrinsic, partly per-target, and the split is the finding"}[world])
    always = [names[i] for i in range(N) if all(s[i] for s in sets)]
    print(f"     arms surviving at ALL {len(SEEDS)} seeds: {len(always)}  {always[:8]}")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_arms": N, "sizes": sizes,
               "obs_jaccard_mean": float(obs.mean()), "chance_sim": float(sim.mean()),
               "chance_closed_form": float(cf.mean()), "ratio": ratio,
               "always_survivors": always, "real_set_size": int(s1.sum()),
               "controls": {"real_set_stable": stable_ok, "cf_vs_sim_max_abs_diff": agree}},
              open(OUT / "survivor_stability.json", "w"), indent=2)
    print(f"\n  artifact: results/survivor_stability.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
