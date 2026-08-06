#!/usr/bin/env python3
"""R819 · the per-prompt ratio is not estimable as R818 computed it.

R818 reported a per-prompt share averaged over prompts (`coval_core` 0.0617 against a corpus-level
0.5001), found four arms below the constant floor, and returned WORLD C on a Spearman of +0.9833.
CHECK #421 killed its NEXT on arithmetic — if margin were proportional to span the two statistics
would AGREE — and found the real defect: 12.8% of prompts have span < 0.05, the ratio runs to
−29.00, and the smallest-span decile contributes −503.1% of the total sum.

ESTIMAND        E1 the tail · E2 ⭐ the estimator curve · E3 ⭐ does the reordering survive ·
                E4 the retraction
IDENTIFICATION  a trimmed mean is a DIFFERENT estimand, not a better estimate of the same one; the
                family is reported and each claim names its member
DERIVED FIRST   D1 the span-weighted mean IS the corpus-level ratio, exactly — not a finding ·
                D2 under proportionality the whole family collapses to one number, so ANY
                disagreement disproves proportionality and kills R818's NEXT before a regression ·
                D3 the constant arm returns exactly 0 everywhere · D4 at eps=0 every member
                recovers a planted f, so the naive mean is not broken in general
WORLDS          A unstable · B real · C mixed — B checked FIRST
CONTROLS        OBJECT · PLACEBO · POSITIVE (plant + noise dose) · NEGATIVE · NOISE FLOOR
"""
import hashlib
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R818J = ARC / "R818_the_floor_nobody_subtracted/results/floor_subtracted.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
ARMS = ["coval_core", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k4",
        "genericpool16", "random_k4_s0", "gen_sham", "full"]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def weak_orders():
    seen = {}
    for v in itertools.product(range(4), repeat=4):
        seen.setdefault(tuple(int(np.sign(v[i] - v[j])) for i, j in PR), v)
    return np.array(sorted(seen))


def spearman(a, b):
    ra = np.argsort(np.argsort(-np.asarray(a, float)))
    rb = np.argsort(np.argsort(-np.asarray(b, float)))
    return float(np.corrcoef(ra, rb)[0, 1])


def family(m, s):
    """the estimator family for a per-prompt share. D1: 'weighted' IS the corpus-level ratio."""
    r = m / s
    o = np.argsort(s)
    n = len(s)
    def trim(pct):
        d = int(n * pct)
        return float(r[o[d:]].mean()) if d < n else float("nan")
    lo, hi = np.percentile(r, [5, 95])
    return {"naive": float(r.mean()), "trim5": trim(0.05), "trim10": trim(0.10),
            "trim20": trim(0.20), "median": float(np.median(r)),
            "winsor": float(np.clip(r, lo, hi).mean()),
            "weighted": float(m.sum() / s.sum())}


MEMBERS = ["naive", "trim5", "trim10", "trim20", "median", "winsor", "weighted"]


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ESTIMATOR"}
    W = weak_orders()
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    pids = [p for p in pids if len(H[p]) >= 2]
    N = len(pids)
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    A2 = {a: np.array([float((H[p] == CL[a][p]).mean()) for p in pids]) for a in ARMS}
    percon = np.zeros((len(W), N))
    for i, p in enumerate(pids):
        percon[:, i] = (H[p][None, :, :] == W[:, None, :]).mean(axis=(1, 2))
    bi = int(percon.mean(axis=1).argmax())
    fl = percon[bi]
    att = np.array([((H[p][None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
                    for p in pids])
    span = att - fl
    keep = span > 1e-12
    print(f"  POPULATION  {N} prompts · {int(keep.sum())} with a defined ratio · span mean "
          f"{span.mean():.4f} median {np.median(span):.4f}")
    print(f"     span below 0.05: {100 * (span < 0.05).mean():.1f}%   below 0.10: "
          f"{100 * (span < 0.10).mean():.1f}%")

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R818's committed per-prompt and corpus-level values")
    r818 = json.loads(R818J.read_text())
    pp = {a: float(((A2[a][keep] - fl[keep]) / span[keep]).mean()) for a in ARMS}
    # ⛔ D1's identity FAILED at 3.91e-02 on the first run because `weighted` was computed on the
    # `keep` subset while `corpus` used all 968 prompts and a POOLED floor. On the same population
    # sum(m)/sum(s) IS (mean A2 − mean fl)/(mean att − mean fl), exactly. Two populations, not two
    # quantities.
    FLOOR = float(fl[keep].mean())
    cl_corpus = {a: (float(A2[a][keep].mean()) - FLOOR) / (att[keep].mean() - FLOOR)
                 for a in ARMS}
    ok = (abs(pp["coval_core"] - r818["e3"]["per_prompt"]["coval_core"]) < 1e-6
          and abs(pp["random_k4_s0"] - r818["e3"]["per_prompt"]["random_k4_s0"]) < 1e-6)
    print(f"     per-prompt `coval_core` {pp['coval_core']:+.6f} vs R818's committed "
          f"{r818['e3']['per_prompt']['coval_core']:+.6f}")
    print(f"     per-prompt `random_k4_s0` {pp['random_k4_s0']:+.6f} vs committed "
          f"{r818['e3']['per_prompt']['random_k4_s0']:+.6f}   {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R818's per-prompt values did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"pp": pp, "corpus": cl_corpus, "n": N}

    # ================= E1 · the tail =============================================================
    print("\n  E1 - WHERE R818's PER-PROMPT NUMBER COMES FROM")
    r = (A2["coval_core"][keep] - fl[keep]) / span[keep]
    o = np.argsort(span[keep])
    d = int(keep.sum() // 10)
    print(f"     ratio range [{r.min():+.2f}, {r.max():+.2f}]   median {np.median(r):+.4f}")
    print(f"     smallest-span decile (span <= {span[keep][o[d - 1]]:.4f}): mean ratio "
          f"{r[o[:d]].mean():+.3f}")
    print(f"     remaining nine deciles:                          mean ratio "
          f"{r[o[d:]].mean():+.3f}")
    print(f"     ⭐ the smallest decile contributes {100 * r[o[:d]].sum() / r.sum():+.1f}% of the "
          f"total sum — it flips the aggregate's sign on its own")
    out["e1"] = {"min": float(r.min()), "max": float(r.max()),
                 "small_decile_mean": float(r[o[:d]].mean()),
                 "rest_mean": float(r[o[d:]].mean()),
                 "small_decile_share": float(r[o[:d]].sum() / r.sum())}

    # ================= E2 · the estimator curve ==================================================
    print("\n  E2 - THE ESTIMATOR FAMILY   (D1: `weighted` IS the corpus-level ratio, by identity)")
    fam = {a: family(A2[a][keep] - fl[keep], span[keep]) for a in ARMS}
    print(f"     {'arm':<16}" + "".join(f"{m:>10}" for m in MEMBERS) + f"{'corpus':>10}")
    for a in ARMS:
        print(f"     {a:<16}" + "".join(f"{fam[a][m]:>10.4f}" for m in MEMBERS)
              + f"{cl_corpus[a]:>10.4f}")
    ident = max(abs(fam[a]["weighted"] - cl_corpus[a]) for a in ARMS)
    print(f"     D1 check: max |weighted − corpus-level| = {ident:.2e}   "
          f"{'identity holds' if ident < 1e-9 else 'FAIL - not the same quantity'}")
    out["e2"] = fam

    # ================= E3 · does the reordering survive ==========================================
    print("\n  E3 - DOES R818's REORDERING SURVIVE ANY STABLE ESTIMATOR?")
    base = [cl_corpus[a] for a in ARMS]
    sps = {}
    for m in MEMBERS:
        sps[m] = spearman(base, [fam[a][m] for a in ARMS])
        print(f"     {m:<10} Spearman vs the corpus-level ordering: {sps[m]:+.4f}")
    below = {m: [a for a in ARMS if fam[a][m] < 0] for m in MEMBERS}
    print(f"     arms scoring BELOW the constant floor, by estimator:")
    for m in MEMBERS:
        print(f"        {m:<10} {len(below[m])}: {below[m] if below[m] else '—'}")
    out["e3"] = {"spearman": sps, "below_floor": {m: below[m] for m in MEMBERS}}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    zero = family(np.zeros(int(keep.sum())), span[keep])
    plac_ok = all(abs(zero[m]) < 1e-12 for m in MEMBERS)
    print(f"     PLACEBO   D3 the constant arm (margin identically 0) under every member: "
          f"{max(abs(zero[m]) for m in MEMBERS):.1e}   "
          f"{'PASS - exactly 0 everywhere' if plac_ok else 'FAIL'}")
    print("     POSITIVE  D4 plant an arm at a known share f of each prompt's span")
    rngp = np.random.default_rng(31337)
    pos = {}
    for f in (0.0, 0.25, 0.5):
        fm = family(f * span[keep], span[keep])
        pos[f] = fm
        print(f"        f={f:<5} " + "  ".join(f"{m} {fm[m]:+.4f}" for m in
                                               ("naive", "trim10", "median", "weighted")))
    pos_ok = all(abs(pos[f][m] - f) < 1e-9 for f in pos for m in MEMBERS)
    print(f"        every member recovers f exactly at eps=0: {pos_ok}   "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print("     ⛔ AND THE SEPARATING DOSE WAS BUILT WRONG THE FIRST TIME, in the way D2 had")
    print("        already named: it planted m = f·s EXACTLY — perfect proportionality — which D2")
    print("        says collapses the whole family to one number. A control that CANNOT separate,")
    print("        built after writing down that it cannot. And it targeted the MEAN, when what")
    print("        distinguishes these estimators is VARIANCE: r = f + eps/s is unbiased for any")
    print("        symmetric eps, so the naive mean stays put while its SPREAD explodes.")
    deg = {}
    for eps in (0.0, 0.01, 0.05):
        reps = []
        for _ in range(40):
            v = 0.5 * span[keep] + rngp.normal(0, eps, int(keep.sum()))
            reps.append(family(v, span[keep]))
        deg[eps] = {m: (float(np.mean([r[m] for r in reps])),
                        float(np.std([r[m] for r in reps]))) for m in MEMBERS}
        print(f"        eps={eps:<5} " + "  ".join(
            f"{m} {deg[eps][m][0]:+.4f}±{deg[eps][m][1]:.4f}"
            for m in ("naive", "trim10", "median", "weighted")))
    sep_ok = (deg[0.05]["naive"][1] > deg[0.05]["trim10"][1]
              and deg[0.05]["naive"][1] > deg[0.05]["weighted"][1]
              and deg[0.0]["naive"][1] < 1e-12)
    print(f"        the naive SPREAD exceeds trim10's and weighted's at eps=0.05, and is exactly 0")
    print(f"        at eps=0: {sep_ok}   {'PASS - the control can fail' if sep_ok else 'FAIL'}")
    # ⛔ THE FIRST NEGATIVE CONTROL TARGETED `weighted`, WHICH IS PERMUTATION-INVARIANT BY
    # CONSTRUCTION: sum(m)/sum(s) does not change when m is reordered. It returned a point mass
    # +0.5162 [+0.5162, +0.5162] exactly equal to the observation — the FIFTH degenerate null in
    # this session (R809, R810, R813, R816, and now here). [DERIVATION] so `weighted` cannot be
    # tested by this permutation at all, and the control must target the members that CAN move.
    rngn = np.random.default_rng(707)
    mm = A2["coval_core"][keep] - fl[keep]
    nul = {m: [] for m in MEMBERS}
    for _ in range(200):
        fmn = family(mm[rngn.permutation(len(mm))], span[keep])
        for m in MEMBERS:
            nul[m].append(fmn[m])
    movable = [m for m in MEMBERS if np.std(nul[m]) > 1e-12]
    neg_ok = bool(movable) and all(
        abs(np.mean(nul[m]) - fam["coval_core"][m]) > np.std(nul[m]) for m in movable)
    print(f"     NEGATIVE  margins shuffled across prompts, 200 draws.")
    print(f"               permutation-INVARIANT by construction (excluded from the test): "
          f"{[m for m in MEMBERS if m not in movable]}")
    for m in movable:
        print(f"               {m:<9} null {np.mean(nul[m]):+.4f} ± {np.std(nul[m]):.4f}   "
              f"real {fam['coval_core'][m]:+.4f}")
    print(f"               every movable member's real value lies outside its own null spread: "
          f"{neg_ok}   {'PASS' if neg_ok else 'FAIL'}")
    rngh = np.random.default_rng(55)
    hs = {m: [] for m in MEMBERS}
    for _ in range(20):
        s_ = rngh.permutation(int(keep.sum()))[: int(keep.sum()) // 2]
        fm = family(mm[s_], span[keep][s_])
        for m in MEMBERS:
            hs[m].append(fm[m])
    print(f"     NOISE FLOOR  20 half-splits: " +
          "  ".join(f"{m} sd {np.std(hs[m]):.4f}" for m in ("naive", "trim10", "median",
                                                            "weighted")))
    gate = ok and plac_ok and pos_ok and sep_ok and neg_ok
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "positive_ok": pos_ok, "separating_ok": sep_ok,
                       "negative_ok": neg_ok, "gate": gate,
                       "halfsplit_sd": {m: float(np.std(hs[m])) for m in MEMBERS}}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    idx = np.random.default_rng(1234).integers(0, N, (NBOOT, N))
    bs = np.array([(A2["coval_core"][i].mean() - FLOOR) / (att[i].mean() - FLOOR) for i in idx])
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    t10 = fam["coval_core"]["trim10"]
    inside = lo <= t10 <= hi
    if not gate:
        world = "UNVERIFIED"
    elif abs(sps["median"] - 1.0) < 1e-12 and inside:
        world = "A"
    elif abs(sps["median"] - 1.0) >= 1e-12:
        world = "B"
    else:
        world = "C"
    print(f"     median-based Spearman vs corpus-level: {sps['median']:+.4f}")
    print(f"     trim10 `coval_core` {t10:.4f} vs the corpus-level bootstrap CI "
          f"[{lo:.4f}, {hi:.4f}]: inside = {inside}")
    print(f"     -> WORLD {world}")
    out["world"] = world
    out["kill"] = {"trim10": t10, "corpus_lo": lo, "corpus_hi": hi, "inside": inside}

    art = HERE / "results/estimator_family.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
