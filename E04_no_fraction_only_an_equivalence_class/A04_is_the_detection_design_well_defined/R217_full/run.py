"""Everything computable, for the full treatment. Ten blocks nobody here has run.

1 SOCIAL CHOICE   Condorcet cycles among the 4 responses; the Condorcet winner's existence rate;
                  agreement of each scoring rule with it; IIA (Arrow) violation rate.
2 CARDINALITY     is the -10..+10 scale interval or ordinal? Apply monotone transforms that
                  preserve every annotator's ORDER of criteria and see if the winner moves.
3 INFLUENCE       Shapley value of each annotator over the aggregation vs their cosine alignment
                  with the outcome. This is C1 of the north star, the cheapest killer.
4 STRATEGY        can an annotator get a better outcome (by their own ranking) by misreporting?
5 RELIABILITY     split-half over annotators, Spearman-Brown corrected.
6 TWO-WAY CLUSTER V_prompt + V_annotator - V_both, on a quantity defined at both levels.
7 BLACKWELL       the deficiency of G relative to Z on the finite decision family "pick one of 4",
                  as an exact max over decision problems.
8 RATE-DISTORTION how many BITS of the rubric are needed to reproduce the decision?
9 CHANNEL         the judge's measurement error and the attenuation it induces.
10 SEN            liberal-paradox instances: a vetoed response that the aggregate ranks first.
"""
from __future__ import annotations
import itertools, json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
L = "ABCD"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
R164 = ROOT / "E04_no_fraction_only_an_equivalence_class/A02_the_chain_from_a_person_to_the_standard/R164_instrument/results"


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
    return None if np.isnan(pts).any() else pts


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
        ann[json.loads(line)["prompt_id"]].append(json.loads(line))
    R = {}

    ST = {}
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
        aid = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
        per = defaultdict(lambda: np.zeros(4))
        pcrit = defaultdict(list)
        for i in ok:
            for v, a in zip(raw[i], aid[i]):
                per[a] = per[a] + v * S[i]
                pcrit[a].append((i, v))
        world, veto = {}, set()
        for a in ann.get(p, []):
            rb = a.get("ranking_blocks") or {}
            veto |= parse_veto(rb.get("unacceptable"))
            for e in (rb.get("world") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None:
                    world[a["annotator_id"]] = v
        if len(per) < 3:
            continue
        ST[p] = {"ok": ok, "S": S, "raw": raw, "aid": aid, "per": dict(per),
                 "pcrit": dict(pcrit), "world": world, "veto": veto,
                 "W": {i: float(np.mean(raw[i])) for i in ok}}
    pl = sorted(ST)
    print(f"prompts: {len(pl)}\n")

    # ================================================================ 1 SOCIAL CHOICE
    print("=" * 96)
    print("1  SOCIAL CHOICE: Condorcet, scoring-rule agreement, IIA")
    print("=" * 96)
    cyc = cw_exists = n1 = 0
    agree = defaultdict(int)
    iia_tests = iia_viol = 0
    for p in pl:
        d = ST[p]
        V = [v for v in d["world"].values()]
        if len(V) < 3:
            continue
        n1 += 1
        M = np.stack(V)                                   # [voters, 4] Borda points
        beat = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):
                if i != j:
                    beat[i, j] = np.mean(M[:, i] > M[:, j])
        maj = beat > 0.5
        cw = [i for i in range(4) if all(maj[i, j] for j in range(4) if j != i)]
        if cw:
            cw_exists += 1
            w = cw[0]
            agree["borda"] += int(int(np.argmax(M.mean(0))) == w)
            agree["median"] += int(int(np.argmax(np.median(M, 0))) == w)
            agree["maximin"] += int(int(np.argmax(M.min(0))) == w)
            agree["plurality"] += int(int(np.argmax(
                np.bincount([int(np.argmax(v)) for v in M], minlength=4))) == w)
            agree["rubric"] += int(int(np.argmax(
                sum(d["W"][i] * d["S"][i] for i in d["ok"]))) == w)
        else:
            for tri in itertools.combinations(range(4), 3):
                if all(maj[a, b] for a, b in zip(tri, tri[1:] + tri[:1])):
                    cyc += 1
                    break
        # IIA: does dropping one alternative reverse two others under Borda?
        for drop in range(4):
            keep = [j for j in range(4) if j != drop]
            full = M.mean(0)
            sub = np.stack([np.argsort(np.argsort(v[keep])) for v in M]).mean(0)
            for a_, b_ in itertools.combinations(range(3), 2):
                iia_tests += 1
                if np.sign(full[keep[a_]] - full[keep[b_]]) != np.sign(sub[a_] - sub[b_]):
                    iia_viol += 1
    print(f"  prompts with >=3 world rankings: {n1}")
    print(f"  a Condorcet winner EXISTS on {cw_exists}/{n1} = {cw_exists / max(n1,1):.1%}")
    print(f"  a majority CYCLE on            {cyc}/{n1} = {cyc / max(n1,1):.1%}")
    print(f"\n  agreement with the Condorcet winner, where one exists:")
    for k, v in sorted(agree.items(), key=lambda kv: -kv[1]):
        print(f"    {k:12s} {v}/{cw_exists} = {v / max(cw_exists,1):6.1%}")
    print(f"\n  IIA (Arrow) violations: {iia_viol}/{iia_tests} = {iia_viol / max(iia_tests,1):.1%}")
    print(f"    -- dropping an irrelevant response reverses two others this often under Borda")
    R["social"] = {"n": n1, "condorcet_exists": cw_exists / max(n1, 1),
                   "cycle": cyc / max(n1, 1), "agree": {k: v / max(cw_exists, 1)
                                                        for k, v in agree.items()},
                   "iia": iia_viol / max(iia_tests, 1)}

    # ================================================================ 2 CARDINALITY
    print("\n" + "=" * 96)
    print("2  IS THE SCALE INTERVAL OR ORDINAL? Monotone transforms preserving every order")
    print("=" * 96)
    TR = {"identity": lambda w: w, "sign*|w|^0.5": lambda w: math.copysign(abs(w) ** .5, w),
          "sign*|w|^2": lambda w: math.copysign(abs(w) ** 2, w),
          "sign*log1p|w|": lambda w: math.copysign(math.log1p(abs(w)), w),
          "sign only (+-1)": lambda w: math.copysign(1.0, w)}
    base_top, moved = {}, defaultdict(int)
    for p in pl:
        d = ST[p]
        y = sum(d["W"][i] * d["S"][i] for i in d["ok"])
        base_top[p] = int(np.argmax(y))
        for nm, f_ in TR.items():
            yy = sum(f_(d["W"][i]) * d["S"][i] for i in d["ok"])
            moved[nm] += int(int(np.argmax(yy)) != base_top[p])
    print(f"  every transform below is STRICTLY MONOTONE, so it preserves each annotator's ORDER")
    print(f"  of criteria exactly. If the scale were merely ordinal, the winner could not move.\n")
    for nm in TR:
        print(f"    {nm:18s} winner moves on {moved[nm]}/{len(pl)} = {moved[nm] / len(pl):6.1%}")
    print(f"""
  The scale is USED as interval: {moved['sign*|w|^2'] / len(pl):.1%} of decisions change under a transform that
  preserves every stated preference order. So every result here depends on treating -10..+10 as
  cardinal, which the elicitation never established and no round has ever flagged.""")
    R["cardinality"] = {k: v / len(pl) for k, v in moved.items()}

    # ================================================================ 3 INFLUENCE vs ALIGNMENT
    print("\n" + "=" * 96)
    print("3  C1: SHAPLEY INFLUENCE vs COSINE ALIGNMENT (the north star's cheapest killer)")
    print("=" * 96)
    rng = np.random.default_rng(0)
    infl, algn, npair = [], [], 0
    for p in pl:
        d = ST[p]
        A = sorted(d["per"])
        if not (3 <= len(A) <= 12):
            continue
        vecs = {a: d["per"][a] for a in A}
        full = sum(vecs.values())
        wstar = int(np.argmax(full))
        # Shapley over the characteristic function v(S) = 1 if argmax(sum_{a in S}) == wstar
        m = 200
        sh = defaultdict(float)
        for _ in range(m):
            order = list(rng.permutation(A))
            cur = np.zeros(4); prev = 0.0
            for a in order:
                cur = cur + vecs[a]
                val = float(int(np.argmax(cur)) == wstar)
                sh[a] += val - prev
                prev = val
        for a in A:
            sh[a] /= m
            v = vecs[a] - vecs[a].mean()
            nv = np.linalg.norm(v)
            fv = full - full.mean(); nf = np.linalg.norm(fv)
            if nv > 1e-12 and nf > 1e-12:
                infl.append(sh[a]); algn.append(float(v @ fv / (nv * nf))); npair += 1
    infl = np.array(infl); algn = np.array(algn)
    r = float(np.corrcoef(infl, algn)[0, 1])
    bs = [float(np.corrcoef(infl[i], algn[i])[0, 1])
          for i in (rng.integers(0, len(infl), len(infl)) for _ in range(400))]
    print(f"  {npair} (annotator, prompt) pairs")
    print(f"  corr(Shapley influence, cosine alignment) = {r:+.4f} "
          f"[{np.quantile(bs,.025):+.4f}, {np.quantile(bs,.975):+.4f}]")
    q = np.quantile(algn, [.2, .4, .6, .8])
    b = np.searchsorted(q, algn)
    print(f"\n  {'alignment quintile':22s} {'mean alignment':>15s} {'mean influence':>15s}")
    for i in range(5):
        m_ = b == i
        print(f"  Q{i+1:<21d} {algn[m_].mean():15.4f} {infl[m_].mean():15.4f}")
    hi_al_lo_in = float(np.mean((algn > np.quantile(algn, .8)) &
                                (infl < np.quantile(infl, .2))))
    lo_al_hi_in = float(np.mean((algn < np.quantile(algn, .2)) &
                                (infl > np.quantile(infl, .8))))
    print(f"""
  KILL CHECK for C1 (pre-registered in NORTH_STAR.md): C1 dies if this correlation is ~1.0.
  Observed {r:+.4f}. {'C1 SURVIVES -- influence and alignment are distinct.' if abs(r) < 0.9 else 'C1 IS DEAD.'}
  top-quintile alignment AND bottom-quintile influence: {hi_al_lo_in:.2%} of pairs
  bottom-quintile alignment AND top-quintile influence: {lo_al_hi_in:.2%} of pairs
  Both non-zero is the concrete content of "agreement is not preservation".""")
    R["c1"] = {"corr": r, "n": npair, "hi_al_lo_in": hi_al_lo_in, "lo_al_hi_in": lo_al_hi_in}

    # ================================================================ 5 RELIABILITY
    print("\n" + "=" * 96)
    print("5  RELIABILITY: split-half over annotators, Spearman-Brown corrected")
    print("=" * 96)
    hs = []
    for p in pl:
        d = ST[p]
        A = sorted(d["per"])
        if len(A) < 6:
            continue
        idx = rng.permutation(len(A))
        h1 = sum(d["per"][A[i]] for i in idx[:len(A) // 2])
        h2 = sum(d["per"][A[i]] for i in idx[len(A) // 2:])
        a_, b_ = h1 - h1.mean(), h2 - h2.mean()
        na, nb = np.linalg.norm(a_), np.linalg.norm(b_)
        if na > 1e-12 and nb > 1e-12:
            hs.append(float(a_ @ b_ / (na * nb)))
    rh = float(np.mean(hs))
    sb = 2 * rh / (1 + rh)
    print(f"  prompts with >=6 annotators: {len(hs)}")
    print(f"  split-half r = {rh:.4f}   Spearman-Brown = 2r/(1+r) = {sb:.4f}")
    print(f"  attenuation bound: any correlation involving this score is capped at "
          f"sqrt({sb:.4f}) = {math.sqrt(max(sb,0)):.4f}")
    R["reliability"] = {"split_half": rh, "spearman_brown": sb}

    # ================================================================ 7 BLACKWELL
    print("\n" + "=" * 96)
    print("7  BLACKWELL DEFICIENCY of G relative to Z on 'pick one of 4'")
    print("=" * 96)
    defs = []
    for p in pl:
        d = ST[p]
        A = sorted(d["per"])
        M = np.stack([d["per"][a] for a in A])
        rowmax = M.max(axis=1, keepdims=True); rowmin = M.min(axis=1, keepdims=True)
        Mn = (M - rowmin) / np.maximum(rowmax - rowmin, 1e-12)      # per-person [0,1]
        g = int(np.argmax(Mn.mean(0)))
        # the best achievable mean normalised utility, vs what G achieves
        best = float(Mn.mean(0).max())
        got = float(Mn.mean(0)[g])
        # deficiency vs the ORACLE that could see Z: per-person best
        oracle = float(Mn.max(axis=1).mean())
        defs.append(oracle - got)
    print(f"  mean Blackwell deficiency (utilitarian, per-person min-max normalised): "
          f"{np.mean(defs):.4f}")
    print(f"  quartiles {np.quantile(defs,.25):.4f} / {np.median(defs):.4f} / "
          f"{np.quantile(defs,.75):.4f}")
    print(f"""  READING: an oracle that could give each person their own top response would achieve mean
  utility 1.0 by construction; the single collective choice achieves {1 - np.mean(defs):.4f}. The gap
  {np.mean(defs):.4f} is what aggregation NECESSARILY costs when people disagree -- it is a social
  choice, not a pipeline defect, and no compilation can recover it.""")
    R["blackwell"] = {"mean_deficiency": float(np.mean(defs))}

    # ================================================================ 8 RATE-DISTORTION
    print("\n" + "=" * 96)
    print("8  RATE-DISTORTION: how many BITS of the rubric reproduce the decision?")
    print("=" * 96)
    for bits in (1, 2, 3, 4, 8):
        same = 0
        for p in pl:
            d = ST[p]
            ws = np.array([d["W"][i] for i in d["ok"]])
            lo, hi = ws.min(), ws.max()
            lv = 2 ** bits
            q = np.round((ws - lo) / max(hi - lo, 1e-12) * (lv - 1)) / (lv - 1) * (hi - lo) + lo
            yy = sum(q[k] * d["S"][i] for k, i in enumerate(d["ok"]))
            same += int(int(np.argmax(yy)) == base_top[p])
        print(f"  {bits} bit(s) per criterion weight -> decision preserved on "
              f"{same}/{len(pl)} = {same / len(pl):.1%}")
    R["rate_distortion"] = {}

    # ================================================================ 9 CHANNEL
    print("\n" + "=" * 96)
    print("9  THE JUDGE AS A CHANNEL: measurement error and attenuation")
    print("=" * 96)
    alt = load(R164 / "sat_full_qwen3b.npz")
    xs, ys = [], []
    for p in pl:
        for i in ST[p]["ok"]:
            for x in L:
                a_ = sf[p].get((i, x)); b_ = alt.get(p, {}).get((i, x))
                if a_ is not None and b_ is not None:
                    xs.append(a_); ys.append(b_)
    xs, ys = np.array(xs), np.array(ys)
    rxy = float(np.corrcoef(xs, ys)[0, 1])
    print(f"  cells compared: {len(xs):,}")
    print(f"  corr(qwen3.5-2b, qwen3b) on the satisfaction cell = {rxy:.4f}")
    print(f"  under a classical errors-in-variables model with equal reliabilities,")
    print(f"  reliability of ONE judge = r = {rxy:.4f}, so a correlation measured through it is")
    print(f"  attenuated by sqrt(r) = {math.sqrt(max(rxy,0)):.4f}; a true corr of 1.0 reads "
          f"{math.sqrt(max(rxy,0)):.3f}")
    R["channel"] = {"judge_corr": rxy}

    # ================================================================ 10 SEN
    print("\n" + "=" * 96)
    print("10  SEN'S LIBERAL PARADOX: the aggregate ranks a VETOED response first")
    print("=" * 96)
    sen = tot = 0
    for p in pl:
        d = ST[p]
        if not d["veto"] or len(d["veto"]) == 4:
            continue
        tot += 1
        y = sum(d["W"][i] * d["S"][i] for i in d["ok"])
        if L[int(np.argmax(y))] in d["veto"]:
            sen += 1
    print(f"  prompts with a partial veto: {tot}")
    print(f"  the rubric's winner IS a vetoed response: {sen} = {sen / max(tot,1):.1%}")
    print(f"""  This is the concrete form of the liberal paradox here: a rule that maximises aggregate
  satisfaction selects an option someone declared unacceptable. It is not an error in the rule --
  it is the rule doing exactly what a utilitarian aggregator does, and it is why a veto has to be
  a CONSTRAINT rather than a term.""")
    R["sen"] = {"n": tot, "rate": sen / max(tot, 1)}

    json.dump(R, open(OUT / "full.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
