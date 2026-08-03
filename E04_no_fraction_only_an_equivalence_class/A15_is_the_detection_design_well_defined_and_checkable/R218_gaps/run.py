"""The four gaps the paper audit found, computed.

G1 TIES. The paper asserts exact argmax ties occur with probability zero. Assertion, not measured.
G2 STRATEGY-PROOFNESS. Gibbard-Satterthwaite says every non-dictatorial rule over >=3 alternatives
   is manipulable. The question that matters: can an annotator here actually improve the collective
   outcome BY THEIR OWN RANKING by misreporting their weights? If yes at any rate, the elicited
   norms are not guaranteed sincere and every number is about reported rather than held values.
G3 JUDGE CIRCULARITY. Criteria were written ABOUT these four responses; the judge then scores those
   criteria AGAINST those same responses. Test: is satisfaction higher for the response its author
   ranked first than for the others, beyond what the criterion's content would predict?
G4 THE TWO ELICITATIONS. Criteria-route and ranking-route agree 68.4%. Corrected for the
   reliability of each, how much of the 31.6% is measurement error rather than real disagreement?
"""
from __future__ import annotations
import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"; L = "ABCD"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"


def load(p):
    d = np.load(p, allow_pickle=True); o = defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    return o


def parse_rank(s):
    if not s or (">" not in s and "=" not in s): return None
    blocks = [b.split("=") for b in str(s).split(">")]
    seen, pts, k = set(), np.full(4, np.nan), 0
    for b in blocks:
        ls = [x.strip() for x in b if x.strip() in L]
        if not ls: return None
        share = np.mean([3 - (k + i) for i in range(len(ls))])
        for x in ls:
            if x in seen: return None
            seen.add(x); pts[L.index(x)] = share
        k += len(ls)
    return None if np.isnan(pts).any() else pts


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
        if p not in recs: continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f) if it.get("scores")
              and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4: continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
        raw = {i: [float(s_["score"]) for s_ in f[i]["scores"]] for i in ok}
        aid = {i: [s_["annotator_id"] for s_ in f[i]["scores"]] for i in ok}
        W = {i: float(np.mean(raw[i])) for i in ok}
        per = defaultdict(lambda: np.zeros(4))
        for i in ok:
            for v, a in zip(raw[i], aid[i]): per[a] = per[a] + v * S[i]
        world = {}
        for a in ann.get(p, []):
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                v = parse_rank(e.get("ranking"))
                if v is not None: world[a["annotator_id"]] = v
        ST[p] = {"ok": ok, "S": S, "W": W, "raw": raw, "aid": aid,
                 "per": dict(per), "world": world}
    pl = sorted(ST); print(f"prompts {len(pl)}\n")

    # ------------------------------------------------------------------ G1 ties
    print("=" * 92); print("G1  ARE ARGMAX TIES ACTUALLY ABSENT"); print("=" * 92)
    ties = near = 0
    for p in pl:
        y = sum(ST[p]["W"][i] * ST[p]["S"][i] for i in ST[p]["ok"])
        s = np.sort(y)[::-1]
        ties += int(s[0] == s[1]); near += int((s[0] - s[1]) < 1e-6 * max(abs(s[0]), 1))
    print(f"  exact ties in the top two: {ties} of {len(pl)}")
    print(f"  gaps below 1e-6 relative:  {near} of {len(pl)}")
    print(f"  -> the paper's 'ties occur with probability zero' is {'CONFIRMED as measured' if ties==0 else 'FALSE'}, and is now measured\n")
    R["ties"] = {"exact": ties, "near": near, "n": len(pl)}

    # ------------------------------------------------------------------ G2 manipulability
    print("=" * 92); print("G2  CAN AN ANNOTATOR IMPROVE THE OUTCOME BY MISREPORTING (Gibbard-Satterthwaite)")
    print("=" * 92)
    manip = tested = strict = 0
    for p in pl:
        d = ST[p]; ok, S = d["ok"], d["S"]
        A = sorted(d["per"])
        if len(A) < 3: continue
        for a in A:
            if a not in d["world"]: continue
            own = d["world"][a]                       # their OWN stated ranking, the payoff
            # honest collective score
            def coll(over=None):
                y = np.zeros(4)
                for i in ok:
                    vs = [(over.get(i, v) if (over and aa == a) else v)
                          for v, aa in zip(d["raw"][i], d["aid"][i])]
                    y = y + float(np.mean(vs)) * S[i]
                return y
            base = int(np.argmax(coll()))
            tested += 1
            best = own[base]
            # the manipulation set: push every criterion they rated to +-10
            for sgn in (+1, -1):
                over = {i: sgn * 10.0 for i in ok if a in d["aid"][i]}
                if not over: continue
                w = int(np.argmax(coll(over)))
                if own[w] > best:
                    manip += 1; strict += int(own[w] > own[base]); break
    print(f"  (annotator, prompt) pairs tested: {tested}")
    print(f"  pairs where a +-10 misreport yields a strictly better outcome BY THEIR OWN RANKING:")
    print(f"    {manip} = {manip/max(tested,1):.1%}")
    print(f"""  Gibbard-Satterthwaite guarantees manipulability EXISTS for any non-dictatorial rule over
  >=3 alternatives. What it does not give is the RATE, and the rate is what decides whether the
  elicited weights can be read as sincere. Measured here with only the crudest manipulation
  (saturate every rated criterion to one end of the scale), it is {manip/max(tested,1):.1%} -- a LOWER BOUND,
  since a smarter misreport can only do better.\n""")
    R["manip"] = {"tested": tested, "manipulable": manip, "rate": manip / max(tested, 1)}

    # ------------------------------------------------------------------ G3 circularity
    print("=" * 92); print("G3  IS THE JUDGE SCORING CRITERIA AGAINST THE RESPONSES THEY WERE WRITTEN ABOUT")
    print("=" * 92)
    own_top, other = [], []
    for p in pl:
        d = ST[p]
        for i in d["ok"]:
            for a in set(d["aid"][i]):
                if a not in d["world"]: continue
                t = int(np.argmax(d["world"][a]))
                sat = d["S"][i]
                own_top.append(sat[t]); other.append(np.mean([sat[j] for j in range(4) if j != t]))
    ot, oo = np.array(own_top), np.array(other)
    dd = ot - oo
    se = dd.std(ddof=1) / math.sqrt(len(dd))
    print(f"  criterion-author pairs: {len(dd):,}")
    print(f"  satisfaction of the AUTHOR'S OWN top-ranked response  {ot.mean():.4f}")
    print(f"  mean satisfaction of the other three                  {oo.mean():.4f}")
    print(f"  difference {dd.mean():+.4f}  se {se:.4f}  z {dd.mean()/se:+.1f}")
    print(f"""  A criterion written by someone who ranked response X first is satisfied by X
  {dd.mean():+.4f} more than by the average other response. That is not a bug in the judge -- it is
  what "I wrote down why X is best" means. But it makes SATISFACTION and CHOICE two views of one
  act rather than independent measurements, and every correlation between them inherits it.\n""")
    R["circular"] = {"own": float(ot.mean()), "other": float(oo.mean()),
                     "diff": float(dd.mean()), "z": float(dd.mean() / se), "n": len(dd)}

    # ------------------------------------------------------------------ G4 two elicitations
    print("=" * 92); print("G4  THE 31.6% DISAGREEMENT: HOW MUCH IS MEASUREMENT ERROR")
    print("=" * 92)
    rng = np.random.default_rng(0)
    rel_rank, rel_crit = [], []
    for p in pl:
        d = ST[p]
        Wv = list(d["world"].values())
        if len(Wv) >= 6:
            ix = rng.permutation(len(Wv))
            h1 = np.mean([Wv[i] for i in ix[:len(Wv)//2]], axis=0)
            h2 = np.mean([Wv[i] for i in ix[len(Wv)//2:]], axis=0)
            a_, b_ = h1 - h1.mean(), h2 - h2.mean()
            if np.linalg.norm(a_) > 1e-9 and np.linalg.norm(b_) > 1e-9:
                rel_rank.append(a_ @ b_ / (np.linalg.norm(a_) * np.linalg.norm(b_)))
        P = list(d["per"].values())
        if len(P) >= 6:
            ix = rng.permutation(len(P))
            h1 = sum(P[i] for i in ix[:len(P)//2]); h2 = sum(P[i] for i in ix[len(P)//2:])
            a_, b_ = h1 - h1.mean(), h2 - h2.mean()
            if np.linalg.norm(a_) > 1e-9 and np.linalg.norm(b_) > 1e-9:
                rel_crit.append(a_ @ b_ / (np.linalg.norm(a_) * np.linalg.norm(b_)))
    rr, rc = float(np.mean(rel_rank)), float(np.mean(rel_crit))
    sbr, sbc = 2 * rr / (1 + rr), 2 * rc / (1 + rc)
    obs = []
    for p in pl:
        d = ST[p]
        if not d["world"]: continue
        wv = np.mean(list(d["world"].values()), axis=0)
        yv = sum(d["W"][i] * d["S"][i] for i in d["ok"])
        a_, b_ = wv - wv.mean(), yv - yv.mean()
        if np.linalg.norm(a_) > 1e-9 and np.linalg.norm(b_) > 1e-9:
            obs.append(a_ @ b_ / (np.linalg.norm(a_) * np.linalg.norm(b_)))
    ob = float(np.mean(obs))
    dis = ob / math.sqrt(max(sbr * sbc, 1e-12))
    print(f"  reliability (Spearman-Brown) of the RANKING route:  {sbr:.4f}  (split-half {rr:.4f})")
    print(f"  reliability of the CRITERIA route:                  {sbc:.4f}  (split-half {rc:.4f})")
    print(f"  observed cosine between the two routes:             {ob:.4f}")
    print(f"  DISATTENUATED  = {ob:.4f} / sqrt({sbr:.4f} x {sbc:.4f}) = {dis:.4f}")
    print(f"""  Correcting both routes for their own unreliability raises the agreement from {ob:.3f} to
  {dis:.3f}. {'Even fully corrected the two elicitations do NOT coincide' if dis < 0.95 else 'Fully corrected they coincide'}: the residual {1-dis:.1%} is disagreement between what people WRITE and what
  they CHOOSE, not noise in measuring either. That is the same quantity as the 0.393 self-cosine of
  the paper, now expressed at the panel level and with the measurement error removed.""")
    R["two_elicitations"] = {"rel_rank": sbr, "rel_crit": sbc, "observed": ob, "disattenuated": dis}

    json.dump(R, open(OUT / "gaps.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
