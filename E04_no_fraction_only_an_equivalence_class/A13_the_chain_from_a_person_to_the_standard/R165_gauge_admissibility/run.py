"""Every gauge variant that disagrees with the reference has half its discriminating power.

Two turns ago I downgraded the phase's compilation headline on r130's authority: that round showed
the core-minus-full gap FLIPS SIGN under a question-polarity variant, at three seeds, with a drift
four times the effect. I said the direction was therefore not established.

Then the instrument attack ran a zero-shot variant here and produced the largest movement in the
whole sweep -- weight_effect +0.0724 at clustered z 7.01 against a matched baseline of +0.0104 at
z 1.43. And it reported, in passing, that the judge's own output distribution collapsed.

That collapse is the finding, and it was sitting in r130 too.

    variant                      contrast      instrument's discriminating power
    reference                     +0.0093            0.1447
    default fewshot               +0.0104            0.1451
    swapped exemplar order        +0.0109            0.1355
    ZERO-SHOT                     +0.0724            0.0635      <- less than half

    r130 G0 reference             -0.0223            0.2253  (decisiveness)
    r130 G2 label words           -0.0099            0.2541
    r130 G3 QUESTION POLARITY     +0.0708            0.1119      <- less than half

Two independent phases, two different contrasts, same pattern. Every variant that DISAGREES with the
reference has roughly halved the judge's ability to separate the four responses. Every variant that
PRESERVES that ability agrees with the reference, including the label-word swap that r130 itself
grouped with the movers.

A GAUGE VARIANT MUST PRESERVE THE PROPERTY IT GAUGES. Asking whether a reply VIOLATES rather than
SATISFIES a criterion is a legitimate question to ask a judge; it is not a legitimate gauge of the
same instrument if the judge answers it with half the resolution. The resulting disagreement is then
a fact about a worse instrument, not evidence that the original measurement was unstable.

THE OBVIOUS OBJECTION, AND IT IS MINE TO ANSWER. This is a post-hoc admissibility criterion. I am
introducing "preserves discrimination" as a filter AFTER seeing which variants moved the numbers,
which is the researcher degree of freedom this project has been burned by repeatedly. Three things
distinguish it from a rescue, and none of them is decisive alone:

  1  it is principled independently of any outcome -- an instrument that cannot separate the options
     cannot measure a difference between rubrics that rank those options
  2  it is computed from the satisfaction distribution alone and never touches the concordance
     contrast, so it cannot be tuned to produce a verdict
  3  it makes a falsifiable prediction: ANY future variant with halved discrimination should also
     disagree, and any variant preserving it should agree. The label-flipped exemplar run still
     queued is the first out-of-sample test of that prediction, and it was not used to build it.

Until that prediction is tested, this round licenses a downgrade of the sign-flip evidence, not a
restoration of the original claim.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402

import glob
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(round_results("R164").parent))
OUT = HERE / "results"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    from analyze import (REF, arms_and_weight_effect, load_rankings, load_sat,  # noqa: E402
                         load_weights)
    from covalx.cluster import two_way_se  # noqa: E402

    W, rank = load_weights(), load_rankings()
    R = round_results("R164")
    ref_f, ref_c = load_sat(REF / "a04_full.npz"), load_sat(REF / "a04_core.npz")

    def discrimination(sat) -> float:
        """Mean within-criterion spread ACROSS THE FOUR RESPONSES.

        This is the instrument's resolving power on exactly the axis the study needs: if a criterion
        gives all four responses the same satisfaction, it separates nothing, and a rubric built from
        such criteria cannot rank anything. Computed from the satisfaction tensor alone; it never
        sees a human ranking or a concordance."""
        v = [float(np.nanstd(M, axis=1).mean()) for M in sat.values() if M.shape[0]]
        return float(np.mean(v)) if v else float("nan")

    rows = []
    for tag in ("default", "swapped", "no_fewshot", "neg_polarity"):
        f, c = R / f"sat_full_variant_{tag}.npz", R / f"sat_core_variant_{tag}.npz"
        if not (f.exists() and c.exists()):
            rows.append({"variant": tag, "status": "NOT RUN"})
            continue
        sf, sc = load_sat(f), load_sat(c)
        restrict = set(sf) & set(sc)
        _r, keys, we = arms_and_weight_effect(sf, sc, W, rank, restrict=restrict)
        s = two_way_se(we, [p for p, _x in keys], [r for _x, r in keys])
        rows.append({"variant": tag, "contrast": s["mean"], "z": s["z_2way"],
                     "discrimination": round(discrimination(sf), 4), "status": "ok"})
    _r, keys, we = arms_and_weight_effect(ref_f, ref_c, W, rank)
    s = two_way_se(we, [p for p, _x in keys], [r for _x, r in keys])
    rows.insert(0, {"variant": "reference", "contrast": s["mean"], "z": s["z_2way"],
                    "discrimination": round(discrimination(ref_f), 4), "status": "ok"})

    print("THIS PHASE  (weight-deletion contrast, two-way clustered)")
    print(f"{'variant':16s} {'contrast':>10s} {'z':>7s} {'discrimination':>15s}")
    for r in rows:
        if r["status"] != "ok":
            print(f"  {r['variant']:14s} {'':>10s} {'':>7s} {'NOT RUN':>15s}")
            continue
        print(f"  {r['variant']:14s} {r['contrast']:+10.4f} {r['z']:7} {r['discrimination']:15.4f}")

    r130 = []
    for f in sorted(glob.glob(str(round_results("R130").parent
                                  / "results" / "*.json"))):
        d = json.loads(pathlib.Path(f).read_text())
        for k, v in d["variants"].items():
            r130.append({"seed": pathlib.Path(f).stem, "variant": k,
                         "contrast": v.get("core_minus_full_signed"),
                         "decisiveness": v.get("decisiveness_full")})
    print("\nr130, ONE PHASE EARLIER  (core-minus-full contrast, its own decisiveness column)")
    print(f"{'variant':26s} {'contrast':>10s} {'decisiveness':>13s}")
    agg = {}
    for k in sorted({r["variant"] for r in r130}):
        cs = [r["contrast"] for r in r130 if r["variant"] == k]
        ds = [r["decisiveness"] for r in r130 if r["variant"] == k]
        agg[k] = (float(np.mean(cs)), float(np.mean(ds)))
        print(f"  {k:24s} {np.mean(cs):+10.4f} {np.mean(ds):13.4f}")

    ok = [r for r in rows if r["status"] == "ok"]
    base_d = ok[0]["discrimination"]
    print(f"\nEVERY variant whose contrast departs from its reference has roughly HALVED the "
          f"instrument's discrimination:")
    for r in ok[1:]:
        ratio = r["discrimination"] / base_d
        moved = abs(r["contrast"] - ok[0]["contrast"]) > 0.02
        print(f"  {r['variant']:14s} discrimination {ratio:.2f}x reference   "
              f"contrast moved: {moved}")
    r130_base = agg.get("G0_reference", (0, 1))[1]
    for k, (c, d) in agg.items():
        if k == "G0_reference":
            continue
        print(f"  r130 {k:19s} decisiveness {d / r130_base:.2f}x reference   "
              f"contrast moved: {abs(c - agg['G0_reference'][0]) > 0.02}")

    print("\nPREREGISTERED PREDICTION, made before the last variant lands: the queued "
          "label-flipped-exemplar run PRESERVES the task format and should therefore keep "
          "discrimination near 1.0x and AGREE with the reference. If it disagrees while preserving "
          "discrimination, this criterion is wrong and the sign-flip evidence stands as it was.")

    (OUT / "gauge_admissibility.json").write_text(json.dumps(
        {"this_phase": rows, "r130": {k: {"contrast": round(v[0], 4),
                                          "decisiveness": round(v[1], 4)} for k, v in agg.items()},
         "criterion": "a gauge variant must preserve the instrument's discriminating power; one "
                      "that halves it is a different, worse instrument and its disagreement is not "
                      "evidence about the original measurement",
         "post_hoc_warning": "this admissibility filter was introduced AFTER seeing which variants "
                             "moved; it is defended by being outcome-independent and by making a "
                             "falsifiable prediction, not by the numbers it rescues",
         "instrument": "discrimination is computed from the satisfaction tensor alone and never "
                       "touches a human ranking"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
