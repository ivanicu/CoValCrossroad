"""r50 -- is the cross-rater direction carried by criteria ABOUT the four responses?

CLAIM_CARD.md is the contract, and it records why this round exists: I asserted
that the shared-response and population-property worlds "make identical
predictions in every design this release permits".  That is a universal claim
about designs and the honest reply is to look for one.

Here is a candidate.  Write-in criteria differ in how much they are ABOUT the
particular four candidates -- "invents a statute" versus "maintain a respectful
tone".  If the transferable direction is a shared-response artifact, it should
concentrate in the response-anchored ones.

Anchoring is lexical containment of the criterion's content words in the single
best-matching response, which is a COARSE proxy for aboutness and is treated as
one throughout.  The seeded class gets the same split as a control, because if
anchoring predicts transfer among criteria participants did not author, the
effect is concreteness rather than menu-induced construction.
"""
from __future__ import annotations

import argparse
import json
import re
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
    "against any model proxy."
)
STOP = set("the a an and or of to in for on with is are be that this it as at by from "
           "not no should must does do response answer model user its their they".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{3,}", str(s).lower()) if w not in STOP}


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
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r50_response_anchoring.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--seeds", type=int, default=25)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--nperm", type=int, default=200)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.seeds, a.boot, a.nperm = 3, 200, 20
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
        resp = [toks(r["messages"][0]["content"]) for r in comp["responses"]]
        if not resp:
            continue
        raters_here = {sc["annotator_id"] for it in items for sc in (it.get("scores") or [])}
        thr = max(2, (len(raters_here) + 1) // 2)
        ratings, prov, anchor, clen = {}, {}, {}, {}
        for ci, it in enumerate(items):
            sc = it.get("scores") or []
            if not sc:
                continue
            ratings[ci] = {s["annotator_id"]: float(s["score"]) for s in sc}
            prov[ci] = "seed" if len(sc) >= thr else "writein"
            ct = toks(it["criterion"])
            clen[ci] = len(ct)
            # containment in the SINGLE best-matching response, normalised by
            # criterion length -- so a short criterion scores high easily, which
            # is why length is reported per stratum.
            anchor[ci] = max((len(ct & rt) / max(len(ct), 1)) for rt in resp) if ct else 0.0
        if not ratings:
            continue
        byann = {}
        for asm in comp["metadata"]["assessments"]:
            aid, pr = asm.get("annotator_id"), individual_pairs(asm)
            if aid and pr:
                byann[aid] = pr
        if byann:
            prompts[pid] = {"ratings": ratings, "prov": prov, "anchor": anchor,
                            "clen": clen, "pairs": byann}

    allr = sorted({r for d in prompts.values() for c in d["ratings"].values() for r in c}
                  | {r for d in prompts.values() for r in d["pairs"]})
    print(f"prompts {len(prompts):,}   raters {len(allr):,}")

    def strata(d, cls, perm_rng=None):
        """Within-prompt median split on anchoring, inside one provenance class."""
        cis = [ci for ci in d["ratings"] if d["prov"][ci] == cls]
        if len(cis) < 4:
            return None
        vals = np.array([d["anchor"][ci] for ci in cis])
        if perm_rng is not None:
            vals = perm_rng.permutation(vals)
        med = float(np.median(vals))
        hi = [ci for ci, v in zip(cis, vals) if v > med]
        lo = [ci for ci, v in zip(cis, vals) if v <= med]
        k = min(len(hi), len(lo))
        return (hi, lo, k) if k >= 2 else None

    def arm(cls, stratum, use_sign, seeds, perm=False):
        agg = defaultdict(lambda: [0.0, 0])
        for s in range(seeds):
            rng = np.random.default_rng(2000 + s)
            order = list(allr)
            rng.shuffle(order)
            fold = {r: i % a.folds for i, r in enumerate(order)}
            for f in range(a.folds):
                train = {r for r in allr if fold[r] != f}
                test = {r for r in allr if fold[r] == f}
                assert train.isdisjoint(test)
                for pid, d in prompts.items():
                    tst = {r for r in d["pairs"] if r in test}
                    if not tst:
                        continue
                    st = strata(d, cls, rng if perm else None)
                    if st is None:
                        continue
                    hi, lo, k = st
                    cis = hi if stratum == "high" else lo if stratum == "low" else hi + lo
                    if stratum in ("high", "low") and len(cis) > k:
                        cis = list(rng.choice(cis, size=k, replace=False))
                    w = {}
                    for ci in cis:
                        vals = [v for r_, v in d["ratings"][ci].items() if r_ in train]
                        if vals:
                            w[ci] = (float(np.sign(np.mean(vals))) or 1.0) if use_sign else 1.0
                    if not w:
                        continue
                    score = {}
                    for lab in {l for (_c, l) in sat[pid]}:
                        num = den = 0.0
                        for ci, wc in w.items():
                            sv = sat[pid].get((ci, lab))
                            if sv is None:
                                continue
                            num += wc * sv
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
                        agg[pid][0] += ok / tot
                        agg[pid][1] += 1
        return {p_: s / n for p_, (s, n) in agg.items() if n}

    rng0 = np.random.default_rng(11)

    def paired(a1, a2):
        common = sorted(set(a1) & set(a2))
        d = np.array([a2[p_] - a1[p_] for p_ in common])
        bs = np.array([d[rng0.integers(0, len(d), len(d))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"delta": float(d.mean()), "ci": [float(lo), float(hi)],
                "prompts": len(common), "excludes_zero": bool(lo > 0 or hi < 0),
                "paired_differences": [float(x) for x in d]}

    out = {}
    # positive control: pooled write-in arm must reproduce r49's +0.0777
    pooled = paired(arm("writein", "all", False, a.seeds), arm("writein", "all", True, a.seeds))
    print(f"\npositive control  pooled write-in: {pooled['delta']:+.4f} {pooled['ci']}"
          f"   [r49 got +0.0777]")
    ok = abs(pooled["delta"] - 0.0777) < 0.025
    print(f"  -> {'reproduces r49' if ok else 'DOES NOT reproduce r49'}")
    if not ok:
        raise SystemExit("REFUSING TO REPORT: the pooled write-in arm does not reproduce "
                         "r49, so the stratification below is built on a different "
                         "estimator")
    out["control_pooled_writein"] = pooled

    for cls in ("writein", "seed"):
        hi = paired(arm(cls, "high", False, a.seeds), arm(cls, "high", True, a.seeds))
        lo = paired(arm(cls, "low", False, a.seeds), arm(cls, "low", True, a.seeds))
        hv = np.array(hi["paired_differences"])
        lv = np.array(lo["paired_differences"])
        m = min(len(hv), len(lv))
        g = hv[:m] - lv[:m]
        gb = np.array([g[rng0.integers(0, m, m)].mean() for _ in range(a.boot)])
        glo, ghi = np.percentile(gb, [2.5, 97.5])
        gap = {"high_minus_low": float(g.mean()), "ci": [float(glo), float(ghi)],
               "prompts": int(m), "excludes_zero": bool(glo > 0 or ghi < 0)}
        # mean criterion length per stratum, since containment favours short text
        L = {"high": [], "low": []}
        for d in prompts.values():
            st = strata(d, cls)
            if st is None:
                continue
            L["high"] += [d["clen"][c] for c in st[0]]
            L["low"] += [d["clen"][c] for c in st[1]]
        out[cls] = {"high": hi, "low": lo, "high_minus_low": gap,
                    "mean_criterion_tokens": {k: float(np.mean(v)) for k, v in L.items()}}
        print(f"\n{cls}: anchored(high) {hi['delta']:+.4f} [{hi['ci'][0]:+.4f},{hi['ci'][1]:+.4f}]"
              f"   generic(low) {lo['delta']:+.4f} [{lo['ci'][0]:+.4f},{lo['ci'][1]:+.4f}]")
        print(f"{'':8s} high - low {gap['high_minus_low']:+.4f} "
              f"[{gap['ci'][0]:+.4f},{gap['ci'][1]:+.4f}]"
              f"{'  SIGNIFICANT' if gap['excludes_zero'] else '  (ns)'}"
              f"   mean tokens hi {out[cls]['mean_criterion_tokens']['high']:.1f} / "
              f"lo {out[cls]['mean_criterion_tokens']['low']:.1f}")

    w_gap, s_gap = out["writein"]["high_minus_low"], out["seed"]["high_minus_low"]
    # DIFFERENCE OF THE TWO GAPS, tested rather than eyeballed.  The concreteness
    # control only licenses a conclusion if the write-in gap is no larger than
    # the seeded one; "2.3x bigger" read off two intervals is not that test.
    wv = np.array(out["writein"]["high"]["paired_differences"]) - \
        np.array(out["writein"]["low"]["paired_differences"][
            :len(out["writein"]["high"]["paired_differences"])])
    sv = np.array(out["seed"]["high"]["paired_differences"]) - \
        np.array(out["seed"]["low"]["paired_differences"][
            :len(out["seed"]["high"]["paired_differences"])])
    mm = min(len(wv), len(sv))
    dd = wv[:mm] - sv[:mm]
    db = np.array([dd[rng0.integers(0, mm, mm)].mean() for _ in range(a.boot)])
    dlo, dhi = np.percentile(db, [2.5, 97.5])
    excess = {"writein_gap_minus_seed_gap": float(dd.mean()),
              "ci": [float(dlo), float(dhi)], "prompts": int(mm),
              "excludes_zero": bool(dlo > 0 or dhi < 0)}
    out["anchoring_excess_over_control"] = excess
    print(f"\nwrite-in gap MINUS seeded gap  {excess['writein_gap_minus_seed_gap']:+.4f} "
          f"[{excess['ci'][0]:+.4f},{excess['ci'][1]:+.4f}]"
          f"{'  SIGNIFICANT' if excess['excludes_zero'] else '  (ns)'}"
          f"   <- concreteness alone predicts 0")
    # THE BRANCH ORDER IS THE TEST.  A previous version checked "seed gap
    # significant?" first and, finding it was not while the write-in gap was,
    # declared the effect specific to participants.  That is difference-of-
    # significance masquerading as significance-of-difference, and the quantity
    # that actually separates the worlds -- the EXCESS -- spans zero.  So the
    # excess is now read FIRST and nothing downstream may overrule it.
    if excess["excludes_zero"] and excess["writein_gap_minus_seed_gap"] > 0:
        verdict = (
            f"PARTICIPANT-SIDE RESPONSE ANCHORING. The write-in anchoring gap exceeds the "
            f"seeded one by {excess['writein_gap_minus_seed_gap']:+.4f} {excess['ci']}, and "
            f"concreteness alone predicts zero excess. The shared-response channel is "
            f"showing itself in criteria participants wrote, so my claim that the two "
            f"worlds are indistinguishable in this release is WITHDRAWN, and so is the "
            f"reading that r49 narrowed endogeneity to a channel nothing could reach")
    elif w_gap["excludes_zero"]:
        verdict = (
            f"A DESIGN EXISTS, AND IT DOES NOT SEPARATE THE WORLDS YET. Anchoring predicts "
            f"transfer among write-ins ({w_gap['high_minus_low']:+.4f} {w_gap['ci']}): "
            f"criteria whose words overlap the four candidates carry more of the "
            f"cross-rater direction than generic ones do. But the seeded control shows the "
            f"same tendency ({s_gap['high_minus_low']:+.4f} {s_gap['ci']}) and the EXCESS "
            f"is {excess['writein_gap_minus_seed_gap']:+.4f} {excess['ci']}, spanning zero "
            f"-- so this is not shown to be participant-side rather than concreteness. "
            f"WHAT CHANGES ANYWAY: my claim that the two worlds are indistinguishable in "
            f"EVERY design this release permits was wrong as stated -- a design exists and "
            f"returns a signal. What it cannot yet do is attribute that signal. ⚠ The "
            f"control is also not airtight: the release never says how the seeded six were "
            f"produced, so 'not participant-authored' does not establish 'not "
            f"response-derived'")
    elif s_gap["excludes_zero"]:
        verdict = (
            f"ANCHORING PREDICTS TRANSFER ONLY IN THE SEEDED CLASS "
            f"({s_gap['high_minus_low']:+.4f}) and not among write-ins "
            f"({w_gap['high_minus_low']:+.4f}), which no version of the shared-response "
            f"story predicts and needs its own explanation")
    else:
        verdict = (
            f"ANCHORING DOES NOT CARRY THE DIRECTION in either class (write-in "
            f"{w_gap['high_minus_low']:+.4f} {w_gap['ci']}, seeded "
            f"{s_gap['high_minus_low']:+.4f}). Both strata transfer. The shared-response "
            f"story has to explain why its natural carrier does not matter. NOT AN "
            f"EXCLUSION: lexical containment is a coarse proxy for aboutness and this is a "
            f"non-rejection at this sample size")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": len(prompts), "raters": len(allr), "results": out,
        "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Anchoring = max lexical containment of a criterion's content words in "
                  "any one of the four original responses. It is a COARSE proxy for "
                  "'about these responses': it rises with concreteness and with short "
                  "criterion length, and a criterion can be entirely about a response "
                  "while sharing few of its words. The seeded class carries the same "
                  "split as a concreteness control, since those criteria were not "
                  "participant-authored -- but the release never states HOW the seeds "
                  "were produced, so that control does not establish they are free of "
                  "response derivation. It bounds participant-side anchoring against "
                  "whatever anchoring the seeds already carry, which is weaker."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
