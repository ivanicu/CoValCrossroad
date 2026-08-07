"""R312 — is the shrink a property of the ARM or of the RULE?

R311: `topw_k` slope +0.75, `random_k` slope −0.14, difference +0.889 [+0.594, +1.088] against an
MDE of 0.356, and correcting for the two families' different reliabilities made the gap LARGER
(1.019), not smaller. So construction method and judge interact.

But "rule" may be a proxy. The reading that survives R310 and R311 together is that the smaller
judge keeps the ordering of arms that carry real signal and loses it for arms that do not — and
`topw_k` carries more signal than `random_k` by construction, since it selects on the rubric's own
importance weights. If so the unit is the ARM, not the RULE, and `family` is standing in for
something an arm has.

R310 already killed the obvious version: effect MAGNITUDE explains nothing (adjusted R² −0.027,
dead flat). The version it did not test is PRECISION — an arm whose effect is measured tightly may
survive a weaker judge better than one of the same size measured loosely. That is a different
quantity from magnitude and it is not obviously correlated with the rule.

⛔ AND IT CARRIES A TRAP THAT HAS TO BE DESIGNED AGAINST, NOT CHECKED FOR AFTERWARDS.
The residual from the family fit has, by construction, a spread that grows with the arm's own
standard error: a noisier arm sits further from any line. So `|residual| ~ SE` is MECHANICAL and
would appear at full strength even if the judge did nothing at all. This is `realstat §4 · a
control validated by its own instrument's noise`, and the remedy is the same: **simulate the
mechanical relationship at the observed SEs and require the observed one to EXCEED it**, rather
than comparing to zero.

ESTIMAND      the correlation between an arm's precision (1/SE) and its shrink residual, measured
              AGAINST the mechanically-induced correlation rather than against zero; and whether
              rule membership adds anything once precision is in the model.
IDENTIFICATION partial. 39 arms and two correlated covariates cannot separate precision from rule
              if the rules differ in precision — which they do. So this round can KILL the
              precision story or leave it standing beside rule; it cannot award it the mechanism.
SCOPE         population the 39 arms of R301's fit · instrument 2B and 0.8B · baseline
              `random_k4_s0` · regime clause ① effects, A2·annotator.
WORLDS        W-ARM   precision predicts the shrink BEYOND the mechanical floor, and rule adds
                      nothing once precision is in -> the unit is the arm and R311's families were
                      a proxy.
              W-RULE  rule survives conditioning on precision -> the unit is the rule, and R311
                      stands as it is.
              W-BOTH  both survive -> they are separate contributions and this design cannot rank
                      them; say so rather than pick.
KILL          conditional on the controls, all pre-registered:
                observed |corr| <= mechanical floor            -> precision story DEAD (W-RULE)
                observed > floor AND rule partial R² < 0.05     -> W-ARM
                observed > floor AND rule partial R² >= 0.05    -> W-BOTH
POSITIVE CTRL plant a precision-dependent shrink and require recovery above the floor. Fails at
              g=0: with no plant, the estimator must land ON the mechanical floor, not above it.
NEGATIVE CTRL the mechanical floor itself, simulated at the observed SEs with the judge doing
              nothing beyond the fitted slope — this is the world the claim must beat.
NOISE FLOOR   the floor is the negative control, measured over 200 simulations, not assumed.
MULTIPLICITY  two covariates, one nested comparison. Reported together.
SEEDS         200 simulations for the floor; 3 seeds for each plant.
ARTIFACT      results/arm_or_rule.json with source hash.
IMPOSSIBLE    separating precision from rule when the rules differ in precision — that needs arms
              built by ONE rule spanning a wide precision range, which means generating arms
              rather than reusing the release's.
"""
import hashlib, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
ZEFF = 1.959964 + 0.841621
SRC = (SELF.parent.parent / "R301_is_the_judge_a_shrink_or_a_reorder"
       / "results" / "judge_slope.json")
NSIM = 200


def fit(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    if xc @ xc <= 0 or yc @ yc <= 0:
        return float("nan"), float("nan")
    return float(xc @ yc / (xc @ xc)), float((xc @ yc) ** 2 / ((xc @ xc) * (yc @ yc)))


def corr(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    den = math.sqrt(float(xc @ xc) * float(yc @ yc))
    return float(xc @ yc / den) if den > 0 else float("nan")


def main():
    if not SRC.exists():
        print(f"  UNRUNNABLE: {SRC.relative_to(ROOT)} absent."); return 2
    d = json.loads(SRC.read_text())
    arms = d["fit_arms"]; r = d["rows"]; n = len(arms)
    e2 = np.array([r[a]["c1_2"][0] for a in arms])
    e8 = np.array([r[a]["c1_8"][0] for a in arms])
    s2 = np.array([r[a]["mde1_2"] / ZEFF for a in arms])
    s8 = np.array([r[a]["mde1_8"] / ZEFF for a in arms])
    beta, _ = fit(e2, e8)
    resid = e8 - (beta * e2 + (e8.mean() - beta * e2.mean()))
    prec = 1.0 / s8                     # precision of the 0.8B measurement
    is_topw = np.array([1.0 if a.startswith("topw_k") and not a.endswith("_sham") else 0.0
                        for a in arms])
    print(f"  {n} arms · family slope {beta:+.4f} · residual sd {resid.std(ddof=1):.5f}\n")

    obs = corr(prec, np.abs(resid))
    print(f"  observed corr(precision, |residual|) = {obs:+.4f}")

    # ---- NEGATIVE CONTROL = THE MECHANICAL FLOOR, and it is the world the claim must beat -----
    floor = []
    for t in range(NSIM):
        g = np.random.default_rng(5000 + t)
        # the judge does NOTHING beyond the fitted slope; all scatter is measurement noise
        y = beta * e2 + g.normal(0, s8)
        b2, _ = fit(e2, y)
        rr = y - (b2 * e2 + (y.mean() - b2 * e2.mean()))
        floor.append(corr(prec, np.abs(rr)))
    fl_m, fl_sd = float(np.mean(floor)), float(np.std(floor))
    fl_lo, fl_hi = float(np.percentile(floor, 2.5)), float(np.percentile(floor, 97.5))
    print(f"  MECHANICAL FLOOR (judge does nothing, noise at the observed SEs):")
    print(f"    {fl_m:+.4f} ± {fl_sd:.4f}   95% of simulations in [{fl_lo:+.4f}, {fl_hi:+.4f}]")
    beats = obs < fl_lo or obs > fl_hi
    print(f"  -> observed is {'OUTSIDE' if beats else 'INSIDE'} the mechanical envelope"
          f"   {'(exceeds it)' if beats else '(explained by it)'}")

    # ---- POSITIVE CONTROL · plant a precision-dependent shrink --------------------------------
    print(f"\n  POSITIVE CTRL  plant a shrink that DEPENDS on precision; require it above the floor")
    pos = []
    for seed in range(3):
        g = np.random.default_rng(6000 + seed)
        w = (prec - prec.mean()) / prec.std()
        y = beta * e2 * (1 + 0.5 * w) + g.normal(0, s8)
        b2, _ = fit(e2, y)
        rr = y - (b2 * e2 + (y.mean() - b2 * e2.mean()))
        pos.append(corr(prec, np.abs(rr)))
    pos_m = float(np.mean(pos))
    pos_ok = pos_m < fl_lo or pos_m > fl_hi
    print(f"    planted -> {pos_m:+.4f}   {'PASS (clears the floor)' if pos_ok else 'FAIL'}")
    g0 = []
    for seed in range(3):
        g = np.random.default_rng(6500 + seed)
        y = beta * e2 + g.normal(0, s8)
        b2, _ = fit(e2, y)
        rr = y - (b2 * e2 + (y.mean() - b2 * e2.mean()))
        g0.append(corr(prec, np.abs(rr)))
    g0_m = float(np.mean(g0))
    g0_ok = fl_lo <= g0_m <= fl_hi
    print(f"    g=0 (nothing planted) -> {g0_m:+.4f}   "
          f"{'PASS (lands ON the floor)' if g0_ok else '⚠ fires with nothing planted'}")

    # ---- does RULE survive conditioning on precision? -----------------------------------------
    # partial R²: variance of resid explained by is_topw AFTER removing precision's linear part
    bp, _ = fit(prec, resid)
    resid_p = resid - (bp * prec + (resid.mean() - bp * prec.mean()))
    _, rule_partial = fit(is_topw, resid_p)
    _, prec_alone = fit(prec, resid)
    _, rule_alone = fit(is_topw, resid)
    print(f"\n  {'covariate':<34}{'R² alone':>10}{'R² after removing the other':>30}")
    print(f"    {'precision (1/SE_0.8B)':<32}{prec_alone:>10.4f}"
          f"{fit(prec, resid - (fit(is_topw, resid)[0] * is_topw))[1]:>30.4f}")
    print(f"    {'rule (topw_k vs rest)':<32}{rule_alone:>10.4f}{rule_partial:>30.4f}")

    # ---- KILL ----------------------------------------------------------------------------------
    print("\n  " + "=" * 76)
    ctrl = pos_ok and g0_ok
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; neither covariate is readable.")
    elif not beats:
        world = "W-RULE"
        print(f"  -> W-RULE. corr(precision, |residual|) = {obs:+.4f} sits INSIDE the mechanical")
        print(f"     envelope [{fl_lo:+.4f}, {fl_hi:+.4f}] that a judge doing NOTHING already")
        print("     produces. The precision story is dead: it would have looked like evidence and")
        print("     is an artifact of noisier arms sitting further from any line. R311 stands.")
    elif rule_partial < 0.05:
        world = "W-ARM"
        print(f"  -> W-ARM. Precision beats the mechanical floor and rule adds only "
              f"{rule_partial:.3f}")
        print("     once precision is removed. The unit is the ARM; R311's families were a proxy.")
    else:
        world = "W-BOTH"
        print(f"  -> W-BOTH. Precision clears the floor AND rule keeps {rule_partial:.3f} after")
        print("     conditioning on it. They are separate contributions and 39 arms whose rules")
        print("     DIFFER in precision cannot rank them. Saying which matters more would be")
        print("     picking, not measuring.")
    print("  " + "=" * 76)

    o = SELF.parent / "results" / "arm_or_rule.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], n_arms=n, world=world,
        observed_corr=obs, mechanical_floor=dict(mean=fl_m, sd=fl_sd, lo=fl_lo, hi=fl_hi,
                                                 n_sim=NSIM),
        beats_floor=bool(beats), precision_r2_alone=prec_alone, rule_r2_alone=rule_alone,
        rule_partial_r2=rule_partial, positive_control=pos_m, positive_ok=bool(pos_ok),
        g0=g0_m, g0_ok=bool(g0_ok)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
