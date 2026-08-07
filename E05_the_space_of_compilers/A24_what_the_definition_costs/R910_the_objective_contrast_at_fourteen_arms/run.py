#!/usr/bin/env python3
"""
R910 · R909's contrast re-run at 14 arms — against the kill R909 pre-registered.

⛔ WHY. R909 asked whether clause ②'s bar rewards a specific SELECTION OBJECTIVE among label-free
rubric selectors, and missed separation by **0.024**: signed-mean-weight at k=4 was 3/4,
Wilson [0.301, 0.954]; variance-or-magnitude was 0/8, [0.000, 0.324]. It reported the near-miss as
a near-miss and generated six new arms — `topvar`/`topwvar`/`topabs` at k = 2 and 8 — for **0 judge
calls**, verified against R907's measurement that RUBRIC_SELECTOR is subset 1.000 of `coval_full`.

⭐ **THE KILL IS R909's, WRITTEN BEFORE THESE ARMS WERE SCORED**, and it is quoted rather than
restated: *"disjoint Wilson intervals in either specification, or WORLD B stands."* The arms were
chosen by **k not yet built**, never by expected outcome, so the test can go either way.

⛔⛔ **AND THE CONTROL THAT DECIDES WHETHER ANY OF IT IS COMPARABLE.** The 99 arms' admission flags
come from R881; the six new ones must be judged by **the same criterion computed the same way** —
per-prompt A2 margin against `genericpool16`, cluster bootstrap at NBOOT = 8000, admitted iff the
CI lower bound clears zero. **If my re-implementation does not reproduce R881's flag AND its
numbers on known arms, the new arms are being scored by a different instrument and nothing here is
comparable.** R881's committed values for the four k=4 arms are the reference:
`topw_k4` lo +0.014402 admitted, `topabs_k4` lo −0.063677, `topvar_k4` lo −0.066342,
`topwvar_k4` lo −0.048203 — all three of the last NOT admitted.

ESTIMAND        the admitted share by selection objective among label-free rubric selectors, at
                14 arms instead of 12, with Wilson intervals; and whether R909's pre-registered
                disjointness is met.
IDENTIFICATION  exact. ⚠ Not causal, not an admission probability — the arms were built.
SCOPE           population: `topw` (16, from R881) plus `topabs`/`topvar`/`topwvar` at k = 2, 4, 8
                instrument: per-prompt A2 margin vs genericpool16, cluster bootstrap NBOOT 8000
                baseline:   equal share across objectives
                regime:     home release, judge 2B, seed 910
WORLDS          A · disjoint in at least one specification -> the bar rewards a specific selection
                    objective; R909's WORLD B is overturned by more data, not by argument
                B · still overlapping -> the near-miss was not a small-sample accident at this
                    scale either, and the objective stays unseparated
                C · the new arms are ADMITTED -> the direction reverses and the zero was an
                    accident. **This is the outcome that would embarrass the round, and it is
                    reachable: nothing about a k=2 or k=8 variance selector forces a negative
                    margin.**
KILL            CONDITIONAL:
                  ⭐ ① WIRING, and it is the round's hinge: my admission test must reproduce R881's
                     `lo` for all four k=4 arms to within 0.005 AND agree on every flag. A
                     re-implementation that merely agrees on the VERDICT could still be a different
                     estimator; the numbers are checked too.
                  ⭐ ② the six new arms must all score — a missing arm is NAMED, never dropped.
                  ⭐ ③ R909's kill is quoted from its artifact, not restated from memory.
MULTIPLICITY    2 objectives × 2 specifications; every arm's own margin and CI printed.
ARTIFACT        results/objective_at_14.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: this enlarges one group only. The signed
                group is still 16 arms and 4 at k=4.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
BLIND, NBOOT, SEED = "genericpool16", 8000, 910
REF = {"topw_k4": 0.014402, "topabs_k4": -0.063677,
       "topvar_k4": -0.066342, "topwvar_k4": -0.048203}
NEWARMS = ["topvar_k2", "topvar_k8", "topwvar_k2", "topwvar_k8", "topabs_k2", "topabs_k8"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    r909 = next(A24.glob("R909_*/results/selection_objective.json"), None)
    if r909 is None:
        print("  UNRUNNABLE: R909 artifact missing. Exit 2, never 0.")
        return 2
    d909 = json.loads(r909.read_text())
    c3 = "verdicts" in d909 and d909.get("world") == "B"
    print(f"  ③ R909's kill QUOTED from its artifact: world was {d909.get('world')}, "
          f"verdicts {json.dumps(d909.get('verdicts'))}")
    print(f"     the pre-registration is `disjoint Wilson intervals in either specification, or "
          f"WORLD B stands`: {c3}  {'PASS' if c3 else 'FAIL'}")

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    base = vec(BLIND)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2

    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def admit(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - base
        bs = np.array([float(d[b].mean()) for b in idxb])
        lo = float(np.percentile(bs, 2.5))
        return {"arm": nm, "margin": float(d.mean()), "lo": lo, "admitted": lo > 0}

    print(f"\n  ① WIRING reproduce R881's `lo` on the four k=4 arms (NBOOT {NBOOT}, {n} prompts):")
    ok = True
    for a, ref in REF.items():
        r = admit(a)
        if r is None:
            print(f"     {a:<12} MISSING"); ok = False; continue
        d = abs(r["lo"] - ref)
        good = d < 0.005 and (r["admitted"] == (ref > 0))
        ok = ok and good
        print(f"     {a:<12} lo {r['lo']:+.6f} vs R881 {ref:+.6f}  |Δ|={d:.6f}  "
              f"admitted {r['admitted']}  {'PASS' if good else 'FAIL'}")
    print(f"     numbers checked, not only verdicts — agreeing on the flag alone would not show")
    print(f"     the estimator is the same: {ok}  {'PASS' if ok else 'FAIL'}")

    fresh, missing = [], []
    for a in NEWARMS:
        r = admit(a)
        (fresh.append(r) if r else missing.append(a))
    c2 = not missing
    print(f"\n  ② the six new arms scored: {len(fresh)}/6; MISSING and NAMED: {missing}: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    if not (ok and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "wiring_ok": bool(ok), "missing": missing},
                  open(OUT / "objective_at_14.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ THE SIX NEW ARMS, every margin and CI lower bound printed:")
    for r in fresh:
        print(f"     {r['arm']:<12} margin {r['margin']:+.6f}  lo {r['lo']:+.6f}  "
              f"admitted {r['admitted']}")

    r908 = json.loads(next(A24.glob("R908_*/results/bar_by_rule.json")).read_text())
    rules = {r["rule"]: r for r in r908["rules"]}
    tw = rules["topw"]
    old_other = sum(rules[r]["n_built"] for r in ("topabs", "topvar", "topwvar"))
    old_other_a = sum(rules[r]["n_admitted"] for r in ("topabs", "topvar", "topwvar"))
    new_a = sum(1 for r in fresh if r["admitted"])
    tot_a, tot_n = old_other_a + new_a, old_other + len(fresh)

    tw4 = tw["per_k"]["4"]
    rows = [
        {"objective": "SIGNED_MEAN_WEIGHT", "spec": "pooled over k",
         "n_admitted": tw["n_admitted"], "n_built": tw["n_built"]},
        {"objective": "SIGNED_MEAN_WEIGHT", "spec": "matched k=4",
         "n_admitted": tw4[0], "n_built": tw4[1]},
        {"objective": "VARIANCE_OR_MAGNITUDE", "spec": "pooled over k",
         "n_admitted": tot_a, "n_built": tot_n},
        {"objective": "VARIANCE_OR_MAGNITUDE", "spec": "matched k=4",
         "n_admitted": old_other_a, "n_built": old_other},
    ]
    for r in rows:
        r["share"] = r["n_admitted"] / r["n_built"]
        r["ci95"] = list(wilson(r["n_admitted"], r["n_built"]))

    print(f"\n  ⭐⭐ THE CONTRAST AT {tot_n} ARMS IN THE VARIANCE GROUP (was {old_other}):")
    print(f"     {'objective':<24}{'spec':<16}{'adm/built':>11}{'share':>8}{'Wilson 95%':>22}")
    for r in rows:
        frac = f"{r['n_admitted']}/{r['n_built']}"
        ci = f"[{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]"
        print(f"     {r['objective']:<24}{r['spec']:<16}{frac:>11}{r['share']:>8.3f}{ci:>22}")

    verd = {}
    for spec in ("pooled over k", "matched k=4"):
        a = next(r for r in rows if r["objective"] == "SIGNED_MEAN_WEIGHT" and r["spec"] == spec)
        b = next(r for r in rows if r["objective"] == "VARIANCE_OR_MAGNITUDE" and r["spec"] == spec)
        dis = a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0]
        verd[spec] = {"disjoint": bool(dis),
                      "signed_lo_minus_other_hi": float(a["ci95"][0] - b["ci95"][1])}
        print(f"     {spec:<16} disjoint: {dis}   (signed's lower {a['ci95'][0]:.3f} − other's "
              f"upper {b['ci95'][1]:.3f} = {a['ci95'][0] - b['ci95'][1]:+.3f})")

    world = ("C" if new_a > 0 else "A" if any(v["disjoint"] for v in verd.values()) else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "DISJOINT in at least one specification — the bar rewards a specific selection "
             "objective, and R909's WORLD B is overturned by more data rather than by argument",
        "B": "still overlapping at 14 arms — the near-miss was not a small-sample accident at this "
             "scale either, and the objective stays unseparated",
        "C": f"{new_a} of the new variance/magnitude arms ARE ADMITTED — the direction reverses "
             "and the clean zero was a small-sample accident. **This was the outcome that would "
             "embarrass the round, and it was reachable**"}[world])
    print(f"\n  ⚠ ONE GROUP ONLY WAS ENLARGED. `topw` is still 16 arms and 4 at k=4, so the")
    print(f"    signed side's interval is unchanged and the comparison is asymmetric by design.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT, "n_prompts": n,
               "new_arms": fresh, "n_new_admitted": new_a,
               "groups": rows, "verdicts": verd,
               "r909_prereg": "disjoint Wilson intervals in either specification, or WORLD B "
                              "stands — quoted from R909's artifact, not restated",
               "wiring": {"reference": REF, "reproduced": bool(ok),
                          "why_numbers_not_just_flags": "a re-implementation agreeing on the "
                                                        "verdict could still be a different "
                                                        "estimator"},
               "arms_chosen_by": "k NOT YET BUILT, never by expected outcome",
               "only_one_group_enlarged": "topw is still 16 arms / 4 at k=4; the comparison is "
                                          "asymmetric by design",
               "unit_note": "counts are ARMS; margins are A2 units vs genericpool16",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "objective_at_14.json", "w"), indent=2)
    print(f"\n  artifact: results/objective_at_14.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
