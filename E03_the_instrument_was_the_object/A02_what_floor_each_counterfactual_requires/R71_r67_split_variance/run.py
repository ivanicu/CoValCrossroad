"""r71 -- r67's 0.657 was also one draw, and it is the one still load-bearing.

CLAIM CARD
----------
Claim      the predictors behind the ledger's correlational rows have a
           split-half reliability of 0.657, which multiplies r41's and r46's
           detection floors by 1.23x.
Estimand   the same quantity r67 estimated -- split-half reliability of spread
           loss and of criterion-space geometry, Spearman-Brown corrected --
           AVERAGED OVER MANY RANDOM SPLITS, with the across-split spread.
Target
observed?  YES. r67's own inputs are persisted
           (`r41_satisfaction_qwen2b.npz`) and its estimator is twelve lines.
           Nothing new is measured here; the same estimator is run 200 times
           instead of once.
Alternative
worlds     A STABLE  the 200-split mean lands within ~0.02 of 0.657. The single
                     draw was representative, the 1.23x stands, and the defect
                     found in r69/r70 does not generalise to r67.
           B MOVED   it lands materially away. Then all THREE reliability rounds
                     were single draws, r41's and r46's floors move, and the
                     README's 1.23x is wrong on the two rows where 0.657 is the
                     only number available.
Intervention
           none. Re-running a persisted estimator.
Null       (i) a half against ITSELF must give 1.0;
           (ii) a half against a prompt-shuffled other half must give ~0,
           checked on every draw and reported as a max, not a mean -- a mean
           over 200 draws hides a single bad one.

WHY THIS EXISTS
---------------
Entry 120 ended with a rule: *"A split-half reported from one split is a point
estimate of a quantity that varies by 3.5x across splits. Average it, report the
spread, or do not report it."* r69 and r70 were corrected under it the moment it
was written. **r67 was not, and r67 is the one the README still uses**: 0.657 is
the only predictor reliability available for r41 and r46, and the 1.23x
multiplier in the ledger paragraph is derived from it.

Retraction obliges re-run. This is that re-run.

WHAT IS NOT RE-DERIVED
----------------------
r67's choice of the two predictors, its K<4 exclusion, and its use of a hull
PROXY (the spread of per-criterion means, since a real hull is not computable on
a 2-criterion half) are all r67's and are kept verbatim. If they were wrong they
are still wrong; this round changes exactly one thing, the number of draws.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

TENSOR = _ROOT / "E02_the_plural_public_dissolved/A03_does_the_protocol_have_the_power_it_needs/R41_criterion_support/results/r41_satisfaction_qwen2b.npz"
R67_PUBLISHED = 0.657
REL_OUTCOME = {"pessimistic": 0.302, "optimistic": 0.422}
HALF = {"r41 criterion-space support": 0.1010, "r46 spread loss (held out)": 0.1175}
N_SPLITS = 200


def spearman_brown(r, k=2.0):
    return k * r / (1 + (k - 1) * r) if r > -1 else float("nan")


def halves(Z, off, rng):
    """r67's split, verbatim: each prompt's criteria 2-2, K<4 skipped."""
    A, B, skipped = [], [], 0
    for k in range(len(off) - 1):
        blk = Z[off[k]:off[k + 1]]
        if blk.shape[0] < 4:
            skipped += 1
            A.append(None)
            B.append(None)
            continue
        idx = rng.permutation(blk.shape[0])
        h = blk.shape[0] // 2
        A.append(blk[idx[:h]])
        B.append(blk[idx[h:2 * h]])
    return A, B, skipped


def spread(blocks):
    return np.array([np.mean(b.std(axis=1)) if b is not None else np.nan for b in blocks])


def hull_proxy(blocks):
    return np.array([b.mean(axis=0).std() if b is not None else np.nan for b in blocks])


def corr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 8 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan")
    return float(np.corrcoef(a[ok], b[ok])[0, 1])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r71_r67_split_variance.json")
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
    Z, Zf, off = d["z_orig_real"], d["z_fresh_real"], d["off_real"].astype(int)

    rng = np.random.default_rng(20260802)
    per = {"spread_loss": [], "criterion_space_geometry": []}
    shuf_max, skipped = 0.0, None
    for _ in range(N_SPLITS):
        A, B, skipped = halves(Z, off, rng)
        Af, Bf, _ = halves(Zf, off, rng)
        preds = {"spread_loss": (spread(A) - spread(Af), spread(B) - spread(Bf)),
                 "criterion_space_geometry": (hull_proxy(A) - hull_proxy(Af),
                                              hull_proxy(B) - hull_proxy(Bf))}
        for name, (x, y) in preds.items():
            per[name].append(corr(x, y))
        # the shuffled null, EVERY draw. Reported as a max: a mean over 200
        # draws would hide one bad draw, which is the failure this round exists
        # to correct, committed a second time in the control itself.
        sA = spread(A)
        sh = sA.copy()
        fin = np.isfinite(sh)
        sh[fin] = rng.permutation(sh[fin])
        shuf_max = max(shuf_max, abs(corr(sA, sh)))

    self_r = corr(spread(A), spread(A))
    controls = {"self": self_r, "prompt_shuffled_max_over_draws": shuf_max,
                "all_pass": bool(abs(self_r - 1) < 1e-9 and shuf_max < 0.30)}
    print(f"prompts skipped for K<4: {skipped} of {len(off)-1}")
    print(f"controls: self={self_r:.4f}  shuffled max over {N_SPLITS} draws {shuf_max:.4f}  "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the split-half estimator fails its own controls.")

    out, sb_means = {}, []
    print(f"\n{'predictor':26s} {'mean raw':>9} {'sd':>7} {'min':>8} {'max':>8} {'SB(mean)':>10}")
    for name, v in per.items():
        v = np.array([x for x in v if np.isfinite(x)])
        sb = spearman_brown(float(v.mean()))
        sb_means.append(sb)
        out[name] = {"mean_raw": float(v.mean()), "sd_across_splits": float(v.std()),
                     "min": float(v.min()), "max": float(v.max()),
                     "spearman_brown": float(sb), "n_draws": int(v.size)}
        print(f"  {name:24s} {v.mean():>+9.4f} {v.std():>7.4f} {v.min():>+8.4f} "
              f"{v.max():>+8.4f} {sb:>10.4f}")

    rel = float(np.mean(sb_means))
    delta = rel - R67_PUBLISHED
    world = "A STABLE" if abs(delta) <= 0.02 else "B MOVED"
    ratio_new, ratio_old = 1 / np.sqrt(rel), 1 / np.sqrt(R67_PUBLISHED)
    print(f"\nmean predictor reliability: {rel:.4f}   r67 published {R67_PUBLISHED}   "
          f"delta {delta:+.4f}")
    print(f"floor multiplier: {ratio_new:.3f}x   (published {ratio_old:.3f}x)")

    floors = {}
    print(f"\n{'row':30s} {'published':>10} {'re-averaged':>12}")
    for label, hw in HALF.items():
        floors[label] = {}
        for tag, ro in REL_OUTCOME.items():
            floors[label][tag] = {
                "published": float(hw / np.sqrt(R67_PUBLISHED * ro)),
                "reaveraged": float(hw / np.sqrt(rel * ro))}
        f = floors[label]["pessimistic"]
        print(f"  {label:28s} {f['published']:>10.3f} {f['reaveraged']:>12.3f}")

    verdict = (
        f"{world}. Entry 120 established that a split-half from ONE random split is a point "
        f"estimate of a quantity that varies several-fold across splits, and corrected r69 and r70 "
        f"under it the moment it was written. r67 had the same defect and was NOT corrected, which "
        f"matters more than the other two because 0.657 is the only predictor reliability available "
        f"for r41 and r46 and is where the ledger's 1.23x multiplier comes from. Re-running r67's own "
        f"estimator verbatim -- same predictors, same K<4 exclusion, same hull proxy -- {N_SPLITS} "
        f"times instead of once: "
        f"{', '.join(f'{k} {v['spearman_brown']:.4f} (sd {v['sd_across_splits']:.4f}, range '
                     f'{v['min']:+.4f} to {v['max']:+.4f})' for k, v in out.items())}, "
        f"mean {rel:.4f} against the published {R67_PUBLISHED}, a shift of {delta:+.4f}. The floor "
        f"multiplier is {ratio_new:.3f}x rather than {ratio_old:.3f}x. At the pessimistic outcome "
        f"reliability r41's floor moves "
        f"{floors['r41 criterion-space support']['pessimistic']['published']:.3f} -> "
        f"{floors['r41 criterion-space support']['pessimistic']['reaveraged']:.3f} and r46's "
        f"{floors['r46 spread loss (held out)']['pessimistic']['published']:.3f} -> "
        f"{floors['r46 spread loss (held out)']['pessimistic']['reaveraged']:.3f}. "
        f"ALL THREE RELIABILITY ROUNDS WERE SINGLE DRAWS -- r67, r69 and r70 -- and all three are now "
        f"averaged. The shuffled null was re-run on every draw and is reported as a MAXIMUM "
        f"({shuf_max:.4f}), not a mean, because averaging a control over 200 draws would hide one bad "
        f"draw, which is the very failure this round exists to correct."
    )

    doc = {
        "predictors": out, "n_splits": N_SPLITS,
        "mean_predictor_reliability": rel,
        "r67_published": R67_PUBLISHED, "delta_vs_published": delta,
        "floor_multiplier": float(ratio_new),
        "floor_multiplier_published": float(ratio_old),
        "prompts_skipped_K_lt_4": skipped,
        "floors": floors, "controls": controls, "world": world,
        "outcome_variable_scope": (
            "Predictor-side only. The outcome these predictors are correlated against is the "
            "attribution drop scored by the r08 model gold head, not by humans (entry 50, r47)."),
        "scope": (
            f"r67's estimator verbatim, run {N_SPLITS} times: same two predictors, same K<4 "
            f"exclusion, same hull PROXY (a real hull is not computable on a 2-criterion half). "
            f"Only the number of draws changes. The across-split spread is reported for each "
            f"predictor and the shuffled control as a maximum over draws."),
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
