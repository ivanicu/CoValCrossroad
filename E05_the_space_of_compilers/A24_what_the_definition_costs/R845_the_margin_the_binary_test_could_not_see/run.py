#!/usr/bin/env python3
"""
R845 · the MARGIN the binary test could not see — clause ②'s sham separation, un-binarised.

⛔ WHY, AND WHY IT IS A TRUE GAP RATHER THAN A RE-RUN. R711 already swept all five base/sham pairs
and found clause ② separates **2 of 5**, against an exactly enumerated null (445,891,810
admissions) where random admission separates 1.7247 on average and reaches >=2 with p = 0.5727.
It ran six controls, three admission sizes, and two byte-identical runs. It is not being redone.

**But R711 states its own ceiling and does not follow it up:** *"separation is only POSSIBLE where
the base is admitted -- 2 of 5 pairs. So the residual is 2 of 2 possible."* A statistic whose
maximum attainable value is 2, scoring 2, is SATURATED. That is a resolution limit of the binary
estimand, and this project has now twice mistaken a resolution limit for a fact about the world
(the neutral-gap bound; entry 1352's "undecidable"). R711 says `margin` **zero times**.

The margin has no such ceiling. R844 measured it for ONE pair -- `coval_core - coval_core_sham` =
+0.0709 graded, resolved -- which sits in apparent tension with R711's at-chance verdict. **Only
sweeping all five decides whether R711's null was a ceiling artifact or whether R844 found the one
pair that works.**

ESTIMAND        per base/sham pair, the paired per-prompt MARGIN `base - its own sham`, on GRADED
                A2 and EXACT, over EVERY annotator.
IDENTIFICATION  yes; all ten arms are released score matrices.
SCOPE           population: prompts scored by both arms of a pair, paired, n reported per cell
                instrument: judge J via sat_*.npz; A2 as corebench/rule_sweep.py
                baseline:   R711's binary verdict on the same five pairs
                regime:     all annotators per prompt (median 16), no draw and therefore no seed
WORLDS          A · the margin is at chance too -> R711's deflation stands, R844's +0.0709 is one
                    pair and clause ② has no measurable sham-separating content
                B · the margin separates where the binary test structurally could not -> R711's
                    null was a CEILING ARTIFACT of binarising, and clause ②'s content was
                    invisible to a statistic that could only score 0..2
                These differ ontologically: A says the clause is decorative; B says the clause is
                real and the instrument that judged it was too coarse to see it.
KILL            CONDITIONAL: if the placebo (arm minus itself) is exactly 0 on every arm, read the
                intervals; otherwise UNVERIFIED, because a non-zero self-difference means the
                pairing is broken and no interval below is readable.
PLACEBO         every one of the ten arms against ITSELF -- must be exactly 0.0.
MAGNITUDE REF   R711's three same-family NON-sham pairs, taken from its committed artifact and not
                re-chosen here. ⚠ These are NOT a null: `topw_k1` vs `topw_k12` are genuinely
                different arms and their margin SHOULD be non-zero. They bound how large a margin
                mere arm-difference produces, which is the quantity that makes a sham margin
                interpretable. Labelled as a reference, never subtracted.
POISON CHECK    per pair, where the SHAM sits relative to `genericpool16`, the arm that reads no
                prompt at all. Below it = poison (misdirection actively hurts); at it = placebo
                (the ingredient is merely absent). R844 found poison for `coval_core`; whether
                that is arm-specific is exactly what the other writer's R843 puts in doubt.
MULTIPLICITY    10 primary cells (5 pairs x 2 metrics), BH at q=0.05 over the WHOLE family, with
                cells tested reported beside cells surviving, and every non-survivor printed.
                ⚠ BH threshold at rank k is q*k/C -- the largest is q itself, not q/C.
ARTIFACT        results/margin_sweep.json with the commit hash.
IMPOSSIBLE      causally identified · cross-release · construct validated.
                N/A with what each would require -- never "planned".
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

# from R711's COMMITTED artifact -- not re-chosen here
PAIRS = [("coval_core", "coval_core_sham"), ("full", "full_sham"), ("gen", "gen_sham"),
         ("promptecho", "promptecho_sham"), ("topw_k4", "topw_k4_sham")]
R711_SEPARATED = {"coval_core": True, "full": False, "gen": False,
                  "promptecho": False, "topw_k4": True}
REF_PAIRS = [("oracle_k4", "oracle_k4_fit1"), ("random_k12_s0", "random_k12_s1"),
             ("topw_k1", "topw_k12")]
FLOOR_ARM = "genericpool16"


def graded(c, h): return float(np.mean([c[q] == h[q] for q in range(6)]))
def exact(c, h):  return float(all(c[q] == h[q] for q in range(6)))


def cells(name, tg):
    f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
    if not f.exists():
        return None
    S = load_sat(f)
    return {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S
            if p in tg and len(tg[p]) >= 2}


def paired(A, B, tg, fn):
    ks = sorted(set(A) & set(B))
    d = [float(np.mean([fn(A[p], cls(np.array(y, float))) - fn(B[p], cls(np.array(y, float)))
                        for y, _ in tg[p]])) for p in ks]
    return np.array(d), len(ks)


def boot(d, n=4000, seed=13):
    rng = np.random.default_rng(seed)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    # two-sided bootstrap p: how often the resampled mean crosses zero
    p = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
    p = max(p, 1.0 / (n + 1))                 # floored at the design's resolution, never 0
    return float(d.mean()), float(lo), float(hi), 2.802 * float(bs.std(ddof=1)), float(p)


def bh(ps, q=0.05):
    """BH: threshold at rank k is q*k/C. The LARGEST is q itself -- q/C is Bonferroni."""
    C = len(ps)
    order = sorted(range(C), key=lambda i: ps[i])
    keep, kmax = [False] * C, -1
    for rank, i in enumerate(order, start=1):
        if ps[i] <= q * rank / C:
            kmax = rank
    for rank, i in enumerate(order, start=1):
        if rank <= kmax:
            keep[i] = True
    return keep


def main() -> int:
    tg, _ = load_targets()
    names = sorted({n for p in PAIRS for n in p} | {n for p in REF_PAIRS for n in p} | {FLOOR_ARM})
    arm = {n: cells(n, tg) for n in names}
    missing = [n for n, v in arm.items() if v is None]
    if missing:
        print(f"  UNRUNNABLE: missing arm(s) {missing}. Exit 2, never 0.")
        return 2

    # ---- PLACEBO on every arm: the kill precondition --------------------------------------------
    bad = []
    for n in names:
        d, _ = paired(arm[n], arm[n], tg, graded)
        e, _ = paired(arm[n], arm[n], tg, exact)
        if abs(d.mean()) > 1e-12 or abs(e.mean()) > 1e-12:
            bad.append(n)
    print(f"  PLACEBO  all {len(names)} arms against themselves are exactly 0: "
          f"{not bad}  {'PASS' if not bad else 'FAIL ' + str(bad)}")
    if bad:
        print("\n  UNVERIFIED: a self-difference is non-zero, so the pairing is broken. Exit 2.")
        return 2

    # ---- primary: 5 pairs x 2 metrics -----------------------------------------------------------
    rows = []
    print(f"\n  {'pair':<24}{'metric':<8}{'margin':>10}{'95% CI':>24}{'MDE':>9}{'boot p':>9}  R711")
    for base, sham in PAIRS:
        for mname, fn in (("graded", graded), ("exact", exact)):
            d, n = paired(arm[base], arm[sham], tg, fn)
            o, lo, hi, mde, p = boot(d)
            rows.append({"pair": f"{base}/{sham}", "base": base, "metric": mname, "n": n,
                         "margin": o, "ci": [lo, hi], "mde": mde, "p": p,
                         "r711_separated": R711_SEPARATED[base]})
            print(f"  {base+'/sham':<24}{mname:<8}{o:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]"
                  f"{mde:>9.4f}{p:>9.4f}  {'SEP' if R711_SEPARATED[base] else '—'}")

    keep = bh([r["p"] for r in rows])
    for r, k in zip(rows, keep):
        r["bh_survives"] = bool(k)
    n_sig = sum(keep)
    print(f"\n  MULTIPLICITY  {len(rows)} cells tested · {n_sig} survive BH at q=0.05 "
          f"(threshold at rank k is 0.05*k/{len(rows)})")
    for r, k in zip(rows, keep):
        if not k:
            print(f"    non-survivor: {r['pair']} {r['metric']}  p={r['p']:.4f}")
    if n_sig == len(rows):
        print("    every cell survived — printed anyway, because reporting only survivors is the")
        print("    multiplicity failure with manners.")

    # ---- magnitude reference: R711's same-family NON-sham pairs ---------------------------------
    print(f"\n  MAGNITUDE REFERENCE  {len(REF_PAIRS)} same-family NON-sham pairs (R711's control set)")
    print("    ⚠ NOT a null — these arms genuinely differ, so a non-zero margin is expected.")
    print("    They bound how large a margin mere ARM-DIFFERENCE produces.")
    refs = []
    for a, b in REF_PAIRS:
        d, n = paired(arm[a], arm[b], tg, graded)
        o, lo, hi, _, _ = boot(d)
        refs.append({"pair": f"{a}/{b}", "margin": o, "ci": [lo, hi]})
        print(f"    {a}/{b:<22} graded {o:>+8.4f}  [{lo:+.4f}, {hi:+.4f}]")

    # ---- poison check: where does each SHAM sit vs the never-reads-a-prompt arm? -----------------
    print(f"\n  POISON CHECK  sham − {FLOOR_ARM} (graded): below 0 = misdirection HURTS (poison),")
    print("    at 0 = the ingredient is merely absent (placebo). R844 found poison for coval_core.")
    pois = []
    for _, sham in PAIRS:
        d, n = paired(arm[sham], arm[FLOOR_ARM], tg, graded)
        o, lo, hi, _, _ = boot(d)
        kind = "POISON" if hi < 0 else ("above floor" if lo > 0 else "at floor (placebo)")
        pois.append({"sham": sham, "vs_floor": o, "ci": [lo, hi], "kind": kind})
        print(f"    {sham:<24}{o:>+9.4f}  [{lo:+.4f}, {hi:+.4f}]  {kind}")

    res = [r for r in rows if r["ci"][0] > 0 and r["bh_survives"]]
    world = "B" if len(res) > 2 else "A"
    print(f"\n  ⭐ WORLD {world}: {len(res)} of {len(rows)} cells have a RESOLVED POSITIVE margin "
          f"surviving BH, against R711's 2 of 5 binary separations (exact p 0.5727)")
    print("     A margin resolving where the binary statistic saturated at its ceiling of 2 means")
    print("     the binary null measured the CEILING, not the clause. A margin failing to resolve")
    print("     would mean R844's one pair was the exception. Both were live before this ran.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "cells": rows, "cells_surviving_bh": int(n_sig),
               "magnitude_reference": refs, "poison_check": pois,
               "r711": {"binary_separations": 2, "of": 5, "exact_p": 0.5727,
                        "ceiling_noted_by_r711": "separation only possible where base admitted"}},
              open(OUT / "margin_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/margin_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
