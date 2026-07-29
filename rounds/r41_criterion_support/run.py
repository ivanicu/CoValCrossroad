"""r41 step 2 (CPU) -- criterion-space support geometry.

CLAIM_CARD.md is the contract for this round; read it first.  In one line: r40
asked whether r12's discrepancy tracks GENERIC distance (hidden state,
likelihood) and found it does not -- it runs slightly the other way.  But a
rubric does not measure responses in embedding space.  It measures them in the
space its own criteria span:

    z_R(r) = ( s(c_1, r), ..., s(c_K, r) )        s in (0,1), sigmoid logit gap

A fresh response can be close in embedding, style, length and likelihood while
combining criterion satisfactions no original candidate exhibited.  That is a
support shift the generic metrics are blind to, and it is the distance a
rubric-conditioned failure would actually live in.

WHAT THIS CANNOT DO -- stated here because it belongs next to the numbers
-------------------------------------------------------------------------
z_R is produced by the same judge whose validity on fresh responses is exactly
what is unestablished.  So this round CANNOT separate

    (a) fresh responses occupy new normative territory
    (b) the judge scores them incoherently

It can only say whether the discrepancy is SPATIALLY ORGANISED in criterion
space rather than diffuse.  The judge-family disagreement measure is the one
handle on (b), and it is only available when a second lineage has been
persisted; when it has not, that world is reported UNVERIFIED, never excluded.

Four measures, all per prompt, all computed on the fresh responses against the
originals' own geometry:

  D_nn      nearest-original distance in criterion space, L2 / sqrt(K)
  D_hull    distance to the convex hull of the four originals, normalised by
            the originals' own spread -- "outside the region the rubric was
            written to discriminate"
  D_combo   fraction of fresh responses whose BINARISED criterion pattern does
            not occur among the four originals, swept over thresholds
  D_rank    extra rank instability of the fresh set under a criterion
            bootstrap -- if the ranking depends on which criteria you happened
            to draw, the rubric does not determine an order there

Outcome variable: the per-prompt attribution drop, ORIGINAL minus FRESH, taken
from r12's persisted per-prompt arrays.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import nnls
from scipy.stats import kendalltau, spearmanr

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
sys.path.insert(0, str(_ROOT))
_RES = _HERE / "results"

BOOT = 4000
NPERM = 4000
RNG = np.random.default_rng(20260728)


# ---------------------------------------------------------------- geometry
def hull_distance(Zo: np.ndarray, zf: np.ndarray) -> float:
    """Euclidean distance from zf to conv{columns of Zo}.

    min_{lam >= 0, sum lam = 1} || Zo lam - zf ||.  Solved as NNLS with the
    simplex constraint enforced by an appended heavily-weighted row, which is
    the standard reduction and is exact in the limit; M is set to 1e3 times the
    data scale, which puts the constraint violation ~7 orders below the
    distances being compared.
    """
    K, n = Zo.shape
    M = 1e3 * (np.abs(Zo).max() + 1.0)
    A = np.vstack([Zo, M * np.ones((1, n))])
    b = np.concatenate([zf, [M]])
    lam, _ = nnls(A, b)
    return float(np.linalg.norm(Zo @ lam - zf))


def rank_instability(Z: np.ndarray, boot: int, rng) -> float:
    """1 - mean Kendall tau between the full-criteria ranking and bootstrap ones.

    Z is K x n_resp.  If the ranking of the responses swings with which
    criteria were drawn, the rubric does not pin an order down on that set.
    Requires K >= 2; the caller excludes K == 1 rather than scoring it 0.
    """
    K, n = Z.shape
    full = Z.mean(axis=0)
    if np.allclose(full, full[0]):
        return np.nan
    taus = []
    for _ in range(boot):
        idx = rng.integers(0, K, size=K)
        s = Z[idx].mean(axis=0)
        if np.allclose(s, s[0]):
            taus.append(0.0)
            continue
        t = kendalltau(full, s).statistic
        taus.append(0.0 if np.isnan(t) else float(t))
    return float(1.0 - np.mean(taus))


def combo_novelty(Zo: np.ndarray, Zf: np.ndarray, thr: float) -> float:
    """Fraction of fresh responses whose binarised pattern is absent from originals."""
    po = {tuple((Zo[:, r] > thr).astype(int)) for r in range(Zo.shape[1])}
    novel = [tuple((Zf[:, r] > thr).astype(int)) not in po for r in range(Zf.shape[1])]
    return float(np.mean(novel))


# ---------------------------------------------------------------- statistics
def boot_ci(x: np.ndarray, y: np.ndarray, stat, reps: int, rng):
    n = len(x)
    vals = []
    for _ in range(reps):
        i = rng.integers(0, n, size=n)
        v = stat(x[i], y[i])
        if not np.isnan(v):
            vals.append(v)
    if not vals:
        return (np.nan, np.nan)
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(lo), float(hi)


def perm_p(x: np.ndarray, y: np.ndarray, stat, reps: int, rng) -> float:
    """Two-sided permutation p: how often does a reshuffled x reach |observed|?

    The null the claim card names -- permute the per-prompt novelty across
    prompts, preserving its marginal distribution.
    """
    obs = abs(stat(x, y))
    hits = 0
    for _ in range(reps):
        if abs(stat(rng.permutation(x), y)) >= obs:
            hits += 1
    return (hits + 1) / (reps + 1)


def pearson(a, b):
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a, b):
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return np.nan
    r = spearmanr(a, b).statistic
    return float(r) if not np.isnan(r) else np.nan


def partial_out(y: np.ndarray, *controls) -> np.ndarray:
    """Residual of y after least-squares removal of the controls plus intercept."""
    X = np.column_stack([np.ones(len(y))] + [np.asarray(c, dtype=float) for c in controls])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def analyse(name, x, y, rng, reps_boot, reps_perm):
    keep = np.isfinite(x) & np.isfinite(y)
    x, y = x[keep], y[keep]
    r = pearson(x, y)
    rs = spearman(x, y)
    lo, hi = boot_ci(x, y, pearson, reps_boot, rng)
    p = perm_p(x, y, pearson, reps_perm, rng)
    return {"measure": name, "n": int(keep.sum()), "pearson_r": r, "spearman_r": rs,
            "ci": [lo, hi], "excludes_zero": bool(np.isfinite(lo) and (lo > 0 or hi < 0)),
            "perm_p": p}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat", type=Path, default=_RES / "r41_satisfaction_qwen2b.npz")
    ap.add_argument("--receipt", type=Path, default=_RES / "r41_satisfaction_qwen2b_receipt.json")
    ap.add_argument("--sat2", type=Path, default=None,
                    help="second judge lineage, for judge-family disagreement")
    ap.add_argument("--r12", type=Path,
                    default=_ROOT / "rounds/r12_response_set/results/a12_response_set.json")
    ap.add_argument("--gen", type=Path,
                    default=_ROOT / "rounds/r12_response_set/results/a12_fresh_generations.json")
    ap.add_argument("--feat", type=Path,
                    default=_ROOT / "rounds/r39_feature_cache/results/r39_feature_cache.npz")
    ap.add_argument("--out", type=Path, default=_RES / "r41_criterion_support.json")
    ap.add_argument("--boot", type=int, default=BOOT)
    ap.add_argument("--perm", type=int, default=NPERM)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    if a.smoke:
        a.boot, a.perm = 50, 50
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- reduced resampling; must never reach the README ***")

    d = np.load(a.sat)
    receipt = json.loads(a.receipt.read_text())
    ctrl = receipt["reproduction_control"]
    if receipt.get("smoke"):
        raise SystemExit("REFUSING: the satisfaction tensor is from a smoke run")
    if ctrl["attempted"] and not ctrl["passed"]:
        raise SystemExit("REFUSING: the satisfaction tensor did not reproduce r12; "
                         "analysing it while quoting r12's drop would compare two "
                         "different measurements")
    print(f"judge={receipt['tag']}  reproduction control: "
          f"{'PASSED on ' + str(ctrl['n_compared']) + ' published numbers' if ctrl['passed'] else 'SKIPPED (' + str(ctrl['skipped_because']) + ')'}")

    off = d["off_real"]
    Zo_all, Zf_all = d["z_orig_real"], d["z_fresh_real"]
    n = len(off) - 1
    n_fresh = Zf_all.shape[1]

    # ---- outcome: per-prompt attribution drop ------------------------
    r12 = json.loads(a.r12.read_text())
    pids12 = r12["sets"]["ORIGINAL"]["per_prompt"]["pids"]
    pids = [c["pid"] for c in receipt["criteria"]]
    if pids12[:n] != pids[:n]:
        raise SystemExit("REFUSING: prompt order differs between r12 and the tensor")
    attr_o = np.array(r12["sets"]["ORIGINAL"]["per_prompt"]["attribution"], dtype=float)
    attr_f = np.array(r12["sets"]["FRESH"]["per_prompt"]["attribution"], dtype=float)
    drop = attr_o - attr_f
    print(f"prompts={n}  fresh_per_prompt={n_fresh}  "
          f"drop mean={drop.mean():+.4f} sd={drop.std():.4f}")

    # ---- length control ----------------------------------------------
    gen = json.loads(a.gen.read_text())
    wlen_o = np.array([np.mean([len(t.split()) for t in row]) for row in gen["original"]])
    wlen_f = np.array([np.mean([len(t.split()) for t in row]) for row in gen["fresh"]])
    dlen = wlen_f - wlen_o
    print(f"  median words  original={np.median(wlen_o):.0f}  fresh={np.median(wlen_f):.0f}"
          f"  (r40 found fresh LONGER; the length control exists because of that)")

    # ---- criterion-space measures ------------------------------------
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    D_nn = np.full(n, np.nan)
    D_hull = np.full(n, np.nan)
    D_combo = {t: np.full(n, np.nan) for t in thresholds}
    D_rank = np.full(n, np.nan)
    Kvec = np.zeros(n, dtype=int)
    spread_o = np.full(n, np.nan)

    for k in range(n):
        lo, hi = off[k], off[k + 1]
        Zo, Zf = Zo_all[lo:hi], Zf_all[lo:hi]          # K x 4 , K x n_fresh
        K = hi - lo
        Kvec[k] = K
        if K == 0:
            continue
        rt = np.sqrt(K)
        # originals' own spread: the natural yardstick for "far" on this prompt.
        pd = [np.linalg.norm(Zo[:, i] - Zo[:, j]) / rt
              for i in range(Zo.shape[1]) for j in range(i + 1, Zo.shape[1])]
        spread_o[k] = float(np.mean(pd)) if pd else np.nan

        nn, hl = [], []
        for r in range(n_fresh):
            zf = Zf[:, r]
            nn.append(min(np.linalg.norm(zf - Zo[:, o]) / rt for o in range(Zo.shape[1])))
            hl.append(hull_distance(Zo, zf) / rt)
        D_nn[k] = float(np.mean(nn))
        # Normalising by the originals' spread turns "far in absolute judge
        # units" into "far RELATIVE TO the distances this rubric was written to
        # resolve", which is the quantity the claim is about.  Prompts whose
        # four originals are indistinguishable to the rubric (spread ~ 0) have
        # no scale and are dropped rather than divided by a guard constant --
        # a 1e-9 guard is what produced a distance of 1e9 in r38.
        D_hull[k] = float(np.mean(hl)) / spread_o[k] if spread_o[k] > 1e-6 else np.nan
        for t in thresholds:
            D_combo[t][k] = combo_novelty(Zo, Zf, t)
        if K >= 2:
            io = rank_instability(Zo, 200, RNG)
            iff = rank_instability(Zf, 200, RNG)
            D_rank[k] = iff - io if np.isfinite(io) and np.isfinite(iff) else np.nan

    # ---- the confound D_rank must survive -----------------------------
    # A rubric that does not separate the four fresh responses CANNOT agree
    # with the gold ordering: its accuracy collapses toward chance and the
    # attribution drops.  So "unstable ranking" and "large drop" may be two
    # views of one quantity -- low discriminating power on the fresh set --
    # rather than a relationship between two things.  That is the
    # definitional-necessity trap, and the control is to partial out the
    # rubric's own score SPREAD on each set and see whether anything is left.
    ms_o, ms_f = d["mean_orig_real"], d["mean_fresh_real"]
    spread_score_o = ms_o.std(axis=1)
    spread_score_f = ms_f.std(axis=1)
    d_spread = spread_score_f - spread_score_o

    print(f"  criteria per prompt: min={Kvec.min()} median={int(np.median(Kvec))} max={Kvec.max()}")
    print(f"  K==1 prompts (excluded from the rank-bootstrap measure): {int((Kvec == 1).sum())}")
    print(f"  prompts with degenerate original spread (excluded from D_hull): "
          f"{int(np.sum(~np.isfinite(D_hull)))}")

    # ---- generic distance, for the collinearity check ----------------
    # Recomputed here from r39's cache rather than read from r40, which did not
    # persist per-prompt values (the sixth discard in this repository).  It is
    # therefore CLOSE TO but not identical with r40's array, and is used only
    # to ask whether criterion space is a different axis from embedding space.
    generic = np.full(n, np.nan)
    if a.feat.exists():
        f = np.load(a.feat, allow_pickle=True)
        if "qwen|mean_last" in f.files:
            E = f["qwen|mean_last"].astype(np.float32)
            # The reshape below assumes 8 rows per prompt, originals first, in
            # this prompt order.  Assuming it is how a row-order mismatch turns
            # `generic` into noise with a perfectly plausible shape, so it is
            # read off the cache's own meta rather than trusted.
            want = [f"{p}|{s}|{i}" for p in pids[:n]
                    for s, cnt in (("original", 4), ("fresh", n_fresh))
                    for i in range(cnt)]
            meta_ok = ("meta" in f.files and len(f["meta"]) == len(want)
                       and list(f["meta"]) == want)
            if not meta_ok:
                print("  ! feature-cache row order does not match this round's "
                      "(prompt, response) indexing; generic-distance check SKIPPED")
            elif E.shape[0] == n * (4 + n_fresh):
                E = E.reshape(n, 4 + n_fresh, -1)
                base = E[:, :4, :].reshape(-1, E.shape[-1])
                mu = base.mean(0)
                U, S, Vt = np.linalg.svd(base - mu, full_matrices=False)
                P = Vt[:48].T
                for k in range(n):
                    O = (E[k, :4] - mu) @ P
                    F = (E[k, 4:] - mu) @ P
                    generic[k] = float(np.mean([min(np.linalg.norm(F[r] - O[o])
                                                    for o in range(4))
                                                for r in range(F.shape[0])]))
            else:
                print(f"  ! feature cache has {E.shape[0]} rows, expected "
                      f"{n * (4 + n_fresh)}; generic-distance check SKIPPED")

    # ---- judge-family disagreement in criterion space ----------------
    fam = {"status": "UNVERIFIED",
           "why": "no second judge lineage persisted; world (b) 'the judge scores "
                  "fresh responses incoherently' is NOT excluded"}
    D_fam = np.full(n, np.nan)
    if a.sat2 and Path(a.sat2).exists():
        d2 = np.load(a.sat2)
        if np.array_equal(d2["off_real"], off):
            Zf2 = d2["z_fresh_real"]
            Zo2 = d2["z_orig_real"]
            for k in range(n):
                lo, hi = off[k], off[k + 1]
                if hi - lo == 0:
                    continue
                rt = np.sqrt(hi - lo)
                df = np.mean([np.linalg.norm(Zf_all[lo:hi, r] - Zf2[lo:hi, r]) / rt
                              for r in range(n_fresh)])
                do = np.mean([np.linalg.norm(Zo_all[lo:hi, r] - Zo2[lo:hi, r]) / rt
                              for r in range(4)])
                D_fam[k] = float(df - do)
            fam = {"status": "MEASURED", "second_judge": str(a.sat2),
                   "mean_excess_disagreement_on_fresh": float(np.nanmean(D_fam))}
        else:
            fam["why"] = "second lineage has different criterion offsets; not comparable"

    # ---- correlations -------------------------------------------------
    measures = {"D_nn_criterion_space": D_nn, "D_hull_violation": D_hull,
                "D_rank_instability_excess": D_rank}
    for t in thresholds:
        measures[f"D_combo_novelty@{t}"] = D_combo[t]
    if np.isfinite(D_fam).any():
        measures["D_judge_family_disagreement_excess"] = D_fam
    if np.isfinite(generic).any():
        measures["generic_nn_embedding (r40-style, recomputed)"] = generic

    print("\n=== per-prompt correlation with the attribution drop ===")
    print(f"{'measure':44s} {'n':>4s} {'r':>8s} {'rho':>8s} {'95% CI':>20s} {'perm p':>8s}")
    rows = []
    for name, x in measures.items():
        row = analyse(name, np.asarray(x, dtype=float), drop, RNG, a.boot, a.perm)
        rows.append(row)
        ci = f"[{row['ci'][0]:+.3f},{row['ci'][1]:+.3f}]"
        print(f"{name:44s} {row['n']:4d} {row['pearson_r']:+8.4f} "
              f"{row['spearman_r']:+8.4f} {ci:>20s} {row['perm_p']:8.4f}")

    # ---- length-controlled ---------------------------------------------
    print("\n=== after partialling out the fresh-minus-original length gap ===")
    ctrl_rows = []
    for name, x in measures.items():
        x = np.asarray(x, dtype=float)
        keep = np.isfinite(x) & np.isfinite(drop) & np.isfinite(dlen)
        if keep.sum() < 20:
            continue
        xr = partial_out(x[keep], dlen[keep])
        yr = partial_out(drop[keep], dlen[keep])
        row = analyse(name, xr, yr, RNG, a.boot, a.perm)
        row["corr_measure_with_length"] = pearson(x[keep], dlen[keep])
        ctrl_rows.append(row)
        ci = f"[{row['ci'][0]:+.3f},{row['ci'][1]:+.3f}]"
        print(f"{name:44s} {row['n']:4d} {row['pearson_r']:+8.4f} "
              f"{row['spearman_r']:+8.4f} {ci:>20s} {row['perm_p']:8.4f}"
              f"   (corr with dlen {row['corr_measure_with_length']:+.3f})")

    # ---- discriminating-power control -----------------------------------
    print("\n=== after ALSO partialling out the rubric's own score spread ===")
    print("    (a rubric that cannot separate the fresh responses must score near")
    print("     chance, so 'unstable' and 'inaccurate' risk being one quantity)")
    spread_rows = []
    for name, x in measures.items():
        x = np.asarray(x, dtype=float)
        keep = (np.isfinite(x) & np.isfinite(drop) & np.isfinite(dlen)
                & np.isfinite(d_spread))
        if keep.sum() < 20:
            continue
        xr = partial_out(x[keep], dlen[keep], d_spread[keep])
        yr = partial_out(drop[keep], dlen[keep], d_spread[keep])
        row = analyse(name, xr, yr, RNG, a.boot, a.perm)
        row["corr_measure_with_spread"] = pearson(x[keep], d_spread[keep])
        spread_rows.append(row)
        ci = f"[{row['ci'][0]:+.3f},{row['ci'][1]:+.3f}]"
        print(f"{name:44s} {row['n']:4d} {row['pearson_r']:+8.4f} "
              f"{row['spearman_r']:+8.4f} {ci:>20s} {row['perm_p']:8.4f}"
              f"   (corr with dspread {row['corr_measure_with_spread']:+.3f})")
    print(f"  corr(score spread change, attribution drop) = "
          f"{pearson(d_spread[np.isfinite(d_spread)], drop[np.isfinite(d_spread)]):+.4f}")

    # ---- is criterion space a DIFFERENT axis? ---------------------------
    collin = {}
    if np.isfinite(generic).any():
        print("\n=== collinearity: does criterion space add an axis embedding distance lacks? ===")
        for name in ("D_nn_criterion_space", "D_hull_violation"):
            x = np.asarray(measures[name], dtype=float)
            keep = np.isfinite(x) & np.isfinite(generic)
            r = pearson(x[keep], generic[keep])
            collin[name] = {"r_with_generic": r, "n": int(keep.sum())}
            print(f"  corr({name}, generic embedding NN) = {r:+.4f}  n={int(keep.sum())}")

    # ---- verdict, computed, never written by hand -----------------------
    # Two DIFFERENT questions are being answered and the first version of this
    # block collapsed them into one, which hid the only positive result.
    #   support    -- do fresh responses leave the region the rubric describes?
    #   determinacy -- does the rubric pin an ORDER on them at all?
    # A rubric can describe a response perfectly and still not rank it.
    by = {r["measure"]: r for r in ctrl_rows}
    by_sp = {r["measure"]: r for r in spread_rows}

    def live(row):
        return bool(row and row["excludes_zero"] and row["perm_p"] < 0.05)

    # Liveness is judged on the FULLY controlled row.  Judging it on the
    # length-controlled row would let this round announce an inverted support
    # effect that its own discriminating-power control had already dissolved,
    # which is the confession-never-audited failure written into a verdict.
    names = ("D_nn_criterion_space", "D_hull_violation")
    support = [by_sp[m] for m in names if m in by_sp]
    sup_sig = [r for r in support if live(r)]
    sup_neg = [r for r in sup_sig if r["pearson_r"] < 0]
    sup_pos = [r for r in sup_sig if r["pearson_r"] > 0]
    sup_len_sig = [by[m] for m in names if m in by and live(by[m])]

    rk, rk_sp = by.get("D_rank_instability_excess"), by_sp.get("D_rank_instability_excess")

    if not support:
        support_v = ("UNVERIFIED: no support measure survived the controls with "
                     "enough prompts to correlate")
    elif not sup_sig and sup_len_sig:
        support_v = (
            "SUPPORT CONFOUNDED: criterion-space novelty tracks the drop before the "
            f"discriminating-power control ({sup_len_sig[0]['measure']} = "
            f"{sup_len_sig[0]['pearson_r']:+.4f}) and does NOT survive it. What looked "
            "like geometry is the rubric separating the fresh responses less than it "
            "separated the originals -- one quantity, not a relationship between two")
    elif not sup_sig:
        support_v = ("SUPPORT NOT DETECTED: the drop is not organised along "
                     "criterion-space novelty. A non-rejection at this sample size, "
                     "not evidence of a diffuse discrepancy")
    elif sup_pos and not sup_neg:
        support_v = ("SUPPORT SHIFT: the drop is larger where fresh responses leave "
                     "the originals' criterion support, which generic distance could "
                     "not see")
    elif sup_neg and not sup_pos:
        support_v = ("SUPPORT INVERTED: the drop is larger where fresh responses sit "
                     "INSIDE the originals' criterion support -- the same sign r40 "
                     "found generically. A rubric-conditioned support failure does "
                     "NOT explain r12's discrepancy")
    else:
        support_v = ("SUPPORT SPLIT: the two support measures disagree in sign, so "
                     "this is not a single axis and neither reading holds")

    if not live(rk):
        rank_v = "determinacy not detected"
    elif not live(rk_sp):
        rank_v = ("DETERMINACY CONFOUNDED: rank instability tracks the drop "
                  f"({rk['pearson_r']:+.4f}) but does NOT survive controlling for the "
                  "rubric's own score spread, so it may be a restatement of low "
                  "discriminating power rather than a relationship")
    else:
        rank_v = (f"DETERMINACY: rank instability under a criterion bootstrap tracks "
                  f"the drop at {rk_sp['pearson_r']:+.4f} even after removing both the "
                  f"length gap and the rubric's own score spread. Where the ranking "
                  f"depends on WHICH criteria were drawn, the advantage falls -- a "
                  f"failure to determine an order, not a failure to cover the region")
    verdict = f"{support_v}. {rank_v}."
    print(f"\n-> {verdict}")
    if fam["status"] != "MEASURED":
        print("   world (b) -- the judge scores fresh responses incoherently -- "
              "remains UNVERIFIED: no second lineage was supplied")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "judge": receipt["tag"], "judge_checkpoint": receipt["judge_checkpoint"],
        "reproduction_control": ctrl,
        "prompts": n, "fresh_per_prompt": n_fresh,
        "criteria_per_prompt": {"min": int(Kvec.min()), "max": int(Kvec.max()),
                                "median": float(np.median(Kvec)),
                                "n_K_eq_1": int((Kvec == 1).sum())},
        "drop": {"mean": float(drop.mean()), "sd": float(drop.std())},
        "length": {"median_words_original": float(np.median(wlen_o)),
                   "median_words_fresh": float(np.median(wlen_f))},
        "thresholds_swept": thresholds,
        "raw": rows, "length_controlled": ctrl_rows,
        "length_and_spread_controlled": spread_rows,
        "spread_control_note": (
            "d_spread = sd of the own-rubric mean satisfaction across the four "
            "responses, fresh minus original. A rubric that cannot separate the "
            "fresh responses must score near chance against gold, so this control "
            "asks whether any measure predicts the drop beyond that necessity."),
        "collinearity_with_generic_embedding": collin,
        "judge_family": fam,
        "per_prompt": {"pids": pids[:n], "drop": drop.tolist(),
                       "D_nn": D_nn.tolist(), "D_hull": D_hull.tolist(),
                       "D_rank": D_rank.tolist(),
                       "D_combo_0.5": D_combo[0.5].tolist(),
                       "generic_nn": generic.tolist()},
        "verdict": verdict,
        "scope": ("judge-relative. z_R is produced by the same judge whose "
                  "off-distribution validity is unestablished, so this round cannot "
                  "separate 'new normative territory' from 'the judge scores fresh "
                  "responses incoherently'. It measures whether the discrepancy is "
                  "spatially organised, nothing more."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
