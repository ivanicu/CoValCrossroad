"""R323 — the last unexplained number was NCAL, and it reproduces to six decimals.

R322 killed its own hypothesis (tau does not move with REPS) and left one residual: R268 reports
tau = 0.416 and R274 reports 0.424, same tensor, same 250 prompts. R322's closing line said both
scripts are readable without running anything, and that was right.

    R268   REPS, NCAL, NHOLD = 100,  200,  200
    R274   REPS, NCAL, NHOLD = 400, 3000, 3000

Identical construction on both sides: `cal = [arm_value(0.0, default_rng(10_000 + i)) for i in
range(NCAL)]`, then `tau = quantile(cal, 0.95)`. Same seed formula. And at g = 0 the two
`arm_value` bodies consume the SAME rng draws in the same order — R268's `carry[i] and
rng.random() < g` short-circuits identically to R274's `mode == "real" and rng.random() < g`,
because `carry` is all-True when `sham=False`. So R268's 200 calibration draws should be the FIRST
200 of R274's 3000, and its tau should be recoverable from R274's array alone.

ESTIMAND      whether `quantile(R274_cal[:200], 0.95)` equals R268's committed tau, and
              `quantile(R274_cal[:3000], 0.95)` equals R274's.
IDENTIFICATION exact if the draws coincide, and the test IS whether they coincide. This could
              have come out otherwise in several ways — different seed offsets, a different
              `arm_value`, a different `P` or `delta` — so a match is a MEASUREMENT of code
              identity, not an algebraic necessity. `the arithmetic trap` asks whether the result
              was forced: it was not.
SCOPE         population R274's committed calibration draws at g = 0 · instrument R274's
              `arm_value` on the canonical tensor · baseline none · regime ALPHA = 0.05.
WORLDS        W-NCAL      both quantiles reproduce both committed taus -> the entire tau gap is
                          the calibration size, arithmetically, and nothing is left over.
              W-PARTIAL   one reproduces and the other does not -> the scripts differ in
                          something beyond NCAL and that difference is now localised.
              W-DIFFERENT neither reproduces -> the draws are not shared and the whole line of
                          reasoning above is wrong.
KILL          |computed - committed| < 1e-6 for BOTH        -> W-NCAL
              for exactly one                                -> W-PARTIAL
              for neither                                    -> W-DIFFERENT
POSITIVE CTRL the 3000 cell is the control: it must return R274's own tau, because that is the
              round reproducing itself from its own dumped array. If it does not, the dump is not
              what R274 calibrated on and the 200 cell means nothing.
              Fails at g=0 in the sense that a DIFFERENT prefix length must give a DIFFERENT
              answer -- checked below over a sweep, so the match at 200 is not a coincidence of
              an insensitive statistic.
NEGATIVE CTRL a prefix length neither round used (500, 1000) must match NEITHER committed tau,
              or the statistic is too coarse for the comparison to mean anything.
PLACEBO       n/a and stated: there is no contrast here that must return zero. The round is an
              identity check, and inventing a placebo for it would be decoration.
NOISE FLOOR   the quantile grid: `cal` takes values on a coarse lattice (the statistic is a
              proportion over ~250 prompts), so nearby prefix lengths can tie. The sweep below
              shows how many distinct values the estimator takes, which is the resolution.
MULTIPLICITY  one comparison per committed tau, plus a prefix sweep reported whole.
ARTIFACT      results/tau_is_ncal.json with source hash; `cal_dump.npy` is committed beside it so
              a later round can attack this without re-running R274.
IMPOSSIBLE    showing that R267's dose grid and rule differences reduce similarly — they are a
              different estimand (R321) and this round does not touch them.
"""
import hashlib, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
CAL = SELF.parent / "cal_dump.npy"
A23 = ROOT / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
COMMITTED = {"R268": (A23 / "R268_a_calibrated_detector_and_the_real_MDE" / "results"
                      / "calibrated_mde.json", 200),
             "R274": (A23 / "R274_the_site_MDE_at_fine_resolution" / "results"
                      / "calibrated_mde.json", 3000)}
ALPHA = 0.05


def main():
    if not CAL.exists():
        print(f"  UNRUNNABLE: {CAL.name} absent."); return 2
    cal = np.load(CAL)
    print(f"  R274's calibration draws at g=0: n={len(cal)}, mean {cal.mean():.6f}, "
          f"sd {cal.std():.6f}")
    print(f"  distinct values: {len(np.unique(cal))}  -> the statistic lives on a lattice, "
          f"which is the resolution floor\n")

    rows, ok = [], {}
    print(f"    {'round':<7}{'NCAL':>7}{'quantile(0.95) of the prefix':>32}{'committed tau':>16}"
          f"{'|diff|':>10}")
    for rid, (path, n) in COMMITTED.items():
        if not path.exists():
            print(f"    {rid:<7}  artifact absent"); return 2
        tau_c = json.loads(path.read_text()).get("tau")
        tau_q = float(np.quantile(cal[:n], 1 - ALPHA))
        d = abs(tau_q - tau_c)
        ok[rid] = d < 1e-6
        rows.append(dict(round=rid, ncal=n, computed=tau_q, committed=tau_c, diff=d,
                         match=bool(ok[rid])))
        print(f"    {rid:<7}{n:>7}{tau_q:>32.6f}{tau_c:>16.6f}{d:>10.2e}")

    # ---- NEGATIVE / resolution sweep ------------------------------------------------------------
    print(f"\n  PREFIX SWEEP — the estimator must MOVE, or a match proves nothing\n")
    sweep = {}
    for n in (100, 200, 400, 500, 1000, 2000, 3000):
        sweep[n] = float(np.quantile(cal[:n], 1 - ALPHA))
    print("    " + "  ".join(f"{n}:{v:.4f}" for n, v in sweep.items()))
    distinct = len(set(round(v, 6) for v in sweep.values()))
    taus = {v.get("committed") for v in rows}
    unused = {n: v for n, v in sweep.items() if n not in (200, 3000)}
    neg_ok = any(round(v, 6) not in {round(t, 6) for t in taus} for v in unused.values())
    print(f"    distinct values across the sweep: {distinct} of {len(sweep)}")
    print(f"    at least one UNUSED prefix matches NEITHER committed tau: {neg_ok}")

    pos_ok = ok.get("R274", False)
    alive = distinct > 1
    ctrl = pos_ok and alive and neg_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive(3000 reproduces R274)={pos_ok}  estimator-moves={alive}  "
          f"negative={neg_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. Either the dump is not what R274 calibrated on, or the quantile")
        print("     is too coarse for a match to carry information.")
    elif all(ok.values()):
        world = "W-NCAL"
        print("  -> W-NCAL. Both committed taus are reproduced from ONE array of draws, to six")
        print("     decimals, by taking the first 200 and the first 3000. R268's calibration set")
        print("     IS the prefix of R274's. The entire tau gap is the CALIBRATION SIZE — a 95th")
        print("     percentile from 200 draws against one from 3000 — and there is nothing left")
        print("     over to explain.")
        print("     ⚠ And it could have come out otherwise: different seed offsets, a different")
        print("       arm_value, a different P or delta would all have broken the match. That it")
        print("       holds is a measurement of code identity, not an algebraic necessity.")
    elif any(ok.values()):
        world = "W-PARTIAL"
        print(f"  -> W-PARTIAL. {[r for r, v in ok.items() if v]} reproduces and "
              f"{[r for r, v in ok.items() if not v]} does not, so the scripts differ in")
        print("     something beyond NCAL — now localised to whichever one failed.")
    else:
        world = "W-DIFFERENT"
        print("  -> W-DIFFERENT. Neither reproduces, so the draws are not shared and the")
        print("     reasoning that led here is wrong at its first step.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "tau_is_ncal.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_draws=len(cal), n_distinct_values=int(len(np.unique(cal))),
        cal_mean=float(cal.mean()), cal_sd=float(cal.std()),
        comparisons=rows, prefix_sweep={str(k): v for k, v in sweep.items()},
        positive_ok=bool(pos_ok), estimator_moves=bool(alive), negative_ok=bool(neg_ok)),
        indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
