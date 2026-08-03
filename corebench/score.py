#!/usr/bin/env python3
"""
corebench/score.py -- score one core on all 37 dimensions. See corebench/DIMENSIONS.md.

CONTRACT (from DIMENSIONS.md, restated here because a contract in another file is a
limitation nobody reads at the moment the belief forms):
  * every dimension reports value, FLOOR, CEILING and normalized position
  * floor == ceiling  ->  DEGENERATE, reported as such, never scored
  * not computable here -> REGISTERED with what it would require, never blank, never
    "planned", never silently omitted
  * no dimension may be dropped because it is unflattering

WEIGHTS. A generated core carries no importance weights -- `coval_core` items have only
`criterion`, while `coval_full` items carry `scores`. So the core's predicted score for a
response is the UNWEIGHTED sum of its criteria's satisfactions. That is a modelling choice,
it is stated here rather than buried, and it is why E-family parsimony is measured in
criteria rather than in weight mass.
"""
from __future__ import annotations
import argparse, collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
SEEDS = [0, 1, 2]
DEMO_AXES = ["age", "ai_concern_level", "country_of_residence", "education_level",
             "gender", "generative_ai_usage"]

REGISTERED = {
    "F3_judge_swap": "a second judge model held to the same prompt contract",
    "F4_prompt_format": "a second judge prompt template, pre-registered",
    "H3_cross_release": "a second values-annotation release with this schema",
    "X1_construct_validity": "an external gold standard for what a core should preserve",
    "X2_causal_identification": "intervening on how criteria are written, not observing them",
    "X3_temporal_resolution": "timestamps the release does not carry",
}


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def parse_ranking(s):
    sc = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                sc[tok] = -lvl
    return [sc[c] for c in L] if len(sc) == 4 else None


def load_sat(p):
    d = np.load(p, allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def yvec(sat_p, idxs):
    return np.array([sum(sat_p.get((i, x), 0.0) for i in idxs) for x in L])


def tau_b(a, b):
    n, c, d = len(a), 0, 0
    ta = tb = 0
    for i in range(n):
        for j in range(i + 1, n):
            da, db = a[i] - a[j], b[i] - b[j]
            if da == 0 and db == 0:
                ta += 1; tb += 1
            elif da == 0:
                ta += 1
            elif db == 0:
                tb += 1
            elif da * db > 0:
                c += 1
            else:
                d += 1
    tot = n * (n - 1) / 2
    den = math.sqrt((tot - ta) * (tot - tb))
    return (c - d) / den if den else 0.0


def load_targets():
    """held-out human rankings + per-annotator demographics, per prompt"""
    demo = {}
    for line in open(ROOT / "data" / "annotators.jsonl", encoding="utf-8"):
        r = json.loads(line)
        demo[r["annotator_id"]] = r.get("demographics") or {}
    out = collections.defaultdict(list)
    unacc = collections.defaultdict(list)
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        for asm in rec.get("metadata", {}).get("assessments", []):
            rb = asm.get("ranking_blocks") or {}
            aid = asm.get("annotator_id")
            for e in rb.get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y:
                    out[pid].append((y, demo.get(aid, {})))
            for e in rb.get("unacceptable") or []:
                for r_ in e.get("rating") or []:
                    t = str(r_).strip()
                    if t[:1] in L and "unacceptable" in t.lower():
                        unacc[pid].append(t[0])
    return out, unacc


def score_core(sat, core_texts, targets, unacc, full_sat, full_texts, label=""):
    """-> {dim: (value, floor, ceiling)}. UNCOMPUTED is never blank."""
    pids = [p for p in sat if p in targets and len(targets[p]) >= 2]
    D = {}

    # ---- the core's class per prompt, and the global constant baseline
    core_y = {p: yvec(sat[p], sorted({i for i, _ in sat[p]})) for p in pids}
    core_cls = {p: cls(core_y[p]) for p in pids}
    hum_cls = {p: [tuple(np.sign(np.array(y)[[a for a, _ in PAIRS]]
                                - np.array(y)[[b for _, b in PAIRS]]).astype(float))
                   for y, _d in targets[p]] for p in pids}
    glob = collections.Counter(c for p in pids for c in hum_cls[p])
    const_c = glob.most_common(1)[0][0]

    def held(p, rng):
        v = targets[p]
        j = int(rng.integers(len(v)))
        return v[j], v[:j] + v[j + 1:]

    # ---- A · FIDELITY, averaged over seeds
    acc = collections.defaultdict(list)
    for s in SEEDS:
        rng = np.random.default_rng(s)
        a1 = a2 = a3 = a4 = a5 = a6 = 0; n = 0
        f_const = f_ceil = 0
        for p in pids:
            (hy, _d), rest = held(p, rng)
            if not rest:
                continue
            n += 1
            hc = cls(hy)
            a1 += core_cls[p] == hc
            a2 += float(np.mean([core_cls[p][t] == hc[t] for t in range(6)]))
            a3 += int(np.argmax(core_y[p]) == int(np.argmax(hy)))
            a4 += int(np.argmin(core_y[p]) == int(np.argmin(hy)))
            a5 += tau_b(list(core_y[p]), list(hy))
            modal = collections.Counter(cls(y) for y, _ in rest).most_common(1)[0][0]
            a6 += core_cls[p] == modal
            f_const += const_c == hc
            f_ceil += cls(rest[int(rng.integers(len(rest)))][0]) == hc
        for k, v in (("A1", a1), ("A2", a2), ("A3", a3), ("A4", a4), ("A5", a5), ("A6", a6),
                     ("_const", f_const), ("_ceil", f_ceil)):
            acc[k].append(v / n)
    m = {k: float(np.mean(v)) for k, v in acc.items()}
    sd = {k: float(np.std(v)) for k, v in acc.items()}
    best_avail = 0.1500                      # R283, modal-of-rest, world block
    D["A1_exact_class"] = (m["A1"], m["_const"], best_avail)
    D["A2_pairwise"] = (m["A2"], 0.5, None)
    D["A3_top1"] = (m["A3"], 0.25, None)
    D["A4_bottom1"] = (m["A4"], 0.25, None)
    D["A5_kendall_tau_b"] = (m["A5"], 0.0, None)
    D["A6_modal_agreement"] = (m["A6"], m["_const"], 1.0)
    # A7 unacceptable F1
    if unacc:
        tp = fp = fn = 0
        for p in pids:
            gold = set(collections.Counter(unacc.get(p, [])).keys())
            pred = {L[int(np.argmin(core_y[p]))]} if gold else set()
            tp += len(gold & pred); fp += len(pred - gold); fn += len(gold - pred)
        f1 = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else float("nan")
        D["A7_unacceptable_f1"] = (f1, 0.25, None)
    else:
        D["A7_unacceptable_f1"] = ("UNCOMPUTED", None, None)

    # ---- B · SUFFICIENCY vs coval_full
    if full_sat:
        fp_ = [p for p in pids if p in full_sat]
        full_y = {p: yvec(full_sat[p], sorted({i for i, _ in full_sat[p]})) for p in fp_}
        # seeds: the B family was first computed at ONE held-out draw while A used three.
        # A retention ratio off a single draw is a bracket-read, not an estimate.
        cfs, ffs = [], []
        for s in SEEDS:
            rng = np.random.default_rng(s)
            cf = ff = 0
            for p in fp_:
                (hy, _d), _r = held(p, rng)
                hc = cls(hy)
                cf += core_cls[p] == hc
                ff += cls(full_y[p]) == hc
            cfs.append(cf / len(fp_)); ffs.append(ff / len(fp_))
        cf, ff = float(np.mean(cfs)), float(np.mean(ffs))
        D["B1_retention_sd_over_seeds"] = (float(np.std([a / b for a, b in zip(cfs, ffs)])),
                                           0.0, None)
        D["B1_retention_vs_full"] = (cf / ff if ff else float("nan"), 0.0, 1.0)
        D["B2_incremental_of_discarded"] = (ff - cf, 0.0, None)
        agree = np.mean([core_cls[p] == cls(full_y[p]) for p in fp_])
        D["B3_class_agreement_with_full"] = (float(agree), 1 / 75, 1.0)
        D["B4_score_vector_corr"] = (float(np.mean(
            [np.corrcoef(core_y[p], full_y[p])[0, 1] for p in fp_
             if np.std(core_y[p]) > 0 and np.std(full_y[p]) > 0])), 0.0, 1.0)
    else:
        for k in ("B1_retention_vs_full", "B2_incremental_of_discarded",
                  "B3_class_agreement_with_full", "B4_score_vector_corr"):
            D[k] = ("UNCOMPUTED", None, None)

    # ---- C · NON-DEGENERACY
    cc = collections.Counter(core_cls.values())
    p_ = np.array(list(cc.values()), float); p_ /= p_.sum()
    H_core = float(-(p_ * np.log2(p_)).sum())
    hp = np.array(list(collections.Counter(c for p in pids for c in hum_cls[p]).values()), float)
    hp /= hp.sum()
    D["C1_emitted_class_entropy"] = (H_core, 0.0, float(-(hp * np.log2(hp)).sum()))
    D["C2_margin_over_constant"] = (m["A1"] - m["_const"], 0.0, best_avail - m["_const"])
    D["C3_self_variation"] = (1 - cc.most_common(1)[0][1] / len(pids), 0.0, 1.0)
    span = best_avail - m["_const"]
    D["C4_normalized_position"] = ((m["A1"] - m["_const"]) / span if span else "DEGENERATE",
                                   0.0, 1.0)

    # ---- D · STABILITY
    D["D1_seed_spread"] = (sd["A1"], 0.0, None)
    boots = []
    rb = np.random.default_rng(7)
    for _ in range(100):
        s_ = [pids[int(rb.integers(len(pids)))] for _ in range(len(pids))]
        boots.append(np.mean([core_cls[p] == hum_cls[p][0] for p in s_]))
    D["D2_prompt_bootstrap_sd"] = (float(np.std(boots)), 0.0, None)
    rs = []
    for frac in (0.25, 0.5, 0.75):
        rr = np.random.default_rng(3)
        rs.append(np.mean([core_cls[p] == collections.Counter(
            [hum_cls[p][i] for i in rr.choice(len(hum_cls[p]),
             max(1, int(len(hum_cls[p]) * frac)), replace=False)]).most_common(1)[0][0]
            for p in pids]))
    D["D3_rater_subsample_spread"] = (float(np.std(rs)), 0.0, None)
    tol = []
    for t in (0.0, 0.01, 0.05, 0.1):
        cc_t = {p: tuple(float(np.sign(core_y[p][i] - core_y[p][j]))
                         if abs(core_y[p][i] - core_y[p][j]) > t else 0.0 for i, j in PAIRS)
                for p in pids}
        tol.append(np.mean([cc_t[p] == hum_cls[p][0] for p in pids]))
    D["D4_tie_tolerance_spread"] = (float(np.std(tol)), 0.0, None)

    # ---- E · COST
    k = len(core_texts[pids[0]]) if pids and core_texts else float("nan")
    ks = [len(core_texts[p]) for p in pids if p in core_texts]
    D["E1_k_criteria"] = (float(np.mean(ks)) if ks else "UNCOMPUTED", 1, None)
    toks = [sum(len(c.split()) for c in core_texts[p]) for p in pids if p in core_texts]
    D["E2_total_tokens"] = (float(np.mean(toks)) if toks else "UNCOMPUTED", None, None)
    D["E3_judge_calls_per_prompt"] = (float(np.mean(ks)) * 4 if ks else "UNCOMPUTED", 4, None)
    D["E4_fidelity_per_criterion"] = ((m["A1"] - m["_const"]) / np.mean(ks) if ks
                                      else "UNCOMPUTED", 0.0, None)

    # ---- F · INSTRUMENT
    # ⚠ THE FIRST VERSION OF THIS GAUGE WAS WRONG AND FIRED AT 0.0107 ON A MUST-BE-ZERO
    # BAND. It remapped the human CLASS vector by pair index under the permutation, but a
    # class entry is a SIGN: when a permutation reverses a pair's order the sign must flip
    # too, and the index remap alone does not do that. The fix is not a better remap -- it
    # is to never remap a class at all. Permute the SCORE VECTORS and recompute both
    # classes from scratch, which is what "the labels are arbitrary" actually means.
    hum_y0 = {p: np.array(targets[p][0][0], float) for p in pids}
    base = float(np.mean([core_cls[p] == cls(hum_y0[p]) for p in pids]))
    inv = [base]
    for s in SEEDS:
        o = np.random.default_rng(100 + s).permutation(4)
        inv.append(float(np.mean([cls(core_y[p][o]) == cls(hum_y0[p][o]) for p in pids])))
    D["F1_label_order_gauge"] = (float(np.std(inv)), 0.0, 0.0)
    D["F2_bf16_spread"] = ("UNCOMPUTED", None, None)
    for kk, why in REGISTERED.items():
        D[kk] = (f"REGISTERED: {why}", None, None)

    # ---- G · SUBGROUP, over the 6 real demographic axes
    sub = {}
    rng = np.random.default_rng(0)
    for ax in DEMO_AXES:
        buckets = collections.defaultdict(lambda: [0, 0])
        for p in pids:
            for y, d in targets[p]:
                v = d.get(ax)
                if v is None:
                    continue
                buckets[v][0] += core_cls[p] == cls(y); buckets[v][1] += 1
        for v, (h, n_) in buckets.items():
            if n_ >= 100:
                sub[f"{ax}={v}"] = h / n_
    if sub:
        D["G1_worst_subgroup"] = (min(sub.values()), m["_const"], m["A1"])
        D["G2_subgroup_spread"] = (max(sub.values()) - min(sub.values()), 0.0, None)
        D["G4_share_beating_constant"] = (
            float(np.mean([v > m["_const"] for v in sub.values()])), 0.0, 1.0)
    else:
        for kk in ("G1_worst_subgroup", "G2_subgroup_spread", "G4_share_beating_constant"):
            D[kk] = ("UNCOMPUTED", None, None)
    dis = sorted(pids, key=lambda p: -len(set(hum_cls[p])))[:max(1, len(pids) // 4)]
    D["G3_high_disagreement_prompts"] = (
        float(np.mean([core_cls[p] == hum_cls[p][0] for p in dis])), m["_const"], None)

    # ---- H · TRANSFER
    D["H1_held_out_prompt"] = (m["A1"], m["_const"], None)   # released core is not fitted
    D["H2_cross_block"] = ("UNCOMPUTED", None, None)

    # ---- I · PROVENANCE
    if full_texts:
        import difflib
        sims = []
        for p in pids:
            f = full_texts.get(p, [])
            for c in core_texts.get(p, []):
                sims.append(max((difflib.SequenceMatcher(None, c, x).ratio() for x in f),
                                default=0.0))
        sims = np.array(sims)
        D["I1_traceable_ge_090"] = (float(np.mean(sims >= 0.90)), 0.0, 1.0)
        D["I2_verbatim"] = (float(np.mean(sims >= 0.999)), 0.0, 1.0)
        D["I3_novel_content"] = (float(np.mean(sims < 0.60)), 0.0, 1.0)
        D["I4_median_best_match"] = (float(np.median(sims)), 0.0, 1.0)
    else:
        for kk in ("I1_traceable_ge_090", "I2_verbatim", "I3_novel_content",
                   "I4_median_best_match"):
            D[kk] = ("UNCOMPUTED", None, None)
    D["_n_prompts"] = (len(pids), None, None)
    D["_const_baseline"] = (m["_const"], None, None)
    D["_single_annotator_agreement"] = (m["_ceil"], None, None)
    return D


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat", required=True)
    ap.add_argument("--label", default="coval_core")
    ap.add_argument("--out", default="corebench/results/leaderboard.json")
    a = ap.parse_args()

    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    core_texts = {p: [i["criterion"] for i in (r.get("coval_core") or [])]
                  for p, _pr, r in joined}
    full_texts = {p: [i["criterion"] for i in (r.get("coval_full") or [])]
                  for p, _pr, r in joined}
    sat = load_sat(a.sat)
    fs = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                 "/R04_rebuild_satisfaction/results/a04_full.npz")
    full_sat = load_sat(fs) if fs.exists() else None
    targets, unacc = load_targets()

    D = score_core(sat, core_texts, targets, unacc, full_sat, full_texts, a.label)

    print(f"\n  CoreBench row: {a.label}")
    print(f"  {'-'*74}")
    fam = None
    for k in sorted(D):
        if k.startswith("_"):
            continue
        f = k[0]
        if f != fam:
            fam = f; print()
        v, lo, hi = D[k]
        if isinstance(v, str):
            print(f"    {k:<32} {v}")
            continue
        norm = ""
        if lo is not None and hi is not None:
            norm = "DEGENERATE" if lo == hi and v != lo else (
                f"norm {(v-lo)/(hi-lo):+.3f}" if hi != lo else "band=0")
        band = f"[{lo:.4f}, {hi:.4f}]" if isinstance(lo, float) and isinstance(hi, float) else \
               (f"floor {lo}" if lo is not None else "")
        print(f"    {k:<32} {v:>10.4f}   {band:<22}{norm}")
    print(f"\n    prompts {D['_n_prompts'][0]} | constant baseline "
          f"{D['_const_baseline'][0]:.4f} | one-annotator agreement "
          f"{D['_single_annotator_agreement'][0]:.4f}\n")

    out = pathlib.Path(a.out); out.parent.mkdir(parents=True, exist_ok=True)
    board = json.loads(out.read_text()) if out.exists() else {}
    board[a.label] = {k: (v if not isinstance(v, tuple) else list(v)) for k, v in D.items()}
    out.write_text(json.dumps(board, indent=2, sort_keys=True, default=str))
    print(f"    leaderboard -> {out}\n")


if __name__ == "__main__":
    main()
