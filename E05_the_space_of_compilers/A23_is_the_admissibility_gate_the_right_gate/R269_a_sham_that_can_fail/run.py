"""R269 -- R268's sham was void AS CONCEIVED, not merely as coded. Two shams that can fail.

WHAT WENT WRONG AND WHY THE OBVIOUS FIX IS ALSO WRONG
    R268 declared a sham that re-randomises WHICH prompts carry the plant. Its carrier vector was
    all-True, so permuting it was literally a no-op -- it returned 0.7200 against 0.7700 at the
    same g where it should have collapsed to alpha.

    The obvious repair is to make the carrier a random half. THAT IS ALSO VOID: prompts are
    exchangeable here, so permuting WHICH exchangeable units carry an effect changes nothing in
    distribution, at any fill rate. A sham has to destroy something the statistic depends on, and
    "which prompt" is not such a thing.

TWO REPLACEMENTS, AND ONLY ONE OF THEM IS A TEST
  SHAM-A  UNIFORM SHIFT. Add g to every response's satisfaction equally. A weak ordering is a
          function of DIFFERENCES, so a constant added to all four cannot change any sign.
          ⚠ FORCED BY ALGEBRA -- this is a PLACEBO wearing a sham's name, and it is included only
          to check that the statistic really is shift-invariant in the implementation. Detection
          MUST equal alpha, and if it does not, the class function is not what it claims.
  SHAM-B  WRONG TARGET. Apply the plant of the same magnitude to the FULL RUBRIC's class instead
          of to the arm -- same intervention, same compute, aimed at the object that is supposed
          to be the reference rather than the thing under test. Detection must fall toward alpha.
          THIS ONE CAN FAIL: if making the target easier ALSO raises detection, the statistic is
          not measuring the arm at all, and every MDE in R268 is void.

EVERYTHING ELSE IS R268's, UNCHANGED: the empirical calibration to alpha=0.05 on 200 replicates,
the HELD-OUT validation on 200 fresh ones, the computed positive threshold (3 binomial se of the
g=0 rate, two measured numbers and no literal), and the same dose grid so the two rounds are
directly comparable. R268's MDE of (0.10, 0.12] is the number this round is checking, not repeating.
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
    shA = float((np.array([arm_value(0.10, np.random.default_rng(70_000 + i), mode="shamA")
                           for i in range(REPS)]) > tau).mean())
    shB = float((np.array([arm_value(0.10, np.random.default_rng(80_000 + i), mode="shamB")
                           for i in range(REPS)]) > tau).mean())
    print(" SHAM-A   uniform shift of g=0.10 on all four responses : %.4f" % shA)
    print("          ⚠ FORCED: a constant cannot move a sign. This is a PLACEBO in a sham's name,")
    print("            and it only checks that the class function is shift-invariant as coded.")
    print("          %s" % ("OK -- shift-invariant" if abs(shA - alpha_hat) < 0.10
                            else "THE STATISTIC IS NOT SHIFT-INVARIANT; the class fn is wrong"))
    print(" SHAM-B   g=0.10 applied to the TARGET instead of the arm : %.4f  (real %.4f, alpha %.4f)"
          % (shB, curve[0.10], alpha_hat))
    print("          THIS ONE CAN FAIL: if making the reference easier also raises detection, the")
    print("          statistic is not measuring the arm and every MDE here is void.")
    shamB_ok = shB < curve[0.10] - 0.10
    print("          %s" % ("OK -- detection falls when the plant is aimed at the target"
                            if shamB_ok else "SHAM-B DID NOT FALL; the MDE is void"))
    sh = shB
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
    elif mde_hi > 0.0568:
        # ⚠ REPAIRED 2026-08-03 (R320). The old wording named three effects -- 0.0035, 0.0219,
        # 0.0568 -- and then quantified over all of them: "NO EFFECT THIS ARC REPORTED WAS
        # RESOLVABLE AT THIS INSTRUMENT". PUBLISHED holds FIVE, topping out at 0.1680, which this
        # same script prints as `resolvable` fifteen lines earlier. The branch tested `is the MDE
        # above R260's interval` as though that were the largest published effect. The numbers
        # were right and the word `NO` was typed. R274 retracted this sentence and was correct.
        # ⚠ AND THIS IS THE SECOND AND THIRD SITE: R267 carried the identical defect and was fixed
        # first, alone, because it was the round I happened to be reading. `a fix lands on one path
        # of two` -- the invariant is "a verdict that quantifies over PUBLISHED must compute the
        # quantification", and enumerating its carriers found three.
        res = sorted((k for k, val in PUBLISHED.items() if val / mde_hi >= 1),
                     key=lambda k: -PUBLISHED[k])
        unres = sorted((k for k, val in PUBLISHED.items() if val / mde_hi < 1),
                       key=lambda k: -PUBLISHED[k])
        v = ("W-COARSE -- the MDE is (%.2f, %.2f]. Of the %d published effects, %d are BELOW it "
             "(%s) and %d are resolvable (%s). The sub-MDE downgrades were forced by the SITE; "
             "the resolvable ones were not."
             % (mde_lo, mde_hi, len(PUBLISHED), len(unres),
                ", ".join("%s %.4f" % (k, PUBLISHED[k]) for k in unres) or "none",
                len(res), ", ".join("%s %.4f" % (k, PUBLISHED[k]) for k in res) or "none"))
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
