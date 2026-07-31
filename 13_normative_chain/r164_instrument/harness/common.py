from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
sys.path.insert(0, str(ROOT))
LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}


def load_sat(path) -> dict[str, np.ndarray]:
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


def load_texts():
    from covalx.judge import load_join
    out = {}
    for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                ROOT / "data" / "conversation_rubrics.jsonl"):
        out[pid] = ([it["criterion"].strip() for it in r["coval_full"]],
                    [c["criterion"].strip() for c in r["coval_core"]])
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


def load_rankings_flat(block="world"):
    """dict[cid] -> list[np.ndarray] (one per assessment), matches r155/r158."""
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
            if np.isnan(pref[i]) or np.isnan(pref[j]) or np.isnan(score[i]) or np.isnan(score[j]):
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


def score_arm(S: np.ndarray, w) -> np.ndarray:
    M = np.nan_to_num(S, nan=0.0)
    if w is None:
        return M.mean(axis=0)
    ww = w[: M.shape[0]]
    denom = np.abs(ww).sum()
    return (ww[:, None] * M).sum(axis=0) / denom if denom else M.mean(axis=0)


def ms(v):
    a = np.asarray(v, float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return float("nan"), float("nan"), 0
    return float(a.mean()), float(a.std(ddof=1) / math.sqrt(a.size)) if a.size > 1 else 0.0, a.size


# ---------------------------------------------------------------- I1 (r159 "mean" outcome)
def run_i1(sat_full, sat_core, weights, rank_flat, cids_restrict=None):
    cids = [c for c in sat_core if c in sat_full and c in weights and c in rank_flat]
    if cids_restrict is not None:
        cids = [c for c in cids if c in cids_restrict]
    names = ["full_weighted", "raw_topk_weighted", "core_compiled", "full_unweighted"]
    per_prompt = defaultdict(list)
    for cid in cids:
        SF, SC, w = sat_full[cid], sat_core[cid], weights[cid]
        n = min(SF.shape[0], w.shape[0])
        raters = rank_flat[cid]
        if n < 4 or SC.shape[0] < 2 or len(raters) < 4:
            continue
        top = np.argsort(-np.abs(w[:n]))[: SC.shape[0]]
        arms = {"core_compiled": agg(SC), "raw_topk_weighted": agg(SF[top], w[top]),
                "full_weighted": agg(SF[:n], w[:n]), "full_unweighted": agg(SF[:n])}
        for name, s in arms.items():
            cs = np.array([concordance(s, pref) for pref in raters], float)
            cs = cs[np.isfinite(cs)]
            if cs.size < 4:
                continue
            per_prompt[name].append(float(cs.mean()))
    res = {}
    for nm in names:
        m, se, k = ms(per_prompt[nm])
        res[nm] = {"mean": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": k}
    order = sorted(names, key=lambda nm: res[nm]["mean"], reverse=True)
    return {"n_prompts": len(cids), "arms": res, "order": order}


# ---------------------------------------------------------------- I2 (r155 weight_effect)
def run_i2(sat_full, sat_core, weights, rank_flat, cids_restrict=None, seed=0):
    cids = [c for c in sat_core if c in sat_full and c in weights and c in rank_flat]
    if cids_restrict is not None:
        cids = [c for c in cids if c in cids_restrict]
    rng = np.random.default_rng(seed)
    arms = {k: [] for k in ("core_drop", "core_keep", "full_drop", "full_keep", "core_randsign")}
    for cid in cids:
        SF, SC, w = sat_full[cid], sat_core[cid], weights[cid]
        n = min(SF.shape[0], w.shape[0])
        if n < 2 or SC.shape[0] < 2:
            continue
        top = np.argsort(-np.abs(w[:n]))[: SC.shape[0]]
        wc, Sc = w[top], SF[top]
        rs = np.abs(wc) * rng.choice([-1.0, 1.0], size=wc.shape[0])
        sc = {"core_drop": score_arm(SC, None), "core_keep": score_arm(Sc, wc),
              "full_drop": score_arm(SF[:n], None), "full_keep": score_arm(SF[:n], w[:n]),
              "core_randsign": score_arm(Sc, rs)}
        for pref in rank_flat[cid]:
            for k, s in sc.items():
                arms[k].append(concordance(s, pref))

    def paired(a, b):
        d = np.asarray(arms[a], float) - np.asarray(arms[b], float)
        d = d[np.isfinite(d)]
        if d.size < 2:
            return {"delta": None, "n": int(d.size)}
        m, se = float(d.mean()), float(d.std(ddof=1) / math.sqrt(d.size))
        return {"delta": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
                "n": int(d.size), "z": round(m / se, 2) if se else None}

    res = {}
    for k in arms:
        m, se, n = ms(arms[k])
        res[k] = {"concordance": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": n}
    contrasts = {
        "weight_effect (core_keep - core_drop)": paired("core_keep", "core_drop"),
        "selection_effect (full_drop - core_drop)": paired("full_drop", "core_drop"),
        "weight_on_full (full_keep - full_drop)": paired("full_keep", "full_drop"),
        "real_vs_random_sign (core_keep - core_randsign)": paired("core_keep", "core_randsign"),
    }
    return {"n_prompts": len(cids), "arms": res, "contrasts": contrasts}


# ---------------------------------------------------------------- I3 (r158 rewriting)
def run_i3(sat_full, sat_core, texts, rank_flat, cutoff=0.80, cids_restrict=None, seed=0):
    import difflib
    cids = [c for c in sat_core if c in sat_full and c in texts and c in rank_flat]
    if cids_restrict is not None:
        cids = [c for c in cids if c in cids_restrict]
    rng = np.random.default_rng(seed)
    pairs_by_prompt = {}
    for cid in cids:
        full_txt, core_txt = texts[cid]
        SF, SC = sat_full[cid], sat_core[cid]
        low = [t.lower() for t in full_txt]
        found = []
        for ci, ct in enumerate(core_txt):
            if ci >= SC.shape[0]:
                continue
            hit = difflib.get_close_matches(ct.lower(), low, n=1, cutoff=cutoff)
            if not hit:
                continue
            fi = low.index(hit[0])
            if fi >= SF.shape[0]:
                continue
            sim = difflib.SequenceMatcher(None, ct.lower(), hit[0]).ratio()
            found.append((ci, fi, sim))
        if found:
            pairs_by_prompt[cid] = found

    bands = [(0.80, 0.88, "heavier"), (0.88, 0.95, "moderate"), (0.95, 1.01, "near-identical")]
    arms = defaultdict(list)
    band_arms = {b[2]: defaultdict(list) for b in bands}
    npairs = 0
    for cid, found in pairs_by_prompt.items():
        SF, SC = sat_full[cid], sat_core[cid]
        ci = [p[0] for p in found]
        fi = [p[1] for p in found]
        npairs += len(found)
        rw = np.nan_to_num(SC[ci], nan=0.0).mean(axis=0)
        raw = np.nan_to_num(SF[fi], nan=0.0).mean(axis=0)
        pool = [i for i in range(SF.shape[0]) if i not in set(fi)]
        alt = rng.permutation(pool)[: len(fi)] if len(pool) >= len(fi) else fi
        oth = np.nan_to_num(SF[list(alt)], nan=0.0).mean(axis=0)
        msim = float(np.mean([p[2] for p in found]))
        band = next((b[2] for b in bands if b[0] <= msim < b[1]), None)
        for pref in rank_flat[cid]:
            arms["rewritten"].append(concordance(rw, pref))
            arms["raw_source"].append(concordance(raw, pref))
            arms["other_raw_same_n"].append(concordance(oth, pref))
            if band:
                band_arms[band]["rewritten"].append(concordance(rw, pref))
                band_arms[band]["raw_source"].append(concordance(raw, pref))

    res = {}
    for k in ("rewritten", "raw_source", "other_raw_same_n"):
        m, se, n = ms(arms[k])
        res[k] = {"concordance": round(m, 4), "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)], "n": n}
    d = np.asarray(arms["rewritten"], float) - np.asarray(arms["raw_source"], float)
    d = d[np.isfinite(d)]
    if d.size >= 2:
        dm, dse = float(d.mean()), float(d.std(ddof=1) / math.sqrt(d.size))
        paired_delta = {"delta": round(dm, 4), "ci95": [round(dm - 1.96 * dse, 4), round(dm + 1.96 * dse, 4)],
                        "z": round(dm / dse, 2) if dse else None, "n": int(d.size)}
    else:
        paired_delta = {"delta": None, "n": int(d.size)}

    dose = {}
    for _lo, _hi, name in bands:
        a, b = band_arms[name]["rewritten"], band_arms[name]["raw_source"]
        if len(a) < 30:
            dose[name] = {"n": len(a), "delta": None}
            continue
        dd = np.asarray(a, float) - np.asarray(b, float)
        dd = dd[np.isfinite(dd)]
        m2, se2 = float(dd.mean()), float(dd.std(ddof=1) / math.sqrt(dd.size))
        dose[name] = {"n": int(dd.size), "delta": round(m2, 4),
                      "ci95": [round(m2 - 1.96 * se2, 4), round(m2 + 1.96 * se2, 4)]}

    return {"prompts": len(cids), "prompts_with_pairs": len(pairs_by_prompt), "pairs": npairs,
            "arms": res, "paired_delta": paired_delta, "dose_response": dose}
