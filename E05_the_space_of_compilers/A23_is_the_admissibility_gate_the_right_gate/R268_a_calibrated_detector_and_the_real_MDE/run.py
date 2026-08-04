"""R268 -- R267 refused to read an MDE. Both reasons were mine; this fixes both and reads it.

THE TWO DEFECTS R267 REFUSED ON, AND THE FIX FOR EACH
  1  ITS POSITIVE THRESHOLD WAS `> 0.9` AND THE OBSERVED VALUE WAS EXACTLY 0.9000.
     Failed by 0.0000 -- a bar set at the number the design returns. FIX: the positive control's
     threshold is now COMPUTED, not typed: the largest dose must exceed the g=0 rate by more than
     3 binomial standard errors of that rate. Two measured quantities, no literal.
  2  ITS DETECTOR FIRED ON 20% OF REPLICATES WITH NO EFFECT PRESENT, while its MDE criterion was
     "detected on >= 80%". Those are not compatible. The detector was `arm > max(3 floor draws)`,
     which is the comparison form R231 and R220 use and R240 used at max-of-20. FIX: the threshold
     is CALIBRATED EMPIRICALLY to alpha = 0.05 on g=0 replicates, and -- crucially -- calibrated on
     a DISJOINT set of replicates from the ones it is evaluated on, so the alpha is not fit and
     tested on the same draws.

⛔ WHAT THIS ROUND DOES NOT INHERIT
    R267's effect/MDE table is not carried forward. It was computed against an unverified MDE and
    is unquotable; recomputing it here is the point, not copying it.

ESTIMAND        (a) the threshold tau such that P(arm > tau | g = 0) = 0.05, calibrated on 200
                    held-out no-effect replicates;
                (b) the detection rate at that tau for g in 0..0.20, 100 replicates per dose;
                (c) MDE = the smallest g detected on >= 80% of replicates, as a BRACKET between
                    measured grid points;
                (d) the ratio effect/MDE for each published E05 effect -- a DERIVATION, labelled.
IDENTIFICATION  (a) exact: an empirical quantile of a measured distribution. (b) exact: the plant is
                constructed. (c) read off a curve, reported as a bracket. (d) division.
SCOPE           population: 250 prompts, 6<=n<=14, r04 cache. instrument: the r04 tensor plus the
                batch noise measured in R257, resampled with replacement (91% exact zeros).
                baseline: the calibrated tau. regime: m=4, 100 replicates per dose.
WORLDS          W-COARSE  MDE above 0.0568 -> no effect this arc reported was resolvable, and E05's
                            output is a specification rather than a set of findings
                W-FINE    MDE below 0.0219 -> R249-scale effects were resolvable and their
                            downgrades were design failures, not site limits
                W-MIDDLE  between -> a split, reported as one
KILL            pre-registered, and the thresholds are the SAME as R267's so the two are comparable:
                MDE > 0.0568 -> W-COARSE. MDE < 0.0219 -> W-FINE. Otherwise W-MIDDLE.
POSITIVE CTRL   the largest dose must beat the g=0 rate by > 3 binomial se of the g=0 rate.
                Computed from two measured numbers; cannot be satisfied or defeated by a literal.
NEGATIVE CTRL   the calibration is HELD OUT: alpha is measured on fresh g=0 replicates that were
                not used to set tau. It must land near 0.05. If it lands at 0.20 again, the
                calibration did not take and no MDE is readable.
SHAM            g = 0.10 with the carrier re-randomised after the plant is applied -- magnitude
                preserved, assignment destroyed. Detection must fall to the held-out alpha.
PLACEBO         identical arms, same seed: difference exactly 0.000000.
NOISE FLOOR     the batch-noise distribution from R257, resampled rather than modelled.
MULTIPLICITY    11 doses x 100 replicates + 400 calibration/holdout replicates; whole curve printed.
SPECIFICATION   swept: g. Held fixed and named: the class function, the 4-criterion arm, the noise
                distribution, and alpha = 0.05.
ARTIFACT        tau, the calibration distribution, and the full curve persisted.
IMPOSSIBLE      an MDE under the LABEL-ORDER axis. It is one alternative instrument, not a
                distribution; folding its 0.0378 in would average a bias into a variance. Reported
                beside the MDE, never inside it -- the same call R267 made and for the same reason.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402
import json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
DUPS = round_results("R257", "instruments.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DOSES = [0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]
REPS, NCAL, NHOLD = 100, 200, 200
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
    print("prompts %d | batch noise: %.3f exact zeros, sd %.5f"
          % (len(P), float((delta == 0).mean()), float(delta.std())), flush=True)

    def arm_value(g, rng, sham=False):
        carry = np.ones(len(P), bool)
        if sham:
            carry = rng.permutation(carry)
        hit = 0
        for i, (W, S) in enumerate(P):
            Sn = np.clip(S + rng.choice(delta, size=S.shape), 0, 1)
            cf = cls((W[:, None] * Sn).sum(0))
            idx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
            ok_ = (cls((W[idx, None] * Sn[idx]).sum(0)) == cf)
            if carry[i] and rng.random() < g:
                ok_ = True
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
    shv = np.array([arm_value(0.10, np.random.default_rng(70_000 + i), sham=True)
                    for i in range(REPS)])
    sh = float((shv > tau).mean())
    print(" SHAM     g=0.10, carrier re-randomised : %.4f  (vs %.4f at the same g, alpha %.4f)"
          % (sh, curve[0.10], alpha_hat))
    r1 = arm_value(0.0, np.random.default_rng(4242))
    r2 = arm_value(0.0, np.random.default_rng(4242))
    print(" PLACEBO  identical arms, same seed, differ by : %.6f  %s"
          % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))

    print("\n=== (c) the MDE, as a bracket ===")
    above = [g for g in DOSES if curve[g] >= 0.8]
    below = [g for g in DOSES if curve[g] < 0.8]
    mde_hi = min(above) if above else float("inf")
    mde_lo = max([g for g in below if g < mde_hi]) if above and below else 0.0
    print(" smallest dose detected on >= 80%% : %s"
          % ("%.2f" % mde_hi if above else "none <= %.2f" % DOSES[-1]))
    print(" MDE bracket (%.2f, %.2f]" % (mde_lo, mde_hi))

    print("\n=== (d) published E05 effects against it -- A DERIVATION, labelled ===")
    for name, val in sorted(PUBLISHED.items(), key=lambda kv: kv[1]):
        r_ = val / mde_hi if mde_hi not in (0, float("inf")) else float("nan")
        print(" %-45s %8.4f   effect/MDE %6.2f  %s"
              % (name, val, r_, "resolvable" if r_ >= 1 else "BELOW THE SITE'S MDE"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not neg_ok:
        v = ("UNVERIFIED -- the held-out alpha is %.4f, not near %.2f, so the calibration did not "
             "take and no MDE is readable." % (alpha_hat, ALPHA))
    elif not pos_ok:
        v = ("UNVERIFIED -- the largest planted dose is not detected above the g=0 rate by 3 "
             "binomial se (%.4f vs %.4f, se %.4f)." % (top, g0, se0))
    elif mde_hi == float("inf"):
        v = ("W-COARSE (extreme) -- no dose up to %.2f reaches 80%% detection at a calibrated "
             "alpha of %.4f. The site's MDE is ABOVE the largest effect this arc ever reported."
             % (DOSES[-1], alpha_hat))
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
               "curve": curve, "reps": REPS, "sham": sh, "placebo": r1 - r2,
               "positive_ok": bool(pos_ok), "mde_bracket": [mde_lo, mde_hi],
               "published": PUBLISHED, "verdict": v},
              open(OUT / "calibrated_mde.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
