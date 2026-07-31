"""Did the compiler really select by weight, and what does each discarded criterion cost?

r155 rests on an assumption I took from the release's own documentation: the compiler keeps the
items with the highest average ratings. My core_keep arm reconstructs core's weights by taking the
top four by magnitude, and if that is not what the compiler did then the arm is about the wrong
criteria and its null is about nothing.

PART ONE tests the documented rule against the artifact. Only 30.8% of core items match a source
item at 0.80 similarity, so the check runs on that subset and reports its own coverage. For each
matched pair, is the source item's magnitude in the top four of its prompt? A documented selection
rule that the artifact does not follow is a more interesting finding than anything r155 measured.

PART TWO prices the compression, which r155 left as a rhetorical question. Sweep k from 1 to 15,
keeping the top-k criteria by magnitude, and measure agreement with human rankings at each k, both
weighted and unweighted. That is the whole trade-off curve: how much is lost per criterion dropped,
and where four sits on it.

The curve answers something the earlier round could only gesture at. If concordance is flat from
k=4 upward, compiling to four costs nothing and the compression is free. If it climbs, four is a
choice paid for in accuracy, and the size of the payment is the price of legibility -- the currency
r155 said it could not price. It can be priced; it just needs the curve rather than a single point.

CONTROLS. At every k, a random-k selection says how much of the top-k advantage is the SELECTION
rather than the SIZE, since fewer criteria is not automatically worse. And the shuffled floor is
carried across the whole sweep so no k is read against nothing.
"""
from __future__ import annotations

import argparse
import difflib
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


def load_joined():
    """prompt_id -> (weights, full criterion texts, core criterion texts)"""
    from covalx.judge import load_join
    out = {}
    for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                ROOT / "data" / "conversation_rubrics.jsonl"):
        w = np.array([np.mean([s["score"] for s in it["scores"]]) for it in r["coval_full"]], float)
        out[pid] = (w, [it["criterion"].strip().lower() for it in r["coval_full"]],
                    [c["criterion"].strip().lower() for c in r["coval_core"]])
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


def load_rankings(block: str):
    out: dict[str, list[np.ndarray]] = defaultdict(list)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            for a in rec.get("assessments", []):
                for b in (a.get("ranking_blocks") or {}).get(block, []) or []:
                    v = parse_ranking(b.get("ranking") or "")
                    if v is not None:
                        out[a["conversation_id"]].append(v)
                        break
    return out


def concordance(score, pref) -> float:
    good = tot = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(pref[i]) or np.isnan(pref[j]):
                continue
            tot += 1
            ds, dp = score[i] - score[j], pref[i] - pref[j]
            if dp == 0 or ds == 0:
                good += 0.5
            elif (ds > 0) == (dp > 0):
                good += 1
    return good / tot if tot else float("nan")


def agg(S, w=None):
    M = np.nan_to_num(S, nan=0.0)
    if w is None:
        return M.mean(axis=0)
    d = np.abs(w).sum()
    return (w[:, None] * M).sum(axis=0) / d if d else M.mean(axis=0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="world", choices=["world", "personal"])
    ap.add_argument("--kmax", type=int, default=15)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    sat = load_sat(ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
                   / "a04_full.npz")
    joined = load_joined()
    rank = load_rankings(args.block)
    cids = [c for c in sat if c in joined and c in rank]
    print(f"prompts {len(cids)}   block={args.block}")

    # ---------------------------------------------------------------- PART ONE
    matched = intop = 0
    unmatched = 0
    rankpos = []
    for cid in cids:
        w, full_txt, core_txt = joined[cid]
        n = min(len(w), len(full_txt))
        if n < 4 or not core_txt:
            continue
        order = list(np.argsort(-np.abs(w[:n])))
        for ct in core_txt:
            hit = difflib.get_close_matches(ct, full_txt[:n], n=1, cutoff=0.80)
            if not hit:
                unmatched += 1
                continue
            i = full_txt.index(hit[0])
            matched += 1
            pos = order.index(i)
            rankpos.append(pos / max(1, n - 1))
            if pos < len(core_txt):
                intop += 1
    print(f"\nPART ONE -- did the compiler select by magnitude?")
    print(f"  core items matched to a source item at 0.80: {matched} "
          f"({matched / (matched + unmatched):.1%} of {matched + unmatched})")
    print(f"  of matched, source item was in the top-|w| slots: {intop} ({intop / matched:.1%})")
    print(f"  mean normalised magnitude rank of matched sources: {np.mean(rankpos):.3f} "
          f"(0 = highest |w|, 0.5 = chance)")

    # ---------------------------------------------------------------- PART TWO
    rng = np.random.default_rng(args.seeds[0])
    curve = {k: {"topk_w": [], "topk_u": [], "rand_w": [], "rand_u": []}
             for k in range(1, args.kmax + 1)}
    floor = []
    for cid in cids:
        w, _ft, _ct = joined[cid]
        S = sat[cid]
        n = min(S.shape[0], len(w))
        if n < 2:
            continue
        order = np.argsort(-np.abs(w[:n]))
        prefs = rank[cid]
        for k in range(1, min(args.kmax, n) + 1):
            top = order[:k]
            rnd = rng.permutation(n)[:k]
            sc = {"topk_w": agg(S[top], w[top]), "topk_u": agg(S[top]),
                  "rand_w": agg(S[rnd], w[rnd]), "rand_u": agg(S[rnd])}
            for pref in prefs:
                for key, s in sc.items():
                    curve[k][key].append(concordance(s, pref))
        for pref in prefs:
            floor.append(concordance(rng.permutation(agg(S[:n], w[:n])), pref))

    def ms(v):
        a = np.asarray(v, float)
        a = a[~np.isnan(a)]
        return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size) if a.size > 1 \
            else (float("nan"), float("nan"), a.size)

    print(f"\nPART TWO -- the compression curve  (floor {ms(floor)[0]:.4f})")
    print(f"{'k':>3s} {'top-k weighted':>16s} {'top-k unweighted':>18s} {'random-k w':>12s} "
          f"{'gain over random':>17s}")
    rows = {}
    for k in range(1, args.kmax + 1):
        if not curve[k]["topk_w"]:
            continue
        tw, tw_se, n = ms(curve[k]["topk_w"])
        tu, _, _ = ms(curve[k]["topk_u"])
        rw, _, _ = ms(curve[k]["rand_w"])
        rows[k] = {"topk_weighted": round(tw, 4), "topk_unweighted": round(tu, 4),
                   "random_k_weighted": round(rw, 4), "n": n,
                   "ci95": [round(tw - 1.96 * tw_se, 4), round(tw + 1.96 * tw_se, 4)]}
        mark = "  <- what the release ships" if k == 4 else ""
        print(f"{k:3d} {tw:16.4f} {tu:18.4f} {rw:12.4f} {tw - rw:17.4f}{mark}")

    best_k = max(rows, key=lambda k: rows[k]["topk_weighted"])
    at4 = rows.get(4, {}).get("topk_weighted")
    print(f"\n  best k = {best_k} at {rows[best_k]['topk_weighted']:.4f}")
    if at4 is not None:
        print(f"  cost of compiling to four instead of {best_k}: "
              f"{rows[best_k]['topk_weighted'] - at4:+.4f}")

    (OUT / "compression_curve.json").write_text(json.dumps({
        "block": args.block, "prompts": len(cids),
        "selection_check": {"matched": matched, "unmatched": unmatched,
                            "match_rate": round(matched / (matched + unmatched), 4),
                            "in_top_slots": intop,
                            "in_top_share": round(intop / matched, 4) if matched else None,
                            "mean_normalised_magnitude_rank": round(float(np.mean(rankpos)), 4)},
        "curve": rows, "floor": round(ms(floor)[0], 4), "best_k": best_k,
        "cost_of_four": round(rows[best_k]["topk_weighted"] - at4, 4) if at4 else None,
        "instrument": "one rebuilt 2B judge shared by every k, so it cannot produce a difference "
                      "between points on the curve",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
