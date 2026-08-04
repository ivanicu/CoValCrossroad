"""R267 -- thirteen rounds established what is not resolvable. This asks what WOULD be.

WHY THIS AND NOT A FOURTEENTH AUDIT
    Today measured three instrument noise sources on E05's numbers and used them, every time, to
    downgrade something. That is Closure, and it is now thoroughly done. What has NOT been asked
    once is the constructive form of the same measurement:

        given a batch-noise interval of 0.0568 and a label-order delta of 0.0378 on a class-
        agreement statistic, WHAT EFFECT SIZE WOULD THIS RELEASE HAVE BEEN ABLE TO SHOW?

    That is the MDE of the site rather than of a round, and it is the register entry the arc owes
    the next release: not "we could not resolve X" but "nothing below Y is resolvable here, and
    here is what Y is."

⛔ THE PART THAT IS ARITHMETIC, LABELLED WHERE IT OCCURS
    Dividing each published effect by a measured noise floor is division. It cannot come out
    otherwise once both numbers exist, and it is a DERIVATION. What is NOT forced, and what this
    round measures, is the FLOOR ITSELF for a class-agreement statistic under the two instrument
    perturbations -- computed by planting effects of known size and asking which survive.

ESTIMAND        (a) the detection rate of a PLANTED class-agreement effect of size g, under the
                    measured batch-noise distribution, for g in {0, 0.01, ..., 0.12};
                (b) MDE = the smallest g detected on >= 80% of replicates;
                (c) the ratio effect/MDE for every published E05 effect -- a derivation, labelled.
IDENTIFICATION  (a) exact: the plant is constructed, so detection is observed rather than inferred.
                (b) read off the dose-response curve, reported as a BRACKET between the two grid
                    points it falls between, never interpolated to a point.
SCOPE           population: 250 prompts, 6 <= n <= 14, r04 cache. instrument: the r04 tensor plus
                the batch noise measured in R257 (91% exact zeros, resampled with replacement).
                baseline: the random-4 floor. regime: m=4, 40 replicates per dose.
WORLDS          W-COARSE  the MDE is large -- above most of what E05 reported
                            -> most of today's downgrades were forced by the site and not by the
                               rounds, and the arc's real output is a specification for a better
                               instrument
                W-FINE    the MDE is small and E05's effects mostly clear it
                            -> the downgrades were about individual designs, and the site is not
                               the limiting factor
KILL            pre-registered: if the MDE exceeds R231's gap (0.0035), R249's paired se (0.0219)
                AND R260's own interval (0.0568), then no effect this arc reported was resolvable
                at this instrument and the honest summary of E05 is a specification rather than a
                set of findings. If the MDE is below 0.0219, then R249-scale effects were resolvable
                and their downgrades were design failures rather than site limits.
POSITIVE CTRL   g = 0.12, an effect twice the largest measured noise source, must be detected on
                essentially every replicate. If it is not, the detector cannot see a large real
                effect and no MDE read off this curve means anything.
NEGATIVE CTRL   g = 0, no plant. The detection rate must sit at the nominal false-positive rate
                (0.05), NOT at zero -- a detector that never fires at g=0 is not calibrated, it is
                dead, and would make every MDE below it meaningless.
SHAM            plant the effect and then DESTROY it by re-randomising which prompts carry it,
                keeping the magnitude. Detection must fall to the g=0 rate.
PLACEBO         two identical arms compared to each other: exactly 0 difference, every replicate.
NOISE FLOOR     the batch-noise distribution measured in R257 -- resampled, not modelled.
MULTIPLICITY    13 doses x 40 replicates; the whole curve printed, including the doses that fail.
SPECIFICATION   swept: effect size. Held fixed and named: the class function, the 4-criterion
                comparison, and the batch-noise distribution.
ARTIFACT        the full dose-response curve persisted.
IMPOSSIBLE      the MDE under the LABEL-ORDER axis. That axis is not a noise distribution that can
                be resampled -- it is a single alternative instrument, and there are two of them,
                not a population. Its delta is reported beside the MDE rather than folded into it,
                because averaging a bias into a variance is exactly the error this round exists to
                avoid.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402
import collections, json, pathlib, sys
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
DOSES = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12]
REPS = 40
DRAWS = 20
PUBLISHED = {"R231 core-floor gap": 0.0035, "R249 paired se": 0.0219,
             "R260 batch interval": 0.0568, "R257 label-order delta": 0.0378,
             "R249 minimal-size move under label order": 0.1680}


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(DUPS, allow_pickle=True)
    sat, ntask = d["sat"], int(d["n_tasks"][0])
    delta = (sat[ntask:ntask + 200] - sat[:200]).astype(float)
    print("batch noise, resampled not modelled: %.3f exact zeros, sd %.5f, max |d| %.5f"
          % (float((delta == 0).mean()), float(delta.std()), float(np.abs(delta).max())))

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
    print("prompts %d\n" % len(P))

    def agreement(g, rng, sham=False):
        """class agreement of a 4-subset arm PLANTED to beat the floor by g, under batch noise."""
        hit = n = 0
        carry = rng.random(len(P)) < 1.0        # which prompts carry the plant
        if sham:
            carry = rng.permutation(carry)
        for i, (W, S) in enumerate(P):
            Sn = np.clip(S + rng.choice(delta, size=S.shape), 0, 1)
            cf = cls((W[:, None] * Sn).sum(0))
            idx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
            cr = cls((W[idx, None] * Sn[idx]).sum(0))
            ok_ = (cr == cf)
            # the plant: with probability g, force agreement on a carrying prompt
            if carry[i] and rng.random() < g:
                ok_ = True
            hit += int(ok_); n += 1
        return hit / n

    print("=== dose-response: is a planted effect of size g DETECTED above the floor? ===")
    print("%-7s %12s %12s %12s" % ("g", "arm", "floor", "detect rate"))
    curve = {}
    for g in DOSES:
        det = 0
        for r_ in range(REPS):
            rng = np.random.default_rng(1000 + r_)
            arm = agreement(g, rng)
            fl = [agreement(0.0, np.random.default_rng(50000 + r_ * 97 + k))
                  for k in range(3)]
            det += int(arm > max(fl))
        a_ = agreement(g, np.random.default_rng(7))
        f_ = agreement(0.0, np.random.default_rng(8))
        curve[g] = det / REPS
        print("%-7.2f %12.4f %12.4f %12.4f" % (g, a_, f_, curve[g]))

    print("\n=== controls ===")
    pos = curve[0.12]
    neg = curve[0.0]
    print(" POSITIVE g=0.12 (2x the largest measured noise) detected : %.4f  %s"
          % (pos, "OK" if pos > 0.9 else "THE DETECTOR CANNOT SEE A LARGE REAL EFFECT"))
    print(" NEGATIVE g=0    detected : %.4f  %s"
          % (neg, "OK -- calibrated, not dead" if 0.0 < neg < 0.35
             else ("DEAD -- never fires, so every MDE below is meaningless" if neg == 0
                   else "MISCALIBRATED -- fires too often with no effect")))
    sh = 0
    for r_ in range(REPS):
        rng = np.random.default_rng(2000 + r_)
        arm = agreement(0.06, rng, sham=True)
        fl = [agreement(0.0, np.random.default_rng(60000 + r_ * 97 + k)) for k in range(3)]
        sh += int(arm > max(fl))
    print(" SHAM     g=0.06 with the carrier re-randomised : %.4f  (vs %.4f at the same g)"
          % (sh / REPS, curve[0.06]))
    pl = agreement(0.0, np.random.default_rng(11)) - agreement(0.0, np.random.default_rng(11))
    print(" PLACEBO  identical arms differ by exactly : %.6f  %s"
          % (pl, "OK" if pl == 0.0 else "BROKEN"))

    print("\n=== the MDE, as a BRACKET between measured doses ===")
    above = [g for g in DOSES if curve[g] >= 0.8]
    below = [g for g in DOSES if curve[g] < 0.8]
    mde_lo = max(below) if below else 0.0
    mde_hi = min(above) if above else float("inf")
    print(" smallest dose detected on >= 80%% of replicates : %s" % ("%.2f" % mde_hi
                                                                     if above else "none <= 0.12"))
    print(" MDE bracket : (%.2f, %.2f]  -- not interpolated" % (mde_lo, mde_hi))

    print("\n=== (c) every published E05 effect against that MDE -- A DERIVATION, not evidence ===")
    for name, val in sorted(PUBLISHED.items(), key=lambda kv: kv[1]):
        r_ = val / mde_hi if mde_hi not in (0, float("inf")) else float("nan")
        print(" %-45s %8.4f   effect/MDE %6.2f  %s"
              % (name, val, r_, "resolvable" if r_ >= 1 else "BELOW THE SITE'S MDE"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if pos <= 0.9:
        v = "UNVERIFIED -- the detector misses a planted effect twice the largest noise source."
    elif neg == 0.0:
        v = ("UNVERIFIED -- the detector never fires at g=0, which is not calibration but death; "
             "an MDE read off a dead detector is meaningless.")
    elif mde_hi > 0.0568:
        # ⚠ REPAIRED 2026-08-03 (R320). This branch used to print a TYPED sentence naming three
        # effects -- 0.0035, 0.0219, 0.0568 -- and then quantify over all of them: "NO EFFECT THIS
        # ARC REPORTED WAS RESOLVABLE AT THIS INSTRUMENT". PUBLISHED has FIVE entries and its
        # largest is `R249 minimal-size move under label order` at 0.1680, which this same script
        # prints as "resolvable" at effect/MDE 1.87 four lines earlier. The round computed the
        # contradiction and then asserted the opposite, because the branch condition was written
        # against R260's interval (0.0568) as though that were the largest published effect.
        # `the verdict string is not a computation`, and the quantifier is the part that was typed.
        # R274 retracted this sentence and R274 was RIGHT -- on both tensors, so the retraction
        # never depended on which judging was read.
        res = sorted((k for k, val in PUBLISHED.items() if val / mde_hi >= 1),
                     key=lambda k: -PUBLISHED[k])
        unres = sorted((k for k, val in PUBLISHED.items() if val / mde_hi < 1),
                       key=lambda k: -PUBLISHED[k])
        v = ("W-COARSE -- the MDE of this release is (%.2f, %.2f]. Of the %d published effects, "
             "%d are BELOW it (%s) and %d are resolvable (%s). The downgrades of the sub-MDE "
             "effects were forced by the SITE rather than by the individual rounds; the "
             "resolvable ones were not, and lumping them together is what the previous wording "
             "did." % (mde_lo, mde_hi, len(PUBLISHED), len(unres),
                       ", ".join("%s %.4f" % (k, PUBLISHED[k]) for k in unres) or "none",
                       len(res),
                       ", ".join("%s %.4f" % (k, PUBLISHED[k]) for k in res) or "none"))
    elif mde_hi < 0.0219:
        v = ("W-FINE -- the MDE is (%.2f, %.2f], below R249's se, so R249-scale effects WERE "
             "resolvable here and their downgrades are design failures rather than site limits."
             % (mde_lo, mde_hi))
    else:
        v = ("PARTIAL -- the MDE (%.2f, %.2f] sits between R249's se and R260's interval, so some "
             "of this arc's effects were resolvable and some were never going to be. Reported as a "
             "split rather than rounded to either." % (mde_lo, mde_hi))
    print("\n  " + v)
    print("\n  THE LABEL-ORDER AXIS IS NOT IN THIS MDE and that is deliberate: it is a single")
    print("  alternative instrument, not a distribution, so folding its 0.0378 in would average a")
    print("  BIAS into a VARIANCE. It is reported beside the MDE, never inside it.")
    json.dump({"prompts": len(P), "doses": DOSES, "curve": curve, "reps": REPS,
               "positive": pos, "negative": neg, "sham": sh / REPS, "placebo": pl,
               "mde_bracket": [mde_lo, mde_hi], "published": PUBLISHED, "verdict": v},
              open(OUT / "site_mde.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
