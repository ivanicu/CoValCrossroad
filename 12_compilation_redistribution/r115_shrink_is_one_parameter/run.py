"""r115 -- claim 7 is not a correlation over 7 arm pairs. It is a one-parameter model, and 4 df.

A /frontier step on the programme's largest surviving claim, sampled because everything rests on it:
it is what retracted entry 23, the closing statement calls it "the largest thing here", and it was
verified only on the dataset that produced it and never DERIVED.

THE DERIVATION, which nobody had written
----------------------------------------
r113 reported that the observed coefficient tracks an arithmetic prediction `k*beta_sum` with
k = mean(d)/(mean(sum)-1), across 7 arm pairs at corr +0.9783, with no pair departing by more than
its own noise. Treated as an empirical regularity. It is not one. Write it out:

    beta_d = k*beta_sum
  <=>  beta_B - beta_A = k*(beta_B + beta_A)
  <=>  beta_B/beta_A   = (1+k)/(1-k)

  and with g = e_B - e_A, h = 1 - e_A - e_B, k = -g/h:
    (1+k)/(1-k) = (h-g)/(h+g) = (1-2*e_B)/(1-2*e_A) = (0.5 - e_B)/(0.5 - e_A)

  =>  beta_d = k*beta_sum  <=>  beta_a is PROPORTIONAL TO (0.5 - e_a)   for every arm a.

So the "arithmetic line" is exactly the statement that ONE parameter governs all arms:

    beta_a = lambda * (0.5 - e_a)

which is what a COMMON MULTIPLICATIVE SHRINK TOWARD CHANCE predicts: if a covariate multiplies every
arm's distance from chance by the same (1 - lambda*x), then e_a = 0.5 - (1-lambda*x)*(0.5 - e_a0), and
differentiating in x gives beta_a = lambda*(0.5 - e_a0) directly.

WHAT THIS CHANGES, AND IT CUTS BOTH WAYS
----------------------------------------
STRONGER: claim 7 becomes a theorem plus one fitted number, not a correlation. It names its own
assumption (a common shrink), it is testable on any dataset with two rules and a rater-level
covariate, and it needs no arm-pair sweep to state.

SMALLER, and this is a scope error in the published claim: the 7 arm pairs are NOT 7 independent
confirmations. Five arms give five level coefficients and five mean errors; every pair is a
difference and a sum of those same five numbers. Correlating linear combinations of five numbers
against other linear combinations of the same five numbers cannot yield seven degrees of freedom.
**The evidence is 5 arms and 4 df, and corr = +0.9783 over 7 pairs overstates its own base.**

CLAIM CARD
----------
Claim      r113 / CLOSING.md claim 7: regressing a paired difference of two rules' per-rater error on
           a rater-level covariate gives a coefficient set by the rules' accuracy gap. Supported by 7
           arm pairs, corr +0.9783, no pair beyond its own noise.
Estimand   lambda in beta_a = lambda*(0.5 - e_a), and the chi-square for its CONSTANCY across arms.
           A common shrink requires ONE lambda; the arithmetic line holds if and only if one fits.
Target
observed?  YES, entirely from r113's persisted levels -- which exist only because that round was
           written after a navigator's directive destroyed the same diagnostic by asking for a
           difference and not the levels.
Worlds     W-ONE-PARAMETER  a single lambda fits every arm. The line is a derivation, claim 7 is a
                            theorem with a named assumption, and its evidence is 4 df not 7 pairs.
           W-ARM-SPECIFIC   lambda differs by arm. Then the line is NOT a common shrink, it is a
                            coincidence over the particular arms r113 happened to build, and claim 7
                            loses the mechanism it is stated with while keeping its prediction.
Intervention
           none. Arithmetic on a committed artifact.
Nulls      (i) The constancy test is itself the null: chi-square on 4 df against a critical 9.49.
           (ii) POWER, reported rather than assumed: how much wider would the spread have to be, or
           how much tighter the errors, to refuse constancy? A test that cannot refuse is not a test.
           (iii) The naive spread WITHOUT errors is reported beside the test, because that is the
           number I nearly published as a refutation.

PRE-REGISTERED, before the chi-square was computed
--------------------------------------------------
chi-square > CHI_CRIT_4DF (9.49, the 0.05 point on 4 df, from the distribution and not chosen) ->
W-ARM-SPECIFIC and claim 7's mechanism is withdrawn. Otherwise W-ONE-PARAMETER and claim 7 is
restated as a theorem plus lambda, with its evidence corrected from 7 pairs to 4 df.

THE MISTAKE THIS ROUND ALMOST WAS
---------------------------------
My first pass computed lambda per arm, saw it span 0.2958 to 0.5089 -- a 72% spread on the smallest --
and read that as the model being refused. It has no error bar. With the levels' own standard errors
the same spread is chi-square 3.26 on 4 df, p = 0.52. A ratio quoted without its interval is the
step-size failure this programme retracted eleven claims to: a correct number, over-extended.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx.stamp import stamp  # noqa: E402

R113 = _ROOT / "12_compilation_redistribution/r113_accuracy_matched_arm/results/r113_accuracy_matched_arm.json"
ARMS = ("full", "core", "oracle", "rand4", "first4")
# The 0.05 point of chi-square on 4 df. From the distribution, not chosen after seeing anything.
CHI_CRIT_4DF = 9.4877
CHANCE = 0.5              # pairwise-discordance chance rate: two responses, one comparison


def chi2_sf_even(x: float, dof: int) -> float:
    """Survival function of chi-square for EVEN dof, in closed form. Exact, no scipy."""
    assert dof % 2 == 0
    return math.exp(-x / 2) * sum((x / 2) ** k / math.factorial(k) for k in range(dof // 2))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r115_shrink_is_one_parameter.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

    if not R113.exists():
        print(f"REFUSING: {R113} absent. Nothing-to-analyse exits 2, never 0.", file=sys.stderr)
        return 2
    o = json.loads(R113.read_text())
    me, lv = o["mean_error"], o["levels"]
    missing = [a for a in ARMS if a not in me or a not in lv]
    if missing:
        print(f"REFUSING: arms absent from the artifact: {missing}", file=sys.stderr)
        return 2

    dist = np.array([CHANCE - me[a] for a in ARMS])
    beta = np.array([lv[a]["beta"] for a in ARMS])
    sebs = np.array([lv[a]["se"] for a in ARMS])
    lam, slam = beta / dist, sebs / dist

    print(f"  {'arm':<8}{'mean e':>9}{'0.5-e':>9}{'beta':>10}{'se':>9}{'lambda':>10}{'se(lam)':>10}")
    for a, d_, b_, s_, l_, sl_ in zip(ARMS, dist, beta, sebs, lam, slam):
        print(f"  {a:<8}{me[a]:>9.5f}{d_:>9.5f}{b_:>+10.5f}{s_:>9.5f}{l_:>10.4f}{sl_:>10.4f}")

    w = 1.0 / slam ** 2
    lam_hat = float((w * lam).sum() / w.sum())
    se_hat = float(1.0 / math.sqrt(w.sum()))
    z = (lam - lam_hat) / slam
    chi2 = float((w * (lam - lam_hat) ** 2).sum())
    dof = len(ARMS) - 1
    p = chi2_sf_even(chi2, dof)

    naive_spread = float((lam.max() - lam.min()) / lam.min())
    print(f"\n  ONE shared lambda = {lam_hat:.4f} (se {se_hat:.4f});  chi-square for constancy "
          f"{chi2:.2f} on {dof} df, p = {p:.4f}, critical {CHI_CRIT_4DF}")
    print(f"  per-arm z: " + "  ".join(f"{a}={v:+.2f}" for a, v in zip(ARMS, z))
          + f"   max |z| = {abs(z).max():.2f}")
    print(f"  the SAME spread quoted without errors: {naive_spread:.1%} of the smallest lambda "
          f"-- which is what a ratio without an interval looks like")

    # power, reported rather than assumed
    widen = math.sqrt(CHI_CRIT_4DF / chi2) if chi2 > 0 else float("inf")
    tighten = math.sqrt(chi2 / CHI_CRIT_4DF) if chi2 > 0 else 0.0
    print(f"  POWER: to refuse constancy the spread must be {widen:.2f}x wider, or the errors "
          f"{tighten:.2f}x tighter. A test that cannot refuse is not a test, so this is stated.")

    # the equivalence, verified numerically rather than only derived
    ref = ARMS.index("full")
    eq = []
    for i, a in enumerate(ARMS):
        if i == ref:
            continue
        k = (me[a] - me["full"]) / ((me[a] + me["full"]) - 1.0)
        implied = (1 + k) / (1 - k)
        direct = dist[i] / dist[ref]
        eq.append(abs(implied - direct))
    print(f"\n  EQUIVALENCE CHECK, beta_d = k*beta_sum  <=>  beta_a proportional to (0.5-e_a):")
    print(f"    max |(1+k)/(1-k) - (0.5-e_B)/(0.5-e_A)| over the four pairs = {max(eq):.2e}")
    print(f"    -- identical to machine precision, so the two statements are ONE statement")

    n_arms, n_pairs = len(ARMS), len(o.get("pairs", {}))
    print(f"\n  DEGREES OF FREEDOM: the artifact reports {n_pairs} arm pairs. Every pair is a "
          f"difference and a sum of the SAME {n_arms} level coefficients and {n_arms} mean errors, so "
          f"the constancy test carries {dof} df -- not {n_pairs}.")

    world = "W-ARM-SPECIFIC" if chi2 > CHI_CRIT_4DF else "W-ONE-PARAMETER"
    conclusion = (
        f"beta_d = k*beta_sum is algebraically equivalent to beta_a being proportional to "
        f"(0.5 - e_a), verified to {max(eq):.0e}, which is exactly what a common multiplicative "
        f"shrink toward chance predicts with a single lambda. Across {n_arms} arms one shared lambda "
        f"= {lam_hat:.4f} (se {se_hat:.4f}) fits with chi-square {chi2:.2f} on {dof} df, p = {p:.4f} "
        f"against a pre-registered critical value of {CHI_CRIT_4DF}; largest per-arm departure is "
        f"|z| = {abs(z).max():.2f} at {ARMS[int(abs(z).argmax())]}. Refusing constancy would need the "
        f"spread {widen:.2f}x wider. The same lambdas quoted WITHOUT their errors span "
        f"{naive_spread:.0%} of the smallest, which is the form in which I first mistook them for a "
        f"refutation. WORLD: {world}. "
        + (f"Claim 7 is not a correlation over {n_pairs} arm pairs -- it is a one-parameter model, and "
           f"its evidence is {dof} df. Restate it as a theorem plus lambda: the coefficient on a "
           f"paired difference is set by the arms' distance from chance, with one shrink parameter "
           f"governing every arm. Stronger, because it names its assumption and transfers to any "
           f"dataset with two rules and a rater-level covariate; smaller, because corr over "
           f"{n_pairs} pairs overstates a {dof}-df base."
           if world == "W-ONE-PARAMETER" else
           f"lambda is not constant across arms, so the line is not a common shrink and claim 7 keeps "
           f"its prediction while losing the mechanism it is stated with."))
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    out = {"arms": list(ARMS), "chance": CHANCE,
           "mean_error": {a: me[a] for a in ARMS},
           "levels": {a: {"beta": lv[a]["beta"], "se": lv[a]["se"]} for a in ARMS},
           "distance_from_chance": dist.tolist(),
           "lambda": lam.tolist(), "se_lambda": slam.tolist(),
           "lambda_shared": lam_hat, "se_lambda_shared": se_hat,
           "z_per_arm": dict(zip(ARMS, z.tolist())), "max_abs_z": float(abs(z).max()),
           "chi2": chi2, "dof": dof, "p": p, "chi_crit_4df": CHI_CRIT_4DF,
           "naive_spread_no_errors": naive_spread,
           "power_spread_multiple_to_refuse": widen,
           "equivalence_max_abs_error": float(max(eq)),
           "n_pairs_reported_by_r113": n_pairs, "effective_df": dof,
           "world": world, "conclusion": conclusion, **stamp(__file__)}
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
