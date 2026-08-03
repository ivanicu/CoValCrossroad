"""R222 -- the compiler factorial. What does each operation in Full -> Core actually cost?

THE QUESTION
    The official compiler is documented as: rewrite negative-weight criteria into positive form ·
    merge semantic duplicates · select at most four highly-rated, compatible, non-redundant
    criteria · drop the weights. Those are FOUR operations reported as one number, and no round in
    this project has ever separated them. This runs all 2^5 = 32 on/off combinations and
    Shapley-attributes every axis to every operation.

A DERIVATION, FOUND WHILE BUILDING IT, THAT CHANGES WHAT THE FACTORIAL MEANS
    Polarity normalisation replaces (w, s) by (-w, 1-s) for w < 0. Its contribution to a response
    is  -w(1-s) = -w + w*s : the ORIGINAL term plus a constant that does not depend on the
    response. A constant shifts every response equally, so every argmax, every pairwise relation
    and every ranking is UNCHANGED. Exactly, not approximately.
        => the representational content of "rewrite negatives into positives" is decision-NULL.
    Anything the rewrite costs must therefore come from the TEXT, which needs a judge pass and is
    NOT IDENTIFIED here. But the operation is not inert in combination: selection keeps the
    highest-RATED criteria, and flipping a -8 to a +8 moves it from the bottom of that ordering to
    the top. So R alone is null and R x S is not, which is precisely what a factorial is for and
    what reporting "compilation costs X" can never show.

CARRIED FORWARD FROM R221 -- a constraint on what this round may claim
    R221 measured that on 100% of prompts SOME single criterion alone reproduces the whole
    4-response ranking, with a median of 3 tied at that score. So any axis defined as agreement
    with FULL's own decision is degenerate and cannot rank compilers. Those axes are computed and
    printed, and marked DEGENERATE. The axes that carry weight here are the ones scored against
    HUMANS, against INTERVENTION, and against the INSTRUMENT.
"""
from __future__ import annotations

import json, math, pathlib, sys, itertools, collections, re
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R164 = ROOT / "E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_the_standard/R164_instrument/results"
L = "ABCD"
K_KEEP = 4
MERGE_J = 0.5

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r220)

OPS = ["R_polarity", "M_merge", "S_select", "T_truncate", "W_dropweights"]


def toks(s):
    return set(w for w in re.findall(r"[a-z']+", str(s).lower()) if len(w) > 3)


def apply_ops(W, S, T, ops):
    """Canonical order: polarity -> merge -> select -> truncate -> drop weights.
    Order INSIDE an applied subset is fixed; Shapley attributes across subsets, not orders, and
    that limitation is stated rather than hidden -- a different canonical order is a different
    compiler and would need its own run."""
    W, S, T = W.copy(), S.copy(), list(T)
    src = [[i] for i in range(len(W))]            # provenance: which原 criteria each rule carries
    if "R_polarity" in ops:
        neg = W < 0
        S[neg] = 1.0 - S[neg]
        W[neg] = -W[neg]
    if "M_merge" in ops:
        tk = [toks(t) for t in T]
        used, groups = set(), []
        for i in range(len(W)):
            if i in used:
                continue
            g = [i]; used.add(i)
            for j in range(i + 1, len(W)):
                if j in used:
                    continue
                u = tk[i] | tk[j]
                if u and len(tk[i] & tk[j]) / len(u) >= MERGE_J:
                    g.append(j); used.add(j)
            groups.append(g)
        W = np.array([W[g].mean() for g in groups])
        S = np.array([S[g].mean(0) for g in groups])
        T = [T[g[0]] for g in groups]
        src = [[x for i in g for x in src[i]] for g in groups]
    if "S_select" in ops:
        idx = list(np.argsort(-W)[:max(K_KEEP, 1)]) if len(W) > K_KEEP else list(range(len(W)))
    else:
        idx = list(range(len(W)))
    if "T_truncate" in ops:
        idx = idx[:K_KEEP]
    W, S, T, src = W[idx], S[idx], [T[i] for i in idx], [src[i] for i in idx]
    if "W_dropweights" in ops:
        W = np.sign(W)
        W[W == 0] = 1.0
    return W, S, T, src


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    INSTR = {"base": r220.load_sat(R4 / "a04_full.npz"),
             "phi": r220.load_sat(R164 / "sat_full_phi.npz"),
             "qwen3b": r220.load_sat(R164 / "sat_full_qwen3b.npz"),
             "swapped": r220.load_sat(R164 / "sat_full_variant_swapped.npz"),
             "no_fewshot": r220.load_sat(R164 / "sat_full_variant_no_fewshot.npz")}
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = collections.defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    COALS = [frozenset(c) for k in range(len(OPS) + 1) for c in itertools.combinations(OPS, k)]
    hits = {c: {i: [0, 0] for i in INSTR} for c in COALS}      # rank agreement vs humans
    pres = {c: [0, 0] for c in COALS}                          # pairwise preservation vs Full
    trans = {c: collections.Counter() for c in COALS}          # transport
    kc = {c: [] for c in COALS}                                # rules a human must read
    prov = {c: [] for c in COALS}                              # share of rules with ONE source
    n_used = 0
    base_sf = INSTR["base"]

    for p in sorted(base_sf):
        if p not in recs or p not in ann:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(base_sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < K_KEEP:
            continue
        T0 = [str(f[i].get("criterion", "")) for i in ok]
        W0 = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok], float)
        rank_rows = []
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                pts = r220.parse_rank(e.get("ranking"))
                if pts is not None:
                    rank_rows.append(pts)
        if not rank_rows:
            continue
        n_used += 1

        for c in COALS:
            for ins, sf in INSTR.items():
                if p not in sf:
                    continue
                S0 = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
                W, S, T, src = apply_ops(W0, S0, T0, c)
                if not len(W):
                    continue
                y = (W[:, None] * S).sum(0)
                for pts in rank_rows:
                    for i_, j_ in r220.kendall_pairs(pts):
                        hits[c][ins][0] += int(y[i_] > y[j_]); hits[c][ins][1] += 1
                if ins == "base":
                    yf = (W0[:, None] * S0).sum(0)
                    for i_ in range(4):
                        for j_ in range(i_ + 1, 4):
                            pres[c][0] += int(np.sign(y[i_] - y[j_]) == np.sign(yf[i_] - yf[j_]))
                            pres[c][1] += 1
                    kc[c].append(len(W))
                    prov[c].append(float(np.mean([len(s_) == 1 for s_ in src])))
            # transport, on the build instrument only
            S0 = np.array([[base_sf[p][(i, x)] for x in L] for i in ok], float)
            yf0 = (W0[:, None] * S0).sum(0)
            W, S, _T, _s = apply_ops(W0, S0, T0, c)
            y0 = (W[:, None] * S).sum(0) if len(W) else None
            for d in range(len(ok)):
                keep = [i for i in range(len(ok)) if i != d]
                yfd = (W0[keep, None] * S0[keep]).sum(0)
                dfull = np.sign((yf0[0] - yf0[1]) - (yfd[0] - yfd[1]))
                Wd, Sd, _t, _s2 = apply_ops(W0[keep], S0[keep], [T0[i] for i in keep], c)
                if y0 is None or not len(Wd):
                    trans[c]["NOT_IDENTIFIED"] += 1; continue
                y1 = (Wd[:, None] * Sd).sum(0)
                darm = np.sign((y0[0] - y0[1]) - (y1[0] - y1[1]))
                if dfull == 0:
                    trans[c]["NOT_IDENTIFIED"] += 1
                elif darm == 0:
                    trans[c]["lost"] += 1
                elif darm == dfull:
                    trans[c]["same"] += 1
                else:
                    trans[c]["inverted"] += 1

    # ------------------------------------------------------------------ axes
    def acc(d):
        return d[0] / d[1] if d[1] else float("nan")

    def axis(c, name):
        if name == "human_agreement":
            return acc(hits[c]["base"])
        if name == "gauge_stability":
            v = [acc(hits[c][i]) for i in INSTR if hits[c][i][1]]
            return -(max(v) - min(v)) if v else float("nan")
        if name == "not_inverted":
            t = trans[c]; ident = t["same"] + t["inverted"] + t["lost"]
            return 1 - t["inverted"] / ident if ident else float("nan")
        if name == "pairwise_preservation_vs_Full":
            return acc(pres[c])
        if name == "provenance":
            return float(np.mean(prov[c])) if prov[c] else float("nan")
        if name == "brevity":
            return -float(np.median(kc[c])) if kc[c] else float("nan")
        raise ValueError(name)

    AXES = ["human_agreement", "not_inverted", "gauge_stability",
            "pairwise_preservation_vs_Full", "provenance", "brevity"]
    DEGENERATE = {"pairwise_preservation_vs_Full"}

    # ------------------------------------------------------------------ exact Shapley
    n = len(OPS)
    fact = [math.factorial(i) for i in range(n + 1)]
    shap = {a: {o: 0.0 for o in OPS} for a in AXES}
    for a in AXES:
        for o in OPS:
            rest = [x for x in OPS if x != o]
            for k in range(len(rest) + 1):
                for sub in itertools.combinations(rest, k):
                    Sset = frozenset(sub)
                    w = fact[k] * fact[n - k - 1] / fact[n]
                    v1, v0 = axis(Sset | {o}, a), axis(Sset, a)
                    if not (math.isnan(v1) or math.isnan(v0)):
                        shap[a][o] += w * (v1 - v0)

    res = {"prompts": n_used, "ops": OPS, "axes": AXES, "degenerate_axes": sorted(DEGENERATE),
           "arms": {"+".join(sorted(c)) or "NONE(=Full)": {a: axis(c, a) for a in AXES}
                    for c in COALS},
           "shapley": shap}
    (OUT / "factorial.json").write_text(json.dumps(res, indent=2))

    print("prompts %d   |   2^%d = %d arms   |   exact Shapley over all coalitions"
          % (n_used, len(OPS), len(COALS)))
    print("\n=== the corner arms ===")
    print("%-34s %s" % ("arm", "".join("%16s" % a[:15] for a in AXES)))
    for c in [frozenset(), frozenset(OPS),
              frozenset(["S_select", "T_truncate"]),
              frozenset(["R_polarity"]),
              frozenset(["R_polarity", "S_select", "T_truncate"]),
              frozenset(["W_dropweights"])]:
        nm = "+".join(sorted(x[0] for x in c)) or "NONE (= Full)"
        print("%-34s %s" % (nm, "".join("%16.4f" % axis(c, a) for a in AXES)))

    print("\n=== is R_polarity decision-null, as derived? ===")
    for c in [frozenset(), frozenset(["R_polarity"])]:
        print("   %-16s human_agreement %.6f   pairwise_vs_Full %.6f"
              % ("+".join(sorted(c)) or "Full", axis(c, "human_agreement"),
                 axis(c, "pairwise_preservation_vs_Full")))
    print("   -> identical means the derivation holds on the data as well as on paper")

    print("\n=== SHAPLEY: what each operation contributes to each axis ===")
    print("   (positive = the operation IMPROVES that axis, averaged over every coalition)")
    print("%-16s %s" % ("operation", "".join("%16s" % a[:15] for a in AXES)))
    for o in OPS:
        print("%-16s %s" % (o, "".join("%+16.4f" % shap[a][o] for a in AXES)))
    print("%-16s %s" % ("[DEGENERATE]", "".join("%16s" % ("<-- R221" if a in DEGENERATE else "")
                                                for a in AXES)))

    print("\n=== the interaction the derivation predicts: R alone vs R with S ===")
    for base in [frozenset(), frozenset(["S_select", "T_truncate"])]:
        b = "+".join(sorted(x[0] for x in base)) or "Full"
        d = axis(base | {"R_polarity"}, "human_agreement") - axis(base, "human_agreement")
        print("   on top of %-14s  R_polarity moves human agreement by %+.4f" % (b, d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
