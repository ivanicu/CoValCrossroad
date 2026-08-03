"""R259 -- R253 killed A_real. It never tested U(k), which is what FORMULATION still stands on.

WHAT SURVIVED R253 AND WHY IT IS NOT SAFE
    R253 retracted A_real -- the count of distinct classes -- as the gate's right-hand side: its
    partial rank correlation with recovery, given n, was -0.0380 and +0.0107 against a permutation
    |null|95 of 0.1152 and 0.1399. FORMULATION's surviving upgrade is a DIFFERENT quantity:

        "admissibility is a RATE, not a predicate. U(1)=0.5714, U(2)=0.0606, U(3)=0.0105"

    U(k) is the share of size-k subsets whose induced class NO OTHER subset induces. A_real counts
    classes; U counts SINGLETONS. Related, not identical, and R253 tested only the first.

⛔ THE ARITHMETIC TRAP, LOCATED EXACTLY, BECAUSE HALF THIS ROUND IS FORCED
    R228 established that recovery at ZERO noise is exactly E[1/|ties|]. U is the share with
    |ties| = 1. Both are summaries of the same tie structure, so U PREDICTING RECOVERY AT eps=0 IS
    ALGEBRA, not evidence. It is included below purely as a POSITIVE CONTROL -- an arm whose answer
    is known in advance and which therefore tests the machinery rather than the world.

    THE UNFORCED QUESTION is whether U still predicts at the release's own noise level. At
    eps=0.25 -- R227's calibration to the observed 47.8% two-rater agreement -- recovery could be
    governed entirely by noise and not at all by the tie structure. Nothing in the algebra decides
    that, which is what makes it a measurement.

ESTIMAND        the rank-partial correlation of U(k) with per-prompt planted-subset recovery, GIVEN
                n, at eps in {0, 0.25, 0.50}: partial( U(k), recovery | n ), per k.
                And the out-of-sample version: does adding U to n lower held-out MAE?
IDENTIFICATION  exact per prompt: U is exhaustive over all C(n,k) subsets, recovery is measured on
                a planted subset. The partial correlation is the only estimate; its null is a
                permutation of U across prompts holding n and recovery fixed.
SCOPE           population: 250 prompts, 6 <= n <= 14, r04 cache -- the same set R228/R248/R253
                used, so the comparison is to their published numbers. instrument: Qwen3.5-2B
                tensor. baseline: n alone, and a third trivial scalar as a sham. regime: m=4,
                k in {1,2}, 5 seeds on the planting.
WORLDS          W-RATE-REAL   the tie structure governs recovery at real noise
                                -> partial non-zero at eps=0.25, and FORMULATION's rate is a
                                   statement about the world this release lives in
                W-NOISELESS    ties govern only the noiseless case
                                -> partial ~1 at eps=0 (FORCED, and labelled as such) and at its
                                   null by eps=0.25. Then "admissibility is a rate" describes a
                                   world with no rater noise, and the release has 47.8% two-rater
                                   agreement. The rate would have to carry that scope or go
                W-N-AGAIN      U is n in a costume, exactly as A_real was
                                -> partial at its null at EVERY eps including 0, which would mean
                                   even the forced arm fails and the machinery is broken
KILL            pre-registered: if the partial at eps=0.25 is inside its permutation null at every
                k AND adding U does not lower held-out MAE beyond the seed spread, then
                FORMULATION's surviving upgrade is scoped to the noiseless case and must say so.
                If the eps=0 arm ALSO comes back null, the round is UNVERIFIED -- not a finding
                about U, but a failure of the machinery, because that arm's answer is algebra.
POSITIVE CTRL   the eps=0 arm, whose answer is forced by R228's identity. It must fire. This is a
                control that CAN fail and whose failure is diagnostic of the code, not the world.
NEGATIVE CTRL   permute U across prompts, holding n and recovery fixed. 200 draws, per k per eps.
SHAM            a third trivial scalar -- mean pairwise satisfaction spread -- given the same
                partial treatment. If it predicts as well as U, U is not special among scalars.
PLACEBO         partial(n, recovery | n) must be exactly 0, and Spearman(U, U) exactly 1.
NOISE FLOOR     5 planting seeds; spread reported.
MULTIPLICITY    2 k x 3 eps x 3 predictors x 5 seeds, plus 200 permutation draws per cell.
SPECIFICATION   swept: eps -- the axis FORMULATION's rate was quoted without.
ARTIFACT        per-prompt (n, U, recovery at each eps) persisted.
IMPOSSIBLE      whether the release's TRUE rater noise is eps=0.25. That is R227's calibration from
                47.8% two-rater agreement, an inference and not a measurement of eps itself; the
                sweep over three values is what stands in for it.
"""
from __future__ import annotations
import collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
KS = [1, 2]
EPSS = [0.0, 0.25, 0.50]
SEEDS = [0, 1, 2, 3, 4]
PERM = 200
PUB_U = {1: 0.5714, 2: 0.0606}


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x), dtype=float)
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    for i, c in enumerate(cnt):
        if c > 1:
            m = inv == i; r[m] = r[m].mean()
    return r


def spear(a, b):
    ra, rb = rank(a) - rank(a).mean(), rank(b) - rank(b).mean()
    d = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def partial(a, b, c):
    ra, rb, rc = rank(a), rank(b), rank(c)
    rc = rc - rc.mean()
    ss = float((rc ** 2).sum())
    if ss == 0:
        return spear(a, b)
    ea = ra - ra.mean() - rc * float(((ra - ra.mean()) * rc).sum()) / ss
    eb = rb - rb.mean() - rc * float(((rb - rb.mean()) * rc).sum()) / ss
    d = math.sqrt(float((ea ** 2).sum()) * float((eb ** 2).sum()))
    return float((ea * eb).sum() / d) if d > 0 else 0.0


def uniqueness(W, S, k):
    ctr = collections.Counter()
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        ctr[cls((W[idx, None] * S[idx]).sum(0))] += 1
    n_sub = sum(ctr.values())
    return sum(1 for v in ctr.values() if v == 1) / n_sub


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    P = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 14):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        P.append((W, S))
        if len(P) >= 250:
            break
    ns = np.array([len(W) for W, _S in P], float)
    spread = np.array([float(np.abs(S - S.mean(0)).mean()) for _W, S in P])
    print("prompts %d | n in [%d, %d]" % (len(P), int(ns.min()), int(ns.max())))

    print("\n=== U(k), against what FORMULATION publishes ===")
    U = {}
    for k in KS:
        U[k] = np.array([uniqueness(W, S, k) for W, S in P])
        print(" k=%d  mean U %.4f   FORMULATION publishes %.4f   %s"
              % (k, U[k].mean(), PUB_U[k],
                 "OK" if abs(U[k].mean() - PUB_U[k]) < 0.02 else "DIFFERS -- population mismatch"))
    pub_ok = all(abs(U[k].mean() - PUB_U[k]) < 0.02 for k in KS)

    print("\n=== PLACEBO ===")
    pl1 = partial(ns, ns, ns); pl2 = spear(U[1], U[1])
    print(" partial(n, n | n) %.4f (must be 0)   Spearman(U,U) %.4f (must be 1)   %s"
          % (pl1, pl2, "OK" if abs(pl1) < 1e-9 and abs(pl2 - 1) < 1e-9 else "BROKEN"))

    print("\n=== recovery, and whether U predicts it, by NOISE LEVEL ===")
    print("%-4s %-6s %10s %12s %12s %10s %10s"
          % ("k", "eps", "recovery", "rho(n,rec)", "PART(U|n)", "|null|p95", "SHAM"))
    res, rec_store = {}, {}
    for k in KS:
        for eps in EPSS:
            rec = []
            for pi, (W, S) in enumerate(P):
                v = []
                for seed in SEEDS:
                    rng = np.random.default_rng(abs(hash((pi, seed, k, eps))) % (2 ** 32))
                    T = tuple(sorted(rng.choice(len(W), size=k, replace=False)))
                    y = (W[list(T), None] * S[list(T)]).sum(0)
                    y = y + eps * (np.abs(y).max() or 1.0) * rng.standard_normal(4)
                    obs = np.array(cls(y))
                    best, hits = None, []
                    for c in itertools.combinations(range(len(W)), k):
                        idx = list(c)
                        d = float(np.abs(np.array(cls((W[idx, None] * S[idx]).sum(0))) - obs).sum())
                        if best is None or d < best - 1e-12:
                            best, hits = d, [c]
                        elif abs(d - best) <= 1e-12:
                            hits.append(c)
                    v.append((1.0 / len(hits)) if T in hits else 0.0)
                rec.append(float(np.mean(v)))
            rec = np.array(rec); rec_store[(k, eps)] = rec
            pa = partial(U[k], rec, ns)
            rng2 = np.random.default_rng(int(100 * eps) + k)
            null = np.array([partial(U[k][rng2.permutation(len(U[k]))], rec, ns)
                             for _ in range(PERM)])
            p95 = float(np.percentile(np.abs(null), 95))
            sh = partial(spread, rec, ns)
            res[(k, eps)] = (float(rec.mean()), spear(ns, rec), pa, p95, sh)
            print("%-4d %-6.2f %10.4f %12.4f %12.4f %10.4f %10.4f"
                  % (k, eps, rec.mean(), spear(ns, rec), pa, p95, sh))
    print(" (eps=0 is the POSITIVE CONTROL and its answer is FORCED: R228 showed recovery at zero")
    print("  noise is E[1/|ties|], and U is the share with |ties|=1. It tests the code, not the world.)")

    print("\n=== OUT OF SAMPLE: does adding U to n lower held-out error? ===")
    oos = {}
    for k in KS:
        for eps in (0.0, 0.25):
            rec = rec_store[(k, eps)]
            e_n, e_nu = [], []
            for s in range(5):
                rng = np.random.default_rng(700 + s)
                idx = rng.permutation(len(rec)); tr, te = idx[:len(idx) // 2], idx[len(idx) // 2:]

                def binpred(feat, tr, te):
                    b = {}
                    for v in np.unique(feat[tr]):
                        b[v] = rec[tr][feat[tr] == v].mean()
                    g = rec[tr].mean()
                    return np.array([b.get(v, g) for v in feat[te]])
                e_n.append(float(np.abs(binpred(ns, tr, te) - rec[te]).mean()))
                key = ns * 100 + np.round(U[k] * 20)
                e_nu.append(float(np.abs(binpred(key, tr, te) - rec[te]).mean()))
            oos[(k, eps)] = (float(np.mean(e_n)), float(np.ptp(e_n)),
                             float(np.mean(e_nu)), float(np.ptp(e_nu)))
            print(" k=%d eps=%.2f  MAE n only %.4f (spread %.4f)  n+U %.4f (spread %.4f)  delta %+.4f"
                  % (k, eps, oos[(k, eps)][0], oos[(k, eps)][1], oos[(k, eps)][2],
                     oos[(k, eps)][3], oos[(k, eps)][2] - oos[(k, eps)][0]))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    forced_ok = all(abs(res[(k, 0.0)][2]) > res[(k, 0.0)][3] for k in KS)
    noisy_null = all(abs(res[(k, 0.25)][2]) <= res[(k, 0.25)][3] for k in KS)
    no_oos = all(oos[(k, 0.25)][2] >= oos[(k, 0.25)][0] - max(oos[(k, 0.25)][1], oos[(k, 0.25)][3])
                 for k in KS)
    if not (abs(pl1) < 1e-9 and abs(pl2 - 1) < 1e-9):
        v = "UNVERIFIED -- the placebo failed; the partial-correlation machinery is wrong."
    elif not forced_ok:
        v = ("UNVERIFIED -- the eps=0 arm, whose answer is FORCED by R228's identity, came back "
             "inside its null (%s vs %s). That is a failure of the code, not a finding about U, "
             "and no other cell here is readable."
             % ([round(res[(k, 0.0)][2], 4) for k in KS],
                [round(res[(k, 0.0)][3], 4) for k in KS]))
    elif noisy_null and no_oos:
        v = ("W-NOISELESS -- FORMULATION's surviving upgrade is SCOPED TO A WORLD WITHOUT RATER "
             "NOISE. U predicts recovery at eps=0 (%s, forced) and is inside its permutation null "
             "at the release's own calibrated noise (%s vs |null|95 %s), with no held-out gain. "
             "The rate U(1)=0.5714 / U(2)=0.0606 is real arithmetic about the tie structure and "
             "says nothing about what is recoverable at 47.8%% two-rater agreement. It must carry "
             "that scope or go."
             % ([round(res[(k, 0.0)][2], 4) for k in KS],
                [round(res[(k, 0.25)][2], 4) for k in KS],
                [round(res[(k, 0.25)][3], 4) for k in KS]))
    else:
        surv = [k for k in KS if abs(res[(k, 0.25)][2]) > res[(k, 0.25)][3]]
        v = ("W-RATE-REAL at k=%s -- U still predicts recovery at the release's own noise level "
             "(%s against |null|95 %s), so the rate is a statement about this world and not only "
             "about the noiseless one."
             % (surv, [round(res[(k, 0.25)][2], 4) for k in surv],
                [round(res[(k, 0.25)][3], 4) for k in surv]))
    print("\n  " + v)
    if not pub_ok:
        print("\n  ⚠ AND U DOES NOT REPRODUCE THE PUBLISHED RATE on this population; every cell")
        print("    above is about a different U than FORMULATION quotes.")
    json.dump({"prompts": len(P), "U_mean": {str(k): float(U[k].mean()) for k in KS},
               "published_U": PUB_U, "reproduces_published": bool(pub_ok),
               "cells": {"k%d_eps%.2f" % kk: list(vv) for kk, vv in res.items()},
               "oos": {"k%d_eps%.2f" % kk: list(vv) for kk, vv in oos.items()},
               "verdict": v}, open(OUT / "rate_under_noise.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
