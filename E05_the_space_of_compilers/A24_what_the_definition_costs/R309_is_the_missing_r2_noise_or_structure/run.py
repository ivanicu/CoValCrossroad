"""R309 — is the R² that R301 could not reach MY NOISE, or something the judge is doing?

R301 returned UNRESOLVED: β = +0.434 [0.395, 0.472] and R² = 0.482 (worst leave-one-family-out),
just under the 0.50 the pre-registration required for W-SHRINK and far above the 0.25 for
W-REORDER. An UNRESOLVED is only worth keeping if the next round can move it, and the cheapest
question that could is: **how much R² was ever available?**

A regression of one noisy measurement on another is capped. If `eff_2B` is measured with error,
no amount of true linearity produces R² = 1: the ceiling is the product of the two reliabilities,
`ρx · ρy`. So `R² = 0.48` is either far from its ceiling (something real is unexplained) or close
to it (the shortfall is my own resolution and W-SHRINK stands).

⚠ THE ARITHMETIC WAS DONE FIRST, AND IT KILLED THE HYPOTHESIS I WAS ABOUT TO SPEND A ROUND ON.
From R301's own artifact: mean SE = 0.0049 (2B) and 0.0040 (0.8B) against between-arm variances of
0.00174 and 0.00054, so ρx ≈ 0.99, ρy ≈ 0.97, and the ceiling is ≈ 0.96. The observed R² is
therefore ~64% of what was achievable, not ~100%. **The missing R² is not measurement error.**
That is the attack ladder's second rung — derive it before measuring it — and it turns this round
from "confirm the shrink" into "characterise what the judge adds", which is a different question
with a different answer space.

ESTIMAND      `ratio = R²_obs / (ρx · ρy)`: the share of the ACHIEVABLE association that a single
              linear shrink explains. Plus the attenuation-corrected slope `β / ρx`.
IDENTIFICATION exact given the per-arm standard errors, which R301's cluster bootstrap already
              produced; `ρ = 1 − mean(SE²)/Var(observed)` is the standard reliability estimator and
              is a DERIVATION, labelled as one, not a measurement.
SCOPE         population the 39 arms sharing R301's reference population · instrument Qwen3.5-2B
              and 0.8B · baseline `random_k4_s0` · regime clause ① effects, A2·annotator.
WORLDS        W-SHRINK      ratio ≈ 1 -> the judges are one instrument at two precisions, the
                            ordering is intact, and the definition is judge-bound only through
                            resolution.
              W-REORDER     ratio ≈ 0 -> they measure different things.
              W-STRUCTURED  ratio in between -> the judge does something SYSTEMATIC that one slope
                            cannot express. This world did not exist in R301's design, which is
                            why R301 could only return UNRESOLVED: its two worlds did not span the
                            outcome space, and an outcome that fits no world is a design defect,
                            not a fact about the object.
KILL          conditional on the controls:
                ratio >= 0.85 -> W-SHRINK · ratio <= 0.50 -> W-REORDER · else W-STRUCTURED,
                and W-STRUCTURED obliges naming WHAT the structure is, or it is just a label.
POSITIVE CTRL synthesise y = βx + measurement noise at the OBSERVED per-arm SEs, with perfect
              underlying linearity. The estimator must return ratio ≈ 1. If it does not, the
              correction is wrong and no number below reads. Fails at g=0 by construction: the
              same estimator on a genuinely reordered y must NOT return 1.
NEGATIVE CTRL synthesise a real partial reordering (permute a fraction of the true effects between
              judges) and sweep the fraction 0 -> 1. The ratio must fall monotonically; a
              correction that is flat under increasing reordering is measuring nothing.
NOISE FLOOR   the reliabilities themselves ARE the noise floor, computed rather than assumed.
MULTIPLICITY  one estimand, two controls, one sweep. No grid.
SEEDS         3 seeds for every synthetic arm; the spread is reported, never averaged away.
ARTIFACT      results/reliability_ceiling.json with source hash.
IMPOSSIBLE    whether the structure, if any, generalises to a third judge — needs a third model,
              which is a drop-in here (the prompt template is byte-identical) and not attempted.
"""
import hashlib, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
ZEFF = 1.959964 + 0.841621
SRC = (SELF.parent.parent / "R301_is_the_judge_a_shrink_or_a_reorder"
       / "results" / "judge_slope.json")


def fit(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    if xc @ xc <= 0 or yc @ yc <= 0:
        return float("nan"), float("nan")
    return float(xc @ yc / (xc @ xc)), float((xc @ yc) ** 2 / ((xc @ xc) * (yc @ yc)))


def reliability(eff, se):
    """ρ = 1 − mean(SE²)/Var(observed). A DERIVATION from the classical measurement model, not a
    measurement: it assumes the SEs are correct and the errors independent of the true values."""
    v = float(np.var(eff, ddof=1))
    return max(0.0, min(1.0, 1.0 - float(np.mean(se ** 2)) / v)), v


def main():
    if not SRC.exists():
        print(f"  UNRUNNABLE: {SRC.relative_to(ROOT)} absent."); return 2
    d = json.loads(SRC.read_text())
    fit_arms = d["fit_arms"]
    r = d["rows"]
    e2 = np.array([r[a]["c1_2"][0] for a in fit_arms])
    e8 = np.array([r[a]["c1_8"][0] for a in fit_arms])
    s2 = np.array([r[a]["mde1_2"] / ZEFF for a in fit_arms])
    s8 = np.array([r[a]["mde1_8"] / ZEFF for a in fit_arms])
    n = len(fit_arms)
    print(f"  {n} arms, effects and standard errors taken from R301's own artifact\n")

    rx, vx = reliability(e2, s2)
    ry, vy = reliability(e8, s8)
    ceiling = rx * ry
    beta, r2 = fit(e2, e8)
    ratio = r2 / ceiling if ceiling > 0 else float("nan")
    beta_corr = beta / rx if rx > 0 else float("nan")

    print(f"  {'':22}{'2B':>12}{'0.8B':>12}")
    print(f"  {'mean SE':22}{s2.mean():>12.5f}{s8.mean():>12.5f}")
    print(f"  {'Var(effects)':22}{vx:>12.5f}{vy:>12.5f}")
    print(f"  {'reliability ρ':22}{rx:>12.4f}{ry:>12.4f}")
    print(f"\n  R² CEILING = ρx·ρy = {ceiling:.4f}   observed R² = {r2:.4f}   "
          f"ratio = {ratio:.4f}")
    print(f"  slope {beta:+.4f}   attenuation-corrected {beta_corr:+.4f}   "
          f"(correction is {abs(beta_corr-beta):.4f}, i.e. negligible when ρx≈1)")

    # ---- POSITIVE CONTROL · perfect linearity + the observed noise must return ratio ≈ 1 --------
    rng = np.random.default_rng(31337)
    pos = []
    for seed in range(3):
        g = np.random.default_rng(1000 + seed)
        true_x = e2.copy()
        true_y = beta * true_x
        ox = true_x + g.normal(0, s2)
        oy = true_y + g.normal(0, s8)
        rxp, _ = reliability(ox, s2)
        ryp, _ = reliability(oy, s8)
        _, r2p = fit(ox, oy)
        pos.append(r2p / (rxp * ryp) if rxp * ryp > 0 else float("nan"))
    pos_m, pos_sd = float(np.mean(pos)), float(np.std(pos))
    pos_ok = abs(pos_m - 1.0) < 0.15
    print(f"\n  POSITIVE CTRL  perfect linearity + observed noise -> ratio "
          f"{pos_m:.3f} ± {pos_sd:.3f} over 3 seeds   "
          f"{'PASS' if pos_ok else 'FAIL — the correction is wrong; nothing above reads'}")

    # ---- NEGATIVE CONTROL · sweep a real reordering; the ratio must FALL --------------------
    print(f"\n  NEGATIVE CTRL  sweep a genuine reordering. A correction that does not fall as the")
    print(f"                 reordering grows is measuring nothing.\n")
    print(f"    {'shuffled':>10}{'ratio (mean of 3 seeds)':>28}")
    sweep = []
    for frac in (0.0, 0.25, 0.50, 0.75, 1.0):
        vals = []
        for seed in range(3):
            g = np.random.default_rng(2000 + seed)
            ty = beta * e2.copy()
            k = int(round(frac * n))
            if k > 1:
                idx = g.choice(n, k, replace=False)
                ty[idx] = ty[g.permutation(idx)]
            ox = e2 + g.normal(0, s2)
            oy = ty + g.normal(0, s8)
            rxs, _ = reliability(ox, s2)
            rys, _ = reliability(oy, s8)
            _, r2s = fit(ox, oy)
            vals.append(r2s / (rxs * rys) if rxs * rys > 0 else float("nan"))
        m = float(np.mean(vals)); sweep.append((frac, m, float(np.std(vals))))
        print(f"    {frac:>10.0%}{m:>28.3f}")
    monotone = all(sweep[i][1] >= sweep[i + 1][1] - 0.10 for i in range(len(sweep) - 1))
    neg_ok = monotone and sweep[-1][1] < 0.5
    print(f"    -> falls with reordering: {monotone} · reaches <0.5 when fully shuffled: "
          f"{sweep[-1][1] < 0.5}   {'PASS' if neg_ok else 'FAIL'}")

    # ---- KILL, conditional -----------------------------------------------------------------
    print("\n  " + "=" * 76)
    if not (pos_ok and neg_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the ratio is not readable and this is NOT")
        print("     a verdict about the judges.")
    elif ratio >= 0.85:
        world = "W-SHRINK"
        print(f"  -> W-SHRINK. {ratio:.0%} of the achievable association is a single linear")
        print("     shrink. The judges are one instrument at two precisions.")
    elif ratio <= 0.50:
        world = "W-REORDER"
        print(f"  -> W-REORDER. Only {ratio:.0%} of the achievable association survives; the")
        print("     judges do not order the arms the same way.")
    else:
        world = "W-STRUCTURED"
        print(f"  -> W-STRUCTURED. {ratio:.0%} of the achievable association is a linear shrink,")
        print(f"     and the ceiling is {ceiling:.2f}, so the missing {1-ratio:.0%} is NOT my")
        print("     measurement error -- the reliabilities are ~0.97-0.99. The smaller judge is")
        print("     doing something SYSTEMATIC that one slope cannot express.")
        print("     ⚠ This world did not exist in R301's design. R301 could only return")
        print("     UNRESOLVED because its two worlds did not span the outcome space, and an")
        print("     outcome that fits no world is a defect in the design, not a fact about the")
        print("     object. Naming the structure is the next round's job; this one establishes")
        print("     only that there IS one and that it is not noise.")
    print("  " + "=" * 76)

    o = SELF.parent / "results" / "reliability_ceiling.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], n_arms=n, world=world,
        reliability_2b=rx, reliability_08b=ry, r2_ceiling=ceiling, r2_observed=r2,
        ratio=ratio, beta=beta, beta_attenuation_corrected=beta_corr,
        positive_control=dict(mean=pos_m, sd=pos_sd, ok=bool(pos_ok)),
        negative_control=dict(sweep=sweep, monotone=bool(monotone), ok=bool(neg_ok))), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
