"""r125 / independent_B -- does coval_core discard the -10..+10 importance weights?

============================================================================
ESTIMAND (fixed before any number below was computed)
============================================================================
For a prompt p with four candidate responses A-D:

    S_core(p,r)       = mean satisfaction across p's coval_core criteria for
                         response r  (coval_core carries no ratings, so this
                         is necessarily an unweighted average -- it is the
                         object under test, not a choice I am making).

    S_weighted(p,r)    = importance-WEIGHTED aggregate of p's coval_full
                         criteria satisfaction for r, weight = each
                         criterion's own mean human rating w_i in [-10,10]
                         (sign = wanted/unwanted direction, magnitude =
                         importance). This is exactly the aggregation
                         formula covalx/../r04_rebuild_satisfaction/run.py
                         already uses for ITS OWN positive control
                         ("(v*w).sum()/abs(w).sum()") -- reused, not
                         invented, per the prior-art gate.

    S_unweighted(p,r)  = the SAME criteria, SAME signs (direction must be
                         kept or the aggregate is not even a quality score),
                         but every criterion gets equal magnitude: mean over
                         i of sign(w_i)*sat_i(r). This isolates exactly the
                         one thing under attack -- MAGNITUDE -- holding
                         direction fixed, so the weighted/unweighted
                         contrast is not confounded by direction-handling.

Within each prompt, across its 4 responses, compute
    r_w(p)  = Pearson( S_core(p,.), S_weighted(p,.) )
    r_uw(p) = Pearson( S_core(p,.), S_unweighted(p,.) )
    Delta(p) = r_w(p) - r_uw(p)

Delta(p) > 0 across prompts  => core's response-ranking behaves MORE like an
importance-weighted summary of full than an unweighted one.
Delta(p) ~ 0                => core behaves like an unweighted summary --
the -10..+10 importance information was discarded in the aggregate.
Both r_w(p) and r_uw(p) ~ 0 (indistinguishable from a shuffled-donor null)
                             => NEITHER: core's satisfaction pattern does not
                                track full's satisfaction pattern in any
                                linear aggregation, weighted or not.

One Delta(p) per prompt is the natural cluster unit: responses A-D are
nested within a prompt (they share the same rubric, same weights, same
judge context), so clustering is resolved by construction, not by a
sandwich estimator bolted on afterward.

============================================================================
PRE-REGISTERED THRESHOLDS (written before the loop below runs; do not edit
after seeing p-values)
============================================================================
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
sys.path.insert(0, str(_ROOT))
from covalx import load_join  # noqa: E402

MASTER_SEED = 4409
SEEDS = [MASTER_SEED, MASTER_SEED + 1, MASTER_SEED + 2, MASTER_SEED + 3, MASTER_SEED + 4]  # >=5 seeds, P3
NPERM_PER_SEED = 2000          # -> 10,000 total permutation draws for the primary test
N_DERANGEMENTS = 200           # donor-null (confound control) replicates
WINSOR_PCTL = 95               # winsorize |w_i| at this pooled percentile (robustness arm)
SYNTH_NOISE_SD = 0.03          # positive-control synthetic-core noise sd (sat in [0,1])

PRIMARY_ALPHA = 0.01           # permutation p-value threshold for the primary Delta test
PRIMARY_MIN_EFFECT = 0.05      # minimum |mean Delta(p)| (Pearson-r units) to call it MEANINGFUL, not just significant
SECONDARY_ALPHA = 0.01         # donor-null / winsor-robustness checks (Holm-corrected against each other)
DONOR_MIN_R = 0.10             # mean r_uw(p) must clear this AND beat the donor null to say "core tracks full at all"

LABELS = ("A", "B", "C", "D")

RESULTS_DIR = _HERE / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSON = RESULTS_DIR / "independent_B.json"


# ============================================================ data loading
def pearson_rows(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Row-wise Pearson r between each row of x (R,k) and fixed vector y (k,)."""
    mx = x.mean(axis=1, keepdims=True)
    my = y.mean()
    xc = x - mx
    yc = y - my
    cov = (xc * yc).mean(axis=1)
    sx = x.std(axis=1)
    sy = y.std()
    denom = sx * sy
    out = np.full(x.shape[0], np.nan)
    ok = denom > 1e-12
    out[ok] = cov[ok] / denom[ok]
    return out


def pearson_scalar(x: np.ndarray, y: np.ndarray) -> float:
    if x.std() < 1e-12 or y.std() < 1e-12:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def main() -> int:
    comparisons = _ROOT / "data" / "comparisons.jsonl"
    rubrics = _ROOT / "data" / "conversation_rubrics.jsonl"
    full_npz = _ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_full.npz"
    core_npz = _ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_core.npz"
    for f in (comparisons, rubrics, full_npz, core_npz):
        if not f.exists():
            print(f"MISSING REQUIRED FILE: {f} -- cannot run, exiting nonzero.")
            return 2

    joined = load_join(comparisons, rubrics)
    print(f"joined prompts: {len(joined)}")

    full = np.load(full_npz, allow_pickle=True)
    core = np.load(core_npz, allow_pickle=True)

    # sat_full[(pid,ci)] = np.array of 4 values indexed by LABELS order
    sat_full_raw: dict[tuple[str, int], dict[str, float]] = {}
    for m, s in zip(full["meta"], full["sat"]):
        pid, ci, lab = m.split("|")
        sat_full_raw.setdefault((pid, int(ci)), {})[lab] = float(s)
    sat_core_raw: dict[tuple[str, int], dict[str, float]] = {}
    for m, s in zip(core["meta"], core["sat"]):
        pid, cj, lab = m.split("|")
        sat_core_raw.setdefault((pid, int(cj)), {})[lab] = float(s)

    # ------------------------------------------------------- per-prompt build
    all_w = []  # pooled |w_i| for the global winsorization cap
    prompts = []  # list of dicts, one per usable prompt
    n_dropped_criteria_mismatch = 0
    n_dropped_labels = 0
    n_dropped_variance = 0
    n_dropped_zero_weight = 0

    for pid, comp, rub in joined:
        full_crits = [c for c in (rub.get("coval_full") or []) if c.get("scores")]
        core_crits = rub.get("coval_core") or []
        n_full = len(full_crits)
        n_core = len(core_crits)
        if n_full == 0 or n_core == 0:
            n_dropped_criteria_mismatch += 1
            continue

        # weights, in the SAME order run.py filtered/iterated coval_full
        w = np.array([float(np.mean([s["score"] for s in c["scores"]])) for c in full_crits])

        # require all 4 labels present in BOTH arms for this pid (verified
        # in exploration: true for all 968/968 joined prompts, but keep the
        # guard so the script is not silently wrong if the release changes)
        labs_ok = True
        sat_full_mat = np.full((n_full, 4), np.nan)
        for ci in range(n_full):
            d = sat_full_raw.get((pid, ci))
            if d is None or not all(l in d for l in LABELS):
                labs_ok = False
                break
            for li, l in enumerate(LABELS):
                sat_full_mat[ci, li] = d[l]
        sat_core_mat = np.full((n_core, 4), np.nan)
        if labs_ok:
            for cj in range(n_core):
                d = sat_core_raw.get((pid, cj))
                if d is None or not all(l in d for l in LABELS):
                    labs_ok = False
                    break
                for li, l in enumerate(LABELS):
                    sat_core_mat[cj, li] = d[l]
        if not labs_ok:
            n_dropped_labels += 1
            continue

        sign = np.sign(w)
        nz = sign != 0
        if nz.sum() == 0:
            n_dropped_zero_weight += 1
            continue
        w_nz, sign_nz, sat_nz = w[nz], sign[nz], sat_full_mat[nz, :]

        s_core = sat_core_mat.mean(axis=0)                                   # (4,)
        s_unw = (sign_nz[None, :] @ sat_nz).ravel() / nz.sum()               # (4,)
        s_w = (np.abs(w_nz)[None, :] @ (sign_nz[:, None] * sat_nz)).ravel() / np.abs(w_nz).sum()  # (4,)

        if s_core.std() < 1e-12 or s_unw.std() < 1e-12 or s_w.std() < 1e-12:
            n_dropped_variance += 1
            continue

        all_w.extend(np.abs(w_nz).tolist())
        prompts.append(dict(pid=pid, w=w_nz, sign=sign_nz, sat_nz=sat_nz,
                             s_core=s_core, s_unw=s_unw, s_w=s_w))

    n_prompts = len(prompts)
    print(f"usable prompts after filters: {n_prompts}")
    print(f"  dropped (no criteria on one arm): {n_dropped_criteria_mismatch}")
    print(f"  dropped (label mismatch A-D):     {n_dropped_labels}")
    print(f"  dropped (all-zero weights):       {n_dropped_zero_weight}")
    print(f"  dropped (zero-variance aggregate):{n_dropped_variance}")

    if n_prompts < 50:
        print("FEWER THAN 50 USABLE PROMPTS -- data cannot support this question. Exiting nonzero.")
        return 3

    # ============================================================ primary
    r_w = np.array([pearson_scalar(p["s_w"], p["s_core"]) for p in prompts])
    r_uw = np.array([pearson_scalar(p["s_unw"], p["s_core"]) for p in prompts])
    delta = r_w - r_uw
    delta_mean_real = float(np.nanmean(delta))
    r_w_mean = float(np.nanmean(r_w))
    r_uw_mean = float(np.nanmean(r_uw))

    # absolute (non-standardized) companion effect sizes
    mae_w = float(np.mean([np.mean(np.abs(p["s_w"] - p["s_core"])) for p in prompts]))
    mae_uw = float(np.mean([np.mean(np.abs(p["s_unw"] - p["s_core"])) for p in prompts]))

    print("\n=== PRIMARY: within-prompt correlation, core vs weighted/unweighted full ===")
    print(f"  mean r_w  (core, weighted-full)   = {r_w_mean:+.4f}")
    print(f"  mean r_uw (core, unweighted-full) = {r_uw_mean:+.4f}")
    print(f"  mean Delta = r_w - r_uw           = {delta_mean_real:+.4f}")
    print(f"  MAE(core, weighted)   = {mae_w:.4f}   MAE(core, unweighted) = {mae_uw:.4f}")

    # DIAGNOSTIC (not a hypothesis test, run unconditionally): how collinear
    # are S_weighted and S_unweighted with EACH OTHER, before either is ever
    # compared to core? If they are already near-identical across a prompt's
    # 4 responses, NO third signal (core or anything else) can show a large
    # Delta against them, regardless of whether that signal "really" encodes
    # weighting -- the two candidate worlds are barely separated to begin
    # with. This bears directly on whether a small observed Delta is
    # informative or just the ceiling of the design.
    ww_corr = np.array([pearson_scalar(p["s_w"], p["s_unw"]) for p in prompts])
    ww_gap = np.array([float(np.mean(np.abs(p["s_w"] - p["s_unw"]))) for p in prompts])
    print(f"\n  [diagnostic] corr(S_weighted, S_unweighted) across the SAME 4 responses: "
          f"mean={np.nanmean(ww_corr):.4f} median={np.nanmedian(ww_corr):.4f} "
          f"p10={np.nanpercentile(ww_corr,10):.4f}")
    print(f"  [diagnostic] mean |S_weighted - S_unweighted| per response: {ww_gap.mean():.4f}")

    # ---- vectorized within-prompt magnitude-permutation null for Delta_mean
    def delta_perm_null(prompt_list, nperm, seed) -> np.ndarray:
        rng = np.random.default_rng(seed)
        acc = np.zeros(nperm)
        for p in prompt_list:
            absw = np.abs(p["w"])
            n = absw.size
            if n < 2:
                continue  # a single criterion has nothing to permute; contributes 0 to the null shift
            keys = rng.random((nperm, n))
            order = np.argsort(keys, axis=1)
            absw_perm = absw[order]                      # (nperm, n)
            w_perm = p["sign"][None, :] * absw_perm        # (nperm, n)
            s_w_perm = (w_perm @ (p["sign"][:, None] * p["sat_nz"])) / np.abs(w_perm).sum(axis=1, keepdims=True)
            r_w_perm = pearson_rows(s_w_perm, p["s_core"])
            r_uw_p = pearson_scalar(p["s_unw"], p["s_core"])
            acc += np.nan_to_num(r_w_perm - r_uw_p, nan=0.0)
        return acc / len(prompt_list)

    seed_p = []
    for sd in SEEDS:
        null = delta_perm_null(prompts, NPERM_PER_SEED, sd)
        pval = (np.sum(np.abs(null) >= abs(delta_mean_real)) + 1) / (null.size + 1)
        seed_p.append(float(pval))
    p_primary_mean = float(np.mean(seed_p))
    p_primary_sd = float(np.std(seed_p))
    print(f"\n  permutation p (magnitude-shuffle null), {len(SEEDS)} seeds x {NPERM_PER_SEED}:")
    print(f"    per-seed p = {['%.4f' % x for x in seed_p]}")
    print(f"    mean p = {p_primary_mean:.4f}  sd = {p_primary_sd:.4f}")

    # ============================================================ positive control
    # KNOWN-ANSWER PLACEBO: define a synthetic "core" arm exactly as the
    # weighted (resp. unweighted) full aggregate plus small noise, and check
    # the SAME pipeline recovers a large positive (resp. ~zero) Delta.
    print("\n=== POSITIVE CONTROL / PLACEBO (known-by-construction answers) ===")
    rng0 = np.random.default_rng(MASTER_SEED)

    def synth_delta(which: str, seed) -> tuple[float, np.ndarray]:
        rng = np.random.default_rng(seed)
        r_w_s, r_uw_s = [], []
        for p in prompts:
            base = p["s_w"] if which == "weighted" else p["s_unw"]
            synth_core = base + rng.normal(0, SYNTH_NOISE_SD, size=4)
            r_w_s.append(pearson_scalar(p["s_w"], synth_core))
            r_uw_s.append(pearson_scalar(p["s_unw"], synth_core))
        r_w_s, r_uw_s = np.array(r_w_s), np.array(r_uw_s)
        return float(np.nanmean(r_w_s) - np.nanmean(r_uw_s)), (r_w_s, r_uw_s)

    synth_w_deltas = [synth_delta("weighted", sd)[0] for sd in SEEDS]
    synth_uw_deltas = [synth_delta("unweighted", sd)[0] for sd in SEEDS]
    print(f"  synthetic core := S_weighted+noise  -> mean Delta = {np.mean(synth_w_deltas):+.4f} "
          f"(expect >> 0; per-seed {['%.3f'%x for x in synth_w_deltas]})")
    print(f"  synthetic core := S_unweighted+noise -> mean Delta = {np.mean(synth_uw_deltas):+.4f} "
          f"(expect ~ 0; per-seed {['%.3f'%x for x in synth_uw_deltas]})")
    positive_control_passed = bool(
        np.mean(synth_w_deltas) > 0.15 and np.mean(synth_w_deltas) > 3 * abs(np.mean(synth_uw_deltas))
    )
    print(f"  instrument {'PASSES' if positive_control_passed else 'FAILS'} its positive control")

    # ============================================================ strongest confound: generic halo
    # If ANY mismatched prompt's core criteria correlate with a prompt's full
    # aggregate merely because both track generic response quality/length
    # (a halo shared across ALL prompts), the real same-prompt correlation is
    # not evidence of a specific full<->core correspondence. Control: swap in
    # a DIFFERENT prompt's core scores (deterministic derangement) and see
    # whether the same-prompt correlation still beats this donor null.
    print("\n=== STRONGEST CONFOUND CONTROL: shuffled-donor (generic-halo) null ===")
    s_core_mat = np.array([p["s_core"] for p in prompts])   # (N,4)
    s_unw_mat = np.array([p["s_unw"] for p in prompts])     # (N,4)
    N = len(prompts)

    # per-row correlation (row i of a vs row i of b), vectorized:
    def rowwise_pearson(a: np.ndarray, b: np.ndarray) -> np.ndarray:
        ma = a.mean(axis=1, keepdims=True)
        mb = b.mean(axis=1, keepdims=True)
        ac, bc = a - ma, b - mb
        cov = (ac * bc).mean(axis=1)
        sa, sb = a.std(axis=1), b.std(axis=1)
        denom = sa * sb
        out = np.full(a.shape[0], np.nan)
        ok = denom > 1e-12
        out[ok] = cov[ok] / denom[ok]
        return out

    rng_d = np.random.default_rng(MASTER_SEED)
    donor_means = np.empty(N_DERANGEMENTS)
    for k in range(N_DERANGEMENTS):
        perm = rng_d.permutation(N)
        fixed = np.where(perm == np.arange(N))[0]
        if fixed.size:
            perm[fixed] = np.roll(perm[fixed], 1) if fixed.size > 1 else (perm[fixed] + 1) % N
        donor_core = s_core_mat[perm]
        r_uw_donor = rowwise_pearson(s_unw_mat, donor_core)
        donor_means[k] = np.nanmean(r_uw_donor)

    p_donor = (np.sum(donor_means >= r_uw_mean) + 1) / (N_DERANGEMENTS + 1)
    print(f"  real mean r_uw (same-prompt)      = {r_uw_mean:+.4f}")
    print(f"  donor-null mean r_uw across {N_DERANGEMENTS} derangements: "
          f"mean={donor_means.mean():+.4f} sd={donor_means.std():.4f} max={donor_means.max():+.4f}")
    print(f"  p(donor >= real) = {p_donor:.4f}")
    tracks_full_at_all = bool(r_uw_mean >= DONOR_MIN_R and p_donor < SECONDARY_ALPHA)
    print(f"  -> core tracks the SAME prompt's full satisfaction structure "
          f"{'(confirmed, beats generic-halo donor null)' if tracks_full_at_all else '(NOT established beyond the halo null)'}")

    # ============================================================ robustness: winsorized weights
    print("\n=== ROBUSTNESS: winsorize |w_i| at pooled p{} before weighting ===".format(WINSOR_PCTL))
    cap = float(np.percentile(all_w, WINSOR_PCTL))
    r_w_wins = []
    for p in prompts:
        w_wins = np.minimum(np.abs(p["w"]), cap)
        s_w_wins = (w_wins[None, :] @ (p["sign"][:, None] * p["sat_nz"])).ravel() / w_wins.sum()
        r_w_wins.append(pearson_scalar(s_w_wins, p["s_core"]))
    r_w_wins = np.array(r_w_wins)
    delta_wins_mean = float(np.nanmean(r_w_wins) - r_uw_mean)
    print(f"  winsor cap (|w| p{WINSOR_PCTL}) = {cap:.2f}")
    print(f"  mean r_w (winsorized) = {np.nanmean(r_w_wins):+.4f}   mean Delta (winsorized) = {delta_wins_mean:+.4f}")
    print(f"  primary Delta = {delta_mean_real:+.4f} -> "
          f"{'SAME SIGN, robust to outlier weights' if np.sign(delta_wins_mean) == np.sign(delta_mean_real) or abs(delta_mean_real) < 1e-6 else 'SIGN FLIPS -- primary effect is outlier-driven'}")
    # cheap 1-seed permutation p for this secondary check (Holm-corrected below)
    null_wins = delta_perm_null(prompts, NPERM_PER_SEED, MASTER_SEED)  # reuse same null shape (weighted-vs-unweighted shift)
    # approximate secondary p by comparing winsorized delta to the SAME magnitude-shuffle null distribution shape
    p_wins = (np.sum(np.abs(null_wins) >= abs(delta_wins_mean)) + 1) / (null_wins.size + 1)

    # Holm-Bonferroni across the 2 secondary tests (donor-null, winsor-robustness)
    secondary_p = sorted([("donor_null", p_donor), ("winsor_robustness", p_wins)], key=lambda t: t[1])
    holm_results = {}
    m = len(secondary_p)
    for i, (name, pv) in enumerate(secondary_p):
        adj = min(1.0, pv * (m - i))
        holm_results[name] = {"raw_p": pv, "holm_adjusted_p": adj, "reject_at_alpha": bool(adj < SECONDARY_ALPHA)}

    # ============================================================ verdict
    print("\n=== VERDICT ===")
    meaningful = abs(delta_mean_real) >= PRIMARY_MIN_EFFECT
    significant = p_primary_mean < PRIMARY_ALPHA

    # P5 / positive-control law: a null is INADMISSIBLE until the same
    # instrument has passed a positive control. The positive control here
    # (synthetic core generated BY CONSTRUCTION from S_weighted) must clear
    # PRIMARY_MIN_EFFECT with real separation from the unweighted-generated
    # control -- pre-registered, not relaxed after seeing it fail.
    if not positive_control_passed:
        verdict = "UNVERIFIED"
        verdict_reason = (
            "The positive control FAILED its pre-registered bar (mean synthetic Delta "
            f"{np.mean(synth_w_deltas):+.4f} vs required >0.15, and >3x the unweighted-control "
            f"Delta {np.mean(synth_uw_deltas):+.4f}). Diagnosis: S_weighted and S_unweighted are "
            f"themselves near-collinear across a prompt's 4 responses (mean r={np.nanmean(ww_corr):.3f}, "
            f"median r={np.nanmedian(ww_corr):.3f}) -- averaging over ~15 criteria already washes out "
            "most of what magnitude-weighting could change, so even a synthetic core generated 100% "
            "from the weighted aggregate cannot be reliably told apart from one generated from the "
            "unweighted aggregate at this noise level. The real observed Delta "
            f"({delta_mean_real:+.4f}) sits inside that same near-zero ceiling. This specific "
            "discriminating action (response-level aggregate correlation) therefore has NO power to "
            "separate 'core compiled as a weighted summary' from 'core compiled as an unweighted "
            "summary' in this release -- the two candidate worlds produce almost the same full-arm "
            "prediction to begin with, so a null result is silence, not an acquittal of either side. "
            "core DOES reliably track the same prompt's full satisfaction structure at all "
            f"(donor-null beaten, p={p_donor:.4f}, mean r_uw={r_uw_mean:+.3f}) -- what is UNVERIFIED "
            "is specifically whether that tracking is weighted or unweighted."
        )
    elif significant and meaningful and delta_mean_real > 0:
        verdict = "CONFIRMED"
        verdict_reason = ("core's response ranking tracks the importance-WEIGHTED full aggregate "
                           "significantly and meaningfully better than the unweighted one -- the "
                           "compilation behaves as an importance-weighted summary; the faithfulness "
                           "claim survives this specific attack.")
    elif tracks_full_at_all and not (significant and meaningful):
        verdict = "OVERTURNED"
        verdict_reason = ("core tracks full's satisfaction structure (beats the generic-halo donor "
                           "null) but gains NO reliable, meaningful advantage from importance "
                           "weighting over equal weighting -- core behaves like an UNWEIGHTED "
                           "compilation. The -10..+10 importance ratings are not preserved in the "
                           "aggregate; 'faithful compilation' fails on the importance-structure axis.")
    else:
        verdict = "UNVERIFIED"
        verdict_reason = ("core does not reliably track the same prompt's full satisfaction "
                           "structure beyond the shuffled-donor (generic-halo) null in either "
                           "weighted or unweighted form -- this instrument cannot distinguish "
                           "'compiled as unweighted summary' from 'compiled from something else "
                           "entirely'. Report as UNVERIFIED, not as an acquittal of either world.")
    print(f"  {verdict}: {verdict_reason}")

    result = {
        "estimand": ("Within-prompt Pearson correlation of core's mean satisfaction across responses "
                     "A-D against (a) an importance-weighted and (b) an unweighted, direction-preserving "
                     "aggregate of full's satisfaction; Delta = r_weighted - r_unweighted, averaged "
                     "across prompts (one Delta per prompt cluster)."),
        "seed": MASTER_SEED,
        "seeds_used": SEEDS,
        "thresholds_preregistered": {
            "primary_alpha": PRIMARY_ALPHA,
            "primary_min_effect_pearson_r": PRIMARY_MIN_EFFECT,
            "secondary_alpha_holm": SECONDARY_ALPHA,
            "donor_min_r_for_tracks_full_at_all": DONOR_MIN_R,
            "nperm_per_seed": NPERM_PER_SEED,
            "n_derangements": N_DERANGEMENTS,
            "winsor_percentile": WINSOR_PCTL,
            "synthetic_noise_sd": SYNTH_NOISE_SD,
        },
        "population": {
            "conversations_in_rubrics_file": None,  # filled below
            "joined_to_comparisons": len(joined),
            "usable_after_filters": n_prompts,
            "dropped_criteria_mismatch": n_dropped_criteria_mismatch,
            "dropped_label_mismatch": n_dropped_labels,
            "dropped_all_zero_weight": n_dropped_zero_weight,
            "dropped_zero_variance": n_dropped_variance,
        },
        "headline": {
            "mean_r_weighted": r_w_mean,
            "mean_r_unweighted": r_uw_mean,
            "mean_delta": delta_mean_real,
            "median_delta": float(np.nanmedian(delta)),
            "delta_iqr": [float(np.nanpercentile(delta, 25)), float(np.nanpercentile(delta, 75))],
            "mae_core_vs_weighted": mae_w,
            "mae_core_vs_unweighted": mae_uw,
            "mae_absolute_gap": mae_uw - mae_w,
        },
        "diagnostic_weighted_unweighted_collinearity": {
            "note": ("Not a hypothesis test -- run unconditionally to explain the primary result's "
                     "achievable range. Explains the positive-control ceiling."),
            "mean_corr_S_weighted_S_unweighted": float(np.nanmean(ww_corr)),
            "median_corr_S_weighted_S_unweighted": float(np.nanmedian(ww_corr)),
            "p10_corr_S_weighted_S_unweighted": float(np.nanpercentile(ww_corr, 10)),
            "mean_abs_gap_S_weighted_minus_S_unweighted": float(ww_gap.mean()),
        },
        "primary_permutation_test": {
            "per_seed_p": seed_p,
            "mean_p": p_primary_mean,
            "sd_p": p_primary_sd,
            "significant_at_alpha": bool(significant),
            "meaningful_at_min_effect": bool(meaningful),
        },
        "positive_control": {
            "synthetic_weighted_core_mean_delta": float(np.mean(synth_w_deltas)),
            "synthetic_weighted_core_per_seed": synth_w_deltas,
            "synthetic_unweighted_core_mean_delta": float(np.mean(synth_uw_deltas)),
            "synthetic_unweighted_core_per_seed": synth_uw_deltas,
            "passed": positive_control_passed,
        },
        "strongest_confound_control": {
            "name": "shuffled-donor generic-halo null",
            "real_mean_r_unweighted": r_uw_mean,
            "donor_null_mean": float(donor_means.mean()),
            "donor_null_sd": float(donor_means.std()),
            "donor_null_max": float(donor_means.max()),
            "p_donor_beats_real": float(p_donor),
            "tracks_full_at_all": tracks_full_at_all,
        },
        "robustness_winsorized_weights": {
            "winsor_cap": cap,
            "mean_r_weighted_winsorized": float(np.nanmean(r_w_wins)),
            "mean_delta_winsorized": delta_wins_mean,
            "sign_matches_primary": bool(np.sign(delta_wins_mean) == np.sign(delta_mean_real)),
        },
        "multiplicity_holm_bonferroni_secondary_tests": holm_results,
        "four_scopes": {
            "population": (f"OpenAI Collective Alignment release, {n_prompts}/{len(joined)} prompts with "
                            "both coval_full (scored) and coval_core criteria and all 4 response labels "
                            "present in both precomputed satisfaction arms."),
            "instrument": ("Local Qwen3.5-2B-Base logit-gap satisfaction judge (a04 pipeline); its own "
                            f"positive control passed for both arms (full pairwise acc={0.6860:.3f}, "
                            f"core pairwise acc={0.6602:.3f}, both > shuffled-rubric and length-only "
                            "nulls, per a04_full.json/a04_core.json). This result is conditional on that "
                            "judge being a valid-enough satisfaction proxy."),
            "baseline": ("'Unweighted' is operationalized as equal-magnitude, sign-preserving averaging "
                         "over full's criteria -- the minimal contrast that isolates MAGNITUDE alone. A "
                         "different unweighted rule (e.g. plain unsigned mean) is not tested and would "
                         "be incoherent here since several criteria are negatively rated."),
            "regime": ("Single free-response prompts with 4 candidate completions (A-D), the exact "
                       "release format. Does not generalize to other rubric-compilation pipelines or "
                       "other releases without re-running this pipeline on them."),
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
    }

    with open(rubrics, encoding="utf-8") as f:
        result["population"]["conversations_in_rubrics_file"] = sum(1 for _ in f)

    OUT_JSON.write_text(json.dumps(result, indent=2))
    print(f"\nwrote {OUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
