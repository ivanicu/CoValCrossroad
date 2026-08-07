#!/usr/bin/env python3
"""
R923 · turn clause ② on its own comparators, and count how many admitted arms sit inside the
        design's resolution of the bar.

⛔ WHY. R922 showed clause ② is a threshold on mean A2 whose cut is set by the comparator:
`genericpool16` → 0.5514 (28 admitted), `generic` → 0.5593 (24 admitted). Those differ by 0.0080.
The definition currently quotes one of them as though the other did not exist.

⚠ **AND MY OWN NEXT PROPOSED THE WRONG COMPARISON.** It said to check 0.0080 against R860's MDE of
0.0103. **R860's MDE was measured for a PAIRED DIFFERENCE BETWEEN TWO ARMS; the cut is a THRESHOLD
ON MEAN A2.** Those are different statistics on different scales, and comparing them is §4's *"the
control targets a different statistic than the one being reported"* — the same defect that once
aimed a control at a slope while the paper reported a decile curve. An inherited MDE is not this
design's resolution; it is another design's.

⭐⭐⭐ **THE EXACT MOVE COSTS NOTHING AND USES THE DEFINITION ON ITSELF.** Clause ② already has a
procedure for deciding whether one arm resolvably beats another. **Both comparators are arms.** So
run clause ② on the pair: is `lo(A2(generic) − A2(genericpool16)) > 0`? If neither direction clears
zero, the two admissible calibrations are indistinguishable by the definition's own bar, and the
difference between 24 and 28 admitted arms is not a difference this design can see.

⭐⭐ **AND THE DELIVERABLE IS THE BOUNDARY CENSUS.** For every arm, `lo` under each comparator says
how far it sits from the bar. An arm whose `lo` is within the design's own resolution of zero is
admitted or rejected by a margin the design cannot resolve. **Counting those bounds how much of
"the twelve" is real.**

ESTIMAND        ① whether either legitimate comparator resolvably beats the other under clause ②;
                ② the number of arms whose admission is inside the design's measured resolution.
IDENTIFICATION  exact. Both are functions of the per-prompt A2 vectors and the bootstrap draw.
                ⚠ Not an admission probability; the arms were built, not sampled.
SCOPE           population: R881's 99 arms on 968 shared prompts, and the 2 legitimate comparators
                instrument: A2 vs human class vectors; cluster bootstrap NBOOT 8000, seed 921 —
                            the SAME seed as R921/R922 so control ① is an exact reproduction
                baseline:   `genericpool16`, the comparator every published number used
                regime:     home release
WORLDS          A · one comparator resolvably beats the other -> the cuts are genuinely different,
                    the definition must pick one and say why, and 24-vs-28 is a real distinction
                B · neither clears zero -> the two calibrations are indistinguishable, and the
                    definition must quote an INTERVAL of cuts, not a number
KILL            CONDITIONAL:
                  ⭐ ① WIRING: reproduce R922's implied cut and admitted count for both legitimate
                     comparators exactly, same seed.
                  ⭐ ② RESOLUTION MEASURED HERE, NOT INHERITED: the design's resolution for THIS
                     estimand is the half-width of the bootstrap CI of an arm's margin, measured
                     per arm and reported as a distribution. R860's 0.0103 is printed beside it
                     ONLY to show they are different statistics — it is never used as a threshold.
                  ⭐ ③ POSITIVE / DOSE-RESPONSE, WITH ITS FORCED PART LABELLED. Plant an arm at
                     the bar and sweep a constant offset `d`. ⚠ **`lo(d) = lo(0) + d` EXACTLY** —
                     a constant shifts every bootstrap mean by that constant, so the linearity of
                     the response and the flip point at `d = -lo(0)` are DERIVATIONS, not
                     measurements, and computing them by nine more bootstraps would have spent six
                     minutes rediscovering arithmetic. What is MEASURED is where that flip point
                     sits relative to the resolution band measured in ②: if `|lo(0)|` for the arm
                     nearest the bar is larger than the band, the band is too small to explain the
                     admission decisions and the resolution number is wrong.
                  ⭐ ④ PLACEBO: `lo(X − X)` = 0 exactly for both comparators — the self-comparison
                     structural zero, used as the control it is (R915, R921).
MULTIPLICITY    2 comparators × 99 arms × {lo, boundary distance}; the dose-response grid; every
                arm's boundary distance summarised and the unresolvable ones named.
ARTIFACT        results/bar_resolution.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: this measures whether the two AVAILABLE
                calibrations differ. It cannot say where the cut would fall for a comparator that
                does not exist here — that is still R914's 15,488 judge calls.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

NBOOT, SEED = 8000, 921
R860_MDE = 0.0103          # printed for CONTRAST only — a different statistic, never a threshold
DOSE = [-0.020, -0.010, -0.005, -0.002, 0.0, 0.002, 0.005, 0.010, 0.020]


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r922 = next(A26.glob("R922_*/results/threshold_or_comparison.json"), None)
    if not (r881 and r921 and r922):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(r922.read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]
    print(f"  legitimate comparators READ from R921: {legit}")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v); names.append(a)
    V = np.array(V)
    means = V.mean(axis=1)
    print(f"  arms {len(names)} · prompts {n}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def boot(X):
        return np.stack([X[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)

    M = boot(V)

    def lo_hi(Mx, c):
        d = Mx - Mx[c][None, :]
        return np.percentile(d, 2.5, axis=1), np.percentile(d, 97.5, axis=1)

    # ---------- ① WIRING ----------
    wire = {}
    for c in legit:
        i = names.index(c)
        lo, _ = lo_hi(M, i)
        adm = lo > 0
        cut = float(means[adm].min())
        k = int(adm.sum()) - int(adm[i])
        wire[c] = {"cut": cut, "n": k}
    c1 = all(abs(wire[c]["cut"] - ref922[c]["implied_cut_mean_a2"]) < 1e-9
             and wire[c]["n"] == ref922[c]["n_admitted"] for c in legit)
    print(f"\n  ① WIRING — R922's cut and count reproduced, same seed:")
    for c in legit:
        print(f"     {c:<16} cut {wire[c]['cut']:.6f} (R922 "
              f"{ref922[c]['implied_cut_mean_a2']:.6f})   n {wire[c]['n']} "
              f"(R922 {ref922[c]['n_admitted']})")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ---------- ④ PLACEBO ----------
    zeros = [float(np.percentile(M[names.index(c)] - M[names.index(c)], 2.5)) for c in legit]
    c4 = all(z == 0.0 for z in zeros)
    print(f"\n  ④ PLACEBO — lo(X − X) for both comparators: {zeros}   ④ {c4}  "
          f"{'PASS' if c4 else 'FAIL'}")

    # ---------- ② RESOLUTION MEASURED FOR THIS ESTIMAND ----------
    ci = names.index(legit[-1])          # genericpool16, the published comparator
    lo0, hi0 = lo_hi(M, ci)
    halfw = (hi0 - lo0) / 2.0
    res_med = float(np.median(halfw))
    res_iqr = [float(np.percentile(halfw, 25)), float(np.percentile(halfw, 75))]
    print(f"\n  ② RESOLUTION for THIS estimand, measured not inherited:")
    print(f"     half-width of an arm's margin CI vs `{legit[-1]}`: median {res_med:.6f}, "
          f"IQR [{res_iqr[0]:.6f}, {res_iqr[1]:.6f}] over {len(names)} arms")
    print(f"     ⚠ R860's {R860_MDE} is printed for CONTRAST ONLY — it is the MDE of a PAIRED")
    print(f"        DIFFERENCE BETWEEN TWO ARMS, a different statistic on a different scale, and")
    print(f"        it is never used as a threshold here. My own NEXT proposed exactly that.")
    c2 = res_med > 0

    # ---------- ③ POSITIVE / DOSE-RESPONSE ----------
    cut_pub = wire[legit[-1]]["cut"]
    anchor = names[int(np.argmin(np.abs(means - cut_pub)))]
    va = V[names.index(anchor)]
    ai = names.index(anchor)
    lo_anchor = float(np.percentile(M[ai] - M[ci], 2.5))
    # verify the forced identity ONCE against a real bootstrap, then use the algebra for the grid
    Mp_chk = boot(np.vstack([V, (va + DOSE[0])[None, :]]))
    lo_chk = float(np.percentile(Mp_chk[-1] - Mp_chk[ci], 2.5))
    identity_ok = abs(lo_chk - (lo_anchor + DOSE[0])) < 1e-9
    flips = [{"offset": d, "lo": lo_anchor + d, "admitted": bool(lo_anchor + d > 0)}
             for d in DOSE]
    adm_seq = [f["admitted"] for f in flips]
    at_zero = flips[DOSE.index(0.0)]
    # the flip offset: smallest |d| where admission changes from the d=0 state
    flip_d = None
    for f in flips:
        if f["admitted"] != at_zero["admitted"]:
            if flip_d is None or abs(f["offset"]) < abs(flip_d):
                flip_d = f["offset"]
    c3 = (identity_ok and len(set(adm_seq)) == 2 and flip_d is not None
          and abs(lo_anchor) <= res_med)
    print(f"\n  ③ POSITIVE / DOSE-RESPONSE — anchor `{anchor}` (mean {means[names.index(anchor)]:.4f}, "
          f"nearest the bar {cut_pub:.4f}):")
    print(f"     {'offset':>9}{'lo':>12}  admitted")
    for f in flips:
        print(f"     {f['offset']:>+9.3f}{f['lo']:>+12.6f}  {f['admitted']}")
    print(f"     ⚠ the identity lo(d) = lo(0) + d is FORCED — verified once against a real "
          f"bootstrap at d={DOSE[0]}: {identity_ok}")
    print(f"     what is MEASURED: |lo(0)| = {abs(lo_anchor):.6f} for the arm nearest the bar, "
          f"against the resolution band {res_med:.6f} from ②")
    print(f"     admission changes across the grid: {len(set(adm_seq)) == 2}; flip at "
          f"d = {flip_d} (= -lo(0) by algebra)")
    print(f"     ③ {c3}  {'PASS' if c3 else 'FAIL — the plant flips outside the measured band'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                   "wire": wire, "resolution_median": res_med, "dose": flips},
                  open(OUT / "bar_resolution.json", "w"), indent=2)
        return 2

    # ---------- ESTIMAND ①: clause ② applied to the comparator pair ----------
    a_i, b_i = names.index(legit[0]), names.index(legit[1])
    d_ab = M[a_i] - M[b_i]
    lo_ab, hi_ab = float(np.percentile(d_ab, 2.5)), float(np.percentile(d_ab, 97.5))
    lo_ba, hi_ba = -hi_ab, -lo_ab
    beats_ab, beats_ba = lo_ab > 0, lo_ba > 0
    print(f"\n  ⭐⭐⭐ CLAUSE ② TURNED ON ITS OWN COMPARATORS:")
    print(f"     {legit[0]} − {legit[1]}: margin {float(d_ab.mean()):+.6f} "
          f"[{lo_ab:+.6f}, {hi_ab:+.6f}]  admits = {beats_ab}")
    print(f"     {legit[1]} − {legit[0]}: margin {float(-d_ab.mean()):+.6f} "
          f"[{lo_ba:+.6f}, {hi_ba:+.6f}]  admits = {beats_ba}")
    world = "A" if (beats_ab or beats_ba) else "B"

    # ---------- ESTIMAND ②: the boundary census ----------
    unres = [names[i] for i in range(len(names)) if abs(lo0[i]) < res_med and i != ci]
    adm_pub = [names[i] for i in range(len(names)) if lo0[i] > 0 and i != ci]
    unres_adm = [a for a in adm_pub if a in unres]
    print(f"\n  ⭐⭐ BOUNDARY CENSUS against `{legit[-1]}`, resolution {res_med:.6f}:")
    print(f"     admitted {len(adm_pub)} · of those INSIDE the resolution of the bar "
          f"{len(unres_adm)}: {sorted(unres_adm)}")
    print(f"     all arms inside the resolution (either side): {len(unres)}")

    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"one comparator resolvably beats the other, so the two cuts are genuinely different and "
        f"the definition must name which one it uses and why."
        if world == "A" else
        f"NEITHER comparator resolvably beats the other by clause ②'s own bar. **The two admissible "
        f"calibrations are indistinguishable to this design**, so `{wire[legit[-1]]['cut']:.4f}` and "
        f"`{wire[legit[0]]['cut']:.4f}` are one interval, not two numbers, and the difference "
        f"between {wire[legit[-1]]['n']} and {wire[legit[0]]['n']} admitted arms is not a "
        f"difference this design can see."))
    print(f"     ⚠ AND THE CUT IS NOT THE ONLY UNRESOLVED THING: {len(unres_adm)} of "
          f"{len(adm_pub)} admitted arms sit within the measured resolution of the bar, so their")
    print(f"     admission is a coin the design cannot call either.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT,
               "killed_my_own_next": {
                   "was": "compare the 0.0080 cut gap against R860's MDE of 0.0103",
                   "why_wrong": "R860's MDE is for a PAIRED DIFFERENCE BETWEEN TWO ARMS; the cut "
                                "is a THRESHOLD ON MEAN A2 — different statistics, different "
                                "scales. An inherited MDE is another design's resolution.",
                   "replaced_by": "clause ② applied to the comparator pair, plus a resolution "
                                  "measured for this estimand"},
               "legitimate": legit, "wiring": wire,
               "resolution_this_estimand": {"median_half_width": res_med, "iqr": res_iqr,
                                            "r860_mde_for_contrast_only": R860_MDE},
               "dose_response": {"anchor": anchor, "grid": flips,
                                 "smallest_flipping_offset": flip_d,
                                 "lo_at_zero": lo_anchor,
                                 "identity_lo_d_equals_lo0_plus_d_verified": identity_ok,
                                 "forced_part": "linearity and the flip at d = -lo(0)",
                                 "measured_part": "whether |lo(0)| for the arm nearest the bar "
                                                  "falls inside the resolution band from ②"},
               "comparator_pair": {"a": legit[0], "b": legit[1],
                                   "margin_a_minus_b": float(d_ab.mean()),
                                   "ci": [lo_ab, hi_ab],
                                   "a_beats_b": bool(beats_ab), "b_beats_a": bool(beats_ba)},
               "boundary_census": {"admitted": len(adm_pub),
                                   "admitted_inside_resolution": sorted(unres_adm),
                                   "all_inside_resolution": len(unres)},
               "unit_note": "margins and cuts are in mean-A2 units; counts are ARMS",
               "cannot_say": "where the cut would fall for a comparator that does not exist on "
                             "this release — still R914's 15,488 judge calls",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "bar_resolution.json", "w"), indent=2)
    print(f"\n  artifact: results/bar_resolution.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
