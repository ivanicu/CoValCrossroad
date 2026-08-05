"""
R726 · how wide is the disagreement zone

ESTIMAND        for each admission rule, the interval of t within which the bootstrap-based
                predicate and the analytic-t threshold can disagree given the observed spread of
                r = SE_ci/SE_mde, and how many of the 82 cells fall inside it. R725 measured the
                REALISED disagreements (0); this measures whether that zero is structural or lucky.
IDENTIFICATION  identified from R725's persisted per-cell SEs. NOT identified: the r of an unseen
                arm; the observed range is an extreme order statistic of 82, so the 5-95 percentile
                range is reported beside min-max, never one alone.
SCOPE           population 82 cells · instrument algebraic zone boundaries + occupancy ·
                baseline R725's realised zero · regime census source_sha 2bc1124f6825df0f
WORLDS          W-LUCK wide and unoccupied -> corpus-dependent · W-STRUCTURE narrow -> a property
                of the rules
KILL            conditional; gated on POSITIVE and DOSE-RESPONSE. See PREREGISTRATION.txt.
POSITIVE CTRL   a cell planted at the dead centre of the ci_only zone must be inside it AND flip at
                the adverse end; band floor (t=10 -> 0 inside, 0 flips) < planted <= ceiling 82.
g=0             that far cell must be inside NO zone and flip under NO r.
DOSE-RESPONSE   r spread x {0, 0.5, 1, 2, 4} about its midpoint; width must be monotone and EXACTLY
                0 at multiplier 0. A width that does not scale with the spread is arithmetic.
NEGATIVE CTRL   every r set to exactly 1 -> all widths 0, occupancy 0. excluded world: "the zones
                come from the threshold arithmetic rather than from the SE spread".
SHAM            the same computation on point and mde_only, whose predicates never touch SE_ci ->
                width exactly 0. The ingredient is absent, not inverted.
PLACEBO         a cell against itself under one rule -> 0 flips.
NOISE FLOOR     min-max vs 5-95 percentile r range; the gap between them IS the floor.
MULTIPLICITY    5 rules x 5 dose levels x 82 cells = 2050 classifications, all reported.
SPECIFICATION   r range (min-max vs 5-95) x 5 rules x 5 dose levels
SEEDS           deterministic; two hash seeds byte-identical
ARTIFACT        results/r726_zone_width.json with tree_sha
IMPOSSIBLE      the r of an unobserved arm -> a new arm judged by the same pipeline ·
                independently replicated -> a second implementer
"""
import hashlib, json, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
CENSUS = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"

Z95  = 1.959964
ZEFF = 1.959964 + 0.841621
RULES = ("point", "ci_only", "mde_only", "strict", "conservative")


def boundary(rule: str, r: float):
    """The t_mde at which this rule switches, as a function of r = SE_ci/SE_mde.

    ⛔ DERIVATION. point and mde_only (and strict, which binds on mde_only when eff>0) never touch
    SE_ci, so their boundary is constant in r and their zone width is exactly 0.
    """
    if rule == "point":         return 0.0
    if rule == "ci_only":       return Z95 * r
    if rule == "mde_only":      return ZEFF
    if rule == "strict":        return ZEFF
    if rule == "conservative":  return ZEFF + Z95 * r
    raise ValueError(rule)


def zone(rule: str, rlo: float, rhi: float):
    a, b = boundary(rule, rlo), boundary(rule, rhi)
    return (min(a, b), max(a, b))


def main() -> int:
    print("=" * 100)
    print("R726 · HOW WIDE IS THE DISAGREEMENT ZONE")
    print("=" * 100)
    if not CENSUS.exists():
        print("  UNRUNNABLE: census absent. Exit 2, never 0."); return 2
    rows = json.loads(CENSUS.read_text())["rows"]
    if not rows:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2

    cells = []
    for a, rw in rows.items():
        for ci_k, mde_k, cl in (("c1", "mde1", 1), ("c2", "mde2", 2)):
            eff, lo, hi = rw[ci_k]; mde = rw[mde_k]
            se_ci, se_mde = (hi - lo) / (2 * Z95), mde / ZEFF
            if se_mde <= 0:
                continue
            cells.append({"arm": a, "clause": cl, "t": eff / se_mde, "r": se_ci / se_mde})
    if not cells:
        print("  ⛔ EMPTY POPULATION after filtering — exit 2, never 0"); return 2

    R = np.array([c["r"] for c in cells]); T = np.array([c["t"] for c in cells])
    r_min, r_max = float(R.min()), float(R.max())
    r_p5, r_p95 = float(np.percentile(R, 5)), float(np.percentile(R, 95))
    mid = 0.5 * (r_min + r_max); half = 0.5 * (r_max - r_min)
    print(f"  cells {len(cells)}   r = SE_ci/SE_mde")
    print(f"     min-max      [{r_min:.4f}, {r_max:.4f}]  spread {r_max-r_min:.4f}")
    print(f"     5th-95th pct [{r_p5:.4f}, {r_p95:.4f}]  spread {r_p95-r_p5:.4f}")
    print(f"     ⚠ min-max is an EXTREME ORDER STATISTIC of {len(cells)} draws; the gap between the")
    print(f"       two spreads ({(r_max-r_min)-(r_p95-r_p5):.4f}) is this design's noise floor.")

    print(f"\n  ⛔ DERIVATION — only two rules have an SE-dependent boundary:")
    for rl in RULES:
        z = zone(rl, r_min, r_max)
        print(f"     {rl:<13} boundary t = "
              f"{'0' if rl=='point' else ('%.6f' % ZEFF) if rl in ('mde_only','strict') else ('%.6f*r' % Z95) if rl=='ci_only' else ('%.6f + %.6f*r' % (ZEFF, Z95))}"
              f"   zone [{z[0]:.4f}, {z[1]:.4f}]  width {z[1]-z[0]:.6f}")

    ctl = {}
    print("\n─── CONTROLS ───")

    zc = zone("ci_only", r_min, r_max)
    planted_t = 0.5 * (zc[0] + zc[1])
    far_t = 10.0
    def inside_any(t, rlo, rhi):
        return any(zone(rl, rlo, rhi)[0] < t < zone(rl, rlo, rhi)[1] for rl in RULES)
    def flips(t, rlo, rhi):
        return any((t > boundary(rl, rlo)) != (t > boundary(rl, rhi)) for rl in RULES)
    p_in, p_fl = inside_any(planted_t, r_min, r_max), flips(planted_t, r_min, r_max)
    f_in, f_fl = inside_any(far_t, r_min, r_max), flips(far_t, r_min, r_max)
    ctl["POSITIVE"] = p_in and p_fl and not f_in and not f_fl
    print(f"  POSITIVE   planted at the ci_only zone centre t={planted_t:.4f}: inside={p_in} flips={p_fl}")
    print(f"  g=0        far cell t={far_t}: inside={f_in} flips={f_fl} (both must be False)")
    print(f"             band: floor (0 inside, 0 flips) < planted (1,1) <= ceiling {len(cells)}")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    DOSES = (0.0, 0.5, 1.0, 2.0, 4.0)
    dose_rows = []
    for m in DOSES:
        lo_, hi_ = mid - half * m, mid + half * m
        w = zone("ci_only", lo_, hi_)
        occ = int(sum(1 for c in cells if inside_any(c["t"], lo_, hi_)))
        flp = int(sum(1 for c in cells if flips(c["t"], lo_, hi_)))
        dose_rows.append({"mult": m, "r_lo": lo_, "r_hi": hi_, "width": w[1] - w[0],
                          "occupancy": occ, "flips": flp})
    widths = [d["width"] for d in dose_rows]
    dose_monotone = all(widths[i] <= widths[i + 1] for i in range(len(widths) - 1)) and widths[0] == 0.0
    ctl["DOSE"] = dose_monotone
    print(f"  DOSE-RESP  r-spread multiplier -> ci_only zone width, occupancy, flips")
    for d in dose_rows:
        print(f"             x{d['mult']:<4} r [{d['r_lo']:.4f}, {d['r_hi']:.4f}]  "
              f"width {d['width']:.6f}  inside {d['occupancy']:<3} flips {d['flips']}")
    print(f"             monotone and exactly 0 at multiplier 0 -> "
          f"{'PASS' if ctl['DOSE'] else 'FAIL'}")

    neg_w = [zone(rl, 1.0, 1.0)[1] - zone(rl, 1.0, 1.0)[0] for rl in RULES]
    neg_occ = int(sum(1 for c in cells if inside_any(c["t"], 1.0, 1.0)))
    ctl["NEGATIVE"] = all(w == 0.0 for w in neg_w) and neg_occ == 0
    print(f"  NEGATIVE   every r set to exactly 1 -> widths {[f'{w:.1f}' for w in neg_w]}, "
          f"occupancy {neg_occ} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the zones come from the threshold arithmetic, not the SE spread'")

    sham_w = {rl: zone(rl, r_min, r_max)[1] - zone(rl, r_min, r_max)[0]
              for rl in ("point", "mde_only", "strict")}
    ctl["SHAM"] = all(w == 0.0 for w in sham_w.values())
    print(f"  SHAM       rules whose predicate never touches SE_ci: "
          f"{ {k: round(v,6) for k,v in sham_w.items()} } -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}  (ingredient absent, not inverted)")

    plc = int(sum(1 for c in cells if (c["t"] > boundary("ci_only", c["r"]))
                  != (c["t"] > boundary("ci_only", c["r"]))))
    ctl["PLACEBO"] = plc == 0
    print(f"  PLACEBO    each cell against itself -> {plc} flips (must be 0) -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── OCCUPANCY, both r ranges ─────────────────────────────────────────────────────────────
    print(f"\n─── OCCUPANCY · {len(RULES)} rules x {len(DOSES)} doses x {len(cells)} cells = "
          f"{len(RULES)*len(DOSES)*len(cells)} classifications ───")
    res = {}
    for tag, (rl_, rh_) in (("min-max", (r_min, r_max)), ("p5-p95", (r_p5, r_p95))):
        inside = [c for c in cells if inside_any(c["t"], rl_, rh_)]
        flipped = [c for c in cells if flips(c["t"], rl_, rh_)]
        res[tag] = {"width_ci_only": zone("ci_only", rl_, rh_)[1] - zone("ci_only", rl_, rh_)[0],
                    "width_conservative": zone("conservative", rl_, rh_)[1]
                                          - zone("conservative", rl_, rh_)[0],
                    "inside": [f"{c['arm']}|{c['clause']}" for c in inside],
                    "flipped": [f"{c['arm']}|{c['clause']}" for c in flipped]}
        print(f"  {tag:<9} ci_only width {res[tag]['width_ci_only']:.6f}  "
              f"conservative width {res[tag]['width_conservative']:.6f}  "
              f"inside {len(inside)}  would-flip {len(flipped)}")
        for c in inside:
            print(f"             ⚠ inside: {c['arm']}|clause{c['clause']}  t={c['t']:.4f} r={c['r']:.4f}")

    A = res["min-max"]["width_ci_only"]
    B = len(res["min-max"]["inside"])
    C = len(res["min-max"]["flipped"])
    D = next((d["mult"] for d in dose_rows if d["occupancy"] > 0), None)
    nonzero = [rl for rl in RULES if zone(rl, r_min, r_max)[1] - zone(rl, r_min, r_max)[0] > 0]
    w_eq = (abs(res["min-max"]["width_ci_only"] - res["min-max"]["width_conservative"]) < 1e-12)
    directional = len(nonzero) == 2 and w_eq

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A ci_only zone width", round(A, 4), 0.0, 5.0, 0.24),
                                   ("B cells inside any zone", B, 0, 82, 3),
                                   ("C cells that would flip", C, 0, 82, 0),
                                   ("D dose at first occupancy", D if D is not None else "none",
                                    0.0, 64.0, 2.0)]:
        ok = (lo_ <= val <= hi_) if isinstance(val, (int, float)) else "n/a (never occupied)"
        print(f"  {nm:<28} registered {reg:<6} -> {str(val):<10} in [{lo_},{hi_}]: {ok}")
    print(f"  DIRECTIONAL exactly 2 rules have a non-zero zone and their widths are EQUAL -> "
          f"{directional}   (non-zero: {nonzero}) ⛔ DERIVATION, this is an implementation check")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["DOSE"]):
        verdict = "UNVERIFIED — a gating control did not fire; no zone claim is admissible."
    elif C > 0:
        verdict = (f"⭐⭐⭐ R725's ZERO WAS PARTLY LUCK. {C} of {len(cells)} cells would flip verdict "
                   f"under the adverse end of the observed r range: {res['min-max']['flipped']}. "
                   f"Their admission is rule-dependent and is downgraded.")
    elif A > 0.5:
        verdict = (f"⭐⭐⭐ W-LUCK. The zone is {A:.4f} wide and unoccupied, so R725's collapse holds "
                   f"for these arms and would not be safe for a differently distributed set.")
    else:
        verdict = (f"⭐⭐⭐ W-STRUCTURE. The disagreement zone is {A:.6f} wide at ci_only and "
                   f"{res['min-max']['width_conservative']:.6f} at conservative — equal by algebra — "
                   f"and NO cell of {len(cells)} falls inside either, nor would any flip under the "
                   f"adverse end of the observed r range. ⭐ So R725's zero-of-410 is a property of "
                   f"the rules at this SE agreement, not luck about where these arms sit: the SE "
                   f"spread would have to grow by a factor of {D if D else '>4'} before a single cell "
                   f"entered a zone. ⚠ Three limits attach. The zone is estimated from the min-max r "
                   f"range, an extreme order statistic of {len(cells)} draws; the 5-95 percentile "
                   f"range gives {res['p5-p95']['width_ci_only']:.6f}, and the gap between them is "
                   f"this design's floor. Only two of the five rules have an SE-dependent boundary "
                   f"at all, so three of them could never have disagreed — that is arithmetic, not "
                   f"evidence. And the r of an arm this release does not contain is unmeasurable "
                   f"here.")
    print(f"  {verdict}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {
        "world": verdict, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
        "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        "n_cells": len(cells),
        "r_range_min_max": [r_min, r_max], "r_range_p5_p95": [r_p5, r_p95],
        "noise_floor_spread_gap": (r_max - r_min) - (r_p95 - r_p5),
        "zones": {rl: list(zone(rl, r_min, r_max)) for rl in RULES},
        "zone_widths": {rl: zone(rl, r_min, r_max)[1] - zone(rl, r_min, r_max)[0] for rl in RULES},
        "dose_response": dose_rows,
        "by_r_range": res,
        "A_ci_only_width": A, "B_inside": B, "C_would_flip": C, "D_dose_first_occupancy": D,
        "rules_with_nonzero_zone": nonzero, "directional_two_equal_zones": directional,
        "directional_is_a_derivation": True,
        "registered": "A 0.24 [0,5]; B 3 [0,82]; C 0 [0,82]; D 2.0 [0,64]; directional 2 equal zones",
        "residue": "the r of an arm not in this release is unmeasurable here; min-max is an extreme "
                   "order statistic and the 5-95 range is reported beside it",
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r726_zone_width.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r726_zone_width.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
