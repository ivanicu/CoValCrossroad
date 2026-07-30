"""r27 -- The separator my own separator could not be: raw-scale anti-correlation.

Why r23/r25/r26's sign test was the wrong statistic
---------------------------------------------------
All three asked whether a pair's RESIDUAL -- agreement after removing the prompt
mean and the additive actor effect -- is reliably negative.  I claimed that
answered the M2-vs-competence question, on the grounds that "noise attenuates
agreement toward zero and cannot drive it below."

That reasoning is right and the statistic does not implement it.  Population mean
agreement is +0.2513.  A pair with ZERO competence -- two raters who track each
other not at all -- has agreement about 0, which is 0.25 BELOW the mean, so its
residual is strongly negative.  A centred residual scores "below average" and
"actually disagreeing" identically, and those are exactly the two worlds the test
was built to separate.

So r26's `SIGNED` verdicts do not mean what the field name says.  The three-way
question has to be asked on the RAW scale, where zero is a real boundary rather
than an artifact of centring:

    no pair structure          observed == null everywhere
    competence heterogeneity   excess mass JUST BELOW zero (attenuation piles up
                               there) and NO excess in the far tail, because
                               attenuation moves toward zero and stops
    value blocs                excess in the FAR NEGATIVE TAIL -- pairs that are
                               genuinely anti-correlated, systematically valuing
                               opposite things

The far tail is the discriminator.  Attenuation cannot reach it; opposing
structure can.  Reading the two thresholds together is the whole round: a
competence world and a bloc world make DIFFERENT predictions about the SHAPE of
the excess, not merely its presence.

Null
----
Permute agreement values across dyad slots WITHIN each prompt.  This preserves
each prompt's agreement distribution exactly -- so "some prompts are just harder"
cannot masquerade as pair structure -- and destroys only which pair held which
value.  Note what it does NOT preserve: the additive actor effect.  So an excess
here is evidence of pair-or-actor structure over none, and the actor share is
already measured (47.2%, r23).  The SHAPE comparison across thresholds is what
carries the M2-vs-competence inference, and shape is not something an actor
effect predicts asymmetrically.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))
from covalx.frozen import append_to as _freeze  # noqa: E402


import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"

THRESHOLDS = (0.0, -0.05, -0.10, -0.20, -0.30)


def _cell():
    spec = importlib.util.spec_from_file_location(
        "cell", _ROOT / "03_person_or_pair/r25_actor_dyad_sweep/cell.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def series(data, cell, cfg, rng, permute=False):
    raw = defaultdict(list)
    for rec in data:
        mat = cell.standardize(rec["m"]) if cfg["standardize"] else rec["m"]
        ag = cell.pair_agreements(mat, rec["raters"], cfg["metric"], cfg["min_overlap"])
        if len(ag) < 3:
            continue
        vals = list(ag.values())
        if permute:
            vals = list(rng.permutation(vals))
        for k, v in zip(ag.keys(), vals):
            raw[frozenset(k)].append(float(v))
    return raw


def tail_profile(raw, min_prompts, keep=None):
    """keep: optional set of pair keys to restrict to (a stratum)."""
    items = [(k, v) for k, v in raw.items()
             if len(v) >= min_prompts and (keep is None or k in keep)]
    if len(items) < 100:
        return None
    means = np.array([np.mean(v) for _k, v in items])
    allneg = np.array([float(np.all(np.array(v) < 0)) for _k, v in items])
    return {"n": int(len(means)), "mean": float(means.mean()),
            "below": {f"{t:+.2f}": float((means < t).mean()) for t in THRESHOLDS},
            "all_negative": float(allneg.mean())}


def partner_means(raw):
    """rater -> {partner: their mean agreement}. Kept per-partner so the actor
    score can be recomputed LEAVE-ONE-OUT for each pair under test."""
    by = defaultdict(dict)
    for pair, vals in raw.items():
        u, v = tuple(pair)
        m = float(np.mean(vals))
        by[u][v] = m
        by[v][u] = m
    return by


def both_high_pairs(raw, by, min_prompts, min_partners=4):
    """Pairs where BOTH raters are generally agreeable WITH EVERYONE ELSE.

    The control that separates the last two explanations for a negative tail.
    If the tail is an ACTOR effect -- some people are simply disagreeable, and
    two of them together look anti-correlated -- the excess must disappear among
    pairs of two agreeable raters.  If it is BLOCS it survives, because two
    raters can each sit inside their own large bloc, agree with everyone there,
    and still be anti-correlated with each other.

    ** LEAVE-ONE-OUT, and this is not optional. **  A pair's own agreement feeds
    both of its members' actor scores.  Selecting "both above median" on scores
    that include this pair therefore selects directly on the outcome being
    tested: high-agreement pairs raise their own members' scores and get kept,
    low-agreement pairs lower theirs and get dropped.  That alone would push the
    stratum's negative tail below the null and manufacture exactly the result
    the control is supposed to check for.  So each rater's score is recomputed
    excluding the partner under test.
    """
    med = float(np.median([np.mean(list(d.values())) for d in by.values() if d]))
    keep = set()
    for pair, vals in raw.items():
        if len(vals) < min_prompts:
            continue
        u, v = tuple(pair)
        du, dv = by.get(u, {}), by.get(v, {})
        ou = [m for p, m in du.items() if p != v]
        ov = [m for p, m in dv.items() if p != u]
        if len(ou) < min_partners or len(ov) < min_partners:
            continue
        if float(np.mean(ou)) > med and float(np.mean(ov)) > med:
            keep.add(pair)
    return keep, med


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r27_raw_negative_tail.json")
    p.add_argument("--metric", default="pearson",
                   choices=["pearson", "spearman", "cosine", "negl1"])
    p.add_argument("--min-overlap", type=int, default=3)
    p.add_argument("--thr", default="majority")
    p.add_argument("--standardize", type=int, default=1)
    p.add_argument("--min-prompts", type=int, default=3)
    p.add_argument("--null-reps", type=int, default=200)
    a = p.parse_args()

    cell = _cell()
    cfg = {"metric": a.metric, "min_overlap": a.min_overlap,
           "standardize": bool(a.standardize)}
    rng = np.random.default_rng(20260728)
    data = cell.load(a.data, a.thr)

    obs_raw = series(data, cell, cfg, rng)
    obs = tail_profile(obs_raw, a.min_prompts)
    if obs is None:
        raise SystemExit("too few pairs")
    by = partner_means(obs_raw)
    keep, med = both_high_pairs(obs_raw, by, a.min_prompts)
    obs_hi = tail_profile(obs_raw, a.min_prompts, keep=keep)
    print(f"metric={a.metric}  prompts={len(data):,}  pairs={obs['n']:,}  "
          f"mean raw agreement={obs['mean']:+.4f}")
    print(f"CONTROL stratum: both raters above the median actor score "
          f"({med:+.4f}) -> {len(keep):,} pairs\n")

    nulls, nulls_hi = [], []
    for i in range(a.null_reps):
        s = series(data, cell, cfg, rng, permute=True)
        n = tail_profile(s, a.min_prompts)
        nh = tail_profile(s, a.min_prompts, keep=keep)
        if n:
            nulls.append(n)
        if nh:
            nulls_hi.append(nh)
        if (i + 1) % 50 == 0:
            print(f"  null {i+1}/{a.null_reps}", flush=True)

    print(f"\n{'threshold':>10} {'observed':>10} {'null':>10} {'ratio':>8} {'z':>8} {'p':>8}")
    rows = {}
    for t in THRESHOLDS:
        k = f"{t:+.2f}"
        o = obs["below"][k]
        nv = np.array([x["below"][k] for x in nulls])
        z = (o - nv.mean()) / (nv.std() + 1e-12)
        pv = float((nv >= o).mean())
        ratio = o / nv.mean() if nv.mean() > 1e-12 else float("inf")
        rows[k] = {"observed": o, "null_mean": float(nv.mean()),
                   "null_sd": float(nv.std()), "ratio": float(ratio),
                   "z": float(z), "p": pv}
        print(f"{k:>10} {o:>10.4f} {nv.mean():>10.4f} {ratio:>7.2f}x {z:>+8.2f} {pv:>8.4g}")

    ka = np.array([x["all_negative"] for x in nulls])
    za = (obs["all_negative"] - ka.mean()) / (ka.std() + 1e-12)
    print(f"\n  negative on EVERY one of its prompts: observed {obs['all_negative']:.4f} "
          f"vs null {ka.mean():.4f}   z={za:+.2f}")

    hi_rows = {}
    if obs_hi and nulls_hi:
        print(f"\n=== CONTROL: pairs of two GENERALLY AGREEABLE raters "
              f"({obs_hi['n']:,} pairs) ===")
        print("    an actor explanation predicts the excess VANISHES here")
        print(f"{'threshold':>10} {'observed':>10} {'null':>10} {'ratio':>8} {'z':>8}")
        for t in THRESHOLDS:
            k = f"{t:+.2f}"
            o = obs_hi["below"][k]
            nv = np.array([x["below"][k] for x in nulls_hi])
            z = (o - nv.mean()) / (nv.std() + 1e-12)
            r = o / nv.mean() if nv.mean() > 1e-12 else float("inf")
            hi_rows[k] = {"observed": o, "null_mean": float(nv.mean()),
                          "ratio": float(r), "z": float(z)}
            print(f"{k:>10} {o:>10.4f} {nv.mean():>10.4f} {r:>7.2f}x {z:>+8.2f}")
        hz = hi_rows["-0.20"]["z"]
        print(f"\n  -> far tail among agreeable-pairs: z={hz:+.2f}  "
              f"{'SURVIVES the actor control -- blocs' if hz > 2 else 'VANISHES -- consistent with an actor effect'}")

    near_z = rows["+0.00"]["z"]
    far_z = rows["-0.20"]["z"]
    near_r = rows["+0.00"]["ratio"]
    far_r = rows["-0.20"]["ratio"]
    print(f"\n  SHAPE: just-below-zero {near_r:.2f}x (z={near_z:+.2f})   "
          f"far tail {far_r:.2f}x (z={far_z:+.2f})")

    hz = hi_rows.get("-0.20", {}).get("z", float("nan"))
    hz_near = hi_rows.get("+0.00", {}).get("z", float("nan"))
    # The verdict MUST read the control. The first version of this block ranked
    # the thresholds and printed "VALUE BLOCS" while the actor control, printed
    # ten lines above it, said the tail vanishes among agreeable pairs. A
    # conclusion string that does not consult its own control is the failure this
    # repository catalogues, committed inside the round written to avoid it.
    if hz == hz and hz < 2 and near_z >= 2:
        verdict = ("ACTOR EFFECT, NOT BLOCS: the raw negative tail is real against a "
                   f"within-prompt null ({near_r:.2f}x just below zero, {far_r:.2f}x below "
                   "-0.20) but it VANISHES among pairs of two generally-agreeable raters "
                   f"(far-tail z={hz:+.2f}, leave-one-out). It is carried by pairs "
                   "involving generally-disagreeable raters. Under blocs, two raters could "
                   "each sit inside a large bloc and still oppose each other; the data says "
                   "that essentially does not happen.")
    elif near_z < 2:
        verdict = ("NO PAIR STRUCTURE on the raw scale: the distribution of pair mean "
                   "agreements is indistinguishable from a within-prompt permutation null")
    elif far_z < 2:
        verdict = ("COMPETENCE HETEROGENEITY: excess mass just below zero but NOT in the "
                   "far negative tail. Pairs differ in how well they track each other, "
                   "which attenuates agreement toward zero and stops there. This is "
                   "compatible with ONE shared target and does not require value blocs")
    elif far_r > near_r:
        verdict = ("VALUE BLOCS: the excess GROWS with depth into the negative tail "
                   f"({near_r:.2f}x just below zero, {far_r:.2f}x below -0.20). "
                   "Attenuation toward zero cannot produce reliably anti-correlated "
                   "pairs; opposing structure can")
    else:
        verdict = ("MIXED: both thresholds exceed the null but the excess does NOT grow "
                   "with depth, so the far tail is consistent with being the shoulder of "
                   "the near excess rather than a separate population. This observable "
                   "does not separate blocs from competence heterogeneity")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"cfg": {**cfg, "thr": a.thr, "min_prompts": a.min_prompts},
         "null_reps": a.null_reps, "pairs": obs["n"],
         "mean_raw_agreement": obs["mean"], "thresholds": rows,
         "all_negative_observed": obs["all_negative"],
         "all_negative_null": float(ka.mean()), "all_negative_z": float(za),
         "shape": {"near_ratio": near_r, "near_z": near_z,
                   "far_ratio": far_r, "far_z": far_z},
         "actor_control_both_high": hi_rows,
         "actor_control_n_pairs": obs_hi["n"] if obs_hi else 0,
         "verdict": _freeze(verdict, "r27_raw_negative_tail"),
         "note": "r23/r25/r26 tested the sign of the CENTRED residual, which scores "
                 "'below average' and 'actually disagreeing' identically -- and those "
                 "are the two worlds the test existed to separate. Mean agreement is "
                 "+0.25, so a zero-competence pair has a strongly negative residual "
                 "while never once disagreeing. This asks on the raw scale, where zero "
                 "is a real boundary, and reads the SHAPE of the excess across depth."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
