"""Every quantity in the derivation, computed. No prose here -- the prose is the report.

Computes, in order:
  A  the probe bound, verified: rank of the space of identifiable contrasts
  B  the ICC and design effect behind the z-inflation
  C  the margin distribution and the flip-rate CAP it imposes
  D  NORMALISED REGRET -- the decision-theoretic quantity the flip rate is a coarsening of
  E  the exact M required to encode a veto as a weight (C2, made computable)
  F  se and MDE per operator, paired at the prompt
  G  the instrument's own gauge noise as a floor on every operator claim
"""
from __future__ import annotations
import json, math, pathlib, sys, pickle
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results"
R164 = ROOT / "13_normative_chain/r164_instrument/results"


def load(p):
    d = np.load(p, allow_pickle=True)
    o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o


def parse_veto(block):
    out = set()
    for e in block or []:
        for r in (e.get("rating") or []):
            t = str(r).strip()
            if t and t[0] in L and "unacceptable" in t.lower():
                out.add(t[0])
    return out


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
    res = {}

    # ---------------------------------------------------------------- A probe bound
    print("A  PROBE BOUND")
    U = np.eye(4)
    C = U - U.mean(axis=1, keepdims=True)
    print(f"   rank of the centred utility space over k=4 responses: {np.linalg.matrix_rank(C)}")
    print(f"   after scale quotient: {np.linalg.matrix_rank(C) - 1} free parameters -> S^2\n")
    res["probe_rank"] = int(np.linalg.matrix_rank(C))

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
        W = {i: float(np.mean([s_["score"] for s_ in f[i]["scores"]])) for i in ok}
        y = sum(W[i] * S[i] for i in ok)
        veto = set()
        for a in ann.get(p, []):
            veto |= parse_veto((a.get("ranking_blocks") or {}).get("unacceptable"))
        store[p] = {"ok": ok, "S": S, "W": W, "y": y, "veto": veto}
    pl = sorted(store)
    print(f"   prompts: {len(pl)}\n")

    # ---------------------------------------------------------------- C margins
    print("C  MARGIN DISTRIBUTION AND THE CAP IT IMPOSES")
    marg, rngs = [], []
    for p in pl:
        y = store[p]["y"]; s = np.sort(y)[::-1]
        marg.append(s[0] - s[1]); rngs.append(y.max() - y.min())
    marg = np.array(marg); rngs = np.array(rngs)
    rel = marg / np.maximum(rngs, 1e-12)
    qs = np.quantile(rel, [.05, .25, .5, .75, .95])
    print(f"   relative margin (top1-top2)/(range): "
          f"p05 {qs[0]:.3f} p25 {qs[1]:.3f} MEDIAN {qs[2]:.3f} p75 {qs[3]:.3f} p95 {qs[4]:.3f}")
    res["margin_q"] = qs.tolist()

    # ---------------------------------------------------------------- D regret
    print("\nD  NORMALISED REGRET, per operator")
    rng = np.random.default_rng(0)
    OPS = {"dose_double": 2.0, "dose_delete": 0.0, "dose_invert": -1.0, "dose_weaken": 0.5}
    reg = defaultdict(list); flip = defaultdict(list); reg_pos = defaultdict(list)
    percell = defaultdict(lambda: defaultdict(list))
    for p in pl:
        d = store[p]; ok, S, W, y = d["ok"], d["S"], d["W"], d["y"]
        a0 = int(np.argmax(y)); span = y[a0] - y.min()
        for seed in range(20):
            c = int(np.random.default_rng(hash((p, seed)) % 2**32).choice(ok))
            for nm, mul in OPS.items():
                yy = sum((W[i] * mul if i == c else W[i]) * S[i] for i in ok)
                a1 = int(np.argmax(yy))
                r = (y[a0] - y[a1]) / max(span, 1e-12)
                reg[nm].append(r); flip[nm].append(int(a1 != a0))
                if a1 != a0:
                    reg_pos[nm].append(r)
                percell[nm][p].append((int(a1 != a0), r))
    print(f"   {'operator':14s} {'P(flip)':>9s} {'E[regret]':>10s} "
          f"{'E[reg|flip]':>12s} {'reg/flip':>9s}")
    for nm in OPS:
        pf = float(np.mean(flip[nm])); er = float(np.mean(reg[nm]))
        erf = float(np.mean(reg_pos[nm])) if reg_pos[nm] else float("nan")
        print(f"   {nm:14s} {pf:8.1%} {er:10.4f} {erf:12.4f} {er / max(pf, 1e-9):9.4f}")
        res.setdefault("regret", {})[nm] = {"flip": pf, "E_regret": er, "E_regret_given_flip": erf}

    # ---------------------------------------------------------------- B ICC
    print("\nB  ICC AND DESIGN EFFECT")
    for nm in ("dose_delete",):
        M = [np.array([x[0] for x in percell[nm][p]], float) for p in pl]
        R = len(M[0])
        gm = np.mean([m.mean() for m in M])
        s_b = np.var([m.mean() for m in M], ddof=1)
        s_w = np.mean([m.var(ddof=1) if len(m) > 1 else 0.0 for m in M])
        icc = s_b / max(s_b + s_w, 1e-12)
        deff = 1 + (R - 1) * icc
        print(f"   {nm}: R={R} per prompt, sigma2_between {s_b:.5f}, sigma2_within {s_w:.5f}")
        print(f"   ICC rho = {icc:.4f}   DEFF = 1+(R-1)rho = {deff:.2f}   "
              f"naive se understates by sqrt(DEFF) = {math.sqrt(deff):.2f}x")
        res["icc"] = {"rho": float(icc), "deff": float(deff), "R": R}

    # ---------------------------------------------------------------- E veto as weight
    print("\nE  THE EXACT M REQUIRED TO ENCODE A VETO AS A WEIGHT")
    need, tot, wmax = [], 0, []
    for p in pl:
        d = store[p]; y = d["y"]; v = d["veto"]
        if not v or len(v) == 4:
            continue
        vi = [L.index(x) for x in v]; ni = [j for j in range(4) if j not in vi]
        gap = max(y[j] for j in vi) - max(y[j] for j in ni)
        tot += 1
        need.append(max(gap, 0.0))
        wmax.append(max(abs(w) for w in d["W"].values()))
    need = np.array(need); wmax = np.array(wmax)
    binding = need > 0
    print(f"   prompts with a partial veto: {tot}")
    print(f"   the veto is BINDING (the vetoed response would otherwise win) on "
          f"{binding.sum()} = {binding.mean():.1%}")
    if binding.sum():
        nb = need[binding]
        print(f"   required penalty M = max_vetoed Y - max_allowed Y: "
              f"median {np.median(nb):.2f}, p90 {np.quantile(nb, .9):.2f}, max {nb.max():.2f}")
        scale = 10.0
        print(f"   largest single-criterion weight available: |w| <= {scale}")
        print(f"   M expressed in units of one maximal criterion's contribution "
              f"(w=10, satisfaction span <=1): median {np.median(nb) / scale:.2f} criteria, "
              f"max {nb.max() / scale:.2f} criteria")
        res["veto"] = {"n": int(tot), "binding": float(binding.mean()),
                       "M_median": float(np.median(nb)), "M_max": float(nb.max()),
                       "M_p90": float(np.quantile(nb, .9))}

    # ---------------------------------------------------------------- F se / MDE
    print("\nF  se AND MDE, PAIRED AT THE PROMPT")
    print(f"   {'operator':14s} {'pi':>8s} {'se':>8s} {'95% CI':>18s} {'MDE(80%)':>9s}")
    for nm in OPS:
        pm = np.array([np.mean([x[0] for x in percell[nm][p]]) for p in pl])
        pi = pm.mean(); se = pm.std(ddof=1) / math.sqrt(len(pm))
        print(f"   {nm:14s} {pi:7.1%} {se:8.4f} "
              f"[{pi - 1.96 * se:6.1%},{pi + 1.96 * se:6.1%}] {2.8016 * se:9.4f}")
        res.setdefault("power", {})[nm] = {"pi": float(pi), "se": float(se),
                                           "mde": float(2.8016 * se)}
    a = np.array([np.mean([x[0] for x in percell["dose_delete"][p]]) for p in pl])
    b = np.array([np.mean([x[0] for x in percell["dose_double"][p]]) for p in pl])
    dd = a - b
    sed = dd.std(ddof=1) / math.sqrt(len(dd))
    print(f"   PAIRED delete - double: {dd.mean():+.4f}  se {sed:.4f}  z {dd.mean() / sed:+.1f}  "
          f"MDE {2.8016 * sed:.4f}")
    res["paired_delete_double"] = {"d": float(dd.mean()), "se": float(sed),
                                   "z": float(dd.mean() / sed)}

    # ---------------------------------------------------------------- G gauge floor
    print("\nG  THE GAUGE NOISE FLOOR")
    sw = load(R164 / "sat_full_variant_swapped.npz")
    both = [p for p in pl if p in sw]
    dis = 0
    for p in both:
        d = store[p]; ok = d["ok"]
        if not all((i, x) in sw[p] for i in ok for x in L):
            continue
        y2 = sum(d["W"][i] * np.array([sw[p][(i, x)] for x in L], float) for i in ok)
        dis += int(np.argmax(y2) != int(np.argmax(d["y"])))
    fl = dis / max(len(both), 1)
    print(f"   same judge, same norm, options reordered: winner differs on {fl:.1%} of "
          f"{len(both)} prompts")
    print(f"   operators whose pi is BELOW this floor:")
    for nm in OPS:
        pi = res["power"][nm]["pi"]
        if pi < fl:
            print(f"     {nm:14s} pi {pi:.1%} < floor {fl:.1%}")
    res["gauge_floor"] = fl

    json.dump(res, open(OUT / "derivation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
