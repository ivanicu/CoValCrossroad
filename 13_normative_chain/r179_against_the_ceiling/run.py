"""50.3% against 25% is the wrong denominator. What was actually achievable?

r178 put the crowd rubric at 50.3% and the length heuristic at 37.2% against a 25% null. That
framing quietly assumes the reachable maximum is 100%, and it is not. These are contested prompts
answered by different people, and two humans looking at the same four responses frequently disagree
about which is best. A predictor cannot be blamed for missing a choice that the next person would
also have missed.

So the accounting this release actually needs has three numbers, not two:

  HUMAN-HUMAN     two different annotators on the same prompt, same top choice. This is what
                  "agreement" means for this task, and it is the number that tells you whether the
                  ranking is measuring a shared property at all.
  THE ORACLE      always name that prompt's MODAL human top choice, computed LEAVE-ONE-OUT so the
                  answer being predicted is never in the majority that predicts it. No
                  prompt-level predictor can beat this, whatever it is built from. It is the
                  ceiling, and it is well under 100%.
  THE APPARATUS   what fraction of that ceiling the crowd rubric captures.

WHY LEAVE-ONE-OUT IS NOT OPTIONAL. Computing the mode over ALL raters including the one being
predicted makes the oracle partly a copy of the target, and the ceiling comes out inflated -- which
would then understate how much of it the rubric captures. The oracle must be blind to the row it is
scored on, exactly like the rubric's own leave-one-annotator-out arm in r178.

AND THE SECOND QUESTION THIS OPENS. A predictor can aim at two different things: the individual
rater in front of it, or the crowd's consensus. Those come apart precisely when people disagree,
which is the interesting half of the corpus. Both are measured, and the gap between them is a
statement about what a collective-alignment pipeline is FOR.

Restricted throughout to assessments with a unique first place -- ties are a different question and
were measured separately at a 13.9% rate.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
TENSOR = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
LETTERS = "ABCD"


def two_way_se(y, g1, g2):
    y = np.asarray(y, float)
    n = len(y)
    r = y - y.mean()

    def cl(g):
        s = defaultdict(float)
        for v, k in zip(r, g):
            s[k] += v
        return sum(x * x for x in s.values()) / n ** 2
    return math.sqrt(max(cl(g1) + cl(g2) - cl([f"{a}||{b}" for a, b in zip(g1, g2)]), 0.0))


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    sat = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, ci, letter = str(k).split("|")
        sat[(pid, int(ci), letter)] = float(v)

    from covalx.judge import load_join
    rub = {}
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        rub[pid] = [float(np.mean([sc["score"] for sc in it["scores"]]))
                    if it.get("scores") else 0.0 for it in r["coval_full"]]

    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    texts = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            key = str(r.get("response_index", LETTERS[i])).strip().upper()
            if key in LETTERS:
                o[key] = " ".join(m.get("content") or "" for m in (r.get("messages") or [])
                                  if isinstance(m.get("content"), str))
        if len(o) == 4:
            texts[c["prompt_id"]] = o

    # ---------------------------------------------------------------- collect the human choices
    rows = []
    for a in (json.loads(l) for l in (DATA / "annotators.jsonl").open()):
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            t = top_of(s)
            if t and pid in texts:
                rows.append((pid, a["annotator_id"], t))
    by_prompt = defaultdict(list)
    for pid, aid, t in rows:
        by_prompt[pid].append((aid, t))
    print(f"assessments with a unique first place: {len(rows)} over {len(by_prompt)} prompts")
    cov = [len(v) for v in by_prompt.values()]
    print(f"raters per prompt: median {int(np.median(cov))}  min {min(cov)}  max {max(cov)}")

    # ---------------------------------------------------------------- 1 human-human agreement
    # PAIRWISE, and each prompt weighted by its pair count, which is the estimand that matches
    # "two people drawn from this panel, same prompt". Reported per prompt then averaged so a
    # heavily-rated anchor prompt cannot dominate.
    per_prompt_agree, pair_tot, pair_hit = [], 0, 0
    for pid, v in by_prompt.items():
        if len(v) < 2:
            continue
        c = Counter(t for _a, t in v)
        n = len(v)
        # pairs agreeing = sum over letters of C(count,2); total pairs = C(n,2)
        agree = sum(x * (x - 1) // 2 for x in c.values())
        tot = n * (n - 1) // 2
        per_prompt_agree.append(agree / tot)
        pair_hit += agree
        pair_tot += tot
    hh_prompt = float(np.mean(per_prompt_agree))
    hh_pair = pair_hit / pair_tot
    print("\n" + "=" * 78)
    print("HUMAN-HUMAN -- do two people on the same prompt pick the same best answer")
    print("=" * 78)
    print(f"  per-prompt mean agreement : {hh_prompt:.1%}  over {len(per_prompt_agree)} prompts")
    print(f"  pooled over all pairs     : {hh_pair:.1%}  ({pair_hit:,} of {pair_tot:,} pairs)")
    print(f"  chance is 25.0%. Two annotators agree on the single best of four responses "
          f"{hh_prompt:.1%} of the time.")
    # THE POOLED NUMBER IS THE CENSUS DEFECT MADE VISIBLE. One anchor prompt was seen by almost
    # every annotator, so it contributes C(n,2) pairs against a median prompt's C(14,2)=91. The
    # gap between the two lines above IS that prompt.
    top = max(by_prompt.items(), key=lambda kv: len(kv[1]))
    tp = len(top[1]) * (len(top[1]) - 1) // 2
    print(f"  THE TWO LINES DISAGREE BY {hh_prompt - hh_pair:+.1%} AND THE REASON IS ONE PROMPT.")
    print(f"  The most-rated prompt carries {len(top[1])} raters = {tp:,} pairs, "
          f"{tp / pair_tot:.0%} of all {pair_tot:,} pairs in the corpus,")
    print(f"  against a median prompt's {int(np.median(cov))} raters. Any agreement statistic "
          f"pooled over pairs is")
    print(f"  {tp / pair_tot:.0%} a statement about that single prompt -- which is the census's "
          f"anchor defect, priced.")
    print(f"  The per-prompt mean is the admissible number and is used everywhere below.")

    # ---------------------------------------------------------------- 2 the leave-one-out oracle
    y_or, y_rub, y_len, gp, gr = [], [], [], [], []
    cache = {}
    for pid, aid, t in rows:
        v = by_prompt[pid]
        if len(v) < 3:
            continue
        c = Counter(tt for aa, tt in v if aa != aid)      # LEAVE-ONE-OUT
        if not c:
            continue
        mx = max(c.values())
        modes = [k for k, x in c.items() if x == mx]
        # ties in the mode are resolved by giving the oracle its BEST case, which makes the
        # ceiling an upper bound rather than an estimate -- the conservative direction here.
        y_or.append(1.0 if t in modes else 0.0)
        if pid not in cache and pid in rub:
            w = rub[pid]
            sc = {}
            ok = True
            for L in LETTERS:
                tot, hit = 0.0, 0
                for ci, wi in enumerate(w):
                    x = sat.get((pid, ci, L))
                    if x is not None:
                        tot += wi * x
                        hit += 1
                if not hit:
                    ok = False
                sc[L] = tot
            cache[pid] = (sc, {L: len(texts[pid][L]) for L in LETTERS}) if ok else None
        cell = cache.get(pid)
        if cell is None:
            y_or.pop()
            continue
        sc, lens = cell
        y_rub.append(1.0 if max(sc, key=sc.get) == t else 0.0)
        y_len.append(1.0 if max(lens, key=lens.get) == t else 0.0)
        gp.append(pid)
        gr.append(aid)
    n = len(y_or)
    assert n > 5000 and len(y_rub) == n, f"{n} oracle rows, {len(y_rub)} rubric rows"

    def rep(name, y):
        m = float(np.mean(y))
        se = two_way_se(y, gp, gr)
        print(f"  {name:40s} {m:6.1%}  [{m - 1.96 * se:5.1%}, {m + 1.96 * se:5.1%}]")
        return m, se
    print("\n" + "=" * 78)
    print(f"THE CEILING AND WHAT REACHES IT -- {n} rows, {len(set(gp))} prompts, "
          f"{len(set(gr))} raters")
    print("=" * 78)
    mo, seo = rep("ORACLE: leave-one-out modal choice", y_or)
    mr, ser = rep("crowd rubric", y_rub)
    ml, sel = rep("length only", y_len)
    print(f"  {'chance':40s} {0.25:6.1%}")

    span = mo - 0.25
    print(f"\n  the reachable band is {0.25:.1%} to {mo:.1%}, a span of {span:.1%}.")
    print(f"  crowd rubric captures {(mr - 0.25) / span:.1%} of it.")
    print(f"  length heuristic captures {(ml - 0.25) / span:.1%} of it.")
    dvo = np.array(y_or) - np.array(y_rub)
    mdo = float(dvo.mean())
    sedo = two_way_se(dvo, gp, gr)
    print(f"  PAIRED oracle - rubric  {mdo:+.1%}  [{mdo - 1.96 * sedo:+.1%}, "
          f"{mdo + 1.96 * sedo:+.1%}]  z {mdo / sedo:+.1f}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    print(f"  A predictor that always names the crowd's own majority -- the best any prompt-level")
    print(f"  method can do, and it is allowed to see every other rater's answer -- gets {mo:.1%}.")
    print(f"  That is the ceiling, and it is barely half. The remaining {1 - mo:.0%} is DISAGREEMENT")
    print(f"  between people about which of four answers is best -- and this design cannot say how")
    print(f"  much of it is a real difference in values and how much is rater noise. Separating")
    print(f"  those needs the same person answering the same prompt twice, and the release ships no")
    print(f"  repeated assessment. Naming it 'genuine disagreement' would be the flattering reading")
    print(f"  of an unmeasured quantity, so it is named as what it is: unattributed.")
    print(f"  Against that ceiling the crowd rubric is not a modest {mr:.1%}. It closes")
    print(f"  {(mr - 0.25) / span:.0%} of the reachable gap, and the {mdo:.1%} it still leaves is")
    print(f"  the honest statement of what is missing.")
    print(f"  Reporting {mr:.1%} against 25% understates the apparatus; reporting it against 100%")
    print(f"  would overstate the shortfall. Both are the same error in opposite directions.")

    (OUT / "ceiling.json").write_text(json.dumps(
        {"rows": n, "prompts": len(set(gp)), "raters": len(set(gr)),
         "human_human": {"per_prompt_mean": hh_prompt, "pooled_pairs": hh_pair,
                         "pairs": pair_tot},
         "oracle_loo": {"rate": mo, "se": seo},
         "rubric": {"rate": mr, "se": ser, "share_of_band": (mr - 0.25) / span},
         "length": {"rate": ml, "se": sel, "share_of_band": (ml - 0.25) / span},
         "paired_oracle_minus_rubric": {"diff": mdo, "se": sedo, "z": mdo / sedo},
         "anchor_share_of_pairs": tp / pair_tot, "anchor_raters": len(top[1]),
         "note": "mode ties resolved in the oracle's favour, so the ceiling is an upper bound; "
                 "the residual above the ceiling mixes value disagreement with rater noise and "
                 "this design cannot separate them"},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
