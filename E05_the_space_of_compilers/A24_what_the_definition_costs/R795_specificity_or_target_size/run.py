#!/usr/bin/env python3
"""R795 · is Q1's specificity about the RUBRIC's identity, or about the TARGET's SIZE?

R794 left specificity as a point estimate (+0.0487 to a random arm's class, no interval) and asked
for the interval. CHECK #397 attacked the comparison first: `full` carries mean k 15.48 and every k4
arm carries 4, so `vs full` against `vs (a k=4 arm's class)` varies WHOSE criteria and HOW MANY at
once. Delivering that interval as asked would have put a CI around a confounded quantity, which is
worse than the point it replaces because an interval reads as settled.

ESTIMAND        E1 ⭐ the size dose with content FIXED · E2 ⭐ identity at matched k=4 ·
                E3 ⭐ the specificity interval on a size-matched contrast · E4 `genericpool16`
IDENTIFICATION  exact given `sat_full.npz`'s per-criterion tensor. ⚠ "identity" means "built from
                this prompt's rubric text", nothing finer — the construct wall is untouched
DERIVED FIRST   D1 the dose must terminate at `vs full` = 0.7850 — the POSITIVE control ·
                D2 k=1 targets are often degenerate, so the low end is reported with its share ·
                D3 size and identity are separable by two ONE-factor comparisons ·
                D4 the core is 98.8% novel (R785), so no subset of `full` is a superset of it
WORLDS          A identity matters · B size explains it · C the target barely matters — C FIRST
CONTROLS        OBJECT (k=all reproduces 0.7850) · PLACEBO · POSITIVE (monotone dose, band) ·
                NEGATIVE (the same dose from a DIFFERENT prompt's full) · DEGENERACY share per k ·
                NOISE FLOOR (spread over 20 draws)
"""
import hashlib
import itertools
import json
import math
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
R794 = ARC / "R794_the_fork_was_an_artifact_of_two_targets/results/two_targets.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
KS = [1, 2, 4, 8, 12, "all"]
NDRAW = 20
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


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


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": "a (prompt, subset draw) TARGET", "claim_unit": "the k CELL",
           "claim_unit_e3": "a CONTRAST"}

    print("  OBJECT CHECK")
    if not R794.is_file():
        print("  UNRUNNABLE: R794's artifact is absent. Exit 2, never 0.")
        return 2
    prev = json.loads(R794.read_text())
    targets, _ = load_targets()
    fullS = load_sat(RES / "sat_full.npz")
    coreS = load_sat(RES / "sat_coval_core.npz")
    pids = sorted(p for p in fullS if p in coreS and p in targets and len(targets[p]) >= 2)
    P = len(pids)

    # per-criterion satisfaction tensor for `full`, padded
    idxs = [sorted({i for i, _ in fullS[p]}) for p in pids]
    KMAX = max(len(v) for v in idxs)
    T = np.zeros((P, KMAX, 4))
    M = np.zeros((P, KMAX), bool)
    for a, p in enumerate(pids):
        for c, i in enumerate(idxs[a]):
            M[a, c] = True
            for j, x in enumerate(L):
                T[a, c, j] = fullS[p].get((i, x), 0.0)
    ncrit = M.sum(axis=1)
    print(f"     prompts {P}   criteria per prompt: min {ncrit.min()} mean {ncrit.mean():.2f} "
          f"max {ncrit.max()}")

    CORE = np.array([cls(yvec(coreS[p], sorted({i for i, _ in coreS[p]}))) for p in pids], float)

    def cls_from_y(Y):
        """Y (P,4) -> (P,6) signs."""
        return np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])

    def agree(cm, tgt):
        return (cm == tgt).mean(axis=1)

    full_cls = cls_from_y(T.sum(axis=1))
    vs_full = float(agree(CORE, full_cls).mean())
    ref = prev["e1"]["arms"]["coval_core"]["vs_full"]
    okobj = abs(vs_full - ref) < 1e-9
    plac = float(agree(CORE, CORE).mean())
    print(f"     k=all reproduces R794's `vs full`: {vs_full:.10f} vs {ref:.10f}   "
          f"|Δ| {abs(vs_full - ref):.3e}   {'PASS' if okobj else 'FAIL'}")
    print(f"     PLACEBO  `coval_core` against its OWN class: {plac:.12f}   "
          f"{'PASS' if plac == 1.0 else 'FAIL'}")
    if not (okobj and plac == 1.0):
        print("  UNRUNNABLE: the endpoint disagrees with the committed number. Exit 2, never 0.")
        return 2
    out["object"] = {"prompts": P, "kmax": int(KMAX), "mean_k": float(ncrit.mean()),
                     "vs_full": vs_full, "r794": ref, "placebo": plac}

    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))

    def ci(v):
        b = v[BI].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
        return float(v.mean()), lo, hi, max(min(p, 1.0), 1.0 / (NBOOT + 1))

    def subset_target(k, rg, shift=0):
        """random k-subset of each prompt's criteria; shift>0 takes ANOTHER prompt's criteria."""
        Y = np.zeros((P, 4))
        for a in range(P):
            src = (a + shift) % P
            avail = int(ncrit[src])
            kk = avail if k == "all" else min(k, avail)
            pick = rg.choice(avail, kk, replace=False)
            Y[a] = T[src, pick, :].sum(axis=0)
        return cls_from_y(Y)

    # ================= E1 · the size dose, content fixed and content mismatched ===================
    print("\n  E1 - THE SIZE DOSE  (targets = k-subsets of `full`; matched vs a DIFFERENT prompt)")
    dose = {}
    for k in KS:
        for tag, shift in (("matched", 0), ("mismatched", 137)):
            rg = np.random.default_rng(SEEDS[0] + 41 + (0 if tag == "matched" else 7))
            vals, degen = [], []
            per_prompt = np.zeros(P)
            for d in range(NDRAW):
                tgt = subset_target(k, rg, shift)
                v = agree(CORE, tgt)
                vals.append(float(v.mean()))
                degen.append(float((np.abs(tgt).sum(axis=1) == 0).mean()))
                per_prompt += v
            per_prompt /= NDRAW
            dose[f"{k}_{tag}"] = {"mean": float(np.mean(vals)), "sd": float(np.std(vals, ddof=1)),
                                  "degenerate_share": float(np.mean(degen)),
                                  "per_prompt": per_prompt}
        m, mm = dose[f"{k}_matched"], dose[f"{k}_mismatched"]
        print(f"     k={str(k):<4} matched {m['mean']:.4f} (sd {m['sd']:.4f}, degenerate "
              f"{m['degenerate_share']:.3f})   mismatched {mm['mean']:.4f} (sd {mm['sd']:.4f})   "
              f"gap {m['mean'] - mm['mean']:+.4f}")
    seq = [dose[f"{k}_matched"]["mean"] for k in KS]
    monotone = all(seq[i] <= seq[i + 1] + 1e-9 for i in range(len(seq) - 1))
    band = abs(seq[-1] - seq[0]) > 1e-9
    ends_right = abs(seq[-1] - vs_full) < 1e-9
    posok = monotone and band and ends_right
    print(f"     POSITIVE  D1: matched dose monotone {monotone}, terminates at the committed "
          f"{vs_full:.4f} {ends_right}, band k=1→all {seq[0]:.4f}→{seq[-1]:.4f} {band}   "
          f"{'PASS' if posok else 'FAIL'}")
    negok = all(dose[f"{k}_matched"]["mean"] > dose[f"{k}_mismatched"]["mean"] for k in KS if k != 1)
    print(f"     NEGATIVE  the mismatched-prompt dose is below the matched one at every k>=2: "
          f"{negok}   world it excludes: 'the dose measures target SIZE in general'")
    out["e1"] = {k: {kk: vv for kk, vv in v.items() if kk != "per_prompt"}
                 for k, v in dose.items()}

    # ================= E2/E3 · identity at matched k = 4 ==========================================
    print("\n  E2/E3 - IDENTITY AT MATCHED k = 4")
    prev789 = json.loads((ARC / "R789_how_many_levels_the_a2_axis_resolves"
                          / "results/ladder.json").read_text())
    k4 = []
    for t in prev789["e2"]["a2"]:
        f = RES / f"sat_{t}.npz"
        cf = RES / f"core_{t}.json"
        if not (f.is_file() and cf.is_file()) or t == "coval_core":
            continue
        d = json.loads(cf.read_text())
        ks = [len(v) for v in d.values() if isinstance(v, list)]
        if not ks or abs(float(np.mean(ks)) - 4.0) > 1e-9:
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        k4.append((t, np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids],
                               float)))
    print(f"     size-matched comparators at k=4: {len(k4)}  ({', '.join(t for t, _ in k4[:6])}…)")
    matched4 = dose["4_matched"]["per_prompt"]
    rows, pv = [], []
    for t, cm in k4:
        v = agree(CORE, cm)
        e, lo, hi, p = ci(matched4 - v)
        rows.append({"arm": t, "vs_arm": float(v.mean()), "contrast": e, "lo": lo, "hi": hi,
                     "p": p})
        pv.append(p)
    rows.sort(key=lambda r: -r["contrast"])
    for r in rows[:5] + rows[-2:]:
        print(f"     vs `{r['arm']:<22}` {r['vs_arm']:.4f}   contrast (4-subset of full − this arm) "
              f"{r['contrast']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]  p {r['p']:.4f}")
    keep = bh(np.array(pv))
    mean_arm = float(np.mean([r["vs_arm"] for r in rows]))
    e3, e3lo, e3hi, e3p = ci(matched4 - np.mean(
        [agree(CORE, cm) for _, cm in k4], axis=0))
    print(f"     ⭐ E3  the SIZE-MATCHED specificity: a 4-subset of `full` "
          f"{dose['4_matched']['mean']:.4f} against the mean k=4 arm {mean_arm:.4f}  ->  "
          f"{e3:+.4f} [{e3lo:+.4f}, {e3hi:+.4f}]  p {e3p:.4f}   "
          f"{'RESOLVED' if (e3lo > 0 or e3hi < 0) else 'UNRESOLVED'}")
    print(f"     ⚠ R794 reported +0.0487 by comparing `vs full` (k=15.48) with a k=4 arm. The "
          f"size-matched contrast above is the same question with one factor.")
    out["e2"] = rows
    out["e3"] = {"eff": e3, "lo": e3lo, "hi": e3hi, "p": e3p, "mean_k4_arm": mean_arm,
                 "subset4": dose["4_matched"]["mean"], "bh_surviving": int(keep.sum()),
                 "bh_tested": len(pv)}

    # ================= E4 · the real size-matched comparator ======================================
    print("\n  E4 - THE REAL SIZE-MATCHED COMPARATOR")
    gp = RES / "sat_genericpool16.npz"
    if gp.is_file():
        S = load_sat(gp)
        GC = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids], float)
        vg = agree(CORE, GC)
        e, lo, hi, p = ci(agree(CORE, full_cls) - vg)
        print(f"     `coval_core` vs `genericpool16` (k=16, prompt-BLIND) {vg.mean():.4f}   "
              f"vs `full` (k={ncrit.mean():.2f}, prompt-MATCHED) {vs_full:.4f}")
        print(f"     contrast {e:+.4f} [{lo:+.4f}, {hi:+.4f}]  p {p:.4f}   "
              f"{'RESOLVED' if (lo > 0 or hi < 0) else 'UNRESOLVED'}   "
              f"-- one factor: both targets are large, one is this prompt's rubric")
        out["e4"] = {"vs_genericpool16": float(vg.mean()), "vs_full": vs_full, "eff": e,
                     "lo": lo, "hi": hi, "p": p}
    else:
        out["e4"] = None

    print(f"\n  MULTIPLICITY  {len(pv)} k=4 arm contrasts, BH q=0.05: surviving {int(keep.sum())}   "
          f"not {len(pv) - int(keep.sum())}   plus 12 dose cells reported whole")
    print(f"  NOISE FLOOR  subset-draw sd per cell, largest "
          f"{max(dose[f'{k}_matched']['sd'] for k in KS):.4f}")

    gate = okobj and plac == 1.0 and posok and negok
    out["controls"] = {"positive_ok": posok, "monotone": monotone, "ends_right": ends_right,
                       "negative_ok": negok, "gate": gate}
    print(f"  GATE  {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    print("\n  THE KILL -- conditional, gated on the controls")
    sds = max(dose[f"{k}_matched"]["sd"] for k in KS)
    flat = (max(seq[1:]) - min(seq[1:])) < sds
    if not gate:
        world = "UNVERIFIED"
    elif flat:
        world = "C"
    elif e3lo > 0:
        world = "A"
    elif e3lo <= 0 <= e3hi:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   dose flat from k=2 {flat}   E3 {e3:+.4f} [{e3lo:+.4f}, {e3hi:+.4f}]"
          f"  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/size_or_identity.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
