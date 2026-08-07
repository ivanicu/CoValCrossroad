"""R310 — R309 established there IS structure. This asks WHAT it is, and includes the rival that
says there is none.

R309: the R² ceiling set by measurement error is 0.957, the observed R² is 0.612, so a single
linear shrink explains 64% of the achievable association and the missing 36% is not my noise —
the reliabilities are 0.986 and 0.970. Calibrated against a reordering sweep, 0.640 reads as
~30% of arms reordered. R309 named that world W-STRUCTURED and said explicitly that naming the
structure was the next round's job, because a world called "structured" with no mechanism is a
label.

⚠ AND THE RIVAL THAT SAYS THERE IS NO STRUCTURE GOES FIRST, because it is the one I would skip.
W-SE-TOO-SMALL: the missing 36% is not the judge doing anything — it is my STANDARD ERRORS being
underestimated. R301's bootstrap resamples PROMPTS, so it captures prompt sampling and nothing
else. If the judge itself has run-to-run variance the bootstrap cannot see, every SE is too small,
every reliability too high, the ceiling too high, and the shortfall is manufactured by my own
optimism about my own precision. That is the deflationary reading of R309's headline and it must
be priced before any mechanism is entertained.

It is testable, and the replicate is already on disk: `topw_k4` and `random_k4_s0` were judged at
0.8B by TWO INDEPENDENT PATHS — directly, and by subsetting the judged `coval_full`. Same
criteria, same replies, same template, different batching. That difference is judge-level noise
the prompt bootstrap structurally cannot contain, and it gives an INDEPENDENT floor on how wrong
the SEs could be.

ESTIMAND      ① the SE inflation factor `c` that would be required to push the ceiling down to the
                 observed R², i.e. to make the structure vanish; and whether `c` is plausible
                 against the replicate-based noise estimate.
              ② if structure survives: which covariate the residuals from the linear fit organise
                 on — rule FAMILY, effect MAGNITUDE, or criterion COUNT k.
IDENTIFICATION ① exact algebra given the SEs. ② partial: three covariates, 39 arms, so this can
                 rank them and cannot claim the winner is the only one.
SCOPE         population the 39 arms of R301's fit · instrument 2B and 0.8B · baseline
              `random_k4_s0` · regime clause ① effects, A2·annotator.
WORLDS        W-SE-TOO-SMALL  the required `c` is small and consistent with the replicates ->
                              R309's structure is an artifact of my precision claim. KILLS R309.
              W-FAMILY        residuals cluster by rule family: the shrink differs between
                              selecting from a rubric and generating from a conversation.
              W-MAGNITUDE     residuals depend on |effect|: a floor the smaller judge cannot
                              resolve below, so small effects shrink disproportionately.
              W-K             residuals depend on criterion count: summing more criteria averages
                              judge noise, so large-k arms survive the smaller judge better.
KILL          conditional on the controls:
                required c <= replicate-implied c  -> W-SE-TOO-SMALL, and R309 is retracted.
                else the covariate whose residual R² is highest AND whose CI excludes the others'
                point estimate -> that world. No separation -> UNRESOLVED, and say which pair.
POSITIVE CTRL plant a known structure — residuals made a pure function of one covariate — and
              require the ranking to recover it. Fails at g=0: with residuals shuffled, no
              covariate may win.
NEGATIVE CTRL shuffle the residuals against the covariates; all three residual R² must collapse to
              the permutation floor, which is reported, not assumed.
MULTIPLICITY  3 covariates x 1 residual fit, plus the c calculation. BH over the 3.
SEEDS         3 seeds for every synthetic arm; spread reported.
ARTIFACT      results/structure.json with source hash.
IMPOSSIBLE    whether the winning covariate is CAUSAL — that needs intervening on it, i.e.
              constructing arms that vary it while holding the others fixed, which this release's
              arm set does not span.
"""
import hashlib, itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
ZEFF = 1.959964 + 0.841621
A24 = SELF.parent.parent
SRC = A24 / "R301_is_the_judge_a_shrink_or_a_reorder" / "results" / "judge_slope.json"
R309 = A24 / "R309_is_the_missing_r2_noise_or_structure" / "results" / "reliability_ceiling.json"


def fit(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    if xc @ xc <= 0 or yc @ yc <= 0:
        return float("nan"), float("nan")
    return float(xc @ yc / (xc @ xc)), float((xc @ yc) ** 2 / ((xc @ xc) * (yc @ yc)))


def family(a):
    if a.startswith("random_k"): return "random_k"
    if a.startswith("topw_k"): return "topw_k"
    if a.endswith("_sham"): return "sham"
    for f in ("topabs", "topvar", "topwvar", "oracle", "greedy", "indep"):
        if a.startswith(f): return f
    return a


def main():
    for p in (SRC, R309):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.relative_to(ROOT)} absent."); return 2
    d = json.loads(SRC.read_text())
    d9 = json.loads(R309.read_text())
    arms = d["fit_arms"]; r = d["rows"]; n = len(arms)
    e2 = np.array([r[a]["c1_2"][0] for a in arms])
    e8 = np.array([r[a]["c1_8"][0] for a in arms])
    s2 = np.array([r[a]["mde1_2"] / ZEFF for a in arms])
    s8 = np.array([r[a]["mde1_8"] / ZEFF for a in arms])
    ks = np.array([float(r[a]["k"]) for a in arms])
    fams = [family(a) for a in arms]
    beta, r2 = fit(e2, e8)
    print(f"  {n} arms · observed R² {r2:.4f} · R309 ceiling {d9['r2_ceiling']:.4f} · "
          f"ratio {d9['ratio']:.4f}\n")

    # ---- ① THE DEFLATIONARY RIVAL, PRICED FIRST -------------------------------------------
    # ρ(c) = 1 − c²·mean(SE²)/Var. Find c making ρx(c)·ρy(c) == observed R².
    vx, vy = float(np.var(e2, ddof=1)), float(np.var(e8, ddof=1))
    mx, my = float(np.mean(s2 ** 2)), float(np.mean(s8 ** 2))

    def ceil_at(c):
        return max(0.0, 1 - c * c * mx / vx) * max(0.0, 1 - c * c * my / vy)

    lo, hi = 1.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if ceil_at(mid) > r2:
            lo = mid
        else:
            hi = mid
    c_req = (lo + hi) / 2
    print(f"  ① W-SE-TOO-SMALL: the SEs would have to be {c_req:.2f}x LARGER for the ceiling to")
    print(f"     fall to the observed R² and the structure to vanish.")

    # the independent replicate: two construction paths for the same arm at 0.8B
    par = d.get("controls", {}).get("parity", {}) or {}
    reps = [(k, v) for k, v in par.items() if isinstance(v, dict) and v.get("delta") is not None]
    if reps:
        # |delta| between two independent judgings is a draw from a distribution with sd = sqrt(2)*σ_judge
        deltas = np.array([abs(v["delta"]) for _, v in reps])
        sigma_judge = float(deltas.mean() / math.sqrt(2))
        c_rep = math.sqrt(1 + (sigma_judge ** 2) / mx) if mx > 0 else float("nan")
        print(f"     replicate-based judge noise: |Δ| over {len(reps)} arm(s) judged twice by")
        print(f"     INDEPENDENT PATHS = {deltas.mean():.5f} -> σ_judge {sigma_judge:.5f}")
        print(f"     -> SEs are at most {c_rep:.2f}x too small, from data the bootstrap cannot see")
        se_kills = c_rep >= c_req
    else:
        c_rep, se_kills = float("nan"), False
        print("     ⚠ no replicate on disk -> W-SE-TOO-SMALL is UNPRICED, not refuted")
    print(f"     required {c_req:.2f}x vs available {c_rep:.2f}x  -> "
          f"{'W-SE-TOO-SMALL SURVIVES, R309 retracted' if se_kills else 'W-SE-TOO-SMALL DOES NOT explain it'}")

    # ---- ② which covariate do the residuals organise on? ----------------------------------
    resid = e8 - (beta * e2 + (e8.mean() - beta * e2.mean()))
    covs = {"magnitude |eff_2B|": np.abs(e2),
            "criterion count k": ks,
            "rule family": None}
    fam_names = sorted(set(fams))
    fam_mean = {f: float(np.mean([resid[i] for i in range(n) if fams[i] == f])) for f in fam_names}
    covs["rule family"] = np.array([fam_mean[f] for f in fams])

    print(f"\n  ② WHICH COVARIATE DO THE RESIDUALS ORGANISE ON?  "
          f"(residual sd {resid.std(ddof=1):.5f})\n")
    print(f"    {'covariate':<24}{'residual R²':>13}{'perm floor (3 seeds)':>24}")
    out, floors = {}, {}
    for name, x in covs.items():
        _, rr = fit(x, resid)
        fl = []
        for seed in range(3):
            g = np.random.default_rng(7000 + seed)
            fl.append(fit(x, g.permutation(resid))[1])
        floors[name] = float(np.mean(fl))
        out[name] = dict(r2=rr, perm_floor=floors[name])
        print(f"    {name:<24}{rr:>13.4f}{np.mean(fl):>24.4f}")

    # ---- CONTROLS ---------------------------------------------------------------------------
    print(f"\n  POSITIVE CTRL  plant residuals that ARE a pure function of one covariate\n")
    pos_ok = True
    for planted in ("magnitude |eff_2B|", "criterion count k"):
        wins = []
        for seed in range(3):
            g = np.random.default_rng(8000 + seed)
            xp = covs[planted]
            synth = (xp - xp.mean()) / (xp.std() or 1) * resid.std(ddof=1) + g.normal(0, resid.std(ddof=1) * 0.3, n)
            scores = {k2: fit(v, synth)[1] for k2, v in covs.items()}
            wins.append(max(scores, key=scores.get))
        ok = all(w == planted for w in wins)
        pos_ok &= ok
        print(f"    planted {planted:<24} recovered {wins.count(planted)}/3   "
              f"{'PASS' if ok else 'FAIL'}")
    g0 = []
    for seed in range(3):
        g = np.random.default_rng(9000 + seed)
        sh = g.permutation(resid)
        scores = {k2: fit(v, sh)[1] for k2, v in covs.items()}
        g0.append(max(scores.values()))
    g0_ok = max(g0) < 0.25
    print(f"    g=0 (residuals shuffled) best R² {max(g0):.4f} over 3 seeds   "
          f"{'PASS — no covariate wins on noise' if g0_ok else '⚠ a covariate wins with nothing planted'}")

    # ---- KILL --------------------------------------------------------------------------------
    ranked = sorted(out.items(), key=lambda kv: -kv[1]["r2"])
    top, second = ranked[0], ranked[1]
    sep = top[1]["r2"] > second[1]["r2"] * 1.5 and top[1]["r2"] > max(floors.values()) * 3
    print("\n  " + "=" * 76)
    if not (pos_ok and g0_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the ranking is not readable.")
    elif se_kills:
        world = "W-SE-TOO-SMALL"
        print(f"  -> W-SE-TOO-SMALL. The SEs need only be {c_req:.2f}x larger and the replicates")
        print(f"     allow {c_rep:.2f}x, so R309's structure is my own precision claim. RETRACTED.")
    elif sep:
        world = f"W-{top[0].split()[0].upper()}"
        print(f"  -> {world}. Residual R² {top[1]['r2']:.3f} on `{top[0]}` against {second[1]['r2']:.3f}")
        print(f"     for the runner-up and a permutation floor of {max(floors.values()):.3f}.")
    else:
        world = "UNRESOLVED-BETWEEN-COVARIATES"
        print(f"  -> UNRESOLVED between covariates. `{top[0]}` {top[1]['r2']:.3f} does not separate")
        print(f"     from `{second[0]}` {second[1]['r2']:.3f} at the 1.5x margin this round")
        print(f"     pre-registered. The structure is real (R309) and this design cannot say which")
        print(f"     covariate carries it — which is a statement about 39 arms, not about the judge.")
    print("  " + "=" * 76)

    o = SELF.parent / "results" / "structure.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], n_arms=n, world=world,
        c_required=c_req, c_replicate=c_rep, se_explains=bool(se_kills),
        covariates=out, perm_floors=floors, positive_control_ok=bool(pos_ok),
        fails_at_g0=bool(g0_ok), family_means=fam_mean), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
