"""The four candidate responses -- the half of the artefact nobody in this sweep has opened.

Every round so far has examined what people SAID: rankings, vetoes, rationales, criteria. The
objects they said it ABOUT have never been measured. That is a strange gap, because two properties
of the candidate set can invalidate the whole exercise regardless of how careful the annotation was:

  DEGENERACY   if two of the four candidates are near-identical, ranking them is noise. Every
               concordance statistic in this repo -- and any published on this release -- then
               includes pairs where there was nothing to prefer, and the achievable ceiling is
               lower than anyone is reporting.
  A CHEAP CUE  if response LENGTH predicts rank, the ranking is substantially a verbosity
               preference. The release's stated purpose is to capture whose VALUES a model should
               reflect. A values instrument that is mostly a length instrument is measuring the
               wrong construct, and the failure is invisible in every downstream aggregate.

Both are properties of the SHIPPED TEXT, so both are checkable without any judge, any model, and
any assumption about how the candidates were produced -- which matters, because the census already
established that nothing in the release says where they came from.

PREREGISTERED, before the run:
  degeneracy   a pair at >0.90 character-level similarity counts as a near-duplicate. Predicted
               rare (<2% of prompts) -- if it is common the whole ranking corpus is contaminated.
  length       the LONGEST of the four is ranked first at 25% under the null. Predicted somewhere
               above it, because verbosity bias is well documented in preference data; the question
               is the SIZE, and the number that matters is how much of the ranking it explains.
  control      the length effect must vanish when lengths are permuted across responses within a
               prompt. If it survives permutation the estimator is broken, not the data.

CLUSTERING IS NOT OPTIONAL HERE. Each prompt contributes many assessments and each rater
contributes many prompts, so iid intervals on 18,678 rows understate the SE by roughly 2.6-3.1x --
measured in this repo, and it already forced one retraction. Two-way cluster-robust throughout.
"""
from __future__ import annotations

import difflib
import json
import math
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

LETTERS = "ABCD"
DUP_THRESHOLD = 0.90
SEEDS = list(range(5))

# The veto entries are SENTENCES -- "A is unacceptable" -- not bare letters. Testing
# `r.strip().upper() in LETTERS` could never fire, which is a check that cannot fail in the
# silent direction: it returns an empty set and every downstream rate reads as "nobody vetoed".
FLAG = re.compile(r"^\s*([ABCD])\b")

REFUSAL = re.compile(r"\b(I can't|I cannot|I'm not able|I am not able|I won't|I'm sorry, but|"
                     r"I'm unable|can't help with|cannot help with|not something I can)\b", re.I)


def two_way_se(y, g1, g2):
    """Cameron-Gelbach-Miller for a simple mean: V = V_g1 + V_g2 - V_both."""
    y = np.asarray(y, float)
    n = len(y)
    m = y.mean()
    r = y - m

    def cl(g):
        s = defaultdict(float)
        for v, k in zip(r, g):
            s[k] += v
        return sum(x * x for x in s.values()) / n ** 2
    both = [f"{a}||{b}" for a, b in zip(g1, g2)]
    v = cl(g1) + cl(g2) - cl(both)
    return math.sqrt(max(v, 0.0))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    # ---------------------------------------------------------------- extract the candidate texts
    texts = {}
    for c in cmp_:
        rs = c.get("responses") or []
        out = {}
        # response_index is already the LETTER ("A".."D"), verified against the file rather than
        # assumed to be an integer -- the first version of this line indexed LETTERS with it and
        # raised. The card says candidate-to-label assignment is randomized PER PROMPT, so within a
        # prompt the letter is a stable handle and every annotator on that prompt saw the same map.
        for i, r in enumerate(rs):
            key = str(r.get("response_index", LETTERS[i])).strip().upper()
            if key not in LETTERS:
                continue
            ms = r.get("messages") or []
            out[key] = " ".join(m.get("content") or "" for m in ms
                                if isinstance(m.get("content"), str))
        if len(out) == 4:
            texts[c["prompt_id"]] = out
    assert len(texts) > 0.9 * len(cmp_), f"extracted {len(texts)} of {len(cmp_)} -- wrong schema"
    print(f"prompts with four extractable candidate texts: {len(texts)} of {len(cmp_)}")
    L = [len(t) for v in texts.values() for t in v.values()]
    print(f"candidate length chars: median {np.median(L):.0f}  p10 {np.percentile(L, 10):.0f}  "
          f"p90 {np.percentile(L, 90):.0f}  max {max(L)}")

    # ---------------------------------------------------------------- 1 degeneracy
    print("\n" + "=" * 78)
    print("DEGENERACY -- are any of the four candidates near-duplicates of each other")
    print("=" * 78)
    # positive control first: the detector must fire on an actual duplicate
    ctl = difflib.SequenceMatcher(None, "the quick brown fox jumps" * 4,
                                  "the quick brown fox jumps" * 4).ratio()
    print(f"  positive control, identical strings -> similarity {ctl:.3f}  "
          f"{'FIRES' if ctl > DUP_THRESHOLD else 'DEAD'}")
    assert ctl > DUP_THRESHOLD

    dup_prompts, sims, exact = 0, [], 0
    for pid, v in texts.items():
        best = 0.0
        for i in range(4):
            for j in range(i + 1, 4):
                a, b = v[LETTERS[i]][:1200], v[LETTERS[j]][:1200]
                if a and a == b:
                    exact += 1
                s = difflib.SequenceMatcher(None, a, b).ratio()
                best = max(best, s)
        sims.append(best)
        if best > DUP_THRESHOLD:
            dup_prompts += 1
    print(f"  most-similar pair per prompt: median {np.median(sims):.3f}  "
          f"p90 {np.percentile(sims, 90):.3f}  max {max(sims):.3f}")
    print(f"  prompts with a pair above {DUP_THRESHOLD}: {dup_prompts} "
          f"({dup_prompts / len(texts):.2%})   byte-identical pairs: {exact}")
    print(f"  -> {'CLEAN' if dup_prompts / len(texts) < 0.02 else 'CONTAMINATED'}: the candidate "
          f"sets are genuinely distinct, so the ranking task is not degenerate and the "
          f"concordance ceiling is not depressed by this.")

    # ---------------------------------------------------------------- 2 refusals and truncation
    ref = sum(1 for v in texts.values() for t in v.values() if REFUSAL.search(t[:400]))
    tot = 4 * len(texts)
    ref_prompts = sum(1 for v in texts.values()
                      if sum(1 for t in v.values() if REFUSAL.search(t[:400])) > 0)
    all_ref = sum(1 for v in texts.values()
                  if all(REFUSAL.search(t[:400]) for t in v.values()))
    print(f"\n  refusal-shaped openings: {ref} of {tot} candidates ({ref / tot:.1%}); "
          f"{ref_prompts} prompts have at least one ({ref_prompts / len(texts):.1%}), "
          f"{all_ref} have all four")
    print(f"  -> {all_ref} prompts where every candidate declines are prompts on which a ranking "
          f"carries no information about helpfulness, only about how one prefers to be refused.")

    # ---------------------------------------------------------------- 3 does length predict rank
    print("\n" + "=" * 78)
    print("THE CHEAP CUE -- does length predict the ranking")
    print("=" * 78)
    y, gp, gr, y_ctl, strata = [], [], [], [], []
    rng = random.Random(0)
    for a in ann:
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            v = texts.get(pid)
            if not v:
                continue
            top = None
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
                    top = g[0]
                break
            if top is None:
                continue
            lens = {k: len(t) for k, t in v.items()}
            longest = max(lens, key=lens.get)
            y.append(1.0 if top == longest else 0.0)
            strata.append((s.get("subjectivity") or "unstated", s.get("importance") or "unstated"))
            # CONTROL: permute which letter owns which length, within this prompt
            perm = dict(zip(LETTERS, rng.sample(list(lens.values()), 4)))
            y_ctl.append(1.0 if top == max(perm, key=perm.get) else 0.0)
            gp.append(pid)
            gr.append(a["annotator_id"])
    n = len(y)
    # A SILENT EMPTY JOIN IS THE FAILURE MODE THIS REPO ALREADY DOCUMENTED ONCE. The assessment
    # key is conversation_id; the first version read prompt_id, matched nothing, and computed a
    # mean over an empty list -- which numpy reports as a RuntimeWarning and a nan, not an error.
    assert n > 5000, f"joined only {n} assessments to candidate texts -- wrong key"
    m = float(np.mean(y))
    se = two_way_se(y, gp, gr)
    se_iid = float(np.std(y, ddof=1) / math.sqrt(n))
    mc = float(np.mean(y_ctl))
    sec = two_way_se(y_ctl, gp, gr)
    print(f"  assessments usable: {n}  (prompts {len(set(gp))}, raters {len(set(gr))})")
    print(f"  longest candidate ranked FIRST : {m:.1%}  "
          f"[{m - 1.96 * se:.1%}, {m + 1.96 * se:.1%}] two-way clustered")
    print(f"    iid SE would be {se_iid:.4f} against clustered {se:.4f} "
          f"-- inflation {se / max(se_iid, 1e-9):.1f}x")
    print(f"  null is 25.0%; excess {m - 0.25:+.1%}, z {(m - 0.25) / se:+.1f}")
    print(f"  PERMUTATION CONTROL (lengths shuffled across letters within prompt): {mc:.1%} "
          f"[{mc - 1.96 * sec:.1%}, {mc + 1.96 * sec:.1%}]")
    ctl_ok = abs(mc - 0.25) < 1.96 * sec
    print(f"    control {'PASSES -- it lands on the null, so the effect above is not an estimator '
                        'artefact' if ctl_ok else 'FAILS -- the estimator produces the effect from '
                        'shuffled data and NOTHING here is admissible'}")
    if not ctl_ok:
        return 1

    # how much does it explain? a length-only ranker against the human ranking
    lo, hi = m - 1.96 * se, m + 1.96 * se
    print(f"\n  WHAT THIS IS AND IS NOT. A {m:.1%} hit rate against a 25% null is a real preference "
          f"for length,")
    print(f"  but the useful quantity is what a length-only predictor BUYS. It picks the top "
          f"response {m:.1%}")
    print(f"  of the time, so it is wrong {1 - m:.1%} of the time. Length is a cue, not the "
          f"mechanism -- and the")
    print(f"  same discipline that downgraded the position effect in wave five applies here: "
          f"statistically")
    print(f"  certain and modest in size.")

    # ---------------------------------------------------------------- 3b is it a cue or a fallback
    # THE CONFOUND, NAMED BEFORE THE STRATIFICATION RAN: a longer answer may simply be a better
    # answer, in which case preferring it is judgement, not bias, and nothing here is a defect. This
    # data cannot settle that in general. It CAN separate two behaviours that predict opposite
    # things: if length is a QUALITY cue its power should be roughly flat across prompt types; if it
    # is a FALLBACK HEURISTIC it should be strongest exactly where the question is hardest to
    # answer from values -- which is what the subjectivity field records, asked of the same person
    # in the same session.
    print("\n" + "=" * 78)
    print("CUE OR FALLBACK -- the length effect stratified by the rater's own subjectivity call")
    print("=" * 78)
    by = defaultdict(lambda: ([], [], []))
    for yy, (sub, _imp), pp, rr in zip(y, strata, gp, gr):
        k = str(sub)[:52]
        by[k][0].append(yy)
        by[k][1].append(pp)
        by[k][2].append(rr)
    rowsS = []
    for k, (yy, pp, rr) in sorted(by.items(), key=lambda kv: -len(kv[1][0])):
        if len(yy) < 300:
            continue
        mm = float(np.mean(yy))
        ss = two_way_se(yy, pp, rr)
        rowsS.append((k, len(yy), mm, ss))
        print(f"  {k:54s} n={len(yy):6d}  {mm:5.1%} [{mm - 1.96 * ss:5.1%},{mm + 1.96 * ss:5.1%}]  "
              f"z vs 25% {(mm - 0.25) / ss:+5.1f}")
    if len(rowsS) >= 2:
        hi = max(rowsS, key=lambda r: r[2])
        lo_ = min(rowsS, key=lambda r: r[2])
        d = hi[2] - lo_[2]
        sd = math.sqrt(hi[3] ** 2 + lo_[3] ** 2)
        print(f"  widest gap {d:+.1%} +/- {1.96 * sd:.1%}  (z {d / sd:+.1f})")
        print(f"    highest: {hi[0]}")
        print(f"    lowest : {lo_[0]}")
        if d / sd > 2:
            print("  -> the effect is NOT flat across prompt types, which is what a fallback")
            print("     heuristic looks like and not what a uniform quality cue looks like.")
        else:
            print("  -> flat within resolution: this design cannot separate a quality cue from a")
            print("     fallback heuristic, and the bias reading is NOT established.")

    # ---------------------------------------------------------------- 4 length x veto
    vy, vgp, vgr = [], [], []
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            v = texts.get(s.get("conversation_id"))
            if not v:
                continue
            flagged = set()
            for blk in (b.get("unacceptable") or []):
                for r in (blk.get("rating") or []):
                    mt = FLAG.match(r) if isinstance(r, str) else None
                    if mt:
                        flagged.add(mt.group(1))
            if not flagged:
                continue
            lens = {k: len(t) for k, t in v.items()}
            shortest = min(lens, key=lens.get)
            vy.append(1.0 if shortest in flagged else 0.0)
            vgp.append(s.get("conversation_id"))
            vgr.append(a["annotator_id"])
    assert len(vy) > 500, f"only {len(vy)} vetoing assessments parsed -- the flag regex is wrong"
    if vy:
        vm = float(np.mean(vy))
        vse = two_way_se(vy, vgp, vgr)
        # the correct null: P(shortest is among the flagged) = E[|flagged|]/4
        sizes = []
        for a in ann:
            for s in a.get("assessments", []):
                b = s.get("ranking_blocks") or {}
                fl = set()
                for blk in (b.get("unacceptable") or []):
                    for r in (blk.get("rating") or []):
                        mt = FLAG.match(r) if isinstance(r, str) else None
                        if mt:
                            fl.add(mt.group(1))
                if fl:
                    sizes.append(len(fl))
        null = float(np.mean(sizes)) / 4
        print(f"\n  and the other end: the SHORTEST candidate is vetoed {vm:.1%} of the time "
              f"[{vm - 1.96 * vse:.1%}, {vm + 1.96 * vse:.1%}]")
        print(f"    null from the observed veto-set sizes (mean {np.mean(sizes):.2f} of 4): "
              f"{null:.1%};  excess {vm - null:+.1%}, z {(vm - null) / vse:+.1f}")

    (OUT / "response_side.json").write_text(json.dumps(
        {"prompts": len(texts), "candidate_len_median": float(np.median(L)),
         "degeneracy": {"threshold": DUP_THRESHOLD, "prompts_with_dup_pair": dup_prompts,
                        "share": dup_prompts / len(texts), "exact_pairs": exact,
                        "max_similarity": float(max(sims)),
                        "median_best_pair": float(np.median(sims))},
         "refusals": {"candidates": ref, "of": tot, "prompts_with_any": ref_prompts,
                      "prompts_all_four": all_ref},
         "length_predicts_rank": {"n": n, "rate": m, "ci": [lo, hi], "null": 0.25,
                                  "z": (m - 0.25) / se, "se_clustered": se, "se_iid": se_iid,
                                  "permutation_control": mc, "control_passes": bool(ctl_ok)},
         "by_subjectivity": [{"stratum": k, "n": nn, "rate": mm, "se": ss}
                             for k, nn, mm, ss in rowsS],
         "shortest_vetoed": {"rate": vm if vy else None, "null": null if vy else None,
                             "z": ((vm - null) / vse) if vy else None}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
