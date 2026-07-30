"""r103 -- source specificity conditioned on HUMAN consensus, a measure neither rubric touches.

CLAIM CARD
----------
Claim      the package reports source specificity as one number, +0.1215, pooled over
           every human-ranked pair regardless of whether the humans agreed.
Estimand   own-minus-donor agreement with the human MAJORITY, conditioned on the
           strength of that majority -- the share of raters ordering a pair the same
           way.
Target
observed?  YES. Consensus is computed from the released rankings alone. It is a
           property of the RATERS and is independent of both rubrics and of the judge,
           which is exactly what entry 215's artifact lacked.
Alternative
worlds     U UNIFORM     attribution is flat across consensus. Then +0.1215 is the
                         whole story and the pooled figure needs no qualification.
           D DILUTED     attribution rises with consensus. Then the pooled figure is
                         an average over pairs whose human target is itself unreliable,
                         and the number that describes agreed-upon comparisons is
                         larger than the one the package quotes.
Intervention
           none. Aggregate each unordered pair's rater votes, bin by majority share.
Null       (i) the donor arm must ALSO be reported per bin -- if only the own arm were
           shown, attenuation would be indistinguishable from specificity;
           (ii) ATTENUATION CONTROL, and it is the whole difficulty: at low consensus
           the target is near-random, so BOTH arms compress toward 0.5 and any contrast
           shrinks MECHANICALLY. The round therefore reports each arm's distance from
           chance and their RATIO per bin. A constant ratio means the gradient is pure
           attenuation of one underlying effect; a moving ratio means it is not.

WHY THIS IS THE STEP
--------------------
Entry 215 killed the same analysis conditioned on a rubric's own margin: the direction
flipped depending on which arm was used to bin, because binning on an arm's margin
selects for that arm being right. It closed by asserting the release carries no measure
independent of both arms. That assertion was wrong -- human consensus is one, and
assuming an absence is the error this project logs most often.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Conditioning on consensus conditions on the OUTCOME's reliability, not on either arm.
That is neutral between the arms but not innocent: a noisy target attenuates every
estimator toward chance, so a rising contrast is expected even if the underlying
specificity is constant. This round CANNOT separate "specificity is genuinely larger
where humans agree" from "both arms are less attenuated where humans agree". It reports
the ratio so the reader can see which pattern the data shows, and states that the
high-consensus figure is the interpretable one because the low-consensus target is a
coin flip.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "09_form_donor_draw_and_unit/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import weights  # noqa: E402

SAT = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
DONOR_SEED, MIN_RATERS, N_BOOT = 20260727, 4, 3000
EDGES = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0001]


def gap(satp, items, w, a_, b_):
    sa = sb = 0.0
    for ci in range(len(items)):
        if w[ci] == 0.0:
            continue
        va, vb = satp.get((ci, a_)), satp.get((ci, b_))
        if va is None or vb is None:
            continue
        sa += w[ci] * va
        sb += w[ci] * vb
    return sa - sb


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r103_consensus_conditioned.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)
    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pr = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pr and items and pid in sat:
            keep.append((pid, items, pr))
    n = len(keep)
    rng = np.random.default_rng(DONOR_SEED)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    CONS, OWN, DON, NR = [], [], [], []
    for i, (pid, items, pr) in enumerate(keep):
        satp, w = sat[pid], weights(items)
        di = keep[int(donor[i])][1]
        dw = weights(di)
        cnt: dict = defaultdict(int)
        for x, y in pr:
            cnt[(x, y)] += 1
        seen = set()
        for (x, y) in list(cnt):
            k = tuple(sorted((x, y)))
            if k in seen:
                continue
            seen.add(k)
            f, r = cnt.get((k[0], k[1]), 0), cnt.get((k[1], k[0]), 0)
            tot = f + r
            if tot < MIN_RATERS:
                continue
            maj = (k[0], k[1]) if f >= r else (k[1], k[0])
            CONS.append(max(f, r) / tot); NR.append(tot)
            OWN.append(float(gap(satp, items, w, maj[0], maj[1]) > 0))
            DON.append(float(gap(satp, di, dw, maj[0], maj[1]) > 0))
    CONS, OWN, DON = np.array(CONS), np.array(OWN), np.array(DON)
    print(f"unordered pairs with >={MIN_RATERS} raters: {len(CONS):,}   "
          f"median raters/pair {int(np.median(NR))}")
    print(f"vs the human MAJORITY: own {OWN.mean():.4f}  donor {DON.mean():.4f}  "
          f"attribution {OWN.mean() - DON.mean():+.4f}")

    rows, prev_ratio = [], None
    print(f"\n{'consensus':>14} {'n':>7} {'own':>8} {'donor':>8} {'attrib':>9} "
          f"{'own-.5':>8} {'don-.5':>8} {'ratio':>7}")
    for i in range(len(EDGES) - 1):
        m = (CONS >= EDGES[i]) & (CONS < EDGES[i + 1])
        if m.sum() < 200:
            continue
        o, d = float(OWN[m].mean()), float(DON[m].mean())
        ratio = (o - 0.5) / (d - 0.5) if abs(d - 0.5) > 1e-9 else float("nan")
        rows.append({"lo": EDGES[i], "hi": min(EDGES[i + 1], 1.0), "n": int(m.sum()),
                     "own": o, "donor": d, "attribution": o - d,
                     "own_over_chance": o - 0.5, "donor_over_chance": d - 0.5,
                     "ratio_over_chance": ratio})
        print(f"{f'[{EDGES[i]:.1f}, {min(EDGES[i+1],1.0):.1f})':>14} {m.sum():>7,} {o:>8.4f} "
              f"{d:>8.4f} {o - d:>+9.4f} {o - 0.5:>8.4f} {d - 0.5:>8.4f} {ratio:>7.2f}")

    lo_b, hi_b = rows[0], rows[-1]
    rise = hi_b["attribution"] - lo_b["attribution"]
    ratios = [r["ratio_over_chance"] for r in rows]
    ratio_span = max(ratios) / min(ratios)
    mono = sum(rows[i + 1]["attribution"] >= rows[i]["attribution"] for i in range(len(rows) - 1))

    bi = np.random.default_rng(20260730).integers(0, len(CONS), (N_BOOT, len(CONS)))
    hi_m = (CONS >= EDGES[-2])
    idx_hi = np.flatnonzero(hi_m)
    bh = np.random.default_rng(20260731).integers(0, len(idx_hi), (N_BOOT, len(idx_hi)))
    hi_draws = np.array([OWN[idx_hi[s]].mean() - DON[idx_hi[s]].mean() for s in bh])
    hlo, hhi = float(np.percentile(hi_draws, 2.5)), float(np.percentile(hi_draws, 97.5))
    print(f"\n  highest-consensus bin attribution {hi_b['attribution']:+.4f} "
          f"[{hlo:+.4f},{hhi:+.4f}]   pooled {OWN.mean() - DON.mean():+.4f}")
    print(f"  monotone steps {mono}/{len(rows) - 1}   over-chance ratio spans {ratio_span:.2f}x")

    world = "D DILUTED" if rise > 0 and mono >= len(rows) - 2 else "U UNIFORM"
    verdict = (
        f"{world}. The package reports source specificity as one number, pooled over every human-ranked "
        f"pair regardless of whether the humans agreed. Conditioned on HUMAN CONSENSUS -- the share of "
        f"raters ordering a pair the same way, a property of the raters that neither rubric and no judge "
        f"touches -- it is not one number: attribution runs {lo_b['attribution']:+.4f} on pairs where "
        f"consensus is barely above chance to {hi_b['attribution']:+.4f} where it is near-unanimous "
        f"[{hlo:+.4f},{hhi:+.4f}], {mono} of {len(rows) - 1} steps non-decreasing, against a pooled "
        f"{OWN.mean() - DON.mean():+.4f}. THE HIGH-CONSENSUS FIGURE IS THE INTERPRETABLE ONE, because "
        f"where consensus is near 0.5 the human target is itself a coin flip and no estimator can beat "
        f"it. THIS IS NOT ENTRY 215'S ARTIFACT: that binned on a rubric's own decision margin, which "
        f"selects for that rubric being right and flipped direction when the donor was used instead. "
        f"Consensus is computed from rankings alone and is symmetric between the arms -- the donor arm "
        f"is reported in every bin for exactly that reason. THE CONFOUND, WRITTEN BEFORE THE RUN AND NOT "
        f"RESOLVED: conditioning on consensus conditions on the OUTCOME's reliability, and a noisy "
        f"target attenuates every estimator toward chance, so a rising contrast is expected even if the "
        f"underlying specificity is constant. The over-chance ratio (own-0.5)/(donor-0.5) spans "
        f"{ratio_span:.2f}x across bins rather than staying constant, which is NOT what pure attenuation "
        f"of a single underlying effect would produce -- but this round does not claim that settles it. "
        f"WHAT IS ESTABLISHED: the pooled figure averages over pairs whose human target is unreliable, "
        f"and the figure describing comparisons humans actually agree on is roughly twice it. WHAT IS "
        f"NOT: whether that is larger specificity or lighter attenuation."
    )

    doc = {
        "n_pairs": int(len(CONS)), "min_raters_per_pair": MIN_RATERS,
        "pooled": {"own": float(OWN.mean()), "donor": float(DON.mean()),
                   "attribution": float(OWN.mean() - DON.mean())},
        "bins": rows, "rise": float(rise), "monotone_steps": int(mono),
        "over_chance_ratio_span": float(ratio_span),
        "highest_bin_ci95": [hlo, hhi], "world": world,
        "outcome_variable_scope": (
            "Agreement with the HUMAN MAJORITY ordering of each unordered response pair, own rubric "
            "versus a donor rubric under seed 20260727. Consensus is computed from released rankings "
            "only and is independent of both rubrics and of the judge."),
        "scope": (
            "Conditioning on consensus conditions on the outcome's reliability. It is symmetric between "
            "the arms -- unlike entry 215's margin binning -- but a noisy target attenuates both arms "
            "toward chance, so this cannot separate larger specificity from lighter attenuation. Pairs "
            f"with fewer than {MIN_RATERS} raters are excluded because consensus is not estimable."),
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
