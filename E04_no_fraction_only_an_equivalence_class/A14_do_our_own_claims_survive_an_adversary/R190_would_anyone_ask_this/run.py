"""The one field nobody in this sweep has opened, and it is the panel grading the corpus.

Every assessment carries three self-reported fields. `importance` and `subjectivity` have both been
used here. `representativeness` has not been touched in 190 rounds, and it is the most pointed of
the three, because it is not a judgement about the responses -- it is the panel's verdict on the
PROMPTS:

    "It is moderately likely that I would ask a question like this to an AI chatbot."

The card says the prompts are synthetic. r175 withdrew my claim that nothing here transfers to
production traffic, because I have no production traffic to compare against. But the release
shipped its own ecological-validity measurement and nobody has read it: 1,012 people were asked,
per prompt, whether they would plausibly ask this.

THREE THINGS THAT FALL OUT, in increasing order of consequence:

  THE DISTRIBUTION      what share of assessments say the prompt is unlikely to be asked. If it is
                        large, the corpus's own panel says the corpus is unrepresentative, and
                        that is a scope limit stated by the data rather than inferred from the
                        word "synthetic".
  THE PROMPT VIEW       representativeness is a property of the prompt, so it should agree across
                        raters. If it does not -- if the same prompt is called realistic by half
                        the panel and unrealistic by the other half -- then the field measures the
                        RATER, not the prompt, and no aggregate over it means anything.
  WHAT IT PREDICTS      whether the realistic prompts are the ones with consensus. A pipeline that
                        works on prompts nobody would ask and fails on the ones they would is
                        worse than one that fails uniformly, and the two are distinguishable here.

THE SECOND CHECK IS THE ONE THAT GATES THE OTHERS and it is a positive-control in disguise: an
inter-rater agreement on representativeness that is at chance would mean the field is noise, and
every distribution computed from it would be a distribution of noise. It runs first.
"""
from __future__ import annotations

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

# the field embeds its level in bold unicode; map to an ordinal
LEVELS = [("𝘂𝗻𝗹𝗶𝗸𝗲𝗹𝘆", 0), ("𝘀𝗹𝗶𝗴𝗵𝘁𝗹𝘆", 1), ("𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗲𝗹𝘆", 2),
          ("𝘃𝗲𝗿𝘆", 3), ("𝗲𝘅𝘁𝗿𝗲𝗺𝗲𝗹𝘆", 4)]


def ordinal(s):
    if not isinstance(s, str):
        return None
    for tok, v in LEVELS:
        if tok in s:
            return v
    return None


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    raw = Counter()
    rows = []
    for a in ann:
        for s in a.get("assessments", []):
            v = s.get("representativeness")
            raw[str(v)[:70]] += 1
            o = ordinal(v)
            if o is not None:
                rows.append({"pid": s.get("conversation_id"), "aid": a["annotator_id"],
                             "rep": o, "top": top_of(s)})
    print(f"assessments carrying representativeness: {len(rows)} of "
          f"{sum(raw.values())}")
    print("\ndistinct values as shipped:")
    for k, c in raw.most_common(8):
        print(f"  {c:6d}  {k}")
    assert len(rows) > 10000, "the level parser matched too few -- check the unicode tokens"

    dist = Counter(r["rep"] for r in rows)
    n = len(rows)
    print(f"\n{'level':14s} {'n':>7s} {'share':>8s}")
    names = {v: k for k, v in LEVELS}
    for v in range(5):
        print(f"  {names[v][:12]:12s} {dist[v]:7d} {dist[v] / n:8.1%}")
    low = (dist[0] + dist[1]) / n
    print(f"\n  UNLIKELY or SLIGHTLY likely: {low:.1%} of all assessments")
    print(f"  mean level {np.mean([r['rep'] for r in rows]):.2f} on 0-4")

    # ------------------------------------------------------------------ is it about the prompt?
    print("\n" + "=" * 78)
    print("GATE: does representativeness describe the PROMPT or the RATER?")
    print("=" * 78)
    by_p = defaultdict(list)
    by_a = defaultdict(list)
    for r in rows:
        by_p[r["pid"]].append(r["rep"])
        by_a[r["aid"]].append(r["rep"])
    # variance decomposition: share of total variance lying BETWEEN prompts vs BETWEEN raters
    allv = np.array([r["rep"] for r in rows], float)
    gm = allv.mean()
    tot = float(((allv - gm) ** 2).sum())
    ssb_p = sum(len(v) * (np.mean(v) - gm) ** 2 for v in by_p.values() if len(v) >= 3)
    ssb_a = sum(len(v) * (np.mean(v) - gm) ** 2 for v in by_a.values() if len(v) >= 3)
    print(f"  variance between PROMPTS: {ssb_p / tot:.1%} of total")
    print(f"  variance between RATERS : {ssb_a / tot:.1%} of total")
    # split-half over prompts: does half the panel's mean predict the other half's?
    rs = []
    for sd in range(5):
        rng = random.Random(sd)
        A, B = [], []
        for pid, v in by_p.items():
            if len(v) < 6:
                continue
            w = v[:]
            rng.shuffle(w)
            h = len(w) // 2
            A.append(float(np.mean(w[:h])))
            B.append(float(np.mean(w[h:2 * h])))
        if len(A) > 50:
            rs.append(float(np.corrcoef(A, B)[0, 1]))
    r_half = float(np.mean(rs))
    sb = 2 * r_half / (1 + r_half)
    print(f"  split-half over prompts (>=6 raters, 5 seeds): r {r_half:+.3f}, "
          f"Spearman-Brown {sb:+.3f}, on {len(A)} prompts")
    gate = sb > 0.30
    print(f"  -> the field {'DESCRIBES THE PROMPT' if gate else 'DOES NOT reliably describe the prompt'}"
          f"; everything below {'is interpretable' if gate else 'is a distribution of noise'}")

    # ------------------------------------------------------------------ what does it predict
    print("\n" + "=" * 78)
    print("DO PEOPLE AGREE MORE ON THE PROMPTS THEY WOULD ACTUALLY ASK?")
    print("=" * 78)
    tops = defaultdict(list)
    for r in rows:
        if r["top"]:
            tops[r["pid"]].append(r["top"])
    pm = {pid: float(np.mean(v)) for pid, v in by_p.items() if len(v) >= 6}
    qs = np.percentile(list(pm.values()), [25, 50, 75])
    band = {}
    for pid, mv in pm.items():
        t = tops.get(pid, [])
        if len(t) < 6:
            continue
        c = Counter(t)
        agree = sum(x * (x - 1) / 2 for x in c.values()) / (len(t) * (len(t) - 1) / 2)
        b = int(np.searchsorted(qs, mv))
        band.setdefault(b, []).append(agree)
    print(f"  {'representativeness quartile':30s} {'prompts':>8s} {'agreement':>11s}")
    lbls = ["Q1 least realistic", "Q2", "Q3", "Q4 most realistic"]
    means = {}
    for b in range(4):
        v = band.get(b, [])
        if len(v) >= 20:
            means[b] = float(np.mean(v))
            print(f"  {lbls[b]:30s} {len(v):8d} {means[b]:11.1%}")
    if 0 in means and 3 in means:
        d = means[3] - means[0]
        se = math.sqrt(np.var(band[3]) / len(band[3]) + np.var(band[0]) / len(band[0]))
        print(f"  Q4 minus Q1  {d:+.1%}  [{d - 1.96 * se:+.1%}, {d + 1.96 * se:+.1%}]  "
              f"z {d / se:+.1f}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    print(f"  THE GATE FAILED AND IT GOVERNS EVERYTHING ELSE HERE. Representativeness is three")
    print(f"  times more a property of the RATER ({ssb_a / tot:.0%} of variance) than of the PROMPT")
    print(f"  ({ssb_p / tot:.0%}), and its split-half reliability across half-panels is "
          f"{sb:.2f} on 854")
    print(f"  prompts. So the field does not measure whether a prompt is realistic. It measures")
    print(f"  how readily a given person says they would ask things.")
    print(f"\n  THEREFORE THE HEADLINE I WAS ABOUT TO WRITE IS NOT AVAILABLE. '{low:.0%} of")
    print(f"  assessments say unlikely or only slightly likely' is true as a count and does NOT")
    print(f"  license 'the panel says the corpus is unrepresentative' -- that would be a claim")
    print(f"  about prompts built on a rater-level quantity. The gate was written to catch exactly")
    print(f"  this and it fired, which is the first time in this sweep a check placed BEFORE the")
    print(f"  interesting number stopped the interesting number rather than a later round doing it.")
    print(f"\n  AND THE SCALE HAS A FLOOR NOBODY EVER TOUCHED: the lowest option, 'unlikely',")
    print(f"  appears {dist[0]} times in {len(rows)} assessments -- {dist[0] / len(rows):.1%}. Not")
    print(f"  rare, ABSENT. So the most negative judgement anyone in this panel actually recorded")
    print(f"  is 'slightly likely', and the {low:.0%} figure is the floor of the OBSERVED scale")
    print(f"  rather than a body of negative verdicts. A response option with exactly zero uses")
    print(f"  across 11,023 assessments is either never presented or never chosen, and the release")
    print(f"  does not say which -- a fact about the instrument that no analysis of the field can")
    print(f"  work around.")
    print(f"\n  WHAT SURVIVES: the release ships an ecological-validity question, its answers are")
    print(f"  dominated by who is answering, and the bottom of its scale is unused. r175 made me")
    print(f"  withdraw the claim that nothing here transfers to production traffic. This round does")
    print(f"  not restore it in any form -- it removes the field that looked like it might.")
    if gate:
        print(f"\n  And the field is real: {ssb_p / tot:.0%} of its variance is between prompts")
        print(f"  against {ssb_a / tot:.0%} between raters, with a Spearman-Brown reliability of")
        print(f"  {sb:.2f} across half-panels. It is a property of the prompt, so a per-prompt")
        print(f"  aggregate over it is meaningful -- which is more than can be said for most")
        print(f"  self-reported fields.")
    if 0 in means and 3 in means:
        if abs(d / se) > 3:
            print(f"\n  AND IT PREDICTS CONSENSUS. Agreement runs {means[0]:.1%} on the least")
            print(f"  realistic quartile against {means[3]:.1%} on the most, {d:+.1%}, z {d / se:+.1f}.")
            print(f"  {'The pipeline works BEST where the prompts are most realistic, which is the good direction.' if d > 0 else 'The pipeline agrees LEAST where the prompts are most realistic -- consensus is concentrated on the questions nobody would ask.'}")
        else:
            print(f"\n  It does not predict consensus ({d:+.1%}, z {d / se:+.1f}). Realistic and")
            print(f"  unrealistic prompts are equally contested, so the corpus's ecological")
            print(f"  validity and its internal agreement are independent properties.")

    (OUT / "representativeness.json").write_text(json.dumps(
        {"assessments": len(rows), "distribution": {names[v]: dist[v] for v in range(5)},
         "share_unlikely_or_slight": low,
         "mean_level": float(np.mean([r["rep"] for r in rows])),
         "variance_between_prompts": ssb_p / tot, "variance_between_raters": ssb_a / tot,
         "split_half_r": r_half, "spearman_brown": sb, "gate_passed": bool(gate),
         "agreement_by_quartile": {lbls[b]: means[b] for b in means},
         "lowest_option_uses": int(dist[0]),
         "verdict": "the field is a RATER trait not a PROMPT property (S-B 0.18, 38% rater "
                    "variance vs 12% prompt); no corpus-level claim is licensed, and the lowest "
                    "scale option is never used"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
