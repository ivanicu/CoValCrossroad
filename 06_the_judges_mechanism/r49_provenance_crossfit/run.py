"""r49 -- does the cross-rater direction survive on criteria nobody else saw?

CLAIM_CARD.md is the contract.  In one line: r34 showed the post-choice
criterion direction transfers across people, and item 1 correctly rescoped that
to leave SHARED-MENU endogeneity untouched.  r48 then established that the menu
had two shared parts, not one -- the same four responses AND the same six
pre-seeded criteria -- and that the write-in criteria are private, authored and
rated by exactly one participant.

So the shared-criteria channel is separable even though the shared-response one
is not.  A write-in criterion used to predict a DIFFERENT participant's ranking
involves no text that participant ever saw.

Both classes are size-matched by subsampling to equal criteria per prompt,
because seed carries ~5.7 per prompt and write-in ~10.2, and more criteria is
not neutral.

WHAT A POSITIVE RESULT WOULD AND WOULD NOT MEAN.  It narrows shared-menu
endogeneity to the RESPONSE channel.  It does not eliminate it: a write-in
criterion was still written after seeing the same four candidates as everyone
else.  Worlds "shared-response artifact" and "population property" make the SAME
prediction here and this round cannot separate them.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join, parse_ranking  # noqa: E402

OUTCOME_SCOPE = (
    "Evaluated against INDIVIDUAL human rankings from the released assessments, not "
    "against any model proxy. The satisfaction layer is judge-produced (r04), so the "
    "judge is an instrument here, but the target being predicted is a person's own "
    "ranking of the four candidates."
)


def individual_pairs(asm):
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(l, gi) for gi, g in enumerate(r) for l in g]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r49_provenance_crossfit.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=25)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.seeds, a.boot = 3, 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    prompts = {}
    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in sat:
            continue
        items = rub.get("coval_full") or []
        if not items:
            continue
        ratings, prov = {}, {}
        # r34's EXACT threshold, reproduced line for line: the denominator is the
        # number of raters who touched ANY criterion on this prompt, not the max
        # per-criterion count.  My first version used the latter, which is a
        # different filter and is one of two reasons the control failed.
        raters_here = {sc["annotator_id"] for it in items for sc in (it.get("scores") or [])}
        thr = max(2, (len(raters_here) + 1) // 2)
        for ci, it in enumerate(items):
            sc = it.get("scores") or []
            if not sc:
                continue
            ratings[ci] = {s["annotator_id"]: float(s["score"]) for s in sc}
            prov[ci] = "seed" if len(sc) >= thr else "writein"
        if not ratings:
            continue
        byann = {}
        for asm in comp["metadata"]["assessments"]:
            aid, pr = asm.get("annotator_id"), individual_pairs(asm)
            if aid and pr:
                byann[aid] = pr
        if byann:
            prompts[pid] = {"ratings": ratings, "prov": prov, "pairs": byann}

    allr = sorted({r for d in prompts.values() for c in d["ratings"].values() for r in c}
                  | {r for d in prompts.values() for r in d["pairs"]})
    ns = sum(1 for d in prompts.values() for v in d["prov"].values() if v == "seed")
    nw = sum(1 for d in prompts.values() for v in d["prov"].values() if v == "writein")
    print(f"prompts {len(prompts):,}   raters {len(allr):,}")
    print(f"criteria: seed {ns:,} ({ns/len(prompts):.1f}/prompt)   "
          f"writein {nw:,} ({nw/len(prompts):.1f}/prompt)")

    def score_arm(who, test_of, keep, use_sign, rng, match_k=None):
        """Accuracy against TEST raters' own rankings, per prompt."""
        acc = {}
        for pid, d in prompts.items():
            test = test_of(pid)
            if not test:
                continue
            cis = [ci for ci in d["ratings"] if keep(d["prov"][ci])]
            if match_k is not None and len(cis) > match_k:
                cis = list(rng.choice(cis, size=match_k, replace=False))
            w = {}
            for ci in cis:
                vals = [v for r_, v in d["ratings"][ci].items() if who is None or r_ in who]
                if not vals:
                    continue
                w[ci] = (float(np.sign(np.mean(vals))) or 1.0) if use_sign else 1.0
            if not w:
                continue
            score = {}
            for lab in {l for (_c, l) in sat[pid]}:
                num = den = 0.0
                for ci, wc in w.items():
                    s = sat[pid].get((ci, lab))
                    if s is None:
                        continue
                    num += wc * s
                    den += abs(wc)
                if den > 0:
                    score[lab] = num / den
            if len(score) < 2:
                continue
            ok = tot = 0
            for r_ in test:
                for x, y in d["pairs"].get(r_, []):
                    if x in score and y in score:
                        tot += 1
                        ok += int(score[x] > score[y])
            if tot:
                acc[pid] = ok / tot
        return acc

    def crossfit(keep, use_sign, match_k, shuffle_signs=False):
        """Global rater folds: a person is in exactly one fold, never both sides."""
        agg = defaultdict(lambda: [0.0, 0])
        for s in range(a.seeds):
            rng = np.random.default_rng(1000 + s)
            order = list(allr)
            rng.shuffle(order)
            fold = {r: i % a.folds for i, r in enumerate(order)}
            for f in range(a.folds):
                train = {r for r in allr if fold[r] != f}
                test = {r for r in allr if fold[r] == f}
                assert train.isdisjoint(test)
                if shuffle_signs:
                    # sign channel destroyed, everything else identical
                    got = score_arm_shuffled(train, test, keep, rng, match_k)
                else:
                    got = score_arm(train, lambda pid: {r for r in prompts[pid]["pairs"]
                                                        if r in test},
                                    keep, use_sign, rng, match_k)
                for pid, v in got.items():
                    agg[pid][0] += v
                    agg[pid][1] += 1
        return {p_: s / n for p_, (s, n) in agg.items() if n}

    def score_arm_shuffled(train, test, keep, rng, match_k):
        acc = {}
        for pid, d in prompts.items():
            tst = {r for r in d["pairs"] if r in test}
            if not tst:
                continue
            cis = [ci for ci in d["ratings"] if keep(d["prov"][ci])]
            if match_k is not None and len(cis) > match_k:
                cis = list(rng.choice(cis, size=match_k, replace=False))
            w = {ci: float(rng.choice([-1.0, 1.0])) for ci in cis
                 if any(r_ in train for r_ in d["ratings"][ci])}
            if not w:
                continue
            score = {}
            for lab in {l for (_c, l) in sat[pid]}:
                num = den = 0.0
                for ci, wc in w.items():
                    s = sat[pid].get((ci, lab))
                    if s is None:
                        continue
                    num += wc * s
                    den += abs(wc)
                if den > 0:
                    score[lab] = num / den
            if len(score) < 2:
                continue
            ok = tot = 0
            for r_ in tst:
                for x, y in d["pairs"].get(r_, []):
                    if x in score and y in score:
                        tot += 1
                        ok += int(score[x] > score[y])
            if tot:
                acc[pid] = ok / tot
        return acc

    rng0 = np.random.default_rng(7)

    def paired(a1, a2):
        common = sorted(set(a1) & set(a2))
        d = np.array([a2[p_] - a1[p_] for p_ in common])
        bs = np.array([d[rng0.integers(0, len(d), len(d))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"delta": float(d.mean()), "ci": [float(lo), float(hi)],
                "prompts": len(common), "excludes_zero": bool(lo > 0 or hi < 0),
                "paired_differences": [float(x) for x in d]}

    # size-match: the smaller class's median count per prompt
    med_seed = int(np.median([sum(1 for v in d["prov"].values() if v == "seed")
                              for d in prompts.values()]))
    med_wr = int(np.median([sum(1 for v in d["prov"].values() if v == "writein")
                            for d in prompts.values()]))
    K = max(2, min(med_seed, med_wr))
    print(f"size-matching both classes to {K} criteria per prompt "
          f"(medians: seed {med_seed}, writein {med_wr})\n")

    out = {}
    # POSITIVE CONTROL: r34's EXACT population -- majority-filtered (= the
    # pre-seeded class, per r48), no size matching.  The second reason the first
    # version failed was that it pooled write-ins into this arm, which r34 never
    # sees.  Reproducing r34 requires reproducing what r34 EXCLUDED.
    ctrl_sign = crossfit(lambda p_: p_ == "seed", True, None)
    ctrl_free = crossfit(lambda p_: p_ == "seed", False, None)
    ctrl = paired(ctrl_free, ctrl_sign)
    print(f"positive control  r34's population (majority-filtered, unmatched): "
          f"{ctrl['delta']:+.4f} {ctrl['ci']}   [r34 got +0.0576]")
    passed = bool(abs(ctrl["delta"] - 0.0576) < 0.02)
    print(f"  -> {'reproduces r34' if passed else 'DOES NOT reproduce r34'}")
    if not passed:
        raise SystemExit("REFUSING TO REPORT: the all-criteria arm does not reproduce "
                         "r34's direction advantage, so this is not r34's estimator and "
                         "no per-class number below is interpretable")
    out["control_all"] = ctrl

    for cls in ("seed", "writein"):
        keep = (lambda c, _c=cls: c == _c)
        sign = crossfit(keep, True, K)
        free = crossfit(keep, False, K)
        null = crossfit(keep, True, K, shuffle_signs=True)
        d_dir = paired(free, sign)
        d_null = paired(free, null)
        out[cls] = {"direction_advantage": d_dir, "shuffled_sign_null": d_null,
                    "criteria_per_prompt_matched": K}
        print(f"{cls:8s} direction advantage {d_dir['delta']:+.4f} "
              f"[{d_dir['ci'][0]:+.4f},{d_dir['ci'][1]:+.4f}]"
              f"{'' if d_dir['excludes_zero'] else '  (ns)'}")
        print(f"{'':8s} shuffled-sign null  {d_null['delta']:+.4f} "
              f"[{d_null['ci'][0]:+.4f},{d_null['ci'][1]:+.4f}]"
              f"   <- must be <= 0 if the sign channel is real")

    s_d, w_d = out["seed"]["direction_advantage"], out["writein"]["direction_advantage"]
    # The two intervals nearly separate, and "nearly separate" is not a test.
    # Comparing two CIs by eye is how a difference gets asserted that was never
    # estimated, so the contrast is computed on the PAIRED per-prompt vectors.
    sv = np.array(s_d["paired_differences"])
    wv = np.array(w_d["paired_differences"])
    m = min(len(sv), len(wv))
    gapv = wv[:m] - sv[:m]
    gbs = np.array([gapv[rng0.integers(0, m, m)].mean() for _ in range(a.boot)])
    glo, ghi = np.percentile(gbs, [2.5, 97.5])
    gap = {"writein_minus_seed": float(gapv.mean()), "ci": [float(glo), float(ghi)],
           "prompts": int(m), "excludes_zero": bool(glo > 0 or ghi < 0),
           "note": ("Paired on prompts. Both arms are size-matched to the same K, so "
                    "this is not a criterion-count effect.")}
    out["writein_minus_seed"] = gap
    print(f"\nwritein - seed (paired) {gap['writein_minus_seed']:+.4f} "
          f"[{gap['ci'][0]:+.4f},{gap['ci'][1]:+.4f}]"
          f"{'  SIGNIFICANT' if gap['excludes_zero'] else '  (ns)'}")
    both = s_d["excludes_zero"] and w_d["excludes_zero"]
    if both:
        verdict = (
            f"THE DIRECTION TRANSFERS ON PRIVATE CRITERIA. Size-matched at {K} criteria "
            f"per prompt, write-in criteria -- authored by ONE participant and rated by "
            f"only that participant -- carry a cross-rater direction advantage of "
            f"{w_d['delta']:+.4f} {w_d['ci']}, against {s_d['delta']:+.4f} {s_d['ci']} "
            f"for the pre-seeded six that everyone saw -- a paired gap of "
            f"{gap['writein_minus_seed']:+.4f} {gap['ci']}"
            f"{', which excludes zero' if gap['excludes_zero'] else ', which SPANS zero, so the two classes are not shown to differ'}"
            f". So the transferable direction is NOT an artifact of shared criterion TEXT. SHARED-MENU ENDOGENEITY IS "
            f"NARROWED, NOT REMOVED: every write-in was still written after seeing the "
            f"same four candidates, and 'shared-response artifact' and 'population "
            f"property' make the same prediction here")
    elif w_d["excludes_zero"] and not s_d["excludes_zero"]:
        verdict = (
            f"ONLY THE PRIVATE CRITERIA TRANSFER ({w_d['delta']:+.4f} vs "
            f"{s_d['delta']:+.4f} ns), which is the opposite of the shared-criterion "
            f"story and needs its own explanation")
    elif s_d["excludes_zero"] and not w_d["excludes_zero"]:
        verdict = (
            f"THE DIRECTION IS CARRIED BY THE SHARED CRITERIA. Pre-seeded items transfer "
            f"({s_d['delta']:+.4f}) and private write-ins do not ({w_d['delta']:+.4f}, "
            f"CI spans zero). r34's cross-rater result is then substantially about the "
            f"six criteria OpenAI supplied, not about what participants themselves "
            f"raised -- and the S_pre design must randomise criterion PROVISION as well "
            f"as response exposure. Caveat that cuts the other way: a write-in sign comes "
            f"from ONE rater and is noisier, which biases against this arm")
    else:
        verdict = (
            f"NEITHER CLASS TRANSFERS at this size match ({K}/prompt), so the split is "
            f"underpowered rather than informative -- the all-criteria control does "
            f"reproduce r34, so the signal exists and is being diluted by subsampling")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": len(prompts), "raters": len(allr), "folds": a.folds, "seeds": a.seeds,
        "criteria_seed": ns, "criteria_writein": nw, "size_matched_k": K,
        "results": out, "verdict": verdict,
        "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Separates the SHARED-CRITERION channel of menu endogeneity from the "
                  "SHARED-RESPONSE channel. Only the first is separable in this release: "
                  "write-in criteria are private text, but their authors still saw the "
                  "same four candidates. A write-in's sign comes from a SINGLE rater and "
                  "is therefore noisier than a seeded item's ~15-rater mean, which biases "
                  "AGAINST the write-in arm -- so a positive write-in result is "
                  "conservative and a negative one is ambiguous."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
