"""Scoring a person's criteria against their OWN ranking is a consistency check, not a validity test.

An adversary attacking the framing rather than the arithmetic found the thing that matters, and the
release's own documentation confirms it. The task flow per prompt is, in order:

    unacceptable check -> PERSONAL RANKING + written rationale -> WORLD RANKING + written rationale
    -> prompt-level ratings -> RUBRIC ITEM AUTHORING

The annotator ranks the four responses and explains in prose WHY, and only then writes criteria. So
every concordance number in r155 through r161 is measuring, in part, whether a person's post-hoc
criteria reproduce the ranking they had just finished justifying. That is not a rubric predicting a
preference. It is a person being consistent with themselves twenty seconds later, and it would be
high even if the criteria captured nothing transferable at all.

THE FIX IS IN THE DATA. r142 recovered authorship: a criterion rated by exactly one person was
written by that person. So a person's OWN rubric can be built and scored two ways:

    WITHIN   annotator A's own criteria against A's own ranking      contaminated by design
    CROSS    annotator A's own criteria against a DIFFERENT person's ranking   clean

If the phase's conclusions hold cross-person they survive. If they hold only within-person, the
phase was measuring rationalisation and the compilation comparison was a comparison of two ways of
reproducing an answer the annotator had already given.

    within >> cross ~ chance      the criteria are private rationalisation and transfer nothing
    within >  cross >  chance     both, and the gap is the size of the contamination
    within ~= cross               no contamination; the estimand was fine all along

BOTH BLOCKS ARE RUN. Personal ranking comes first in the session and world second, so if
rationalisation is driving this, the personal block should be MORE contaminated than the world one --
a directional prediction the design makes before seeing the numbers.

CONTROLS. A rubric of criteria authored by OTHER people on the same prompt, matched on count, says
how much of cross-person concordance is just "these are criteria about this prompt" rather than
anything about the author. And a shuffled-ranking floor bounds the whole scale.
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


def load_sat() -> dict[str, np.ndarray]:
    z = np.load(round_results("R04")
                / "a04_full.npz", allow_pickle=True)
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


def load_authored():
    """prompt -> author -> [(criterion_index, own_weight)] for SELF-AUTHORED criteria only.

    Self-authored means rated by exactly one person, which r142 established is the signature of an
    item created in that person's own session and never shown to anyone else.
    """
    from covalx.judge import load_join
    out: dict[str, dict[str, list[tuple[int, float]]]] = defaultdict(lambda: defaultdict(list))
    for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                ROOT / "data" / "conversation_rubrics.jsonl"):
        for i, it in enumerate(r["coval_full"]):
            if len(it["scores"]) == 1:
                s = it["scores"][0]
                out[pid][s["annotator_id"]].append((i, float(s["score"])))
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


def agg(S, w):
    M = np.nan_to_num(S, nan=0.0)
    d = np.abs(w).sum()
    return (w[:, None] * M).sum(axis=0) / d if d else M.mean(axis=0)


def run(block: str, sat, authored, seed: int):
    """Rows now carry their prompt and rater so the SE can be clustered on both.

    The first version reported iid intervals over (author, ranking) rows. Those rows share a prompt
    -- same four responses, same criterion pool -- and share a rater, whose ranking style travels
    with them. An adversary showed that inflates the SE by 2.6 to 3.1x elsewhere in this phase, and
    the contamination gap here is small enough that it matters.
    """
    rank = load_rankings(block)
    rng = np.random.default_rng(seed)
    within, cross, others, floor = [], [], [], []
    cl_w, cl_c = [], []          # (prompt, rater) keys for two-way clustering
    n_pairs = 0
    for pid, by_author in authored.items():
        M = sat.get(pid)
        if M is None or pid not in rank:
            continue
        auths = [a for a in by_author if a in rank[pid] and by_author[a]]
        if len(auths) < 2:
            continue
        for a in auths:
            idx = [i for i, _w in by_author[a] if i < M.shape[0]]
            w = np.array([wt for i, wt in by_author[a] if i < M.shape[0]], float)
            if len(idx) < 1 or np.abs(w).sum() == 0:
                continue
            s = agg(M[idx], w)
            within.append(concordance(s, rank[pid][a]))
            cl_w.append((pid, a))
            for b in auths:
                if b == a:
                    continue
                cross.append(concordance(s, rank[pid][b]))
                cl_c.append((pid, b))          # cluster on the RATER whose ranking is scored
                n_pairs += 1
                # control: a same-size rubric of criteria authored by SOMEONE ELSE on this prompt
                pool = [(i, wt) for c in auths if c != a
                        for i, wt in by_author[c] if i < M.shape[0]]
                if len(pool) >= len(idx):
                    pick = [pool[k] for k in rng.permutation(len(pool))[: len(idx)]]
                    so = agg(M[[i for i, _ in pick]], np.array([x for _, x in pick], float))
                    others.append(concordance(so, rank[pid][b]))
                floor.append(concordance(rng.permutation(s), rank[pid][b]))
    return within, cross, others, floor, n_pairs, cl_w, cl_c


def ms(v):
    a = np.asarray(v, float)
    a = a[np.isfinite(a)]
    return (float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), int(a.size)) \
        if a.size > 1 else (float("nan"), float("nan"), int(a.size))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    sat = load_sat()
    authored = load_authored()
    print(f"prompts with self-authored criteria: {len(authored)}")

    res = {}
    for block in ("personal", "world"):
        within, cross, others, floor, npairs, cl_w, cl_c = run(block, sat, authored, args.seed)
        from covalx.cluster import two_way_se
        cw = two_way_se(within, [p for p, _r in cl_w], [r for _p, r in cl_w])
        cc = two_way_se(cross, [p for p, _r in cl_c], [r for _p, r in cl_c])
        mw, sw, nw = ms(within)
        mc, sc, nc = ms(cross)
        mo, so, no = ms(others)
        mf, sf, nf = ms(floor)
        gap = mw - mc
        gap_se = math.sqrt(cw["se_2way"] ** 2 + cc["se_2way"] ** 2)   # clustered, not iid
        res[block] = {
            "within": {"c": round(mw, 4), "ci": [round(mw - 1.96 * sw, 4),
                                                 round(mw + 1.96 * sw, 4)], "n": nw},
            "cross": {"c": round(mc, 4), "ci": [round(mc - 1.96 * sc, 4),
                                                round(mc + 1.96 * sc, 4)], "n": nc},
            "others_criteria": {"c": round(mo, 4), "n": no},
            "floor": {"c": round(mf, 4), "n": nf},
            "within_clustered": cw, "cross_clustered": cc,
            "contamination_gap": round(gap, 4),
            "gap_ci": [round(gap - 1.96 * gap_se, 4), round(gap + 1.96 * gap_se, 4)],
            "cross_over_floor": round(mc - mf, 4),
        }
        print(f"\n{block.upper()} block   (author-ranking pairs {npairs})")
        print(f"  within  own criteria vs OWN ranking      {mw:.4f} "
              f"[{mw - 1.96 * sw:.4f},{mw + 1.96 * sw:.4f}]  n={nw}")
        print(f"  cross   own criteria vs ANOTHER ranking  {mc:.4f} "
              f"[{mc - 1.96 * sc:.4f},{mc + 1.96 * sc:.4f}]  n={nc}")
        print(f"  control others' criteria vs that ranking {mo:.4f}  n={no}")
        print(f"  floor   shuffled score                   {mf:.4f}")
        print(f"  SE inflation from two-way clustering: within x{cw['inflation']}  "
              f"cross x{cc['inflation']}")
        print(f"  CONTAMINATION GAP within - cross = {gap:+.4f} "
              f"[{gap - 1.96 * gap_se:+.4f},{gap + 1.96 * gap_se:+.4f}]  (CLUSTERED)  "
              f"z={gap / gap_se:.2f}")
        print(f"  cross above floor: {mc - mf:+.4f}  <- what actually transfers between people")

    p, w = res["personal"]["contamination_gap"], res["world"]["contamination_gap"]
    pr = res["personal"]["gap_ci"][0] > 0 or res["personal"]["gap_ci"][1] < 0
    wr = res["world"]["gap_ci"][0] > 0 or res["world"]["gap_ci"][1] < 0
    print(f"\nprediction made before the run: personal is ranked FIRST in the session, so if "
          f"rationalisation drives this, personal should be MORE contaminated than world.")
    print(f"  personal gap {p:+.4f} {'resolved' if pr else 'CI SPANS ZERO'}   "
          f"world gap {w:+.4f} {'resolved' if wr else 'CI SPANS ZERO'}")
    # A COMPARISON BETWEEN TWO POINT ESTIMATES, ONE OF WHICH IS NOT DISTINGUISHABLE FROM ZERO, IS
    # NOT A TEST. Under iid SEs both gaps excluded zero and this printed PREDICTION HELD. Clustered,
    # the personal block spans zero -- it carries a fifth of the world block's rows -- so the
    # ordering of the two point estimates decides nothing.
    print("  VERDICT: " + ("both resolved and personal > world -- prediction held"
                           if (pr and wr and p > w) else
                           "UNDECIDED -- the personal gap is not resolved, so comparing the two "
                           "point estimates tests nothing"))

    (OUT / "whose_ranking.json").write_text(json.dumps(
        {"results": res, "prediction_personal_more_contaminated": bool(p > w),
         "task_flow": "unacceptable -> personal ranking + rationale -> world ranking + rationale "
                      "-> prompt ratings -> RUBRIC AUTHORING LAST (DATASET_CARD lines 106-114)",
         "instrument": "one rebuilt 2B judge, identical for every arm"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
