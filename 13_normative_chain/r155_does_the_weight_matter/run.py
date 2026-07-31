"""Does deleting the weight cost anything? The compiler comparison, with everything else held fixed.

r154 established that force IS elicited in this release -- through the signed weight, not through
wording -- and that coval_core items carry exactly one key, `criterion`, in 3,899 of 3,899 cases.
So compilation deletes force. The memo's flagship question is whether that deletion has any
behavioural consequence, and until now the plan was an LLM compiler bake-off: prose arm, structured
arm, typed arm.

That design is worse than it looks. Three LLM compilers differ in a dozen uncontrolled ways at
once -- wording, length, ordering, how many items survive -- and any difference downstream is
unattributable. The clean version holds the CRITERIA FIXED and varies only the one thing
compilation actually does:

    DROP   score a response by the UNWEIGHTED mean satisfaction over its criteria   (= what core does)
    KEEP   score it by the WEIGHT-WEIGHTED mean over the SAME criteria             (= force retained)

Same criteria, same judge, same responses, same aggregation shape. The single difference is whether
the number people attached to each criterion survives into the scoring. Nothing else can explain a
gap, which is what makes the comparison worth running at all.

THE OUTCOME IS OUT-OF-SAMPLE AGREEMENT WITH HUMANS, not internal consistency. For each prompt, each
scoring rule induces a ranking over the four responses; that ranking is compared against each
annotator's own ranking by pairwise concordance. A rule that better recovers what people actually
chose is the better compilation of what they wanted.

FOUR ARMS, because two would leave the obvious rival alive:

    core_drop     unweighted over the compiled four        what the release ships
    core_keep     weighted over the compiled four          the deletion undone
    full_drop     unweighted over all criteria             does the SELECTION matter, absent weight
    full_keep     weighted over all criteria               the upper bound this data allows

core_keep minus core_drop isolates the weight. full_drop minus core_drop isolates the selection.
Reporting only the first would let a reader attribute to force what is really about which four
items were chosen.

CONTROLS. A random-weight arm, where each criterion keeps its magnitude but gets a random sign,
says how much of any weighted advantage is the weights CARRYING INFORMATION rather than merely
being unequal. And a shuffled-ranking null gives the concordance floor.

INSTRUMENT: every arm routes through the same rebuilt 2B satisfaction judge on the same responses,
so the judge cannot produce a difference BETWEEN arms -- which is the only reason a difference here
is readable at all.
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


def load_weights() -> dict[str, np.ndarray]:
    """Mean signed weight per criterion, keyed by prompt_id via the text join."""
    from covalx.judge import load_join
    out = {}
    for pid, _prompt, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                     ROOT / "data" / "conversation_rubrics.jsonl"):
        out[pid] = np.array([np.mean([s["score"] for s in it["scores"]])
                             for it in r["coval_full"]], float)
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


def concordance(score: np.ndarray, pref: np.ndarray) -> float:
    """Share of the six response pairs ordered the same way. Ties count as half on either side."""
    good = tot = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(pref[i]) or np.isnan(pref[j]) or np.isnan(score[i]) or np.isnan(score[j]):
                continue
            tot += 1
            ds, dp = score[i] - score[j], pref[i] - pref[j]
            if dp == 0 or ds == 0:
                good += 0.5
            elif (ds > 0) == (dp > 0):
                good += 1
    return good / tot if tot else float("nan")


def score_arm(S: np.ndarray, w: np.ndarray | None) -> np.ndarray:
    """Aggregate criterion x response satisfaction into a score per response.

    Unweighted is the plain mean, which is what a rubric with no weights can do. Weighted uses the
    signed mean rating: a negatively-rated criterion SUBTRACTS its satisfaction, which is the whole
    content of a prohibition and the exact thing an unweighted mean cannot express.
    """
    M = np.nan_to_num(S, nan=0.0)
    if w is None:
        return M.mean(axis=0)
    ww = w[: M.shape[0]]
    denom = np.abs(ww).sum()
    return (ww[:, None] * M).sum(axis=0) / denom if denom else M.mean(axis=0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--block", choices=["world", "personal"], default="world")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    base = ROOT / "01_object_and_rebuild" / "r04_rebuild_satisfaction" / "results"
    sat_full, sat_core = load_sat(base / "a04_full.npz"), load_sat(base / "a04_core.npz")
    weights = load_weights()
    rank = load_rankings(args.block)

    # core criteria are a SUBSET of full, but the release gives no pointer, so the core arm's
    # weights are unavailable directly. Use the full arm's weights restricted to the top-|w| items,
    # which is the compiler's own documented selection rule -- and state that this is a
    # RECONSTRUCTION of the weights core would have had, not a recovery of them.
    cids = [c for c in sat_core if c in sat_full and c in weights and c in rank]
    print(f"prompts usable across all four arms: {len(cids)}   block={args.block}")

    arms = {k: [] for k in ("core_drop", "core_keep", "full_drop", "full_keep", "core_randsign")}
    rng = np.random.default_rng(args.seeds[0])
    floor = []
    for cid in cids:
        SF, SC, w = sat_full[cid], sat_core[cid], weights[cid]
        n = min(SF.shape[0], w.shape[0])
        if n < 2 or SC.shape[0] < 2:
            continue
        top = np.argsort(-np.abs(w[:n]))[: SC.shape[0]]      # the compiler's documented rule
        wc, Sc = w[top], SF[top]
        rs = np.abs(wc) * rng.choice([-1.0, 1.0], size=wc.shape[0])
        sc = {
            "core_drop": score_arm(SC, None),
            "core_keep": score_arm(Sc, wc),
            "full_drop": score_arm(SF[:n], None),
            "full_keep": score_arm(SF[:n], w[:n]),
            "core_randsign": score_arm(Sc, rs),
        }
        for pref in rank[cid]:
            for k, s in sc.items():
                arms[k].append(concordance(s, pref))
            floor.append(concordance(rng.permutation(sc["core_drop"]), pref))

    def ms(v):
        a = np.asarray(v, float)
        a = a[~np.isnan(a)]
        return float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)), a.size

    print(f"\n{'arm':16s} {'concordance':>12s} {'95% CI':>20s} {'n':>7s}")
    res = {}
    for k in ("core_drop", "core_keep", "full_drop", "full_keep", "core_randsign"):
        m, se, n = ms(arms[k])
        res[k] = {"concordance": round(m, 4),
                  "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": n}
        print(f"  {k:14s} {m:12.4f} [{m - 1.96 * se:7.4f},{m + 1.96 * se:7.4f}] {n:7d}")
    fm, fse, fn = ms(floor)
    print(f"  {'shuffled floor':14s} {fm:12.4f} [{fm - 1.96 * fse:7.4f},{fm + 1.96 * fse:7.4f}] "
          f"{fn:7d}")

    # paired contrasts: same prompt, same rater, so the pairing removes prompt difficulty entirely
    def paired(a, b):
        d = np.asarray(arms[a], float) - np.asarray(arms[b], float)
        d = d[~np.isnan(d)]
        m, se = float(d.mean()), float(d.std(ddof=1) / math.sqrt(d.size))
        return {"delta": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
                "n": int(d.size), "z": round(m / se, 2) if se else None}
    contrasts = {
        "weight_effect (core_keep - core_drop)": paired("core_keep", "core_drop"),
        "selection_effect (full_drop - core_drop)": paired("full_drop", "core_drop"),
        "weight_on_full (full_keep - full_drop)": paired("full_keep", "full_drop"),
        "real_vs_random_sign (core_keep - core_randsign)": paired("core_keep", "core_randsign"),
    }
    print("\npaired contrasts (same prompt, same rater):")
    for k, v in contrasts.items():
        print(f"  {k:48s} {v['delta']:+.4f} {v['ci95']}  z={v['z']}")

    (OUT / "weight_matters.json").write_text(json.dumps(
        {"block": args.block, "prompts": len(cids), "arms": res,
         "shuffled_floor": {"concordance": round(fm, 4), "n": fn},
         "contrasts": contrasts,
         "caveat": ("core's own weights are not recoverable -- the release gives no pointer from a "
                    "core item back to a full one -- so the core_keep arm reconstructs them by the "
                    "compiler's documented top-|w| rule. That is a reconstruction, not a recovery."),
         "instrument": "one rebuilt 2B judge, shared by every arm, so it cannot produce a "
                       "between-arm difference"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
