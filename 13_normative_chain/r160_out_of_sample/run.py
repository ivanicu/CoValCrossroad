"""Every comparison so far was in-sample. Compression's whole defence is out-of-sample.

r159 found that keeping all fifteen criteria with their weights beats the compiled four under every
outcome, and left the phase with a question it could not answer: why compile at all. The remaining
candidate was legibility -- four criteria fit in a head and fifteen do not -- which this release
cannot price.

But there is a second candidate it CAN price, and it is the standard one. Every number in r155
through r159 was scored IN SAMPLE. The weights come from a panel; concordance is measured against
that same panel's rankings. Fifteen weights fitted to seventeen people and evaluated on those
seventeen people is a fit statistic, and a fit statistic always rewards the richer model.

Compression's classic justification is that it stops you fitting the panel you happen to have.

THE TEST. Split each prompt's raters into two halves. Build the weights from half A only. Score
against half B's rankings, which contributed nothing to the weights. The arms that carry many fitted
parameters should lose more than the arms that carry few, and core_compiled -- which uses NO weights
at all, only the compiled text -- cannot overfit the panel that way.

    full_weighted       15 weights fitted on half A        most exposed
    raw_topk_weighted   4 weights fitted on half A         less exposed
    core_compiled       0 weights, unweighted mean         cannot overfit the panel
    full_unweighted     0 weights                          the no-information control

PREDICTION, WRITTEN BEFORE THE RUN: full_weighted's advantage shrinks out-of-sample. If it shrinks
to nothing or reverses, compilation has an empirical defence and the phase's headline changes from
"compilation is a net loss" to "compilation is a net loss in sample and a net gain out of it". If it
survives intact, compression has no measurable justification in this data at all, and the honest
statement is that the only remaining defence is one this release cannot price.

The in-sample arm is rerun alongside on exactly the same prompts, so the shrinkage is a paired
quantity rather than a comparison across two different tables.
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


def load_per_rater_weights():
    """prompt -> (criteria x annotators) signed weights, plus the annotator order.

    Per-rater rather than pre-averaged, because averaging first would make the split impossible --
    the whole point is to build the weights from ONE half of the panel.
    """
    from covalx.judge import load_join
    out = {}
    for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                ROOT / "data" / "conversation_rubrics.jsonl"):
        ann = sorted({s["annotator_id"] for it in r["coval_full"] for s in it["scores"]})
        idx = {a: i for i, a in enumerate(ann)}
        M = np.full((len(r["coval_full"]), len(ann)), np.nan)
        for i, it in enumerate(r["coval_full"]):
            for s in it["scores"]:
                M[i, idx[s["annotator_id"]]] = float(s["score"])
        out[pid] = (M, ann)
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
    out: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            for a in rec.get("assessments", []):
                for b in (a.get("ranking_blocks") or {}).get(block, []) or []:
                    v = parse_ranking(b.get("ranking") or "")
                    if v is not None:
                        out[a["conversation_id"]][rec["annotator_id"]] = v
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
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    W = load_per_rater_weights()
    rank = load_rankings(args.block)
    cids = [c for c in sat_core if c in sat_full and c in W and c in rank]
    print(f"prompts {len(cids)}   block={args.block}   seeds {args.seeds}")

    ins = defaultdict(list)
    oos = defaultdict(list)
    for seed in args.seeds:
        rng = np.random.default_rng(seed)
        for cid in cids:
            Mw, ann = W[cid]
            SF, SC = sat_full[cid], sat_core[cid]
            n = min(SF.shape[0], Mw.shape[0])
            # only raters who both rated criteria AND gave a ranking can be split
            usable = [i for i, a in enumerate(ann) if a in rank[cid]]
            if n < 4 or SC.shape[0] < 2 or len(usable) < 6:
                continue
            perm = rng.permutation(usable)
            h = len(perm) // 2
            A, B = perm[:h], perm[h:]
            wA = np.nanmean(Mw[:n][:, A], axis=1)
            wA = np.nan_to_num(wA, nan=0.0)
            wAll = np.nan_to_num(np.nanmean(Mw[:n], axis=1), nan=0.0)
            topA = np.argsort(-np.abs(wA))[: SC.shape[0]]
            topAll = np.argsort(-np.abs(wAll))[: SC.shape[0]]
            arms_oos = {"full_weighted": agg(SF[:n], wA),
                        "raw_topk_weighted": agg(SF[topA], wA[topA]),
                        "core_compiled": agg(SC),
                        "full_unweighted": agg(SF[:n])}
            arms_ins = {"full_weighted": agg(SF[:n], wAll),
                        "raw_topk_weighted": agg(SF[topAll], wAll[topAll]),
                        "core_compiled": agg(SC),
                        "full_unweighted": agg(SF[:n])}
            for j in B:                      # held-out raters only
                pref = rank[cid][ann[j]]
                for k, s in arms_oos.items():
                    oos[k].append(concordance(s, pref))
                for k, s in arms_ins.items():
                    ins[k].append(concordance(s, pref))

    def ms(v):
        a = np.asarray(v, float)
        a = a[np.isfinite(a)]
        return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size)

    names = ["full_weighted", "raw_topk_weighted", "core_compiled", "full_unweighted"]
    print(f"\n{'arm':22s} {'in-sample w':>13s} {'held-out w':>12s} {'shrinkage':>11s} "
          f"{'fitted params':>14s}")
    res = {}
    params = {"full_weighted": "15", "raw_topk_weighted": "4", "core_compiled": "0",
              "full_unweighted": "0"}
    for nm in names:
        mi, sei, ni = ms(ins[nm])
        mo, seo, no = ms(oos[nm])
        d = np.asarray(ins[nm], float) - np.asarray(oos[nm], float)
        d = d[np.isfinite(d)]
        dm = float(d.mean())
        res[nm] = {"in_sample": round(mi, 4), "held_out": round(mo, 4),
                   "shrinkage": round(dm, 4), "n": no,
                   "held_out_ci95": [round(mo - 1.96 * seo, 4), round(mo + 1.96 * seo, 4)]}
        print(f"  {nm:20s} {mi:13.4f} {mo:12.4f} {dm:+11.4f} {params[nm]:>14s}")

    gap_in = res["full_weighted"]["in_sample"] - res["core_compiled"]["in_sample"]
    gap_out = res["full_weighted"]["held_out"] - res["core_compiled"]["held_out"]
    print(f"\n  full_weighted advantage over core_compiled:")
    print(f"    in sample  {gap_in:+.4f}")
    print(f"    held out   {gap_out:+.4f}")
    print(f"    lost to overfitting the panel: {gap_in - gap_out:+.4f}")
    verdict = ("COMPRESSION HAS AN EMPIRICAL DEFENCE -- the advantage does not survive held-out "
               "raters" if gap_out <= 0 else
               "NO MEASURABLE DEFENCE -- keeping everything still wins on raters who contributed "
               "nothing to the weights")
    print(f"\nVERDICT: {verdict}")

    (OUT / "out_of_sample.json").write_text(json.dumps(
        {"block": args.block, "seeds": args.seeds, "prompts": len(cids), "arms": res,
         "gap_in_sample": round(gap_in, 4), "gap_held_out": round(gap_out, 4),
         "overfitting_cost": round(gap_in - gap_out, 4), "verdict": verdict,
         "instrument": "one rebuilt 2B judge for every arm; the split touches only the weights"},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
