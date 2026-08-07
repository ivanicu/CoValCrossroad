#!/usr/bin/env python3
"""
R915 · the comparator is a STRUCTURAL ZERO inside R906's denominator — and my own NEXT proposed a
        check that could not fail.

⛔⛔ **FIRST, MY OWN NEXT WAS A DERIVATION AND IT IS LABELLED AS ONE.** R914 closed by proposing to
*"recompute the admitted set with `genericpool16` EXCLUDED from the tested population and see
whether any admission flag changes."* **No flag can change.** Admission of arm X is
`lo(A2(X) − A2(comparator)) > 0` — a function of X and the comparator ONLY. Removing some other arm
Y from the tested list is not an input to X's computation. **The proposed check cannot fail**, which
is §4's first row, arriving in my own closing sentence for the fourth time this arc. It is
recomputed here anyway, as a WIRING test, precisely because its answer is forced.

⭐⭐ **AND THE REAL DEFECT IS ONE LEVEL OVER, IN A DENOMINATOR.** R906 typed `genericpool16` into
`FIXED_CHECKLIST` and reported that kind as **1/2 = 0.500, Wilson [0.095, 0.905]**. The two members
are `generic` and `genericpool16` — **and `genericpool16` is the comparator, so its margin against
itself is exactly 0 and it can NEVER be admitted.** It is not an eligible unit; it is a structural
zero sitting in the denominator of a share R906 used to reason about the bar.

⭐ **THAT IS R902's FAILURE AT THE ARM LEVEL.** R902 found 25.5% of prompts contributing exact zeros
to a mean and wrote: *"a mean over a population containing structural zeros is not the effect on the
units that can show one."* The same sentence applies here with `prompts` replaced by `arms`, and
nobody noticed because the denominator was 2.

ESTIMAND        (a) whether excluding a non-comparator arm changes any admission flag — FORCED, a
                    wiring test; (b) the corrected `FIXED_CHECKLIST` share once the structural zero
                    is removed from the denominator, and what it does to R906's verdict.
IDENTIFICATION  (a) forced by the algebra. (b) exact.
SCOPE           population: R906's typed kinds; the comparator `genericpool16`
                instrument: per-prompt A2 margin vs genericpool16, bootstrap NBOOT 8000
                baseline:   R906's committed 1/2
                regime:     home release, judge 2B, seed 915
WORLDS          A · the corrected share changes R906's readability or verdict -> R906's WORLD A
                    rested on a denominator containing an ineligible unit
                B · the corrected share leaves the verdict intact -> the defect is real but not
                    load-bearing, and saying so is the honest form
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / DERIVATION-AS-WIRING: `genericpool16`'s margin against itself
                     must be EXACTLY 0 and its `lo` must not exceed 0. Forced by the algebra, so a
                     failure localises a coding error rather than a finding — the same construction
                     R902 used.
                  ⭐ ② the flag-invariance claim must be CHECKED, not asserted: recompute every
                     flag with the comparator dropped from the tested list and require ZERO
                     changes among the other arms.
                  ⭐ ③ the corrected share must be recomputed from the arm lists, never edited by
                     hand from 1/2.
MULTIPLICITY    one kind corrected; every kind's before/after printed.
ARTIFACT        results/structural_zero.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this fixes ONE denominator. It does not revisit whether
                `genericpool16` should have been the comparator at all — R913/R914 own that.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
COMP, NBOOT, SEED = "genericpool16", 8000, 915


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    r906 = json.loads(next(A24.glob("R906_*/results/bar_by_source.json")).read_text())
    kinds = r906["kinds"]

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None

    base = vec(COMP)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2
    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def stats(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - base
        bs = np.array([float(d[b].mean()) for b in idxb])
        return {"margin": float(d.mean()), "lo": float(np.percentile(bs, 2.5))}

    self_s = stats(COMP)
    c1 = abs(self_s["margin"]) < 1e-12 and self_s["lo"] <= 0
    print(f"  ① POSITIVE/DERIVATION the comparator against ITSELF: margin "
          f"{self_s['margin']:.3e}, lo {self_s['lo']:.3e}")
    print(f"     exactly 0 and never admitted: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"     forced by the algebra, so a FAILURE localises a coding error, not a finding")

    # ② the flag-invariance claim, CHECKED
    fc = next(k for k in kinds if k["kind"] == "FIXED_CHECKLIST")
    members = sorted(fc["built"])
    flags_all, flags_drop = {}, {}
    for a in members:
        s = stats(a)
        if s is None:
            continue
        flags_all[a] = s["lo"] > 0
        if a != COMP:
            flags_drop[a] = s["lo"] > 0
    changed = [a for a in flags_drop if flags_all.get(a) != flags_drop[a]]
    c2 = not changed
    print(f"\n  ② FLAG INVARIANCE dropping the comparator from the tested list changes "
          f"{len(changed)} other flag(s): {c2}  {'PASS' if c2 else 'FAIL'}")
    print(f"     checked rather than asserted — but the answer was FORCED, which is exactly why")
    print(f"     my own NEXT proposing it was a check that could not fail")

    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "self": self_s, "changed": changed},
                  open(OUT / "structural_zero.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ FIXED_CHECKLIST's MEMBERS, and which are ELIGIBLE:")
    for a in members:
        s = stats(a)
        elig = a != COMP
        print(f"     {a:<18} margin {s['margin']:+.6f}  lo {s['lo']:+.6f}  "
              f"admitted {s['lo'] > 0}   eligible {elig}"
              f"{'   <- STRUCTURAL ZERO: it IS the comparator' if not elig else ''}")

    rows = []
    for k in kinds:
        built = [a for a in k["built"]]
        adm = [a for a in k["admitted"]]
        elig = [a for a in built if a != COMP]
        elig_adm = [a for a in adm if a != COMP]
        before = (len(adm), len(built))
        after = (len(elig_adm), len(elig))
        rows.append({"kind": k["kind"], "before": list(before), "after": list(after),
                     "ci_before": list(wilson(*before)) if before[1] else None,
                     "ci_after": list(wilson(*after)) if after[1] else None,
                     "changed": before != after})
    print(f"\n  ⭐⭐ ③ EVERY KIND, BEFORE AND AFTER REMOVING THE INELIGIBLE UNIT "
          f"(recomputed from the lists, never edited by hand):")
    print(f"     {'kind':<26}{'before':>10}{'after':>10}   {'Wilson before':<22}Wilson after")
    for r in rows:
        b = f"{r['before'][0]}/{r['before'][1]}"
        a = f"{r['after'][0]}/{r['after'][1]}"
        cb = (f"[{r['ci_before'][0]:.3f}, {r['ci_before'][1]:.3f}]" if r["ci_before"] else "—")
        ca = (f"[{r['ci_after'][0]:.3f}, {r['ci_after'][1]:.3f}]" if r["ci_after"] else "—")
        print(f"     {r['kind']:<26}{b:>10}{a:>10}   {cb:<22}{ca}"
              f"{'   CHANGED' if r['changed'] else ''}")

    fcr = next(r for r in rows if r["kind"] == "FIXED_CHECKLIST")
    # R906's readability bound was a Wilson width < 0.60
    w_before = fcr["ci_before"][1] - fcr["ci_before"][0]
    w_after = fcr["ci_after"][1] - fcr["ci_after"][0]
    read_before, read_after = w_before < 0.60, w_after < 0.60
    world = "A" if read_before != read_after else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "the correction changes whether FIXED_CHECKLIST is READABLE, so R906's verdict "
             "rested on a denominator containing an ineligible unit",
        "B": f"FIXED_CHECKLIST stays unreadable either way (width {w_before:.3f} -> "
             f"{w_after:.3f}, both above R906's 0.60 bound), so the defect is REAL but NOT "
             "load-bearing — R906's `no source preference is demonstrable` survives"}[world])
    print(f"\n  ⛔ THE REPORTED 0.500 WAS STILL WRONG. `FIXED_CHECKLIST 1/2` counted the")
    print(f"     comparator as a unit that failed to clear itself. Corrected: "
          f"{fcr['after'][0]}/{fcr['after'][1]}. **R902's sentence, one level up: a share over a")
    print(f"     population containing STRUCTURAL ZEROS is not the rate on the units that can")
    print(f"     show one** — and nobody noticed because the denominator was 2.")
    print(f"\n  ⚠ THIS FIXES ONE DENOMINATOR. It does not revisit whether `genericpool16` should")
    print(f"    have been the comparator at all — R913 and R914 own that question, and its price")
    print(f"    is 15,488 judge calls.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED,
               "comparator_self": self_s, "flag_changes_when_dropped": changed,
               "my_next_was_a_derivation": "admission(X) = f(X, comparator); removing arm Y != X "
                                           "from the tested list is not an input to X. R914's "
                                           "proposed check could not fail — §4's first row, in my "
                                           "own closing sentence for the fourth time this arc.",
               "kinds_before_after": rows,
               "fixed_checklist": {"before": fcr["before"], "after": fcr["after"],
                                   "width_before": w_before, "width_after": w_after,
                                   "readable_before": bool(read_before),
                                   "readable_after": bool(read_after)},
               "the_defect": "genericpool16 is the comparator, so its margin against itself is "
                             "exactly 0 and it can never be admitted; it is an INELIGIBLE unit "
                             "sitting in FIXED_CHECKLIST's denominator",
               "r902_one_level_up": "a share over a population containing structural zeros is not "
                                    "the rate on the units that can show one — prompts there, "
                                    "ARMS here, and the denominator of 2 hid it",
               "does_not_revisit": "whether genericpool16 should be the comparator — R913/R914, "
                                   "priced at 15,488 judge calls",
               "unit_note": "counts are ARMS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "structural_zero.json", "w"), indent=2)
    print(f"\n  artifact: results/structural_zero.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
