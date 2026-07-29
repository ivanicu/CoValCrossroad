"""r47 -- is r12's inversion carried by the gold proxy's length channel?

CLAIM_CARD.md is the contract.  In one line: r40, r41 and r46 each tested a
property of the RUBRIC and each came back empty.  None tested the OUTCOME
VARIABLE.  r08's gold head was fitted with length as an explicit feature --
hstack([embedding, [char_len, word_len]]) @ w, char-length weight |w| = 0.2085
against a mean embedding weight of 0.0620 -- so if fresh responses vary in
length far more than the released candidates do, gold may be ordering them
largely by length, and "own rubric vs donor rubric on fresh" becomes partly a
contest over which rubric correlates with length.

Run on BOTH independent samples: r12's original 250 prompts and r46's 250
held-out ones.  The whole lesson of r46 was that same-sample checks do not
accumulate, so this one is built to run on two samples from the start.

The residualisation is applied to BOTH arms and BOTH response sets, because
testing only the fresh arm would let a general loss of signal look like a
targeted debunking.
"""
from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))


def within_prompt_resid(gold: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Regress gold on x within each prompt; return the residual ordering."""
    out = np.empty_like(gold)
    for k in range(gold.shape[0]):
        g, v = gold[k], x[k]
        if np.std(v) < 1e-12:
            out[k] = g - g.mean()
            continue
        b = np.cov(v, g, bias=True)[0, 1] / np.var(v)
        out[k] = g - (b * (v - v.mean()) + g.mean())
    return out


def corr_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Per-row Pearson correlation, NaN where a row is constant."""
    out = np.full(a.shape[0], np.nan)
    for k in range(a.shape[0]):
        if np.std(a[k]) > 1e-12 and np.std(b[k]) > 1e-12:
            out[k] = np.corrcoef(a[k], b[k])[0, 1]
    return out


def agreement(sc: np.ndarray, gd: np.ndarray) -> np.ndarray:
    n, m = sc.shape
    per = np.full(n, np.nan)
    for k in range(n):
        ok = tot = 0
        for x, y in combinations(range(m), 2):
            if gd[k, x] == gd[k, y]:
                continue
            tot += 1
            ok += int((sc[k, x] > sc[k, y]) == (gd[k, x] > gd[k, y]))
        if tot:
            per[k] = ok / tot
    return per


def attribution(real, shuf, gold):
    return agreement(real, gold) - agreement(shuf, gold)


def boot_mean(d, rng, reps):
    d = d[np.isfinite(d)]
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(reps)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def load_sample(tag, sat_npz, gen_json, means):
    """means: dict of the four score matrices already in the npz."""
    d = np.load(sat_npz)
    gen = json.loads(Path(gen_json).read_text())
    wl_o = np.array([[len(t.split()) for t in row] for row in gen["original"]], dtype=float)
    wl_f = np.array([[len(t.split()) for t in row] for row in gen["fresh"]], dtype=float)
    return {"tag": tag,
            "gold_o": d["gold_orig"], "gold_f": d["gold_fresh"],
            "real_o": d[means[0]], "shuf_o": d[means[1]],
            "real_f": d[means[2]], "shuf_f": d[means[3]],
            "wl_o": wl_o, "wl_f": wl_f}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r47_gold_is_length.json")
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")
    rng = np.random.default_rng(20260728)

    samples = [load_sample(
        "r12 (discovery)",
        _ROOT / "rounds/r41_criterion_support/results/r41_satisfaction_qwen2b.npz",
        _ROOT / "rounds/r12_response_set/results/a12_fresh_generations.json",
        ("mean_orig_real", "mean_orig_shuf", "mean_fresh_real", "mean_fresh_shuf"))]

    # r46 saved generations but collapsed its satisfaction to means it did not
    # persist, so the held-out sample enters only if a tensor exists for it.
    r46 = _ROOT / "rounds/r46_spread_replication/results/r46_satisfaction.npz"
    if r46.exists():
        print("  note: the held-out tensor's donor permutation comes from persist.py's "
              "seed, not r46's, so its RAW attribution need not equal r46's published "
              "figure. The raw-vs-residualised contrast is within-tensor and unaffected.")
        samples.append(load_sample(
            "r46 (held out)", r46,
            _ROOT / "rounds/r46_spread_replication/results/r46_fresh_generations.json",
            ("mean_orig_real", "mean_orig_shuf", "mean_fresh_real", "mean_fresh_shuf")))
    else:
        print("  ! r46 persisted no satisfaction tensor, so the held-out sample is "
              "ABSENT here -- this round runs on ONE sample and inherits exactly the "
              "weakness that killed the spread-loss effect. Stated, not hidden.\n")

    out = {}
    for S in samples:
        tag = S["tag"]
        print(f"=== {tag} ===")
        c_o = corr_rows(S["gold_o"], S["wl_o"])
        c_f = corr_rows(S["gold_f"], S["wl_f"])
        # The SIGNED mean can sit near zero while individual prompts are strongly
        # length-ordered in opposite directions, so the magnitude is reported
        # beside it.  Residualisation responds to magnitude, not to the sign.
        print(f"  within-prompt corr(gold, word count)   original {np.nanmean(c_o):+.4f}   "
              f"fresh {np.nanmean(c_f):+.4f}")
        print(f"  ...same, in MAGNITUDE |r|              original "
              f"{np.nanmean(np.abs(c_o)):.4f}   fresh {np.nanmean(np.abs(c_f)):.4f}")
        print(f"  within-prompt word-count sd (mean)     original "
              f"{S['wl_o'].std(axis=1).mean():.1f}   fresh {S['wl_f'].std(axis=1).mean():.1f}")

        base_o = attribution(S["real_o"], S["shuf_o"], S["gold_o"])
        base_f = attribution(S["real_f"], S["shuf_f"], S["gold_f"])
        m_o, lo_o, hi_o = boot_mean(base_o, rng, a.boot)
        m_f, lo_f, hi_f = boot_mean(base_f, rng, a.boot)

        g_o = within_prompt_resid(S["gold_o"], S["wl_o"])
        g_f = within_prompt_resid(S["gold_f"], S["wl_f"])
        # sanity floor: residualised gold must still order the responses
        ord_o = float(np.mean(g_o.std(axis=1) > 1e-9))
        ord_f = float(np.mean(g_f.std(axis=1) > 1e-9))
        if min(ord_o, ord_f) < 0.9:
            raise SystemExit("REFUSING TO REPORT: residualised gold no longer orders the "
                             "responses, so the comparison below is void")
        r_o = attribution(S["real_o"], S["shuf_o"], g_o)
        r_f = attribution(S["real_f"], S["shuf_f"], g_f)
        rm_o, rlo_o, rhi_o = boot_mean(r_o, rng, a.boot)
        rm_f, rlo_f, rhi_f = boot_mean(r_f, rng, a.boot)

        # POSITIVE CONTROL: residualising on noise gold does not encode must
        # barely move anything.  If it does, residualisation destroys signal by
        # construction and no comparison here is licensed.
        nz_o = within_prompt_resid(S["gold_o"], rng.normal(size=S["gold_o"].shape))
        nz_f = within_prompt_resid(S["gold_f"], rng.normal(size=S["gold_f"].shape))
        cm_o = float(np.nanmean(attribution(S["real_o"], S["shuf_o"], nz_o)))
        cm_f = float(np.nanmean(attribution(S["real_f"], S["shuf_f"], nz_f)))
        ctrl_ok = bool(abs(cm_o - m_o) < 0.02 and abs(cm_f - m_f) < 0.02)
        print(f"  control: residualise on NOISE            original {cm_o:+.4f} "
              f"(was {m_o:+.4f})   fresh {cm_f:+.4f} (was {m_f:+.4f}) -> "
              f"{'pass' if ctrl_ok else 'FAIL'}")
        if not ctrl_ok:
            raise SystemExit("REFUSING TO REPORT: residualising on noise moved the "
                             "attribution, so the procedure destroys signal by "
                             "construction")

        print(f"  attribution ORIGINAL   raw {m_o:+.4f} [{lo_o:+.4f},{hi_o:+.4f}]   "
              f"length-residualised {rm_o:+.4f} [{rlo_o:+.4f},{rhi_o:+.4f}]")
        print(f"  attribution FRESH      raw {m_f:+.4f} [{lo_f:+.4f},{hi_f:+.4f}]   "
              f"length-residualised {rm_f:+.4f} [{rlo_f:+.4f},{rhi_f:+.4f}]")
        inv_raw, inv_res = m_o - m_f, rm_o - rm_f
        print(f"  the INVERSION (orig - fresh)   raw {inv_raw:+.4f}   "
              f"residualised {inv_res:+.4f}   "
              f"({inv_res / inv_raw:.1%} of it survives)" if abs(inv_raw) > 1e-9 else "")
        out[tag] = {
            "corr_gold_length_original": float(np.nanmean(c_o)),
            "corr_gold_length_fresh": float(np.nanmean(c_f)),
            "abs_corr_gold_length_original": float(np.nanmean(np.abs(c_o))),
            "abs_corr_gold_length_fresh": float(np.nanmean(np.abs(c_f))),
            "wordcount_sd_original": float(S["wl_o"].std(axis=1).mean()),
            "wordcount_sd_fresh": float(S["wl_f"].std(axis=1).mean()),
            "attribution_original_raw": [m_o, lo_o, hi_o],
            "attribution_fresh_raw": [m_f, lo_f, hi_f],
            "attribution_original_residualised": [rm_o, rlo_o, rhi_o],
            "attribution_fresh_residualised": [rm_f, rlo_f, rhi_f],
            "inversion_raw": inv_raw, "inversion_residualised": inv_res,
            "share_surviving": (inv_res / inv_raw) if abs(inv_raw) > 1e-9 else float("nan"),
            "noise_control": {"original": cm_o, "fresh": cm_f, "passed": ctrl_ok},
        }
        print()

    # ---- verdict, computed ------------------------------------------
    tags = list(out)
    shares = [out[t]["share_surviving"] for t in tags]
    lifts = [out[t]["corr_gold_length_fresh"] - out[t]["corr_gold_length_original"]
             for t in tags]
    orig_kept = [out[t]["attribution_original_residualised"][0]
                 / out[t]["attribution_original_raw"][0]
                 if abs(out[t]["attribution_original_raw"][0]) > 1e-9 else float("nan")
                 for t in tags]
    mean_share = float(np.nanmean(shares))
    mean_orig_kept = float(np.nanmean(orig_kept))
    # NO BINARY AT 0.5.  The first run of this block branched on share < 0.5 and
    # got 50.2%, which would have printed "not a length artifact" off a coin
    # flip.  The quantity is a SHARE and it is reported as one; the only
    # qualitative distinction drawn is whether the fresh comparison loses more
    # than the original does, which is what "specific to the fresh set" means.
    selective = mean_orig_kept - mean_share
    verdict = (
        f"ROUGHLY HALF THE INVERSION IS CARRIED BY THE GOLD PROXY'S LENGTH CHANNEL: "
        f"{mean_share:.0%} of it survives residualising gold on within-prompt word count. "
        f"This is a SHARE, not a verdict -- it is near enough to half that no binary "
        f"reading is licensed, and the earlier draft of this round would have branched on "
        f"it at 0.5. "
        if 0.35 <= mean_share <= 0.65 else
        f"THE INVERSION IS LARGELY LENGTH-CARRIED: only {mean_share:.0%} survives "
        f"residualisation. "
        if mean_share < 0.35 else
        f"THE INVERSION IS MOSTLY NOT LENGTH-CARRIED: {mean_share:.0%} survives "
        f"residualisation. ")
    verdict += (
        f"The ORIGINAL-set advantage keeps {mean_orig_kept:.0%} of its size under the same "
        f"treatment, so the loss is "
        + (f"NOT specific to the fresh comparison (difference {selective:+.0%}) -- length "
           f"is load-bearing in both, which is itself a scope fact about the proxy"
           if abs(selective) < 0.15 else
           f"specific to the fresh comparison (difference {selective:+.0%})")
        + f". gold-length correlation moves {np.nanmean(lifts):+.3f} in signed mean between "
          f"the released candidates and generated ones. CONSEQUENCE EITHER WAY: r12 cannot "
          f"be cited as evidence of rubric transport failure without recording response "
          f"length, and H_fresh must collect it")
    if len(samples) == 1:
        verdict += (". ONE SAMPLE ONLY -- r46 persisted no satisfaction tensor, so this "
                    "carries exactly the weakness that killed the spread-loss effect and "
                    "is not established until it runs on the held-out set")
    print(f"-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "samples": out, "n_samples": len(samples), "verdict": verdict,
        "gold_head_note": ("r08's gold head is hstack([embedding, [char_len, word_len]]) @ w "
                           "with char-length |w| = 0.2085 against a mean embedding weight "
                           "of 0.0620 -- length is an explicit feature, not an incidental "
                           "correlate"),
        "scope": ("Length is not a nuisance by definition: a longer answer is often "
                  "genuinely better, so residualising it removes real signal along with "
                  "any artifact. A shrinking inversion shows the inversion is CARRIED BY "
                  "the length-aligned component, which is weaker than showing it is "
                  "spurious. Human preference on these responses is unobserved."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
