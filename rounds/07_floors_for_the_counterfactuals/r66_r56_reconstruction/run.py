"""r66 -- reconstruct r56, whose numbers exist in a commit message and no artifact.

CLAIM CARD
----------
Claim      r56's held-out result -- corr(per-criterion selectivity collapse,
           per-prompt attribution drop) = +0.0198 [-0.1196, +0.1592], NOT
           REPLICATED against its own preregistered [+0.06, +0.30] -- is a fact
           about this data.
Estimand   that correlation, on both samples, recomputed from persisted tensors.
Target
observed?  YES, and that is the problem this round exists for. `rounds/
           r56_semantic_selectivity/` has contained exactly one file, PREDICTION.md,
           in every commit it has ever appeared in. It has never held a run.py or
           a results file. The numbers live in a commit message and in RETRACTIONS
           prose, and searching every artifact in the package for its CI bounds
           `0.1592` and `0.2880` returns NOTHING.
Alternative
worlds     R REPRODUCES   the recomputation lands on r56's published values; the
                          claim was right and only its provenance was missing.
           D DIVERGES     it does not; a number that entered the record through
                          prose was wrong, and entries 55/56 rest on it.
Intervention
           none. Arithmetic on r41's and r46's persisted satisfaction tensors.
Null       the discovery-sample value is also recomputed. If the reconstruction
           reproduces the discovery figure (+0.1806) but not the held-out one, the
           method is right and the disagreement is real; if it reproduces neither,
           the method is wrong and this round says nothing about r56.

WHY THIS EXISTS
---------------
r56 is the round that best exemplifies this project's discipline: a prediction
committed to git BEFORE the held-out number existed (`5cb7426`), then an honest
NOT REPLICATED (`664c568`). It is also the only round whose code was never
committed. **A preregistered failure that cannot be recomputed is a claim resting
on prose**, which is the state this project spends every round refusing to accept
from anyone else.

DEFINITION, taken verbatim from PREDICTION.md
---------------------------------------------
"Per-criterion semantic selectivity = mean over a prompt's criteria of the sd of
judge satisfaction across the four responses. Distinct from r41's D_spread_loss,
which aggregated criteria *first*; this takes the per-criterion spread and then
aggregates."

SCOPE
-----
Judge-relative and equal-weight, inheriting r41's tensor. This reconstructs a
number; it does not re-adjudicate whether the quantity was worth measuring.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

DISCOVERY = _ROOT / "rounds/05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"
# NOTE: r46's tensor is persisted under r41's results directory, not r46's --
# the round that WROTE it is not the round that NAMES it. Found only by listing
# the directory; nothing in the package records where a tensor lives.
HELDOUT = _ROOT / "rounds/05_human_protocol_and_power/r41_criterion_support/results/r46_satisfaction.npz"

PUBLISHED = {"discovery": (0.1806, [0.0708, 0.2880]),
             "held_out": (0.0198, [-0.1196, 0.1592])}
PREDICTED = [0.06, 0.30]


def selectivity(Z, off):
    """Mean over a prompt's criteria of the sd of satisfaction across responses."""
    out = []
    for k in range(len(off) - 1):
        blk = Z[off[k]:off[k + 1]]
        out.append(float(np.mean(blk.std(axis=1))) if blk.shape[0] else np.nan)
    return np.array(out)


def boot_ci(x, y, rng, boot=8000):
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 4:
        return float("nan"), [float("nan")] * 2, 0
    r = float(np.corrcoef(x, y)[0, 1])
    bs = []
    for _ in range(boot):
        i = rng.integers(0, len(x), len(x))
        if np.std(x[i]) == 0 or np.std(y[i]) == 0:
            continue
        bs.append(np.corrcoef(x[i], y[i])[0, 1])
    return r, [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], len(x)


def arm(path, rng):
    d = np.load(path)
    off = d["off_real"].astype(int)
    sel_o = selectivity(d["z_orig_real"], off)
    sel_f = selectivity(d["z_fresh_real"], off)
    collapse = sel_o - sel_f                       # selectivity LOST on fresh
    drop = d["acc_orig_real"] - d["acc_fresh_real"]  # attribution drop
    n = min(len(collapse), len(drop))
    r, ci, used = boot_ci(collapse[:n], drop[:n], rng)
    return {"corr": r, "ci95": ci, "n": used,
            "mean_selectivity_original": float(np.nanmean(sel_o)),
            "mean_selectivity_fresh": float(np.nanmean(sel_f)),
            "mean_collapse": float(np.nanmean(collapse))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tol", type=float, default=0.05,
                    help="how close a recomputation must land to count as reproducing")
    ap.add_argument("--out", type=Path, default=_RES / "r66_r56_reconstruction.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260729)

    for p in (DISCOVERY, HELDOUT):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent; nothing to reconstruct from.")

    got = {"discovery": arm(DISCOVERY, rng), "held_out": arm(HELDOUT, rng)}
    for k, v in got.items():
        pub, pci = PUBLISHED[k]
        v["published_corr"] = pub
        v["published_ci95"] = pci
        v["abs_diff_from_published"] = abs(v["corr"] - pub)
        v["reproduces"] = bool(v["abs_diff_from_published"] <= a.tol)
        print(f"  {k:10s} recomputed {v['corr']:+.4f} {[round(c,4) for c in v['ci95']]}  n={v['n']}"
              f"   published {pub:+.4f} {pci}   diff {v['abs_diff_from_published']:.4f}"
              f"   {'REPRODUCES' if v['reproduces'] else 'DIVERGES'}")

    both = all(v["reproduces"] for v in got.values())
    disc_only = got["discovery"]["reproduces"] and not got["held_out"]["reproduces"]
    ho = got["held_out"]
    fails_prediction = bool(ho["ci95"][0] <= 0 <= ho["ci95"][1] or ho["corr"] < PREDICTED[0])

    world = ("R REPRODUCES" if both else
             "M METHOD-MISMATCH" if not got["discovery"]["reproduces"] else
             "D DIVERGES")

    verdict = (
        f"{world}. r56's numbers exist in a commit message, in its PREDICTION.md, and in "
        f"RETRACTIONS prose -- and in NO ARTIFACT: `rounds/06_the_judges_mechanism/r56_semantic_selectivity/` has contained "
        f"only PREDICTION.md in every commit it has ever appeared in, and a search of every results "
        f"file in this package for its CI bounds 0.1592 and 0.2880 returns nothing. Recomputing the "
        f"quantity its own PREDICTION.md defines, from r41's and r46's persisted tensors: discovery "
        f"{got['discovery']['corr']:+.4f} {[round(c,4) for c in got['discovery']['ci95']]} against a "
        f"published {PUBLISHED['discovery'][0]:+.4f}, held out {ho['corr']:+.4f} "
        f"{[round(c,4) for c in ho['ci95']]} against a published {PUBLISHED['held_out'][0]:+.4f}. "
        f"{'Both land within ' + str(a.tol) + ' of the published values, so the claim was right and only its provenance was missing.' if both else ''}"
        f"{'The discovery arm reproduces and the held-out arm does not, so the method is right and the disagreement is real.' if disc_only else ''}"
        f"{'Neither arm reproduces, so this reconstruction does not share r56 method and says NOTHING about whether r56 was correct -- UNVERIFIED, not overturned.' if not got['discovery']['reproduces'] else ''} "
        f"THE DIRECTION OF r56'S CONCLUSION {'SURVIVES' if fails_prediction else 'DOES NOT SURVIVE'} "
        f"this reconstruction: its preregistered interval was [{PREDICTED[0]}, {PREDICTED[1]}] with a "
        f"CI excluding zero, and the recomputed held-out CI "
        f"{'includes zero' if ho['ci95'][0] <= 0 <= ho['ci95'][1] else 'excludes zero'}. "
        f"WHAT THIS ROUND IS REALLY ABOUT: a preregistered failure that cannot be recomputed is a "
        f"claim resting on prose, and r56 is the round that best exemplifies this project's "
        f"discipline while being the only one whose code was never committed."
    )

    doc = {
        "arms": got,
        "published": {k: {"corr": v[0], "ci95": v[1]} for k, v in PUBLISHED.items()},
        "predicted_interval": PREDICTED,
        "tolerance": a.tol,
        "world": world,
        "r56_has_code_in_repo": False,
        "r56_ci_bounds_found_in_any_artifact": False,
        "scope": ("Judge-relative and equal-weight, inheriting r41's tensor. It reconstructs a "
                  "NUMBER and does not re-adjudicate whether the quantity was worth measuring. If "
                  "the discovery arm fails to reproduce, this round is UNVERIFIED about r56 rather "
                  "than a refutation of it -- a reconstruction that does not share the original's "
                  "method cannot overturn it."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
