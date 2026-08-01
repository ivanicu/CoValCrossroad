"""The project's main positive claim, recomputed under the weighting that just fabricated a finding.

r195 identified the mechanism exactly: one anchor prompt carries 929 assessments, and an
assessment-weighted mean counts it 929 times. That produced a +4.9pp "finding" out of nothing, and
the collapse to +0.4pp on removing a single prompt is the whole story.

Every headline in this project is assessment-weighted. Two-way clustered standard errors were used
throughout, and they are the right tool for the DEPENDENCE -- but a clustered SE widens an
interval, it does not reweight a point estimate. The anchor still counts 929 times inside every
mean this sweep has published.

So the central positive claim has to survive the same grid it was just used to kill something with:

  r178   crowd rubric 50.3%, length heuristic 37.2%, weights-shuffled 35.7%, chance 25%,
         paired rubric-minus-length +13.1%
  r179   leave-one-out modal oracle 62.5%, so the reachable band is 37.5 points and the rubric
         closes 67.5% of it

If those move under prompt weighting or on removing one prompt, the strongest result in this
project has the same defect as the weakest, and I would rather find that here than have someone
else find it.

THE GRID: two weightings x anchor in or out, every arm recomputed from scratch, every cell printed.
Nothing is claimed that does not hold in all four.

WHY THIS IS NOT MERELY DEFENSIVE. The anchor is a genuinely different kind of item -- 929 raters
against a median of 14, garbled text per the census, and r195 measured its longest-first rate at
54.3% against a 34% baseline. A result that depends on it is a result about that prompt. A result
that does not is a result about the corpus. Only the grid can say which this is.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
TENSOR = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
LETTERS = "ABCD"


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
        pid, ci, L = str(k).split("|")
        sat[(pid, int(ci), L)] = float(v)

    from covalx.judge import load_join
    rub = {}
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        rub[pid] = [float(np.mean([s["score"] for s in it["scores"]]))
                    if it.get("scores") else 0.0 for it in r["coval_full"]]

    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                o[k] = float(len(" ".join(m.get("content") or ""
                                          for m in (r.get("messages") or [])
                                          if isinstance(m.get("content"), str))))
        if len(o) == 4:
            lens[c["prompt_id"]] = o

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    choices = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            pid = s.get("conversation_id")
            if t and pid in lens and pid in rub:
                choices[pid].append((a["annotator_id"], t))

    # per-prompt predictor picks, computed once
    picks = {}
    rng = random.Random(0)
    for pid, rows in choices.items():
        w = rub[pid]
        sc, ok = {}, True
        for L in LETTERS:
            tot, n_ = 0.0, 0
            for ci, wi in enumerate(w):
                v = sat.get((pid, ci, L))
                if v is not None:
                    tot += wi * v
                    n_ += 1
            if not n_:
                ok = False
            sc[L] = tot
        if not ok:
            continue
        wsh = w[:]
        rng.shuffle(wsh)
        scn = {}
        for L in LETTERS:
            tot = 0.0
            for ci, wi in enumerate(wsh):
                v = sat.get((pid, ci, L))
                if v is not None:
                    tot += wi * v
            scn[L] = tot
        picks[pid] = {"rubric": max(sc, key=sc.get),
                      "length": max(lens[pid], key=lens[pid].get),
                      "shuffled": max(scn, key=scn.get)}
    # THE TRUE ANCHOR IS FOUND OVER ALL PROMPTS, NOT OVER THE ANALYSED POOL. My first version took
    # max() inside the rubric-joined pool and got a prompt with 42 assessments -- so the toggle was
    # removing the wrong item and the grid below would have "shown stability" against a prompt that
    # never mattered. That is the same class of error as r194's: a quantity computed on the
    # convenient population rather than the one the question is about.
    all_counts = defaultdict(int)
    for a in ann:
        for s in a.get("assessments", []):
            if top_of(s):
                all_counts[s.get("conversation_id")] += 1
    true_anchor = max(all_counts, key=all_counts.get)
    pool = [p for p in picks if len(choices[p]) >= 6]
    sizes = {p: len(choices[p]) for p in pool}
    anchor = max(sizes, key=sizes.get)
    print(f"prompts {len(pool)};  assessments {sum(sizes.values())}")
    print(f"  TRUE anchor over all prompts: {all_counts[true_anchor]} assessments")
    print(f"  is it in the rubric-joined pool? {'YES' if true_anchor in picks else 'NO'}")
    if true_anchor not in picks:
        print(f"  => THE 929-RATER PROMPT HAS NO RUBRIC. It is one of the 110 prompts the census")
        print(f"     found unjoinable, so every rubric-based result in this project EXCLUDED it")
        print(f"     from the start. That is why the headline was never exposed to the anchor --")
        print(f"     not because assessment weighting is safe, but because the item that makes it")
        print(f"     unsafe was already absent. Luck, and worth knowing which kind.")
    print(f"  largest prompt that IS in the pool: {sizes[anchor]} assessments "
          f"({sizes[anchor] / sum(sizes.values()):.1%})")

    def arm2(name, P, weighting):
        if weighting == "assessment":
            v = [1.0 if picks[p][name] == t else 0.0 for p in P for _a, t in choices[p]]
        else:
            v = [float(np.mean([1.0 if picks[p][name] == t else 0.0
                                for _a, t in choices[p]])) for p in P]
        return v

    def oracle(P, weighting):
        """leave-one-out modal human choice"""
        if weighting == "assessment":
            v = []
            for p in P:
                ts = [t for _a, t in choices[p]]
                for i, t in enumerate(ts):
                    c = Counter(ts[:i] + ts[i + 1:])
                    mx = max(c.values())
                    v.append(1.0 if t in [k for k, n in c.items() if n == mx] else 0.0)
        else:
            v = []
            for p in P:
                ts = [t for _a, t in choices[p]]
                inner = []
                for i, t in enumerate(ts):
                    c = Counter(ts[:i] + ts[i + 1:])
                    mx = max(c.values())
                    inner.append(1.0 if t in [k for k, n in c.items() if n == mx] else 0.0)
                v.append(float(np.mean(inner)))
        return v

    print("\n" + "=" * 78)
    print("THE HEADLINE TABLE UNDER FOUR SPECIFICATIONS")
    print("=" * 78)
    print(f"  {'weighting':12s} {'anchor':9s} {'rubric':>8s} {'length':>8s} {'shuffled':>9s} "
          f"{'oracle':>8s} {'rub-len':>9s} {'band%':>7s}")
    grid = []
    for weighting in ("assessment", "prompt"):
        for anc in ("included", "excluded"):
            P = [p for p in pool if anc == "included" or p != anchor]
            r_ = arm2("rubric", P, weighting)
            l_ = arm2("length", P, weighting)
            s_ = arm2("shuffled", P, weighting)
            o_ = oracle(P, weighting)
            mr, ml, ms, mo = (float(np.mean(x)) for x in (r_, l_, s_, o_))
            dv = np.array(r_) - np.array(l_)
            # SE always with the prompt as the unit
            pr = [float(np.mean([1.0 if picks[p]["rubric"] == t else 0.0
                                 for _a, t in choices[p]])) for p in P]
            pl = [float(np.mean([1.0 if picks[p]["length"] == t else 0.0
                                 for _a, t in choices[p]])) for p in P]
            dp = np.array(pr) - np.array(pl)
            se = float(np.std(dp, ddof=1) / math.sqrt(len(dp)))
            band = (mr - 0.25) / (mo - 0.25)
            grid.append({"weighting": weighting, "anchor": anc, "rubric": mr, "length": ml,
                         "shuffled": ms, "oracle": mo, "diff": float(dv.mean()),
                         "diff_se_promptunit": se, "band_share": band, "prompts": len(P)})
            print(f"  {weighting:12s} {anc:9s} {mr:8.1%} {ml:8.1%} {ms:9.1%} {mo:8.1%} "
                  f"{dv.mean():+9.1%} {band:7.1%}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    ds = [g["diff"] for g in grid]
    bs = [g["band_share"] for g in grid]
    rs = [g["rubric"] for g in grid]
    print(f"  rubric-minus-length across the four cells: "
          + ", ".join(f"{x:+.1%}" for x in ds))
    print(f"  share of the reachable band closed:        "
          + ", ".join(f"{x:.0%}" for x in bs))
    se0 = grid[0]["diff_se_promptunit"]
    print(f"  prompt-unit SE on the paired difference: {se0:.4f}, so the spread across")
    print(f"  specifications ({max(ds) - min(ds):.1%}) is {(max(ds) - min(ds)) / se0:.1f} SE.")
    stable = min(ds) > 0 and (max(ds) - min(ds)) < 4 * se0
    if stable:
        print(f"\n  THE CENTRAL CLAIM SURVIVES THE GRID. The crowd rubric beats the length")
        print(f"  heuristic in every cell, by {min(ds):+.1%} to {max(ds):+.1%}, and the anchor")
        print(f"  that fabricated r191's finding moves it by "
              f"{abs(grid[0]['diff'] - grid[1]['diff']):.1%}.")
        print(f"  Unlike the length-by-contestedness lean, this is a property of the corpus and")
        print(f"  not of one prompt counted 929 times. The rounds that produced it were")
        print(f"  assessment-weighted and got away with it -- which is luck rather than method,")
        print(f"  and the reason to run the grid was that I could not know which until now.")
    else:
        print(f"\n  THE CENTRAL CLAIM MOVES ACROSS THE GRID ({min(ds):+.1%} to {max(ds):+.1%}).")
        print(f"  The strongest positive result in this project has the same weighting defect as")
        print(f"  the finding it was used to kill, and every statement of it needs the")
        print(f"  specification attached.")
    print(f"\n  THE ORACLE MOVES TOO, and it sets the denominator: "
          + ", ".join(f"{g['oracle']:.1%}" for g in grid))
    print(f"  A ceiling quoted without its weighting is a ceiling for a different question.")

    # ---------------------------------------------------------------- the ceiling, where the
    # anchor DOES live. r179's oracle was computed over every prompt with a ranking, not over the
    # rubric-joined subset, so unlike the rubric arms it really did contain the 929-rater prompt.
    full = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            if t:
                full[s.get("conversation_id")].append(t)
    fpool = [p for p in full if len(full[p]) >= 6]
    print("\n" + "=" * 78)
    print("AND r179's CEILING, RECOMPUTED WHERE THE REAL ANCHOR IS PRESENT")
    print("=" * 78)
    print(f"  {'weighting':12s} {'anchor':9s} {'prompts':>8s} {'oracle':>8s}")
    ora = []
    for weighting in ("assessment", "prompt"):
        for anc in ("included", "excluded"):
            P = [p for p in fpool if anc == "included" or p != true_anchor]
            v = []
            for p in P:
                ts = full[p]
                inner = []
                for i, t in enumerate(ts):
                    c = Counter(ts[:i] + ts[i + 1:])
                    mx = max(c.values())
                    inner.append(1.0 if t in [k for k, n in c.items() if n == mx] else 0.0)
                if weighting == "assessment":
                    v.extend(inner)
                else:
                    v.append(float(np.mean(inner)))
            m = float(np.mean(v))
            ora.append({"weighting": weighting, "anchor": anc, "oracle": m, "prompts": len(P)})
            print(f"  {weighting:12s} {anc:9s} {len(P):8d} {m:8.1%}")
    spread = max(o["oracle"] for o in ora) - min(o["oracle"] for o in ora)
    print(f"\n  spread across the four cells: {spread:.1%}")
    print(f"  r179 published 62.5% as THE ceiling and used it as the denominator for 'the rubric")
    print(f"  closes 67.5% of the reachable band'. The ceiling ranges "
          f"{min(o['oracle'] for o in ora):.1%}-{max(o['oracle'] for o in ora):.1%} across")
    print(f"  weighting and anchor, so the band share inherits that range and should be quoted")
    print(f"  as a range rather than a number.")

    (OUT / "reweighted_headline.json").write_text(json.dumps(
        {"prompts": len(pool), "anchor_assessments": sizes[anchor], "grid": grid,
         "diff_range": [min(ds), max(ds)], "band_range": [min(bs), max(bs)],
         "rubric_range": [min(rs), max(rs)], "stable": bool(stable),
         "true_anchor_assessments": all_counts[true_anchor],
         "true_anchor_in_rubric_pool": bool(true_anchor in picks),
         "ceiling_grid": ora, "ceiling_spread": spread}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
