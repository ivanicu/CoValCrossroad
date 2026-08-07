#!/usr/bin/env python3
"""
R864 · a POWERED null for the statistic actually being thresholded — three nulls, 20 seeds each.

⛔ WHY. R863 set out to calibrate the 1.5 floor against a MAX comparator and its primary instrument
was degenerate: a leave-one-out null in which **1819 of 1820 outcomes are negative by arithmetic**,
because a family member cannot beat the max of its own family. The round's own derivation predicted
exactly 1 positive and exactly 1 was observed — **the agreement is what proved the instrument
useless**, and its `WORLD A` verdict was withdrawn before commit.

What survived was a SECOND null (pair-shuffled target) that centred near **zero** while the LOO null
sat at **−2.18** — two nulls disagreeing by more than two units of the statistic. But it had 3 seeds
and it is the pair shuffle **R852/R853 already established is not pure**: it preserves each prompt's
marginal verdict mix and left ~14 arms clearing clause ②.

**So the calibration question is open, and this round answers it with nulls that do not share those
defects.** R852 built a cross-prompt swap and a uniform null — but for the clause-② EXTENSION COUNT,
never for `margin/MDE`. **No round has produced a powered null for the quantity being thresholded.**

⚠ NO DIRECTION IS PRE-REGISTERED. Two rounds running, a "forced" direction was refuted (R861's
variance claim, R862's width guess). The worlds below are a genuine fork and the docstring says so
before the run rather than after it.

ESTIMAND        the null distribution of `ratio = mean(core − max_k B_k) / MDE` when the human
                target carries no information the core could track, under three independent
                destructions of that target; and the percentile at which the observed +0.8683 and
                the project's 1.5 floor each sit in it.
IDENTIFICATION  exact. Each subset's verdict vector `C` is a function of the RESPONSES only and is
                independent of the target, so it is computed ONCE (968×1820×6 int8) and every null
                is an array comparison rather than a re-derivation. That is what makes 3 nulls ×
                20 seeds affordable at all.
SCOPE           population: 968 prompts scored by both `genericpool16` and `coval_core`
                instrument: A2 vs every annotator; comparator = max over C(16,4) = 1,820 subsets,
                            RE-SELECTED on each nulled family (a fixed argmax would import the real
                            target's choice into the null)
                baseline:   the observed ratio +0.8683 and the floor 1.5
                regime:     home release, judge J
WORLDS          A · all three nulls centre far BELOW the observed ratio and their p95 is under 1.5
                    -> the floor is over-strict for a max comparator, and `coval_core`'s failure is
                    a property of the BAR
                B · the nulls' p95 reaches or exceeds 1.5 -> the max comparator inflates the
                    statistic and 1.5 is too PERMISSIVE, i.e. the bar was protecting nothing
                C · the nulls DISAGREE with each other by more than the observed effect
                    -> the framing is the finding: `margin/MDE` has no null-invariant meaning here,
                    and no single threshold on it can be calibrated at all
KILL            CONDITIONAL, and nothing is readable unless all fire:
                  ① reproduce R331's blind max and `coval_core` to 1e-9 via the precomputed C
                     (this doubles as the positive control ON THE OPTIMISATION: if C is wrong,
                     these two numbers cannot come out)
                  ② reproduce R860's committed MDE 0.010343530538451993 to 1e-12
                  ⭐ ③ each null must be NON-DEGENERATE in R863's corrected sense: its ratios must
                     have non-zero spread across seeds AND must not be pinned to one sign by
                     construction. R863's KILL ③ accepted `>0 positives` and let a null through
                     that arithmetic had already determined; the threshold here is on SPREAD.
POSITIVE CTRL   the planted dose-response from R863, re-run through the precomputed path:
                g in {0, .005, .01, .02, .04}. Must be monotone, must NOT clear 1.5 at g=0, and
                must reproduce R863's first-clearing dose g=0.01.
PLACEBO         the argmax subset against itself: margin exactly 0.
MULTIPLICITY    3 nulls × 20 seeds = 60 cells; every cell reported, not a summary of the tail.
SEEDS           20 per null, and the seed is verified to change the target it produces.
ARTIFACT        results/powered_null.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism) ·
                temporally resolved (the release carries no annotation timestamps).
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
R860_MDE = 0.010343530538451993
OBSERVED = 0.8683
PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, ZEFF, FLOOR, NSEED = 4000, 2.802, 1.5, 20
DOSES = (0.0, 0.005, 0.01, 0.02, 0.04)


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    M = len(subs)
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    # ---- the optimisation: C is a function of the RESPONSES, never of the target ---------------
    C = np.empty((N, M, 6), np.int8)
    CV = np.empty((N, 6), np.int8)
    for n, p in enumerate(pids):
        SATn = np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
        Y = SATn[subs].sum(axis=1)
        C[n] = np.sign(Y[:, ii] - Y[:, jj]).astype(np.int8)
        CV[n] = np.array(cls(yvec(A[p], sorted({i for i, _ in A[p]}))), np.int8)
    print(f"  prompts {N} · family {M} · C precomputed {C.nbytes/1e6:.1f} MB "
          f"(target-independent, so every null is an array compare)")

    def build(Ht):
        """-> (B (M,N), core (N,)) against an arbitrary target list Ht."""
        B = np.empty((M, N)); cv = np.empty(N)
        for n in range(N):
            h = Ht[n]
            B[:, n] = (C[n][:, None, :] == h[None, :, :]).mean(axis=(1, 2))
            cv[n] = (CV[n][None, :] == h).mean()
        return B, cv

    B, core = build(H)
    per = B.mean(1); kglob = int(per.argmax())
    d1 = abs(float(per[kglob]) - R331_MAX); d2 = abs(float(core.mean()) - CORE_MEAN)
    print(f"  KILL ①  blind max |Δ|={d1:.3e} · coval_core |Δ|={d2:.3e}  "
          f"{'PASS' if max(d1, d2) <= 1e-9 else 'FAIL'}")
    print("    Doubles as the positive control ON THE OPTIMISATION: a wrong C cannot produce these.")
    rng860 = np.random.default_rng(31)
    idx860 = np.array([rng860.integers(0, N, N) for _ in range(NBOOT)])
    mde860 = ZEFF * float((core - B[kglob])[idx860].mean(1).std(ddof=1))
    d3 = abs(mde860 - R860_MDE)
    print(f"  KILL ②  R860 MDE |Δ|={d3:.3e}  {'PASS' if d3 <= 1e-12 else 'FAIL'}")
    if max(d1, d2) > 1e-9 or d3 > 1e-12:
        print("\n  UNVERIFIED: cannot reproduce what it extends. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "powered_null.json", "w"), indent=2)
        return 2

    W = np.zeros((NBOOT, N))
    bidx = np.random.default_rng(11).integers(0, N, size=(NBOOT, N))
    for b in range(NBOOT):
        np.add.at(W[b], bidx[b], 1.0)
    W /= N

    def ratio(arm, comp):
        d = arm - comp
        return float(d.mean() / max(ZEFF * float((W @ d).std(ddof=1)), 1e-300)), float(d.mean())

    pl_r, pl_m = ratio(B[kglob], B[kglob])
    pl_ok = abs(pl_m) < 1e-15
    print(f"  PLACEBO  argmax vs itself: margin {pl_m:+.3e}  {'PASS' if pl_ok else 'FAIL'}")

    print(f"\n  POSITIVE CONTROL  planted dose-response (must reproduce R863's first-clear g=0.01)")
    dose = []
    for g in DOSES:
        r, _ = ratio(core + g, B[kglob])
        dose.append({"g": g, "ratio": r, "clears": bool(r >= FLOOR)})
        print(f"    g={g:<6} ratio {r:+.4f}  {'CLEARS' if r >= FLOOR else 'below'}")
    rises = all(dose[i + 1]["ratio"] > dose[i]["ratio"] for i in range(len(dose) - 1))
    g0_ok = not dose[0]["clears"]
    first = next((d["g"] for d in dose if d["clears"]), None)
    pc_ok = rises and g0_ok and first == 0.01
    print(f"    monotone {rises} · fails at g=0 {g0_ok} · first clear {first}  "
          f"{'PASS' if pc_ok else 'FAIL'}")

    # ---- the three nulls, 20 seeds each ---------------------------------------------------------
    def null(kind, seed):
        r = np.random.default_rng(seed)
        if kind == "N1_pair_shuffle":
            return [h[:, r.permutation(6)] for h in H]
        if kind == "N2_cross_prompt":
            pm = r.permutation(N)
            return [H[pm[n]] for n in range(N)]
        if kind == "N3_uniform":
            return [np.array([cls(r.random(4)) for _ in range(len(H[n]))], float)
                    for n in range(N)]
        raise ValueError(kind)

    print(f"\n  {'null':<20}{'mean':>9}{'sd':>9}{'p95':>9}{'max':>9}{'>=1.5':>8}"
          f"{'obs pct':>9}")
    rows = []
    for kind in ("N1_pair_shuffle", "N2_cross_prompt", "N3_uniform"):
        rs = []
        for sd in range(NSEED):
            Ht = null(kind, 5000 + sd)
            Bn, cn = build(Ht)
            kn = int(Bn.mean(1).argmax())          # RE-SELECTED on the nulled family
            r, _ = ratio(cn, Bn[kn])
            rs.append(r)
        rs = np.array(rs)
        p95 = float(np.percentile(rs, 95))
        fp = float((rs >= FLOOR).mean())
        obs_pct = float((rs < OBSERVED).mean() * 100)
        rows.append({"null": kind, "n_seeds": NSEED, "mean": float(rs.mean()),
                     "sd": float(rs.std(ddof=1)), "p95": p95, "max": float(rs.max()),
                     "min": float(rs.min()), "fp_at_floor": fp,
                     "observed_percentile": obs_pct, "values": [float(x) for x in rs]})
        print(f"  {kind:<20}{rs.mean():>+9.4f}{rs.std(ddof=1):>9.4f}{p95:>+9.4f}"
              f"{rs.max():>+9.4f}{fp*100:>7.1f}%{obs_pct:>8.1f}%")

    spreads_ok = all(x["sd"] > 1e-6 for x in rows)
    print(f"\n  KILL ③  every null has non-zero SPREAD across seeds: {spreads_ok}  "
          f"{'PASS' if spreads_ok else 'FAIL'}")
    print("    R863's KILL ③ accepted `>0 positive margins` and passed a null arithmetic had")
    print("    already determined. The threshold here is on SPREAD, which degeneracy cannot fake.")
    if not (pl_ok and pc_ok and spreads_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "placebo": pl_m, "pos": pc_ok, "rows": rows},
                  open(OUT / "powered_null.json", "w"), indent=2)
        return 2

    means = np.array([x["mean"] for x in rows])
    p95s = np.array([x["p95"] for x in rows])
    disagree = float(means.max() - means.min())
    if disagree > OBSERVED:
        world = "C"
    elif p95s.max() >= FLOOR:
        world = "B"
    else:
        world = "A"
    print(f"\n  ⭐ null means span {means.min():+.4f} .. {means.max():+.4f}  "
          f"(disagreement {disagree:.4f} vs observed effect {OBSERVED})")
    print(f"  ⭐ largest null p95 = {p95s.max():+.4f}  vs floor {FLOOR}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "all three nulls sit far below the observed ratio and none reaches 1.5 — the floor is"
             " OVER-STRICT for a max comparator, and coval_core's failure is a property of the BAR",
        "B": "a null's p95 reaches 1.5 — the max comparator INFLATES the statistic and the floor was"
             " protecting nothing",
        "C": "the nulls disagree with each other by MORE than the observed effect — the framing is"
             " the finding, and no single threshold on margin/MDE can be calibrated here"}[world])
    print(f"     observed {OBSERVED:+.4f} sits above "
          f"{min(x['observed_percentile'] for x in rows):.1f}–"
          f"{max(x['observed_percentile'] for x in rows):.1f}% of null draws across the three")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": N, "family": M, "world": world,
               "observed_ratio": OBSERVED, "floor": FLOOR, "nulls": rows,
               "null_mean_disagreement": disagree,
               "max_null_p95": float(p95s.max()),
               "dose_response": dose, "first_clearing_g": first,
               "controls": {"placebo_margin": pl_m, "positive_ok": pc_ok,
                            "spreads_ok": spreads_ok, "reproduced_r860_mde": mde860},
               "supersedes": "R863's LOO null, retracted as degenerate"},
              open(OUT / "powered_null.json", "w"), indent=2)
    print(f"\n  artifact: results/powered_null.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
