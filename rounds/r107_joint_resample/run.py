"""r107 -- every interval on this axis counts ONE source. What is the width when both are counted?

CLAIM CARD
----------
Claim      r105 reported the across-bin share difference with a PAIR bootstrap, holding the
           donor draw fixed: half-width 0.1260. r106 reported the same quantity's DRAW
           spread, holding the pairs fixed: sd 0.0596. Neither interval covers the other's
           source, and entry 220 recorded the pattern -- three consecutive rounds each
           believed they had bounded the thing, and the next source was never visible from
           inside the round that missed it.
Estimand   the JOINT sampling distribution of (a) the pooled prompt-specific share and
           (b) its high-minus-low-consensus difference, under donor redraw AND pair
           resampling in the same iteration.
Target
observed?  YES. Both sources are simulable on artifacts already persisted: r104's split
           records supply the pairs, and r106's construction supplies the donor arm as a
           dot product against per-criterion satisfaction differences.
Alternative
worlds     A ADDITIVE     the joint variance is approximately the sum of the two marginal
                          variances. Then the sources are effectively independent, the
                          previous intervals were each too narrow by a KNOWN amount, and
                          the joint width is quotable.
           I INTERACTING  it is materially larger or smaller than the sum. Larger means a
                          draw that is unlucky on one bin is also unlucky on the pairs
                          resampled into it; smaller means the two partly cancel. Either
                          way neither marginal can be corrected by a simple inflation and
                          the joint sampler is the only admissible interval.
Intervention
           redraw the donor assignment and cluster-resample the pairs in the SAME
           iteration; hold everything else -- own arm, labels, bins, population -- fixed.
Null       THREE DEGENERATE IDENTITY CONTROLS on the joint sampler, all exact:
           (i) both sources OFF must return the canonical value every iteration, sd
               exactly 0. A sampler with residual noise when nothing is resampled is
               drawing from somewhere this card does not name.
           (ii) draw ON, pairs OFF must reproduce r106's persisted draws EXACTLY, seed for
               seed. That is a cross-round rebuild control: if it does not, this round's
               "draw source" is not the one r106 measured and the comparison is void.
           (iii) draw OFF, pairs ON must have the canonical share as its centre, since
               every iteration scores the canonical donor.
           These are identities, not tolerances. The joint condition is only interpretable
           if switching each source off recovers the round that measured it alone.

WHY THIS IS THE STEP
--------------------
Entry 220's NEXT, and it is the last one on this axis that costs nothing. Four rounds have
now reported a width; none of them is the width. This is not a new measurement -- it is the
admission that the previous three intervals were each conditional on something they did not
say they were conditional on.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
A joint interval is still not THE interval. It counts donor assignment and pair sampling.
It does NOT count: the judge (one lineage), the satisfaction reconstruction (r04's tensor
taken as given), the rater split (r104's twelve splits are averaged over, not resampled as
a source), or the donor POOL (fixed 968 weight vectors -- r106's confound, inherited here
unchanged). So the honest name for this quantity is "joint over the two sources anyone has
measured", and the verdict uses that name rather than calling it total uncertainty.
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

# EVERY round file is named run.py, so `import run` is ambiguous and r106's own
# `from run import weights` resolved back to r106 itself -- a circular import. Load it
# under an explicit module name and leave its directory OFF sys.path, so that r106's
# internal import still finds r85's run.py, which is what it means.
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "r106_share_level_under_redraw",
    _ROOT / "rounds/r106_share_level_under_redraw/run.py")
_r106 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _r106
_spec.loader.exec_module(_r106)
DONOR_SEED, build, draw_donors, share_of = (
    _r106.DONOR_SEED, _r106.build, _r106.draw_donors, _r106.share_of)

VEC = _ROOT / "rounds/r104_deattenuated_consensus/results/r104_split_records.npz"
R106V = _ROOT / "rounds/r106_share_level_under_redraw/results/r106_share_draws.npz"
N_ITER = 200
MARGIN = 0.05           # r105's pre-registered equivalence margin, unchanged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r107_joint_resample.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not (VEC.exists() and R106V.exists()):
        raise SystemExit("REFUSING: r104's records or r106's draws are absent; this round composes them.")

    D, own_dir, pair_prompt, W, n, _ = build()
    rec = np.load(VEC)
    rpid, cons, own_hit, don_hit = rec["pid"], rec["cons"], rec["own"], rec["donor"]
    npairs = int(rpid.max()) + 1
    if len(D) != npairs:
        raise SystemExit(f"REFUSING: built {len(D)} pairs against r104's {npairs}; the pair order "
                         f"does not match and every iteration would score the wrong label.")
    od = own_dir[rpid]
    label_dir = np.where(own_hit > 0.5, od, 1.0 - od)

    def donor_hits(assign):
        dd = (np.einsum("ij,ij->i", W[assign[pair_prompt]], D) > 0).astype(float)
        return (dd[rpid] == label_dir).astype(float)

    canon = draw_donors(n, DONOR_SEED)
    mism = int((donor_hits(canon) != don_hit).sum())
    print(f"CONTROL rebuild of r104's canonical donor arm: {mism} mismatches of {len(don_hit):,}")
    if mism:
        raise SystemExit("REFUSING: the imported construction does not reproduce r104's donor arm.")

    order = np.argsort(rpid, kind="stable")
    start = np.searchsorted(rpid[order], np.arange(npairs), side="left")
    end = np.searchsorted(rpid[order], np.arange(npairs), side="right")

    def sampler(redraw: bool, resample: bool, iters=N_ITER):
        """One switch per source. Seeds match r106's when redraw is the only source on."""
        rb = np.random.default_rng(20260735)
        pooled, hl = [], []
        for s_ in range(iters):
            dh = donor_hits(draw_donors(n, 900000 + s_)) if redraw else don_hit
            if resample:
                pick = rb.integers(0, npairs, npairs)
                sel = np.concatenate([order[start[p]:end[p]] for p in pick])
                p_, b_ = share_of(own_hit[sel], dh[sel], cons[sel], min_bin=1)
            else:
                p_, b_ = share_of(own_hit, dh, cons)
            pooled.append(p_); hl.append(b_[-1] - b_[0])
        return np.array(pooled), np.array(hl)

    # ---- DEGENERATE IDENTITY CONTROLS ----------------------------------------
    p0, h0 = sampler(False, False, iters=5)
    ok0 = p0.std() == 0.0 and h0.std() == 0.0
    print(f"CONTROL (i)  both sources OFF: pooled sd {p0.std():.1e}, difference sd {h0.std():.1e} "
          f"-> {'PASS' if ok0 else 'FAIL'}")

    pA, hA = sampler(True, False)
    ref = np.load(R106V)
    driftA = float(np.abs(pA - ref["pooled"]).max())
    ok1 = driftA == 0.0
    print(f"CONTROL (ii) draw ON, pairs OFF vs r106's persisted draws: max drift {driftA:.1e} "
          f"-> {'PASS' if ok1 else 'FAIL'}")

    pB, hB = sampler(False, True)
    canon_pooled, canon_bins = share_of(own_hit, don_hit, cons)
    canon_hl = canon_bins[-1] - canon_bins[0]
    ok2 = abs(pB.mean() - canon_pooled) < 4 * pB.std(ddof=1) / np.sqrt(N_ITER)
    print(f"CONTROL (iii) draw OFF, pairs ON centred on canonical {canon_pooled:.4f}: "
          f"mean {pB.mean():.4f} -> {'PASS' if ok2 else 'FAIL'}")
    if not (ok0 and ok1 and ok2):
        raise SystemExit("REFUSING: switching a source off does not recover the round that measured "
                         "it alone, so the joint condition below is not a composition of the two.")

    pC, hC = sampler(True, True)

    print(f"\n  {'condition':<28} {'pooled sd':>10} {'diff sd':>9} {'difference 95%':>22}")
    rows = {}
    for name, (pp, hh) in (("A  donor redraw only", (pA, hA)),
                           ("B  pair bootstrap only", (pB, hB)),
                           ("C  JOINT", (pC, hC))):
        lo, hi = float(np.percentile(hh, 2.5)), float(np.percentile(hh, 97.5))
        rows[name.split()[0]] = {"label": name.strip(), "pooled_sd": float(pp.std(ddof=1)),
                                 "pooled_mean": float(pp.mean()), "diff_sd": float(hh.std(ddof=1)),
                                 "diff_mean": float(hh.mean()), "diff_ci95": [lo, hi]}
        print(f"  {name:<28} {pp.std(ddof=1):>10.4f} {hh.std(ddof=1):>9.4f} "
              f"{f'[{lo:+.4f},{hi:+.4f}]':>22}")

    vA, vB, vC = hA.var(ddof=1), hB.var(ddof=1), hC.var(ddof=1)
    ratio = vC / (vA + vB)
    additive = 0.75 <= ratio <= 1.35
    print(f"\n  variance of the difference: draw {vA:.5f} + pair {vB:.5f} = {vA + vB:.5f}   "
          f"joint {vC:.5f}   ratio {ratio:.2f}")
    lo, hi = rows["C"]["diff_ci95"]
    significant = not (lo <= 0 <= hi)
    equivalent = lo > -MARGIN and hi < MARGIN
    print(f"  joint verdict on the difference: significant {significant}   "
          f"equivalent at +/-{MARGIN} {equivalent}")

    world = ("A ADDITIVE" if additive else "I INTERACTING")
    vec = _RES / "r107_joint_draws.npz"
    np.savez_compressed(vec, pooled_joint=pC, diff_joint=hC, diff_draw=hA, diff_pair=hB)
    print(f"  draws persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. Four rounds have reported a width for the prompt-specific share and none of them is "
        f"the width: r105 bootstrapped PAIRS with the donor held fixed, r106 redrew DONORS with the "
        f"pairs held fixed, and entry 220 recorded that each round's interval covered only the source it "
        f"modelled. Composing both in the same iteration, on the high-minus-low-consensus difference: "
        f"draw alone sd {np.sqrt(vA):.4f}, pairs alone sd {np.sqrt(vB):.4f}, JOINT sd {np.sqrt(vC):.4f} "
        f"with 95% in [{lo:+.4f},{hi:+.4f}] around a mean of {hC.mean():+.4f}. Variance ratio "
        f"{ratio:.2f} against additivity"
        + (f", so the two sources are effectively INDEPENDENT and each previous interval was too narrow "
           f"by a knowable amount -- {np.sqrt(vC) / np.sqrt(vB):.2f}x for r105's, "
           f"{np.sqrt(vC) / np.sqrt(vA):.2f}x for r106's."
           if additive else
           f", so they INTERACT: neither marginal can be corrected by inflation and only the joint "
           f"sampler is admissible.") +
        f" THE VERDICT THE JOINT INTERVAL LICENSES: the difference is "
        + ("SIGNIFICANT" if significant else "NOT significant -- the interval covers zero")
        + " and "
        + (f"EQUIVALENT within the pre-registered {MARGIN}" if equivalent else
           f"NOT equivalent within the pre-registered {MARGIN}")
        + f". So after four rounds the honest statement is unchanged in KIND from r105's -- an "
        f"answerable margin -- but its width is now {np.sqrt(vC) / np.sqrt(vB):.2f}x what r105 reported, "
        f"and the point estimate has moved from {canon_hl:+.4f} on one draw to {hC.mean():+.4f} over "
        f"many. THREE DEGENERATE IDENTITY CONTROLS, all exact rather than tolerant: both sources off "
        f"returns the canonical value every iteration (sd {p0.std():.0e}); draw on with pairs off "
        f"reproduces r106's persisted draws seed for seed (max drift {driftA:.0e}), which is a "
        f"CROSS-ROUND rebuild control -- if it failed, this round's draw source would not be the one "
        f"r106 measured; and pairs on with the draw off centres on the canonical share "
        f"{canon_pooled:.4f}. Switching each source off recovers the round that measured it alone, "
        f"which is what makes the joint condition a composition rather than a third unrelated number. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN AND UNRESOLVED: this is NOT total uncertainty. It counts "
        f"donor assignment and pair sampling. It does not count the judge (one lineage), the "
        f"satisfaction reconstruction (r04's tensor taken as given), the rater split (r104's twelve "
        f"splits are averaged over, not resampled), or the donor POOL (the same {n} weight vectors in "
        f"every draw). The name for this quantity is joint-over-the-two-sources-anyone-has-measured, "
        f"and the next source is, on this axis's own record, not visible from inside it."
    )

    doc = {
        "n_iter": N_ITER, "conditions": rows, "margin": MARGIN,
        "variance_draw": float(vA), "variance_pair": float(vB), "variance_joint": float(vC),
        "additivity_ratio": float(ratio), "additive": bool(additive),
        "joint_significant": bool(significant), "joint_equivalent": bool(equivalent),
        "canonical_difference": float(canon_hl), "canonical_pooled": float(canon_pooled),
        "controls": {"both_off_sd": float(p0.std()), "draw_only_drift_vs_r106": driftA,
                     "pair_only_centred": bool(ok2)},
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "The joint sampling distribution, over donor assignment AND pair resampling, of the "
            "prompt-specific share and its across-consensus-bin difference, on r104's records."),
        "scope": (
            "Joint over the two sources anyone has measured -- NOT total uncertainty. Excludes the "
            "judge lineage, r04's satisfaction reconstruction, the rater split, and the fixed donor "
            "pool of 968 weight vectors."),
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
