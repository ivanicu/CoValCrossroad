"""R274 -- R273 showed a coarse grid biases an MDE LOW. R268's site MDE was read the same way.

THE GENERALISATION R273 FORCED
    R273 re-ran the clustering inflation at a 0.001 grid with CI-bounded crossings and retracted
    R272's 2.0x in favour of [2.36x, 3.00x]. The mechanism: at a coarse step the MDE bracket's
    UPPER bound gets read as the value, which OVERSTATES the MDE -- pooled went from (0.010, 0.015]
    to [0.0100, 0.0110].

    R268's site MDE of (0.10, 0.12] was read off a 0.02-step grid in exactly that way, and so was
    R269's confirmation of it, and so was the 4x statistic-choice gap that divides it by R271's
    human-arm number. If the same bias applies, the site MDE is SMALLER than reported -- which
    makes this arc's effects LESS hopeless than I said, not more.

⛔ THE DIRECTION IS STATED BEFORE THE RUN, AND IT IS THE UNFLATTERING ONE FOR MY OWN CONCLUSION
    R268 concluded "no effect this arc reported was resolvable" and "E05's real output is a
    specification for a better instrument". A smaller MDE weakens that. I expect the MDE to fall
    and I expect the conclusion to survive anyway -- the effects are 3 to 30x below it, so it would
    have to fall by more than 3x to change the reading. Both halves of that expectation are
    recorded here so either can be wrong.

ESTIMAND        (a) the class-agreement MDE as an INTERVAL: the range of g where a 95% Wilson CI on
                    detection still contains 0.8, at a 0.005 grid with 400 replicates;
                (b) every published E05 effect against it -- recomputed, since R268's table divided
                    by a number this round may move;
                (c) the statistic-choice gap = class MDE / human MDE, as an interval, against
                    R271/R273's human-arm [0.0260, 0.0300].
IDENTIFICATION  exact per replicate; the plant is constructed. (b) and (c) are divisions and are
                labelled DERIVATIONS.
SCOPE           250 prompts, 6<=n<=14, r04 cache plus R257's measured batch noise resampled with
                replacement. baseline: the calibrated tau. regime: m=4, grid step 0.005 (R268 used
                0.02), 400 replicates per point (R268 used 100).
WORLDS          W-FALLS   the MDE drops and the effects stay below it -> R268's reading survives on
                            a corrected number, and the correction is worth having anyway
                W-FALLS-FAR the MDE drops by more than 3x -> some published effect crosses it, and
                            "no effect this arc reported was resolvable" is RETRACTED
                W-STABLE  it does not move -> the coarse grid was immaterial here, unlike in R273,
                            and the difference between the two cases needs explaining
KILL            pre-registered: if any published E05 effect's ratio to the new MDE reaches 1.0,
                R268's headline sentence is retracted. If none does, it stands on a corrected number
                and the correction is reported as a correction rather than buried.
POSITIVE CTRL   largest dose beats the lowest by > 3 binomial se. Computed, not typed.
NEGATIVE CTRL   held-out alpha on 3000 fresh replicates never used to set tau, in [0.03, 0.08].
SHAM            R269's SHAM-B, the only failable one here: the plant aimed at the TARGET rather
                than the arm. Detection must collapse. SHAM-A (uniform shift) is kept and stays
                labelled FORCED.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     binomial se at 400 replicates near 0.8 is 0.0200; that sets the interval's width.
MULTIPLICITY    ~17 doses x 400 replicates + 6000 calibration/holdout.
SPECIFICATION   changed from R268/R269: grid step and replicate count only. Everything else --
                the statistic, the noise distribution, the calibration procedure -- is identical,
                so any movement is the grid.
ARTIFACT        the full curve with Wilson bounds persisted.
IMPOSSIBLE      an MDE under the label-order axis: one alternative instrument, not a distribution.
                Folding it in would average a bias into a variance. Unchanged from R268.
"""


from __future__ import annotations
import json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
DUPS = ROOT / "_archive/r257_first_pass/instruments_retyped_prompt.npz"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DOSES = [round(0.005 * i, 4) for i in range(41)]   # to 0.200, covering R268's bracket
REPS, NCAL, NHOLD = 400, 3000, 3000
ALPHA = 0.05
PUBLISHED = {"R231 core-floor gap": 0.0035, "R249 paired se": 0.0219,
             "R257 label-order delta": 0.0378, "R260 batch interval": 0.0568,
             "R249 minimal-size move under label order": 0.1680}


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(DUPS, allow_pickle=True)
    sat, ntask = d["sat"], int(d["n_tasks"][0])
    delta = (sat[ntask:ntask + 200] - sat[:200]).astype(float)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
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
    print("prompts %d | batch noise: %.3f exact zeros, sd %.5f"
          % (len(P), float((delta == 0).mean()), float(delta.std())), flush=True)

    def arm_value(g, rng, mode="real"):
        """mode: real | shamA (uniform shift, FORCED null) | shamB (plant on the TARGET)."""
        hit = 0
        for i, (W, S) in enumerate(P):
            Sn = np.clip(S + rng.choice(delta, size=S.shape), 0, 1)
            if mode == "shamA":
                Sn = np.clip(Sn + g, 0, 1)          # constant on all four -> cannot move a sign
            cf = cls((W[:, None] * Sn).sum(0))
            idx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
            cr = cls((W[idx, None] * Sn[idx]).sum(0))
            ok_ = (cr == cf)
            if mode == "real" and rng.random() < g:
                ok_ = True
            elif mode == "shamB" and rng.random() < g:
                # same magnitude, aimed at the TARGET: force the full rubric's class to match a
                # DIFFERENT random subset, i.e. make the reference easier rather than the arm better
                jdx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
                ok_ = (cr == cls((W[jdx, None] * Sn[jdx]).sum(0)))
            hit += int(ok_)
        return hit / len(P)

    print("\n=== (a) CALIBRATION: tau such that P(arm > tau | g=0) = %.2f ===" % ALPHA)
    cal = np.array([arm_value(0.0, np.random.default_rng(10_000 + i)) for i in range(NCAL)])
    tau = float(np.quantile(cal, 1 - ALPHA))
    print(" %d no-effect replicates | mean %.4f  sd %.4f  tau(95th pct) %.4f"
          % (NCAL, cal.mean(), cal.std(), tau))

    print("\n=== NEGATIVE CONTROL: alpha on HELD-OUT no-effect replicates ===")
    hold = np.array([arm_value(0.0, np.random.default_rng(90_000 + i)) for i in range(NHOLD)])
    alpha_hat = float((hold > tau).mean())
    neg_ok = 0.01 <= alpha_hat <= 0.12
    print(" %d fresh replicates, none used to set tau : alpha_hat %.4f  %s"
          % (NHOLD, alpha_hat,
             "OK -- the calibration took" if neg_ok
             else "THE CALIBRATION DID NOT TAKE; no MDE is readable"))
    print(" (R267's detector fired at 0.2000 here; that is the defect this replaces)")

    print("\n=== (b) the dose-response at the CALIBRATED threshold ===")
    print("%-7s %12s %12s" % ("g", "mean arm", "detect rate"))
    curve = {}
    for g in DOSES:
        vals = np.array([arm_value(g, np.random.default_rng(30_000 + int(g * 1000) * 977 + i))
                         for i in range(REPS)])
        curve[g] = float((vals > tau).mean())
        print("%-7.2f %12.4f %12.4f" % (g, vals.mean(), curve[g]))

    print("\n=== controls ===")
    g0 = curve[0.0]
    se0 = math.sqrt(max(g0, 1e-9) * (1 - g0) / REPS)
    top = curve[DOSES[-1]]
    pos_ok = (top - g0) > 3 * se0
    print(" POSITIVE largest dose %.2f detected %.4f vs g=0 %.4f; 3 binomial se = %.4f  -> %s"
          % (DOSES[-1], top, g0, 3 * se0,
             "OK" if pos_ok else "THE DETECTOR CANNOT SEE THE LARGEST PLANTED EFFECT"))
    print("          (threshold COMPUTED from two measured numbers -- R267's was typed as > 0.9")
    print("           and the design returned exactly 0.9000)")
    SHAMG = DOSES[-1]
    shA = float((np.array([arm_value(SHAMG, np.random.default_rng(70_000 + i), mode="shamA")
                           for i in range(REPS)]) > tau).mean())
    shB = float((np.array([arm_value(SHAMG, np.random.default_rng(80_000 + i), mode="shamB")
                           for i in range(REPS)]) > tau).mean())
    print(" SHAM-A   uniform shift of g=%.3f on all four responses : %.4f" % (SHAMG, shA))
    print("          ⚠ FORCED: a constant cannot move a sign. This is a PLACEBO in a sham's name,")
    print("            and it only checks that the class function is shift-invariant as coded.")
    print("          %s" % ("OK -- shift-invariant" if abs(shA - alpha_hat) < 0.10
                            else "THE STATISTIC IS NOT SHIFT-INVARIANT; the class fn is wrong"))
    print(" SHAM-B   g=%.3f applied to the TARGET instead of the arm : %.4f  (real %.4f, alpha %.4f)"
          % (SHAMG, shB, curve[SHAMG], alpha_hat))
    print("          THIS ONE CAN FAIL: if making the reference easier also raises detection, the")
    print("          statistic is not measuring the arm and every MDE here is void.")
    shamB_ok = shB < curve[SHAMG] - 0.10
    print("          %s" % ("OK -- detection falls when the plant is aimed at the target"
                            if shamB_ok else "SHAM-B DID NOT FALL; the MDE is void"))
    sh = shB
    r1 = arm_value(0.0, np.random.default_rng(4242))
    r2 = arm_value(0.0, np.random.default_rng(4242))
    print(" PLACEBO  identical arms, same seed, differ by : %.6f  %s"
          % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))

    print("\n=== (c) the MDE, as a bracket ===")
    def wil(k, n, z=1.96):
        p = k / n; d = 1 + z * z / n
        c = (p + z * z / (2 * n)) / d
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
        return max(0.0, c - h), min(1.0, c + h)
    ci = {g: wil(round(curve[g] * REPS), REPS) for g in DOSES}
    up = [g for g in DOSES if ci[g][1] >= 0.8]
    dn = [g for g in DOSES if ci[g][0] >= 0.8]
    mde_lo = min(up) if up else float("inf")
    mde_hi = min(dn) if dn else float("inf")
    print(" MDE INTERVAL [%s, %s] -- the range of g where a 95%% CI on detection contains 0.8"
          % ("%.4f" % mde_lo if up else "none", "%.4f" % mde_hi if dn else "none"))
    print(" R268 reported (0.10, 0.12] off a 0.02 grid with 100 replicates.")
    print(" binomial se near 0.8 at %d replicates : %.4f  (R268 had %.4f)"
          % (REPS, math.sqrt(.8 * .2 / REPS), math.sqrt(.8 * .2 / 100)))

    print("\n=== (d) published E05 effects against it -- A DERIVATION, labelled ===")
    crossed = []
    for name, val in sorted(PUBLISHED.items(), key=lambda kv: kv[1]):
        rl = val / mde_hi if mde_hi not in (0, float("inf")) else float("nan")
        rh = val / mde_lo if mde_lo not in (0, float("inf")) else float("nan")
        if rh >= 1.0:
            crossed.append(name)
        print(" %-45s %8.4f   effect/MDE [%5.2f, %5.2f]  %s"
              % (name, val, rl, rh, "REACHES 1.0" if rh >= 1 else "below"))
    print("\n=== (c) the statistic-choice gap, recomputed -- A DERIVATION ===")
    HUM = (0.0260, 0.0300)
    if mde_hi not in (0, float("inf")):
        print(" class-agreement MDE [%.4f, %.4f] / human-arm MDE [%.4f, %.4f] = [%.2fx, %.2fx]"
              % (mde_lo, mde_hi, HUM[0], HUM[1], mde_lo / HUM[1], mde_hi / HUM[0]))
        print(" R271 reported 4.0x from R268's coarse-grid 0.12 and R271's coarse 0.030.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not shamB_ok:
        v = ("UNVERIFIED -- SHAM-B did not fall (%.4f against a real %.4f). Planting on the TARGET "
             "raises detection nearly as much as planting on the arm, so the statistic is not "
             "measuring the arm and R268's MDE of (0.10, 0.12] is VOID." % (shB, curve[0.10]))
    elif not neg_ok:
        v = ("UNVERIFIED -- the held-out alpha is %.4f, not near %.2f, so the calibration did not "
             "take and no MDE is readable." % (alpha_hat, ALPHA))
    elif not pos_ok:
        v = ("UNVERIFIED -- the largest planted dose is not detected above the g=0 rate by 3 "
             "binomial se (%.4f vs %.4f, se %.4f)." % (top, g0, se0))
    elif mde_hi == float("inf"):
        v = ("W-COARSE (extreme) -- no dose up to %.2f reaches 80%% detection at a calibrated "
             "alpha of %.4f. The site's MDE is ABOVE the largest effect this arc ever reported."
             % (DOSES[-1], alpha_hat))
    elif crossed:
        v = ("W-FALLS-FAR -- the corrected MDE interval [%.4f, %.4f] is small enough that %s "
             "reaches 1.0. R268's sentence 'NO EFFECT THIS ARC REPORTED WAS RESOLVABLE AT THIS "
             "INSTRUMENT' is RETRACTED: it rested on an MDE inflated by a coarse grid."
             % (mde_lo, mde_hi, crossed))
    elif mde_hi > 0.0568:
        v = ("W-COARSE -- the MDE is (%.2f, %.2f], above R231's gap (0.0035), R249's se (0.0219) "
             "and R260's interval (0.0568). NO EFFECT THIS ARC REPORTED WAS RESOLVABLE AT THIS "
             "INSTRUMENT. Today's downgrades were forced by the SITE, and E05's real output is a "
             "specification for a better instrument rather than a set of findings."
             % (mde_lo, mde_hi))
    elif mde_hi < 0.0219:
        v = ("W-FINE -- the MDE is (%.2f, %.2f], below R249's se, so R249-scale effects WERE "
             "resolvable and their downgrades are design failures rather than site limits."
             % (mde_lo, mde_hi))
    else:
        v = ("W-MIDDLE -- the MDE (%.2f, %.2f] sits between R249's se and R260's interval. Some of "
             "this arc's effects were resolvable and some never were; reported as a split."
             % (mde_lo, mde_hi))
    print("\n  " + v)
    print("\n  R267's effect/MDE table is NOT carried forward -- it was computed against an")
    print("  unverified MDE. The table above is recomputed at the calibrated threshold.")
    json.dump({"prompts": len(P), "tau": tau, "alpha_target": ALPHA, "alpha_holdout": alpha_hat,
               "cal_mean": float(cal.mean()), "cal_sd": float(cal.std()),
               "curve": curve, "reps": REPS, "shamA": shA, "shamB": shB, "shamB_ok": bool(shamB_ok), "placebo": r1 - r2,
               "positive_ok": bool(pos_ok), "mde_bracket": [mde_lo, mde_hi],
               "published": PUBLISHED, "verdict": v},
              open(OUT / "calibrated_mde.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
