"""Reconciling two results in this repo that answer "who is served" with different words.

fcaa949 measured the DEPARTURE FROM THE ARITHMETIC LINE in how well the compiled rubric agrees with
a person's whole ranking, and found nothing: 30 group cells, max |t| 1.83, nothing surviving BH, and
a positive control recovering a planted effect at t 4.89 with an MDE about seven times smaller than
the spread being explained. That is a well-powered null and it is not in question here.

r146 measured whether the response the rubric ACTUALLY PICKS is one the person wanted, and found ten
of 43 groups changing, with South Africa's relative disadvantage doubling from full to core.

Both cannot be dismissed, and the obvious move -- deciding which round was wrong -- is available and
probably incorrect. They measure different functionals of the same score vector:

    TRACKING   how close the rubric's ordering is to the person's, over the whole ranking.
               A least-squares-flavoured quantity. Dominated by the bulk of the ordering.
    SERVING    whether the argmax is in the person's top set.
               A single order statistic. Determined entirely by the top of the ordering.

A rubric can track everyone equally well and still have its argmax land outside one group's top set
systematically, because a margin of 0.001 at the top decides the pick while contributing almost
nothing to overall agreement. If that is what is happening here, then

    a rubric can be representative in what it WEIGHS and still fail a group in what it CHOOSES,

and the two rounds are both right about different things.

THE TEST, and it has a real kill branch. Compute both quantities on the same people, prompts and
groups, then correlate the two group-gap vectors across all 43 groups.

    r near 0   the estimands are orthogonal; both rounds stand; tracking and serving come apart.
    r high     they measure the same thing and one of the two rounds is wrong -- and then the
               powered null wins, because r146 has no positive control of comparable strength.

THE MECHANISM, tested separately rather than asserted. If the story above is right, the serving gap
must be concentrated where the top-two margin is SMALL, and must vanish where the winner is clear.
A gap that is flat across margin strata refutes the explanation even if the correlation is zero.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
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


def disagreement(score: np.ndarray, pref: np.ndarray) -> float:
    """Pairwise disagreement over the six pairs: the TRACKING quantity, using the whole ordering.

    Ties on either side count as half, so a person who ranks two responses equal is not forced into
    a direction they did not express.
    """
    bad = tot = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(pref[i]) or np.isnan(pref[j]):
                continue
            tot += 1
            ds, dp = score[i] - score[j], pref[i] - pref[j]
            if dp == 0 or ds == 0:
                bad += 0.5
            elif (ds > 0) != (dp > 0):
                bad += 1
    return bad / tot if tot else float("nan")


def collect(rank, demo, sat_core):
    """Per (prompt, person): tracking disagreement, serving indicator, top-two margin."""
    rows = []
    for pid, per in rank.items():
        M = sat_core.get(pid)
        if M is None or len(per) < 4:
            continue
        score = np.nanmean(M, axis=0)
        order = np.sort(score)[::-1]
        margin = float(order[0] - order[1])
        pick = int(np.argmax(score))
        for a, v in per.items():
            top = set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist())
            rows.append({"pid": pid, "a": a, "size": len(top),
                         "unserved": 0 if pick in top else 1,
                         "err": disagreement(score, v), "margin": margin})
    return rows


def group_gap(rows, demo, field: str, subset=None) -> dict:
    """Within-prompt, decisiveness-matched group gap on `field`."""
    strata: dict[tuple[str, str], list[float]] = defaultdict(list)
    by: dict[tuple[str, int], list] = defaultdict(list)
    for r in rows:
        if subset is not None and not subset(r):
            continue
        by[(r["pid"], r["size"])].append(r)
    for members in by.values():
        if len(members) < 4:
            continue
        for k in {kk for r in members for kk in (demo.get(r["a"]) or {})}:
            vals = [(demo.get(r["a"], {}).get(k), r[field]) for r in members]
            vals = [(v, u) for v, u in vals
                    if isinstance(v, str) and v and len(v) < 60 and not np.isnan(u)]
            for g in {v for v, _u in vals}:
                ins = [u for v, u in vals if v == g]
                outs = [u for v, u in vals if v != g]
                if ins and outs:
                    strata[(k, g)].append(float(np.mean(ins)) - float(np.mean(outs)))
    out = {}
    for key, d in strata.items():
        if len(d) < MIN_STRATA:
            continue
        arr = np.array(d)
        m, se = float(arr.mean()), float(arr.std(ddof=1) / math.sqrt(len(arr)))
        out[key] = {"gap": m, "se": se, "n": len(d),
                    "ci95": [m - 1.96 * se, m + 1.96 * se]}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--margin-splits", type=float, nargs="+", default=[0.02, 0.05])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "E01" / "R04_rebuild_satisfaction" / "results"
    sat_core = load_sat(base / "a04_core.npz")
    rank, demo = load_rankings()
    rows = collect(rank, demo, sat_core)
    print(f"rows {len(rows)}   prompts {len({r['pid'] for r in rows})}   "
          f"people {len({r['a'] for r in rows})}")
    print(f"mean tracking disagreement {np.nanmean([r['err'] for r in rows]):.4f}   "
          f"mean unserved {np.mean([r['unserved'] for r in rows]):.4f}")

    g_serve = group_gap(rows, demo, "unserved")
    g_track = group_gap(rows, demo, "err")
    keys = sorted(set(g_serve) & set(g_track))
    x = np.array([g_track[k]["gap"] for k in keys])
    y = np.array([g_serve[k]["gap"] for k in keys])
    r = float(np.corrcoef(x, y)[0, 1])
    # Fisher z interval on the correlation across groups
    z = 0.5 * math.log((1 + r) / (1 - r))
    sez = 1 / math.sqrt(len(keys) - 3)
    lo, hi = (math.tanh(z - 1.96 * sez), math.tanh(z + 1.96 * sez))
    print(f"\ngroups compared on both estimands: {len(keys)}")
    print(f"correlation of TRACKING gap with SERVING gap: r = {r:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    print(f"  shared variance {r * r:.1%}  -> the two rounds measure "
          f"{'the same thing' if abs(r) > 0.7 else 'largely different things'}")

    # mechanism: is the serving gap concentrated where the top-two margin is small?
    ms = sorted(r_["margin"] for r_ in rows)
    cuts = [ms[int(len(ms) * q)] for q in (0.33, 0.66)]
    print(f"\ntop-two margin terciles at {cuts[0]:.4f} / {cuts[1]:.4f}")
    strata_res = {}
    for name, sub in (("narrow", lambda r_: r_["margin"] <= cuts[0]),
                      ("middle", lambda r_: cuts[0] < r_["margin"] <= cuts[1]),
                      ("wide", lambda r_: r_["margin"] > cuts[1])):
        gs = group_gap(rows, demo, "unserved", subset=sub)
        gt = group_gap(rows, demo, "err", subset=sub)
        common = sorted(set(gs) & set(gt))
        spread = float(np.std([gs[k]["gap"] for k in common], ddof=1)) if len(common) > 2 else None
        sa = next((gs[k] for k in gs if k[1] == "South Africa"), None)
        strata_res[name] = {
            "n_groups": len(common),
            "spread_of_serving_gaps": round(spread, 4) if spread else None,
            "south_africa_serving_gap": round(sa["gap"], 4) if sa else None,
            "south_africa_ci": [round(c, 4) for c in sa["ci95"]] if sa else None}
        print(f"  {name:7s} groups {len(common):3d}  spread of serving gaps "
              f"{spread if spread else float('nan'):.4f}   South Africa "
              f"{sa['gap'] if sa else float('nan'):+.4f}")

    top = sorted(keys, key=lambda k: -abs(g_serve[k]["gap"]))[:8]
    print(f"\n{'group':30s} {'tracking gap':>14s} {'serving gap':>13s}")
    for k in top:
        print(f"  {k[1][:28]:28s} {g_track[k]['gap']:+14.4f} {g_serve[k]['gap']:+13.4f}")

    (OUT / "tracking_vs_serving.json").write_text(json.dumps({
        "n_rows": len(rows), "n_groups": len(keys),
        "correlation_tracking_vs_serving": round(r, 4), "ci95": [round(lo, 4), round(hi, 4)],
        "shared_variance": round(r * r, 4),
        "margin_terciles": [round(c, 4) for c in cuts],
        "by_margin": strata_res,
        "groups": [{"axis": k[0], "group": k[1],
                    "tracking_gap": round(g_track[k]["gap"], 5),
                    "serving_gap": round(g_serve[k]["gap"], 5)} for k in keys],
        "instrument": "compiled-core scores come from the rebuilt 2B judge; both estimands share "
                      "it, so their CONTRAST is instrument-free even though their levels are not.",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
