"""Is the compiler's rewriting doing normative work, or manufacturing a quality detector?

r156 left one anomaly. The compiled core criteria score 0.6380 against human rankings UNWEIGHTED,
while the raw top-four criteria score 0.5578 unweighted -- eight points, at matched criterion count,
same judge, same responses. Something about the rewritten text works better, and this phase has so
far found only losses, so a gain deserves more suspicion than a loss.

THREE WORLDS, and only one of them is good news for the compiler:

  REWRITING HELPS   the compiler turns vague crowd wording into criteria a judge can actually
                    evaluate. The gain is real and it is normative.
  SELECTION HELPS   whatever rule picks the survivors picks better ones, and the rewriting is
                    incidental. r156 already showed the rule is not top-magnitude, so this would
                    mean an unknown and undocumented rule is doing the work.
  QUALITY DETECTOR  the rewriting smooths criteria toward generic goodness -- "be clear",
                    "be balanced" -- so they stop measuring anything prompt-specific and start
                    measuring which response is better overall. Concordance rises precisely
                    BECAUSE the rubric stopped being about values.

The third is deflationary and is the one to try hardest to confirm, because it is the one that turns
an apparent success into a failure of a different kind.

THE DECISIVE TEST IS A CONTENT-FREE PROXY. If a rubric that knows nothing about the prompt matches
core's concordance, then core's concordance is not evidence that the rubric captures what people
wanted. Three proxies, none of which reads a criterion at all:

    length         longer responses win
    verbosity      more distinct words win
    generic-mean   mean satisfaction across ALL of a prompt's criteria -- a pure "how good is this
                   response" index, using the criteria only as a sensor bank rather than as a rubric

And one structural signature: if core's four criteria are all measuring the same underlying quality,
their satisfaction vectors across the four responses will be far more inter-correlated than four raw
criteria are. That is measurable directly and needs no proxy at all.
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


def load_responses() -> dict[str, list[str]]:
    out = {}
    with (ROOT / "data" / "comparisons.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            slots = {}
            for resp in r.get("responses", []):
                idx = RANK_MAP.get((resp.get("response_index") or "").strip())
                if idx is None:
                    continue
                txt = []
                for m in resp.get("messages", []):
                    c = m.get("content")
                    if isinstance(c, str):
                        txt.append(c)
                    elif isinstance(c, dict):
                        txt.extend(x for x in (c.get("parts") or []) if isinstance(x, str))
                slots[idx] = " ".join(txt)
            if len(slots) == 4:
                out[r["prompt_id"]] = [slots[i] for i in range(4)]
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


def mean_abs_offdiag_corr(M: np.ndarray) -> float:
    """How much do a rubric's criteria agree with each other across the four responses?

    Four criteria measuring four different things have low inter-correlation. Four criteria that
    have all become 'is this a good answer' have high inter-correlation, and that is the signature
    of a rubric that has stopped discriminating between values.
    """
    A = np.nan_to_num(M, nan=0.0)
    A = A[np.std(A, axis=1) > 1e-9]
    if A.shape[0] < 2:
        return float("nan")
    C = np.corrcoef(A)
    iu = np.triu_indices_from(C, k=1)
    v = C[iu]
    v = v[np.isfinite(v)]
    return float(np.mean(np.abs(v))) if v.size else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", default="world", choices=["world", "personal"])
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    resp = load_responses()
    rank = load_rankings(args.block)
    cids = [c for c in sat_core if c in sat_full and c in rank and c in resp]
    print(f"prompts {len(cids)}   block={args.block}")

    rng = np.random.default_rng(args.seed)
    arms = defaultdict(list)
    icc = defaultdict(list)
    for cid in cids:
        SF, SC = sat_full[cid], sat_core[cid]
        if SF.shape[0] < 4 or SC.shape[0] < 2:
            continue
        k = SC.shape[0]
        rnd = rng.permutation(SF.shape[0])[:k]
        texts = resp[cid]
        scores = {
            "core_rewritten": np.nan_to_num(SC, nan=0.0).mean(axis=0),
            "raw_random_k": np.nan_to_num(SF[rnd], nan=0.0).mean(axis=0),
            "generic_mean_all": np.nan_to_num(SF, nan=0.0).mean(axis=0),
            "length": np.array([float(len(t)) for t in texts]),
            "verbosity": np.array([float(len(set(t.lower().split()))) for t in texts]),
        }
        icc["core_rewritten"].append(mean_abs_offdiag_corr(SC))
        icc["raw_random_k"].append(mean_abs_offdiag_corr(SF[rnd]))
        icc["raw_all"].append(mean_abs_offdiag_corr(SF))
        for pref in rank[cid]:
            for name, s in scores.items():
                arms[name].append(concordance(s, pref))

    def ms(v):
        a = np.asarray(v, float)
        a = a[np.isfinite(a)]
        return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size)

    print(f"\n{'arm':20s} {'concordance':>12s} {'95% CI':>20s} {'n':>7s}   reads a criterion?")
    order = ["core_rewritten", "generic_mean_all", "raw_random_k", "length", "verbosity"]
    reads = {"core_rewritten": "yes", "generic_mean_all": "yes, as a sensor bank",
             "raw_random_k": "yes", "length": "NO", "verbosity": "NO"}
    res = {}
    for name in order:
        m, se, n = ms(arms[name])
        res[name] = {"concordance": round(m, 4),
                     "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": n}
        print(f"  {name:18s} {m:12.4f} [{m - 1.96 * se:7.4f},{m + 1.96 * se:7.4f}] {n:7d}   "
              f"{reads[name]}")

    def paired(a, b):
        x, y = np.asarray(arms[a], float), np.asarray(arms[b], float)
        d = (x - y)[np.isfinite(x - y)]
        m, se = float(d.mean()), float(d.std(ddof=1) / math.sqrt(d.size))
        return {"delta": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
                "z": round(m / se, 2) if se else None}
    contrasts = {"core - generic_mean_all": paired("core_rewritten", "generic_mean_all"),
                 "core - length": paired("core_rewritten", "length"),
                 "core - raw_random_k": paired("core_rewritten", "raw_random_k")}
    print("\npaired contrasts:")
    for k_, v in contrasts.items():
        print(f"  {k_:28s} {v['delta']:+.4f} {v['ci95']}  z={v['z']}")

    print("\ninter-criterion agreement within a rubric (mean |r| across the four responses):")
    for k_ in ("core_rewritten", "raw_random_k", "raw_all"):
        m, se, n = ms(icc[k_])
        res[f"icc_{k_}"] = {"mean_abs_r": round(m, 4), "n": n}
        print(f"  {k_:18s} {m:.4f}   (n={n} prompts)")

    verdict = ("QUALITY DETECTOR -- a content-free or criterion-blind proxy matches core"
               if contrasts["core - generic_mean_all"]["ci95"][0] <= 0
               or contrasts["core - length"]["ci95"][0] <= 0
               else "core beats every proxy that does not read its criteria")
    print(f"\nVERDICT: {verdict}")

    (OUT / "quality_detector.json").write_text(json.dumps(
        {"block": args.block, "prompts": len(cids), "arms": res, "contrasts": contrasts,
         "verdict": verdict,
         "instrument": "one rebuilt 2B judge for every criterion-based arm; the length and "
                       "verbosity arms execute no model at all"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
