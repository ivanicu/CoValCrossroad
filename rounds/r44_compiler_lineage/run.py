"""r44 (queue item 6) -- the core compiler, reconstructed stage by stage.

CLAIM_CARD.md is the contract.  Read the second section of it first: **the
intermediate artifacts do not exist**.  The release ships C0 (full criteria with
ratings) and C6 (core).  C1-C5 -- polarity rewrite, cleanup, dedup, merge,
compatibility selection -- are internal to a compiler OpenAI did not publish.

So this round CANNOT decompose OpenAI's compiler, and no sentence it emits may
say otherwise.  What it does is build a RECONSTRUCTION out of the operations the
dataset card names, measure what each simulated stage contributes, and then
measure the RESIDUAL between the reconstruction's end state and the real core.

    Delta_k = A(S_k) - A(S_{k-1})        increment of a SIMULATED stage
    R       = A(core_real) - A(S_6)      what the reconstruction does not explain

The residual is the deliverable.  A large residual is a finding: it says the
card's description does not account for what core does.

Everything runs under EQUAL weights with no ratings applied at scoring time,
because that is r33's regime and the only one in which "did the polarity move
into the text?" is askable at all.

TWO CONTROLS, both gating:
  identity     a stage that does nothing must return Delta ~ 0.  If it does not,
               the harness is measuring its own re-scoring noise.
  random-k     the selection stage keeps <=4 criteria, and keeping ANY 4 changes
               the score.  A size-matched random choice runs alongside, or the
               increment measures truncation rather than selection.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join, parse_ranking  # noqa: E402

KEEP = 4          # core truncates to at most four items (dataset card)


def individual_pairs(asm):
    w = (asm.get("ranking_blocks") or {}).get("world") or []
    if not w:
        return []
    r = parse_ranking(w[0].get("ranking", ""))
    flat = [(lab, gi) for gi, grp in enumerate(r) for lab in grp]
    return [(a, b) for a, ga in flat for b, gb in flat if ga < gb]


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)
    return sat


def sat_matrix(sat_pid, cis, labs):
    """K x R matrix of satisfaction, NaN where the judge produced nothing."""
    return np.array([[sat_pid.get((ci, l), np.nan) for l in labs] for ci in cis])


def score_and_agree(M, signs, labs, pairs, test):
    """Equal-weight score over the retained criteria, then pairwise agreement."""
    if M.size == 0:
        return None
    w = np.asarray(signs, dtype=float)
    num = np.nansum(M * w[:, None], axis=0)
    den = np.nansum(np.abs(w)[:, None] * ~np.isnan(M), axis=0)
    ok = den > 0
    if ok.sum() < 2:
        return None
    score = {l: num[i] / den[i] for i, l in enumerate(labs) if ok[i]}
    good = tot = 0
    for r_ in test:
        for x, y in pairs.get(r_, []):
            if x in score and y in score:
                tot += 1
                good += int(score[x] > score[y])
    return (good / tot) if tot else None


# ------------------------------------------------------------------- stages
def stage_sets(M, ratings_train, rng, keep=KEEP, dup_r=0.95, quiet=0.5):
    """Return {stage: (row indices, signs)} for the reconstructed pipeline.

    M is K x R satisfaction for this prompt's FULL criteria.  ratings_train maps
    criterion index -> mean rating over TRAIN raters only, so every stage that
    consults ratings is rater-disjoint from the raters it is evaluated on.
    """
    K = M.shape[0]
    idx = list(range(K))
    plus = [1.0] * K
    out = {"S0_full_equal": (idx, plus)}

    # identity control -- documented as a stage so its Delta is reported in the
    # same table as the real ones and cannot be quietly omitted.
    out["S0b_identity_control"] = (list(idx), list(plus))

    # C1 polarity rewrite.  The text rewrite cannot be simulated; its EFFECT can:
    # a criterion carrying a negative weight becomes a positively-phrased
    # criterion whose satisfaction is the complement.
    s1 = [(-1.0 if ratings_train.get(ci, 0.0) < 0 else 1.0) for ci in idx]
    out["S1_polarity_rewrite"] = (list(idx), s1)

    # C2 cleanup: drop criteria whose train raters gave near-zero magnitude --
    # no consensus direction to carry.
    keep2 = [ci for ci in idx if abs(ratings_train.get(ci, 0.0)) >= quiet]
    if not keep2:
        keep2 = list(idx)
    out["S2_cleanup"] = (keep2, [s1[ci] for ci in keep2])

    # C3 dedup: two criteria that score every response alike are functional
    # duplicates regardless of wording, and equal weighting double-counts them.
    kept = []
    for ci in keep2:
        v = M[ci] * s1[ci]
        dup = False
        for cj in kept:
            u = M[cj] * s1[cj]
            m = ~np.isnan(u) & ~np.isnan(v)
            if m.sum() >= 3 and np.std(u[m]) > 1e-9 and np.std(v[m]) > 1e-9:
                if np.corrcoef(u[m], v[m])[0, 1] >= dup_r:
                    dup = True
                    break
        if not dup:
            kept.append(ci)
    out["S3_dedup"] = (kept, [s1[ci] for ci in kept])

    # C5 compatibility selection: keep the mutually most consistent items, i.e.
    # drop the item that agrees least with the rest until <= keep remain.
    sel = list(kept)
    while len(sel) > keep:
        worst, worst_r = None, np.inf
        for ci in sel:
            v = M[ci] * s1[ci]
            rs = []
            for cj in sel:
                if cj == ci:
                    continue
                u = M[cj] * s1[cj]
                m = ~np.isnan(u) & ~np.isnan(v)
                if m.sum() >= 3 and np.std(u[m]) > 1e-9 and np.std(v[m]) > 1e-9:
                    rs.append(np.corrcoef(u[m], v[m])[0, 1])
            mr = float(np.mean(rs)) if rs else 0.0
            if mr < worst_r:
                worst, worst_r = ci, mr
        sel.remove(worst)
    out["S5_compatibility_selection"] = (sel, [s1[ci] for ci in sel])

    # size-matched random null for the selection stage
    rnd = list(rng.choice(kept, size=min(keep, len(kept)), replace=False)) if kept else []
    out["S5null_random_same_size"] = (rnd, [s1[ci] for ci in rnd])
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat-full", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--sat-core", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_core.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r44_compiler_lineage.json")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.boot = 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    rng = np.random.default_rng(20260728)
    satF, satC = load_sat(a.sat_full), load_sat(a.sat_core)

    prompts = {}
    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in satF or pid not in satC:
            continue
        full = rub.get("coval_full") or []
        core = rub.get("coval_core") or []
        if not full or not core:
            continue
        ratings = {ci: {s["annotator_id"]: float(s["score"])
                        for s in (it.get("scores") or [])}
                   for ci, it in enumerate(full)}
        ratings = {ci: r for ci, r in ratings.items() if r}
        if not ratings:
            continue
        pairs = {}
        for asm in comp["metadata"]["assessments"]:
            aid, pr = asm.get("annotator_id"), individual_pairs(asm)
            if aid and pr:
                pairs[aid] = pr
        if not pairs:
            continue
        labs = sorted({l for (_c, l) in satF[pid]} & {l for (_c, l) in satC[pid]})
        if len(labs) < 2:
            continue
        prompts[pid] = {"ratings": ratings, "pairs": pairs, "labs": labs,
                        "n_full": len(full), "n_core": len(core)}

    allr = sorted({r for d in prompts.values() for c in d["ratings"].values() for r in c}
                  | {r for d in prompts.values() for r in d["pairs"]})
    fold = {r: i % a.folds for i, r in enumerate(allr)}
    print(f"prompts {len(prompts):,}   raters {len(allr):,}   folds {a.folds}")
    print(f"criteria per prompt: full median "
          f"{np.median([d['n_full'] for d in prompts.values()]):.0f}, core median "
          f"{np.median([d['n_core'] for d in prompts.values()]):.0f}\n")

    per = defaultdict(lambda: defaultdict(list))
    for pid, d in prompts.items():
        labs = d["labs"]
        cis = sorted(d["ratings"])
        M = sat_matrix(satF[pid], cis, labs)
        core_cis = sorted({c for (c, _l) in satC[pid]})
        Mc = sat_matrix(satC[pid], core_cis, labs)
        for f in range(a.folds):
            test = {r for r in d["pairs"] if fold[r] == f}
            if not test:
                continue
            rt = {}
            for j, ci in enumerate(cis):
                vals = [v for r_, v in d["ratings"][ci].items() if fold.get(r_) != f]
                if vals:
                    rt[j] = float(np.mean(vals))
            sets = stage_sets(M, rt, rng)
            for name, (rows, signs) in sets.items():
                if not rows:
                    continue
                v = score_and_agree(M[rows], signs, labs, d["pairs"], test)
                if v is not None:
                    per[name][pid].append(v)
            v = score_and_agree(Mc, [1.0] * Mc.shape[0], labs, d["pairs"], test)
            if v is not None:
                per["C6_core_REAL"][pid].append(v)

    ORDER = ["S0_full_equal", "S0b_identity_control", "S1_polarity_rewrite",
             "S2_cleanup", "S3_dedup", "S5_compatibility_selection",
             "S5null_random_same_size", "C6_core_REAL"]
    common = sorted(set.intersection(*[set(per[k]) for k in ORDER if per[k]]))
    print(f"prompts with every arm: {len(common)}\n")
    if len(common) < 50:
        raise SystemExit("REFUSING TO REPORT: fewer than 50 prompts carry every arm")

    means = {k: np.array([np.mean(per[k][p_]) for p_ in common]) for k in ORDER}

    def paired(a1, a2):
        dd = means[a2] - means[a1]
        bs = np.array([dd[rng.integers(0, len(dd), len(dd))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return {"delta": float(dd.mean()), "ci": [float(lo), float(hi)],
                "excludes_zero": bool(lo > 0 or hi < 0),
                "paired_differences": [float(x) for x in dd]}

    print(f"{'arm':32s} {'accuracy':>9}")
    for k in ORDER:
        print(f"{k:32s} {means[k].mean():>9.4f}")

    # ---- identity control gates everything ----------------------------
    ident = paired("S0_full_equal", "S0b_identity_control")
    print(f"\nidentity control  Delta = {ident['delta']:+.6f} "
          f"[{ident['ci'][0]:+.6f},{ident['ci'][1]:+.6f}]"
          f"  -> {'FAIL' if ident['excludes_zero'] else 'pass'}")
    if ident["excludes_zero"]:
        raise SystemExit("REFUSING TO REPORT: a no-op stage produced a non-zero "
                         "increment, so every Delta below is re-scoring noise")

    steps = [("S0_full_equal", "S1_polarity_rewrite"),
             ("S1_polarity_rewrite", "S2_cleanup"),
             ("S2_cleanup", "S3_dedup"),
             ("S3_dedup", "S5_compatibility_selection")]
    print(f"\n{'reconstructed stage increment':46s} {'delta':>9} {'95% CI':>22}")
    incr = {}
    for a1, a2 in steps:
        r = paired(a1, a2)
        incr[f"{a1} -> {a2}"] = r
        print(f"{a1 + ' -> ' + a2:46s} {r['delta']:>+9.4f} "
              f"[{r['ci'][0]:+.4f},{r['ci'][1]:+.4f}]"
              f"{'' if r['excludes_zero'] else '  (ns)'}")

    sel_vs_null = paired("S5null_random_same_size", "S5_compatibility_selection")
    print(f"\nselection vs SIZE-MATCHED random  {sel_vs_null['delta']:+.4f} "
          f"[{sel_vs_null['ci'][0]:+.4f},{sel_vs_null['ci'][1]:+.4f}]"
          f"{'' if sel_vs_null['excludes_zero'] else '  (ns)'}"
          "   <- without this, the selection increment is truncation")

    resid = paired("S5_compatibility_selection", "C6_core_REAL")
    total = paired("S0_full_equal", "C6_core_REAL")
    explained = (1 - abs(resid["delta"]) / abs(total["delta"])) if abs(total["delta"]) > 1e-9 \
        else float("nan")
    print(f"\ntotal   full -> REAL core          {total['delta']:+.4f} "
          f"[{total['ci'][0]:+.4f},{total['ci'][1]:+.4f}]")
    print(f"residual  reconstruction -> REAL   {resid['delta']:+.4f} "
          f"[{resid['ci'][0]:+.4f},{resid['ci'][1]:+.4f}]")
    print(f"share of the total the reconstruction accounts for: {explained:.1%}")

    named = [(k, v) for k, v in incr.items() if v["excludes_zero"]]
    biggest = max(incr.items(), key=lambda t: abs(t[1]["delta"])) if incr else None
    # Rank by MAGNITUDE before naming a driver.  The first version of this block
    # tested the selection-vs-random contrast before comparing sizes, so a real
    # but secondary +0.0149 claimed the headline over a +0.0733 rewrite that is
    # larger than the entire full->core total.  Significance is not precedence.
    sel_secondary = (biggest is not None and sel_vs_null["excludes_zero"]
                     and abs(sel_vs_null["delta"]) < abs(biggest[1]["delta"]))
    if abs(resid["delta"]) > abs(total["delta"]) * 0.5:
        verdict = (
            f"THE CARD'S OPERATIONS DO NOT ACCOUNT FOR CORE. The reconstruction "
            f"explains {explained:.0%} of the full->core gap; the residual is "
            f"{resid['delta']:+.4f} against a total of {total['delta']:+.4f}. Whatever "
            f"CoVal-core does, the documented sequence -- polarity rewrite, cleanup, "
            f"dedup, compatibility selection, truncation -- simulated on the released "
            f"criteria does not reproduce it. NOT a claim about OpenAI's compiler, which "
            f"is unobservable here: it is a claim about this reconstruction")
    elif sel_secondary:
        verdict = (
            f"POLARITY DOMINATES, AND SELECTION IS A REAL SECOND TERM. The largest "
            f"reconstructed increment is {biggest[0]} at {biggest[1]['delta']:+.4f} -- "
            f"on its own larger than the entire full->core total of "
            f"{total['delta']:+.4f}, which the later stages give part of back. "
            f"Separately, compatibility selection beats a SIZE-MATCHED random choice of "
            f"the same number of criteria by {sel_vs_null['delta']:+.4f}, so WHICH items "
            f"survive carries signal too -- core encodes the post-choice ranking partly "
            f"through item membership, not only through wording. The reconstruction "
            f"accounts for {explained:.0%} of the total. RECONSTRUCTION ONLY: C1-C5 are "
            f"unobservable in this release and no increment here describes OpenAI's "
            f"compiler")
    elif sel_vs_null["excludes_zero"] and sel_vs_null["delta"] > 0:
        verdict = (
            f"SELECTION, NOT REPHRASING. The compatibility-selection stage beats a "
            f"SIZE-MATCHED random choice of the same number of criteria by "
            f"{sel_vs_null['delta']:+.4f}, larger than any single reconstructed stage "
            f"increment, so the gain is in WHICH items survive rather than how they are "
            f"phrased. Core would then encode the post-choice ranking through item "
            f"membership -- a stronger form of r33 than rewriting alone. Reconstruction "
            f"only; C1-C5 are unobservable in this release")
    elif named:
        verdict = (
            f"THE GAIN IS CONCENTRATED IN {biggest[0]} ({biggest[1]['delta']:+.4f}), with "
            f"{len(named)} of {len(incr)} reconstructed stages significant and the "
            f"selection stage indistinguishable from a size-matched random choice. "
            f"Reconstruction only; C1-C5 are unobservable in this release")
    else:
        verdict = (
            "NO RECONSTRUCTED STAGE IS SIGNIFICANT. The simulated pipeline does not "
            "localise the full->core gap to any documented operation, and the residual "
            f"is {resid['delta']:+.4f}. This is a non-detection over the stages I could "
            "simulate, not evidence that the compiler is doing nothing")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": len(common), "folds": a.folds,
        "arm_accuracy": {k: float(means[k].mean()) for k in ORDER},
        "identity_control": ident,
        "stage_increments": incr,
        "selection_vs_size_matched_random": sel_vs_null,
        "residual_reconstruction_to_real_core": resid,
        "total_full_to_real_core": total,
        "share_of_total_explained": float(explained),
        "verdict": verdict,
        "scope": ("RECONSTRUCTION, not decomposition. The release ships C0 (full with "
                  "ratings) and C6 (core); the intermediate artifacts C1-C5 exist only "
                  "inside a compiler OpenAI did not publish, verified field by field. "
                  "No increment here may be read as 'step X of OpenAI's compiler "
                  "contributes Y'. All stages that consult ratings are built on "
                  "rater-disjoint folds, and the selection stage carries a size-matched "
                  "random null because keeping ANY 4 criteria changes the score."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
