"""A06 -- The rule tournament: which aggregation principle predicts humans best?

"Which aggregation rule is legitimate?" is normally argued from axioms, and
Arrow guarantees that argument never terminates.  With a rebuilt satisfaction
layer it becomes an OUT-OF-SAMPLE PREDICTION CONTEST instead:

  each rule selects a different core from coval_full
    -> each core scores the four candidate responses
      -> compare the induced ordering against held-out human world rankings

Entrants
--------
  utility        largest |mean| signed preference
  majority       direction with the largest share of raters
  consensus      strongest lower-quartile support
  constituency   intense supporting bloc, weak minority penalty
  conflict_aware top-2 consensus items PLUS top-2 most polarized items
  no_compression every shared item, unweighted  <- the k=inf control
  random_k4      four shared items chosen at random   <- the floor

`no_compression` and `random_k4` are the two that make the contest honest.
Without the first we cannot tell whether compressing to four items costs
predictive power; without the second we cannot tell whether any rule beats
picking items with no principle at all.

Every score is reported against the shuffled-rubric baseline established in
A04, because roughly half of a naive rubric-predicts-preference number is
generic response quality that any rubric earns for free.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if (p / "covalx").is_dir())))
from covalx import LABELS, load_join, parse_ranking  # noqa: E402

from covalx import rule_score  # noqa: E402

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")


def build_cores(scores: list[np.ndarray], k: int, rng) -> dict[str, list[tuple[int, int]]]:
    """scores[j] = the rating vector of shared item j. Returns rule -> [(item, dir)]."""
    n = len(scores)
    out: dict[str, list[tuple[int, int]]] = {}
    for rule in ("utility", "majority", "consensus", "constituency"):
        ranked = []
        for j, v in enumerate(scores):
            s, d = rule_score(v, rule)
            ranked.append((s, j, d))
        ranked.sort(key=lambda t: (-t[0], t[1]))
        out[rule] = [(j, d) for _, j, d in ranked[:k]]

    # conflict-aware: half consensus, half most-polarized
    pol = []
    for j, v in enumerate(scores):
        v = v[~np.isnan(v)]
        if v.size == 0:
            pol.append((0.0, j, 1))
            continue
        p, ng = float((v > 0).mean()), float((v < 0).mean())
        pol.append((4 * p * ng * float(np.mean(np.abs(v))) / 10.0, j,
                    1 if v.mean() >= 0 else -1))
    cons = []
    for j, v in enumerate(scores):
        s, d = rule_score(v, "consensus")
        cons.append((s, j, d))
    cons.sort(key=lambda t: (-t[0], t[1]))
    pol.sort(key=lambda t: (-t[0], t[1]))
    picked, seen = [], set()
    for _, j, d in cons[: max(1, k // 2)]:
        picked.append((j, d)); seen.add(j)
    for _, j, d in pol:
        if len(picked) >= k:
            break
        if j not in seen:
            picked.append((j, d)); seen.add(j)
    out["conflict_aware"] = picked

    out["no_compression"] = [
        (j, 1 if np.nanmean(v) >= 0 else -1) for j, v in enumerate(scores)
    ]
    idx = rng.permutation(n)[:k]
    out["random_k4"] = [(int(j), 1 if np.nanmean(scores[j]) >= 0 else -1) for j in idx]
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    p.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    p.add_argument("--scores", type=Path, default=round_results("R04", "a04_full.npz"))
    p.add_argument("--out", type=Path, default=Path(_RES + "/a06_rule_tournament.json"))
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--boot", type=int, default=2000)
    a = p.parse_args()

    z = np.load(a.scores, allow_pickle=True)
    sat, meta = z["sat"], z["meta"]
    lut: dict[tuple[str, int, str], float] = {}
    for m, s in zip(meta, sat):
        pid, ci, lab = str(m).split("|")
        lut[(pid, int(ci), lab)] = float(s)
    print(f"satisfaction cells loaded: {len(lut):,}")

    joined = load_join(a.comparisons, a.rubrics)
    rng = np.random.default_rng(20260727)

    hits = misses = 0
    per_prompt: dict[str, dict[str, tuple[int, int]]] = {}
    for pid, comp, rub in joined:
        items = rub.get("coval_full") or []
        crit_scores, ci_map = [], []
        ci = 0
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        for it in items:
            sc = [float(s["score"]) for s in it.get("scores") or []]
            if not sc:
                continue
            if len(sc) >= thr:                     # shared items only
                crit_scores.append(np.array(sc))
                ci_map.append(ci)
            ci += 1
        if len(crit_scores) < a.k:
            continue

        cores = build_cores(crit_scores, a.k, rng)
        hp = []
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            r = parse_ranking(w[0].get("ranking", ""))
            flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
            for x, gx in flat:
                for y, gy in flat:
                    if gx < gy:
                        hp.append((x, y))
        if not hp:
            continue

        res = {}
        for rule, core in cores.items():
            score = {}
            for lab in LABELS:
                vals = []
                for j, d in core:
                    v = lut.get((pid, ci_map[j], lab))
                    if v is not None:
                        vals.append(d * v)
                        hits += 1
                    else:
                        misses += 1
                score[lab] = float(np.mean(vals)) if vals else 0.0
            ok = sum(1 for x, y in hp if score.get(x, 0) > score.get(y, 0))
            res[rule] = (ok, len(hp))
        per_prompt[pid] = res

    cover = hits / max(hits + misses, 1)
    print(f"prompts scored: {len(per_prompt):,}")
    print(f"satisfaction lookup coverage: {cover:.1%} ({hits:,} hits / {misses:,} misses)")
    if cover < 0.90:
        raise SystemExit(
            f"REFUSING TO REPORT: only {cover:.1%} of (prompt, criterion, response) "
            "lookups resolved. Missing cells silently score 0.0, which drags every "
            "rule toward a tie and produces a plausible-looking but meaningless "
            "accuracy. Almost certainly the score file was built with a different "
            "--source than this tournament indexes (core vs full)."
        )
    rules = list(next(iter(per_prompt.values())).keys())
    pids = list(per_prompt)

    print(f"\n{'rule':16s} {'pairwise acc':>13} {'95% CI':>20} {'vs shuffled(.578)':>19}")
    out = {}
    for rule in rules:
        ok = sum(per_prompt[p][rule][0] for p in pids)
        tot = sum(per_prompt[p][rule][1] for p in pids)
        acc = ok / tot
        bs = np.empty(a.boot)
        for i in range(a.boot):
            pick = rng.integers(0, len(pids), size=len(pids))
            o = sum(per_prompt[pids[j]][rule][0] for j in pick)
            t = sum(per_prompt[pids[j]][rule][1] for j in pick)
            bs[i] = o / max(t, 1)
        lo, hi = np.percentile(bs, [2.5, 97.5])
        out[rule] = {"accuracy": acc, "ci": [float(lo), float(hi)], "pairs": tot}
        print(f"{rule:16s} {acc:>13.4f} {f'[{lo:.4f},{hi:.4f}]':>20} {acc-0.5784:>+19.4f}")

    # paired head-to-head against the no-compression control
    print("\n=== paired contrast vs no_compression (prompt-clustered) ===")
    base = "no_compression"
    for rule in rules:
        if rule == base:
            continue
        d = np.array([
            per_prompt[p][rule][0] / max(per_prompt[p][rule][1], 1)
            - per_prompt[p][base][0] / max(per_prompt[p][base][1], 1)
            for p in pids
        ])
        bs = np.array([d[rng.integers(0, len(d), size=len(d))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        verdict = "better" if lo > 0 else "worse" if hi < 0 else "indistinguishable"
        out[rule]["vs_no_compression"] = {"delta": float(d.mean()),
                                          "ci": [float(lo), float(hi)],
                                          "verdict": verdict}
        print(f"  {rule:16s} {d.mean():+.4f} [{lo:+.4f},{hi:+.4f}]  {verdict}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"k": a.k, "prompts": len(pids), "rules": out}, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
