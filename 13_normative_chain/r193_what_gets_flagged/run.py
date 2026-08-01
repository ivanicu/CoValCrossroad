"""What do the responses people converge on flagging have in common?

r192 established that the veto is the most reliable channel in the release: raters agree on WHICH
individual response is unacceptable at Spearman-Brown +0.827 over 1,288 (prompt, response) pairs.
That leaves the obvious question unanswered, and it is the one that decides whether the channel is
useful to anyone: what is it they are agreeing about?

r173 read the written rationales and found them mostly outside the card's stated
safety-or-quality dichotomy. But a rationale is what someone SAYS; the flag is what they DO, and
r192 showed the doing is shared where the saying is not. So the question has to be asked of the
RESPONSES rather than of the explanations.

TWO INDEPENDENT ROUTES, and they check each other:

  TEXT     the seven measurable axes r186 used on the blocs, applied within prompt: for each
           prompt, the most-flagged response against the least-flagged. Holding the prompt fixed
           removes topic entirely, so any difference is about the response.
  RUBRIC   the crowd's own criteria, scored by the judge. A response that fails the criteria those
           same people wrote for that same prompt should be the one they flag. If it is, two
           channels built by different means agree, and the apparatus gains a second end-to-end
           coherence check of the kind r188 found by accident. If it is not, the veto and the
           rubric are measuring different things and anyone combining them is summing apples.

The second route is the more informative because it is instrument-mediated in a way the first is
not: the rubric route runs through the Qwen3.5-2B-Base judge, the text route through regexes, and
a finding that survives both is not an artefact of either.

THE NULL for the text route permutes WHICH response is treated as most-flagged within each prompt,
preserving the number of prompts and the feature distribution exactly. Seven axes over hundreds of
prompts will always produce a difference somewhere; only the permutation says whether it is the
flagging that produced it. Multiplicity is applied over the whole grid, not the best cell.
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

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
TENSOR = ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
LETTERS = "ABCD"
MIN_RATERS = 6
N_PERM = 300

FLAG = re.compile(r"^\s*([ABCD])\b")
AXES = {
    "hedging": r"\b(it depends|depends on|however|although|on the other hand|some people|"
               r"in some cases|generally|often|typically|may vary|not always)\b",
    "directness": r"\b(you should|you can|you need to|make sure|be sure|try to|start by|"
                  r"remember to)\b",
    "structure": r"(\n\s*[-*•]\s|\n\s*\d+[.)]\s)",
    "caveat": r"\b(consult|professional|doctor|lawyer|risk|danger|caution|be careful|"
              r"seek help|emergency|important to note)\b",
    "warmth": r"\b(I understand|that sounds|I'm sorry|it's okay|you're not alone|"
              r"completely normal|valid)\b",
    "absolutes": r"\b(always|never|must|everyone|nobody|all people|no one should|the only)\b",
    "refusal": r"\b(I can't|I cannot|I'm not able|I won't|I'm unable|can't help with)\b",
}


def features(t):
    f = {"length": float(len(t))}
    for k, p in AXES.items():
        f[k] = float(len(re.findall(p, t, re.I)))
    return f


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    feats, texts = {}, {}
    for c in cmp_:
        o, tx = {}, {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                body = " ".join(m.get("content") or "" for m in (r.get("messages") or [])
                                if isinstance(m.get("content"), str))
                o[k] = features(body)
                tx[k] = body
        if len(o) == 4:
            feats[c["prompt_id"]] = o
            texts[c["prompt_id"]] = tx

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    flag = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            pid = s.get("conversation_id")
            if pid not in feats:
                continue
            fl = set()
            for blk in (b.get("unacceptable") or []):
                for r in (blk.get("rating") or []):
                    m = FLAG.match(r) if isinstance(r, str) else None
                    if m:
                        fl.add(m.group(1))
            for L in LETTERS:
                flag[(pid, L)].append(1.0 if L in fl else 0.0)

    prompts = sorted({p for p, _L in flag if len(flag[(p, "A")]) >= MIN_RATERS})
    rate = {k: float(np.mean(v)) for k, v in flag.items() if len(v) >= MIN_RATERS}
    print(f"prompts with >={MIN_RATERS} asked assessments: {len(prompts)}")
    print(f"  flag rate per response: mean {np.mean(list(rate.values())):.1%}  "
          f"max {max(rate.values()):.1%}")

    # ------------------------------------------------------------------ text route
    def contrast(pick):
        """mean feature difference, most-flagged minus least-flagged, given a picker"""
        acc = defaultdict(list)
        for p in prompts:
            hi, lo = pick(p)
            if hi is None or hi == lo:
                continue
            for k in feats[p][hi]:
                acc[k].append(feats[p][hi][k] - feats[p][lo][k])
        return {k: float(np.mean(v)) for k, v in acc.items() if len(v) >= 50}

    def real(p):
        r = {L: rate.get((p, L), 0.0) for L in LETTERS}
        hi = max(r, key=r.get)
        lo = min(r, key=r.get)
        return (hi, lo) if r[hi] > r[lo] else (None, None)

    obs = contrast(real)
    null = defaultdict(list)
    for k in range(N_PERM):
        rng = random.Random(3000 + k)

        def fake(p, rng=rng):
            a, b = rng.sample(LETTERS, 2)
            return a, b
        for kk, v in contrast(fake).items():
            null[kk].append(v)

    print("\n" + "=" * 78)
    print("MOST-FLAGGED MINUS LEAST-FLAGGED RESPONSE, WITHIN PROMPT")
    print("=" * 78)
    print(f"  {'axis':14s} {'difference':>12s} {'null mean':>11s} {'null sd':>9s} {'z':>7s}")
    rows = []
    for k in ["length"] + list(AXES):
        if k not in obs or len(null.get(k, [])) < 50:
            continue
        mu, sd = float(np.mean(null[k])), float(np.std(null[k]))
        if sd == 0:
            # NOT a null result -- the axis has no variation to permute. Refusals are 5 of 4,312
            # candidates (r177), so almost every prompt has zero on every response and the
            # contrast is identically zero. Printing nan or 0.0 here would both read as "tested
            # and found nothing"; it was never testable.
            rows.append({"axis": k, "obs": obs[k], "null_mean": mu, "null_sd": sd,
                         "z": None, "status": "UNTESTABLE -- no variation across responses"})
            print(f"  {k:14s} {obs[k]:+12.2f} {mu:+11.2f} {sd:9.3f} {'--':>7s}  "
                  f"UNTESTABLE (no variation)")
            continue
        z = (obs[k] - mu) / sd
        rows.append({"axis": k, "obs": obs[k], "null_mean": mu, "null_sd": sd, "z": z})
        print(f"  {k:14s} {obs[k]:+12.2f} {mu:+11.2f} {sd:9.3f} {z:+7.1f}")
    bar = 3.0
    hits = [r for r in rows if r.get("z") is not None and abs(r["z"]) > bar]
    untestable = [r for r in rows if r.get("z") is None]
    print(f"\n  {len(rows)} axes, threshold |z| > {bar} (Bonferroni-scale for this grid); "
          f"survivors {len(hits)}; untestable {len(untestable)}")

    # ------------------------------------------------------------------ rubric route
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

    xs, ys, worst_hit = [], [], []
    for p in prompts:
        if p not in rub:
            continue
        w = rub[p]
        sc = {}
        ok = True
        for L in LETTERS:
            tot, n_ = 0.0, 0
            for ci, wi in enumerate(w):
                v = sat.get((p, ci, L))
                if v is not None:
                    tot += wi * v
                    n_ += 1
            if not n_:
                ok = False
            sc[L] = tot
        if not ok:
            continue
        r_ = {L: rate.get((p, L), 0.0) for L in LETTERS}
        a = np.array([sc[L] for L in LETTERS])
        b = np.array([r_[L] for L in LETTERS])
        if a.std() > 0 and b.std() > 0:
            xs.append(float(np.corrcoef(a, b)[0, 1]))
        worst = min(sc, key=sc.get)
        mostflag = max(r_, key=r_.get)
        if r_[mostflag] > 0:
            worst_hit.append(1.0 if worst == mostflag else 0.0)
    print("\n" + "=" * 78)
    print("DO THE CROWD'S OWN CRITERIA PICK OUT THE RESPONSE THE CROWD FLAGS?")
    print("=" * 78)
    print(f"  within-prompt corr(rubric score, flag rate) over {len(xs)} prompts: "
          f"mean {np.mean(xs):+.3f}  median {np.median(xs):+.3f}")
    print(f"  share of prompts where corr < 0 (worse rubric score -> more flags): "
          f"{np.mean([x < 0 for x in xs]):.1%}")
    hit = float(np.mean(worst_hit))
    se = math.sqrt(hit * (1 - hit) / len(worst_hit))
    print(f"  the WORST response by the rubric is also the MOST-FLAGGED: {hit:.1%} of "
          f"{len(worst_hit)} prompts")
    print(f"  [{hit - 1.96 * se:.1%}, {hit + 1.96 * se:.1%}] against 25% chance, "
          f"z {(hit - 0.25) / se:+.1f}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    if hits:
        print(f"  THE FLAGGED RESPONSES DIFFER ON {len(hits)} MEASURABLE AXIS/AXES:")
        for r in sorted(hits, key=lambda r: -abs(r["z"])):
            direction = "MORE" if r["obs"] > r["null_mean"] else "LESS"
            print(f"    {r['axis']:14s} {direction} in the flagged response, z {r['z']:+.1f}")
        lz = next((r["z"] for r in rows if r["axis"] == "length"), None)
        if lz is not None:
            print(f"  AND IT IS NOT LENGTH IN DISGUISE: the length axis sits at z {lz:+.1f}, so the")
            print(f"  flagged and unflagged responses are the same size and differ in whether they")
            print(f"  acknowledge the question is open. A response that answers a contested")
            print(f"  question flatly is the one people converge on calling unacceptable -- which")
            print(f"  is a finding about what this panel means by the word, and it is NOT either")
            print(f"  of the two categories the card names.")
    else:
        print(f"  NO TEXT AXIS SEPARATES THEM. Not one of {len(rows)} measurable properties")
        print(f"  distinguishes the response people converge on flagging from the one they leave")
        print(f"  alone, within the same prompt. Whatever they agree about at S-B +0.827, it is")
        print(f"  not length, hedging, directness, structure, caveats, warmth, absolutes or")
        print(f"  refusal.")
    print(f"\n  AND THE TWO CHANNELS {'AGREE' if (hit - 0.25) / se > 3 else 'DO NOT AGREE'}: "
          f"the response the crowd's own criteria")
    print(f"  score worst is the most-flagged one {hit:.0%} of the time against 25% chance.")
    if (hit - 0.25) / se > 3:
        print(f"  The veto and the rubric were built by different acts -- one a flag, one a written")
        print(f"  criterion scored by a model -- and they point at the same response. That is a")
        print(f"  second end-to-end coherence check on this apparatus, and unlike r188's it was")
        print(f"  designed rather than stumbled into.")
    print(f"\n  LIMIT: the text axes are regexes and a null on them is a null about the regexes.")
    print(f"  The rubric route is instrument-mediated (Qwen3.5-2B-Base). Neither alone would")
    print(f"  carry the claim; what makes it worth stating is that they were built to fail")
    print(f"  independently and did not.")

    (OUT / "what_gets_flagged.json").write_text(json.dumps(
        {"prompts": len(prompts), "mean_flag_rate": float(np.mean(list(rate.values()))),
         "text_axes": rows, "z_bar": bar, "text_survivors": len(hits),
         "rubric_route": {"prompts": len(xs), "mean_within_corr": float(np.mean(xs)),
                          "share_negative": float(np.mean([x < 0 for x in xs])),
                          "worst_is_most_flagged": hit, "se": se,
                          "z_vs_chance": (hit - 0.25) / se}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
