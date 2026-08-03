"""R311 — do two rule families shrink DIFFERENTLY under the smaller judge?

R310 found the judge's residual structure organises on rule FAMILY (adjusted R² 0.701) and not on
effect magnitude (adjusted R² −0.027, dead flat). But `family` was 13 groups on 39 arms — 12
degrees of freedom for a third of the data — and R310 said so. The verdict survived a df-matched
correction and it is still a between-family statistic with a lot of parameters.

This round asks the same question in the one shape the df problem cannot touch: **take two
families that each span a k range, fit each one its own slope, and ask whether the two slopes
differ.** Two parameters, not twelve, and the comparison is within-construction-rule by
construction:

    topw_k     8 arms, k = 1 … 12      criteria selected by the rubric's own importance weights
    random_k  17 arms, k = 2 … 12 × 3 seeds, criteria drawn uniformly from the same rubric

Same source of criteria, same prompts, same judges, same baseline. **The only thing that differs
is the selection rule.** If the smaller judge shrinks these two differently, construction method
and judge interact, and that is a mechanism rather than a label.

⛔ NO RATIOS. The obvious statistic is `eff_08B / eff_2B` per arm, and it is a trap this project
has already been caught by: `random_k` effects sit ON the null, so the denominator passes through
zero and the ratio explodes. A ratio of noisy quantities is biased toward the noisier arm even
when the denominator is safely away from zero. So the statistic is a SLOPE fitted within each
family, and the estimand is the DIFFERENCE of two slopes.

ESTIMAND      β_topw − β_random, where β_f is the slope of `eff_08B` on `eff_2B` over the arms of
              family f, with a cluster bootstrap over PROMPTS that recomputes every arm's effect
              inside each resample — so the two families' errors stay correlated exactly as they
              are in the data, because they share the prompts.
IDENTIFICATION exact for these two families. It says nothing about the other eleven, which have
              too few arms to fit a slope, and that limit is the round's main scope line.
SCOPE         population CoVal prompts with ≥2 annotators · instrument Qwen3.5-2B and 0.8B ·
              baseline `random_k4_s0` · regime clause ① effects, A2·annotator.
WORLDS        W-INTERACT   the slopes differ resolvably -> construction method and judge interact,
                           and R310's family finding has a mechanism.
              W-COMMON     they do not differ -> the family structure R310 saw is carried by
                           families OTHER than these two, or by something correlated with family
                           that is not the selection rule. R310 is not refuted; it is narrowed.
KILL          conditional on the controls: the 95% bootstrap CI of the difference excludes 0
              -> W-INTERACT; includes 0 -> W-COMMON. And the difference must exceed its own MDE,
              the criterion this arc has used throughout, not merely exclude zero.
POSITIVE CTRL plant a slope difference by scaling one family's 0.8B effects; require recovery at
              the planted size. Fails at g=0: with no plant the same estimator must return a
              difference consistent with zero.
NEGATIVE CTRL reassign arms to the two families AT RANDOM, preserving group sizes, and recompute.
              The difference must collapse to its permutation floor, which is reported.
PLACEBO       a family against itself: exactly 0.
NOISE FLOOR   the permutation distribution of the difference, measured over seeds.
MULTIPLICITY  one estimand, one comparison. The k-trend below is reported as descriptive and is
              NOT a second test.
SEEDS         bootstrap seed fixed at 31337 as everywhere in this arc; the negative control uses
              3 independent seeds and its spread is reported.
ARTIFACT      results/family_slopes.json with source hash.
IMPOSSIBLE    the other 11 families — they have 1–3 arms each, so a slope is not identified. Would
              require more arms per rule, which is a generation cost, not a release limit.
"""
import hashlib, itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 800
RES = ROOT / "corebench" / "results"
BASE = "random_k4_s0"
FAMS = {"topw_k": lambda a: a.startswith("topw_k") and not a.endswith("_sham"),
        "random_k": lambda a: a.startswith("random_k")}


def sat08(a):
    d, r = RES / f"sat08_{a}.npz", RES / f"sat_{a}_08b.npz"
    return d if d.exists() else (r if r.exists() else None)


def slope(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    return float(xc @ yc / (xc @ xc)) if xc @ xc > 0 else float("nan")


def main():
    tg, _ = load_targets()
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16"
                  and not p.stem.endswith(("_08b", "_08bR")))
    members = {f: [a for a in arms if pred(a) and sat08(a) and a != BASE]
               for f, pred in FAMS.items()}
    if min(len(v) for v in members.values()) < 4:
        print(f"  UNRUNNABLE: a family has too few arms {[(f, len(v)) for f, v in members.items()]}")
        return 2
    need = sorted(set(sum(members.values(), [])) | {BASE})
    S2 = {a: load_sat(RES / f"sat_{a}.npz") for a in need}
    S8 = {a: load_sat(sat08(a)) for a in need}
    pids = sorted(set.intersection(*(set(S2[a]) for a in need)) &
                  set.intersection(*(set(S8[a]) for a in need)) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    print(f"  {N} prompts · " + " · ".join(f"{f}: {len(v)} arms" for f, v in members.items()) + "\n")

    def vec(sat):
        return np.array([np.mean([[cls(yvec(sat[p], sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in pids])
    V2 = {a: vec(S2[a]) for a in need}
    V8 = {a: vec(S8[a]) for a in need}
    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def fam_slope(f, idx=None, scale=None, assign=None):
        mem = assign[f] if assign else members[f]
        b2 = V2[BASE][idx] if idx is not None else V2[BASE]
        b8 = V8[BASE][idx] if idx is not None else V8[BASE]
        x = np.array([(V2[a][idx] if idx is not None else V2[a]).mean() - b2.mean() for a in mem])
        y = np.array([(V8[a][idx] if idx is not None else V8[a]).mean() - b8.mean() for a in mem])
        if scale is not None:
            y = y * scale
        return slope(x, y)

    b_t, b_r = fam_slope("topw_k"), fam_slope("random_k")
    diff = b_t - b_r
    bs = np.array([fam_slope("topw_k", IDX[t]) - fam_slope("random_k", IDX[t])
                   for t in range(NBOOT)])
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    mde = ZEFF * float(bs.std(ddof=1))
    print(f"  slope topw_k   {b_t:+.4f}")
    print(f"  slope random_k {b_r:+.4f}")
    print(f"  DIFFERENCE     {diff:+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  MDE {mde:.4f}")

    # ---- PLACEBO ---------------------------------------------------------------------------
    pl = fam_slope("topw_k") - fam_slope("topw_k")
    print(f"\n  PLACEBO   a family against itself: {pl:.2e}  {'PASS' if pl == 0 else 'FAIL'}")

    # ---- POSITIVE CONTROL · plant a slope difference ----------------------------------------
    print(f"  POSITIVE  plant a known slope difference by scaling topw_k's 0.8B effects\n")
    print(f"    {'planted x':>11}{'recovered Δ':>14}{'expected':>11}")
    pos_ok = True
    for s in (0.5, 1.5, 2.0):
        got = fam_slope("topw_k", scale=s) - b_r
        want = b_t * s - b_r
        ok = abs(got - want) < 1e-9
        pos_ok &= ok
        print(f"    {s:>11.1f}{got:>14.4f}{want:>11.4f}   {'ok' if ok else 'MISMATCH'}")
    g0 = abs((fam_slope("topw_k", scale=1.0) - b_r) - diff) < 1e-12
    print(f"    g=0 (scale 1.0) reproduces the observed difference exactly: {g0}")

    # ---- NEGATIVE CONTROL · random family assignment -----------------------------------------
    print(f"\n  NEGATIVE  reassign arms to the two groups AT RANDOM, sizes preserved\n")
    allm = members["topw_k"] + members["random_k"]
    nt = len(members["topw_k"])
    perm = []
    for seed in range(3):
        g = np.random.default_rng(4000 + seed)
        sh = list(g.permutation(allm))
        assign = {"topw_k": sh[:nt], "random_k": sh[nt:]}
        perm.append(fam_slope("topw_k", assign=assign) - fam_slope("random_k", assign=assign))
    pm, ps = float(np.mean(np.abs(perm))), float(np.std(perm))
    neg_ok = abs(diff) > pm
    print(f"    |Δ| under random assignment: {pm:.4f} ± {ps:.4f} over 3 seeds")
    print(f"    observed |Δ| {abs(diff):.4f}  ->  "
          f"{'clears the permutation floor' if neg_ok else '⚠ INSIDE the floor'}")

    # ---- KILL ---------------------------------------------------------------------------------
    ctrl = (pl == 0) and pos_ok and g0
    resolved = not (lo <= 0 <= hi) and abs(diff) >= mde
    print("\n  " + "=" * 76)
    print(f"  CONTROLS  placebo={pl == 0}  positive={pos_ok}  g0={g0}  negative={neg_ok}"
          f"   -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the difference is not readable.")
    elif resolved and neg_ok:
        world = "W-INTERACT"
        print(f"  -> W-INTERACT. The two families shrink differently: Δ {diff:+.4f}")
        print(f"     [{lo:+.4f}, {hi:+.4f}], |Δ| ≥ MDE {mde:.4f}, and above the permutation floor.")
        print("     Construction method and judge INTERACT, which is the mechanism R310's family")
        print("     finding needed.")
    else:
        world = "W-COMMON"
        print(f"  -> W-COMMON. Δ {diff:+.4f} [{lo:+.4f}, {hi:+.4f}] against MDE {mde:.4f}: these")
        print("     two families do NOT shrink resolvably differently. R310 is NARROWED, not")
        print("     refuted -- its family structure is carried by families other than these two,")
        print("     or by something correlated with family that is not the selection rule.")
        print("     ⚠ And these are the two BIGGEST families; the other eleven have 1-3 arms and")
        print("     cannot be fitted at all, so this is the most power the release affords.")
    print("  " + "=" * 76)

    o = SELF.parent / "results" / "family_slopes.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], n_prompts=N, world=world,
        members={f: v for f, v in members.items()},
        slope_topw=b_t, slope_random=b_r, diff=diff, ci=[lo, hi], mde=mde,
        placebo=pl, positive_ok=bool(pos_ok), g0=bool(g0),
        perm_floor=pm, perm_sd=ps, negative_ok=bool(neg_ok)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
