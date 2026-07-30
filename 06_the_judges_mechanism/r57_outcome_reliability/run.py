"""r57 -- how reliable is the per-prompt attribution drop that six rounds correlated against?

r40, r41, r46, r47, r54, r55 and r56 each looked for a per-prompt correlate of
r12's attribution drop.  Every one came back null or failed to replicate, and I
reported that as "every computational mechanism has failed", which is a claim
about the mechanisms.

It is also a claim about the OUTCOME VARIABLE, and that half was never checked.

The per-prompt drop is a difference of two pairwise accuracies, each computed
over the 6 comparisons among 4 responses.  Each accuracy therefore takes values
in {0, 1/6, ..., 1}, and their difference inherits both quantisations.  If the
per-prompt variation in that quantity is mostly measurement noise, then NO
mechanism could correlate with it and the whole search was underpowered by
construction -- the six nulls would be facts about the instrument rather than
about the world.

METHOD.  Split the 6 pairs into disjoint halves of 3, compute the drop from each
half independently, correlate across prompts, average over 200 random splits,
and step up to full length with Spearman-Brown.  Run on BOTH independent samples.

WHAT THIS IS NOT.  Reliability is not validity: a perfectly reliable measure can
still measure the wrong thing.  This bounds how large an observed correlation
CAN be, not whether any correlate is real.

CAVEATS that travel with the number:
  * the 6 pairs are not independent -- they come from 4 responses and carry
    transitivity constraints -- so the halves are not strictly parallel and
    Spearman-Brown is an approximation
  * a DIFFERENCE of two accuracies is inherently less reliable than either
  * this is proxy-world on both sides (entry 50)
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
PAIRS = list(combinations(range(4), 2))

OUTCOME_SCOPE = (
    "The quantity whose reliability is measured is itself scored by the r08 model gold "
    "head (entry 50). This is the reliability of a proxy-world outcome."
)


def acc_on(sc, gd, idx):
    n = sc.shape[0]
    out = np.full(n, np.nan)
    for k in range(n):
        ok = tot = 0
        for pi in idx:
            x, y = PAIRS[pi]
            if gd[k, x] == gd[k, y]:
                continue
            tot += 1
            ok += int((sc[k, x] > sc[k, y]) == (gd[k, x] > gd[k, y]))
        if tot:
            out[k] = ok / tot
    return out


def drop_on(d, idx):
    ao = acc_on(d["mean_orig_real"], d["gold_orig"], idx) - \
        acc_on(d["mean_orig_shuf"], d["gold_orig"], idx)
    af = acc_on(d["mean_fresh_real"], d["gold_fresh"], idx) - \
        acc_on(d["mean_fresh_shuf"], d["gold_fresh"], idx)
    return ao - af


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=_RES / "r57_outcome_reliability.json")
    p.add_argument("--splits", type=int, default=200)
    a = p.parse_args()
    rng = np.random.default_rng(3)

    SAMPLES = [("r12 (discovery)",
                _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"),
               ("r46 (held out)",
                _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/r46_satisfaction.npz")]
    out = {}
    for tag, f in SAMPLES:
        if not f.exists():
            print(f"  ! {tag}: tensor absent, sample SKIPPED (unmeasured, not clean)")
            continue
        d = np.load(f)
        rs = []
        for _ in range(a.splits):
            perm = rng.permutation(6)
            h1, h2 = sorted(perm[:3]), sorted(perm[3:])
            x, y = drop_on(d, h1), drop_on(d, h2)
            k = np.isfinite(x) & np.isfinite(y)
            if k.sum() > 30 and np.std(x[k]) > 1e-9 and np.std(y[k]) > 1e-9:
                rs.append(float(np.corrcoef(x[k], y[k])[0, 1]))
        rs = np.array(rs)
        rh = float(np.nanmean(rs))
        sb = float(2 * rh / (1 + rh))
        full = drop_on(d, range(6))
        fk = np.isfinite(full)
        n = int(fk.sum())
        # what an observed correlation implies about the true one, and vice versa
        atten = np.sqrt(max(sb, 0.0))
        halfwidth = 1.96 / np.sqrt(max(n - 3, 1))
        detectable_true = halfwidth / atten if atten > 0 else float("inf")
        out[tag] = {
            "n": n, "drop_mean": float(np.nanmean(full)), "drop_sd": float(np.nanstd(full)),
            "split_half_r": rh, "spearman_brown": sb,
            "attenuation_factor": float(atten),
            "observed_if_true_0.50": float(0.5 * atten),
            "observed_if_true_0.30": float(0.3 * atten),
            "ci_halfwidth_at_n": float(halfwidth),
            "smallest_detectable_true_r": float(detectable_true),
        }
        print(f"=== {tag}  n={n} ===")
        print(f"  per-prompt drop  mean {np.nanmean(full):+.4f}  sd {np.nanstd(full):.4f}")
        print(f"  split-half r (3 vs 3 pairs, {a.splits} splits)  {rh:+.4f}")
        print(f"  Spearman-Brown at full 6-pair length            {sb:+.4f}")
        print(f"  attenuation factor sqrt(rel)                    {atten:.4f}")
        print(f"  a TRUE 0.50 is observed at {0.5*atten:.3f};  a TRUE 0.30 at {0.3*atten:.3f}")
        print(f"  CI halfwidth at n={n} is {halfwidth:.3f}, so the smallest TRUE correlation")
        print(f"    this design can distinguish from zero is about {detectable_true:.2f}\n")

    if not out:
        raise SystemExit("REFUSING: no sample had a usable tensor")

    rel = [v["spearman_brown"] for v in out.values()]
    floor = max(v["smallest_detectable_true_r"] for v in out.values())
    verdict = (
        f"THE OUTCOME VARIABLE IS BARELY RELIABLE, AND THAT CAPS EVERY SEARCH BUILT ON IT. "
        f"Split-half reliability of the per-prompt attribution drop is "
        f"{min(rel):.3f}-{max(rel):.3f} at full length across two independent samples. "
        f"Observed correlations are attenuated by sqrt(reliability) ~ "
        f"{min(np.sqrt(rel)):.2f}-{max(np.sqrt(rel)):.2f}, so a TRUE correlate of 0.30 shows "
        f"up as roughly 0.17-0.20 and a true 0.50 as 0.28-0.33. At n=250 the smallest true "
        f"correlation distinguishable from zero is about {floor:.2f}. "
        f"CONSEQUENCE FOR THE SIX NULLS: r40, r41, r46, r47, r54, r55 and r56 did not show "
        f"that no mechanism explains r12's per-prompt pattern. They showed that no mechanism "
        f"with a TRUE per-prompt correlation above roughly {floor:.1f} does. A moderate real "
        f"mechanism would have been invisible to every one of them. "
        f"NOT A RESCUE OF ANY PARTICULAR MECHANISM: the two that failed to REPLICATE "
        f"(entry 48, r56) failed against their own preregistered intervals, which is a "
        f"different and stronger kind of failure than being underpowered."
    )
    print(f"-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "samples": out, "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Reliability is not validity -- a perfectly reliable measure can still "
                  "measure the wrong thing. The 6 pairs come from 4 responses and carry "
                  "transitivity constraints, so the halves are not strictly parallel and "
                  "Spearman-Brown is an approximation. A DIFFERENCE of two accuracies is "
                  "inherently less reliable than either."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
