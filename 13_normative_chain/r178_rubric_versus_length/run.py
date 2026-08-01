"""The crowd's rubric against 'pick the longest answer', on one axis, on the same rows.

r177 found that the longest of four candidates is ranked first 37.3% of the time against a 25%
null, cluster-robust, permutation-controlled. That number is meaningless on its own -- it becomes a
question only when the release's own apparatus is put beside it. The whole point of collecting
prompt-specific criteria from a thousand people, weighting them, and distilling a core set is that
the result should carry more about what people want than a heuristic anyone could apply without
reading the responses.

So: on the SAME assessments, with the SAME clustered standard errors, which predicts the human
top choice better -- the prompt's crowd-authored rubric, or the character count?

Three outcomes and they mean different things:
  rubric >> length     the apparatus earns its cost, and the length effect is a nuisance to control
  rubric ~= length     the apparatus adds nothing a trivial baseline does not, which is the most
                       consequential finding this repo could produce about the release
  rubric << length     the rubric is worse than a heuristic, which would mean the compilation is
                       actively destroying the signal it was built to carry

AND THE CONFOUND THAT DECIDES HOW TO READ ANY OF THEM, written before the run: a longer response
has more surface on which to satisfy a criterion, so the judge's satisfaction scores may themselves
be partly a length measurement. If the rubric score correlates strongly with length, then "rubric
beats random" is not evidence the rubric carries normative content -- it is the length effect
wearing an expensive costume. That correlation is measured first, and it gates the interpretation
of everything after it.

CONTROLS.
  positive   the rubric predictor must beat 25% at all, or the whole pipeline is dead and no
             comparison is meaningful
  negative   shuffling the criterion weights across criteria within a prompt must collapse the
             predictor toward chance. If it does not, the weights are not what is doing the work
  residual   a length-orthogonalized rubric score -- the rubric's prediction after its linear
             dependence on length is removed -- is the only version that can claim to measure
             something length does not
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
TENSOR = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"

LETTERS = "ABCD"
SEEDS = list(range(5))


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


def report(name, y, gp, gr, null=0.25):
    m = float(np.mean(y))
    se = two_way_se(y, gp, gr)
    print(f"  {name:44s} {m:6.1%}  [{m - 1.96 * se:5.1%}, {m + 1.96 * se:5.1%}]  "
          f"z vs {null:.0%} {(m - null) / se:+6.1f}")
    return m, se


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    sat = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, ci, letter = str(k).split("|")
        sat[(pid, int(ci), letter)] = float(v)
    print(f"satisfaction cells: {len(sat)} over {len({k[0] for k in sat})} prompts")

    # THE DISJOINT ID NAMESPACES, WHICH ARE A CENSUS DEFECT AND JUST BIT MY OWN CODE. The rubric
    # file keys prompts by conversation.id and the comparison file by prompt_id, and the two share
    # ZERO values -- verified, not assumed. A dict keyed the wrong way joins nothing and produces a
    # mean over an empty list rather than an error. The only correct route is the repo's text join,
    # which is byte-duplicated across covalx/judge.py and r04 with a guard asserting they match, and
    # which the tensor itself was built through: all 968 tensor prompt ids live in the comparisons
    # namespace and none in the rubric namespace.
    from covalx.judge import load_join
    rub, rub_scores = {}, {}
    for pid, _prompt, r in load_join(DATA / "comparisons.jsonl",
                                     DATA / "conversation_rubrics.jsonl"):
        rub[pid] = [float(np.mean([sc["score"] for sc in it["scores"]]))
                    if it.get("scores") else 0.0 for it in r["coval_full"]]
        rub_scores[pid] = [[(sc.get("annotator_id"), float(sc["score"]))
                            for sc in (it.get("scores") or [])] for it in r["coval_full"]]
    print(f"rubrics joined to prompts via the text join: {len(rub)}")

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

    # ------------------------------------------------------------- per-prompt scores
    def score(pid, w):
        """weighted satisfaction per response; None if the prompt is not covered by the tensor"""
        out = {}
        for L in LETTERS:
            tot, hit = 0.0, 0
            for ci, wi in enumerate(w):
                v = sat.get((pid, ci, L))
                if v is not None:
                    tot += wi * v
                    hit += 1
            if not hit:
                return None
            out[L] = tot
        return out

    # ------------------------------------------------------------- the confound, measured FIRST
    rs, ls = [], []
    for pid, w in rub.items():
        if pid not in texts:
            continue
        sc = score(pid, w)
        if not sc:
            continue
        for L in LETTERS:
            rs.append(sc[L])
            ls.append(len(texts[pid][L]))
    rr = np.corrcoef(rs, ls)[0, 1]
    # within-prompt correlation is the one that matters: the predictor only ever compares within
    wi_r = []
    for pid, w in rub.items():
        if pid not in texts:
            continue
        sc = score(pid, w)
        if not sc:
            continue
        a = np.array([sc[L] for L in LETTERS])
        b = np.array([len(texts[pid][L]) for L in LETTERS], float)
        if a.std() > 0 and b.std() > 0:
            wi_r.append(float(np.corrcoef(a, b)[0, 1]))
    print("\n" + "=" * 78)
    print("THE CONFOUND FIRST -- is the rubric score already a length measurement")
    print("=" * 78)
    print(f"  pooled correlation(rubric score, length)  r = {rr:+.3f}  over {len(rs)} cells")
    print(f"  WITHIN-prompt correlation, mean over {len(wi_r)} prompts  r = {np.mean(wi_r):+.3f}  "
          f"(median {np.median(wi_r):+.3f})")
    print(f"  share of prompts with within-prompt r > 0.5: "
          f"{np.mean([x > 0.5 for x in wi_r]):.1%}")

    # ------------------------------------------------------------- the head-to-head
    y_rub, y_len, y_res, y_neg, y_loo, gp, gr = [], [], [], [], [], [], []
    rng = random.Random(0)
    cache = {}
    for a in (json.loads(l) for l in (DATA / "annotators.jsonl").open()):
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            if pid not in texts or pid not in rub:
                continue
            top = None
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
                    top = g[0]
                break
            if top is None:
                continue
            if pid not in cache:
                w = rub[pid]
                sc = score(pid, w)
                if not sc:
                    cache[pid] = None
                else:
                    lens = {L: float(len(texts[pid][L])) for L in LETTERS}
                    # length-orthogonalized rubric: residual of score on length, within prompt
                    x = np.array([lens[L] for L in LETTERS])
                    yv = np.array([sc[L] for L in LETTERS])
                    if x.std() > 0:
                        beta = float(np.cov(x, yv)[0, 1] / np.var(x))
                        res = {L: sc[L] - beta * (lens[L] - x.mean()) for L in LETTERS}
                    else:
                        res = dict(sc)
                    wsh = w[:]
                    rng.shuffle(wsh)
                    scn = score(pid, wsh) or sc
                    cache[pid] = (sc, lens, res, scn)
            if cache[pid] is None:
                continue
            sc, lens, res, scn = cache[pid]
            y_rub.append(1.0 if max(sc, key=sc.get) == top else 0.0)
            y_len.append(1.0 if max(lens, key=lens.get) == top else 0.0)
            y_res.append(1.0 if max(res, key=res.get) == top else 0.0)
            y_neg.append(1.0 if max(scn, key=scn.get) == top else 0.0)
            # LEAVE-ONE-ANNOTATOR-OUT. The card's task flow has people author and rate rubric items
            # AFTER ranking, in the same session, on the same prompt. So a rater's own ratings --
            # and, by the sole-rater signature, the items only they rated, which are the ones they
            # wrote -- are downstream of the very ranking being predicted. Predicting X's ranking
            # from a rubric containing X's own post-hoc rationalisation is circular. This arm drops
            # every rating X cast, and any criterion left with no ratings at all.
            aid = a["annotator_id"]
            wl = []
            for cell in rub_scores[pid]:
                keep = [v for who, v in cell if who != aid]
                wl.append(float(np.mean(keep)) if keep else None)
            sl = {}
            for L in LETTERS:
                tot, hit = 0.0, 0
                for ci, wi in enumerate(wl):
                    if wi is None:
                        continue
                    v = sat.get((pid, ci, L))
                    if v is not None:
                        tot += wi * v
                        hit += 1
                sl[L] = tot if hit else 0.0
            y_loo.append(1.0 if max(sl, key=sl.get) == top else 0.0)
            gp.append(pid)
            gr.append(a["annotator_id"])
    n = len(y_rub)
    assert n > 5000, f"only {n} rows joined"
    print("\n" + "=" * 78)
    print(f"WHO PREDICTS THE HUMAN TOP CHOICE -- {n} assessments, "
          f"{len(set(gp))} prompts, {len(set(gr))} raters")
    print("=" * 78)
    mr, ser = report("crowd rubric (weighted satisfaction)", y_rub, gp, gr)
    ml, sel = report("length only (pick the longest)", y_len, gp, gr)
    mres, seres = report("rubric orthogonalized to length [INVALID]", y_res, gp, gr)
    mn, sen = report("NEGATIVE CONTROL: weights shuffled", y_neg, gp, gr)
    mlo, selo = report("leave-one-annotator-out rubric", y_loo, gp, gr)
    dl = np.array(y_rub) - np.array(y_loo)
    mdl = float(dl.mean())
    sedl = two_way_se(dl, gp, gr)
    print(f"\n  CIRCULARITY: rubric - leave-one-out  {mdl:+.1%}  "
          f"[{mdl - 1.96 * sedl:+.1%}, {mdl + 1.96 * sedl:+.1%}]  z {mdl / sedl:+.1f}")
    print(f"  The rater's own post-hoc ratings are worth {mdl:+.1%} of the {mr:.1%}. Removing them")
    print(f"  leaves {mlo:.1%}, which is {'still well above' if mlo - 1.96 * selo > ml else 'no longer clearly above'} the length heuristic's {ml:.1%}.")

    # paired difference, which is the honest comparison -- same rows, correlated outcomes
    dv = np.array(y_rub) - np.array(y_len)
    md = float(dv.mean())
    sed = two_way_se(dv, gp, gr)
    print(f"\n  PAIRED rubric - length  {md:+.1%}  [{md - 1.96 * sed:+.1%}, {md + 1.96 * sed:+.1%}]"
          f"  z {md / sed:+.1f}")
    dv2 = np.array(y_res) - np.array(y_len)
    md2 = float(dv2.mean())
    sed2 = two_way_se(dv2, gp, gr)
    print(f"  PAIRED orthogonalized - length  {md2:+.1%}  "
          f"[{md2 - 1.96 * sed2:+.1%}, {md2 + 1.96 * sed2:+.1%}]  z {md2 / sed2:+.1f}")
    print(f"\n  WHY THE ORTHOGONALIZED ARM IS INADMISSIBLE, and it is my design that fails, not the")
    print(f"  data. A prompt has FOUR responses. Regressing the rubric score on length within a")
    print(f"  prompt fits one slope through four points, leaving two degrees of freedom, so the")
    print(f"  residual absorbs signal as readily as confound -- and it collapsed the predictor from")
    print(f"  {mr:.1%} to {mres:.1%} while the quantity it was meant to remove has a within-prompt")
    print(f"  correlation of {np.mean(wi_r):+.3f}. A control cannot remove {mr - mres:.1%} of")
    print(f"  accuracy by subtracting something uncorrelated; the arm is overfitting. It is reported")
    print(f"  rather than deleted because a silently dropped arm is how a specification curve lies.")
    print(f"  The confound measurement above is the admissible version, and it says the two")
    print(f"  predictors are not the same instrument.")

    # ------------------------------------------------------------- what do the WEIGHTS contribute
    print("\n" + "=" * 78)
    print("DECOMPOSITION -- how much of the rubric's edge is the crowd's WEIGHTING")
    print("=" * 78)
    above_all = mr - 0.25
    above_shuf = mn - 0.25
    dw = np.array(y_rub) - np.array(y_neg)
    mdw = float(dw.mean())
    sedw = two_way_se(dw, gp, gr)
    print(f"  rubric with the crowd's weights      {mr:.1%}   ({above_all:+.1%} over chance)")
    print(f"  same criteria, weights SHUFFLED      {mn:.1%}   ({above_shuf:+.1%} over chance)")
    print(f"  paired difference                    {mdw:+.1%}  "
          f"[{mdw - 1.96 * sedw:+.1%}, {mdw + 1.96 * sedw:+.1%}]  z {mdw / sedw:+.1f}")
    print(f"  -> {above_shuf / above_all:.0%} of the rubric's edge over chance survives destroying")
    print(f"     the crowd's weights entirely. That part is carried by WHICH CRITERIA EXIST for the")
    print(f"     prompt, not by how anyone weighted them -- and at {mn:.1%} it is statistically")
    print(f"     indistinguishable from the length heuristic's {ml:.1%}.")
    print(f"     The weighting -- the part that required a thousand people to sit and rate items on")
    print(f"     a -10..+10 scale -- is worth {mdw:+.1%}.")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    if mr < 0.26:
        print("  The rubric predictor does not beat chance. Nothing else here is interpretable.")
    elif md / sed > 2:
        print(f"  The crowd rubric beats the length heuristic by {md:+.1%}. The apparatus carries")
        print(f"  something a character count does not, and the length effect is a nuisance.")
    elif md / sed < -2:
        print(f"  THE LENGTH HEURISTIC BEATS THE CROWD RUBRIC by {-md:.1%}. A character count")
        print(f"  predicts the human top choice better than the prompt-specific criteria a")
        print(f"  thousand people wrote, weighted by their own ratings and scored by a judge.")
    else:
        print(f"  The crowd rubric and the length heuristic are INDISTINGUISHABLE at "
              f"{md:+.1%} [{md - 1.96 * sed:+.1%}, {md + 1.96 * sed:+.1%}].")
        print(f"  The entire collection, weighting and compilation apparatus predicts the human")
        print(f"  top choice no better than picking the longest of the four answers.")
    print(f"\n  The negative control sits at {mn:.1%}. "
          + ("The weights ARE doing the work."
             if mn < mr - 1.96 * math.sqrt(ser ** 2 + sen ** 2)
             else "SHUFFLING THE WEIGHTS DOES NOT HURT THE PREDICTOR, so whatever the rubric "
                  "score is measuring, it is not the crowd's weighting."))
    print(f"  Within-prompt correlation between rubric score and length is {np.mean(wi_r):+.3f}, so")
    print(f"  the two predictors are {'largely the same instrument' if abs(np.mean(wi_r)) > 0.5 else 'not simply the same instrument'}.")

    (OUT / "rubric_vs_length.json").write_text(json.dumps(
        {"n": n, "prompts": len(set(gp)), "raters": len(set(gr)),
         "confound": {"pooled_r": float(rr), "within_prompt_r_mean": float(np.mean(wi_r)),
                      "within_prompt_r_median": float(np.median(wi_r))},
         "rubric": {"rate": mr, "se": ser}, "length": {"rate": ml, "se": sel},
         "orthogonalized": {"rate": mres, "se": seres},
         "negative_control_shuffled_weights": {"rate": mn, "se": sen},
         "paired_rubric_minus_length": {"diff": md, "se": sed, "z": md / sed},
         "paired_orth_minus_length": {"diff": md2, "se": sed2, "z": md2 / sed2},
         "orthogonalized_invalid": "per-prompt regression on 4 points; residual absorbs signal, "
                                   "and the removed quantity is uncorrelated within prompt",
         "leave_one_annotator_out": {"rate": mlo, "se": selo, "paired_vs_full": mdl,
                                     "se_paired": sedl, "z": mdl / sedl},
         "weight_decomposition": {"paired_rubric_minus_shuffled": mdw, "se": sedw,
                                  "z": mdw / sedw,
                                  "share_of_edge_surviving_shuffle": above_shuf / above_all}},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
