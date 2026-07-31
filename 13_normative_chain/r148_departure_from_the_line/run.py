"""Does r146's +0.0418 survive the correction that already retracted one claim in this programme?

r146 reported that compilation widens South Africa's serving gap by 4.2 points, core over full,
paired within prompt and matched on decisiveness. r147 then noticed that this differential was never
corrected for the arithmetic line -- and fcaa949's entry 24 retracted a structurally identical claim
for exactly that reason: any covariate that moves BOTH arms produces a differential proportional to
the arms' gap, so an uncorrected differential is partly a restatement of the level.

THE ESTIMAND IS THE DEPARTURE, NOT THE DIFFERENCE.

    level_g       the group's mean serving gap across both arms       (how badly served, overall)
    diff_g        core gap minus full gap                             (what r146 reported)
    line          diff = k * level, with k FIT ON THIS OUTCOME
    departure_g   diff_g - k * level_g                                (the estimand)

k is re-derived here rather than copied. fcaa949's k = 0.26514 was fit for a continuous agreement
error; this outcome is a binary indicator and there is no reason its arithmetic constant is the same.
Importing a constant across estimands would be the same class of error the correction exists to catch.

TWO CONTROLS, and the null is inadmissible without the first.

  POSITIVE  plant a one-armed effect: add g to the CORE arm only, for one real group, leaving full
            untouched. If the method cannot recover a planted effect, its null is silence rather than
            an acquittal, and the MDE says how small an effect would have been missed.
  NEGATIVE  synthetic groups matched to a real group on SIZE and on LEVEL. A group that differs only
            by being more poorly served should land ON the line. Where the synthetic band falls tells
            you what "on the line" means before any real group is judged against it.

The negative control is deliberately not a permutation. A permutation answers whether the labelling
mattered; it never answers whether the level explains the difference, which is the whole question.

READING RULE, fixed before the run. Departure CI excluding zero after BH -> compilation adds a
distributive cost. Departure inside the synthetic band -> the cost is INHERITED, r146's headline
comes down, and the retraction is written in the same commit that finds it.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
MIN_STRATA = 20


def load_sat(path: pathlib.Path) -> dict[str, np.ndarray]:
    z = np.load(path, allow_pickle=True)
    cells: dict[str, dict[tuple[int, int], float]] = defaultdict(dict)
    for s, m in zip(z["sat"], z["meta"]):
        cid, ci, rl = str(m).split("|")
        if rl in LETTERS:
            cells[cid][(int(ci), LETTERS.index(rl))] = float(s)
    out = {}
    for cid, d in cells.items():
        M = np.full((max(k[0] for k in d) + 1, 4), np.nan)
        for (i, j), v in d.items():
            M[i, j] = v
        out[cid] = M
    return out


def parse_ranking(txt: str):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def load_rankings():
    rank: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                for key in ("world", "personal"):
                    got = False
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            rank[a["conversation_id"]][aid] = v
                            got = True
                            break
                    if got:
                        break
    return rank, demo


def strata_table(rank, demo, sat_full, sat_core, plant=None):
    """Per (prompt, decisiveness, group): the full-arm and core-arm gaps, kept SEPARATE.

    Keeping both arms rather than only their difference is the direct remedy for the failure that
    produced the earlier retraction: that round computed both arms' errors and discarded them three
    lines later, destroying the diagnostic that overturned it.

    `plant` = (group_value, g) adds g to the CORE arm only, for members of that group.
    """
    out: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for pid, per in rank.items():
        Mf, Mc = sat_full.get(pid), sat_core.get(pid)
        if Mf is None or Mc is None or len(per) < 4:
            continue
        pick_f = int(np.argmax(np.nanmean(Mf, axis=0)))
        pick_c = int(np.argmax(np.nanmean(Mc, axis=0)))
        tops = {a: set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist()) for a, v in per.items()}
        for size in (1, 2, 3):
            members = [a for a, t in tops.items() if len(t) == size]
            if len(members) < 4:
                continue
            for k in {kk for a in members for kk in (demo.get(a) or {})}:
                vals = [(demo.get(a, {}).get(k), a) for a in members]
                vals = [(v, a) for v, a in vals if isinstance(v, str) and v and len(v) < 60]
                for g in {v for v, _a in vals}:
                    ins = [a for v, a in vals if v == g]
                    outs = [a for v, a in vals if v != g]
                    if not ins or not outs:
                        continue

                    def rate(ppl, pick):
                        return float(np.mean([0 if pick in tops[a] else 1 for a in ppl]))
                    gf = rate(ins, pick_f) - rate(outs, pick_f)
                    gc = rate(ins, pick_c) - rate(outs, pick_c)
                    if plant and plant[0] == g:
                        gc += plant[1]
                    out[(k, g)].append((gf, gc))
    return out


def summarise(tab) -> dict:
    res = {}
    for key, pairs in tab.items():
        if len(pairs) < MIN_STRATA:
            continue
        arr = np.array(pairs)
        gf, gc = arr[:, 0], arr[:, 1]
        d = gc - gf
        lev = (gc + gf) / 2
        res[key] = {"n": len(pairs), "gap_full": float(gf.mean()), "gap_core": float(gc.mean()),
                    "diff": float(d.mean()), "level": float(lev.mean()),
                    "diff_se": float(d.std(ddof=1) / math.sqrt(len(d)))}
    return res


def fit_line(res, exclude=None) -> tuple[float, float]:
    """diff = k * level, through the origin: a group at level zero has nothing to differentiate.

    LEAVE-ONE-OUT IS NOT OPTIONAL. Fitting the line on all groups INCLUDING the one being judged
    means a group with a real departure drags the line toward itself and is then measured against a
    line it helped set. The first version of this round did exactly that, and the positive control
    caught it: a planted effect of g was recovered at only 61-65%, giving an MDE of 0.056 -- LARGER
    than the entire differential under test, so the test could not have returned significant for any
    possible true value. That is a check that cannot fail, in the acquitting direction, which is the
    worst direction because nobody re-examines a cleared claim.
    """
    items = [(kk, v) for kk, v in res.items() if kk != exclude]
    lev = np.array([v["level"] for _kk, v in items])
    d = np.array([v["diff"] for _kk, v in items])
    k = float(lev @ d / (lev @ lev)) if lev @ lev else 0.0
    resid = d - k * lev
    return k, float(resid.std(ddof=1))


def departures(res, k=None) -> dict:
    out = {}
    for key, v in res.items():
        kk = fit_line(res, exclude=key)[0] if k is None else k
        dep = v["diff"] - kk * v["level"]
        se = v["diff_se"]                       # level is a constant offset per group here
        z = dep / se if se else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        out[key] = {**v, "departure": dep, "se": se, "z": z, "p": p, "k_loo": kk,
                    "ci95": [dep - 1.96 * se, dep + 1.96 * se]}
    ps = [v["p"] for v in out.values()]
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    kmax = -1
    for r_, i in enumerate(order, 1):
        if ps[i] <= 0.05 * r_ / len(ps):
            kmax = r_
    for r_, i in enumerate(order, 1):
        list(out.values())[i]["bh_significant"] = r_ <= kmax
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="South Africa")
    ap.add_argument("--plant-sizes", type=float, nargs="+", default=[0.01, 0.02, 0.04])
    ap.add_argument("--synthetic", type=int, default=200)
    ap.add_argument("--seed", type=int, default=17)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    rank, demo = load_rankings()

    tab = strata_table(rank, demo, sat_full, sat_core)
    res = summarise(tab)
    k, rsd = fit_line(res)
    dep = departures(res)          # leave-one-out line per group
    print(f"groups {len(res)}   arithmetic line fit on THIS outcome: k = {k:+.5f}   "
          f"residual sd {rsd:.5f}")

    tkey = next((kk for kk in dep if kk[1] == args.target), None)
    if tkey:
        t = dep[tkey]
        print(f"\n{args.target}:  full {t['gap_full']:+.4f}  core {t['gap_core']:+.4f}  "
              f"diff {t['diff']:+.4f}  level {t['level']:+.4f}")
        print(f"  line predicts diff = {k * t['level']:+.4f}   DEPARTURE {t['departure']:+.4f} "
              f"[{t['ci95'][0]:+.4f}, {t['ci95'][1]:+.4f}]  p={t['p']:.4f}  "
              f"BH={t.get('bh_significant')}")

    # ---- POSITIVE CONTROL: plant a one-armed effect on the target group's core arm
    print("\npositive control (plant g on the CORE arm of the target only):")
    recov = []
    for g in args.plant_sizes:
        tabp = strata_table(rank, demo, sat_full, sat_core, plant=(args.target, g))
        resp = summarise(tabp)
        kp, _ = fit_line(resp)
        depp = departures(resp)
        tp = depp.get(tkey)
        if tp:
            print(f"   g={g:+.3f}  recovered departure {tp['departure']:+.5f}  "
                  f"z={tp['z']:+.2f}  retention {(tp['departure'] - dep[tkey]['departure']) / g:.1%}")
            recov.append({"g": g, "departure": tp["departure"], "z": tp["z"],
                          "retention": (tp["departure"] - dep[tkey]["departure"]) / g})
    mde = None
    if recov:
        per_g = float(np.mean([r["retention"] for r in recov]))
        se = dep[tkey]["se"] if tkey else float("nan")
        mde = 2.8 * se / per_g if per_g else None
        print(f"   MDE at 80% power: g ~ {mde:.5f}")

    # ---- NEGATIVE CONTROL: synthetic groups matched on size and level
    rng = np.random.default_rng(args.seed)
    levels = np.array([v["level"] for v in res.values()])
    target_level = dep[tkey]["level"] if tkey else float(np.median(levels))
    target_n = dep[tkey]["n"] if tkey else int(np.median([v["n"] for v in res.values()]))
    pool = [v for v in res.values()
            if abs(v["level"] - target_level) < 0.5 * levels.std() and v["n"] >= MIN_STRATA]
    band = []
    for _ in range(args.synthetic):
        if len(pool) < 2:
            break
        pick = pool[int(rng.integers(len(pool)))]
        jitter = rng.normal(0, pick["diff_se"], size=max(2, min(target_n, pick["n"])))
        d = pick["diff"] + jitter.mean()
        band.append(d - k * pick["level"])
    band_lo, band_hi = (float(np.percentile(band, 2.5)), float(np.percentile(band, 97.5))) \
        if band else (float("nan"), float("nan"))
    print(f"\nnegative control: {len(band)} synthetic groups matched on size and level")
    print(f"   departure band [{band_lo:+.5f}, {band_hi:+.5f}]")

    verdict = "UNDECIDED"
    if tkey:
        d0 = dep[tkey]["departure"]
        inside = band_lo <= d0 <= band_hi
        verdict = ("INHERITED -- r146 headline retracted" if inside
                   else "ADDED -- r146 headline survives")
        print(f"\n{args.target} departure {d0:+.5f} is "
              f"{'INSIDE' if inside else 'OUTSIDE'} the matched band")
    n_bh = sum(1 for v in dep.values() if v.get("bh_significant"))
    print(f"groups with BH-significant departure: {n_bh}/{len(dep)}")
    print(f"\nVERDICT: {verdict}")

    (OUT / "departure.json").write_text(json.dumps({
        "k_fit_on_this_outcome": round(k, 5), "residual_sd": round(rsd, 5),
        "n_groups": len(res), "n_bh_significant": n_bh,
        "target": args.target,
        "target_row": {kk: (round(vv, 5) if isinstance(vv, float) else vv)
                       for kk, vv in dep[tkey].items()} if tkey else None,
        "positive_control": recov, "mde": mde,
        "negative_control_band": [band_lo, band_hi], "n_synthetic": len(band),
        "verdict": verdict,
        "top_departures": sorted(
            [{"axis": a, "group": g, "departure": round(v["departure"], 5),
              "ci95": [round(c, 5) for c in v["ci95"]], "p": v["p"],
              "bh": v.get("bh_significant")} for (a, g), v in dep.items()],
            key=lambda r: r["p"])[:10],
    }, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
