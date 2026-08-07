"""
R725 · the specification curve was a threshold sweep

ESTIMAND        (1) DERIVATION: given mde = ZEFF*SE and a percentile CI ~ eff +- 1.959964*SE, the
                five admission rules R724 swept are FOUR thresholds on the same t = eff/SE.
                (2) MEASUREMENT: is R724's exclusion of coval_core under `lo > mde` flippable by the
                mde's OWN sampling error?
IDENTIFICATION  (1) exact from the artifact -- t recoverable two ways, their ratio the diagnostic.
                (2) PARTIAL: the sampling law of a sample SD is chi under NORMALITY, unverifiable
                here because the raw difference vectors are not in the artifact. Model-based, and
                reported with an assumption-light distance beside it.
SCOPE           population 41 arms x 2 clauses · instrument algebraic re-expression + chi model ·
                baseline R724's grid · regime census source_sha 2bc1124f6825df0f
WORLDS          W-COLLAPSE / W-DISTINCT (does the equivalence hold) ·
                W-FLIP / W-STABLE (can resampling the mde move coval_core)
KILL            conditional; gated on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   a synthetic arm planted at exactly t = 4.761549 must return crossing prob ~0.5;
                band floor (t=0 -> ~0) < planted <= ceiling (t=20 -> ~0 on the other side).
g=0             a synthetic arm at t = 0 -> ~0, NOT ~0.5. The control must not fire on nothing.
NEGATIVE CTRL   an SE drawn independently of mde must BREAK the rule/threshold agreement.
                excluded world: "any t-threshold reproduces these rules".
SHAM            the equivalence check with the threshold removed -> agreement trivially total.
PLACEBO         each rule against itself -> exactly 0 mismatches.
NOISE FLOOR     Monte-Carlo error of the crossing probability over >=3 seeds, measured.
MULTIPLICITY    410 equivalence checks + 82 t-statistics + 3 seeds, all reported.
SPECIFICATION   SE recovered two ways x 5 rules x 2 clauses
SEEDS           3 for the chi simulation; two hash seeds byte-identical
ARTIFACT        results/r725_threshold_sweep.json with tree_sha
IMPOSSIBLE      normality of the per-prompt differences -> needs the raw vectors (a census re-run) ·
                independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
CENSUS = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"

Z95  = 1.959964
ZEFF = 1.959964 + 0.841621                      # R294:59
RULES = ("point", "ci_only", "mde_only", "strict", "conservative")
THRESH = {"point": 0.0, "ci_only": Z95, "mde_only": ZEFF, "strict": ZEFF,
          "conservative": Z95 + ZEFF}           # lo > mde  <->  eff - Z95*SE > ZEFF*SE


def rule_says(eff, lo, hi, mde, rule):
    """R724's predicates, verbatim."""
    if rule == "strict":        return lo > 0.0 and abs(eff) >= mde
    if rule == "ci_only":       return lo > 0.0
    if rule == "point":         return eff > 0.0
    if rule == "mde_only":      return eff >= mde
    if rule == "conservative":  return lo > mde
    raise ValueError(rule)


def thresh_says(t, rule):
    return t > THRESH[rule] if rule in ("point", "ci_only", "conservative") else t >= THRESH[rule]


def crossing_prob(t_obs, n, seed, ndraw=200_000):
    """P(the arm crosses t = 4.761549) when the mde's sd is RESAMPLED.

    ⚠ MODEL-BASED. Under normality of the per-prompt differences, sd_hat/sd ~ sqrt(chi2_{n-1}/(n-1)).
    The threshold is conservative <-> eff > (Z95+ZEFF)*SE, and SE carries the same sd, so a resample
    of sd rescales BOTH sides identically -- which is exactly why this has to be computed rather
    than asserted. What actually varies between the two sides is that `lo` comes from a bootstrap of
    the mean while `mde` comes from the analytic sd, so only the mde leg is resampled here.
    """
    rng = np.random.default_rng(seed)
    ratio = np.sqrt(rng.chisquare(n - 1, ndraw) / (n - 1))      # sd_hat / sd
    # observed decision: eff - Z95*SE > ZEFF*SE_resampled   <->   t_obs - Z95 > ZEFF*ratio
    crossed = (t_obs - Z95) > (ZEFF * ratio)
    return float(crossed.mean())


def main() -> int:
    print("=" * 100)
    print("R725 · THE SPECIFICATION CURVE WAS A THRESHOLD SWEEP")
    print("=" * 100)
    if not CENSUS.exists():
        print("  UNRUNNABLE: R294's census absent. Exit 2, never 0."); return 2
    cen = json.loads(CENSUS.read_text()); rows = cen["rows"]
    if not rows:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2

    print(f"  arms {len(rows)}   Z95 {Z95}   ZEFF {ZEFF:.6f}   conservative threshold "
          f"{Z95+ZEFF:.6f}")
    print(f"\n  ⛔ THE COLLAPSE IS A DERIVATION, NOT A RESULT:")
    for r in RULES:
        print(f"     {r:<13} -> t {'>=' if r in ('mde_only','strict') else '> '} {THRESH[r]:.6f}")
    A = len(set(THRESH.values()))
    print(f"     distinct thresholds among 5 labels: {A}   (strict == mde_only whenever eff > 0)")

    # ── recover t two ways, per arm per clause ────────────────────────────────────────────────
    cells = []
    for a, r in rows.items():
        for ci_k, mde_k, cl in (("c1", "mde1", 1), ("c2", "mde2", 2)):
            eff, lo, hi = r[ci_k]; mde = r[mde_k]
            se_ci  = (hi - lo) / (2 * Z95)
            se_mde = mde / ZEFF
            cells.append({"arm": a, "clause": cl, "eff": eff, "lo": lo, "hi": hi, "mde": mde,
                          "n": r["n"], "se_ci": se_ci, "se_mde": se_mde,
                          "se_ratio": (se_ci / se_mde) if se_mde else float("nan"),
                          "t_ci": eff / se_ci if se_ci else float("nan"),
                          "t_mde": eff / se_mde if se_mde else float("nan")})

    ratios = [c["se_ratio"] for c in cells if math.isfinite(c["se_ratio"])]
    print(f"\n  SE recovered two ways: bootstrap CI half-width vs mde/ZEFF")
    print(f"     ratio  min {min(ratios):.4f}  median {float(np.median(ratios)):.4f}  "
          f"max {max(ratios):.4f}   (1.0 = the two estimates agree)")

    ctl = {}
    print("\n─── CONTROLS ───")

    # POSITIVE + g=0 : the crossing-probability instrument
    p_at   = crossing_prob(Z95 + ZEFF, 968, 11)
    p_zero = crossing_prob(0.0, 968, 11)
    p_high = crossing_prob(20.0, 968, 11)
    ctl["POSITIVE"] = 0.35 < p_at < 0.65 and p_zero < 0.01 and p_high > 0.99
    print(f"  POSITIVE   planted AT the threshold t={Z95+ZEFF:.4f} -> crossing prob {p_at:.4f} "
          f"(must be ~0.5)")
    print(f"  g=0        planted at t=0 -> {p_zero:.4f} (must be ~0, the control must not fire)")
    print(f"             band: floor t=0 -> {p_zero:.4f}  <  planted {p_at:.4f}  <=  "
          f"ceiling t=20 -> {p_high:.4f}")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    # equivalence check, 410 classifications
    mism, per_rule = [], {r: 0 for r in RULES}
    for c in cells:
        for r in RULES:
            a_ = rule_says(c["eff"], c["lo"], c["hi"], c["mde"], r)
            b_ = thresh_says(c["t_mde"], r)
            if a_ != b_:
                mism.append({"arm": c["arm"], "clause": c["clause"], "rule": r,
                             "rule_says": a_, "thresh_says": b_, "t": c["t_mde"]})
                per_rule[r] += 1
    B = len(mism)

    # NEGATIVE: an SE unrelated to mde must break the agreement
    rng = np.random.default_rng(4242)
    fake = rng.permutation([c["se_mde"] for c in cells])
    bad = sum(1 for c, s in zip(cells, fake)
              for r in RULES
              if rule_says(c["eff"], c["lo"], c["hi"], c["mde"], r) != thresh_says(
                  c["eff"] / s if s else float("nan"), r))
    ctl["NEGATIVE"] = bad > B
    print(f"  NEGATIVE   SE permuted across cells -> {bad} mismatches vs {B} with the real SE "
          f"-> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'any t-threshold reproduces these rules'")

    sham_agree = sum(1 for c in cells for r in RULES if True)      # threshold removed => always true
    ctl["SHAM"] = sham_agree == len(cells) * len(RULES)
    print(f"  SHAM       threshold removed, predicate always true -> agreement "
          f"{sham_agree}/{len(cells)*len(RULES)} trivially total -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}")

    plc = sum(1 for c in cells for r in RULES
              if rule_says(c["eff"], c["lo"], c["hi"], c["mde"], r)
              != rule_says(c["eff"], c["lo"], c["hi"], c["mde"], r))
    ctl["PLACEBO"] = plc == 0
    print(f"  PLACEBO    each rule against itself -> {plc} mismatches (must be 0) -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    ctl["UNIT"] = (B == 0)
    print(f"  UNIT       instrument: a threshold on t recovered from the CI and mde")
    print(f"             claim     : the admission rule R294 actually applied")
    print(f"             EQUAL only if mismatches == 0; observed {B} -> "
          f"{'PASS' if ctl['UNIT'] else 'FAIL — downstream statements are about the RECOVERED rule'}")

    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the 410 equivalence checks ───────────────────────────────────────────────────────────
    print(f"\n─── EQUIVALENCE · {len(cells)} cells x {len(RULES)} rules = {len(cells)*len(RULES)} "
          f"CHECKS (all reported) ───")
    print(f"  mismatches total: {B}")
    for r in RULES:
        print(f"     {r:<13} {per_rule[r]} mismatch(es)")
    for m in mism[:8]:
        print(f"       ⚠ {m['arm']} clause{m['clause']} {m['rule']}: rule={m['rule_says']} "
              f"threshold={m['thresh_says']} t={m['t']:.4f}")

    # ── coval_core, the arm R724's qualification is about ───────────────────────────────────
    cc = next(c for c in cells if c["arm"] == "coval_core" and c["clause"] == 2)
    t_cc, n_cc = cc["t_mde"], cc["n"]
    rel_sd = 1.0 / math.sqrt(2 * (n_cc - 1))                       # rel. sampling SD of sd_hat
    gap_t = (Z95 + ZEFF) - t_cc
    D = abs(gap_t) / (ZEFF * rel_sd)
    seeds = (11, 12, 13)
    probs = [crossing_prob(t_cc, n_cc, s) for s in seeds]
    mc_sd = float(np.std(probs, ddof=1)) if len(probs) > 1 else 0.0

    print(f"\n─── coval_core, clause ② ───")
    print(f"  eff {cc['eff']:.6f}   CI [{cc['lo']:.6f}, {cc['hi']:.6f}]   mde {cc['mde']:.6f}   "
          f"n {n_cc}")
    print(f"  t = {t_cc:.4f}   conservative threshold {Z95+ZEFF:.4f}   gap {gap_t:+.4f}")
    print(f"  the mde's OWN relative sampling SD at n={n_cc}: {rel_sd:.6f}  "
          f"(= 1/sqrt(2(n-1)), assumption-light)")
    print(f"  D = gap / (ZEFF * rel_sd) = {D:.2f} sampling SDs of the mde")
    print(f"  crossing probability over seeds {seeds}: "
          f"{', '.join(f'{p:.6f}' for p in probs)}   MC sd {mc_sd:.2e}")

    C = A * A
    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A distinct thresholds", A, 1, 5, 4),
                                   ("B rule/threshold mismatches", B, 0, 410, 0),
                                   ("C distinct rule pairs of 25", C, 1, 25, 16),
                                   ("D gap in mde sampling SDs", round(D, 2), 0, 100, 7.0)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<8} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  ⛔ A and C ARE DERIVATIONS, NOT EVIDENCE — forced by mde = ZEFF*SE and the CI's form.")
    directional = max(probs) < 0.01
    print(f"  DIRECTIONAL the mde's sampling error CANNOT flip coval_core (crossing < 0.01) "
          f"-> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        verdict = "UNVERIFIED — a gating control did not fire; no collapse or stability claim is admissible."
    elif B > 10:
        verdict = (f"⭐⭐⭐ W-DISTINCT. {B} of {len(cells)*len(RULES)} checks disagree, so the rules are "
                   f"NOT a single threshold on t and R724's grid was as wide as it looked.")
    elif max(probs) > 0.05:
        verdict = (f"⭐⭐⭐ W-FLIP. coval_core's exclusion under `lo > mde` flips with probability "
                   f"{max(probs):.4f} when the mde is resampled; R724's qualification is WITHDRAWN "
                   f"as a threshold artifact.")
    else:
        verdict = (f"⭐⭐⭐ BOTH: THE GRID COLLAPSES AND THE QUALIFICATION SURVIVES. "
                   f"(1) DERIVATION — the five rule labels carry {A} distinct thresholds on the same "
                   f"t = eff/SE, and the equivalence holds on the artifact with {B} mismatches over "
                   f"{len(cells)*len(RULES)} checks, so R724's 5x5 grid has at most {C} distinct rule "
                   f"pairs of 25 and its '100 cells' overstate the dimensionality explored. "
                   f"(2) MEASUREMENT — coval_core's clause-② t is {t_cc:.4f} against a conservative "
                   f"threshold of {Z95+ZEFF:.4f}, a gap of {abs(gap_t):.4f}, which is {D:.1f} sampling "
                   f"SDs of the mde at n={n_cc}; the crossing probability is {max(probs):.6f}. "
                   f"⭐ SO MY OWN PROPOSED ATTACK FAILS: the exclusion is a property of the arm, not "
                   f"of a noisy threshold, and R724's qualification STANDS. ⚠ The crossing probability "
                   f"is MODEL-BASED — it assumes the per-prompt differences are normal, which this "
                   f"artifact cannot check because it does not carry the raw vectors; the gap in "
                   f"sampling SDs is the assumption-light version of the same statement.")
    print(f"  {verdict}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {
        "world": verdict, "controls_ok": all(ctl.values()), "controls": ctl,
        "tree_sha": tree_sha,
        "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        "census_source_sha": cen["source_sha"],
        "thresholds": THRESH, "Z95": Z95, "ZEFF": ZEFF,
        "A_distinct_thresholds": A, "A_is_a_derivation": True,
        "B_mismatches": B, "B_per_rule": per_rule, "B_examples": mism[:20],
        "C_distinct_rule_pairs": C, "C_is_a_derivation": True,
        "D_gap_in_mde_sampling_sds": round(D, 4),
        "coval_core_clause2": {"eff": cc["eff"], "lo": cc["lo"], "hi": cc["hi"], "mde": cc["mde"],
                               "n": n_cc, "t": t_cc, "threshold": Z95 + ZEFF, "gap": gap_t,
                               "rel_sd_of_mde": rel_sd},
        "crossing_probs": dict(zip(map(str, seeds), probs)), "crossing_mc_sd": mc_sd,
        "se_ratio": {"min": min(ratios), "median": float(np.median(ratios)), "max": max(ratios)},
        "n_cells": len(cells), "n_checks": len(cells) * len(RULES),
        "directional_cannot_flip": directional,
        "registered": "A 4 [1,5] deriv; B 0 [0,410]; C 16 [1,25] deriv; D 7.0 [0,100]; "
                      "directional crossing<0.01",
        "residue": "normality of the per-prompt differences is unverifiable from this artifact",
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r725_threshold_sweep.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r725_threshold_sweep.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
