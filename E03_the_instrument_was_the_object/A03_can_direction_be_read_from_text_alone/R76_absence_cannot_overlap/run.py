"""r76 -- is r75's asymmetry about attention, or is it that an absence has no words to overlap?

CLAIM CARD
----------
Claim      r75/entry 129: "Praise is drawn from the menu; criticism is not, or
           much less so." Positive criteria track the rater's own top response
           (+0.01755 residualised); negative criteria are flat (-0.00271).
Estimand   the same best-minus-worst overlap gap, computed separately for
           criteria that describe a PRESENT property and criteria that describe
           an ABSENT one, within each sign.
Target
observed?  YES. The distinction is in the criterion's own wording -- "fails to
           mention X", "does not address Y", "omits" describe something the
           response did NOT do; "is preachy", "moralises", "too long" describe
           something it DID.
Alternative
worlds     P NO-WORDS-TO-OVERLAP  the asymmetry is mechanical. A criterion about
                                  an absence cannot lexically overlap the text
                                  that lacks it, so negative criteria look flat
                                  because most of them are absence-shaped. Then
                                  PRESENCE-type negatives should track the WORST
                                  response -- a NEGATIVE gap -- and absence-type
                                  criteria of BOTH signs should be flat. Entry
                                  129's sentence must be narrowed: criticism is
                                  not less drawn from the menu, it is less
                                  lexically visible when drawn.
           A ASYMMETRIC-ATTENTION raters genuinely engage more with the answer
                                  they preferred. Then the split changes little:
                                  presence-type negatives stay flat too, and the
                                  asymmetry is about people rather than about
                                  the measure.
Intervention
           none. Recomputation, re-partitioned.
Null       shuffle signs within each partition; every gap must collapse.

WHY THIS MATTERS MORE THAN IT LOOKS
-----------------------------------
Under P, containment is not a neutral instrument for this question: it is
systematically blind to exactly one of the two things being compared. Every
overlap-based finding in this package that contrasts positive with negative
material inherits that blindness -- and r75's headline was written as a claim
about raters, which under P it is not.

THE SYMMETRY TEST, which is what makes this decisive
----------------------------------------------------
Absence-shaped wording is not the property of negative criteria alone: "avoids
moralising" and "does not lecture the user" are POSITIVE criteria describing an
absence. If P holds, the effect must live in PRESENCE-type criteria of both
signs and vanish for absence-type criteria of both signs. That is a prediction
the attention story does not make, and it is checkable in the same pass.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "E03_the_instrument_was_the_object/A03_can_direction_be_read_from_text_alone/R75_menu_read_direction"))

from covalx import load_join  # noqa: E402
# Imported, not copied: a second copy of `contain`/`toks` could drift from r75's
# and the two rounds' numbers would stop being comparable, which is the whole
# point of this one.
from run import LAB, contain, ranks_from, resp_text, toks  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
N_BOOT = 3000

# ABSENCE-shaped wording: the criterion is about something the response did not
# do. Deliberately narrow -- it must match the CONSTRUCTION, not merely contain a
# negative word, because "not" appears inside plenty of presence descriptions
# ("is not concise" describes a property the text has).
ABSENT = re.compile(
    r"\b(fails? to|failing to|does ?n[o']t (?:mention|address|include|acknowledge|"
    r"provide|explain|offer|give|discuss|cover|consider)|did ?n[o']t (?:mention|address|include)|"
    r"omits?|omitting|lacks?|lacking|without (?:mention|any|providing)|"
    r"no mention of|leaves? out|missing|neglects? to|avoids? (?:mention)|"
    r"should (?:have )?(?:mention|include|address|provide|explain|offer|acknowledge))\b", re.I)


def boot_gap(vec, y, pids, seed):
    uni = np.unique(pids)
    idx = {p: np.flatnonzero(pids == p) for p in uni}
    bs = np.random.default_rng(seed)
    out = []
    for _ in range(N_BOOT):
        take = np.concatenate([idx[p] for p in bs.choice(uni, len(uni), replace=True)])
        yy, vv = y[take], vec[take]
        if (yy > 0).sum() and (yy < 0).sum():
            out.append(vv[yy > 0].mean() - vv[yy < 0].mean())
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def boot_mean(v, seed):
    bs = np.random.default_rng(seed)
    b = np.array([v[bs.integers(0, len(v), len(v))].mean() for _ in range(N_BOOT)])
    return float(v.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r76_absence_cannot_overlap.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    rows = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        rt, rlen = {}, {}
        for r in comp["responses"]:
            lab = r.get("response_index")
            if lab not in LAB:
                continue
            txt = resp_text(r)
            rt[lab] = toks(txt)
            rlen[lab] = len(txt.split())
        if len(rt) < 4:
            continue
        rk = {}
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            aid = asm.get("annotator_id")
            if w and aid:
                rk[aid] = ranks_from(w[0].get("ranking", ""))
        for c in rub.get("coval_full") or []:
            sc = c["scores"]
            if len(sc) != 1:
                continue
            aid, s = sc[0].get("annotator_id"), sc[0]["score"]
            if s == 0 or aid not in rk:
                continue
            ct = toks(c["criterion"])
            if not ct:
                continue
            vals = sorted(rk[aid].values())
            if vals[0] == vals[-1]:
                continue
            best = [l for l, v in rk[aid].items() if v == vals[0] and l in rt]
            worst = [l for l, v in rk[aid].items() if v == vals[-1] and l in rt]
            if not best or not worst:
                continue
            xs = np.array([rlen[l] for l in LAB], float)
            ys = np.array([contain(ct, rt[l]) for l in LAB], float)
            if np.std(xs) > 0:
                b1 = float(np.cov(xs, ys, bias=True)[0, 1] / np.var(xs))
                b0 = float(ys.mean() - b1 * xs.mean())
                res = {l: ys[i] - (b0 + b1 * xs[i]) for i, l in enumerate(LAB)}
            else:
                res = {l: ys[i] for i, l in enumerate(LAB)}
            rows.append({
                "pid": pid, "y": 1 if s > 0 else -1,
                "d_res": float(np.mean([res[l] for l in best]))
                         - float(np.mean([res[l] for l in worst])),
                "absent": bool(ABSENT.search(c["criterion"]))})
    if len(rows) < 1000:
        raise SystemExit(f"REFUSING: only {len(rows)} usable write-ins.")

    y = np.array([r["y"] for r in rows])
    d = np.array([r["d_res"] for r in rows])
    ab = np.array([r["absent"] for r in rows])
    pids = np.array([r["pid"] for r in rows])
    print(f"write-ins {len(rows)}   absence-shaped {int(ab.sum())} ({ab.mean():.1%})")
    print(f"  absence-shaped among POSITIVE {ab[y > 0].mean():.1%}   "
          f"among NEGATIVE {ab[y < 0].mean():.1%}")

    cells = {}
    print(f"\n{'cell':26s} {'n':>6} {'mean best-worst overlap':>26}")
    for sname, smask in (("positive", y > 0), ("negative", y < 0)):
        for aname, amask in (("presence-type", ~ab), ("absence-type", ab)):
            m = smask & amask
            if m.sum() < 100:
                cells[f"{sname}/{aname}"] = {"n": int(m.sum()), "insufficient": True}
                print(f"  {sname}/{aname:16s} {int(m.sum()):>6}   (too few, reported not used)")
                continue
            mm, lo, hi = boot_mean(d[m], 20260824 + len(sname) + len(aname))
            cells[f"{sname}/{aname}"] = {"n": int(m.sum()), "mean": mm, "ci": [lo, hi]}
            print(f"  {sname}/{aname:16s} {int(m.sum()):>6}   {mm:+.5f} [{lo:+.5f},{hi:+.5f}]")

    gaps = {}
    print(f"\n{'partition':26s} {'positive - negative gap':>26}")
    for aname, amask in (("presence-type", ~ab), ("absence-type", ab)):
        m = amask
        if (m & (y > 0)).sum() < 100 or (m & (y < 0)).sum() < 100:
            continue
        g = d[m & (y > 0)].mean() - d[m & (y < 0)].mean()
        lo, hi = boot_gap(d[m], y[m], pids[m], 20260830 + len(aname))
        gaps[aname] = {"gap": float(g), "ci": [lo, hi]}
        print(f"  {aname:24s} {g:+.5f} [{lo:+.5f},{hi:+.5f}]")

    rng = np.random.default_rng(20260840)
    sh = y.copy()
    rng.shuffle(sh)
    null = {k: float(d[(m) & (sh > 0)].mean() - d[(m) & (sh < 0)].mean())
            for k, m in (("presence-type", ~ab), ("absence-type", ab))}
    print(f"\n  NULL (signs shuffled): " +
          "   ".join(f"{k} {v:+.5f}" for k, v in null.items()))
    controls = {"shuffled_gaps": null,
                "all_pass": all(abs(v) < 0.006 for v in null.values())}
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: a shuffled-sign gap is not negligible.")

    pn = cells.get("negative/presence-type", {})
    pres_neg_tracks_worst = bool(pn.get("ci") and pn["ci"][1] < 0)
    pres_gap = gaps.get("presence-type", {}).get("gap", float("nan"))
    abs_gap = gaps.get("absence-type", {}).get("gap", float("nan"))
    if pres_neg_tracks_worst:
        world = "P NO-WORDS-TO-OVERLAP -- confirmed on its own prediction"
    elif np.isfinite(abs_gap) and abs(pres_gap) > 2 * abs(abs_gap):
        world = "P NO-WORDS-TO-OVERLAP (partial) -- effect concentrates in presence-type, but presence-negatives do not track the worst answer"
    else:
        world = "A ASYMMETRIC-ATTENTION -- the split does not explain it"

    verdict = (
        f"{world}. r75 found that a rater's positive criteria overlap the response they ranked best "
        f"while their negative criteria are flat, and entry 129 read that as a fact about raters: "
        f"praise is drawn from the menu, criticism is not. There is a mechanical rival: a criterion "
        f"about an ABSENCE -- 'fails to mention X', 'omits Y' -- cannot lexically overlap the text "
        f"that lacks it, so negative criteria would look flat because most of them are absence-shaped, "
        f"with no claim about attention involved. Absence-shaped wording is "
        f"{ab.mean():.1%} of write-ins overall, {ab[y > 0].mean():.1%} of positive ones and "
        f"{ab[y < 0].mean():.1%} of negative ones. Splitting the best-minus-worst overlap by both sign "
        f"and shape: "
        f"{', '.join(f'{k} {v['mean']:+.5f} [{v['ci'][0]:+.5f},{v['ci'][1]:+.5f}]' for k, v in cells.items() if 'mean' in v)}. "
        f"THE DECIDING PREDICTION is one the attention story does not make: under the mechanical "
        f"rival, PRESENCE-type negatives should track the WORST response, i.e. a negative cell mean. "
        f"They {'DO' if pres_neg_tracks_worst else 'DO NOT'}. The positive-minus-negative gap is "
        f"{pres_gap:+.5f} among presence-type criteria and {abs_gap:+.5f} among absence-type, against "
        f"shuffled-sign nulls of "
        f"{', '.join(f'{k} {v:+.5f}' for k, v in null.items())}. "
        f"WHAT THIS DOES TO ENTRY 129: "
        f"{'its sentence must be narrowed -- criticism is not less DRAWN from the menu, it is less lexically VISIBLE when drawn, and containment is blind to exactly one of the two things being compared' if pres_neg_tracks_worst else 'it survives the mechanical rival on the rivals own prediction, and the asymmetry remains a fact about what raters write rather than about what containment can see'}. "
        f"SCOPE UNCHANGED: this is still association within a rater, and still cannot separate a menu "
        f"that created the direction from a menu that supplied the words. That is S_pre."
    )

    doc = {
        "n": len(rows), "absence_share": float(ab.mean()),
        "absence_share_positive": float(ab[y > 0].mean()),
        "absence_share_negative": float(ab[y < 0].mean()),
        "cells": cells, "gaps": gaps, "controls": controls,
        "presence_negatives_track_worst": pres_neg_tracks_worst,
        "world": world,
        "outcome_variable_scope": (
            "Sign is the single author's own score; the ranking is that same author's own world "
            "block. Containment is lexical. No judge, no model gold head."),
        "scope": (
            "ABSENT is a regex over criterion CONSTRUCTIONS, not a semantic classifier: it matches "
            "'fails to', 'omits', 'lacks', 'no mention of' and similar, and deliberately does not "
            "match every sentence containing a negative word, because 'is not concise' describes a "
            "property the text HAS. Misclassification is therefore expected in both directions and "
            "would bias the split toward finding nothing. Cells below 100 items are reported with "
            "their count and not used."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
