"""The instrument attack, re-analysed with clustered SEs and kept in the repo rather than in /tmp.

An adversary rescored all 968 prompts under two alternative model families and began a set of
prompt-template variants on the reference model. Its harness and tensors were written to a
session-scoped scratchpad, which is where results go to disappear -- so they are copied in here and
re-analysed with the correct variance estimator, which the harness's own code did not use. Its
author flagged that itself: the replication code is a byte-for-byte port of r155's SE computation,
pairwise rows treated as independent.

WHAT THE TWO AXES SEPARATE, and why both are needed.

    MODEL FAMILY   phi-3.5-mini and qwen2.5-3b against the reference Qwen3.5-2B-Base.
                   Answers: is this claim a property of one model's training?
    PROMPT         few-shot order swapped, few-shot removed, negative-polarity exemplars, all on the
                   REFERENCE model. Answers: is it a property of how the question was asked?

r130 had already shown the core-minus-full gap flips sign under a question-polarity variant. That is
the PROMPT axis. Nothing in this phase had tested the MODEL axis until now, and the two do not have
to agree -- a claim can be model-robust and prompt-fragile, which is exactly what the compilation
direction turns out to be.

THE DEFAULT VARIANT IS A POSITIVE CONTROL AND IS REPORTED AS ONE. Same model, same prompt template,
same 300-prompt sample: it must reproduce the reference restricted to those prompts, or the variant
machinery is measuring itself. It does -- +0.0104 against +0.0093, a difference of 0.0011.

AND THE SUBSET IS A SAMPLE, NOT A STRATUM. The 300 prompts are drawn by a seeded permutation, not by
taking the first 300, which is the failure this project has a standing note about. The reference
reads +0.0093 on those 300 and +0.0015 on all 968; under clustering both are nulls, so the gap is
sampling variation and not a selection effect.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402

import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx.cluster import two_way_se  # noqa: E402

LETTERS = "ABCD"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
REF = round_results("R04")


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


def load_rankings(block="world"):
    out: dict[str, list[tuple[str, np.ndarray]]] = defaultdict(list)
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            for a in rec.get("assessments", []):
                for b in (a.get("ranking_blocks") or {}).get(block, []) or []:
                    t = b.get("ranking")
                    if not t:
                        continue
                    v = np.full(4, np.nan)
                    for gi, g in enumerate(t.replace(" ", "").split(">")):
                        for L in g.split("="):
                            if L in RANK_MAP:
                                v[RANK_MAP[L]] = -gi
                    if not np.isnan(v).all():
                        out[a["conversation_id"]].append((rec["annotator_id"], v))
                        break
    return out


def conc(s, p):
    g = t = 0.0
    for i in range(4):
        for j in range(i + 1, 4):
            if np.isnan(p[i]) or np.isnan(p[j]):
                continue
            t += 1
            ds, dp = s[i] - s[j], p[i] - p[j]
            if dp == 0 or ds == 0:
                g += 0.5
            elif (ds > 0) == (dp > 0):
                g += 1
    return g / t if t else float("nan")


def agg(S, w=None):
    M = np.nan_to_num(S, nan=0.0)
    if w is None:
        return M.mean(axis=0)
    d = np.abs(w).sum()
    return (w[:, None] * M).sum(axis=0) / d if d else M.mean(axis=0)


def arms_and_weight_effect(sf, sc, W, rank, restrict=None):
    """Returns per-arm concordance rows and the weight-deletion contrast, all with cluster keys."""
    rows = defaultdict(list)
    keys = []
    we = []
    for cid in sf:
        if cid not in sc or cid not in W or cid not in rank:
            continue
        if restrict is not None and cid not in restrict:
            continue
        SF, SC, w = sf[cid], sc[cid], W[cid]
        n = min(SF.shape[0], len(w))
        if n < 4 or SC.shape[0] < 2:
            continue
        top = np.argsort(-np.abs(w[:n]))[: SC.shape[0]]
        a = {"full_weighted": agg(SF[:n], w[:n]), "core_compiled": agg(SC),
             "raw_topk_weighted": agg(SF[top], w[top]), "full_unweighted": agg(SF[:n])}
        ck, cd = agg(SF[top], w[top]), agg(SC)
        for aid, pref in rank[cid]:
            for k, s in a.items():
                rows[k].append(conc(s, pref))
            keys.append((cid, aid))
            we.append(conc(ck, pref) - conc(cd, pref))
    return rows, keys, we


def rewriting_contrast(sf, sc, rank, texts, cutoff=0.80):
    """The rewriting effect under an arbitrary judge, with cluster keys.

    The matched pair set is TEXT-ONLY and therefore identical across judges by construction, so a
    difference between judges here is the judge and cannot be the matching.
    """
    import difflib
    rows, keys, bands = [], [], defaultdict(list)
    B = [(0.80, 0.88, "heavier"), (0.88, 0.95, "moderate"), (0.95, 1.01, "near-identical")]
    for cid, (ft, ct) in texts.items():
        if cid not in sf or cid not in sc or cid not in rank:
            continue
        low = [t.lower() for t in ft]
        found = []
        for ci, c in enumerate(ct):
            if ci >= sc[cid].shape[0]:
                continue
            h = difflib.get_close_matches(c.lower(), low, n=1, cutoff=cutoff)
            if not h:
                continue
            fi = low.index(h[0])
            if fi < sf[cid].shape[0]:
                found.append((ci, fi, difflib.SequenceMatcher(None, c.lower(), h[0]).ratio()))
        if not found:
            continue
        rw = np.nan_to_num(sc[cid][[p_[0] for p_ in found]], nan=0.0).mean(axis=0)
        raw = np.nan_to_num(sf[cid][[p_[1] for p_ in found]], nan=0.0).mean(axis=0)
        msim = float(np.mean([p_[2] for p_ in found]))
        bd = next((b[2] for b in B if b[0] <= msim < b[1]), None)
        for aid, pref in rank[cid]:
            d = conc(rw, pref) - conc(raw, pref)
            rows.append(d)
            keys.append((cid, aid))
            if bd:
                bands[bd].append((d, cid, aid))
    return rows, keys, bands


def main() -> int:
    W, rank = load_weights(), load_rankings()
    ref_f, ref_c = load_sat(REF / "a04_full.npz"), load_sat(REF / "a04_core.npz")
    R = HERE / "results"

    judges = {"reference": (ref_f, ref_c)}
    for tag in ("phi", "qwen3b"):
        f, c = R / f"sat_full_{tag}.npz", R / f"sat_core_{tag}.npz"
        if f.exists() and c.exists():
            judges[tag] = (load_sat(f), load_sat(c))
    variants = {}
    for v in ("default", "swapped", "no_fewshot", "neg_polarity"):
        f, c = R / f"sat_full_variant_{v}.npz", R / f"sat_core_variant_{v}.npz"
        if f.exists() and c.exists():
            variants[v] = (load_sat(f), load_sat(c))

    print("MODEL-FAMILY AXIS  (all 968 prompts; concordance with individual world rankings)")
    print(f"{'judge':12s} {'full_wtd':>9s} {'core':>9s} {'raw_topk':>9s} {'full_unw':>9s} "
          f"{'top-bottom gap':>15s}")
    out = {"model_axis": {}, "prompt_axis": {}}
    for name, (sf, sc) in judges.items():
        rows, keys, we = arms_and_weight_effect(sf, sc, W, rank)
        m = {k: float(np.nanmean(v)) for k, v in rows.items()}
        gap = m["full_weighted"] - m["full_unweighted"]
        s = two_way_se(we, [p for p, _r in keys], [r for _p, r in keys])
        out["model_axis"][name] = {"arms": {k: round(v, 4) for k, v in m.items()},
                                   "top_bottom_gap": round(gap, 4), "weight_effect": s}
        print(f"  {name:10s} {m['full_weighted']:9.4f} {m['core_compiled']:9.4f} "
              f"{m['raw_topk_weighted']:9.4f} {m['full_unweighted']:9.4f} {gap:15.4f}")
    print("\nweight deletion (raw_topk_weighted - core_compiled), TWO-WAY CLUSTERED:")
    for name, d in out["model_axis"].items():
        s = d["weight_effect"]
        print(f"  {name:10s} {s['mean']:+.4f}  se iid {s['se_iid']:.4f} -> 2way {s['se_2way']:.4f} "
              f"(x{s['inflation']})  z {s['z_2way']}")

    if variants:
        print(f"\nPROMPT AXIS  (reference model, {len(variants)} of 4 variants ready, n=300 sample)")
        for v, (sf, sc) in variants.items():
            restrict = set(sf) & set(sc)
            _r, keys, we = arms_and_weight_effect(sf, sc, W, rank, restrict=restrict)
            s = two_way_se(we, [p for p, _r2 in keys], [r for _p, r in keys])
            _r2, keys2, we2 = arms_and_weight_effect(ref_f, ref_c, W, rank, restrict=restrict)
            s2 = two_way_se(we2, [p for p, _r3 in keys2], [r for _p, r in keys2])
            out["prompt_axis"][v] = {"variant": s, "reference_same_prompts": s2}
            tag = "  <- POSITIVE CONTROL: must match the reference" if v == "default" else ""
            print(f"  {v:14s} {s['mean']:+.4f} z {s['z_2way']}   "
                  f"reference on the same prompts {s2['mean']:+.4f} z {s2['z_2way']}{tag}")

    # the rewriting effect across judges, clustered -- the claim I overstated on phi alone
    from covalx.judge import load_join
    texts = {pid: ([it["criterion"].strip() for it in r["coval_full"]],
                   [c["criterion"].strip() for c in r["coval_core"]])
             for pid, _p, r in load_join(ROOT / "data" / "comparisons.jsonl",
                                         ROOT / "data" / "conversation_rubrics.jsonl")}
    print("\nREWRITING EFFECT across judges, two-way clustered "
          "(matched pair set is text-only, identical across judges by construction)")
    out["rewriting"] = {}
    for name, (sf, sc) in judges.items():
        rows, keys, bands = rewriting_contrast(sf, sc, rank, texts)
        s = two_way_se(rows, [p for p, _r in keys], [r for _p, r in keys])
        bs = {}
        for b, vals in bands.items():
            sb = two_way_se([v for v, _c, _a in vals], [c for _v, c, _a in vals],
                            [a for _v, _c, a in vals])
            bs[b] = {"mean": sb["mean"], "z": sb["z_2way"]}
        mono = (bs.get("heavier", {}).get("mean", 0) > bs.get("moderate", {}).get("mean", 0)
                > bs.get("near-identical", {}).get("mean", 0)) if len(bs) == 3 else None
        out["rewriting"][name] = {"overall": s, "bands": bs, "monotonic": mono}
        print(f"  {name:10s} {s['mean']:+.4f} z {s['z_2way']:>6}   bands "
              + " ".join(f"{b[:4]}={bs[b]['mean']:+.4f}" for b in
                         ("heavier", "moderate", "near-identical") if b in bs)
              + f"   monotonic: {mono}")

    (HERE / "results" / "instrument_clustered.json").write_text(json.dumps(out, indent=1))
    print("\nNOTE: every z above is two-way clustered on prompt and rater. The harness's own "
          "numbers were iid and its author flagged them as optimistic by 2.6-3.1x.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
