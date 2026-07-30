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


def null_abs_r(n: int, rng, reps: int = 40000) -> float:
    """E|r| between two INDEPENDENT n-vectors.

    At n = 4 this is ~0.50, so any raw |r| near 0.6 is mostly the sample size.
    A magnitude reported without this floor invites exactly the reading the
    first draft of this round produced.
    """
    a = rng.normal(size=(reps, n))
    b = rng.normal(size=(reps, n))
    a = a - a.mean(1, keepdims=True)
    b = b - b.mean(1, keepdims=True)
    num = (a * b).sum(1)
    den = np.sqrt((a ** 2).sum(1) * (b ** 2).sum(1))
    ok = den > 1e-12
    return float(np.abs(num[ok] / den[ok]).mean())


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


def human_validation(pids, real, shuf, gold, comparisons, rubrics, rng, reps):
    """Attribution against GOLD vs against the released HUMAN rankings.

    Only possible on the ORIGINAL candidates -- the release contains no human
    rankings for generated responses, which is the whole reason a proxy is used
    on the fresh set.  So the proxy can be validated exactly where it is least
    length-driven, and is then applied where it is most length-driven.  That
    asymmetry is the point of computing this.
    """
    from covalx import load_join, parse_ranking
    LAB = ["A", "B", "C", "D"]

    def ipairs(asm):
        w = (asm.get("ranking_blocks") or {}).get("world") or []
        if not w:
            return []
        r = parse_ranking(w[0].get("ranking", ""))
        flat = [(l, gi) for gi, g in enumerate(r) for l in g]
        return [(x, y) for x, gx in flat for y, gy in flat if gx < gy]

    want = set(pids)
    human = {}
    for pid, comp, _rub in load_join(comparisons, rubrics):
        if pid not in want:
            continue
        prs = [pr for asm in comp["metadata"]["assessments"] for pr in ipairs(asm)]
        if prs:
            human[pid] = prs
    idx = {p: i for i, p in enumerate(pids)}

    def a_gold(sc, k):
        ok = tot = 0
        for x, y in combinations(range(4), 2):
            if gold[k, x] == gold[k, y]:
                continue
            tot += 1
            ok += int((sc[k, x] > sc[k, y]) == (gold[k, x] > gold[k, y]))
        return ok / tot if tot else np.nan

    def a_human(sc, k, prs):
        ok = tot = 0
        for x, y in prs:
            ix, iy = LAB.index(x), LAB.index(y)
            if sc[k, ix] == sc[k, iy]:
                continue
            tot += 1
            ok += int(sc[k, ix] > sc[k, iy])
        return ok / tot if tot else np.nan

    ag, ah = [], []
    for pid, prs in human.items():
        k = idx[pid]
        g = a_gold(real, k) - a_gold(shuf, k)
        h = a_human(real, k, prs) - a_human(shuf, k, prs)
        if np.isfinite(g) and np.isfinite(h):
            ag.append(g)
            ah.append(h)
    if len(ag) < 30:
        return None
    ag, ah = np.array(ag), np.array(ah)
    mg, lg, hg = boot_mean(ag, rng, reps)
    mh, lh, hh = boot_mean(ah, rng, reps)
    md, ld, hd = boot_mean(ah - ag, rng, reps)
    return {"n": len(ag), "gold": [mg, lg, hg], "human": [mh, lh, hh],
            "human_minus_gold": [md, ld, hd],
            "differ": bool(ld > 0 or hd < 0),
            "per_prompt_corr": float(np.corrcoef(ag, ah)[0, 1])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r47_gold_is_length.json")
    ap.add_argument("--boot", type=int, default=4000)
    ap.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    ap.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")
    rng = np.random.default_rng(20260728)

    receipts = {
        "r12 (discovery)": _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/"
                                   "r41_satisfaction_qwen2b_receipt.json",
        "r46 (held out)": _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/"
                                  "r46_satisfaction_receipt.json"}
    samples = [load_sample(
        "r12 (discovery)",
        _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/r41_satisfaction_qwen2b.npz",
        _ROOT / "02_attribution_under_attack/r12_response_set/results/a12_fresh_generations.json",
        ("mean_orig_real", "mean_orig_shuf", "mean_fresh_real", "mean_fresh_shuf"))]

    # r46 saved generations but collapsed its satisfaction to means it did not
    # persist, so the held-out sample enters only if a tensor exists for it.
    # persist.py writes into its OWN round's results directory, not r46's.
    r46 = _ROOT / "05_human_protocol_and_power/r41_criterion_support/results/r46_satisfaction.npz"
    if r46.exists():
        print("  note: the held-out tensor's donor permutation comes from persist.py's "
              "seed, not r46's, so its RAW attribution need not equal r46's published "
              "figure. The raw-vs-residualised contrast is within-tensor and unaffected.")
        samples.append(load_sample(
            "r46 (held out)", r46,
            _ROOT / "06_the_judges_mechanism/r46_spread_replication/results/r46_fresh_generations.json",
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
        # |r| MUST be read against its own null.  With four responses per prompt,
        # two INDEPENDENT vectors already give E|r| ~ 0.50, so a raw |r| of 0.62
        # is mostly the sample size.  The first draft reported these magnitudes
        # bare and they read as though gold were a length detector in BOTH sets;
        # half of that was n = 4.
        nullr = null_abs_r(S["gold_o"].shape[1], rng)
        print(f"  ...same, in MAGNITUDE |r|              original "
              f"{np.nanmean(np.abs(c_o)):.4f}   fresh {np.nanmean(np.abs(c_f)):.4f}"
              f"   (null for n={S['gold_o'].shape[1]}: {nullr:.4f})")
        print(f"  ...EXCESS over that null               original "
              f"{np.nanmean(np.abs(c_o)) - nullr:+.4f}   fresh "
              f"{np.nanmean(np.abs(c_f)) - nullr:+.4f}"
              f"   <- the SIGNED shift is the interpretable one; |r| is mostly n")
        print(f"  within-prompt word-count sd (mean)     original "
              f"{S['wl_o'].std(axis=1).mean():.1f}   fresh {S['wl_f'].std(axis=1).mean():.1f}")

        # PROXY VALIDATION, only possible on the ORIGINAL arm.
        rp = receipts.get(tag)
        if rp and Path(rp).exists():
            pids = [c["pid"] for c in json.loads(Path(rp).read_text())["criteria"]]
            hv = human_validation(pids, S["real_o"], S["shuf_o"], S["gold_o"],
                                  a.comparisons, a.rubrics, rng, a.boot)
            if hv:
                print(f"  proxy check on ORIGINAL: gold {hv['gold'][0]:+.4f} vs human "
                      f"{hv['human'][0]:+.4f}   diff {hv['human_minus_gold'][0]:+.4f} "
                      f"[{hv['human_minus_gold'][1]:+.4f},{hv['human_minus_gold'][2]:+.4f}]"
                      f" -> {'DIFFER' if hv['differ'] else 'indistinguishable'}"
                      f"   per-prompt r={hv['per_prompt_corr']:+.3f}")
        else:
            hv = None

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

        # THE PROCEDURE'S OWN NULL, and it is not a pass/fail gate.
        #
        # Residualising four responses on ANY variable removes one of three
        # degrees of freedom and perturbs the ordering by itself.  The first
        # version of this block tested that against an arbitrary 0.02 threshold
        # and flipped between pass and FAIL purely on the RNG state -- which is
        # the honest answer that the damage is real and comparable to the effect
        # being measured.
        #
        # So noise residualisation is not a gate, it is the BASELINE: the length
        # effect is length-residualised vs NOISE-residualised, never vs raw.
        # Averaged over several draws because a single noise vector is itself
        # a high-variance quantity at n = 4.
        nrep = 20
        no_o, no_f = [], []
        for _ in range(nrep):
            no_o.append(attribution(S["real_o"], S["shuf_o"],
                                    within_prompt_resid(S["gold_o"],
                                                        rng.normal(size=S["gold_o"].shape))))
            no_f.append(attribution(S["real_f"], S["shuf_f"],
                                    within_prompt_resid(S["gold_f"],
                                                        rng.normal(size=S["gold_f"].shape))))
        noise_o = np.nanmean(np.vstack(no_o), axis=0)
        noise_f = np.nanmean(np.vstack(no_f), axis=0)
        cm_o, clo_o, chi_o = boot_mean(noise_o, rng, a.boot)
        cm_f, clo_f, chi_f = boot_mean(noise_f, rng, a.boot)
        ctrl_ok = True
        print(f"  procedure null (residualise on NOISE, {nrep} draws)   original "
              f"{cm_o:+.4f} [{clo_o:+.4f},{chi_o:+.4f}]   fresh {cm_f:+.4f} "
              f"[{clo_f:+.4f},{chi_f:+.4f}]")
        print(f"    ^ raw was {m_o:+.4f} / {m_f:+.4f}, so removing ONE degree of freedom "
              f"costs {cm_o - m_o:+.4f} / {cm_f - m_f:+.4f} by itself")

        print(f"  attribution ORIGINAL   raw {m_o:+.4f} [{lo_o:+.4f},{hi_o:+.4f}]   "
              f"length-residualised {rm_o:+.4f} [{rlo_o:+.4f},{rhi_o:+.4f}]")
        print(f"  attribution FRESH      raw {m_f:+.4f} [{lo_f:+.4f},{hi_f:+.4f}]   "
              f"length-residualised {rm_f:+.4f} [{rlo_f:+.4f},{rhi_f:+.4f}]")
        inv_raw, inv_res = m_o - m_f, rm_o - rm_f
        inv_noise = cm_o - cm_f
        # The quantity that isolates LENGTH: how much of the inversion survives
        # length-residualisation, measured against what survives residualising
        # on nothing in particular.
        share_vs_noise = (inv_res / inv_noise) if abs(inv_noise) > 1e-9 else float("nan")
        print(f"  inversion   raw {inv_raw:+.4f}   NOISE-residualised {inv_noise:+.4f}   "
              f"LENGTH-residualised {inv_res:+.4f}")
        print(f"    -> vs the procedure's own null, length residualisation leaves "
              f"{share_vs_noise:.1%} of the inversion")
        print(f"  the INVERSION (orig - fresh)   raw {inv_raw:+.4f}   "
              f"residualised {inv_res:+.4f}   "
              f"({inv_res / inv_raw:.1%} of it survives)" if abs(inv_raw) > 1e-9 else "")
        out[tag] = {
            "corr_gold_length_original": float(np.nanmean(c_o)),
            "corr_gold_length_fresh": float(np.nanmean(c_f)),
            "abs_corr_gold_length_original": float(np.nanmean(np.abs(c_o))),
            "abs_corr_gold_length_fresh": float(np.nanmean(np.abs(c_f))),
            "abs_corr_null_for_n": nullr,
            "abs_corr_excess_original": float(np.nanmean(np.abs(c_o))) - nullr,
            "abs_corr_excess_fresh": float(np.nanmean(np.abs(c_f))) - nullr,
            "wordcount_sd_original": float(S["wl_o"].std(axis=1).mean()),
            "wordcount_sd_fresh": float(S["wl_f"].std(axis=1).mean()),
            "attribution_original_raw": [m_o, lo_o, hi_o],
            "attribution_fresh_raw": [m_f, lo_f, hi_f],
            "attribution_original_residualised": [rm_o, rlo_o, rhi_o],
            "attribution_fresh_residualised": [rm_f, rlo_f, rhi_f],
            "inversion_raw": inv_raw, "inversion_residualised": inv_res,
            "share_surviving": (inv_res / inv_raw) if abs(inv_raw) > 1e-9 else float("nan"),
            "procedure_null_noise_residualised": {
                "original": [cm_o, clo_o, chi_o], "fresh": [cm_f, clo_f, chi_f],
                "cost_of_one_dof_original": cm_o - m_o,
                "cost_of_one_dof_fresh": cm_f - m_f,
                "inversion_under_noise": inv_noise,
                "note": ("Not a pass/fail gate. Residualising 4 responses on ANY variable "
                         "removes one of three degrees of freedom and perturbs the "
                         "ordering, so this is the BASELINE the length effect is measured "
                         "against, never a threshold to clear.")},
            "share_surviving_vs_noise": share_vs_noise,
            # The decisive distinction: "own rubric does WORSE than an unrelated
            # one on fresh responses" is a bizarre claim demanding explanation.
            # "own rubric has NO advantage on fresh responses" is ordinary
            # transport failure.  Whether the length-residualised fresh arm is
            # still NEGATIVE is what separates them.
            "fresh_still_inverted_after_length": bool(rhi_f < 0),
            "fresh_residualised_ci": [rm_f, rlo_f, rhi_f],
            "proxy_validation_on_original": hv,
        }
        print()

    # ---- verdict, computed ------------------------------------------
    tags = list(out)
    # Against the procedure's own null, not against raw.
    shares = [out[t]["share_surviving_vs_noise"] for t in tags]
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
          f"the released candidates and generated ones. THE ASYMMETRY THAT MATTERS: the "
          f"proxy can only be validated against human rankings on the ORIGINAL arm, "
          f"because the release contains no human rankings for generated responses -- so "
          f"it is validated exactly where its length channel is WEAKEST and applied where "
          f"that channel is strongest. CONSEQUENCE EITHER WAY: r12 cannot be cited as "
          f"evidence of rubric transport failure without recording response length, and "
          f"H_fresh must collect it")
    inverted = [out[t]["fresh_still_inverted_after_length"] for t in tags]
    if all(inverted):
        inv_v = ("In BOTH samples the fresh arm stays NEGATIVE after length is removed, so "
                 "the own rubric really is out-performed by an unrelated one on generated "
                 "responses and that is not a length artifact")
    elif not any(inverted):
        inv_v = ("In BOTH samples the fresh arm stops being negative once length is "
                 "removed -- it becomes indistinguishable from zero. The INVERSION is a "
                 "length artifact; what survives is the weaker and far more ordinary "
                 "claim that the own-rubric advantage does not TRANSFER")
    else:
        inv_v = (f"The samples disagree on the sharpest point: the length-residualised "
                 f"fresh arm is still negative in {sum(inverted)} of {len(inverted)} "
                 f"samples. So 'the own rubric is BEATEN by an unrelated one on fresh "
                 f"responses' is not established -- what replicates is only that its "
                 f"advantage does not transfer. The inversion itself is at least partly "
                 f"length")
    verdict += ". " + inv_v
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
