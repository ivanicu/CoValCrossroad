"""R229 -- the control band, and a replay of the four times I set an impossible threshold.

Arc E05.A05. The decision this makes safe: HOW DO I SET A POSITIVE CONTROL'S THRESHOLD?

Three of the last five rounds failed first on a control whose target the design made unreachable.
realstat §4 already names the mirror image -- "check that cannot fail", built 4x caught 4x -- and
has nothing for this direction. P7: the third instance is infrastructure, not a third patch.

ESTIMAND        for each historical control: was its registered threshold inside [floor, ceiling]?
IDENTIFICATION  exact -- floor, ceiling and threshold are all recorded in the rounds' own outputs.
SCOPE           the four positive controls in E05 whose numbers are persisted. NOT a survey of the
                whole repository: 217 rounds do not record their ceilings, and claiming otherwise
                would be the completeness-over-a-visible-subset failure this repo has hit before.
WORLDS          W1 the three failures share one cause -> a single band check catches all of them
                W2 they are unrelated accidents       -> the check catches some and misses others
KILL            if the band check does not catch all three known failures, it is not the mechanism
                and this round's diagnosis is wrong.
POSITIVE CTRL   the checker itself must FIRE on the three known-bad thresholds. A checker that has
                never caught anything is silence, not an acquittal.
NEGATIVE CTRL   it must NOT fire on the thresholds that were admissible (R227's, R226's).
NOISE FLOOR     n/a -- every input is a recorded constant, not a sample. This is a DERIVATION over
                recorded values and is labelled one.
IMPOSSIBLE      whether the rounds BEFORE E05 have the same defect. They do not record ceilings,
                so the honest answer is UNVERIFIED, not "clean".
"""
from __future__ import annotations
import pathlib, sys, json

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx.control_band import check, ControlBandError

OUT = pathlib.Path(__file__).resolve().parent / "results"

# (round, what the control measured, floor, ceiling, threshold I registered, what it returned)
HISTORY = [
    ("R221 posthoc",  "selection rate of a winner-predictor by a RANK-fitter",
     0.2713, 0.2713, 0.2713, 0.0537),
    ("R225a dispersion", "tie-count ratio under planted rater dispersion",
     1.0000, 1.0000, 0.5000, 0.9650),
    ("R225b sparsity", "tie-count ratio under planted sparsity",
     1.0000, 1.0000, 0.5000, 0.9970),
    ("R228 recovery", "recovery of a planted k=1 subset at zero noise",
     0.0870, 0.7269, 0.9000, 0.7269),
    # the two that WERE admissible, as the negative control for the checker
    ("R227 richness", "recovery at g10 vs rank",
     0.0182, 0.9993, 0.0527, 0.0690),
    ("R226 entropy",  "empirical entropy of the ordering",
     0.0000, 6.2288, 3.0000, 5.9561),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("=== replaying every positive control in E05 through the band check ===")
    print("%-20s %9s %9s %9s %9s   %s"
          % ("control", "floor", "ceiling", "threshold", "observed", "verdict"))
    caught, ok, rows = [], [], []
    for name, what, fl, ce, th, obs in HISTORY:
        try:
            v = check(name, fl, ce, th, obs)
            print("%-20s %9.4f %9.4f %9.4f %9.4f   admissible (used %.0f%% of the band)"
                  % (name, fl, ce, th, obs, 100 * v["headroom_used"]))
            ok.append(name); rows.append({**v, "measured": what})
        except ControlBandError as e:
            kind = "CANNOT PASS" if th >= ce else "CANNOT FAIL"
            print("%-20s %9.4f %9.4f %9.4f %9.4f   %s" % (name, fl, ce, th, obs, kind))
            print("      %s" % str(e).split(" -- ")[1].split(".")[0])
            caught.append(name)
            rows.append({"name": name, "floor": fl, "ceiling": ce, "threshold": th,
                         "observed": obs, "admissible": False, "kind": kind, "measured": what})

    known_bad = {"R221 posthoc", "R225a dispersion", "R225b sparsity", "R228 recovery"}
    known_good = {"R227 richness", "R226 entropy"}
    print("\n=== controls on the checker itself ===")
    pos = known_bad <= set(caught)
    neg = known_good <= set(ok)
    print(" POSITIVE  fires on all %d known-bad thresholds : %s  (%d/%d)"
          % (len(known_bad), "OK" if pos else "MISSES SOME",
             len(known_bad & set(caught)), len(known_bad)))
    print(" NEGATIVE  silent on the %d admissible ones      : %s  (%d/%d)"
          % (len(known_good), "OK" if neg else "FALSE POSITIVE",
             len(known_good & set(ok)), len(known_good)))

    print("\n" + "=" * 78)
    print("KILL: is one mechanism behind all three failures?")
    print("=" * 78)
    if pos and neg:
        v = ("SUPPORTED -- a single band check catches all four impossible thresholds and fires on "
             "neither admissible one. They are one habit, not four accidents: setting a control's "
             "target by intuition about what success looks like, without computing what the design "
             "can return when the plant is maximal.")
    else:
        v = "REFUTED -- the band check is not the common mechanism; the diagnosis is wrong."
    print("\n  " + v)
    print("\n  Note the shape of the first three: floor == ceiling. The statistic returns the SAME")
    print("  value under a maximal plant as under none, so NO threshold on it is admissible and")
    print("  the defect is the STATISTIC, not the number I picked. R228 is the other kind: a real")
    print("  band, 0.0870 to 0.7269, and a threshold of 0.90 outside it.")
    (OUT / "control_band.json").write_text(json.dumps(
        {"rows": rows, "caught": caught, "admissible": ok, "verdict": v}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
