"""Compilation is near break-even on the average rater. Is it still, on the worst-served one?

Every number in r155 through r158 scores a rubric by its mean concordance with individual human
rankings. That is a utilitarian outcome: how often does this rubric agree with a randomly chosen
person. It is one choice among several, it was never argued for, and the whole balance sheet may be
an artefact of it.

    weight deletion            0
    discarding 74% of criteria  -0.027
    selection + rewriting       +0.061

That nearly balances, and a quantity that nearly balances is one whose sign is decided by the
scoring rule rather than by the object.

THE PREDICTION THAT MAKES THIS A FORK. Compilation compresses fifteen criteria into four. Compression
should cost minority positions more than it costs the mean, because a position held by three of
seventeen people is exactly what a four-item summary drops. So under an outcome that scores the
WORST-served rater rather than the average one, compilation should look worse -- possibly reversing
the sign of the balance.

If instead the ordering of the arms is identical under every outcome, then compression is not
distributively selective here and the utilitarian framing was harmless. Either result is worth
having, and only one of them is the one this phase has been circling.

FOUR OUTCOMES over the same arms, the same prompts, the same judge:

    mean        average concordance across the prompt's raters      utilitarian
    min         the single worst-served rater on that prompt         maximin
    p10         the tenth percentile rater                           robust maximin
    group_gap   spread of mean concordance across demographic groups distributive

The first three need no demographics. The fourth uses country, age, gender, education, AI usage --
whichever have at least three raters on that prompt -- and reports the spread across group means,
where LOWER is more equal.

A rubric can raise the mean by serving the majority better while lowering the minimum. That is not a
hypothetical failure mode; it is what aggregation is for.
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
from covalx.legacy import round_results  # noqa: E402
OUT = pathlib.Path(__file__).resolve().parent / "results"
LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
AXES = ("country_of_residence", "age", "gender", "education_level", "generative_ai_usage")


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


def load_weights():
    from covalx.judge import load_join
    return {pid: np.array([np.mean([s["score"] for s in it["scores"]])
                           for it in r["coval_full"]], float)
            for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                        ROOT / "data" / "conversation_rubrics.jsonl")}


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
    out: dict[str, list[tuple[str, np.ndarray]]] = defaultdict(list)
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                for b in (a.get("ranking_blocks") or {}).get(block, []) or []:
                    v = parse_ranking(b.get("ranking") or "")
                    if v is not None:
                        out[a["conversation_id"]].append((aid, v))
                        break
    return out, demo


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


def group_spread(per_rater: list[tuple[str, float]], demo) -> float:
    """Spread of mean concordance across demographic groups on this prompt. Lower is more equal."""
    vals = []
    for ax in AXES:
        g = defaultdict(list)
        for aid, c in per_rater:
            v = (demo.get(aid) or {}).get(ax)
            if isinstance(v, str) and v and len(v) < 60:
                g[v].append(c)
        means = [np.mean(v) for v in g.values() if len(v) >= 3]
        if len(means) >= 2:
            vals.append(float(np.std(means, ddof=1)))
    return float(np.mean(vals)) if vals else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="world", choices=["world", "personal"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = round_results("R04")
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    weights = load_weights()
    rank, demo = load_rankings(args.block)
    cids = [c for c in sat_core if c in sat_full and c in weights and c in rank]
    print(f"prompts {len(cids)}   block={args.block}")

    outcomes = defaultdict(lambda: defaultdict(list))
    for cid in cids:
        SF, SC, w = sat_full[cid], sat_core[cid], weights[cid]
        n = min(SF.shape[0], w.shape[0])
        raters = rank[cid]
        if n < 4 or SC.shape[0] < 2 or len(raters) < 4:
            continue
        top = np.argsort(-np.abs(w[:n]))[: SC.shape[0]]
        arms = {"core_compiled": agg(SC), "raw_topk_weighted": agg(SF[top], w[top]),
                "full_weighted": agg(SF[:n], w[:n]), "full_unweighted": agg(SF[:n])}
        for name, s in arms.items():
            per = [(aid, concordance(s, pref)) for aid, pref in raters]
            cs = np.array([c for _a, c in per], float)
            cs = cs[np.isfinite(cs)]
            if cs.size < 4:
                continue
            outcomes[name]["mean"].append(float(cs.mean()))
            outcomes[name]["min"].append(float(cs.min()))
            outcomes[name]["p10"].append(float(np.percentile(cs, 10)))
            gs = group_spread(per, demo)
            if math.isfinite(gs):
                outcomes[name]["group_gap"].append(gs)

    def ms(v):
        a = np.asarray(v, float)
        a = a[np.isfinite(a)]
        return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size)

    names = ["full_weighted", "core_compiled", "raw_topk_weighted", "full_unweighted"]
    print(f"\n{'arm':22s} {'mean':>10s} {'min':>10s} {'p10':>10s} {'group_gap':>11s}")
    res = {}
    for nm in names:
        row = {}
        line = f"  {nm:20s}"
        for oc in ("mean", "min", "p10", "group_gap"):
            m, se, k = ms(outcomes[nm][oc])
            row[oc] = {"value": round(m, 4),
                       "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": k}
            line += f" {m:10.4f}"
        res[nm] = row
        print(line)
    print("  (group_gap: LOWER is more equal)")

    print("\nranking of arms under each outcome:")
    flips = {}
    for oc in ("mean", "min", "p10", "group_gap"):
        rev = oc != "group_gap"
        order = sorted(names, key=lambda nm: res[nm][oc]["value"], reverse=rev)
        flips[oc] = order
        print(f"  {oc:10s} " + "  >  ".join(order))

    same = all(flips[oc] == flips["mean"] for oc in ("min", "p10"))
    print(f"\nmaximin ordering identical to utilitarian: {same}")
    cc, fw = res["core_compiled"], res["full_weighted"]
    print(f"compiled vs keeping everything, by outcome:")
    for oc in ("mean", "min", "p10"):
        print(f"  {oc:10s} {cc[oc]['value'] - fw[oc]['value']:+.4f}")
    print(f"  {'group_gap':10s} {cc['group_gap']['value'] - fw['group_gap']['value']:+.4f}"
          f"   (positive = compilation is LESS equal)")

    (OUT / "which_outcome.json").write_text(json.dumps(
        {"block": args.block, "prompts": len(cids), "arms": res, "orderings": flips,
         "maximin_matches_utilitarian": same,
         "instrument": "one rebuilt 2B judge for every arm; the outcome definitions execute no "
                       "model at all"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
