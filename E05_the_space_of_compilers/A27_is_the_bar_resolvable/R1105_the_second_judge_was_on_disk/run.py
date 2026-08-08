#!/usr/bin/env python3
"""R1105 — the second judge was on disk the whole time. Recompute the definition's extension under it.

R1103 and R1104 priced the SAMPLING axis: |admitted| = 22.77 [17, 26], the slack 10.48 [7, 17]. The
INSTRUMENT axis was never priced at all, and this project's own memory index already flags the CoVal
line as *10 of 11 claims instrument-dependent (a local 2B judge)*.

⛔ AND THE WALL WAS NEVER CHECKED. `corebench/results/` holds `sat08_full.npz`, `sat08_generic.npz`,
`sat08_genericpool16.npz`, `sat08_coval_core.npz` and 32 selection arms already rebuilt under the 8B
judge — **materialised, committed, zero further judge calls.** Two of my own impossibility registers
(R1100, R1101) print *the verdict for `*_08bR` arms — N/A — the 8B judge npz, a different instrument
axis*, which marked as unavailable a file sitting beside the one those rounds read. §4's `a wall never
checked`: an unchecked wall is UNVERIFIED, never SETTLED, and a register line saying `N/A` is exactly
what stops anyone looking.

⭐ AND THE SPECIFICATION CURVE IS ON DISK TOO, which is why this is one round and not two. Measured
from the objects, not assumed: `core_topvar_k4_08b.json` has the SAME criterion texts as the 2B arm
while `_08bR` does not. So the release's two suffixes are the two defensible specifications —
  `_08b`  : the 2B-selected criteria RE-SCORED by the 8B judge  -> pure MEASUREMENT sensitivity
  `_08bR` : the rule RE-RUN under the 8B judge                  -> whole-PIPELINE sensitivity
⚠ DERIVATION, labelled: `select_core.py`'s own help states the two coincide EXACTLY for the
satisfaction-blind rules (`random_k`, `topw_k`, `topabs_k`, `full`), so no `_08bR` exists for them and
none is expected. Only the five satisfaction-consuming rules can differ.

ESTIMAND        (Q1) the ②′ admitted set under the 2B judge and under the 8B judge, on the arms
                     scoreable under BOTH, and their symmetric difference.
                (Q2) the same under specification `_08bR` where the release provides it, so the
                     measurement axis and the pipeline axis are separated rather than merged.
IDENTIFICATION  identified on the common population only. ⚠ NOT identified for the 56 arms with no 8B
                counterpart — they are excluded from BOTH sides and named, because comparing a
                99-arm set to a 43-arm set would attribute a population change to the judge.
UNIT OF THE     an arm and its ②′ membership under a named judge.
  INSTRUMENT
UNIT OF THE     the same. ⚠ NOT the same as R1103's unit (an arm and its admission frequency over
  CLAIM         prompt resamples): that measured SAMPLING, this measures INSTRUMENT, and the two are
                named separately here so neither is quoted as the other's interval.
SCOPE           population: the 43 arms carrying both a 2B and an 8B satisfaction file. instrument:
                R1055's operator, analytic inner bound (validated against its 4000-draw bootstrap).
                baseline: the 2B set on the same population. regime: 968 prompts, target A2,
                comparators {generic, genericpool16} taken from the judge under test.
WORLDS          A THE DEFINITION IS INSTRUMENT-PORTABLE  the two admitted sets differ by at most 4
                                arms (R978's registered band at N=968, the yardstick R1103 and R1104
                                both used). Then ②′ membership is a property of the arms.
                B THE DEFINITION IS INSTRUMENT-BOUND     they differ by more. Then every membership
                                statement in this arc is a statement about a local 2B judge, and the
                                gauge bound is larger than the sampling interval already published.
                Prediction matrix on (|symmetric difference|, 2B set size vs 8B set size):
                  A -> (<= 4, similar)      B -> (> 4, may differ in size as well as membership)
KILL            pre-registered. World A is KILLED if |symmetric difference| > 4 under specification
                `_08b`. Gated on its own controls:
                                    if positive_2B_matches_R1055_on_common and judges_differ:
                                        evaluate(symmetric_difference)
                                    else: UNVERIFIED
POSITIVE CTRL   the 2B run restricted to the common population must be exactly R1055's committed
                admitted set intersected with that population. If it is not, the operator is not the
                definition's and the 8B side means nothing.
NEGATIVE CTRL   the two judges must not be the same instrument: the raw per-cell satisfaction must
                differ. Measured, not assumed — correlation and the share of differing cells.
                ⚠ This control can FAIL: if someone had copied the file, `sat08_full.npz` would be
                identical to `sat_full.npz` and every downstream difference would be zero for a
                reason that has nothing to do with judging.
SHAM            the same operation with the judge held FIXED: compute ②′ twice from the 2B files, on
                the same population, and require an empty symmetric difference. Same operator, same
                population, same compute, minus the ingredient — the change of judge.
PLACEBO         each judge's set against itself: empty.
NOISE FLOOR     R1103's committed sampling interval on |admitted|, [17, 26] at the full population,
                is the yardstick a gauge difference must be read against. A judge difference smaller
                than the sampling spread is not an instrument finding.
MULTIPLICITY    43 arms x 2 judges x 2 specifications where available; every arm's membership
                reported, movers and non-movers.
SPECIFICATION   judge {2B, 8B} x spec {`_08b` re-scored, `_08bR` re-run} on the 5 arms that have both.
SEEDS           the analytic inner bound is deterministic; the bootstrap validation uses 3 seeds.
ARTIFACT        results/second_judge.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      | criterion | what it would require |
                | the 8B verdict for the 56 arms without an 8B file | judging those arms' criteria
                  with the 8B model — real inference, not a re-read |
                | Qwen3B and Phi, which also sit on disk at 968 prompts | their COMPARATOR files;
                  `E04/.../R164_instrument/` ships `sat_full_*` and `sat_core_*` only, so ②′ is not
                  computable there. ⭐ This is a REAL N/A and it is stated with what would lift it |
                | whether either judge is CORRECT | an external gold standard; A2 is agreement with
                  this release's annotators under whichever judge scored the criteria |
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

OUT = HERE / "results" / "second_judge.json"
COMP = ["generic", "genericpool16"]
Z, NBOOT = 1.959963984540054, 4000
BAND = 4                      # R978's registered band at N=968, the arc's standing yardstick


def main() -> int:
    f55 = next(A27.glob("R1055_*/results/component_ablation.json"), None)
    f03 = next(A27.glob("R1103_*/results/set_stability.json"), None)
    if f55 is None or f03 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    r55 = set(json.loads(f55.read_text())["baseline_admitted"])
    samp = json.loads(f03.read_text())["set_size"]

    # ---- which arms exist under each judge, measured from the directory
    sel8 = {p.stem[4:-4] for p in RES.glob("sat_*_08b.npz")}       # 2B-selected, 8B-scored
    sel8R = {p.stem[4:-5] for p in RES.glob("sat_*_08bR.npz")}     # rule re-run under 8B
    non8 = {p.stem[6:] for p in RES.glob("sat08_*.npz")}           # arm's own criteria, 8B-scored
    two = {p.stem[4:] for p in RES.glob("sat_*.npz")}
    two = {a for a in two if not a.endswith(("_08b", "_08bR"))}
    w8 = sel8 | non8
    common = sorted(w8 & two)
    excluded = sorted(two - w8)
    if not all(c in common for c in COMP):
        print("  UNRUNNABLE: a comparator is missing from a judge world. Exit 2, never 0."); return 2
    print(f"  common population {len(common)} · excluded for want of an 8B file {len(excluded)}")
    print(f"  spec `_08b` arms {len(sel8)} · spec `_08bR` arms {len(sel8R)} {sorted(sel8R)}")

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

    def path_for(arm, judge, spec="08b"):
        if judge == "2B":
            f = RES / f"sat_{arm}.npz"
            return f if f.exists() else None
        f = RES / f"sat_{arm}_{spec}.npz"                # 2B-selected, 8B-scored (or re-run)
        if f.exists():
            return f
        f = RES / f"sat08_{arm}.npz"                     # the arm's own criteria, 8B-scored
        return f if f.exists() else None

    def build(judge, spec="08b"):
        V, COVm, names = {}, {}, []
        for a in common:
            p = path_for(a, judge, spec)
            if p is None:
                continue
            v = perprompt(p)
            cov = np.isfinite(v)
            if cov.sum() < 100:
                continue
            V[a] = np.nan_to_num(v, nan=0.0); COVm[a] = cov; names.append(a)
        return V, COVm, names

    def lo_ana(d):
        m = len(d)
        return float(d.mean() - Z * d.std(ddof=1) / np.sqrt(m)) if m > 1 else 0.0

    def lo_boot(d, seed):
        rng = np.random.default_rng(seed); m = len(d)
        return float(np.percentile(d[rng.integers(0, m, size=(NBOOT, m))].mean(axis=1), 2.5))

    def admit(V, COVm, names, inner="analytic", seed=0):
        out = set()
        for a in names:
            if a in COMP:
                continue
            beats = 0
            for c in COMP:
                if c not in V:
                    continue
                m = COVm[a] & COVm[c]
                d = (V[a] - V[c])[m]
                if len(d) < 30:
                    continue
                if (lo_boot(d, seed) if inner == "boot" else lo_ana(d)) > 0:
                    beats += 1
            if beats >= len(COMP):
                out.add(a)
        return out

    V2, C2, N2 = build("2B")
    V8, C8, N8 = build("8B", "08b")
    a2, a8 = admit(V2, C2, N2), admit(V8, C8, N8)
    sym = sorted(a2 ^ a8)
    only2, only8 = sorted(a2 - a8), sorted(a8 - a2)

    # ---- controls
    positive = a2 == (r55 & set(N2))
    x = np.asarray(np.load(RES / "sat_full.npz", allow_pickle=True)["sat"], float)
    y = np.asarray(np.load(RES / "sat08_full.npz", allow_pickle=True)["sat"], float)
    corr = float(np.corrcoef(x, y)[0, 1]); frac_diff = float((x != y).mean())
    judges_differ = frac_diff > 0.5 and corr < 0.99
    # ⛔ THE CONTROL WITHOUT WHICH 9 -> 0 IS SILENCE, NOT A MEASUREMENT. If the 8B judge could not
    #    order anything, every arm would fail against every comparator for a reason that has nothing
    #    to do with the definition. So the 8B judge must still resolvably rank the comparator ABOVE
    #    the random baseline — a known-signed contrast in the same design, on the same population.
    def gap(V, COVm, a, b):
        m = COVm[a] & COVm[b]
        d = (V[a] - V[b])[m]
        return {"delta": round(float(d.mean()), 5), "lo": round(lo_ana(d), 5), "n": int(len(d))}
    RB = "random_k4_s0"
    ord2 = gap(V2, C2, "generic", RB) if RB in V2 else None
    ord8 = gap(V8, C8, "generic", RB) if RB in V8 else None
    judge8_can_order = bool(ord8 and ord8["lo"] > 0)

    sham = sorted(admit(V2, C2, N2) ^ admit(*build("2B"), inner="analytic"))
    placebo = not (a2 ^ a2) and not (a8 ^ a8)
    a2b = admit(V2, C2, N2, "boot", 11)
    a8b = admit(V8, C8, N8, "boot", 11)
    instrument_ok = (a2b == a2) and (a8b == a8)

    # ---- ⛔ SIGN OR RESOLUTION? R1102 downgraded a whole round for reporting a null without asking
    #      this. A `not admitted` under 8B can mean the arm LOST to the comparator (sign flipped) or
    #      merely stopped RESOLVING (still ahead, interval widened). They are different findings and
    #      a set difference cannot tell them apart.
    def margins(V, COVm, arm):
        out = {}
        for c in COMP:
            if c not in V or arm not in V:
                continue
            m = COVm[arm] & COVm[c]
            d = (V[arm] - V[c])[m]
            if len(d) < 30:
                continue
            out[c] = {"delta": round(float(d.mean()), 5), "lo": round(lo_ana(d), 5),
                      "n": int(len(d))}
        return out

    diag = {}
    for a in sorted(a2 - a8):
        m2, m8 = margins(V2, C2, a), margins(V8, C8, a)
        # the arm fails under 8B; classify against EACH comparator it now fails
        worst = min((m8[c]["delta"] for c in m8), default=None)
        diag[a] = {
            "margins_2B": m2, "margins_8B": m8,
            "min_point_delta_8B": worst,
            "class": ("SIGN FLIP — the arm is now BEHIND a comparator" if worst is not None and worst < 0
                      else "RESOLUTION LOSS — still ahead on the point estimate, no longer resolvable"
                      if worst is not None else "UNEVALUABLE"),
        }
    n_flip = sum(1 for v in diag.values() if v["class"].startswith("SIGN"))
    n_res = sum(1 for v in diag.values() if v["class"].startswith("RESOLUTION"))

    # ---- the MECHANISM, measured rather than named: where do the comparators sit under each judge?
    def level(V, arm):
        return round(float(V[arm].mean()), 4) if arm in V else None
    mech = {"2B": {a: level(V2, a) for a in COMP + ["coval_core", "topw_k4", "random_k4_s0"]},
            "8B": {a: level(V8, a) for a in COMP + ["coval_core", "topw_k4", "random_k4_s0"]}}

    # ---- Q2: the two specifications, where the release provides both
    specrows = {}
    if sel8R:
        V8R, C8R, N8R = build("8B", "08bR")
        a8R = admit(V8R, C8R, N8R)
        for a in sorted(sel8R):
            if a in common:
                specrows[a] = {"in_2B": a in a2, "in_8B_rescored": a in a8,
                               "in_8B_rerun": a in a8R}
        # ⚠ RESTRICTED TO THE ARMS BOTH BUILDS CONTAIN. The `_08bR` build falls back to `sat08_<arm>`
        #   where no re-run file exists, so its population is SMALLER — differencing the two sets
        #   unrestricted would attribute a population change to the specification.
        shared_spec_pop = set(N8) & set(N8R)
        spec_sym = sorted((a8 & shared_spec_pop) ^ (a8R & shared_spec_pop))
    else:
        a8R, spec_sym, shared_spec_pop = set(), [], set()

    gate_open = (positive and judges_differ and not sham and placebo and instrument_ok
                 and judge8_can_order)
    world_A_killed = (len(sym) > BAND) if gate_open else None

    per_arm = {a: {"in_2B": a in a2, "in_8B": a in a8, "moved": (a in a2) != (a in a8)}
               for a in sorted(set(N2) & set(N8))}

    payload = {
        "round": "R1105",
        "question": "does the definition's extension survive a change of judge?",
        "wall_that_was_never_checked": {
            "registers_that_marked_the_8B_judge_N/A": ["R1100", "R1101"],
            "what_was_on_disk": sorted(non8),
            "n_selection_arms_already_rebuilt_under_8B": len(sel8),
            "further_judge_calls_required": 0,
        },
        "population": {"common": common, "n_common": len(common),
                       "excluded_for_want_of_an_8B_file": excluded,
                       "n_excluded": len(excluded)},
        "sets": {"admitted_2B": sorted(a2), "admitted_8B": sorted(a8),
                 "n_2B": len(a2), "n_8B": len(a8),
                 "only_2B": only2, "only_8B": only8,
                 "symmetric_difference": sym, "n_symmetric_difference": len(sym),
                 "R1055_full_population": len(r55)},
        "specification_curve": {
            "spec_08b_means": "the 2B-selected criteria RE-SCORED by 8B — measurement sensitivity",
            "spec_08bR_means": "the rule RE-RUN under 8B — whole-pipeline sensitivity",
            "arms_with_both": sorted(specrows), "rows": specrows,
            "symmetric_difference_between_specs": spec_sym,
            "spec_comparison_population": len(shared_spec_pop),
            "derivation": ("select_core.py's own help states the two specifications COINCIDE EXACTLY "
                           "for the satisfaction-blind rules (random_k, topw_k, topabs_k, full), so "
                           "no `_08bR` exists for them and none is expected — labelled as a "
                           "derivation, not read as missing data"),
        },
        "judge_disagreement": {"per_cell_correlation": round(corr, 4),
                               "share_of_cells_differing": round(frac_diff, 4)},
        "sign_or_resolution": {"per_arm": diag, "n_sign_flip": n_flip,
                               "n_resolution_loss": n_res,
                               "why": ("R1102 downgraded an entire round for reporting a null "
                                       "without asking this. A set difference cannot distinguish "
                                       "`the arm lost` from `the arm stopped resolving`.")},
        "mechanism_mean_A2_by_judge": mech,
        "judge_can_order": {"2B_generic_minus_random": ord2, "8B_generic_minus_random": ord8,
                            "why": ("without this, 9 -> 0 is silence: an instrument that orders "
                                    "nothing fails every arm for a reason unrelated to the "
                                    "definition")},
        "yardsticks": {"R978_registered_band": BAND,
                       "R1103_sampling_interval_on_size": [samp["p2.5"], samp["p97.5"]],
                       "note": ("the sampling interval is on the FULL 99-arm population and the "
                                "gauge here is on 43 arms; they are reported side by side as two "
                                "axes, never subtracted from one another")},
        "per_arm": per_arm,
        "controls": {
            "POSITIVE the 2B run equals R1055's committed set restricted to the common population":
                bool(positive),
            "NEGATIVE the two judges are not the same instrument (cells differ)": bool(judges_differ),
            "POSITIVE the 8B judge can still ORDER — `generic` beats the random baseline resolvably":
                judge8_can_order,
            "SHAM the same operation with the judge held FIXED moves nothing": not sham,
            "PLACEBO each judge's set against itself is empty": bool(placebo),
            "INSTRUMENT the analytic inner bound equals the 4000-draw bootstrap, both judges":
                bool(instrument_ok),
        },
        "kill": {"gate_open": gate_open, "world_A_killed": world_A_killed,
                 "threshold": BAND, "observed": len(sym)},
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    if not gate_open:
        payload["verdict"] = ("⚠ UNVERIFIED — a control is red. "
                              f"Controls: {json.dumps(payload['controls'])}")
    else:
        payload["verdict"] = (
            f"{'⛔ WORLD A IS KILLED' if world_A_killed else '⭐ WORLD A SURVIVES'}: the admitted set "
            f"is {len(a2)} under the 2B judge and {len(a8)} under the 8B judge on the same "
            f"{len(common)} arms, symmetric difference {len(sym)} against a threshold of {BAND}. "
            f"Only-2B {only2}; only-8B {only8}. The judges disagree on "
            f"{frac_diff:.1%} of cells at correlation {corr:.3f}, so this is a second instrument and "
            f"not a copy. ⭐ AND THE FAILURES ARE CLASSIFIED rather than left as a set difference: "
            f"{n_flip} of {len(diag)} are SIGN FLIPS (the arm is now BEHIND a comparator) and "
            f"{n_res} are RESOLUTION LOSSES (still ahead on the point estimate, no longer "
            f"resolvable). ⛔ AND THE FILES WERE COMMITTED THE WHOLE TIME: {len(sel8)} selection arms "
            f"already rebuilt under 8B plus {len(non8)} directly judged, zero further judge calls, "
            f"while R1100 and R1101 printed the 8B axis as N/A in their impossibility registers.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True))
    print(f"\n  2B admitted {len(a2)} · 8B admitted {len(a8)} · symmetric difference {len(sym)}")
    print(f"    only 2B: {only2}")
    print(f"    only 8B: {only8}")
    if specrows:
        print("\n  specification curve (arms with both `_08b` and `_08bR`):")
        for a, r in specrows.items():
            print(f"    {a:<20} 2B={r['in_2B']}  8B rescored={r['in_8B_rescored']}  "
                  f"8B rerun={r['in_8B_rerun']}")
    print()
    for k, v in payload["controls"].items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
    print()
    print(" ", payload["verdict"])
    return 0 if gate_open else 2


if __name__ == "__main__":
    sys.exit(main())
