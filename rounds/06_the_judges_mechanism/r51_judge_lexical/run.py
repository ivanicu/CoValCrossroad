"""r51 -- does the satisfaction judge score lexical overlap?

CLAIM_CARD.md is the contract.  Every cross-rater result here runs through one
instrument: the judge answering "does response r satisfy criterion c?".  r04
validated it in aggregate against held-out human rankings.  Nothing asked what
it is USING.

r50 supplies the reason to ask: criteria whose words overlap the four candidates
carry more of the cross-rater direction.  The values reading is that concrete
criteria discriminate better.  The instrument reading is that the judge scores
overlap, so overlapping criteria are the ones it gets right -- a fact about J,
not about R or P.

Read the SIGNED mean, whose null is zero by symmetry.  At four responses per
prompt two independent vectors give E|r| ~ 0.50, so a bare magnitude here would
repeat entry 49.
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
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join  # noqa: E402

OUTCOME_SCOPE = (
    "Descriptive on the judge's own outputs. No human rankings and no model preference "
    "proxy enter this round; the quantity is the judge's satisfaction score and a "
    "text statistic."
)
STOP = set("the a an and or of to in for on with is are be that this it as at by from "
           "not no should must does do response answer model user its their they".split())


def toks(s):
    return [w for w in re.findall(r"[a-z']{3,}", str(s).lower()) if w not in STOP]


def corr(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])


def partial(y, x):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if np.std(x) < 1e-12:
        return y - y.mean()
    b = np.cov(x, y, bias=True)[0, 1] / np.var(x)
    return y - (b * (x - x.mean()) + y.mean())


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r51_judge_lexical.json")
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--nperm", type=int, default=200)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.boot, a.nperm = 200, 20
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    LAB = ["A", "B", "C", "D"]
    rows = []          # (rho, rho_lenctl, polarity, pid, ci)
    synth_rows = []    # positive control
    rng = np.random.default_rng(20260728)
    perm_rows = defaultdict(list)

    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in sat:
            continue
        items = rub.get("coval_full") or []
        resp = [r["messages"][0]["content"] for r in comp["responses"]]
        if not items or len(resp) < 4:
            continue
        rtok = [set(toks(t)) for t in resp[:4]]
        rlen = np.array([len(toks(t)) for t in resp[:4]], dtype=float)
        labs = [l for l in LAB]
        for ci, it in enumerate(items):
            sc = it.get("scores") or []
            ct = set(toks(it["criterion"]))
            if not ct or not sc:
                continue
            s_vec = [sat[pid].get((ci, l)) for l in labs]
            if any(v is None for v in s_vec):
                continue
            ov = np.array([len(ct & rt) / max(len(ct), 1) for rt in rtok])
            r = corr(ov, s_vec)
            if not np.isfinite(r):
                continue
            pol = "positive" if np.mean([float(x["score"]) for x in sc]) >= 0 else "negative"
            rows.append((r, corr(partial(np.array(ov), rlen),
                                 partial(np.array(s_vec, float), rlen)), pol))
            # NULL: break the (criterion, response) pairing, keep both marginals
            for _ in range(3):
                perm_rows["null"].append(corr(rng.permutation(ov), s_vec))

        # ESTIMATOR-RECOVERY CHECK -- and it is NOT the positive control the
        # claim card asked for.  The card said a criterion built from one
        # response's tokens must be SCORED BY THE JUDGE and come back
        # overlap-driven.  That needs a GPU pass; this does not call the judge
        # at all.  What it checks is only that a 4-point correlation recovers a
        # planted link, which is nearly tautological.
        #
        # Recorded as a KNOWN GAP rather than passed off as the control:
        # world "judge is a string matcher" is not positively controlled here,
        # so a NULL result below is weaker than the card promised.
        for j in range(4):
            src = toks(resp[j])
            if len(src) < 8:
                continue
            fake = set(rng.choice(src, size=8, replace=False))
            ovf = np.array([len(fake & rt) / len(fake) for rt in rtok])
            planted = ovf + rng.normal(scale=0.05, size=4)
            synth_rows.append(corr(ovf, planted))

    R = np.array([r[0] for r in rows], dtype=float)
    RL = np.array([r[1] for r in rows], dtype=float)
    POL = np.array([r[2] for r in rows])
    NULL = np.array(perm_rows["null"], dtype=float)
    SYN = np.array(synth_rows, dtype=float)
    R, RL = R[np.isfinite(R)], RL[np.isfinite(RL)]
    NULL, SYN = NULL[np.isfinite(NULL)], SYN[np.isfinite(SYN)]

    def ci(x):
        bs = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(x.mean()), float(lo), float(hi)

    print(f"(prompt, criterion) cells with a usable correlation: {len(R):,}")
    sm, slo, shi = ci(SYN)
    print(f"\nestimator recovery (planted link, judge NOT involved): {sm:+.4f} "
          f"[{slo:+.4f},{shi:+.4f}]")
    pc_ok = bool(slo > 0.5)
    print(f"  -> {'the 4-point estimator recovers a planted link' if pc_ok else 'FAILS'}")
    print("  ! THIS IS NOT THE POSITIVE CONTROL THE CLAIM CARD ASKED FOR. That one needs")
    print("    the JUDGE to score a criterion copied out of a response, which is a GPU")
    print("    pass. Until it runs, a null below is UNDERCONTROLLED, not an acquittal.")
    if not pc_ok:
        raise SystemExit("REFUSING TO REPORT: the estimator cannot recover a planted "
                         "link at n=4, so nothing below is measurable")

    nm, nlo, nhi = ci(NULL)
    om, olo, ohi = ci(R)
    lm, llo, lhi = ci(RL)
    print(f"\nmean SIGNED corr(overlap, judge satisfaction)   {om:+.4f} [{olo:+.4f},{ohi:+.4f}]")
    print(f"  response-permutation null                     {nm:+.4f} [{nlo:+.4f},{nhi:+.4f}]")
    print(f"  with response LENGTH partialled out           {lm:+.4f} [{llo:+.4f},{lhi:+.4f}]")
    print(f"  (magnitude is NOT the headline: at n=4, E|r| between independent")
    print(f"   vectors is ~0.50 -- entry 49. The signed null is 0 by symmetry.)")

    pol_out = {}
    for pol in ("positive", "negative"):
        sel = R[: len(POL)][POL[: len(R)] == pol] if len(POL) >= len(R) else np.array([])
        if len(sel) >= 30:
            m, lo, hi = ci(sel)
            pol_out[pol] = {"mean": m, "ci": [lo, hi], "n": int(len(sel))}
            print(f"  criteria with {pol:8s} human mean rating: {m:+.4f} [{lo:+.4f},{hi:+.4f}]"
                  f"  n={len(sel):,}")
    if len(pol_out) == 2:
        d = pol_out["positive"]["mean"] - pol_out["negative"]["mean"]
        print(f"  positive minus negative: {d:+.4f}   <- a NEGATION TRAP would make this large")

    excess = om - nm
    # 0.15 is a STIPULATION separating "present" from "large", not a measurement.
    # It is named in the output so a reader can apply their own, the way r42's
    # delta is swept rather than inherited.
    STRONG_AT = 0.15
    strong = bool(olo > nhi and excess > STRONG_AT)
    present = bool(olo > nhi)
    if strong:
        verdict = (
            f"THE JUDGE SCORES LEXICAL OVERLAP. Within a fixed (prompt, criterion), its "
            f"satisfaction across the four responses tracks word overlap at {om:+.4f} "
            f"against a response-permutation null of {nm:+.4f} -- an excess of "
            f"{excess:+.4f} -- and {lm:+.4f} with response length partialled out. r50's "
            f"anchoring result must be reread as a property of J, and every round using "
            f"the satisfaction layer inherits the scope note. ⚠ 'LARGE' HERE IS A "
            f"STIPULATION: the excess is called large because it clears {STRONG_AT}, a "
            f"threshold I chose and not one the data supplies -- the number to carry is "
            f"{excess:+.4f}. NOT ESTABLISHED that this is "
            f"ERROR: overlap and genuine satisfaction are correlated in the world, and "
            f"this release has no satisfaction ground truth to set the honest ceiling")
    elif present:
        verdict = (
            f"OVERLAP IS PRESENT IN THE JUDGE'S SCORES BUT MODEST: {om:+.4f} "
            f"[{olo:+.4f},{ohi:+.4f}] against a null of {nm:+.4f}, "
            f"{lm:+.4f} with length partialled out. It is real and it is not large enough "
            f"to reduce the satisfaction layer to string matching. r50's anchoring effect "
            f"is not thereby explained away, and is not thereby cleared either -- the "
            f"instrument channel exists and its size relative to the values channel is "
            f"unmeasured. NO CEILING: overlap and true satisfaction covary in the world, "
            f"so no part of this is established as ERROR")
    else:
        verdict = (
            f"NOT DETECTABLY SCORING OVERLAP, AND UNDERCONTROLLED: {om:+.4f} "
            f"[{olo:+.4f},{ohi:+.4f}] against a permutation null of {nm:+.4f}. The "
            f"instrument reading of r50 loses its mechanism -- but the claim card's "
            f"positive control was NOT run: it requires the judge to score a criterion "
            f"copied out of a response, which needs a GPU pass. A null from an instrument "
            f"that has never been shown to detect the thing it is looking for is silence, "
            f"so this is UNVERIFIED rather than negative")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "cells": int(len(R)),
        "mean_signed_corr": [om, olo, ohi],
        "permutation_null": [nm, nlo, nhi],
        "length_controlled": [lm, llo, lhi],
        "estimator_recovery_planted": [sm, slo, shi],
        "positive_control_status": (
            "NOT RUN. The claim card's control requires the JUDGE to score a criterion "
            "copied out of a response; that is a GPU pass and was not done. The check "
            "reported here only shows a 4-point correlation recovers a planted link, "
            "which is nearly tautological and does not license reading a null as absence."),
        "by_polarity": pol_out,
        "excess_over_null": excess,
        "strong_threshold_is_stipulated": STRONG_AT,
        "verdict": verdict,
        "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Signed correlation only; at n=4 responses a bare |r| is ~0.50 under "
                  "independence (entry 49). This measures whether the judge's output MOVES "
                  "with lexical overlap. It does NOT establish that overlap-driven scoring "
                  "is erroneous: overlap and genuine satisfaction are correlated in the "
                  "world, and the release contains no satisfaction ground truth against "
                  "which to set the ceiling a correct judge would show."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
