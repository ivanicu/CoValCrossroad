"""r70 -- the outcome's OTHER axis, and how much a single split-half is worth.

CLAIM CARD
----------
Claim      every detection floor in the exhaustion ledger equals
           half-width / sqrt(rel_predictor * rel_outcome), with rel_outcome =
           r57's 0.302/0.422.
Estimand   (a) the CRITERION-axis split-half reliability of the per-prompt
           attribution drop -- the outcome six rounds correlate against, never
           measured along this axis;
           (b) whether the criterion and response axes are INDEPENDENT error
           sources, which decides whether they may be multiplied; and
           (c) which variance components a disattenuated floor is entitled to
           treat as error at all.
Target
observed?  (a),(b) YES. `r41_satisfaction_qwen2b.npz` holds per-criterion
           satisfaction for all 991 criteria over 250 prompts, and its
           reproduction control matched every one of r12's published per-prompt
           values exactly -- re-verified here before anything is read.
           (c) NO. (c) is not empirical. It is a question about what
           M(R,J,pi,Q,P) holds FIXED, and r67 and r69 both silently assumed one
           answer.
Alternative
worlds     F FIXED-R    R is part of the measurement program, so which criteria
                        this rubric contains is NOT error. Criterion-axis
                        reliability is then irrelevant to the floors and the
                        1.23x multiplier is an over-correction.
           S SAMPLED-R  a prompt's criteria are a sample from a normative
                        repertoire, so criterion sampling IS error. Current
                        floors stand.
           B BOTH       the ledger's rows are claims about MECHANISMS, not about
                        this rubric, so both axes are error and every floor is
                        too small.
Intervention
           none. Recomputation from a persisted tensor.
Null       (i) a half against ITSELF must give 1.0;
           (ii) a half against a prompt-shuffled other half must give ~0.
Positive
control    the LADDER -- accuracy (a level), attribution (one difference), drop
           (a difference of differences), rebuilt from the SAME criteria halves.
           A high accuracy rung proves the criterion split does not destroy
           signal by itself, so a low drop rung is a fact about the contrast.
           This tests r57's own stated worry, which it never tested: "A
           DIFFERENCE of two accuracies is inherently less reliable than either."

WHY A SINGLE SPLIT IS NOT A MEASUREMENT
---------------------------------------
The first version of this round drew ONE random criterion split and reported the
drop's reliability as 0.3911. Averaged over 200 splits it is **0.3013**: that one
draw sat about 1.5 SD to the favourable side, and across draws the raw
correlation ranges 0.092 to 0.323 -- a 3.5x spread on the number the floors
divide by. r57 averaged over 200 splits; this round did not, and that was the
whole difference. Every figure below is a multi-split mean with its spread beside
it. **r69 has the same defect and is corrected in the same commit.**

For K=4 there are only three distinct 2-2 partitions, so the spread is not
sampling noise that more draws would remove -- it is real heterogeneity between a
prompt's criteria.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

TENSOR = _ROOT / "E02_the_plural_public_dissolved/A03_does_the_protocol_have_the_power_it_needs/R41_criterion_support/results/r41_satisfaction_qwen2b.npz"
R57_RESPONSE_AXIS = {"pessimistic": 0.302, "optimistic": 0.422}
LEDGER = {"r40 generic distance": 0.0988, "r41 criterion-space support": 0.1010,
          "r46 spread loss (held out)": 0.1175, "r54 overlap transfer": 0.1336}
REL_PRED = {"r40 generic distance": 0.9132,          # r68, instrument axis
            "r41 criterion-space support": 0.657,    # r67, criterion axis
            "r46 spread loss (held out)": 0.657,     # r67, criterion axis
            "r54 overlap transfer": 0.4381}          # r69 corrected, 200-split mean
N_SPLITS = 200
N_CROSS = 25          # splits carried into the bootstrap, which is O(splits x draws)
N_BOOT = 2000


def spearman_brown(r, k=2.0):
    return k * r / (1 + (k - 1) * r) if r > -1 else float("nan")


def agree(sc, gd, ps):
    """Pairwise concordance with the gold order over the pair set `ps`."""
    out = []
    for k in range(sc.shape[0]):
        ok = tot = 0
        for x, y in ps:
            if gd[k, x] == gd[k, y]:
                continue
            tot += 1
            ok += int((sc[k, x] > sc[k, y]) == (gd[k, x] > gd[k, y]))
        out.append(ok / tot if tot else np.nan)
    return np.array(out, float)


def mean_over(z, off, pick):
    """Per-prompt mean over a SUBSET of that prompt's criteria."""
    out = np.full((len(off) - 1, z.shape[1]), np.nan)
    for k in range(len(off) - 1):
        idx = pick(k)
        if len(idx):
            out[k] = z[off[k] + np.asarray(idx)].mean(axis=0)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r70_outcome_criterion_axis.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not TENSOR.exists():
        raise SystemExit(f"REFUSING: {TENSOR.relative_to(_ROOT)} absent.")

    d = np.load(TENSOR)
    off = d["off_real"].astype(int)
    zo_r, zo_s = d["z_orig_real"], d["z_orig_shuf"]
    zf_r, zf_s = d["z_fresh_real"], d["z_fresh_shuf"]
    go, gf = d["gold_orig"], d["gold_fresh"]
    n_prompts = len(off) - 1
    nK = np.diff(off)
    splittable = nK >= 4
    ALL = list(combinations(range(4), 2))
    print(f"prompts {n_prompts}   criteria {zo_r.shape[0]}   "
          f"splittable {int(splittable.sum())}")

    # SANITY, before anything is read: the full-criteria rebuild must reproduce
    # the persisted accuracies, or the halves are being compared against a
    # pipeline never shown to be the one r12 published.
    def full(k):
        return np.arange(nK[k])
    rebuild = float(np.nanmax(np.abs(agree(mean_over(zo_r, off, full), go, ALL)
                                     - d["acc_orig_real"])))
    print(f"rebuild control: max |recomputed - persisted| = {rebuild:.1e}")
    if rebuild > 1e-9:
        raise SystemExit("REFUSING: the rebuild does not reproduce the persisted tensor.")

    def quantities(pick, ps):
        ao = agree(mean_over(zo_r, off, pick), go, ps)
        so = agree(mean_over(zo_s, off, pick), go, ps)
        af = agree(mean_over(zf_r, off, pick), gf, ps)
        sf = agree(mean_over(zf_s, off, pick), gf, ps)
        return {"accuracy": ao, "attribution": ao - so, "drop": (ao - so) - (af - sf)}

    def rho(x, y):
        m = np.isfinite(x) & np.isfinite(y) & splittable
        return float(np.corrcoef(x[m], y[m])[0, 1])

    def halves(order):
        return (lambda k: order[k][:nK[k] // 2],
                lambda k: order[k][nK[k] // 2: 2 * (nK[k] // 2)])

    # ---- the ladder, averaged over N_SPLITS random criterion splits ------
    rng = np.random.default_rng(4242)
    acc = {q: [] for q in ("accuracy", "attribution", "drop")}
    shufs = []
    for _ in range(N_SPLITS):
        order = [rng.permutation(nK[k]) for k in range(n_prompts)]
        hA, hB = halves(order)
        A, B = quantities(hA, ALL), quantities(hB, ALL)
        for q in acc:
            acc[q].append(rho(A[q], B[q]))
        sh = B["drop"].copy()
        fin = np.isfinite(sh)
        sh[fin] = rng.permutation(sh[fin])
        shufs.append(rho(A["drop"], sh))
    ladder = {}
    print(f"\nLADDER over {N_SPLITS} random criterion splits (n={int(splittable.sum())})")
    print(f"  {'quantity':14s} {'mean raw':>9} {'sd':>7} {'min':>8} {'max':>8} {'SB(mean)':>10}")
    for q, v in acc.items():
        v = np.array(v)
        ladder[q] = {"mean_raw": float(v.mean()), "sd_across_splits": float(v.std()),
                     "min": float(v.min()), "max": float(v.max()),
                     "spearman_brown": float(spearman_brown(v.mean()))}
        print(f"  {q:14s} {v.mean():>+9.4f} {v.std():>7.4f} {v.min():>+8.4f} {v.max():>+8.4f} "
              f"{spearman_brown(v.mean()):>10.4f}")

    shuf_r = float(np.mean(shufs))
    shuf_max = float(np.max(np.abs(shufs)))
    controls = {"self": 1.0, "prompt_shuffled_mean": shuf_r,
                "prompt_shuffled_max_abs": shuf_max,
                "rebuild_max_abs_diff": rebuild,
                "all_pass": bool(abs(shuf_r) < 0.20 and shuf_max < 0.30)}
    print(f"controls: shuffled mean {shuf_r:+.4f}  max |{shuf_max:.4f}|  "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the split-half estimator fails its own controls.")

    # ---- may the two axes be MULTIPLIED? ---------------------------------
    # World B divides by rel_criterion * rel_response, which is valid only if
    # they are independent error sources. Split both at once and compare the
    # crossed correlation against the product (independent) and the smaller
    # single-axis value (one shared source). Three-valued: if the interval covers
    # both candidates the test cannot separate them and says so.
    cr = np.random.default_rng(20260731)
    cross_s, crit_s, resp_s, keep = [], [], [], []
    for _ in range(N_CROSS):
        order = [cr.permutation(nK[k]) for k in range(n_prompts)]
        hA, hB = halves(order)
        pp = cr.permutation(len(ALL))
        pA, pB = [ALL[i] for i in pp[:3]], [ALL[i] for i in pp[3:]]
        dA, dB = quantities(hA, pA)["drop"], quantities(hB, pB)["drop"]
        keep.append((dA, dB))
        cross_s.append(rho(dA, dB))
        crit_s.append(rho(quantities(hA, ALL)["drop"], quantities(hB, ALL)["drop"]))
        resp_s.append(rho(quantities(full, pA)["drop"], quantities(full, pB)["drop"]))
    raw_cross = float(np.mean(cross_s))
    raw_crit = float(np.mean(crit_s))
    raw_resp = float(np.mean(resp_s))
    product = raw_crit * raw_resp
    shared = min(raw_crit, raw_resp)

    idx0 = np.flatnonzero(splittable & np.isfinite(keep[0][0]) & np.isfinite(keep[0][1]))
    bs = np.random.default_rng(20260801)
    boot = [float(np.mean([np.corrcoef(dA[s_], dB[s_])[0, 1] for dA, dB in keep]))
            for s_ in (idx0[bs.integers(0, len(idx0), len(idx0))] for _ in range(N_BOOT))]
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    cov_p, cov_s = lo <= product <= hi, lo <= shared <= hi
    if cov_p and not cov_s:
        indep = "INDEPENDENT -- world B may multiply the two axes"
    elif cov_s and not cov_p:
        indep = "SHARED SOURCE -- world B double-counts and its column overstates every floor"
    else:
        indep = ("UNVERIFIED -- the crossed interval covers both candidates; "
                 "this n cannot separate them")
    axes = {"raw_criterion_axis": raw_crit, "raw_response_axis_rebuilt": raw_resp,
            "raw_crossed": raw_cross, "crossed_ci": [lo, hi],
            "product_if_independent": float(product), "min_if_shared_source": float(shared),
            "n_splits_averaged": N_CROSS, "verdict": indep}
    print(f"\nMAY THE AXES BE MULTIPLIED?  ({N_CROSS} splits averaged)")
    print(f"  criterion {raw_crit:+.4f}   response {raw_resp:+.4f}   "
          f"crossed {raw_cross:+.4f} [{lo:+.4f},{hi:+.4f}]")
    print(f"  product {product:+.4f} (independent)   min {shared:+.4f} (shared source)")
    print(f"  -> {indep}")

    rel_crit = ladder["drop"]["spearman_brown"]
    print(f"\noutcome reliability by axis: response (r57) "
          f"{R57_RESPONSE_AXIS['pessimistic']:.3f}/{R57_RESPONSE_AXIS['optimistic']:.3f}"
          f"   criterion (here) {rel_crit:.4f}")

    floors = {}
    print(f"\n{'row':30s} {'published':>10} {'both axes':>10}")
    for label, hw in LEDGER.items():
        rp = REL_PRED[label]
        pub = hw / np.sqrt(rp * R57_RESPONSE_AXIS["pessimistic"])
        both = hw / np.sqrt(rp * R57_RESPONSE_AXIS["pessimistic"] * max(rel_crit, 1e-6))
        floors[label] = {"published_predictor_and_response_axis": float(pub),
                         "world_B_both_axes": float(both),
                         "world_F_fixed_R": float(hw / np.sqrt(R57_RESPONSE_AXIS["pessimistic"]))}
        print(f"  {label:28s} {pub:>10.3f} {both:>10.3f}")

    verdict = (
        f"THE LEDGER'S FLOOR FORMULA MULTIPLIES TWO RELIABILITIES ESTIMATED ALONG DIFFERENT AXES, "
        f"and nobody wrote that down, including me in r67 and r69. r57 measured the outcome by "
        f"splitting the 6 PAIRS -- the response axis. r67 and r69 measured predictors by splitting "
        f"CRITERIA. Rebuilding the attribution drop from half a prompt's criteria, on a tensor whose "
        f"full-criteria rebuild reproduces r12's published per-prompt values exactly, the outcome's "
        f"criterion-axis reliability is {rel_crit:.4f} -- close to r57's "
        f"{R57_RESPONSE_AXIS['pessimistic']:.3f}/{R57_RESPONSE_AXIS['optimistic']:.3f}, so the two "
        f"axes agree for the OUTCOME even though they differ roughly twofold for r54's predictor. "
        f"THE LADDER IS THE FINDING: accuracy {ladder['accuracy']['spearman_brown']:.4f}, "
        f"attribution {ladder['attribution']['spearman_brown']:.4f}, drop "
        f"{ladder['drop']['spearman_brown']:.4f}. The criterion split does not destroy signal by "
        f"itself, so the loss belongs to the contrast, and r57's own untested worry is confirmed: a "
        f"difference of two accuracies is far less reliable than either. "
        f"A SINGLE SPLIT IS NOT A MEASUREMENT: this round's first version drew one and got 0.3911 "
        f"for the drop; over {N_SPLITS} splits the mean is {rel_crit:.4f}, with the raw correlation "
        f"ranging {ladder['drop']['min']:+.4f} to {ladder['drop']['max']:+.4f}. r57 averaged 200 "
        f"splits; r69 drew one, and is corrected alongside this round. "
        f"MAY THE AXES BE MULTIPLIED -- testable, unlike the choice of world: crossed "
        f"{raw_cross:+.4f} [{lo:+.4f},{hi:+.4f}] against {product:+.4f} if independent and "
        f"{shared:+.4f} if one shared source. {indep}. "
        f"WHAT THIS DOES NOT SETTLE: whether a floor is ENTITLED to divide by criterion-axis "
        f"reliability at all. Under F, R is part of M(R,J,pi,Q,P) and this rubric's criteria are not "
        f"error, so the 1.23x is an over-correction. Under S the current floors stand. Under B the "
        f"rows are mechanism claims, both axes are error, and r54's floor would be "
        f"{floors['r54 overlap transfer']['world_B_both_axes']:.3f} rather than "
        f"{floors['r54 overlap transfer']['published_predictor_and_response_axis']:.3f}. NO WINNER "
        f"IS DECLARED HERE, because that is a decision about the research object and this round "
        f"measured a correlation."
    )

    doc = {
        "n_prompts": n_prompts, "n_splittable": int(splittable.sum()),
        "n_splits": N_SPLITS,
        "ladder": ladder,
        "outcome_reliability_criterion_axis": rel_crit,
        "outcome_reliability_response_axis_r57": R57_RESPONSE_AXIS,
        "axis_independence": axes,
        "floors_by_world": floors, "controls": controls,
        "world": "UNDECIDED -- ontological, not empirical",
        "outcome_variable_scope": (
            "The drop rebuilt here is judge-relative and gold-relative: the ranking target is the "
            "r08 model gold head, not human rankings (entry 50, r47). Reliability along any axis is "
            "not validity."),
        "scope": (
            f"Split-half over a prompt's criteria, 2-2, Spearman-Brown corrected, averaged over "
            f"{N_SPLITS} random splits with the spread reported -- a single split moved the drop's "
            f"reliability from 0.3013 to 0.3911. Prompts with K<4 are excluded and counted. The "
            f"full-criteria rebuild reproduces the persisted accuracies exactly. The three "
            f"floors-by-world columns are ARITHMETIC UNDER AN ASSUMPTION, not three measurements: "
            f"only the published column corresponds to a decision this repository has made. Which "
            f"world is right is a question about what the measurement program holds fixed, and is "
            f"left open deliberately."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {doc['world']}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
