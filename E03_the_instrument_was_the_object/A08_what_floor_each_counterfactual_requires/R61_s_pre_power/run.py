"""r61 -- Experiment 1's chance baseline and detection floor, computed from the release.

CLAIM CARD
----------
Claim      Experiment 1, as designed, can detect a departure from marginal-matched
           chance agreement between the PRE and POST arms.
Estimand   (a) the POST arm's marginal sign distribution, measured; (b) the
           marginal-matched chance agreement it implies, swept over PRE marginals
           that nobody has observed; (c) the minimum detectable departure at
           plausible n, with the design effect from rater clustering applied.
Target
observed?  PARTLY, and the split is the point. The POST marginal is FULLY observed
           -- 102,147 released ratings. The PRE marginal is NOT OBSERVED BY
           ANYONE: no participant in this release wrote a criterion before seeing
           responses, which is the whole reason S_pre needs an experiment. So it
           is SWEPT, never assumed, and every figure here is conditional on the
           swept value.
Alternative
worlds     A  baseline near 0.5 -- a naive test would have been adequate and the
              preregistration's warning was decorative.
           B  baseline well above 0.5 -- the warning was right, and the n required
              is far larger than a naive calculation gives.
           C  baseline so high that the ceiling leaves little room -- sign
              agreement is a weak instrument for S_pre and the experiment needs a
              different primary outcome, not a bigger sample.
Intervention
           none. Arithmetic on released ratings plus a swept unobserved parameter.
Null       none applicable: this round estimates a floor, it does not test a
           hypothesis. Its positive control is that a degenerate marginal must
           drive chance agreement to 1 and the detectable departure to 0.

WHY THIS EXISTS
---------------
`ADVERSARY_FORECAST.md` objection 5, at P=0.65: Experiment 2 carries reliability,
attenuation and per-rater-count detection floors; Experiment 3 now carries a
flip-rate prior; **Experiment 1 has "fixed n, decided from a pilot" and nothing
else** -- and it is the experiment addressing S_pre. The forecast noted the
baseline is computable from the release today. This computes it, which answers
the objection before a reviewer raises it rather than after.

SCOPE
-----
The design effect uses an intraclass correlation estimated from rater-level
positive-share dispersion in the released POST data. A PRE arm's clustering could
differ, and nothing here measures it.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

PRE_SWEEP = [0.50, 0.60, 0.65, 0.70, 0.7701, 0.85, 0.95]
N_SWEEP = [200, 400, 800, 1600, 3200]


def chance(p1: float, p2: float) -> float:
    """Agreement two independent sign-assigners reach by their marginals alone."""
    return p1 * p2 + (1 - p1) * (1 - p2)


def post_marginal():
    pos = neg = zero = 0
    per_rater = collections.Counter()
    per_rater_pos = collections.Counter()
    for line in open(_ROOT / "data/conversation_rubrics.jsonl"):
        rec = json.loads(line)
        for c in rec.get("coval_full") or []:
            for sc in c.get("scores") or []:
                v = sc.get("score")
                if v is None:
                    continue
                if v > 0:
                    pos += 1
                elif v < 0:
                    neg += 1
                else:
                    zero += 1
                    continue
                a = sc.get("annotator_id")
                per_rater[a] += 1
                per_rater_pos[a] += (v > 0)
    shares = np.array([per_rater_pos[a] / per_rater[a] for a in per_rater if per_rater[a] >= 10])
    sizes = np.array([per_rater[a] for a in per_rater if per_rater[a] >= 10])
    p = pos / (pos + neg)
    # ICC for a binary outcome: observed between-rater variance against the
    # binomial variance expected if every rater drew from the same p.
    expected = p * (1 - p) / sizes.mean()
    observed = float(shares.var(ddof=1))
    icc = max(0.0, (observed - expected) / (p * (1 - p))) if p not in (0.0, 1.0) else 0.0
    return dict(positive=pos, negative=neg, zero=zero, p_positive=p,
                n_raters=len(shares), rater_share_median=float(np.median(shares)),
                rater_share_iqr=[float(np.percentile(shares, 25)),
                                 float(np.percentile(shares, 75))],
                mean_ratings_per_rater=float(sizes.mean()),
                icc=float(icc))


def mde(base: float, n: int, deff: float, z: float = 1.96) -> float:
    """Smallest departure from `base` an n-pair study can distinguish, given deff."""
    se = np.sqrt(base * (1 - base) / n * deff)
    return float(z * se)


def positive_control() -> dict:
    """Degenerate marginals must send chance agreement to 1 and the room to 0."""
    c1 = chance(1.0, 1.0)
    c0 = chance(0.0, 0.0)
    half = chance(0.5, 0.5)
    ok = abs(c1 - 1.0) < 1e-12 and abs(c0 - 1.0) < 1e-12 and abs(half - 0.5) < 1e-12
    return {"chance(1,1)": c1, "chance(0,0)": c0, "chance(.5,.5)": half, "all_pass": bool(ok)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r61_s_pre_power.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    pc = positive_control()
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}  {pc}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the chance-agreement function is wrong on known marginals.")

    m = post_marginal()
    # CRITERIA PER PARTICIPANT IS A DESIGN PARAMETER, NOT A PROPERTY OF THE
    # RELEASE. The first version of this round computed the design effect from
    # the release's 91.9 ratings per rater and reported DEFF = 9.32 -- but an
    # Experiment 1 participant writes a handful of criteria, not ninety. Using
    # the release's cluster size inflated the required n by ~7x. The ICC is the
    # transferable quantity; the cluster size belongs to whoever runs the study.
    M_SWEEP = [3, 5, 10, 20]
    if m["positive"] + m["negative"] == 0:
        raise SystemExit("REFUSING: no ratings observed. An empty population has not passed.")
    p_post = m["p_positive"]
    deff_by_m = {str(mm): 1 + (mm - 1) * m["icc"] for mm in M_SWEEP}
    deff_release = 1 + (m["mean_ratings_per_rater"] - 1) * m["icc"]
    M_PLAN = 5
    deff = deff_by_m[str(M_PLAN)]

    print(f"\nPOST arm, measured on {m['positive'] + m['negative']:,} released ratings:")
    print(f"  P(positive) = {p_post:.4f}   zero used {m['zero']} time(s)")
    print(f"  raters {m['n_raters']}, mean {m['mean_ratings_per_rater']:.1f} ratings each, "
          f"ICC {m['icc']:.4f}")
    print(f"  design effect by CRITERIA PER PARTICIPANT (a design choice): "
          + "  ".join(f"m={k}:{v:.2f}" for k, v in deff_by_m.items()))
    print(f"    the release's own m={m['mean_ratings_per_rater']:.0f} would give "
          f"{deff_release:.2f}, which is NOT this experiment's cluster size")
    print(f"  planning at m={M_PLAN} -> deff {deff:.2f}")

    grid = {}
    print(f"\nchance agreement by PRE marginal (POST fixed at {p_post:.4f}):")
    for p_pre in PRE_SWEEP:
        b = chance(p_pre, p_post)
        grid[f"{p_pre}"] = {"chance": b, "room_above": 1 - b,
                            "mde": {str(n): mde(b, n, deff) for n in N_SWEEP}}
        print(f"  PRE={p_pre:.4f}  chance={b:.4f}  room={1-b:.4f}   "
              f"MDE@n=400 {mde(b,400,deff):.4f}   @n=1600 {mde(b,1600,deff):.4f}")

    base_same = chance(p_post, p_post)
    mde_400 = mde(base_same, 400, deff)
    worst_room = min(1 - chance(p, p_post) for p in PRE_SWEEP)

    world = ("A NAIVE-OK" if base_same < 0.55 else
             "C CEILING-COMPRESSED" if worst_room < 0.10 else
             "B BASELINE-ELEVATED")

    verdict = (
        f"{world}. The POST arm's sign marginal is measured, not assumed: {p_post:.4f} positive over "
        f"{m['positive'] + m['negative']:,} released ratings, with the neutral point used "
        f"{m['zero']} time(s). If the PRE arm shares that marginal, chance agreement is "
        f"{base_same:.4f} -- NOT 0.5 -- leaving {1-base_same:.4f} of room above it, so a naive test "
        f"against 0.5 would report agreement far above chance while measuring nothing but the shared "
        f"tendency to write positive criteria. Rater clustering is real: {m['n_raters']} raters with "
        f">=10 ratings have positive-shares of median {m['rater_share_median']:.3f} "
        f"[{m['rater_share_iqr'][0]:.3f}, {m['rater_share_iqr'][1]:.3f}], giving ICC {m['icc']:.4f} "
        f"and a design effect of {deff:.2f} at the PLANNED {M_PLAN} criteria per participant -- note "
        f"the release's own {m['mean_ratings_per_rater']:.0f} ratings per rater would give "
        f"{deff_release:.2f}, which is not this experiment's cluster size -- "
        f"so the effective n is roughly n/{deff:.2f}, not n. At 400 matched criterion pairs the "
        f"minimum detectable departure is {mde_400:.4f}; reaching 0.02 needs about "
        f"{int(round(400 * (mde_400 / 0.02) ** 2)):,} pairs. THE PRE MARGINAL IS UNOBSERVED BY ANYONE "
        f"-- no participant in this release wrote a criterion before seeing responses, which is why "
        f"S_pre needs an experiment at all -- so it is swept across {PRE_SWEEP[0]:.2f}-"
        f"{PRE_SWEEP[-1]:.2f} and every figure here is conditional on the swept value, with the "
        f"tightest room across that sweep being {worst_room:.4f}."
    )

    doc = {
        "post_marginal": m,
        "design_effect_planned": deff,
        "criteria_per_participant_planned": M_PLAN,
        "design_effect_by_criteria_per_participant": deff_by_m,
        "design_effect_if_release_cluster_size": deff_release,
        "chance_if_pre_matches_post": base_same,
        "room_above_chance": 1 - base_same,
        "mde_at_400_pairs": mde_400,
        "pairs_needed_for_mde_0.02": int(round(400 * (mde_400 / 0.02) ** 2)),
        "pre_marginal_sweep": grid,
        "worst_room_across_sweep": worst_room,
        "world": world,
        "positive_control": pc,
        "scope": ("The PRE marginal is unobserved in this release and is SWEPT, never assumed. The "
                  "design effect uses an ICC estimated from rater-level positive-share dispersion in "
                  "the released POST data; a PRE arm's clustering could differ and nothing here "
                  "measures it. This round estimates a floor and tests no hypothesis."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  chance if PRE matches POST : {base_same:.4f}   room {1-base_same:.4f}")
    print(f"  MDE @ 400 pairs            : {mde_400:.4f}")
    print(f"  pairs for MDE=0.02         : {doc['pairs_needed_for_mde_0.02']:,}")
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
