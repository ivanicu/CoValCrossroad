#!/usr/bin/env python3
"""
R862 · does R861's sign survive a 60× wider family? — the selection component as a DOSE-RESPONSE.

⛔ WHY. R861 measured, for the first time in this project, what a MAX bar's fixed argmax hides:
re-selecting `best_rule` INSIDE each bootstrap resample gives an MDE **0.966×** the fixed-argmax one
— **smaller**, the opposite of the direction I had called forced. The mechanism it found is
**downside-clipping**: when the rank-1 candidate dips on a resample another wins instead, so the max
truncates the bar's lower tail. It measured this on **30 rules**.

**R860's published `margin/MDE = 0.870` rests on the identical omission over 1,820 subsets**, and
R861 explicitly refused to transfer its number there — importing a factor across families is the
exact error that produced this whole thread (entry 1386). So the width is the open variable.

⛔⛔ **AND THIS ROUND PRE-REGISTERS NO DIRECTION, DELIBERATELY.** R861's closing sentence guessed
that clipping should WEAKEN with width "as the winners stop being near-tied". **That guess has no
more standing than the derivation it replaced**, and there is a competing mechanism pointing the
other way: 4-subsets of a 16-pool overlap heavily, so a wider family is a max over MORE and MORE
CORRELATED variables, and extreme-value concentration predicts MORE clipping, not less. **Writing
the direction down as an expectation is what made the last error visible; writing it down as a
DERIVATION is what made it an error. This round writes it as a fork.**

ESTIMAND        `MDE_selective / MDE_fixed` as a function of family width w, for the comparison
                `coval_core − max_over_w_blind_subsets`, at w = 30, 100, 300, 1000, 1820.
IDENTIFICATION  exact; every quantity is a deterministic function of released matrices. The
                bootstrap is closed-form as two matmuls — bar_b(k) = (B @ w_b)/N — so the full
                1820×4000 grid is 58 MB rather than the 56 TB a naive resample-index would need.
SCOPE           population: prompts scored by BOTH `genericpool16` and `coval_core`, all annotators
                instrument: A2 vs every annotator; comparator = max over w blind 4-subsets
                baseline:   the fixed-argmax MDE, i.e. R860's own construction
                regime:     home release, judge J. ⚠ w=1820 is the COMPLETE enumeration C(16,4);
                            smaller w are uniform draws WITHOUT forcing the global argmax in, since
                            forcing it in would manufacture the comparison this round is making.
WORLDS          A · ratio falls further below 1 as w grows -> clipping STRENGTHENS with width;
                    extreme-value concentration dominates and every wide max-bar MDE in this
                    project is conservative by a widening margin
                B · ratio rises toward/past 1 as w grows -> switching HETEROGENEITY dominates at
                    width; R861's 0.966 is a narrow-family artifact and does not generalise
                C · ratio flat in w -> the effect is a property of the max operation, not of the
                    family size, and R861's number transfers after all
KILL            CONDITIONAL, three arms, ALL required before any ratio is readable:
                  ① reproduce R331's blind max 0.55747530882624 to 1e-9
                  ② reproduce `coval_core` 0.5664774811929549 to 1e-9
                  ⭐ ③ reproduce **R860's own published MDE 0.010343530538451993** to 1e-12, by
                     drawing the bootstrap indices in R860's exact order at its exact seed. This
                     ties the round to the committed number rather than to a re-derivation of it —
                     §4's `determinism read as currency`, which compares two fresh runs to each
                     other and never to disk.
POSITIVE CTRL   the argmax must SWITCH across resamples at every width. Where it does not, the two
                constructions are the same object, the ratio is 1.000 by construction, and a bug
                would print identically to a finding. Reported per width, not once.
PLACEBO         at w = 1 the two constructions are identical by definition -> ratio must be exactly
                1.000. A width sweep that does not return 1.000 at w=1 is measuring something else.
SEEDS           3 bootstrap seeds × 5 family draws per width; both spreads reported.
MULTIPLICITY    5 widths × 3 seeds = 15 cells, all reported including any that disagree in sign.
ARTIFACT        results/width_sweep.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism).
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
PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, ZEFF = 4000, 2.802
WIDTHS = (1, 30, 100, 300, 1000, 1820)


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    print(f"  prompts {N} · pool {npool} · C({npool},4) = {len(subs)}")

    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    B = np.empty((len(subs), N))
    for n in range(N):
        Y = SAT[n][subs].sum(axis=1)
        C_ = np.sign(Y[:, ii] - Y[:, jj])
        B[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
    per_sub = B.mean(axis=1)
    kglob = int(per_sub.argmax())
    got_max = float(per_sub[kglob])

    core = np.array([np.mean([[cls(yvec(A[p], sorted({i for i, _ in A[p]})))[c] == h[c]
                               for c in range(6)] for h in H[n]]) for n, p in enumerate(pids)])
    got_core = float(core.mean())

    d1, d2 = abs(got_max - R331_MAX), abs(got_core - CORE_MEAN)
    print(f"  KILL ①  blind max  {got_max!r}  |Δ|={d1:.3e}  {'PASS' if d1 <= 1e-9 else 'FAIL'}")
    print(f"  KILL ②  coval_core {got_core!r}  |Δ|={d2:.3e}  {'PASS' if d2 <= 1e-9 else 'FAIL'}")

    # ---- KILL ③ : reproduce R860's COMMITTED MDE by replaying its exact draw order ---------------
    rng860 = np.random.default_rng(31)
    idx860 = np.array([rng860.integers(0, N, N) for _ in range(NBOOT)])
    d860 = core - B[kglob]
    mde860 = ZEFF * float(d860[idx860].mean(1).std(ddof=1))
    d3 = abs(mde860 - R860_MDE)
    print(f"  KILL ③  R860 MDE   {mde860!r}")
    print(f"          committed  {R860_MDE!r}  |Δ|={d3:.3e}  {'PASS' if d3 <= 1e-12 else 'FAIL'}")
    print("    Replays R860's seed AND its draw ORDER, so this compares against the number on disk")
    print("    rather than against a fresh re-derivation of it.")
    if d1 > 1e-9 or d2 > 1e-9 or d3 > 1e-12:
        print("\n  UNVERIFIED: the construction cannot reproduce what it is extending. Exit 2.")
        json.dump({"verdict": "UNVERIFIED", "got_max": got_max, "got_core": got_core,
                   "mde860": mde860}, open(OUT / "width_sweep.json", "w"), indent=2)
        return 2

    def counts(idx):
        W = np.zeros((NBOOT, N))
        for b in range(NBOOT):
            np.add.at(W[b], idx[b], 1.0)
        return W / N

    print(f"\n  {'w':>6} {'ratio':>8} {'sd(draws)':>10} {'switch%':>9} {'winners':>8} "
          f"{'mde_fix':>10} {'mde_sel':>10}")
    rows = []
    for w in WIDTHS:
        rats, sws, wins, mfs, mss = [], [], [], [], []
        for sd in (11, 22, 33):
            Wc = counts(np.random.default_rng(1000 + sd).integers(0, N, size=(NBOOT, N)))
            coreM = Wc @ core
            for fd in range(5 if w < len(subs) else 1):
                sel = (np.arange(len(subs)) if w >= len(subs)
                       else np.random.default_rng(7000 + fd).choice(len(subs), w, replace=False))
                Bw = B[sel]
                BM = Wc @ Bw.T                       # (NBOOT, w) resampled means, exact
                kf = int(Bw.mean(1).argmax())        # argmax on the FULL sample, fixed
                ks = BM.argmax(1)                    # argmax RE-SELECTED per resample
                mf = ZEFF * float((coreM - BM[:, kf]).std(ddof=1))
                ms = ZEFF * float((coreM - BM[np.arange(NBOOT), ks]).std(ddof=1))
                rats.append(ms / mf); sws.append(float((ks != kf).mean()))
                wins.append(int(len(np.unique(ks)))); mfs.append(mf); mss.append(ms)
        r, s, nw = float(np.mean(rats)), float(np.mean(sws)), float(np.mean(wins))
        # ⚠ every field is the MEAN over the same cells the ratio averages. The first draft stored
        # the LAST cell's mde_fixed/mde_selective beside an AVERAGED ratio, so the artifact would
        # have implied ms/mf == ratio when it did not. A row whose fields come from different
        # populations is §4's `truncated string read as data` in JSON form.
        rows.append({"width": w, "ratio": r, "sd_over_draws": float(np.std(rats)),
                     "switch_rate": s, "distinct_winners": nw,
                     "mde_fixed": float(np.mean(mfs)), "mde_selective": float(np.mean(mss)),
                     "cells": len(rats)})
        print(f"  {w:>6} {r:>8.4f} {np.std(rats):>10.2e} {s*100:>8.1f}% {nw:>8.1f} "
              f"{np.mean(mfs):>10.6f} {np.mean(mss):>10.6f}")

    pl = rows[0]
    pl_ok = abs(pl["ratio"] - 1.0) < 1e-12 and pl["switch_rate"] == 0.0
    print(f"\n  PLACEBO  w=1: the two constructions are one object -> ratio must be exactly 1.000")
    print(f"           got {pl['ratio']!r}, switch {pl['switch_rate']:.3f}  "
          f"{'PASS' if pl_ok else 'FAIL'}")
    sw_ok = all(x["switch_rate"] > 0.01 for x in rows[1:])
    print(f"  POSITIVE the argmax SWITCHES at every width > 1: {sw_ok}  "
          f"{'PASS' if sw_ok else 'FAIL'}")
    if not (pl_ok and sw_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "width_sweep.json", "w"), indent=2)
        return 2

    wide = [x for x in rows if x["width"] > 1]
    r30, rfull = wide[0]["ratio"], wide[-1]["ratio"]
    trend = rfull - r30
    world = "A" if trend < -0.01 else ("B" if trend > 0.01 else "C")
    print(f"\n  ⭐ ratio at w=30: {r30:.4f}   at w=1820: {rfull:.4f}   trend {trend:+.4f}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "clipping STRENGTHENS with width — extreme-value concentration dominates, and every"
             " wide max-bar MDE in this project is conservative by a WIDENING margin",
        "B": "switching HETEROGENEITY dominates at width — R861's 0.966 is a narrow-family"
             " artifact and does NOT generalise",
        "C": "the ratio is FLAT in width — the effect is a property of the max operation itself,"
             " not of family size, and R861's number transfers"}[world])
    corrected = 0.870 / rfull
    print(f"\n  ⭐ R860's published margin/MDE 0.870 -> {corrected:.3f} once the argmax is"
          f" re-selected")
    print(f"     {'STILL BELOW' if corrected < 1.5 else 'NOW CLEARS'} this project's 1.5× floor"
          f"  (it would need ratio <= {0.870/1.5:.4f} to clear)")
    print("     ⚠ R861 refused to transfer 0.966 here. This round MEASURED it here instead, and")
    print("       the two numbers are reported side by side rather than one standing for both.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": N, "pool": npool, "n_subsets": len(subs),
               "world": world, "rows": rows, "trend_w30_to_full": trend,
               "r861_ratio_30_rules": 0.966,
               "r860_margin_over_mde_published": 0.870,
               "r860_margin_over_mde_corrected": corrected,
               "ratio_needed_to_clear_1p5": 0.870 / 1.5,
               "controls": {"placebo_w1": pl_ok, "switch_all_widths": sw_ok,
                            "reproduced_r860_mde": mde860}},
              open(OUT / "width_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/width_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
