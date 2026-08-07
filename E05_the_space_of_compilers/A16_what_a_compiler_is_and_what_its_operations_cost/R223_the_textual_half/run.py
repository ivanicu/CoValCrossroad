"""R223 -- the textual half of the rewrite. Does the TEXT carry R222's gauge gain, or the algebra?

WHERE THIS COMES FROM
    R222 derived that polarity normalisation is decision-null as an ARITHMETIC operation:
    (w,s) -> (-w, 1-s) contributes -w + w*s, the original term plus a response-independent
    constant, so no argmax, pair or ranking moves. Measured identical to six decimals. Yet the same
    operation carried +0.0343 of gauge stability -- an order more than anything else in the
    lattice. Both cannot be about the same thing. The arithmetic cannot change instrument
    dependence, because it never touches the judge: it re-labels a number AFTER the judge has
    spoken.
        => the gauge gain, if real, belongs to the TEXT. R222 could not see that, because it
           implemented the arithmetic and called it the operation.

WHY THIS NEEDS NO GPU
    I was about to queue a judge pass over generated rewrites. The rewrites already exist and are
    already judged: `coval_core` IS the official positive-form rewrite, human-reviewed, and r164
    scored it under all five instruments. Generating my own would have made the rewrite MY
    instrument and answered a question about my prompt rather than about OpenAI's compiler.

THE ARITHMETIC PREDICTION, STATED BEFORE MEASURING
    If the rewrite were only the algebra, the judge would score the rewritten text at exactly
    s' = 1 - s. Every departure from that line is what the TEXT does that the algebra does not.

LINEAGE IS INFERRED, AND THAT IS THE CENTRAL LIMITATION
    The release ships no source_criterion_id. Pairs are matched by content-word Jaccard (R219:
    matched median 0.444 against 0.050 shuffled). Every number below is therefore reported over
    lineage-confidence strata AND against a shuffled-lineage null.
"""
from __future__ import annotations

import json, pathlib, re, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R164 = ROOT / "E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_the_standard/R164_instrument/results"
L = "ABCD"
SEEDS = [0, 1, 2, 3, 4]

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r220)

STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if so "
           "when about into over than then there their they them we you your our its his her do does "
           "did can could should would will shall may might have has had been being any all each "
           "other more most less least such very".split())


def toks(s):
    return set(w for w in re.findall(r"[a-z']+", str(s).lower()) if w not in STOP and len(w) > 2)


def jac(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FULL = {"base": r220.load_sat(R4 / "a04_full.npz"),
            "phi": r220.load_sat(R164 / "sat_full_phi.npz"),
            "qwen3b": r220.load_sat(R164 / "sat_full_qwen3b.npz"),
            "swapped": r220.load_sat(R164 / "sat_full_variant_swapped.npz"),
            "no_fewshot": r220.load_sat(R164 / "sat_full_variant_no_fewshot.npz")}
    CORE = {"base": r220.load_sat(R4 / "a04_core.npz"),
            "phi": r220.load_sat(R164 / "sat_core_phi.npz"),
            "qwen3b": r220.load_sat(R164 / "sat_core_qwen3b.npz"),
            "swapped": r220.load_sat(R164 / "sat_core_variant_swapped.npz"),
            "no_fewshot": r220.load_sat(R164 / "sat_core_variant_no_fewshot.npz")}
    INS = list(FULL)
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}

    rows = []          # one per inferred (full -> core) pair
    rng = np.random.default_rng(0)
    pool = []          # for the shuffled-lineage null: every full criterion's vectors
    for p in sorted(FULL["base"]):
        if p not in recs:
            continue
        f, cr = recs[p]["coval_full"], recs[p]["coval_core"]
        okf = [i for i, it in enumerate(f)
               if it.get("scores") and all(FULL[j][p].get((i, x)) is not None
                                           for j in INS for x in L)]
        okc = [j for j in range(len(cr))
               if all((CORE[j2].get(p) or {}).get((j, x)) is not None
                      for j2 in INS for x in L)]
        if not okf or not okc:
            continue
        Tf = {i: toks(f[i].get("criterion", "")) for i in okf}
        Wf = {i: float(np.mean([float(s["score"]) for s in f[i]["scores"]])) for i in okf}
        Sf = {i: {j: np.array([FULL[j][p][(i, x)] for x in L]) for j in INS} for i in okf}
        for j in okc:
            tc = toks(cr[j].get("criterion", ""))
            best_i, best_j = None, -1.0
            for i in okf:
                v = jac(tc, Tf[i])
                if v > best_j:
                    best_i, best_j = i, v
            if best_i is None:
                continue
            sc = {k: np.array([CORE[k][p][(j, x)] for x in L]) for k in INS}
            sf = Sf[best_i]
            verbatim = (str(cr[j].get("criterion", "")).lower().strip(" .")
                        == str(f[best_i].get("criterion", "")).lower().strip(" ."))
            rows.append({"pid": p, "jac": best_j, "w": Wf[best_i], "verbatim": verbatim,
                         "sf": {k: sf[k].tolist() for k in INS},
                         "sc": {k: sc[k].tolist() for k in INS}})
            pool.append({k: sf[k].tolist() for k in INS})

    def gauge(d):
        """instrument spread of one criterion: mean over responses of (max-min) across judges."""
        a = np.array([d[k] for k in INS])          # 5 x 4
        return float(np.mean(a.max(0) - a.min(0)))

    def arith_err(sf, sc):
        """distance from the arithmetic prediction s' = 1 - s, on the build judge."""
        return float(np.mean(np.abs(np.array(sc["base"]) - (1 - np.array(sf["base"])))))

    def ident_err(sf, sc):
        """distance from 'the text did nothing': s' = s."""
        return float(np.mean(np.abs(np.array(sc["base"]) - np.array(sf["base"]))))

    neg = [r for r in rows if r["w"] < 0]
    pos = [r for r in rows if r["w"] >= 0]
    vb = [r for r in rows if r["verbatim"]]
    hi = [r for r in neg if r["jac"] >= 0.5]

    def block(name, rs):
        if not rs:
            print("%-26s (empty)" % name); return None
        gf = float(np.mean([gauge(r["sf"]) for r in rs]))
        gc = float(np.mean([gauge(r["sc"]) for r in rs]))
        ae = float(np.mean([arith_err(r["sf"], r["sc"]) for r in rs]))
        ie = float(np.mean([ident_err(r["sf"], r["sc"]) for r in rs]))
        print("%-26s n=%5d   gauge_full %.4f  gauge_core %.4f  Δ %+.4f   "
              "|s'-(1-s)| %.4f   |s'-s| %.4f" % (name, len(rs), gf, gc, gc - gf, ae, ie))
        return {"n": len(rs), "gauge_full": gf, "gauge_core": gc, "delta": gc - gf,
                "err_vs_arithmetic": ae, "err_vs_identity": ie}

    print("inferred (full -> core) pairs: %d   |   negative-source %d   positive-source %d   "
          "verbatim %d" % (len(rows), len(neg), len(pos), len(vb)))
    print("\n=== instrument spread, and distance from the two predictions ===")
    res = {"all": block("ALL pairs", rows),
           "negative_source": block("NEGATIVE source (flip)", neg),
           "negative_hi_lineage": block("  ...lineage Jaccard>=0.5", hi),
           "positive_source": block("POSITIVE source (sham)", pos),
           "verbatim": block("VERBATIM (pos. control)", vb)}

    # ---------------------------------------------------------------- shuffled-lineage null
    nulls = []
    for s in SEEDS:
        r2 = np.random.default_rng(s)
        idx = r2.permutation(len(rows))
        gd, ae = [], []
        for a, b in zip(rows, idx):
            gd.append(gauge(rows[int(b)]["sc"]) - gauge(a["sf"]))
            ae.append(arith_err(a["sf"], rows[int(b)]["sc"]))
        nulls.append((float(np.mean(gd)), float(np.mean(ae))))
    print("\n=== shuffled-lineage null, %d seeds ===" % len(SEEDS))
    print("  Δgauge  %s   mean %+.4f" % (" ".join("%+.4f" % g for g, _ in nulls),
                                         np.mean([g for g, _ in nulls])))
    print("  |s'-(1-s)|  %s   mean %.4f" % (" ".join("%.4f" % a for _, a in nulls),
                                            np.mean([a for _, a in nulls])))
    res["shuffled_null"] = {"delta_gauge_mean": float(np.mean([g for g, _ in nulls])),
                            "arith_err_mean": float(np.mean([a for _, a in nulls])),
                            "seeds": SEEDS}

    # ---------------------------------------------------------------- the kill
    print("\n" + "=" * 78)
    print("PRE-REGISTERED KILL -- a conditional, not a threshold")
    print("=" * 78)
    v = res["verbatim"]; n_ = res["negative_source"]; nl = res["shuffled_null"]
    pos_ok = v is not None and abs(v["delta"]) < abs(n_["delta"])
    neg_ok = abs(nl["delta_gauge_mean"]) < abs(n_["delta"])
    print("positive control  VERBATIM pairs Δgauge %+.4f  (same text, so must be ~0 and smaller\n"
          "                  than the flipped pairs' %+.4f)   -> %s"
          % (v["delta"], n_["delta"], "OK" if pos_ok else "FAILS"))
    print("negative control  shuffled lineage Δgauge %+.4f   -> %s"
          % (nl["delta_gauge_mean"], "null" if neg_ok else "NOT NULL"))
    if pos_ok and neg_ok:
        if n_["delta"] < 0:
            verdict = ("The TEXT carries the gauge gain: rewriting a negative criterion into "
                       "positive form lowers its instrument spread by %.4f, and the arithmetic "
                       "cannot do that because it never reaches the judge." % -n_["delta"])
        else:
            verdict = ("REFUTED: the rewritten text is MORE instrument-dependent (%+.4f), so "
                       "R222's +0.0343 gauge gain is not the text." % n_["delta"])
        print("\n  " + verdict)
        print("  and the rewrite is not the algebra either: |s'-(1-s)| = %.4f against "
              "|s'-s| = %.4f" % (n_["err_vs_arithmetic"], n_["err_vs_identity"]))
    else:
        verdict = "UNVERIFIED -- the controls did not behave, so no verdict is admissible"
        print("\n  " + verdict)
    # ---------------------------------------------------------------- where DOES it come from
    # Eliminated: not the algebra (it never reaches the judge) and not the rewritten text's own
    # instrument spread (just measured, wrong sign). The remaining candidate is the INTERACTION
    # R222 predicted: polarity normalisation reorders the "highest-rated" list, so a DIFFERENT
    # four criteria survive the cut, and that set may be the stable one. Measured directly.
    sel_plain, sel_flip = [], []
    for p_ in sorted(FULL["base"]):
        if p_ not in recs:
            continue
        f = recs[p_]["coval_full"]
        okf = [i for i, it in enumerate(f)
               if it.get("scores") and all(FULL[j][p_].get((i, x)) is not None
                                           for j in INS for x in L)]
        if len(okf) < 4:
            continue
        W = np.array([np.mean([float(s2["score"]) for s2 in f[i]["scores"]]) for i in okf])
        G = np.array([gauge({k: [FULL[k][p_][(i, x)] for x in L] for k in INS}) for i in okf])
        sel_plain.append(float(G[np.argsort(-W)[:4]].mean()))
        sel_flip.append(float(G[np.argsort(-np.abs(W))[:4]].mean()))
    print("\n=== so where does R222's +0.0343 come from? the SELECTION it reorders ===")
    print("  top-4 by rating, polarity NOT normalised : mean gauge of the kept set %.4f"
          % np.mean(sel_plain))
    print("  top-4 by |rating|, i.e. after normalising: mean gauge of the kept set %.4f"
          % np.mean(sel_flip))
    print("  difference %+.4f   (n=%d prompts)" % (np.mean(sel_flip) - np.mean(sel_plain),
                                                   len(sel_plain)))
    res["selection_reordering"] = {"gauge_top4_by_rating": float(np.mean(sel_plain)),
                                   "gauge_top4_by_abs_rating": float(np.mean(sel_flip)),
                                   "delta": float(np.mean(sel_flip) - np.mean(sel_plain)),
                                   "n_prompts": len(sel_plain)}
    res["verdict"] = verdict
    (OUT / "textual_half.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
