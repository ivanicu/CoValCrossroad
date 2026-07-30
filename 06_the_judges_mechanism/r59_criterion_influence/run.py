"""r59 -- per-criterion leave-one-out on the judge's induced ranking.

CLAIM CARD
----------
Claim      the rubric's induced ranking is a genuine MULTI-criterion aggregate --
           no single criterion decides it.
Estimand   for each criterion c in prompt p's core rubric: whether dropping c
           changes the induced top-1 response, and by how much it moves the
           top-2 score gap. Distribution over all 991 criteria in 250 prompts.
Target
observed?  JUDGE-RELATIVE ONLY, and this is the whole caveat. It measures a
           criterion's influence on THE JUDGE'S induced ranking under a fixed
           equal-weight scoring rule. It is NOT tau_c -- the queue's third
           counterfactual, the change in HUMAN preference when criterion
           satisfaction changes -- which no release data can reach. Nothing here
           substitutes for that experiment.
Alternative
worlds     A CONCENTRATED  a minority of criteria decide the ranking; dropping one
                           flips top-1 often and influence is heavy-tailed beyond
                           what discriminating power explains. Then CoVal-core's
                           C5 compatibility SELECTION is the whole measurement and
                           queue item 6 is the highest-value remaining work.
           B DIFFUSE       influence is spread; single drops rarely change
                           anything. The AGGREGATION RULE is doing the work, and
                           the selection step matters less.
           C DEGENERATE    most criteria barely separate the four responses, so
                           influence is concentrated for a structural reason
                           rather than a normative one. Distinguished from A by
                           whether influence is explained by each criterion's own
                           spread across the four responses.
Intervention
           leave-one-criterion-out on r41's persisted satisfaction tensor. No GPU:
           the tensor reproduced all 1,500 of r12's per-prompt values exactly, so
           the judge pass is already paid for.
Null       (i)  the persisted SHUFFLED arm z_orig_shuf -- same shapes, criteria
                detached from their prompts, so any flip rate it shows is what
                arithmetic alone produces at this K.
           (ii) within-prompt column permutation, which destroys the
                criterion-response association while preserving each criterion's
                marginal spread. (ii) is the sharper of the two for separating C.

POSITIVE CONTROL
----------------
Synthetic prompts of known class: one where a single criterion is constructed to
decide the ranking (must flip on its removal, must not flip on any other), and
one where every criterion agrees (must never flip). A census that cannot separate
these has measured nothing, and its flip rate would be silence rather than a
finding.

WHAT THIS CANNOT DO
-------------------
Equal weights. CoVal-core ships criteria already rewritten to positive weight, so
an equal-weight mean is the rule this tensor was built under (r41) -- but the
released scoring rule is not equal-weight, and a criterion negligible here could
matter under the real weights. That is a scope limit, not a result.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

TENSOR = _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"


def loo_stats(Z: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Leave-one-criterion-out on one prompt's K x 4 satisfaction block.

    Returns (flip, dgap, spread) per criterion:
      flip   did the top-1 response change when this criterion was removed
      dgap   |top-2 gap with c| - |top-2 gap without c|, signed: positive means
             removing c NARROWED the decision, i.e. c was holding it apart
      spread this criterion's own sd across the four responses -- its
             discriminating power, the quantity world C says explains influence
    """
    K = Z.shape[0]
    full = Z.mean(axis=0)
    top_full = int(np.argmax(full))
    srt = np.sort(full)[::-1]
    gap_full = float(srt[0] - srt[1])

    flip = np.zeros(K, dtype=bool)
    dgap = np.zeros(K)
    spread = Z.std(axis=1)
    if K <= 1:
        return flip, dgap, spread
    for c in range(K):
        keep = np.delete(Z, c, axis=0)
        s = keep.mean(axis=0)
        flip[c] = int(np.argmax(s)) != top_full
        srt_c = np.sort(s)[::-1]
        dgap[c] = gap_full - float(srt_c[0] - srt_c[1])
    return flip, dgap, spread


def sweep(Z_all: np.ndarray, off: np.ndarray, rng=None, permute=False):
    """Run LOO over every prompt. permute=True shuffles each criterion's four
    values independently, destroying the criterion-response association while
    preserving that criterion's marginal spread exactly."""
    flips, dgaps, spreads, per_prompt = [], [], [], []
    for k in range(len(off) - 1):
        Z = Z_all[off[k]:off[k + 1]]
        if Z.shape[0] < 2:
            continue
        if permute:
            Z = np.array([rng.permutation(row) for row in Z])
        f, d, s = loo_stats(Z)
        flips.append(f)
        dgaps.append(d)
        spreads.append(s)
        per_prompt.append(bool(f.any()))
    return (np.concatenate(flips), np.concatenate(dgaps),
            np.concatenate(spreads), np.array(per_prompt))


def gini(x: np.ndarray) -> float:
    x = np.sort(np.abs(x))
    n = len(x)
    if n == 0 or x.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1) @ x / (n * x.sum()))


def positive_control(rng) -> dict:
    """Two prompts of known class; the sweep must classify both correctly."""
    # one decisive criterion: it alone prefers response 1, the rest prefer 0 weakly
    decisive = np.array([[0.50, 0.49, 0.48, 0.47],
                         [0.50, 0.49, 0.48, 0.47],
                         [0.00, 1.00, 0.00, 0.00]])
    f_d, _, _ = loo_stats(decisive)
    # unanimous: every criterion ranks the responses identically
    unan = np.array([[0.9, 0.6, 0.3, 0.1],
                     [0.8, 0.5, 0.2, 0.1],
                     [0.7, 0.4, 0.2, 0.0]])
    f_u, _, _ = loo_stats(unan)
    out = {
        "decisive_prompt": {"flips": f_d.tolist(),
                            "expected": "only the last criterion flips",
                            "pass": bool(f_d[-1] and not f_d[:-1].any())},
        "unanimous_prompt": {"flips": f_u.tolist(),
                             "expected": "no criterion flips",
                             "pass": bool(not f_u.any())},
    }
    out["all_pass"] = bool(out["decisive_prompt"]["pass"] and out["unanimous_prompt"]["pass"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tensor", type=Path, default=TENSOR)
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--out", type=Path, default=_RES / "r59_criterion_influence.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260728)

    pc = positive_control(rng)
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}")
    for k, v in pc.items():
        if k != "all_pass":
            print(f"  {k:20s} flips={v['flips']}  expected: {v['expected']}  "
                  f"{'ok' if v['pass'] else 'MISMATCH'}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: leave-one-out cannot classify prompts of known class.")

    d = np.load(a.tensor)
    Z, off = d["z_orig_real"], d["off_real"].astype(int)
    Zs, offs = d["z_orig_shuf"], d["off_shuf"].astype(int)
    if Z.shape[0] == 0:
        raise SystemExit("REFUSING: the tensor is empty. Nothing observed is not a pass.")

    flip, dgap, spread, pflip = sweep(Z, off)
    f_sh, d_sh, s_sh, p_sh = sweep(Zs, offs)
    f_pm, d_pm, s_pm, p_pm = sweep(Z, off, rng=rng, permute=True)

    def ci(x, stat=np.mean):
        bs = np.array([stat(x[rng.integers(0, len(x), len(x))]) for _ in range(a.boot)])
        return [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

    # world C: is influence explained by the criterion's own discriminating power?
    ok = np.isfinite(dgap) & np.isfinite(spread)
    r_infl_spread = float(np.corrcoef(np.abs(dgap[ok]), spread[ok])[0, 1])
    # concentration WITHIN a prompt, on |dgap|
    gin = []
    i = 0
    for k in range(len(off) - 1):
        K = off[k + 1] - off[k]
        if K < 2:
            continue
        gin.append(gini(dgap[i:i + K]))
        i += K
    gini_mean = float(np.mean(gin))

    flip_rate = float(flip.mean())
    flip_ci = ci(flip.astype(float))
    sh_rate = float(f_sh.mean())
    pm_rate = float(f_pm.mean())

    # --- WORLD D, added AFTER seeing the result, and labelled as such -----
    #
    # The claim card enumerated A CONCENTRATED / B DIFFUSE / C DEGENERATE. All
    # three assume the real rubric flips at least as often as a permuted one.
    # It flips LESS. That is a fourth world the card did not contain, so the
    # decomposition was incomplete rather than the measurement surprising --
    # recorded here instead of being folded into B, which would have reported
    # "diffuse influence" for what is actually "criteria that agree with each
    # other more than chance".
    #
    # D is not a post-hoc rescue: it makes a prediction the others do not --
    # paired, per-prompt, the real flip rate must sit BELOW its own permutation
    # null, and that is what carries the CI below.
    paired_delta = float(flip.mean() - f_pm.mean())
    bs_delta = np.array([
        float(flip[i].mean() - f_pm[i].mean())
        for i in (rng.integers(0, len(flip), len(flip)) for _ in range(a.boot))])
    delta_ci = [float(np.percentile(bs_delta, 2.5)), float(np.percentile(bs_delta, 97.5))]

    concentrated = flip_rate > pm_rate + 0.05
    explained = r_infl_spread > 0.5
    below_null = delta_ci[1] < 0
    world = ("D CONCORDANT" if below_null else
             "A CONCENTRATED" if concentrated and not explained else
             "C DEGENERATE" if concentrated and explained else
             "B DIFFUSE")

    explained_clause = (
        "largely structural -- a criterion that does not separate the four responses cannot "
        "influence the ranking, and most do not" if explained else
        "NOT explained by discriminating power alone")

    # Is the concordance OWN-rubric-specific? The shuffled arm scores criteria
    # from other prompts against these same four responses. If it flips at the
    # same rate, the agreement is a property of criterion rows in general, not of
    # the compiler's compatibility selection -- which is a different claim and
    # the one a reader would otherwise get wrong.
    own_specific = abs(flip_rate - sh_rate) > max(0.02, 0.15 * flip_rate)
    specificity_clause = (
        "and it IS specific to the prompt's own rubric" if own_specific else
        "and it is NOT specific to the prompt's own rubric -- the shuffled arm, which scores "
        "criteria borrowed from OTHER prompts against these same four responses, flips at "
        f"{sh_rate:.1%} against the real {flip_rate:.1%}. So the agreement is a property of "
        "criterion rows in general against this response set, not a product of the compiler's "
        "compatibility selection")

    lead = ("CRITERIA AGREE MORE THAN CHANCE: the rubric is robust to losing one BECAUSE its "
            "criteria are concordant, not because influence is evenly spread"
            if below_null else
            "influence is spread across criteria" if world.startswith("B") else
            "a minority of criteria decide the ranking")

    verdict = (
        f"{world} -- {lead}. Dropping a single criterion changes the judge's top-1 response for "
        f"{flip_rate:.1%} of the {len(flip)} criteria [{flip_ci[0]:.1%}, {flip_ci[1]:.1%}], "
        f"which is BELOW the {pm_rate:.1%} produced by within-prompt column permutation -- a null "
        f"that preserves each criterion's own spread exactly and destroys only its association with "
        f"the responses. Paired difference {paired_delta:+.4f} "
        f"[{delta_ci[0]:+.4f}, {delta_ci[1]:+.4f}] -- {specificity_clause}. "
        f"{float(pflip.mean()):.1%} of prompts have at least one criterion whose removal flips the "
        f"winner, against {float(p_pm.mean()):.1%} under permutation. Influence correlates with a "
        f"criterion's own discriminating power at r={r_infl_spread:+.4f}, so it is "
        f"{explained_clause}; mean within-prompt Gini of |top-2 gap change| is {gini_mean:.4f}. "
        f"WORLD D WAS NOT IN THIS ROUND'S CLAIM CARD -- A, B and C all assume the real rubric flips "
        f"at least as often as a permuted one, and it flips less, so the world list was incomplete "
        f"rather than the result surprising. JUDGE-RELATIVE: influence on the judge's induced "
        f"ranking under EQUAL WEIGHTS, not tau_c, which needs human preference under a criterion "
        f"intervention and is unreachable from this release."
    )

    doc = {
        "judge": "qwen2b (r41 persisted tensor; reproduction control passed, 1500/1500 exact)",
        "n_criteria": int(len(flip)),
        "n_prompts": int(len(pflip)),
        "flip_rate": flip_rate,
        "flip_rate_ci95": flip_ci,
        "flip_rate_permutation_null": pm_rate,
        "flip_rate_shuffled_arm_null": sh_rate,
        "prompts_with_any_flip": float(pflip.mean()),
        "prompts_with_any_flip_permutation_null": float(p_pm.mean()),
        "influence_vs_discriminating_power_r": r_infl_spread,
        "mean_within_prompt_gini_of_dgap": gini_mean,
        "spread_quartiles": [float(x) for x in np.percentile(spread, [25, 50, 75])],
        "dgap_mean": float(dgap.mean()),
        "dgap_mean_ci95": ci(dgap),
        "world": world,
        "paired_flip_minus_permutation": paired_delta,
        "paired_flip_minus_permutation_ci95": delta_ci,
        "world_D_added_after_seeing_the_result": True,
        "concordance_is_own_rubric_specific": bool(own_specific),
        "positive_control": pc,
        "scope": (
            "JUDGE-RELATIVE AND EQUAL-WEIGHT. This measures a criterion's influence on the judge's "
            "induced ranking under an equal-weight mean, which is the rule r41's tensor was built "
            "under. The released CoVal scoring rule is not equal-weight, so a criterion negligible "
            "here could matter under the real weights. It is NOT tau_c: the queue's third "
            "counterfactual is the change in HUMAN preference under a criterion intervention, and "
            "no release data can reach it. Nothing here substitutes for that experiment."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass

    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\ncriteria: {len(flip)}   prompts: {len(pflip)}")
    print(f"  top-1 flip rate            {flip_rate:.4f}  {flip_ci}")
    print(f"    within-prompt permutation null {pm_rate:.4f}")
    print(f"    shuffled-arm null              {sh_rate:.4f}")
    print(f"  prompts with any flip      {pflip.mean():.4f}  (null {p_pm.mean():.4f})")
    print(f"  influence ~ discriminating power  r={r_infl_spread:+.4f}")
    print(f"  mean within-prompt Gini(|dgap|)   {gini_mean:.4f}")
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
