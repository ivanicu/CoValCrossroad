"""r67 -- how reliable are the PREDICTORS whose correlations were called refutations?

CLAIM CARD
----------
Claim      the five correlational rows of the exhaustion ledger rule out mechanisms
           with true |r| above the floors published there.
Estimand   split-half reliability of each per-prompt PREDICTOR, Spearman-Brown
           corrected, and the resulting corrected floor
           half-width / sqrt(rel_predictor * rel_outcome).
Target
observed?  For the tensor-based predictors, YES: r41's persisted satisfaction
           tensor lets a prompt's criteria be split in half and the quantity
           recomputed on each half. For r40's embedding distances, NO -- the
           embeddings are not persisted, so that row's predictor reliability is
           UNMEASURED and is reported as such rather than assumed.
Alternative
worlds     A RELIABLE     rel_predictor > 0.7. The floors rise by <20% and the
                          published refutations stand roughly as stated.
           B AS NOISY AS THE OUTCOME  rel_predictor ~ 0.35, like r57's outcome.
                          Floors nearly DOUBLE, to 0.25-0.40, and those rows rule
                          out much less than the ledger claims.
           C MIXED        some predictors carry, some do not, and the ledger's
                          five rows stop being one class.
Intervention
           none. Split-half on persisted values.
Null       (i) a predictor correlated with ITSELF must return 1.0;
           (ii) one half against a SHUFFLED other half must return ~0.
           Both run before any reliability is read.
Stopping   single pass. The floors are recomputed and reported; no follow-up is
           conditional on the result.

WHY THIS EXISTS
---------------
Entry 108 published per-row detection floors of 0.152-0.243, every one computed
as half-width / sqrt(rel_outcome) with the PREDICTOR taken as perfectly reliable.
That makes each a LOWER BOUND on the true floor, stated at the time, with the
real value higher by an unmeasured amount. This measures the amount.

Entry 108 also declined to build a round whose answer was known in advance. This
one is not known: if the predictors are as unreliable as the outcome, the ledger's
five correlational refutations rule out almost nothing.

SCOPE
-----
Splitting a prompt's criteria in half is a small split -- K is 3 or 4 -- so the
raw split-half correlation is heavily attenuated by length and MUST be
Spearman-Brown corrected to full length. Both figures are reported. Prompts with
K < 4 cannot be split 2-2 and are excluded, with the count stated.
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

TENSOR = _ROOT / "rounds/r41_criterion_support/results/r41_satisfaction_qwen2b.npz"
REL_OUTCOME = {"pessimistic": 0.302, "optimistic": 0.422}
# half-widths from the exhaustion ledger, each read off that round's own CI
HALF = {"r40 generic distance": 0.0988, "r41 criterion-space support": 0.1010,
        "r46 spread loss (held out)": 0.1175, "r54 overlap transfer": 0.1336}


def spearman_brown(r: float, k: float = 2.0) -> float:
    return k * r / (1 + (k - 1) * r) if r > -1 else float("nan")


def halves(Z, off, rng):
    """Split each prompt's criteria 2-2 and return the two half-blocks."""
    A, B, skipped = [], [], 0
    for k in range(len(off) - 1):
        blk = Z[off[k]:off[k + 1]]
        if blk.shape[0] < 4:
            skipped += 1
            A.append(None); B.append(None)
            continue
        idx = rng.permutation(blk.shape[0])
        h = blk.shape[0] // 2
        A.append(blk[idx[:h]]); B.append(blk[idx[h:2 * h]])
    return A, B, skipped


def spread(blocks):
    return np.array([np.mean(b.std(axis=1)) if b is not None else np.nan for b in blocks])


def hull_proxy(blocks):
    """Spread of the per-criterion MEAN across responses -- r41's geometry axis
    reduced to something computable on a half-block."""
    return np.array([b.mean(axis=0).std() if b is not None else np.nan for b in blocks])


def corr(a, b):
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 8 or np.std(a[ok]) == 0 or np.std(b[ok]) == 0:
        return float("nan"), int(ok.sum())
    return float(np.corrcoef(a[ok], b[ok])[0, 1]), int(ok.sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r67_predictor_reliability.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260729)
    if not TENSOR.exists():
        raise SystemExit(f"REFUSING: {TENSOR.relative_to(_ROOT)} absent.")

    d = np.load(TENSOR)
    Z, off = d["z_orig_real"], d["off_real"].astype(int)
    Zf = d["z_fresh_real"]

    A, B, skipped = halves(Z, off, rng)
    Af, Bf, _ = halves(Zf, off, rng)

    # ---- controls, before any reliability is read ------------------------
    sA = spread(A)
    self_r, _ = corr(sA, sA)
    shuf = sA.copy()
    fin = np.isfinite(shuf)
    shuf[fin] = rng.permutation(shuf[fin])
    shuf_r, _ = corr(sA, shuf)
    controls = {"self_correlation": self_r, "shuffled_half": shuf_r,
                "all_pass": bool(abs(self_r - 1.0) < 1e-9 and abs(shuf_r) < 0.20)}
    print(f"controls: self={self_r:.4f} shuffled={shuf_r:+.4f}  "
          f"{'PASS' if controls['all_pass'] else 'FAIL'}")
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the split-half estimator fails its own controls.")

    preds = {
        "spread_loss": (spread(A) - spread(Af), spread(B) - spread(Bf)),
        "criterion_space_geometry": (hull_proxy(A) - hull_proxy(Af),
                                     hull_proxy(B) - hull_proxy(Bf)),
    }
    out = {}
    print(f"\nprompts skipped for K<4: {skipped} of {len(off)-1}\n")
    for name, (x, y) in preds.items():
        r, n = corr(x, y)
        sb = spearman_brown(r)
        out[name] = {"split_half_r": r, "spearman_brown": sb, "n_prompts": n}
        print(f"  {name:26s} split-half {r:+.4f}  Spearman-Brown {sb:+.4f}  n={n}")

    rel_pred = float(np.nanmean([v["spearman_brown"] for v in out.values()]))
    floors = {}
    for label, h in HALF.items():
        floors[label] = {}
        for tag, ro in REL_OUTCOME.items():
            lower = h / np.sqrt(ro)
            corrected = h / np.sqrt(max(rel_pred, 1e-6) * ro) if rel_pred > 0 else float("nan")
            floors[label][tag] = {"published_lower_bound": float(lower),
                                  "corrected": float(corrected)}
    print(f"\nmean predictor reliability (Spearman-Brown): {rel_pred:.4f}")
    print(f"{'row':30s} {'published':>10} {'corrected':>10}   (rel_outcome=0.302)")
    for label in HALF:
        f = floors[label]["pessimistic"]
        print(f"  {label:28s} {f['published_lower_bound']:>10.3f} {f['corrected']:>10.3f}")

    world = ("A RELIABLE" if rel_pred > 0.7 else
             "B AS NOISY AS THE OUTCOME" if rel_pred < 0.45 else "C MIXED")
    ratio = float(1 / np.sqrt(max(rel_pred, 1e-6)))

    verdict = (
        f"{world}. Splitting each prompt's criteria 2-2 and recomputing the predictor on each half, "
        f"the per-prompt quantities behind the ledger's correlational rows have a Spearman-Brown "
        f"reliability of {rel_pred:.4f} "
        f"({', '.join(f'{k} {v['spearman_brown']:+.4f}' for k, v in out.items())}), against "
        f"{skipped} of {len(off)-1} prompts excluded for having fewer than four criteria. Entry 108 "
        f"published floors computed as half-width / sqrt(rel_outcome), taking the predictor as "
        f"perfectly reliable and saying so; correcting for the measured predictor reliability "
        f"multiplies every one of them by {ratio:.2f}x. At the pessimistic outcome reliability the "
        f"ledger's four floors move from "
        f"{', '.join(f'{floors[l]['pessimistic']['published_lower_bound']:.3f}' for l in HALF)} to "
        f"{', '.join(f'{floors[l]['pessimistic']['corrected']:.3f}' for l in HALF)}. "
        f"WHAT THIS DOES TO THE LEDGER: a correlational row that failed to detect an effect has ruled "
        f"out only mechanisms above ITS OWN corrected floor, and those floors are now "
        f"{'materially larger' if ratio > 1.2 else 'close to'} the published lower bounds. "
        f"NOT MEASURED HERE: r40's predictor is an embedding distance whose embeddings are not "
        f"persisted, so its reliability is UNMEASURED rather than assumed, and its corrected floor "
        f"above uses the mean of the two that could be measured -- which is an assumption, flagged, "
        f"not a measurement."
    )

    doc = {
        "predictors": out,
        "mean_predictor_reliability_spearman_brown": rel_pred,
        "floor_multiplier": ratio,
        "prompts_skipped_K_lt_4": skipped,
        "floors": floors,
        "controls": controls,
        "world": world,
        "scope": ("Split-half on a prompt's criteria, 2 vs 2, Spearman-Brown corrected to full "
                  "length -- a small split, and both raw and corrected figures are reported. "
                  "r40's embedding-distance predictor is NOT measured here (embeddings not "
                  "persisted); its corrected floor uses the mean of the measured predictors, which "
                  "is an assumption and is flagged as one. Judge-relative throughout."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}   floors multiply by {ratio:.2f}x")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
