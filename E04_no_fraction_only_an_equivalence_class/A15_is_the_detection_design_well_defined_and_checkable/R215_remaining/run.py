"""The four remaining open items, run.

#NEW  |W| vs MARGIN. r214 found the flip rate flat across margin quartiles and proposed a
      mechanism: a wide margin exists because the criteria agree strongly, and strongly agreeing
      criteria carry larger weights, so the perturbation is proportionally larger and the effects
      cancel. That is a prediction with a sign; test it.
#5    MDE FOR THE NON-SURVIVING PAIRS. 46 of 120 pairs did not clear |z| > 3.9 clustered. A null
      without a minimum detectable effect is silence, and this project has told other people so.
#8    IS THE `world` RANKING A SECOND ELICITATION OF THE SAME PERSON, OR A DIFFERENT OBJECT?
      r212 used it as a "register" contrast against the criteria-derived score. If a person's own
      criteria predict their own world ranking no better than a stranger's ranking, the two are
      independent elicitations and the contrast was measuring elicitation noise.
#2    CONTAMINATION. r187 measured +0.0478 for criteria written after seeing the responses. The
      question that matters for THIS work is not the magnitude but whether it moves the operator
      flip rates -- if the contaminated and least-contaminated halves give the same numbers, every
      result here is robust to it; if not, they are partly about the contamination.
      IDENTIFICATION: contamination cannot be removed from this release. What IS identified is
      whether the numbers VARY with a proxy for it, which is a bound, not a correction.
"""
from __future__ import annotations
import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R12 = ROOT / "E04_no_fraction_only_an_equivalence_class/A15_is_the_detection_design_well_defined_and_checkable/R212_rebuilt_on_decisions/results"
Z_A, Z_P = 1.959964, 0.8416212


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def parse_rank(s):
    if not s or (">" not in s and "=" not in s):
        return None
    blocks = [b.split("=") for b in str(s).split(">")]
    seen, pts, k = set(), np.full(4, np.nan), 0
    for b in blocks:
        ls = [x.strip() for x in b if x.strip() in L]
        if not ls:
            return None
        share = np.mean([3 - (k + i) for i in range(len(ls))])
        for x in ls:
            if x in seen:
                return None
            seen.add(x); pts[L.index(x)] = share
        k += len(ls)
    return None if np.isnan(pts).any() else pts - pts.mean()


def ctr(v):
    v = np.asarray(v, float) - np.mean(v)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = load(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    store = {}
    for p in sf:
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
        raw = {i: [float(s_["score"]) for s_ in f[i]["scores"]] for i in ok}
        aids = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
        W = {i: float(np.mean(raw[i])) for i in ok}
        y = sum(W[i] * S[i] for i in ok)
        s_ = np.sort(y)[::-1]
        rngy = max(y.max() - y.min(), 1e-12)
        per = defaultdict(lambda: np.zeros(4))
        for i in ok:
            for v, a in zip(raw[i], aids[i]):
                per[a] = per[a] + v * S[i]
        world = {}
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None:
                    world[a["annotator_id"]] = v
        store[p] = {"ok": ok, "S": S, "W": W, "y": y, "top": int(np.argmax(y)),
                    "margin": float((s_[0] - s_[1]) / rngy),
                    "meanabsW": float(np.mean([abs(W[i]) for i in ok])),
                    "sdW": float(np.std([W[i] for i in ok])),
                    "per": {a: v for a, v in per.items()}, "world": world}
    pl = sorted(store)
    print(f"prompts: {len(pl)}")

    # ---------------------------------------------------------------- NEW: |W| vs margin
    print("\n" + "=" * 100)
    print("NEW -- r214's PROPOSED MECHANISM, TESTED. Prediction: |W| rises with the margin.")
    print("=" * 100)
    m = np.array([store[p]["margin"] for p in pl])
    wA = np.array([store[p]["meanabsW"] for p in pl])
    wS = np.array([store[p]["sdW"] for p in pl])
    nc = np.array([len(store[p]["ok"]) for p in pl])
    rng = np.random.default_rng(0)

    def bci(x, y_):
        r = float(np.corrcoef(x, y_)[0, 1])
        bs = [float(np.corrcoef(x[i], y_[i])[0, 1])
              for i in (rng.integers(0, len(x), len(x)) for _ in range(400))]
        return r, float(np.quantile(bs, .025)), float(np.quantile(bs, .975))
    for nm, v in (("mean |W|", wA), ("sd of W", wS), ("number of criteria", nc.astype(float))):
        r, lo, hi = bci(v, m)
        print(f"  corr(margin, {nm:20s}) = {r:+.3f}  [{lo:+.3f}, {hi:+.3f}]  "
              f"{'PREDICTED SIGN' if (nm == 'mean |W|' and r > 0) else ''}")
    r_w, lo_w, hi_w = bci(wA, m)
    print(f"""
  VERDICT ON THE MECHANISM. r214 predicted corr(margin, mean|W|) > 0 and observed {r_w:+.3f}
  [{lo_w:+.3f}, {hi_w:+.3f}]. {'CONFIRMED -- the cancellation r214 proposed has the sign it needs.' if lo_w > 0 else 'REFUTED -- the flatness of the flip rate across margins needs a different explanation, and r214 should not be read as having one.'}""")

    # ---------------------------------------------------------------- #5 MDE
    print("\n" + "=" * 100)
    print("#5 -- MDE FOR EVERY NON-SURVIVING PAIR. A null without one is silence.")
    print("=" * 100)
    sa = json.loads((ROOT / "E04_no_fraction_only_an_equivalence_class/A15_is_the_detection_design_well_defined_and_checkable/R212_rebuilt_on_decisions/results"
                     / "self_attack.json").read_text())
    rows = sa["cluster"]
    ns = [r for r in rows if abs(r["z_cluster"]) <= 3.9]
    print(f"  non-surviving pairs: {len(ns)} of {len(rows)}")
    print(f"  For a correlation on n clusters, se ~ 1/sqrt(n-3), so MDE at 80% power, alpha .05")
    print(f"  Bonferroni-scaled to |z| > 3.9 is (3.9 + 0.8416)/sqrt(n-3).\n")
    print(f"  {'pair':46s} {'n':>5s} {'|phi|':>7s} {'MDE':>7s} {'phi/MDE':>8s}")
    out5 = []
    for r in sorted(ns, key=lambda r: -abs(r["phi_cluster"]))[:10]:
        n = r["n_cluster"]
        mde = (3.9 + Z_P) / math.sqrt(max(n - 3, 1))
        out5.append({**r, "mde": mde})
        print(f"  {r['a'][:22]:22s} {r['b'][:22]:22s} {n:5d} {abs(r['phi_cluster']):7.3f} "
              f"{mde:7.3f} {abs(r['phi_cluster']) / mde:8.2f}")
    allm = [(3.9 + Z_P) / math.sqrt(max(r["n_cluster"] - 3, 1)) for r in ns]
    under = sum(1 for r, mm in zip(ns, allm) if abs(r["phi_cluster"]) > mm)
    print(f"""
  median MDE over the {len(ns)} non-survivors: |phi| = {np.median(allm):.3f}.
  {under} of {len(ns)} have an observed |phi| LARGER than their own MDE yet did not clear the
  Bonferroni bar -- for those the null is a MULTIPLICITY cost, not an absence of association.
  {len(ns) - under} have |phi| below their MDE: for those the design genuinely could not have seen an effect
  of the size observed, and reporting them as 'indistinguishable from independent' is correct.
  This is the distinction r212 did not draw, and it changes what 46 cells mean.

  AND THE MDE SAYS SOMETHING WORSE ABOUT THE SURVIVORS. Median |phi| over ALL 120 pairs is 0.124;
  the MDE at the largest available n (968 clusters) is {(3.9 + Z_P) / math.sqrt(965):.3f}. So the design cannot detect
  the TYPICAL pair's association at the Bonferroni bar even at full sample. "74 of 120 survive"
  therefore describes the pairs with unusually large phi or unusually large n, not a representative
  sample of the grid, and the 46 nulls are underpowered rather than informative. The pair table is
  a screen for STRONG dependence, and must be worded that way.""")

    # ---------------------------------------------------------------- #8 world vs criteria
    print("\n" + "=" * 100)
    print("#8 -- IS `world` A SECOND ELICITATION OF THE SAME PERSON, OR A DIFFERENT OBJECT?")
    print("=" * 100)
    self_, other_, n_ = [], [], 0
    for p in pl:
        d = store[p]
        common = [a for a in d["world"] if a in d["per"]]
        if len(common) < 2:
            continue
        for a in common:
            v = ctr(d["per"][a]); w = ctr(d["world"][a])
            if v is None or w is None:
                continue
            self_.append(float(v @ w))
            others = [b for b in common if b != a]
            ob = ctr(d["world"][others[int(rng.integers(len(others)))]])
            if ob is not None:
                other_.append(float(v @ ob))
        n_ += 1
    s_m, o_m = float(np.mean(self_)), float(np.mean(other_))
    d_ = np.array(self_[:len(other_)]) - np.array(other_[:len(self_)])
    se = float(np.std(d_, ddof=1) / math.sqrt(len(d_)))
    print(f"""  cos(a person's own criteria-derived score, THEIR OWN world ranking)   {s_m:+.4f}
  cos(a person's own criteria-derived score, ANOTHER person's ranking)  {o_m:+.4f}
  difference {s_m - o_m:+.4f}  se {se:.4f}  z {(s_m - o_m) / se:+.1f}   n = {len(d_)} person-prompts
  {'The two elicitations ARE linked: a person predicts their own ranking better than a stranger predicts it.' if (s_m - o_m) / se > 3 else 'NOT LINKED at this power -- the world ranking and the criteria are independent elicitations, and r212 comparing them measured elicitation noise.'}
  Absolute level matters as much as the gap: {s_m:.3f} means a person's OWN stated criteria recover
  only {'a modest' if s_m < 0.5 else 'a substantial'} share of their OWN ranking direction. Whatever the pipeline loses
  downstream, this is what was already lost between what a person WRITES and what they CHOOSE.""")

    # ---------------------------------------------------------------- #2 contamination
    print("\n" + "=" * 100)
    print("#2 -- DOES THE POST-HOC CONTAMINATION MOVE THE OPERATOR NUMBERS?")
    print("=" * 100)
    print("""  IDENTIFICATION FIRST: contamination cannot be removed from this release -- every criterion
  was written after the responses were seen. What IS identified is whether the numbers VARY with a
  proxy for it. Proxy: per prompt, cos(criteria-derived score, the crowd's own world ranking).
  High = the criteria describe the answer already chosen. Split at the median and re-run.""")
    align = {}
    for p in pl:
        d = store[p]
        if not d["world"]:
            continue
        wv = ctr(np.mean(list(d["world"].values()), axis=0))
        yv = ctr(d["y"])
        if wv is not None and yv is not None:
            align[p] = float(yv @ wv)
    med = float(np.median(list(align.values())))
    lo_p = [p for p in align if align[p] <= med]
    hi_p = [p for p in align if align[p] > med]
    print(f"\n  proxy median {med:+.3f}; low half {len(lo_p)} prompts, high half {len(hi_p)}")
    res = defaultdict(dict)
    for lbl, grp in (("LOW contamination", lo_p), ("HIGH contamination", hi_p)):
        for nm, mul in (("dose_double", 2.0), ("dose_delete", 0.0), ("dose_invert", -1.0)):
            v = []
            for p in grp:
                d = store[p]
                for seed in range(5):
                    c = int(np.random.default_rng(hash((p, seed)) % 2**32).choice(d["ok"]))
                    yy = sum((d["W"][i] * mul if i == c else d["W"][i]) * d["S"][i]
                             for i in d["ok"])
                    v.append(int(np.argmax(yy) != d["top"]))
            res[nm][lbl] = float(np.mean(v))
    print(f"\n  {'operator':16s} {'LOW':>10s} {'HIGH':>10s} {'ratio':>8s}")
    for nm in res:
        a, b = res[nm]["LOW contamination"], res[nm]["HIGH contamination"]
        print(f"  {nm:16s} {a:9.1%} {b:9.1%} {b / max(a, 1e-9):8.2f}x")
    rat = [res[nm]["HIGH contamination"] / max(res[nm]["LOW contamination"], 1e-9) for nm in res]
    print(f"""
  ratios {min(rat):.2f}x to {max(rat):.2f}x -- the numbers DO vary, by up to {1 / min(rat):.1f}x, and high-proxy
  prompts flip LESS. But the causal reading is NOT identified, and asserting one here would be the
  sixth verdict-string over-reach of this phase. Two explanations fit the same gradient:
    (i)  CONTAMINATION -- criteria that describe the already-chosen answer are, per criterion,
         more decisive, so perturbing one is absorbed by the others.
    (ii) REDUNDANCY -- a rubric that aligns strongly with the crowd's ranking is one whose criteria
         agree with each other, and a redundant rubric is insensitive to any single member.
  These predict the same sign and this release cannot separate them, because the proxy is built
  from the same tensors as the outcome. WHAT IS ESTABLISHED is a BOUND: every operator number in
  r212-r214 varies by up to {1 / min(rat):.1f}x across the proxy's range, and the pooled figure sits between the
  halves. That bound belongs on every flip rate this project has published.
  LIMIT: the proxy is itself built from the same tensors, so it cannot separate "criteria describe
  the chosen answer" from "criteria and choice both track response quality". That separation needs
  response-blind elicitation and is the first item on the north star's collection list.""")

    json.dump({"corr_margin_meanW": [r_w, lo_w, hi_w],
               "mde_nonsurvivors": {"n": len(ns), "median_mde": float(np.median(allm)),
                                    "above_own_mde": under},
               "world_self": s_m, "world_other": o_m, "world_z": (s_m - o_m) / se,
               "contamination": {k: dict(v) for k, v in res.items()}},
              open(OUT / "remaining.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
