"""R313 — the SIGNED shrink-vs-precision relation: a property of the arm, or shared bootstrap noise?

R312 recorded a number and refused to claim it: `corr(1/SE_0.8B, signed residual) = -0.6288`
(R² 0.3954), four times what rule membership explains — but it had no null, and R312's own
absolute-value statistic turned out to have an envelope so wide that a planted effect and no
effect landed in the same place. So the signed statistic gets a floor, plus one control it
needs and the absolute one did not.

⛔ THE TRAP SPECIFIC TO THIS STATISTIC. The residual is built from the 0.8B effect. The
covariate is `1/SE_0.8B`, estimated from THE SAME cluster bootstrap over the same prompts. If a
realisation whose sampling error pushed `eff_08B` off the line also moved its own `SE_08B`, the
covariate and the outcome share an estimation error and the correlation is manufactured. That
is `realstat §4 · a control validated by its own instrument's noise`, and simulating at the
observed SEs does NOT address it — that null holds SE fixed and true, so it cannot contain the
channel under suspicion.

THE SEPARATOR IS A SECOND INSTRUMENT AND IT IS FREE. The 2B judge supplies an independent
precision `1/SE_2B`, estimated from a different judge's outputs, which CANNOT share estimation
noise with a residual built from 0.8B effects. The two correlate at 0.80, so they largely
measure a common latent property of the arm.

⚠ AND TWO PURE WORLDS DO NOT SPAN THE OUTCOME SPACE — that was R301's defect, diagnosed in
R310, and writing them as `all latent` vs `all artifact` would repeat it. The real object is a
MIXTURE, so the estimand is the mixture fraction itself.

ESTIMAND      f — the fraction of the signed precision-residual relation carried by the
              component of `1/SE_0.8B` that `1/SE_2B` also measures (latent precision), the
              remainder being carried by the 0.8B-specific component (which is where shared
              bootstrap noise must live). Estimated by simulating each f, calibrating its dose
              so the 8B coordinate reproduces the observed, and scoring the 2B coordinate.
IDENTIFICATION partial. `1/SE_2B` is itself a noisy measure of latent precision, so f is
              identified only up to the attenuation the simulation carries; and if the f-curve
              of predicted 2B values is flat, f is not identified at all. Report a BOUND, or
              report that the design cannot resolve it — never a point off a flat curve.
SCOPE         population the 39 arms of R301's fit · instrument Qwen3.5-2B and 0.8B · baseline
              `random_k4_s0` · regime clause ① effects, A2·annotator.
WORLDS        the f-continuum. f≈1 -> precision is a real arm property both judges see;
              f≈0 -> the relation is 0.8B-specific and R312's 0.3954 is an artifact of the
              covariate sharing a bootstrap with the outcome; intermediate f -> both.
KILL          conditional on the controls, all pre-registered:
                8B corr INSIDE its own floor                  -> W-NEITHER, nothing to attribute
                admissible f-set excludes f>=0.5              -> W-SPECIFIC
                admissible f-set excludes f<=0.5              -> W-LATENT
                admissible f-set spans both                   -> UNRESOLVED at 39 arms; say so
                no (f, g) reproduces the observed PAIR        -> the mixture family is refuted
                                                                 and the ontology is wrong
              ⚠ THE VERDICT NAME IS `W-SPECIFIC`, NOT `W-ARTIFACT`, and the change is
              substantive rather than cosmetic. The 0.8B-specific component contains BOTH
              shared bootstrap noise AND any genuine 0.8B-specific precision; this design
              separates `does it generalise across judges` from `does it not`, and does NOT
              isolate a mechanism. Calling it an artifact would be the verdict string
              asserting what nobody computed.
SPECIFICATIONS two were run and BOTH are reported. ① MARGINAL: dose each f so its 8B
              coordinate matches the observed, then test the 2B coordinate alone -> admissible
              f <= 0.25 on a 5-point grid. ② JOINT (the one below): Mahalanobis on the 2-D
              cloud over an 11 x 12 (f, g) surface, which does not condition on the 8B match
              -> admissible f <= 0.3. The second was written because the first conditions on
              one coordinate, a design defect, not because of what the first returned; the
              two agree and the record carries both.
POSITIVE CTRL a latent plant (f=1) calibrated to the observed 8B value must be RECOVERED by the
              2B instrument above its own floor. Validates the 2B instrument's POWER, not its
              direction: if it cannot see a planted latent effect of the observed size, its
              -0.255 is silence and the round is UNVERIFIED. Dose-response over 4 doses,
              and it must fail at g=0. CEILING: a maximal plant with no noise must land outside
              the floor, or no threshold is admissible (this is exactly where R312 died).
NEGATIVE CTRL the floor: judge does nothing beyond the fitted slope, noise at the observed SEs,
              400 simulations, computed separately per instrument, at two disjoint seed blocks.
PLACEBO       corr(residual, e2) = 0 exactly, by OLS. A DERIVATION: it tests that the residual
              is computed correctly and says NOTHING about the world. Labelled as such.
NOISE FLOOR   simulated per instrument, not assumed.
MULTIPLICITY  2 instrument-vs-floor cells + a 11 x 12 = 132-cell (f, g) surface, printed
              whole. Note the DIRECTION: more cells gives a high-f world MORE chances to admit
              by chance, so multiplicity makes the exclusion of f >= 0.4 harder to obtain, not
              easier. No correction is applied and the reason is stated rather than assumed.
SEEDS         400 floor sims per instrument x 2 blocks; 400 sims per (f, g) cell; the whole
              admissible set recomputed at 3 disjoint seed blocks and required identical.
ROBUSTNESS    leverage (drop-one jackknife over all 39 arms), estimator (Spearman vs Pearson),
              and the reliability derivation. Reported beside the verdict, not gating it.
ARTIFACT      results/signed_floor.json with source hash.
IMPOSSIBLE    a THIRD judge, which is what would break a tie if the f-curve is flat; and
              re-estimating SE inside the simulation, which needs the per-prompt vectors and a
              fresh bootstrap per simulated arm. The two-instrument separator is the cheap
              substitute and it targets the same channel.
"""
import hashlib, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
ZEFF = 1.959964 + 0.841621
SRC = (SELF.parent.parent / "R301_is_the_judge_a_shrink_or_a_reorder"
       / "results" / "judge_slope.json")
NSIM = 400
FGRID = tuple(round(0.1 * i, 2) for i in range(11))
GGRID = (0.05, 0.10, 0.15, 0.20, 0.30, 0.45, 0.65, 1.0, 1.6, 3.0, 8.0, 30.0)


def fit(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    return float(xc @ yc / (xc @ xc)) if xc @ xc > 0 else float("nan")


def corr(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    den = math.sqrt(float(xc @ xc) * float(yc @ yc))
    return float(xc @ yc / den) if den > 0 else float("nan")


def resid_of(x, y):
    b = fit(x, y)
    return y - (b * x + (y.mean() - b * x.mean()))


def z(v):
    return (v - v.mean()) / v.std()


def main():
    if not SRC.exists():
        print(f"  UNRUNNABLE: {SRC.relative_to(ROOT)} absent."); return 2
    d = json.loads(SRC.read_text())
    arms = d["fit_arms"]; r = d["rows"]; n = len(arms)
    e2 = np.array([r[a]["c1_2"][0] for a in arms])
    e8 = np.array([r[a]["c1_8"][0] for a in arms])
    s2 = np.array([r[a]["mde1_2"] / ZEFF for a in arms])
    s8 = np.array([r[a]["mde1_8"] / ZEFF for a in arms])
    beta = fit(e2, e8)
    resid = resid_of(e2, e8)
    rsd = float(resid.std(ddof=1))
    p8, p2 = 1.0 / s8, 1.0 / s2

    obs8, obs2 = corr(p8, resid), corr(p2, resid)
    r_inst = corr(p8, p2)
    print(f"  {n} arms · family slope {beta:+.4f} · residual sd {rsd:.5f}")
    print(f"  the two precision instruments correlate at {r_inst:+.4f}\n")
    print(f"  {'instrument':<28}{'corr(prec, signed resid)':>26}{'R²':>10}")
    print(f"    {'1/SE_0.8B  (shares a bootstrap)':<26}{obs8:>26.4f}{obs8**2:>10.4f}")
    print(f"    {'1/SE_2B    (cannot)':<26}{obs2:>26.4f}{obs2**2:>10.4f}")

    # ---- PLACEBO (a DERIVATION -- tests the code, not the world) -----------------------------
    pl = corr(e2, resid)
    print(f"\n  PLACEBO   corr(e2, residual) = {pl:+.2e}  "
          f"{'PASS' if abs(pl) < 1e-10 else 'FAIL'}   [DERIVATION: OLS forces this to 0]")

    # ---- the carriers: latent (shared) and 0.8B-specific --------------------------------------
    b82 = fit(p2, p8)
    lat = z(b82 * p2)                                    # ∝ 1/SE_2B: what both judges measure
    spc = z(p8 - (b82 * p2 + (p8.mean() - b82 * p2.mean())))   # ⟂ 1/SE_2B: 0.8B-specific
    print(f"\n  CARRIERS  corr(latent, 1/SE_0.8B) {corr(lat, p8):+.4f} · "
          f"corr(specific, 1/SE_0.8B) {corr(spc, p8):+.4f} · "
          f"corr(specific, 1/SE_2B) {corr(spc, p2):+.4f}")
    print(f"            a PURE specific world can drive the 8B coordinate no further than "
          f"{corr(spc, p8):+.4f} — reported because it bounds what f=0 can explain.")

    # ---- NEGATIVE CONTROL · the floor, per instrument, two disjoint seed blocks ---------------
    def floor(prec, base):
        a = np.array([corr(prec, resid_of(e2, beta * e2 +
                                          np.random.default_rng(base + t).normal(0, s8)))
                      for t in range(NSIM)])
        return float(a.mean()), float(a.std()), float(np.percentile(a, 2.5)), \
            float(np.percentile(a, 97.5))

    print(f"\n  NEGATIVE  floor: judge does nothing beyond the slope, noise at observed SEs, "
          f"{NSIM} sims\n")
    print(f"    {'instrument':<12}{'block':>7}{'mean':>10}{'sd':>9}{'95% envelope':>26}"
          f"{'observed':>11}")
    fl = {}
    for nm, prec, obs in (("1/SE_0.8B", p8, obs8), ("1/SE_2B", p2, obs2)):
        for blk, base in (("A", 7000), ("B", 9000)):
            m, sd, lo, hi = floor(prec, base)
            if blk == "A":
                fl[nm] = (lo, hi)
            print(f"    {nm:<12}{blk:>7}{m:>10.4f}{sd:>9.4f}"
                  f"{f'[{lo:+.4f}, {hi:+.4f}]':>26}"
                  f"{('OUTSIDE' if (obs < lo or obs > hi) else 'inside'):>11}")
    beats8 = obs8 < fl["1/SE_0.8B"][0] or obs8 > fl["1/SE_0.8B"][1]
    beats2 = obs2 < fl["1/SE_2B"][0] or obs2 > fl["1/SE_2B"][1]

    # ---- the f-curve: mixture fraction on the latent carrier ----------------------------------
    def sim(f, g, seeds):
        w = -(f * lat + (1 - f) * spc)      # sign: the observed relation is negative
        c8, c2 = [], []
        for sd_ in seeds:
            y = beta * e2 + g * rsd * w + np.random.default_rng(sd_).normal(0, s8)
            rr = resid_of(e2, y)
            c8.append(corr(p8, rr)); c2.append(corr(p2, rr))
        return np.array(c8), np.array(c2)

    # JOINT admissibility. Calibrating on one coordinate and testing the other CONDITIONS on
    # the 8B match, so a world that misses BOTH coordinates could still be scored on one. The
    # honest test asks whether the observed PAIR (corr_8B, corr_2B) lies inside the world's own
    # 2-D 95% region — Mahalanobis on the simulated cloud, which carries the two coordinates'
    # correlation instead of ignoring it.
    def joint_p(f, g, base=4000):
        c8, c2 = sim(f, g, range(base, base + NSIM))
        X = np.column_stack([c8, c2])
        mu = X.mean(0); C = np.cov(X.T)
        if not np.isfinite(np.linalg.cond(C)) or np.linalg.cond(C) > 1e12:
            return None, mu, C          # degenerate cloud: no admissibility call is possible
        Ci = np.linalg.inv(C)
        D = np.einsum("ij,jk,ik->i", X - mu, Ci, X - mu)
        dobs = float((np.array([obs8, obs2]) - mu) @ Ci @ (np.array([obs8, obs2]) - mu))
        return float((D >= dobs).mean()), mu, C

    print(f"\n  THE (f, g) SPECIFICATION SURFACE — joint test on the PAIR "
          f"({obs8:+.4f}, {obs2:+.4f}).")
    print(f"  Each cell is a Mahalanobis p against that world's own 2-D cloud; "
          f"admissible = p ≥ 0.05.\n")
    print("    f\\g " + "".join(f"{g:>7.2f}" for g in GGRID))
    curve, adm, degen = {}, [], 0
    for f in FGRID:
        row, best = [], (0.0, None, None)
        for g in GGRID:
            p, mu, _ = joint_p(f, g)
            if p is None:
                degen += 1
                row.append("   deg")
            else:
                row.append(f"{p:>7.3f}")
                if p > best[0]:
                    best = (p, g, (float(mu[0]), float(mu[1])))
        if best[0] >= 0.05:
            adm.append(f)
        curve[f] = dict(best_p=best[0], best_g=best[1], best_mu=best[2])
        print(f"    {f:<4.1f}" + "".join(row) + ("   <- admissible" if best[0] >= 0.05 else ""))

    # SEED ROBUSTNESS of the surface itself, at two further disjoint blocks.
    adm_seeds = {4000: list(adm)}
    for base in (12000, 20000):
        a2 = [f for f in FGRID
              if max((joint_p(f, g, base)[0] or 0.0) for g in GGRID) >= 0.05]
        adm_seeds[base] = a2
    print(f"\n    seed robustness of the admissible set, 3 disjoint blocks of {NSIM}:")
    for base, a2 in adm_seeds.items():
        print(f"      block {base:>6}   f ∈ {a2}")
    seed_ok = all(set(v) == set(adm) for v in adm_seeds.values())
    print(f"      identical across blocks: {seed_ok}")

    # ---- ROBUSTNESS · three axes that have killed findings in this project before -------------
    # (a) LEVERAGE. A correlation over 39 points can be one arm. Jackknife both coordinates.
    jk8 = np.array([corr(np.delete(p8, i), np.delete(resid, i)) for i in range(n)])
    jk2 = np.array([corr(np.delete(p2, i), np.delete(resid, i)) for i in range(n)])
    worst = int(np.argmax(jk8))     # the drop that weakens the 8B relation most
    # (b) ESTIMATOR. Spearman: does the whole thing survive going to ranks?
    def rank(v):
        o = v.argsort(); rr = np.empty(n); rr[o] = np.arange(n, dtype=float); return rr
    sp8, sp2 = corr(rank(p8), rank(resid)), corr(rank(p2), rank(resid))
    # (c) an alternative reading: is the gap just the two instruments' different reliabilities?
    # If both measured one latent precision, disattenuation would EQUALISE them. It is a
    # DERIVATION under that assumption, reported to show the assumption's own consequence.
    dis8, dis2 = obs8 / math.sqrt(abs(r_inst)), obs2 / math.sqrt(abs(r_inst))
    print(f"\n  ROBUSTNESS")
    print(f"    leverage    8B jackknife [{jk8.min():+.4f}, {jk8.max():+.4f}] · "
          f"2B [{jk2.min():+.4f}, {jk2.max():+.4f}]")
    print(f"                worst single drop ({arms[worst]}) leaves 8B at {jk8[worst]:+.4f} "
          f"and 2B at {jk2[worst]:+.4f}")
    print(f"    estimator   Spearman 8B {sp8:+.4f} · 2B {sp2:+.4f}   "
          f"(Pearson {obs8:+.4f} · {obs2:+.4f})")
    print(f"    reliability if ONE latent precision, disattenuating by √{abs(r_inst):.3f} gives "
          f"8B {dis8:+.4f} · 2B {dis2:+.4f}")
    print(f"                — a common latent property would make these EQUAL; the gap "
          f"{abs(dis8 - dis2):.4f} is what the f-surface is measuring. [DERIVATION]")
    lev_ok = (jk8.max() < fl["1/SE_0.8B"][0]) and (jk2.max() < 0 or jk2.min() > 0)
    est_ok = abs(sp8) > abs(sp2)
    print(f"    -> leverage: the 8B relation survives EVERY single-arm drop below its floor: "
          f"{jk8.max() < fl['1/SE_0.8B'][0]}")
    print(f"    -> estimator: the 8B > 2B ordering survives ranks: {est_ok}")

    # ---- POSITIVE CONTROL · can the 2B instrument see a planted LATENT effect at all? ---------
    g_cal = curve[1.0]["best_g"] or 0.31
    print(f"\n  POSITIVE  plant f=1 (pure latent); require the 2B instrument to clear its own")
    print(f"            floor [{fl['1/SE_2B'][0]:+.4f}, {fl['1/SE_2B'][1]:+.4f}]. "
          f"Validates POWER, not direction.\n")
    print(f"    {'g':>8}{'8B sees':>12}{'2B sees':>12}{'2B verdict':>30}")
    pos_ok = g0_ok = False
    for g in (0.0, 0.25 * g_cal, 0.5 * g_cal, g_cal):
        c8, c2 = sim(1.0, g, range(5000, 5003))
        m8, m2 = float(c8.mean()), float(c2.mean())
        out2 = m2 < fl["1/SE_2B"][0] or m2 > fl["1/SE_2B"][1]
        if g == 0.0:
            g0_ok = not out2
            v = "lands ON the floor" if g0_ok else "⚠ FIRES with nothing planted"
        else:
            v = "clears its floor" if out2 else "inside the floor"
            if g == g_cal:
                pos_ok = out2
        print(f"    {g:>8.2f}{m8:>12.4f}{m2:>12.4f}{v:>30}")

    ceil2 = corr(p2, resid_of(e2, beta * e2 + 50.0 * rsd * (-lat)))
    ceil_ok = ceil2 < fl["1/SE_2B"][0] or ceil2 > fl["1/SE_2B"][1]
    print(f"\n    CEILING (maximal plant, no noise) 2B -> {ceil2:+.4f}   "
          f"{'outside the floor: a threshold IS admissible'if ceil_ok else '⚠ INSIDE: NO threshold is admissible'}")

    # ---- KILL ---------------------------------------------------------------------------------
    ctrl = (abs(pl) < 1e-10) and pos_ok and g0_ok and ceil_ok and seed_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  placebo={abs(pl) < 1e-10}  positive={pos_ok}  g0={g0_ok}  "
          f"ceiling={ceil_ok}  seed={seed_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    print(f"  ROBUST    leverage={lev_ok}  estimator={est_ok}   (reported, not gating: they")
    print("            narrow the claim rather than license it)")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the surface is not readable.")
    elif not beats8:
        world = "W-NEITHER"
        print(f"  -> W-NEITHER. The 8B correlation {obs8:+.4f} sits INSIDE its own floor")
        print(f"     [{fl['1/SE_0.8B'][0]:+.4f}, {fl['1/SE_0.8B'][1]:+.4f}]. Nothing to attribute;")
        print("     R312's recorded 0.3954 is dead and the mixture question does not arise.")
    elif not adm:
        world = "W-ONTOLOGY-WRONG"
        print("  -> THE MIXTURE FAMILY IS REFUTED. No (f, g) cell reproduces the observed PAIR.")
        print("     The relation is not carried by either component of the precision")
        print("     decomposition, so these worlds do not span the outcome space and the next")
        print("     round's job is a different ontology, not a finer grid.")
    elif max(adm) < 0.5:
        world = "W-SPECIFIC"
        print(f"  -> W-SPECIFIC. Only f ≤ {max(adm):.1f} reproduces both coordinates jointly. The")
        print("     signed relation lives in the component of 1/SE_0.8B that 1/SE_2B cannot see:")
        print("     it is a property of THIS JUDGE'S measurement of the arm, not of the arm.")
        print(f"     R312's R² {obs8**2:.4f} does not generalise across judges, and its natural")
        print(f"     reading — that precisely-measured arms survive the smaller judge — requires")
        print(f"     f ≥ 0.5, which the data excludes.")
        print("     ⚠ NOT named `artifact`: `0.8B-specific` contains BOTH shared bootstrap noise")
        print("       AND genuine 0.8B-specific precision, and this design cannot separate them.")
        print("       Naming a mechanism here would be the verdict string asserting what nobody")
        print("       computed. What separates them: independent re-judgings per arm, of which")
        print("       the release has 2 — enough for R309's noise estimate, not for a slope.")
    elif min(adm) > 0.5:
        world = "W-LATENT"
        print(f"  -> W-LATENT. Only f ≥ {min(adm):.1f} reproduces both coordinates. Precision is a")
        print("     real property of the ARM that both judges measure and that predicts how the")
        print("     arm survives the smaller judge. R312's number stands, with a mechanism.")
    else:
        world = "UNRESOLVED"
        print(f"  -> UNRESOLVED. The admissible set is f ∈ {adm}, spanning both halves: the")
        print("     surface is too flat at 39 arms with two 80%-correlated instruments. What")
        print("     would resolve it: a THIRD judge, or re-estimating SE inside the simulation")
        print("     from the per-prompt vectors so the shared-noise channel is simulated rather")
        print("     than proxied.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {2 + len(FGRID) * len(GGRID)} cells: 2 instrument-vs-floor "
          f"({sum([beats8, beats2])} outside their floor) + {len(FGRID) * len(GGRID)} (f, g) cells,")
    print(f"                of which {len(adm)} of {len(FGRID)} f values admit at any dose and "
          f"{degen} cells were degenerate (no call made).")

    o = SELF.parent / "results" / "signed_floor.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], n_arms=n, world=world,
        corr_8b=obs8, corr_2b=obs2, r_instruments=r_inst,
        floor_8b=list(fl["1/SE_0.8B"]), floor_2b=list(fl["1/SE_2B"]),
        beats_floor_8b=bool(beats8), beats_floor_2b=bool(beats2),
        max_8b_from_specific=corr(spc, p8), f_surface={str(k): v for k, v in curve.items()},
        admissible_f=adm, degenerate_cells=degen, placebo=pl, positive_ok=bool(pos_ok),
        g0_ok=bool(g0_ok), ceiling_2b=ceil2, ceiling_ok=bool(ceil_ok),
        n_sim=NSIM, f_grid=list(FGRID), g_grid=list(GGRID),
        admissible_by_seed={str(k): v for k, v in adm_seeds.items()}, seed_ok=bool(seed_ok),
        jackknife_8b=[float(jk8.min()), float(jk8.max())],
        jackknife_2b=[float(jk2.min()), float(jk2.max())],
        spearman_8b=sp8, spearman_2b=sp2, leverage_ok=bool(lev_ok),
        estimator_ok=bool(est_ok)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
