#!/usr/bin/env python3
"""R1106 — is the judges' disagreement a SCALE COMPRESSION or a REORDERING? They imply different repairs.

R1105: the definition admits 9 arms under the 2B judge and 0 under the 8B, 8 of the 9 by sign flip,
and mean A2 falls for every arm (`coval_core` 0.5665 -> 0.4695, `generic` 0.5514 -> 0.4767). Two very
different worlds produce that pattern and R1105 could not separate them.

⛔ THE ARITHMETIC TRAP, LABELLED BEFORE ANYTHING IS RUN. *That the ordering changed somewhere* is
already forced by R1105's committed table: `coval_core` leads `generic` under 2B and trails it under
8B. Re-reporting that would be 1+1=2. **The open question is whether the reordering is what a pure
SCALE CHANGE would produce anyway.** A judge with a smaller dynamic range compresses every margin
toward zero; margins that were small then cross zero *without the judge disagreeing about the
ordering at all*. That world predicts the sign flips, and it is repairable.

⛔ AND THE POPULATION FOR THE OBVIOUS CONTRAST IS n=2, MEASURED NOT ASSUMED. Counting distinct
criterion sets across the 968 prompts in each `core_<arm>.json`: only `generic` and `genericpool16`
have exactly ONE — every other arm on the common list has 398 to 968. So a `fixed vs prompt-specific`
arm-level contrast has two units on one side and both are the comparators. **The unit has to be the
PROMPT, and the quantity has to be the MARGIN OVER THE COMPARATOR**, which cancels the level shift by
construction because both of its terms are within-judge.

ESTIMAND        (Q1) the Spearman rank correlation of the 43 arms' mean A2 between judges. A pure
                     monotone rescaling gives exactly 1.
                (Q2) the regression of each arm's 8B margin over `generic` on its 2B margin:
                     `m8 = c * m2 + b`. Compression is `0 < c < 1` with high R² and b ~ 0.
                (Q3) the residual `m8 - (c*m2 + b)` per arm — what compression does NOT explain.
IDENTIFICATION  identified. All quantities are within-judge differences over the same 968 prompts on
                the 43 arms scoreable under both judges.
UNIT OF THE     Q1/Q2/Q3: an arm (n = 43). The per-prompt bootstrap below is on a prompt (n = 968).
  INSTRUMENT    Both are stated because the regression is the underpowered one and must say so.
UNIT OF THE     the same. ⚠ NOT `a cell`: R1105's 0.483 is a per-CELL correlation and this round's
  CLAIM         quantities are per-ARM means, which average 968 prompts and are far less noisy. The
                two must never be quoted as one another.
SCOPE           population: the 43 arms with both judges' files. instrument: mean A2 per arm, margins
                against `generic`. baseline: the 2B judge. regime: 968 prompts, target A2.
WORLDS          A SCALE COMPRESSION      the 8B judge has a smaller dynamic range. Then rank
                                 correlation is near 1, the regression has high R², and the sign
                                 flips are margins crossing zero under a shrinking scale. **The
                                 definition is repairable by renormalising the comparator.**
                B REORDERING            the judges disagree about which arms are better. Then rank
                                 correlation is materially below 1 and the residuals are large and
                                 structured. **No threshold reconciles them.**
                Prediction matrix on (Spearman rho, regression R^2):
                  A -> (>= 0.90, >= 0.80)      B -> (< 0.90, < 0.80)
KILL            pre-registered, and it can fire either way. World A is KILLED if Spearman rho < 0.90
                OR R^2 < 0.80. World B is KILLED if BOTH rho >= 0.90 and R^2 >= 0.80. Gated:
                                    if placebo_exact and synthetic_A_recovered and plant_detected:
                                        evaluate(rho, R2)
                                    else: UNVERIFIED
POSITIVE CTRL   a PLANTED REORDERING: swap two arms' 8B vectors and require the residual diagnostic
                to flag exactly those two. An instrument that cannot see a reordering it was handed
                cannot report the absence of one.
SYNTHETIC       ⭐ BUILD WORLD A AND CHECK THE INSTRUMENT SAYS SO. Take the 2B per-cell scores,
  WORLD         compress them about their own mean by the observed variance ratio, add Gaussian noise
                matched to the observed per-cell residual sd, and run the whole pipeline on it. The
                instrument must return rho ~ 1 and high R^2. If it does not, a low R^2 on the real 8B
                data says nothing, because the design cannot recognise compression when it is there.
PLACEBO         2B against itself: rho exactly 1, slope exactly 1, R^2 exactly 1, residuals 0.
NEGATIVE CTRL   the 2B margins must not be degenerate — if every arm had the same margin the
                regression would be undefined and R^2 meaningless. Their spread is reported.
NOISE FLOOR     a cluster bootstrap over prompts on rho, on the slope and on R^2, so `0.90` and
                `0.80` are read against the precision the design actually has.
MDE             reported for the regression: n = 43 arms is the small population here, and the
                bootstrap interval on R^2 is what says whether the threshold was reachable.
MULTIPLICITY    43 arms reported individually in the residual table, movers and non-movers.
SPECIFICATION   margin baseline in {`generic`, `genericpool16`} x statistic in {Spearman, Kendall} x
                normalisation in {raw margin, margin relative to the arm's own 2B level}. The last
                axis exists because §4's `difference of two bounded scores` says a covariate
                compressing both arms yields a differential proportional to their gap — which is
                world A's signature and must not be mistaken for evidence of it.
SEEDS           3, on the bootstrap and on the synthetic world.
ARTIFACT        results/compression_or_reordering.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      | criterion | what it would require |
                | whether either judge is CORRECT | an external gold standard |
                | a fixed-vs-prompt-specific arm contrast | more than 2 fixed arms; the release
                  ships exactly two and both are the comparators (measured above, not assumed) |
                | Qwen3B and Phi | their comparator files; that directory ships `sat_full_*` and
                  `sat_core_*` only |
                | cross-release | a second release |
"""
from __future__ import annotations

import hashlib, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

OUT = HERE / "results" / "compression_or_reordering.json"
NBOOT, SEEDS = 2000, (1106, 2212, 3318)
RHO_T, R2_T = 0.90, 0.80


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def kendall(a, b):
    n = len(a); c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
            c += s > 0; d += s < 0
    return float((c - d) / (c + d)) if (c + d) else float("nan")


def fit(m2, m8):
    c, b = np.polyfit(m2, m8, 1)
    pred = c * m2 + b
    ss_res = float(((m8 - pred) ** 2).sum())
    ss_tot = float(((m8 - m8.mean()) ** 2).sum())
    return float(c), float(b), (1 - ss_res / ss_tot if ss_tot > 0 else float("nan")), m8 - pred


def main() -> int:
    f05 = next(A27.glob("R1105_*/results/second_judge.json"), None)
    if f05 is None:
        print("  UNRUNNABLE: R1105's artifact is absent. Exit 2, never 0."); return 2
    common = json.loads(f05.read_text())["population"]["common"]

    tg, _ = load_targets()
    base = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(base) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    def perprompt(path):
        Sa = load_sat(path)
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({j for j, _ in Sa[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return v

    def path_for(arm, judge):
        if judge == "2B":
            f = RES / f"sat_{arm}.npz"
            return f if f.exists() else None
        f = RES / f"sat_{arm}_08b.npz"
        if f.exists():
            return f
        f = RES / f"sat08_{arm}.npz"
        return f if f.exists() else None

    V2, V8, arms = {}, {}, []
    for a in common:
        p2, p8 = path_for(a, "2B"), path_for(a, "8B")
        if p2 is None or p8 is None:
            continue
        v2, v8 = perprompt(p2), perprompt(p8)
        ok = np.isfinite(v2) & np.isfinite(v8)
        if ok.sum() < 100:
            continue
        V2[a] = np.nan_to_num(v2, nan=0.0); V8[a] = np.nan_to_num(v8, nan=0.0)
        arms.append(a)
    print(f"  arms scoreable under both judges: {len(arms)} · prompts {n}")

    # ---- SPECIFICITY, measured from the criterion sets rather than from names
    spec = {}
    for a in arms:
        f = RES / f"core_{a}.json"
        spec[a] = len({tuple(sorted(v)) for v in json.load(open(f)).values()}) if f.exists() else None
    n_fixed = sum(1 for v in spec.values() if v == 1)

    BASE = "generic"
    cand = [a for a in arms if a != BASE]

    def margins(V):
        return np.array([float((V[a] - V[BASE]).mean()) for a in cand])

    def analyse(V2_, V8_, label):
        m2 = np.array([float((V2_[a] - V2_[BASE]).mean()) for a in cand])
        m8 = np.array([float((V8_[a] - V8_[BASE]).mean()) for a in cand])
        lv2 = np.array([float(V2_[a].mean()) for a in cand])
        lv8 = np.array([float(V8_[a].mean()) for a in cand])
        rho = spearman(lv2, lv8)
        tau = kendall(lv2, lv8)
        c, b, r2, resid = fit(m2, m8)
        return {"label": label, "spearman_levels": round(rho, 4), "kendall_levels": round(tau, 4),
                "slope": round(c, 4), "intercept": round(b, 5), "r2": round(r2, 4),
                "resid": {a: round(float(r), 5) for a, r in zip(cand, resid)},
                "m2": m2, "m8": m8}

    real = analyse(V2, V8, "2B vs 8B")
    print(f"  REAL   spearman(levels) {real['spearman_levels']:.4f} · kendall "
          f"{real['kendall_levels']:.4f} · slope {real['slope']:.4f} · R^2 {real['r2']:.4f}")

    # ---- PLACEBO: 2B against itself
    plac = analyse(V2, V2, "2B vs 2B")
    placebo_exact = (abs(plac["spearman_levels"] - 1) < 1e-9 and abs(plac["slope"] - 1) < 1e-9
                     and abs(plac["r2"] - 1) < 1e-9
                     and max(abs(v) for v in plac["resid"].values()) < 1e-9)

    # ---- SYNTHETIC WORLD A: compression + matched noise, built from the 2B data
    rng = np.random.default_rng(SEEDS[0])
    allv2 = np.concatenate([V2[a] for a in arms]); allv8 = np.concatenate([V8[a] for a in arms])
    shrink = float(allv8.std() / allv2.std())
    resid_sd = float(np.std(allv8 - (allv2 - allv2.mean()) * shrink - allv8.mean()))
    VA = {a: (V2[a] - allv2.mean()) * shrink + allv8.mean()
             + rng.normal(0, resid_sd, n) for a in arms}
    synth = analyse(V2, VA, "2B vs synthetic-compressed 2B")
    synth_ok = synth["spearman_levels"] >= RHO_T and synth["r2"] >= R2_T
    print(f"  SYNTH  world A rebuilt (shrink {shrink:.3f}, noise sd {resid_sd:.4f}): "
          f"spearman {synth['spearman_levels']:.4f} · R^2 {synth['r2']:.4f} · recovered {synth_ok}")

    # ---- POSITIVE: a planted reordering must be flagged by the residual
    order = sorted(cand, key=lambda a: float(V8[a].mean()))
    lo_a, hi_a = order[0], order[-1]
    VP = dict(V8); VP[lo_a], VP[hi_a] = V8[hi_a], V8[lo_a]
    plant = analyse(V2, VP, "planted swap")
    # ⛔ THIS CONTROL FAILED FOR ITS OWN REASONS ON THE FIRST RUN, and the repair is the statistic.
    #    v1 ranked by |residual| IN THE PLANTED RUN and required the swapped pair to be the top two.
    #    It flagged `indep_k4_fit1` and `promptecho` — because `promptecho` already carries a large
    #    REAL residual (-0.02765) and the plant drags the fitted line, so a near-twin can outrank the
    #    plant itself. **A plant laid on top of real structure cannot top an ABSOLUTE list unless it
    #    exceeds everything real — and this round's whole finding is that real structure exists.**
    #    §4's `the control fails for its own reasons`, sub-kind ③: it targeted a different statistic
    #    than the one the question needs. The discriminating statistic is the CHANGE in residual, and
    #    it separates cleanly: 0.2815 and 0.1717 for the swapped pair against 0.0591 for the next arm.
    dres = {a: abs(plant["resid"][a] - real["resid"][a]) for a in cand}
    flagged = sorted(dres, key=lambda a: -dres[a])[:2]
    plant_detected = set(flagged) == {lo_a, hi_a}
    plant_margin = (round(dres[flagged[1]] / max(dres[a] for a in cand if a not in flagged), 2)
                    if len(cand) > 2 else None)
    print(f"  PLANT  swapped `{lo_a}` <-> `{hi_a}`; two largest residual CHANGES {flagged}; "
          f"detected {plant_detected} (separation x{plant_margin} over the next arm)")

    # ---- NEGATIVE: the 2B margins must not be degenerate
    m2 = real["m2"]
    margins_nondegenerate = float(m2.std()) > 1e-4

    # ---- NOISE FLOOR: cluster bootstrap over prompts on rho, slope, R^2
    boot = {"rho": [], "slope": [], "r2": []}
    for s in SEEDS:
        r_ = np.random.default_rng(s)
        for _ in range(NBOOT // len(SEEDS)):
            idx = r_.integers(0, n, n)
            b2 = {a: V2[a][idx] for a in arms}; b8 = {a: V8[a][idx] for a in arms}
            lv2 = np.array([b2[a].mean() for a in cand]); lv8 = np.array([b8[a].mean() for a in cand])
            bm2 = np.array([(b2[a] - b2[BASE]).mean() for a in cand])
            bm8 = np.array([(b8[a] - b8[BASE]).mean() for a in cand])
            c_, b_, r2_, _ = fit(bm2, bm8)
            boot["rho"].append(spearman(lv2, lv8)); boot["slope"].append(c_); boot["r2"].append(r2_)
    ci = {k: [round(float(np.percentile(v, 2.5)), 4), round(float(np.percentile(v, 97.5)), 4)]
          for k, v in boot.items()}
    print(f"  BOOT   rho {ci['rho']} · slope {ci['slope']} · R^2 {ci['r2']}")

    # ---- SPECIFICATION CURVE
    spec_rows = {}
    for bl in ("generic", "genericpool16"):
        if bl not in V2 or bl not in V8:
            continue
        cd = [a for a in arms if a != bl]
        mm2 = np.array([float((V2[a] - V2[bl]).mean()) for a in cd])
        mm8 = np.array([float((V8[a] - V8[bl]).mean()) for a in cd])
        c_, b_, r2_, _ = fit(mm2, mm8)
        lv2 = np.array([float(V2[a].mean()) for a in cd]); lv8 = np.array([float(V8[a].mean()) for a in cd])
        spec_rows[f"baseline={bl}|raw"] = {"slope": round(c_, 4), "r2": round(r2_, 4),
                                           "spearman": round(spearman(lv2, lv8), 4),
                                           "kendall": round(kendall(lv2, lv8), 4)}
        # normalised: margin relative to the arm's own 2B level — §4's bounded-score guard
        nz = mm2 != 0
        cn, bn, r2n, _ = fit(mm2[nz] / np.abs(mm2[nz]).max(), mm8[nz] / np.abs(mm2[nz]).max())
        spec_rows[f"baseline={bl}|normalised"] = {"slope": round(cn, 4), "r2": round(r2n, 4)}

    # ---- ⭐ THE QUESTION THE NUMBERS THEN DEMAND, and it is not the global one. Compression and
    #      reordering can both be present; what decides whether the DEFINITION is repairable is
    #      which of the two produced R1105's NINE SIGN FLIPS. If the compression line already
    #      predicts a negative 8B margin for those arms, their flips are a scale effect and
    #      renormalising the comparator recovers them. If they are residual outliers, it does not.
    c_, b_, _, _ = fit(real["m2"], real["m8"])
    flipped = json.loads(f05.read_text())["sets"]["only_2B"]
    flip_rows = {}
    for a in flipped:
        if a not in cand:
            continue
        i = cand.index(a)
        pred = float(c_ * real["m2"][i] + b_)
        flip_rows[a] = {"margin_2B": round(float(real["m2"][i]), 5),
                        "predicted_8B_by_compression": round(pred, 5),
                        "observed_8B": round(float(real["m8"][i]), 5),
                        "residual": round(float(real["resid"][a]), 5),
                        "compression_alone_predicts_a_flip": pred < 0}
    n_flip_by_compression = sum(1 for v in flip_rows.values()
                                if v["compression_alone_predicts_a_flip"])

    gate_open = placebo_exact and synth_ok and plant_detected and margins_nondegenerate
    rho, r2 = real["spearman_levels"], real["r2"]
    world_A_killed = (rho < RHO_T or r2 < R2_T) if gate_open else None
    world_B_killed = (rho >= RHO_T and r2 >= R2_T) if gate_open else None
    big = sorted(real["resid"], key=lambda a: real["resid"][a])[:5]

    payload = {
        "round": "R1106",
        "question": "is the judges' disagreement a scale compression or a reordering?",
        "labelled_derivation": ("that the ordering changed SOMEWHERE is forced by R1105's committed "
                               "table (coval_core leads generic under 2B, trails it under 8B). This "
                               "round asks whether the change exceeds what a pure scale change "
                               "produces — that is the part which could have come out otherwise."),
        "specificity_measured": {"distinct_criterion_sets": spec, "n_fixed_arms": n_fixed,
                                 "why": ("only `generic` and `genericpool16` have exactly one "
                                         "criterion set, so a fixed-vs-specific ARM contrast has "
                                         "n=2 and the unit had to be the prompt")},
        "real": {k: real[k] for k in ("spearman_levels", "kendall_levels", "slope", "intercept",
                                      "r2", "resid")},
        "placebo_2B_vs_2B": {k: plac[k] for k in ("spearman_levels", "slope", "r2")},
        "synthetic_world_A": {"shrink_factor": round(shrink, 4), "noise_sd": round(resid_sd, 5),
                              "spearman": synth["spearman_levels"], "r2": synth["r2"],
                              "recovered": synth_ok},
        "planted_reordering": {"swapped": [lo_a, hi_a],
                               "two_largest_residual_CHANGES": flagged,
                               "detected": plant_detected,
                               "separation_over_next_arm": plant_margin,
                               "v1_failed_because": ("it ranked by |residual| in the planted run and "
                                                     "a real large residual (`promptecho`) outranked "
                                                     "the plant; the change statistic separates")},
        "which_flips_compression_explains": {
            "rows": flip_rows, "n_flipped": len(flip_rows),
            "n_predicted_by_compression_alone": n_flip_by_compression,
            "why": ("compression and reordering can both be present; what decides whether the "
                    "DEFINITION is repairable is which of the two produced R1105's sign flips")},
        "bootstrap_ci": ci,
        "specification_curve": spec_rows,
        "largest_negative_residuals": {a: real["resid"][a] for a in big},
        "controls": {
            "PLACEBO 2B against itself is exact (rho=1, slope=1, R^2=1, residuals 0)": placebo_exact,
            "SYNTHETIC world A rebuilt from the 2B data IS recognised as compression": synth_ok,
            "POSITIVE a planted swap is flagged by the two largest residual CHANGES": plant_detected,
            "NEGATIVE the 2B margins are not degenerate": bool(margins_nondegenerate),
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "world_B_killed": world_B_killed,
                 "thresholds": {"spearman": RHO_T, "r2": R2_T},
                 "observed": {"spearman": rho, "r2": r2}},
        "seeds": list(SEEDS),
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        which = ("SCALE COMPRESSION" if world_B_killed else
                 "REORDERING" if world_A_killed else "NEITHER CLEANLY")
        payload["verdict"] = (
            f"⭐ {which}. Spearman on arm levels {rho:.4f} (CI {ci['rho']}), R^2 of the margin "
            f"regression {r2:.4f} (CI {ci['r2']}), slope {real['slope']:.4f} (CI {ci['slope']}), "
            f"against thresholds rho>={RHO_T} and R^2>={R2_T}. World A killed: {world_A_killed}; "
            f"world B killed: {world_B_killed}. The synthetic compression world built from the 2B "
            f"data returns rho {synth['spearman_levels']:.4f} and R^2 {synth['r2']:.4f}, so the "
            f"design CAN recognise compression when it is present. Largest negative residuals: "
            f"{ {a: real['resid'][a] for a in big} }."
            + f" ⭐ AND THE PRACTICAL QUESTION IS NARROWER THAN THE GLOBAL ONE: of R1105's "
              f"{len(flip_rows)} sign-flipped arms, {n_flip_by_compression} are already predicted to "
              f"flip by the COMPRESSION LINE ALONE, so their loss is a scale effect and "
              f"renormalising the comparator would recover them; "
              f"{len(flip_rows) - n_flip_by_compression} are not."
            + (" So the ordering the definition depends on is preserved and the failure is a scale "
               "artifact." if n_flip_by_compression == len(flip_rows) else
               " So the two mechanisms split the casualties and neither repair is sufficient alone."))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True, default=float))
    print()
    for k, v in spec_rows.items():
        print(f"  spec {k:<34} {v}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
